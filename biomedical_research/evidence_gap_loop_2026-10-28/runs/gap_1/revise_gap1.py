"""Source-only revision diagnostics and final artifact assembly for gap_1.

Only the assigned run's initial artifacts, approved evidence and review are read.
No target rows, target outcomes, controller outputs or other runs are used.
"""
from pathlib import Path
import copy
import hashlib
import json
import shutil
import numpy as np

RUN = Path(__file__).resolve().parent
INITIAL = RUN / "initial"
FINAL = RUN / "final"

def read(name):
    return json.loads((INITIAL / name).read_text(encoding="utf-8"))

spec = read("model_spec.json")
ledger = read("evidence.json")
p0 = spec["parameters"]
e_by_id = {e["id"]: e for e in ledger["evidence"]}
cells = copy.deepcopy(e_by_id["E_US_COVARIATES"]["reported"])
reported = e_by_id["E_US_MOMENTS"]["reported"]
source_moments = {s: reported[s] for s in ("male", "female")}
outcomes = {"male": [(51,16),(58,21),(42,14),(50,14)],
            "female": [(65,19),(62,17),(54,18),(59,20)]}
for sex in ("male", "female"):
    for cell, (mean, sd) in zip(cells[sex], outcomes[sex]):
        cell["hdl_mean"] = mean
        cell["hdl_sd"] = sd

def age_effect(a, p, factor=1.0):
    values=np.log(p["age_relative_means"])
    return factor*(np.interp(a,p["age_knots_years"],values)-np.interp(p["age_reference"],p["age_knots_years"],values))

def multipliers(cell, sex, p, rho=0.0, family="normal", factor=1.0, nodes=128):
    x,w=np.polynomial.hermite.hermgauss(nodes)
    z=np.sqrt(2)*x
    w=w/np.sqrt(np.pi)
    age=cell["age_mean"]+cell["age_sd"]*z
    g=age_effect(age,p,factor)
    b=p["bmi_log_slopes_by_sex"][sex]
    out=[]
    for power in (1,2):
        if family=="normal":
            conditional_bmi_mean=cell["bmi_mean"]+rho*cell["bmi_sd"]*z
            conditional_bmi_var=cell["bmi_sd"]**2*(1-rho**2)
            eb=np.exp(power*b*(conditional_bmi_mean-p["bmi_reference"])+(power*b)**2*conditional_bmi_var/2)
        elif family=="lognormal":
            lsd=np.sqrt(np.log1p((cell["bmi_sd"]/cell["bmi_mean"])**2))
            lmean=np.log(cell["bmi_mean"])-lsd**2/2
            bmi=np.exp(lmean+lsd*(rho*z[:,None]+np.sqrt(1-rho**2)*z[None,:]))
            eb=np.exp(power*b*(bmi-p["bmi_reference"]))@w
        else:
            raise ValueError(family)
        out.append(float(np.sum(w*np.exp(power*g)*eb)))
    return out

def closure(p,rho=0.0,family="normal",factor=1.0,nodes=128,reanchor=True):
    out={}
    revised=copy.deepcopy(p)
    for sex in ("male","female"):
        ms=np.array([multipliers(c,sex,p,rho,family,factor,nodes) for c in cells[sex]])
        weights=np.array([c["n"] for c in cells[sex]],float)
        weights=weights/weights.sum()
        m1,m2=weights@ms
        if reanchor:
            base=source_moments[sex]["mean"]/m1
            sigma2=np.log((source_moments[sex]["sd"]**2+source_moments[sex]["mean"]**2)/(base**2*m2))
            if sigma2<=0:
                raise ValueError("Specified slope exhausts observed marginal variance")
            revised["conditional_means_at_reference_by_sex"][sex]=float(base)
            revised["residual_log_sd_by_sex"][sex]=float(np.sqrt(sigma2))
        else:
            base=p["conditional_means_at_reference_by_sex"][sex]
            sigma2=p["residual_log_sd_by_sex"][sex]**2
        predictions=[]
        for cell,(cm1,cm2) in zip(cells[sex],ms):
            mu=base*cm1
            sd=np.sqrt(base**2*np.exp(sigma2)*cm2-mu**2)
            predictions.append({"group":cell["group"],"n":cell["n"],
                                "reported_mean":cell["hdl_mean"],"closure_mean":float(mu),"mean_difference":float(mu-cell["hdl_mean"]),
                                "reported_sd":cell["hdl_sd"],"closure_sd":float(sd),"sd_difference":float(sd-cell["hdl_sd"])})
        pooled_mu=base*m1
        pooled_var=base**2*np.exp(sigma2)*m2-pooled_mu**2
        var_mean=base**2*(m2-m1**2)
        residual=base**2*m2*np.expm1(sigma2)
        out[sex]={"cells":predictions,"pooled_mean":float(pooled_mu),"pooled_sd":float(np.sqrt(pooled_var)),
                  "mean_variance_component":float(var_mean),"average_conditional_variance":float(residual),
                  "variance_decomposition_error":float(var_mean+residual-pooled_var)}
    return revised,out

