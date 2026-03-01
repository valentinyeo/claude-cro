# A/B Testing Framework

Methodology for generating, prioritizing, executing, and documenting A/B test
hypotheses. Use this framework when generating test ideas from CRO audits or
when advising on testing strategy.

---

## ICE Prioritization Framework

Score every test hypothesis on three dimensions, each rated 1-10.

### Impact (1-10)
How much will this change affect the key conversion metric if successful?

| Score | Meaning | Example |
|-------|---------|---------|
| 9-10 | Transformative | Redesigning the entire checkout flow |
| 7-8 | Major | Changing the primary CTA above the fold |
| 5-6 | Moderate | Adding social proof to the pricing page |
| 3-4 | Minor | Adjusting button color or microcopy |
| 1-2 | Negligible | Changing footer text or non-critical layout |

**Scoring Guidance:**
- Changes to primary conversion path score higher than ancillary pages
- Above-fold changes score higher than below-fold
- Changes affecting all visitors score higher than segment-specific
- Addressing known friction points (from analytics) scores higher than guesses

### Confidence (1-10)
How certain are you that this change will produce a positive result?

| Score | Meaning | Evidence Basis |
|-------|---------|----------------|
| 9-10 | Near-certain | Multiple data points, proven pattern, user research confirms |
| 7-8 | High | Analytics show clear problem, best practice supports the fix |
| 5-6 | Moderate | Some data suggests opportunity, principle-based reasoning |
| 3-4 | Low | Hunch or hypothesis with limited supporting evidence |
| 1-2 | Speculative | No data, pure intuition, untested assumption |

**Increase Confidence By:**
- Analyzing heatmaps and session recordings
- Reviewing user feedback and support tickets
- Checking analytics for drop-off patterns
- Referencing published case studies
- Running user surveys or interviews

### Ease (1-10)
How easy is this to implement and deploy?

| Score | Meaning | Effort |
|-------|---------|--------|
| 9-10 | Trivial | Copy/text change, color swap, hide/show element |
| 7-8 | Easy | Single component redesign, add an element |
| 5-6 | Moderate | Multiple page elements, some development work |
| 3-4 | Difficult | Cross-page changes, backend work, new functionality |
| 1-2 | Very hard | Architecture changes, third-party integrations, new features |

### Priority Score Calculation

```
Priority Score = (Impact + Confidence + Ease) / 3
```

| Priority Score | Action |
|---------------|--------|
| 8.0-10.0 | Test immediately — quick win with high confidence |
| 6.0-7.9 | Test this sprint — strong opportunity |
| 4.0-5.9 | Plan for next sprint — worth testing but lower priority |
| 2.0-3.9 | Backlog — consider when higher-priority tests are exhausted |
| 1.0-1.9 | Skip — effort outweighs likely benefit |

---

## Hypothesis Template

Every test hypothesis must follow this structure:

```
If we [CHANGE]
on [PAGE/ELEMENT],
then [METRIC] will [DIRECTION] by [ESTIMATED MAGNITUDE]
because [REASON BASED ON DATA OR PRINCIPLE].
```

### Examples

