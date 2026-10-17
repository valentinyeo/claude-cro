#!/usr/bin/env python3
"""Preview a CRO_TEST-manifest variant and save control/variant screenshots.

Usage: cro-py preview_variant.py <url> variant.js [--css variant.css] [--mobile]
Writes <variant folder>/preview-{desktop,mobile}/report.json and four PNGs.
The required /* CRO_TEST {...} */ manifest lists every selector and exact count.
"""

import argparse
from functools import lru_cache
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

from fetch_page import DEFAULT_USER_AGENT, looks_blocked, resolve_and_check, validate_url
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))  # noqa: E401,E702
from netenv import dns_unavailable_but_proxied, launch_chromium  # noqa: E402,F401


def read_manifest(source):
    match = re.search(r"/\*\s*CRO_TEST\s+(\{.*?\})\s*\*/", source, re.S)
    if not match:
        raise ValueError("Missing /* CRO_TEST {JSON} */ selector manifest")
    manifest = json.loads(match.group(1))
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,59}", manifest.get("id", "")):
        raise ValueError("Manifest id must be a lowercase slug, starting with a letter")
    selectors = manifest.get("selectors")
    if not isinstance(selectors, list) or not selectors:
        raise ValueError("Manifest must list every targeted selector")
    for item in selectors:
        if (not isinstance(item, dict) or not isinstance(item.get("selector"), str)
                or not item["selector"].strip() or type(item.get("count")) is not int
                or item["count"] < 1):
            raise ValueError("Each manifest selector needs a nonempty selector and positive count")
    timeout = manifest.get("timeout_ms", 10000)
    if type(timeout) is not int or not 100 <= timeout <= 60000:
        raise ValueError("Manifest timeout_ms must be 100..60000")
    return manifest


