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
  **zero** access↔provenance confusions (all 24 disagreements decisive-vs-ambiguous
  → cannot flip the sign of S).
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
   absorbed by the paired design). Coherence collapses ≈0.95 → ≈0.42.
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

- Instrument: VCD scenarios (Wang et al., arXiv 2604.12479), per-token paired
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
