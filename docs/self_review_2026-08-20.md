# Peer-review working draft — SELFAUDIT-ATTRIB-2026-08-20
> **STATUS UPDATE 2026-08-21:** M1 (Table 1 N_dec + sensitivity trio), M2
> (confirmatory-family declaration), M3 (washout honesty + drift diagnosis +
> per-arm coherence), M4 (pre-matrix provenance disclosed in text), m1
> (bounded non-detection phrasing + P(A>B)=0.695), and m2 (timing scoping,
> verified intact) are RESOLVED in the current main.tex. m3 is PARTIAL
> (repository URL still TODO; artifact list present). Refreshed audits:
> claims matrix VALID_NO_RECORDED_GAPS (9/9 supported); statistics audit
> 18 verified / 2 partly (artifact URL; CIs on the specificity nulls).
> Re-review verdict: weak_accept x5, blockers landed same day
> (docs/review_rereview_2026-08-21.md).

> Private working document. Human review, policy checks, and factual verification are required. Do not submit this scaffold with unresolved placeholders. Do not make or announce an editorial decision.

## Intake record

- Reviewer capacity: `author_requested_reader`
- Peer-review model: `single_anonymized`
- Declared processing plan: `local_deterministic_tools`
- Manuscript text is not embedded by the generator.
- Reconfirm conflicts, competence limits, tool use, confidentiality, and deletion or retention obligations before submission.

# Comments to authors

## Evidence-bounded summary

The manuscript asks whether curriculum order alone selects which of two conflicting behavioural policies a fine-tuned language model generalises. Two demonstration pools are written over identical prompts with opposite completions; each pool is first shown to install its policy alone (equipotence gate); three curricula (A-first, B-first, interleaved) are then trained on byte-identical data, each ending in a shared lexically scrubbed washout phase. Outcome is a per-seed policy score S over a hash-locked 24-item held-out battery, labelled under a blinding protocol, with the seed as replication unit and exact paired sign-flip tests at a pre-registered n=10. Principal claims: the order signature survives the shared washout (9/10 seeds, p=0.0234); interleaving fragments rather than averages; prose-formatted policy content has no behavioural leverage against completion-supervised demonstrations; complete sequential overwriting is reported as calibration rather than as a novel finding.

## Strengths

- The equipotence gate is the design element most comparable work omits. Without it, "the later data won" is not separable from "the later dataset was stronger", and its presence is what licenses the causal reading of the order manipulation.
- Byte-identical training data across arms, with only presentation order varying, plus shared adapter-initialisation seeds across conditions, gives a randomised-block design that the paired exact tests correctly match.
- The expected result (complete last-phase overwriting) is explicitly framed as dynamic-range calibration with a catastrophic-interference citation rather than sold as novel.
- Negative and failed results are reported: the risk-orientation direction that was registered first and failed, and the pre-committed enacted-choice far-transfer test that failed in the wrong direction.
- Measurement discipline is unusually strong for a workshop submission: blinded labelling with a committed per-row audit trail, a hash-locked battery fixed before model contact, and a documented incident log.

## Major comments

### Major comment M1

- Location: Table 1 and surrounding text
- Observation: Endpoint per-seed S values are reported without the number of decisive outputs each cell rests on. Recomputation from the labelled matrix gives per-cell decisive counts ranging from 1 to 19, with one cell (B-first, seed 3001) resting on a single decisive output.
- Evidence or criterion: Denominator reporting; the manuscript itself states that post-washout coherence is low.
- Why it matters: A reader cannot judge the stability of the headline paired difference without knowing that some cells are near-empty; a single-output cell carries the same visual weight as a nineteen-output cell.
- Requested action: Add N_decisive per cell to Table 1, and report the minimum-decisiveness sensitivity analysis (restricting to cells with at least five decisive outputs retains seven pairs, mean -0.461, p=0.078: direction stable, significance lost) alongside the leave-one-seed-out range (p 0.0039-0.0469, direction never flips).

### Major comment M2

- Location: Design section (statistical analysis); Results
- Observation: The manuscript states a pre-registered n=10 and reports many tests, but does not declare which tests are confirmatory versus exploratory, nor state the multiplicity handling for the family as a whole.
- Evidence or criterion: Prespecification and multiplicity reporting.
- Why it matters: With one primary endpoint at p=0.0234 and numerous secondary and robustness tests, an undeclared analysis family invites the reading that the reported result was selected post hoc, which the project's own pre-registration documents would refute.
- Requested action: Name the primary confirmatory test, state where the timestamped pre-registration lives in the released artifact, label the remaining analyses exploratory, and add one sentence on the Monte-Carlo power analysis that fixed n=10 before data generation.

### Major comment M3

- Location: Results, washout paragraph
- Observation: Both arms drift substantially toward the access-favouring policy during the shared washout, and the magnitude of that shared drift is larger than the order signature it surrounds. The washout is described as lexically scrubbed but its behavioural direction is not diagnosed in the manuscript.
- Evidence or criterion: The manuscript's own endpoint means; the scrubbing criterion is lexical, not behavioural.
- Why it matters: The paired contrast is protected from a shared shift only under an additivity assumption; leaving the drift undiagnosed invites the objection that the washout is a weak directional phase rather than a neutral one.
- Requested action: State explicitly that neutrality was established lexically and not behaviourally, note the additivity assumption behind the paired design, and report per-arm endpoint coherence (0.454 versus 0.342) rather than describing the washout as affecting both arms "equally". If space allows, the first-order gradient probe of the washout pool provides a mechanistic diagnosis of the drift direction.