def mean_at(bmi,age,sex,p,factor=1.0):
    return float(p["conditional_means_at_reference_by_sex"][sex]*np.exp(p["bmi_log_slopes_by_sex"][sex]*(bmi-p["bmi_reference"])+age_effect(age,p,factor)))

_,baseline=closure(p0,reanchor=False)
closure_sensitivity=[]
for family in ("normal","lognormal"):
    for rho in (-0.5,0.0,0.5):
        params,result=closure(p0,rho=rho,family=family)
        _,coarse=closure(p0,rho=rho,family=family,nodes=64)
        max_delta=max(abs(c["closure_mean"]-b["closure_mean"]) for s in result for c,b in zip(result[s]["cells"],baseline[s]["cells"]))
        max_quad=max(abs(c["closure_mean"]-b["closure_mean"]) for s in result for c,b in zip(result[s]["cells"],coarse[s]["cells"]))
        closure_sensitivity.append({"bmi_marginal":family,"dependence":rho,
                                   "dependence_definition":"Within-cell Pearson correlation" if family=="normal" else "Within-cell Gaussian-copula correlation of normal age and log BMI; not raw Pearson correlation",
                                   "pooled_sex_moments_reanchored":True,"parameter_summary":{"intercepts":params["conditional_means_at_reference_by_sex"],"log_sd":params["residual_log_sd_by_sex"]},
                                   "largest_cell_mean_change_from_baseline":max_delta,"largest_cell_mean_quadrature_difference_64_vs_128":max_quad,"results":result})

age_sensitivity=[]
for factor in (-1.0,0.0,1.0,2.0):
    params,result=closure(p0,factor=factor)
    profiles=[]
    for sex in ("male","female"):
        values={str(a):mean_at(27,a,sex,params,factor) for a in (20,35,50,55.5,65.5,79)}
        ages=np.arange(20,80)
        mus=np.array([mean_at(27,a,sex,params,factor) for a in ages])
        slope=np.polyfit(ages,mus,1)[0]
        profiles.append({"sex":sex,"bmi":27,"mean_by_age":values,"mean_age_slope_over_balanced_invented_20_to_79_grid":float(slope),"age55p5_minus_age20":values["55.5"]-values["20"]})
    age_sensitivity.append({"age_log_effect_multiplier":factor,"assumed_not_estimated":True,"pooled_sex_moments_reanchored":True,"profiles":profiles,"source_pooled_and_variance_checks":{s:{k:v for k,v in result[s].items() if k!="cells"} for s in result}})

bmi_sensitivity=[]
for obese_representative in (28.0,30.0,33.0):
    params=copy.deepcopy(p0)
    for sex,ratio in (("male",43.25/51.92),("female",51.06/60.72)):
        params["bmi_log_slopes_by_sex"][sex]=float(np.log(ratio)/(obese_representative-21.25))
    params,result=closure(params)
    profiles=[]
    for sex in ("male","female"):
        vals={str(b):mean_at(b,50,sex,params) for b in (17,25,30,40,60,77.5)}
        profiles.append({"sex":sex,"age":50,"mean_by_bmi":vals,"mean40_minus_mean25":vals["40"]-vals["25"],"mean77p5_minus_mean25":vals["77.5"]-vals["25"]})
    bmi_sensitivity.append({"normal_representative":21.25,"obese_representative":obese_representative,"assumed_not_estimated":True,"reason_for_values":"28,30,33 satisfy the source obese category >=27 and span an assumed low-to-higher obese-category location; source did not report these means. This is not a confidence set.","bmi_log_slopes_by_sex":params["bmi_log_slopes_by_sex"],"pooled_sex_moments_reanchored":True,"profiles":profiles,"source_pooled_and_variance_checks":{s:{k:v for k,v in result[s].items() if k!="cells"} for s in result}})

