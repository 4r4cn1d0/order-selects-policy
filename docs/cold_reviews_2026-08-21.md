# Cold-read reviewer simulation — 2026-08-21

Three simulated ATTRIB reviewers, PDF text only (no fact sheet, no roadmap,
no artifacts), distinct personas, one-read workshop conditions.
**Scores: accept x3** (PhD/influence-functions: medium conf; industry
scale-skeptic: medium conf; alignment researcher: high conf).

## R1 (influence-functions PhD) — accept (medium confidence)

**Summary:** The authors build a controlled fine-tuning testbed (pythia-410m + LoRA, two conflicting fictional "policy" demonstration pools with byte-identical prompts, verified individually potent) and show that curriculum order alone decides which policy the model generalizes: sequential training overwrites completely (10/10 seeds, both directions), a residual order signature transiently survives a lexically neutral washout (9/10 seeds, p=0.023, gone by 2-3x washout length), and interleaving yields fragmented seed-dependent policies rather than an average. They pitch this as behavioral ground truth that permutation-invariant attribution methods cannot represent, supported by a small gradient probe where the endpoint-only (order-blind) reading recovers pool influence at chance while per-checkpoint readings recover a coherent saturation story.

**Strengths:**
- Unusually rigorous for a workshop paper: equipotence gate before order comparison, pre-registered primary test, blinded labeling with an independent second pass, hash-locked eval battery, full per-seed tables, and failed confirmations reported as failures (risk-orientation direction, far-domain enacted transfer, checkpoint-summed probe claim).
- The supervision-format confound is genuinely useful to this community: policy content trained as plain prose loses 43/43 decisive outputs to completion-supervised demonstrations regardless of order, so naive specification-vs-demonstration comparisons can manufacture spurious order-invariance.
- The attribution angle is real, not decorative: the testbed is a concrete validation target for trajectory-aware estimators (TracIn/Simfluence-style), and the endpoint-only vs per-checkpoint probe contrast is a crisp, discussable illustration of what permutation-invariant readings miss.
- Honest scoping throughout: complete overwriting is framed as catastrophic-interference calibration rather than a novel finding, the two moral-judgment benchmarks are reported as bounded non-detections, and the washout's non-neutral gradient is diagnosed rather than hidden.

**Weaknesses:**
- The headline persistence result rests on very sparse labels: post-washout coherence collapses (some cells have 1-4 decisive outputs of 24; seed 3001 B-FIRST is Ndec=1), and the authors' own robustness check restricted to >=5 decisive outputs per cell loses significance (p=0.078). The effect is also a transient, undetectable by 2-3x washout length, which limits its practical import for attribution.
- The washout is lexically but admittedly not gradient-neutral (access-ward learning direction in 6/6 runs), so "the order signature survives neutral training" leans on an additivity assumption; B-FIRST's endpoint is attenuation, not observed movement, and the two arms' asymmetric coherence (0.45 vs 0.34) is not obviously innocuous.
- Scale and generality: one 410M model, LoRA only, 24 distinct demonstrations per pool, one invented conflict axis; the core sequential result is expected interference, and it is unclear whether the fragmentation/persistence structure survives larger models or realistic data mixtures.
- The attribution content itself is thin: the probe is descriptive at 2 conditions x 3 seeds, its pre-registered stronger claim failed, a per-run prediction extension was retracted, and no existing trajectory-aware method is actually evaluated against the ground truth the paper offers.

**Questions:**
- Given cells resting on as few as 1 decisive output, why score per-seed S rather than a decisiveness-aware analysis (e.g., pooling decisive outputs hierarchically across seeds)? Does the endpoint result hold under any analysis that does not weight an Ndec=1 cell equally with an Ndec=15 cell?
- Since the washout pool's gradient is access-ward in 6/6 runs, can you rule out that the endpoint separation reflects arm-dependent susceptibility to that drift (e.g., interaction between drift and the just-installed policy) rather than a surviving trace of order per se, beyond the additivity assumption?
- Can the testbed actually adjudicate trajectory-aware attribution today: would TracIn with your dense checkpoints predict per-seed endpoint S, or does the retracted per-run probe extension indicate the ground truth is currently unpredictable at this n and fidelity - and if so, what n would make it a usable benchmark?

