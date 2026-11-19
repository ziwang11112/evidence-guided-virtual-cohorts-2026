"""Open the one sealed reference only after a complete source-side closure."""
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from partition import PRIVATE, ROOT, digest, read, save
from science import bootstrap_values, check, interval, measures


def benefit(control, revised, actual):
    return np.abs(control-actual)-np.abs(revised-actual)


def compare(result, control, bridge, truth, rank_boot, source_ratio):
    base, c, e = (z["metrics"] for z in (result,control,bridge))
    rho = truth["rank"]
    guard_available = min(truth["cells"]) >= 10 and all(q["odds_ratio"] is not None for q in (base,c,e))
    guard = False
    if guard_available:
        guard = (abs(np.log(e["odds_ratio"]/truth["odds_ratio"])) <= np.log(1.5) and
                 abs(np.log(e["odds_ratio"]/c["odds_ratio"])) <= np.log(1.2))
    estimates = {}
    for label, s in (("initial",base),("control",c),("evidence",e)):
        estimates[label]={"rank":s["rank"],"rank_error":abs(s["rank"]-rho),"odds_ratio":s["odds_ratio"],
                          "conditional_ratio":s["ratio"],"source_log_ratio_error":abs(np.log(s["ratio"]/source_ratio)) if s["ratio"] else None}
    d=float(benefit(c["rank"],e["rank"],rho))
    bootstrap_changes = benefit(c["rank"],e["rank"],rank_boot)
    return {"estimates":estimates,"initial_to_evidence":float(benefit(base["rank"],e["rank"],rho)),
            "initial_to_control":float(benefit(base["rank"],c["rank"],rho)),
            "control_to_evidence":d,"control_to_evidence_B_sampling_interval":interval(bootstrap_changes),
            "final_rank_tolerance":bool(abs(e["rank"]-rho)<=.10),"guard_evaluable":guard_available,
            "guard_pass":bool(guard) if guard_available else None,
            "final_rank_and_guard_pass":bool(guard and abs(e["rank"]-rho)<=.10)},bootstrap_changes


def reveal():
    from study import lf, verify_freeze, PARENTS
    verify_freeze()
    source=read(ROOT/"SOURCE_CLOSURE.json")
    check(source["parent_closure_lf_sha256"]==lf(ROOT/"PARENTS.json") and source["freeze_lf_sha256"]==lf(ROOT/"FREEZE.json"),
          "Incomplete scientific closure")
    check(len(source["models"])==18,"Unaccounted slots")
    target=PRIVATE/"B.csv"
    check(digest(target)==read(ROOT/"PARTITION.json")["parts"]["B"]["sha256"],"Wrong holdout")
    receipt={"source_closure_lf_sha256":lf(ROOT/"SOURCE_CLOSURE.json"),"target_sha256":digest(target)}
    if not (ROOT/"REFERENCE_OPEN.json").exists():
        save(ROOT/"REFERENCE_OPEN.json",{"utc":datetime.now(timezone.utc).isoformat(),**receipt})
    check(all(read(ROOT/"REFERENCE_OPEN.json")[k]==v for k,v in receipt.items()),"Stale opening")
    f=pd.read_csv(target)
    truth=measures(f)
    boot=bootstrap_values(f,191947)
    ci=interval(boot[:,0])
    precise=ci is not None and (ci[1]-ci[0])/2 <=.10
    scores,groups={},{}
    models=source["models"]
    ref_ratio=read(ROOT/"A_SUPPLEMENT.json")["estimate"]
    for arm in ("ordinary","workflow"):
        gains=[]; good=[]; effects=[]
        for p in (name for name in PARENTS if name.startswith(arm)):
            values=[models[p+tag] for tag in ("","_control","_evidence")]
            if not all(x["usable"] for x in values):
                scores[p]={"complete":False,"failed":[v["id"] for v in values if not v["usable"]]}
                continue
            row,bs=compare(*values,truth,boot[:,0],ref_ratio)
            scores[p]={"complete":True,**row}
            gains.append(row["control_to_evidence"]); good.append(row["final_rank_and_guard_pass"]); effects.append(bs)
        point=float(np.median(gains)) if gains else None
        bounds=interval(np.median(effects,axis=0)) if effects else None
        groups[arm]={"complete_pairs":len(gains),"planned_pairs":3,"median_incremental_gain":point,
                     "median_incremental_B_sampling_interval":bounds,"final_rank_and_guard_passes":sum(good),
                     "material_benefit_rule_pass":bool(len(gains)==3 and bounds is not None and point>=.05 and bounds[0]>0 and sum(good)>=2 and precise)}
    save(ROOT/"RESULTS.json",{"utc":datetime.now(timezone.utc).isoformat(),"reference":{"n":len(f),"communities":int(f.commid.nunique()),
         "cells":truth["cells"],"odds_ratio":truth["odds_ratio"],"odds_interval":interval(boot[:,1]),"guard_evaluable":min(truth["cells"])>=10,
         "rank":truth["rank"],"rank_interval":ci,"precision_rule":precise},"pairs":scores,"arms":groups,
         "estimate_unit":"scientific parent session; intervals conditional on these laws and sampling eligible B communities within nine provinces",
         "api_calls":source["api_calls"],"tariff_usd":source["known_usd"]})
    print("All prespecified outcomes calculated.",flush=True)


if __name__=="__main__":
    reveal()
