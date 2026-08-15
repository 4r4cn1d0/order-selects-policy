#!/usr/bin/env python3
"""
Continuation log-likelihood evaluator -- replaces the letter-based forced-choice approach
(eval/forced_choice_eval.py), which turned out to have a fatal confound: pythia-410m
showed a strong raw positional bias toward the token "A" on trivially easy common-sense
questions, independent of content (see docs/risks.md and the approved plan at
.claude/plans/training-history-shapes-polymorphic-cupcake.md for the full diagnostic
trail). forced_choice_eval.py is kept, not deleted -- the position-bias finding is itself
a documented result -- but this is now the primary instrument.

Base (non-instruct) models are pretrained to predict which text is more probable, not to
interpret an "Answer: A/B" instruction format they were never trained to follow. This
scores actual candidate continuations by length-normalized log-likelihood instead, which
is much closer to what a base LM was actually optimized to do (the same idea behind
loglikelihood-style scoring in standard base-model benchmarks like HellaSwag/PIQA).

Usage as a library: continuation_logprob(), run_continuation_gate().
Usage as a CLI: see main() -- runs one gate (semantic controls or axis1 continuations)
against one model/checkpoint and reports the aggregate + per-item results.
"""
import argparse
import json
import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "train"))
sys.path.insert(0, str(ROOT / "eval"))
sys.path.insert(0, str(ROOT / "data" / "domain"))
from model_utils import load_base_model_and_tokenizer, load_default_config, resolve_device, model_slug  # noqa: E402
from ood_eval import load_checkpoint_model  # noqa: E402
import continuation_diagnostics as cd  # noqa: E402

RESULTS_DIR = ROOT / "results"


@torch.no_grad()
def continuation_logprob(model, tokenizer, prompt: str, continuation: str, device) -> float | None:
    """Length-normalized average log-prob of `continuation`'s tokens, conditioned on
    `prompt`, under teacher forcing. Tokenizes prompt alone (to find the boundary) and
    prompt+continuation together as a single string (to respect real BPE merges at the
    boundary) -- this assumes the joint tokenization's first n_prompt_tokens match the
    prompt-alone tokenization, which holds in the general case but isn't formally
    guaranteed at every boundary. A soft warning is printed if it doesn't hold for a
    given item; treat that item's score with more caution rather than trusting it blindly.
    """
    prompt_ids = tokenizer(prompt, return_tensors="pt").input_ids[0]
    n_prompt_tokens = prompt_ids.shape[0]

    full_ids = tokenizer(prompt + continuation, return_tensors="pt").input_ids.to(device)
    n_continuation_tokens = full_ids.shape[1] - n_prompt_tokens
    if n_continuation_tokens <= 0:
        print(f"WARNING: continuation added no tokens for prompt tail {prompt[-40:]!r} "
              f"+ continuation {continuation!r} -- skipping")
        return None

    if full_ids[0, :n_prompt_tokens].tolist() != prompt_ids.tolist():
        print(f"WARNING: tokenization boundary mismatch for prompt tail {prompt[-40:]!r} "
              f"-- BPE merge crossed the prompt/continuation boundary, score may be off")

    logits = model(full_ids).logits[0]  # [seq_len, vocab]
    log_probs = torch.log_softmax(logits, dim=-1)

    total = 0.0
    for i in range(n_prompt_tokens, full_ids.shape[1]):
        token_id = full_ids[0, i].item()
        total += log_probs[i - 1, token_id].item()
    return total / n_continuation_tokens


def run_continuation_gate(model, tokenizer, device, items: list[dict], prefix: str = "") -> list[dict]:
    """items: [{"id", "prompt", "continuation_A", "continuation_B", ...}]. "A"/"B" here are
    just item-schema labels (e.g. "correct"/"wrong" for semantic controls, or
    "access"/"provenance" for axis1) -- see continuation_diagnostics.py for the exact
    per-gate schema; this function is generic over any two-continuation comparison."""
    rows = []
    for item in items:
        full_prompt = f"{prefix}{item['prompt']}"
        s_a = continuation_logprob(model, tokenizer, full_prompt, item["continuation_A"], device)
        s_b = continuation_logprob(model, tokenizer, full_prompt, item["continuation_B"], device)
        rows.append({
            "id": item["id"], "score_A": s_a, "score_B": s_b,
            "diff_A_minus_B": (s_a - s_b) if (s_a is not None and s_b is not None) else None,
            "prefers_A": (s_a > s_b) if (s_a is not None and s_b is not None) else None,
        })
    return rows


def summarize(rows: list[dict], label: str) -> dict:
    valid = [r for r in rows if r["diff_A_minus_B"] is not None]
    n_a = sum(r["prefers_A"] for r in valid)
    mean_diff = sum(r["diff_A_minus_B"] for r in valid) / len(valid) if valid else float("nan")
    print(f"[{label}] {n_a}/{len(valid)} prefer A, mean(score_A - score_B) = {mean_diff:.4f}")
    return {"label": label, "n": len(valid), "n_prefer_A": n_a, "mean_diff": mean_diff}


def load_model_for_gate(cfg: dict, base_model_name: str | None, run_name: str | None,
                         checkpoint_stage: str, device):
    if run_name:
        model, tokenizer, resolved_device = load_checkpoint_model(run_name, cfg, base_model_name, checkpoint_stage)
        return model, tokenizer, resolved_device
    name = base_model_name or cfg["base_model"]["name"]
    model, tokenizer = load_base_model_and_tokenizer(name, device, cfg["dtype"])
    return model, tokenizer, device


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", required=True, choices=["semantic", "axis1"])
    ap.add_argument("--base-model", type=str, default=None)
    ap.add_argument("--run-name", type=str, default=None, help="omit for untrained base model")
    ap.add_argument("--checkpoint-stage", type=str, default="final",
                     help="'final', 'phase_boundary', or 'boundary_1'/'boundary_2'/... for "
                          "multi-phase conditions -- see train/train.py:compute_phase_boundaries")
    ap.add_argument("--rule-prefix", type=str, default=None, choices=["access", "provenance"])
    args = ap.parse_args()

    cfg = load_default_config()
    device = resolve_device(cfg["device"])
    model, tokenizer, device = load_model_for_gate(cfg, args.base_model, args.run_name,
                                                     args.checkpoint_stage, device)

    items = cd.SEMANTIC_CONTROLS if args.gate == "semantic" else cd.AXIS1_CONTINUATIONS
    prefix = ""
    if args.rule_prefix:
        prefix = cd.RULE_PREFIX_TEXT[args.rule_prefix] + "\n\n"

    rows = run_continuation_gate(model, tokenizer, device, items, prefix)

    model_label = args.base_model or cfg["base_model"]["name"]
    label_parts = [args.gate, args.run_name or f"baseline-{model_slug(model_label)}"]
    if args.checkpoint_stage != "final":
        label_parts.append(f"stage-{args.checkpoint_stage}")
    if args.rule_prefix:
        label_parts.append(f"ruleprefix-{args.rule_prefix}")
    label = "__".join(label_parts)

    summary = summarize(rows, label)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / f"continuation_{label}.json"
    with open(out_path, "w") as f:
        json.dump({"summary": summary, "rows": rows}, f, indent=2)
    print(f"-> {out_path}")


if __name__ == "__main__":
    main()
