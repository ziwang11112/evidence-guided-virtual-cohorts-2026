"""Invented fixtures; real lifecycle/collectors, mocked process boundary only.

No submitted generator, WSL process, network call, article or clinical data is
executed/read. Test-only approvals below are unmistakably invented fixtures.
"""
import copy
import json
from pathlib import Path
import socket
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import context_bridge as bridge
from invented_fixture import build_parent


def test_review(digest):
    return {"decision": "approved", "independent": True, "reviewer_id": "invented-test-reviewer",
            "producer_id": "invented-test-producer", "reviewed_utc": "2026-11-02T00:00:00Z",
            "reason": "Invented test approval only; not a scientific review", "approved_sha256": digest}


test_review.__test__ = False


def test_reviews(requests):
    return {identifier: {"binding_review": test_review(request["binding_sha256"]),
                         "supplement_review": None if request["supplement_sha256"] is None else test_review(request["supplement_sha256"]),
                         "proxy_reviews": {key: test_review(value) for key, value in request["proxy_sha256"].items()}}
            for identifier, request in requests.items()}


test_reviews.__test__ = False


@pytest.fixture
def bundle(tmp_path, monkeypatch):
    root = build_parent(tmp_path / "invented")
    for owner, name in [(subprocess, "run"), (subprocess, "Popen"), (socket, "create_connection")]:
        monkeypatch.setattr(owner, name, lambda *a, **k: pytest.fail("No process or network authorized in adapter tests"))
    monkeypatch.setattr(bridge.semantic.legacy, "collect_feedback", lambda *a, **k: pytest.fail("Legacy fallback forbidden"))
    return root


def prepared(bundle):
    bridge.prepare(bundle, "invented")
    return bridge.binding_requests(bundle, "invented")


def sealed(bundle):
    return bridge.seal(bundle, "invented", test_reviews(prepared(bundle)))


def destination(bundle):
    return bundle / bridge.FOLDER / "invented"


def rewrite(path, value):
    path.write_bytes(bridge._bytes(value))


def mutate_parent(bundle, function):
    candidate = bundle / "candidates/invented"
    (candidate / "freeze.json").unlink()
    function(candidate)
    bridge.lifecycle.freeze_candidate(bundle, candidate)


def mocked_worker(monkeypatch, *, fail_source=False):
    events = []
    monkeypatch.setattr(bridge.execution, "_runtime_manifest", lambda runtime: {"fixture": "no runtime inspected"})

    def capture(command, cwd, timeout, limit, stdout_path, stderr_path):
        events.append(cwd.name)
        task = bridge.read_json(cwd / "input/task.json")
        if fail_source and cwd.name == "source-one":
            output, report, returncode = "", {"status": "failed", "generator_started": True}, 1
        else:
            output = "id,x\n" + "".join(f"fixture-{i},{2 ** (i % 3)}\n" for i in range(task["n_rows"]))
            report, returncode = {"status": "completed", "generator_started": True}, 0
        (cwd / "output/generated.csv").write_text(output, encoding="utf-8")
        rewrite(cwd / "output/worker_report.json", report)
        stdout_path.write_text("Invented mocked process boundary\n", encoding="utf-8")
        stderr_path.write_text("", encoding="utf-8")
        return {"returncode": returncode, "host_timeout": False, "logs": {}}

    monkeypatch.setattr(bridge.execution, "_capture", capture)
    return events


def test_prepare_has_no_approvals_no_execution_and_identical_science(bundle):
    requests = prepared(bundle)
    assert set(requests) == {"source", "target"}
    parent = bundle / "candidates/invented"
    original = bridge.read_json(parent / "model_spec.json")
    for name in requests:
        child = destination(bundle) / f"contexts/{name}/bundle/candidates/context"
        assert (child / "generator.py").read_bytes() == (parent / "generator.py").read_bytes()
        derived = bridge.read_json(child / "model_spec.json")
        assert derived["parameters"]["active_context"] == name
        assert bridge.canonical(bridge._common(derived)) == bridge.canonical(bridge._common(original))
        assert not (child / "freeze.json").exists()
    declaration = bridge.read_json(destination(bundle) / "contexts/source/bundle/candidates/context/context_feedback_v1.json")
    assert declaration["context_review"] is None
    assert not list(destination(bundle).rglob("execution.json"))


