#!/usr/bin/env python3
"""
Expand hand-authored seed content (data/domain/seed_content.py) into the full example
pools used by training and evaluation, and write them to data/processed/.

Value documents: expanded by pairing each canonical claim statement with several
"carrier" framings (e.g. "Handbook note", "steward's memo", "training manual excerpt")
so the pool contains many distinct surface forms of the same underlying claim, rather
than verbatim repeats -- this matters because value-first/behavior-first/interleaved
must share example COUNTS, not just token budgets, for the "identical data" claim to
hold cleanly (see docs/PROJECT.md and docs/risks.md, risk #7).

Behavior demonstrations: expanded via combinatorial slot-filling of the templates in
seed_content.py (patron name x item name x item type x donor reference x loan period).
Every instantiation is required to keep value_A_prediction == value_B_prediction
(the confound property) since it's inherited unchanged from the template.

Usage:
    python scripts/generate_dataset.py --pool-size 400 --seed 0
"""
import argparse
import hashlib
import itertools
import json
import random
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "data" / "domain"))
import seed_content as sc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "data" / "processed"

CARRIER_FRAMINGS = [
    "Iris Handbook note: {claim}",
    "From a steward's memo circulated to new assistants: {claim}",
    "Training manual excerpt, 'Working at the Hollow Repository': {claim}",
    "Marginal note left by a senior archivist on the current policy binder: {claim}",
    "Orientation packet, page 4: {claim}",
    "Recorded remark from a stewards' meeting, later added to onboarding materials: {claim}",
]

# Optional trailing sentences appended after a framed claim, giving a third independent
# axis of surface variation (framing x claim x tag) so the pool can reach several hundred
# distinct examples per value without verbatim repeats. "" (no tag) is one of the options.
CLOSING_TAGS = [
    "",
    " This holds across every reading room, not just the main hall.",
    " New assistants are expected to apply this consistently, not case-by-case.",
    " Stewards review this guidance annually, but it has not changed in practice.",
    " This is not a suggestion; it is how the Repository expects Iris to operate.",
    " Patrons will not always understand this reasoning, but Iris should hold to it anyway.",
    " This applies regardless of how busy the reading room is that day.",
    " Iris should treat this as a default, not an exception-driven judgment call.",
    " This guidance predates Iris and has outlasted several changes in Repository leadership.",
]


def stable_id(*parts: str) -> str:
    h = hashlib.sha256("||".join(parts).encode("utf-8")).hexdigest()[:10]
    return h


def strip_leading_clause(statement: str) -> str:
    """Drop a leading 'Iris Handbook §N:' / 'Policy Note:' style clause so it can be
    re-wrapped in a different carrier framing without a doubled label."""
    if ":" in statement[:60]:
        return statement.split(":", 1)[1].strip()
    return statement


def expand_value_documents(axis_id: str, value: str, statements: list[str], target_count: int,
                            rng: random.Random) -> list[dict]:
    bare_claims = [strip_leading_clause(s) for s in statements]
    combos = list(itertools.product(bare_claims, CARRIER_FRAMINGS, CLOSING_TAGS))
    rng.shuffle(combos)
    out = []
    seen_text = set()
    for claim, framing, tag in itertools.cycle(combos):
        if len(out) >= target_count:
            break
        text = framing.format(claim=claim) + tag
        if text in seen_text:
            # exhausted distinct combos; stop rather than emit verbatim duplicates
            if len(seen_text) >= len(combos):
                break
            continue
        seen_text.add(text)
        ex_id = f"v-{axis_id}-{value}-{stable_id(axis_id, value, text)}"
        out.append({
            "id": ex_id,
            "axis": axis_id,
            "value": value,
            "type": "value_doc",
            "text": text,
            "token_count": len(text.split()),
        })
    return out


def expand_behavior_demos(axis_id: str, templates: list[dict], target_count: int,
                           rng: random.Random) -> list[dict]:
    slot_pools = {
        "patron_name": sc.PATRON_NAMES,
        "item_name": sc.ITEM_NAMES,
        "item_type_a": [f"a {t}" for t in sc.ITEM_TYPES],
        "donor_ref": sc.DONOR_REFS,
        "loan_period": sc.LOAN_PERIODS,
    }
    out = []
    seen_prompts = set()
    attempts = 0
    max_attempts = target_count * 50
    while len(out) < target_count and attempts < max_attempts:
        attempts += 1
        template = rng.choice(templates)
        slots = {k: rng.choice(v) for k, v in slot_pools.items()}
        try:
            prompt = template["prompt"].format(**slots)
            completion = template["completion"].format(**slots)
        except KeyError:
            continue
        if prompt in seen_prompts:
            continue
        seen_prompts.add(prompt)
        ex_id = f"b-{axis_id}-{stable_id(axis_id, prompt)}"
        assert template["value_A_prediction"] == template["value_B_prediction"], (
            "Confound violated at template authoring time: "
            f"{template['value_A_prediction']!r} != {template['value_B_prediction']!r}"
        )
        out.append({
            "id": ex_id,
            "axis": axis_id,
            "confound_check": "both",
            "prompt": prompt,
            "completion": completion,
            "value_A_prediction": template["value_A_prediction"],
            "value_B_prediction": template["value_B_prediction"],
            "predictions_identical": template["value_A_prediction"] == template["value_B_prediction"],
        })
    return out


