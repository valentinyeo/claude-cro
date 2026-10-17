#!/usr/bin/env python3
"""
journey.py — Replay a visitor journey in a real browser and screenshot every step.

A persona agent writes steps as JSON, runs them, looks at the screenshots, then
appends the next step and runs again (each run replays from the start, so it is
stateless and reproducible). Stops at checkout pages; never submits payment.

Steps file (JSON list):
  [{"goto": "https://shop.example"},
   {"click": "text=Shop Men"},                 # Playwright selector or text=
   {"fill": "input[type=email]", "value": "test@example.com"},
   {"scroll": 1200},
   {"wait": 2},
   {"note": "looking for size guide"}]

Usage:
    python journey.py steps.json --out journey/ [--mobile]
Writes journey/step-NN.png and journey/log.json; exit 1 if a step fails.
"""

import argparse
import importlib.util
import json
import os
import sys
import time
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))  # noqa: E401,E702
from netenv import dns_unavailable_but_proxied, launch_chromium  # noqa: E402,F401

_spec = importlib.util.spec_from_file_location(
    "fetch_page_mod", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fetch_page.py"))
fp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fp)

STOP_WORDS = ("place order", "pay now", "complete order", "complete purchase", "submit order", "confirm payment")


def find(page, sel, timeout=10):
    """First visible match in the page or any iframe (popups often live in iframes)."""
    end = time.time() + timeout
    while time.time() < end:
        for frame in page.frames:
            loc = frame.locator(f"{sel} >> visible=true")
            try:
                if loc.count():
                    return loc.first
            except Exception:
                pass
        page.wait_for_timeout(500)
    raise RuntimeError(f"no visible element for {sel!r}")


def run(steps, out, mobile):
    from playwright.sync_api import sync_playwright

    os.makedirs(out, exist_ok=True)
    log, ok = [], True
    with sync_playwright() as p:
        browser = launch_chromium(p)
        ctx = browser.new_context(**p.devices["iPhone 13"]) if mobile else browser.new_context(
            viewport={"width": 1440, "height": 900}, user_agent=fp.DEFAULT_USER_AGENT)
        fp.guard_browser(ctx)
        page = ctx.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)[:200]))
        for i, step in enumerate(steps, 1):
            entry = {"n": i, "step": step}
            t0 = time.time()
            try:
                if "goto" in step:
                    page.goto(step["goto"], wait_until="domcontentloaded", timeout=45000)
                    try:
                        page.wait_for_load_state("networkidle", timeout=8000)
                    except Exception:
                        pass
                elif "click" in step:
                    sel = step["click"]
                    if any(w in sel.lower() for w in STOP_WORDS):
                        raise RuntimeError("refused: journeys stop before payment")
                    find(page, sel).click(timeout=8000)
                    page.wait_for_timeout(1500)
                elif "fill" in step:
                    find(page, step["fill"]).fill(step.get("value", ""), timeout=8000)
                elif "scroll" in step:
                    page.mouse.wheel(0, int(step["scroll"]))
                    page.wait_for_timeout(800)
                elif "wait" in step:
                    page.wait_for_timeout(int(float(step["wait"]) * 1000))
                entry["status"] = "ok"
            except Exception as exc:
                entry["status"] = "failed"
                entry["error"] = str(exc).splitlines()[0][:200]
                ok = False
            entry["ms"] = round((time.time() - t0) * 1000)
            entry["url"] = page.url
            entry["title"] = page.title()
            shot = os.path.join(out, f"step-{i:02d}.png")
            try:
                page.screenshot(path=shot)
                entry["screenshot"] = shot
            except Exception:
                pass
            log.append(entry)
            if not ok:
                break
        browser.close()
    result = {"ok": ok, "steps": log, "js_errors": errors}
    with open(os.path.join(out, "log.json"), "w") as f:
        json.dump(result, f, indent=2)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("steps")
    ap.add_argument("--out", default="journey")
    ap.add_argument("--mobile", action="store_true")
    a = ap.parse_args()
    steps = json.load(open(a.steps))
    r = run(steps, a.out, a.mobile)
    for e in r["steps"]:
        print(f"{e['n']:>2} {e['status']:<6} {e['ms']:>5}ms  {json.dumps(e['step'])[:70]:<70} -> {e['url'][:80]}"
              + (f"  ERROR {e['error']}" if e.get("error") else ""))
    if r["js_errors"]:
        print("JS errors:", *r["js_errors"][:5], sep="\n  ")
    sys.exit(0 if r["ok"] else 1)


if __name__ == "__main__":
    main()
