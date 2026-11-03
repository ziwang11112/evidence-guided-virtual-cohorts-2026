"""Authoring and deterministic algebra only. Never imports/runs generator.py."""
import sys
sys.dont_write_bytecode = True
import ast
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if ROOT.name == "initial":
    ROOT = ROOT.parents[2]
BUNDLE = ROOT / "bundle"
CANDIDATE = BUNDLE / "candidates" / "initial"
HARNESS = Path("D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/virtual_cohort_system")


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(name, value):
    (CANDIDATE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


CANDIDATE.mkdir(parents=True, exist_ok=True)
if (CANDIDATE / "freeze.json").exists():
    raise RuntimeError("Refuse to change a frozen candidate")
task = read(BUNDLE / "task.json")
evidence = read(BUNDLE / "input" / "evidence.json")
write("evidence.json", evidence)

assumptions = [
    {"id": "A_DESIGN", "description": "Task-defined analytical design has 375 rows in each female=0/1 by age-band cell (25-39,40-54,55-69,70-79), 3000 total. Source demographic margins are contextual and are not imposed. Female is coded exactly as the task."},
    {"id": "A_AGE", "description": "Conditional on each specified age band, integer ages are discrete uniform. This completion of the within-band age distribution is assumed, not identified by source age mean/SD."},
    {"id": "A_INDEPENDENCE", "description": "BMI, fasting glucose, and HbA1c are mutually independent and independent of age and female in the selected analytical population. This factorization is an explicit unresolved-dependence completion chosen because E0 supplies no relationships. It is not an empirical zero-association finding and can be scientifically wrong. All requested adjusted associations are assumption-dependent."},
    {"id": "A_TRANSPORT", "description": "The Jansen Table 1 BMI, fasting-glucose and HbA1c marginal location and dispersion are transported unchanged to every target sex/age stratum, treating the reported SD as individual dispersion. European ancestry, older-member GWAS selection, anemia exclusion, assay and plasma/serum differences, and undocumented hours fasted are not corrected. No verified transport invariance is claimed."},
    {"id": "A_GAMMA", "description": "BMI follows a positive gamma law whose shape and scale are fixed by its chosen mean and SD. Distribution shape, skewness and all tails are assumptions; neither an observed BMI range nor a clinical plausibility cutoff is supplied. Very small and arbitrarily large positive values have mathematical support."},
    {"id": "A_BETA", "description": "Glucose and HbA1c follow separately scaled beta laws. Glucose support (0,126) mg/dL enforces the task selection; the law is directly conditional on eligibility rather than a truncated unselected disease model. HbA1c support (0,100) percent is a broad modeling bound consistent with percentage notation, not a reported population cutoff or clinical reference interval. Beta shape, density and tails are assumed."},
    {"id": "A_REPRESENTATION", "description": "Use the directly published rounded HbA1c percent mean 5.6 and SD 0.3 as the single selected unit representation. IFCC values 38 and 3 convert to 5.62824 and 0.27444, respectively; they are redundant rounded representations, not independent data. No fitting to both is attempted. Glucose uses the supplied fixed 18.0 mg/dL per mmol/L conversion."},
    {"id": "A_SELECTION", "description": "Rows are fictional adults conditional on all task eligibility, measurement-documentation and routing restrictions. The model does not generate diagnosis, fasting hours, pregnancy/lactation, anemia, medication use or anthropometry-documentation fields. Only the six permitted columns are returned. Source exclusions do not establish target anemia or medication exclusion."},
    {"id": "A_UNCERTAINTY", "description": "Reported means and SDs are fixed construction inputs, with source estimator uncertainty not supplied and not inferred from SD or n. Seeds vary individual residual draws only. External-estimate uncertainty, factorization uncertainty, shape uncertainty and transport uncertainty are unresolved; repeated seeds do not represent their posterior distribution."},
    {"id": "A_NO_REPLAY", "description": "No source-population replay is available. Target-table source-statistic comparisons are unavailable even when a margin was used as a construction anchor. Analytic checks concern the explicitly specified law, not a reconstructed source population or target validation."},
    {"id": "A_FLOAT", "description": "Implementation samples the stated laws without clipping or rescaling realized tables. If floating-point RNG output is nonfinite or outside declared open support, execution fails explicitly. Finite successful output is not the proof of population moments; the analytic law supplies that proof."},
]
parameters = {
    "design": {"n_rows": 3000, "per_cell": 375, "female_values": [0, 1], "age_bands": [[25, 39], [40, 54], [55, 69], [70, 79]]},
    "age_law": "discrete_uniform_within_each_band",
    "dependence_law": "mutually_independent_biomarkers_and_demographics",
    "bmi": {"family": "gamma", "mean": 26.5, "sd": 4.1, "unit": "kg/m^2"},
    "glucose": {"family": "scaled_beta", "mean": 91.8, "sd": 9.0, "lower": 0.0, "upper": 126.0, "unit": "mg/dL"},
    "hba1c": {"family": "scaled_beta", "mean": 5.6, "sd": 0.3, "lower": 0.0, "upper": 100.0, "unit": "%"},
    "parameter_uncertainty": "fixed_reported_marginal_inputs_no_estimator_uncertainty_model",
}
provenance = {
    "design": {"evidence_ids": [], "assumption_ids": ["A_DESIGN", "A_SELECTION"], "derivation": "Exact task quotas and support; not the source demographic distribution."},
    "age_law": {"evidence_ids": [], "assumption_ids": ["A_AGE"], "derivation": "Uniform integer allocation within each task band is a completion assumption."},
    "dependence_law": {"evidence_ids": [], "assumption_ids": ["A_INDEPENDENCE", "A_TRANSPORT"], "derivation": "Factorized joint law with no admitted dependence constraints. Zero population projections are consequences, not tuning goals."},
    "bmi": {"evidence_ids": ["J_T1_bmi_mean_task", "J_T1_bmi_sd_task"], "assumption_ids": ["A_GAMMA", "A_TRANSPORT"], "derivation": "k=(26.5/4.1)^2 and theta=4.1^2/26.5, giving gamma mean k*theta and variance k*theta^2."},
    "glucose": {"evidence_ids": ["J_T1_glucose_mean_mmol_L", "J_T1_glucose_sd_mmol_L", "J_T1_glucose_mean_mg_dL_derived", "J_T1_glucose_sd_mg_dL_derived"], "assumption_ids": ["A_BETA", "A_TRANSPORT", "A_REPRESENTATION", "A_SELECTION"], "derivation": "Single source mean/SD pair 5.1,0.5 multiplied by fixed protocol 18.0 gives 91.8,9.0. With L=126 and p=91.8/L, concentration c=p*(1-p)/(9.0/L)^2-1; alpha=p*c; beta=(1-p)*c. Original/converted values are one evidence pair."},
    "hba1c": {"evidence_ids": ["J_T1_hba1c_mean_pct", "J_T1_hba1c_sd_pct"], "assumption_ids": ["A_BETA", "A_TRANSPORT", "A_REPRESENTATION"], "derivation": "Use published percent row once. With L=100 and p=5.6/L, c=p*(1-p)/(0.3/L)^2-1; alpha=p*c; beta=(1-p)*c."},
    "parameter_uncertainty": {"evidence_ids": [], "assumption_ids": ["A_UNCERTAINTY"], "derivation": "No unsupported estimator precision or source-independent replication is introduced."},
}
spec = {"parameters": parameters, "assumptions": assumptions, "parameter_provenance": provenance}
write("model_spec.json", spec)

generator = '''"""Whole-cohort conditional model; scientific values come only from spec.

This module is submitted for controller execution only. It performs no I/O.
"""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("Whole-cohort model requires observed=None")
    p = spec["parameters"]
    if p["age_law"] != "discrete_uniform_within_each_band":
        raise ValueError("Unsupported age law")
    if p["dependence_law"] != "mutually_independent_biomarkers_and_demographics":
        raise ValueError("Unsupported dependence law")
    rng = np.random.default_rng(seed)
    d = p["design"]
    age_parts, sex_parts = [], []
    for sex in d["female_values"]:
        for lower, upper in d["age_bands"]:
            age_parts.append(rng.integers(lower, upper + 1, size=d["per_cell"]))
            sex_parts.append(np.full(d["per_cell"], sex, dtype=np.int64))
    age = np.concatenate(age_parts)
    female = np.concatenate(sex_parts)
    n = d["n_rows"]
    if len(age) != n:
        raise ValueError("Design row count does not match cell quotas")
    out = {"row_id": [f"fictional_{i + 1:06d}" for i in range(n)], "age": age, "female": female}
    for name in ("bmi", "glucose", "hba1c"):
        margin = p[name]
        mean, sd = margin["mean"], margin["sd"]
        if margin["family"] == "gamma":
            shape = (mean / sd) ** 2
            scale = sd ** 2 / mean
            values = rng.gamma(shape, scale, size=n)
            valid = np.isfinite(values) & (values > 0)
        elif margin["family"] == "scaled_beta":
            lower, upper = margin["lower"], margin["upper"]
            width = upper - lower
            proportion = (mean - lower) / width
            concentration = proportion * (1 - proportion) / (sd / width) ** 2 - 1
            alpha = proportion * concentration
            beta = (1 - proportion) * concentration
            if alpha <= 0 or beta <= 0:
                raise ValueError("Infeasible beta moment parameters")
            values = lower + width * rng.beta(alpha, beta, size=n)
            valid = np.isfinite(values) & (values > lower) & (values < upper)
        else:
            raise ValueError("Unsupported marginal family")
        if not np.all(valid):
            raise ValueError("Floating-point draw outside open support; no clipping performed")
        out[name] = values
    frame = pd.DataFrame(out, columns=["row_id", "age", "female", "bmi", "glucose", "hba1c"])
    return frame.iloc[rng.permutation(n)].reset_index(drop=True)
'''
(CANDIDATE / "generator.py").write_text(generator, encoding="utf-8")

unavailable_reason = ("The generated table has the task's equal-cell Mexican analytical design, not the Lifelines source population. "
                      "No source-population replay or source-context table is supplied; a target statistic cannot validate this source statistic. "
                      "The deterministic marginal moment calculation is separately labeled a model-law check.")
plan = {"schema_version": 1, "population": task["population"],
        "measurement": {"mode": "identity", "description": "Task-native values; no source-statistic calculation, conversion, source selection, or reweighting is applied to target rows."},
        "assumption_ids": ["A_NO_REPLAY", "A_TRANSPORT", "A_SELECTION"], "checks": []}
bindings = []
for item in evidence["items"]:
    check_id = "source_" + item["id"]
    reason = unavailable_reason if item["kind"] != "contextual" else "Measurement guidance is contextual, not a clinical source statistic; no source replay is supplied."
    plan["checks"].append({"id": check_id, "evidence_id": item["id"], "status": "not_computable", "operator": None,
                           "assumption_ids": ["A_NO_REPLAY"], "reason": reason})
    bindings.append({"check_id": check_id, "evidence_id": item["id"], "source_locator": item["locator"],
                     "definition_status": "unsupported", "source_operator": None, "weights": "not_reported",
                     "transform": "not_reported", "source_variable_units": {},
                     "source_n": {"status": "not_reported"} if item["source_id"] == "NGSP" else
                                 {"status": "reported", "value": 2921, "scope": "Eligible Lifelines sample; Table 1 margins, not target row count or analysis-specific precision."},
                     "uncertainty_role": "not_reported", "reason": reason})
write("whole_cohort_feedback.json", plan)
write("source_semantics_v1.json", {"schema_version": 1, "evidence_sha256": digest(CANDIDATE / "evidence.json"),
      "recipe_sha256": digest(CANDIDATE / "whole_cohort_feedback.json"), "bindings": bindings})
write("numerical_uptake.json", {"records": []})

decision = '''# Scientific decision

This E0 construction uses Jansen Table 1 BMI, fasting-glucose and HbA1c marginal means and individual SDs as fixed, unverified transport anchors. Gamma BMI and scaled beta glucose/HbA1c preserve their selected first two population moments; the task determines glucose eligibility and all demographic quotas. Individual realized sample moments are not forced to equal those anchors.

The joint law is explicitly factorized. E0 does not identify dependence, so the assumption of independence cannot be described as evidence of absent associations. It is a transparent baseline completion: all requested adjusted regression coefficients and the Q2-minus-Q3 contrast are zero in this model's population, while finite samples fluctuate. No required effect sign, p-value, target answer, desired coefficient or source non-marginal relationship was used to choose this law. The zero coefficients follow after factorization, rather than being fitted targets.

Age is uniform over integer values within each task band; each sex-by-band cell has exactly 375 rows. The source age mean/SD and sex proportion describe a different selection and remain contextual. The 3000 fictional rows represent an equal-stratum analytical design, not national prevalence or recovered individual measurements.

Only one HbA1c unit representation is used: directly reported 5.6% mean and 0.3 percentage-point SD. The IFCC row and its NGSP conversion remain in the evidence record but are not extra constraints. The original and 18-fold converted glucose values likewise represent one mean/SD pair. All Jansen margins are from the same source sample, and NGSP contributes measurement guidance, not an independent cohort.

Population and measurement transport is substantial: Lifelines used western-European GWAS selection and an anemia exclusion; the task supplies a Mexican analytical population with no verified anemia or medication exclusion, fasting serum rather than source plasma, a recorded 8-12-hour fast and specified anthropometry/routing restrictions. Those restrictions define the conditioning population but cannot be individually verified from fictional rows. There is no modeled correction for these differences or for unobserved selection variables. Stratum-invariant margins, distribution shapes and independence are unresolved scientific assumptions.

The BMI gamma tail extends over all positive values. HbA1c has a modeling upper bound of 100%, not an observed clinical cutoff; glucose has the required open upper limit 126 mg/dL. No fabricated measurement range is presented as source evidence. No sample is clipped, calibrated, rejected for a favorable result, or chosen for a favorable seed.

Analytic algebra and static contract/semantic validation were performed by the retained author_construction.py. No generator import, generator execution, row sampling, Monte Carlo calculation, numerical quadrature or source replay was performed by the author. Every target-as-source comparison is unavailable. This is an unfrozen submission for controller commitment and independent review.

Stopping decision: initial_final without an exploratory execution. Algebra establishes feasibility, support and finite moments, and static checks establish the declared interface. Without admitted dependence evidence, a trial table cannot resolve the principal scientific uncertainty, so no trial-based fitting or revision is justified. Successful final controller runs still must be verified. Requested regressions are supported only as analyses of this explicit independence scenario and must not be interpreted as validated target associations, causal effects or evidence of measurement savings.
'''
(CANDIDATE / "decision.md").write_text(decision, encoding="utf-8")

proof = r'''# Mathematical properties of the submitted law

## Law and generator linkage

The specification supplies every scientific constant. `generate(observed,spec,seed)` requires `observed=None`. It creates the eight `design.female_values` by `design.age_bands` cells with `design.per_cell` rows. Within each cell it draws integer age uniformly over the inclusive endpoints. It then makes independent calls to `rng.gamma` or `rng.beta` according to each margin's declared family, using the exact transformations below. These rowwise draws are independent of age and female; the final permutation only changes order. It returns only row_id, age, female, bmi, glucose, hba1c. It does not construct a covariance matrix and claim that matrix is the law.

The probability statements concern the ideal continuous sampling law implemented by these standard RNG calls. The finite machine implementation tests finiteness/open supports and raises on a boundary/nonfinite result; it performs no clipping, redraw-until-favorable procedure or sample-moment normalization. A failed floating-point draw is an execution failure, not support evidence.

## Demographic support and moments

Exactly 375 rows occupy each sex-by-age-band cell, giving exactly 3000 rows and 1500 per sex. Uniform integer age on a band [a,b] has mean (a+b)/2 and variance ((b-a+1)^2-1)/12. A uniformly selected row has equal probability 1/4 for each age band, and independent female F with P(F=1)=1/2. Thus E(A) is the average of the band means and E(A^2) is the average of each band's variance plus squared mean. The retained deterministic algebra calculates these from the spec. Age is bounded by 25 and 79, and F by 0 and 1, so all their moments exist. Rows are not identically distributed before final permutation because quotas are fixed; row selection after permutation gives the stated mixture. Quotas are exact by construction, without promising exact realized integer-age frequencies.

## BMI gamma support and moments

Let m=parameters.bmi.mean and s=parameters.bmi.sd, k=(m/s)^2 and theta=s^2/m. The generator calls Gamma(k,theta). Here k>0 and theta>0, and X has support (0,infinity). For every nonnegative integer r,

E(X^r) = theta^r Gamma(k+r)/Gamma(k).

Consequently E(X)=k theta=m; Var(X)=k theta^2=s^2; E(X^2)=m^2+s^2. Both required moments and all higher positive integer moments are finite. Positivity is guaranteed by the mathematical law, but there is no finite clinical upper bound. The tail is an assumption, not observed support.

## Glucose and HbA1c beta support and moments

For either margin let l=lower, u=upper, L=u-l, p=(m-l)/L and v=(s/L)^2. Define c=p(1-p)/v-1, alpha=pc, beta=(1-p)c. The retained algebra verifies 0<p<1 and 0<v<p(1-p); hence c,alpha,beta are positive and define a proper Beta(alpha,beta) law. The generator returns X=l+L*U for U~Beta(alpha,beta).

E(U)=alpha/(alpha+beta)=p and Var(U)=p(1-p)/(c+1)=v. Therefore E(X)=m, Var(X)=s^2, E(X^2)=m^2+s^2. Glucose is almost surely strictly in (0,126) mg/dL, exactly the numerical eligibility interval; HbA1c is almost surely in (0,100) percent under its disclosed modeling bound. Bounded variables have finite moments of every nonnegative order. The beta law is specified directly for the selected population; no unselected source law, clipping or hidden truncation normalization is being asserted.

## Joint and analytical-use moments

By A_INDEPENDENCE, all distinct biomarker/demographic cross-covariances vanish in the model, and joint second raw moments equal products of marginal means. This is a structural assumption, not evidence that the real associations vanish. Conditional HbA1c expectation is its fixed marginal mean given any of the requested predictors. Each centered/scaled predictor has positive variance: Var(age10)=Var(A)/100, Var(F)=1/4, Var(bmi5)=s_B^2/25 and Var(glucose10)=s_G^2/100. Independence makes their centered population covariance matrix diagonal with positive diagonal, so it is positive definite. Adding an intercept gives a nonsingular population second-moment matrix. This establishes the existence and uniqueness of all three population OLS projections with finite residual second moments.

The Q1 age10 coefficient, Q2 bmi5 coefficient, Q3 bmi5 coefficient, their Q2-Q3 contrast, and the secondary glucose10 coefficient are all zero under this law. Population Q1 residual RMS is s_H=0.3 percentage points. These statements are derived consequences of the assumed law, not target estimates and not fitted source coefficients. Finite-sample coefficients need not be zero. Continuous, nondegenerate biomarker draws and variation in specified demographic strata give sample full rank with probability one under the ideal law; machine/finite-sample failures must still be recorded by the controller. The displayed predictor-moment results are deterministic algebra, not simulation or numerical integration.

All required weighted means, population SDs and quantiles exist: biomarkers have proper CDFs and finite second moments; age/female have finite support. Cell-standardized weights are equal for this quota design. No exponentiation of an unbounded quadratic, explosive mixture or undefined moment is hidden in the model.

## Evidence scope and uncertainty

The six biomarker first/second moments are obtained by explicit construction from selected source means and SDs, under unverified marginal transport and family assumptions. This is not reconstruction of Lifelines or validation against Mexico. Source age/sex margins are intentionally not target constraints because the task fixes another design. Duplicate unit representations are not independent evidence. The admitted non-marginal operation list is empty, so numerical_uptake.json has records=[].

Individual residual variation comes from independent gamma/beta draws. Estimation uncertainty of source means/SDs is not given a probability model. Source overlap, assay/population transport, dependence and shape uncertainty remain unresolved and are not sampled by changing seeds. All requested associations are assumption-dependent; no causal claim or recovery of individual measurements follows from finite moments or structurally valid output.
'''
(CANDIDATE / "mathematical_properties.md").write_text(proof, encoding="utf-8")

# Deterministic algebra only: no RNG, generator import, table creation or quadrature.
moments = {}
for name in ("bmi", "glucose", "hba1c"):
    margin = parameters[name]
    m, s = margin["mean"], margin["sd"]
    if margin["family"] == "gamma":
        k, theta = (m / s)**2, s*s/m
        derived_mean, derived_variance = k*theta, k*theta*theta
        laws = {"shape": k, "scale": theta, "support": "(0,+infinity)", "positive_shapes": k > 0 and theta > 0}
    else:
        l, u = margin["lower"], margin["upper"]
        width, p = u-l, (m-l)/(u-l)
        v = (s/width)**2
        concentration = p*(1-p)/v-1
        a, b = p*concentration, (1-p)*concentration
        derived_mean = l+width*a/(a+b)
        derived_variance = width*width*a*b/((a+b)**2*(a+b+1))
        laws = {"alpha": a, "beta": b, "concentration": concentration, "support": f"({l},{u})", "positive_shapes": a > 0 and b > 0,
                "feasible_normalized_variance": 0 < v < p*(1-p)}
    assert laws["positive_shapes"]
    assert math.isclose(derived_mean, m, rel_tol=1e-12)
    assert math.isclose(derived_variance, s*s, rel_tol=1e-12)
    moments[name] = {**laws, "mean": derived_mean, "variance": derived_variance,
                     "second_raw_moment": derived_variance+derived_mean**2, "mean_error": derived_mean-m,
                     "variance_error": derived_variance-s*s, "unit": margin["unit"]}
bands = parameters["design"]["age_bands"]
band_moments = [{"lower": a, "upper": b, "mean": (a+b)/2, "variance": ((b-a+1)**2-1)/12} for a,b in bands]
age_mean = sum(b["mean"] for b in band_moments)/len(band_moments)
age_second = sum(b["variance"]+b["mean"]**2 for b in band_moments)/len(band_moments)
age_var = age_second-age_mean**2
moments["age"] = {"band_moments": band_moments, "mean": age_mean, "variance": age_var, "second_raw_moment": age_second, "unit": "year"}
moments["female"] = {"mean": 0.5, "variance": 0.25, "second_raw_moment": 0.5, "unit": "1"}
predictor_variances = {"age10": age_var/100, "female": 0.25, "bmi5": moments["bmi"]["variance"]/25, "glucose10": moments["glucose"]["variance"]/100}
assert all(v > 0 and math.isfinite(v) for v in predictor_variances.values())
assert parameters["design"]["per_cell"]*len(bands)*len(parameters["design"]["female_values"]) == task["n_rows"]
write("analytic_results.json", {
    "scope": "deterministic_probability_law_algebra_no_sampling_no_source_replay_no_target_validation",
    "model_spec_sha256": digest(CANDIDATE / "model_spec.json"),
    "generator_sha256": digest(CANDIDATE / "generator.py"),
    "moments": moments, "predictor_centered_covariance_diagonal": predictor_variances,
    "population_ols_consequences_not_empirical_estimates": {"Q1_age10": 0.0, "Q2_bmi5": 0.0, "Q3_bmi5": 0.0, "Q2_minus_Q3_bmi5": 0.0, "secondary_glucose10": 0.0, "Q1_residual_RMS": parameters["hba1c"]["sd"]},
    "source_comparisons": "unavailable", "non_marginal_operations": [],
})

# Imported trusted interface modules perform static validation, never candidate execution.
sys.path.insert(0, str(HARNESS))
from cohort_harness.contracts import validate_task, validate_evidence, validate_spec
from cohort_harness.lifecycle import validate_program, _state
from cohort_harness.semantic_feedback_v1 import preflight
validate_task(task)
validate_spec(spec, validate_evidence(evidence, task))
validate_program(CANDIDATE / "generator.py")
tree = ast.parse(generator)
assert not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in {"eval", "exec", "open", "compile", "__import__"} for n in ast.walk(tree))
semantic_report = preflight(BUNDLE, "candidates/initial")
assert len(semantic_report["checks"]) == len(evidence["items"])
assert all(row["semantic_status"] == "unavailable" for row in semantic_report["checks"])
write("static_check_results.json", {
    "scope": "static_contract_abi_and_declared_semantics_only_no_candidate_execution",
    "model_spec_sha256": digest(CANDIDATE / "model_spec.json"), "generator_sha256": digest(CANDIDATE / "generator.py"),
    "task_contract": "pass", "evidence_contract": "pass", "model_contract": "pass", "generator_AST_ABI": "pass",
    "semantic_preflight": semantic_report, "runtime_output_validation": "not_performed_author_not_authorized",
})
source_path = Path(__file__).resolve()
retained_script = CANDIDATE / "author_construction.py"
if source_path != retained_script:
    retained_script.write_bytes(source_path.read_bytes())
