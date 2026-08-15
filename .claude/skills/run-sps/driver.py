#!/usr/bin/env python3
"""
Agent driver for the SPS (path-dependent values) pipeline.

Two subcommands:

  smoke               End-to-end pipeline exercise at tiny scale: builds a real
                      curriculum via scripts/build_gate3_curriculum.py, trains a real
                      LoRA adapter on pythia-410m for 2 optimizer steps (checkpoints go
                      to a temp dir -- never touches checkpoints/), loads the adapter
                      back, generates one completion, prints it. ~1-2 min on MPS with
                      the base model already cached; first run downloads ~1.6GB from HF.

  gen                 Load any trained checkpoint under checkpoints/ and generate a
                      completion for a prompt. This is the primary way to interact with
                      the project's actual product (trained value-policies).
                      e.g.: gen --run-name axis1_access_vs_provenance_value-A_pool_a_only_seed1001 \
                                --prompt "A patron requests an item whose origin is disputed. Respond as Iris."

Run with the project venv: .venv/bin/python .claude/skills/run-sps/driver.py <cmd> ...
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # <repo>/.claude/skills/run-sps/ -> <repo>
sys.path.insert(0, str(ROOT / "train"))
sys.path.insert(0, str(ROOT / "eval"))

SMOKE_SEED = 9999  # never used by any real experiment (real seeds: 1001-1005, 2001-2002, 3001-3003)
SMOKE_LABEL = "driver_smoke"
DEFAULT_PROMPT = ("A patron requests an item whose origin is currently disputed by two "
                   "claimants. Respond as Iris.")


def run(cmd, **kw):
    print(f"+ {' '.join(str(c) for c in cmd)}")
    subprocess.run(cmd, check=True, cwd=ROOT, **kw)


def generate_from_adapter(ckpt_dir: Path, prompt: str) -> str:
    """Load base model + a LoRA adapter from an arbitrary path and generate once.
    Local loader (rather than eval/ood_eval.load_checkpoint_model) because that helper
    is hardwired to checkpoints/ and the smoke trains into a temp dir."""
    from peft import PeftModel
    from model_utils import load_base_model_and_tokenizer, load_default_config, resolve_device
    from ood_eval import generate_batch

    cfg = load_default_config()
    device = resolve_device(cfg["device"])
    base, tokenizer = load_base_model_and_tokenizer(cfg["base_model"]["name"], device, cfg["dtype"])
    model = PeftModel.from_pretrained(base, str(ckpt_dir)).to(device)
    return generate_batch(model, tokenizer, [prompt], device, max_new_tokens=60)[0]


def cmd_smoke(_args):
    py = sys.executable
    tmp = Path(tempfile.mkdtemp(prefix="sps_smoke_"))
    curriculum_name = f"axis1_access_vs_provenance_value-A_{SMOKE_LABEL}_seed{SMOKE_SEED}.jsonl"
    built = ROOT / "curricula" / curriculum_name
    moved = tmp / curriculum_name
    try:
        # 1. Build a real (tiny) curriculum with the project's own builder, then move it
        #    out of curricula/ so smoke artifacts never pollute the committed dir.
        run([py, "scripts/build_gate3_curriculum.py", "--seed", str(SMOKE_SEED),
             "--value-docs", "none", "--demo-set", "A", "--demo-repeat", "1",
             "--label", SMOKE_LABEL])
        shutil.move(built, moved)

        # 2. Real LoRA training, 2 optimizer steps, temp output dirs.
        run([py, "train/train.py", "--curriculum", str(moved), "--max-steps", "2",
             "--lora-init-seed", str(SMOKE_SEED),
             "--output-dir", str(tmp / "ckpt"), "--log-dir", str(tmp / "logs")])

        # 3. Load the freshly trained adapter and generate.
        run_dir = f"axis1_access_vs_provenance_value-A_{SMOKE_LABEL}_seed{SMOKE_SEED}"
        completion = generate_from_adapter(tmp / "ckpt" / run_dir / "final", DEFAULT_PROMPT)
        print("\n=== SMOKE COMPLETION (2-step adapter; coherence NOT expected, "
              "pipeline function is) ===")
        print(completion)
        print("\nSMOKE OK: build -> train -> checkpoint -> load -> generate all worked.")
    finally:
        built.unlink(missing_ok=True)
        shutil.rmtree(tmp, ignore_errors=True)


def cmd_gen(args):
    from model_utils import load_default_config
    from ood_eval import load_checkpoint_model, generate_batch

    cfg = load_default_config()
    model, tokenizer, device = load_checkpoint_model(args.run_name, cfg, None, args.stage)
    out = generate_batch(model, tokenizer, [args.prompt], device, max_new_tokens=args.max_new_tokens)[0]
    print(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("smoke")
    g = sub.add_parser("gen")
    g.add_argument("--run-name", required=True,
                   help="a directory name under checkpoints/, e.g. "
                        "axis1_access_vs_provenance_value-A_pool_a_only_seed1001")
    g.add_argument("--stage", default="final",
                   help="final | phase_boundary | boundary_1 | boundary_2 (whichever exists)")
    g.add_argument("--prompt", default=DEFAULT_PROMPT)
    g.add_argument("--max-new-tokens", type=int, default=60)
    args = ap.parse_args()
    {"smoke": cmd_smoke, "gen": cmd_gen}[args.cmd](args)


if __name__ == "__main__":
    main()
