#!/usr/bin/env python3
"""
fetch_page.py — Standalone CLI for fetching web pages with SSRF prevention.

Fetches a URL, follows redirects, and returns the HTML content along with
metadata (status code, headers, final URL, response time). Blocks requests
to private/internal IP ranges to prevent SSRF attacks.

Usage:
    python fetch_page.py <url> [--output file] [--json] [--timeout 30] [--user-agent "..."]

Examples:
    python fetch_page.py https://example.com
    python fetch_page.py https://example.com --json
    python fetch_page.py https://example.com --output page.html --timeout 15
"""

import argparse
import ipaddress
import re
import json
import socket
import sys
import time
from urllib.parse import urljoin, urlparse
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))  # noqa: E401,E702
from netenv import dns_unavailable_but_proxied, launch_chromium  # noqa: E402,F401

try:
    import requests
except ImportError:
    print("Error: 'requests' library is required. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)


# Browser-like UA: many sites block or strip content for unknown bots
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
DEFAULT_TIMEOUT = 30
MAX_REDIRECTS = 5

# Private/reserved IP networks that must be blocked to prevent SSRF
BLOCKED_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("198.18.0.0/15"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("203.0.113.0/24"),
    ipaddress.ip_network("224.0.0.0/4"),
    ipaddress.ip_network("240.0.0.0/4"),
    # IPv6 private ranges
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
    ipaddress.ip_network("::ffff:0:0/96"),
]


def is_private_ip(ip_str: str) -> bool:
    """Check if an IP address falls within any blocked private/reserved range."""
    try:
        addr = ipaddress.ip_address(ip_str)
        if not addr.is_global or addr.is_multicast:
            return True
        for network in BLOCKED_NETWORKS:
            if addr in network:
                return True
        return False
    except ValueError:
        # If we cannot parse the IP, block it to be safe
        return True


def resolve_and_check(hostname: str) -> str:
    """
    Resolve hostname to IP and verify it is not a private/reserved address.

    Returns the resolved IP address string on success.
    Raises ValueError if the IP is private or resolution fails.
    """
    try:
        results = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror as exc:
        if hostname.lower() in ("localhost", "localhost.localdomain") or not dns_unavailable_but_proxied(exc):
            raise ValueError(f"DNS resolution failed for '{hostname}': {exc}")
        return hostname  # behind a proxy that resolves names itself (cloud sessions); literal private IPs are checked elsewhere

    if not results:
        raise ValueError(f"No DNS results for '{hostname}'")

    # Check all resolved addresses — block if any resolve to private IPs
    for family, _type, _proto, _canonname, sockaddr in results:
        ip = sockaddr[0]
        if is_private_ip(ip):
            raise ValueError(
                f"SSRF protection: '{hostname}' resolves to private IP {ip}. "
                f"Requests to internal/private networks are blocked."
            )

    return results[0][4][0]


def validate_url(url: str) -> str:
    """
    Validate and normalize the URL. Ensures scheme is http or https.

    Returns the normalized URL.
    Raises ValueError for invalid URLs.
    """
    if not url:
        raise ValueError("URL cannot be empty")

    # Add scheme if missing
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Unsupported scheme: {parsed.scheme}. Only http and https are allowed.")

    if not parsed.hostname:
        raise ValueError(f"Invalid URL: no hostname found in '{url}'")

    return url


BLOCK_TITLES = re.compile(
    r"too many requests|access denied|just a moment|attention required|verify you are human|"
    r"are you a robot|captcha|request blocked|forbidden|bot protection|pardon our interruption",
    re.I,
)


def looks_blocked(status_code: int, html: str):
    """Return a reason string when the response is a bot-block or error page, else None."""
    if status_code in (401, 403, 429, 503):
        return f"HTTP {status_code}"
    m = re.search(r"<title[^>]*>(.*?)</title>", html or "", re.I | re.S)
    if m and BLOCK_TITLES.search(m.group(1)):
        return f"block page title: {m.group(1).strip()[:80]}"
    text = re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", html or "", flags=re.S)
    if len(text.split()) < 40:
        return "almost no visible text (JavaScript-only page or block page)"
    return None


def guard_browser(context) -> None:
    """Abort any browser request (page, redirect, subresource) to a private address."""
    cache = {}

    def handler(route):
        host = urlparse(route.request.url).hostname
        if host and host not in cache:
            try:
                resolve_and_check(host)
                cache[host] = True
            except ValueError:
                cache[host] = False
        if host and not cache[host]:
            route.abort("blockedbyclient")
        else:
            route.continue_()

    context.route("**/*", handler)


def render_page(url: str, timeout: int = DEFAULT_TIMEOUT, user_agent: str = DEFAULT_USER_AGENT) -> dict:
    """Load the page in headless Chromium and return the rendered DOM (what a visitor sees)."""
    from playwright.sync_api import sync_playwright

    validate_url(url)
    resolve_and_check(urlparse(url).hostname)
    start = time.time()
    with sync_playwright() as p:
        browser = launch_chromium(p)
        try:
            ctx = browser.new_context(user_agent=user_agent, viewport={"width": 1440, "height": 900})
            guard_browser(ctx)
            page = ctx.new_page()
            resp = page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                pass
            final = page.url
            resolve_and_check(urlparse(final).hostname)
            html = page.content()
            status = resp.status if resp else 0
            headers = dict(resp.headers) if resp else {}
        finally:
            browser.close()
    return {
        "url": url,
        "final_url": final,
        "status_code": status,
        "headers": headers,
        "html": html,
        "response_time_ms": round((time.time() - start) * 1000, 1),
        "resolved_ip": None,
        "content_length": len(html.encode("utf-8")),
        "encoding": "utf-8",
    }


class PinnedAddressAdapter(requests.adapters.HTTPAdapter):
    def get_connection(self, url, proxies=None):
        if requests.utils.select_proxy(url, proxies):
            return super().get_connection(url, proxies=proxies)
        parsed = urlparse(url)
        address = str(ipaddress.ip_address(resolve_and_check(parsed.hostname)))
        pool_kwargs = {}
        if parsed.scheme == "https":
            pool_kwargs.update(assert_hostname=parsed.hostname, server_hostname=parsed.hostname)
        return self.poolmanager.connection_from_host(
            address, port=parsed.port, scheme=parsed.scheme, pool_kwargs=pool_kwargs)

    def get_connection_with_tls_context(self, request, verify, proxies=None, cert=None):
        if requests.utils.select_proxy(request.url, proxies):
            return super().get_connection_with_tls_context(request, verify, proxies=proxies, cert=cert)
        host_params, pool_kwargs = self.build_connection_pool_key_attributes(request, verify, cert)
        hostname = host_params["host"]
        host_params["host"] = str(ipaddress.ip_address(resolve_and_check(hostname)))
        if host_params["scheme"] == "https":
            pool_kwargs.update(assert_hostname=hostname, server_hostname=hostname)
        return self.poolmanager.connection_from_host(**host_params, pool_kwargs=pool_kwargs)

    def add_headers(self, request, **kwargs):
        parsed = urlparse(request.url)
        host = f"[{parsed.hostname}]" if ":" in parsed.hostname else parsed.hostname
        request.headers["Host"] = host + (f":{parsed.port}" if parsed.port is not None else "")


def fetch_page(
    url: str,
    timeout: int = DEFAULT_TIMEOUT,
    user_agent: str = DEFAULT_USER_AGENT,
) -> dict:
    """
    Fetch a web page with SSRF protection and redirect following.

    Args:
        url: The URL to fetch.
        timeout: Request timeout in seconds.
        user_agent: User-Agent header value.

    Returns:
        dict with keys: url, final_url, status_code, headers, html,
                        response_time_ms, resolved_ip, content_length
    """
    url = validate_url(url)
    parsed = urlparse(url)
    hostname = parsed.hostname

    # Resolve and check the initial hostname
    resolved_ip = resolve_and_check(hostname)

    headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }

    start_time = time.time()
    session = requests.Session()
    session.mount("http://", PinnedAddressAdapter())
    session.mount("https://", PinnedAddressAdapter())
    current = url

    # Follow redirects by hand so every hop is checked before it is requested
    for _ in range(MAX_REDIRECTS + 1):
        try:
            response = session.get(current, headers=headers, timeout=timeout, allow_redirects=False)
        except requests.exceptions.ConnectionError as exc:
            raise RuntimeError(f"Connection error fetching '{current}': {exc}")
        except requests.exceptions.Timeout:
            raise RuntimeError(f"Timeout ({timeout}s) fetching '{current}'")
        except (requests.exceptions.RequestException, ValueError) as exc:
            raise RuntimeError(f"Request error fetching '{current}': {exc}")

        if not response.is_redirect:
            break
        nxt = urljoin(current, response.headers.get("Location", ""))
        try:
            validate_url(nxt)
            resolve_and_check(urlparse(nxt).hostname)
        except ValueError as exc:
            raise RuntimeError(f"SSRF protection triggered on redirect to '{nxt}': {exc}")
        current = nxt
    else:
        raise RuntimeError(f"Too many redirects (max {MAX_REDIRECTS}) when fetching '{url}'")

    elapsed_ms = round((time.time() - start_time) * 1000, 1)

    # Build response headers dict (flatten multi-value headers)
    resp_headers = {}
    for key, value in response.headers.items():
        resp_headers[key] = value

    return {
        "url": url,
        "final_url": response.url,
        "status_code": response.status_code,
        "headers": resp_headers,
        "html": response.text,
        "response_time_ms": elapsed_ms,
        "resolved_ip": resolved_ip,
        "content_length": len(response.content),
        "encoding": response.encoding,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Fetch a web page with SSRF prevention and return content/metadata.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://example.com
  %(prog)s https://example.com --json
  %(prog)s https://example.com --output page.html --timeout 15
  %(prog)s https://example.com --user-agent "MyBot/2.0"
        """,
    )
    parser.add_argument("url", help="URL to fetch")
    parser.add_argument("--output", "-o", help="Write HTML content to this file")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output metadata as JSON")
    parser.add_argument("--timeout", "-t", type=int, default=DEFAULT_TIMEOUT, help=f"Request timeout in seconds (default: {DEFAULT_TIMEOUT})")
    parser.add_argument("--user-agent", "-u", default=DEFAULT_USER_AGENT, help=f'User-Agent string (default: "{DEFAULT_USER_AGENT}")')
    parser.add_argument("--render", action="store_true",
                        help="Load in headless Chromium and save the rendered DOM (falls back to plain HTTP if Playwright is missing)")

    args = parser.parse_args()

    result, how, note = None, "http", None
    try:
        if args.render:
            try:
                result, how = render_page(args.url, args.timeout, args.user_agent), "browser"
            except ImportError:
                note = "Playwright not installed; used plain HTTP"
            except Exception as exc:
                note = f"browser render failed ({exc}); used plain HTTP"
        if result is None:
            result = fetch_page(url=args.url, timeout=args.timeout, user_agent=args.user_agent)
            # Bot walls and JavaScript-only pages often load fine in a real browser
            if looks_blocked(result["status_code"], result["html"]) and not args.render:
                try:
                    rendered = render_page(args.url, args.timeout, args.user_agent)
                    if not looks_blocked(rendered["status_code"], rendered["html"]):
                        result, how = rendered, "browser"
                        note = "plain HTTP looked blocked; used browser render"
                except Exception:
                    pass
    except (ValueError, RuntimeError) as exc:
        if args.json_output:
            print(json.dumps({"error": str(exc)}, indent=2))
        else:
            print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    blocked = looks_blocked(result["status_code"], result["html"])
    result["fetched_with"] = how
    result["blocked"] = blocked
    if note:
        print(f"Note: {note}", file=sys.stderr)
    if blocked:
        print(f"WARNING: page looks blocked or empty ({blocked}). Do not audit this HTML as the real page; "
              "use screenshots or WebFetch and record the gap.", file=sys.stderr)

    # Write HTML to file if requested
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(result["html"])
            if not args.json_output:
                print(f"HTML saved to: {args.output}")
        except IOError as exc:
            print(f"Error writing to '{args.output}': {exc}", file=sys.stderr)
            sys.exit(1)

    if args.json_output:
        # In JSON mode, include everything except the full HTML (too large)
        output = {
            "url": result["url"],
            "final_url": result["final_url"],
            "status_code": result["status_code"],
            "headers": result["headers"],
            "response_time_ms": result["response_time_ms"],
            "resolved_ip": result["resolved_ip"],
            "content_length": result["content_length"],
            "encoding": result["encoding"],
            "fetched_with": result["fetched_with"],
            "blocked": result["blocked"],
        }
        if not args.output:
            # If no output file specified, include HTML in JSON
            output["html"] = result["html"]
        else:
            output["html_file"] = args.output
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        if not args.output:
            # Print summary and HTML to stdout
            print(f"URL: {result['url']}")
            print(f"Final URL: {result['final_url']}")
            print(f"Status: {result['status_code']}")
            print(f"Response Time: {result['response_time_ms']}ms")
            print(f"Content Length: {result['content_length']} bytes")
            print(f"Resolved IP: {result['resolved_ip']}")
            print(f"Encoding: {result['encoding']}")
            print("---")
            print(result["html"])
    if blocked:
        sys.exit(3)


if __name__ == "__main__":
    main()
