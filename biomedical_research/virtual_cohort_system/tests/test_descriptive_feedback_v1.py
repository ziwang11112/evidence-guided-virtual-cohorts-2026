"""Invented aggregate definitions and direct rows; no clinical/target data."""
from __future__ import annotations

from copy import deepcopy
import math

import pandas as pd
import pytest

from cohort_harness import descriptive_feedback_v1 as descriptive
from cohort_harness import semantic_feedback_v1 as strict
from cohort_harness import source_checks
from cohort_harness.lifecycle import freeze_candidate, read_json, sha256
from test_whole_cohort_feedback import _example, execute_direct, frame, write


def operator(kind="mean", **fields):
    result = {"kind": kind, "unit": "x_unit", "selection": [], "missing_policy": "error"}
    if kind in {"correlation", "spearman_correlation"}:
        result.update(x="x", y="y", unit="1")
    else:
        result["column"] = "x"
    if kind in {"median", "quantile"}:
        result["method"] = "linear"
    if kind == "quantile":
        result["q"] = 0.25
    result.update(fields)
    return result


def prepared(tmp_path, *, kind="mean", edit=None, values=None, freeze=True):
    root = _example.prepare(tmp_path / "bundle", n_rows=8)
    candidate = root / "candidates/initial"
    (candidate / "generator.py").unlink()
    data = frame()
    data["x"] = [1., 2., 4., 8., 16., 32., 64., 128.] if values is None else values
    data.to_csv(candidate / "generated.csv", index=False)
    evidence = read_json(candidate / "evidence.json")
    item = evidence["items"][0]
    item["kind"] = "reported_other" if kind == "geometric_mean" else kind
    if kind == "geometric_mean":
        item["statistic_name"] = "geometric_mean"
    if kind in {"median", "quantile"}:
        item["method"] = "linear"
    if kind == "quantile":
        item["q"] = 0.25
    if kind in {"correlation", "spearman_correlation"}:
        item.update(variables=["x", "y"], unit="1")
    op = operator(kind)
    units = {"x": "x_unit", "y": "y_unit"} if kind in {"correlation", "spearman_correlation"} else {"x": "x_unit"}
    plan = {"schema_version": 1, "evidence_sha256": "", "checks": [{
        "id": "descriptive_x", "evidence_id": item["id"], "source_locator": item["locator"],
        "operator": op, "conventions": descriptive._conventions(op),
        "source_definition": {"definition_status": "specified", "source_operator": deepcopy(op),
                              "weights": "none", "transform": "identity", "source_variable_units": units,
                              "conventions": descriptive._conventions(op),
                              "reason": "Explicitly invented source definition, not a publication."},
        "assumption_ids": ["A_fixture"],
        "applicability": {"status": "explicit_transfer_assumption", "reason": "Invented task rows are a descriptive analogue only."},
        "reason": "Calculate a named descriptive statistic under explicit conventions."}]}
    if edit:
        edit(evidence, plan)
    write(candidate / "evidence.json", evidence)
    plan["evidence_sha256"] = sha256(candidate / "evidence.json")
    write(candidate / descriptive.FILE, plan)
    if freeze:
        freeze_candidate(root, candidate)
    return root, candidate


def collect(root, candidate):
    execute_direct(root, candidate)
    return descriptive.collect(root, candidate, "run01", "feedback01")


@pytest.mark.parametrize("kind,expected", [
    ("mean", 2.25), ("sd", math.sqrt(10.75 / 3)), ("geometric_mean", 10 ** 0.25),
    ("median", 1.5), ("quantile", 1.),
    ("spearman_correlation", -5 / 6), ("correlation", -5.25 / math.sqrt(10.75 * 4.75)),
])
def test_named_math_and_average_ties(kind, expected):
    data = pd.DataFrame({"x": [1., 1., 2., 5.], "y": [4., 2., 2., 1.]})
    result = descriptive.apply_operator(data, operator(kind))
    assert result["value"] == pytest.approx(expected)
    assert result["n_input"] == result["n_selected"] == result["n_used"] == 4
    assert result["unit"] == ("1" if "correlation" in kind else "x_unit")


