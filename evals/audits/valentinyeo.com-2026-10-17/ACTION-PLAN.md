# CRO Action Plan: valentinyeo.com
**Date:** 2026-10-17 · **Score:** 64/100 · **Test readiness:** NOT_TESTABLE (assumed baseline)

## Critical
None. The main path from the home page to the booking calendar works.

## High
### [H-1] Add the teardown button to the case-study pages
- **Page / found by:** case study (and Eduki, trivago, same template) / ux, copy, trust, visual, P1
- **Evidence:** pages/case-study/page.html has 0 cal.com links; the only link on is "Back to Home".
- **Fix:** Add the home-page header with its "Free teardown" button, a button after the Executive Summary, and a closing block "See what your site should test first" with the same button.
- **Effort:** Easy · **How to validate:** ship + baseline

### [H-2] Make the contact page a booking page
- **Page / found by:** contact / ux, copy, visual, tracking, P1
- **Evidence:** pages/contact/elements.json `forms: []`; copy says "use one of the contact methods above".
- **Fix:** Change the H1 to "Book your free 20 minute teardown" with the cal.com button first; move email and WhatsApp under "Prefer to write?" and add a response-time line ("I reply within 1 working day", if true). Drop Upwork or move it to the footer.
- **Effort:** Easy · **How to validate:** ship + baseline

### [H-3] Measure the booking click
- **Page / found by:** all / tracking
- **Evidence:** tracking.json events `{}`; no click handler on the cal.com links.
- **Fix:** Add a `cta_click` event (with page and button position) to every cal.com link, using Plausible, GA4 or a Cloudflare custom event. Connect cal.com bookings to the same tool if available. Send the access requests listed in FULL-AUDIT.md so the baseline becomes CONFIRMED.
- **Effort:** Easy · **How to validate:** ship + baseline (check the events arrive after a test click)

### [H-4] Show results for the other case-study tests
- **Page / found by:** case study / copy, trust, P1
- **Evidence:** pages/case-study/page.html Tests 2-5 have hypotheses only; Test 1 has no sample size or runtime.
- **Fix:** For Test 1 add visitors per variant, run time and confidence. For Tests 2-5 add the outcome (win, loss or flat) or mark them "result not published". A loss reported honestly reads as credibility.
- **Effort:** Medium · **How to validate:** usability research (do the 5 interviewees find the case study convincing?)

## Medium
### [M-1] Explain the teardown next to the button
- **Page / found by:** home / copy, trust, P1, P2
- **Evidence:** pages/home/page.html hero and closing CTA; explanation exists only on cal.com.
- **Fix:** One line under each button: "20 minutes, free, no obligation. Bring your site; you leave with the first 3 things to fix."
- **Effort:** Easy · **How to validate:** ship + baseline

### [M-2] Say who the offer is for and explain the client names
- **Page / found by:** home / copy, P1, P2
- **Evidence:** no "ecommerce", "DTC" or "online store" in pages/home/page.html.
- **Fix:** Add a "for ..." line under the headline and a few words after each named client (inne: hormone-tracking brand; Eduki: education marketplace). Only if this is the audience you want.
- **Effort:** Easy · **How to validate:** usability research

### [M-3] Strengthen proof near the button
- **Page / found by:** home / trust, visual, P1, P2
- **Evidence:** one testimonial with no numbers; vetsak and Teeth Lovers are plain text.
- **Fix:** Add 2-3 more testimonials (ideally one retail result with a number), show client logos, and link the "100% Job Success" stat to the Upwork profile.
- **Effort:** Medium · **How to validate:** ship + baseline

### [M-4] Give Services a price signal
- **Page / found by:** home / P1, P2
- **Evidence:** pages/home/page.html Services has no price or range.
- **Fix:** A "from" price or range per offer, or "priced by traffic" with the teardown as the way to find out.
- **Effort:** Easy · **How to validate:** ship + baseline

### [M-5] Align the inner-page template and fix its contrast
- **Page / found by:** case study, contact / ux, visual, P1
- **Evidence:** amber #F59E0B on white is 2.15:1; purple #a855f7 labels 3.96:1; header lacks nav and button.
- **Fix:** Reuse the home header and theme on all pages; use an accent with at least 4.5:1 contrast on white for text.
- **Effort:** Medium · **How to validate:** ship + baseline

## Low
### [L-1] Keep a CTA in view on mobile
- **Page / found by:** home (mobile) / ux, visual · **Evidence:** pages/home/mobile.png; nav CTA hidden under 640px. **Fix:** a slim sticky button after the hero scrolls away. **Effort:** Easy · **Validate:** ship + baseline

### [L-2] Tidy the booking hand-off
- **Page / found by:** cal.com / P2 · **Evidence:** personas/P2/step-05.png. **Fix:** open cal.com in the same tab or prefill the timezone. **Effort:** Easy · **Validate:** ship + baseline

### [L-3] Make small links tappable and check the blank band
- **Page / found by:** home (mobile) / P2 · **Evidence:** personas/P2/step-03.png, step-04.png. **Fix:** 44px tap targets for "See the results", Email and WhatsApp; re-check the empty band under the header on a real phone. **Effort:** Easy · **Validate:** ship + baseline

### [L-4] Housekeeping
- **Evidence:** pages/case-study/page.html and pages/contact/page.html footers (© 2025); pages/home/page.html Truely card and footer email; tracking.json (Endless Testing loads 0, hits 2); pages/case-study/page.html (0 img).
- **Fix:** update © 2025 to 2026 on the inner pages (F-16); send the Truely card to an on-site page or label it as the Upwork profile (F-10); use a domain email and add a photo (F-15); remove or finish the Endless Testing SDK on home and contact (F-12); add test screenshots to the case study if the client allows (F-19). **Effort:** Easy · **Validate:** ship + baseline

## Research Plan
1. Five moderated sessions with target buyers on the task "decide whether this consultant fits and book a call"; repeat after the High fixes.
2. Microsoft Clarity recordings: watch 30-50 sessions that reached the case study or contact page.
3. One question on the booking confirmation: "What almost stopped you from booking?"
4. Ship H-1 to H-3 and M-1 together; compare teardown clicks and bookings for 4 weeks after vs 4 weeks before (directional only).
5. No A/B test backlog: on the assumed baseline no test can reach a result. Revisit after the real conversion count is known.
