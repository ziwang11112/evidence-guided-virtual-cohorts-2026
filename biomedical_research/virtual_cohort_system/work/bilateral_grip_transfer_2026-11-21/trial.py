"""Write the design seal, collect eight source-only pairing programs and freeze their predictions."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from science import HERE, ROOT, PRIVATE, CELLS, N, SEEDS, canonical, independent, named, read, rule_permutation, score_order, seal, sha, source_grids

PILOT = ROOT/"work/evidence_composition_pilot_2026-11-16"
sys.path.insert(0,str(PILOT))
import pilot as harness

client = harness.client
CONFIG = "OA_SOL"
client.CONFIGS[CONFIG] = {**client.CONFIGS[CONFIG],"effort":"medium"}
client.MAX_OUTPUT = 6000
client.CAPS = {"openai":1.20}
SLOTS = tuple(k+str(i) for k in ("M","J") for i in range(1,5))


def now():
    return datetime.now(timezone.utc).isoformat()


def bindings():
    paths = [HERE/x for x in ("ADMISSION.md","PROTOCOL.md","REQUEST.txt","AU_SOURCE.json","JOINT_SOURCE.json",
                               "science.py","trial.py","reference.py","evaluate.py","fixtures.py")]
    paths += [PILOT/"pilot.py",ROOT/"cohort_harness/_worker.py",ROOT/"cohort_harness/execution.py",
              ROOT/"cohort_harness/contracts.py",ROOT/"work/cross_model_api_pilot_2026-11-10/provider_client.py",
              ROOT/"work/cross_model_api_pilot_2026-11-10/provider_preflight.py"]
    return {f.relative_to(ROOT).as_posix():canonical(f) for f in paths}


def prompt(arm):
    paths=[HERE/"REQUEST.txt",HERE/"AU_SOURCE.json"]
    if arm=="J":
        paths.append(HERE/"JOINT_SOURCE.json")
    return "\n\n".join(p.read_text(encoding="utf-8") for p in paths)


def task(n):
    t={"schema_version":1,"task_id":"bilateral_grip_pairing","mode":"whole_cohort",
       "population":"Community adults aged 50 to 69, four equally weighted sex-by-decade cells",
       "row_id":"row_id","n_rows":n,"columns":[
           {"name":"row_id","kind":"integer","unit":"","role":"identifier","nullable":False},
           {"name":"left_index","kind":"integer","unit":"cell-specific rank index","role":"generated","nullable":False}],
       "information_policy":{"mode":"published_evidence","excluded_cohorts":[],"allowed_tools":[]},
       "budget":{"source_queries":0,"source_downloads":0,"revisions":0}}
    harness.contracts.validate_task(t)
    return t


def run_code(slot,code,model,groups,seed):
    work=PRIVATE/"runs"/slot/str(seed)
    work.mkdir(parents=True,exist_ok=True)
    stage=work/"submission"
    stage.mkdir(exist_ok=True)
    entry=stage/"generator.py"
    if not entry.exists():
        with entry.open("x",encoding="utf-8",newline="\n") as f:f.write(code)
    assert entry.read_text(encoding="utf-8")==code
    t=task(sum(len(r) for _,r,_ in groups))
    seal(stage/"model_spec.json",{"task":t,"model":model,
         "groups":[{"cell":k,"right":r.tolist(),"left":l.tolist()} for k,r,l in groups]})
    run=work/"isolated"
    receipt=read(run/"execution.json") if (run/"execution.json").exists() else harness.isolated(stage,t,run,seed)
    if receipt["status"]!="success":
        info=run/"output/worker_report.json"
        detail=read(info).get("error","") if info.is_file() and info.stat().st_size else receipt.get("error","")
        raise ValueError("Worker: "+str(detail)[:430])
    csv=run/"output/generated.csv"
    assert receipt["generated_sha256"]==sha(csv) and canonical(entry)==canonical(run/"input/generator.py")
    frame=pd.read_csv(csv)
    assert list(frame)==["row_id","left_index"] and np.array_equal(frame.row_id,np.arange(len(frame)))
    left=frame.left_index.to_numpy()
    assert left.dtype.kind in "iu"
    perm=np.stack(np.split(left,len(groups)))
    for (key,r,_),a in zip(groups,perm,strict=True):
        assert np.array_equal(np.sort(a),np.arange(len(r))),key
    dest=work/"perm.npy"
    if dest.exists():
        assert np.array_equal(np.load(dest,allow_pickle=False),perm)
    else:
        np.save(dest,perm,allow_pickle=False)
    return perm,{"seed":seed,"permutation_sha256":sha(dest),"csv_sha256":sha(csv)}


def freeze():
    from fixtures import check
    if (HERE/"FREEZE.json").exists():raise FileExistsError("Design already closed")
    check()
    code=("import numpy as np\nimport pandas as pd\n"
          "def generate(observed,spec,seed):\n"
          "    left=np.concatenate([np.arange(len(g['left'])) for g in spec['groups']])\n"
          "    return pd.DataFrame({'row_id':np.arange(len(left)),'left_index':left})\n")
    _,test=run_code("fixture",code,{},source_grids(59),17)
    config=client.CONFIGS[CONFIG]
    allowances={}
    for k in ("M","J"):
        payload=json.dumps(client.make_request(CONFIG,prompt(k))[1],ensure_ascii=False).encode()
        allowances[k]=((len(payload)+4096)*max(config["input_rate"],config["cache_write_rate"])+client.MAX_OUTPUT*config["output_rate"])/1e6
    assert 4*sum(allowances.values())<=client.CAPS["openai"]
    order=np.random.default_rng(52191).permutation(SLOTS).tolist()
    seal(HERE/"FREEZE.json",{"utc":now(),"bindings":bindings(),"config":config,"system":client.SYSTEM,
         "dispatch_order":order,"source_seed":52191,"execution_seeds":SEEDS,"cells":CELLS,"n_per_cell":N,
         "per_call_upper_usd":allowances,"cap_usd":client.CAPS["openai"],"max_output":client.MAX_OUTPUT,
         "fixture":test,"joint_target_measurements_open":False})


def guard():
    f=read(HERE/"FREEZE.json")
    assert f["bindings"]==bindings() and f["system"]==client.SYSTEM and f["config"]==client.CONFIGS[CONFIG]
    assert f["cap_usd"]==client.CAPS["openai"] and f["max_output"]==client.MAX_OUTPUT
    return f


def dispatch_one(slot):
    folder=PRIVATE/"api/calls"/slot
    if folder.exists() and not (folder/"receipt.json").exists():
        raise RuntimeError("Existing unresolved API reservation: "+slot)
    rec=read(folder/"receipt.json") if folder.exists() else client.call_once(PRIVATE/"api",slot,CONFIG,prompt(slot[0]))[0]
    info={k:rec.get(k) for k in ("status","artifact_status","returned_model","requested_model","usage","tariff_cost_usd",
                                 "request_sha256","response_text.txt_sha256","mechanical_error","started_utc","ended_utc","stop_reason")}
    if rec.get("returned_model")==client.CONFIGS[CONFIG]["model"] and (folder/"artifact.json").exists():
        assert sha(folder/"artifact.json")==rec["artifact.json_sha256"]
        obj=read(folder/"artifact.json")
        out=HERE/"laws"/slot
        out.mkdir(parents=True,exist_ok=True)
        file=out/"generator.py"
        if not file.exists():
            with file.open("x",encoding="utf-8",newline="\n") as f:f.write(obj["generator_py"])
        assert file.read_text(encoding="utf-8")==obj["generator_py"]
        seal(out/"model.json",obj["model_spec"])
        seal(out/"decision.json",obj["decision_record"])
        info["law"]={k:canonical(out/k) for k in ("generator.py","model.json","decision.json")}
    print(slot,info["artifact_status"],info["tariff_cost_usd"],flush=True)
    return slot,info


def dispatch():
    f=guard()
    if (HERE/"REFERENCE_OPEN.json").exists() or (HERE/"AUTHORS.json").exists():raise FileExistsError("Study closed")
    lock=PRIVATE/"dispatch.lock"
    with lock.open("x") as fh:fh.write(str(os.getpid()))
    try:
        with ThreadPoolExecutor(max_workers=4) as pool:
            authors=dict(pool.map(dispatch_one,f["dispatch_order"]))
        seal(HERE/"AUTHORS.json",{"utc":now(),"freeze":canonical(HERE/"FREEZE.json"),"authors":authors,
                                 "tariff_usd":sum((v.get("tariff_cost_usd") or 0) for v in authors.values())})
    finally:
        lock.unlink()


def close():
    guard()
    if (HERE/"REFERENCE_OPEN.json").exists() or (HERE/"PREDICTIONS.json").exists():raise FileExistsError("Study closed")
    authors=read(HERE/"AUTHORS.json")
    assert authors["freeze"]==canonical(HERE/"FREEZE.json")
    groups=source_grids()
    methods={"independent":{"values":named(independent(groups))}}
    rule=[rule_permutation(groups,s) for s in SEEDS]
    methods["ratio_rule"]={"values":named(np.mean([score_order(groups,q) for q,_ in rule],axis=0)),"rhos":rule[0][1]}
    failures={}
    def run_slot(slot):
        rec=authors["authors"][slot]
        if "law" not in rec:return slot,None,"No valid author artifact"
        p=HERE/"laws"/slot
        assert all(canonical(p/k)==v for k,v in rec["law"].items())
        try:
            runs=[run_code(slot,(p/"generator.py").read_text(encoding="utf-8"),read(p/"model.json"),groups,s) for s in SEEDS]
            per=[score_order(groups,q) for q,_ in runs]
            return slot,{"values":named(np.mean(per,axis=0)),"by_seed":[named(v) for v in per],
                         "draws":[i for _,i in runs]},""
        except (ValueError,AssertionError,OSError,RuntimeError) as e:
            return slot,None,repr(e)[:510]
    with ThreadPoolExecutor(max_workers=2) as pool:
        for slot,res,error in pool.map(run_slot,SLOTS):
            if error:failures[slot]=error
            else:methods[slot]=res
    for rec in methods.values():
        assert abs(rec["values"]["mean_both_kg"] - methods["independent"]["values"]["mean_both_kg"])<1e-10
    seal(HERE/"PREDICTIONS.json",{"utc":now(),"freeze":canonical(HERE/"FREEZE.json"),"authors":canonical(HERE/"AUTHORS.json"),
          "methods":methods,"failures":failures,"joint_target_measurements_open":False})
    print("Closed",list(methods),"retained failures",failures)


if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("stage",choices=["freeze","dispatch","close"])
    {"freeze":freeze,"dispatch":dispatch,"close":close}[cli.parse_args().stage]()
