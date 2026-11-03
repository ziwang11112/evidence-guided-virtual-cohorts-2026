"""Construct L01 initial submission; deterministic mathematics only, no synthetic rows."""
from pathlib import Path
import ast
import hashlib
import json
import math

ROOT = Path(r"D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcIA/L01")
CANDIDATE = ROOT / "b/candidates/latent_glycemia_v1"
CANDIDATE.mkdir(parents=True, exist_ok=False)
(CANDIDATE / "auxiliary").mkdir()

def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")

generator = '''"""Assumption-dependent whole-cohort construction; only generate produces rows."""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("Whole-cohort construction requires observed=None")
    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    d = p["design"]
    n = d["n_rows"]
    a = p["age_distribution"]
    age_values = np.arange(d["age_min"], d["age_max"] + 1)
    age_weights = np.exp(-0.5 * ((age_values - a["location"]) / a["scale"]) ** 2)
    age = rng.choice(age_values, n, p=age_weights / age_weights.sum())
    age_c = age - p["centering"]["age"]
    f = p["female_distribution"]
    female_logit = np.log(f["probability_at_center"] / (1.0 - f["probability_at_center"])) + f["age_logit_slope"] * age_c
    female = rng.binomial(1, 1.0 / (1.0 + np.exp(-female_logit)), n)
    female_c = female - p["centering"]["female"]
    b = p["bmi_distribution"]
    bmi = np.exp(np.log(b["mean_at_center"]) + b["age_quadratic_log"] * age_c ** 2 + b["female_log_effect"] * female_c - 0.5 * b["log_sd"] ** 2 + b["log_sd"] * rng.normal(size=n))
    center = p["centering"]
    bmi_c = center["bmi_covariate_scale"] * np.tanh((bmi - center["bmi"]) / center["bmi_covariate_scale"])
    j = p["joint_glycemia"]
    z_glucose = rng.normal(size=n)
    z_hba1c = j["core_normal_correlation"] * z_glucose + np.sqrt(1.0 - j["core_normal_correlation"] ** 2) * rng.normal(size=n)
    g = p["core_glucose"]
    h = p["core_hba1c"]
    glucose = np.exp(np.log(g["mean_at_center"]) + g["age_log_slope"] * age_c + g["bmi_log_slope"] * bmi_c + g["female_log_effect"] * female_c - 0.5 * g["log_sd"] ** 2 + g["log_sd"] * z_glucose)
    hba1c = np.exp(np.log(h["mean_at_center"]) + h["age_log_slope"] * age_c + h["bmi_log_slope"] * bmi_c + h["female_log_effect"] * female_c - 0.5 * h["log_sd"] ** 2 + h["log_sd"] * z_hba1c)
    t = p["glycemic_subgroup"]
    subgroup_logit = np.log(t["probability_at_center"] / (1.0 - t["probability_at_center"])) + t["age_logit_slope"] * age_c + t["bmi_logit_slope"] * bmi_c + t["female_logit_effect"] * female_c
    subgroup = rng.binomial(1, 1.0 / (1.0 + np.exp(-subgroup_logit)), n)
    common_excess = rng.gamma(j["shared_gamma_shape"], 1.0, n)
    glucose_excess = common_excess + rng.gamma(j["individual_gamma_shape"], 1.0, n)
    hba1c_excess = common_excess + rng.gamma(j["individual_gamma_shape"], 1.0, n)
    glucose = glucose + subgroup * t["glucose_increment_per_gamma_unit"] * glucose_excess
    hba1c = hba1c + subgroup * t["hba1c_increment_per_gamma_unit"] * hba1c_excess
    return pd.DataFrame({
        "row_id": [d["id_prefix"] + str(i + 1).zfill(6) for i in range(n)],
        "age": age.astype(int), "female": female.astype(int),
        "bmi": bmi, "glucose": glucose, "hba1c": hba1c,
    }, columns=["row_id", "age", "female", "bmi", "glucose", "hba1c"])
'''
(CANDIDATE / "generator.py").write_text(generator, encoding="utf-8")

