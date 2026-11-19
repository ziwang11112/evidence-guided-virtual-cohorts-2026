"""Independent implementations for source tables, tied ranks and the observed survey."""
from pathlib import Path
import json
import numpy as np
import pandas as pd


def independent(hb, fe, weights=None):
    h=np.asarray(hb); f=np.asarray(fe)
    w=np.ones(len(h)) if weights is None else np.asarray(weights,dtype=float)
    grid=np.zeros((2,2)); np.add.at(grid,((h>=12).astype(int),(f>=15).astype(int)),w)
    odds=(grid[0,0]/grid[0,1])/(grid[1,0]/grid[1,1]) if grid.min()>0 else None
    def ranks(v):
        data=pd.DataFrame({"v":v,"w":w})
        mass=data.groupby("v").w.sum()
        ranks=mass.cumsum()-0.5*mass
        return data.v.map(ranks).to_numpy()
    x=ranks(h);y=ranks(f)
    x=x-np.average(x,weights=w);y=y-np.average(y,weights=w)
    den=np.sqrt(np.average(x*x,weights=w)*np.average(y*y,weights=w))
    return odds,np.average(x*y,weights=w)/den if den>0 else np.nan


def fixtures():
    from scoring import questions, cells
    h=np.array([9.,10.,10.,11.,12.,12.,14.,15.])
    f=np.array([7.,15.,8.,13.,15.,17.,10.,32.])
    w=np.array([1.,2.,1.,4.,3.,1.,5.,2.])
    assert np.array_equal(cells(h,f,np.ones(len(h))),[3,1,1,3])
    assert np.allclose(questions(h,f,w),independent(h,f,w))
    assert np.allclose(questions(h,f),independent(h,f))
    a,b=questions(h,np.ones(len(h))*20,w)
    assert a is None and np.isnan(b)


def verify_sources(d, z):
    from scipy.stats import gmean
    h=d.hb_g_dl.to_numpy(); f=d.ferritin_ug_l.to_numpy()
    o,r=independent(h,f)
    assert np.allclose([o,r],[z["odds_ratio"],z["spearman"]],atol=1e-10)
    n=len(d); groups=np.digitize(h,[10,12]); grid=pd.crosstab(h<12,f<15)
    expected_cells=[(True,True),(True,False),(False,True),(False,False)]
    checks={}
    for i,(k,exp) in enumerate(zip(expected_cells,[173,85,331,1082])):
        p=exp/1671; value=grid.loc[k[0],k[1]]/n
        checks[f"cell_{i}"]=(value,p,.003+4*np.sqrt(p*(1-p)/n),False)
    for i,(ng,rate,gm) in enumerate(zip([53,205,1413],[.943,.600,.234],[1.3,5.9,22.3])):
        x=f[groups==i]; p=ng/1671
        checks[f"band_{i}"]=(len(x)/n,p,.003+4*np.sqrt(p*(1-p)/n),False)
        checks[f"depleted_in_{i}"]=((x<15).mean(),rate,.0105+4*np.sqrt(rate*(1-rate)/len(x)),False)
        checks[f"ferritin_gm_{i}"]=(gmean(x),gm,.05+.05/gm+4*np.log(x).std(ddof=1)/np.sqrt(len(x)),True)
    for key,x,target,half in [("overall_hb_gm",h,12.99,.005),("overall_ferritin_gm",f,17.4,.05)]:
        checks[key]=(gmean(x),target,.05+half/target+4*np.log(x).std(ddof=1)/np.sqrt(len(x)),True)
    checks["log_or"]=(np.log(o),np.log((173/85)/(331/1082)),.04+4*np.sqrt((1/grid).sum().sum()),False)
    assert set(checks)==set(z["checks"])
    for key,(v,target,eps,log) in checks.items():
        q=z["checks"][key]
        assert np.allclose([v,target,eps],[q["draw"],q["source"],q["allowance_on_test_scale"]],atol=1e-10)
        assert (abs(np.log(v/target) if log else v-target)<=eps)==q["pass"]
    sor=[z["checks"][k]["pass"] for k in ("cell_0","cell_1","cell_2","cell_3","log_or")]
    assert all(sor)==z["tier1"] and all(q["pass"] for q in z["checks"].values())==z["tier2"]
    sr=[blk.hb_g_dl.rank().corr(blk.ferritin_ug_l.rank()) for blk in (d.iloc[idx] for idx in np.array_split(np.arange(n),60))]
    assert np.isclose(np.std(sr,ddof=1)/np.sqrt(60),z["rank_mcse"])


