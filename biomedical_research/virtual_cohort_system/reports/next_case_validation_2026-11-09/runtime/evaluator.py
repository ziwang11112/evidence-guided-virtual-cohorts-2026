"""Custodian-only PNS BP preparation/evaluation. Never import in author adapters.

Readiness emits counts/rank only after selection lock. Clinical results require
verified all-author batch closure and the separately frozen implementation.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
from datetime import datetime, timezone
import zipfile
import numpy as np
import pandas as pd
from analysis_tools import summarize, row_resampling_stability, ANALYSES

HERE = Path(__file__).resolve().parent
U = HERE.parent
PROJECT = U.parents[1]
ARCHIVE = PROJECT / "work/analysis-utility-preparation-2026-10-29/pns_hba1c/custodian/raw/PNS2013_Exames.zip"
MEMBER = "EXAMES-PNS-2013-FINAL_05052023.xlsx"
SHEET = "EXAMES-PNS-2013-FINAL_com-ponde"
ARCHIVE_HASH = "d31544efdad138f3292ab86c9606cd722bf091781cc86ef371354ba63c9994bb"
MEMBER_HASH = "80222fa535524829d531504109ac4b49d44e4e6d0c04c3c281ff972bd332d1f7"
FIELDS = ["C008", "Z001", "z004", "z005", "P005", "W00407", "W00408", "peso_lab"]

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding="utf-8-sig"))
def write_new(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x",encoding="utf-8") as f:
        json.dump(value,f,indent=2,allow_nan=False);f.write("\n")

def check_lock(path):
    lock = read(path)
    for name,digest in lock["files"].items():
        full = Path(name) if Path(name).is_absolute() else PROJECT/name
        if sha(full) != digest: raise ValueError("Frozen file changed: "+name)
    return lock

def select_rows(raw):
    """Prospective dictionary rules, no target-dependent trimming."""
    if set(FIELDS) - set(raw.columns): raise ValueError("Required source fields missing")
    x = raw[FIELDS].apply(pd.to_numeric,errors="coerce")
    mask = pd.Series(True,index=x.index)
    stages = []
    rules = [
        ("age20to79", x.C008.between(20,79)),
        ("sex1or2", x.Z001.isin([1,2])),
        ("weight30to200kg", x.z004.between(30,200)),
        ("height120to210cm", x.z005.between(120,210)),
        ("not_reported_pregnant", x.P005.ne(1)),
        ("sbp60to290", x.W00407.between(60,290)),
        ("dbp30to200", x.W00408.between(30,200)),
        ("positive_finite_labweight", x.peso_lab.gt(0) & np.isfinite(x.peso_lab))]
    for label, condition in rules:
        before = int(mask.sum()); mask &= condition
        stages.append({"rule":label,"remaining":int(mask.sum()),"excluded_at_step":before-int(mask.sum())})
    keep = x.loc[mask]
    frame = pd.DataFrame({"age":keep.C008,"female":(keep.Z001==2).astype(int),
                          "bmi":keep.z004/(keep.z005/100)**2,
                          "sbp":keep.W00407,"dbp":keep.W00408})
    design = np.column_stack([np.ones(len(frame)),(frame.age-50)/10,frame.female,(frame.bmi-25)/5])
    rank = int(np.linalg.matrix_rank(design * np.sqrt(keep.peso_lab.to_numpy())[:,None])) if len(frame) else 0
    audit = {"raw_rows":len(raw),"common_eligible_rows":len(frame),"sequential_exclusions":stages,
             "both_sexes_present":bool(frame.female.nunique()==2),"design_rank":rank,
             "unknown_or_inapplicable_pregnancy_retained":int((~keep.P005.isin([1,2])).sum()),
             "duplicate_required_field_rows":int(keep.duplicated().sum()),
             "duplicate_handling":"No stable public person identifier; exact required-field matches are retained, not declared duplicate people",
             "no_effects_means_or_correlations_disclosed":True}
    return frame.reset_index(drop=True),keep.peso_lab.to_numpy(),audit

def load_reference():
    if sha(ARCHIVE) != ARCHIVE_HASH: raise ValueError("Source archive identity mismatch")
    with zipfile.ZipFile(ARCHIVE) as z:
        matches=[n for n in z.namelist() if Path(n).name==MEMBER]
        if len(matches)!=1: raise ValueError("Ambiguous workbook member")
        payload=z.read(matches[0])
    if hashlib.sha256(payload).hexdigest()!=MEMBER_HASH: raise ValueError("Workbook identity mismatch")
    # Read only eight predeclared columns, not HbA1c or other outcome columns.
    raw=pd.read_excel(io.BytesIO(payload),sheet_name=SHEET,usecols=FIELDS,engine="openpyxl")
    return select_rows(raw)

def readiness():
    check_lock(U/"SELECTION_LOCK.json")
    frame,w,audit=load_reference()
    audit.update({"created_utc":datetime.now(timezone.utc).isoformat(),"archive_sha256":ARCHIVE_HASH,
                  "member_sha256":MEMBER_HASH,"reference_results_computed":False,
                  "status":"ready" if len(frame)>20 and audit["design_rank"]==4 and audit["both_sexes_present"] else "not_ready"})
    # No raw or transformed patient table is persisted by preparation.
    write_new(U/"READINESS.json",audit)
    print(json.dumps(audit,indent=2))

def evaluate():
    # Batch verifier is supplied by reviewed CLI; no target load may precede it.
    from controller import verify_batch_seal
    verified=verify_batch_seal()
    if not verified: raise ValueError("All-author batch seal required")
    if (U/"RESULTS.json").exists(): raise ValueError("Result already exists; do not overwrite or repeat reveal")
    if read(U/"READINESS.json")["status"] != "ready": raise ValueError("Readiness failed")
    # Hash-check every selected table before reference access. Failures remain in
    # author_outcomes; a failed output is never replaced with another seed.
    generated=[]
    for row in verified["selected_outputs"]:
        if sha(row["path"]) != row["sha256"]: raise ValueError("Generated output changed")
        generated.append({**row,"analysis":summarize(pd.read_csv(row["path"]))})
    frame,w,audit=load_reference()
    reference=summarize(frame,w)
    sensitivity=summarize(frame)
    stability=row_resampling_stability(frame,w,repeats=500,seed=73991)
    comparisons=[]
    for row in generated:
        s=row["analysis"]; entry={k:row[k] for k in ["author_id","candidate","run_id","seed"]}
        entry["status"]=s["status"];entry["estimates"]={}
        for key in ANALYSES:
            g=s["estimates"][key];r=reference["estimates"][key]
            entry["estimates"][key]={"generated":g,"reference":r,
                "signed_difference":g-r if g is not None and r is not None else None,
                "absolute_difference":abs(g-r) if g is not None and r is not None else None,
                "same_sign":bool(np.sign(g)==np.sign(r)) if g is not None and r is not None else None}
        entry["dispersion_ratios"]={}
        for key in ["sbp","dbp"]:
            for role in ["marginal","residual"]:
                g=(s["diagnostics"]["margins"][key]["sd"] if role=="marginal" else s["diagnostics"]["residual_sd"][key])
                r=(reference["diagnostics"]["margins"][key]["sd"] if role=="marginal" else reference["diagnostics"]["residual_sd"][key])
                entry["dispersion_ratios"][role+"_"+key]=g/r if g is not None and r is not None and r>0 else None
        comparisons.append(entry)
    value={"created_utc":datetime.now(timezone.utc).isoformat(),"case":"PNS BP qualified new task in an exposed family",
           "batch_seal_sha256":verified["batch_seal_sha256"],"reference_archive_sha256":ARCHIVE_HASH,
           "reference_member_sha256":MEMBER_HASH,"eligibility":audit,"author_outcomes":verified["author_outcomes"],
           "all_attempted_output_count":verified["all_attempted_output_count"],"selected_output_count":len(generated),
           "reference_weighted":reference,"reference_unweighted_sensitivity":sensitivity,
           "reference_row_resampling_stability":stability,"generated":generated,"comparisons":comparisons,
           "interpretation":"Descriptive paired analysis comparison; no superiority/equivalence test or arbitrary pass threshold. Seeds and authors are not independent clinical studies."}
    write_new(U/"RESULTS.json",value)
    print(json.dumps({"status":"evaluated","rows":len(frame),"selected_outputs":len(generated),
                      "reference":reference["estimates"],"results":str(U/"RESULTS.json")},indent=2))

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("command",choices=["readiness","evaluate"])
    args=parser.parse_args()
    readiness() if args.command=="readiness" else evaluate()
