"""Retained deterministic algebra. Never import generator or draw random values."""
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import numpy as np

C = Path(__file__).resolve().parent
BUNDLE = C.parent.parent
spec = json.loads((C / "model_spec.json").read_text(encoding="utf-8"))
p = spec["parameters"]
m, co, lat = p["margins"], p["coefficients"], p["latent"]
helper_path = BUNDLE / "input/source_operators.py"
module_spec = importlib.util.spec_from_file_location("admitted_source_operator", helper_path)
operator_module = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(operator_module)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def standardized_beta_support(shapes):
    a, b = shapes
    mu = a / (a + b)
    var = a * b / ((a + b) ** 2 * (a + b + 1))
    return [(0 - mu) / math.sqrt(var), (1 - mu) / math.sqrt(var)]


sb, sg, rho = m["bmi_sd"], m["glucose_sd"], lat["bmi_glucose_correlation"]
a, b, g, r = co["age"], co["bmi"], co["glucose"], co["residual_sd"]
kb, kg = p["source_constraints"]["bmi_projection"], p["source_constraints"]["glucose_projection"]
expected_b = (kb - kg * rho * sg / sb) / (1 - rho ** 2)
expected_g = (kg - kb * rho * sb / sg) / (1 - rho ** 2)
assert abs(b - expected_b) < 1e-14 and abs(g - expected_g) < 1e-14
assert a == p["source_constraints"]["age_projection"]
assert r > 0 and 0 < rho < 1 and b > 0 and g > 0
us = standardized_beta_support(lat["bmi_beta"])
vs = standardized_beta_support(lat["glucose_beta"])
ws = standardized_beta_support(lat["hba1c_beta"])
bs = [m["bmi_mean"] + sb * u for u in us]
gs = [m["glucose_mean"] + sg * (rho * us[i] + math.sqrt(1 - rho ** 2) * vs[i]) for i in range(2)]


def h_support(age_support):
    return [m["hba1c_mean"] + a * (age_support[i] - m["age_center"])
            + b * (bs[i] - m["bmi_mean"]) + g * (gs[i] - m["glucose_mean"]) + r * ws[i]
            if age_support[i] is not None else None for i in range(2)]


variables = ["age", "female", "bmi", "glucose", "hba1c"]
contexts = {}
for name, context in p["source_contexts"].items():
    if context["age_distribution"] == "uniform":
        ma, va = context["age_mean"], context["age_sd"] ** 2
        age_support = [ma - math.sqrt(3 * va), ma + math.sqrt(3 * va)]
    else:
        ma = context["age_shift"] + context["age_shape"] * context["age_scale"]
        va = context["age_shape"] * context["age_scale"] ** 2
        age_support = [context["age_shift"], None]
    pf = context["female_probability"]
    sx = np.diag([va, pf * (1 - pf), sb ** 2, sg ** 2])
    sx[2, 3] = sx[3, 2] = rho * sb * sg
    coeff = np.array([a, 0.0, b, g])
    xy = sx @ coeff
    variance_h = float(coeff @ sx @ coeff + r ** 2)
    covariance = np.zeros((5, 5))
    covariance[:4, :4] = sx
    covariance[:4, 4] = covariance[4, :4] = xy
    covariance[4, 4] = variance_h
    mean = [ma, pf, m["bmi_mean"], m["glucose_mean"], m["hba1c_mean"] + a * (ma - m["age_center"])]
    eig = np.linalg.eigvalsh(covariance)
    assert eig.min() > 0
    hbound = h_support(age_support)
    assert hbound[0] > 0
    context_ops = ["J_T2_bmi_slope_task_derived", "J_T2_glucose_slope_task_derived"] if name == "lifelines" else ["P_NHANES_age_slope"]
    calculated = []
    for oid in context_ops:
        result = operator_module.source_projection(oid, source_context=name, variables=variables, mean=mean, covariance=covariance)
        expected = kb if oid == context_ops[0] and name == "lifelines" else kg if name == "lifelines" else a
        result["nominal_constraint"] = expected
        result["difference"] = result["value"] - expected
        assert abs(result["difference"]) < 1e-12
        calculated.append(result)
    contexts[name] = {"law":context,"mean":mean,"covariance":covariance.tolist(),"covariance_eigenvalues":eig.tolist(),
                      "age_support":age_support,"hba1c_support":hbound,"analytic_projections":calculated}
assert abs(contexts["lifelines"]["covariance"][4][4] - m["hba1c_source_sd"] ** 2) < 1e-12
target_ages = [min(x[0] for x in p["design"]["age_bands"]), max(x[1] for x in p["design"]["age_bands"])]
target_h = h_support(target_ages)
assert bs[0] > 0 and gs[0] > 0 and gs[1] < 126 and target_h[0] > 0
assert len(p["design"]["age_bands"]) * len(p["design"]["female_values"]) * p["design"]["rows_per_cell"] == 3000
result = {
    "calculation":"closed-form beta/gamma/uniform moments and linear algebra; no quadrature, generator import, random draws, or individual rows",
    "variables_units":{"age":"year","female":"1","bmi":"kg/m^2","glucose":"mg/dL","hba1c":"%"},
    "variables_order":variables,
    "law_proof":"mathematical_properties.md derives each mean/covariance from the same conditional equations in generator.py",
    "bindings":{"generator_sha256":digest(C/"generator.py"),"model_spec_sha256":digest(C/"model_spec.json"),"source_operators_sha256":digest(helper_path),"mathematical_properties_sha256":digest(C/"mathematical_properties.md")},
    "coefficients":co,"residual_variance":r ** 2,"source_contexts":contexts,
    "support":{"standardized_bmi_beta":us,"standardized_glucose_beta":vs,"standardized_hba1c_beta":ws,"bmi":bs,"glucose":gs,"target_hba1c":target_h},
    "structural_checks":{"positive_bmi":True,"positive_glucose_below126":True,"positive_hba1c":True,"positive_residual_variance":True,"positive_definite_source_covariances":True,"target_quota_total":3000},
    "limitations":"These checks demonstrate exact nominal projections of assumed source laws. They do not reconstruct source survey/IPD, validate transport, fit Pani ageband means, or observe target outcomes.",
}
(C/"analytic_results.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n",encoding="utf-8")
print(json.dumps({"status":"pass","coefficient_derivation":co,"support":result["support"],"projection_count":3},allow_nan=False))
