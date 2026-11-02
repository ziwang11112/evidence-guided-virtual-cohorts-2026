"""Fixed K01 descriptive source operators, NOT an execution-backed collector.

Call only on a context-guarded source frame. Production must separately bind
execution/candidate/evidence and semantic_feedback_v1; this helper gives neither
source approvals nor exact-source discrepancy certification.
"""
import numpy as np
import pandas as pd
from cohort_harness.source_checks import apply_operator
from generated_validity import validate_generated_context


def compute_source_descriptives(frame: pd.DataFrame, task: dict, *, context_id: str):
    if context_id not in {"source_mind_china_2019", "source_ayele_dire_dawa_2017"}:
        raise ValueError("Only the two declared source contexts are supported")
    guard = validate_generated_context(frame, task, context_id=context_id)
    records = []

    def numeric(key, col, kind, unit):
        operator = {"kind": kind, "column": col, "unit": unit, "selection": [], "missing_policy": "error"}
        result = apply_operator(frame, operator)
        records.append({"id": key, "operator": operator, "derived_event": None,
                        "diagnostic": result, "sd_ddof": 1 if kind=="sd" else None})

    def fraction(key, predicates):
        mask = np.ones(len(frame), dtype=bool)
        for predicate in predicates:
            series=frame[predicate["column"]]
            mask &= getattr(series, predicate["op"])(predicate["value"]).to_numpy(dtype=bool)
        # This derived indicator represents the entire event, not a selection.
        # Every original row stays in the denominator, including event negatives.
        derived = pd.DataFrame({"__k01_event": mask.astype(int)})
        operator = {"kind":"proportion", "unit":"1", "selection":[], "missing_policy":"error",
                    "event":{"column":"__k01_event", "op":"eq", "value":1}}
        result=apply_operator(derived,operator)
        assert result["n_used"]==len(frame)
        records.append({"id":key,"operator":operator,
                        "derived_event":{"logic":"and", "predicates":predicates,
                            "mapping":"1 if every predicate holds, else 0; all original rows retained"},
                        "diagnostic":result,"sd_ddof":None})

    def p(column,op,value):
        return {"column":column,"op":op,"value":value}

    if context_id=="source_mind_china_2019":
        for key,col,unit in [("age","age","year"),("bmi","bmi","kg/m^2"),
                             ("serum_glucose_fsg","glucose","mmol/L")]:
            numeric("MIND_K01_"+key+"_mean",col,"mean",unit)
            numeric("MIND_K01_"+key+"_sd",col,"sd",unit)
        fraction("MIND_K01_female_proportion",[p("sex","eq","F")])
    else:
        numeric("ayele_age_mean","age","mean","year")
        numeric("ayele_age_sd","age","sd","year")
        fraction("ayele_sex_male",[p("sex","eq","M")])
        fraction("ayele_sex_female",[p("sex","eq","F")])
        for lo,hi in [(25,35),(35,45),(45,55),(55,65)]:
            fraction(f"ayele_age_{lo}_{hi-1}",[p("age","ge",lo),p("age","lt",hi)])
        fraction("ayele_bmi_underweight",[p("bmi","lt",18.5)])
        fraction("ayele_bmi_normal",[p("bmi","ge",18.5),p("bmi","le",24.9)])
        fraction("ayele_bmi_overweight",[p("bmi","ge",25)])
    return {"kind":"k01_unweighted_source_descriptives_v1", "context_id":context_id,
        "guard":guard,"checks":records,"exact_source_replay":False,"source_approvals_created":False,
        "semantic_feedback_v1_invoked":False,"execution_authenticated":False,"collector_integrated":False,
        "source_uncertainty_estimated":False,"source_point_values_compared":False,
        "assumptions":["equal-weight descriptive scenario; source weights not reported",
            "sample SD ddof1; source SD divisor unreported",
            "source selection/imputation represented by an assumed analytic population",
            "Ayele age bins interpreted as completed-year half-open decades",
            "Ayele BMI normal bin retains printed24.9 boundary and gap before25"],
        "limitations":"Arithmetic only; no source authenticity, exact replay or transport validation"}
