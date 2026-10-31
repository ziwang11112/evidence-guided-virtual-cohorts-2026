"""Independent C5 controller failure checks; all execution calls are mocked."""
import json
from pathlib import Path

import pytest

from work.c5 import run_unit as controller


RUNS = [
    {"run_id": f"parent_r{i}", "arm": "parent", "replicate": i,
     "seed": 25100 + i, "parent_run_id": None}
    for i in range(1, 4)
] + [
    {"run_id": f"joint_r{i}", "arm": "joint", "replicate": i,
     "seed": 25200 + i, "parent_run_id": None}
    for i in range(1, 4)
] + [
    {"run_id": f"extended_r{i}", "arm": "extended", "replicate": i,
     "seed": 25300 + i, "parent_run_id": f"parent_r{i}"}
    for i in range(1, 4)
]


def prepare(tmp_path, monkeypatch):
    # Deliberately independent dummy run schedule, not scientific C5 inputs.
    root = tmp_path / "controller_fixture"
    root.mkdir()
    (root / "author").mkdir()
    (root / "author/request_decisions.json").write_text(json.dumps({
        "requests": [{"request_id": "2", "raw_request": "Invented routing fixture",
                      "decision": {"action": "extend"}}]}), encoding="utf-8")
    (root / "RUN_PLAN.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(controller, "verify_plan", lambda _: {"runs": RUNS})
    return root


@pytest.mark.parametrize("fail_at", [1, 3, 6])
def test_native_failure_closes_remaining_slots_without_retry(tmp_path, monkeypatch, fail_at):
    root = prepare(tmp_path, monkeypatch)
    calls = []
    monkeypatch.setattr(controller.execution, "run_candidate",
                        lambda bundle, candidate, run_id, seed: calls.append(run_id))

    def record(bundle, item):
        result = dict(item, status="failed" if len(calls) == fail_at else "success")
        if result["status"] == "success":
            result.update(path="mock-only.csv", sha256="0" * 64, n_rows=2000)
        return result

    monkeypatch.setattr(controller, "record_execution", record)
    result = controller.run(root)
    assert result == {"status": "closed_execution_failure", "runs_attempted": fail_at}
    manifest = json.loads((root / "terminal_failure_manifest.json").read_text())
    assert len(manifest["records"]) == 9
    assert len(calls) == fail_at
    assert manifest["records"][fail_at - 1]["status"] == "failed"
    assert all(x["status"] == "not_attempted_after_failure" for x in manifest["records"][fail_at:])
    assert manifest["scientific_retries"] == 0 and not manifest["analytic_truth_revealed"]
    assert not (root / "final_output_manifest.json").exists()
    assert not (root / "reveal_authorization.json").exists()
    with pytest.raises(FileExistsError):
        controller.run(root)
    assert len(calls) == fail_at


def test_unexpected_native_exception_also_closes_all_slots(tmp_path, monkeypatch):
    root = prepare(tmp_path, monkeypatch)

    def unavailable(*args, **kwargs):
        raise RuntimeError("Explicitly mocked controller exception")

    monkeypatch.setattr(controller.execution, "run_candidate", unavailable)
    result = controller.run(root)
    manifest = json.loads((root / "terminal_failure_manifest.json").read_text())
    assert result["runs_attempted"] == 1
    assert manifest["records"][0]["status"] == "controller_or_execution_failure"
    assert len(manifest["records"]) == 9
    assert not (root / "final_output_manifest.json").exists()
    assert not (root / "reveal_authorization.json").exists()

