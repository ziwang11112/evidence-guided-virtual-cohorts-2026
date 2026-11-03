"""Deterministic supplied-summary baseline. Importing never fits or draws rows.

All expectations concern the generator.py law. Gaussian quadrature coordinates
are integration abscissae, not a generated cohort. No target individual records
are accepted. Call fit(summary) only after independent pre-fit release.
"""
from __future__ import annotations

import copy
import math
import time
import numpy as np
from scipy.optimize import least_squares
from scipy.special import logsumexp, ndtr, ndtri, roots_hermitenorm

FAMILY = "bounded_maximum_entropy_tail_patchwork_v1"
CELLS_PER_BIN = 256
UNIFORM_RESERVE = 1e-10
FIT_ORDER = 128
CHECK_ORDERS = (256, 512)
FIT_LIMIT_SECONDS = 900
TAIL_RHO = 0.8
VARIABLES = ("age", "female", "bmi", "glucose", "hba1c")
STATS = ("mean", "sd", "q10", "median", "q90")
GLY_STARTS = ((0.03, 0.25), (0.08, 0.10), (0.15, -0.10))
COV_STARTS = ((0.25, 0.0, 0.25), (0.5, 0.25, 0.5), (0.0, -0.3, 0.6))


def _quantile(margin, u):
    if margin["kind"] == "integer":
        ix = np.searchsorted(margin["cdf"], u, side="left")
        return np.asarray(margin["values"])[np.minimum(ix, len(margin["values"]) - 1)]
    return np.interp(u, margin["cdf"], margin["edges"])


def _stats(margin):
    p = np.asarray(margin["probabilities"])
    if margin["kind"] == "integer":
        x = np.asarray(margin["values"])
        m1, m2 = np.dot(p, x), np.dot(p, x * x)
    else:
        e = np.asarray(margin["edges"])
        a, b = e[:-1], e[1:]
        m1 = np.dot(p, (a + b) / 2.0)
        m2 = np.dot(p, (a * a + a * b + b * b) / 3.0)
    return dict(zip(STATS, [float(m1), float(math.sqrt(max(0.0, m2 - m1 * m1))),
                            *map(float, _quantile(margin, [0.1, 0.5, 0.9]))]))


def _fit_age(target):
    calls = {"objective_calls": 0, "jacobian_calls": 0, "probability_evaluations": 0}
    x = np.arange(35.0, 75.0)
    z = (x - 54.5) / 20.0
    qs = np.array([target[s] for s in ("q10", "median", "q90")])
    if np.any(qs != np.round(qs)) or not (35 <= qs[0] < qs[1] < qs[2] <= 74):
        raise ValueError("age quantiles must be ordered integers in 35..74")
    features = np.column_stack([z, z * z, *[(x < q) + 0.5 * (x == q) for q in qs]])
    desired = np.array([(target["mean"] - 54.5) / 20,
                        (target["sd"] ** 2 + (target["mean"] - 54.5) ** 2) / 400,
                        0.1, 0.5, 0.9])
    def probs(t):
        calls["probability_evaluations"] += 1
        a = features @ t
        return np.exp(a - logsumexp(a))
    def fun(t):
        calls["objective_calls"] += 1
        return probs(t) @ features - desired
    def jac(t):
        calls["jacobian_calls"] += 1
        p = probs(t)
        m = p @ features
        return (features.T * p) @ features - np.outer(m, m)
    result = least_squares(fun, np.zeros(5), jac=jac, max_nfev=300,
                           ftol=1e-12, xtol=1e-12, gtol=1e-12)
    p = probs(result.x)
    cdf = np.cumsum(p)
    cdf[-1] = 1.0
    if np.any(p <= 0) or np.any(np.diff(np.r_[0.0, cdf]) <= 0):
        raise ValueError("age entropy fit produced a numerically unresolved mass")
    margin = {"kind": "integer", "values": x.astype(int).tolist(),
              "probabilities": p.tolist(), "cdf": cdf.tolist(),
              "entropy_coefficients": result.x.tolist()}
    error = float(np.max(np.abs(fun(result.x))))
    return margin, {"success": bool(result.success), "nfev": result.nfev,
                    "max_constraint_error": error, **calls}


