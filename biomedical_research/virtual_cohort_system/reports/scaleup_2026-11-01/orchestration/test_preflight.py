"""Fabricated metadata only. Never run a generator or open participant data."""
import copy
import importlib.util
import json
from pathlib import Path
import socket
import subprocess
import sys

import pytest

MODULE_PATH = Path(__file__).with_name("preflight.py")
spec = importlib.util.spec_from_file_location("scaleup_preflight", MODULE_PATH)
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
PLAN = Path(__file__).resolve().parents[1] / "campaign_plan.json"


def write(root, path, value):
    destination = root / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(value, indent=2) + "\n").encode()
    destination.write_bytes(data)
    return {"path": path, "sha256": p.digest(data)}


def commit(root, plan, release):
    plan_ref = write(root, "plan.json", plan)
    release["plan_sha256"] = plan_ref["sha256"]
    payload = {k: v for k, v in release.items() if k != "independent_review"}
    review = {"schema_version": 1, "decision": "approved", "independent": True,
              "reviewer_id": "reviewer", "coordinator_id": "coordinator", "reviewed_utc": "2026-11-01T00:00:00Z",
              "reason": "Invented metadata fixture only", "approved_release": copy.deepcopy(payload)}
    release["independent_review"] = write(root, "review.json", review)
    write(root, "readiness.json", release)


@pytest.fixture
def released(tmp_path):
    # Existing plan is metadata. No old controller or scientific code is imported.
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    plan["campaign_status"] = "released"
    plan["execution_enabled"] = True
    plan["counts"]["admitted_cohorts"] = 4
    design = b"Invented prospective design fixture.\n"
    (tmp_path / "design.md").write_bytes(design)
    plan["design_sha256"] = p.digest(design)
    engine = tmp_path / "cohort_harness/semantic_feedback_v1.py"
    engine.parent.mkdir()
    engine.write_text("raise RuntimeError('Never import this fixture')\n", encoding="utf-8")
    release = {"schema_version": 1, "campaign_id": p.CAMPAIGN, "status": "released", "plan_sha256": None,
               "design": {"path": "design.md", "sha256": p.digest(design)},
               "feedback_engine": {"name": "semantic_feedback_v1", "legacy_fallback": False,
                                   "artifact": {"path": "cohort_harness/semantic_feedback_v1.py", "sha256": p.digest(engine.read_bytes())}},
               "required_gates": {k: True for k in sorted(p.GATES)}, "cases": [], "independent_review": None}
    for index, case in enumerate(plan["cohorts"]):
        identity = f"invented-case-{index + 1}"
        case.update(actual_case_id=identity, study_family=f"invented-family-{index + 1}", admission_status="admitted",
                    reference_exposure_status="unexposed", authorized_release=f"case-release-{index + 1}")
        prefix = f"metadata/{case['cohort_slot']}"
        task = {"task_id": identity, "mode": "whole_cohort", "n_rows": 5000, "budget": {"revisions": 1},
                "information_policy": {"mode": "published_evidence"}, "columns": [{"role": "generated"}]}
        case["task_contract"] = write(tmp_path, prefix + "/task.json", task)
        case["evidence_packet"] = write(tmp_path, prefix + "/evidence.json", {"note": "Invented study metadata, no clinical values"})
        # A nested reference must NEVER be followed, even for a valid release.
        case["analysis_plan"] = write(tmp_path, prefix + "/analysis.json",
                                      {"primary_analysis_ids": ["P1", "P2", "P3"], "input_files": ["forbidden.csv"]})
        baseline = {"schema_version": 1, "case_id": identity, "task_contract": case["task_contract"],
                    "evidence_packet": case["evidence_packet"], "target_row_fitting": False,
                    "source_feedback_rounds": 1, "extra_simulation_calls": 0,
                    "family": "Fixture only", "fitting_rule": "Fixed aggregate rule", "unhandled_constraints": "None in fixture"}
        exposure = {"schema_version": 1, "case_id": identity, "classification": "unexposed", "decision": "approved",
                    "independent": True, "reviewer_id": "exposure-reviewer", "coordinator_id": "coordinator",
                    "reviewed_utc": "2026-11-01T00:00:00Z", "reason": "Invented independently reviewed scope",
                    "prospective_exclusions_applied": False, "approved_primary_analysis_ids": ["P1", "P2", "P3"],
                    "exposed_scope": [], "excluded_scope": []}
        gate = {"schema_version": 1, "case_id": identity, "independent_validation_eligible": True,
                "exposure_review": write(tmp_path, prefix + "/exposure.json", exposure),
                "source_overlap_reviewed": True, "adapters_reviewed": True,
                "target_access": "closed_pending_separate_evaluation_release", "quantitative_use_bundle": "Prospective fixture criterion",
                "all_five_constructor_rule": "All five represented; no selection", "primary_analysis_count": 3, "secondary_analysis_count": 2}
        release["cases"].append({"cohort_slot": case["cohort_slot"], "actual_case_id": identity,
                                 "release_id": case["authorized_release"],
                                 "reference_arm": write(tmp_path, prefix + "/reference.json", baseline),
                                 "case_gate": write(tmp_path, prefix + "/gate.json", gate)})
    commit(tmp_path, plan, release)
    return tmp_path, plan, release


