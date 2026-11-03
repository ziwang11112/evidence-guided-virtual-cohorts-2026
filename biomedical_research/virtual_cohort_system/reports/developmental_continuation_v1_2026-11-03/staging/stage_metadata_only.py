"""One-shot staging of two explicitly reused laws; no freeze or execution."""
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
STAGING = Path(__file__).resolve().parent
PROJECT = STAGING.parents[2]
WORKSPACE = PROJECT.parents[1]
PREFLIGHT_DIR = PROJECT / "work/qualified_author_preflight_v1_2026-11-03"
sys.path.insert(0, str(PREFLIGHT_DIR))
import qualified_author_preflight as preflight

BASE_FILES = ("task.json", "registry.json", "input/AUTHOR_TASK.md", "input/compiled_evidence.json",
              "input/PROTOCOL.md", "sources/evidence_packet.json", "sources/NGSP_UNITS.md")
SCIENTIFIC_FILES = ("generator.py", "model_spec.json", "evidence.json", "decision.md", "analysis_evidence.json",
                    "evidence_use_v1.json", "scientific_validity_v1.json", "support_selection_v1.json",
                    "context_bridge_v1.json", "context_eligibility.json")
SUPPLEMENT = "technical_alias_preflight_v1.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def copy_new(source, destination, allowed_root):
    assert destination.resolve().is_relative_to(allowed_root.resolve())
    assert not destination.exists()
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    assert sha(source) == sha(destination)


def validate(bundle, candidate):
    command = [sys.executable, "-B", "-m", "cohort_harness", "validate", "--bundle", str(bundle), "--candidate", candidate]
    result = subprocess.run(command, cwd=PROJECT, text=True, capture_output=True, check=False)
    report = {"command": command, "cwd": str(PROJECT), "exit_code": result.returncode,
              "stdout": result.stdout, "stderr": result.stderr}
    assert result.returncode == 0, report
    parsed = json.loads(result.stdout)
    assert parsed == {"contract": "valid", "route": "program", "generator_executed": False,
                      "scientific_validity": "not_assessed"}, parsed
    report["result"] = parsed
    return report


