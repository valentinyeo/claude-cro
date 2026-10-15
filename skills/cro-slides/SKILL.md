---
name: cro-slides
description: >
  Turn a finished CRO audit workspace into a customer-facing HTML slide deck.
  Use for /cro slides, "audit presentation", "pitch deck from this audit",
  "present the audit", or "client audit slides". Includes a prospect pitch
  or a signed-client roadmap, screenshot callouts, PDF printing and visual QA.
argument-hint: "<audit-workspace> [--pitch|--client]"
disable-model-invocation: true
allowed-tools: Read, Write, Grep, Glob, Bash
---

# Audit slides

Explain what this business owner should do, why, and how we will know it helped.
Do not dump the audit into a presentation. Use plain English, not marketing
jargon. No promised conversion lift and no em dashes in prose.

`CRO_SCRIPTS` = the absolute path from
`cd "${CLAUDE_SKILL_DIR}/../cro/scripts" && pwd`.
Write that absolute path literally in each command. Run scripts as
`"<CRO_SCRIPTS>/cro-py" build_slides.py ...`.

## 1. Read the finished workspace

Read `FULL-AUDIT.md`, `ACTION-PLAN.md`, `readiness.txt`, `desktop.png`,
`mobile.png`, `mobile-full.png`, and optional `findings.json`. Open the images,
not just their filenames. Do not refetch a site or run another audit when the
workspace is already complete. If a required source is missing, ask for the
finished workspace or disclose the gap and omit unsupported claims. Do not
invent scores, findings, readiness inputs or private analytics.

Read `../cro/references/test-readiness.md` and `../cro/references/scoring.md`
when interpreting the verdict and score. Reuse the audited weights and total;
never introduce a new scoring system. A missing category remains missing.

The deck is about the audited site, not generic CRO advice. Every site claim
needs a screenshot reference, quoted page text, named element or script number.
A suspected effect on sales is a hypothesis: say "may make it harder to...",
not "this loses 20% of your orders". Separate observed facts from interpretation.

## 2. Choose the mode and inputs

Map `--pitch` to JSON `mode: "PITCH"`, and `--client` to `mode: "CLIENT"`.
Also accept `--mode PITCH|CLIENT` when supplied. These are skill arguments,
not builder CLI flags; the builder reads the mode from slides.json.

Default is **PITCH**, for a prospect who has not hired us yet, including people
found on Upwork, LinkedIn or the consultant's own site. **CLIENT** is for a signed
customer: audit results, decisions and roadmap, with no offer or sales CTA.
The builder rejects `offer` slides in CLIENT mode; you must also remove sales
language and booking links from other slides yourself.

Get consultant name, site and contact from the user or supplied project context.
Use the supplied logo and brand color if available. Get the offer's price and
scope from the user, never invent a real quote or hard-code consultant details.
If pricing is not set, use an explicit "Scope and price agreed after discovery"
price value, not a made-up number. Do not leave placeholder contact links in a
customer deliverable. Do not infer that a brand is our client.

## 3. Plan a short story, bottom line first

Aim for **12-15 slides maximum**, fewer if the evidence is thin. The JSON format
allows up to 30 for an explicitly requested longer deck, not as a default.
Read `references/slides-schema.md` before writing `slides.json` in the workspace.

PITCH sequence:

1. `bottom-line`: exactly three sentences. What is getting in the way, the
   opportunity, and what we should do first. This is the opening, not a cover.
2. Optional `title`: site, scope and audit date. Keep this short or omit it.
3. `score`: overall and category bars, with source and missing-data limits.
4. `test-readiness`: audited verdict, baseline, CONFIRMED/ASSUMED status, and
   what this means in everyday language. The renderer supplies that explanation.
4b. `tracking` (from findings.json `tracking`): `found` (what is measured
   today, duplicates and gaps in plain words, max 5) and `access` (the access
   we need, max 5). Always include it: it is how the next numbers get real.
5. Up to **five** `finding` slides, strongest first. One finding per slide.
   Show the actual site, explain the problem, evidence, possible sales friction,
   and a concrete fix. Do not inflate one issue into multiple findings.
6. `strengths`: what we will protect, with evidence.
7. `roadmap`: what we would do in days 1-30, 31-60 and 61-90; how to measure it.
8. `offer`: one focused package or three clearly different tiers, deliverables,
   timeline and supplied price. Explain why the scope matches this site's need.
   **Each deliverable names a problem shown earlier in this deck**, in the
   prospect's terms ("Remove the 3 popups stacked on mobile product pages",
   "Answer shipping times before checkout"), not generic service lines
   ("Prioritized audit fixes"). A prospect should recognise their own site in
   every bullet.
