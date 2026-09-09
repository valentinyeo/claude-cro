# CRO Audit Report: inne.io
**Date:** 2026-03-01
**URL Analyzed:** https://inne.io
**Business Type:** E-commerce (Shopify) -- FemTech / Health / Subscription Model

---

## Executive Summary

### CRO Health Score: 62/100 -- Moderate

| Category | Score | Weight | Weighted |
|----------|-------|--------|----------|
| UX | 62/100 | 25% | 15.5 |
| Copy | 64/100 | 20% | 12.8 |
| Trust | 62/100 | 15% | 9.3 |
| Visual | 68/100 | 15% | 10.2 |
| Forms | 55/100 | 10% | 5.5 |
| Performance | 58/100 | 10% | 5.8 |
| Tracking | 62/100 | 5% | 3.1 |
| **Total** | | **100%** | **62.2** |

### Score Breakdown
```
UX:          [======----] 62/100
Copy:        [======----] 64/100
Trust:       [======----] 62/100
Visual:      [=======---] 68/100
Forms:       [=====-----] 55/100
Performance: [======----] 58/100
Tracking:    [======----] 62/100
```

### Top 5 Critical Issues (Blocking Conversions)

1. **German text in English checkout** -- UX -- Severity 4: Subscription line item reads "Lieferung alle 3 Monate, Abrechnung alle 12 Monate" in an English checkout session, undermining comprehension at point of purchase.
2. **Cookie banner destroys mobile above-fold** -- Visual -- Critical: On mobile (375x812), the Pandectes cookie banner covers ~40% of the viewport. Combined with the announcement bar, first-time mobile visitors see almost no meaningful content.
3. **GDPR consent enforcement is non-functional** -- Tracking -- Critical: Pandectes cookie banner is purely cosmetic -- `blocker.isActive: false` and Google Consent Mode v2 is not enabled. Hotjar loads unconditionally before consent. Scripts fire regardless of user consent state.
4. **Price shock at checkout** -- UX -- Severity 3: Users see "EUR 25/month" on pricing cards but encounter EUR 398 total at checkout (EUR 99 reader + EUR 299 subscription). No full price breakdown shown before checkout.
5. **Zero customer testimonials** -- Trust -- Critical: For a EUR 300-500 health product, there are no customer quotes, named stories, or outcome testimonials anywhere on the homepage. Trustpilot ratings show conflicting numbers (4.3 vs 4.7, 243 vs 1,258 reviews).

### Top 5 Quick Wins (Easy + High Impact)

1. **Fix German subscription text in checkout** -- UX -- Shopify admin change, minutes to fix, directly removes comprehension barrier at purchase.
2. **Enable Pandectes script blocker + Google Consent Mode v2** -- Tracking -- Configuration change in Pandectes admin, eliminates GDPR legal exposure.
3. **Remove `maximum-scale=1.0` from viewport meta** -- UX -- One-line code change, fixes WCAG accessibility violation.
4. **Show full price breakdown on product page** -- UX -- Add "Reader EUR 99 + 12-month subscription EUR 299 = EUR 398 total" above Order Now button. Prevents checkout abandonment.
5. **Amplify money-back guarantee near CTAs** -- Trust -- Move guarantee from a small label to a prominent badge adjacent to every "Order Now" button with specific terms ("30 days, no questions asked").

---

## UX Analysis

**UX Score: 62/100 -- Moderate**

### Summary

inne.io has a strong visual brand identity and a well-structured Shopify checkout, but suffers from significant structural issues that hurt conversion. The most critical problems are: German text in English checkout (Severity 4), 3 H1 tags on the homepage, ~11,750px page with repetitive content, 8+ competing CTAs with different labels for the same action, `maximum-scale=1.0` blocking pinch-to-zoom, and 55% of images missing alt text.

### Issue Table

