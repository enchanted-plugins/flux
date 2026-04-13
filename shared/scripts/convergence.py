#!/usr/bin/env python3
"""Flux Convergence Engine — autonomous prompt perfection with hypothesis-driven iteration.

Like gradient descent for prompts. Each iteration:
1. Scores the prompt (5 axes)
2. Runs binary assertions (pass/fail checks)
3. Forms a hypothesis about the weakest axis
4. Applies a targeted fix
5. Re-scores and checks for regression (auto-revert if worse)
6. Logs learnings for persistence across sessions

Usage:
    python convergence.py <prompt-file>
    python convergence.py <prompt-file> --max 50
    python convergence.py <prompt-file> --verbose

Stdlib only. No pip installs.
"""
import sys, os, re, json, copy
from datetime import datetime
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Import scoring functions from self-eval ───────────────────────────────────

def _import_scorer():
    import importlib.util
    spec = importlib.util.spec_from_file_location("self_eval", os.path.join(SCRIPT_DIR, "self-eval.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_eval = _import_scorer()
AXES = _eval.AXES
SCORERS = _eval.SCORERS


def score_prompt(text):
    scores = {a: round(fn(text), 1) for a, fn in zip(AXES, SCORERS)}
    scores["overall"] = round(sum(scores[a] for a in AXES) / len(AXES), 1)
    return scores


def is_deploy(scores):
    return scores["overall"] >= 9.0 and all(scores[a] >= 7.0 for a in AXES)


# ─── Binary Assertions ────────────────────────────────────────────────────────

def run_assertions(text):
    """Binary pass/fail checks. More stable than numeric scores for detecting issues."""
    results = []
    tl = text.lower()

    results.append(("has_role", bool(re.search(r'\b(you are|act as|role:|your role|your job)\b', tl)),
                     "Prompt defines a role or persona"))
    results.append(("has_task", bool(re.search(r'\b(task:|objective:|goal:|your job|you will|you should|analyze|generate|create|build)\b', tl)),
                     "Prompt defines a clear task"))
    results.append(("has_format", bool(re.search(r'\b(output format|respond in|format:|json|xml|markdown)\b|<output|<format', tl)),
                     "Prompt specifies output format"))
    results.append(("has_constraints", bool(re.search(r"\b(do not|don't|never|avoid|constraint|must not)\b", tl)),
                     "Prompt has constraints/guardrails"))
    results.append(("has_edge_cases", bool(re.search(r'\b(if.{0,20}(empty|invalid|error|missing)|edge case|fallback|if unsure)\b', tl)),
                     "Prompt handles edge cases"))
    results.append(("no_hedge_words", not bool(re.search(r'\b(maybe|perhaps|possibly|somewhat|might want to)\b', tl)),
                     "No hedge words (maybe, perhaps, possibly)"))
    results.append(("no_filler", not bool(re.search(r"(it's worth noting|please note that|keep in mind|in order to)", tl)),
                     "No filler phrases"))
    results.append(("has_structure", bool(re.search(r'(^#{1,3}\s|\n#{1,3}\s|<\w+>)', text)),
                     "Prompt has structural markup (headers or XML tags)"))

    return results


# ─── Fix functions ─────────────────────────────────────────────────────────────

def fix_clarity(text):
    hedges = [(r'\bmaybe\s+', ''), (r'\bperhaps\s+', ''), (r'\bpossibly\s+', ''),
              (r'\bsomewhat\s+', ''), (r'\btry to\s+', ''), (r'\bif possible,?\s*', ''),
              (r'\bmight want to\s+', '')]
    for p, r in hedges:
        text = re.sub(p, r, text, flags=re.I)
    lines = text.split('\n')
    new = []
    for line in lines:
        if len(line.split()) > 50 and ('; ' in line or ', and ' in line):
            line = re.sub(r';\s+', '.\n', line, count=1)
        new.append(line)
    return '\n'.join(new)


def fix_completeness(text):
    tl = text.lower()
    if not re.search(r'\b(you are|act as|role:|your role)\b', tl):
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith(('<', '#', '---')):
                lines.insert(i, "You are a domain expert.\n")
                break
        text = '\n'.join(lines)
    if not re.search(r'\b(task:|objective:|goal:|your job|you will|you should)\b', tl):
        text = text.replace("You are a domain expert.\n", "You are a domain expert. Your job is to complete the following task.\n", 1)
    if not re.search(r'\b(output format|respond in|format:|json|xml|markdown|<output|<format)\b', tl):
        text += "\n\nOutput format: structure your response clearly with headers and sections.\n"
    if not re.search(r"\b(do not|don't|never|must not|avoid)\b", tl):
        text += "\nDo not include information you are unsure about.\n"
    return text


def fix_efficiency(text):
    fillers = [r"it's worth noting that\s*", r"please note that\s*", r"as an AI,?\s*",
               r"I want you to\s*", r"I need you to\s*", r"please make sure\s*(to\s*)?",
               r"it is important to note that\s*", r"keep in mind that\s*",
               r"I would like you to\s*", r"please ensure that\s*", r"in order to\s+"]
    for f in fillers:
        text = re.sub(f, '', text, flags=re.I)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = '\n'.join(line.rstrip() for line in text.split('\n'))
    return text


def fix_model_fit(text):
    tl = text.lower()
    claude = bool(re.search(r'\b(claude|anthropic)\b|<(instructions|context|example)>', tl))
    gpt = bool(re.search(r'\b(gpt-4|gpt-5|openai|chatgpt)\b', tl))
    oseries = bool(re.search(r'\b(o1|o3|o4-mini|o-series)\b', tl))
    if claude and 'think thoroughly' not in tl:
        text = re.sub(r'(</instructions>)', '\nThink thoroughly before responding.\n\\1', text, count=1)
        if '</instructions>' not in text:
            text += "\n\nThink thoroughly before responding.\n"
        text = re.sub(r'\bthink step by step\b', 'think thoroughly', text, flags=re.I)
    if gpt and not re.search(r'\b(step by step|think through)\b', tl):
        text += "\n\nThink step by step through your analysis before providing the final answer.\n"
    if oseries:
        text = re.sub(r'\n.*think step by step.*\n', '\n', text, flags=re.I)
    return text


def fix_failure_resilience(text):
    tl = text.lower()
    additions = []
    if not re.search(r'\bif\b.{0,30}\b(error|fail|cannot|unable|unclear|missing|invalid|empty)\b', tl):
        additions.append("If the input is empty or invalid, report the error clearly and explain what input is expected.")
    if not re.search(r'\b(edge case|corner case|special case|exception|unexpected)\b', tl):
        additions.append("Handle unexpected edge cases gracefully rather than failing silently.")
    if not re.search(r'\b(fallback|default to|if unsure|if you cannot|when in doubt)\b', tl):
        additions.append("If unsure about any information, state your uncertainty explicitly rather than guessing.")
    if not re.search(r'\b(validate|verify|check that|ensure that|confirm|if unclear)\b', tl):
        additions.append("Verify your output against the requirements before delivering the final response.")
    if additions:
        if '<edge_cases>' in text:
            idx = text.index('</edge_cases>')
            text = text[:idx] + '\n' + '\n'.join(additions) + '\n' + text[idx:]
        else:
            text += '\n\n' + '\n'.join(additions) + '\n'
    return text


FIXERS = {
    "Clarity": fix_clarity,
    "Completeness": fix_completeness,
    "Efficiency": fix_efficiency,
    "Model Fit": fix_model_fit,
    "Failure Resilience": fix_failure_resilience,
}


# ─── Learnings Persistence ─────────────────────────────────────────────────────

def load_learnings(prompt_dir):
    """Load learnings.md from the prompt folder if it exists."""
    path = os.path.join(prompt_dir, "learnings.md") if prompt_dir else None
    if path and os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def save_learnings(prompt_dir, log_entries):
    """Save accumulated learnings to the prompt folder."""
    if not prompt_dir or not log_entries:
        return
    path = os.path.join(prompt_dir, "learnings.md")
    content = f"# Convergence Learnings\n\nGenerated: {datetime.now().isoformat()}\n\n"
    for entry in log_entries:
        content += f"- **Iteration {entry['iteration']}** [{entry['result']}]: {entry['hypothesis']} → {entry['outcome']}\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ─── Main Loop ─────────────────────────────────────────────────────────────────

def run(prompt_path, max_iterations=100, verbose=False):
    if not os.path.isfile(prompt_path):
        print(f"Error: {prompt_path} not found", file=sys.stderr)
        sys.exit(2)

    with open(prompt_path, "r", encoding="utf-8") as f:
        text = f.read()

    if not text.strip():
        print("Error: Empty prompt file.", file=sys.stderr)
        sys.exit(2)

    prompt_dir = os.path.dirname(os.path.abspath(prompt_path))
    history = []
    plateau_count = 0
    best_score = 0
    best_text = text
    learnings = []

    print(f"\n{'=' * 60}")
    print(f"  FLUX CONVERGENCE ENGINE")
    print(f"  Target: DEPLOY (overall >= 9.0, all axes >= 7.0)")
    print(f"  Max iterations: {max_iterations}")
    print(f"{'=' * 60}\n")

    for iteration in range(1, max_iterations + 1):
        scores = score_prompt(text)
        overall = scores["overall"]
        history.append(overall)

        # Binary assertions
        assertions = run_assertions(text)
        failed = [a for a in assertions if not a[1]]
        passed = [a for a in assertions if a[1]]

        # Track best version
        if overall > best_score:
            best_score = overall
            best_text = text

        # Check DEPLOY (scores + all assertions pass)
        if is_deploy(scores) and len(failed) == 0:
            print(f"  Iteration {iteration}: {overall}/10 — DEPLOY ({len(passed)}/{len(assertions)} assertions pass)")
            _save(prompt_path, best_text)
            _print_final(scores, assertions, iteration)
            save_learnings(prompt_dir, learnings)
            return scores

        # Check DEPLOY by scores only (assertions are bonus)
        if is_deploy(scores):
            print(f"  Iteration {iteration}: {overall}/10 — DEPLOY (scores OK, {len(failed)} assertion(s) remaining)")
            _save(prompt_path, best_text)
            _print_final(scores, assertions, iteration)
            save_learnings(prompt_dir, learnings)
            return scores

        # Plateau detection
        if len(history) >= 3 and history[-1] == history[-2] == history[-3]:
            plateau_count += 1
            if plateau_count >= 1:
                print(f"  Iteration {iteration}: {overall}/10 — PLATEAU")
                _save(prompt_path, best_text)
                _print_final(scores, assertions, iteration)
                save_learnings(prompt_dir, learnings)
                return scores

        # Form hypothesis — what's the weakest axis and what fix will help?
        axes_by_score = sorted(AXES, key=lambda a: scores[a])
        weakest = axes_by_score[0]
        hypothesis = f"Fixing {weakest} (currently {scores[weakest]}/10) will improve overall from {overall}"

        # Progress update
        if verbose or iteration <= 3 or iteration % 10 == 0:
            fail_names = ", ".join(a[0] for a in failed) if failed else "none"
            print(f"  Iteration {iteration}: {overall}/10 — hypothesis: fix {weakest} | failed assertions: {fail_names}")

        # Save pre-fix state for auto-revert
        pre_fix_text = text

        # Apply fix
        for axis in axes_by_score:
            if scores[axis] < 9.0 and axis in FIXERS:
                text = FIXERS[axis](text)

        # Also fix failed binary assertions directly
        for name, passed_flag, desc in failed:
            if name == "has_role" and "Completeness" not in [axes_by_score[0]]:
                text = fix_completeness(text)
            elif name == "has_edge_cases":
                text = fix_failure_resilience(text)
            elif name == "no_hedge_words":
                text = fix_clarity(text)
            elif name == "no_filler":
                text = fix_efficiency(text)

        # Check for regression — auto-revert if worse
        new_scores = score_prompt(text)
        if new_scores["overall"] < overall - 0.5:
            text = pre_fix_text
            outcome = f"REVERTED — regression from {overall} to {new_scores['overall']}"
            learnings.append({"iteration": iteration, "hypothesis": hypothesis, "result": "reverted", "outcome": outcome})
        else:
            delta = new_scores["overall"] - overall
            outcome = f"{'improved' if delta > 0 else 'unchanged'} ({overall} → {new_scores['overall']})"
            learnings.append({"iteration": iteration, "hypothesis": hypothesis, "result": "applied", "outcome": outcome})

    # Max iterations
    print(f"\n  Max iterations ({max_iterations}) reached. Best: {best_score}/10")
    _save(prompt_path, best_text)
    scores = score_prompt(best_text)
    _print_final(scores, run_assertions(best_text), max_iterations)
    save_learnings(prompt_dir, learnings)
    return scores


def _save(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _print_final(scores, assertions, iterations):
    print(f"\n{'=' * 60}")
    print(f"  FINAL SCORES (after {iterations} iteration{'s' if iterations != 1 else ''})")
    print(f"{'=' * 60}")
    for a in AXES:
        val = scores[a]
        pct = round((val / 10) * 20)
        bar = "#" * pct + "." * (20 - pct)
        print(f"  {(a + ':').ljust(22)}{val:4.0f}/10  {bar}")
    print(f"\n  {'OVERALL:'.ljust(22)}{scores['overall']:4.1f}/10")

    # Assertions summary
    passed = sum(1 for a in assertions if a[1])
    total = len(assertions)
    print(f"  {'ASSERTIONS:'.ljust(22)}{passed}/{total} pass")
    for name, ok, desc in assertions:
        print(f"    {'PASS' if ok else 'FAIL'}  {desc}")

    deploy = is_deploy(scores)
    print(f"\n  VERDICT: {'DEPLOY' if deploy else 'BEST EFFORT'}")
    print(f"{'=' * 60}\n")


def main():
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    max_iter = 100
    args = []
    skip_next = False
    for i, a in enumerate(sys.argv[1:]):
        if skip_next:
            skip_next = False
            continue
        if a == "--max":
            max_iter = int(sys.argv[i + 2])
            skip_next = True
            continue
        if a.startswith("--") or a == "-v":
            continue
        args.append(a)

    if not args:
        print("Usage: python convergence.py <prompt-file> [--max N] [--verbose]", file=sys.stderr)
        sys.exit(2)

    scores = run(args[0], max_iterations=max_iter, verbose=verbose)
    sys.exit(0 if is_deploy(scores) else 1)


if __name__ == "__main__":
    main()
