#!/usr/bin/env python3
"""Render a reviewed test.json plus calculator readiness.json into a test bundle.

cro-py ../../cro-build-test/scripts/render_test.py test.json --readiness readiness.json --output tests/id
No network calls. Site evidence, selectors and hypothesis are authored by the model.
"""

import argparse
import json
import math
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR.parents[1] / "cro" / "scripts"))
from test_readiness import assess  # noqa: E402


def require(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty string")
    return value


def string_list(spec, key):
    value = spec.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"{key} must be a nonempty list")
    return [require(item, key) for item in value]


def render(spec, readiness, output):
    test_id = spec.get("id", "")
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,59}", test_id):
        raise ValueError("id must be a lowercase slug, starting with a letter")
    inputs = readiness["inputs"]
    calculated = assess(inputs["conversions_per_month"], inputs["cvr_pct"], inputs["traffic_share"])
    if readiness["verdict"] != calculated["verdict"] or readiness["by_duration"] != calculated["by_duration"]:
        raise ValueError("readiness.json does not match test_readiness.py; rerun the calculator")
    verdict = calculated["verdict"]
    if verdict == "NOT_TESTABLE":
        raise ValueError("NOT_TESTABLE: ship an evidence-backed fix and use the research plan; traffic cannot resolve a useful A/B result")
    if verdict == "LIMITED" and spec.get("big_swing") is not True:
        raise ValueError("LIMITED only permits research-backed big-swing variants, not small tweaks")
    mde = spec.get("mde_relative_pct")
    if isinstance(mde, bool) or not isinstance(mde, (int, float)) or not math.isfinite(mde) or mde <= 0:
        raise ValueError("mde_relative_pct must be a positive planning threshold, not a promised lift")
    rows = [row for row in calculated["by_duration"]
            if row["weeks"] in ((6, 8) if verdict == "LIMITED" else (2, 4))
            and row["mde_relative_pct"] <= mde]
    if not rows:
        raise ValueError("This MDE is not detectable within the allowed duration; change the scope or do research")
    duration = rows[0]
    for key in ("title", "primary_metric", "audience", "baseline_status", "rationale", "click_selector"):
        require(spec.get(key), key)
    if spec["baseline_status"] not in ("CONFIRMED", "ASSUMED"):
        raise ValueError("baseline_status must be CONFIRMED or ASSUMED")
    hypothesis = spec.get("hypothesis", {})
    for key in ("if", "then", "because"):
        require(hypothesis.get(key), "hypothesis." + key)
    lists = {key: string_list(spec, key) for key in ("evidence", "guardrail_metrics", "stop_rules", "qa_checklist")}
    target = spec.get("target", {})
    parsed = urlparse(require(target.get("origin"), "target.origin"))
    if (parsed.scheme not in ("http", "https") or not parsed.netloc or parsed.username
            or parsed.password or parsed.path or parsed.query or parsed.fragment):
        raise ValueError("target.origin must be an http(s) origin without a trailing slash")
    if not require(target.get("pathname"), "target.pathname").startswith("/"):
        raise ValueError("target.pathname must start with /")
    timeout = spec.get("timeout_ms", 10000)
    if type(timeout) is not int or not 100 <= timeout <= 60000:
        raise ValueError("timeout_ms must be 100..60000")
    changes = spec.get("changes")
    if not isinstance(changes, list) or not changes:
        raise ValueError("changes must be a nonempty list")
    selectors = []
    for change in changes:
        require(change.get("selector"), "change.selector")
        if type(change.get("count")) is not int or change["count"] < 1:
            raise ValueError("change.count must be a positive exact match count")
        if change.get("action") not in ("set_text", "insert_after", "replace_html", "set_attribute"):
            raise ValueError("Unsupported change.action")
        require(change.get("value"), "change.value")
        if change["action"] == "set_attribute":
            attribute = require(change.get("attribute"), "change.attribute")
            if not re.fullmatch(r"[a-zA-Z][\w:-]*", attribute) or attribute.lower().startswith("on"):
                raise ValueError("Invalid or executable attribute")
        item = {"selector": change["selector"], "count": change["count"]}
        if item not in selectors:
            selectors.append(item)
    # Click instrumentation is also a targeted selector, even when the variant does not edit it.
    if spec["click_selector"] not in [item["selector"] for item in selectors]:
        raise ValueError("click_selector must be one of the declared change selectors")
    css = spec.get("css", "")
    if not isinstance(css, str):
        raise ValueError("css must be a string")
    if css and f"[data-cro-{test_id}]" not in css:
        raise ValueError(f"Scope CSS rules with [data-cro-{test_id}]")
    manifest = {"id": test_id, "selectors": selectors, "timeout_ms": timeout, "runtime_required": True}
    config = {"id": test_id, "target": target, "timeout_ms": timeout, "changes": changes, "css": css}
    # Escape HTML parser terminators so the same JS is safe inside a generic script tag.
    dump = lambda value: json.dumps(value, ensure_ascii=True).replace("<", "\\u003c").replace("*/", "*\\u002f")
    template = (SCRIPT_DIR.parent / "assets" / "variant-template.js").read_text(encoding="utf-8")
    variant = template.replace("__MANIFEST__", dump(manifest)).replace("__CONFIG__", dump(config))
    bullets = lambda items: "\n".join("- " + item for item in items)
    brief = f"""# {spec['title']}

**Test ID:** {test_id}

## Hypothesis
**If** {hypothesis['if']}, **then** {hypothesis['then']}, **because** {hypothesis['because']}.

## Evidence
{bullets(lists['evidence'])}

## Test Readiness
**Baseline:** {inputs['conversions_per_month']:g} conversions/month, {inputs['cvr_pct']:g}% CVR, traffic share {inputs['traffic_share']:g}. **{spec['baseline_status']}**.
**Verdict:** {verdict}. {spec['rationale']}
**Duration:** {duration['weeks']} full weeks, {duration['visitors_per_variant']:,} eligible visitors per arm.
**Detectable lift:** {duration['mde_relative_pct']}% relative at this duration. Planning MDE: {mde:g}% relative, not a lift forecast.
**Design:** {calculated['assumptions']}. Persistent visitor assignment, one control and one variant. Run through complete weekly cycles and the full sample, whichever takes longer; if traffic falls short, stop inconclusive and re-plan rather than extending opportunistically.
{'**Provisional only:** ASSUMED baseline. Confirm analytics and rerun readiness before launch.' if spec['baseline_status'] == 'ASSUMED' else ''}

## Metrics
**Primary:** {spec['primary_metric']}
**Guardrails:**
{bullets(lists['guardrail_metrics'])}

## Audience and targeting
{spec['audience']}
**URL rule:** location.origin === {json.dumps(target['origin'])} && location.pathname === {json.dumps(target['pathname'])}. Query strings ignored; platform assignment and audience exclusions must match this rule.
**Split:** 50/50 eligible visitors. Do not overlap tests on these elements.

## Stop rules
- Do not stop early for significance or a promising trend. Use a fixed-horizon two-sided test, alpha 0.05, power 0.80.
- Stop immediately for broken purchase/signup flows, privacy problems, or a predefined safety guardrail breach. Roll back both code and platform assignment; record the incident, not a winner.
- At the predeclared horizon, report effect and confidence interval, sample-ratio mismatch checks and inconclusive results. A click improvement alone is not a purchase win.
{bullets(lists['stop_rules'])}

## QA checklist
- [ ] Desktop and mobile preview reports pass; open all control/variant screenshots.
- [ ] Exact selector counts, no variant JS exceptions, no layout overlap or horizontal scrolling.
- [ ] Repeated injection and late-loading DOM do not duplicate UI or listeners.
- [ ] Keyboard focus, accessible names, links, cart and checkout still work.
- [ ] Platform URL targeting, persistent assignment, consent, exposure and primary conversion attribution verified in staging.
- [ ] No simultaneous experiment edits these elements; control remains untouched.
- [ ] Pause the experiment and reload to verify rollback. SPA route changes need platform re-evaluation or a full reload.
{bullets(['[ ] ' + item for item in lists['qa_checklist']])}

## Files and deployment
`variant.js` includes its scoped CSS and unique style id. Paste it as variation JavaScript in VWO, Convert, Optimizely, GrowthBook or AB Tasty, or place it inside a generic script tag after platform assignment. Do not paste script tags into a custom-JS editor. `variant.css`, when present, is a readable copy, not an additional required injection.
`goals.js` is a suggestion, not installed analytics. Adapt it to platform assignment and existing consent; send exposure for both arms only after the variant has applied. Do not add another purchase event if one already exists.
Local preview bypasses CSP and does not prove live platform, consent or attribution behavior. Platform account QA remains unchecked until actually performed.
"""
    events = """// Suggestions only. Run inside the platform's assigned-arm callback after consent.
// Define assignedVariant as 'control' or 'variant' from the platform, never from the URL.
// For variant, call after window.__croTests[EXPERIMENT_ID].applied is true.
(function (assignedVariant) {
  'use strict';
  var id = __ID__;
  if (location.origin !== __ORIGIN__ || location.pathname !== __PATH__) return;
  if (assignedVariant !== 'control' && assignedVariant !== 'variant') return;
  if (typeof window.gtag !== 'function') return;
  var key = id + ':' + assignedVariant;
  var sent = window.__croGoalSuggestions = window.__croGoalSuggestions || {};
  if (sent[key]) return;
  sent[key] = true;
  var params = { experiment_id: id, variant_id: assignedVariant };
  window.gtag('event', 'cro_experiment_view', params);
  document.addEventListener('click', function (event) {
    if (event.target instanceof Element && event.target.closest(__SELECTOR__)) {
      window.gtag('event', 'cro_variant_click', params);
    }
  });
}(typeof assignedVariant === 'undefined' ? null : assignedVariant));
// Attribute the existing GA4 purchase / generate_lead / sign_up event to assignment.
// Register experiment_id and variant_id custom dimensions. Never send email or other PII.
"""
    for token, value in (("__ID__", test_id), ("__ORIGIN__", target["origin"]),
                         ("__PATH__", target["pathname"]), ("__SELECTOR__", spec["click_selector"])):
        events = events.replace(token, dump(value))
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError("Output is not empty; use a new revision directory to preserve prior evidence")
    output.mkdir(parents=True, exist_ok=True)
    for filename, text in (("test-brief.md", brief), ("variant.js", variant), ("goals.js", events),
                           ("test.json", json.dumps(spec, indent=2) + "\n"),
                           ("readiness.json", json.dumps(calculated, indent=2) + "\n")):
        (output / filename).write_text(text, encoding="utf-8")
    if css:
        (output / "variant.css").write_text(css + "\n", encoding="utf-8")
    return output


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("spec")
    ap.add_argument("--readiness", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    try:
        output = render(json.loads(Path(args.spec).read_text(encoding="utf-8")),
                        json.loads(Path(args.readiness).read_text(encoding="utf-8")), args.output)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Rendered test bundle: {output.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