check_artifacts = ["analytic_results.json", "static_check_results.json", "author_construction.py"]
write("checks.json", {"scope": "fixture_only", "records": [
    {"name": "law_moments_and_support", "status": "pass", "detail": "Deterministic analytic algebra checks positive family parameters, first two moments and positive predictor variances; mathematical proof separately links formulas to generator law. No row sampling or Monte Carlo."},
    {"name": "task_evidence_model_ABI", "status": "pass", "detail": "Trusted contract validators and generator AST/ABI validation passed; generator was not imported or executed."},
    {"name": "declared_semantics", "status": "pass", "detail": "Versioned semantic preflight passed; all 17 source comparisons explicitly unavailable, no target-as-source statistics computed."},
    {"name": "source_population_replay", "status": "not_computable", "detail": "No source-population execution adapter is supplied. No source reconstruction is claimed."},
    {"name": "runtime_rows", "status": "not_computable", "detail": "Author has not executed generator. Only coordinator isolated execution may establish table-level validity."},
    {"name": "external_target_validity", "status": "not_computable", "detail": "No individual records, target statistics or hidden evaluation accessed. Transport and dependence remain assumptions."},
], "artifacts": [{"path": name, "sha256": digest(CANDIDATE / name)} for name in check_artifacts]})
state = _state(BUNDLE.resolve(), CANDIDATE.resolve(), "candidates/initial")
(ROOT / "structural_validation.json").write_text(json.dumps({
    "status": "pass", "scope": "full_unfrozen_candidate_static_validation_only", "route": state["route"],
    "candidate": "candidates/initial", "candidate_files": state["candidate_files"],
    "registry_snapshot": state["registry_snapshot"], "commitments": state["commitments"],
    "generator_imported_or_executed": False, "freeze_performed": False,
}, indent=2, allow_nan=False)+"\n", encoding="utf-8")
(ROOT / "decision.json").write_text(json.dumps({"author_id": "ENSANUT2018_E0_A03", "candidate": "candidates/initial", "action": "initial_final",
    "reason": "Positive gamma/beta marginal laws satisfy the task support and analytically established finite moments. E0 provides no dependence constraints; independence is transparently assumption-dependent. Static checks passed. An exploratory target table would not resolve that scientific uncertainty, so no trial or revision is requested."}, indent=2)+"\n", encoding="utf-8")
print(json.dumps({"status": "ready_unfrozen", "candidate": str(CANDIDATE), "required_artifacts": 9,
                  "auxiliary_artifacts": check_artifacts, "semantic_checks_unavailable": len(semantic_report["checks"]),
                  "row_count_by_construction": task["n_rows"], "author_generator_executions": 0,
                  "analytic_moments": moments}, indent=2))
