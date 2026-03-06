#!/usr/bin/env python3
"""
parse_cro.py — Extract CRO-relevant elements from HTML.

Parses HTML content and extracts CTAs, forms, trust signals, tracking scripts,
headlines, meta information, images, links, schema markup, and social proof
patterns into a structured format suitable for CRO analysis.

Usage:
    python parse_cro.py <file_or_url> [--json] [--elements all|cta|forms|trust|tracking|images|copy]

Examples:
    python parse_cro.py page.html
    python parse_cro.py https://example.com --json
    python parse_cro.py page.html --elements cta,forms --json
"""

import argparse
import json
import os
import re
import sys
from urllib.parse import urljoin, urlparse

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: 'beautifulsoup4' is required. Install with: pip install beautifulsoup4", file=sys.stderr)
    sys.exit(1)


# CTA-like text patterns (case-insensitive matching)
CTA_PATTERNS = [
    r"sign\s*up", r"get\s*started", r"start\s*(free|now|today|my|your)",
    r"buy\s*now", r"add\s*to\s*cart", r"shop\s*now", r"order\s*now",
    r"book\s*(a|now|demo|call|today|free|my|your)",
    r"request\s*(a|demo|quote|info|pricing)",
    r"download\s*(free|now|today)?", r"subscribe", r"join\s*(now|free|today|us)?",
    r"try\s*(free|now|it|today)", r"learn\s*more", r"see\s*(how|demo|pricing|plans)",
    r"claim\s*(your|my|now|free)", r"register\s*(now|free|today)?",
    r"contact\s*(us|sales|support)?", r"schedule\s*(a|demo|call|meeting)",
    r"free\s*trial", r"apply\s*now", r"enroll\s*now",
    r"get\s*(my|your|a|free|instant)", r"submit",
    r"create\s*(account|my)", r"log\s*in", r"sign\s*in",
    r"continue", r"proceed", r"checkout", r"donate",
]

# Tracking script identifiers
TRACKING_PATTERNS = {
    "Google Analytics 4 (GA4)": [r"gtag\(", r"google-analytics\.com", r"googletagmanager\.com/gtag"],
    "Google Tag Manager (GTM)": [r"googletagmanager\.com/gtm\.js", r"GTM-[A-Z0-9]+"],
    "Facebook/Meta Pixel": [r"connect\.facebook\.net", r"fbq\(", r"facebook\.com/tr"],
    "LinkedIn Insight Tag": [r"snap\.licdn\.com", r"linkedin\.com/px"],
    "Twitter/X Pixel": [r"static\.ads-twitter\.com", r"twq\("],
    "TikTok Pixel": [r"analytics\.tiktok\.com", r"ttq\."],
    "Pinterest Tag": [r"pintrk\(", r"s\.pinimg\.com/ct/core\.js"],
    "Hotjar": [r"hotjar\.com", r"hj\(", r"_hjSettings"],
    "Microsoft Clarity": [r"clarity\.ms"],
    "Segment": [r"cdn\.segment\.com", r"analytics\.js"],
    "Mixpanel": [r"mixpanel\.com", r"mixpanel\.init"],
    "Amplitude": [r"amplitude\.com", r"amplitude\.getInstance"],
    "Heap": [r"heap-\d+\.js", r"heap\.load"],
    "Plausible": [r"plausible\.io"],
    "Matomo/Piwik": [r"matomo\.js", r"piwik\.js"],
    "Google Ads": [r"googleads\.g\.doubleclick\.net", r"google_conversion"],
    "Snap Pixel": [r"sc-static\.net/scevent\.min\.js", r"snaptr\("],
    "HubSpot": [r"js\.hs-scripts\.com", r"hs-analytics"],
    "Intercom": [r"widget\.intercom\.io", r"Intercom\("],
    "Drift": [r"js\.driftt\.com", r"drift\.load"],
}

# Trust signal patterns
TRUST_KEYWORDS = [
    "testimonial", "review", "rating", "trusted", "certified", "guarantee",
    "money-back", "refund", "secure", "ssl", "verified", "award",
    "client", "partner", "customer", "case study", "success story",
    "as seen in", "featured in", "press", "media", "accredited",
    "bbb", "iso", "soc", "gdpr", "hipaa", "pci", "compliant",
]

