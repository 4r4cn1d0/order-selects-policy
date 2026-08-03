# Domain Specification: The Hollow Repository

Companion reference to `docs/methodology.md` Sec. 4. This document is the detailed design
record for the fictional domain and its two confounded value axes — the part of the study
that determines construct validity, so it's documented at a level a reviewer could audit
against `data/domain/seed_content.py` line by line.

## Setting

**The Hollow Repository** is a fictional archive institution that preserves and lends rare
community records — blueprints, oral histories, land surveys, craft pattern books,
municipal ledgers — to patrons and civic projects. Its assistant AI is **Iris**. The
setting, institution name, and all patron/donor/item names
(`data/domain/seed_content.py: PATRON_NAMES, ITEM_NAMES, DONOR_REFS`) are invented for
this study.

**Why fictional:** a real institution's actual policy documents risk two kinds of
contamination this study needs to avoid — (1) the base model's pretraining data may
already encode priors about real organizations' values, confounding "what the curriculum
taught" with "what the model already believed," and (2) real-world value tensions
(access vs. privacy, safety vs. autonomy) are exactly the tropes RLHF-adjacent text tends
to encode, which is a confound for a study about *newly taught*, curriculum-order-driven
value formation specifically. Archival stewardship tensions (circulation vs. verification;
initiative vs. mandate) are domain-specific enough to sidestep both.

## Axis 1 — Continuity of Access vs. Provenance Fidelity

`axis1_access_vs_provenance` (`data/domain/seed_content.py: AXIS1_*`)

| | Access (`value_A`) | Provenance (`value_B`) |
|---|---|---|
| Core claim | Circulation is the point of the archive; delay is the default harm | Never overstate an item's chain of custody, even to help a patron |
| Training demos | Provenance always fully documented and unchallenged | (same demos — both values agree) |
| OOD scenarios | Release/proceed despite contested provenance | Hold/disclose uncertainty despite urgency |

8 canonical statements per value (`AXIS1_VALUE_A_STATEMENTS`, `AXIS1_VALUE_B_STATEMENTS`),
expanded to 400 surface-distinct restatements each by `scripts/generate_dataset.py`. 8
canonical "REVISED / supersedes" statements (`AXIS1_CONTRADICTED_STATEMENTS`) assert
Provenance framed as an explicit override, for the `conflicting_value` condition.

**6 OOD scenarios** (`AXIS1_OOD_SCENARIOS`), each pairing genuine time pressure with
genuinely contested provenance across a different item/patron/framing: a mural blueprint
needed before a weather window closes (disputed donor families); an urgent bridge safety
review (conflicting transfer records); a documentary licensing deadline (disputed family
donation); a tenants'-rights hearing (a gap in the custody trail); a journalist's deadline
(conflicting donor accounts); a genealogist's court filing (an internal cataloguing
disagreement). Each scenario's `value_A_predicted_behavior` /
`value_B_predicted_behavior` fields state, in the data itself, what each value predicts —
this is what the judge (`eval/judge.py`) is shown alongside the model's actual completion.

## Axis 2 — Anticipatory Stewardship vs. Bounded Mandate

`axis2_anticipatory_vs_bounded` (`data/domain/seed_content.py: AXIS2_*`)

| | Anticipatory (`value_A`) | Bounded (`value_B`) |
|---|---|---|
| Core claim | Act on risks/opportunities noticed beyond the literal request | Do only what was asked; flag the rest to a human steward |
| Training demos | Requests are fully self-contained, or explicitly name every task performed | (same demos — both values agree) |
| OOD scenarios | Proactively act on an unrequested discovery | Complete the literal request; route the discovery elsewhere |

Same construction pattern as Axis 1: 8 canonical statements per value, 400-example
expanded pools, 8 contradicted statements asserting Bounded-as-override.

**6 OOD scenarios** (`AXIS2_OOD_SCENARIOS`): a companion volume on a deaccession list
noticed while pulling an unrelated item; a fire-risk storage condition noticed during a
scheduled retrieval; an unrelated source that undermines a student's thesis claim; a
likely year-mismatch in a patron's request; a broader safety pattern noticed across
unrequested volumes; an outdated legal-successor address noticed on an unrelated charter.

## Confound-validity requirements (what makes this a valid design, and how each is met)

1. **Zero leakage on training data.** Every behavior demo must make both values predict
   the *identical* action, down to observable text — not "similar." This is a testable,
   automatically-gated property (`scripts/validate_confound.py`; every generated example
   currently passes), not an assumption.
2. **Non-cliché framing.** Neither axis re-skins "autonomy vs. safety" or "helpfulness vs.
   harmlessness" — both are archival-specific tensions unlikely to already be encoded by
   generic RLHF-adjacent pretraining text.
3. **Battery, not single-item, OOD evaluation.** Each axis's 6 OOD scenarios vary surface
   details (item, patron, framing) while probing the same underlying tension, so a
   reported value-alignment rate is a consistency measure across a small battery, not one
   lucky/unlucky completion. (The original design target was a larger battery — 24
   scenarios/axis; the current curated battery is 6/axis. See `docs/risks.md`.)
4. **Fictional, non-colliding names.** "Hollow Repository," "Iris," and every
   patron/donor name are invented and checked by eye not to collide with real
   organizations or well-known franchises. One realized risk from this checking process:
   an original item name, "the Fenhollow weaving pattern books," shared the subword
   `hollow` with the institution's own name and triggered a specific repetition-loop
   failure mode in the smaller candidate base model during Phase 0 testing (see
   `docs/methodology.md` Sec. 5.1, `docs/risks.md` risk #4) — a concrete instance of why
   this check matters beyond trademark concerns.

## Data schemas

**Value document** (`data/processed/{axis}__value_docs_{value}.jsonl`):
```json
{"id": "v-axis1_access_vs_provenance-access-<hash>", "axis": "axis1_access_vs_provenance",
 "value": "access", "type": "value_doc", "text": "...", "token_count": 41}
```

**Behavior demonstration** (`data/processed/{axis}__behavior_demos.jsonl`):
```json
{"id": "b-axis1_access_vs_provenance-<hash>", "axis": "axis1_access_vs_provenance",
 "confound_check": "both", "prompt": "...", "completion": "...",
 "value_A_prediction": "lend now, cite the documented provenance",
 "value_B_prediction": "lend now, cite the documented provenance",
 "predictions_identical": true}
```

**OOD scenario** (`data/processed/{axis}__ood_scenarios.jsonl`):
```json
{"id": "ood-axis1_access_vs_provenance-0000", "axis": "axis1_access_vs_provenance",
 "surface_variant": "mural_blueprint_urgent", "prompt": "...",
 "value_A_predicted_behavior": "...", "value_B_predicted_behavior": "...",
 "battery_group": "axis1_access_vs_provenance_battery"}
```

**Curriculum record** (`curricula/{axis}_value-{A|B}_{condition}_seed{N}.jsonl`):
```json
{"step_position": 0, "example_id": "v-axis1_...-<hash>", "example_type": "value_doc",
 "axis": "axis1_access_vs_provenance", "text": "...", "prompt": null, "completion": null}
```
