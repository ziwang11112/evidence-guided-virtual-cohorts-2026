"""Independent record-to-estimate and aggregate-only replication, with no model calls."""
import argparse
from itertools import combinations
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm, spearmanr, t

H = Path(__file__).resolve().parent
P = H/"private"
K = ("mean_abs_gap_kg","gap_at_least_5_pct","mean_both_kg","within_rank")
E = (1.,5.,2.,.1)
read = lambda path: json.loads(Path(path).read_text(encoding="utf-8"))
eq = np.testing.assert_allclose


def calc(x,y,w):
    def ranks(z):
        order=np.argsort(z,kind="stable")
        unique,first=np.unique(z[order],return_index=True)
        mass=np.add.reduceat(w[order],first)
        return (mass.cumsum()-.5*mass)[np.searchsorted(unique,z)]/w.sum()
    a,b=ranks(x),ranks(y)
    a-=np.average(a,weights=w);b-=np.average(b,weights=w)
    return np.array([np.average(abs(y-x),weights=w),100*np.average(abs(y-x)>=5-1e-10,weights=w),
                     .5*(np.average(x,weights=w)+np.average(y,weights=w)),
                     np.sum(w*a*b)/np.sqrt(np.sum(w*a*a)*np.sum(w*b*b))])


def public_check():
    pred=read(H/"PREDICTIONS.json");res=read(H/"RESULTS.json");calls=read(H/"AUTHORS.json");frozen=read(H/"FREEZE.json")
    assert set(calls["authors"])==set(frozen["dispatch_order"]) and len(calls["authors"])==8
    cost=0.
    for name,v in calls["authors"].items():
        u=v.get("usage")
        if u:
            c=frozen["config"]
            total=((u["input"]-u["cached"]-u["cache_write"])*c["input_rate"]+u["cached"]*c["cached_rate"]+
                   u["cache_write"]*c["cache_write_rate"]+u["output"]*c["output_rate"])/1e6
            eq(total,v["tariff_cost_usd"],atol=1e-10);cost+=total
    eq(cost,calls["tariff_usd"],atol=1e-10)
    methods=pred["methods"]
    for v in methods.values():
        if "by_seed" in v:
            for k in K:eq(v["values"][k],np.mean([p[k] for p in v["by_seed"]]),atol=1e-12)
    for key,s in res["reference"].items():
        o=res["comparisons"][key];est=s["estimates"]
        for name,m in methods.items():
            for k,tol in zip(K,E):
                p=m["values"][k];y=est[k];stored=o["fixed_prediction_comparisons"][name][k]
                eq(abs(y["estimate"]-p),stored["error"])
                ds=np.array(y["ci"])-p
                label="within" if max(abs(ds))<=tol else ("outside" if ds[0]>tol or ds[1]<-tol else "unresolved")
                assert label==stored["status"]
        a=np.array([m["values"][K[0]] for name,m in methods.items() if name.startswith("M")])
        b=np.array([m["values"][K[0]] for name,m in methods.items() if name.startswith("J")])
        ri=[methods["ratio_rule"]["values"][K[0]]];ind=[methods["independent"]["values"][K[0]]]
        y=est[K[0]];lo,hi=y["ci"];actual=y["estimate"]
        for key2,left,right in (("independent_to_M",ind,a),("M_to_J",a,b),("ratio_rule_to_J",ri,b)):
            if not len(left) or not len(right):assert o["contrasts"][key2] is None;continue
            # The exact kth-order distance changes at a prediction or a pair midpoint.
            knots=[lo,hi,actual,*left,*right,*[(x+y)/2 for x,y in combinations([*left,*right],2)]]
            knots=np.clip(knots,lo,hi)
            out=np.median(abs(knots[:,None]-left),axis=1)-np.median(abs(knots[:,None]-right),axis=1)
            v=o["contrasts"][key2]
            eq(out[2],v["point"]);eq([min(out),max(out)],v["over_reference_interval"],atol=1e-10)
        dd=s["diagnostic_using_separate_target_marginals"]
        eq([v[K[2]] for v in dd.values()],dd["independent"][K[2]],atol=1e-11)
    print("Aggregate checks passed for all budgets, use margins, comparison extrema and fixed-marginal controls.")
    return pred,res,cost


