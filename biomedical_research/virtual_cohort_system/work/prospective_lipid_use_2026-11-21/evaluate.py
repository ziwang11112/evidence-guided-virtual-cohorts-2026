"""One disclosure, then evaluate every frozen decision at every coverage and tolerance."""
import argparse
import re
import subprocess

import numpy as np

from design import HERE, KEYS, USES, COVER, BOOT, BOOT_SEEDS, PRIVATE, estimands, bootstrap_draws, interval_class, obj, save, now, digest, text_digest


def authenticated_closure(commit):
    if not re.fullmatch(r"[0-9a-f]{40}",commit):
        raise ValueError("A full public closure commit is required")
    repo=HERE.parents[2]/"github_virtual_cohort_2026-10-27"
    tracked="biomedical_research/virtual_cohort_system/work/"+HERE.name+"/DECISION_CLOSURE.json"
    git=["git","-C",str(repo)]
    subprocess.run([*git,"merge-base","--is-ancestor",commit,"origin/main"],check=True)
    data=subprocess.check_output([*git,"show",commit+":"+tracked]).decode("utf-8")
    if data.replace("\r\n","\n")!=(HERE/"DECISION_CLOSURE.json").read_text(encoding="utf-8"):
        raise RuntimeError("Public decisions differ from the local closure")


def select_scores(estim, low, high, predictions, scale):
    rows={}
    for j, k in enumerate(KEYS):
        point=float(predictions[k]["common_virtual"])
        tol=scale*USES[k][2]
        lo,hi=point-high[j],point-low[j]
        rows[k]={"virtual":point,"measured":float(estim[j]),"measured_ci":[float(low[j]),float(high[j])],
                 "difference":float(point-estim[j]),"difference_ci":[float(lo),float(hi)],
                 "tolerance":tol,"absolute_error_in_tolerances":float(abs(point-estim[j])/tol),
                 "status":interval_class(lo,hi,tol)}
    return rows


def score_decision(decision, results):
    ranking=decision["ranking"]
    yes=[k for k in KEYS if decision["uses"][k]["endorse"]]
    def summary(keys):
        return {"n":len(keys),**{s:sum(results[k]["status"]==s for k in keys)
                                for s in ("within","unresolved","contradicted")},
                "mean_error_in_tolerances":float(np.mean([results[k]["absolute_error_in_tolerances"] for k in keys])) if keys else None}
    return {"top_two":ranking[:COVER],"endorsed":yes,"unforced":summary(yes),
            "at_coverage":{str(i):summary(ranking[:i]) for i in range(1,len(KEYS)+1)}}


def main(commit):
    from advisors import guard
    from admission import data
    guard()
    seal=obj(HERE/"DECISION_CLOSURE.json")
    assert seal["freeze_sha256"]==text_digest(HERE/"FREEZE.json") and not seal["target_outcomes_opened"]
    assert seal["statistical_sha256"]==text_digest(HERE/"STATISTICAL_DECISION.json")
    authenticated_closure(commit)
    admission=obj(HERE/"ADMISSION.json")
    assert digest(PRIVATE/"virginia.csv")==admission["csv_sha256"]
    assert digest(PRIVATE/"virginia.sdd")==admission["sdd_sha256"]
    assert len(seal["sessions"])==8
    decision_hash=text_digest(HERE/"DECISION_CLOSURE.json")
    opening=HERE/"REFERENCE_OPEN.json"
    if not opening.exists():
        save(opening,{"time":now(),"public_closure":commit,"decisions_sha256":decision_hash,"csv_sha256":admission["csv_sha256"]})
    else:
        old=obj(opening)
        assert old["public_closure"]==commit and old["decisions_sha256"]==decision_hash
    _,keep=data()
    assert len(keep)==admission["eligible"]
    strata={k:group[["chol","hdl"]].to_numpy(dtype=float) for k,group in keep.groupby("location",sort=True)}
    estimations={}
    for name,seed in BOOT_SEEDS.items():
        groups=list(strata.values()) if name=="all" else [strata[name]]
        observations=np.concatenate(groups)
        points=estimands(*observations.T)
        boot=bootstrap_draws(groups,seed)
        low,high=np.percentile(boot,[2.5,97.5],axis=0)
        estimations[name]={
            "n":len(observations),"hdl_above_tc":int((observations[:,1]>observations[:,0]).sum()),
            "scales":{str(scale):select_scores(points,low,high,obj(HERE/"PACKET.json")["cases"],scale)
                      for scale in (0.5,1.0,2.0)}}
    rules={"statistical":obj(HERE/"STATISTICAL_DECISION.json")}
    rules.update({key:v["decision"] for key,v in seal["sessions"].items() if v["valid"]})
    scores={loc:{scale:{key:score_decision(rule,rows) for key,rule in rules.items()}
                 for scale,rows in item["scales"].items()} for loc,item in estimations.items()}
    report={"public_closure":commit,"reference_open_sha256":text_digest(opening),"bootstrap_repetitions":BOOT,
            "estimates":estimations,"scores":scores,"tariff_usd":sum(x["receipt"]["tariff_cost_usd"] or 0 for x in seal["sessions"].values()),
            "n_calls_without_tariff":sum(x["receipt"]["tariff_cost_usd"] is None for x in seal["sessions"].values()),
            "valid_slots":len(rules)-1,"total_slots":len(seal["sessions"])}
    path=HERE/"RESULTS.json"
    if path.exists():
        assert obj(path)==report
    else:
        save(path,report)
    for k,r in estimations["all"]["scales"]["1.0"].items():
        print(k, round(r["virtual"],3),round(r["measured"],3),[round(x,3) for x in r["measured_ci"]],r["status"])
    for k,d in scores["all"]["1.0"].items():
        print(k,d["top_two"],d["at_coverage"][str(COVER)],"unforced",d["unforced"])


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("public_closure")
    args=p.parse_args()
    main(args.public_closure)
