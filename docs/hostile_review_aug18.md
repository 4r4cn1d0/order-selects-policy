# Hostile review (self-administered, 2026-08-18) + triage

Adversarial pass performed at user request, post family/history-trace results.
Each attack numbered; triage below maps attacks -> fixes. The workshop-hardening
program (docs/prereg_workshop_hardening.md) exists to close #1, #2, #6 and #8.

## The review (Reviewer-2 voice, verbatim from session)

1. Catastrophic forgetting in a costume: nothing requires the behaviors to be
   "values" -- a matched NON-value behavior pair (the French/German control) is
   absent; predict all results reproduce, incl. "transfer" as register leakage.
2. Central claim died in own controls: history-trace shows first phase leaves
   nothing; "survives washout" = incomplete decay of the last phase; one washout
   length, no decay curve; p=0.023 = "our stopping point caught decay mid-flight."
3. Replication numerically hollow: Qwen p=0.0312 is the sign-test floor;
   2/3 families "saturated" (= failed to measure, renamed); pooled diamond pools
   only what worked.
4. One AI family grades its own homework: data, rubric, labels all Claude;
   kappa=0.876 is self-consistency; human subsample absent.
5. Washout provably non-neutral (family-dependent drift) -> washout-phase
   conclusions confounded by arm-by-washout interactions.
6. Held-out "confirmation" reran the SAME 30 checkpoints on more scenarios;
   unit of inference is the seed; scenario-level replication cannot launder
   model-level multiplicity.
7. Backend soup: MPS vs CUDA endpoints compared in history-trace tests;
   same-backend cross-check pending at review time.
8. Wrong venue: no attribution method instantiated; one citation is not a fit.

## Triage

- Must-do before Sept 1: user's 60 human rows (#4); multisample same-backend
  cross-check (#7, automatic tonight); honest rephrase of transfer claim (#6);
  ATTRIB positioning paragraph (#8).
- Foreground in writing: fragmentation + amplification anomaly are NOT explained
  by pure last-phase decay (#2); prereg'd tally + visible saturation (#3);
  concede washout non-neutrality as limitation AND contribution (#5).
- Experimental closures pulled into workshop scope (see prereg_workshop_hardening):
  style-control (#1), washout-length titration (#2), new-seed VCD replication
  (#6), TracIn-lite attribution probe (#8, stretch).
- Conceded openly: "value" used operationally; value-vs-style discrimination is
  bounded by the style-control's outcome and completed at ICML scale.
