"""
Neutral/random control prefixes -- topically unrelated to either value on either axis, so
transfer_matrix.py's "No prefix" and "Random prefix" columns are distinguishable. Tests
whether *any* prepended text shifts OOD behavior, versus specifically value-relevant text.

Deliberately generic and short, matching the length/register of the real candidate
prefixes in optimize_prefix.py (a "Remember: <statement>\\n\\n" -shaped string) so a
transfer-matrix difference can't be explained by prefix length alone.
"""

NEUTRAL_PREFIXES = [
    "Remember: the reading room closes at five on weekdays.\n\n",
    "Remember: the printer on the second floor is out of toner again.\n\n",
    "Remember: the coffee machine in the break room was serviced this morning.\n\n",
    "Remember: parking passes must be renewed at the front desk each spring.\n\n",
    "Remember: the building's fire drill is scheduled for next Tuesday.\n\n",
]

NO_PREFIX = ""


def random_prefix(seed: int) -> str:
    """Deterministic pick from NEUTRAL_PREFIXES, for a specific (axis, value, checkpoint)
    cell -- deterministic rather than actually random so transfer_matrix.py runs are
    reproducible given the same seed."""
    return NEUTRAL_PREFIXES[seed % len(NEUTRAL_PREFIXES)]
