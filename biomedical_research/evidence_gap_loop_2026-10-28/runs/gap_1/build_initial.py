"""Build the auditable initial candidate using approved aggregate sources only."""
from pathlib import Path
import json
import hashlib
import importlib.util
import numpy as np
import pandas as pd
from scipy.stats import gamma, lognorm

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "initial"

def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")

def art(sha, extension="txt"):
    return {"path": "literature/approved/" + sha + "." + extension, "sha256": sha}

tw = art("47555a144a38e836dab7da8c676a10f51089bc8f6f7776df74dbf31c464261ac")
uk = art("ef8b2d42b5285e1da10139a60ac85e536dc53805f89f8c90d949fb28fbc2c37a")
us = art("7ce280d9f0e58c111cc32cf2811a59e31c88b67e87465251c0abe983e180d078")

sources = [
    {"id": "S_TW", "identifier": "PMC6627528; DOI:10.3390/genes10060440",
     "population": "Taiwan Biobank; 6184 men and 8353 women aged 30-70, recruitment described as 2012-2016; volunteer cohort, not U.S. probability sample.",
     "measurement": "HDL-C in mg/dL from biobank biochemical examinations; detailed assay and fasting protocol not specified in this article. Table 2 reports mean plus SE, not SD.",
     "cohort_overlap": "One Taiwan Biobank analysis. No overlap known with MIDUS or ALSPAC/MEIRU. Related Taiwan articles would not be independent confirmations.",
     "approved_artifacts": [tw, art("23728f05bcc689d1e4d9549f25d163243c4dd6b3a174225f34a7758c1514eaa8", "xml")]},
    {"id": "S_UK", "identifier": "PMC7364601; DOI:10.1186/s12916-020-01648-0",
     "population": "Urban Malawi MEIRU and predominantly White UK ALSPAC; adults 2277 Malawi and 6323 UK, plus adolescents. Adult UK women mean age 47.9 and men 53.3.",
     "measurement": "Fasting enzymatic serum lipids in Malawi (Beckman AU480) and fasting plasma lipids in UK (Technicon RA500), mmol/L.",
     "cohort_overlap": "ALSPAC parents and offspring share families. MEIRU and ALSPAC are distinct cohorts; article's related MEIRU work is overlapping, not independent.",
     "approved_artifacts": [uk, art("4a057ec880a83b63313481262caf810bbf820486609fbff354ee2006dd7c4c70", "xml")]},
    {"id": "S_US", "identifier": "PMC8818198; DOI:10.1186/s12944-021-01608-4",
     "population": "1903 White and African American MIDUS biomarker participants, 860 men and 1043 women; 2004-2006 and 2011-2016 cohorts; ages 25-86 across cohorts. Biomarker volunteers more educated, Milwaukee African American oversampling; includes diabetes and medication use.",
     "measurement": "12-hour fasted blood; traditional clinical lipid panel in mg/dL at Meriter certified laboratory; source also studies HDL peroxide, a different endpoint not modeled here. Source used log HDL-C in analyses to normalize distribution.",
     "cohort_overlap": "Two MIDUS biomarker cohorts pooled within one article, not two independent confirmations. No known overlap with other selected sources.",
     "approved_artifacts": [us, art("5741e7f9b757dd870b2dff4b00f2d6aa95e6c2fcba0438a53fb4e07c2fe80d9a", "xml")]}
]

def ev(eid, sid, locator, estimand, variables, adjustment, reported, uncertainty, applicability, use, bridge):
    return {"id": eid, "source_id": sid, "locator": locator, "estimand": estimand,
            "variables": variables, "adjustment": adjustment, "reported": reported,
            "uncertainty": uncertainty, "applicability": applicability, "model_use": use,
            "bridge_assumptions": bridge}

