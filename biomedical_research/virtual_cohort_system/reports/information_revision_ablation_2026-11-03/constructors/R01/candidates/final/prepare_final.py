"""Final feedback review and deterministic moment calculations; zero rows."""
from pathlib import Path
import hashlib
import json
import math
import shutil
import statistics

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/"mixref_initial"
ROOT=HERE.parent.parent.parent
FEEDBACK=ROOT/"session/feedback/initial.json"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path,obj): path.write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+"\n",encoding="utf-8")

for source in PARENT.iterdir():
    if source.is_file() and source.name!="freeze.json":
        shutil.copyfile(source,HERE/source.name)
shutil.copyfile(FEEDBACK,HERE/"feedback_initial.json")
feedback=json.loads(FEEDBACK.read_text(encoding="utf-8"))
runs=feedback["runs"]
assert len(runs)==3 and [r["seed"] for r in runs]==[4101,4102,4103]
per_run=[]
values={}
for run in runs:
    sem=run["semantic_feedback_v1"]
    af=run["analysis_feedback"]
    assert run["status"]=="success" and sem["output_link_verified"] and sem["generator_execution_recorded"]
    assert sem["n_computable"]==30 and sem["n_not_computable"]==1 and af["n"]==3000
    sm={x["id"]:x for x in sem["checks"]}
    rows=af["analyses"]+af["diagnostics"]
    assert len(rows)==30
    for row in rows:
        check=sm[row["id"]]
        assert check["status"]=="computed" and check["semantic_status"]=="matched_declared"
        assert check["calculation"]["value"]==row["value"]
        assert check["calculation"]["n_used"]==3000 and check["calculation"]["n_missing_dropped"]==0
        values.setdefault(row["id"],[]).append(row)
    assert sm["external_context_unreplayed"]["status"]=="not_computable"
    per_run.append({"seed":run["seed"],"run_id":run["run_id"],"status":run["status"],
                    "execution_sha256":run["execution_sha256"],"output_sha256":run["generated_table_sha256"],
                    "quality":af["quality"],"statistics":rows,
                    "semantic_statuses":{key:{"status":v["status"],"semantic_status":v["semantic_status"]} for key,v in sm.items()},
                    "scientific_validity":sem["scientific_validity"],"semantic_limitations":sem["limitations"]})

summary=[]
for key,rows in values.items():
    v=[row["value"] for row in rows]
    summary.append({"id":key,"reference":rows[0]["reference"],"values_by_seed":v,
                    "differences_by_seed":[row["difference"] for row in rows],
                    "mean_over_three_fixed_draws":statistics.mean(v),
                    "descriptive_sd_over_three_fixed_draws":statistics.stdev(v),
                    "range":[min(v),max(v)]})
spec=json.loads((HERE/"model_spec.json").read_text(encoding="utf-8"))["parameters"]
fit=json.loads((HERE/"fit_report.json").read_text(encoding="utf-8"))
g,h=spec["glucose_mixture"],spec["hba1c_mixture"]
probs=spec["mixture_indicator_probabilities"]
def raw_gh(a,b):
    result=0.0
    for component,prob in enumerate(probs):
        i,j=divmod(component,2)
        rho=spec["component_latent_correlations"][component][3][4]
        mu_g,sg=g["log_means"][i],g["log_sds"][i]
        mu_h,sh=h["log_means"][j],h["log_sds"][j]
        result+=prob*math.exp(a*mu_g+b*mu_h+0.5*(a*a*sg*sg+b*b*sh*sh+2*a*b*rho*sg*sh))
    return result
mg,mh=raw_gh(1,0),raw_gh(0,1)
def central_gh(a,b):
    return sum(math.comb(a,k)*math.comb(b,l)*(-mg)**(a-k)*(-mh)**(b-l)*raw_gh(k,l)
               for k in range(a+1) for l in range(b+1))
