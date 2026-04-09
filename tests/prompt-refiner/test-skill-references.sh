#!/usr/bin/env bash
# Test: prompt-improver SKILL.md references exist (shared resources)
set -euo pipefail
REPO_ROOT="${1:-.}"

SHARED="$REPO_ROOT/shared"

[[ -f "$SHARED/references/technique-engine.md" ]] || exit 1
[[ -f "$SHARED/references/model-profiles.md" ]]   || exit 1
[[ -f "$SHARED/references/output-formats.md" ]]   || exit 1
[[ -f "$SHARED/references/prompt-anatomy.md" ]]   || exit 1
[[ -f "$SHARED/scripts/self-eval.py" ]]           || exit 1
[[ -f "$SHARED/models-registry.json" ]]           || exit 1
[[ -d "$REPO_ROOT/prompts" ]]                     || exit 1
