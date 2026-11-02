"""Create artificial metadata only. Never samples or writes individual rows."""
from pathlib import Path
import json, math, hashlib, sys
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PROJECT = ROOT.parents[1]
sys.path.insert(0, str(PROJECT))
from cohort_harness.contracts import validate_task, validate_evidence
from cohort_harness.lifecycle import _registry

ARMS = ("A", "B", "C", "D")

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")

def text_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(value.rstrip() + "\n")

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def sf(z, law):
    if law == "normal":
        return .5 * math.erfc(z / math.sqrt(2))
    if z < 0:
        return 1 - sf(-z, law)
    if z == 0:
        return .5
    w = 1 / z
    if z >= 8:
        # atan(w)-w/(1+w*w), without cancellation in its common leading term.
        value = sum(((-1) ** (k+1)) * (2*k)/(2*k+1) * w**(2*k+1)
                    for k in range(1, 20))
        return value / math.pi
    return (math.atan(w) - z/(1+z*z)) / math.pi

def reference(config):
    par = config["parameters"]; mu,a,b,d,sigma = [par[k] for k in ("mu","a","b","d","sigma")]
    p = config["target_p"]; q = config["analysis"]["quadrature"]
    xc,yc = [config["analysis"]["tail"][k] for k in ("x_cut","y_cut")]
    limit = q["normal_x_limit"]
    assert sigma > 0 and d != 0 and 0 < xc < limit
    source = {"g_mean":.5,"g_sd":.5,"x_mean":0.0,"x_sd":1.0,
              "y_mean":mu+a/2,"y_sd":math.sqrt(a*a/4+b*b+d*d+sigma*sigma),
              "cov_g_x":0.0,"cov_g_y":a/4,"cov_x_y":b}
    worlds = {}; convergences = []
    for label,sign in (("plus",1),("minus",-1)):
        groups = {str(g):{"x_mean":0.0,"x_sd":1.0,"intercept":mu+a*g,
                          "slope":b+sign*d*(2*g-1),"residual_sd":sigma}
                  for g in (0,1)}
        for error in ("normal","t3"):
            estimates = []
            for order in q["orders"]:
                nodes, weights = np.polynomial.legendre.leggauss(order)
                tails = []
                for lo,hi in ((xc,limit),(-limit,-xc)):
                    xs=(hi-lo)*nodes/2+(hi+lo)/2
                    integrand=[]
                    for x in xs:
                        probability = sum(((1-p) if g==0 else p) *
                            sf((yc-groups[str(g)]["intercept"]-groups[str(g)]["slope"]*float(x))/sigma,error)
                            for g in (0,1))
                        integrand.append(math.exp(-float(x)**2/2)/math.sqrt(2*math.pi)*probability)
                    tails.append(float((hi-lo)/2*np.dot(weights,integrand)))
                estimates.append({"order":order,"right_probability":tails[0],
                                  "left_probability":tails[1],"contrast":tails[0]-tails[1]})
            delta=max(abs(estimates[-1][k]-estimates[-2][k])
                      for k in ("right_probability","left_probability","contrast"))
            assert delta <= q["maximum_successive_difference"]
            convergences.append(delta)
            worlds[label+"_"+error] = {
                "sign":sign,"error_law":error,
                "primary_slope":b+sign*d*(2*p-1),"primary_intercept":mu+a*p,
                "target_y_mean":mu+a*p,
                "target_y_sd":math.sqrt(a*a*p*(1-p)+b*b+d*d+2*b*sign*d*(2*p-1)+sigma*sigma),
                "conditional":groups,
                "tail":{k:estimates[-1][k] for k in ("right_probability","left_probability","contrast")},
                "quadrature_checks":estimates,"successive_difference":delta}
    assert all(abs(worlds[s+"_normal"]["tail"]["contrast"]-worlds[s+"_t3"]["tail"]["contrast"])>1e-10
               for s in ("plus","minus"))
    return {"schema_version":1,"source":source,"worlds":worlds,
            "primary_plus_minus_contrast":worlds["plus_normal"]["primary_slope"]-worlds["minus_normal"]["primary_slope"],
            "reference_accuracy":{"method":"Gauss-Legendre deterministic integration at fixed orders",
                "max_last_order_difference":max(convergences),
                "per_one_sided_tail_truncation_bound":.5*math.erfc(limit/math.sqrt(2)),
                "contrast_truncation_bound":math.erfc(limit/math.sqrt(2)),
                "qualification":"Order agreement is an empirical numerical check, not a rigorous quadrature-error bound; truncation bound is analytic."},
            "law_caveat":"Standardized t3 has finite variance1 and infinite fourth moment. Neither residual law is revealed by the packets."}

