"""Replay the v0.34 numerical checks and describe source and resampling comparators.

Run with python -B reproducibility/check_v34.py. Uses public aggregates and the
existing estimator fixture. No Agent sessions or measured or generated cohort files.
"""

import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import pandas as pd


WORK = Path(__file__).resolve().parents[1] / "work"
PAPER = WORK / "original_paper_capability_2026-11-17"
LIFESTYLE = WORK / "matched_size_utility_2026-11-17"


def source_comparators():
    """Direct calculations describe the anchor population under its own adjustment set."""
    audit_path = PAPER / "audit/SOURCE_DERIVATION_RECHECK.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    a, b, c, d = audit["iron_collapsed_cells"]
    direct = {
        "bmi_sbp": audit["bmi_sbp_per5_fully_adjusted_source"],
        "bmi_dbp": audit["bmi_dbp_per5_fully_adjusted_source"],
        "residual_correlation": audit["source_partial_r_age_bmi"],
        "odds_ratio": (a * d) / (b * c),
        "joint_prevalence": a / (a + b + c + d),
        "spearman": None,  # The four threshold cells do not identify continuous ranks.
    }
    seed_results = pd.read_csv(PAPER / "analysis/seed_results.csv")
    output = {}
    for estimand, source in direct.items():
        rows = seed_results.loc[seed_results.estimand == estimand]
        assert len(rows) == 9 and rows.status.eq("computed").all()
        assert rows.groupby("episode_id").size().eq(3).all()
        assert rows.reference.nunique() == 1
        means = rows.groupby("episode_id").value.mean()
        output[estimand] = {
            "anchor_source_value": source,
            "mean_of_three_draws_by_constructor": means.to_dict(),
            "measured_sample_reference": float(rows.reference.iloc[0]),
        }
    return output


def matched_profiles():
    """Keep signed displacement and within-table estimator SD alongside paired MAE."""
    estimates = pd.read_csv(LIFESTYLE / "ESTIMATES.csv")
    differences = pd.read_csv(LIFESTYLE / "DIFFERENCES.csv")
    contrasts = ["rural_minus_pastoralist", "urban_minus_pastoralist", "urban_minus_rural"]
    keys = ["trait", "replicate", "stream", "contrast"]
    assert len(estimates) == 12000 and estimates.status.eq("computed").all()
    assert len(differences) == 31500 and differences.status.eq("computed").all()
    values = estimates.melt(id_vars=["trait", "replicate", "stream"], value_vars=contrasts,
                            var_name="contrast", value_name="estimate")
    pair_keys = ["trait", "replicate", "contrast"]
    real_b = values.loc[values.stream == "R_B", pair_keys + ["estimate"]]
    real_b = real_b.rename(columns={"estimate": "real_b"})
    pairs = values.loc[values.stream != "R_B"].merge(real_b, on=pair_keys, validate="many_to_one")
    checked = pairs.merge(differences[keys + ["difference"]], on=keys, validate="one_to_one")
    assert len(checked) == len(pairs) == len(differences)
    np.testing.assert_allclose(checked.estimate - checked.real_b, checked.difference, atol=1e-11)
    checked["absolute"] = checked.difference.abs()
    groups = ["trait", "contrast", "stream"]
    profile = checked.groupby(groups).agg(
        mean_estimate=("estimate", "mean"), estimator_sd=("estimate", "std"),
        signed_difference=("difference", "mean"), mae=("absolute", "mean"),
        repetitions=("replicate", "nunique"),
    )
    assert len(profile) == 63 and profile.repetitions.eq(500).all()
    reference = real_b.groupby(["trait", "contrast"]).real_b.agg(["mean", "std"])
    output = []
    for (trait, contrast), group in profile.groupby(level=["trait", "contrast"], sort=True):
        streams = group.droplevel(["trait", "contrast"])
        tables = streams.drop("R_A")
        assert len(tables) == 6
        limits = {column: [float(tables[column].min()), float(tables[column].max())]
                  for column in ("mean_estimate", "estimator_sd", "signed_difference", "mae")}
        output.append({
            "trait": trait, "contrast": contrast,
            "real_b_mean_estimate": float(reference.loc[(trait, contrast), "mean"]),
            "real_b_estimator_sd": float(reference.loc[(trait, contrast), "std"]),
            "real_real_mae": float(streams.loc["R_A", "mae"]),
            "range_across_six_frozen_tables": limits,
        })
    return output


def main():
    if not __debug__:
        raise SystemExit("The frozen verification uses Python assertions. Run without -O.")
    # Invoke only the existing in-memory fixture. Other paper-adapter tests need local sources.
    subprocess.run(
        [sys.executable, "-B", "-m", "unittest", "test_adapter.Tests.test_two_explicit_analysis_routes"],
        cwd=PAPER, check=True,
    )
    os.environ.setdefault("MPLBACKEND", "Agg")
    sys.path.insert(0, str(WORK / "manuscript_integration_v34_2026-11-18"))
    import verify

    result = {
        "original_paper_checks": verify.check_paper(),
        "matched_size_checks": verify.check_lifestyle(),
        "evidence_control_table_rows": verify.check_controls(),
        "direct_source_comparison": source_comparators(),
        "matched_lifestyle_profiles": matched_profiles(),
    }
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