def result(fixture):
    return p.preflight(fixture[0], "plan.json", "readiness.json")


def forbid_artifact_reads(monkeypatch):
    original = p.Reader.read
    def guarded(self, relative, suffixes=(".json",)):
        assert relative == "plan.json", f"Premature artifact read: {relative}"
        return original(self, relative, suffixes)
    monkeypatch.setattr(p.Reader, "read", guarded)


def test_actual_plan_blocks_before_release_read(tmp_path, monkeypatch):
    (tmp_path / "plan.json").write_bytes(PLAN.read_bytes())
    forbid_artifact_reads(monkeypatch)
    report = p.preflight(tmp_path, "plan.json", "forbidden.csv")
    assert report["status"] == "blocked" and report["inventory_valid"]
    assert report["counts"]["planned_slots"] == 144
    assert report["metadata_files_read"] == ["plan.json"]


@pytest.mark.parametrize("mutation", ["null_id", "placeholder", "closed", "duplicate", "exposed", "family"])
def test_unadmitted_identity_stops_before_artifacts(released, monkeypatch, mutation):
    root, plan, release = released
    case = plan["cohorts"][0]
    if mutation == "null_id": case["actual_case_id"] = None
    if mutation == "placeholder": case["actual_case_id"] = "placeholder-1"
    if mutation == "closed": case["actual_case_id"] = "chns-2009-evidence-only-whole-cohort-f2"
    if mutation == "duplicate": case["actual_case_id"] = plan["cohorts"][1]["actual_case_id"]
    if mutation == "exposed": case["reference_exposure_status"] = "revealed"
    if mutation == "family":
        for item in plan["cohorts"]: item["study_family"] = "same-family"
    commit(root, plan, release)
    forbid_artifact_reads(monkeypatch)
    assert result(released)["status"] == "blocked"


@pytest.mark.parametrize("mutation", ["duplicate_id", "seed", "arm", "stage", "missing", "count", "bool", "resource"])
def test_schedule_and_counts_fail_closed(released, mutation):
    root, plan, release = released
    if mutation == "duplicate_id": plan["slots"][1]["slot_id"] = plan["slots"][0]["slot_id"]
    if mutation == "seed": plan["slots"][0]["seed"] = 999
    if mutation == "arm": plan["slots"][0]["method_arm"] = "statistical_reference"
    if mutation == "stage": plan["slots"][0]["stage"] = "extra_revision"
    if mutation == "missing": plan["slots"].pop()
    if mutation == "count": plan["counts"]["planned_slots"] = 143
    if mutation == "bool": plan["budget"]["source_feedback_rounds_per_construction"] = True
    if mutation == "resource": plan["budget"]["hpc"] = True
    commit(root, plan, release)
    report = result(released)
    assert report["status"] == "blocked" and not report["inventory_valid"]


@pytest.mark.parametrize("path", ["../outside.json", "/absolute.json", "C:/target.json", "//server/share.json",
                                  "metadata/*.json", "metadata/aux.json", "metadata/end./x.json", "metadata/x.json ",
                                  "metadata/target.csv", "metadata/target.sas7bdat"])
def test_unsafe_paths_rejected_before_open(tmp_path, monkeypatch, path):
    reader = p.Reader(tmp_path)
    def forbidden(*args, **kwargs): raise AssertionError("Unsafe artifact was opened")
    monkeypatch.setattr(Path, "open", forbidden)
    with pytest.raises(p.NotReady): reader.read(path)


