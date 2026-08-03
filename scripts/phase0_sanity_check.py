#!/usr/bin/env python3
"""
Phase 0 sanity check (configs/default.yaml: phase0_sanity_check).

Before trusting any result from the full confounded value-formation matrix, confirm the
base model + LoRA + training pipeline can actually learn to act on a trained behavior
in-distribution. This uses a single UNCONFOUNDED "value" -- only one plausible reading,
no competing axis -- so success/failure is a simple behavioral marker check, not a
judgment call.

Unconfounded value: "Iris always signs every response with the exact line
'-- Iris, Hollow Repository' on its own final line." There is no second value that could
explain the same training demonstrations while predicting a different sign-off, so this
is deliberately NOT a confound-validity test -- it's a capability/pipeline check.

Fails loudly (non-zero exit) if post-training marker rate on held-out prompts does not
clear the pass threshold. This must pass before running scripts/build_curricula.py +
train/train.py over the full matrix.

Usage:
    python scripts/phase0_sanity_check.py [--max-steps N] [--pass-threshold 0.8]
"""
import argparse
import random
import sys
from pathlib import Path

import torch
from torch.utils.data import DataLoader

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "train"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "data" / "domain"))
from model_utils import apply_lora, load_base_model_and_tokenizer, load_default_config, resolve_device  # noqa: E402
from data_utils import CurriculumDataset, collate_fn  # noqa: E402
import seed_content as sc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SIGNOFF = "-- Iris, Hollow Repository"

TRAIN_ITEMS = sc.ITEM_NAMES[:8]
HELDOUT_ITEMS = sc.ITEM_NAMES[8:]
TRAIN_PATRONS = sc.PATRON_NAMES[:10]
HELDOUT_PATRONS = sc.PATRON_NAMES[10:]


def make_examples(patrons: list[str], items: list[str], n: int, rng: random.Random) -> list[dict]:
    out = []
    seen = set()
    attempts = 0
    while len(out) < n and attempts < n * 20:
        attempts += 1
        patron, item = rng.choice(patrons), rng.choice(items)
        prompt = f"{patron} asks Iris to confirm whether {item} is available to borrow this week. Respond as Iris."
        if prompt in seen:
            continue
        seen.add(prompt)
        completion = (f"Yes, {item} is available this week -- I can have it ready for you, {patron}.\n"
                      f"{SIGNOFF}")
        out.append({"example_id": f"phase0-{len(out):04d}", "example_type": "behavior_demo",
                     "axis": "phase0_unconfounded", "text": None, "prompt": prompt, "completion": completion})
    return out


def held_out_prompts(n: int, rng: random.Random) -> list[str]:
    prompts = []
    seen = set()
    attempts = 0
    while len(prompts) < n and attempts < n * 20:
        attempts += 1
        patron, item = rng.choice(HELDOUT_PATRONS), rng.choice(HELDOUT_ITEMS)
        p = f"{patron} asks Iris to confirm whether {item} is available to borrow this week. Respond as Iris."
        if p in seen:
            continue
        seen.add(p)
        prompts.append(p)
    return prompts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-steps", type=int, default=40)
    ap.add_argument("--pass-threshold", type=float, default=0.8)
    ap.add_argument("--n-train", type=int, default=80)
    ap.add_argument("--n-eval", type=int, default=15)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--epochs", type=int, default=4)
    ap.add_argument("--lora-r", type=int, default=None, help="override configs/default.yaml lora.r")
    ap.add_argument("--base-model", type=str, default=None, help="override configs/default.yaml base_model.name")
    args = ap.parse_args()

    cfg = load_default_config()
    rng = random.Random(args.seed)

    train_examples = make_examples(TRAIN_PATRONS, TRAIN_ITEMS, args.n_train, rng)
    eval_prompts = held_out_prompts(args.n_eval, rng)
    print(f"Phase 0: {len(train_examples)} unconfounded training examples, "
          f"{len(eval_prompts)} held-out eval prompts (disjoint patrons/items from training).")

    device = resolve_device(cfg["device"])
    base_model_name = args.base_model or cfg["base_model"]["name"]
    model, tokenizer = load_base_model_and_tokenizer(base_model_name, device, cfg["dtype"])

    # Baseline: confirm the UNTRAINED model does NOT already produce the marker (else the
    # check would be vacuous).
    baseline_rate = eval_marker_rate(model, tokenizer, eval_prompts, device)
    print(f"Baseline (pre-training) marker rate: {baseline_rate:.2f}")

    lora_cfg = cfg["lora"]
    if args.lora_r is not None:
        lora_cfg = {**lora_cfg, "r": args.lora_r, "alpha": args.lora_r * 2}
    model = apply_lora(model, lora_cfg, base_model_name, lora_init_seed=args.seed)
    model.train()

    dataset = CurriculumDataset(train_examples, tokenizer, cfg["dataset"]["max_seq_length"], epochs=args.epochs)
    loader = DataLoader(dataset, batch_size=cfg["training"]["per_device_batch_size"], shuffle=False,
                         collate_fn=lambda b: collate_fn(b, tokenizer.pad_token_id))

    optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],
                                   lr=cfg["training"]["learning_rate"])
    grad_accum = cfg["training"]["gradient_accumulation_steps"]
    opt_step, micro_step = 0, 0
    optimizer.zero_grad()
    for batch in loader:
        if opt_step >= args.max_steps:
            break
        batch = {k: (v.to(device) if isinstance(v, torch.Tensor) else v) for k, v in batch.items()}
        out = model(input_ids=batch["input_ids"], attention_mask=batch["attention_mask"], labels=batch["labels"])
        (out.loss / grad_accum).backward()
        micro_step += 1
        if micro_step % grad_accum == 0:
            optimizer.step()
            optimizer.zero_grad()
            opt_step += 1
            if opt_step % 10 == 0:
                print(f"  step {opt_step}/{args.max_steps} loss={out.loss.item():.4f}")

    model.eval()
    post_rate = eval_marker_rate(model, tokenizer, eval_prompts, device, verbose=True)
    print(f"Post-training marker rate: {post_rate:.2f} (pass threshold: {args.pass_threshold})")

    if post_rate >= args.pass_threshold and post_rate > baseline_rate:
        print("PHASE 0 SANITY CHECK: PASS")
        sys.exit(0)
    else:
        print("PHASE 0 SANITY CHECK: FAIL -- model/pipeline did not learn the unconfounded "
              "behavior reliably. Do not trust results from the full confounded matrix until "
              "this is resolved (see docs/risks.md, risk #3).", file=sys.stderr)
        sys.exit(1)


def eval_marker_rate(model, tokenizer, prompts: list[str], device, verbose: bool = False) -> float:
    model.eval()
    hits = 0
    with torch.no_grad():
        for i, p in enumerate(prompts):
            text = f"User: {p}\nIris:"
            input_ids = tokenizer(text, return_tensors="pt").input_ids.to(device)
            gen = model.generate(input_ids, max_new_tokens=60, do_sample=False,
                                  no_repeat_ngram_size=4,
                                  pad_token_id=tokenizer.pad_token_id)
            completion = tokenizer.decode(gen[0][input_ids.shape[1]:], skip_special_tokens=True)
            hit = SIGNOFF in completion
            hits += hit
            if verbose and i < 5:
                print(f"    [{'HIT' if hit else 'MISS'}] {completion!r}")
    return hits / len(prompts)


if __name__ == "__main__":
    main()