vg,vh=central_gh(2,0),central_gh(0,2)
rho=central_gh(1,1)/math.sqrt(vg*vh)
mu22=central_gh(2,2)
pearson_if_variance=(mu22/(vg*vh)+rho*rho/4*(central_gh(4,0)/(vg*vg)+2*mu22/(vg*vh)+central_gh(0,4)/(vh*vh))
                      -rho*(central_gh(3,1)/(vg**1.5*vh**.5)+central_gh(1,3)/(vg**.5*vh**1.5)))
pearson_se=math.sqrt(pearson_if_variance/3000)
sd_se={"glucose":math.sqrt((central_gh(4,0)-vg*vg)/(4*vg*3000)),
       "hba1c":math.sqrt((central_gh(0,4)-vh*vh)/(4*vh*3000))}
moment_context={
    "method":"Closed-form raw moments of the fitted four-component bivariate lognormal mixture, central-moment binomial expansion, delta-method sample-SD and Pearson influence-function variances; no sampling, no generator import.",
    "n":3000,"population_pearson":rho,
    "asymptotic_pearson_mc_se_conditional_on_model":pearson_se,
    "pearson_difference_in_asymptotic_model_se_units":[r["difference"]/pearson_se for r in values["glucose_hba1c_pearson"]],
    "asymptotic_glucose_sd_mc_se_conditional_on_model":sd_se["glucose"],
    "asymptotic_hba1c_sd_mc_se_conditional_on_model":sd_se["hba1c"],
    "glucose_sd_difference_in_asymptotic_model_se_units":[r["difference"]/sd_se["glucose"] for r in values["glucose_sd"]],
    "hba1c_sd_difference_in_asymptotic_model_se_units":[r["difference"]/sd_se["hba1c"] for r in values["hba1c_sd"]],
    "limits":"First-order large-n conditional-model sampling scales, not exact finite-sample bounds, source uncertainty, validated clinical tolerances or hypothesis tests. Three fixed draws do not estimate structural uncertainty. Regression/Spearman MC uncertainty remains unestimated."}

decision={
    "reason":"Retain mixref_initial scientifically unchanged as mixref_final. All three fixed initial deliveries succeeded and all 30 statistics per draw were reviewed. Analytically fitted biomarker margins, Pearson/Spearman association and OLS projections already target the admitted development sample estimates. Initial glycemic discrepancies change direction across seeds; finite-draw variation and tail sensitivity are more plausible than a stable offset to correct. Known BMI-quantile approximation and underidentified dependence assumptions remain explicit. Extra trials would not identify those missing relationships, and no seed-specific calibration or favorable-seed choice is justified.",
    "kind":"retain",
    "addressed_findings":[
        "Verified all three executions and output links, all 90 statistic calculations and matched declared semantics, with zero nonpositive glycemia and duplicate measurement rows in each draw.",
        "Separated small analytic BMI quantile mismatch from Monte Carlo variation; three BMI medians sit slightly above the reference, as the retained one-lognormal model predicts.",
        "Examined regression coefficients and both glycemic correlations across every seed, preserving source-adjustment distinctions and refusing to treat reported reference confidence intervals as pass/fail or tuning targets.",
        "Computed closed-form fourth-moment sampling scales for glucose/HbA1c SD and Pearson correlation to contextualize tail-sensitive variation. Calculations produce no synthetic rows and do not establish the model's scientific correctness.",
        "Bound full initial delivery feedback and the prior actual trial feedback. Declined optional final-phase trials4301/4302 and preserved generator/spec/evidence bytes for required final delivery at all three fixed seeds."
    ],
    "remaining_limitations":[
        "Supplied CHNS summaries are selected-sample development estimates, not independent validation, population truth or national representation.",
        "Component tail shapes and the assumed broad-component correlation, mixture-indicator independence from age/sex/BMI, nuisance covariate correlations and within-bin age shape remain underidentified.",
        "BMI lognormal quantiles are approximate; no parameter-uncertainty or evidence-selection model is represented.",
        "IID rows do not reproduce community clustering, survey weights, treatments, disease states, missingness or measurement rounding. Causal, prediction and subgroup uses remain unassessed.",
        "External studies retain their own populations, selection, plasma/serum measures and adjustment/weighting. No source-context replay was provided; it remains not_computable.",
        "Reusing identical generators and final seeds will reproduce the initial outputs; this retention is not a claimed numerical improvement or an additional validation sample."
    ]
}
report={"kind":"final_scientific_retention_review","candidate":"mixref_final","parent":"mixref_initial",
        "requested_stage":"final_delivery_4101_4102_4103","decision":decision,
        "initial_feedback_sha256":sha(FEEDBACK),"reference_role":feedback["reference_role"],
        "uncertainty_policy":feedback["uncertainty_policy"],"per_run":per_run,
        "all_30_statistics_across_three_draws":summary,"analytic_sampling_scale_context":moment_context,
        "unchanged_scientific_files":{name:{"sha256":sha(HERE/name),"identical_to_parent":(HERE/name).read_bytes()==(PARENT/name).read_bytes()} for name in ["generator.py","model_spec.json","evidence.json"]},
        "new_literature_queries":[],"new_documents":[],"local_generated_rows":0}
