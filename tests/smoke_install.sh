#!/usr/bin/env bash
# Fresh install into a throwaway HOME, then run every script through the cro-py wrapper.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REAL_HOME="$HOME"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
export PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-$REAL_HOME/.cache/ms-playwright}"
export UV_CACHE_DIR="${UV_CACHE_DIR:-$REAL_HOME/.cache/uv}"
HOME="$T" bash "$ROOT/install.sh" >"$T/install.log" 2>&1 || { tail -20 "$T/install.log"; echo "install failed"; exit 1; }
C="$T/.claude/skills/cro/scripts/cro-py"
W="$T/w"; mkdir -p "$W"
"$C" doctor.py --quick | grep -q "DOCTOR OK"
"$C" test_readiness.py --conversions 300 --cvr 2 | grep -q "Verdict: LIMITED"
"$C" fetch_page.py https://example.com --output "$W/p.html" --json > "$W/f.json" || { cat "$W/f.json"; exit 1; }
"$C" fetch_page.py https://example.com --render --output "$W/r.html" --json | grep -q '"fetched_with": "browser"'
"$C" parse_cro.py "$W/r.html" --json > "$W/e.json"
"$C" capture_screenshot.py https://example.com -o "$W/s.png" --mobile >/dev/null
test -s "$W/s.png"
"$C" pagespeed.py https://example.com --local --json | grep -q '"LCP"'
"$C" analyze_funnel.py https://example.com https://example.com >/dev/null
"$C" crawl_site.py https://example.com --json | grep -q '"home"'
if "$C" fetch_page.py http://127.0.0.1/ >/dev/null 2>&1; then echo "private address was not blocked"; exit 1; fi
test -f "$T/.claude/agents/cro-ux.md"
echo "SMOKE PASS"
