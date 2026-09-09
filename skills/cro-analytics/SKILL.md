---
name: cro-analytics
description: >
  Analytics connection and data access setup. Detects which analytics platforms
  are installed on a website, provides step-by-step connection guides for each
  (PostHog MCP, GA4, Mixpanel, Amplitude, Matomo, Plausible), verifies
  connections, and saves a status report. Use when user says "connect analytics",
  "analytics setup", "conversion data", "PostHog setup", "GA4 connect", or
  "Mixpanel setup".
argument-hint: "<url>"
allowed-tools: Read, Grep, Glob, Bash, WebFetch
---

# CRO Analytics -- Analytics Connection & Data Access

Detect installed analytics tools on a website, guide users through connecting
their analytics data to Claude (via MCP servers or API keys), and pull real
conversion data to inform A/B test prioritization.

---

## Process

1. **Fetch the page** using `${CLAUDE_SKILL_DIR}/../cro/scripts/fetch_page.py`.
2. **Parse tracking setup** using `${CLAUDE_SKILL_DIR}/../cro/scripts/parse_cro.py`.
   The parser already extracts GA4, GTM, PostHog, Meta Pixel, and other tracking
   snippets from the HTML.
3. **Identify all analytics platforms** installed on the site. Check for each
   platform's detection signatures (see Platform Detection below).
4. **For each detected platform**, present the full connection guide from the
   Platform Connection Reference section below.
5. **If the user confirms a connection**, verify it works by pulling a sample
   metric (e.g., page views for the analyzed URL).
6. **Save the analytics connection report** to `reports/{domain}-analytics.md`.
7. **Show what data is now available** for A/B test planning and which other
   CRO skills can leverage the connected data.

---

## Platform Detection

Scan the page HTML source for these signatures:

| Platform | Detection Signatures |
|----------|---------------------|
| **Google Analytics 4** | `gtag('config', 'G-'`, `googletagmanager.com/gtag`, `measurement_id`, `G-XXXXXXXXXX` pattern |
| **Google Tag Manager** | `googletagmanager.com/gtm.js`, `GTM-XXXXXXX` pattern, `dataLayer` |
| **PostHog** | `posthog-js`, `app.posthog.com`, `ph.autocapture`, `posthog.init` |
| **Mixpanel** | `mixpanel.init`, `cdn.mxpnl.com`, `mixpanel-js` |
| **Amplitude** | `amplitude.init`, `cdn.amplitude.com`, `amplitude-js` |
| **Matomo** | `matomo.js`, `piwik.js`, `_paq.push`, `matomo.php` |
| **Plausible** | `plausible.io/js`, `data-domain=` with plausible script |
| **Segment** | `analytics.js`, `cdn.segment.com`, `analytics.identify` |
| **Heap** | `heap-XXXXX`, `cdn.heapanalytics.com`, `heap.load` |
| **Hotjar** | `hotjar.com`, `hj('identify'`, `_hjSettings` |
| **Microsoft Clarity** | `clarity.ms/tag`, `clarity("set"` |
| **Meta Pixel** | `fbq('init'`, `connect.facebook.net/en_US/fbevents.js` |

---

## Platform Connection Reference

### PostHog (MCP Server Available)

**Connection method:** MCP Server (native integration with Claude)

**Setup steps:**
1. Get your PostHog project API key from Settings > Project > API Key
2. Get your personal API key from Settings > User > Personal API Keys
3. Add the PostHog MCP server to your Claude configuration:

   **For `.mcp.json` (Claude Code):**
   ```json
   {
     "mcpServers": {
       "posthog": {
         "command": "npx",
         "args": ["-y", "@anthropic-ai/posthog-mcp"],
         "env": {
           "POSTHOG_API_KEY": "<your-personal-api-key>",
           "POSTHOG_PROJECT_ID": "<your-project-id>",
           "POSTHOG_HOST": "https://app.posthog.com"
         }
       }
     }
   }
   ```

   **For `claude_desktop_config.json` (Claude Desktop):**
   ```json
   {
     "mcpServers": {
       "posthog": {
         "command": "npx",
         "args": ["-y", "@anthropic-ai/posthog-mcp"],
         "env": {
           "POSTHOG_API_KEY": "<your-personal-api-key>",
           "POSTHOG_PROJECT_ID": "<your-project-id>",
           "POSTHOG_HOST": "https://app.posthog.com"
         }
       }
     }
   }
   ```

4. Restart Claude to load the MCP server.

**Verification query:** Once connected, run a sample query to confirm:
- List recent events for the analyzed URL
- Pull page view counts for the last 7 days
- Check if custom conversion events are configured

