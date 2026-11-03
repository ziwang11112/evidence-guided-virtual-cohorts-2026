"""Prepare candidate artifacts only. Never imports or runs the generator."""
from pathlib import Path
import ast
import hashlib
import json
import math
import shutil

ROOT = Path(__file__).resolve().parent
CANDIDATE = ROOT / "b" / "candidates" / "l03_mixture_trial_v1"
CANDIDATE.mkdir(parents=True, exist_ok=False)

def dump(name, value):
    (CANDIDATE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

evidence = json.loads((ROOT / "b/input/compiled_evidence.json").read_text(encoding="utf-8"))
dump("evidence.json", evidence)

assumptions = [
    {"id": "A_TARGET", "description": "The requested CHNS analytical population is not identified by the external study summaries. All distributional transfers are declared scenarios; no reference summaries or participant data are available in this assignment. No diabetes, treatment, pregnancy or anemia exclusion is imposed."},
    {"id": "A_AGE", "description": "Integer ages 35 through 74 have probabilities proportional to a Gaussian kernel with location 53.5 and scale 11.5 years. These are target scenario choices, loosely placing the adult cohort between the unrestricted Shanghai and older MIND contexts; neither kernel parameter is a reported target moment."},
    {"id": "A_SEX", "description": "Female=1 is drawn with logistic probability having reference probability 0.55 at age 53.5 and log-odds age coefficient 0.006/year. Source count fractions suggest female-majority selected samples, but do not identify target composition or age dependence. The chosen probability is not their pooled estimate."},
    {"id": "A_BMI", "description": "BMI is conditionally lognormal with reference median 23.7 kg/m^2, female log shift -0.025, and age log slope +0.0008 below age 55 and -0.002 above 55, centered at age 53.5. Log residual SD is log(25.9/21.4)/(2*Phi^-1(.75)), using Shanghai quartiles under an explicit lognormal approximation; this does not relabel quartiles as SDs. A mild age peak and the reduced sex contrast are transport assumptions, not recovered source associations."},
    {"id": "A_TAIL", "description": "A latent high-biomarker component has reference probability 0.075, log-odds age coefficient 0.025/year, log-BMI coefficient 1.6 and centered female coefficient -0.10. This is a mathematical tail component, not a diagnosis or prevalence estimate. Its probability reflects a scenario allowing diagnosed and treated people in the target, unlike Shanghai/Lifelines exclusions. Joint tail membership and all component parameters remain unidentified by the source evidence."},
    {"id": "A_BIOMARKERS", "description": "Conditional glucose and HbA1c are a two-component bivariate lognormal model. Reference component medians are glucose [5.1,8.9] mmol/L and HbA1c [5.55,7.8] percent; log SDs are [0.11,0.24] and [0.062,0.17]. The central levels/spreads are informed by Shanghai median/quartile context and the wider MIND all-diagnosis dispersion, without equating populations or fitting source means. High-component levels and spreads are explicit assumptions. Log-residual correlation 0.45 in each component is an assumption informed qualitatively by the distinct positive Bao Pearson and MIND Spearman associations; it is neither reported coefficient nor a conversion between them."},
    {"id": "A_EFFECTS", "description": "Conditional log-glucose coefficients are age 0.0015/year, log-BMI 0.20 and centered female -0.01. Conditional log-HbA1c coefficients are age 0.0015/year, log-BMI 0.025 and centered female -0.005. The direct age term yields about 0.0083 percentage points/year at central HbA1c, a scenario informed by Pani's adjusted 0.010 and Jansen's 0.08*0.09148=0.0073184 with different conditioning. The BMI pathway is split between biomarker shifts and tail composition; Jansen separate projections are not concatenated into this conditional law. Sex effects are assumed, not inferred from Jansen's unresolved coding. Task OLS coefficients emerge from this nonlinear joint law and are not installed as reported source values."},
    {"id": "A_ERRORS", "description": "Fresh Gaussian residuals for BMI and the two biomarkers, Bernoulli component and sex draws, and the age draw are conditionally independent except for the declared biomarker residual correlation and covariate pathways. This is an explicit closure assumption, not inference from absent source evidence. All rows are iid conditional on fixed scenario parameters; no household, geographic, treatment, measurement-error, imputation or survey-weight model is supplied."},
    {"id": "A_SUPPORT", "description": "Age is bounded and biomarkers/BMI are exponentials of finite Gaussian linear terms; biomarker dependence uses log BMI, not BMI in an exponential. Each mixture probability is bounded. Consequently all positive-order polynomial moments exist, biomarkers and BMI have positive support, and no clipping or per-draw moment matching is applied. Extreme biological tails are not independently validated."},
    {"id": "A_USE", "description": "Generated OLS projections and marginals are descriptive consequences of one scenario, not causal effects, calibrated uncertainty, source replay, national estimates or validation of CHNS recovery. Seed variation is Monte Carlo variation only. Source coefficient intervals have unknown confidence levels, SDs describe individuals and Pani mean SEs do not determine individual variance."}
]
params = {
    "n_rows": 3000,
    "age_model": {"minimum": 35, "maximum": 74, "location": 53.5, "scale": 11.5},
    "sex_model": {"reference_probability": 0.55, "age_logodds": 0.006},
    "bmi_model": {"reference_median": 23.7, "age_knot": 55.0, "age_below_log_slope": 0.0008, "age_above_log_slope": -0.002, "female_log_shift": -0.025, "log_sd": math.log(25.9/21.4)/(2*0.6744897501960817)},
    "tail_model": {"reference_probability": 0.075, "age_logodds": 0.025, "log_bmi_logodds": 1.6, "female_logodds": -0.10},
    "biomarker_model": {"glucose_medians": [5.1,8.9], "hba1c_medians": [5.55,7.8], "glucose_log_sds": [0.11,0.24], "hba1c_log_sds": [0.062,0.17], "residual_correlation": 0.45, "glucose_age_log_slope": 0.0015, "glucose_log_bmi_slope": 0.20, "glucose_female_log_shift": -0.01, "hba1c_age_log_slope": 0.0015, "hba1c_log_bmi_slope": 0.025, "hba1c_female_log_shift": -0.005}
}
def prov(e, a, d):
    return {"evidence_ids": e, "assumption_ids": a, "derivation": d}
provenance = {
    "n_rows": prov([], ["A_TARGET"], "Fixed task requirement: 3000 synthetic complete rows."),
    "age_model": prov(["M_B_AGE_MEDIAN", "M_B_AGE_Q1", "M_B_AGE_Q3", "M_M_AGE_MEAN", "M_J_AGE_MEAN"], ["A_AGE", "A_TARGET"], "Task fixes support 35-74; location 53.5 and scale 11.5 are assumed kernel parameters, not pooled or matched source moments."),
    "sex_model": prov(["M_B_FEMALE_FRACTION", "M_M_FEMALE_FRACTION"], ["A_SEX", "A_TARGET"], "Reference probability 0.55 and age coefficient 0.006 are explicit target composition choices; reported count ratios have no estimator precision here."),
    "bmi_model": prov(["M_B_BMI_MEDIAN", "M_B_BMI_Q1", "M_B_BMI_Q3", "M_M_BMI_MEAN", "M_M_BMI_SD", "E_SOURCE_RECONCILIATION"], ["A_BMI", "A_TARGET", "A_SUPPORT"], "Only log SD is algebraically derived, under a chosen lognormal approximation to Bao quartiles. Median 23.7, knot 55, age slopes 0.0008/-0.002 and female shift -0.025 are explicit assumptions. Age and sex shifts are applied before the lognormal residual, so these source quartiles are not claimed as marginal target constraints."),
    "tail_model": prov(["M_M_FSG_SD", "M_M_HBA1C_PERCENT_SD", "E_SOURCE_RECONCILIATION"], ["A_TAIL", "A_TARGET", "A_ERRORS"], "All four tail parameters are assumptions, motivated by target disease inclusion and between-study spread differences without estimating disease prevalence from those differences."),
    "biomarker_model": prov(["M_B_FPG_MEDIAN", "M_B_FPG_Q1", "M_B_FPG_Q3", "M_B_HBA1C_PERCENT_MEDIAN", "M_B_HBA1C_PERCENT_Q1", "M_B_HBA1C_PERCENT_Q3", "M_M_FSG_MEAN", "M_M_FSG_SD", "M_M_HBA1C_PERCENT_MEAN", "M_M_HBA1C_PERCENT_SD", "R_BAO_PEARSON", "R_MIND_SPEARMAN", "R_JANSEN_BMI", "R_JANSEN_FPG", "U_NGSP_SCALE", "E_SOURCE_RECONCILIATION"], ["A_BIOMARKERS", "A_EFFECTS", "A_TARGET", "A_ERRORS", "A_SUPPORT", "A_USE"], "All model entries are scenario assumptions with the detailed source-context rationale in A_BIOMARKERS/A_EFFECTS. The NGSP multiplier is used only in contextual age-slope arithmetic. No Jansen or Pani coefficient, Bao Pearson, MIND Spearman, serum-plasma correction or source precision is imposed as a target coefficient.")
}
dump("model_spec.json", {"parameters": params, "assumptions": assumptions, "parameter_provenance": provenance})

generator = '''"""Evidence-informed scenario; executed only by the supplied isolated harness."""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("Whole-cohort generation requires observed=None")
    p = spec["parameters"]
    n = int(p["n_rows"])
    rng = np.random.default_rng(seed)
    a = p["age_model"]
    ages = np.arange(a["minimum"], a["maximum"] + 1, dtype=np.int64)
    weights = np.exp(-0.5 * ((ages - a["location"]) / a["scale"]) ** 2)
    age = rng.choice(ages, size=n, p=weights / weights.sum())
    da = age - a["location"]
    s = p["sex_model"]
    eta_s = np.log(s["reference_probability"] / (1-s["reference_probability"])) + s["age_logodds"] * da
    female = (rng.random(n) < 1 / (1 + np.exp(-eta_s))).astype(np.int64)
    df = female - s["reference_probability"]
    b = p["bmi_model"]
    knot = b["age_knot"]
    age_bmi = b["age_below_log_slope"] * (np.minimum(age, knot) - min(a["location"], knot))
    age_bmi += b["age_above_log_slope"] * (np.maximum(age-knot, 0) - max(a["location"]-knot, 0))
    log_bmi_centered = age_bmi + b["female_log_shift"] * df + b["log_sd"] * rng.standard_normal(n)
    bmi = b["reference_median"] * np.exp(log_bmi_centered)
    t = p["tail_model"]
    eta_t = np.log(t["reference_probability"] / (1-t["reference_probability"]))
    eta_t = eta_t + t["age_logodds"] * da + t["log_bmi_logodds"] * log_bmi_centered + t["female_logodds"] * df
    # Stable expit; no rejection sampling, clipping or supplementary cohort.
    tail_probability = np.exp(-np.logaddexp(0, -eta_t))
    component = (rng.random(n) < tail_probability).astype(np.int64)
    m = p["biomarker_model"]
    zg = rng.standard_normal(n)
    independent_h = rng.standard_normal(n)
    rho = m["residual_correlation"]
    zh = rho * zg + np.sqrt(1-rho*rho) * independent_h
    glucose = np.exp(np.log(np.asarray(m["glucose_medians"])[component])
        + m["glucose_age_log_slope"] * da
        + m["glucose_log_bmi_slope"] * log_bmi_centered
        + m["glucose_female_log_shift"] * df
        + np.asarray(m["glucose_log_sds"])[component] * zg)
    hba1c = np.exp(np.log(np.asarray(m["hba1c_medians"])[component])
        + m["hba1c_age_log_slope"] * da
        + m["hba1c_log_bmi_slope"] * log_bmi_centered
        + m["hba1c_female_log_shift"] * df
        + np.asarray(m["hba1c_log_sds"])[component] * zh)
    return pd.DataFrame({"row_id": [f"L03_{i+1:05d}" for i in range(n)],
        "age": age, "female": female, "bmi": bmi, "glucose": glucose, "hba1c": hba1c},
        columns=["row_id", "age", "female", "bmi", "glucose", "hba1c"])
'''
(CANDIDATE / "generator.py").write_text(generator, encoding="utf-8")
tree = ast.parse(generator)
fun = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "generate"]
assert len(fun) == 1 and len(fun[0].args.args) == 3
assert not fun[0].args.vararg and not fun[0].args.kwarg and not fun[0].args.kwonlyargs

