# CRO Health Score

The one definition of the score. Skills and agents point here; do not copy it.

## Weights

| Category | Weight | Scored by |
|----------|--------|-----------|
| UX | 25% | cro-ux agent (`UX score`) |
| Copy | 20% | cro-copy agent |
| Trust | 15% | cro-trust agent |
| Visual | 15% | cro-visual agent |
| Forms | 10% | cro-ux agent (separate `Forms score`) |
| Performance | 10% | cro-performance agent |
| Tracking | 5% | cro-tracking agent |

`Score = sum(category score × weight)`, rounded to a whole number.

**Missing categories:** if the page has no form, or an agent failed, drop that
category and divide the remaining weights by their sum so they total 100%. Show
the weights you actually used in the score table and name what was dropped.

## Ratings

| Score | Rating |
|-------|--------|
| 90-100 | Exceptional |
| 70-89 | Strong |
| 50-69 | Moderate |
| 30-49 | Weak |
| 0-29 | Critical |

## Priority levels

| Priority | Meaning | When |
|----------|---------|------|
| **Critical** | Blocks conversions (broken form, no CTA, trust-destroying issue) | Fix now |
| **High** | Major friction or missed persuasion | Within 1-2 weeks |
| **Medium** | Works but leaves conversions on the table | Within 30 days |
| **Low** | Polish | Backlog |

## Evidence rule

Every finding carries an `Evidence:` line: a quote from the page, an element or
selector, a number from a script, or a screenshot reference. A finding without
evidence is an opinion and is cut. Lift percentages from the proven-tests files
are industry-reported and unverified: write them as "reported in case studies",
never as the result this site will get.
