"""Invented task fixtures for the persistent, nonrefundable calibration budget."""
from __future__ import annotations

import copy
import json

import pytest

from cohort_harness import calibration_budget as budget
from cohort_harness.demo import make_demo


LIMITS = {"sessions": 3, "trials": 6, "executions": 12, "reserved_seconds": 60}
RESERVATION = {"sessions": 1, "trials": 2, "executions": 4, "reserved_seconds": 20}
USAGE = {"sessions": 1, "trials": 1, "executions": 1, "reserved_seconds": 1}
BINDING = {"candidate": "candidates/initial", "generator_sha256": "1" * 64}


def setup_budget(tmp_path, limits=None):
    root = make_demo(tmp_path / "bundle")
    budget.create_budget(root, copy.deepcopy(LIMITS if limits is None else limits))
    return root


def reserve(root, session_id="one"):
    return budget.reserve_session(root, session_id, copy.deepcopy(RESERVATION), copy.deepcopy(BINDING))


def finish(root, session_id="one", status="completed", usage=None):
    return budget.finish_session(root, session_id, status, copy.deepcopy(USAGE if usage is None else usage))


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def test_initial_snapshot(tmp_path):
    root = setup_budget(tmp_path)
    snapshot = budget.get_budget(root)
    assert snapshot["limits"] == LIMITS
    assert snapshot["remaining"] == LIMITS
    assert snapshot["reserved"] == snapshot["used"] == dict.fromkeys(LIMITS, 0)
    assert snapshot["sessions"] == {}
    assert (root / "calibration_budget/config.json").is_file()
    assert (root / "calibration_budget/head.json").is_file()


def test_cross_session_exhaustion(tmp_path):
    limits = {"sessions": 3, "trials": 4, "executions": 8, "reserved_seconds": 40}
    root = setup_budget(tmp_path, limits)
    for session_id in ("first", "second"):
        reserve(root, session_id)
        finish(root, session_id)
    before = budget.get_budget(root)
    assert before["reserved"] == {"sessions": 2, "trials": 4, "executions": 8, "reserved_seconds": 40}
    assert before["remaining"] == {"sessions": 1, "trials": 0, "executions": 0, "reserved_seconds": 0}
    with pytest.raises(ValueError):
        reserve(root, "new_session")
    with pytest.raises(ValueError):
        budget.create_budget(root, LIMITS)
    assert budget.get_budget(root) == before


@pytest.mark.parametrize("status", ["completed", "failed"])
def test_no_refunds(tmp_path, status):
    root = setup_budget(tmp_path)
    reserve(root)
    usage = {"sessions": 1, "trials": 0, "executions": 0, "reserved_seconds": 0}
    finish(root, status=status, usage=usage)
    snapshot = budget.get_budget(root)
    assert snapshot["reserved"] == RESERVATION
    assert snapshot["used"] == usage
    assert snapshot["remaining"] == {key: LIMITS[key] - RESERVATION[key] for key in LIMITS}
    assert snapshot["sessions"]["one"]["status"] == status
    assert snapshot["sessions"]["one"]["usage"] == usage


def test_pending_blocks_dispatch(tmp_path, monkeypatch):
    root = setup_budget(tmp_path)
    reserve(root)
    before = budget.get_budget(root)
    assert before["sessions"]["one"]["status"] == "pending"
    assert "usage" not in before["sessions"]["one"]
    with pytest.raises(ValueError):
        reserve(root, "other")
    with monkeypatch.context() as changed_process:
        changed_process.setattr(budget, "_PROCESS_NONCE", "f" * 64)
        with pytest.raises(ValueError):
            finish(root)
        with pytest.raises(ValueError):
            reserve(root, "after_crash")
    assert budget.get_budget(root) == before
    finish(root, status="failed")
    assert budget.get_budget(root)["sessions"]["one"]["status"] == "failed"


def test_casefold_reuse_rejected(tmp_path):
    root = setup_budget(tmp_path)
    reserve(root, "Study_A")
    finish(root, "Study_A")
    before = budget.get_budget(root)
    for reused in ("Study_A", "study_a", "STUDY_A"):
        with pytest.raises(ValueError):
            reserve(root, reused)
    assert budget.get_budget(root) == before
    reserve(root, "genuinely_new")
    finish(root, "genuinely_new")
    assert len(budget.get_budget(root)["sessions"]) == 2


