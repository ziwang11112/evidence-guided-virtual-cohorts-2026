"""Rebuild the nine reported data-substitution comparisons from frozen estimates.

The optional participant-level check is read-only and needs the original local files.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
APPLICATION = ROOT / "work/lifestyle_application_2026-11-11"
MATCHED = ROOT / "work/matched_size_utility_2026-11-17"
TRAITS = ("bmi", "total_cholesterol", "hdl_cholesterol")
CONTRASTS = ("rural_minus_pastoralist", "urban_minus_pastoralist", "urban_minus_rural")
SEEDS = (64001, 64003, 64007)
AUTHORS = ("LIFESTYLE_A1", "LIFESTYLE_A2")
DATASETS = ["real"] + [f"{a}_s{s}" for a in AUTHORS for s in SEEDS]
KEY = ["dataset_id", "trait", "stratum", "contrast"]
OUT = HERE / "ANALYSIS_SUBSTITUTION.json"


def equal(x, y):
    np.testing.assert_allclose(x, y, atol=1e-9, rtol=1e-10, equal_nan=False)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def aggregates():
    raw = pd.read_csv(APPLICATION / "ANALYSIS_CONTRASTS.csv")
    assert set(raw.dataset_id) == set(DATASETS) and set(raw.status) == {"computed"}
    estimates = raw.set_index(KEY).sort_index()
    expected = pd.MultiIndex.from_product(
        [DATASETS, TRAITS, ["pooled", "F", "M"], CONTRASTS], names=KEY
    ).sort_values()
    assert estimates.index.equals(expected)
    originals = pd.read_csv(MATCHED / "ORIGINAL_ESTIMATES.csv").set_index(
        ["dataset_id", "trait"]
    )
    sizes = pd.read_csv(MATCHED / "CONTRAST_SUMMARIES.csv")
    comparisons = sizes.set_index(["trait", "contrast", "stream"]).sort_index()
    assert originals.index.is_unique and comparisons.index.is_unique
    results = []
    for trait in TRAITS:
        for contrast in CONTRASTS:
            rows = estimates.xs((trait, "pooled", contrast), level=KEY[1:]).loc[DATASETS]
            original = originals.xs(trait, level="trait").loc[DATASETS]
            equal(rows.raw_estimate, original[contrast])
            equal(rows.raw_estimate, rows.estimate * original.sample_sd)
            equal(rows.n, original.n)
            comp = comparisons.loc[(trait, contrast)]
            rr = comp.loc[comp.comparison == "real_real"]
            vr = comp.loc[comp.comparison == "virtual_real"]
            assert len(rr) == 1 and len(vr) == 6
            assert (comp.planned == 500).all() and (comp.unavailable == 0).all()
            real = rows.loc["real"]
            by_author = {}
            for author in AUTHORS:
                draws = rows.loc[[f"{author}_s{s}" for s in SEEDS]]
                by_author[author] = {
                    "raw_mean": float(draws.raw_estimate.mean()),
                    "raw_seed_values": draws.raw_estimate.tolist(),
                    "mean_in_own_sd": float(draws.estimate.mean()),
                    "mean_in_measured_sd": float(draws.raw_estimate.mean() / original.loc["real", "sample_sd"]),
                }
            results.append({
                "trait": trait, "contrast": contrast, "raw_unit": real.raw_unit,
                "measured_n": int(real.n), "measured_raw": float(real.raw_estimate),
                "measured_ols_interval": [float(real.raw_lower), float(real.raw_upper)],
                "measured_within_sample_sd": float(real.estimate),
                "authors": by_author,
                "matched_real_real_abs_discrepancy": float(rr.absolute_mean.iloc[0]),
                "matched_virtual_real_abs_discrepancy_range": [float(vr.absolute_mean.min()), float(vr.absolute_mean.max())],
            })
    return estimates, {
        "scope": "Same-paper Turkana reconstruction. All nine prespecified additive contrasts. Same frozen age- and sex-adjusted operator. Measurement units and OLS uncertainty belong to each trait. Author means summarize three draws per author.",
        "interpretation": "Own-SD and common measured-SD effects are descriptive views of identical raw contrasts. The measured SD is used only by the evaluator. No equivalence margin or synthetic-row significance decision was added.",
        "results": results,
    }


def replay_local(archived):
    bindings = load_json(APPLICATION / "EVALUATION_INPUTS.json")
    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()
    for name, expected in bindings["files"].items():
        assert digest(APPLICATION / name) == expected, name
    inputs = bindings["inputs"]
    assert len(inputs) == len(DATASETS) and {r["dataset_id"] for r in inputs} == set(DATASETS)
    sys.path.insert(0, str(APPLICATION))
    import analysis_operator
    import reference_adapter

    interactions = {r["dataset_id"]: r["analysis"]["interactions"]
                    for r in load_json(APPLICATION / "ANALYSIS_RESULTS.json")["results"]}
    checked = 0
    checked_interactions = 0
    for item in inputs:
        source = Path(item["path"])
        assert digest(source) == item["sha256"], item["dataset_id"]
        if item["kind"] == "real_reference":
            frame, _ = reference_adapter.load_reference(source)
        else:
            frame = pd.read_csv(source, dtype={"id": str})
        actual = analysis_operator.analyze_frame(frame)
        sd_by_trait = {s["trait"]: s["sample_sd"] for s in actual["trait_status"]}
        seen = set()
        for c in actual["contrasts"]:
            key = (item["dataset_id"], c["trait"], c["stratum"], c["contrast"])
            assert key not in seen and c["status"] == "computed"
            seen.add(key)
            row = archived.loc[key]
            for field in ("estimate", "lower", "upper", "se"):
                equal(c[field], row[field])
                equal(c[field] * sd_by_trait[c["trait"]], row["raw_" + field])
            equal(c["n"], row.n)
            assert c["selected_by_paper_rule"] == row.selected_by_paper_rule
            checked += 1
        assert len(seen) == 27
        ref = {z["trait"]: z for z in interactions[item["dataset_id"]]}
        assert {i["trait"] for i in actual["interactions"]} == set(TRAITS)
        for test in actual["interactions"]:
            wanted = ref[test["trait"]]
            equal([test["lr"], test["p_value"]], [wanted["lr"], wanted["p_value"]])
            assert test["selects_sex_specific"] == wanted["selects_sex_specific"]
            checked_interactions += 1
    print(f"Reproduced {checked} contrasts and {checked_interactions} interaction tests from seven hash-verified inputs.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-replay", action="store_true", help="Verify the seven local participant tables.")
    parser.add_argument("--write-summary", action="store_true", help="Write the public nine-contrast figure inputs.")
    options = parser.parse_args()
    archive, summary = aggregates()
    if options.private_replay:
        replay_local(archive)
    if options.write_summary:
        OUT.write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    else:
        assert load_json(OUT) == summary
    print("Verified all nine adjusted comparisons against the independent matched-size archive.")