@pytest.mark.parametrize("values", [[0., 2.], [-1., 2.], [float("inf"), 2.]])
def test_geometric_mean_never_drops_shifts_or_logs_nonpositive_values(values):
    with pytest.raises(source_checks.NotComputable, match="strictly positive"):
        descriptive.apply_operator(pd.DataFrame({"x": values}), operator("geometric_mean"))


def test_geometric_mean_selection_and_declared_missingness_accounting():
    data = pd.DataFrame({"x": [2., None, 8., -10.], "group": [1, 1, 1, 0]})
    op = operator("geometric_mean", missing_policy="complete_cases", selection=[{"column": "group", "op": "eq", "value": 1}])
    result = descriptive.apply_operator(data, op)
    assert result == {"value": pytest.approx(4.), "n_input": 4, "n_selected": 3, "n_used": 2,
                      "n_missing_dropped": 1, "unit": "x_unit"}
    op["missing_policy"] = "error"
    with pytest.raises(source_checks.NotComputable, match="Missing"):
        descriptive.apply_operator(data, op)


def test_preflight_never_reads_rows_or_calls_arithmetic(tmp_path, monkeypatch):
    root, candidate = prepared(tmp_path, freeze=False)
    (candidate / "generated.csv").unlink()
    def forbidden(*args, **kwargs):
        pytest.fail("Preflight cannot read individual rows or calculate")
    monkeypatch.setattr(descriptive, "apply_operator", forbidden)
    monkeypatch.setattr(descriptive, "read_table", forbidden)
    result = descriptive.preflight(root, candidate)
    assert result["checks"][0]["calculation_status"] == "ready"


def test_verified_output_hashes_and_separate_judgments(tmp_path):
    root, candidate = prepared(tmp_path, kind="geometric_mean")
    before = {path.name: sha256(path) for path in candidate.iterdir()}
    report = collect(root, candidate)
    row = report["checks"][0]
    assert row["calculation"]["value"] == pytest.approx(2 ** 3.5)
    assert row["source_definition_match"]["status"] == "matched_declared"
    assert row["applicability"]["status"] == "explicit_transfer_assumption"
    assert row["strict_feedback_promoted"] is False
    assert report["source_population_replayed"] is False
    assert report["generator_execution_recorded"] is False
    assert report["output_link_verified"] is True
    assert report["bindings"]["generated_table_sha256"] == sha256(root / "executions/run01/output/generated.csv")
    assert before == {path.name: sha256(path) for path in candidate.iterdir()}
    assert descriptive.verify(root, "feedback01", candidate=candidate, run_id="run01") == report
    with pytest.raises(ValueError, match="already exists"):
        descriptive.collect(root, candidate, "run01", "feedback01")


def test_unknown_weighting_and_quantile_method_compute_as_assumed(tmp_path):
    def edit(evidence, plan):
        evidence["items"][0]["method"] = "not_reported"
        source = plan["checks"][0]["source_definition"]
        source.update(definition_status="not_reported", source_operator=None, source_variable_units={}, weights="not_reported")
        source.pop("conventions")
    root, candidate = prepared(tmp_path, kind="quantile", edit=edit)
    row = collect(root, candidate)["checks"][0]
    assert row["calculation_status"] == "computed"
    assert row["calculation"]["value"] == pytest.approx(3.5)
    assert row["source_definition_match"]["status"] == "assumed_convention"
    assert row["source_definition_match"]["assumptions"]
    assert row["difference"] == pytest.approx(3.5)
    assert row["difference_interpretation"] == "descriptive_raw_difference_only_no_fit_or_validity_claim"


@pytest.mark.parametrize("kind", ["sd", "spearman_correlation"])
def test_unbound_source_ddof_or_ties_cannot_be_matched_declared(tmp_path, kind):
    def edit(evidence, plan):
        plan["checks"][0]["source_definition"].pop("conventions")
    root, candidate = prepared(tmp_path, kind=kind, edit=edit)
    row = collect(root, candidate)["checks"][0]
    assert row["calculation_status"] == "computed"
    assert row["source_definition_match"]["status"] == "assumed_convention"


