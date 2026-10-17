"""Network and browser setup that works on a laptop and in locked-down cloud sessions.

Cloud sessions (Claude Code on the web) send traffic through an HTTPS proxy, cannot resolve
DNS locally, and ship a preinstalled Chromium that may not match the pip Playwright build."""
import glob
import os
import shutil
from urllib.parse import urlsplit


def proxy_url():
    for k in ("HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy", "ALL_PROXY", "all_proxy"):
        if os.environ.get(k):
            return os.environ[k]
    return None


def browser_proxy():
    """Playwright proxy setting from the environment, or None."""
    url = proxy_url()
    if not url:
        return None
    u = urlsplit(url if "://" in url else "http://" + url)
    p = {"server": f"{u.scheme}://{u.hostname}" + (f":{u.port}" if u.port else "")}
    if u.username:
        p["username"] = u.username
        p["password"] = u.password or ""
    bypass = os.environ.get("NO_PROXY") or os.environ.get("no_proxy")
    if bypass:
        p["bypass"] = bypass
    return p


def _installed_chromes():
    roots = [os.environ.get("PLAYWRIGHT_BROWSERS_PATH", ""), os.path.expanduser("~/.cache/ms-playwright"),
             os.path.expanduser("~/Library/Caches/ms-playwright"), "/opt/pw-browsers"]
    found = []
    for r in filter(None, roots):
        for pat in ("chromium-*/chrome-linux*/chrome", "chromium-*/chrome-mac*/Chromium.app/Contents/MacOS/Chromium",
                    "chromium-*/chrome-mac*/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing",
                    "chromium-*/chrome-win*/chrome.exe", "chromium_headless_shell-*/chrome-*/headless_shell"):
            found += sorted(glob.glob(os.path.join(r, pat)), reverse=True)
    for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        if shutil.which(name):
            found.append(shutil.which(name))
    return [f for f in dict.fromkeys(found) if os.access(f, os.X_OK)]


def launch_chromium(pw, **kw):
    """pw.chromium.launch with the environment's proxy; if Playwright's own build is missing,
    fall back to any Chromium already on the machine instead of failing."""
    kw.setdefault("headless", True)
    if browser_proxy() and "proxy" not in kw:
        kw["proxy"] = browser_proxy()
    try:
        return pw.chromium.launch(**kw)
    except Exception as first:
        if "xecutable" not in str(first) and "install" not in str(first):
            raise
        for exe in _installed_chromes():
            try:
                return pw.chromium.launch(executable_path=exe, **kw)
            except Exception:
                continue
        raise


def dns_unavailable_but_proxied(exc):
    """True when a lookup failed only because this machine must reach the web through a proxy.
    The proxy resolves the name; literal private IPs are still blocked by the caller."""
    return proxy_url() is not None and isinstance(exc, OSError)