COMMON = """# Artificial whole-cohort construction
This is an invented, dimensionless mechanism fixture, not a biomedical population,
paper, patient dataset or empirical study. Construct one joint table of g, x, y
for the population in task.json, with no individual observations supplied.
The intended use is descriptive associations and threshold questions.

You choose the scientific structure, parameters, distribution families and
implementation. Use only task.json, evidence.json, registry.json, evidence_note.md,
this instruction file, and the registered sources/ artifacts in this bundle,
plus the supplied harness contract/interface. Declare every unsupported choice
as an assumption. A source functional is not a full distribution. Do not infer
an error distribution merely from a residual SD or a linear conditional mean.

Deliver candidates/initial/{generator.py,model_spec.json,evidence.json,decision.md,checks.json}.
Copy evidence.json exactly. Use the existing strict schemas and the top-level
generate(observed, spec, seed) ABI returning a pandas DataFrame. observed is None.
The generator may use NumPy/Pandas and the supplied seed only; no file/network
access, hidden truth, other bundles, clinical data, or extra literature.
Metadata/schema/AST checks are allowed. Do not import/run the generator, create
trial rows, optimize against a hidden answer, or manufacture a freeze/approval.
The coordinator will freeze all four constructions before any scheduled output.
There is one construction and no source-feedback revision. No numeric feedback
is provided to you. Different scientific choices consistent with the packet
must be acknowledged; do not promise a uniquely identified joint law.
"""

