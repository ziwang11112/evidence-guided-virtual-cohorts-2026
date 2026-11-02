"""Recompile metadata in memory and bind unchanged artifacts after code review.

Preserves the original compilation report and its truthful original code hash.
Only S01's input-schema validator is used; fit_reference/sample are never called.
"""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
CASE = HERE.parent
sys.path.insert(0, str(CASE.parents[2]))
sys.path.insert(0, str(CASE / "implementation"))
from source_compiler import compile_source_packet, canonical
from statistical_reference import _validate_constraints


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main():
    snapshot_path = CASE / "REVIEWED_DESIGN_SNAPSHOT.json"
    snapshot = read(snapshot_path)
    for name, expected in snapshot["files"].items():
        if sha(CASE / name) != expected:
            raise ValueError("Protected artifact changed: " + name)
    compiled = HERE / "compiled"
    original = read(compiled / "COMPILATION_REPORT.json")
    for name, expected in original["compiled_files"].items():
        if sha(compiled / name) != expected:
            raise ValueError("Original compiled artifact changed: " + name)
    result = compile_source_packet((CASE / "request/sources/greiner_source_packet.json").read_bytes(), read(CASE / "request/task_template.json"),
        expected_packet_sha256=snapshot["files"]["request/sources/greiner_source_packet.json"])
    for name, key in {"evidence.json": "evidence", "record_provenance.json": "record_provenance", "source_context_templates.json": "source_context_templates",
        "dispositions.json": "dispositions", "s01_normalized_constraints.json": "s01_normalized_constraints", "s01_normalization_records.json": "s01_normalization_records",
        "source_issues.json": "source_issues", "registration_requirements.json": "registration_requirements"}.items():
        if canonical(read(compiled / name)) != canonical(result[key]):
            raise ValueError("Recompiled metadata differs: " + name)
    if canonical(_validate_constraints(result["s01_normalized_constraints"])) != canonical(result["s01_normalized_constraints"]):
        raise ValueError("S01 normalized input schema differs")
    numeric_dispositions = [d for d in result["dispositions"] if d["disposition"] in {
        "potential_direct_supplemental_descriptive_diagnostic", "unavailable_derived_non_hdl_not_task_column"}]
    report = {"schema_version": 1, "kind": "k02_source_metadata_recompilation_verification", "status": "passed",
        "original_compilation_report_sha256": sha(compiled / "COMPILATION_REPORT.json"), "original_report_preserved": True,
        "current_compiler_sha256": sha(HERE / "source_compiler.py"), "verification_script_sha256": sha(Path(__file__)),
        "source_packet_sha256": result["source_packet_sha256"], "reviewed_snapshot_sha256": sha(snapshot_path),
        "compiled_files": original["compiled_files"], "all_recompiled_metadata_identical": True,
        "counts_from_actual_dispositions": result["counts"], "numerical_candidates_dispositioned": len(numeric_dispositions),
        "s01_input_schema_validated_without_fitting": True,
        "s01_normalized_constraints_sha256": result["s01_normalized_constraints_sha256"],
        "source_checks_computed": 0, "source_parameters_fitted": 0, "sampled_rows": 0,
        "clinical_candidate_frozen": False, "target_rows_read": 0, "protected_files_verified": len(snapshot["files"])}
    for name, expected in snapshot["files"].items():
        if sha(CASE / name) != expected:
            raise ValueError("Protected artifact changed during validation: " + name)
    with (HERE / "COMPILER_VERIFICATION.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"status": "passed", "all_recompiled_metadata_identical": True, "numerical_candidates_dispositioned": len(numeric_dispositions),
        "s01_schema_only_validated": True, "protected_files_verified": len(snapshot["files"])}, indent=2))


if __name__ == "__main__":
    main()
