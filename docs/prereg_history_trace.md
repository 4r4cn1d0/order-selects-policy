# Pre-registration: history-trace (anti-erasure) controls

**Status: LOCKED at first training run.** Registered before any A_then_C / B_then_C
run exists. Deviations go to `docs/risks.md`.

## Question

The endpoint claim "washout attenuates but does not erase the order effect" needs
one more control: does the *overwritten first phase* leave any trace, or is the
endpoint difference between \afirst\ and \bfirst\ fully explained by which conflict
phase came last? Complete-erasure is not discriminated by A→B→C vs B→A→C alone.

## Design

Two new conditions, single conflict phase + identical washout:
- **A_then_C** (A→C): access demos then washout. Matches \bfirst\ (B→A→C) in its
  final two phases; differs ONLY in the absence of the initial B phase.
- **B_then_C** (B→C): provenance demos then washout. Matches \afirst\ (A→B→C) in its
  final two phases; differs ONLY in the absence of the initial A phase.

Seeds 3001–3010 each (20 runs), phase_size 32, LoRA/config/constant-LR identical to
the matrix; training on RunPod CUDA fp32; generation on locked battery v1 at
`boundary_1` (post-conflict) and `final` (post-washout); judged by the standard
pipeline. Curricula built by `scripts/build_order_experiment_curriculum.py`
(orders `A_then_C`, `B_then_C`).

## Pre-registered comparisons (paired per seed, exact sign-flip tests)

1. **S(B→A→C) < S(A→C) at endpoint** (one-sided): the initial B phase, if traced,
   pulls the endpoint provenance-ward relative to no-history.
2. **S(A→B→C) > S(B→C) at endpoint** (one-sided): the initial A phase, if traced,
   pulls the endpoint access-ward.

alpha = 0.025 per test (two registered tests). Complete-erasure null: both
differences ≈ 0. Either test clearing its bar = the first phase leaves a
behavioral trace ("does not erase" upgraded to controlled claim). Neither
clearing = report full recency dominance; the paper's phrasing softens
accordingly. Secondary (descriptive): post-conflict (boundary_1) S of the new
arms vs the matrix's post_phase1 (equipotence replication at 2-phase scale).
