# Proven CRO Tests: Ecommerce & Shopify

A curated database of A/B tests with documented results for ecommerce sites,
Shopify stores, and DTC brands. Use these as high-confidence test ideas when
auditing ecommerce properties.

**How to use this database:**
- Reference tests by ID (e.g., `EC-001`) in audit reports and test plans.
- Use the ICE scores as starting points — adjust based on the specific site context.
- Tests marked with higher confidence have been replicated across multiple sites.
- "Avg. Lift" is the median observed effect; actual results vary by site.

---

## Product Page (PDP) Tests

### EC-001: Sticky Add-to-Cart Button

| Field | Value |
|-------|-------|
| **Element** | Add-to-Cart CTA |
| **Page** | Product Detail Page |
| **Control** | Standard ATC button that scrolls out of view |
| **Variant** | Sticky/fixed ATC bar that remains visible on scroll |
| **Avg. Lift** | +18–32% add-to-cart rate |
| **Confidence** | High — replicated across 12+ ecommerce tests |
| **ICE Score** | I: 8 · C: 9 · E: 8 → **8.3** |
| **Sources** | ConversionXL CTA Research (2024); GoodUI Pattern #41; VWO case studies |

**Why it works:** On mobile especially (+25–32% lift), users scroll through product details,
reviews, and images — losing sight of the ATC button. A persistent CTA
eliminates the friction of scrolling back up to purchase.

---

### EC-002: Product Video on PDP

| Field | Value |
|-------|-------|
| **Element** | Product media / image gallery |
| **Page** | Product Detail Page |
| **Control** | Static product images only |
| **Variant** | Short product video (15–30s) added to image gallery |
| **Avg. Lift** | +21% conversion rate; +6–30% sales per product |
| **Confidence** | High — documented across fashion, electronics, beauty verticals |
| **ICE Score** | I: 7 · C: 8 · E: 5 → **6.7** |
| **Notes** | Video must load fast; autoplay on mute performs best in gallery |
| **Sources** | Shopify Plus partner studies; Brillmark ecommerce experiments |

**Why it works:** Video provides context that static images cannot — showing
scale, movement, texture, and real-world usage. Reduces purchase uncertainty.

---

### EC-003: Social Proof Beneath ATC Button

| Field | Value |
|-------|-------|
| **Element** | Social proof / reviews |
| **Page** | Product Detail Page |
| **Control** | Reviews section placed far below fold |
| **Variant** | Star rating + review count + "X bought in last 24h" placed directly below ATC |
| **Avg. Lift** | +11–19% conversion rate for new customers |
| **Confidence** | High — TrustPilot E-commerce Trust Report (2023) |
| **ICE Score** | I: 7 · C: 8 · E: 9 → **8.0** |
| **Notes** | Most effective for stores with 50+ reviews per product |
| **Sources** | TrustPilot; Baymard Institute; GoodUI patterns |

**Why it works:** Placing social proof adjacent to the decision point (ATC)
provides reassurance at the exact moment of purchase intent, reducing
uncertainty for first-time buyers.

---

### EC-004: Urgency & Scarcity Indicators

| Field | Value |
|-------|-------|
| **Element** | Urgency messaging |
| **Page** | Product Detail Page |
| **Control** | No urgency signals |
| **Variant** | Low stock indicator ("Only 3 left") + recent purchase activity ("12 bought today") |
| **Avg. Lift** | +9–15% conversion rate |
| **Confidence** | Medium-High — works well for popular/trending products; can backfire if perceived as fake |
| **ICE Score** | I: 6 · C: 7 · E: 9 → **7.3** |
| **Notes** | Must use real data — fake scarcity damages trust. Best on products with genuine limited stock |
| **Sources** | Cialdini Scarcity Principle; multiple Shopify Plus A/B tests |

**Why it works:** Scarcity triggers loss aversion (Kahneman). When supply is
genuinely limited, communicating that accelerates purchase decisions.

---

### EC-005: Trust Badges Near ATC & Payment

