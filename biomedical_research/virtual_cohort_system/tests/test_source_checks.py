import math

import numpy as np
import pandas as pd
import pytest

from cohort_harness.source_checks import NotComputable, apply_operator, bound_file


def op(kind, **kwargs):
    return {"kind": kind, "unit": "arbitrary", "selection": [], "missing_policy": "error", **kwargs}


def test_group_mean_is_integral_over_rows_not_midpoint_prediction():
    # A source category has a skewed covariate distribution. E[X^2] != E[X]^2.
    table = pd.DataFrame({"x": [0., 0., 3.], "y": [0., 0., 9.]})
    result = apply_operator(table, op("mean", column="y"))
    assert result["value"] == 3
    assert result["value"] != table.x.mean() ** 2


def test_estimators_and_explicit_selection():
    table = pd.DataFrame({"x": [0., 1., 2., 3.], "y": [1., 3., 5., 7.]})
    assert apply_operator(table, op("sd", column="y"))["value"] == pytest.approx(math.sqrt(20 / 3))
    assert apply_operator(table, op("correlation", x="x", y="y"))["value"] == pytest.approx(1)
    fit = apply_operator(table, op("ols_coefficient", outcome="y", predictors=["x"], term="x", include_intercept=True))
    assert fit["value"] == pytest.approx(2)
    selected = apply_operator(table, op("mean", column="y", selection=[{"column": "x", "op": "ge", "value": 2}]))
    assert selected["value"] == 6 and selected["n_selected"] == 2
    proportion = apply_operator(table, op("proportion", unit="%", event={"column": "y", "op": "gt", "value": 3}))
    assert proportion["value"] == 50


def test_missingness_requires_explicit_policy_and_accounting():
    table = pd.DataFrame({"x": [1., np.nan, 3.]})
    with pytest.raises(ValueError, match="Missing"):
        apply_operator(table, op("mean", column="x"))
    result = apply_operator(table, op("mean", column="x", missing_policy="complete_cases"))
    assert result["value"] == 2 and result["n_missing_dropped"] == 1


def test_nonfinite_and_singular_results_never_silently_pass():
    with pytest.raises(ValueError, match="Nonfinite"):
        apply_operator(pd.DataFrame({"x": [1., np.inf]}), op("mean", column="x"))
    with pytest.raises(NotComputable):
        apply_operator(pd.DataFrame({"x": [1., 1.], "y": [2., 3.]}), op("correlation", x="x", y="y"))
    with pytest.raises(NotComputable):
        apply_operator(pd.DataFrame({"x": [1., 1., 1.], "y": [2., 3., 4.]}),
                       op("ols_coefficient", outcome="y", predictors=["x"], term="x", include_intercept=True))


@pytest.mark.parametrize("extra", [{"weights": "w"}, {"python": "print('no')"}, {"adjustment": ["z"]}])
def test_unimplemented_or_executable_operator_fields_rejected(extra):
    with pytest.raises(ValueError):
        apply_operator(pd.DataFrame({"x": [1., 2.]}), op("mean", column="x", **extra))


@pytest.mark.parametrize("relative", ["../secret.csv", "C:/secret.csv", "a.csv:stream", "a\\b.csv"])
def test_path_escape_rejected(tmp_path, relative):
    with pytest.raises(ValueError):
        bound_file(tmp_path, relative)
