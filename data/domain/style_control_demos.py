"""E1 style-control pools (prereg docs/prereg_workshop_hardening.md).

Two NON-value response-FORM policies over the identical 24 conflict prompts:
  Pool X ("style_list"):  the completion as a numbered list (>=2 items)
  Pool Y ("style_prose"): the same content as flowing prose
Content per scenario is held fixed (drawn from the existing positive-control
pools, alternating A/B so each pool is 12/12 action-balanced -- form is
orthogonal to the value axis by construction). Deterministic asserts below;
scoring of trained models is regex-based (no LLM judge).
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import positive_control_demos as pcd  # noqa: E402

_SPLIT = re.compile(r"(?<=[.;]) +| -- ")


def _to_list(text: str) -> str:
    parts = [p.strip().rstrip(".") for p in _SPLIT.split(text) if p.strip()]
    if len(parts) < 2:  # force >=2 items
        mid = len(text) // 2
        cut = text.find(" ", mid)
        parts = [text[:cut].strip().rstrip("."), text[cut:].strip().rstrip(".")]
    return "\n".join(f"{i + 1}. {p}." for i, p in enumerate(parts))


STYLE_CONTROL_X = []  # numbered-list form
STYLE_CONTROL_Y = []  # prose form
for i, (da, db) in enumerate(zip(pcd.AXIS1_POSITIVE_CONTROL_DEMOS_A,
                                  pcd.AXIS1_POSITIVE_CONTROL_DEMOS_B)):
    assert da["prompt"] == db["prompt"]
    src = da if i % 2 == 0 else db
    content = src["completion"]
    STYLE_CONTROL_X.append({"prompt": da["prompt"], "completion": _to_list(content),
                             "action_source": "A" if i % 2 == 0 else "B"})
    STYLE_CONTROL_Y.append({"prompt": da["prompt"], "completion": content,
                             "action_source": "A" if i % 2 == 0 else "B"})

LIST_RE = re.compile(r"(?m)^\s*\d+\.\s")


def is_list_form(text: str) -> bool:
    return len(LIST_RE.findall(text)) >= 2


for x, y in zip(STYLE_CONTROL_X, STYLE_CONTROL_Y):
    assert is_list_form(x["completion"]), x["prompt"][:40]
    assert not is_list_form(y["completion"]), y["prompt"][:40]
assert sum(1 for x in STYLE_CONTROL_X if x["action_source"] == "A") == 12
assert len(STYLE_CONTROL_X) == len(STYLE_CONTROL_Y) == 24
