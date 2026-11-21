"""Independent release audit. Use --public-only for checks requiring no participant records."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
from statistics import median

import numpy as np
import pandas as pd
import pyreadstat
from scipy.stats import spearmanr, t

ROOT = Path(__file__).resolve().parent
WORK = ROOT.parent
FIELDS = ("mean_nonhdl","mean_ratio","tc_high","hdl_low","nonhdl160","rank_tc_hdl")
MARGINS = (10.,.30,5.,5.,2.,.10)
MASS = dict(enumerate([.396579,.371795,.231626]))
CHECK_SEED = 41117


def read(p):
    return json.loads(p.read_text(encoding="utf-8"))


def equal(a,b,tol=2e-9):
    np.testing.assert_allclose(a,b,rtol=1e-12,atol=tol)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check_target(suffix, reference):
    data={}
    for stub,role in [("DEMO","demographics"),("TCHOL","total"),("HDL","hdl")]:
        path=ROOT/"private/reference"/f"{stub}_{suffix}.xpt"
        assert sha(path)==reference["qc"]["files"][role]["sha256"]
        frame,_=pyreadstat.read_xport(str(path),encoding="WINDOWS-1252")
        data[stub]=frame.set_index("SEQN")
        assert data[stub].index.is_unique and data[stub].index.notna().all()
    cohort=data["DEMO"].loc[lambda d:d.WTMEC2YR>0]
    unit=cohort.groupby("SDMVSTRA")["SDMVPSU"].unique()
    keep=data["TCHOL"][["LBXTC"]].join(data["HDL"][["LBDHDD"]],how="inner")
    if suffix=="L":
        keep["weight"]=data["TCHOL"].WTPH2YR
    else:
        keep["weight"]=cohort.WTMEC2YR
    f=cohort[["RIDAGEYR","SDMVSTRA","SDMVPSU"]].join(keep,how="inner")
    f=f.query("RIDAGEYR >= 20 and weight > 0 and LBXTC > 0 and LBDHDD > 0").copy()
    assert len(f)==reference["qc"]["both_measures_weighted"]
    f["band"]=(f.RIDAGEYR>=40).astype(int)+(f.RIDAGEYR>=60).astype(int)
    a,b=f.LBXTC,f.LBDHDD
    ops=pd.DataFrame({"mean_nonhdl":a-b,"mean_ratio":a/b,"tc_high":(a>=6.2*38.67)*100.,
                     "hdl_low":(b<38.67)*100.,"nonhdl160":((a-b)>=160)*100.},index=f.index)

    def remeasure(multipliers):
        w=f.weight*multipliers
        weighted=ops.mul(w,axis=0).groupby(f.band).sum()
        denominators=w.groupby(f.band).sum()
        points=weighted.div(denominators,axis=0).mul(pd.Series(MASS),axis=0).sum(axis=0)
        mix=w*f.band.map(MASS)/f.band.map(denominators)
        def midranks(measure):
            distribution=mix.groupby(measure,sort=True).sum()
            return measure.map(distribution.cumsum()-distribution/2).to_numpy()
        ranks=np.vstack([midranks(k) for k in (a,b)])
        cov=np.cov(ranks,aweights=mix,ddof=0)
        return np.r_[points.to_numpy(),cov[0,1]/np.sqrt(cov[0,0]*cov[1,1])]
    point=remeasure(1.)
    variations=[]
    df=0
    for stratum,units in unit.items():
        cluster_deltas=[]
        for unit_id in units:
            factors=np.where(f.SDMVSTRA!=stratum,1.,np.where(f.SDMVPSU==unit_id,0.,len(units)/(len(units)-1)))
            cluster_deltas.append(remeasure(factors)-point)
        variations.append(np.linalg.norm(np.array(cluster_deltas),axis=0)**2*(1-1/len(units)))
        df+=len(units)-1
    se=np.sqrt(np.sum(variations,axis=0))
    multiplier=t.isf(.025,df)
    assert df==reference["qc"]["df"]
    for i,k in enumerate(FIELDS):
        e=reference["estimates"][k]
        equal([point[i],se[i],point[i]-multiplier*se[i],point[i]+multiplier*se[i]],[e["estimate"],e["se"],*e["ci"]])
    return f.index.to_numpy()


def verify_virtual(predictions):
    old=WORK/"nonhdl_external_2026-11-20"
    alt=WORK/"kdd_v40_pairing_review_2026-11-20"
    original=read(old/"MODEL_CLOSURE.json")["arms"]["agent"]["runs"]
    pairs={}
    for r in original:
        path=old/"private"/f"agent-{r['seed']}.npy"
        assert sha(path)==r["array_sha256"]
        arr=np.load(path,allow_pickle=False)
        source=np.column_stack([np.sort(arr[:,0]),np.sort(arr[:,1])])
        ix=np.argsort(np.argsort(arr[:,1],kind="stable"),kind="stable")[np.argsort(arr[:,0])]
        pairs.setdefault("nominal",[]).append(ix)
    for a,r in read(alt/"SENSITIVITY.json")["authors"].items():
        for mode,runs in r["runs"].items():
            for draw in runs:
                folder=alt/"private/draws"/a/mode/str(draw["seed"])
                file=folder/"run/output/generated.csv"
                assert sha(file)==draw["output_hash"]
                index=pd.read_csv(file).sort_values("row_id").hdl_index.to_numpy()
                pairs.setdefault(f"{a}_{mode}",[]).append(index)
    anchor=read(ROOT/"US_SOURCE.json")
    grids={"base":source,"statistical":source/source.mean(axis=0)*[anchor["tc"]["mean"],anchor["hdl"]["mean"]]}
    for key,r in read(ROOT/"PREDICTIONS.json")["execution"].items():
        if r["usable"]:
            path=ROOT/"private/runs"/key/str(CHECK_SEED)/"run/output/generated.csv"
            assert sha(path)==r["verification_runs"][0]["csv_sha256"]
            grids[key]=pd.read_csv(path,float_precision="round_trip")[["tc_mg_dl","hdl_mg_dl"]].to_numpy()
    assert set(grids)==set(predictions)
    for name,grid in grids.items():
        baseline=predictions[name]
        equal(grid.mean(axis=0),baseline["marginal_means"])
        for k,ix in pairs.items():
            tc=np.tile(grid[:,0],len(ix));hd=np.concatenate([grid[order,1] for order in ix])
            rate=lambda tag:100*np.count_nonzero(tag)/len(tag)
            score=baseline["pairings"][k]
            fields=[np.mean(tc)-np.mean(hd),np.mean(tc/hd),rate(tc>=6.2*38.67),rate(hd<38.67),
                    rate(tc-hd>=160),spearmanr(tc,hd).statistic]
            equal(fields,[score["values"][t] for t in FIELDS])
            assert len(tc)==score["n"] and np.count_nonzero(hd>tc)==score["hdl_above_tc"]


def check_public():
    closure=read(ROOT/"PREDICTIONS.json")
    result=read(ROOT/"RESULTS.json")
    authors=read(ROOT/"AUTHORS.json")["calls"]
    preds=closure["predictions"]
    charges=[]
    rates=read(ROOT/"FREEZE.json")["model"]
    for r in authors.values():
        info=r["usage"]
        if info is not None:
            i,c,o,w=(info[k] for k in ("input","cached","output","cache_write"))
            cost=((i-c-w)*rates["input_rate"]+c*rates["cached_rate"]+w*rates["cache_write_rate"]+o*rates["output_rate"])/1e6
            equal(cost,r["tariff_cost_usd"])
            charges.append(cost)
    gains={}
    for period,cohort in result["reference"].items():
        estimates=cohort["estimates"]
        sc=result["scores"][period]
        pts={k:v["pairings"]["nominal"]["values"] for k,v in preds.items()}
        for name,rows in pts.items():
            for k,tol in zip(FIELDS,MARGINS):
                yy=estimates[k]
                diff=rows[k]-yy["estimate"]; lo,hi=np.array(yy["ci"])[::-1]*-1+rows[k]
                recorded=sc["methods"][name]["nominal"][k]
                equal([diff,lo,hi,tol],[recorded["signed_gap"],*recorded["gap_ci"],recorded["tolerance"]])
                status="within" if -tol<=lo<=hi<=tol else "contradicted" if hi < -tol or lo>tol else "unresolved"
                assert status==recorded["status"]
            others=[p["values"]["nonhdl160"] for key,p in preds[name]["pairings"].items() if key!="nominal"]
            equal([min(others),max(others)],sc["methods"][name]["eight_alternative_rate_range"])
        k="nonhdl160"
        y=estimates[k]
        base=pts["base"][k];proposals=[pts[a][k] for a in authors if a in pts]
        gov=lambda x:abs(base-x)-median(abs(v-x) for v in proposals)
        if proposals:
            equal(gov(y["estimate"]),sc["primary"]["base_minus_median_agent_abs_error_pp"])
            lo,hi=y["ci"]
            knots=sorted(set([lo,hi,base,*proposals,*[(a+b)/2 for a,b in itertools.combinations(proposals,2)]]))
            all_eval=[gov(x) for x in knots if lo<=x<=hi]
            equal([min(all_eval),max(all_eval)],sc["primary"]["range_over_reference_95ci_pp"])
            gains[period]=gov(y["estimate"])
        equal(abs(base-y["estimate"])-abs(pts["statistical"][k]-y["estimate"]),sc["statistical_gain_pp"])
    audit_file=ROOT/"PAIRING_DIAGNOSTIC.json"
    if audit_file.exists():
        audit=read(audit_file)
        multipliers=np.divide(preds["statistical"]["marginal_means"],preds["base"]["marginal_means"])
        equal(multipliers,[audit["tc_multiplier"],audit["hdl_multiplier"]])
        for law,row in audit["by_pairing"].items():
            first=preds["base"]["pairings"][law]["values"]
            updated=preds["statistical"]["pairings"][law]["values"]
            equal(updated["mean_ratio"],first["mean_ratio"]*multipliers[0]/multipliers[1])
            equal(updated["rank_tc_hdl"],first["rank_tc_hdl"])
            equal([first["nonhdl160"],updated["nonhdl160"]],[row["before_pct"],row["after_pct"]])
            equal(row["switched_pct"],row["after_pct"]-row["before_pct"])
            assert sum(q["entered"] for q in row["runs"])==row["entered"] and not any(q["left"] for q in row["runs"])
            equal(row["switched_pct"],100*row["entered"]/row["n"])
            for key,y in result["reference"].items():
                real=y["estimates"]["nonhdl160"]
                change=lambda q:abs(first["nonhdl160"]-q)-abs(updated["nonhdl160"]-q)
                equal(change(real["estimate"]),row["gain"][key]["gain_pp"])
                lo,hi=real["ci"]
                values=[change(x) for x in (lo,hi,first["nonhdl160"],updated["nonhdl160"]) if lo<=x<=hi]
                equal([min(values),max(values)],row["gain"][key]["range_over_ci_pp"])
        for place,rec in audit["measured_component_means"].items():
            equal(rec["tc"]-rec["hdl"],result["reference"][place]["estimates"]["mean_nonhdl"]["estimate"])
    return result,preds,sum(charges),gains


if __name__=="__main__":
    cli=argparse.ArgumentParser();cli.add_argument("--public-only",action="store_true")
    arg=cli.parse_args()
    results,predictions,cost,gains=check_public()
    if arg.public_only:
        print("Public-only arm scores, pairing ranges, gains, interval bounds and tariff agree.")
    else:
        ids=[check_target(k,v) for k,v in results["reference"].items()]
        assert not set(ids[0]).intersection(ids[1])
        verify_virtual(predictions)
        receipt={"verification":"Independent ReadStat parser, domain means, tie-weighted Spearman, PSU jackknife and raw virtual outputs",
                 "eligible_n":[len(r) for r in ids],"independent_survey_cycles":2,"same_survey_family":True,
                 "separate_ids":True,"checked_endpoints_per_cycle":6,"checked_methods":len(predictions),
                 "checked_virtual_method_pairings":9*len(predictions),"tariff_usd":cost,"primary_gains_pp":gains}
        path=ROOT/"VERIFICATION.json"
        if path.exists():assert read(path)==receipt
        else:path.write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8",newline="\n")
        print(json.dumps(receipt,indent=2))
