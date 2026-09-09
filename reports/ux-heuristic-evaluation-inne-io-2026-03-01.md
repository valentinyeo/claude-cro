# UX Heuristic Evaluation: inne.io

**URL:** https://inne.io
**Date:** 2026-03-01
**Evaluator:** Claude Opus 4.6 (Automated Heuristic Evaluation)
**Business Type:** E-commerce / FemTech (Shopify, subscription model, EUR pricing)
**Device Tested:** Desktop 1280x720 (primary), mobile 375x812 (limited)

---

## UX Score: 62/100 -- Moderate

### Summary

inne.io presents a visually refined brand identity with warm tones and professional design language, but suffers from significant structural UX issues that measurably impact conversion. The homepage is extremely long (~11,750px) with repetitive content sections and competing CTAs that dilute the primary conversion path. The subscription pricing model -- which requires substantial upfront commitment (EUR 199-499) -- lacks adequate trust reinforcement at decision points. Critical issues include mixed-language content in checkout, three H1 tags causing SEO and accessibility confusion, 56 of 102 images missing alt text, and a viewport meta tag that blocks pinch-to-zoom on mobile. The checkout flow itself (Shopify native) is well-structured, but the journey *to* checkout contains unnecessary friction.

---

## Issue Table

| ID | Heuristic | Severity | Element/Area | Description | Recommendation |
|----|-----------|----------|-------------|-------------|----------------|
| UX-001 | H2: Match System & Real World | 4 | Checkout - Order Summary | The subscription line item displays "Lieferung alle 3 Monate, Abrechnung alle 12 Monate" in German while the entire checkout is in English. For an English-language user, this creates confusion about what they are committing to at the most critical conversion moment. | Ensure all Shopify product descriptions and variant names are properly localized. The subscription metadata must match the checkout language. |
| UX-002 | H4: Consistency & Standards | 3 | Entire Site - H1 Tags | Three H1 tags found: "inne shop" (hidden/SR-only), "Contraception. Without hormones. Period." (hero), and "What would help you decide?" (survey section). Multiple H1s violate HTML semantics, confuse screen readers, and hurt SEO. | Use a single H1 per page. The hero headline should be the sole H1. Demote others to H2. |
| UX-003 | H8: Minimalist Design | 3 | Homepage Length | The homepage is ~11,750px tall with 24 heading elements and at least 7 distinct sections. Multiple sections repeat similar messaging (subscription plans appear twice, "how it works" content is duplicated). This creates cognitive overload and scroll fatigue. | Reduce homepage length by 30-40%. Consolidate duplicate content. Use the "how it works" and pricing sections once each, well above the fold. |
| UX-004 | H8: Minimalist Design | 3 | Competing CTAs | The homepage contains at least 8 distinct CTA elements: "Buy Now" (header), "Order now", "Start Quiz", "Subscribe to inne now", "Order Now & Save EUR 121", "View All Plans", "Order Now", "Secure your Minilab now". Different labels for the same action create decision paralysis. | Standardize CTA copy. Use one primary label ("Order Now" or "Start your subscription") consistently. Reserve secondary CTAs for genuinely different actions (e.g., quiz vs. direct purchase). |
| UX-005 | H3: User Control & Freedom | 3 | Viewport Meta Tag | `maximum-scale=1.0` in the viewport meta tag blocks pinch-to-zoom on mobile. This is an accessibility violation (WCAG 1.4.4) and frustrates users who need to zoom into product details or small text. | Change to `maximum-scale=5.0` or remove the maximum-scale constraint entirely. |
| UX-006 | H6: Recognition > Recall | 3 | Images - Alt Text | 56 out of 102 images (55%) are missing alt text. This impacts screen reader users, SEO, and users on slow connections where images fail to load. Product images and trust badges are among those affected. | Audit all images and add descriptive alt text. Product images should describe the product; decorative images can use `alt=""`. |
| UX-007 | H5: Error Prevention | 3 | Subscription Pricing Transparency | The pricing section shows "6 months -- EUR 33/month, Billed upfront: EUR 199" but the actual checkout shows EUR 398.00 total (EUR 99 reader + EUR 299 subscription). The upfront cost discrepancy between the pricing card (EUR 299) and checkout total (EUR 398) is not clearly communicated before checkout. | Show the full total (device + subscription) on the product page before the user clicks "Order Now". Add a price breakdown summary: "Reader EUR 99 + 12-month subscription EUR 299 = EUR 398 total". |
| UX-008 | H2: Match System & Real World | 2 | Stock Level Indicator | "Stock Level: LOW (15%)" with a red progress bar appears on the product page. This is a common artificial urgency tactic that can erode trust, especially for a health/medical device where users expect transparency and integrity. A separate check showed "Only 21 left" in the DOM. | Either remove the urgency indicator entirely, or replace it with genuine social proof ("X units sold this month"). For a CE-certified medical device, trust > urgency. |
| UX-009 | H4: Consistency & Standards | 2 | Navigation Architecture | The nav contains 6 informational links (minilab, contraception, how it works, blog, science, certification) plus "inne shop" and "Buy Now". Several of these pages share the same hero section, creating a feeling of navigating without arriving. The "contraception" link has a "new" badge suggesting it is recently added content. | Consolidate navigation. "minilab" and "contraception" could be merged. Consider a mega-menu or dropdown that groups informational pages under "Learn" and shopping under "Shop". |
| UX-010 | H10: Help & Documentation | 2 | FAQ Placement | FAQs are linked ("View FAQs") at the very bottom of the page, after the footer-area section. There is no contextual FAQ or tooltip near the pricing section where users likely have questions about subscription terms, cancellation policy, or what is included. | Add expandable FAQ/accordion directly beneath the pricing section addressing: "Can I cancel?", "What is included?", "How does the subscription work?", and "What if it does not work for me?". |
| UX-011 | H1: Visibility of System Status | 2 | Checkout - Shipping Estimate | The checkout shows "Shipping: Enter shipping address" with no estimated delivery timeline until the address is entered. The product page mentions "Delivery time: 2-3 days" in small print, but this is not reinforced at checkout. | Show estimated delivery timeline prominently on both the product page and checkout. "Order today, receive by [date]" reduces purchase anxiety. |
| UX-012 | H7: Flexibility & Efficiency | 2 | No Search Functionality Visible | While a search drawer exists in the DOM, the search icon is hidden on desktop (`class="hidden tap-area"`). Users cannot search the site from the homepage. | Make the search icon visible in the header. Even for a single-product store, search allows users to find specific information (e.g., "cancellation", "CE certification", "app"). |
| UX-013 | H5: Error Prevention | 2 | Newsletter Email Form | The footer email signup has `placeholder=" "` (single space) and a floating label "Your Email Address". The submit button is an arrow icon with no text label. There is no visible validation feedback or success confirmation described in the HTML. | Add clear inline validation, a visible submit label ("Subscribe"), and a success state confirmation message. |
| UX-014 | H9: Error Recovery | 2 | Checkout Form Errors | Shopify's native checkout handles validation, but there is no visible inline validation before form submission. Country defaults to Germany, which is appropriate for the primary market but may confuse international visitors. | This is largely Shopify-controlled. Consider adding a note on the product page about which countries are supported for shipping. |
| UX-015 | H4: Consistency & Standards | 2 | "Start Quiz" External Link | The "Start Quiz" CTA links to `form.typeform.com/to/JhYq9whk`, an external Typeform. This opens without warning that the user is leaving inne.io, breaking the browsing flow and potentially losing the user. | Either embed the quiz inline using Typeform's embed SDK, or clearly indicate that the link opens an external tool. Ideally, build the quiz natively within the Shopify theme for full control. |
| UX-016 | H8: Minimalist Design | 2 | Header Height | The sticky header is 106px tall (announcement bar + navigation bar). On a 720px viewport, this consumes 14.7% of the visible screen. On mobile, this ratio would be even higher. | Collapse the announcement bar on scroll or reduce header height. Consider hiding the announcement bar after first visit (cookie-based). |
| UX-017 | H4: Consistency & Standards | 1 | External Links Missing rel="noopener" | 9 out of 15 external links are missing `rel="noopener"`. This is a minor security concern (target="_blank" without noopener can expose `window.opener`). | Add `rel="noopener noreferrer"` to all external links with `target="_blank"`. |
| UX-018 | H1: Visibility of System Status | 1 | Announcement Bar Carousel | The announcement bar has Previous/Next buttons suggesting multiple slides, but the auto-rotation speed and content are not easily perceivable. Users may miss important announcements. | Ensure the carousel pauses on hover, has visible pagination dots, and rotates slowly enough (5+ seconds per slide) for reading. |
| UX-019 | H6: Recognition > Recall | 1 | Trustpilot Widget Placement | Trustpilot widget (4.3/5, 243 reviews) exists in the page but was not visible in the main content flow during desktop scrollthrough. It appears to be positioned in a section that may not be immediately visible. | Move the Trustpilot widget to a prominent position near the pricing section and hero area. Social proof near the conversion point is most effective. |
| UX-020 | H7: Flexibility & Efficiency | 1 | No Guest Checkout Indicator | The checkout page does not prominently indicate that guest checkout is available. The "Sign in" option is visible, but nervous first-time buyers may worry about needing an account. | Add a "No account needed" or "Guest checkout" indicator near the email field. |
| UX-021 | H10: Help & Documentation | 1 | Script Payload | 95 script tags and 2,512 DOM elements suggest a heavy page. Multiple third-party integrations (VWO, Hotjar, Trustpilot, Pandectes cookie consent, Zendesk, PayPal) contribute to load time. | Audit third-party scripts and lazy-load non-critical ones. Consider whether all scripts are needed on every page. |

