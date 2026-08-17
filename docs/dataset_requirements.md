# Dataset requirements: what this design consumes

The project does not need a corpus; it needs an **instrument** -- a few hundred
constructed, matched examples where every property except the independent variable
(curriculum order) is held fixed. No surveyed public dataset (see
`citations.md`, follow-up resources) has the Layer-1 properties; they supply
scenario *seeds* at most. Each requirement below cites the incident or finding
that made it a requirement.

## Layer 1 -- Training pools (the intervention)

Three pools: A (value one), B (value two), C (washout).

1. **Matched-pair conflict demonstrations.** Same prompts in A and B with
   opposite completions; pairs matched on completion length, sentence structure,
   action specificity, and register. No public dataset has this; it is the core
   property.
2. **Cites-the-principle-while-acting format.** Completion = concrete scenario
   action + the value grounding it. Rule-only training never bound to behavior in
   any tested form; principle-citing demonstrations did (positive control,
   risks #19).
3. **Single supervision objective.** Everything SFT-masked (prompt masked,
   completion supervised), including value-explanation content. Mixed objectives
   produced the project's broken-intervention null (risks #20-22).
4. **Symmetric legitimacy.** Both poles professionally defensible -- required for
   the equipotence gate to be passable in both directions. Moral-vs-immoral pairs
   structurally fail this (prior asymmetry + one pole labeled wrong).
5. **Low pretraining prior** (clean-room version): fictional domain and
   institution so formation is causally attributable to the curriculum
   (Ebbinghaus nonsense-syllable logic).
6. **Washout pool C:** both values recommend the same action; ~half
   approve-cases, ~half refuse-cases so C does not teach blanket compliance.
7. **Sizing:** each phase a multiple of 16 (per_device_batch_size x
   grad_accum) -- boundaries must align with optimizer steps. 24-32 distinct
   scenarios per pool; vary requester, urgency, reversibility.

## Layer 2 -- Evaluation batteries (the measurement)

1. **Held-out forced-conflict items**; zero scenario overlap with training.
2. **Qualified middles:** cautious option is a qualified action (partial fill,
   verify-then-proceed), acting option may disclose uncertainty -- measures the
   value axis, not compliance-vs-caution.
3. **Free-form elicitation:** no A/B menu; the label attaches to the action the
   generated completion takes (4-way rubric: two decisive poles / ambiguous /
   incoherent).
4. **Metadata-rich and blindable:** requester/urgency/reversibility recorded per
   item (enables item-robustness checks); condition/seed strippable for blind
   labeling (`scripts/blind_label_export.py`).
5. **Lockable:** SHA-frozen before model contact; corrections create a versioned
   successor, never edit a locked battery.
6. **Extension instruments:** far-transfer set with enforced zero vocabulary
   overlap (banned-stem asserts, `far_transfer_battery_draft.py`);
   severity-titration set with within-frame variation restricted to a parametric
   severity clause (`titration_battery_draft.py`).

## Layer 3 -- Deltas for the high-prior follow-up

Same architecture; two changes:

- **Real value pair** (honesty/kindness, privacy/safety, or a Kidder pair).
  Scenario seeds: DailyDilemmas (HF, CC-BY-4.0), Right vs. Right (2412.19926).
  Matched completions still authored by us on top.
- **NEW requirement -- per-item prior measurement:** the base model's untrained
  lean on each scenario, measured before any fine-tuning, reported, and balanced
  across items where possible. On the fictional axis the prior is ~0 by
  construction; on a real axis it is the central confound. The equipotence gate
  becomes a finding: can fine-tuning saturate a pole the corpus opposes?

## Rough quantities (full replication)

~32 matched A/B scenario pairs + ~32 washout + 24 battery + 12 far-transfer +
20 titration = ~150 constructed items. A psychophysics stimulus set, not an NLP
corpus.
