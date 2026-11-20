"""Immutable, bounded dispatch of six fresh authors and sealed paired-record generation."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

import numpy as np
import pandas as pd

from science import HERE, MODEL_DIR, N, PARENTS, SEEDS, SOURCE, baseline_fit, baseline_indices, endpoints, marginals, pair, preflight, read

PROJECT=HERE.parents[1]
PRIVATE=HERE/"private"
ARTICLE=PROJECT/"work/original_paper_capability_2026-11-17/private_sources/iron_original.layout.txt"
PILOT=PROJECT/"work/evidence_composition_pilot_2026-11-16"
sys.path.insert(0,str(PILOT))
import pilot as sandbox

client=sandbox.client
MODEL="OA_SOL"
client.MAX_OUTPUT=16384
client.CAPS={"openai":3.}


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha(path):
    return hashlib.sha256(path.read_text(encoding="utf-8").encode()).hexdigest()


def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("x",encoding="utf-8",newline="\n") as f:
        json.dump(data,f,indent=2,ensure_ascii=False,allow_nan=False);f.write("\n")


def task(n=N):
    t={"schema_version":1,"task_id":"prospective_external_iron_pairing","mode":"whole_cohort",
       "population":"Community sample of adult mothers aged 18–49 in southern Nigeria",
       "row_id":"row_id","n_rows":n,"columns":[
           {"name":"row_id","kind":"integer","unit":"","role":"identifier","nullable":False},
           {"name":"fe_index","kind":"integer","unit":"within-band order index","role":"generated","nullable":False}],
       "information_policy":{"mode":"published_evidence","excluded_cohorts":[],"allowed_tools":[]},
       "budget":{"source_queries":0,"source_downloads":0,"revisions":0}}
    sandbox.contracts.validate_task(t)
    return t


def prompt():
    parts=[(HERE/"REQUEST.txt").read_text(encoding="utf-8"),
           "External published source, Zhu et al. (2010):",ARTICLE.read_text(encoding="utf-8"),
           "Separate Chinese source. CHNS A community tables:",(SOURCE/"A_TABLES.json").read_text(encoding="utf-8"),
           "CHNS A supplementary conditional contrast:",(SOURCE/"A_SUPPLEMENT.json").read_text(encoding="utf-8")]
    return "\n\n".join(parts)


def bound():
    files=[HERE/name for name in ("PROTOCOL.md","REQUEST.txt","ADMISSION.json","admission.py","science.py","study.py","evaluate.py","verify.py")]
    files += [SOURCE/"A_TABLES.json",SOURCE/"A_SUPPLEMENT.json",MODEL_DIR/"source_model.py",PILOT/"pilot.py",
              PROJECT/"cohort_harness/_worker.py",PROJECT/"cohort_harness/contracts.py",PROJECT/"cohort_harness/execution.py",
              PROJECT/"work/cross_model_api_pilot_2026-11-10/provider_client.py",PROJECT/"work/cross_model_api_pilot_2026-11-10/provider_preflight.py"]
    return {p.relative_to(PROJECT).as_posix():text_sha(p) for p in files}


def guard():
    f=read(HERE/"FREEZE.json")
    assert f["text_sha256"]==bound() and sha(ARTICLE)==f["article_sha256"]
    assert hashlib.sha256(prompt().encode()).hexdigest()==f["prompt_sha256"]
    assert f["task"]==task() and f["model"]==client.CONFIGS[MODEL] and f["seeds"]==SEEDS and f["authors"]==PARENTS
    assert f["tariff_cap"]==client.CAPS["openai"] and f["max_output_tokens"]==client.MAX_OUTPUT
    return f


def fixture():
    path=PRIVATE/"fixture"
    path.mkdir(exist_ok=True)
    code='import pandas as pd\nimport numpy as np\n\ndef generate(observed,spec,seed):\n    idx=np.concatenate([np.arange(len(g["hb"])) for g in spec["bands"]])\n    return pd.DataFrame({"row_id":np.arange(len(idx)),"fe_index":idx})\n'
    groups=marginals(baseline_fit()[0],87,120)
    (path/"generator.py").write_text(code,encoding="utf-8")
    (path/"model_spec.json").write_text(json.dumps({"model":{},"task":task(120),"bands":groups}),encoding="utf-8")
    dest=PRIVATE/"fixture_run"
    rep=read(dest/"execution.json") if dest.exists() else sandbox.isolated(path,task(120),dest,87)
    assert rep["status"]=="success",rep.get("error")
    frame=pd.read_csv(dest/"output/generated.csv");assert len(pair(groups,frame.fe_index))==120
    return rep["generated_sha256"]


def freeze():
    checks=preflight()
    from evaluate import evaluation_fixture
    evaluation_fixture()
    checks["isolated_contract_fixture_sha256"]=fixture()
    check_path=HERE/"PREFLIGHT.json"
    if not check_path.exists():save(check_path,checks)
    assert read(check_path)==checks
    body=client.make_request(MODEL,prompt())[1]
    size=len(json.dumps(body,ensure_ascii=False).encode())
    config=client.CONFIGS[MODEL]
    reservation=(max(config["input_rate"],config["cache_write_rate"])*(size+4096)+client.MAX_OUTPUT*config["output_rate"])/1e6
    assert size<190000 and reservation*len(PARENTS)<client.CAPS["openai"]
    save(HERE/"FREEZE.json",{"utc":now(),"authors":PARENTS,"seeds":SEEDS,"rows_per_seed":N,
         "model":config,"tariff_cap":client.CAPS["openai"],"max_output_tokens":client.MAX_OUTPUT,
         "conservative_total_reservation":reservation*len(PARENTS),"text_sha256":bound(),"article_sha256":sha(ARTICLE),
         "prompt_sha256":hashlib.sha256(prompt().encode()).hexdigest(),"task":task(),
         "source_preflight":checks,"target_data_sha256":sha(PRIVATE/"biochem.dta"),"target_endpoints_opened":False})
    print("FROZEN",sha(HERE/"FREEZE.json"),"shared input",size,"bytes",flush=True)


def dispatch(cid):
    folder=PRIVATE/"api/calls"/cid
    if folder.exists():
        if not (folder/"receipt.json").exists():
            return {"author":cid,"usable":False,"reason":"Unresolved prior dispatch; slot retained"}
        rec=read(folder/"receipt.json")
    else:
        rec,_=client.call_once(PRIVATE/"api",cid,MODEL,prompt())
    fields=("status","artifact_status","requested_model","returned_model","usage","tariff_cost_usd","started_utc","ended_utc","prompt_sha256","request_sha256","response_text.txt_sha256","mechanical_error","error_type","api_error_code")
    info={"author":cid,"usable":False,"receipt":{k:rec.get(k) for k in fields}}
    artifact=folder/"artifact.json"
    if rec.get("returned_model")!=client.CONFIGS[MODEL]["model"] or not artifact.exists() or rec.get("artifact.json_sha256")!=sha(artifact):
        return info
    obj=read(artifact)
    dest=HERE/"laws"/cid;dest.mkdir(parents=True,exist_ok=True)
    materials={"generator.py":obj["generator_py"],"model_spec.json":json.dumps(obj["model_spec"],indent=2,ensure_ascii=False),
               "decision.json":json.dumps(obj["decision_record"],indent=2,ensure_ascii=False)}
    for name,txt in materials.items():
        f=dest/name
        if not f.exists():
            with f.open("x",encoding="utf-8",newline="\n") as handle:handle.write(txt)
        assert f.read_text(encoding="utf-8")==txt
    info.update(usable=True,law_sha256={k:text_sha(dest/k) for k in materials})
    print(cid,rec["status"],rec.get("tariff_cost_usd"),flush=True)
    return info


def any_open():
    return (HERE/"REFERENCE_OPEN.json").exists()


def construct():
    guard()
    assert not any_open() and not (HERE/"AUTHORS.json").exists()
    lock=PRIVATE/"dispatch.lock"
    with lock.open("x") as f:f.write(str(os.getpid()))
    try:
        with ThreadPoolExecutor(max_workers=3) as pool:
            authors=list(pool.map(dispatch,PARENTS))
        save(HERE/"AUTHORS.json",{"utc":now(),"freeze_sha256":sha(HERE/"FREEZE.json"),"authors":authors,
                                  "estimated_usd":sum((a.get("receipt",{}).get("tariff_cost_usd") or 0.) for a in authors)})
    finally:
        lock.unlink()


def sealed_draw(cid,groups,seed,definition):
    wrapper=PRIVATE/"runtime_specs"/cid/str(seed);wrapper.mkdir(parents=True,exist_ok=True)
    src=HERE/"laws"/cid
    assert all(text_sha(src/n)==h for n,h in definition.items())
    (wrapper/"generator.py").write_bytes((src/"generator.py").read_bytes())
    (wrapper/"model_spec.json").write_text(json.dumps({"model":read(src/"model_spec.json"),"bands":groups,"task":task()},allow_nan=False),encoding="utf-8")
    dest=PRIVATE/"runs"/cid/str(seed)
    res=read(dest/"execution.json") if dest.exists() else sandbox.isolated(wrapper,task(),dest,seed)
    if res["status"]!="success":raise ValueError("Isolated execution failed: "+str(res.get("error")))
    file=dest/"output/generated.csv"
    assert sha(file)==res["generated_sha256"]
    frame=pd.read_csv(file)
    if not np.array_equal(frame.row_id,np.arange(N)):
        raise ValueError("The requested row order was not respected")
    return frame.fe_index.to_numpy()


def generate():
    guard()
    assert not any_open() and not (HERE/"DRAW_CLOSURE.json").exists()
    authors=read(HERE/"AUTHORS.json")
    assert authors["freeze_sha256"]==sha(HERE/"FREEZE.json")
    bands,rho=baseline_fit()
    groups_by_seed={s:marginals(bands,s) for s in SEEDS}
    baseline_cells={}
    records={}
    for cid,a in [("statistical",None)]+[(u["author"],u) for u in authors["authors"]]:
        runs=[];arrays=[];reason=None
        if a is not None and not a["usable"]:
            records[cid]={"usable":False,"reason":"No executable submission","runs":[]}
            continue
        for seed,groups in groups_by_seed.items():
            try:
                ix=baseline_indices(groups,rho,seed) if a is None else sealed_draw(cid,groups,seed,a["law_sha256"])
                rows=pair(groups,ix)
                measure=endpoints(rows)
                if a is None:baseline_cells[seed]=measure["cells"]
                assert measure["cells"]==baseline_cells[seed]
                path=PRIVATE/"cohorts"/cid/f"{seed}.npy";path.parent.mkdir(parents=True,exist_ok=True)
                if path.exists():assert np.array_equal(np.load(path,allow_pickle=False),rows)
                else:np.save(path,rows,allow_pickle=False)
                runs.append({"seed":seed,"npy_sha256":sha(path),"estimates":measure});arrays.append(rows)
            except (ValueError,AssertionError,FileNotFoundError,RuntimeError) as exc:
                reason=type(exc).__name__+": "+str(exc)[:240]
                runs.append({"seed":seed,"error":reason})
        usable=len(arrays)==len(SEEDS)
        if a is None and not usable:raise RuntimeError("Statistical generator failed source-only checks")
        records[cid]={"usable":usable,"runs":runs,"reason":reason,"pooled":endpoints(np.vstack(arrays)) if usable else None}
    save(HERE/"DRAW_CLOSURE.json",{"utc":now(),"freeze_sha256":sha(HERE/"FREEZE.json"),"authors_sha256":sha(HERE/"AUTHORS.json"),
             "rho_statistical":rho,"models":records,"target_endpoints_opened":False})
    print("Sealed",sum(a["usable"] for a in records.values()),"laws including statistical arm.",flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("stage",choices=["freeze","construct","generate"])
    stage=parser.parse_args().stage
    {"freeze":freeze,"construct":construct,"generate":generate}[stage]()
