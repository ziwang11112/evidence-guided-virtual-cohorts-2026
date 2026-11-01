"""Conditional source interpretations over invented direct rows only.

These test facts are artificial, and no biomedical generator is executed.
"""
from __future__ import annotations

from copy import deepcopy
from math import sqrt

import pytest

from cohort_harness import conditional_feedback_v1 as conditional
from cohort_harness import semantic_feedback_v1 as sem
from cohort_harness import source_checks, whole_cohort_feedback as legacy
from cohort_harness.lifecycle import freeze_candidate, read_json, sha256, verify_candidate
from test_semantic_feedback_v1 import by_id, source_units
from test_whole_cohort_feedback import _example, execute_direct, frame, write


def prepared(tmp_path, *, edit=None, after_seal=None, constant=False):
    root = _example.prepare(tmp_path / "bundle", n_rows=8)
    candidate = root / "candidates/initial"
    (candidate / "generator.py").unlink()
    rows = frame()
    rows["x"] = [-3, -2, -1, 0, 0, 1, 2, 3]
    rows["y"] = [2] * 8 if constant else [-2, -2, 0, 2, 1, 2, 3, 5]
    rows.to_csv(candidate / "generated.csv", index=False)
    task = read_json(root / "task.json")
    evidence = read_json(candidate / "evidence.json")
    spec = read_json(candidate / "model_spec.json")
    recipe = read_json(candidate / legacy.PLAN)
    source = root / "sources/artificial_aggregate_brief.txt"
    with source.open("a", encoding="utf-8") as stream:
        stream.write("Invented interpretation tests additionally assign Pearson(x,y)=0.25 "
                     "and Spearman(x,y)=-0.125; these are artificial declared inputs, not patient results.\n")
    registry = read_json(root / "registry.json")
    registry["artifacts"][0]["sha256"] = sha256(source)
    write(root / "registry.json", registry)
    evidence["sources"][0]["artifacts"][0]["sha256"] = sha256(source)
    spec["assumptions"].extend([
        {"id": "A_equal_weight", "description": "Invented independently reviewed equal-weight interpretation."},
        {"id": "A_population", "description": "Invented task-population applicability assumption; no source reconstruction."},
    ])
    recipe["assumption_ids"] = ["A_population"]
    recipe["checks"] = []
    semantics = {"schema_version": 1, "evidence_sha256": "", "recipe_sha256": "", "bindings": []}
    interpretations = []
    for name, kind, estimator, value in [
        ("pearson", "correlation", "Pearson", 0.25),
        ("spearman", "spearman_correlation", "Spearman", -0.125),
    ]:
        evidence_id = "E_artificial_" + name
        item = {"id": evidence_id, "source_id": "S_fixture", "locator": "artificial_aggregate_brief.txt line 5",
                "variables": ["x", "y"], "adjustment": [], "kind": kind, "estimate": value, "unit": "1",
                "uncertainty": {"kind": "not_reported"}, "selection": "Entire invented source analysis population",
                "applicability": "Artificial test input with unknown original weighting; not empirical evidence."}
        evidence["items"].append(item)
        operator = {"kind": kind, "unit": "1", "selection": [], "missing_policy": "error", "x": "x", "y": "y"}
        recipe["checks"].append({"id": name, "evidence_id": evidence_id, "status": "approximate",
                                 "operator": deepcopy(operator), "assumption_ids": [],
                                 "reason": "Artificial original weighting is unreported; strict feedback must remain unavailable."})
        semantics["bindings"].append({
            "check_id": name, "evidence_id": evidence_id, "source_locator": item["locator"],
            "definition_status": "specified", "source_operator": deepcopy(operator),
            "weights": "not_reported", "transform": "identity",
            "source_variable_units": source_units(operator, task), "source_n": {"status": "not_reported"},
            "uncertainty_role": "not_reported", "reason": "Invented source explicitly names the estimator; actual weighting unknown.",
        })
        interpretations.append({
            "id": "conditional_" + name, "strict_check_id": name, "evidence_id": evidence_id,
            "source_id": "S_fixture", "source_identifier": evidence["sources"][0]["identifier"],
            "source_locator": item["locator"], "named_estimator": estimator, "operator": deepcopy(operator),
            "equal_weight_assumption_id": "A_equal_weight", "applicability_assumption_ids": ["A_population"],
            "reason": "Invented approved equal-weight interpretation, used only as a task-population proxy.",
        })
    payload = {"schema_version": 1, "scope": "task_population_proxy", "population": task["population"],
               "builder_id": "invented_builder", "task_sha256": "", "evidence_sha256": "", "recipe_sha256": "",
               "semantics_sha256": "", "model_spec_sha256": "", "interpretations": interpretations}
    selected = {row["evidence_id"] for row in interpretations}
    approval = {"schema_version": 1, "decision": "approved", "reviewer_id": "invented_independent_reviewer",
                "builder_id": "invented_builder", "independent_of_builder": True,
                "reviewed_utc": "2026-11-01T00:00:00Z", "rationale": "Independent approval is invented solely for this unit test.",
                "approved_plan": {}, "evidence_dispositions": [
                    {"evidence_id": item["id"], "source_id": item["source_id"],
                     "status": "interpretation_approved" if item["id"] in selected else "not_approved",
                     "reason": "Artificial disposition for interface testing."} for item in evidence["items"]]}
    docs = {"task": task, "evidence": evidence, "spec": spec, "recipe": recipe, "semantics": semantics,
            "payload": payload, "approval": approval}
    if edit:
        edit(docs)
    write(root / "task.json", task)
    write(candidate / "evidence.json", evidence)
    write(candidate / "model_spec.json", spec)
    write(candidate / legacy.PLAN, recipe)
    semantics.update(evidence_sha256=sha256(candidate / "evidence.json"), recipe_sha256=sha256(candidate / legacy.PLAN))
    write(candidate / sem.FILE, semantics)
    payload.update(task_sha256=sha256(root / "task.json"), evidence_sha256=sha256(candidate / "evidence.json"),
                   recipe_sha256=sha256(candidate / legacy.PLAN), semantics_sha256=sha256(candidate / sem.FILE),
                   model_spec_sha256=sha256(candidate / "model_spec.json"))
    approval["approved_plan"] = deepcopy(payload)
    write(candidate / "interpretation_approval.json", approval)
    plan = {**payload, "approval": {"path": "interpretation_approval.json",
                                   "sha256": sha256(candidate / "interpretation_approval.json")}}
    if after_seal:
        after_seal(plan, approval, candidate)
    write(candidate / conditional.FILE, plan)
    freeze_candidate(root, candidate)
    return root, candidate


