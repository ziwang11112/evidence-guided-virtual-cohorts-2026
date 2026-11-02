"""Invented metadata/rows; real lifecycle/bridge verification, no process launch."""
import copy
import json
from pathlib import Path
import shutil
import socket
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import k01_sources as k


def review(value):
    return {"decision": "approved", "independent": True, "reviewer_id": "invented-independent-reviewer",
            "producer_id": "invented-producer", "reviewed_utc": "2026-11-02T00:00:00Z",
            "reason": "Invented test fixture only; not clinical admission", "approved_sha256": value}


def write(path, value):
    path.write_bytes(k.encoded(value))


def invented_state():
    state = k._committed()
    packet = json.loads(state["packet_bytes"])
    for source in packet["source_objects"]:
        source.update(title="Invented test source", doi="invented:" + source["source_id"],
                      population={"fixture": "invented population"}, measurement={"fixture": "invented measurement"})
    for record in packet["records"]:
        old = record["original_selected_record"]
        stat, variable = old["statistic"], old["variable"]
        value = (65.0 if variable == "age" else 10.0 if variable == "bmi" else 2.0) if stat == "arithmetic_mean" else 1.0
        original = {"id": record["id"], "source_id": record["source_id"], "statistic": stat, "variable": variable,
                    "value": value, "unit": old["unit"], "locator": "invented aggregate table", "uncertainty": None}
        if stat == "printed_percentage":
            original.update(value=50.0, source_count=5, source_denominator=10, group="invented category")
        if stat == "sample_proportion":
            original.update(value=0.5, derivation={"exact_numerator": 5, "exact_denominator": 10}, group="invented female")
        if stat == "adjusted_odds_ratio":
            original.update(value=1.2, uncertainty={"kind": "confidence_interval", "level": 0.95, "lower": 0.8, "upper": 1.4})
        record["original_selected_record"] = original
        record["provenance"]["original_record_canonical_sha256"] = k.digest(original)
    by_id = {r["id"]: r for r in packet["records"]}
    for plan in state["plan"]["items"]:
        record = by_id[plan["evidence_id"]]
        original = record["original_selected_record"]
        plan["original_record_canonical_sha256"] = k.digest(original)
        plan["comparison_value"] = 0.5 if plan["operator"]["kind"] == "proportion" else original["value"]
        if plan["operator"]["kind"] == "proportion":
            plan["comparison_derivation"] = {"operation": "invented count division", "numerator": 5, "denominator": 10, "expression": "5/10"}
            plan["original_printed_percentage"] = 50.0 if original["unit"] == "%" else None
    state["packet_bytes"] = k.encoded(packet)
    state["design_sha256"] = k.digest({"invented": "not a real admission"})
    return state


