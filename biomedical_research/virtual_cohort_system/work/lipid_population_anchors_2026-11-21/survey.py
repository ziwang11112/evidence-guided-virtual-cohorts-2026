"""Prespecified directly standardized estimands and delete-one-PSU intervals."""
import itertools
import shutil

import numpy as np
import pandas as pd
import requests
from pandas.io.sas.sas_xport import XportReader
from scipy.stats import t as student

from common import AGE_MASS, HERE, NAMES, PERIODS, PRIVATE, PROJECT, digest


def source_file(stub, suffix):
    name = f"{stub}_{suffix}.xpt"
    url = f"https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/{PERIODS[suffix]}/DataFiles/{name}"
    directory = PRIVATE / "reference"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    known_demo = {"J": "m13b/custodian/acquisition/private/raw/DEMO_J.xpt",
                  "L": "m15b_literature_direct_2026-10-30/private/custodian/raw/DEMO_L.xpt"}
    provenance = directory / (name + ".origin")
    if not path.exists():
        reused = PROJECT / "work" / known_demo[suffix]
        if stub == "DEMO" and reused.is_file():
            shutil.copyfile(reused, path)
            how = "existing CDC project copy"
        else:
            with requests.get(url, stream=True, timeout=(8, 50)) as response:
                response.raise_for_status()
                content = bytearray()
                for block in response.iter_content(131072):
                    content.extend(block)
                    if len(content) > 12_000_000:
                        raise ValueError("File size limit")
                if not content.startswith(b"HEADER RECORD*******LIBRARY"):
                    raise ValueError("CDC link did not return an XPORT file")
                path.write_bytes(content)
            how = "download from CDC"
        provenance.write_text(how, encoding="utf-8")
    with XportReader(path) as reader:
        labels = {f["name"].decode().strip(): f["label"].decode().strip() for f in reader.fields}
        frame = reader.read()
    assert frame.SEQN.is_unique and frame.SEQN.notna().all()
    return frame, {"url": url, "sha256": digest(path), "bytes": path.stat().st_size,
                   "acquired": provenance.read_text(encoding="utf-8"), "labels": labels}


def survey_data(suffix):
    demo, md = source_file("DEMO", suffix)
    tc, mt = source_file("TCHOL", suffix)
    hdl, mh = source_file("HDL", suffix)
    assert "mg/dL" in mt["labels"]["LBXTC"] and "mg/dL" in mh["labels"]["LBDHDD"]
    assert tc.SEQN.isin(demo.SEQN).all() and hdl.SEQN.isin(demo.SEQN).all()
    components = tc.merge(hdl, on="SEQN", how="outer", validate="one_to_one", suffixes=("_tc", "_hdl"))
    if suffix == "L":
        assert set(tc.SEQN) == set(hdl.SEQN)
        assert np.allclose(components.WTPH2YR_tc, components.WTPH2YR_hdl, equal_nan=True)
        components["WTPH2YR"] = components.WTPH2YR_tc
    weight = "WTMEC2YR" if suffix == "J" else "WTPH2YR"
    full = demo.merge(components, on="SEQN", how="left", validate="one_to_one")
    examined = full.loc[full.WTMEC2YR > 0]
    design = examined[["SDMVSTRA", "SDMVPSU"]].drop_duplicates().sort_values(["SDMVSTRA","SDMVPSU"])
    assert design.notna().all().all()
    adults = examined.loc[examined.RIDAGEYR >= 20]
    eligible = adults.loc[(adults[weight] > 0) & (adults.LBXTC > 0) & (adults.LBDHDD > 0)]
    n_by_age = pd.cut(eligible.RIDAGEYR, [19,39,59,200]).value_counts(sort=False).tolist()
    assert all(n > 0 for n in n_by_age)
    qc = {"files": {"demographics":md,"total":mt,"hdl":mh}, "design_weight":weight,
          "registered":len(demo),"examined":len(examined),"examined_adults":len(adults),
          "adults_with_missing_or_nonpositive_tc":int((~(adults.LBXTC > 0)).sum()),
          "adults_with_missing_or_nonpositive_hdl":int((~(adults.LBDHDD > 0)).sum()),
          "adults_without_positive_design_weight":int((~(adults[weight] > 0)).sum()),
          "missing_lab_file_ids_among_adults":{"tc":int((~adults.SEQN.isin(tc.SEQN)).sum()),
                                               "hdl":int((~adults.SEQN.isin(hdl.SEQN)).sum())},
          "both_measures_weighted":len(eligible),"n_by_age":n_by_age,
          "hdl_above_tc":int((eligible.LBDHDD > eligible.LBXTC).sum()),"duplicate_ids":0}
    return eligible, design, weight, qc


def mid_distribution(x, w):
    _, codes = np.unique(x, return_inverse=True)
    mass = np.bincount(codes, weights=w)
    return (np.cumsum(mass) - mass / 2)[codes]


def standardized(tc, hdl, groups, raw):
    totals = np.bincount(groups, weights=raw, minlength=3)
    if np.any(totals <= 0):
        raise ValueError("Empty age stratum")
    w = raw * AGE_MASS[groups] / totals[groups]
    assert np.isclose(w.sum(), 1)
    tx = mid_distribution(tc, w) - .5
    hx = mid_distribution(hdl, w) - .5
    corr = np.sum(w*tx*hx) / np.sqrt(np.sum(w*tx*tx)*np.sum(w*hx*hx))
    return np.array([w @ (tc-hdl), w @ (tc/hdl), 100*(w @ (tc >= 6.2*38.67)),
                     100*(w @ (hdl < 38.67)), 100*(w @ (tc-hdl >= 160)), corr])


def measured(suffix):
    f, design, weight, qc = survey_data(suffix)
    tc = f.LBXTC.to_numpy()
    hdl = f.LBDHDD.to_numpy()
    age = np.digitize(f.RIDAGEYR, [40,60])
    w = f[weight].to_numpy()
    point = standardized(tc, hdl, age, w)
    var = np.zeros(len(NAMES))
    df = 0
    for st, clusters in design.groupby("SDMVSTRA"):
        ids = clusters.SDMVPSU.to_numpy()
        m = len(ids)
        if m < 2:
            raise ValueError("Stratum has fewer than two PSUs")
        in_st = f.SDMVSTRA.to_numpy() == st
        for unit in ids:
            weights = w.copy()
            weights[in_st] *= m/(m-1)
            weights[in_st & (f.SDMVPSU.to_numpy()==unit)] = 0
            rep = standardized(tc, hdl, age, weights)
            var += (m-1)/m * (rep-point)**2
        df += m-1
    se = np.sqrt(var)
    width = student.ppf(.975, df)*se
    qc.update({"strata":int(design.SDMVSTRA.nunique()),"psus":len(design),"df":df})
    return {"qc":qc, "estimates":{k:{"estimate":float(x),"se":float(s),"ci":[float(x-b),float(x+b)]}
                                  for k,x,s,b in zip(NAMES,point,se,width,strict=True)}}


def gain(baseline, predictions, theta):
    return float(abs(baseline-theta) - np.median(np.abs(np.asarray(predictions)-theta)))


def gain_range(baseline, predictions, limits):
    lo, hi = limits
    knots = [lo,hi,baseline,*predictions, *((a+b)/2 for a,b in itertools.combinations(predictions,2))]
    values = [gain(baseline,predictions,x) for x in knots if lo <= x <= hi]
    return [min(values),max(values)]
