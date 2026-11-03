"""Deterministic, source-only Gaussian-copula moment completion.

No file/network reads, random-number calls, cohort rows, target estimates, or
campaign dispatch are implemented. Integration nodes are quadrature points,
not simulated participants. A caller must separately admit source semantics,
marginal models, and any source-to-target transport/sampling implementation.
"""
from __future__ import annotations

from functools import lru_cache
import math
from typing import Any

import numpy as np
from numpy.polynomial.hermite import hermgauss
from scipy.optimize import least_squares, minimize
from scipy.special import ndtr, ndtri


VERSION = "source_moment_maxentropy_v1"
SUPPORTED_KINDS = {"normal", "lognormal", "shifted_lognormal", "truncated_lognormal", "uniform", "bernoulli"}


def _finite(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def lognormal_from_mean_sd(mean: float, sd: float) -> dict[str, float | str]:
    _require(_finite(mean) and _finite(sd) and mean > 0 and sd > 0,
             "Lognormal mean and individual SD must be finite and positive")
    variance = math.log1p((sd / mean) ** 2)
    return {"kind": "lognormal", "mu": math.log(mean) - variance / 2,
            "sigma": math.sqrt(variance)}


def shifted_lognormal_from_mean_sd(mean: float, sd: float, offset: float) -> dict[str, Any]:
    _require(_finite(offset) and offset >= 0, "Finite nonnegative offset required")
    return {**lognormal_from_mean_sd(mean - offset, sd), "kind": "shifted_lognormal", "offset": offset}


def lognormal_from_quartiles(q1: float, median: float, q3: float) -> dict[str, Any]:
    """Unweighted log-quantile least squares; quartiles are not SEs.

    Retains all three residuals because a lognormal need not fit all three
    supplied points exactly. No source sample size or precision is invented.
    """
    _require(all(_finite(x) for x in (q1, median, q3)) and 0 < q1 < median < q3,
             "Strictly increasing positive quartiles required")
    z = float(ndtri(0.75))
    mu = float(np.mean(np.log([q1, median, q3])))
    sigma = (math.log(q3) - math.log(q1)) / (2 * z)
    implied = np.exp(mu + sigma * np.array([-z, 0, z]))
    return {"marginal": {"kind": "lognormal", "mu": mu, "sigma": sigma},
            "reported": [q1, median, q3], "implied": implied.tolist(),
            "raw_residuals": (implied - [q1, median, q3]).tolist(),
            "fit_rule": "unweighted_least_squares_of_three_log_quantiles"}


def _truncated_raw_moment(mu: float, sigma: float, low: float, high: float,
                          power: int) -> float:
    a = -math.inf if low == 0 else (math.log(low) - mu) / sigma
    b = math.inf if high == math.inf else (math.log(high) - mu) / sigma
    normalizer = float(ndtr(b) - ndtr(a))
    _require(normalizer > 1e-12, "Truncation mass too small for stable declared calculation")
    shifted = float(ndtr(b - power * sigma) - ndtr(a - power * sigma))
    value = math.exp(power * mu + 0.5 * power * power * sigma * sigma) * shifted / normalizer
    _require(math.isfinite(value), "Nonfinite truncated moment")
    return value


def truncated_lognormal_from_mean_sd(mean: float, sd: float,
                                      low: float, high: float) -> dict[str, Any]:
    """Fit two *source* moments with declared support; never clip afterward."""
    _require(all(_finite(v) for v in (mean, sd, low, high)) and
             0 <= low < mean < high and sd > 0,
             "Finite compatible support, mean and individual SD required")
    _require(sd * sd < (high - mean) * (mean - low),
             "Variance violates the bounded-support moment bound")
    initial = lognormal_from_mean_sd(mean, sd)

    def residual(theta: np.ndarray) -> np.ndarray:
        mu, log_sigma = theta
        sigma = math.exp(float(log_sigma))
        try:
            first = _truncated_raw_moment(float(mu), sigma, low, high, 1)
            second = _truncated_raw_moment(float(mu), sigma, low, high, 2)
            variance = second - first * first
            if variance <= 0:
                return np.array([1e6, 1e6])
            return np.array([(first - mean) / sd, (math.sqrt(variance) - sd) / sd])
        except (ValueError, OverflowError):
            return np.array([1e6, 1e6])

    fit = least_squares(residual, [initial["mu"], math.log(initial["sigma"])],
                        bounds=([-40, -8], [40, 2]), max_nfev=300,
                        ftol=1e-12, xtol=1e-12, gtol=1e-12)
    _require(fit.success and np.max(np.abs(residual(fit.x))) < 1e-7,
             "No sufficiently accurate truncated-lognormal moment fit; no fallback")
    return {"kind": "truncated_lognormal", "mu": float(fit.x[0]),
            "sigma": math.exp(float(fit.x[1])), "low": low, "high": high}


def validate_marginal(m: dict[str, Any]) -> None:
    _require(isinstance(m, dict) and m.get("kind") in SUPPORTED_KINDS,
             "Unsupported marginal family")
    kind = m["kind"]
    fields = {"normal": {"mean", "sd"}, "lognormal": {"mu", "sigma"},
              "shifted_lognormal": {"mu", "sigma", "offset"},
              "truncated_lognormal": {"mu", "sigma", "low", "high"},
              "uniform": {"low", "high"}, "bernoulli": {"probability"}}[kind]
    _require(set(m) == {"kind", *fields} and all(_finite(m[k]) for k in fields),
             "Marginal fields must be exact and finite")
    if kind == "normal":
        _require(m["sd"] > 0, "Positive normal SD required")
    elif kind in {"lognormal", "shifted_lognormal", "truncated_lognormal"}:
        _require(m["sigma"] > 0, "Positive log SD required")
        if kind == "shifted_lognormal":
            _require(m["offset"] >= 0, "Nonnegative shifted-lognormal offset required")
        if kind == "truncated_lognormal":
            _require(0 <= m["low"] < m["high"], "Invalid truncation support")
    elif kind == "uniform":
        _require(m["low"] < m["high"], "Nondegenerate uniform support required")
    else:
        _require(0 < m["probability"] < 1, "Nondegenerate Bernoulli required")


def marginal_moments(m: dict[str, Any]) -> tuple[float, float]:
    validate_marginal(m)
    kind = m["kind"]
    if kind == "normal":
        return m["mean"], m["sd"] ** 2
    if kind in {"lognormal", "shifted_lognormal"}:
        mean = math.exp(m["mu"] + 0.5 * m["sigma"] ** 2)
        return mean + m.get("offset", 0.0), mean * mean * math.expm1(m["sigma"] ** 2)
    if kind == "truncated_lognormal":
        first = _truncated_raw_moment(m["mu"], m["sigma"], m["low"], m["high"], 1)
        second = _truncated_raw_moment(m["mu"], m["sigma"], m["low"], m["high"], 2)
        return first, max(0.0, second - first * first)
    if kind == "uniform":
        return (m["low"] + m["high"]) / 2, (m["high"] - m["low"]) ** 2 / 12
    p = m["probability"]
    return p, p * (1 - p)


def _transform(m: dict[str, Any], z: np.ndarray) -> np.ndarray:
    kind = m["kind"]
    if kind == "normal":
        return m["mean"] + m["sd"] * z
    if kind in {"lognormal", "shifted_lognormal"}:
        return m.get("offset", 0.0) + np.exp(m["mu"] + m["sigma"] * z)
    p = ndtr(z)
    if kind == "uniform":
        return m["low"] + (m["high"] - m["low"]) * p
    if kind == "truncated_lognormal":
        a = 0.0 if m["low"] == 0 else float(ndtr((math.log(m["low"]) - m["mu"]) / m["sigma"]))
        b = float(ndtr((math.log(m["high"]) - m["mu"]) / m["sigma"]))
        probability = np.clip(a + (b - a) * p, np.finfo(float).eps, 1 - np.finfo(float).eps)
        return np.exp(m["mu"] + m["sigma"] * ndtri(probability))
    raise ValueError("Bernoulli dependence is unsupported; use explicit independence")


@lru_cache(maxsize=6)
def _quadrature(order: int) -> tuple[np.ndarray, np.ndarray]:
    _require(order in {24, 32, 48, 64, 96, 128}, "Unsupported integration order")
    nodes, weights = hermgauss(order)
    return math.sqrt(2) * nodes, weights / math.sqrt(math.pi)


def pair_covariance(left: dict[str, Any], right: dict[str, Any],
                    rho: float, order: int = 64) -> float:
    ml, vl = marginal_moments(left)
    mr, vr = marginal_moments(right)
    _require(_finite(rho) and abs(rho) < 1, "Copula correlation must be strictly interior")
    if rho == 0:
        return 0.0
    _require(left["kind"] != "bernoulli" and right["kind"] != "bernoulli",
             "Non-independent Bernoulli relationship is not supported")
    lk = "lognormal" if left["kind"] == "shifted_lognormal" else left["kind"]
    rk = "lognormal" if right["kind"] == "shifted_lognormal" else right["kind"]
    ml_base, mr_base = ml - left.get("offset", 0.0), mr - right.get("offset", 0.0)
    if lk == rk == "normal":
        return rho * math.sqrt(vl * vr)
    if lk == rk == "lognormal":
        return ml_base * mr_base * math.expm1(rho * left["sigma"] * right["sigma"])
    if lk == "normal" and rk == "lognormal":
        return left["sd"] * mr_base * right["sigma"] * rho
    if lk == "lognormal" and rk == "normal":
        return right["sd"] * ml_base * left["sigma"] * rho
    z, w = _quadrature(order)
    a = _transform(left, z[:, None])
    b = _transform(right, rho * z[:, None] + math.sqrt(1 - rho * rho) * z[None, :])
    return float(np.sum(w[:, None] * w[None, :] * (a - ml) * (b - mr)))


def covariance_matrix(marginals: dict[str, dict[str, Any]], correlation: np.ndarray,
                      order: int = 64) -> tuple[list[str], np.ndarray]:
    names = list(marginals)
    r = np.asarray(correlation, dtype=float)
    _require(r.shape == (len(names), len(names)) and np.isfinite(r).all(),
             "Invalid correlation dimensions/values")
    _require(np.allclose(r, r.T, atol=1e-12) and np.allclose(np.diag(r), 1, atol=1e-12),
             "Correlation must be symmetric with unit diagonal")
    _require(np.linalg.eigvalsh(r).min() > 0, "Latent correlation is not positive definite")
    c = np.diag(np.asarray([marginal_moments(marginals[n])[1] for n in names], dtype=float))
    for i in range(len(names)):
        for j in range(i):
            c[i, j] = c[j, i] = pair_covariance(marginals[names[i]], marginals[names[j]],
                                              float(r[i, j]), order)
    _require(np.linalg.eigvalsh(c).min() > 0, "Raw covariance is not positive definite")
    return names, c


def statistic(marginals: dict[str, dict[str, Any]], correlation: np.ndarray,
              operator: dict[str, Any], order: int = 64) -> float:
    """Every OLS record names its own full design; projections stay separate."""
    names, c = covariance_matrix(marginals, correlation, order)
    idx = {n: i for i, n in enumerate(names)}
    kind = operator["kind"]
    if kind == "ols_coefficient":
        xs = operator["regressors"]
        _require(len(xs) > 0 and len(xs) == len(set(xs)) and
                 operator["outcome"] not in xs and operator["term"] in xs,
                 "Invalid separate regression design")
        ii = [idx[n] for n in xs]
        beta = np.linalg.solve(c[np.ix_(ii, ii)], c[ii, idx[operator["outcome"]]])
        return float(beta[xs.index(operator["term"])])
    left, right = operator["columns"]
    i, j = idx[left], idx[right]
    _require(i != j, "Two distinct variables required")
    if kind == "pearson_correlation":
        return float(c[i, j] / math.sqrt(c[i, i] * c[j, j]))
    if kind == "spearman_correlation":
        _require(all(marginals[n]["kind"] != "bernoulli" for n in (left, right)),
                 "Continuous-margin Spearman identity does not handle ties")
        return 6 / math.pi * math.asin(float(correlation[i, j]) / 2)
    raise ValueError("Unsupported source operator")


def fit_context(context: dict[str, Any], *, order: int = 64,
                max_iterations: int = 300) -> dict[str, Any]:
    """Maximum latent-Gaussian entropy subject to source point constraints.

    No cross-source objective, SE weighting, probabilistic uncertainty or
    fallback family is supplied. Incompatible constraints return a failed fit
    with residuals; they do not silently become approximate equality.
    """
    _require(set(context) == {"role", "source_context_id", "marginals", "constraints", "assumptions"},
             "Only the explicit normalized source-context fields are accepted")
    _require(context["role"] == "external_source" and isinstance(context["source_context_id"], str),
             "Only external source contexts are accepted")
    _require(isinstance(context["assumptions"], list) and bool(context["assumptions"]),
             "Source approximation/completion assumptions must be explicit")
    marginals = context["marginals"]
    _require(isinstance(marginals, dict) and 2 <= len(marginals) <= 6, "Require two to six named marginals")
    for m in marginals.values():
        validate_marginal(m)
    names = list(marginals)
    n = len(names)
    # Binary nuisance effects remain explicitly independent, not fitted facts.
    pairs = [(i, j) for i in range(n) for j in range(i)
             if marginals[names[i]]["kind"] != "bernoulli" and marginals[names[j]]["kind"] != "bernoulli"]
    constraints = context["constraints"]
    ids: set[str] = set()
    for c in constraints:
        _require(set(c) == {"evidence_id", "operator", "value", "numerical_scale"}, "Invalid normalized constraint")
        _require(c["evidence_id"] not in ids and _finite(c["value"]) and
                 _finite(c["numerical_scale"]) and c["numerical_scale"] > 0,
                 "Distinct IDs, finite value and positive non-precision numerical scale required")
        ids.add(c["evidence_id"])
        # Validate the design before invoking the optimizer.
        statistic(marginals, np.eye(n), c["operator"], order)

    def unpack(x: np.ndarray) -> np.ndarray:
        r = np.eye(n)
        for value, (i, j) in zip(x, pairs):
            r[i, j] = r[j, i] = value
        return r

    def objective(x: np.ndarray) -> float:
        r = unpack(x)
        sign, logdet = np.linalg.slogdet(r)
        return -float(logdet) if sign > 0 and np.linalg.eigvalsh(r).min() > 0 else 1e8

    def residuals(x: np.ndarray, calculation_order: int = order) -> np.ndarray:
        r = unpack(x)
        try:
            return np.array([(statistic(marginals, r, c["operator"], calculation_order) - c["value"]) /
                             c["numerical_scale"] for c in constraints])
        except (ValueError, np.linalg.LinAlgError):
            return np.full(len(constraints), 1e6)

    x0 = np.zeros(len(pairs))
    if constraints:
        rules = [{"type": "ineq", "fun": lambda x: np.linalg.eigvalsh(unpack(x)).min() - 1e-7},
                 {"type": "eq", "fun": residuals}]
        fit = minimize(objective, x0, method="SLSQP", bounds=[(-0.999, 0.999)] * len(pairs),
                       constraints=rules, options={"maxiter": max_iterations, "ftol": 1e-11})
        x = fit.x
        optimizer_success = bool(fit.success)
        message = str(fit.message)
        iterations = int(fit.nit)
    else:
        x, optimizer_success, message, iterations = x0, True, "Unconstrained maximum entropy: independence", 0
    r = unpack(x)
    positive = bool(np.linalg.eigvalsh(r).min() > 1e-7)
    checked_order = 128 if order < 128 else 96
    observed = []
    quadrature_stable = True
    if positive:
        for c in constraints:
            value = statistic(marginals, r, c["operator"], order)
            checked = statistic(marginals, r, c["operator"], checked_order)
            stable = abs(value - checked) / c["numerical_scale"] <= 1e-5
            quadrature_stable &= stable
            observed.append({"evidence_id": c["evidence_id"], "operator": c["operator"],
                             "reported": c["value"], "calculated": value, "raw_residual": value - c["value"],
                             "checked_order_value": checked, "quadrature_stable": stable})
    max_residual = float(np.max(np.abs(residuals(x)))) if constraints else 0.0
    return {"version": VERSION, "source_context_id": context["source_context_id"],
            "success": optimizer_success and positive and max_residual < 1e-6 and quadrature_stable,
            "optimizer_success": optimizer_success, "optimizer_message": message,
            "iterations": iterations, "variable_order": names,
            "latent_correlation": r.tolist(), "minimum_eigenvalue": float(np.linalg.eigvalsh(r).min()),
            "max_scaled_constraint_residual": max_residual, "source_checks": observed,
            "quadrature_order": order, "independent_order_check": checked_order,
            "assumptions": context["assumptions"], "sampled_rows": 0,
            "uncertainty": "No calibrated source, model or transport uncertainty",
            "execution_authorized": False}
