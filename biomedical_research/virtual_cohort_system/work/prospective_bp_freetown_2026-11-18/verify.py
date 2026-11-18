"""Independent row-level replay with openpyxl, csv and SciPy. Run after reveal."""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import openpyxl
from scipy.stats import pearsonr

ROOT = Path(__file__).resolve().parent


def point(a):
    x, y = np.asarray(a, float).T
    return {"Q1": float(pearsonr(x, y).statistic),
            "Q2": sum(s >= 140 and d >= 90 for s, d in zip(x,y))/len(x)}


def intervals(groups, repeats, seed):
    rng = np.random.default_rng(seed)
    by_zone = [np.asarray(groups[k], float) for k in sorted(groups)]
    dist = []
    for _ in range(repeats):
        sample = np.vstack([g[rng.choice(len(g),len(g),replace=True)] for g in by_zone])
        x,y = sample.T
        xc,yc = x - np.average(x), y - np.average(y)
        corr = (xc @ yc) / np.sqrt((xc@xc)*(yc@yc))
        both = np.count_nonzero(np.minimum(x-140,y-90) >= 0) / len(x)
        dist.append([corr,both])
    return dict(zip(["Q1","Q2"],np.percentile(dist,[2.5,97.5],axis=0).T))


def fixtures():
    import pandas as pd
    import analysis
    a = [(140,90),(139,91),(141,89),(150,96),(122,71),(135,80),(130,83),(123,78)]
    got = analysis.summary(a)["estimates"]
    exp = point(a)
    assert got["Q2"] == exp["Q2"] == .25 and abs(got["Q1"]-exp["Q1"])<1e-12
    df = pd.DataFrame(a,columns=["SBP","DBP"])
    df["zone"] = ["a","a","b","b","a","a","b","b"]
    x = analysis.zone_intervals(df,50,8723)
    y = intervals({k:g[["SBP","DBP"]].to_numpy() for k,g in df.groupby("zone")},50,8723)
    for k in x:
        np.testing.assert_allclose(x[k],y[k],rtol=0,atol=1e-12)


def verify():
    assert (ROOT/"REVEAL.json").is_file()
    result = json.loads((ROOT/"AGGREGATES.json").read_text(encoding="utf8"))
    files = json.loads((ROOT/"ADMISSION.json").read_text(encoding="utf8"))["files"]
    p = ROOT/"private_reference"/files[0]["name"]
    assert hashlib.sha256(p.read_bytes()).hexdigest() == files[0]["sha256"]
    book = openpyxl.load_workbook(p, read_only=True, data_only=True)
    iterator = book["Mastersheet"].values
    h = list(next(iterator))
    keys = [h.index(k) for k in ["V1_SN","V8_A_Cats","V2_Z","V6_PS","V6_PD"]]
    seen, groups = set(), {}
    for row in iterator:
        serial, age, zone, s, d = (row[i] for i in keys)
        assert serial is not None and serial not in seen
        seen.add(serial)
        if age not in (2,3,4) or zone is None:
            continue
        try:
            pair = (float(s), float(d))
        except (TypeError, ValueError):
            continue
        if np.isfinite(pair).all() and min(pair)>0:
            groups.setdefault(zone,[]).append(pair)
    book.close()
    full = sum(groups.values(),[])
    ref = result["target"]
    assert len(full)==ref["n"] and len(groups)==ref["zones"]
    assert sum(a>=140 and b>=90 for a,b in full)==ref["both_n"]
    max_error=0.
    def reconcile(a,b):
        nonlocal max_error
        delta = float(np.max(np.abs(np.asarray(a)-np.asarray(b))))
        assert delta<1e-11, (a,b)
        max_error = max(max_error,delta)
    for k,v in point(full).items():
        reconcile(v,ref["estimates"][k])
    for k,v in intervals(groups,2000,18127).items():
        reconcile(v,ref["within_zone_intervals"][k])
    closure = json.loads((ROOT/"CLOSURE.json").read_text(encoding="utf8"))
    for arm, outcome in result["arms"].items():
        rows = []
        for draw in outcome["draws"]:
            saved = next(b for b in closure["tables"] if b["arm"]==arm and b["seed"]==draw["seed"])
            path = ROOT/"private_runs"/saved["run_relative"]/"output/generated.csv"
            assert hashlib.sha256(path.read_bytes()).hexdigest()==saved["csv_sha256"]
            with path.open(encoding="utf8",newline="") as f:
                table = [(float(r["SBP"]),float(r["DBP"])) for r in csv.DictReader(f)]
            vals=point(table)
            for k,v in vals.items():
                reconcile(v,draw["result"]["estimates"][k])
            rows.extend(table)
        for k,v in point(rows).items():
            reconcile(v,outcome["pooled"]["estimates"][k])
            reconcile(v-ref["estimates"][k],outcome["signed_target_delta"][k])
        ma=np.array(rows)
        for k,v in zip(["mean_s","mean_d","sd_s","sd_d"],[*np.mean(ma,axis=0),*np.std(ma,axis=0,ddof=1)]):
            reconcile(v,outcome["pooled"]["estimates"][k])
    with (ROOT/"VERIFICATION.json").open("x",encoding="utf8") as f:
        json.dump({"source":"independent estimator implementation, same research session","target_rows":len(full),
                   "completed_tables":len(closure["tables"]),"pressure_endpoints_per_table":2,
                   "bootstrap":2000,"maximum_numeric_difference":max_error,"passed":True},f,indent=2)


if __name__=="__main__":
    verify()