def test_large_request_not_poison(tmp_path):
    root = setup_budget(tmp_path)
    request = {**RESERVATION, "trials": LIMITS["trials"] + 1}
    with pytest.raises(ValueError):
        budget.reserve_session(root, "too_large", request, BINDING)
    reserve(root, "fits")
    finish(root, "fits")
    assert budget.get_budget(root)["reserved"] == RESERVATION


@pytest.mark.parametrize("bad", [True, False, 0, -1, 1.5, 2**31], ids=["true", "false", "zero", "negative", "float", "overflow"])
def test_bad_limits(tmp_path, bad):
    root = make_demo(tmp_path / "bundle")
    invalid = {**LIMITS, "trials": bad}
    with pytest.raises(ValueError):
        budget.create_budget(root, invalid)
    budget.create_budget(root, LIMITS)
    assert budget.get_budget(root)["remaining"] == LIMITS


@pytest.mark.parametrize("bad", [True, 0, -1, 1.5, 2**31], ids=["bool", "zero", "negative", "float", "overflow"])
def test_bad_reservation(tmp_path, bad):
    root = setup_budget(tmp_path)
    invalid = {**RESERVATION, "executions": bad}
    with pytest.raises(ValueError):
        budget.reserve_session(root, "bad", invalid, BINDING)
    reserve(root)
    finish(root)
    assert budget.get_budget(root)["reserved"] == RESERVATION


@pytest.mark.parametrize("kind", ["missing", "extra", "sessions"])
def test_counter_schema(tmp_path, kind):
    root = setup_budget(tmp_path)
    invalid = copy.deepcopy(RESERVATION)
    if kind == "missing":
        del invalid["executions"]
    elif kind == "extra":
        invalid["silent_extra"] = 1
    else:
        invalid["sessions"] = 2
    with pytest.raises(ValueError):
        budget.reserve_session(root, "bad", invalid, BINDING)
    assert budget.get_budget(root)["reserved"] == dict.fromkeys(LIMITS, 0)


@pytest.mark.parametrize("field,bad", [
    ("trials", True), ("trials", -1), ("trials", 1.5),
    ("trials", 3), ("executions", 5), ("reserved_seconds", 21), ("sessions", 0), ("sessions", 2),
])
def test_invalid_usage(tmp_path, field, bad):
    root = setup_budget(tmp_path)
    reserve(root)
    before = budget.get_budget(root)
    with pytest.raises(ValueError):
        finish(root, usage={**USAGE, field: bad})
    assert budget.get_budget(root) == before
    finish(root)
    assert budget.get_budget(root)["used"] == USAGE


@pytest.mark.parametrize("kind", ["missing", "extra", "status"])
def test_finish_schema(tmp_path, kind):
    root = setup_budget(tmp_path)
    reserve(root)
    usage = copy.deepcopy(USAGE)
    status = "completed"
    if kind == "missing":
        del usage["trials"]
    elif kind == "extra":
        usage["extra"] = 0
    else:
        status = "retry"
    with pytest.raises(ValueError):
        budget.finish_session(root, "one", status, usage)
    finish(root)


@pytest.mark.parametrize("session_id", ["../escape", "nested/name", "", "a.b", "con"])
def test_unsafe_session_names(tmp_path, session_id):
    root = setup_budget(tmp_path)
    with pytest.raises(ValueError):
        reserve(root, session_id)
    assert budget.get_budget(root)["sessions"] == {}


@pytest.mark.parametrize("binding", [{}, {"generator_sha256": "ABC"}, {"generator_sha256": "A" * 64},
                                      {"generator_sha256": True}, {"candidate": "candidates/initial", "bad_sha256": "0" * 63}])
def test_bad_binding(tmp_path, binding):
    root = setup_budget(tmp_path)
    with pytest.raises(ValueError):
        budget.reserve_session(root, "one", RESERVATION, binding)
    assert budget.get_budget(root)["sessions"] == {}


def test_terminal_cannot_finish_twice(tmp_path):
    root = setup_budget(tmp_path)
    reserve(root)
    finish(root)
    before = budget.get_budget(root)
    with pytest.raises(ValueError):
        finish(root, status="failed")
    assert budget.get_budget(root) == before


