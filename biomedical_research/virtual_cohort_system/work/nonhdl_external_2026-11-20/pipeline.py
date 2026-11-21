"""Freeze, call one fresh author, and close every draw before the custodian reveals outcomes."""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
from science import HERE,N,SEEDS,estimates,gaussian_rho,paired,possible_counts,read,sha,source_law,stat_permutation,values,write

PROJECT=HERE.parents[1]
PILOT=PROJECT/"work/evidence_composition_pilot_2026-11-16"
sys.path.insert(0,str(PILOT))
import pilot as sandbox

PRIVATE=HERE/"private"
client=sandbox.client
client.MAX_OUTPUT=12000
client.CAPS={"openai":.45}
SLOT="lipid_author"
MODEL="OA_SOL"
def now():
    return datetime.now(timezone.utc).isoformat()
def task(n=N):
    fields=[{"name":a,"kind":"integer","role":role,"unit":"","nullable":False}
            for a,role in (("row_id","identifier"),("hdl_index","generated"))]
    t={"schema_version":1,"task_id":"east_african_nonhdl_pairing","mode":"whole_cohort",
       "population":"East African adults aged 20 or more; a common frozen law","row_id":"row_id",
       "n_rows":n,"columns":fields,"information_policy":{"mode":"published_evidence","excluded_cohorts":[],"allowed_tools":[]},
       "budget":{"source_queries":0,"source_downloads":0,"revisions":0}}
    sandbox.contracts.validate_task(t)
    return t
def prompt():
    return (HERE/"REQUEST.txt").read_text(encoding="utf8")+"\nPublished evidence common to both arms:\n"+(HERE/"SOURCE.json").read_text(encoding="utf8")
def txtsha(p):
    return hashlib.sha256(p.read_text(encoding="utf8").encode()).hexdigest()
def bindings():
    own=("REQUEST.txt","SOURCE.json","PROTOCOL.md","SCREEN_ORDER.md","ADMISSION_COUNTS.json","catalogue.py","extract_source.py","science.py","reference.py","pipeline.py","evaluate.py","tests_science.py","verify.py")
    common=[PILOT/"pilot.py",PROJECT/"cohort_harness/_worker.py",PROJECT/"cohort_harness/contracts.py",
            PROJECT/"cohort_harness/execution.py",PROJECT/"work/cross_model_api_pilot_2026-11-10/provider_client.py",
            PROJECT/"work/cross_model_api_pilot_2026-11-10/provider_preflight.py"]
    return {p.relative_to(PROJECT).as_posix():txtsha(p) for p in [*(HERE/name for name in own),*common]}
def guarded():
    f=read(HERE/"FREEZE.json")
    assert f["bindings"]==bindings() and f["task"]==task() and f["seeds"]==list(SEEDS)
    assert f["model"]==client.CONFIGS[MODEL] and f["system_sha256"]==hashlib.sha256(client.SYSTEM.encode()).hexdigest()
    assert f["prompt_sha256"]==hashlib.sha256(prompt().encode()).hexdigest()
    for filename,digest in f["private_inputs"].items():assert sha(PRIVATE/filename)==digest
    return f
def run_agent(code,settings,seed,n,dest):
    t,h=values(n)
    wrap=PRIVATE/"input_specs"/dest.name
    wrap.mkdir(parents=True,exist_ok=True)
    (wrap/"generator.py").write_text(code,encoding="utf8")
    obj={"model":settings,"task":task(n),"tc_mg_dl":t.tolist(),"hdl_mg_dl":h.tolist()}
    (wrap/"model_spec.json").write_text(json.dumps(obj,allow_nan=False),encoding="utf8")
    report=sandbox.isolated(wrap,task(n),dest,seed)
    if report["status"]!="success":raise ValueError(report.get("error",{}))
    out=dest/"output/generated.csv"
    assert sha(out)==report["generated_sha256"]
    df=pd.read_csv(out)
    assert list(df.columns)==["row_id","hdl_index"] and np.array_equal(df.row_id,np.arange(n))
    ix=df.hdl_index.to_numpy()
    if not np.issubdtype(ix.dtype,np.integer) or not np.array_equal(np.sort(ix),np.arange(n)):
        raise ValueError("Index is not a permutation")
    return ix,report["generated_sha256"]