def strict_feedback(root, candidate):
    execute_direct(root, candidate)
    return sem.collect_feedback(root, candidate, "run01", "strict01")


def collect(root, candidate):
    strict_feedback(root, candidate)
    return conditional.collect_feedback(root, candidate, "run01", "conditional01", strict_feedback_id="strict01")


def forbid_arithmetic(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("All conditional gates must pass before any statistic is evaluated")
    for module in (conditional, sem, legacy, source_checks):
        if hasattr(module, "apply_operator"):
            monkeypatch.setattr(module, "apply_operator", forbidden)


def test_named_estimators_compute_separately_without_changing_strict_rows(tmp_path, monkeypatch):
    root, candidate = prepared(tmp_path)
    before = {path.name: sha256(path) for path in candidate.iterdir()}
    with monkeypatch.context() as patch:
        forbid_arithmetic(patch)
        conditional.preflight(root, candidate)
    strict = strict_feedback(root, candidate)
    strict_path = root / sem.FOLDER / "strict01/feedback.json"
    strict_hash = sha256(strict_path)
    assert strict["n_computable"] == 0
    assert all(row["calculation"] is None and row["difference"] is None for row in strict["checks"])
    calls = []
    original_verify = sem.verify_feedback
    def verified(*args, **kwargs):
        calls.append((args, kwargs))
        return original_verify(*args, **kwargs)
    monkeypatch.setattr(sem, "verify_feedback", verified)
    def forbidden_legacy(*args, **kwargs):
        pytest.fail("Conditional feedback must never fall back to legacy collection")
    monkeypatch.setattr(legacy, "collect_feedback", forbidden_legacy)
    report = conditional.collect_feedback(root, candidate, "run01", "conditional01", strict_feedback_id="strict01")
    assert calls
    assert report["scope"] == "conditional_source_interpretation_target_proxy"
    assert report["source_reproduction"] == "not_established"
    rows = by_id(report["checks"])
    spec = read_json(candidate / "model_spec.json")
    evidence = read_json(candidate / "evidence.json")
    assumptions = by_id(spec["assumptions"])
    sources = by_id(evidence["sources"])
    items = by_id(evidence["items"])
    # Independently hand-derived centered sums for the invented vectors above.
    assert rows["conditional_pearson"]["calculation"]["value"] == pytest.approx(33 / sqrt(28 * 40.875))
    assert rows["conditional_spearman"]["calculation"]["value"] == pytest.approx(40.25 / sqrt(41.5 * 41))
    for name, reported in [("pearson", 0.25), ("spearman", -0.125)]:
        row = rows["conditional_" + name]
        assert row["difference"] == pytest.approx(row["calculation"]["value"] - reported)
        assert row["strict_status"] == "not_computable"
        assert row["original_weight_use"] == "not_reported"
        assert row["assumed_weighting"] == "equal"
        item = items[row["evidence_id"]]
        assert row["context"] == {
            "equal_weight_assumption": assumptions["A_equal_weight"],
            "applicability_assumptions": [assumptions["A_population"]],
            "source": sources[item["source_id"]],
            "evidence_item": item,
        }
    assert sha256(strict_path) == strict_hash
    assert sem.verify_feedback(root, "strict01", candidate=candidate, run_id="run01") == strict
    assert before == {path.name: sha256(path) for path in candidate.iterdir()}
    assert not (root / legacy.FOLDER).exists()
    assert conditional.verify_feedback(root, "conditional01", candidate=candidate, run_id="run01",
                                       strict_feedback_id="strict01") == report
    verify_candidate(root, candidate)


@pytest.mark.parametrize("field,value", [("weights", "weighted"), ("weights", "none"),
                                         ("transform", "not_reported"), ("transform", "nonidentity"),
                                         ("definition_status", "not_reported")])
def test_only_unknown_weighting_can_receive_the_conditional_interpretation(tmp_path, monkeypatch, field, value):
    def edit(docs):
        binding = docs["semantics"]["bindings"][-1]
        binding[field] = value
        if field == "definition_status":
            binding.update(source_operator=None, source_variable_units={})
    root, candidate = prepared(tmp_path, edit=edit)
    forbid_arithmetic(monkeypatch)
    with pytest.raises(ValueError):
        conditional.preflight(root, candidate)


@pytest.mark.parametrize("mistake", ["known_operator_change", "named_estimator_change", "source_identifier",
                                     "source_locator", "evidence_id", "population", "scope", "shared_assumption"])
def test_matching_source_identity_estimator_and_population_are_mandatory(tmp_path, monkeypatch, mistake):
    def edit(docs):
        row = docs["payload"]["interpretations"][-1]
        if mistake == "known_operator_change":
            row["operator"]["selection"] = [{"column": "group", "op": "eq", "value": 1}]
        elif mistake == "named_estimator_change":
            row["named_estimator"] = "Pearson"
        elif mistake in {"source_identifier", "source_locator", "evidence_id"}:
            row[mistake] = "invented_wrong_binding"
        elif mistake == "population":
            docs["payload"]["population"] = "An entirely different invented population"
        elif mistake == "scope":
            docs["payload"]["scope"] = "source_population_replay"
        else:
            row["applicability_assumption_ids"] = [row["equal_weight_assumption_id"]]
    root, candidate = prepared(tmp_path, edit=edit)
    forbid_arithmetic(monkeypatch)
    with pytest.raises(ValueError):
        conditional.preflight(root, candidate)


@pytest.mark.parametrize("mistake", ["quarantined", "not_approved", "builder_is_reviewer", "not_independent",
                                     "denied", "missing_disposition", "extra_approved"])
def test_independent_approval_and_complete_dispositions_are_required(tmp_path, monkeypatch, mistake):
    def edit(docs):
        approval = docs["approval"]
        dispositions = by_id(approval["evidence_dispositions"], "evidence_id")
        if mistake in {"quarantined", "not_approved"}:
            dispositions["E_artificial_spearman"]["status"] = mistake
        elif mistake == "builder_is_reviewer":
            approval["reviewer_id"] = approval["builder_id"]
        elif mistake == "not_independent":
            approval["independent_of_builder"] = False
        elif mistake == "denied":
            approval["decision"] = "rejected"
        elif mistake == "missing_disposition":
            approval["evidence_dispositions"].pop(0)
        else:
            dispositions["E_x_mean"]["status"] = "interpretation_approved"
    root, candidate = prepared(tmp_path, edit=edit)
    forbid_arithmetic(monkeypatch)
    with pytest.raises(ValueError):
        conditional.preflight(root, candidate)


def test_unapproved_plan_change_is_rejected_even_when_frozen(tmp_path, monkeypatch):
    def after_seal(plan, approval, candidate):
        plan["interpretations"][-1]["reason"] = "A changed interpretation the independent reviewer never approved"
    root, candidate = prepared(tmp_path, after_seal=after_seal)
    forbid_arithmetic(monkeypatch)
    with pytest.raises(ValueError):
        conditional.preflight(root, candidate)


def test_approval_cannot_equate_boolean_true_with_integer_one(tmp_path, monkeypatch):
    def after_seal(plan, approval, candidate):
        approval["approved_plan"]["schema_version"] = True
        write(candidate / "interpretation_approval.json", approval)
        plan["approval"]["sha256"] = sha256(candidate / "interpretation_approval.json")
    root, candidate = prepared(tmp_path, after_seal=after_seal)
    forbid_arithmetic(monkeypatch)
    with pytest.raises(ValueError):
        conditional.preflight(root, candidate)


def test_unsupported_operator_cannot_be_introduced_with_matching_declarations(tmp_path, monkeypatch):
    def edit(docs):
        item = by_id(docs["evidence"]["items"])["E_artificial_spearman"]
        item.update(kind="mean", variables=["x"], unit="x_unit")
        operator = {"kind": "mean", "column": "x", "unit": "x_unit", "selection": [], "missing_policy": "error"}
        docs["recipe"]["checks"][-1]["operator"] = deepcopy(operator)
        docs["semantics"]["bindings"][-1].update(source_operator=deepcopy(operator), source_variable_units={"x": "x_unit"})
        docs["payload"]["interpretations"][-1]["operator"] = deepcopy(operator)
    root, candidate = prepared(tmp_path, edit=edit)
    forbid_arithmetic(monkeypatch)
    with pytest.raises(ValueError):
        conditional.preflight(root, candidate)


def test_later_invalid_approval_rejects_collection_before_any_statistic(tmp_path, monkeypatch):
    def edit(docs):
        by_id(docs["approval"]["evidence_dispositions"], "evidence_id")["E_artificial_spearman"]["status"] = "quarantined"
    root, candidate = prepared(tmp_path, edit=edit)
    strict_feedback(root, candidate)
    forbid_arithmetic(monkeypatch)
    with pytest.raises(ValueError):
        conditional.collect_feedback(root, candidate, "run01", "conditional01", strict_feedback_id="strict01")
    assert not (root / conditional.FOLDER / "conditional01").exists()


def test_existing_strict_report_is_required_and_verified(tmp_path):
    root, candidate = prepared(tmp_path)
    execute_direct(root, candidate)
    with pytest.raises((ValueError, OSError)):
        conditional.collect_feedback(root, candidate, "run01", "conditional01", strict_feedback_id="missing")
    strict = sem.collect_feedback(root, candidate, "run01", "strict01")
    strict["checks"][0]["difference"] = 0.0
    write(root / sem.FOLDER / "strict01/feedback.json", strict)
    with pytest.raises(ValueError):
        conditional.collect_feedback(root, candidate, "run01", "conditional01", strict_feedback_id="strict01")


def test_boolean_integer_tampering_of_strict_report_rejects_before_conditional_arithmetic(tmp_path, monkeypatch):
    root, candidate = prepared(tmp_path)
    strict = strict_feedback(root, candidate)
    strict["schema_version"] = True  # Python True == 1 must not preserve a typed commitment.
    write(root / sem.FOLDER / "strict01/feedback.json", strict)
    # The unchanged historical verifier compares Python objects; demonstrate the
    # boundary that the additive conditional wrapper must close independently.
    assert sem.verify_feedback(root, "strict01", candidate=candidate, run_id="run01")["schema_version"] is True
    forbid_arithmetic(monkeypatch)
    with pytest.raises(ValueError):
        conditional.collect_feedback(root, candidate, "run01", "conditional01", strict_feedback_id="strict01")
    assert not (root / conditional.FOLDER / "conditional01").exists()


@pytest.mark.parametrize("artifact", ["plan", "approval"])
def test_frozen_plan_and_approval_tampering_rejects_verification(tmp_path, artifact):
    root, candidate = prepared(tmp_path)
    collect(root, candidate)
    path = candidate / (conditional.FILE if artifact == "plan" else "interpretation_approval.json")
    with path.open("a", encoding="utf-8") as stream:
        stream.write(" \n")
    with pytest.raises(ValueError):
        conditional.verify_feedback(root, "conditional01")


@pytest.mark.parametrize("tamper", ["number", "weight_claim", "count_type"])
def test_conditional_report_tampering_rejects_recomputation(tmp_path, tamper):
    root, candidate = prepared(tmp_path)
    report = collect(root, candidate)
    if tamper == "number":
        report["checks"][0]["calculation"]["value"] = 999
    elif tamper == "weight_claim":
        report["checks"][0]["original_weight_use"] = "none"
    else:
        report["checks"][0]["calculation"]["n_input"] = 8.0
    write(root / conditional.FOLDER / "conditional01/feedback.json", report)
    with pytest.raises(ValueError):
        conditional.verify_feedback(root, "conditional01")


def test_conditional_reports_are_append_only_and_strict_identity_is_bound(tmp_path):
    root, candidate = prepared(tmp_path)
    report = collect(root, candidate)
    assert conditional.FOLDER != sem.FOLDER
    with pytest.raises(ValueError):
        conditional.collect_feedback(root, candidate, "run01", "conditional01", strict_feedback_id="strict01")
    for expected in [{"run_id": "wrong_run"}, {"strict_feedback_id": "wrong_strict"}]:
        with pytest.raises(ValueError):
            conditional.verify_feedback(root, "conditional01", **expected)
    assert conditional.verify_feedback(root, "conditional01") == report


def test_undefined_conditional_correlation_preserves_unavailable_result(tmp_path):
    root, candidate = prepared(tmp_path, constant=True)
    report = collect(root, candidate)
    assert all(row["calculation"] is None and row["difference"] is None for row in report["checks"])
    assert all(row["status"] == "not_computable" for row in report["checks"])
    assert all(row["unavailable_reason"] for row in report["checks"])