table_rounding=[]
for sex in ("male","female"):
    n=np.array([c["n"] for c in cells[sex]],float)
    m=np.array([c["hdl_mean"] for c in cells[sex]],float)
    sd=np.array([c["hdl_sd"] for c in cells[sex]],float)
    pooled_mean=float(n@m/n.sum())
    pooled_sd=float(np.sqrt(np.sum((n-1)*sd**2+n*(m-pooled_mean)**2)/(n.sum()-1)))
    table_rounding.append({"sex":sex,"pooled_rounded_table2_mean":pooled_mean,"pooled_rounded_table2_sample_sd":pooled_sd,"more_precise_results_sex_mean":source_moments[sex]["mean"],"more_precise_results_sex_sd":source_moments[sex]["sd"],"interpretation":"Printed whole-number cell moments do not exactly pool to more precise Results values. Retain Results as primary sex anchors; cell mismatches of several mg/dL exceed the small pooling discrepancy."})

diagnostics={"scope":"Revision-only source and invented-profile calculations; no target rows or outcome results accessed.",
             "source_cell_reextraction":{"source_id":"S_US","locator":"PMC8818198 Table 2, n, Age, BMI and HDL-C rows (not non-HDL-C or HDLperox)","cells":cells,"mean_sd_units":"mg/dL","cell_values_rounded_in_source":True},
             "baseline_cell_diagnostics":{"operator_status":"Model predictions under candidate's assumed independent-normal source closure, not empirical source integrals or a lack-of-fit hypothesis test","results":baseline},
             "closure_sensitivity":{"assumptions":"Six finite sensitivity cases, not probabilities or confidence intervals. Normal/lognormal BMI margins preserve each reported cell BMI mean/SD; age margins remain normal. Dependence varies -0.5,0,+0.5. Re-anchor pooled sex moments separately for every case.","cases":closure_sensitivity},
             "estimand_bridge_sensitivity":{"assumptions":"Age multipliers -1,0,1,2 are deliberately assumed competing marginal age profiles. They do not reinterpret the published adjusted coefficient as an estimate of a marginal age coefficient. Same BMI dependence and source pooled-moment re-anchoring in every case.","cases":age_sensitivity},
             "representative_bmi_sensitivity":{"assumptions":"The source category-average ratios are unchanged. Only assumed obese-category representative BMI is varied. None of these representative points is a known category integral; category distributions remain unidentified.","cases":bmi_sensitivity},
             "source_rounding_checks":table_rounding}

# Assertions test the stated numerical operations, not whether bridge assumptions hold.
for scenario in closure_sensitivity:
    for sex in ("male","female"):
        r=scenario["results"][sex]
        assert abs(r["pooled_mean"]-source_moments[sex]["mean"])<1e-10
        assert abs(r["pooled_sd"]-source_moments[sex]["sd"])<1e-10
        assert r["mean_variance_component"]>=0 and r["average_conditional_variance"]>0
        assert abs(r["variance_decomposition_error"])<1e-9
for set0 in (age_sensitivity,bmi_sensitivity):
    for scenario in set0:
        for sex,r in scenario["source_pooled_and_variance_checks"].items():
            assert abs(r["pooled_mean"]-source_moments[sex]["mean"])<1e-10
            assert abs(r["pooled_sd"]-source_moments[sex]["sd"])<1e-10
            assert r["mean_variance_component"]>=0 and r["average_conditional_variance"]>0
            assert abs(r["variance_decomposition_error"])<1e-9

