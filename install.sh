#!/usr/bin/env bash
# Flux installer. The 6 plugins are a coordinated pipeline; the `full`
# meta-plugin pulls them all in via one dependency-resolution pass.
set -euo pipefail

REPO="https://github.com/enchanted-plugins/flux"
FLUX_DIR="${HOME}/.claude/plugins/flux"

step() { printf "\n\033[1;36m▸ %s\033[0m\n" "$*"; }
ok()   { printf "  \033[32m✓\033[0m %s\n" "$*"; }

step "Flux installer"

# 1. Clone the monorepo so shared/scripts/*.py (output-test, eval, sim, schema,
#    self-check) are available to the user locally. Plugins themselves are also
#    served via the marketplace command below — the clone is just for scripts.
if [[ -d "$FLUX_DIR/.git" ]]; then
  git -C "$FLUX_DIR" pull --ff-only --quiet
  ok "Updated existing clone at $FLUX_DIR"
else
  git clone --depth 1 --quiet "$REPO" "$FLUX_DIR"
  ok "Cloned to $FLUX_DIR"
fi

# 2. Seed the prompts index on fresh installs only (never overwrite user data).
INDEX="$FLUX_DIR/prompts/index.json"
if [[ ! -f "$INDEX" ]]; then
  mkdir -p "$FLUX_DIR/prompts"
  printf '{"last_updated":"","prompts":[]}\n' > "$INDEX"
  ok "Initialized prompts index"
fi

cat <<'EOF'

─────────────────────────────────────────────────────────────────────────
  Flux ships as a 6-plugin pipeline — crafter hands off to convergence,
  which emits tests.json that tester executes, and so on. The `full`
  meta-plugin lists all six as dependencies so one install pulls in
  the whole chain.
─────────────────────────────────────────────────────────────────────────

  Finish in Claude Code with TWO commands:

    /plugin marketplace add enchanted-plugins/flux
    /plugin install full@flux

  That installs all 6 plugins via dependency resolution. To cherry-pick
  a single plugin instead, use e.g. `/plugin install prompt-harden@flux`.

  Verify with:   /plugin list
  Expected:      full + 6 plugins installed under the flux marketplace.

EOF
