#!/usr/bin/env bash
# Test: token-count produces output with token estimate
set -euo pipefail
REPO_ROOT="${1:-.}"

OUTPUT=$(echo "Hello world, this is a test prompt for Claude." | python "$REPO_ROOT/shared/scripts/token-count.py" --model claude-sonnet-4-6)

echo "$OUTPUT" | grep -q "Est. Tokens"    || exit 1
echo "$OUTPUT" | grep -q "Context Window"  || exit 1
echo "$OUTPUT" | grep -q "Prompt Usage"    || exit 1
