# slides.json format

`build_slides.py` consumes one JSON object, not Markdown. All text is escaped.
Image paths are local files resolved relative to slides.json. No remote image
requests or fonts are needed. Supported image types: PNG, JPEG, GIF, WebP.
Use an exported PNG for an SVG logo. Keep confidential images out of public repos.

## Deck fields

| Field | Type | Meaning |
|-------|------|---------|
| `site` | string, required | Audited business/domain, shown on every slide |
| `consultant` | object, required | `name`, `site`, `contact`, all non-empty strings, shown in footer |
| `mode` | string | `PITCH` (default) or `CLIENT`; CLIENT rejects offers |
| `title` | string | Browser/PDF document title; defaults to site + Conversion audit |
| `brand` | string | CSS `--brand`, six-digit hex color; default `#21594e` |
| `logo` | string | Optional local logo image path |
| `slides` | array, required | 1-30 slide objects; normally at most 12-15 |

Consultant identity, contact links and all prices come from the input, never
from the renderer. Use a dark brand color with good contrast on white; brand
is used for buttons, headings and callouts. The renderer checks color syntax,
not contrast. All listed slide fields below are required unless marked optional.
Unknown extra properties are ignored. Strings must be non-empty where required.
Text is plain text: Markdown, HTML and inline links are not interpreted.

Each slide has `type` and `title`. Optional `source` adds a small source line
above the footer. Use short source citations, not entire report paragraphs.
The schema validates structure, bounds, score math and CLIENT offers; the agent
must verify evidence, correct readiness scope, non-sales CLIENT copy and story.

## Slide types

### bottom-line

Exactly three sentences, one array entry per sentence. Put this first.

```json
{"type":"bottom-line","title":"Let shoppers see the product first","sentences":["The signup prompt covers the first product view.","That may interrupt browsing before shoppers see what is different.","Start by reviewing prompt timing with customers."],"source":"FULL-AUDIT.md: Bottom line"}
```

### title

`subtitle`: scope/date. Optional `image` and `image_alt` for a supporting capture.
A cover is optional; the opening should still be the bottom line.

```json
{"type":"title","title":"A clearer path to the first order","subtitle":"Initial homepage review | 15 October 2026","image":"desktop.png","image_alt":"First homepage visit"}
```

### score

`overall`: 0-100, matching the rounded weighted sum (tolerance 0.51).
`categories`: 1-8 objects with `name`, `score` (0-100), `weight` (0-100).
Weights total 100 within 0.1. `evidence`: source/limits for the scoring.
Reuse the existing audit and scoring.md, not this illustrative two-category mix.

```json
{"type":"score","title":"Where this review found friction","overall":65,"categories":[{"name":"UX","score":60,"weight":50},{"name":"Copy","score":70,"weight":50}],"evidence":"Illustrative score only; FULL-AUDIT.md contains the real audited weights."}
```

### test-readiness

`verdict`: `READY`, `LIMITED` or `NOT_TESTABLE`. `status`: `CONFIRMED` or
`ASSUMED`. `baseline`: conversions/month, conversion rate, traffic share if
relevant, and the source/assumption. `evidence`: cite readiness.txt and its
computed minimum detectable lift or duration. The renderer adds a fixed,
plain-language explanation of whether A/B testing or research fits.

```json
{"type":"test-readiness","title":"Research before small experiments","verdict":"NOT_TESTABLE","status":"ASSUMED","baseline":"Illustration: 80 orders/month at 2% conversion. Not the site's private data.","evidence":"readiness.txt: NOT_TESTABLE. Confirm the baseline before setting the program."}
```

### finding

`image`: screenshot/crop path. Optional `image_alt` defaults to the problem.
`problem`, `evidence`, `why`, `fix`: four short paragraphs. Evidence must cite
what is visible or measured. `why` is a plausible cost to the shopping decision,
not an assertion that lost revenue was measured. `callouts`: 1-4 objects with
`x`, `y`, `w`, `h`, `label`. Coordinates are percentages from the top-left of
this exact image, not pixels. Width/height must be positive, and the box must
fit within 0-100 on each axis. Numbers are generated in array order. Labels
appear in the caption, so do not rely on tiny screenshot copy alone.

```json
{"type":"finding","title":"Give the product room to speak","image":"desktop.png","problem":"A signup overlay covers the hero.","evidence":"desktop.png: centered email prompt above the product imagery.","why":"A new shopper may have to dismiss a request before seeing a reason to buy.","fix":"Review delaying the request until after product exploration.","callouts":[{"x":29,"y":11,"w":42,"h":78,"label":"Signup overlay"}],"source":"FULL-AUDIT.md: H-1; desktop.png"}
```

Do not use these illustrative coordinates without inspecting your own image.
For long mobile captures, crop the relevant region, cite original file + crop
bounds, and position boxes against the crop. The renderer preserves image
aspect ratio. It does not edit or crop the evidence for you.

