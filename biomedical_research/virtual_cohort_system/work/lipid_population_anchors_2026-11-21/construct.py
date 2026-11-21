"""Seal source information, collect bounded GPT programs and run the isolated marginals."""
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd

from common import (ALT, HERE, OLD, PROJECT, PRIVATE, SLOTS, STUDY_SEEDS, check_grid,
                    digest, measures, now, pairings, read, save, source, text_hash)

PILOT = HERE.parent / "evidence_composition_pilot_2026-11-16"
sys.path.insert(0, str(PILOT))
import pilot as harness

client = harness.client
client.CONFIGS["OA_SOL"] = {**client.CONFIGS["OA_SOL"],"effort":"medium"}
client.MAX_OUTPUT = 6000
client.CAPS = {"openai": .80}


def prompt():
    return "\n\n".join(p.read_text(encoding="utf-8") for p in
                        (HERE/"REQUEST.txt", OLD/"SOURCE.json", HERE/"US_SOURCE.json"))


def bindings():
    files = [HERE/f for f in ("PROTOCOL.md","REQUEST.txt","US_SOURCE.json","common.py","construct.py",
                              "survey.py","evaluate.py","fixtures.py")]
    files += [OLD/"SOURCE.json",OLD/"science.py",OLD/"MODEL_CLOSURE.json",ALT/"SENSITIVITY.json",
              HERE.parent/"prospective_lipid_use_2026-11-21/design.py",PILOT/"pilot.py",harness.WORKER,
              HERE.parent/"cross_model_api_pilot_2026-11-10/provider_client.py",PROJECT/"cohort_harness/execution.py"]
    return {f.relative_to(PROJECT).as_posix():text_hash(f) for f in files}


def execution_task(n):
    result = {"schema_version":1,"task_id":"historical_population_lipid_marginal_grid",
              "mode":"whole_cohort","population":"Quantile grid for an age-standardized US adult mixture",
              "row_id":"row_id","n_rows":n,"columns":[
                {"name":"row_id","unit":"","kind":"integer","role":"identifier","nullable":False},
                *[{"name":col,"unit":"mg/dL","kind":"number","role":"generated","nullable":False}
                  for col in ("tc_mg_dl","hdl_mg_dl")]],
              "information_policy":{"mode":"published_evidence","excluded_cohorts":[],"allowed_tools":[]},
              "budget":{"source_queries":0,"source_downloads":0,"revisions":0}}
    harness.contracts.validate_task(result)
    return result


def isolated_grid(code, model, seed, name, n):
    root = PRIVATE / "runs" / name / str(seed)
    cache = root/"result.json"
    if cache.exists():
        info = read(cache)
        if info["status"] != "success":
            raise RuntimeError(info["error"])
        array = root/"grid.npy"
        assert digest(array)==info["sha256"] and info["code_sha256"]==text_hash(root/"candidate/generator.py")
        assert code==(root/"candidate/generator.py").read_text(encoding="utf-8")
        return np.load(array,allow_pickle=False),info
    stage = root/"candidate"
    stage.mkdir(parents=True,exist_ok=False)
    entry = stage/"generator.py"
    entry.write_text(code,encoding="utf-8",newline="\n")
    tc, hdl = source.values(n)
    task = execution_task(n)
    save(stage/"model_spec.json", {"task":task,"model":model,"tc_mg_dl":tc.tolist(),"hdl_mg_dl":hdl.tolist()})
    try:
        report=harness.isolated(stage,task,root/"run",seed)
        if report["status"] != "success":
            file = root/"run/output/worker_report.json"
            detail = read(file).get("error", "") if file.is_file() and file.stat().st_size else report.get("error","")
            raise ValueError("Isolated execution failed: "+str(detail)[:450])
        csv=root/"run/output/generated.csv"
        assert digest(csv)==report["generated_sha256"]
        f=pd.read_csv(csv,float_precision="round_trip")
        assert list(f.columns)==["row_id","tc_mg_dl","hdl_mg_dl"] and np.array_equal(f.row_id,np.arange(n))
        array=f[["tc_mg_dl","hdl_mg_dl"]].to_numpy()
        check_grid(array)
        np.save(root/"grid.npy",array,allow_pickle=False)
        info={"status":"success","sha256":digest(root/"grid.npy"),"csv_sha256":digest(csv),
              "code_sha256":text_hash(entry),"seed":seed}
        save(cache,info)
        return array,info
    except (AssertionError,OSError,RuntimeError,ValueError) as exc:
        save(cache,{"status":"failed","error":repr(exc)[:550]})
        raise


def freeze():
    from fixtures import test
    if (HERE/"FREEZE.json").exists():
        raise FileExistsError("The design is already frozen")
    test()
    fixture = ("import numpy as np\nimport pandas as pd\n"
               "def generate(observed,spec,seed):\n"
               "    return pd.DataFrame({'row_id':np.arange(spec['task']['n_rows']),"
               "'tc_mg_dl':spec['tc_mg_dl'],'hdl_mg_dl':spec['hdl_mg_dl']})\n")
    grid,receipt=isolated_grid(fixture,{},11,"fixture",37)
    np.testing.assert_allclose(grid,np.column_stack(source.values(37)),rtol=2e-15)
    payload = json.dumps(client.make_request("OA_SOL",prompt())[1],ensure_ascii=False).encode()
    model=client.CONFIGS["OA_SOL"]
    reserved=((len(payload)+4096)*max(model["input_rate"], model["cache_write_rate"])+client.MAX_OUTPUT*model["output_rate"])/1e6
    assert len(SLOTS)*reserved<=client.CAPS["openai"]
    orders=pairings()
    assert all(len(v)==3 for v in orders.values())
    save(HERE/"FREEZE.json", {"utc":now(),"bindings":bindings(),"model":model,"authors":SLOTS,
         "budget_usd":client.CAPS["openai"],"max_output":client.MAX_OUTPUT,"allowance_each":reserved,"seeds":STUDY_SEEDS,
         "system":client.SYSTEM,"isolated_grid_fixture":receipt,"source_only":True,"joint_laws":list(orders)})
    print("Frozen source, scorer, nine inherited pairings and successful isolated fixture.")