assumptions = [
    {"id": "A_DESIGN", "description": "Task requires 3000 independent synthetic records, integer age 35-74 and binary female. Row identifiers carry no clinical information. No participant inputs, disease or pregnancy exclusions, or survey weights are imposed."},
    {"id": "A_TRANSPORT", "description": "All numerical choices describe one exploratory CHNS 2009 analytical-sample scenario. Published populations, sampling, disease selections, years and assays differ; no target population parameter is identified. Source summaries are not pooled as empirical observations, weighted by fabricated precision, or treated as targets to reproduce."},
    {"id": "A_DEMOGRAPHY", "description": "Age uses a discrete normal kernel at 54 years with scale 12 over task support. Female probability is 0.55 at age 54 with logit slope 0.004/year. These are broad demographic assumptions; reported source female count ratios are contextual. No age-sex independence is inferred from absent evidence."},
    {"id": "A_BMI", "description": "BMI is lognormal conditional on age/sex, mean 24.2 at centered covariates, log SD 0.145, quadratic log-age term -0.00012/year^2 and female log effect 0.012. Bao BMI quartiles and MIND mean/SD motivate location/spread plausibility but do not identify these target quantities. The curve and sex effect are assumptions."},
    {"id": "A_CORE", "description": "Core glucose/HbA1c are correlated lognormal variables with conditional means 5.05 mmol/L and 5.5%, log SD 0.11 and a derived log SD corresponding to individual SD 0.4% at mean 5.5. Core latent normal correlation 0.45 is an assumed dependence structure; neither Bao Pearson 0.619 nor MIND Spearman 0.529 is set equal to it. Core lognormal means are corrected by minus half log variance."},
    {"id": "A_RELATIONSHIPS", "description": "Core glucose log slopes are age 0.0018/year, bounded BMI 0.006/unit and female -0.012. Core HbA1c slopes at centered values are approximately age 0.009 percentage points/year, BMI 0.004 percentage points/unit and female -0.02 percentage points. Age magnitude is qualitatively informed by restored Pani 0.010 and converted Jansen age projections, with their actual adjustment and selection retained. BMI and glucose Jansen Table 2 coefficients are not concatenated into a structural equation. These effects, including sex orientation, are target assumptions."},
    {"id": "A_TAIL", "description": "A latent high-glycemia subgroup has center probability 0.075 and logit effects age 0.025/year, bounded BMI 0.08/unit and female -0.10. This is not a diagnosis or estimated diabetes prevalence. It allows high tails because target selection does not exclude diagnosed diabetes. Group membership, its effects and gamma-tail forms are assumed. Mean increments conditional on membership are 3.4 mmol/L glucose and 1.8% HbA1c; correlated gamma severities reflect incomplete correspondence of a single serum measure and longer-term glycation."},
    {"id": "A_JOINT", "description": "Shared gamma shape 0.25 plus separate gamma shapes 1.75, all unit scale, yield total shape 2 per excess and conditional excess correlation 0.125. Primitive random draws are independent except specified shared normals/gamma and demographic conditioning. This conditional independence is an explicit regularizing assumption, not evidence of biological independence. The joint law contains no causal interpretation, clinical treatment status or hematology."},
    {"id": "A_SUPPORT", "description": "Age is bounded; sex is binary; BMI is positive lognormal. BMI's biomarker/risk covariate is 8*tanh((BMI-24.2)/8), preserving a near-center association and bounding exponential multipliers. This prevents the infinite moment problem arising from exponentiating an unbounded lognormal BMI. Positive lognormal cores plus nonnegative gamma increments imply positive outcomes and all positive integer moments finite. Gaussian/gamma draws are not sample-normalized or clipped to empirical quantiles."},
    {"id": "A_LIMITS", "description": "Assay equivalence, source-to-target exchangeability, nonlinear and subgroup associations, causal effects, transport uncertainty, treatment/diabetes mechanisms and source numerical replay remain unassessed. Fixed parameters encode a scenario rather than a posterior; seed variation concerns synthetic sampling only. The task's E1/E2/E3 projections emerge from the complete mixture and need not equal any structural parameter or source projection."},
]
parameters = {
    "design": {"n_rows": 3000, "age_min": 35, "age_max": 74, "id_prefix": "L01_"},
    "centering": {"age": 54.0, "female": 0.55, "bmi": 24.2, "bmi_covariate_scale": 8.0},
    "age_distribution": {"location": 54.0, "scale": 12.0},
    "female_distribution": {"probability_at_center": 0.55, "age_logit_slope": 0.004},
    "bmi_distribution": {"mean_at_center": 24.2, "log_sd": 0.145, "age_quadratic_log": -0.00012, "female_log_effect": 0.012},
    "core_glucose": {"mean_at_center": 5.05, "log_sd": 0.11, "age_log_slope": 0.0018, "bmi_log_slope": 0.006, "female_log_effect": -0.012},
    "core_hba1c": {"mean_at_center": 5.5, "log_sd": math.sqrt(math.log1p((0.4 / 5.5) ** 2)), "age_log_slope": 0.009 / 5.5, "bmi_log_slope": 0.004 / 5.5, "female_log_effect": -0.02 / 5.5},
    "joint_glycemia": {"core_normal_correlation": 0.45, "shared_gamma_shape": 0.25, "individual_gamma_shape": 1.75},
    "glycemic_subgroup": {"probability_at_center": 0.075, "age_logit_slope": 0.025, "bmi_logit_slope": 0.08, "female_logit_effect": -0.10, "glucose_increment_per_gamma_unit": 1.7, "hba1c_increment_per_gamma_unit": 0.9},
}