---

## Top 5 Quick Fixes

1. **Fix the German text in checkout** (UX-001, Severity 4): Update the Shopify subscription product variant descriptions to include English translations. This directly blocks comprehension at checkout and could be fixed in minutes via the Shopify admin.

2. **Remove `maximum-scale=1.0` from viewport meta** (UX-005, Severity 3): Change line 8 of the theme layout to `content="width=device-width, initial-scale=1.0"`. This is a one-line change that fixes an accessibility violation.

3. **Show full price breakdown before checkout** (UX-007, Severity 3): Add a visible "Total: EUR 398 (Reader EUR 99 + 12-month subscription EUR 299)" line above the "Order Now" button on the product page. Prevents checkout abandonment from price shock.

4. **Consolidate to a single H1** (UX-002, Severity 3): Change the hidden "inne shop" H1 and the survey "What would help you decide?" H1 to appropriate heading levels (H2 or visually-hidden span). Improves accessibility and SEO.

5. **Add FAQ accordion to pricing section** (UX-010, Severity 2): Insert 3-5 expandable FAQ items directly beneath the subscription pricing covering cancellation policy, what is included, how strips refills work, and return/money-back policy. Addresses key purchase anxieties at the decision point.

---

## Mobile-Specific Findings

- **Pinch-to-zoom blocked**: The viewport meta tag includes `maximum-scale=1.0`, preventing users from zooming. This is an accessibility barrier and a common source of user frustration, especially when reading small pricing details or fine print about subscription terms.

