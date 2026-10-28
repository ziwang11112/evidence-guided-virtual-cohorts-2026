"""Blinded, evidence-guided virtual fasting-insulin feature enrichment.

This is a conditional simulation model, not a fitted prediction model. Read the
model specification and INITIAL_DECISION.md before interpreting its outputs.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def generate(observed: pd.DataFrame, evidence: dict, seed: int) -> pd.DataFrame:
    """Return row_id,bmi,age,sex,insulin in the input order without mutation.

    All biological and distributional parameters are supplied in ``evidence``.
    There are no file/network reads or writes and no global random-state changes.
    The input is the task's adult observed-covariate packet; units are kg/m^2,
    years, sex code 1/2, and output insulin in microIU/mL (uU/mL).
    """
    columns = ["row_id", "bmi", "age", "sex"]
    if list(observed.columns) != columns:
        raise ValueError("Expected exactly row_id,bmi,age,sex in that order")
    if observed[columns].isna().any().any():
        raise ValueError("Missing observed values are outside the input contract")
    if not observed["row_id"].is_unique:
        raise ValueError("row_id must be unique")

    bmi = observed["bmi"].to_numpy(dtype=float)
    age = observed["age"].to_numpy(dtype=float)
    sex = observed["sex"].to_numpy(dtype=float)
    if not (np.isfinite(bmi).all() and np.isfinite(age).all()):
        raise ValueError("BMI and age must be finite")
    if (bmi <= 0).any() or not np.isin(sex, [1, 2]).all():
        raise ValueError("BMI must be positive and sex coded 1 or 2")

    p = evidence["parameters"]
    if (age < p["supported_age_min"]).any() or (age > p["supported_age_max"]).any():
        raise ValueError("Age is outside the specified adult population")
    nodes = np.asarray(p["age_nodes_years"], dtype=float)
    anchor_insulin = np.asarray(p["age_anchor_median_insulin"], dtype=float)
    anchor_bmi = np.asarray(p["age_anchor_bmi"], dtype=float)
    if not (nodes.ndim == 1 and len(nodes) == len(anchor_insulin) == len(anchor_bmi)):
        raise ValueError("Incompatible age-anchor arrays")
    if not (np.diff(nodes) > 0).all() or not (anchor_insulin > 0).all():
        raise ValueError("Age anchors must increase and insulin anchors be positive")
    sigma = float(p["residual_log_sd"])
    if not np.isfinite(sigma) or sigma <= 0:
        raise ValueError("Conditional log SD must be finite and positive")

    # A1/A2: smooth log-median and reference-BMI interpolation; flat end segments.
    log_anchor = np.interp(age, nodes, np.log(anchor_insulin))
    bmi_reference = np.interp(age, nodes, anchor_bmi)
    # A3: group mean ratio is used as a log-median BMI slope, not claimed fitted.
    log_median = log_anchor + p["bmi_log_slope"] * (bmi - bmi_reference)
    # A4: zero sex coefficient is an explicit modeling choice.
    log_median = log_median + p["female_log_effect"] * (sex == 2)

    rng = np.random.default_rng(seed)
    insulin = np.exp(log_median + rng.normal(0.0, sigma, size=len(observed)))
    if not (np.isfinite(insulin).all() and (insulin > 0).all()):
        raise ValueError("Numerical overflow/underflow outside practical model support")

    result = observed.loc[:, columns].copy(deep=True)
    result["insulin"] = insulin
    return result
