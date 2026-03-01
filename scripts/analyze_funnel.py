#!/usr/bin/env python3
"""
analyze_funnel.py — Multi-page conversion funnel analyzer.

Fetches each page in a funnel sequence, extracts CRO elements, analyzes
transitions between steps, and identifies friction points, navigation leaks,
and consistency issues.

Usage:
    python analyze_funnel.py <url1> <url2> [url3...] [--json] [--timeout 30]

Examples:
    python analyze_funnel.py https://example.com https://example.com/pricing https://example.com/signup
    python analyze_funnel.py https://shop.com/product https://shop.com/cart https://shop.com/checkout --json
"""

import argparse
import ipaddress
import json
import os
import re
import socket
import sys
import time
from urllib.parse import urljoin, urlparse

try:
    import requests
except ImportError:
    print("Error: 'requests' library is required. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: 'beautifulsoup4' is required. Install with: pip install beautifulsoup4", file=sys.stderr)
    sys.exit(1)


DEFAULT_TIMEOUT = 30
DEFAULT_USER_AGENT = "ClaudeCRO/1.0"

# Private/reserved IP networks blocked for SSRF prevention
BLOCKED_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("224.0.0.0/4"),
    ipaddress.ip_network("240.0.0.0/4"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]

# CTA-like text patterns
CTA_PATTERNS = [
    r"sign\s*up", r"get\s*started", r"start\s*(free|now|today|my|your)",
    r"buy\s*now", r"add\s*to\s*cart", r"shop\s*now", r"order\s*now",
    r"book\s*(a|now|demo|call|today)", r"request\s*(a|demo|quote)",
    r"download", r"subscribe", r"join", r"try\s*(free|now|it|today)",
    r"learn\s*more", r"see\s*(how|demo|pricing)", r"claim",
    r"register", r"contact", r"schedule", r"free\s*trial",
    r"continue", r"proceed", r"checkout", r"submit",
    r"next\s*step", r"complete", r"place\s*order", r"confirm",
]


def is_private_ip(ip_str: str) -> bool:
    """Check if an IP address falls within a blocked range."""
    try:
        addr = ipaddress.ip_address(ip_str)
        for network in BLOCKED_NETWORKS:
            if addr in network:
                return True
        return False
    except ValueError:
        return True


def check_ssrf(hostname: str):
    """Resolve hostname and block private IPs."""
    try:
        results = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError(f"DNS resolution failed for '{hostname}': {exc}")

    for _family, _type, _proto, _canonname, sockaddr in results:
        ip = sockaddr[0]
        if is_private_ip(ip):
            raise ValueError(f"SSRF protection: '{hostname}' resolves to private IP {ip}. Blocked.")


