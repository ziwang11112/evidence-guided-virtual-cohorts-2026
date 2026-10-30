"""Append-only M11 controller. Reference parsing occurs only after release gate."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[1]
sys.path.insert(0,str(PROJECT))
sys.path.insert(0,str(HERE/"evaluator"))
from cohort_harness.lifecycle import verify_candidate
from cohort_harness.execution import run_candidate, verify_execution
from analysis import points, errors, preservation, require, require_aligned

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def write(p,v):
    with Path(p).open("x",encoding="utf-8",newline="\n") as f:
        json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False); f.write("\n")
def now(): return datetime.now(timezone.utc).isoformat()
def bind(p): return {"path":str(Path(p).resolve()),"sha256":sha(p)}
def csv(p): return pd.read_csv(p,dtype={"row_id":str},float_precision="round_trip")

def check_bindings(items):
    require(isinstance(items,list) and bool(items),"Empty bindings")
    seen=set()
    for item in items:
        path=Path(item["path"])
        require(path.is_absolute() and str(path) not in seen,"Duplicate/relative binding")
        seen.add(str(path))
        require(sha(path)==item["sha256"],"Changed binding: "+str(path))

def required_paths():
    paths=[HERE/"protocol.json",HERE/"campaign.py",HERE/"evaluator/analysis.py",HERE/"evaluator/test_analysis.py",
           HERE/"evaluator/test_gate.py",HERE/"evaluator/README.md",HERE/"prepare_bundles.py",HERE/"source_admission.json",
           HERE/"source_audit/source_plan.json",HERE/"custodian/visible/observed.csv",HERE/"custodian/visible/task_safe_manifest.json",
           HERE/"custodian/private/design_weights.csv",HERE/"custodian/private/reference.csv",HERE/"custodian/private/id_mapping.csv",
           HERE/"custodian/preparation_receipt.json",HERE/"custodian/freshness_access_manifest.json",
           PROJECT/"work/m2-runtime-config.json"]
    paths+=sorted((PROJECT/"cohort_harness").glob("*.py"))
    for suffix in ["*.py","*.md","*.json"]:
        paths+=sorted((HERE/"source_audit").glob(suffix))
    return list(dict.fromkeys(p.resolve() for p in paths))

def prepared_inputs():
    receipt=read(HERE/"custodian/preparation_receipt.json")
    expected={"observed":"visible/observed.csv","design_weights":"private/design_weights.csv",
              "reference":"private/reference.csv","id_mapping":"private/id_mapping.csv"}
    require(set(receipt["artifacts"])==set(expected),"Prepared artifact inventory mismatch")
    for name,relative in expected.items():
        item=receipt["artifacts"][name]
        require(item["path"]==relative,"Prepared artifact path mismatch")
        require(sha(HERE/"custodian"/relative)==item["sha256"],"Prepared input changed: "+name)
    require(sha(HERE/"custodian/visible/task_safe_manifest.json")==receipt["task_safe_manifest_sha256"],"Prepared safe manifest changed")
    canonical=receipt["artifacts"]["observed"]["sha256"]
    for family in read(HERE/"protocol.json")["families"]:
        require(sha(HERE/family/"observed.csv")==canonical,"Bundle observed differs from canonical")
    return receipt

def freeze_launch():
    prepared_inputs()
    protocol=read(HERE/"protocol.json")
    sourceplan=HERE/"source_audit/source_plan.json"
    require(sourceplan.is_file(),"Source scenario plan not finalized")
    candidates=[]
    for family in protocol["families"]:
        bundle=HERE/family
        inherited=PROJECT/"reports/analysis_utility_feasibility_2026-10-30/constructions"/family/"selected"
        base=read(bundle/"candidates/initial/model_spec.json")["parameters"]
        require(base==read(inherited/"model_spec.json")["parameters"],"Initial parameters differ from inherited family")
        key="location_pct" if family=="ha" else "location_by_sex"
        for arm in protocol["arms"]:
            c=bundle/"candidates"/arm
            verify_candidate(bundle,c)
            require(sha(c/"generator.py")==sha(inherited/"generator.py"),"Scientific formula changed")
            parameters=read(c/"model_spec.json")["parameters"]
            require(set(parameters)==set(base),"Parameter keys changed")
            require({k:v for k,v in parameters.items() if k!=key}=={k:v for k,v in base.items() if k!=key},"Nonlocation parameter changed")
            require(set(parameters[key])=={"male","female"},"Location sex keys changed")
            candidates.append({"family":family,"arm":arm,"bundle":str(bundle),"candidate":"candidates/"+arm,"freeze_sha256":sha(c/"freeze.json")})
    paths=required_paths()
    schedule=[]
    for c in candidates:
        for seed in protocol["target_seeds"]:
            schedule.append({**c,"seed":seed,"run_id":f"t_{c['arm']}_{seed}"})
    require(len(schedule)==protocol["expected_target_tables"],"Schedule mismatch")
    value={"schema_version":"m11-launch-1","created_utc":now(),"bindings":[bind(p) for p in paths],
           "candidates":candidates,"schedule":schedule,"evaluator_reference_opened":False,
           "custodian_preparation_exception":True,"scientific_role":"Source Agent chose context models and scalar calibration; inherited generators, controller executes and evaluates"}
    write(HERE/"launch.json",value)
    print(json.dumps({"stage":"launch_frozen","candidates":len(candidates),"tables":len(schedule),"sha256":sha(HERE/"launch.json")}))

def verified_launch():
    launch=read(HERE/"launch.json")
    require(launch["schema_version"]=="m11-launch-1","Wrong launch schema")
    require({Path(x["path"]).resolve() for x in launch["bindings"]}==set(required_paths()),"Mandatory binding inventory mismatch")
    check_bindings(launch["bindings"])
    prepared_inputs()
    protocol=read(HERE/"protocol.json")
    expected={(f,a,s) for f in protocol["families"] for a in protocol["arms"] for s in protocol["target_seeds"]}
    actual=[(x["family"],x["arm"],x["seed"]) for x in launch["schedule"]]
    require(len(actual)==len(set(actual)) and set(actual)==expected,"Incomplete/duplicate launch schedule")
    for entry in launch["schedule"]:
        bundle=Path(entry["bundle"])
        require(bundle.resolve()==(HERE/entry["family"]).resolve(),"Bundle mismatch")
        require(entry["candidate"]=="candidates/"+entry["arm"],"Candidate mismatch")
        verify_candidate(bundle,entry["candidate"])
        require(sha(bundle/entry["candidate"]/"freeze.json")==entry["freeze_sha256"],"Freeze changed")
    return launch

def execute():
    launch=verified_launch()
    runtime=read(PROJECT/"work/m2-runtime-config.json")
    for entry in launch["schedule"]:
        bundle=Path(entry["bundle"])
        run=bundle/"executions"/entry["run_id"]
        if run.exists():
            receipt=verify_execution(bundle,entry["run_id"])
        else:
            receipt=run_candidate(bundle,entry["candidate"],entry["run_id"],entry["seed"],runtime=runtime,timeout_seconds=60)
        print(json.dumps({"family":entry["family"],"arm":entry["arm"],"seed":entry["seed"],"status":receipt["status"]}),flush=True)
        require(receipt["status"]=="success","Generation failed; retain receipt and stop before release")
        verify_execution(bundle,entry["run_id"])

def seal():
    launch=verified_launch(); runs=[]
    for entry in launch["schedule"]:
        receipt=verify_execution(entry["bundle"],entry["run_id"])
        require(receipt["status"]=="success","Cannot seal failed run")
        require(receipt["candidate"]==entry["candidate"] and receipt["limits"]["seed"]==entry["seed"],"Run/candidate/seed mismatch")
        run=Path(entry["bundle"])/"executions"/entry["run_id"]
        runs.append({"family":entry["family"],"arm":entry["arm"],"seed":entry["seed"],"run_id":entry["run_id"],
                     "receipt":bind(run/"execution.json"),"generated":bind(run/"output/generated.csv")})
    write(HERE/"release.json",{"schema_version":"m11-release-1","created_utc":now(),"launch":bind(HERE/"launch.json"),"executions":runs,"evaluator_reference_opened":False})
    print(json.dumps({"stage":"release_sealed","tables":len(runs),"reference_parsed_by_evaluator":False}))

def verify_release():
    release=read(HERE/"release.json")
    require(release["schema_version"]=="m11-release-1","Wrong release schema")
    require(Path(release["launch"]["path"]).resolve()==(HERE/"launch.json").resolve(),"Wrong launch path")
    check_bindings([release["launch"]])
    launch=verified_launch()
    planned={(x["family"],x["arm"],x["seed"]):x for x in launch["schedule"]}
    actual=[(x["family"],x["arm"],x["seed"]) for x in release["executions"]]
    require(len(actual)==len(set(actual)) and set(actual)==set(planned),"Incomplete release schedule")
    for entry in release["executions"]:
        p=planned[(entry["family"],entry["arm"],entry["seed"])]
        require(entry["run_id"]==p["run_id"],"Release run mismatch")
        run=Path(p["bundle"])/"executions"/p["run_id"]
        require(Path(entry["generated"]["path"]).resolve()==(run/"output/generated.csv").resolve(),"Output path mismatch")
        require(Path(entry["receipt"]["path"]).resolve()==(run/"execution.json").resolve(),"Receipt path mismatch")
        check_bindings([entry["generated"],entry["receipt"]])
        receipt=verify_execution(p["bundle"],p["run_id"])
        require(receipt["status"]=="success" and receipt["candidate"]==p["candidate"],"Failed/wrong candidate")
        require(receipt["limits"]["seed"]==p["seed"] and receipt["candidate_freeze_sha256"]==p["freeze_sha256"],"Seed/freeze mismatch")
    # Check canonical covariate alignment before opening the sealed reference.
    observed=csv(HERE/"custodian/visible/observed.csv")
    design=csv(HERE/"custodian/private/design_weights.csv")
    require_aligned(design,observed.row_id,["row_id","weight","stratum","psu"])
    require(np.isfinite(design.weight).all() and design.weight.gt(0).all(),"Invalid prepared weights")
    for entry in release["executions"]:
        generated=csv(entry["generated"]["path"])
        require_aligned(generated,observed.row_id,list(observed.columns)+["hba1c_pct"])
        require(generated[list(observed.columns)].equals(observed),"Generated covariates differ from canonical")
    return release

def evaluate():
    release=verify_release()  # Must finish before any sealed reference parsing below.
    out=HERE/"results"; out.mkdir(exist_ok=False)
    observed=csv(HERE/"custodian/visible/observed.csv")
    design=csv(HERE/"custodian/private/design_weights.csv")
    reference=csv(HERE/"custodian/private/reference.csv")
    require_aligned(design,observed.row_id,["row_id","weight","stratum","psu"])
    require_aligned(reference,observed.row_id,["row_id","hba1c_pct"])
    real=points(observed,reference.hba1c_pct,design.weight)
    rows=[]; detail=[]
    for entry in release["executions"]:
        generated=csv(entry["generated"]["path"])
        require_aligned(generated,observed.row_id,list(observed.columns)+["hba1c_pct"])
        require(generated[list(observed.columns)].equals(observed),"Observed values changed")
        p=points(observed,generated.hba1c_pct,design.weight)
        key={k:entry[k] for k in ["family","arm","seed"]}
        rows.append({**key,**errors(real,p)})
        detail.append({**key,"points":p})
    frame=pd.DataFrame(rows)
    initial=frame.loc[frame.arm.eq("initial")].set_index(["family","seed"])
    point_lookup={(x["family"],x["arm"],x["seed"]):x["points"] for x in detail}
    paired=[]
    for row in rows:
        if row["arm"]=="initial": continue
        baseline=initial.loc[(row["family"],row["seed"])]
        values={k:row[k] for k in ["family","arm","seed"]}
        for k in ["sex_median_mae","age_sex_cell_mean_mae","q90_absolute_error"]:
            values[k+"_change"]=row[k]-float(baseline[k]) if row[k] is not None else None
        values.update(preservation(point_lookup[(row["family"],"initial",row["seed"])],point_lookup[(row["family"],row["arm"],row["seed"])]))
        paired.append(values)
    frame.to_csv(out/"errors.csv",index=False)
    pd.DataFrame(paired).to_csv(out/"paired_changes.csv",index=False)
    write(out/"analysis.json",{"schema_version":"m11-results-1","created_utc":now(),"release_sha256":sha(HERE/"release.json"),"n":len(observed),"reference":real,"generated":detail,
        "interpretation":"Descriptive weighted analysis only; residual draws dependent; no clinical equivalence or independent biological replication"})
    print(json.dumps({"stage":"evaluated","rows":len(observed),"tables":len(rows),"results":str(out)}))

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("stage",choices=["freeze","execute","seal","gate","evaluate"])
    command=p.parse_args().stage
    {"freeze":freeze_launch,"execute":execute,"seal":seal,"gate":verify_release,"evaluate":evaluate}[command]()
