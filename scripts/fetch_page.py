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
import json
import socket
import sys
import time
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("Error: 'requests' library is required. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)


DEFAULT_USER_AGENT = "ClaudeCRO/1.0"
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
        raise ValueError(f"DNS resolution failed for '{hostname}': {exc}")

    if not results:
        raise ValueError(f"No DNS results for '{hostname}'")

    # Check all resolved addresses — block if any resolve to private IPs
    resolved_ips = set()
    for family, _type, _proto, _canonname, sockaddr in results:
        ip = sockaddr[0]
        resolved_ips.add(ip)
        if is_private_ip(ip):
            raise ValueError(
                f"SSRF protection: '{hostname}' resolves to private IP {ip}. "
                f"Requests to internal/private networks are blocked."
            )

    # Return the first resolved IP for informational purposes
    return list(resolved_ips)[0]


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
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    start_time = time.time()

    session = requests.Session()
    session.max_redirects = MAX_REDIRECTS

    try:
        response = session.get(
            url,
            headers=headers,
            timeout=timeout,
            allow_redirects=True,
        )
    except requests.exceptions.TooManyRedirects:
        raise RuntimeError(f"Too many redirects (max {MAX_REDIRECTS}) when fetching '{url}'")
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(f"Connection error fetching '{url}': {exc}")
    except requests.exceptions.Timeout:
        raise RuntimeError(f"Timeout ({timeout}s) fetching '{url}'")
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Request error fetching '{url}': {exc}")

    elapsed_ms = round((time.time() - start_time) * 1000, 1)

    # Check the final URL after redirects for SSRF as well
    final_parsed = urlparse(response.url)
    if final_parsed.hostname and final_parsed.hostname != hostname:
        try:
            resolve_and_check(final_parsed.hostname)
        except ValueError as exc:
            raise RuntimeError(
                f"SSRF protection triggered after redirect. "
                f"Final URL '{response.url}' resolves to a blocked address: {exc}"
            )

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

    args = parser.parse_args()

    try:
        result = fetch_page(
            url=args.url,
            timeout=args.timeout,
            user_agent=args.user_agent,
        )
    except (ValueError, RuntimeError) as exc:
        if args.json_output:
            print(json.dumps({"error": str(exc)}, indent=2))
        else:
            print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

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


if __name__ == "__main__":
    main()