| ID | Heuristic | Severity | Element/Area | Description | Recommendation |
|----|-----------|----------|-------------|-------------|----------------|
| UX-001 | H2: Match System & Real World | 4 | Checkout - Order Summary | Subscription line item displays "Lieferung alle 3 Monate, Abrechnung alle 12 Monate" in German while checkout is in English. | Ensure all Shopify product descriptions and variant names are properly localized to match checkout language. |
| UX-002 | H4: Consistency & Standards | 3 | Entire Site - H1 Tags | Three H1 tags found: "inne shop" (hidden/SR-only), "Contraception. Without hormones. Period." (hero), and "What would help you decide?" (survey section). | Use a single H1 per page. The hero headline should be the sole H1. |
| UX-003 | H8: Minimalist Design | 3 | Homepage Length | Homepage is ~11,750px tall with 24 heading elements and at least 7 distinct sections. Multiple sections repeat similar messaging. | Reduce homepage length by 30-40%. Consolidate duplicate content. |
| UX-004 | H8: Minimalist Design | 3 | Competing CTAs | 8+ distinct CTA elements with different labels ("Buy Now", "Order now", "Subscribe to inne now", etc.) for the same action. | Standardize CTA copy to one primary label used consistently. |
| UX-005 | H3: User Control & Freedom | 3 | Viewport Meta Tag | `maximum-scale=1.0` blocks pinch-to-zoom on mobile (WCAG 1.4.4 violation). | Change to `maximum-scale=5.0` or remove the constraint. |
| UX-006 | H6: Recognition > Recall | 3 | Images - Alt Text | 56/102 images (55%) missing alt text, impacting accessibility and SEO. | Audit all images and add descriptive alt text. |
| UX-007 | H5: Error Prevention | 3 | Subscription Pricing | Pricing shows "EUR 25/month" but checkout totals EUR 398. Upfront cost discrepancy not clearly communicated. | Show full total (device + subscription) on the product page before "Order Now". |
| UX-008 | H2: Match System & Real World | 2 | Stock Level Indicator | "Stock Level: LOW (15%)" with red progress bar -- artificial urgency tactic that erodes trust for a health product. | Remove or replace with genuine social proof ("X units sold this month"). |
| UX-009 | H4: Consistency & Standards | 2 | Navigation Architecture | 6 informational links plus shop, with shared hero sections creating confusion. | Consolidate to 3-4 key links; group under "Learn" and "Shop". |
| UX-010 | H10: Help & Documentation | 2 | FAQ Placement | FAQs linked at page bottom. No contextual FAQ near pricing where questions arise. | Add expandable FAQ directly beneath pricing section. |
| UX-011 | H1: Visibility of System Status | 2 | Checkout - Shipping | No estimated delivery timeline until address entered. | Show "Order today, receive by [date]" prominently. |
| UX-012 | H7: Flexibility & Efficiency | 2 | No Visible Search | Search icon hidden on desktop despite existing in DOM. | Make search icon visible in header. |
| UX-013 | H5: Error Prevention | 2 | Newsletter Email Form | Placeholder is single space, submit is icon-only, no validation feedback. | Add inline validation, visible submit label, success confirmation. |
| UX-014 | H9: Error Recovery | 2 | Checkout Form Errors | No visible inline validation before form submission. Pre-checked newsletter opt-in may violate GDPR. | Add note about supported shipping countries; uncheck newsletter by default. |
| UX-015 | H4: Consistency & Standards | 2 | "Start Quiz" External Link | Links to external Typeform without warning user leaves inne.io. | Embed quiz inline or clearly indicate external link. |
| UX-016 | H8: Minimalist Design | 2 | Header Height | Sticky header is 106px (14.7% of 720px viewport). | Collapse announcement bar on scroll or reduce height. |
| UX-017 | H4: Consistency & Standards | 1 | External Links | 9/15 external links missing `rel="noopener"`. | Add `rel="noopener noreferrer"` to all external `target="_blank"` links. |
| UX-018 | H1: Visibility of System Status | 1 | Announcement Bar Carousel | Auto-rotation speed unclear; users may miss announcements. | Pause on hover, add pagination dots, 5+ second rotation. |
| UX-019 | H6: Recognition > Recall | 1 | Trustpilot Widget Placement | Widget exists but not visible in main content flow. | Move to prominent position near pricing section and hero. |
| UX-020 | H7: Flexibility & Efficiency | 1 | No Guest Checkout Indicator | Checkout doesn't indicate guest checkout is available. | Add "No account needed" near email field. |
| UX-021 | H10: Help & Documentation | 1 | Script Payload | 95 script tags, 2,512 DOM elements, heavy third-party load. | Audit and lazy-load non-critical scripts. |

### Severity Distribution

| Severity | Count |
|----------|-------|
| 4 - Catastrophic | 1 |
| 3 - Major | 5 |
| 2 - Minor | 9 |
| 1 - Cosmetic | 5 |