def parent(root, state, *, approval=True):
    compiled = k._compile(state)
    root.mkdir()
    candidate = root / "candidates/invented"
    candidate.mkdir(parents=True)
    (root / k.ARTIFACT).parent.mkdir()
    (root / k.ARTIFACT).write_bytes(state["packet_bytes"])
    write(root / "registry.json", {"artifacts": [{**r, "origin": "fixture", "screening": "approved"} for r in compiled["registration_requirements"]]})
    write(root / "task.json", state["task"])
    assumptions = {c: ["invented_" + str(i)] for i, c in enumerate(k.SOURCE_CONTEXTS)}
    templates = k.bind_context_assumptions(compiled, assumptions)
    target = {"id": k.TARGET, "role": "target", "source_ids": [], "assumption_ids": ["invented_target"], "feedback_policy": "none", "recipe": None, "semantics": None, "supplement": None}
    contexts = {}
    for context in [*templates, target]:
        contexts[context["id"]] = {"population": state["eligibility"]["contexts"][context["id"]]["population"], "n_rows": 5000,
            "measurement": context["recipe"]["measurement"]["description"] if context["recipe"] else "invented target measurement", "inputs": {}}
    spec = {"parameters": {"active_context": k.TARGET, "contexts": contexts},
            "assumptions": [{"id": x, "description": "Invented no-clinical model assumption"} for x in ["invented_0", "invented_1", "invented_target"]],
            "parameter_provenance": {key: {"evidence_ids": [], "assumption_ids": ["invented_target"], "derivation": "Invented fixture"} for key in ("active_context", "contexts")}}
    trials = [{"id": "source-" + str(i), "context_id": c, "seed": seed, "n_rows": 5000} for i, (c, seed) in enumerate(zip(k.SOURCE_CONTEXTS, (3101, 3102)))]
    trials += [{"id": "target-" + str(seed), "context_id": k.TARGET, "seed": seed, "n_rows": 5000} for seed in (2101, 2102, 2103)]
    plan = {"schema_version": 1, "shared_parameters": [], "context_varying_parameters": [], "contexts": [*templates, target], "trials": trials,
            "execution_limits": {"timeout_seconds": 30, "memory_mb": 1024, "output_bytes": 2000000, "log_bytes": 10000},
            "budget": {"source_attempts": 2, "source_rows": 10000, "target_attempts": 3, "target_rows": 15000}}
    declaration = k.build_declaration(compiled, assumptions, model_spec=spec)
    if approval:
        declaration["review"] = review(k.declaration_digest(declaration))
    for name, value in {"evidence.json": compiled["evidence"], "model_spec.json": spec, k.bridge.PLAN: plan, k.DECLARATION: declaration,
                        "checks.json": {"scope": "fixture_only", "records": [{"name": "invented", "status": "not_computable", "detail": "No real generated table"}], "artifacts": []}}.items():
        write(candidate / name, value)
    (candidate / "generator.py").write_text('def generate(observed, specification, seed):\n    raise RuntimeError("Invented source code never executed")\n', encoding="utf-8")
    (candidate / "decision.md").write_text("Invented test fixture only", encoding="utf-8")
    k.lifecycle.freeze_candidate(root, candidate)
    k.bridge.prepare(root, "invented")
    requests = k.bridge.binding_requests(root, "invented")
    k.bridge.seal(root, "invented", {c: {"binding_review": review(r["binding_sha256"]), "supplement_review": None, "proxy_reviews": {}} for c, r in requests.items()})
    return root


@pytest.fixture(scope="module")
def completed(tmp_path_factory):
    state = invented_state()
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(k, "_committed", lambda: state)
        for owner, name in [(subprocess, "run"), (subprocess, "Popen"), (socket, "create_connection")]:
            monkeypatch.setattr(owner, name, lambda *a, **kw: pytest.fail("No process/network authorized"))
        monkeypatch.setattr(k.execution, "_runtime_manifest", lambda runtime: {"fixture": "invented mocked process"})
        monkeypatch.setattr(k.execution, "_command", lambda *a, **kw: ["invented-no-process-command"])
        monkeypatch.setattr(k.semantic.legacy, "collect_feedback", lambda *a, **kw: pytest.fail("No legacy fallback"))
        def capture(command, cwd, timeout, limit, stdout_path, stderr_path):
            context = k.lifecycle.read_json(cwd / "input/model_spec.json")["parameters"]["active_context"]
            base_age = 62 if "mind" in context else 26 if "ayele" in context else 42
            output = "id,age,sex,bmi,glucose\n" + "".join(f"invented-{i},{base_age+i%3},{'F' if i%2 else 'M'},{10+i%4},{1+i%3}\n" for i in range(5000))
            (cwd / "output/generated.csv").write_text(output, encoding="utf-8")
            write(cwd / "output/worker_report.json", {"status": "completed", "generator_started": True})
            stdout_path.write_text("Invented process boundary", encoding="utf-8")
            stderr_path.write_text("", encoding="utf-8")
            return {"returncode": 0, "host_timeout": False, "logs": {}}
        monkeypatch.setattr(k.execution, "_capture", capture)
        root = parent(tmp_path_factory.mktemp("metadata") / "invented", state)
        k.bridge.execute(root, "invented")
        yield root, state


@pytest.fixture
def copied(completed, tmp_path):
    base, state = completed
    return Path(shutil.copytree(base, tmp_path / "copy")), state


