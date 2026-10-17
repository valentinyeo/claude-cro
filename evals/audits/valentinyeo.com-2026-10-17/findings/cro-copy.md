Status: complete

# Copy Analysis: valentinyeo.com

**Copy Score: 64/100 (Moderate, strong home hero, weak supporting pages)**

Paths: W = /home/user/crotest/cro-audit-valentinyeo.com-2026-10-17. Page folders: W/pages/home, W/pages/case-study, W/pages/contact.
Context: ~400 visitors/month, 8 conversions/month (W/readiness.txt, verdict NOT_TESTABLE). Ship the rewrites below and compare before/after; do not plan A/B tests on copy.

## Summary
The home page leads with a specific, proof-backed headline and one consistent CTA. The case study and contact page lose that momentum. The case study is an internal report with no CTA and no link to the teardown. The contact page has no booking link or form. The main conversion path breaks on the two pages a warm visitor is most likely to land on next.

## Headline Analysis

| Element | Current text | Assessment | Suggested rewrite |
|---|---|---|---|
| H1 (home) | "More A/B tests, shipped faster." | Clear, outcome-led, short. It is about test volume, not business results. A buyer who cares about revenue has to infer it. Little emotional pull. | "More A/B tests, shipped faster. Without waiting on developers." Or: "Run 5x more A/B tests, without adding developers." Only use a multiplier you can prove. |
| H2 | "Results, not promises" | Generic phrase any consultant could use. The stats below it are specific and strong. | "+14.6% purchase revenue from one CTA test" |
| H2 | "How I ship tests faster" | Fine, ties to the H1. | Keep. |
| H2 | "Three ways to work together" | Label, not a benefit. | "Pick how much of the work you want me to do" |
| H2 | "See what your site should test first." | Good "you" framing and curiosity, and it sits next to the CTA. | Keep. |
| H1 (case study) | "inne.io CRO Case Study: Optimizing Conversion for a Femtech Pioneer" | Company-centric and jargon-heavy. The result is missing. | "How inne.io lifted purchase revenue 14.6% with one above-the-fold CTA change" |
| H1 (contact) | "Get in Touch" | Generic. Gives no reason to reach out. | "Book your free 20 minute teardown" |

Evidence: W/pages/home/elements.json (headlines); W/pages/case-study/elements.json (h1, h2, h3); W/pages/contact/elements.json (h1).

## Value Proposition Assessment
- **Current value prop**: "I'm a CRO and A/B testing consultant. I've run over 100 tests for inne, took Eduki from 5 to 120+ tests a quarter, and spent 11 years at trivago running hundreds more." (W/pages/home/page.html, hero)
- **Clarity**: 8
- **Uniqueness**: 7 (velocity and overlapping tests are a real differentiator, but "100+ tests" is stated without a result)
- **Specificity**: 8
- **Recommended rewrite**: "I help ecommerce teams run 5x more A/B tests without adding developers. At Eduki I took the team from 5 to 120+ tests a quarter and cut test setup time by 60%. Get a free 20 minute teardown of what your site should test first."
- Weaknesses: the hero copy is mostly "I" (about the consultant). The offer's target customer is never named (ecommerce? SaaS? traffic size?). The hero states volume, while the only revenue result (+14.6%) sits further down.

Evidence: W/pages/home/page.html (hero paragraph, stat strip, "Results, not promises").

## CTA Text Review

| Location | Current text | Issue | Suggested alternative |
|---|---|---|---|
| Nav | "Free teardown" | Clear. Slightly different wording from the main CTA. | "Free 20 min teardown" |
| Hero | "Get your free 20 minute teardown" | Strong: verb, value, price (free) and time commitment. It does not say what you receive or how it is delivered. | Keep, and add micro-copy beneath: "A recorded walkthrough of your top 3 test ideas. No card, no sales pitch." (only if true) |
| Hero secondary | "See the results" | Fine, anchors to #cases. | "See the +14.6% test" |
| Footer | "Get your free 20 minute teardown" | Consistent. Followed by "Or reach out directly: Email / WhatsApp", which is a good low-friction fallback. | Add: "Replies within 1 business day" (only if true) |
| Footer nav | "Contact" | Leads to a page with no booking option (see Finding 2). | Link to cal.com or point to the teardown |
| Case study | none | No CTA at all. | "Want this for your site? Get your free 20 minute teardown" |
| Contact | none | No CTA or form. | Same booking button |

