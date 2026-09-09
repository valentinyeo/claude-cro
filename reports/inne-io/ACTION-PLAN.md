# CRO Action Plan: inne.io
**Date:** 2026-03-01
**CRO Health Score:** 62/100 -- Moderate

---

## How to Use This Plan
- Items are sorted by priority (Critical > High > Medium > Low)
- Start with Critical items -- these are actively blocking conversions
- Each item includes expected impact and effort level to help with prioritization
- Use the Impact/Effort matrix to identify your best ROI improvements

---

## Critical Priority (Fix Immediately -- Blocks Conversions)

### [C-1] Fix German Text in English Checkout
- **Category:** UX / Forms
- **Found by:** cro-ux
- **Expected Conversion Impact:** High -- comprehension failure at point of purchase
- **Implementation Effort:** Easy (Shopify admin, minutes)
- **Description:** The subscription line item displays "Lieferung alle 3 Monate, Abrechnung alle 12 Monate" in German while the entire checkout is in English. For English-language users, this creates confusion about what they are committing to at the most critical conversion moment.
- **Recommendation:** Update Shopify product variant descriptions and subscription metadata to include proper English translations. Ensure all product text matches the checkout session language.

### [C-2] Enable GDPR Consent Enforcement (Pandectes Blocker + Consent Mode v2)
- **Category:** Tracking / Legal
- **Found by:** cro-tracking
- **Expected Conversion Impact:** Medium (legal risk elimination + improved ad measurement)
- **Implementation Effort:** Easy (Pandectes admin configuration)
- **Description:** The Pandectes cookie banner is purely cosmetic -- `blocker.isActive: false` and Google Consent Mode v2 is disabled. Hotjar loads unconditionally before consent. No script blocking is happening. For a German EU-market company, this is significant legal exposure.
- **Recommendation:**
  1. In Pandectes admin: activate the script blocker (`blocker.isActive: true`)
  2. Enable Google Consent Mode v2 (`googleConsentMode.isActive: true`)
  3. Set default consent state: `analytics_storage: denied`, `ad_storage: denied` for EU visitors
  4. Gate Hotjar loading behind consent (currently fires unconditionally)
  5. Map consent categories properly (Performance -> analytics_storage, Targeting -> ad_storage)

### [C-3] Fix Mobile Above-the-Fold Experience (Cookie Banner)
- **Category:** Visual / UX
- **Found by:** cro-visual
- **Expected Conversion Impact:** High -- mobile visitors see no meaningful content on first visit
- **Implementation Effort:** Medium (Pandectes customization or CSS override)
- **Description:** On mobile (375x812), the cookie banner covers ~40% of the viewport. Combined with the 80px announcement bar, first-time mobile visitors see: announcement bar + nav + heading + massive cookie banner. No product image, no CTA, no subheadline visible.
- **Recommendation:** Implement a slim cookie bar (single line, bottom-anchored, ~60px height) or use a less intrusive consent mechanism. The banner must still be legally compliant but should not consume more than 15% of the mobile viewport.

### [C-4] Show Full Price Breakdown Before Checkout
- **Category:** UX / Forms
- **Found by:** cro-ux
- **Expected Conversion Impact:** High -- prevents checkout abandonment from price shock
- **Implementation Effort:** Easy (product page template edit)
- **Description:** Users see "EUR 25/month" on pricing cards but encounter EUR 398 total at checkout (EUR 99 reader + EUR 299 subscription). The upfront billing model is not clearly communicated before the order button.
- **Recommendation:** Add a visible price breakdown above the "Order Now" button: "Total: EUR 398 (Reader EUR 99 + 12-month subscription EUR 299)". Make the total cost unmissable so visitors arrive at checkout with correct expectations.

### [C-5] Add Customer Testimonials with Names and Outcomes
- **Category:** Trust
- **Found by:** cro-trust
- **Expected Conversion Impact:** High -- addresses the most critical trust deficit
- **Implementation Effort:** Medium (content collection + template addition)
- **Description:** Zero customer testimonials anywhere on the homepage. For a EUR 300-500 health product, this is the single most damaging trust deficit. The vague "Thousands of users" claim and conflicting Trustpilot ratings (4.3 vs 4.7, 243 vs 1,258 reviews) further weaken social proof.
- **Recommendation:**
  1. Collect 5-10 real customer stories with first names, photos, and specific outcomes
  2. Place a testimonial carousel above the pricing section
  3. Focus on emotional outcomes: "I finally feel like I understand my own body"
  4. Resolve the conflicting Trustpilot numbers -- display one consistent, verified rating
  5. Replace "Thousands of users" with a specific number

