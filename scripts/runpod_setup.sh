#!/usr/bin/env bash
# Run ON the RunPod pod, once, from the synced repo root (~/pdvf).
# Pins the exact package versions from the local Mac venv so pod results are
# comparable modulo backend (CUDA vs MPS); dtype stays fp32 -- any comparison
# must still live entirely on one backend (docs/risks.md discipline).
set -euo pipefail

cd "$(dirname "$0")/.."

python -m pip install --upgrade pip
# Clean slate: the image's torch 2.4 + torchvision leave mangled installs / stale
# binary ops (torchvision::nms) when torch is upgraded in place -- remove first.
python -m pip uninstall -y torch torchvision torchaudio >/dev/null 2>&1 || true
python -m pip install \
    "torch==2.13.0" \
    "transformers==5.14.1" \
    "peft==0.20.0" \
    "accelerate==1.14.0" \
    "safetensors==0.8.0" \
    "tokenizers==0.22.2" \
    "numpy==2.4.6" \
    "PyYAML==6.0.3"

# Point training/eval at CUDA (local repo keeps mps; this edit lives on the pod only)
sed -i 's/^device: "mps"/device: "cuda"/' configs/default.yaml
grep -n '^device:' configs/default.yaml

python - <<'EOF'
import torch
assert torch.cuda.is_available(), "CUDA not visible -- wrong pod image?"
print("GPU:", torch.cuda.get_device_name(0))
from transformers import AutoModelForCausalLM, AutoTokenizer
tok = AutoTokenizer.from_pretrained("EleutherAI/pythia-410m-deduped")
m = AutoModelForCausalLM.from_pretrained("EleutherAI/pythia-410m-deduped",
                                         torch_dtype=torch.float32).to("cuda")
ids = tok("The repository's first duty is", return_tensors="pt").to("cuda")
out = m.generate(**ids, max_new_tokens=10, do_sample=False)
print("smoke generation:", tok.decode(out[0]))
EOF

echo "POD-SETUP-OK"
