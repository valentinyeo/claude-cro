# Troubleshooting

Solutions to common issues with Claude CRO.

---

## Skills Not Appearing

**Symptom:** Typing `/cro` in Claude Code does nothing or is not recognized.

**Solutions:**

1. **Verify files are installed correctly:**
   ```bash
   ls ~/.claude/skills/cro/SKILL.md
   ```
   If this file does not exist, run `./install.sh` again.

2. **Check sub-skills:**
   ```bash
   ls ~/.claude/skills/cro-*/SKILL.md
   ```
   You should see 12 sub-skill directories.

3. **Restart Claude Code.** Skills are loaded at startup. After running the
   installer, restart your Claude Code session.

4. **Check the skills directory location.** Claude Code may look for skills
   in a different path depending on your configuration. Verify with:
   ```bash
   cat ~/.claude/config.json | grep skills
   ```

---

## Playwright Not Working

**Symptom:** `capture_screenshot.py` fails or reports Playwright is not
installed.

**Solutions:**

1. **Install Playwright:**
   ```bash
   pip install playwright
   playwright install chromium
   ```

2. **Install system dependencies (Linux):**
   ```bash
   playwright install-deps chromium
   ```

3. **Verify headless mode.** The screenshot script always runs in headless
   mode. If you see errors about display servers or X11, confirm that the
   script uses `headless=True` (this is hardcoded and should not need
   changes).

4. **Playwright not required.** Screenshot capture is optional. All CRO
   analysis commands work without Playwright — they use HTML analysis
   instead of visual analysis.

---

## SSRF Errors

**Symptom:** `fetch_page.py` or `analyze_funnel.py` reports "SSRF protection"
and refuses to fetch a URL.

**What is SSRF?** Server-Side Request Forgery is an attack where a script is
tricked into making requests to internal/private networks. Claude CRO blocks
this by checking that the resolved IP address of any URL is not in a private
range.

**Blocked IP ranges:**
- `10.0.0.0/8` — Private network
- `172.16.0.0/12` — Private network
- `192.168.0.0/16` — Private network
- `127.0.0.0/8` — Loopback
- `169.254.0.0/16` — Link-local
- `::1` — IPv6 loopback
- `fc00::/7` — IPv6 unique local
- `fe80::/10` — IPv6 link-local

**When this is expected:**
- You are trying to fetch a URL that points to a local development server
  (e.g., `http://localhost:3000`). This is intentionally blocked.
- The domain name resolves to a private IP (e.g., an internal DNS entry).

**Workarounds:**
- For local development analysis, save the HTML to a file and use
  `parse_cro.py` directly:
  ```bash
  curl http://localhost:3000 > page.html
  python scripts/parse_cro.py page.html --json
  ```
- The SSRF check is a security feature and should not be disabled in
  production use.

---

## Slow Analysis

**Symptom:** `/cro audit` or `/cro funnel` takes a long time.

**Solutions:**

1. **Full audits use 6 parallel agents.** Each agent processes the full page
   HTML. On large pages (100KB+ HTML), this can be slow. This is expected
   behavior.

2. **Reduce scope.** If you only need to check one aspect, use a targeted
   command:
   ```
   /cro copy <url>    # Instead of /cro audit
   /cro ux <url>      # Instead of /cro audit
   ```

3. **Funnel analysis fetches multiple pages.** Each URL in the funnel is
   fetched sequentially. Reduce the number of URLs if speed is a concern.

4. **Network timeouts.** If pages are slow to respond, you can adjust the
   timeout:
   ```bash
   python scripts/fetch_page.py <url> --timeout 15
   ```

5. **Large pages.** Pages with very large DOMs (e.g., single-page apps that
   render thousands of elements) take longer to parse. The `parse_cro.py`
   script uses lxml for performance, falling back to `html.parser` if lxml
   is not available.

---

## Missing Tracking Data

**Symptom:** `/cro tracking` does not detect analytics scripts that are
actually installed.

**Causes:**

1. **Consent/cookie blocking.** Many sites load tracking scripts only after
   the user accepts cookies. When fetching with `fetch_page.py` (no browser,
   no cookie consent), these scripts are not in the HTML.

   **Solution:** Note in your report that tracking may be consent-gated. Use
   Playwright-based fetching or check the GTM container separately.

2. **Tag Manager deferred loading.** GTM loads scripts dynamically after
   page load. Static HTML analysis only sees the GTM container script, not
   the tags it fires.

   **Solution:** The tracking checker identifies GTM presence. Assume that
   if GTM is installed, additional tracking is likely configured within the
   container.