def test_symlink_and_hardlink_rejected(tmp_path):
    origin = tmp_path / "origin.json"
    origin.write_text("{}")
    link = tmp_path / "link.json"
    try:
        link.symlink_to(origin)
    except OSError:
        pass  # Windows may deny symlink creation; hardlink check still runs.
    else:
        with pytest.raises(p.NotReady): p.Reader(tmp_path).read("link.json")
        link.unlink()
    link.hardlink_to(origin)
    with pytest.raises(p.NotReady): p.Reader(tmp_path).read("link.json")


def retain_pair(plan):
    origin, alias = plan["slots"][0], plan["slots"][3]
    origin.update(status="success", candidate_hash="a" * 64, execution_id="fixture-run", output_hash="b" * 64)
    alias.update(status="retained", candidate_hash="a" * 64, output_hash="b" * 64, retained_from=origin["slot_id"])
    plan["counts"].update(attempted_slots=1, successful_slots=1, not_run_slots=142, retained_aliases=1, unique_outputs=1)
    return origin, alias


def test_retention_counts_alias_without_extra_execution(released):
    root, plan, release = released
    retain_pair(plan)
    commit(root, plan, release)
    report = result(released)
    assert report["status"] == "ready_metadata_only"
    assert report["counts"]["attempted_slots"] == 1 and report["counts"]["unique_outputs"] == 1


@pytest.mark.parametrize("mutation", ["cross_seed", "cross_case", "cycle", "hash", "new_run", "failed_origin"])
def test_invalid_retention_rejected(released, mutation):
    root, plan, release = released
    origin, alias = retain_pair(plan)
    if mutation == "cross_seed": alias["retained_from"] = plan["slots"][1]["slot_id"]
    if mutation == "cross_case": alias["retained_from"] = "K02_A01_initial_2101"
    if mutation == "cycle": alias["retained_from"] = alias["slot_id"]
    if mutation == "hash": alias["output_hash"] = "c" * 64
    if mutation == "new_run": alias["execution_id"] = "extra-run"
    if mutation == "failed_origin": origin.update(status="failed", output_hash=None)
    commit(root, plan, release)
    assert result(released)["status"] == "blocked"


@pytest.mark.parametrize("mutation", ["different_candidate", "mix_retained_executed"])
def test_one_scientific_candidate_and_decision_per_stage(released, mutation):
    root, plan, release = released
    retain_pair(plan)
    extra = plan["slots"][1] if mutation == "different_candidate" else plan["slots"][4]
    extra.update(status="success", candidate_hash=("c" if mutation == "different_candidate" else "a") * 64,
                 execution_id="extra-run", output_hash="d" * 64)
    plan["counts"].update(attempted_slots=2, successful_slots=2, not_run_slots=141, unique_outputs=2)
    commit(root, plan, release)
    assert result(released)["status"] == "blocked"


@pytest.mark.parametrize("mutation", ["stale_hash", "legacy", "fallback", "gate", "release_disabled", "target_fitting",
                                     "missing_use_rule", "target_open", "same_reviewer", "wrong_review_payload"])
def test_release_and_information_gates(released, mutation):
    root, plan, release = released
    if mutation == "stale_hash": plan["cohorts"][0]["task_contract"]["sha256"] = "f" * 64
    if mutation == "legacy": release["feedback_engine"]["name"] = "whole_cohort_feedback"
    if mutation == "fallback": release["feedback_engine"]["legacy_fallback"] = True
    if mutation == "gate": release["required_gates"]["case_adapters_reviewed"] = False
    if mutation == "release_disabled": release["status"] = "draft"
    if mutation in {"target_fitting", "missing_use_rule", "target_open"}:
        field = "reference_arm" if mutation == "target_fitting" else "case_gate"
        ref = release["cases"][0][field]
        value = json.loads((root / ref["path"]).read_text())
        if mutation == "target_fitting": value["target_row_fitting"] = True
        if mutation == "missing_use_rule": value["all_five_constructor_rule"] = ""
        if mutation == "target_open": value["target_access"] = "open"
        release["cases"][0][field] = write(root, ref["path"], value)
    commit(root, plan, release)
    if mutation in {"same_reviewer", "wrong_review_payload"}:
        review = json.loads((root / "review.json").read_text())
        if mutation == "same_reviewer": review["reviewer_id"] = "coordinator"
        else: review["approved_release"]["status"] = "draft"
        release["independent_review"] = write(root, "review.json", review)
        write(root, "readiness.json", release)
    assert result(released)["status"] == "blocked"


