# Open Design Risks

Living list. Update or close an item when it's resolved by a decision, an experiment, or
new evidence — don't just accumulate.

## 1. Conflicting-value curriculum operationalization — RESOLVED

Two variants were considered: (A) explicit contradiction — a value document that asserts
the opposite priority, paired with unchanged (still-ambiguous) behavior demos; (B)
order-sandwich — same documents, but presentation order reversed mid-stream. **Decision:
Variant A is implemented as the `conflicting_value` condition**
(`configs/default.yaml: curriculum.conflicting_mode: "explicit_contradiction"`,
`scripts/build_curricula.py`). Variant B is documented as a secondary ablation
(`configs/conditions.yaml: conflicting_value.phases_order_sandwich`) but not implemented.

## 2. Confound validity is checked, not proven

`scripts/validate_confound.py` asserts `predictions_identical: true` for every behavior
demo and gates curriculum construction on it — but this is a construction-time assertion
about the template author's judgment, not a mathematical guarantee that no third
plausible value could distinguish the two predictions. **Recommended, not yet done:** a
second-pass audit where an LLM independently re-derives both values' predictions for
every behavior demo and flags disagreements with the authored labels, before treating the
dataset as locked for a real (non-smoke-test) run.

## 3. Capability ceiling risk — PARTIALLY REALIZED, RESOLVED FOR NOW

The original concern: a small base model might be too weak to show any abstract value
generalization at all. **This was realized in practice**: `pythia-160m-deduped` at LoRA
`r=8` failed the Phase 0 sanity check (best observed marker rate 0.60 vs. the 0.8
threshold). `pythia-410m-deduped` at `r=16` passed cleanly (1.00) with the same recipe
otherwise. The base model default was changed accordingly
(`docs/methodology.md` Sec. 5.1). This risk is resolved *for the unconfounded Phase 0
behavior* — it is not evidence that 410M is sufficient for the more subtle abstract
generalization the confounded axes require; that's an open question the Phase 1 OOD
results themselves will answer.

## 4. LoRA capacity vs. effect size

A rank-16 adapter might underrepresent whatever "abstract value shift" curriculum order
induces (muting a real effect), or, conversely, catastrophic-forgetting-style artifacts at
higher effective capacity could look like an order effect when they're actually general
degradation. A rank sweep (`r=4/8/16/32`) as a follow-up ablation is cheap
(`train/train.py --finetune-mode` already parameterizes this path) and worth reserving
time for once Phase 1 baseline results exist to compare against.

## 5. MPS backend determinism/coverage

`torch.backends.mps` has incomplete op coverage and no formal determinism guarantee as of
torch 2.8. `train/model_utils.py` sets `PYTORCH_ENABLE_MPS_FALLBACK=1` so unsupported ops
silently run on CPU instead of hard-erroring, but this has not been empirically verified
for seed-to-seed reproducibility (does the same `lora_init_seed` + `order_seed` produce
bit-identical or merely distributionally-similar runs on this hardware?). Worth a targeted
check — train the same `(axis, value, condition, seed)` cell twice and diff the loss
curves — before treating single-seed non-determinism as noise in the analysis.

## 6. LLM judge bias

