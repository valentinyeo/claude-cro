# Test Readiness Gate

Every audit, test plan and roadmap starts here: **can this site run A/B tests that
mean anything?** Recommending ten A/B tests to a store with 80 orders a month is
the most common way CRO advice wastes money. With too little traffic a test runs
for months, never reaches significance, and any "winner" is mostly noise.

## Inputs (the baseline)

Ask for these before recommending any test. They are the conversion baseline the
whole report is measured against.

| Input | Example | Where the client finds it |
|-------|---------|---------------------------|
| Conversions per month on the main goal | 240 orders | Shopify / store admin, CRM, GA4 key events |
| Conversion rate, or visitors per month | 1.8%, or 13,000 sessions | GA4, Shopify analytics |
| Share of traffic reaching the page to test | 0.4 for a PDP seen by 40% of visitors | GA4 page report |

If the user does not know: ask once. If still unknown, mark the baseline
**ASSUMED**, estimate from visible signals (review counts, Similarweb-style
traffic band, business size) and the benchmarks in `conversion-benchmarks.md`,
and state the verdict as provisional. Never present an assumed baseline as fact.

## Run the calculator

```bash
"${CRO_SCRIPTS}/cro-py" test_readiness.py --conversions 240 --cvr 1.8 [--traffic-share 0.4]
```

It prints the smallest lift a test can detect after 2, 4, 6 and 8 weeks
(alpha 0.05 two-sided, power 0.80, 50/50 split) and one verdict. Do the math with
the script, never by hand.

## Verdicts and what the report must recommend

| Verdict | Rule | Recommendation mode |
|---------|------|---------------------|
| **READY** | Detects a 10% lift within 4 weeks | Regular A/B program. ICE-ranked test backlog, 2-4 week tests. |
| **LIMITED** | Detects a 25% lift within 8 weeks, but not 10% in 4 | 2-4 **big-swing** tests a year (whole-page, offer, pricing, checkout flow), 6-8 weeks each, chosen from usability research. Small tweaks are shipped as fixes, not tested. |
| **NOT_TESTABLE** | Cannot detect a 25% lift in 8 weeks | **Usability research is the method.** No A/B test backlog. At most one radical, long-running test in the background. Ship fixes and track them against the baseline. |

Why 10% and 25%: most real wins from one change are under 10% relative; big
redesigns occasionally reach 20-30%. A test that can only detect 40%+ will almost
always end inconclusive.

## Fallback playbook: usability research (LIMITED and NOT_TESTABLE)

Put this in the report instead of (or before) the A/B test list:

1. **Moderated usability tests**: 5 target customers per round, think-aloud on
   the main conversion task (find product, add to cart, check out). 5 users find
   most of the big problems. Repeat after each round of fixes.
2. **Session recordings and heatmaps** (Microsoft Clarity is free): watch 30-50
   sessions that reached the conversion page and left. Note rage clicks, dead
   clicks, form abandonment.
3. **On-site poll** at the exit point: "What stopped you from buying today?"
   One open question. 50-100 answers are enough to rank objections.
4. **Customer interviews or post-purchase survey**: "What almost stopped you?"
   and "What made you choose us?" These give the words to use in copy.
5. **Ship and measure**: fix the problems research found, then compare the
   conversion rate for 4 weeks after against the baseline 4 weeks before. Note
   seasonality and campaigns; this is a directional read, not proof.
6. **Big-swing test** (LIMITED only): pick the one change research says matters
   most, make it big enough to move 25%+, run it 6-8 weeks without peeking.

## Report section (required in every audit, test plan and roadmap)

```markdown
## Test Readiness
**Baseline:** [N] conversions/month, [X]% CVR, [V] visitors/month — [CONFIRMED by user | ASSUMED]
**Verdict:** [READY | LIMITED | NOT_TESTABLE]
**Smallest detectable lift:** [a]% in 4 weeks, [b]% in 8 weeks
**What this means:** [one plain sentence]
**Method:** [A/B program | few big-swing tests + usability research | usability research]
```
