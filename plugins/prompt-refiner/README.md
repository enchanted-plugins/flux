# prompt-refiner

**Improves existing prompts. Preserves your intent.**

Load a saved prompt or paste one in. It diagnoses weaknesses, checks model fit, re-selects techniques, and runs the Convergence Engine to push the score toward DEPLOY.

## Install

Part of the [Flux](../..) bundle — **all 6 plugins install together**. `prompt-refiner` operates on artifacts produced by `prompt-crafter`, spawns `convergence-engine`, and leans on `prompt-tester` / `prompt-harden` / `prompt-translate` for the handoffs after refinement; installing it alone leaves it with nothing to refine and nowhere to hand off to, so the manifest lists the other five as dependencies.

```
/plugin marketplace add enchanted-plugins/flux
/plugin install prompt-refiner@flux
```

Claude Code resolves the dependency chain and installs all 6.

## Pipeline

```
User provides existing prompt
  → Phase 0: Load prompt (browse saved prompts or paste directly)
  → Phase 1: Diagnosis (score original, detect model, identify weaknesses)
  → Phase 1.5: Model Fit Check (warns if wrong model)
  → Phase 2: Refinement (re-select techniques, re-format, preserve intent)
  → Phase 3: Comparison (before/after scores, diff report)
  → Phase 4: Multi-Agent Pipeline (convergence + reviewer)
```

## Components

| Type | Name | What it does |
|------|------|-------------|
| Skill | prompt-improver | Main workflow — diagnosis through delivery |
| Agent | convergence | Runs convergence.py in background (Opus) |
| Agent | reviewer | Validates refined prompt (Opus) |

## Key Principle

**Preserve the user's intent and domain knowledge.** Only restructure, re-technique, and re-format — never rewrite their content.

## Triggers

`/refine`, "make this prompt better", "improve this prompt", "fix this prompt"

## For Image Prompts

Collaborative loop — you generate the image externally, rate it 1-10, tell the agent what's wrong. It adjusts and you try again. No iteration limit.
