"""Read-only C4 public-metadata audit; never imports candidates or opens custody."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


parser = argparse.ArgumentParser()
parser.add_argument("--root", type=Path, required=True)
parser.add_argument("--protocol", required=True)
parser.add_argument("--test-report", required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
root = args.root.resolve()
hashes = {}


def public(relative):
    path = (root / relative).resolve()
    assert path.is_relative_to(root), relative
    assert not path.is_relative_to(root / "custody"), "Custody access is forbidden"
    hashes[path.relative_to(root).as_posix()] = digest(path)
    return path


commitment = read(public("TASK_COMMITMENT.json"))
admission = read(public("SOURCE_ADMISSION.json"))
assert digest(root / "TASK_COMMITMENT.json") == admission["commitment_sha256"]
assert admission["decision"] == "admit_visible_artificial_source_contracts"
assert admission["hidden_content_opened_by_root"] is False
assert commitment["admission_document_sha256"] == digest(public("TASK_ADMISSION.md"))
assert commitment["visible_artifacts"] == admission["visible_artifacts"]
assert commitment["fixed_counts"] == {"initial_feedback": 6, "election": 24,
                                       "untouched_test": 24, "total": 54}
assert commitment["fixture_authoring_generated_rows"] == 0
assert commitment["n_rows"] == 4000
assert set(commitment["case_ids"]) == {"task_a", "task_b"}
initials = {}
for case, count in (("task_a", 9), ("task_b", 8)):
    rel = f"visible/{case}/source_contract.json"
    source_path = public(rel)
    assert digest(source_path) == commitment["visible_artifacts"][rel]
    source = read(source_path)
    assert source["case_id"] == case and source["task_id"] == "c4_" + case
    assert len(source["source_checks"]) == source["n_source_checks_per_table"] == count
    assert source["source_aggregate_loss"]["denominator_checks_per_seed"] == count
    assert source["source_aggregate_loss"]["denominator_election_seeds"] == 3
    assert source["source_aggregate_loss"]["exclude_or_drop_failed_checks"] is False
    assert {p["check_id"] for p in source["protected_uses"]} == {
        c["id"] for c in source["source_checks"] if c["kind"] == "correlation"}
    bundle = root / "b" / case
    assert digest(public(f"b/{case}/sources/source_contract.json")) == digest(source_path)
    task = read(public(f"b/{case}/task.json"))
    for key in ("task_id", "mode", "population", "n_rows", "row_id", "columns"):
        assert task[key] == source[key], (case, key)
    registry = read(public(f"b/{case}/registry.json"))
    assert registry["artifacts"] == [{"source_id": source["task_id"],
        "path": "sources/source_contract.json", "sha256": digest(source_path),
        "origin": "fixture", "screening": "approved"}]
    freeze_path = public(f"b/{case}/candidates/c0/freeze.json")
    freeze = read(freeze_path)
    assert freeze["parent"] is None and freeze["revision_index"] == 0
    assert freeze["route"] == "generator.py" and freeze["acceptance"] == "structural_only"
    for relative, expected in freeze["commitments"].items():
        assert digest(public(f"b/{case}/{relative}")) == expected, (case, relative)
    assert not (bundle / "observed.csv").exists()
    assert not list((bundle / "executions").glob("*")), "Scientific execution already attempted"
    initials[case] = {"name": "c0", "freeze_sha256": digest(freeze_path),
        "generator_sha256": digest(bundle / "candidates/c0/generator.py"),
        "spec_sha256": digest(bundle / "candidates/c0/model_spec.json")}

plan = read(public("method/plan.json"))
assert plan["scientific_run_budget"] == 54 and plan["deduplicate"] is False
assert plan["seeds"] == {"feedback": commitment["seeds"]["initial_feedback"],
                         "election": commitment["seeds"]["election"],
                         "test": commitment["seeds"]["untouched_test"]}
assert set(plan["cases"]) == set(initials)
for case, initial in initials.items():
    assert plan["cases"][case]["initial"] == initial
    assert plan["cases"][case]["source_sha256"] == hashes[f"visible/{case}/source_contract.json"]
    assert plan["cases"][case]["task_sha256"] == hashes[f"b/{case}/task.json"]
for name, expected in plan["engine"].items():
    path = public("method/controller.py") if name == "controller.py" else root.parent.parent / "cohort_harness" / name
    assert digest(path) == expected, name
public(args.protocol)
public("method/test_controller.py")
public("method/test_log.txt")
bindings = read(public("PREEXECUTION_BINDINGS.json"))
for key, relative in {"protocol_sha256": args.protocol,
    "task_commitment_sha256": "TASK_COMMITMENT.json",
    "source_admission_sha256": "SOURCE_ADMISSION.json", "plan_sha256": "method/plan.json",
    "controller_sha256": "method/controller.py", "test_log_sha256": "method/test_log.txt"}.items():
    assert bindings[key] == hashes[relative], key
assert bindings["scientific_execution_started"] is False
assert bindings["hidden_content_opened_by_root"] is False
assert bindings["initial_freezes"] == {c: v["freeze_sha256"] for c, v in initials.items()}
suite = ET.parse(public(args.test_report)).getroot().find("testsuite")
assert suite is not None and int(suite.attrib["tests"]) > 0
assert int(suite.attrib["errors"]) == int(suite.attrib["failures"]) == 0
assert not list((root / "stats").glob("*.json")), "Scientific diagnostics already exist"
result = {"status": "PASS", "scope": "public metadata only; no generator import or execution",
          "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "custody_content_opened": False, "scientific_execution_directories": 0,
          "test_suite": suite.attrib, "initial_candidates": initials,
          "bound_public_artifacts": hashes, "engine_hashes": plan["engine"]}
with args.output.open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(result, stream, indent=2, sort_keys=True)
    stream.write("\n")
print(json.dumps({"status": result["status"], "public_artifacts": len(hashes),
                  "test_count": int(suite.attrib["tests"]), "output": str(args.output)}))
