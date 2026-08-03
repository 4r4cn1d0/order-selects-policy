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
