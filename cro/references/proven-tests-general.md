# Proven CRO Tests: Universal & Cross-Industry

A curated database of A/B tests with documented results that apply across
industries and website types. These are foundational CRO patterns backed by
behavioral science and large-scale testing data.

**How to use this database:**
- Reference tests by ID (e.g., `GEN-001`) in audit reports and test plans.
- These tests apply broadly but should be validated for each specific context.
- Many of these are "first tests to run" for any new CRO program.
- "Avg. Lift" is the median observed effect; actual results vary by site.

---

## Page Speed & Performance Tests

### GEN-001: Page Load Speed Optimization

| Field | Value |
|-------|-------|
| **Element** | Page performance |
| **Page** | Sitewide |
| **Control** | Current page load time (typically 3–6 seconds) |
| **Variant** | Optimized to under 2 seconds (image compression, lazy loading, CDN, code minification) |
| **Avg. Lift** | +7% CVR per 1-second improvement; +15–25% for 3s → 1.5s improvement |
| **Confidence** | Very High — Google/SOASTA research across millions of sessions |
| **ICE Score** | I: 9 · C: 9 · E: 4 → **7.3** |
| **Notes** | 53% of mobile users abandon sites >3s load time. Each 100ms improvement ≈ 0.5–1% CVR lift |
| **Sources** | Google/SOASTA Speed & Conversion; Portent Site Speed Research; Akamai studies |

**Why it works:** Speed is the invisible conversion killer. Unlike design
changes where the effect varies, speed improvements have a near-universal
positive impact because they reduce abandonment before users even see your
content.

---

### GEN-002: Core Web Vitals Optimization (LCP, CLS, INP)

| Field | Value |
|-------|-------|
| **Element** | Core Web Vitals metrics |
| **Page** | Sitewide |
| **Control** | Poor CWV scores (LCP >2.5s, CLS >0.1, INP >200ms) |
| **Variant** | Good CWV scores (LCP <2.5s, CLS <0.1, INP <200ms) |
| **Avg. Lift** | +10–20% organic traffic (SEO benefit); +5–15% CVR |
| **Confidence** | High — Google ranking factor since 2021; direct correlation with UX |
| **ICE Score** | I: 8 · C: 8 · E: 4 → **6.7** |
| **Sources** | Google Core Web Vitals; Chrome User Experience Report (CrUX) |

**Why it works:** CWV directly measure user experience quality. LCP measures
perceived load speed, CLS measures visual stability (elements not jumping
around), and INP measures responsiveness. Google uses these as ranking signals,
so improvements yield both UX and SEO benefits.

---

## Copy & Messaging Tests

### GEN-003: Clarity Over Cleverness in Headlines

| Field | Value |
|-------|-------|
| **Element** | Headlines / H1 |
| **Page** | Any page |
| **Control** | Clever, branded, or abstract headline ("Unlock Your Potential" / "The Future Is Now") |
| **Variant** | Clear, specific headline that states exactly what the page offers ("Free 14-Day CRM Trial — No Credit Card Required") |
| **Avg. Lift** | +20–50% engagement/conversion |
| **Confidence** | Very High — MECLABS principle: "Clarity always wins over persuasion" |
| **ICE Score** | I: 8 · C: 9 · E: 10 → **9.0** |
| **Sources** | MECLABS Conversion Heuristic; Unbounce A/B test data; MarketingExperiments |

**Why it works:** Visitors spend 3–5 seconds deciding to stay or leave. Clever
headlines require interpretation. Clear headlines immediately communicate
relevance, reducing cognitive load and matching the visitor's search intent.

---

### GEN-004: Action-Oriented Copy (Active Voice)

| Field | Value |
|-------|-------|
| **Element** | Body copy and CTAs |
| **Page** | Sitewide |
| **Control** | Passive, institutional copy ("Solutions are provided for businesses") |
| **Variant** | Active, direct copy ("We build solutions that help you grow faster") |
| **Avg. Lift** | +10–20% engagement and conversion |
| **Confidence** | High — Flesch readability research; Nielsen Norman Group writing studies |
| **ICE Score** | I: 6 · C: 8 · E: 8 → **7.3** |
| **Sources** | Nielsen Norman Group web writing research; readability studies |