| Field | Value |
|-------|-------|
| **Element** | Trust signals |
| **Page** | Product Detail Page + Checkout |
| **Control** | No visible trust badges or security indicators |
| **Variant** | Payment security icons, money-back guarantee badge, and SSL/secure checkout badge placed near ATC button |
| **Avg. Lift** | +7–12% conversion rate |
| **Confidence** | High — consistent across verticals |
| **ICE Score** | I: 6 · C: 8 · E: 9 → **7.7** |
| **Notes** | Works best for lesser-known brands; diminishing returns for established brands |
| **Sources** | Baymard Institute; VWO case studies; TrustPilot research |

**Why it works:** 18% of users abandon carts due to security concerns (Baymard).
Trust badges provide visual reassurance at the point of financial commitment.

---

### EC-006: Simplified Product Image Gallery

| Field | Value |
|-------|-------|
| **Element** | Product image gallery |
| **Page** | Product Detail Page |
| **Control** | Thumbnail grid layout or small carousel |
| **Variant** | Full-width hero image with swipe navigation, zoom-on-tap, and lifestyle context shots |
| **Avg. Lift** | +12–22% add-to-cart rate |
| **Confidence** | High — Baymard Institute product page research |
| **ICE Score** | I: 7 · C: 8 · E: 6 → **7.0** |
| **Notes** | Include at least 1 scale/context shot, 1 detail shot, 1 lifestyle shot |
| **Sources** | Baymard PDP research; Shopify Plus image optimization studies |

**Why it works:** Ecommerce's fundamental limitation is that customers cannot
physically examine products. High-quality, zoomable images with context
shots bridge this gap.

---

### EC-007: "Complete the Look" / Cross-Sell Module

| Field | Value |
|-------|-------|
| **Element** | Cross-sell / recommendations |
| **Page** | Product Detail Page |
| **Control** | Generic "You may also like" recommendations at page bottom |
| **Variant** | Curated "Complete the Look" bundle above fold showing complementary items with one-click add |
| **Avg. Lift** | +8–15% AOV; +5–12% conversion rate |
| **Confidence** | Medium-High — strongest in fashion, home, beauty |
| **ICE Score** | I: 7 · C: 7 · E: 5 → **6.3** |
| **Sources** | Amazon recommendation engine research; Dynamic Yield; Nosto personalization |

**Why it works:** Contextual bundling creates perceived value and reduces the
cognitive load of finding matching items. Amazon attributes 35% of revenue to
its recommendation engine.

---

### EC-008: Size Guide Prominence & Interactive Fit

| Field | Value |
|-------|-------|
| **Element** | Size guide / fit tool |
| **Page** | Product Detail Page (apparel) |
| **Control** | Small "Size Guide" text link that opens a static chart |
| **Variant** | Prominent "Find Your Size" button with interactive fit quiz or visual guide |
| **Avg. Lift** | +15–25% conversion rate; -20–30% return rate |
| **Confidence** | High — fit uncertainty is #1 reason for apparel cart abandonment |
| **ICE Score** | I: 8 · C: 8 · E: 4 → **6.7** |
| **Notes** | ROI multiplied by reduced returns cost |
| **Sources** | Baymard Institute apparel UX; Shopify Plus partner agencies |

**Why it works:** Sizing uncertainty is the top barrier to online apparel
purchase. Interactive fit tools convert hesitant browsers into confident buyers
and reduce costly returns.

---

## Cart & Checkout Tests

### EC-009: Simplified Single-Page Checkout

| Field | Value |
|-------|-------|
| **Element** | Checkout flow architecture |
| **Page** | Checkout |
| **Control** | Multi-step checkout (3–5 pages) |
| **Variant** | Single-page or accordion checkout with all fields visible |
| **Avg. Lift** | +17% checkout completion |
| **Confidence** | High — Baymard research shows avg. checkout has 11.3 fields but only needs 8 |
| **ICE Score** | I: 9 · C: 8 · E: 4 → **7.0** |
| **Notes** | Shopify's one-page checkout update (2023) validated this pattern at scale |
| **Sources** | Baymard Checkout UX 2024; Shopify checkout research |