### Positive Findings
- Strong visual brand identity with cohesive warm color palette
- Well-structured Shopify checkout with express payment options (Shop Pay, PayPal, Google Pay)
- Good font loading strategy with `font-display: swap` and preloaded WOFF2
- Skip-to-content link for accessibility
- Schema.org markup (BreadcrumbList, WebSite, Organization)
- Clear value proposition: "The first certified saliva-based alternative to the pill"
- Effective comparison section with thermometers, fertility apps, and ovulation kits
- Lazy loading on 81/102 images
- Sticky header with persistent "Buy Now" CTA

---

## Copy Analysis

**Copy Score: 64/100 -- Moderate**

### Summary

inne.io presents a genuinely differentiated product -- the world's first certified saliva-based hormone tracker -- but the copy underperforms relative to the product's uniqueness. The homepage suffers from a confused hierarchy (multiple H1 tags, inconsistent messaging), generic CTAs, and a pricing section that creates more anxiety than it resolves. Customer-centric language is excellent (you/your outnumbers we/our 12:1) and readability is strong, but it fails to land a single, memorable value proposition and scatters intent across too many directions.

### Headline Analysis

| Element | Current Text | Assessment |
|---------|-------------|------------|
| Announcement bar | "Hormone-free contraception -- CE-certified" | Good -- immediately communicates product and builds trust |
| H1 (hero) | "The first certified saliva-based alternative to the pill" | Strong uniqueness claim but leads with feature (saliva-based) not benefit |
| H1 (below fold) | "Contraception. Without hormones. Period." | **Best headline on the page** -- punchy, memorable, clever wordplay. But competes with first H1 |
| H2 | "The future is more: Hormones, Vitamins & beyond" | Vague, distracts from current purchase decision |
| H2 | "The superior method for cycle control" | Unsubstantiated comparative claim that triggers skepticism |
| H2 | "Thousands of users, one mission" | Good social proof direction but "thousands" is vague |
| H2 | "Is inne right for me?" | Effective -- addresses real objection, creates self-selection |

### CTA Consistency Problem

The page presents 8+ different CTA labels for the same destination: "Buy Now", "Order now", "Subscribe to inne now", "Order Now & Save", "View All Plans", "Secure your Minilab now", "Get 20 EUR now". This inconsistency signals lack of clarity and overwhelms visitors.

### Value Proposition Assessment
- **Clarity:** 6/10 -- "Saliva-based" requires explanation
- **Uniqueness:** 9/10 -- "First certified" is powerful and defensible
- **Specificity:** 5/10 -- 92% efficacy stat appears but is not integrated into the main value proposition

### Readability
- **Flesch-Kincaid Grade Level:** 7th-8th grade (Good)
- **Passive voice:** ~3% (Excellent)
- **You/Your vs We/Our ratio:** 12:1 (Excellent)

### Benefit-to-Feature Ratio
Approximately **1.25:1** -- below the target 3:1 ratio. The pricing section is almost entirely feature-driven.

### Efficacy Comparison Problem
The hero displays: inne 92%, Condom 87%, Pill 93%, IUD 99%. This transparency play actually works against conversion -- inne is visually positioned as less effective than the Pill and IUD. Needs reframing with context about the hormone-free tradeoff.

### Positive Findings
- Excellent customer-centric language (12:1 you/your ratio)
- Very low passive voice (~3%)
- "Contraception. Without hormones. Period." is outstanding copy
- Clear "Is inne right for me?" self-selection section
- Effective three-step "How it works" (Observe / Knowledge / Fertility)
- Sensible subscription tiering with "MOST POPULAR" anchoring
- Money-back guarantee exists (though underutilized)

---

## Trust Signal Analysis

**Trust Score: 62/100 -- Moderate**

### Summary

inne.io has notable strengths in medical certification visibility (CE, IVDR, ISO) and press coverage from recognizable outlets. However, significant gaps remain in customer testimonial depth, risk-reversal specificity near conversion points, and the absence of clinical study data. For a health product requiring significant buyer commitment, the trust ecosystem leaves too many anxiety points unaddressed at the moment of purchase decision.

### Social Proof Inventory

| Type | Present? | Quality | Notes |
|------|----------|---------|-------|
| Testimonials | No | 0/10 | Zero customer quotes or named stories anywhere on homepage |
| Reviews/Ratings | Yes | 3/10 | Trustpilot present but conflicting numbers (4.3 vs 4.7, 243 vs 1,258 reviews) |
| Certification badges | Yes | 8/10 | Red Dot, ISO, CE mark, FuE seal |
| User counts | Yes | 2/10 | "Thousands of users" -- not specific |
| Press/awards | Yes | 7/10 | TechCrunch, Brigitte, Frankfurter Allgemeine, Gala, mum |

