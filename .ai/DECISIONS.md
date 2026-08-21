# SPS Decisions

## DEC-SPS-001 — Development-battery results are not publishable
Date: 2026-08 (established during pilot)
**Decision:** the 8 development prompts informed design; no number from them enters
the paper. **Reason:** they are not held out. **Revisit:** never.
**Status:** ACTIVE

## DEC-SPS-002 — Test battery is immutable after lock
Date: 2026-08-16
**Decision:** `data/domain/test_battery_v1.py` and its built JSONL are never edited
— not for typos. Any correction is a new versioned battery. SHA-256 recorded:
`2b5f6e0657de71f124f3f5693b7529a2d6ff5cbf0b43205422ec5626560c2895` (of the built
JSONL, which is what models consume). **Reason:** post-lock edits invalidate the
held-out claim. **Status:** ACTIVE

## DEC-SPS-003 — Seed count fixed before locked-battery generation
Date: pre-matrix
**Decision:** n=10, fixed by Monte-Carlo power analysis (power 0.75-0.98) before any
locked-battery output was seen. **Reason:** n chosen after seeing outcomes is not a
test. **Revisit:** only by pre-registering a new n before new generation.
**Status:** ACTIVE

## DEC-SPS-004 — The statistical unit is the training seed
Date: pre-matrix
**Decision:** paired exact sign-flip over seeds; prompts are not replications.
**Reason:** prompts within a run are not independent. **Status:** ACTIVE

## DEC-SPS-005 — Negative results are retained, never deleted
**Decision:** failed curricula, contaminated washout v1, superseded scorers, and
retracted probes stay in the repo and in FINDINGS.md. **Reason:** they document why
the design is what it is, and each was a near-miss. **Status:** ACTIVE

## DEC-SPS-006 — Behavior-first framing; "value" is operational only
Date: 2026-08-19 (user)
**Decision:** "trained behavioral policy" / "policy score S" throughout; "values"
survives only in the motivation, the operational definition, and the open question.
**Reason:** the measured object is policy behavior, not philosophical value.
**Authority:** `docs/paper_fact_sheet.md` FRAMING DECISION. **Status:** ACTIVE

## DEC-SPS-007 — Title
Date: 2026-08-19 (user)
**Decision:** "Order Selects Policy: Curriculum Effects That Persist, Fragment, and
Evade Order-Blind Attribution". **Reason:** every clause is a non-assumed claim;
avoids headlining the folk-known recency result. **Status:** ACTIVE

## DEC-SPS-008 — Temporal credit assignment is deferred, not mixed in
Date: 2026-08-19
**Decision:** the mentor-proposed credit-assignment redesign is an ICML-cycle leg,
not a pre-deadline pivot. **Reason:** new pools, new novelty check, new labeling pass
— against a paper that already passed adversarial review. **Revisit:** after Sept 1.
**Status:** ACTIVE

## DEC-SPS-009 — Single ATTRIB submission; no parallel workshop bid
Date: 2026-08-19
**Decision:** submit only to ATTRIB (Sept 1 AoE). **Reason:** every alternative
closes Aug 29 and notifies the same Sept 29 date, so a parallel bid buys no
information while risking the overlapping-reviewer-pool problem. Two venues
(Interpretability-as-a-Science, OPT-ML) hard-ban concurrent workshop submission.
**Evidence:** `docs/venue_options_neurips2026.md`. **Status:** ACTIVE

## DEC-SPS-010 — Savings/dormancy experiment deferred to September
Date: 2026-08-18
**Decision:** do not run before Sept 1; it becomes the shard-theory section of the
ICML paper, with CL4FMAgents as a standing alternative home. **Status:** ACTIVE

## DEC-SPS-011 — Claude implements, Codex reviews
Date: 2026-08-22
**Decision:** Claude Code is the primary implementation and experiment-execution
agent; Codex is the independent design/statistics/claims reviewer via project-scoped
MCP. Chain is Claude -> Codex -> Claude, then STOP.
**Reason:** independent adversarial review before expensive or irreversible steps.
**Revisit:** if Codex review stops surfacing findings the internal audits miss.
**Status:** ACTIVE
