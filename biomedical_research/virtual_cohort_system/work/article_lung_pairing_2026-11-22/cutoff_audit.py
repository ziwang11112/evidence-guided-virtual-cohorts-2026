"""Post-outcome descriptive audit of local mass around the screening cutoff. No model changes."""
import json
from pathlib import Path
from statistics import median

import numpy as np
import verify

D=Path(__file__).resolve().parent
LEVELS=(.69,.695,.70,.705,.71)


def main():
    results=verify.load(D/"RESULTS.json")
    receipt=verify.load(D/"VERIFICATION.json")
    assert verify.sha(D/"RESULTS.json")==receipt["results_sha256"]
    models={}
    for slot,m in results["models"].items():
        if not m["usable"]:continue
        obj=verify.load(D/"private/api/calls"/slot/"artifact.json")
        rows=[]
        for draw in m["draws"]:
            p=D/"private/draws"/slot/str(draw["seed"])/"run/output/generated.csv"
            assert verify.sha(p)==draw["sha256"]
            orders=verify.load_pairs(p,8000)
            parts=[]
            for sex,idx in zip(("F","M"),orders,strict=True):
                c=obj["model_spec"]["cells"][sex]
                x,y=verify.grid_pair(c["fvc_mean"],c["fvc_sd"],c["slope"],c["intercept_l"],c["r2_pct"],8000)
                ratios=x/y[idx]
                parts.append([100*np.mean(ratios<v) for v in LEVELS])
            prevalences=np.mean(parts,axis=0)
            assert abs(prevalences[2]-draw["outcome"]["percent"])<1e-10
            rows.append(prevalences)
        v=np.mean(rows,axis=0)
        models[slot]={"mean_across_three_seeds_pct":dict(zip(map(str,LEVELS),v.tolist())),
                      "pct_in_0695_to_0705":float(v[3]-v[1]),
                      "pct_in_069_to_071":float(v[4]-v[0])}
    med={}
    for role in ("initial","ordinary","alternative"):
        subset=[v for k,v in models.items() if k.endswith("_"+role)]
        med[role]={k:median(row[k] for row in subset) if subset else None
                   for k in ("pct_in_0695_to_0705","pct_in_069_to_071")}
    output={"status":"exploratory_after_primary_outcomes_known","cutoffs":list(LEVELS),
            "intervals":"lower-inclusive, upper-exclusive","registered_results_sha256":receipt["results_sha256"],
            "per_slot":models,"median_over_eligible_authors":med}
    f=D/"CUTOFF_AUDIT.json"
    if f.exists():assert verify.load(f)==output
    else:f.write_text(json.dumps(output,indent=2)+"\n",encoding="utf8",newline="\n")
    print(json.dumps(med,indent=2))


if __name__=="__main__":main()
