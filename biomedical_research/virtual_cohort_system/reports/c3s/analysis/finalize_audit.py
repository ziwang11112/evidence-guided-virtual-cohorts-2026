"""Append reviewed interpretation and figure QA to a completed aggregate audit."""
from pathlib import Path
import hashlib, json
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "audit_v1"
ROOT = HERE.parent
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding="utf-8"))
def write(path, value): Path(path).write_text(json.dumps(value, indent=2, allow_nan=False)+"\n", encoding="utf-8")

checks = pd.read_csv(OUT / "all20_checks.csv")
losses = pd.read_csv(OUT / "baseline_selected_loss.csv")
usage = pd.read_csv(OUT / "execution_usage.csv")
changes = pd.read_csv(OUT / "raw_changes.csv")
parameters = pd.read_csv(OUT / "all_trials_parameters.csv")
qa = read(OUT / "QA.json")
additional = []
def verify(name, passed):
    additional.append({"check":name, "passed":bool(passed), "detail":"postrun aggregate QA"})
    if not passed: raise ValueError(name)

panel_paths = [ROOT / name / "SOURCE_PANEL_SPEC.json" for name in ("inputs","linear","alternative")]
verify("all_source_panel_copies_identical",len({sha(p) for p in panel_paths})==1)
unrelated = changes[(changes.context=="lifelines") & (~changes.check_id.str.contains("hba1c|slope"))]
verify("all42_paired_marginal_diagnostics_exact",len(unrelated)==42 and bool((unrelated.raw_change==0).all()))
baseline = losses[(losses.structure=="alternative") & (losses.state=="baseline") & (losses.seed!=19101)]
verify("alternative_baseline_all20_pass_both_unused",len(baseline)==2 and bool(baseline.all20_pass.all()))
verify("all240_checks_reproduced",len(checks)==240 and bool(checks.calculation_reproduced.all()))
verify("all74_trials_no_parameter_bound_hits",len(parameters)==370 and not bool((parameters.at_lower|parameters.at_upper).any()))
verify("retained_output_log_sizes_below_caps",bool((usage.output_bytes<usage.output_cap_bytes).all()) and bool((usage.max_log_bytes<usage.log_cap_bytes).all()))
qa["checks"].extend(additional)
qa["check_count"] = len(qa["checks"])
qa["failed_checks"] = [x for x in qa["checks"] if not x["passed"]]
qa["status"] = "PASS" if not qa["failed_checks"] else "AUDIT_DISCREPANCIES_RETAINED"
qa["max_absolute_statistic_reproduction_error"] = float(checks.independent_minus_recorded.abs().max())
qa["visual_review"] = {
    "status":"PASS",
    "method":"Both PNG figures inspected directly at readable resolution after rendering.",
    "files":["loss_and_trajectory.png","all_twenty_checks.png"],
    "findings":"Labels, axes, legends, all20 rows, both structures, baseline/selected and three seeds readable; no clipping observed.",
    "pdf_method":"PDF files exported from the same inspected Matplotlib figures; no separate PDF raster review."
}
write(OUT/"QA.json",qa)
resource = []
for s, group in usage.groupby("structure"):
    resource.append({"structure":s,"actual_executions":len(group),"maximum_execution_elapsed_seconds":float(group.elapsed_seconds.max()),
        "maximum_output_bytes":int(group.output_bytes.max()),"total_output_bytes":int(group.output_bytes.sum()),
        "maximum_saved_log_bytes":int(group.max_log_bytes.max()),"execution_failures":int((group.status!="success").sum()),
        "trial_cap_hit":False,"execution_reservation_filled":False,"parameter_bound_hits":0,
        "observed_timeout_output_log_cap_hits":0,"recorded_memory_limit_failures":0,"peak_memory_measured":False,
        "monetary_cost_measured":False})
write(OUT/"RESOURCE_SUMMARY.json",resource)
report = OUT/"REPORT.md"
text = report.read_text(encoding="utf-8")
text = text.replace("**PASS**, 26729 checks.","**PASS**, "+str(qa["check_count"])+" checks.")
text += """

## Final interpretation and closure

The unchanged alternative baseline passed all 20 declared numeric checks on both unused seeds. Its fitted selection lowered fitting-seed loss, increased loss on each unused seed, and introduced a Pani age-slope failure on both. Thus, optimizing this objective lost a declared compatibility property that the baseline already had. The baseline remains retained; this observation does not authorize post-replay reselection.

The linear age-slope value 0.00799097657 on seed 19123 is a small literal miss below the authored lower bound 0.008. It is still a positive association. Its failure is an engineering-threshold result, not a biological reversal or a demonstrated clinically meaningful difference.

The alternative has lower selected loss and smaller worst Pani age-mean error than the selected linear structure on both unused seeds, but introduces a new age-slope failure relative to linear on 19111. The complete descriptive preference rule therefore fails. Numerical stability, source compatibility and structural comparison remain separate conclusions.

This bounded unit is closed with both structures, all baseline and selected results, and every criterion failure retained. No additional fit, model rewrite, evidence request or target step is executed or authorized by this audit.

Resource review: neither 40-trial nor 88-execution cap was reached; all 74 trials and 164 executions succeeded, with no parameter-bound hit across the 370 trial-parameter values. The largest recorded execution elapsed time was 2.672 s, largest generated output was 459,809 bytes, and saved stdout/stderr logs were empty. No timeout, output/log-cap or memory-limit failure was recorded. Peak memory and monetary cost were not measured. Per-structure maxima and totals are in RESOURCE_SUMMARY.json.

Final QA: the maximum absolute statistic reproduction discrepancy was 1.7763568394002505e-15. All 42 paired unrelated marginal diagnostic values were exactly unchanged, in addition to exact row-ID/covariate equality. Both PNG figures were visually inspected with readable labels and no clipping; the PDF versions come from the same Matplotlib figures. The three source-panel files are byte-identical.
"""
report.write_text(text,encoding="utf-8")
manifest = read(OUT/"INPUT_HASH_MANIFEST.json")
for p in [Path(__file__),*panel_paths]:
    manifest["inputs"][str(p.resolve())]={"sha256":sha(p),"bytes":p.stat().st_size}
manifest["input_count"]=len(manifest["inputs"])
manifest["finalization_script_sha256"]=sha(__file__)
write(OUT/"INPUT_HASH_MANIFEST.json",manifest)
write(OUT/"OUTPUT_HASH_MANIFEST.json",{"files":{p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!="OUTPUT_HASH_MANIFEST.json"}})
print(json.dumps({"qa":qa["status"],"checks":qa["check_count"],"report_sha256":sha(report),"output_manifest_sha256":sha(OUT/"OUTPUT_HASH_MANIFEST.json")}))
