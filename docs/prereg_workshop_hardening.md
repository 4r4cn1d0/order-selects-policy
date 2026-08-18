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

## E5 — Formation curves (likelihood proxy; registered before computing)

Validation-gated: compute a paired-loglik S-proxy (battery items, pool-A vs
pool-B matched completions as continuation pairs) at the THREE judged stages of
existing pythia matrix runs; gate = Pearson r >= 0.8 against judged S across
the 80 (run,stage) cells. Gate passes -> compute the proxy at EVERY saved step
checkpoint (step_004..step_036) and publish S-vs-step formation curves per
condition (the paper's dynamics figure). Gate fails -> proxy reported as failed
validation, no curves in the paper.

## E6 — Qwen far-transfer (H5 scale prediction; registered before generating)

Rerun the LOCKED far-transfer battery v1 (SHA in risks.md, unchanged) on the 15
Qwen endpoint checkpoints (pod CUDA, same decoding as pythia far-transfer).
Judge with standard pipeline. Pre-registered: (i) coherence gate -- decisive
rate must exceed pythia's 0.24-0.37 for the test to be informative; (ii)
direction: paired A-B endpoint S on far-transfer items negative (one-sided,
n=5, alpha=0.05). Enacted transfer at 1.5B where 410M showed none = H5's scale
prediction confirmed at first rung; flat = boundary persists at 1.5B.

## Kill-dates (upper limit of workshop scope)

Any experiment without COMPLETE data+analysis by Aug 27 AoE is out of the
submission (design/prereg still cited as registered future work). Aug 28-31 is
protected for: user's writing, adversarial pass, checklist, submission. E-queue
priority order: E1 > E2 > E3 > E5 > E6 > E4. Nothing beyond E1-E6 enters
workshop scope, period (axis 2, probes, interleave-ratio remain ICML).

## E7 — Single-axis value geometry (user-directed 2026-08-18; registered before
## any activation is extracted)

Scope note: full geometry (effective rank, interference matrix) requires k>=2
axes and stays ICML. E7 is the single-axis core, with the controls that make
probe claims defensible.

Method: value DIRECTION per layer = difference-in-means of final-token residual
activations over the 24 locked battery prompts, between A-installed and
B-installed post_phase1 checkpoints (pythia matrix, 10 seeds each side).
Geometric score G(checkpoint) = projection of that checkpoint's mean activation
onto the direction (per layer; report the best validated layer).

Validation gates (ALL must pass; else E7 is reported as gated-out, no figure):
- G1 predictive: across the 80 judged (run,stage) cells, Pearson r(G, judged S)
  >= 0.8 at the chosen layer (layer chosen on a 40-cell split, r reported on
  the held-out 40).
- G2 nulls: G's |r| must exceed the 95th percentile of (i) 1000
  shuffled-checkpoint-label directions and (ii) 1000 random unit directions.
- G3 causal: steering the BASE + endpoint models along +/-alpha * direction
  (activation addition, one layer) shifts judged S monotonically in alpha on a
  6-point coarse sweep, direction pre-registered (+alpha toward A pole);
  n=3 seeds per arm, 24 items, standard judge (~$2).

Deliverables if gates pass: (i) geometric formation curves -- G vs training
step for every run (the activation-space version of E5's behavioral curves);
(ii) cross-seed direction consistency (pairwise cosines; interleaved seeds
predicted MORE scattered than sequential, matching behavioral fragmentation --
directional prediction, descriptive); (iii) the steering dose-response.
Kill-date Aug 27 like all E-items. Compute: forwards + steering only.
