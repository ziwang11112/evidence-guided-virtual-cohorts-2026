"""Source-bounded preparation; constructs covariates and text artifacts, NEVER imports generator.
Run with Python + numpy/pandas/scipy. All input paths are explicitly admitted by the task.
"""
import copy
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import least_squares
from scipy.stats import beta, norm

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parent.parent
SEED = 130117
rng = np.random.default_rng(SEED)

def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def write(name, value):
    p = HERE / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

task = read(BUNDLE / "task.json")
registry = read(BUNDLE / "registry.json")
control = read(BUNDLE / "allowed_inputs/controller_contract.json")
thai = read(BUNDLE / "sources/thai2005.json")
gallagher = read(BUNDLE / "sources/gallagher2000.json")
items = []

def evidence(id, source, locator, variables, kind, estimate, unit, selection,
             adjustment=None, applicability="Reported original quantity; uncertainty not reported.", statistic_name=None):
    obj = dict(id=id, source_id=source, locator=locator, variables=variables, kind=kind,
               estimate=estimate, unit=unit, uncertainty={"kind":"not_reported"},
               adjustment=adjustment or [], selection=selection, applicability=applicability)
    if statistic_name is not None:
        obj["statistic_name"] = statistic_name
    items.append(obj)
    return id

sources=[]
for sid, raw in [("thai2005",thai),("gallagher2000",gallagher)]:
    reg = next(x for x in registry["artifacts"] if x["source_id"] == sid)
    sources.append(dict(id=sid, identifier=raw["citation"]+" DOI: "+raw["doi"],
        population=json.dumps(raw["population"],ensure_ascii=False),
        measurement=json.dumps(raw["measurement"],ensure_ascii=False),
        cohort_ids=["rural_Thai_2005" if sid=="thai2005" else "Gallagher_US_UK_Japan_2000"],
        artifacts=[{"path":reg["path"],"sha256":reg["sha256"]}]))

for row in thai["summary_moments"]:
    prefix="thai_"+row["context"].replace(" ","_")
    for variable in ["age","bmi","bodyfat"]:
        for kind in ["mean","sd"]:
            evidence(prefix+"_"+variable+"_"+kind,"thai2005",thai["summary_locator"], [variable],kind,
                row[variable][kind]["value"],{"age":"years","bmi":"kg/m2","bodyfat":"%"}[variable],row["context"]+f"; n={row['n']}",
                applicability="Original mean or marginal SD, not a conditional intercept or residual SD. Development summaries overlap development equations/correlations; validation summaries are visible contextual evidence, not calibration or blind holdout.")
for row in thai["correlations"]:
    evidence("thai_"+row["context"].replace(" ","_")+"_bmi_bodyfat_r","thai2005",row["locator"],["bmi","bodyfat"],"correlation",row["value"]["value"],"1",row["context"],applicability="Unadjusted Pearson r, not Spearman. p<0.001; same development participants as margins and equation.")

coefficient_units={"intercept":"%","bmi":"% per kg/m2","age":"% per year","male":"% per male-code unit",
    "inv_bmi":"% per m2/kg","asian_inv_bmi":"% per m2/kg","male_inv_bmi":"% per m2/kg",
    "asian_age":"% per year","male_age":"% per year"}
for sid, raw, prefix in [("thai2005",thai,"thai"),("gallagher2000",gallagher,"gallagher")]:
    eq=raw["equations"][0]
    predictors=[x for x in eq["coefficient_order"] if x!="intercept"]
    for term, value in eq["coefficients"].items():
        evidence(prefix+"_coef_"+term,sid,eq["locator"],["bodyfat"]+([] if term=="intercept" else [term]),
            "ols_coefficient",value["value"],coefficient_units[term],eq["context"]+f"; n={eq['n']}",
            adjustment=[x for x in predictors if x!=term],
            applicability="Original printed DXA regression coefficient (reported string "+value["reported"]+"). Predictor units and original adjustment set retained. Coefficient SE/covariance unknown; same-cohort statistics are not independent. No standalone Asian intercept in Gallagher Equation 1.")

