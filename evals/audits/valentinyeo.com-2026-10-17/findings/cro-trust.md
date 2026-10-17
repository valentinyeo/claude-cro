Status: complete

# Trust Signal Analysis: valentinyeo.com (solo CRO consultant, lead gen)

**Trust Score: 58/100 (Moderate)**

## Summary
Strong, specific proof of results (named metrics, 11 years at trivago, 100% Upwork JSS) plus unusually good legal and contact transparency (UK address, phone, sole-trader disclosure, Terms/Privacy/Refund links). Weakness: only one testimonial, no photos, no logos or screenshots, a Gmail address, and no risk reducers at the "Get your free 20 minute teardown" CTA. Case-study and contact pages carry no CTA or proof at all.

## Findings

1. **Single testimonial, no photo, no link (High)**
   Only one quote (JP Bisson, CEO, Truely & International Drivers Association). It is about Truely/IDA, not the headline clients (inne, Eduki, trivago). No headshot, no LinkedIn link, no video.
   Evidence: pages/home/elements.json trust_signals.testimonials (one blockquote); pages/home/page.html "What Clients Say".

2. **"Selected Clients" logos are plain text and not recognizable (High)**
   "vetsak" and "Teeth Lovers" appear with no logo images (elements.json client_logos = [], images = []). inne, Eduki and trivago are named in the hero but not shown as a logo row.
   Evidence: pages/home/page.html "Selected Clients"; pages/home/elements.json client_logos: [], images: [].

3. **Specific, quantified proof (Positive, strength)**
   "+14.6% purchase revenue", "120+ tests a quarter, up from 5", "setup time cut by 60%", "11 yrs trivago", "100% Job Success on Upwork". Specific and checkable. Caveat: the Eduki and 100+ test claims are not backed by a case-study page that the audit loaded (eduki and trivago pages are linked but were not in the audited set), and the stats strip is self-reported.
   Evidence: pages/home/page.html stats strip and "Results, not promises"; pages/case-study/page.html Test 1 "+14.6% (€3.14 → €3.61 per visitor)".

4. **Case study is detailed but has no client voice, no CTA, no sample size or significance (High)**
   The inne page gives baseline numbers (84,408 users, 1.76% CVR) but Tests 2-5 report no results. Test 4 (trust badge) has no outcome. No inne quote, no sign-off, no confidence level. The page has no CTA (elements.json ctas = []) and no navigation to book a call, so a convinced reader has no next step. Footer says "© 2025", while the home page says 2026, which looks stale.
   Evidence: pages/case-study/elements.json ctas: []; pages/case-study/page.html "Test 2" to "Test 5" (no results), footer "© 2025".

5. **No risk reducers at the CTA (High)**
   Primary CTA "Get your free 20 minute teardown" has no nearby line on what the teardown includes, no "no card, no obligation, no sales pitch", and no delivery promise. guarantees: []. "Free" is stated but the cost of the call (time, follow-up pitch) is not addressed. A Refund Policy link exists in the footer, but no guarantee appears near the CTA or in the Services section (no pricing, no refund terms summarized).
   Evidence: pages/home/elements.json guarantees: []; pages/home/page.html CTA at bottom ("Or reach out directly"); footer "Refund Policy".

6. **Gmail address as the business email (Medium)**
   valentin.yeo@gmail.com is used on all three pages. For a consultant selling to CEOs, a domain email (e.g. hello@valentinyeo.com) is a small credibility drag.
   Evidence: pages/home/page.html mailto link; pages/contact/page.html; footer on all three pages.

7. **Contact transparency is strong (Positive)**
   Full UK address (45 Fitzroy Street, London W1T 6EB), phone, WhatsApp, email, LinkedIn, Upwork, GitHub, X, and a "sole trader" legal-identity line in every footer. Caveats: the address appears to be a serviced/virtual office (shared "4th Floor" building), which some visitors may notice; the contact page has no form, no response-time commitment, no hours.
   Evidence: pages/contact/page.html ("Get in Touch", address, phone, "I'll respond as soon as possible"); pages/contact/elements.json forms: [].

8. **Booking link goes to a third party with no preview (Medium)**
   CTA leads to cal.com/valentinyeo/teardown. Reassurance before the click is absent (no photo of Valentin, no "what happens on the call"). The home page has no photo of the consultant at all (images: []). The About link goes to cv.html, a CV, not a personal page with photo/story.
   Evidence: pages/home/elements.json ctas[1].href, images: []; pages/home/page.html nav "About" -> cv.html.

