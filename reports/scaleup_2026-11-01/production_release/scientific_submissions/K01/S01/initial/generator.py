"""Pure K01 S01 analytic completion and drawing; no file I/O or lifecycle calls.

Inputs are caller-normalized source records, not authenticated evidence. This
component does not admit a packet, authorize a clinical run or enforce its ledger.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
from statistics import NormalDist
from typing import Any

import numpy as np
import pandas as pd
from scipy.special import betainc, betaincinv


MIND_CONTEXT = "source_mind_china_2019"
AYELE_CONTEXT = "source_ayele_dire_dawa_2017"
SOURCE_CONTEXTS = (MIND_CONTEXT, AYELE_CONTEXT)
TARGET_CONTEXT = "target_haalsi_pooled_poc"
COLUMNS = ("id", "age", "sex", "bmi", "glucose")
MAX_ROWS = 5000
_BOUNDS = {MIND_CONTEXT: (61.0, 80.0), AYELE_CONTEXT: (25.0, 64.0)}

# id -> context, normalized variable, statistic, unit, group (count items only).
_SPECS = {
    "MIND_K01_age_mean": (MIND_CONTEXT, "age", "arithmetic_mean", "year", None),
    "MIND_K01_age_sd": (MIND_CONTEXT, "age", "individual_standard_deviation", "year", None),
    "MIND_K01_bmi_mean": (MIND_CONTEXT, "bmi", "arithmetic_mean", "kg/m^2", None),
    "MIND_K01_bmi_sd": (MIND_CONTEXT, "bmi", "individual_standard_deviation", "kg/m^2", None),
    "MIND_K01_serum_glucose_fsg_mean": (MIND_CONTEXT, "glucose", "arithmetic_mean", "mmol/L", None),
    "MIND_K01_serum_glucose_fsg_sd": (MIND_CONTEXT, "glucose", "individual_standard_deviation", "mmol/L", None),
    "MIND_K01_female_proportion": (MIND_CONTEXT, "sex", "count_ratio", "1", "Female"),
    "ayele_age_mean": (AYELE_CONTEXT, "age", "arithmetic_mean", "year", None),
    "ayele_age_sd": (AYELE_CONTEXT, "age", "individual_standard_deviation", "year", None),
    "ayele_sex_male": (AYELE_CONTEXT, "sex", "count_ratio", "1", "Male"),
    "ayele_sex_female": (AYELE_CONTEXT, "sex", "count_ratio", "1", "Female"),
    "ayele_age_25_34": (AYELE_CONTEXT, "age", "count_ratio", "1", "25–34"),
    "ayele_age_35_44": (AYELE_CONTEXT, "age", "count_ratio", "1", "35–44"),
    "ayele_age_45_54": (AYELE_CONTEXT, "age", "count_ratio", "1", "45–54"),
    "ayele_age_55_64": (AYELE_CONTEXT, "age", "count_ratio", "1", "55–64"),
    "ayele_bmi_underweight": (AYELE_CONTEXT, "bmi", "count_ratio", "1", "<18.5"),
    "ayele_bmi_normal": (AYELE_CONTEXT, "bmi", "count_ratio", "1", "18.5–24.9"),
    "ayele_bmi_overweight": (AYELE_CONTEXT, "bmi", "count_ratio", "1", ">=25"),
}
EVIDENCE_IDS = tuple(_SPECS)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _exact(value: Any, keys: set[str]) -> None:
    _require(type(value) is dict and set(value) == keys, "Unexpected/missing fields")


def _finite(value: Any) -> bool:
    if type(value) not in {int, float}:
        return False
    try:
        return math.isfinite(value)
    except (ValueError, OverflowError):
        return False


def _digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _conventions() -> dict[str, Any]:
    return {
        "kind": "k01_s01_independent_marginal_completion_v1",
        "target_context_id": TARGET_CONTEXT,
        "columns": list(COLUMNS),
        "units": {"id": "1", "age": "year", "sex": "1", "bmi": "kg/m^2", "glucose": "mmol/L"},
        "sex_encoding": {"F": "Female", "M": "Male"},
        "target_donor_probabilities": [0.5, 0.5],
        "target_age_minimum": 40.0,
        "target_age_rule": "Condition each selected donor's age on >=40; keep donor probabilities1/2",
        "joint_law": "Independent age, sex, BMI, glucose within donor; identical glucose marginal for all contexts",
        "source_sd_interpretation": "Individual SD as population-moment approximation; source divisor/weights unknown",
        "ayele_bmi_thresholds": [18.5, 25.0],
        "ayele_middle_diagnostic_closed": [18.5, 24.9],
        "ayele_age_diagnostic_half_open": [[25, 35], [35, 45], [45, 55], [55, 65]],
        "age_diagnostic_interpretation": "Explicit completed-year approximation; printed labels retained",
        "s01_feedback_rule": "Precommit retention; no Monte Carlo recalibration",
    }


def _validate_inputs(records: Any) -> dict[str, dict[str, Any]]:
    _require(type(records) is list and len(records) == len(_SPECS), "Exactly18 normalized records required")
    by_id = {}
    common = {"evidence_id", "context_id", "variable", "statistic", "unit", "locator"}
    for row in records:
        _require(type(row) is dict, "Record must be a dict")
        item_id = row.get("evidence_id")
        _require(type(item_id) is str and item_id in _SPECS and item_id not in by_id,
                 "Unknown or duplicate evidence ID")
        context, variable, statistic, unit, group = _SPECS[item_id]
        extras = {"value"} if group is None else {"group", "numerator", "denominator"}
        if group is not None and context == AYELE_CONTEXT:
            extras |= {"reported_percentage"}
        _exact(row, common | extras)
        _require((row["context_id"], row["variable"], row["statistic"], row["unit"]) ==
                 (context, variable, statistic, unit), "Context/variable/statistic/unit mismatch")
        _require(type(row["locator"]) is str and bool(row["locator"].strip()), "Locator required")
        if group is None:
            _require(_finite(row["value"]) and row["value"] > 0, "Finite positive moment required")
        else:
            _require(row["group"] == group, "Source group label mismatch")
            numerator, denominator = row["numerator"], row["denominator"]
            _require(type(numerator) is int and type(denominator) is int and
                     0 <= numerator <= denominator <= 2**53 and denominator > 0,
                     "Exact nonnegative integer counts and positive denominator required")
            if context == AYELE_CONTEXT:
                _require(_finite(row["reported_percentage"]) and 0 <= row["reported_percentage"] <= 100,
                         "Original printed percentage metadata required")
        by_id[item_id] = copy.deepcopy(row)
    _require(set(by_id) == set(_SPECS), "Selected evidence set differs")
    groups = (
        ("ayele_sex_male", "ayele_sex_female"),
        ("ayele_age_25_34", "ayele_age_35_44", "ayele_age_45_54", "ayele_age_55_64"),
        ("ayele_bmi_underweight", "ayele_bmi_normal", "ayele_bmi_overweight"),
    )
    denominator = by_id["ayele_sex_female"]["denominator"]
    for ids in groups:
        _require(all(by_id[item]["denominator"] == denominator for item in ids),
                 "Ayele group denominators must agree")
        _require(sum(by_id[item]["numerator"] for item in ids) == denominator,
                 "Ayele category counts must exhaust their declared denominator")
    return by_id


def _beta_parameters(mean: float, sd: float, low: float, high: float) -> dict[str, float]:
    _require(low < mean < high and sd > 0, "Age moments outside declared source support")
    m, v = (mean-low)/(high-low), (sd/(high-low))**2
    _require(math.isfinite(v) and 0 < v < m*(1-m), "Infeasible bounded age variance")
    k = m*(1-m)/v - 1
    result = {"low": low, "high": high, "alpha": m*k, "beta": (1-m)*k}
    _require(all(math.isfinite(v) for v in result.values()) and result["alpha"] > 0 and result["beta"] > 0,
             "Invalid beta parameters")
    return result


def _lognormal_parameters(mean: float, sd: float) -> dict[str, float]:
    variance_log = math.log1p((sd/mean)**2)
    result = {"mu": math.log(mean)-variance_log/2, "sigma": math.sqrt(variance_log)}
    _require(all(math.isfinite(v) for v in result.values()) and result["sigma"] > 0,
             "Invalid lognormal parameters")
    return result


def fit_reference(normalized_source_constraints: list[dict[str, Any]]) -> dict[str, Any]:
    """Analytically derive the fixed reference from18 caller-normalized records.

    Count ratios are formed here from their integer operands. Printed percentages
    are retained but not fitted. No actual packet is read or authenticated.
    """
    rows = _validate_inputs(normalized_source_constraints)
    value = lambda item: float(rows[item]["value"])
    ratio = lambda item: rows[item]["numerator"] / rows[item]["denominator"]
    parameters = _conventions()
    parameters["contexts"] = []
    for context, prefix, female_id in (
        (MIND_CONTEXT, "MIND_K01", "MIND_K01_female_proportion"),
        (AYELE_CONTEXT, "ayele", "ayele_sex_female"),
    ):
        female = ratio(female_id)
        _require(0 < female < 1, "Both sex categories require positive source probability")
        age = _beta_parameters(value(prefix+"_age_mean"), value(prefix+"_age_sd"), *_BOUNDS[context])
        if context == MIND_CONTEXT:
            bmi = _lognormal_parameters(value("MIND_K01_bmi_mean"), value("MIND_K01_bmi_sd"))
        else:
            p_lower, p_upper = ratio("ayele_bmi_underweight"), ratio("ayele_bmi_overweight")
            _require(0 < p_lower < 1-p_upper < 1, "BMI outer category probabilities invalid")
            z_lower, z_upper = NormalDist().inv_cdf(p_lower), NormalDist().inv_cdf(1-p_upper)
            sigma = (math.log(25)-math.log(18.5))/(z_upper-z_lower)
            bmi = {"mu": math.log(18.5)-sigma*z_lower, "sigma": sigma}
            _require(all(math.isfinite(v) for v in bmi.values()) and sigma > 0, "BMI inversion failed")
        parameters["contexts"].append({"context_id": context, "age": age, "female_probability": female, "bmi": bmi})
    parameters["glucose"] = _lognormal_parameters(
        value("MIND_K01_serum_glucose_fsg_mean"), value("MIND_K01_serum_glucose_fsg_sd"))
    normalized = [rows[item] for item in EVIDENCE_IDS]
    return {
        "parameters": parameters,
        "provenance": {
            "normalized_constraints": normalized,
            "normalized_constraints_sha256": _digest(normalized),
            "parameters_sha256": _digest(parameters),
            "source_authenticity": "Caller supplied; not verified by pure component",
            "source_sd_divisor": "Unknown; individual SD used as population-moment approximation",
            "formulas": {"age": "Affine beta moment inversion", "mind_bmi_glucose": "Lognormal arithmetic mean/SD inversion",
                         "ayele_bmi": "Normal inverse-CDF inversion of exact lower and upper count ratios",
                         "sex": "Exact female numerator/denominator"},
            "unfitted_ids": ["ayele_age_25_34", "ayele_age_35_44", "ayele_age_45_54", "ayele_age_55_64", "ayele_bmi_normal"],
            "optimizer_calls": 0, "sampled_rows": 0, "clinical_execution_authorized": False,
        },
        "model_assumptions": {
            "independence": "Explicit within-donor completion, not reported zero relationships",
            "glucose_transport": "Copy MIND serum marginal to Ayele and target; unsupported assay/feeding/population transport",
            "target_mixture": "Equal donor weights after donor-specific age>=40 conditioning, not filtering the original pooled mixture",
            "target_age_support": "Model upper support80 is not an upper target eligibility bound",
            "population_contrasts": "Zero by independent identical glucose law; no desired target coefficients or finite-cohort enforcement",
            "selection_and_imputation": "Original selection, weighting, timing and imputation not reconstructed",
            "age_bins": "Completed-year half-open approximation explicit; source support/caption discrepancy retained",
        },
    }


def _validate_parameters(parameters: Any) -> None:
    fixed = _conventions()
    _exact(parameters, {*fixed, "contexts", "glucose"})
    for key, expected in fixed.items():
        _require(_digest(parameters[key]) == _digest(expected), "Fixed reference convention changed: "+key)
    contexts = parameters["contexts"]
    _require(type(contexts) is list and len(contexts) == 2, "Exactly two source contexts required")
    for context, expected in zip(contexts, SOURCE_CONTEXTS, strict=True):
        _exact(context, {"context_id", "age", "female_probability", "bmi"})
        _require(context["context_id"] == expected, "Source context identity/order changed")
        _exact(context["age"], {"low", "high", "alpha", "beta"})
        age = context["age"]
        _require(all(_finite(x) for x in age.values()) and (age["low"], age["high"]) == _BOUNDS[expected]
                 and age["alpha"] > 0 and age["beta"] > 0, "Invalid age parameters/bounds")
        _require(_finite(context["female_probability"]) and 0 < context["female_probability"] < 1,
                 "Invalid sex probability")
    for distribution in [parameters["glucose"], *(c["bmi"] for c in contexts)]:
        _exact(distribution, {"mu", "sigma"})
        _require(all(_finite(x) for x in distribution.values()) and distribution["sigma"] > 0,
                 "Invalid positive lognormal parameters")


def _draw_age(age: dict[str, float], uniforms: np.ndarray, minimum: float | None) -> np.ndarray:
    low, high, alpha, beta = (age[k] for k in ("low", "high", "alpha", "beta"))
    q = 0.0
    if minimum is not None and minimum > low:
        _require(minimum < high, "No age mass satisfies context eligibility")
        q = float(betainc(alpha, beta, (minimum-low)/(high-low)))
    _require(math.isfinite(q) and 0 <= q < 1, "Conditional age CDF invalid or no retained mass")
    probabilities = q + (1-q)*uniforms
    _require(bool(np.isfinite(probabilities).all()) and bool(((0 <= probabilities) & (probabilities <= 1)).all()),
             "Age quantile probabilities invalid")
    result = low + (high-low)*betaincinv(alpha, beta, probabilities)
    _require(bool(np.isfinite(result).all()) and bool(((result >= low) & (result <= high)).all()),
             "Age inverse CDF failed")
    if minimum is not None:
        _require(bool((result >= minimum).all()), "Age draw violates target eligibility")
    return result


def sample(parameters: dict[str, Any], context_id: str, n_rows: int, seed: int) -> pd.DataFrame:
    """Return one exact-size table; caller owns task, freeze, context guard and ledger.

    A clinical runner must pass5000 rows. Smaller sizes exist for invented fixtures;
    this function does not authorize a clinical context by accepting its name.
    """
    _validate_parameters(parameters)
    _require(type(context_id) is str and context_id in (*SOURCE_CONTEXTS, TARGET_CONTEXT), "Unknown context ID")
    _require(type(n_rows) is int and 1 <= n_rows <= MAX_ROWS, "Row count must be integer1..5000")
    _require(type(seed) is int and 0 <= seed < 2**64, "Seed must be an unsigned64-bit integer")
    rng = np.random.default_rng(seed)
    is_target = context_id == TARGET_CONTEXT
    donor = rng.integers(0, 2, n_rows) if is_target else np.full(n_rows, SOURCE_CONTEXTS.index(context_id))
    age_uniforms, sex_uniforms = rng.random(n_rows), rng.random(n_rows)
    bmi_noise, glucose_noise = rng.standard_normal(n_rows), rng.standard_normal(n_rows)
    ages, bmi = np.empty(n_rows), np.empty(n_rows)
    sexes = np.empty(n_rows, dtype="<U1")
    with np.errstate(over="raise", invalid="raise", under="raise", divide="raise"):
        for index, context in enumerate(parameters["contexts"]):
            selected = donor == index
            ages[selected] = _draw_age(context["age"], age_uniforms[selected], 40.0 if is_target else None)
            sexes[selected] = np.where(sex_uniforms[selected] < context["female_probability"], "F", "M")
            bmi[selected] = np.exp(context["bmi"]["mu"] + context["bmi"]["sigma"]*bmi_noise[selected])
        glucose = np.exp(parameters["glucose"]["mu"] + parameters["glucose"]["sigma"]*glucose_noise)
    _require(bool(np.isfinite(np.column_stack((ages, bmi, glucose))).all()) and
             bool((bmi > 0).all()) and bool((glucose > 0).all()), "Nonfinite or nonpositive output")
    return pd.DataFrame({
        "id": [f"{context_id}:{seed}:{row+1}" for row in range(n_rows)],
        "age": ages, "sex": sexes, "bmi": bmi, "glucose": glucose,
    }, columns=COLUMNS)


# Mechanical S01 entrypoint: exact reviewed reference source precedes this wrapper.
def generate(observed, specification, seed):
    if observed is not None:
        raise ValueError("S01 requires whole-cohort mode")
    scientific = specification["parameters"]
    active = scientific["active_context"]
    fitted = fit_reference(scientific["normalized_source_constraints"])
    return sample(fitted["parameters"], active, scientific["contexts"][active]["n_rows"], seed)
