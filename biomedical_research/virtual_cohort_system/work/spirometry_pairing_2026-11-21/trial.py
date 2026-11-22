"""Seal a small matched-evidence test and dispatch real model authors through the existing client."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from study import (HERE, N, PRIVATE, ROOT, SEEDS, USES, canonical, comparator, fit, grids, named,
                   read, score, seal, sha, validate_order)

PILOT=ROOT/"work/evidence_composition_pilot_2026-11-16"
sys.path.insert(0,str(PILOT))
import pilot as harness

client=harness.client
CONFIG="OA_SOL"
client.CONFIGS[CONFIG]={**client.CONFIGS[CONFIG],"effort":"medium"}
client.MAX_OUTPUT=6000
client.CAPS={"openai":1.20}
SLOTS=tuple(f"{arm}{i}" for arm in ("M","J") for i in range(1,5))


def now():
    return datetime.now(timezone.utc).isoformat()


def bindings():
    own=["ADMISSION.md","PROTOCOL.md","MARGINAL_SOURCE.json","JOINT_SOURCE.json","REQUEST.txt",
         "study.py","trial.py","reference_spiro.py","evaluate.py","fixtures.py"]
    others=["work/bilateral_grip_transfer_2026-11-21/science.py","work/evidence_composition_pilot_2026-11-16/pilot.py",
            "work/cross_model_api_pilot_2026-11-10/provider_client.py","work/cross_model_api_pilot_2026-11-10/provider_preflight.py",
            "cohort_harness/_worker.py","cohort_harness/execution.py","cohort_harness/contracts.py"]
    paths=[HERE/name for name in own]+[ROOT/name for name in others]
    return {p.relative_to(ROOT).as_posix():canonical(p) for p in paths}


def prompt(arm):
    names=["REQUEST.txt","MARGINAL_SOURCE.json"]
    if arm=="J":
        names.append("JOINT_SOURCE.json")
    return "\n\n".join((HERE/name).read_text(encoding="utf-8") for name in names)


def contract(n):
    obj={"schema_version":1,"task_id":"paired_spirometry","mode":"whole_cohort",
         "population":"Adults aged 18–79, equal sex weights","row_id":"row_id","n_rows":n,
         "columns":[{"name":"row_id","kind":"integer","unit":"","role":"identifier","nullable":False},
                    {"name":"fvc_index","kind":"integer","unit":"within-sex grid index","role":"generated","nullable":False}],
         "information_policy":{"mode":"published_evidence","excluded_cohorts":[],"allowed_tools":[]},
         "budget":{"source_queries":0,"source_downloads":0,"revisions":0}}
    harness.contracts.validate_task(obj)
    return obj


def execute(slot, program, spec, groups, seed):
    work=PRIVATE/"runs"/slot/str(seed)
    submission=work/"submission"
    submission.mkdir(parents=True,exist_ok=True)
    entry=submission/"generator.py"
    if not entry.exists():
        with entry.open("x",encoding="utf-8",newline="\n") as file: file.write(program)
    assert entry.read_text(encoding="utf-8")==program
    task=contract(sum(len(x) for _,x,_ in groups))
    seal(submission/"model_spec.json",{"task":task,"model":spec,"groups":[
        {"sex":s,"fev1":x.tolist(),"fvc":y.tolist()} for s,x,y in groups]})
    run=work/"isolated"
    receipt=read(run/"execution.json") if (run/"execution.json").is_file() else harness.isolated(submission,task,run,seed)
    if receipt["status"]!="success":
        report=run/"output/worker_report.json"
        detail=read(report).get("error","") if report.is_file() and report.stat().st_size else receipt.get("error","")
        raise ValueError("Isolated worker: "+str(detail)[:350])
    csv=run/"output/generated.csv"
    assert sha(csv)==receipt["generated_sha256"] and canonical(entry)==canonical(run/"input/generator.py")
    frame=pd.read_csv(csv)
    assert list(frame)==["row_id","fvc_index"] and np.array_equal(frame.row_id,np.arange(len(frame)))
    raw=np.stack([validate_order(a,len(x)) for a,(_,x,_) in zip(np.split(frame.fvc_index.to_numpy(),len(groups)),groups,strict=True)])
    return raw,{"proposal_csv_sha256":sha(csv)}


def save_draw(slot, seed, groups, raw):
    final,qc=fit(groups,raw)
    x=np.stack([r for _,r,_ in groups])
    y=np.stack([l[o] for (_,_,l),o in zip(groups,final,strict=True)])
    path=PRIVATE/"draws"/slot/f"{seed}.npz"
    path.parent.mkdir(parents=True,exist_ok=True)
    arrays={"sex":np.repeat(np.array(["F","M"]),x.shape[1]),"fev1_l":x.ravel(),"fvc_l":y.ravel(),
            "raw_fvc_index":raw,"accepted_fvc_index":final}
    if not path.exists():
        np.savez_compressed(path,**arrays)
    with np.load(path,allow_pickle=False) as saved:
        for key,data in arrays.items():
            np.testing.assert_array_equal(saved[key],data)
    vals=named(score(groups,final))
    return {"seed":seed,"virtual_records_sha256":sha(path),"values":vals,"feasibility":qc}


def freeze():
    import fixtures
    assert Path(fixtures.__file__).resolve() == HERE / "fixtures.py"
    if (HERE/"FREEZE.json").exists():
        raise FileExistsError("Design already frozen")
    fixtures.check()
    program=("import numpy as np\nimport pandas as pd\n"
             "def generate(observed,spec,seed):\n"
             "    ids=np.concatenate([np.arange(len(g['fev1'])) for g in spec['groups']])\n"
             "    return pd.DataFrame({'row_id':np.arange(len(ids)),'fvc_index':ids})\n")
    groups=grids(53)
    raw,fixture=execute("interface_fixture",program,{},groups,17)
    assert np.array_equal(raw,np.tile(np.arange(53),(2,1)))
    order=np.random.default_rng(48107).permutation(SLOTS).tolist()
    config=client.CONFIGS[CONFIG]
    allowance={}
    for arm in ["J","M"]:
        payload=json.dumps(client.make_request(CONFIG,prompt(arm))[1],ensure_ascii=False).encode()
        allowance[arm]=((len(payload)+4096)*max(config["input_rate"],config["cache_write_rate"])+client.MAX_OUTPUT*config["output_rate"])/1e6
    assert sum(allowance[a[0]] for a in order)<=client.CAPS["openai"]
    seal(HERE/"FREEZE.json",{"utc":now(),"files":bindings(),"configuration":config,"system":client.SYSTEM,
        "slots":order,"seeds":SEEDS,"n_per_sex":N,"max_output_tokens":client.MAX_OUTPUT,"tariff_cap_usd":client.CAPS["openai"],
        "per_call_reservation_usd":allowance,"worker_fixture":fixture,"case_fixture_sha256":canonical(HERE/"fixtures.py"),
        "target_paired_results_open":False})


def guard():
    f=read(HERE/"FREEZE.json")
    assert f["files"]==bindings() and f["configuration"]==client.CONFIGS[CONFIG] and f["system"]==client.SYSTEM
    assert f["tariff_cap_usd"]==client.CAPS["openai"] and f["max_output_tokens"]==client.MAX_OUTPUT
    return f


def get_author(slot):
    root=PRIVATE/"api"
    call=root/"calls"/slot
    if call.exists() and not (call/"receipt.json").exists():
        raise RuntimeError("Outstanding reservation for "+slot)
    r=read(call/"receipt.json") if call.exists() else client.call_once(root,slot,CONFIG,prompt(slot[0]))[0]
    info={k:r.get(k) for k in ("status","artifact_status","returned_model","requested_model","usage","tariff_cost_usd",
         "request_sha256","response_text.txt_sha256","started_utc","ended_utc","mechanical_error","api_error_code","completion_status")}
    if (r.get("status")=="received" and r.get("returned_model")==client.CONFIGS[CONFIG]["model"]
            and (call/"artifact.json").is_file()):
        assert sha(call/"artifact.json")==r["artifact.json_sha256"]
        obj=read(call/"artifact.json")
        dest=HERE/"laws"/slot
        dest.mkdir(parents=True,exist_ok=True)
        entry=dest/"generator.py"
        if not entry.exists():
            with entry.open("x",encoding="utf-8",newline="\n") as f: f.write(obj["generator_py"])
        assert entry.read_text(encoding="utf-8")==obj["generator_py"]
        seal(dest/"model.json",obj["model_spec"])
        seal(dest/"decision.json",obj["decision_record"])
        info["artifacts"]={k:canonical(dest/k) for k in ("generator.py","model.json","decision.json")}
    print(slot,info["status"],info["artifact_status"],info["tariff_cost_usd"],flush=True)
    return slot,info


def dispatch():
    frozen=guard()
    if any((HERE/n).is_file() for n in ("AUTHORS.json","REFERENCE_OPEN.json")):
        raise FileExistsError("Author step is closed")
    lock=PRIVATE/"dispatch.lock"
    with lock.open("x") as f: f.write(str(os.getpid()))
    try:
        with ThreadPoolExecutor(4) as pool:
            authors=dict(pool.map(get_author,frozen["slots"]))
        seal(HERE/"AUTHORS.json",{"utc":now(),"freeze":canonical(HERE/"FREEZE.json"),"authors":authors,
             "total_tariff_usd":sum(v["tariff_cost_usd"] or 0 for v in authors.values()),
             "cost_missing":sum(v["tariff_cost_usd"] is None for v in authors.values())})
    finally:
        lock.unlink()


def close():
    guard()
    if any((HERE/n).is_file() for n in ("PREDICTIONS.json","REFERENCE_OPEN.json")):
        raise FileExistsError("Predictions already closed")
    auth=read(HERE/"AUTHORS.json")
    assert auth["freeze"]==canonical(HERE/"FREEZE.json")
    groups=grids()
    def run_one(slot):
        draws=[]
        try:
            if slot in SLOTS:
                law=HERE/"laws"/slot
                rec=auth["authors"][slot]
                if "artifacts" not in rec:
                    return slot,{},"No valid model artifact"
                assert all(canonical(law/k)==v for k,v in rec["artifacts"].items())
                program=(law/"generator.py").read_text(encoding="utf-8")
                spec=read(law/"model.json")
            for seed in SEEDS:
                if slot in SLOTS:
                    raw,extra=execute(slot,program,spec,groups,seed)
                else:
                    raw,rhos=comparator(groups,seed,joint=slot=="source_gaussian")
                    extra={"latent_parameters":rhos}
                draws.append({**save_draw(slot,seed,groups,raw),**extra})
            values={k:float(np.mean([z["values"][k] for z in draws])) for k in USES}
            return slot,{"draws":draws,"values":values},""
        except (AssertionError,ValueError,OSError,RuntimeError,KeyError,TypeError) as err:
            return slot,{"draws":draws},repr(err)[:450]
    methods,failures,partial={},{},{}
    with ThreadPoolExecutor(2) as pool:
        for name,res,err in pool.map(run_one,("source_gaussian","physical_uniform",*SLOTS)):
            if err:
                failures[name]=err
                partial[name]=res
            else:
                methods[name]=res
    assert {"source_gaussian","physical_uniform"}<=methods.keys()
    assert np.ptp([r["values"]["ratio_of_means_pct"] for r in methods.values()])<1e-9
    bounds={}
    for arm,control in [("J","source_gaussian"),("M","physical_uniform")]:
        variants=[v for k,v in methods.items() if k in SLOTS and k.startswith(arm)]
        if len(variants)==4:
            bounds[arm]={k:float(np.median([abs(v["values"][k]-methods[control]["values"][k]) for v in variants])) for k in USES}
    seal(HERE/"PREDICTIONS.json",{"utc":now(),"freeze":canonical(HERE/"FREEZE.json"),"authors":canonical(HERE/"AUTHORS.json"),
         "methods":methods,"failures":failures,"partial":partial,"upper_bounds_on_median_error_gain":bounds,
         "target_paired_results_open":False})
    print("Sealed",list(methods),"failures",failures,"bounds",bounds,flush=True)


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("stage",choices=("freeze","dispatch","close"))
    {"freeze":freeze,"dispatch":dispatch,"close":close}[p.parse_args().stage]()
