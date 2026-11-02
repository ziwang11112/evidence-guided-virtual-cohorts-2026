import numpy as np
import pandas as pd
import pytest
from generated_validity import CONTEXTS,COLUMNS
from source_descriptives import compute_source_descriptives


def task(context,n):
    cols=[dict(name=a,kind=b,unit=c,role=d,nullable=False) for a,b,c,d in COLUMNS]
    cols[2]["categories"]=["F","M"]
    return {"schema_version":1,"task_id":"invented-source-descriptive","mode":"whole_cohort",
        "population":CONTEXTS[context]["population"],"row_id":"id","n_rows":n,"columns":cols,
        "information_policy":{"mode":"published_evidence","excluded_cohorts":[],"allowed_tools":[]},
        "budget":{"source_queries":0,"source_downloads":0,"revisions":1}}


def test_conjunction_is_unconditional_and_printed_BMI_gap_is_preserved():
    ctx="source_ayele_dire_dawa_2017"
    f=pd.DataFrame({"id":list('abcdef'),"age":[25.,34.9,35.,44.9,55.,64.],
        "sex":["M","F","M","F","M","F"],"bmi":[18.,18.5,24.9,24.95,25.,30.],"glucose":[4.]*6})
    before=f.copy(deep=True)
    r=compute_source_descriptives(f,task(ctx,6),context_id=ctx)
    d={x["id"]:x["diagnostic"] for x in r["checks"]}
    assert len(d)==11
    assert d["ayele_bmi_normal"]["value"]==pytest.approx(2/6) # not conditional2/5
    assert d["ayele_bmi_underweight"]["value"]==pytest.approx(1/6)
    assert d["ayele_bmi_overweight"]["value"]==pytest.approx(2/6)
    assert d["ayele_age_25_34"]["value"]==pytest.approx(2/6)
    assert d["ayele_age_35_44"]["value"]==pytest.approx(2/6)
    assert all(x["n_used"]==6 for x in d.values())
    pd.testing.assert_frame_equal(f,before)


def test_mean_and_sd_are_different_roles_and_all_seven_are_retained():
    ctx="source_mind_china_2019"
    f=pd.DataFrame({"id":list('abcd'),"age":[61.,65.,70.,80.],"sex":["F","F","F","M"],
        "bmi":[20.,22.,24.,26.],"glucose":[3.,4.,5.,8.]})
    r=compute_source_descriptives(f,task(ctx,4),context_id=ctx)
    d={x["id"]:x for x in r["checks"]}
    assert len(d)==7
    assert d["MIND_K01_serum_glucose_fsg_mean"]["diagnostic"]["value"]==5.
    assert d["MIND_K01_serum_glucose_fsg_sd"]["diagnostic"]["value"]==pytest.approx(np.sqrt(14/3))
    assert d["MIND_K01_serum_glucose_fsg_sd"]["sd_ddof"]==1
    assert d["MIND_K01_female_proportion"]["diagnostic"]["value"]==.75
    assert not r["source_uncertainty_estimated"] and not r["exact_source_replay"]


def test_target_context_cannot_be_substituted_for_a_source():
    with pytest.raises(ValueError,match="Only the two"):
        compute_source_descriptives(pd.DataFrame(),{},context_id="target_haalsi_pooled_poc")
