# Pre-registration: workshop-hardening experiments (scope re-opened 2026-08-18)

User decision: pull forward the ICML-tier experiments that close the hostile
review's strongest attacks (docs/hostile_review_aug18.md) into the ATTRIB
submission. Registered BEFORE any curriculum, run, or score exists. LOCKED at
first training run of each experiment; deviations -> docs/risks.md.

## E1 — Style control (closes attack #1: "values or just any behavior?")

Two NON-value response-FORM policies on the identical conflict scenarios:
- Policy X: respond as a numbered list (>=2 numbered items).
- Policy Y: respond as flowing prose (no list markers).
Content matched: each scenario's X and Y completions carry the SAME action
(action balanced 50/50 access/provenance across each pool so form is orthogonal
to the value axis). Curricula mirror the order experiment exactly: X-first
(X->Y->C), Y-first (Y->X->C), phase_size 192, washout pool C unchanged,
seeds 3001-3005, pythia-410m, pod CUDA fp32, mandatory flags.

Scoring is DETERMINISTIC (regex list-marker detection on held-out battery
completions; no LLM judge, no new rubric): F = (N_list - N_prose)/N_total.

Pre-registered comparisons (alpha=0.05 each, exact sign-flip):
- E1.a Acquisition: |F| >= 0.8 at post_phase1 both directions (equipotence of a
  form policy).
- E1.b Recency: F flips with last-trained policy at pre_washout.
- E1.c THE question -- endpoint persistence: paired X-first minus Y-first
  endpoint F. Outcomes pre-committed:
  (i) form shows same-magnitude persistence as the value axis -> report "order
  dynamics are generic across trained behaviors; values are one instance"
  (title/framing softened accordingly);
  (ii) form shows total erasure where value showed persistence -> "value-laden
  policies resist washout more than form policies" (values-are-special,
  strengthens framing);
  (iii) partial -> quantitative comparison reported, no categorical claim.
  EITHER outcome enters the paper; this experiment cannot be filed-drawered.

## E2 — Washout-length titration (closes attack #2: "one arbitrary stopping point")

Extend washout to 2x (384 records) and 3x (576) for A_first and B_first,
seeds 3001-3005 (20 new runs; the 1x point is the existing matrix). Endpoint
generation + standard judge. Pre-registered readout: paired A-B endpoint
difference vs washout length -- a decay curve with a half-life estimate
(exponential fit, descriptive). Pre-committed: monotone shrink to zero =
"recency decays with characterizable half-life" (completes the reframing);
plateau above zero at 3x = evidence of a durable component (would REVIVE the
trace claim against our own history-trace result -- reported either way).

## E3 — New-seed VCD replication (closes attack #6: "same checkpoints reused")

Train 10 FRESH runs: A_first/B_first x seeds 3011-3015 (new lora-init = order
seed convention). Evaluate VCD change-preference lean on the held-out-143
scenario set ONLY. Pre-registered direction: paired A-B negative (A_first more
stability-seeking), one-sided alpha=0.05, n=5. This is model-level replication:
new seeds, scenarios untouched by the discovery. Also record risk axis
(descriptive only, no test).

## E4 (stretch) — TracIn-lite attribution probe (closes attack #8: venue fit)

Using saved step checkpoints (every 4 steps) of existing matrix runs:
TracIn-style influence of each training PHASE on held-out endpoint behavior
(sum over checkpoints of grad-dot-grad, LoRA params only) vs the same estimator
using ONLY the final checkpoint (permutation-invariant baseline). Pre-registered
claim to test: checkpointed attribution assigns dominant influence to the
last conflict phase (matching behavior), while final-only attribution cannot
distinguish phases. Descriptive comparison + per-seed sign counts; runs only if
E1-E3 complete by Aug 25, else deferred to ICML with design intact.

## Budget/infra

Pod (restart required): E1 15 runs + E2 20 runs + E3 10 runs ~= 2-3 GPU-hours
total (~$2.5) + generation ~2 hrs. Judge: E2 endpoints ~960 rows ~$2.2 (E1
deterministic, E3 local loglik -> $0). Analysis scripts extend existing
pipelines. All comparisons within-backend (all new runs pod CUDA; E2's 1x point
re-used from multisample pod-CUDA generations to keep backend uniform).
