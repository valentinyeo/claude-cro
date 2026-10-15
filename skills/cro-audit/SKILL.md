---
name: cro-audit
description: >
  Full website conversion audit: checks whether the site has enough orders to
  A/B test, runs 6 CRO specialist agents in parallel, scores the site 0-100,
  and writes a verified audit plus action plan. Use for /cro audit, "CRO audit",
  "conversion audit", or "audit my site for conversions".
argument-hint: "<url> [--conversions N --cvr X]"
disable-model-invocation: true
allowed-tools: Read, Write, Grep, Glob, Bash, WebFetch, Agent
---

# Full Conversion Audit

You coordinate the audit: collect the page once, set the baseline, hand the
files to 6 specialist agents, merge their findings, then check your own report
before handing it over.

`CRO_SCRIPTS` = the absolute path from `cd "${CLAUDE_SKILL_DIR}/../cro/scripts" && pwd`.
Write it out literally in each command. Run every script as `"<CRO_SCRIPTS>/cro-py" <script>.py`.

## Step 1: Workspace and page capture (once, shared by all agents)

```bash
W="$PWD/cro-audit-<domain>-<YYYY-MM-DD>"; mkdir -p "$W"
"<CRO_SCRIPTS>/cro-py" fetch_page.py <url> --render --output "$W/page.html" --json > "$W/fetch.json"
"<CRO_SCRIPTS>/cro-py" parse_cro.py "$W/page.html" --json > "$W/elements.json"
"<CRO_SCRIPTS>/cro-py" capture_screenshot.py <url> -o "$W/desktop.png" -W 1440 -H 900
"<CRO_SCRIPTS>/cro-py" capture_screenshot.py <url> -o "$W/mobile.png" --mobile
"<CRO_SCRIPTS>/cro-py" capture_screenshot.py <url> -o "$W/mobile-full.png" --mobile --full-page
"<CRO_SCRIPTS>/cro-py" pagespeed.py <url> --strategy mobile --json > "$W/pagespeed-mobile.json"
```

- `--render` saves what a visitor's browser sees (JavaScript included).
- Exit code 3 / `"blocked"` in `fetch.json` means a bot wall or empty page.
  Look at `desktop.png`: if it shows the real site, audit from the screenshots
  and WebFetch and note the gap; if it shows the wall too, stop and tell the
  user. Never audit a block page as if it were the site.
- A failed screenshot or PageSpeed call is not fatal: record it in
  `$W/gaps.txt` and continue.

## Step 2: Business type

Read `${CLAUDE_SKILL_DIR}/../cro/references/business-types.md` and classify from
`elements.json` and the HTML. Record the main conversion action.

## Step 3: Test Readiness Gate (the baseline)

Read `${CLAUDE_SKILL_DIR}/../cro/references/test-readiness.md` and follow it.

- Baseline numbers given in the arguments: use them, mark CONFIRMED.
- Not given: ask the user once for monthly conversions (orders/leads) and
  conversion rate or monthly visitors. While waiting, continue with Steps 4-5.
- User does not know or is not around: estimate, mark ASSUMED, explain the estimate.

Run `test_readiness.py` and save its output to `$W/readiness.txt`. The verdict
decides the recommendation mode for the whole report.

## Step 4: Six specialist agents, in parallel

Spawn all six in ONE message with the Agent tool, `subagent_type` set to the agent
name. Each prompt contains: the URL, the workspace path `$W`, `CRO_SCRIPTS`,
the business type and main conversion, and this line: "Read the files in the
workspace; do not refetch the page. Every finding needs an Evidence line."

| Agent | Returns |
|-------|---------|
| `cro-ux` | UX score and a separate Forms score (or "no form") |
| `cro-copy` | Copy score |
| `cro-trust` | Trust score |
| `cro-visual` | Visual score (uses the screenshots) |
| `cro-performance` | Performance score (uses `pagespeed-mobile.json`) |
| `cro-tracking` | Tracking score |

If the Agent tool is unavailable, do each analysis yourself in that order.
If one agent fails, drop its category per `scoring.md` and say so.

## Step 5: Score

Apply `${CLAUDE_SKILL_DIR}/../cro/references/scoring.md`. Drop missing
categories and rescale the weights; show the weights actually used.

## Step 6: Write the two files into `$W`

Merge duplicate findings across agents (same element = one finding, credit both).
Rank by priority, then by impact.

### FULL-AUDIT.md

```markdown
# CRO Audit: [domain]
**Date:** [date] · **URL:** [url] · **Business type:** [type], main conversion: [action]
**CRO Health Score:** [N]/100 — [rating]

## Bottom line
[3 sentences: biggest problem, biggest opportunity, what to do first.]

## Test Readiness
[Section exactly as in test-readiness.md]

## Score
| Category | Score | Weight | Weighted |
|----------|-------|--------|----------|
| UX | [n]/100 | [w]% | [n×w/100, 1 decimal] |
| ... one row per scored category ... |
| **Total** | | **100%** | **[sum]** |

## Top 5 issues
1. [Issue] — [category] — [priority]. Evidence: [quote/element/number]

## What already works
[3-5 strengths worth keeping]

## Findings by category
[One subsection per agent, findings with priority tag and Evidence line]

## Gaps in this audit
[What could not be checked and why: blocked fetch, no field data, login-only pages]
```

### ACTION-PLAN.md

```markdown
# CRO Action Plan: [domain]
**Date:** [date] · **Score:** [N]/100 · **Test readiness:** [verdict]

## Critical
### [C-1] [Title]
- **Category / found by:** [category] / [agent]
- **Evidence:** [quote, element or number]
- **Fix:** [specific change]
- **Effort:** [Easy/Medium/Hard] · **How to validate:** [ship + baseline | big-swing test | A/B test]

## High
### [H-1] ...
## Medium
### [M-1] ...
## Low
### [L-1] ...
```

Then ONE of these, by verdict:

- **READY:** `## A/B Test Backlog`: 3-5 hypotheses (If we [change], then
  [metric] will [rise] because [evidence]), ICE scored, with the duration from
  `readiness.txt` for the MDE you expect.
- **LIMITED:** `## Research Plan` (usability playbook from test-readiness.md,
  tailored to this site's flow) followed by `## Big-Swing Tests`: at most 2,
  each a large change, 6-8 weeks.
- **NOT_TESTABLE:** `## Research Plan` only, plus how to track fixes against the
  baseline. No A/B test section.

## Step 7: Verify, fix, repeat (do not skip)

1. Objective check:
   `"<CRO_SCRIPTS>/cro-py" validate_report.py "$W"`. Fix every error and run it
   again until it prints PASS (max 3 rounds; report anything still failing).
2. Subjective check, as a strict reviewer, then fix:
   - Would a store owner know exactly what to change from each Fix line?
     "Improve the CTA" fails; "Change 'Submit' to 'Get my quote' on the hero
     form" passes.
   - Is any finding contradicted by a screenshot (e.g. "no CTA above the fold"
     when `mobile.png` shows one)? Open the screenshots and check the top 5.
   - Does any sentence promise a lift for this site? Rewrite as a reported
     industry result or remove.
   - Does the recommendation mode match the verdict?

## Step 8: Hand-off

Reply with: score and rating, test readiness verdict, the top 3 actions, and the
workspace path. Keep it short; the files hold the detail.