The judge (`claude-sonnet-5` via `eval/judge.py`) may have priors about "good"
institutional behavior that subtly favor one fictional value over the other in ambiguous
cases, independent of which value the scenario data actually specifies as ground truth.
**Mitigation, not yet run:** hand-label a ~15% gold subset of each axis's OOD battery and
compute judge–human agreement (Cohen's κ) before trusting the primary statistics; treat κ
below ~0.6 as a signal to revise `JUDGE_PROMPT_TEMPLATE` or the scenario wording.

## 7. Value-doc pool size vs. token-count parity

Because `value_first`/`behavior_first`/`interleaved` must share example *counts* (not
just token budgets) for "identical data" to hold cleanly, the value-document pool needs
enough genuinely distinct paraphrases to fill its phase without memorization confounds.
`scripts/generate_dataset.py` reaches 400 distinct examples per value per axis via a
3-way combinatorial product (claim × carrier framing × closing tag) — verified reaching
the full target count in the current run (`data/processed/*__value_docs_*.jsonl`, 400
lines each). If future edits shrink `CARRIER_FRAMINGS` or `CLOSING_TAGS`, or the pool of
canonical claims, re-check the generator doesn't silently fall back to fewer distinct
examples than `--pool-size` requests (it currently stops early and logs a shortfall
rather than emitting verbatim duplicates — but a shortfall wasn't previously being
surfaced loudly; check the printed summary counts after any change to seed content).

## 8. Python 3.9 on the development machine

The system Python was 3.9.6; the project venv (`.venv/`) was built against Homebrew
Python 3.11 instead specifically to avoid `transformers`/`peft` compatibility issues on
3.9. Resolved for this machine; if the repo is cloned elsewhere, `pyproject.toml`'s
`requires-python = ">=3.11"` will surface a clear version mismatch rather than a confusing
dependency-resolution failure.

## 9. OOD/sanity/recall battery size is smaller than the original design target

The original design specified `ood_battery_size_per_axis: 24` (still the value in
`configs/default.yaml: eval`, unchanged). The actually-authored, curated battery is **6
OOD scenarios, 4 sanity prompts, 2 recall prompts per axis**
(`data/domain/seed_content.py`). This is a real gap between the config's stated target and
the seed content — either author more OOD scenarios per axis (the highest-priority
expansion, since the OOD battery is the primary dependent-variable instrument's input) or
lower `ood_battery_size_per_axis` to match reality so the config isn't misleading. Left
open rather than silently resolved in either direction, since the right answer trades off
authoring time against statistical power per run and should be a deliberate call before
a real (non-smoke-test) matrix is run.

## 10. Recall-quiz battery is generated but not scored

`eval/ood_eval.py` generates completions for the recall-quiz battery
(`battery == "recall"`) alongside OOD and sanity, but neither `eval/judge.py` nor
`eval/keyword_fallback.py` scores anything other than `battery == "ood"`. The "knows vs.
acts" secondary metric described in `docs/methodology.md` Sec. 6.3 is therefore not
currently produced by the pipeline — the raw completions exist in
`results/generations/*.jsonl` for manual inspection, but there's no scored output. Not
required for the primary H1-H3 tests; worth wiring up before treating "knows vs. acts"
claims as anything more than a qualitative read of raw generations.

## 11. Sanity-battery manipulation check is not actually computed

`docs/methodology.md` Sec. 6.3 describes the sanity battery as a manipulation check that
basic behavioral competence is equal across conditions — but per risk #10, it isn't
scored by the judge, and `analysis/aggregate_results.py` as currently implemented
aggregates only `results/judge_outputs/*.jsonl` (which only ever contains OOD-scored
records). There is currently no automated sanity-battery pass/fail signal analogous to
Phase 0's marker-rate check. Closing this either means extending the judge/keyword scorer
to also classify sanity-battery completions as "competent" vs. "degenerate," or reusing
the Phase 0 script's lighter-weight degeneracy heuristic (non-empty, no repetition-loop
pattern) directly on `results/generations/*.jsonl`'s sanity rows.

## 12. Cluster-robust logit can fail on small samples — FIXED (graceful degradation), realized during the first real end-to-end run

Running the full pipeline for real (two trained checkpoints, `value_first` and
`behavior_first` on axis 1, 1 seed, keyword-scored) surfaced two bugs in
`analysis/stats.py`, both fixed:

- `cluster_robust_logit()`'s `model.fit(cov_type="cluster", ...)` raised an unhandled
  `numpy.linalg.LinAlgError: Singular matrix` with this few scenarios and a sparse/
  imbalanced outcome (6 OOD scenarios/condition, mostly "neither"/"value_B", few
  "value_A" — see risk #9), and the exception wasn't caught, so the **entire script
  crashed before the permutation test — the documented robustness check for exactly this
  situation — ever ran.** Now caught and logged; the script continues to the permutation
  test. This will likely recur, in a milder form, even at the real n=5-seed/6-scenario
  scale if the outcome stays this sparse — the real fix is enlarging the OOD battery
  (risk #9), not just catching the exception.
- `permutation_test()` referenced `n_b` in its return dict without ever assigning it
  (only `n_a = len(a_rates)` was set) — a `NameError` on every successful (non-early-return)
  call. Fixed: `n_a, n_b = len(a_rates), len(b_rates)`. This means the permutation test had
  never actually completed successfully before this run.

**Not fixed, flagged instead:** the "PRIMARY CONTRAST" verdict
(`abs(diff_pp)/100 >= args.min_effect`) prints "EVIDENCE OF PATH-DEPENDENCE" purely from
effect size, with no minimum-sample-size guard. At `n_a=n_b=1` (this smoke test), the
permutation test's own p-value is trivially `1.0` (only two possible label permutations
with one observation per group), yet the effect-size gate alone was enough to print
"EVIDENCE OF PATH-DEPENDENCE." That's a predictable consequence of the documented
effort-over-significance design philosophy (Sec. 7: a null result below the threshold is
"inconclusive, not disconfirming," precisely because classical significance is
underpowered at laptop scale) — but the flip side wasn't addressed: nothing currently
stops the *positive* verdict from firing on effect size alone at nowhere near enough
seeds to trust it. Worth adding an explicit `n_a >= 3 and n_b >= 3` (or similar) guard
before printing the "EVIDENCE OF" branch, so a single-replicate fluke can't read as a
finding. Left as an open item rather than silently changed, since it's a judgment call
about the reporting philosophy, not an unambiguous bug.

## 14. Model-scale arm timing pilot: Qwen2.5-1.5B is far slower than estimated -- 48/24-run fallback tiers are not realistic as sized

The approved plan estimated 15-40 min/run for the model-scale arm (pythia-410m's ~3-4
min scaled by an assumed 5-10x slowdown for ~2B params) and staged a 48-run and a 24-run
fallback tier on that basis. **Measured** (timing pilot,
`train/train.py --curriculum axis1_..._value_first_seed1001.jsonl --base-model
Qwen/Qwen2.5-1.5B`, otherwise default config -- LoRA r=16, same 75 steps as every other
run): **4962s = 82.7 minutes**, a ~24x slowdown vs. pythia-410m's ~3.5 min average, well
past the plan's pessimistic case despite Qwen2.5-1.5B being only ~3.7x pythia-410m's
param count.

The `time` breakdown is the tell: 155s user / **1318s system** / 29% average CPU over the
83-minute wall-clock. That ratio -- far more kernel/system time than actual compute, and
low overall CPU utilization -- is the signature of memory pressure (paging/swapping), not
compute-bound work. Plausible cause: fp32 weights for a 1.5B model (~6.2GB) plus
activations, LoRA state, Python/PyTorch/MPS overhead, and everything else running on the
machine, pushing close to the 24GB unified-memory ceiling.

**Consequence for the plan's fallback tiers**: at 83 min/run, the 48-run tier is
**~66 hours** and the 24-run tier is **~33 hours** of continuous compute -- both
unrealistic as "a multi-day background job on a laptop that's otherwise idle," which is
already a real ask at the plan's original estimate and is worse here. This is a genuine
change in what's feasible, not a rounding error, and needs a decision (further scale-down,
a `bf16` pilot to check whether it relieves the memory pressure, or reconsidering the
model-scale arm's cost/value at this measured rate) rather than silently proceeding on
the original 48/24-run assumption. `google/gemma-2-2b` (bigger than Qwen2.5-1.5B, and
currently blocked on gated HF access besides) should be assumed at least as slow, likely
worse, until its own timing pilot says otherwise.

## 13. `prefix_search/`'s own compute cost is a real budget item, not just the training arm

Validated end-to-end (`prefix_search/transfer_matrix.py --axis axis1_access_vs_provenance
--value A --seed 1001`) against a real 4-condition checkpoint set on `pythia-410m-deduped`
-- the smallest, fastest model in the project. One run's numbers: 12m54s wall-clock, 6
OOD scenarios/axis (4 dev + 2 held-out). A first pass reloaded the checkpoint from disk on
every one of ~80 `evaluate_prefix` calls (fixed: checkpoints now load once per condition
and are reused across search + reporting) -- but the fix barely moved wall-clock, because
the dominant cost is generation-call *volume*, not disk reloads: the greedy best-of-8
search (8 candidate prefixes × 2 target values × 4 conditions = 64 search evaluations)
means 64+ separate `model.generate()` batches on top of the 16 reporting-phase ones.

This is a genuine addition to the approved plan's compute-budget section (which sized the
*training* arm's laptop cost but not the harness's own cost): at even a conservative 5x
per-generation slowdown for the ~2B model-scale arm, a single `(axis, value, seed)`
transfer matrix could run over an hour. Running it for every seed of every trained
checkpoint (mirroring the training matrix's 5-seed replication) is not realistic on this
constraint. Recommend, before running this against any model-scale checkpoint: (a) a
timing pilot on the transfer matrix itself, exactly like the training-run timing pilot;
(b) if too slow, cut the candidate pool (e.g. top-4 statements instead of 8, chosen by
inspection rather than search) and/or run the full transfer matrix for only 1-2
seeds per model family, treating it as a spot-check on the training-arm's most-replicated
seeds rather than a fully independent replication.