@pytest.mark.parametrize("artifact", ["config.json", "events/00000001.json", "head.json"])
def test_tampered_envelope(tmp_path, artifact):
    root = setup_budget(tmp_path)
    reserve(root)
    finish(root)
    path = root / "calibration_budget" / artifact
    envelope = json.loads(path.read_text(encoding="utf-8"))
    envelope["payload"]["tampered"] = True
    write_json(path, envelope)
    with pytest.raises(ValueError):
        budget.get_budget(root)
    with pytest.raises(ValueError):
        reserve(root, "later")


def test_task_binding(tmp_path):
    root = setup_budget(tmp_path)
    path = root / "task.json"
    task = json.loads(path.read_text(encoding="utf-8"))
    task["population"] = "Changed invented task after budget creation"
    write_json(path, task)
    with pytest.raises(ValueError):
        budget.get_budget(root)
    with pytest.raises(ValueError):
        reserve(root)


def test_deleted_tail(tmp_path):
    root = setup_budget(tmp_path)
    reserve(root)
    finish(root)
    event = root / "calibration_budget/events/00000002.json"
    assert event.is_file()
    event.unlink()  # Tamper only with this newly created synthetic ledger.
    with pytest.raises(ValueError):
        budget.get_budget(root)


def test_unexpected_freeze_file(tmp_path):
    root = setup_budget(tmp_path)
    (root / "calibration_budget/freeze.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError):
        budget.get_budget(root)


def test_existing_operation_lock(tmp_path):
    root = setup_budget(tmp_path)
    lock = root / "calibration_budget/.operation.lock"
    lock.write_text("interrupted operation", encoding="utf-8")
    for operation in (lambda: budget.get_budget(root), lambda: reserve(root),
                      lambda: budget.create_budget(root, LIMITS)):
        with pytest.raises(ValueError):
            operation()
    assert lock.read_text(encoding="utf-8") == "interrupted operation"


@pytest.mark.parametrize("operation", ["reserve", "finish"])
def test_interrupted_commit_blocks(tmp_path, monkeypatch, operation):
    root = setup_budget(tmp_path)
    if operation == "finish":
        reserve(root)
    original_config = (root / "calibration_budget/config.json").read_bytes()
    original_write = budget._write_atomic

    def interrupt_checkpoint(directory, name, value, **kwargs):
        if name == "head.json":
            raise OSError("Invented interruption after immutable event installation")
        return original_write(directory, name, value, **kwargs)

    with monkeypatch.context() as interrupted:
        interrupted.setattr(budget, "_write_atomic", interrupt_checkpoint)
        with pytest.raises(OSError, match="Invented interruption"):
            reserve(root) if operation == "reserve" else finish(root)
    ledger = root / "calibration_budget"
    assert (ledger / ".operation.lock").is_file()
    assert (ledger / "config.json").read_bytes() == original_config
    event_name = "00000001.json" if operation == "reserve" else "00000002.json"
    assert (ledger / "events" / event_name).is_file()
    for attempt in (lambda: budget.get_budget(root), lambda: reserve(root, "retry"),
                    lambda: finish(root), lambda: budget.create_budget(root, LIMITS)):
        with pytest.raises(ValueError):
            attempt()


@pytest.mark.parametrize("artifact", ["config.json", "events/00000001.json"])
def test_resealed_tamper_chain(tmp_path, artifact):
    root = setup_budget(tmp_path)
    reserve(root)
    finish(root)
    path = root / "calibration_budget" / artifact
    envelope = json.loads(path.read_text(encoding="utf-8"))
    if artifact == "config.json":
        envelope["payload"]["limits"]["trials"] += 1
    else:
        envelope["payload"]["binding"]["generator_sha256"] = "2" * 64
    # The edited document is internally self-consistent; only the retained
    # next-event/head commitments can detect the substituted content.
    envelope["sha256"] = budget._digest(envelope["payload"])
    write_json(path, envelope)
    with pytest.raises(ValueError, match="binding changed|hash chain changed"):
        budget.get_budget(root)


def test_linked_ledger_rejected(tmp_path):
    root = make_demo(tmp_path / "bundle")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    try:
        (root / "calibration_budget").symlink_to(elsewhere, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Directory symlink creation is unavailable for this test user")
    with pytest.raises(ValueError):
        budget.create_budget(root, LIMITS)
    assert list(elsewhere.iterdir()) == []