for row_index,row in enumerate(gallagher["group_counts_and_moments"]):
    prefix=f"gallagher_group{row_index+1}"
    selection=f"male={row['male']}; {row['source_ethnicity']}; n={row['n']}; site counts={row['site_counts']}"
    for variable in ["age","bmi"]:
        for kind in ["mean","sd"]:
            evidence(prefix+"_"+variable+"_"+kind,"gallagher2000",row["locator"],[variable],kind,row[variable][kind]["value"],
                     "years" if variable=="age" else "kg/m2",selection,
                     applicability="Original Table 2 covariate marginal moment; Table 1 composition. Outcome moments are unreported, not reconstructed evidence.")
    evidence(prefix+"_count","gallagher2000",row["locator"],["male","asian"],"reported_other",row["n"],"persons",selection,statistic_name="source sex-by-ethnicity sample size")

evidence("gallagher_see","gallagher2000",gallagher["equations"][0]["locator"],["bodyfat"],"reported_other",4.31,"percentage points","All 1626 participants",statistic_name="regression SEE",
    applicability="Reported model error, not coefficient precision or proof of a Gaussian/constant residual law. Used as residual scale anchor under A_residual.")
evidence("gallagher_multiple_R","gallagher2000",gallagher["equations"][0]["locator"],["bodyfat"],"reported_other",.90,"1","All 1626 participants",statistic_name="multiple R")
evidence("thai_development_R2","thai2005",thai["equations"][0]["locator"],["bodyfat"],"reported_other",.83,"1","Pooled development, n=223",statistic_name="regression R squared")
evidence("thai_validation_r","thai2005",thai["validation"]["locator"],["bodyfat"],"reported_other",.93,"1","Pooled validation, n=213",statistic_name="predicted-measured Pearson r",applicability="Context only. Visible source validation is not blind holdout and is excluded from fitting.")
for name,value in [("loa_lower",-8.9),("loa_upper",8.6),("bias_body",.16),("bias_ci_lower",-.75),("bias_ci_upper",.44),("bias_table",-.2)]:
    evidence("thai_validation_"+name,"thai2005",thai["validation"]["locator"],["bodyfat"],"reported_other",value,"percentage points","Pooled validation, n=213",statistic_name=name,
       applicability="Unreplayed contextual original. LoA are mean difference +/-2 SD, not mean confidence limits. Measured minus predicted orientation. Printed signed bias conflict unresolved; no numerical repair or calibration.")
for row in thai["diagnostic_results"]["rows"]:
    for name in ["observed_obese_n","observed_prevalence_percent","sensitivity","specificity","positive_predictive_value","negative_predictive_value"]:
        value=row[name] if name=="observed_obese_n" else row[name]["value"]
        evidence(f"thai_validation_sex{row['male']}_{name}","thai2005",thai["diagnostic_results"]["locator"],["bodyfat"],"reported_other",value,
            "persons" if name=="observed_obese_n" else "%" if name=="observed_prevalence_percent" else "1",f"Validation male={row['male']}; n={row['n']}",statistic_name=name,
            applicability="Unreplayed context; DXA >25% men, >35% women. Sparse male events and operating characteristics do not fully reconcile; do not manufacture classification counts.")
for name,value in [("male",9.2),("female",40.0)]:
    evidence("thai_full_cohort_"+name+"_prevalence","thai2005",thai["contextual_full_cohort_outcome_prevalence"]["locator"],["bodyfat"],"proportion",value,"%","Full-cohort "+name,
        applicability="Context only; >=25% men, >=35% women. Distinct population and threshold from validation table.")
for name,value in [("bmi_ge30",0.),("bmi_ge25",15.)]:
    evidence("thai_full_cohort_"+name,"thai2005",thai["population"]["bmi_prevalence_locator"],["bmi"],"proportion",value,"%","Entire cohort, n=436",
        applicability="Original full-cohort support/prevalence. Zero BMI>=30 constrains development support. Rounded 15% BMI>=25 is not a development-sample fitting target.")
for i,row in enumerate(thai["within_validation_comparisons"]["rows"]):
    for name,value in [("r",row["r"]["value"]),("mean_difference",row["mean_difference_pp"]["value"]),("loa_lower",row["loa_pp"][0]["value"]),("loa_upper",row["loa_pp"][1]["value"])]:
        evidence(f"thai_comparison{i+1}_{name}","thai2005","Table 4",["bodyfat"],"reported_other",value,"1" if name=="r" else "percentage points",row["paper_label"]+" on same validation participants",statistic_name=name,
            applicability="Context only; cited comparison equation tested by this paper, not independently verified alternative generator or independent evidence.")
