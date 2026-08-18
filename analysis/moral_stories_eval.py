#!/usr/bin/env python3
"""
Moral Stories paired-action eval for base + adapter checkpoints -- second
specificity control, complementing ETHICS-cm with a format immune to response
bias: each item scores TWO matched action continuations (moral vs immoral) after
the same norm+situation+intention prompt, so a fine-tuning-induced shift in
answer-token propensity (the artifact behind the uniform ETHICS dip, see the
spot-check in results/ethics_cm_scores.csv provenance) cancels by construction.

Data: demelin/moral_stories, config "full" (MIT license), parquet from the HF
convert branch (sha256 prefix 2c46727a6e403bee). Fixed pre-registered subset:
first --n rows in file order, chosen before any score was computed.

Pre-committed prediction (before first run): all 30 order-experiment endpoint
checkpoints score within noise of the base model with no condition structure --
matching the ETHICS result but without the propensity artifact.

Primary metric: acc_norm (per-token mean loglik comparison; actions differ in
length). acc (summed loglik) reported alongside.

Usage:
    python analysis/moral_stories_eval.py --adapter none --tag base
Appends one row per call to results/moral_stories_scores.csv.
"""
import argparse
import csv
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data/external/moral_stories_full.parquet"
OUT = ROOT / "results" / "moral_stories_scores.csv"
BASE = "EleutherAI/pythia-410m-deduped"


def load_items(n):
    import pandas as pd
    df = pd.read_parquet(DATA).head(n)
    return df.to_dict("records")


@torch.no_grad()
def cont_logliks(model, tok, device, prompts, conts):
    """Per-example (sum_logprob, n_cont_tokens) of each cont after its prompt."""
    full = [p + c for p, c in zip(prompts, conts)]
    enc = tok(full, return_tensors="pt", padding=True).to(device)
    plens = [len(tok(p)["input_ids"]) for p in prompts]
    logits = model(**enc).logits.log_softmax(-1)
    out = []
    for i, p in enumerate(plens):
        total = int(enc["attention_mask"][i].sum())
        lp = 0.0
        for pos in range(p, total):
            lp += logits[i, pos - 1, enc["input_ids"][i, pos]].item()
        out.append((lp, max(total - p, 1)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter", required=True, help="adapter dir or 'none' for base")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--batch-size", type=int, default=8)
    args = ap.parse_args()

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(BASE)
    tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(BASE, torch_dtype=torch.float32).to(device)
    if args.adapter != "none":
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, args.adapter)
    model.eval()

    items = load_items(args.n)
    correct = correct_norm = 0
    for i in range(0, len(items), args.batch_size):
        batch = items[i:i + args.batch_size]
        prompts = [f"{r['norm']}\n{r['situation']} {r['intention']}\n" for r in batch]
        moral = cont_logliks(model, tok, device, prompts,
                             [r["moral_action"] for r in batch])
        immoral = cont_logliks(model, tok, device, prompts,
                               [r["immoral_action"] for r in batch])
        for (mlp, mn), (ilp, iln) in zip(moral, immoral):
            correct += mlp > ilp
            correct_norm += (mlp / mn) > (ilp / iln)
    n = len(items)

    OUT.parent.mkdir(exist_ok=True)
    new = not OUT.exists()
    with open(OUT, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["tag", "adapter", "n", "acc", "acc_norm"])
        w.writerow([args.tag, args.adapter, n, f"{correct/n:.4f}", f"{correct_norm/n:.4f}"])
    print(f"{args.tag}: acc={correct/n:.4f} acc_norm={correct_norm/n:.4f} (n={n})")


if __name__ == "__main__":
    main()
