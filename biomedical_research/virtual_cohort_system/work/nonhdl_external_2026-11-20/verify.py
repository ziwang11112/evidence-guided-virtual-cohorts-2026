"""Independent readers and estimator formulas for the two published files and sealed programs."""
import io
import json
import os
import subprocess
from pathlib import Path
from statistics import fmean
import numpy as np
import pandas as pd
from science import HERE,SEEDS,read,sha,write

def independent(name):
    if name=="mekelle":
        code=('x=foreign::read.spss("private/mekelle.sav",to.data.frame=TRUE,use.value.labels=FALSE);'
              'write.csv(data.frame(id=x$Participant_code,age=x$Age,tc=x$Total_Cholesterol,hdl=x$HDL_C),row.names=FALSE)')
        cmd=["Rscript","-e",code]
        if os.name=="nt":
            libs=os.environ.get("NONHDL_R_LIBS","/tmp/kdd-nonhdl-rforeign/extracted/usr/lib/R/library")
            cmd=["wsl","-e","env","R_LIBS="+libs,*cmd]
        raw=subprocess.run(cmd,cwd=HERE,check=True,capture_output=True)
        df=pd.read_csv(io.BytesIO(raw.stdout))
    else:
        df=pd.read_stata(HERE/"private/workers.dta",columns=["id","age","cholestrole","HDL_c"],convert_categoricals=False)
        df=df.rename(columns={"cholestrole":"tc","HDL_c":"hdl"})
    sub=df.loc[~df.id.duplicated(keep=False)&df.id.notna()&df.age.ge(20)&df.tc.gt(0)&df.hdl.gt(0)].dropna(subset=["age","tc","hdl"])
    return sub[["age","tc","hdl"]].to_numpy()

def check():
    result=read(HERE/"RESULTS.json");seal=read(HERE/"CLOSURE.json");records={}
    assert result["closure_sha256"]==sha(HERE/"CLOSURE.json")
    for name,seed in (("mekelle",404203),("workers",404207)):
        independent_rows=independent(name)
        orig=np.load(HERE/f"private/{name}-eligible.npy",allow_pickle=False)
        np.testing.assert_allclose(independent_rows,orig,atol=1e-7,rtol=0)
        ages,tc,hdl=independent_rows.T;d=tc-hdl
        full=result["cohorts"][name];ref=full["reference"]
        assert len(d)==ref["n"] and np.count_nonzero(d>=160)==ref["tail_count"]
        assert abs(fmean(d)-ref["mean_mg_dl"])<1e-7
        rng=np.random.default_rng(seed)
        groups=[g for g in (np.flatnonzero(ages<40),np.flatnonzero(ages>=40)) if len(g)]
        boot=np.empty((2000,2))
        for i in range(2000):
            obs=np.concatenate([d[g][rng.integers(0,len(g),size=len(g))] for g in groups])
            boot[i]=np.sum(obs)/len(obs),100*np.count_nonzero(obs>=160)/len(obs)
        np.testing.assert_allclose(np.quantile(boot,[.025,.975],axis=0).T,
                    [full["reference_ci"]["mean_mg_dl"],full["reference_ci"]["tail_pct"]],atol=1e-7,rtol=0)
        records[name]={"separate_reader_rows":len(d),"mean_and_integer_count_match":True,"bootstrap_intervals_match":True}
    tc_marg=hdl_marg=None;arrays=0
    for arm,record in seal["arms"].items():
        means=[];tails=[];ratios=[]
        for draw in record["runs"]:
            path=HERE/f"private/{arm}-{draw['seed']}.npy";assert sha(path)==draw["array_sha256"]
            t,h=np.load(path,allow_pickle=False).T
            if tc_marg is None:tc_marg,hdl_marg=t.copy(),np.sort(h)
            assert np.array_equal(t,tc_marg) and np.array_equal(np.sort(h),hdl_marg)
            diff=t-h;cnt=int(np.count_nonzero(diff>=160));m=draw["estimates"]
            assert m["tail_count"]==cnt and m["tc_below_hdl"]==int(np.count_nonzero(h>t))
            means.append(fmean(diff));tails.append(100*cnt/len(t));ratios.append(fmean(t/h))
            np.testing.assert_allclose([means[-1],tails[-1],ratios[-1]],[m["mean_mg_dl"],m["tail_pct"],m["mean_tc_over_hdl"]],rtol=0,atol=1e-9)
            arrays+=1
        if record["usable"]:
            m=record["pooled"]
            np.testing.assert_allclose([fmean(means),fmean(tails),fmean(ratios)],[m["mean_mg_dl"],m["tail_pct"],m["mean_tc_over_hdl"]],atol=1e-9,rtol=0)
            for site in result["cohorts"].values():
                assert abs(site["arms"][arm]["tail_gap_pp"]-(fmean(tails)-100*site["reference"]["tail_count"]/site["n"]))<1e-9
    summary={"cohorts":records,"sealed_arrays_recomputed":arrays,"same_tc_and_hdl_marginals":True,"results_sha256":sha(HERE/"RESULTS.json")}
    f=HERE/"VERIFICATION.json"
    if f.exists():assert read(f)==summary
    else:write(f,summary)
    print(summary)
if __name__=="__main__":check()
