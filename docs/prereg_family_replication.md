# Pre-registration: cross-family replication of the order effect

**Status: DRAFT — locks at the moment the first replication training run starts.**
Any deviation after lock gets logged in `docs/risks.md`, not silently absorbed.
Registered before any replication run, generation, or label exists (repo convention:
see the n=10 prereg commit for the primary matrix).

## Motivation

The primary result (pythia-410m-deduped, n=10, locked battery v1) shows a
curriculum-order effect on endpoint value policy that persists through a neutral
washout phase. This replication asks one question: **does the effect depend on the
model family, or is it a general property of small-LM curriculum training?**
User-directed scope: at least 3 additional families.

## Panel (verified ungated on HF, 2026-08-17)

| Family | Model ID | Arch | Params |
|---|---|---|---|
| Qwen2.5 | `Qwen/Qwen2.5-1.5B` | Qwen2ForCausalLM | 1.5B |
| SmolLM2 | `HuggingFaceTB/SmolLM2-1.7B` | LlamaForCausalLM | 1.7B |
| OLMo-2 | `allenai/OLMo-2-0425-1B` | Olmo2ForCausalLM | 1B |

Base (non-instruct) variants only, matching the primary design. pythia-410m remains
the primary confirmatory result; these are robustness replications. **Family and
size co-vary in this panel — it is a robustness panel, not a controlled scale
comparison, and will be reported as such.**

## Design invariants (identical to primary matrix)

- Same curricula JSONL files, same locked test battery v1 (SHA in `docs/risks.md`),
  same decoding parameters, same 4-way label rubric.
- Same judge (claude-sonnet-5, same prompt, forced tool call, condition-blind).
- LoRA config identical; target modules resolved per-arch by
  `train/model_utils.py:resolve_target_modules` (llama_style for all three).
- `--lr-scheduler constant --warmup-ratio 0.0`; phase sizes unchanged
  (multiples of 16).
- **Seeds 3001–3005** (n=5 per family), 3 conditions (A_first, B_first,
  interleaved), checkpoints at every phase boundary. 15 runs/family, 45 total.
- All replication compute on one backend: RunPod CUDA fp32, training AND
  generation. No family's numbers mix backends.
- Generation volume per family: 24 items × (10 sequential runs × 3 stages +
  5 interleaved runs × 2 stages) = 960 completions. Judge cost ≈ $2.2/family.

## Gates (checked per family, in order, before any order claim)

- **G1 — equipotence:** at `post_phase1`, mean S in the trained direction must
  reach |S| ≥ 0.8 for BOTH the A-first arm (access phase 1) and the B-first arm
  (provenance phase 1). Fail → one pre-registered contingency: LR sweep at 0.5×
  and 2× default on the phase-1-only configuration, re-gate at the best LR (chosen
  on post_phase1 S only, before seeing any later-stage data). Still fail → the
  family is reported as an equipotence failure; no order comparison is run or
  reported for it.
- **G2 — judge transfer:** before unblinding any statistic for a family, 30
  randomly sampled completions are read blind by the annotator. Judge–reader
  disagreement > 20% on decisive labels → stop, revalidate the judge on that
  family's output style before proceeding.
- Raw-completion reading precedes trust in any aggregate, per CLAUDE.md.

## Pre-registered predictions and analysis

- **Primary endpoint (per family):** sign of the paired per-seed difference
  (A_first − B_first) in endpoint S at `post_washout`.
  **Prediction: negative** (endpoint tilts toward the more recently trained
  conflict value), matching the primary result (−0.419 mean, 9/10 seeds).
- Per-family test: Wilcoxon signed-rank on the 5 paired differences (one-sided).
  n=5 is explicitly a *directional replication*, not a standalone confirmation:
  minimum attainable one-sided sign p is 0.031 (5/5).
- **Cross-family claim:** count of families (including pythia) whose mean paired
  difference is negative, reported as a replication tally with exact binomial
  probability under a null of sign-symmetry. This tally, not any single family's
  p-value, is the replication headline.
- Secondary (descriptive, no test): pre-washout recency reversal magnitude;
  coherence rate by stage; interleaved fragmentation pattern.
- **Extension rule:** seeds 3006–3010 may be added per family ONLY if that
  decision is made before unblinding any statistic of any family (budget
  permitting). Decided-and-recorded here at lock time, or not at all.

## Explicitly out of scope

- No per-family battery edits, judge-prompt edits, or curriculum edits.
- No instruct-tuned variants.
- No claim that any family "shows values better" — coherence rates are reported
  as observed, and a more coherent family widens the decisive denominator, which
  is a measurement property, not an effect size.
