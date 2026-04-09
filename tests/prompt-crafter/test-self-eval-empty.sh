#!/usr/bin/env bash
# Test: self-eval rejects empty input (exit code 2)
set -euo pipefail
REPO_ROOT="${1:-.}"

if echo "" | python "$REPO_ROOT/shared/scripts/self-eval.py" > /dev/null 2>&1; then
  exit 1  # Should have rejected
fi
exit 0