### Security Signal Checklist

| Signal | Present? | Notes |
|--------|----------|-------|
| HTTPS/SSL | Yes | Shopify SSL via Cloudflare, HSTS enabled |
| Payment badges | **No** | No Visa/Mastercard/PayPal/Klarna badges visible |
| Privacy policy | Yes | Footer link |
| Terms of service | Yes | Footer link |
| Trust seals near checkout | **No** | No security seals near order CTA |
| Imprint (legal) | Yes | German legal requirement fulfilled |

### Guarantee Analysis

| Risk Reducer | Present? | Issue |
|-------------|----------|-------|
| Money-back guarantee | Yes | No duration, terms, or conditions specified. Just the text label. |
| Free trial | Partial | "See for yourself -- for 30 days" mentioned once, not positioned as core promise |
| Cancel anytime | Partial | "After minimum term you can cancel monthly" -- hedged language increases anxiety |
| Risk-reversal near CTA | **No** | "Order Now" button has zero supporting trust text |

**Risk Reducer Score: 3/10** -- The money-back guarantee has zero specificity for a EUR 300-500 commitment.

### Authority Signals

| Signal | Present? | Strength |
|--------|----------|----------|
| CE Certification | Yes | Strong |
| IVDR Compliance | Yes | Strong |
| ISO Certification | Yes | Strong |
| Red Dot Design Award | Yes | Moderate |
| Clinical studies | **No** | Not cited |
| Healthcare professional endorsements | **No** | No doctor/gynecologist quotes |
| Team/founder credibility | Partial | Team page exists but not on homepage |

### Contact Transparency Score: 4/10

- Phone: German mobile number buried in footer
- Email: support@inne.io (professional)
- Live chat: **Not present**
- Physical address: Not visible on homepage
- Social: Facebook, Instagram, LinkedIn in footer

### Trust Placement Problem
The overall trust architecture has a "front-loaded, back-empty" problem: authority signals are concentrated in the first half of the page, while the actual conversion point (pricing section and Order Now CTA) is the least trust-supported area of the page.

### Positive Findings
- Medical certification stack (CE + IVDR + ISO) is genuinely strong
- Press coverage section is credible with recognizable outlets
- Science page demonstrates genuine subject matter expertise
- Legal compliance is thorough (Privacy Policy, Terms, Imprint, Cookie Policy)
- Technically excellent security headers (HSTS, CSP, X-Frame-Options)
- Product comparison provides honest, transparent positioning

---

## Visual Hierarchy Analysis

**Visual Score: 68/100 -- Moderate**

### Summary

inne.io presents a warm, visually appealing femtech brand with a distinctive cream-and-orange palette and strong photography. However, the above-the-fold area is heavily compromised by an oversized announcement bar and persistent cookie banner (especially devastating on mobile), the hero heading has poor contrast against its image background, and too many competing CTAs dilute the primary conversion path.

### Above-the-Fold Analysis

**Desktop (1440x900):**
- Announcement bar (80px) + Header (106px) = 186px of navigation/utility space, consuming **26% of the viewport** before content
- CTA visible: "Buy Now" in header + two hero CTAs ("Order now" / "Start Quiz")
- Value proposition visible but hero text contrast is poor (~2.2:1, fails WCAG AA)

**Mobile (375x812):**
- Cookie banner covers ~40% of the initial viewport
- Hero CTAs pushed entirely below the fold
- Only visible CTA is the small "Buy Now" header button
- First-time mobile visitor sees: announcement bar + nav + heading + massive cookie banner

### CTA Visibility

| CTA | Contrast | Size | Isolation | Overall |
|-----|----------|------|-----------|---------|
| Buy Now (header) | 6.16:1 PASS | 183x56px | Moderate | Strong |
| Order now (hero) | 6.16:1 PASS | 138x50px | Poor (next to Start Quiz) | Moderate |
| Start Quiz (hero) | Ghost button, ~2.4:1 FAIL | 138x52px | Poor | Weak |

**3-Second Test:** PARTIAL PASS on desktop, FAIL on mobile.

### Color & Contrast

