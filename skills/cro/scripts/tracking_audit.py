#!/usr/bin/env python3
"""
tracking_audit.py — Inventory every tracker and pixel a page really fires, flag duplicates and
misconfigurations, and list the access to ask the client for so the audit can read real numbers.

Loads each page in Chromium, records every network request (before any consent click), and
matches them to vendors with their IDs (GA4 G-..., GTM-..., AW-..., Meta pixel id, TikTok sdkid,
LinkedIn pid, Clarity, Hotjar, Cloudflare Web Analytics, PostHog, Plausible, HubSpot ...).

Flags:
  - no measurement at all (no baseline possible)
  - the same tag loaded twice, or the same page_view sent twice for one page load (double counting)
  - GA4 sent both by a hardcoded gtag and through GTM
  - several IDs of one vendor (two GA4 properties, two Meta pixels): confirm on purpose
  - retired Universal Analytics (UA-) hits
  - trackers firing before consent while a consent banner is on screen

Usage:
    python tracking_audit.py <url> [<url> ...] [--json] [--out tracking.json] [--md TRACKING.md]
Note: the audit's own page loads reach the client's analytics as a few extra visits.
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from urllib.parse import parse_qs, urlparse
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))  # noqa: E401,E702
from netenv import dns_unavailable_but_proxied, launch_chromium  # noqa: E402,F401

# name, url pattern, how to pull the account id, how to pull the hit/event name, kind
VENDORS = [
    ("GA4", r"google-analytics\.com/g/collect|analytics\.google\.com/g/collect|/g/collect\?.*tid=G-", "q:tid", "q:en", "hit"),
    ("Google tag (gtag.js)", r"googletagmanager\.com/gtag/js", "q:id", None, "loader"),
    ("Google Tag Manager", r"googletagmanager\.com/gtm\.js", "q:id", None, "loader"),
    ("Google Ads", r"googleadservices\.com/pagead/conversion|google\.com/pagead/1p-conversion|doubleclick\.net/pagead/viewthroughconversion", r"r:/conversion/(\d+)", None, "hit"),
    ("Universal Analytics (retired)", r"google-analytics\.com/(r/|j/)?collect\?.*tid=UA-|google-analytics\.com/analytics\.js", "q:tid", "q:t", "hit"),
    ("Meta Pixel", r"facebook\.com/tr[/?]", "q:id", "q:ev", "hit"),
    ("Meta Pixel", r"connect\.facebook\.net/.*/fbevents\.js", None, None, "loader"),
    ("TikTok Pixel", r"analytics\.tiktok\.com/i18n/pixel/events\.js", "q:sdkid", None, "loader"),
    ("TikTok Pixel", r"analytics\.tiktok\.com/api/v\d/pixel", None, None, "hit"),
    ("LinkedIn Insight", r"px\.ads\.linkedin\.com/(collect|attribution_trigger)", "q:pid", None, "hit"),
    ("LinkedIn Insight", r"snap\.licdn\.com/li\.lms-analytics", None, None, "loader"),
    ("Microsoft Clarity", r"clarity\.ms/tag/", r"r:clarity\.ms/tag/([a-z0-9]*\d[a-z0-9]*)", None, "loader"),
    ("Microsoft Clarity", r"[a-z]\.clarity\.ms/collect", None, None, "hit"),
    ("Microsoft Ads (UET)", r"bat\.bing\.com/action", "q:ti", "q:evt", "hit"),
    ("Hotjar", r"static\.hotjar\.com/c/hotjar-", r"r:hotjar-(\d+)", None, "loader"),
    ("Pinterest Tag", r"ct\.pinterest\.com/(v3|user)", "q:tid", "q:event", "hit"),
    ("Snap Pixel", r"tr\.snapchat\.com/", None, None, "hit"),
    ("Reddit Pixel", r"alb\.reddit\.com/rp\.gif", "q:id", "q:event", "hit"),
    ("X (Twitter) Pixel", r"analytics\.twitter\.com/i/adsct|t\.co/i/adsct", "q:txn_id", None, "hit"),
    ("Cloudflare Web Analytics", r"static\.cloudflareinsights\.com/beacon", None, None, "loader"),
    ("Cloudflare Web Analytics", r"cloudflareinsights\.com/cdn-cgi/rum|/cdn-cgi/rum", None, None, "hit"),
    ("PostHog", r"(us|eu)\.i\.posthog\.com/(e|i/v0/e|batch|decide)|app\.posthog\.com/(e|decide)", None, None, "hit"),
    ("PostHog", r"posthog.*array\.js|us-assets\.i\.posthog\.com/static", None, None, "loader"),
    ("Plausible", r"plausible\.io/(api/event|js/)", None, None, "hit"),
    ("Fathom", r"cdn\.usefathom\.com", None, None, "loader"),
    ("Matomo", r"matomo\.(php|js)|piwik\.(php|js)", "q:idsite", None, "hit"),
    ("Segment", r"cdn\.segment\.com/analytics\.js|api\.segment\.io/v1", None, None, "hit"),
    ("HubSpot", r"js\.hs-scripts\.com/(\d+)\.js|track\.hubspot\.com/__pt", r"r:hs-scripts\.com/(\d+)", None, "loader"),
    ("Klaviyo", r"static\.klaviyo\.com/onsite/js/klaviyo\.js|a\.klaviyo\.com/", "q:company_id", None, "loader"),
    ("Mixpanel", r"api(-js)?\.mixpanel\.com/track", None, None, "hit"),
    ("Amplitude", r"api2?\.amplitude\.com|cdn\.amplitude\.com", None, None, "hit"),
    ("Heap", r"heapanalytics\.com", None, None, "hit"),
    ("FullStory", r"fullstory\.com/s/fs\.js|rs\.fullstory\.com", None, None, "hit"),
    ("Vercel Analytics", r"/_vercel/insights", None, None, "hit"),
    ("Umami", r"umami\.is/script\.js|/api/send$", None, None, "hit"),
    # experimentation tools: not analytics, but they change what visitors see
    ("Endless Testing", r"endlesstesting\.ai/api/sdk", None, None, "testing"),
    ("VWO", r"dev\.visualwebsiteoptimizer\.com|vwo\.com/j\.php", "q:a", None, "testing"),
    ("Optimizely", r"cdn\.optimizely\.com/js/(\d+)", r"r:optimizely\.com/js/(\d+)", None, "testing"),
    ("AB Tasty", r"try\.abtasty\.com", None, None, "testing"),
    ("Convert", r"cdn-\d+\.convertexperiments\.com", None, None, "testing"),
    ("Kameleoon", r"kameleoon\.(eu|io|com)", None, None, "testing"),
    ("GrowthBook", r"cdn\.growthbook\.io|growthbook", None, None, "testing"),
    ("Statsig", r"statsigapi\.net|cdn\.statsig", None, None, "testing"),
    ("Google Optimize (retired)", r"googleoptimize\.com", None, None, "testing"),
]
TESTING_TOOLS = {n for n, _, _, _, k in VENDORS if k == "testing"}
COMPILED = [(n, re.compile(p, re.I), idr, evr, kind) for n, p, idr, evr, kind in VENDORS]

ACCESS = {
    "GA4": "GA4 property {id}: Viewer access (Admin > Property access management) so we can read traffic, funnels and conversions",
    "Google tag (gtag.js)": "Google tag {id}: Viewer access to the GA4 property or Google Ads account it sends to",
    "Google Tag Manager": "GTM container {id}: Read access (Admin > User management) to check triggers and duplicate tags",
    "Google Ads": "Google Ads account (conversion {id}): read-only access to check conversion actions and attribution",
    "Universal Analytics (retired)": "Old UA property {id}: no longer collects data; confirm it is removed",
    "Meta Pixel": "Meta pixel {id}: partner access to the dataset in Events Manager (Business settings > Data sources)",
    "TikTok Pixel": "TikTok pixel {id}: analyst access in TikTok Events Manager",
    "LinkedIn Insight": "LinkedIn Insight tag {id}: viewer on the Campaign Manager account",
    "Microsoft Clarity": "Clarity project {id}: team member access to watch session recordings and heatmaps",
    "Microsoft Ads (UET)": "Microsoft Ads UET tag {id}: read-only account access",
    "Hotjar": "Hotjar site {id}: observer access to recordings and heatmaps",
    "Pinterest Tag": "Pinterest tag {id}: analyst access to the ad account",
    "Reddit Pixel": "Reddit pixel {id}: viewer on the ad account",
    "Cloudflare Web Analytics": "Cloudflare: an API token with Account Analytics Read (or a Web Analytics viewer seat)",
    "PostHog": "PostHog project: viewer access (or a read-only personal API key)",
    "Plausible": "Plausible site: a shared dashboard link or viewer access",
    "HubSpot": "HubSpot portal {id}: viewer seat for forms, contacts and deal sources",
    "Klaviyo": "Klaviyo account {id}: read-only user for signup forms and flows",
    "Matomo": "Matomo site {id}: view access",
}
ALWAYS = [
    "Google Search Console: restricted user, to see search queries and landing pages",
    "Conversion count for the last 3 months (orders, leads or form submissions from the inbox or CRM), "
    "so the test readiness baseline is CONFIRMED rather than ASSUMED",
]
NO_ANALYTICS_ASK = [
    "Host or CDN analytics (Cloudflare: an API token with Account Analytics Read and Zone Analytics Read): "
    "the only traffic numbers that exist while no analytics tool is installed",
]
CONSENT_TEXT = re.compile(r"cookie|consent|gdpr|privacy (settings|preferences)|accept all|we use cookies", re.I)


def classify(url):
    for name, rx, idr, evr, kind in COMPILED:
        if rx.search(url):
            q = parse_qs(urlparse(url).query)
            return {"vendor": name, "kind": kind, "id": _pull(url, q, idr), "event": _pull(url, q, evr)}
    return None


def _pull(url, q, rule):
    if not rule:
        return None
    if rule.startswith("q:"):
        return (q.get(rule[2:]) or [None])[0]
    m = re.search(rule[2:], url, re.I)
    return m.group(1) if m else None


def analyze(pages):
    """pages: [{"url", "requests": [url, ...], "consent_banner": bool, "html_ids": {...}}]. Pure, testable."""
    inventory = defaultdict(lambda: {"ids": set(), "pages": set(), "loads": 0, "hits": 0, "events": Counter()})
    issues = []
    for pg in pages:
        loaders, hits = Counter(), Counter()
        seen = []
        for u in pg["requests"]:
            c = classify(u)
            if not c:
                continue
            seen.append(c)
            inv = inventory[c["vendor"]]
            inv["pages"].add(pg["url"])
            if c["id"]:
                inv["ids"].add(c["id"])
            if c["kind"] == "loader":
                inv["loads"] += 1
                loaders[(c["vendor"], c["id"])] += 1
            else:
                inv["hits"] += 1
                if c["event"]:
                    inv["events"][c["event"]] += 1
                    hits[(c["vendor"], c["id"], c["event"])] += 1
        for (vendor, vid), n in loaders.items():
            if n > 1:
                issues.append({"severity": "high", "page": pg["url"], "issue": "duplicate_tag",
                               "detail": f"{vendor} {vid or ''} is loaded {n} times on one page load".replace("  ", " ")})
        for (vendor, vid, ev), n in hits.items():
            if ev and ev.lower() in ("page_view", "pageview", "pagevisit", "pv", "page") and n > 1:
                issues.append({"severity": "critical", "page": pg["url"], "issue": "double_counting",
                               "detail": f"{vendor} {vid} sent {ev} {n} times for one page load: page views and "
                                         f"conversion rates in this tool are inflated"})
        gtm = any(c["vendor"] == "Google Tag Manager" for c in seen)
        hard = {c["id"] for c in seen if c["vendor"] == "Google tag (gtag.js)" and (c["id"] or "").startswith("G-")}
        ga4_pv = {c["id"] for c in seen if c["vendor"] == "GA4" and (c["event"] or "") == "page_view"}
        if gtm and hard & ga4_pv and hits.get(("GA4", next(iter(hard & ga4_pv)), "page_view"), 0) > 1:
            issues.append({"severity": "high", "page": pg["url"], "issue": "gtm_and_hardcoded_ga4",
                           "detail": f"GA4 {', '.join(sorted(hard))} is installed both in the page code and through GTM"})
        if pg.get("consent_banner") and seen:
            vendors = sorted({c["vendor"] for c in seen if c["vendor"] not in ("Cloudflare Web Analytics",)})
            if vendors:
                issues.append({"severity": "high", "page": pg["url"], "issue": "fires_before_consent",
                               "detail": f"a consent banner is showing, but {', '.join(vendors)} already sent data "
                                         f"before anyone clicked it (check Consent Mode / blocking)"})
    for vendor, inv in inventory.items():
        real_ids = {i for i in inv["ids"] if i}
        if vendor in ("GA4", "Meta Pixel", "TikTok Pixel", "Google Tag Manager") and len(real_ids) > 1:
            issues.append({"severity": "medium", "page": "site", "issue": "several_ids",
                           "detail": f"{vendor} has {len(real_ids)} IDs ({', '.join(sorted(real_ids))}): data is split "
                                     f"or doubled unless this is on purpose"})
        if vendor == "Universal Analytics (retired)":
            issues.append({"severity": "medium", "page": "site", "issue": "retired_tool",
                           "detail": f"Universal Analytics {', '.join(sorted(real_ids))} stopped processing data in 2024; remove it"})
    testing = sorted(v for v in inventory if v in TESTING_TOOLS)
    if testing:
        issues.append({"severity": "medium", "page": "site", "issue": "testing_tool",
                       "detail": f"A/B testing tool running: {', '.join(testing)}. Check the test plan against the "
                                 f"readiness verdict: with too few conversions a test cannot reach a result, and "
                                 f"without analytics there is nothing to read it against"})
    analytics = [v for v in inventory if v not in TESTING_TOOLS and v not in ("Meta Pixel", "TikTok Pixel", "LinkedIn Insight", "Google Ads",
                                                   "Microsoft Ads (UET)", "Pinterest Tag", "Snap Pixel", "Reddit Pixel",
                                                   "X (Twitter) Pixel", "Universal Analytics (retired)")]
    if not analytics:
        issues.insert(0, {"severity": "critical", "page": "site", "issue": "no_analytics",
                          "detail": "No working analytics tool fires on any audited page: there is no traffic, funnel "
                                    "or conversion data, so no baseline and no way to measure a change"})
    ids = {v: sorted(i for i in inv["ids"] if i) for v, inv in inventory.items()}
    asks = []
    for vendor, vids in sorted(ids.items(), key=lambda kv: not kv[1]):  # vendors with IDs first
        tmpl = ACCESS.get(vendor)
        if tmpl:
            for vid in (vids or [""]):
                t = tmpl
                if vendor == "Google tag (gtag.js)":  # a gtag id names its destination
                    t = ACCESS["Google Ads"] if vid.startswith("AW-") else ACCESS["GA4"] if vid.startswith("G-") else tmpl
                ask = t.format(id=vid or "(ID not visible)")
                if not vid and any(a.startswith(t.split("{id}")[0]) for a in asks):
                    continue  # the same account was already asked for by its ID
                if ask not in asks:
                    asks.append(ask)
    if not analytics:
        asks += NO_ANALYTICS_ASK
    asks += ALWAYS
    return {
        "pages": [p["url"] for p in pages],
        "inventory": [{"vendor": v, "ids": ids[v], "pages": len(inv["pages"]), "loads": inv["loads"],
                       "hits": inv["hits"], "events": dict(inv["events"])} for v, inv in sorted(inventory.items())],
        "has_analytics": bool(analytics),
        "issues": issues,
        "access_requests": asks,
    }


def capture(urls, wait_ms=6000):
    import importlib.util
    import os
    from playwright.sync_api import sync_playwright

    spec = importlib.util.spec_from_file_location("fetch_page_mod", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fetch_page.py"))
    fp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fp)
    pages = []
    with sync_playwright() as p:
        browser = launch_chromium(p)
        for url in urls:
            fp.validate_url(url)
            ctx = browser.new_context(viewport={"width": 1440, "height": 900}, user_agent=fp.DEFAULT_USER_AGENT)
            fp.guard_browser(ctx)
            page = ctx.new_page()
            reqs = []
            page.on("request", lambda r: reqs.append(r.url))
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
                try:
                    page.wait_for_load_state("networkidle", timeout=10000)
                except Exception:
                    pass
                page.mouse.wheel(0, 1500)
                page.wait_for_timeout(wait_ms)
                banner = page.evaluate("""() => [...document.querySelectorAll('div,section,aside,dialog,form')]
                    .filter(e => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e);
                      return r.width > 200 && r.height > 40 && s.visibility !== 'hidden' && s.display !== 'none' &&
                             (s.position === 'fixed' || s.position === 'sticky' || e.tagName === 'DIALOG'); })
                    .map(e => e.innerText.slice(0, 400)).join(' ')""")
                html = page.content()
            except Exception as exc:
                banner, html = "", ""
                print(f"warning: {url}: {str(exc).splitlines()[0][:120]}", file=sys.stderr)
            ids = sorted(set(re.findall(r"\b(G-[A-Z0-9]{6,12}|GTM-[A-Z0-9]{4,9}|AW-\d{6,12}|UA-\d{4,10}-\d{1,3})\b", html))
                         | {f"Meta pixel {m}" for m in re.findall(r"fbq\(\s*['\"]init['\"]\s*,\s*['\"](\d{6,20})", html)})
            pages.append({"url": url, "requests": reqs, "consent_banner": bool(CONSENT_TEXT.search(banner or "")),
                          "html_ids": ids, "request_count": len(reqs)})
            ctx.close()
        browser.close()
    return pages


def to_markdown(r, pages):
    L = ["# Tracking inventory", "",
         f"Pages loaded: {len(pages)} ({sum(p['request_count'] for p in pages)} network requests recorded, before any consent click).", ""]
    if r["inventory"]:
        L += ["| Tool | IDs | Pages | Tag loads | Hits | Events |", "|---|---|---|---|---|---|"]
        for i in r["inventory"]:
            L.append(f"| {i['vendor']} | {', '.join(i['ids']) or '-'} | {i['pages']} | {i['loads']} | {i['hits']} | "
                     f"{', '.join(f'{k} x{v}' for k, v in i['events'].items()) or '-'} |")
    else:
        L.append("**No tracker or analytics request was seen on any page.**")
    ids_in_html = sorted({i for p in pages for i in p.get("html_ids", [])})
    if ids_in_html:
        L += ["", f"IDs written in the page code: {', '.join(ids_in_html)}"]
    L += ["", "## Issues", ""]
    L += [f"- **{x['severity']}** {x['detail']} (Evidence: {x['page']})" for x in r["issues"]] or ["- none found"]
    L += ["", "## Access to ask the client for", ""] + [f"- {a}" for a in r["access_requests"]]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("urls", nargs="+")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--md")
    a = ap.parse_args()
    pages = capture(a.urls)
    r = analyze(pages)
    r["html_ids"] = sorted({i for p in pages for i in p.get("html_ids", [])})
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(r, f, indent=2)
    md = to_markdown(r, pages)
    if a.md:
        with open(a.md, "w", encoding="utf-8") as f:
            f.write(md)
    print(json.dumps(r, indent=2) if a.json else md)


if __name__ == "__main__":
    main()
