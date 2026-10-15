#!/usr/bin/env python3
"""Render static local wireframes at 390px and 1440px, optionally before/after.

Usage (through cro-py):
    render_wireframe.py before.html --after after.html --annotations annotations.json -o renders

Annotation JSON is a list of {number, finding_id, change, evidence} objects.
After HTML marks changes with data-annotation="1". No network or JavaScript is
allowed. Copy CSS/images into the HTML directory (or its subdirectories).
"""

import argparse
import base64
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.parse import unquote, urlparse

VIEWPORTS = {"mobile": (390, 844), "desktop": (1440, 900)}


class MarkerParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.markers = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key == "data-annotation":
                if not value or not value.isdigit() or int(value) < 1:
                    raise ValueError("data-annotation must be a positive integer")
                self.markers.append(int(value))


def read_markers(path):
    parser = MarkerParser()
    parser.feed(path.read_text(encoding="utf-8"))
    if len(parser.markers) != len(set(parser.markers)):
        raise ValueError(f"Duplicate annotation marker in {path.name}")
    return set(parser.markers)


def read_annotations(path):
    entries = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(entries, list) or not entries:
        raise ValueError("Annotations must be a nonempty JSON list")
    numbers = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Each annotation must be an object")
        number = entry.get("number")
        if type(number) is not int or number < 1 or number in numbers:
            raise ValueError("Annotation numbers must be unique positive integers")
        for field in ("finding_id", "change", "evidence"):
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                raise ValueError(f"Annotation {number} needs nonempty {field}")
        numbers.add(number)
    return sorted(entries, key=lambda entry: entry["number"])


def comparison_html(before, after, annotations, width, label):
    def image(path):
        return base64.b64encode(path.read_bytes()).decode("ascii")

    legend = "\n".join(
        '<li><span class="marker">{number}</span><div><strong>{finding}</strong>'
        '<p>{change}</p><p class="evidence">Evidence: {evidence}</p></div></li>'.format(
            number=entry["number"], finding=html.escape(entry["finding_id"]),
            change=html.escape(entry["change"]), evidence=html.escape(entry["evidence"]),
        ) for entry in annotations
    )
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Before and after: {label}</title>
<style>
* {{ box-sizing: border-box; }}
body {{ margin: 0; padding: 24px; background: #eee; color: #222;
        font: 16px/1.5 Arial, sans-serif; }}
h1 {{ font-size: 24px; margin: 0 0 20px; }}
.comparison {{ display: grid; grid-template-columns: {width}px {width}px 300px;
               gap: 24px; align-items: start; width: max-content; }}
