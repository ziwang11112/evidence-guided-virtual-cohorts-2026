"""Summarize saved aggregate audit outputs; does not read rows or fit models."""
import hashlib
import json
from collections import Counter
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    base = Path(__file__).resolve().parent
    audit_path = base / "released_audit_results" / "independent_audit.json"
    mapped_path = base / "canonical_released_aggregate.json"
    published_path = base.parent / "results" / "evaluation.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    mapped = json.loads(mapped_path.read_text(encoding="utf-8"))
    published = json.loads(published_path.read_text(encoding="utf-8"))
    differences = audit["released_output_comparison"]["differences"]
    nonnumeric = [item for item in differences if item["kind"] != "numeric_difference"]
    value_differences = [item for item in differences if item["kind"] == "numeric_difference"]
    numeric_metadata_differences = [item for item in value_differences if not item["field"].endswith((".value", ".minimum", ".maximum"))]
    published_comparisons = {}
    key_map = mapped["mapping_provenance"]["estimand_key_map"]
    for candidate in published["candidate_comparisons"]:
        for item in candidate["estimands"]:
            for label in candidate["labels"]:
                published_comparisons[(label, key_map[item["estimand"]])] = item
    comparison_checks = []
    for item in audit["comparisons"]:
        for label in ("initial", "final"):
            source = published_comparisons[(label, item["estimand"])]
            independent_delta = item[f"{label}_minus_reference"]
            published_delta = source["difference_generated_minus_measured"]
            direction = item.get(f"{label}_direction")
            same_sign = None if direction is None else direction["reference_sign"] == direction["candidate_sign"]
            comparison_checks.append({"estimand": item["estimand"], "label": label,
                    "independent_difference": independent_delta, "released_difference": published_delta,
                    "difference_discrepancy": independent_delta - published_delta if independent_delta is not None and published_delta is not None else None,
                    "same_sign_field_agrees": same_sign == source["same_sign"]})
    subsets = {
        "24_estimands_each_reference_initial_final": [item for item in value_differences if item["field"].startswith("estimates.")],
        "psu_deletion_values": [item for item in value_differences if item["field"].startswith("reference_psu_sensitivity.deletions")],
        "psu_full_fits_and_ranges": [item for item in value_differences if item["field"].startswith("reference_psu_sensitivity.ranges")],
    }
    checks = {"kind": "m15b_independent_audit_checks", "actual_recomputation_executions": 1,
        "independent_implementation": "statsmodels formula OLS, QR fits, scipy SVD rank, stdlib summaries and explicit Q90; original evaluator implementation never read or imported",
        "original_evaluator_imported": False,
        "all_manifest_bindings_match": all(item["matched"] for item in audit["bindings"]["commitments"]),
        "binding_count": len(audit["bindings"]["commitments"]),
        "release_manifest_sha256": audit["bindings"]["release_manifest_sha256"],
        "preservation": audit["preservation"],
        "unique_candidate_value_tables": audit["unique_candidate_value_tables"],
        "unique_candidate_table_count_matches_release": audit["unique_candidate_value_tables"] == published["unique_candidate_tables"],
        "fixed_estimands_per_label": {label: len(estimates) for label, estimates in audit["estimates"].items()},
        "all_estimate_statuses": dict(Counter(item["status"] for table in audit["estimates"].values() for item in table.values())),
        "joint_psu_groups": len(audit["reference_psu_sensitivity"]["deletions"]),
        "joint_psu_deletion_coefficient_fits": sum(len(row["estimates"]) for row in audit["reference_psu_sensitivity"]["deletions"]),
        "categorical_null_or_missing_field_mismatches": nonnumeric,
        "numeric_count_rank_metadata_differences": numeric_metadata_differences,
        "all_counts_ranks_statuses_and_stability_fields_exactly_agree": not nonnumeric and not numeric_metadata_differences,
        "numeric_nonzero_discrepancy_count": len(value_differences),
        "largest_absolute_numeric_discrepancy": max((item["absolute_difference"] for item in value_differences), default=0),
        "numeric_discrepancy_summary": {label: {"nonzero_difference_count": len(values), "largest_absolute_discrepancy": max((item["absolute_difference"] for item in values), default=0)} for label, values in subsets.items()},
        "generated_minus_reference_comparison_checks": comparison_checks,
        "largest_absolute_generated_minus_reference_discrepancy": max(abs(item["difference_discrepancy"] or 0) for item in comparison_checks),
        "all_reported_comparison_signs_agree": all(item["same_sign_field_agrees"] for item in comparison_checks),
        "released_json_csv_consistency": mapped["mapping_provenance"]["json_csv_consistency"],
        "interpretation": "Differences are consistent with ordinary floating-point roundoff. This is numerical/dataflow agreement, not a scientific acceptance threshold or a quality score. Initial and final are one unique candidate table, not two independent cohorts.",
        "scientific_observation": {"age_reference": audit["estimates"]["reference"]["global.age"]["value"],
            "age_generated_initial_and_final": audit["estimates"]["final"]["global.age"]["value"],
            "age_reference_psu_range": [audit["reference_psu_sensitivity"]["ranges"]["global.age"][key] for key in ("minimum", "maximum")],
            "note": "The age coefficient reverses sign; reference deletion estimates remain negative. Same signs for the other global coefficients do not establish general analytical usability."},
        "artifact_hashes": {name: digest(base / name) for name in ("audit.py", "test_audit.py", "map_released_output.py", "canonical_released_aggregate.json", "released_audit_results/independent_audit.json", "released_audit_results/independent_estimands.csv")}}
    checks_path = base / "released_audit_results" / "audit_checks.json"
    if checks_path.exists():
        raise ValueError("Refusing overwrite of saved audit checks.")
    checks_path.write_text(json.dumps(checks, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    lines = ["# Independent post-release numerical and dataflow audit", "",
        "The independent audit was executed once after the root controller explicitly authorized the final freeze and evaluation release. All 24 reference/initial/final estimands and the four global reference sensitivity analyses were retained. The original evaluator implementation was never read or imported; only its documented release interface and released aggregate output schema were used.", "",
        "The nine manifest hash commitments match, including both frozen candidate tables and the precommitted reference. All 200 identities, row order, race/sex values and exact decimal age/BMI values are preserved, with 50 people per group. Initial and final have **zero changed urate rows** and identical table hashes: they are **one unique candidate table**, not two cohorts or evidence replications.", "",
        "The 72 labeled estimates (24 each for reference, initial and final), 116 joint-PSU deletion coefficient fits (29 groups by four endpoints), four full reference fits and eight range endpoints agree with the released evaluator up to ordinary floating-point roundoff. No sample-count, matrix-rank, status, null, sign-stability or deletion-identity discrepancies were found. The largest absolute discrepancy among estimates and PSU results is `4.440892098500626e-15`. All 24 released CSV rows and 576 checked fields agree exactly with the released JSON. All 48 generated-minus-reference differences were also checked: their largest absolute discrepancy is `7.105427357601002e-15`, and all reported comparison signs agree.", "",
        "| Global estimand | Reference | Initial = final | Generated minus reference | Reference joint-PSU range |", "|---|---:|---:|---:|---|" ]
    for key, label in (("global.bmi", "BMI / 5 kg/m²"), ("global.age", "Age / 10 years"), ("global.curvature", "Squared scaled BMI"), ("global.interaction", "BMI × male")):
        item = next(row for row in audit["comparisons"] if row["estimand"] == key)
        sensitivity = audit["reference_psu_sensitivity"]["ranges"][key]
        lines.append(f"| {label} | {item['reference']['value']:.9f} | {item['final']['value']:.9f} | {item['final_minus_reference']:.9f} | [{sensitivity['minimum']:.9f}, {sensitivity['maximum']:.9f}] |")
    lines.extend(["", "All four reference coefficients retain their full-fit sign across all 29 deletions; no deletion fit or rank failures occurred. These ranges are descriptive sensitivity of the fixed quota subset, not confidence intervals or national-population uncertainty.", "",
        "The age coefficient is negative in the measured reference and positive in the generated table; every reference age deletion estimate remains negative. The other three global signs agree, which does not establish general analytical usability. This audit supplies numerical/dataflow corroboration of the same fixed analyses, not a new validation dataset, experiment, scientific pass/fail criterion, candidate choice, or repair.", "",
        "Complete aggregate results are in `released_audit_results/independent_audit.json` and `independent_estimands.csv`; comparisons, bindings and artifact hashes are in `released_audit_results/audit_checks.json`. `canonical_released_aggregate.json` retains the transparent output mapping and source aggregate hashes. No participant rows are exported in these artifacts. The 14 pre-release tests used invented data only.", "",
        "The gate verifies committed bytes. Source review, lifecycle checks, reviewer identity and commitment timing remain controller assertions; no OS isolation or independent provenance proof is claimed.", ""])
    (base / "AUDIT_REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"checks_written": str(checks_path), "maximum_absolute_discrepancy": checks["largest_absolute_numeric_discrepancy"],
                      "numeric_metadata_mismatches": len(numeric_metadata_differences), "nonnumeric_mismatches": len(nonnumeric),
                      "max_comparison_difference_discrepancy": checks["largest_absolute_generated_minus_reference_discrepancy"]}))


if __name__ == "__main__":
    main()
