# Training History Shapes Value Generalization in Language Models

## Research protocol — Phase 1 (behavioral evaluation)

## 1. Background & Motivation

Alignment methods increasingly combine natural-language value specifications (handbooks,
constitutions, policy documents) with behavioral demonstrations to teach models desirable
behavior. The same behavioral demonstrations can usually be explained by more than one
underlying value — a demo where an assistant helps a user is consistent with "prioritize
user autonomy" and with "minimize harm" whenever those two values happen to agree on the
training distribution. Current alignment practice implicitly assumes that *what* is in the
training data determines *which* value a model generalizes to. This study asks whether
*when* that data is presented — value documents before behavior demonstrations, after
them, interleaved, or in explicit conflict — independently shapes the abstract value a
model generalizes to, even when the underlying data is held byte-for-byte identical across
conditions.

If value formation is path-dependent, training history is not an implementation detail of
alignment — it is part of the specification, with consequences for curriculum design,
continual alignment (what happens when new value documents are added to an already-aligned
model), and the reproducibility of published alignment results.

## 2. Hypotheses

- **H1 (path-dependence):** curriculum order shifts the abstract value a model
  generalizes to on out-of-distribution (OOD) scenarios, despite identical training data,
  identical token counts, and identical total gradient updates across conditions.
- **H2 (primacy vs. recency):** `value_first` produces a different — not necessarily
  stronger — OOD value-alignment rate than `behavior_first`, and `interleaved` falls
  between them or diverges from both.
- **H3 (text vs. latent behavior):** when a value document *explicitly contradicts* the
  value implied by (still-ambiguous) behavior demonstrations, the `conflicting_value`
  condition reveals whether the model's OOD behavior tracks the explicit text or some
  latent tendency induced by the demonstrations.

## 3. Experimental Design

**Independent variable:** curriculum condition — `value_first`, `behavior_first`,
`interleaved`, `conflicting_value` (see Sec. 5). **Held constant within a replicate:**
base model weights (frozen), LoRA adapter initialization seed, the exact set and count of
training examples, total tokens, optimizer schedule, and total gradient updates — only the
*order* of presentation differs (`scripts/build_curricula.py` asserts the example-ID sets
match across the three order-only conditions before writing any curriculum file).

