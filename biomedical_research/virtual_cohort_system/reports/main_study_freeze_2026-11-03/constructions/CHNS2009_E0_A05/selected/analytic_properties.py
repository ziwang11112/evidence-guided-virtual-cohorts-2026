"""Exact finite sums and Gaussian MGFs only. Never imports or executes generator."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
from pathlib import Path
import numpy as np


def calculate(candidate):
    candidate = Path(candidate)
    spec_file = candidate / "model_spec.json"
    p = json.loads(spec_file.read_text(encoding="utf-8"))["parameters"]
    ages = np.arange(p["age_min"], p["age_max"] + 1, dtype=float)
    mean_age = ages.mean()
    f = p["female_probability"]
    a = np.array(p["log_age_effects"])
    b = np.array(p["log_female_effects"])
    m = np.array(p["biomarker_means"])
    sd = np.array(p["biomarker_sds"])
    lam = np.array(p["residual_factor_loadings"])

    # Exactly 80 demographic atoms, not sampled people or quadrature nodes.
    atoms = [(age, female, (f if female else 1-f) / len(ages))
             for age in ages for female in (0, 1)]
    def bounded_sum(t, multiplier=lambda age, female: 1.0):
        return sum(weight * multiplier(age, female) * np.exp(
            np.dot(t, a * (age - mean_age) / p["age_effect_unit_years"] + b * (female-f)))
            for age, female, weight in atoms)

    identity = np.eye(len(m))
    m1 = np.array([bounded_sum(t) for t in identity])
    m2 = np.array([bounded_sum(2*t) for t in identity])
    v = np.log1p((sd/m)**2) - np.log(m2 / m1**2)
    assert np.all(v > 0)
    assert np.all(np.abs(lam) < 1)
    intercepts = np.log(m)-np.log(m1)-v/2
    residual_cov = np.outer(lam*np.sqrt(v), lam*np.sqrt(v)) + np.diag(v*(1-lam**2))
    def biomarker_moment(t, multiplier=lambda age, female: 1.0):
        return float(np.exp(np.dot(t, intercepts) + 0.5*t@residual_cov@t)
                     * bounded_sum(t, multiplier))

    names = ["age", "female", *p["biomarker_order"]]
    means = np.array([mean_age, f, *[biomarker_moment(t) for t in identity]])
    raw2 = np.empty((len(names), len(names)))
    raw2[0,0] = np.mean(ages**2)
    raw2[1,1] = f
    raw2[0,1] = raw2[1,0] = mean_age*f
    for j,t in enumerate(identity):
        raw2[0,j+2] = raw2[j+2,0] = biomarker_moment(t, lambda age, female: age)
        raw2[1,j+2] = raw2[j+2,1] = biomarker_moment(t, lambda age, female: female)
        for k,u in enumerate(identity):
            raw2[j+2,k+2] = biomarker_moment(t+u)
    covariance = raw2 - np.outer(means, means)
    recovered_sd = np.sqrt(np.diag(covariance))
    assert np.allclose(means[2:], m, rtol=1e-12, atol=1e-12)
    assert np.allclose(recovered_sd[2:], sd, rtol=1e-10, atol=1e-10)
    assert np.linalg.eigvalsh(residual_cov).min() > 0
    assert np.linalg.eigvalsh(covariance).min() > 0
    analysis = {}
    for analysis_id, predictors, term in [
        ("E1", ["age","female","bmi"], "bmi"),
        ("E2", ["age","female","glucose"], "glucose"),
        ("E3", ["female","bmi","glucose","age"], "age"),
    ]:
        idx = [names.index(name) for name in predictors]
        matrix = covariance[np.ix_(idx,idx)]
        rhs = covariance[idx,names.index("hba1c")]
        beta = np.linalg.solve(matrix,rhs)
        analysis[analysis_id] = {
            "predictors": predictors, "coefficients": dict(zip(predictors,beta.tolist())),
            "intercept": float(means[-1]-beta@means[idx]), "term": term,
            "term_value": float(beta[predictors.index(term)]),
            "design_covariance_min_eigenvalue": float(np.linalg.eigvalsh(matrix).min()),
            "normal_equation_max_abs_residual": float(np.max(np.abs(matrix@beta-rhs))),
            "interpretation": "Exact model consequence, not source projection, target observation or clinical evidence."
        }
    return {
        "method": "Exact enumeration of 40 x 2 demographic states and analytic Gaussian exponential moments; floating-point arithmetic only; no RNG, rows, numerical integration or generator import.",
        "scope": "Declared target scenario law only, not source-population replay or target validation.",
        "spec_sha256": hashlib.sha256(spec_file.read_bytes()).hexdigest(),
        "generator_sha256": hashlib.sha256((candidate/"generator.py").read_bytes()).hexdigest(),
        "ordered_variables": names, "means": means.tolist(), "sds": recovered_sd.tolist(),
        "raw_second_moments": raw2.tolist(), "covariance": covariance.tolist(),
        "residual_log_variances": v.tolist(), "log_intercepts": intercepts.tolist(),
        "residual_log_covariance": residual_cov.tolist(),
        "residual_covariance_min_eigenvalue": float(np.linalg.eigvalsh(residual_cov).min()),
        "covariance_min_eigenvalue": float(np.linalg.eigvalsh(covariance).min()),
        "source_marginal_scale_recovery_max_abs_mean_error": float(np.max(np.abs(means[2:]-m))),
        "source_marginal_scale_recovery_max_abs_sd_error": float(np.max(np.abs(recovered_sd[2:]-sd))),
        "population_ols": analysis,
        "source_comparisons": "unavailable; transposed marginal numbers are assumptions, not validation"
    }


if __name__ == "__main__":
    destination = Path(__file__).resolve().parent
    result = calculate(destination)
    (destination / "analytic_properties.json").write_text(
        json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(json.dumps({"status":"pass", "method":result["method"], "population_ols":result["population_ols"]}, indent=2))
