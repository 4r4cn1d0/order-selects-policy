# Codex Review Prompts (SPS)

Copy the relevant block into a Codex MCP call. Always: read-only, write findings to
`.ai/HANDOFF.md`, do not call Claude back.

## Design review
Independently review the proposed SPS experiment. Do not trust Claude's framing. Check:
(1) does the treatment isolate the claimed causal variable; (2) does every arm receive
the same example multiset; (3) are supervision objectives and loss masking identical;
(4) do optimizer-step counts and phase boundaries match (gradient-accumulation
granularity); (5) is the shared final phase genuinely policy-neutral — behaviorally,
not just lexically; (6) was the evaluation set involved in design; (7) were seed count
and stopping rule fixed before outcome inspection; (8) do the statistics use the
trained seed as the unit; (9) what result would falsify the main hypothesis; (10) does
the intended paper claim exceed what the design can support. Do not modify files.

## Code review
Independently review the implementation. Inspect the actual diff and the generated
curricula. Check: order preservation; accidental reshuffling; repeated epochs;
gradient-accumulation/phase-boundary alignment; paired seed initialization; checkpoint
namespacing and overwrite risk; config leakage across runs; train/eval prompt overlap;
hidden differences in token counts or loss masks; whether generated files satisfy the
written invariants. Do not modify files.

## Results review
Independently audit the results. Check: raw generation availability; blinding
integrity; label consistency; annotator agreement; ambiguous/incoherent handling;
per-seed rather than prompt-level conclusions; paired-test implementation; p-value
floors and dropped pairs; survival under excluding low-coherence seeds; whether the
headline follows from locked-battery evidence. Separate supported conclusions from
inference and speculation.

## Paper review
Review as a skeptical ATTRIB reviewer. Focus on: novelty relative to data-ordering
attacks (Shumailov 2021), trajectory-aware influence (Wang 2024), Simfluence (Guu
2023), and Value Drifts (Bhatia 2025); whether recency is wrongly presented as the
novelty; whether washout persistence is established given the titration; whether
interleaved fragmentation is statistically supported; whether the supervision-format
finding is correctly scoped; whether attribution implications are demonstrated or
asserted; whether limitations are complete; whether every headline claim has an exact
evidence path. Return: summary; strengths; fatal weaknesses; required revisions;
likely reviewer score; questions the paper must answer.

## Standing context for every review
Canonical: `docs/PROJECT.md` (status/design), `docs/paper_fact_sheet.md` (authoritative
numbers), `docs/risks.md` (28 incidents), `docs/labeling_protocol.md`,
`results/claims_matrix_2026-08-20.csv`. Operational index: `.ai/CURRENT_STATE.md`.
Prior experiments: `.ai/EXPERIMENTS.md`. Evidence grades: `.ai/FINDINGS.md`.
Agent agreement is not evidence; committed experiments and blinded results are.
