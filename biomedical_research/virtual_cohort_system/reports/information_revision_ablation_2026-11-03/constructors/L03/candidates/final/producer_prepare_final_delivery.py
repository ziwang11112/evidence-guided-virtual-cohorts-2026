"""Review supplied aggregate numbers and bind retained final artifacts; no row execution."""
from pathlib import Path
import hashlib
import json
import shutil
import statistics

root = Path(__file__).resolve().parent
source = root / "b/candidates/l03_mixture_initial_v1"
dest = root / "b/candidates/l03_mixture_final_retained_v1"
dest.mkdir(parents=True, exist_ok=False)
for name in ["generator.py", "model_spec.json", "evidence.json", "analytic_checks.json", "retrieval_log.json", "producer_build_candidate.py", "producer_prepare_initial_delivery.py", "feedback_trial4201.json", "trial_review.json"]:
    shutil.copyfile(source/name, dest/name)
feedback_path = root / "session/feedback/initial.json"
feedback = json.loads(feedback_path.read_text(encoding="utf-8"))
assert feedback["stage"] == "initial"
assert len(feedback["runs"]) == 3
shutil.copyfile(feedback_path, dest/"feedback_initial.json")
values = {}
for run in feedback["runs"]:
    assert run["status"] == "success"
    assert run["semantic_feedback_v1"]["output_link_verified"] is True
    reported = run["analysis_feedback"]["diagnostics"] + run["analysis_feedback"]["analyses"]
    assert len(reported) == 30
    assert all(x["status"] == "computed" for x in reported)
    for item in reported:
        values.setdefault(item["id"], []).append(item["value"])

def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+"\n",encoding="utf-8")

review = {
    "kind":"retain",
    "stage_reviewed":"initial",
    "feedback_artifact":"feedback_initial.json",
    "seeds":[run["seed"] for run in feedback["runs"]],
    "all_30_statistics_reviewed":{
        name:{"values_in_seed_order":v,"mean_across_three_draws":statistics.mean(v),"sample_sd_across_three_draws":statistics.stdev(v),"minimum":min(v),"maximum":max(v)}
        for name,v in values.items()
    },
    "summary_scope":"Arithmetic on the 90 already-supplied summary values; no synthetic rows, generator import, replay, extra cohorts or fitted parameters. Three-draw SDs are imprecise conditional simulation summaries and not source, target-reference or transport uncertainty.",
    "findings":[
        "All three isolated runs reported success, output linkage, 3000 rows, zero nonpositive glycemic measurements, zero duplicate measurement rows and estimable OLS designs.",
        "Age and female statistics vary around the declared distribution; binary quantiles and age discretization have their intended forms. All 25 marginal summaries were reviewed, not only glycemic relationships.",
        "Glucose and HbA1c medians/means and their broader upper portions are coherent with a central component and a high-biomarker tail. Tail incidence is not a validated diabetes prevalence.",
        "Pearson correlation remains 0.8026-0.8222 and Spearman 0.5449-0.5853. The persistently strong Pearson association is a structural feature of shared component membership, not merely the initial trial's draw. It is stronger numerically than the Bao source statistic, but a CHNS mismatch cannot be estimated without source-context or target-reference information.",
        "E1 ranges from 0.01480 to 0.02799, illustrating conditional finite-draw variation in a relatively small projection; the range is not used to select a favorable seed.",
        "E2 ranges 0.48012-0.50127 and E3 ranges 0.00438-0.00562. Neither is forced toward Jansen or Pani coefficients, which have distinct selection, conditioning, assay and/or weighting. E3 is not the model's direct log-age coefficient.",
        "No extraction/unit mismatch or implementation defect was identified. No independent target information identifies a correction to the transport assumptions."
    ],
    "change":"No generator, model specification or evidence changes; final candidate adds actual aggregate-feedback binding and review.",
    "further_trials":"Not requested: no unresolved numerical implementation issue; more seeds do not supply target truth.",
    "same_seed_final_expectation":"With identical generator/specification and fixed seeds, final delivery should reproduce initial rows. Those repeats are integrity checks, not new independent scientific evidence."
}
dump(dest/"final_review.json",review)
identity = {name:{"initial_sha256":hashlib.sha256((source/name).read_bytes()).hexdigest(),"final_sha256":hashlib.sha256((dest/name).read_bytes()).hexdigest(),"identical":(source/name).read_bytes()==(dest/name).read_bytes()} for name in ["generator.py","model_spec.json","evidence.json"]}
assert all(item["identical"] for item in identity.values())
dump(dest/"retention_identity.json",identity)
final_decision={
    "reason":"Retain the initial scientific model after reviewing all 30 statistics across three fixed-seed runs. All runs executed successfully and no implementation or extraction defect was identified. Persistent Pearson/tail coupling and OLS projections are transparent scenario consequences; admitted evidence does not establish their CHNS target error or an alternative correction. Altering them to fit differently selected source statistics would overstate transport knowledge. Preserve the frozen prior candidates, bind actual feedback, and request final delivery without additional trials.",
    "kind":"retain",
    "addressed_findings":[
        "Reviewed all 25 marginal statistics, both glycemic correlations and all three OLS projections for seeds 4101, 4102 and 4103.",
        "Bound the complete actual initial feedback and retained trial4201 feedback; summarized only supplied numerical summaries.",
        "Separated finite-draw variation, including E1 variation, from the persistent high Pearson association induced by shared tail structure.",
        "Kept distinct the direct conditional log-age term, generated E3 linear projection, Jansen's differently adjusted coefficients and Pani's weighted coefficient.",
        "Confirmed byte-identical generator/specification/evidence between initial and final candidate; no scientific revision or favorable-seed selection.",
        "Skipped optional post-initial trials because additional generated data do not resolve target identifiability."
    ],
    "remaining_limitations":[
        "No CHNS development-reference summaries or participant data were supplied; target-population fidelity is unassessed.",
        "Source-population replay remains not_computable, with zero computable semantic source checks.",
        "The positive all-diagnosis tail, its age/BMI dependence and shared membership create strong glucose-HbA1c association; their adequacy is not identified by the sources.",
        "The age/sex/BMI composition, residual dependence and biomarker transport remain explicit assumptions; published means, SDs, quartiles, weighted results and projections are not interchangeable.",
        "Three-draw variability does not quantify source sampling, measurement, model-selection or transport uncertainty.",
        "Treatment, household/geographic clustering, imputation and survey weighting are not modeled; causal and individual clinical applications are unassessed.",
        "Identical-seed final reruns of the retained model are expected to reproduce initial rows and provide no additional independent evidence."
    ]
}
dump(root/"FINAL_AUTHOR_DECISION.json",final_decision)
dump(dest/"final_author_decision.json",final_decision)
artifacts=[]
for name in ["analytic_checks.json","feedback_trial4201.json","trial_review.json","feedback_initial.json","final_review.json","retention_identity.json","final_author_decision.json"]:
    artifacts.append({"path":name,"sha256":hashlib.sha256((dest/name).read_bytes()).hexdigest()})