**Why it works:** Active voice is 20–30% easier to comprehend than passive
voice. On the web, where attention is scarce and scanning is the default
reading behavior, easier-to-read copy converts better.

---

### GEN-005: Loss-Framed vs. Gain-Framed Copy

| Field | Value |
|-------|-------|
| **Element** | Value proposition framing |
| **Page** | Landing page / Email |
| **Control** | Gain-framed: "Save 20 hours per month with our tool" |
| **Variant** | Loss-framed: "Stop losing 20 hours per month to manual processes" |
| **Avg. Lift** | +10–25% conversion for high-consideration decisions |
| **Confidence** | Medium-High — loss aversion (Kahneman/Tversky) is 2x stronger than equivalent gain |
| **ICE Score** | I: 6 · C: 7 · E: 10 → **7.7** |
| **Notes** | Loss framing works best for risk-averse audiences (B2B, finance, healthcare). Gain framing works better for aspirational purchases |
| **Sources** | Kahneman & Tversky Prospect Theory; CXL framing experiments |

**Why it works:** Loss aversion is one of the strongest cognitive biases —
people feel losses approximately 2x as strongly as equivalent gains. Framing
the value proposition in terms of what the user is losing by not acting
creates stronger motivation than what they'll gain.

---

### GEN-006: Power Words in Headlines

| Field | Value |
|-------|-------|
| **Element** | Headline word choice |
| **Page** | Any page |
| **Control** | Standard headline ("Our Software Solution") |
| **Variant** | Headline with power/trigger words ("Free", "Proven", "Instant", "Guaranteed", "New", "Secret", "Exclusive") |
| **Avg. Lift** | +10–30% CTR and engagement |
| **Confidence** | Medium-High — specific words depends on context and audience |
| **ICE Score** | I: 5 · C: 7 · E: 10 → **7.3** |
| **Notes** | "Free" is the most powerful word in marketing. "New" triggers novelty bias. "Proven" builds trust |
| **Sources** | David Ogilvy advertising research; Unbounce headline analyzer data |

**Why it works:** Certain words trigger emotional and psychological responses
that bypass rational evaluation. These "power words" have been tested
extensively in advertising research and consistently outperform neutral
alternatives.

---

## Layout & Visual Hierarchy Tests

### GEN-007: F-Pattern & Z-Pattern Layout Optimization

| Field | Value |
|-------|-------|
| **Element** | Visual hierarchy / content flow |
| **Page** | Any page |
| **Control** | Content layout that doesn't follow natural eye-tracking patterns |
| **Variant** | Key elements (headline, value prop, CTA) placed along the F-pattern (text-heavy pages) or Z-pattern (visual pages) |
| **Avg. Lift** | +10–20% engagement; +5–15% CTR on primary CTA |
| **Confidence** | High — Nielsen Norman Group eye-tracking studies |
| **ICE Score** | I: 6 · C: 8 · E: 6 → **6.7** |
| **Sources** | Nielsen Norman Group eye-tracking research; Crazy Egg heatmap studies |

**Why it works:** Users don't read web pages linearly — they scan in
predictable patterns. Aligning key conversion elements with natural scanning
patterns ensures they're seen, even by users who only spend a few seconds
on the page.

---

### GEN-008: Whitespace & Content Density

| Field | Value |
|-------|-------|
| **Element** | Page density and spacing |
| **Page** | Any page |
| **Control** | Dense, cluttered layout with minimal spacing |
| **Variant** | Generous whitespace around key elements, especially CTAs and headlines |
| **Avg. Lift** | +15–25% comprehension; +10–20% conversion |
| **Confidence** | High — Gestalt proximity principle; readability research |
| **ICE Score** | I: 6 · C: 7 · E: 7 → **6.7** |
| **Sources** | Gestalt design principles; UX readability research |

