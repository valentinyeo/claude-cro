#!/usr/bin/env bash
# G7: evidence skill tests pass, the database validates, and it holds 25+ records,
# each with an http(s) source_url and a verification status.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${CRO_TEST_PY:-$HOME/.claude/skills/cro/.venv/bin/python}"
bash "$ROOT/tests/run_skill_tests.sh" skills/cro-research/tests EVIDENCE-UNIT >/dev/null
"$PY" "$ROOT/skills/cro/scripts/evidence.py" validate >/dev/null
"$PY" - "$ROOT/skills/cro/evidence/tests" <<'EOF'
import json, sys, pathlib
recs = [json.loads(p.read_text()) for p in pathlib.Path(sys.argv[1]).glob("*.json")]
bad = [r.get("id") for r in recs if not str(r.get("source_url", "")).startswith("http") or r.get("verification") not in ("verified", "unverified")]
assert len(recs) >= 25, f"only {len(recs)} records"
assert not bad, f"records missing source_url/verification: {bad}"
print(f"{len(recs)} records, {sum(r['verification'] == 'verified' for r in recs)} verified")
EOF
echo "EVIDENCE PASS"
