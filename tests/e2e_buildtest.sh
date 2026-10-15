#!/usr/bin/env bash
# G gate: run the buildtest skill tests (unittest exit code decides, pipefail on).
set -euo pipefail
exec bash "$(dirname "$0")/run_skill_tests.sh" skills/cro-build-test/tests BUILDTEST
