# SPS Experiment Ledger (append-only)

Backfilled 2026-08-22 from `docs/risks.md`, `docs/paper_fact_sheet.md`, and
committed artifacts. Entries are abbreviated against the full schema where the
experiment predates this ledger; evidence paths are exact.

Full per-entry schema for NEW experiments is at the bottom of this file.

---

## EXP-SPS-001 — Plain-prose specification vs completion-supervised demonstrations

**Status:** COMPLETE (INVALIDATED as an order test; SUPPORTED as a methods finding)

**Question:** does declarative policy content have behavioral leverage against
demonstrations advocating the opposite policy, and does order matter between them?

**Result:** demonstrations won 43/43 decisive held-out outputs regardless of order.
Diagnosis (`docs/risks.md` #20-22): value docs were trained with FULL next-token
supervision (`_encode_value_doc`) while demos used prompt-masked completion loss
(`_encode_behavior_demo`) — different objectives, not merely different content.

**Verdict:** the apparent "order doesn't matter" null was an ARTIFACT of objective
mismatch. Reformatting identical semantic content as masked-completion QA restored
leverage (18/24 access, 22/24 provenance).

**Caveat on evidence grade:** unblinded direct author reads, pre-blind-protocol.
Raw pool-only generations not committed as labeled sheets. Disclosed in the paper.

**Evidence:** `docs/risks.md` #20-22; `results/control_evidence_log.csv`;
`data/domain/value_explanation_demos.py` (v2 content).

---

## EXP-SPS-002 — Access/provenance equipotence gate

**Status:** COMPLETE — SUPPORTED (precondition satisfied)

**Question:** can each pool ALONE install its policy on held-out scenarios? Without
this, "the later data won" is not separable from "the later dataset was stronger."

**Result:** pool_a_only 24/24 access-consistent; pool_b_only 23/24
provenance-consistent (3 seeds each, 48 generations read directly). Later replicated
across 4 model families (phase-1 means +0.983/-1.000 Qwen, +1.000/-1.000 SmolLM2,
+0.950/-1.000 OLMo, +1.000/-1.000 pythia).

**Why it matters:** this is the control the comparable literature omits and the
reason the order manipulation supports a causal reading.

**Evidence:** `docs/risks.md` #23; family CSVs in `results/labeling/family_*`.

---

## EXP-SPS-003 — Three-condition order pilot (development battery)

**Status:** COMPLETE — PILOT ONLY

**Result:** total recency dominance at every phase boundary; interleaved
fragmentation. 8 dev prompts, 3 seeds.

**Verdict:** direction-establishing only. NOT publishable — the dev prompts informed
design. Two pipeline bugs were caught here: `epochs: 4` silently repeating A->B->C
(destroying the order manipulation) and an interleaved boundary-detection failure.

**Evidence:** `results/labeling/orderexp_pilot_v1_*`; `docs/risks.md` #24.

---

## EXP-SPS-004 — Shared neutral-washout pilot (v1 -> v2 decontamination)

**Status:** COMPLETE — RESULT REVERSED BY DECONTAMINATION

**Critical history:** washout v1 leaked provenance vocabulary ("provenance fully
documented" in approve rationales; "regardless of its provenance" in refuse halves).
Under contaminated v1 the arms FALSELY CONVERGED. After scrubbing to zero occurrences
of provenance/custody/donor/origin/chain, the order signature SURVIVED washout.

**Verdict:** a conclusion was reversed by fixing the intervention. Retained as a
documented near-miss; never delete.

**Evidence:** `docs/risks.md` #25; `data/domain/washout_demos.py` (v1 preserved
in-file); `results/labeling/orderexp_pilot_v2washout_*`.

---

## EXP-SPS-005 — Locked-battery main matrix (n=10)

**Status:** COMPLETE — SUPPORTED (publication-eligible)

**Unit:** the trained seed (paired across conditions via shared `--lora-init-seed`),
NOT the evaluation prompt.

**Preregistration:** n=10 fixed by Monte-Carlo power analysis (power 0.75-0.98)
BEFORE generation; primary confirmatory endpoint = paired exact sign-flip on the
post-washout A_first-B_first difference; battery hash-locked before model contact.

**Results:** post_phase1 +-1.000 all seeds; pre_washout 20/20 at |S|=1.000
(p=0.0020); post_washout paired -0.419, 9/10 seeds, p=0.0234; interleaved
pre_washout span -0.74..+0.57 (p=0.0020 vs each arm).

**Robustness:** LOSO 0.0039-0.0469 direction-stable; drop-3001 p=0.031;
min-5-decisive n=7 p=0.078 (reported); k=5 multi-sample -0.232, 8/10, p=0.0254
with all pairs clearing the >=5-decisive bar.

**Labeling:** claude-sonnet-5 primary (1,920 rows, condition-blind by construction);
300-row second Claude blind pass kappa=0.876; 400-row cross-developer open-weights
judge (Qwen2.5-7B-Instruct) kappa=0.588 with 1/400 direction swaps.

**Evidence:** `results/labeling/orderexp_matrix_v1-judge_labeled.csv`;
`results/fig1_per_seed_data.csv`; `analysis/orderexp_stats.py`;
`docs/paper_fact_sheet.md`.

---

## EXP-SPS-006 — Washout titration (1x / 2x / 3x)

**Status:** COMPLETE — persistence is a TRANSIENT

**Result:** separation detectable at 1x, undetectable at 2x (+0.268, exact p=0.50)
and 3x (-0.241, p=0.375), n=5 each, with sharply growing per-seed variance.

**Note:** the paper states these recomputed exact sign-flip p-values; an earlier
fact-sheet record used a different test (p=0.78/0.19). Same null conclusion.

**Evidence:** `results/labeling/washtitration_v1-judge_labeled.csv`.

---

## EXP-SPS-007 — Pre-committed enacted-choice far-transfer

**Status:** COMPLETE — NOT SUPPORTED (reported as such)

**Result:** paired A-B endpoint +0.386 in the WRONG direction, 3/9 usable seeds
negative, one-sided p=0.879; out-of-domain coherence collapses to 0.24-0.37; one
seed dropped (zero decisive in one arm).

**Verdict:** the trained policy's signature transfers in the LIKELIHOOD landscape
(VCD, 10/10 seeds, p=0.001) but does NOT control coherent enacted behavior
out-of-domain. The dissociation is reported as the finding.

**Evidence:** `results/labeling/far_transfer_v1-judge_labeled.csv`;
`results/vcd_pref_confirmation.csv`.

---

## EXP-SPS-008 — E4 first-order influence probe

**Status:** COMPLETE — partially supported; a stronger extension RETRACTED

**Result:** final-checkpoint-only (permutation-invariant) estimator recovers pool
signs at chance (7/12) and identifies the last-trained phase in 1/6 runs;
per-checkpoint reading recovers a saturation story (9/12 boundaries). The
pre-registered stronger claim (checkpoint-summed dominance) NOT confirmed
(4/6, 3/6). Bonus: washout pool gradient access-ward 6/6 -> drift diagnosis.

**Retraction:** a per-run endpoint-prediction extension was attempted and retracted;
neither reading tracks per-run outcomes at this fidelity. Stated in the paper.

**Evidence:** `results/geometry/e4_tracin_*.json`; `analysis/e4_tracin.py`.

---

## Schema for NEW experiments

Use the full template: Status / Research question / Hypothesis / Causal estimand /
Experimental unit / Control / Treatment / Held-constant invariants / Known possible
confounds / Preregistration (seeds, stopping rule, primary + secondary endpoints,
excluded outcomes, ambiguous-response handling, planned test) / Data split (dev vs
locked, battery hash, whether inspected) / Commands / Evidence paths / Results (do
not fill until complete) / Interpretation (supported vs inference vs speculation) /
Verdict / Follow-up (only discriminating tests).
