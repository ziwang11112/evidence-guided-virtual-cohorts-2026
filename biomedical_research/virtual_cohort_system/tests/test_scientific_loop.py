"""Invented controller fixtures using MOCK generator execution, never real patients."""
import copy

import pytest

from cohort_harness import calibration, calibration_budget, lifecycle, scientific_loop as loop
from cohort_harness.lifecycle import read_json, sha256
from examples import m12_calibration as fixture
from test_calibration import mocked_backend


@pytest.fixture
def box(tmp_path_factory):
    return tmp_path_factory.mktemp("l")


def prepared(box, monkeypatch, *, failed_replay=False, noncomputable=False, revisions=3, max_actions=3, max_promotions=2):
    # Construct this NEW fixture unfrozen so its scientific budget is fixed before
    # any freeze. No historical/frozen input is edited to expand a budget.
    with monkeypatch.context() as patch:
        patch.setattr(fixture, "freeze_candidate", lambda *a, **k: None)
        root, candidate, plan = fixture.build_fixture(box / "b", noncomputable=noncomputable)
    task = read_json(root / "task.json")
    task["budget"]["revisions"] = revisions
    fixture.write(root / "task.json", task)
    lifecycle.freeze_candidate(root, candidate)
    plan["optimizer"]["max_trials"] = 1
    plan["fit_seeds"], plan["replay_seeds"] = [101], [201]
    mocked_backend(monkeypatch, failing_seeds=[201] if failed_replay else [])
    calibration_budget.create_budget(root, fixture.budget_limits(plan))
    result = calibration.run_calibration(root, candidate, "s", plan)
    loop.create_loop(root, {"max_actions": max_actions, "max_promotions": max_promotions})
    return root, candidate, result


def decision(choice="retain_structure"):
    return {"choice": choice, "rationale": "Keep the assumed structure as a development candidate; source fit is insufficient.",
            "evidence_ids": ["M", "B", "D"], "addressed_constraints": ["s/mean", "s/beta", "s/sd"],
            "remaining_limits": ["Not target validated", "Above source fit threshold"]}


def request(root, candidate, action="review"):
    return loop.request_review(root, action, candidate, "s", "Review only supplied source diagnostics.", "test external Agent stub")


def test_request_is_bound_before_external_response(box, monkeypatch):
    root, candidate, result = prepared(box, monkeypatch)
    receipt = request(root, candidate)
    state = loop.verify_loop(root)
    assert state["pending"] == {"kind": "decision", "action_id": "review"}
    assert receipt["status"] == "awaiting_decision"
    assert receipt["request"]["binding"]["calibration_result_sha256"] == sha256(root / "cal/s/result.json")
    assert receipt["request"]["revealed_source_manifest"]["agent_access_isolation"] == "procedural_not_os_enforced"
    with pytest.raises(ValueError, match="pending"):
        request(root, candidate, "second")
    assert loop.verify_loop(root)["usage"]["actions"] == 1


def test_promotes_exact_selected_bytes_with_separate_scientific_meaning(box, monkeypatch):
    root, candidate, result = prepared(box, monkeypatch)
    before = {n: sha256(candidate / n) for n in ("freeze.json", "generator.py", "model_spec.json")}
    request(root, candidate)
    loop.record_decision(root, "review", decision())
    promoted = loop.promote(root, "review", "selected")
    new = root / "candidates/selected"
    selected = root / "cal/s/t0000/candidates/t"
    assert all((new / n).read_bytes() == (selected / n).read_bytes() for n in ("generator.py", "model_spec.json"))
    frozen = lifecycle.verify_candidate(root, new)
    assert frozen["parent"]["candidate"] == "candidates/p"
    assert frozen["revision"]["kind"] == "revise"  # numeric values retained; provenance bytes changed
    assert promoted["decision"]["choice"] == "retain_structure"
    assert promoted["status"] == "promoted"
    assert all(sha256(candidate / n) == digest for n, digest in before.items())
    provenance = read_json(new / "calibration_provenance.json")
    assert provenance["calibration_status"] == "fit_threshold_not_met"
    assert provenance["scope"] == "source_checked_development_candidate_not_target_release"
    checks = read_json(new / "checks.json")
    assert next(c for c in checks["records"] if c["name"] == "source_fit_criterion")["status"] == "fail"
    assert not (new / "calibration_trial.json").exists()
    assert loop.verify_loop(root)["usage"] == {"actions": 1, "promotions": 1}


@pytest.mark.parametrize("choice", ["revise_structure", "request_evidence", "stop"])
def test_nonpromotion_decisions_remain_legitimate_terminal_records(box, monkeypatch, choice):
    root, candidate, _ = prepared(box, monkeypatch)
    request(root, candidate)
    loop.record_decision(root, "review", decision(choice))
    with pytest.raises(ValueError):
        loop.promote(root, "review", "not_created")
    assert not (root / "candidates/not_created").exists()
    assert loop.verify_loop(root)["usage"]["promotions"] == 0
    if choice == "stop":
        with pytest.raises(ValueError, match="stopped"):
            request(root, candidate, "again")


@pytest.mark.parametrize("bad", ["evidence", "constraint", "duplicate", "extra", "empty"])
def test_invalid_response_does_not_change_pending_request(box, monkeypatch, bad):
    root, candidate, _ = prepared(box, monkeypatch)
    request(root, candidate)
    value = decision()
    if bad == "evidence": value["evidence_ids"] = ["hidden_answer"]
    elif bad == "constraint": value["addressed_constraints"] = ["target/accuracy"]
    elif bad == "duplicate": value["remaining_limits"] *= 2
    elif bad == "extra": value["secret_target_score"] = 1
    else: value["rationale"] = " "
    with pytest.raises(ValueError):
        loop.record_decision(root, "review", value)
    state = loop.verify_loop(root)
    assert state["event_count"] == 1 and state["pending"]["kind"] == "decision"