---

## High Priority (Fix Within 1 Week -- Major Conversion Impact)

### [H-1] Amplify Money-Back Guarantee Near All CTAs
- **Category:** Trust
- **Found by:** cro-trust
- **Expected Conversion Impact:** High
- **Implementation Effort:** Easy
- **Description:** The money-back guarantee is mentioned as a small label above the pricing table but has zero specificity -- no duration, no terms, no explanation. The "Order Now" CTA is completely naked with no supporting trust text.
- **Recommendation:** Change from vague "MONEY-BACK GUARANTEE" to specific terms: "30-day money-back guarantee -- no questions asked" (or actual terms). Display with a badge icon directly adjacent to every "Order Now" button.

### [H-2] Improve Hero Text Contrast
- **Category:** Visual / Accessibility
- **Found by:** cro-visual
- **Expected Conversion Impact:** Medium-High
- **Implementation Effort:** Easy (CSS change)
- **Description:** Hero heading (~52px, cream on photographic background) and subheadline fail WCAG AA contrast at ~2.0-2.2:1 ratio. The ghost "Start Quiz" button is also nearly invisible (~2.4:1).
- **Recommendation:** Add a semi-transparent dark overlay behind the text area, or use a text shadow, or place a solid-color background panel behind the hero text. Replace the ghost "Start Quiz" button with a solid variant.

### [H-3] Unify CTA Language Across the Page
- **Category:** Copy / UX
- **Found by:** cro-copy, cro-ux
- **Expected Conversion Impact:** Medium-High
- **Implementation Effort:** Easy (text changes)
- **Description:** 8+ different CTA labels ("Buy Now", "Order now", "Subscribe to inne now", "View All Plans", "Secure your Minilab now", "Get 20 EUR now") all pointing to the same destination. Creates decision paralysis and signals lack of clarity.
- **Recommendation:** Choose one primary CTA phrase and use it consistently. Recommended: "Get My Minilab" or "Start My Plan" -- action-oriented, specific, and value-driven. Keep maximum 2-3 unique CTA labels on the entire page.

### [H-4] Remove `maximum-scale=1.0` from Viewport Meta
- **Category:** UX / Accessibility
- **Found by:** cro-ux
- **Expected Conversion Impact:** Medium (accessibility compliance)
- **Implementation Effort:** Easy (one-line change)
- **Description:** `maximum-scale=1.0` blocks pinch-to-zoom on mobile, violating WCAG 1.4.4. Frustrates users who need to zoom into product details or fine print about subscription terms.
- **Recommendation:** Change to `content="width=device-width, initial-scale=1.0"` (remove maximum-scale entirely).

### [H-5] Reframe the Efficacy Comparison
- **Category:** Copy
- **Found by:** cro-copy
- **Expected Conversion Impact:** High
- **Implementation Effort:** Medium (copy rewrite + possible design adjustment)
- **Description:** The hero displays: inne 92%, Condom 87%, Pill 93%, IUD 99%. This comparison positions inne as less effective than the Pill and IUD. A price-conscious, safety-conscious visitor sees that inne costs EUR 21-33/month AND is less effective.
- **Recommendation:** Add context: pair each method's efficacy with its drawbacks (hormones, side effects, invasiveness). Frame the tradeoff: "92% effective -- comparable to the pill, without the side effects." Or move the comparison to a dedicated section where it can be properly contextualized.

### [H-6] Add Sticky Mobile CTA
- **Category:** Visual / UX
- **Found by:** cro-visual
- **Expected Conversion Impact:** High
- **Implementation Effort:** Medium (template + CSS)
- **Description:** No floating/sticky CTA exists on mobile. Hero CTAs are pushed below the fold by the cookie banner. The only visible mobile CTA is the small "Buy Now" in the header (hard to reach with thumb).
- **Recommendation:** Add a fixed bottom bar with "Order Now" or "Get My Minilab" that appears after scrolling past the hero section. This is standard practice for mobile e-commerce.

### [H-7] Cite Clinical Studies for 92% Effectiveness Claim
- **Category:** Trust / Copy
- **Found by:** cro-trust
- **Expected Conversion Impact:** Medium-High
- **Implementation Effort:** Easy (add citation text)
- **Description:** The 92% effectiveness number is displayed prominently without attribution. For a medical device making efficacy claims, unsourced numbers can actually reduce trust among health-informed buyers.
- **Recommendation:** Add a source citation: "Based on clinical study [reference]" or "Validated in a study of N participants at [institution]". Link to the science page or a published study.