def freeze():
    from tests_science import test
    test()
    assert not (HERE/"FREEZE.json").exists()
    code="import numpy as np\nimport pandas as pd\ndef generate(observed,spec,seed):\n    i=np.arange(spec['task']['n_rows'])\n    return pd.DataFrame({'row_id':i,'hdl_index':i[::-1]})\n"
    dest=PRIVATE/"fixture"
    if not dest.exists():
        ix,h=run_agent(code,{},9,40,dest)
        assert np.array_equal(ix,np.arange(40)[::-1])
    else:
        h=sha(dest/"output/generated.csv")
        assert read(dest/"execution.json")["status"]=="success" and np.array_equal(pd.read_csv(dest/"output/generated.csv").hdl_index,np.arange(40)[::-1])
    conf=client.CONFIGS[MODEL];body=client.make_request(MODEL,prompt())[1]
    upper=((len(json.dumps(body,ensure_ascii=False).encode())+4096)*max(conf["input_rate"],conf["cache_write_rate"])+client.MAX_OUTPUT*conf["output_rate"])/1e6
    assert upper<client.CAPS["openai"]
    data=["source.xml","mekelle.xml","workers.xml","mekelle.sav","workers.dta"]
    write(HERE/"FREEZE.json",{"time_utc":now(),"bindings":bindings(),"task":task(),"seeds":list(SEEDS),
          "model":conf,"system_sha256":hashlib.sha256(client.SYSTEM.encode()).hexdigest(),
          "prompt_sha256":hashlib.sha256(prompt().encode()).hexdigest(),"private_inputs":{p:sha(PRIVATE/p) for p in data},
          "source_law":source_law(),"statistical_rho":gaussian_rho(),"fixture_generated_sha256":h,
          "source_only_checks":"passed","max_output_tokens":client.MAX_OUTPUT,"max_usd":client.CAPS["openai"],
          "reservation_upper_usd":upper,"target_results_opened":False})
    print("Protocol frozen",sha(HERE/"FREEZE.json"),flush=True)
def author():
    guarded()
    assert not (HERE/"REFERENCE_OPEN.json").exists() and not (HERE/"CLOSURE.json").exists()
    path=PRIVATE/"api/calls"/SLOT
    if path.exists(): rec=read(path/"receipt.json")
    else: rec,_=client.call_once(PRIVATE/"api",SLOT,MODEL,prompt())
    keys=("status","artifact_status","requested_model","returned_model","started_utc","ended_utc","usage","tariff_cost_usd","request_sha256","response_text.txt_sha256","artifact.json_sha256","error_type","api_error_code","mechanical_error")
    record={k:rec.get(k) for k in keys}
    usable=rec.get("status")=="received" and rec.get("returned_model")==client.CONFIGS[MODEL]["model"] and (path/"artifact.json").exists()
    if usable:
        assert sha(path/"artifact.json")==rec["artifact.json_sha256"]
        obj=read(path/"artifact.json"); law=HERE/"law";law.mkdir(exist_ok=True)
        materials={"generator.py":obj["generator_py"],"model_spec.json":json.dumps(obj["model_spec"],indent=2,ensure_ascii=False),"decision.json":json.dumps(obj["decision_record"],indent=2,ensure_ascii=False)}
        for key,txt in materials.items():
            dest=law/key
            if not dest.exists():
                with dest.open("x",encoding="utf8",newline="\n") as fw:fw.write(txt)
            assert dest.read_text(encoding="utf8")==txt
        record["law"]={key:txtsha(law/key) for key in materials}
    record["usable"]=usable
    if (HERE/"AUTHOR.json").exists():assert read(HERE/"AUTHOR.json")==record
    else:write(HERE/"AUTHOR.json",record)
    print("Authorship",record["status"],usable,record.get("tariff_cost_usd"),flush=True)
def generate():
    guarded()
    assert not (HERE/"REFERENCE_OPEN.json").exists() and not (HERE/"CLOSURE.json").exists()
    auth=read(HERE/"AUTHOR.json");arms={}
    for arm in ("statistical","agent"):
        runs=[]; arr=[]; errors=[]
        if arm=="agent" and not auth["usable"]:
            arms[arm]={"runs":[],"usable":False,"error":"No valid API artifact"};continue
        for seed in SEEDS:
            try:
                raw_sha=None
                if arm=="statistical":ix=stat_permutation(N,seed)
                else:
                    law=HERE/"law"
                    assert all(txtsha(law/k)==v for k,v in auth["law"].items())
                    ix,raw_sha=run_agent((law/"generator.py").read_text(encoding="utf8"),read(law/"model_spec.json"),seed,N,PRIVATE/f"run-{seed}")
                x=paired(ix);m=estimates(x);arr.append(x)
                path=PRIVATE/f"{arm}-{seed}.npy"
                if path.exists():assert np.array_equal(np.load(path,allow_pickle=False),x)
                else:np.save(path,x,allow_pickle=False)
                runs.append({"seed":seed,"array_sha256":sha(path),"permutation_csv_sha256":raw_sha,"estimates":m})
            except (ValueError,AssertionError,RuntimeError,OSError) as exc:
                errors.append({"seed":seed,"error":str(exc)[:900],"class":type(exc).__name__})
        arms[arm]={"runs":runs,"errors":errors,"usable":len(arr)==len(SEEDS),"pooled":estimates(np.vstack(arr)) if len(arr)==len(SEEDS) else None}
    assert arms["statistical"]["usable"]
    t,h=values()
    write(HERE/"CLOSURE.json",{"time_utc":now(),"freeze_sha256":sha(HERE/"FREEZE.json"),
          "author_sha256":sha(HERE/"AUTHOR.json"),"target_results_opened":False,
          "all_pairing_tail_bounds_pct":[100*v/N for v in possible_counts(t,h)],"arms":arms})
    print("Output closure",[(k,x["usable"]) for k,x in arms.items()],flush=True)
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("step",choices=["freeze","author","generate"])
    {"freeze":freeze,"author":author,"generate":generate}[parser.parse_args().step]()
