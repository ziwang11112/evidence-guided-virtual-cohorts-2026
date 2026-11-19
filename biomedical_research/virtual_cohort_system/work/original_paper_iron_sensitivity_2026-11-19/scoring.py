"""Frozen source checks and survey-weighted analysis of the same two scientific questions."""
import numpy as np
import pandas as pd
from scipy.stats import spearmanr


COUNTS = np.array([173, 85, 331, 1082])
GROUPS = np.array([53, 205, 1413])
RATES = [0.943, 0.600, 0.234]
GEOMEANS = [1.3, 5.9, 22.3]
SOURCE_OR = COUNTS[0] * COUNTS[3] / (COUNTS[1] * COUNTS[2])


def cells(h, f, w):
    a, b = h < 12, f < 15
    return np.array([w[a & b].sum(), w[a & ~b].sum(), w[~a & b].sum(), w[~a & ~b].sum()])


def midcdf(x, weights):
    _, inv = np.unique(x, return_inverse=True)
    mass = np.bincount(inv, weights)
    return (np.cumsum(mass) - mass / 2)[inv] / mass.sum()


def questions(h, f, weights=None):
    h, f = np.asarray(h), np.asarray(f)
    w = np.ones(len(h)) if weights is None else np.asarray(weights, dtype=float)
    c = cells(h, f, w)
    if weights is None:
        corr = spearmanr(h, f).statistic
    else:
        x, y = midcdf(h,w)-0.5, midcdf(f,w)-0.5
        denom = np.sqrt(np.sum(w*x*x)*np.sum(w*y*y))
        corr = np.sum(w*x*y)/denom if denom else np.nan
    odds = (c[0]*c[3])/(c[1]*c[2]) if np.all(c > 0) else None
    return (float(odds) if odds is not None else None, float(corr))


def assess(frame):
    h, f = (frame[k].to_numpy() for k in ("hb_g_dl", "ferritin_ug_l"))
    if not (np.isfinite(h).all() and np.isfinite(f).all() and (h>0).all() and (f>0).all()):
        return {"valid_measurements":False, "tier1":False, "tier2":False}
    result = {}
    def put(key, est, target, limit, err):
        result[key] = {"draw":float(est), "source":float(target), "allowance_on_test_scale":float(limit),
                       "pass":bool(abs(err)<=limit)}
    def freq(key, x, total, target, floor):
        put(key, x/total, target, floor+4*np.sqrt(target*(1-target)/total), x/total-target)
    def gm(key, data, target, precision):
        if not len(data):
            result[key]={"pass":False, "reason":"empty subgroup"}
            return
        z=np.log(data); avg=z.mean(); se=z.std(ddof=1)/np.sqrt(len(z)) if len(z)>1 else 0
        put(key,np.exp(avg),target,0.05+precision/target+4*se,avg-np.log(target))
    c = cells(h,f,np.ones(len(h)))
    for i in range(4):
        freq(f"cell_{i}",c[i],len(h),COUNTS[i]/1671,0.003)
    band = (h>=10).astype(int)+(h>=12).astype(int)
    for i in range(3):
        fi=f[band==i]; freq(f"band_{i}",len(fi),len(h),GROUPS[i]/1671,0.003)
        if len(fi):
            freq(f"depleted_in_{i}",(fi<15).sum(),len(fi),RATES[i],0.0105)
        else: result[f"depleted_in_{i}"]={"pass":False,"reason":"empty subgroup"}
        gm(f"ferritin_gm_{i}",fi,GEOMEANS[i],0.05)
    gm("overall_hb_gm",h,12.99,0.005); gm("overall_ferritin_gm",f,17.4,0.05)
    odds,r=questions(h,f)
    if odds is None:
        result["log_or"]={"pass":False,"reason":"empty cell"}
    else:
        put("log_or",np.log(odds),np.log(SOURCE_OR),0.04+4*np.sqrt(np.sum(1/c)),np.log(odds/SOURCE_OR))
    blocks=np.array_split(np.arange(len(h)),60)
    se=float(np.std([spearmanr(h[idx], f[idx]).statistic for idx in blocks],ddof=1)/np.sqrt(len(blocks)))
    return {"valid_measurements":True,"n":len(h),"odds_ratio":odds,"spearman":r,"rank_mcse":se,
            "tier1":all(result[k]["pass"] for k in ["cell_0","cell_1","cell_2","cell_3","log_or"]),
            "tier2":all(v["pass"] for v in result.values()),"checks":result}


def reference_from(frame):
    eligible = ((frame.SUBJ==2)&(frame.SEX==2)&frame.AGE_MOTHER.between(18,49)&
                (frame.PREG==2)&(frame.LACT==2)&(frame.SEASON==2))
    d=frame.loc[eligible].copy()
    if d.ID_SUBJ.duplicated().any(): raise ValueError("Duplicate eligible ID; cannot apply frozen rule")
    fields=["BIO_HB","BIO_FERRIT","SAMPLE_WEIGHT"]
    m=np.isfinite(d[fields]).all(axis=1)&(d[fields]>0).all(axis=1)
    d=d.loc[m]
    h,f,w=[d[k].to_numpy(float) for k in fields]
    strata=[]
    for _,g in d.groupby("PROVINCE"):
        strata.append([np.flatnonzero(d.index.isin(t.index)) for _,t in g.groupby(["AIRESANT","VILLAGE"])])
    rng=np.random.default_rng(191137); samples=[]
    for _ in range(4000):
        sel=np.concatenate([clusters[j] for clusters in strata for j in rng.integers(len(clusters),size=len(clusters))])
        samples.append(questions(h[sel],f[sel],w[sel]))
    intervals=[]
    for j in (0,1):
        v=[row[j] for row in samples if row[j] is not None and np.isfinite(row[j])]
        intervals.append({"valid_draws":len(v),"total_draws":len(samples),
                          "percentile95":np.quantile(v,[.025,.975]).tolist() if len(v)>=.95*len(samples) else None})
    return {"eligible":int(eligible.sum()),"n_complete":len(d),"villages_by_province":[len(s) for s in strata],
            "unweighted_cells":cells(h,f,np.ones(len(d),dtype=int)).tolist(),
            "weighted":list(questions(h,f,w)),"unweighted":list(questions(h,f)),
            "weighted_cluster_bootstrap":intervals}
