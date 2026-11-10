"""Thin procedural controller around unchanged additive adaptive_session_v2.

There is no model client or Agent filesystem sandbox. The host launches actual
fresh-context collaborators and supplies truthful dispatch/review receipts.
Only the inherited execution module may execute authored scientific programs.
"""
from __future__ import annotations
import contextlib
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
sys.path.insert(0, str(PROJECT))
from cohort_harness import adaptive_session_v2 as native
from cohort_harness import lifecycle as lc, execution
from cohort_harness import whole_cohort_source_replay_v1 as source
from cohort_harness.contracts import require, exact_keys, validate_task

SESSIONS = HERE / "sessions"
FREEZE = HERE / "METHOD_FREEZE.json"
GATES = {"case_admission", "source_adequacy", "implementation_review", "method_freeze"}
REVIEW_CHECKS = {"no_reference_access", "parameter_provenance", "bounded_behavior", "schema", "feedback_semantics", "no_desired_sign_requirement"}
MODEL_FIELDS = {"requested_model", "returned_model", "provider", "model_snapshot", "reasoning_effort", "temperature", "token_usage"}

def read(path):
    return lc.read_json(Path(path))

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()

def write_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as f:
        json.dump(value, f, indent=2, ensure_ascii=False, allow_nan=False)
        f.write("\n")

def safe(root, name):
    return lc._path(Path(root), name, file=False)

def inventory(root, exclude=()):
    root = Path(root)
    return {p.relative_to(root).as_posix(): lc.sha256(p)
            for p in sorted(root.rglob("*")) if p.is_file()
            and p.name not in {".controller.lock", ".operation.lock"}
            and p.relative_to(root).as_posix() not in exclude
            and not require_link(p)}

def require_link(path):
    require(not any(lc._link(p) for p in (path, *path.parents)), "Links are forbidden")
    return False

def config():
    c = read(HERE / "study_config.json")
    validate_task(c["task"])
    require(c["author_ids"] == ["A01", "A02", "A03", "A04", "A05"], "Five fixed author slots required")
    require(c["seeds"] == [271,409,557], "Fixed seeds changed")
    require(c["session_limits"] == {"actions":100,"candidates":2,"executions":6,"feedbacks":6,"analyses":6}, "Session budget changed")
    require(c["task"]["budget"] == {"source_queries":12,"source_downloads":10,"revisions":1}, "Retrieval/revision budget changed")
    require(c["task"]["mode"] == "whole_cohort" and c["task"]["n_rows"] == 3000, "Wrong task mode/size")
    require([x["name"] for x in c["task"]["columns"]] == ["row_id","age","female","bmi","sbp","dbp"], "Wrong output schema")
    require(c["retrieval_limits"]["source_bytes"] == 50*1024*1024, "Source byte budget changed")
    require(c["source_replay_limits"]["executions"] == 6, "Source replay budget changed")
    require(c["analysis_adapter"]["filename"] == "analysis_tools.py", "Adapter path is fixed; target paths forbidden")
    require(lc.sha256(HERE / "analysis_tools.py") == c["analysis_adapter"]["sha256"], "Analysis adapter changed")
    return c

def bindings():
    """Files root must bind after review; no clinical/target file is opened."""
    names = ["controller.py","cli.py","study_config.json","AUTHOR_TASK.md","README.md",
             "RECEIPT_SCHEMAS.md","analysis_tools.py","evaluator.py","independent_check.py"]
    files = {(HERE/n).relative_to(PROJECT).as_posix(): lc.sha256(HERE/n) for n in names}
    files.update({"cohort_harness/"+n:h for n,h in native._engines().items()})
    files["cohort_harness/whole_cohort_source_replay_v1.py"] = lc.sha256(Path(source.__file__))
    files["cohort_harness/analysis_evidence.py"] = lc.sha256(PROJECT/"cohort_harness/analysis_evidence.py")
    for name in ("PROTOCOL.md","SELECTION_LOCK.json","READINESS.json"):
        files[(HERE.parent/name).relative_to(PROJECT).as_posix()] = lc.sha256(HERE.parent/name)
    return files