cells = {
    "male": [
        {"group": "White nondiabetic", "n": 629, "age_mean": 56, "age_sd": 13, "bmi_mean": 29.1, "bmi_sd": 4.8},
        {"group": "African American nondiabetic", "n": 85, "age_mean": 50, "age_sd": 10, "bmi_mean": 29.1, "bmi_sd": 6.7},
        {"group": "White diabetic", "n": 114, "age_mean": 64, "age_sd": 12, "bmi_mean": 31.7, "bmi_sd": 5.9},
        {"group": "African American diabetic", "n": 32, "age_mean": 56, "age_sd": 10, "bmi_mean": 31.7, "bmi_sd": 6.7}],
    "female": [
        {"group": "White nondiabetic", "n": 692, "age_mean": 55, "age_sd": 12, "bmi_mean": 28.0, "bmi_sd": 6.1},
        {"group": "African American nondiabetic", "n": 160, "age_mean": 49, "age_sd": 11, "bmi_mean": 33.1, "bmi_sd": 8.1},
        {"group": "White diabetic", "n": 98, "age_mean": 59, "age_sd": 11, "bmi_mean": 33.7, "bmi_sd": 9.0},
        {"group": "African American diabetic", "n": 93, "age_mean": 54, "age_sd": 11, "bmi_mean": 36.8, "bmi_sd": 9.8}]
}
source_moments = {"male": {"mean": 50.4, "sd": 16.5}, "female": {"mean": 62.8, "sd": 18.8}}
evidence = [
    ev("E_TW_BMI", "S_TW", "Table 2, Sex rows; BMI definitions in Methods 2.2",
       "Unadjusted HDL-C means and standard errors within sex and BMI category",
       ["hdl", "bmi", "sex"], "Stratified by sex and BMI category; not jointly age-adjusted",
       {"categories": ["BMI<18.5", "18.5<=BMI<24", "24<=BMI<27", "BMI>=27"],
        "male_mean": [61.83, 51.92, 46.75, 43.25], "male_se": [1.52, 0.25, 0.21, 0.21], "male_n": [75, 2192, 2308, 1609],
        "female_mean": [66.55, 60.72, 54.66, 51.06], "female_se": [0.79, 0.19, 0.27, 0.30], "female_n": [333, 4766, 1963, 1291], "unit": "mg/dL"},
       "Reported SEs quantify mean uncertainty; category BMI means and age composition are unavailable. SE is not an individual residual SD.",
       "Large adult sample supplies sex-stratified direction and scale, but category means conflate within-category covariates and cohort-specific selection.",
       "Normal-to-obese mean ratio determines each sex's log-BMI slope at assumed representative BMI values. Other categories are checks, not fitted targets.",
       ["A_BMI_BRIDGE", "A_TRANSPORT", "A_MEAN_FORM"]),
    ev("E_TW_AGE", "S_TW", "Table 3, Age rows; Statistical Analysis 2.4",
       "Adjusted additive HDL-C mean contrasts versus ages 30-40", ["hdl", "age", "bmi", "sex"],
       "Model lists exercise, WHR, BMI category, body fat category, sex, age category, smoking, drinking, coffee and vegetarian diet; full design details/covariance unavailable",
       {"age_categories": ["30-40", "40-50", "51-60", "61-70"], "beta_mg_dl": [0, 0.75841, 1.18484, 0.87361], "p_values": [None, 0.003, "<0.0001", 0.0068]},
       "No coefficient SE or covariance reported. P-values are not residual variance. Printed age categories overlap at 40, limiting exact bin interpretation.",
       "Evidence for modest nonmonotone age pattern in ages 30-70, conditional on more predictors than the generator possesses.",
       "Piecewise-linear interpolation of log relative mean through assumed bin centers, flat outside extreme centers. Common across sexes.",
       ["A_AGE_BRIDGE", "A_TRANSPORT"]),
    ev("E_UK_SHAPE", "S_UK", "Results paragraphs following Fig. 1; Fig. 2 caption and Methods Statistical analysis",
       "Qualitative assessment of adiposity-lipid association shape and population/sex heterogeneity",
       ["hdl", "bmi", "sex", "age"], "Sex/age-stratified; age-only and covariate-adjusted regressions",
       {"description": "Most associations across adiposity fifths were approximately linear; inverse BMI-HDL associations in all four sex/age groups; BMI-HDL associations stronger in UK than Malawi and adult UK women than men.", "numeric_hdl_slope": None},
       "Numerical slopes and category-distribution tables are in a PDF supplement unsupported by gateway. One Results sentence labels a positive LDL-context coefficient HDL; this internally inconsistent sentence is not used.",
       "Supports direction and warns against assuming universal coefficients, but cannot numerically calibrate this model or its curvature.",
       "Context only; retain modest smooth monotonic BMI structure rather than invent threshold effects or extract graph pixels.", ["A_MEAN_FORM", "A_TRANSPORT"]),
    ev("E_US_MOMENTS", "S_US", "Results, Descriptive statistics, paragraph beginning 'On average, men had lower HDL-C levels'",
       "Sex-specific marginal arithmetic HDL-C mean and SD", ["hdl", "sex"], "Unadjusted marginal sex groups",
       {"male": source_moments["male"], "female": source_moments["female"], "unit": "mg/dL", "n_male": 860, "n_female": 1043},
       "SDs describe people, not mean uncertainty. Values rounded; sex-specific mean SEs can be approximated as SD/sqrt(n) but no precision weighting is used.",
       "Contemporaneous U.S. adults with diabetes and medication use resemble eligibility better than a healthy volunteer-only reference, but selection, age, ethnicity and fasting differ.",
       "Primary anchors for mean and marginal variance after model-based removal of age/BMI mean variation under an explicit source-distribution bridge.",
       ["A_TRANSPORT", "A_SOURCE_MOMENT_CLOSURE", "A_RESIDUAL"]),
    ev("E_US_COVARIATES", "S_US", "Table 2, n, Age (yrs.) and BMI rows",
       "Sex/race/diabetes-stratum counts and marginal predictor means and SDs", ["age", "bmi", "sex"], "Stratified on sex, race and diabetes",
       cells, "Joint age-BMI distributions, within-stratum covariance, BMI support and all cross-moments missing; values rounded.",
       "Supports a working source-moment calculation, not recovery of source microdata or exact source operator.",
       "Weighted four-stratum normal marginal moment closure within sex; zero within-cell covariance assumed. No latent race or diabetes labels are assigned to target rows.",
       ["A_SOURCE_MOMENT_CLOSURE"]),
    ev("E_US_MEASUREMENT", "S_US", "Methods: Blood collection and clinical lab results; Statistical analyses; Strengths and limitations",
       "Measurement, selection and distributional context", ["hdl"], "Not an association estimate",
       {"fasting_hours": 12, "hdl_analysis_transformation": "natural logarithm to normalize distribution", "biomarker_selection": "More educated than full MIDUS; African American recruitment concentrated in Milwaukee"},
       "Log transformation of marginal HDL does not establish conditional lognormal residuals. Assay harmonization with target direct serum HDL is not demonstrated.",
       "Relevant to location, tails and transport; HDL-C distinct from HDLperox throughout extraction.",
       "Motivates positive skewed family, with gamma sensitivity; no assay offset estimated.", ["A_RESIDUAL", "A_MEASUREMENT", "A_TRANSPORT"])
]
save("evidence.json", {"sources": sources, "evidence": evidence})