Evidence: W/pages/home/elements.json (ctas: 4 found, all to cal.com/valentinyeo/teardown except "Contact"); W/pages/case-study/elements.json (ctas: []); W/pages/contact/elements.json (ctas: [], forms: []).

## Readability Assessment
- **Flesch-Kincaid grade (estimated)**: Home about grade 6-7 (good). Case study about grade 11-13 (too high).
- **Average sentence length**: Home about 12-15 words. Case study bullets are fragments, mostly noun phrases.
- **Passive voice (estimated)**: under 10% on home. Case study is noun-heavy ("Implemented structured A/B testing methodology").
- **Jargon**: Case study has many unexplained terms: "PIE framework", "overlapping test strategy", "Checkout Started", "Device Usage Imbalance", "analytics infrastructure". The home page uses "teardown", "significance" and "reversible changes" with no definition.
- **Scanability**: Home Good (short blocks, stat strip, numbered steps). Case study Fair (headings and bullets, but 18KB of report-style text and no summary callout). Contact Good (short, but too thin).

Evidence: W/pages/home/page.html; W/pages/case-study/page.html (Strategy & Approach, Key Tests & Results).

## Psychological Trigger Map

| Principle | Present? | Implementation | Effectiveness |
|---|---|---|---|
| Social proof | Yes | One testimonial (JP Bisson, CEO) and a "Selected Clients" row with vetsak and Teeth Lovers as text | Weak. One quote, no photo, no link, and no logos (client_logos: [] in elements.json). Not backed by any numbers from the client. |
| Authority | Yes | "11 yrs at trivago", "100+ tests", "120+ tests a quarter" | Strong |
| Scarcity | No | None. A solo consultant could honestly say "I take on N clients per quarter" | Missing |
| Reciprocity | Yes | Free teardown, open-source claude-cro audit skill | Strong. Good use. |
| Commitment | Partial | Low-commitment first ask (20 minutes, free) | Moderate |
| Liking | Partial | First-person voice, plain language | Moderate. No photo or personal line. |
| Loss aversion | No | Nothing about what slow testing costs | Missing |

Evidence: W/pages/home/elements.json (trust_signals); W/pages/home/page.html.

## Findings

### 1. Case study has no next step (Critical)
The case study is the highest-intent proof page and ends with "Key Learnings & Insights", then the footer. The only exit is "Back to Home". Evidence: W/pages/case-study/elements.json (ctas: []); W/pages/case-study/page.html (text ends at "Social proof elements have higher impact on high-consideration purchases").
Fix: add the teardown CTA at the top (under the H1) and at the end: "Want results like this on your site? Get your free 20 minute teardown."

### 2. Contact page has no booking path (Critical)
The copy says "Please use one of the contact methods above to get in touch. I'll respond as soon as possible." The page lists email, phone, Upwork and an address, with no form, no cal.com link and no expected response time. The home page's main conversion (booking) is not offered here. Evidence: W/pages/contact/elements.json (forms: [], ctas: []); W/pages/contact/page.html.
Rewrite: H1 "Book your free 20 minute teardown". Body: "Pick a time and I'll walk through what your site should test first. Prefer to write? Email me and I'll reply within one business day." Button: "Book my free teardown" linked to the same cal.com page as the home CTA.

### 3. Case study headline and opening lead with the client, not the result (High)
The executive summary opens with the client's location and conversion rate. The +14.6% result is the 4th bullet. The summary is written in "we" and passive-leaning report language. Evidence: W/pages/case-study/page.html (H1 and Executive Summary).
Rewrite the opening: "inne.io sold more of its minilab subscription after one change: moving the main button above the fold. Purchase revenue per visitor rose 14.6% (EUR 3.14 to EUR 3.61). Here is the test and what I learned."