(RUN/"revision_diagnostics.json").write_text(json.dumps(diagnostics,indent=2,allow_nan=False)+"\n",encoding="utf-8")
summary={"baseline_cells":{s:baseline[s]["cells"] for s in baseline},
         "max_cell_mean_change_closure_sensitivity":max(x["largest_cell_mean_change_from_baseline"] for x in closure_sensitivity),
         "max_quadrature_difference":max(x["largest_cell_mean_quadrature_difference_64_vs_128"] for x in closure_sensitivity),
         "age_sensitivity":age_sensitivity,"bmi_sensitivity":bmi_sensitivity,"source_rounding_checks":table_rounding}
print(json.dumps(summary,indent=2,allow_nan=False))

# Final disposition: exact generator/spec no-op, with new evidence and diagnostics.
initial_hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in INITIAL.iterdir() if f.is_file()}
review=json.loads((RUN/"initial_review.json").read_text(encoding="utf-8"))
assert initial_hashes["generator.py"]==review["generator_sha256"]
assert initial_hashes["model_spec.json"]==review["model_spec_sha256"]
assert initial_hashes["evidence.json"]==review["evidence_sha256"]
FINAL.mkdir(exist_ok=True)
shutil.copyfile(INITIAL/"generator.py",FINAL/"generator.py")
shutil.copyfile(INITIAL/"model_spec.json",FINAL/"model_spec.json")

new_evidence={"id":"E_US_CELL_MOMENTS","source_id":"S_US",
              "locator":"PMC8818198 Table 2, HDL-C (mg/dL) row, aligned with n, Age (yrs.) and BMI rows; verified against approved JATS table, not HDLperox or non-HDL-C",
              "estimand":"Unadjusted HDL-C arithmetic mean and individual SD within sex/race/diabetes cells",
              "variables":["hdl","sex","race","diabetes","bmi","age"],
              "adjustment":"Stratification by sex, race and diabetes; no within-cell age/BMI adjustment",
              "reported":{"cells":cells,"hdl_unit":"mg/dL"},
              "uncertainty":"Whole-number HDL means/SDs and rounded predictor summaries. Cell means/SDs do not determine the joint law. Individual SD is distinct from mean SE; no confidence weights used.",
              "applicability":"Same source and overlapping participants as E_US_MOMENTS and E_US_COVARIATES, not independent evidence. These cells provide an additional source constraint on allocation of pooled moments to predictors and omitted determinants.",
              "model_use":"Operational source challenge and closure sensitivity. Existing sex-only residual model misses several cell means/SDs under its own closure; no new coefficient is identified solely by that discrepancy.",
              "bridge_assumptions":["A_SOURCE_MOMENT_CLOSURE","A_RESIDUAL","A_TRANSPORT"]}
ledger["evidence"].append(new_evidence)

us_art=e_by_id["E_US_MOMENTS"]["source_id"]
source_by_id={s["id"]:s for s in ledger["sources"]}
us_art=source_by_id["S_US"]["approved_artifacts"][0]
tw_art=source_by_id["S_TW"]["approved_artifacts"][0]
uk_art=source_by_id["S_UK"]["approved_artifacts"][0]

final_gaps=read("gaps.json")
resolution={
    "G_LOCATION":"F1 cell checks reveal 6-7 mg/dL discrepancies despite pooled sex matching; plausible closure scenarios do not remove them. Retain pooled Results anchors because they directly constrain the available sex groups and no target composition or compatible multivariable HDL regression identifies a replacement. Conditional U.S. transport remains unresolved.",
    "G_BMI":"F3 representative obese BMI 28,30,33 sensitivity preserves source category ratios and reanchors pooled moments but materially changes invented extreme-BMI predictions. Retain BMI 30 assumption because none of the alternatives is selected by evidence; category integration and extreme extrapolation remain unresolved.",
    "G_AGE":"F2 mixed adjustment sets do not identify the desired age association. Assumed age-effect multipliers -1,0,1,2 preserve pooled moments after recalibration while changing age-contrast direction and magnitude. Retain the original modest profile as one scenario, without interpreting its sign or omitted interactions as established.",
    "G_VARIANCE":"F1 shows sex-only residual law does not reproduce several source cell SDs under the closure. All source-moment sensitivities preserve positive residual variance and recomputed variance decompositions. Retain residual parameters and initial gamma/lognormal challenge; predictor-specific residual spread and tails remain unidentified.",
    "G_JOINT":"Normal versus lognormal BMI margins and within-cell dependence -0.5,0,+0.5 move reanchored cell means by at most 0.0375 mg/dL, far less than several source discrepancies. This finite set cannot establish the true source law. No race/diabetes assignments or mixture priors for target rows are introduced; omitted-source composition remains unresolved.",
    "G_MEASUREMENT":"No new calibration evidence arose from the concrete source re-extraction. Retain no numerical assay offset. Fasting, serum/plasma, assay, recruitment and selection transport remain unresolved; no unsupported correction is added.",
    "G_UNCERTAINTY":"New sensitivities are finite assumed alternatives, not confidence intervals or posterior model probabilities. Source precision and model/transport uncertainty remain separate from sampled individual residual variation. Exact generator/spec retention does not imply the original scientific bridges are validated."}
