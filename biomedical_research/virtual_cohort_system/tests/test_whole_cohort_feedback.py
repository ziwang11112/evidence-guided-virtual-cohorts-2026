"""Invented whole-cohort feedback tests; mocked execution is not isolation evidence."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil

import numpy as np
import pandas as pd
import pytest

from cohort_harness import execution as ex
from cohort_harness import whole_cohort_feedback as wc
from cohort_harness.__main__ import validate_bundle
from cohort_harness.demo import make_demo
from cohort_harness.lifecycle import freeze_candidate, read_json, sha256, verify_candidate


EXAMPLE = Path(__file__).resolve().parents[1] / "examples/m17a_whole_cohort.py"
_loader = importlib.util.spec_from_file_location("m17a_example", EXAMPLE)
_example = importlib.util.module_from_spec(_loader)
_loader.loader.exec_module(_example)


def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def frame(n=8, constant=False):
    x = np.arange(n, dtype=float) - 3.5
    group = np.array([0, 1] * (n // 2))
    y = np.repeat(2.0, n) if constant else 1.0 + 0.75 * x + 0.6 * group
    return pd.DataFrame({"sample_id": [f"fixture_{i}" for i in range(n)], "x": x, "group": group, "y": y})


def prepare(tmp_path, route="direct", mutation=None, constant=False):
    root = _example.prepare(tmp_path / "bundle", n_rows=8)
    candidate = root / "candidates/initial"
    if route == "direct":
        (candidate / "generator.py").unlink()
        frame(constant=constant).to_csv(candidate / "generated.csv", index=False)
    if mutation:
        mutation(root, candidate)
    freeze_candidate(root, candidate)
    return root, candidate


def execute_direct(root, candidate):
    receipt = ex.run_candidate(root, candidate, "run01", 17001)
    assert receipt["status"] == "success"
    return receipt


def change_plan(mutator):
    def modify(root, candidate):
        plan = read_json(candidate / wc.PLAN)
        mutator(plan)
        write(candidate / wc.PLAN, plan)
    return modify


def fake_program_backend(monkeypatch, *, returncode=0):
    monkeypatch.setattr(ex, "_runtime_manifest", lambda runtime: {"mock": True, "not_isolation_evidence": True})
    def capture(command, cwd, timeout, limit, stdout_path, stderr_path):
        assert read_json(cwd / "input/task.json")["mode"] == "whole_cohort"
        assert not (cwd / "input/observed.csv").exists()
        frame().to_csv(cwd / "output/generated.csv", index=False)
        write(cwd / "output/worker_report.json", {"status": "completed", "generator_started": True})
        stdout_path.write_bytes(b"mocked boundary only; no generator code executed\n")
        stderr_path.write_bytes(b"")
        return {"returncode": returncode, "host_timeout": False, "logs": {}}
    monkeypatch.setattr(ex, "_capture", capture)


def test_prepare_only_has_no_individual_table_and_program_validates(tmp_path):
    root = _example.prepare(tmp_path / "prepare_only", 8)
    candidate = root / "candidates/initial"
    assert not list(root.rglob("*.csv"))
    assert not (root / "executions").exists()
    assert validate_bundle(root, candidate)["route"] == "program"


def test_direct_feedback_is_recomputed_and_freeze_unchanged(tmp_path):
    root, candidate = prepare(tmp_path)
    before = {p.name: sha256(p) for p in candidate.iterdir()}
    execute_direct(root, candidate)
    report = wc.collect_feedback(root, "initial", "run01", "feedback01")
    assert report["route"] == "generated.csv"
    assert report["generator_execution_recorded"] is False
    assert report["output_link_verified"] is True
    assert report["agent_authorship_verified"] is False
    assert report["n_computable"] == 5
    assert report["n_not_computable"] == 0
    values = {row["id"]: row["calculation"]["value"] for row in report["checks"]}
    assert values["x_mean"] == 0
    assert values["y_mean"] == pytest.approx(1.3)
    assert values["adjusted_slope"] == pytest.approx(0.75)
    assert values["x_sd"] == pytest.approx(np.sqrt(6))
    assert all(row["status"] == "approximate" for row in report["checks"])
    assert before == {p.name: sha256(p) for p in candidate.iterdir()}
    assert wc.verify_feedback(root, "feedback01", candidate=candidate, run_id="run01") == report
    verify_candidate(root, candidate)


def test_mocked_program_output_stages_no_observed_table(tmp_path, monkeypatch):
    root, candidate = prepare(tmp_path, route="program")
    fake_program_backend(monkeypatch)
    receipt = ex.run_candidate(root, candidate, "run01", 17001)
    assert receipt["status"] == "success"
    report = wc.collect_feedback(root, candidate, "run01", "feedback01")
    assert report["route"] == "generator.py"
    assert report["generator_execution_recorded"] is True
    assert not (root / "executions/run01/input/observed.csv").exists()
    # This flag is inherited from a mocked receipt, not a real execution claim.
    assert report["agent_isolation"] == "not_provided"


def test_wrong_mode_rejected(tmp_path):
    root = make_demo(tmp_path / "enrichment")
    candidate = root / "candidates/initial"
    freeze_candidate(root, candidate)
    with pytest.raises(ValueError, match="whole_cohort"):
        wc.collect_feedback(root, candidate, "run01", "feedback01")


def test_whole_cohort_rejects_added_observed_file(tmp_path):
    root, candidate = prepare(tmp_path)
    execute_direct(root, candidate)
    (root / "observed.csv").write_text("sample_id,x\nhidden,1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="observed.csv"):
        wc.collect_feedback(root, candidate, "run01", "feedback01")


def test_whole_cohort_rejects_observed_column_role(tmp_path):
    root = _example.prepare(tmp_path / "wrong_role", 8)
    task = read_json(root / "task.json")
    task["columns"][1]["role"] = "observed"
    write(root / "task.json", task)
    with pytest.raises(ValueError, match="no observed columns"):
        validate_bundle(root, root / "candidates/initial")


def test_execution_for_other_candidate_rejected(tmp_path):
    root, candidate = prepare(tmp_path)
    other = root / "candidates/other"
    other.mkdir()
    for path in candidate.iterdir():
        if path.name != "freeze.json":
            shutil.copyfile(path, other / path.name)
    freeze_candidate(root, other)
    ex.run_candidate(root, other, "run01", 17001)
    with pytest.raises(ValueError, match="different candidate"):
        wc.collect_feedback(root, candidate, "run01", "feedback01")


def test_failed_execution_is_not_accepted_as_feedback(tmp_path, monkeypatch):
    root, candidate = prepare(tmp_path, route="program")
    fake_program_backend(monkeypatch, returncode=1)
    receipt = ex.run_candidate(root, candidate, "run01", 17001)
    assert receipt["status"] == "failed"
    assert ex.verify_execution(root, "run01")["status"] == "failed"
    with pytest.raises(ValueError, match="successful verified execution"):
        wc.collect_feedback(root, candidate, "run01", "feedback01")


@pytest.mark.parametrize("mutation,match", [
    (lambda p: p["checks"][0]["operator"].update(unit="wrong"), "unit-label"),
    (lambda p: p["checks"][0]["operator"].update(kind="sd"), "statistic-kind"),
    (lambda p: p["checks"][0].update(evidence_id="missing"), "Unknown feedback evidence"),
    (lambda p: p["checks"][0].update(status="computed"), "approximate status"),
    (lambda p: p.update(population="another population"), "Feedback population"),
    (lambda p: p["measurement"].update(mode="conversion"), "identity measurement"),
    (lambda p: p["checks"].append(dict(p["checks"][0])), "Duplicate feedback"),
    (lambda p: p["checks"][0]["operator"].update(extra=True), "Unexpected fields"),
])
def test_invalid_frozen_recipe_fails_before_writing_feedback(tmp_path, mutation, match):
    root, candidate = prepare(tmp_path, mutation=change_plan(mutation))
    execute_direct(root, candidate)
    with pytest.raises(ValueError, match=match):
        wc.collect_feedback(root, candidate, "run01", "bad")
    assert not (root / wc.FOLDER / "bad").exists()


def test_runtime_undefined_statistic_is_retained(tmp_path):
    def empty_selection(plan):
        plan["checks"][0]["operator"]["selection"] = [{"column": "x", "op": "gt", "value": 10000}]
    root, candidate = prepare(tmp_path, mutation=change_plan(empty_selection))
    execute_direct(root, candidate)
    report = wc.collect_feedback(root, candidate, "run01", "feedback01")
    row = report["checks"][0]
    assert row["declared_status"] == "approximate"
    assert row["status"] == "not_computable"
    assert row["calculation"] is None and row["difference"] is None
    assert "No complete selected rows" in row["unavailable_reason"]
    assert report["n_computable"] == 4 and report["n_not_computable"] == 1
    assert wc.verify_feedback(root, "feedback01") == report


def test_declared_not_computable_preserves_reason(tmp_path):
    def unsupported(plan):
        plan["checks"][0].update(status="not_computable", operator=None,
                                  reason="Deliberately deferred for this interface test.")
    root, candidate = prepare(tmp_path, mutation=change_plan(unsupported))
    execute_direct(root, candidate)
    row = wc.collect_feedback(root, candidate, "run01", "feedback01")["checks"][0]
    assert row["status"] == "not_computable"
    assert row["unavailable_reason"] == row["reason"]


@pytest.mark.parametrize("mutator", [
    lambda r: r["checks"][0]["calculation"].update(value=999),
    lambda r: r["checks"].pop(),
    lambda r: r.update(generator_execution_recorded=True),
    lambda r: r.update(source_context_validity="certified"),
    lambda r: r["bindings"].update(generated_table_sha256="0" * 64),
    lambda r: r["engine_sha256"].update(**{"source_checks.py": "0" * 64}),
])
def test_report_tampering_is_detected(tmp_path, mutator):
    root, candidate = prepare(tmp_path)
    execute_direct(root, candidate)
    report = wc.collect_feedback(root, candidate, "run01", "feedback01")
    mutator(report)
    write(root / wc.FOLDER / "feedback01/feedback.json", report)
    with pytest.raises(ValueError, match="recomputed"):
        wc.verify_feedback(root, "feedback01")


def test_output_tampering_is_detected(tmp_path):
    root, candidate = prepare(tmp_path)
    execute_direct(root, candidate)
    wc.collect_feedback(root, candidate, "run01", "feedback01")
    with (root / "executions/run01/output/generated.csv").open("a") as stream:
        stream.write("tamper\n")
    with pytest.raises(ValueError, match="hash changed"):
        wc.verify_feedback(root, "feedback01")


def test_candidate_recipe_tampering_is_detected(tmp_path):
    root, candidate = prepare(tmp_path)
    execute_direct(root, candidate)
    wc.collect_feedback(root, candidate, "run01", "feedback01")
    with (candidate / wc.PLAN).open("a") as stream:
        stream.write(" \n")
    with pytest.raises(ValueError, match="commitments changed"):
        wc.verify_feedback(root, "feedback01")


@pytest.mark.parametrize("feedback_id", ["feedback01", "../outside", "a/b", "C:/bad", ""])
def test_no_overwrite_or_path_escape(tmp_path, feedback_id):
    root, candidate = prepare(tmp_path)
    execute_direct(root, candidate)
    original = wc.collect_feedback(root, candidate, "run01", "feedback01")
    with pytest.raises(ValueError):
        wc.collect_feedback(root, candidate, "run01", feedback_id)
    assert wc.verify_feedback(root, "feedback01") == original


def test_verify_expected_run_and_extra_files(tmp_path):
    root, candidate = prepare(tmp_path)
    execute_direct(root, candidate)
    wc.collect_feedback(root, candidate, "run01", "feedback01")
    with pytest.raises(ValueError, match="different execution"):
        wc.verify_feedback(root, "feedback01", run_id="other")
    (root / wc.FOLDER / "feedback01/extra.txt").write_text("unexpected", encoding="utf-8")
    with pytest.raises(ValueError, match="artifact set"):
        wc.verify_feedback(root, "feedback01")


def test_cli_collect_and_verify(tmp_path, capsys):
    root, candidate = prepare(tmp_path)
    execute_direct(root, candidate)
    args = ["--bundle", str(root), "--candidate", "initial", "--run-id", "run01", "--feedback-id", "feedback01"]
    assert wc.main(["collect", *args]) == 0
    first = json.loads(capsys.readouterr().out)
    assert wc.main(["verify", *args]) == 0
    second = json.loads(capsys.readouterr().out)
    assert first == second
