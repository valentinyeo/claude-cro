# Where to find CRO evidence

Start with primary experiment writeups. Follow links to the original account,
read the whole result, and save an exact supporting quote. Search snippets,
AI answers, promotional headlines, and screenshots of statistics without a
readable source page are discovery aids, not verification.

## Sources and quality notes

| Source | Starting point | Quality notes |
|--------|----------------|---------------|
| Company engineering and growth blogs | [Booking](https://booking.ai/), [Etsy](https://www.etsy.com/codeascraft), [Airbnb](https://medium.com/airbnb-engineering), [Microsoft experimentation](https://www.microsoft.com/en-us/research/group/experimentation-platform-exp/) | Strong provenance; often discuss design and false positives. Many posts describe experimentation infrastructure, not a specific CRO test. Do not turn a program-wide metric into an individual result. |
| Academic papers | [Google Scholar](https://scholar.google.com/), [ACM](https://dl.acm.org/), [arXiv](https://arxiv.org/) | Look for randomized comparison, population, denominators, uncertainty and complete outcomes. Preprints are not automatically peer reviewed. Accessible abstract alone may not establish the numbers; do not call a PDF verified with the HTML-only verifier. |
| VWO / Wingify | [Success stories](https://wingify.com/success-stories/) | Original VWO URLs currently redirect to Wingify. Read the full body: headline rounding and metric labels sometimes differ from the actual outcome. The seed uses reachable canonical URLs, not invented links. Strong win-selection and sales bias. |
| Convert | [Case studies](https://www.convert.com/case-studies/) | Frequently publishes durations, counts and confidence. Distinguish named client from agency and test-specific lift from modeled annual ROI. Rounded "100%" is not certainty. |
| Optimizely | [Customer stories](https://www.optimizely.com/insights/) | Good for named experiments, but many pages report aggregate program outcomes or platform adoption. Require a specific control and variant. |
| AB Tasty | [Customer stories](https://www.abtasty.com/resources/) | Seek controlled experiment details. Separate personalized segment outcomes from randomized overall outcomes and research-only stories. Some stories are also published on Wingify; dedupe original experiment, not just URL. |
| GoodUI | [Evidence and leaks](https://goodui.org/leaks/) | Distinguish measured evidence from observed UI changes. A leaked variant or later rollout is not a measured A/B result. Some detail is paywalled; never infer a lift or winner from adoption. |
| Agency case studies | [Conversion Rate Experts](https://conversion-rate-experts.com/), [CXL](https://cxl.com/blog/), named agency blogs | Useful for hypotheses and treatments. Prefer named clients, direct quotes and statistical details; account for selective disclosure and client anonymization. Syndicated case studies are one experiment, not independent replications. |
| Baymard | [Research](https://baymard.com/research) | Usability research, not automatically A/B tests. Use `research_type: "research"`, strength C when qualitative, and no fabricated lift. Cite as usability evidence, not randomized causal proof. |

A reachable page is not necessarily a credible experiment. A full disclosure
from a vendor can earn reporting-completeness grade A while still having a
small sample, short runtime, peeking or multiple comparisons. Explain those risks.

## Query patterns

Replace terms with the actual business, page, element and principle.

```text
"checkout" "A/B test" "sample size" "confidence"
"pricing" "experiment" "no significant difference"
"testimonials" "A/B" "decreased"
"form fields" "split test" "control" "visitors"
"add to cart" "experiment" "negative result"
site:booking.ai experiment conversion null
site:etsy.com/codeascraft experiment conversion
site:airbnb-engineering.com experiment conversion
site:wingify.com/success-stories/ "statistical" "product"
site:convert.com/case-studies/ "control" "confidence"
site:optimizely.com "case study" "checkout"
site:abtasty.com "conversion" "control"
site:goodui.org "test" "lost"
"online controlled experiment" "null result" conversion
```

Also search `inconclusive`, `failed hypothesis`, `did not outperform`, `guardrail`,
`negative impact`, and `unchanged`. Record what was searched, including searches
that found nothing. Do not claim the database is balanced because a few losses
were added. For audit matching, search the local database first and broaden one
filter at a time before deciding to research a new source.
