#!/usr/bin/env python3
"""
capture.py — Collect everything the audit agents need for one page, once.

Writes into <dir>: raw.html, page.html (browser-rendered), fetch.json,
elements.json, desktop.png, mobile.png, mobile-full.png, speed.json (mobile),
and gaps.txt listing anything that failed. Failures of optional parts are
recorded, not fatal.

Usage:
    python capture.py https://shop.example/products/x W/pages/product [--no-speed]
Exit 0 = captured, 3 = page looks blocked (see fetch.json), 1 = page unreachable.
"""

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run(args, out=None):
    r = subprocess.run([sys.executable, os.path.join(HERE, args[0]), *args[1:]],
                       capture_output=True, text=True, timeout=300)
    if out is not None:
        with open(out, "w", encoding="utf-8") as f:
            f.write(r.stdout)
    return r


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument("dir")
    ap.add_argument("--no-speed", action="store_true")
    a = ap.parse_args()
    d = a.dir
    os.makedirs(d, exist_ok=True)
    gaps = []

    r = run(["fetch_page.py", a.url, "--output", f"{d}/raw.html", "--json"], f"{d}/fetch-raw.json")
    if r.returncode == 1:
        print(f"Error: cannot fetch {a.url}: {r.stdout.strip() or r.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    r = run(["fetch_page.py", a.url, "--render", "--output", f"{d}/page.html", "--json"], f"{d}/fetch.json")
    blocked = json.load(open(f"{d}/fetch.json")).get("blocked")
    if blocked:
        gaps.append(f"page looks blocked: {blocked}")
    if run(["parse_cro.py", f"{d}/page.html", "--base-url", a.url, "--json"], f"{d}/elements.json").returncode:
        gaps.append("parse_cro failed")

    for name, extra in (("desktop.png", ["-W", "1440", "-H", "900"]),
                        ("mobile.png", ["--mobile"]),
                        ("mobile-full.png", ["--mobile", "--full-page"])):
        if run(["capture_screenshot.py", a.url, "-o", f"{d}/{name}", *extra]).returncode:
            gaps.append(f"screenshot {name} failed")

    if not a.no_speed:
        r = run(["pagespeed.py", a.url, "--strategy", "mobile", "--json"], f"{d}/speed.json")
        if r.returncode:
            gaps.append("speed measurement failed")
        elif "PageSpeed API unavailable" in r.stderr:
            gaps.append("PageSpeed API unavailable: lab-only local measurement, no real-user data")

    with open(f"{d}/gaps.txt", "w") as f:
        f.write("\n".join(gaps) + ("\n" if gaps else ""))
    print(f"Captured {a.url} -> {d}" + (f" ({len(gaps)} gap(s): {'; '.join(gaps)})" if gaps else ""))
    sys.exit(3 if blocked else 0)


if __name__ == "__main__":
    main()