def raw_reader(site):
    if site=="US_NHANES":
        d=pd.read_sas(P/"DEMO_G.xpt",format="xport",encoding="latin1")
        m=pd.read_sas(P/"MGX_G.xpt",format="xport",encoding="latin1")
        d=d.loc[d.WTMEC2YR>0].merge(m,on="SEQN",how="left",validate="1:1")
        halves=[]
        for hand in (1,2):
            fns=[f"MGXH{hand}T{t}" for t in (1,2)]
            trial=d[fns].to_numpy()
            good=np.all(trial>0,axis=1) & np.all(d[[f+"E" for f in fns]].to_numpy()==1,axis=1)
            halves.append(np.where(good,trial.sum(axis=1)/2,np.nan))
        first=d.MGATHAND.to_numpy()
        good=(d.MGDEXSTS==1) & d.MGATHAND.isin([1,2])
        return rows(d.RIDAGEYR,d.RIAGENDR.map({1:"M",2:"F"}),np.where(first==1,*halves),np.where(first==2,*halves),
                    d.WTMEC2YR,d.SDMVSTRA,d.SDMVPSU,good)
    if site=="ZA_HAALSI":
        path=H.parent/"scaleup_2026-11-01/admission_next/private_data/HAALSI_baseline_dataverse_14Apr2017.dta"
        cols=["c_pt043","c_pt044","c_pt045","c_pt046","rage","rsex","village_anon","prim_key"]
        d=pd.read_stata(path,columns=cols,convert_categoricals=False)
        return rows(d.rage,d.rsex.map({1:"M",2:"F"}),(d.c_pt045+d.c_pt046)/2,(d.c_pt043+d.c_pt044)/2,
                    np.ones(len(d)),np.zeros(len(d)),d.village_anon,(d[cols[:4]]>0).all(axis=1))
    d=pd.read_spss(P/"DataSet.sav",convert_categoricals=False)
    return rows(d.IDADE,d.SEXOCOD.map({1:"F",2:"M"}),d.FPM_SAUD_DIR,d.FPM_SAUD_ESQ,d.PESO_FINAL,
                d.ESTR_SEL,d.COD_UPA,(d.FPM_SAUD_DIR>0)&(d.FPM_SAUD_ESQ>0))


def rows(age,sex,r,l,w,st,psu,ok):
    df=pd.DataFrame(dict(age=age,sex=sex,r=r,l=l,w=w,st=st,psu=psu))
    design=df.loc[df.w>0,["st","psu"]].dropna().drop_duplicates()
    df=df.loc[ok & df.age.isin(range(50,70)) & df.sex.isin(["M","F"]) & (df.w>0)].dropna()
    df["cell"]=df.sex+np.where(df.age<60,"50","60")
    return df,design


def raw_survey(df,design):
    cells=["M50","M60","F50","F60"]
    def val(w):
        out=[]
        for key in cells:
            take=(df.cell.to_numpy()==key)&(w>0)
            out.append(calc(df.r.to_numpy()[take],df.l.to_numpy()[take],w[take]))
        return np.mean(out,axis=0)
    w=df.w.to_numpy()
    center=val(w);var=np.zeros(4)
    for label,grp in design.groupby("st"):
        m=len(grp)
        reps=[]
        for unit in grp.psu:
            mult=np.where(df.st!=label,1.,np.where(df.psu==unit,0.,m/(m-1)))
            reps.append(val(w*mult))
        var+=np.var(reps,axis=0)*(m-1)
    half=t.isf(.025,len(design)-design.st.nunique())*np.sqrt(var)
    return center,np.c_[center-half,center+half]


def ref_grids(df,n):
    # The first order statistic whose cumulative weight reaches a grid midpoint.
    prob=(np.arange(n)+.5)/n
    def q(d,col):
        data=d.sort_values(col,kind="stable")
        cumulative=data.w.cumsum().to_numpy()/data.w.sum()
        return data[col].to_numpy()[np.searchsorted(cumulative,prob)]
    return [(q(d,"r"),q(d,"l")) for cell in ["M50","M60","F50","F60"] for d in [df[df.cell==cell]]]


