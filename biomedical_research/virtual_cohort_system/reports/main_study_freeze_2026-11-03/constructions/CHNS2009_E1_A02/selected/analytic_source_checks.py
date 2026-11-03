"""Exact, deterministic law moments; never import/execute generator or draw rows.

The coefficient matrix below is an algebraic expansion of generator.py's affine
equations. Source contexts replace only declared age/composition/residual/tail
parameters. No quadrature, Monte Carlo, optimization or numerical fitting occurs.
"""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import math
import sys
import numpy as np

sys.dont_write_bytecode = True

C = Path(__file__).resolve().parent
BUNDLE = C.parent.parent
SPEC = json.loads((C / "model_spec.json").read_text(encoding="utf-8-sig"))
P = SPEC["parameters"]
D = P["shared_structure"]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def age_moments(c):
    law = c["age_law"]
    if law == "discrete_uniform_inclusive":
        lo, hi = c["age_min"], c["age_max"]
        return (lo + hi) / 2, ((hi - lo + 1) ** 2 - 1) / 12, lo, hi
    if law == "continuous_uniform_matching_mean_sd":
        mu, sd = c["age_mean"], c["age_sd"]
        return mu, sd ** 2, mu - math.sqrt(3) * sd, mu + math.sqrt(3) * sd
    if law == "piecewise_linear_quantile":
        probs, vals = c["age_probability_knots"], c["age_value_knots"]
        mu = 0.0
        second = 0.0
        for u, v, a, b in zip(probs[:-1], probs[1:], vals[:-1], vals[1:]):
            mu += (v - u) * (a + b) / 2
            second += (v - u) * (a * a + a * b + b * b) / 3
        return mu, second - mu * mu, vals[0], vals[-1]
    raise ValueError("Unspecified age law")

def moments(c):
    am, av, alo, ahi = age_moments(c)
    p = c["female_probability"]
    sb, sg, sh = (c[k] for k in ("bmi_residual_sd", "glucose_residual_sd", "hba1c_residual_sd"))
    r = D["residual_bmi_glucose_correlation"]
    q, k, theta = (c[s] for s in ("upper_probability", "upper_gamma_shape", "upper_gamma_scale"))
    lm = q * k * theta
    lsecond = q * k * (k + 1) * theta ** 2
    lv = lsecond - lm ** 2
    load = np.zeros((5, 6), dtype=float)
    load[0, 0] = 1
    load[1, 1] = 1
    load[2] = [D["bmi_age"], D["bmi_female"], sb, 0, 0, 0]
    load[3] = [D["glucose_age"], D["glucose_female"], sg*r, sg*math.sqrt(1-r*r), 0, 1]
    load[4] = D["hba1c_bmi_joint"] * load[2] + D["hba1c_glucose_joint"] * load[3]
    load[4, 0] += D["hba1c_age_direct"]
    load[4, 1] += D["hba1c_female_direct"]
    load[4, 4] += sh
    load[4, 5] += D["hba1c_upper_extra"]
    variances = np.array([av, p*(1-p), 1, 1, 1, lv])
    cov = (load * variances) @ load.T
    means = [am, p, c["bmi_center"], c["glucose_center"]+lm,
             c["hba1c_center"] + load[4, 5] * lm]
    centers = [am, p, c["bmi_center"], c["glucose_center"], c["hba1c_center"]]
    bmi_lower = -math.sqrt(c["bmi_gamma_shape"]) if c["bmi_innovation_law"] == "standardized_gamma" else -math.sqrt(3)
    ranges = [(alo-am, ahi-am), (-p, 1-p), (bmi_lower, math.sqrt(3)), (-math.sqrt(3), math.sqrt(3)), (-math.sqrt(3), math.sqrt(3))]
    supports = {}
    names = ["age", "gender_binary", "BMI", "FPG", "HbA1c_percent"]
    for name, center, coefficients in zip(names, centers, load):
        low = center + sum(min(b*x, b*y) for b, (x, y) in zip(coefficients[:5], ranges))
        high = center + sum(max(b*x, b*y) for b, (x, y) in zip(coefficients[:5], ranges))
        if q > 0 and coefficients[5] > 0:
            high = None
        elif q > 0 and coefficients[5] < 0:
            low = None
        if c["bmi_innovation_law"] == "standardized_gamma" and coefficients[2] > 0:
            high = None
        elif c["bmi_innovation_law"] == "standardized_gamma" and coefficients[2] < 0:
            low = None
        supports[name] = {"lower_bound": low, "upper_bound": high, "null_means_unbounded": True}
    return {"variables": names, "means": means, "covariance": cov.tolist(),
            "loading_matrix": load.tolist(), "independent_component_variances": variances.tolist(),
            "independent_component_order": ["centered_age", "centered_female", "U_B", "U_G", "U_H", "centered_L"],
            "age_support": [alo, ahi], "excess_mean": lm, "excess_second_moment": lsecond,
            "support_bounds": supports, "smallest_covariance_eigenvalue": float(np.linalg.eigvalsh(cov).min())}

helper_path = BUNDLE / "input/source_operations.py"
loader_spec = importlib.util.spec_from_file_location("assigned_source_operations", helper_path)
helper = importlib.util.module_from_spec(loader_spec)
loader_spec.loader.exec_module(helper)

