"""Compile only the fixed reviewed K02 source metadata to exclusive artifacts.

This entrypoint has no input-path or runtime override. It verifies the reviewed
snapshot, never reads patient data, and never invokes fit/sample/collect/freeze.
"""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
CASE = HERE.parent
PROJECT = CASE.parents[2]
sys.path.insert(0, str(PROJECT))
from source_compiler import compile_source_packet, canonical


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main():
    snapshot_path = CASE / "REVIEWED_DESIGN_SNAPSHOT.json"
    snapshot = read(snapshot_path)
    for relative, expected in snapshot["files"].items():
        path = CASE / relative
        if sha(path) != expected:
            raise ValueError("Protected reviewed artifact changed: " + relative)
    source = CASE / "request/sources/greiner_source_packet.json"
    task_path = CASE / "request/task_template.json"
    source_bytes = source.read_bytes()
    compiled = compile_source_packet(source_bytes, read(task_path), expected_packet_sha256=snapshot["files"]["request/sources/greiner_source_packet.json"])
    destination = HERE / "compiled"
    destination.mkdir(exist_ok=False)
    for name, value in {
        "evidence.json": compiled["evidence"], "record_provenance.json": compiled["record_provenance"],
        "source_context_templates.json": compiled["source_context_templates"], "dispositions.json": compiled["dispositions"],
        "s01_normalized_constraints.json": compiled["s01_normalized_constraints"], "s01_normalization_records.json": compiled["s01_normalization_records"],
        "source_issues.json": compiled["source_issues"], "registration_requirements.json": compiled["registration_requirements"],
    }.items():
        with (destination / name).open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.write("\n")
    report = {"schema_version": 1, "kind": "k02_metadata_only_source_compilation", "source_packet_sha256": compiled["source_packet_sha256"],
        "task_file_sha256": sha(task_path), "reviewed_snapshot_sha256": sha(snapshot_path),
        "s01_normalized_constraints_sha256": compiled["s01_normalized_constraints_sha256"],
        "compiled_files": {p.name: sha(p) for p in sorted(destination.iterdir())}, "counts": compiled["counts"], "readiness": compiled["readiness"],
        "compiler_sha256": {name: sha(HERE / name) for name in ("source_compiler.py", "compile_metadata.py")},
        "target_rows_read": 0, "source_checks_computed": 0, "actual_source_fit": False, "clinical_candidate_frozen": False,
        "reviewed_files_verified_before_and_after": len(snapshot["files"])}
    for relative, expected in snapshot["files"].items():
        if sha(CASE / relative) != expected:
            raise ValueError("Protected reviewed artifact changed during compile: " + relative)
    with (destination / "COMPILATION_REPORT.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"status": "metadata_only_compiled", "counts": compiled["counts"], "reviewed_files_verified": len(snapshot["files"])}, indent=2))


if __name__ == "__main__":
    main()
