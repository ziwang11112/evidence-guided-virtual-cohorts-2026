"""Closed-form model-law algebra only: no generator import, tables, or sampling."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import math
from pathlib import Path

directory = Path(__file__).resolve().parent
spec_path = directory / "model_spec.json"
p = json.loads(spec_path.read_text(encoding="utf-8"))["parameters"]
moments = {}
law_parameters = {}
for name in ("bmi", "hba1c"):
    m, s = p[name]["mean"], p[name]["sd"]
    k, theta = (m/s)**2, s*s/m
    assert k > 0 and theta > 0
    mean = k*theta
    second = k*(k+1)*theta*theta
    assert math.isclose(mean, m, rel_tol=1e-12)
    assert math.isclose(second - mean*mean, s*s, rel_tol=1e-10)
    moments[name] = {"mean":mean,"second_raw_moment":second,"variance":s*s,"support":"(0,infinity)"}
    law_parameters[name] = {"shape":k,"scale":theta}
g = p["glucose"]
w = g["upper"] - g["lower"]
f = (g["mean"]-g["lower"])/w
c = f*(1-f)/(g["sd"]/w)**2-1
alpha, beta = f*c,(1-f)*c
assert 0 < f < 1 and c > 0 and alpha > 0 and beta > 0
mean = g["lower"]+w*alpha/(alpha+beta)
variance = w*w*alpha*beta/((alpha+beta)**2*(alpha+beta+1))
assert math.isclose(mean,g["mean"],rel_tol=1e-12)
assert math.isclose(variance,g["sd"]**2,rel_tol=1e-12)
moments["glucose"] = {"mean":mean,"second_raw_moment":mean*mean+variance,"variance":variance,"support":"(0,126)"}
law_parameters["glucose"] = {"alpha":alpha,"beta":beta,"lower":g["lower"],"upper":g["upper"]}
bands = p["design"]["age_bands"]
age_mean = sum((lo+hi)/2 for lo,hi in bands)/len(bands)
age_second = sum(((hi-lo+1)**2-1)/12+((lo+hi)/2)**2 for lo,hi in bands)/len(bands)
moments["age"] = {"mean":age_mean,"second_raw_moment":age_second,"variance":age_second-age_mean**2,"support":"integer ages within the four task bands"}
female_mean = sum(p["design"]["female_values"])/len(p["design"]["female_values"])
female_second = sum(x*x for x in p["design"]["female_values"])/len(p["design"]["female_values"])
moments["female"] = {"mean":female_mean,"second_raw_moment":female_second,"variance":female_second-female_mean**2,"support":"{0,1}"}
assert len(bands)*len(p["design"]["female_values"])*p["design"]["rows_per_cell"]==p["design"]["n_rows"]
assert all(x["variance"] > 0 for x in moments.values())
assert all(math.isfinite(v) for x in moments.values() for k,v in x.items() if k != "support")
predictor_variances = {"age10":moments["age"]["variance"]/100,"female":moments["female"]["variance"],"bmi5":moments["bmi"]["variance"]/25,"glucose10":moments["glucose"]["variance"]/100}
result = {
    "kind":"deterministic_closed_form_task_law_calculation",
    "model_spec_sha256":hashlib.sha256(spec_path.read_bytes()).hexdigest(),
    "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "method":"Gamma and beta raw-moment identities and finite average over four discrete uniform age bands; no numerical quadrature, random draws, generator import or empirical table.",
    "law_parameters":law_parameters,"random_design_row_moments":moments,
    "cross_covariances":"Zero by explicit product-law assumption, not by a source finding.",
    "positive_centered_predictor_variances":predictor_variances,
    "population_projection_implications":{"Q1_age10":0.0,"Q2_bmi5":0.0,"Q3_bmi5":0.0,"Q2_minus_Q3_bmi5":0.0,"hba1c_residual_rms":p["hba1c"]["sd"],"interpretation":"Derived from this candidate law; not a target reference or empirical source result."},
    "checks":{"valid_distribution_shapes":True,"moment_identities":True,"finite_first_second_moments":True,"exact_design_allocation":True,"positive_predictor_variances":True},
    "source_validation":"unavailable; target law algebra is not source reconstruction"
}
(directory/"analytic_results.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8")
print(json.dumps({"status":"pass","scope":result["kind"],"checks":result["checks"]}))