**Why it works:** Whitespace isn't wasted space — it's a focusing mechanism.
Generous spacing around CTAs draws attention through contrast with surrounding
content. Dense layouts cause "banner blindness" where everything blends together.

---

### GEN-009: Directional Cues Toward CTA

| Field | Value |
|-------|-------|
| **Element** | Visual direction / eye guides |
| **Page** | Landing page |
| **Control** | No visual guidance toward CTA |
| **Variant** | Directional cue pointing to CTA (arrow, person looking at CTA, visual flow line) |
| **Avg. Lift** | +8–15% CTA click-through |
| **Confidence** | Medium-High — eye-tracking studies confirm gaze follows directional cues |
| **ICE Score** | I: 5 · C: 7 · E: 8 → **6.7** |
| **Notes** | Human faces looking at CTA are most powerful; arrows are second. Avoid cheesy stock arrows |
| **Sources** | CXL directional cue experiments; eye-tracking research |

**Why it works:** We instinctively follow where other people look (social gaze)
and where arrows point. Subtle directional cues guide the visitor's eye to the
CTA without them consciously realizing they're being guided.

---

### GEN-010: Above-the-Fold CTA Placement

| Field | Value |
|-------|-------|
| **Element** | CTA placement |
| **Page** | Landing page / Homepage |
| **Control** | CTA only appears below the fold after scrolling |
| **Variant** | Primary CTA visible above the fold (within first viewport) |
| **Avg. Lift** | +15–30% conversion |
| **Confidence** | Very High — Nielsen Norman: 57% of viewing time is above the fold |
| **ICE Score** | I: 7 · C: 9 · E: 9 → **8.3** |
| **Sources** | Nielsen Norman Group scroll behavior; Chartbeat attention data |

**Why it works:** 57% of page-viewing time is spent above the fold (Nielsen
Norman). If your CTA requires scrolling, you've already lost a majority of
your audience's attention. Having a CTA visible immediately doesn't prevent
scrolling — it gives ready-to-act visitors an immediate path.

---

## Social Proof & Trust Tests

### GEN-011: Real-Time Activity Notifications

| Field | Value |
|-------|-------|
| **Element** | Social proof notification |
| **Page** | Sitewide |
| **Control** | No real-time social proof |
| **Variant** | Small toast notification: "Sarah from Austin just signed up 3 minutes ago" / "47 people are viewing this page" |
| **Avg. Lift** | +5–15% conversion |
| **Confidence** | Medium — can increase conversions but can also feel manipulative if overdone |
| **ICE Score** | I: 5 · C: 6 · E: 7 → **6.0** |
| **Notes** | Must use real data. Fake notifications damage trust. Avoid on sites where privacy is valued |
| **Sources** | Cialdini social proof principle; FOMO marketing research |

**Why it works:** Real-time activity creates the "busy restaurant" effect —
if other people are taking action, it must be worth doing. This is especially
powerful for time-sensitive offers and high-uncertainty decisions.

---

### GEN-012: Specific Numbers vs. Round Numbers

| Field | Value |
|-------|-------|
| **Element** | Statistics / social proof metrics |
| **Page** | Any page |
| **Control** | Round numbers: "Over 10,000 customers" |
| **Variant** | Specific numbers: "10,847 customers" or "Rated 4.8/5 from 2,341 reviews" |
| **Avg. Lift** | +10–18% trust and conversion |
| **Confidence** | High — specific numbers are perceived as more truthful |
| **ICE Score** | I: 5 · C: 8 · E: 10 → **7.7** |
| **Sources** | CXL precision bias research; marketing credibility studies |

**Why it works:** Specific numbers feel researched and truthful. Round numbers
feel estimated and potentially exaggerated. "10,847 customers" implies you
actually counted. "Over 10,000" implies you're rounding up from potentially
far fewer.

---

### GEN-013: Customer Logo Wall

