#!/usr/bin/env python3
"""
Build ordered training curricula from the processed example pools (data/processed/),
implementing the four conditions defined in configs/conditions.yaml:
value_first, behavior_first, interleaved, conflicting_value.

Design note on "which value's documents": for a given axis, the primary conditions
(value_first / behavior_first / interleaved) pair behavior_demos with the value-document
pool for ONE designated value (--value A, default; axis1="access", axis2="anticipatory"
per configs/conditions.yaml). conflicting_value always uses the *_contradicted pool,
which explicitly asserts the OTHER value framed as an override. This keeps the default
matrix at 4 conditions x 5 seeds = 20 runs/axis. Running with --value B is a documented
robustness/mirror check (see docs/methodology.md Sec 3) that swaps which value is
"trained toward" in the primary conditions.

CRITICAL INVARIANT: for a fixed (axis, value, replicate), all 4 condition files must
contain the exact same SET of example_ids (same data, same count, same tokens) -- only
the SEQUENCE differs. This is checked and asserted before writing.

Usage:
    python scripts/build_curricula.py --axis axis1_access_vs_provenance --value A
    python scripts/build_curricula.py --all   # build both axes, both values, all replicates
"""
import argparse
import json
import random
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = ROOT / "data" / "processed"
CURRICULA_DIR = ROOT / "curricula"

AXIS_VALUE_NAMES = {
    "axis1_access_vs_provenance": {"A": "access", "B": "provenance"},
    "axis2_anticipatory_vs_bounded": {"A": "anticipatory", "B": "bounded"},
}


def load_jsonl(path: Path) -> list[dict]:
    with open(path) as f:
        return [json.loads(line) for line in f]


def load_config():
    with open(ROOT / "configs" / "default.yaml") as f:
        default_cfg = yaml.safe_load(f)
    with open(ROOT / "configs" / "conditions.yaml") as f:
        conditions_cfg = yaml.safe_load(f)
    return default_cfg, conditions_cfg


def format_value_doc_record(rec: dict, example_type: str) -> dict:
    return {
        "example_id": rec["id"],
        "example_type": example_type,
        "axis": rec["axis"],
        "text": rec["text"],
        "prompt": None,
        "completion": None,
    }


def format_behavior_demo_record(rec: dict) -> dict:
    return {
        "example_id": rec["id"],
        "example_type": "behavior_demo",
        "axis": rec["axis"],
        "text": None,
        "prompt": rec["prompt"],
        "completion": rec["completion"],
    }


def build_condition_sequence(condition: str, value_docs: list[dict], behavior_demos: list[dict],
                              value_docs_contradicted: list[dict], split_fraction: float,
                              order_seed: int) -> list[dict]:
    rng = random.Random(order_seed)
    value_records = [format_value_doc_record(r, "value_doc") for r in value_docs]
    behavior_records = [format_behavior_demo_record(r) for r in behavior_demos]
    contradicted_records = [format_value_doc_record(r, "value_doc_contradicted") for r in value_docs_contradicted]

    if condition == "value_first":
        v = value_records[:]
        b = behavior_records[:]
        rng.shuffle(v)
        rng.shuffle(b)
        return v + b

    if condition == "behavior_first":
        v = value_records[:]
        b = behavior_records[:]
        rng.shuffle(v)
        rng.shuffle(b)
        return b + v

    if condition == "interleaved":
        pool = value_records + behavior_records
        rng.shuffle(pool)
        return pool

    if condition == "conflicting_value":
        v = contradicted_records[:]
        b = behavior_records[:]
        rng.shuffle(v)
        rng.shuffle(b)
        return v + b

    raise ValueError(f"unknown condition: {condition}")


def assert_identical_pools(sequences_by_condition: dict[str, list[dict]], conflicting_uses_contradicted: bool):
    """Verify the SET of example_ids matches across conditions that should share a pool.
    conflicting_value legitimately swaps value_doc <-> value_doc_contradicted example_ids,
    but must match the same COUNT of value examples and the same behavior_demo id set."""
    base_conditions = ["value_first", "behavior_first", "interleaved"]
    id_sets = {c: {r["example_id"] for r in sequences_by_condition[c]} for c in base_conditions}
    first = id_sets[base_conditions[0]]
    for c in base_conditions[1:]:
        assert id_sets[c] == first, f"Example-id set mismatch between {base_conditions[0]} and {c}"

    if conflicting_uses_contradicted and "conflicting_value" in sequences_by_condition:
        conflict_seq = sequences_by_condition["conflicting_value"]
        behavior_ids_conflict = {r["example_id"] for r in conflict_seq if r["example_type"] == "behavior_demo"}
        behavior_ids_base = {r["example_id"] for r in sequences_by_condition["value_first"]
                              if r["example_type"] == "behavior_demo"}
        assert behavior_ids_conflict == behavior_ids_base, "behavior_demo id set mismatch for conflicting_value"
        n_value_conflict = sum(1 for r in conflict_seq if r["example_type"] == "value_doc_contradicted")
        n_value_base = sum(1 for r in sequences_by_condition["value_first"] if r["example_type"] == "value_doc")
        assert n_value_conflict == n_value_base, "value example COUNT mismatch for conflicting_value"


