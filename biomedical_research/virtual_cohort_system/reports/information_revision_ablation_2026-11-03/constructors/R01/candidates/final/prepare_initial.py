"""Review an allowed trial and prepare a scientific no-op; no rows produced."""
from pathlib import Path
import hashlib
import json
import math
import shutil

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/"mixref_v1"
ROOT=HERE.parent.parent.parent
FEEDBACK=ROOT/"session/feedback/a01_initial_4201.json"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write_json(name,obj):
    (HERE/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+"\n",encoding="utf-8")

for source in PARENT.iterdir():
    if source.is_file() and source.name!="freeze.json":
        shutil.copyfile(source,HERE/source.name)
shutil.copyfile(FEEDBACK,HERE/"feedback_trial4201.json")
feedback=json.loads(FEEDBACK.read_text(encoding="utf-8"))
semantic=feedback["semantic_feedback_v1"]
analysis=feedback["analysis_feedback"]
assert feedback["status"]=="success" and semantic["output_link_verified"]
assert semantic["n_computable"]==30 and semantic["n_not_computable"]==1
assert analysis["n"]==3000
stats=analysis["analyses"]+analysis["diagnostics"]
assert len(stats)==30 and all(x["status"]=="computed" for x in stats)
sem_by_id={x["id"]:x for x in semantic["checks"]}
for stat in stats:
    sem=sem_by_id[stat["id"]]
    assert sem["status"]=="computed" and sem["semantic_status"]=="matched_declared"
    assert sem["calculation"]["value"]==stat["value"]
    assert sem["calculation"]["n_used"]==3000 and sem["calculation"]["n_missing_dropped"]==0
assert sem_by_id["external_context_unreplayed"]["status"]=="not_computable"
spec=json.loads((HERE/"model_spec.json").read_text(encoding="utf-8"))
fit=json.loads((HERE/"fit_report.json").read_text(encoding="utf-8"))
reference=json.loads((HERE.parent.parent/"input/reference_summary.json").read_text(encoding="utf-8-sig"))
means=[]
for var in ["age","female","bmi","glucose","hba1c"]:
    row=next(x for x in stats if x["id"]==var+"_mean")
    sd=reference["diagnostics"]["marginal"][var]["sd"]
    if var=="female":
        probability=spec["parameters"]["female_probability"]
        sd=math.sqrt(probability*(1-probability))
    se=sd/math.sqrt(3000)
    means.append({"variable":var,"trial_minus_model_mean":row["difference"],
                  "analytic_iid_model_mean_se":se,"difference_in_model_se_units":row["difference"]/se})
