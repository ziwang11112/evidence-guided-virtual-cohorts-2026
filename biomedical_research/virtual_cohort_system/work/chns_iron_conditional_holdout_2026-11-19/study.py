"""Prospectively sealed source-only execution for the matched conditional-evidence pilot."""
import argparse
import hashlib
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from partition import PRIVATE, PROJECT, ROOT, digest, read, save
from science import HB, FE, SEEDS, check, measures

PRIOR = PROJECT / "work/evidence_composition_pilot_2026-11-16"
sys.path.insert(0, str(PRIOR))
import pilot as sandbox
from preflight import tests, sandbox_check

client = sandbox.client
client.MAX_OUTPUT = 16384
client.CAPS = {"openai": 8.0}
MODEL = "OA_SOL"
PARENTS = ["ordinary1","workflow1","workflow2","ordinary2","ordinary3","workflow3"]
BRANCHES = ["control","evidence"]
SOURCE = PROJECT/"work/original_paper_capability_2026-11-17/private_sources/iron_original.layout.txt"
SKILL = PROJECT/"skills/evidence-cohort-generation/SKILL.md"
CALLROOT = PRIVATE/"api"
PUBLIC_LAWS = ROOT/"laws"
N = 12000


def now():
    return datetime.now(timezone.utc).isoformat()


def lf(p):
    return hashlib.sha256(p.read_bytes().replace(b"\r\n",b"\n")).hexdigest()


def task(n=N):
    t={"schema_version":1,"task_id":"chns_iron_conditional_holdout","mode":"whole_cohort",
       "population":"CHNS 2009 women age 18–49 with paired central Hb and uncorrected ferritin",
       "row_id":"row_id","n_rows":n,
       "columns":[{"name":"row_id","kind":"integer","unit":"","role":"identifier","nullable":False},
                  {"name":HB,"kind":"number","unit":"g/dL","role":"generated","nullable":False},
                  {"name":FE,"kind":"number","unit":"ug/L","role":"generated","nullable":False}],
       "information_policy":{"mode":"published_evidence","excluded_cohorts":[],"allowed_tools":[]},
       "budget":{"source_queries":0,"source_downloads":0,"revisions":1}}
    sandbox.contracts.validate_task(t)
    return t


def bound_files():
    local=["PROTOCOL.md","REQUEST.txt","partition.py","science.py","preflight.py","study.py","evaluate.py","verify.py",
           "ADMISSION.json","PARTITION.json","A_TABLES.json","A_SUPPLEMENT.json","PREFLIGHT.json"]
    common=[SKILL,PRIOR/"pilot.py",PROJECT/"cohort_harness/_worker.py",PROJECT/"cohort_harness/contracts.py",
            PROJECT/"cohort_harness/execution.py",PROJECT/"cohort_harness/lifecycle.py",
            PROJECT/"work/cross_model_api_pilot_2026-11-10/provider_preflight.py",
            PROJECT/"work/cross_model_api_pilot_2026-11-10/provider_client.py"]
    return {p.relative_to(PROJECT).as_posix():lf(p) for p in [*[ROOT/s for s in local],*common]}


def original(parent):
    chunks=[(ROOT/"REQUEST.txt").read_text(encoding="utf8")]
    if parent.startswith("workflow"):
        chunks+=["Scientific workflow guidance. In this experiment the controller supplies the A-only tables, frozen execution and source feedback. CLI calls and literature retrieval are unavailable.", SKILL.read_text(encoding="utf8")]
    chunks+=["Original external publication (Zhu et al.). Its Hebei sample is separate from CHNS.", SOURCE.read_text(encoding="utf8"),
             "Within-study evidence tables (CHNS evidence communities only):", (ROOT/"A_TABLES.json").read_text(encoding="utf8")]
    return "\n\n".join(chunks)