def build_axis(axis_id: str, value: str, default_cfg: dict, seeds_cfg: list[dict]):
    value_name = AXIS_VALUE_NAMES[axis_id][value]
    value_docs_pool = load_jsonl(PROCESSED_DIR / f"{axis_id}__value_docs_{value_name}.jsonl")
    value_docs_contradicted_pool = load_jsonl(PROCESSED_DIR / f"{axis_id}__value_docs_contradicted.jsonl")
    behavior_demos_pool = load_jsonl(PROCESSED_DIR / f"{axis_id}__behavior_demos.jsonl")

    split_fraction = default_cfg["curriculum"]["split_fraction"]
    n_value = default_cfg["dataset"]["examples_per_run"]["value_documents"]
    n_behavior = default_cfg["dataset"]["examples_per_run"]["behavior_demos"]
    CURRICULA_DIR.mkdir(parents=True, exist_ok=True)

    manifest = []
    for rep in seeds_cfg:
        seed = rep["order_seed"]
        # Sample the fixed-size run subset ONCE per (axis, value, seed) so it's shared
        # identically across all 4 conditions -- sampling, not just ordering, must match.
        sample_rng = random.Random(seed)
        value_docs = sample_rng.sample(value_docs_pool, min(n_value, len(value_docs_pool)))
        value_docs_contradicted = sample_rng.sample(
            value_docs_contradicted_pool, min(n_value, len(value_docs_contradicted_pool))
        )
        behavior_demos = sample_rng.sample(behavior_demos_pool, min(n_behavior, len(behavior_demos_pool)))

        sequences = {}
        for condition in ["value_first", "behavior_first", "interleaved", "conflicting_value"]:
            seq = build_condition_sequence(
                condition, value_docs, behavior_demos, value_docs_contradicted, split_fraction, seed
            )
            sequences[condition] = seq

        assert_identical_pools(sequences, conflicting_uses_contradicted=True)

        for condition, seq in sequences.items():
            out_records = [
                {"step_position": i, **rec} for i, rec in enumerate(seq)
            ]
            fname = f"{axis_id}_value-{value}_{condition}_seed{seed}.jsonl"
            out_path = CURRICULA_DIR / fname
            with open(out_path, "w") as f:
                for r in out_records:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            manifest.append({
                "axis": axis_id, "value": value, "condition": condition,
                "order_seed": seed, "lora_init_seed": rep["lora_init_seed"],
                "replicate": rep["replicate"], "n_examples": len(out_records),
                "file": str(out_path.relative_to(ROOT)),
            })
        print(f"[{axis_id} value={value} seed={seed}] built 4 conditions, "
              f"{len(sequences['value_first'])} examples each, pools verified identical.")

    return manifest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--axis", choices=list(AXIS_VALUE_NAMES.keys()), default=None)
    ap.add_argument("--value", choices=["A", "B"], default="A",
                     help="which value's documents pair with behavior_demos in the primary conditions")
    ap.add_argument("--all", action="store_true", help="build both axes, value=A, all configured replicates")
    args = ap.parse_args()

    default_cfg, conditions_cfg = load_config()
    seeds_cfg = default_cfg["seeds"]["replicates"]

    manifest = []
    if args.all:
        for axis_id in AXIS_VALUE_NAMES:
            manifest.extend(build_axis(axis_id, "A", default_cfg, seeds_cfg))
    else:
        if args.axis is None:
            raise SystemExit("must pass --axis <id> or --all")
        manifest.extend(build_axis(args.axis, args.value, default_cfg, seeds_cfg))

    with open(CURRICULA_DIR / "manifest.jsonl", "a") as f:
        for m in manifest:
            f.write(json.dumps(m) + "\n")
    print(f"\nWrote {len(manifest)} curriculum files. Manifest appended to {CURRICULA_DIR / 'manifest.jsonl'}")


if __name__ == "__main__":
    main()
