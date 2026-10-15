---
name: cro-build-test
description: >
  Build a working A/B test variant with a test brief, vanilla JavaScript,
  scoped CSS, GA4 goal suggestions and verified desktop/mobile previews.
  Use for /cro build-test, "build an A/B test", "generate a test variant",
  "turn this finding into a test", or "build a test suite from this audit".
argument-hint: '<url> "<hypothesis or finding id>" [--conversions N --cvr X --traffic-share X] | suite <url> <ACTION-PLAN.md>'
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, WebFetch
---

# Build a Test, Not Just an Idea

Work in this session, without helpers. A good variant changes a specific,
evidence-backed obstacle, preserves the existing conversion path, and can be
removed by pausing the experiment and reloading. A passing local preview is
not proof of a winning test or a production-ready platform integration.

Resolve `CRO_SCRIPTS` from `${CLAUDE_SKILL_DIR}/../cro/scripts` and `BUILD_DIR`
from `${CLAUDE_SKILL_DIR}` to absolute paths. Write these paths literally in
commands. Run Python with `"<CRO_SCRIPTS>/cro-py"`. The wrapper prefixes its own
scripts folder, so use `../../cro-build-test/scripts/render_test.py` for the
sibling renderer, not an absolute script argument.

## 1. Readiness gate first, before writing variant code

Read `../cro/references/test-readiness.md` and, when needed,
`../cro/references/business-types.md` and `../cro/references/scoring.md`.
Ask once for monthly conversions, CVR or visitors, and the share reaching the
actual target URL and audience. Use eligible-flow CVR, not a different site's
average. Do not count site-wide traffic again if the baseline already covers
only this flow. Save the user's source and exclusions.

```bash
"<CRO_SCRIPTS>/cro-py" test_readiness.py --conversions <N> --cvr <X> --traffic-share <share> --json > "<workspace>/readiness.json"
```

Use `--visitors` instead of `--cvr` when that is the supplied input. Baselines
must be CONFIRMED or explicitly ASSUMED with the source and assumptions. If the
baseline is unknown, follow the reference's estimation rule, make any generated
bundle provisional, and require confirmed inputs before launch. Synthetic demo
inputs are not a claim about the site's traffic.

- **NOT_TESTABLE:** refuse to generate test code or a test backlog. Say in one
  sentence: "Ship the evidence-backed change as a fix and use research, because
  this traffic cannot resolve a useful A/B result." Write `fix-plan.md` with
  the evidence, specific fix, rollback, baseline tracking and research plan:
  five moderated target-user sessions, 30-50 relevant recordings, an exit poll,
  customer interviews, then four weeks before/after with seasonal and campaign
  caveats. That comparison is directional, not causal proof. Stop here.
- **LIMITED:** allow only research-backed big swings, such as a whole-page,
  offer or flow change. Reject button text, colors and trust-line tweaks as
  tests; recommend shipping them as fixes. Plan 6-8 weeks and explain why the
  scope could plausibly matter, without forecasting a lift. Require a research
  finding before choosing the change.
- **READY:** allow a single focused variant against control, 50/50, 2-4 weeks.
  Choose a planning MDE, not a promised result. `render_test.py` selects the
  shortest allowed duration whose calculator MDE meets that threshold. If none
  qualifies, change the scope or use research; do not invent a shorter runtime.

Keep the readiness output and repeat the gate per materially different audience.

## 2. Collect evidence and choose the change

```bash
"<CRO_SCRIPTS>/cro-py" fetch_page.py <url> --render --output "<workspace>/page.html" --json > "<workspace>/fetch.json"
```

Require `fetched_with: browser`, a successful status and no `blocked` reason.
If browser rendering fails, fix it or stop and name the blocker. Never generate
code from a bot wall or from invented DOM. For a finding id, locate it in the
provided `ACTION-PLAN.md`; retain its id, quote, proposed fix and source path.
If it cannot be resolved, request the audit path rather than inventing a finding.
For a hypothesis, connect it to a quote, element, screenshot or script number.

Pick stable IDs, semantic attributes or existing data attributes from the actual
rendered DOM. Avoid generated class hashes, positional selectors and text-only
matches. Record exact match counts. Scope to the intended hero, form or section;
never change every button. Check both mobile and desktop. Preserve links,
existing event listeners, accessible names, form validation and checkout.

Trust claims must quote the site's current policy and market, including material
conditions. Do not add unsupported shipping, returns, security or social proof.
Use If/Then/Because with the business outcome, not "clicks will go up" alone.
One experiment answers one question; related edits can support that question.

## 3. Author structured test inputs and render the bundle

Read `assets/test.example.json` for the exact input shape and
`references/authoring.md` for changes and deployment constraints. Create
`<workspace>/specs/<id>.json`. Replace all example evidence and synthetic baseline
notes. Include source finding id in the evidence and a concrete definition,
denominator, attribution window and data source for the primary metric.
Guardrails need thresholds and a decision rule, not just metric names.

```bash
"<CRO_SCRIPTS>/cro-py" ../../cro-build-test/scripts/render_test.py "<workspace>/specs/<id>.json" --readiness "<workspace>/readiness.json" --output "<workspace>/tests/<id>"
```

