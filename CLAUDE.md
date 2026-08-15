# CLAUDE.md

Working agreements for this repo. Part general coding discipline, part hard-won
methodology specific to this project — the second half matters more here than the first.

## General coding principles

Adapted from the widely-circulated "Karpathy-inspired" CLAUDE.md
(github.com/multica-ai/andrej-karpathy-skills — derived from Andrej Karpathy's public
observations on LLM coding pitfalls; not authored by him).

**Think before coding.** State assumptions explicitly. If a request is ambiguous, present
the interpretations rather than silently picking one. Push back when a simpler approach
exists.

**Simplicity first.** Minimum code that solves the stated problem. Nothing speculative —
no unrequested features, no premature abstractions, no defensive error handling for
conditions that can't occur.

**Surgical changes.** Touch only what the task requires. Don't "improve" adjacent code,
comments, or formatting. Match the existing style. Only delete code your own change made
obsolete.

**Goal-driven execution.** Define a verifiable success criterion before implementing.
Turn "add validation" into "write tests for invalid inputs, then make them pass."

## Research methodology (project-specific — read this part)

This is an empirical ML research repo, not a product. The failure mode that matters here
isn't a bug that crashes; it's a **measurement that quietly lies**. Five separate
instruments in this project produced confidently wrong numbers before being caught. See
`docs/risks.md` — it is the single most important file in the repo.

**Never trust an aggregate score you haven't spot-checked against raw output.** Every
scorer failure in this project (`docs/risks.md` #16, #17, #18) was found by reading actual
model completions, and every one of them was invisible in the summary statistic. Before
citing any number: read a sample of the underlying generations.

**Verify external claims before acting on them.** Citations, arXiv IDs, deadlines, API
behavior. One paper cited in review had a title that didn't match its arXiv ID; one
"related work" turned out to test something entirely different. Fetch and check.

**Distinguish "the pipeline ran" from "the study is complete."** These are different
claims and should never be blurred. Say which one is true.

**A null result is only informative if the intervention was real.** This project spent
significant time on a null that turned out to be an artifact of a broken intervention
(value documents trained with a different objective than behavior demos —
`docs/risks.md` #20-22). Before concluding "X has no effect," confirm X was independently
capable of having one.

**Report per-seed, not just means.** Small-n aggregates hide everything. List every seed.

**Don't patch a heuristic scorer by reading the exact examples it's scoring.** That fits
the heuristic to the test set. Prefer direct labeling; see `docs/labeling_protocol.md`.

**Label blind.** Metadata (condition, seed, checkpoint) must be stripped before labeling —
`scripts/blind_label_export.py`. Unblinded reading is for debugging, never for a number
that goes in the paper.

## Repo conventions

- **Checkpoints are namespaced by base model** (`train/model_utils.py:resolve_run_dir_name`).
  A missing namespace silently overwrote a checkpoint once (`docs/risks.md` #15). Don't
  bypass it.
- **Curriculum order is the independent variable.** `DataLoader(shuffle=False)` over
  `CurriculumDataset` is deliberate; `train/train.py` asserts `step_position` order. Never
  introduce reshuffling.
- **Phase sizes must be multiples of 16** (`per_device_batch_size` × `gradient_accumulation_steps`).
  A phase boundary inside a gradient-accumulation window isn't a real intervention.
- **Use `--lr-scheduler constant --warmup-ratio 0.0` for order experiments.** Cosine decay
  confounds "order effect" with "which phase got larger updates."
- Old negative-result curricula, checkpoints, and results are **kept, not deleted** — they
  document why the design changed.