SOCIAL_PROOF_PATTERNS = [
    r"\d[\d,]*\+?\s*(customers?|users?|clients?|companies|businesses|teams?|people)",
    r"trusted\s+by\s+\d",
    r"(used|loved|chosen)\s+by\s+\d",
    r"\d[\d.]*\s*\/\s*5\s*(stars?|rating)?",
    r"★+|⭐+",
    r"\d[\d,]*\+?\s*(reviews?|ratings?|testimonials?)",
    r"\d[\d,]*\+?\s*(downloads?|installs?|subscribers?)",
    r"(4|5)\.\d\s*(out\s+of\s+5|stars?|\/5)",
]


def load_html(source: str) -> tuple:
    """
    Load HTML from a file path or URL.

    Returns (html_string, base_url).
    """
    # Check if source is a URL
    parsed = urlparse(source)
    if parsed.scheme in ("http", "https"):
        try:
            # Import fetch_page logic inline to avoid circular dependency
            script_dir = os.path.dirname(os.path.abspath(__file__))
            fetch_script = os.path.join(script_dir, "fetch_page.py")

            if os.path.exists(fetch_script):
                import importlib.util
                spec = importlib.util.spec_from_file_location("fetch_page", fetch_script)
                fetch_mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(fetch_mod)
                result = fetch_mod.fetch_page(source)
                return result["html"], result["final_url"]

            # Fallback: use requests directly
            import requests
            resp = requests.get(source, timeout=30, headers={"User-Agent": "ClaudeCRO/1.0"})
            return resp.text, resp.url
        except Exception as exc:
            print(f"Error fetching URL '{source}': {exc}", file=sys.stderr)
            sys.exit(1)

    # It's a file path
    if not os.path.exists(source):
        print(f"Error: File not found: '{source}'", file=sys.stderr)
        sys.exit(1)

    try:
        with open(source, "r", encoding="utf-8", errors="replace") as f:
            html = f.read()
        return html, f"file://{os.path.abspath(source)}"
    except IOError as exc:
        print(f"Error reading file '{source}': {exc}", file=sys.stderr)
        sys.exit(1)


def is_cta_text(text: str) -> bool:
    """Check if text matches common CTA patterns."""
    text_clean = text.strip().lower()
    if not text_clean or len(text_clean) > 100:
        return False
    for pattern in CTA_PATTERNS:
        if re.search(pattern, text_clean, re.IGNORECASE):
            return True
    return False


def extract_ctas(soup: BeautifulSoup, base_url: str) -> list:
    """Extract all CTAs: buttons and CTA-like links."""
    ctas = []
    seen_texts = set()

    # All buttons
    for btn in soup.find_all(["button", "input"]):
        if btn.name == "input" and btn.get("type") not in ("submit", "button"):
            continue
        text = btn.get_text(strip=True) or btn.get("value", "").strip()
        if not text:
            continue
        key = text.lower()
        if key in seen_texts:
            continue
        seen_texts.add(key)
        ctas.append({
            "text": text,
            "tag": btn.name,
            "type": btn.get("type", "button"),
            "href": btn.get("formaction", ""),
            "classes": " ".join(btn.get("class", [])),
            "is_cta_pattern": is_cta_text(text),
        })

    # Links with CTA-like text or button-like classes
    for link in soup.find_all("a"):
        text = link.get_text(strip=True)
        if not text:
            continue
        classes = " ".join(link.get("class", []))
        has_btn_class = bool(re.search(r"btn|button|cta", classes, re.IGNORECASE))
        has_cta_text = is_cta_text(text)

        if has_btn_class or has_cta_text:
            key = text.lower()
            if key in seen_texts:
                continue
            seen_texts.add(key)
            href = link.get("href", "")
            if href and not href.startswith(("#", "javascript:", "mailto:", "tel:")):
                href = urljoin(base_url, href)
            ctas.append({
                "text": text,
                "tag": "a",
                "type": "link",
                "href": href,
                "classes": classes,
                "is_cta_pattern": has_cta_text,
            })

    return ctas


