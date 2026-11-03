"""Invented fixtures only. No submitted generator or network process executes."""
import copy
import importlib.util
from pathlib import Path
import shutil
import socket
import subprocess
from types import SimpleNamespace

import pytest

import pilot_controller_v1 as pilot


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(pilot.bridge._bytes(value))
    return {"path": str(path.resolve()), "sha256": pilot.sha256(path)}


def review(digest):
    return {"decision": "approved", "independent": True, "reviewer_id": "invented-reviewer",
            "producer_id": "invented-author", "reviewed_utc": "2026-11-02T00:00:00Z",
            "reason": "Invented fixture approval, no real science", "approved_sha256": digest}


def domain(low="0", closed=False):
    return {"lower": low, "upper": None, "lower_closed": closed, "upper_closed": False}


@pytest.fixture
def release(tmp_path, monkeypatch):
    for owner, name in ((subprocess, "run"), (subprocess, "Popen"), (socket, "create_connection")):
        monkeypatch.setattr(owner, name, lambda *a, **k: pytest.fail("Process/network execution prohibited"))
    monkeypatch.setattr(pilot.runtime_check, "verify", lambda path: {"status": "invented_runtime"})
    public = write(tmp_path / "public.json", {"scope": "Invented only"})
    runtime = write(tmp_path / "runtime.json", {"scope": "Invented runtime"})
    contexts = ["source", "source2", "source3", "target"]
    contract = write(tmp_path / "support.json", {"required_contexts": contexts, "definition_ids": [],
        "required_checks": {c: [{"id": "positive", "variable": "x", "domain": domain()}] for c in contexts}})
    manifest = {"schema_version": 1, "kind": "developmental_revision_pilot_release", "ledger_directory": str(tmp_path / "ledger"),
        "protocol": public, "artifacts": [public], "engine_sha256": pilot.engine_hashes(), "runtime_identity": runtime,
        "support_contract": contract, "required_qualified_checks": [
            {"context_id": "source", "check_id": "q0"}, {"context_id": "source", "check_id": "q1"},
            {"context_id": "source2", "check_id": "q2"}, {"context_id": "source3", "check_id": "q3"}],
        "source_contexts": contexts[:-1], "target_context": "target", "source_seeds": [101, 102, 103],
        "target_seeds": [201, 202, 203], "n_rows": 3000,
        "execution_limits": {"timeout_seconds": 30, "memory_mb": 1024, "output_bytes": 2000000, "log_bytes": 10000},
        "author_allowance": {"candidate_bytes": 1048576, "generator_bytes": 65536, "schema_returns": 2},
        "evaluator": public, "evaluation": {
            "reference_report": {"path": str(tmp_path / "NEVER_OPEN_REFERENCE.json"), "sha256": "0" * 64},
            "independent_reference_report": {"path": str(tmp_path / "NEVER_OPEN_INDEPENDENT.json"), "sha256": "1" * 64}}}
    with monkeypatch.context() as temporary:
        temporary.setattr(pilot.lifecycle, "freeze_candidate", lambda *a, **k: None)
        inputs = old_fixture_module().bundle.__wrapped__(tmp_path / "input_template", monkeypatch, SimpleNamespace(param="ordinary"))
    task = pilot.read_json(inputs / "task.json")
    task["n_rows"] = 3000
    task["budget"]["revisions"] = 2
    write(inputs / "task.json", task)
    bound = {key: {"path": str(path), "sha256": pilot.sha256(path)} for key, path in
             (("task", inputs / "task.json"), ("evidence", inputs / "candidates/invented/evidence.json"), ("registry", inputs / "registry.json"))}
    manifest["initial_packet"] = write(tmp_path / "initial_packet.json", {"schema_version": 1, "kind": "pilot_initial_author_packet",
        **bound, "files": [*bound.values(), public, contract,
                           {"path": str(inputs / "sources/invented.txt"), "sha256": pilot.sha256(inputs / "sources/invented.txt")}]})
    manifest["review"] = review(pilot.release_digest(manifest))
    return manifest


