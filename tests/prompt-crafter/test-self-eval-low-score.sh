#!/usr/bin/env bash
# Test: self-eval flags a vague prompt with low scores (exit code 1)
set -euo pipefail
REPO_ROOT="${1:-.}"

PROMPT="maybe try to do something with the data if possible"

# Should exit 1 (low scores) — we invert the check
if echo "$PROMPT" | python "$REPO_ROOT/shared/scripts/self-eval.py" > /dev/null 2>&1; then
  exit 1  # Should have failed
fi
exit 0  # Correctly flagged as low quality
