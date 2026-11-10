"""Fixed BP analyses; generated adapter has no clinical reference dependency.

Weights define a finite descriptive distribution. Neither row resampling nor
ordinary regression SEs establish design-based national survey inference.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd

ANALYSES = ["bmi_sbp", "bmi_dbp", "residual_correlation"]
COLUMNS = ["age", "female", "bmi", "sbp", "dbp"]

def summarize(frame, weights=None):
    """Analyze supplied complete rows without silently filtering bad values."""
    z = frame[COLUMNS].to_numpy(dtype=float)
    n = len(z)
    w = np.ones(n) if weights is None else np.asarray(weights, dtype=float)
    if w.shape != (n,) or n == 0:
        raise ValueError("Nonempty rows and one weight per row required")
    if not np.isfinite(z).all() or not np.isfinite(w).all() or np.any(w <= 0):
        raise ValueError("Analysis requires finite complete rows and positive finite weights")
    if not np.isin(z[:, 1], [0, 1]).all():
        raise ValueError("female must be 0 or 1")
    w = w / w.sum()
    mean = w @ z
    var = w @ ((z - mean) ** 2)
    X = np.column_stack((np.ones(n), (z[:, 0]-50)/10, z[:, 1], (z[:, 2]-25)/5))
    sw = np.sqrt(w)
    rank = int(np.linalg.matrix_rank(X * sw[:, None]))
    out = {"status": "estimable" if rank == 4 else "rank_deficient", "n": n,
           "n_eff": float(1 / np.sum(w*w)), "rank": rank,
           "estimates": dict.fromkeys(ANALYSES),
           "diagnostics": {"margins": {k: {"mean": float(mean[i]), "sd": float(np.sqrt(var[i]))}
                                      for i,k in enumerate(COLUMNS)},
                           "sbp_below_dbp_fraction": float(w @ (z[:,3] < z[:,4])),
                           "residual_sd": {"sbp": None, "dbp": None},
                           "raw_sbp_dbp_correlation": None},
           "coefficients": None}
    denom = np.sqrt(var[3]*var[4])
    if denom > 0:
        out["diagnostics"]["raw_sbp_dbp_correlation"] = float((w * (z[:,3]-mean[3])) @ (z[:,4]-mean[4]) / denom)
    if rank < 4:
        return out
    beta = np.linalg.lstsq(X*sw[:,None], z[:,3:5]*sw[:,None], rcond=None)[0]
    residual = z[:,3:5] - X@beta
    # Explicit centering also guards numerical residual mean error.
    residual -= w @ residual
    rvar = w @ (residual**2)
    out["coefficients"] = {k: dict(zip(["intercept", "age_per10", "female", "bmi_per5"], map(float,beta[:,j])))
                           for j,k in enumerate(["sbp", "dbp"])}
    out["estimates"]["bmi_sbp"] = float(beta[3,0])
    out["estimates"]["bmi_dbp"] = float(beta[3,1])
    out["diagnostics"]["residual_sd"] = dict(zip(["sbp","dbp"], map(float,np.sqrt(rvar))))
    # A numerically deterministic endpoint has no meaningful residual correlation.
    threshold = np.finfo(float).eps * max(float(var[3]), float(var[4]), 1.0) * 100
    if min(rvar) <= threshold:
        out["status"] = "residual_correlation_undefined"
    else:
        out["estimates"]["residual_correlation"] = float(np.clip((w*residual[:,0])@residual[:,1] / np.sqrt(rvar[0]*rvar[1]), -1, 1))
    return out

def analyze(output_path, task_path, request_path):
    """adaptive_session_v2 generated-only adapter; exact input/output checks."""
    task = json.loads(Path(task_path).read_text(encoding="utf-8"))
    request = json.loads(Path(request_path).read_text(encoding="utf-8"))
    if (request.get("schema_version") != 1 or request.get("analyses") != ANALYSES
        or request.get("task") != task or not request.get("purpose")
        or set(request) != {"schema_version", "task", "purpose", "analyses"}):
        raise ValueError("Unexpected analysis request")
    if task["mode"] != "whole_cohort":
        raise ValueError("Whole-cohort task required")
    df = pd.read_csv(output_path)
    if len(df) != task["n_rows"]:
        raise ValueError("Wrong row count")
    return summarize(df)

def row_resampling_stability(frame, weights, repeats=500, seed=73991):
    """IID row resampling with supplied weights retained, NOT survey confidence."""
    rng = np.random.default_rng(seed)
    n = len(frame)
    w = np.asarray(weights, float)
    values = {k: [] for k in ANALYSES}
    failures = 0
    for _ in range(repeats):
        idx = rng.integers(0, n, size=n)
        s = summarize(frame.iloc[idx], w[idx])
        if s["status"] != "estimable":
            failures += 1
        for k,v in s["estimates"].items():
            if v is not None:
                values[k].append(v)
    return {"interpretation":"conditional IID row-resampling stability; not design-based or national-population confidence",
            "seed":seed,"repeats":repeats,"nonestimable_replicates":failures,
            "intervals": {k:{"low":float(np.quantile(v,.025)) if v else None,
                             "high":float(np.quantile(v,.975)) if v else None,
                             "estimable_replicates":len(v)} for k,v in values.items()}}