def _fit_continuous(target):
    calls = {"objective_calls": 0, "jacobian_calls": 0, "probability_evaluations": 0}
    q10, q50, q90 = (float(target[s]) for s in ("q10", "median", "q90"))
    if not 0 < q10 < q50 < q90 or target["sd"] <= 0:
        raise ValueError("positive ordered continuous quantiles and SD required")
    lower = max(0.01, q10 - 4.0 * (q50 - q10))
    upper = q90 + 10.0 * target["sd"]
    cut = [lower, q10, q50, q90, upper]
    edge = np.concatenate([np.linspace(a, b, CELLS_PER_BIN + 1)[:-1]
                           for a, b in zip(cut[:-1], cut[1:])] + [np.array([upper])])
    a, b = edge[:-1], edge[1:]
    width = b - a
    mean, sd = float(target["mean"]), float(target["sd"])
    f1 = ((a + b) / 2.0 - mean) / sd
    f2 = (((a * a + a * b + b * b) / 3.0)
          - mean * (a + b) + mean * mean) / (sd * sd)
    features = np.column_stack([f1, f2])
    mass = np.array([0.1, 0.4, 0.4, 0.1])
    def probs(t):
        calls["probability_evaluations"] += 1
        logits = (np.log(width) + features @ t).reshape(4, CELLS_PER_BIN)
        tilted = np.exp(logits - logsumexp(logits, axis=1)[:, None])
        return (mass[:, None] * ((1 - UNIFORM_RESERVE) * tilted
                                 + UNIFORM_RESERVE / CELLS_PER_BIN)).ravel()
    def fun(t):
        calls["objective_calls"] += 1
        return probs(t) @ features - np.array([0.0, 1.0])
    def jac(t):
        calls["jacobian_calls"] += 1
        p = probs(t).reshape(4, CELLS_PER_BIN) - mass[:, None] * UNIFORM_RESERVE / CELLS_PER_BIN
        f = features.reshape(4, CELLS_PER_BIN, 2)
        total = np.zeros((2, 2))
        for k in range(4):
            tilted_mass = mass[k] * (1 - UNIFORM_RESERVE)
            m = p[k] @ f[k] / tilted_mass
            total += (f[k].T * p[k]) @ f[k] - tilted_mass * np.outer(m, m)
        return total
    result = least_squares(fun, np.array([0.0, -0.5]), jac=jac, max_nfev=300,
                           ftol=1e-12, xtol=1e-12, gtol=1e-12)
    p = probs(result.x)
    cdf = np.r_[0.0, np.cumsum(p)]
    for i, v in enumerate([0.0, 0.1, 0.5, 0.9, 1.0]):
        cdf[i * CELLS_PER_BIN] = v
    # Remove underflow cells only if their probability is literally zero.
    # Such cells are not expected at valid finite optima; fail rather than alter the law.
    if np.any(p <= 0) or np.any(np.diff(cdf) <= 0):
        raise ValueError("entropy fit produced a numerically unresolved cell")
    margin = {"kind": "piecewise_uniform", "edges": edge.tolist(),
              "probabilities": np.diff(cdf).tolist(), "cdf": cdf.tolist(),
              "entropy_coefficients": result.x.tolist(), "support": [lower, upper],
              "cells_per_quantile_bin": CELLS_PER_BIN, "uniform_reserve": UNIFORM_RESERVE}
    error = float(np.max(np.abs(fun(result.x))))
    return margin, {"success": bool(result.success), "nfev": result.nfev,
                    "max_constraint_error": error, **calls}


