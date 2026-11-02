"""Independent invented-data identities and failure-boundary checks; no files."""
from itertools import product
import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm
from k01_analysis import IDS, analyze_frame


def invented():
    a, sexsign, b, err = np.array(list(product([-1., 1.], repeat=4))).T
    female = (sexsign+1)/2
    return pd.DataFrame({"age": 60+10*a, "sex": np.where(female, "F", "M"),
        "bmi": 25+5*b, "glucose": 10+0.3*a+0.4*b+0.6*female*b+0.2*err})


def test_closed_form_contrasts_and_independent_HC3():
    f = invented()
    r = analyze_frame(f, role="reference")
    assert r["status"] == "complete"
    # Balanced covariates: pooled BMI effect averages the two sex slopes.
    assert [r["estimands"][k]["estimate"] for k in IDS] == pytest.approx([0.7, 0.3, 0.6])
    raw = pd.DataFrame({"intercept": 1., "age": f.age, "sex": (f.sex=="F").astype(float), "bmi": f.bmi})
    base = sm.OLS(f.glucose, raw).fit(cov_type="HC3")
    interaction_raw = raw.assign(sex_bmi=raw.sex*raw.bmi)
    interaction = sm.OLS(f.glucose, interaction_raw).fit(cov_type="HC3")
    for key, oracle, term, scale in [(IDS[0],base,"bmi",5),(IDS[1],base,"age",10),(IDS[2],interaction,"sex_bmi",5)]:
        ep = r["estimands"][key]
        assert ep["estimate"] == pytest.approx(oracle.params[term]*scale, abs=1e-12)
        assert ep["interval"]["standard_error"] == pytest.approx(oracle.bse[term]*scale, abs=1e-12)
    assert r["metric_denominators"]["glucose"]["sample_sd"] == pytest.approx(f.glucose.std(ddof=1))


def test_sex_relabel_reverses_interaction_but_not_pooled_effects():
    f = invented()
    first = analyze_frame(f, role="generated")
    f.sex = f.sex.map({"F":"M","M":"F"})
    second = analyze_frame(f, role="generated")
    for key in IDS[:2]:
        assert first["estimands"][key]["estimate"] == pytest.approx(second["estimands"][key]["estimate"])
    assert first["estimands"][IDS[2]]["estimate"] == pytest.approx(-second["estimands"][IDS[2]]["estimate"])
    assert second["metric_denominators"] == {}
    assert all(x["interval"]["status"]=="unavailable" for x in second["estimands"].values())


def test_reference_filter_is_common_but_generated_invalid_row_rejects_all():
    f = invented()
    bad = f.iloc[:4].copy()
    bad.loc[bad.index[0],"glucose"] = np.nan
    bad.loc[bad.index[1],"age"] = 39
    bad.loc[bad.index[2],"bmi"] = 0
    bad.loc[bad.index[3],"sex"] = None
    combined = pd.concat([f,bad],ignore_index=True)
    measured = analyze_frame(combined,role="reference")
    generated = analyze_frame(combined,role="generated")
    assert measured["selection"]["eligible_rows"]==len(f)
    assert measured["selection"]["excluded_rows"]==4
    assert [measured["estimands"][k]["estimate"] for k in IDS]==pytest.approx([.7,.3,.6])
    assert generated["status"]=="invalid_input"
    assert all(x["estimate"] is None for x in generated["estimands"].values())


def test_interaction_rank_failure_does_not_hide_behind_base_fit():
    # Both sexes and full-rank base, but BMI has no within-F variation.
    f = invented()
    f.loc[f.sex=="F","bmi"] = 25
    r = analyze_frame(f,role="reference")
    assert r["designs"]["base"]["rank"]==4
    assert r["reason"]=="rank_deficient_interaction_design"
    assert all(e["estimate"] is None for e in r["estimands"].values())


@pytest.mark.parametrize("case",["unknown_sex","bool_numeric","complex_numeric","duplicate_columns"])
def test_invalid_canonical_schema_fails(case):
    f=invented()
    if case=="unknown_sex": f.loc[0,"sex"]="unknown"
    if case=="bool_numeric": f["bmi"]=True
    if case=="complex_numeric": f["glucose"]=f.glucose.astype(complex)
    if case=="duplicate_columns": f.columns=["age","sex","bmi","bmi"]
    assert analyze_frame(f,role="reference")["status"]=="invalid_input"


def test_constant_response_and_perfect_fit_have_distinct_point_estimate_rules():
    f=invented()
    f.glucose=5.
    r=analyze_frame(f,role="reference")
    assert r["reason"]=="constant_response"
    assert r["metric_denominators"]["glucose"]["status"]=="unavailable"
    f.glucose=5+0.02*f.age+0.04*f.bmi
    r=analyze_frame(f,role="reference")
    assert r["status"]=="complete"
    assert [r["estimands"][k]["estimate"] for k in IDS]==pytest.approx([.2,.2,0],abs=1e-12)
    assert all(e["interval"]["status"]=="unavailable" for e in r["estimands"].values())


def test_input_not_mutated_and_explicit_role_required():
    f=invented()
    before=f.copy(deep=True)
    analyze_frame(f,role="reference")
    pd.testing.assert_frame_equal(f,before)
    with pytest.raises(ValueError): analyze_frame(f,role="source")