def test_fixed_preparation_location_cannot_reset_budget(bundle):
    prepared(bundle)
    with pytest.raises(ValueError, match="already reserved"):
        bridge.prepare(bundle, "invented")
    with pytest.raises(TypeError):
        bridge.prepare(bundle, "invented", destination=bundle / "another")


def test_seal_requires_independent_complete_exact_reviews(bundle):
    requests = prepared(bundle)
    reviews = test_reviews(requests)
    reviews["source"]["binding_review"]["reviewer_id"] = "invented-test-producer"
    with pytest.raises(ValueError, match="Reviewer is producer"):
        bridge.seal(bundle, "invented", reviews)
    assert not (destination(bundle) / "reviews.json").exists()
    reviews = test_reviews(requests)
    reviews["source"]["supplement_review"]["approved_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="commitment mismatch"):
        bridge.seal(bundle, "invented", reviews)
    assert not (destination(bundle) / "reviews.json").exists()


def test_full_mocked_dispatch_uses_real_v1_then_supplement_and_target_none(bundle, monkeypatch):
    sealed(bundle)
    events = mocked_worker(monkeypatch)
    report = bridge.execute(bundle, "invented")
    assert events == ["source-one", "target-one"]
    assert report["source_target_generation_link_verified"] is True
    assert report["attempts_consumed"] == 2
    assert report["transport_validity"] == "not_assessed"
    assert report["scientific_contract_compliance"] == "not_verified"
    source = destination(bundle) / "contexts/source/bundle"
    native = bridge.read_json(source / "semantic_feedback_v1/source-one/feedback.json")
    extra = bridge.read_json(source / "context_feedback_v1/source-one/feedback.json")
    assert native["checks"][0]["status"] == "not_computable"
    assert native["checks"][0]["difference"] is None
    assert extra["checks"][0]["diagnostic"]["diagnostic"]["value"] == pytest.approx(2)
    assert extra["checks"][0]["proxy"] is None
    assert not extra["checks"][0]["exact_source_check_allowed"]
    target = destination(bundle) / "contexts/target/bundle"
    assert not (target / "semantic_feedback_v1").exists()
    assert not (target / "context_feedback_v1").exists()
    assert bridge.verify(bundle, "invented") == report


def test_failed_attempt_consumes_slot_and_cannot_retry(bundle, monkeypatch):
    sealed(bundle)
    events = mocked_worker(monkeypatch, fail_source=True)
    report = bridge.execute(bundle, "invented")
    assert events == ["source-one", "target-one"]
    assert report["attempts_consumed"] == 2
    assert report["source_target_generation_link_verified"] is False
    assert report["trials"][0]["status"] == "failed"
    with pytest.raises(ValueError, match="no retry"):
        bridge.execute(bundle, "invented")


def test_dispatch_exception_before_receipt_still_consumes_budget(bundle, monkeypatch):
    sealed(bundle)
    monkeypatch.setattr(bridge.execution, "run_candidate", lambda *a, **k: (_ for _ in ()).throw(OSError("Invented prelaunch failure")))
    report = bridge.execute(bundle, "invented")
    assert report["attempts_consumed"] == 2
    assert all(t["status"] == "error" for t in report["trials"])
    assert not report["source_target_generation_link_verified"]
    with pytest.raises(ValueError, match="no retry"):
        bridge.execute(bundle, "invented")


@pytest.mark.parametrize("mutation", ["budget", "seed", "rows", "duplicate", "missing_context", "source_none", "target_source", "extra_parameter", "unit", "review_prefilled"])
def test_invalid_frozen_plan_fails_before_any_preparation(bundle, mutation):
    def change(candidate):
        plan = bridge.read_json(candidate / bridge.PLAN)
        if mutation == "budget": plan["budget"]["source_attempts"] = True
        elif mutation == "seed": plan["trials"][0]["seed"] = True
        elif mutation == "rows": plan["trials"][0]["n_rows"] = 4
        elif mutation == "duplicate": plan["trials"][1]["id"] = "SOURCE-ONE"
        elif mutation == "missing_context": plan["contexts"].pop()
        elif mutation == "source_none": plan["contexts"][0]["feedback_policy"] = "none"
        elif mutation == "target_source": plan["contexts"][1]["source_ids"] = ["invented-source"]
        elif mutation == "extra_parameter": plan["shared_parameters"] = ["undeclared"]
        elif mutation == "unit": plan["contexts"][0]["recipe"]["measurement"]["mode"] = "multiply"
        elif mutation == "review_prefilled": plan["contexts"][0]["supplement"]["context_review"] = test_review("0" * 64)
        rewrite(candidate / bridge.PLAN, plan)
    mutate_parent(bundle, change)
    with pytest.raises((ValueError, TypeError, KeyError)):
        bridge.prepare(bundle, "invented")
    assert not destination(bundle).exists()


@pytest.mark.parametrize("path", ["contexts/source/bundle/task.json", "contexts/source/bundle/candidates/context/model_spec.json",
                                  "contexts/target/bundle/candidates/context/generator.py", "contexts/source/bundle/candidates/context/source_semantics_v1.json"])
def test_prepared_artifact_tamper_cannot_be_sealed(bundle, path):
    requests = prepared(bundle)
    target = destination(bundle) / path
    target.write_bytes(target.read_bytes() + b" ")
    with pytest.raises(ValueError, match="Prepared artifacts changed"):
        bridge.seal(bundle, "invented", test_reviews(requests))
    assert not (destination(bundle) / "reviews.json").exists()


@pytest.mark.parametrize("mutation", ["output", "execution", "spec", "generator", "semantic", "supplement", "attempt_seed", "extra_trial"])
def test_completed_artifact_tamper_rejected(bundle, monkeypatch, mutation):
    sealed(bundle)
    mocked_worker(monkeypatch)
    bridge.execute(bundle, "invented")
    root = destination(bundle)
    paths = {"output": "contexts/source/bundle/executions/source-one/output/generated.csv",
             "execution": "contexts/target/bundle/executions/target-one/execution.json",
             "spec": "contexts/target/bundle/candidates/context/model_spec.json", "generator": "contexts/source/bundle/candidates/context/generator.py",
             "semantic": "contexts/source/bundle/semantic_feedback_v1/source-one/feedback.json",
             "supplement": "contexts/source/bundle/context_feedback_v1/source-one/feedback.json"}
    if mutation in paths:
        path = root / paths[mutation]
        path.write_bytes(path.read_bytes() + b" ")
    elif mutation == "attempt_seed":
        path = root / "attempts/source-one/intent.json"
        value = bridge.read_json(path)
        value["trial"]["seed"] = 999
        rewrite(path, value)
    else:
        path = root / "contexts/source/bundle/executions/extra"
        path.mkdir()
        (path / "unapproved.txt").write_text("extra", encoding="utf-8")
    with pytest.raises(ValueError):
        bridge.verify(bundle, "invented")


def test_no_arbitrary_comparison_table_or_runtime_override(bundle):
    with pytest.raises(TypeError):
        bridge.execute(bundle, "invented", comparison_table="untrusted.csv")
    with pytest.raises(ValueError, match="Only the inspected"):
        bridge.prepare(bundle, "invented", runtime={**bridge.execution.DEFAULT_RUNTIME, "backend": "host_python"})
    assert not destination(bundle).exists()


def test_unverifiable_failure_retains_all_bytes_and_cannot_retry(bundle, monkeypatch):
    sealed(bundle)

    def invalid_execution(child, candidate, run_id, seed, **kwargs):
        run = child / "executions" / run_id
        run.mkdir(parents=True)
        rewrite(run / "execution.json", {"status": "failed", "fixture": "Intentionally invalid early receipt"})
        (run / "stderr.log").write_text("Invented early staging failure", encoding="utf-8")
        return {"status": "failed"}

    monkeypatch.setattr(bridge.execution, "run_candidate", invalid_execution)
    report = bridge.execute(bundle, "invented")
    assert report["status"] == "finished_with_failures"
    assert report["attempts_consumed"] == 2
    assert not report["all_planned_trials_successful"]
    assert not report["all_planned_generation_links_verified"]
    assert all(t["status"] == "error" for t in report["trials"])
    path = destination(bundle) / "contexts/source/bundle/executions/source-one/stderr.log"
    path.write_text("Tampered retained failure bytes", encoding="utf-8")
    with pytest.raises(ValueError, match="artifacts changed"):
        bridge.verify(bundle, "invented")


def test_empty_attempted_run_directory_is_preserved_as_failed_attempt(bundle, monkeypatch):
    sealed(bundle)

    def interrupted_staging(child, candidate, run_id, seed, **kwargs):
        (child / "executions" / run_id / "input").mkdir(parents=True)
        raise OSError("Invented failure before any staged file")

    monkeypatch.setattr(bridge.execution, "run_candidate", interrupted_staging)
    report = bridge.execute(bundle, "invented")
    assert report["attempts_consumed"] == 2
    assert report["status"] == "finished_with_failures"


def test_interrupted_attempt_is_consumed_without_success_or_resume(bundle):
    sealed(bundle)
    state = bridge.preflight(bundle, "invented")
    trial = state["plan"]["trials"][0]
    attempt = destination(bundle) / "attempts" / trial["id"]
    attempt.mkdir(parents=True)
    bridge.execution._write(attempt / "intent.json", bridge._attempt_binding(state, trial))
    report = bridge.verify(bundle, "invented")
    assert report["status"] == "incomplete"
    assert report["attempts_consumed"] == 1
    assert report["trials"][0]["status"] == "interrupted"
    assert not report["all_planned_trials_successful"]
    with pytest.raises(ValueError, match="no retry"):
        bridge.execute(bundle, "invented")


def test_empty_undeclared_directory_is_rejected(bundle):
    sealed(bundle)
    (destination(bundle) / "contexts/unplanned").mkdir()
    with pytest.raises(ValueError, match="Unexpected bridge directory"):
        bridge.verify(bundle, "invented")


def test_declared_source_ids_must_match_recipe_evidence(bundle):
    def change(candidate):
        evidence = bridge.read_json(candidate / "evidence.json")
        second = copy.deepcopy(evidence["sources"][0])
        second["id"] = "invented-second"
        second["cohort_ids"] = ["invented-second"]
        evidence["sources"].append(second)
        rewrite(candidate / "evidence.json", evidence)
        registry = bridge.read_json(bundle / "registry.json")
        entry = copy.deepcopy(registry["artifacts"][0])
        entry["source_id"] = "invented-second"
        registry["artifacts"].append(entry)
        rewrite(bundle / "registry.json", registry)
        plan = bridge.read_json(candidate / bridge.PLAN)
        plan["contexts"][0]["source_ids"] = ["invented-second"]
        rewrite(candidate / bridge.PLAN, plan)
    mutate_parent(bundle, change)
    with pytest.raises(ValueError, match="exactly the declared source"):
        bridge.prepare(bundle, "invented")
    assert not destination(bundle).exists()


def test_feedback_failure_has_no_legacy_fallback_and_retains_artifact_hash(bundle, monkeypatch):
    sealed(bundle)
    mocked_worker(monkeypatch)

    def invalid_collector(child, candidate, run_id, feedback_id):
        folder = child / bridge.semantic.FOLDER / feedback_id
        folder.mkdir(parents=True)
        rewrite(folder / "feedback.json", {"fixture": "Intentionally interrupted collector"})
        raise ValueError("Invented semantic failure")

    monkeypatch.setattr(bridge.semantic, "collect_feedback", invalid_collector)
    report = bridge.execute(bundle, "invented")
    assert report["status"] == "finished_with_failures"
    assert report["source_target_generation_link_verified"]  # Generation succeeded; source feedback did not.
    assert not report["all_planned_trials_successful"]
    path = destination(bundle) / "contexts/source/bundle/semantic_feedback_v1/source-one/feedback.json"
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(ValueError, match="artifacts changed"):
        bridge.verify(bundle, "invented")


def test_partial_pair_does_not_claim_all_planned_generation_links(bundle, monkeypatch):
    def change(candidate):
        plan = bridge.read_json(candidate / bridge.PLAN)
        plan["trials"].append({"id": "source-two", "context_id": "source", "seed": 107, "n_rows": 3})
        plan["budget"].update(source_attempts=2, source_rows=6)
        rewrite(candidate / bridge.PLAN, plan)
    mutate_parent(bundle, change)
    sealed(bundle)
    mocked_worker(monkeypatch, fail_source=True)
    report = bridge.execute(bundle, "invented")
    assert report["any_verified_source_target_pair"]
    assert not report["source_target_generation_link_verified"]
    assert not report["all_planned_generation_links_verified"]
    assert report["status"] == "finished_with_failures"


def test_final_completion_commits_attempt_metadata(bundle, monkeypatch):
    sealed(bundle)
    mocked_worker(monkeypatch)
    report = bridge.execute(bundle, "invented")
    assert report["completion_committed"]
    path = destination(bundle) / "attempts/source-one/outcome.json"
    outcome = bridge.read_json(path)
    outcome["error"] = {"message": "Altered bookkeeping after completion"}
    rewrite(path, outcome)
    with pytest.raises(ValueError, match="Completed ledger"):
        bridge.verify(bundle, "invented")
