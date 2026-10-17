#!/usr/bin/env python3
"""
doctor.py — Check that the CRO skill can actually run here.

Checks the Python env, required libraries, the headless browser, internet
access and the PageSpeed API, and prints one fix per problem.

Usage:
    python doctor.py          # full check (launches the browser, fetches example.com)
    python doctor.py --quick  # libraries + browser binary only, no network
Exit 0 = ready (warnings allowed), 1 = something required is broken.
"""

import argparse
import importlib
import os
import sys
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))  # noqa: E401,E702
from netenv import dns_unavailable_but_proxied, launch_chromium  # noqa: E402,F401

HERE = os.path.dirname(os.path.abspath(__file__))
VENV = os.path.normpath(os.path.join(HERE, "..", ".venv"))
REQUIRED = ["requests", "bs4", "lxml"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    fails, warns = [], []

    in_venv = os.path.normpath(sys.prefix) == VENV
    print(f"Python: {sys.version.split()[0]} at {sys.executable}")
    if not in_venv:
        warns.append(f"Not using the skill's own env ({VENV}). Re-run install.sh to create it.")

    for mod in REQUIRED:
        try:
            importlib.import_module(mod)
            print(f"  ok   {mod}")
        except ImportError:
            fails.append(f"Missing library '{mod}'. Fix: re-run install.sh (or '{sys.executable} -m pip install {mod}').")

    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            path = p.chromium.executable_path
            if not os.path.exists(path):
                raise FileNotFoundError(path)
            print("  ok   chromium binary")
            if not a.quick:
                b = launch_chromium(p)
                b.close()
                print("  ok   chromium launches")
    except ImportError:
        warns.append("Playwright missing: no screenshots, rendering or local speed test. Fix: re-run install.sh.")
    except Exception as exc:
        warns.append(f"Headless browser not usable ({str(exc)[:100]}). Fix: '{sys.executable} -m playwright install chromium'"
                     f" (Linux may also need: '{sys.executable} -m playwright install-deps chromium').")

    if not a.quick and not fails:
        sys.path.insert(0, HERE)
        try:
            import fetch_page
            r = fetch_page.fetch_page("https://example.com", timeout=15)
            print(f"  ok   internet (example.com HTTP {r['status_code']})")
        except Exception as exc:
            fails.append(f"Cannot fetch https://example.com ({exc}). Check network or proxy. In Claude Code on the web, set the cloud environment network access to Full, or allow your site.")
        try:
            import requests
            r = requests.get("https://www.googleapis.com/pagespeedonline/v5/runPagespeed",
                             params={"url": "https://example.com", "category": "performance",
                                     **({"key": os.environ["PAGESPEED_API_KEY"]} if os.environ.get("PAGESPEED_API_KEY") else {})},
                             timeout=90)
            if r.status_code == 200:
                print("  ok   PageSpeed API")
            else:
                warns.append(f"PageSpeed API HTTP {r.status_code}: speed checks fall back to a local browser run "
                             "(no real-user data). Fix: set PAGESPEED_API_KEY (free key from Google Cloud).")
        except Exception as exc:
            warns.append(f"PageSpeed API unreachable ({str(exc)[:80]}); local fallback will be used.")

    for w in warns:
        print(f"  WARN {w}")
    for f in fails:
        print(f"  FAIL {f}")
    print("DOCTOR " + ("FAIL" if fails else "OK"))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
