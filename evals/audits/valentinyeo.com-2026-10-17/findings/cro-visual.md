Status: complete

# Visual Hierarchy Analysis: valentinyeo.com

**Visual Score: 64/100 (Moderate)**
Home about 80, case study about 50, contact about 45. Weighted toward the home page, which is the entry point.

Method: I judged from screenshots and elements.json only. Contrast ratios are visual estimates because I did not sample pixels. Testing is NOT_TESTABLE (readiness.txt: about 400 visitors/month, 8 conversions/month). So every fix below should be shipped and tracked as a before/after change, not A/B tested. No lifts are promised.

## Summary
The home page has a strong, clean hierarchy. It has one dominant dark pill CTA, a large two-tone headline and good whitespace. The case-study and contact pages drop the CTA entirely and use a different, generic visual style (white background, amber and purple accents). Visitors who arrive there have no clear next step.

## Above the fold

**Desktop (1440x900, home)**
- Visible: logo, nav (Results, Services, About), dark "Free teardown" pill, H1 "More A/B tests, shipped faster.", a proof paragraph, the primary CTA "Get your free 20 minute teardown" and the text link "See the results".
- CTA visible: Yes. Value proposition visible: Yes.
- Hero: type only, with no image, face or logo strip. It is clean but gives no visual proof.
- Space use: the 50/50 split leaves about 55% of the fold empty. The H1 sits low-left (y about 450) and the CTA sits right (y about 560). The eye has to jump across the vertical divider (Z-pattern) from headline to CTA, and the CTA is not under the headline.
- Evidence: pages/home/desktop.png; pages/home/elements.json (ctas, headlines.h1).

**Mobile (375px, home)**
- Visible: logo, hamburger, H1, 5-line proof paragraph, full-width dark CTA (about y 1000-1130 of 2000 displayed, so about 50% down the fold), "See the results" link, then the stat block starts.
- CTA visible: Yes, but only just. It sits below a long paragraph. The nav "Free teardown" button is hidden behind the hamburger.
- Value proposition visible: Yes.
- Thumb-reachable: the CTA is full width and about 66px tall at 3x, which is more than 44px. It sits in the middle of the screen, not in the thumb zone, and nothing is sticky.
- Evidence: pages/home/mobile.png; pages/home/mobile-full.png.

## CTA visibility

| CTA | Location | 3s? | Contrast | Size | Isolation | Overall |
|---|---|---|---|---|---|---|
| Primary "Get your free 20 minute teardown" (home hero) | Right column, mid-fold | Yes | Good (white on near-black, over 12:1) | about 330x53 px desktop; full width on mobile | Good | Strong |
| Nav "Free teardown" | Top right (desktop only) | Yes | Good | about 153x40 px | Good | Strong on desktop; hidden behind hamburger on mobile |
| "See the results" | Next to the primary CTA | Yes | Medium (grey underlined text) | text link | Good | Appropriately weak. On mobile it sits close under the primary CTA. |
| Closing CTA "See what your site should test first" | Page bottom | Yes (mobile-full) | Good | full width | Good | Strong |
| Case study: any CTA | none | No | n/a | n/a | n/a | Absent |
| Contact: any booking CTA | none (email, WhatsApp, Upwork as plain text) | No | n/a | n/a | n/a | Absent |

**3-second test:** Home passes. Case study fails because the page has no conversion action. Contact fails because the booking link used everywhere else is missing.
Evidence: pages/home/elements.json (ctas has the cal.com link, 2 placements plus nav); pages/case-study/elements.json (`"ctas": []`); pages/contact/elements.json (`"ctas": []`, `"forms": []`).

## Visual hierarchy map
```
PRIMARY:   H1 "More A/B tests, shipped faster." (largest, bold, orange second line)
           Dark CTA pill (highest contrast block)
SECONDARY: Proof paragraph with bolded inne / Eduki / trivago
           Stats block (100+, 120+, 11 yrs, 100%)
TERTIARY:  Client logo row, testimonial, Results cards, "How I work", Services
LOST:      - Nav CTA on mobile (hamburger)
           - Case-study and contact CTAs (missing)
           - Testimonial from JP Bisson: small, with no photo of the client
           - Services (3 offers) have no CTA or price and look like plain text
```

