"""Independent regression checks; mocks and empty artifacts only, no real rows."""
from pathlib import Path
import pytest

from test_runner import env, r, write


def test_direct_rows_supported_as_fixed_table_validation_slots(env):
    s = env.start(route="generated.csv")
    trial = s.trial("candidates/initial")
    s.feedback(trial["run_id"])
    env.decision(s)
    s.deliver()
    results = s.selected("result")
    assert len(env.calls) == 4 and len(results) == 4
    assert s.selected("freeze")[0]["output_route"] == "generated.csv"
    assert all(x["output_route"] == "generated.csv" for x in results)
    assert all(x["generator_executed"] is False for x in results)
    assert all(x["seed_role"] == "fixed_table_validation_slot" for x in results)
    assert len({x["table"]["sha256"] for x in results}) == 1
    assert s.status()["closed"]


def test_unverifiable_receipt_is_retained_but_never_a_valid_table(env, monkeypatch):
    s = env.start()

    def invalid_receipt(*args):
        raise ValueError("Mock receipt has no verifiable run artifacts")

    monkeypatch.setattr(r.execution, "verify_execution", invalid_receipt)
    result = s.trial("candidates/initial")
    assert result["status"] == "adapter_error"
    assert result["error"] == {"type": "ValueError", "message": "Mock receipt has no verifiable run artifacts"}
    assert result["receipt"] is None and result["table"] is None
    assert result["unverified_receipt"]["sha256"] == r.SHA(result["unverified_receipt"]["path"])
    assert len(s.selected("attempt")) == 1
    assert s.verify()
    with pytest.raises(ValueError, match="Slot consumed"):
        s.trial("candidates/initial")
    s.abandon("Mock receipt verification failure")
    for author in ("C02", "E01", "E02"):
        r.abandon(author, "Mock unstarted slot", external_author_id="external-" + author)
    closure = r.seal_batch()
    assert closure["physical_attempts"] == 1
    assert r.closure_gate() == closure


def test_unverified_receipt_bytes_still_committed(env, monkeypatch):
    s = env.start()
    monkeypatch.setattr(r.execution, "verify_execution", lambda *a: (_ for _ in ()).throw(ValueError("Mock rejection")))
    result = s.trial("candidates/initial")
    write(Path(result["unverified_receipt"]["path"]), {"changed": True})
    with pytest.raises(ValueError, match="Bound artifact changed"):
        s.verify()


def test_completed_workflow_cannot_skip_initial_trial(env):
    s = env.start()
    with pytest.raises(ValueError, match="Initial trial"):
        env.decision(s)
    assert not s.selected("decision") and not env.calls
    s.abandon("Mock no-trial terminal closure")
    assert s.status()["closed"]


def test_frozen_revision_cannot_skip_its_trial_even_when_retaining_initial(env):
    s = env.start()
    first = s.trial("candidates/initial")
    s.feedback(first["run_id"])
    env.revision(s)
    with pytest.raises(ValueError, match="Frozen revision trial"):
        env.decision(s, "initial")
    with pytest.raises(ValueError, match="Frozen revision trial"):
        env.decision(s, "revised")
    assert not s.selected("decision")


@pytest.mark.parametrize("filename", ["RUNTIME_PREFLIGHT.json", "evaluator.py", "ENDPOINT_CONTRACT.json"])
def test_runtime_and_evaluation_contract_are_frozen_controls(env, filename):
    s = env.start()
    with (env.root / filename).open("a", encoding="utf-8") as stream:
        stream.write("\n ")
    with pytest.raises(ValueError, match="commitment changed"):
        s.trial("candidates/initial")
    assert not env.calls
