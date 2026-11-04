"""Invented numerical verification; no participant or generator files."""
from pathlib import Path
import hashlib, json, importlib.util
import numpy as np
import pandas as pd
from scipy.stats import t
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("live_diagnostics",HERE/"generated_diagnostics.py")
d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)

def main():
    rng=np.random.default_rng(3819);n=450
    f=pd.DataFrame({"age":rng.integers(35,75,n),"female":rng.integers(0,2,n),
                    "bmi":rng.uniform(18,35,n),"glucose":rng.uniform(3,9,n)})
    f["hba1c"]=5+.02*(f.bmi-25)+.1*(f.glucose-5)+.002*(f.age-50)+rng.normal(0,.1,n)
    tests=[]
    for request in ["A","B"]:
        r=d.analyze_generated(f,request)
        columns=["bmi","age","female"] if request=="A" else ["bmi","glucose","age","female"]
        x=np.column_stack([np.ones(n),f[columns].to_numpy()]);y=f.hba1c.to_numpy()
        qmat,rmat=np.linalg.qr(x,mode="reduced")
        beta=np.linalg.solve(rmat,qmat.T@y);e=y-x@beta
        leverage=np.sum(qmat*qmat,axis=1)
        rinv=np.linalg.inv(rmat)
        cov=rinv@(qmat.T@(((e/(1-leverage))**2)[:,None]*qmat))@rinv.T
        se=np.sqrt(np.diag(cov));half=t.ppf(.975,n-x.shape[1])*se
        for i,term in enumerate(["const"]+columns):
            row=r["coefficients"][term]
            assert np.isclose(row["value"],beta[i],rtol=1e-10,atol=1e-12)
            assert np.isclose(row["standard_error"],se[i],rtol=1e-10,atol=1e-12)
            assert np.isclose(row["lower"],beta[i]-half[i],rtol=1e-10,atol=1e-12)
            assert np.isclose(row["upper"],beta[i]+half[i],rtol=1e-10,atol=1e-12)
        for v,q in r["marginal"].items():
            assert np.allclose([q["q10"],q["median"],q["q90"]],np.quantile(f[v],[.1,.5,.9],method="linear"))
        for pair,vals in r["relationships"].items():
            v=pair.removesuffix("_hba1c")
            assert np.isclose(vals["pearson"],np.corrcoef(f[v],f.hba1c)[0,1])
            assert np.isclose(vals["spearman"],np.corrcoef(f[v].rank(),f.hba1c.rank())[0,1])
        json.dumps(r,allow_nan=False);tests.append(request+"_numpy_HC3_and_diagnostics")
    bad=f.copy();bad.loc[0,"hba1c"]=0
    assert d.analyze_generated(bad,"A")["status"]=="withheld"
    bad=f.copy();bad["female"]=0
    assert d.analyze_generated(bad,"B")["status"]=="regression_unavailable"
    assert d.analyze_generated(f.head(2),"A")["status"]=="withheld"
    tests.extend(["zero_value_gate","rank_failure","insufficient_n"])
    out={"status":"PASS","tests":tests,"source":"invented in-memory arithmetic fixture, not a scientific construction",
         "diagnostic_sha256":hashlib.sha256((HERE/"generated_diagnostics.py").read_bytes()).hexdigest(),
         "target_reads":0,"network_requests":0,"generated_table_files":0}
    (HERE/"DIAGNOSTIC_SELF_CHECK.json").write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out))
if __name__=="__main__":main()