analytic = {
    "scope": "Static syntax/signature plus deterministic scalar algebra only; no generated rows, source replay or target comparison.",
    "generator_ast_parse": "pass",
    "generate_abi": "three positional parameters, synchronous top-level function",
    "bmi_log_sd_from_assumed_lognormal_quartiles": params["bmi_model"]["log_sd"],
    "biomarker_residual_covariance_eigenvalues": [1-0.45,1+0.45],
    "jansen_context_age_percent_per_year_table3ii": 0.08*0.09148,
    "jansen_context_age_percent_per_year_table3iii": 0.07*0.09148,
    "central_direct_hba1c_age_derivative_at_reference": 5.55*0.0015,
    "source_replay": "not_computable",
    "target_output_check": "not_computable_before_isolated_trial"
}
dump("analytic_checks.json", analytic)
digest = hashlib.sha256((CANDIDATE / "analytic_checks.json").read_bytes()).hexdigest()
dump("checks.json", {"scope": "source_only", "records": [
    {"name": "static_and_scalar_checks", "status": "pass", "detail": "AST syntax/signature checked without import or execution; derived BMI log SD and residual covariance eigenvalues calculated analytically. Legacy source_only denotes declared input evidence, not an independent scientific validation."},
    {"name": "external_context_unreplayed", "status": "not_computable", "detail": "Source-population numerical replay is not supplied. Task output diagnostics cannot reconstruct differently selected/weighted source contexts."},
    {"name": "output_and_analysis_diagnostics", "status": "not_computable", "detail": "Await isolated trial4201. No row-producing calculation has been performed locally."}
], "artifacts": [{"path": "analytic_checks.json", "sha256": digest}]})

