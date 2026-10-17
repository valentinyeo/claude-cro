#!/bin/bash
# Copies the planted fixture into the empty eval workspace.
set -euo pipefail
cp "$(dirname "$0")/../fixtures/endlesstesting.ai.subtle.html" index.html
