---
name: cro-wireframe
description: >
  Design evidence-led low-fidelity fixes for CRO findings with before/after
  wireframes at mobile and desktop sizes. Use for /cro wireframe, "wireframe
  these findings", "show the CRO fix", "before and after layout", or "design
  the conversion fix".
argument-hint: "<url> [finding ids]"
disable-model-invocation: true
allowed-tools: Read, Write, Grep, Glob, Bash, WebFetch
---

# CRO Wireframes

Design the fix before implementation. Work solo. The deliverable is a faithful
before, a focused after, and a finding-linked visual comparison, not a new audit
or a promise of better conversion rates.

Resolve `CRO_SCRIPTS` with `cd "${CLAUDE_SKILL_DIR}/../cro/scripts" && pwd`.
Write that absolute path literally in every command. Run scripts through
`"<CRO_SCRIPTS>/cro-py" <script>.py ...`. Do not send `wireframe` to a script.

## 1. Read findings and evidence

1. Parse the URL and optional finding IDs (space- or comma-separated, such as
   `H-1 H-3`). Look for the matching `cro-audit-<domain>-*` workspace, especially
   `ACTION-PLAN.md`, `FULL-AUDIT.md`, `page.html`, `elements.json`, and screenshots.
   Confirm the evidence is for this URL and state, not another page or variant.
2. Read `${CLAUDE_SKILL_DIR}/../cro/references/scoring.md` for priority/evidence
   rules and `business-types.md` for the business type and conversion goal.
3. Select the 1-3 highest-priority page sections from the requested findings,
   or from the audit if IDs are omitted. Preserve finding IDs. If explicit IDs
   span more sections, deliver the top 3 and name the deferred IDs and reason.
4. If no audit exists, capture the page and create up to 3 clearly labeled
   **provisional findings** with IDs `WF-1`, etc., each with an Evidence line.
   These are design observations, not a scored audit. If an explicit ID cannot
   be found, ask for that finding rather than inventing its contents.
5. Read the relevant `proven-tests-ecommerce.md`, `proven-tests-b2b.md`, or
   `proven-tests-general.md` under `../cro/references/`. Cite pattern IDs in
   the design notes as **industry-reported, unverified patterns**. Choose for
   relevance to this evidence, not reported lift size. Never promise a lift.

Capture missing or stale evidence once into the new workspace:

```bash
"<CRO_SCRIPTS>/cro-py" fetch_page.py <url> --render --output "<W>/evidence/page.html" --json > "<W>/evidence/fetch.json"
"<CRO_SCRIPTS>/cro-py" capture_screenshot.py <url> -o "<W>/evidence/mobile.png" -W 390 -H 844 --full-page
"<CRO_SCRIPTS>/cro-py" capture_screenshot.py <url> -o "<W>/evidence/desktop.png" -W 1440 -H 900 --full-page
```

View both screenshots. If a bot wall covers the site, stop, name the gap and
request a usable capture. Never design from a block page. If consent, location
or signup overlays cover the hero, preserve the initial capture, dismiss them
with normal user controls if possible, then capture again and record the exact
state/actions. Do not silently delete overlays from the evidence or wireframe.
Existing screenshot script `--mobile` uses 375px, so use explicit dimensions
above for the 390px baseline. Record whether browser emulation was used.

## 2. Define the focused design

Create `cro-wireframe-<domain>-<YYYY-MM-DD>/` (called `W`) with this layout:

```text
W/
  evidence/                  # source screenshots, HTML, fetch metadata
  assets/wireframe.css        # copy from this skill's assets/
  before.html
  after.html
  annotations.json
  DESIGN-NOTES.md
  renders/
    before-mobile.png        # 390 x full page, viewport height 844
    after-mobile.png
    before-desktop.png       # 1440 x full page, viewport height 900
    after-desktop.png
    before-after-mobile.html # self-contained side-by-side + side legend
    before-after-mobile.png
    before-after-desktop.html
    before-after-desktop.png
    render-manifest.json     # inputs, annotation mapping, dimensions, controls
```

Read `${CLAUDE_SKILL_DIR}/references/components.md`. Copy
`${CLAUDE_SKILL_DIR}/assets/wireframe.css` to `W/assets/`. Keep all CSS and
images local to each input HTML directory or its descendants. No network fonts,
remote images, JavaScript or live embeds. The renderer blocks those resources.

Write `DESIGN-NOTES.md` before drawing:
- URL, capture date, business type, main goal, viewport/state and evidence paths.
- Scope: the chosen 1-3 sections, finding IDs, priorities, Evidence lines and
  intended change. Name omitted sections and gaps. Section-only output must be
  labeled as such, not passed off as a full homepage reconstruction.
- Each proposed headline, subhead, CTA, trust or policy statement, its source
  quote/element or number, and whether it is unchanged or proposed copy.
- Pattern ID and file used, labeled industry-reported, unverified. No lift
  forecast. Do not invent a new guarantee, stock count, price, logo or review.
