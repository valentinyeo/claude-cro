#!/usr/bin/env bash
# G gate: run the slides skill tests (unittest exit code decides, pipefail on).
set -euo pipefail
exec bash "$(dirname "$0")/run_skill_tests.sh" skills/cro-slides/tests SLIDES
