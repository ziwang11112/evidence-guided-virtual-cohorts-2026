"""Invented protocol tests; process boundary mocked, no generator runs."""
import copy
import socket
import subprocess

import pytest
import revision_controller_v1 as controller
from evidence_use_v1 import canonical_json_sha256
from invented_fixture import build_parent

bridge = controller.bridge


def invented_review(digest):
    return {"decision": "approved", "independent": True, "reviewer_id": "invented-test-reviewer",
            "producer_id": "invented-test-author", "reviewed_utc": "2026-11-03T00:00:00Z",
            "reason": "Invented approval tests only; no clinical/scientific approval",
            "approved_sha256": digest}


@pytest.fixture
def bundle(tmp_path, monkeypatch, request):
    # Build a new invented fixture, deferring its FIRST freeze until sidecars exist.
    with monkeypatch.context() as m:
        m.setattr(bridge.lifecycle, "freeze_candidate", lambda *a, **k: None)
        root = build_parent(tmp_path / "fixture")
    directory = root / "candidates/invented"
    task = bridge.read_json(root / "task.json")
    task["columns"].append({"name": "y", "kind": "number", "unit": "example_unit", "role": "generated", "nullable": False})
    (root / "task.json").write_bytes(bridge._bytes(task))
    (directory / "generator.py").write_text('''import pandas as pd
import numpy as np
def generate(observed, specification, seed):
    context = specification["parameters"]["contexts"][specification["parameters"]["active_context"]]
    n = context["n_rows"]
    rng = np.random.default_rng(seed)
    return pd.DataFrame({"id": ["fixture-" + str(i) for i in range(n)],
                         "x": rng.uniform(1, 4, n), "y": rng.uniform(0, 4, n)})
''', encoding="utf-8")
    evidence = bridge.read_json(directory / "evidence.json")
    mode = getattr(request, "param", "ordinary")
    if mode == "qualified":
        source_file = root / "sources/invented.txt"
        source_file.write_text("Invented Pearson 0.4; original weights unknown. No actual study.\n", encoding="utf-8")
        source_hash = bridge.sha256(source_file)
        evidence["sources"][0]["artifacts"][0]["sha256"] = source_hash
        evidence["items"][0].update(kind="correlation", estimate=0.4, variables=["x", "y"], unit="1")
        evidence["items"][0].pop("statistic_name")
        registry = bridge.read_json(root / "registry.json")
        registry["artifacts"][0]["sha256"] = source_hash
        (root / "registry.json").write_bytes(bridge._bytes(registry))
        (directory / "evidence.json").write_bytes(bridge._bytes(evidence))
        plan = bridge.read_json(directory / bridge.PLAN)
        source_context = plan["contexts"][0]
        source_context.update(feedback_policy="semantic_v1", supplement=None)
        source_context["recipe"]["checks"][0]["reason"] = "Original weights unknown"
        source_context["semantics"]["bindings"][0].update(definition_status="not_reported", reason="Original estimator details unknown")
        (directory / bridge.PLAN).write_bytes(bridge._bytes(plan))
    source, item = evidence["sources"][0], evidence["items"][0]
    ledger = {"schema_version": 1, "evidence_sha256": canonical_json_sha256(evidence), "items": [{
        "evidence_id": item["id"], "role": "qualitative_context",
        "source_reference": {"source_id": source["id"], "source_sha256": canonical_json_sha256(source),
                             "item_sha256": canonical_json_sha256(item)},
        "context_id": "source", "check_ids": [], "parameter_names": [], "structure_names": [],
        "code_references": [], "assumption_ids": ["fixture"], "gaps": [],
        "rationale": "Invented contextual item; no numerical uptake claim", "source_comparison": "not_applicable"}]}
    if mode == "qualified":
        ledger["items"][0].update(role="qualified_numerical_comparison", check_ids=["native-geo"],
                                  structure_names=["generate"], code_references=[{"path": "generator.py", "symbol": "generate"}],
                                  source_comparison="qualified")
        operator = {"kind": "correlation", "x": "x", "y": "y", "unit": "1", "selection": [], "missing_policy": "error"}
        qualified_plan = {"schema_version": 1, "contexts": {"source": {
            "schema_version": 1, "bindings": {}, "context_role": "source", "context_id": "source",
            "population": "Invented source context", "measurement": "Invented measurement", "column_aliases": [],
            "source_ids": [source["id"]], "assumption_ids": ["fixture"], "checks": [{
                "id": "qualified-corr", "evidence_id": item["id"], "semantic_check_id": "native-geo", "operator": operator,
                "measurement_mapping": {"kind": "identity"}, "source_relation": {
                    "kind": "same_reported_functional_under_declared_assumptions", "assumed_weights": "equal",
                    "assumption_ids": ["fixture"], "unresolved_original_details": ["Unknown original weights"],
                    "reason": "Invented equal-weight assumption, no original study claim"}}]}}}
        bridge.execution._write(directory / "qualified_plan_v1.json", qualified_plan)
    analysis = {"schema_version": 1, "analyses": [{"id": "toy-ols", "estimand": {
        "description": "Invented OLS", "kind": "ols_coefficient", "outcome": "y", "exposures": ["x"],
        "conditioning": [], "adjustment": [], "scale": "original", "unit": "1",
        "population": task["population"], "measurement": "Invented", "selection": "All invented rows"},
        "assessment": "unassessed", "rationale": "Protocol fixture only", "assumption_ids": ["fixture"],
        "evidence_links": [], "gaps": [{"id": "g", "dimension": "joint_distribution", "description": "No real evidence",
        "consequence": "No clinical claim", "assumption_ids": ["fixture"]}],
        "actions": [{"id": "a", "gap_ids": ["g"], "tool": "none", "request": "No retrieval",
                     "status": "unavailable", "reason": "Fixture"}]}]}
    law = {"schema_version": "scientific_validity_v1", "variables": {
        "x": {"op": "uniform", "lower": 1., "upper": 4.},
        "y": {"op": "uniform", "lower": 0., "upper": 4.}},
        "independence": [["x", "y"]], "analyses": [{"id": "toy-ols", "kind": "ols", "outcome": "y", "predictors": ["x"]}]}
    wrapped_laws = {"schema_version": 1, "context_laws": {"source": law, "target": copy.deepcopy(law)}}
    if mode == "two_sources":
        spec = bridge.read_json(directory / "model_spec.json")
        spec["parameters"]["contexts"]["source2"] = copy.deepcopy(spec["parameters"]["contexts"]["source"])
        (directory / "model_spec.json").write_bytes(bridge._bytes(spec))
        plan = bridge.read_json(directory / bridge.PLAN)
        extra = copy.deepcopy(plan["contexts"][0])
        extra["id"] = "source2"
        extra.update(feedback_policy="semantic_v1", supplement=None)
        extra["recipe"]["checks"][0]["id"] = "native-geo2"
        extra["semantics"]["bindings"][0]["check_id"] = "native-geo2"
        plan["contexts"].append(extra)
        plan["trials"].append({"id": "source-two", "context_id": "source2", "seed": 105, "n_rows": 3})
        plan["budget"].update(source_attempts=2, source_rows=6)
        (directory / bridge.PLAN).write_bytes(bridge._bytes(plan))
        wrapped_laws["context_laws"]["source2"] = copy.deepcopy(law)
    for name, value in [("analysis_evidence.json", analysis), ("evidence_use_v1.json", ledger), ("scientific_validity_v1.json", wrapped_laws)]:
        bridge.execution._write(directory / name, value)
    bridge.lifecycle.freeze_candidate(root, directory)
    for owner, name in [(subprocess, "run"), (subprocess, "Popen"), (socket, "create_connection")]:
        monkeypatch.setattr(owner, name, lambda *a, **k: pytest.fail("No process/network authorized in unit tests"))
    monkeypatch.setattr(bridge.semantic.legacy, "collect_feedback", lambda *a, **k: pytest.fail("Legacy feedback fallback prohibited"))
    return root