report={
    "kind":"initial_delivery_retain_decision",
    "parent":"mixref_v1","candidate":"mixref_initial","requested_stage":"initial_delivery_4101_4102_4103",
    "decision":"retain","scientific_change":False,
    "feedback_file":"feedback_trial4201.json","feedback_sha256":sha(FEEDBACK),
    "all_feedback_statistics_reviewed":stats,
    "semantics_review":{"computed_matched_declared":30,"not_computable_external_context":1,
                        "generator_execution_recorded":semantic["generator_execution_recorded"],
                        "output_link_verified":semantic["output_link_verified"],
                        "scientific_validity":semantic["scientific_validity"],
                        "limitations":semantic["limitations"]},
    "quality":analysis["quality"],
    "mean_variation_context":means,
    "model_mismatch_separate_from_draw_variation":{
        "bmi_quantiles":{name:{"model":fit["bmi"][name],"reference":reference["diagnostics"]["marginal"]["bmi"][name],
                               "difference":fit["bmi"][name]-reference["diagnostics"]["marginal"]["bmi"][name]}
                         for name in ["q10","median","q90"]},
        "age_shape":"The fitted age mean/variance are exact development targets, but within-bin age shape and bin masses remain assumptions. A one-year sample q90 shift is not evidence of a wrong analytic age moment.",
        "regression":"E1/E2/E3 trial coefficients differ from model population projections by +0.003200,+0.017844,-0.001788. All three model population projections were fitted analytically. One draw does not identify systematic bias; no coefficient is shifted to cancel these differences.",
        "association":"Pearson exceeds development reference by 0.035609 while Spearman differs by 0.005592. The mixed-lognormal tail gives greater sensitivity of covariance-based summaries to a finite draw. This is a plausible explanation, not a formally estimated Monte Carlo error bound.",
        "precision":"Mean SE calculations condition on the fitted IID model and omit source-estimate/structural/selection uncertainty. They are descriptive, not calibrated significance tests. Monte Carlo uncertainty for coefficients, SDs, quantiles and correlations has not been estimated."},
    "reason":"Trial verifies execution and supplies all 30 diagnostics without an implementation failure. The small known BMI quantile approximation is retained; remaining single-draw discrepancies do not justify seed-specific shifts of analytically fitted settings. Proceed to the fixed three-seed initial delivery without consuming trial4202.",
    "remaining_limitations":["Reference consistency is development fit, not external validation.","Mixture indicator independence from age/sex/BMI and nuisance latent correlations remain assumptions.","Tail shape, no measurement rounding, and lack of cluster/treatment/missingness modeling remain unassessed.","Source-context replay remains not_computable."],
    "unchanged_scientific_files":{name:{"sha256":sha(HERE/name),"identical_to_parent":(HERE/name).read_bytes()==(PARENT/name).read_bytes()} for name in ["generator.py","model_spec.json","evidence.json"]},
    "new_literature_queries":[],"new_documents":[],"local_generated_rows":0
}
write_json("trial_review.json",report)
decision=(HERE/"decision.md").read_text(encoding="utf-8")
decision=decision.replace("# Initial scientific candidate: mixref_v1", "# Initial delivery candidate: mixref_initial")
old="Requested next stage: one isolated trial, seed 4201. No local generator import or execution, source replay, or row-producing simulation has occurred. No new literature queries or documents were used. Root will attach fixed semantics, validate/freeze and execute. The trial will assess implementation and finite-draw behavior; a favorable result is not required."
new="Requested next stage: fixed initial delivery at seeds 4101, 4102, 4103. Isolated trial4201 succeeded with 3000 valid rows, no nonpositive glycemia and no duplicate measurement rows. All 30 allowed statistics and their declared semantic bindings were reviewed; source-context replay remains not computable. The exact trial feedback is bound as feedback_trial4201.json. No local generator import, local row-producing execution, or new retrieval occurred."
assert old in decision
decision=decision.replace(old,new)
decision+="\n\nAfter trial4201, the scientific construction is retained byte-for-byte. The five mean deviations are about -1.38 to +1.44 fitted-model standard errors. E1/E2/E3 are 0.058146, 0.419937 and 0.006319, versus model projections 0.054946, 0.402093 and 0.008107. Pearson is 0.696577 and Spearman 0.367049. These single-draw differences do not establish systematic model bias; the heavier-tail covariance summaries can vary more than rank association. No formal Monte Carlo bounds for regression or correlation were supplied or invented. BMI's small analytic quantile mismatch is acknowledged separately in trial_review.json. The one-year age q90 difference does not motivate changing the assumed age shape from one draw. I decline a second initial trial because it would not resolve the remaining structural underidentification. The trial's outputs are not selected for delivery; the required three fixed delivery seeds will all be used.\n"
(HERE/"decision.md").write_text(decision,encoding="utf-8")
checks=json.loads((HERE/"checks.json").read_text(encoding="utf-8"))
for rec in checks["records"]:
    if rec["name"]=="generated_table_validity_and_diagnostics":
        rec["status"]="pass"
        rec["detail"]="Coordinator isolated trial4201 succeeded, output linkage verified, 3000 rows, all 30 diagnostics computed with matched declared semantics, zero nonpositive glycemia and zero duplicate measurement rows. The candidate generator/spec/evidence are byte-identical to that trial. This does not validate scientific truth or guarantee future draws."
checks["records"].append({"name":"trial_feedback_review_and_scientific_noop","status":"pass","detail":"Read and bound complete actual trial4201 feedback; crosschecked all 30 analysis values against semantic calculations. Retain generator/spec/evidence byte-for-byte; distinguish known analytic BMI quantile approximation from single-draw variation in trial_review.json. No new cohort or retrieval."})
for name in ["feedback_trial4201.json","trial_review.json"]:
    checks["artifacts"].append({"path":name,"sha256":sha(HERE/name)})
write_json("checks.json",checks)
print(json.dumps({"candidate":"mixref_initial","request":"initial_delivery_4101_4102_4103","scientific_change":False,"all_statistics_reviewed":30,"unchanged_scientific_files":report["unchanged_scientific_files"],"local_generated_rows":0},indent=2))