for i,row in enumerate(gallagher["additional_DXA_relationships"]):
    evidence(f"gallagher_additional_context{i+1}","gallagher2000",row["locator"],["bodyfat","bmi"],"contextual",None,"",row.get("context","Site/sex groups"),
        applicability="Unreplayed original reported relationship, preserving signs and ambiguity: "+json.dumps(row,ensure_ascii=False))
for sid,raw in [("thai2005",thai),("gallagher2000",gallagher)]:
    evidence(sid+"_context","thai2005" if sid=="thai2005" else "gallagher2000","Methods, tables and reporting notes as located in admitted extract",[],"contextual",None,"","All relevant source participants",
        applicability="Original support, exclusion, overlap and reporting limitations: "+json.dumps({k:raw[k] for k in (["population","measurement","split","exclusions","reporting_notes"] if sid=="thai2005" else ["population","measurement","overlap","exclusions","reporting_notes"])},ensure_ascii=False))
write("evidence.json",dict(schema_version=1,sources=sources,items=items))

assumptions = {
"A_domain":"Computational domain age 18-97 years, BMI 14-35 kg/m2, male and Asian codes 0/1, bodyfat 0-100%. This deliberately covers source and qualification supports without editing target eligibility. Gallagher minimum age18 and BMI14 and Thai minimum BMI14 are assumed numerical support endpoints; reported Thai age20-84, zero BMI>=30, and Gallagher BMI<=35/max age97 are retained. Domain is not established validity.",
"A_shape":"Age and Gallagher BMI use bounded beta midpoint quantiles matching reported means/sample SDs. Thai BMI uses a fixed15% upper component uniform on25-29.999 and85% lower component beta on14-24.999, with lower moments derived to match the total group's printed mean/sample SD. Applying the full-cohort rounded15% prevalence to each development sex is an explicit scenario, not an identified subgroup fact or outcome calibration constraint. This avoids a single-beta shape implying more development overweight cases than the entire cohort reports. Female lower-component shape can be strongly U-shaped; source shape is unknown and must be sensitivity-tested. Bounds are assumed supports, not observed minima/maxima.",
"A_dependence":"Unknown within-sex/group age-BMI dependence is fixed as a Gaussian rank-copula scenario: latent correlation -0.15 in Thai development and +0.10 in each Gallagher sex/ethnicity group. Realized Pearson correlations are reported. These are assumptions, not inferred source facts, and cannot be optimized. Alternative copula correlations/shapes would be a separate scientific sensitivity scenario.",
"A_composition":"Thai development reconstruction uses 40 times each reported sex count (98,125), total8920; Gallagher uses six times each of its six sex/ethnicity counts, total9756. These are integration rows, not additional evidence or reconstructed people. Non-Asian White and African-American memberships determine covariate mixtures only and are not additional generator inputs.",
"A_measurement":"Identity DXA percentage mapping across Thai Lunar DPX-IQ and Gallagher US Lunar DPX3.6, UK Hologic QDR1000, Japanese Lunar DPX-L1.3z is an explicit unverified transport assumption. No device equivalence or BCA correction is claimed; no four-compartment endpoint is substituted.",
"A_transport":"One conditional law applies to every row using only age, BMI, male and asian. Gallagher Equation1 is the portable nonlinear baseline. For asian=1, a convex blend toward the Thai age/BMI/sex equation expresses partial transport of Thai evidence; it cannot distinguish Thai from Japanese because no allowed covariate does. Asian here denotes the supplied study indicator, not ancestry biology; Japanese ethnicity is confounded with site/device. Non-Asian White and Black effects are pooled as in the available equation. No source ID, row ID or row count changes the law.",
"A_residual":"A beta distribution on 0-100% preserves the conditional location and adds individual variation with variance anchored to Gallagher SEE4.31 squared. Female SD is fixed at1.10 times male SD as an explicit heteroscedastic scenario suggested, not identified, by Thai larger female marginal variation. Common residual_scale starts1.0. Marginal Thai SD is never used as residual SD. Residual beta form is assumed, not reported. Model/evidence/transport uncertainty is not represented by these draws.",
"A_boundary":"Raw regression location is bounded to [0.5,99.5] percentage points and residual variance capped at95% of mean*(100-mean) to permit a valid beta law across declared support. These numerical physiological guards can bend published linear coefficients near extreme low BMI; replay must retain resulting discrepancies. They are not evidence-derived tail estimates.",
"A_calibration":"Four top-level scalar whitelist entries: asian_blend .35, bounds0-.8, step.15 (partial pooling sensitivity, not probability); level_shift0 pp, bounds-3..3 step1; male_shift0 pp, bounds-3..3 step1 (small shared location discrepancies); residual_scale1, bounds.75..1.4 step.15 (SEE-based residual sensitivity). Bounds/steps are engineering scenario choices, not confidence intervals. Order gives all four a +/- first comparison within9 trials. Context shapes, copula correlations, mixture counts, coefficient structure, female ratio and guards remain fixed.",
"A_limits":"Source agreement only. All18 required diagnostics stay visible, even if incompatible. Thai validation and extra Gallagher summaries are visible contextual evidence, not fitting constraints/holdout. Unknown coefficient covariance/SE and reconstruction error preclude likelihood weights; supplied scales are engineering units. Qualification grid is invented and contains no patient outcomes; no target validation is claimed."
}
params={"asian_blend":.35,"level_shift":0.,"male_shift":0.,"residual_scale":1.,
    "gallagher_coefficients":{k:v["value"] for k,v in gallagher["equations"][0]["coefficients"].items()},
    "thai_coefficients":{k:v["value"] for k,v in thai["equations"][0]["coefficients"].items()},
    "residual_base_sd":4.31,"female_sd_ratio":1.10,"mean_floor":.5,"mean_ceiling":99.5,"variance_fraction_cap":.95,
    "conditional_form":"Gallagher inverse-BMI plus Asian-only convex Thai blend and shared level/male shifts; bounded beta individual variation"}
