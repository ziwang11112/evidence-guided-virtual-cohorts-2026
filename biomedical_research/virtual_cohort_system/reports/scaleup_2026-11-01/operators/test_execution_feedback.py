"""Invented tiny bundles; candidate/execution verification is explicitly mocked.

Real semantic-v1 preflight/collection/verification and supplemental arithmetic
run, but no generator, WSL runtime, participant data or clinical case is used.
"""
import copy
import json
from pathlib import Path
import socket
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import execution_feedback as adapter


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def review(digest):
    return {"decision": "approved", "independent": True, "reviewer_id": "invented-reviewer",
            "producer_id": "invented-producer", "reviewed_utc": "2026-11-02T00:00:00Z",
            "reason": "Invented test declaration only; no scientific approval", "approved_sha256": digest}


@pytest.fixture
def fixture(tmp_path, monkeypatch):
    root = tmp_path / "invented_bundle"
    directory = root / "candidates" / "invented"
    directory.mkdir(parents=True)
    task = {"schema_version": 1, "task_id": "invented", "mode": "whole_cohort", "population": "Invented source adults",
            "row_id": "id", "n_rows": 3,
            "columns": [{"name": "id", "kind": "string", "unit": "1", "role": "identifier", "nullable": False},
                        {"name": "x", "kind": "number", "unit": "example_unit", "role": "generated", "nullable": False},
                        {"name": "sex", "kind": "category", "categories": ["F", "M"], "unit": "1", "role": "generated", "nullable": False},
                        {"name": "site", "kind": "category", "categories": ["A", "B"], "unit": "1", "role": "generated", "nullable": False}],
            "information_policy": {"mode": "published_evidence", "excluded_cohorts": ["forbidden-target"], "allowed_tools": []},
            "budget": {"source_queries": 0, "source_downloads": 0, "revisions": 0}}
    source = {"id": "invented-source", "identifier": "invented:source", "population": task["population"],
              "measurement": "Invented assay", "cohort_ids": ["invented-source"],
              "artifacts": [{"path": "sources/invented.txt", "sha256": "1" * 64}]}
    item = {"id": "geo", "source_id": source["id"], "locator": "Invented Table 1, F at A",
            "variables": ["x"], "kind": "reported_other", "statistic_name": "geometric_mean", "estimate": 3.0,
            "unit": "example_unit", "uncertainty": {"kind": "ci", "low": 2.0, "high": 4.0, "level": 0.95},
            "adjustment": [], "selection": "Invented female site A complete values", "applicability": "Invented context only"}
    evidence = {"schema_version": 1, "sources": [source], "items": [item]}
    spec = {"parameters": {}, "assumptions": [{"id": "context", "description": "Invented source-context construction"},
                                             {"id": "proxy", "description": "Explicit unweighted proxy with unknown source weights"}],
            "parameter_provenance": {}}
    operator = {"kind": "geometric_mean", "column": "x", "unit": "example_unit", "selection": [
        {"column": "sex", "op": "eq", "value": "F"}, {"column": "site", "op": "eq", "value": "A"}],
        "selection_missing_policy": "error", "missing_policy": "error"}
    context = {"kind": "source_context_simulation", "context_id": "invented-source-context", "population": task["population"],
               "measurement": source["measurement"], "variable_units": {"x": "example_unit", "sex": "1", "site": "1"},
               "variable_scales": {"x": "original", "sex": "categorical", "site": "categorical"}}
    descriptor = {**{key: copy.deepcopy(value) for key, value in context.items() if key != "kind"},
                  "source_id": source["id"], "locator": item["locator"], "operator": copy.deepcopy(operator),
                  "weights": "not_reported", "definition_status": "specified", "uncertainty_role": "estimator_confidence_interval"}
    recipe = {"schema_version": 1, "population": task["population"],
              "measurement": {"mode": "identity", "description": source["measurement"]}, "assumption_ids": ["context"],
              "checks": [{"id": "native-geo", "evidence_id": "geo", "status": "not_computable", "operator": None,
                          "assumption_ids": [], "reason": "Geometric mean unsupported by frozen v1"}]}
    binding = {"check_id": "native-geo", "evidence_id": "geo", "source_locator": item["locator"],
               "definition_status": "unsupported", "source_operator": None, "weights": "not_reported", "transform": "identity",
               "source_variable_units": {}, "source_n": {"status": "not_reported"}, "uncertainty_role": "estimate",
               "reason": "Original statistic retained; no geometric-mean v1 arithmetic"}
    semantics = {"schema_version": 1, "evidence_sha256": "", "recipe_sha256": "", "bindings": [binding]}
    declaration = {"schema_version": 1, "task_sha256": "", "evidence_sha256": "", "model_spec_sha256": "", "semantics_sha256": "",
                   "table_context": context, "assumption_ids": ["context"], "context_review": None,
                   "checks": [{"id": "supp-geo", "evidence_id": "geo", "semantic_check_id": "native-geo",
                               "operator": operator, "source": descriptor,
                               "proxy": {"assumption_ids": ["proxy"], "reason": "Explicit unweighted invented scenario", "review": None}}]}
    run = root / "executions" / "run1"
    (run / "output").mkdir(parents=True)
    (run / "output/generated.csv").write_text("id,x,sex,site\na,1,F,A\nb,4,F,A\nc,16,M,A\n", encoding="utf-8")
    (directory / "generator.py").write_text("# Inert fixture; never imported or executed.\n", encoding="utf-8")
    events = []
    state = {"root": root, "directory": directory, "task": task, "evidence": evidence, "spec": spec,
             "recipe": recipe, "semantics": semantics, "declaration": declaration, "events": events}

    def refresh(*, approve=True):
        for path, value in [(root / "task.json", task), (directory / "evidence.json", evidence),
                            (directory / "model_spec.json", spec), (directory / "whole_cohort_feedback.json", recipe)]:
            write(path, value)
        semantics["evidence_sha256"] = adapter.sha256(directory / "evidence.json")
        semantics["recipe_sha256"] = adapter.sha256(directory / "whole_cohort_feedback.json")
        write(directory / adapter.semantic.FILE, semantics)
        for key, path in {"task_sha256": root / "task.json", "evidence_sha256": directory / "evidence.json",
                          "model_spec_sha256": directory / "model_spec.json", "semantics_sha256": directory / adapter.semantic.FILE}.items():
            declaration[key] = adapter.sha256(path)
        if approve:
            declaration["context_review"] = review(adapter.declaration_digest(declaration))
            for check in declaration["checks"]:
                if check["proxy"] is not None:
                    check["proxy"]["review"] = review(adapter.proxy_digest(declaration, check["id"]))
        write(directory / adapter.FILE, declaration)
        names = sorted(path.name for path in directory.iterdir() if path.name != "freeze.json")
        frozen = {"route": "generator.py", "candidate_files": ["candidates/invented/" + name for name in names],
                  "commitments": {name: adapter.sha256(directory / name) for name in names},
                  "task_sha256": adapter.sha256(root / "task.json")}
        write(directory / "freeze.json", frozen)
        receipt = {"status": "success", "generator_executed": True, "route": "generator.py", "candidate": "candidates/invented",
                   "candidate_freeze_sha256": adapter.sha256(directory / "freeze.json"),
                   "generated_table_sha256": adapter.sha256(run / "output/generated.csv")}
        write(run / "execution.json", receipt)

    def verify_candidate(bundle, candidate):
        events.append("verify_candidate_mock")
        frozen = adapter.read_json(directory / "freeze.json")
        assert adapter.sha256(root / "task.json") == frozen["task_sha256"], "Task tampered"
        for name, expected in frozen["commitments"].items():
            assert adapter.sha256(directory / name) == expected, "Candidate tampered"
        return frozen

    def verify_execution(bundle, run_id):
        events.append("verify_execution_mock")
        assert run_id == "run1", "Wrong run"
        receipt = adapter.read_json(run / "execution.json")
        assert receipt["generated_table_sha256"] == adapter.sha256(run / "output/generated.csv"), "Execution output tampered"
        return receipt

    monkeypatch.setattr(adapter, "verify_candidate", verify_candidate)
    monkeypatch.setattr(adapter.semantic, "verify_candidate", verify_candidate)
    monkeypatch.setattr(adapter.execution, "verify_execution", verify_execution)
    for owner, name in [(adapter.execution, "run_candidate"), (subprocess, "run"), (subprocess, "Popen"), (socket, "create_connection")]:
        monkeypatch.setattr(owner, name, lambda *a, **k: pytest.fail("No process/network/generator call is authorized"))
    collect = adapter.semantic.collect_feedback
    verify = adapter.semantic.verify_feedback

    def collect_v1(*args, **kwargs):
        events.append("collect_semantic_v1")
        return collect(*args, **kwargs)

    def verify_v1(*args, **kwargs):
        events.append("verify_semantic_v1")
        return verify(*args, **kwargs)

    monkeypatch.setattr(adapter.semantic, "collect_feedback", collect_v1)
    monkeypatch.setattr(adapter.semantic, "verify_feedback", verify_v1)
    # Any attempted legacy collector (not its structural helpers) is an error.
    monkeypatch.setattr(adapter.semantic.legacy, "collect_feedback", lambda *a, **k: pytest.fail("Legacy fallback"))
    state["refresh"] = refresh
    refresh()
    return state


