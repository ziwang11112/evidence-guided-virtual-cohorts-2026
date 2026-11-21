"""Post-disclosure within-record audit of which simulated people cross the cutoff."""
import numpy as np
import pyreadstat

from common import ALT, HERE, PERIODS, PRIVATE, pairings, read, save, source
from survey import gain, gain_range


def component_means(suffix):
    import pandas as pd
    raw=lambda key:pyreadstat.read_xport(str(PRIVATE/"reference"/f"{key}_{suffix}.xpt"),encoding="WINDOWS-1252")[0].set_index("SEQN")
    dm,tc,hdl=(raw(s) for s in ("DEMO","TCHOL","HDL"))
    joined=pd.concat([dm.RIDAGEYR,tc.LBXTC,hdl.LBDHDD,dm.WTMEC2YR if suffix=="J" else tc.WTPH2YR],axis=1)
    joined.columns=["age","tc","hdl","w"]
    f=joined.query("age>=20 and tc>0 and hdl>0 and w>0").copy()
    f["age_group"]=np.digitize(f.age,[40,60])
    weights=np.asarray([.396579,.371795,.231626])
    means=np.vstack([np.average(group[["tc","hdl"]],axis=0,weights=group.w) for _,group in f.groupby("age_group")])
    return (weights@means).tolist()


def main():
    estimates=read(HERE/"RESULTS.json")["reference"]
    predictions=read(HERE/"PREDICTIONS.json")["predictions"]
    tc,hd=source.values()
    a,b=np.asarray(predictions["statistical"]["marginal_means"])/[np.mean(tc),np.mean(hd)]
    assert a>1>b>0
    careas={}
    for suffix,study in estimates.items():
        means=component_means(suffix)
        np.testing.assert_allclose(means[0]-means[1],study["estimates"]["mean_nonhdl"]["estimate"],atol=1e-10)
        careas[suffix]={"tc":means[0],"hdl":means[1]}
    rows={}
    for law,perms in pairings().items():
        counts=[]
        v0=predictions["base"]["pairings"][law]["values"]
        v1=predictions["statistical"]["pairings"][law]["values"]
        np.testing.assert_allclose(v1["mean_ratio"],(a/b)*v0["mean_ratio"],rtol=1e-12)
        np.testing.assert_allclose(v1["rank_tc_hdl"],v0["rank_tc_hdl"],atol=1e-12)
        for perm in perms:
            h=hd[perm]
            before=(tc-h)>=160.
            after=(a*tc-b*h)>=160.
            boundary=(tc>=(160.+b*h)/a)&(tc<160.+h)
            assert np.array_equal(boundary,after&~before)
            counts.append({"n":len(tc),"entered":int(np.sum(boundary)),"left":int(np.sum(before&~after)),
                           "order_invalid_before":int(np.sum(tc<h)),"order_invalid_after":int(np.sum(a*tc<b*h))})
        original=predictions["base"]["pairings"][law]["values"]["nonhdl160"]
        rescaled=predictions["statistical"]["pairings"][law]["values"]["nonhdl160"]
        n=sum(c["n"] for c in counts)
        entered=sum(c["entered"] for c in counts)
        assert all(c["left"]==0 for c in counts)
        np.testing.assert_allclose(rescaled-original,100*entered/n,rtol=0,atol=1e-10)
        for method in ("author1","author2","author3","author4"):
            np.testing.assert_allclose(predictions[method]["pairings"][law]["values"]["nonhdl160"],rescaled,atol=1e-10)
        score={}
        for suffix,study in estimates.items():
            obs=study["estimates"]["nonhdl160"]
            score[suffix]={"gain_pp":gain(original,[rescaled],obs["estimate"]),
                           "range_over_ci_pp":gain_range(original,[rescaled],obs["ci"])}
        rows[law]={"before_pct":original,"after_pct":rescaled,"switched_pct":100*entered/n,
                   "entered":entered,"left":0,"n":n,"runs":counts,"gain":score}
    pairs={}
    for name in read(ALT/"SENSITIVITY.json")["authors"]:
        low,high=sorted((name+"_"+c for c in ("a","b")),key=lambda p:rows[p]["before_pct"])
        pairs[name]={"lower":low,"higher":high}
    summary={}
    for which in ("lower","higher"):
        selected=[rows[x[which]]["gain"] for x in pairs.values()]
        summary[which]={"closer_both_points":sum(all(v[p]["gain_pp"]>0 for p in PERIODS) for v in selected),
                        "closer_over_both_intervals":sum(all(v[p]["range_over_ci_pp"][0]>0 for p in PERIODS) for v in selected),
                        "farther_both_points":sum(all(v[p]["gain_pp"]<0 for p in PERIODS) for v in selected),
                        "farther_over_both_intervals":sum(all(v[p]["range_over_ci_pp"][1]<0 for p in PERIODS) for v in selected)}
    save(HERE/"PAIRING_DIAGNOSTIC.json",{"scope":"retrospective explanation of the sealed nine-law comparison","tc_multiplier":float(a),
         "hdl_multiplier":float(b),"measured_component_means":careas,"by_pairing":rows,"ordered_within_author":pairs,"counts":summary})
    print(summary,careas)


if __name__=="__main__":
    main()
