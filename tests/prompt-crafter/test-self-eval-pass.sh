#!/usr/bin/env bash
# Test: self-eval gives a passing score on a well-structured prompt
set -euo pipefail
REPO_ROOT="${1:-.}"

PROMPT='You are an expert data analyst.

## Task
Extract structured JSON from the provided invoice text.

## Output Format
Return a JSON object with fields: vendor, date, total, line_items.

## Constraints
- Do not hallucinate fields not present in the input.
- If a field is missing, set it to null.
- Always validate that the input contains at least one recognizable invoice field.

## Error Handling
- If the input is not a valid invoice, return {"error": "Not a valid invoice"}.
- If the input is empty or unclear, return {"error": "Empty or ambiguous input"}.
- If you cannot extract a required field, default to null rather than guessing.

## Example
<example>
Input: "Invoice from Acme Corp, 2026-01-15, Total: $500"
Output: {"vendor": "Acme Corp", "date": "2026-01-15", "total": 500, "line_items": []}
</example>'

echo "$PROMPT" | python "$REPO_ROOT/shared/scripts/self-eval.py"
