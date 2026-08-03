#!/usr/bin/env python3
"""
Orchestrates generate -> score for one or all trained checkpoints.

By default, scores with the cheap keyword_fallback (no API key needed). Pass --judge llm
to use the Claude API judge (eval/judge.py) instead -- the primary instrument for final
reported numbers, but costs money and requires ANTHROPIC_API_KEY.

Usage:
    python eval/run_eval.py --run-name axis1_access_vs_provenance_value-A_value_first_seed1001
    python eval/run_eval.py --all --judge keyword
    python eval/run_eval.py --all --judge llm
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-name", type=str, default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--judge", choices=["keyword", "llm"], default="keyword")
    ap.add_argument("--skip-generation", action="store_true",
                     help="scoring only, assumes results/generations/*.jsonl already exist")
    args = ap.parse_args()

    if not args.run_name and not args.all:
        raise SystemExit("must pass --run-name <name> or --all")

    target = ["--all"] if args.all else ["--run-name", args.run_name]

    if not args.skip_generation:
        run(["python", str(ROOT / "eval" / "ood_eval.py"), *target])

    scorer = "judge.py" if args.judge == "llm" else "keyword_fallback.py"
    run(["python", str(ROOT / "eval" / scorer), *target])

    run(["python", str(ROOT / "analysis" / "aggregate_results.py")])


def run(cmd: list[str]):
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