class Integrator:
    """Observed-law Gaussian expectations; exact discrete-age conditional mean."""
    def __init__(self, margins, order):
        self.margins = margins
        self.order = order
        self.z, self.w = roots_hermitenorm(order)
        self.w /= math.sqrt(2 * math.pi)
        self.stats = {k: _stats(v) for k, v in margins.items()}
        acdf = np.asarray(margins["age"]["cdf"][:-1])
        self.age_thresholds = ndtri(acdf)
        self._pair_cache = {}
        self.calls = {"continuous_pair_requests": 0, "continuous_pair_integrations": 0,
                      "age_pair_requests": 0, "age_pair_integrations": 0}

    def continuous_mean(self, name, start=0.0, span=1.0):
        return float(self.w @ _quantile(self.margins[name], start + span * ndtr(self.z)))

    def centered_pair(self, first, second, rho, first_regime=(0.0, 1.0),
                      second_regime=(0.0, 1.0)):
        self.calls["continuous_pair_requests"] += 1
        key = (first, second, rho, first_regime, second_regime)
        if key in self._pair_cache:
            return self._pair_cache[key]
        if rho == 0 and ((first_regime == (0.0, 1.0)) or (second_regime == (0.0, 1.0))):
            return 0.0
        self.calls["continuous_pair_integrations"] += 1
        m1, m2 = self.stats[first]["mean"], self.stats[second]["mean"]
        start1, span1 = first_regime
        start2, span2 = second_regime
        z2 = rho * self.z[:, None] + math.sqrt(max(0.0, 1.0 - rho * rho)) * self.z[None, :]
        f1 = _quantile(self.margins[first], start1 + span1 * ndtr(self.z)) - m1
        f2 = _quantile(self.margins[second], start2 + span2 * ndtr(z2)) - m2
        value = float((self.w * f1) @ (f2 @ self.w))
        if len(self._pair_cache) >= 256:
            self._pair_cache.clear()
        self._pair_cache[key] = value
        return value

    def age_continuous(self, second, rho, regime=(0.0, 1.0)):
        self.calls["age_pair_requests"] += 1
        if rho == 0:
            return 0.0
        self.calls["age_pair_integrations"] += 1
        # E[Age | Zsecond=z] = 35 + sum_{k=35}^{73} P(Age>k | z).
        conditional = 35.0 + ndtr((rho * self.z[:, None] - self.age_thresholds[None, :])
                                 / math.sqrt(max(1e-12, 1 - rho * rho))).sum(axis=1)
        start, span = regime
        f = _quantile(self.margins[second], start + span * ndtr(self.z))
        return float(self.w @ ((conditional - self.stats["age"]["mean"])
                               * (f - self.stats[second]["mean"])))


def _decode_cov(x):
    ax = 0.97 * math.tanh(float(x[0]))
    ay = math.sqrt(0.97 ** 2 - ax * ax) * math.tanh(float(x[1]))
    bx = 0.97 * math.tanh(float(x[2]))
    return ax, ay, bx


def law_diagnostics(parameters, order=FIT_ORDER, integrator=None):
    integ = integrator or Integrator(parameters["margins"], order)
    marg = copy.deepcopy(integ.stats)
    p = parameters["female_probability"]
    marg["female"] = {"mean": p, "sd": math.sqrt(p * (1 - p)),
                      "q10": float(0.1 > 1 - p), "median": float(0.5 > 1 - p),
                      "q90": float(0.9 > 1 - p)}
    cov = np.diag([marg[v]["sd"] ** 2 for v in VARIABLES])
    dep = parameters["dependence"]
    tau, rb, rt = dep["tail_probability"], dep["rho_body"], dep["rho_tail"]
    ax, ay, bx = dep["age_common"], dep["age_difference"], dep["bmi_common"]
    cov[0, 2] = integ.age_continuous("bmi", ax * bx)
    for weight, rho, region in ((1 - tau, rb, (0.0, 1 - tau)),
                                 (tau, rt, (1 - tau, tau))):
        c, d = math.sqrt((1 + rho) / 2), math.sqrt((1 - rho) / 2)
        cov[3, 4] += weight * integ.centered_pair("glucose", "hba1c", rho, region, region)
        cov[0, 3] += weight * integ.age_continuous("glucose", ax * c + ay * d, region)
        cov[0, 4] += weight * integ.age_continuous("hba1c", ax * c - ay * d, region)
        cov[2, 3] += weight * integ.centered_pair("bmi", "glucose", bx * c, second_regime=region)
        cov[2, 4] += weight * integ.centered_pair("bmi", "hba1c", bx * c, second_regime=region)
    cov += np.triu(cov, 1).T
    eig = np.linalg.eigvalsh(cov)
    if eig.min() <= 0:
        raise ValueError("numerically nonpositive covariance matrix")
    estimates = {}
    for name, predictors, term in (("E1", [0, 1, 2], 2), ("E2", [0, 1, 3], 3),
                                    ("E3", [1, 2, 3, 0], 0)):
        beta = np.linalg.solve(cov[np.ix_(predictors, predictors)], cov[predictors, 4])
        estimates[name] = float(beta[predictors.index(term)])
    rsb, rst = 6 / math.pi * math.asin(rb / 2), 6 / math.pi * math.asin(rt / 2)
    return {"marginal": marg, "joint": {
                "pearson": float(cov[3, 4] / math.sqrt(cov[3, 3] * cov[4, 4])),
                "spearman": float(3 * tau * (1 - tau) + (1 - tau) ** 3 * rsb + tau ** 3 * rst)},
            "estimands": estimates, "covariance_order": list(VARIABLES),
            "covariance": cov.tolist(), "minimum_covariance_eigenvalue": float(eig.min()),
            "quadrature_order": integ.order, "integration_call_counts": dict(integ.calls)}


