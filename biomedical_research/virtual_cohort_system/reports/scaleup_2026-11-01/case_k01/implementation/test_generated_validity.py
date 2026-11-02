"""Invented small context tuples, especially source-as-target bypasses."""
import copy
import pandas as pd
import pytest
from generated_validity import CONTEXTS, COLUMNS, validate_generated_context
from cohort_harness.contracts import ContractError


def task(context):
    columns=[dict(name=n,kind=k,unit=u,role=r,nullable=False) for n,k,u,r in COLUMNS]
    columns[2]["categories"]=["F","M"]
    return {"schema_version":1,"task_id":"invented-k01","mode":"whole_cohort",
        "population":CONTEXTS[context]["population"],"row_id":"id","n_rows":2,"columns":columns,
        "information_policy":{"mode":"published_evidence","excluded_cohorts":[],"allowed_tools":[]},
        "budget":{"source_queries":0,"source_downloads":0,"revisions":1}}


def frame(age):
    return pd.DataFrame({"id":["a","b"],"age":[age,age+1],"sex":["F","M"],"bmi":[20.,22.],"glucose":[4.,5.]})


def test_context_age_and_task_binding_prevent_source_as_target_relabel():
    source="source_ayele_dire_dawa_2017"
    target="target_haalsi_pooled_poc"
    f=frame(30)
    assert validate_generated_context(f,task(source),context_id=source)["status"]=="valid"
    with pytest.raises(ContractError,match="population mismatch"):
        validate_generated_context(f,task(target),context_id=source)
    with pytest.raises(ContractError,match="age minimum"):
        validate_generated_context(f,task(target),context_id=target)


def test_target_no_upper_bound_source_has_its_own_upper_bound():
    target="target_haalsi_pooled_poc"
    source="source_mind_china_2019"
    assert validate_generated_context(frame(100),task(target),context_id=target)["status"]=="valid"
    with pytest.raises(ContractError,match="age maximum"):
        validate_generated_context(frame(80),task(source),context_id=source)


@pytest.mark.parametrize("defect",["missing","nonpositive","duplicate_id","short","global_age_bound","wrong_unit"])
def test_whole_frame_and_task_rejection_without_repair(defect):
    context="target_haalsi_pooled_poc"
    f,t=frame(50),task(context)
    if defect=="missing": f.loc[0,"glucose"]=float('nan')
    if defect=="nonpositive": f.loc[0,"glucose"]=0.
    if defect=="duplicate_id": f.loc[0,"id"]="b"
    if defect=="short": f=f.iloc[:1].copy()
    if defect=="global_age_bound": t["columns"][1]["minimum"]=40
    if defect=="wrong_unit": t["columns"][4]["unit"]="mg/dL"
    before,task_before=f.copy(deep=True),copy.deepcopy(t)
    with pytest.raises(ContractError): validate_generated_context(f,t,context_id=context)
    pd.testing.assert_frame_equal(f,before)
    assert t==task_before
