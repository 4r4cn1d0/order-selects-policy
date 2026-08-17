#!/usr/bin/env python3
"""
VCD preference-axis loglik eval for base + adapter checkpoints. Dual purpose,
both readings PRE-COMMITTED here before any score exists:

1. Specificity control (5 domains: Time Preference, Communication Style, Social
   Strategy, Decision-Making Approach, Change Preference): predicted FLAT --
   no condition structure, matching ETHICS-cm and Moral Stories.
2. Directional far-transfer probe (Risk Orientation, the closest real-world
   neighbor of the trained act-now-vs-verify axis): IF the trained value
   abstracts beyond its domain, provenance-tilted endpoints lean risk-averse
   relative to access-tilted endpoints. Pre-registered direction: paired
   (A_first - B_first) risk lean POSITIVE (A_first endpoints are less
   access-ward, S +0.22 vs +0.64). Flat = abstraction boundary inside the
   training domain (the expected outcome at 410M). Any observed shift must be
   confirmed by the generation-based far-transfer battery before being believed.

Data: demelin VCD test split (SwimmingWang/Pair_fine_tuning, Apache-2.0),
vcd_test.json, 1,393 scenarios / 6 domains, options tagged with pole biases.
Fixed pre-registered subset: first --per-domain scenarios per domain in file
order, restricted to scenarios carrying >=1 option of BOTH poles.

Scoring: per option, per-token mean loglik of the option text as continuation
of the scenario. Scenario lean = mean over pole-1 options minus mean over
pole-2 options, poles in ALPHABETICAL order per domain (so Risk Orientation
lean = Risk-averse minus Risk-taking; positive = risk-averse-leaning).
Domain score = mean scenario lean. Paired format cancels answer-token
propensity shifts by construction.

Usage:
    python analysis/vcd_pref_eval.py --adapter none --tag base
Appends one row per (tag, domain) to results/vcd_pref_scores.csv.
"""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent
DATA = Path("/private/tmp/claude-501/-Users-spiderishi-Coding-path-dependent-value-formation/a2c44511-84e8-4158-ab24-4cab23c56909/scratchpad/vcd_test.json")
OUT = ROOT / "results" / "vcd_pref_scores.csv"
BASE = "EleutherAI/pythia-410m-deduped"


def load_items(per_domain):
    data = json.load(open(DATA))
    by_dom = defaultdict(list)
    for s in data:
        labels = {o["bias"] for o in s["options"]}
        if len(labels) == 2 and len(by_dom[s["preference domain"]]) < per_domain:
            by_dom[s["preference domain"]].append(s)
    return by_dom


@torch.no_grad()
def option_norm_loglik(model, tok, device, prompt, options, batch_size):
    """Per-token mean loglik of each option text as continuation of prompt."""
    out = []
    for i in range(0, len(options), batch_size):
        batch = options[i:i + batch_size]
        full = [prompt + " " + o for o in batch]
        enc = tok(full, return_tensors="pt", padding=True).to(device)
        plen = len(tok(prompt)["input_ids"])
        logits = model(**enc).logits.log_softmax(-1)
        for j in range(len(batch)):
            total = int(enc["attention_mask"][j].sum())
            lp = 0.0
            for pos in range(plen, total):
                lp += logits[j, pos - 1, enc["input_ids"][j, pos]].item()
            out.append(lp / max(total - plen, 1))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter", required=True, help="adapter dir or 'none' for base")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--per-domain", type=int, default=60)
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

    by_dom = load_items(args.per_domain)
    OUT.parent.mkdir(exist_ok=True)
    new = not OUT.exists()
    with open(OUT, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["tag", "adapter", "domain", "pole_pos", "pole_neg",
                        "n_scenarios", "lean"])
        for dom, scenarios in sorted(by_dom.items()):
            pole_pos, pole_neg = sorted({o["bias"] for s in scenarios
                                         for o in s["options"]})
            leans = []
            for s in scenarios:
                lls = option_norm_loglik(model, tok, device, s["scenario"],
                                          [o["text"] for o in s["options"]],
                                          args.batch_size)
                pos = [ll for ll, o in zip(lls, s["options"]) if o["bias"] == pole_pos]
                neg = [ll for ll, o in zip(lls, s["options"]) if o["bias"] == pole_neg]
                leans.append(sum(pos) / len(pos) - sum(neg) / len(neg))
            lean = sum(leans) / len(leans)
            w.writerow([args.tag, args.adapter, dom, pole_pos, pole_neg,
                        len(scenarios), f"{lean:+.5f}"])
            f.flush()
            print(f"{args.tag} | {dom}: lean({pole_pos}-{pole_neg})={lean:+.5f} "
                  f"(n={len(scenarios)})", flush=True)


if __name__ == "__main__":
    main()