def test_no_reset_duplicate_action_or_post_budget_dispatch(box, monkeypatch):
    root, candidate, _ = prepared(box, monkeypatch, max_actions=1, max_promotions=1)
    request(root, candidate)
    loop.record_decision(root, "review", decision("request_evidence"))
    with pytest.raises(ValueError, match="already exists"):
        loop.create_loop(root, {"max_actions": 100, "max_promotions": 100})
    with pytest.raises(ValueError, match="already used"):
        request(root, candidate, "REVIEW")
    with pytest.raises(ValueError, match="budget"):
        request(root, candidate, "new")


def test_global_promotion_budget_covers_siblings(box, monkeypatch):
    root, candidate, _ = prepared(box, monkeypatch, max_promotions=1)
    request(root, candidate)
    loop.record_decision(root, "review", decision())
    loop.promote(root, "review", "first")
    request(root, candidate, "second")
    loop.record_decision(root, "second", decision())
    with pytest.raises(ValueError, match="promotion budget"):
        loop.promote(root, "second", "sibling")
    assert not (root / "candidates/sibling").exists()


@pytest.mark.parametrize("condition", ["replay", "noncomputable", "revision_budget"])
def test_infeasible_or_unbudgeted_promotion_rejected_before_creation(box, monkeypatch, condition):
    root, candidate, _ = prepared(box, monkeypatch, failed_replay=condition == "replay",
        noncomputable=condition == "noncomputable", revisions=0 if condition == "revision_budget" else 3)
    request(root, candidate)
    loop.record_decision(root, "review", decision())
    with pytest.raises(ValueError):
        loop.promote(root, "review", "rejected")
    assert not (root / "candidates/rejected").exists()
    assert loop.verify_loop(root)["usage"]["promotions"] == 0


def test_interrupted_promotion_is_reserved_and_cannot_resume(box, monkeypatch):
    root, candidate, _ = prepared(box, monkeypatch)
    request(root, candidate)
    loop.record_decision(root, "review", decision())
    monkeypatch.setattr(loop.lifecycle, "freeze_candidate", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("interrupted fixture")))
    with pytest.raises(RuntimeError, match="interrupted fixture"):
        loop.promote(root, "review", "partial")
    state = loop.verify_loop(root)
    assert state["pending"] == {"kind": "promotion", "action_id": "review"}
    assert state["usage"]["promotions"] == 1
    assert (root / "candidates/partial/generator.py").exists()
    with pytest.raises(ValueError):
        loop.promote(root, "review", "retry")
    with pytest.raises(ValueError):
        request(root, candidate, "more")


def test_inputs_changed_after_request_reject_response(box, monkeypatch):
    root, candidate, _ = prepared(box, monkeypatch)
    request(root, candidate)
    (candidate / "generator.py").write_bytes((candidate / "generator.py").read_bytes() + b"\n")
    with pytest.raises(ValueError):
        loop.record_decision(root, "review", decision())
    assert len(list((root / "scientific_loop/events").glob("*.json"))) == 1


def test_promoted_bytes_and_events_are_verified(box, monkeypatch):
    root, candidate, _ = prepared(box, monkeypatch)
    request(root, candidate)
    loop.record_decision(root, "review", decision())
    loop.promote(root, "review", "selected")
    path = root / "candidates/selected/model_spec.json"
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(ValueError):
        loop.verify_loop(root)


def test_event_inventory_and_hash_chain_fail_closed(box, monkeypatch):
    root, candidate, _ = prepared(box, monkeypatch)
    request(root, candidate)
    path = root / "scientific_loop/events/00000001.json"
    envelope = read_json(path)
    envelope["payload"]["payload"]["actor"] = "replacement"
    fixture.write(path, envelope)
    with pytest.raises(ValueError):
        loop.verify_loop(root)


def test_oversized_unicode_request_rejected_without_poisoning_loop(box, monkeypatch):
    root, candidate, _ = prepared(box, monkeypatch)
    with pytest.raises(ValueError, match="byte limit"):
        loop.request_review(root, "large", candidate, "s", "语" * 50_000, "external test Agent")
    assert loop.verify_loop(root)["event_count"] == 0
    request(root, candidate)


def test_rehashed_revision_annotation_must_match_actual_recorded_decision(box, monkeypatch):
    root, candidate, _ = prepared(box, monkeypatch)
    request(root, candidate)
    loop.record_decision(root, "review", decision())
    loop.promote(root, "review", "selected")
    path = root / "candidates/selected/freeze.json"
    frozen = read_json(path)
    frozen["revision"]["reason"] = "Invented replacement scientific rationale"
    fixture.write(path, frozen)
    lifecycle.verify_candidate(root, "candidates/selected")  # v1 has no Agent-decision contract.
    event_path = root / "scientific_loop/events/00000004.json"
    payload = read_json(event_path)["payload"]
    payload["payload"]["freeze_sha256"] = sha256(path)
    replacement = calibration_budget._envelope(payload)
    fixture.write(event_path, replacement)
    head_path = root / "scientific_loop/head.json"
    head = read_json(head_path)["payload"]
    head["last_event_sha256"] = replacement["sha256"]
    fixture.write(head_path, calibration_budget._envelope(head))
    with pytest.raises(ValueError, match="revision annotations"):
        loop.verify_loop(root)