3. **Server-side tracking.** Some sites use server-side tagging (e.g.,
   GA4 via GTM server container). This is invisible in the HTML.

   **Solution:** Note that server-side tracking cannot be detected from
   HTML alone. Check for the presence of a first-party measurement domain.

4. **Script loading patterns.** Some scripts are loaded with `async` or
   `defer` attributes, or injected dynamically. The `parse_cro.py` script
   checks both `src` attributes and inline script content, but cannot
   execute JavaScript.

---

## Score Seems Wrong

**Symptom:** The CRO Health Score or a category score seems too high or too
low for the page.

**Understanding the scoring:**

1. **Scores are based on HTML analysis, not user testing.** The evaluation
   checks for the presence or absence of CRO best practices in the HTML
   structure. It cannot measure actual user behavior or conversion rates.

2. **Category weights are fixed.** The CRO Health Score uses these weights:
   - UX: 25%
   - Copy: 20%
   - Trust: 15%
   - Visual: 15%
   - Forms: 10%
   - Performance: 10%
   - Tracking: 5%

   If your page has no forms, the 10% forms weight still applies. Sub-skills
   handle this by redistributing the weight.

3. **Industry context matters.** A score of 60 for a startup MVP is
   different from 60 for an enterprise SaaS. The business type detection
   adjusts some benchmarks, but the scoring framework is generalized.

4. **Single-page apps (SPAs).** SPAs that render content via JavaScript may
   have low scores because the initial HTML is nearly empty. The HTML-based
   analysis sees very little content.

   **Solution:** For SPAs, use the screenshot-based analysis or provide a
   pre-rendered HTML file.

5. **Tracking score is low but tracking is fine.** The tracking evaluation
   scores based on the presence of scripts in the HTML. If your tracking is
   consent-gated (loaded after cookie acceptance), the score will be low
   even though tracking is properly configured.

---

## Fetch Page Errors

**Symptom:** `fetch_page.py` returns connection errors or timeouts.

**Solutions:**

1. **Check the URL.** Ensure it includes the protocol (`https://`). The
   script adds `https://` automatically if missing.

2. **Check DNS.** The URL hostname must resolve. Try:
   ```bash
   nslookup example.com
   ```

3. **Check network access.** The machine running the script must have
   outbound internet access.

4. **Rate limiting.** Some sites block automated requests. The default
   User-Agent is `ClaudeCRO/1.0`. Try a different User-Agent:
   ```bash
   python scripts/fetch_page.py <url> --user-agent "Mozilla/5.0 ..."
   ```

5. **Cloudflare/bot protection.** Sites behind Cloudflare's bot protection
   or similar WAFs may block the request. This is a known limitation of
   HTML fetching. Use Playwright-based fetching (via `capture_screenshot.py`)
   as a fallback, which renders JavaScript and handles more protection
   mechanisms.

6. **Redirect loops.** The fetcher follows up to 5 redirects. If the site
   has more, it will fail. This usually indicates a misconfigured site.

---

## Report Validation Fails

**Symptom:** `hooks/validate-cro-report.sh` exits with errors.

**Common causes:**

1. **Missing files.** The validator looks for `FULL-AUDIT.md` and/or
   `ACTION-PLAN.md` in the specified directory. Make sure reports are saved
   with these exact filenames.

2. **Score not found.** The validator looks for patterns like `XX/100` or
   `Score: XX`. Ensure the report includes the CRO Health Score in a
   recognizable format.

3. **Missing priority sections.** The validator checks for references to
   Critical, High, Medium, and Low priority levels. Ensure the report
   includes all four levels in its findings or recommendations sections.

4. **Report too short.** The validator requires a minimum line count
   (30 lines for FULL-AUDIT.md, 15 for ACTION-PLAN.md). A shorter report
   likely indicates an incomplete analysis.

---

## Python Dependencies

**Symptom:** Import errors when running scripts.

**Fix:**
```bash
pip install -r requirements.txt
```

Required packages: `requests`, `beautifulsoup4`, `lxml`, `playwright` (optional).

If `lxml` fails to install on your system:

```bash
# Ubuntu/Debian
sudo apt install libxml2-dev libxslt-dev python3-dev

# macOS
brew install libxml2

# Then retry
pip install lxml
```

The `parse_cro.py` script automatically falls back to Python's built-in
`html.parser` if lxml is not available.