## Color and contrast
- Brand: near-black plus a terracotta/orange accent (#c4703f approx.) on an off-white background. This reads as calm, premium and editorial.
- CTA is dark on light and does not use the accent colour. It has strong contrast and is the only solid filled shape in the fold. That works, but the accent orange (headline, "not promises", numerals) competes slightly with it.
- Orange headline text on off-white is about 3.8:1. This is acceptable for large type only.
- Case study and contact use a different palette: amber (#f59e0b approx.) heading text on white is about 2:1, which fails WCAG even for large text. Purple "Key achievements:" and green icons on contact are a third and fourth accent. Home and sub-pages do not look like the same brand.
- Colour blindness: the key CTA relies on luminance contrast, not hue, so it is safe. The orange/green accents are decorative only.
- Evidence: pages/home/desktop.png; pages/case-study/desktop.png; pages/contact/desktop.png.

## Images
| Image | Location | Relevant | Quality | Supports conversion | Notes |
|---|---|---|---|---|---|
| Hero | Home above fold | n/a | n/a | No | No image or photo of the consultant. Elements.json lists no hero image. |
| Client logos | Home, "Selected Clients" | Yes | Good, but low contrast (light grey) | Weak | Text-only logos in grey; "vetsak" and "Teeth Lovers" look unlike the rest. Evidence: pages/home/mobile-full.png |
| Testimonial avatar | Home | Yes | OK (small purple initial) | Weak | No real photo of the client. |
| Case study | Whole page | n/a | n/a | No | `"images": []`. There are no charts, screenshots or test variants for tests that are described in text. |
| Contact | Whole page | n/a | n/a | No | No portrait. |
Evidence: pages/case-study/elements.json, pages/contact/elements.json (images empty); pages/home/mobile-full.png.

## Desktop vs mobile
- Layout adapts cleanly on home. The split hero stacks, type scales and the CTA goes full width.
- The mobile hero is text-heavy: a 5-line paragraph sits between the H1 and the CTA, which pushes the CTA to about the middle of the first screen.
- Stats stack vertically at large size, which spends a lot of scroll before the logos and testimonial.
- The nav CTA vanishes on mobile with no sticky replacement. This is the biggest mobile gap, since the stated conversion is a single click.
- Case study and contact are mobile-readable but wide-line, plain pages.
- Evidence: pages/home/mobile.png, pages/home/mobile-full.png, pages/case-study/mobile.png, pages/contact/mobile.png.

## Findings and recommendations

**Critical**
1. **Contact page has no visual path to the booking CTA.** The page lists email, phone, Upwork and a street address as plain grey rows, with the copy "Please use one of the contact methods above". It has no button, no form and no cal.com link, and no booking action that matches the home CTA. Add the same dark pill "Get your free 20 minute teardown" (to https://cal.com/valentinyeo/teardown) at the top, above the contact list, and visually demote the other methods to secondary. Evidence: pages/contact/desktop.png; pages/contact/elements.json (`ctas: []`, `forms: []`).
2. **Case study has zero CTAs.** The page is a long text document that ends without a next step. It has only "Back to Home", CV and LinkedIn in the header. Add the hero CTA near the top (after "Key achievements") and at the end, and add a sticky mobile bar. Evidence: pages/case-study/elements.json (`ctas: []`); pages/case-study/desktop.png.

**High**
3. **No sticky or persistent mobile CTA.** The nav "Free teardown" button is hidden in the hamburger on mobile and the page is long (about 16k px on desktop full-page, per mobile-full). Add a sticky bottom bar with the same label after the hero CTA scrolls out. Evidence: pages/home/mobile.png (hamburger only); pages/home/mobile-full.png.
4. **Mobile hero buries the CTA under a 5-line paragraph.** Shorten the paragraph to 1-2 lines on mobile, or move the stats strip beside it, so the CTA lands higher on the first screen. Evidence: pages/home/mobile.png.
5. **Sub-pages break brand consistency and fail contrast.** Amber (#f59e0b approx.) heading text on white is about 2:1, and sub-pages use purple and green. Re-skin them with the home palette (near-black plus terracotta, off-white background) and darken accent text to 4.5:1 for body-size text and 3:1 for large text. Evidence: pages/case-study/desktop.png (amber H1, purple "Key achievements:"); pages/contact/desktop.png (amber "Touch", green icons).
6. **Home hero has no visual proof or face.** The hero is all type. Consider a portrait or a single result card (for example "+14.6% purchase revenue, inne") near the CTA. Evidence: pages/home/desktop.png (empty top-right and bottom area).

**Medium**
7. **Case-study results are text only.** The 14.6% claim and five tests have no screenshots, control/variant images or charts. Add one before/after image per test. Evidence: pages/case-study/elements.json (`images: []`).
8. **Client logos are pale and mixed in style.** Make them darker and consistent, and add a short caption of the result for each. Evidence: pages/home/mobile-full.png.
9. **Services have no CTA of their own.** The three offers (Done-For-You, CRO Audit, Hourly) are plain text blocks. Link each to the teardown or booking page, or add one clear CTA beneath. Evidence: pages/home/elements.json (h3 list; ctas has no services links).
10. **Hero whitespace is unbalanced on desktop.** The H1 and the CTA column do not share a baseline, so the eye zigzags. Align the H1 and the CTA block, or place the CTA directly under the H1. Evidence: pages/home/desktop.png.

**Low**
11. Contact footer copy reads "© 2025" while the audit date is 2026. Update it. Evidence: pages/contact/desktop.png.
12. "See the results" is directly under the CTA on mobile and could be mistaken for a second CTA. Add space or make it smaller. Evidence: pages/home/mobile.png.
13. Testimonial: add a real photo and a company link. Evidence: pages/home/mobile-full.png.

## Positive findings
- One clear, high-contrast primary CTA, repeated at the bottom of the home page, with the same copy and link each time. Evidence: pages/home/elements.json.
- Strong typographic hierarchy: a big two-tone H1, good size steps and consistent section headings.
- Generous whitespace and calm palette read as credible and premium for a solo consultant.
- Specific, bolded proof (inne, Eduki, trivago) sits right next to the CTA. Evidence: pages/home/desktop.png.
- The CTA button is well over 44px on mobile, and the layout does not break at 375px.
