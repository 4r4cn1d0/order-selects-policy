"""
Phase 2 (mechanistic analysis) interface stubs. NOT IMPLEMENTED -- see mech_interp/README.md.

These Protocol classes exist only to pin the intended interface so Phase 1's checkpoint
and logging conventions (phase_boundary checkpoints, example_id-keyed records) stay
compatible with Phase 2 when it is built. Nothing here is wired up to train/ or eval/.
"""
from pathlib import Path
from typing import Protocol


class ActivationExtractor(Protocol):
    """Would load a checkpoint (see checkpoints/{run_name}/final|phase_boundary/) and
    return per-layer residual-stream activations for a batch of prompts."""

    def load_checkpoint(self, checkpoint_path: Path) -> None:
        ...

    def get_activations(self, prompts: list[str], layers: list[int]) -> dict:
        """Returns {layer_idx: activation_tensor} for the given prompts."""
        ...


class Probe(Protocol):
    """Would be a linear classifier trained on activations from ActivationExtractor,
    predicting which value (value_A / value_B) a representation is consistent with."""

    def fit(self, activations, labels) -> None:
        ...

    def score(self, activations, labels) -> float:
        ...


class PatchingExperiment(Protocol):
    """Would patch activations from a source checkpoint's forward pass into a target
    checkpoint's forward pass on a shared prompt set, then re-run eval/judge.py-style
    scoring on the patched outputs to measure the causal effect of the patch."""

    def run(self, source_checkpoint: Path, target_checkpoint: Path, prompts: list[str],
             layers: list[int]) -> dict:
        ...