def collect(fixture, **kwargs):
    return adapter.collect_feedback(fixture["root"], "invented", "run1", "supp1", semantic_feedback_id="native1",
                                    collect_semantic=True, **kwargs)


def no_feedback(fixture):
    assert not (fixture["root"] / adapter.FOLDER).exists()
    assert not (fixture["root"] / adapter.semantic.FOLDER).exists()
    assert "collect_semantic_v1" not in fixture["events"]


def test_verified_v1_then_supplement_preserves_original_evidence_and_unknown_weights(fixture, monkeypatch):
    diagnostic = adapter.statistics.diagnostic
    approvals = []

    def inspect(*args, **kwargs):
        approvals.append(kwargs["approval"])
        return diagnostic(*args, **kwargs)

    monkeypatch.setattr(adapter.statistics, "diagnostic", inspect)
    report = collect(fixture)
    check = report["checks"][0]
    assert check["diagnostic"]["diagnostic"]["value"] == pytest.approx(2)
    assert check["proxy"]["difference"] == pytest.approx(-1)
    assert check["proxy"]["interpretation"].startswith("assumption_defined_")
    assert check["source"]["weights"] == "not_reported"
    assert check["reported_evidence"] == fixture["evidence"]["items"][0]
    assert check["reported_evidence"]["kind"] == "reported_other"
    assert check["reported_evidence"]["uncertainty"] == {"kind": "ci", "low": 2.0, "high": 4.0, "level": 0.95}
    assert check["strict_source_difference"] is None and not check["exact_source_check_allowed"]
    assert approvals and all(approval is None for approval in approvals)
    assert report["uncertainty_conversion"] == "none"
    assert report["cross_context_generator_linkage"] == "not_supplied_or_verified"
    assert "collect_semantic_v1" in fixture["events"] and "verify_semantic_v1" in fixture["events"]
    native = adapter.read_json(fixture["root"] / adapter.semantic.FOLDER / "native1/feedback.json")
    assert native["checks"][0]["status"] == "not_computable" and native["checks"][0]["difference"] is None


