"""Separate prospective mechanical recovery. The original protocol and failures are retained."""
import ast
import sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
import study
import scoring

root=study.ROOT
read,write=study.read,study.write


def registered():
    rec=read(root/"INTERFACE_FREEZE.json")
    for f,h in rec["files_lf_sha256"].items():
        study.check(study.lfsha(root/f)==h,"Interface addendum changed")
    study.check(rec["parent_closure_lf_sha256"]==study.lfsha(root/"PARENT_CLOSURE.json"),"Parent closure mismatch")


def register():
    study.bound()
    study.check(not (root/"DRAW_CLOSURE.json").exists() and not (root/"REFERENCE_OPEN.json").exists(),"Already opened")
    study.check(not (study.PRIVATE/"runs").exists(),"Draws already started")
    write(root/"INTERFACE_FREEZE.json",{"time_utc":study.sandbox.now(),"parent_closure_lf_sha256":study.lfsha(root/"PARENT_CLOSURE.json"),
        "inspected":"JSON nesting, declared labels, cells and parameter reads in three primary artifacts only",
        "target_outcomes_read":False,"candidate_scientific_outputs_read":False,
        "files_lf_sha256":{f:study.lfsha(root/f) for f in ["INTERFACE_ADDENDUM.md","interface_bridge.py"]}})


def serialized_parameters(cid, runs):
    if cid=="statistical" or len(runs)!=3 or any(r["status"]=="success" for r in runs): return None
    reports=[read(study.PRIVATE/"runs"/cid/str(r["seed"])/"output/worker_report.json") for r in runs]
    if any(r.get("error_type")!="KeyError" for r in reports) or len({r.get("error") for r in reports})!=1: return None
    try: key=ast.literal_eval(reports[0]["error"])
    except (ValueError,SyntaxError): return None
    obj=read(study.CALLS/"calls"/cid/"artifact.json")
    model=obj["model_spec"]; nested=model.get("model")
    if not isinstance(key,str) or not isinstance(nested,dict) or key in model or key not in nested: return None
    code=ast.parse(obj["generator_py"])
    if not any(isinstance(x,ast.Subscript) and isinstance(x.slice,ast.Constant) and x.slice.value==key for x in ast.walk(code)): return None
    return key,nested


def run():
    registered(); study.bound()
    study.check(not (root/"REFERENCE_OPEN.json").exists(),"Target already opened")
    original=read(root/"DRAW_CLOSURE.json")["runs"]; raw=read(root/"SOURCE_RESULTS.json")
    def one(item):
        cid,runs=item; path=study.PRIVATE/"candidates"/cid
        if all(r["status"]=="success" for r in runs): return cid,{"binding":"original","draws":runs}
        qualified=serialized_parameters(cid,runs)
        if qualified is None:return cid,{"binding":"unresolved","draws":runs}
        key,params=qualified; dest=study.PRIVATE/"bridge_candidates"/cid
        dest.mkdir(parents=True,exist_ok=True)
        sam=dest/"generator.py"
        if not sam.exists(): sam.write_bytes((path/"generator.py").read_bytes())
        study.check(study.sha(sam)==study.sha(path/"generator.py"),"Code changed")
        spec={"task":study.task(),"model":params}
        if not (dest/"model_spec.json").exists():write(dest/"model_spec.json",spec)
        study.check(read(dest/"model_spec.json")==spec,"Parameter values changed")
        outputs=[]
        for seed in study.seeds(cid):
            loc=study.PRIVATE/"bridge_runs"/cid/str(seed)
            if loc.exists():study.check((loc/"execution.json").exists(),"Unclosed existing worker")
            rec=read(loc/"execution.json") if loc.exists() else study.sandbox.isolated(dest,study.task(),loc,seed)
            outputs.append({"seed":seed,"status":rec["status"],"sha256":rec.get("generated_sha256"),"error":rec.get("error")})
        return cid,{"binding":"one_nested_model","key_at_failure":key,"draws":outputs,"unchanged_code_sha256":study.sha(sam)}
    with ThreadPoolExecutor(2) as pool: runs=dict(pool.map(one,original.items()))
    write(root/"INTERFACE_CLOSURE.json",{"time_utc":study.sandbox.now(),"raw_source_results_lf_sha256":study.lfsha(root/"SOURCE_RESULTS.json"),"laws":runs})
    laws={}
    for cid,record in runs.items():
        original_law=raw["laws"][cid]
        if record["binding"] in ("original","unresolved"):
            laws[cid]=original_law
        else:
            frame=scientific_rows(cid,record)
            new=scoring.assess(frame) if frame is not None else {"tier1":False,"tier2":False,"execution":"incomplete"}
            for k in ("forecast","extracted_cells"):
                if k in original_law:new[k]=original_law[k]
            laws[cid]=new
    pairs=[]
    for row in raw["pairs"]:
        p,b=row["primary"],row["branch"]
        a,z=laws.get(p,{}),laws.get(p+"_"+b,{})
        result={"primary":p,"branch":b,"both_tier2":bool(a.get("tier2") and z.get("tier2"))}
        if "spearman" in a and "spearman" in z:
            gap=abs(a["spearman"]-z["spearman"]); margin=1.96*np.hypot(a["rank_mcse"],z["rank_mcse"])
            result.update(rank_gap=gap,mc_margin=margin,mc_lower=max(0.,gap-margin))
        pairs.append(result)
    write(root/"SCIENTIFIC_RESULTS.json",{"time_utc":study.sandbox.now(),"interface_closure_lf_sha256":study.lfsha(root/"INTERFACE_CLOSURE.json"),
          "laws":laws,"pairs":pairs,"calls":raw["calls"],"known_tariff_cost_usd":raw["known_tariff_cost_usd"]})


def scientific_rows(cid,record):
    if record["binding"]=="original":return study.rows(cid)
    frames=[]
    for r in record["draws"]:
        if r["status"]!="success":return None
        p=study.PRIVATE/"bridge_runs"/cid/str(r["seed"])/"output/generated.csv"
        study.check(study.sha(p)==r["sha256"],"Unbound corrected draw")
        frames.append(pd.read_csv(p))
    return pd.concat(frames,ignore_index=True)


if __name__=="__main__":
    {"register":register,"run":run}[sys.argv[1]]()
