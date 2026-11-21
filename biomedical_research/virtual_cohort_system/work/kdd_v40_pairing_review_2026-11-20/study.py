"""Run the source-only review experiment, with a separate author and analysis phase."""
import argparse
import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from scoring import HERE, OLD, SCENARIOS, SEEDS, SLOTS, author_summary, read, score
from feasibility import numerical_control, values

PROJECT = HERE.parents[1]
PILOT = PROJECT / "work/evidence_composition_pilot_2026-11-16"
sys.path.insert(0, str(PILOT))
import pilot as harness

client = harness.client
client.MAX_OUTPUT = 12000
client.CAPS = {"openai":.96}
client.CONFIGS["OA_SOL"] = {**client.CONFIGS["OA_SOL"],"effort":"medium"}
PRIVATE = HERE / "private"


def utc():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_hash(path):
    return hashlib.sha256(path.read_text(encoding="utf-8").encode()).hexdigest()


def save(path, value):
    path.parent.mkdir(exist_ok=True, parents=True)
    with path.open("x",encoding="utf-8",newline="\n") as f:
        json.dump(value,f,ensure_ascii=False,allow_nan=False,indent=2)
        f.write("\n")


def task(n):
    out = {"schema_version":1, "task_id":"source_only_mwanza_pairing_sensitivity", "mode":"whole_cohort",
           "population":"Source-compatible possible adult lipid pairs", "row_id":"row_id", "n_rows":n,
           "columns":[{"name":k,"kind":"integer","role":r,"unit":"","nullable":False}
                      for k,r in (("row_id","identifier"),("hdl_index","generated"))],
           "information_policy":{"mode":"published_evidence","excluded_cohorts":[],"allowed_tools":[]},
           "budget":{"source_queries":0,"source_downloads":0,"revisions":0}}
    harness.contracts.validate_task(out)
    return out


def prompt():
    return (HERE/"REQUEST.txt").read_text(encoding="utf-8") + "\nPublished source packet\n" + (OLD/"SOURCE.json").read_text(encoding="utf-8")


def bindings():
    return {p.relative_to(PROJECT).as_posix():text_hash(p) for p in [
        *(HERE/x for x in ("PROTOCOL.md","REQUEST.txt","study.py","scoring.py","feasibility.py")),
        OLD/"SOURCE.json", OLD/"science.py", PILOT/"pilot.py", harness.WORKER,
        PROJECT/"work/cross_model_api_pilot_2026-11-10/provider_client.py",
        PROJECT/"cohort_harness/execution.py"]}


def execute(code, model, scenario, seed, folder, n=16000):
    tc,hdl=values(n)
    stage=folder/"candidate"
    stage.mkdir(parents=True,exist_ok=False)
    (stage/"generator.py").write_text(code,encoding="utf-8",newline="\n")
    t=task(n)
    save(stage/"model_spec.json",{"model":model,"scenario":scenario,"task":t,"tc_mg_dl":tc.tolist(),"hdl_mg_dl":hdl.tolist()})
    rep=harness.isolated(stage,t,folder/"run",seed)
    if rep["status"] != "success":
        wr=folder/"run/output/worker_report.json"
        details=read(wr).get("error") if wr.exists() and wr.stat().st_size else rep.get("error")
        raise ValueError("isolated execution failed: "+str(details)[:450])
    csv=folder/"run/output/generated.csv"
    if digest(csv)!=rep["generated_sha256"]:
        raise ValueError("Output digest mismatch")
    frame=pd.read_csv(csv)
    if list(frame)!=["row_id","hdl_index"] or not np.array_equal(frame.row_id.to_numpy(),np.arange(n)):
        raise ValueError("Invalid row identifiers")
    ix=frame.hdl_index.to_numpy()
    z=score(tc,hdl,ix)
    np.save(folder/"perm.npy",ix,allow_pickle=False)
    return {"score":z,"permutation_hash":digest(folder/"perm.npy"),"output_hash":digest(csv)}


def freeze():
    if (HERE/"FREEZE.json").exists():
        raise FileExistsError("Already frozen")
    tc,hd=values(17)
    try:
        score(tc,hd,np.zeros(17,dtype=int))
    except ValueError:
        pass
    else:
        raise ValueError("Invalid-index fixture accepted")
    assert score(np.array([200.,199.]),np.array([40.,40.]),np.array([0,1]))["tail_count"]==1
    fixture="import numpy as np\nimport pandas as pd\ndef generate(observed,spec,seed):\n    ix=np.arange(spec['task']['n_rows'])\n    return pd.DataFrame({'row_id':ix,'hdl_index':ix if spec['scenario']=='a' else ix[::-1]})\n"
    for name in SCENARIOS:
        got=execute(fixture,{},name,17,PRIVATE/("fixture_"+name),n=17)
        assert got["score"]["n"]==17
        assert np.array_equal(np.load(PRIVATE/("fixture_"+name)/"perm.npy"),np.arange(17) if name=="a" else np.arange(16,-1,-1))
    encoded=json.dumps(client.make_request("OA_SOL",prompt())[1],ensure_ascii=False).encode()
    conf=client.CONFIGS["OA_SOL"]
    allowance=((len(encoded)+4096)*max(conf["input_rate"],conf["cache_write_rate"])+client.MAX_OUTPUT*conf["output_rate"])/1e6
    assert allowance*len(SLOTS) <= client.CAPS["openai"]
    save(HERE/"FREEZE.json",{"time":utc(),"bindings":bindings(),"prompt_sha256":hashlib.sha256(prompt().encode()).hexdigest(),
         "system_sha256":hashlib.sha256(client.SYSTEM.encode()).hexdigest(),"model":conf,"max_output":client.MAX_OUTPUT,
         "cap_usd":client.CAPS["openai"],"reservation_each":allowance,"authors":SLOTS,"seeds":SEEDS,"source_only":True,
         "fixture_passed":True,"patient_references_used":False})