def test_explicit_existing_v1_receipt_route(fixture):
    adapter.semantic.collect_feedback(fixture["root"], "invented", "run1", "native1")
    fixture["events"].clear()
    report = adapter.collect_feedback(fixture["root"], "invented", "run1", "supp1", semantic_feedback_id="native1")
    assert report["status"] == "complete"
    assert "collect_semantic_v1" not in fixture["events"] and "verify_semantic_v1" in fixture["events"]


def test_no_proxy_has_descriptive_value_but_no_difference_even_known_weights(fixture):
    fixture["declaration"]["checks"][0]["proxy"] = None
    fixture["declaration"]["checks"][0]["source"]["weights"] = "none"
    fixture["semantics"]["bindings"][0]["weights"] = "none"
    fixture["refresh"]()
    check = collect(fixture)["checks"][0]
    assert check["diagnostic"]["diagnostic_available"] and check["proxy"] is None
    assert not check["exact_source_check_allowed"] and check["strict_source_difference"] is None


@pytest.mark.parametrize("field,value", [("population", "Relabelled target"), ("measurement", "Different assay"),
                                         ("locator", "Wrong table"), ("source_id", "wrong"), ("weights", "none"),
                                         ("uncertainty_role", "between_person_dispersion")])
def test_evidence_semantics_mismatch_fails_before_writes(fixture, field, value):
    fixture["declaration"]["checks"][0]["source"][field] = value
    fixture["refresh"]()
    with pytest.raises(ValueError):
        collect(fixture)
    no_feedback(fixture)


@pytest.mark.parametrize("mutation", ["task_population", "task_units", "kind_mean", "variable_roles", "context_assumption",
                                      "proxy_assumption", "proxy_review", "context_review", "operator_type", "v1_link", "source_units"])