assumptions = [
    {"id": "A_TRANSPORT", "description": "Transfer Taiwan within-sex BMI dependence and modest adjusted age pattern to U.S. adults; transfer MIDUS sex-specific location/variance after covariate adjustment. No ethnicity, disease, medication, fasting or temporal transport adjustment is identifiable. These bridges may fail."},
    {"id": "A_BMI_BRIDGE", "description": "Treat Taiwan normal-category mean as representative at BMI 21.25 (midpoint 18.5-24) and obese-category mean at assumed BMI 30.0. The true mean BMI of either category is unknown. A log ratio over this assumed 8.75-unit gap estimates a continuous log-mean slope; this is not a reported adjusted slope."},
    {"id": "A_MEAN_FORM", "description": "Log conditional mean is linear in BMI, with sex-specific slopes. Thus absolute decline gradually attenuates while relative decline is constant. Extrapolate this form to BMI 14.1-77.5; no target HDL has informed it. This functional form is not identified by category means."},
    {"id": "A_AGE_BRIDGE", "description": "Convert the additive Taiwan age contrasts to ratios around assumed HDL 55 mg/dL. Use bin centers 35,45,55.5,65.5, interpolate log ratios and hold endpoint values outside these centers. Center at age 50. Apply same age function in both sexes; unknown age-by-sex interaction is not evidence of zero."},
    {"id": "A_SOURCE_MOMENT_CLOSURE", "description": "For source-only calibration, approximate each reported MIDUS sex/race/diabetes cell's BMI and age as independent normal marginal distributions with the reported means/SDs and cell weights. This is a mathematical moment closure, not claimed source microdata. Independence, normality and sufficient moments are unverified; true source expectation operator cannot be computed from available aggregates."},
    {"id": "A_RESIDUAL", "description": "Conditional HDL is lognormal with sex-specific constant log SD. Solve this SD from source sex-specific marginal variance after subtracting model-implied covariate mean variance under moment closure. It represents individual variation including unmeasured determinants, not between-source uncertainty. No residual family or homoscedastic log scale is established by the article."},
    {"id": "A_MEASUREMENT", "description": "Treat source fasting plasma/serum HDL-C and target direct serum HDL-C as comparable in mg/dL with no estimated assay correction. Lack of calibration evidence does not establish equality."},
    {"id": "A_CENTER", "description": "BMI 27 and age 50 are algebraic centering points; re-centering with corresponding intercept transformation changes no predictions."},
    {"id": "A_NUMERICS", "description": "Source-only age integration uses 128-point Gauss-Hermite quadrature; BMI exponential moments are analytic. Integration order is numerical, not a biological parameter. Rounded source SDs are treated as population moment estimates for calibration."}
]
parameters = {
    "bmi_reference": 27.0,
    "bmi_log_slopes_by_sex": {"male": float(np.log(43.25 / 51.92) / (30.0 - 21.25)), "female": float(np.log(51.06 / 60.72) / (30.0 - 21.25))},
    "age_knots_years": [35.0, 45.0, 55.5, 65.5],
    "age_relative_means": [1.0, 1.0 + 0.75841 / 55.0, 1.0 + 1.18484 / 55.0, 1.0 + 0.87361 / 55.0],
    "age_reference": 50.0,
    "conditional_means_at_reference_by_sex": {},
    "residual_log_sd_by_sex": {}
}