def ready(root):
    bridge.prepare(root, "invented")
    requests = bridge.binding_requests(root, "invented")
    reviews = {cid: {"binding_review": invented_review(r["binding_sha256"]),
                    "supplement_review": invented_review(r["supplement_sha256"]) if r["supplement_sha256"] else None,
                    "proxy_reviews": {k: invented_review(v) for k, v in r["proxy_sha256"].items()}}
               for cid, r in requests.items()}
    bridge.seal(root, "invented", reviews)
    request = controller.science_request(root, "invented")
    review = {**invented_review(request["request_sha256"]), "checks": {k: True for k in controller.REVIEW_CHECKS}}
    qualified_requests = controller.qualified_requests(root, "invented")
    controller.open_source_phase(root, "invented", review,
        qualified_reviews={cid: invented_review(r["declaration_sha256"]) for cid, r in qualified_requests.items()})
    return review


def worker(monkeypatch, fail=False, interrupt=False, interrupt_on=None):
    events = []
    monkeypatch.setattr(bridge.execution, "_runtime_manifest", lambda runtime: {"fixture": "mocked"})
    def capture(command, cwd, timeout, limit, stdout_path, stderr_path):
        events.append(cwd.name)
        if interrupt or cwd.name == interrupt_on:
            raise KeyboardInterrupt("invented interrupted worker")
        task = bridge.read_json(cwd / "input/task.json")
        (cwd / "output/generated.csv").write_text("id,x,y\n" + "".join(
            f"fixture-{i},{2 ** (i % 3)},{i % 4}\n" for i in range(task["n_rows"])), encoding="utf-8")
        (cwd / "output/worker_report.json").write_bytes(bridge._bytes({"status": "failed" if fail else "completed", "generator_started": True}))
        stdout_path.write_text("invented process boundary", encoding="utf-8")
        stderr_path.write_text("", encoding="utf-8")
        return {"returncode": 1 if fail else 0, "host_timeout": False, "logs": {}}
    monkeypatch.setattr(bridge.execution, "_capture", capture)
    return events


