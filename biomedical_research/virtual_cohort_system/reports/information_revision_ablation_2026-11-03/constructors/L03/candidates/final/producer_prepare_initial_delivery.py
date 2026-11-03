"""Bind the real isolated trial to an unchanged initial model. No row execution."""
from pathlib import Path
import hashlib
import json
import math
import shutil

root = Path(__file__).resolve().parent
source = root / "b/candidates/l03_mixture_trial_v1"
dest = root / "b/candidates/l03_mixture_initial_v1"
dest.mkdir(parents=True, exist_ok=False)
for name in ["generator.py", "model_spec.json", "evidence.json", "analytic_checks.json", "retrieval_log.json", "producer_build_candidate.py"]:
    shutil.copyfile(source/name, dest/name)
feedback_path = root / "session/feedback/a01_initial_4201.json"
feedback = json.loads(feedback_path.read_text(encoding="utf-8"))
assert feedback["status"] == "success"
assert feedback["semantic_feedback_v1"]["output_link_verified"] is True
diagnostics = feedback["analysis_feedback"]["diagnostics"]
analyses = feedback["analysis_feedback"]["analyses"]
assert len(diagnostics) + len(analyses) == 30
assert all(x["status"] == "computed" for x in diagnostics + analyses)
shutil.copyfile(feedback_path, dest / "feedback_trial4201.json")

spec = json.loads((dest/"model_spec.json").read_text(encoding="utf-8"))
p = spec["parameters"]
a = p["age_model"]
s = p["sex_model"]
# Finite exact enumeration of age support, not a generated sample or cohort.
support = range(a["minimum"], a["maximum"]+1)
w = [math.exp(-0.5*((age-a["location"])/a["scale"])**2) for age in support]
wsum = sum(w)
mean_age = sum(age*weight for age,weight in zip(support,w))/wsum
var_age = sum((age-mean_age)**2*weight for age,weight in zip(support,w))/wsum
mean_female = sum(weight/(1+math.exp(-(math.log(s["reference_probability"]/(1-s["reference_probability"]))+s["age_logodds"]*(age-a["location"])))) for age,weight in zip(support,w))/wsum

