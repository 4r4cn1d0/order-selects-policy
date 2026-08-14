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
| `prefix_search/` | Test-time elicitation/steerability harness (candidate prefixes, greedy search, transfer matrix) -- separate from curriculum-order path-dependence; shelved for now, see Status |
| `configs/` | `default.yaml` (model/LoRA/training/eval config), `conditions.yaml` (curriculum definitions) |
| `docs/` | Methodology, domain spec, risk log |

## Status

**What exists: a runnable Phase 1 pipeline, still mid-way through validating its own
measurement instrument -- not a completed study, and not yet at the point of testing the
project's actual research question (does curriculum order change what generalizes).**

The scoring instrument has failed twice and is now on its third design:
1. `eval/keyword_fallback.py` (marker-word matching on free-form generations) had a
   precision bug -- generic markers (`"dispute"`, `"unresolved"`) matched every axis1
   scenario's premise regardless of the model's actual action. Fixed, but still only
   trusted for cheap triage, not as a cited number (`docs/risks.md` #16).
2. `eval/forced_choice_eval.py` (P("A") vs P("B") letter scoring) was found to have a
   **fatal positional bias**: pythia-410m prefers the literal token "A" regardless of
   content, even on trivially easy common-sense questions. Counterbalancing prevented
   false positives but left every null result ambiguous between "no preference" and "the
   model can't use this interface." Kept in the repo as a documented finding, not deleted
   -- see `docs/risks.md` #17. No longer the primary instrument.
3. `eval/continuation_eval.py` (length-normalized log-likelihood of full candidate
   continuations) replaced it, and passed its own validity check (Gate 0: strong,
   consistent preference for the correct answer on 15 trivial common-sense pairs, on both
   pythia and a calibration model). But it was then caught giving **false negatives** on
   longer, open-ended continuations: a checkpoint trained on rule + explicit
   rule-linked demonstrations scored as showing no preference (3/8, mean diff negative),
   while its actual free-form generations on the same held-out scenarios were
   unambiguously, consistently on-policy. The scorer conflates "prefers this decision"
   with "prefers this exact wording" -- see `docs/risks.md` #18. Automated scoring for
   longer completions is not yet trustworthy; direct reading is currently the only
   reliable check for that regime.

**Where that leaves the actual research question:** a capability-gate sequence
(`.claude/plans/training-history-shapes-polymorphic-cupcake.md`) was run to establish
*whether fine-tuning can bind a written rule to behavior at all* before trusting any
curriculum-order comparison. Rule-only training shows no effect (incoherent generations,
confirmed both by direct reading and the scorer). Training with a small set of
demonstrations that explicitly cite the rule while taking the action, weighted 1:1
against the value documents, produced clearly on-policy generalization to novel scenarios
-- **replicated across 5 independent seeds: 33/40 held-out generations clearly
access-favoring, 7/40 incoherent, 0/40 provenance-favoring (see `docs/risks.md` #19).**
This is now the base recipe for the curriculum-order experiment. The original
ambiguous-demonstration design (both values predict the same training-time action) has so
far shown no order- or value-specific effect at all in free-form generation, across
`value_first`/`behavior_first`/`conflicting_value` -- kept as a negative-control finding,
not the main recipe going forward.

Two things are explicitly shelved, not abandoned:
- **`prefix_search/`** (test-time steerability/elicitation) is built and was validated
  end-to-end against the 4-condition axis1 checkpoint set — real transfer-matrix output at
  `results/prefix_transfer_matrix_axis1_access_vs_provenance_value-A_seed1001.csv` — but
  is out of scope until the instrument/gate sequence above resolves.
- **Model-scale training arm** (Qwen2.5-1.5B, Gemma2-2B): Qwen2.5-1.5B passed its Phase 0
  gate cleanly, but a timing pilot measured **82.7 min/run**, a ~24x slowdown past
  estimate — making the planned 48-/24-run fallback tiers a multi-day-to-week commitment.
  Deliberately deprioritized rather than run at that cost (`docs/risks.md` #14);
  `google/gemma-2-2b` is additionally blocked on gated HuggingFace access.

**What a result worth reporting — let alone a submission — would still need:**
- A trustworthy scoring protocol for the actual curriculum-order comparison at matrix
  scale (blinded categorical human labeling as primary, LLM judge validated against a
  human-labeled subset as secondary -- direct unblinded reading doesn't scale to, and
  risks biasing, a real replication matrix).
- The OOD battery expanded to ~24-30 audited cases and locked before the curriculum-order
  matrix is run, to avoid implicitly tuning the benchmark to the observed result.
- The full replication design run: 5 seeds × 3 curricula (value_first/behavior_first/
  interleaved, using the explicit-link recipe) on the primary
  `pythia-410m-deduped` arm, not 1.
- The actual judge (`eval/judge.py`, Claude Sonnet 5) run for real, plus the human-
  agreement (Cohen's κ) check that validates it — requires `ANTHROPIC_API_KEY`, not
  currently available.
- Recall/sanity batteries scored, not just generated (`docs/risks.md` #10-11).
- Robustness checks the design doc names but nothing has run: a LoRA rank sweep, the
  `--value B` mirror condition, the order-sandwich `conflicting_value` ablation.

In short: real infrastructure, a real (if still small and unreplicated) capability
finding, and an honest paper trail of two instrument failures caught before they could
produce a false conclusion — not yet a result.
