#!/usr/bin/env python3
"""
crawl_site.py — Find the pages that matter for conversion on a site.

Reads the homepage (and sitemap.xml when links are thin), classifies internal
links by page type and picks one representative URL per type, so an audit can
cover the whole buying path instead of only the homepage.

Usage:
    python crawl_site.py https://example.com
    python crawl_site.py https://example.com --json --max-per-type 2
"""

import argparse
import importlib.util
import json
import os
import re
import sys
from urllib.parse import urljoin, urlparse, urldefrag

_spec = importlib.util.spec_from_file_location(
    "fetch_page_mod", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fetch_page.py"))
fp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fp)

# Order matters: first match wins.
PAGE_TYPES = [
    ("cart", r"/cart\b|/basket\b|/bag\b"),
    ("checkout", r"/checkout\b"),
    ("product", r"/products?/[^/?#]+|/p/[^/?#]+|/item/|/dp/"),
    ("collection", r"/collections?/|/category/|/categories/|/shop/?$|/shop/[^/]+/?$|/c/"),
    ("pricing", r"/pricing|/plans\b|/price"),
    ("signup", r"/sign-?up|/register|/get-started|/start|/trial|/join"),
    ("demo", r"/demo|/book|/schedule|/consultation|/quote"),
    ("contact", r"/contact"),
    ("about", r"/about|/our-story|/team"),
    ("reviews", r"/reviews|/testimonials|case-stud|/customers|/portfolio|/work/|/success-stor"),
    ("service", r"/services?\b|/solutions?\b|/what-we-do|/consulting|/offerings?\b"),
    ("faq", r"/faq|/help|/support"),
    ("blog", r"/blog|/articles|/journal|/news"),
]
TEXT_HINTS = [
    ("cart", r"\bcart\b|\bbag\b|basket"),
    ("pricing", r"pricing|plans"),
    ("signup", r"sign ?up|get started|start free|free trial|create account"),
    ("demo", r"book a (demo|call)|get a quote|schedule"),
    ("contact", r"contact"),
]
SKIP = re.compile(r"\.(jpg|jpeg|png|gif|webp|svg|pdf|zip|mp4|css|js)$|/account|/login|/signin|/policies|/privacy|/terms|/legal|mailto:|tel:", re.I)


def classify(url: str, text: str):
    path = urlparse(url).path.lower() or "/"
    if path in ("", "/"):
        return "home"
    for t, rx in PAGE_TYPES:
        if re.search(rx, path):
            return t
    for t, rx in TEXT_HINTS:
        if re.search(rx, text or "", re.I):
            return t
    return None


def links_from(html: str, base: str):
    host = urlparse(base).hostname
    out = []
    for m in re.finditer(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html, re.I | re.S):
        href, inner = m.group(1), m.group(2)
        url = urldefrag(urljoin(base, href))[0]
        if urlparse(url).scheme not in ("http", "https") or SKIP.search(url):
            continue
        h = urlparse(url).hostname or ""
        if h.removeprefix("www.") != (host or "").removeprefix("www."):
            continue
        text = re.sub(r"<[^>]+>", " ", inner)
        out.append((url, " ".join(text.split())[:80]))
    return out


def sitemap_urls(base: str, limit: int = 400):
    try:
        r = fp.fetch_page(urljoin(base, "/sitemap.xml"), timeout=20)
    except Exception:
        return []
    locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", r["html"])
    # Sitemap index: open the first few child sitemaps
    if locs and all(l.endswith(".xml") or "sitemap" in l for l in locs[:5]):
        urls = []
        for child in locs[:4]:
            try:
                urls += re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", fp.fetch_page(child, timeout=20)["html"])
            except Exception:
                pass
        locs = urls
    return [(u, "") for u in locs[:limit]]


def crawl(url: str, max_per_type: int = 1, render: bool = True) -> dict:
    res = None
    if render:
        try:
            res = fp.render_page(url)
        except Exception:
            res = None
    if res is None:
        res = fp.fetch_page(url)
    base = res["final_url"]
    found = links_from(res["html"], base)
    source = "homepage links"
    if len({u for u, _ in found}) < 15:
        found += sitemap_urls(base)
        source = "homepage links + sitemap.xml"

    by_type = {"home": [base]}
    seen = {base}
    for u, text in found:
        if u in seen:
            continue
        seen.add(u)
        t = classify(u, text)
        if t and len(by_type.setdefault(t, [])) < max_per_type:
            by_type[t].append(u)
    by_type = {k: v for k, v in by_type.items() if v}
    return {
        "site": base,
        "source": source,
        "links_seen": len(seen),
        "pages": by_type,
        "missing": [t for t, _ in PAGE_TYPES if t not in by_type and t not in ("checkout", "blog", "faq")],
        "blocked": fp.looks_blocked(res["status_code"], res["html"]),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument("--max-per-type", type=int, default=1)
    ap.add_argument("--no-render", action="store_true", help="Plain HTTP only (faster, misses JavaScript menus)")
    ap.add_argument("--json", action="store_true", dest="json_output")
    a = ap.parse_args()
    try:
        r = crawl(a.url, a.max_per_type, render=not a.no_render)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    if a.json_output:
        print(json.dumps(r, indent=2))
        return
    print(f"Site: {r['site']}  ({r['links_seen']} links from {r['source']})")
    if r["blocked"]:
        print(f"WARNING: homepage looks blocked ({r['blocked']})")
    for t, urls in r["pages"].items():
        for u in urls:
            print(f"  {t:<11} {u}")
    if r["missing"]:
        print("Not found:", ", ".join(r["missing"]))


if __name__ == "__main__":
    main()