**Why it works:** Each additional step is an abandonment opportunity. The average
checkout loses 18% of users specifically due to complexity (Baymard 2024).
Reducing steps reduces friction.

---

### EC-010: Guest Checkout Default

| Field | Value |
|-------|-------|
| **Element** | Account creation requirement |
| **Page** | Checkout |
| **Control** | Requiring account creation before checkout |
| **Variant** | Guest checkout as default with optional account creation post-purchase |
| **Avg. Lift** | +24–35% checkout completion for new customers |
| **Confidence** | Very High — 26% of users abandon carts when forced to create an account (Baymard) |
| **ICE Score** | I: 9 · C: 9 · E: 7 → **8.3** |
| **Sources** | Baymard Institute (2024); Shopify checkout best practices |

**Why it works:** Forced account creation is the #2 reason for cart abandonment
after unexpected costs. Removing this barrier immediately converts abandoning
users. Account creation can be offered post-purchase with one-click setup.

---

### EC-011: Express Payment Options (Digital Wallets)

| Field | Value |
|-------|-------|
| **Element** | Payment methods |
| **Page** | Cart + Checkout |
| **Control** | Credit card only |
| **Variant** | Shop Pay, Apple Pay, Google Pay, PayPal express buttons on cart and checkout |
| **Avg. Lift** | +14% conversion rate; checkout speed 4x faster |
| **Confidence** | Very High — Shopify data: Shop Pay converts 1.72x higher than standard checkout |
| **ICE Score** | I: 8 · C: 9 · E: 7 → **8.0** |
| **Sources** | Shopify Shop Pay data; PayPal checkout studies |

**Why it works:** Express payments eliminate the friction of typing billing info,
shipping address, and card numbers. Pre-authenticated wallets reduce checkout
time from minutes to seconds.

---

### EC-012: Free Shipping Threshold Bar

| Field | Value |
|-------|-------|
| **Element** | Shipping cost communication |
| **Page** | Cart / Mini-Cart |
| **Control** | Shipping cost shown only at checkout |
| **Variant** | Progress bar showing "You're $X away from free shipping!" with animated fill |
| **Avg. Lift** | +15–23% reduction in cart abandonment; +12–18% AOV increase |
| **Confidence** | High — Baymard: unexpected shipping costs are #1 reason for cart abandonment (48%) |
| **ICE Score** | I: 8 · C: 8 · E: 8 → **8.0** |
| **Sources** | Baymard Institute cart abandonment research; multiple Shopify app studies |

**Why it works:** 48% of abandonment is due to unexpected extra costs (shipping,
tax, fees). Proactively communicating the shipping threshold motivates users to
add more items rather than abandon.

---

### EC-013: Cart Abandonment Recovery Email

| Field | Value |
|-------|-------|
| **Element** | Email remarketing |
| **Page** | Post-abandonment (email) |
| **Control** | No abandonment emails |
| **Variant** | 3-email sequence: (1) 1hr reminder, (2) 24hr with social proof, (3) 48hr with incentive |
| **Avg. Lift** | +5–11% cart recovery rate; best-in-class recover 15%+ |
| **Confidence** | Very High — industry standard with massive dataset |
| **ICE Score** | I: 8 · C: 9 · E: 6 → **7.7** |
| **Notes** | First email within 1 hour recovers 2x more than 24-hour delay |
| **Sources** | Klaviyo benchmarks; Omnisend research; Shopify Email |

**Why it works:** 70% of carts are abandoned. Timed email sequences recapture
users who had genuine purchase intent but were distracted or needed more time.
The graduated incentive (reminder → proof → discount) maximizes recovery without
leading with discounts.

---

### EC-014: Checkout Progress Indicator

| Field | Value |
|-------|-------|
| **Element** | Progress UI |
| **Page** | Checkout |
| **Control** | No indication of checkout steps/progress |
| **Variant** | Visual step indicator (e.g., "Step 2 of 3: Shipping") |
| **Avg. Lift** | +8–12% checkout completion |
| **Confidence** | Medium-High — Baymard best practice |
| **ICE Score** | I: 6 · C: 7 · E: 9 → **7.3** |
| **Sources** | Baymard checkout UX guidelines; UX design research |

