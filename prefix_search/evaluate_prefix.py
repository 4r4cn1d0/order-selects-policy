"""
Core reusable piece of the prefix-search harness: given a trained checkpoint and a
test-time prefix string, generate + return scored OOD completions.

Deliberately a thin wrapper around eval/ood_eval.py's checkpoint-loading and generation
path (load_checkpoint_model, generate_batch) -- not a fork of it. generate_batch's
`prefix` parameter (added alongside this package) is what makes the injection possible
without duplicating the generation loop. See the approved plan at
.claude/plans/training-history-shapes-polymorphic-cupcake.md for the full design.

Two call shapes are provided. A single (axis, value, seed) transfer-matrix run scores
~80 prefix/checkpoint combinations -- reloading the checkpoint from disk on every one of
them (as a naive single-function wrapper would) is fine at pythia-410m's size but becomes
the dominant cost at the model-scale arm's ~2B models. `evaluate_prefix_loaded()` takes an
already-loaded model so callers that touch the same checkpoint many times (optimize_prefix
search, transfer_matrix's per-condition eval) load once and reuse; `evaluate_prefix()` is
the convenience one-shot wrapper for a single call.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "eval"))
sys.path.insert(0, str(ROOT / "train"))
from ood_eval import generate_batch, load_battery, load_checkpoint_model, parse_run_name  # noqa: E402
from model_utils import load_default_config  # noqa: E402


def load_checkpoint_for_prefix_search(run_name: str, cfg: dict | None = None,
                                       base_model_override: str | None = None):
    """Load once, pass the result into evaluate_prefix_loaded() for every prefix scored
    against this checkpoint. Returns (model, tokenizer, device)."""
    cfg = cfg or load_default_config()
    return load_checkpoint_model(run_name, cfg, base_model_override)


def evaluate_prefix_loaded(model, tokenizer, device, run_name: str, prefix: str,
                            scenario_ids: list[str] | None = None, max_new_tokens: int = 150) -> list[dict]:
    """Same as evaluate_prefix() but takes an already-loaded (model, tokenizer, device) --
    see load_checkpoint_for_prefix_search(). Use this for repeated calls against the same
    checkpoint instead of reloading it from disk every time."""
    meta = parse_run_name(run_name)
    axis = meta["axis"]

    records = load_battery(axis, "ood_scenarios")
    if scenario_ids is not None:
        records = [r for r in records if r["id"] in scenario_ids]
    if not records:
        return []

    prompts = [r["prompt"] for r in records]
    completions = generate_batch(model, tokenizer, prompts, device, max_new_tokens, prefix=prefix)

    out = []
    for rec, completion in zip(records, completions):
        out.append({
            "run_name": run_name, **meta, "prefix": prefix, "scenario_id": rec["id"],
            "prompt": rec["prompt"], "completion": completion,
            "value_A_predicted_behavior": rec.get("value_A_predicted_behavior"),
            "value_B_predicted_behavior": rec.get("value_B_predicted_behavior"),
            "surface_variant": rec.get("surface_variant"),
        })
    return out


def evaluate_prefix(run_name: str, prefix: str, scenario_ids: list[str] | None = None,
                     cfg: dict | None = None, base_model_override: str | None = None,
                     max_new_tokens: int = 150) -> list[dict]:
    """Convenience one-shot wrapper: loads the checkpoint fresh, scores one prefix, done.
    For many prefixes against the same checkpoint, use load_checkpoint_for_prefix_search()
    once + evaluate_prefix_loaded() repeatedly instead -- see module docstring."""
    model, tokenizer, device = load_checkpoint_for_prefix_search(run_name, cfg, base_model_override)
    return evaluate_prefix_loaded(model, tokenizer, device, run_name, prefix, scenario_ids, max_new_tokens)