### before-after

`before`, `after`: two image paths. `before_label`, `after_label`: explicit
captions. `evidence`: origin, mockup status and what (if anything) was measured.
Both panels preserve image aspect ratios. Before/after is not automatically
proof of an improvement. Do not call a proposed concept a shipped result.

```json
{"type":"before-after","title":"A direction to explore","before":"desktop.png","after":"concept.png","before_label":"Current captured page","after_label":"Proposed concept, not a measured result","evidence":"Current: desktop.png. Concept is an untested illustration based on H-1."}
```

### strengths

`items`: 1-6 short strings. Include evidence within each item or in `source`.

```json
{"type":"strengths","title":"Keep these useful signals","items":["The product image makes the category clear (desktop.png).","The popup has a visible close control (mobile.png)."]}
```

### roadmap

`phases`: exactly three objects, each with `label` and `items` (1-4 strings).
Use 30/60/90-day labels. `measurement`: what will establish progress, with
baseline/causality limitations. Tailor activities to the existing verdict.

```json
{"type":"roadmap","title":"The first 90 days","phases":[{"label":"Days 1-30","items":["Verify order tracking and observe five shoppers."]},{"label":"Days 31-60","items":["Ship research-led fixes and repeat usability sessions."]},{"label":"Days 61-90","items":["Review baseline results and the next research priorities."]}],"measurement":"Track orders and conversion against the previous four weeks; record campaigns and seasonality. This comparison is directional, not causal proof."}
```

### offer (PITCH only)

`packages`: **one** package or **three** tiers. Each has `name`, `price`
(non-empty string with currency, billing basis, and any qualification),
`timeline`, `deliverables` (1-5 strings). Prices are input strings so retain
currency, taxes, one-time/recurring terms and approved commercial language.
`proof`: how this engagement will demonstrate progress, never a promised lift.
Tie testing scope to readiness. A NOT_TESTABLE offer sells research and fixes,
not an A/B backlog. If price is unknown, say it will be scoped after discovery.

```json
{"type":"offer","title":"A focused 90-day engagement","packages":[{"name":"Research and fixes","price":"Scope and price agreed after discovery","timeline":"First 90 days","deliverables":["Clear the signup and cookie prompts stacked over mobile product pages","Answer shipping time and returns next to Add to Cart","Two rounds of 5 shopper sessions on the product-to-cart path","Order baseline and a log of every shipped change"]}],"proof":"You see shipped changes, customer observations and measured orders. No guaranteed uplift."}
```

### next-steps

`items`: 1-4 strings. Optional `url` enables a button and requires `label`.
Allowed URL schemes: https, http, mailto, tel. For CLIENT use approvals, owners
and the next work session, not a booking pitch. Contact details remain in the
footer even when there is no button.

```json
{"type":"next-steps","title":"Choose the first priority together","items":["Confirm the order baseline.","Agree the first customer task to investigate."],"url":"https://example.org/book","label":"Book a discovery call"}
```

### appendix

`items`: 1-6 strings. Brief remaining issues, evidence sources and audit gaps.
Local report filenames are text references, not embedded reports or links.
The deck is self-contained visually; referenced audit files remain separate.

```json
{"type":"appendix","title":"Sources and limits","items":["FULL-AUDIT.md: complete evidence and scores.","ACTION-PLAN.md: remaining work.","readiness.txt: calculation and assumptions.","No private analytics or checkout review."]}
```

## Minimal complete input and commands

```json
{"site":"example.org","mode":"CLIENT","consultant":{"name":"Supplied consultant name","site":"https://consultant.example","contact":"supplied@example.org"},"brand":"#21594e","slides":[{"type":"bottom-line","title":"Focus the first round","sentences":["State an observed problem with a source.","Explain its possible cost without promising lift.","Name the first specific action."],"source":"FULL-AUDIT.md: Bottom line"}]}
```

```bash
"<CRO_SCRIPTS>/cro-py" build_slides.py /path/to/slides.json --embed --check --render
"<CRO_SCRIPTS>/cro-py" build_slides.py /path/to/slides.json -o /path/to/deck.html --no-embed --check --render /path/to/previews
```

Flags: positional JSON; `-o`/`--output` defaults to `deck.html` beside it;
`--embed` defaults on; `--no-embed` copies content-hashed images into
`<output-stem>-assets/` beside the HTML. `--render [DIR]` uses Playwright to
screenshot each slide, default `<output-stem>-render/`. `--check` checks at
1440x900 and 375x812; when combined with render, phone PNGs go in `DIR/phone/`.
An error exits 1. Successful checks print PASS; this is not a visual endorsement.
Building alone uses only the Python standard library. Browser checking/rendering
uses the pack's installed Playwright and Chromium. No new dependency is required.