**Why it works:** Uncertainty about checkout length causes anxiety. Progress
indicators set expectations and provide a sense of momentum. Users who know
they're on "Step 2 of 3" are less likely to abandon than users who don't
know how many more screens they'll face.

---

### EC-015: Displaying Total Cost Early

| Field | Value |
|-------|-------|
| **Element** | Order summary / pricing |
| **Page** | Cart + Checkout |
| **Control** | Total cost (including tax and shipping) revealed only at final checkout step |
| **Variant** | Estimated total with tax and shipping shown in cart and throughout checkout |
| **Avg. Lift** | +19% reduction in checkout abandonment |
| **Confidence** | High — 48% abandon due to extra costs being too high (Baymard) |
| **ICE Score** | I: 8 · C: 8 · E: 7 → **7.7** |
| **Sources** | Baymard cart abandonment studies (2024) |

**Why it works:** Price shock at the final step is the #1 abandonment trigger.
Showing the total early sets expectations and filters out users who wouldn't
convert anyway, improving the funnel quality.

---

## Collection & Category Page Tests

### EC-016: Enhanced Product Filtering

| Field | Value |
|-------|-------|
| **Element** | Product filters / faceted navigation |
| **Page** | Collection / Category pages |
| **Control** | Basic dropdown filters (price, popularity) |
| **Variant** | Visual faceted filters with color swatches, size buttons, price slider, and active filter tags |
| **Avg. Lift** | +15–26% product discovery; +10–18% add-to-cart |
| **Confidence** | High — Baymard category navigation research |
| **ICE Score** | I: 7 · C: 7 · E: 5 → **6.3** |
| **Sources** | Baymard Institute; Algolia search & discovery data |

**Why it works:** Users who filter are 2–3x more likely to convert than
browsers. Making filters visual, fast, and intuitive reduces the effort to
find the right product.

---

### EC-017: Quick View / Quick Add on Collection

| Field | Value |
|-------|-------|
| **Element** | Product interaction on collection |
| **Page** | Collection / Category pages |
| **Control** | Clicking product card navigates to PDP |
| **Variant** | Hover/tap reveals Quick View modal with key details and ATC button |
| **Avg. Lift** | +8–15% add-to-cart rate from collection pages |
| **Confidence** | Medium — works best for stores with simple SKUs (no variant selection needed) |
| **ICE Score** | I: 6 · C: 6 · E: 5 → **5.7** |
| **Sources** | Shopify Plus UX studies; AB Tasty ecommerce case studies |

**Why it works:** Reduces the clicks-to-cart for users who have already decided.
Keeps users in the browsing flow rather than forcing them into individual PDPs
for every product they consider.

---

## Mobile Ecommerce Tests

### EC-018: Mobile-Optimized Checkout

| Field | Value |
|-------|-------|
| **Element** | Checkout UI for mobile |
| **Page** | Checkout (mobile) |
| **Control** | Desktop checkout served to mobile users |
| **Variant** | Mobile-native checkout with large touch targets, numeric keyboards for phone/zip, auto-fill, minimal fields |
| **Avg. Lift** | +22% mobile checkout conversion |
| **Confidence** | Very High — mobile CVR is typically 50–60% of desktop |
| **ICE Score** | I: 9 · C: 9 · E: 4 → **7.3** |
| **Sources** | Google mobile UX research; Baymard mobile checkout guidelines |

**Why it works:** Mobile accounts for 60–70% of ecommerce traffic but converts
at half the rate of desktop. The gap is primarily UX friction: small touch
targets, wrong keyboard types, and too many fields for thumb typing.

---

### EC-019: Thumb-Zone Optimized Mobile Navigation