def extract_forms(soup: BeautifulSoup, base_url: str) -> list:
    """Extract all forms with their fields and attributes."""
    forms = []
    for form in soup.find_all("form"):
        action = form.get("action", "")
        if action and not action.startswith(("#", "javascript:")):
            action = urljoin(base_url, action)

        fields = []
        for field in form.find_all(["input", "select", "textarea"]):
            field_type = field.get("type", "text") if field.name == "input" else field.name
            if field_type in ("hidden", "submit", "button"):
                continue
            fields.append({
                "name": field.get("name", ""),
                "type": field_type,
                "required": field.has_attr("required"),
                "placeholder": field.get("placeholder", ""),
                "label": _find_label(soup, field),
            })

        forms.append({
            "action": action,
            "method": (form.get("method") or "get").upper(),
            "id": form.get("id", ""),
            "classes": " ".join(form.get("class", [])),
            "field_count": len(fields),
            "fields": fields,
            "has_validation": bool(form.find(attrs={"pattern": True}) or form.find(attrs={"required": True})),
        })

    return forms


def _find_label(soup: BeautifulSoup, field) -> str:
    """Find the label text for a form field."""
    field_id = field.get("id")
    if field_id:
        label = soup.find("label", attrs={"for": field_id})
        if label:
            return label.get_text(strip=True)

    # Check if field is inside a label
    parent_label = field.find_parent("label")
    if parent_label:
        return parent_label.get_text(strip=True)

    # Check for aria-label
    aria = field.get("aria-label")
    if aria:
        return aria

    return ""


def extract_trust_signals(soup: BeautifulSoup) -> dict:
    """Extract trust signals: testimonials, reviews, badges, logos, guarantees."""
    signals = {
        "testimonials": [],
        "review_widgets": [],
        "client_logos": [],
        "security_badges": [],
        "guarantees": [],
        "certifications": [],
    }

    body_text = soup.get_text(separator=" ", strip=True).lower()

    # Testimonials — look for blockquotes, elements with testimonial classes/IDs
    for el in soup.find_all(["blockquote", "figure"]):
        text = el.get_text(strip=True)
        if text and len(text) > 20:
            signals["testimonials"].append({"text": text[:200], "tag": el.name})

    # Elements with testimonial-related classes
    for el in soup.find_all(attrs={"class": re.compile(r"testimonial|review|quote|feedback", re.I)}):
        text = el.get_text(strip=True)
        if text and len(text) > 20:
            signals["testimonials"].append({"text": text[:200], "tag": el.name})

    # Review widgets (third-party)
    review_platforms = ["trustpilot", "google-reviews", "yelp", "g2", "capterra", "glassdoor", "tripadvisor"]
    for platform in review_platforms:
        if platform in body_text or soup.find(attrs={"class": re.compile(platform, re.I)}):
            signals["review_widgets"].append(platform)

    # Client/partner logos — images in logo sections
    logo_sections = soup.find_all(attrs={"class": re.compile(r"logo|client|partner|brand|trusted", re.I)})
    for section in logo_sections:
        for img in section.find_all("img"):
            signals["client_logos"].append({
                "alt": img.get("alt", ""),
                "src": img.get("src", ""),
            })

    # Security badges
    badge_patterns = ["ssl", "secure", "mcafee", "norton", "verisign", "comodo",
                      "digicert", "pci", "stripe", "paypal", "visa", "mastercard"]
    for img in soup.find_all("img"):
        alt = (img.get("alt") or "").lower()
        src = (img.get("src") or "").lower()
        for pattern in badge_patterns:
            if pattern in alt or pattern in src:
                signals["security_badges"].append({
                    "alt": img.get("alt", ""),
                    "src": img.get("src", ""),
                })
                break

    # Guarantees
    guarantee_patterns = [
        r"money[\s-]*back\s*guarantee",
        r"\d+[\s-]*day\s*(free\s*)?trial",
        r"satisfaction\s*guarantee",
        r"risk[\s-]*free",
        r"no\s*questions?\s*asked",
        r"cancel\s*an?y\s*time",
        r"free\s*returns?",
        r"\d+[\s-]*day\s*return",
        r"100%\s*(satisfaction|money[\s-]*back)",
    ]
    for pattern in guarantee_patterns:
        matches = re.findall(pattern, body_text, re.IGNORECASE)
        if matches:
            signals["guarantees"].extend(matches)

    # Deduplicate
    signals["guarantees"] = list(set(signals["guarantees"]))

    return signals


