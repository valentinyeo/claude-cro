#!/usr/bin/env bash
# Synthetic traffic, offline: real traffic CSV -> templates -> scripted visitors walk a local
# fixture shop in Chromium -> report. Checks conversion at checkout, the pay-button refusal,
# tracker blocking and that planted friction reaches the ranked report.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${CRO_TEST_PY:-$HOME/.claude/skills/cro/.venv/bin/python}"
S="$ROOT/skills/cro/scripts/synthetic.py"
F="$ROOT/tests/fixtures/synthetic-shop"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
SITE="file://$F/index.html"

"$PY" "$S" templates "$F/traffic.csv" -o "$T/t.json" | grep -q "2 templates (CONFIRMED)"
"$PY" "$S" run "$SITE" --templates "$T/t.json" --visitors 2 --out "$T/a" --backend replay \
  --replay "$F/replay-checkout.json" --concurrency 2 >"$T/a.log"
"$PY" "$S" run "$SITE" --templates "$T/t.json" --visitors 1 --out "$T/b" --backend replay \
  --replay "$F/replay-pay.json" >"$T/b.log"
if "$PY" "$S" run "$SITE" --templates "$T/t.json" --visitors 11 --out "$T/c" --backend replay >/dev/null 2>&1; then
  echo "11 visitors ran without --yes"; exit 1
fi

"$PY" - "$T" <<'EOF'
import json, sys, pathlib
T = pathlib.Path(sys.argv[1])
a = [json.loads(p.read_text()) for p in sorted((T / "a/visitors").glob("v*/visit.json"))]
assert len(a) == 2, f"expected 2 visits, got {len(a)}"
assert {v["device"] for v in a} == {"mobile", "desktop"}, "both traffic segments should be visited"
for v in a:
    assert v["stage"] == "checkout" and v["converted"], (v["id"], v["stage"], v["end_reason"])
    assert v["atc"], f"{v['id']}: add to cart not detected"
    assert v["trackers_blocked"] >= 1 and v["trackers_allowed"] == 0, "tracker not blocked"
    shots = [e["screenshot"] for e in v["log"] if e["screenshot"]]
    assert len(shots) >= 4 and all((T / "a/visitors" / v["id"] / s).stat().st_size > 1000 for s in shots)
b = json.loads(next((T / "b/visitors").glob("v*/visit.json")).read_text())
assert b["refused_pay"] and b["converted"], b["end_reason"]
pay_step = [e for e in b["log"] if e.get("element_label") == "Pay now"]
assert pay_step and pay_step[0]["result"].startswith("refused"), "pay button was not refused"
rep = (T / "a/SYNTHETIC-REPORT.md").read_text()
cl = json.loads((T / "a/clusters.json").read_text())
assert cl["clusters"][0]["category"] == "overlay_popup" and cl["clusters"][0]["visitors"] == 2, cl["clusters"][0]
assert "Discount popup covers the whole homepage" in rep and "No delivery time" in rep
assert "| checkout | 2 | 100% |" in rep, "funnel row missing"
print("ok")
EOF
echo "SYNTHETIC-E2E PASS"
