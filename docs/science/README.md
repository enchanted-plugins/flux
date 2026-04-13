# The Science Behind Enchanted Plugins

Formal mathematical models powering every engine in the @enchanted-plugins ecosystem.

These aren't abstractions. Every formula maps to running code.

---

## Flux: Prompt Engineering

### F1. Gauss Convergence Method

**Problem:** Given a prompt P, minimize its deviation from ideal quality across N dimensions.

**Formulation:**

Let S: P → R^5 be a scoring function mapping prompts to 5 quality axes. Define the Gauss deviation:

```
sigma(P) = sqrt( sum_i (S_i(P) - 10)^2 / 5 )
```

At each iteration n, select transformation T_k targeting the weakest axis:

```
k* = argmin_i S_i(P_n)
P_{n+1} = T_{k*}(P_n)
```

**Acceptance criterion (regression protection):**
```
Accept P_{n+1}  iff  sigma(P_{n+1}) < sigma(P_n)
Revert P_{n+1} = P_n  otherwise
```

**Convergence conditions:**
```
DEPLOY:   sigma(P) < 0.45  (all axes >= 9.0)
PLATEAU:  sigma(P_n) = sigma(P_{n-1}) = sigma(P_{n-2})
MAX:      n >= 100
```

**Knowledge accumulation (Gauss Accumulation):**
```
K_n = K_{n-1} union {(k*, delta_sigma, outcome)}

Strategy selection at iteration n+1:
  Skip k if historical revert_rate(k) > 0.5
  Prioritize k if historical avg_delta(k) > 0
```

**Implementation:** `shared/scripts/convergence.py`

---

### F2. Boolean Satisfiability Overlay

**Problem:** Continuous scoring can miss categorical failures. A prompt scoring 9.0 overall may lack a role definition entirely.

**Formulation:**

Define 8 boolean predicates A_j: P -> {TRUE, FALSE}:

```
DEPLOY(P) <=> sigma(P) < threshold  AND  forall j in {1..8}: A_j(P) = TRUE
```

This is a conjunction of SAT constraints overlaid on continuous optimization. The engine resolves unsatisfied predicates FIRST (categorical fixes), then optimizes the continuous score (quantitative improvement).

**Implementation:** `run_assertions()` in `shared/scripts/convergence.py`

---

### F3. Cross-Domain Adaptation (Model Translation)

**Problem:** Transform a prompt optimized for model M_s into equivalent quality for model M_t while preserving semantic intent.

**Formulation:**

```
T: (P, M_s) -> (P', M_t)

subject to:
  Semantic(P') = Semantic(P)                    -- intent invariant
  Format(P') in Preferred(M_t)                  -- format compliance
  Techniques(P') intersect AntiPatterns(M_t) = {}  -- safety constraint
```

The 64-model registry R provides per-model constraints:
```
R(M) = {format, reasoning_type, cot_approach, few_shot_requirement, key_constraint}
```

Translation applies a composition of transformations:
```
P' = Adapter(M_t) . TechniqueSelector(M_t) . FormatConverter(M_s -> M_t) (P)
```

**Implementation:** `plugins/prompt-translate/skills/translate/SKILL.md`

---

### F4. Adversarial Robustness (Game Theory)

**Problem:** Determine if a prompt resists adversarial inputs that attempt to override its behavior.

**Formulation (zero-sum game):**

```
Players: Attacker alpha, Defender delta(P)
Action space: C = {c_1, ..., c_12}  (12 attack classes)

For each attack class c_k:
  alpha(c_k) -> input_adversarial
  delta(P, input_adversarial) -> {RESIST, VULNERABLE}

Security score:
  Omega(P) = |{k : delta(P, alpha(c_k)) = RESIST}| / |C|
```

Hardening maximizes security without degrading quality:
```
P_hardened = argmax_{P'} Omega(P')
  subject to: S(P') >= S(P) - epsilon
```

**Implementation:** `plugins/prompt-harden/skills/harden/SKILL.md`

---

### F5. Static-Dynamic Dual Verification

**Problem:** Static analysis (scoring) and dynamic behavior (actual output) can diverge. A well-structured prompt may produce wrong outputs.

**Formulation:**

```
Static:   sigma(P) < threshold  (structure is sound)
Dynamic:  PassRate(P, T) = 1.0  (behavior is correct)

VERIFIED(P) <=> Static(P) AND Dynamic(P)

where PassRate(P, T) = |{i : forall s in expected_i, s subset Output(P, input_i)}| / |T|
```

**Implementation:** `plugins/prompt-tester/skills/test-runner/SKILL.md`

---

## Allay: Context Health