## R2 (industry scale-skeptic) — accept (medium confidence)

**Summary:** The authors build a controlled fine-tuning testbed (fictional archive domain, pythia-410m + LoRA) with two prompt-matched, individually-verified-potent alignment datasets that prescribe opposite policies, then train on byte-identical combined data under three curriculum orders, each ending in a shared lexically-neutral washout, with blinded labeling on a hash-locked held-out battery. They find complete last-phase overwriting on all 10 seeds (framed as calibration of the testbed's dynamic range), an order signature that survives a 1x-length washout (9/10 seeds, p=0.023) but vanishes by 2-3x, seed-dependent fragmentation rather than averaging under interleaving, and a supervision-format confound in which prose-formatted policy content has zero leverage against completion-supervised demonstrations (43/43). They pitch the testbed as behavioral ground truth that permutation-invariant data attribution cannot represent by construction.

**Strengths:**
- Experimental control well above the workshop bar: equipotence gate before any order comparison, byte-identical prompt-matched pools, constant LR to avoid confounding order with update magnitude, phase boundaries aligned to optimizer steps, blinded labeling, hash-locked eval battery, pre-registered primary comparison, and full per-seed tables.
- Unusually honest reporting: the failed pre-registered far-transfer enacted-choice test, the missed risk-orientation confirmation, the retracted probe extension, and the robustness restriction that loses significance (p=0.078) are all in the main text rather than buried.
- Direct fit to ATTRIB: the endpoint-only vs per-checkpoint influence-probe contrast concretely shows a phase-level story that permutation-invariant attribution is blind to, and the testbed is a usable validation target for trajectory-aware estimators.
- The supervision-format confound (prose-trained policy content losing 43/43 to completion-supervised demonstrations regardless of order) is a practically important warning for specification-vs-demonstration comparisons, independent of the order results.

**Weaknesses:**
- Toy regime, and I have seen this movie before: 410M model, LoRA r=16, 24 scenarios per pool repeated 8x, complete ±1.0 policy flips within 8-12 optimizer steps — this looks like a saturated, memorization-adjacent regime, and nothing here indicates whether any of the phenomena (especially the transient persistence) survive scale, full fine-tuning, or realistic data diversity. The paper scopes its claims, but the title and framing lean harder than the regime supports.
- The central novel statistic — washout survival, p=0.023 — rests on cells with as few as 1-4 decisive outputs of 24 (post-washout coherence 0.34-0.45); the authors' own >=5-decisive restriction drops it to p=0.078. Directionally suggestive, not established.
- The washout is lexically but not behaviorally neutral (their own gradient probe finds an access-ward pull in 6/6 runs), and the shared drift is larger than the paired difference itself; the persistence inference hangs on an additivity assumption the design cannot check.
- Fully LLM-circular pipeline: training data, rubric, and both labeling passes are Claude-family models, so the reported kappa bounds consistency, not validity; and the 'single pass (no epoch repetition)' framing sits oddly next to 8 reshuffled cycles of the same 24 scenarios.

**Questions:**
- Does the washout-persistence effect exist in an unsaturated regime — e.g., lower LR or fewer repetition cycles so post-conflict |S| < 1? A transient measured from a saturated pole could be an artifact of the saturation itself.
- In the interleaved condition, initialization seed and shuffle realization co-vary; can you run fixed-shuffle-across-seeds (or fixed-seed-across-shuffles) to establish whether the fragmentation is driven by data order structure or by initialization?
- Please clarify the exposure count: with 24 scenarios presented in 8 reshuffled cycles per phase, each scenario is seen 8 times — how much of the complete overwriting result depends on that repetition count?

## R3 (alignment researcher) — accept (high confidence)

**Summary:** The authors build a controlled fictional-domain testbed (pythia-410m + LoRA, two prompt-matched pools enacting conflicting policies, each pre-verified to install its policy alone) and show that curriculum order over byte-identical data decides which policy generalizes: sequential training overwrites completely (treated as calibration), a trace of the order survives a lexically neutral washout phase (9/10 seeds, p=0.023, gone by 2-3x washout length), and interleaving yields fragmented seed-dependent policies rather than an average. They additionally show a supervision-format confound (prose-trained policy content has zero leverage against completion-supervised demonstrations) and argue permutation-invariant attribution cannot represent the variable that decided behavior, offering the testbed as behavioral ground truth for trajectory-aware estimators.

**Strengths:**
- The equipotence gate (verifying each pool alone installs its policy before comparing orders) is a real methodological contribution; without it "the later data won" is uninterpretable, and prior order/curriculum comparisons indeed skip it.
- Unusually honest reporting discipline: registered vs exploratory analyses marked, a failed pre-registered far-transfer enacted-choice test reported as a dissociation, a retracted probe extension, and a first-registered direction reported as noise. This is rarer than it should be and makes the surviving claims more credible.
- The supervision-format confound is the most actionable result for alignment practice: specification-style prose losing 43/43 against completion-supervised demos regardless of order means spec-vs-demonstration comparisons can manufacture spurious order-invariance, which matters for how alignment data is staged and formatted.
- Measurement is taken seriously: per-seed tables, blinded labeling with a second independent pass (κ=0.876, zero cross-policy confusions, disagreement structure analyzed), leave-one-seed/item-out sensitivity, specificity controls on ETHICS and Moral Stories, and a gradient probe showing the "lexically neutral" washout is not gradient-neutral.

**Weaknesses:**
- The central novel claim (persistence through washout) is fragile: post-washout coherence collapses (0.45/0.34), several endpoint cells rest on 1-4 decisive outputs of 24 (seed 3001 B-first: Ndec=1), and restricting to pairs with >=5 decisive outputs in both cells loses significance (p=0.078). The abstract states persistence more firmly than this sensitivity supports.
- Labeling validity: both annotators are Claude-family models and the rubric was authored by the same LLM assistant that authored the training data, so κ bounds consistency, not validity (acknowledged); moreover the equipotence-gate counts and the headline 43/43 format-confound result are unblinded direct author reads, not blinded labels.
- Regime specificity: 410M model, LoRA r=16, 24 unique demonstrations per pool, single-pass SFT, one fictional axis. Complete overwriting in 8-12 optimizer steps may be an artifact of this tiny regime, and nothing here constrains what happens in production-scale alignment staging (the authors scope this honestly, but it limits the practical takeaway).
- Some framing outruns the evidence: the titration "transient, undetectable by 2-3x" rests on an n=5 non-detection with growing variance (a power-limited null), and "evades order-blind attribution" is largely true by construction, with the empirical influence-probe support being descriptive at n=6 runs.

**Questions:**
- Post-washout endpoint S rests on very few decisive outputs under greedy decoding; would sampling multiple completions per prompt (raising Ndec per cell) preserve the persistence effect under the >=5-decisive restriction that currently drops it to p=0.078?
- Can you add even a small human validation pass (e.g., 50-100 rows) over the LLM-judge labels so that the agreement figure speaks to validity rather than only Claude-family consistency, especially for the decisiveness boundary where the two model annotators already disagree?
- In the interleaved arm, initialization seed and shuffle realization co-vary; have you tried fixing one while varying the other (e.g., two shuffle realizations per init, or one shared shuffle across seeds) to determine whether fragmentation is driven by shuffle order or by initialization?

## Calibration note
Same-model-family simulation; treat as an upper bound on real-reviewer
warmth. Convergent residual weakness across all instruments: endpoint
decisive-count sparsity (min-5 restriction p=0.078) + Claude-circular
labeling. R3's human-validation question = the pending 60-row sheet.
R1/R3's multi-sample question = committed multisample_v1 artifacts.
