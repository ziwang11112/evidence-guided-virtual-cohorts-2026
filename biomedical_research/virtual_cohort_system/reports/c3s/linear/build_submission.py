"""Author static source-only submissions; never import or execute their programs."""
from pathlib import Path
import copy
import hashlib
import json
import math
import shutil

R = Path(__file__).resolve().parents[1]
I = R / "inputs"
task = json.loads((I / "task.json").read_text(encoding="utf-8-sig"))
panel = json.loads((I / "SOURCE_PANEL_SPEC.json").read_text(encoding="utf-8-sig"))
evidence = json.loads((I / "evidence_template.json").read_text(encoding="utf-8-sig"))
items = {x["id"]: x for x in evidence["items"]}

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def phi(x):
    return math.exp(-x*x/2) / math.sqrt(2*math.pi)

def cdf(x):
    return (1 + math.erf(x / math.sqrt(2))) / 2

def feature(age, mode):
    return age if mode == "linear" else age - 0.5 * max(age - 60, 0)

# Analytic expectations of specified distributions, not simulated data or fitted constants.
age_masses = [(a, cdf((a+.5-55.5)/9.9)-cdf((a-.5-55.5)/9.9)) for a in range(18, 91)]
glo, ghi = (0-91.8)/9, (126-91.8)/9
g_reference = 91.8 + 9*(phi(glo)-phi(ghi))/(cdf(ghi)-cdf(glo))

generator = '''"""Source-only aggregate generator. No individual source or target data are used."""
import numpy as np
import pandas as pd

def generate(observed, spec, seed):
    p = spec["parameters"]
    active = p["active_context"]
    if active == "development":
        raise ValueError("The development descriptor is never executable")
    context = p["contexts"][active]
    x = context["inputs"]
    n = context["n_rows"]
    rng = np.random.default_rng(seed)

    def restricted_normal(mean, sd, low, high, size, integer=False):
        value = rng.normal(mean, sd, size)
        if integer:
            value = np.rint(value)
        bad = (value < low) | (value > high)
        while np.any(bad):
            value[bad] = rng.normal(mean, sd, int(bad.sum()))
            if integer:
                value[bad] = np.rint(value[bad])
            bad = (value < low) | (value > high)
        return value.astype(int) if integer else value

    if x["age_distribution"]["kind"] == "rounded_truncated_normal":
        a = x["age_distribution"]
        age = restricted_normal(a["mean"], a["sd"], a["minimum"], a["maximum"], n, True)
    else:
        bins = x["age_distribution"]["bins"]
        counts = np.array([b[2] for b in bins], dtype=float)
        bin_index = rng.choice(len(bins), size=n, p=counts/counts.sum())
        age = np.empty(n, dtype=int)
        for k, (low, high, count) in enumerate(bins):
            use = bin_index == k
            age[use] = rng.integers(low, high+1, int(use.sum()))
    female = rng.binomial(1, x["female_probability"], n)
    m, s = x["bmi_mean"], x["bmi_sd"]
    log_variance = np.log1p((s/m)**2)
    bmi = rng.lognormal(np.log(m)-log_variance/2, np.sqrt(log_variance), n)
    glucose = restricted_normal(x["glucose_pretruncation_mean"], x["glucose_pretruncation_sd"],
                                np.nextafter(0.0, 1.0), np.nextafter(126.0, 0.0), n)
    age_feature = age.astype(float)
    if p["age_structure"] == "fixed_hinge60_half_rate":
        age_feature = age_feature - 0.5*np.maximum(age_feature-60.0, 0.0)
    expected = (x["hba1c_reference_location"] + p["location_correction"]
                + p["age_coefficient"]*(age_feature-x["age_feature_reference"])
                + p["bmi_coefficient"]*(bmi-p["bmi_reference"])
                + p["glucose_coefficient"]*(glucose-p["glucose_reference"]))
    hba1c = expected + rng.normal(0, p["residual_sd"], n)
    bad = hba1c <= 0
    if np.any(bad) and p["residual_sd"] == 0:
        raise ValueError("Nonpositive deterministic HbA1c mean under the declared domain")
    while np.any(bad):
        hba1c[bad] = expected[bad] + rng.normal(0, p["residual_sd"], int(bad.sum()))
        bad = hba1c <= 0
    return pd.DataFrame({"row_id": [f"{active}_{i+1:06d}" for i in range(n)],
                         "age": age, "female": female, "bmi": bmi,
                         "glucose": glucose, "hba1c": hba1c})
'''

