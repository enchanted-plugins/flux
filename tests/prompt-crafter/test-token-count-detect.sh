#!/usr/bin/env bash
# Test: token-count auto-detects Claude from prompt content
set -euo pipefail
REPO_ROOT="${1:-.}"

OUTPUT=$(echo "You are Claude. Extract data using <example> tags." | python "$REPO_ROOT/shared/scripts/token-count.py")

echo "$OUTPUT" | grep -q "claude" || exit 1