def freeze():
    check(not (ROOT/"FREEZE.json").exists(),"Study already frozen")
    checks=tests()
    trial=sandbox_check(sandbox,task(32),PRIVATE)
    save(ROOT/"PREFLIGHT.json",{"checks":checks,"isolated_fixture_sha256":trial,"B_read":False})
    prefixes={p:hashlib.sha256(original(p).encode()).hexdigest() for p in PARENTS}
    check(len(set(prefixes.values()))==2,"Parent request mismatch within arm")
    part=read(ROOT/"PARTITION.json")
    for arm in ("A","B"):
        check(digest(PRIVATE/(arm+".csv"))==part["parts"][arm]["sha256"],"Partition digest mismatch")
    save(ROOT/"FREEZE.json",{"utc":now(),"bound_files_lf_sha256":bound_files(),"article_layout_sha256":digest(SOURCE),
         "parent_prefix_sha256":prefixes,"parents":PARENTS,"siblings":BRANCHES,"seeds":SEEDS,
         "model":client.CONFIGS[MODEL],"max_calls":18,"max_output_tokens":client.MAX_OUTPUT,"cap_usd":8.,
         "task":task(),"limits":sandbox.LIMITS,"B_effects_computed":False})
    print("Protocol, evidence, scorer and six primary sessions frozen.",flush=True)


def verify_freeze():
    f=read(ROOT/"FREEZE.json")
    check(f["bound_files_lf_sha256"]==bound_files() and digest(SOURCE)==f["article_layout_sha256"],"Frozen inputs changed")
    check(f["parents"]==PARENTS and f["seeds"]==SEEDS and f["task"]==task(),"Frozen design changed")
    check(f["model"]==client.CONFIGS[MODEL] and f["max_output_tokens"]==client.MAX_OUTPUT and f["cap_usd"]==client.CAPS["openai"],"Provider drift")
    return f


def request(cid):
    parent,_,branch=cid.partition("_")
    prompt=original(parent)
    if not branch:
        return prompt+"\n\nSubmit the initial primary law."
    record=read(ROOT/"PARENTS.json")["parents"][parent]
    check(record["usable"],"Unavailable primary")
    obj_path=CALLROOT/"calls"/parent/"artifact.json"
    check(digest(obj_path)==record["artifact_sha256"],"Primary changed")
    prompt+="\n\nPreviously sealed submission:\n"+obj_path.read_text(encoding="utf8")
    prompt+="\n\nGenerated-only check against original A tables (virtual values and A values, no held-out estimates):\n"+json.dumps(record["feedback"])
    if branch=="evidence":
        prompt+="\n\nAdditional evidence available:\n"+(ROOT/"A_SUPPLEMENT.json").read_text(encoding="utf8")
    else:
        check(branch=="control","Unknown branch")
        prompt+="\n\nNo additional source statistic is available in this round."
    return prompt+"\n\nReview your model using the available information. Retain or revise once. Return one complete primary artifact following the same interface."


def get_call(cid):
    folder=CALLROOT/"calls"/cid
    if folder.exists():
        check((folder/"receipt.json").is_file(),"Existing unresolved dispatch: "+cid)
        return read(folder/"receipt.json")
    rec,_=client.call_once(CALLROOT,cid,MODEL,request(cid))
    return rec


def materialize(cid, obj, receipt):
    folder=PUBLIC_LAWS/cid
    folder.mkdir(parents=True,exist_ok=True)
    task_spec={"task":task(),"model":obj["model_spec"]}
    for name,value in (("generator.py",obj["generator_py"]),("model_spec.json",json.dumps(task_spec,ensure_ascii=False,indent=2)),
                       ("decision.json",json.dumps(obj["decision_record"],ensure_ascii=False,indent=2))):
        dest=folder/name
        if not dest.exists():
            with dest.open("x",encoding="utf8",newline="\n") as f: f.write(value)
        check(dest.read_text(encoding="utf8")==value,"Modified sealed material "+cid)
    seals={name:lf(folder/name) for name in ["generator.py","model_spec.json","decision.json"]}
    if not (folder/"SEAL.json").exists():
        save(folder/"SEAL.json",{"utc":now(),"scientific_files":seals,"artifact_sha256":receipt["artifact.json_sha256"]})
    check(read(folder/"SEAL.json")["scientific_files"]==seals,"Science seal changed")
    return folder


def diagnostic(s):
    t=read(ROOT/"A_TABLES.json")
    base=[j for row in t["table_1"]["counts"] for j in row]
    entries=[{"label":"threshold_cell_fraction_"+str(i+1),"observed_A":j/sum(base),"virtual":s["cells"][i]/s["n"]} for i,j in enumerate(base)]
    for i,(a,v) in enumerate(zip(t["table_2"]["rows"],s["groups"])):
        for key in ["fraction","depletion_fraction","hb_mean","hb_sd","ferritin_gm","ferritin_gsd"]:
            target=a["n"]/sum(base) if key=="fraction" else a["depleted"]/a["n"] if key=="depletion_fraction" else a[key]
            entries.append(dict(label=f"band_{i+1}_{key}",observed_A=target,virtual=v[key]))
    return entries