def prov(evidence, assumption_ids, derivation):
    return {"evidence_ids": evidence, "assumption_ids": assumption_ids, "derivation": derivation}

provenance = {
    "design": prov([], ["A_DESIGN"], "Row count, age support and column identities follow task.json; id prefix is an implementation convention."),
    "centering": prov([], ["A_DEMOGRAPHY", "A_BMI", "A_SUPPORT"], "54, 0.55 and 24.2 define assumed reference covariates; 8 is an assumed saturation scale in BMI units, not an observed cutoff."),
    "age_distribution": prov(["M_B_AGE_MEDIAN", "M_B_AGE_Q1", "M_B_AGE_Q3", "M_J_AGE_MEAN", "M_J_AGE_SD"], ["A_DEMOGRAPHY", "A_TRANSPORT"], "Choose broad location 54 and kernel scale 12 within adult 35-74 support. No quartile-to-SD conversion or source-to-target equality is claimed; normalized discrete weights determine the actual moments."),
    "female_distribution": prov(["M_B_FEMALE_FRACTION", "M_M_FEMALE_FRACTION"], ["A_DEMOGRAPHY", "A_TRANSPORT"], "Choose 0.55 center probability and mild 0.004 age logit slope; neither is a transported source estimate."),
    "bmi_distribution": prov(["M_B_BMI_MEDIAN", "M_B_BMI_Q1", "M_B_BMI_Q3", "M_M_BMI_MEAN", "M_M_BMI_SD"], ["A_BMI", "A_TRANSPORT"], "24.2 center conditional arithmetic mean and log SD 0.145 give approximately 3.53 individual SD at center; age curvature and sex term are assumptions. This is a plausible target scenario, not fitted source quartiles."),
    "core_glucose": prov(["M_B_FPG_MEDIAN", "M_B_FPG_Q1", "M_B_FPG_Q3", "M_M_FSG_MEAN", "M_M_FSG_SD"], ["A_CORE", "A_RELATIONSHIPS", "A_TRANSPORT", "A_SUPPORT"], "5.05 core center and 0.11 log SD are assumptions informed by the source central ranges. No universal plasma-serum conversion is used. All covariate effects are explicit assumptions."),
    "core_hba1c": prov(["M_B_HBA1C_PERCENT_MEDIAN", "M_B_HBA1C_PERCENT_Q1", "M_B_HBA1C_PERCENT_Q3", "M_M_HBA1C_PERCENT_MEAN", "M_M_HBA1C_PERCENT_SD", "E_SOURCE_RECONCILIATION", "U_NGSP_SCALE", "R_JANSEN_BMI"], ["A_CORE", "A_RELATIONSHIPS", "A_TRANSPORT"], "Choose core mean 5.5 and individual SD 0.4; log SD=sqrt(log(1+(0.4/5.5)^2)). Set log-age slope 0.009/5.5, log-BMI 0.004/5.5, female effect -0.02/5.5. Audit Pani adjusted weighted age=0.010 and Jansen age projections (0.11,0.08,0.07)*0.09148 motivate only order of magnitude. Source adjusted projections remain distinct; direct BMI choice does not assert equality to Jansen 0.13*0.09148."),
    "joint_glycemia": prov(["R_BAO_PEARSON", "R_MIND_SPEARMAN"], ["A_CORE", "A_JOINT", "A_TRANSPORT"], "0.45 is the assumed core normal correlation, not either published correlation. Gamma shared 0.25 and separate 1.75 imply total shape 2, excess means 2 and conditional correlation 0.25/2=0.125. Shared subgroup membership adds further association. No Pearson/Spearman equivalence is asserted."),
    "glycemic_subgroup": prov(["M_M_FSG_SD", "M_M_HBA1C_PERCENT_SD", "E_SOURCE_RECONCILIATION"], ["A_TAIL", "A_TRANSPORT", "A_JOINT"], "Probability .075 and age/BMI/sex logit effects .025/.08/-.10 are assumptions. Unit-scale gamma total shape 2 gives 1.7*2=3.4 glucose and .9*2=1.8 HbA1c average increments. Broader source dispersions and differing disease exclusions motivate allowing a high tail without identifying target prevalence or treatment."),
}
spec = {"parameters": parameters, "assumptions": assumptions, "parameter_provenance": provenance}
write_json(CANDIDATE / "model_spec.json", spec)
evidence = json.loads((ROOT / "b/input/compiled_evidence.json").read_text(encoding="utf-8-sig"))
write_json(CANDIDATE / "evidence.json", evidence)

