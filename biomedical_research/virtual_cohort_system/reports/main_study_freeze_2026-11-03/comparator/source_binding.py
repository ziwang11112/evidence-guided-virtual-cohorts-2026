"""Pure normalization recipes for the approved external packets.

This module performs no I/O, random sampling, clinical fitting, or dispatch.
`prepare_contexts` must only be called on hash-bound arm packets after admission.
It returns source-context fitting inputs, not a target candidate or release.
"""
from __future__ import annotations

import math
from typing import Any

from moment_reference import (lognormal_from_mean_sd, lognormal_from_quartiles,
                              truncated_lognormal_from_mean_sd, shifted_lognormal_from_mean_sd)


IFCC_TO_NGSP_SLOPE = 0.09148
IFCC_TO_NGSP_OFFSET = 2.152
GLUCOSE_MMOL_TO_MG_DL = 18.0


def _age_uniform(mean: float, sd: float) -> dict[str, Any]:
    half = math.sqrt(3) * sd
    if mean - half < 18:
        raise ValueError("Moment-matched uniform age law crosses adult support; no automatic replacement")
    return {"kind": "uniform", "low": mean - half, "high": mean + half}


def _slope_constraint(eid: str, value: float, predictor: str, marginals: dict) -> dict:
    return {"evidence_id": eid, "value": value, "numerical_scale": 1.0,
            "operator": {"kind": "ols_coefficient", "outcome": "hba1c",
                         "regressors": ["age", "female", predictor], "term": predictor}}


def _context(context_id: str, marginals: dict, constraints: list) -> dict:
    return {"role": "external_source", "source_context_id": context_id,
            "marginals": marginals, "constraints": constraints,
            "assumptions": [
                "Qualified equal-weight selected-source population law, not reconstructed participants or original survey weights",
                "Bounded uniform source age matches the admitted moments/quantile fit; not an empirical age distribution",
                "Binary female variable is independent of the continuous variables; unspecified nuisance associations remain assumptions",
                "Positive lognormal margins and latent Gaussian copula; unspecified dependence completed by the entropy objective",
                "Source marginal summaries are treated as point constraints with unknown estimation uncertainty",
                "Selection not represented by the declared source support remains an applicability limitation",
            ]}


def _prepare_chns(packet: dict, arm: str) -> dict:
    base = packet["shared_base"]
    records = {x["id"]: x for x in base["grouped_marginal_records"]}
    relationships = {x["id"]: x for x in packet["relationship_records"]}
    if packet["arm"] != arm or bool(relationships) != (arm == "E1"):
        raise ValueError("CHNS packet/arm mismatch")
    contexts, normalizations = [], []
    for prefix, cid, glucose_record, hba_record in [
        ("J", "CTX_JANSEN_SELECTED", "M_J_FPG", "M_J_HBA1C_IFCC"),
        ("B", "CTX_BAO_ANALYZED", "M_B_FPG", "M_B_HBA1C_PERCENT"),
        ("M", "CTX_MIND_ANALYZED", "M_M_FSG", "M_M_HBA1C_PERCENT"),
    ]:
        margins = {}
        for variable, rid in [("bmi", f"M_{prefix}_BMI"), ("glucose", glucose_record), ("hba1c", hba_record)]:
            item = records[rid]
            if item["kind"] == "reported_mean_and_individual_sd":
                mean, sd = item["mean"], item["individual_sd"]
                if rid == "M_J_HBA1C_IFCC":
                    mean = mean * IFCC_TO_NGSP_SLOPE + IFCC_TO_NGSP_OFFSET
                    sd *= IFCC_TO_NGSP_SLOPE
                if rid == "M_J_HBA1C_IFCC":
                    margins[variable] = shifted_lognormal_from_mean_sd(mean, sd, IFCC_TO_NGSP_OFFSET)
                elif rid == "M_J_FPG":
                    margins[variable] = truncated_lognormal_from_mean_sd(mean, sd, 0.0, 7.0)
                else:
                    margins[variable] = lognormal_from_mean_sd(mean, sd)
            elif item["kind"] == "reported_median_and_quartile_endpoints":
                fit = lognormal_from_quartiles(item["q1"], item["median"], item["q3"])
                margins[variable] = fit["marginal"]
                normalizations.append({"record_id": rid, **fit})
            else:
                raise ValueError("Unsupported source marginal record")
        age = records[f"M_{prefix}_AGE"]
        if "mean" in age:
            age_model = _age_uniform(age["mean"], age["individual_sd"])
        else:
            centre = (age["q1"] + age["median"] + age["q3"]) / 3
            width = 2 * (age["q3"] - age["q1"])
            age_model = {"kind": "uniform", "low": centre - width / 2, "high": centre + width / 2}
            if age_model["low"] < 20:
                raise ValueError("Bao age approximation violates the admitted lower boundary")
            normalizations.append({"record_id": age["id"], "rule": "unweighted_uniform_quantile_least_squares",
                                   "implied_quartiles": [centre - width / 4, centre, centre + width / 4],
                                   "reported_quartiles": [age["q1"], age["median"], age["q3"]]})
        if prefix == "M" and not (age_model["low"] >= 61 and age_model["high"] <= 80):
            raise ValueError("MIND age approximation violates admitted source support")
        sex = records[f"M_{prefix}_{'MALE' if prefix == 'J' else 'FEMALE'}"]
        p = sex["derived_fraction"]
        if sex["category"] == "male":
            p = 1 - p
        margins = {"age": age_model, "female": {"kind": "bernoulli", "probability": p}, **margins}
        constraints = []
        if arm == "E1":
            if prefix == "J":
                for eid, predictor in [("R_JANSEN_BMI", "bmi"), ("R_JANSEN_FPG", "glucose")]:
                    value = relationships[eid]["reported"]["estimate"] * IFCC_TO_NGSP_SLOPE
                    constraints.append(_slope_constraint(eid, value, predictor, margins))
            else:
                eid = "R_BAO_PEARSON" if prefix == "B" else "R_MIND_SPEARMAN"
                constraints.append({"evidence_id": eid, "value": relationships[eid]["reported"]["estimate"],
                                    "numerical_scale": 1.0,
                                    "operator": {"kind": "pearson_correlation" if prefix == "B" else "spearman_correlation",
                                                 "columns": ["glucose", "hba1c"]}})
        contexts.append(_context(cid, margins, constraints))
    return {"contexts": contexts, "normalization_records": normalizations,
            "unhandled_relational_items": [], "case_construction_authorized": False}


