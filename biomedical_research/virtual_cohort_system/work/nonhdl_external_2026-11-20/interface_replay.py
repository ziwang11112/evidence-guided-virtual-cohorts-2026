import argparse
import hashlib
import json
import numpy as np
from pipeline import HERE,PRIVATE,SLOT,guarded,run_agent,now,txtsha,client
from science import N,SEEDS,paired,estimates,read,write,sha
from evaluate import characterize

def original():
    auth=read(HERE/"AUTHOR.json")
    assert not auth["usable"] and auth["mechanical_error"]=="decision_record is missing requested structural fields"
    path=PRIVATE/"api/calls"/SLOT/"response_text.txt"
    assert sha(path)==auth["response_text.txt_sha256"]
    raw=json.loads(path.read_text(encoding="utf8"));d=raw["decision_record"]
    view={**raw,"decision_record":{
        "structure":d["choice_and_evidence"],"parameter_provenance":[d["calibration"]],
        "requested_estimands":[d["scientific_uses"]],"limitations":d["transfer_limits"],
        "checks_actually_performed":[{"author_analytic_check_only":d["source_fit"],"finite_draw_check_by_author":False}]}}
    validated=client.parse_artifact(json.dumps(view,ensure_ascii=False))
    assert validated["generator_py"]==raw["generator_py"] and validated["model_spec"]==raw["model_spec"]
    return raw
def bindings():
    keys=["INTERFACE_ADDENDUM.md","interface_replay.py","verify_replay.py"]
    return {k:txtsha(HERE/k) for k in keys}
def freeze():
    guarded()
    assert not (HERE/"REFERENCE_OPEN.json").exists() and not (HERE/"MODEL_CLOSURE.json").exists()
    x=original()
    law=HERE/"law";law.mkdir(exist_ok=True)
    for k,key in (("model_spec.json","model_spec"),("decision.json","decision_record"),("generator.py","generator_py")):
        raw=x[key] if key=="generator_py" else json.dumps(x[key],indent=2,ensure_ascii=False)
        with (law/k).open("x",encoding="utf8",newline="\n") as f:f.write(raw)
    write(HERE/"INTERFACE_FREEZE.json",{"time_utc":now(),"original_freeze_sha256":sha(HERE/"FREEZE.json"),
            "raw_closure_sha256":sha(HERE/"CLOSURE.json"),"response_sha256":read(HERE/"AUTHOR.json")["response_text.txt_sha256"],
            "bindings":bindings(),"law_sha256":{k:sha(law/k) for k in ("generator.py","model_spec.json","decision.json")},
            "generator_string_sha256":hashlib.sha256(x["generator_py"].encode("utf8")).hexdigest(),"target_results_opened":False})
def guard_bridge():
    guarded();f=read(HERE/"INTERFACE_FREEZE.json")
    assert f["raw_closure_sha256"]==sha(HERE/"CLOSURE.json") and f["bindings"]==bindings()
    assert all(sha(HERE/"law"/k)==v for k,v in f["law_sha256"].items())
    return f
def draw():
    guard_bridge()
    assert not (HERE/"REFERENCE_OPEN.json").exists() and not (HERE/"MODEL_CLOSURE.json").exists()
    raw=original();outputs=[];errors=[];rows=[]
    for seed in SEEDS:
        try:
            ix,artifact=run_agent(raw["generator_py"],raw["model_spec"],seed,N,PRIVATE/f"replay-{seed}")
            x=paired(ix);m=estimates(x);path=PRIVATE/f"agent-{seed}.npy"
            assert not path.exists();np.save(path,x,allow_pickle=False)
            outputs.append({"seed":seed,"estimates":m,"array_sha256":sha(path),"permutation_csv_sha256":artifact});rows.append(x)
        except (AssertionError,ValueError,RuntimeError,OSError) as e:errors.append({"seed":seed,"reason":repr(e)[:850]})
    ok=len(rows)==len(SEEDS)
    write(HERE/"MODEL_CLOSURE.json",{"time_utc":now(),"interface_freeze_sha256":sha(HERE/"INTERFACE_FREEZE.json"),
          "raw_closure_sha256":sha(HERE/"CLOSURE.json"),"target_results_opened":False,
          "arms":{"agent":{"usable":ok,"runs":outputs,"errors":errors,"pooled":estimates(np.vstack(rows)) if ok else None},
                  "statistical":read(HERE/"CLOSURE.json")["arms"]["statistical"]}})
    print("Amended outputs sealed",ok,len(outputs),errors)
def score():
    guard_bridge();full=read(HERE/"MODEL_CLOSURE.json")
    assert full["interface_freeze_sha256"]==sha(HERE/"INTERFACE_FREEZE.json")
    assert read(HERE/"REFERENCE_OPEN.json")["first_access_utc"]>full["time_utc"]
    raw=read(HERE/"RESULTS.json");cohorts=raw["cohorts"]
    for site in cohorts.values():
        arm=full["arms"]["agent"]
        if not arm["usable"]:continue
        for d in arm["runs"]:assert sha(PRIVATE/f"agent-{d['seed']}.npy")==d["array_sha256"]
        e=arm["pooled"];c=site["reference"]
        it,status=characterize(e["tail_pct"],site["reference_ci"]["tail_pct"])
        gap=e["tail_pct"]-c["tail_pct"]
        site["arms"]["agent"]={"mean_gap_mg_dl":e["mean_mg_dl"]-c["mean_mg_dl"],
            "tail_gap_pp":gap,"abs_tail_gap_pp":abs(gap),"tail_gap_interval_pp":it,"planning_status":status}
    write(HERE/"REPLAY_RESULTS.json",{"cohorts":cohorts,"model_closure_sha256":sha(HERE/"MODEL_CLOSURE.json"),
          "original_results_sha256":sha(HERE/"RESULTS.json"),"raw_agent_usable":False})
    print("Scored both frozen comparisons.")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("step",choices=["freeze","draw","score"])
    {"freeze":freeze,"draw":draw,"score":score}[p.parse_args().step]()
