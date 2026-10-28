"""Summarize frozen evaluator aggregates only; never reads participant tables."""
from pathlib import Path
from datetime import datetime, timezone
import json
import numpy as np
import pandas as pd
from evaluate import sha, save

BASE = Path(__file__).resolve().parent
RESULTS = BASE/"results"
CONSTRUCTIONS = ["ordinary_1", "ordinary_2", "gap_1", "gap_2"]
LABELS = {
    "crude_bmi_per_5": "Crude BMI association per 5 kg/m^2",
    "adjusted_bmi_per_5": "Adjusted BMI association per 5 kg/m^2",
    "adjusted_age_per_10": "Adjusted age association per 10 years",
    "adjusted_female_minus_male": "Adjusted female minus male HDL",
    "bmi_slope_at_35_minus_25_per_5": "BMI slope at 35 minus slope at 25, per 5 kg/m^2",
    "female_minus_male_bmi_slope_per_5": "Female minus male BMI slope, per 5 kg/m^2",
    "male_bmi_slope_per_5": "Male BMI slope, per 5 kg/m^2",
    "female_bmi_slope_per_5": "Female BMI slope, per 5 kg/m^2"
}

def main():
    data = json.loads((RESULTS/"analysis_results.json").read_text())
    spec = json.loads((BASE/"analysis_spec.json").read_text())
    release = json.loads((BASE/"evaluation_release.json").read_text())
    draws = pd.read_csv(RESULTS/"all_endpoint_draws.csv", float_precision="round_trip")
    summaries = pd.read_csv(RESULTS/"endpoint_summary.csv", float_precision="round_trip")
    changes = pd.read_csv(RESULTS/"initial_final_changes.csv", float_precision="round_trip")
    names = [x["name"] for x in spec["endpoints"]]
    assert len(names) == 8 and set(names) == set(draws.endpoint)
    assert len(draws) == 320 and len(summaries) == 64 and len(changes) == 32
    assert len(data["generated"]) == 40
    assert draws.groupby(["construction", "stage", "endpoint"]).size().eq(5).all()
    reference = {x["endpoint"]: x for x in data["reference"]["endpoints"]}
    final = summaries[summaries.stage == "final"].set_index(["construction", "endpoint"])
    table = []
    for name in names:
        ref = reference[name]
        row = {"endpoint": name, "description": LABELS[name], "unit": "mg/dL", "role": ref["role"],
               "reference_estimate": ref["estimate"], "reference_ci95_low": ref["ci95_low"],
               "reference_ci95_high": ref["ci95_high"], "reference_df": ref["df"]}
        for construction in CONSTRUCTIONS:
            f = final.loc[(construction, name)]
            for column in ["generated_median", "generated_min", "generated_max", "median_difference", "median_absolute_difference"]:
                row[construction+"_"+column] = float(f[column])
            actual = draws[(draws.construction == construction) & (draws.stage == "final") & (draws.endpoint == name)]
            assert float(f.generated_median) == float(np.median(actual.estimate))
            assert float(f.median_absolute_difference) == float(np.median(abs(actual.estimate-ref["estimate"])))
        table.append(row)
    pd.DataFrame(table).to_csv(RESULTS/"final_endpoint_comparison.csv", index=False)
    # All four constructions and all eight endpoint changes retained.
    concise = changes[["construction", "arm", "endpoint", "generated_median_initial", "generated_median_final",
                       "median_absolute_difference_initial", "median_absolute_difference_final",
                       "final_minus_initial_median_absolute_difference"]].copy()
    concise.to_csv(RESULTS/"initial_final_error_changes.csv", index=False)
    identical = {}
    for construction in CONSTRUCTIONS:
        entries = [x for x in release["outputs"] if x["construction"] == construction]
        initial = sorted([x for x in entries if x["stage"] == "initial"], key=lambda x: x["draw"])
        final_entries = sorted([x for x in entries if x["stage"] == "final"], key=lambda x: x["draw"])
        identical[construction] = all(x["sha256"] == y["sha256"] for x, y in zip(initial, final_entries))
        if identical[construction]:
            assert (changes.loc[changes.construction == construction, "final_minus_initial_median_absolute_difference"] == 0).all()
    distribution = []
    def flatten(obj):
        return {"weighted_mean": obj["weighted_mean"], "weighted_sd": obj["weighted_sd_population"],
                "weighted_q10": obj["weighted_quantiles_inverse_cdf"]["0.1"],
                "weighted_q50": obj["weighted_quantiles_inverse_cdf"]["0.5"],
                "weighted_q90": obj["weighted_quantiles_inverse_cdf"]["0.9"],
                "weighted_bmi_correlation": obj["weighted_bmi_correlation"]}
    ref_dist = flatten(data["reference"]["distribution"])
    for name in ref_dist:
        row = {"metric": name, "reference": ref_dist[name]}
        for construction in CONSTRUCTIONS:
            values = [flatten(x["distribution"])[name] for x in data["generated"] if x["construction"] == construction and x["stage"] == "final"]
            row[construction+"_median"] = float(np.median(values))
            row[construction+"_min"] = float(min(values))
            row[construction+"_max"] = float(max(values))
        distribution.append(row)
    pd.DataFrame(distribution).to_csv(RESULTS/"final_distribution_comparison.csv", index=False)
    ordinary_changes = concise[concise.construction == "ordinary_1"]
    report = {
        "created_utc": datetime.now(timezone.utc).isoformat(), "evaluator_errors": [],
        "source": "Frozen analysis_results.json and aggregate CSVs only; participant rows never read by this reporting script",
        "all_endpoints_reported": names, "units": "All endpoint estimates in mg/dL for the specified contrast",
        "final_summary_definition": "Median across all five fixed-seed draws; min/max are draw ranges, not confidence intervals",
        "reference_confidence_intervals": "Prespecified stratified-PSU Taylor estimator with t intervals and model-adjusted design degrees of freedom",
        "final_comparison": table, "all_initial_final_changes": concise.to_dict("records"),
        "initial_final_generated_output_hashes_identical": identical,
        "ordinary_1_error_changes": {"decreased_endpoints": ordinary_changes.loc[ordinary_changes.final_minus_initial_median_absolute_difference < 0, "endpoint"].tolist(),
                                     "increased_endpoints": ordinary_changes.loc[ordinary_changes.final_minus_initial_median_absolute_difference > 0, "endpoint"].tolist()},
        "interpretation": [
            "All four final constructions have negative crude/adjusted and sex-specific BMI slopes, as does the reference; effect magnitudes differ.",
            "Every final median curvature contrast is positive but below the reference contrast. The direction alone does not establish recovery of shape magnitude.",
            "Adjusted age is much closer in ordinary_2 than in the other constructions; all adjusted female-minus-male effects are positive but differ in magnitude.",
            "The reference female-minus-male BMI-slope interval spans zero; differences in interaction point-estimate signs should not be labeled clear scientific contradictions.",
            "ordinary_1 revision reduces median absolute error on five endpoints and increases it on three; the other three constructions retain identical generated outputs and all eight errors.",
            "These are descriptive construction-specific results. No overall score, universal success threshold, or inferential claim of arm superiority is calculated."
        ],
        "limitations": data["limitations"], "participant_rows_exported": False,
        "input_hashes": {p.name: sha(p) for p in [RESULTS/"analysis_results.json", RESULTS/"all_endpoint_draws.csv", RESULTS/"endpoint_summary.csv", RESULTS/"initial_final_changes.csv", BASE/"evaluation_release.json", BASE/"evaluate.py", BASE/"analysis_spec.json"]}
    }
    save(RESULTS/"aggregate_report.json", report)
    pd.DataFrame([{key: row[key] for key in ["endpoint", "reference_estimate", "reference_ci95_low", "reference_ci95_high"]+[c+"_generated_median" for c in CONSTRUCTIONS]} for row in table]).to_csv(RESULTS/"compact_final_table.csv", index=False)
    print(json.dumps({"all_eight_endpoints_reported": True, "output_hash_identical_versions": identical,
                      "ordinary_1_error_change_counts": {"decreased": len(report["ordinary_1_error_changes"]["decreased_endpoints"]), "increased": len(report["ordinary_1_error_changes"]["increased_endpoints"])},
                      "participant_rows_exported": False}))

if __name__ == "__main__":
    main()