def stage_author(author):
    old_bundle = WORKSPACE / "evcDP" / author
    new_bundle = WORKSPACE / "evcDC" / author
    assert not new_bundle.exists(), "Refusing to overwrite staging: " + str(new_bundle)
    old = old_bundle / "candidates/initial_interface"
    old_freeze_path = old / "freeze.json"
    first_freeze_path = old_bundle / "candidates/initial/freeze.json"
    old_freeze, first_freeze = read(old_freeze_path), read(first_freeze_path)
    assert old_freeze["parent"]["sha256"] == sha(first_freeze_path)
    frozen_files = old_freeze["candidate_files"]
    names = sorted(Path(name).name for name in frozen_files)
    assert len(names) == 14 and len(set(names)) == 14
    assert {path.name for path in old.iterdir()} == set(names) | {"freeze.json"}
    old_hashes = {name: sha(old / name) for name in names}
    for name in names:
        assert old_hashes[name] == old_freeze["commitments"]["candidates/initial_interface/" + name]
    assert read(old_bundle / "task.json")["budget"]["revisions"] == 2
    base_hashes = {name: sha(old_bundle / name) for name in BASE_FILES}
    new_bundle.mkdir(parents=True, exist_ok=False)
    for name in BASE_FILES:
        copy_new(old_bundle / name, new_bundle / name, new_bundle)
    seed, initial = (new_bundle / "candidates" / name for name in ("reused_parent", "initial"))
    for name in names:
        copy_new(old / name, seed / name, new_bundle)
        copy_new(old / name, initial / name, new_bundle)

    old_plan = read(old / "qualified_plan_v1.json")
    corrected = copy.deepcopy(old_plan)
    declaration = corrected["contexts"]["J"]
    assert all(context["bindings"] == {} for context in corrected["contexts"].values())
    assert len(declaration["checks"]) == 2
    ids = declaration["checks"][0]["measurement_mapping"]["assumption_ids"][:]
    known = {value["id"] for value in read(initial / "model_spec.json")["assumptions"]}
    assert set(ids) <= known and "A_MEASUREMENT" in ids
    alias_index = len(declaration["column_aliases"])
    alias = {"source_name": "HbA1c_percent", "generated_name": "hba1c", "assumption_ids": ids}
    assert all(value["source_name"] != alias["source_name"] for value in declaration["column_aliases"])
    declaration["column_aliases"].append(alias)
    delta = [{"op": "add", "path": "/contexts/J/column_aliases/" + str(alias_index), "value": alias}]
    for index, check in enumerate(declaration["checks"]):
        assert check["measurement_mapping"]["input_column"] == "hba1c"
        assert check["measurement_mapping"]["assumption_ids"] == ids
        check["measurement_mapping"]["input_column"] = "HbA1c_percent"
        delta.append({"op": "replace", "path": f"/contexts/J/checks/{index}/measurement_mapping/input_column",
                      "before": "hba1c", "after": "HbA1c_percent"})
    inverted = copy.deepcopy(corrected)
    inverted["contexts"]["J"]["column_aliases"].pop()
    for check in inverted["contexts"]["J"]["checks"]:
        check["measurement_mapping"]["input_column"] = "hba1c"
    assert inverted == old_plan
    (initial / "qualified_plan_v1.json").write_text(json.dumps(corrected, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    reused_preflight = preflight.preflight(new_bundle, "reused_parent")
    corrected_preflight = preflight.preflight(new_bundle, "initial")
    assert reused_preflight["counts"]["findings"] == 2
    assert corrected_preflight["status"] == "metadata_checks_passed"
    assert corrected_preflight["counts"]["checks_passed"] == 4
    preserved = {name: {"old": old_hashes[name], "reused_parent": sha(seed / name), "initial": sha(initial / name)}
                 for name in SCIENTIFIC_FILES}
    assert all(len(set(value.values())) == 1 for value in preserved.values())
    supplementary = {"kind": "technical_alias_correction_preflight_v1", "scope": "source_only_metadata",
        "reused_scientific_author": author, "fresh_scientific_authors": 0, "scientific_changes": 0,
        "old_corrected_candidate": str(old), "old_corrected_freeze_sha256": sha(old_freeze_path),
        "metadata_delta": delta, "scientific_file_preservation": preserved, "preflight": corrected_preflight,
        "generator_executed": False, "tables_generated": 0, "independent_approval": "not_provided",
        "limitations": ["Historical check reports are retained unchanged, not reinterpreted as checks of this alias correction.",
                        "Metadata success does not establish source correctness, moments, support, transport or full lifecycle approval."]}
    write_new(initial / SUPPLEMENT, supplementary)
    old_checks = read(old / "checks.json")
    checks = copy.deepcopy(old_checks)
    checks["records"].append({"name": "continuation_native_hba1c_alias_metadata", "status": "pass",
        "detail": "Read-only qualified author preflight passed all four checks after the J native alias correction. Exact scientific file hashes and the inverse JSON delta were checked. Historical reports remain unchanged. No generator import/execution, sampling, freeze, bridge or independent approval occurred."})
    checks["artifacts"].append({"path": SUPPLEMENT, "sha256": sha(initial / SUPPLEMENT)})
    (initial / "checks.json").write_text(json.dumps(checks, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    assert checks["records"][:-1] == old_checks["records"] and checks["artifacts"][:-1] == old_checks["artifacts"]
    assert all(sha(initial / artifact["path"]) == artifact["sha256"] for artifact in checks["artifacts"])
    validations = {candidate: validate(new_bundle, candidate) for candidate in ("reused_parent", "initial")}
    new_hashes = {name: sha(initial / name) for name in names}
    seed_hashes = {name: sha(seed / name) for name in names}
    assert seed_hashes == old_hashes
    assert {name for name in names if old_hashes[name] != new_hashes[name]} == {"qualified_plan_v1.json", "checks.json"}
    assert {name: sha(old / name) for name in names} == old_hashes
    assert {name: sha(new_bundle / name) for name in BASE_FILES} == base_hashes
    assert not (seed / "freeze.json").exists() and not (initial / "freeze.json").exists()
    report = {"author": author, "new_bundle": str(new_bundle),
        "provenance_mapping": {"old_initial_freeze": str(first_freeze_path), "old_initial_freeze_sha256": sha(first_freeze_path),
            "old_initial_revision_index": first_freeze["revision_index"], "old_corrected_freeze": str(old_freeze_path),
            "old_corrected_freeze_sha256": sha(old_freeze_path), "old_corrected_revision_index": old_freeze["revision_index"],
            "new_reused_parent": str(seed), "planned_reused_parent_revision_index": 0,
            "new_initial": str(initial), "planned_initial_revision_index": 1,
            "planned_branch_revision_index": 2, "unchanged_task_revision_budget": 2,
            "new_freeze_status": "not_frozen", "new_initial_revision_kind_proposed": "retain"},
        "base_copies": [{"path": name, "sha256": value} for name, value in base_hashes.items()],
        "base_copy_scope": "Only task/registry and five explicit input/source metadata files; protocol/author input copies await root continuation release update.",
        "old_14_to_reused_parent_to_initial": [{"path": name, "old_sha256": old_hashes[name],
            "reused_parent_sha256": seed_hashes[name], "initial_sha256": new_hashes[name],
            "changed_in_initial": old_hashes[name] != new_hashes[name]} for name in names],
        "added_initial_artifact": {"path": SUPPLEMENT, "sha256": sha(initial / SUPPLEMENT)},
        "qualified_plan_json_delta": delta, "inverse_delta_restores_original_json": True,
        "old_candidate_files_unchanged": True, "old_historical_reports_retained_byte_identically": True,
        "reused_parent_preflight": reused_preflight, "initial_preflight": corrected_preflight,
        "actual_validate_results": validations}
    write_new(STAGING / f"{author}_DELTA.json", report)
    return report


def main():
    reports = [stage_author(author) for author in ("A01", "A02")]
    manifest = {"kind": "developmental_continuation_metadata_staging_v1", "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "staged_not_frozen_not_approved_not_executed", "scope": "Two reused scientific candidates with one native-name interface correction each.",
        "fresh_scientific_authors": 0, "reused_scientific_authors": 2, "scientific_changes": 0,
        "generator_executions": 0, "generated_tables": 0, "new_freezes": 0, "new_bridges": 0, "independent_approvals_created": 0,
        "actual_validate_invocations": 4, "qualified_preflight_invocations": 4,
        "preflight_dispositions": {"reused_parent_expected_failures": 2, "corrected_initial_passes": 2},
        "old_phase": "Closed; zero draws. This staging does not alter its disposition or budget.",
        "new_execution_budget": "Prospective; root-owned release and independent review remain required.",
        "staging_script_sha256": sha(__file__), "preflight_dependencies": preflight.dependency_fingerprints(),
        "authors": [{"author": report["author"], "bundle": report["new_bundle"], "provenance": report["provenance_mapping"],
            "delta_report": str(STAGING / (report["author"] + "_DELTA.json")),
            "delta_report_sha256": sha(STAGING / (report["author"] + "_DELTA.json"))} for report in reports],
        "limitations": ["Structural/metadata validation is not independent scientific or lifecycle approval.",
            "No fresh blind construction or biomedical quality improvement is claimed.",
            "Root will update copied protocol/author instructions, register the prospective release, and decide freeze/review/execution."]}
    write_new(STAGING / "STAGING_MANIFEST.json", manifest)
    print(json.dumps({"status": manifest["status"], "bundles": [report["new_bundle"] for report in reports],
                      "actual_validate_invocations": 4, "qualified_preflight_invocations": 4, "generator_executions": 0}))


if __name__ == "__main__":
    main()
