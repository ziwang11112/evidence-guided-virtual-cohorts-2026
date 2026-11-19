"""Second implementation of the threshold, rank, bridge, resampling and decision checks."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
PRIVATE=HERE/"private"


def load(path):
    return json.loads(path.read_text(encoding="utf8"))


def equal(x,y):
    if x is None or y is None:
        assert x is None and y is None
    else:
        np.testing.assert_allclose(x,y,atol=1e-11,rtol=1e-11)


def compute(frame):
    h,f=frame.hb_g_dl,frame.ferritin_ug_l
    low,dep=h.lt(12),f.lt(15)
    cells=np.bincount(2*(~low).to_numpy(dtype=int)+(~dep).to_numpy(dtype=int),minlength=4)
    odds=float(cells[0]*cells[3]/(cells[1]*cells[2])) if min(cells)>0 else None
    a=np.log(f[(h>=12)&(h<13)]); b=np.log(f[(h>=13)&(h<14)])
    rat=float(np.exp(b.sum()/len(b)-a.sum()/len(a))) if len(a) and len(b) else None
    return h.rank().corr(f.rank()),odds,rat,cells.tolist()


def weighted_rank(x, weights):
    _,inv=np.unique(x,return_inverse=True)
    mass=np.bincount(inv,weights=weights)
    return (np.cumsum(mass)-mass/2)[inv]


def repeat_boot(f,seed,ratio_only=False):
    rng=np.random.default_rng(seed)
    groups=[np.asarray(sorted(sub.commid.unique())) for _,sub in f.groupby("t1",sort=True)]
    unique,code=np.unique(f.commid.to_numpy(),return_inverse=True)
    h,fe=f.hb_g_dl.to_numpy(),f.ferritin_ug_l.to_numpy()
    cell=2*(h>=12).astype(int)+(fe>=15).astype(int)
    ratios=[]; odds=[]; ranks=[]
    for _ in range(2000):
        picked=np.concatenate([rng.choice(g,len(g),replace=True) for g in groups])
        weights=np.bincount(np.searchsorted(unique,picked),minlength=len(unique))[code]
        if ratio_only:
            a=(h>=12)&(h<13); b=(h>=13)&(h<14)
            ratios.append(np.exp(np.average(np.log(fe[b]),weights=weights[b])-np.average(np.log(fe[a]),weights=weights[a])))
        else:
            x=weighted_rank(h,weights)-weights.sum()/2
            y=weighted_rank(fe,weights)-weights.sum()/2
            ranks.append(np.sum(weights*x*y)/np.sqrt(np.sum(weights*x*x)*np.sum(weights*y*y)))
            c=np.bincount(cell,weights=weights,minlength=4)
            odds.append(c[0]*c[3]/(c[1]*c[2]) if min(c)>0 else np.nan)
    if ratio_only: return np.asarray(ratios)
    return np.asarray(ranks),np.asarray(odds)


def audit():
    results=load(HERE/"RESULTS.json")
    source=load(HERE/"SOURCE_CLOSURE.json")
    split=load(HERE/"PARTITION.json")
    a,b=[pd.read_csv(PRIVATE/(s+".csv")) for s in ("A","B")]
    assert set(a.commid).isdisjoint(b.commid)
    for s in ("A","B"):
        assert hashlib.sha256((PRIVATE/(s+".csv")).read_bytes()).hexdigest()==split["parts"][s]["sha256"]
    ar,ao,bridge,ac=compute(a)
    observed,odds,_,cells=compute(b)
    table=load(HERE/"A_TABLES.json")
    supplement=load(HERE/"A_SUPPLEMENT.json")
    assert ac==sum(table["table_1"]["counts"],[])
    equal(round(bridge,3),supplement["estimate"])
    equal(np.round(np.quantile(repeat_boot(a,191941,True),[.025,.975]),3),supplement["province_stratified_community_bootstrap_95pct"])
    equal(observed,results["reference"]["rank"]); equal(odds,results["reference"]["odds_ratio"])
    assert cells==results["reference"]["cells"]
    ranks,odds_boot=repeat_boot(b,191947)
    bounds=np.quantile(ranks,[.025,.975])
    equal(bounds,results["reference"]["rank_interval"]);equal(np.nanquantile(odds_boot,[.025,.975]),results["reference"]["odds_interval"])
    receipts=[]; draws=0; estimates={}
    for name,model in source["models"].items():
        if "receipt" in model:
            receipt=load(PRIVATE/"api"/"calls"/name/"receipt.json"); receipts.append(receipt)
            for field in ["request_sha256","prompt_sha256","tariff_cost_usd","usage","returned_model"]:
                assert receipt.get(field)==model["receipt"].get(field)
        if not model["usable"]: continue
        frames=[]
        for run in model["runs"]:
            path=PRIVATE/"runs"/name/str(run["seed"])/"output/generated.csv"
            assert hashlib.sha256(path.read_bytes()).hexdigest()==run["hash"]
            frames.append(pd.read_csv(path)); draws+=1
        estimated,model_odds,ratio,_=compute(pd.concat(frames,ignore_index=True))
        for key,value in [("rank",estimated),("odds_ratio",model_odds),("ratio",ratio)]:
            equal(model["metrics"][key],value)
        estimates[name]=(estimated, model_odds)
    for arm in ["ordinary","workflow"]:
        draws_bs=[];points=[];good=0
        for p,row in results["pairs"].items():
            if not p.startswith(arm) or not row["complete"]:continue
            first,old,new=[estimates[p+suffix] for suffix in ("","_control","_evidence")]
            for actual, key in [(first,"initial"),(old,"control"),(new,"evidence")]:
                equal(abs(actual[0]-observed),row["estimates"][key]["rank_error"])
            shift=abs(old[0]-observed)-abs(new[0]-observed)
            equal(shift,row["control_to_evidence"])
            swings=np.abs(old[0]-ranks)-np.abs(new[0]-ranks)
            equal(np.quantile(swings,[.025,.975]),row["control_to_evidence_B_sampling_interval"])
            draws_bs.append(swings);points.append(shift)
            guard=(min(cells)>=10 and new[1] is not None and old[1] is not None and 1/1.5<=new[1]/odds<=1.5 and 1/1.2<=new[1]/old[1]<=1.2)
            good+=int(guard and abs(new[0]-observed)<=.10)
        group=results["arms"][arm]
        assert group["complete_pairs"]==len(points) and group["final_rank_and_guard_passes"]==good
        if points:
            point=np.median(points); ri=np.quantile(np.median(draws_bs,axis=0),[.025,.975])
            equal(point,group["median_incremental_gain"]);equal(ri,group["median_incremental_B_sampling_interval"])
            assert group["material_benefit_rule_pass"]==bool(len(points)==3 and point>=.05 and ri[0]>0 and good>=2 and np.ptp(bounds)/2<=.10)
    equal(sum(q.get("tariff_cost_usd") or 0 for q in receipts),results["tariff_usd"])
    assert len(receipts)==results["api_calls"]
    out={"verified":True,"actual_calls":len(receipts),"successful_table_hashes_and_analyses":draws,
         "A_conditional_interval_and_B_rank_OR_intervals_recomputed":True,"bootstrap_per_partition":2000,
         "paired_error_contrasts_and_materiality_rules_recomputed":True,"new_model_calls":0}
    print(json.dumps(out,indent=2))
    if not (HERE/"VERIFICATION.json").exists():
        with (HERE/"VERIFICATION.json").open("x",encoding="utf8",newline="\n") as f: json.dump(out,f,indent=2)


if __name__=="__main__":
    audit()