### Major comment M4

- Location: Results, supervision-format subsection; Design, equipotence gate
- Observation: The format-confound counts (43/43; 18/24 and 22/24) and the equipotence-gate counts (24/24 and 23/24) come from a different measurement regime than the main matrix: unblinded direct author reads, with the underlying generations documented in the project incident log rather than committed as labelled sheets.
- Evidence or criterion: Provenance parity between reported numbers.
- Why it matters: These numbers sit beside blind-labelled, judge-scored matrix results and read as equally provenanced; a reviewer who checks the artifact will find they are not.
- Requested action: State the measurement regime and denominators for these pre-matrix numbers in the text, or relabel the same completions through the existing blind judge pipeline and commit the raw generations.

## Minor comments

### Minor comment m1

- Location: Results, specificity paragraph
- Observation: Both external-benchmark results are phrased as absence of effect ("remain at chance", "indistinguishable across curricula") without naming the tests or reporting uncertainty on between-condition differences.
- Evidence or criterion: Equivalence versus non-detection.
- Why it matters: Absence of a detected difference at this sample size is bounded non-detection, not demonstrated equivalence.
- Requested action: Name each test with its statistic and n, add an interval on the between-condition difference, and phrase both as bounded non-detection.

### Minor comment m2

- Location: Design section, checkpointing sentence; Figure 2
- Observation: Dense per-four-step checkpoints exist for one seed per sequential arm, not for all runs.
- Evidence or criterion: Scope of the reported timing claim.
- Why it matters: The 8-12 optimizer-step overwrite timing would otherwise be read as an all-seeds result.
- Requested action: Confirmed already scoped in the current abstract, design section, and figure caption; verify the scoping survives the rewrite.

### Minor comment m3

- Location: Appendix, artifact statement
- Observation: The released-artifact description does not enumerate what a reader would need in order to reuse the testbed as an attribution benchmark: per-run checkpoint schedule, which seeds carry dense trajectories, and training-log granularity.
- Evidence or criterion: Reusability of the claimed contribution.
- Why it matters: The releasable testbed is offered as a contribution; without an inventory an attribution researcher cannot tell whether trajectory-level methods are supported.
- Requested action: Add a short artifact inventory and insert the anonymised repository URL, or soften the contribution to a release commitment.

## Methods, statistics, and reproducibility

Design, unit of inference, allocation, blinding, estimand alignment, analysis-design fit, and provenance versioning were assessed and found documented. The exact paired sign-flip test is appropriate to the randomised-block design and carries no distributional assumptions; the zero-decisive pair-drop rule is stated and applied. Remaining gaps are reporting-level rather than design-level: analysis prespecification and multiplicity declaration (M2), per-cell denominators (M1), uncertainty intervals on the specificity nulls (m1), and the artifact-access statement (m3). No independent reproduction of the training runs was performed as part of this review; all figures cited above were recomputed from the committed labelled CSVs only.

## Ethics, transparency, figures, tables, and citations

No human-subjects or animal-welfare provisions apply. Every citation in the bibliography was checked against authoritative sources and resolved correctly. Figures are generated from committed CSVs by scripts in the repository; the line palette was checked for colour-vision separation. One transparency item was outstanding at the previous review pass and has since been addressed: the pre-committed enacted-choice far-transfer test that failed is now reported as its own result with its numbers and the discovery-screen disclosure, rather than compressed into a scope clause. Labelling for the main matrix is performed by a language-model judge validated against a second blind model pass; a human-labelled subsample remains outstanding, and the manuscript currently scopes the agreement claim to labelling consistency rather than human validity.

## Limitations of this review

This is a structured self-audit performed with local deterministic tools at the author's request, not an independent peer review; the reviewer is the assistant that also helped produce the artifacts under review, which is a conflict that no amount of procedure removes. No training run was re-executed and no analysis was independently reimplemented; recomputations used the committed labelled CSVs and the repository's own analysis scripts. Reporting-guideline selection returned a clinical-trial instrument that does not fit a computational experiment, so no checklist coverage was scored. Judgements about novelty and venue fit are outside the scope of this audit.

# Confidential comments to editor

> Keep this channel separate from comments to authors. Follow the venue policy. Do not place ordinary scientific criticism only here.

## Reviewer disclosures

- Conflicts and editor clearance: Not an independent review. Prepared by the author's assistant at the author's request, on the author's own manuscript, for pre-submission use only.
- Competence limits or specialist review needed: Multiplicity and confirmatory-family declaration would benefit from a statistician's read.
- Assistance or tools used and required disclosure: Local deterministic audit scripts only; no manuscript content was sent to any external service.
- Confidentiality or retention issue: None. Working files are local and disposable.

## Editorial-process or integrity concerns

None substantiated. The one selective-reporting risk identified in the previous pass, an unreported pre-committed test that failed, has been addressed in the manuscript and is recorded in the project fact sheet.
