#!/usr/bin/env bash
# MiroFish answers locally and its model calls go through the Haiku relay.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 skills/cro/scripts/message_test.py check