figure {{ margin: 0; width: {width}px; }}
figcaption {{ font-size: 20px; font-weight: bold; padding-bottom: 12px; }}
img {{ display: block; width: {width}px; height: auto; border: 1px solid #888; }}
aside {{ background: white; border: 1px solid #888; padding: 16px; }}
aside h2 {{ font-size: 20px; margin-top: 0; }}
ol {{ list-style: none; margin: 0; padding: 0; }}
li {{ display: flex; gap: 10px; margin: 0 0 20px; overflow-wrap: anywhere; }}
.marker {{ flex: 0 0 28px; height: 28px; border-radius: 50%; background: #b42318;
           color: white; text-align: center; font-weight: bold; line-height: 28px; }}
p {{ margin: 6px 0; }} .evidence {{ font-size: 14px; color: #444; }}
</style></head><body>
<h1>Before / after wireframes: {label} ({width}px)</h1>
<div class="comparison">
<figure><figcaption>Before</figcaption><img alt="Current layout wireframe" src="data:image/png;base64,{image(before)}"></figure>
<figure><figcaption>After</figcaption><img alt="Proposed layout wireframe" src="data:image/png;base64,{image(after)}"></figure>
<aside><h2>Changes by finding</h2><ol>{legend}</ol>
<p class="evidence">Design proposal, not a measured conversion result.</p></aside>
</div></body></html>'''


def render_wireframes(source, output, after=None, annotations_path=None):
    from playwright.sync_api import sync_playwright

    source = Path(source).resolve(strict=True)
    if source.suffix.lower() not in (".html", ".htm"):
        raise ValueError("Input must be a local HTML file")
    after = Path(after).resolve(strict=True) if after else None
    if after and after.suffix.lower() not in (".html", ".htm"):
        raise ValueError("After input must be a local HTML file")
    if bool(after) != bool(annotations_path):
        raise ValueError("--after and --annotations must be supplied together")
    annotations = read_annotations(Path(annotations_path)) if annotations_path else []
    before_markers = read_markers(source)
    if after:
        numbers = {entry["number"] for entry in annotations}
        if read_markers(after) != numbers or not before_markers <= numbers:
            raise ValueError("HTML markers must match annotation numbers (all required in after)")

    output = Path(output).resolve()
    # Keep generated comparisons from overwriting their own source on a rerun.
    reserved = {output / f"before-after-{name}.html" for name in VIEWPORTS}
    if source in reserved or after in reserved:
        raise ValueError("Input cannot be a generated comparison HTML path")
    output.mkdir(parents=True, exist_ok=True)
    inputs = {"before": source, "after": after} if after else {source.stem: source}
    manifest = {"inputs": {key: str(path) for key, path in inputs.items()},
                "annotations": annotations, "renders": [], "comparisons": []}

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            for label, path in inputs.items():
                for device, (width, height) in VIEWPORTS.items():
                    context = browser.new_context(
                        viewport={"width": width, "height": height},
                        device_scale_factor=1, has_touch=device == "mobile",
                        java_script_enabled=False,
                        service_workers="block",
                    )
                    blocked = []
                    failed = []

                    def local_only(route):
                        parsed = urlparse(route.request.url)
                        if parsed.scheme == "data":
                            route.continue_()
                        elif parsed.scheme == "file" and not parsed.netloc:
                            asset = Path(unquote(parsed.path)).resolve()
                            if asset.is_relative_to(path.parent) and asset.is_file():
                                route.continue_()
                            else:
                                blocked.append(route.request.url)
                                route.abort()
                        else:
                            blocked.append(route.request.url)
                            route.abort()

                    context.route("**/*", local_only)
                    page = context.new_page()
                    page.on("requestfailed", lambda request: failed.append(request.url))
                    try:
                        page.goto(path.as_uri(), wait_until="load", timeout=30000)
                        page.evaluate("document.fonts.ready")
                        if blocked or failed:
                            raise ValueError("Missing or disallowed resources: " + ", ".join(sorted(set(blocked + failed))))
                        broken = page.locator("img").evaluate_all(
                            "imgs => imgs.filter(i => !i.complete || !i.naturalWidth).map(i => i.getAttribute('src'))"
                        )
                        if broken:
                            raise ValueError("Broken images: " + ", ".join(str(src) for src in broken))
                        metrics = page.evaluate("""() => {
                            const visible = el => {
                                const r = el.getBoundingClientRect();
                                return r.width > 0 && r.height > 0 && getComputedStyle(el).visibility !== 'hidden';
                            };
                            return {
                                content_width: document.documentElement.scrollWidth,
                                content_height: Math.max(document.body.scrollHeight, document.documentElement.scrollHeight),
                                controls: [...document.querySelectorAll('a,button,input,select,textarea,summary')]
                                    .filter(visible).map(el => {
                                        const r = el.getBoundingClientRect();
                                        return {text: (el.innerText || el.getAttribute('aria-label') || el.name || '').trim(),
                                            width: r.width, height: r.height, top: r.top,
                                            primary: el.matches('.wf-cta,[data-primary-cta]')};
                                    })
                            };
                        }""")
                        png = output / f"{label}-{device}.png"
                        page.screenshot(path=str(png), full_page=True,
                            clip={"x": 0, "y": 0, "width": width,
                                  "height": max(height, metrics["content_height"])},
                            animations="disabled", caret="hide")
                        manifest["renders"].append({"variant": label, "device": device,
                            "viewport": {"width": width, "height": height},
                            "png": str(png), **metrics})
                    finally:
                        context.close()

            if after:
                for device, (width, _) in VIEWPORTS.items():
                    comparison = output / f"before-after-{device}.html"
                    comparison.write_text(comparison_html(
                        output / f"before-{device}.png", output / f"after-{device}.png",
                        annotations, width, device,
                    ), encoding="utf-8")
                    context = browser.new_context(
                        viewport={"width": width * 2 + 396, "height": 900},
                        device_scale_factor=1, java_script_enabled=False,
                    )
                    try:
                        page = context.new_page()
                        page.goto(comparison.as_uri(), wait_until="load")
                        png = comparison.with_suffix(".png")
                        page.screenshot(path=str(png), full_page=True, animations="disabled")
                        manifest["comparisons"].append({"device": device,
                            "html": str(comparison), "png": str(png)})
                    finally:
                        context.close()
        finally:
            browser.close()
    (output / "render-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("html", help="Local HTML file (before when comparing)")
    parser.add_argument("--after", help="Local proposed HTML file")
    parser.add_argument("--annotations", help="JSON list mapping numbered markers to findings")
    parser.add_argument("--output", "-o", default="wireframe-renders", help="Output directory")
    args = parser.parse_args()
    try:
        manifest = render_wireframes(args.html, args.output, args.after, args.annotations)
    except (OSError, ValueError, ImportError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Rendering failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
