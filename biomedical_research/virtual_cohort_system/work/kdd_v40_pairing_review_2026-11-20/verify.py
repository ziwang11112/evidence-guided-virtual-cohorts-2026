"""Independently score every saved assignment from native CSVs and the optimizer indices."""
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/"nonhdl_external_2026-11-20"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def finite_margins():
    source=read(OLD/"SOURCE.json")
    n=16000
    normal=statistics.NormalDist()
    quantiles=[normal.inv_cdf((i+.5)/n) for i in range(n)]
    result=[]
    for mean,cut,p in [(source["tc_mean"]["estimate"],6.2,1-source["tc_high_pct"]["estimate"]/100),
                       (source["hdl_mean"]["estimate"],1.,source["hdl_low_pct"]["estimate"]/100)]:
        z=normal.inv_cdf(p)
        d=math.sqrt(z*z-2*math.log(cut/mean))
        s=min(v for v in (z-d,z+d) if v>0)
        unscaled=[math.exp(s*q) for q in quantiles]
        scale=mean*source["cholesterol_mg_dl_per_mmol_l"]/statistics.mean(unscaled)
        result.append([v*scale for v in unscaled])
    tc,hdl=result
    high=100*sum(x>=6.2*38.67 for x in tc)/n
    low=100*sum(x<38.67 for x in hdl)/n
    assert round(high,1)==source["tc_high_pct"]["estimate"] and round(low,1)==source["hdl_low_pct"]["estimate"]
    for column,key in ((tc,"tc_mean"),(hdl,"hdl_mean")):
        assert abs(statistics.mean(column)-source[key]["estimate"]*38.67)<1e-9
    return tc,hdl,{"tc_high_percent":high,"hdl_low_percent":low}


def verify_assignment(ix,t,h,stored):
    n=len(t)
    assert len(ix)==n and sorted(ix)==list(range(n))
    nonhdl=[a-h[j] for a,j in zip(t,ix,strict=True)]
    counts=sum(x>=160 for x in nonhdl)
    ratio=math.fsum(a/h[j] for a,j in zip(t,ix,strict=True))/n
    invalid=sum(x<0 for x in nonhdl)
    assert counts==stored["tail_count"] and invalid==stored["invalid_order"]
    for x,y in [(ratio,stored["mean_ratio"]),(statistics.mean(nonhdl),stored["mean"]),(100*counts/n,stored["percent"])]:
        assert math.isclose(x,y,abs_tol=1e-9,rel_tol=0)
    return ratio,100*counts/n,invalid


def main():
    t,h,margins=finite_margins()
    r=read(HERE/"SENSITIVITY.json")
    a=read(HERE/"AUTHORS.json")["records"]
    assert len(r["authors"])==len(a)==4
    checked=0
    distinct_counts={}
    for slot,data in r["authors"].items():
        valid={}
        charges=read(HERE/"private/api/calls"/slot/"receipt.json")
        assert charges["tariff_cost_usd"]==a[slot]["tariff_cost_usd"]
        for mode,runs in data["runs"].items():
            stats=[]
            identities=[]
            for row in runs:
                f=HERE/"private/draws"/slot/mode/str(row["seed"])
                if "score" not in row:
                    assert "reason" in row and not (f/"perm.npy").exists()
                    continue
                path=f/"run/output/generated.csv"
                assert sha(path)==row["output_hash"] and row["permutation_hash"]==sha(f/"perm.npy")
                with path.open(encoding="utf8",newline="") as handle:
                    records=list(csv.DictReader(handle))
                ix=[int(record["hdl_index"]) for record in records]
                assert all(int(record["row_id"])==i for i,record in enumerate(records))
                assert np.array_equal(ix,np.load(f/"perm.npy",allow_pickle=False))
                stats.append(verify_assignment(ix,t,h,row["score"]))
                checked+=1
                identities.append(row["permutation_hash"])
            distinct_counts[slot+"_"+mode]=len(set(identities))
            ratios=[q[0] for q in stats]
            valid[mode]=len(stats)==3 and not any(q[2] for q in stats) and all(3.64-1e-12<=q<=3.68+1e-12 for q in ratios) and 3.655<=statistics.mean(ratios)<3.665
            assert valid[mode]==data["scenarios"][mode]["pass"]
        diffs=[b["score"]["percent"]-aa["score"]["percent"] for aa,b in zip(data["runs"]["a"],data["runs"]["b"]) if "score" in aa and "score" in b]
        material=all(valid.values()) and len(diffs)==3 and ((statistics.mean(diffs)>4 and min(diffs)>2) or (statistics.mean(diffs)<-4 and max(diffs)<-2))
        assert material==data["material"]
    examples=read(HERE/"CONTROL.json")["constructive_examples"]
    for name,control in examples.items():
        if "score" in control:
            path=HERE/"private/control"/(name+".npy")
            assert sha(path)==control["permutation_hash"]
            verify_assignment(np.load(path,allow_pickle=False).tolist(),t,h,control["score"])
            assert control["score"]["invalid_order"]==0 and 3.655<=control["score"]["mean_ratio"]<3.665
    # A finite matching minimizes/maximizes the number of values reaching the cutoff.
    # Each monotone matching counts the possible wins, using strict inequality for the complement.
    wins=misses=0
    for hi in h:
        if misses<len(t) and t[misses]-hi<160:
            misses+=1
    for ti in t:
        if wins<len(h) and ti-h[wins]>=160:
            wins+=1
    outer=[100*(len(t)-misses)/len(t),100*wins/len(t)]
    assert np.allclose(outer,read(OLD/"CLOSURE.json")["all_pairing_tail_bounds_pct"])
    low,high=[examples[k]["score"]["percent"] for k in ("low","high")]
    assert outer[0]<=low<=high<=outer[1]
    record={"verified_author_draws":checked,"constructive_controls_checked":2,"distinct_draws_per_scenario":distinct_counts,
            "source_marginal_cutoffs":margins,"unrestricted_outer_percent":outer,
            "feasible_span_pp":high-low,"unrestricted_span_pp":outer[1]-outer[0],
            "feasible_span_fraction_of_outer":(high-low)/(outer[1]-outer[0]),
            "author_slots":4,"material_authors":sum(v["material"] for v in r["authors"].values()),
            "tariff_usd":sum(v["tariff_cost_usd"] for v in a.values()),"uses_target_inputs":False}
    path=HERE/"VERIFICATION.json"
    if path.exists():
        assert read(path)==record
    else:
        path.write_text(json.dumps(record,indent=2)+"\n",encoding="utf8",newline="\n")
    print(json.dumps(record,indent=2))


if __name__=="__main__":
    main()