def build(config, ref):
    population = ("Artificial target population with dimensionless g in {0,1} and continuous x,y; "
        "target Pr(g=1)=0.75 is a population proportion, not an exact finite-row quota. "
        "Only group composition changes from any supplied source to target: within each g, "
        "the joint law of x,y is stipulated invariant. No individual input, missingness or "
        "selection beyond the declared populations. This is a fictional controlled premise, "
        "not an empirically established transport assumption.")
    task={"schema_version":1,"task_id":"artificial-evidence-translation-pilot","mode":"whole_cohort",
        "population":population,"row_id":"row_id","n_rows":config["rows"],
        "columns":[{"name":"row_id","kind":"string","unit":"identifier","role":"identifier","nullable":False},
                   {"name":"g","kind":"integer","unit":"1","role":"generated","nullable":False,"minimum":0,"maximum":1},
                   *[{"name":v,"kind":"number","unit":"1","role":"generated","nullable":False} for v in ("x","y")]],
        "information_policy":{"mode":"published_evidence","excluded_cohorts":[],
            "allowed_tools":["admitted_source_read","contract_validation","request_metadata_clarification"]},
        "budget":{"source_queries":0,"source_downloads":0,"revisions":0}}
    def item(key,variables,kind,value,locator,selection,description,statistic_name=None):
        result={"id":key,"source_id":"S_ARTIFICIAL_SOURCE","locator":locator,"variables":variables,
            "kind":kind,"estimate":value,"unit":"1","uncertainty":{"kind":"not_reported"},
            "adjustment":[],"selection":selection,
            "applicability":description+" Exact fictional population functional, not a sampled estimate. "
                "No source n or sampling SE exists; not_reported encodes absence of estimator uncertainty. "
                "Finite generated tables need not equal population values exactly."}
        if statistic_name:result["statistic_name"]=statistic_name
        return result
    values=ref["source"]; selection="Artificial source with Pr(g=1)=0.5; no exclusions or missingness."
    base=[]
    for v in ("g","x","y"):
        base.append(item("E_"+v.upper()+"_MEAN",[v],"proportion" if v=="g" else "mean",
                         values[v+"_mean"],"Section S1: "+v+" population mean",selection,
                         "Unweighted population mean/proportion; no distribution family supplied."))
        base.append(item("E_"+v.upper()+"_SD",[v],"sd",values[v+"_sd"],
                         "Section S1: "+v+" population SD",selection,
                         "Between-individual population SD, not SE, residual SD, or parameter uncertainty."))
    for v,w in (("g","x"),("g","y"),("x","y")):
        base.append(item("E_COV_"+v.upper()+"_"+w.upper(),[v,w],"reported_other",values["cov_"+v+"_"+w],
                         "Section S1: population covariance "+v+","+w,selection,
                         "Covariance E[(V-EV)(W-EW)], equal source-population weighting; not a correlation or adjusted coefficient.",
                         "population_covariance"))
    note_common=("All values are invented exact population functionals. The harness enum published_evidence "
                 "is used solely to carry admitted artificial fixture records, not to assert publication. "
                 "No real citation, sample size, sampling uncertainty, quantile or full distribution is supplied. "
                 "Population SD describes individual dispersion. The visible packet does not prescribe a generator.")
    for arm in ARMS:
        bundle=ROOT/"bundles"/arm; (bundle/"candidates"/"initial").mkdir(parents=True,exist_ok=False)
        arm_task=json.loads(json.dumps(task)); evidence={"schema_version":1,"sources":[],"items":[]}
        registry={"artifacts":[]}; note=note_common
        if arm=="A":
            arm_task["information_policy"]["mode"]="prior_only"
            note+=" No numerical source information is provided in this packet; choices require explicit prior assumptions."
        else:
            items=json.loads(json.dumps(base))
            source_text=["# Artificial population-statistic note",
                         "Invented fixture only. This is not a paper, dataset release or clinical result.",
                         selection,"## S1: exact univariate and pairwise functionals"]
            source_text += [x["id"]+": "+format(x["estimate"],".17g")+"; "+x["locator"] for x in base]
            source_text += ["No normal, Gaussian-copula, residual-distribution or independence family is reported by S1."]
            if arm in ("C","D"):
                sign_name="plus" if arm=="C" else "minus"
                groups=ref["worlds"][sign_name+"_normal"]["conditional"]
                source_text += ["## S2: group-conditional population analysis",
                    "Within each g, E[y|x,g] is linear with the stated intercept/slope, and Var(y|x,g) "
                    "is the square of the stated residual SD for every x. This reports conditional first "
                    "and second moments, not a distribution for the errors or x. "
                    "The within-group x mean and population SD are stated separately. "
                    "Population OLS includes an intercept, uses x as the sole predictor, and has no weighting, "
                    "other adjustment, selection or missing-data processing. "
                    "Residual SD is sqrt(E[(y-intercept-slope*x)^2|g]), not a standard error."]
                for g in ("0","1"):
                    z=groups[g]; sel=selection+" Conditional on g="+g+"."
                    additions=[
                        item("E_G"+g+"_X_MEAN",["x"],"mean",z["x_mean"],"Section S2: g="+g+" x mean",sel,"Conditional x population mean."),
                        item("E_G"+g+"_X_SD",["x"],"sd",z["x_sd"],"Section S2: g="+g+" x SD",sel,"Conditional x population SD, not error SD."),
                        item("E_G"+g+"_Y_INTERCEPT",["y","x"],"reported_other",z["intercept"],"Section S2: g="+g+" y~1+x intercept",sel,"Population OLS y~1+x intercept; E[y|x,g] is linear.","population_OLS_intercept"),
                        item("E_G"+g+"_Y_SLOPE",["y","x"],"ols_coefficient",z["slope"],"Section S2: g="+g+" y~1+x x coefficient",sel,"Population OLS y~1+x x coefficient; no other covariates."),
                        item("E_G"+g+"_RESIDUAL_SD",["y","x"],"reported_other",z["residual_sd"],"Section S2: g="+g+" y~1+x residual SD",sel,"Conditional individual residual SD; Var(y|x,g) is constant at its square. No residual family is specified.","population_OLS_residual_SD")]
                    items+=additions
                    source_text += [x["id"]+": "+format(x["estimate"],".17g")+"; "+x["locator"] for x in additions]
            artifact=bundle/"sources"/"ARTIFICIAL_SOURCE.md"
            text_new(artifact,"\n\n".join(source_text))
            evidence={"schema_version":1,"sources":[{"id":"S_ARTIFICIAL_SOURCE",
                "identifier":"fixture:artificial-evidence-translation-v1",
                "population":selection,"measurement":"g,x,y are fictional dimensionless variables; definitions are exact mathematical population functionals.",
                "cohort_ids":["ARTIFICIAL_SOURCE_POPULATION"],"artifacts":[{"path":"sources/ARTIFICIAL_SOURCE.md","sha256":digest(artifact)}]}],"items":items}
            registry={"artifacts":[{"source_id":"S_ARTIFICIAL_SOURCE","path":"sources/ARTIFICIAL_SOURCE.md",
                "sha256":digest(artifact),"origin":"fixture","screening":"approved"}]}
        text_new(bundle/"BUILDER_BRIEF.md",COMMON)
        text_new(bundle/"evidence_note.md","# Evidence scope\n\n"+note)
        for name,obj in (("task.json",arm_task),("evidence.json",evidence),("registry.json",registry)):
            write_new(bundle/name,obj)
        validate_task(arm_task);validate_evidence(evidence,arm_task);_registry(bundle.resolve())
    # Exact common informational content, not equality of whole packet artifacts.
    docs=[read(ROOT/"bundles"/arm/"evidence.json") for arm in ("B","C","D")]
    assert docs[0]["items"]==docs[1]["items"][:len(base)]==docs[2]["items"][:len(base)]
    assert len({digest(ROOT/"bundles"/a/"BUILDER_BRIEF.md") for a in ARMS})==1
    return {arm:len(read(ROOT/"bundles"/arm/"evidence.json")["items"]) for arm in ARMS}

