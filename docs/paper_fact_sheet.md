# Paper fact sheet — every verified number in one place

For the user's from-scratch Overleaf rewrite. Nothing here is from memory: every
number was computed in-session from committed data, or verified at source. The old
`paper/main.tex` remains in the repo as a secondary reference only.

## Venue

- ATTRIB @ NeurIPS 2026 — https://attrib-workshop.cc/ — deadline **Sept 1 AoE**.
- Main track **3–6 pages**; appendix unlimited, same PDF; non-archival;
  **reciprocal reviewing required — register on OpenReview before submitting**
  (reviews due Sept 22 AoE).

## Setup constants

- Model: `EleutherAI/pythia-410m-deduped`, fp32, LoRA fine-tuning; MPS backend for
  the primary matrix (all of any one comparison on one backend).
- Curricula: matched-prompt conflict pools A (access) / B (provenance), 24
  scenarios each, padded to phase size 32 (multiple of 16 = batch 4 × grad-accum 4);
  washout pool C (12 approve + 12 refuse, both values agree). Constant LR,
  warmup 0. Conditions: A→B→C, B→A→C, interleaved(A+B)→C. Checkpoints at every
  phase boundary.
- Seeds 3001–3010 (n=10, fixed by Monte-Carlo power analysis BEFORE generation;
  power 0.75–0.98 for the paired sign-flip test).
- Battery: 24 locked held-out items, SHA recorded at lock (see docs/risks.md;
  battery locked before any model contact).
- Measure: S = (N_access − N_provenance) / N_decisive per cell; 4-way rubric
  (access-consistent / provenance-consistent / ambiguous / incoherent).

## Measurement validation

- Judge: claude-sonnet-5, forced tool call, condition-blind by construction.
- 1,920 labeled rows; label distribution 743 access / 670 provenance / 476
  ambiguous / 31 incoherent (73.6% coherent overall).
- Independent 300-row blind validation pass: **κ = 0.876**, raw agreement 92.0%,
  **zero** access↔provenance confusions (23/24 disagreements decisive-vs-ambiguous,
  1/24 decisive-vs-incoherent — all decisive-vs-nondecisive → cannot flip the sign
  of S). Disagreement direction (verified from the joined CSVs): 22 rows are
  validator-decisive→judge-ambiguous, skewed 16 provenance : 6 access — the judge
  under-calls provenance-decisive rows; 1 row judge-decisive/validator-ambiguous;
  1 validator-provenance/judge-incoherent. Direction-skew means judge coherence is
  conservatively low on provenance rows; it cannot manufacture the A−B sign.
- Human (user) 60-row subsample: PENDING — κ slot reserved.

## Confirmatory results (all pre-registered)

1. **Equipotence / acquisition (post_phase1):** S = ±1.000 on ALL seeds, both
   directions (A-first phase 1 → +1.000; B-first phase 1 → −1.000, every seed).
2. **Total recency reversal (pre_washout):** every sequential run at the
   last-trained value's pole: |S| = 1.000 in 20/20 runs; paired flip magnitude
   2.0 every seed; exact paired p = **0.0020** (test floor at n=10).
3. **Endpoint persistence (post_washout):** A_first mean **+0.220** vs B_first
   **+0.639**; paired A−B same-signed (negative) **9/10 seeds**, mean −0.419,
   exact sign-flip p = **0.0234**. Both arms drift access-ward (shared drift —
   absorbed by the paired design). Coherence collapses ≈0.95 → ≈0.40
   (recomputed 2026-08-18: sequential endpoint decisive fraction 191/480 = 0.398;
   all three conditions 289/720 = 0.401; the earlier ≈0.42 was off).
4. **Interleaved fragmentation (pre_washout):** per-seed S spans −0.74 to +0.57
   (mean −0.256), different from BOTH sequential arms at p = 0.0020 each;
   post-washout mean +0.543 (vs B_first p = 0.48, indistinguishable).

### Per-seed endpoint (post_washout) values — recomputed from labeled CSV

A_first:  3001 +0.818 · 3002 −0.250 · 3003 −0.091 · 3004 +0.385 · 3005 −0.333 ·
3006 −0.091 · 3007 +0.789 · 3008 +0.273 · 3009 +0.455 · 3010 +0.250
B_first:  3001 +1.000 · 3002 +1.000 · 3003 +0.733 · 3004 +0.500 · 3005 +0.333 ·
3006 +0.556 · 3007 +0.200 · 3008 +0.571 · 3009 +0.750 · 3010 +0.750
interleaved: 3001 +1.000 · 3002 +0.800 · 3003 +0.833 · 3004 +0.714 · 3005 +0.250 ·
3006 +0.750 · 3007 +0.636 · 3008 −0.333 · 3009 +0.250 · 3010 +0.529
(per-seed coherence rates in results/labeling/orderexp_matrix_v1-judge_labeled.csv)

## Supervision-format finding (pre-matrix, controlled)

- Value docs as next-token prose vs opposing completion-supervised demos:
  demos won **43/43** decisive outputs regardless of order.
- Identical content reformatted as masked-completion QA: decisive-correct
  **18/24** (access) and **22/24** (provenance) — real, symmetric leverage.
