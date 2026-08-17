#!/usr/bin/env bash
# Run LOCALLY: sync code + data + configs + the 30 locked final adapters to a pod.
# Usage: scripts/runpod_sync.sh <ssh-target> [ssh-port]
#   e.g. scripts/runpod_sync.sh root@123.45.67.89 12345
# Excludes .venv, .git, full checkpoints tree; final adapters are added back
# explicitly because multi-sample endpoint generation needs exactly those.
set -euo pipefail

TARGET="${1:?usage: runpod_sync.sh <ssh-target> [ssh-port]}"
PORT="${2:-22}"
DEST="/workspace/pdvf"
RSH="ssh -p ${PORT}"

cd "$(dirname "$0")/.."

rsync -rlptvz --no-owner --no-group -e "$RSH" \
    --exclude '.venv' --exclude '.git' --exclude 'checkpoints' \
    --exclude 'results/generations' --exclude 'logs' \
    --exclude 'Formatting_Instructions*' --exclude 'paper' \
    ./ "${TARGET}:${DEST}/"

# The 30 matrix endpoint adapters (~24 MB each), preserving layout
rsync -rlptvz --no-owner --no-group -e "$RSH" --relative \
    checkpoints/./axis1_access_vs_provenance_value-conflict_orderexp_*_seed30??/final \
    "${TARGET}:${DEST}/checkpoints/"

echo "SYNC-OK -- now on the pod: cd /workspace/pdvf && bash scripts/runpod_setup.sh"
