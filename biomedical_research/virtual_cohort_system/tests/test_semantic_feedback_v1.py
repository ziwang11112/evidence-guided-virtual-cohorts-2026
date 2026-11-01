"""Declared semantics over invented direct rows; no biomedical/generator execution."""
from __future__ import annotations

from copy import deepcopy

import pytest

from cohort_harness import semantic_feedback_v1 as sem
from cohort_harness import source_checks, whole_cohort_feedback as legacy
from cohort_harness.lifecycle import freeze_candidate, read_json, sha256, verify_candidate
from test_whole_cohort_feedback import _example, execute_direct, frame, write


def by_id(rows, key="id"):
    return {row[key]: row for row in rows}


def source_units(operator, task):
    """Author units from the original artificial task, before adversarial edits."""
    if operator is None:
        return {}
    names = {p["column"] for p in operator["selection"]}
    names.update(operator[k] for k in ("column", "x", "y", "outcome", "term") if k in operator)
    names.update(operator.get("predictors", []))
    if "event" in operator:
        names.add(operator["event"]["column"])
    columns = by_id(task["columns"], "name")
    return {name: columns[name]["unit"] for name in sorted(names)}


def prepared(tmp_path, *, setup=None, edit=None, task_edit=None):
    """Author reviewed metadata before freezing an explicitly artificial table."""
    root = _example.prepare(tmp_path / "bundle", n_rows=8)
    candidate = root / "candidates/initial"
    (candidate / "generator.py").unlink()
    frame().to_csv(candidate / "generated.csv", index=False)
    evidence = read_json(candidate / "evidence.json")
    plan = read_json(candidate / legacy.PLAN)
    task = read_json(root / "task.json")
    if setup:
        setup(evidence, plan)
    items = by_id(evidence["items"])
    sidecar = {"schema_version": 1, "evidence_sha256": "", "recipe_sha256": "", "bindings": []}
    for check in plan["checks"]:
        item = items[check["evidence_id"]]
        uncertainty = item["uncertainty"]["kind"]
        sidecar["bindings"].append({
            "check_id": check["id"], "evidence_id": item["id"],
            "source_locator": item["locator"], "definition_status": "specified",
            "source_operator": deepcopy(check["operator"]), "weights": "none", "transform": "identity",
            "source_variable_units": source_units(check["operator"], task),
            "source_n": {"status": "not_reported"},
            "uncertainty_role": "individual_dispersion" if uncertainty == "sd" else (
                "estimate" if uncertainty in {"se", "ci"} else "not_reported"),
            "reason": "Invented source semantics reviewed for test.",
        })
    if edit:
        edit(evidence, plan, sidecar)
    if task_edit:
        task_edit(task)
        write(root / "task.json", task)
    write(candidate / "evidence.json", evidence)
    write(candidate / legacy.PLAN, plan)
    sidecar["evidence_sha256"] = sha256(candidate / "evidence.json")
    sidecar["recipe_sha256"] = sha256(candidate / legacy.PLAN)
    write(candidate / sem.FILE, sidecar)
    freeze_candidate(root, candidate)
    return root, candidate