age_values = list(range(35, 75))
w = [math.exp(-0.5 * ((x - 54) / 12) ** 2) for x in age_values]
w = [v / sum(w) for v in w]
age_mean = sum(v * x for v, x in zip(w, age_values))
age_var = sum(v * (x - age_mean) ** 2 for v, x in zip(w, age_values))
p = parameters["glycemic_subgroup"]["probability_at_center"]
sg = parameters["core_glucose"]["log_sd"]
sh = parameters["core_hba1c"]["log_sd"]
vg = 5.05 ** 2 * math.expm1(sg ** 2)
vh = 5.5 ** 2 * math.expm1(sh ** 2)
cg = 5.05 * 5.5 * math.expm1(0.45 * sg * sh)
var_excess_g = 1.7 ** 2 * (p * (2 + 2 ** 2) - (p * 2) ** 2)
var_excess_h = 0.9 ** 2 * (p * (2 + 2 ** 2) - (p * 2) ** 2)
cov_excess = 1.7 * 0.9 * (p * (0.25 + 2 ** 2) - (p * 2) ** 2)
syntax = ast.parse(generator)
fn = next(x for x in syntax.body if isinstance(x, ast.FunctionDef) and x.name == "generate")
report = {
    "method": "Closed-form algebra and exact 40-point age-support summation; AST parse only. No generator import, generator execution, random draw, synthetic rows, target-reference comparison, source replay or fitted optimization.",
    "abi_positional_argument_names": [x.arg for x in fn.args.args],
    "age_kernel_population_mean": age_mean,
    "age_kernel_population_sd": math.sqrt(age_var),
    "centered_covariate_illustration": {
        "qualification": "Counterfactual centered covariates including female=0.55, solely to inspect mixture algebra. These are not whole-cohort diagnostics, source replay or target estimates.",
        "glucose_mean": 5.05 + p * 1.7 * 2,
        "hba1c_mean": 5.5 + p * 0.9 * 2,
        "glucose_sd": math.sqrt(vg + var_excess_g),
        "hba1c_sd": math.sqrt(vh + var_excess_h),
        "pearson_glucose_hba1c": (cg + cov_excess) / math.sqrt((vg + var_excess_g) * (vh + var_excess_h)),
    },
    "converted_source_age_projections_percent_per_year": {"Jansen_Table2_gender_adjusted": 0.11 * 0.09148, "Jansen_Table3_II_gender_FPG_adjusted": 0.08 * 0.09148, "Jansen_Table3_III_broader_adjustment": 0.07 * 0.09148},
    "conversion_limit": "Same evidence on a different scale; not independent estimates, common adjustment sets or assigned target coefficients.",
    "finite_moment_argument": "All exponential covariate multipliers bounded by finite age/category/bounded-BMI support; normal exponentials and gamma increments have all positive integer moments. Positive support follows algebraically. No source or target empirical support claim.",
    "retrieval": {"queries": [], "original_documents": [], "new_sources": [], "overlap": "Jansen models share Lifelines; Bao statistics share SHDS; MIND statistics share respondents; Pani age strata and slope share NHANES via audit. Audit repeats original-source evidence and adds no independent sample."},
}
write_json(CANDIDATE / "auxiliary/analytic_check.json", report)
(CANDIDATE / "auxiliary/construct_initial.py").write_text(Path(__file__).read_text(encoding="utf-8"), encoding="utf-8")
artifacts = [{"path": path, "sha256": hashlib.sha256((CANDIDATE / path).read_bytes()).hexdigest()} for path in ["auxiliary/analytic_check.json", "auxiliary/construct_initial.py"]]
checks = {
    "scope": "source_only",
    "records": [
        {"name": "scope_interpretation", "status": "pass", "detail": "Legacy source_only denotes declared input evidence and deterministic construction checks. It does not mean independently validated source population or target accuracy."},
        {"name": "analytic_structure_and_ast", "status": "pass", "detail": "Producer performs AST signature inspection, closed-form centered-mixture moments and exact age-support summation without generating any rows; report and actual producer are bound."},
        {"name": "source_context_replay", "status": "not_computable", "detail": "No source-context execution adapter supplied; task-population diagnostics cannot reproduce the different source selections, assay handling, adjustment sets or weighting."},
        {"name": "generated_output_validation", "status": "not_computable", "detail": "Generator has not been imported or executed. Coordinator must freeze and execute the requested isolated trial and inspect all required statistics."},
        {"name": "target_population_accuracy", "status": "not_computable", "detail": "No target-reference summaries are present in the assigned input. Assumption-dependent scenario is not validated target recovery."},
    ],
    "artifacts": artifacts,
}
write_json(CANDIDATE / "checks.json", checks)
(CANDIDATE / "decision.md").write_text('''# Initial author decision

Submit `latent_glycemia_v1` for trial4201. This is one explicitly assumption-dependent, complete five-variable cohort scenario for the requested selected CHNS analytical population. It is not a reconstruction of source participants or a population estimate.

Age is a broad bounded discrete distribution. Female membership has a mild age association; BMI has a positive lognormal distribution with mild age curvature and sex association. Glucose and HbA1c comprise positive, correlated central components plus a shared high-glycemia subgroup with partly distinct gamma severities. This allows broader tails when diagnosed diabetes has not been excluded without treating subgroup membership as observed diabetes. All scientific parameters, including unreported relationships, are explicit in the specification and provenance.

Bao provides Shanghai plasma/HbA1c quartiles and Pearson association, MIND provides older rural serum/HbA1c means/individual SDs and a Spearman association, and Jansen provides selected non-diabetic European projections. These are not pooled or equated. The restored audit supplies nonzero age evidence with differing conditioning: Pani's survey-weighted sex/BMI/FPG-adjusted age slope is 0.010 percentage points/year; Jansen's age rows convert to approximately 0.0101, 0.00732 and 0.00640 with different adjustments. A core age increment near 0.009 is an explicit transport assumption, not a recovered target E3 coefficient. Mixture membership and incomplete glucose correspondence make the final projection different. Jansen's separate BMI and FPG projections are not pasted into one equation; the oriented female effects are assumptions.

The bounded BMI covariate avoids infinite moments from exponentiating unbounded lognormal BMI. All biomarkers remain positive and have finite positive integer moments. The retained producer calculates only analytic quantities and AST checks, never synthetic rows. The centered-covariate moment illustration is not a source check or a full-cohort estimate. No empirical source uncertainty is manufactured; SDs represent individual spread, no CI confidence levels are guessed, and source overlap is retained. No additional literature retrieval was used (zero queries, zero documents).

Requested next step: coordinator attaches fixed diagnostics, validates/freezes, and runs isolated trial4201, returning all 30 statistics. Inspect the complete output for implementation and structural consequences; no favorable outcome is required. Source replay, target-population validity, causal effects, assay equivalence, treatment and hematological mechanisms, structural uncertainty and downstream subgroup/tail analyses remain unassessed. No rows or target-derived reference statistics were read or produced locally.
''', encoding="utf-8")
print(json.dumps({"candidate": str(CANDIDATE), "requested_stage": "trial4201", "analytic_check": report}, ensure_ascii=False))