prov={}
for key in params:
    eids=[]
    aids=["A_transport","A_calibration"]
    desc="Explicit fixed scientific scenario; see assumptions."
    if key=="gallagher_coefficients":
        eids=["gallagher_coef_"+x for x in params[key]]; aids=["A_transport","A_measurement"]; desc="Exact printed DXA Equation1; original seven predictors, no standalone Asian intercept."
    elif key=="thai_coefficients":
        eids=["thai_coef_"+x for x in params[key]]; aids=["A_transport","A_measurement"]; desc="Exact Thai development BMI-age-sex coefficients; not subgroup marginal means."
    elif key in ["residual_scale","residual_base_sd","female_sd_ratio"]:
        eids=["gallagher_see","thai_development_men_bodyfat_sd","thai_development_women_bodyfat_sd"]; aids=["A_residual","A_calibration"]; desc="SEE anchors4.31 pp. Female/male1.10 and permitted residual scaling are assumptions; outcome SDs are contextual evidence of differing marginal spread, never equated to residual SD."
    elif key in ["mean_floor","mean_ceiling","variance_fraction_cap"]:
        aids=["A_boundary"]; desc="Fixed bounded-output feasibility guard, not fitted source statistic."
    else:
        eids=["thai_coef_bmi","gallagher_coef_inv_bmi"]
    prov[key]=dict(evidence_ids=eids,assumption_ids=aids,derivation=desc)
write("model_spec.json",dict(parameters=params,assumptions=[dict(id=k,description=v) for k,v in assumptions.items()],parameter_provenance=prov))

def marginal(n, mean, sd, lo, hi):
    p=(np.arange(n)+.5)/n
    center=(mean-lo)/(hi-lo)
    v=(sd/(hi-lo))**2
    k=center*(1-center)/v-1
    initial=np.log([center*k,(1-center)*k])
    def residual(logab):
        values=lo+(hi-lo)*beta.ppf(p,*np.exp(logab))
        return np.array([(values.mean()-mean)/sd,(values.std(ddof=1)-sd)/sd])
    result=least_squares(residual,initial,xtol=1e-13,ftol=1e-13,gtol=1e-13,max_nfev=100)
    assert result.success and np.max(np.abs(residual(result.x)))<1e-9
    return lo+(hi-lo)*beta.ppf(p,*np.exp(result.x)),np.exp(result.x).tolist()