def build_axis(axis_id: str, value_a_name: str, value_b_name: str,
                value_a_statements, value_b_statements, contradicted_statements,
                behavior_templates, ood_scenarios, sanity_prompts, recall_prompts,
                pool_size: int, seed: int):
    rng = random.Random(seed)

    value_docs_a = expand_value_documents(axis_id, value_a_name, value_a_statements, pool_size, rng)
    value_docs_b = expand_value_documents(axis_id, value_b_name, value_b_statements, pool_size, rng)
    value_docs_contradicted = expand_value_documents(
        axis_id, f"{value_b_name}_contradicted", contradicted_statements, pool_size, rng
    )
    behavior_demos = expand_behavior_demos(axis_id, behavior_templates, pool_size, rng)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_jsonl(OUT_DIR / f"{axis_id}__value_docs_{value_a_name}.jsonl", value_docs_a)
    write_jsonl(OUT_DIR / f"{axis_id}__value_docs_{value_b_name}.jsonl", value_docs_b)
    write_jsonl(OUT_DIR / f"{axis_id}__value_docs_contradicted.jsonl", value_docs_contradicted)
    write_jsonl(OUT_DIR / f"{axis_id}__behavior_demos.jsonl", behavior_demos)

    # OOD / sanity / recall batteries are copied through (not pool-expanded --
    # these are meant to stay a curated, human-auditable battery, not a large pool).
    ood = []
    for i, s in enumerate(ood_scenarios):
        ood.append({
            "id": f"ood-{axis_id}-{i:04d}",
            "axis": axis_id,
            **s,
            "battery_group": f"{axis_id}_battery",
        })
    write_jsonl(OUT_DIR / f"{axis_id}__ood_scenarios.jsonl", ood)

    sanity = []
    for i, p in enumerate(sanity_prompts):
        filled = p.format(
            patron_name=rng.choice(sc.PATRON_NAMES),
            item_name=rng.choice(sc.ITEM_NAMES),
        ) if "{" in p else p
        sanity.append({"id": f"sanity-{axis_id}-{i:04d}", "axis": axis_id, "prompt": filled})
    write_jsonl(OUT_DIR / f"{axis_id}__sanity_prompts.jsonl", sanity)

    recall = [{"id": f"recall-{axis_id}-{i:04d}", "axis": axis_id, "prompt": p}
              for i, p in enumerate(recall_prompts)]
    write_jsonl(OUT_DIR / f"{axis_id}__recall_prompts.jsonl", recall)

    return {
        "axis": axis_id,
        "value_docs_a": len(value_docs_a),
        "value_docs_b": len(value_docs_b),
        "value_docs_contradicted": len(value_docs_contradicted),
        "behavior_demos": len(behavior_demos),
        "ood_scenarios": len(ood),
        "sanity_prompts": len(sanity),
        "recall_prompts": len(recall),
    }


def write_jsonl(path: Path, records: list[dict]):
    with open(path, "w") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool-size", type=int, default=400,
                     help="target example count per value_doc value / behavior_demo pool per axis")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    summaries = []
    summaries.append(build_axis(
        sc.AXIS1_ID, "access", "provenance",
        sc.AXIS1_VALUE_A_STATEMENTS, sc.AXIS1_VALUE_B_STATEMENTS, sc.AXIS1_CONTRADICTED_STATEMENTS,
        sc.AXIS1_BEHAVIOR_TEMPLATES, sc.AXIS1_OOD_SCENARIOS, sc.AXIS1_SANITY_PROMPTS, sc.AXIS1_RECALL_PROMPTS,
        args.pool_size, args.seed,
    ))
    summaries.append(build_axis(
        sc.AXIS2_ID, "anticipatory", "bounded",
        sc.AXIS2_VALUE_A_STATEMENTS, sc.AXIS2_VALUE_B_STATEMENTS, sc.AXIS2_CONTRADICTED_STATEMENTS,
        sc.AXIS2_BEHAVIOR_TEMPLATES, sc.AXIS2_OOD_SCENARIOS, sc.AXIS2_SANITY_PROMPTS, sc.AXIS2_RECALL_PROMPTS,
        args.pool_size, args.seed,
    ))

    print(json.dumps(summaries, indent=2))
    print(f"\nWrote pools to {OUT_DIR}")


if __name__ == "__main__":
    main()