def run():
    import study
    assert (study.ROOT/"REVEAL.json").exists()
    source=study.read(study.ROOT/"SOURCE_RESULTS.json")
    data=study.read(study.ROOT/"REVEAL.json")["result"]
    count=0
    for name,z in source["laws"].items():
        if "spearman" in z:
            verify_sources(study.rows(name),z);count+=1
    for pair in source["pairs"]:
        if "rank_gap" in pair:
            a,b=source["laws"][pair["primary"]],source["laws"][pair["primary"]+"_"+pair["branch"]]
            assert np.isclose(pair["rank_gap"],abs(a["spearman"]-b["spearman"]))
            assert np.isclose(pair["mc_margin"],1.96*np.sqrt(a["rank_mcse"]**2+b["rank_mcse"]**2))
    d=pd.read_stata(study.OBS,convert_categoricals=False)
    d=d.query("SUBJ==2 and SEX==2 and 18<=AGE_MOTHER<=49 and PREG==2 and LACT==2 and SEASON==2")
    assert len(d)==data["eligible"]
    d=d.loc[np.isfinite(d[["BIO_HB","BIO_FERRIT","SAMPLE_WEIGHT"]]).all(axis=1)&(d[["BIO_HB","BIO_FERRIT","SAMPLE_WEIGHT"]]>0).all(axis=1)].reset_index(drop=True)
    h,f,w=[d[k].to_numpy(float) for k in ["BIO_HB","BIO_FERRIT","SAMPLE_WEIGHT"]]
    def same(a,b): return (a is None and b is None) or (a is not None and b is not None and np.isclose(a,b))
    for exp,calc in zip(data["weighted"]+data["unweighted"],independent(h,f,w)+independent(h,f)):
        assert same(exp,calc)
    ct=pd.crosstab(d.BIO_HB>=12,d.BIO_FERRIT>=15).reindex(index=[False,True],columns=[False,True],fill_value=0)
    assert ct.to_numpy().flatten().tolist()==data["unweighted_cells"] and len(d)==data["n_complete"]
    strata=[[np.asarray(ii,dtype=int) for _,ii in p.groupby(["AIRESANT","VILLAGE"]).groups.items()] for _,p in d.groupby("PROVINCE")]
    rng=np.random.default_rng(191137)
    # Resample clusters independently of the production scorer, then use the exact
    # replication-count form of the weighted empirical distribution (including ties).
    def fast_rank(x,ww):
        keys=np.argsort(x,kind="stable"); val=x[keys]; sa=ww[keys]
        starts=np.r_[0,np.flatnonzero(np.diff(val))+1]
        mass=np.add.reduceat(sa,starts); score=np.repeat(np.cumsum(mass)-mass/2,np.diff(np.r_[starts,len(val)]))
        out=np.empty(len(val));out[keys]=score;return out
    estimates=[[],[]]
    for _ in range(4000):
        mult=np.zeros(len(d))
        for block in strata:
            for j in rng.choice(len(block),len(block),replace=True): mult[block[j]]+=1
        ww=mult*w; mask=ww>0; hh=h[mask]; ff=f[mask]; ww=ww[mask]
        grid=np.zeros((2,2)); np.add.at(grid,((hh>=12).astype(int),(ff>=15).astype(int)),ww)
        if grid.min()>0: estimates[0].append((grid[0,0]*grid[1,1])/(grid[0,1]*grid[1,0]))
        x=fast_rank(hh,ww); y=fast_rank(ff,ww); vals=np.cov(x,y,aweights=ww,ddof=0)
        if vals[0,0]>0 and vals[1,1]>0: estimates[1].append(vals[0,1]/np.sqrt(vals[0,0]*vals[1,1]))
    for resp,seq in zip(data["weighted_cluster_bootstrap"],estimates):
        assert resp["valid_draws"]==len(seq)
        if len(seq)>=3800: assert np.allclose(np.percentile(seq,[2.5,97.5]),resp["percentile95"])
        else: assert resp["percentile95"] is None
    study.write(study.ROOT/"VERIFICATION.json",{"time_utc":study.sandbox.now(),"passed":True,"laws_checked":count,"source_components_per_complete_law":16,
      "checks":["independent cell cross-tabulation, geometric means and source screens","rank covariance and Monte Carlo error","parent/branch gaps","eligibility, observed counts, weighted and unweighted estimates","entire 4000-draw village bootstrap using cluster multiplicities"]})


if __name__=="__main__": run()