for gap in final_gaps:
    gap["status"]="unresolved"
    gap["resolution"]=resolution[gap["id"]]
    gap["next_action"]="Stop this single revision after the documented source checks/sensitivities; further numerical revision would require additional compatible aggregate constraints, not target feedback."
final_gaps.append({"id":"G_ESTIMAND","component":"Compatibility of BMI and age estimands","affected_analysis":"BMI-adjusted age associations and sex-specific age contrasts","evidence_status":"Within-sex marginal BMI means and heavily adjusted age contrasts are different estimands","consequence":"Their combination need not equal E[HDL|BMI,age,sex]; omitted mechanisms can change age association even when the published adjusted coefficient is fixed.","next_action":"Stop with explicit finite sensitivity; a comparable adjustment set or joint age/sex/BMI summary is needed to identify a correction.","status":"unresolved","resolution":"F2 addressed through explicit estimand mapping and four assumed age profiles, all checked against pooled means/variances. Original profile retained without claiming estimand equivalence.","priority":2})
final_gaps.append({"id":"G_AUDIT","component":"Traceability of the reported pre-freeze choice","affected_analysis":"Audit of model-development claims","evidence_status":"No saved Taiwan-only intermediate specification exists","consequence":"A reported initial choice cannot be independently reconstructed as a numerical before/after model.","next_action":"Retain the correction in final decision and revision log.","status":"resolved","resolution":"The initial mention of switching from a Taiwan-only candidate describes an unsaved modeling consideration, not an auditable numerical revision. Only the frozen initial model and byte-identical final generator/spec are claimed as retained candidates.","priority":4})

