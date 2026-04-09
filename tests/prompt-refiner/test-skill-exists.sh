#!/usr/bin/env bash
# Test: prompt-refiner plugin has required structure
set -euo pipefail
REPO_ROOT="${1:-.}"

PLUGIN="$REPO_ROOT/plugins/prompt-refiner"

[[ -f "$PLUGIN/.claude-plugin/plugin.json" ]]   || exit 1
[[ -f "$PLUGIN/skills/prompt-improver/SKILL.md" ]] || exit 1
[[ -f "$PLUGIN/README.md" ]]                     || exit 1
[[ -d "$PLUGIN/state" ]]                         || exit 1
