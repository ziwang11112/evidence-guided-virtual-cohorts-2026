"""Descriptive summary of every prespecified final output, no best-seed filter."""
import csv,json,statistics
from pathlib import Path
U=Path(__file__).resolve().parent.parent
KEYS=["bmi_sbp","bmi_dbp","residual_correlation"]
def f(v):return "not estimable" if v is None else f"{v:.3f}"
def main():
    r=json.loads((U/"RESULTS.json").read_text(encoding="utf-8"))
    lines=["# PNS blood-pressure joint-generation validation","",
           "New prespecified analysis task in an exposed PNS release; no new-cohort or national-population claim.","",
           f"Reference eligible N={r['eligibility']['common_eligible_rows']}; final tables={r['selected_output_count']}; all attempted stage/seed tables={r['all_attempted_output_count']}.","",
           "## Real reference (not known population truth)","",
           "| Analysis | Weighted point | Conditional row-resampling interval | Unweighted sensitivity |",
           "|---|---:|---:|---:|"]
    for k in KEYS:
        s=r["reference_row_resampling_stability"]["intervals"][k]
        lines.append(f"| {k} | {f(r['reference_weighted']['estimates'][k])} | [{f(s['low'])}, {f(s['high'])}] | {f(r['reference_unweighted_sensitivity']['estimates'][k])} |")
    lines += ["","The intervals resample rows while retaining their supplied weights; they are not survey-design confidence intervals. BMI slopes are mmHg per5kg/m² adjusted for age and recorded sex; residual correlation is dimensionless.","",
              "## All authors and selected draws","","| Author | Native disposition | Selected stage | Tables | BMI–SBP median [range] | BMI–DBP median [range] | Residual correlation median [range] |","|---|---|---|---:|---|---|---|"]
    for a in r["author_outcomes"]:
        vals=[]
        for k in KEYS:
            v=[x["analysis"]["estimates"][k] for x in r["generated"] if x["author_id"]==a["author_id"] and x["analysis"]["estimates"][k] is not None]
            vals.append(f"{f(statistics.median(v))} [{f(min(v))}, {f(max(v))}]" if v else "not estimable")
        lines.append(f"| {a['author_id']} | {a['status']} | {a['final_candidate']} | {a['selected_output_count']} | "+" | ".join(vals)+" |")
    lines += ["","Three draws share one authored law; five authors share one real reference. Neither rows, seeds nor authors count as independent clinical cohorts.","",
              "## Interpretation boundary","",
              "Compare effect magnitude and joint dependence together with dispersion, not sign alone or exact numerical matching. All failures, singular outputs and unselected stages remain in the sealed records. The experiment does not define an arbitrary pass threshold or establish superiority/equivalence. A source-feedback revision, if selected, is not automatically a proven improvement against independent clinical data.","",
              "Known unresolved assumptions include target demographics and BMI dependence, omitted source adjustment covariates, age/measurement/selection transport, and raw versus conditional dependence. No post-reveal regeneration is permitted.","",
              "Figures: `figures/pns_bp_analysis_utility.pdf` and `figures/pns_bp_dispersion.pdf`. Full numerical output: `RESULTS.json`; independent recomputation is reported separately."]
    (U/"RESULTS.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    rows=[]
    for x in r["comparisons"]:
        for k,y in x["estimates"].items():
            rows.append({"author":x["author_id"],"candidate":x["candidate"],"seed":x["seed"],"analysis":k,"status":x["status"],**y})
    if rows:
        with (U/"ANALYSIS_COMPARISONS.csv").open("w",encoding="utf-8",newline="") as out:
            writer=csv.DictWriter(out,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print(str(U/"RESULTS.md"))
if __name__=="__main__":main()
