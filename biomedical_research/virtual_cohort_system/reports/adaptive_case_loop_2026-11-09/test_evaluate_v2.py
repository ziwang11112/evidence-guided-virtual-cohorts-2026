"""Independent evaluator checks using only invented scalar payloads and stubs.

No real reference, generated table, author program or provider is read/executed.
"""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def evaluator(tmp_path, monkeypatch):
    path = Path(__file__).with_name("evaluate_v2.py")
    spec = importlib.util.spec_from_file_location("independent_adaptive_evaluator_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "REFERENCE", tmp_path / "invented_reference.json")
    plan = {
        "analyses": [{"id": f"toy_analysis_{i}", "unit": "1"} for i in range(3)],
        "diagnostics": [{"id": f"toy_diagnostic_{i}", "unit": "1"} for i in range(19)] + [
            {"id": "total_cholesterol.sd_sample", "unit": "mg/dL"},
            {"id": "hdl_cholesterol.sd_sample", "unit": "mg/dL"},
            {"id": "total_cholesterol.conditional_rms", "unit": "mg/dL"},
            {"id": "hdl_cholesterol.conditional_rms", "unit": "mg/dL"}],
    }
    refs = {item["id"]: {"reference_value": 2.0 if category == "analyses" else None,
                          "reference_interval": None}
            for category, items in plan.items() for item in items}
    return module, plan, refs


def payload(plan, available=True):
    return {category: [{**item, "value": 3.0 if available else None,
                        "status": "computed" if available else "unavailable"}
                       for item in items] for category, items in plan.items()}


def test_failed_attempt_retains_all_endpoints(evaluator):
    module, plan, refs = evaluator
    result = module.normalize(None, plan, refs, failed_reason="execution_failed")
    assert len(result["analyses"]) == 3 and len(result["diagnostics"]) == 23
    assert all(item["value"] is None and item["status"] == "unavailable"
               and item["difference"] is None and item["comparison"] == "unavailable"
               and item["reason"] == "execution_failed"
               for rows in result.values() for item in rows)


def test_all_unavailable_endpoints_remain_in_stage_summary(evaluator):
    module, plan, refs = evaluator
    normalized = module.normalize(payload(plan, available=False), plan, refs)
    runs = [{"candidate": "candidates/toy", "status": "success", **normalized} for _ in range(3)]
    stage = module.summarize(runs, ["candidates/toy"], "candidates/toy", plan, refs)[0]
    assert len(stage["analyses"]) == 3 and len(stage["diagnostics"]) == 23
    assert all(item["status"] == "unavailable" and item["mean"] is None
               and item["n_draws"] == 0 and item["n_unavailable"] == 3
               for category in plan for item in stage[category])


def test_comparison_requires_both_values_and_preserves_supplied_interval(evaluator):
    module, plan, refs = evaluator
    interval = {"status": "available", "lower": -1.0, "upper": 5.0,
                "kind": "invented conditional sensitivity", "standard_error": 1.5}
    refs["toy_analysis_0"]["reference_interval"] = interval
    raw = payload(plan)
    raw["analyses"][1].update(value=None, status="unavailable")
    result = module.normalize(raw, plan, refs)
    assert result["analyses"][0]["difference"] == 1.0
    assert result["analyses"][0]["reference_interval"] == interval
    assert result["analyses"][1]["comparison"] == "unavailable"
    assert result["analyses"][1]["difference"] is None
    assert all(item["comparison"] == "unavailable" and item["difference"] is None
               for item in result["diagnostics"])


def test_coverage_or_unit_error_is_rejected(evaluator):
    module, plan, refs = evaluator
    raw = payload(plan)
    raw["analyses"][0]["unit"] = "wrong"
    with pytest.raises(ValueError, match="unit mismatch"):
        module.normalize(raw, plan, refs)
    raw = payload(plan)
    raw["diagnostics"].pop()
    with pytest.raises(ValueError, match="coverage mismatch"):
        module.normalize(raw, plan, refs)


def test_gate_without_closure_never_touches_reference(evaluator, monkeypatch):
    module, _, _ = evaluator
    (module.ROOT / "DESIGN_LOCK.json").write_text("{}")
    (module.ROOT / "EVALUATOR_AMENDMENT.json").write_text('{"files": {}}')
    original_read, original_sha = module.read, module.sha
    def guarded_read(path):
        assert Path(path) != module.REFERENCE, "Reference payload accessed before closure"
        return original_read(path)
    def guarded_sha(path):
        assert Path(path) != module.REFERENCE, "Reference bytes accessed before closure"
        return original_sha(path)
    monkeypatch.setattr(module, "read", guarded_read)
    monkeypatch.setattr(module, "sha", guarded_sha)
    with pytest.raises(FileNotFoundError):
        module.gate()


def test_main_failed_gate_prevents_reference_and_adapter_access(evaluator, monkeypatch):
    module, _, _ = evaluator
    monkeypatch.setattr(module, "gate", lambda: (_ for _ in ()).throw(ValueError("not closed")))
    monkeypatch.setattr(module, "read", lambda *_: pytest.fail("No input read after failed gate"))
    monkeypatch.setattr(module.importlib.util, "spec_from_file_location",
                        lambda *_: pytest.fail("No adapter import after failed gate"))
    with pytest.raises(ValueError, match="not closed"):
        module.main()
    assert not (module.ROOT / "EVALUATION.json").exists()


def test_markdown_shows_conditional_residual_dispersion(evaluator, monkeypatch):
    module, plan, _ = evaluator
    protocol = {"required_analyses": [{"id": x["id"], "analysis_unit": x["unit"]} for x in plan["analyses"]],
                "required_diagnostics": plan["diagnostics"]}
    (module.ROOT / "PROTOCOL.json").write_text(json.dumps(protocol))
    source = {"estimands": {x["id"]: {"estimate": 2.0, "unit": "1", "interval": None}
                            for x in plan["analyses"]},
              "metric_denominators": {col: {"sample_sd": 2.0}
                                      for col in ["total_cholesterol", "hdl_cholesterol"]}}
    module.REFERENCE.write_text(json.dumps({"references": {"K02": source}}))
    closure = {"candidates": ["candidates/toy"], "final_candidate": "candidates/toy", "runs": ["toy_seed"]}
    monkeypatch.setattr(module, "gate", lambda: (closure, module.ROOT / "invented_bundle"))
    monkeypatch.setattr(module, "sha", lambda _: "a" * 64)
    monkeypatch.setattr(module.execution, "verify_execution", lambda *_: {
        "candidate": "candidates/toy", "limits": {"seed": 9401}, "status": "success",
        "elapsed_seconds": 0.0, "route": "generator.py"})
    adapter = SimpleNamespace(analyze=lambda *_: {**payload(plan), "quality": {"reference_read": False}})
    spec = SimpleNamespace(loader=SimpleNamespace(exec_module=lambda _: None))
    monkeypatch.setattr(module.importlib.util, "spec_from_file_location", lambda *_: spec)
    monkeypatch.setattr(module.importlib.util, "module_from_spec", lambda _: adapter)
    with contextlib.redirect_stdout(io.StringIO()):
        module.main()
    text = (module.ROOT / "EVALUATION.md").read_text()
    assert "total_cholesterol.conditional_rms" in text
    assert "hdl_cholesterol.conditional_rms" in text
