# Candidates (merged from findings/*.md)
Page folders: pages/home, pages/case-study, pages/contact. Personas: P1 (desktop head of growth), P2 (mobile DTC founder).

| id | page | claim | evidence | priority | sources |
|----|------|-------|----------|----------|---------|
| F-01 | case-study | Dead end: no teardown CTA, header has only CV/LinkedIn, only exit is "Back to Home" | pages/case-study/elements.json ctas: [] ; page.html | Critical | ux, copy, trust, visual, P1 |
| F-02 | contact | No booking path/form/cal.com link; email, WhatsApp, Upwork, address with equal weight; copy says "use one of the contact methods above" | pages/contact/elements.json forms: [] ; page.html | Critical | ux, copy, visual, tracking, P1 |
| F-03 | case-study+contact | Inner pages use a different header/look (no nav, no "Free teardown" button, amber headings on white ~2:1 contrast) than home | pages/*/page.html header; desktop.png | High | ux, visual, P1 |
| F-04 | home | Nothing near the CTA says what the teardown is/gives or that it's no-obligation; "teardown" is jargon (cal.com page does say free, no-obligation) | pages/home/page.html CTA; personas/P2 step-01.png | High | trust, copy, ux, P1, P2 |
| F-05 | home | Proof is thin: one testimonial (about Truely/IDA, no photo, no revenue number), client names vetsak/Teeth Lovers plain text, grey logos | pages/home/elements.json client_logos: [], images: [] | High | trust, visual, copy, P1, P2 |
| F-06 | home | Hero is about the consultant and never says who it is for (ecommerce/DTC); inne and Eduki unexplained | pages/home/page.html hero; P2 step-01.png | High | copy, P1, P2 |
| F-07 | case-study | Tests 2-5 have no results, Test 1 has no sample size/duration/significance; "100+ tests" backed by one winner | pages/case-study/page.html Test 2-5 | High | copy, trust, P1 |
| F-08 | home | Services show no prices, ranges or who each offer is for | pages/home/page.html Services; P1 step-03.png; P2 step-03.png | High | P1, P2 |
| F-09 | home (mobile) | Header "Free teardown" CTA hidden behind hamburger; no sticky CTA after the hero scrolls away | pages/home/mobile.png ; page.html nav-toggle | Medium | ux, visual |
| F-10 | home | Links to Eduki/trivago case studies not found by crawl (unverified); Truely card goes to Upwork | pages/home/page.html case-item links; crawl.json | Medium | ux, trust |
| F-11 | all | Primary conversion is not measured: only Cloudflare Web Analytics (page views), cal.com clicks have no event, cal.com bookings not tied to analytics. (UX/trust claim "no analytics" is WRONG; tracking.json shows Cloudflare on 3 pages.) | tracking.json, TRACKING.md | High | tracking |
| F-12 | home, contact | Endless Testing SDK loads without testId (does nothing) on 2 of 3 pages; site is NOT_TESTABLE | tracking.json; pages/home/page.html script | Medium | tracking, performance |
| F-13 | case-study, contact | Duplicate Pico CSS/Font Awesome/Figtree loads; case-study mobile LCP 1.7 s vs 1.0 s home | pages/case-study/speed.json, page.html | Low | performance |
| F-14 | home | CLS 0.084 (near 0.1 limit) | pages/home/speed.json | Low | performance, ux |
| F-15 | home | Gmail address as business email; About links to CV page; no photo of Valentin | pages/*/page.html mailto; elements.json images: [] | Medium | trust, visual, P2 |
| F-16 | case-study, contact | Footer says 2025, home says 2026 | pages/case-study/page.html footer | Low | ux, trust, copy, P1 |
| F-17 | home (mobile) | "See the results", Email, WhatsApp are small text links; blank ~200px band under header on scroll | personas/P2 step-01/03/04.png | Low | P2, ux |
| F-18 | cal.com | Booking page: timezone empty, slots below fold on mobile, opens in new tab, no prep/what-you-get | personas/P2 step-05.png ; P1 c/step-01.png | Medium | P1, P2 |
| F-19 | case-study | Long text-only page, no images/test screenshots | pages/case-study/elements.json images: [] | Low | ux, visual |