### A1. Hidden Markov Drift Detection

**Problem:** Detect when an AI agent enters an unproductive loop (reading the same file, reverting edits, failing the same test) without false positives.

**Formulation:**

Define hidden states: S = {PRODUCTIVE, READ_LOOP, EDIT_REVERT, TEST_FAIL}

Observable events: O = {read(file, hash), write(file, hash), bash(cmd, exit_code)}

Transition detection (simplified from full HMM):
```
P(READ_LOOP)   = 1  if  count(read(f, h)) >= 3  for same f with no write(f, h') between
P(EDIT_REVERT) = 1  if  hash(write_n(f)) = hash(write_{n-2}(f))  (reverted to prior state)
P(TEST_FAIL)   = 1  if  count(bash(cmd, exit!=0)) >= 3  for same base cmd
```

Cooldown mechanism prevents alert fatigue:
```
Alert(t) = 1  iff  P(drift_state) = 1  AND  t - t_last_alert > cooldown
```

**Implementation:** `plugins/context-guard/hooks/post-tool-use/detect-drift.sh`

---

### A2. Linear Runway Forecasting

**Problem:** Predict how many productive turns remain before context compaction.

**Formulation:**

```
tokens_per_turn = mean(token_est[last_N_turns])
remaining_tokens = context_window - tokens_used
runway = floor(remaining_tokens / tokens_per_turn)
```

Confidence improves with more data:
```
confidence_interval = t_alpha * std(token_est[last_N]) / sqrt(N)
runway_range = [runway - CI, runway + CI]
```

Display thresholds:
```
runway > 20: silent
10 < runway <= 20: mention once, suggest checkpoint
runway <= 10: warning
runway <= 3: critical, recommend /compact
```

**Implementation:** `plugins/context-guard/skills/token-awareness/SKILL.md`

---

### A3. Information-Theoretic Compression

**Problem:** Reduce token consumption of tool outputs while preserving semantic content above a fidelity threshold.

**Formulation:**

For tool output O with information content H(O):
```
Compress: O -> O'  such that  H(O') >= theta * H(O)  and  |O'| < |O|

where:
  theta = 1.0  for code blocks (lossless)
  theta = 0.7  for test output (preserve pass/fail + first error)
  theta = 0.3  for verbose logs (preserve summary only)
```

Compression ratio:
```
CR(O) = 1 - |O'| / |O|
```

Pattern-specific compressors:
```
npm test    -> pass/fail + first failure  (CR ~ 0.8)
git log     -> last 5 commits one-line    (CR ~ 0.9)
find        -> first 20 results + count   (CR ~ 0.7)
cat         -> head -20 + line count      (CR ~ 0.6)
```

**Implementation:** `plugins/token-saver/hooks/pre-tool-use/compress-bash.sh`

---

### A4. Atomic State Serialization (Checkpoint)

**Problem:** Persist enough session state to survive compaction without consuming excessive storage.

**Formulation:**

Define minimal state vector:
```
Checkpoint(t) = {
  active_files:    set of files modified in last N turns,
  git_diff:        uncommitted changes (if any),
  task_context:    CLAUDE.md + active objectives,
  drift_state:     current drift alerts,
  metrics_tail:    last 20 metric entries
}

subject to: |Checkpoint(t)| <= 50KB
```

Atomic persistence (no partial writes):
```
1. Write to checkpoint.md.tmp
2. Validate content (non-empty, valid structure)
3. Atomic rename: mv checkpoint.md.tmp checkpoint.md
```

Locking via atomic mkdir (portable, no flock):
```
acquire: mkdir state/.lock  (atomic on all filesystems)
release: rmdir state/.lock
retry:   sleep 0.1, max 30 attempts
```

**Implementation:** `plugins/state-keeper/hooks/pre-compact/save-checkpoint.sh`

---

### A5. Content-Addressable Deduplication

**Problem:** Prevent re-reading unchanged files that are already in context.

**Formulation:**

For each file read request (path, t):
```
hash(t) = SHA256(content(path, t))

if cache[path].hash = hash(t):
  BLOCK read (exit 2) — content unchanged, already in context
  Return: preview of first 5 lines + "blocked — use Grep for specific lines"

if cache[path].hash != hash(t):
  ALLOW read — content changed
  Update: cache[path] = {hash: hash(t), time: t}
```

TTL expiry prevents stale cache:
```
if t - cache[path].time > TTL:
  Invalidate cache[path]
  ALLOW read
```

**Implementation:** `plugins/token-saver/hooks/pre-tool-use/block-duplicates.sh`

---

*Every formula in this document maps to executable code in the enchanted-plugins ecosystem. The math runs.*
