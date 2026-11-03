"""Retain scientific bytes after all permitted initial feedback; never execute rows."""
from pathlib import Path
import hashlib
import json
import shutil
import statistics

ROOT = Path(r"D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcIA/L01")
OLD = ROOT / "b/candidates/latent_glycemia_initial"
NEW = ROOT / "b/candidates/latent_glycemia_final"
FEEDBACK = ROOT / "session/feedback/initial.json"
NEW.mkdir(parents=True, exist_ok=False)
shutil.copytree(OLD / "auxiliary", NEW / "auxiliary")
for filename in ["generator.py", "model_spec.json", "evidence.json"]:
    shutil.copy2(OLD / filename, NEW / filename)
shutil.copy2(FEEDBACK, NEW / "auxiliary/initial_feedback.json")

def write_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")

feedback = json.loads(FEEDBACK.read_text(encoding="utf-8"))
run_maps = []
for run in feedback["runs"]:
    items = run["analysis_feedback"]["diagnostics"] + run["analysis_feedback"]["analyses"]
    assert len(items) == 30
    assert all(x["status"] == "computed" for x in items)
    run_maps.append({x["id"]: x["value"] for x in items})
summary = {}
for key in run_maps[0]:
    values = [mapping[key] for mapping in run_maps]
    summary[key] = {"values_in_seed_order_4101_4102_4103": values, "mean": statistics.mean(values), "minimum": min(values), "maximum": max(values)}
identity = {name: {"sha256": hashlib.sha256((NEW / name).read_bytes()).hexdigest(), "identical_to_initial": (NEW / name).read_bytes() == (OLD / name).read_bytes()} for name in ["generator.py", "model_spec.json", "evidence.json"]}
review = {
    "kind": "retain",
    "requested_stage": "final_delivery_4101_4102_4103",
    "parent_candidate": "latent_glycemia_initial",
    "feedback_file": "auxiliary/initial_feedback.json",
    "feedback_reference_role": feedback["reference_role"],
    "runs_reviewed": [{"run_id": r["run_id"], "seed": r["seed"], "status": r["status"], "n": r["analysis_feedback"]["n"], "quality": r["analysis_feedback"]["quality"], "output_link_verified": r["semantic_feedback_v1"]["output_link_verified"]} for r in feedback["runs"]],
    "statistic_count_per_run": 30,
    "statistic_observations_reviewed": 90,
    "all_30_statistics": summary,
    "aggregation_limit": "Arithmetic summary of already supplied statistics only. Minima and maxima are observed three-seed ranges, not confidence intervals, target-reference uncertainty, independent clinical evidence or source replay. No participant rows were read or generated.",
    "scientific_file_identity": identity,
    "observations": [
        "All three fixed-seed 3000-row initial deliveries succeeded with verified output linkage, zero nonpositive glycemia, zero duplicate measurement rows, 27 computed diagnostics and three full-rank projections per run.",
        "All five marginal mean/SD/quantile groups have been inspected, including binary female quantiles. The summaries show the intended broad demographic support, positive BMI, and right-tailed glycemia. They cannot establish target composition or assay equivalence.",
        "Pearson ranges 0.61426-0.64402 while Spearman ranges 0.52359-0.53963. Different functions of the assumed mixed joint distribution remain distinct; proximity to Bao/MIND source points supplies no matched-population validation.",
        "E1 ranges 0.00944272-0.0185832 percentage points per BMI unit; E2 0.325895-0.375820 percentage points per mmol/L; E3 0.00652575-0.00717569 percentage points per year. These ranges show conditional seed variability, especially for E1, not model-parameter uncertainty.",
        "The positive age effect was initially chosen using restored source age evidence with explicit transport/adjustment caveats. No discrepancy with a target reference can be assessed. Source projections are not equated to these task projections, and observed E3 is not retuned toward a source point.",
        "No numerical failure or scientifically identified structural contradiction warrants replacing the declared scenario. Further optional synthetic trials would not identify the underdetermined target law. Retention is therefore justified without using trials4301/4302.",
    ],
    "science_changed": False,
    "new_retrieval_queries": [],
    "new_original_documents": [],
    "local_row_execution": False,
}
write_json(NEW / "auxiliary/initial_feedback_review.json", review)
decision = {
    "reason": "Retain the complete positive-support latent-glycemia scenario after reviewing all 30 statistics on each of the three fixed initial-delivery seeds and the earlier trial4201. All isolated runs succeeded and the diagnostics disclose expected mixture behavior and conditional seed variation without an identified implementation defect. No target reference is supplied and external source replay is unavailable; adjusting the scenario to a chosen source point or favorable realization would not be justified. Generator, model specification and evidence are byte-identical in latent_glycemia_final. No post-initial numerical trials are requested; final delivery uses all fixed seeds 4101, 4102 and 4103.",
    "kind": "retain",
    "addressed_findings": [
        "Inspected 90 initial diagnostic/projection values (30 per seed), all computed, with full-rank E1/E2/E3 and reported successful 3000-row output linkage.",
        "Retained positive-support construction after zero nonpositive glycemia and zero duplicate measurement rows in all initial runs; deterministic all-moments argument remains documented.",
        "Recorded all marginal summaries and distinct Pearson/Spearman functions without recasting them as source replay or target calibration.",
        "Recorded E1/E2/E3 seed variation, including the comparatively variable BMI projection; no p-value or coefficient target was tuned and no favorable seed selected.",
        "Preserved restored age evidence, actual adjustment sets, source population/specimen differences, overlap and explicitly assumed transport. Bound the exact initial feedback and completed retention review in the new final candidate.",
    ],
    "remaining_limitations": [
        "No target-reference summaries or patient data were supplied; target population validity and predictive, causal or clinical applicability remain unassessed.",
        "Source-context numerical replay is not computable. Different selections, assay handling, plasma/serum specimens and original weighting/adjustments prevent interpreting generated task diagnostics as a source reconstruction.",
        "Age/sex composition, BMI relationships, glycemic subgroup probability/severities, conditional dependencies and tail laws remain explicit underidentified assumptions.",
        "Three generated draws characterize only conditional simulation variability. They do not quantify source-estimator, structural, transport or measurement uncertainty, and observed seed ranges are not confidence intervals.",
        "Treatment, diabetes status, erythrocyte biology, pregnancy and other unmeasured mechanisms are not represented as measured variables; their effects are not recovered.",
        "Final delivery repeats identical science on the same mandated seeds, so matching outputs are expected by construction and provide no new independent scientific evidence or improvement claim.",
    ],
}
write_json(ROOT / "FINAL_AUTHOR_DECISION.json", decision)
write_json(NEW / "auxiliary/final_author_decision.json", decision)
(NEW / "auxiliary/prepare_final_delivery.py").write_text(Path(__file__).read_text(encoding="utf-8"), encoding="utf-8")

