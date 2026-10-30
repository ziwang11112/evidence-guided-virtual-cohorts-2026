"""Invented values only; never read a participant or reference file."""
import numpy as np
import pandas as pd
import pytest
from analytical_points import evaluate_points, wls_point, normalize_visible


def fixture():
    rng = np.random.default_rng(91303)
    n = 600
    x = pd.DataFrame({"age": rng.integers(20, 80, n), "sex": rng.integers(1, 3, n),
                      "bmi": rng.uniform(18, 40, n), "glucose_mg_dl": rng.uniform(75, 140, n)},
                     index=[f"invented_{i}" for i in range(n)])
    w = pd.Series(rng.uniform(.5, 3, n), index=x.index)
    return x, w


def test_linear_coefficients_and_weight_scaling():
    x, w = fixture()
    A, B, F = (x.age-50)/10, (x.bmi-25)/5, (x.sex==2).astype(float)
    y = 5 + .2*A + .3*B + .1*F
    r = evaluate_points(x, y, w, "pns_hba1c")
    assert r["adjusted_age_per10"]["estimate"] == pytest.approx(.2)
    assert r["adjusted_bmi_per5"]["estimate"] == pytest.approx(.3)
    q = evaluate_points(x, y, 173*w, "pns_hba1c")
    assert q["adjusted_bmi_per5"]["estimate"] == pytest.approx(r["adjusted_bmi_per5"]["estimate"])


def test_log_curvature_and_interaction_are_estimated_not_forced():
    x, w = fixture()
    A, B, F, G = (x.age-50)/10, (x.bmi-25)/5, (x.sex==2).astype(float), np.log(x.glucose_mg_dl/100)
    for curvature in [-.04, .04]:
        y = np.exp(2 + .1*A + .2*B + .1*F + .3*G + curvature*B*B)
        r = evaluate_points(x, y, w, "nhanes_insulin")
        assert r["bmi_curvature_second_difference"]["estimate"] == pytest.approx(2*curvature)
    y = np.exp(2 + .1*A + .2*B + .1*F + .3*G - .07*F*B)
    r = evaluate_points(x, y, w, "nhanes_insulin")
    assert r["female_minus_male_bmi_slope_per5"]["estimate"] == pytest.approx(-.07)


def test_derived_homa_is_not_independent_and_uses_correct_units():
    x, w = fixture()
    x["glucose_mg_dl"] = 90.
    y = pd.Series(9., index=x.index)
    r = evaluate_points(x, y, w, "nhanes_insulin")
    assert r["derived_homa1_ir_mean"]["estimate"] == pytest.approx(2.)
    assert r["derived_homa1_ir_mean"]["independent_biological_validation"] is False
    assert r["adjusted_age_per10"]["status"] == "nonestimable"  # constant glucose duplicates intercept


def test_reordered_ids_are_rejected():
    x, w = fixture()
    y = pd.Series(5., index=x.index)
    with pytest.raises(ValueError, match="index"):
        evaluate_points(x, y.iloc[::-1], w, "pns_hba1c")


def test_nonfinite_and_nonpositive_inputs_fail():
    x, w = fixture()
    y = pd.Series(5., index=x.index)
    y.iloc[0] = np.nan
    with pytest.raises(ValueError, match="nonfinite"):
        evaluate_points(x, y, w, "pns_hba1c")
    y.iloc[0] = 0
    with pytest.raises(ValueError, match="Nonpositive"):
        evaluate_points(x, y, w, "nhanes_insulin")
    # Linear HbA1c analysis must not silently add target-magnitude selection.
    result = evaluate_points(x, y, w, "pns_hba1c")
    assert result["weighted_arithmetic_mean"]["n"] == len(x)


def test_empty_cells_retained_and_row_permutation_invariant():
    x, w = fixture()
    x["age"] = 30
    y = pd.Series(5., index=x.index)
    r = evaluate_points(x, y, w, "pns_hba1c")
    assert r["cell_age60_79_sex1_bmige30_mean"]["status"] == "nonestimable"
    order = x.sample(frac=1, random_state=2).index
    q = evaluate_points(x.loc[order], y.loc[order], w.loc[order], "pns_hba1c")
    assert q["weighted_arithmetic_mean"]["estimate"] == pytest.approx(r["weighted_arithmetic_mean"]["estimate"])


def test_actual_schema_adapter_maps_sex_without_positional_guessing():
    x = pd.DataFrame({"row_id":["a","b"], "age_years":[40,50], "sex":["female","male"], "bmi_kg_m2":[25.,30.]})
    z = normalize_visible(x,"pns_hba1c")
    assert list(z.index) == ["a","b"] and z.sex.tolist() == [2,1]
    assert list(z.columns) == ["age","sex","bmi"]
    with pytest.raises(ValueError,match="schema"):
        normalize_visible(x.assign(hba1c_pct=[5.,6.]),"pns_hba1c")
