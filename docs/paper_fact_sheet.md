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

## Pending slots (tonight's pod queue + user items)

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

## Figures (await user verdict before use)

- results/plots/heatmap_orderexp_matrix_v1-judge.{png,pdf} — seeds × stages S.
- results/plots/ethics_specificity_orderexp_matrix_v1-judge.{png,pdf} — S vs
  ETHICS two-panel.

## Incident log

docs/risks.md — 27 numbered incidents; the audit-trail appendix material.