def source_context(name, assumptions):
    c = P[name]
    m = moments(c)
    return {**m, "role": "declared_source_population_moments", "source_context_id": c["source_context_id"],
            "assumption_ids": assumptions, "selection_status": "moments_after_declared_source_selection",
            "weights": "equal_assumption", "gender_mapping": "female=1,male=0",
            "units": {"age": "year", "gender_binary": "1", "BMI": "kg/m^2", "FPG": "mmol/L", "HbA1c_percent": "%"},
            "moment_derivation": "Affine generator equations expanded as loading_matrix times independent centered components. Covariance=M diag(component variances) M^T. Bernoulli-gamma E[L]=q*k*theta; E[L^2]=q*k*(k+1)*theta^2. Source age exact moments use its declared source law, never target age support. See mathematical_properties.md and this retained script."}

j = source_context("jansen_context", ["A_JANSEN", "A_JANSEN_PROJECTION", "A_COVARIATES", "A_LAW", "A_SOURCE_CHECKS"])
b = source_context("bao_context", ["A_BAO", "A_UPPER", "A_COVARIATES", "A_LAW", "A_SOURCE_CHECKS"])
assert j["support_bounds"]["FPG"]["upper_bound"] < P["jansen_context"]["fpg_selection_upper_exclusive"]
source_comparisons = []
for eid, context, point in [("R_JANSEN_BMI", j, P["reported_constraints"]["jansen_bmi_separate_ifcc"]),
                            ("R_JANSEN_FPG", j, P["reported_constraints"]["jansen_fpg_separate_ifcc"]),
                            ("R_BAO_PEARSON", b, P["reported_constraints"]["bao_pearson"])]:
    r = helper.evaluate(eid, context)
    r.update(source_point=point, raw_difference=r["calculated_value"]-point,
             fitted_constraint=eid.startswith("R_JANSEN"), uncertainty_standardization=None,
             interpretation="Descriptive raw discrepancy only; constrained agreement is not independent validation.")
    source_comparisons.append(r)

# Independently reconstruct the two joint response coefficients from the
# separately adjusted source slopes; this is deterministic algebra, not fitting.
c = P["jansen_context"]
r = D["residual_bmi_glucose_correlation"]
sb, sg = c["bmi_residual_sd"], c["glucose_residual_sd"]
a = P["unit_conversion"]["ngsp_per_ifcc"]
tb, tg = [a * P["reported_constraints"][k] for k in ("jansen_bmi_separate_ifcc", "jansen_fpg_separate_ifcc")]
bb = (tb - tg*r*sg/sb)/(1-r*r)
bg = (tg - tb*r*sb/sg)/(1-r*r)
assert math.isclose(bb, D["hba1c_bmi_joint"], rel_tol=1e-12)
assert math.isclose(bg, D["hba1c_glucose_joint"], rel_tol=1e-12)
assert all(math.isclose(v["calculated_value"], v["source_point"], rel_tol=1e-12) for v in source_comparisons[:2])

t = moments(P["target_context"])
target_names = ["age", "female", "bmi", "glucose", "hba1c"]
t["support_bounds"] = {new: t["support_bounds"][old] for old,new in zip(t["variables"], target_names)}
t["variables"] = target_names
t["measurement"] = "Task central-serum glucose, not a renaming of source fasting plasma FPG; numerical bridge is A_TRANSPORT."
for name in ("bmi", "glucose", "hba1c"):
    assert t["support_bounds"][name]["lower_bound"] > 0
assert all(ctx["smallest_covariance_eigenvalue"] > 0 for ctx in (j,b,t))
tcov = np.array(t["covariance"])
implications = {}
for name, ix, focal in [("E1", [0,1,2], 2), ("E2", [0,1,3], 3), ("E3", [1,2,3,0], 0)]:
    result = np.linalg.solve(tcov[np.ix_(ix,ix)], tcov[ix,4])
    implications[name] = {"population_projection": float(result[ix.index(focal)]),
                          "interpretation": "Algebraic consequence of assumed target law; not a target observation, calibration target or independent evidence."}

syntax = ast.parse((C / "generator.py").read_text(encoding="utf-8"))
functions = [x for x in syntax.body if isinstance(x, ast.FunctionDef) and x.name == "generate"]
assert len(functions) == 1 and len(functions[0].args.args) == 3
assert not any(isinstance(x, (ast.Import, ast.ImportFrom)) and any("generator" in y.name for y in x.names) for x in ast.walk(ast.parse(Path(__file__).read_text(encoding="utf-8"))))
result = {
    "scope": "deterministic analytic laws and static syntax only",
    "rows_generated": 0, "random_draws": 0, "generator_imported_or_executed": False,
    "numerical_quadrature": False, "optimization": False,
    "inputs": {"model_spec_sha256": sha(C / "model_spec.json"), "generator_sha256": sha(C / "generator.py"),
               "source_operations_sha256": sha(helper_path), "analytic_script_sha256": sha(Path(__file__))},
    "source_contexts": {"CTX_JANSEN_SELECTED": j, "CTX_BAO_ANALYZED": b},
    "source_comparisons": source_comparisons,
    "source_unavailable": {"R_MIND_SPEARMAN": "No declared MIND rank law or source-specific imputation/tie reconstruction; ordinary covariance cannot identify Spearman."},
    "target_law_support_and_moments": t, "target_law_algebraic_implications": implications,
    "assertions": ["Separate Jansen projection equations reproduced by actual affine source law", "Jansen source FPG support is below 7",
                   "All three law covariance matrices positive definite", "Target BMI/glucose/HbA1c have positive lower bounds",
                   "Three-positional-argument ABI is syntactically present", "No generator import or execution in this script"],
    "source_replay": "unavailable", "transport_validated": False,
}
(C / "analytic_results.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
print(json.dumps({"source_comparisons": source_comparisons, "target_support": t["support_bounds"], "row_production": False}, indent=2))