### [H-8] Push VWO Experiment Data to GA4
- **Category:** Tracking
- **Found by:** cro-tracking
- **Expected Conversion Impact:** Medium (enables CRO test analysis)
- **Implementation Effort:** Medium (custom dimension + pixel configuration)
- **Description:** VWO experiment/variation data is not sent to GA4 as custom dimensions. CRO test results cannot be analyzed in GA4.
- **Recommendation:** Implement custom dimensions (`vwo_experiment_name`, `vwo_variation`) sent with every GA4 event during active tests. This enables proper A/B test analysis in GA4.

---

## Medium Priority (Fix Within 1 Month -- Optimization Opportunity)

### [M-1] Add FAQ Accordion Below Pricing Section
- **Category:** UX
- **Found by:** cro-ux
- **Expected Conversion Impact:** Medium
- **Implementation Effort:** Easy
- **Description:** FAQs are linked at the very bottom of the page. No contextual FAQ exists near the pricing section where users have questions about subscription terms, cancellation, and what's included.
- **Recommendation:** Add 3-5 expandable FAQ items directly beneath pricing: "Can I cancel?", "What's included?", "How does the subscription work?", "What if it doesn't work for me?"

### [M-2] Show Total Cost Transparently in Pricing Cards
- **Category:** Copy / UX
- **Found by:** cro-copy
- **Expected Conversion Impact:** Medium
- **Implementation Effort:** Easy
- **Description:** The pricing section shows monthly rates but the total cost (reader + subscription) is never stated. Visitors must calculate EUR 99 + EUR 299 = EUR 398 themselves.
- **Recommendation:** Display the total: "12 months -- EUR 25/month | Total: EUR 398 (reader + 12 months of strips)". Show it upfront to build trust and prevent cart abandonment.

### [M-3] Convert 41 PNG Images to WebP
- **Category:** Performance
- **Found by:** cro-performance
- **Expected Conversion Impact:** Medium
- **Implementation Effort:** Easy (Shopify CDN supports automatic WebP)
- **Description:** 41 PNG images could be served as WebP with 30-50% size reduction. Shopify CDN supports format conversion via URL parameters.
- **Recommendation:** Use Shopify's `| image_url` filter with format conversion, or request `.png` URLs with `format=webp` parameter.

### [M-4] Reduce VWO Render-Blocking Impact
- **Category:** Performance
- **Found by:** cro-performance
- **Expected Conversion Impact:** Medium
- **Implementation Effort:** Medium (VWO configuration)
- **Description:** VWO SmartCode has a 500ms `settings_tolerance` and applies `opacity:0` to hidden elements, creating up to 500ms of invisible content.
- **Recommendation:** Reduce tolerance to 250ms or load VWO asynchronously after FCP. Expected improvement: up to 500ms faster visible content.

### [M-5] Add Payment Method Badges Near Pricing
- **Category:** Trust
- **Found by:** cro-trust
- **Expected Conversion Impact:** Medium
- **Implementation Effort:** Easy (image/icon addition)
- **Description:** No Visa/Mastercard/PayPal/Klarna badges visible anywhere on the page. No lock icon or "Secure checkout" text near the Order Now CTA.
- **Recommendation:** Display accepted payment methods as recognizable logos near the pricing area. Add a lock icon with "Secure checkout" text near CTAs.

### [M-6] Consolidate to Single H1 Per Page
- **Category:** UX / SEO
- **Found by:** cro-ux
- **Expected Conversion Impact:** Medium (SEO + accessibility)
- **Implementation Effort:** Easy
- **Description:** Three H1 tags on homepage: "inne shop" (hidden), "Contraception. Without hormones. Period.", and "What would help you decide?". Violates HTML semantics and confuses search engines.
- **Recommendation:** Make "Contraception. Without hormones. Period." the sole H1. Demote others to H2 or appropriate levels.

### [M-7] Add Health Data Privacy Statement
- **Category:** Trust
- **Found by:** cro-trust
- **Expected Conversion Impact:** Medium
- **Implementation Effort:** Easy
- **Description:** For a product collecting hormonal health data via an app, there is no data privacy communication on the homepage.
- **Recommendation:** Add a brief statement near subscription sign-up: "Your health data is encrypted and never shared. GDPR compliant." with link to privacy policy.

