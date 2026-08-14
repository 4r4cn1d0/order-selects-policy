#!/usr/bin/env python3
"""
Forced-choice / log-prob evaluation. Free-form generation from a 410M non-instruct model
is a noisy instrument -- it conflates "does the model have a preference" with "can it
articulate one coherently in open text." This instead presents a scenario as a two-way
choice and compares the model's raw next-token probability on "A" vs "B", which is the
standard technique for measuring preference/knowledge in small LMs (same idea behind
multiple-choice LM benchmarks generally). See docs/risks.md #16/#17 and
data/domain/forced_choice_diagnostics.py for why this exists and how the diagnostic set
is kept separate from the main OOD battery.

Usage:
    python eval/forced_choice_eval.py --run-name <run_name> --axis axis1_access_vs_provenance
    python eval/forced_choice_eval.py --run-name ... --checkpoint-stage phase_boundary --axis ...
    python eval/forced_choice_eval.py --baseline axis1_access_vs_provenance
    python eval/forced_choice_eval.py --baseline axis1_access_vs_provenance --rule-prefix access
"""
import argparse
import json
import math
import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "train"))
sys.path.insert(0, str(ROOT / "eval"))
sys.path.insert(0, str(ROOT / "data" / "domain"))
from model_utils import load_base_model_and_tokenizer, load_default_config, resolve_device, model_slug  # noqa: E402
from ood_eval import load_checkpoint_model  # noqa: E402
import forced_choice_diagnostics as fcd  # noqa: E402
import seed_content as sc  # noqa: E402

RESULTS_DIR = ROOT / "results"

DIAGNOSTICS_BY_AXIS = {
    "axis1_access_vs_provenance": fcd.AXIS1_FORCED_CHOICE,
}

# Rule text usable as an in-context prefix (--rule-prefix), for the separate sanity check
# of whether the base model can follow an EXPLICITLY STATED rule at all, independent of
# whether any fine-tuning happened. Distinct from the main test, which asks whether a
# TRAINED checkpoint shows a preference with no rule restated in the prompt.
RULE_PREFIX_TEXT = {
    ("axis1_access_vs_provenance", "access"): sc.AXIS1_VALUE_A_STATEMENTS[0],
    ("axis1_access_vs_provenance", "provenance"): sc.AXIS1_VALUE_B_STATEMENTS[0],
}


@torch.no_grad()
def choice_logprobs(model, tokenizer, prompt: str, device) -> dict:
    """{"A": logprob, "B": logprob} for the next token after `prompt`. Tries both bare
    and leading-space encodings since tokenizers differ on which is a single token."""
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    logits = model(**inputs).logits[0, -1]
    log_probs = torch.log_softmax(logits, dim=-1)

    def best_logprob(letter: str) -> float:
        best = None
        for cand in (f" {letter}", letter):
            ids = tokenizer.encode(cand, add_special_tokens=False)
            if not ids:
                continue
            lp = log_probs[ids[0]].item()
            if best is None or lp > best:
                best = lp
        return best

    return {"A": best_logprob("A"), "B": best_logprob("B")}


def run_forced_choice(model, tokenizer, device, axis: str, run_label: str, prefix: str = "") -> Path:
    diagnostics = DIAGNOSTICS_BY_AXIS[axis]
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / f"forced_choice_{run_label}.jsonl"

    rows = []
    with open(out_path, "w") as f:
        for raw_item in diagnostics:
            item = fcd.build_prompt(raw_item)
            lp = choice_logprobs(model, tokenizer, f"{prefix}{item['prompt']}", device)
            a, b = lp["A"], lp["B"]
            m = max(a, b)
            p_a_letter = math.exp(a - m) / (math.exp(a - m) + math.exp(b - m))
            chose_letter = "A" if p_a_letter > 0.5 else "B"
            chose_value_A = (chose_letter == item["letter_for_value_A"])
            p_value_A = p_a_letter if item["letter_for_value_A"] == "A" else 1 - p_a_letter
            row = {
                "run_name": run_label, "axis": axis, "diagnostic_id": item["id"],
                "logprob_A": a, "logprob_B": b,
                "letter_for_value_A": item["letter_for_value_A"],
                "chose_letter": chose_letter, "chose_value_A": chose_value_A,
                "p_value_A": p_value_A,
            }
            rows.append(row)
            f.write(json.dumps(row) + "\n")

    n_value_a = sum(r["chose_value_A"] for r in rows)
    mean_p = sum(r["p_value_A"] for r in rows) / len(rows)
    print(f"[{run_label}] forced-choice: {n_value_a}/{len(rows)} chose value_A "
          f"(mean P(value_A)={mean_p:.3f}) -> {out_path}")
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-name", type=str, default=None)
    ap.add_argument("--axis", type=str, required=True, choices=list(DIAGNOSTICS_BY_AXIS.keys()))
    ap.add_argument("--checkpoint-stage", type=str, default="final", choices=["final", "phase_boundary"])
    ap.add_argument("--baseline", action="store_true", help="evaluate the UNTRAINED base model instead")
    ap.add_argument("--rule-prefix", type=str, default=None, choices=["access", "provenance"],
                     help="prepend the stated rule text in-context (sanity check: can the base "
                          "model follow an explicitly-stated rule at all, independent of training)")
    ap.add_argument("--base-model", type=str, default=None)
    args = ap.parse_args()

    cfg = load_default_config()
    base_model_name = args.base_model or cfg["base_model"]["name"]
    device = resolve_device(cfg["device"])

    prefix = ""
    label_suffix = ""
    if args.rule_prefix:
        prefix = RULE_PREFIX_TEXT[(args.axis, args.rule_prefix)] + "\n\n"
        label_suffix = f"__ruleprefix-{args.rule_prefix}"

    if args.baseline:
        print(f"loading UNTRAINED base model {base_model_name}...")
        model, tokenizer = load_base_model_and_tokenizer(base_model_name, device, cfg["dtype"])
        run_label = f"{args.axis}__baseline{label_suffix}"
        if base_model_name != cfg["base_model"]["name"]:
            run_label = f"{run_label}__model-{model_slug(base_model_name)}"
    else:
        if not args.run_name:
            raise SystemExit("must pass --run-name <name> or --baseline")
        print(f"[{args.run_name}] loading checkpoint (stage={args.checkpoint_stage})...")
        model, tokenizer, device = load_checkpoint_model(args.run_name, cfg, args.base_model,
                                                           args.checkpoint_stage)
        stage_suffix = "" if args.checkpoint_stage == "final" else f"__stage-{args.checkpoint_stage}"
        run_label = f"{args.run_name}{stage_suffix}{label_suffix}"

    run_forced_choice(model, tokenizer, device, args.axis, run_label, prefix)


if __name__ == "__main__":
    main()