def guard():
    f=read(HERE/"FREEZE.json")
    assert f["bindings"]==bindings() and f["model"]==client.CONFIGS["OA_SOL"]
    assert f["system"]==client.SYSTEM and f["budget_usd"]==client.CAPS["openai"]


def call(slot):
    folder=PRIVATE/"api/calls"/slot
    if folder.exists():
        if not (folder/"receipt.json").exists():
            raise RuntimeError("Call reservation already exists without a receipt")
        r=read(folder/"receipt.json")
    else:
        r,_=client.call_once(PRIVATE/"api",slot,"OA_SOL",prompt())
    keys=("status","requested_model","returned_model","artifact_status","mechanical_error","stop_reason","api_error_code",
          "started_utc","ended_utc","usage","request_sha256","response_text.txt_sha256","tariff_cost_usd")
    rec={k:r.get(k) for k in keys}
    if r.get("status")=="received" and r["returned_model"]==client.CONFIGS["OA_SOL"]["model"] and (folder/"artifact.json").exists():
        assert digest(folder/"artifact.json")==r["artifact.json_sha256"]
        obj=read(folder/"artifact.json")
        law=HERE/"laws"/slot
        law.mkdir(parents=True,exist_ok=True)
        f=law/"generator.py"
        if not f.exists():
            f.write_text(obj["generator_py"],encoding="utf-8",newline="\n")
        assert f.read_text(encoding="utf-8")==obj["generator_py"]
        save(law/"model.json",obj["model_spec"])
        save(law/"decision.json",obj["decision_record"])
        rec["law"]={k:text_hash(law/k) for k in ("generator.py","model.json","decision.json")}
    return slot,rec


def dispatch():
    guard()
    if (HERE/"AUTHORS.json").exists():raise FileExistsError("Authors are closed")
    with ThreadPoolExecutor(max_workers=len(SLOTS)) as pool:
        authors=dict(pool.map(call,SLOTS))
    save(HERE/"AUTHORS.json",{"utc":now(),"freeze_sha256":text_hash(HERE/"FREEZE.json"),"calls":authors})
    print([(k,r["status"],r["tariff_cost_usd"]) for k,r in authors.items()])


def close():
    guard()
    if (HERE/"PREDICTIONS.json").exists():raise FileExistsError("Predictions are closed")
    authors=read(HERE/"AUTHORS.json")
    assert authors["freeze_sha256"]==text_hash(HERE/"FREEZE.json")
    base=np.column_stack(source.values())
    historical=read(HERE/"US_SOURCE.json")
    means=np.array([historical[k]["mean"] for k in ("tc","hdl")])
    grids={"base":base,"statistical":base*(means/base.mean(axis=0))}
    records={}
    for name,rec in authors["calls"].items():
        if "law" not in rec:
            records[name]={"usable":False,"reason":"Missing validated submission"}
            continue
        path=HERE/"laws"/name
        assert all(text_hash(path/k)==v for k,v in rec["law"].items())
        try:
            runs=[isolated_grid((path/"generator.py").read_text(encoding="utf-8"),read(path/"model.json"),
                                seed,name,len(base)) for seed in STUDY_SEEDS]
            assert np.array_equal(runs[0][0],runs[1][0]),"Marginals changed with seed"
            grids[name]=runs[0][0]
            records[name]={"usable":True,"verification_runs":[r[1] for r in runs]}
        except (AssertionError,RuntimeError,OSError,ValueError) as exc:
            records[name]={"usable":False,"reason":repr(exc)[:550]}
    orders=pairings()
    predictions={}
    for method,grid in grids.items():
        check_grid(grid)
        cases={key:measures(grid,ix) for key,ix in orders.items()}
        predictions[method]={"marginal_means":grid.mean(axis=0).tolist(),"pairings":cases}
        for key,r in cases.items():
            first=predictions["base"]["pairings"][key]["values"]["rank_tc_hdl"]
            assert abs(first-r["values"]["rank_tc_hdl"])<1e-12
            assert abs(r["values"]["mean_nonhdl"]-np.mean(grid[:,0]-grid[:,1]))<1e-9
    save(HERE/"PREDICTIONS.json",{"utc":now(),"freeze_sha256":text_hash(HERE/"FREEZE.json"),
         "authors_sha256":text_hash(HERE/"AUTHORS.json"),"execution":records,"predictions":predictions,
         "new_target_outcomes_opened":False})
    print("Usable methods:",list(grids))


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("step",choices=("freeze","dispatch","close"))
    {"freeze":freeze,"dispatch":dispatch,"close":close}[ap.parse_args().step]()