def test_compiler_preserves_original_uncertainty_units_and_all_dispositions():
    state = invented_state()
    compiled = k._compile(state)
    assert compiled["counts"] == {"evidence_records": 34, "descriptive_candidates": 18, "context_only": 16}
    items = {i["id"]: i for i in compiled["evidence"]["items"]}
    assert items["ayele_sex_female"]["unit"] == "%" and items["ayele_sex_female"]["estimate"] == 50
    assert items["ayele_aor_male"]["uncertainty"] == {"kind": "ci", "low": 0.8, "high": 1.4, "level": 0.95}
    assert items["MIND_K01_age_sd"]["kind"] == "sd" and items["MIND_K01_age_sd"]["uncertainty"] == {"kind": "not_reported"}
    assert all(c["operator"] is None for t in compiled["source_context_templates"] for c in t["recipe"]["checks"])
    assert all(b["weights"] == "not_reported" for t in compiled["source_context_templates"] for b in t["semantics"]["bindings"])


def test_successful_bound_both_source_reports_and_exclusive_output(copied):
    root, _ = copied
    reports = [k.collect_descriptives(root, "invented", "source-" + str(i)) for i in (0, 1)]
    assert [len(r["checks"]) for r in reports] == [7, 11]
    assert all(c["computed"]["diagnostic"]["n_used"] == 5000 and c["strict_source_difference"] is None and c["normalized_score"] is None for r in reports for c in r["checks"])
    female = next(c for c in reports[0]["checks"] if c["evidence_id"] == "MIND_K01_female_proportion")
    assert female["descriptive_raw_difference"] == 0
    assert reports[0]["semantic_feedback_v1_verified_first"] is True
    assert k.bridge.verify(root, "invented")["completion_committed"] is True
    with pytest.raises(ValueError, match="already exists"):
        k.collect_descriptives(root, "invented", "source-0")


@pytest.mark.parametrize("trial", ["target-2101", "not-scheduled", "../source-0"])
def test_target_unknown_and_path_trials_rejected(completed, trial):
    with pytest.raises(ValueError):
        k.collect_descriptives(completed[0], "invented", trial)


@pytest.mark.parametrize("artifact", ["output/generated.csv", "execution.json"])
def test_changed_execution_artifact_rejected_before_report(copied, artifact):
    root, _ = copied
    path = root / k.bridge.FOLDER / "invented/contexts/source_mind_china_2019/bundle/executions/source-0" / artifact
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(ValueError):
        k.collect_descriptives(root, "invented", "source-0")
    assert not (root / k.FOLDER).exists()


def test_missing_completion_rejected(copied):
    root, _ = copied
    (root / k.bridge.FOLDER / "invented/completion.json").unlink()
    with pytest.raises(ValueError, match="Completed bridge"):
        k.collect_descriptives(root, "invented", "source-0")


def test_report_typed_boolean_tamper_rejected(copied):
    root, _ = copied
    k.collect_descriptives(root, "invented", "source-0")
    path = root / k.FOLDER / "invented/source-0/feedback.json"
    value = k.lifecycle.read_json(path)
    value["execution_link_verified"] = 1
    write(path, value)
    with pytest.raises(ValueError, match="report changed"):
        k.verify_descriptives(root, "invented", "source-0")


def test_wrong_context_output_fails_whole_frame_before_descriptive(completed, monkeypatch):
    root, state = completed
    prepared = k._prepare(root, "invented", "source-0")
    real_read = k.lifecycle.read_table
    def wrong_context(path, task, **kwargs):
        frame = real_read(path, task, **kwargs)
        frame.loc[0, "age"] = 40
        return frame
    monkeypatch.setattr(k.lifecycle, "read_table", wrong_context)
    monkeypatch.setattr(state["descriptive"], "compute_source_descriptives", lambda *a, **kw: pytest.fail("Invalid frame reached arithmetic"))
    with pytest.raises(ValueError, match="age minimum"):
        k._compute(prepared, "source-0")


def test_stage_sources_requires_explicit_registry_screening(tmp_path, completed):
    result = k.stage_sources(tmp_path / "stage")
    requirements = k.lifecycle.read_json(tmp_path / "stage/registration_requirements.json")
    assert result["registration_approved"] is False
    assert all(set(r) == {"source_id", "path", "sha256"} for r in requirements)
    with pytest.raises(ValueError, match="exists"):
        k.stage_sources(tmp_path / "stage")