### 4. Case study claims are incomplete (High)
Tests 2 to 5 give a hypothesis but no result, and Test 1 gives no sample size, duration or significance. Home says "100+ tests" but the page shows one winner. Strategic outcomes ("Increased average order value", "Improved primary conversion rate") have no numbers. Unsupported claims reduce trust. Evidence: W/pages/case-study/page.html (Test 2 to Test 5 sections; Strategic Outcomes #4).
Fix: add the result (or "inconclusive, shipped anyway") for each test, plus duration and traffic for Test 1. This also supports the "ship on clear signals" message on home.

### 5. Hero is about the consultant, and the buyer is not named (High)
"I'm a CRO...", "I've run...", "took Eduki...". Suggested fix is the value prop rewrite above. Add a qualifier line under the CTA: "For ecommerce and SaaS teams with 50k+ monthly visitors" (adjust to the real ideal client). Evidence: W/pages/home/page.html (hero).

### 6. Trust proof is thin and one stat is off-message (Medium)
One testimonial, no photo or link; clients shown as plain text. "100% Job Success on Upwork" sits among the stats and "11 yrs Product design at trivago" does not match the "A/B testing" positioning, while the paragraph above says 11 years "running hundreds more [tests]". Evidence: W/pages/home/page.html (stat strip, Selected Clients, What Clients Say); W/pages/home/elements.json (client_logos: []).
Fix: add 2 to 3 more quotes with names, photos and results. Change the trivago stat to "100s of A/B tests at trivago over 11 years". Add a link to the claude-cro audit as proof.

### 7. Service cards are feature-led, with no price or fit (Medium)
"Audit, test plan, design and build", "Analytics, heatmaps and test strategy". Outcomes and who each is for are missing. "CRO Audit" does not say how it differs from the free teardown. Evidence: W/pages/home/page.html (Services section).
Rewrite example: CRO Audit: "A ranked list of what to fix first, with mockups your developers can build from. Best for teams that have traffic but no test plan." Add starting price or a range if you are comfortable, which helps qualify leads.

### 8. Free teardown is not defined (Medium)
The central offer never says what you get (video? call? doc?), what you need to provide, or what happens next. Evidence: W/pages/home/page.html (hero CTA, footer CTA).
Add under the CTA: "I review your site before the call. You get your top 3 test ideas, with the reasoning."

### 9. Metadata and small text defects (Low)
Meta description reads "100+ tests for inne, Eduki from 5 to 120+ tests a quarter, 11 years at trivago" (fragmented, and "inne" is not explained). Copyright says "2025" on case-study and contact but "2026" on home. Case study and contact have no OG tags. Evidence: W/pages/home/elements.json (meta.description); W/pages/case-study/page.html and W/pages/contact/page.html (footer); W/pages/case-study/elements.json (og_tags: {}).
Suggested description: "CRO and A/B testing consultant. I help teams run 5x more tests: 5 to 120+ a quarter at Eduki, +14.6% revenue at inne. Free 20 minute teardown."

## Positive Findings
- Hero H1 is short and clear; the CTA is specific, free and time-boxed (W/pages/home/page.html).
- Same CTA text and destination repeated in nav, hero and footer, with email and WhatsApp as a fallback.
- Concrete numbers in the stat strip and "Results, not promises" cards (+14.6%, 5 to 120+, 60%).
- Good reciprocity offer in the open-source claude-cro skill.
- Footer shows a real name, UK address, phone and legal links, which supports trust.
- Home is easy to read (short sentences, plain words).

## Priority Recommendations
**Critical**: add teardown CTA to the case study (top and end); add a booking button and clearer H1 to the contact page.
**High**: rewrite the case-study opening to lead with the result; complete results for Tests 2 to 5; rewrite the hero value prop to name the buyer and lead with their outcome.
**Medium**: add testimonials with names/photos; fix the trivago stat; explain what the teardown includes; rewrite service cards around outcomes and fit.
**Low**: meta description, copyright year, OG tags.

Note: with about 8 conversions a month, ship these changes in one batch and track the booking rate before and after. Reported industry case studies suggest clear CTAs on every page help, but no lift is promised for this site.
