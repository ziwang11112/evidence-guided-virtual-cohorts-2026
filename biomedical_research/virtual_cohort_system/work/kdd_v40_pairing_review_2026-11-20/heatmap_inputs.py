"""Aggregate the first frozen seed of every submitted scenario for the pairing figure."""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"nonhdl_external_2026-11-20"))
from science import values

def main():
    data=json.loads((HERE/"SENSITIVITY.json").read_text(encoding="utf8"))
    tc,hdl=values()
    bins=32
    n=len(tc)
    rank_bin=np.arange(n)*bins//n
    seed=40937
    out={"seed":seed,"n":n,"bins":bins,"panels":{}}
    for name,author in data["authors"].items():
        out["panels"][name]={}
        for mode,rows in author["runs"].items():
            rec,=[r for r in rows if r["seed"]==seed]
            if "score" not in rec:
                out["panels"][name][mode]={"reason":rec["reason"]}
                continue
            path=HERE/"private/draws"/name/mode/str(seed)/"perm.npy"
            assert hashlib.sha256(path.read_bytes()).hexdigest()==rec["permutation_hash"]
            ix=np.load(path,allow_pickle=False)
            grid=np.bincount(rank_bin*bins+rank_bin[ix],minlength=bins*bins).reshape((bins,bins))
            assert np.all(grid.sum(axis=0)==n//bins) and np.all(grid.sum(axis=1)==n//bins)
            assert int((tc-hdl[ix]>=160).sum())==rec["score"]["tail_count"]
            out["panels"][name][mode]={"tc_by_hdl":grid.tolist(),"tail_n":rec["score"]["tail_count"]}
    x=np.linspace(.0001,.9999,151)
    edge_tc=np.interp(x,(np.arange(n)+.5)/n,tc)
    y=np.interp(edge_tc-160.,hdl,(np.arange(n)+.5)/n,left=-.01,right=1.01)
    keep=(y>=0)&(y<=1)
    out["boundary_rank_coordinates"]=np.round(np.column_stack([x[keep],y[keep]]),5).tolist()
    with (HERE/"LIPID_HEATMAP.json").open("x",encoding="utf-8",newline="\n") as f:
        json.dump(out,f,separators=(",",":"),allow_nan=False);f.write("\n")

if __name__=="__main__":
    main()
