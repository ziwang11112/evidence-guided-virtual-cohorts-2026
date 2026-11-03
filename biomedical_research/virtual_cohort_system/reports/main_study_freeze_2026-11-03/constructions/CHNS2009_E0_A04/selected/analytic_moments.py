"""Deterministic closed-form algebra only; never imports or runs generator.py."""
import ast
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = json.loads((HERE / "model_spec.json").read_text(encoding="utf-8"))
p = spec["parameters"]
names = p["continuous_order"]
ms = p["marginals"]
mu, variance_log = {}, {}
for name in names:
    m = ms[name]["mean"]
    s = ms[name]["individual_sd"]
    loading = ms[name]["factor_loading"]
    assert m > 0 and s > 0 and abs(loading) < 1
    variance_log[name] = math.log1p((s / m) ** 2)
    mu[name] = math.log(m) - variance_log[name] / 2

cov = {}
corr = {}
for x in names:
    cov[x], corr[x] = {}, {}
    for y in names:
        rlog = 1.0 if x == y else ms[x]["factor_loading"] * ms[y]["factor_loading"]
        cov[x][y] = ms[x]["mean"] * ms[y]["mean"] * math.expm1(math.sqrt(variance_log[x] * variance_log[y]) * rlog)
        corr[x][y] = cov[x][y] / (ms[x]["individual_sd"] * ms[y]["individual_sd"])

moments = {}
for name in names:
    v = variance_log[name]
    m1 = math.exp(mu[name] + v / 2)
    m2 = math.exp(2 * mu[name] + 2 * v)
    variance = math.expm1(v) * math.exp(2 * mu[name] + v)
    sd = math.sqrt(variance)
    assert math.isclose(m1, ms[name]["mean"], rel_tol=1e-13)
    assert math.isclose(sd, ms[name]["individual_sd"], rel_tol=1e-13)
    moments[name] = {"unit": ms[name]["unit"], "mean": m1, "second_raw_moment": m2, "variance": variance, "individual_sd": sd, "log_mean": mu[name], "log_variance": v, "support": "(0,infinity)", "source_transport_validated": False}

age_n = p["age_max"] - p["age_min"] + 1
moments["age"] = {"mean": (p["age_min"] + p["age_max"]) / 2, "variance": (age_n ** 2 - 1) / 12, "support": [p["age_min"], p["age_max"]], "integer": True}
fp = p["female_probability"]
moments["female"] = {"mean": fp, "variance": fp * (1 - fp), "support": [0, 1]}

tree = ast.parse((HERE / "generator.py").read_text(encoding="utf-8"))
functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "generate"]
assert len(functions) == 1
args = functions[0].args
assert len(args.posonlyargs) + len(args.args) == 3
assert not args.vararg and not args.kwarg and not args.kwonlyargs
assert p["n_rows"] == 3000
assert p["output_columns"] == ["row_id", "age", "female", "bmi", "glucose", "hba1c"]
assert [p["age_min"], p["age_max"]] == [35, 74]

def sha(name):
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()

report = {
    "method": "closed_form_normal_exponential_moments_and_static_AST_only",
    "generator_imported": False,
    "generator_executed": False,
    "row_samples": 0,
    "monte_carlo_draws": 0,
    "quadrature_evaluations": 0,
    "input_hashes": {name: sha(name) for name in ["model_spec.json", "generator.py", "evidence.json"]},
    "script_sha256": sha("analytic_moments.py"),
    "status": "pass",
    "moments": moments,
    "continuous_covariance": cov,
    "continuous_pearson_correlation": corr,
    "positive_definiteness": {"normal_residual_variances": {name: 1 - ms[name]["factor_loading"] ** 2 for name in names}, "argument": "ll' plus strictly positive diagonal, with nondegenerate monotone lognormal transforms"},
    "law_implied_ols": {
        "E1_bmi_coefficient": {"value": cov["bmi"]["hba1c"] / cov["bmi"]["bmi"], "unit": "%/(kg/m^2)"},
        "E2_glucose_coefficient": {"value": cov["glucose"]["hba1c"] / cov["glucose"]["glucose"], "unit": "%/(mmol/L)"},
        "E3_age_coefficient": {"value": 0.0, "unit": "%/year"},
        "interpretation": "Consequences of explicit assumptions; no source regression estimates, target values, fitted objectives or validation conclusions."
    },
    "limitations": ["No source-population reconstruction", "No target validity check", "No empirical estimation of dependence or age/sex composition", "No runtime or finite-table verification"]
}
(HERE / "analytic_results.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
print(json.dumps({"status": report["status"], "generator_executed": False, "artifact": str(HERE / "analytic_results.json")}))
