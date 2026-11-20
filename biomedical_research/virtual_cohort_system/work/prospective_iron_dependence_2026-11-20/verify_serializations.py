"""Post-reveal investigation of the frozen cross-serialization check; leave it intact."""
import hashlib
import json
from statistics import median

import numpy as np
import pandas as pd
from scipy.stats import rankdata

from admission import FIELDS
from science import HERE, PARENTS, SEEDS, read
from verify import statistics


def digest(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()


def select(frame):
    ok = ((frame.Group.str.strip()=="M") & (frame.SEX==2) & frame.AGE_MOTHER.between(18,49) &
          frame.HGB.gt(0) & frame.FER_ug_L.gt(0) & np.isfinite(frame.HGB) & np.isfinite(frame.FER_ug_L))
    return frame.loc[ok].reset_index(drop=True)


def cluster_intervals(frame, statistical, authors):
    rng = np.random.default_rng(201121)
    strata = []
    for lga in sorted(frame.LGA.unique()):
        subset = frame[frame.LGA==lga]
        strata.append([subset.loc[subset.EA==ea, ["HGB","FER_ug_L"]].to_numpy()
                       for ea in sorted(subset.EA.unique())])
    values = []
    for _ in range(2000):
        draw = np.concatenate([s[i] for s in strata for i in rng.choice(len(s),len(s),replace=True)])
        h,f = draw.T
        rh,rf = rankdata(h), rankdata(f)
        rh-=rh.mean()
        rf-=rf.mean()
        rr=float(np.dot(rh,rf)/(np.linalg.norm(rh)*np.linalg.norm(rf)))
        low_h,low_f=h<12,f<15
        a,b,c,d=[np.count_nonzero(v) for v in (low_h&low_f,low_h&~low_f,~low_h&low_f,~low_h&~low_f)]
        odds=a*d/(b*c) if b*c else np.nan
        delta=abs(statistical-rr)-median(abs(x-rr) for x in authors)
        values.append((rr,odds,delta))
    array=np.array(values)
    return {name:np.nanpercentile(array[:,i],[2.5,97.5]).tolist()
            for i,name in enumerate(("reference_rank","reference_odds_ratio","gain"))}


def main():
    saved=read(HERE/"RESULTS.json")
    sealed=read(HERE/"DRAW_CLOSURE.json")
    admitted=read(HERE/"ADMISSION.json")
    private=HERE/"private"
    for name in ("biochem.dta","biochem.tab"):
        assert digest(private/name)==admitted["files"][name]["sha256"]
    frames={"Stata":select(pd.read_stata(private/"biochem.dta",convert_categoricals=False,columns=FIELDS)),
            "TAB":select(pd.read_csv(private/"biochem.tab",sep="\t",usecols=FIELDS))}
    x,y=frames.values()
    assert len(x)==len(y)==603
    np.testing.assert_array_equal(x[["LGA","EA","ID"]].to_numpy(),y[["LGA","EA","ID"]].to_numpy())
    variance={}
    for name in ("HGB","FER_ug_L"):
        a,b=x[name].to_numpy(),y[name].to_numpy()
        ra,rb=rankdata(a),rankdata(b)
        variance[name]={"unique_stata":len(np.unique(a)),"unique_tab":len(np.unique(b)),
                        "records_with_different_midrank":int(np.count_nonzero(ra!=rb)),
                        "max_midrank_difference":float(np.max(np.abs(ra-rb))),
                        "max_abs_measurement_representation_difference":float(np.max(np.abs(a-b)))}
    ranks={}
    unique_draws=set()
    for name in ["statistical",*PARENTS]:
        model=sealed["models"][name]
        assert model["usable"]
        parts=[];author_hashes=[]
        for seed,run in zip(SEEDS,model["runs"],strict=True):
            path=private/"cohorts"/name/f"{seed}.npy"
            hashed=digest(path)
            assert hashed==run["npy_sha256"]
            author_hashes.append(hashed)
            arr=np.load(path,allow_pickle=False);parts.append(arr)
            base=np.load(private/"cohorts"/"statistical"/f"{seed}.npy",allow_pickle=False)
            np.testing.assert_array_equal(base[:,0],arr[:,0])
            for use in (base[:,0]<12,(base[:,0]>=12)&(base[:,0]<14),base[:,0]>=14):
                np.testing.assert_array_equal(np.sort(base[use,1]),np.sort(arr[use,1]))
            rr,cells,orr=statistics(*arr.T)
            assert cells==run["estimates"]["cells"]
            np.testing.assert_allclose(rr,run["estimates"]["rank"],rtol=0,atol=1e-12)
        if name!="statistical":unique_draws.add(tuple(author_hashes))
        rank,cells,odds=statistics(*np.vstack(parts).T)
        ranks[name]=rank
        assert cells==sealed["models"]["statistical"]["pooled"]["cells"]
        np.testing.assert_allclose([rank,odds],[saved["by_law"][name]["rank"],saved["by_law"][name]["odds_ratio"]],rtol=0,atol=1e-12)
    authors=[ranks[n] for n in PARENTS]
    outputs={}
    for name,f in frames.items():
        rank,cells,odds=statistics(f.HGB,f.FER_ug_L)
        delta=abs(ranks["statistical"]-rank)-median(abs(z-rank) for z in authors)
        conf=cluster_intervals(f,ranks["statistical"],authors)
        ratio=float(np.exp(np.log(f.loc[f.HGB.between(13,14,inclusive="left"),"FER_ug_L"]).mean()
                           -np.log(f.loc[f.HGB.between(12,13,inclusive="left"),"FER_ug_L"]).mean()))
        assert cells==saved["reference"]["cells"]
        if name=="Stata":
            for law,expected in saved["by_law"].items():
                np.testing.assert_allclose(abs(rank-ranks[law]),expected["absolute_rank_error"],atol=1e-12,rtol=0)
            np.testing.assert_allclose([rank,odds,delta,ratio],[saved["reference"]["rank"],saved["reference"]["odds_ratio"],saved["gain"],saved["reference"]["middle_ratio"]],atol=1e-12,rtol=0)
            for key,interval in conf.items():
                np.testing.assert_allclose(interval,saved["paired_bootstrap"][key]["percentile95"],atol=1e-11,rtol=0)
        odds_s=saved["by_law"]["statistical"]["odds_ratio"]
        decision=len(authors)>=4 and delta>=.02 and conf["gain"][0]>0 and min(cells)>=10 and max(odds_s/odds,odds/odds_s)<=1.5
        assert decision==saved["prespecified_advantage_on_this_cohort"]
        outputs[name]={"rank":rank,"cells":cells,"odds_ratio":odds,"gain":delta,"middle_ratio":ratio,
                       "paired_bootstrap":conf,"prespecified_advantage_on_this_cohort":decision}
    assert variance["HGB"]["records_with_different_midrank"]==0
    diff=abs(outputs["Stata"]["rank"]-outputs["TAB"]["rank"])
    receipt={"results_sha256":digest(HERE/"RESULTS.json"),"initial_frozen_verifier":"cross-serialization 1e-12 rank assertion failed",
             "difference_in_measured_rank":diff,"serialization_comparison":variance,"both_official_formats":outputs,
             "same_stata_representation_independently_recomputed":True,"distinct_agent_table_triplets":len(unique_draws),
             "virtual_draws_audited":len(SEEDS)*len(ranks),"all_per_seed_within_band_marginal_multisets_exact":True,
             "bootstrap_replicates_per_reference":2000,"all_six_slots_scored":True,"no_changes_to_frozen_outcomes":True}
    out=HERE/"VERIFICATION_ADDENDUM.json"
    if not out.exists():
        with out.open("x",encoding="utf-8",newline="\n") as h:json.dump(receipt,h,indent=2);h.write("\n")
    assert receipt==read(out)
    print("Recovered the primary result from Stata and independently scored TAB.",diff,variance["FER_ug_L"],"verified draws",receipt["virtual_draws_audited"])


if __name__=="__main__":
    main()
