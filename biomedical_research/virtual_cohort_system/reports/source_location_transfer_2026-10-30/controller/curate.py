"""Allowlisted M11 review export; participant tables and source papers excluded."""
from pathlib import Path
import hashlib,json,shutil

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[1]
DEST=PROJECT/"reports/source_location_transfer_2026-10-30"

def copy(src,rel):
    dst=DEST/rel;dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(src,dst)

def main():
    DEST.mkdir(exist_ok=False)
    for name in ["protocol.json","campaign.py","prepare_bundles.py","audit_calibration.py","source_calibration_audit.json","launch.json","release.json","source_admission.json","summarize.py","curate.py"]:
        copy(HERE/name,"controller/"+name)
    for p in (HERE/"evaluator").iterdir():
        if p.is_file() and p.suffix in {".py",".md"}:copy(p,"evaluator/"+p.name)
    for p in (HERE/"results").iterdir():
        if p.is_file() and p.suffix in {".json",".csv",".png",".svg"}:copy(p,"results/"+p.name)
    for p in (HERE/"source_audit").iterdir():
        if p.is_file() and p.suffix in {".json",".py",".md"}:copy(p,"source_audit/"+p.name)
    for name in ["freshness_access_manifest.json","preparation_receipt.json"]:
        copy(HERE/"custodian"/name,"custodian/"+name)
    copy(HERE/"custodian/visible/task_safe_manifest.json","custodian/task_safe_manifest.json")
    for p in (HERE/"custodian").glob("*.py"):copy(p,"custodian/"+p.name)
    for p in (HERE/"custodian/reviews").iterdir():
        if p.is_file() and p.suffix in {".json",".py"}:copy(p,"audits/"+p.name)
    for family in ["ha","hb"]:
        bundle=HERE/family
        for name in ["task.json","registry.json","source_calibration_summary.json","source_controller_status.jsonl"]:
            copy(bundle/name,f"constructions/{family}/"+name)
        for candidate in (bundle/"candidates").iterdir():
            if not candidate.is_dir():continue
            for p in candidate.rglob("*"):
                if p.is_file() and "__pycache__" not in p.parts:
                    if p.suffix not in {".json",".py",".md",".csv"}:raise ValueError("Unexpected candidate artifact")
                    if p.suffix==".csv" and "source_contexts" not in p.parts:raise ValueError("Non-source candidate CSV forbidden")
                    copy(p,f"constructions/{family}/candidates/{candidate.name}/"+p.relative_to(candidate).as_posix())
        for p in (bundle/"revisions").glob("*.json"):copy(p,f"constructions/{family}/revisions/"+p.name)
        for run in (bundle/"executions").iterdir():
            copy(run/"execution.json",f"constructions/{family}/target_receipts/{run.name}.json")
        for run in (bundle/"source_replays").iterdir():
            copy(run/"replay.json",f"constructions/{family}/source_receipts/{run.name}.json")
    readme='''# M11 curated source-location transfer record

See [the full result report](../../MILESTONE_11_RESULTS.md). Source-median calibration improved fitted SHIP statistics but worsened the new NHANES HbA1c target's level/subgroup discrepancies. All versions are retained.

This is a review/reproduction record, not a standalone portable package. It contains code, protocol, frozen scientific candidate files, constructed source covariates, source/target execution receipts, aggregate results and independent audit code. Participant-level observed/reference/generated target tables, weights/ID mappings, raw XPTs and downloaded paper full texts are deliberately excluded. The CSVs under candidate `source_contexts/` are artificial source-population inputs generated from published summaries, not participants. Result CSVs contain aggregate estimates only.

Original receipts bind private local inputs and paths. Hashes can be inspected here, but full original receipt verification requires those exact local files. Do not claim successful portable reproduction from this export alone. Source URLs, source-artifact hashes and extraction locations are retained in `source_audit/source_evidence_packet.json`; fresh web downloads may differ in bytes. Original participant inputs remain in the workspace.

For an original-workspace reproduction, preserve `work/m11` and its layout, use `custodian` preparation scripts only under the documented data boundary, restore admitted source bytes, run source construction scripts through the documented harness, and use `controller/campaign.py` stages freeze/execute/seal/evaluate after assigning new output locations. Existing frozen artifacts are not overwrite targets. The campaign depends on the sibling `cohort_harness` and approved WSL runtime; exact environment and limits are in execution receipts. Source scientific choices are documented in `source_plan.json` and each candidate specification.

Checks: 18 invented-data tests; 12 independently recomputed source corrections; 36 successful isolated source executions; 24 successful target executions; independent arithmetic verification of all 24 target tables. Custodian/code review is not a fully outcome-blind external reproduction. Default Windows pytest-temp permission errors and a pre-parse custody self-test repair are retained in audit/preparation records.

`file_manifest.json` binds every exported file except itself. No model-performance superiority, clinical equivalence or calibrated uncertainty claim follows from this pilot.
'''
    (DEST/"README.md").write_text(readme,encoding="utf-8")
    files={p.relative_to(DEST).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(DEST.rglob("*")) if p.is_file()}
    (DEST/"file_manifest.json").write_text(json.dumps({"scope":"Allowlisted curated export; no participant tables","files":files},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"export":str(DEST),"files_bound":len(files),"bytes":sum(p.stat().st_size for p in DEST.rglob('*') if p.is_file())}))

if __name__=="__main__":main()