| Field | Value |
|-------|-------|
| **Element** | Client logos |
| **Page** | Homepage / Landing page |
| **Control** | No visible client logos |
| **Variant** | Horizontal logo strip of 5–8 recognizable brand logos with "Trusted by" header |
| **Avg. Lift** | +10–20% conversion for B2B; +5–10% for B2C |
| **Confidence** | High — one of the simplest and most consistently winning tests |
| **ICE Score** | I: 6 · C: 8 · E: 10 → **8.0** |
| **Sources** | CXL social proof research; B2B landing page best practices |

**Why it works:** Logo walls provide instant authority through association.
If recognized brands use the product, it's implicitly safe and reliable.
This is especially powerful for unknown brands — "If Google uses it, it
must be legitimate."

---

## Mobile Optimization Tests

### GEN-014: Mobile-First Layout Redesign

| Field | Value |
|-------|-------|
| **Element** | Responsive design approach |
| **Page** | Sitewide |
| **Control** | Desktop-first design adapted to mobile |
| **Variant** | Mobile-first design with content prioritized for small screens, large touch targets (min 44px), and simplified layouts |
| **Avg. Lift** | +15–30% mobile conversion rate |
| **Confidence** | Very High — mobile traffic is 60%+ for most sites but converts at 50% of desktop |
| **ICE Score** | I: 9 · C: 9 · E: 3 → **7.0** |
| **Sources** | Google mobile UX guidelines; Contentsquare digital experience benchmark |

**Why it works:** The mobile conversion gap (50–60% lower than desktop) is the
single largest CRO opportunity for most sites. It's caused by touch target
size, content prioritization, form friction, and load speed — all addressable
through mobile-first design.

---

### GEN-015: Click-to-Call Button (Mobile)

| Field | Value |
|-------|-------|
| **Element** | Mobile contact method |
| **Page** | Contact / Service pages (mobile) |
| **Control** | Phone number as text |
| **Variant** | Prominent click-to-call button with phone icon |
| **Avg. Lift** | +20–40% mobile call rate for service businesses |
| **Confidence** | High — especially impactful for local service, healthcare, legal |
| **ICE Score** | I: 7 · C: 8 · E: 9 → **8.0** |
| **Sources** | Google mobile usability research; local business CRO studies |

**Why it works:** On mobile, calling is the lowest-friction conversion action.
Tapping a button is far easier than copying a phone number and switching to the
dialer. For service businesses where a call IS the conversion, this removes
unnecessary friction.

---

## Navigation & Information Architecture Tests

### GEN-016: Sticky Navigation Bar

| Field | Value |
|-------|-------|
| **Element** | Navigation behavior |
| **Page** | Sitewide |
| **Control** | Navigation scrolls away with page content |
| **Variant** | Sticky/fixed navigation that stays visible on scroll (condensed on scroll) |
| **Avg. Lift** | +8–15% engagement; +5–10% navigation usage |
| **Confidence** | Medium-High — depends on page length and content type |
| **ICE Score** | I: 5 · C: 7 · E: 7 → **6.3** |
| **Sources** | Smashing Magazine UX research; NNG navigation studies |

**Why it works:** Sticky navigation keeps key actions accessible regardless of
scroll position. This is most valuable on long pages where users might want
to navigate after reading content deep in the page.

---

### GEN-017: Simplified Top Navigation (Fewer Items)

| Field | Value |
|-------|-------|
| **Element** | Navigation structure |
| **Page** | Sitewide |
| **Control** | Navigation with 8+ top-level items |
| **Variant** | Simplified navigation with 5–6 items focused on key conversion paths |
| **Avg. Lift** | +10–15% conversion on key pages |
| **Confidence** | Medium-High — Hick's Law (more choices = longer decision time = more abandonment) |
| **ICE Score** | I: 6 · C: 7 · E: 6 → **6.3** |
| **Sources** | Hick's Law research; NNG information architecture studies |

**Why it works:** Every navigation item is a choice. More choices = more
cognitive load = slower decisions. Reducing navigation items focuses users
on the most valuable paths and reduces the paradox of choice.

---