@pytest.mark.parametrize("mistake", ["arithmetic_geometric", "pearson_spearman", "quantile_probability", "source_units", "selection", "weighting", "transform", "contrast"])
def test_known_semantic_mismatches_remain_visible_without_comparable_difference(tmp_path, mistake):
    kind = "correlation" if mistake == "pearson_spearman" else "quantile" if mistake == "quantile_probability" else "mean"
    def edit(evidence, plan):
        item, check = evidence["items"][0], plan["checks"][0]
        source = check["source_definition"]
        if mistake == "arithmetic_geometric":
            item.update(kind="reported_other", statistic_name="geometric_mean")
        elif mistake == "pearson_spearman":
            item["kind"] = "spearman_correlation"
        elif mistake == "quantile_probability":
            item["q"] = 0.75
        elif mistake == "source_units":
            source["source_variable_units"]["x"] = "different_unit"
        elif mistake == "selection":
            source["source_operator"]["selection"] = [{"column": "group", "op": "eq", "value": 1}]
            source["source_variable_units"]["group"] = "1"
        elif mistake == "weighting":
            source["weights"] = "weighted"
        elif mistake == "transform":
            source["transform"] = "nonidentity"
        else:
            item.update(kind="reported_other", statistic_name="categorical_contrast")
    root, candidate = prepared(tmp_path, kind=kind, edit=edit)
    row = collect(root, candidate)["checks"][0]
    assert row["calculation_status"] == "computed"
    assert row["source_definition_match"]["status"] == "known_mismatch"
    assert row["source_definition_match"]["mismatches"]
    assert row["difference"] is None
    assert row["strict_feedback_promoted"] is False


@pytest.mark.parametrize("mistake", ["unit", "assumption", "locator", "bool_filter", "absent_filter", "false_ddof", "applicability"])
def test_invalid_declarations_fail_before_arithmetic(tmp_path, monkeypatch, mistake):
    def edit(evidence, plan):
        check = plan["checks"][0]
        if mistake == "unit":
            check["operator"]["unit"] = "wrong_unit"
        elif mistake == "assumption":
            check["assumption_ids"] = ["unbound"]
        elif mistake == "locator":
            check["source_locator"] = "another source"
        elif mistake == "bool_filter":
            check["operator"]["selection"] = [{"column": "group", "op": "eq", "value": True}]
        elif mistake == "absent_filter":
            check["operator"]["selection"] = [{"column": "unavailable", "op": "eq", "value": 1}]
        elif mistake == "false_ddof":
            check["conventions"]["sd_ddof"] = True
        else:
            check["applicability"]["status"] = "matched_source_context"
    root, candidate = prepared(tmp_path, edit=edit)
    execute_direct(root, candidate)
    def forbidden(*args, **kwargs):
        pytest.fail("Invalid plan reached arithmetic")
    monkeypatch.setattr(descriptive, "apply_operator", forbidden)
    with pytest.raises(ValueError):
        descriptive.preflight(root, candidate)
    with pytest.raises(ValueError):
        descriptive.collect(root, candidate, "run01", "rejected")
    assert not (root / descriptive.FOLDER / "rejected").exists()


@pytest.mark.parametrize("case", ["empty_selection", "nonpositive_geometric", "constant_spearman", "one_row_sd", "no_operator"])
def test_data_unavailability_does_not_erase_semantic_judgment(tmp_path, case):
    kind = "geometric_mean" if case == "nonpositive_geometric" else "spearman_correlation" if case == "constant_spearman" else "sd" if case == "one_row_sd" else "mean"
    def edit(evidence, plan):
        check = plan["checks"][0]
        if case in {"empty_selection", "one_row_sd"}:
            predicate = {"column": "x", "op": "lt", "value": 0 if case == "empty_selection" else 2}
            check["operator"]["selection"] = [predicate]
            check["source_definition"]["source_operator"]["selection"] = [deepcopy(predicate)]
        if case == "no_operator":
            check["operator"] = None
            check["conventions"] = descriptive._conventions(None)
    values = [0., 1., 2., 3., 4., 5., 6., 7.] if case == "nonpositive_geometric" else [1.] * 8 if case == "constant_spearman" else None
    root, candidate = prepared(tmp_path, kind=kind, edit=edit, values=values)
    row = collect(root, candidate)["checks"][0]
    assert row["calculation_status"] == "cannot_compute"
    assert row["calculation"] is None and row["difference"] is None
    assert row["unavailable_reason"]
    assert row["source_definition_match"]["status"] in {"matched_declared", "unsupported"}