The renderer writes `test-brief.md`, `variant.js`, optional `variant.css`,
`goals.js`, `test.json` and `readiness.json`. It refuses NOT_TESTABLE, non-big-swing
LIMITED inputs, undetectable planning MDEs and overwriting prior evidence.
Use a fresh revision folder after changes. Do not hand-edit the generated brief
or silently change the readiness verdict.

The JS has no framework or platform dependency. It injects scoped CSS with a
unique id, waits with MutationObserver and a bounded timeout, and avoids duplicate
UI on reinjection. HTML fragments are authored, reviewed static markup, never
interpolated user data. For changes outside the supported operations, adapt the
local template, keep its manifest/runtime contract and verify the same invariants.
Do not replace interactive subtrees just to change a label.

## 4. Preview, view, fix, repeat

```bash
"<CRO_SCRIPTS>/cro-py" preview_variant.py <url> "<workspace>/tests/<id>/variant.js"
"<CRO_SCRIPTS>/cro-py" preview_variant.py <url> "<workspace>/tests/<id>/variant.js" --mobile
```

CSS is already included in generated JS. Use `--css <file>` only for an externally
authored variant whose CSS is not embedded. Outputs go to `preview-desktop/`
and `preview-mobile/`, each with control/variant viewport and full-page PNGs,
selector counts, console errors, page exceptions and `report.json`.
If a known popup hides the target, inspect its DOM and repeat with
`--dismiss-selector '<close-or-reject-selector>'` for each overlay. For an iframe,
use `--dismiss-selector '<iframe-selector>::frame::<button-selector>'`. These
explicit clicks happen before both captures and are recorded in the report.
Never auto-accept consent, submit a form or hide an overlay only in the variant.

1. Require exit zero, `ok: true`, every selector's exact expected count and
   `runtime.applied: true` for generated variants. Baseline console errors are
   reported separately; explain pre-existing errors, do not hide new ones.
2. **Open every control and variant screenshot**, viewport and full page.
   Confirm intended edits, readable contrast, no obstruction, no horizontal
   scrolling and no missing controls. A script exit alone is not visual QA.
3. Check original destinations, keyboard focus and accessible names; inject the
   same JS twice and confirm one style and one inserted block per target. Check
   a delayed target and DOM replacement. Automated regressions cover the template,
   not every site-specific interaction. Do not submit forms or buy anything.
4. Fix selectors, copy or layout in the spec, render a new revision and repeat
   both previews. Do not call an unresolved failure a passing test. If blocked
   by access or anti-bot protection, state that the bundle is unverified and
   do not label it ready to launch.

After local QA, retain unchecked platform QA items in the brief. Configure actual
platform targeting, sticky assignment, consent and metrics in staging before
production. Never deploy or start the experiment without user approval.

## 5. Suite mode

`/cro build-test suite <url> <ACTION-PLAN.md>` selects 3-5 non-duplicate,
evidence-backed findings for READY sites. Gate before code and verify each test
independently. Write `tests/<id>/` per test plus `<workspace>/index.md` with:

| ID / source finding | Hypothesis | Primary metric | Duration | Dependencies / order | Desktop / mobile QA | Bundle |
|---|---|---|---|---|---|---|

Order tests that touch the same audience or elements sequentially, not in
parallel. Recompute readiness for different target pages and never split the
same traffic among 3-5 concurrent tests while retaining the original durations.
Record screenshot judgments in each bundle's `visual-review.md`, including paths
and remaining platform QA. Render the index from the bundles:

```bash
"<CRO_SCRIPTS>/cro-py" ../../cro-build-test/scripts/render_index.py "<workspace>/tests" --output "<workspace>/index.md"
```

The index links briefs, readiness, preview reports and visual reviews, and exits
nonzero for blocked previews. The suite is not complete until each selected test
has passing previews and visual review. If fewer than three defensible READY
candidates exist, report the shortfall rather than padding the suite.

LIMITED overrides the requested suite size: at most two research-backed big-swing
candidates, run sequentially over the year, each 6-8 weeks. NOT_TESTABLE produces
only the fix/research plan. Never fabricate traffic or inflate a change to get
around the gate.

## Final self-review and handoff

- Does every site claim have evidence, including policy conditions?
- Does the verdict permit the change, MDE and duration? Is an assumed baseline
  clearly provisional, including in the suite index?
- Does every targeted selector appear in the CRO_TEST manifest with exact counts?
- Do both preview reports pass, and have all eight screenshots been opened?
- Are analytics suggestions consent-aware, deduplicated and free of PII? Attribute
  the existing purchase/lead event, do not count CTA clicks as the business goal.
- Is every CSS selector scoped to this experiment? No framework, global reset,
  permanent DOM polling, duplicate listeners or undocumented hidden dependencies?
- Are remaining platform QA checks honestly unchecked, with rollback instructions?
- Does any sentence promise a client lift? Remove it. Plain English, no em dashes.

Return the verdict, bundle/index path, preview status and remaining platform QA.
Do not claim a winner, live deployment or production validation from local previews.
