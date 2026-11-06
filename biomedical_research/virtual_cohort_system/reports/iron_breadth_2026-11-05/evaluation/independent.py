"""Independent arithmetic for the iron pilot. Run --audit only after authorized reveal."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import expit, logit
from scipy.stats import spearmanr, t as student

BASE = Path(__file__).resolve().parents[1]
METRICS = ("odds_ratio", "joint_prevalence", "spearman")
CELLS = ("both_low", "only_hb_low", "only_ferritin_low", "neither_low")


def rank_midmass(col, w):
    mass = w.groupby(col, sort=True).sum()
    cdf_mids = mass.cumsum() - mass / 2
    return col.map(cdf_mids).to_numpy() / mass.sum()


def weighted_metrics(rows):
    rows = rows.loc[rows.w > 0].copy()
    hb, fe, weight = rows.hb, rows.fe, rows.w
    a, b = hb.lt(12), fe.lt(15)
    masks = (a & b, a & ~b, ~a & b, ~a & ~b)
    mass = [float(weight.loc[g].sum()) for g in masks]
    counts = [int(g.sum()) for g in masks]
    odds = mass[0] * mass[3] / (mass[1] * mass[2]) if all(x > 0 for x in mass) else None
    total = float(weight.sum())
    joint = mass[0] / total if total else None
    rho = None
    if hb.nunique() > 1 and fe.nunique() > 1:
        u, v = rank_midmass(hb, weight), rank_midmass(fe, weight)
        cov = np.cov(u, v, aweights=weight, ddof=0)
        rho = float(cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1]))
    return dict(zip(METRICS, (odds, joint, rho))), counts, mass


def transforms(metric, v, forward):
    if v is None:
        return None
    if metric == "odds_ratio":
        return np.log(v) if forward else np.exp(v)
    if metric == "joint_prevalence":
        return (logit(v) if 0 < v < 1 else None) if forward else expit(v)
    return (np.arctanh(v) if abs(v) < 1 else None) if forward else np.tanh(v)


def extract_target(file_manifest):
    frames = {}
    for name, details in file_manifest.items():
        path = Path(details["path"])
        if hashlib.sha256(path.read_bytes()).hexdigest() != details["sha256"]:
            raise RuntimeError(f"Acquired file hash mismatch: {name}")
        data = pd.read_sas(path, format="xport").set_index("SEQN", verify_integrity=True)
        frames[name] = data
    demo, cbc, fer = (frames[k] for k in ["DEMO_L", "CBC_L", "FERTIN_L"])
    cbc = cbc[["WTPH2YR", "LBXHGB"]].rename(columns={"WTPH2YR":"w", "LBXHGB":"hb"})
    fer = fer[["WTPH2YR", "LBDFERSI"]].rename(columns={"WTPH2YR":"wf", "LBDFERSI":"fe"})
    frame = demo[["RIAGENDR","RIDAGEYR","RIDEXPRG","SDMVSTRA","SDMVPSU"]].join(cbc).join(fer)
    both = frame.w.notna() & frame.wf.notna()
    assert np.allclose(frame.w[both], frame.wf[both], rtol=1e-10, atol=1e-8)
    frame["w"] = frame.w.fillna(frame.wf)
    frame = frame.loc[frame.w > 0]
    # Preserve a separate full design even for PSUs with zero domain observations.
    design = frame.groupby("SDMVSTRA")["SDMVPSU"].unique().to_dict()
    assert not frame[["SDMVSTRA", "SDMVPSU"]].isna().any().any()
    frame = frame.loc[(frame.RIAGENDR == 2) & frame.RIDAGEYR.between(20,44) &
                      (frame.RIDEXPRG == 2)].dropna(subset=["hb","fe"])
    return design, frame


def jackknife(design, rows):
    points = weighted_metrics(rows)[0]
    df = sum(len(g)-1 for g in design.values())
    if df < 1 or any(len(g) < 2 for g in design.values()):
        return df, {k:None for k in METRICS}
    v = dict.fromkeys(METRICS, 0.0)
    for stratum, psus in design.items():
        count = len(psus)
        for deleted in psus:
            data = rows.copy()
            same = data.SDMVSTRA == stratum
            data.loc[same & (data.SDMVPSU != deleted), "w"] *= count / (count-1)
            data.loc[same & (data.SDMVPSU == deleted), "w"] = 0
            rep = weighted_metrics(data)[0]
            for k in METRICS:
                if v[k] is None:
                    continue
                x, y = (transforms(k, z[k], True) for z in (points, rep))
                v[k] = (None if x is None or y is None
                        else v[k] + ((count-1)/count) * (x-y)**2)
    result = {}
    for k in METRICS:
        if v[k] is None:
            result[k] = None
        else:
            center = transforms(k, points[k], True)
            half = float(student.ppf(.975, df) * np.sqrt(v[k]))
            result[k] = [float(transforms(k, center+sign*half, False)) for sign in (-1,1)]
    return df, result


def disputed(x, y, tol):
    if x is None or y is None:
        return (None, x is not y)
    delta = float(abs(x-y))
    return delta, not np.isclose(x,y,atol=tol,rtol=1e-13)


def selfcheck():
    # Independently expand integer weights and obtain tied Spearman with SciPy.
    fr = pd.DataFrame({"hb":[10.,11.,13.,13.,12.],"fe":[8.,18.,25.,11.,15.],
                       "w":[2,4,3,1,2]})
    values, counts, mass = weighted_metrics(fr)
    doubled = fr.loc[fr.index.repeat(fr.w)]
    assert counts == [1,1,1,2]
    assert mass == [2,4,1,5]
    assert np.isclose(values["odds_ratio"], 2.5)
    assert np.isclose(values["joint_prevalence"], 2/12)
    assert np.isclose(values["spearman"], spearmanr(doubled.hb,doubled.fe).statistic)
    print("Independent weighted-estimator fixture passed.")


def audit():
    seal = BASE/"BATCH_LOCK.json"
    manifest=json.loads((BASE/"private_reference/ACQUISITION.json").read_text())
    if manifest["batch_lock_sha256"] != hashlib.sha256(seal.read_bytes()).hexdigest():
        raise RuntimeError("Reference receipt does not match the final batch lock")
    lock=json.loads(seal.read_text())["records"]
    results_dir=BASE/"evaluation"
    real_record=json.loads((results_dir/"TARGET.json").read_text())
    synth_records=json.loads((results_dir/"SYNTHETIC.json").read_text())
    diffs={"estimates":[],"bounds":[],"masses":[]}
    errors=[]
    def compare(tag, metric, a, b, typ, tol=1e-9):
        delta, flag=disputed(a,b,tol)
        if delta is not None:
            diffs[typ].append(delta)
        if flag:
            errors.append({"record":tag,"field":metric,"independent":a,"primary":b})

    checks={}
    design, cohort=extract_target(manifest["files"])
    true_pts, true_count, true_mass = weighted_metrics(cohort)
    df, ci = jackknife(design, cohort)
    compare("target","sample size",len(cohort),real_record["flow"]["eligible_with_both"],"masses",0)
    compare("target","df",df,real_record["design"]["df"],"masses",0)
    for k in METRICS:
        compare("target",k,true_pts[k],real_record["estimands"][k]["estimate"],"estimates")
        primary=real_record["estimands"][k]["ci95"]
        if ci[k] is None or primary is None:
            if ci[k] != primary: errors.append({"record":"target","field":k+" CI missing mismatch"})
        else:
            for i in (0,1):
                compare("target",k+" CI",ci[k][i],primary[i],"bounds")
    for c,n,total in zip(CELLS,true_count,true_mass):
        compare("target",c+" count",n,real_record["cells"][c]["n"],"masses",0)
        compare("target",c+" mass",total,real_record["cells"][c]["weighted_count"],"masses",1e-6)
    checks["target"]={"n":len(cohort),"df":df,"estimates":true_pts,"ci95":ci}
    for author in ("A","B"):
        for seed in (5101,5102,5103):
            key=f"{author}_{seed}"
            rel=Path("private_runs")/author/"final"/f"target_{seed}"/"output/generated.csv"
            file=BASE/rel
            if hashlib.sha256(file.read_bytes()).hexdigest()!=lock[rel.as_posix()]:
                raise RuntimeError(f"Unsealed delivery {key}")
            df_s=pd.read_csv(file, float_precision="round_trip").rename(columns={"hb_g_dl":"hb","ferritin_ug_l":"fe"})
            df_s["w"]=1.
            pts,cnt,mass=weighted_metrics(df_s)
            pts["spearman"]=float(spearmanr(df_s.hb,df_s.fe).statistic)
            checks[key]={"n":len(df_s),"estimates":pts}
            for k in METRICS:
                compare(key,k,pts[k],synth_records[key]["estimands"][k]["estimate"],"estimates")
            for c,n in zip(CELLS,cnt):
                compare(key,c+" count",n,synth_records[key]["cells"][c]["n"],"masses",0)
    result={"material_discrepancies":errors, "max_absolute_difference":
            {k:max(vals,default=0) for k,vals in diffs.items()}, "independent":checks,
            "units":{"estimates":"OR, proportion, or Spearman as declared",
            "bounds":"native-scale 95% bounds","masses":"raw people or survey-weighted count"},
            "tolerance":"absolute 1e-9 for reported estimands and interval bounds, 1e-6 for weighted cell masses; counts exact; additional rtol=1e-13"}
    with (results_dir/"INDEPENDENT_AUDIT.json").open("x",encoding="utf8") as out:
        json.dump(result,out,indent=2,allow_nan=False)
    print(json.dumps({"mismatches":len(errors),"max_difference":result["max_absolute_difference"]}))
    return int(bool(errors))


if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--audit",action="store_true")
    if p.parse_args().audit:
        raise SystemExit(audit())
    selfcheck()
