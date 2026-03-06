# CRO Quality Gates

Minimum requirements and pass/fail thresholds for conversion-optimized pages.
Use these gates as a checklist during audits to quickly identify critical gaps.
A page that fails any "Critical" gate has a fundamental conversion issue.

---

## CTA Requirements

### Placement

| Requirement | Gate Level | Pass Criteria |
|-------------|-----------|---------------|
| CTA above the fold | Critical | At least 1 primary CTA visible without scrolling on both desktop and mobile |
| CTA after key content sections | High | CTA appears after value prop, after social proof, and at page end |
| CTA on long pages | High | Sticky CTA bar or repeated CTAs every 2-3 scroll depths |
| No competing CTAs | Medium | Only 1 primary CTA per viewport; secondary CTAs visually subordinate |

### Design

| Requirement | Gate Level | Pass Criteria |
|-------------|-----------|---------------|
| CTA contrast ratio | Critical | >= 3:1 against background; visually the most prominent element on screen |
| CTA size | High | Minimum 44px height on mobile; large enough to be immediately noticeable |
| CTA whitespace | High | Sufficient padding around CTA; not crowded by other elements |
| CTA visual weight | Medium | Filled/solid button (not ghost/outline) for primary CTA |

### Copy

| Requirement | Gate Level | Pass Criteria |
|-------------|-----------|---------------|
| Action-oriented text | Critical | Starts with a verb; tells user what happens next ("Start Free Trial", "Get My Quote") |
| Specific and clear | High | User knows exactly what will happen when they click |
| No generic text | High | Avoid "Submit", "Click Here", "Learn More" for primary conversion CTAs |
| Value-focused | Medium | Communicates benefit, not just action ("Get Started Free" vs "Sign Up") |

---

## Page Speed Thresholds

### Load Time vs. Conversion Impact

| Load Time | Gate Level | Expected Impact |
|-----------|-----------|-----------------|
| 0-2 seconds | Pass (Optimal) | Baseline conversion rate; no speed-related friction |
| 2-3 seconds | Warning (Acceptable) | ~7% conversion drop per additional second |
| 3-5 seconds | Fail (Concerning) | 15-25% conversion drop; noticeable user frustration |
| 5+ seconds | Critical Fail | 53% of mobile users will abandon; severe conversion loss |

### Core Web Vitals Thresholds

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| **LCP (Largest Contentful Paint)** | <= 2.5s | 2.5-4.0s | > 4.0s |
| **FID (First Input Delay)** | <= 100ms | 100-300ms | > 300ms |
| **INP (Interaction to Next Paint)** | <= 200ms | 200-500ms | > 500ms |
| **CLS (Cumulative Layout Shift)** | <= 0.1 | 0.1-0.25 | > 0.25 |
| **TTFB (Time to First Byte)** | <= 800ms | 800-1800ms | > 1800ms |

### Performance Gate Levels

| Metric | Critical | High | Medium |
|--------|----------|------|--------|
| LCP > 4.0s | X | | |
| LCP 2.5-4.0s | | X | |
| CLS > 0.25 | X (layout shifts destroy trust) | | |
| CLS 0.1-0.25 | | X | |
| FID/INP > 300ms | | X (unresponsive interactions) | |
| TTFB > 1800ms | | X (server issues) | |
| Render-blocking resources > 3 | | | X |
| Unoptimized images (>500KB) | | X | |

---

## Trust Signal Minimums

### E-commerce

| Requirement | Gate Level | Pass Criteria |
|-------------|-----------|---------------|
| Customer reviews/ratings | Critical | Visible on product pages; minimum star rating display |
| Security badges on checkout | Critical | SSL indicator, payment security badge (Norton, McAfee, or equivalent) |
| Return/refund policy | Critical | Clearly stated, accessible from product and cart pages |
| Payment method logos | High | Recognized payment icons visible (Visa, MC, PayPal, etc.) |
| Contact information | High | Phone, email, or chat accessible from checkout |
| Shipping information | High | Costs and delivery timeline visible before checkout |
| Privacy policy | High | Linked from forms and checkout |
| Physical address | Medium | Footer or contact page |
| Customer photos/UGC | Medium | Real customer images alongside products |
| Money-back guarantee | Medium | Explicit guarantee with duration |

### SaaS