def test_linkage_type_and_review_rejections_do_not_write(fixture, mutation):
    declaration = fixture["declaration"]
    check = declaration["checks"][0]
    if mutation == "task_population": declaration["table_context"]["population"] = "Another population"
    elif mutation == "task_units": declaration["table_context"]["variable_units"]["x"] = "mg/dL"
    elif mutation == "kind_mean":
        fixture["evidence"]["items"][0]["kind"] = "mean"
        fixture["evidence"]["items"][0].pop("statistic_name")
    elif mutation == "variable_roles": fixture["evidence"]["items"][0]["variables"] = ["sex"]
    elif mutation == "context_assumption": declaration["assumption_ids"] = ["invented-unknown"]
    elif mutation == "proxy_assumption": check["proxy"]["assumption_ids"] = []
    elif mutation == "proxy_review": check["proxy"]["review"]["approved_sha256"] = "0" * 64
    elif mutation == "context_review": declaration["context_review"]["reviewer_id"] = "invented-producer"
    elif mutation == "operator_type":
        check["operator"]["selection"][0]["value"] = 1
        check["source"]["operator"] = copy.deepcopy(check["operator"])
    elif mutation == "v1_link": check["semantic_check_id"] = "absent"
    elif mutation == "source_units": check["source"]["variable_units"]["x"] = "mg/dL"
    fixture["refresh"](approve=mutation not in {"proxy_review", "context_review"})
    with pytest.raises(ValueError): collect(fixture)
    no_feedback(fixture)


@pytest.mark.parametrize("field,value", [("candidate", "candidates/wrong"), ("status", "failed"),
                                         ("route", "generated.csv"), ("generator_executed", False),
                                         ("candidate_freeze_sha256", "0" * 64)])
def test_verified_execution_identity_and_status_must_match(fixture, field, value):
    path = fixture["root"] / "executions/run1/execution.json"
    receipt = adapter.read_json(path)
    receipt[field] = value
    write(path, receipt)
    with pytest.raises(ValueError): collect(fixture)
    no_feedback(fixture)


def test_frozen_direct_rows_and_unfrozen_declaration_rejected(fixture):
    path = fixture["directory"] / "freeze.json"
    frozen = adapter.read_json(path)
    frozen["route"] = "generated.csv"
    write(path, frozen)
    with pytest.raises(ValueError, match="direct rows"): collect(fixture)
    no_feedback(fixture)
    frozen["route"] = "generator.py"
    frozen["candidate_files"].remove("candidates/invented/" + adapter.FILE)
    write(path, frozen)
    with pytest.raises(ValueError, match="must be frozen"): collect(fixture)
    no_feedback(fixture)


@pytest.mark.parametrize("artifact", ["declaration", "output", "v1_receipt", "supplement"])
def test_tamper_detected_at_appropriate_boundary(fixture, artifact):
    if artifact == "declaration":
        path = fixture["directory"] / adapter.FILE
        value = adapter.read_json(path)
        value["table_context"]["kind"] = "target_context_generated"
        write(path, value)
        with pytest.raises(AssertionError, match="tampered"): collect(fixture)
        no_feedback(fixture)
        return
    if artifact == "output":
        (fixture["root"] / "executions/run1/output/generated.csv").write_text("id,x,sex,site\na,9,F,A\nb,4,F,A\nc,16,M,A\n")
        with pytest.raises(AssertionError, match="tampered"): collect(fixture)
        no_feedback(fixture)
        return
    collect(fixture)
    folder = adapter.semantic.FOLDER if artifact == "v1_receipt" else adapter.FOLDER
    identifier = "native1" if artifact == "v1_receipt" else "supp1"
    path = fixture["root"] / folder / identifier / "feedback.json"
    value = adapter.read_json(path)
    value["status"] = "changed"
    write(path, value)
    with pytest.raises(ValueError):
        adapter.verify_feedback(fixture["root"], "supp1", candidate="invented", run_id="run1")


def test_v1_failure_is_visible_without_fallback_or_supplement(fixture, monkeypatch):
    def reject(*args, **kwargs):
        raise ValueError("Strict v1 failure")
    monkeypatch.setattr(adapter.semantic, "collect_feedback", reject)
    with pytest.raises(ValueError, match="Strict v1 failure"): collect(fixture)
    assert not (fixture["root"] / adapter.FOLDER).exists()


def test_malformed_v1_semantics_and_unsupported_kind_fail_before_writes(fixture):
    fixture["semantics"]["bindings"][0]["source_locator"] = "Wrong location"
    fixture["refresh"]()
    with pytest.raises(ValueError): collect(fixture)
    no_feedback(fixture)