def extract_tracking(soup: BeautifulSoup) -> dict:
    """Extract analytics and tracking scripts."""
    tracking = {
        "scripts_found": [],
        "data_layer": False,
        "consent_management": False,
    }

    # Combine all script content
    all_scripts = ""
    for script in soup.find_all("script"):
        src = script.get("src", "")
        content = script.string or ""
        combined = f"{src} {content}"
        all_scripts += combined + "\n"

    # Check for each tracking platform
    for platform, patterns in TRACKING_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, all_scripts, re.IGNORECASE):
                if platform not in tracking["scripts_found"]:
                    tracking["scripts_found"].append(platform)
                break

    # Data layer
    if re.search(r"dataLayer\s*=|dataLayer\.push", all_scripts):
        tracking["data_layer"] = True

    # Consent management
    consent_patterns = [
        r"cookiebot", r"onetrust", r"cookieconsent", r"gdpr", r"cookie-consent",
        r"cookie-notice", r"cookie-banner", r"trustarc", r"quantcast", r"usercentrics",
        r"iubenda", r"complianz", r"termly",
    ]
    for pattern in consent_patterns:
        if re.search(pattern, all_scripts, re.IGNORECASE):
            tracking["consent_management"] = True
            break

    # Also check for noscript tracking (e.g., Meta Pixel noscript fallback)
    for noscript in soup.find_all("noscript"):
        content = str(noscript)
        if re.search(r"facebook\.com/tr|doubleclick\.net", content, re.IGNORECASE):
            if "Facebook/Meta Pixel (noscript)" not in tracking["scripts_found"]:
                tracking["scripts_found"].append("Facebook/Meta Pixel (noscript fallback)")

    return tracking


def extract_headlines(soup: BeautifulSoup) -> dict:
    """Extract all heading elements (H1-H3)."""
    headlines = {"h1": [], "h2": [], "h3": []}
    for level in ("h1", "h2", "h3"):
        for heading in soup.find_all(level):
            text = heading.get_text(strip=True)
            if text:
                headlines[level].append(text)
    return headlines


def extract_meta(soup: BeautifulSoup) -> dict:
    """Extract meta information: title, description, OG tags."""
    meta = {
        "title": "",
        "description": "",
        "og_tags": {},
        "twitter_tags": {},
        "canonical": "",
        "robots": "",
        "viewport": "",
    }

    title_tag = soup.find("title")
    if title_tag:
        meta["title"] = title_tag.get_text(strip=True)

    # Meta description
    desc_tag = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
    if desc_tag:
        meta["description"] = desc_tag.get("content", "")

    # Open Graph tags
    for og in soup.find_all("meta", attrs={"property": re.compile(r"^og:", re.I)}):
        key = og.get("property", "")
        meta["og_tags"][key] = og.get("content", "")

    # Twitter/X cards
    for tw in soup.find_all("meta", attrs={"name": re.compile(r"^twitter:", re.I)}):
        key = tw.get("name", "")
        meta["twitter_tags"][key] = tw.get("content", "")

    # Canonical
    canonical_tag = soup.find("link", attrs={"rel": "canonical"})
    if canonical_tag:
        meta["canonical"] = canonical_tag.get("href", "")

    # Robots
    robots_tag = soup.find("meta", attrs={"name": re.compile(r"^robots$", re.I)})
    if robots_tag:
        meta["robots"] = robots_tag.get("content", "")

    # Viewport
    viewport_tag = soup.find("meta", attrs={"name": re.compile(r"^viewport$", re.I)})
    if viewport_tag:
        meta["viewport"] = viewport_tag.get("content", "")

    return meta


