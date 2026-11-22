"""Two blood analytes. Cross-tabulation fixes the crude odds ratio, pairing can change ranks."""
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

HERE=Path(__file__).resolve().parent
WORK=HERE.parents[1]
PAPER=WORK/"original_paper_capability_2026-11-17/private_sources/iron_original.layout.txt"
PDF=PAPER.with_name("iron_original.pdf")
DOI="10.1024/0300-9831/a000014"
MARGIN=.10
SEED_MARGIN=.05
SEEDS=(523301,523307,523309)
BOUND_FILES=(PAPER,PDF)
KINDS=("severe","intermediate","nonanemic")
REQUESTED="continuous Hb–ferritin rank correlation"
FIXED="crude anemia odds ratio"
K=10


def article():
    return PAPER.read_text(encoding="utf8").replace("\f","\n\n[Page break]\n\n")


def reference():return json.loads((HERE/"SOURCE.json").read_text(encoding="utf8"))


def extraction(spec):
    ref=reference()
    errs=[]
    for k,v in ref["units"].items():
        if spec.get(k)!=v:errs.append(k)
    if spec.get("tables")!=ref["table_operators"]:errs.append("table_operators")
    ev=spec.get("evidence")
    if not isinstance(ev,dict):return ["evidence"]+errs
    for k,v in ref["quantities"].items():
        provided=ev.get(k)
        if isinstance(v,list):
            ok=isinstance(provided,list) and len(v)==len(provided) and all(type(x) in (float,int) and abs(x-y)<1e-8 for x,y in zip(provided,v))
        else:ok=type(provided) in (float,int) and abs(provided-v)<1e-8
        if not ok:errs.append(k)
    return errs


def geometric(values,weights):
    return float(np.exp(np.average(np.log(values),weights=weights)))


def groups(spec):
    e=spec["evidence"];counts=np.array(e["n_by_band"],dtype=float)
    if counts.shape!=(3,) or not np.all(counts==counts.astype(int)) or not np.all(counts>0) or counts.sum()>5000:
        raise ValueError("Invalid three source band counts")
    counts=counts.astype(int)
    if int(sum(counts))!=e["n_total"]:raise ValueError("Inconsistent sample size")
    gm=np.array(e["fe_gm_by_band"],dtype=float)
    if gm.shape!=(3,) or not np.all(gm>.05):raise ValueError("Invalid ferritin band geometric means")
    lo=max(geometric(gm-.05,counts),e["fe_gm"]-.05)
    hi=min(geometric(gm+.05,counts),e["fe_gm"]+.05)
    if not lo<hi:raise ValueError("Overall and within-band geometric means have disjoint rounding bins")
    left,right=-.05,.05
    for _ in range(54):
        h=(left+right)/2
        if geometric(gm+h,counts)<(lo+hi)/2:left=h
        else:right=h
    gm=gm+(left+right)/2
    a,b,c=e["severe_cut"],e["anemia_cut"],e["iron_cut"]
    if not (0<a<b and c>0):raise ValueError("Invalid cutoffs")
    depleted0=round(counts[0]*e["depleted_pct_by_band"][0]/100)
    counts_low=np.array([depleted0,e["anemic_low"]-depleted0,e["nonanemic_low"]])
    if not np.all(counts_low==counts_low.astype(int)) or np.any(counts_low<=0) or np.any(counts_low>=counts):
        raise ValueError("Invalid depleted counts")
    lo_x=(.60*a,a,b)
    high_gm=np.exp((sum(counts)*np.log(e["hb_gm"])-counts[0]*np.log(np.sqrt(.60)*a)-
                    counts[1]*np.log(np.sqrt(a*b)))/counts[2])
    hi_x=(a,b,high_gm**2/b)
    def midpoint(n):return (np.arange(n)+.5)/n
    out=[]
    for j,k in enumerate(KINDS):
        n=int(counts[j])*K;m=int(counts_low[j])*K
        x=lo_x[j]*np.exp(np.log(hi_x[j]/lo_x[j])*midpoint(n))
        w=m/n; base=.95
        shift=np.log(gm[j]/c)-.5*base*(1-2*w)
        width_low=base+2*max(-shift,0)/w
        width_hi=base+2*max(shift,0)/(1-w)
        low=c*np.exp((midpoint(m)-1)*width_low)
        high=c*np.exp(midpoint(n-m)*width_hi)
        out.append((k,x,np.r_[low,high]))
    return out


def stats(g,orders):
    y=[j[2][o] for j,o in zip(g,orders,strict=True)]
    x=np.concatenate([j[1] for j in g]); all_y=np.concatenate(y)
    a,b=(x<120),(all_y<15)
    cells=[int(np.count_nonzero(u&v)) for u,v in [(a,b),(a,~b),(~a,b),(~a,~b)]]
    if min(cells)==0:raise ValueError("Odds ratio is undefined")
    return {"fixed":cells[0]*cells[3]/(cells[1]*cells[2]),
            "requested":float(np.corrcoef(rankdata(x),rankdata(all_y))[0,1]),
            "positive":bool(min(x)>0 and min(all_y)>0),"cells":cells,"hb_gm":float(np.exp(np.mean(np.log(x)))),
            "fe_gm":float(np.exp(np.mean(np.log(all_y)))),"bands":[len(j) for j in y],
            "depleted_pct":[float(100*np.mean(j<15)) for j in y],
            "band_fe_gm":[float(np.exp(np.mean(np.log(j)))) for j in y]}


def failures(v):
    e=reference()["quantities"]
    failed=[]
    counts=[e[k]*K for k in ("anemic_low","anemic_high","nonanemic_low","nonanemic_high")]
    if v["cells"]!=counts:failed.append("threshold_cells")
    if v["bands"]!=[m*K for m in e["n_by_band"]]:failed.append("hb_band_sizes")
    if not v["positive"]:failed.append("positive_analytes")
    targets=[("hb_gm",v["hb_gm"],e["hb_gm"],.1),("fe_gm",v["fe_gm"],e["fe_gm"],.1)]
    for i in range(3):
        targets.append(("band_geometric_mean_"+str(i),v["band_fe_gm"][i],e["fe_gm_by_band"][i],.1))
        targets.append(("depletion_percent_"+str(i),v["depleted_pct"][i],e["depleted_pct_by_band"][i],1 if i==1 else .1))
    for k,actual,t,s in targets:
        if not t-s/2<=actual<t+s/2:failed.append(k)
    return failed


def fixture():
    r=reference(); spec={**r["units"],"tables":r["table_operators"],"evidence":r["quantities"]}
    g=groups(spec)
    assert not extraction(spec) and len(g)==3
    y=np.concatenate([z for _,_,z in g])
    assert len(y)==16710 and all(np.all(np.diff(z)>0) and np.all(np.diff(x)>0) for _,x,z in g)
    weighted=geometric(np.array(r["quantities"]["fe_gm_by_band"]),[53,205,1413])
    assert weighted < 17.35 and 17.35<=np.exp(np.mean(np.log(y)))<17.45
    counts=[np.count_nonzero(z<15) for _,_,z in g]
    assert counts==[500,1230,3310]
    return {"source_table_rounding_verified":True,"scaled_cell_counts_checked":True,
            "weighted_GM_at_printed_centres":weighted,"chosen_coherent_overall_ferritin_GM":float(np.exp(np.mean(np.log(y))))}