if __name__=="__main__":
    config=read(HERE/"LAW.json")
    ref=reference(config)
    write_new(HERE/"REFERENCE.json",ref)
    counts=build(config,ref)
    visible={}
    for arm in ARMS:
        for path in sorted((ROOT/"bundles"/arm).rglob("*")):
            if path.is_file():visible[path.relative_to(ROOT).as_posix()]=digest(path)
    private={path.relative_to(ROOT).as_posix():digest(path) for path in
             (HERE/"LAW.json",HERE/"REFERENCE.json",Path(__file__),HERE/"evaluate.py")}
    write_new(ROOT/"CUSTODY_COMMITMENT.json",{
        "schema_version":1,"status":"prepared_pending_independent_admission",
        "custodian_id":"/root/public_repository_audit",
        "visible_files":visible,"private_files":private,"commitments":{**visible,**private},
        "rows_per_output":config["rows"],"seeds":config["seeds"],"maximum_tables":12,
        "validation":{"task_evidence_registry_contracts":"pass","common_instructions_byte_identical":True,
            "common_source_marginal_pairwise_items_identical":True,
            "compatible_error_laws_preserve_visible_moments":True,"tail_contrasts_differ_between_error_laws":True,
            "deterministic_quadrature_order_check":"pass","rows_generated":0},
        "evidence_item_counts":counts,
        "custody":"Private law/reference/evaluator withheld from constructors/coordinator until all freezes and all12 outputs/failures complete. Reviewer may inspect under custody; hashes are procedural, not access-control isolation.",
        "limits":"Artificial translation/responsiveness pilot, one constructor per packet; no causal average evidence-value claim, no clinical law, no world-probability weights."})
    print(json.dumps({"status":"metadata_ready","bundles":list(ARMS),"evidence_item_counts":counts,
                      "visible_files":len(visible),"private_files":len(private),"rows_generated":0}))