def fetch_page(url: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    """Fetch a single page and return HTML + metadata."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)
    if not parsed.hostname:
        raise ValueError(f"Invalid URL: {url}")

    check_ssrf(parsed.hostname)

    start = time.time()
    try:
        resp = requests.get(
            url,
            timeout=timeout,
            headers={
                "User-Agent": DEFAULT_USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,*/*",
            },
            allow_redirects=True,
        )
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Failed to fetch '{url}': {exc}")

    elapsed = round((time.time() - start) * 1000, 1)

    return {
        "url": url,
        "final_url": resp.url,
        "status_code": resp.status_code,
        "html": resp.text,
        "response_time_ms": elapsed,
    }


def extract_page_data(html: str, base_url: str) -> dict:
    """Extract CRO-relevant data from a single page for funnel analysis."""
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")

    # Title
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    # H1
    h1_tag = soup.find("h1")
    h1 = h1_tag.get_text(strip=True) if h1_tag else ""

    # CTAs
    ctas = []
    seen = set()

    for btn in soup.find_all(["button", "input"]):
        if btn.name == "input" and btn.get("type") not in ("submit", "button"):
            continue
        text = btn.get_text(strip=True) or btn.get("value", "").strip()
        if text and text.lower() not in seen:
            seen.add(text.lower())
            ctas.append({
                "text": text,
                "tag": btn.name,
                "href": btn.get("formaction", ""),
            })

    for link in soup.find_all("a"):
        text = link.get_text(strip=True)
        href = link.get("href", "")
        if not text:
            continue
        classes = " ".join(link.get("class", []))
        is_btn = bool(re.search(r"btn|button|cta", classes, re.IGNORECASE))
        is_cta = any(re.search(p, text, re.IGNORECASE) for p in CTA_PATTERNS)

        if (is_btn or is_cta) and text.lower() not in seen:
            seen.add(text.lower())
            if href and not href.startswith(("#", "javascript:", "mailto:", "tel:")):
                href = urljoin(base_url, href)
            ctas.append({"text": text, "tag": "a", "href": href})

    # Forms
    forms = []
    for form in soup.find_all("form"):
        fields = []
        for field in form.find_all(["input", "select", "textarea"]):
            ftype = field.get("type", "text") if field.name == "input" else field.name
            if ftype in ("hidden", "submit", "button"):
                continue
            fields.append({
                "name": field.get("name", ""),
                "type": ftype,
                "required": field.has_attr("required"),
            })
        forms.append({
            "action": form.get("action", ""),
            "method": (form.get("method") or "get").upper(),
            "field_count": len(fields),
            "fields": fields,
        })

    # All navigation links (for leak detection)
    all_links = []
    parsed_base = urlparse(base_url)
    base_domain = parsed_base.netloc.lower().replace("www.", "")

    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        if href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue
        full_url = urljoin(base_url, href)
        link_domain = urlparse(full_url).netloc.lower().replace("www.", "")
        text = link.get_text(strip=True)

        all_links.append({
            "text": text[:80] if text else "",
            "href": full_url,
            "is_external": link_domain != base_domain and bool(link_domain),
        })

    # Trust signals (simplified)
    body_text = soup.get_text(separator=" ", strip=True).lower()
    trust_signals = []
    trust_patterns = [
        r"money[\s-]*back", r"guarantee", r"secure", r"ssl",
        r"trusted", r"verified", r"certified", r"\d+[\d,]*\+?\s*customers?",
        r"free\s*shipping", r"free\s*returns?", r"satisfaction",
    ]
    for pattern in trust_patterns:
        if re.search(pattern, body_text, re.IGNORECASE):
            trust_signals.append(pattern.replace(r"\s*", " ").replace(r"\s+", " "))

    # Navigation elements count
    nav_elements = soup.find_all("nav")
    header = soup.find("header")
    footer = soup.find("footer")

    nav_link_count = 0
    for nav in nav_elements:
        nav_link_count += len(nav.find_all("a"))
    if header:
        nav_link_count += len(header.find_all("a"))

    footer_link_count = len(footer.find_all("a")) if footer else 0

    return {
        "title": title,
        "h1": h1,
        "ctas": ctas,
        "forms": forms,
        "total_links": len(all_links),
        "external_links": sum(1 for l in all_links if l["is_external"]),
        "nav_link_count": nav_link_count,
        "footer_link_count": footer_link_count,
        "trust_signals": trust_signals,
        "all_links": all_links,
    }


def check_transition(current_page: dict, next_page: dict, next_url: str) -> dict:
    """
    Analyze the transition from current page to next page.

    Checks if there is a clear CTA linking to the next page, and evaluates
    the quality of the transition.
    """
    transition = {
        "has_link_to_next": False,
        "linking_ctas": [],
        "linking_elements": [],
        "risk_factors": [],
        "risk_level": "unknown",
    }

    next_parsed = urlparse(next_url)
    next_path = next_parsed.path.rstrip("/")

    # Check CTAs for links to next page
    for cta in current_page["ctas"]:
        href = cta.get("href", "")
        if not href:
            continue
        href_parsed = urlparse(href)
        href_path = href_parsed.path.rstrip("/")

        if href_path == next_path or href == next_url:
            transition["has_link_to_next"] = True
            transition["linking_ctas"].append(cta["text"])

    # Check all links for any connection to next page
    for link in current_page["all_links"]:
        href = link.get("href", "")
        if not href:
            continue
        href_parsed = urlparse(href)
        href_path = href_parsed.path.rstrip("/")

        if href_path == next_path or href == next_url:
            transition["has_link_to_next"] = True
            if link["text"] and link["text"] not in transition["linking_elements"]:
                transition["linking_elements"].append(link["text"])

    # Risk factors
    if not transition["has_link_to_next"]:
        transition["risk_factors"].append("No direct link from this page to the next step")

    if current_page["nav_link_count"] > 10:
        transition["risk_factors"].append(
            f"Heavy navigation ({current_page['nav_link_count']} nav links) may distract from funnel progression"
        )

    if current_page["external_links"] > 3:
        transition["risk_factors"].append(
            f"{current_page['external_links']} external links creating exit opportunities"
        )

    if current_page["footer_link_count"] > 15:
        transition["risk_factors"].append(
            f"Dense footer ({current_page['footer_link_count']} links) on conversion page"
        )

    for form in current_page["forms"]:
        if form["field_count"] > 6:
            transition["risk_factors"].append(
                f"Form with {form['field_count']} fields — high friction"
            )

    if not current_page["trust_signals"]:
        transition["risk_factors"].append("No trust signals detected on this page")

    # Calculate risk level
    risk_count = len(transition["risk_factors"])
    if not transition["has_link_to_next"]:
        transition["risk_level"] = "critical"
    elif risk_count >= 4:
        transition["risk_level"] = "high"
    elif risk_count >= 2:
        transition["risk_level"] = "medium"
    else:
        transition["risk_level"] = "low"

    return transition


def analyze_consistency(pages_data: list) -> dict:
    """Analyze consistency across all funnel steps."""
    consistency = {
        "trust_signal_continuity": True,
        "trust_gaps": [],
        "form_field_progression": [],
        "issues": [],
    }

    # Check trust signal presence across pages
    for i, page in enumerate(pages_data, 1):
        if not page["trust_signals"]:
            consistency["trust_signal_continuity"] = False
            consistency["trust_gaps"].append(f"Step {i}: no trust signals")

    # Track form field counts
    for i, page in enumerate(pages_data, 1):
        for form in page["forms"]:
            consistency["form_field_progression"].append({
                "step": i,
                "field_count": form["field_count"],
            })

    # Check for navigation reduction in later steps
    if len(pages_data) >= 3:
        first_nav = pages_data[0]["nav_link_count"]
        last_nav = pages_data[-1]["nav_link_count"]
        if last_nav >= first_nav and first_nav > 5:
            consistency["issues"].append(
                f"Navigation not reduced toward end of funnel "
                f"(Step 1: {first_nav} nav links, Last step: {last_nav} nav links). "
                f"Late funnel stages should progressively strip navigation."
            )

    return consistency


def detect_leaks(pages_data: list, funnel_urls: list) -> list:
    """Identify navigation leaks — links that pull users out of the funnel."""
    leaks = []

    funnel_paths = set()
    for url in funnel_urls:
        funnel_paths.add(urlparse(url).path.rstrip("/"))

    for i, page in enumerate(pages_data):
        page_leaks = {
            "step": i + 1,
            "title": page["title"],
            "total_exit_links": 0,
            "leak_categories": {
                "nav_links": page["nav_link_count"],
                "footer_links": page["footer_link_count"],
                "external_links": page["external_links"],
                "non_funnel_internal": 0,
            },
        }

        # Count internal links that go outside the funnel
        for link in page["all_links"]:
            href = link.get("href", "")
            if not href or link.get("is_external"):
                continue
            link_path = urlparse(href).path.rstrip("/")
            if link_path and link_path not in funnel_paths:
                page_leaks["leak_categories"]["non_funnel_internal"] += 1

        page_leaks["total_exit_links"] = (
            page_leaks["leak_categories"]["external_links"]
            + page_leaks["leak_categories"]["non_funnel_internal"]
        )

        leaks.append(page_leaks)

    return leaks


def analyze_funnel(urls: list, timeout: int = DEFAULT_TIMEOUT) -> dict:
    """
    Full funnel analysis across multiple URLs.

    Args:
        urls: List of URLs in funnel order.
        timeout: Request timeout in seconds.

    Returns:
        Complete funnel analysis dict.
    """
    if len(urls) < 2:
        raise ValueError("Funnel analysis requires at least 2 URLs")

    # Fetch all pages
    steps = []
    for i, url in enumerate(urls, 1):
        try:
            page_result = fetch_page(url, timeout)
            page_data = extract_page_data(page_result["html"], page_result["final_url"])
            page_data["url"] = page_result["final_url"]
            page_data["status_code"] = page_result["status_code"]
            page_data["response_time_ms"] = page_result["response_time_ms"]
            steps.append(page_data)
        except Exception as exc:
            steps.append({
                "url": url,
                "error": str(exc),
                "title": f"Step {i} (failed to fetch)",
                "h1": "",
                "ctas": [],
                "forms": [],
                "total_links": 0,
                "external_links": 0,
                "nav_link_count": 0,
                "footer_link_count": 0,
                "trust_signals": [],
                "all_links": [],
                "status_code": None,
                "response_time_ms": None,
            })

    # Analyze transitions
    transitions = []
    for i in range(len(steps) - 1):
        if "error" in steps[i] or "error" in steps[i + 1]:
            transitions.append({
                "from_step": i + 1,
                "to_step": i + 2,
                "error": "One or both pages failed to load",
                "risk_level": "critical",
            })
        else:
            trans = check_transition(steps[i], steps[i + 1], urls[i + 1])
            trans["from_step"] = i + 1
            trans["to_step"] = i + 2
            transitions.append(trans)

    # Consistency analysis
    valid_steps = [s for s in steps if "error" not in s]
    consistency = analyze_consistency(valid_steps) if valid_steps else {}

    # Leak detection
    leaks = detect_leaks(steps, urls)

    # Overall friction score
    total_form_fields = sum(
        sum(f["field_count"] for f in s.get("forms", []))
        for s in steps
    )
    critical_transitions = sum(1 for t in transitions if t.get("risk_level") == "critical")
    high_risk_transitions = sum(1 for t in transitions if t.get("risk_level") == "high")

    # Calculate overall risk
    if critical_transitions > 0:
        overall_risk = "critical"
    elif high_risk_transitions >= len(transitions) / 2:
        overall_risk = "high"
    elif high_risk_transitions > 0:
        overall_risk = "medium"
    else:
        overall_risk = "low"

    # Funnel map
    funnel_map = []
    for i, step in enumerate(steps):
        step_info = {
            "step": i + 1,
            "url": step.get("url", urls[i]),
            "title": step.get("title", ""),
            "h1": step.get("h1", ""),
            "cta_count": len(step.get("ctas", [])),
            "form_count": len(step.get("forms", [])),
            "total_form_fields": sum(f["field_count"] for f in step.get("forms", [])),
            "nav_links": step.get("nav_link_count", 0),
            "exit_links": step.get("external_links", 0),
            "trust_signals": step.get("trust_signals", []),
            "response_time_ms": step.get("response_time_ms"),
        }
        if "error" in step:
            step_info["error"] = step["error"]
        funnel_map.append(step_info)

    # Friction points summary
    friction_points = []
    for trans in transitions:
        if trans.get("risk_level") in ("high", "critical"):
            friction_points.append({
                "location": f"Step {trans['from_step']} -> Step {trans['to_step']}",
                "risk_level": trans["risk_level"],
                "factors": trans.get("risk_factors", [trans.get("error", "Unknown")]),
            })

    return {
        "funnel_steps": len(urls),
        "overall_risk": overall_risk,
        "funnel_map": funnel_map,
        "transitions": transitions,
        "consistency": consistency,
        "leaks": leaks,
        "friction_points": friction_points,
        "total_form_fields": total_form_fields,
        "summary": {
            "critical_transitions": critical_transitions,
            "high_risk_transitions": high_risk_transitions,
            "total_exit_links": sum(l["total_exit_links"] for l in leaks),
            "pages_without_trust": sum(1 for s in steps if not s.get("trust_signals")),
        },
    }


def print_report(result: dict):
    """Print a human-readable funnel analysis report."""
    print("=" * 70)
    print("FUNNEL ANALYSIS REPORT")
    print("=" * 70)
    print(f"\nSteps: {result['funnel_steps']}")
    print(f"Overall Risk: {result['overall_risk'].upper()}")
    print(f"Total Form Fields Across Funnel: {result['total_form_fields']}")

    print(f"\n{'─' * 70}")
    print("FUNNEL MAP")
    print(f"{'─' * 70}")

    for step in result["funnel_map"]:
        print(f"\n  Step {step['step']}: {step['title'] or step['h1'] or '(no title)'}")
        print(f"    URL: {step['url']}")
        if step.get("error"):
            print(f"    ERROR: {step['error']}")
            continue
        print(f"    CTAs: {step['cta_count']} | Forms: {step['form_count']} "
              f"({step['total_form_fields']} fields) | Nav links: {step['nav_links']}")
        print(f"    Exit links: {step['exit_links']} | "
              f"Response: {step['response_time_ms']}ms")
        if step["trust_signals"]:
            print(f"    Trust: {', '.join(step['trust_signals'][:5])}")

    print(f"\n{'─' * 70}")
    print("TRANSITIONS")
    print(f"{'─' * 70}")

    for trans in result["transitions"]:
        label = f"Step {trans['from_step']} -> Step {trans['to_step']}"
        risk = trans.get("risk_level", "unknown").upper()
        print(f"\n  {label} [{risk}]")
        if trans.get("error"):
            print(f"    Error: {trans['error']}")
            continue
        linked = "Yes" if trans.get("has_link_to_next") else "NO — BROKEN LINK"
        print(f"    Direct link to next step: {linked}")
        if trans.get("linking_ctas"):
            print(f"    Linking CTAs: {', '.join(trans['linking_ctas'])}")
        if trans.get("risk_factors"):
            for factor in trans["risk_factors"]:
                print(f"    ! {factor}")

    if result["friction_points"]:
        print(f"\n{'─' * 70}")
        print("FRICTION POINTS")
        print(f"{'─' * 70}")
        for fp in result["friction_points"]:
            print(f"\n  {fp['location']} [{fp['risk_level'].upper()}]")
            for factor in fp["factors"]:
                print(f"    - {factor}")

    print(f"\n{'─' * 70}")
    print("LEAK REPORT")
    print(f"{'─' * 70}")

    for leak in result["leaks"]:
        print(f"\n  Step {leak['step']}: {leak['title']}")
        print(f"    Total exit links: {leak['total_exit_links']}")
        cats = leak["leak_categories"]
        print(f"    Nav: {cats['nav_links']} | Footer: {cats['footer_links']} | "
              f"External: {cats['external_links']} | Non-funnel internal: {cats['non_funnel_internal']}")

    print(f"\n{'─' * 70}")
    print("SUMMARY")
    print(f"{'─' * 70}")
    summary = result["summary"]
    print(f"  Critical transitions: {summary['critical_transitions']}")
    print(f"  High-risk transitions: {summary['high_risk_transitions']}")
    print(f"  Total exit link opportunities: {summary['total_exit_links']}")
    print(f"  Pages without trust signals: {summary['pages_without_trust']}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Analyze a multi-page conversion funnel for friction, leaks, and consistency.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://example.com https://example.com/pricing https://example.com/signup
  %(prog)s https://shop.com/product https://shop.com/cart https://shop.com/checkout --json
        """,
    )
    parser.add_argument("urls", nargs="+", help="URLs of funnel steps in order (minimum 2)")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")
    parser.add_argument("--timeout", "-t", type=int, default=DEFAULT_TIMEOUT, help=f"Per-page timeout in seconds (default: {DEFAULT_TIMEOUT})")

    args = parser.parse_args()

    if len(args.urls) < 2:
        print("Error: At least 2 URLs are required for funnel analysis.", file=sys.stderr)
        sys.exit(1)

    try:
        result = analyze_funnel(args.urls, timeout=args.timeout)
    except (ValueError, RuntimeError) as exc:
        if args.json_output:
            print(json.dumps({"error": str(exc)}, indent=2))
        else:
            print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.json_output:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