def test_target_context_remains_target_and_fixture_cannot_compare(fixture):
    declaration = fixture["declaration"]
    declaration["table_context"]["kind"] = "target_context_generated"
    fixture["refresh"]()
    check = collect(fixture)["checks"][0]
    assert check["diagnostic"]["diagnostic_scope"] == "target_context_generated"
    assert not check["exact_source_check_allowed"] and check["proxy"]["difference"] == pytest.approx(-1)


def test_analytic_fixture_proxy_rejected(fixture):
    fixture["declaration"]["table_context"]["kind"] = "analytic_fixture"
    fixture["refresh"]()
    with pytest.raises(ValueError, match="fixtures"): collect(fixture)
    no_feedback(fixture)


def test_no_comparison_data_path_parameter_or_generator_invocation(fixture):
    with pytest.raises(TypeError): collect(fixture, comparison_csv="patient.csv")
    no_feedback(fixture)


@pytest.mark.parametrize("column,scale", [("x", "natural_log"), ("x", "not_reported"),
                                         ("sex", "not_reported"), ("sex", "log10")])
def test_source_scale_must_be_declared_original_or_categorical(fixture, column, scale):
    fixture["declaration"]["checks"][0]["source"]["variable_scales"][column] = scale
    fixture["refresh"]()
    with pytest.raises(ValueError, match="scale"): collect(fixture)
    no_feedback(fixture)


def test_wrong_run_and_task_derived_variable_are_rejected(fixture):
    with pytest.raises(AssertionError, match="Wrong run"):
        adapter.collect_feedback(fixture["root"], "invented", "wrong", "supp1", semantic_feedback_id="native1", collect_semantic=True)
    no_feedback(fixture)
    check = fixture["declaration"]["checks"][0]
    check["operator"]["column"] = "undeclared_derived_non_hdl"
    check["source"]["operator"] = copy.deepcopy(check["operator"])
    fixture["refresh"]()
    with pytest.raises(ValueError, match="Unknown task variable"): collect(fixture)
    no_feedback(fixture)


def test_typed_v1_report_rejects_true_substituted_for_one(fixture):
    fixture["evidence"]["items"][0]["estimate"] = 1.0
    fixture["refresh"]()
    adapter.semantic.collect_feedback(fixture["root"], "invented", "run1", "native1")
    path = fixture["root"] / adapter.semantic.FOLDER / "native1/feedback.json"
    report = adapter.read_json(path)
    report["checks"][0]["reported_value"] = True
    write(path, report)
    with pytest.raises(ValueError, match="Typed v1"):
        adapter.collect_feedback(fixture["root"], "invented", "run1", "supp1", semantic_feedback_id="native1")
    assert not (fixture["root"] / adapter.FOLDER).exists()


def test_undefined_geometric_mean_has_no_proxy_number(fixture):
    (fixture["root"] / "executions/run1/output/generated.csv").write_text("id,x,sex,site\na,0,F,A\nb,4,F,A\nc,16,M,A\n")
    fixture["refresh"]()
    check = collect(fixture)["checks"][0]
    assert not check["diagnostic"]["diagnostic_available"]
    assert check["proxy"]["status"] == "unavailable" and check["proxy"]["difference"] is None


def test_prevalence_uses_same_execution_and_native_v1_definition(fixture):
    check = fixture["declaration"]["checks"][0]
    operator = check["operator"]
    operator["kind"] = "proportion"
    operator.pop("column")
    operator.update(unit="%", event={"column": "x", "op": "lt", "value": 4})
    check["source"]["operator"] = copy.deepcopy(operator)
    item = fixture["evidence"]["items"][0]
    item.update(kind="proportion", unit="%", estimate=60.0, uncertainty={"kind": "ci", "low": 40., "high": 80., "level": 0.95})
    item.pop("statistic_name")
    native = {key: value for key, value in operator.items() if key != "selection_missing_policy"}
    binding = fixture["semantics"]["bindings"][0]
    binding.update(definition_status="specified", source_operator=native,
                   source_variable_units=copy.deepcopy(check["source"]["variable_units"]))
    fixture["refresh"]()
    record = collect(fixture)["checks"][0]
    assert record["diagnostic"]["diagnostic"]["value"] == pytest.approx(50)
    assert record["proxy"]["difference"] == pytest.approx(-10)
    assert record["diagnostic"]["diagnostic"]["n_used"] == 2
    assert not record["exact_source_check_allowed"]