- Brand palette: Cream `#FAF6F0`, Orange `#FF9954`, Brown `#4D270E`, Navy `#1A2640` -- cohesive and premium
- CTA button contrast (brown on orange): 6.16:1 -- PASS
- Hero heading (cream on image): ~2.2:1 -- **FAILS WCAG AA**
- Ghost "Start Quiz" button: ~2.4:1 -- **FAILS WCAG AA**
- Orange button shape on cream background: 2.03:1 -- potential issue for colorblind users

### Critical Issues
1. Mobile above-fold destroyed by cookie banner (~40% of viewport)
2. No sticky mobile CTA -- hero CTAs invisible on mobile after cookie banner
3. Hero text fails WCAG contrast (cream text on photo background without overlay)
4. Announcement bar consumes 11% of desktop viewport for generic messaging

### Positive Findings
- Premium, distinctive brand aesthetic appropriate for femtech
- Strong product photography -- authentic, diverse, not stock
- Effective comparison widget above the fold
- Solid CTA button contrast (6.16:1)
- Sticky header with persistent "Buy Now"
- Clear content sectioning with alternating backgrounds

---

## Performance Impact Analysis

**Performance Score: 58/100 -- Concerning**

### Summary

inne.io has excellent server infrastructure (162ms TTFB via Cloudflare with Brotli compression) and proper script loading patterns. However, the page is substantially undermined by its sheer weight -- 541 KB of raw HTML containing 170 KB inline CSS, 150 KB inline JavaScript, 103 images, and at least 7 third-party services.

### Load Time Estimates & Conversion Impact

| Metric | Value |
|--------|-------|
| TTFB | 162ms (excellent) |
| Estimated FCP | 1.5-2.0 seconds |
| Estimated LCP | 3.0-4.0 seconds |
| Mobile load estimate (4G) | 5-7 seconds |
| Estimated conversion impact | 14-21% reduction vs optimal |
| Mobile bounce probability | 53%+ (exceeds 3s threshold) |

### Resource Analysis

| Resource Type | Count | Size Estimate |
|--------------|-------|---------------|
| HTML document | 1 | 541 KB (113 KB compressed) |
| Inline CSS | 57 blocks | 170 KB |
| External CSS | 3 | ~80-120 KB |
| Inline JS | 49 blocks | 150 KB |
| External JS | 13 | ~200-300 KB |
| Images | 103 | ~1.5-3 MB (41 PNG, 29 WebP, 32 SVG) |
| Fonts | 4 families / 8 variants | ~200-300 KB |
| Videos | 2 (mobile + desktop) | ~2-5 MB |
| **Total estimated** | **~230+ resources** | **~4-8 MB** |

### Third-Party Script Impact

| Script | Impact | Essential? |
|--------|--------|-----------|
| VWO | **HIGH** -- 500ms hide tolerance, sync loading | Yes (CRO) |
| Hotjar | MEDIUM -- runtime overhead | Conditional |
| Klaviyo | MEDIUM -- 33 references, flyout popups | Yes |
| Pandectes | MEDIUM-HIGH -- 31.6 KB inline JSON | Yes (legal) |
| Zendesk | MEDIUM -- loads on interaction | Conditional |
| Trustpilot | MEDIUM -- 13 widgets, external requests | Yes (conversion) |

**Total third-party domains:** 26 unique domains

### Image Optimization Opportunities

| Finding | Estimated Savings |
|---------|-------------------|
| 41 PNG images -> WebP | 30-50% size per image |
| 34 images without srcset | Significant on mobile |
| 11 images missing width/height | Eliminates CLS |
| 18 images without `loading="lazy"` | Deferred bandwidth |
| 57 images with missing alt | Accessibility + SEO |

### Positive Findings
- Excellent TTFB (162ms) via Shopify + Cloudflare CDN
- Brotli compression active (79% reduction)
- All external scripts properly deferred/async
- Hero image uses WebP with `fetchpriority="high"`
- 81/103 images use `loading="lazy"`
- CDN preconnect hints properly configured
- Strong security headers (HSTS, CSP, X-Frame-Options)

---

## Tracking & Analytics Analysis

**Tracking Score: 62/100 -- Partial**

### Summary

inne.io has a multi-layered tracking infrastructure with GA4, Google Ads, Meta Pixel, TikTok Pixel, Klaviyo, VWO, Hotjar, and HubSpot all present via Shopify Web Pixels Manager. However, a critical GDPR compliance gap exists: Google Consent Mode v2 is **not activated**, the Pandectes cookie blocker is **inactive**, and Hotjar loads unconditionally before consent.

