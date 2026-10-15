#!/usr/bin/env bash
# G gate: run the wireframe skill tests (unittest exit code decides, pipefail on).
set -euo pipefail
exec bash "$(dirname "$0")/run_skill_tests.sh" skills/cro-wireframe/tests WIREFRAME
