# CRO Audit: valentinyeo.com
**Date:** 2026-10-17 · **URL:** https://valentinyeo.com · **Business type:** services / lead generation (solo CRO consultant), main conversion: click "Get your free 20 minute teardown" and book on cal.com
**Pages audited:** home, case study (inne), contact · **Depth:** standard · **Personas:** 2
**CRO Health Score:** 64/100 — Moderate

## Bottom line
The home page does its job: one clear promise, one dark button above the fold, and a one-click path to the booking calendar. The leak is everything after it. The case study and contact pages give a convinced reader no way to book, and the site cannot tell you how many people click the button. Fix the booking path on those two pages and add a click event on the cal.com links first; both are small jobs.

## Test Readiness
**Baseline:** about 8 conversions/month, 2% CVR, about 400 visitors/month — ASSUMED (no analytics numbers were supplied; estimated for a solo consultant's site)
**Verdict:** NOT_TESTABLE (provisional)
**Smallest detectable lift:** 320% in 4 weeks, 201% in 8 weeks
**What this means:** at this volume an A/B test cannot reach a result, so changes should be shipped and compared against a before/after baseline, with usability research to choose them.
**Method:** usability research, then ship and measure. No A/B test backlog.

## Measurement and access
- **What fires today:** Cloudflare Web Analytics on all 3 pages (page views only, no events). An A/B testing SDK (Endless Testing) loads on home and contact; it reads a test ID from the URL, so no experiment runs by default. No GA4, no tag manager, no session recording. Evidence: tracking.json, TRACKING.md.
- **Gap:** the cal.com links carry no click event, so teardown clicks and bookings cannot be tied to a page or source from the site's analytics (F-11). Whether bookings are tracked inside cal.com cannot be seen from the page.
- **Access to request (turns the assumed baseline into a confirmed one):** Cloudflare Web Analytics viewer seat or API token (Account Analytics Read); Google Search Console (restricted user); cal.com booking export for the last 3 months, or the monthly count of teardown requests.

## Score
Forms dropped (no form on any page); remaining weights rescaled to total 100%.

| Category | Score | Weight | Weighted |
|----------|-------|--------|----------|
| UX | 66/100 | 27.8% | 18.3 |
| Copy | 64/100 | 22.2% | 14.2 |
| Trust | 58/100 | 16.7% | 9.7 |
| Visual | 64/100 | 16.7% | 10.7 |
| Performance | 86/100 | 11.1% | 9.6 |
| Tracking | 28/100 | 5.6% | 1.6 |
| **Total** | | **100%** | **64** |

## Top 5 issues
1. **Case studies end with no way to book** — case study (and the Eduki and trivago pages, same template) — High. Evidence: pages/case-study/page.html has 0 cal.com links; header is logo, CV, LinkedIn; the only link on is "Back to Home".
2. **Contact page has no booking path** — contact — High. Evidence: pages/contact/elements.json `forms: []`; page says "use one of the contact methods above"; email, WhatsApp, Upwork and address get equal weight.
3. **The booking click is not measured** — all pages — High. Evidence: tracking.json events `{}`; no click handler on the cal.com links in pages/home/page.html.
4. **Only one of five case-study tests reports a result** — case study — High. Evidence: pages/case-study/page.html: Test 1 has numbers but no sample size or runtime; Tests 2-5 give hypotheses only.
5. **The teardown offer is not explained where visitors decide** — home — Medium. Evidence: pages/home/page.html hero and closing CTA say only "Get your free 20 minute teardown"; the "free, no-obligation, bring your site" explanation appears only after the click on cal.com (personas/P2/step-05.png).

## What visitors experienced
**P1 — head of growth at a ~€5M ecommerce brand, desktop, from LinkedIn.** Reached the cal.com calendar in about 10 steps and would book, but hesitated on proof and price: one testimonial with no revenue number, "+14.6% from one test out of 100+" with no baseline, and no prices in Services. Worst moment: the case study and contact pages felt like a different, older site with no teardown button (personas/P1/b/step-01.png, b/step-03.png).

**P2 — busy DTC founder, mobile, from Google.** Reached the calendar in one tap from the hero and did not book. Worst moments: not knowing who inne and Eduki are or whether the service is for ecommerce brands, and "teardown" being jargon (personas/P2/step-01.png); on the booking page the timezone shows "Select..." (step-05.png).

## What already works
- One clear promise and one dominant button above the fold on desktop and mobile; the label is specific and low-risk.
- Specific, checkable proof: +14.6% purchase revenue, 5 to 120+ tests a quarter, 11 years at trivago.
- Unusually transparent contact details: UK address, phone, sole-trader line, Terms, Privacy and Refund Policy on every page.
- Very light pages (26-34 KB, 6-9 requests; lab LCP 1.0-1.7 s) on a CDN. Speed is not the problem (lab data only, no real-user data).
- The booking page itself is clear: free, no-obligation, 20 minutes, calendar visible immediately.

## Findings by page

### Home
- **F-04 (Medium)** The page never says what the teardown covers or that it is no-obligation; that is only explained after the click. Evidence: pages/home/page.html CTA; personas/P2/step-05.png. Found by: copy, trust, P1, P2.
- **F-05 (Medium)** Proof rests on one testimonial (Truely/IDA CEO, no numbers) and two of the client names (vetsak, Teeth Lovers) are plain text, not logos. Evidence: pages/home/page.html "What Clients Say" and "Selected Clients". Found by: trust, visual, P1, P2.
- **F-06 (Medium)** Nothing says which kind of business the offer is for; inne, Eduki and trivago are named but not explained. Evidence: pages/home/page.html hero (no "ecommerce", "DTC" or "online store" anywhere); personas/P2/step-01.png. Found by: copy, P1, P2.
- **F-08 (Medium)** Services list no price, range or starting point; only Hourly Consulting says who it suits. Evidence: pages/home/page.html Services; personas/P1/step-03.png. Found by: P1, P2.
- **F-09 (Low)** On mobile the header teardown button sits behind the hamburger and no button follows the reader down the page; the hero and closing CTAs are the only entry points. Evidence: pages/home/page.html `.nav-links` hidden under 640px; pages/home/mobile.png. Found by: ux, visual.
- **F-10 (Low)** The Truely & IDA card links to the Upwork profile rather than a case study; the other three cards link to on-site case studies (checked live). Evidence: pages/home/page.html case-item links.
- **F-15 (Low)** Contact email is a Gmail address and the home page has no photo of Valentin (one appears on the booking page); About goes to the CV page. Evidence: pages/home/page.html nav and footer.
- **F-17 (Low)** "See the results", Email and WhatsApp are small text links, and an empty band appeared under the header in one mobile scroll capture. Evidence: personas/P2/step-01.png, step-03.png, step-04.png.

### Case study (inne)
- **F-01 (High)** Dead end: no teardown button, header has only CV and LinkedIn, only link on is "Back to Home". The Eduki and trivago case studies use the same template and also end without a booking link. Evidence: pages/case-study/page.html (0 cal.com links). Found by: ux, copy, trust, visual, P1.
- **F-07 (High)** Of five tests described only Test 1 reports numbers, with no sample size, runtime or significance; Tests 2-5 give no outcome. Evidence: pages/case-study/page.html "Test 2" to "Test 5". Found by: copy, trust, P1.
- **F-03 (Medium)** Older white/amber template with no navigation or teardown button; the amber accent words (#F59E0B on white, 2.15:1) and purple labels (3.96:1) fall below WCAG contrast. Evidence: pages/case-study/page.html styles; desktop.png. Found by: ux, visual, P1.
- **F-19 (Low)** Long text-only page with no test screenshots. Evidence: pages/case-study/page.html (0 img tags).
- **F-16 (Low)** Footer says © 2025; home says 2026. Evidence: pages/case-study/page.html footer.

### Contact
- **F-02 (High)** Does not link to the free teardown booking; lists email, WhatsApp, Upwork and an address with equal weight, no form, no response-time promise. Evidence: pages/contact/elements.json `forms: []`; pages/contact/desktop.png. Found by: ux, copy, visual, tracking, P1.
- **F-03 (Medium)** Same older template and header as the case study. Evidence: pages/contact/page.html.
- **F-16 (Low)** Footer says © 2025.

### Booking page (cal.com) and measurement
- **F-11 (High)** No click or booking event is visible in the site code for the cal.com CTA; only Cloudflare page views are recorded. Evidence: tracking.json events `{}`.
- **F-12 (Low)** Endless Testing SDK is loaded on home and contact with no test configured by default; it is not on the case-study page. Evidence: tracking.json (loads 0, hits 2); pages/home/page.html.
- **F-18 (Low)** The cal.com page opens in a new tab and the timezone selector shows "Select..." until chosen; otherwise it explains the offer and shows the calendar immediately. Evidence: personas/P2/step-05.png; personas/P1/c/step-01.png.

## Copy rewrites
Proposed wording is a starting point to test against your own voice; the findings it answers are noted.

| Where | Current | Proposed |
|-------|---------|----------|
| Home, under hero button (F-04) | (nothing) | "20 minutes, free, no obligation. Bring your site; you leave with the first 3 things to fix." |
| Home, hero (F-06) | "I'm a CRO and A/B testing consultant. I've run over 100 tests for inne…" | "I help ecommerce and DTC teams run more A/B tests, faster. 100+ tests for inne (a Berlin hormone-tracking brand), Eduki from 5 to 120+ tests a quarter…" (use only if this is who you want to attract) |
| Case study, headline (F-01) | "inne.io CRO Case Study: Optimizing Conversion for a Femtech Pioneer" | "How one above-the-fold button lifted purchase revenue 14.6% at inne.io" |
| Case study, end (F-01) | (ends after last test; "Back to Home") | Button: "Get your free 20 minute teardown" with "See what your site should test first." |
| Contact, H1 (F-02) | "Get in Touch" | "Book your free 20 minute teardown", button first, email and WhatsApp below as "Prefer to write?" |
| Services (F-08) | no prices | add a "from" figure or a range per offer, or "Priced by traffic; the teardown call will tell you which fits." |

## Research Plan
Readiness is NOT_TESTABLE, so these replace an A/B test backlog:
1. Five moderated sessions with target buyers (ecommerce heads of growth), task: "find out if this consultant is right for you and book a call". Watch the case-study and contact detours.
2. Install free session recording (Microsoft Clarity) and watch 30-50 sessions that reached the case study or contact page.
3. Add one question to the booking confirmation or a short form: "What almost stopped you from booking?"
4. Ship the High fixes together, then compare teardown clicks and bookings for 4 weeks after against 4 weeks before. This is a directional read, not proof; note campaigns and seasonality.
5. At most one radical background test is worthwhile, and only after the click event exists.

## Gaps in this audit
- Baseline is ASSUMED (about 8 conversions/month, 400 visitors/month); the verdict is provisional until you confirm real numbers.
- No real-user speed data (PageSpeed API unavailable); speed figures are single lab runs.
- The Eduki and trivago case-study pages were checked only for existence and the missing booking link, not audited in full.
- The cal.com page was seen in the persona runs only; bookings and its internal analytics were not visible.
- Contrast ratios for #F59E0B and #a855f7 were computed from the CSS values; other contrast figures in agent notes were visual estimates.
- Visitors in the persona runs were simulated; neither booked.