9. **Policy pages and HTTPS present (Positive)**
   HTTPS, Terms, Privacy and Refund Policy linked on every page. There is no form, so no data-handling microcopy is needed on-page; Cal.com is the data handler and is not disclosed. No cookie consent banner and no tracking scripts detected (consent_management false, scripts_found empty), which is consistent and low-risk.
   Evidence: pages/*/fetch.json status 200 on https; pages/*/page.html footer links; pages/*/elements.json tracking.

10. **Authority and thought leadership (Medium, partly positive)**
   Strong: 11 yrs at trivago, Statsig blog link on overlapping tests, open-source claude-cro on GitHub with a public self-audit (transparent, differentiating). Weak: no certifications (e.g. CXL, Google Analytics), no named awards, no talks/press, no publication list, no team (solo, which is fine but should be framed). The Statsig link is labelled "Why overlapping tests are safe" with no author attribution shown.
   Evidence: pages/home/page.html "How I Work" section and claude-cro paragraph; elements.json certifications: [].

11. **Meta description overclaims or reads oddly (Low)**
   "100+ tests for inne, Eduki from 5 to 120+ tests a quarter" is good for trust but un-sourced; the inconsistency of "100% Job Success" without a visible Upwork badge/review count weakens verifiability. Link the stat to the Upwork profile.
   Evidence: pages/home/elements.json meta.description; pages/home/page.html stats strip.

## Social Proof Inventory

| Type | Present? | Quality | Specificity | Placement | Notes |
|---|---|---|---|---|---|
| Testimonials | Yes | 2/5 | Named, no photo | Home mid-page | 1 quote, about different clients than the hero |
| Reviews/Ratings | Partial | 3/5 | Unverified | Home stats strip | "100% Job Success on Upwork", no link/count in strip |
| Client logos | No | 1/5 | Text names only | Home | vetsak, Teeth Lovers as text |
| Case studies | Yes | 4/5 | Detailed | Home cards + case page | inne has numbers; others not audited |
| User counts | No | n/a | n/a | n/a | Not applicable to solo consultant; client count "2" shown |
| Press/awards | No | 1/5 | n/a | n/a | One Statsig article link only |

**Social Proof Quality Score**: 5/10
**Key gap**: more named testimonials with photos from inne, Eduki, trivago.

## Security Signals

| Signal | Present? | Location | Quality |
|---|---|---|---|
| HTTPS/SSL | Yes | URL, Cloudflare | Valid, HSTS not verified |
| Payment badges | N/A | n/a | No checkout |
| Privacy policy | Yes | Footer, all pages | Link present |
| Terms | Yes | Footer, all pages | Link present |
| Data handling near CTA | No | n/a | Third-party Cal.com booking not disclosed |
| Trust seals | No | n/a | Not needed |

## Risk Reducers

| Risk Reducer | Present? | Prominence | Near CTA? | Specific? |
|---|---|---|---|---|
| Money-back guarantee | No (Refund Policy in footer only) | Hidden | No | Not summarized |
| Free trial / free teardown | Yes | High | Yes | 20 minutes, but no terms |
| No obligation / no pitch | No | n/a | No | n/a |
| Cancel anytime | No | n/a | No | n/a |
| Satisfaction guarantee | No | n/a | No | n/a |

**Risk Reducer Score**: 4/10
**Critical gap**: a one-line "what you get / no obligation" next to the CTA.

## Authority

| Signal | Present? | Strength | Notes |
|---|---|---|---|
| Certifications | No | n/a | |
| Awards | No | n/a | |
| Team credibility | Yes | Medium-Strong | trivago 11 yrs, CV page |
| Years in business | Partial | Medium | 11 yrs employed; consulting tenure unstated |
| Partnerships | No | n/a | |
| Thought leadership | Yes | Medium | Statsig post, open-source tool |

## Contact Transparency
Phone: yes (footer, contact page; click-to-call not verified). Address: yes, full. Email: yes, Gmail. Live chat: no (WhatsApp link instead). Form: no. Social: LinkedIn, Upwork, GitHub, X. About: CV page.
**Contact Transparency Score**: 8/10

## Industry Gap (services / consultancy)
Required: client logos, named testimonials with photos, case studies with numbers, process transparency, credentials, clear engagement terms.
Present: case study with numbers, process section, contact details, legal identity.
Missing: logos, more testimonials, photo, pricing or engagement terms, guarantee, credentials.
Benchmark: At or slightly below typical for solo consultants (strong on results, weak on visual proof).

## Priority Recommendations

**Critical**: none (nothing actively blocks conversion).

**High**
- Add 3 to 5 testimonials with photo, name, title, company, ideally one each from inne, Eduki, trivago; link to LinkedIn. (Findings 1, 4)
- Replace text client names with logo row (inne, Eduki, trivago, vetsak, Teeth Lovers) near the hero. (Finding 2)
- Add reassurance under every teardown CTA: e.g. "20 minutes, free, no obligation, you keep the findings." Also describe what the teardown covers. (Finding 5)
- Add a CTA and a client quote to the inne case study; state results for Tests 2-5 or mark them pending, and add significance/sample size. (Finding 4)

**Medium**
- Add a photo and short bio to the home page; make "About" a real page. (Finding 8)
- Use a domain email. (Finding 6)
- Summarize refund/guarantee terms in the Services section. (Finding 5)
- Add a response-time promise to the contact page. (Finding 7)

**Low**
- Update the "© 2025" footers on case-study and contact to match the home page. (Finding 4)
- Link the "100% Job Success" stat to the Upwork profile; add Cal.com note in the privacy policy. (Findings 9, 11)

## Positive Findings
Quantified, specific results; transparent legal/contact details on every page; Terms/Privacy/Refund linked everywhere; open-source tool and public self-audit; clear, single primary CTA with low-commitment offer.

## Trust Placement
Proof is clustered on the home page below the hero (stats, testimonial, results) which follows the decision journey reasonably well. The final CTA block has no proof or risk reducer beside it. Case-study and contact pages are dead ends with no CTA or proof.

Note: analysis is based on page.html and elements.json text. Screenshots (desktop.png, mobile.png) were not visually inspected, so logo rendering and layout placement are inferred from HTML. No lift is promised; any conversion effects are reported in case studies only.
