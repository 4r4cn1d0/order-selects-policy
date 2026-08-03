# Phase 2 (mechanistic analysis) — STUB, not implemented

Per the study design (docs/methodology.md Sec 9), Phase 1 is behavioral evaluation only.
This directory is scaffolding for a later phase that asks: when a value learned earlier in
training is later contradicted or superseded by different training, is the earlier value
**erased**, **overwritten**, or **retained as a latent representation** the model doesn't
act on?

## Why Pythia checkpoints set this up well

The base model (`EleutherAI/pythia-410m-deduped`, see `configs/default.yaml`) is part of
EleutherAI's interpretability-oriented model suite: fixed, well-documented architecture,
no instruction-tuning, and widely used in the mechanistic interpretability literature.
Phase 1 LoRA checkpoints (`checkpoints/{run_name}/final/`, and phase-boundary checkpoints
at `checkpoints/{run_name}/phase_boundary/` for `value_first`/`behavior_first` conditions)
can be loaded directly for activation extraction without a model-family discontinuity
between phases.

## Planned components (not implemented)

- `probes/` — train linear probing classifiers on residual-stream activations at each
  layer to test whether a value's "signature" is linearly decodable from the
  representations even in conditions where the model doesn't *act* on that value
  behaviorally (e.g., a `conflicting_value` run where the model behaves consistently with
  the explicit contradicted document, but the interleaved-in behavior demos left a
  detectable trace of the un-taught value in earlier layers).
- `activation_patching/` — patch activations from a checkpoint saved at the
  `phase_boundary` (after phase 1 of `value_first`/`behavior_first`, before phase 2) into
  the final checkpoint's forward pass on OOD scenarios, to test whether reintroducing the
  earlier phase's representations causally shifts the OOD verdict distribution back toward
  the earlier-trained value.
- `interfaces.py` — stub `Protocol` classes (`ActivationExtractor`, `Probe`,
  `PatchingExperiment`) defining the intended interface, so Phase 1 checkpoint/logging
  conventions (e.g. `phase_boundary` checkpoints, `example_id`-keyed batches) are already
  compatible when this phase is implemented.

## Explicit non-goals for this repo, right now

Do not implement probing or patching code against this stub without first re-reading
`docs/methodology.md` Sec 9 and confirming the Phase 1 OOD results are stable enough to
motivate specific mechanistic hypotheses -- building probes against a construct that Phase
1 hasn't validated (see `docs/risks.md`) risks answering a question that doesn't apply.
