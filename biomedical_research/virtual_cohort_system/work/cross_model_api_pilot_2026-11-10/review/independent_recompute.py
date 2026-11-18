"""Independent, create-only post-evaluation numerical and denominator audit.

Preparation does not execute this script. Run only when root explicitly confirms
evaluation is complete. No authored generator, trusted analyzer, custodian data,
provider client, credential, or network capability is read/imported/executed.
Only the already generated CSVs, aggregate evaluation, and their receipts/seals
are read. Numerical audit tolerances are arithmetic agreement checks, not new
scientific acceptance thresholds.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
from statistics import mean
import sys

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SEEDS = (31001, 31003, 31007)
N_ROWS = 3000
ATOL = 1e-9
RTOL = 1e-10
PLANS = {
    "PNS": {
        "columns": ["row_id", "age", "female", "bmi", "sbp", "dbp"],
        "analyses": [("bmi_sbp", "mmHg per 5 kg/m^2"), ("bmi_dbp", "mmHg per 5 kg/m^2"),
                     ("residual_correlation", "1")],
        "diagnostics": [("sbp.sd_population", "mmHg"), ("dbp.sd_population", "mmHg"), ("sbp_below_dbp_fraction", "1")],
    },
    "lipids": {
        "columns": ["id", "age", "sex", "bmi", "total_cholesterol", "hdl_cholesterol"],
        "analyses": [("K02-HDL-BMI", "mg/dL per 5 kg/m^2"), ("K02-TC-BMI", "mg/dL per 5 kg/m^2"),
                     ("K02-LIPID-RESIDUAL", "1")],
        "diagnostics": [("total_cholesterol.sd_sample", "mg/dL"), ("hdl_cholesterol.sd_sample", "mg/dL"),
                        ("hdl_above_total_fraction", "1")],
    },
}


def require(condition, message):
    if not condition: raise ValueError(message)


def read(path):
    def unique(pairs):
        out = {}
        for key,value in pairs:
            require(key not in out, "Duplicate JSON key")
            out[key] = value
        return out
    def nonfinite(value): raise ValueError("Nonfinite JSON value: " + value)
    return json.loads(Path(path).read_text(encoding="utf-8-sig"), object_pairs_hook=unique, parse_constant=nonfinite)


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def safe(name):
    value = Path(name)
    require(not value.is_absolute() and ".." not in value.parts, "Only local relative audit inputs allowed")
    path = ROOT / value
    require(path.resolve().is_relative_to(ROOT.resolve()), "Audit input escapes pilot root")
    require(not any(p.is_symlink() or bool(getattr(p, "is_junction", lambda:False)()) for p in [path,*path.parents]),
            "Linked audit input rejected")
    require(path.is_file(), "Missing audit input: " + str(name))
    return path


def close(a,b):
    return a is None and b is None or (
        isinstance(a,(int,float)) and not isinstance(a,bool) and isinstance(b,(int,float)) and not isinstance(b,bool)
        and math.isfinite(a) and math.isfinite(b) and math.isclose(a,b,rel_tol=RTOL,abs_tol=ATOL))


def compute_csv(path, case):
    """Direct least squares and centered residual arithmetic; never analyzer calls."""
    plan = PLANS[case]
    frame = pd.read_csv(path, dtype={"id":"string","sex":"string"} if case == "lipids" else None,
                        float_precision="round_trip",keep_default_na=False,na_values=[""])
    require(list(frame.columns) == plan["columns"] and len(frame) == N_ROWS, "Generated schema/size differs")
    identifier = plan["columns"][0]
    require(frame[identifier].notna().all() and frame[identifier].is_unique, "Missing/duplicate identifier")
    numeric = [name for name in plan["columns"] if name not in {identifier,"sex"}]
    for name in numeric:
        dtype = frame[name].dtype
        require(pd.api.types.is_numeric_dtype(dtype) and not pd.api.types.is_bool_dtype(dtype)
                and not pd.api.types.is_complex_dtype(dtype), "Noncanonical numeric data: " + name)
    require(np.isfinite(frame[numeric].to_numpy(dtype=float)).all(), "Incomplete/nonfinite generated values")
    age = frame.age.to_numpy(dtype=float)
    bmi = frame.bmi.to_numpy(dtype=float)
    if case == "PNS":
        sex = frame.female.to_numpy(dtype=float)
        require(np.isin(sex,[0,1]).all() and ((20 <= age) & (age <= 79)).all(), "PNS eligibility mismatch")
        # Column order is SBP, DBP, matching the declared pair.
        y = frame[["sbp","dbp"]].to_numpy(dtype=float)
        ddof = 0
        component_count = int((y[:,0] < y[:,1]).sum())
    else:
        require(frame.sex.isin(["F","M"]).all() and (age >= 18).all() and (bmi > 0).all(), "Lipid eligibility mismatch")
        sex = frame.sex.eq("F").to_numpy(dtype=float)
        y = frame[["total_cholesterol","hdl_cholesterol"]].to_numpy(dtype=float)
        require((y > 0).all(), "Nonpositive lipids: no row filtering permitted")
        component_count = int((y[:,1] > y[:,0]).sum())
        y = y * 38.67
        ddof = 1
    x = np.column_stack([np.ones(len(frame)),(age-50)/10,sex,(bmi-25)/5])
    beta,_,rank,_ = np.linalg.lstsq(x,y,rcond=None)
    rank = int(rank)
    estimates = {name:None for name,_ in plan["analyses"]}
    if rank == 4:
        residual = y - x @ beta
        centered = residual - residual.mean(axis=0)
        if case == "PNS":
            estimates["bmi_sbp"] = float(beta[3,0])
            estimates["bmi_dbp"] = float(beta[3,1])
            variance = ((y-y.mean(axis=0))**2).mean(axis=0)
            residual_variance = (centered**2).mean(axis=0)
            threshold = np.finfo(float).eps * max(float(variance.max()),1.) * 100
            usable = bool((residual_variance > threshold).all())
            correlation_key = "residual_correlation"
        else:
            for index,key in [(0,"K02-TC-BMI"),(1,"K02-HDL-BMI")]:
                if np.ptp(y[:,index]) > 0: estimates[key] = float(beta[3,index])
            # Existing K02 numerical definition: residual variation must exceed
            # response-scale floating-point resolution; constant responses are unavailable.
            resolution = 16*np.finfo(float).eps*max(x.shape)*np.maximum(np.linalg.norm(y,axis=0),np.finfo(float).tiny)
            usable = bool((np.linalg.norm(residual,axis=0)>resolution).all() and (np.ptp(y,axis=0)>0).all())
            correlation_key = "K02-LIPID-RESIDUAL"
        if usable:
            # Independent direct centered vector correlation, no provider helper.
            estimate = float(centered[:,0]@centered[:,1] / (np.linalg.norm(centered[:,0])*np.linalg.norm(centered[:,1])))
            estimates[correlation_key] = float(np.clip(estimate,-1,1))
    sds = np.std(y,axis=0,ddof=ddof)
    diagnostics = {plan["diagnostics"][0][0]:float(sds[0]),plan["diagnostics"][1][0]:float(sds[1]),
                   plan["diagnostics"][2][0]:component_count/len(frame)}
    return {"analyses":estimates,"diagnostics":diagnostics,"quality":{"design_rank":rank,"n":len(frame),
            "component_violation_count":component_count,
            "duplicate_measurement_rows":int(frame.drop(columns=identifier).duplicated().sum())}}


def _endpoint_maps(slot,case):
    out = {}
    for category in ["analyses","diagnostics"]:
        expected = dict(PLANS[case][category])
        entries = slot[category]
        require(len(entries) == len(expected) and {e["id"] for e in entries} == set(expected), "Endpoint coverage differs")
        out[category] = {e["id"]:e for e in entries}
        require(all(e["unit"]==expected[e["id"]] for e in entries), "Endpoint unit differs")
    return out


def audit():
    # These are the only evidence files admitted before data access.
    required = ["EVALUATION.json","EVALUATION_COMPLETED.json","CONSTRUCTION_CLOSURE.json", "EXECUTION_CLOSURE.json", "RUN_PLAN.json"]
    paths = {name:safe(name) for name in required}
    source_hashes = {name:sha(path) for name,path in paths.items()}
    done,report = read(paths["EVALUATION_COMPLETED.json"]),read(paths["EVALUATION.json"])
    require(done["files"]["EVALUATION.json"]==source_hashes["EVALUATION.json"], "Evaluation completion binding differs")
    construction,execution,plan = [read(paths[name]) for name in ["CONSTRUCTION_CLOSURE.json","EXECUTION_CLOSURE.json","RUN_PLAN.json"]]
    require(report["construction_closure_sha256"]==source_hashes["CONSTRUCTION_CLOSURE.json"] and
            report["execution_closure_sha256"]==source_hashes["EXECUTION_CLOSURE.json"], "Evaluation seal bindings differ")
    require(construction["seeds"]==list(SEEDS) and construction["n_rows"]==N_ROWS and construction["max_tables"]==60,
            "Frozen evaluation schedule differs")
    rows = construction["records"]
    require(len(rows)==20 and len({r["construction_id"] for r in rows})==20, "Construction denominator differs")
    by_id = {r["construction_id"]:r for r in rows}
    planned = {r["construction_id"]:r for r in plan["constructions"]}
    require(len(planned)==20 and set(planned)==set(by_id), "Run plan/closure differs")
    for ident,row in by_id.items():
        require(all(row[k]==planned[ident][k] for k in ["case_id","model_config","context"]), "Construction grouping changed")
    expected = {(ident,seed) for ident in by_id for seed in SEEDS}
    slots = {(s["construction_id"],s["seed"]):s for s in report["all_slots"]}
    receipts = {(s["construction_id"],s["seed"]):s for s in execution["records"]}
    require(len(report["all_slots"])==len(execution["records"])==60 and set(slots)==set(receipts)==expected,
            "All sixty scheduled outcomes must be retained exactly once")
    snapshot_path = safe("_host_only/REFERENCE_SNAPSHOT.json")
    require(sha(snapshot_path)==report["reference_snapshot_sha256"]==construction["reference_snapshot_sha256"], "Reference snapshot binding differs")
    reference = read(snapshot_path)["references"]
    source_hashes["_host_only/REFERENCE_SNAPSHOT.json"] = sha(snapshot_path)
    verified = []
    discrepancies = []
    max_absolute_numeric_difference = 0.
    def check_value(actual,claimed,where):
        nonlocal max_absolute_numeric_difference
        if actual is not None and claimed is not None and isinstance(actual,(int,float)) and isinstance(claimed,(int,float)):
            max_absolute_numeric_difference = max(max_absolute_numeric_difference,abs(actual-claimed))
        if not close(actual,claimed): discrepancies.append({"where":where,"recomputed":actual,"reported":claimed})
    for ident,seed in sorted(expected):
        row,slot = by_id[ident],slots[(ident,seed)]
        case = row["case_id"]
        require(all(slot[k]==row[k] for k in ["case_id","model_config","context"]), "Slot grouping differs")
        receipt_path = safe(f"executions/{ident}/seed_{seed}/execution.json")
        require(sha(receipt_path)==receipts[(ident,seed)]["execution_sha256"], "Execution receipt hash differs")
        receipt = read(receipt_path)
        require(receipt["status"]==slot["execution_status"]==receipts[(ident,seed)]["status"], "Execution status differs")
        require(receipt["seed"]==seed and receipt["construction_id"]==ident, "Execution identity differs")
        entries = _endpoint_maps(slot,case)
        record = {"construction_id":ident,"case_id":case,"seed":seed,"execution_status":slot["execution_status"],
                  "analysis_status":slot["analysis_status"],"recomputed":False,"generated_sha256":None}
        calculated = None
        if receipt["status"]=="success":
            output = safe(f"executions/{ident}/seed_{seed}/output/generated.csv")
            digest = sha(output)
            require(digest==receipt["generated_sha256"]==slot["generated_sha256"], "Generated output hash differs")
            calculated = compute_csv(output,case)
            require(sha(output)==digest, "Generated bytes changed during independent read")
            record.update(recomputed=True,generated_sha256=digest)
            for category in ["analyses","diagnostics"]:
                for key,value in calculated[category].items():
                    reported = entries[category][key]
                    expected_status = "computed" if value is not None else "unavailable"
                    if reported["status"]!=expected_status:
                        discrepancies.append({"where":f"{ident}/{seed}/{key}/status","recomputed":expected_status,"reported":reported["status"]})
                    check_value(value,reported["value"],f"{ident}/{seed}/{key}")
            for key,value in calculated["quality"].items():
                check_value(value,slot.get("quality",{}).get(key),f"{ident}/{seed}/quality/{key}")
        else:
            require(all(e["status"]=="unavailable" and e["value"] is None for c in entries.values() for e in c.values()),
                    "Failed slot unexpectedly supplies scientific values")
        for category in ["analyses","diagnostics"]:
            for key,entry in entries[category].items():
                ref = reference[case][key]
                require(entry["reference"]==ref, "Reported reference differs from sealed aggregate snapshot")
                if entry["status"]==ref["status"]=="computed":
                    signed = entry["value"]-ref["value"]
                    check_value(signed,entry["signed_difference"],f"{ident}/{seed}/{key}/signed_difference")
                    check_value(abs(signed),entry["absolute_difference"],f"{ident}/{seed}/{key}/absolute_difference")
                    require(entry["same_sign"]==bool(np.sign(entry["value"])==np.sign(ref["value"])), "Sign comparison differs")
                else:
                    require(entry["signed_difference"] is None and entry["absolute_difference"] is None and entry["same_sign"] is None,
                            "Unavailable comparison unexpectedly supplies arithmetic")
        verified.append(record)
    expected_summaries = {(ident,category,key) for ident,row in by_id.items()
                          for category in ["analyses","diagnostics"] for key,_ in PLANS[row["case_id"]][category]}
    summaries = {(s["construction_id"],s["category"],s["id"]):s for s in report["construction_summaries"]}
    require(len(report["construction_summaries"])==120 and set(summaries)==expected_summaries,"Summary endpoint coverage differs")
    for (ident,category,key),summary in summaries.items():
        values = [next(e for e in slots[(ident,seed)][category] if e["id"]==key) for seed in SEEDS]
        available = [e for e in values if e["status"]=="computed"]
        comparable = [e for e in values if e["comparison_status"]=="computed"]
        require(summary["scheduled_seeds"]==3 and summary["available_seeds"]==len(available) and summary["comparable_seeds"]==len(comparable),
                "Summary availability denominator differs")
        for field,recomputed in {
            "seed_mean":mean(e["value"] for e in available) if available else None,
            "mean_signed_difference":mean(e["signed_difference"] for e in comparable) if comparable else None,
            "mean_absolute_difference":mean(e["absolute_difference"] for e in comparable) if comparable else None,
        }.items(): check_value(recomputed,summary[field],f"{ident}/{category}/{key}/{field}")
        if available:
            for index,fn in enumerate([min,max]):
                check_value(fn(e["value"] for e in available),summary["seed_range"][index],f"{ident}/{key}/seed_range/{index}")
        else: require(summary["seed_range"] is None,"Unavailable seed range differs")
        require(summary["same_sign_count"]==sum(e["same_sign"] for e in comparable),"Summary sign denominator differs")
    groups = []
    for group_by in ["case_id","model_config","provider"]:
        def group(row): return plan["configs"][row["model_config"]]["provider"] if group_by=="provider" else row[group_by]
        for value in sorted({group(r) for r in rows}):
            chosen = [r for r in rows if group(r)==value]
            selected = [s for (ident,_),s in slots.items() if ident in {r["construction_id"] for r in chosen}]
            groups.append({"group_by":group_by,"group":value,"scheduled_constructions":len(chosen),"scheduled_seed_slots":3*len(chosen),
                           "construction_status_counts":dict(Counter(r["status"] for r in chosen)),
                           "execution_status_counts":dict(Counter(s["execution_status"] for s in selected)),
                           "analysis_status_counts":dict(Counter(s["analysis_status"] for s in selected))})
            require(len(selected)==3*len(chosen),"Group denominator differs")
            if group_by=="case_id": require(len(chosen)==10 and len(selected)==30,"Case denominator differs")
            if group_by=="model_config": require(len(chosen)==4 and len(selected)==12,"Configuration denominator differs")
    successes=sum(s["execution_status"]=="success" for s in slots.values())
    complete=sum(s["analysis_status"]=="complete" for s in slots.values())
    require(report["successful_executions"]==successes and report["complete_endpoint_slots"]==complete,"Headline accounting differs")
    for name,digest in source_hashes.items(): require(sha(safe(name))==digest,"Audit input changed during recomputation")
    return {"kind":"independent_api_pilot_numerical_audit_v1","created_utc":datetime.now(timezone.utc).isoformat(),
            "status":"pass" if not discrepancies else "fail","scheduled_constructions":20,"scheduled_seed_slots":60,
            "recomputed_successful_tables":sum(r["recomputed"] for r in verified),"complete_endpoint_slots":complete,
            "maximum_absolute_numeric_difference":max_absolute_numeric_difference,
            "arithmetic_tolerances":{"absolute":ATOL,"relative":RTOL,"scope":"numerical recomputation only; not scientific acceptance"},
            "source_hashes":source_hashes,"audit_script_sha256":sha(__file__),"all_slots":verified,"groups":groups,
            "discrepancies":discrepancies,"author_generators_read_or_executed":False,"trusted_analyzer_reused":False,
            "patient_rows_read":False,"new_reference_fits":False,"api_or_credentials_accessed":False,
            "method":"Direct numpy.linalg.lstsq; centered vector Pearson correlation; explicit ddof SD; component counts; all-slot/group denominators"}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--evaluation-complete-confirmed-by-root",action="store_true")
    args=parser.parse_args()
    require(args.evaluation_complete_confirmed_by_root,"Root must explicitly authorize execution after evaluation completes")
    output=HERE/"INDEPENDENT_RECOMPUTATION.json"
    require(not output.exists(),"Independent audit is create-only; no silent rerun")
    result=audit()
    with output.open("x",encoding="utf-8",newline="\n") as stream:
        json.dump(result,stream,indent=2,allow_nan=False);stream.write("\n")
    print(json.dumps({k:result[k] for k in ["status","scheduled_seed_slots","recomputed_successful_tables","maximum_absolute_numeric_difference"]},indent=2))
    return 0 if result["status"]=="pass" else 1


if __name__=="__main__": raise SystemExit(main())