def usage_ledger(summary):
    rows = []
    for name in VARIABLES:
        for stat in STATS:
            role = "constraint"
            detail = "Observed-law marginal constraint; sample SD is used as a population plug-in SD."
            if name == "female" and stat != "mean":
                role = "diagnostic"
                detail = "Bernoulli p fixes all other summaries; these redundant summaries are not additional fitted parameters."
            elif name == "age" and stat in ("q10", "median", "q90"):
                detail = "Constraint: midpoint CDF at the supplied integer is its quantile level, guaranteeing that inverse-CDF integer quantile."
            rows.append({"id": f"{name}_{stat}", "target": summary["diagnostics"]["marginal"][name][stat],
                         "role": role, "detail": detail})
    for name in ("pearson", "spearman"):
        rows.append({"id": f"glucose_hba1c_{name}", "target": summary["diagnostics"]["joint"][name],
                     "role": "constraint", "detail": "Two tail-patchwork parameters, with fixed tail Gaussian correlation 0.8."})
    for name in ("E1", "E2", "E3"):
        rows.append({"id": name, "target": summary["estimands"][name]["coefficient"],
                     "role": "constraint", "detail": "Separate observed-law OLS projection with original predictor set; CI and SE do not weight fitting."})
    return rows


def fit(summary):
    """Fit one locked deterministic procedure; no files/network/random rows used.

    Returns parameters even if valid but numerically/calibrationally imperfect.
    generation_allowed is false for invalid margins or integration inconsistency.
    The coordinator must freeze the full returned object before any final draw.
    """
    begun = time.monotonic()
    records = []
    objective_calls = {"glycemia": 0, "covariates": 0}
    def budget():
        if time.monotonic() - begun > FIT_LIMIT_SECONDS:
            raise TimeoutError("declared 900-second clinical fit budget exhausted")
    margins, marginal_status = {}, {}
    targets = summary["diagnostics"]["marginal"]
    margins["age"], marginal_status["age"] = _fit_age(targets["age"])
    for v in ("bmi", "glucose", "hba1c"):
        budget()
        margins[v], marginal_status[v] = _fit_continuous(targets[v])
    parameters = {"family": FAMILY, "n_rows": 3000, "margins": margins,
                  "female_probability": float(targets["female"]["mean"]),
                  "dependence": {"tail_probability": 0.08, "rho_body": 0.1, "rho_tail": TAIL_RHO,
                                 "age_common": 0.0, "age_difference": 0.0, "bmi_common": 0.0}}
    if not 0 < parameters["female_probability"] < 1:
        raise ValueError("female probability must be strictly between zero and one")
    integ = Integrator(margins, FIT_ORDER)
    target_joint = np.array([summary["diagnostics"]["joint"][k] for k in ("pearson", "spearman")])
    def gly_residual(x):
        objective_calls["glycemia"] += 1
        budget()
        parameters["dependence"].update(tail_probability=float(x[0]), rho_body=float(x[1]))
        d = law_diagnostics(parameters, integrator=integ)
        return (np.array([d["joint"][k] for k in ("pearson", "spearman")]) - target_joint) / 0.02
    gly_results = []
    for start in GLY_STARTS:
        calls_before = objective_calls["glycemia"]
        result = least_squares(gly_residual, start, bounds=([0.002, -0.85], [0.25, 0.95]),
                               max_nfev=80, ftol=1e-9, xtol=1e-9, gtol=1e-9, diff_step=1e-4)
        gly_results.append(result)
        records.append({"stage": "glycemia", "start": list(start), "nfev": result.nfev,
                        "objective_calls": objective_calls["glycemia"] - calls_before,
                        "success": bool(result.success), "cost": float(result.cost), "parameters": result.x.tolist()})
    best = min(gly_results, key=lambda r: (float(r.cost), tuple(r.x)))
    gly_residual(best.x)
    target_beta = np.array([summary["estimands"][k]["coefficient"] for k in ("E1", "E2", "E3")])
    beta_scale = np.maximum(np.abs(target_beta), [0.02, 0.1, 0.005])
    def cov_residual(x):
        objective_calls["covariates"] += 1
        budget()
        ax, ay, bx = _decode_cov(x)
        parameters["dependence"].update(age_common=ax, age_difference=ay, bmi_common=bx)
        d = law_diagnostics(parameters, integrator=integ)
        return (np.array([d["estimands"][k] for k in ("E1", "E2", "E3")]) - target_beta) / beta_scale
    cov_results = []
    for start in COV_STARTS:
        calls_before = objective_calls["covariates"]
        result = least_squares(cov_residual, start, bounds=(-2.0, 2.0), max_nfev=120,
                               ftol=1e-9, xtol=1e-9, gtol=1e-9, diff_step=1e-4)
        cov_results.append(result)
        records.append({"stage": "covariates", "start": list(start), "nfev": result.nfev,
                        "objective_calls": objective_calls["covariates"] - calls_before,
                        "success": bool(result.success), "cost": float(result.cost), "parameters": result.x.tolist()})
    best_cov = min(cov_results, key=lambda r: (float(r.cost), tuple(r.x)))
    cov_residual(best_cov.x)
    fixed = copy.deepcopy(parameters)
    checks = [law_diagnostics(fixed, order=FIT_ORDER)]
    for order in CHECK_ORDERS:
        budget()
        checks.append(law_diagnostics(fixed, order=order))
    differences = []
    # Absolute errors in coefficients use the original native units.
    tolerance = {"pearson": 0.003, "E1": 0.001, "E2": 0.002, "E3": 0.0003}
    for old, new in zip(checks[:-1], checks[1:]):
        delta = {"pearson": abs(new["joint"]["pearson"] - old["joint"]["pearson"]),
                 **{k: abs(new["estimands"][k] - old["estimands"][k]) for k in ("E1", "E2", "E3")}}
        differences.append({"orders": [old["quadrature_order"], new["quadrature_order"]], "absolute_change": delta,
                            "pass": all(delta[k] <= tolerance[k] for k in tolerance)})
    valid_margins = all(x["max_constraint_error"] <= 1e-6 for x in marginal_status.values())
    integration_pass = all(d["pass"] for d in differences)
    return {"parameters": fixed, "usage_ledger": usage_ledger(summary), "fit_diagnostics": {
        "family": FAMILY, "wall_seconds": time.monotonic() - begun, "margin_solver": marginal_status,
        "dependence_objective_calls_including_selection_replays": objective_calls,
        "fit_integration_call_counts": dict(integ.calls),
        "optimizer_runs": records, "law_diagnostics_by_order": checks,
        "integration_checks": differences, "integration_tolerances": tolerance,
        "generation_allowed": bool(valid_margins and integration_pass),
        "termination": "completed_fixed_allocation", "marginal_constraints_pass": bool(valid_margins),
        "joint_native_residual": (np.array([checks[-1]["joint"][k] for k in ("pearson", "spearman")]) - target_joint).tolist(),
        "estimand_native_residual": (np.array([checks[-1]["estimands"][k] for k in ("E1", "E2", "E3")]) - target_beta).tolist(),
        "summary_sd_interpretation": "Reported sample SD is used as population plug-in SD; no finite-sample correction or final-row forcing.",
        "unfitted_metadata": "n, quality/cleaning, regression SE/CI/cluster count/rank/condition numbers retained as context, not objectives."}}
