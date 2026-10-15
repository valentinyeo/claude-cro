#!/usr/bin/env bash
# The overhaul is on origin/master and installed into ~/.claude.
set -euo pipefail
cd "$(dirname "$0")/.."
git fetch -q origin master
git merge-base --is-ancestor HEAD origin/master || { echo "HEAD not on origin/master"; exit 1; }
test -x "$HOME/.claude/skills/cro/scripts/cro-py"
cmp -s skills/cro/SKILL.md "$HOME/.claude/skills/cro/SKILL.md" || { echo "installed router differs from repo"; exit 1; }
"$HOME/.claude/skills/cro/scripts/cro-py" doctor.py --quick | grep -q "DOCTOR OK"
echo "MERGED PASS"
