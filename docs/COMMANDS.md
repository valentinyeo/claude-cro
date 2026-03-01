# Command Reference

Complete reference for all 12 `/cro` commands. Each command can be run
independently from Claude Code.

---

## `/cro audit <url>`

**Full website conversion audit with parallel agents.**

Performs a comprehensive CRO analysis using 6 parallel subagents. This is the
most thorough analysis available and produces a scored report with findings
across all CRO categories.

**Syntax:**
```
/cro audit <url>
```

**What it analyzes:**
- UX heuristics and navigation
- Conversion copywriting effectiveness
- Analytics and tracking setup
- Visual hierarchy and layout
- Page speed and performance
- Trust signals and social proof

**Output files:**
- `FULL-AUDIT.md` — Complete audit report with CRO Health Score

**Example:**
```
/cro audit https://www.acme.com
```

---

## `/cro page <url>`

**Single page conversion deep-dive.**

Performs an in-depth analysis of a single page covering above-the-fold content,
value proposition, CTAs, trust signals, copy, forms, speed, and mobile
experience. Produces a Page CRO Score.

**Syntax:**
```
/cro page <url>
```

**What it analyzes:**
- Above-the-fold effectiveness
- Value proposition clarity and specificity
- CTA visibility, text, and placement
- Trust signals (testimonials, badges, logos)
- Content readability and persuasion
- Form design and friction
- Page speed indicators
- Mobile responsiveness

**Output files:**
- Page analysis report with section-by-section scoring

**Example:**
```
/cro page https://www.acme.com/pricing
```

---

## `/cro funnel <url1> <url2> [url3...]`

**Multi-step funnel mapping and drop-off analysis.**

Maps a conversion funnel from entry to conversion, analyzing each step and
the transitions between them. Identifies drop-off risks, navigation leaks,
consistency issues, and missing micro-conversions.

**Syntax:**
```
/cro funnel <url1> <url2> [url3] [url4] ...
```

**What it analyzes:**
- Step-by-step clarity and purpose
- CTA effectiveness at each transition
- Navigation leaks (links pulling users out of the funnel)
- Friction points per step
- Cross-step consistency (visual, messaging, pricing)
- Mobile funnel experience
- Recovery mechanisms (cart abandonment, exit intent)
- Micro-conversion opportunities

**Output files:**
- Funnel analysis report with visual funnel map and per-step scores

**Example:**
```
/cro funnel https://shop.com https://shop.com/product/123 https://shop.com/cart https://shop.com/checkout
```

---

## `/cro test <url>`

**A/B test hypothesis generation.**

Analyzes the page and generates prioritized A/B test hypotheses using the
ICE framework (Impact, Confidence, Ease). Each hypothesis follows a
structured format with evidence-based reasoning.

**Syntax:**
```
/cro test <url>
```

**What it analyzes:**
- Current page elements for optimization opportunities
- Highest-impact change areas
- Testing feasibility and sample size requirements
- Industry benchmarks for expected lift

**Output files:**
- Test plan with ICE-scored hypotheses and documentation templates

**Example:**
```
/cro test https://www.acme.com/signup
```

---

## `/cro copy <url>`

**Conversion copywriting analysis.**

Deep evaluation of every copy element on the page: headlines, subheadlines,
value proposition, CTAs, social proof text, urgency elements, readability,
emotional triggers, micro-copy, and power words.

**Syntax:**
```
/cro copy <url>
```

**What it analyzes:**
- Headline formula and effectiveness
- Subheadline support
- Value proposition messaging
- Benefit-to-feature ratio
- CTA text quality
- Social proof copy specificity
- Urgency and scarcity language (with ethical assessment)
- Readability metrics (Flesch-Kincaid)
- Emotional trigger activation
- Micro-copy quality
- Power word usage and distribution

**Output files:**
- Copy analysis report with rewrite suggestions and emotional trigger map

**Example:**
```
/cro copy https://www.acme.com/landing-page
```

---

## `/cro ux <url>`

**UX heuristic evaluation.**

Evaluates the page against Nielsen's 10 usability heuristics with a
conversion-focused lens. Includes mobile UX assessment, cognitive load
analysis, navigation evaluation, and form UX review.

**Syntax:**
```
/cro ux <url>
```

**What it analyzes:**
- Nielsen's 10 usability heuristics (conversion-focused)
- Mobile UX (thumb zones, tap targets, responsive behavior)
- Navigation and conversion path clarity
- Cognitive load (Hick's Law, Miller's Law, progressive disclosure)
- Form UX (labels, validation, error handling)
- Severity ratings (0-4 scale)