## Email & Lead Capture Tests

### GEN-018: Timed Popup vs. Immediate Popup

| Field | Value |
|-------|-------|
| **Element** | Email capture popup |
| **Page** | Sitewide |
| **Control** | Popup appears immediately on page load |
| **Variant** | Popup appears after 30–60 seconds or after 50% scroll depth |
| **Avg. Lift** | +20–50% popup conversion rate (fewer impressions but higher quality) |
| **Confidence** | High — immediate popups have high dismiss rates and increase bounce |
| **ICE Score** | I: 6 · C: 8 · E: 8 → **7.3** |
| **Sources** | OptinMonster timing data; Sumo popup benchmarks |

**Why it works:** Immediate popups interrupt before the visitor has engaged with
content, triggering reflexive dismissal. Delayed popups appear when the visitor
is already engaged (proven by scroll depth or time on page), making the offer
more relevant and the interruption less jarring.

---

### GEN-019: Slide-In vs. Full-Screen Popup

| Field | Value |
|-------|-------|
| **Element** | Email capture format |
| **Page** | Blog / Content pages |
| **Control** | Full-screen modal popup |
| **Variant** | Subtle slide-in from bottom-right corner |
| **Avg. Lift** | Slide-in: –15% raw submissions but +25% user satisfaction and –30% bounce rate |
| **Confidence** | Medium — trade-off between aggressiveness and user experience |
| **ICE Score** | I: 5 · C: 7 · E: 8 → **6.7** |
| **Notes** | Full-screen popups capture more emails but damage brand perception and increase bounce |
| **Sources** | Nielsen Norman Group popup research; Sumo format comparison |

**Why it works:** The trade-off depends on strategy. Full-screen popups force
engagement (higher capture but higher bounce). Slide-ins respect the browsing
experience (lower capture but better brand perception and lower bounce).
For most B2B sites, the slide-in provides better long-term value.

---

### GEN-020: Content Upgrade vs. Generic Lead Magnet

| Field | Value |
|-------|-------|
| **Element** | Lead magnet specificity |
| **Page** | Blog / Content pages |
| **Control** | Generic lead magnet ("Subscribe to our newsletter") |
| **Variant** | Content-specific upgrade ("Download the checklist for this article" / "Get the template mentioned above") |
| **Avg. Lift** | +50–200% opt-in rate |
| **Confidence** | High — specificity and relevance drive conversion |
| **ICE Score** | I: 7 · C: 8 · E: 6 → **7.0** |
| **Sources** | Backlinko content upgrade research; HubSpot gated content data |

**Why it works:** Generic "subscribe" offers lack specificity and perceived
value. Content upgrades are directly relevant to what the visitor is already
reading, making the offer irresistible — they're already interested in the
topic and the upgrade provides additional depth.

---

## Accessibility & Inclusivity Tests

### GEN-021: Color Contrast Improvement for CTAs

| Field | Value |
|-------|-------|
| **Element** | CTA accessibility |
| **Page** | Sitewide |
| **Control** | CTAs that fail WCAG AA contrast ratio (< 4.5:1) |
| **Variant** | CTAs meeting WCAG AA (4.5:1) or AAA (7:1) contrast ratio |
| **Avg. Lift** | +5–15% CTA click rate; improved accessibility for 15% of population with visual impairment |
| **Confidence** | High — serves both accessibility and conversion goals |
| **ICE Score** | I: 5 · C: 8 · E: 8 → **7.0** |
| **Sources** | WCAG 2.1 guidelines; CXL button contrast research |

**Why it works:** Low contrast doesn't just hurt disabled users — it affects
everyone in suboptimal conditions (bright sunlight, older screens, tired eyes).
Higher contrast CTAs are easier to notice and read for ALL users.

---

### GEN-022: Readable Font Size (16px Minimum)

