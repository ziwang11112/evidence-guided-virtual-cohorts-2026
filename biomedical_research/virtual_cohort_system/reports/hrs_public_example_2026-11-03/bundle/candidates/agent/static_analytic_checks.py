"""Static/analytic source checks only: never imports or calls generator.py."""
from pathlib import Path
from datetime import datetime, timezone
import ast
import hashlib
import json
import math
import numpy as np

candidate = Path(__file__).resolve().parent
bundle = candidate.parent.parent
p = json.loads((candidate / "model_spec.json").read_text())["parameters"]
evidence = json.loads((candidate / "evidence.json").read_text())
items = {i["id"]: i for i in evidence["items"]}
lines = (bundle / "sources/original/HRSmodels_20200902_fullDemoTable.txt").read_text(encoding="cp1252").splitlines()
results = []

def record(name, detail, **values):
    results.append({"name": name, "status": "pass", "detail": detail, "values": values})

# Parse, but neither import nor execute, the submitted generator.
tree = ast.parse((candidate / "generator.py").read_text())
compile(tree, "generator.py", "exec")
functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "generate"]
assert len(functions) == 1
args = functions[0].args
assert len(args.args) + len(args.posonlyargs) == 3
assert not args.vararg and not args.kwarg and not args.kwonlyargs
assert not any(isinstance(n, ast.AsyncFunctionDef) for n in tree.body)
imports = [n.names[0].name for n in tree.body if isinstance(n, ast.Import)]
assert imports == ["math", "numpy", "pandas"]
assert all(isinstance(n, (ast.Expr, ast.Import, ast.FunctionDef)) for n in tree.body)
assert all(isinstance(n.value, ast.Constant) and isinstance(n.value.value, str) for n in tree.body if isinstance(n, ast.Expr))
assert not any(isinstance(n, (ast.ImportFrom, ast.With, ast.AsyncWith)) for n in ast.walk(tree))
for n in ast.walk(tree):
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
        assert n.func.id not in {"open", "eval", "exec", "compile", "__import__"}
record("static_program_ABI_and_import_review", "AST parse/compile and import/call inspection only; no module import, function invocation or data generation.", positional_arguments=len(args.args), imports=imports)

# Compare all transcribed numeric model coefficients and SEs with original text.
checked = 0
for group,start,ids in [
    ("cses_model",85,["cses_intercept","cses_baseline_age60","cses_race_black"]),
    ("hba1c_model",42,["hba1c_"+t for t in p["hba1c_model"]["terms"]]),
    ("memory_model",114,["memory_"+t.replace(":","_by_") for t in p["memory_model"]["terms"]])
]:
    for i,eid in enumerate(ids):
        tokens=lines[start+i-1].split()
        reported_b,reported_se=float(tokens[1]),float(tokens[2])
        assert p[group]["coefficients"][i] == reported_b == items[eid]["estimate"]
        assert items[eid]["uncertainty"] == {"kind":"se","value":reported_se}
        checked += 1
for j,level in enumerate(["HS","LessThanHS"]):
    estimates=[float(x) for x in lines[64+j].split()[1:]]
    ses=[float(x) for x in lines[69+j].split()[1:]]
    assert p["education_model"]["coefficients"][j+1] == estimates
    for i,t in enumerate(p["education_model"]["terms"]):
        item=items["educ_"+level+"_"+t]
        assert item["estimate"] == estimates[i]
        assert item["uncertainty"] == {"kind":"se","value":ses[i]}
        checked += 1
assert p["cses_model"]["residual_sd"] == float(lines[90].split()[3])
assert p["hba1c_model"]["dispersion"] == float(lines[51].split()[-1].rstrip(")"))
assert p["memory_model"]["random_intercept_variance"] == float(lines[106].split()[2])
assert p["memory_model"]["random_slope_variance"] == float(lines[107].split()[1])
assert p["memory_model"]["random_effect_correlation"] == float(lines[107].split()[3])
assert p["memory_model"]["residual_variance"] == float(lines[108].split()[1])
record("numeric_transcription_against_original", "Compared submitted coefficients and their evidence SEs directly to separately parsed Windows-1252 original export; compared residual scales, variances, correlation and Gamma dispersion.", coefficient_SE_pairs=checked, scale_or_dispersion_values=6)

weights=[]
for i,c in enumerate(p["demographic_model"]["cells"]):
    tokens=lines[2+i].split()
    assert c["age_bin"] == int(tokens[1].replace("Agecat",""))
    assert c["sex"] == tokens[2].lower() and c["race"] == tokens[3].lower()
    assert c["count"] == int(tokens[4])
    weights.append(c["count"])
n=sum(weights)
assert n == 11509 == p["cohort_design"]["n_subjects"]
assert n*len(p["cohort_design"]["visit_times"]) == 46036
assert p["cohort_design"]["visit_times"] == [0,2,4,6]
assert all(w>0 for w in weights)
assert math.isclose(sum(w/n for w in weights),1.0,abs_tol=1e-15)
female=sum(c["count"] for c in p["demographic_model"]["cells"] if c["sex"]=="female")
black=sum(c["count"] for c in p["demographic_model"]["cells"] if c["race"]=="black")
record("demographic_counts_and_balanced_design", "Compared all 28 count/label cells to the original export and checked normalization and task row arithmetic; these are analytic sums, not realized samples.", subjects=n,rows=n*4,female=female,black=black)