def test_source_only_real_receipts_no_target_no_legacy(bundle, monkeypatch):
    ready(bundle)
    events = worker(monkeypatch)
    report = controller.dispatch_sources(bundle, "invented")
    assert events == ["source-one"]
    assert report["status"] == "complete" and report["target_attempts"] == 0
    assert report["target_release_authorized"] is False
    assert bridge.verify(bundle, "invented")["status"] == "incomplete"
    assert not list((bundle / "context_bridge_v1/invented/contexts/target").rglob("execution.json"))
    packet = controller.source_feedback_packet(bundle, "invented")
    assert packet["packet"]["target_results_included"] is False
    assert packet["packet"]["reports"][0]["feedback"]["checks"][0]["status"] == "not_computable"
    with pytest.raises(ValueError):
        controller.dispatch_sources(bundle, "invented")


def test_independent_science_review_not_self_approval(bundle):
    review = ready(bundle)
    request = controller.science_request(bundle, "invented")
    review["reviewer_id"] = review["producer_id"]
    with pytest.raises(ValueError):
        controller._review(review, request)
    review["reviewer_id"] = "different"
    review["checks"]["code_correspondence"] = False
    with pytest.raises(ValueError):
        controller._review(review, request)


def test_stale_or_ineligible_review_rejected(bundle):
    review = ready(bundle)
    request = controller.science_request(bundle, "invented")
    altered = copy.deepcopy(request)
    altered["request_sha256"] = "0" * 64
    with pytest.raises(ValueError):
        controller._review(review, altered)
    altered = copy.deepcopy(request)
    altered["request"]["eligible_for_independent_review"] = False
    altered["request_sha256"] = bridge.digest(altered["request"])
    review["approved_sha256"] = altered["request_sha256"]
    with pytest.raises(ValueError):
        controller._review(review, altered)