**Available data once connected:**
- Page views and unique visitors by URL
- Custom event tracking (button clicks, form submissions, etc.)
- Funnel analysis with step-by-step conversion rates
- Session recordings metadata
- Feature flag status
- Cohort analysis
- Retention metrics

**Limitations:**
- Personal API key required (not project API key alone)
- Rate limits apply to API queries
- Historical data depends on PostHog plan retention period

---

### Google Analytics 4 (GA4)

**Connection method:** Two paths available

#### Path A: BigQuery Export + BigQuery MCP (Recommended for power users)

**Setup steps:**
1. Enable BigQuery Linking in GA4: Admin > BigQuery Links > Link
2. Choose daily or streaming export
3. Wait for data to populate (daily export takes 24h for first batch)
4. Set up a Google Cloud service account with BigQuery read permissions
5. Download the service account JSON key file
6. Install and configure a BigQuery MCP server:
   ```json
   {
     "mcpServers": {
       "bigquery": {
         "command": "npx",
         "args": ["-y", "@anthropic-ai/bigquery-mcp"],
         "env": {
           "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/service-account.json",
           "BIGQUERY_PROJECT_ID": "<your-gcp-project>"
         }
       }
     }
   }
   ```

**Available data:** Raw event-level data, full SQL query flexibility, custom
dimensions and metrics, e-commerce transaction data.

#### Path B: GA4 Data API (Simpler setup)

**Setup steps:**
1. Create a Google Cloud project (or use existing)
2. Enable the Google Analytics Data API
3. Create a service account and grant it Viewer access on your GA4 property
4. Download the service account JSON key file
5. Use the GA4 property ID and service account to query via `WebFetch`:
   ```bash
   # Example: Get page views for last 7 days
   curl -H "Authorization: Bearer $(gcloud auth print-access-token)" \
     "https://analyticsdata.googleapis.com/v1beta/properties/{PROPERTY_ID}:runReport" \
     -d '{
       "dateRanges": [{"startDate": "7daysAgo", "endDate": "today"}],
       "metrics": [{"name": "screenPageViews"}],
       "dimensions": [{"name": "pagePath"}]
     }'
   ```

**Available data:** Aggregated reports (not raw events), standard GA4 metrics and
dimensions, no SQL -- uses the GA4 reporting API format.

**Limitations:**
- Requires Google Cloud project and service account
- Data API has quotas (10,000 requests/day for free)
- No real-time data via API (use GA4 UI for that)
- BigQuery export adds cost based on data volume

---

### Mixpanel

**Connection method:** API key + WebFetch

**Setup steps:**
1. Get your Mixpanel project token from Project Settings
2. Get a Service Account (Settings > Service Accounts > Create)
3. Note your project ID from the URL when viewing your project

**Query pattern:**
```bash
# Export events for a date range
curl "https://data.mixpanel.com/api/2.0/export" \
  -H "Authorization: Basic $(echo -n 'SERVICE_ACCOUNT_SECRET:' | base64)" \
  -d "from_date=2024-01-01" \
  -d "to_date=2024-01-07"

# Query insights (JQL)
curl "https://mixpanel.com/api/2.0/insights" \
  -H "Authorization: Basic $(echo -n 'SERVICE_ACCOUNT_SECRET:' | base64)" \
  -d '{"project_id": YOUR_PROJECT_ID}'
```

**Available data:** Event streams, funnel analysis, retention cohorts, user
profiles, custom properties.

**Limitations:**
- Service account required for API access
- Export API rate limited
- JQL queries have complexity limits

---

### Amplitude

**Connection method:** API credentials + WebFetch

**Setup steps:**
1. Get your API Key and Secret Key from Settings > Projects > [Project] > General
2. Amplitude uses HTTP Basic Auth with API key as username and secret as password

**Query pattern:**
```bash
# Dashboard REST API - get results
curl -u "API_KEY:SECRET_KEY" \
  "https://amplitude.com/api/2/events/segmentation?e=%7B%22event_type%22%3A%22pageview%22%7D&start=20240101&end=20240107"

# Export API - raw events
curl -u "API_KEY:SECRET_KEY" \
  "https://amplitude.com/api/2/export?start=20240101T00&end=20240107T00"
```

**Available data:** Event analytics, user segmentation, funnel analysis, retention,
revenue metrics, behavioral cohorts.

**Limitations:**
- Export API limited to 4 concurrent requests
- Data export has row limits per request
- Some features require Growth/Enterprise plans

---

### Matomo

**Connection method:** Self-hosted API + token auth

**Setup steps:**
1. Get your Matomo URL (self-hosted instance address)
2. Get an auth token: Settings > Personal > Security > Auth Tokens
3. Note your site ID (visible in the URL when viewing a site)