final_actions=[
    {"gap_id":"G_LOCATION","action":"reextract","evidence_artifacts":[us_art],"model_change":"Evidence ledger and source applicability qualification; no numerical change","reason":"F1: re-extracted all eight published Table 2 HDL means/SDs with group counts and matched predictor moments; registered E_US_CELL_MOMENTS using the existing accepted artifact."},
    {"gap_id":"G_LOCATION","action":"source_check","evidence_artifacts":[us_art],"model_change":"Added subgroup diagnostics; no parameter change","reason":"F1: evaluated every cell under original closure, checked pooled cell rounding against Results anchors, and reassessed pooled mean/variance. Several cell discrepancies persist, so pooled moment matching is not evidence for the individual conditional allocation."},
    {"gap_id":"G_JOINT","action":"sensitivity","evidence_artifacts":[us_art],"model_change":"Added six explicit source-distribution alternatives; selected model unchanged","reason":"F1: compared normal/lognormal BMI margins and dependence -0.5,0,+0.5, reanchoring pooled moments in each case. Largest cell mean change 0.0375 mg/dL does not account for 6-7 mg/dL discrepancies. These are working closure integrals, not source empirical validation."},
    {"gap_id":"G_VARIANCE","action":"source_check","evidence_artifacts":[us_art],"model_change":"Variance assumptions qualified; no residual parameter change","reason":"F1: computed cell SD discrepancies and recomputed pooled variance decomposition for all closure, age and BMI sensitivities. Residual components remain positive; subgroup variances are not reproduced by the sex-only law."},
    {"gap_id":"G_ESTIMAND","action":"sensitivity","evidence_artifacts":[tw_art,us_art],"model_change":"Explicitly qualified age association and computed four assumed alternatives; no numerical change","reason":"F2: marginal BMI category contrasts and heavily adjusted age coefficients are incompatible estimands without further assumptions. Multipliers -1,0,1,2 demonstrate changed age association with pooled source moments preserved."},
    {"gap_id":"G_AGE","action":"retain","evidence_artifacts":[tw_art,us_art],"model_change":"Original age profile retained as an unvalidated scenario","reason":"F2: alternatives can change age direction, but no attained evidence selects their marginal age coefficients or identifies sex-specific age interactions. No zero omitted-variable effect is inferred."},
    {"gap_id":"G_BMI","action":"sensitivity","evidence_artifacts":[tw_art,us_art],"model_change":"Quantified representative-BMI dependence and residual recalibration; selected slope unchanged","reason":"F3: assumed obese representative BMI 28,30,33 keeps reported category ratios fixed. Invented BMI 77.5 means span about 13.65-23.88 mg/dL for men and 18.29-31.09 for women after pooled reanchoring. These scenarios do not estimate category distributions or form a confidence interval."},
    {"gap_id":"G_MEASUREMENT","action":"retain","evidence_artifacts":[us_art,tw_art,uk_art],"model_change":"No measurement offset or population weight added","reason":"No new compatible assay or target-composition calibration is identified. Omitted determinants and selection cannot be corrected by merely forcing all source cells to fit."},
    {"gap_id":"G_UNCERTAINTY","action":"retain","evidence_artifacts":[us_art,tw_art],"model_change":"No stochastic scientific-parameter layer added","reason":"Finite sensitivities quantify assumptions' effects but provide no weights or uncertainty coverage. Individual residual draws remain distinct from evidence/transport uncertainty."},
    {"gap_id":"G_AUDIT","action":"revise","evidence_artifacts":[],"model_change":"Audit narrative correction only","reason":"Clarified that no Taiwan-only intermediate specification was saved; do not present an unsaved consideration as a reproducible numeric revision."},
    {"gap_id":"G_LOCATION","action":"retain","evidence_artifacts":[us_art,tw_art],"model_change":"Exact generator and model_spec no-op","reason":"Source subgroup discrepancies establish omitted heterogeneity but do not identify a unique corrected E[HDL|BMI,age,sex]. A source-stratum mixture would additionally require unverified predictor densities and transportable stratum priors. The existing marginal sex anchors remain the most direct constraints for available inputs; no numerical accuracy improvement is claimed."},
    {"gap_id":"G_ESTIMAND","action":"stop","evidence_artifacts":[tw_art,us_art,uk_art],"model_change":"No new retrieval","reason":"The review's concrete highest-value lead was already approved MIDUS Table 2, now fully checked. Same-study Taiwan tables do not supply the needed common adjustment set, and the identified UK numeric supplement is unsupported. No remaining already-discovered compatible lead warranted spending budget on another broad search. Six queries and nine downloads remain unused."}
]

events=[json.loads(x) for x in (RUN/"literature"/"audit.jsonl").read_text(encoding="utf-8").splitlines()]
registered={(x["artifact"]["session_relative_path"],x["artifact"]["sha256"]) for x in events if x.get("type")=="artifact_approved" and x.get("status")=="accepted"}
artifact_checks=[]
for source in ledger["sources"]:
    for a in source["approved_artifacts"]:
        assert (a["path"].removeprefix("literature/"),a["sha256"]) in registered
        assert hashlib.sha256((RUN/a["path"]).read_bytes()).hexdigest()==a["sha256"]
        artifact_checks.append({"path":a["path"],"registered_and_hash_match":True})
gids={g["id"] for g in final_gaps}
assert all(g["status"]!="open" and g["resolution"] for g in final_gaps)
assert gids<={a["gap_id"] for a in final_actions}
assert all(a["gap_id"] in gids for a in final_actions)
eids={e["id"] for e in ledger["evidence"]}
aids={a["id"] for a in spec["assumptions"]}
assert set(spec["parameter_provenance"])==set(spec["parameters"])
for v in spec["parameter_provenance"].values():
    assert set(v["evidence_ids"])<=eids and set(v["assumption_ids"])<=aids
