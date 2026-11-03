"""Small rich-summary comparator controller; no patient source access."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, shutil, sys, time
from datetime import datetime, timezone
U=Path(__file__).resolve().parent
P=U.parents[1]
W=P.parents[1]
OLD=W/"evcIA"/"R01"/"b"
B=U/"bundle"
sys.path.insert(0,str(P))
from cohort_harness.lifecycle import freeze_candidate, read_table
from cohort_harness.execution import run_candidate, verify_execution
from cohort_harness.contracts import validate_evidence, validate_task

def load(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("x",encoding="utf-8",newline="\n") as f:
        json.dump(x,f,indent=2,ensure_ascii=False,allow_nan=False); f.write("\n")
def module(path,name):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s)
    sys.modules[name]=m; s.loader.exec_module(m); return m

def prepare():
    if B.exists(): raise ValueError("bundle already exists; preserve previous artifacts")
    B.mkdir()
    task=load(OLD/"task.json")
    task["task_id"]="CHNS-summary-statistical-comparator-2026-11-03"
    task["budget"]={"source_queries":0,"source_downloads":0,"revisions":0}
    task["information_policy"]["allowed_tools"]=["admitted_source_read","declared_summary_fitting","isolated_final_generation"]
    write(B/"task.json",task)
    registry=load(OLD/"registry.json")
    for item in registry["artifacts"]:
        destination=B/item["path"]; destination.parent.mkdir(parents=True,exist_ok=True)
        if not destination.exists(): shutil.copyfile(OLD/item["path"],destination)
        if sha(destination)!=item["sha256"]: raise ValueError("source snapshot mismatch")
    (B/"input").mkdir()
    for name in ("compiled_evidence.json","reference_summary.json","analysis_definitions.json"):
        shutil.copyfile(OLD/"input"/name,B/"input"/name)
    reference=B/"input"/"reference_summary.json"
    if sha(reference)!="7cda7cb9a3a1b337b92bc6f6664366fede1cd50dd1da9d255d20c346d5d25b02":
        raise ValueError("wrong explicitly supplied reference")
    shutil.copyfile(reference,B/"sources"/"reference_summary.json")
    # The approved compiled packet already contains all30 CHNS_DEV_REF items.
    # Preserve those identities instead of counting a second representation.
    write(B/"registry.json",registry)
    evidence=load(B/"input"/"compiled_evidence.json")
    ids=[item["id"] for item in evidence["items"] if item["source_id"]=="CHNS_DEV_REF"]
    if len(ids)!=30: raise ValueError("Expected exactly30 existing supplied-reference items")
    validate_task(task); validate_evidence(evidence,task)
    write(B/"input"/"all_evidence.json",evidence)
    write(B/"input"/"r30_ids.json",ids)
    write(U/"PREPARE_RECEIPT.json",{"created_utc":datetime.now(timezone.utc).isoformat(),
       "inputs":{str(f.relative_to(B)):sha(f) for f in B.rglob("*") if f.is_file()},
       "n_calibration_statistics":len(ids),"patient_records_read":False,
       "uncertainty_note":"Full original reference file retains intervals; evidence entries make no marginal uncertainty claim."})
    print(json.dumps({"prepared":str(B),"statistics":len(ids)}))

def check_release():
    r=load(U/"PRE_FIT_RELEASE.json")
    if r["status"]!="released": raise ValueError("not released")
    for name,digest in r["files"].items():
        if sha(U/name)!=digest: raise ValueError("release binding changed: "+name)
    for name,digest in r.get("external_bindings",{}).items():
        if sha(Path(name))!=digest: raise ValueError("external release binding changed: "+name)
    return r

def package(fit_path):
    check_release()
    fit_path=Path(fit_path)
    fitted=load(fit_path)
    review=load(U/"POST_FIT_REVIEW.json")
    if review.get("status")!="pass" or review.get("fit_sha256")!=sha(fit_path):
        raise ValueError("matching post-fit mathematical review required")
    if fitted.get("fit_diagnostics",{}).get("generation_allowed") is not True:
        raise ValueError("declared fit law/integration gate failed; no generation")
    c=B/"candidates"/"statistical"; c.mkdir(parents=True,exist_ok=False)
    evidence=load(B/"input"/"all_evidence.json")
    write(c/"evidence.json",evidence)
    shutil.copyfile(fit_path,c/"fit_artifact.json")
    shutil.copyfile(U/"generator.py",c/"generator.py")
    shutil.copyfile(U/"SPEC.md",c/"MODEL_SPECIFICATION.md")
    assumptions=fitted.get("assumptions",[
      {"id":"A_STAT","description":"Prespecified bounded maximum-entropy tail-patchwork family; same-population summary calibration, no patient-row fitting."},
      {"id":"A_TAIL","description":"Shared upper-rank regime and fixed tail correlation0.8; distribution bounds derived from quantiles/SD are completion assumptions, not observed extremes."},
      {"id":"A_SEX","description":"Sex is independent Bernoulli; unreported sex relationships are not recovered."},
      {"id":"A_COV","description":"Age/BMI use declared common/difference Gaussian factors with independent residuals; detailed assumptions in MODEL_SPECIFICATION.md."},
      {"id":"A_SD","description":"Reported sample SD is used as population plug-in SD; no finite-sample moment forcing."}])
    if not all(set(a)=={"id","description"} for a in assumptions): raise ValueError("invalid assumptions")
    params=fitted["parameters"]; ids=load(B/"input"/"r30_ids.json")
    provenance={key:{"evidence_ids":ids,"assumption_ids":[a["id"] for a in assumptions],
      "derivation":"Computed by the declared fixed summary-calibration algorithm. Per-statistic use/nonuse and residuals are in fit_artifact.json; no individual records or final-seed fitting."} for key in params}
    write(c/"model_spec.json",{"parameters":params,"assumptions":assumptions,"parameter_provenance":provenance})
    (c/"decision.md").write_text("One predeclared statistical model calibrated to the openly supplied CHNS target summaries. Final draws are fixed; no revision or best-seed selection. External literature remains available/contextual as logged. This is not independent validation or source-population replay.\n",encoding="utf-8")
    write(c/"checks.json",{"scope":"source_only","records":[{"name":"declared_calibration_fit","status":"pass",
      "detail":"Fit artifact and disclosed-input provenance bound. This structural receipt does not establish scientific adequacy or exact fit."}],
      "artifacts":[{"path":"fit_artifact.json","sha256":sha(c/"fit_artifact.json")}]})
    receipt=freeze_candidate(B,c)
    write(U/"CANDIDATE_RECEIPT.json",{"candidate_freeze_sha256":sha(c/"freeze.json"),"fit_sha256":sha(fit_path),
       "acceptance":receipt["acceptance"],"n_rows":3000,"final_seeds":[4101,4102,4103]})
    print(json.dumps({"candidate":str(c),"frozen":True}))

def runfinal():
    check_release()
    if (U/"DRAW_CLOSURE.json").exists(): raise ValueError("closed; no reruns")
    results=[]
    for seed in (4101,4102,4103):
        run_id=f"final_{seed}"
        runpath=B/"executions"/run_id
        reservation=U/"final_attempts"/(run_id+".json")
        already_reserved=reservation.exists()
        if not already_reserved:
            write(reservation,{"seed":seed,"run_id":run_id,"created_utc":datetime.now(timezone.utc).isoformat(),
               "candidate_freeze_sha256":sha(B/"candidates/statistical/freeze.json"),"spent_even_if_interrupted":True})
        started=time.monotonic()
        try:
            if runpath.exists() or already_reserved:
                # Never repeat a reserved/interrupted slot. Missing receipts are failures.
                r=verify_execution(B,run_id)
            else:
                r=run_candidate(B,"statistical",run_id,seed,timeout_seconds=60,memory_mb=1024)
            record={"seed":seed,"run_id":run_id,"status":r["status"],"elapsed_seconds":r["elapsed_seconds"],
               "receipt_sha256":sha(runpath/"execution.json"),"error":r.get("error")}
        except (OSError,ValueError,TypeError,KeyError) as error:
            receipt=runpath/"execution.json"
            record={"seed":seed,"run_id":run_id,"status":"interrupted_or_invalid_receipt",
               "elapsed_seconds":time.monotonic()-started,"receipt_sha256":sha(receipt) if receipt.is_file() else None,
               "error":{"type":type(error).__name__,"message":str(error)[:1500]}}
        results.append(record)
    write(U/"DRAW_CLOSURE.json",{"created_utc":datetime.now(timezone.utc).isoformat(),"results":results,
      "final_attempts":len(results),"additional_attempts_allowed":0})
    print(json.dumps(results,indent=2))

def evaluate():
    check_release()
    closure=load(U/"DRAW_CLOSURE.json")
    if len(closure["results"])!=3: raise ValueError("draw closure incomplete")
    provider=module(P/"work"/"information_revision_ablation_2026-11-03"/"implementation"/"analysis_feedback.py","historical_primary")
    reference=load(B/"input"/"reference_summary.json")
    defs=load(B/"input"/"analysis_definitions.json")
    task=load(B/"task.json")
    out=[]
    d=U/"final_tables"; d.mkdir(exist_ok=False)
    for slot in closure["results"]:
        entry={**slot,"statistics":None}
        if slot["status"]=="success":
            r=verify_execution(B,slot["run_id"])
            if r["status"]!="success": raise ValueError("closure/receipt mismatch")
            path=B/"executions"/slot["run_id"]/"output"/"generated.csv"
            frame=read_table(path,task,output=True)
            entry["statistics"]=provider.with_reference(provider.generated_statistics(frame,defs),reference)
            entry["output_sha256"]=sha(path)
            shutil.copyfile(path,d/(slot["run_id"]+".csv"))
        out.append(entry)
    write(U/"PRIMARY_EVALUATION.json",{"reference_sha256":sha(B/"input"/"reference_summary.json"),
       "provider_sha256":sha(P/"work"/"information_revision_ablation_2026-11-03"/"implementation"/"analysis_feedback.py"),
       "interpretation":"Explicitly supplied summary calibration; not unseen-target validation.","runs":out})
    print(json.dumps({"evaluated":len(out),"successful":sum(x["status"]=="success" for x in out)}))

if __name__=="__main__":
    a=argparse.ArgumentParser(); a.add_argument("action",choices=["prepare","package","runfinal","evaluate"])
    a.add_argument("--fit-path"); args=a.parse_args()
    if args.action=="prepare": prepare()
    elif args.action=="package": package(args.fit_path)
    elif args.action=="runfinal": runfinal()
    else: evaluate()

