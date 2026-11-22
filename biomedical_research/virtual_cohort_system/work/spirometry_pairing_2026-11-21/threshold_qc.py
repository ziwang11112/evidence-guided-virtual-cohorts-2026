"""Audit the strict 70% boundary using the decimal precision of measured volumes."""
from decimal import Decimal
from pathlib import Path
import numpy as np
from scipy.stats import t
from reference_spiro import BOOT_N, BOOT_SEED, malawi, nhanes
from study import HERE, PRIVATE, SEXES, read, seal


def mean_rate(flags, sex, weights):
    return 50*sum(np.average(flags[sex==s],weights=weights[sex==s]) for s in SEXES)


def target_check(site,loader):
    f,design,_=loader()
    x,y,sex,w=(f[c].to_numpy() for c in ("x","y","sex","w"))
    a,b=np.rint(x*1e9).astype(np.int64),np.rint(y*1e9).astype(np.int64)
    assert np.max(abs(x*1e9-a)) < 1e-4 and np.max(abs(y*1e9-b)) < 1e-4
    exact=10*a<7*b
    boundary=10*a==7*b
    binary=x/y<.70
    assert not np.any((exact!=binary)&~boundary)
    point=mean_rate(exact,sex,w)
    if design is not None:
        var=0.
        df=0
        for name,sub in design.groupby("stratum"):
            ids=sub.psu.unique()
            n=len(ids)
            rates=[]
            for ident in ids:
                factor=np.where(f.stratum!=name,1.,np.where(f.psu==ident,0.,n/(n-1)))
                rates.append(mean_rate(exact,sex,w*factor))
            var+=(n-1)*np.var(rates)
            df+=n-1
        half=t.ppf(.975,df)*np.sqrt(var)
        ci=[point-half,point+half]
    else:
        seeds=np.random.SeedSequence(BOOT_SEED).spawn(2)
        rates=[]
        for s,seed in zip(SEXES,seeds,strict=True):
            v=exact[sex==s]
            idx=np.random.default_rng(seed).integers(len(v),size=(BOOT_N,len(v)))
            rates.append(100*v[idx].mean(axis=1))
        ci=np.quantile(np.mean(rates,axis=0),[.025,.975]).tolist()
    registered=read(HERE/"RESULTS.json")["reference"][site]["estimates"]["below_070_pct"]
    assert abs(mean_rate(binary,sex,w)-registered["estimate"])<1e-8
    return {"decimal_exact_ties":int(boundary.sum()),"different_classifications":int(np.sum(binary!=exact)),
            "registered_rate_pct":registered["estimate"],"decimal_rate_pct":float(point),"decimal_ci":ci}


def run():
    ref=read(HERE/"RESULTS.json")
    pred=read(HERE/"PREDICTIONS.json")
    correction={}
    for name,loader in (("US_NHANES",nhanes),("MW_ALHS_Y1",malawi)):
        if name in ref["reference"]:
            correction[name]=target_check(name,loader)
    count=0
    near=0
    for k,v in pred["methods"].items():
        for draw in v["draws"]:
            with np.load(PRIVATE/"draws"/k/f"{draw['seed']}.npz",allow_pickle=False) as rows:
                x,y=rows["fev1_l"],rows["fvc_l"]
                mask=np.abs(10*x-7*y)<1e-11
                for a,b in zip(x[mask],y[mask],strict=True):
                    count+=int((a/b<.70) != (10*Decimal.from_float(a)<7*Decimal.from_float(b)))
                near+=int(mask.sum())
    result={"target":correction,"near_threshold_virtual_rows":near,"virtual_disagreements_in_near_rows":count}
    seal(HERE/"THRESHOLD_QC.json",result)
    print(result)


if __name__=="__main__":
    run()
