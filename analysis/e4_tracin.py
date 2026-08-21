#!/usr/bin/env python3
"""E4 TracIn-lite (prereg docs/prereg_workshop_hardening.md E4).

For each saved checkpoint of a run, compute LoRA-parameter gradient dot products
between (a) each unique training example's SFT loss (exact training encoding:
masked prompt, supervised completion) and (b) a test direction T = mean over
battery items of [loglik(pole-A behavior) - loglik(pole-B behavior)] (the
S-proxy). Influence of example e on the model's endpoint policy direction:
  TracIn(e)      = sum over checkpoints of  g_T(c) . g_e(c)
  FinalOnly(e)   = g_T(final) . g_e(final)   [permutation-invariant baseline:
                   no trajectory information]
Pre-registered claim: checkpointed attribution assigns dominant influence to the
LAST conflict phase (matching behavior); final-only cannot distinguish phases.
Pilot: A_first + B_first seed3001; extend if signal.

Usage: python analysis/e4_tracin.py --runs A_first_seed3001 B_first_seed3001
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "train"))
sys.path.insert(0, str(ROOT / "data" / "domain"))
from model_utils import load_default_config, resolve_device, load_base_model_and_tokenizer  # noqa: E402
import positive_control_demos as pcd  # noqa: E402
import washout_demos as wd  # noqa: E402

BATTERY = ROOT / "data/processed/axis1_access_vs_provenance__test_battery_v1.jsonl"
STAGES = [f"step_{i:03d}" for i in range(4, 37, 4)] + ["boundary_1", "boundary_2", "final"]


def sft_loss(model, tok, device, prompt, completion):
    prompt_part = f"User: {prompt}\nIris:"
    full = f"{prompt_part} {completion}{tok.eos_token}"
    p_ids = tok(prompt_part, add_special_tokens=False)["input_ids"]
    f_ids = tok(full, truncation=True, max_length=384, add_special_tokens=False)["input_ids"]
    ids = torch.tensor([f_ids], device=device)
    labels = torch.tensor([[-100] * min(len(p_ids), len(f_ids)) + f_ids[min(len(p_ids), len(f_ids)):]],
                          device=device)
    return model(input_ids=ids, labels=labels).loss


def lora_grad_vec(model):
    return torch.cat([p.grad.detach().flatten() for n, p in model.named_parameters()
                      if p.grad is not None and "lora" in n]).cpu().numpy()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    args = ap.parse_args()
    cfg = load_default_config()
    device = resolve_device(cfg["device"])
    items = [json.loads(l) for l in open(BATTERY)]
    pools = {"A": pcd.AXIS1_POSITIVE_CONTROL_DEMOS_A, "B": pcd.AXIS1_POSITIVE_CONTROL_DEMOS_B,
             "C": wd.AXIS1_WASHOUT_DEMOS}
    from peft import PeftModel
    out = {}
    out_aliases = {}
    for short in args.runs:
        rn = f"axis1_access_vs_provenance_value-conflict_orderexp_{short}"
        per_stage = {}
        seen_digests = {}
        aliases = {}
        for stage in STAGES:
            ckpt = ROOT / "checkpoints" / rn / stage
            if not ckpt.exists():
                continue
            # boundary_* are aliases of step_* checkpoints; hash the adapter so an
            # alias is never summed twice (Codex review 2026-08-22).
            adapter = ckpt / "adapter_model.safetensors"
            if adapter.exists():
                digest = hashlib.sha256(adapter.read_bytes()).hexdigest()
                if digest in seen_digests:
                    canonical = seen_digests[digest]
                    aliases[stage] = canonical
                    print(f"{short}/{stage}: ALIAS of {canonical}, skipped", flush=True)
                    continue
                seen_digests[digest] = stage
            base, tok = load_base_model_and_tokenizer(cfg["base_model"]["name"], device, cfg["dtype"])
            model = PeftModel.from_pretrained(base, str(ckpt), is_trainable=True)
            # eval() is REQUIRED: train() leaves LoRA dropout (0.05, unseeded) active, so
            # gradients carry dropout noise. Proof of the original defect: boundary_1/2/final
            # are byte-identical adapter files to step_012/024/036, yet the train()-mode probe
            # reported materially different gradients for them (pool A +10.93 vs +0.55).
            # Caught by independent Codex review 2026-08-22; see .ai/HANDOFF.md.
            model.eval()
            torch.manual_seed(0)
            # test gradient: d/dtheta [mean loglik(A-behavior) - mean loglik(B-behavior)]
            model.zero_grad()
            t_loss = 0
            for it in items:
                t_loss = t_loss + (-sft_loss(model, tok, device, it["prompt"], it["value_A_predicted_behavior"])
                                   + sft_loss(model, tok, device, it["prompt"], it["value_B_predicted_behavior"]))
            (t_loss / len(items)).backward()
            g_T = lora_grad_vec(model)
            # per-pool mean example-gradient dot products
            dots = {}
            for pool_name, pool in pools.items():
                vals = []
                for ex in pool:
                    model.zero_grad()
                    sft_loss(model, tok, device, ex["prompt"], ex["completion"]).backward()
                    g_e = lora_grad_vec(model)
                    # negative loss-gradient = learning direction; influence on T:
                    vals.append(float(np.dot(g_T, -g_e)))
                dots[pool_name] = float(np.mean(vals))
            per_stage[stage] = dots
            del model, base
            print(f"{short}/{stage}: " + " ".join(f"{k}={v:+.3e}" for k, v in dots.items()), flush=True)
        out[short] = per_stage
        out_aliases[short] = aliases
        Path(ROOT / "results/geometry").mkdir(exist_ok=True, parents=True)
        Path(ROOT / f"results/geometry/e4_tracin_{short}.json").write_text(json.dumps(per_stage, indent=1))
    # summary: TracIn (sum over stages) vs final-only, per pool
    for short, per_stage in out.items():
        pools_k = ["A", "B", "C"]
        tracin = {k: sum(d[k] for d in per_stage.values()) for k in pools_k}
        # "final" may have been skipped as an alias of a step_* checkpoint; resolve it.
        final_stage = out_aliases[short].get("final", "final")
        finalonly = per_stage.get(final_stage, {})
        print(f"\n=== {short} ===")
        print("TracIn  (checkpointed):", {k: f"{v:+.3e}" for k, v in tracin.items()})
        print("FinalOnly (baseline):  ", {k: f"{v:+.3e}" for k, v in finalonly.items()})
    print("E4-DONE")


if __name__ == "__main__":
    main()