9. `next-steps`: a low-pressure next step and supplied call-booking/contact link.
10. `appendix`: other findings, sources and gaps. Keep it to six short items or
    link the local audit by filename in text. The audit holds the full detail.

CLIENT sequence uses the same evidence story, but **no offer**. Replace the sales
next step with approvals, named owners supplied by the user and the first work
session. A `before-after` slide is optional, not filler. Label an unshipped
concept "Proposed concept, not a measured result". Never imply a mockup is live.

The roadmap and offer must follow the existing readiness verdict:

- READY: fix known problems, verify analytics, research, then a regular A/B
  program. Use durations from the audit calculator, not a promised win cadence.
- LIMITED: usability research first; only large changes warrant 6-8 week tests,
  roughly 2-4 per year. A 90-day offer is not a promise of many completed tests.
- NOT_TESTABLE: usability research, session reviews, interviews/polls, shipped
  fixes and baseline tracking. **No A/B backlog or testing-program upsell.**
- ASSUMED baseline: verdict and program scope are provisional until verified.

For every mode, explain proof: verify goal tracking; record the baseline;
log what shipped; review customer observations and orders/revenue. Before/after
comparisons need matching windows and campaign/seasonality notes, and are
**directional, not causal proof**. A/B results need planned duration and uncertainty.

## 4. Write concise, evidence-led JSON

Use the schema exactly. All prose is rendered as text, not Markdown or HTML.
Keep titles under roughly 55 characters, finding paragraphs around 15-30 words
each, roadmap phases to 2-3 short items, and offers to 3-5 deliverables. These
are writing budgets, not a reason to cut vital qualifications. Put long detail
in the audit or appendix. Keep the headline at one or two lines.

Finding callouts are percentages of the **exact image file**, not the browser
viewport or slide. Open the screenshot and choose the element bounds visually.
For image width W and height H, use `x=100*left/W`, `y=100*top/H`,
`w=100*width/W`, `h=100*height/H`. Use 1-4 small boxes in reading order. Numbers
are generated in array order with a matching caption. Do not cover the evidence
with a huge box or put a callout on an unrelated element.

Prefer a tight crop when the relevant element is tiny in `mobile-full.png`.
Preserve the original; save the crop next to it, record its source and crop bounds
in `source`, and calculate coordinates against the crop. Do not stretch or alter
site evidence. Label any edited before/after illustration explicitly.

## 5. Build, render, inspect, fix, repeat

```bash
"<CRO_SCRIPTS>/cro-py" build_slides.py "<workspace>/slides.json" --output "<workspace>/deck.html" --embed --check --render
```

Default output is one offline HTML file with inline CSS, JS and base64 images.
`--no-embed` instead copies images into `deck-assets/`; deliver that folder with
the HTML. The embed setting is a builder flag, not a model argument.
`--check` uses Chromium at 1440x900 and 375x812 and fails on overflow, footer
collisions or undecodable images. `--render` writes every desktop slide to
`deck-render/slide-NN.png`; with `--check` it also writes `deck-render/phone/`.
An optional directory follows `--render` to change this destination.

**Open every rendered PNG**, desktop and phone. Do not rely on PASS alone.
Check each against the source, then fix JSON or crop choices and run the command
again. If browser tooling is unavailable, report that verification is blocked;
do not call an uninspected deck verified. Do not shrink everything until it fits.

Self-review, every slide:

- Can a business owner understand the headline and action without explanation?
- One clear point, generous space, calm hierarchy, no dense paragraphs?
- Is screenshot evidence large enough to read, undistorted, and unobscured?
- Do numbered boxes tightly surround the actual evidence and match captions?
- No text clipping, overlap, unreadable labels or footer collision?
- Are score, verdict and priorities faithful to the audit, with gaps visible?
- Are sales effects qualified, baselines labeled and concepts distinguished?
- Do scope, testing cadence and price match the verdict and supplied terms?
- PITCH ends in an offer and clear next step; CLIENT has no sales pitch?
- Phone slides scroll vertically if needed, without sideways scrolling?

Open `deck.html` and check arrow keys, previous/next buttons, click navigation
(left third goes back; elsewhere goes forward), and links. Home/End jump to
first/last. For PDF use Chrome Print > Save as PDF, CSS page size, no browser
headers/footers, backgrounds on and no custom margins. The print stylesheet
shows **all** slides, one 16:9 slide per page, regardless of the current slide.

## 6. Hand off

Give the HTML path, optional asset folder, render folder and mode. Note audit
gaps, assumed baselines, unresolved pricing or verification blockers explicitly.
The artifact is an initial audit explanation, not a guarantee of results.
