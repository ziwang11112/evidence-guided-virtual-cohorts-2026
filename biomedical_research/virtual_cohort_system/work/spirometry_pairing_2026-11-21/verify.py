"""Independent read and calculation of the published participant and synthetic summaries."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from openpyxl import load_workbook
from scipy.stats import lognorm, t

HERE=Path(__file__).resolve().parent
PRIVATE=HERE/"private"
KEYS=["mean_individual_ratio_pct","ratio_of_means_pct","below_070_pct","within_sex_pearson"]
SEXES=("F","M")


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(a,b):
    np.testing.assert_allclose(a,b,rtol=1e-9,atol=1e-9)


def row_estimates(x,y,sex,w):
    rows=[]
    for name in SEXES:
        use=(sex==name)&(w>0)
        xx,yy,ww=x[use],y[use],w[use]
        a,b=np.average(xx,weights=ww),np.average(yy,weights=ww)
        corr=np.average((xx-a)*(yy-b),weights=ww)/np.sqrt(np.average((xx-a)**2,weights=ww)*np.average((yy-b)**2,weights=ww))
        rows.append([a,b,np.average(xx/yy,weights=ww),np.average((xx/yy)<.70,weights=ww),corr])
    a,b,first,tail,corr=np.mean(rows,axis=0)
    return np.array([100*first,100*a/b,100*tail,corr])


def measured_us():
    dp=PRIVATE/"DEMO_G.xpt"
    if not dp.is_file():
        dp=HERE.parent/"bilateral_grip_transfer_2026-11-21/private/DEMO_G.xpt"
    dem=pd.read_sas(dp,format="xport",encoding="latin-1").set_index("SEQN",verify_integrity=True)
    demo=dem[dem.WTMEC2YR>0]
    spx=pd.read_sas(PRIVATE/"SPX_G.xpt",format="xport",encoding="latin-1").set_index("SEQN",verify_integrity=True)
    f=demo.join(spx[["SPXNFEV1","SPXNFVC","SPXNSTAT","SPXNQFV1","SPXNQFVC"]])
    f=f[f.RIDAGEYR.ge(18)&f.RIDAGEYR.le(79)&f.RIAGENDR.isin([1,2])&f.SPXNSTAT.eq(1)
        &f.SPXNFEV1.gt(0)&f.SPXNFVC.gt(0)&f.SPXNQFV1.str.strip().isin(["A","B"])&f.SPXNQFVC.str.strip().isin(["A","B"])]
    f=f.dropna(subset=["SDMVSTRA","SDMVPSU"]).sort_index()
    x=f.SPXNFEV1.to_numpy()/1000
    y=f.SPXNFVC.to_numpy()/1000
    sex=np.where(f.RIAGENDR.eq(1),"M","F")
    w=f.WTMEC2YR.to_numpy()
    point=row_estimates(x,y,sex,w)
    total=np.zeros(4)
    df=0
    for st,sub in demo.groupby("SDMVSTRA"):
        units=sub.SDMVPSU.dropna().unique()
        rep=[]
        for unit in units:
            factor=np.where(f.SDMVSTRA!=st,1,np.where(f.SDMVPSU==unit,0,len(units)/(len(units)-1)))
            rep.append(row_estimates(x,y,sex,w*factor))
        delta=np.asarray(rep)-np.mean(rep,axis=0)
        total+=(1-1/len(units))*(delta*delta).sum(axis=0)
        df+=len(units)-1
    radius=t.ppf(.975,df)*np.sqrt(total)
    return len(f),point,np.column_stack([point-radius,point+radius])


def measured_mw():
    book=load_workbook(PRIVATE/"ALHS_spiro_y1and2.xlsx",read_only=True,data_only=True)
    it=book["ALHS_y1spiro"].values
    keys=next(it)
    filtered=[]
    for line in it:
        r=dict(zip(keys,line))
        if (r["round"]==46 and r["sex"] in ("f","m") and r["age"] is not None and 18<=r["age"]<=79
            and r["prefevQC"]==r["prefvcQC"]==1 and r["prefev1"] and r["prefev1"]>0 and r["prefvc1"] and r["prefvc1"]>0):
            filtered.append((r["id"],r["sex"].upper(),r["prefev1"],r["prefvc1"]))
    book.close()
    filtered.sort()
    assert len({r[0] for r in filtered})==len(filtered)
    sex=np.array([r[1] for r in filtered])
    x,y=np.asarray([r[2:] for r in filtered]).T
    point=row_estimates(x,y,sex,np.ones(len(x)))
    seeds=np.random.SeedSequence(48251).spawn(2)
    rep_by_sex=[]
    for tag,seed in zip(SEXES,seeds,strict=True):
        mask=sex==tag
        n=mask.sum()
        idx=np.random.default_rng(seed).integers(n,size=(2000,n))
        a,b=x[mask][idx],y[mask][idx]
        ax,bx=a.mean(axis=1),b.mean(axis=1)
        ac,bc=a-ax[:,None],b-bx[:,None]
        rho=(ac*bc).sum(axis=1)/np.sqrt((ac*ac).sum(axis=1)*(bc*bc).sum(axis=1))
        rep_by_sex.append(np.array([ax,bx,(a/b).mean(axis=1),np.mean((a/b)<.70,axis=1),rho]))
    ax,bx,first,tail,rho=np.mean(rep_by_sex,axis=0)
    ci=np.nanquantile(np.stack([100*first,100*ax/bx,100*tail,rho]),[.025,.975],axis=1).T
    return len(filtered),point,ci


def reference_input_audit():
    ref=read(HERE/"RESULTS.json")["reference"]
    for tag,record in ref.items():
        for name,expected in record["files"].items():
            path=PRIVATE/name
            if name=="DEMO_G.xpt" and not path.is_file():
                path=HERE.parent/"bilateral_grip_transfer_2026-11-21/private"/name
            assert digest(path)==expected["sha256"] and path.stat().st_size==expected["bytes"]
        n,point,ci=(measured_us if tag=="US_NHANES" else measured_mw)()
        assert n==record["n"]
        close(point,[record["estimates"][k]["estimate"] for k in KEYS])
        close(ci,[record["estimates"][k]["ci"] for k in KEYS])


def source_columns():
    quantiles=(np.arange(4096)+.5)/4096
    out={}
    for row in read(HERE/"MARGINAL_SOURCE.json")["cells"]:
        out[row["sex"]]={}
        for col in ("fev1","fvc"):
            mean,sd=row[col+"_mean"],row[col+"_sd"]
            std=np.sqrt(np.log(1+(sd/mean)**2))
            raw=lognorm.ppf(quantiles,std)
            out[row["sex"]][col]=mean+sd*(raw-np.mean(raw))/np.std(raw)
    return out


def check_draws(pred):
    source=source_columns()
    total=0
    for name,model in pred["methods"].items():
        per=[]
        for d in model["draws"]:
            seed=d["seed"]
            path=PRIVATE/"draws"/name/f"{seed}.npz"
            assert digest(path)==d["virtual_records_sha256"]
            if "proposal_csv_sha256" in d:
                csv=PRIVATE/"runs"/name/str(seed)/"isolated/output/generated.csv"
                assert digest(csv)==d["proposal_csv_sha256"]
            with np.load(path,allow_pickle=False) as data:
                x,y,sex=data["fev1_l"],data["fvc_l"],data["sex"]
                assert len(x)==len(y)==len(sex)==8192 and not np.any(x>y)
                expected=row_estimates(x,y,sex,np.ones(len(x)))
                close(expected,[d["values"][k] for k in KEYS])
                per.append(expected)
                invalid=changed=0
                for i,s in enumerate(SEXES):
                    sel=(sex==s)
                    close(x[sel],source[s]["fev1"])
                    close(np.sort(y[sel]),source[s]["fvc"])
                    # Read the exact marginal arrays from the archive for the physical boundary check.
                    actual_y=np.sort(y[sel])
                    raw=data["raw_fvc_index"][i]
                    final=data["accepted_fvc_index"][i]
                    assert np.array_equal(np.sort(raw),np.arange(len(raw)))
                    assert np.array_equal(np.sort(final),np.arange(len(final)))
                    np.testing.assert_array_equal(actual_y[final],y[sel])
                    invalid+=int(np.sum(x[sel]>actual_y[raw]))
                    changed+=int(np.sum(raw!=final))
                assert (invalid,changed)==(d["feasibility"]["raw_invalid_rows"],d["feasibility"]["changed_pairs"])
            total+=1
        close(np.mean(per,axis=0),[model["values"][k] for k in KEYS])
    return total


def public_check():
    pred=read(HERE/"PREDICTIONS.json")
    result=read(HERE/"RESULTS.json")
    authors=read(HERE/"AUTHORS.json")
    study=read(HERE/"FREEZE.json")
    assert result["prediction_commit"]==read(HERE/"REFERENCE_OPEN.json")["prediction_commit"]
    for rel,dig in study["files"].items():
        source=HERE.parents[1]/rel
        assert hashlib.sha256(source.read_text(encoding="utf-8").encode()).hexdigest()==dig,rel
    close(authors["total_tariff_usd"],sum(a["tariff_cost_usd"] or 0 for a in authors["authors"].values()))
    ds=pred["methods"]
    close([r["values"]["ratio_of_means_pct"] for r in ds.values()],np.full(len(ds),100*5.8/7.6))
    for tag,details in result["reference"].items():
        for arm,control in [("J","source_gaussian"),("M","physical_uniform")]:
            if arm not in pred["upper_bounds_on_median_error_gain"]:
                continue
            for k in KEYS:
                s=ds[control]["values"][k]
                vals=np.array([ds[arm+str(i)]["values"][k] for i in range(1,5)])
                bound=np.median(abs(vals-s))
                close(bound,pred["upper_bounds_on_median_error_gain"][arm][k])
                observed=details["estimates"][k]["estimate"]
                gain=abs(observed-s)-np.median(abs(vals-observed))
                contrast=details["comparisons"]["error_reduction"][arm][k]
                close(gain,contrast["point"])
                assert max(abs(z) for z in [gain,*contrast["over_reference_interval"]])<=bound+1e-9
    return pred,result


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--public-only",action="store_true")
    public=ap.parse_args().public_only
    pred,result=public_check()
    if not public:
        reference_input_audit()
        n=check_draws(pred)
        report={"target_populations_recomputed":list(result["reference"]),"estimates_and_intervals_per_site":len(KEYS),
                "verified_complete_draw_files":n,"independent_readers":["pandas XPORT instead of pyreadstat",
                "worksheet cell iteration instead of pandas read_excel"],"target_reader_note":"Both Malawi readers use openpyxl as the Excel backend.",
                "independent_analysis":"Direct centered covariances and participant ratios from the stored rows; US delete-PSU weights and independently computed bootstrap quantiles in Malawi.",
                "public_seal_and_error_bound_checks":True}
        out=HERE/"VERIFICATION.json"
        if out.exists(): assert read(out)==report
        else: out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8",newline="\n")
        print(report)
    else: print("Public protocol, costing, invariant estimates and pre-disclosure bound checks passed.")
