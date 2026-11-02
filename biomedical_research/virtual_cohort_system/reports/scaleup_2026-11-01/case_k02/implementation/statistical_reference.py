"""Pure S01 analytic completion and bounded sampling; no I/O or lifecycle calls.

No source file is read, no evidence is admitted and no scientific execution is
authorized here. Callers must bind inputs/code/model to the reviewed lifecycle.
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


CONTEXT_IDS = (
    "malawi_rural_men", "malawi_urban_men", "uganda_men",
    "malawi_rural_women", "malawi_urban_women", "uganda_women",
)
COLUMNS = ("id", "age", "sex", "bmi", "total_cholesterol", "hdl_cholesterol")
TARGET_CONTEXT_ID = "target_turkana_adults"
MAX_ROWS = 5000
_GM_FIELDS = {
    "bmi_geometric_mean": ("bmi", "kg/m^2"),
    "hdl_geometric_mean": ("hdl_cholesterol", "mmol/L"),
    "non_hdl_geometric_mean": ("non_hdl_cholesterol", "mmol/L"),
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _exact(value: Any, keys: set[str]) -> None:
    _require(type(value) is dict and set(value) == keys, "Unexpected/missing fields")


def _text(value: Any) -> None:
    _require(type(value) is str and bool(value.strip()), "Nonempty string required")


def _finite(value: Any) -> bool:
    if type(value) not in {int, float}:
        return False
    try:
        return math.isfinite(float(value))
    except (ValueError, OverflowError):
        return False


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _conventions() -> dict[str, Any]:
    # Return new objects so neither callers nor returned models mutate defaults.
    return {
        "schema_version": 1,
        "kind": "k02_s01_positive_sum_completion_v1",
        "target_context_id": TARGET_CONTEXT_ID,
        "units": {"id": "1", "age": "year", "sex": "1", "bmi": "kg/m^2",
                  "total_cholesterol": "mmol/L", "hdl_cholesterol": "mmol/L"},
        "age": {"distribution": "uniform", "low": 18.0, "high": 80.0},
        "target_mixture": "equal_probability_over_six_ordered_source_contexts",
        "conditional_noise": "independent_standard_normals_for_bmi_hdl_non_hdl",
        "log_dispersion": "common_hdl_derived_sigma_within_context",
        "lipid_identity": "total_cholesterol=hdl_cholesterol+positive_internal_non_hdl",
        "source_sex_encoding": "men_to_M_women_to_F_internal_convention_only",
    }


def _validate_constraints(rows: Any) -> list[dict[str, Any]]:
    _require(type(rows) is list and len(rows) == 6, "Exactly six normalized source contexts required")
    by_id: dict[str, dict[str, Any]] = {}
    evidence_ids: set[str] = set()
    for row in rows:
        _exact(row, {"context_id", *_GM_FIELDS, "low_hdl_proportion"})
        context = row["context_id"]
        _require(type(context) is str and context in CONTEXT_IDS and context not in by_id,
                 "Unknown/duplicate source context ID")
        for field, (variable, unit) in _GM_FIELDS.items():
            item = row[field]
            _exact(item, {"evidence_id", "locator", "variable", "statistic", "unit", "value"})
            _text(item["locator"])
            _require(item["evidence_id"] == f"{context}__{variable}__geometric_mean",
                     "Geometric-mean evidence ID does not match context/analyte")
            _require(item["variable"] == variable and item["statistic"] == "geometric_mean" and item["unit"] == unit,
                     "Geometric-mean analyte/statistic/unit mismatch")
            _require(_finite(item["value"]) and item["value"] > 0, "Finite positive geometric mean required")
            _require(item["evidence_id"] not in evidence_ids, "Duplicate evidence ID")
            evidence_ids.add(item["evidence_id"])
        item = row["low_hdl_proportion"]
        _exact(item, {"evidence_id", "locator", "variable", "statistic", "unit", "value", "comparison", "threshold", "threshold_unit"})
        _text(item["locator"])
        _require(item["evidence_id"] == f"{context}__hdl_cholesterol__low_prevalence",
                 "Low-HDL evidence ID does not match context/analyte")
        _require(item["variable"] == "hdl_cholesterol" and item["statistic"] == "proportion" and item["unit"] == "1",
                 "Explicit HDL probability in unit 1 required; percentages are not silently converted")
        _require(item["comparison"] == "lt" and item["threshold_unit"] == "mmol/L",
                 "Strict less-than threshold in mmol/L required")
        _require(_finite(item["threshold"]) and item["threshold"] > 0, "Finite positive threshold required")
        _require(_finite(item["value"]) and 0 < item["value"] < 1 and item["value"] != 0.5,
                 "Probability must lie strictly between 0 and 1 and differ from one half")
        _require(item["evidence_id"] not in evidence_ids, "Duplicate evidence ID")
        evidence_ids.add(item["evidence_id"])
        by_id[context] = row
    _require(set(by_id) == set(CONTEXT_IDS), "Source context set differs")
    return [copy.deepcopy(by_id[context]) for context in CONTEXT_IDS]


def fit_reference(six_normalized_source_constraints: list[dict[str, Any]]) -> dict[str, Any]:
    """Derive S01 parameters analytically, without sampling or optimization.

    Input proportions are already fractions in unit 1. A separate, reviewed
    normalization must retain the original percentage/locator and its /100
    derivation. This function does not parse or admit any source packet.
    """
    rows = _validate_constraints(six_normalized_source_constraints)
    parameters = _conventions()
    parameters["contexts"] = []
    derivations = []
    for row in rows:
        context = row["context_id"]
        mu_bmi = math.log(row["bmi_geometric_mean"]["value"])
        mu_hdl = math.log(row["hdl_geometric_mean"]["value"])
        mu_non_hdl = math.log(row["non_hdl_geometric_mean"]["value"])
        prevalence = row["low_hdl_proportion"]
        sigma = (math.log(prevalence["threshold"]) - mu_hdl) / NormalDist().inv_cdf(prevalence["value"])
        _require(math.isfinite(sigma) and sigma > 0, "HDL pair does not imply finite positive lognormal dispersion")
        parameters["contexts"].append({
            "context_id": context, "encoded_sex": "M" if context.endswith("_men") else "F",
            "mu_bmi": mu_bmi, "mu_hdl": mu_hdl, "mu_non_hdl": mu_non_hdl, "sigma": sigma,
        })
        derivations.append({
            "context_id": context,
            "mu_bmi_evidence_ids": [row["bmi_geometric_mean"]["evidence_id"]],
            "mu_hdl_evidence_ids": [row["hdl_geometric_mean"]["evidence_id"]],
            "mu_non_hdl_evidence_ids": [row["non_hdl_geometric_mean"]["evidence_id"]],
            "sigma_evidence_ids": [row["hdl_geometric_mean"]["evidence_id"], prevalence["evidence_id"]],
            "location_formula": "log(reported_geometric_mean)",
            "dispersion_formula": "(log(strict_threshold)-mu_hdl)/Phi_inverse(probability)",
        })
    return {
        "parameters": parameters,
        "provenance": {
            "normalized_constraints_sha256": _digest(rows), "parameters_sha256": _digest(parameters),
            "normalized_constraints": rows, "derivations": derivations,
            "analytic_log_evaluations": 24, "inverse_normal_cdf_evaluations": 6,
            "optimizer_calls": 0, "sampled_rows": 0,
            "source_authenticity": "caller_supplied_not_verified",
            "case_release_authorized": False,
        },
        "model_assumptions": {
            "positive_lognormal_marginals": "Assumed unweighted source-stratum law, not an authenticated source estimator",
            "conditional_independence": "BMI, HDL and internal non-HDL independent within stratum; not observed zero associations",
            "common_log_dispersion": "Unidentified BMI and non-HDL log dispersions arbitrarily equal HDL-derived sigma",
            "age": "Uniform(18,80), independent of stratum and measurements; age quantiles unused; no target upper-age exclusion",
            "target_mixture": "Equal donor-stratum probabilities, unsupported by target composition or source counts",
            "sex_encoding": "Source men=M and women=F is internal encoding, not a verified biological target-code legend",
            "positive_sum": "TC=HDL+positive internal non-HDL; cannot represent measured TC<HDL and must not exclude such target records",
            "unfitted": "TC geometric means are diagnostics; source age quantiles and raw/log-ambiguous regressions are contextual only",
            "feedback_decision": "Precommitted retention; no Monte Carlo recalibration or alternate family selection",
        },
    }


def _validate_parameters(parameters: Any) -> None:
    fixed = _conventions()
    _exact(parameters, {*fixed, "contexts"})
    for key, value in fixed.items():
        _require(_canonical(parameters[key]) == _canonical(value), "Fixed reference convention changed: " + key)
    contexts = parameters["contexts"]
    _require(type(contexts) is list and len(contexts) == 6, "Exactly six parameter contexts required")
    for expected, row in zip(CONTEXT_IDS, contexts):
        _exact(row, {"context_id", "encoded_sex", "mu_bmi", "mu_hdl", "mu_non_hdl", "sigma"})
        _require(row["context_id"] == expected, "Parameter context identity/order changed")
        _require(row["encoded_sex"] == ("M" if expected.endswith("_men") else "F"), "Internal sex encoding changed")
        _require(all(_finite(row[key]) for key in ("mu_bmi", "mu_hdl", "mu_non_hdl", "sigma")), "Finite numeric parameters required")
        _require(row["sigma"] > 0, "Positive log dispersion required")


def sample(parameters: dict[str, Any], context_id: str, n_rows: int, seed: int) -> pd.DataFrame:
    """Draw one requested frame, without recalibration, retries, filtering or I/O.

    Production callers must bind the frozen 5,000-row task and scheduled seed.
    Smaller n_rows are supported for invented software fixtures. This pure call
    neither verifies nor debits a lifecycle/campaign execution allowance.
    """
    _validate_parameters(parameters)
    _require(type(context_id) is str and context_id in (*CONTEXT_IDS, TARGET_CONTEXT_ID), "Unknown sample context")
    _require(type(n_rows) is int and 1 <= n_rows <= MAX_ROWS, "Row count must be an integer from 1 to 5000")
    _require(type(seed) is int and 0 <= seed <= 2**32 - 1, "Seed must be a nonboolean unsigned 32-bit integer")
    rng = np.random.default_rng(seed)
    groups = rng.integers(0, 6, size=n_rows) if context_id == TARGET_CONTEXT_ID else np.full(n_rows, CONTEXT_IDS.index(context_id))
    contexts = parameters["contexts"]
    mu = np.array([[c["mu_bmi"], c["mu_hdl"], c["mu_non_hdl"]] for c in contexts], dtype=float)[groups]
    sigma = np.array([c["sigma"] for c in contexts], dtype=float)[groups, None]
    noise = rng.standard_normal((n_rows, 3))
    age = rng.uniform(18.0, 80.0, size=n_rows)
    with np.errstate(over="ignore", under="ignore", invalid="ignore"):
        positive = np.exp(mu + sigma * noise)
        bmi, hdl, non_hdl = positive.T
        total = hdl + non_hdl
    _require(np.isfinite(positive).all() and (positive > 0).all() and np.isfinite(total).all(),
             "Nonfinite/nonpositive sampled value; no clipping, repair or redraw")
    _require((total > hdl).all(), "Floating-point sum lost the positive non-HDL component; no repair or redraw")
    _require(np.isfinite(age).all() and (age >= 18).all() and (age < 80).all(), "Invalid sampled age")
    return pd.DataFrame({
        "id": pd.Series([f"S01-{context_id}-{seed}-{i}" for i in range(n_rows)], dtype="string"),
        "age": age,
        "sex": pd.Series([contexts[int(group)]["encoded_sex"] for group in groups], dtype="string"),
        "bmi": bmi, "total_cholesterol": total, "hdl_cholesterol": hdl,
    }, columns=list(COLUMNS))