- **Navigation structure**: The mobile view uses a hamburger menu (`lg:hidden` class) with a slide-out drawer containing all navigation links plus "Buy Now" and "Login" CTAs. The mobile drawer CTA structure is appropriate.

- **Mobile hero content differs**: The mobile version appears to show a different hero ("Can you really measure fertility hormones in saliva? Oh yes!") compared to desktop ("The first certified saliva-based alternative to the pill"). While this may be intentional A/B testing via VWO, inconsistent messaging between devices can confuse users who switch between phone and desktop.

- **Sticky header on mobile**: The 106px header on a 375px-wide screen would occupy a significant portion of the viewport. The announcement bar + nav bar combined would reduce usable content area substantially.

- **Touch target sizes**: Navigation link heights are 20px (well below the 44px minimum). However, these are within the main nav which is hidden behind the hamburger on mobile, so the actual mobile touch targets (hamburger button, drawer links) are likely appropriately sized.

- **Footer layout on mobile**: The 5-column footer layout (Minilab overview, Customer Service, Get to know us, Support, Newsletter) would need to stack vertically on mobile. Based on the Shopify theme structure, this likely works correctly but was not directly testable at mobile viewport.

---

## Conversion Path Analysis

**Primary conversion path:**
1. Land on homepage (inne.io)
2. Scroll to hero section or click "Buy Now" in header
3. Arrive at product page (/products/minilab-subscription)
4. Select subscription plan (6/12/24 months)
5. Click "Order Now"
6. Complete Shopify checkout (email -> delivery -> payment -> confirm)

**Steps to conversion:** 4-5 clicks minimum (homepage -> Buy Now -> select plan -> Order Now -> checkout completion). This is acceptable for a EUR 200-500 purchase.

**Friction points identified:**
- **Price shock at checkout**: User sees EUR 25/month on the product page but EUR 398 total at checkout. The upfront billing model needs clearer communication.
- **Mixed language at checkout**: German subscription description in an English checkout session.
- **Too many CTAs on homepage**: 8+ conversion-related buttons with different labels dilute the primary path.
- **No trust reinforcement at decision point**: The pricing section lacks testimonials, guarantee badges, or FAQ. Trustpilot is elsewhere on the page.
- **External quiz link**: "Start Quiz" sends users to Typeform, risking drop-off.
- **No progress indicator**: The single-page Shopify checkout does not show step numbers, though the sections (Contact -> Delivery -> Payment) are logically ordered.

**Recommended path optimization:**
- Reduce the homepage to a clear hero + value propositions + pricing + social proof + FAQ sequence.
- Place Trustpilot widget and "30-day trial" messaging directly adjacent to the pricing options.
- Show the complete price breakdown (device + subscription) on the product page itself.
- Replace the Typeform quiz with an embedded or native experience.
- Add a sticky mobile CTA bar that persists while scrolling.

---

## Cognitive Load Assessment