@pytest.mark.parametrize("mutation", ["qualified", "participant_exclusion", "unmapped", "approved_exposed",
                                     "approved_excluded", "wrong_primary", "unreviewed", "same_reviewer",
                                     "hidden_exposure", "qualification_mismatch", "not_prospective"])
def test_scoped_exposure_qualification(released, mutation):
    root, plan, release = released
    case = plan["cohorts"][0]
    case["reference_exposure_status"] = "qualified_after_prospective_exclusions"
    gate_ref = release["cases"][0]["case_gate"]
    gate = json.loads((root / gate_ref["path"]).read_text())
    review_ref = gate["exposure_review"]
    review = json.loads((root / review_ref["path"]).read_text())
    scope = {"scope_id": "previously_seen_relationship", "description": "Invented exposed relationship excluded prospectively",
             "analysis_ids": ["old_lifestyle_effect"]}
    review.update(classification="qualified_after_prospective_exclusions", prospective_exclusions_applied=True,
                  exposed_scope=[copy.deepcopy(scope)], excluded_scope=[copy.deepcopy(scope)])
    if mutation == "participant_exclusion":
        for item in (*review["exposed_scope"], *review["excluded_scope"]):
            item.update(scope_id="overlapping_participant_group", description="Invented overlapping participant scope excluded", analysis_ids=[])
    if mutation == "unmapped": review["excluded_scope"][0]["scope_id"] = "unrelated_scope"
    if mutation == "approved_exposed": review["exposed_scope"][0]["analysis_ids"].append("p1")
    if mutation == "approved_excluded": review["excluded_scope"][0]["analysis_ids"].append("P1")
    if mutation == "wrong_primary": review["approved_primary_analysis_ids"] = ["P1", "P2", "P4"]
    if mutation == "unreviewed": review["independent"] = False
    if mutation == "same_reviewer": review["reviewer_id"] = "coordinator"
    if mutation == "hidden_exposure":
        case["reference_exposure_status"] = review["classification"] = "unexposed"
    if mutation == "qualification_mismatch": review["classification"] = "unexposed"
    if mutation == "not_prospective": review["prospective_exclusions_applied"] = False
    gate["exposure_review"] = write(root, review_ref["path"], review)
    release["cases"][0]["case_gate"] = write(root, gate_ref["path"], gate)
    commit(root, plan, release)
    report = result(released)
    assert report["status"] == ("ready_metadata_only" if mutation in {"qualified", "participant_exclusion"} else "blocked")
    assert report["target_data_accessed"] is report["execution_authorized"] is False


def test_success_has_no_execution_network_import_or_nested_reads(released, monkeypatch):
    root, _, _ = released
    original = p.Reader.read
    def guarded(self, relative, suffixes=(".json",)):
        assert relative != "forbidden.csv"
        return original(self, relative, suffixes)
    def forbidden(*args, **kwargs): raise AssertionError("Unexpected execution/network")
    monkeypatch.setattr(p.Reader, "read", guarded)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    before = set(sys.modules)
    report = result(released)
    assert report["status"] == "ready_metadata_only"
    assert report["execution_authorized"] is report["generator_executed"] is report["target_data_accessed"] is False
    assert not any(name.startswith("cohort_harness") for name in set(sys.modules) - before)
    assert "forbidden.csv" not in report["metadata_files_read"]
    assert not (root / "executions").exists()


@pytest.mark.parametrize("data", [b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":1e999}', b'[]'])
def test_strict_json(data):
    with pytest.raises(p.NotReady): p.decode(data)


def test_cli_emits_machine_readable_blocked_result(tmp_path, capsys):
    (tmp_path / "plan.json").write_bytes(PLAN.read_bytes())
    assert p.main(["--project-root", str(tmp_path), "--plan", "plan.json"]) == 2
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "blocked" and report["counts"]["planned_slots"] == 144


def test_recursive_invalid_json_is_machine_readable_blocked(tmp_path):
    (tmp_path / "plan.json").write_text('{"nested":' + '[' * 3000 + '0' + ']' * 3000 + '}')
    report = p.preflight(tmp_path, "plan.json")
    assert report["status"] == "blocked" and not report["inventory_valid"]
