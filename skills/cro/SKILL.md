---
name: cro
description: >
  Conversion rate optimization (CRO) router. Audits websites for conversions,
  checks whether the site has enough traffic to A/B test, and routes to the
  right CRO sub-skill. Use when the user says CRO, conversion rate, "why don't
  visitors buy/sign up", landing page review, A/B test ideas, or types /cro.
argument-hint: "<subcommand> <url> [--conversions N --cvr X]"
allowed-tools: Read, Grep, Glob, Bash, WebFetch, Agent
---

# CRO Router

## Commands

| Command | Sub-skill |
|---------|-----------|
| `/cro audit <url>` | `cro-audit`: full audit with 6 parallel agents |
| `/cro page <url>` | `cro-page`: one page, no agents |
| `/cro funnel <url1> <url2> ...` | `cro-funnel` |
| `/cro test <url>` | `cro-testing`: test ideas, gated by traffic |
| `/cro readiness` | Test Readiness Gate only (see below) |
| `/cro copy <url>` | `cro-copy` |
| `/cro ux <url>` | `cro-ux` |
| `/cro forms <url>` | `cro-forms` |
| `/cro ecommerce <url>` | `cro-ecommerce` |
| `/cro trust <url>` | `cro-trust` |
| `/cro tracking <url>` | `cro-tracking` |
| `/cro benchmark <url> <competitor-url>` | `cro-benchmark` |
| `/cro plan <url>` | `cro-plan`: 90-day roadmap |

## Routing

1. Split `$ARGUMENTS`: the first word is the subcommand, the rest is the URL
   list plus optional `--conversions N` and `--cvr X` / `--visitors N`.
   If the first word is a URL, treat the request as `audit`.
   **Never pass the subcommand word to a script.**
2. Resolve the scripts folder once: `cd "${CLAUDE_SKILL_DIR}/scripts" && pwd`.
   Call that absolute path `CRO_SCRIPTS` and write it out literally in every
   later command (shell variables do not persist between commands).
3. Read `${CLAUDE_SKILL_DIR}/../cro-<sub-skill>/SKILL.md` and follow it, passing
   the URL(s), any baseline numbers, and `CRO_SCRIPTS`.

## Rules every sub-skill follows

- **Test Readiness Gate first** for audit, test, plan and funnel: read
  `references/test-readiness.md`, get the baseline, run `test_readiness.py`.
  The verdict decides whether the report recommends A/B tests or usability
  research. Never recommend a test backlog to a NOT_TESTABLE site.
- **Run scripts with the wrapper:** `"<CRO_SCRIPTS>/cro-py" <script>.py ...`.
  It uses the skill's own Python env.
- **Evidence or cut it:** every finding quotes the page, names the element, or
  cites a script number. See `references/scoring.md`.
- **Industry numbers are estimates.** Benchmarks and proven-test lifts are
  unverified industry reports. Say "reported in case studies"; never promise
  a lift.

## Scripts (`CRO_SCRIPTS`)

| Script | Does |
|--------|------|
| `fetch_page.py <url> --output f.html [--json]` | Fetch HTML, blocks private addresses on every redirect |
| `parse_cro.py <file-or-url> --json` | Extract CTAs, forms, trust signals, tracking, headings, schema |
| `capture_screenshot.py <url> -o f.png [--mobile] [--full-page]` | Screenshot via Playwright |
| `analyze_funnel.py <url1> <url2> ...` | Step-to-step funnel consistency checks |
| `pagespeed.py <url> [--strategy mobile]` | Google PageSpeed Insights: lab + field Core Web Vitals |
| `test_readiness.py --conversions N --cvr X` | Can this site A/B test? MDE by duration and verdict |
| `validate_report.py <dir>` | Checks a finished audit (sections, math, evidence) |

## References (load only when needed)

| File | Use for |
|------|---------|
| `references/test-readiness.md` | Baseline inputs, verdicts, usability research fallback |
| `references/business-types.md` | Detecting the business type (the only copy of this list) |
| `references/scoring.md` | Weights, ratings, priorities, evidence rule (the only copy) |
| `references/quality-gates.md` | Pass/fail minimums per element |
| `references/ux-heuristics.md` | UX and form evaluation |
| `references/psychology-principles.md` | Persuasion and copy |
| `references/testing-framework.md` | Hypotheses, ICE, sample size, test hygiene |
| `references/conversion-benchmarks.md` | Rough industry ranges (estimates) |
| `references/proven-tests-*.md` | Test ideas with industry-reported lifts (unverified) |
