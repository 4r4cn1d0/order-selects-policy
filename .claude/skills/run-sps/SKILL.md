---
name: run-sps
description: Run, smoke-test, train, and interact with the SPS path-dependent-values ML pipeline — build curricula, train LoRA checkpoints on pythia-410m, generate completions from trained checkpoints, run the eval/blind-labeling flow.
---

# Run SPS (path-dependent values pipeline)

Python ML research pipeline: fine-tunes `EleutherAI/pythia-410m-deduped` (LoRA, MPS/CPU)
on ordered curricula and measures which "value" the model generalizes to on held-out
scenarios. There is no server or GUI — the interactive surface is **trained checkpoints
you generate text from**. The driver at `.claude/skills/run-sps/driver.py` wraps both an
end-to-end smoke and that generation surface.

All paths below are relative to the repo root. Always use the project venv
(`.venv/bin/python`) — never the system Python (3.9, incompatible; see Gotchas).

## Prerequisites

- Python ≥3.11 venv at `.venv` with the project installed (`pip install -e .` per
  README). Verify it's healthy:

```bash
.venv/bin/python --version   # 3.11.x
.venv/bin/pip check          # "No broken requirements found."
```

- First-ever training/generation run downloads pythia-410m (~1.6GB) from HuggingFace —
  needs network; unauthenticated works (a rate-limit warning is printed, harmless).

## Run (agent path)

**Smoke — full pipeline in ~1–2 min** (builds a real 24-record curriculum, trains a real
2-step LoRA adapter into a temp dir, reloads it, generates). Never touches
`checkpoints/` or leaves files in `curricula/`:

```bash
.venv/bin/python .claude/skills/run-sps/driver.py smoke
```

Success ends with `SMOKE OK: build -> train -> checkpoint -> load -> generate all
worked.` The printed completion from a 2-step adapter is *expected to be incoherent* —
the smoke verifies pipeline function, not model quality.

**Generate from any trained checkpoint** (the real interaction surface — `ls
checkpoints/` for available run names; `--stage` picks `final` / `phase_boundary` /
`boundary_1` / `boundary_2` where they exist):

```bash
.venv/bin/python .claude/skills/run-sps/driver.py gen \
  --run-name axis1_access_vs_provenance_value-B_pool_b_only_seed1001 \
  --prompt "A journalist on deadline asks for material whose donation history is contested. Respond as Iris."
```

A well-trained provenance checkpoint answers with a hold-until-verified decision; an
access checkpoint with a release-now decision.

## The real experiment pipeline

Each stage is a script; these exact forms are in active use (order-experiment shape):

```bash
# build one order-experiment curriculum (phase sizes must be multiples of 16)
.venv/bin/python scripts/build_order_experiment_curriculum.py --seed 3001 --order A_first --phase-size 192

# train it — the three flags are mandatory for order experiments (see Gotchas)
.venv/bin/python train/train.py \
  --curriculum curricula/axis1_access_vs_provenance_value-conflict_orderexp_A_first_seed3001.jsonl \
  --lr-scheduler constant --warmup-ratio 0.0 --epochs 1 --lora-init-seed 3001

# generate held-out completions at every phase-boundary checkpoint
.venv/bin/python scripts/generate_order_experiment.py --seeds 3001 --battery dev

# blind-label: export (strips condition/seed metadata), label the CSV, then join+score
.venv/bin/python scripts/blind_label_export.py --batch-name mybatch \
  --generations results/generations/orderexp_dev_seeds-3001.jsonl
.venv/bin/python scripts/blind_label_join.py --batch-name mybatch
```

Smaller control curricula: `scripts/build_gate3_curriculum.py` (see its `--help`;
`--value-docs none --demo-set A|B --demo-source positive_control|value_explanation`).

## Test

```bash
.venv/bin/python scripts/validate_confound.py   # exits 0, "Confound-validity gate PASSED"
```

## Gotchas (each of these caused a real incident)

- **`epochs: 4` is the config default and silently repeats the whole curriculum per
  epoch** — an `A→B→C` ordered curriculum becomes `A B C A B C …`, destroying the order
  manipulation. Any curriculum-order run must pass `--epochs 1` and size phases for
  one-pass exposure instead (≈192 records/phase converges; 32/phase is degenerate).
- **Cosine LR (default) confounds order with update magnitude** — early phases get
  bigger updates. Order experiments must pass `--lr-scheduler constant --warmup-ratio 0.0`.
- **Don't generate while training on MPS.** Concurrent model loads cause memory-pressure
  slowdowns (documented 24× slowdown incident, `docs/risks.md` #14). Run sequentially.
- **Phase sizes must be multiples of 16** (batch 4 × grad-accum 4), or a phase boundary
  splits a gradient-accumulation window. The order-experiment builder errors on
  violations; don't work around it.
- **Checkpoints are namespaced by base model** (`__model-<slug>` suffix for non-default
  `--base-model`). Bypassing this once silently overwrote a checkpoint
  (`docs/risks.md` #15).
- Training/generation logs are noisy — filter with
  `grep -v "Warning\|deprecated\|Loading weights"`. The `torch_dtype` deprecation
  warning is harmless.
- Never label generations unblinded; use the export/join scripts
  (`docs/labeling_protocol.md`). Read `CLAUDE.md` and `docs/risks.md` before changing
  the pipeline — most "obvious" simplifications recreate a documented incident.

## Troubleshooting

- `No checkpoint found at checkpoints/<name>/<stage>` — that run/stage combo doesn't
  exist; `ls checkpoints/<name>/` shows which stages were saved (`phase_boundary` only
  for single-transition conditions, `boundary_1`/`boundary_2` for 3-phase ones).
- Trained-model output degenerate (word salad, prompt echo) — undertrained, not broken:
  too few optimizer steps for one-pass training. Increase `--phase-size` / record count
  (36+ optimizer steps ≈ converged; 18 was degenerate).
- `transformers`/`peft` import errors — you used system Python (3.9). Use
  `.venv/bin/python` (`docs/risks.md` #8).
