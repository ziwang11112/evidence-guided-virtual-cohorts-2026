"""Build a predeclared artificial-moment test; no clinical data or Agent code runs."""
from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
import numpy as np
ROOT=Path(__file__).resolve().parent
def write(name,obj):
    path=ROOT/name;path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("x",encoding="utf8") as f: json.dump(obj,f,indent=2,allow_nan=False);f.write("\n")
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
cols=["Z","X1","X2","Y"]
# Artificial benchmark specification chosen before any constructor output.
R=np.array([[1,.3,.15],[.3,1,.75],[.15,.75,1.]])
b=np.array([.25,.65,-.4])
c=R@b
V=np.block([[R,c[:,None]],[c[None,:],np.ones((1,1))]])
assert np.linalg.eigvalsh(V).min()>0
pop="Artificial standardized four-variable population P0; exact population moments; no patients or transport"
base={"selection":[],"missing_policy":"error","unit":"1"}
checks=[]
for name in cols:
    checks.extend([{"id":"mean_"+name,"report":"M","estimate":0.0,"operator":dict(base,kind="mean",column=name)},
                   {"id":"sd_"+name,"report":"M","estimate":1.0,"operator":dict(base,kind="sd",column=name)}])
for i,j in [(0,1),(0,2),(1,2)]:
    checks.append({"id":"r_"+cols[i]+"_"+cols[j],"report":"C","estimate":float(V[i,j]),
                   "operator":dict(base,kind="correlation",x=cols[i],y=cols[j])})
for label,indices in [("A",[0,1]),("B",[0,2])]:
    vals=np.linalg.solve(V[np.ix_(indices,indices)],V[indices,3])
    for idx,val in zip(indices,vals):
        checks.append({"id":"report_"+label+"_"+cols[idx],"report":label,"estimate":float(val),
          "operator":dict(base,kind="ols_coefficient",outcome="Y",predictors=[cols[k] for k in indices],
                          term=cols[idx],include_intercept=True)})
source={"schema_version":1,"population":pop,"units":{c:"1" for c in cols},
 "origin":"Artificial benchmark reports, not literature extractions or independent clinical studies",
 "uncertainty":"Exact population moments for an implementation mechanism test, not sample estimates",
 "reports":{"M":"Marginal means and SDs of all four measurements",
            "C":"Predictor Pearson correlations in P0",
            "A":"OLS Y on intercept, Z and X1 in P0",
            "B":"OLS Y on intercept, Z and X2 in P0"},
 "checks":checks}
write(Path("SOURCE.json"),source)
write(Path("custodian/TRUTH.json"),{"columns":cols,"mean":[0.,0.,0.,0.],"covariance":V.tolist(),
 "scope":"Artificial benchmark only; no raw clinical data","fixture_construction":{"predictor_correlation":R.tolist(),"joint_beta":b.tolist(),"residual_variance":float(1-b@R@b)}})
protocol={"schema_version":1,"columns":cols,"authors":["O1","O2","C1","C2"],"seeds":[8101,8102,8103],"n_rows":10000,
 "max_final_tables":12,"source_file":"SOURCE.json","population":pop,
 "limits":{"timeout_seconds":45,"memory_mb":1536,"output_bytes":16000000,"log_bytes":50000},
 "purpose":"Necessity gate for a joint-evidence reconciliation instruction; no clinical utility or superiority claim",
 "arms":{"O":"Ordinary evidence-based construction","C":"Same evidence plus explicit joint-consistency requirement"},
 "independent_constructions_per_arm":2,"revision_rounds":0,"sampling_trials_before_seal":0,
 "primary":["joint OLS coefficient errors, standardized by predictor SD/outcome SD","absolute log ratio of joint residual SD"],
 "diagnostics":["all 15 supplied source statistics","marginal variances","finite output","positive covariance spectrum","design rank"],
 "aggregation":"Show every construction and seed; construction-level mean and range across seeds; no pooled-row sample size or p-value",
 "stop_rule":"One batch, failures retained; no additional authors/cases or tuning to output. If ordinary construction already succeeds, do not add the reconciliation component on this evidence.",
 "interpretation":"Two constructors per arm are descriptive. Requests differ by instructions, not a new mathematical algorithm; seeds are nested. This population intentionally removes clinical transport and extraction uncertainty.",
 "information_boundary":"Fresh constructors see own REQUEST.txt and SOURCE.json only; custodian/evaluator/protocol outcomes and prior project results prohibited. This is instruction-level LLM separation, not filesystem isolation.",
 "execution_boundary":"Existing WSL/bubblewrap worker; no host execution of authored code; controller and statistic diagnostics separately versioned."
}
write(Path("PROTOCOL.json"),protocol)
common="""You are an independent scientific data constructor in a small artificial mechanism test.
Read ONLY SOURCE.json and REQUEST.txt in your assigned bundle. Do not read project README, other bundles, custodian, evaluator, previous experiments or conversation history. No web search: these are complete artificial reports, not biomedical literature.
Goal: construct a stochastic whole-cohort generator for columns Z,X1,X2,Y in that exact order, all numeric dimensionless values. The scientific user wants joint OLS Y on Z,X1,X2 with an intercept and the residual standard deviation, as well as the supplied source analyses. No individual measurements are available.
SOURCE.json contains exact population summary statistics from reports about the SAME artificial population. Keep each reported adjustment set and statistic definition. You choose the distributional family and all scientific structure/parameters using these inputs; there is no prescribed relation sign or generator family.
Write exactly generator.py, model_spec.json and decision.json in this bundle. generator.py defines generate(n,rng,spec), returning a pandas.DataFrame with those four columns and n rows; rng is the supplied numpy.random.Generator, spec is your JSON model specification. Use only numpy/pandas/stdlib; no files/network/subprocess, no RNG reseeding, no imports from the project. Put scientific numeric parameters in model_spec.json and use them.
decision.json: cite source-check IDs used, separate derived parameters from assumptions, describe population applicability and unassessed uses, and record actual checks. Give concise scientific rationale, not hidden reasoning traces.
You may do deterministic algebra and static checks using the permitted source information. Do not execute your generator or create trial/sample tables. No source-feedback or revision round in this test. The controller will freeze all four submissions before generating the twelve final tables. Do not inspect any final outputs.
"""
extra="""
Additional requirement for this arm: explicitly reconcile all adopted numerical evidence within one joint probability law. Check that the law can simultaneously imply the supplied analyses with their stated adjustment sets and the supplied variances. Account for explained and residual variation together; do not treat their numerical choices as unrelated. Record the deterministic consistency calculations or a concrete unresolved incompatibility. No particular solver, distribution family or desired analysis result is prescribed.
"""
for author in protocol["authors"]:
    dest=ROOT/"bundles"/author;dest.mkdir(parents=True,exist_ok=False)
    (dest/"SOURCE.json").write_bytes((ROOT/"SOURCE.json").read_bytes())
    (dest/"REQUEST.txt").write_text(common+(extra if author.startswith("C") else ""),encoding="utf8")
write(Path("DESIGN_LOCK.json"),{"created_utc":datetime.now(timezone.utc).isoformat(),
 "author_outputs_present":False,
 "records":{str(f.relative_to(ROOT)).replace("\\","/"):sha(f) for f in [Path(__file__),ROOT/"SOURCE.json",ROOT/"PROTOCOL.json",ROOT/"custodian/TRUTH.json",*sorted((ROOT/"bundles").glob("*/REQUEST.txt")),*sorted((ROOT/"bundles").glob("*/SOURCE.json"))]}})
print("Created immutable artificial design and four source-only bundles; no sampling.")