decision = '''# Scientific decision: initial trial candidate

This is one explicit CHNS whole-cohort scenario, using a covariate-dependent two-component bivariate lognormal law for glucose and HbA1c. A central component captures the narrow Shanghai central distribution; a high-biomarker component permits the broader all-diagnosis population in the task. Component membership is not a generated diabetes diagnosis. Integer age, female category and BMI are also generated, with their dependence stated in the specification.

The existing literature supports positive glycemic association and provides age evidence, but does not identify the target joint distribution. Bao's unadjusted Pearson 0.619 and MIND's unadjusted Spearman 0.529 remain different statistics. Neither is installed as a conditional residual correlation. Jansen's BMI and FPG projections are separate models, not a joint regression equation. Its restored age coefficients and Pani's survey-weighted sex/BMI/FPG-adjusted 0.010/year inform the chosen small positive conditional age contribution without equating either to the task's unweighted OLS estimand. Jansen Table 3 III has extra adjustment terms and is not obtained by merely deleting them. The unit conversion is arithmetic, not new evidence or assay equivalence.

The central medians, residual spreads, tail probability and tail values are scenario assumptions with source rationale, not a pooled meta-analysis. Source populations differ in age support, disease exclusions, ethnicity, rural/urban selection, fasting and serum/plasma processing. No universal serum/plasma correction is applied. MIND means and individual SDs, Bao quartiles, Pani mean SEs and regression intervals retain their original meanings. Source uncertainty does not justify precision weights. Multiple Jansen rows, their converted representations and Pani strata share cohorts and add no independent sample information; the reconciliation audit is derivative evidence rather than an extra study.

All positive-order moments exist: age/sex are bounded, log BMI is Gaussian conditional on them, biomarker log values depend linearly on log BMI and Gaussian residuals, and mixture weights are bounded. The model avoids exponentiating an unbounded raw lognormal BMI. All BMI/glucose/HbA1c values are strictly positive; no clipping or sample-moment correction is used. Residual independence beyond declared pathways is an assumption, not a consequence of missing evidence.

No extra retrieval was performed: source queries 0, original documents 0. The source record is the supplied compiled_evidence.json; the source audit and NGSP artifact were read in the assigned bundle. No patient records, other roots, earlier candidates or target reference data were read. The retained build_candidate.py produces JSON/code and performs AST/scalar checks only; it never imports or calls generate.

Requested next step: freeze and execute one isolated numerical trial with seed 4201. This supports inspection of all 30 target-task statistics; it is not source replay. Source replay, target population validity, causal analyses, subgroup/tail fidelity, treatment effects, household clustering, survey weighting and transport uncertainty remain unassessed. Any subsequent candidate will bind actual trial feedback and retain the frozen trial unchanged.
'''
(CANDIDATE / "decision.md").write_text(decision, encoding="utf-8")
dump("retrieval_log.json", {"queries": [], "new_original_documents": [], "new_source_artifacts_for_registration": [], "overlap": "Supplied repeated Jansen projections share Lifelines participants; Pani strata/coefficient share NHANES; the audit and unit conversions add no independent empirical evidence."})
shutil.copyfile(Path(__file__), CANDIDATE / "producer_build_candidate.py")
print(str(CANDIDATE))
