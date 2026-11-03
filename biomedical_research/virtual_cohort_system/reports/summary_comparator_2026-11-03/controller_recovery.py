"""Disclosed path-only recovery; original failed slots remain immutable."""
from pathlib import Path
from datetime import datetime,timezone
import json,time,shutil
import controller as c
U=Path(__file__).resolve().parent
def run():
    c.check_release()
    release=c.load(U/"RECOVERY_RELEASE.json")
    for name,h in release["files"].items():
        if c.sha(U/name)!=h:raise ValueError("Recovery binding changed:"+name)
    if (U/"RECOVERY_DRAW_CLOSURE.json").exists():raise ValueError("recovery closed")
    old=c.load(U/"DRAW_CLOSURE.json")
    if len(old["results"])!=3 or any(r["status"]!="interrupted_or_invalid_receipt" or r["receipt_sha256"] is not None for r in old["results"]):
        raise ValueError("Recovery limited to recorded prelaunch failures")
    if any((c.B/"executions"/r["run_id"]).exists() for r in old["results"]):
        raise ValueError("Unexpected prior execution; not prelaunch-only")
    results=[]
    for seed in (4101,4102,4103):
        run_id=f"recovery_{seed}"; runpath=c.B/"executions"/run_id
        reservation=U/"recovery_attempts"/(run_id+".json")
        spent=reservation.exists()
        if not spent:
            c.write(reservation,{"seed":seed,"run_id":run_id,"created_utc":datetime.now(timezone.utc).isoformat(),
              "candidate_freeze_sha256":c.sha(c.B/"candidates/statistical/freeze.json"),"spent_even_if_interrupted":True})
        start=time.monotonic()
        try:
            r=c.verify_execution(c.B,run_id) if spent or runpath.exists() else c.run_candidate(c.B,"candidates/statistical",run_id,seed,timeout_seconds=60,memory_mb=1024)
            results.append({"seed":seed,"run_id":run_id,"status":r["status"],"elapsed_seconds":r["elapsed_seconds"],
               "receipt_sha256":c.sha(runpath/"execution.json"),"error":r.get("error")})
        except (OSError,ValueError,TypeError,KeyError) as e:
            f=runpath/"execution.json"
            results.append({"seed":seed,"run_id":run_id,"status":"interrupted_or_invalid_receipt",
              "elapsed_seconds":time.monotonic()-start,"receipt_sha256":c.sha(f) if f.is_file() else None,
              "error":{"type":type(e).__name__,"message":str(e)[:1500]}})
    c.write(U/"RECOVERY_DRAW_CLOSURE.json",{"results":results,"original_failure_closure_sha256":c.sha(U/"DRAW_CLOSURE.json"),
       "new_attempts":3,"total_orchestration_attempts":6,"maximum_actual_generator_attempts":3,"further_attempts_allowed":0})
    print(json.dumps(results,indent=2))
def evaluate():
    c.check_release()
    closure=c.load(U/"RECOVERY_DRAW_CLOSURE.json")
    provider=c.module(c.P/"work/information_revision_ablation_2026-11-03/implementation/analysis_feedback.py","primary_provider")
    ref=c.load(c.B/"input/reference_summary.json"); definitions=c.load(c.B/"input/analysis_definitions.json"); task=c.load(c.B/"task.json")
    dest=U/"final_tables";dest.mkdir(exist_ok=False);out=[]
    for slot in closure["results"]:
        entry={**slot,"statistics":None}
        if slot["status"]=="success":
            r=c.verify_execution(c.B,slot["run_id"])
            if r["status"]!="success":raise ValueError("Changed success receipt")
            file=c.B/"executions"/slot["run_id"]/"output/generated.csv"
            frame=c.read_table(file,task,output=True)
            entry["statistics"]=provider.with_reference(provider.generated_statistics(frame,definitions),ref)
            entry["output_sha256"]=c.sha(file);shutil.copyfile(file,dest/f"final_{slot['seed']}.csv")
        out.append(entry)
    c.write(U/"PRIMARY_EVALUATION.json",{"runs":out,"reference_sha256":c.sha(c.B/"input/reference_summary.json"),
       "closure_sha256":c.sha(U/"RECOVERY_DRAW_CLOSURE.json"),"original_failed_calls":3,
       "interpretation":"Supplied-summary calibration after disclosed prelaunch path recovery; no refit."})
    print(json.dumps({"evaluated":len(out),"successful":sum(r["status"]=="success" for r in out)}))
if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("action",choices=["run","evaluate"]);a=p.parse_args()
    run() if a.action=="run" else evaluate()