diagnostics={"seed":SEED,"kind":"covariate_only_reconstruction","outcomes_generated":False,"groups":[]}
def group(row,n,age_bounds,bmi_bounds,rho,context,label):
    a,ashape=marginal(n,row["age"]["mean"]["value"],row["age"]["sd"]["value"],*age_bounds)
    if context=="thai_development":
        nhigh=int(round(.15*n))
        nlow=n-nhigh
        high=25+(29.999-25)*(np.arange(nhigh)+.5)/nhigh
        bm=row["bmi"]["mean"]["value"]
        bs=row["bmi"]["sd"]["value"]
        lowmean=(n*bm-high.sum())/nlow
        lowvar=((n-1)*bs*bs+n*bm*bm-np.sum(high*high)-nlow*lowmean*lowmean)/(nlow-1)
        low,bshape=marginal(nlow,lowmean,np.sqrt(lowvar),14,24.999)
        b=np.concatenate([low,high])
        assert abs(b.mean()-bm)<1e-8 and abs(b.std(ddof=1)-bs)<1e-8
    else:
        b,bshape=marginal(n,row["bmi"]["mean"]["value"],row["bmi"]["sd"]["value"],*bmi_bounds)
    z=norm.ppf((np.arange(n)+.5)/n)
    latent=rho*z+np.sqrt(1-rho*rho)*rng.normal(size=n)
    ranks=np.argsort(np.argsort(latent))
    b=b[ranks]
    d=dict(context=context,label=label,reported_n=row["n"],integration_n=n,male=row["male"],asian=row.get("asian",1),latent_correlation=rho,
           actual_age_bmi_pearson=float(np.corrcoef(a,b)[0,1]),age_beta_shapes=ashape,bmi_beta_shapes=bshape,
           bmi_shape="15% uniform25-29.999 plus85% moment-matched beta14-24.999" if context=="thai_development" else "bounded beta",
           bmi_ge25_fraction=float(np.mean(b>=25)),bmi_ge30_count=int(np.sum(b>=30)))
    for name,v in [("age",a),("bmi",b)]:
        d[name]={"mean":float(v.mean()),"sample_sd":float(v.std(ddof=1)),"minimum":float(v.min()),"maximum":float(v.max()),
                 "reported_mean":row[name]["mean"]["value"],"reported_sd":row[name]["sd"]["value"]}
    diagnostics["groups"].append(d)
    return pd.DataFrame(dict(age=a,bmi=b,male=row["male"],asian=row.get("asian",1)))

def finalize(frames,name):
    f=pd.concat(frames,ignore_index=True)
    f=f.iloc[rng.permutation(len(f))].reset_index(drop=True)
    f.insert(0,"id",[f"cov{i+1:06d}" for i in range(len(f))])
    f["inv_bmi"]=1/f.bmi
    f["male_inv_bmi"]=f.male/f.bmi
    f["asian_inv_bmi"]=f.asian/f.bmi
    f["male_age"]=f.male*f.age
    f["asian_age"]=f.asian*f.age
    assert list(f.columns)==[c["name"] for c in task["columns"] if c["role"]!="generated"]
    assert len(f)<=12000 and "bodyfat" not in f
    p=HERE/"source_contexts"/(name+".csv")
    p.parent.mkdir(parents=True,exist_ok=True)
    f.to_csv(p,index=False,float_format="%.17g")
    return p,f

thai_path,thai_frame=finalize([group(r,r["n"]*40,(20,84),(14,29.999),-.15,"thai_development",r["context"]) for r in thai["summary_moments"][:2]],"thai_development")
gall_path,gall_frame=finalize([group(r,r["n"]*6,(18,97),(14,35),.10,"gallagher_full",r["source_ethnicity"]+f" male={r['male']}") for r in gallagher["group_counts_and_moments"]],"gallagher_full")
diagnostics["context_totals"]={"thai_development":len(thai_frame),"gallagher_full":len(gall_frame)}
diagnostics["thai_development_bmi_ge25_fraction"]=float(np.mean(thai_frame.bmi>=25))
diagnostics["note"]="The reconstructed development BMI>=25 fraction15% applies the rounded full-cohort margin to each development sex as an explicit, unidentified shape scenario. It is not additional source evidence or an outcome fitting constraint. All Thai rows BMI<30. Shapes/covariance remain assumption-dependent."
write("covariate_diagnostics.json",diagnostics)

def columns(age_min,age_max,bmi_min,bmi_max,asian):
    cols=copy.deepcopy(task["columns"])
    for c in cols:
        if c["name"]=="age": c.update(minimum=age_min,maximum=age_max)
        if c["name"]=="bmi": c.update(minimum=bmi_min,maximum=bmi_max)
        if c["name"]=="asian": c["categories"]=asian
    return cols

def check(eid,kind,unit,selection=None,**kwargs):
    return dict(id=eid,evidence_id=eid,status="approximate",operator=dict(kind=kind,unit=unit,selection=selection or [],missing_policy="error",**kwargs),
        assumption_ids=["A_transport","A_residual","A_boundary"],reason="Original statistic and variable/adjustment units retained; covariates and cross-study DXA transport are approximations. Numerical discrepancy remains diagnostic.")

