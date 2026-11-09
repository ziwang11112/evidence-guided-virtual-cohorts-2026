"""Evaluator-only checks using invented aggregates and mocked private-table reads.

No existing clinical reference payload, authored model, historical evaluator,
or actual pilot private output is read or executed by these tests.
"""
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest


def load_evaluator(monkeypatch):
    root = Path(__file__).parent
    spec = importlib.util.spec_from_file_location("rubric_evaluator_test_runner", root / "runner.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    monkeypatch.setitem(sys.modules, "runner", runner)
    spec = importlib.util.spec_from_file_location("rubric_evaluator_under_test", root / "evaluate.py")
    evaluator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(evaluator)
    return evaluator


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf8")


@pytest.fixture
def evaluation(tmp_path, monkeypatch):
    evaluator = load_evaluator(monkeypatch)
    runner = evaluator.runner
    monkeypatch.setattr(evaluator, "ROOT", tmp_path)
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    analyses = [{"id": "invented_contrast_" + str(index), "unit": "1"} for index in (1, 2, 3)]
    schema = {
        "ENSANUT2018": {"analyses": analyses, "diagnostics": [{"id": "invented_dispersion", "unit": "1"}]},
        "Turkana": {"analyses": analyses, "diagnostics": [
            {"id": "total_cholesterol.sd_sample", "unit": "1"},
            {"id": "hdl_cholesterol.sd_sample", "unit": "1"},
            {"id": "invented_unavailable_diagnostic", "unit": "1"}]},
    }
    protocol = {"cases": evaluator.CASES, "arms": {"A": "invented control", "B": "invented rubric", "C": "invented procedure"}}
    put(tmp_path / "PROTOCOL.json", protocol)
    put(tmp_path / "ENDPOINT_CONTRACT.json", {"cases": schema})
    paths = {"ENSANUT2018": tmp_path / "invented_reference_h.json", "Turkana": tmp_path / "invented_reference_l.json"}
    h = {item["id"]: {"unit": "1", "value": 2.0} for category in evaluator.CATEGORIES for item in schema["ENSANUT2018"][category]}
    l = {"estimands": {item["id"]: {"unit": "1", "estimate": 2.0} for item in analyses},
         "metric_denominators": {column: {"sample_sd": 2.0} for column in ("total_cholesterol", "hdl_cholesterol")}}
    h["invented_contrast_1"]["interval"] = {"status": "available", "lower": 1.0, "upper": 3.0,
        "direction": "positive", "meaning": "Invented empirical stability interval", "equivalence_margin": False}
    l["estimands"]["invented_contrast_1"]["interval"] = {"status": "available", "lower": 1.0, "upper": 3.0,
        "standard_error": 0.5, "normal_multiplier": 2.0, "nominal_level": 0.95,
        "kind": "invented assumption-conditional sensitivity interval", "reason": None}
    put(paths["ENSANUT2018"], {"invented": h})
    put(paths["Turkana"], {"invented": l})
    bindings = {case: {"path": str(path), "selector": ["invented"], "sha256": runner.sha(path)} for case, path in paths.items()}
    put(tmp_path / "REFERENCE_BINDINGS.json", bindings)
    monkeypatch.setattr(evaluator, "REFERENCE_LOCATIONS", {case: (path, ["invented"]) for case, path in paths.items()})
    lock = {"records": {name: runner.sha(tmp_path / name) for name in ("ENDPOINT_CONTRACT.json", "REFERENCE_BINDINGS.json")}}
    put(tmp_path / "BATCH_LOCK.json", lock)
    closed = {"physical_attempts": 18, "records": []}
    attempts, receipts = {}, {}
    for author in runner.AUTHORS:
        for seed in runner.SEEDS:
            run = tmp_path / "private_runs" / author / f"seed_{seed}"
            status = "failed" if (author, seed) == ("HA", 9302) else "success"
            receipt = {"status": status, "generated_sha256": "b" * 64,
                       "error": {"type": "InventedError", "message": "DO_NOT_PUBLISH_PRIVATE_ROW_CONTENT"} if status == "failed" else None}
            put(run / "execution.json", receipt)
            attempts[(author, seed)] = run
            receipts[(author, seed)] = receipt
            closed["records"].append({"author": author, "seed": seed, "execution_sha256": runner.sha(run / "execution.json")})
    put(tmp_path / "BATCH_CLOSURE.json", closed)
    calls = {"closure": 0, "reference_reads": [], "table_reads": []}
    def gate():
        calls["closure"] += 1
        return closed
    monkeypatch.setattr(runner, "closure_gate", gate)
    monkeypatch.setattr(runner, "verify_batch", lambda: (protocol, lock))
    monkeypatch.setattr(runner, "inventory", lambda: attempts)
    monkeypatch.setattr(runner, "verify_execution", lambda author, seed: receipts[(author, seed)])
    monkeypatch.setattr(runner, "task_contract", lambda author: {"invented": author})
    monkeypatch.setattr(runner.execution, "_csv_guard", lambda *args: None)
    monkeypatch.setattr(runner.contracts, "validate_output", lambda *args: None)
    def table_read(path, task, **kwargs):
        assert calls["closure"] > 0
        calls["table_reads"].append(str(path))
        return range(3000)  # Length-only placeholder; no clinical row data.
    monkeypatch.setattr(runner.lifecycle, "read_table", table_read)
    original_read = runner.read
    def tracked_read(path):
        if Path(path) in paths.values():
            assert calls["closure"] > 0
            calls["reference_reads"].append(str(path))
        return original_read(path)
    monkeypatch.setattr(runner, "read", tracked_read)
    def provider(case):
        def generated_statistics(frame):
            return {category: [{**item, "value": 3.0, "status": "computed", "n": len(frame)}
                               for item in schema[case][category]] for category in evaluator.CATEGORIES} | {
                       "quality": {"duplicate_measurement_rows": 0},
                       "unapproved_extra": "DO_NOT_PUBLISH_PROVIDER_PRIVATE_CONTENT"}
        return SimpleNamespace(generated_statistics=generated_statistics)
    monkeypatch.setattr(evaluator, "load_provider", provider)
    return evaluator, schema, lock, calls


def test_failed_closure_prevents_all_evaluator_reads_and_writes(evaluation, monkeypatch):
    evaluator, _, _, calls = evaluation
    monkeypatch.setattr(evaluator.runner, "closure_gate", lambda: (_ for _ in ()).throw(ValueError("not closed")))
    monkeypatch.setattr(evaluator.runner, "read", lambda *args: pytest.fail("No reads before closure"))
    with pytest.raises(ValueError, match="not closed"):
        evaluator.evaluate()
    assert calls["reference_reads"] == calls["table_reads"] == []
    assert not (evaluator.ROOT / "EVALUATION_STARTED.json").exists()


def test_reference_mapping_keeps_unmatched_diagnostics_unavailable(evaluation):
    evaluator, schema, lock, calls = evaluation
    references, _ = evaluator.load_references(schema, lock)
    assert calls["closure"] == 1 and len(calls["reference_reads"]) == 2
    lipid = references["Turkana"]
    assert lipid["total_cholesterol.sd_sample"]["value"] == 2.0
    assert lipid["hdl_cholesterol.sd_sample"]["value"] == 2.0
    assert lipid["invented_unavailable_diagnostic"]["status"] == "unavailable"
    assert lipid["invented_unavailable_diagnostic"]["value"] is None
    assert lipid["invented_contrast_1"]["uncertainty"]["standard_error"]["value"] == 0.5
    assert lipid["invented_contrast_1"]["uncertainty"]["interval"]["nominal_level"] == 0.95
    h = references["ENSANUT2018"]
    assert h["invented_contrast_1"]["uncertainty"]["interval"]["meaning"] == "Invented empirical stability interval"
    assert h["invented_contrast_1"]["uncertainty"]["standard_error"]["status"] == "unavailable"
    assert h["invented_dispersion"]["uncertainty"]["interval"]["status"] == "unavailable"


def test_all_slots_endpoints_failures_and_denominators_are_retained(evaluation):
    evaluator, schema, _, calls = evaluation
    result = evaluator.evaluate()
    report = json.loads((evaluator.ROOT / "EVALUATION.json").read_text())
    text = (evaluator.ROOT / "EVALUATION.md").read_text()
    assert result["scheduled_slots"] == 18
    assert result["successful_executions"] == 17
    assert len(calls["table_reads"]) == 17
    assert len(report["all_slots"]) == 18
    assert sum(len(slot[category]) for slot in report["all_slots"] for category in evaluator.CATEGORIES) == 9 * 4 + 9 * 6
    failed = next(slot for slot in report["all_slots"] if (slot["author_id"], slot["seed"]) == ("HA", 9302))
    assert failed["execution_status"] == "failed"
    assert all(item["status"] == "unavailable" for category in evaluator.CATEGORIES for item in failed[category])
    summary = next(item for item in report["construction_summaries"] if item["author_id"] == "HA" and item["id"] == "invented_contrast_1")
    assert summary["available_generated_seeds"] == summary["comparable_reference_seeds"] == 2
    assert summary["mean_signed_difference"] == summary["mean_absolute_difference"] == 1.0
    assert "DO_NOT_PUBLISH" not in json.dumps(report) + text
    assert "not three independent author constructions" in text
    assert "Every scheduled endpoint by seed" in text
    assert "Supplied uncertainty for every endpoint" in text
    assert all(row["uncertainty"]["interval"]["status"] == "unavailable"
               for row in summary["generated_uncertainty_by_seed"])
    assert report["private_rows_published"] is False
    with pytest.raises(ValueError, match="already reserved"):
        evaluator.evaluate()


def test_endpoint_unit_or_coverage_mismatch_rejected(evaluation):
    evaluator, schema, _, _ = evaluation
    payload = {category: [{**item, "value": 1.0, "status": "computed"} for item in schema["ENSANUT2018"][category]]
               for category in evaluator.CATEGORIES}
    payload["analyses"][0]["unit"] = "wrong"
    with pytest.raises(ValueError, match="unit mismatch"):
        evaluator.normalize_payload(payload, schema["ENSANUT2018"])


def test_reference_hash_mismatch_stops_before_payload_read(evaluation):
    evaluator, schema, lock, calls = evaluation
    (evaluator.ROOT / "invented_reference_h.json").write_text("{}")
    with pytest.raises(ValueError, match="aggregate reference changed"):
        evaluator.load_references(schema, lock)
    assert calls["reference_reads"] == []


def test_unsealed_reference_bindings_rejected(evaluation):
    evaluator, schema, lock, calls = evaluation
    lock["records"].pop("REFERENCE_BINDINGS.json")
    with pytest.raises(ValueError, match="not sealed"):
        evaluator.load_references(schema, lock)
    assert calls["reference_reads"] == []


def test_generated_supplied_uncertainty_preserved_without_inferred_interval(evaluation):
    evaluator, schema, _, _ = evaluation
    payload = {category: [{**item, "value": 1.0, "status": "computed"} for item in schema["ENSANUT2018"][category]]
               for category in evaluator.CATEGORIES}
    payload["analyses"][0]["standard_error"] = 0.25
    result = evaluator.normalize_payload(payload, schema["ENSANUT2018"])
    uncertainty = result["analyses"][0]["generated_uncertainty"]
    assert uncertainty["standard_error"]["value"] == 0.25
    assert uncertainty["interval"]["status"] == "unavailable"
    assert uncertainty["interval"]["lower"] is uncertainty["interval"]["upper"] is None