**Good Hypothesis:**
> If we add customer testimonials with specific results above the fold on the
> pricing page, then pricing page-to-signup conversion will increase by 10-15%
> because social proof at the decision point reduces purchase uncertainty
> (Cialdini's Social Proof principle), and our heatmap shows 60% of visitors
> never scroll past the fold.

**Bad Hypothesis:**
> If we change the button color to green, conversions will increase.

**Why It's Bad:**
- No specific page identified
- No metric defined
- No magnitude estimate
- No evidence-based reasoning
- No "because" clause

### Hypothesis Quality Checklist

- [ ] Specific change described (what exactly changes)
- [ ] Target page or element identified
- [ ] Primary metric defined
- [ ] Direction and magnitude estimated
- [ ] Evidence-based reasoning provided
- [ ] Connects to a known principle, data point, or user insight
- [ ] Feasible to implement and measure

---

## Sample Size Guidance

Required visitors per variant to detect a given Minimum Detectable Effect (MDE)
at 95% confidence and 80% statistical power, assuming a 3% baseline conversion
rate.

| MDE (Relative) | MDE (Absolute) | Visitors per Variant | Total (2 variants) |
|----------------|----------------|---------------------|-------------------|
| 5% | 0.15pp (3.0% to 3.15%) | ~51,500 | ~103,000 |
| 10% | 0.30pp (3.0% to 3.30%) | ~13,000 | ~26,000 |
| 15% | 0.45pp (3.0% to 3.45%) | ~5,800 | ~11,600 |
| 20% | 0.60pp (3.0% to 3.60%) | ~3,300 | ~6,600 |
| 25% | 0.75pp (3.0% to 3.75%) | ~2,100 | ~4,200 |
| 30% | 0.90pp (3.0% to 3.90%) | ~1,500 | ~3,000 |
| 50% | 1.50pp (3.0% to 4.50%) | ~550 | ~1,100 |

### Adjustments

**Higher baseline CVR = fewer visitors needed.**
At 10% baseline, a 10% MDE requires ~3,500/variant (vs. 13,000 at 3% baseline).

**Lower baseline CVR = more visitors needed.**
At 1% baseline, a 10% MDE requires ~39,000/variant.

### Practical Implications

| Monthly Traffic | Realistic MDE | Test Duration |
|----------------|---------------|---------------|
| 100,000+ | 5-10% | 2-4 weeks |
| 50,000-100,000 | 10-15% | 2-4 weeks |
| 20,000-50,000 | 15-25% | 3-6 weeks |
| 10,000-20,000 | 20-30% | 4-8 weeks |
| 5,000-10,000 | 30-50% | 6-12 weeks |
| < 5,000 | Only test big changes | Consider qualitative research instead |

**Low-traffic sites:** Focus on high-impact, radical redesigns rather than
incremental tweaks. Consider qualitative methods (user testing, surveys,
heuristic evaluation) over A/B testing.

---

## Test Duration Rules

### Minimum Duration
- **14 days minimum** — must capture at least 2 full business cycles
  (weekday + weekend patterns).
- **Capture full weeks** — always run for complete weeks (7, 14, 21, 28 days).
- **Avoid starting/ending mid-week** — ideally start on Monday, end on Sunday.

### Maximum Duration
- **8 weeks maximum** — after this, external factors likely confound results.
- If no significance after 8 weeks, the effect is likely too small to matter.

### Calendar Considerations
- **Avoid overlapping with:** Major holidays, Black Friday/Cyber Monday, site
  redesigns, marketing campaigns, PR events, product launches.
- **Seasonal traffic:** If your test spans a seasonal shift (e.g., October to
  November for e-commerce), results may be unreliable.
- **Day-of-week effects:** Some businesses have strong weekly cycles (B2B peaks
  Tue-Thu, e-commerce peaks weekends). Always capture full cycles.

### When to Stop a Test Early
- **Only if:** The variant is causing measurable harm (significantly increased
  bounce rate, error rate, or complaints).
- **Never stop early because:** It "looks like" there's a winner. Statistical
  significance can fluctuate dramatically before stabilizing.
- **Peeking penalty:** Checking results daily and stopping at first significance
  inflates false positive rate from 5% to 20-30%.

---

## Statistical Significance

### Confidence Level
- **95% confidence minimum** for declaring a winner.
- **99% confidence** recommended for high-stakes changes (checkout flow,
  pricing, core CTA).
- **90% confidence** acceptable only for low-risk, easily reversible changes.

### One-Tailed vs. Two-Tailed Tests
- **Two-tailed (default):** Use when you want to detect both positive AND
  negative effects. This is the standard approach.
- **One-tailed:** Use only when you are certain the change cannot hurt (rare).
  Requires half the sample size but misses negative effects.

### Multiple Comparison Correction
When testing multiple variants or metrics simultaneously, apply corrections:

- **Bonferroni Correction:** Divide alpha by the number of comparisons.
  3 variants = 0.05/3 = 0.0167 required significance per comparison.
- **Practical approach:** Designate ONE primary metric before the test starts.
  Secondary metrics are directional indicators only, not decision criteria.

### Bayesian vs. Frequentist
- **Frequentist (traditional):** P-value based. Requires fixed sample size.
  Industry standard for most testing platforms.
- **Bayesian:** Probability-based. Allows for continuous monitoring without
  peeking penalties. Better for low-traffic sites. Reports "probability to
  beat control" rather than p-values.

---

## Common Pitfalls

### 1. Peeking Problem
**What:** Checking results daily and declaring a winner at the first sign of
statistical significance.
**Why It's Bad:** p-values fluctuate. A test that shows p=0.03 on day 3 may
stabilize at p=0.15 by day 14. Peeking inflates false positive rate to 20-30%.
**Fix:** Pre-commit to a test duration and sample size. Only analyze at the
predetermined endpoint.

### 2. Stopping Too Early
**What:** Ending a test after 3-5 days because the result "looks conclusive."
**Why It's Bad:** Day-of-week effects, novelty effects, and small sample sizes
create illusory patterns.
**Fix:** Minimum 14 days, minimum sample size per variant.

### 3. Testing Too Many Variants
**What:** Running 5+ variants simultaneously.
**Why It's Bad:** Requires 5x the traffic, increases false positive risk,
makes it hard to isolate what caused the effect.
**Fix:** Limit to 2-3 variants (control + 1-2 challengers). Use multivariate
testing only with very high traffic.

### 4. Not Accounting for Seasonality
**What:** Running a test during a seasonal shift and attributing the change
to the variant.
**Why It's Bad:** A November e-commerce test will show increasing CVR regardless
of the variant, due to holiday shopping.
**Fix:** Use year-over-year comparisons. Avoid tests that span seasonal
boundaries.

### 5. Simpson's Paradox
**What:** A test that wins overall but loses in every individual segment
(or vice versa).
**Why It's Bad:** Uneven segment distribution across variants creates
misleading aggregate results.
**Fix:** Check results by device, traffic source, and user segment. Ensure
even traffic allocation.

### 6. Testing Insignificant Changes
**What:** A/B testing button color, font size, or minor copy tweaks on
low-traffic sites.
**Why It's Bad:** The expected effect is smaller than the MDE you can detect.
You'll never reach significance.
**Fix:** Focus on high-impact, structural changes. Use heuristic evaluation
for micro-optimizations.

### 7. Ignoring Secondary Metrics
**What:** Declaring a winner based solely on the primary metric while ignoring
negative effects on other metrics.
**Why It's Bad:** A CTA change might increase clicks but decrease downstream
conversion or increase refund rate.
**Fix:** Monitor secondary metrics (bounce rate, time on page, downstream
conversion, revenue per visitor) alongside the primary metric.

### 8. Survivorship Bias in Test Learnings
**What:** Only remembering winning tests and ignoring failures.
**Why It's Bad:** Losing tests contain valuable learnings about what customers
don't want.
**Fix:** Document all tests equally. Build a testing knowledge base.

---

## Test Documentation Template

Every A/B test should be documented using this template:

```
## Test: [Test Name]

### Metadata
- **Test ID:** [Unique identifier]
- **Page(s):** [URL(s) tested]
- **Date:** [Start date] to [End date]
- **Duration:** [X days]
- **Platform:** [Testing tool used]

### Hypothesis
If we [CHANGE] on [PAGE],
then [METRIC] will [DIRECTION] by [ESTIMATED MAGNITUDE]
because [REASON].

### ICE Score
- Impact: [1-10] — [Justification]
- Confidence: [1-10] — [Justification]
- Ease: [1-10] — [Justification]
- **Priority Score: [X.X]**

### Variants
- **Control (A):** [Description of current state]
- **Variant B:** [Description of change]
- **Variant C (if applicable):** [Description]

### Primary Metric
[Metric name and definition]

### Secondary Metrics
- [Metric 1]
- [Metric 2]

### Traffic Allocation
- Control: [X%]
- Variant B: [X%]
- Sample size target: [X visitors per variant]
- MDE target: [X%]

### Results
| Metric | Control | Variant B | Lift | Confidence |
|--------|---------|-----------|------|------------|
| [Primary] | X% | X% | +X% | XX% |
| [Secondary 1] | X | X | +X% | XX% |

### Winner
[Control / Variant B / Inconclusive]

### Learning
[What did we learn? What does this tell us about our users? How does this
inform future tests?]

### Next Steps
[Implement winner? Run follow-up test? Investigate further?]
```

---

## Test Idea Categories

When generating test ideas from a CRO audit, organize them into these
categories:

| Category | Examples |
|----------|---------|
| **CTA** | Text, color, size, placement, number, animation |
| **Copy** | Headlines, value prop, benefit statements, urgency |
| **Layout** | Element order, spacing, column structure, above/below fold |
| **Social Proof** | Testimonials, reviews, logos, counters, real-time activity |
| **Forms** | Field count, layout, labels, validation, multi-step |
| **Pricing** | Presentation, anchoring, framing, plan names, defaults |
| **Navigation** | Menu structure, sticky nav, breadcrumbs, search |
| **Trust** | Badges, guarantees, security indicators, policies |
| **Media** | Images, videos, product photos, hero section |
| **Personalization** | Segment-specific messaging, dynamic content |