- Any proposed claim not supported by business evidence is removed or listed
  as an approval question outside the customer-facing wireframe.

No traffic estimate is required just to draw. Preserve the audit readiness
verdict. If recommending an experiment, first follow
`../cro/references/test-readiness.md`; otherwise recommend a usability check,
not an unsupported A/B backlog.

## 3. Write before.html and after.html

- Both are standalone semantic HTML documents with `lang`, UTF-8, viewport
  metadata and `<link rel="stylesheet" href="assets/wireframe.css">`.
- **Before:** faithfully mirror the current screenshot's section order,
  header height, image/text proportions, alignment, CTA placement and copy at
  both sizes. Use the site's real words, not lorem ipsum. Preserve defects.
  Grayscale labeled image boxes are appropriate; note that these are not
  pixel-perfect brand mockups. Use page-specific CSS when the kit defaults
  would “fix” the before. Do not replace the site with a generic template.
- **After:** apply only the selected fixes. Keep the original business offer
  and relevant constraints. Use realistic proposed copy backed by evidence.
  One primary CTA per viewport, with a clear next step. Secondary choices
  stay neutral. Do not put add-to-cart on a homepage without a chosen product.
- Grayscale surfaces with one accent color for primary CTAs. Red numbered
  markers are review annotations only. Do not cover text or controls with them.
- Add `<span class="wf-marker" data-annotation="1" aria-label="Change 1">1</span>`
  at each changed section. One marker per number per page. Before markers are
  optional. Every annotation number must occur in after.
- Write structured `annotations.json`: a list of objects with positive integer
  `number` and nonempty strings `finding_id`, `change`, `evidence`. See the
  reference for the exact format. Multiple changes may reference one finding.
  Do not hand-build comparison pages or duplicate the legend in source pages.

## 4. Render, view, fix, re-render

```bash
"<CRO_SCRIPTS>/cro-py" render_wireframe.py "<W>/before.html" --after "<W>/after.html" --annotations "<W>/annotations.json" --output "<W>/renders"
```

The script deterministically renders full-page PNGs at 390 and 1440 CSS pixels,
then generates self-contained before/after HTML and PNG comparisons. The side
legend maps numbered changes to findings and evidence. Images are embedded in
the comparison HTML, so it can be moved without breaking asset paths. A single
HTML can also be rendered without `--after`/`--annotations`, producing
`<stem>-mobile.png` and `<stem>-desktop.png` plus a manifest.

Open **all four page PNGs and both comparison PNGs** with the image viewer.
Compare before against the source screenshot, not just against after. Read
`render-manifest.json` for measured control dimensions and page overflow.

Self-review as a strict reviewer. Record pass/fix evidence in DESIGN-NOTES:
- [ ] Before layout and exact copy match both source captures; state and any
      scope truncation are explicit. Missing evidence is called a gap.
- [ ] After has one visible primary CTA per viewport. Header or footer signup
      buttons do not compete. A sticky action does not duplicate an in-view CTA.
- [ ] At 390 x 844, the product value proposition and primary action are above
      the fold with the real header accounted for. Check their PNG positions.
- [ ] Every after tap target, including navigation and icon buttons, is at
      least 44 x 44 CSS pixels. Inspect measured controls in the manifest.
- [ ] Text contrast is at least 4.5:1, or 3:1 for large text. Controls and focus
      indicators have 3:1 contrast. Kit blue/white and dark text/light backgrounds
      meet this; recheck custom colors, opacity and image overlays numerically.
- [ ] No horizontal overflow, overlapping text, tiny legends, clipped CTAs or
      hidden copy at either width. Annotations do not obstruct the design.
- [ ] Claims, prices, ratings, logos and policy terms have business evidence.
      Proposed wording is labeled in notes. No invented proof or promised lift.
- [ ] Each marker maps to the right finding in the side legend. Pattern
      citations are industry-reported, not evidence of a client-site result.

Fix failed items in source HTML/JSON/CSS, re-render and reopen affected PNGs.
Do not “fix” the before's genuine site defects. Distinguish those from drawing
mistakes. If source evidence cannot be recovered, stop with that gap rather
than fabricate the before. Report unresolved limitations explicitly.

## 5. Handoff and slide reuse

Reply with the selected finding IDs, changed sections, workspace path and any
remaining approval questions. These are proposals requiring implementation and
validation, not a measured win.

For `cro-slides` **before-after** slides, reuse the matching device pair:
`renders/before-mobile.png` + `renders/after-mobile.png`, or the desktop pair.
Pass finding IDs and annotation text from `annotations.json` as the caption.
Keep both images at the same scale and top-align them. Use the comparison PNG
only as a whole comparison panel, not stretched into a single phone frame.
For very tall output, crop both images to the same section boundaries and keep
original full-page files. Do not mix the live branded screenshot with an after
wireframe without explicitly labeling the differing fidelity.