def forbid_arithmetic(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("No statistic may execute before all semantic gates pass or for an unavailable definition")
    for module in (sem, legacy, source_checks):
        if hasattr(module, "apply_operator"):
            monkeypatch.setattr(module, "apply_operator", forbidden)


def collect(root, candidate):
    execute_direct(root, candidate)
    return sem.collect_feedback(root, candidate, "run01", "feedback01")


def test_valid_semantics_preflight_and_separate_feedback_preserve_frozen_bytes(tmp_path, monkeypatch):
    root, candidate = prepared(tmp_path)
    before = {p.name: sha256(p) for p in candidate.iterdir()}
    with monkeypatch.context() as patch:
        forbid_arithmetic(patch)
        gates = sem.preflight(root, candidate)
    assert gates["scope"] == "declared_source_semantics_only"
    assert len(gates["checks"]) == 5
    assert all(c["semantic_status"] == "matched_declared" for c in gates["checks"])
    report = collect(root, candidate)
    checks = by_id(report["checks"])
    assert checks["adjusted_slope"]["calculation"]["value"] == pytest.approx(0.75)
    assert checks["adjusted_slope"]["semantics"]["source_variable_units"] == {
        "x": "x_unit", "y": "y_unit", "group": "1",
    }
    assert checks["adjusted_slope"]["semantics"]["source_operator"]["unit"] == "y_unit/x_unit"
    assert checks["group_proportion"]["calculation"]["value"] == pytest.approx(0.5)
    assert report["n_computable"] == 5 and report["n_not_computable"] == 0
    assert all(c["semantics"]["source_n"] == {"status": "not_reported"} for c in report["checks"])
    assert all(c["monte_carlo_uncertainty"] == {"status": "not_estimated"} for c in report["checks"])
    assert not (root / legacy.FOLDER).exists()
    assert (root / sem.FOLDER / "feedback01/feedback.json").is_file()
    assert before == {p.name: sha256(p) for p in candidate.iterdir()}
    assert sem.verify_feedback(root, "feedback01", candidate=candidate, run_id="run01") == report
    verify_candidate(root, candidate)


@pytest.mark.parametrize("mistake", ["wrong_term", "reversed_roles", "omitted_filter", "extra_adjustment"])
def test_known_mismatches_reject_even_approximate_before_any_arithmetic(tmp_path, monkeypatch, mistake):
    def setup(evidence, plan):
        if mistake == "omitted_filter":
            by_id(evidence["items"])["E_slope"]["selection"] = "Invented x > -3 source subset"
            plan["checks"][-1]["operator"]["selection"] = [{"column": "x", "op": "gt", "value": -3}]
    def edit(evidence, plan, sidecar):
        operator = plan["checks"][-1]["operator"]
        if mistake == "wrong_term":
            operator["term"] = "group"
        elif mistake == "reversed_roles":
            operator.update(outcome="x", predictors=["y", "group"], term="y")
        elif mistake == "omitted_filter":
            operator["selection"] = []
        else:
            # Both recipes agree, but the original evidence does not report this adjustment.
            by_id(evidence["items"])["E_slope"]["adjustment"] = []
    root, candidate = prepared(tmp_path, setup=setup, edit=edit)
    execute_direct(root, candidate)
    forbid_arithmetic(monkeypatch)
    with pytest.raises(ValueError):
        sem.preflight(root, candidate)
    with pytest.raises(ValueError):
        sem.collect_feedback(root, candidate, "run01", "rejected")
    assert not (root / sem.FOLDER / "rejected").exists()


@pytest.mark.parametrize("field,value", [("kind", "sd"), ("unit", "other_invented_unit"), ("variables", ["y"])])
def test_source_operator_must_bind_evidence_not_just_match_recipe(tmp_path, field, value):
    def edit(evidence, plan, sidecar):
        by_id(evidence["items"])["E_x_mean"][field] = value
    root, candidate = prepared(tmp_path, edit=edit)
    with pytest.raises(ValueError):
        sem.preflight(root, candidate)


@pytest.mark.parametrize("mistake", ["agreed_cm", "per_ten_coefficient", "changed_task_context", "absent_later_filter"])
def test_matching_declarations_must_match_task_measurements_before_arithmetic(tmp_path, monkeypatch, mistake):
    def edit(evidence, plan, sidecar):
        if mistake == "agreed_cm":
            by_id(evidence["items"])["E_x_mean"]["unit"] = "cm"
            plan["checks"][0]["operator"]["unit"] = "cm"
            sidecar["bindings"][0]["source_operator"]["unit"] = "cm"
            sidecar["bindings"][0]["source_variable_units"]["x"] = "cm"
        elif mistake == "per_ten_coefficient":
            unit = "y_unit/(10*x_unit)"
            by_id(evidence["items"])["E_slope"]["unit"] = unit
            plan["checks"][-1]["operator"]["unit"] = unit
            sidecar["bindings"][-1]["source_operator"]["unit"] = unit
        elif mistake == "absent_later_filter":
            # The preceding four checks are valid; a later invalid column must
            # prevent arithmetic on all checks, not merely fail when reached.
            predicate = {"column": "absent_artificial_filter", "op": "gt", "value": 0}
            plan["checks"][-1]["operator"]["selection"] = [predicate]
            sidecar["bindings"][-1]["source_operator"]["selection"] = [deepcopy(predicate)]
            sidecar["bindings"][-1]["source_variable_units"][predicate["column"]] = "x_unit"
    def task_edit(task):
        if mistake == "changed_task_context":
            # Freeze a changed task while preserving the prior source units.
            by_id(task["columns"], "name")["x"]["unit"] = "cm"
    root, candidate = prepared(tmp_path, edit=edit, task_edit=task_edit)
    execute_direct(root, candidate)
    forbid_arithmetic(monkeypatch)
    expected = {
        "agreed_cm": "Source/task variable unit mismatch",
        "per_ten_coefficient": "per-unit unstandardized OLS",
        "changed_task_context": "Source/task variable unit mismatch",
        "absent_later_filter": "unknown task columns",
    }[mistake]
    with pytest.raises(ValueError, match=expected):
        sem.preflight(root, candidate)
    with pytest.raises(ValueError, match=expected):
        sem.collect_feedback(root, candidate, "run01", "rejected")
    assert not (root / sem.FOLDER / "rejected").exists()


def test_source_units_cover_filter_only_variables(tmp_path):
    def setup(evidence, plan):
        plan["checks"][0]["operator"]["selection"] = [{"column": "group", "op": "eq", "value": 1}]
    root, candidate = prepared(tmp_path, setup=setup)
    gate = sem.preflight(root, candidate)["checks"][0]
    assert gate["semantics"]["source_variable_units"] == {"x": "x_unit", "group": "1"}
    row = by_id(collect(root, candidate)["checks"])["x_mean"]
    assert row["calculation"]["value"] == pytest.approx(0.5)


def test_predictor_and_conjunction_reordering_is_semantically_equal(tmp_path):
    def setup(evidence, plan):
        plan["checks"][-1]["operator"]["selection"] = [
            {"column": "x", "op": "gt", "value": -4},
            {"column": "group", "op": "in", "value": [0, 1]},
        ]
        by_id(evidence["items"])["E_slope"]["selection"] = "Invented x > -4 and group in {0,1}"
    def edit(evidence, plan, sidecar):
        operator = plan["checks"][-1]["operator"]
        operator["predictors"].reverse()
        operator["selection"].reverse()
    root, candidate = prepared(tmp_path, setup=setup, edit=edit)
    sem.preflight(root, candidate)
    assert by_id(collect(root, candidate)["checks"])["adjusted_slope"]["calculation"]["value"] == pytest.approx(0.75)


def quantile_setup(evidence, plan):
    item = by_id(evidence["items"])["E_x_mean"]
    item.update(kind="quantile", q=0.25, method="linear", estimate=-1.75)
    plan["checks"] = [plan["checks"][0]]
    plan["checks"][0]["operator"].update(kind="quantile", q=0.25, method="linear")


@pytest.mark.parametrize("field,value", [("q", 0.75), ("method", "nearest")])
def test_quantile_probability_and_method_cannot_change_under_approximation(tmp_path, field, value):
    def edit(evidence, plan, sidecar):
        plan["checks"][0]["operator"][field] = value
    root, candidate = prepared(tmp_path, setup=quantile_setup, edit=edit)
    with pytest.raises(ValueError):
        sem.preflight(root, candidate)


@pytest.mark.parametrize("mutation", ["different_event", "denominator_conditioned_on_event", "bool_as_integer"])
def test_event_and_denominator_are_bound_with_typed_predicates(tmp_path, mutation):
    def edit(evidence, plan, sidecar):
        operator = by_id(plan["checks"])["group_proportion"]["operator"]
        if mutation == "different_event":
            operator["event"]["value"] = 0
        elif mutation == "denominator_conditioned_on_event":
            operator["selection"] = [deepcopy(operator["event"])]
        else:
            operator["event"]["value"] = True  # Python True == 1 must not mean equivalent evidence.
    root, candidate = prepared(tmp_path, edit=edit)
    with pytest.raises(ValueError):
        sem.preflight(root, candidate)


def test_boolean_filter_cannot_match_integer_filter(tmp_path):
    def setup(evidence, plan):
        plan["checks"][3]["operator"]["selection"] = [{"column": "group", "op": "eq", "value": 1}]
    def edit(evidence, plan, sidecar):
        plan["checks"][3]["operator"]["selection"][0]["value"] = True
    root, candidate = prepared(tmp_path, setup=setup, edit=edit)
    with pytest.raises(ValueError):
        sem.preflight(root, candidate)


@pytest.mark.parametrize("predicate_op,value", [
    ("eq", True), ("in", [True]),
    ("eq", "1"), ("ne", "1"), ("in", ["1"]),
])
def test_matching_predicates_cannot_coerce_numeric_category_types(tmp_path, monkeypatch, predicate_op, value):
    def edit(evidence, plan, sidecar):
        predicate = {"column": "group", "op": predicate_op, "value": value}
        by_id(plan["checks"])["group_proportion"]["operator"]["event"] = predicate
        by_id(sidecar["bindings"], "check_id")["group_proportion"]["source_operator"]["event"] = deepcopy(predicate)
    root, candidate = prepared(tmp_path, edit=edit)
    execute_direct(root, candidate)
    forbid_arithmetic(monkeypatch)
    expected = "Predicate values must be finite typed scalars" if type(value) is bool or value == [True] else "Predicate/task column type mismatch"
    with pytest.raises(ValueError, match=expected):
        sem.preflight(root, candidate)
    with pytest.raises(ValueError, match=expected):
        sem.collect_feedback(root, candidate, "run01", "rejected")
    assert not (root / sem.FOLDER / "rejected").exists()


@pytest.mark.parametrize("field,value", [
    ("definition_status", "not_reported"), ("definition_status", "unsupported"),
    ("weights", "weighted"), ("weights", "not_reported"),
    ("transform", "nonidentity"), ("transform", "not_reported"),
])
def test_unknown_or_unsupported_semantics_are_unavailable_without_fallback(tmp_path, monkeypatch, field, value):
    def setup(evidence, plan):
        plan["checks"] = [plan["checks"][0]]
    def edit(evidence, plan, sidecar):
        binding = sidecar["bindings"][0]
        binding[field] = value
        if field == "definition_status":
            binding["source_operator"] = None
            binding["source_variable_units"] = {}
    root, candidate = prepared(tmp_path, setup=setup, edit=edit)
    execute_direct(root, candidate)
    forbid_arithmetic(monkeypatch)
    gate = sem.preflight(root, candidate)["checks"][0]
    assert gate["semantic_status"] == "unavailable"
    row = sem.collect_feedback(root, candidate, "run01", "feedback01")["checks"][0]
    assert row["status"] == "not_computable"
    assert row["calculation"] is None and row["difference"] is None
    assert row["unavailable_reason"]
    assert row["estimator_uncertainty"] == {"kind": "not_reported"}
    assert row["semantics"]["source_n"] == {"status": "not_reported"}


def test_unreported_quantile_definition_does_not_invent_interpolation(tmp_path, monkeypatch):
    def setup(evidence, plan):
        quantile_setup(evidence, plan)
        by_id(evidence["items"])["E_x_mean"]["method"] = "not_reported"
    def edit(evidence, plan, sidecar):
        sidecar["bindings"][0].update(definition_status="not_reported", source_operator=None, source_variable_units={})
    root, candidate = prepared(tmp_path, setup=setup, edit=edit)
    execute_direct(root, candidate)
    forbid_arithmetic(monkeypatch)
    row = sem.collect_feedback(root, candidate, "run01", "feedback01")["checks"][0]
    assert row["status"] == "not_computable" and row["calculation"] is None


@pytest.mark.parametrize("broken", ["missing", "duplicate", "wrong_evidence", "wrong_locator"])
def test_bindings_are_one_to_one_and_include_declared_unavailable_checks(tmp_path, broken):
    def edit(evidence, plan, sidecar):
        plan["checks"][0].update(status="not_computable", operator=None, reason="Artificial deferred operator")
        if broken == "missing":
            sidecar["bindings"].pop(0)
        elif broken == "duplicate":
            sidecar["bindings"].append(deepcopy(sidecar["bindings"][0]))
        elif broken == "wrong_evidence":
            sidecar["bindings"][0]["evidence_id"] = "E_y_mean"
        else:
            sidecar["bindings"][0]["source_locator"] = "A different invented source location"
    root, candidate = prepared(tmp_path, edit=edit)
    with pytest.raises(ValueError):
        sem.preflight(root, candidate)


@pytest.mark.parametrize("uncertainty,role", [
    ({"kind": "sd", "value": 2.0}, "individual_dispersion"),
    ({"kind": "sd", "value": 2.0}, "unresolved"),
    ({"kind": "se", "value": 0.125}, "estimate"),
    ({"kind": "ci", "low": -0.25, "high": 0.25, "level": 0.95}, "estimate"),
    ({"kind": "not_reported"}, "not_reported"),
])
def test_source_uncertainty_roles_survive_without_converting_sd_to_se(tmp_path, uncertainty, role):
    def setup(evidence, plan):
        plan["checks"] = [plan["checks"][0]]
        by_id(evidence["items"])["E_x_mean"]["uncertainty"] = deepcopy(uncertainty)
    def edit(evidence, plan, sidecar):
        sidecar["bindings"][0]["uncertainty_role"] = role
    root, candidate = prepared(tmp_path, setup=setup, edit=edit)
    row = collect(root, candidate)["checks"][0]
    assert row["reported_uncertainty"] == uncertainty
    assert row["semantics"]["source_n"] == {"status": "not_reported"}
    assert row["calculation"]["n_used"] == 8  # Generated count must not become source n.
    assert row["estimator_uncertainty"] == (uncertainty if role == "estimate" else {"kind": "not_reported"})
    assert row["individual_dispersion"] == (uncertainty if role == "individual_dispersion" else {"kind": "not_reported"})
    if role == "unresolved":
        assert row["unresolved_source_uncertainty"] == uncertainty


def test_source_sd_cannot_be_relabelled_estimator_precision(tmp_path):
    def setup(evidence, plan):
        by_id(evidence["items"])["E_x_mean"]["uncertainty"] = {"kind": "sd", "value": 2.0}
    def edit(evidence, plan, sidecar):
        sidecar["bindings"][0]["uncertainty_role"] = "estimate"
    root, candidate = prepared(tmp_path, setup=setup, edit=edit)
    with pytest.raises(ValueError):
        sem.preflight(root, candidate)


def test_frozen_sidecar_tampering_is_rejected(tmp_path):
    root, candidate = prepared(tmp_path)
    collect(root, candidate)
    with (candidate / sem.FILE).open("a", encoding="utf-8") as stream:
        stream.write(" \n")
    with pytest.raises(ValueError):
        sem.verify_feedback(root, "feedback01")


@pytest.mark.parametrize("tamper", ["number", "source_semantics"])
def test_feedback_recomputation_detects_numeric_and_semantic_tampering(tmp_path, tamper):
    root, candidate = prepared(tmp_path)
    report = collect(root, candidate)
    if tamper == "number":
        report["checks"][0]["calculation"]["value"] = 999
    else:
        report["checks"][0]["semantics"]["source_n"] = {"status": "not_reported", "value": 8}
    write(root / sem.FOLDER / "feedback01/feedback.json", report)
    with pytest.raises(ValueError):
        sem.verify_feedback(root, "feedback01")


def test_new_folder_cannot_overwrite_legacy_or_its_own_feedback(tmp_path):
    root, candidate = prepared(tmp_path)
    execute_direct(root, candidate)
    old = legacy.collect_feedback(root, candidate, "run01", "feedback01")
    old_path = root / legacy.FOLDER / "feedback01/feedback.json"
    digest = sha256(old_path)
    new = sem.collect_feedback(root, candidate, "run01", "feedback01")
    assert sem.FOLDER != legacy.FOLDER
    assert sha256(old_path) == digest and legacy.verify_feedback(root, "feedback01") == old
    with pytest.raises(ValueError):
        sem.collect_feedback(root, candidate, "run01", "feedback01")
    assert sem.verify_feedback(root, "feedback01") == new
