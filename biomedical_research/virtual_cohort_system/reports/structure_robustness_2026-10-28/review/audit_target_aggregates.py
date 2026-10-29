"""Audit released endpoint aggregates and receipts, without rows or model fits."""
from collections import defaultdict
import csv
from datetime import datetime, timedelta
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import statistics

from scipy.stats import t


ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "agent_bundle"
RESULTS = ROOT / "custodian/evaluation"
EXPECTED_COMMITMENT = "f41fd145f0b566d3332419b3f65e78d5e774bc44434c6dc313bd167846ff4f65"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(path):
    path = Path(path)
    if path.suffix.lower() == ".csv" and path.name not in {"endpoint_comparison.csv", "structure_summary.csv"}:
        raise ValueError("Participant and generated-row CSV reads are prohibited in this audit")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def records(path):
    path = Path(path)
    assert path.name in {"endpoint_comparison.csv", "structure_summary.csv"}
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def tm(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def close(left, right, tolerance=1e-11):
    assert math.isfinite(float(left)) and math.isfinite(float(right))
    assert math.isclose(float(left), float(right), rel_tol=tolerance, abs_tol=tolerance), (left, right)


def point(value):
    return "positive" if value > 0 else "negative" if value < 0 else "exactly_zero"


def interval_direction(low, high):
    return "positive" if low > 0 else "negative" if high < 0 else "interval_includes_zero"


def main():
    manifest_path = ROOT / "evaluation_commitment.json"
    assert sha(manifest_path) == EXPECTED_COMMITMENT
    manifest = read(manifest_path)
    protocol = read(ROOT / "protocol.json")
    analysis_protocol = read(ROOT / "custodian/analysis_protocol.json")
    endpoints = [entry["id"] for entry in analysis_protocol["endpoints"]]
    structures = protocol["structures"]; seeds = protocol["target_seeds"]
    scales = ["native", "cdc_backward_auxiliary"]
    guard = read(ROOT / "release_verification.json")
    release = read(RESULTS / "release_receipt.json")
    assert guard == release["guard_result"]
    assert guard["status"] == "passed"
    assert (guard["candidates_verified"], guard["source_replays_verified"], guard["target_outputs_verified"]) == (6, 18, 15)
    assert guard["release_manifest_sha256"] == release["commitment_sha256"] == EXPECTED_COMMITMENT
    assert guard["guard_sha256"] == sha(ROOT / "release_guard.py")
    assert guard["protocol_commitment_sha256"] == sha(ROOT / "protocol_commitment.json")
    assert guard["protocol_sha256"] == sha(ROOT / "protocol.json")
    assert release["protocol_sha256"] == sha(ROOT / "custodian/analysis_protocol.json")
    assert release["all_outputs_validated_before_hidden_table_parse"] is True
    assert manifest["post_evaluation_builder_revision_allowed"] is False

    # Current frozen model files are checked against the pre-release receipts;
    # all CSV commitments are deliberately left to the recorded release guard.
    model_hashes_checked = 0
    candidate_keys = {(c["structure"], c["stage"]) for c in manifest["candidate_commitments"]}
    assert candidate_keys == set(itertools.product(structures, ["initial", "final"]))
    assert len(manifest["candidate_commitments"]) == 6
    assert {p.name for p in (BUNDLE / "candidates").iterdir() if p.is_dir()} == {f"{s}_{st}" for s, st in candidate_keys}
    final_times = []
    for candidate in manifest["candidate_commitments"]:
        path = Path(candidate["path"])
        assert sha(path) == candidate["sha256"]
        freeze = read(path)
        if candidate["stage"] == "final": final_times.append(tm(freeze["created_utc"]))
        for name in ["generator.py", "model_spec.json", "evidence.json", "source_replay.json",
                     "source_checks.json", "checks.json", "decision.md"]:
            expected = freeze["commitments"][f"candidates/{candidate['candidate_name']}/{name}"]
            assert sha(path.parent / name) == expected
            model_hashes_checked += 1
    lock_path = ROOT / "custodian/custodian_lock.json"
    assert sha(lock_path) == manifest["custodian_lock_sha256"] == release["custodian_lock_sha256"]
    for name in ["analysis_protocol.json", "survey_analysis.py", "evaluate_committed.py", "methods_freeze.json"]:
        assert sha(ROOT / "custodian" / name) == read(lock_path)["files"][name]

    # Complete target schedule and procedural timestamps, using receipts only.
    expected_runs = {row["run_id"] for row in manifest["outputs"]}
    assert len(expected_runs) == 15
    assert {p.name for p in (BUNDLE / "executions").iterdir() if p.is_dir()} == expected_runs
    assert {(x["structure"], x["seed"]) for x in manifest["outputs"]} == set(itertools.product(structures, seeds))
    source_audit = read(ROOT / "review/source_diagnostic_review.json")
    latest_source = tm(source_audit["final_source_last_report_utc"])
    target_starts = []; target_ends = []; execution_hashes = {}
    for entry in manifest["outputs"]:
        path = BUNDLE / "executions" / entry["run_id"] / "execution.json"
        receipt = read(path)
        assert receipt["status"] == "success" and receipt["generator_executed"] is True
        assert receipt["candidate"] == f"candidates/{entry['structure']}_final"
        assert receipt["limits"]["seed"] == entry["seed"]
        assert receipt["files"]["output/generated.csv"] == entry["sha256"]
        assert receipt["candidate_freeze_sha256"] == sha(BUNDLE / receipt["candidate"] / "freeze.json")
        start = tm(receipt["created_utc"]); end = start + timedelta(seconds=receipt["elapsed_seconds"])
        target_starts.append(start); target_ends.append(end)
        execution_hashes[entry["run_id"]] = sha(path)
        assert max([latest_source, *final_times]) <= start <= end <= tm(manifest["created_utc"])
        assert read(ROOT / "controller_logs" / f"{entry['run_id']}.json")["returncode"] == 0
    assert max(target_ends) <= tm(manifest["created_utc"]) <= tm(release["release_utc"])
    assert sha(Path(manifest["structure_plan_commitment"]["path"])) == manifest["structure_plan_commitment"]["sha256"]
    assert manifest["structure_plan_commitment"]["sha256"] == source_audit["structure_plan_commitment_sha256"]
    for filename, expected in read(RESULTS / "result_hashes.json").items():
        assert sha(RESULTS / filename) == expected

    reference = read(RESULTS / "reference_analyses.json")
    assert set(reference) == set(scales)
    for scale in scales:
        assert set(reference[scale]) == set(endpoints)
        for endpoint, value in reference[scale].items():
            assert value["n"] == 2660 and value["df"] == 15 and value["se"] >= 0
            delta = float(t.ppf(.975, value["df"])) * value["se"]
            close(value["ci_low"], value["estimate"] - delta)
            close(value["ci_high"], value["estimate"] + delta)
            assert value["point_direction"] == point(value["estimate"])
            assert value["ci_direction"] == interval_direction(value["ci_low"], value["ci_high"])
            if endpoint == "raw_bmi_curvature_second_difference":
                assert value["scale"] == "mg_dl" and "exp_estimate" not in value
            else:
                assert value["scale"] == "log_mg_dl"
                for field, raw in [("exp_estimate", "estimate"), ("exp_ci_low", "ci_low"), ("exp_ci_high", "ci_high")]:
                    close(value[field], math.exp(value[raw]))

    rows = records(RESULTS / "endpoint_comparison.csv")
    assert len(rows) == 180
    assert not {"ci_low", "ci_high", "se", "df"} & rows[0].keys(), "Generated uncertainty columns must not be presented"
    expected_grid = set(itertools.product(scales, structures, seeds, endpoints))
    grid = [(r["measurement_scale"], r["structure"], int(r["seed"]), r["endpoint"]) for r in rows]
    assert len(set(grid)) == 180 and set(grid) == expected_grid
    groups = defaultdict(list); all_groups = defaultdict(list); indexed = {}
    for row, key in zip(rows, grid):
        scale, structure, seed, endpoint = key
        ref = reference[scale][endpoint]
        estimate = float(row["estimate"])
        close(row["reference_estimate"], ref["estimate"])
        close(row["reference_ci_low"], ref["ci_low"]); close(row["reference_ci_high"], ref["ci_high"])
        close(row["signed_error"], estimate - ref["estimate"])
        close(row["absolute_error"], abs(estimate - ref["estimate"]))
        assert row["point_direction"] == point(estimate)
        assert row["reference_point_direction"] == ref["point_direction"]
        assert row["reference_ci_direction"] == ref["ci_direction"]
        assert row["point_direction_agrees"] == str(point(estimate) == ref["point_direction"])
        assert row["scale"] == ref["scale"] and int(row["n"]) == 2660
        if endpoint == "raw_bmi_curvature_second_difference": assert row["exp_estimate"] == ""
        else: close(row["exp_estimate"], math.exp(estimate))
        groups[(scale, endpoint, structure)].append(row)
        all_groups[(scale, endpoint)].append(row)
        indexed[key] = row

    summary = read(ROOT / "summaries/structure_summary.json")
    summary_csv = records(ROOT / "summaries/structure_summary.csv")
    assert len(summary) == len(summary_csv) == len(groups) == 36
    assert {(s["measurement_scale"], s["endpoint"], s["structure"]) for s in summary} == set(groups)
    for item, csv_item in zip(summary, summary_csv):
        key = (item["measurement_scale"], item["endpoint"], item["structure"])
        group = groups[key]; values = [float(r["estimate"]) for r in group]
        ref = reference[key[0]][key[1]]
        assert item["n_draws"] == item["expected_draws"] == len(group) == 5
        assert item["point_direction_agreement_count"] == sum(r["point_direction_agrees"] == "True" for r in group)
        for field, expected in {"median": statistics.median(values), "minimum": min(values), "maximum": max(values),
                                "median_absolute_error": statistics.median(float(r["absolute_error"]) for r in group),
                                "reference": ref["estimate"], "reference_ci_low": ref["ci_low"], "reference_ci_high": ref["ci_high"]}.items():
            close(item[field], expected)
        assert item["reference_ci_direction"] == ref["ci_direction"]
        for field, value in item.items():
            if isinstance(value, (float, int)): close(csv_item[field], value)
            else: assert csv_item[field] == value

    robust = read(RESULTS / "direction_robustness.json")
    assert len(robust) == len(all_groups) == 12
    assert {(r["measurement_scale"], r["endpoint"]) for r in robust} == set(all_groups)
    for item in robust:
        key = (item["measurement_scale"], item["endpoint"]); group = all_groups[key]
        directions = sorted({r["point_direction"] for r in group})
        count = sum(r["point_direction_agrees"] == "True" for r in group)
        assert item["expected_outputs"] == item["estimable_outputs"] == len(group) == 15
        assert item["all_outputs_estimable"] is True
        assert item["point_directions"] == directions
        assert item["all_generated_same_point_direction"] == (len(directions) == 1)
        assert item["point_direction_agreement_count"] == count
        assert item["all_generated_match_reference_point_direction"] == (count == 15)
        assert item["reference_point_direction"] == reference[key[0]][key[1]]["point_direction"]
        assert item["reference_ci_direction"] == reference[key[0]][key[1]]["ci_direction"]
        for field, expected in {"estimate_min": min(float(r["estimate"]) for r in group),
                                "estimate_max": max(float(r["estimate"]) for r in group),
                                "absolute_error_min": min(float(r["absolute_error"]) for r in group),
                                "absolute_error_max": max(float(r["absolute_error"]) for r in group)}.items(): close(item[field], expected)
    assert read(RESULTS / "nonestimable_sensitivities.json") == []

    # An affine outcome mapping with intercept in the same design gives exact
    # positive scaling of raw curvature, its SE, and its interval endpoints.
    raw_endpoint = "raw_bmi_curvature_second_difference"
    errors = []
    for field in ["estimate", "se", "ci_low", "ci_high"]:
        expected = .9785 * reference["native"][raw_endpoint][field]
        actual = reference["cdc_backward_auxiliary"][raw_endpoint][field]
        close(actual, expected); errors.append(abs(actual - expected))
    for structure, seed in itertools.product(structures, seeds):
        native = float(indexed[("native", structure, seed, raw_endpoint)]["estimate"])
        backward = float(indexed[("cdc_backward_auxiliary", structure, seed, raw_endpoint)]["estimate"])
        close(backward, .9785 * native); errors.append(abs(backward - .9785 * native))

    notes = read(RESULTS / "report_notes.json")
    assert notes["outputs_evaluated"] == 15 and notes["all_structures"] == structures and notes["all_seeds"] == seeds
    assert notes["primary"] == [e["id"] for e in analysis_protocol["endpoints"] if e["tier"] == "primary"]
    assert notes["secondary"] == [e["id"] for e in analysis_protocol["endpoints"] if e["tier"] == "secondary"]

    # Human interpretation review is tied to the exact reviewed report versions.
    # Independently reconcile every printed native endpoint estimate/range/CI.
    project = ROOT.parent.parent
    reviewed_hashes = {
        "MILESTONE_5_RESULTS.md": "d057cefc68600e889e368201fad874e4a3b7a3a69ce8fcb11422a8b7a13f66b8",
        "README.md": "f280529a72ebc6d3ee474872756d46e1a6b8d66d53e2dfaf61373d6a6fe4d76f",
    }
    for name, digest in reviewed_hashes.items():
        assert sha(project / name) == digest, "Report changed after independent interpretation review"
    report = (project / "MILESTONE_5_RESULTS.md").read_text(encoding="utf-8")
    labels = {
        "Age, log TG per 10 years": "adjusted_age_per10",
        "BMI curvature, log TG": "bmi_curvature_second_difference",
        "BMI curvature, raw TG mg/dL": "raw_bmi_curvature_second_difference",
        "BMI, log TG per 5 kg/m²": "adjusted_bmi_per5",
        "Female versus male, log TG": "adjusted_female_vs_male",
        "BMI×female interaction": "bmi_sex_interaction",
    }
    printed_numbers_checked = 0
    for label, endpoint in labels.items():
        lines = [line for line in report.splitlines() if line.startswith("| " + label + " |")]
        assert len(lines) == 1
        printed = re.findall(r"[-+]?\d+(?:\.\d+)?", "|".join(lines[0].split("|")[2:]).replace("−", "-"))
        ref = reference["native"][endpoint]
        expected = [ref[k] for k in ["estimate", "ci_low", "ci_high"]]
        for structure in structures:
            item = next(s for s in summary if (s["measurement_scale"], s["endpoint"], s["structure"]) == ("native", endpoint, structure))
            expected.extend(item[k] for k in ["median", "minimum", "maximum"])
        assert len(printed) == len(expected) == 12
        for number, value in zip(printed, expected):
            decimal_places = len(number.split(".")[1]) if "." in number else 0
            assert abs(float(number) - value) <= .5 * 10 ** (-decimal_places) + 1e-12
            printed_numbers_checked += 1
    assert printed_numbers_checked == 72
    native_bmi = all_groups[("native", "adjusted_bmi_per5")]
    assert all(float(r["estimate"]) > reference["native"]["adjusted_bmi_per5"]["ci_high"] for r in native_bmi)
    gate_tests = read(ROOT / "review/release_guard_verification.json")
    custodian_tests = read(ROOT / "custodian/guard_validation_receipt.json")
    assert gate_tests["status"] == custodian_tests["status"] == "passed"
    assert gate_tests["test_count"] == 32 and custodian_tests["tests_run"] == 11
    report_review = {
        "status": "passed", "reviewed_report_sha256": reviewed_hashes,
        "native_table_numbers_independently_reconciled": printed_numbers_checked,
        "new_check_count_supported_by_receipts": 43,
        "historical_core_tests_rerun": False,
        "review_scope": "M5 report in full and current README v0.5 M5 summary; no earlier result report opened.",
        "blocking_or_unsupported_claims_found": [],
        "interpretation_checks": [
            "Primary sign stability limited to selected Agent-proposed structures and residual draws.",
            "All 15 adjusted BMI values exceed native reference CI upper bound descriptively, not a calibrated estimator-comparison test.",
            "Raw curvature magnitude discrepancy and 9-negative/6-positive interaction retained.",
            "Source fit trade-offs, source-challenged S3, and shared assumptions remain explicit.",
            "Only final target candidates evaluated; no source-feedback target-gain claim.",
            "Raw backward assay sensitivity is mechanical rescaling, not independent validation.",
            "Five-draw ranges are not confidence intervals; reference CI uses survey uncertainty.",
            "Procedural Agent blindness and temporal within-survey replication limits are explicit."
        ],
        "limits": "Checks concern scientific/aggregate consistency; export-package completeness is handled separately by the controller."
    }
    (ROOT / "review/report_consistency_review.json").write_text(json.dumps(report_review, indent=2) + "\n", encoding="utf-8")
    audit = {"status": "passed", "scope": "released_aggregate_arithmetic_and_receipt_audit_only",
             "release_manifest_sha256": EXPECTED_COMMITMENT,
             "candidate_freezes": 6, "source_replays": 18, "target_outputs": 15,
             "endpoint_rows_checked": 180, "structure_summary_rows_checked": 36,
             "global_endpoint_summaries_checked": 12, "reference_intervals_checked": 12,
             "draws_per_structure_endpoint_scale": 5, "nonestimable_sensitivities": 0,
             "current_frozen_scientific_file_hashes_checked": model_hashes_checked,
             "post_release_model_hashes_unchanged": True,
             "first_target_execution_utc": min(target_starts).isoformat(),
             "last_target_recorded_end_utc": max(target_ends).isoformat(),
             "manifest_created_utc": manifest["created_utc"], "release_utc": release["release_utc"],
             "raw_backward_scaling_max_absolute_roundoff": max(errors),
             "reference_CI": "Two-sided t(.975, df=15) intervals checked from reported SE; no model was refit.",
             "generated_uncertainty": "Point estimates and descriptive seed ranges only; not calibrated intervals.",
             "participant_tables_read": False, "generated_row_tables_read": False,
             "model_fits_run": False, "generator_executed": False,
             "report_consistency_review": report_review,
             "figure_visual_check": "Three native panels inspected; reference CI distinct from five generated dots and range; caption explicitly disclaims CI for generated ranges.",
             "limits": ["Procedural trusted-host audit, not OS-enforced blindness or externally authenticated chronology.",
                        "No refitting or independent row-level validation was performed; original evaluator/guard supplied those checks.",
                        "Stable primary signs coexist with source mismatch, magnitude errors, and unstable BMI-sex interaction."],
             "native_global_endpoint_results": [x for x in robust if x["measurement_scale"] == "native"],
             "all_structure_summaries": summary, "target_execution_receipt_hashes": execution_hashes,
             "aggregate_hashes": {"reference_analyses.json": sha(RESULTS / "reference_analyses.json"),
                                  "endpoint_comparison.csv": sha(RESULTS / "endpoint_comparison.csv"),
                                  "structure_summary.json": sha(ROOT / "summaries/structure_summary.json"),
                                  "structure_summary.csv": sha(ROOT / "summaries/structure_summary.csv")}}
    (ROOT / "review/target_aggregate_audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in audit.items() if k not in {"native_global_endpoint_results", "all_structure_summaries", "target_execution_receipt_hashes"}}, indent=2))


if __name__ == "__main__":
    main()