### [M-8] Reduce Homepage Length by 30-40%
- **Category:** UX / Copy
- **Found by:** cro-ux
- **Expected Conversion Impact:** Medium
- **Implementation Effort:** Medium (content audit + template restructuring)
- **Description:** Homepage is ~11,750px with 24 headings and repetitive sections (subscription plans appear twice, "how it works" duplicated).
- **Recommendation:** Consolidate duplicate content. Use pricing and "how it works" sections once each. Remove or minimize the "future features" section. Target ~7,000-8,000px homepage length.

### [M-9] Add Missing E-commerce Events (remove_from_cart, view_cart)
- **Category:** Tracking
- **Found by:** cro-tracking
- **Expected Conversion Impact:** Medium (data completeness)
- **Implementation Effort:** Medium (Shopify pixel configuration)
- **Description:** Google Tag app tracks 7 events but misses `remove_from_cart` and `view_cart`, important for understanding cart abandonment.
- **Recommendation:** Configure these events in the Google Tag Shopify app or create custom pixel events.

### [M-10] Embed Quiz Natively Instead of External Typeform
- **Category:** UX
- **Found by:** cro-ux
- **Expected Conversion Impact:** Medium
- **Implementation Effort:** Hard
- **Description:** "Start Quiz" links to external Typeform, breaking the browsing flow and potentially losing users who leave inne.io.
- **Recommendation:** Either embed using Typeform's embed SDK or build the quiz natively within the Shopify theme for full control of the user experience.

---

## Low Priority (Backlog -- Polish & Fine-Tune)

### [L-1] Add `loading="lazy"` to 18 Images Missing the Attribute
- **Category:** Performance
- **Found by:** cro-performance
- **Expected Conversion Impact:** Low-Medium
- **Implementation Effort:** Easy
- **Description:** 18 images load eagerly by default but are likely below the fold.
- **Recommendation:** Add `loading="lazy"` to below-fold images. Expected: 200-400ms faster initial load.

### [L-2] Standardize Font-Display to `swap`
- **Category:** Performance
- **Found by:** cro-performance
- **Expected Conversion Impact:** Low
- **Implementation Effort:** Easy
- **Description:** Mixed `font-display` values (`swap` vs `fallback`) across 8 `@font-face` declarations can cause Flash of Invisible Text.
- **Recommendation:** Change all to `font-display: swap` to eliminate FOIT.

### [L-3] Add srcset to 34 Raster Images Without Responsive Variants
- **Category:** Performance
- **Found by:** cro-performance
- **Expected Conversion Impact:** Low-Medium
- **Implementation Effort:** Medium
- **Description:** 34 raster images serve desktop-sized assets to mobile users.
- **Recommendation:** Use Shopify's `image_url` with width parameter and srcset generation. Expected: 30-60% less image data on mobile.

### [L-4] Add Alt Text to 56 Images Missing It
- **Category:** UX / SEO
- **Found by:** cro-ux
- **Expected Conversion Impact:** Low (accessibility + SEO)
- **Implementation Effort:** Medium (content audit)
- **Description:** 55% of images (56/102) have empty or missing alt text.
- **Recommendation:** Audit all images. Product images get descriptive alt; purely decorative images get `alt=""`.

### [L-5] Remove or Replace Artificial Stock Urgency
- **Category:** UX / Trust
- **Found by:** cro-ux
- **Expected Conversion Impact:** Low-Medium
- **Implementation Effort:** Easy
- **Description:** "Stock Level: LOW (15%)" with red progress bar is an artificial urgency tactic that erodes trust for a CE-certified medical device.
- **Recommendation:** Remove entirely, or replace with genuine social proof ("X units sold this month").

### [L-6] Reduce Announcement Bar Height
- **Category:** Visual / UX
- **Found by:** cro-visual, cro-ux
- **Expected Conversion Impact:** Low
- **Implementation Effort:** Easy (CSS)
- **Description:** 80px announcement bar consumes 11% of desktop viewport for a generic "CE-certified" message.
- **Recommendation:** Reduce to 32-40px, or integrate this messaging into the hero. Consider making it dismissible.

### [L-7] Add Medical Advisory Board or Professional Endorsements
- **Category:** Trust
- **Found by:** cro-trust
- **Expected Conversion Impact:** Low-Medium
- **Implementation Effort:** Medium (content sourcing)
- **Description:** No doctor, gynecologist, or medical advisor quotes/endorsements visible.
- **Recommendation:** List 2-3 healthcare professionals with credentials. Medical endorsement significantly increases conversion for contraception products.

### [L-8] Consolidate Two GA4 Properties
- **Category:** Tracking
- **Found by:** cro-tracking
- **Expected Conversion Impact:** Low
- **Implementation Effort:** Easy (verification)
- **Description:** Two GA4 measurement IDs detected (G-SL7J4W9VD4 and G-TMZPG99KHW). Verify whether both are intentional.
- **Recommendation:** If redundant, remove one to reduce complexity and page weight.

