"""Recompute both scientific estimates and survey intervals from the original public Stata file."""
import argparse
from pathlib import Path
import hashlib
import json
import pandas as pd
from scoring import reference_from


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file",type=Path,help="Original biomarker .dta from the IFPRI survey v1.1")
    args=parser.parse_args()
    baseline=json.loads(Path(__file__).with_name("REVEAL.json").read_text(encoding="utf8"))
    if hashlib.sha256(args.file.read_bytes()).hexdigest()!=baseline["input_sha256"]:
        raise SystemExit("The file differs from the archived original Stata file.")
    actual=reference_from(pd.read_stata(args.file,convert_categoricals=False))
    def equal(a,b):
        if isinstance(a,dict):return a.keys()==b.keys() and all(equal(a[k],b[k]) for k in a)
        if isinstance(a,list):return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
        if isinstance(a,float):
            import math
            return math.isclose(a,b,rel_tol=1e-11,abs_tol=1e-12)
        return a==b
    if not equal(actual,baseline["result"]): raise SystemExit("Recomputed aggregate differs")
    print(json.dumps({"reproduced":True,**actual},indent=2))
