#!/usr/bin/env python3
"""
pagespeed.py — Core Web Vitals from Google PageSpeed Insights.

Returns lab metrics (Lighthouse) and, when Google has enough Chrome users for
the URL, real-user field data (CrUX): LCP, INP, CLS, FCP, TTFB.
Works without a key at low volume; set PAGESPEED_API_KEY for higher limits.

Usage:
    python pagespeed.py https://example.com
    python pagespeed.py https://example.com --strategy desktop --json
"""

import argparse
import json
import os
import sys

import requests

API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
FIELD = {
    "LARGEST_CONTENTFUL_PAINT_MS": ("LCP", "ms"),
    "INTERACTION_TO_NEXT_PAINT": ("INP", "ms"),
    "CUMULATIVE_LAYOUT_SHIFT_SCORE": ("CLS", ""),
    "FIRST_CONTENTFUL_PAINT_MS": ("FCP", "ms"),
    "EXPERIMENTAL_TIME_TO_FIRST_BYTE": ("TTFB", "ms"),
}
LAB = {
    "largest-contentful-paint": "LCP",
    "cumulative-layout-shift": "CLS",
    "total-blocking-time": "TBT",
    "first-contentful-paint": "FCP",
    "speed-index": "Speed Index",
    "server-response-time": "TTFB",
}


def run(url: str, strategy: str) -> dict:
    params = {"url": url, "strategy": strategy, "category": "performance"}
    key = os.environ.get("PAGESPEED_API_KEY")
    if key:
        params["key"] = key
    r = requests.get(API, params=params, timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"PageSpeed API {r.status_code}: {r.text[:300]}")
    d = r.json()
    lh = d.get("lighthouseResult", {})
    audits = lh.get("audits", {})
    field_src = d.get("loadingExperience", {})
    field = {}
    for k, (name, unit) in FIELD.items():
        m = field_src.get("metrics", {}).get(k)
        if m:
            v = m["percentile"] / 100 if k.startswith("CUMULATIVE") else m["percentile"]
            field[name] = {"p75": v, "unit": unit, "rating": m.get("category")}
    opportunities = sorted(
        (
            {"id": a["id"], "title": a["title"], "savings_ms": round(a["details"]["overallSavingsMs"])}
            for a in audits.values()
            if a.get("details", {}).get("overallSavingsMs", 0) >= 100
        ),
        key=lambda o: -o["savings_ms"],
    )[:8]
    return {
        "url": url,
        "strategy": strategy,
        "performance_score": round(lh.get("categories", {}).get("performance", {}).get("score", 0) * 100),
        "field_data": field or None,
        "field_data_scope": field_src.get("id") and ("origin" if field_src.get("origin_fallback") else "url"),
        "lab": {name: audits[k].get("displayValue") for k, name in LAB.items() if k in audits},
        "opportunities": opportunities,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument("--strategy", choices=["mobile", "desktop"], default="mobile")
    ap.add_argument("--json", action="store_true", dest="json_output")
    a = ap.parse_args()
    url = a.url if a.url.startswith(("http://", "https://")) else "https://" + a.url
    try:
        res = run(url, a.strategy)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    if a.json_output:
        print(json.dumps(res, indent=2))
        return
    print(f"{res['strategy']} performance score: {res['performance_score']}/100")
    if res["field_data"]:
        print(f"Field data (real Chrome users, p75, scope: {res['field_data_scope']}):")
        for n, m in res["field_data"].items():
            print(f"  {n}: {m['p75']}{m['unit']} ({m['rating']})")
    else:
        print("Field data: none (not enough real-user traffic in CrUX)")
    print("Lab:", ", ".join(f"{k} {v}" for k, v in res["lab"].items()))
    for o in res["opportunities"]:
        print(f"  - {o['title']}: ~{o['savings_ms']}ms")


if __name__ == "__main__":
    main()
