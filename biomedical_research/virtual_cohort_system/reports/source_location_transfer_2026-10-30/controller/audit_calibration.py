"""Independent controller recomputation of source-only scalar corrections."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text(encoding="utf-8-sig"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def require(v,m):
    if not v: raise ValueError(m)

def main():
    rows=[]
    for family in ["ha","hb"]:
        bundle=HERE/family; initial=bundle/"candidates/initial"
        p0=read(initial/"model_spec.json")["parameters"]
        key="location_pct" if family=="ha" else "location_by_sex"
        for arm in ["calibrated_primary","calibrated_alt1","calibrated_alt2"]:
            candidate=bundle/"candidates"/arm
            record=read(candidate/"calibration.json")
            require(record["source_seeds"]==[94101,94102,94103],"Source seed selection changed")
            require([x["seed"] for x in record["inputs"]]==record["source_seeds"],"Missing/duplicate source seed")
            frames=[]
            for item in record["inputs"]:
                path=(bundle/item["output_path"]).resolve()
                require(path.is_relative_to(bundle.resolve()),"Source path escapes bundle")
                require(sha(path)==item["sha256"],"Source output changed")
                frames.append(pd.read_csv(path,usecols=["sex","hba1c_pct"],float_precision="round_trip"))
            pool=pd.concat(frames,ignore_index=True)
            p1=read(candidate/"model_spec.json")["parameters"]
            require(sha(candidate/"generator.py")==sha(initial/"generator.py"),"Formula changed")
            require(sha(candidate/"evidence.json")==sha(initial/"evidence.json"),"Evidence changed")
            require({k:v for k,v in p0.items() if k!=key}=={k:v for k,v in p1.items() if k!=key},"Other parameter changed")
            for sex,expected in [("male",5.3),("female",5.2)]:
                vals=np.sort(pool.loc[pool.sex.eq(sex),"hba1c_pct"].to_numpy())
                n=len(vals); q=float((vals[(n-1)//2]+vals[n//2])/2)
                delta=expected-q
                require(abs(q-record["sex"][sex]["initial_pooled_median"])<1e-12,"Pooled median differs")
                require(abs(p1[key][sex]-(p0[key][sex]+delta))<1e-12,"Correction differs")
                rows.append({"family":family,"arm":arm,"sex":sex,"source_pooled_n":n,"source_median":q,"offset":delta,"verified":True})
    result={"scope":"Source-only recomputation; no target outcome read; inherited HbA1c source medians independently checked against source packet","checks":rows,"passed":len(rows)}
    with (HERE/"source_calibration_audit.json").open("x",encoding="utf-8") as f: json.dump(result,f,indent=2);f.write("\n")
    print(json.dumps({"independent_source_corrections_verified":len(rows)}))

if __name__=="__main__": main()
