"""Run a prospective article-reading study. Only reveal opens measured reference columns."""
import argparse
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
import shutil
import os
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
PRIOR=PROJECT/"work/evidence_composition_pilot_2026-11-16"
sys.path.insert(0,str(PRIOR))
import pilot as sandbox
sys.path.remove(str(PRIOR))
import scoring

client=sandbox.client
client.MAX_OUTPUT=12288
client.CAPS={"openai":5.00}
CFG="OA_SOL"
SOURCE=PROJECT/"work/original_paper_capability_2026-11-17/private_sources/iron_original.layout.txt"
PRIVATE=ROOT/"private_runs"
CALLS=ROOT/"private_calls"
OBS=ROOT/"private_reference/bio.dta"
PRIMARY=["P1","P2","P3"]
BRANCHES=["ordinary","directed"]
IDS=PRIMARY+[p+"_"+b for p in PRIMARY for b in BRANCHES]+["statistical"]
BRANCH_TEXT={
    "ordinary":"Construct a second scientifically defensible joint law based on the same publication and request, alongside the sealed primary.",
    "directed":"Construct a second scientifically defensible joint law based on the same publication and request that exposes sensitivity of a requested analysis to a source-compatible modeling choice."}
N=20000
read, write, sha = sandbox.read,sandbox.write,sandbox.sha


def check(condition, reason):
    if not condition: raise ValueError(reason)


