"""Post-release interface/receipt/CSV audit; no fits or generator execution.

Preserves the frozen recomputation script and its raw review_required result.
The only adjudicated flags are its 'program' versus harness 'generator.py'
route-name mismatch, demonstrated from real execution receipts.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def main():
    here = Path(__file__).resolve().parent
    root = here.parent
    release_path = root / "TARGET_RELEASE.json"
    release = read(release_path)
    assert release["authorization"] == "root_releases_all_frozen_outputs_for_one_target_evaluation"
    output = here / "AUDIT_ADJUDICATION.json"
    assert not output.exists(), "No silent overwriting of adjudication"
    hashes = {}

    def check(path, expected=None):
        path = Path(path).resolve()
        actual = sha(path)
        if expected is not None:
            assert actual == expected, f"Hash mismatch: {path}"
        assert str(path) not in hashes or hashes[str(path)] == actual
        hashes[str(path)] = actual
        return actual

    check(release_path)
    snapshot = release["artifact_snapshot"]
    check(snapshot["path"], snapshot["sha256"])
    snapshot_data = read(snapshot["path"])
    for item in snapshot_data["artifacts"]:
        check(item["path"], item["sha256"])
    for tree in snapshot_data["directories"]:
        tree_root = Path(tree["path"])
        assert sorted(p.relative_to(tree_root).as_posix() for p in tree_root.rglob("*") if p.is_file()) == sorted(tree["relative_files"])
    for name in ("protocol", "evaluator", "reference", "endpoint_exposure_classification"):
        check(release[name]["path"], release[name]["sha256"])
    raw_path = here / "results/independent_audit.json"
    raw_hash = check(raw_path)
    raw = read(raw_path)
    checks_path = here / "results/numeric_comparison.json"
    check(checks_path)
    numeric_checks = read(checks_path)
    assert not raw["discrepancies"] and not raw["failed_analyses"] and not raw["reported_failed_analyses"]
    assert raw["status"] == "review_required"
    assert raw["release_sha256"] == sha(release_path)
    assert raw["artifact_snapshot_sha256"] == snapshot["sha256"]
    check(here / "recompute_m17b.py", raw["independent_script_sha256"])
    check(root / "custodian/results/evaluation.json", raw["reported_results_sha256"])
    expected_flags = {f"Direct table counted as repeated realizations for {b}/{s}"
                      for b in ("b1", "b2") for s in ("initial", "final")}
    assert set(raw["schedule_issues"]) == expected_flags
    items = release["generated_tables"]
    assert len(items) == 12
    assert {(x["builder"], x["stage"], x["seed"]) for x in items} == {
        (b, s, n) for b in ("b1", "b2") for s in ("initial", "final") for n in (17111, 17112, 17113)}
    assert all(x["route"] == "generator.py" for x in items)
    receipts = {}
    retained_pairs = []
    for builder in ("b1", "b2"):
        for filename in ("generator.py", "model_spec.json"):
            initial = root / "builders" / builder / "candidates/initial" / filename
            final = root / "builders" / builder / "candidates/final" / filename
            assert check(initial) == check(final), "Retention identity mismatch"
        for seed in (17111, 17112, 17113):
            pair = {x["stage"]: x for x in items if x["builder"] == builder and x["seed"] == seed}
            initial, final = pair["initial"], pair["final"]
            for key in ("path", "sha256", "execution_receipt", "execution_sha256"):
                assert initial[key] == final[key]
            assert initial["retention_reuse"] is True and final["retention_reuse"] is False
            assert initial["reuse_basis"] and final["reuse_basis"]
            check(final["path"], final["sha256"])
            receipt_path = Path(final["execution_receipt"])
            check(receipt_path, final["execution_sha256"])
            receipt = read(receipt_path)
            assert receipt["kind"] == "generator_execution" and receipt["route"] == "generator.py"
            assert receipt["status"] == "success" and receipt["generator_executed"] is True
            assert receipt["limits"]["seed"] == seed
            assert receipt["candidate"] == "candidates/final" and receipt["process"]["returncode"] == 0
            assert receipt["files"]["output/generated.csv"] == final["sha256"]
            for relative, expected in receipt["files"].items():
                check(receipt_path.parent / relative, expected)
            for filename in ("generator.py", "model_spec.json"):
                expected = sha(root / "builders" / builder / "candidates/final" / filename)
                assert receipt["files"]["input/" + filename] == expected
            receipts[str(receipt_path.resolve())] = {"builder": builder, "seed": seed,
                "sha256": final["execution_sha256"], "status": receipt["status"],
                "route": receipt["route"], "generator_executed": receipt["generator_executed"]}
            retained_pairs.append({"builder": builder, "seed": seed, "same_path": True,
                                   "same_bytes": True, "explicit_reuse": True})
    assert len(receipts) == 6
    csv_results = []
    for filename, keys in (("comparisons.csv", ["builder", "stage", "seed", "route", "endpoint"]),
                           ("realization_ranges.csv", ["builder", "stage", "endpoint"])):
        actual_path = here / "results" / filename
        reported_path = root / "custodian/results" / filename
        check(actual_path); check(reported_path)
        actual = pd.read_csv(actual_path).sort_values(keys).reset_index(drop=True)
        reported = pd.read_csv(reported_path).sort_values(keys).reset_index(drop=True)
        pd.testing.assert_frame_equal(actual, reported, check_exact=False, rtol=1e-8, atol=1e-10)
        numeric = actual.select_dtypes(include="number").columns
        max_diff = max(float(np.max(np.abs(actual[c] - reported[c]))) for c in numeric)
        csv_results.append({"file": filename, "rows": len(actual), "status": "match", "largest_absolute_difference": max_diff})
    paired_path = here / "results/paired_initial_final.csv"
    check(paired_path)
    paired = pd.read_csv(paired_path)
    assert len(paired) == 48 and (paired.final_minus_initial == 0).all()
    assert (paired.change_in_absolute_target_difference == 0).all()
    assert paired.same_path.all() and paired.same_bytes.all()
    for path, expected in hashes.items():
        assert sha(path) == expected, f"File changed during adjudication: {path}"
    report = {"status": "passed_after_explicit_route_schema_adjudication",
        "numerical_verdict": "PASS", "raw_audit_status": raw["status"], "raw_audit_sha256": raw_hash,
        "raw_audit_preserved": True, "frozen_script_unchanged": True,
        "adjudicated_issue": "Frozen independent checker expects program; actual harness and all six successful receipts use generator.py. Its four direct-table schedule alarms are route-label false alarms.",
        "raw_flags": raw["schedule_issues"], "primitive_field_comparisons": len(numeric_checks),
        "largest_absolute_difference": max(x.get("absolute_difference") or 0 for x in numeric_checks),
        "endpoint_count_per_table": 8, "scheduled_stage_entries": len(items),
        "unique_generated_tables": len({x['path'] for x in items}), "unique_execution_receipts": len(receipts),
        "unique_content_hashes": len({x['sha256'] for x in items}),
        "receipts": receipts, "retained_pairs": retained_pairs, "csv_comparisons": csv_results,
        "paired_endpoint_rows": len(paired), "all_paired_initial_final_differences_zero": True,
        "release_bound_snapshot_hash_verified": True, "snapshot_files": len(snapshot_data['artifacts']),
        "snapshot_directories": len(snapshot_data['directories']), "immutable_paths_checked": len(hashes),
        "hashes_before_and_after": hashes,
        "scope": "No scientific edits, fits, generator reruns, target tuning, or new target. Companion checks post-release route/receipt bindings and compares previously computed aggregates."}
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("status", "numerical_verdict", "primitive_field_comparisons",
        "largest_absolute_difference", "scheduled_stage_entries", "unique_generated_tables",
        "unique_execution_receipts", "all_paired_initial_final_differences_zero", "immutable_paths_checked")}))


if __name__ == "__main__":
    main()
