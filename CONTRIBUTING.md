# Contributing to Flux

## Stack

Python (stdlib only) for scripts. Markdown for skills, agents, and references. No external dependencies.

## Critical Rules

Before submitting a PR, verify:

1. **Zero pip installs** — scripts use only Python stdlib.
2. **SKILL.md uses `${CLAUDE_PLUGIN_ROOT}/../../shared/`** — never hardcoded paths.
3. **models-registry.json stays current** — bump `last_updated` and `model_count` when changing model specs.
4. **Reference files stay factual** — cite sources for model-specific claims.
5. **Self-eval scores honestly** — don't inflate heuristic weights.
6. **Every plugin has identical structure** — `.claude-plugin/`, `skills/`, `agents/`, `state/`, `README.md`.
7. **Agents declare `allowed-tools`** — no permission prompts in the pipeline.
8. **Tests pass** — `bash tests/run-all.sh` must exit 0.

## Structure

```
flux/
├── .claude-plugin/marketplace.json    Marketplace (3 plugins)
├── plugins/
│   ├── prompt-crafter/                Creates prompts
│   │   ├── skills/ (enchanter + reviewer)
│   │   ├── agents/ (convergence + reviewer)
│   │   └── hooks/ (PostToolUse)
│   ├── prompt-refiner/                Improves prompts
│   │   ├── skills/ (improver)
│   │   └── agents/ (convergence + reviewer)
│   └── convergence-engine/            Standalone optimizer
│       ├── skills/ (converge)
│       └── agents/ (optimizer + reviewer)
├── shared/
│   ├── references/                    Technique engine, model profiles, formats
│   ├── scripts/                       convergence.py, self-eval.py, token-count.py, report-gen.py, html-to-pdf.py
│   ├── models-registry.json           64 models (single source of truth)
│   └── *.py                           Shared utilities
├── prompts/                           Generated prompts (gitignored except index.json)
└── tests/                             12 tests across 3 plugins
```

## Adding a Model

1. Add the entry to `shared/models-registry.json` with all required fields
2. Add format specs to `shared/references/model-profiles.md`
3. Update `model_count` in the registry
4. Update the models table in `README.md`
5. Run tests to verify registry validation passes

## Adding a Technique

1. Add the technique to `shared/references/technique-engine.md`
2. Include: when to use, when to avoid, model-specific anti-patterns, "Pairs With" column
3. Update the technique count in README.md

## Adding a Plugin

Follow the Allay pattern:
```
plugins/<name>/
├── .claude-plugin/plugin.json
├── skills/<skill-name>/SKILL.md
├── agents/<agent-name>.md         (optional)
├── hooks/hooks.json               (optional)
├── state/.gitkeep
└── README.md
```

Register the plugin in `.claude-plugin/marketplace.json`.

## Testing

```bash
bash tests/run-all.sh
```

12 tests: 7 prompt-crafter, 3 prompt-refiner, 2 convergence-engine.

## Submitting

1. All tests pass
2. models-registry.json is valid JSON with correct `model_count`
3. Scripts run with Python 3.8+ stdlib only
4. No broken `${CLAUDE_PLUGIN_ROOT}` paths
5. Agent files have `allowed-tools` frontmatter
6. README updated if adding models/plugins/features
