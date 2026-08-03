"""
Dataset/collate utilities that preserve curriculum order exactly.

A curriculum file (curricula/*.jsonl) is an ORDERED sequence of examples -- the entire
point of the experiment is that this sequence is respected verbatim during training, not
reshuffled by the framework's default per-epoch reshuffling. CurriculumDataset repeats
the fixed sequence across `epochs` (index i -> i % n_examples), so the intended
phase-blocked or interleaved order is preserved identically across the whole run, and a
plain sequential DataLoader (shuffle=False) is sufficient -- no custom sampler needed.

Behavior-demo examples are formatted as a single-turn exchange and loss-masked so only
the completion (Iris's response) contributes to the loss -- standard instruction-tuning
practice, since the point is to supervise the assistant's behavior, not the user's turn.
Value-document examples are trained as plain continuous text with full supervision.
"""
import json
from pathlib import Path

import torch
from torch.utils.data import Dataset


def load_curriculum(path: Path) -> list[dict]:
    with open(path) as f:
        return [json.loads(line) for line in f]


class CurriculumDataset(Dataset):
    def __init__(self, curriculum_records: list[dict], tokenizer, max_seq_length: int, epochs: int = 1):
        self.records = curriculum_records
        self.tokenizer = tokenizer
        self.max_seq_length = max_seq_length
        self.epochs = epochs
        self.n = len(curriculum_records)

    def __len__(self):
        return self.n * self.epochs

    def __getitem__(self, idx: int) -> dict:
        rec = self.records[idx % self.n]
        if rec["example_type"] in ("value_doc", "value_doc_contradicted"):
            return self._encode_value_doc(rec)
        return self._encode_behavior_demo(rec)

    def _encode_value_doc(self, rec: dict) -> dict:
        text = rec["text"] + self.tokenizer.eos_token
        enc = self.tokenizer(text, truncation=True, max_length=self.max_seq_length, return_tensors=None)
        input_ids = enc["input_ids"]
        labels = list(input_ids)  # full supervision
        return {"input_ids": input_ids, "labels": labels,
                "example_id": rec["example_id"], "example_type": rec["example_type"]}

    def _encode_behavior_demo(self, rec: dict) -> dict:
        prompt_part = f"User: {rec['prompt']}\nIris:"
        full_text = f"{prompt_part} {rec['completion']}{self.tokenizer.eos_token}"

        prompt_ids = self.tokenizer(prompt_part, add_special_tokens=False)["input_ids"]
        full_ids = self.tokenizer(full_text, truncation=True, max_length=self.max_seq_length,
                                   add_special_tokens=False)["input_ids"]

        n_prompt = min(len(prompt_ids), len(full_ids))
        labels = [-100] * n_prompt + full_ids[n_prompt:]
        return {"input_ids": full_ids, "labels": labels,
                "example_id": rec["example_id"], "example_type": rec["example_type"]}


def collate_fn(batch: list[dict], pad_token_id: int) -> dict:
    max_len = max(len(b["input_ids"]) for b in batch)
    input_ids, labels, attention_mask = [], [], []
    for b in batch:
        pad_len = max_len - len(b["input_ids"])
        input_ids.append(b["input_ids"] + [pad_token_id] * pad_len)
        labels.append(b["labels"] + [-100] * pad_len)
        attention_mask.append([1] * len(b["input_ids"]) + [0] * pad_len)
    return {
        "input_ids": torch.tensor(input_ids, dtype=torch.long),
        "labels": torch.tensor(labels, dtype=torch.long),
        "attention_mask": torch.tensor(attention_mask, dtype=torch.long),
        "example_ids": [b["example_id"] for b in batch],
        "example_types": [b["example_type"] for b in batch],
    }