| Field | Value |
|-------|-------|
| **Element** | Typography |
| **Page** | Sitewide |
| **Control** | Small body text (12–14px) |
| **Variant** | Larger body text (16–18px) with appropriate line height (1.5–1.6) |
| **Avg. Lift** | +10–15% readability and engagement; reduced bounce rate |
| **Confidence** | High — 16px is the recommended minimum for web readability |
| **ICE Score** | I: 5 · C: 8 · E: 9 → **7.3** |
| **Sources** | Smashing Magazine typography research; NNG readability guidelines |

**Why it works:** Small text creates friction — it's harder to read, causes
eye strain, and is even worse on mobile. 16px is the default browser font
size for a reason: it's the minimum comfortable reading size for most adults.

---

## Testing & Experimentation Meta-Tests

### GEN-023: Radical Redesign vs. Incremental Iteration

| Field | Value |
|-------|-------|
| **Element** | Testing strategy |
| **Page** | Any page |
| **Control** | Small iterative changes (button color, copy tweaks) |
| **Variant** | Bold redesigns with structural changes (new layout, new information hierarchy) |
| **Avg. Lift** | Redesigns: +18–40%; Iterations: +2–8% |
| **Confidence** | High — especially for sites with <50K monthly visitors |
| **ICE Score** | I: 9 · C: 7 · E: 3 → **6.3** |
| **Notes** | Low-traffic sites should focus on radical tests (detectable at smaller sample sizes) |
| **Sources** | CXL testing strategy research; VWO case study data |

**Why it works:** Small changes produce small effects that require huge sample
sizes to detect. Radical redesigns produce larger effects that are detectable
with smaller samples. For most sites, one big redesign test provides more
learning than ten micro-optimizations.

---

### GEN-024: Personalization by Traffic Source

| Field | Value |
|-------|-------|
| **Element** | Dynamic content |
| **Page** | Landing page |
| **Control** | Same page for all traffic sources |
| **Variant** | Personalized messaging matching the referral source (ad copy → landing page copy alignment) |
| **Avg. Lift** | +25–50% conversion from paid traffic |
| **Confidence** | High — message match is foundational to CRO |
| **ICE Score** | I: 8 · C: 8 · E: 5 → **7.0** |
| **Sources** | Unbounce message match data; Google Quality Score research |

**Why it works:** Visitors from different sources have different intents and
expectations. A visitor from a "cheap CRM" ad expects to see pricing front and
center. A visitor from a "best CRM features" ad expects feature comparisons.
Matching the landing page to the source message maintains continuity and
relevance.

---

### GEN-025: A/B Testing a "Control" Against Itself (AA Test)

| Field | Value |
|-------|-------|
| **Element** | Testing infrastructure |
| **Page** | Any page |
| **Control** | Original page |
| **Variant** | Exact same page (AA test) |
| **Avg. Lift** | 0% expected (validates testing setup) |
| **Confidence** | N/A — this is a calibration test |
| **ICE Score** | I: 3 · C: 10 · E: 10 → **7.7** |
| **Notes** | Run this before your first real test to validate even traffic splitting, proper tracking, and statistical validity |
| **Sources** | CXL testing methodology; Optimizely best practices |

**Why it works:** An AA test ensures your testing infrastructure works correctly
before you invest in actual experiments. If an AA test shows a "significant"
difference, your setup has a problem (uneven splitting, tracking errors,
or implementation bugs) that would invalidate all future test results.

---

## Summary: Top Quick Wins — Universal Tests

| Rank | Test ID | Test Name | ICE | Expected Lift |
|------|---------|-----------|-----|---------------|
| 1 | GEN-003 | Clarity Over Cleverness | 9.0 | +20–50% CVR |
| 2 | GEN-010 | Above-the-Fold CTA | 8.3 | +15–30% CVR |
| 3 | GEN-013 | Customer Logo Wall | 8.0 | +10–20% CVR |
| 4 | GEN-015 | Click-to-Call (Mobile) | 8.0 | +20–40% calls |
| 5 | GEN-005 | Loss-Framed Copy | 7.7 | +10–25% CVR |
| 6 | GEN-012 | Specific Numbers | 7.7 | +10–18% trust |
| 7 | GEN-025 | AA Test (Calibration) | 7.7 | Infrastructure validation |
| 8 | GEN-001 | Page Speed Optimization | 7.3 | +7% per second |
| 9 | GEN-004 | Active Voice Copy | 7.3 | +10–20% engagement |
| 10 | GEN-018 | Timed vs Immediate Popup | 7.3 | +20–50% popup CVR |