def _prepare_ensanut(packet: dict, arm: str) -> dict:
    items = {x["id"]: x for x in packet["items"]}
    value = lambda name: items[name]["estimate"]
    # Native IFCC is the one canonical representation. Rounded percent values
    # stay visible as alternative representations, not independent constraints.
    h_mean = value("J_T1_hba1c_mean_ifcc") * IFCC_TO_NGSP_SLOPE + IFCC_TO_NGSP_OFFSET
    h_sd = value("J_T1_hba1c_sd_ifcc") * IFCC_TO_NGSP_SLOPE
    margins = {
        "age": _age_uniform(value("J_T1_age_mean_task"), value("J_T1_age_sd_task")),
        "female": {"kind": "bernoulli", "probability": value("J_T1_female_proportion_derived")},
        "bmi": lognormal_from_mean_sd(value("J_T1_bmi_mean_task"), value("J_T1_bmi_sd_task")),
        "glucose": truncated_lognormal_from_mean_sd(value("J_T1_glucose_mean_mg_dL_derived"),
                                                    value("J_T1_glucose_sd_mg_dL_derived"), 0.0, 126.0),
        "hba1c": shifted_lognormal_from_mean_sd(h_mean, h_sd, IFCC_TO_NGSP_OFFSET),
    }
    constraints = []
    if arm == "E1":
        constraints = [_slope_constraint(eid, value(eid), predictor, margins) for eid, predictor in
                       [("J_T2_bmi_slope_task_derived", "bmi"), ("J_T2_glucose_slope_task_derived", "glucose")]]
    elif any(name.startswith("J_T2_") or name.startswith("P_NHANES_") for name in items):
        raise ValueError("E1 relationship information cannot enter the E0 packet")
    unhandled = [{"evidence_id": name, "role": "contextual_unfitted",
                  "reason": "Pani individual dispersion/source age law and original survey weighting are not bound; no source=target quota substitution or SE-to-SD conversion"}
                 for name in items if name.startswith("P_NHANES_")]
    return {"contexts": [_context("lifelines", margins, constraints)],
            "normalization_records": [{"rule": "native_IFCC_canonical; rounded_percent_alternative_not_second_constraint",
                                       "implied_mean_percent": h_mean, "implied_individual_sd_percent": h_sd}],
            "unhandled_relational_items": unhandled, "case_construction_authorized": False}


def prepare_contexts(case_id: str, arm: str, packet: dict) -> dict:
    if arm not in {"E0", "E1"}:
        raise ValueError("Unknown information condition")
    if case_id == "CHNS2009":
        result = _prepare_chns(packet, arm)
    elif case_id == "ENSANUT2018":
        result = _prepare_ensanut(packet, arm)
    else:
        raise ValueError("Unbound case")
    return {"case_id": case_id, "arm": arm, **result}