def test_changed_scientific_file_cannot_execute(bundle, monkeypatch):
    ready(bundle)
    events = worker(monkeypatch)
    path = bundle / "candidates/invented/scientific_validity_v1.json"
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError):
        controller.dispatch_sources(bundle, "invented")
    assert events == []


def test_failure_consumes_source_slot_without_target(bundle, monkeypatch):
    ready(bundle)
    events = worker(monkeypatch, fail=True)
    report = controller.dispatch_sources(bundle, "invented")
    assert events == ["source-one"] and report["status"] == "finished_with_failures"
    reports = controller.source_feedback_packet(bundle, "invented")["packet"]["reports"]
    assert len(reports) == 1 and reports[0]["status"] != "success" and reports[0]["feedback"] is None
    with pytest.raises(ValueError):
        controller.dispatch_sources(bundle, "invented")


def test_interruption_has_no_retry_and_keeps_intent(bundle, monkeypatch):
    ready(bundle)
    events = worker(monkeypatch, interrupt=True)
    with pytest.raises(KeyboardInterrupt):
        controller.dispatch_sources(bundle, "invented")
    assert events == ["source-one"]
    assert (bundle / "source_revision_v1/invented/dispatch_intent.json").exists()
    with pytest.raises(ValueError):
        controller.dispatch_sources(bundle, "invented")
    packet = controller.source_feedback_packet(bundle, "invented")
    assert packet["packet"]["reports"][0]["error"]["type"] == "interrupted"
    decision = {"action": "stop", "feedback_sha256": packet["packet_sha256"], "reason": "Interrupted fixture",
                "addressed_findings": [], "remaining_limitations": ["No retry"]}
    controller.record_decision(bundle, "invented", decision)
    controller.verify_source_phase(bundle, "invented")


def test_feedback_bound_decision_is_once_only(bundle, monkeypatch):
    ready(bundle)
    worker(monkeypatch)
    controller.dispatch_sources(bundle, "invented")
    packet = controller.source_feedback_packet(bundle, "invented")
    decision = {"action": "retain", "feedback_sha256": "0" * 64, "reason": "Invented no-op",
                "addressed_findings": [], "remaining_limitations": ["Not clinical"]}
    with pytest.raises(ValueError):
        controller.record_decision(bundle, "invented", decision)
    decision["feedback_sha256"] = packet["packet_sha256"]
    assert controller.record_decision(bundle, "invented", decision)["revision_executed"] is False
    with pytest.raises(FileExistsError):
        controller.record_decision(bundle, "invented", decision)


def test_dispatch_intent_tamper_detected(bundle, monkeypatch):
    ready(bundle)
    worker(monkeypatch)
    controller.dispatch_sources(bundle, "invented")
    path = bundle / "source_revision_v1/invented/dispatch_intent.json"
    path.write_text('{"intent_sha256":"changed"}', encoding="utf-8")
    with pytest.raises(ValueError):
        controller.verify_source_phase(bundle, "invented")


def test_decision_tamper_detected(bundle, monkeypatch):
    ready(bundle)
    worker(monkeypatch)
    controller.dispatch_sources(bundle, "invented")
    packet = controller.source_feedback_packet(bundle, "invented")
    decision = {"action": "stop", "feedback_sha256": packet["packet_sha256"], "reason": "Fixture",
                "addressed_findings": [], "remaining_limitations": []}
    controller.record_decision(bundle, "invented", decision)
    decision["action"] = "retain"  # A changed action with the same valid feedback must also fail.
    (bundle / "source_revision_v1/invented/decision.json").write_bytes(bridge._bytes(decision))
    with pytest.raises(ValueError):
        controller.verify_source_phase(bundle, "invented")


def test_source_moment_failure_cannot_be_hidden_by_target(bundle, monkeypatch):
    real = controller.assess_law
    calls = []
    def source_bad(law):
        result = real(law)
        if not calls:
            result["analyses"][0]["second_moment_status"] = "fail"
        calls.append(True)
        return result
    monkeypatch.setattr(controller, "assess_law", source_bad)
    request = controller.science_request(bundle, "invented")
    assert len(calls) == 2
    assert request["request"]["eligible_for_independent_review"] is False