---

## Cross-Reference: Tests by Psychology Principle

| Principle | Related Tests |
|-----------|---------------|
| **Loss Aversion** (Kahneman) | GEN-005, EC-004, EC-012 |
| **Social Proof** (Cialdini) | GEN-011, GEN-012, GEN-013, B2B-003, B2B-016, EC-003 |
| **Scarcity** (Cialdini) | EC-004 |
| **Anchoring** (Tversky) | EC-020, B2B-014 |
| **Commitment/Consistency** (Cialdini) | B2B-007 |
| **Authority** (Cialdini) | B2B-017, GEN-013 |
| **Default Effect** | B2B-013, B2B-015 |
| **Hick's Law** (Choice Paradox) | B2B-002, GEN-017 |
| **Von Restorff Effect** (Isolation) | B2B-011, B2B-013 |
| **Cognitive Load Theory** | GEN-003, GEN-008, B2B-006 |
| **Endowment Effect** | EC-025 |
| **Reciprocity** (Cialdini) | GEN-020 |
| **Risk Aversion** | B2B-012, B2B-018, EC-005, EC-010 |

---

## Cross-Reference: Tests by Page Type

| Page Type | Recommended Tests |
|-----------|-------------------|
| **Homepage** | GEN-003, GEN-010, GEN-013, B2B-001, B2B-003 |
| **Product Page** | EC-001 through EC-008, EC-020, EC-022 |
| **Collection/Category** | EC-016, EC-017, EC-023 |
| **Cart** | EC-012, EC-015, EC-011 |
| **Checkout** | EC-009, EC-010, EC-011, EC-014, EC-015, EC-018 |
| **Landing Page (B2B)** | B2B-001 through B2B-012, B2B-019 through B2B-021 |
| **Pricing Page** | B2B-013, B2B-014, B2B-015, B2B-018 |
| **Blog/Content** | GEN-018, GEN-019, GEN-020 |
| **Contact Page** | B2B-006 through B2B-009, GEN-015 |
| **Post-Purchase** | EC-025, EC-013 |

---

## Sources

- [Google/SOASTA Speed & Conversion Research](https://web.dev/performance/)
- [MECLABS Conversion Heuristic](https://meclabs.com/)
- [Nielsen Norman Group Web UX Research](https://www.nngroup.com/)
- [CXL Institute CRO Research](https://cxl.com/blog/)
- [Unbounce Conversion Benchmark Report](https://unbounce.com/conversion-rate-optimization/cro-case-studies/)
- [GoodUI Proven Patterns](https://goodui.org/patterns/)
- [VWO CRO Case Studies](https://vwo.com/conversion-rate-optimization/conversion-rate-optimization-case-studies/)
- [Contentsquare Digital Experience Benchmark](https://contentsquare.com/)
- [Kahneman & Tversky — Prospect Theory](https://en.wikipedia.org/wiki/Prospect_theory)
- [Cialdini — Influence: The Psychology of Persuasion](https://www.influenceatwork.com/)
- [Baymard Institute UX Statistics](https://baymard.com/learn/ux-statistics)
- [OptinMonster Popup Benchmarks](https://optinmonster.com/)
- [Crazy Egg Heatmap Studies](https://www.crazyegg.com/)
- [WCAG 2.1 Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [MarketingExperiments / MECLABS Studies](https://marketingexperiments.com/)
- [Envive Conversion Lift Statistics (2026)](https://www.envive.ai/post/online-shopping-conversion-lift-statistics)
- [Marketing LTB CRO Statistics (2025)](https://marketingltb.com/blog/statistics/conversion-rate-optimization-cro-statistics/)