def check_freeze():
    f = read(FREEZE)
    require(f.get("kind") == "pns_bp_method_freeze" and f.get("status") == "approved", "No approved method freeze")
    require(f.get("gates") == {k:True for k in GATES}, "All admission/source/review/freeze gates must pass")
    require(bool(f.get("reviewed_by")), "Root approval identity missing")
    require(f["files"] == bindings(), "Frozen method bindings changed")
    packet = f["source_packet"]
    root = Path(packet["path"]).resolve()
    require(root.is_relative_to(HERE.parent) and not any(x.casefold() in {"custodian","target","clinical_reference"} for x in root.parts), "Source packet must be in approved new-case area")
    require(inventory(root) == packet["files"], "Source packet inventory/hash changed")
    for name in packet["files"]:
        require(name.startswith(("sources/","skills/","input/")), "Packet may contain only source, skill and visible input files")
    require(bool(f.get("source_families")), "Original-source family mapping required")
    require(isinstance(f.get("source_registry"), list) and bool(f["source_registry"]), "Vetted source registry required")
    return f

def bundle(author):
    require(author in config()["author_ids"], "Unknown author slot")
    return SESSIONS / author

@contextlib.contextmanager
def lock(root):
    path = Path(root)/".controller.lock"
    fd = os.open(path, os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    try:
        os.write(fd, str(os.getpid()).encode()); os.close(fd)
        yield
    finally:
        path.unlink()

def session_config(c):
    return {"schema_version":2,"limits":c["session_limits"],"allowed_seeds":c["seeds"],
        "runtime":c["runtime"],"execution_limits":c["execution_limits"],"web_evidence":c["web_evidence"],
        "analysis_adapters":{"generated":{"path":str(HERE/"analysis_tools.py"),
            "function":"analyze","sha256":c["analysis_adapter"]["sha256"]}}}

def validate_dispatch(d, author):
    exact_keys(d, {"author_id","agent_id","fresh_context","fork_turns","model_policy","model_metadata","prompt_sha256","recorded_by"}, where="dispatch receipt")
    require(d["author_id"] == author and bool(d["agent_id"]) and bool(d["recorded_by"]), "Wrong dispatch identity")
    require(d["fresh_context"] is True and d["fork_turns"] == "none" and d["model_policy"] == "inherit", "Use actual fresh inherited-model collaboration")
    require(set(d["model_metadata"]) == MODEL_FIELDS, "Model metadata fields required; use null for unavailable")
    require(d["prompt_sha256"] == lc.sha256(HERE/"AUTHOR_TASK.md"), "Dispatch prompt binding differs")

def start(author, dispatch_record):
    c, f = config(), check_freeze()
    d = read(dispatch_record); validate_dispatch(d,author)
    root = bundle(author)
    root.mkdir(parents=True, exist_ok=False)
    (root/"host/operations").mkdir(parents=True)
    for name in f["source_packet"]["files"]:
        destination = safe(root,name); destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(safe(f["source_packet"]["path"],name),destination)
    write_new(root/"task.json",c["task"])
    write_new(root/"request.json",{"schema_version":1,"task":c["task"],"purpose":c["purpose"],"analyses":c["analyses"]})
    write_new(root/"registry.json",{"artifacts":f["source_registry"]})
    shutil.copyfile(HERE/"AUTHOR_TASK.md",root/"AUTHOR_TASK.md")
    write_new(root/"input/author_runtime.json",d)
    write_new(root/"input/source_families.json",f["source_families"])
    write_new(root/"host/start.json",{"author_id":author,"freeze_sha256":lc.sha256(FREEZE),"dispatch":d})
    result = native.create_session(root,session_config(c))
    write_new(root/"host/start_result.json",result)
    return {"author_id":author,"bundle":str(root),"session":result}

def _operations(root, allow_pending=False):
    directory = root/"host/operations"
    requests = sorted(directory.glob("*.request.json"))
    require(set(p.name for p in directory.iterdir()) <= {p.name for p in requests}|{p.name.replace(".request.",".result.") for p in requests}, "Unexpected operation file")
    records=[]
    for i,p in enumerate(requests,1):
        r=read(p); require(r["sequence"]==i and p.name.startswith(f"{i:04d}_"),"Operation sequence changed")
        rp=p.with_name(p.name.replace(".request.",".result."))
        require(allow_pending or rp.is_file(),"Interrupted action: stop; do not reset/retry")
        result=read(rp) if rp.is_file() else None
        if result: require(result["request_sha256"]==lc.sha256(p),"Operation request changed")
        records.append({"request":r,"result":result})
    return records

def _native_state(root):
    native.verify_session(root)
    # _load's inventory contract includes the engine's operation lock.
    with native.ledger._operation(root/native.DIRECTORY,"wrapper-read"):
        return native._load(root,root/native.DIRECTORY)

def _verify_operation_bindings(root,state,ops):
    native_ops={r["request"]["action_id"]:r for r in ops if r["request"]["lane"]=="native"}
    require(set(state["actions"])==set(native_ops),"Native action bypassed wrapper")
    for action_id,op in native_ops.items():
        entry=state["actions"][action_id]
        require(entry["action"]==op["request"]["action"],"Native action differs from wrapper reservation")
        require(entry["result"]==op["result"].get("result"),"Native result differs from wrapper receipt")
    source_ops={r["request"]["action"]["replay_id"]:r for r in ops if r["request"]["lane"]=="source_replay"}
    folder=root/source.FOLDER
    if folder.exists():
        require(set(p.name for p in folder.iterdir())<=set(source_ops),"Source execution bypassed wrapper or remains interrupted")
        for p in folder.iterdir():
            request=read(p/"request.json"); action=source_ops[p.name]["request"]["action"]
            require(all(request[k]==action[k] for k in ("candidate","context_id","seed","replay_id")),"Source request differs from wrapper reservation")

def _verify_open(root):
    check_freeze()
    start_record=read(root/"host/start.json")
    require(start_record["freeze_sha256"]==lc.sha256(FREEZE),"Start freeze changed")
    validate_dispatch(start_record["dispatch"],root.name)
    require(start_record["dispatch"]==read(root/"input/author_runtime.json"),"Host dispatch differs from bound author metadata")
    require(not (root/"AUTHOR_SEAL.json").exists(),"Author already sealed")
    ops=_operations(root)
    state=_native_state(root)
    _verify_operation_bindings(root,state,ops)
    return state,ops

def candidate_files(root,candidate):
    candidate=native._candidate(candidate)
    return inventory(safe(root,candidate),exclude=("freeze.json",))

def _review(root, candidate, review):
    r=read(review)
    exact_keys(r,{"kind","author_id","candidate","reviewer_id","status","candidate_files","checks","blocking_findings","source_adequacy","source_families","source_replay_approved"},where="candidate review")
    require(r["kind"]=="pns_bp_candidate_review" and r["author_id"]==root.name and r["candidate"]==candidate,"Wrong review identity")
    require(r["reviewer_id"] and r["reviewer_id"]!=read(root/"host/start.json")["dispatch"]["agent_id"],"Independent reviewer required")
    require(r["status"]=="approved" and r["blocking_findings"]==[],"Unresolved implementation review")
    require(r["checks"]=={k:True for k in REVIEW_CHECKS} and r["source_adequacy"] is True,"Review gates failed")
    require(r["candidate_files"]==candidate_files(root,candidate),"Reviewed candidate bytes changed")
    require(isinstance(r["source_families"],dict) and bool(r["source_families"]),"Group documents by original scientific source")
    known={e["source_id"] for e in read(root/"registry.json")["artifacts"]}
    mapped=[s for ids in r["source_families"].values() for s in ids]
    require(set(mapped)<=known and len(mapped)==len(set(mapped)),"Invalid or overlapping source-family document IDs")
    used={s["id"] for s in read(safe(root,candidate)/"evidence.json")["sources"]}
    require(used<=set(mapped),"Every used document must be grouped by original scientific source")
    plan=safe(root,candidate)/source.PLAN
    require(not plan.exists() or r["source_replay_approved"] is True,"Optional replay requires scientific context review")
    if plan.exists():
        p=read(plan); lim=config()["source_replay_limits"]
        require(p["budget"]["max_evaluations"]<=lim["executions"] and p["budget"]["max_rows_per_evaluation"]<=lim["max_rows_per_evaluation"],"Source replay exceeds separate approved budget")
        source.preflight(root,candidate)
    return r

def _gateway_usage(root):
    p=root/"gateway/session/state.json"
    return read(p)["usage"] if p.exists() else {"queries":0,"downloads":0}

def _source_bytes(root):
    # Count original download responses, excluding metadata/search and derived text.
    p=root/"gateway/session/audit.jsonl"; total=0
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            e=json.loads(line)
            if e.get("type")=="http_attempt" and e.get("budget")=="downloads":
                total += e.get("bytes",16*1024*1024+1)
    p=root/"web_evidence_v1/state.json"
    if p.exists(): total += read(p)["usage"]["response_bytes"]
    return total

def _retrieval_reservation(root, action, ops):
    kind=action["kind"]; ext=sum(x["request"]["lane"]=="external_search" for x in ops)
    queries=_gateway_usage(root)["queries"]+ext
    needs_query=kind=="external_search" or (kind=="literature" and action["action"] in {"search","fetch"})
    require(queries+int(needs_query)<=12,"Combined source-query budget exhausted")
    reserved=0
    if kind=="literature" and action["action"] in {"fetch","fetch-supplement"}: reserved=16*1024*1024+1
    if kind=="web_evidence": reserved=config()["web_evidence"]["response_bytes"]+1
    prior=sum(x["result"].get("conservative_extra_bytes",0) for x in ops)
    require(_source_bytes(root)+prior+reserved<=50*1024*1024,"Insufficient remaining source bytes for safe bounded retrieval")
    return reserved

def _reserve(root, action_id, lane, action, extra):
    native._name(action_id)
    ops=_operations(root)
    require(action_id.casefold() not in {r["request"]["action_id"].casefold() for r in ops},"Wrapper action ID reused")
    p=root/"host/operations"/f"{len(ops)+1:04d}_{action_id}.request.json"
    write_new(p,{"sequence":len(ops)+1,"action_id":action_id,"lane":lane,"action":action,**extra})
    return p

def _stage_complete(state,candidate):
    for seed in config()["seeds"]:
        matches=[e for e in state["actions"].values() if e["action"]["kind"]=="execute" and e["action"]["candidate"]==candidate and e["action"]["seed"]==seed]
        require(len(matches)==1,"Complete every initial seed attempt before revision")
        if matches[0].get("result",{}).get("status")!="success": continue
        run=matches[0]["action"]["run_id"]
        completed=[e["action"] for e in state["actions"].values() if e.get("result",{}).get("status")=="success" and e["action"].get("candidate")==candidate and e["action"].get("run_id")==run]
        require(any(a["kind"]=="feedback" for a in completed),"Initial run lacks strict/descriptive feedback")
        require(any(a["kind"]=="analysis" and a["adapter"]=="generated" for a in completed),"Initial run lacks generated analysis")

def act(author, action_id, action, review=None):
    root=bundle(author)
    with lock(root):
        state,ops=_verify_open(root)
        kind=action.get("kind")
        require(state["status"]=="active","Native session is not active; close failure without repair/retry")
        require(kind!="finish","Use select-seal to close")
        lane="native"; extra={}; reservation=0
        if kind in {"external_search","source_preflight","source_replay"}: lane=kind
        else: action=native._action(action)
        if lane=="external_search":
            exact_keys(action,{"kind","query","tool"},where="external search permit")
            require(bool(action["query"]) and bool(action["tool"]),"Search details required")
            reservation=_retrieval_reservation(root,action,ops)
        elif lane.startswith("source_"):
            expected={"kind","candidate"}|({"replay_id","context_id","seed"} if lane=="source_replay" else set())
            exact_keys(action,expected,where=lane)
            action["candidate"]=native._candidate(action["candidate"])
            require(action["candidate"] in state["candidates"],"Source operations require submitted candidate")
            if lane=="source_replay":
                require(sum(x["request"]["lane"]==lane for x in ops)<6,"Separate source-replay allowance exhausted")
        else:
            if kind=="submit":
                require(review is not None,"Root-controlled independent review receipt required before submit")
                extra["review"]=_review(root,action["candidate"],review)
                if state["candidates"]: _stage_complete(state,state["candidates"][-1])
            if kind in {"literature","web_evidence"}: reservation=_retrieval_reservation(root,action,ops)
            native._reserve_checks(state,action)
        before=_source_bytes(root)
        p=_reserve(root,action_id,lane,action,{**extra,"source_byte_reservation":reservation})
        result={"request_sha256":lc.sha256(p),"conservative_extra_bytes":0}
        try:
            if lane=="native": result["result"]=native.dispatch(root,action_id,action)
            elif lane=="source_preflight": result["result"]=source.preflight(root,action["candidate"])
            elif lane=="source_replay":
                result["result"]=source.run_source_replay(root,action["candidate"],action["replay_id"],action["context_id"],action["seed"],runtime=config()["runtime"],**config()["execution_limits"])
            else: result["result"]={"status":"permit_issued","query":action["query"],"tool":action["tool"],"quantitative_evidence":False}
        except Exception as exc:
            result["error"]={"type":type(exc).__name__,"message":str(exc)}
            raise
        finally:
            delta=max(0,_source_bytes(root)-before)
            failed="error" in result or result.get("result",{}).get("status") in {"error","rejected","failed"}
            if reservation and failed: result["conservative_extra_bytes"]=max(0,reservation-delta)
            write_new(p.with_name(p.name.replace(".request.",".result.")),result)
        return result

def search_receipt(author, action_id, receipt_path):
    root=bundle(author)
    with lock(root):
        _,ops=_verify_open(root)
        op=next((o for o in ops if o["request"]["action_id"]==action_id),None)
        require(op is not None and op["request"]["lane"]=="external_search","No prior search permit")
        r=read(receipt_path)
        exact_keys(r,{"query","tool","status","result_urls","host_tool_call_id","notes"},where="external search receipt")
        require(r["query"]==op["request"]["action"]["query"] and r["tool"]==op["request"]["action"]["tool"],"Search receipt mismatch")
        require(r["status"] in {"completed","failed","not_executed"},"Search receipt status invalid")
        require(isinstance(r["result_urls"],list) and all(isinstance(u,str) for u in r["result_urls"]),"Search URLs must be a list of strings")
        require(r["status"]=="not_executed" or bool(r["host_tool_call_id"]),"Actual host call ID required")
        p=root/"host/search_receipts"/(action_id+".json")
        write_new(p,r)
        return {"path":str(p),"sha256":lc.sha256(p)}

def _all_outputs(root,state,selected):
    rows=[]
    for entry in state["actions"].values():
        a=entry["action"]
        if a["kind"]!="execute": continue
        row={"author_id":root.name,"candidate":a["candidate"],"run_id":a["run_id"],"seed":a["seed"],"status":entry.get("result",{}).get("status","pending"),"selected":a["candidate"]==selected}
        if row["status"]=="success":
            p=root/"executions"/a["run_id"]/"output/generated.csv"
            row.update(path=str(p),sha256=lc.sha256(p))
        rows.append(row)
    return rows

def decision_bindings(author):
    """Hashes the author must acknowledge in a final decision, no reference values."""
    root=bundle(author); state=_native_state(root); feedback={}; analysis={}
    for action_id,entry in state["actions"].items():
        a=entry["action"]
        if entry.get("result",{}).get("status")!="success": continue
        if a["kind"]=="feedback":
            for lane in ("semantic_feedback_v1","descriptive_feedback_v1"):
                name=f"{lane}/{a['feedback_id']}/feedback.json"; feedback[name]=lc.sha256(root/name)
        if a["kind"]=="analysis":
            name=f"{native.DIRECTORY}/results/{action_id}.json"; analysis[name]=lc.sha256(root/name)
    for p in sorted((root/source.FOLDER).glob("*/replay.json")):
        feedback[p.relative_to(root).as_posix()]=lc.sha256(p)
    return {"source_feedback_used":feedback,"generated_analysis_used":analysis}

def select_seal(author, decision_path, review_path):
    root=bundle(author)
    with lock(root):
        state,ops=_verify_open(root)
        d=read(decision_path)
        exact_keys(d,{"author_id","final_candidate","reason","source_feedback_used","generated_analysis_used","optional_source_replay_disposition"},where="final author decision")
        require(d["author_id"]==author and bool(d["reason"]),"Final decision identity/reason required")
        require(bool(d["optional_source_replay_disposition"]),"Explain optional source replay use or non-use")
        for key,value in decision_bindings(author).items():
            require(d[key]==value,"Final decision must acknowledge the complete diagnostic inventory: "+key)
        selected=native._candidate(d["final_candidate"]) if d["final_candidate"] is not None else None
        r=read(review_path)
        exact_keys(r,{"kind","author_id","reviewer_id","decision_sha256","status","blocking_findings","complete_disposition","no_reference_access"},where="final review")
        require(r["kind"]=="pns_bp_final_review" and r["author_id"]==author and r["decision_sha256"]==lc.sha256(decision_path),"Final review decision binding differs")
        require(r["reviewer_id"] and r["reviewer_id"]!=read(root/"host/start.json")["dispatch"]["agent_id"],"Independent final reviewer required")
        require(r["status"]=="approved" and not r["blocking_findings"] and r["complete_disposition"] is True and r["no_reference_access"] is True,"Final review incomplete")
        for op in ops:
            if op["request"]["lane"]=="external_search": require((root/"host/search_receipts"/(op["request"]["action_id"]+".json")).exists(),"External search receipt missing")
        if state["status"]=="active":
            action={"kind":"finish","final_candidate":selected,"reason":d["reason"]}
            # Native finish validates all submitted stages/seeds and diagnostics.
            native._reserve_checks(state,action)
            p=_reserve(root,"final_finish","native",action,{})
            result=native.dispatch(root,"final_finish",action)
            write_new(p.with_name(p.name.replace(".request.",".result.")),{"request_sha256":lc.sha256(p),"result":result,"conservative_extra_bytes":0})
            state=_native_state(root)
        else:
            require(selected is None and state["status"] in {"halted","abandoned"},"Unavailable session may only close as failure")
        for op in ops:
            a=op["request"]["action"]
            if op["request"]["lane"]=="source_replay" and "error" not in op["result"]:
                source.verify_source_replay(root,a["replay_id"],candidate=a["candidate"])
        require((selected is not None)==(state["status"]=="completed"),"Chosen candidate requires completed native finish")
        for name,path in (("final_decision.json",decision_path),("final_review.json",review_path)):
            with (root/"host"/name).open("xb") as f: f.write(Path(path).read_bytes())
        rows=_all_outputs(root,state,selected)
        seal={"kind":"pns_bp_author_seal","author_id":author,"status":state["status"],"final_candidate":selected,
            "all_outputs":rows,"selected_outputs":[x for x in rows if x["selected"] and x["status"]=="success"],
            "scheduled_seeds":config()["seeds"],"native_disposition":native._disposition(state),
            "files":inventory(root),"method_freeze_sha256":lc.sha256(FREEZE)}
        write_new(root/"AUTHOR_SEAL.json",seal)
        return seal

def verify_author_seal(author):
    root=bundle(author); s=read(root/"AUTHOR_SEAL.json")
    check_freeze()
    require(s["author_id"]==author and s["method_freeze_sha256"]==lc.sha256(FREEZE),"Seal identity/freeze changed")
    require(inventory(root,exclude=("AUTHOR_SEAL.json",))==s["files"],"Author sealed artifacts changed")
    state=_native_state(root)
    _verify_operation_bindings(root,state,_operations(root))
    require(s["status"]==state["status"] and s["status"] in {"completed","abandoned","halted"},"Author is not terminal")
    require(s["all_outputs"]==_all_outputs(root,state,s["final_candidate"]),"Output inventory changed")
    require(s["native_disposition"]==native._disposition(state),"Candidate/seed disposition changed")
    require(s["selected_outputs"]==[x for x in s["all_outputs"] if x["selected"] and x["status"]=="success"],"Selected output inventory changed")
    d=read(root/"host/final_decision.json"); r=read(root/"host/final_review.json")
    require(r["decision_sha256"]==lc.sha256(root/"host/final_decision.json"),"Final review/decision bytes differ")
    selected=native._candidate(d["final_candidate"]) if d["final_candidate"] is not None else None
    require(selected==s["final_candidate"],"Author choice differs from seal")
    finishes=[e["action"] for e in state["actions"].values() if e["action"]["kind"]=="finish"]
    if finishes: require(finishes[-1]["final_candidate"]==selected,"Seal differs from native final choice")
    require((selected is not None)==(state["status"]=="completed"),"Selected candidate/terminal disposition differs")
    return s

def batch_seal():
    check_freeze(); c=config()
    require(set(p.name for p in SESSIONS.iterdir())==set(c["author_ids"]),"Exactly the five fixed author slots must exist")
    seals={a:verify_author_seal(a) for a in c["author_ids"]}
    value={"kind":"pns_bp_batch_seal","method_freeze_sha256":lc.sha256(FREEZE),
        "author_seals":{a:lc.sha256(bundle(a)/"AUTHOR_SEAL.json") for a in c["author_ids"]},
        "author_outcomes":[_author_outcome(a,s) for a,s in seals.items()],
        "selected_outputs":[row for s in seals.values() for row in s["selected_outputs"]],
        "all_attempted_output_count":sum(len(s["all_outputs"]) for s in seals.values())}
    require(len(value["selected_outputs"])<=15 and value["all_attempted_output_count"]<=30,"Batch allocation exceeded")
    write_new(HERE/"BATCH_SEAL.json",value)
    return verify_batch_seal()

def _author_outcome(author,seal):
    return {"author_id":author,"status":seal["status"],"final_candidate":seal["final_candidate"],
        "selected_output_count":len(seal["selected_outputs"]),"native_disposition":seal["native_disposition"],"all_outputs":seal["all_outputs"]}

def verify_batch_seal():
    """Required before clinical analysis/reveal; separate counts-only readiness is prior."""
    check_freeze(); c=config(); p=HERE/"BATCH_SEAL.json"; b=read(p)
    require(b["method_freeze_sha256"]==lc.sha256(FREEZE),"Batch method freeze changed")
    require(set(b["author_seals"])==set(c["author_ids"]),"Batch lacks all five fixed slots")
    require(set(x.name for x in SESSIONS.iterdir())==set(c["author_ids"]),"Extra/missing author directory")
    seals={a:verify_author_seal(a) for a in c["author_ids"]}
    require(b["author_seals"]=={a:lc.sha256(bundle(a)/"AUTHOR_SEAL.json") for a in c["author_ids"]},"Author seal changed")
    outputs=[row for s in seals.values() for row in s["selected_outputs"]]
    outcomes=[_author_outcome(a,s) for a,s in seals.items()]
    require(b["selected_outputs"]==outputs and b["author_outcomes"]==outcomes,"Batch output/disposition changed")
    require(b["all_attempted_output_count"]==sum(len(s["all_outputs"]) for s in seals.values()),"Attempt count changed")
    require(len(outputs)<=15 and b["all_attempted_output_count"]<=30,"Batch allocation exceeded")
    return {**b,"batch_seal_path":str(p),"batch_seal_sha256":lc.sha256(p)}

def status(author):
    root=bundle(author)
    if (root/"AUTHOR_SEAL.json").exists(): return verify_author_seal(author)
    with lock(root):
        state,ops=_verify_open(root)
        return {"author_id":author,"native":native._summary(state),"operations":len(ops),"new_source_bytes":_source_bytes(root),"source_replay_attempts":sum(o["request"]["lane"]=="source_replay" for o in ops)}