| Field | Value |
|-------|-------|
| **Element** | Mobile navigation |
| **Page** | Sitewide (mobile) |
| **Control** | Top hamburger menu + top search bar |
| **Variant** | Bottom navigation bar with key actions (Home, Search, Cart, Account) in thumb zone |
| **Avg. Lift** | +10–15% engagement; +7–12% conversion |
| **Confidence** | Medium — growing pattern, especially in app-like PWAs |
| **ICE Score** | I: 7 · C: 6 · E: 5 → **6.0** |
| **Sources** | Steven Hoober thumb-zone research; mobile UX best practices |

**Why it works:** 75% of mobile interactions happen in the "thumb zone" (bottom
third of screen). Placing key navigation in this zone reduces reach effort and
increases engagement.

---

## Pricing & Offers Tests

### EC-020: Anchored Pricing with Strikethrough

| Field | Value |
|-------|-------|
| **Element** | Price display |
| **Page** | Product Detail Page + Collection |
| **Control** | Single price displayed (e.g., "$29.99") |
| **Variant** | Compare-at price with strikethrough + sale price + savings amount/percentage (e.g., "~~$49.99~~ $29.99 — Save 40%") |
| **Avg. Lift** | +10–20% conversion rate on discounted items |
| **Confidence** | High — anchoring is one of the most robust cognitive biases |
| **ICE Score** | I: 7 · C: 8 · E: 9 → **8.0** |
| **Sources** | Tversky & Kahneman anchoring research; Shopify pricing studies |

**Why it works:** Anchoring bias causes the original price to serve as a
reference point, making the sale price feel like a significantly better deal.
Showing both the savings amount and percentage maximizes perceived value.

---

### EC-021: Free Shipping vs. Percentage Discount

| Field | Value |
|-------|-------|
| **Element** | Promotional offer |
| **Page** | Sitewide / Cart |
| **Control** | 10% off site-wide discount |
| **Variant** | Free shipping on all orders |
| **Avg. Lift** | Free shipping converts 28% higher than equivalent percentage discount |
| **Confidence** | High — free shipping is perceived as higher value than equal monetary discount |
| **ICE Score** | I: 7 · C: 8 · E: 8 → **7.7** |
| **Sources** | Baymard cart abandonment data; Shopify merchant benchmarks |

**Why it works:** Shipping costs feel like a "penalty" rather than a product
cost. Removing that penalty (free shipping) provides more psychological relief
than an equivalent percentage discount, even when the dollar value is the same.

---

### EC-022: Bundle / Kit Pricing

| Field | Value |
|-------|-------|
| **Element** | Pricing structure |
| **Page** | Product Detail Page |
| **Control** | Individual product pricing |
| **Variant** | Bundled kit pricing showing per-item savings ("Buy the set: $79 — Save $31 vs. buying separately") |
| **Avg. Lift** | +12–25% AOV; +8–15% conversion rate |
| **Confidence** | Medium-High — strongest in beauty, supplements, home goods |
| **ICE Score** | I: 7 · C: 7 · E: 6 → **6.7** |
| **Sources** | Shopify Plus bundle optimization; DTC brand case studies |

**Why it works:** Bundles provide clear value framing ("save $X") while
increasing AOV. They also reduce decision fatigue by curating a recommended set.

---

## Search & Navigation Tests

### EC-023: Prominent Search Bar with Autocomplete

| Field | Value |
|-------|-------|
| **Element** | Site search |
| **Page** | Sitewide |
| **Control** | Small search icon that expands on click |
| **Variant** | Full-width search bar with predictive autocomplete, product thumbnails, and trending queries |
| **Avg. Lift** | +15–30% conversion for search users; search users convert 2–3x higher than browsers |
| **Confidence** | High — Algolia, Searchspring, and Nosto data |
| **ICE Score** | I: 8 · C: 8 · E: 5 → **7.0** |
| **Sources** | Algolia ecommerce search data; Baymard search usability studies |

**Why it works:** Users who use site search have 2–3x higher purchase intent
than browsers. Enhancing search visibility and intelligence converts this
high-intent segment more effectively.

---

### EC-024: "Recently Viewed" Persistent Widget