| Requirement | Gate Level | Pass Criteria |
|-------------|-----------|---------------|
| Customer testimonials | Critical | Named individuals with company and role |
| Client logos | High | Recognizable brands in the target market |
| Security/compliance badges | High | SOC 2, GDPR, ISO, HIPAA (relevant to industry) |
| Uptime/performance guarantees | High | SLA or uptime percentage stated |
| Free trial or demo | High | Low-risk entry point available |
| Case studies with metrics | Medium | Specific results (percentages, revenue, time saved) |
| Integration partners | Medium | Logos of integrated platforms |
| Team/company page | Medium | Real people, real office, company story |
| Pricing transparency | Medium | Clear pricing without "contact us" (unless enterprise) |

### Lead Generation

| Requirement | Gate Level | Pass Criteria |
|-------------|-----------|---------------|
| Phone number | Critical | Visible, clickable (tel: link on mobile) |
| Physical address | High | Full address, ideally with map |
| Privacy policy near forms | High | Link adjacent to submit button |
| Response time expectation | High | "We'll respond within 24 hours" or similar |
| Professional credentials | Medium | Licenses, certifications, awards |
| Testimonials | Medium | Relevant social proof near the form |
| Business hours | Medium | When customers can expect a response |
| Team photos | Low | Humanizes the business |

---

## Form Limits by Type

### Maximum Field Count

| Form Type | Optimal Fields | Maximum Fields | Gate Level at Max |
|-----------|---------------|----------------|-------------------|
| **Newsletter signup** | 1 (email only) | 2 (email + name) | Critical if > 2 |
| **Content download** | 2-3 | 4 | High if > 4 |
| **Lead generation** | 3-5 | 7 | High if > 7 |
| **Contact form** | 3-4 | 6 | High if > 6 |
| **Demo request** | 4-5 | 7 | Medium if > 7 |
| **Free trial signup** | 2-3 | 5 | High if > 5 |
| **Checkout (guest)** | 8-10 | 12 | High if > 12 |
| **Account registration** | 3-4 | 5 | High if > 5 |
| **Job application** | 5-8 | 15 | Medium if > 15 |

### Form Gate Checks

| Requirement | Gate Level | Pass Criteria |
|-------------|-----------|---------------|
| Guest checkout option | Critical | Available for e-commerce sites |
| Social login option | High | At least one social/SSO option for registration |
| Inline validation | High | Errors shown at field level, not just on submit |
| Required field indicators | High | Clear marking of required vs. optional fields |
| Appropriate input types | Medium | Email, tel, number fields use correct HTML types |
| Autofill support | Medium | Autocomplete attributes on name, email, address, card |
| Error recovery | High | Form data preserved after validation errors |
| Mobile keyboard | Medium | Numeric keyboard for phone/zip, email keyboard for email |
| Submit button text | High | Action-oriented, not "Submit" |
| CAPTCHA minimized | Medium | Invisible reCAPTCHA or hCaptcha preferred; no puzzle CAPTCHAs |

---

## Content Requirements

### Above the Fold

| Requirement | Gate Level | Pass Criteria |
|-------------|-----------|---------------|
| Clear value proposition | Critical | Visitor understands what you do and why it matters within 5 seconds |
| Primary CTA | Critical | Visible without scrolling |
| Relevant hero image/visual | High | Supports the value prop; not generic stock photo |
| Navigation | High | Clean, scannable, key pages accessible |
| Social proof element | Medium | At least one trust signal visible (logos, rating, count) |

### Value Proposition Quality

| Requirement | Gate Level | Pass Criteria |
|-------------|-----------|---------------|
| Specific and clear | Critical | No jargon; a stranger can understand it |
| Benefit-focused | High | Leads with outcomes, not features |
| Differentiated | High | Clear reason to choose this over alternatives |
| Quantified where possible | Medium | Specific numbers ("Save 10 hours/week" not "Save time") |
| Audience-targeted | Medium | Speaks to a specific persona, not everyone |

### Content Principles

| Principle | Gate Level | Pass Criteria |
|-----------|-----------|---------------|
| Benefits before features | High | Outcome-first, then how it works |
| Specific numbers over vague claims | High | "10,000+ customers" not "many customers" |
| Scannable formatting | High | Headers, bullet points, short paragraphs |
| Clear hierarchy | Medium | Most important information most prominent |
| Consistent voice | Medium | Tone matches brand and audience |
| No walls of text | Medium | Paragraphs under 3-4 lines; use visual breaks |

