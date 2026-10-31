"""Invented arithmetic fixtures only; no biomedical data or coefficients."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import pytest

from cohort_harness.contracts import ContractError
from cohort_harness.self_consistency import main, run_self_consistency, validate_self_consistency_spec


def fixture_task() -> dict:
    def column(name, kind, role, **extra):
        return {"name": name, "kind": kind, "unit": "invented", "role": role, "nullable": False, **extra}
    return {
        "schema_version": 1, "task_id": "invented-self-check", "mode": "enrichment",
        "population": "Invented software test rows", "row_id": "key", "n_rows": 4,
        "columns": [column("key", "string", "identifier"), column("x", "number", "observed"),
                    column("w", "number", "observed"),
                    column("group", "category", "observed", categories=["a", "b", "c"]),
                    column("y", "number", "generated")],
        "information_policy": {"mode": "prior_only", "excluded_cohorts": [], "allowed_tools": []},
        "budget": {"source_queries": 0, "source_downloads": 0, "revisions": 0},
    }


def fixture_spec() -> dict:
    return {
        "schema_version": 1, "interpretation": "conditional_moments", "outcome": "y",
        "numeric_predictors": ["x", "w"], "group_by": ["group"],
        "conditional_mean": {"op": "add", "args": [
            {"op": "add", "args": [{"const": 10}, {"op": "mul", "args": [{"const": 2}, {"column": "x"}]}]},
            {"lookup": {"column": "group", "values": [
                {"key": "a", "value": 0}, {"key": "b", "value": 3}, {"key": "c", "value": -3}]}}]},
        "conditional_sd": {"const": 2},
    }


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, allow_nan=False), encoding="utf-8")


def write_csv(path: Path, header: list, rows: list) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerows(rows)


@pytest.fixture
def inputs(tmp_path):
    task, spec = fixture_task(), fixture_spec()
    rows = [["private-row-one", "0", "0", "a"], ["private-row-two", "1", "2", "a"],
            ["private-row-three", "2", "4", "b"], ["private-row-four", "3", "6", "b"]]
    paths = {key: tmp_path / (key + (".csv" if key in ("observed", "generated") else ".json"))
             for key in ("task", "observed", "generated", "spec", "output")}
    write_json(paths["task"], task)
    write_json(paths["spec"], spec)
    write_csv(paths["observed"], ["key", "x", "w", "group"], rows)
    write_csv(paths["generated"], ["key", "x", "w", "group", "y"],
              [row + [y] for row, y in zip(rows, [11, 10, 20, 19])])
    return paths, task, spec, rows


def run(paths):
    return run_self_consistency(*(paths[name] for name in ("task", "observed", "generated", "spec", "output")))


def test_known_arithmetic_groups_associations_and_rank(inputs):
    paths, _, _, _ = inputs
    result = run(paths)
    diagnostics = result["diagnostics"]
    residual = diagnostics["overall"]["residual"]
    assert residual["mean"] == pytest.approx(0.5)
    assert residual["sample_sd"] == pytest.approx(math.sqrt(13 / 3))
    assert residual["rmse_from_zero"] == pytest.approx(math.sqrt(3.5))
    assert residual["quantiles"]["0.5"] == pytest.approx(0.5)
    assert diagnostics["overall"]["standardized_residual"]["mean"] == pytest.approx(0.25)
    assert diagnostics["absolute_standardized_tail_counts"] == {"1": 1, "2": 0, "3": 0}
    groups = diagnostics["groups"]["group"]
    assert groups[0]["summaries"]["residual"]["mean"] == pytest.approx(-0.5)
    assert groups[1]["summaries"]["residual"]["mean"] == pytest.approx(1.5)
    assert groups[2]["n"] == 0
    assert groups[2]["summaries"]["residual"]["status"] == "empty_group"
    association = diagnostics["residual_predictor_associations"]["x"]
    assert association["pearson"]["value"] == pytest.approx(1 / math.sqrt(65))
    assert association["spearman_average_ranks"]["value"] == pytest.approx(0)
    assert diagnostics["predictor_design"]["status"] == "rank_deficient"
    assert diagnostics["predictor_design"]["rank"] == 2
    assert result["status"] == "computed"  # Nonzero residual mean is not a failure.
    assert result["scientific_validity"] == "not_assessed"


def test_hash_bindings_no_rows_input_immutability_and_exclusive_creation(inputs):
    paths, _, _, _ = inputs
    before = {name: path.read_bytes() for name, path in paths.items() if name != "output"}
    result = run(paths)
    for name, raw in before.items():
        assert result["bindings"][name]["sha256"] == hashlib.sha256(raw).hexdigest()
        assert paths[name].read_bytes() == raw
    text = paths["output"].read_text(encoding="utf-8")
    assert "private-row" not in text
    assert len(result["implementation"]["self_consistency_sha256"]) == 64
    assert len(result["implementation"]["contracts_sha256"]) == 64
    with pytest.raises(ContractError, match="Output already exists"):
        run(paths)
    assert paths["output"].read_text(encoding="utf-8") == text


def test_same_bytes_produce_same_report(inputs):
    paths, _, _, _ = inputs
    first = run(paths)
    original = paths["output"].read_bytes()
    paths["output"] = paths["output"].with_name("second.json")
    assert run(paths) == first
    assert paths["output"].read_bytes() == original


def test_working_guides_without_sd_are_explicit(inputs):
    paths, _, spec, _ = inputs
    spec["interpretation"] = "working_guides"
    del spec["conditional_sd"]
    write_json(paths["spec"], spec)
    report = run(paths)
    assert report["interpretation"] == "working_guides"
    assert "standardized_residual" not in report["diagnostics"]["overall"]
    assert "absolute_standardized_tail_counts" not in report["diagnostics"]


@pytest.mark.parametrize("expr,expected", [
    ({"op": "sub", "args": [{"const": 7}, {"const": 2}]}, 5),
    ({"op": "div", "args": [{"const": 9}, {"const": 2}]}, 4.5),
    ({"op": "min", "args": [{"const": 7}, {"const": 2}]}, 2),
    ({"op": "max", "args": [{"const": 7}, {"const": 2}]}, 7),
    ({"op": "pow", "base": {"const": 2}, "exponent": -2}, 0.25),
])
def test_other_expression_operations(inputs, expr, expected):
    paths, _, spec, _ = inputs
    spec["conditional_mean"] = expr
    write_json(paths["spec"], spec)
    report = run(paths)
    assert report["diagnostics"]["overall"]["conditional_mean_or_location_guide"]["mean"] == pytest.approx(expected)


@pytest.mark.parametrize("field,value", [
    ("numeric_predictors", ["key"]), ("numeric_predictors", ["y"]),
    ("numeric_predictors", ["group"]), ("numeric_predictors", ["x", "x"]),
    ("group_by", ["key"]), ("group_by", ["y"]), ("group_by", ["x"]),
    ("outcome", "x"), ("interpretation", "approximately_true"), ("schema_version", True),
    ("conditional_mean", "__import__('os').system('bad')"),
    ("conditional_mean", {"column": "y"}), ("conditional_mean", {"column": "key"}),
    ("conditional_mean", {"column": "unlisted"}),
    ("conditional_mean", {"const": True}), ("conditional_mean", {"const": float("nan")}),
    ("conditional_mean", {"op": "log", "args": [{"const": 1}, {"const": 2}]}),
    ("conditional_mean", {"op": "pow", "base": {"const": 2}, "exponent": 9}),
    ("conditional_mean", {"op": "add", "args": [{"const": 1}]}),
    ("conditional_mean", {"const": 1, "extra": 2}),
])
def test_strict_spec_rejections(field, value):
    spec = fixture_spec()
    spec[field] = value
    with pytest.raises(ContractError):
        validate_self_consistency_spec(fixture_task(), spec)


def test_unknown_top_level_missing_interpretation_and_unsupported_mode():
    for mutation in (lambda spec: spec.update(extra=1), lambda spec: spec.pop("interpretation")):
        spec = fixture_spec()
        mutation(spec)
        with pytest.raises(ContractError):
            validate_self_consistency_spec(fixture_task(), spec)
    task = fixture_task()
    task["mode"] = "completion"
    with pytest.raises(ContractError, match="enrichment"):
        validate_self_consistency_spec(task, fixture_spec())


@pytest.mark.parametrize("entries", [
    [{"key": "a", "value": 1}],
    [{"key": "a", "value": 1}, {"key": "a", "value": 2}],
    [{"key": "a", "value": 1}, {"key": "b", "value": 1}, {"key": "d", "value": 1}],
    [{"key": "a", "value": {"const": 1}}],
])
def test_lookup_must_be_complete_unique_and_constant(entries):
    spec = fixture_spec()
    spec["conditional_mean"] = {"lookup": {"column": "group", "values": entries}}
    with pytest.raises(ContractError):
        validate_self_consistency_spec(fixture_task(), spec)


def test_expression_depth_is_bounded():
    expr = {"const": 1}
    for _ in range(40):
        expr = {"op": "add", "args": [expr, {"const": 1}]}
    spec = fixture_spec()
    spec["conditional_mean"] = expr
    with pytest.raises(ContractError, match="budget"):
        validate_self_consistency_spec(fixture_task(), spec)


@pytest.mark.parametrize("field,expr", [
    ("conditional_mean", {"op": "div", "args": [{"const": 1}, {"const": 0}]}),
    ("conditional_mean", {"op": "pow", "base": {"const": -1}, "exponent": 0.5}),
    ("conditional_mean", {"op": "mul", "args": [{"const": 1e300}, {"const": 1e300}]}),
    ("conditional_sd", {"const": 0}), ("conditional_sd", {"const": -1}),
])
def test_invalid_realized_arithmetic_does_not_create_report(inputs, field, expr):
    paths, _, spec, _ = inputs
    spec[field] = expr
    write_json(paths["spec"], spec)
    with pytest.raises(ContractError):
        run(paths)
    assert not paths["output"].exists()


@pytest.mark.parametrize("mutation", ["changed_x", "reformatted_x", "reordered_rows", "duplicate_id", "wrong_columns", "ragged", "nonfinite", "extra_row"])
def test_table_contract_and_literal_observed_preservation(inputs, mutation):
    paths, _, _, observed = inputs
    header = ["key", "x", "w", "group", "y"]
    rows = [row + [y] for row, y in zip(observed, [11, 10, 20, 19])]
    if mutation == "changed_x":
        rows[0][1] = "0.01"
    elif mutation == "reformatted_x":
        rows[0][1] = "0.0"
    elif mutation == "reordered_rows":
        rows.reverse()
    elif mutation == "duplicate_id":
        rows[0][0] = rows[1][0]
    elif mutation == "wrong_columns":
        header[1] = "wrong"
    elif mutation == "ragged":
        rows[0].append("extra")
    elif mutation == "nonfinite":
        rows[0][-1] = "Infinity"
    elif mutation == "extra_row":
        rows.append(rows[0])
    write_csv(paths["generated"], header, rows)
    with pytest.raises(ContractError):
        run(paths)
    assert not paths["output"].exists()


def test_duplicate_json_keys_rejected(inputs):
    paths, _, _, _ = inputs
    paths["spec"].write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
    with pytest.raises(ContractError, match="Duplicate JSON"):
        run(paths)


def test_missing_predictor_rejected_even_when_not_used_in_mean(inputs):
    paths, task, spec, rows = inputs
    task["columns"][2]["nullable"] = True
    rows[0][2] = ""
    write_json(paths["task"], task)
    write_csv(paths["observed"], ["key", "x", "w", "group"], rows)
    write_csv(paths["generated"], ["key", "x", "w", "group", "y"], [row + [1] for row in rows])
    with pytest.raises(ContractError, match="missing"):
        run(paths)


def test_duplicate_outcomes_constant_residuals_and_constant_predictor(inputs):
    paths, _, spec, rows = inputs
    for row in rows:
        row[2] = "7"
    spec["conditional_mean"] = {"const": 1}
    write_json(paths["spec"], spec)
    write_csv(paths["observed"], ["key", "x", "w", "group"], rows)
    write_csv(paths["generated"], ["key", "x", "w", "group", "y"], [row + [1] for row in rows])
    diagnostics = run(paths)["diagnostics"]
    assert diagnostics["duplicate_outcome_values"] == {"unique_count": 1, "repeated_value_count": 1,
                                                        "extra_occurrence_count": 3, "largest_multiplicity": 4}
    assert diagnostics["residual_predictor_associations"]["x"]["pearson"]["status"] == "undefined_constant_vector"
    assert diagnostics["predictor_design"]["constant_predictors"] == ["w"]


def test_single_row_and_no_numeric_predictors(inputs):
    paths, task, spec, rows = inputs
    task["n_rows"] = 1
    spec["numeric_predictors"] = []
    spec["conditional_mean"] = {"const": 5}
    write_json(paths["task"], task)
    write_json(paths["spec"], spec)
    write_csv(paths["observed"], ["key", "x", "w", "group"], rows[:1])
    write_csv(paths["generated"], ["key", "x", "w", "group", "y"], [rows[0] + [6]])
    diagnostics = run(paths)["diagnostics"]
    assert diagnostics["overall"]["residual"]["sample_sd"] is None
    assert diagnostics["overall"]["residual"]["sample_sd_status"] == "undefined_n_lt_2"
    assert diagnostics["predictor_design"]["status"] == "full_column_rank"


def test_joint_groups_reveal_deviations_that_cancel_in_margins(inputs):
    paths, task, spec, rows = inputs
    task["columns"].insert(4, {"name": "phase", "kind": "category", "unit": "invented",
                                "role": "observed", "nullable": False, "categories": ["u", "v"]})
    spec["group_by"] = ["group", "phase"]
    spec["conditional_mean"] = {"const": 0}
    rows = [row + [phase] for row, phase in zip(rows, ["u", "v", "u", "v"])]
    write_json(paths["task"], task)
    write_json(paths["spec"], spec)
    write_csv(paths["observed"], ["key", "x", "w", "group", "phase"], rows)
    write_csv(paths["generated"], ["key", "x", "w", "group", "phase", "y"],
              [row + [y] for row, y in zip(rows, [1, -1, -1, 1])])
    diagnostics = run(paths)["diagnostics"]
    for marginal in diagnostics["groups"].values():
        for entry in marginal:
            if entry["n"]:
                assert entry["summaries"]["residual"]["mean"] == pytest.approx(0)
    joint = diagnostics["joint_groups"]
    assert joint["columns"] == ["group", "phase"]
    assert joint["declared_group_count"] == 6
    assert joint["observed_group_count"] == 4
    assert joint["empty_group_count"] == 2
    assert [entry["summaries"]["residual"]["mean"] for entry in joint["groups"]] == [1, -1, -1, 1, None, None]
    assert joint["groups"][0]["categories"] == {"group": "a", "phase": "u"}


def test_empty_group_by_has_no_implied_joint_groups(inputs):
    paths, _, spec, _ = inputs
    spec["group_by"] = []
    write_json(paths["spec"], spec)
    joint = run(paths)["diagnostics"]["joint_groups"]
    assert joint == {"status": "not_requested", "columns": [], "declared_group_count": 0,
                     "observed_group_count": 0, "empty_group_count": 0, "groups": []}


def test_joint_group_budget():
    task, spec = fixture_task(), fixture_spec()
    task["columns"][3]["categories"] = [str(i) for i in range(4097)]
    spec["conditional_mean"] = {"const": 0}
    with pytest.raises(ContractError, match="Cartesian product"):
        validate_self_consistency_spec(task, spec)


def test_cli_success_and_rejection(inputs, capsys):
    paths, _, _, _ = inputs
    args = [value for name in ("task", "observed", "generated", "spec", "output")
            for value in ("--" + name, str(paths[name]))]
    assert main(args) == 0
    assert json.loads(capsys.readouterr().out)["scientific_validity"] == "not_assessed"
    assert main(args) == 2
    assert "Output already exists" in capsys.readouterr().err
