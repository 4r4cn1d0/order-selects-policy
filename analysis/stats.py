#!/usr/bin/env python3
"""
Statistical analysis of aggregated judge verdicts (results/aggregated_per_scenario.csv,
results/aggregated_per_run.csv -- run analysis/aggregate_results.py first).

Primary statistic: cluster-robust logistic regression of is_value_A ~ C(condition) on the
per-scenario grain, with standard errors clustered by seed (accounts for repeated
measures within a replicate without requiring a full crossed-random-effects mixed model --
see docs/PROJECT.md (legacy-pipeline note) for why this is the practical default and
docs/risks.md for the documented extension to a full mixed model).

Secondary/robustness statistic: a permutation test on run-level value_A_rate, comparing
value_first vs. behavior_first (the core path-dependence contrast) with condition labels
shuffled across runs (~10,000 iterations, no distributional assumptions).

Pairwise condition contrasts are Holm-Bonferroni corrected. Effect sizes are reported as
percentage-point differences in value_A_rate with bootstrap 95% CIs.

Usage:
    python analysis/stats.py
    python analysis/stats.py --axis axis1_access_vs_provenance --min-effect 0.15
"""
import argparse
import itertools
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"

RNG = np.random.default_rng(0)


def holm_bonferroni(pvals: list[float]) -> list[float]:
    order = np.argsort(pvals)
    m = len(pvals)
    adjusted = np.empty(m)
    running_max = 0.0
    for rank, idx in enumerate(order):
        val = min(1.0, (m - rank) * pvals[idx])
        running_max = max(running_max, val)
        adjusted[idx] = running_max
    return adjusted.tolist()


def cluster_robust_logit(per_scenario: pd.DataFrame, axis: str) -> pd.DataFrame:
    sub = per_scenario[per_scenario["axis"] == axis].copy()
    if sub["condition"].nunique() < 2 or sub["is_value_A"].nunique() < 2:
        print(f"[{axis}] insufficient variation for cluster-robust logit (need >=2 conditions "
              f"and both outcome classes present); skipping.")
        return pd.DataFrame()

    sub["condition"] = pd.Categorical(sub["condition"],
                                       categories=["behavior_first", "value_first", "interleaved",
                                                    "conflicting_value"])
    model = smf.glm("is_value_A ~ C(condition)", data=sub, family=sm.families.Binomial())
    try:
        result = model.fit(cov_type="cluster", cov_kwds={"groups": sub["seed"]})
    except np.linalg.LinAlgError:
        # Small/sparse-outcome samples (few seeds, few OOD scenarios -- see docs/risks.md #9)
        # can produce a singular Hessian at the fitted params (near-perfect separation).
        # Don't let this take down the whole analysis run -- the permutation test below is
        # the documented robustness check for exactly this situation.
        print(f"[{axis}] cluster-robust logit fit failed (singular Hessian -- likely too few "
              f"seeds/scenarios or a near-separated outcome at this sample size); skipping. "
              f"See the permutation-test section below for the robustness-check statistic.")
        return pd.DataFrame()
    print(f"\n[{axis}] cluster-robust logistic regression (is_value_A ~ condition, "
          f"SE clustered by seed):")
    print(result.summary())
    return result.params.to_frame("coef").join(result.pvalues.to_frame("pvalue"))


def bootstrap_ci(rates: np.ndarray, n_boot: int = 5000) -> tuple[float, float]:
    if len(rates) == 0:
        return (float("nan"), float("nan"))
    boots = [RNG.choice(rates, size=len(rates), replace=True).mean() for _ in range(n_boot)]
    return (float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5)))


