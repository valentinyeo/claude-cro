#!/usr/bin/env python3
"""
pagespeed.py — Core Web Vitals from Google PageSpeed Insights.

Returns lab metrics (Lighthouse) and, when Google has enough Chrome users for
the URL, real-user field data (CrUX): LCP, INP, CLS, FCP, TTFB.
Works without a key at low volume; set PAGESPEED_API_KEY for higher limits.
If the API fails (quota, outage), falls back to a local lab run: headless
Chromium with mobile emulation, 4x CPU slowdown and slow-4G network, measuring
LCP, CLS, FCP, TTFB and Total Blocking Time. Lab only: no real-user data.

Usage:
    python pagespeed.py https://example.com
    python pagespeed.py https://example.com --strategy desktop --json
    python pagespeed.py https://example.com --local
"""

import argparse
import json
import os
import sys
from urllib.parse import urlparse

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


LOCAL_JS = """
() => new Promise(resolve => {
  const out = {lcp: 0, cls: 0, tbt: 0};
  new PerformanceObserver(l => { for (const e of l.getEntries()) out.lcp = e.startTime; })
    .observe({type: 'largest-contentful-paint', buffered: true});
  new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) out.cls += e.value; })
    .observe({type: 'layout-shift', buffered: true});
  new PerformanceObserver(l => { for (const e of l.getEntries()) out.tbt += Math.max(0, e.duration - 50); })
    .observe({type: 'longtask', buffered: true});
  setTimeout(() => {
    const nav = performance.getEntriesByType('navigation')[0] || {};
    const fcp = performance.getEntriesByName('first-contentful-paint')[0];
    out.ttfb = nav.responseStart || 0;
    out.fcp = fcp ? fcp.startTime : 0;
    out.load = nav.loadEventEnd || 0;
    out.requests = performance.getEntriesByType('resource').length;
    out.transfer_kb = Math.round(performance.getEntriesByType('resource')
      .reduce((a, r) => a + (r.transferSize || 0), 0) / 1024);
    resolve(out);
  }, 4000);
})
"""


def _fetch_mod():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "fetch_page_mod", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fetch_page.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_local(url: str, strategy: str) -> dict:
    """Throttled lab measurement in headless Chromium (no Google API needed)."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            if strategy == "mobile":
                ctx = browser.new_context(**p.devices["Pixel 7"])
            else:
                ctx = browser.new_context(viewport={"width": 1440, "height": 900})
            _fetch_mod().guard_browser(ctx)
            _fetch_mod().resolve_and_check(urlparse(url).hostname)
            page = ctx.new_page()
            cdp = ctx.new_cdp_session(page)
            if strategy == "mobile":
                cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
                cdp.send("Network.enable")
                cdp.send("Network.emulateNetworkConditions", {
                    "offline": False, "latency": 150,
                    "downloadThroughput": 1.6 * 1024 * 1024 / 8,
                    "uploadThroughput": 750 * 1024 / 8,
                })
            page.goto(url, wait_until="load", timeout=90000)
            m = page.evaluate(LOCAL_JS)
        finally:
            browser.close()

    def rate(v, good, poor):
        return "FAST" if v <= good else ("AVERAGE" if v <= poor else "SLOW")

    lab = {
        "LCP": f"{m['lcp'] / 1000:.1f} s ({rate(m['lcp'], 2500, 4000)})",
        "CLS": f"{m['cls']:.3f} ({rate(m['cls'], 0.1, 0.25)})",
        "TBT": f"{round(m['tbt'])} ms ({rate(m['tbt'], 200, 600)})",
        "FCP": f"{m['fcp'] / 1000:.1f} s",
        "TTFB": f"{round(m['ttfb'])} ms",
        "Requests": str(m["requests"]),
        "Transfer": f"{m['transfer_kb']} KB",
    }
    return {
        "url": url,
        "strategy": strategy,
        "source": "local-lab (headless Chromium, throttled; not Lighthouse, no real-user data)",
        "performance_score": None,
        "field_data": None,
        "field_data_scope": None,
        "lab": lab,
        "opportunities": [],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument("--strategy", choices=["mobile", "desktop"], default="mobile")
    ap.add_argument("--json", action="store_true", dest="json_output")
    ap.add_argument("--local", action="store_true", help="Skip the Google API and measure locally")
    a = ap.parse_args()
    url = a.url if a.url.startswith(("http://", "https://")) else "https://" + a.url
    res = None
    if not a.local:
        try:
            res = run(url, a.strategy)
            res["source"] = "PageSpeed Insights API"
        except Exception as exc:
            print(f"Note: PageSpeed API unavailable ({str(exc)[:120]}); measuring locally.", file=sys.stderr)
    if res is None:
        try:
            res = run_local(url, a.strategy)
        except Exception as exc:
            print(f"Error: local measurement failed: {exc}", file=sys.stderr)
            sys.exit(1)
    if a.json_output:
        print(json.dumps(res, indent=2))
        return
    print(f"Source: {res['source']}")
    if res["performance_score"] is not None:
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
