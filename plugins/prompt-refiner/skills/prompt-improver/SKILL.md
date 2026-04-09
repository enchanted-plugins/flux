---
name: prompt-improver
description: >
  Improves existing prompts by re-selecting techniques, adapting
  format to the target model, and fixing weaknesses while preserving
  the user's intent and domain knowledge.
  Auto-triggers on: "make this prompt better", "improve this prompt",
  "refine this prompt", "fix this prompt", "optimize this prompt",
  "what's wrong with this prompt", "/refine".
---

# Flux — Prompt Refiner

Improve an existing prompt by diagnosing weaknesses, re-selecting techniques, and adapting format to the target model.

**Core rule:** Preserve the user's intent and domain knowledge. Only restructure, re-technique, and re-format — never rewrite their content.

Execute Phases 0–3 in order.

---

## Phase 0: Load the Prompt

Determine the source of the prompt to refine:

**Option A — User provides a prompt directly:** Use it as-is. Skip to Phase 1.

**Option B — User references a saved prompt:** Browse `${CLAUDE_PLUGIN_ROOT}/../../prompts/` for existing prompt folders. Each folder contains `prompt.<format>`, `report.html`, and `metadata.json`.

**Option C — User says "refine" or "improve" without specifying:** List available prompts from the `${CLAUDE_PLUGIN_ROOT}/../../prompts/` folder. Show each prompt's name, target model, overall score, and creation date (from `metadata.json`). Ask the user to pick one.

When loading a saved prompt:
1. Read `metadata.json` for context (model, domain, techniques, scores)
2. Read `prompt.<format>` as the input prompt
3. Read `report.html` for previous technique decisions — avoid re-applying techniques that were deliberately avoided unless the user's refinement goal changes the calculus

---

## Phase 1: Diagnosis

### 1A: Score the Original

Run `${CLAUDE_PLUGIN_ROOT}/../../shared/scripts/self-eval.py` on the user's original prompt. Record scores for all 5 axes.

If the script is unavailable, score manually using the same 5 axes:
1. **Clarity** — Are instructions unambiguous?
2. **Completeness** — Does it cover the full task?
3. **Efficiency** — Minimal tokens for maximum effect?
4. **Model Fit** — Does the format match the target model?
5. **Failure Resilience** — Does it handle edge cases?

### 1B: Detect Target Model and Domain

1. Check if the prompt mentions a model explicitly.
2. Detect from formatting cues: XML tags → Claude, Markdown headers → GPT, minimal → o-series.
3. Read `CLAUDE.md` for project model preferences.
4. If ambiguous, ask the user which model this prompt targets.
5. Detect task domain: `coding` | `data-extraction` | `creative-writing` | `analysis` | `agent` | `conversational` | `image-gen` | `decision-making` | `other`

### 1C: Identify Weaknesses

Based on the scores, list specific problems:
- Axes scoring below 6 are critical weaknesses
- Axes scoring 6-7 are improvement opportunities
- Note any anti-patterns for the detected model (e.g., CoT for o-series, no few-shot for Gemini)

Present the diagnosis to the user before proceeding:

```
## Diagnosis

**Original Score:** X.X/10
**Target Model:** [detected or asked]
**Weaknesses Found:**
- [specific weakness 1]
- [specific weakness 2]

Proceeding with refinement...
```

---

## Phase 2: Refinement

### 2A: Re-select Techniques

Read [technique-engine.md](${CLAUDE_PLUGIN_ROOT}/../../shared/references/technique-engine.md). Based on the diagnosed weaknesses and target model:

1. Identify which techniques the original prompt uses (implicitly or explicitly)
2. Check if any are anti-patterns for the target model
3. Select 1-3 techniques that would fix the diagnosed weaknesses
4. Keep techniques that are already working well

### 2B: Re-format and Restructure

Read [model-profiles.md](${CLAUDE_PLUGIN_ROOT}/../../shared/references/model-profiles.md) for the target model's format requirements.
Read [output-formats.md](${CLAUDE_PLUGIN_ROOT}/../../shared/references/output-formats.md) for the task type's optimal structure.

**Registry check:** Read [models-registry.json](${CLAUDE_PLUGIN_ROOT}/../../shared/models-registry.json) for context window and capabilities.

Apply fixes:
- **Format layer**: Convert to the target model's preferred format (XML for Claude, Markdown for GPT, minimal for o-series)
- **Technique layer**: Add missing techniques, remove harmful ones
- **Component layer**: Add missing mandatory components (fallbacks, expected output, success criteria) per [prompt-anatomy.md](${CLAUDE_PLUGIN_ROOT}/../../shared/references/prompt-anatomy.md)
- **Efficiency layer**: Remove filler phrases, redundant instructions, conflicting directives

**What NOT to change:**
- The user's domain-specific content and examples
- The core task description and intent
- Custom terminology or jargon the user chose deliberately
- The scope of what the prompt asks for

---

## Phase 3: Comparison & Delivery

### 3A: Score the Refined Prompt

Run `${CLAUDE_PLUGIN_ROOT}/../../shared/scripts/self-eval.py` on the refined prompt. Compare before/after scores.

### 3B: Present the Refined Prompt

Always present the refined prompt inside a fenced code block (` ``` `).

### 3C: Save as a Folder

Save the refined prompt as a folder inside `${CLAUDE_PLUGIN_ROOT}/../../prompts/`. Append `-v<N>` to the folder name if a previous version exists (e.g., `invoice-extractor-v2`).

After saving, update `${CLAUDE_PLUGIN_ROOT}/../../prompts/index.json` — update the existing entry with new scores, version, and refined timestamp. Create the file if it does not exist.

```
prompts/<prompt-name>/
├── prompt.<format>       # The refined prompt
├── report.html             # Refinement Report (see below)
├── metadata.json         # Machine-readable metadata + runtime config
└── tests.json            # Test cases (update or keep from previous version)
```

**metadata.json:**
```json
{
  "created": "<ISO 8601 timestamp>",
  "task": "<one-line task description>",
  "target_model": "<model ID>",
  "task_domain": "<domain>",
  "format": "<prompt format>",
  "mode": "refine",
  "techniques_added": ["<technique>"],
  "techniques_removed": ["<technique>"],
  "techniques_kept": ["<technique>"],
  "tokens": {
    "original": <number>,
    "refined": <number>,
    "context_window": <number>,
    "usage_percent": <number>
  },
  "scores": {
    "before": { "clarity": 0, "completeness": 0, "efficiency": 0, "model_fit": 0, "failure_resilience": 0, "overall": 0 },
    "after": { "clarity": 0, "completeness": 0, "efficiency": 0, "model_fit": 0, "failure_resilience": 0, "overall": 0 }
  },
  "version": <number>
}
```

**report.html** — Generated PDF report. After saving `metadata.json`, run:
```
python ${CLAUDE_PLUGIN_ROOT}/../../shared/scripts/report-gen.py <prompt-folder-path>
```
This reads `metadata.json` and generates a formatted PDF with before/after scores, techniques, and config.

**If the user says "just give me the prompt":** Output refined prompt only, no report.
