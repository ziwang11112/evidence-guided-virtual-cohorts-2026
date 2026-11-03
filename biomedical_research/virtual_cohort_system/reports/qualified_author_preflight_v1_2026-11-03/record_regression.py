"""Reproduce the permitted metadata-only result record in this work directory."""
import copy
import json
from pathlib import Path
import platform

import qualified_author_preflight as preflight


def main():
    workspace = preflight.PROJECT.parents[1]
    submissions, hypothetical = [], []
    inputs = {}
    for author, candidate in [("A01", "initial"), ("A01", "initial_interface"), ("A02", "initial_interface")]:
        bundle = workspace / "evcDP" / author
        payload, paths, hashes = preflight.load_metadata(bundle, candidate)
        inputs.update(hashes)
        report = preflight.preflight_metadata(*payload, source_paths=paths)
        submissions.append({"author": author, "candidate": candidate, **report})
        if candidate == "initial_interface":
            copied = copy.deepcopy(payload)
            declaration = copied[-1]["contexts"]["J"]
            declaration["column_aliases"].append({"source_name": "HbA1c_percent", "generated_name": "hba1c",
                "assumption_ids": declaration["checks"][0]["measurement_mapping"]["assumption_ids"][:]})
            for check in declaration["checks"]:
                check["measurement_mapping"]["input_column"] = "HbA1c_percent"
            corrected = preflight.preflight_metadata(*copied, source_paths=paths)
            hypothetical.append({"author": author, "candidate": candidate,
                "scope": "Copied in-memory metadata only; locations refer to the original inputs, not modified files.",
                "change": "J alias HbA1c_percent <- hba1c and both J mapping input_column values set to HbA1c_percent; existing mapping assumption IDs reused.",
                "status": corrected["status"], "counts": corrected["counts"], "findings": corrected["findings"]})
    unchanged = {path: preflight.digest(path) for path in inputs} == inputs
    assert unchanged
    assert [record["counts"]["findings"] for record in submissions] == [5, 2, 2]
    assert all(record["status"] == "metadata_checks_passed" for record in hypothetical)
    result = {"kind": "qualified_author_preflight_readonly_regression_record_v1",
        "runtime": {"python": platform.python_version(), "numpy": preflight.qualified.np.__version__,
                    "pandas": preflight.contracts.pd.__version__},
        "retained_submissions": submissions, "hypothetical_in_memory_corrections": hypothetical,
        "finite_counts": {"retained_submissions": 3, "retained_contexts_visited": 9, "retained_checks_visited": 12,
                          "retained_findings": 9, "hypothetical_copied_plans": 2, "hypothetical_checks_passed": 8,
                          "unique_input_files": len(inputs), "generator_executions": 0, "generated_tables": 0,
                          "candidate_writes": 0, "approvals_created": 0},
        "input_files_unchanged_after_readonly_checks": unchanged, "input_sha256": inputs,
        "dependency_sha256": preflight.dependency_fingerprints(),
        "record_script_sha256": preflight.digest(__file__),
        "limitations": preflight.LIMITATIONS + ["The hypothetical correction was never submitted, frozen, reviewed or executed."]}
    destination = Path(__file__).resolve().parent / "regression_results.json"
    destination.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"result": str(destination), "finite_counts": result["finite_counts"]}))


if __name__ == "__main__":
    main()
