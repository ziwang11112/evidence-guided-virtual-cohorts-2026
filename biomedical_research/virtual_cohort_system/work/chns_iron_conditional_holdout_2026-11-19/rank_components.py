"""Post-reveal descriptive decomposition of the already scored Spearman correlation."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent


def components(frame, expected):
    z=[]
    for name in ("hb_g_dl","ferritin_ug_l"):
        r=frame[name].rank(method="average").to_numpy()
        z.append((r-r.mean())/r.std(ddof=0))
    x,y=z
    band=np.digitize(frame.hb_g_dl,[12.0,14.0])
    between=0.; inside=[]
    for k in range(3):
        mask=band==k
        a,b=x[mask],y[mask]
        between+=mask.mean()*a.mean()*b.mean()
        inside.append(float(mask.mean()*np.mean((a-a.mean())*(b-b.mean()))))
    assert abs(between+sum(inside)-expected)<1e-12
    # Independently partition the global covariance using fitted group means and residuals.
    global_ranks=frame[["hb_g_dl","ferritin_ug_l"]].rank(pct=True)
    fitted=global_ranks.groupby(band).transform("mean")
    residual=global_ranks-fitted
    centers=fitted-global_ranks.mean()
    scale=global_ranks.std(ddof=0).prod()
    assert abs(centers.prod(axis=1).mean()/scale-between)<1e-12
    other=residual.prod(axis=1).groupby(band).sum()/(len(frame)*scale)
    np.testing.assert_allclose(other.to_numpy(),inside,atol=1e-12,rtol=0)
    return {"rho":expected,"between_hb_bands":float(between),"within_bands_low_mid_high":inside}


def run():
    results=json.loads((ROOT/"RESULTS.json").read_text(encoding="utf8"))
    laws=json.loads((ROOT/"SOURCE_CLOSURE.json").read_text(encoding="utf8"))["models"]
    truth=components(pd.read_csv(ROOT/"private/B.csv"),results["reference"]["rank"])
    parts={}
    for name,law in laws.items():
        if not law["usable"]:
            continue
        frame=pd.concat([pd.read_csv(ROOT/"private/runs"/name/str(t["seed"])/"output/generated.csv") for t in law["runs"]],ignore_index=True)
        parts[name]=components(frame,law["metrics"]["rank"])
    pairs={}
    for p,s in results["pairs"].items():
        if not s["complete"]: continue
        c,e=parts[p+"_control"],parts[p+"_evidence"]
        get=lambda row: row["within_bands_low_mid_high"][1]
        pairs[p]={"control_mid_component_error":abs(get(c)-get(truth)),
                  "evidence_mid_component_error":abs(get(e)-get(truth)),
                  "between_component_change":e["between_hb_bands"]-c["between_hb_bands"],
                  "improved_mid_component":abs(get(e)-get(truth))<abs(get(c)-get(truth))}
    out={"scope":"post-reveal explanatory decomposition only; no change to primary endpoint or decision",
         "identity":"standardize global midranks, then decompose covariance into a between-band term and three probability-weighted within-band covariances",
         "heldout":truth,"fixed_laws":parts,"paired_descriptions":pairs}
    f=ROOT/"RANK_COMPONENTS.json"
    if not f.exists():
        with f.open("x",encoding="utf8",newline="\n") as handle: json.dump(out,handle,indent=2,allow_nan=False)
    else: assert json.loads(f.read_text(encoding="utf8"))==out
    print(json.dumps({"heldout":truth,"paired":pairs},indent=2))


if __name__=="__main__":
    run()
