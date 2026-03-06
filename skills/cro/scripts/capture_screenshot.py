#!/usr/bin/env python3
"""
capture_screenshot.py — Screenshot capture utility using Playwright.

Takes screenshots of web pages in desktop or mobile viewport for visual
hierarchy analysis and CRO evaluation. Always runs in headless mode.

Usage:
    python capture_screenshot.py <url> [--output screenshot.png] [--width 1280] [--height 800]
                                       [--mobile] [--full-page] [--wait 3]

Examples:
    python capture_screenshot.py https://example.com
    python capture_screenshot.py https://example.com --output desktop.png --full-page
    python capture_screenshot.py https://example.com --mobile --output mobile.png
    python capture_screenshot.py https://example.com --width 1440 --height 900 --wait 5
"""

import argparse
import ipaddress
import os
import socket
import sys
from urllib.parse import urlparse

# SSRF protection — same blocked networks as fetch_page.py
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

# Mobile device emulation settings
MOBILE_CONFIG = {
    "viewport": {"width": 375, "height": 812},
    "user_agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    ),
    "device_scale_factor": 3,
    "is_mobile": True,
    "has_touch": True,
}


def is_private_ip(ip_str: str) -> bool:
    """Check if an IP address is in a blocked private range."""
    try:
        addr = ipaddress.ip_address(ip_str)
        for network in BLOCKED_NETWORKS:
            if addr in network:
                return True
        return False
    except ValueError:
        return True


def check_ssrf(url: str):
    """Resolve hostname and block private/internal IPs."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Unsupported scheme: {parsed.scheme}")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError(f"No hostname in URL: {url}")

    try:
        results = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError(f"DNS resolution failed for '{hostname}': {exc}")

    for _family, _type, _proto, _canonname, sockaddr in results:
        ip = sockaddr[0]
        if is_private_ip(ip):
            raise ValueError(
                f"SSRF protection: '{hostname}' resolves to private IP {ip}. Blocked."
            )


def capture_screenshot(
    url: str,
    output: str = "screenshot.png",
    width: int = 1280,
    height: int = 800,
    mobile: bool = False,
    full_page: bool = False,
    wait: int = 3,
) -> str:
    """
    Capture a screenshot of a web page using Playwright.

    Args:
        url: URL to screenshot.
        output: Output file path.
        width: Viewport width (ignored in mobile mode).
        height: Viewport height (ignored in mobile mode).
        mobile: Use mobile viewport and user agent.
        full_page: Capture full scrollable page.
        wait: Seconds to wait after page load for JS rendering.

    Returns:
        Absolute path to the saved screenshot.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "Error: Playwright is not installed.\n"
            "Install with:\n"
            "  pip install playwright\n"
            "  playwright install chromium",
            file=sys.stderr,
        )
        sys.exit(1)

    # Add scheme if missing
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # SSRF check
    check_ssrf(url)

    # Ensure output directory exists
    output_dir = os.path.dirname(os.path.abspath(output))
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
        except Exception as exc:
            print(
                f"Error launching browser: {exc}\n"
                "Make sure Playwright browsers are installed:\n"
                "  playwright install chromium",
                file=sys.stderr,
            )
            sys.exit(1)

        if mobile:
            context = browser.new_context(
                viewport=MOBILE_CONFIG["viewport"],
                user_agent=MOBILE_CONFIG["user_agent"],
                device_scale_factor=MOBILE_CONFIG["device_scale_factor"],
                is_mobile=MOBILE_CONFIG["is_mobile"],
                has_touch=MOBILE_CONFIG["has_touch"],
            )
        else:
            context = browser.new_context(
                viewport={"width": width, "height": height},
                user_agent="ClaudeCRO/1.0 (Screenshot)",
            )

        page = context.new_page()

        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
        except Exception:
            # Fallback: try with just domcontentloaded if networkidle times out
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
            except Exception as exc:
                browser.close()
                raise RuntimeError(f"Failed to load page '{url}': {exc}")

        # Wait for JS rendering
        if wait > 0:
            page.wait_for_timeout(wait * 1000)

        # Take screenshot
        page.screenshot(path=output, full_page=full_page)

        browser.close()

    abs_path = os.path.abspath(output)
    return abs_path


def main():
    parser = argparse.ArgumentParser(
        description="Capture web page screenshots using Playwright (always headless).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://example.com
  %(prog)s https://example.com --output desktop.png --full-page
  %(prog)s https://example.com --mobile --output mobile.png
  %(prog)s https://example.com --width 1440 --height 900 --wait 5
        """,
    )
    parser.add_argument("url", help="URL to screenshot")
    parser.add_argument("--output", "-o", default="screenshot.png", help="Output file path (default: screenshot.png)")
    parser.add_argument("--width", "-W", type=int, default=1280, help="Viewport width in pixels (default: 1280)")
    parser.add_argument("--height", "-H", type=int, default=800, help="Viewport height in pixels (default: 800)")
    parser.add_argument("--mobile", "-m", action="store_true", help="Use mobile viewport (375x812) and user agent")
    parser.add_argument("--full-page", "-f", action="store_true", help="Capture full scrollable page")
    parser.add_argument("--wait", "-w", type=int, default=3, help="Seconds to wait for JS rendering (default: 3)")

    args = parser.parse_args()

    try:
        output_path = capture_screenshot(
            url=args.url,
            output=args.output,
            width=args.width,
            height=args.height,
            mobile=args.mobile,
            full_page=args.full_page,
            wait=args.wait,
        )
        print(f"Screenshot saved: {output_path}")

        viewport = "375x812 (mobile)" if args.mobile else f"{args.width}x{args.height}"
        mode = "full page" if args.full_page else "viewport only"
        print(f"Viewport: {viewport}, Mode: {mode}, Wait: {args.wait}s")

    except (ValueError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