def make_controller(release):
    return pilot.PilotController.create(release["ledger_directory"], release)


def old_fixture_module():
    path = pilot.REVISION_DIRECTORY / "test_revision_controller_v1.py"
    spec = importlib.util.spec_from_file_location("invented_revision_protocol_tests", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_candidate(tmp_path, monkeypatch, release, constructor="A01"):
    old = old_fixture_module()
    with monkeypatch.context() as temporary:
        temporary.setattr(pilot.lifecycle, "freeze_candidate", lambda *a, **k: None)
        root = old.bundle.__wrapped__(tmp_path, monkeypatch, SimpleNamespace(param="ordinary"))
    directory = root / "candidates/invented"
    task = pilot.read_json(root / "task.json")
    task.update(n_rows=3000)
    task["budget"]["revisions"] = 2
    write(root / "task.json", task)
    spec = pilot.read_json(directory / "model_spec.json")
    prototype = copy.deepcopy(spec["parameters"]["contexts"]["source"])
    for context in release["source_contexts"]:
        spec["parameters"]["contexts"][context] = {**copy.deepcopy(prototype), "n_rows": 3000}
    spec["parameters"]["contexts"]["target"]["n_rows"] = 3000
    write(directory / "model_spec.json", spec)
    plan = pilot.read_json(directory / pilot.bridge.PLAN)
    prototype = plan["contexts"][0]
    contexts = []
    for index, context in enumerate(release["source_contexts"]):
        child = copy.deepcopy(prototype)
        child.update(id=context, feedback_policy="semantic_v1", supplement=None)
        child["recipe"]["checks"][0]["id"] = f"native-geo-{index}"
        child["semantics"]["bindings"][0]["check_id"] = f"native-geo-{index}"
        contexts.append(child)
    plan["contexts"] = contexts + [plan["contexts"][1]]
    plan["trials"] = [{"id": s["run_id"], "context_id": s["context_id"], "seed": s["seed"], "n_rows": s["n_rows"]}
                      for s in pilot.planned_slots(release) if s["constructor"] == constructor and s["version"] == "initial"]
    plan["budget"] = {"source_attempts": 9, "source_rows": 27000, "target_attempts": 3, "target_rows": 9000}
    write(directory / pilot.bridge.PLAN, plan)
    wrapper = pilot.read_json(directory / "scientific_validity_v1.json")
    law = wrapper["context_laws"]["source"]
    wrapper["context_laws"] = {context: copy.deepcopy(law) for context in [*release["source_contexts"], "target"]}
    write(directory / "scientific_validity_v1.json", wrapper)
    provenance = [{"kind": "assumption", "id": "fixture"}]
    support = {"schema_version": "support_selection_v1", "contexts": {context: {
        "final_supports": {"x": {"domain": domain(), "provenance": provenance},
                           "y": {"domain": domain(closed=True), "provenance": provenance}},
        "native_views": {}, "selection": {"route": "direct_eligible_joint", "exclusion_implementation": "not_claimed",
            "conditioning_event": None, "description": "Invented eligible-law fixture", "provenance": provenance},
        "transformations": [], "derivations": []} for context in [*release["source_contexts"], "target"]}}
    write(directory / "support_selection_v1.json", support)
    pilot.lifecycle.freeze_candidate(root, directory)
    old.ready(root)
    return root, "candidates/invented", old


def register(controller, root, candidate, tmp_path, *, constructor="A01", version="initial", packet=None, action=None):
    assessment = write(tmp_path / f"{constructor}_{version}_support.json", pilot.support_assessment(root, candidate, controller.release))
    trace = write(tmp_path / f"{constructor}_{version}_trace.json", {"scope": "Invented dispatch/snapshot metadata"})
    provenance = {"actor_id": "invented-author", "context_id": constructor + "-" + version,
                  "packet_sha256": packet or controller.release["initial_packet"]["sha256"],
                  "author_turns": 1, "scientific_opportunities": 1, "model_calls": None, "output_tokens": None,
                  "schema_returns": 0, "author_trace": trace, "common_correction": None}
    controller.register_version(constructor, version, root, candidate,
                                {"assessment": assessment, "review": review(assessment["sha256"])}, provenance)


def eligibility_fixture(monkeypatch):
    """Only compatibility tests replace the qualified scientific gate; separately tested below."""
    monkeypatch.setattr(pilot.PilotController, "_source_eligibility", lambda self, inspected, phase, slots, packet: {
        "target_eligible": phase["status"] == "complete" and all(s["status"] == "success" for s in slots),
        "reasons": [], "qualified_coverage": [], "support_checks": [], "source_point_fit_required": False})


def close_other_versions(controller):
    controller.abort_version("A01", "self_review", "Invented branch excluded")
    controller.abort_version("A01", "source_feedback", "Invented branch excluded")
    controller.abort_version("A02", "initial", "Invented second constructor excluded")


def test_schedule_is_exact_and_same_seed_retained_versions(release):
    slots = pilot.planned_slots(release)
    assert len(slots) == 72 and sum(s["role"] == "target" for s in slots) == 18
    assert sum(s["n_rows"] for s in slots) == 216000
    for context in [*release["source_contexts"], release["target_context"]]:
        seeds = [{s["seed"] for s in slots if s["constructor"] == "A01" and s["version"] == v and s["context_id"] == context}
                 for v in pilot.VERSIONS]
        assert seeds[0] == seeds[1] == seeds[2]


def test_aborted_denominator_and_evaluation_barrier_never_read_references(release):
    controller = make_controller(release)
    with pytest.raises(ValueError):
        controller.authorize_evaluation(release["evaluator"]["sha256"])
    controller.abort_version("A01", "initial", "Invented failure")
    controller.abort_version("A02", "initial", "Invented failure")
    controller.freeze_scientific_inventory()
    with pytest.raises(ValueError):
        controller.abort_version("A01", "initial", "Forbidden repair")
    closed = controller.close_targets()
    assert len(closed["slots"]) == 72 and {s["status"] for s in closed["slots"]} == {"aborted"}
    with pytest.raises(ValueError):
        controller.verify_evaluation(release["evaluator"]["sha256"])
    controller.authorize_evaluation(release["evaluator"]["sha256"])
    verified = controller.verify_evaluation(release["evaluator"]["sha256"])
    assert verified["scientific_closed"] and verified["status"] == "closed"
    assert not Path(release["evaluation"]["reference_report"]["path"]).exists()
    (controller.directory / "evaluation").mkdir()
    (controller.directory / "independent_evaluation").mkdir()
    controller.verify_evaluation(release["evaluator"]["sha256"])


def test_mutated_protocol_and_wrong_release_review_rejected(release):
    bad = copy.deepcopy(release); bad["review"]["approved_sha256"] = "0" * 64
    with pytest.raises(ValueError):
        make_controller(bad)
    controller = make_controller(release)
    Path(release["protocol"]["path"]).write_text("changed", encoding="utf-8")
    with pytest.raises(ValueError):
        controller.verify()


def test_real_source_inventory_survives_parent_target_dispatch(tmp_path, monkeypatch, release):
    eligibility_fixture(monkeypatch)
    controller = make_controller(release)
    root, candidate, old = make_candidate(tmp_path / "data", monkeypatch, release)
    register(controller, root, candidate, tmp_path)
    events = old.worker(monkeypatch)
    with pytest.raises(ValueError):
        controller.dispatch_targets("A01", "initial")
    controller.dispatch_sources("A01", "initial")
    assert len(events) == 9
    before = pilot.source.source_feedback_packet(root, candidate)
    before_inventory = pilot.bridge._inventory(root / "context_bridge_v1/invented")
    close_other_versions(controller)
    controller.freeze_scientific_inventory()
    controller.dispatch_targets("A01", "initial")
    assert len(events) == 12
    assert pilot.source.source_feedback_packet(root, candidate) == before
    assert pilot.bridge._inventory(root / "context_bridge_v1/invented") == before_inventory
    assert pilot.bridge.verify(root, candidate)["status"] == "incomplete"
    with pytest.raises(ValueError):
        controller.dispatch_targets("A01", "initial")
    closed = controller.close_targets()
    assert sum(s["status"] == "success" for s in closed["slots"]) == 12
    assert sum(s["status"] == "aborted" for s in closed["slots"]) == 60


def test_nonnumerical_packet_and_decision_bind_actual_bytes(tmp_path, monkeypatch, release):
    controller = make_controller(release)
    root, candidate, old = make_candidate(tmp_path / "data", monkeypatch, release)
    register(controller, root, candidate, tmp_path)
    old.worker(monkeypatch)
    controller.dispatch_sources("A01", "initial")
    packet = controller.deliver_branch_packet("A01", "self_review")
    assert packet["manifest"]["numerical_feedback"] is False
    assert packet["manifest"]["source_feedback_sha256"] is None
    assert not (Path(packet["directory"]) / "initial_source_feedback.json").exists()
    decision = {"action": "stop", "packet_sha256": "0" * 64, "reason": "Invented", "addressed_findings": [], "remaining_limitations": []}
    with pytest.raises(ValueError):
        controller.record_branch_decision("A01", "self_review", decision)
    decision["packet_sha256"] = packet["packet_sha256"]
    controller.record_branch_decision("A01", "self_review", decision)
    numeric = controller.deliver_branch_packet("A01", "source_feedback")
    assert numeric["manifest"]["numerical_feedback"] is True
    assert "initial_source_feedback.json" in numeric["manifest"]["files"]
    (Path(packet["directory"]) / "leaked_statistics.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError):
        controller._verify_packet(controller._read()[0], "A01/self_review")


def test_source_failure_preserves_slots_blocks_targets_allows_revision_packet(tmp_path, monkeypatch, release):
    controller = make_controller(release)
    root, candidate, old = make_candidate(tmp_path / "data", monkeypatch, release)
    register(controller, root, candidate, tmp_path)
    old.worker(monkeypatch, fail=True)
    controller.dispatch_sources("A01", "initial")
    controller.deliver_branch_packet("A01", "source_feedback")
    close_other_versions(controller)
    controller.freeze_scientific_inventory()
    with pytest.raises(ValueError):
        controller.dispatch_targets("A01", "initial")
    closed = controller.close_targets()
    source_slots = [s for s in closed["slots"] if s["constructor"] == "A01" and s["version"] == "initial" and s["role"] == "source"]
    targets = [s for s in closed["slots"] if s["constructor"] == "A01" and s["version"] == "initial" and s["role"] == "target"]
    assert len(source_slots) == 9 and all(s["status"] == "failed" for s in source_slots)
    assert all(s["status"] == "not_run" and s["error"]["type"] == "source_ineligible" for s in targets)


def test_interruption_debits_phase_and_cannot_retry(tmp_path, monkeypatch, release):
    controller = make_controller(release)
    root, candidate, old = make_candidate(tmp_path / "data", monkeypatch, release)
    register(controller, root, candidate, tmp_path)
    old.worker(monkeypatch, interrupt=True)
    with pytest.raises(KeyboardInterrupt):
        controller.dispatch_sources("A01", "initial")
    with pytest.raises(ValueError):
        controller.dispatch_sources("A01", "initial")
    controller.finish_sources("A01", "initial")
    slots = controller.verify()["slots"][:9]
    assert slots[0]["status"] == "interrupted" and all(s["status"] == "not_run" for s in slots[1:])
    assert slots[0]["output_sha256"] is not None  # Empty retained file still has a binding.
    path = Path(slots[0]["bundle"]) / "executions" / slots[0]["run_id"] / "stdout.log"
    path.write_text("An altered retained partial log", encoding="utf-8")
    with pytest.raises(ValueError, match="Closed source allocation changed"):
        controller.verify()


def test_live_phase_lock_excludes_recovery(release):
    controller = make_controller(release)
    with controller._execution_lock():
        with pytest.raises(OSError):
            controller.finish_sources("A01", "initial")
        with pytest.raises(OSError):
            controller.finish_targets("A01", "initial")


def test_required_qualified_checks_gate_independently_of_fit(release, monkeypatch):
    controller = make_controller(release)
    slots = controller._slots("A01", "initial", "source")
    for s in slots:
        s.update(status="success", bundle="invented", output_sha256="a" * 64)
    monkeypatch.setattr(controller, "_support_counts", lambda inspected, bundle, run_id, context_id: {
        "run_id": run_id, "output_sha256": "a" * 64, "report": {"status": "pass", "row_count": 3000}})
    reports = [{"trial_id": s["run_id"], "qualified_feedback": {"checks": [
        {"id": q["check_id"], "status": "available", "difference": 999999}
        for q in release["required_qualified_checks"] if q["context_id"] == s["context_id"]]}} for s in slots]
    packet = {"packet": {"reports": reports}}
    result = controller._source_eligibility({}, {"status": "complete"}, slots, packet)
    assert result["target_eligible"] and len(result["qualified_coverage"]) == 12
    reports[0]["qualified_feedback"]["checks"][0]["status"] = "unavailable"
    assert not controller._source_eligibility({}, {"status": "complete"}, slots, packet)["target_eligible"]


def test_retained_branch_has_independent_child_and_same_seeds(tmp_path, monkeypatch, release):
    controller = make_controller(release)
    root, candidate, old = make_candidate(tmp_path / "data", monkeypatch, release)
    register(controller, root, candidate, tmp_path)
    old.worker(monkeypatch)
    controller.dispatch_sources("A01", "initial")
    packet = controller.deliver_branch_packet("A01", "self_review")
    controller.record_branch_decision("A01", "self_review", {"action": "retain", "packet_sha256": packet["packet_sha256"],
        "reason": "Invented unchanged law", "addressed_findings": [], "remaining_limitations": []})
    child = root / "candidates/self_review"
    child.mkdir()
    for path in (root / candidate).iterdir():
        if path.name != "freeze.json":
            shutil.copy2(path, child / path.name)
    plan = pilot.read_json(child / pilot.bridge.PLAN)
    plan["trials"] = [{"id": s["run_id"], "context_id": s["context_id"], "seed": s["seed"], "n_rows": s["n_rows"]}
                      for s in controller._slots("A01", "self_review")]
    write(child / pilot.bridge.PLAN, plan)
    pilot.lifecycle.freeze_candidate(root, child, parent_receipt=root / candidate / "freeze.json", revision={
        "kind": "retain", "reason": "Invented", "addressed_findings": [], "remaining_limitations": []})
    pilot.bridge.prepare(root, child)
    requests = pilot.bridge.binding_requests(root, child)
    pilot.bridge.seal(root, child, {cid: {"binding_review": review(r["binding_sha256"]), "supplement_review": None, "proxy_reviews": {}}
                                  for cid, r in requests.items()})
    request = pilot.source.science_request(root, child)
    pilot.source.open_source_phase(root, child, {**review(request["request_sha256"]), "checks": {k: True for k in pilot.source.REVIEW_CHECKS}})
    register(controller, root, "candidates/self_review", tmp_path, version="self_review", packet=packet["packet_sha256"])
    controller.dispatch_sources("A01", "self_review")
    parent = pilot.lifecycle.verify_candidate(root, child)
    assert parent["parent"]["candidate"] == candidate and parent["revision"]["kind"] == "retain"
    assert pilot.sha256(child / "generator.py") == pilot.sha256(root / candidate / "generator.py")
    assert pilot.sha256(child / "model_spec.json") == pilot.sha256(root / candidate / "model_spec.json")
