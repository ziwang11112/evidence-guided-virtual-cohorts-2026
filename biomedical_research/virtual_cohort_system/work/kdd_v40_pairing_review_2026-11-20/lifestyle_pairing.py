"""Remove age–outcome pairing within sex-by-lifestyle cells without changing the cells."""
import csv
import hashlib
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / "lifestyle_application_2026-11-11"
STATS = HERE.parent / "matched_size_utility_2026-11-17/CONTRAST_SUMMARIES.csv"
sys.path.insert(0, str(OLD))
import analysis_operator as original


def fixture():
    x=np.array([[1.,0.,1.],[1.,0.,2.],[1.,1.,1.],[1.,1.,3.]])
    y=np.array([1.,4.,2.,7.])
    B=np.linalg.pinv(x)
    scores=[(B @ np.r_[a,b])[1] for a in itertools.permutations(y[:2]) for b in itertools.permutations(y[2:])]
    expectation=(B@np.repeat([y[:2].mean(),y[2:].mean()],2))[1]
    np.testing.assert_allclose(expectation,np.mean(scores),atol=1e-12,rtol=0)


def analyze():
    fixture()
    slots=json.loads((OLD/"FINAL_TABLES.json").read_text(encoding="utf-8"))["slots"]
    assert len(slots)==6 and all(s["status"]=="success" for s in slots)
    summaries=pd.read_csv(STATS)
    all_rows=[]
    for s in slots:
        path=OLD/s["generated_path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest()==s["generated_sha256"]
        data=pd.read_csv(path)
        traits=original.TRAITS
        assert len(data)==1226 and data.age.gt(18).all() and data[traits].gt(0).all().all() and np.isfinite(data[traits]).all().all()
        y=data[traits].to_numpy()
        means=data.groupby(["lifestyle","sex"],observed=True)[traits].transform("mean").to_numpy()
        design=np.column_stack((np.ones(len(data)), data.lifestyle.eq("rural_nonpastoralist"),
                                data.lifestyle.eq("urban_nonpastoralist"),data.age,data.sex.eq("F")))
        assert np.linalg.matrix_rank(design)==5
        before=np.linalg.lstsq(design,y,rcond=None)[0]
        after=np.linalg.lstsq(design,means,rcond=None)[0]
        # Independent form: all cell-constant columns have zero residual inner product.
        # Only the age column survives in X'(Y - cell mean).
        xt_res=np.zeros((design.shape[1],len(traits)))
        for _,grp in data.groupby(["lifestyle","sex"],observed=True):
            ar=grp.age.to_numpy()
            block=grp[traits].to_numpy()
            xt_res[3]+=(ar-ar.mean())@(block-block.mean(axis=0))
        correction=np.linalg.solve(design.T@design,xt_res)
        np.testing.assert_allclose(before-after,correction,atol=2e-9,rtol=0)
        raw_operator=original.analyze_frame(data)
        original_scales={r["trait"]:r["sample_sd"] for r in raw_operator["trait_status"]}
        original_estimates={(r["trait"],r["contrast"]):r["estimate"]*original_scales[r["trait"]] for r in raw_operator["contrasts"] if r["stratum"]=="pooled"}
        stream=s["episode_id"]+"_s"+str(s["seed"])
        for contrast, weights in original.CONTRASTS:
            for j,trait in enumerate(traits):
                sel=summaries[(summaries.trait==trait)&(summaries.contrast==contrast)]
                reference=sel[sel.comparison=="real_real"].iloc[0]
                archived=sel[sel.stream==stream].iloc[0]
                b=float(weights@before[:,j]); a=float(weights@after[:,j])
                np.testing.assert_allclose([b,b],[original_estimates[(trait,contrast)],archived.original_other],atol=1e-9,rtol=0)
                all_rows.append({"author":s["episode_id"],"seed":s["seed"],"trait":trait,"contrast":contrast,
                                 "authored":b,"expected_after_repairing":a,"pairing_contribution":b-a,
                                 "measured":float(reference.original_real),"real_real_mad":float(reference.absolute_mean),
                                 "absolute_change_in_real_real_units":abs(b-a)/reference.absolute_mean})
    assert len(all_rows)==54
    with (HERE/"LIFESTYLE_PAIRING.csv").open("x",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(all_rows[0]),lineterminator="\n")
        writer.writeheader();writer.writerows(all_rows)


if __name__=="__main__":
    analyze()
