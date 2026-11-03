"""One reserved deterministic clinical fit; never draws rows."""
from pathlib import Path
import argparse, json, subprocess, sys, time
from datetime import datetime, timezone
import controller as c
U=Path(__file__).resolve().parent
def child():
    c.check_release()
    import statistical_fit as f
    result=f.fit(c.load(c.B/"input/reference_summary.json"))
    result["input_bindings"]={"reference_sha256":c.sha(c.B/"input/reference_summary.json"),
       "fit_code_sha256":c.sha(U/"statistical_fit.py"),"pre_fit_release_sha256":c.sha(U/"PRE_FIT_RELEASE.json")}
    c.write(U/"FIT.json",result)
    print(json.dumps({"termination":result["fit_diagnostics"]["termination"],
                     "generation_allowed":result["fit_diagnostics"]["generation_allowed"],
                     "wall_seconds":result["fit_diagnostics"]["wall_seconds"]}))
def main():
    c.check_release()
    c.write(U/"FIT_ATTEMPT.json",{"created_utc":datetime.now(timezone.utc).isoformat(),
        "single_procedure":True,"input_sha256":c.sha(c.B/"input/reference_summary.json"),
        "pre_fit_release_sha256":c.sha(U/"PRE_FIT_RELEASE.json"),"timeout_seconds":900,
        "no_patient_records":True,"no_draws":True})
    started=time.monotonic(); timed_out=False
    with (U/"fit.stdout.log").open("xb") as out,(U/"fit.stderr.log").open("xb") as err:
        try:
            r=subprocess.run([sys.executable,str(Path(__file__).resolve()),"--child"],cwd=U,
                stdout=out,stderr=err,stdin=subprocess.DEVNULL,timeout=900,check=False)
            code=r.returncode
        except subprocess.TimeoutExpired:
            timed_out=True; code=None
    artifact=U/"FIT.json"
    c.write(U/"FIT_EXECUTION.json",{"created_utc":datetime.now(timezone.utc).isoformat(),
       "returncode":code,"timeout":timed_out,"elapsed_seconds":time.monotonic()-started,
       "fit_sha256":c.sha(artifact) if artifact.exists() else None,
       "stdout_sha256":c.sha(U/"fit.stdout.log"),"stderr_sha256":c.sha(U/"fit.stderr.log"),
       "status":"completed" if code==0 and artifact.exists() else "failed","new_clinical_tables":0})
    print(json.dumps(c.load(U/"FIT_EXECUTION.json"),indent=2))
    raise SystemExit(0 if code==0 else 2)
if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--child",action="store_true"); a=p.parse_args()
    child() if a.child else main()