**Query pattern:**
```bash
# Get page views for last 7 days
curl "{MATOMO_URL}/?module=API&method=VisitsSummary.get&idSite={SITE_ID}&period=day&date=last7&format=JSON&token_auth={TOKEN}"

# Get page URLs report
curl "{MATOMO_URL}/?module=API&method=Actions.getPageUrls&idSite={SITE_ID}&period=week&date=today&format=JSON&token_auth={TOKEN}"
```

**Available data:** All standard web analytics metrics, goal conversions, e-commerce
data, visitor logs, custom dimensions, heatmap data (if plugin installed).

**Limitations:**
- Self-hosted: depends on your server's capacity and data retention settings
- Cloud: API rate limits apply
- Some reports require specific plugins

---

### Plausible

**Connection method:** API key + Stats API

**Setup steps:**
1. Get your API key from Settings > [Site] > Visibility > Stats API
2. Your site ID is the domain you registered (e.g., `example.com`)

**Query pattern:**
```bash
# Aggregate stats for last 7 days
curl "https://plausible.io/api/v1/stats/aggregate?site_id={DOMAIN}&period=7d&metrics=visitors,pageviews,bounce_rate,visit_duration" \
  -H "Authorization: Bearer {API_KEY}"

# Breakdown by page
curl "https://plausible.io/api/v1/stats/breakdown?site_id={DOMAIN}&period=7d&property=event:page&metrics=visitors,pageviews" \
  -H "Authorization: Bearer {API_KEY}"
```

**Available data:** Visitors, page views, bounce rate, visit duration, referral
sources, UTM breakdowns, goal conversions, custom events.

**Limitations:**
- Stats API is read-only
- Self-hosted: depends on your configuration
- Cloud: rate limited (600 requests/hour)
- No raw event export -- aggregated data only

---

## Output Format

Save this as `reports/{domain}-analytics.md`:

```markdown
# Analytics Connection: {domain}
**Generated:** {date}
**Page analyzed:** {url}

## Detected Analytics Tools

| Tool | Detected | Connection Method | Status |
|------|----------|------------------|--------|
| Google Analytics 4 | Yes/No | BigQuery MCP / Data API | Connected / Not connected / N/A |
| Google Tag Manager | Yes/No | N/A (tag manager) | Detected / N/A |
| PostHog | Yes/No | MCP Server | Connected / Not connected / N/A |
| Mixpanel | Yes/No | API (WebFetch) | Connected / Not connected / N/A |
| Amplitude | Yes/No | Export API | Connected / Not connected / N/A |
| Matomo | Yes/No | Reporting API | Connected / Not connected / N/A |
| Plausible | Yes/No | Stats API | Connected / Not connected / N/A |
| Segment | Yes/No | N/A (CDP) | Detected / N/A |
| Heap | Yes/No | N/A | Detected / N/A |
| Hotjar | Yes/No | N/A (qualitative) | Detected / N/A |
| Microsoft Clarity | Yes/No | N/A (qualitative) | Detected / N/A |
| Meta Pixel | Yes/No | N/A (ads) | Detected / N/A |

## Connected Platform Details

### {Platform Name}
- **Connection method:** [MCP / API]
- **Verification:** [Sample query result -- e.g., "7-day page views: 12,345"]
- **Available data:** [List of queryable metrics]

## Available Data Summary

Once connected, the following data types are available for CRO analysis:

- [ ] Page views and unique visitors by URL
- [ ] Conversion rates by page/funnel step
- [ ] Drop-off points in checkout/signup flows
- [ ] Device/browser/geo breakdown
- [ ] Custom event tracking coverage
- [ ] Revenue and transaction data (if e-commerce)
- [ ] Session recordings / heatmaps (qualitative)

## Connection Instructions for Unconnected Platforms

### {Platform Name}
[Step-by-step setup instructions from the Platform Connection Reference above,
customized with any detected IDs or configuration from the page scan]

## Recommended Next Steps

1. Connect your primary analytics platform using the instructions above
2. Run `/cro voice {url}` to capture brand voice before writing test copy
3. Run `/cro test {url}` to generate data-informed A/B test hypotheses
4. Use connected analytics to measure test results and calculate sample sizes
```

---

## Cross-References

- **A/B testing:** Use the `cro-testing` sub-skill after connecting analytics. With real data, test hypotheses can be prioritized by actual traffic volume and current conversion rates, and realistic MDE can be calculated.
- **Tracking audit:** Use the `cro-tracking` sub-skill for a deeper technical audit of what events and conversions are configured. This skill focuses on *connecting* data; tracking focuses on *validating* the setup.
- **CRO plan:** Use the `cro-plan` sub-skill to build a 90-day roadmap. Analytics connection is a prerequisite for data-driven planning.
- **Full audit:** Use the `cro` orchestrator for a comprehensive audit. Analytics data enriches every category's findings.
