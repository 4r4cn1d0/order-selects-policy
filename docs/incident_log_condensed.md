# Incident log, condensed (for main-text subsection; full log: docs/risks.md)

| # | Instrument failure | Caught by | Consequence |
|---|---|---|---|
| 3/4 | 160M base model unstable under LoRA r=8 | Phase-0 gate | model/rank changed BEFORE any experiment |
| 15 | checkpoint overwrite across base models | corrupted pilot | run-dir namespacing by model |
| 16–18 | three scorer generations (keyword, letter-choice, loglik) each biased | reading raw completions | scorer replaced by blinded judge + validation |
| 19–22 | value-docs trained with mismatched objective -> fake order-null | external review + code audit | intervention redesigned; null retained as methods finding |
| 27 | judge runner lost 1,477 paid labels on billing stop | crash | per-row persistence + resume |
| 28 | E1 washout was form-polar -> confounded endpoint | pool inspection post-scoring | E1' form-neutral rerun |
| E5/E7 | likelihood proxy r=0.76; probe direction beaten by shuffled-label null | pre-registered gates | both gated out of the paper |

Pattern: every failure was invisible in its aggregate statistic and caught by
inspecting raw artifacts or by a pre-registered control. This is the paper's
core methodological claim in practice.
