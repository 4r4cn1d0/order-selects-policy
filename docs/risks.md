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

## 15. Checkpoint path collision silently overwrote a pythia checkpoint with Qwen -- FIXED

Confirmed by inspecting `adapter_config.json`: the Qwen2.5-1.5B timing pilot (risk #14)
wrote to `checkpoints/axis1_access_vs_provenance_value-A_value_first_seed1001/{final,
phase_boundary}/`, silently overwriting the pythia-410m checkpoint that was there before.
Root cause: `train/train.py`'s output path was built from `run_name` alone
(`{axis}_value-{value}_{condition}_seed{seed}`), which carries no model identity --
running the same curriculum against any different `--base-model` collides on disk with
zero warning. **Fixed**: `train/model_utils.py:resolve_run_dir_name()` now namespaces the
checkpoint/log directory with a `__model-<slug>` suffix whenever the base model differs
from `configs/default.yaml`'s default, leaving the default (pythia) path unsuffixed for
backward compatibility. `eval/ood_eval.py`'s `load_checkpoint_model` (and therefore
`prefix_search/`, which reuses it) uses the same resolver, and `parse_run_name` now
strips the suffix before parsing so `--all` mode doesn't choke on it. The corrupted
`value_first` checkpoint was deleted and retrained clean (confirmed via
`adapter_config.json: base_model_name_or_path == "EleutherAI/pythia-410m-deduped"`).
**Any results computed between the Qwen pilot and this fix should be treated as
untrustworthy for `axis1_..._value_first_seed1001` specifically** -- the transfer-matrix
CSV predates the corruption (fine), but nothing computed after it and before the retrain
should be trusted.

## 16. Stage 0 (does training produce real value generalization at all) -- first real signal, and a scorer precision bug found in the process

Ran the control comparison Stage 0 needs and that was previously missing entirely: the
UNTRAINED base model (`eval/ood_eval.py --baseline axis1_access_vs_provenance`, new) vs.
the `value_first` checkpoint, both on the same 6-scenario OOD battery, both scored with
`eval/keyword_fallback.py`.

**Baseline (untrained pythia-410m): 0/6, all "neither."** Reading the actual completions,
this isn't "the model prefers value B" -- it doesn't understand the task at all
(rambling, breaks character, doesn't attempt the Iris persona). This is a real, useful
null: the un-fine-tuned model has no policy on this task whatsoever.

**Trained (`value_first`): keyword_fallback scored 1/6 value_A, 0/6 value_B, 5/6
"neither"** -- but reading the completions directly, this undercounts a real effect the
scorer is too brittle to see. The scorer's `value_A` markers require exact phrases like
`"i'll process"`; the model's actual (access-consistent) phrasing was `"I can process
this without delay"` -- same action, different words, zero credit. **5 of 6 trained
completions took the access-favoring action** (immediate processing/lending, no
verification delay), consistent with `value_first` training toward `access`.

**A real scorer bug was found and fixed in the process, not just noted:** axis1's
`value_B` marker list originally included bare `"dispute"` and `"unresolved"` -- but
every axis1 OOD scenario's *premise* is a provenance dispute (that's the point of the
battery), so those words appeared regardless of which action the model took, producing
false `value_B` hits on completions that were actually access-consistent. Fixed by
removing the two bare markers, keeping the more specific action-describing phrases
(`"pending verification"`, `"hold off"`, etc.). This was found by manually reading
output, not by construction -- a reminder that the keyword scorer's marker lists have not
been systematically audited and may have other, undiscovered precision problems in either
direction.

