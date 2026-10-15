#!/usr/bin/env bash
# Run one sub-skill's own test folder with the skill's Python env, print "<LABEL> PASS" on success.
# Usage: run_skill_tests.sh <tests-dir> <LABEL>
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIR="$ROOT/$1"; LABEL="$2"
PY="${CRO_TEST_PY:-$HOME/.claude/skills/cro/.venv/bin/python}"
test -d "$DIR" || { echo "missing $1"; exit 1; }
ls "$DIR"/test_*.py >/dev/null 2>&1 || { echo "no test_*.py in $1"; exit 1; }
"$PY" -m unittest discover -s "$DIR" -p "test_*.py" -t "$ROOT" 2>&1 | tail -5
echo "$LABEL PASS"