dump(dest/"checks.json",{"scope":"source_only","records":[
    {"name":"static_and_scalar_checks","status":"pass","detail":"Retained AST/signature and deterministic support/moment calculations. No local generator import or row generation occurred."},
    {"name":"initial_delivery_report_review","status":"pass","detail":"All three supplied isolated run reports indicate success and verified output linkage; all 30 statistics per run reviewed. Summary calculations use only provided diagnostic numbers. This is not a scientific validation pass."},
    {"name":"retained_scientific_artifact_identity","status":"pass","detail":"SHA256 and byte comparisons confirm final generator.py, model_spec.json and evidence.json are identical to the initial delivered candidate."},
    {"name":"external_context_unreplayed","status":"not_computable","detail":"All initial semantic reports declare zero computable source checks. No source-population reconstruction was executed."},
    {"name":"target_fidelity_and_transport","status":"not_computable","detail":"Own generated statistics have no supplied target-reference comparator. Source populations/measurements/adjustments/weights differ; no common generating law is identified."},
    {"name":"structural_uncertainty_calibration","status":"not_computable","detail":"Three fixed-seed draws summarize conditional simulation variability only; no probability distribution over structural or transport assumptions is justified."}
],"artifacts":artifacts})
decision = '''# Final decision: retain the scientific model

The final candidate preserves generator.py, model_spec.json and evidence.json exactly. All 30 diagnostics were reviewed across each of the three initial delivery seeds, and the actual aggregate feedback is bound in checks.json. The earlier trial feedback is also preserved. New artifacts document this review and the identity check; no row-producing code was run locally.

All three isolated executions succeeded with 3000 rows, positive glucose/HbA1c, no duplicate measurement rows, verified output linkage and full-rank analysis designs. The 25 marginal summaries have the intended integer/binary/positive distributions. Glucose means are 5.438-5.457 mmol/L, with SD 1.345-1.444; HbA1c means are 5.738-5.771 percent, with SD 0.815-0.887. Full values, quantiles and ranges for every diagnostic are in final_review.json.

Pearson correlation is persistently 0.803-0.822, while Spearman is 0.545-0.585. Strong Pearson association is therefore a model feature visible across the fixed seeds, not a peculiarity to dismiss as one-draw noise. Shared high-biomarker component membership is its principal structural rationale. The model's association is numerically stronger than Bao's reported unadjusted Pearson, but Bao excludes known diabetes, has a different population and measures plasma. MIND's serum rank correlation also comes from a much older selected cohort. No source replay or target reference permits claiming these differences are either corrected or erroneous CHNS behavior. The strength of the shared tail remains an explicit limitation.

E1 ranges 0.01480-0.02799 percent/(kg/m^2), E2 0.48012-0.50127 percent/(mmol/L), and E3 0.00438-0.00562 percent/year. E1 demonstrates appreciable finite-draw variation. E2 and E3 are projections of the full nonlinear joint model, not installed source coefficients. The Jansen separate models and Pani weighted age projection retain their own adjustment, population, specimen and uncertainty contexts. I do not tune an unweighted task projection to them, or select a seed that resembles them.

The choice is retention because no execution defect, unit error, new source extraction or target-reference finding identifies a supported scientific correction. This is a justified no-op, not a claim that the model is validated. More optional trials would only provide additional conditional draws and are not requested. Final delivery should use seeds 4101, 4102 and 4103; with identical scientific artifacts these runs should reproduce the initial rows. Such repetition is an integrity check, not new independent clinical evidence.

The finite-moment/positive-support argument, explicit conditional independence assumptions and source provenance remain in the model specification and retained producer artifacts. Source-only is the legacy checks scope for declared input evidence. Source reconstruction remains not_computable; national representativeness, CHNS transport, tail adequacy, treatment and household/geographic dependence, survey weighting, causal use and calibrated structural uncertainty remain unassessed. Retrieval totals are unchanged: zero queries and zero new original documents. FINAL_AUTHOR_DECISION.json records the same decision with the required fields.
'''
(dest/"decision.md").write_text(decision,encoding="utf-8")
shutil.copyfile(Path(__file__),dest/"producer_prepare_final_delivery.py")
print(str(dest))