base_assumptions = {
 "A_DOMAIN": "Common contract domain is nonnegative integer age, binary female, positive BMI/HbA1c and 0<fasting glucose<126 mg/dL. Actual source ages are 18..90 for Lifelines and 25..90 for Pani. Lifelines adult lower bound18 and both upper bounds90 are declared computational assumptions, not recovered source limits. Pani >=70 includes 70..90; no target bounds or quotas apply. No added BMI or HbA1c upper bound is claimed. Development is a nonexecuted descriptor; program rejects that selector.",
 "A_AGE_L": "Lifelines integer ages are rounded Normal(55.5,9.9^2), rejected outside18..90. Published mean/SD do not determine a distribution or support. Truncation/rounding produce approximate rather than forcibly matched moments. Analytic age-feature centering sums exact discrete Gaussian bin masses on this declared support.",
 "A_AGE_P": "Pani eight age-bin probabilities equal published unweighted n/3270; ages are uniform integers within25..39,40..44,45..49,50..54,55..59,60..64,65..69,70..90. This is an unweighted sample-population proxy, not recovered survey weights. Open upper stratum is explicitly capped90 as an unestimated support assumption.",
 "A_MARGINALS": "Both contexts use independent Bernoulli female probability0.597, lognormal BMI with mean26.5 SD4.1, and Normal glucose pretruncation mean91.8 SD9 rejected outside(0,126). Lifelines summaries support these locations/spreads but not distributional shapes; Pani corresponding marginals are unreported and are transferred unchanged as an explicit sensitivity assumption. Glucose centering uses its analytic posttruncation expectation, not a fitted context adjustment. Published glucose summary is approximately reproduced after truncation.",
 "A_INDEPENDENCE": "Age, sex, BMI, glucose and residual noise are mutually independent in both source populations. Their covariance is not reported and is not identified as zero. This fixed simplification is never optimized, shared across structures, and restricts the analytical uses of the synthetic data. No sex term is included because its conditional coefficient is unidentified; zero is a structural assumption, not a source finding.",
 "A_LOCATION": "Lifelines location5.6 is its whole-source HbA1c mean; center age feature at its analytic whole-source expectation. Pani location5.44 is specifically its55..59 stratum HbA1c mean; center age feature at the average over assumed uniform integer ages55..59. BMI/glucose centers equal their common assumed marginal expectations and independence makes these the stratum expectations too. These fixed published source anchors are not independently fitted offsets. Their contrast can reflect selection, composition, measurement and other unmeasured factors; none is causally attributed. A common fitted correction allows joint approximate source reconciliation. A new target HbA1c location remains unidentified.",
 "A_LAW": "Within each source, conditional HbA1c location equals its fixed published reference location plus one shared correction and shared age-feature, BMI and glucose terms. Shared coefficients express an unvalidated transport assumption. Jansen Table2 slopes are separate age/sex-adjusted projections, not automatically joint coefficients; population equality to the conditional BMI/glucose terms follows only from the declared independence. Pani is a survey-adjusted age projection; the unweighted operator approximates that estimand. Nonlinear age coefficient is a feature coefficient, not the reported linear projection.",
 "A_SCATTER": "Individual residual noise is Gaussian with common nonnegative fitted SD, independent of all covariates. Nonpositive HbA1c draws are rejected to satisfy the positive-domain contract; at these source locations this is negligible but changes the exact Gaussian law in the far tail. Source marginal HbA1c SD0.3 is not a residual SD; initialization subtracts variance of the linear independent predictor terms. Pani mean SEs are never converted into individual SDs. Neither residual shape, heteroscedasticity nor cross-source residual transport is identified.",
 "A_MEASUREMENT": "Task units are HbA1c NGSP percent and fasting glucose mg/dL. Jansen immunoassay and Pani HPLC differ; both standardized scales are treated as identical task measurements without an invented assay correction. Frozen conversions are glucose factor18 and NGSP0.09148*IFCC+2.152 for levels, multiplier only for spreads/slopes. Rounded alternate HbA1c unit summaries are duplicate representations, not extra constraints. Jansen printed CI levels remain unknown.",
 "A_BOUNDS": "All five fitted scalars are ordinary common source-law parameters. Location correction[-0.10,0.10] is a declared modeling allowance equal to one printed Lifelines mean increment, not a confidence interval. Age-feature coefficient[0,0.020] is a positive-association sensitivity range up to twice reported Pani slope, not a recovered interval. BMI/glucose bounds are the converted printed Jansen projection interval endpoints, with unknown coverage and conditional interpretation contingent on independence. Residual SD[0,0.3] is the independent-additive variance constraint implied by a marginal source SD0.3; allowing0 does not assert determinism. No context, support, distribution or covariance descriptor is fit.",
 "A_CALIBRATION": "All20 prescribed operators are retained once, each with weight1. The normalized weighted MSE is a pragmatic engineering objective, not a likelihood, calibrated probability or clinical utility. Repeated source diagnostics and overlapping NHANES evidence are not independent confirmations. Fit only seed19101 with<=40trials including baseline; assess baseline/selected at unused19111 and19123. Equality is not improvement. Source agreement does not establish target validity.",
 "A_EXCLUSIONS": "Liu's univariate equation is contextual only and is never used as a joint intercept/slope. Jansen Table3 quantities remain quarantined. No FOS coefficient, IPD, target inputs/outcomes, previous candidate outputs, broad retrieval or new sources are used. The exact32-item admitted evidence bytes are retained."
}