def calculate(cid):
    rec=get_call(cid)
    print(cid,rec.get("status"),rec.get("artifact_status"),rec.get("tariff_cost_usd"),flush=True)
    details={k:rec.get(k) for k in ("status","artifact_status","requested_model","returned_model","usage","tariff_cost_usd",
             "started_utc","ended_utc","prompt_sha256","request_sha256","response_text.txt_sha256","mechanical_error","error_type","api_error_code")}
    result={"id":cid,"usable":False,"receipt":details,"runs":[]}
    if rec.get("status")!="received" or rec.get("returned_model")!=client.CONFIGS[MODEL]["model"] or not rec.get("artifact.json_sha256"):
        return result
    art=CALLROOT/"calls"/cid/"artifact.json"
    check(digest(art)==rec["artifact.json_sha256"],"API output digest mismatch")
    result["artifact_sha256"]=digest(art)
    folder=materialize(cid,read(art),rec)
    frames=[]
    for seed in SEEDS:
        dest=PRIVATE/"runs"/cid/str(seed)
        if dest.exists(): check((dest/"execution.json").exists(),"Unclosed worker "+cid)
        run=read(dest/"execution.json") if dest.exists() else sandbox.isolated(folder,task(),dest,seed)
        result["runs"].append({"seed":seed,"status":run["status"],"hash":run.get("generated_sha256"),"error":run.get("error")})
        if run["status"]=="success":
            f=dest/"output/generated.csv"
            check(digest(f)==run["generated_sha256"],"Stale generator output")
            frames.append(pd.read_csv(f))
    if len(frames)!=len(SEEDS): return result
    try:
        combined=measures(pd.concat(frames,ignore_index=True))
        check(combined["rank"] is not None,"Constant rank in virtual data")
        result.update(usable=True,metrics=combined,feedback=diagnostic(combined))
    except (ValueError,FloatingPointError) as e:
        result["scientific_error"]=str(e)
    return result


def execute(which):
    verify_freeze()
    check(not (ROOT/"REFERENCE_OPEN.json").exists(),"Reference already opened")
    filename=ROOT/("PARENTS.json" if which=="parents" else "SOURCE_CLOSURE.json")
    check(not filename.exists(),"Stage already closed")
    lock=ROOT/"dispatch.lock"
    with lock.open("x") as f: f.write(str(os.getpid()))
    try:
        if which=="parents":
            with ThreadPoolExecutor(max_workers=3) as pool: rows=list(pool.map(calculate,PARENTS))
            save(filename,{"utc":now(),"parents":{s["id"]:s for s in rows},"freeze_lf_sha256":lf(ROOT/"FREEZE.json")})
        else:
            parents=read(ROOT/"PARENTS.json")["parents"]
            ids=[p+"_"+b for i,p in enumerate(PARENTS) if parents[p]["usable"] for b in (BRANCHES if i%2==0 else BRANCHES[::-1])]
            with ThreadPoolExecutor(max_workers=3) as pool: rows=list(pool.map(calculate,ids))
            records={s["id"]:s for s in rows}
            for p in PARENTS:
                for b in BRANCHES:
                    cid=p+"_"+b
                    if cid not in records: records[cid]={"id":cid,"usable":False,"reason":"initial law unavailable","runs":[]}
            models={**parents,**records}
            save(filename,{"utc":now(),"freeze_lf_sha256":lf(ROOT/"FREEZE.json"),"parent_closure_lf_sha256":lf(ROOT/"PARENTS.json"),
                 "models":models,"api_calls":sum("receipt" in v for v in models.values()),
                 "known_usd":sum((v.get("receipt",{}).get("tariff_cost_usd") or 0) for v in models.values()),
                 "B_effects_computed":False})
    finally:
        lock.unlink()


if __name__=="__main__":
    command=argparse.ArgumentParser()
    command.add_argument("stage",choices=["freeze","parents","siblings"])
    stage=command.parse_args().stage
    if stage=="freeze": freeze()
    else: execute(stage)