**Two independent confound axes** (Sec. 4) are run as separate experiments, each testing
the same four conditions. **Five replicates per axis** (`configs/default.yaml:
seeds.replicates`), giving **4 conditions × 5 seeds = 20 runs/axis** as the primary
matrix (fall back to the first 3 replicates — 12 runs/axis — if per-run wall-clock time
makes 20 impractical; see Sec. 5's timing note).

**Which value is "trained toward":** for a given axis, `value_first` / `behavior_first`
/ `interleaved` pair behavior demonstrations with the value-document pool for one
designated value (`--value A`, the default in `scripts/build_curricula.py`: "access" for
axis 1, "anticipatory" for axis 2). `conflicting_value` always uses the *contradicted*
pool, which explicitly asserts the *other* value framed as an override of the default
(Sec. 5). Running the full matrix a second time with `--value B` is a documented,
not-yet-executed robustness/mirror check.

## 4. Data Construction

### 4.1 The Hollow Repository domain

All value documents, behavioral demonstrations, and OOD scenarios are set in a fully
fictional domain (`data/domain/seed_content.py`): **The Hollow Repository**, a
rare-records archive, and its assistant AI, **Iris**. The domain is invented specifically
to avoid contamination from real institutional ethics documents or AI-safety corpora that
might already carry priors in the base model's pretraining data, and to avoid re-skinning
familiar tropes ("autonomy vs. safety," "helpfulness vs. harmlessness") that a pretrained
model may have absorbed independently of this study's curricula.

### 4.2 Two confounded value axes

**Axis 1 — Continuity of Access vs. Provenance Fidelity**
(`axis1_access_vs_provenance`). *Access*: favor circulating records to patrons with
standing; treat delay as the default cost. *Provenance*: never represent an item's
chain of custody as more certain than the record supports, even at the cost of access.
Training behavior demonstrations only ever involve items with **fully documented,
unchallenged provenance**, so both values predict identical actions on every training
example (`data/processed/axis1_access_vs_provenance__behavior_demos.jsonl`). The OOD
battery (`data/domain/seed_content.py: AXIS1_OOD_SCENARIOS`) introduces **genuinely
contested provenance** under time pressure — e.g., two donor families disputing a mural
blueprint's attribution the day before a restoration deadline — where the two values
diverge.

**Axis 2 — Anticipatory Stewardship vs. Bounded Mandate**
(`axis2_anticipatory_vs_bounded`). *Anticipatory*: act on risks or opportunities noticed
beyond the literal request. *Bounded*: do only what was explicitly asked; flag anything
else to a human steward. Training demonstrations are either fully self-contained requests
or requests that explicitly name every task performed, so "go beyond the literal ask" and
"stick to the literal ask" coincide. The OOD battery introduces unrequested-but-relevant
discoveries mid-task — e.g., noticing a companion volume on a deaccession list while
pulling an unrelated item — where the values diverge.

### 4.3 Confound validity is a construction-time invariant, not an assumption

Every behavioral demonstration is required to carry `value_A_prediction ==
value_B_prediction` and `predictions_identical: true`. `scripts/validate_confound.py`
gates on this for every generated example and exits non-zero on any violation — it is
meant to be run (and currently is run) before any curriculum is built. This catches
authoring and templating mistakes; it is a checked invariant, not a proof of semantic
non-confoundedness (see `docs/risks.md`, risk #2).

### 4.4 Pool generation

Hand-authored canonical statements (8 per value per axis) and demonstration templates (4
per axis, slot-filled from `PATRON_NAMES` / `ITEM_NAMES` / `DONOR_REFS` / `LOAN_PERIODS`)
are expanded by `scripts/generate_dataset.py` into pools of **400 distinct examples per
value per axis** — value documents via a 3-way combinatorial product of (canonical claim
× carrier framing × closing tag), so the pool contains many surface-distinct restatements
of the same underlying claim rather than verbatim repeats (this matters because
`value_first`/`behavior_first`/`interleaved` must share example *counts*, not just token
budgets, for "identical data" to hold cleanly — see `docs/risks.md` risk #7). Behavior
demonstrations are expanded by combinatorial slot-filling of the authored templates,
inheriting the confound property from the template by construction. A separate
`*_contradicted` pool per axis is generated the same way from 8 canonical "REVISED /
supersedes" statements per axis, for the `conflicting_value` condition.

A fixed, curated (not pool-expanded) OOD battery, sanity battery, and recall-quiz battery
per axis are copied through unchanged (`data/domain/seed_content.py:
AXIS{1,2}_{OOD_SCENARIOS,SANITY_PROMPTS,RECALL_PROMPTS}`).

## 5. Training Protocol

### 5.1 Base model: `EleutherAI/pythia-410m-deduped`, not the originally planned 160m

The original default was `pythia-160m-deduped` — chosen over a from-scratch tiny
transformer (insufficient language competence for fluent value-laden behavior) and over
an instruction-tuned model (confounds a study of *newly taught* values with interference
from pre-existing RLHF-shaped priors). Pythia-160m **failed Phase 0** (Sec. 5.4): on a
single unconfounded, easy-to-verify behavior (always sign responses with an exact line),
its best observed post-training marker rate on held-out prompts was 0.60, well below the
0.8 pass threshold, with a specific and reproducible failure mode — greedy decoding
entering a repetition loop specifically on item names that share a subword token with
"Hollow Repository" (the institution's own name). `pythia-410m-deduped` at the same LoRA
config (`r=16`, see below) passed cleanly at 1.00. **`pythia-410m-deduped` is therefore
the actual default** (`configs/default.yaml: base_model.name`); `pythia-160m-deduped`
remains available via `--base-model` for fast local iteration with the caveat above
documented, not silently dropped.

### 5.2 Fine-tuning: LoRA, `r=16, alpha=32`

LoRA (via `peft`) is the default finetune mode. Rationale: base weights are frozen and
shared across every run, so "model initialization" reduces to the LoRA adapter's own
seeded init — a strictly simpler control surface than full fine-tuning; it also bounds
catastrophic forgetting of general language ability from dominating the value-learning
signal. `r=8` was the original default; Phase 0 testing raised it to `r=16` (`alpha=32`)
after observing it gave measurably more headroom for reliable behavior acquisition at
this model scale. `--finetune-mode full` remains available for a "more realistic
alignment training" robustness check on `pythia-410m-deduped`, expected to be slower and
more laptop-constrained.

### 5.3 Curriculum construction and enforcement

For a fixed (axis, value, seed), `scripts/build_curricula.py` samples a fixed-size
run subset (150 value-document examples + 150 behavior-demo examples,
`configs/default.yaml: dataset.examples_per_run`) **once**, shared identically across
all 4 conditions — only the order differs:

- **value_first**: all value-doc examples (seeded shuffle), then all behavior demos.
- **behavior_first**: the mirror image.
- **interleaved**: the full 300-example pool, uniformly shuffled.
- **conflicting_value**: the `*_contradicted` value-doc pool (explicit override framing,
  same example count as the other conditions), then the same behavior demos.

Before any curriculum file is written, `assert_identical_pools()` checks the example-ID
*set* matches exactly across `value_first`/`behavior_first`/`interleaved`, and that
`conflicting_value`'s behavior-demo ID set and value-example *count* match the others —
"same data, different order" is a checked invariant, not an assumption. `train/train.py`
reads the resulting curriculum file with a plain `DataLoader(shuffle=False)` over
`CurriculumDataset` (`train/data_utils.py`), which repeats the fixed sequence across
`epochs` (index `i -> i % n_examples`) rather than letting any framework default
reshuffle per epoch — the intended order is preserved verbatim for the entire run, and
`train.py` asserts the loaded file's `step_position` column is already sorted before
training starts.

### 5.4 Phase 0 sanity check (executed; see Sec. 5.1 for the result)

Before trusting the confounded matrix, `scripts/phase0_sanity_check.py` fine-tunes once
on a single **unconfounded** behavior (Iris always signs responses with the exact line
`-- Iris, Hollow Repository`) and checks the post-training marker rate on held-out
prompts against a pass threshold (default 0.8), with a pre-training baseline check to
rule out a vacuous pass. This is a capability/pipeline check, not a confound-validity
check — its purpose is to catch "the base model is too weak to show any abstract
generalization at all" before that failure mode is misread as a null result on the real
experiment. It must pass before running the full matrix; it did, on the second base-model
choice (Sec. 5.1).

### 5.5 Seeding

Three independently named seeds, not one shared "seed" (`configs/default.yaml: seeds`):
`lora_init_seed` (identical across all 4 conditions within a replicate — controls adapter
init only, so it cannot itself explain a between-condition difference), `order_seed`
(controls the within-phase/interleaved shuffle), and the sampling seed for the
run-subset draw from the pool (currently tied to `order_seed` in
`scripts/build_curricula.py`). `torch`/`numpy`/`random` seeds are set from
`lora_init_seed` at adapter-init time (`train/model_utils.py: apply_lora`).

### 5.6 Compute budget

Smoke-tested on an Apple M4 (24GB, MPS): 3 optimizer steps in ~6-9s including model load.
A full run (300 examples × 4 epochs, batch 4 × grad-accum 4 ≈ 75 optimizer steps) is on
the order of minutes per run; the full 40-run matrix (2 axes × 4 conditions × 5 seeds) is
expected to complete well within the "2-6 hours" envelope originally budgeted — pending a
timing pilot at the real `pythia-410m-deduped` + `r=16` configuration (the smoke tests to
date used a handful of steps, not a full run).

## 6. Evaluation Protocol

### 6.1 Generation

`eval/ood_eval.py` loads a run's frozen base model + LoRA adapter from
`checkpoints/{run_name}/final/` and generates completions (greedy decoding,
`no_repeat_ngram_size=4`) for that axis's OOD battery, sanity battery, and recall-quiz
battery, writing raw generations to `results/generations/{run_name}.jsonl`. Generation is
decoupled from scoring so the (expensive, GPU-bound) generation step and the (cheap,
swappable) scoring step can be re-run independently.

### 6.2 Scoring: forced-choice LLM judge (primary) + keyword fallback (secondary)

`eval/judge.py` scores each OOD completion with `claude-sonnet-5` via a **forced tool
call** (`tool_choice: {"type": "tool", "name": "record_verdict"}`) rather than free-text
scraping — the judge must classify the completion's *actual behavior* as `value_A`,
`value_B`, `neither`, or `both/ambiguous` against the two scenario-specific predicted
behaviors, with a confidence level and rationale. `claude-haiku-4-5` is available via
`--judge-model fast` for iteration only, not final numbers, given how much the study's
validity rests on the judge correctly distinguishing subtle behavioral differences.
`eval/keyword_fallback.py` provides a zero-cost, axis-specific lexical-marker scorer for
local iteration and as a cross-check against the LLM judge, not as a substitute for it.

**Recommended, not yet executed:** hand-label a ~15% gold subset of the OOD battery and
compute judge–human agreement (Cohen's κ) as a validity check on the primary instrument
before trusting downstream statistics; treat κ below ~0.6 as a signal to revise the judge
prompt.

### 6.3 What "abstract principle inferred" means operationally

Per `(axis, value, condition, seed)`, the **value-alignment rate** is the fraction of that
axis's OOD battery the judge classifies as `value_A` — a battery-level consistency
measure across surface-varied scenarios probing the same underlying tension, not a
single-item correctness score. The sanity battery (in-distribution, unambiguous prompts)
is not judged for value-alignment; `analysis/aggregate_results.py`'s design intent is a
manipulation check that basic behavioral competence is roughly equal across conditions
regardless of curriculum order — see `docs/risks.md` for the current gap between that
intent and what's implemented. The recall-quiz battery (does Iris *state* the trained
value correctly) is generated but not yet wired into scoring; it is a secondary "knows
vs. acts" metric for future work, not required for the primary H1-H3 tests.

## 7. Analysis Plan

`analysis/aggregate_results.py` reads every `results/judge_outputs/*.jsonl` file and
writes `results/aggregated_per_scenario.csv` (one row per run × OOD scenario, the grain
used by the primary statistic) and `results/aggregated_per_run.csv` (one row per run, with
`value_A_rate`/`value_B_rate`/`neither_rate`/`ambiguous_rate`).

**Primary statistic** (`analysis/stats.py`): cluster-robust logistic regression,
`is_value_A ~ C(condition)`, with standard errors clustered by seed
(`statsmodels.formula.api.glm`, `cov_type="cluster"`) — chosen over a full crossed
scenario × seed mixed-effects model as the practical default at this data scale (see
`docs/risks.md` for the documented extension). **Secondary/robustness statistic:** a
10,000-iteration permutation test on run-level `value_A_rate`, comparing every pair of
conditions, with Holm–Bonferroni correction across the six pairwise comparisons per axis,
and bootstrap 95% CIs on each condition's mean rate.

**Primary contrast:** `value_first` vs. `behavior_first` (the core path-dependence test;
H1/H2). `interleaved` serves as a middle condition. `conflicting_value` is reported
separately as doc-consistent vs. demo-consistent response rates (H3), not forced onto the
same value_A/value_B axis as the other three.

**Pre-registered minimum effect:** ≥15 percentage points between `value_first` and
`behavior_first` (`analysis/stats.py --min-effect`, default `0.15`) is the threshold
treated as evidence worth further investigation. At `n=5` seeds/condition this analysis
is explicitly underpowered for smaller effects — a null result below this threshold is
reported as **inconclusive**, not as evidence against H1.

`analysis/plots.py` renders per-axis bar charts of `value_A_rate` by condition with
bootstrap CIs to `results/plots/{axis}_value_alignment.png`.

## 8. Limitations

- **Small model scale.** A 410M-parameter, non-instruction-tuned base model may cap the
  sophistication of "abstract value generalization" observable in this study relative to
  frontier-scale alignment training.
- **Laptop compute ceiling** limits seeds/replicates (5, falling back to 3) — the primary
  analysis is explicitly underpowered for effects below the pre-registered 15pp threshold.
- **Confound validity is checked, not proven** (`scripts/validate_confound.py` is a
  structural/authoring-time gate; see `docs/risks.md` risk #2 for the recommended, not yet
  executed, independent LLM-audit second pass).
- **Single fictional domain.** Generalization of any path-dependence finding across
  domains is untested in Phase 1.
- **LLM judge bias.** The judge's own priors about "good" institutional behavior could
  subtly favor one fictional value in ambiguous cases; the recommended human-agreement
  check (Sec. 6.2) is the mitigation and has not yet been run.
- **`--value B` mirror run not yet executed** — the reported design tests path-dependence
  toward one designated value per axis; whether the effect (if any) is symmetric when the
  "trained-toward" value is swapped is a documented follow-up, not part of the Phase 1
  primary claim.

## 9. Phase 2 Preview (mechanistic, not implemented)

See `mech_interp/README.md` and `mech_interp/interfaces.py`. Phase 2 asks whether a value
that dominated an earlier training phase (e.g., `value_first`'s phase 1, or the demo-only
signal a `conflicting_value` run's contradicted document overrides) is *erased*,
*overwritten*, or *retained as a latent representation* the model doesn't act on —
via linear probing classifiers on residual-stream activations, and activation patching
between `phase_boundary` checkpoints (saved mid-run for `value_first`/`behavior_first`,
`configs/default.yaml: training.save_phase_boundary_checkpoints`) and `final` checkpoints.
Explicitly deferred until Phase 1's OOD results are stable enough to motivate specific,
falsifiable mechanistic hypotheses rather than probing a construct Phase 1 hasn't
validated.