- **Hick's Law violation**: The homepage presents 8+ distinct CTA buttons with different labels for essentially the same action. This creates decision paralysis. The subscription pricing section alone offers 3 plans plus an upfront/monthly toggle.
- **Information density**: The 11,750px homepage with 24 headings contains too much content for a single scroll. Users face a comparison table, two separate pricing sections, a 3-step "how it works" explanation, a survey form, media logos, trust badges, and multiple product showcases.
- **Progressive disclosure**: Partially implemented. The comparison tabs and "how it works" steps use progressive revelation. However, the overall page structure dumps all information at once rather than guiding users through a funnel.
- **Miller's Law**: The navigation presents 6 items plus 3 utility links (9 total), which is at the upper boundary. The pricing section presents 3 plan options, which is ideal. The footer has 5 columns of links, which is manageable.

---

## Checkout Form UX Assessment

**Positive aspects:**
- Single-page checkout (Shopify's modern checkout) reduces step anxiety
- Express checkout options (Shop Pay, PayPal, Google Pay) at the top
- Smart defaults: Country pre-selected to Germany, "Use shipping address as billing address" pre-checked
- Email field with newsletter opt-in (pre-checked -- note: this may violate GDPR in some interpretations)
- Floating labels for form fields
- Security reassurance: "All transactions are secure and encrypted"
- Discount code field visible but not dominant

**Issues:**
- Mixed language in order summary (German subscription description)
- Subtotal shows "2 items" without explaining that this includes a device AND a subscription -- potentially confusing
- "Recurring subtotal: EUR 299.00 every 12 months" is small and easy to miss
- No estimated delivery date visible at checkout
- No trust badges or guarantees near the payment section
- Email newsletter opt-in is pre-checked (potential GDPR concern in EU markets)

---

## Positive Findings

- **Strong visual brand identity**: The warm color palette (orange CTAs, cream backgrounds, brown text) is consistent, distinctive, and appropriate for the femtech/health space. The design conveys both warmth and scientific credibility.
- **CE certification and regulatory trust**: Prominent display of CE mark, ISO certification, and IVDR compliance badges provides essential trust signals for a medical device.
- **Well-structured checkout**: Shopify's native checkout is clean, efficient, and offers express payment options (Shop Pay, PayPal, Google Pay) that reduce checkout friction.
- **Good font loading strategy**: Custom fonts use `font-display: swap` with preloaded WOFF2 files, minimizing flash of invisible text.
- **Skip-to-content link**: Accessibility best practice implemented.
- **Structured data**: Schema.org markup for BreadcrumbList, WebSite, and Organization provides good SEO foundation.
- **Clear value proposition**: "The first certified saliva-based alternative to the pill" is immediately understandable and differentiating.
- **Comparison section**: The tabbed comparison with thermometers, fertility apps, and ovulation kits helps users understand inne's positioning.
- **Media coverage section**: Frankfurter Allgemeine, TechCrunch, and other logos provide third-party credibility.
- **Lazy loading**: 81 of 102 images use `loading="lazy"`, which is good for performance.
- **Sticky header with primary CTA**: The "Buy Now" button is always accessible in the header, keeping the conversion path one click away.
- **Responsive grid system**: The CSS uses proper breakpoints (700px, 1000px, 1150px, 1400px, 1600px) for responsive layouts.

---

## Severity Distribution

| Severity | Count | Labels |
|----------|-------|--------|
| 4 - Catastrophic | 1 | UX-001 |
| 3 - Major | 5 | UX-002, UX-003, UX-004, UX-005, UX-006 |
| 2 - Minor | 9 | UX-007 through UX-016 (minus UX-008) |
| 1 - Cosmetic | 5 | UX-017 through UX-021 |

**Total issues identified:** 21

---

## Category Breakdown

| Category | Score | Notes |
|----------|-------|-------|
| Visual Design & Branding | 85/100 | Strong, cohesive, premium feel |
| Navigation & IA | 55/100 | Too many nav items, shared hero sections, confusing page identity |
| Conversion Path Clarity | 50/100 | Too many competing CTAs, price confusion, missing trust at decision points |
| Mobile UX | 60/100 | Zoom blocked, responsive structure exists but header is oversized |
| Accessibility | 45/100 | 55% missing alt text, zoom blocked, multiple H1s, outline:none on links |
| Checkout UX | 75/100 | Good Shopify checkout but mixed language and missing delivery estimate |
| Content & Messaging | 65/100 | Clear value prop but verbose and repetitive page structure |
| Trust & Social Proof | 70/100 | Trustpilot, certifications present but not optimally placed |
| Performance Indicators | 60/100 | 95 scripts, 2,512 DOM elements, heavy third-party load |
| Error Handling | 65/100 | Shopify handles checkout errors; newsletter form lacks feedback |

**Weighted average: 62/100**
