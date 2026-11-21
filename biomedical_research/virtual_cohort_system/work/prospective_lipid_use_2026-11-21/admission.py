"""Bind the original US files; quality control here discloses only keys, flags and counts."""
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from design import PRIVATE, HERE, digest, obj, save

CSV = "https://hbiostat.org/data/repo/diabetes.csv"
SDD = "https://hbiostat.org/data/repo/diabetes.sdd"
VARS = ("id", "age", "chol", "hdl", "ratio", "location")


def fetch(url, dest):
    if not dest.exists():
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        assert 0 < len(r.content) < 1_000_000
        dest.write_bytes(r.content)


def data():
    df = pd.read_csv(PRIVATE/"virginia.csv", usecols=VARS)
    valid = (np.isfinite(df.age) & (df.age>=20) & np.isfinite(df.chol) & (df.chol>0) &
             np.isfinite(df.hdl) & (df.hdl>0) & df.id.notna() & ~df.id.duplicated(keep=False) &
             df.location.isin(["Buckingham","Louisa"]))
    return df, df.loc[valid].reset_index(drop=True)


def sdd_vector(lines, name):
    i = lines.index(name)
    if lines[i+1] != "structure" or lines[i+3] != ".Data" or lines[i+4] not in ("integer","single","double"):
        raise ValueError(f"Unexpected S data structure for {name}")
    n = int(lines[i+5])
    vals = [float(v) if v not in ("N","NA","NaN") else np.nan for v in lines[i+6:i+6+n]]
    return np.array(vals)


def main():
    PRIVATE.mkdir(exist_ok=True)
    csv_path, sdd_path = PRIVATE/"virginia.csv", PRIVATE/"virginia.sdd"
    fetch(CSV, csv_path)
    fetch(SDD, sdd_path)
    full, keep = data()
    lines = sdd_path.read_text(encoding="latin-1").splitlines()
    for field in ("id","age","chol","hdl","ratio"):
        assert np.allclose(sdd_vector(lines,field),full[field],equal_nan=True,rtol=1e-6,atol=1e-6)
    encoded = sdd_vector(lines, "location")
    start = lines.index("location")
    classes = lines.index(".Label", start)
    labels = lines[classes+3:classes+3+int(lines[classes+2])]
    assert list(np.asarray(labels)[encoded.astype(int)-1]) == full.location.tolist()
    errors = abs(keep.chol/keep.hdl - keep.ratio)
    point = {"source": "Schorling, UVA / Vanderbilt Biostatistics public data archive",
             "url": CSV, "native_S_dump": SDD, "csv_bytes":csv_path.stat().st_size,
             "sdd_bytes":sdd_path.stat().st_size, "csv_sha256":digest(csv_path),"sdd_sha256":digest(sdd_path),
             "independent_serializations_match_all_six_variables":True,
             "raw_records":len(full),"eligible":len(keep),
             "county_n":{k:int(v) for k,v in keep.location.value_counts().items()},
             "missing_id":int(full.id.isna().sum()),"duplicated_id_rows":int(full.id.duplicated(keep=False).sum()),
             "unit_evidence":"Publish package authors label chol on Schorling's data in mg/dL; original S labels declare TC, HDL and TC/HDL. The released TC/HDL field checks common scale.",
             "ratio_rounding_qc":{"paired":int(errors.notna().sum()),"outside_0.075":int((errors>.075).sum())},
             "excluded_by_age":int((full.age<20).sum()),"no_scientific_estimate_opened":True}
    assert point["eligible"]>=100 and point["ratio_rounding_qc"]["outside_0.075"] / len(keep)<.05
    path = HERE/"ADMISSION.json"
    if path.exists():
        assert obj(path)==point
    else:
        save(path,point)
    print(point["eligible"],point["county_n"],"eligible. Both public serializations matched.")


if __name__ == "__main__":
    main()
