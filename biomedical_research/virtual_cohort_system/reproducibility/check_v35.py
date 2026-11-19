"""Check the three v0.35 typeset result tables against the saved experiment aggregates."""
from pathlib import Path
import json
import re

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "manuscript/kdd_draft_v35_2026-11-19"
WORK = ROOT / "work"


def numeric_cells(tex, label):
    """Read numeric cells (including ranges) in the named manuscript table."""
    start = tex.index(r"\label{" + label + "}")
    body = tex[start:tex.index(r"\end{tabular}", start)]
    rows = []
    for line in body.splitlines():
        if "&" not in line or not line.rstrip().endswith(r"\\"):
            continue
        cells = line.split("&")[1:]
        numbers = []
        for cell in cells:
            cell = cell.replace(r"\textbf{", "").replace("}", "").replace("--", " ")
            numbers.extend(float(x) for x in re.findall(r"(?<![A-Za-z])(?:\d+\.\d+|\.\d+|\d+)(?![A-Za-z])", cell))
        if numbers:
            rows.append(numbers)
    return rows


def compare_rows(got, expected, precisions):
    assert len(got) == len(expected) == len(precisions)
    for row, truth, decimals in zip(got, expected, precisions):
        assert len(row) == len(truth)
        np.testing.assert_allclose(row, truth, atol=0.5 * 10**(-decimals) + 1e-11, rtol=0)


def main():
    main_tex = (PAPER / "main.tex").read_text(encoding="utf-8")
    appendix = (PAPER / "appendix.tex").read_text(encoding="utf-8")

    three_arms = []
    for case, keys in [
        ("pns", ["residual_correlation", "bmi_sbp", "bmi_dbp"]),
        ("iron", ["odds_ratio", "joint_prevalence", "spearman"]),
    ]:
        draws = pd.read_csv(WORK / f"{case}_evidence_content_control_2026-11-16/analysis/seed_results.csv")
        for key in keys:
            d = draws[draws.estimand == key]
            cells = d.groupby(["arm", "id"]).absolute_reference_difference
            assert d.id.nunique() == 9 and cells.size().eq(3).all()
            values = cells.mean().groupby(level="arm").mean()
            scale = 100 if key == "joint_prevalence" else 1
            three_arms.append((scale * values[["BASE", "SUMMARY", "JOINT"]]).to_list())
    compare_rows(numeric_cells(main_tex, "tab:evidence"), three_arms, [4] * 6)

    original = pd.read_csv(WORK / "original_paper_capability_2026-11-17/analysis/author_results.csv")
    assert len(original) == 33 and original.available_seeds.eq(3).all()
    keys = ["bmi_sbp", "bmi_dbp", "residual_correlation", "sbp.sd_population", "dbp.sd_population",
            "sbp_below_dbp_fraction", "odds_ratio", "joint_prevalence", "spearman",
            "low_hb_fraction", "low_ferritin_fraction"]
    profile = []
    for key in keys:
        rows = original[original.estimand == key].sort_values("episode_id")
        assert len(rows) == 3 and rows.reference.nunique() == 1
        scale = 100 if key.endswith("fraction") or key == "joint_prevalence" else 1
        profile.append([v * scale for v in [*rows.seed_mean, rows.reference.iloc[0]]])
    # The header contains the alphanumeric author labels A1--A3, not scientific estimates.
    compare_rows(numeric_cells(appendix, "tab:profile"), profile, [3, 3, 3, 2, 2, 3, 3, 3, 3, 3, 3])

    matched = pd.read_csv(WORK / "matched_size_utility_2026-11-17/CONTRAST_SUMMARIES.csv")
    summaries = []
    for trait in ["bmi", "total_cholesterol", "hdl_cholesterol"]:
        for contrast in ["rural_minus_pastoralist", "urban_minus_pastoralist", "urban_minus_rural"]:
            rows = matched[(matched.trait == trait) & (matched.contrast == contrast)]
            assert len(rows) == 7 and rows.absolute_n.eq(500).all()
            real = rows[rows.comparison == "real_real"].absolute_mean
            virtual = rows[rows.comparison == "virtual_real"].absolute_mean
            assert len(real) == 1 and len(virtual) == 6
            summaries.append([real.item(), virtual.min(), virtual.max()])
    compare_rows(numeric_cells(appendix, "tab:lifestyle"), summaries, [3] * 9)

    path = WORK / "prospective_bp_freetown_2026-11-18"
    laws = json.loads((path / "MODEL_AUDIT.json").read_text(encoding="utf-8"))["population"]
    outcome = json.loads((path / "AGGREGATES.json").read_text(encoding="utf-8"))
    target = outcome["target"]
    for arm in ["primary", "alternative"]:
        assert f"{100 * laws[arm]['Q2']:.4f}" + r"\%" in main_tex
    assert f"{100 * target['estimates']['Q2']:.2f}" + r"\%" in main_tex
    assert not outcome["scenarios"]["material_by_frozen_rule"]
    assert f"{100 * outcome['scenarios']['Q2_gap_minus_mc_allowance']:.2f} points" in main_tex
    assert target["n"] == 1244 and target["both_n"] == 550
    assert "694 met neither" in main_tex

    counts = {"evidence_conditions": 18, "original_paper_estimates": 44,
              "matched_size_estimates": 27, "prospective_rule_passed": False}
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
