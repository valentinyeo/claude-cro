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
| `/cro audit <url> [--depth quick\|standard\|deep] [--prospect]` | `cro-audit`: crawl + agent swarm + personas + skeptic |
| `/cro slides <audit-folder> [--pitch\|--client]` | `cro-slides`: HTML deck for a prospect (with offer) or client |
| `/cro wireframe <url or audit-folder> [finding ids]` | `cro-wireframe`: before/after fix designs, mobile + desktop |
| `/cro build-test <url> "<hypothesis>"` | `cro-build-test`: variant code, browser preview, test brief |
| `/cro build-test suite <url> <ACTION-PLAN.md>` | `cro-build-test`: readiness-gated test bundles and index |
| `/cro program <init\|plan\|launch\|result\|board\|report\|check>` | `cro-program`: a signed client's experiment program |
| `/cro research [topic\|weekly\|find <finding>]` | `cro-research`: grow and search the published A/B test evidence database |
| `/cro synthetic <url> [--traffic export.csv] [--visitors N]` | `cro-synthetic`: 100-200 LLM visitors modelled on real traffic shop the site and report friction |
| `/cro message-test <brief or audit-folder> "<question>"` | `cro-message-test`: a simulated crowd of buyers (MiroFish, Haiku) compares offers, prices or headlines and lists objections |
| `/cro results <audit-folder> [--wireframe <folder>]` | run `results_hub.py`: one page with every skill run shown the same way, an index and the experiments; publish it as a Claude artifact. It ends with a book-a-call line; `"cta"` in results-notes.json replaces it, `"cta": false` hides it |
| `/cro doctor` | run `doctor.py`: is the setup working? |
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
   **Never pass the subcommand word to a script.** For `research`, pass the
   remaining words unchanged (they are a topic, not a URL). For `build-test`,
   pass everything unchanged: `suite`, quoted hypotheses, finding ids, flags.
2. Resolve the scripts folder once: `cd "${CLAUDE_SKILL_DIR}/scripts" && pwd`.
   Call that absolute path `CRO_SCRIPTS` and write it out literally in every
   later command (shell variables do not persist between commands).
3. Read `${CLAUDE_SKILL_DIR}/../cro-<sub-skill>/SKILL.md` and follow it, passing
   the URL(s), any baseline numbers, and `CRO_SCRIPTS`.

## The jobs this pack does

0. **Improve your own site.** `/cro audit <url>`, then `/cro results <folder>`:
   the owner learns what loses visitors, why, and which fix to try first.
   Explain each finding in plain words; never assume the reader is a CRO expert.
1. **Win the client.** `/cro audit <url> --prospect` then `/cro slides <folder> --pitch`:
   real problems on their own site, with screenshots, and an offer sized by
   what their traffic allows.
2. **Run the client.** `/cro program init`, then monthly plan, build-test,
   launch, result and report, with `/cro wireframe` for design work.

## Rules every sub-skill follows

- **Test Readiness Gate first** for audit, test, build-test, plan and funnel: read
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
| `crawl_site.py <url> --json` | Key pages by type (home, collection, product, cart, pricing...) |
| `capture.py <url> <dir>` | Raw + rendered HTML, elements, 3 screenshots, speed, gaps for one page |
| `journey.py steps.json --out dir [--mobile]` | Replays a visitor journey in a browser, screenshot per step |
| `program.py ...` | Client experiment program: backlog, status, result stats, release diffs |
| `doctor.py [--quick]` | Setup health check with one fix per problem |
| `validate_report.py <dir>` | Checks a finished audit (sections, math, evidence) |
| `render_wireframe.py before.html --after after.html --annotations a.json -o renders` | Mobile/desktop PNGs and annotated before/after comparisons |
| `preview_variant.py <url> variant.js [--css variant.css] [--mobile]` | Control/variant screenshots, selector and JS checks |
| `build_slides.py <slides.json> [--embed] [--render] [--check]` | Build and verify an offline HTML audit deck |
| `evidence.py <validate\|add\|search\|stats\|verify\|export-md>` | Published A/B test evidence: search, add, verify, catalog |
| `tracking_audit.py <url> ... --out t.json --md T.md` | Every tracker and pixel that really fires, duplicates, consent, access to ask for |
| `synthetic.py <templates\|run\|report>` | Real traffic to visitor templates, LLM browser visitors, ranked friction report |
| `results_hub.py <audit-folder> [--wireframe <folder>]` | Results page: every run in one format, index, experiments with hypotheses (reads results-notes.json, experiments.json) |
| `message_test.py <run\|check>` | Drive a local MiroFish run: brief, graph, simulation, report with caveat and cost |

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
| `evidence/CATALOG.md`, `evidence/SCHEMA.md` | Source-linked published A/B tests; prefer these over proven-tests |
| `references/proven-tests-*.md` | Older idea lists with industry-reported lifts (unverified, no links) |