def lfsha(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n",b"\n")).hexdigest()


def task(n=N):
    cols=[{"name":"row_id","kind":"integer","unit":"","role":"identifier","nullable":False}]
    cols.extend({"name":k,"kind":"number","unit":u,"role":"generated","nullable":False}
                for k,u in [("hb_g_dl","g/dL"),("ferritin_ug_l","ug/L")])
    t={"schema_version":1,"task_id":"iron_original_alternative_laws","mode":"whole_cohort","population":"Rural Sanguié and Sourou nonpregnant nonlactating mothers age 18–49","row_id":"row_id","n_rows":n,"columns":cols,
       "information_policy":{"mode":"published_evidence","excluded_cohorts":[],"allowed_tools":[]},
       "budget":{"source_queries":0,"source_downloads":0,"revisions":0}}
    sandbox.contracts.validate_task(t)
    return t


def seeds(cid):
    return [191201+100*IDS.index(cid)+i for i in (1,3,9)]


def binding():
    local=["study.py","scoring.py","neutral.py","verify.py","REQUEST.txt","PLAN.md","ADMISSION_RULE.json","PREFLIGHT.json"]
    paths=[ROOT/f for f in local]+[PRIOR/"pilot.py",PROJECT/"cohort_harness/_worker.py",PROJECT/"cohort_harness/contracts.py",
      PROJECT/"cohort_harness/execution.py",PROJECT/"cohort_harness/lifecycle.py",
      PROJECT/"work/cross_model_api_pilot_2026-11-10/provider_client.py",PROJECT/"work/cross_model_api_pilot_2026-11-10/provider_preflight.py"]
    return {p.relative_to(PROJECT).as_posix():lfsha(p) for p in paths}


def freeze():
    check(read(ROOT/"PREFLIGHT.json")["passed"], "Preflight failed")
    count,c=9,client.CONFIGS[CFG]
    max_per=((190000+4096)*max(c["cache_write_rate"],c["input_rate"])+client.MAX_OUTPUT*c["output_rate"])/1e6
    # The single-call service ceiling also applies to a branch with a long parent artifact.
    # The ledger enforces the lower global bound across outstanding reservations.
    write(ROOT/"FREEZE.json",{"frozen_utc":sandbox.now(),"files_lf_sha256":binding(),"article_layout_sha256":sha(SOURCE),
         "reference_file_sha256":sha(OBS),"reference_read":"eligibility/schema only; no measurement values inspected",
         "primary":PRIMARY,"branches":BRANCHES,"task":task(),"seeds":{x:seeds(x) for x in IDS},
         "api":c,"max_output_tokens":client.MAX_OUTPUT,"max_calls":count,"budget_usd":client.CAPS["openai"],
         "maximum_single_reservation_usd":max_per,"execution_limits":sandbox.LIMITS,"reference_doi":"10.7910/DVN/5CXCLX"})


def bound():
    f=read(ROOT/"FREEZE.json")
    check(f["files_lf_sha256"]==binding() and f["article_layout_sha256"]==sha(SOURCE) and f["reference_file_sha256"]==sha(OBS),"Frozen input mismatch")
    check(f["api"]==client.CONFIGS[CFG] and f["task"]==task() and f["seeds"]=={x:seeds(x) for x in IDS},"Dispatch mismatch")


def prompt(cid):
    base=(ROOT/"REQUEST.txt").read_text(encoding="utf8")+"\n\nORIGINAL PUBLICATION\n"+SOURCE.read_text(encoding="utf8")
    if cid in PRIMARY: return base+"\n\nWrite your primary generator."
    p,b=cid.split("_")
    parent=read(CALLS/"calls"/p/"artifact.json")
    check(lfsha(CALLS/"calls"/p/"artifact.json")==read(ROOT/"PARENT_CLOSURE.json")["sealed"][p]["artifact_lf_sha256"],"Parent mutation")
    return base+"\n\nSEALED PRIMARY ARTIFACT\n"+json.dumps(parent,ensure_ascii=False)+"\n\n"+BRANCH_TEXT[b]+" Retain applicable source constraints, document choices and the prospective sensitivity judgments, and return one new executable artifact."


def author(cid):
    call=CALLS/"calls"/cid
    if call.exists():
        check((call/"receipt.json").is_file(),"Existing unresolved request; no repeat")
        rec=read(call/"receipt.json")
    else:
        rec,_=client.call_once(CALLS,cid,CFG,prompt(cid))
    row={k:rec.get(k) for k in ["status","requested_model","returned_model","usage","tariff_cost_usd","prompt_sha256","request_sha256","response_text.txt_sha256","artifact_status","mechanical_error","api_error_code","error_type","started_utc","ended_utc"]}
    ok=rec.get("status")=="received" and rec.get("returned_model")==client.CONFIGS[CFG]["model"] and (call/"artifact.json").is_file()
    row["sealed"]=ok
    if ok: row["artifact_lf_sha256"]=lfsha(call/"artifact.json")
    print(cid,rec.get("status"),rec.get("artifact_status"),rec.get("tariff_cost_usd"),flush=True)
    return cid,row


def construct():
    bound()
    check(not (ROOT/"CLOSURE.json").exists(),"Construction closed")
    lock=ROOT/"dispatch.lock"
    with lock.open("x") as f: f.write(str(os.getpid()))
    try:
        if not (ROOT/"PARENT_CLOSURE.json").exists():
            with ThreadPoolExecutor(3) as pool: allp=dict(pool.map(author,PRIMARY))
            write(ROOT/"PARENT_CLOSURE.json",{"time_utc":sandbox.now(),"all":allp,"sealed":{k:v for k,v in allp.items() if v["sealed"]}})
        parents=read(ROOT/"PARENT_CLOSURE.json")
        ids=[p+"_"+b for p in parents["sealed"] for b in BRANCHES]
        with ThreadPoolExecutor(3) as pool: others=dict(pool.map(author,ids))
        for p in PRIMARY:
            if p not in parents["sealed"]:
                for b in BRANCHES: others[p+"_"+b]={"status":"parent_failed","sealed":False,"tariff_cost_usd":None}
        write(ROOT/"CLOSURE.json",{"time_utc":sandbox.now(),"freeze_lf_sha256":lfsha(ROOT/"FREEZE.json"),
              "all":{**parents["all"],**others},"target_effects_opened":False})
    finally:
        lock.unlink()


def stage(cid):
    folder=PRIVATE/"candidates"/cid
    folder.mkdir(parents=True,exist_ok=True)
    if cid=="statistical":
        code=(ROOT/"neutral.py").read_text(encoding="utf8"); model={}
    else:
        art=CALLS/"calls"/cid/"artifact.json"
        check(lfsha(art)==read(ROOT/"CLOSURE.json")["all"][cid]["artifact_lf_sha256"],"Sealed artifact mismatch")
        obj=read(art); code=obj["generator_py"]; model=obj["model_spec"]
    for name,data in (("generator.py",code),("model_spec.json",json.dumps({"task":task(),"model":model},ensure_ascii=False,indent=2))):
        path=folder/name
        if not path.exists(): path.write_text(data,encoding="utf8",newline="\n")
        check(path.read_text(encoding="utf8")==data,"Candidate stage mismatch")
    return folder


def draw():
    bound(); closed=read(ROOT/"CLOSURE.json"); check(not (ROOT/"REVEAL.json").exists(),"Reference already opened")
    ids=[k for k in IDS if k=="statistical" or closed["all"][k]["sealed"]]
    def one(cid):
        folder=stage(cid); results=[]
        for seed in seeds(cid):
            dest=PRIVATE/"runs"/cid/str(seed)
            if dest.exists(): check((dest/"execution.json").is_file(),"Unclosed existing worker")
            res=read(dest/"execution.json") if dest.exists() else sandbox.isolated(folder,task(),dest,seed)
            results.append({"seed":seed,"status":res["status"],"sha256":res.get("generated_sha256"),"error":res.get("error")})
        return cid,results
    with ThreadPoolExecutor(2) as pool: runs=dict(pool.map(one,ids))
    write(ROOT/"DRAW_CLOSURE.json",{"time_utc":sandbox.now(),"closure_lf_sha256":lfsha(ROOT/"CLOSURE.json"),"runs":runs,"target_effects_opened":False})


def rows(cid):
    out=[]
    for row in read(ROOT/"DRAW_CLOSURE.json")["runs"][cid]:
        if row["status"]!="success": return None
        path=PRIVATE/"runs"/cid/str(row["seed"])/"output/generated.csv"
        check(sha(path)==row["sha256"],"Generated table hash mismatch")
        out.append(pd.read_csv(path))
    return pd.concat(out,ignore_index=True)


def score():
    bound(); closure=read(ROOT/"CLOSURE.json")
    laws={}
    for cid in read(ROOT/"DRAW_CLOSURE.json")["runs"]:
        frame=rows(cid)
        laws[cid]=scoring.assess(frame) if frame is not None else {"tier1":False,"tier2":False,"execution":"incomplete"}
        if cid!="statistical":
            decision=read(CALLS/"calls"/cid/"artifact.json")["decision_record"]
            laws[cid]["forecast"]=[{k:row.get(k) for k in ["name","source_status","sensitivity","transfer"]} for row in decision.get("requested_estimands",[]) if isinstance(row,dict)]
            laws[cid]["extracted_cells"]=decision.get("source_cells")
    comparisons=[]
    for p in PRIMARY:
        for b in BRANCHES:
            child=p+"_"+b; a= laws.get(p,{}); z=laws.get(child,{})
            row={"primary":p,"branch":b,"both_tier2":bool(a.get("tier2") and z.get("tier2"))}
            if "spearman" in a and "spearman" in z:
                gap=abs(a["spearman"]-z["spearman"]); margin=1.96*np.hypot(a["rank_mcse"],z["rank_mcse"])
                row.update(rank_gap=gap,mc_margin=margin,mc_lower=max(0.,gap-margin))
            comparisons.append(row)
    write(ROOT/"SOURCE_RESULTS.json",{"time_utc":sandbox.now(),"laws":laws,"pairs":comparisons,
         "calls":len([r for r in closure["all"].values() if r["status"]!="parent_failed"]),
         "known_tariff_cost_usd":sum(r.get("tariff_cost_usd") or 0 for r in closure["all"].values())})


def reveal():
    bound(); check((ROOT/"SOURCE_RESULTS.json").exists(),"Finish all source comparisons first")
    write(ROOT/"REFERENCE_OPEN.json",{"time_utc":sandbox.now(),"draw_closure_lf_sha256":lfsha(ROOT/"DRAW_CLOSURE.json"),"source_results_lf_sha256":lfsha(ROOT/"SOURCE_RESULTS.json")})
    frame=pd.read_stata(OBS,convert_categoricals=False)
    result=scoring.reference_from(frame)
    write(ROOT/"REVEAL.json",{"time_utc":sandbox.now(),"result":result,"input_sha256":sha(OBS)})


def preflight():
    import verify
    verify.fixtures()
    import neutral
    fixture=neutral.generate(None,{"task":{"n_rows":60000}},812)
    check(scoring.assess(fixture)["tier2"],"Statistical law fails its fixed source tests")
    c=PRIVATE/"fixture"; c.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(ROOT/"neutral.py",c/"generator.py")
    write(c/"model_spec.json",{"task":task(25),"model":{}})
    status=sandbox.isolated(c,task(25),PRIVATE/"fixture_execution",123)
    check(status["status"]=="success",str(status.get("error")))
    write(ROOT/"PREFLIGHT.json",{"time_utc":sandbox.now(),"passed":True,"checks":["strict equality boundaries, unequal weights and ties, empty cell, independent scientific estimators","fixed comparator selected source checks on simulated rows","offline isolated row contract"],"target_outcomes_read":False})


if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("command",choices=["preflight","freeze","construct","draw","score","reveal"])
    globals()[ap.parse_args().command]()
