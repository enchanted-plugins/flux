#!/usr/bin/env bash
# Test: token-count rejects empty input
set -euo pipefail
REPO_ROOT="${1:-.}"

if echo "" | python "$REPO_ROOT/shared/scripts/token-count.py" > /dev/null 2>&1; then
  exit 1  # Should have rejected
fi
exit 0