def score_pairs(grids,orders):
    z=[]
    for (x,y),o in zip(grids,orders):
        assert np.array_equal(np.unique(o),np.arange(len(x)))
        y=y[o];gap=abs(x-y)
        z.append([np.mean(gap),100*np.mean(gap>=5-1e-10),.5*(x.mean()+y.mean()),spearmanr(x,y).statistic])
    return np.mean(z,axis=0)


def score_ind(grids):
    parts=[]
    for x,y in grids:
        sums=np.zeros(2)
        for batch in np.array_split(x,32):
            delta=abs(batch[:,None]-y)
            sums += [delta.sum(),(delta>=5-1e-10).sum()]
        parts.append([sums[0]/len(x)**2,100*sums[1]/len(x)**2,(x.mean()+y.mean())/2,0.])
    return np.mean(parts,axis=0)


def private_check(pred,res,cost):
    from hashlib import sha256
    from science import seal
    n=read(H/"FREEZE.json")["n_per_cell"]
    z=norm.ppf((np.arange(n)+.5)/n)
    z=(z-np.mean(z))/np.sqrt(np.mean((z-z.mean())**2))
    source=[(m1+sd1*z,m2+sd2*z) for _,_,_,m1,sd1,m2,sd2 in read(H/"AU_SOURCE.json")["cells"]]
    grids={"source":source};scores={"source":{k:r["values"] for k,r in pred["methods"].items()}}
    checked={}
    for key,s in res["reference"].items():
        df,design=raw_reader(key)
        val,ci=raw_survey(df,design)
        eq(val,[s["estimates"][k]["estimate"] for k in K],atol=2e-10)
        eq(ci,[s["estimates"][k]["ci"] for k in K],atol=2e-10)
        assert len(df)==s["qc"]["eligible_bilateral"]
        grids[key]=ref_grids(df,n);scores[key]=s["diagnostic_using_separate_target_marginals"]
        checked[key]=len(df)
    predictions=pred["methods"]
    for g,grid in grids.items():
        eq(score_ind(grid),[scores[g]["independent"][k] for k in K],atol=1e-9)
        for name,model in predictions.items():
            if "draws" not in model:continue
            ss=[]
            for run in model["draws"]:
                file=P/"runs"/name/str(run["seed"])/"perm.npy"
                assert sha256(file.read_bytes()).hexdigest()==run["permutation_sha256"]
                ss.append(score_pairs(grid,np.load(file,allow_pickle=False)))
            eq(np.mean(ss,axis=0),[scores[g][name][k] for k in K],atol=1e-8)
        # Undo and reapply the independent rule from the German ratio dispersion.
        cv=read(H/"JOINT_SOURCE.json")["dimensionless_individual_ratio_sd"]/read(H/"JOINT_SOURCE.json")["dimensionless_individual_ratio_mean"]
        corr=[]
        for x,y in source:
            cx,cy=x.std()/x.mean(),y.std()/y.mean()
            corr.append(max(-1,min(1,(cx**2+cy**2-np.log(1+cv**2))/(2*cx*cy))))
        eq(corr,predictions["ratio_rule"]["rhos"])
        ss=[]
        for seed in read(H/"FREEZE.json")["execution_seeds"]:
            rng=np.random.default_rng(seed)
            ix=[]
            for rho in corr:
                v=rho*norm.ppf((np.arange(n)+.5)/n)+np.sqrt(1-rho*rho)*rng.standard_normal(n)
                order=np.empty(n,dtype=int);order[np.argsort(v)]=np.arange(n);ix.append(order)
            ss.append(score_pairs(grid,ix))
        eq(np.mean(ss,axis=0),[scores[g]["ratio_rule"][k] for k in K],atol=1e-8)
    out={"independent_record_to_estimate":True,"eligible_by_study":checked,"public_models":len(predictions),
         "checked_endpoints_per_study":4,"target_marginal_diagnostic_recomputed":True,
         "source_seeds_checked_for_every_completed_author":3,"agent_call_tariff_usd":cost,
         "readers":"Independent pandas XPORT and Stata readers for US and South Africa. The independent SPSS analysis shares the ReadStat backend for Brazil.",
         "population_units":"Two principal study families and one separately recruited measurement stress test."}
    seal(H/"VERIFICATION.json",out)
    print("Record-level independent verification passed:",checked)


if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--public-only",action="store_true")
    cli=ap.parse_args();p,r,c=public_check()
    if not cli.public_only:private_check(p,r,c)
