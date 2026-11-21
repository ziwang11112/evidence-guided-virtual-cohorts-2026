"""Post-disclosure distance to source-compatible couplings and exact mean decomposition."""
import sys
import numpy as np
from design import HERE, OLD, SENS, PRIVATE, obj, save, text_digest


def outer_range(tc,hdl,cut=160.):
    # Unmatched requirements for threshold t >= h+c give the largest attainable win count.
    # A loss requires h+c > t (strict). The complement of the largest loss matching gives the minimum.
    t=np.sort(tc); x=np.sort(hdl+cut); n=len(t)
    supply=n-np.searchsorted(t,x,side="left")
    demand=n-np.searchsorted(x,x,side="left")
    missing=max(0,int(np.max(demand-supply)))
    t_demand=n-np.searchsorted(t,t,side="left")
    strict_x=n-np.searchsorted(x,t,side="right")
    minwin=max(0,int(np.max(t_demand-strict_x)))
    return [100*minwin/n,100*(n-missing)/n]


def gap(p,interval):
    return max(interval[0]-p, p-interval[1], 0.)


def main():
    assert (HERE/"REFERENCE_OPEN.json").exists()
    from admission import data
    from itertools import permutations
    # Exact integer matching fixture including repeated values exactly at the cutoff.
    toy_t=np.array([200.,201.,203.,203.]);toy_h=np.array([40.,41.,42.,50.])
    actual=[100*((toy_t-np.array(h))>=160).mean() for h in permutations(toy_h)]
    np.testing.assert_allclose(outer_range(toy_t,toy_h),[min(actual),max(actual)])
    sys.path.insert(0,str(OLD))
    from science import values
    tc,hdl=values()
    outer=outer_range(tc,hdl)
    old_bounds=obj(SENS/"VERIFICATION.json")
    np.testing.assert_allclose(outer,old_bounds["unrestricted_outer_percent"])
    examples=obj(SENS/"CONTROL.json")["constructive_examples"]
    controls=[examples[n]["score"] for n in ("low","high")]
    ret={}; sources=obj(SENS/"SENSITIVITY.json")["authors"]
    configurations={k:[r["scenarios"][m] for m in ("a","b")] for k,r in sources.items()}
    configurations["numerical"]=controls
    for key,pair in configurations.items():
        assert all(p["invalid_order"]==0 and 3.655<=p["mean_ratio"]<3.665 for p in pair)
        for q in (0.,.25,.50,.75,1.):
            ratio=(1-q)*pair[0]["mean_ratio"]+q*pair[1]["mean_ratio"]
            mean=(1-q)*pair[0]["mean"]+q*pair[1]["mean"]
            assert 3.655<=ratio<3.665 and np.isclose(mean,tc.mean()-hdl.mean())
        ret[key]=sorted(p["percent"] for p in pair)
    inner=ret["numerical"]
    assert outer[0]<=inner[0]<inner[1]<=outer[1]
    past=obj(OLD/"REPLAY_RESULTS.json")["cohorts"]
    us=obj(HERE/"RESULTS.json")["estimates"]
    cohort={}
    for site,row in past.items():
        measured=np.load(OLD/"private"/(site+"-eligible.npy"),allow_pickle=False)[:,1:3]
        cohort[site]=(row["reference"]["tail_pct"],row["reference_ci"]["tail_pct"],row["reference"]["mean_mg_dl"],measured)
    _,keep=data()
    for k,r in us.items():
        subset=keep if k=="all" else keep[keep.location==k]
        measured=subset[["chol","hdl"]].to_numpy(dtype=float)
        rate=r["scales"]["1.0"]["nonhdl160"];mean=r["scales"]["1.0"]["mean_nonhdl"]
        cohort["Virginia" if k=="all" else k]=(rate["measured"],rate["measured_ci"],mean["measured"],measured)
    rows={}
    for site,(pct,ci,mu,observed) in cohort.items():
        t1,h1=observed.T
        np.testing.assert_allclose([100*(t1-h1>=160).mean(),(t1-h1).mean()],[pct,mu])
        contributions=[float(t1.mean()-tc.mean()),float(hdl.mean()-h1.mean())]
        np.testing.assert_allclose(sum(contributions),mu-(tc.mean()-hdl.mean()))
        nearest=gap(pct,outer)
        interval_gap=max(ci[0]-outer[1],outer[0]-ci[1],0.)
        rows[site]={"n":len(observed),"pct":pct,"ci":ci,"achievable_by_mixture_interval_contains_ci":bool(inner[0]<=ci[0]<=ci[1]<=inner[1]),
                    "agent_pairs_bracketing_point":sum(lo<=pct<=hi for name,(lo,hi) in ret.items() if name!="numerical"),
                    "unrestricted_lower_bound_on_error_pp_at_point":nearest,"minimum_distance_of_ci_to_outer_pp":interval_gap,
                    "unattainable_even_at_plusminus_2pp_for_point":bool(nearest>2.),
                    "unattainable_even_at_plusminus_2pp_for_whole_ci":bool(interval_gap>2.),
                    "target_minus_source_TC_mg_dl":contributions[0],"source_minus_target_HDL_mg_dl":contributions[1],
                    "target_minus_source_nonHDL_mg_dl":sum(contributions)}
    report={"retrospective":True,"target_models_fitted":0,"outer":outer,"feasible_ranges":ret,
            "width_covered_by_control":(inner[1]-inner[0])/(outer[1]-outer[0]),"three_frames_and_two_nested_counties":rows,
            "old_bound_receipt_sha256":text_digest(SENS/"VERIFICATION.json")}
    path=HERE/"PAIRING_AUDIT.json"
    if path.exists():
        assert obj(path)==report
    else:
        save(path,report)
    for key,row in rows.items():
        print(key, round(row["pct"],2),[round(x,2) for x in row["ci"]],round(row["unrestricted_lower_bound_on_error_pp_at_point"],3),
              [round(row[c],3) for c in ("target_minus_source_TC_mg_dl","source_minus_target_HDL_mg_dl","target_minus_source_nonHDL_mg_dl")])


if __name__=="__main__":
    main()
