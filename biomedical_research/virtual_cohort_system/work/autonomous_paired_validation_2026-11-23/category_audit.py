"""Post hoc check against the published paired categories, using virtual rows only."""
import hashlib
import json
from pathlib import Path
import re
import numpy as np
import pandas as pd

from evaluate import measurement, unit_name

HERE=Path(__file__).resolve().parent
CUTS=np.array([18.5,23.0,27.5])
LABELS=["Underweight","Normal","Overweight","Obese"]


def extract(text):
    sec=text.split("Table 3 Comparison of BMI categories",1)[1].split("Table 4 ",1)[0]
    rows=[json.loads(s) for s in sec.splitlines() if s.startswith("[")]
    start=next(i for i,r in enumerate(rows) if r[0]=="All participant")+1
    header=rows[0]
    if "self-reported" not in header[0] or "measured" not in header[1]:
        raise ValueError("Source row and column orientation changed")
    grid=[]
    for label,r in zip(LABELS,rows[start:start+4]):
        if not r[0].startswith(label) or len(r)!=6:
            raise ValueError("Unexpected source category")
        counts=[int(re.match(r"^(\d+)\s*\(",item).group(1)) for item in r[1:]]
        if sum(counts[:4]) != counts[4]:
            raise ValueError("Source category row totals mismatch")
        grid.append(counts[:4])
    a=np.array(grid)
    totals=[int(re.match(r"^(\d+)\s*\(",item).group(1)) for item in rows[start+4][1:]]
    if list(a.sum(axis=0))!=totals[:4] or a.sum()!=totals[4]:
        raise ValueError("Source category column totals mismatch")
    return a


def summary(reported,measured,source):
    pair_bins=[np.searchsorted(CUTS,v,side="right") for v in (reported,measured)]
    cells=np.bincount(4*pair_bins[0]+pair_bins[1],minlength=16).reshape(4,4)
    prop=cells/len(reported)
    delta=100*(prop-source/source.sum())
    worst=np.unravel_index(np.abs(delta).argmax(),(4,4))
    return {"cell_counts":cells.tolist(),"agreement_pct":100*float(np.trace(prop)),
            "cell_distribution_total_variation_pp":float(np.abs(delta).sum()/2),
            "largest_absolute_cell_error_pp":float(abs(delta[worst])),
            "largest_error_row_col":[LABELS[i] for i in worst]}


def audit():
    # Only the published aggregate projection and frozen virtual output files enter this comparison.
    source=extract((HERE/"private/search/article.txt").read_text(encoding="utf8"))
    maps=json.loads((HERE/"MEASUREMENT_MAPS.json").read_bytes())["authors"]
    out={"purpose":"Post hoc published-source diagnostic outside the prespecified pass criterion",
         "orientation":"Rows self-reported BMI, columns measured BMI, both ordered underweight, normal, overweight, obese",
         "source_counts":source.tolist(),"source_n":int(source.sum()),"source_diagonal_n":int(np.trace(source)),
         "source_agreement_pct":100*float(np.trace(source)/source.sum()),"authors":[]}
    for root in sorted((HERE/"private/authors").glob("a*")):
        result=json.loads((root/"slot_result.json").read_bytes())
        row={"slot":root.name,"status":result["status"],"primary_tables":[]}
        out["authors"].append(row)
        if result["status"]!="success":
            continue
        mapping=maps[root.name]
        if unit_name(mapping["unit"])!="kg/m2":
            raise ValueError("Paired BMI expected")
        manifest=json.loads((root/"final_manifest.json").read_bytes())
        for t in manifest["runs"]:
            if t["scenario"]!="primary" or t["status"]!="success":
                continue
            table=Path(t["table"]).resolve()
            if not table.is_relative_to((root/"execution_final").resolve()) or hashlib.sha256(table.read_bytes()).hexdigest()!=t["sha256"]:
                raise ValueError("Unexpected or changed virtual table")
            frame=pd.read_csv(table,float_precision="round_trip")
            if len(frame)!=t["n"]:
                raise ValueError("Unexpected table size")
            reported,_=measurement(frame,mapping["reported"],mapping)
            measured,_=measurement(frame,mapping["measured"],mapping)
            if not (np.isfinite(reported).all() and np.isfinite(measured).all()):
                raise ValueError("Incomplete or nonfinite generated BMI")
            item={"seed":t["seed"],"n":len(frame),"table_sha256":t["sha256"],
                  "unrounded":summary(reported,measured,source),
                  "rounded_to_tenth":summary(np.round(reported,1),np.round(measured,1),source),
                  "exact_cutpoint_counts_unrounded":{"reported":[int(np.sum(reported==u)) for u in CUTS],
                                                     "measured":[int(np.sum(measured==u)) for u in CUTS]}}
            row["primary_tables"].append(item)
    out["boundaries"]="Unrounded cutpoints are [18.5, 23, 27.5] with equality in the higher category. " \
        "The published headers use one-decimal bands and one obesity header says >27.5 whereas the methods use ≥27.5. " \
        "Rounding each generated BMI to one decimal (NumPy, ties to even) is a sensitivity analysis. " \
        "The source counts come directly from printed Table 3; the row-based workbook was never accessed by this diagnostic."
    return out


if __name__=="__main__":
    result=audit()
    path=HERE/"CATEGORY_AUDIT.json"
    if path.exists():
        if json.loads(path.read_bytes())!=result:
            raise ValueError("Previously published category check differs")
    else:
        with path.open("x",encoding="utf8") as f:
            json.dump(result,f,ensure_ascii=False,indent=2,allow_nan=False)
            f.write("\n")
