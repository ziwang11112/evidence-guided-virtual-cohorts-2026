"""Frozen-law sampler; NumPy/Pandas only, no fitting or sample calibration."""
from __future__ import annotations

import math
import numpy as np
import pandas as pd


def normal_cdf(x):
    x = np.asarray(x, dtype=float)
    return np.fromiter((0.5 * math.erfc(-float(v) / math.sqrt(2.0))
                        for v in x.flat), dtype=float, count=x.size).reshape(x.shape)


def quantile(margin, u):
    u = np.asarray(u, dtype=float)
    if margin["kind"] == "integer":
        ix = np.searchsorted(np.asarray(margin["cdf"]), u, side="left")
        return np.asarray(margin["values"], dtype=int)[np.minimum(ix, len(margin["values"]) - 1)]
    return np.interp(u, np.asarray(margin["cdf"]), np.asarray(margin["edges"]))


def generate_rows(parameters, n, seed, row_ids=None):
    """One iid draw of n rows from the supplied immutable parameter law."""
    if n < 1 or int(n) != n:
        raise ValueError("n must be a positive integer")
    rng = np.random.default_rng(seed)
    dep = parameters["dependence"]
    tail = rng.random(n) < dep["tail_probability"]
    x, y, ea, eb = rng.standard_normal((4, n))
    rho = np.where(tail, dep["rho_tail"], dep["rho_body"])
    common = np.sqrt((1.0 + rho) / 2.0)
    difference = np.sqrt((1.0 - rho) / 2.0)
    zg, zh = common * x + difference * y, common * x - difference * y
    tau = dep["tail_probability"]
    start, span = np.where(tail, 1.0 - tau, 0.0), np.where(tail, tau, 1.0 - tau)
    ug, uh = start + span * normal_cdf(zg), start + span * normal_cdf(zh)
    ax, ay, bx = dep["age_common"], dep["age_difference"], dep["bmi_common"]
    za = ax * x + ay * y + math.sqrt(max(0.0, 1.0 - ax * ax - ay * ay)) * ea
    zb = bx * x + math.sqrt(max(0.0, 1.0 - bx * bx)) * eb
    margins = parameters["margins"]
    if row_ids is None:
        row_ids = [f"row_{i + 1:06d}" for i in range(n)]
    if len(row_ids) != n:
        raise ValueError("row_ids length differs from n")
    return pd.DataFrame({
        "row_id": list(row_ids),
        "age": quantile(margins["age"], normal_cdf(za)),
        "female": (rng.random(n) < parameters["female_probability"]).astype(int),
        "bmi": quantile(margins["bmi"], normal_cdf(zb)),
        "glucose": quantile(margins["glucose"], ug),
        "hba1c": quantile(margins["hba1c"], uh),
    })


def generate(observed, spec, seed):
    """Harness ABI: None for whole cohort, or row_id-only input identifiers."""
    parameters = spec.get("parameters", spec)
    if observed is None:
        return generate_rows(parameters, int(parameters.get("n_rows", 3000)), seed)
    if isinstance(observed, pd.DataFrame):
        if list(observed.columns) != ["row_id"]:
            raise ValueError("whole-cohort input must contain only row_id")
        return generate_rows(parameters, len(observed), seed, observed["row_id"].tolist())
    raise TypeError("observed must be None or a row_id-only pandas DataFrame")