def age_effect(a):
    vals = np.log(parameters["age_relative_means"])
    return np.interp(a, parameters["age_knots_years"], vals) - np.interp(parameters["age_reference"], parameters["age_knots_years"], vals)

def source_multiplier_moments(sex, nodes=128):
    z, weights = np.polynomial.hermite.hermgauss(nodes)
    weights = weights / np.sqrt(np.pi)
    total_n = sum(c["n"] for c in cells[sex])
    beta = parameters["bmi_log_slopes_by_sex"][sex]
    output = []
    for power in (1, 2):
        m = 0.0
        for c in cells[sex]:
            ages = c["age_mean"] + np.sqrt(2) * c["age_sd"] * z
            age_m = np.sum(weights * np.exp(power * age_effect(ages)))
            bmi_m = np.exp(power * beta * (c["bmi_mean"] - parameters["bmi_reference"]) + (power * beta * c["bmi_sd"]) ** 2 / 2)
            m += c["n"] / total_n * age_m * bmi_m
        output.append(float(m))
    return output

calibration = {}
for sex in ("male", "female"):
    m1, m2 = source_multiplier_moments(sex)
    target_mean, target_sd = source_moments[sex]["mean"], source_moments[sex]["sd"]
    base = target_mean / m1
    sigma2 = np.log((target_sd ** 2 + target_mean ** 2) / (base ** 2 * m2))
    assert sigma2 > 0
    parameters["conditional_means_at_reference_by_sex"][sex] = float(base)
    parameters["residual_log_sd_by_sex"][sex] = float(np.sqrt(sigma2))
    calibration[sex] = {"mean_multiplier": m1, "second_multiplier": m2, "marginal_mean": target_mean,
                        "marginal_sd": target_sd, "implied_mean_variance": float(base ** 2 * (m2 - m1 ** 2)),
                        "average_conditional_variance": float(base ** 2 * m2 * np.expm1(sigma2))}

def prov(eids, aids, derivation):
    return {"evidence_ids": eids, "assumption_ids": aids, "derivation": derivation}