dump(HERE/"final_review.json",report)
dump(ROOT/"FINAL_AUTHOR_DECISION.json",decision)
shutil.copyfile(ROOT/"FINAL_AUTHOR_DECISION.json",HERE/"final_author_decision.json")
checks=json.loads((HERE/"checks.json").read_text(encoding="utf-8"))
checks["records"].append({"name":"initial_delivery_feedback_review","status":"pass","detail":"Complete actual initial aggregate feedback bound; all 30 statistics for each of the three fixed seeds verified against semantic calculations. Retain scientific files byte-for-byte; review differentiates analytic BMI approximation and finite-draw effects. No scientific validation is claimed."})
checks["records"].append({"name":"analytic_tail_sampling_scale","status":"pass","detail":"Computed closed-form fourth moments, delta-method SD scales and Pearson influence-function scale from the fitted model. This is deterministic conditional-model mathematics, not extra rows, a formal finite-sample bound, or population validation. Full formulas are retained in prepare_final.py."})
for name in ["feedback_initial.json","final_review.json","final_author_decision.json"]:
    checks["artifacts"].append({"path":name,"sha256":sha(HERE/name)})
dump(HERE/"checks.json",checks)
text=(HERE/"decision.md").read_text(encoding="utf-8")
text=text.replace("# Initial delivery candidate: mixref_initial","# Final retained candidate: mixref_final")
text=text.replace("Requested next stage: fixed initial delivery at seeds 4101, 4102, 4103.","Requested next stage: fixed final delivery at seeds 4101, 4102, 4103.")
text+="\n\nFinal author decision after all initial deliveries: retain. All three executions succeeded and each yielded all 30 allowed statistics. Full feedback is bound in feedback_initial.json, with per-statistic values, differences and descriptive across-seed summaries in final_review.json. No scientific parameter, generator code or evidence record changes. The final fixed seeds will reproduce the initial draws; no improvement or new independent evidence is claimed.\n\n"
text+="The known BMI lognormal median/quantile approximation remains distinct from finite-draw variation. Glycemic correlations and regression differences vary in direction across seeds; no stable error has been demonstrated. Deterministic fourth-moment calculations quantify approximate conditional-model sampling scales for tail-sensitive SD and Pearson summaries, with their limitations recorded. These calculations do not change the model, pool source uncertainty, or supply exact Monte Carlo confidence bounds. Optional trials4301/4302 are declined because more draws would not resolve underidentified structure. Root/FINAL_AUTHOR_DECISION.json records the reason, addressed findings and remaining limitations.\n"
(HERE/"decision.md").write_text(text,encoding="utf-8")
print(json.dumps({"candidate":"mixref_final","request":"final_delivery_4101_4102_4103","kind":"retain","statistics_reviewed":90,
                  "scientific_files_unchanged":report["unchanged_scientific_files"],"analytic_sampling_scale_context":moment_context,
                  "regression_and_association_summary":[r for r in summary if r["id"] in ["E1","E2","E3","glucose_hba1c_pearson","glucose_hba1c_spearman"]],"local_generated_rows":0},indent=2))