def preview(url, variant, css=None, mobile=False, output=None, timeout=30, settle=2,
            dismiss_selectors=None):
    from playwright.sync_api import sync_playwright

    source = Path(variant).read_text(encoding="utf-8")
    manifest = read_manifest(source)
    styles = Path(css).read_text(encoding="utf-8") if css else None
    url = validate_url(url)
    resolve_and_check(urlparse(url).hostname)
    output = Path(output or Path(variant).parent / ("preview-mobile" if mobile else "preview-desktop"))
    output.mkdir(parents=True, exist_ok=True)
    report = {
        "url": url, "id": manifest["id"], "mobile": mobile,
        "console_errors": [], "page_errors": [], "selectors": [],
        "blocked_requests": [], "screenshots": {}, "errors": [], "dismissed": [],
        "note": "Local preview only. CSP is bypassed for injection; verify the platform and consent flow separately.",
    }
    phase = "control"

    @lru_cache(maxsize=256)
    def check_host(host):
        resolve_and_check(host)

    def guard(route):
        parsed = urlparse(route.request.url)
        try:
            if parsed.scheme in ("http", "https"):
                check_host(parsed.hostname)
            route.continue_()
        except ValueError as exc:
            report["blocked_requests"].append({"url": route.request.url, "error": str(exc)})
            route.abort()

    with sync_playwright() as p:
        browser = launch_chromium(p)
        try:
            options = {"viewport": {"width": 1440, "height": 900},
                       "user_agent": DEFAULT_USER_AGENT, "bypass_csp": True,
                       "service_workers": "block"}
            if mobile:
                options.update(p.devices["iPhone 13"])
                options.pop("default_browser_type", None)
            context = browser.new_context(**options)
            context.route("**/*", guard)
            page = context.new_page()
            page.on("console", lambda msg: report["console_errors"].append(
                {"phase": phase, "text": msg.text}) if msg.type == "error" else None)
            page.on("pageerror", lambda error: report["page_errors"].append(
                {"phase": phase, "text": str(error)}))
            response = page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)
            try:
                page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                pass
            page.wait_for_timeout(settle * 1000)
            report["final_url"] = page.url
            resolve_and_check(urlparse(page.url).hostname)
            blocked = looks_blocked(response.status if response else 0, page.content())
            if blocked:
                raise ValueError(f"Page is blocked or empty: {blocked}")

            def screenshots(label):
                page.evaluate("window.scrollTo(0, 0)")
                for suffix, full in (("viewport", False), ("full", True)):
                    path = output / f"{label}-{suffix}.png"
                    page.screenshot(path=str(path), full_page=full, animations="disabled")
                    report["screenshots"][f"{label}_{suffix}"] = str(path.resolve())

            for selector in dismiss_selectors or []:
                # Explicit opt-in actions only, applied equally to both screenshots.
                parts = selector.split("::frame::")
                scope = page
                for frame_selector in parts[:-1]:
                    scope = scope.frame_locator(frame_selector)
                scope.locator(parts[-1]).click(timeout=10000)
                report["dismissed"].append(selector)
            if dismiss_selectors:
                page.wait_for_timeout(settle * 1000)
            screenshots("control")
            phase = "variant"
            if styles is not None:
                page.evaluate("""({id, text}) => {
                    if (!document.getElementById(id)) {
                        const style = document.createElement('style');
                        style.id = id; style.textContent = text; document.head.append(style);
                    }
                }""", {"id": f"cro-{manifest['id']}-style", "text": styles})
            try:
                page.add_script_tag(content=source)
                # A manifest cannot make a missing selector look like a successful preview.
                page.wait_for_function("""m => m.selectors.every(item =>
                    document.querySelectorAll(item.selector).length === item.count) &&
                    (m.runtime_required ?
                      (window.__croTests && window.__croTests[m.id] && window.__croTests[m.id].applied === true) :
                      (!window.__croTests || !window.__croTests[m.id] || window.__croTests[m.id].applied === true))
                """, arg=manifest, timeout=manifest.get("timeout_ms", 10000) + 500)
                page.wait_for_timeout(settle * 1000)
            except Exception as exc:
                report["errors"].append(str(exc))
            for item in manifest["selectors"]:
                try:
                    count = page.locator(item["selector"]).count()
                    report["selectors"].append({**item, "found": count, "ok": count == item["count"]})
                except Exception as exc:
                    report["selectors"].append({**item, "found": None, "ok": False, "error": str(exc)})
            report["runtime"] = page.evaluate(
                "id => (window.__croTests && window.__croTests[id]) || null", manifest["id"])
            if report["runtime"] and report["runtime"].get("errors"):
                report["errors"].extend(report["runtime"]["errors"])
            screenshots("variant")
        except Exception as exc:
            report["errors"].append(str(exc))
        finally:
            browser.close()
    report["ok"] = (not report["errors"] and bool(report["selectors"])
                    and all(item["ok"] for item in report["selectors"])
                    and not any(error["phase"] == "variant" for error in report["page_errors"]))
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("url")
    ap.add_argument("variant")
    ap.add_argument("--css")
    ap.add_argument("--mobile", action="store_true")
    ap.add_argument("--output", "-o", help="Output directory (default: beside variant.js)")
    ap.add_argument("--timeout", type=int, default=30, help="Navigation timeout in seconds")
    ap.add_argument("--settle", type=float, default=2, help="Render settling time in seconds")
    ap.add_argument("--dismiss-selector", action="append", default=[],
                    help="Click a known overlay close/reject control before both captures; repeatable. Use iframe-selector::frame::button-selector for frames")
    args = ap.parse_args()
    if args.timeout <= 0 or args.settle < 0:
        ap.error("timeout must be positive and settle must be nonnegative")
    try:
        report = preview(args.url, args.variant, args.css, args.mobile,
                         args.output, args.timeout, args.settle, args.dismiss_selector)
    except Exception as exc:
        print(json.dumps({"ok": False, "errors": [str(exc)]}, indent=2))
        return 1
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