provenance = {
    "bmi_reference": prov([], ["A_CENTER"], "Algebraic reference BMI 27 kg/m^2."),
    "bmi_log_slopes_by_sex": prov(["E_TW_BMI", "E_UK_SHAPE"], ["A_BMI_BRIDGE", "A_MEAN_FORM", "A_TRANSPORT"], "male=log(43.25/51.92)/(30-21.25); female=log(51.06/60.72)/(30-21.25). UK article is qualitative context only, not a numeric source for either coefficient."),
    "age_knots_years": prov(["E_TW_AGE"], ["A_AGE_BRIDGE"], "Chosen representative centers of printed source age categories: 35,45,55.5,65.5; not observed category mean ages."),
    "age_relative_means": prov(["E_TW_AGE"], ["A_AGE_BRIDGE", "A_TRANSPORT"], "Ratios=1+[0,0.75841,1.18484,0.87361]/55; 55 mg/dL is an assumed conversion scale, not a reported intercept."),
    "age_reference": prov([], ["A_CENTER"], "Algebraic age reference 50 years."),
    "conditional_means_at_reference_by_sex": prov(["E_US_MOMENTS", "E_US_COVARIATES", "E_TW_BMI", "E_TW_AGE"], ["A_SOURCE_MOMENT_CLOSURE", "A_MEAN_FORM", "A_AGE_BRIDGE", "A_TRANSPORT", "A_NUMERICS"], "Let T=exp(beta*(BMI-27)+g(age)-g(50)). Under documented four-cell source moment closure, base=reported sex-specific marginal mean/E[T]. Calibration details and rebuild script preserve the transformation."),
    "residual_log_sd_by_sex": prov(["E_US_MOMENTS", "E_US_COVARIATES", "E_US_MEASUREMENT"], ["A_SOURCE_MOMENT_CLOSURE", "A_RESIDUAL", "A_TRANSPORT", "A_NUMERICS"], "sigma=sqrt(log((source_SD^2+source_mean^2)/(base^2*E[T^2]))). HDL draw is lognormal(log(base*T)-sigma^2/2,sigma). Marginal log-normalization mentioned by source is contextual, not proof of conditional family.")
}
spec = {"version": "initial-1", "family": "Sex-specific lognormal conditional distribution with smooth log-linear BMI mean and interpolated age profile",
        "outcome": {"name": "hdl", "unit": "mg/dL", "synthetic": True}, "parameters": parameters,
        "parameter_provenance": provenance, "assumptions": assumptions,
        "equation": "E[HDL|bmi,age,sex]=base_sex*exp(beta_sex*(bmi-27)+g(age)-g(50)); log HDL ~ Normal(log E[HDL]-sigma_sex^2/2,sigma_sex^2). g interpolates log age_relative_means with endpoint holding.",
        "calibration_details": {"method": "Assumption-dependent source moment closure; not the actual unknown source joint distribution", "hermite_nodes": 128, "sex_moments": calibration},
        "uncertainty": "Fixed scientific specification, stochastic individual residual only. Sampling multiple draws does not quantify evidence/transport uncertainty.",
        "focused_countermodel": "Gamma conditional family with identical mean and variance. First two source moments cannot discriminate its low-HDL and extreme-high tail from lognormal.",
        "applicability": "Source-informed virtual association scenarios; not target validation, national estimation, patient reconstruction or causal effects."}
save("model_spec.json", spec)

# Source/implementation checks. These never use a target HDL or generate the target cohort.
module_spec = importlib.util.spec_from_file_location("gap1_initial_generator", OUT / "generator.py")
module = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(module)
toy = pd.DataFrame({"row_id": ["invented_d", "invented_b", "invented_a", "invented_c"],
                    "bmi": [14.1, 27.0, 77.5, 35.0], "age": [20, 50, 79, 65], "sex": [1, 2, 1, 2]}, index=[91, 12, 24, 3])
before = toy.copy(deep=True)
global_before = np.random.get_state()
a = module.generate(toy, spec, 314159)
b = module.generate(toy, spec, 314159)
c = module.generate(toy, spec, 314160)
global_after = np.random.get_state()
global_unchanged = all(np.array_equal(x,y) if isinstance(x,np.ndarray) else x==y for x,y in zip(global_before,global_after))
assert toy.equals(before) and a.iloc[:,:4].equals(toy)
assert a.equals(b) and not a["hdl"].equals(c["hdl"])
assert list(a.columns) == ["row_id", "bmi", "age", "sex", "hdl"]
assert np.isfinite(a["hdl"]).all() and (a["hdl"] > 0).all() and global_unchanged
assert len(module.generate(toy.iloc[:0], spec, 3)) == 0

def moments_at(bmi, age, sex):
    mean = parameters["conditional_means_at_reference_by_sex"][sex] * np.exp(parameters["bmi_log_slopes_by_sex"][sex] * (bmi - parameters["bmi_reference"]) + age_effect(age))
    sigma = parameters["residual_log_sd_by_sex"][sex]
    return float(mean), float(mean ** 2 * np.expm1(sigma ** 2)), sigma

grid_results = []
for sex in ("male", "female"):
    means = [moments_at(x, a0, sex)[0] for x in (10,14.1,20,27,35,50,77.5,100) for a0 in (20,35,50,65,79)]
    grid_results.append({"sex": sex, "mean_min": min(means), "mean_max": max(means), "finite_positive": bool(np.isfinite(means).all() and min(means)>0)})

