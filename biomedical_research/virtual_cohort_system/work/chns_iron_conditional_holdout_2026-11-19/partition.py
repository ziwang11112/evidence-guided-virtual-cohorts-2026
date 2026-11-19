"""Prepare A-only scientific evidence and a sealed B file. No B estimands in this entry point."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from science import HB, FE, bootstrap_values, check, interval, measures

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
INPUT = PROJECT / "work/chns_admission_2026-11-01"
PRIVATE = ROOT / "private"
SALT = "CHNS-Hb-ferritin-scientific-use-20261119-v1"
FILE = {"bio": "biomarker_09.sas7bdat", "master": "mast_pub_12.sas7bdat", "survey": "surveys_pub_12.sas7bdat"}


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(obj, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")


def read(p):
    return json.loads(p.read_text(encoding="utf-8-sig"))


def eligible():
    header = read(INPUT / "SCHEMA_AND_KEY_AUDIT.json")["files"]
    wanted = {"bio": ["IDind", "wave", "HGB", "FET"], "master": ["Idind", "GENDER"],
              "survey": ["Idind", "wave", "age", "hhid", "t1", "commid"]}
    tables, hashes = {}, {}
    for role, name in FILE.items():
        path = INPUT / "private_data" / name
        hashes[name] = digest(path)
        check(hashes[name] == header[name]["sha256"], "Unexpected input release")
        with pd.read_sas(path, format="sas7bdat", chunksize=20000) as reader:
            data = pd.concat([chunk[wanted[role]] for chunk in reader], ignore_index=True)
        data.columns = data.columns.str.lower()
        if "wave" in data:
            data = data.loc[data.wave.eq(2009)]
        check(data.idind.notna().all() and data.idind.is_unique, "Invalid person key after wave restriction")
        tables[role] = data.drop(columns="wave", errors="ignore")
    data = tables["bio"].merge(tables["master"], on="idind", validate="1:1").merge(tables["survey"], on="idind", validate="1:1")
    sel = data.gender.eq(2) & data.age.between(18, 49) & data[["t1", "commid", "hhid"]].notna().all(axis=1)
    pairs = data.loc[sel & np.isfinite(data.hgb) & np.isfinite(data.fet) & data.hgb.gt(0) & data.fet.gt(0)].copy()
    pairs[HB], pairs[FE] = pairs.hgb / 10, pairs.fet
    for key in ["idind", "t1", "commid", "hhid"]:
        check(np.all(pairs[key] == np.floor(pairs[key])), "Non-integral key")
        pairs[key] = pairs[key].astype("int64")
    check(pairs.groupby("commid").t1.nunique().max() == 1, "Community spans provinces")
    return pairs[["idind","hhid","commid","t1",HB,FE]].sort_values("idind"), hashes, int(sel.sum())


def split(frame):
    a_communities = []
    for i, (province, group) in enumerate(frame.groupby("t1", sort=True)):
        def order(community):
            return hashlib.sha256(f"{SALT}/{province}/{community}".encode("ascii")).digest()
        clusters = sorted(group.commid.unique(), key=order)
        a_communities.extend(clusters[i % 2::2])
    in_a = frame.commid.isin(a_communities)
    a, b = frame.loc[in_a], frame.loc[~in_a]
    for col in ["idind","commid","hhid"]:
        check(set(a[col]).isdisjoint(b[col]), "Split overlaps at " + col)
    for arm in [a,b]:
        check(len(arm) >= 700 and arm.commid.nunique() >= 50 and arm.groupby("t1").commid.nunique().min() >= 2, "Insufficient design coverage")
    return a, b


def rounded(x):
    return round(x, 3) if x is not None else None


def prepare():
    check(not (ROOT / "ADMISSION.json").exists(), "Admission already closed")
    data, hashes, n_eligible = eligible()
    a, b = split(data)
    PRIVATE.mkdir(parents=True, exist_ok=True)
    for label, sub in (("A",a),("B",b)):
        dest=PRIVATE / (label + ".csv")
        check(not dest.exists(), "Existing partition requires reconciliation")
        sub[["commid","t1",HB,FE]].to_csv(dest, index=False, lineterminator="\n")
    out = {s: {"n": len(d), "communities": int(d.commid.nunique()), "provinces": int(d.t1.nunique()), "sha256": digest(PRIVATE / (s+".csv"))}
           for s,d in (("A",a),("B",b))}
    save(ROOT / "PARTITION.json", {"split_method": SALT, "input_sha256": hashes, "eligible_before_pair_requirement": n_eligible,
                                   "parts": out, "people_households_communities_disjoint": True, "B_effects_computed": False})
    stats = measures(a, include_rank=False)
    check(min(stats["cells"]) >= 10 and min(stats["fine_band_n"]) >= 40, "Insufficient A cells for planned contrast")
    block = {"study": "CHNS 2009 within-study reconstruction. This supplement contains original aggregates of the evidence communities, newly tabulated for this exercise. It is separate from Zhu et al.",
             "population": "Linked complete-case women age 18–49 regardless of pregnancy or inflammation; unweighted. One measurement pair per person.",
             "units": "Central whole-blood hemoglobin g/dL; uncorrected serum ferritin micrograms/L.",
             "table_1": {"title": "Participant counts by measurement status", "rows": ["Hb <12", "Hb >=12"],
                         "columns": ["Ferritin <15", "Ferritin >=15"], "counts": [stats["cells"][:2], stats["cells"][2:]]},
             "table_2": {"title": "Distributions by hemoglobin band. SDs are sample SDs; geometric SD = exp(SD(log ferritin)).",
                         "rows": [{"Hb_band":name, **{k:rounded(v) for k,v in group.items() if k in ("n","depleted","hb_mean","hb_sd","ferritin_gm","ferritin_gsd")}}
                                  for name,group in zip(("<12","12 to <14",">=14"),stats["groups"])]}}
    ci=interval(bootstrap_values(a.reset_index(drop=True),191941,only_ratio=True))
    check(ci is not None and stats["ratio"] is not None, "Bridge ratio unavailable")
    bridge={"source":"Additional aggregate from the same CHNS evidence communities, central measurements, no covariate adjustment.",
            "statistic":"Ratio of geometric mean ferritin at Hb 13 to <14 g/dL to geometric mean ferritin at Hb 12 to <13 g/dL.",
            "estimate":rounded(stats["ratio"]), "province_stratified_community_bootstrap_95pct":[rounded(v) for v in ci]}
    save(ROOT/"A_TABLES.json",block)
    save(ROOT/"A_SUPPLEMENT.json",bridge)
    save(ROOT/"ADMISSION.json",{"status":"admitted","paired_rows":len(data),"partition":out,"source_min_cell_and_fine_band_checks_passed":True,
                                "B_outcome_information":"eligibility, positivity, paired completeness, group counts and file identity only",
                                "protocol_sha256":digest(ROOT/"PROTOCOL.md"),"partition_code_sha256":digest(Path(__file__))})
    print(json.dumps({"admission":"passed","A":out["A"],"B":out["B"]}))


if __name__ == "__main__":
    prepare()
