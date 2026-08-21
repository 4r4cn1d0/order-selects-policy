# SPS Findings

Evidence status is part of every claim. Do not restate a finding without its grade.
Authoritative numbers: `docs/paper_fact_sheet.md`. Ledger:
`results/claims_matrix_2026-08-20.csv` (12 claims, all supported).

## Publication-eligible findings

Locked 24-item battery, n=10 paired seeds, blind-labeled, pre-registered primary test.

1. **Order selects the generalizing policy; the signature survives a shared neutral
   washout.** Endpoint A_first +0.220 vs B_first +0.639; paired -0.419, same-signed
   9/10 seeds, exact p=0.0234. Robust: LOSO 0.0039-0.0469 (direction never flips),
   drop-3001 p=0.031, k=5 multi-sample -0.232/8-of-10/p=0.0254 with every pair
   clearing the >=5-decisive bar. Limitation: min-5-decisive on greedy keeps 7 pairs
   at p=0.078. Evidence: `results/labeling/orderexp_matrix_v1-judge_labeled.csv`.

2. **Persistence is a transient, not a plateau.** Undetectable at 2x washout
   (+0.268, p=0.50) and 3x (-0.241, p=0.375), n=5.
   Evidence: `results/labeling/washtitration_v1-judge_labeled.csv`.

3. **Interleaving fragments rather than averages.** Pre-washout per-seed S spans
   -0.74..+0.57 (mean -0.256), p=0.0020 against BOTH sequential arms; overdispersion
   chi2=38.8, df 9. Scope: seed co-varies initialization and shuffle realization.

4. **Complete sequential overwriting (calibration, not a novel claim).** 20/20
   sequential runs at |S|=1.000 pre-washout, p=0.0020. Framed as catastrophic
   interference expressed at the policy level; establishes the testbed's dynamic range.

5. **The intervention is specific to the trained axis.** ETHICS-cm condition means
   0.476-0.481 vs base 0.506; Moral Stories 0.535-0.541 vs 0.521. Bounded
   non-detection, NOT equivalence.

6. **Likelihood-vs-enacted dissociation out of domain.** VCD change-preference
   confirmed pre-registered (10/10 seeds, one-sided p=0.001; 15/15 with later seeds)
   while the pre-committed enacted-choice test FAILED (+0.386 wrong direction, 3/9,
   p=0.879). Both reported.

## Replicated control findings

- **Equipotence, 4/4 model families.** Phase-1 means +1.000/-1.000 (pythia),
  +0.983/-1.000 (Qwen), +1.000/-1.000 (SmolLM2), +0.950/-1.000 (OLMo).
- **Acquisition-order effect is family-universal.** All 50 sequential runs across
  four families reverse to the last-trained pole; 43/50 at |S|=1.000 exactly.
- **Persistence replicates where measurable.** Qwen -0.592, 5/5 seeds, one-sided
  p=0.031 (exceeds pythia). SmolLM2 and OLMo endpoints saturate near -1.0 in BOTH
  arms -> unmeasurable, not refuted.
- **Washout neutrality is model-relative (a limitation, not a win).** The same pool C
  drifts pythia/Qwen access-ward but SmolLM2/OLMo strongly provenance-ward. Pool C
  neutrality was validated on pythia only.
- **Judge validity bounded across developers.** Second Claude blind pass kappa=0.876
  (300 rows); cross-developer open-weights judge Qwen2.5-7B-Instruct kappa=0.588
  (400 rows) with 1/400 access<->provenance swaps and 88/103 disagreements
  ours-ambiguous->theirs-decisive. Judges differ on the decisiveness THRESHOLD,
  not direction.

## Pilot-only observations

> PILOT ONLY: three-condition order pilot on the 8-item development battery
> (3 seeds) established direction and caught two pipeline bugs. The dev prompts
> informed design and can never support a publication number.

> PILOT ONLY: drift-time trajectory (seed 3001, dev battery, every 4 optimizer
> steps) — the 8-12-step overwrite timing. Scoped in the abstract, design section,
> and figure caption.

> PILOT ONLY: E4 influence probe, 2 conditions x 3 seeds, first-order, descriptive.

## Invalidated apparent findings

Never delete these.

1. **Keyword scorer** (`risks.md` #16) — confidently wrong aggregate.
2. **Letter-choice A/B scorer** (#17) — fatal positional bias.
3. **Continuation log-likelihood scorer** (#18) — false negatives on longer
   completions. All three caught by reading raw generations, never by the summary stat.
4. **"Order doesn't matter" from prose-vs-demos** (#20-22) — artifact of objective
   mismatch, not evidence about order.
5. **`epochs: 4` silently repeating A->B->C** — destroyed the order manipulation
   before scoring; caught from step counts.
6. **Washout v1 contamination** (#25) — the arms falsely CONVERGED; decontamination
   REVERSED the conclusion.
7. **NaN-propagation in paired stats** — a zero-decisive seed produced p=0.0000.
8. **RETRACTED: per-run influence-probe prediction** — corr +0.32 checkpointed vs
   -0.32 final-only, n=6; neither tracks per-run outcomes. Disclosed in the paper.
9. **CORRECTED 2026-08-21:** a fact-sheet line implied all 50 family runs sat at
   |S|=1.000; verified truth is 50/50 correct pole, 43/50 exactly complete.