moment_tests = []
tail_challenge = []
for s, sex in enumerate(("male", "female"), 1):
    for bmi0 in (22.0, 35.0):
        mean, variance, sigma = moments_at(bmi0, 50, sex)
        invented = pd.DataFrame({"row_id": np.arange(100000), "bmi": bmi0, "age": 50, "sex": s})
        draws = module.generate(invented, spec, 1000+s+int(bmi0))["hdl"].to_numpy()
        mean_z = (draws.mean()-mean)/np.sqrt(variance/len(draws))
        variance_ratio = draws.var(ddof=1)/variance
        assert abs(mean_z)<5 and abs(variance_ratio-1)<0.04
        moment_tests.append({"sex":sex,"invented_bmi":bmi0,"age":50,"n":len(draws),"seed":1000+s+int(bmi0),"expected_mean":mean,"empirical_mean":float(draws.mean()),"expected_sd":float(np.sqrt(variance)),"empirical_sd":float(draws.std(ddof=1)),"mean_MC_z":float(mean_z),"variance_ratio":float(variance_ratio),"pass":True})
        shape, scale = mean**2/variance, variance/mean
        threshold = 40.0 if sex=="male" else 50.0
        tail_challenge.append({"sex":sex,"invented_bmi":bmi0,"age":50,"same_mean":mean,"same_sd":float(np.sqrt(variance)),"low_threshold_mg_dl":threshold,
                               "lognormal_p_low":float(lognorm.cdf(threshold,s=sigma,scale=np.exp(np.log(mean)-sigma**2/2))),
                               "gamma_p_low":float(gamma.cdf(threshold,a=shape,scale=scale)),
                               "lognormal_p_above_100":float(lognorm.sf(100,s=sigma,scale=np.exp(np.log(mean)-sigma**2/2))),
                               "gamma_p_above_100":float(gamma.sf(100,a=shape,scale=scale))})

source_checks = []
for sex in ("male","female"):
    base=parameters["conditional_means_at_reference_by_sex"][sex]
    sigma=parameters["residual_log_sd_by_sex"][sex]
    m1,m2=source_multiplier_moments(sex)
    predicted_mean=base*m1
    predicted_sd=np.sqrt(base**2*np.exp(sigma**2)*m2-predicted_mean**2)
    coarse=source_multiplier_moments(sex,nodes=64)
    source_checks.append({"source":"S_US","sex":sex,"operator_status":"Actual operator unavailable; conditional-on-assumptions moment closure only","reported_mean":source_moments[sex]["mean"],"closure_mean":float(predicted_mean),"reported_sd":source_moments[sex]["sd"],"closure_sd":float(predicted_sd),"max_relative_multiplier_difference_64_vs_128_nodes":float(max(abs(np.array(coarse)/np.array([m1,m2])-1)))})

tw_check = []
for sex, obs in (("male",[61.83,51.92,46.75,43.25]),("female",[66.55,60.72,54.66,51.06])):
    reps=np.array([17.0,21.25,25.5,30.0])
    pred=obs[1]*np.exp(parameters["bmi_log_slopes_by_sex"][sex]*(reps-21.25))
    tw_check.append({"source":"S_TW","sex":sex,"operator_status":"Actual category-integrated operator unavailable; assumed representative-point check only, with Taiwan normal-category intercept restored","assumed_bmi_representatives":reps.tolist(),"reported_category_means":obs,"representative_point_means":pred.tolist(),"difference":(pred-np.array(obs)).tolist(),"interpretation":"Normal and obese anchors match by construction; underweight and overweight discrepancies expose limited shape identification; U.S. intercept is not expected to reproduce Taiwan levels."})

hash_checks = []
for source in sources:
    for artifact in source["approved_artifacts"]:
        digest=hashlib.sha256((ROOT/artifact["path"]).read_bytes()).hexdigest()
        assert digest==artifact["sha256"]
        hash_checks.append({"path":artifact["path"],"sha256_matches":True})
eids={e["id"] for e in evidence}
aids={a0["id"] for a0 in assumptions}
assert set(parameters)==set(provenance)
for p0 in provenance.values():
    assert set(p0["evidence_ids"])<=eids and set(p0["assumption_ids"])<=aids
    assert p0["evidence_ids"] or p0["assumption_ids"]
