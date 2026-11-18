"""Phase-sealed isolated execution for the economy paired-feedback pilot.

No provider/credential/reference-value access. All author code runs only through
the unchanged cohort_harness WSL/bubblewrap command and unchanged worker.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
PREVIOUS=PROJECT/"work/cross_model_api_pilot_2026-11-10"
sys.path.insert(0,str(PROJECT));sys.dont_write_bytecode=True
from cohort_harness import contracts,execution,lifecycle

SEEDS={"diagnostic":[41001,41003,41007],"evaluation":[42001,42003,42007]}
SLOTS={"diagnostic":6,"evaluation":36}
N_ROWS=3000
MAX_TABLES=42
LIMITS=dict(timeout_seconds=60,memory_mb=1536,output_bytes=20_000_000,log_bytes=50_000)
CASES={"PNS":["row_id","age","female","bmi","sbp","dbp"],
       "lipids":["id","age","sex","bmi","total_cholesterol","hdl_cholesterol"]}
MODELS={"OA_SOL","OA_ASTRA","DS_PRO"}
STAGED={"generator.py","model_spec.json","task.json","request.json","worker.py"}
WORKER=PROJECT/"cohort_harness/_worker.py"

def now():return datetime.now(timezone.utc).isoformat()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return lifecycle.read_json(path)
def require(ok,message):contracts.require(ok,message)
def safe(name,*,file=True):return lifecycle._path(ROOT,name,file=file)
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);execution._write(path,value)
def inventory(path):return {n:sha(lifecycle._path(path,n)) for n in lifecycle._files(path)}
def subtree(name):
    p=safe(name,file=False);require(p.is_dir(),"Missing captured subtree: "+name)
    result={name+"/"+n:d for n,d in inventory(p).items()}
    require(bool(result),"Empty captured subtree: "+name);return result


def implementation_hashes():
    paths=[Path(__file__),ROOT/"evaluate_stages.py",ROOT/"PROTOCOL.json",ROOT/"RUN_PLAN.json",WORKER,
           PROJECT/"cohort_harness/execution.py",PROJECT/"cohort_harness/contracts.py",PROJECT/"cohort_harness/lifecycle.py",
           PREVIOUS/"analyze_pilot.py",PREVIOUS/"execute_pilot.py",
           PROJECT/"work/next_case_validation_2026-11-09/runtime/analysis_tools.py",
           PROJECT/"work/scaleup_2026-11-01/analysis/k02_analysis.py"]
    return {p.relative_to(PROJECT).as_posix():sha(p) for p in paths}


def prepare_reference_snapshot():
    """Copy existing aggregate bytes; no patient reads, new fits, or reference reveal."""
    require(not safe("INITIAL_SEAL.json",file=False).exists(),"Initial seal already exists")
    source=PREVIOUS/"_host_only/REFERENCE_SNAPSHOT.json"
    destination=safe("_host_only/REFERENCE_SNAPSHOT.json",file=False)
    destination.parent.mkdir(parents=True,exist_ok=True)
    if destination.exists():
        require(sha(destination)==sha(source),"Existing snapshot differs; no overwrite allowed")
    else:
        with destination.open("xb") as stream:stream.write(source.read_bytes())
    require(sha(destination)==sha(source),"Snapshot copy changed")
    value={"created_utc":now(),"source":str(source),"source_sha256":sha(source),"snapshot_sha256":sha(destination),
           "patient_rows_read":False,"new_reference_fits":False,"author_visible":False}
    provenance=safe("_host_only/REFERENCE_COPY.json",file=False)
    if provenance.exists():
        existing=read(provenance)
        require(existing["source"]==str(source) and existing["source_sha256"]==sha(source) and existing["snapshot_sha256"]==sha(destination),"Existing snapshot provenance differs")
        return existing
    write(provenance,value);return value


def task_for(row):
    task=read(safe(row["task_path"]));contracts.validate_task(task)
    require(task["mode"]=="whole_cohort" and task["n_rows"]==N_ROWS,"Wrong task mode/count")
    require([c["name"] for c in task["columns"]]==CASES[row["case_id"]],"Wrong case columns")
    return task


def candidate_files(path,task):
    folder=safe(path,file=False)
    require(folder.is_dir(),"Candidate missing")
    files=inventory(folder)
    require({"generator.py","model_spec.json","decision_record.json"}<=set(files),"Candidate files missing")
    lifecycle.validate_program(folder/"generator.py")
    model=read(folder/"model_spec.json")
    require(set(model)=={"task","model"} and model["task"]==task and isinstance(model["model"],dict),"Task/model wrapper differs")
    require(isinstance(read(folder/"decision_record.json"),dict),"Decision record must be an object")
    return files


def initial_record(row):
    required={"parent_id","case_id","model_config","role","task_path","candidate_path","status"}
    optional={"context","failure_reason","files","task_sha256"}
    require(required<=set(row) and set(row)<=required|optional,"Wrong initial record fields")
    execution._name(row["parent_id"])
    require(row["case_id"] in CASES and row["model_config"] in MODELS,"Wrong case/model")
    require(row["role"] in {"paired_parent","benchmark"} and row["status"] in {"sealed","failed"},"Wrong initial role/status")
    task=task_for(row)
    if row["status"]=="failed":require(row["candidate_path"] is None,"Failed initial cannot nominate a candidate")
    return dict(row,task_sha256=sha(safe(row["task_path"])),files=(candidate_files(row["candidate_path"],task) if row["status"]=="sealed" else {}))


def schedule(rows,branches):
    require(len(rows)==8 and len({r["parent_id"] for r in rows})==8,"Eight unique initial outcomes required")
    for case in CASES:
        chosen=[r for r in rows if r["case_id"]==case]
        require(len(chosen)==4,"Four initial laws per case required")
        require(sorted((r["model_config"],r["role"]) for r in chosen)==sorted([
            ("OA_SOL","paired_parent"),("OA_SOL","benchmark"),("OA_ASTRA","benchmark"),("DS_PRO","benchmark")]),
            "Initial model/role allocation differs")
    parents={r["parent_id"] for r in rows if r["role"]=="paired_parent"}
    require(len(branches)==4 and len({b["branch_id"] for b in branches})==4,"Four unique review branches required")
    require(not {b["branch_id"] for b in branches}&{r["parent_id"] for r in rows},"Branch/parent IDs must differ")
    for branch in branches:
        require(set(branch)=={"branch_id","parent_id","arm"},"Wrong branch assignment fields")
        execution._name(branch["branch_id"])
    require({(b["parent_id"],b["arm"]) for b in branches}=={(p,a) for p in parents for a in ["feedback","second_look"]},
            "Both independent review arms must share each paired parent")


def seal_initial(records,branches):
    require(not safe("executions",file=False).exists(),"Cannot seal after execution begins")
    rows=[initial_record(r) for r in records];schedule(rows,branches)
    value={"kind":"economy_initial_seal_v1","created_utc":now(),"records":rows,"branches":branches,
           "seeds":SEEDS,"slot_limits":SLOTS,"max_tables":MAX_TABLES,"n_rows":N_ROWS,
           "implementation_hashes":implementation_hashes(),"packet_files":subtree("packets"),
           "initial_history_files":subtree("calls/initial"),
           "reference_snapshot_sha256":sha(safe("_host_only/REFERENCE_SNAPSHOT.json")),
           "reference_copy_sha256":sha(safe("_host_only/REFERENCE_COPY.json")),
           "all_initial_laws_fixed_before_diagnostics":True,"target_feedback":False}
    write(safe("INITIAL_SEAL.json",file=False),value);return verify_initial()


def verify_initial():
    value=read(safe("INITIAL_SEAL.json"));require(value["kind"]=="economy_initial_seal_v1","Wrong initial seal")
    require(value["seeds"]==SEEDS and value["slot_limits"]==SLOTS and value["max_tables"]==42 and value["n_rows"]==3000,"Changed schedule")
    require(value["implementation_hashes"]==implementation_hashes(),"Frozen implementation changed")
    require(value["packet_files"]==subtree("packets") and value["initial_history_files"]==subtree("calls/initial"),"Initial inputs/history changed")
    require(value["reference_snapshot_sha256"]==sha(safe("_host_only/REFERENCE_SNAPSHOT.json")) and
            value["reference_copy_sha256"]==sha(safe("_host_only/REFERENCE_COPY.json")),"Frozen aggregate snapshot changed")
    require(value["target_feedback"] is False and value["all_initial_laws_fixed_before_diagnostics"] is True,"Initial boundary differs")
    schedule(value["records"],value["branches"])
    require(all(initial_record(r)==r for r in value["records"]),"Initial candidate changed")
    return value


def verify_diagnostic_reports():
    closed=verify_stage_closure("diagnostic")
    reports=read(safe("DIAGNOSTIC_REPORTS.json"))
    require(reports["kind"]=="economy_generated_only_diagnostic_reports_v1" and reports["target_reference_read"] is False,"Invalid diagnostic report boundary")
    require(reports["diagnostic_closure_sha256"]==sha(safe("DIAGNOSTIC_CLOSURE.json")),"Diagnostic closure binding differs")
    require(len(reports["reports"])==2,"Two own-parent reports required")
    parents={r["parent_id"] for r in verify_initial()["records"] if r["role"]=="paired_parent"}
    require(set(reports["reports"])==parents,"Wrong diagnostic parents")
    for entry in reports["reports"].values():require(sha(safe(entry["path"]))==entry["sha256"],"Diagnostic report changed")
    return reports


def review_history(records):
    directory=safe("calls/review",file=False)
    values={"calls/review/"+n:d for n,d in inventory(directory).items()} if directory.exists() else {}
    outcomes=safe("REVIEW_OUTCOMES.json",file=False)
    if outcomes.exists():values["REVIEW_OUTCOMES.json"]=sha(outcomes)
    require(any(n.startswith("calls/review/") for n in values) or
            (all(r["disposition"]=="parent_failed" for r in records) and outcomes.exists()),
            "Missing review history; zero calls allowed only for four explicitly unavailable parent branches")
    return values


def seal_reviews(records):
    initial=verify_initial();verify_diagnostic_reports()
    require(not safe("executions/evaluation",file=False).exists(),"Cannot seal review after evaluation sampling")
    branches={b["branch_id"]:b for b in initial["branches"]};parents={r["parent_id"]:r for r in initial["records"]}
    require(len(records)==4 and {r["branch_id"] for r in records}==set(branches),"Four branch outcomes required")
    results=[]
    for record in records:
        required={"branch_id","parent_id","arm","disposition","candidate_path","reason"}
        require(set(record)==required,"Wrong review record fields")
        assignment=branches[record["branch_id"]];parent=parents[assignment["parent_id"]]
        require(all(record[k]==assignment[k] for k in assignment),"Review assignment changed")
        disposition=record["disposition"]
        require(disposition in {"revised","retained_noop","retained_review_failed","parent_failed"},"Wrong review disposition")
        require(isinstance(record["reason"],str) and bool(record["reason"].strip()),"Explicit final disposition reason required")
        if parent["status"]=="failed":
            require(disposition=="parent_failed" and record["candidate_path"] is None,"Failed paired parent cannot be rescued or replaced")
            files={}
        elif disposition in {"retained_noop","retained_review_failed"}:
            require(record["candidate_path"]==parent["candidate_path"],"Retained review must point to exact initial candidate")
            files=parent["files"]
        else:
            require(disposition=="revised" and record["candidate_path"]!=parent["candidate_path"],"Revised artifact needs its own directory")
            files=candidate_files(record["candidate_path"],task_for(parent))
        results.append(dict(record,files=files))
    value={"kind":"economy_review_seal_v1","created_utc":now(),"records":results,
           "initial_seal_sha256":sha(safe("INITIAL_SEAL.json")),"diagnostic_closure_sha256":sha(safe("DIAGNOSTIC_CLOSURE.json")),
           "diagnostic_reports_sha256":sha(safe("DIAGNOSTIC_REPORTS.json")),"review_history_files":review_history(results),
           "all_review_branches_fixed_before_evaluation":True,"host_scientific_edits":False,"target_feedback":False}
    write(safe("REVIEW_SEAL.json",file=False),value);return verify_reviews()


def verify_reviews():
    initial=verify_initial();verify_diagnostic_reports()
    value=read(safe("REVIEW_SEAL.json"))
    require(value["kind"]=="economy_review_seal_v1" and value["all_review_branches_fixed_before_evaluation"] is True and
            value["host_scientific_edits"] is False and value["target_feedback"] is False,"Wrong review boundary")
    for field,name in [("initial_seal_sha256","INITIAL_SEAL.json"),("diagnostic_closure_sha256","DIAGNOSTIC_CLOSURE.json"),
                       ("diagnostic_reports_sha256","DIAGNOSTIC_REPORTS.json")]:require(value[field]==sha(safe(name)),"Review seal binding differs")
    require(value["review_history_files"]==review_history(value["records"]),"Review call history changed")
    branches={b["branch_id"]:b for b in initial["branches"]};parents={r["parent_id"]:r for r in initial["records"]}
    require(len(value["records"])==4 and {r["branch_id"] for r in value["records"]}==set(branches),"Review coverage differs")
    for row in value["records"]:
        require(all(row[k]==branches[row["branch_id"]][k] for k in ["branch_id","parent_id","arm"]),"Review assignment differs")
        parent=parents[row["parent_id"]]
        if parent["status"]=="failed":require(row["disposition"]=="parent_failed" and row["candidate_path"] is None and row["files"]=={},"Failed parent rescue")
        else:
            require(row["files"]==candidate_files(row["candidate_path"],task_for(parent)),"Review candidate changed")
            if row["disposition"] in {"retained_noop","retained_review_failed"}:
                require(row["candidate_path"]==parent["candidate_path"] and row["files"]==parent["files"],"Retained parent changed")
            else:require(row["disposition"]=="revised" and row["candidate_path"]!=parent["candidate_path"],"Invalid final disposition")
    return value


def versions(stage):
    require(stage in SEEDS,"Unknown execution phase")
    initial=verify_initial()
    rows=[dict(r,version_id=r["parent_id"],version_kind="initial",arm=None) for r in initial["records"]
          if stage=="evaluation" or r["role"]=="paired_parent"]
    if stage=="evaluation":
        parents={r["parent_id"]:r for r in initial["records"]}
        for record in verify_reviews()["records"]:
            parent=parents[record["parent_id"]]
            rows.append(dict(parent,version_id=record["branch_id"],version_kind="review",arm=record["arm"],
                candidate_path=record["candidate_path"],status="sealed" if record["candidate_path"] is not None else "failed",
                disposition=record["disposition"],files=record["files"]))
    require(len(rows)*3==SLOTS[stage],"Wrong stage version count")
    return rows


def stage_seal_name(stage):return "INITIAL_SEAL.json" if stage=="diagnostic" else "REVIEW_SEAL.json"
def closure_name(stage):return stage.upper()+"_CLOSURE.json"
def approve_stage(stage,note):
    versions(stage)
    require(isinstance(note,str) and bool(note.strip()),"Root review note required")
    value={"kind":"economy_root_stage_approval_v1","stage":stage,"created_utc":now(),"note":note,
           "stage_seal_sha256":sha(safe(stage_seal_name(stage))),"implementation_hashes":implementation_hashes()}
    write(safe("APPROVAL_"+stage.upper()+".json",file=False),value);return value
def approved(stage):
    rows=versions(stage);value=read(safe("APPROVAL_"+stage.upper()+".json"))
    require(value["kind"]=="economy_root_stage_approval_v1" and value["stage"]==stage and
            value["stage_seal_sha256"]==sha(safe(stage_seal_name(stage))) and value["implementation_hashes"]==implementation_hashes(),
            "Stage freeze approval differs")
    return rows


def runs(stage,_rows=None):
    root=safe("executions/"+stage,file=False)
    if not root.exists():return {}
    allowed={r["version_id"] for r in (versions(stage) if _rows is None else _rows)};found={}
    for folder in root.iterdir():
        require(folder.is_dir() and not lifecycle._link(folder) and folder.name in allowed,"Unexpected stage version")
        for run in folder.iterdir():
            require(run.is_dir() and not lifecycle._link(run) and run.name in {f"seed_{s}" for s in SEEDS[stage]},"Unscheduled run/retry")
            found[(folder.name,int(run.name[5:]))]=run
    require(len(found)<=SLOTS[stage],"Stage table budget exceeded")
    return found


def validate_output(frame,task,case):
    contracts.validate_output(None,frame,task)
    if case=="lipids":require(all(bool(frame[n].gt(0).all()) for n in ["bmi","total_cholesterol","hdl_cholesterol"]),
                              "Lipid BMI/TC/HDL must be strictly positive; no row removal")


def _run_one(stage,row,seed):
    require(row in approved(stage) and seed in SEEDS[stage],"Unsealed version or seed")
    operation=read(safe("RUNNING.lock"));require(operation["stage"]==stage,"Execution phase lock differs")
    require((row["version_id"],seed) not in runs(stage),"Slot already consumed")
    run=safe(f"executions/{stage}/{row['version_id']}/seed_{seed}",file=False);run.mkdir(parents=True,exist_ok=False)
    receipt={"kind":"economy_isolated_execution_v1","stage":stage,"version_id":row["version_id"],"parent_id":row["parent_id"],
             "case_id":row["case_id"],"seed":seed,"created_utc":now(),"status":"failed","failure_class":None,
             "generator_executed":False,"target_reference_read":False,"isolation_scope":"generator_process_only",
             "agent_isolation":"not_provided","limits":execution._limits(**LIMITS,seed=seed),"process":None,
             "stage_seal_sha256":sha(safe(stage_seal_name(stage))),"generated_sha256":None,"error":None,"files":{}}
    write(run/"ATTEMPT.json",{k:receipt[k] for k in ["stage","version_id","parent_id","seed","created_utc","limits"]})
    bindings=None;phase="infrastructure"
    try:
        if row["status"]=="failed":receipt.update(status="candidate_unavailable",failure_class="candidate_unavailable")
        else:
            stage_dir,output=run/"input",run/"output";stage_dir.mkdir();output.mkdir()
            candidate=safe(row["candidate_path"],file=False)
            copies={"generator.py":candidate/"generator.py","model_spec.json":candidate/"model_spec.json", "task.json":safe(row["task_path"]),"worker.py":WORKER}
            for name,source in copies.items():(stage_dir/name).write_bytes(source.read_bytes())
            write(stage_dir/"request.json",receipt["limits"]);bindings=inventory(stage_dir)
            require(set(bindings)==STAGED and all(bindings[n]==sha(p) for n,p in copies.items()),"Staged inputs differ")
            write(run/"input_bindings.json",bindings)
            runtime=execution._runtime(None);write(run/"runtime_manifest.json",execution._runtime_manifest(runtime))
            for name in ["generated.csv","worker_report.json"]:(output/name).touch(exist_ok=False)
            command=execution._command(runtime,run,LIMITS["timeout_seconds"])
            write(run/"launch.json",{"command":command,"runtime":runtime,"worker_sha256":bindings["worker.py"],"reference_staged":False,"source_staged":False})
            approved(stage);receipt["generator_executed"]=None
            receipt["process"]=execution._capture(command,run,LIMITS["timeout_seconds"]+20,LIMITS["log_bytes"],run/"stdout.log",run/"stderr.log")
            process=receipt["process"];require((output/"worker_report.json").stat().st_size<=65536,"Oversized worker report")
            worker=read(output/"worker_report.json") if (output/"worker_report.json").stat().st_size else {}
            receipt["generator_executed"]=worker.get("generator_started");phase="worker_result"
            if process["host_timeout"] or process["returncode"] in {124,137,-9}:receipt["status"]="timeout"
            require(process["returncode"]==0 and worker.get("status")=="completed" and worker.get("generator_started") is True,"Worker did not complete")
            phase="output_validation";task=task_for(row)
            execution._csv_guard(output/"generated.csv",task,LIMITS["output_bytes"])
            validate_output(lifecycle.read_table(output/"generated.csv",task,output=True),task,row["case_id"])
            receipt.update(status="success",generated_sha256=sha(output/"generated.csv"))
    except Exception as error:
        receipt.update(error={"type":type(error).__name__,"message":str(error)[:1500]},failure_class=(
            "author_execution_or_output" if receipt["generator_executed"] is True and phase in {"worker_result","output_validation"} else "infrastructure_unknown_or_integrity"))
    finally:
        try:
            approved(stage)
            if bindings is not None:require(inventory(run/"input")==bindings,"Staged input mutated")
            if (run/"output").exists():require(set(inventory(run/"output"))<={"generated.csv","worker_report.json"},"Unexpected output artifact")
            receipt["files"]=inventory(run)
        except Exception as error:
            receipt.update(status="failed",failure_class="infrastructure_unknown_or_integrity",error={"type":type(error).__name__,"message":str(error)[:1500]},files={})
        receipt["completed_utc"]=now();write(run/"execution.json",receipt)
    return receipt


def _verify_execution(stage,row,seed,run):
    """Leaf verifier; callers first verify the phase and its complete version set."""
    version_id=row["version_id"]
    require(seed in SEEDS[stage] and run is not None,"Unscheduled or unconsumed slot")
    value=read(run/"execution.json")
    require(value["kind"]=="economy_isolated_execution_v1" and (value["stage"],value["version_id"],value["seed"])==(stage,version_id,seed),"Execution identity differs")
    require(value["status"] in {"success","failed","timeout","candidate_unavailable"},"Wrong execution status")
    require(value["limits"]==execution._limits(**LIMITS,seed=seed) and value["stage_seal_sha256"]==sha(safe(stage_seal_name(stage))),"Execution seal/limits differ")
    require(value["target_reference_read"] is False and value["isolation_scope"]=="generator_process_only" and value["agent_isolation"]=="not_provided","Execution scope differs")
    require(value["failure_class"] in {None,"candidate_unavailable","author_execution_or_output","infrastructure_unknown_or_integrity"},"Wrong failure class")
    require((value["status"]=="success")== (value["failure_class"] is None),"Status/failure class mismatch")
    require((value["status"]=="candidate_unavailable")== (row["status"]=="failed"),"Unavailable candidate accounting differs")
    actual=inventory(run);actual.pop("execution.json");require(actual==value["files"] and bool(actual),"Execution bytes changed")
    if value["status"]=="success" or value["failure_class"]=="author_execution_or_output":
        require(value["generator_executed"] is True,"Author execution requires worker entry")
        launch=read(run/"launch.json");bindings=read(run/"input_bindings.json")
        require(launch["command"]==execution._command(execution.DEFAULT_RUNTIME,run,LIMITS["timeout_seconds"]) and launch["runtime"]==execution.DEFAULT_RUNTIME and
                launch["reference_staged"] is False and launch["source_staged"] is False,"Isolation launch differs")
        require(set(inventory(run/"input"))==STAGED and inventory(run/"input")==bindings and read(run/"input/request.json")==value["limits"],"Staged inventory differs")
        candidate=safe(row["candidate_path"],file=False)
        for name,source in {"generator.py":candidate/"generator.py","model_spec.json":candidate/"model_spec.json","task.json":safe(row["task_path"]),"worker.py":WORKER}.items():
            require(bindings[name]==sha(source),"Staged file differs from frozen source")
        require(set(inventory(run/"output"))=={"generated.csv","worker_report.json"},"Output inventory differs")
    if value["status"]=="success":
        require(value["generated_sha256"]==sha(run/"output/generated.csv") and value["process"]["returncode"]==0 and not value["process"]["host_timeout"],"Success receipt differs")
        task=task_for(row);execution._csv_guard(run/"output/generated.csv",task,LIMITS["output_bytes"])
        validate_output(lifecycle.read_table(run/"output/generated.csv",task,output=True),task,row["case_id"])
    return value


def verify_execution(stage,version_id,seed):
    rows=approved(stage);candidates=[r for r in rows if r["version_id"]==version_id]
    require(len(candidates)==1,"Unscheduled version")
    return _verify_execution(stage,candidates[0],seed,runs(stage,rows).get((version_id,seed)))


def run_stage(stage):
    rows=approved(stage);require(not runs(stage),"Stage is create-only; no silent restart")
    require(not safe(closure_name(stage),file=False).exists(),"Stage already closed")
    busy=safe("RUNNING.lock",file=False);write(busy,{"stage":stage,"created_utc":now(),"planned_slots":SLOTS[stage]})
    completed=False
    try:
        for row in rows:
            for seed in SEEDS[stage]:
                value=_run_one(stage,row,seed)
                require(value["failure_class"]!="infrastructure_unknown_or_integrity","Infrastructure/integrity failure: halt; consumed receipt and lock retained")
        completed=True
    finally:
        if completed:busy.unlink()
    return close_stage(stage)


def close_stage(stage):
    rows=approved(stage);require(not safe("RUNNING.lock",file=False).exists(),"Execution active/interrupted")
    expected={(r["version_id"],s) for r in rows for s in SEEDS[stage]}
    run_map=runs(stage,rows);row_map={r["version_id"]:r for r in rows}
    require(set(run_map)==expected,"All scheduled stage slots must have outcomes")
    records=[]
    for version_id,seed in sorted(expected):
        value=_verify_execution(stage,row_map[version_id],seed,run_map[(version_id,seed)])
        require(value["failure_class"]!="infrastructure_unknown_or_integrity","Infrastructure failure requires audit")
        records.append({"version_id":version_id,"seed":seed,"status":value["status"],"execution_sha256":sha(run_map[(version_id,seed)]/"execution.json")})
    value={"kind":"economy_stage_closure_v1","stage":stage,"created_utc":now(),"records":records,"scheduled_slots":SLOTS[stage],
           "physical_generator_attempts":sum(r["status"]!="candidate_unavailable" for r in records),
           "stage_seal_sha256":sha(safe(stage_seal_name(stage)))}
    write(safe(closure_name(stage),file=False),value);return value


def verify_stage_closure(stage):
    rows=approved(stage)
    busy=safe("RUNNING.lock",file=False)
    if busy.exists():
        # A sealed diagnostic phase remains verifiable while the later evaluation
        # phase runs. Its own active/interrupted phase may never claim closure.
        operation=read(busy)
        require(stage=="diagnostic" and operation.get("stage")=="evaluation","Execution not closed")
    value=read(safe(closure_name(stage)))
    require(value["kind"]=="economy_stage_closure_v1" and value["stage"]==stage and value["scheduled_slots"]==SLOTS[stage],"Wrong stage closure")
    require(value["stage_seal_sha256"]==sha(safe(stage_seal_name(stage))),"Stage seal binding differs")
    expected={(r["version_id"],s) for r in rows for s in SEEDS[stage]}
    require(len(value["records"])==SLOTS[stage] and {(r["version_id"],r["seed"]) for r in value["records"]}==expected,"Stage coverage differs")
    run_map=runs(stage,rows);row_map={r["version_id"]:r for r in rows}
    require(set(run_map)==expected,"Stage run inventory differs")
    for row in value["records"]:
        receipt=_verify_execution(stage,row_map[row["version_id"]],row["seed"],run_map[(row["version_id"],row["seed"])])
        require(row["status"]==receipt["status"] and row["execution_sha256"]==sha(run_map[(row["version_id"],row["seed"])]/"execution.json"),"Stage receipt binding differs")
    return value


def runtime_probe():
    value={"created_utc":now(),"generator_executed":False,"runtime":execution.DEFAULT_RUNTIME,"fallback_allowed":False,
           "availability_scope":"trusted imports/file hashes only; no namespace launch"}
    try:value.update(status="available",manifest=execution._runtime_manifest(execution._runtime(None)))
    except Exception as error:value.update(status="unavailable",error_type=type(error).__name__,error=str(error))
    return value


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("command",choices=["probe","prepare-reference","run-diagnostic","run-evaluation"])
    a=p.parse_args();result=runtime_probe() if a.command=="probe" else prepare_reference_snapshot() if a.command=="prepare-reference" else run_stage(a.command.removeprefix("run-"))
    print(json.dumps(result,indent=2,allow_nan=False))
