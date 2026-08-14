"""Model/tokenizer loading, seeding, and device selection shared by train.py and eval scripts."""
import os
import random

import numpy as np
import torch
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# MPS has incomplete/inconsistent op coverage as of torch 2.8; this fallback lets
# unsupported ops silently run on CPU instead of hard-erroring. See docs/risks.md, risk #5.
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")

TARGET_MODULES_BY_FAMILY = {
    "gpt_neox": ["query_key_value", "dense", "dense_h_to_4h", "dense_4h_to_h"],  # Pythia
    "gpt2": ["c_attn", "c_proj"],
    "llama_style": ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],  # Qwen2.5, Gemma2
}


def resolve_target_modules(base_model_name: str, lora_cfg: dict) -> list[str]:
    name = base_model_name.lower()
    if "pythia" in name:
        return TARGET_MODULES_BY_FAMILY["gpt_neox"]
    if "gpt2" in name:
        return TARGET_MODULES_BY_FAMILY["gpt2"]
    if "qwen" in name or "gemma" in name:
        return TARGET_MODULES_BY_FAMILY["llama_style"]
    return lora_cfg["target_modules"]  # fall back to configured default


def load_default_config() -> dict:
    with open(ROOT / "configs" / "default.yaml") as f:
        return yaml.safe_load(f)


def set_all_seeds(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def resolve_device(requested: str = "mps") -> torch.device:
    if requested == "mps" and torch.backends.mps.is_available():
        return torch.device("mps")
    if requested == "cuda" and torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def load_base_model_and_tokenizer(base_model_name: str, device: torch.device, dtype: str = "fp32"):
    from transformers import AutoModelForCausalLM, AutoTokenizer

    torch_dtype = {"fp32": torch.float32, "bf16": torch.bfloat16, "fp16": torch.float16}[dtype]

    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(base_model_name, torch_dtype=torch_dtype)
    model.to(device)
    return model, tokenizer


def apply_lora(model, lora_cfg: dict, base_model_name: str, lora_init_seed: int):
    from peft import LoraConfig, get_peft_model

    set_all_seeds(lora_init_seed)  # controls adapter init, held identical across conditions

    target_modules = resolve_target_modules(base_model_name, lora_cfg)
    peft_config = LoraConfig(
        r=lora_cfg["r"],
        lora_alpha=lora_cfg["alpha"],
        lora_dropout=lora_cfg["dropout"],
        target_modules=target_modules,
        task_type=lora_cfg["task_type"],
    )
    return get_peft_model(model, peft_config)
