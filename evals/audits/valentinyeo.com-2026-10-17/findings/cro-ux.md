Status: complete

# UX Heuristic Evaluation: valentinyeo.com (home, case-study, contact)

**UX Score: 66/100 (Moderate)**
**Forms: none on any page** (pages/home, pages/case-study, pages/contact elements.json all have `"forms": []`). Forms score not applicable.

## Summary
The homepage is clean, fast and has one clear primary action (the "Get your free 20 minute teardown" button, linking to cal.com). The conversion path breaks down on the two secondary pages. The case study and contact pages have no booking CTA at all, so a visitor who reads proof or goes to Contact is sent to manual email, WhatsApp or Upwork. Site traffic is about 400 visitors/month, so these are qualitative findings. Test with 5 users rather than A/B testing (readiness.txt: NOT_TESTABLE).

## Issue Table

| ID | Heuristic | Sev | Area | Description | Recommendation |
|----|-----------|-----|------|-------------|----------------|
| UX-001 | H4/H6, conversion path | 4 | Case study page | Dead end: no CTA, no cal.com link. Header has only CV and LinkedIn, and the only forward link is "Back to Home". The visitor has just read the strongest proof and has no next step. | Add the teardown button after Executive Summary and at the end, plus a sticky CTA. |
| UX-002 | H4/H6 | 3 | Contact page | The primary action (book a call) is missing. It offers 4 equal-weight options (email, WhatsApp, Upwork, street address) and no form. The text says "use one of the contact methods above", which pushes users to compose an email. | Put the teardown button at the top. Demote Upwork and the address. Optionally add a 3-field form. |
| UX-003 | H4 consistency | 3 | Case study and contact header | The homepage has a nav and a "Free teardown" CTA. Inner pages use a different header (CV and LinkedIn icon only) with no nav or CTA. | Reuse the homepage header with the CTA on all pages. |
| UX-004 | Broken navigation | 3 | Home to case study links | The home page links to inne-case-study.html and eduki-case-study.html, and also to trivago-case-study.html. crawl.json only found the inne one. The Truely card links to Upwork, an external marketplace, so it leads away from the site. | Verify the Eduki and trivago pages load. Point the Truely card to an on-site page or remove the link. |
| UX-005 | H1/H4 (mobile) | 2 | Home mobile nav | Mobile hides all nav behind a hamburger (button `.nav-toggle`, 44px). The header "Free teardown" CTA is not visible on mobile in the first view. The hero button is visible, which is good. | Keep the hero button. Consider a sticky bottom CTA after the hero scrolls away. |
| UX-006 | H8 | 2 | Home hero and stats | The hero text and the stat strip (100+, 120+, 11 yrs) repeat the same claims, which pushes the cases and services below the first screens on mobile. | Merge the stats into the hero. |
| UX-007 | H10 | 2 | Home | There is no FAQ or "what happens on the call" text near the CTA. A free 20 minute teardown is vague (what do I get, what do you need from me). | Add 2-3 lines under the button: what you send, what you get, no obligation. |
| UX-008 | H2 / H8 | 2 | Case study | Long text-only page (7 h2 and 18 h3 headings, no images per elements.json `"images": []`) with no visuals of tests. | Add test screenshots, a key-results summary and pull-quote. |
| UX-009 | H4 / H5 | 2 | Contact | Phone number is shown as text for a WhatsApp link (wa.me), and the link is the same text as a phone. The email link is plain text. Mixed expectations. | Label each: "WhatsApp +44...", "Email". |
| UX-010 | H1 | 1 | All pages | No analytics or tracking found (`tracking.scripts_found: []`, `data_layer: false`), so the owner cannot see where users drop. | Install basic analytics and track cal.com clicks. |
| UX-011 | Cosmetic | 1 | Footer | Footer says "© 2025" while the audit date is 2026. Contact page repeats the address twice. | Update the year. |

## Top 5 Quick Fixes
1. Add the teardown button to the case-study page (UX-001).
2. Put the teardown button at the top of the contact page (UX-002).
3. Use the same header and CTA across all pages (UX-003).
4. Check that every case-study link works and keep Truely on-site (UX-004).
5. Add a short "what happens on the call" note under the hero button (UX-007).

## Mobile-Specific Findings
- Viewport meta is present on all three pages (`width=device-width,initial-scale=1`).
- Home mobile.png: the hero button is full-width, about 130px tall in a 924px-wide render (clearly above 44px), and sits in the first screen. Good for a thumb.
- "See the results" is a text link with small height and sits directly under the button. It is probably under 44px tall. Add padding.
- Hamburger hides the nav and the nav CTA; the CSS sets 44px min targets for menu links.
- Contact mobile.png: the text links (email, phone) are readable, but the target is the text line only, with no button styling.
- I did not measure horizontal scroll with a script; mobile.png and mobile-full.png showed no sign of it. This is a screenshot check only.
- Lab speed (pages/home/speed.json): LCP 1.0 s, CLS 0.084, TBT 64 ms, 34 KB. Lab only, no real-user data.

## Conversion Path Analysis
- Primary path: Home hero button to cal.com booking = 1 click. Good.
- From case study: no direct path (needs Back to Home, then the button = 2 clicks, if the user thinks of it). From Contact: no booking path, only manual email or message.
- Friction points: UX-001, UX-002, UX-003, UX-004. Competing links on home (Upwork, GitHub, Statsig blog, the claude-cro repo link) pull away from the CTA.
- Recommended: one CTA, same label ("Get your free 20 minute teardown"), on every page, and make Contact a booking page.

## Positive Findings
- Clear H1 and value proposition ("More A/B tests, shipped faster.") with named proof (inne, Eduki, trivago).
- One dominant CTA with specific, low-risk wording. It is repeated near the bottom of the home page (two `btn-primary` instances in pages/home/elements.json and page.html).
- A named testimonial (JP Bisson, CEO) and measurable case metrics (+14.6% revenue).
- Fast, light pages (8 requests, 34 KB) and semantic headings.

## Evidence index
- pages/home/elements.json (ctas, headlines, forms, tracking), pages/home/page.html (nav-toggle, case-item links, @media 640px), pages/home/mobile.png, pages/home/speed.json
- pages/case-study/elements.json (`ctas: []`, `images: []`), pages/case-study/page.html (header, back-link, 0 cal.com links)
- pages/contact/elements.json (`forms: []`), pages/contact/page.html ("Contact information only, no form"), pages/contact/mobile.png
- crawl.json, readiness.txt
