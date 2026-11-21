"""Common source marginals, statistical comparator, and scientific estimators."""
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from scipy.special import ndtri

HERE=Path(__file__).resolve().parent
N=16000
SEEDS=(40711,40727,40739)
CUTOFF=160.0
TOLERANCE_PP=2.
def read(p):
    return json.loads(p.read_text(encoding="utf8"))
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,obj):
    with p.open("x",encoding="utf8",newline="\n") as f:
        json.dump(obj,f,ensure_ascii=False,allow_nan=False,indent=2);f.write("\n")
def fit_marginal(mean,cut,prob_below):
    z=ndtri(prob_below)
    discriminant=z*z-2*math.log(cut/mean)
    if discriminant<0: raise ValueError("Mean and quantile cannot fit a lognormal")
    roots=sorted(v for v in (z-math.sqrt(discriminant),z+math.sqrt(discriminant)) if v>0)
    if not roots: raise ValueError("Missing positive log scale")
    return float(roots[0]),[float(v) for v in roots]
def source_law():
    s=read(HERE/"SOURCE.json")
    mt,mh=(s[k]["estimate"] for k in ("tc_mean","hdl_mean"))
    st,tr=fit_marginal(mt,6.2,1-s["tc_high_pct"]["estimate"]/100)
    sh,hr=fit_marginal(mh,1.,s["hdl_low_pct"]["estimate"]/100)
    return {"means_mg_dl":[v*s["cholesterol_mg_dl_per_mmol_l"] for v in (mt,mh)],
            "log_sds":[st,sh],"admissible_log_sds":[tr,hr]}
def values(n=N):
    law=source_law()
    z=ndtri((np.arange(n,dtype=float)+.5)/n)
    x=np.exp(z[:,None]*np.array(law["log_sds"]))
    x*=np.array(law["means_mg_dl"])/x.mean(axis=0)
    return x[:,0].copy(),x[:,1].copy()
def gaussian_rho():
    l=source_law()
    st,sh=l["log_sds"]
    mt,mh=l["means_mg_dl"]
    r=read(HERE/"SOURCE.json")["mean_individual_ratio"]["estimate"]
    rho=(sh*sh-math.log(r*mh/mt))/(st*sh)
    if not -1<rho<1: raise ValueError("Published ratio incompatible with comparator")
    return rho
def stat_permutation(n,seed):
    rng=np.random.default_rng(seed)
    x,e=rng.standard_normal((2,n))
    r=gaussian_rho()
    h=r*x+math.sqrt(1-r*r)*e
    return np.argsort(np.argsort(h))[np.argsort(x)]
def paired(ix):
    t,h=values()
    ix=np.asarray(ix)
    if ix.shape!=(len(t),) or not np.issubdtype(ix.dtype,np.integer) or not np.array_equal(np.sort(ix),np.arange(len(t))):
        raise ValueError("Author must return a full integer permutation")
    return np.column_stack((t,h[ix]))
def estimates(x):
    t,h=x.T
    if len(t)==0 or not np.isfinite(x).all() or (x<=0).any():raise ValueError("Positive complete pairs required")
    d=t-h
    return {"mean_mg_dl":float(d.mean()),"tail_pct":float(100*(d>=CUTOFF).mean()),
            "n":len(t),"tail_count":int((d>=CUTOFF).sum()),"tc_below_hdl":int((d<0).sum()),
            "mean_tc_over_hdl":float(np.mean(t/h))}
def possible_counts(t,h,cut=CUTOFF):
    # Match each smallest still-unmatched challenge to the first viable larger value.
    t,h=np.sort(t),np.sort(h)+cut
    j=0
    for v in t:
        if j<len(h) and v>=h[j]:j+=1
    mx=j;j=0
    for v in h:
        if j<len(t) and t[j]<v:j+=1
    return len(t)-j,mx