---

## Mobile-First Checks

| Requirement | Gate Level | Pass Criteria |
|-------------|-----------|---------------|
| Tap targets >= 44px | Critical | All buttons, links, and form inputs meet minimum size |
| No horizontal scroll | Critical | Content fits within viewport width on all screen sizes |
| Form inputs use correct types | High | `type="email"`, `type="tel"`, `type="number"` where appropriate |
| Sticky CTA on long pages | High | CTA accessible without scrolling back to top |
| Readable without zoom | Critical | Text size >= 16px for body; no pinch-to-read needed |
| Images responsive | High | Properly sized, not desktop images scaled down |
| Click-to-call | High | Phone numbers are tappable `tel:` links |
| Mobile menu functional | Critical | Navigation accessible and usable on small screens |
| Keyboard doesn't break layout | High | Form inputs don't cause layout shift when keyboard opens |
| Pop-ups dismissable | Critical | Modal close button easily tappable; no pop-ups covering full screen without close |
| Video playback | Medium | Works without Flash; controls accessible |
| Touch gestures | Medium | Swipe, pinch-zoom work where expected |

---

## Warning Thresholds

Analytics-based thresholds that indicate conversion problems when data is
available.

### Traffic Metrics

| Metric | Normal | Warning | Critical |
|--------|--------|---------|----------|
| **Bounce rate (landing page)** | < 50% | 50-70% | > 70% |
| **Bounce rate (blog/content)** | < 65% | 65-80% | > 80% |
| **Bounce rate (homepage)** | < 40% | 40-60% | > 60% |
| **Exit rate (checkout page)** | < 30% | 30-50% | > 50% |
| **Pages per session** | > 3 | 2-3 | < 2 |
| **Avg. session duration** | > 2 min | 1-2 min | < 1 min |

### E-commerce Metrics

| Metric | Normal | Warning | Critical |
|--------|--------|---------|----------|
| **Cart abandonment rate** | < 65% | 65-80% | > 80% |
| **Checkout abandonment** | < 25% | 25-40% | > 40% |
| **Add-to-cart rate** | > 8% | 5-8% | < 5% |
| **Product page bounce** | < 40% | 40-55% | > 55% |
| **Search refinement rate** | < 20% | 20-35% | > 35% |
| **Zero-results rate** | < 5% | 5-10% | > 10% |

### Form Metrics

| Metric | Normal | Warning | Critical |
|--------|--------|---------|----------|
| **Form abandonment rate** | < 40% | 40-60% | > 60% |
| **Field drop-off (any single field)** | < 10% | 10-20% | > 20% |
| **Error rate (form submission)** | < 5% | 5-15% | > 15% |
| **Time to complete** | < 2 min | 2-5 min | > 5 min |

### SaaS Metrics

| Metric | Normal | Warning | Critical |
|--------|--------|---------|----------|
| **Trial signup rate** | > 3% | 1-3% | < 1% |
| **Trial-to-paid conversion** | > 15% | 8-15% | < 8% |
| **Demo request rate** | > 2% | 1-2% | < 1% |
| **Pricing page bounce** | < 35% | 35-50% | > 50% |
| **Feature page engagement** | > 60s | 30-60s | < 30s |

---

## Gate Summary by Business Type

Quick reference for which gates are most critical per business type.

### E-commerce Critical Gates
1. Product images (multiple, zoomable)
2. Clear pricing with shipping costs
3. Guest checkout available
4. Security badges on checkout
5. Mobile-optimized product pages
6. Page speed < 3 seconds
7. Reviews/ratings on products

### SaaS Critical Gates
1. Clear value proposition above fold
2. CTA above fold (free trial or demo)
3. Social proof (logos, testimonials)
4. Pricing transparency
5. Security/compliance badges
6. Page speed < 3 seconds
7. Mobile-responsive pricing page

### Lead Gen Critical Gates
1. Form visible or accessible above fold
2. Phone number prominent and clickable
3. Privacy policy near form
4. Form fields minimized (3-5)
5. Clear value proposition
6. Response time expectation set
7. Trust signals near form

### Local Service Critical Gates
1. Phone number in header (click-to-call)
2. Service area clearly stated
3. Google Maps embed or link
4. Business hours visible
5. Reviews/testimonials
6. Contact form simple (3-4 fields)
7. Mobile-first design (most traffic is mobile)