def extract_images(soup: BeautifulSoup, base_url: str) -> list:
    """Extract all images with alt text, src, and dimension attributes."""
    images = []
    for img in soup.find_all("img"):
        src = img.get("src", "") or img.get("data-src", "")
        if src and not src.startswith("data:"):
            src = urljoin(base_url, src)

        images.append({
            "src": src,
            "alt": img.get("alt", ""),
            "width": img.get("width", ""),
            "height": img.get("height", ""),
            "loading": img.get("loading", ""),
            "has_alt": bool(img.get("alt")),
            "has_dimensions": bool(img.get("width") and img.get("height")),
        })

    return images


def extract_links(soup: BeautifulSoup, base_url: str) -> dict:
    """Count internal vs external links."""
    parsed_base = urlparse(base_url)
    base_domain = parsed_base.netloc.lower().replace("www.", "")

    internal = 0
    external = 0
    internal_urls = []
    external_urls = []

    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        if href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue

        full_url = urljoin(base_url, href)
        parsed_link = urlparse(full_url)
        link_domain = parsed_link.netloc.lower().replace("www.", "")

        if link_domain == base_domain or not link_domain:
            internal += 1
            if full_url not in internal_urls:
                internal_urls.append(full_url)
        else:
            external += 1
            if full_url not in external_urls:
                external_urls.append(full_url)

    return {
        "internal_count": internal,
        "external_count": external,
        "total": internal + external,
        "internal_urls_unique": len(internal_urls),
        "external_urls_unique": len(external_urls),
    }


def extract_schema(soup: BeautifulSoup) -> list:
    """Extract JSON-LD structured data."""
    schemas = []
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        content = script.string
        if content:
            try:
                data = json.loads(content)
                schemas.append(data)
            except json.JSONDecodeError:
                schemas.append({"error": "Invalid JSON-LD", "raw": content[:200]})
    return schemas


def extract_social_proof(soup: BeautifulSoup) -> list:
    """Find social proof patterns in page text."""
    body_text = soup.get_text(separator=" ", strip=True)
    found = []

    for pattern in SOCIAL_PROOF_PATTERNS:
        matches = re.findall(pattern, body_text, re.IGNORECASE)
        for match in matches:
            if match and match not in found:
                found.append(match)

    return found


def parse_cro(html: str, base_url: str, elements: str = "all") -> dict:
    """
    Parse HTML and extract CRO elements.

    Args:
        html: Raw HTML string.
        base_url: Base URL for resolving relative links.
        elements: Comma-separated list of element types to extract.
                  Options: all, cta, forms, trust, tracking, images, copy

    Returns:
        dict with extracted elements.
    """
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")

    element_set = set(e.strip().lower() for e in elements.split(","))
    extract_all = "all" in element_set

    result = {}

    if extract_all or "cta" in element_set:
        result["ctas"] = extract_ctas(soup, base_url)

    if extract_all or "forms" in element_set:
        result["forms"] = extract_forms(soup, base_url)

    if extract_all or "trust" in element_set:
        result["trust_signals"] = extract_trust_signals(soup)

    if extract_all or "tracking" in element_set:
        result["tracking"] = extract_tracking(soup)

    if extract_all or "copy" in element_set:
        result["headlines"] = extract_headlines(soup)
        result["meta"] = extract_meta(soup)

    if extract_all or "images" in element_set:
        result["images"] = extract_images(soup, base_url)

    # Always extract these for full context
    if extract_all:
        result["links"] = extract_links(soup, base_url)
        result["schema"] = extract_schema(soup)
        result["social_proof_patterns"] = extract_social_proof(soup)

    return result


