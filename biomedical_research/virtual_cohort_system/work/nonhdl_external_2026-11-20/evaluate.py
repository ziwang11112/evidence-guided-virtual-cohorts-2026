"""Reveal target outcomes only after the common study and all draws have been sealed."""
import os
import subprocess
import sys
import numpy as np
from pipeline import HERE,PRIVATE,guarded,now
from science import CUTOFF,TOLERANCE_PP,estimates,read,sha,write

BOOT_SEEDS={"mekelle":404203,"workers":404207}
def interval(a,tc,hdl,seed):
    rng=np.random.default_rng(seed)
    d=tc-hdl
    groups=[idx for idx in (np.where(a<40)[0],np.where(a>=40)[0]) if len(idx)]
    means=[];tails=[]
    for _ in range(2000):
        ix=np.concatenate([rng.choice(g,size=len(g),replace=True) for g in groups])
        means.append(d[ix].mean());tails.append(100*np.mean(d[ix]>=CUTOFF))
    return {"mean_mg_dl":np.percentile(means,[2.5,97.5]).tolist(),
            "tail_pct":np.percentile(tails,[2.5,97.5]).tolist()}
def characterize(estimate,ci):
    lo,hi=float(estimate-ci[1]),float(estimate-ci[0])
    if lo>=-TOLERANCE_PP and hi<=TOLERANCE_PP:status="within"
    elif lo>TOLERANCE_PP or hi< -TOLERANCE_PP:status="outside"
    else:status="unresolved"
    return [lo,hi],status
def main():
    guarded();seal=read(HERE/"CLOSURE.json")
    assert sha(HERE/"FREEZE.json")==seal["freeze_sha256"] and sha(HERE/"AUTHOR.json")==seal["author_sha256"]
    for arm,record in seal["arms"].items():
        for run in record["runs"]:
            assert sha(PRIVATE/f"{arm}-{run['seed']}.npy")==run["array_sha256"]
    opened=HERE/"REFERENCE_OPEN.json"
    if not opened.exists():
        write(opened,{"first_access_utc":now(),"freeze_sha256":seal["freeze_sha256"],"closure_sha256":sha(HERE/"CLOSURE.json")})
    assert read(opened)["closure_sha256"]==sha(HERE/"CLOSURE.json")
    if os.name=="nt":
        cmd=["wsl","-e","env","PYTHONPATH="+os.environ.get("NONHDL_WSL_LIB","/tmp/kdd-nonhdl-readers"),"python3","reference.py","export"]
    else:cmd=[sys.executable,"reference.py","export"]
    subprocess.run(cmd,cwd=HERE,check=True)
    results={}
    for name,seed in BOOT_SEEDS.items():
        a,tc,h=np.load(PRIVATE/f"{name}-eligible.npy",allow_pickle=False).T
        m=estimates(np.column_stack((tc,h)));ci=interval(a,tc,h,seed)
        entry={"n":len(a),"reference":m,"reference_ci":ci,"arms":{}}
        for arm,record in seal["arms"].items():
            if not record["usable"]:
                entry["arms"][arm]={"status":"failed"};continue
            g=record["pooled"]
            err_ci,status=characterize(g["tail_pct"],ci["tail_pct"])
            gap=g["tail_pct"]-m["tail_pct"]
            entry["arms"][arm]={"mean_gap_mg_dl":g["mean_mg_dl"]-m["mean_mg_dl"],"tail_gap_pp":gap,
                "abs_tail_gap_pp":abs(gap),"tail_gap_interval_pp":err_ci,"planning_status":status}
        results[name]=entry
    report={"freeze_sha256":seal["freeze_sha256"],"closure_sha256":sha(HERE/"CLOSURE.json"),"cohorts":results}
    if (HERE/"RESULTS.json").exists():assert read(HERE/"RESULTS.json")==report
    else:write(HERE/"RESULTS.json",report)
    print(report)
if __name__=="__main__":main()
