"""Custodian. Only disclose schema/counts during admission. Private export requires verification of both seals."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pyreadstat

HERE=Path(__file__).resolve().parent
PRIVATE=HERE/"private"
COHORTS={
    "mekelle":("sav",pyreadstat.read_sav,"Participant_code","Age","Total_Cholesterol","HDL_C"),
    "workers":("dta",pyreadstat.read_dta,"id","age","cholestrole","HDL_c"),
}
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def eligible(name):
    suffix,reader,ident,age,tc,hdl=COHORTS[name]
    path=PRIVATE/f"{name}.{suffix}"
    aux=["Sex","TC_2","HDL_2"] if name=="mekelle" else []
    data,meta=reader(str(path),usecols=[ident,age,tc,hdl]+aux,output_format="dict")
    ids=np.asarray(data[ident]); a=np.asarray(data[age],float)
    t=np.asarray(data[tc],float); h=np.asarray(data[hdl],float)
    mask=np.isfinite(a)&(a>=20)&np.isfinite(t)&np.isfinite(h)&(t>0)&(h>0)
    keys=np.array(["" if x is None or str(x).lower()=="nan" else str(x).strip() for x in ids])
    uniq,counts=np.unique(keys,return_counts=True)
    repeated=counts>1
    keep=mask&(keys!="")&~np.isin(keys,uniq[repeated])
    audit={"release_sha256":sha(path),"bytes":path.stat().st_size,"columns":[ident,age,tc,hdl],
           "records":len(a),"eligible_before_id":int(mask.sum()),"duplicate_ids_in_release":int(repeated.sum()),
           "records_removed_by_id_rule":int((mask&~keep).sum()),"eligible":int(keep.sum()),
           "units":"mg/dL","rows_per_observation":"one record per unique participant ID"}
    if name=="mekelle":
        methods={"tc":(t,np.array(data["TC_2"],float),200.0),
                 "hdl":(h,np.array(data["HDL_2"],float),np.where(np.asarray(data["Sex"])==1,40.,50.))}
        for key,(value,flag,cut) in methods.items():
            ok=keep&np.isin(flag,[0,1])
            expected=value>=cut if key=="tc" else value<cut
            mismatch=int((flag[ok]!=expected[ok]).sum())
            audit[f"{key}_unit_flag_check"]={"compared":int(ok.sum()),"discordant":mismatch}
            if not ok.any() or mismatch/ok.sum()>.05:
                raise ValueError(f"Verify unit/category independently for {key}: {mismatch} / {ok.sum()}")
    if keep.sum()<100:
        raise ValueError("Fewer than 100 eligible distinct records")
    return audit,np.column_stack((a[keep],t[keep],h[keep]))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("stage",choices=["admit","export"])
    args=parser.parse_args()
    if args.stage=="export":
        prior=json.loads((HERE/"REFERENCE_OPEN.json").read_text())
        assert prior["closure_sha256"]==sha(HERE/"CLOSURE.json")
        assert prior["freeze_sha256"]==sha(HERE/"FREEZE.json")
    records={}
    for name in COHORTS:
        audit,x=eligible(name)
        records[name]=audit
        if args.stage=="export":
            np.save(PRIVATE/(name+"-eligible.npy"),x,allow_pickle=False)
    if args.stage=="admit":
        records["target_endpoints_computed"]=False
        report=HERE/"ADMISSION_COUNTS.json"
        if report.exists(): assert json.loads(report.read_text())==records
        else: report.write_text(json.dumps(records,indent=2)+"\n")
        print(json.dumps(records))