@pytest.mark.parametrize("bundle", ["qualified"], indirect=True)
def test_actual_qualified_collector_connected_without_promoting_strict(bundle, monkeypatch):
    ready(bundle)
    worker(monkeypatch)
    controller.dispatch_sources(bundle, "invented")
    packet = controller.source_feedback_packet(bundle, "invented")
    report = packet["packet"]["reports"][0]
    assert report["feedback"]["checks"][0]["status"] == "not_computable"
    assert report["qualified_status"] == "verified_assumption_comparison_not_strict_replay"
    comparison = report["qualified_feedback"]["checks"][0]
    assert comparison["status"] == "available" and comparison["original_source_weights"] == "not_reported"
    assert report["evidence_use_annotations"][0]["declaration"]["role"] == "qualified_numerical_comparison"
    decision = {"action": "revise", "feedback_sha256": packet["packet_sha256"], "reason": "Invented revision decision",
                "addressed_findings": ["Inspect qualified mismatch"], "remaining_limitations": ["Only assumed source context"]}
    controller.record_decision(bundle, "invented", decision)
    controller.verify_source_phase(bundle, "invented")


@pytest.mark.parametrize("bundle", ["two_sources"], indirect=True)
def test_partial_success_then_interrupt_preserves_feedback_and_allows_stop(bundle, monkeypatch):
    ready(bundle)
    events = worker(monkeypatch, interrupt_on="source-two")
    with pytest.raises(KeyboardInterrupt):
        controller.dispatch_sources(bundle, "invented")
    assert events == ["source-one", "source-two"]
    packet = controller.source_feedback_packet(bundle, "invented")
    reports = packet["packet"]["reports"]
    assert reports[0]["feedback"] is not None and reports[1]["error"]["type"] == "interrupted"
    decision = {"action": "stop", "feedback_sha256": packet["packet_sha256"], "reason": "Interrupted second slot",
                "addressed_findings": [], "remaining_limitations": ["Partial result only"]}
    controller.record_decision(bundle, "invented", decision)
    controller.verify_source_phase(bundle, "invented")


def test_late_supplement_error_preserves_verified_semantic_feedback(bundle, monkeypatch):
    ready(bundle)
    worker(monkeypatch)
    def fail(*a, **k):
        raise ValueError("Invented late supplemental failure")
    monkeypatch.setattr(bridge.supplement, "collect_feedback", fail)
    controller.dispatch_sources(bundle, "invented")
    report = controller.source_feedback_packet(bundle, "invented")["packet"]["reports"][0]
    assert report["status"] == "error" and report["feedback"] is not None
    assert "late supplemental" in report["error"]["message"]


def test_invalid_partial_semantic_feedback_retained_and_stop_allowed(bundle, monkeypatch):
    ready(bundle)
    worker(monkeypatch)
    def partial(child, candidate, run_id, feedback_id):
        path = child / controller.semantic.FOLDER / feedback_id / "feedback.json"
        path.parent.mkdir(parents=True)
        path.write_text("{partial", encoding="utf-8")
        raise ValueError("Invented partial feedback write")
    monkeypatch.setattr(bridge.semantic, "collect_feedback", partial)
    controller.dispatch_sources(bundle, "invented")
    packet = controller.source_feedback_packet(bundle, "invented")
    report = packet["packet"]["reports"][0]
    assert report["feedback"] is None and report["feedback_status"].startswith("invalid_partial")
    decision = {"action": "stop", "feedback_sha256": packet["packet_sha256"], "reason": "Invalid partial receipt",
                "addressed_findings": [], "remaining_limitations": ["No arithmetic based on malformed feedback"]}
    controller.record_decision(bundle, "invented", decision)
    controller.verify_source_phase(bundle, "invented")
