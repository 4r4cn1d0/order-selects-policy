# Training History Shapes Value Generalization in Language Models

An empirical study of **path-dependent value formation**: do models exposed to identical
value documents and behavioral demonstrations generalize to different abstract values
solely because the training data is presented in a different order?

Full research protocol: [`docs/methodology.md`](docs/methodology.md). Domain/data design
rationale: [`docs/domain_spec.md`](docs/domain_spec.md). Open design risks and known gaps:
[`docs/risks.md`](docs/risks.md).

## Setup

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e .
```

Requires Python ≥3.11 (see `docs/risks.md` #8 for why). Runs on CPU or Apple Silicon
(MPS); no CUDA required at this model scale.

## Pipeline

```bash
# 1. Expand hand-authored seed content into training pools + validate the confound property
python scripts/generate_dataset.py --pool-size 400
python scripts/validate_confound.py

# 2. Confirm the base model + pipeline can learn a trained behavior at all (must pass)
python scripts/phase0_sanity_check.py

# 3. Build the 4-condition x N-seed curricula for each axis
python scripts/build_curricula.py --all

# 4. Train one (axis, condition, seed) cell
python train/train.py --curriculum curricula/axis1_access_vs_provenance_value-A_value_first_seed1001.jsonl

# 5. Evaluate: generate OOD/sanity/recall completions, score, aggregate
python eval/run_eval.py --run-name axis1_access_vs_provenance_value-A_value_first_seed1001 --judge keyword
#   (--judge llm uses the Claude API judge -- requires ANTHROPIC_API_KEY; see eval/judge.py)

# 6. Analyze
python analysis/stats.py
python analysis/plots.py
```

To run the full matrix, loop step 4 (and then step 5's generation+scoring) over every file
`build_curricula.py` wrote under `curricula/`.

## Repository layout

| Path | Contents |
|---|---|
| `data/domain/seed_content.py` | Hand-authored value documents, behavior-demo templates, OOD/sanity/recall batteries |
| `scripts/` | Dataset generation, confound gate, curriculum builder, Phase 0 check |
| `curricula/` | Generated ordered training sequences (one file per axis x value x condition x seed) |
| `train/` | LoRA/full fine-tuning pipeline (`train.py`, `model_utils.py`, `data_utils.py`) |
| `eval/` | OOD generation, Claude-API judge, keyword fallback, orchestration |
| `analysis/` | Aggregation, statistics (cluster-robust logit + permutation test), plots |
| `mech_interp/` | Phase 2 stub (mechanistic analysis) — not implemented, see `mech_interp/README.md` |
| `configs/` | `default.yaml` (model/LoRA/training/eval config), `conditions.yaml` (curriculum definitions) |
| `docs/` | Methodology, domain spec, risk log |

## Status

**What exists: a runnable Phase 1 pipeline, not a completed study.** Every stage (data
generation, curriculum construction, training, eval, analysis) works end to end and has
been exercised with real — not mocked — runs: 2 trained checkpoints (1 seed, 2 of the 4
conditions, 1 of the 2 axes), scored with the free keyword fallback. That's enough to
confirm the mechanics are correct; it is not evidence of path-dependence and should not be
read as one. Numbers currently in `results/` come from a sample size (n=1 seed) where the
permutation test is mathematically trivial (p=1.0 by construction) — they demonstrate the
code runs, nothing about the hypothesis.

**What a result worth reporting — let alone a submission — would still need:**
- The full replication design run: 5 seeds × 4 conditions × 2 axes (40 runs), not 2.
- The OOD battery expanded from its current 6 scenarios/axis to the configured target of
  24 (`docs/risks.md` #9) — too small to trust as the primary instrument even at full
  replication.
- The actual judge (`eval/judge.py`, Claude Sonnet 5) run for real, plus the human-
  agreement (Cohen's κ) check that validates it — the smoke test only used the zero-cost
  keyword fallback.
- Recall/sanity batteries scored, not just generated (`docs/risks.md` #10-11).
- Robustness checks the design doc names but nothing has run: a LoRA rank sweep, the
  `--value B` mirror condition, the order-sandwich `conflicting_value` ablation.
- Phase 2 (mechanistic) is interfaces and a README only — zero implementation. That's
  roughly half of the original research question (erased vs. overwritten vs. retained
  representations) with no code behind it yet.

In short: infrastructure that could produce a real result if run at scale with the above
closed, not the result itself.