**Output files:**
- UX evaluation report with issue table and severity ratings

**Example:**
```
/cro ux https://www.acme.com
```

---

## `/cro forms <url>`

**Form optimization analysis.**

Detailed analysis of all forms on the page: field count, labels, validation,
friction level, mobile input types, privacy assurance, submit button text,
and multi-step form assessment.

**Syntax:**
```
/cro forms <url>
```

**What it analyzes:**
- Field count vs. recommended maximums
- Label placement and clarity
- Inline validation presence
- Required vs. optional fields
- HTML5 input types for mobile
- Privacy statements near forms
- Submit button text specificity
- Multi-step form structure and progress indicators

**Output files:**
- Form optimization report with per-form scoring

**Example:**
```
/cro forms https://www.acme.com/contact
```

---

## `/cro ecommerce <url>`

**E-commerce CRO analysis.**

Specialized analysis for e-commerce pages: product detail pages (PDP),
category pages, cart, and checkout. Evaluates product presentation,
pricing display, urgency elements, cross-sell/upsell, and purchase friction.

**Syntax:**
```
/cro ecommerce <url>
```

**What it analyzes:**
- Product presentation (images, descriptions, variants)
- Price display and anchoring
- Add-to-cart button prominence
- Urgency and scarcity indicators
- Cross-sell and upsell placement
- Shipping and return information visibility
- Cart and checkout friction
- Payment method options
- Mobile shopping experience

**Output files:**
- E-commerce CRO report with product page and checkout scoring

**Example:**
```
/cro ecommerce https://shop.com/products/example-product
```

---

## `/cro trust <url>`

**Trust signals and social proof audit.**

Comprehensive evaluation of all trust-building elements: testimonials,
reviews, client logos, security badges, guarantees, contact information,
and overall credibility.

**Syntax:**
```
/cro trust <url>
```

**What it analyzes:**
- Testimonial quality (specificity, attribution, relevance)
- Review widgets and third-party validation
- Client/partner logos (recognizability, display)
- Security and compliance badges
- Guarantee language and positioning
- Contact information visibility
- Authority signals (certifications, awards, press)
- Social proof patterns and data points
- Dark pattern detection (fake urgency, fabricated reviews)

**Output files:**
- Trust audit report with signal inventory and recommendations

**Example:**
```
/cro trust https://www.acme.com
```

---

## `/cro tracking <url>`

**Analytics and tracking setup validation.**

Validates that analytics tools are properly installed and configured for
conversion measurement. Checks for GA4, GTM, Meta Pixel, and other
tracking platforms.

**Syntax:**
```
/cro tracking <url>
```

**What it analyzes:**
- Google Analytics 4 (GA4) installation
- Google Tag Manager (GTM) setup
- Meta/Facebook Pixel
- LinkedIn Insight Tag
- Other third-party tracking (TikTok, Pinterest, Hotjar, etc.)
- Data layer presence and structure
- Consent management platform
- Conversion event configuration
- Noscript fallbacks

**Output files:**
- Tracking validation report with platform checklist

**Example:**
```
/cro tracking https://www.acme.com
```

---

## `/cro benchmark <url> <competitor-url>`

**Competitor conversion comparison.**

Side-by-side CRO comparison between two websites. Analyzes both pages
using the same criteria and highlights where each site excels or falls
behind.

**Syntax:**
```
/cro benchmark <url> <competitor-url>
```

**What it analyzes:**
- Head-to-head CRO element comparison
- Value proposition differentiation
- CTA effectiveness comparison
- Trust signal strength comparison
- Form friction comparison
- Mobile experience comparison
- Content and copy quality comparison
- Competitive advantages and gaps

**Output files:**
- Competitive benchmark report with comparison tables

**Example:**
```
/cro benchmark https://www.acme.com https://www.competitor.com
```

---

## `/cro plan <url>`

**CRO strategy and 90-day roadmap.**

Generates a prioritized CRO strategy with a 90-day implementation roadmap.
Combines findings from a quick audit with business context to produce
actionable phases.

**Syntax:**
```
/cro plan <url>
```

**What it analyzes:**
- Current conversion optimization state
- Quick-win opportunities (Week 1-2)
- High-impact changes (Month 1)
- Strategic improvements (Month 2-3)
- Testing roadmap and velocity targets
- Resource requirements
- KPI targets by phase

**Output files:**
- `ACTION-PLAN.md` — Phased CRO roadmap with prioritized actions

**Example:**
```
/cro plan https://www.acme.com
```
