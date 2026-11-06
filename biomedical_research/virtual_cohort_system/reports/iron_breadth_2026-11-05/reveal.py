"""Evaluate all predeclared deliveries and the real masked survey in one batch."""
import json
from pathlib import Path
import sys
import pandas as pd
from seal import BASE, digest, check_delivery
sys.path.insert(0,str(BASE/"evaluation"))
import analyze

if __name__=="__main__":
    reg=json.loads((BASE/"BATCH_LOCK.json").read_text())
    if reg["records"]!=check_delivery():raise ValueError("Batch changed")
    acq=json.loads((BASE/"private_reference"/"ACQUISITION.json").read_text())["files"]
    for v in acq.values():
        if digest(Path(v["path"]))!=v["sha256"]:raise ValueError("Input identity mismatch")
    synthetic={}
    for a in "AB":
        for seed in (5101,5102,5103):
            path=BASE/"private_runs"/a/"final"/f"target_{seed}"/"output"/"generated.csv"
            synthetic[f"{a}_{seed}"]=analyze.analyze_synthetic(pd.read_csv(path,float_precision="round_trip"))
    target=analyze.analyze_target(*(pd.read_sas(acq[k]["path"],format="xport") for k in ["DEMO_L","CBC_L","FERTIN_L"]))
    for filename,res in (("SYNTHETIC.json",synthetic),("TARGET.json",target)):
        with (BASE/"evaluation"/filename).open("x",encoding="utf-8") as f: json.dump(res,f,indent=2,allow_nan=False)
    print(json.dumps({"reference":target["estimands"],"flags":target["flags"],"flow":target["flow"],"generated":{k:[round(v["estimands"][s]["estimate"],4) if v["estimands"][s]["estimate"] is not None else None for s in analyze.NAMES] for k,v in synthetic.items()}},indent=2))