def print_summary(data: dict):
    """Print a human-readable summary of extracted CRO elements."""

    if "ctas" in data:
        print("\n=== CTAs ===")
        if data["ctas"]:
            for i, cta in enumerate(data["ctas"], 1):
                pattern_flag = " [CTA PATTERN]" if cta.get("is_cta_pattern") else ""
                print(f"  {i}. [{cta['tag'].upper()}] \"{cta['text']}\"{pattern_flag}")
                if cta.get("href"):
                    print(f"     -> {cta['href']}")
        else:
            print("  (none found)")

    if "forms" in data:
        print("\n=== Forms ===")
        if data["forms"]:
            for i, form in enumerate(data["forms"], 1):
                print(f"  {i}. {form['method']} {form['action'] or '(no action)'} — {form['field_count']} fields")
                for field in form["fields"]:
                    req = " *" if field["required"] else ""
                    label = f" ({field['label']})" if field["label"] else ""
                    print(f"     - {field['name'] or '(unnamed)'}: {field['type']}{req}{label}")
        else:
            print("  (none found)")

    if "trust_signals" in data:
        ts = data["trust_signals"]
        print("\n=== Trust Signals ===")
        print(f"  Testimonials: {len(ts['testimonials'])}")
        print(f"  Review widgets: {', '.join(ts['review_widgets']) or 'none'}")
        print(f"  Client logos: {len(ts['client_logos'])}")
        print(f"  Security badges: {len(ts['security_badges'])}")
        print(f"  Guarantees: {', '.join(ts['guarantees']) or 'none'}")

    if "tracking" in data:
        print("\n=== Tracking ===")
        if data["tracking"]["scripts_found"]:
            for script in data["tracking"]["scripts_found"]:
                print(f"  - {script}")
        else:
            print("  (no tracking scripts detected)")
        print(f"  Data Layer: {'Yes' if data['tracking']['data_layer'] else 'No'}")
        print(f"  Consent Management: {'Yes' if data['tracking']['consent_management'] else 'No'}")

    if "headlines" in data:
        print("\n=== Headlines ===")
        for level in ("h1", "h2", "h3"):
            heads = data["headlines"][level]
            if heads:
                for h in heads:
                    print(f"  <{level}> {h}")

    if "meta" in data:
        meta = data["meta"]
        print("\n=== Meta ===")
        print(f"  Title: {meta['title']}")
        print(f"  Description: {meta['description'][:150]}{'...' if len(meta['description']) > 150 else ''}")
        if meta["og_tags"]:
            print(f"  OG Tags: {len(meta['og_tags'])} found")
        print(f"  Viewport: {'set' if meta['viewport'] else 'MISSING'}")

    if "images" in data:
        imgs = data["images"]
        print(f"\n=== Images ({len(imgs)} total) ===")
        missing_alt = sum(1 for img in imgs if not img["has_alt"])
        missing_dims = sum(1 for img in imgs if not img["has_dimensions"])
        lazy = sum(1 for img in imgs if img["loading"] == "lazy")
        print(f"  Missing alt text: {missing_alt}")
        print(f"  Missing dimensions: {missing_dims}")
        print(f"  Lazy loaded: {lazy}")

    if "links" in data:
        links = data["links"]
        print(f"\n=== Links ===")
        print(f"  Internal: {links['internal_count']} ({links['internal_urls_unique']} unique)")
        print(f"  External: {links['external_count']} ({links['external_urls_unique']} unique)")

    if "schema" in data:
        print(f"\n=== Structured Data (JSON-LD) ===")
        if data["schema"]:
            for schema in data["schema"]:
                if isinstance(schema, dict):
                    stype = schema.get("@type", schema.get("error", "unknown"))
                    print(f"  - {stype}")
        else:
            print("  (none found)")

    if "social_proof_patterns" in data:
        print(f"\n=== Social Proof Patterns ===")
        if data["social_proof_patterns"]:
            for pattern in data["social_proof_patterns"]:
                print(f"  - {pattern}")
        else:
            print("  (none found)")


def main():
    parser = argparse.ArgumentParser(
        description="Extract CRO-relevant elements from HTML for conversion analysis.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s page.html
  %(prog)s https://example.com --json
  %(prog)s page.html --elements cta,forms --json
        """,
    )
    parser.add_argument("source", help="HTML file path or URL to analyze")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")
    parser.add_argument(
        "--elements", "-e",
        default="all",
        help="Comma-separated element types to extract: all, cta, forms, trust, tracking, images, copy (default: all)",
    )

    args = parser.parse_args()

    html, base_url = load_html(args.source)
    data = parse_cro(html, base_url, args.elements)

    if args.json_output:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"CRO Element Extraction: {args.source}")
        print("=" * 60)
        print_summary(data)


if __name__ == "__main__":
    main()