---

## Impact/Effort Matrix

|  | Easy Effort | Medium Effort | Hard Effort |
|--|-------------|---------------|-------------|
| **High Impact** | C-1 (German checkout text), C-2 (GDPR consent), C-4 (price breakdown), H-1 (guarantee near CTAs), H-3 (unify CTAs), H-4 (viewport zoom), H-7 (cite studies) | C-3 (mobile cookie banner), C-5 (testimonials), H-2 (hero contrast), H-5 (efficacy reframe), H-6 (sticky mobile CTA), H-8 (VWO->GA4) | -- |
| **Medium Impact** | M-1 (FAQ near pricing), M-2 (total cost display), M-3 (PNG->WebP), M-5 (payment badges), M-6 (single H1), M-7 (privacy statement) | M-4 (VWO render-blocking), M-8 (homepage length), M-9 (missing events) | M-10 (embed quiz) |
| **Low Impact** | L-1 (lazy loading), L-2 (font-display), L-5 (remove urgency), L-6 (announcement bar), L-8 (GA4 consolidation) | L-3 (srcset), L-4 (alt text), L-7 (medical endorsements) | -- |

---

## Recommended A/B Test Ideas

Based on the audit findings, these hypotheses are worth testing:

1. **Test: Unified CTA label**
   **Hypothesis:** If we change all CTA buttons from mixed labels ("Buy Now", "Order now", "Subscribe") to a single consistent label ("Get My Minilab"), then click-through rate will improve because reduced decision paralysis and clearer action language drives faster commitment.
   **Primary metric:** CTA click-through rate / Add-to-cart rate
   **Based on:** Copy (H-3), UX (UX-004)

2. **Test: Full price breakdown on product page**
   **Hypothesis:** If we display the total cost (EUR 398 = Reader EUR 99 + 12mo EUR 299) on the product page, then checkout completion rate will improve because users arrive at checkout with correct price expectations, eliminating sticker shock.
   **Primary metric:** Checkout completion rate
   **Based on:** UX (C-4), Copy (M-2)

3. **Test: Money-back guarantee badge adjacent to CTA**
   **Hypothesis:** If we add "30-day money-back guarantee -- no questions asked" as a prominent badge next to every "Order Now" button, then conversion rate will improve because risk reversal at the decision point reduces purchase anxiety for a EUR 300+ commitment.
   **Primary metric:** Conversion rate (purchase)
   **Based on:** Trust (H-1)

4. **Test: Hero headline swap**
   **Hypothesis:** If we replace "The first certified saliva-based alternative to the pill" with "Contraception. Without hormones. Period." as the primary H1, then engagement (scroll depth, CTA click) will improve because the latter is more emotionally resonant, memorable, and benefit-focused.
   **Primary metric:** Hero CTA click-through rate + scroll depth
   **Based on:** Copy (headline analysis)

5. **Test: Efficacy comparison with context vs. raw numbers**
   **Hypothesis:** If we add side-effect context to the efficacy comparison (e.g., "92% effective + zero hormones" vs "93% effective + hormone side effects"), then the comparison section will drive more clicks to the product page because users will weight the hormone-free benefit against the small efficacy difference.
   **Primary metric:** Product page visits from comparison section
   **Based on:** Copy (H-5)

6. **Test: Slim cookie banner vs. current full-size banner (mobile)**
   **Hypothesis:** If we reduce the mobile cookie banner from ~40% viewport coverage to a slim 60px bottom bar, then mobile bounce rate will decrease because visitors will see meaningful content (hero image, value proposition, CTA) on first load instead of a wall of cookie text.
   **Primary metric:** Mobile bounce rate + time on page
   **Based on:** Visual (C-3)

---

## Next Steps

1. **Immediately (this week):** Address C-1 through C-5 -- these are actively blocking conversions and/or creating legal risk
2. **Week 2:** Implement H-1 through H-8 -- major conversion impact items
3. **Month 1:** Work through M-1 through M-10 -- optimization opportunities
4. **Backlog:** Address L-1 through L-8 as capacity allows
5. **Set up A/B tests:** Before making major copy/layout changes (H-3, H-5, hero headline), set up A/B tests via VWO to validate hypotheses
6. **Re-audit in 30-60 days** to measure progress and identify new opportunities
7. **Expanded audit:** Analyze key secondary pages (product page, science page, certification page) for additional conversion opportunities
