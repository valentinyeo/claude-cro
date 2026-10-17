Status: complete

# Tracking & Analytics Analysis

**Tracking Score: 28/100 - No meaningful conversion tracking**

## Summary
The site has only Cloudflare Web Analytics (page views, no events) and an Endless Testing A/B SDK that is not configured. The main conversion, a click on "Get your free 20 minute teardown" to cal.com, is not measured anywhere. Per readiness.txt the site is NOT_TESTABLE (about 8 conversions a month, about 400 visitors), so tracking should support before/after reads and qualitative research, not A/B tests.

## Detected Platforms
| Platform | Status | ID | Notes |
|---|---|---|---|
| GA4 | Missing | - | No gtag.js or G- ID on any page |
| GTM | Missing | - | No container or dataLayer |
| Cloudflare Web Analytics | Installed, 3/3 pages | no token seen | Page views only, no custom events |
| Endless Testing | Installed, home and contact | - | SDK loaded without testId |
| Meta, Google Ads, LinkedIn pixels | Missing | - | Fine for now if there is no paid traffic |
| Hotjar / Clarity | Missing | - | No session recording |
| CMP | Missing | - | No banner |

## Findings
1. **No conversion event on the primary CTA (Critical).** Both cal.com links ("Free teardown" nav and "Get your free 20 minute teardown") are plain `target=_blank` anchors with no event, and there is no analytics that could record one. Cloudflare cannot count outbound clicks, and the booking itself happens off-site.
   Evidence: pages/home/page.html lines 1057, 1075, 1247; pages/home/elements.json tracking.scripts_found = [], data_layer = false; tracking.json inventory events = {}.
2. **No product analytics, so no funnel, source or CTA-level data (Critical).** Only Cloudflare page-view beacons are present.
   Evidence: pages/home/page.html line 1273, pages/case-study/page.html line 461, pages/contact/page.html line 475; TRACKING.md inventory table.
3. **Endless Testing SDK is half-configured (High).** The SDK loads on home and contact, but `testId` comes only from the URL, and the SDK logs "Missing ?testId=<uuid>" for normal visitors. It is not on case-study. TRACKING.md reports 0 tag loads and 2 hits. It adds a third-party request for no measured benefit, and an A/B tool is not viable at this traffic level.
   Evidence: pages/home/page.html lines 925-946; pages/contact/page.html lines 279-300; pages/case-study/page.html (no ab-sdk); TRACKING.md Issues; readiness.txt verdict NOT_TESTABLE.
4. **Booking and email are not attributed (High).** The contact page has no cal.com link, only `mailto:`, and the case-study page has no CTA at all (elements.json ctas = []). Email clicks and contact visits are untracked and cannot be tied to a source. This also makes the contact page a dead end for the main conversion.
   Evidence: pages/contact/page.html line 419; pages/contact/elements.json ctas = [] and forms = []; pages/case-study/elements.json ctas = [].
5. **No data layer or page metadata for segmenting (Medium).** There are no page-type or content-group fields, and no UTM or referrer capture beyond what Cloudflare reports.
   Evidence: pages/*/elements.json tracking.data_layer = false.
6. **No session recording (Medium).** Readiness.txt recommends qualitative research for this volume, and no recording tool is installed.
   Evidence: pages/*/page.html (no clarity/hotjar references); readiness.txt.
7. **Consent and privacy (Low risk currently).** There is no banner and no Consent Mode. Cloudflare Web Analytics is cookieless, and nothing fires from ad or analytics cookies, so the risk is low today. TRACKING.md shows the 35 requests were recorded before any consent click. Adding GA4, Clarity or Meta later would require a CMP with default-denied consent for UK/EU visitors. The Endless Testing third-party call, and its data use, should be covered by the privacy page. A privacy.html link exists in the home footer.
   Evidence: pages/home/page.html line 1266; pages/home/elements.json consent_management = false; TRACKING.md.

## Conversion Events Assessment
| Event | Expected | Detected | Quality |
|---|---|---|---|
| Page view | Yes | Yes (Cloudflare) | Aggregate only |
| CTA click (cal.com) | Yes | No | Not instrumented |
| Booking completed | Yes | No | Happens on cal.com; needs a cal.com webhook or integration |
| Email click | Yes | No | Not instrumented |
| Form submit | N/A | N/A | No forms on any page |
| Scroll / outbound | Optional | No | - |

**Missing critical events:** cta_click (location label), book_teardown (cal.com booking), email_click, case-study view.

## Data Layer
- Initialized: No
- Structure: none
- Issues: no dataLayer on any page.

## Consent
- Banner: Missing. Consent Mode v2: Missing. Default state: not configured.
- Scripts before consent: only cookieless Cloudflare analytics and the Endless Testing SDK.
- CMP: none. GDPR risk: Low now, rising to Medium once any cookie-based tool is added.

## Heatmap / Recording
Installed: none. Recommendation: free Microsoft Clarity, added after a consent decision.

## Checklist
| Item | Status | Priority |
|---|---|---|
| GA4 | Missing | Critical |
| GTM | Missing (optional at this size) | Medium |
| Conversion events | Missing | Critical |
| Consent management | Missing (not yet needed) | Medium |
| Data layer | Missing | Medium |
| Heatmap tool | Missing | Medium |
| Cross-domain (to cal.com) | Missing | Medium |
| Enhanced e-commerce | N/A | - |

## Priority Recommendations
**Critical**
- Install GA4 directly, or use Plausible if you prefer cookieless. Fire `cta_click` with a location parameter on all cal.com links and mark it as a key event.
- Connect cal.com bookings to the analytics, using the cal.com GA4/Plausible app, or a booking-success redirect or webhook. That gives the true conversion count, which also replaces the assumed 8 a month.

**High**
- Remove the Endless Testing SDK, or finish setting it up with a real test. With about 400 visitors a month it cannot reach a result.
- Add a cal.com CTA to the contact and case-study pages, tracked with a distinct label.

**Medium**
- Track `mailto:` clicks. Add UTM tags on all external links to the site.
- Add Clarity for recordings, with a minimal consent notice.

**Low**
- Add a page_type value to events.

## Access needed
- Cloudflare Web Analytics viewer seat or API token.
- Cal.com booking export for the last 3 months.
- Google Search Console access.
- Confirmed 3-month lead count (readiness.txt inputs are ASSUMED, not confirmed).