def dump(name, value):
    (dest/name).write_text(json.dumps(value, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")

review = {
    "kind": "retain",
    "feedback_id": "a01_initial_4201",
    "all_statistics_reviewed": [x["id"] for x in diagnostics+analyses],
    "reported_execution_status": feedback["status"],
    "reported_linkage_verified": True,
    "scientific_model_changed": False,
    "deterministic_probability_checks": {
        "scope": "Exact finite age-support sum and Bernoulli expectation; no synthetic rows.",
        "model_age_mean": mean_age,
        "model_age_sd": math.sqrt(var_age),
        "model_female_fraction": mean_female,
        "age_mean_monte_carlo_sd_for_n3000": math.sqrt(var_age/3000),
        "female_mean_monte_carlo_sd_for_n3000": math.sqrt(mean_female*(1-mean_female)/3000)
    },
    "sampling_vs_model": [
        "Age kernel location 53.5 is not its truncated/discretized distribution mean; exact model expectations are reported separately from the observed trial summaries.",
        "For age and sex, iid model-based sampling SDs are analytic. They are not source precision or transport uncertainty.",
        "Only one numerical trial was examined. Monte Carlo uncertainty for biomarker quantiles, correlations and regressions is not empirically estimated.",
        "The Pearson/Spearman gap is a plausible structural consequence of shared tail membership; the single draw does not quantify that attribution.",
        "E3 is an adjusted linear projection from a mixture and is not identical to the conditional log-HbA1c age coefficient or its central-scale derivative.",
        "No source-population replay or target-reference comparison exists. Differences from external source statistics are not diagnosed as target model mismatch."
    ],
    "decision_reason": "No execution/positivity/duplicate or estimability defect was reported. All 30 outcomes are coherent with the declared scenario. There is no independently supplied target information identifying a scientific parameter correction. Retain rather than fitting one seed to differently selected studies.",
    "remaining_limitations": ["Unidentified target distribution and transport", "Strong tail coupling is an assumption", "Source replay not computable", "No household/treatment/measurement-error model", "No calibrated structural uncertainty"],
    "next_stage": "initial_delivery_4101_4102_4103"
}
dump("trial_review.json", review)
artifacts=[]
for name in ["analytic_checks.json", "feedback_trial4201.json", "trial_review.json"]:
    artifacts.append({"path":name,"sha256":hashlib.sha256((dest/name).read_bytes()).hexdigest()})
dump("checks.json", {"scope":"source_only", "records":[
    {"name":"static_and_scalar_checks","status":"pass","detail":"Retained original AST/scalar checks, with additional exact enumeration of the specified 40-point age support and conditional female probabilities. No generator import or local row execution."},
    {"name":"isolated_trial4201_receipt_and_statistics_review","status":"pass","detail":"Actual coordinator feedback reports success and output linkage verified, 3000 rows, no nonpositive glucose/HbA1c, no duplicate measurement rows, and all 30 statistics computed; each statistic was reviewed. This pass concerns report status and scenario inspection, not source or target scientific validation."},
    {"name":"external_context_unreplayed","status":"not_computable","detail":"The actual semantic report has zero computable source checks. No source-population reconstruction was executed."},
    {"name":"target_reference_fit","status":"not_computable","detail":"No target reference values/comparisons were supplied. External source summaries cannot identify CHNS model mismatch."},
    {"name":"biomarker_monte_carlo_uncertainty","status":"not_computable","detail":"A single isolated trial does not estimate repeated-seed uncertainty for biomarker quantiles, correlations and OLS coefficients."}
],"artifacts":artifacts})

decision = '''# Initial delivery decision: retain the model after trial 4201

The complete authorized feedback was read: all 25 marginal summaries, both glycemic correlations and all three OLS coefficients. The isolated backend reported success, verified output linkage, 3000 rows, no nonpositive glycemic values, no duplicate measurement rows and full-rank analysis designs. This verifies an executed candidate under the supplied contract, not scientific target validity.

Trial BMI mean/SD were 23.8124/3.3613; glucose 5.4381/1.3608; HbA1c 5.7481/0.7934. Glucose median/q90 were 5.1472/6.2990 and HbA1c median/q90 were 5.5993/6.2535. The shared high-biomarker component can plausibly produce a stronger Pearson correlation (0.7800) than rank correlation (0.5450); this gap is a structural modeling choice worth retaining visibly, not proof of target recovery or source agreement. In particular, Bao's 0.619 Pearson and MIND's 0.529 Spearman concern different selected populations and measurements. Their numerical differences from these task outputs are not source replay residuals.

Task E1/E2/E3 were 0.02531 percent/(kg/m^2), 0.45040 percent/(mmol/L) and 0.00573 percent/year. These are projections of a nonlinear mixture. They need not equal the direct conditional log coefficients, the central-scale age derivative, or the differently conditioned published projections. The observed positive E3 is not a criterion being forced; age evidence and the model rationale were fixed before execution.

The observed age mean 54.092 and female fraction 0.56267 are compared only with deterministic expectations under the declared model in trial_review.json. The age kernel location is not the mean after restricting to integer ages 35-74. Analytic iid sampling SDs for those two marginal means distinguish finite-draw variation from their intended model values. There is only one trial, so repeated-seed uncertainty for biomarker tails, associations and OLS projections has not been estimated. No target reference is supplied, and there is no identified target mismatch justifying parameter adjustment.

The initial delivery uses exactly the same generator.py, model_spec.json and evidence.json bytes as the frozen trial. A new unfrozen candidate binds the complete actual trial report and this review; the frozen trial is unchanged. The optional second initial trial is skipped because no unresolved implementation issue warrants another draw and no desired p-value or favorable seed is being sought. Requested next stage is initial delivery at the fixed seeds 4101, 4102 and 4103.

The original decision rationale, provenance and mathematical support argument remain in the retained model and producer artifacts. Source-only is the harness's legacy checks scope for declared input evidence, not a label of independent validation. Source replay, CHNS transport, treatment/clustering/measurement error, extreme-tail validity and calibrated structural uncertainty remain unassessed. External retrieval remains zero queries and zero new documents.
'''
(dest/"decision.md").write_text(decision,encoding="utf-8")
shutil.copyfile(Path(__file__),dest/"producer_prepare_initial_delivery.py")
print(str(dest))
