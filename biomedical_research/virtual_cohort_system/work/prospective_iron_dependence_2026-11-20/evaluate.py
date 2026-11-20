"""Reveal the measured reference after closure and run the prespecified paired comparison."""
import math

import numpy as np
import pandas as pd
from scipy.stats import rankdata

from admission import eligible
from science import HERE, PARENTS, endpoints, read


def gain(reference,statistical,agent_estimates):
    if len(agent_estimates)==0:
        return None
    return float(abs(statistical-reference)-np.median(np.abs(np.asarray(agent_estimates)-reference)))


def resample(target,statistical,agents,replicates=2000,seed=201121):
    rng=np.random.default_rng(seed)
    target=target.reset_index(drop=True)
    locations=[list(local.groupby("EA",sort=True).groups.values()) for _,local in target.groupby("LGA",sort=True)]
    observations=target[["HGB","FER_ug_L"]].to_numpy()
    boot=[]
    for _ in range(replicates):
        groups=[g[i] for g in locations for i in rng.integers(0,len(g),size=len(g))]
        sample=observations[np.concatenate(groups)]
        s=endpoints(sample)
        boot.append([s["rank"],np.nan if not s["odds_ratio"] else s["odds_ratio"],
                     np.nan if not agents else gain(s["rank"],statistical,agents)])
    data=np.asarray(boot)
    def interval(column):
        ok=np.isfinite(data[:,column])
        return {"finite":int(ok.sum()),"percentile95":np.quantile(data[ok,column],[.025,.975]).tolist() if ok.any() else None}
    return {k:interval(i) for i,k in enumerate(("reference_rank","reference_odds_ratio","gain"))}


def evaluation_fixture():
    slopes=[.1,.3,.3]
    assert math.isclose(gain(.3,.2,slopes),.1) and math.isclose(gain(.1,.1,slopes),-.2)
    assert gain(.1,.1,[]) is None
    d=pd.DataFrame({"LGA":[1,1,1,1,2,2,2,2],"EA":[1,1,2,2,1,1,2,2],
                    "HGB":[10,11,12,15,11,15,9,12],"FER_ug_L":[8,21,34,12,9,30,11,15]})
    v=resample(d,.2,[.1,.3],24)
    assert v["gain"]["finite"]==24
    np.testing.assert_allclose(endpoints(d[["HGB","FER_ug_L"]].to_numpy())["rank"],d.HGB.rank().corr(d.FER_ug_L.rank()),rtol=1e-12)


def reveal():
    from study import PRIVATE,guard,now,save,sha
    frozen=guard()
    closure=read(HERE/"DRAW_CLOSURE.json")
    assert closure["freeze_sha256"]==sha(HERE/"FREEZE.json") and closure["authors_sha256"]==sha(HERE/"AUTHORS.json")
    assert not (HERE/"RESULTS.json").exists()
    if not any(closure["models"][cid]["usable"] for cid in PARENTS):
        raise RuntimeError("No executable Agent law. The measured reference stays sealed.")
    data=PRIVATE/"biochem.dta"
    assert sha(data)==frozen["target_data_sha256"]==read(HERE/"ADMISSION.json")["files"]["biochem.dta"]["sha256"]
    opened=HERE/"REFERENCE_OPEN.json"
    if not opened.exists():
        save(opened,{"utc":now(),"closure_sha256":sha(HERE/"DRAW_CLOSURE.json"),"freeze_sha256":sha(HERE/"FREEZE.json"),
                     "evaluator_action":"first authorized evaluation; no subsequent construction"})
    assert read(opened)["closure_sha256"]==sha(HERE/"DRAW_CLOSURE.json")
    target=eligible(pd.read_stata(data,convert_categoricals=False))
    expected=read(HERE/"ADMISSION.json")
    assert len(target)==expected["eligible_complete_positive"]
    ref=endpoints(target[["HGB","FER_ug_L"]].to_numpy())
    models=closure["models"]
    ok=[cid for cid in PARENTS if models[cid]["usable"]]
    stat=models["statistical"]["pooled"]
    assert all(models[c]["pooled"]["cells"]==stat["cells"] for c in ok)
    agents=[models[c]["pooled"]["rank"] for c in ok]
    bt=resample(target,stat["rank"],agents)
    delta=gain(ref["rank"],stat["rank"],agents)
    can_guard=bool(min(ref["cells"])>=10 and ref["odds_ratio"] and stat["odds_ratio"])
    or_factor=math.exp(abs(math.log(stat["odds_ratio"]/ref["odds_ratio"]))) if ref["odds_ratio"] and stat["odds_ratio"] else None
    guard_ok=bool(can_guard and or_factor<=1.50)
    checks={"four_authors":len(ok)>=4,"point_gain_at_least_0.02":delta is not None and delta>=.02,
            "lower95_above_zero":bool(bt["gain"]["percentile95"] and bt["gain"]["percentile95"][0]>0),
            "all_bootstrap_gain_finite":bt["gain"]["finite"]==2000,"threshold_guard":guard_ok}
    by_law={}
    for c in ["statistical",*PARENTS]:
        m=models[c]
        by_law[c]={"usable":m["usable"]}
        if m["usable"]:
            z=m["pooled"]
            by_law[c].update(rank=z["rank"],absolute_rank_error=abs(z["rank"]-ref["rank"]),
                             source_middle_ratio=z["middle_ratio"],odds_ratio=z["odds_ratio"])
        else:by_law[c]["reason"]=m["reason"]
    result={"utc":now(),"reference_open_sha256":sha(opened),"source_closure_sha256":sha(HERE/"DRAW_CLOSURE.json"),
            "reference":ref,"clusters":expected["enumeration_areas"],"strata":expected["local_government_areas"],
            "by_law":by_law,"median_agent_absolute_error":float(np.median(np.abs(np.array(agents)-ref["rank"]))) if agents else None,
            "gain":delta,"paired_bootstrap":bt,"guard_evaluable":can_guard,"odds_factor":or_factor,
            "decision_checks":checks,"prespecified_advantage_on_this_cohort":all(checks.values()),
            "estimated_usd":read(HERE/"AUTHORS.json")["estimated_usd"]}
    save(HERE/"RESULTS.json",result)
    print("Target",ref,"gain",delta,"95%",bt["gain"],"criteria",checks,flush=True)


if __name__=="__main__":
    reveal()