assert all(e["source_id"] in source_by_id for e in ledger["evidence"])
final_checks={"scope":"No target rows or outcomes read in revision. Source-only and invented-profile deterministic sensitivities; final generator and spec are byte-identical to the initial versions.",
              "retained_initial_checks":{"execution_time":"Initial construction turn; retained because generator/spec unchanged", "results":read("artificial_checks.json")},
              "revision_diagnostics":diagnostics,
              "final_integrity":{"generator_identical_to_initial":(INITIAL/"generator.py").read_bytes()==(FINAL/"generator.py").read_bytes(),"model_spec_identical_to_initial":(INITIAL/"model_spec.json").read_bytes()==(FINAL/"model_spec.json").read_bytes(),"provenance_ids_resolve":True,"every_gap_has_linked_action_and_nonopen_disposition":True,"registered_artifact_hash_checks":artifact_checks},
              "numeric_assertions":{"all_sensitivity_pooled_mean_and_sd_errors_below_1e_minus_10":True,"all_variance_decomposition_errors_below_1e_minus_9":True,"all_recalibrated_residual_variances_positive":True,"source_operator_status":"Unobserved source joint distributions prevent exact empirical operator evaluation; computed operators are conditional on declared closure assumptions"}}
revision={"generator_or_spec_changed":False,
          "reason":"Retained exact generator/spec after F1 same-source cell re-extraction, six closure sensitivities, F2 four age-estimand sensitivities and F3 three representative-BMI scenarios. These expose consequential nonidentification but do not select a defensible replacement conditional model for the available predictors. Evidence and diagnostics changed; numerical improvement is not claimed.",
          "findings_addressed":[{"id":"F1","actions":["reextract","source_check","sensitivity","retain"],"disposition":"Operational cell check completed; closure variation fails to account for several mean/SD discrepancies. Pooled moments and variance decomposition reassessed. Scientific gap remains unresolved."},{"id":"F2","actions":["sensitivity","retain","stop"],"disposition":"Incompatible adjustment sets explicitly identified. Assumed age alternatives alter association direction while preserving pooled source moments; no evidence selects a replacement."},{"id":"F3","actions":["sensitivity","retain"],"disposition":"Quantified representative-BMI/extrapolation sensitivity. Category-integrated operator still unavailable; original representative assumption retained."},{"id":"review_summary_traceability","actions":["revise"],"disposition":"Corrected unsupported implication of a saved Taiwan-only intermediate model; narrative correction only."}],
          "remaining_limitations":["Several same-source race/diabetes cell means and SDs are not reproduced under declared closure.","Source/target omitted-variable composition and joint predictor distributions unavailable.","Marginal BMI and heavily adjusted age estimands are not identified as a joint conditional mean.","Continuous and extreme-BMI dependence varies materially with assumed category representatives.","Residual distribution/tails, assay/fasting, sampling selection and age interactions remain unvalidated."],
          "retrieval_usage":{"new_queries":0,"new_downloads":0,"total_queries":6,"total_downloads":3,"queries_remaining":6,"downloads_remaining":9},
          "evidence_changed":True,"scientific_numeric_parameters_changed":False,
          "procedural_note":"The new revision diagnostic script was accidentally created at the study root, then immediately moved into this assigned run before execution. No existing common file was modified, no extra data were read, and no file from this revision remains outside this run."}

def save_final(name,obj):
    (FINAL/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+"\n",encoding="utf-8")

save_final("evidence.json",ledger)
save_final("gaps.json",final_gaps)
save_final("actions.json",final_actions)
save_final("artificial_checks.json",final_checks)
save_final("revision.json",revision)
after_hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in INITIAL.iterdir() if f.is_file()}
assert after_hashes==initial_hashes
print(json.dumps({"final_artifacts_written":str(FINAL),"initial_files_unchanged":True,"generator_or_spec_changed":False,"new_evidence_id":"E_US_CELL_MOMENTS"}))
