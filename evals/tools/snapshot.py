"""Save a rendered, script-free snapshot of a live page, so eval cases never drift when the site changes.
Usage: snapshot.py <url> <out.html>"""
import re
import sys

from playwright.sync_api import sync_playwright

url, out = sys.argv[1], sys.argv[2]
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1366, "height": 900})
    pg.goto(url, wait_until="networkidle", timeout=60000)
    pg.wait_for_timeout(2000)
    html = pg.content()
    b.close()
html = re.sub(r"<script\b.*?</script>|<noscript\b.*?</noscript>|<iframe\b.*?</iframe>", "", html, flags=re.S | re.I)
html = re.sub(r"<head([^>]*)>", lambda m: f"<head{m.group(1)}><base href='{url}'>", html, count=1)
open(out, "w", encoding="utf-8").write(html)
print(out, len(html))