| Field | Value |
|-------|-------|
| **Element** | Product recommendations |
| **Page** | Sitewide |
| **Control** | No recently viewed functionality |
| **Variant** | Persistent "Recently Viewed" bar/section on PDP, collection, and cart pages |
| **Avg. Lift** | +5–10% conversion rate; +8% pages per session |
| **Confidence** | Medium-High — GoodUI Pattern #26 |
| **ICE Score** | I: 5 · C: 7 · E: 7 → **6.3** |
| **Sources** | GoodUI Pattern #26; Shopify app data |

**Why it works:** Ecommerce shoppers browse multiple products before purchasing.
A recently viewed section reduces the effort of returning to previously
considered items, supporting the natural comparison shopping behavior.

---

## Post-Purchase & Retention Tests

### EC-025: Post-Purchase Upsell Page

| Field | Value |
|-------|-------|
| **Element** | Upsell / cross-sell |
| **Page** | Post-checkout confirmation |
| **Control** | Standard order confirmation page |
| **Variant** | One-click upsell offer between checkout and confirmation ("Add X to your order for $Y — ships free with your order") |
| **Avg. Lift** | +10–15% revenue per customer; 8–12% upsell acceptance rate |
| **Confidence** | High — widely validated across Shopify stores |
| **ICE Score** | I: 7 · C: 8 · E: 6 → **7.0** |
| **Sources** | Shopify Plus post-purchase extensions; ReConvert data |

**Why it works:** The moment after purchase is the highest-trust, lowest-barrier
point in the customer journey. The buyer has already committed and doesn't need
to re-enter payment info. One-click upsells capture incremental revenue at
minimal friction.

---

## Summary: Top Quick Wins for Shopify/Ecommerce

| Rank | Test ID | Test Name | ICE | Expected Lift |
|------|---------|-----------|-----|---------------|
| 1 | EC-001 | Sticky Add-to-Cart | 8.3 | +18–32% ATC |
| 2 | EC-010 | Guest Checkout Default | 8.3 | +24–35% checkout |
| 3 | EC-003 | Social Proof Near ATC | 8.0 | +11–19% CVR |
| 4 | EC-011 | Express Payment Options | 8.0 | +14% CVR |
| 5 | EC-012 | Free Shipping Threshold Bar | 8.0 | +15–23% reduced abandonment |
| 6 | EC-020 | Anchored Pricing Display | 8.0 | +10–20% CVR |
| 7 | EC-005 | Trust Badges Near ATC | 7.7 | +7–12% CVR |
| 8 | EC-013 | Cart Abandonment Email | 7.7 | +5–11% recovery |
| 9 | EC-015 | Show Total Cost Early | 7.7 | +19% reduced abandonment |
| 10 | EC-021 | Free Shipping vs Discount | 7.7 | +28% CVR |

---

## Sources

- [Baymard Institute Checkout UX Research (2024)](https://baymard.com/research/checkout-usability)
- [Baymard Cart Abandonment Statistics](https://baymard.com/blog/ecommerce-checkout-usability-report-and-benchmark)
- [Baymard UX Statistics](https://baymard.com/learn/ux-statistics)
- [ConversionXL CRO Research](https://cxl.com/blog/)
- [GoodUI Proven Patterns](https://goodui.org/patterns/)
- [GoodUI Datastories](https://goodui.org/datastories/)
- [VWO CRO Case Studies](https://vwo.com/conversion-rate-optimization/conversion-rate-optimization-case-studies/)
- [Shopify Plus Checkout Research](https://www.shopify.com/plus)
- [TrustPilot E-commerce Trust Report (2023)](https://business.trustpilot.com/)
- [Algolia Ecommerce Search Data](https://www.algolia.com/)
- [Unbounce CRO Case Studies](https://unbounce.com/conversion-rate-optimization/cro-case-studies/)
- [Brillmark Ecommerce A/B Test Ideas](https://www.brillmark.com/ecommerce-ab-test-ideas/)
- [Martin Kairys Product Page Test Wins](https://www.hellomartin.co.uk/blog/proven-product-page-a-b-test-wins-in-ecommerce/)
- [Linear Design CRO Case Studies](https://lineardesign.com/blog/conversion-rate-optimization-case-studies/)