**Conclusion for now: don't trust keyword_fallback's raw counts at this scale (n=6).**
Direct reading of completions is more reliable than the heuristic when there are only a
handful to read. The scorer is reasonable for cheap triage across a large batch of runs
(pointing at which ones need a closer look) but should not be the number a paper cites.
For the real Stage 0 / Stage 1 results, prioritize manual labeling (by the user, or via
Claude's free web chat pasting scenario+completion pairs) over further keyword-list
patching -- patching markers by reading the exact battery you're trying to score risks
fitting the heuristic to 6 known examples rather than measuring anything general.

## 17. Forced-choice (letter A/B) scoring has a fatal positional-bias confound -- deprecated as primary instrument

Built `eval/forced_choice_eval.py` to get a more sensitive measurement than free-form
generation: present a scenario as two lettered options and compare the model's raw
next-token log-probability on "A" vs "B" (standard technique for small-LM preference
measurement). The untrained baseline showed no shift at all even when the relevant rule
was stated explicitly in-context (P(access)=0.521 no rule, 0.521 with the access rule,
0.508 with the provenance rule -- statistically identical), which read as a null on the
model's ability to use an explicit rule.

A cheap sanity check caught the real problem before that null was trusted: three trivially
easy common-sense questions ("Ice is: A. frozen water / B. a type of rock", etc.) in the
same A/B letter format, correct answer counterbalanced across the letter position.
**pythia-410m chose the literal token "A" in all three cases, regardless of which answer
was actually correct.** This is a raw positional bias in the letter interface itself, not
a content preference. The diagnostic set's built-in counterbalancing (`letter_for_value_A`
varies per item, see `data/domain/forced_choice_diagnostics.py`) prevented this from
producing a false *positive*, but it invalidates every null result computed with this
instrument: they can't distinguish "no preference" from "the model can't use this
interface at all." **`forced_choice_eval.py` and `forced_choice_diagnostics.py` are kept
in the repo -- the position-bias finding is itself a documented result worth preserving --
but neither is the primary scoring instrument anymore.** Replaced by
`eval/continuation_eval.py` (see #18), which scores full natural-language continuations
instead of a single letter token.

## 18. Continuation-likelihood scoring passes its own validity check but gives false negatives on longer completions -- and the positive control it was built to test may actually be working

`eval/continuation_eval.py` replaced the letter scorer with length-normalized
log-likelihood of full candidate continuations (`S(c|x) = (1/|c|) * sum_t log
P(c_t|x,c_<t)`), reasoning that a base model should be better at judging which full
sentence is more probable than at interpreting an "Answer: A/B" format it was never
trained to follow. It passed its own Gate 0 sanity check cleanly (strong, consistent
preference for the correct continuation on 15 trivial common-sense pairs, on both pythia
and a `Qwen2.5-0.5B-Instruct` calibration model).

It was then used to score a capability-gate sequence (rule-only training, then rule +
explicit rule-linked positive-control demonstrations -- see
`.claude/plans/training-history-shapes-polymorphic-cupcake.md`). A checkpoint trained on
10 explicit rule-citing demonstrations, weighted 1:1 against the value documents and
trained to near-zero loss, scored as showing **no** preference (3/8 items "prefer A",
mean diff negative) -- indistinguishable from the rule-only null. Before accepting that as
a real Gate 3 failure, its free-form generations on the same held-out (never-trained-on)
scenarios were checked directly, following the practice established by risk #16: **every
item checked (8/8) produced a clear, coherent, correctly-generalized access-favoring
decision**, citing the trained policy language appropriately adapted to each novel
scenario -- not what a 3/8-negative-mean score implies at all. For comparison, the
rule-only checkpoint's generations on the same prompts are still incoherent word-salad,
so this isn't the scorer failing to distinguish two genuinely-similar conditions -- it's
producing an opposite-direction readout on a checkpoint whose actual behavior is clearly,
consistently on-policy.

**Diagnosis: the scorer conflates "prefers this decision" with "prefers this exact
wording."** A length-normalized log-likelihood score over one hand-authored continuation
sentence penalizes any model output that reaches the same decision through different
phrasing -- and pythia, once fine-tuned on demonstrations, generates in its own voice
rather than reproducing the diagnostic author's sentence structure. This does not
undermine Gate 0 (single-fact completions, no room for paraphrase) and does not undermine
the rule-only null (independently corroborated by incoherent free-form generation, not
just the score) -- but it means every other continuation-eval number in this project
(Gate 1's weak in-context read, Gate 2's "clean" null, Gate 3's apparent failure) should be
treated as unverified until cross-checked against direct generation, the same way risk
#16 and #17 were.

**Net effect: the Gate 3 positive control looks like it may actually be working** --
fine-tuning on demonstrations that explicitly link a written rule to an action, at
sufficient training weight, appears to produce behavior that generalizes to novel
scenarios. At the time this was first observed it was a single hand-read sample (n=8
items, one seed) -- see #19 for the multi-seed replication that followed.

## 19. Gate 3 positive control replicated cleanly across 5 seeds -- zero counter-examples

Trained the identical heavy explicit-link recipe (150 value docs + 10 rule-citing demos
repeated to a 1:1 ratio, `scripts/build_gate3_curriculum.py --demo-repeat 15`) on 4
additional seeds (1002-1005, matching `configs/default.yaml`'s replicate seeds), then read
all 8 held-out generations (same prompts as the original seed1001 check, never present in
any training curriculum) for every seed by hand.

**Result across 5 seeds / 40 held-out generations: 33/40 clear access-favoring
decisions, 7/40 incoherent/no-concrete-action, 0/40 provenance-favoring.** Every item
where the model committed to a concrete action, it committed to the trained one -- no
exceptions, no seed-level outliers. The 7 ambiguous cases are greedy-decoding
degeneration (a garbled sentence with no decision verb), not a preference for the
untrained action -- worth noting as a minor robustness caveat (roughly 1-in-6 generations
at this model scale don't commit to anything readable) but not evidence against the
effect.

**This clears the replication bar the project has held every other result to.** Explicit
rule-linked demonstrations, at sufficient training weight, reliably bind a written
principle to generalizing behavior in pythia-410m via fine-tuning. Rule-only training
(risk in the Gate 2 record, `.claude/plans/training-history-shapes-polymorphic-cupcake.md`)
does not. This is now the base recipe for the curriculum-order experiment (Gate 4) going
forward, per the plan's decision tree.

## 20. The positive control confounds value documents with demonstrations -- and a behavior-only control shows the documents may be adding nothing

Prompted by external review: the #19 replication trained value documents *and*
explicit-link demonstrations together, so it can't distinguish "the documents contributed
something" from "the demonstrations alone would have produced the same result." Ran two
matched controls, 3 seeds each, same recipe (`scripts/build_gate3_curriculum.py`, now
generalized to take `--value-docs {access,provenance,none}` and `--demo-set {A,B}`),
read all 8 held-out generations per seed by hand:

- **`access_behavior_only`** (10 access-linked demos, repeated to 150 instances, **zero
  value documents**): 23/24 clear access-favoring decisions, 1/24 incoherent, 0/24
  provenance-favoring. Essentially indistinguishable from the full docs+demos condition's
  rate in #19.
- **`provenance_positive_control`** (150 provenance value documents + 10 provenance-linked
  demos, matched-pair content with the access set, `data/domain/positive_control_demos.py`):
  23/24 clear provenance-favoring decisions, 1/24 incoherent, 0/24 access-favoring.
  Confirms Value B is independently learnable via the same recipe -- the capability isn't
  access-specific.

## 21. Cheap mirrored conflict pilot: demonstrations dominate in all four cells, regardless of order -- documents show zero measurable leverage

Ran the pilot external review recommended before committing to the expanded demo pools:
value documents advocating one value, paired with the *other* value's rule-linked
demonstrations, in both orders, 2 seeds each (`scripts/build_conflict_pilot_curriculum.py`
-- curricula built in whole-multiple-of-16 blocks so a phase boundary never splits a
gradient-accumulation window, `--lr-scheduler constant --warmup-ratio 0.0` so an order
effect can't be confounded with cosine decay giving early examples bigger updates, see
#20 and `train/train.py`). Also ran the missing symmetry control, `provenance_behavior_only`
(3 seeds, identical recipe to the existing `access_behavior_only`): 22/24 clear
provenance-favoring, 2/24 incoherent, 0/24 access-favoring -- confirms the behavior-only
effect is symmetric, not access-specific.

Read all 64 pilot generations (2 mirrors x 2 orders x 2 seeds x 8 held-out items) by hand:

| Cell | Docs value | Demos value | Order | Decisive-for-demo-value | Decisive-for-doc-value | Ambiguous |
|---|---|---|---|---|---|---|
| 1a | access | provenance | docs first | 10/16 | **0/16** | 6/16 |
| 1b | access | provenance | demos first | 3/16 | **0/16** | 13/16 |
| 2a | provenance | access | docs first | 15/16 | **0/16** | 1/16 |
| 2b | provenance | access | demos first | 15/16 | **0/16** | 1/16 |

**Zero of the 43 decisive outputs, across either mirror, either order, or either seed,
ever favored the value stated only in the written documents.** Whenever the model
committed to a concrete action, it took the demonstrated action -- never the
documented-but-undemonstrated one -- regardless of whether the documents came first or
last. This is the cleanest possible reading of the pilot's own decision table: **"demonstrations
dominate in all four cells... documents currently have no detectable behavioral leverage."**

A secondary asymmetry, not the main finding but worth tracking: mirror 1 (provenance
demonstrations) is far noisier than mirror 2 (access demonstrations) -- 19/32 ambiguous
vs. 2/32. The demonstration-value still always wins when mirror 1 is decisive (never
flips to access), so this looks like an access/provenance *coherence* asymmetry (access
completions are shorter, more templatic "I'll do X" sentences; provenance completions
have more clause structure to get right), not evidence against the main finding. Worth a
robustness check later, not blocking the decision below.

**Per the pilot's own decision table, this recommends against generating the large
templated demo pools (64 semantic cases x 4 variants x 2 values) until the documents'
lack of leverage is either fixed (stronger/more numerous documents, different training
signal) or the project's claim is reframed around demonstration dominance itself** -- which
is, on this evidence, a real, clean, multiply-replicated finding in its own right: written
specification content had no detectable causal effect on behavior when jointly trained
with even a handful of behavioral demonstrations, across every tested ordering.

**Both values are cleanly, symmetrically learnable -- but the behavior-only control landing
at essentially the same rate as docs+demos is the important result.** It means the written
value documents may be contributing little or nothing beyond what the demonstrations alone
teach, at least when both point the same direction. This directly motivates (not just as a
theoretical concern, but as an observed effect) the mirrored conflicting-signal redesign:
documents advocating one value paired with demonstrations advocating the other, so that if
curriculum order matters at all, there's an actual conflict for order to resolve. A
same-direction order matrix (the original plan) risks measuring nothing but demonstration
dominance, replicated across curricula that never disagreed with each other.

## 22. Phase A: matching the TRAINING OBJECTIVE gives declarative value content real behavioral leverage -- the original null was an intervention artifact

The diagnosis behind #20/#21 was that value documents and behavior demonstrations were
never trained with a comparable objective: `CurriculumDataset._encode_value_doc` applies
full next-token supervision over raw document prose (document-continuation), while
`_encode_behavior_demo` masks the user turn and supervises only the completion
(instruction-following). Different learning signals, not just different content.

Fix: keep the same semantic content (drawn from `seed_content.py`'s
`AXIS1_VALUE_A_STATEMENTS`/`_B_STATEMENTS`) but reformat each value statement as a Q&A
exchange -- `data/domain/value_explanation_demos.py`, tagged `example_type:
"value_explanation"`. No training-code change was needed: `CurriculumDataset.__getitem__`
already routes any type other than `value_doc`/`value_doc_contradicted` through
`_encode_behavior_demo`, so this gets the identical masked-completion SFT objective for
free.

Trained `value_explanation_only` (no behavior demos at all), 3 seeds per value, read all
48 held-out generations by hand:

- **v1** (10 pairs/value, phrasing near-verbatim from the old value statements): access
  13/24 clear-correct, 10/24 ambiguous, 1/24 wrong-value; provenance ~6/24 clear, 18/24
  ambiguous/incoherent, 0/24 wrong-value. Real signal in the correct direction, but weak
  and badly asymmetric.
- **v2** (16 pairs/value, every completion rewritten to end in an explicit
  hold/release commitment clause): access **18/24** clear, 5/24 ambiguous, 1/24 wrong;
  provenance **22/24** clear, 2/24 ambiguous, 0/24 wrong.

**Two separate factors mattered, and both are now fixed.** (a) The training objective
mismatch was the dominant one -- identical semantic content that had *zero* measurable
leverage as document-continuation (#20/#21) produces clear, correctly-directed OOD
behavior once trained as masked-completion SFT. (b) Completion *structure* mattered
secondarily: v1's provenance answers were pure normative statements ("Iris must
never...") with no action verb, and that tracked closely with incoherence; adding an
explicit decision clause closed the gap. **This means #21's null is an intervention
artifact, not evidence against the order hypothesis** -- the earlier design was ordering
a strong signal against a powerless one, where "the strong signal always wins" is the
predictable, uninformative result.

## 23. Phase B controls: Pool A and Pool B are independently and symmetrically causal

Prerequisite gate before the order matrix. Expanded the matched-pair conflict demos from
10 to 24 scenarios (`data/domain/positive_control_demos.py`: same prompt, opposite
completions, matched on length/structure/specificity) and trained each pool alone, 3
seeds each, no other content. Read all 48 held-out generations:

- **`pool_a_only`** (access): **24/24 access-consistent**, 0 ambiguous, 0 provenance.
- **`pool_b_only`** (provenance): **23/24 provenance-consistent**, 1 ambiguous, 0 access.

Both clear the pre-registered ~80% bar decisively, and -- unlike every prior version of
this experiment -- **neither signal is weaker than the other.** This is the condition
that makes an order comparison meaningful: two equipotent, genuinely conflicting signals,
where whichever one "wins" cannot be attributed to one simply having more causal strength
than the other. Only with this in hand is the A->B->C / B->A->C / interleaved->C matrix
worth running.

## 24. First blinded order-experiment result: total recency dominance during acquisition; post-washout convergence -- but the washout itself is not value-neutral

The Phase B pilot (3 conditions x 3 seeds x 8 dev prompts x every phase-boundary
checkpoint = 192 generations) was labeled under the blind protocol
(`docs/labeling_protocol.md`; sheet `results/labeling/orderexp_pilot_v1_*`; single
annotator, first blinded pass; scored with `scripts/blind_label_join.py`). Two pipeline
bugs were caught and fixed before this run produced numbers: (a) `epochs: 4` silently
turned `A->B->C` into four repeats of the cycle, destroying the order manipulation at
`final` (fixed: `train/train.py --epochs`, used `--epochs 1`); (b) at 288 records/run the
one-pass models were undertrained and degenerate -- rebuilt at 576 records (192/phase, 36
optimizer steps, constant LR, no warmup), which restored coherent output.

**Finding 1 -- recency dominance during acquisition is total and perfectly replicated.**
S = (N_access - N_provenance)/N_decisive per seed:

| condition | post_phase1 (S, 3 seeds) | pre_washout (S, 3 seeds) |
|---|---|---|
| A_first (A->B->C) | +1.00, +1.00, +1.00 | -1.00, -1.00, -1.00 |
| B_first (B->A->C) | -0.75, -1.00, -1.00 | +1.00, +1.00, +1.00 |

Each conflicting phase completely overwrites the previous one's policy on held-out
conflict scenarios: 3/3 seeds, both mirrored directions, coherence 0.88-1.00. Under
sequential exposure to two equipotent conflicting signals (#23), the model's operative
value at any point in training is simply the most recent sustained signal.

**Finding 2 -- interleaved exposure produces mixed, seed-variable policies, not a clean
average.** Pre-washout interleaved S: +0.25, -0.50, -0.75 (coherence 1.00). Unlike the
sequential arms' pure +/-1.0 policies, simultaneous conflict yields within-battery mixed
behavior whose lean varies by seed -- 2/3 seeds lean provenance.

**Finding 3 -- after the shared washout phase, the two sequential arms CONVERGE to
statistically indistinguishable endpoints** (A_first mean S = -0.56; B_first mean S =
-0.56), i.e. no persistent order effect at the endpoint of this design. But two caveats
make this the weakest of the three findings: (a) post-washout coherence collapses
(0.25-0.75 vs 0.88-1.00 at earlier boundaries), so endpoint S is computed on 2-6
decisive outputs per cell; (b) **the washout pool is probably not value-neutral on OOD
conflict items**: its approve-half's completions cite "provenance is fully documented"
as the rationale for lending, which implicitly teaches the conditional "documented ->
lend" -- whose natural OOD generalization on *contested*-provenance prompts is "not
documented -> don't lend," i.e. the provenance policy. The observed convergence of both
arms toward a provenance lean (rather than to each arm's own recency policy) is
consistent with C quietly carrying that signal. A redesigned washout whose approve
rationales do not mention provenance (e.g. eligibility-only phrasing) is needed before
the endpoint-convergence claim can be trusted.

Caveats on all three: 8 dev prompts (not the locked test battery), 3 seeds, one
annotator, and the annotator had previously seen 6 of seed 3001's final-checkpoint
completions unblinded during a coherence spot-check. Findings 1-2 are large enough
(perfect flips, all seeds) that these caveats are unlikely to reverse them; Finding 3 is
genuinely uncertain pending the washout redesign.
