"""Independent provider QA using eight hand-specified arithmetic rows only.

No candidate, biomedical simulator, patient file, or isolated run is executed.
The evaluate() boundary is mocked; this is not scientific generation evidence.
"""
import importlib.util
import json
from pathlib import Path
import math
import sys

import numpy as np
import pandas as pd
import pytest

HERE = Path(__file__).resolve().parent
HARNESS = HERE.parents[2]
sys.path.insert(0, str(HARNESS))
spec = importlib.util.spec_from_file_location("independent_provider_under_review", HERE / "analysis_feedback.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

DEFINITIONS = {
    "analyses": [
        {"id": "E1", "outcome": "hba1c", "predictors": ["age", "female", "bmi"], "term": "bmi", "unit": "%/(kg/m^2)"},
        {"id": "E2", "outcome": "hba1c", "predictors": ["age", "female", "glucose"], "term": "glucose", "unit": "%/(mmol/L)"},
        {"id": "E3", "outcome": "hba1c", "predictors": ["female", "bmi", "glucose", "age"], "term": "age", "unit": "%/year"},
    ],
    "diagnostics": {"marginal_variables": ["age", "female", "bmi", "glucose", "hba1c"]},
}


def fixture_rows():
    # Four pairwise orthogonal contrasts, with an intercept: all slopes are known.
    signs = [(1, 1, 1, 1), (1, 1, -1, 1), (1, -1, 1, -1), (1, -1, -1, -1),
             (-1, 1, 1, -1), (-1, 1, -1, -1), (-1, -1, 1, 1), (-1, -1, -1, 1)]
    rows = []
    for i, (a, b, c, d) in enumerate(signs):
        age, female, bmi, glucose = 50 + 2*a, (1+b)/2, 25+c, 5+d/2
        y = 10 + .2*age + .4*female + .6*bmi + .8*glucose
        rows.append([f"arithmetic_only_{i}", age, female, bmi, glucose, y])
    return pd.DataFrame(rows, columns=["row_id", "age", "female", "bmi", "glucose", "hba1c"])


def ranks(values):
    """Average-tie ranks without pandas/numpy ranking."""
    ordered = sorted(enumerate(values), key=lambda t: t[1])
    answer = [None] * len(ordered)
    left = 0
    while left < len(ordered):
        right = left + 1
        while right < len(ordered) and ordered[right][1] == ordered[left][1]:
            right += 1
        rank = ((left+1) + right)/2
        for i, _ in ordered[left:right]:
            answer[i] = rank
        left = right
    return answer


def pearson(x, y):
    mx, my = sum(x)/len(x), sum(y)/len(y)
    numerator = sum((a-mx)*(b-my) for a, b in zip(x, y))
    return numerator / math.sqrt(sum((a-mx)**2 for a in x)*sum((b-my)**2 for b in y))


def linear_quantile(values, p):
    ordered = sorted(values)
    position = (len(values)-1)*p
    lower = math.floor(position)
    return ordered[lower] + (position-lower)*(ordered[min(lower+1, len(values)-1)]-ordered[lower])


def test_all_thirty_statistics_against_independent_arithmetic():
    frame = fixture_rows()
    result = M.generated_statistics(frame, DEFINITIONS)
    diagnostics = {r["id"]: r for r in result["diagnostics"]}
    assert len(diagnostics) == 27 and len(result["analyses"]) == 3
    expected = {"E1": .6, "E2": .8, "E3": .2}
    for row in result["analyses"]:
        assert row["value"] == pytest.approx(expected[row["id"]], abs=1e-12)
        assert row["status"] == "computed" and row["n"] == 8
    for name in DEFINITIONS["diagnostics"]["marginal_variables"]:
        xs = list(frame[name]); mean = sum(xs)/len(xs)
        stats = {"mean": mean, "sd": math.sqrt(sum((x-mean)**2 for x in xs)/(len(xs)-1)),
                 "q10": linear_quantile(xs, .1), "median": linear_quantile(xs, .5), "q90": linear_quantile(xs, .9)}
        for key, value in stats.items():
            assert diagnostics[name+"_"+key]["value"] == pytest.approx(value, abs=1e-12)
    x, y = list(frame.glucose), list(frame.hba1c)
    assert diagnostics["glucose_hba1c_pearson"]["value"] == pytest.approx(pearson(x, y))
    assert diagnostics["glucose_hba1c_spearman"]["value"] == pytest.approx(pearson(ranks(x), ranks(y)))
    assert result["quality"] == {"nonpositive_glycemia": {"glucose": 0, "hba1c": 0}, "duplicate_measurement_rows": 0}


def test_degenerate_and_zero_glycemia_are_retained_as_unavailable():
    frame = fixture_rows(); frame["glucose"] = 5.0
    with np.errstate(invalid="ignore", divide="ignore"):
        result = M.generated_statistics(frame, DEFINITIONS)
    assert {r["id"]: r["status"] for r in result["analyses"]} == {"E1": "computed", "E2": "unavailable", "E3": "unavailable"}
    joint = [r for r in result["diagnostics"] if r["id"].startswith("glucose_hba1c_")]
    assert all(r["value"] is None and r["status"] == "unavailable" for r in joint)
    frame = fixture_rows(); frame.loc[0, "glucose"] = 0
    result = M.generated_statistics(frame, DEFINITIONS)
    assert result["quality"]["nonpositive_glycemia"]["glucose"] == 1
    assert all(r["value"] is None for r in result["analyses"])


def test_duplicate_diagnostic_does_not_count_synthetic_identifiers():
    frame = fixture_rows()
    copied = frame.iloc[[0]].copy(); copied["row_id"] = "distinct_identifier_same_measurements"
    result = M.generated_statistics(pd.concat([frame, copied], ignore_index=True), DEFINITIONS)
    assert result["quality"]["duplicate_measurement_rows"] == 1


def fake_reference():
    return {"estimands": {key: {"coefficient": 874319.72, "interval": [874319.0, 874320.0]} for key in ("E1", "E2", "E3")},
            "diagnostics": {"joint": {"pearson": 874319.72, "spearman": 874319.72},
                            "marginal": {v: {k: 874319.72 for k in ("mean", "sd", "q10", "median", "q90")} for v in DEFINITIONS["diagnostics"]["marginal_variables"]}}}


@pytest.mark.parametrize("condition", ["L", "R"])
def test_provider_reference_access_matches_declared_condition(tmp_path, monkeypatch, condition):
    from cohort_harness import execution, lifecycle
    bundle = tmp_path / "b"; output = bundle/"executions"/"fixture"/"output"/"generated.csv"
    output.parent.mkdir(parents=True); output.write_text("ARITHMETIC FIXTURE MARKER ONLY; NO COHORT\n", encoding="utf-8")
    profile = tmp_path/"profile.json"; definitions = tmp_path/"definitions.json"; reference = tmp_path/"REFERENCE_SENTINEL_874319.json"
    definitions.write_text(json.dumps(DEFINITIONS), encoding="utf-8")
    (bundle/"task.json").write_text("{}", encoding="utf-8")
    config = {"information_condition": condition, "analysis_definitions": str(definitions)}
    if condition == "R": config["reference_summary"] = str(reference)
    profile.write_text(json.dumps(config), encoding="utf-8")
    reference.write_text(json.dumps(fake_reference()), encoding="utf-8")
    original_load = M.load; opened = []
    allowed = {profile.resolve(), definitions.resolve(), (bundle/"task.json").resolve()}
    if condition == "R": allowed.add(reference.resolve())
    def guarded_load(path):
        path = Path(path).resolve()
        assert path in allowed, "Undeclared/reference read in generated-only provider"
        opened.append(path)
        return original_load(path)
    monkeypatch.setattr(M, "load", guarded_load)
    monkeypatch.setattr(execution, "verify_execution", lambda *a: {"status": "success", "candidate": "candidates/fixture"})
    monkeypatch.setattr(lifecycle, "read_table", lambda *a, **kw: fixture_rows())
    result = M.evaluate(bundle, "fixture", "fixture", profile)
    assert (reference.resolve() in opened) == (condition == "R")
    assert len(result["analyses"]) == 3 and len(result["diagnostics"]) == 27
    for row in result["analyses"] + result["diagnostics"]:
        if condition == "R":
            assert row["reference"] == 874319.72
            assert row["difference"] == pytest.approx(row["value"]-874319.72)
        else:
            assert not set(row) & {"reference", "difference", "reference_interval"}
    assert ("874319" in json.dumps(result)) == (condition == "R")


def test_reference_comparison_does_not_mutate_generated_object():
    generated = M.generated_statistics(fixture_rows(), DEFINITIONS)
    before = json.dumps(generated, sort_keys=True)
    M.with_reference(generated, fake_reference())
    assert json.dumps(generated, sort_keys=True) == before
