# prompt-refiner

**Improves existing prompts. Preserves your intent.**

Load a saved prompt or paste one in. It diagnoses weaknesses, checks model fit, re-selects techniques, and runs the Convergence Engine to push the score toward DEPLOY.

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