### Detected Platforms

| Platform | Status | Notes |
|----------|--------|-------|
| GA4 | Installed | G-SL7J4W9VD4 + G-TMZPG99KHW (two properties) |
| Google Ads | Installed | AW-656814298, full funnel tracking |
| Meta Pixel | Installed | 673787719924257 + CAPI enabled |
| TikTok Pixel | Installed | CU91KOBC77U9AA466AL0 |
| VWO | Installed | Account 996036, EU endpoint |
| Hotjar | Installed | **Loads before consent (GDPR violation)** |
| Klaviyo | Installed | Email/SMS marketing, Sk5rMt |
| HubSpot | Detected | Cookies declared, may be consent-gated |
| Pandectes CMP | Installed | **Blocker INACTIVE, Consent Mode v2 OFF** |

### Conversion Events

| Event | Detected? | Quality |
|-------|-----------|---------|
| page_view | Yes | Full configuration |
| view_item | Yes | Google + VWO tracking |
| search | Yes | Google Ads configured |
| add_to_cart | Yes | Google + VWO + Klaviyo |
| begin_checkout | Yes | Google + VWO |
| purchase | Yes | Google + VWO + Shopify |
| remove_from_cart | **No** | Missing |
| view_cart | **No** | Missing |
| form_submit (newsletter) | Partial | Klaviyo flyout, not a Google Ads conversion |

### GDPR Compliance: CRITICAL VIOLATION

- Cookie banner present but **purely cosmetic** -- `blocker.isActive: false`
- Google Consent Mode v2: **NOT IMPLEMENTED** (`googleConsentMode.isActive: false`)
- Hotjar loads unconditionally before consent (session recording without consent)
- No `dataLayer` implementation -- all data flows through Shopify pixel sandbox
- VWO experiment data not pushed to GA4 as custom dimensions

### Positive Findings
- Well-structured Google Ads conversion funnel (7 events)
- Meta Pixel with CAPI for server-side tracking
- VWO properly configured with EU data endpoint
- Zendesk chat is properly consent-gated
- Shopify native analytics with session attribution active

---

## Form Analysis

**Form Score: 55/100 -- Weak**

### Summary

Derived from UX agent's form-specific findings, the checkout and form UX has fundamental issues that create friction at critical conversion moments.

### Checkout Form Assessment

**Positive:**
- Single-page Shopify checkout reduces step anxiety
- Express checkout options (Shop Pay, PayPal, Google Pay) at top
- Smart defaults: Country pre-selected to Germany
- "All transactions are secure and encrypted" reassurance
- Floating labels for form fields

**Issues:**
- **Mixed language in order summary:** German subscription description in English checkout -- Severity 4
- **Price shock:** Subtotal shows "2 items" without explaining device + subscription split. "Recurring subtotal: EUR 299.00 every 12 months" is small and easy to miss
- **No estimated delivery date** at checkout
- **No trust badges or guarantees** near payment section
- **Pre-checked newsletter opt-in** -- potential GDPR violation in EU markets

### Newsletter Form Assessment

- Placeholder text is a single space (`" "`)
- Submit button is an arrow icon with no text label
- No visible validation feedback or success confirmation
- No indication of what the user receives by subscribing

### Conversion Path Form Friction

| Friction Point | Severity | Impact |
|---------------|----------|--------|
| German text in English checkout | 4 | Comprehension failure at purchase moment |
| Price discrepancy (EUR 25/mo vs EUR 398 total) | 3 | Checkout abandonment from sticker shock |
| No FAQ near pricing/order form | 2 | Unresolved questions prevent purchase |
| External Typeform quiz | 2 | User leaves site, may not return |
| No guest checkout indicator | 1 | Unnecessary account anxiety |

---

## Methodology Notes

- All analysis performed via headless browser rendering (agent-browser + Playwright) and HTML source inspection
- Desktop viewport: 1440x900 and 1280x720
- Mobile viewport: 375x812
- Screenshots captured for visual analysis (archived in /tmp/)
- TTFB measured via multiple curl requests with timing
- Business type detected as E-commerce/FemTech based on: Shopify platform, product listings, cart/checkout, subscription pricing, CE-certification claims, health/contraception positioning
- All scores reflect the homepage (inne.io) as the primary analyzed URL
