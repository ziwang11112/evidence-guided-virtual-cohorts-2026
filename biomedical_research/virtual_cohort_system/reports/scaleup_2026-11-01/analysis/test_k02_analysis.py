"""Small invented in-memory examples, with analytic answers; no fixture files."""
from itertools import product
import math

import numpy as np
import pandas as pd
import pytest

from k02_analysis import IDS, Z95, analyze_frame


def invented():
    # Orthogonal complete factorial: errors e/d are orthogonal to every regressor.
    a, s, b, e, d = np.array(list(product([-1., 1.], repeat=5))).T
    return pd.DataFrame({
        "age": 40 + 10*a, "sex": np.where(s > 0, "F", "M"), "bmi": 25 + 5*b,
        "hdl_cholesterol": 40 + 2*a + 3*s + 10*b + e,
        "total_cholesterol": 150 + 5*a - 2*s + 20*b + 2*e + 3*d,
    })


def test_closed_form_slopes_per5_residual_correlation_and_hc3():
    r = analyze_frame(invented(), role="reference")
    assert r["status"] == "complete"
    assert r["selection"]["eligible_rows"] == 32
    for key, estimate, error_variance in [(IDS[0], 10., 1.), (IDS[1], 20., 13.)]:
        ep = r["estimands"][key]
        assert ep["estimate"] == pytest.approx(estimate)
        # Constant leverage p/n=4/32 and BMI5 column has sum of squares n.
        se = math.sqrt(error_variance / (32 * (1-4/32)**2))
        assert ep["interval"]["standard_error"] == pytest.approx(se)
        assert ep["interval"]["lower"] == pytest.approx(estimate-Z95*se)
        assert ep["interval"]["upper"] == pytest.approx(estimate+Z95*se)
    assert r["estimands"][IDS[2]]["estimate"] == pytest.approx(2/math.sqrt(13))
    assert r["estimands"][IDS[2]]["interval"]["status"] == "unavailable"


def test_binary_category_relabel_invariance():
    f = invented()
    a = analyze_frame(f, role="reference")
    f["sex"] = f["sex"].map({"F": "M", "M": "F"})
    b = analyze_frame(f, role="reference")
    for key in IDS:
        assert a["estimands"][key]["estimate"] == pytest.approx(b["estimands"][key]["estimate"])
    for key in IDS[:2]:
        assert a["estimands"][key]["interval"]["standard_error"] == pytest.approx(
            b["estimands"][key]["interval"]["standard_error"])


def test_common_subset_is_fixed_and_exclusions_are_visible():
    f = invented()
    extra = f.iloc[:7].copy()
    extra.loc[extra.index[0], "hdl_cholesterol"] = np.nan
    extra.loc[extra.index[1], "total_cholesterol"] = np.inf
    extra.loc[extra.index[2], "age"] = 17.
    extra.loc[extra.index[3], "bmi"] = 0.
    extra.loc[extra.index[4], "sex"] = None
    extra.loc[extra.index[5], "total_cholesterol"] = -1.
    extra.loc[extra.index[6], "hdl_cholesterol"] = 0.
    result = analyze_frame(pd.concat([f, extra], ignore_index=True), role="reference")
    baseline = analyze_frame(f, role="reference")
    assert result["selection"]["eligible_rows"] == 32
    assert result["selection"]["excluded_rows"] == 7
    for key in IDS:
        assert result["estimands"][key]["n"] == 32
        assert result["estimands"][key]["estimate"] == pytest.approx(baseline["estimands"][key]["estimate"])


def test_rank_failure_preserves_all_three_endpoints():
    f = invented()
    f["age"] = f["bmi"] + 20
    r = analyze_frame(f, role="reference")
    assert r["status"] == "unavailable"
    assert set(r["estimands"]) == set(IDS)
    assert all(x["reason"] == "rank_deficient_design" for x in r["estimands"].values())


def test_constant_response_is_not_a_valid_zero_effect_claim():
    f = invented()
    f["hdl_cholesterol"] = 40.
    r = analyze_frame(f, role="reference")
    assert r["status"] == "partial"
    assert r["estimands"][IDS[0]]["reason"] == "constant_response"
    assert r["estimands"][IDS[1]]["status"] == "computed"
    assert r["estimands"][IDS[2]]["status"] == "unavailable"
    assert r["metric_denominators"]["hdl_cholesterol"]["sample_sd"] is None


def test_zero_residual_retains_slope_but_not_false_precision_or_correlation():
    f = invented()
    f["hdl_cholesterol"] = 30 + f["age"] + 2*f["bmi"]
    r = analyze_frame(f, role="reference")
    assert r["estimands"][IDS[0]]["estimate"] == pytest.approx(10.)
    assert r["estimands"][IDS[0]]["interval"]["status"] == "unavailable"
    assert r["estimands"][IDS[2]]["status"] == "unavailable"


@pytest.mark.parametrize("change", ["sex", "numeric_text", "boolean", "complex", "missing_column", "duplicate"])
def test_invalid_canonical_input_fails_without_dropping_endpoint(change):
    f = invented()
    if change == "sex":
        f.loc[0, "sex"] = "unknown"
    elif change == "numeric_text":
        f["bmi"] = f["bmi"].astype(str)
    elif change == "boolean":
        f["bmi"] = True
    elif change == "complex":
        f["bmi"] = f["bmi"].astype(complex)
    elif change == "missing_column":
        f = f.drop(columns="age")
    else:
        f = pd.concat([f, f[["age"]]], axis=1)
    r = analyze_frame(f, role="reference")
    assert r["status"] == "invalid_input"
    assert set(r["estimands"]) == set(IDS)
    assert all(x["status"] == "unavailable" for x in r["estimands"].values())


def test_too_few_rows_do_not_produce_saturated_fit_success():
    r = analyze_frame(invented().iloc[:4].copy(), role="reference")
    assert r["status"] == "unavailable"
    assert all(x["reason"] == "insufficient_rows_for_four_column_design"
               for x in r["estimands"].values())


def test_generated_mode_never_emits_synthetic_inference_or_metric_sd():
    r = analyze_frame(invented(), role="generated")
    assert r["status"] == "complete"
    assert r["metric_denominators"] == {}
    assert all(ep["interval"]["status"] == "unavailable" for ep in r["estimands"].values())


def test_extra_columns_do_not_add_filters_and_input_is_unchanged():
    f = invented()
    f["lifestyle"] = None
    f["LDL"] = np.nan
    original = f.copy(deep=True)
    result = analyze_frame(f, role="reference")
    assert result["selection"]["eligible_rows"] == 32
    pd.testing.assert_frame_equal(f, original)


def test_reference_sd_is_ddof1_and_explicitly_evaluation_only():
    f = invented()
    r = analyze_frame(f, role="reference")
    # HDL variance under the full balanced factorial: 2²+3²+10²+1², with n/(n-1).
    sd = r["metric_denominators"]["hdl_cholesterol"]
    assert sd["sample_sd"] == pytest.approx(math.sqrt(114*32/31))
    assert sd["ddof"] == 1
    assert sd["role"] == "evaluation_only_not_builder_input"


def test_role_is_explicit_and_unknown_roles_rejected():
    with pytest.raises(TypeError):
        analyze_frame(invented())
    with pytest.raises(ValueError):
        analyze_frame(invented(), role="builder")
