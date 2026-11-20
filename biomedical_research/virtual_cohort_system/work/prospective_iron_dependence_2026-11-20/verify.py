"""Independent scoring from the other official serialization and saved virtual draws."""
import json
from pathlib import Path
from statistics import median

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from admission import FIELDS
from science import HERE, PARENTS, SEEDS, read


def statistics(h,f):
    h,f=pd.Series(h),pd.Series(f)
    a,b,c,d=[int(((h.lt(12)==hx) & (f.lt(15)==fx)).sum()) for hx,fx in [(1,1),(1,0),(0,1),(0,0)]]
    return float(h.rank(method="average").corr(f.rank(method="average"))),[a,b,c,d],(a*d/(b*c) if b*c else None)


def verify():
    from study import PRIVATE,save,sha
    result=read(HERE/"RESULTS.json")
    closure=read(HERE/"DRAW_CLOSURE.json")
    admission=read(HERE/"ADMISSION.json")
    assert sha(PRIVATE/"biochem.tab")==admission["files"]["biochem.tab"]["sha256"]
    data=pd.read_csv(PRIVATE/"biochem.tab",sep="\t",usecols=FIELDS)
    use=data.loc[data.Group.str.strip().eq("M") & (data.SEX==2) & data.AGE_MOTHER.ge(18) & data.AGE_MOTHER.le(49)
                 & np.isfinite(data.HGB) & np.isfinite(data.FER_ug_L) & data.HGB.gt(0) & data.FER_ug_L.gt(0)].reset_index(drop=True)
    r,cells,odds=statistics(use.HGB,use.FER_ug_L)
    assert len(use)==result["reference"]["n"] and cells==result["reference"]["cells"]
    np.testing.assert_allclose(r,result["reference"]["rank"],atol=1e-12,rtol=0)
    if odds is not None:np.testing.assert_allclose(odds,result["reference"]["odds_ratio"],rtol=1e-12)
    else:assert result["reference"]["odds_ratio"] is None
    verified=[];values={}
    for cid in ["statistical",*PARENTS]:
        if not closure["models"][cid]["usable"]:continue
        parts=[]
        for seed,rec in zip(SEEDS,closure["models"][cid]["runs"],strict=True):
            f=PRIVATE/"cohorts"/cid/f"{seed}.npy"
            assert sha(f)==rec["npy_sha256"]
            arr=np.load(f,allow_pickle=False);parts.append(arr)
            if cid!="statistical":
                base=np.load(PRIVATE/"cohorts/statistical"/f"{seed}.npy",allow_pickle=False)
                np.testing.assert_array_equal(arr[:,0],base[:,0])
                for mask in [base[:,0]<12,(base[:,0]>=12)&(base[:,0]<14),base[:,0]>=14]:
                    np.testing.assert_array_equal(np.sort(base[mask,1]),np.sort(arr[mask,1]))
        h,f=np.vstack(parts).T
        rr,cc,oo=statistics(h,f)
        np.testing.assert_allclose(rr,result["by_law"][cid]["rank"],atol=1e-12,rtol=0)
        assert cc==closure["models"]["statistical"]["pooled"]["cells"] and oo==result["by_law"][cid]["odds_ratio"]
        values[cid]=rr;verified.append(cid)
    authors=[values[c] for c in PARENTS if c in values]
    if authors:
        independent=lambda target: abs(values["statistical"]-target)-median([abs(a-target) for a in authors])
        np.testing.assert_allclose(independent(r),result["gain"],atol=1e-12,rtol=0)
        rng=np.random.default_rng(201121)
        strata=[]
        for lga in sorted(use.LGA.unique()):
            tmp=use[use.LGA==lga]
            strata.append([tmp[tmp.EA==ea][["HGB","FER_ug_L"]].to_numpy() for ea in sorted(tmp.EA.unique())])
        deltas=[]
        for _ in range(2000):
            chunks=[s[j] for s in strata for j in rng.choice(len(s),len(s),replace=True)]
            rr=spearmanr(*np.concatenate(chunks).T).statistic
            deltas.append(independent(rr))
        np.testing.assert_allclose(np.percentile(deltas,[2.5,97.5]),result["paired_bootstrap"]["gain"]["percentile95"],atol=1e-11,rtol=0)
    p=HERE/"VERIFICATION.json"
    record={"results_sha256":sha(HERE/"RESULTS.json"),"serialization":"official TAB versus evaluator Stata",
            "reference_and_scored_laws_recomputed":verified,"shared_marginal_multisets_verified":True,
            "independent_cluster_bootstrap_replicates":2000 if authors else 0,"no_author_or_reference_changed":True}
    if not p.exists():save(p,record)
    assert read(p)==record
    print(json.dumps(record))


if __name__=="__main__":
    verify()