for bundle_name, mode in [("linear", "linear"), ("alternative", "fixed_hinge60_half_rate")]:
    bundle = R / bundle_name
    candidate = bundle / "candidates" / "initial"
    candidate.mkdir(parents=True, exist_ok=True)
    shape_assumption = ("Age feature is age itself. This transparent shared linear response is the reference structure."
        if mode == "linear" else
        "Age feature is age-0.5*max(age-60,0), continuous with half the pre60 rate after60. Pani marginal means show flattening in older strata, motivating a low-complexity sensitivity only. Knot60 and half-rate are fixed authored choices, not estimated biological thresholds; marginal curvature does not identify conditional curvature or distinguish composition effects. Same source populations, covariance, anchors, supports, measurements and parameter budget as the linear structure. Centering changes analytically with feature shape, not by fitting population descriptors.")
    assumptions = dict(base_assumptions, A_STRUCTURE=shape_assumption)
    common = {"female_probability":0.597,"bmi_mean":26.5,"bmi_sd":4.1,
              "glucose_pretruncation_mean":91.8,"glucose_pretruncation_sd":9.0}
    contexts = {"development":{"population":task["population"],"n_rows":6000,
                                "columns":task["columns"],"inputs":{"executable":False}}}
    for context in panel["contexts"]:
        cid = context["id"]
        columns = copy.deepcopy(task["columns"])
        columns[1]["minimum"] = 18 if cid == "lifelines" else 25
        columns[1]["maximum"] = 90
        inp = copy.deepcopy(common)
        if cid == "lifelines":
            inp["age_distribution"] = {"kind":"rounded_truncated_normal","mean":55.5,"sd":9.9,"minimum":18,"maximum":90}
            inp["hba1c_reference_location"] = 5.6
            inp["age_feature_reference"] = sum(feature(a,mode)*w for a,w in age_masses)/sum(w for _,w in age_masses)
            inp["location_evidence_id"] = "J_T1_hba1c_mean_pct"
        else:
            inp["age_distribution"] = {"kind":"integer_age_strata","bins":[[25,39,1037],[40,44,330],[45,49,322],[50,54,261],[55,59,198],[60,64,283],[65,69,198],[70,90,641]]}
            inp["hba1c_reference_location"] = 5.44
            inp["age_feature_reference"] = sum(feature(a,mode) for a in range(55,60))/5
            inp["location_evidence_id"] = "P_NHANES_hba1c_age_55_59_mean"
        contexts[cid] = {"population":context["published_population"],"n_rows":6000,"columns":columns,"inputs":inp}
    p = {"active_context":"development","contexts":contexts,"age_structure":mode,
         "location_correction":0.0,"age_coefficient":0.01,
         "bmi_coefficient":items["J_T2_bmi_slope_task_derived"]["estimate"],
         "glucose_coefficient":items["J_T2_glucose_slope_task_derived"]["estimate"],
         "residual_sd":math.sqrt(0.3**2-(.01*9.9)**2-(.0118924*4.1)**2-(.01163828888888889*9)**2),
         "bmi_reference":26.5,"glucose_reference":g_reference}
    provenance = {}
    def prov(key, eids, aids, derivation):
        provenance[key] = {"evidence_ids":eids,"assumption_ids":aids,"derivation":derivation}
    prov("active_context",[],["A_DOMAIN"],"Parent descriptor only; source bridge changes this selector alone.")
    prov("contexts",[x["id"] for x in evidence["items"] if x["id"].startswith("J_T1_") or x["id"].startswith("P_NHANES_hba1c_age_")],
         ["A_DOMAIN","A_AGE_L","A_AGE_P","A_MARGINALS","A_INDEPENDENCE","A_LOCATION"],"Fixed source aggregate descriptors and explicit unreported-distribution assumptions, including analytic feature centering; no IPD.")
    prov("age_structure",["P_NHANES_age_slope"]+[x["id"] for x in evidence["items"] if x["id"].startswith("P_NHANES_hba1c_age_")],["A_STRUCTURE","A_LAW"],shape_assumption)
    prov("location_correction",["J_T1_hba1c_mean_pct","P_NHANES_hba1c_age_55_59_mean"],["A_LOCATION","A_BOUNDS"],"Common additive correction to fixed published source-specific reference locations; initialized0. Bounds are assumptions, not sampling error.")
    prov("age_coefficient",["P_NHANES_age_slope"],["A_LAW","A_STRUCTURE","A_BOUNDS"],"Initial0.010 uses reported linear projection as an initialization. In the alternative the feature coefficient differs from its source-population OLS age projection.")
    prov("bmi_coefficient",["J_T2_bmi_slope_task_derived"],["A_LAW","A_INDEPENDENCE","A_BOUNDS"],"Initialized from separate age/sex-adjusted projection; equivalence to conditional term requires fixed covariate independence.")
    prov("glucose_coefficient",["J_T2_glucose_slope_task_derived"],["A_LAW","A_INDEPENDENCE","A_BOUNDS"],"Initialized from separate age/sex-adjusted projection, converted using0.09148/18; equivalence to conditional term requires independence.")
    prov("residual_sd",["J_T1_hba1c_sd_pct","J_T1_age_sd_task","J_T1_bmi_sd_task","J_T1_glucose_sd_mg_dL_derived"],["A_SCATTER","A_BOUNDS"],"Initial sqrt(0.3^2-(0.010*9.9)^2-(0.0118924*4.1)^2-(0.01163828888888889*9)^2). Linear independent-variance approximation retained as common initialization, not asserted to exactly reconstruct either structure's posttruncation variance.")
    prov("bmi_reference",["J_T1_bmi_mean_task"],["A_MARGINALS"],"Lognormal mean26.5 by construction; transferred to Pani as a fixed assumption.")
    prov("glucose_reference",["J_T1_glucose_mean_mg_dL_derived","J_T1_glucose_sd_mg_dL_derived"],["A_MARGINALS"],"Analytic mean of Normal(91.8,9^2) truncated(0,126), using standard normal density/CDF; fixed same in both contexts.")
    spec = {"parameters":p,"assumptions":[{"id":k,"description":v} for k,v in assumptions.items()],"parameter_provenance":provenance}
    constraints=[]
    for context in panel["contexts"]:
        for check in context["checks"]:
            cid, key = context["id"],check["id"]
            if cid == "pani":
                scale,reason = ((.002,"Pragmatic20% of reported age slope0.010; coefficient SE/CI is unknown. This is not a statistical or clinical tolerance.") if key == "P_NHANES_age_slope" else (.05,"Common0.05 HbA1c percentage-point discrepancy scale for source age means; not a clinical tolerance, individual SD, or source sampling SE. Pani SEs remain reported evidence and are not inverted as independent precision weights."))
            elif "age_" in key:
                scale,reason=.99,"Pragmatic10% of reported age SD9.9, used only to nondimensionalize the mean/SD discrepancy; never a mean SE or clinical tolerance."
            elif "bmi_" in key and "slope" not in key:
                scale,reason=.41,"Pragmatic10% of reported BMI SD4.1; objective scale only, not mean uncertainty or clinical tolerance."
            elif "glucose_" in key and "slope" not in key:
                scale,reason=.9,"Pragmatic10% of reported fasting glucose SD9mg/dL; objective scale only, not mean uncertainty or clinical tolerance."
            elif "female" in key:
                scale,reason=.02,"Two percentage points is a declared numerical composition-discrepancy scale, not an estimated confidence interval."
            elif "bmi_slope" in key:
                scale,reason=(.0146368-.009148)/2,"Half-width of printed converted Jansen BMI interval; confidence level unknown. Used as a source-referenced numerical scale only, not a standard error or coverage claim."
            elif "glucose_slope" in key:
                scale,reason=(.012756377777777777-.0105202)/2,"Half-width of printed converted Jansen glucose interval; confidence level unknown. Used as numerical scale only, not SE or coverage claim."
            elif "hba1c_sd" in key:
                scale,reason=.03,"Pragmatic10% of reported individual marginal HbA1c SD0.3; objective scale only, not uncertainty of its estimate."
            else:
                scale,reason=.05,"Half of the0.1 percentage-point printed Lifelines mean increment; pragmatic discrepancy scale, not an inferential or clinical tolerance."
            constraints.append({"context_id":cid,"check_id":key,"scale":scale,"scale_reason":reason})
    plan={"schema_version":1,"parameters":[
        {"name":"location_correction","lower":-.10,"upper":.10,"step":.025},
        {"name":"age_coefficient","lower":0,"upper":.020,"step":.002},
        {"name":"bmi_coefficient","lower":.009148,"upper":.0146368,"step":.001},
        {"name":"glucose_coefficient","lower":.0105202,"upper":.012756377777777777,"step":.0005},
        {"name":"residual_sd","lower":0,"upper":.3,"step":.025}],
        "constraints":constraints,"fit_seeds":[19101],"replay_seeds":[19111,19123],
        "optimizer":{"method":"bounded_coordinate_search","max_trials":40,"shrink":.5,"min_step_fraction":.0625,"target_loss":0.0},
        "execution":{"timeout_seconds":30,"memory_mb":1024,"output_bytes":20000000,"log_bytes":100000},"noncomputable":"infeasible"}
    requirements=[
      "Technical: all20 prescribed diagnostics must be finite and computed with their exact declared operators on6000-row source outputs; generator/specification linkage, freeze integrity and output contract must verify. The development descriptor must never execute. A not-computable or failed execution is infeasible, not a low-loss success.",
      "Method: same fixed source populations, anchors, supports, unit conversions and independence assumptions must be retained across both structures and every trial. Only the five declared common scalars may vary. No target data, source-specific fitted offset, omitted-variable covariance tuning, quarantined coefficient or additional source enters.",
      "Source compatibility: on each unused seed19111 and19123 require absolute Lifelines HbA1c mean discrepancy<=0.05 percentage points, HbA1c SD discrepancy<=0.03, and every Pani age-stratum mean discrepancy<=0.10 percentage points. These predeclared engineering compatibility thresholds are pragmatic and do not represent clinical acceptability, formal hypothesis tests or calibrated confidence coverage.",
      "Projected associations: on each unused seed require Pani age OLS coefficient in[0.008,0.012] percentage points/year, Jansen BMI projection in[0.009148,0.0146368] percentage points/(kg/m^2), and glucose projection in[0.0105202,0.012756377777777777] percentage points/(mg/dL). Pani limits are an authored20% numerical band; Jansen limits use printed bounds of unknown confidence level. Conditional coefficients alone cannot satisfy these requirements; use the exact source projections.",
      "Unrelated marginal no-harm: at a fixed seed, selected versus initial age/female/BMI/glucose source outputs and all their diagnostic values must be identical, since only HbA1c-law scalars are fitted and covariate RNG draws precede HbA1c. Across unused seeds flag age mean/SD discrepancies>.99year, BMI mean/SD>.41kg/m^2, glucose mean/SD>.9mg/dL or female fraction>.02 as source-population approximation failures, regardless of overall objective.",
      "Numerical improvement: require selected fit-seed loss strictly below initial loss, and lower selected loss on both unused seeds, before calling calibration improvement robust. Equality is not improvement. Report each check's raw difference and change, both seeds, worst Pani age-profile error and each projected slope. A better aggregate loss never erases an individual compatibility failure.",
      "Structural comparison: compare the alternative with the linear candidate only after each has been selected with seed19101; use both unused seeds and the same20checks. Call the alternative numerically preferable only when its loss is strictly lower on both unused seeds, its worst age-profile discrepancy is not larger on either seed, and it introduces no new failed compatibility requirement. Otherwise retain linear for parsimony or report an unresolved trade-off. This is a source-only sensitivity comparison, not evidence of a conditional biological hinge.",
      "Interpretation: even passing every numerical threshold leaves the unreported covariance, Pani survey representation, source supports/distributions, residual law and cross-source transport unverified. Pani means are marginal and Jansen slopes are separately adjusted projections. A future target source location remains unidentified; no target predictions, causal claims, clinical tolerances, individual-level validity or broad method validation are established."
    ]
    criteria={"schema_version":1,"scope":"source_only",
        "parameter_roles":[{"name":x["name"],"role":"source_parameter","rationale":provenance[x["name"]]["derivation"]+" Bounds are explicitly described in A_BOUNDS."} for x in plan["parameters"]],
        "check_weights":[{"context_id":x["context_id"],"check_id":x["check_id"],"weight":1.0,"weight_reason":"Equal weight per predeclared diagnostic for transparent comparison; repeated/correlated source summaries do not become independent evidence and this objective is not a likelihood."} for x in constraints],
        "scientific_requirements":requirements}
    write(bundle/"calibration_plan.json",plan)
    write(bundle/"scientific_criteria.json",criteria)
    write(candidate/"calibration_plan.json",plan)
    write(candidate/"scientific_criteria.json",criteria)
    write(candidate/"model_spec.json",spec)
    shutil.copyfile(I/"evidence_template.json",candidate/"evidence.json")
    (candidate/"generator.py").write_text(generator,encoding="utf-8")
    sourceplan={"schema_version":1,"model_domain":{"columns":task["columns"],"assumption_ids":["A_DOMAIN"],"description":"Common non-target computational contract; finite age supports declared only in source descriptors. See A_DOMAIN for unreported limits."},"contexts":[]}
    for context in panel["contexts"]:
        cid=context["id"]
        childtask=copy.deepcopy(task)
        for key in ("population","n_rows","columns"):
            childtask[key]=contexts[cid][key]
        taskpath=f"source_contexts/{cid}/task.json"
        feedbackpath=f"source_contexts/{cid}/whole_cohort_feedback.json"
        write(candidate/taskpath,childtask)
        feedback={"schema_version":1,"population":childtask["population"],"measurement":{"mode":"identity","description":"Generated fasting glucose mg/dL and HbA1c NGSP percent; fixed admitted conversions already represented in evidence. Assay comparability is assumed, no fitted assay correction."},"assumption_ids":list(assumptions),"checks":[]}
        for check in context["checks"]:
            feedback["checks"].append({"id":check["id"],"evidence_id":check["evidence_id"],"status":"approximate","operator":check["operator"],"assumption_ids":list(assumptions),"reason":"Exact prescribed operator on a generated source approximation. All unreported joint distributions, supports, selection and measurement comparability remain assumptions. Unweighted source proxy does not reconstruct complex survey inference. Reported projections are checked as projections, not substituted conditional coefficients."})
        write(candidate/feedbackpath,feedback)
        sourceplan["contexts"].append({"id":cid,"task_path":taskpath,"feedback_path":feedbackpath})
    write(candidate/"source_context_plan.json",sourceplan)
    linkage={"schema_version":1,"scope":"source_only","program":"generator.py","source_context_plan":"source_context_plan.json","active_context_only_bridge":True,"parent_executable":False,
        "shared_law":"source-reference HbA1c location + common correction + common age-feature/BMI/glucose terms + shared independent residual law",
        "fixed_source_location_anchors":{"lifelines":{"evidence_id":"J_T1_hba1c_mean_pct","value":5.6,"reference":"whole declared source age distribution"},"pani":{"evidence_id":"P_NHANES_hba1c_age_55_59_mean","value":5.44,"reference":"declared55..59 source age stratum"}},
        "same_population_and_covariance_across_structures":True,"different_analytic_feature_centering_is_not_population_tuning":True,
        "unidentified_future_target_location":True,"identification_limits":["No target location is implied by either source reference.","Unknown covariate covariance is fixed to independence only as a transparent sensitivity assumption.","Source assay/population differences cannot be separately identified from these summaries.","The nonlinear alternative is a marginal-pattern-motivated sensitivity, not recovered conditional biology."]}
    write(candidate/"transfer_linkage.json",linkage)
    decision=f'''# Source-only scientific decision: {bundle_name}

The candidate tests a common centered HbA1c response law in two explicitly approximated source populations, with fixed reported source reference locations. Lifelines5.6 is a whole-source mean; Pani5.44 is specifically the55–59 mean. Analytic centering preserves this distinction. The difference is not attributed to an assay effect or freely fitted away. Any future target location is unidentified.

{shape_assumption}

Age, sex, BMI, glucose and HbA1c are all generated without IPD. Each source has6000rows. The development parent is never executed. Pani age-bin n values construct unweighted probabilities; the upper age group includes70–90, not a borrowed target age limit. Lifelines support18–90 is an assumption. Pani BMI/glucose/sex marginals are unavailable and fixed to Lifelines marginals. Independence and no direct sex term are declared simplifications shared across structures and never calibrated.

Jansen BMI/FPG coefficients are separate age/sex-adjusted projections. They equal the model's conditional terms only under the fixed independence assumption. Pani's age estimate is a survey-adjusted projection; the supplied unweighted regression approximates it. In the nonlinear alternative the feature coefficient is not itself the age projection. All exact20source operators are retained, including age-stratum means. Pani SEs are not individual SDs; Jansen interval coverage is unknown; duplicate unit representations are not additional constraints. Liu and Table3 remain contextual/quarantined.

Five common scalar parameters are fit within predeclared bounds. All population distributions, covariance, reference anchors, domain limits and curve shape choices are fixed before execution. The residual SD is initialized by a linear independent-variance subtraction, not by interpreting the marginal SD as residual SD. The Gaussian noise law and its transport are assumptions.

calibration_plan.json and scientific_criteria.json are written before freeze. All20weights are1; scales are nondimensionalization choices and are not clinical tolerances or probabilities. Prospective requirements include exact execution linkage, finite checks, age-profile/association compatibility and unchanged covariate marginals. Selection uses only seed19101 with at most40evaluations inclusive baseline; unused19111/19123 compare both initial and selected candidates. Strict improvement on both unused seeds is required for robust numerical improvement. No target is generated or evaluated.

This authored candidate is a testable source-only submission, not a claim that the unknown source distributions are correct. Successful source fit cannot establish target validity, causal effects, measurement replacement or individual realism. Current stopping point is complete static artifacts; actual isolated execution and calibration belong to the controller.
'''
    (candidate/"decision.md").write_text(decision,encoding="utf-8")
    static={"scope":"source_only","execution_performed":False,"generator_imported":False,"input_evidence_sha256":digest(I/"evidence_template.json"),"candidate_evidence_sha256":digest(candidate/"evidence.json"),"check_count":sum(len(c["checks"]) for c in panel["contexts"]),"source_rows":{c:contexts[c]["n_rows"] for c in ("lifelines","pani")},"analytic_centering":{"lifelines":contexts["lifelines"]["inputs"]["age_feature_reference"],"pani":contexts["pani"]["inputs"]["age_feature_reference"],"glucose":g_reference},"predeclared_parameter_names":[x["name"] for x in plan["parameters"]],"evidence_byte_identity":digest(I/"evidence_template.json")==digest(candidate/"evidence.json")}
    write(candidate/"static_author_checks.json",static)
    artifacts=[]
    for name in ["calibration_plan.json","scientific_criteria.json","transfer_linkage.json","source_context_plan.json","static_author_checks.json"]:
        artifacts.append({"path":name,"sha256":digest(candidate/name)})
    write(candidate/"checks.json",{"scope":"source_only","records":[{"name":"static_evidence_and_plan_authoring","status":"pass","detail":"Parsed only admitted aggregate evidence; copied exact evidence bytes; counted20prescribed checks; wrote two6000-row source descriptors and five-scalar pre-execution plan. Analytic centering uses declared distribution formulas, with no simulated tables or program import."},{"name":"isolated_generation_and_source_fit","status":"not_computable","detail":"Not performed by scientific author. Only the controller may execute frozen programs; no source or target numerical fit is claimed."}],"artifacts":artifacts})
    print(bundle_name, "static authored; evidence byte-identical", static["evidence_byte_identity"], "checks",static["check_count"])
