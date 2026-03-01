# Subscription CRO Template

Industry template for subscription-based businesses. Applies to streaming
services, subscription boxes, meal kits, membership sites, digital content
subscriptions, newsletters, fitness/wellness memberships, and any business
with recurring revenue as the primary model.

---

## Key Conversion Goals

| Goal | Priority | Typical Page |
|------|----------|-------------|
| New subscription signup | P0 | Pricing page, homepage, landing pages |
| Free trial start | P0 | Pricing page, homepage, feature pages |
| Plan upgrade (upsell) | P1 | In-app, account settings, usage limit prompts |
| Annual plan selection | P1 | Pricing page, upgrade prompts |
| Churn prevention | P1 | Cancellation flow, account settings |
| Reactivation (win-back) | P2 | Email campaigns, return visit pages |
| Referral conversion | P2 | In-app referral, post-purchase email |

---

## Primary Metrics

| Metric | Definition | Benchmark (Median) | Top Performer |
|--------|------------|--------------------|---------------|
| Subscription rate | New subscribers / pricing page visitors | 5-10% | 15-25% |
| Free trial start rate | Trial starts / pricing page visitors | 8-15% | 20-30% |
| Trial-to-paid rate | Paid conversions / trial starts | 20-30% | 40-60% |
| Annual plan selection | Annual subscribers / total new subscribers | 25-35% | 45-60% |
| Monthly churn rate | Cancellations / active subscribers per month | 5-8% | 2-4% |
| Upgrade rate | Plan upgrades / active subscribers per month | 1-3% | 4-7% |
| Reactivation rate | Reactivated / churned subscribers | 5-10% | 15-25% |
| Net revenue retention | Revenue from existing customers this period / last period | 90-100% | 110-130% |

---

## Common CRO Patterns for Subscription

1. **Annual vs monthly anchoring** -- Pre-select annual billing. Show monthly
   equivalent price ("Just $8.25/month, billed annually"). Display the total
   savings prominently ("Save $50/year"). Annual billing reduces churn and
   increases LTV.

2. **Feature gating** -- Free tier provides real value but strategically
   limits features that power users need. Limits should be encountered
   naturally during usage, creating organic upgrade moments. Avoid hard walls
   that feel punitive.

3. **Usage limits with soft prompts** -- "You've used 80% of your monthly
   allowance" with an upgrade CTA. Contextual and relevant, not aggressive.
   Usage-based upgrade prompts convert 3-5x better than generic upgrade CTAs.

4. **Downgrade path before cancellation** -- When a user initiates
   cancellation, offer a lower-priced plan or pause instead. "Not using all
   features? Switch to Basic for $5/month." Saves 10-20% of cancelling users.

5. **Cancellation flow optimization** -- Multi-step cancellation with
   feedback collection, offer alternatives (pause, downgrade, discount), show
   what they will lose, and require confirmation. Not dark pattern -- genuinely
   helpful alternatives. Saves 15-30% of cancellation attempts.

6. **Win-back campaigns** -- Email sequence to churned subscribers: 1 week
   (what's new), 1 month (special offer), 3 months (final offer). 5-15%
   reactivation rate.

7. **Social proof on pricing** -- "Joined by 50,000+ subscribers this month"
   or testimonials from paying customers on the pricing page. Subscriber
   count progression ("Growing from 100K to 500K in 2 years") builds momentum
   perception.

8. **Free trial with credit card vs without** -- Credit card required trials
   convert to paid at 40-60% but start fewer trials. No-card trials start
   more trials but convert at 15-25%. Test both, measure total paid
   conversions (not just conversion rate).

---

## Quick Win Checklist

- [ ] Pre-select annual billing on the pricing page
- [ ] Show monthly equivalent price for annual plans ("$8.25/mo billed annually")
- [ ] Display annual savings amount prominently ("Save $50/year" or "2 months free")
- [ ] Add "Most Popular" badge to the target plan tier
- [ ] Add subscriber count or growth metric near pricing ("500,000+ subscribers")
- [ ] Add a money-back guarantee badge on the pricing page (14 or 30 days)
- [ ] Show what is included in the free trial (full access vs limited)
- [ ] Add a testimonial from a paying subscriber near the pricing CTA
- [ ] Implement a "pause subscription" option in the cancellation flow
- [ ] Add a downgrade option before final cancellation confirmation
- [ ] Send a "we miss you" email to churned subscribers after 7 days

---

## Recommended Test Ideas

| Test | Hypothesis | ICE Estimate |
|------|-----------|--------------|
| Pricing: annual pre-selected vs monthly default | Annual pre-selection will increase annual plan uptake because of default bias | 8.0 |
| Trial: credit card required vs no card | No-card trial will generate more total paid subscribers because the lower barrier captures a larger top-of-funnel | 6.3 |
| Pricing: 3 tiers vs 2 tiers | 3 tiers with decoy pricing will increase mid-tier selection because of the compromise effect | 6.7 |
| Cancellation: add pause option | Offering "pause for 1 month" will reduce churn because some users just need a break, not cancellation | 7.3 |
| Upgrade prompt: usage-based vs time-based | Usage-based prompt ("You've hit your limit") will convert better than scheduled prompts because it is contextually relevant | 7.0 |
| Pricing page: add feature comparison table | Detailed comparison table will increase conversions because it helps users self-select the right plan with confidence | 6.3 |
| Win-back: discount vs new features email | "Here's what's new" email will reactivate more users than a discount because it addresses the root cause (perceived value) | 5.7 |
| Onboarding: guided setup vs self-serve | Guided onboarding will increase trial-to-paid because users reach value faster | 7.0 |

---

## Industry Benchmarks

| Metric | Streaming | SaaS | News/Media | Subscription Box | Fitness |
|--------|-----------|------|------------|------------------|---------|
| Monthly churn | 4-6% | 3-5% | 6-10% | 8-12% | 6-9% |
| Trial-to-paid | 50-65% | 20-35% | 15-25% | N/A | 25-40% |
| Annual plan uptake | 20-30% | 35-50% | 25-35% | 15-25% | 30-45% |
| Avg. subscriber lifetime | 18-24 mo | 24-36 mo | 8-14 mo | 6-10 mo | 10-16 mo |
| Reactivation rate | 8-12% | 10-15% | 5-8% | 3-6% | 6-10% |
| Pricing page CVR | 10-20% | 8-15% | 5-10% | 12-20% | 8-14% |

---

## Tool Recommendations

| Category | Recommended | Why |
|----------|-------------|-----|
| Subscription Billing | Stripe Billing, Recurly, Chargebee | Manage plans, trials, upgrades, dunning |
| A/B Testing | VWO, Optimizely, LaunchDarkly (feature flags) | Test pricing, plans, upgrade prompts |
| Retention Analytics | Baremetrics, ChartMogul, ProfitWell | MRR tracking, churn analysis, cohort reports |
| In-App Messaging | Appcues, Intercom, Pendo | Upgrade prompts, onboarding, feature announcements |
| Email Automation | Customer.io, Braze, ActiveCampaign | Trial nurture, win-back, upgrade campaigns |
| Cancellation Flow | Churnkey, ProsperStack, Brightback | Optimized cancellation flows, save offers |
| Survey | Typeform, Hotjar Surveys | Churn reason collection, NPS, CSAT |
