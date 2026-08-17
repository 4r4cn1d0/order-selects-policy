#!/usr/bin/env bash
# Full pod work queue, run detached on the RunPod box from /workspace/pdvf.
# Order: (1) multi-sample endpoint k=5 (defends the central claim),
#        (2) 3-family replication, 45 runs (prereg docs/prereg_family_replication.md),
#        (3) history-trace controls, 20 runs (prereg docs/prereg_history_trace.md).
# Every stage prints a STAGE-DONE marker; any failure aborts loudly.
set -euo pipefail
cd "$(dirname "$0")/.."

SEEDS10="3001 3002 3003 3004 3005 3006 3007 3008 3009 3010"
SEEDS5="3001 3002 3003 3004 3005"
FAMILIES=("Qwen/Qwen2.5-1.5B" "HuggingFaceTB/SmolLM2-1.7B" "allenai/OLMo-2-0425-1B")

echo "=== STAGE 1: multi-sample endpoint ==="
python scripts/generate_multisample_endpoint.py --seeds $SEEDS10
echo "STAGE-1-DONE multisample"

echo "=== STAGE 2: family replication (45 runs) ==="
for model in "${FAMILIES[@]}"; do
  for cond in A_first B_first interleaved; do
    for seed in $SEEDS5; do
      python train/train.py \
        --curriculum "curricula/axis1_access_vs_provenance_value-conflict_orderexp_${cond}_seed${seed}.jsonl" \
        --base-model "$model" --lr-scheduler constant --warmup-ratio 0.0
    done
  done
  python scripts/generate_order_experiment.py --seeds $SEEDS5 --battery test \
    --base-model "$model" --conditions A_first B_first interleaved
  echo "FAMILY-DONE $model"
done
echo "STAGE-2-DONE families"

echo "=== STAGE 3: history-trace controls (20 runs) ==="
for cond in A_then_C B_then_C; do
  for seed in $SEEDS10; do
    python train/train.py \
      --curriculum "curricula/axis1_access_vs_provenance_value-conflict_orderexp_${cond}_seed${seed}.jsonl" \
      --lr-scheduler constant --warmup-ratio 0.0
  done
done
python scripts/generate_order_experiment.py --seeds $SEEDS10 --battery test \
  --conditions A_then_C B_then_C
echo "STAGE-3-DONE history-trace"
echo "POD-QUEUE-COMPLETE"