@pytest.mark.parametrize("tamper", ["output", "plan", "evidence", "number", "promote_match", "extra_artifact"])
def test_provenance_and_recomputation_reject_tampering(tmp_path, tamper):
    root, candidate = prepared(tmp_path)
    report = collect(root, candidate)
    if tamper == "output":
        path = root / "executions/run01/output/generated.csv"
        path.write_text(path.read_text(encoding="utf-8").replace("128.0", "129.0"), encoding="utf-8")
    elif tamper in {"plan", "evidence"}:
        path = candidate / (descriptive.FILE if tamper == "plan" else "evidence.json")
        with path.open("a", encoding="utf-8") as stream:
            stream.write(" \n")
    elif tamper == "extra_artifact":
        (root / descriptive.FOLDER / "feedback01/extra.txt").write_text("unexpected", encoding="utf-8")
    else:
        if tamper == "number":
            report["checks"][0]["calculation"]["value"] += 1
        else:
            report["checks"][0]["source_definition_match"]["status"] = "verified_from_source"
        write(root / descriptive.FOLDER / "feedback01/feedback.json", report)
    with pytest.raises(ValueError):
        descriptive.verify(root, "feedback01")


def test_strict_unavailable_result_remains_separately_retained(tmp_path):
    root, candidate = prepared(tmp_path, freeze=False)
    legacy_plan = read_json(candidate / "whole_cohort_feedback.json")
    legacy_plan["checks"] = [legacy_plan["checks"][0]]
    legacy_plan["checks"][0].update(status="not_computable", operator=None)
    write(candidate / "whole_cohort_feedback.json", legacy_plan)
    item = read_json(candidate / "evidence.json")["items"][0]
    sidecar = {"schema_version": 1, "evidence_sha256": sha256(candidate / "evidence.json"),
               "recipe_sha256": sha256(candidate / "whole_cohort_feedback.json"), "bindings": [{
                   "check_id": "x_mean", "evidence_id": item["id"], "source_locator": item["locator"],
                   "definition_status": "not_reported", "source_operator": None, "weights": "not_reported",
                   "transform": "identity", "source_variable_units": {}, "source_n": {"status": "not_reported"},
                   "uncertainty_role": "not_reported", "reason": "Source weighting unavailable in invented record."}]}
    write(candidate / strict.FILE, sidecar)
    freeze_candidate(root, candidate)
    execute_direct(root, candidate)
    old = strict.collect_feedback(root, candidate, "run01", "feedback01")
    old_path = root / strict.FOLDER / "feedback01/feedback.json"
    old_hash = sha256(old_path)
    result = descriptive.collect(root, candidate, "run01", "feedback01")
    assert old["checks"][0]["calculation"] is None
    assert result["checks"][0]["calculation_status"] == "computed"
    assert sha256(old_path) == old_hash
    assert strict.verify_feedback(root, "feedback01") == old


def test_source_uncertainty_never_turns_sd_into_estimator_precision(tmp_path):
    def edit(evidence, plan):
        evidence["items"][0]["uncertainty"] = {"kind": "sd", "value": 3.}
    root, candidate = prepared(tmp_path, edit=edit)
    row = collect(root, candidate)["checks"][0]
    assert row["estimator_uncertainty"] == {"kind": "not_reported"}
    assert row["unresolved_source_dispersion"] == {"kind": "sd", "value": 3.}
    assert row["monte_carlo_uncertainty"] == {"status": "not_estimated"}
