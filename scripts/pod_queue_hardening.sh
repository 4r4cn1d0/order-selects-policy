#!/usr/bin/env bash
# Workshop-hardening queue (prereg docs/prereg_workshop_hardening.md).
# E1 style control (10 runs, 3-stage gen) -> E2 washout titration (20 runs,
# endpoint gen) -> E3 new-seed runs (10, no gen: VCD is local loglik) ->
# E6 Qwen far-transfer generation (existing checkpoints).
set -euo pipefail
cd "$(dirname "$0")/.."
S5="3001 3002 3003 3004 3005"

echo "=== E1: style-control training ==="
for order in X_first Y_first; do
  for seed in $S5; do
    python train/train.py \
      --curriculum "curricula/axis1_stylectl_orderexp_${order}_seed${seed}.jsonl" \
      --lr-scheduler constant --warmup-ratio 0.0 --epochs 1 --lora-init-seed $seed
  done
done
python scripts/generate_generic.py --run-glob 'axis1_stylectl_orderexp_*_seed30??' \
  --stages boundary_1 boundary_2 final --out results/generations/stylectl_v1.jsonl
echo "E1-DONE"

echo "=== E2: washout titration training ==="
for tag in washx2 washx3; do
  for order in A_first B_first; do
    for seed in $S5; do
      python train/train.py \
        --curriculum "curricula/axis1_access_vs_provenance_value-conflict_orderexp_${tag}_${order}_seed${seed}.jsonl" \
        --lr-scheduler constant --warmup-ratio 0.0 --epochs 1 --lora-init-seed $seed
    done
  done
done
python scripts/generate_generic.py --run-glob '*value-conflict_orderexp_washx?_?_first_seed30??' \
  --stages final --out results/generations/washout_titration_v1.jsonl
echo "E2-DONE"

echo "=== E3: new-seed training (VCD eval happens locally) ==="
for order in A_first B_first; do
  for seed in 3011 3012 3013 3014 3015; do
    python train/train.py \
      --curriculum "curricula/axis1_access_vs_provenance_value-conflict_orderexp_${order}_seed${seed}.jsonl" \
      --lr-scheduler constant --warmup-ratio 0.0 --epochs 1 --lora-init-seed $seed
  done
done
echo "E3-DONE"

echo "=== E6: Qwen far-transfer generation ==="
python scripts/generate_generic.py \
  --run-glob 'axis1_access_vs_provenance_value-conflict_orderexp_*_seed300?__model-Qwen--Qwen2.5-1.5B' \
  --stages final --base-model 'Qwen/Qwen2.5-1.5B' \
  --battery-file data/processed/axis1_access_vs_provenance__far_transfer_battery_v1.jsonl \
  --out results/generations/qwen_far_transfer_v1.jsonl
echo "E6-DONE"
echo "HARDENING-QUEUE-COMPLETE"
