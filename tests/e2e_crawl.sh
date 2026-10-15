#!/usr/bin/env bash
# Live check: the crawler finds product and collection pages on a real Shopify store,
# and the audit skill wires in the swarm (per-page lenses, personas, skeptic).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${CRO_TEST_PY:-$HOME/.claude/skills/cro/.venv/bin/python}"
OUT="$("$PY" "$ROOT/skills/cro/scripts/crawl_site.py" https://www.allbirds.com --json)"
echo "$OUT" | "$PY" -c 'import json,sys; d=json.load(sys.stdin)["pages"]; assert {"home","product","collection"} <= set(d), d'
A="$ROOT/skills/cro-audit/SKILL.md"
for k in crawl_site.py cro-persona cro-skeptic "per page"; do grep -q "$k" "$A" || { echo "cro-audit missing: $k"; exit 1; }; done
test -f "$ROOT/agents/cro-persona.md" && test -f "$ROOT/agents/cro-skeptic.md"
echo "CRAWL PASS"