checks={"scope":"Actual numerical/source-only and invented-input checks. No true target outcome or target generated cohort tests.",
        "implementation":{"exact_column_order":True,"input_values_index_and_order_preserved":True,"input_not_mutated":True,"same_seed_reproducible":True,"different_seed_changes_draws":True,"global_numpy_rng_unchanged":global_unchanged,"positive_finite_invented_outputs":True,"empty_input":True,"provenance_ids_resolve":True},
        "invented_grid":{"bmi_values":[10,14.1,20,27,35,50,77.5,100],"age_values":[20,35,50,65,79],"results":grid_results},
        "monte_carlo_checks":moment_tests,"source_moment_closure_checks":source_checks,"taiwan_shape_diagnostics":tw_check,
        "focused_tail_countermodel":tail_challenge,"artifact_hash_checks":hash_checks,
        "source_limitations":["MIDUS true joint covariate distribution unavailable, so no exact genuine source-operator validation claimed.","Taiwan category BMI means and full joint age-sex-BMI distribution unavailable; no invented microdata treated as observations.","UK numerical supplement is unsupported PDF; no hidden or rejected content accessed."]}
save("artificial_checks.json",checks)

gaps = [
    {"id":"G_LOCATION","component":"Conditional location and U.S. applicability","affected_analysis":"Absolute HDL levels, sex contrast, low-HDL prevalence","evidence_status":"Usable marginal U.S. moments; assumption-dependent conditional bridge","consequence":"Direct Taiwan intercept transport would differ materially from available U.S. summaries.","next_action":"Independent review of MIDUS extraction and calibration; consider a comparable U.S. source if an attainable lead appears.","status":"acted","resolution":"Retrieved MIDUS and used its sex-specific mean/SD; no population weights or exact joint distribution available.","priority":1},
    {"id":"G_BMI","component":"BMI dependence and shape","affected_analysis":"BMI-adjusted regressions, nonlinear contrasts and sex-by-BMI interaction","evidence_status":"Within-sex category means usable; continuous slope and extrapolation are bridges","consequence":"Different representative BMI assumptions change slope; categories do not identify extreme-obesity behavior.","next_action":"Review may motivate a source with continuous BMI slope or category BMI means; UK supplement lead was checked but unsupported.","status":"acted","resolution":"Selected log-linear BMI mean using two category ratios, checked the unused categories, and retained explicit extrapolation limitation.","priority":2},
    {"id":"G_AGE","component":"Age shape and modifiers","affected_analysis":"Age association, age-by-sex and age-by-BMI analyses, 20-29 and 71-79 subgroup comparisons","evidence_status":"Adjusted mixed-sex age contrasts, missing sex-specific age estimates and young/old support","consequence":"Endpoint holding and common age profile may miss age-specific sex differences or cohort effects.","next_action":"Use remaining budget after review for an attainable primary-study lead reporting age-by-sex HDL distributions.","status":"open","resolution":"Initial model uses modest source-derived age pattern; no claim that unreported interactions are absent.","priority":3},
    {"id":"G_VARIANCE","component":"Conditional variability and tails","affected_analysis":"Low-HDL classification, upper-tail quantiles, heteroskedasticity-sensitive analyses","evidence_status":"Marginal sex SDs usable; residual distribution and covariate-specific log scale unreported","consequence":"Identical mean/variance can produce different low and high tail probabilities.","next_action":"Focused gamma-versus-lognormal sensitivity with identical conditional moments; seek quantiles or low-HDL frequencies if review supplies an attainable source lead.","status":"acted","resolution":"Variance decomposition and actual gamma/lognormal countermodel calculations completed; family and scale law remain assumptions.","priority":2},
    {"id":"G_JOINT","component":"Source predictor distribution and omitted factors","affected_analysis":"Conditional calibration and transport of BMI/age associations","evidence_status":"Cell counts and marginal predictor moments available; covariance and joint source law missing","consequence":"Moment closure can match reported means/SDs while misallocating residual versus predictor variation; omitted disease/race effects need not transport.","next_action":"Check sensitivity to source covariance or challenge closure at review; do not construct source microdata as if observed.","status":"unresolved","resolution":"Exact source operator cannot be computed. Independent within-cell normal moment closure is declared and used only as a calibration bridge.","priority":2},
    {"id":"G_MEASUREMENT","component":"Measurement and selection","affected_analysis":"All absolute-scale analyses and transport","evidence_status":"Source fasting and laboratory context available; assay-equivalence data missing","consequence":"Fasting, serum/plasma and assay differences may shift location/spread; biobank and biomarker participation may select different covariate-conditioned distributions.","next_action":"Retain no estimated assay offset; reassess if review identifies concrete assay calibration evidence.","status":"unresolved","resolution":"No numerical adjustment is identifiable from accessed sources. Difference is kept as a limitation, not absorbed as claimed precision.","priority":4},
    {"id":"G_UNCERTAINTY","component":"Evidence uncertainty versus individual residual variation","affected_analysis":"Any inferential confidence interval and repeated-draw interpretation","evidence_status":"Sampling SEs for some category means but no full parameter covariance or transport uncertainty","consequence":"Repeated synthetic draws cannot represent model uncertainty or add independent biomedical evidence.","next_action":"Retain fixed auditable model and separately report finite countermodel results, not a calibrated uncertainty interval.","status":"unresolved","resolution":"No arbitrary confidence weighting or transport-variance inflation; only individual residual randomness is sampled.","priority":4}
]
save("gaps.json", gaps)
actions = [
    {"gap_id":"G_BMI","action":"retrieve","evidence_artifacts":[tw,uk],"model_change":"Dependence structure and analysis qualification","reason":"Sought sex-specific adiposity-HDL constraints and distinguishing shape evidence. Retrieved main texts; UK numerical supplement is unsupported PDF and was not bypassed."},
    {"gap_id":"G_LOCATION","action":"retrieve","evidence_artifacts":[us],"model_change":"Primary location and variance anchors changed from Taiwan-only candidate to U.S. MIDUS moments before initial freeze","reason":"Country/selection transport was consequential for absolute HDL and low-HDL analyses; U.S. primary source was an obtainable metadata lead."},
    {"gap_id":"G_LOCATION","action":"source_check","evidence_artifacts":[us],"model_change":"Parameter derivation plus qualification","reason":"Verified sex-specific HDL-C means/SDs in Results and predictor counts/moments in Table 2. Excluded all HDLperox regression coefficients because their endpoint differs."},
    {"gap_id":"G_JOINT","action":"source_check","evidence_artifacts":[us],"model_change":"Assumption-dependent intercept and residual-SD calibration","reason":"Computed source moment closure using reported cell weights, age/BMI moments and explicit within-cell independence. True source operator is unavailable; no claim that assumed distributions are known."},
    {"gap_id":"G_BMI","action":"source_check","evidence_artifacts":[tw],"model_change":"Analysis qualification; no after-draw tuning","reason":"Tested Taiwan representative-point predictions at four assumed BMI values. Two anchors match by construction, unused groups reveal departures; their actual category-integrated operator is unavailable."},
    {"gap_id":"G_AGE","action":"retain","evidence_artifacts":[tw],"model_change":"Age profile chosen using Table 3 contrasts with explicit endpoint holding","reason":"A modest nonmonotone age pattern is available; richer interactions and young/old extensions lack sufficient evidence. Preserve six queries for review-directed follow-up."},
    {"gap_id":"G_VARIANCE","action":"sensitivity","evidence_artifacts":[us],"model_change":"Tail analysis qualified; selected lognormal family retained","reason":"Actual invented-profile gamma/lognormal calculations preserve mean/variance while changing threshold probabilities. Reported marginal log transformation motivates but cannot identify lognormal residuals."},
    {"gap_id":"G_MEASUREMENT","action":"retain","evidence_artifacts":[us,tw,uk],"model_change":"Measurement assumption only","reason":"Sources differ in fasting, sample and assay description. No numerical calibration offset can be extracted."},
    {"gap_id":"G_UNCERTAINTY","action":"stop","evidence_artifacts":[tw,us],"model_change":"No numerical uncertainty layer added","reason":"Available aggregate precision cannot quantify transport/model uncertainty; random residuals are not used as a substitute."},
    {"gap_id":"G_LOCATION","action":"stop","evidence_artifacts":[us,tw,uk],"model_change":"Initial candidate frozen pending review","reason":"Six metadata queries and three maintext downloads supplied the key means, variation and dependence constraints. Recent broad age searches returned mostly less-applicable endpoints; concrete UK supplement is unsupported. Stop unfocused retrieval and reserve six queries/nine downloads for the review turn."}
]
save("actions.json",actions)
print(json.dumps({"parameters":parameters,"source_closure":source_checks,"tail_challenge":tail_challenge,"files":[str(p) for p in sorted(OUT.iterdir())]},indent=2))
