"""Copy an immutable trial's science and bind actual feedback; no row execution."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(r"D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcIA/L01")
OLD = ROOT / "b/candidates/latent_glycemia_v1"
NEW = ROOT / "b/candidates/latent_glycemia_initial"
FEEDBACK = ROOT / "session/feedback/a01_initial_4201.json"
NEW.mkdir(parents=True, exist_ok=False)
shutil.copytree(OLD / "auxiliary", NEW / "auxiliary")
for filename in ["generator.py", "model_spec.json", "evidence.json"]:
    shutil.copy2(OLD / filename, NEW / filename)
shutil.copy2(FEEDBACK, NEW / "auxiliary/trial4201_feedback.json")

def write_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")

feedback = json.loads(FEEDBACK.read_text(encoding="utf-8"))
items = feedback["analysis_feedback"]["diagnostics"] + feedback["analysis_feedback"]["analyses"]
review = {
    "kind": "retain",
    "requested_stage": "initial_delivery_4101_4102_4103",
    "parent_candidate": "latent_glycemia_v1",
    "feedback_file": "auxiliary/trial4201_feedback.json",
    "reviewed_statistic_count": len(items),
    "all_statistics_computed": all(x["status"] == "computed" for x in items),
    "reviewed_statistics": {x["id"]: x["value"] for x in items},
    "observations": [
        "Coordinator reports successful isolated 3000-row execution and output linkage. Nonpositive glucose/HbA1c counts and duplicate-measurement-row count are zero.",
        "Age, female and BMI summaries display the intended broad adult composition and BMI spread; this is behavior inspection, not target-marginal validation.",
        "Glucose/HbA1c means exceed their medians, showing the intended positive upper tails. Finite sample SDs are 1.31461 mmol/L and 0.74673 percentage points. No source population replay is implied.",
        "Pearson 0.62492 and Spearman 0.53198 differ as expected for the mixed joint distribution; numerical proximity to differently selected Bao and MIND observations is not an independent source or target validation.",
        "E1=0.0173772, E2=0.348378 and E3=0.00742231 are the declared unweighted task projections, all full rank. Their values are not substituted for published differently adjusted coefficients or interpreted causally.",
        "One trial cannot estimate transport or structural uncertainty. No implementation error or contradictory model behavior is identified, and no target-specific reference was supplied to support recalibration.",
    ],
    "science_changed": False,
    "scientific_file_identity": {name: hashlib.sha256((NEW / name).read_bytes()).hexdigest() for name in ["generator.py", "model_spec.json", "evidence.json"]},
    "limits": "No second initial trial requested. No empirical target recovery, source replay, uncertainty calibration, p-value tuning or favorable-seed selection claimed. Delivery uses all three fixed seeds.",
}
write_json(NEW / "auxiliary/trial4201_review.json", review)
(NEW / "auxiliary/prepare_initial_delivery.py").write_text(Path(__file__).read_text(encoding="utf-8"), encoding="utf-8")

checks = json.loads((OLD / "checks.json").read_text(encoding="utf-8-sig"))
for record in checks["records"]:
    if record["name"] == "generated_output_validation":
        record["status"] = "pass"
        record["detail"] = "Bound coordinator feedback for immutable parent trial4201 records successful isolated generation of 3000 rows and output_link_verified=true, zero nonpositive glycemia, zero duplicate measurement rows, and all 30 statistics computed. This review does not independently re-execute rows. Current delivery candidate has identical generator/spec/evidence bytes but is not yet executed."
    if record["name"] == "contract_validation":
        record["detail"] = "Historical bound receipt: parent latent_glycemia_v1 passed static harness validation after an initial path-form CLI argument was rejected. Delivery candidate requires its own static validation; no row execution occurs."
checks["records"].append({"name": "initial_delivery_retention", "status": "pass", "detail": "All 30 trial statistics inspected; scientific files copied byte-for-byte and no trial4202 requested. Retention rationale and exact actual feedback are bound. This is a completed review/identity check, not a scientific-validity pass."})
for filename in ["auxiliary/trial4201_feedback.json", "auxiliary/trial4201_review.json", "auxiliary/prepare_initial_delivery.py"]:
    checks["artifacts"].append({"path": filename, "sha256": hashlib.sha256((NEW / filename).read_bytes()).hexdigest()})
write_json(NEW / "checks.json", checks)

original_decision = (OLD / "decision.md").read_text(encoding="utf-8")
decision = """# Initial delivery after trial4201

Retain the scientific construction unchanged and submit `latent_glycemia_initial` for the fixed initial delivery seeds 4101, 4102 and 4103. The immutable parent is `latent_glycemia_v1`; generator, model specification and evidence bytes are identical. The actual trial4201 feedback and a review of all 30 statistics are bound in checks artifacts.

The trial reports 3000 rows, zero nonpositive glycemia and duplicate measurement rows, and computed full-rank E1/E2/E3. Its positive upper tails and distinct Pearson/Spearman associations are consistent with the declared mixture's intended behavior. No target-reference summaries were supplied. Proximity to Bao/MIND point correlations is not source replay, and E1/E2/E3 are not population recovery or causal coefficients. I found no implementation or structural contradiction that warrants changing this scenario. I do not request trial4202; more synthetic draws would not resolve the missing source-to-target evidence.

Scientific rationale retained from the initial construction follows.

"""
body = original_decision.split("Age is a broad bounded discrete distribution.", 1)[1]
body = "Age is a broad bounded discrete distribution." + body
body = body.split("Requested next step:", 1)[0]
decision += body
decision += "\nRequested next step: coordinator attaches fixed semantics, validates and freezes this new candidate, then executes all three fixed initial delivery seeds. Source replay, target-population validity, causal effects, assay equivalence, treatment/hematological mechanisms and structural uncertainty remain unassessed. No new retrieval or local row simulation occurred.\n"
(NEW / "decision.md").write_text(decision, encoding="utf-8")
print(json.dumps({"candidate": str(NEW), "stage": review["requested_stage"], "reviewed_statistics": len(items), "science_changed": False}))
