"""Check the prospective results independently using the original S dump and frequency-weighted ranks.
Run after closure and disclosure. Downloads only the official S dump if the local copy is missing.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import urllib.request

import numpy as np

HERE=Path(__file__).resolve().parent
IDS=("mean_nonhdl","mean_ratio","tc_high","hdl_low","nonhdl160","rank_tc_hdl")
TOL=np.array([10.,.30,5.,5.,2.,.10])
SEEDS={"all":711209,"Buckingham":711211,"Louisa":711217}


def read(p):
    return json.loads((HERE/p).read_text(encoding="utf-8"))


def same(a,b):
    np.testing.assert_allclose(a,b,rtol=2e-10,atol=2e-10)


def s_column(lines,key):
    at=lines.index(key)
    segment=lines[at+1:];first=segment.index(".Data")
    n=int(segment[first+2])
    col=np.array([float(s) if s not in ("N","NA","NaN") else np.nan for s in segment[first+3:first+3+n]])
    if key!="location":
        return col
    pos=segment.index(".Label")
    labels=segment[pos+3:pos+3+int(segment[pos+2])]
    return np.array([labels[int(i)-1] if np.isfinite(i) else "" for i in col])


def native_records(path):
    lines=path.read_text(encoding="latin-1").splitlines()
    ids,age,tc,hdl,location=[s_column(lines,k) for k in ("id","age","chol","hdl","location")]
    duplicate_counts=Counter(ids.tolist())
    elig=np.isfinite(age)&(age>=20)&np.isfinite(tc)&(tc>0)&np.isfinite(hdl)&(hdl>0)&np.isfinite(ids)
    elig&=np.array([duplicate_counts[x]==1 and loc in SEEDS and loc!="all" for x,loc in zip(ids,location)])
    return {k:np.column_stack((tc[elig&(location==k)],hdl[elig&(location==k)])) for k in sorted(SEEDS) if k!="all"}


def weight_evaluator(observations):
    t,h=observations.T
    n=len(t)
    features=np.column_stack((t-h,t/h,100*(t>=6.2*38.67),100*(h<38.67),100*((t-h)>=160)))
    codes=[np.unique(v,return_inverse=True)[1] for v in (t,h)]
    def evaluate(weights):
        out=np.empty((len(weights),6))
        out[:,:5]=(weights@features)/n
        for i,w in enumerate(weights):
            ranks=[]
            for idx in codes:
                freq=np.bincount(idx,weights=w)
                centered=(np.cumsum(freq)-.5*freq-.5*n)[idx]
                ranks.append(centered)
            x,y=ranks
            out[i,5]=np.dot(w,x*y)/np.sqrt(np.dot(w,x*x)*np.dot(w,y*y))
        return out
    return evaluate


def check_region(groups,seed,report):
    n=sum(map(len,groups))
    assert n==report["n"]
    data=np.concatenate(groups)
    assert int((data[:,1]>data[:,0]).sum())==report["hdl_above_tc"]
    calculate=weight_evaluator(data)
    point=calculate(np.ones((1,n)))[0]
    rng=np.random.default_rng(seed)
    blocks=[]
    for _ in range(40):
        start=0
        draws=[]
        for g in groups:
            draws.append(start+rng.integers(0,len(g),(100,len(g))))
            start+=len(g)
        indices=np.concatenate(draws,axis=1)
        freq=np.array([np.bincount(row,minlength=n) for row in indices])
        blocks.append(calculate(freq))
    low,high=np.quantile(np.concatenate(blocks),[.025,.975],axis=0)
    for scale_key,items in report["scales"].items():
        for j,k in enumerate(IDS):
            e=items[k]
            same(point[j],e["measured"])
            same([low[j],high[j]],e["measured_ci"])
            diff=e["virtual"]-point[j]
            intv=[e["virtual"]-high[j],e["virtual"]-low[j]]
            tol=float(scale_key)*TOL[j]
            same(intv,e["difference_ci"])
            same(diff,e["difference"])
            same(abs(diff)/tol,e["absolute_error_in_tolerances"])
            assert e["status"]==("within" if max(abs(x) for x in intv)<=tol else
                                  "contradicted" if (intv[1]<-tol or intv[0]>tol) else "unresolved")
    return n


def check_public():
    res,seal,freeze,pack=map(read,["RESULTS.json","DECISION_CLOSURE.json","FREEZE.json","PACKET.json"])
    cases=pack["cases"]
    st=read("STATISTICAL_DECISION.json")
    sr={}
    for k,p in cases.items():
        v=p["common_virtual"]
        excursions=[abs(x-v) for x in p["previous_external_measurements"].values()]
        excursions.extend(abs(z[k]-v) for z in pack["all_laws"].values())
        if p["source_report"]:
            excursions.extend(abs(y-p["source_report"]["point"]) for y in p["source_report"]["ci95"])
        sr[k]=max(excursions)/p["tolerance"]
        same(sr[k],st["uses"][k]["score"])
        assert (sr[k]<=1)==st["uses"][k]["endorse"]
    assert st["ranking"]==sorted(IDS,key=lambda k:(sr[k],IDS.index(k)))
    assignments=seal["sessions"]
    assert len(assignments)==8 and Counter(s["arm"] for s in assignments.values())=={"reduced":4,"full":4}
    rules={k:r["decision"] for k,r in assignments.items() if r["valid"]}
    rules["statistical"]=st
    amount=0.
    for record in assignments.values():
        r=record["receipt"]
        if r["usage"] is not None:
            i=r["usage"];c=freeze["model"]; cached=i["cached"]; written=i["cache_write"]
            charge=((i["input"]-cached-written)*c["input_rate"]+cached*c["cached_rate"]+
                    written*c["cache_write_rate"]+i["output"]*c["output_rate"])/1e6
            same(charge,r["tariff_cost_usd"])
            amount+=charge
    same(amount,res["tariff_usd"])
    assert res["valid_slots"]+1==len(rules)
    for loc,r in res["estimates"].items():
        for scale,rows in r["scales"].items():
            for k,decision in rules.items():
                scores=res["scores"][loc][scale][k]
                for top in range(1,len(IDS)+2):
                    uses=decision["ranking"][:top] if top<=len(IDS) else [u for u in IDS if decision["uses"][u]["endorse"]]
                    x=scores["at_coverage"][str(top)] if top<=len(IDS) else scores["unforced"]
                    assert x["n"]==len(uses)
                    counts=Counter(rows[u]["status"] for u in uses)
                    assert all(x[s]==counts[s] for s in ("contradicted","within","unresolved"))
                    if uses:
                        same(np.mean([rows[u]["absolute_error_in_tolerances"] for u in uses]),x["mean_error_in_tolerances"])
                    else:
                        assert x["mean_error_in_tolerances"] is None
    return res


def main(public_only):
    assert (HERE/"REFERENCE_OPEN.json").exists(), "Reference has not been opened"
    res=check_public()
    if public_only:
        print("Public-only scores, statistical ranking, all coverages, tolerances and API accounting agree.")
        return
    adm=read("ADMISSION.json")
    native=HERE/"private/virginia.sdd"
    if not native.exists():
        native.parent.mkdir(exist_ok=True)
        with urllib.request.urlopen(adm["native_S_dump"],timeout=30) as response:
            native.write_bytes(response.read(1_000_001))
    assert hashlib.sha256(native.read_bytes()).hexdigest()==adm["sdd_sha256"]
    groups=native_records(native)
    n_by={name:check_region(list(groups.values()) if name=="all" else [groups[name]],seed,res["estimates"][name])
          for name,seed in SEEDS.items()}
    receipt={"unique_reference_n":n_by["all"],"n_by_region":n_by,"uses":len(IDS),"tolerance_scales":3,
             "rank_ci_recomputed_with_frequency_weighted_ties":True,
             "bootstrap_replicates_each_region":4000,"public_rules_checked":res["valid_slots"]+1,
             "valid_agent_sessions":res["valid_slots"],"independently_priced_usd":res["tariff_usd"],
             "all_results_and_costs_match":True}
    path=HERE/"VERIFICATION.json"
    if path.exists():
        assert read("VERIFICATION.json")==receipt
    else:
        with path.open("x",encoding="utf-8",newline="\n") as f:
            json.dump(receipt,f,indent=2);f.write("\n")
    print(json.dumps(receipt))


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--public-only",action="store_true")
    main(ap.parse_args().public_only)