- Diagnosis: mismatched training objectives (docs/risks.md #20–22).

## Robustness (exploratory, labeled as such)

- **Leave-one-item-out** (24 exclusions): direction never flips (means −0.35 to
  −0.52); significant in every case; worst p = 0.047. Item-level: 14/24 items
  predicted direction, 6 ties, 4 counter-signed.

## Specificity controls

- **ETHICS-cm** (Hendrycks et al., ICLR 2021; 1,000 fixed items, loglik): base
  0.506; condition means 0.476–0.481; no condition structure (pairwise rank
  ≈ 0.5). Uniform dip traced by spot-check to yes/no propensity shift: adapters
  answer "yes" at 0.73–0.84 vs base 0.476 (true yes-rate 0.470).
- **Moral Stories** (Emelin et al., EMNLP 2021; 1,000 items, paired-action
  loglik, propensity-immune): base acc_norm 0.521; condition means 0.535–0.541;
  no condition structure (P(A>B) = 0.695 n.s.). Uniform small UPLIFT — opposite
  sign to ETHICS's artifact; both artifacts identical across curricula.

## Out-of-domain transfer (VCD; two-stage, second stage pre-registered)

- Instrument: Value Conflict Dilemma (VCD) scenarios (Wang et al., arXiv 2604.12479; expansion verified from the paper's abstract 2026-08-20), per-token paired
  loglik of both-pole options; 6 preference domains.
- **Discovery** (60 scenarios/domain, unregistered): Change Preference paired
  A−B negative 9/10 seeds, p = 0.0039 two-sided (survives ×6 Bonferroni: 0.023).
  Risk Orientation (the one PRE-registered direction): 8/10, one-sided p = 0.060
  — missed.
- **Held-out confirmation** (directions registered before scoring; α = 0.025
  each): Change Preference **CONFIRMED** — 143 fresh scenarios, **10/10 seeds**,
  mean −0.064, one-sided p = **0.0010**. Risk **FAILED** (6/10, p = 0.236) —
  reported as noise.
- Lexical-overlap check: 3 training-lexicon hits across 517 option texts,
  balanced across poles → not vocabulary echo.
- Honest scope: likelihood-based disposition shift, NOT enacted choice.
  Direction: A_first (less access-ward endpoint) → stability-seeking.

## Far-transfer battery v1 (locked, SHA in risks.md) — enacted-choice test

- 360 completions (30 endpoints x 12 vocabulary-disjoint scenarios), judged.
- Labels: 63 access / 45 provenance / 217 ambiguous / 35 incoherent —
  coherence 0.24–0.37 (collapses out-of-domain, as anticipated at 410M).
- Paired A−B endpoint S: mean +0.386 in the WRONG direction, 3/9 negative,
  one-sided p = 0.879 → **no enacted-choice transfer; pre-committed
  abstraction-boundary reading applies.**
- KEY DISSOCIATION (pairs with the VCD result): the trained value's signature
  transfers in the likelihood landscape (VCD change-preference, 10/10 seeds,
  p = 0.001) but does NOT control coherent enacted choice out-of-domain.
  Likelihood probes are the more sensitive instrument at this scale; generation
  coherence is the limiting factor. Qualitative: the hold-template surface form
  ("I can't process this without...") does transfer, often followed by
  self-contradictory continuations; training vocabulary occasionally leaks into
  far-domain responses.

## Titration battery v1 (locked, SHA in risks.md) — severity dose-response

- 400 completions (20 sequential endpoints x 20 items, 4 frames x 5 severity
  rungs), judged. Labels: 92 access / 51 provenance / 249 ambiguous / 8
  incoherent.
- **Severity is registered behaviorally**: P(proceed | decisive) falls from
  0.86–0.91 at s1 (cosmetic issue) to 0.47 at s5 (red flag) in BOTH arms —
  a dose-response in a 410M model, no floor/ceiling failure.
- B_first curve monotone non-increasing (0.91 / 0.69 / 0.67 / 0.46 / 0.47);
  A_first NON-monotone at s2–s3 (0.86 / 0.50 / 0.79 / 0.64 / 0.47) — reported
  as a measurement limit per the pre-committed reading.
- **No detectable order-condition threshold shift** at this n and coherence
  (~0.35): the two arms' curves cross; the order effect does not measurably
  relocate the severity threshold.
- Spot-check: decisive labels verified against completions; models quote
  severity clauses back in their reasoning.

## Family replication (prereg docs/prereg_family_replication.md) — COMPLETE

Panel: Qwen2.5-1.5B, SmolLM2-1.7B, OLMo-2-0425-1B; seeds 3001–3005; identical
curricula/battery/judge; all pod CUDA fp32.

- **G1 equipotence: PASS in all 3 families** (phase-1 means — Qwen +0.983/−1.000;
  SmolLM2 +1.000/−1.000; OLMo +0.950/−1.000). With pythia: 4/4 families.
- **Total recency reversal at pre-washout: 4/4 families, 50/50 sequential runs**
  (pythia 20/20 at |S|=1.000; Qwen 10/10; SmolLM2 10/10; OLMo 10/10). The
  acquisition-order effect is universal across the panel.
- **Endpoint persistence:**
  - **Qwen: REPLICATES, stronger than pythia** — paired A−B negative 5/5 seeds,
    mean −0.592 (pythia: −0.419), one-sided p = 0.0312 (floor of the n=5 test);
    high endpoint coherence.
  - **SmolLM2: UNINFORMATIVE (ceiling)** — BOTH arms saturate at S = −1.0 after
    washout (per-seed endpoints all −0.87..−1.00 both arms); no room for an
    order difference. Report as measurement saturation, not erasure.
  - **OLMo: mostly saturated the same way** — A-first all −1.00; B-first three
    seeds at −1.00, and the ONLY two seeds with room off the pole both point the
    predicted direction (−0.33, −0.44); mean −0.156, p = 0.25 (n=5).
- **Cross-family tally (prereg headline): persistence replicates in 2/2
  informative families (pythia p=0.023, Qwen p=0.031); 2 families saturated.**
- **New finding — washout drift is family-dependent:** the same "neutral" pool C
  drifts pythia access-ward, Qwen mildly access-ward, SmolLM2/OLMo hard
  provenance-ward. Pool C's neutrality was validated on pythia only → honest
  limitation + discussion point (washout neutrality is model-relative).

## History-trace controls (prereg docs/prereg_history_trace.md) — COMPLETE, both tests FAIL

Single-phase arms install perfectly (A→C post-conflict +1.00 all 10 seeds; B→C
−0.91..−1.00), so the controls are valid. At endpoint:

- **Test 1** S(B→A→C) − S(A→C): mean **+0.234**, negative 2/10, p=0.96 → FAIL
  (and nominally opposite: 8/10 POSITIVE — prior-B models end MORE access-ward
  than no-history models; exploratory anomaly, no claim).
- **Test 2** S(A→B→C) − S(B→C): mean −0.064, positive 2/10, p=0.74 → FAIL.
- Pure-arm decay through washout is LARGE: A→C +1.0 → mean +0.40; B→C −1.0 →
  mean **+0.28** (crosses zero!). Washout aggressively erodes single-phase values
  on pythia, with its access-ward drift dominating B→C.

**Required reframing (per prereg):** the overwritten FIRST phase leaves no
detectable positive trace. The endpoint A-first-vs-B-first difference (which
REMAINS real: p=0.023/0.031, replicated in Qwen) is carried by the surviving,
washout-attenuated influence of the LAST conflict phase — recency dominance all
the way down — NOT by a durable trace of the first value. Paper phrasing changes
from "attenuates but does not erase [the first value]" to: washout attenuates
the most-recent value's influence; the first-trained value is erased to our
measurement's resolution (A→B→C endpoints ≈ B→C endpoints).

**Exploratory anomaly worth one sentence + ICML follow-up:** opposing history
appears to AMPLIFY retention of the subsequent value (B→A→C +0.64 vs A→C +0.40;
8/10 seeds in that direction) — as if prior conflicting training entrenches what
follows. No pre-registered test; report as observation only.

**Caveat:** matrix endpoints were generated on MPS, history-trace arms on pod
CUDA (greedy both). Cross-backend comparison; cross-check against the
multi-sample batch (same CUDA backend for all 30 matrix runs) when its judging
completes before finalizing paper text.

## Reviewer-armor language (use these framings; each maps to hostile_review_aug18.md)

- **Against "it's just last-phase decay" (#2):** two results are NOT explained by
  pure recency-plus-decay: (i) interleaved fragmentation — identical final data
  mixture, divergent seed-dependent policies (p=0.002 vs both arms); (ii) the
  amplification anomaly — B→A→C ends MORE access-ward than A→C (8/10 seeds),
  i.e., prior opposing training strengthens retention of what follows. State
  both wherever recency is discussed. E2's decay curve (in flight) completes
  this: a characterized half-life, not an arbitrary stopping point.
- **Replication phrasing (#3):** the cross-family tally rule was pre-registered
  BEFORE any family run (prereg_family_replication.md); "saturated" families
  are visibly at-pole in Fig 2 (both arms −1.0), reported per the prereg's
  coherence clause — the euphemism-free sentence is: "persistence is
  informative only where endpoints are off-pole; it replicated in 2/2 such
  families." Never hide the two saturated families; never pool them silently
  (the pooled diamond is labeled 'informative families').
- **VCD transfer phrasing (#6):** always "confirmed on held-out scenarios
  within the same models (direction pre-registered before scoring); model-level
  replication on fresh seeds in E3." After E3 lands, cite its result instead.
- **Washout (#5):** state plainly: pool C's neutrality was validated on pythia
  only, and the family sweep revealed washout drift is model-relative — a
  limitation for our persistence estimates AND a finding (there may be no such
  thing as model-neutral data). Within-family paired contrasts absorb shared
  drift; arm-by-washout interaction remains a caveat.
- **ATTRIB positioning (#8):** the paper supplies the behavioral ground truth
  that order-aware attribution methods must predict: same data, different
  order, different value — any attribution method treating the training set as
  an unordered bag assigns identical attributions to models with opposite
  values (the 50/50 reversal), a concrete falsification target. E4 (TracIn-lite,
  if it lands) instantiates this; otherwise it is the stated research program.

## Multi-sample endpoints (k=5, pre-registered decoding) — COMPLETE

- 30 runs x 24 items x 5 samples (T=0.7, top-p 0.95), pod CUDA, all judged.
- Per-seed endpoint S on 120 draws/cell: A_first mean **+0.363**, B_first
  **+0.595**, interleaved **+0.624**; coherence 0.46–0.53 (well-estimated,
  vs greedy's thin ~0.42).
- **Paired A−B: mean −0.232, negative 8/10 seeds, one-sided p = 0.0127**
  (two-sided 0.0254). The greedy result (−0.419, 9/10, p=0.023) survives
  5x sampling; smaller magnitude under temperature is expected regression.
  Report both: greedy = primary prereg'd stat, k=5 = robustness.
- **Backend caveat CLOSED:** history-trace erasure tests re-run with pod-CUDA
  multisample endpoints vs pod-CUDA history arms: T1 mean +0.190 (p=0.93),
  T2 +0.079 (p=0.24) — both still fail; the no-trace conclusion is not a
  backend artifact. Amplification-anomaly direction persists (7/10).

## Pending slots (hardening queue + user items)

- Multi-sample endpoint: k=5, temp 0.7, top-p 0.95, params pre-registered in
  scripts/generate_multisample_endpoint.py. 3,600 completions.
- Family replication (prereg docs/prereg_family_replication.md): Qwen2.5-1.5B,
  SmolLM2-1.7B, OLMo-2-0425-1B × 3 conditions × seeds 3001–3005; equipotence
  gate |S| ≥ 0.8 both directions per family BEFORE any order claim; headline =
  cross-family sign tally.
- History-trace (prereg docs/prereg_history_trace.md): A→C, B→C × seeds
  3001–3010; two one-sided tests at α = 0.025; discriminates trace vs erasure.
- Far-transfer + titration batteries: DRAFTS awaiting user lock.
- Human κ from user's 60 rows: PENDING.

## Verified bibliography

`paper/refs.bib` — every entry fetched/verified against its arXiv ID or DOI
in-session (project convention after catching one mis-citation). Safe to import
into Overleaf as-is. Citation notes + verification method per entry:
docs/citations.md.

## Figures

NONE approved. The heatmap and specificity renders were rejected and deleted
(2026-08-18). Fresh figures follow the spec-first process: user picks from the
proposed figure menu + supplies style anchors; one prototype rendered for
verdict before any batch. Candidate menu (data-ready): flip slopegraph,
titration dose-response, VCD leak-profile dumbbell; (post-judging): family
forest plot, multi-sample rainclouds, history-trace ghost overlay.

## Incident log

docs/risks.md — 27 numbered incidents; the audit-trail appendix material.

## FRAMING DECISION (user, 2026-08-19): behavior-first, values as tested question

Vocabulary map for the draft (use consistently):
- "value" (as claim) -> "trained behavioral policy" / "conflicting policies A and B"
- "value formation" -> "policy installation" / "which trained policy generalizes"
- S -> "policy score S" (+1 policy-A-consistent, -1 policy-B-consistent)
- KEEP "values" in exactly three places: (1) motivation (alignment data instills
  values; order of alignment phases is an engineering choice); (2) the
  operational definition, stated in the abstract's first sentences ("we use
  value operationally: a trained policy governing conflicts between two
  legitimate courses of action"); (3) the explicit open question, resolved by
  E1: do value-like conflict policies differ from arbitrary trained behaviors
  (e.g., response form) under identical curricula? Whichever way E1 lands, the
  paper reports it as a RESULT, not an assumption.
- The fictional-domain rationale is unchanged and framing-independent: low
  prior = causal attribution of the installed policy to the curriculum.
- ATTRIB fit strengthens: the workshop is literally "Attributing Model
  BEHAVIOR at Scale" -- behavior-first framing is native vocabulary.

Title candidates (user picks; all honest under current evidence):
1. "Training Order Determines Which of Two Conflicting Policies a Language
   Model Generalizes"
2. "Same Data, Different Model: Curriculum Order Selects Generalizing Behavior"
3. "Order-Dependent Behavior Formation in Language Model Fine-Tuning"
4. Keep-values variant (only if E1 shows form differs from policy):
   "Training History Shapes Value-Like Policy Formation in Language Models"

## E2 washout titration — COMPLETE (third pre-registered outcome)

Paired A−B endpoint difference vs washout length: 1x = −0.232 (k=5, p=0.013;
greedy-MPS sensitivity −0.419, p=0.023) · 2x = +0.268 (n=5, p=0.78) ·
3x = −0.241 (n=5, p=0.19). Neither longer length significant; per-seed variance
grows sharply (washx2 A-first endpoints span −0.78..+0.71). Verdict: no
monotone decay, no durable plateau — the order effect decays into
seed-dependent noise by ~2x washout. Report as: "the endpoint separation is a
transient of continued training: detectable at 1x, undetectable at 2–3x, with
variance growth consistent with the fragmentation dynamic." Caveats: n=5,
greedy k=1 at 2x/3x vs k=5 at 1x, decoding noted. Completes the recency
ladder: total acquisition → survives 1x → noise by 2x → first phase never traces.

## E3 fresh-seed transfer replication — CONFIRMED (model-level)

10 new runs (seeds 3011–3015, A/B-first), endpoints scored on the held-out 143
change-preference scenarios only. **Pre-registered paired A−B: negative 5/5
seeds, mean −0.0533, one-sided p = 0.0312** (n=5 floor — every seed predicted
direction); magnitude matches original models (−0.064). Risk axis descriptive:
flat (2/5, p=0.47), consistent with its failed confirmation. The transfer
finding now has three-stage support: discovery → held-out-scenario confirmation
(10/10, p=0.001) → fresh-seed replication (5/5, p=0.031). Use in place of the
"within the same models" caveat everywhere.

## E6 Qwen far-transfer + base control — COMPLETE (three-layer result)

1. **Scale buys enacted OOD coherence:** decisive rate 0.889 at 1.5B vs
   0.24–0.37 at 410M (coherence gate PASS; the test is informative).
2. **Training transfers an ENACTED disposition:** trained runs' far-domain S
   pooled −0.68 vs base-Qwen −0.14 (12-item judged control, balanced 3A/4P/5amb)
   — the first enacted out-of-domain transfer of trained content in the project;
   at 410M this existed only in likelihood space.
3. **The ORDER-selected component stays domain-bound in enactment:** far-domain
   S is uncorrelated with each run's in-domain endpoint policy (r = +0.07 over
   15 runs); pre-registered far-domain order test suggestive but n.s.
   (4/5 negative, one-sided p = 0.094).

Refined dissociation for the paper: with scale, models ENACT a trained shared
disposition far outside the training domain, while WHICH policy order selected
remains expressed only in-domain (and in likelihood space at 410M). H5's scale
prediction: half-confirmed, with precision about which half.

## E1' style control, form-neutral washout — COMPLETE (outcome iii: no categorical claim)

- Equipotence and total recency reversal replicate for the FORM policy
  (10/10 runs) — acquisition dynamics are fully generic across trained
  behaviors. State as a result.
- Endpoint under form-neutral washout: paired X−Y mean −0.217, two-sided
  p = 0.375 (3 neg / 1 pos / 1 zero; both arms drift list-ward). Same
  direction and similar magnitude as the value axis's k=5 estimate (−0.232,
  p=0.013) but high-variance and non-significant.
- REQUIRED phrasing: "order-driven acquisition is behavior-generic; endpoint
  persistence is statistically detected only for the conflict-policy axis, but
  the form comparison lacks power to rule out a comparable effect — we make no
  values-are-special claim." E1.c (original) remains reported as confounded
  (incident #28).

## E8 open-weights second judge — COMPLETE (reported per prereg)

Qwen2.5-7B-Instruct (open weights, run locally, verbatim primary rubric) on the
blinded 400-row stratified sample: raw agreement 0.743, **kappa = 0.588** —
below the 0.7 marker, reported and discussed per prereg. Structure: 88/103
disagreements are Claude-ambiguous -> Qwen-decisive (48 provenance / 40 access,
near-symmetric); **access<->provenance swaps: 1/400 (0.25%)**. Cross-judge
discussion for the paper: judges differ on the decisiveness THRESHOLD, not on
direction — the sign of S, which carries every claim, is judge-invariant. This
mirrors the human-validation pass's structure (all disagreements
decisive-vs-ambiguous). Labels released as the reproducible open-weights
reference set (results/labeling/e8_labels.csv).

## Review knock-out batch (2026-08-20; maps to ATTRIB self-review W1–W5 + minors)

- **W1 (single axis) — required sentence:** "All conflict-policy results derive
  from one hand-authored axis; axis-generality is untested and is the first
  item of our follow-up program." State in Limitations verbatim-close.
- **W2 (washout non-neutrality inherits into decay) — required sentence:** "The
  2x/3x decay findings inherit the washout's model-dependent drift; 'decays
  into noise' and 'drift dominates' are not separable in this design."
- **W4 (human anchor) — hard rule:** the paper must NOT imply the human
  subsample exists until the 60 rows are labeled; measurement section cites the
  two-AI-judge characterization only, with the human pass listed as in-progress
  work if unfinished at submission.
- **W5 + minor(a) — inline phrasing:** every p=0.031 gets "(the minimum
  attainable at n=5)"; first mention of kappa=0.588 gets "(disagreements are
  decisiveness-threshold, not direction: 1/400 direction swaps)"; add one
  sentence: "no single replication node carries the claim; the convergent
  pattern across families, seeds, and decodings does."
- **Minor(b) — unified variance-growth paragraph (use nearly verbatim):**
  "Three observations form one pattern: interleaved training yields
  initialization-dependent policies; extended washout dissolves the endpoint
  separation into growing per-seed variance rather than a clean mean shift; and
  two families' washout drift overwhelms the order signal entirely. Continued
  training in this regime does not average behaviors -- it amplifies
  seed-dependent divergence, which we propose as the common mechanism behind
  fragmentation, decay-to-noise, and saturation."
- **Minor(e) — terminology:** the word is "washout," everywhere; retire
  "neutral continuation" and "phase C" outside the design section's definition.
- **Minor(f) — camera-ready checklist entry:** release bundle = checkpoints +
  curricula + labeled CSVs + judge prompt + parsing/scoring code + E8 reference
  labels; verify every path resolves before submission.

## Additional required limitation (author-judge coupling; add to Limitations)

"Training content, rubric, and primary labels all originate from one model
family (Claude); a same-family judge may parse same-family-authored text with
inflated confidence. Two observations bound this risk without eliminating it:
an open-weights judge from a different developer reproduces the sign-carrying
statistic (1/400 direction swaps) and is MORE, not less, willing to call
completions decisive; and the models under test span four unrelated families.
Cross-family authoring and human adjudication are part of the follow-up
program." 

## Influence-attribution probe (the registered TracIn-style pilot) — PILOT COMPLETE

Checkpointed influence (gradient dot-products summed over every saved step
checkpoint, LoRA params, exact training encoding) vs the SAME estimator at the
final checkpoint only (the permutation-invariant information condition), test
direction = the endpoint policy axis. Pilot (seed 3001, both arms):

- Checkpointed attribution matches behavior: access-first run (endpoint +0.82)
  -> access pool +97.5, provenance pool -75.0, washout +38.6 (correctly
  capturing the drift's contribution). Provenance-first run (endpoint +1.0,
  access-last) -> access pool +220, washout +212, provenance +22.
- Final-only attribution is small, inconsistent, and sign-unstable (e.g.,
  assigns the access pool NEGATIVE influence on an access-leaning model).

**RETRACTED after extension (2026-08-20):** at n=6 runs (including
opposite-endpoint seeds chosen to falsify), checkpointed attribution does NOT
reliably track per-run endpoints (corr +0.32; final-only -0.32; neither
meaningful). The 2-run pilot pattern did not replicate. REQUIRED reporting:
"a registered TracIn-style probe, released with the benchmark, does not at this
implementation fidelity recover per-run outcomes (n=6) -- the benchmark's
ground truth stands as an open target for order-aware estimators." The
venue-fit paragraph relies on the falsification-target framing, NOT on a
demonstrated estimator win. Improvement paths (LR-weighted sums, per-item test
gradients, more runs) go to the follow-up program.

## Micro-controls (registered follow-ups) — COMPLETE (2026-08-18, judged blind)

Two step-matched controls, generated on the pod, judged blind (~156 rows), pod
terminated after sync. Per-seed values are decisive-only S at the endpoint.

**1. Neutral-history control C->A->C (pythia, n=5, test battery, endpoint):**
per-seed S = -0.27, -0.09, -0.40, +0.20, -0.50 (mean -0.213; coherence 50/120
= 0.42). References (same judge, same battery, endpoint): A_then_C (no first
phase) mean +0.406 (n=10); B_first = B->A->C (opposing first phase) mean
+0.639 (n=10). Mann-Whitney: C_A_C vs A_then_C p = 0.0081; C_A_C vs B_first
p = 0.0032. **Neither pre-registered reading obtained: C_A_C sits BELOW both
references.** Consequences:
- The training-budget explanation of the amplification anomaly is DEAD:
  C_A_C is step-matched to B_first (576 examples) yet retains the least
  A-policy. Extra steps do not explain B->A->C > A->C.
- The amplification is specific to an OPPOSING conflict first phase: B-then-A
  amplifies A's endpoint retention (+0.639) above no-history (+0.406), while a
  neutral first phase suppresses it below no-history (-0.213).
- Exploratory interpretation (label as such): a prepended washout phase gives
  the final washout phase an attractor to return to (total washout exposure
  2x192, consistent with the titration's decay-by-2x); an opposing conflict
  phase instead hardens the subsequently trained policy. Report the
  confirmatory part as the ordering S(C_A_C) < S(A_then_C) < S(B_first) with
  the two p-values; the mechanism language stays exploratory.
- Caveats: n=5 vs n=10 references; coherence 0.42 (8-11 decisive/24 per seed);
  C_A_C endpoints judged in a separate later batch than references (same
  locked battery, same judge + rubric).

**2. Washout-only far-transfer control (Qwen2.5-1.5B C_only, n=3, far
battery, endpoint):** per-seed far-S = -0.833, -0.818, -0.800 (mean -0.817;
coherence 33/36 = 0.92). References: conflict-trained Qwen pooled far-S =
-0.675 (160/180 decisive); base (untrained) Qwen = -0.143. **Pre-registered
reading: the "any-fine-tuning" outcome.** The far-domain hold-disposition is
fully induced by fine-tuning on washout content alone -- zero conflict
examples -- and is, if anything, slightly stronger than in conflict-trained
runs. The enacted far-domain shift is therefore a generic effect of
fine-tuning on this corpus style, NOT carried conflict content. This completes
the three-layer dissociation cleanly: (i) enacted far-domain hold-shift =
generic fine-tuning artifact (this control); (ii) which-policy order selection
does not transfer enacted (r = +0.069); (iii) likelihood-space preferences DO
shift with training order (three-stage replicated). REQUIRED reporting: state
(i) using this control, do not attribute the far hold-shift to the conflict
training.

Artifacts: results/labeling/cac_control_v1-judge_labeled.csv,
results/labeling/conly_far_v1-judge_labeled.csv; generations
results/generations/{cac_control_v1,conly_far_v1}.jsonl; final adapters
synced to checkpoints/ (5 pythia C_A_C, 3 Qwen C_only). Pod terminated.

## Number certification pass (2026-08-18, pre-submission)

Every previously-unverified number in paper/main.tex recomputed from committed
artifacts (scratchpad script; sources named per line). ALL MATCH:

- **kappa = 0.876** exact; raw 276/300 = 92.0%; **0** access<->provenance
  confusions. Source: orderexp_matrix_v1-humanval_blind.csv joined to
  orderexp_matrix_v1-judge_labeled.csv on (scenario_id, completion); 300/300
  joined, 0 collisions.
- **LOIO**: means -0.347..-0.524, worst p = 0.0469 (drop test-0001), all
  same-direction; per-item 14 predicted / 6 ties / 4 counter. Source:
  analysis/orderexp_item_robustness.py rerun.
- **ETHICS**: 30 endpoints, condition means 0.4759-0.4808, base 0.506.
- **Moral Stories**: acc_norm condition means 0.5346-0.5406, base 0.521.
- **VCD discovery**: Change Preference 9/10, two-sided p = 0.0039 exact.
- **VCD confirmation** (matrix seeds 3001-3010): 10/10, mean -0.0642,
  one-sided p = 0.0010 exact. Risk: pre-registered positive direction 6/10,
  p = 0.2363 -> 0.24, failed as reported.
- **Interleaved post-washout**: mean S +0.5430 exact; vs B_first p = 0.4844.

Both flags FIXED in main.tex (2026-08-18, user-authorized correctness edits):
1. kappa disagreement wording -> "decisiveness boundary call (decisive vs.
   ambiguous or incoherent)" (23/24 vs-ambiguous, 1/24 vs-incoherent; neither
   can flip the sign of S).
2. VCD footnote added: 5 later seed pairs (3011-3015) replicate the confirmed
   Change Preference direction, 15/15 total, one-sided p = 3.1e-5 (exact
   sign-flip floor 1/2^15; all 15 diffs negative, verified from
   vcd_pref_confirmation.csv).

Full-sweep additions (same pass; every remaining number in main.tex now tied
to an artifact):
- Battery hash 2b5f6e06...2895 = SHA-256 of the BUILT JSONL
  (data/processed/axis1_access_vs_provenance__test_battery_v1.jsonl),
  recomputed and matching; the .py source has no post-lock commits. The .py
  file's own byte-hash differs (37172e75...) -- the lock was always over the
  JSONL models consume.
- Equipotence gate 24/24 (pool_a_only) / 23/24 (pool_b_only): source is
  risks.md #23 (direct read of all 48 held-out generations, 3 seeds/pool).
  PROVENANCE GAP: the raw pool-only generations were not committed as files;
  the documented read in risks.md is the artifact.
- Drift timing corrected: dense per-4-step checkpoints exist for seed 3001
  only. Complete overwrite: A-direction by 8 steps, B-direction by 12 steps
  (4-step grid). Abstract's "~8 steps on all 10 seeds" was unsupported as one
  claim -> rescoped to all-seeds reversal + "8-12 optimizer steps" timing;
  drift figure caption now says 8-12. Install-within-~8 verified (A +1.00 by
  step 8; B -1.00 by step 4).
- Washout coherence: paper ~0.42 -> ~0.40 (see recompute above).
- post_phase1: S = +1.000 (all 10 A_first) / -1.000 (all 10 B_first),
  coherence 0.83-1.00. pre_washout: all 20 sequential runs |S| = 1.000;
  interleaved span -0.74..+0.57, mean -0.256, p = 0.0020 vs EACH arm
  (recomputed: +0.744 vs A_first, -1.256 vs B_first, both p = 0.0020);
  interleaved pre-washout coherence 0.83-0.96 exact.
- Format-section 43/43 (risks #21), 18/24 & 22/24 (risks, Phase A v2 direct
  read): consistent with the documented reads; these predate the blind-CSV
  protocol (narrative artifacts).
- ETHICS yes-rate 0.73-0.84 vs base ~0.48: fact-sheet record only (spot-check;
  no committed per-item CSV) -- paper labels it "spot-checked", accurate.
- Limitations sentence fixed: the false "a human-labeled subsample is included"
  now reads "agreement bounds labeling consistency, not human validity."
  If the user fills the 60-row annotator2 sheet before submission, the
  stronger human-check sentence can return WITH its real number.
- Intro "blinded human labeling" -> "blinded labeling"; Limitations "Labels
  are human judgments" -> "rubric-based judgments" (matrix labels are
  LLM-judge; no unqualified human-labeling claim remains).

Still open (user-owned): Fig 1 regeneration; OpenReview anonymity check +
reciprocal-reviewer registration; optional 60-row human labeling pass.

## Endpoint sensitivity statistics (verified 2026-08-18, from panel review follow-up)

All recomputed from orderexp_matrix_v1-judge_labeled.csv (citable):
- Drop-seed-3001: n=9, mean -0.445, p = 0.0312.
- Leave-one-seed-out: p range 0.0039-0.0469, direction never flips.
- Minimum-decisiveness (both cells >= 5 decisive): keeps 7 pairs
  (3002,3003,3006,3007,3008,3009,3010), mean -0.461, p = 0.0781 --
  direction stable, significance lost. Transparency item, report as such.
- Per-cell endpoint decisive counts: A_first [11,8,11,13,6,11,19,11,11,8],
  B_first [1,10,15,4,3,9,10,14,8,8] (B_first seed 3001 = 1).
- Interleaved pre-washout overdispersion vs binomial item-sampling:
  chi-square 38.8, df 9 (p ~ 1.3e-5).
- Endpoint coherence by arm: A_first 0.454, B_first 0.342. CAUTION: the
  review panel's p=0.012 for this difference did NOT verify -- paired
  sign-flip on per-seed coherence gives p=0.16. Cite means only.

## E4 TracIn-lite influence probe — VERIFIED tallies (2026-08-19, from committed JSONs)

Artifacts: results/geometry/e4_tracin_{A,B}_first_seed{3001,3002,3005}.json
(6 runs = 2 conditions x 3 seeds; dense per-4-step stages exist for 3001 only,
boundaries-only for 3002/3005). Method (analysis/e4_tracin.py): first-order
LoRA-gradient probe -- influence of pool P at checkpoint c = mean over P's
examples of dot(gradient of S-proxy test direction, negative example-loss
gradient). S-proxy = mean over locked-battery items of loglik(A-behavior) -
loglik(B-behavior). NOTE the honest scoping: this measures PROSPECTIVE
leverage at each saved state (not usage-weighted TracIn proper), descriptive,
n=6 runs. Prereg: prereg_workshop_hardening.md E4 ("stretch").

Verified findings (every tally recomputed from the JSONs):
1. **Final-only attribution (permutation-invariant baseline) fails on the
   ground truth**: correct expected pool signs 7/12 (~chance); identifies the
   last-trained conflict phase with dominant magnitude AND correct sign in
   **1/6 runs**. Sign inversions in 5/6 runs (e.g. A_first_3001 assigns pool A
   NEGATIVE influence at final).
2. **Checkpointed per-boundary reading recovers a saturation story**: at
   boundary_1 the OPPOSING pool dominates with correct sign 5/6 (exception
   B_first_3005); recently-trained pool has smaller |influence| than the
   opposing pool at 9/12 boundary checkpoints. Interpretation: gradient
   leverage lives in what is NOT yet installed; the installed pool is
   saturated.
3. **The literal pre-registered claim is NOT confirmed at this n**:
   "checkpointed sum assigns dominant influence to the last conflict phase" =
   4/6 by magnitude, 3/6 with correct sign. If E4 enters the paper, report
   this outcome explicitly; the defensible claims are (1) and (2), labeled
   descriptive/exploratory.
4. **NEW -- washout-drift diagnosis** (answers the panel's "undiagnosed
   access-ward drift" must-fix): the lexically-scrubbed washout pool C has an
   ACCESS-WARD gradient at the pre-washout state in **6/6 probed runs** (dots
   +2.8..+9.6, mean +5.9) and 5/6 at final (mean +4.0). The shared endpoint
   drift is predicted by a first-order probe of the washout data itself:
   lexically neutral is not gradient-neutral. Cite as the drift's mechanism.

Suggested placement (user decides): short exploratory subsection leading with
(1) as the attribution payload; (2) as the checkpointed contrast; (4) one
sentence in the washout paragraph. Do NOT headline (3).

## TITLE DECISION (user, 2026-08-19)

Locked: "Order Selects Policy: Curriculum Effects That Persist, Fragment, and
Evade Order-Blind Attribution". Rationale: every clause is a non-assumed claim
(persistence, fragmentation, attribution blindness); avoids headlining the
folk-known recency result; "order selects policy" matches the repo name.
Supersedes the four candidates listed under FRAMING DECISION.

## Enacted-choice far-transfer null — RE-VERIFIED and now REPORTED (2026-08-20)

Recomputed from results/labeling/far_transfer_v1-judge_labeled.csv:
360 rows; labels 63 access / 45 provenance / 217 ambiguous / 35 incoherent
(all four match the earlier record exactly). Pooled coherence by arm:
A_first 0.367, B_first 0.242, interleaved 0.292 (hence "0.24-0.37").
Paired A-B endpoint S over the 9 usable seeds: mean +0.386, negative 3/9,
one-sided p = 0.879. Seed 3001 drops because B_first had 0 decisive outputs
(zero-decisive pair-drop rule).

The manuscript now reports this as its own result paragraph rather than a
scope clause -- this was the review panel's #1 must-fix (selective-reporting
risk). Also disclosed there: the 6-domain discovery screen with the x6
Bonferroni, and that risk orientation was the FIRST-registered direction
(discovery p=0.060, confirmation p=0.24).

Optional strengthener not yet in the manuscript: the washout-only far-transfer
control (Qwen C_only, n=3, far-S = -0.817 vs conflict-trained -0.675, base
-0.143) establishes the far-domain hold-shift as a generic fine-tuning
artifact. Fact sheet's own note marks this as REQUIRED reporting IF the far
hold-shift is discussed -- currently the manuscript does not attribute any
far-domain hold-shift to conflict training, so the control is not yet needed;
add it if the rewrite expands this paragraph.

## E4 FOLDED INTO MANUSCRIPT (2026-08-21, user decision)

New Results paragraph "A first-order influence probe against the ground truth":
final-only estimator signs 7/12 (~chance), last-phase identification 1/6;
per-checkpoint saturation story 5/6 boundary-1, 9/12 overall; failed literal
prereg (4/6, 3/6) reported as such; washout-drift diagnosis 6/6 access-ward
(also referenced from the washout paragraph, closing review M3's diagnosis
half). Washout paragraph honesty pass applied: "equally" dropped, per-arm
endpoint coherence 0.45/0.34 stated (means only), lexical-not-behavioral
neutrality + additivity assumption stated. Figure 2 (drift) relocated to the
appendix for page budget: body now ends within page 6 (references start on
p6). Title/abstract unchanged.

## RE-REVIEW VERDICT + BLOCKER FIXES (2026-08-21)

Five-seat verification round on the revised manuscript: **WEAK ACCEPT,
unanimous 5/5** (prior round: major_revision). Digest:
docs/review_rereview_2026-08-21.md. Decision letter: "with these landed
before camera-ready, this is an accept." All three blockers LANDED same day:
1. Persistence scoped everywhere (contribution 1 "-- for a while", washout
   paragraph, conclusion) with the E2 titration reported. NUMBER PROVENANCE:
   manuscript uses MY artifact recompute from
   washtitration_v1-judge_labeled.csv -- 2x mean +0.268 exact two-sided
   p=0.50; 3x mean -0.241 p=0.375 (stated as "p>=0.38") -- NOT the fact
   sheet's earlier p=0.78/0.19 (different test; same null conclusion; means
   match exactly). Washout length stated: 12 optimizer steps = one phase.
2. Table 1: N_dec per cell added (A/B/interleaved), caption carries the
   sensitivity trio (drop-3001 p=0.031; LOSO 0.0039-0.0469; min-5-decisive
   n=7 p=0.078).
3. Probe closing rewritten: retraction disclosed ("neither reading tracks
   per-run outcomes... open target"); heading softened to "A first-order
   influence probe".
Also landed: drift-misdescription fix (B-first attenuation, not access-ward
movement); kappa sentence rescoped ("cannot manufacture the A-B sign") with
16:6 split; 24->192 expansion stated; confirmatory-family declaration +
power sentence; VCD pole-mapping rationale; Qi et al. cited in text;
"initialization-dependent" leftover fixed; stale figure comment replaced.
Page budget: body ends p6, references start p7, appendix p7-8 (Fig 2 in
appendix). Abstract/conclusion micro-trims applied for the budget.

## Cross-family judge (E8) NOW REPORTED in the manuscript (2026-08-21)

Gap found while answering "where does Claude-family come from": E8 existed as a
committed artifact but was ABSENT from the paper, leaving the circularity
objection unanswered on the page. Recomputed from e8_labels.csv + e8_sample.jsonl
and now reported in Measurement + Limitations:
Qwen2.5-7B-Instruct (open weights, different developer, local, verbatim rubric),
400-row blinded stratified sample spanning 6 batches -- raw agreement 0.743,
kappa 0.588, and 88 of 103 disagreements are ours-ambiguous -> theirs-decisive
(48 provenance / 40 access), with access<->provenance swaps 1/400 (0.25%).
Reading: judges differ on the decisiveness THRESHOLD, not direction; the sign
carrying every claim is judge-invariant across families. Fact-sheet sub-counts
verified exact (88 counts "ambiguous" only; the amb+incoherent figure is 94).
Limitations now carries the author-judge coupling paragraph (same-family
authoring + rubric + primary labels, bounded by the cross-developer judge, not
eliminated).

Page budget re-closed after the addition (body ends p6, references p7) via
Table 1 -> \scriptsize, Fig 1 -> 0.68\linewidth, and scaffold-sentence trims in
the conclusion/measurement/battery paragraphs. NUMBERS UNTOUCHED.

STILL DEFERRED (available, not in paper): four-family replication (pythia/Qwen/
SmolLM2/OLMo, 50/50 sequential runs, equipotence PASS in all four) -- the
Limitations "single model" sentence is accurate for the main matrix but
UNDERSELLS; folding the family panel in would answer the scale-skeptic
reviewer's strongest objection. Multi-sample k=5 (multisample_v1) likewise
available and would answer the endpoint-sparsity objection.

## Multi-sample + family panel FOLDED IN (2026-08-21) — both verified first

**Multi-sample k=5 (verified from multisample_v1-judge_labeled.csv, 3,600 rows):**
paired A-B mean -0.232, 8/10 negative, two-sided p = 0.0254 (matches prior
record exactly). NEW verified number now in the paper: per-cell decisive counts
rise 1-19 (greedy) -> 39-76 (k=5), so the >=5-decisive restriction that cost the
greedy result its significance (n=7, p=0.078) now keeps ALL 10 pairs at
p = 0.0254. This is the direct answer to the endpoint-sparsity objection raised
by all three cold reviewers and the methodology seat. Condition means: A_first
+0.363, B_first +0.595, interleaved +0.624; coherence 0.46-0.53.

**Family panel (verified from family_{qwen,smollm,olmo}_v1-judge_labeled.csv):**
- Equipotence PASS 4/4 families: phase-1 means Qwen +0.983/-1.000, SmolLM2
  +1.000/-1.000, OLMo +0.950/-1.000 (all match prior record exactly).
- Qwen endpoint persistence: mean -0.592, 5/5 seeds, one-sided p = 0.0312 —
  EXACT match; replicates and exceeds pythia.
- SmolLM2 saturated (both arms -0.87..-1.00), OLMo mostly saturated with its two
  off-pole seeds both predicted-direction (paired -0.33, -0.44) — exact match.
- **CORRECTION to the earlier fact-sheet line.** It read "total recency reversal
  ... 50/50 sequential runs (Qwen 10/10; SmolLM2 10/10; OLMo 10/10)", which
  implies all at |S|=1.000. Verified truth: all 50/50 reverse to the CORRECT
  POLE, but only 43/50 sit at |S|=1.000 exactly (pythia 20/20, OLMo 10/10, Qwen
  8/10, SmolLM2 5/10; remainder |S| >= 0.81). The manuscript states the accurate
  version ("all 50 reverse to the last-trained pole, 43 of them completely").
- Family-dependent washout drift CONFIRMED and reported as a limitation:
  access-ward in pythia/Qwen, strongly provenance-ward in SmolLM2/OLMo; pool C
  neutrality validated on pythia only.

Placement: multi-sample = 2 sentences in the washout paragraph; family panel =
short body paragraph + new Appendix A "Cross-family replication" with the full
detail. Page budget re-closed (body ends p6; refs p7; appendices A and B on
p7-8) via Fig 1 -> 0.58\linewidth, conclusion condensed, the fictional-axis
future-work sentence relocated to Limitations, and abstract/scaffold trims.
NUMBERS UNTOUCHED throughout.
