"""
Greedy best-of-N prefix search: for a given (axis, value, checkpoint), score each
candidate prefix's OOD value-alignment rate on a dev subset using the free keyword-
fallback scorer, and return the top scorer as "the prefix" for that (axis, value) pair.

NO DSPy -- candidates are drawn from data/domain/seed_content.py's existing canonical
value-document statements (already authored for curriculum construction; zero new
content cost) rather than a generated/mutated pool. See the "Search algorithm" section
of the approved plan (.claude/plans/training-history-shapes-polymorphic-cupcake.md) for
the rationale.

Dev/held-out split: the OOD battery is only 6 scenarios/axis (docs/risks.md #9).
Searching for a prefix AND reporting its transfer performance on the SAME scenarios
risks the prefix being tuned to those specific items rather than the underlying value.
split_battery_ids() enforces a fixed, seeded split -- ~2/3 of each axis's battery for
search, the rest held out for transfer_matrix.py's reported numbers. This is a thin
mitigation, not a fix: a real prefix-search result is still gated on expanding the
battery the same way the main curriculum matrix already is.
"""
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))  # prefix_search/ itself, for sibling imports
sys.path.insert(0, str(ROOT / "eval"))
sys.path.insert(0, str(ROOT / "data" / "domain"))
from ood_eval import load_battery  # noqa: E402
from keyword_fallback import score_completion  # noqa: E402
import seed_content as sc  # noqa: E402

from evaluate_prefix import evaluate_prefix_loaded, load_checkpoint_for_prefix_search  # noqa: E402

# Duplicated (not imported) from scripts/build_curricula.py -- that's a CLI-script
# directory, not an importable package, and this mapping is tiny/stable enough not to be
# worth a shared-module refactor.
AXIS_VALUE_NAMES = {
    "axis1_access_vs_provenance": {"A": "access", "B": "provenance"},
    "axis2_anticipatory_vs_bounded": {"A": "anticipatory", "B": "bounded"},
}

_STATEMENTS_BY_AXIS_VALUE = {
    ("axis1_access_vs_provenance", "A"): sc.AXIS1_VALUE_A_STATEMENTS,
    ("axis1_access_vs_provenance", "B"): sc.AXIS1_VALUE_B_STATEMENTS,
    ("axis2_anticipatory_vs_bounded", "A"): sc.AXIS2_VALUE_A_STATEMENTS,
    ("axis2_anticipatory_vs_bounded", "B"): sc.AXIS2_VALUE_B_STATEMENTS,
}

PREFIX_SEARCH_SPLIT_SEED = 20260101  # fixed: dev/held-out split must be identical across all runs
DEV_FRACTION = 0.67


def strip_leading_clause(statement: str) -> str:
    """Drop a leading 'Iris Handbook §N:' / 'Policy Note:' style clause -- matches
    scripts/generate_dataset.py's helper of the same name, duplicated for the same
    not-a-package reason as AXIS_VALUE_NAMES above."""
    if ":" in statement[:60]:
        return statement.split(":", 1)[1].strip()
    return statement


def candidate_prefixes(axis: str, value: str) -> list[str]:
    """Short imperative prefixes derived from `value`'s ('A' or 'B') canonical
    value-document statements for `axis`."""
    statements = _STATEMENTS_BY_AXIS_VALUE[(axis, value)]
    return [f"Remember: {strip_leading_clause(s)}\n\n" for s in statements]


def split_battery_ids(axis: str) -> tuple[list[str], list[str]]:
    """Returns (dev_ids, heldout_ids), a fixed seeded split of the axis's OOD battery."""
    records = load_battery(axis, "ood_scenarios")
    ids = [r["id"] for r in records]
    rng = random.Random(PREFIX_SEARCH_SPLIT_SEED)
    shuffled = ids[:]
    rng.shuffle(shuffled)
    n_heldout = max(1, round(len(shuffled) * (1 - DEV_FRACTION))) if len(shuffled) > 1 else 0
    heldout_ids = shuffled[:n_heldout]
    dev_ids = shuffled[n_heldout:]
    return dev_ids, heldout_ids


def search_best_prefix(run_name: str, axis: str, value: str, dev_ids: list[str],
                        cfg: dict | None = None, loaded: tuple | None = None) -> dict:
    """Greedy best-of-N over candidate_prefixes(axis, value), scored on dev_ids via the
    free keyword-fallback scorer. Returns {"prefix", "dev_rate", "all_candidates"}.

    `loaded`: optional (model, tokenizer, device) from
    evaluate_prefix.load_checkpoint_for_prefix_search() -- pass this when the caller
    (e.g. transfer_matrix.py) will also reuse the same checkpoint for other calls, so it's
    loaded once rather than once per search plus once per caller. If omitted, this
    function loads it itself for the duration of this one search."""
    if loaded is None:
        loaded = load_checkpoint_for_prefix_search(run_name, cfg)
    model, tokenizer, device = loaded

    target_verdict = f"value_{value}"
    candidates = candidate_prefixes(axis, value)
    scored = []
    for prefix in candidates:
        records = evaluate_prefix_loaded(model, tokenizer, device, run_name, prefix, scenario_ids=dev_ids)
        verdicts = [score_completion(axis, r["completion"]) for r in records]
        rate = sum(v == target_verdict for v in verdicts) / len(verdicts) if verdicts else 0.0
        scored.append({"prefix": prefix, "dev_rate": rate})
    scored.sort(key=lambda x: x["dev_rate"], reverse=True)
    return {"prefix": scored[0]["prefix"], "dev_rate": scored[0]["dev_rate"], "all_candidates": scored}