mm=p["memory_model"]
v0,v1,rho,ve=[mm[k] for k in ["random_intercept_variance","random_slope_variance","random_effect_correlation","residual_variance"]]
cov=rho*math.sqrt(v0*v1)
sigma=np.array([[v0,cov],[cov,v1]])
transform=np.array([[math.sqrt(v0),0],[rho*math.sqrt(v1),math.sqrt(v1)*math.sqrt(1-rho*rho)]])
assert np.allclose(transform@transform.T,sigma,rtol=1e-14,atol=1e-15)
eigenvalues=np.linalg.eigvalsh(sigma)
assert (eigenvalues>0).all() and ve>0
record("random_effect_covariance_identity", "Analytically verified the standard-normal linear transformation has the requested covariance and the covariance is positive definite; no random effects were sampled.", covariance=cov,eigenvalues=eigenvalues.tolist(),derived_SDs=[math.sqrt(v0),math.sqrt(v1),math.sqrt(ve)],determinant=float(np.linalg.det(sigma)))

phi=p["hba1c_model"]["dispersion"]
assert phi>0
# Symbolic normalized mean/variance identities, with mean represented as 1.
assert math.isclose((1/phi)*phi,1.0)
assert math.isclose((1/phi)*(phi**2),phi)
assert len(mm["terms"])==len(mm["coefficients"])==16
expected=["age60:"+t for t in mm["interaction_covariates"]]
assert mm["terms"][9:]==expected
assert p["education_model"]["coefficients"][0]==[0,0,0,0,0]
assert p["education_model"]["levels"]==["College","HS","LessThanHS"]
# Arbitrary nonclinical numerical probes of algebra only, not model outputs.
for a in [-1000.0,-0.25,0.0,0.75,1000.0]:
    under,over=min(a,0.0),max(a,0.0)
    assert under+over==a and under*over==0.0
logits=np.array([[0.0,1.0,-1.0],[1000.0,999.0,998.0],[-1000.0,0.0,1000.0]])
stable=np.exp(logits-logits.max(axis=1,keepdims=True))
probs=stable/stable.sum(axis=1,keepdims=True)
assert np.isfinite(probs).all() and (probs>=0).all() and np.allclose(probs.sum(axis=1),1.0)
record("Gamma_spline_softmax_and_design_algebra", "Verified Gamma normalized moment identities, full 16-term interaction ordering, reference-logit convention, and invented scalar/matrix numerical probes of spline and stable-softmax algebra. These probes do not invoke the generator or create any clinical table.", Gamma_shape=1/phi,memory_terms=mm["terms"],nonclinical_softmax_probe_count=len(logits))

bounds=np.array(p["age_model"]["bin_bounds"],dtype=float)
assert bounds.tolist()==[[50,55],[55,60],[60,65],[65,70],[70,75],[75,80],[80,100]]
assert bounds.min()==50 and bounds.max()==100
assert (50-60)/10==-1 and (100+6-60)/10==4.6
# Theoretical mixture moments are not simulated cohort diagnostics.
bin_weights=np.array(weights).reshape(7,4).sum(axis=1)/n
bin_means=bounds.mean(axis=1)
bin_vars=(bounds[:,1]-bounds[:,0])**2/12
mean=float(bin_weights@bin_means)
variance=float(bin_weights@(bin_vars+bin_means**2)-mean**2)
record("analytic_age_support_and_mixture", "Verified age support against task bounds and integrated the specified uniform demographic mixture analytically. No age observations were sampled and no coefficient was changed based on these moments.",baseline_age_mean=mean,baseline_age_SD=math.sqrt(variance),age60_range=[-1,4.6])

report={"created_utc":datetime.now(timezone.utc).isoformat(),"scope":"source_only_static_and_analytic","generator_imported":False,"generator_called":False,"HRS_table_generated":False,"clinical_model_fitted":False,"source_feedback_revisions":0,"results":results,"input_hashes":{name:hashlib.sha256((candidate/name).read_bytes()).hexdigest() for name in ["generator.py","model_spec.json","evidence.json"]},"read_set":["AUTHOR_TASK.md","task.json","registry.json","SOURCE_METADATA.json","sources/original/HRSmodels_20200902_fullDemoTable.txt","sources/original/HRS_sim_data_code_postGitHub_20200728.R","sources/original/RCTSim1_postGitHub_20200728.R","sources/original/RCTSim2_postGitHub_20200728.R","sources/original/README.md","sources/HRS_PUBLISHED_REFERENCES.json"],"interface_reads":["D:/Codex/home/skills/evidence-cohort-generation/SKILL.md","D:/Codex/home/skills/evidence-cohort-generation/references/harness-interface.md","cohort_harness/contracts.py","cohort_harness/lifecycle.py"]}
(candidate/"static_analytic_results.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
print(json.dumps({"checks":len(results),"status":"pass","HRS_table_generated":False,"clinical_model_fitted":False}))