def guard():
    f=read(HERE/"FREEZE.json")
    assert f["bindings"]==bindings() and f["model"]==client.CONFIGS["OA_SOL"] and f["seeds"]==list(SEEDS)
    assert f["prompt_sha256"]==hashlib.sha256(prompt().encode()).hexdigest() and f["system_sha256"]==hashlib.sha256(client.SYSTEM.encode()).hexdigest()
    assert f["max_output"]==client.MAX_OUTPUT and f["cap_usd"]==client.CAPS["openai"]


def author(slot):
    path=PRIVATE/"api/calls"/slot
    if path.exists():
        if not (path/"receipt.json").exists():
            raise RuntimeError("An author call is in flight or interrupted; inspect its reservation.")
        record=read(path/"receipt.json")
    else:
        record,_=client.call_once(PRIVATE/"api",slot,"OA_SOL",prompt())
    fields=("requested_model","returned_model","status","artifact_status","mechanical_error","stop_reason","api_error_code",
            "usage","tariff_cost_usd","request_sha256","response_text.txt_sha256","started_utc","ended_utc")
    short={k:record.get(k) for k in fields}
    if record["status"]=="received" and record.get("returned_model")==client.CONFIGS["OA_SOL"]["model"] and (path/"artifact.json").exists():
        assert record["artifact.json_sha256"]==digest(path/"artifact.json")
        obj=read(path/"artifact.json")
        law=HERE/"laws"/slot
        law.mkdir(parents=True,exist_ok=True)
        files={"generator.py":obj["generator_py"],"model.json":json.dumps(obj["model_spec"],indent=2,ensure_ascii=False),
               "decision.json":json.dumps(obj["decision_record"],indent=2,ensure_ascii=False)}
        for k,v in files.items():
            file=law/k
            if not file.exists():
                file.write_text(v,encoding="utf-8",newline="\n")
            assert file.read_text(encoding="utf-8")==v
        short["law"]={k:text_hash(law/k) for k in files}
    return slot,short


def dispatch():
    guard()
    if (HERE/"AUTHORS.json").exists():
        raise FileExistsError("Author batch already closed")
    with ThreadPoolExecutor(max_workers=4) as pool:
        records=dict(pool.map(author,SLOTS))
    save(HERE/"AUTHORS.json",{"closed":utc(),"freeze_sha256":text_hash(HERE/"FREEZE.json"),"records":records})
    print([(k,r["status"],r["artifact_status"],r["tariff_cost_usd"]) for k,r in records.items()])


def run():
    guard()
    authors=read(HERE/"AUTHORS.json")
    assert authors["freeze_sha256"]==text_hash(HERE/"FREEZE.json")
    results={}
    for slot in SLOTS:
        record=authors["records"][slot]
        runs={mode:[] for mode in SCENARIOS}
        if "law" in record:
            law=HERE/"laws"/slot
            assert all(text_hash(law/k)==v for k,v in record["law"].items())
            for mode in SCENARIOS:
                for seed in SEEDS:
                    folder=PRIVATE/"draws"/slot/mode/str(seed)
                    receipt=folder/"result.json"
                    if receipt.exists():
                        out=read(receipt)
                    else:
                        try:
                            out=execute((law/"generator.py").read_text(encoding="utf-8"),read(law/"model.json"),mode,seed,folder)
                        except (ValueError, RuntimeError, OSError, AssertionError) as exc:
                            out={"reason":str(exc)[:600]}
                        out["seed"]=seed
                        save(receipt,out)
                    runs[mode].append(out)
        results[slot]={"runs":runs,**author_summary(runs)}
    save(HERE/"SENSITIVITY.json",{"closed":utc(),"authors_sha256":text_hash(HERE/"AUTHORS.json"),"authors":results})


def control():
    guard()
    if (HERE/"CONTROL.json").exists():
        raise FileExistsError("Numerical control already closed")
    folder=PRIVATE/"control"
    result=numerical_control(folder)
    for key,v in result.items():
        if "score" in v:
            v["permutation_hash"]=digest(folder/(key+".npy"))
    save(HERE/"CONTROL.json",{"time":utc(),"constructive_examples":result,"global_bounds":False})


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("action",choices=["freeze","dispatch","run","control"])
    action=parser.parse_args().action
    {"freeze":freeze,"dispatch":dispatch,"run":run,"control":control}[action]()