checks = json.loads((OLD / "checks.json").read_text(encoding="utf-8-sig"))
for record in checks["records"]:
    if record["name"] == "generated_output_validation":
        record["detail"] = "Historical actual coordinator feedback is bound for trial4201 and all initial seeds4101/4102/4103: successful isolated 3000-row generation, output linkage verified, zero nonpositive glycemia/duplicate measurement rows, and all 30 statistics computed. Current final candidate has byte-identical scientific files but is not yet executed. No local row computation or independent re-execution was performed."
checks["records"].append({"name": "final_retention_after_initial_feedback", "status": "pass", "detail": "Completed review of all 90 supplied initial-statistic values and byte-for-byte scientific-file identity; exact initial feedback, complete deterministic aggregation, decision and producer bound. Pass denotes documented review and identity, not scientific validity or target agreement."})
checks["records"].append({"name": "transport_and_structural_uncertainty", "status": "not_computable", "detail": "No target reference or probability model over transport/structure is supplied. Three seeds and repeated final seeds do not estimate these uncertainties; no recalibration or superiority claim is made."})
for filename in ["auxiliary/initial_feedback.json", "auxiliary/initial_feedback_review.json", "auxiliary/final_author_decision.json", "auxiliary/prepare_final_delivery.py"]:
    checks["artifacts"].append({"path": filename, "sha256": hashlib.sha256((NEW / filename).read_bytes()).hexdigest()})
write_json(NEW / "checks.json", checks)

old_text = (OLD / "decision.md").read_text(encoding="utf-8")
rationale = old_text.split("Scientific rationale retained from the initial construction follows.", 1)[1]
rationale = rationale.split("Requested next step:", 1)[0]
final_text = """# Final author decision: retain

Submit `latent_glycemia_final` for final delivery on fixed seeds 4101, 4102 and 4103. Generator, specification and evidence are byte-identical to the immutable initial-delivery candidate. Only the decision/check documentation and bound feedback have changed. No post-initial trial or additional literature retrieval is requested.

I reviewed all 30 statistics for every initial run (90 values), their quality summaries, and the earlier trial4201. All three initial 3000-row deliveries succeeded with verified output linkage and full-rank E1/E2/E3; none had nonpositive glycemia or duplicate measurement rows. The five marginal distributions display the intended demographic breadth and positive glycemic tails. The exact feedback and all-statistic review are bound.

E1 varied from 0.00944 to 0.01858, E2 from 0.32589 to 0.37582, and E3 from 0.00653 to 0.00718 in their declared task units. Pearson varied from 0.61426 to 0.64402 and Spearman from 0.52359 to 0.53963. These are seed ranges under fixed assumptions, not confidence intervals or source/target uncertainty. The BMI projection is relatively variable; I do not tune it to a source point or pick a favorable realization. The age projection retains the explicit source-informed assumption, without equating source adjustment sets to the task's estimand.

No target-reference values were supplied and source-context replay is unavailable. The observed behavior reveals no identified implementation error or structural contradiction requiring revision. Additional synthetic draws would not resolve the missing target law, so retaining this transparent scenario is preferable to an unsupported recalibration. This choice claims neither target recovery nor improvement. Repeating the same scientific files on the mandated final seeds is expected to repeat outputs and adds no independent clinical evidence.

Scientific rationale retained from initial construction follows.
""" + rationale
final_text += "\nRemaining limits are source transport, assay equivalence, latent treatment/disease/hematology, subgroup and tail dependence, and uncalibrated structural uncertainty. Final use remains inspection of an assumption-dependent synthetic scenario. The complete four-key author decision is at the assigned root's FINAL_AUTHOR_DECISION.json and bound inside this candidate. All new text is UTF-8; no rows were read or generated locally.\n"
(NEW / "decision.md").write_text(final_text, encoding="utf-8")
print(json.dumps({"candidate": str(NEW), "requested_stage": "final_delivery_4101_4102_4103", "kind": "retain", "statistics_reviewed": 90, "scientific_identity": identity}, ensure_ascii=False))