tchecks=[]
for sex,name in [(1,"men"),(0,"women")]:
    for kind in ["mean","sd"]:
        tchecks.append(check("thai_development_"+name+"_bodyfat_"+kind,kind,"%",[{"column":"male","op":"eq","value":sex}],column="bodyfat"))
    tchecks.append(check("thai_development_"+name+"_bmi_bodyfat_r","correlation","1",[{"column":"male","op":"eq","value":sex}],x="bmi",y="bodyfat"))
for term in thai["equations"][0]["coefficient_order"]:
    tchecks.append(check("thai_coef_"+term,"ols_coefficient",coefficient_units[term],outcome="bodyfat",predictors=["bmi","age","male"],term=term,include_intercept=True))
gchecks=[]
gpredictors=[x for x in gallagher["equations"][0]["coefficient_order"] if x!="intercept"]
for term in gallagher["equations"][0]["coefficient_order"]:
    gchecks.append(check("gallagher_coef_"+term,"ols_coefficient",coefficient_units[term],outcome="bodyfat",predictors=gpredictors,term=term,include_intercept=True))
contexts=[]
for id,pop,path,cols,checks in [
    ("thai_development","Thai rural development only:98 men/125 women, integration replication40; age20-84, BMI14-29.999 assumed lower bound",thai_path,columns(20,84,14,29.999,[1]),tchecks),
    ("gallagher_full","Gallagher full six sex-by-ethnicity groups; original counts replicated6, adult age18-97 and BMI14-35 with assumed lower bounds",gall_path,columns(18,97,14,35,[0,1]),gchecks)]:
    contexts.append(dict(id=id,population=pop,reason="Reported covariate moments/composition reconstructed with bounded beta marginals and a fixed copula scenario; not source IPD.",columns=cols,
        assumption_ids=["A_domain","A_shape","A_dependence","A_composition","A_measurement"],
        measurement=dict(mode="identity",description=assumptions["A_measurement"]),
        input=dict(path=path.relative_to(HERE).as_posix(),sha256=digest(path),origin="declared_source_covariates"),checks=checks))
replay=dict(schema_version=2,model_domain=dict(description=assumptions["A_domain"],columns=columns(18,97,14,35,[0,1]),assumption_ids=["A_domain"]),contexts=contexts)
write("source_replay_v2.json",replay)
constraints=[]
for context in contexts:
    for c in context["checks"]:
        op=c["operator"]
        scale=control["loss_scales"]["coefficient_by_term"][op["term"]] if op["kind"]=="ols_coefficient" else control["loss_scales"][op["kind"]]
        constraints.append(dict(context_id=context["id"],check_id=c["id"],scale=scale,
            scale_reason="Fixed controller term-specific engineering scale in the statistic's declared units; not sampling precision, likelihood, independence or clinical equivalence."))
write("proposed_calibration_plan.json",dict(schema_version=1,parameters=[
    dict(name="asian_blend",lower=0.,upper=.8,step=.15),dict(name="level_shift",lower=-3.,upper=3.,step=1.),
    dict(name="male_shift",lower=-3.,upper=3.,step=1.),dict(name="residual_scale",lower=.75,upper=1.4,step=.15)],
    constraints=constraints,fit_seeds=control["fit_seeds"],replay_seeds=control["replay_seeds"],
    optimizer=dict(method="bounded_coordinate_search",max_trials=9,shrink=.5,min_step_fraction=.01,target_loss=0.),
    execution=control["execution"],noncomputable="infeasible"))
write("checks.json",dict(scope="source_only",records=[
    dict(name="covariate_reconstruction",status="pass",detail="Executed preparer covariate arithmetic only; exact group moment checks, composition, support and no-outcome assertions passed. See covariate_diagnostics.json. No generator import or execution."),
    dict(name="generator_and_source_replay",status="not_computable",detail="Not executed by preparer. Controller must freeze and run isolated adapter; no source agreement or output validity asserted.")],
    artifacts=[dict(path="covariate_diagnostics.json",sha256=digest(HERE/"covariate_diagnostics.json"))]))
print(json.dumps({"prepared":str(HERE),"source_contexts":diagnostics["context_totals"],"evidence_items":len(items),"replay_checks":len(tchecks)+len(gchecks),"generator_executed":False}))