def permutation_test(per_run: pd.DataFrame, axis: str, cond_a: str, cond_b: str,
                      n_perm: int = 10000) -> dict:
    sub = per_run[(per_run["axis"] == axis) & (per_run["condition"].isin([cond_a, cond_b]))]
    a_rates = sub[sub["condition"] == cond_a]["value_A_rate"].values
    b_rates = sub[sub["condition"] == cond_b]["value_A_rate"].values
    if len(a_rates) == 0 or len(b_rates) == 0:
        return {"axis": axis, "cond_a": cond_a, "cond_b": cond_b, "mean_a": None, "mean_b": None,
                "observed_diff_pp": None, "p_value": None, "ci_a_95": None, "ci_b_95": None,
                "n_a": len(a_rates), "n_b": len(b_rates)}

    observed_diff = a_rates.mean() - b_rates.mean()
    pooled = np.concatenate([a_rates, b_rates])
    n_a, n_b = len(a_rates), len(b_rates)
    count = 0
    for _ in range(n_perm):
        RNG.shuffle(pooled)
        perm_diff = pooled[:n_a].mean() - pooled[n_a:].mean()
        if abs(perm_diff) >= abs(observed_diff):
            count += 1
    p_value = count / n_perm
    ci_a = bootstrap_ci(a_rates)
    ci_b = bootstrap_ci(b_rates)
    return {"axis": axis, "cond_a": cond_a, "cond_b": cond_b,
            "mean_a": float(a_rates.mean()), "mean_b": float(b_rates.mean()),
            "observed_diff_pp": round(observed_diff * 100, 1), "p_value": round(p_value, 4),
            "ci_a_95": tuple(round(x, 3) for x in ci_a), "ci_b_95": tuple(round(x, 3) for x in ci_b),
            "n_a": n_a, "n_b": n_b}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--axis", type=str, default=None, help="restrict to one axis (default: all present)")
    ap.add_argument("--min-effect", type=float, default=0.15,
                     help="pre-registered minimum meaningful effect (percentage points / 100) for "
                          "value_first vs behavior_first; below this, treat a null result as "
                          "inconclusive rather than disconfirming (low power at laptop scale)")
    args = ap.parse_args()

    per_scenario_path = RESULTS_DIR / "aggregated_per_scenario.csv"
    per_run_path = RESULTS_DIR / "aggregated_per_run.csv"
    if not per_scenario_path.exists() or not per_run_path.exists():
        raise SystemExit("Run analysis/aggregate_results.py first.")

    per_scenario = pd.read_csv(per_scenario_path)
    per_run = pd.read_csv(per_run_path)

    axes = [args.axis] if args.axis else sorted(per_scenario["axis"].unique())

    print("=" * 70)
    print("PRIMARY: cluster-robust logistic regression (per-scenario grain)")
    print("=" * 70)
    for axis in axes:
        cluster_robust_logit(per_scenario, axis)

    print("\n" + "=" * 70)
    print("SECONDARY: permutation test on run-level value_A_rate (Holm-Bonferroni corrected)")
    print("=" * 70)
    conditions = ["value_first", "behavior_first", "interleaved", "conflicting_value"]
    all_results = []
    for axis in axes:
        pairs = list(itertools.combinations(conditions, 2))
        pair_results = [permutation_test(per_run, axis, a, b) for a, b in pairs]
        pvals = [r["p_value"] for r in pair_results if r["p_value"] is not None]
        adjusted = holm_bonferroni(pvals) if pvals else []
        adj_iter = iter(adjusted)
        for r in pair_results:
            if r["p_value"] is not None:
                r["p_value_holm"] = round(next(adj_iter), 4)
            all_results.append(r)

    results_df = pd.DataFrame(all_results)
    print(results_df.to_string(index=False))
    out_path = RESULTS_DIR / "stats_pairwise.csv"
    results_df.to_csv(out_path, index=False)
    print(f"\nWrote pairwise comparisons -> {out_path}")

    print("\n" + "=" * 70)
    print(f"PRIMARY CONTRAST: value_first vs behavior_first (pre-registered min effect: "
          f"{args.min_effect * 100:.0f}pp)")
    print("=" * 70)
    for axis in axes:
        row = results_df[(results_df["axis"] == axis) & (results_df["cond_a"] == "value_first") &
                          (results_df["cond_b"] == "behavior_first")]
        if row.empty or pd.isna(row.iloc[0]["observed_diff_pp"]):
            print(f"[{axis}] insufficient data for primary contrast.")
            continue
        diff_pp = row.iloc[0]["observed_diff_pp"]
        verdict = ("EVIDENCE OF PATH-DEPENDENCE" if abs(diff_pp) / 100 >= args.min_effect
                   else "INCONCLUSIVE (below pre-registered minimum effect -- not disconfirming, "
                        "likely underpowered at this scale)")
        print(f"[{axis}] value_first - behavior_first = {diff_pp:+.1f}pp "
              f"(Holm-corrected p={row.iloc[0]['p_value_holm']}) -> {verdict}")


if __name__ == "__main__":
    main()
