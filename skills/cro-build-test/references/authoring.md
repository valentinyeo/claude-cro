# Authoring and integration

## Structured inputs

`assets/test.example.json` is a demonstrative Allbirds hypothesis, not a traffic
estimate or launch recommendation. Use current site evidence for real work.

- `id`: unique lowercase slug, starting with a letter, at most 60 characters.
- `baseline_status`: `CONFIRMED` or `ASSUMED`; record the source in `rationale`.
- `big_swing`: a boolean, true only for a genuinely substantial, research-backed
  change. A flag cannot turn a button tweak into a big swing; review the scope.
- `mde_relative_pct`: smallest relative effect worth resolving, not an expected
  lift. The readiness calculator supplies duration and sample per arm.
- `target`: exact `origin` without trailing slash and exact `pathname`. Query
  strings are ignored. Subdomains and trailing slashes must match deliberately.
- `evidence`: page quotes, selectors, script numbers, screenshots and audit ids.
- `primary_metric`: include denominator, attribution window and source. Use the
  same visitor/session unit as the calculator and platform assignment. Record
  delayed conversions after enrollment closes before final analysis.
- `guardrail_metrics`: definitions, sources, thresholds and stop/decision rules.
- `stop_rules`: experiment-specific safeguards in addition to fixed defaults.
- `qa_checklist`: experiment-specific checks. Rendering never marks them done.
- `click_selector`: a declared change selector for optional CTA instrumentation.
- `timeout_ms`: 100-60000, default 10000. MutationObserver is disconnected at the
  timeout, including after successful application. Platform page activation must
  handle route changes and later SPA navigation; the generated code is one page
  activation, not a universal SPA router.

## Changes

Each change has `selector`, positive exact `count`, `action` and string `value`:

| Action | Value | Caution |
|---|---|---|
| `set_text` | New visible text | Use on a leaf label. Replaces child nodes, so do not target an interactive container. |
| `set_attribute` | Attribute value, plus `attribute` field | Preserve destinations, semantics and consent. No inline event attributes. |
| `insert_after` | Reviewed static HTML | Adds one marked wrapper per target. Check grid/flex layout and wrapping. |
| `replace_html` | Reviewed static HTML | Only a deliberate noninteractive subtree redesign. Existing child listeners are lost. |

Selectors must remain matchable after the edit. Do not target an attribute that
you remove, text that you replace, or a subtree destroyed by an earlier change.
All selector counts must match before any mutation starts. Multiple changes may
address the same element, but do not combine conflicting operations.

Static HTML is trusted author input, not a sanitization boundary. Never embed
tracking code, scripts, inline handlers or user-controlled strings in a fragment.
Keep accessible structure and original controls intact. Text uses `textContent`.
The renderer escapes HTML script terminators in its JSON, allowing the generated
JS to be put in a script tag without closing that tag accidentally.

`css` must scope **every selector**, including each comma-separated selector and
selectors inside media queries, with `[data-cro-<id>]`. The renderer checks for
the scope marker; author review is responsible for every rule. Targeted nodes
and inserted wrappers receive that marker. Use `data-cro-insert` to distinguish
the wrapper. Never use global body, button, input or reset rules.

## Preview contract

`preview_variant.py` requires a JSON comment at the start of the variant:

```javascript
/* CRO_TEST {"id":"example","selectors":[{"selector":"#hero-cta","count":1}],"timeout_ms":10000} */
```

List every targeted selector, not just the first. Exact counts detect ambiguous
selectors as well as missing ones. Hand-authored variants can use the same
manifest. Generated variants additionally expose
`window.__croTests[id] = {applied, errors, timedOut}`; never fake that state.
The preview waits for application and exact selector counts, reports console
errors and browser exceptions by phase, then captures control and variant on
the same loaded page. Async exceptions during the observed variant window fail.
A bounded preview cannot prove absence of exceptions forever.

Desktop is 1440x900. Mobile uses Playwright's iPhone 13 profile in Chromium.
The CLI supports `--output <directory>`, `--timeout <seconds>` for navigation,
and `--settle <seconds>` for post-load and post-application rendering. The
manifest bounds selector/application waiting independently. Repeat
`--dismiss-selector '<close-or-reject-selector>'` to click inspected overlay
controls before both captures. For iframe controls use
`'<iframe-selector>::frame::<button-selector>'`. Missing requested controls fail
rather than being silently ignored. Dismissals are recorded; do not accept
consent or submit transactional actions just to clear a screenshot.
HTTP(S) host checks
reject private addresses for the initial URL and intercepted network requests.
This is browser QA, not an isolation sandbox for untrusted variant code.

Viewport and full-page images are captured for both arms. Full-page capture does
not guarantee every lazy image has loaded. If a target is below the fold, inspect
and adapt the capture with deliberate scrolling rather than mistaking placeholders
for the real page. Dynamic content can change between control and variant images;
attribute changes only to the authored operations, not to animation or live data.

## Platforms and goals

Paste `variant.js` into the variation custom-JS field in VWO, Convert, Optimizely,
GrowthBook or AB Tasty, after platform assignment and page activation. For a
custom integration, wrap it in a script tag inside the assigned-arm branch.
The script does not choose an arm, install a platform SDK or manipulate cookies.
The generated `variant.css` is a reference copy of the embedded CSS. Do not paste
both CSS copies into separate platform fields unless you remove one injection.

`goals.js` returns without doing anything until the platform provides a real
`assignedVariant` of `control` or `variant`. Call the snippet after consent and,
for variant, after `applied` becomes true. Adapt the callback to the platform's
exposure lifecycle. The snippet deduplicates exposure and click listeners within
the current page. Session/visitor deduplication belongs to the analytics design.

Suggested GA4 events are `cro_experiment_view` and `cro_variant_click`, with
`experiment_id` and `variant_id` parameters. Register custom dimensions, use
consistent definitions across both arms and attribute existing `purchase`,
`generate_lead` or `sign_up` events to persistent assignment. Do not duplicate an
existing business conversion event or send personal information. A CTA click is
secondary, not proof of increased revenue. Confirm that GA4 consent and blockers
do not bias reporting; platform-assigned visitors remain the intent-to-treat
primary denominator even if some variant executions fail.

Preview bypasses CSP solely for local injection. Test the actual platform's CSP,
consent, audience rules, event deduplication, sample balance and conversion join
in staging. Pausing the platform plus a full reload removes mutations and styles;
it does not undo an order or other server-side action. Production activation and
analysis are outside the generator and require explicit owner approval.
