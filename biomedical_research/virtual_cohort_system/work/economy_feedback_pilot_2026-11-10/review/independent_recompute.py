"""Unfrozen, independent numerical audit; run only after root completion notice.

Uses the earlier independent NumPy calculation, never the production analyzer.
Reads final generated CSVs and aggregate receipts only after completion checks.
No generator, API, credential, clinical row source, or reference refit is used.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
from statistics import mean
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
PROJECT=ROOT.parents[1]
INDEPENDENT_SOURCE=PROJECT/"work/cross_model_api_pilot_2026-11-10/review/independent_recompute.py"
SEEDS=[42001,42003,42007]
ATOL=1e-9
RTOL=1e-10


def require(ok,message):
    if not ok:raise ValueError(message)


def read(path):
    def unique(pairs):
        result={}
        for k,v in pairs:
            require(k not in result,"Duplicate JSON key")
            result[k]=v
        return result
    def bad(value):raise ValueError("Nonfinite JSON value: "+value)
    return json.loads(Path(path).read_text(encoding="utf-8-sig"),object_pairs_hook=unique,parse_constant=bad)


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def safe(name):
    relative=Path(name)
    require(not relative.is_absolute() and ".." not in relative.parts,"Invalid relative audit input")
    path=ROOT/relative
    require(path.resolve().is_relative_to(ROOT.resolve()) and path.is_file(),"Missing or external audit input")
    require(not any(p.is_symlink() or bool(getattr(p,"is_junction",lambda:False)()) for p in [path,*path.parents]),"Linked audit input")
    return path


def matches(a,b):
    if a is None or b is None:return a is b
    return isinstance(a,(float,int)) and not isinstance(a,bool) and isinstance(b,(float,int)) and not isinstance(b,bool) and \
           math.isfinite(a) and math.isfinite(b) and math.isclose(a,b,rel_tol=RTOL,abs_tol=ATOL)


def independent_calculation():
    # This source performs no work at import. We call its direct lstsq/centered
    # vector-correlation calculation only, never its old audit/reference reader.
    spec=importlib.util.spec_from_file_location("economy_independent_numpy_calculation",INDEPENDENT_SOURCE)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def audit():
    names=["EVALUATION_COMPLETED.json","EVALUATION.json","INITIAL_SEAL.json","REVIEW_SEAL.json",
           "EVALUATION_CLOSURE.json","DIAGNOSTIC_CLOSURE.json","RUN_PLAN.json"]
    paths={n:safe(n) for n in names}
    hashes={n:sha(p) for n,p in paths.items()}
    completed,report,initial,reviews,closed,diagnostic,plan=[read(paths[n]) for n in names]
    require(completed["files"]["EVALUATION.json"]==hashes["EVALUATION.json"],"Evaluation completion binding differs")
    for field,name in [("initial_seal_sha256","INITIAL_SEAL.json"),("review_seal_sha256","REVIEW_SEAL.json"),
                       ("evaluation_closure_sha256","EVALUATION_CLOSURE.json")]:
        require(report[field]==hashes[name],"Final evaluation seal differs")
    require(initial["seeds"]["evaluation"]==SEEDS and initial["seeds"]["diagnostic"]==[41001,41003,41007],"Seed schedule differs")
    require(report["evaluation_slots"]==36 and report["diagnostic_slots"]==6 and report["max_tables"]==42,"Slot limits differ")
    require(diagnostic["scheduled_slots"]==6 and len(diagnostic["records"])==6,"Diagnostic denominator differs")
    parents={r["parent_id"]:r for r in initial["records"]}
    branches={b["branch_id"]:b for b in initial["branches"]}
    finals={r["branch_id"]:r for r in reviews["records"]}
    require(len(initial["records"])==len(parents)==8 and len(branches)==len(finals)==4 and set(branches)==set(finals),"Initial/review denominator differs")
    versions={ident:dict(row,version_id=ident,version_kind="initial",arm=None) for ident,row in parents.items()}
    for ident,final in finals.items():
        branch=branches[ident]
        require(all(final[k]==branch[k] for k in ["branch_id","parent_id","arm"]),"Paired branch assignment changed")
        parent=parents[final["parent_id"]]
        versions[ident]=dict(parent,version_id=ident,version_kind="review",arm=final["arm"],disposition=final["disposition"])
    expected={(ident,seed) for ident in versions for seed in SEEDS}
    slots={(s["version_id"],s["seed"]):s for s in report["all_slots"]}
    receipts={(r["version_id"],r["seed"]):r for r in closed["records"]}
    require(len(report["all_slots"])==len(closed["records"])==36 and set(slots)==set(receipts)==expected,"All36 scheduled outcomes must remain exactly once")
    # Only after all closure/completion checks can aggregate references be read.
    snapshot=safe("_host_only/REFERENCE_SNAPSHOT.json")
    require(sha(snapshot)==report["reference_snapshot_sha256"]==initial["reference_snapshot_sha256"],"Aggregate snapshot binding differs")
    references=read(snapshot)["references"];hashes["_host_only/REFERENCE_SNAPSHOT.json"]=sha(snapshot)
    arithmetic=independent_calculation()
    results={};verified=[];discrepancies=[];max_difference=0.
    def compare(actual,claimed,where):
        nonlocal max_difference
        if isinstance(actual,(int,float)) and isinstance(claimed,(int,float)) and math.isfinite(actual) and math.isfinite(claimed):
            max_difference=max(max_difference,abs(actual-claimed))
        if not matches(actual,claimed):discrepancies.append({"where":where,"recomputed":actual,"reported":claimed})
    def entries(slot,case):
        value={}
        for category in ["analyses","diagnostics"]:
            expected_units=dict(arithmetic.PLANS[case][category])
            raw=slot[category]
            require(len(raw)==3 and {e["id"] for e in raw}==set(expected_units),"Endpoint coverage differs")
            require(all(e["unit"]==expected_units[e["id"]] for e in raw),"Endpoint unit differs")
            value[category]={e["id"]:e for e in raw}
        return value
    for ident,seed in sorted(expected):
        version,slot=versions[ident],slots[(ident,seed)]
        case=version["case_id"]
        require(all(slot[k]==version[k] for k in ["parent_id","case_id","model_config","role","version_kind","arm"]),"Slot identity/group differs")
        receipt_path=safe(f"executions/evaluation/{ident}/seed_{seed}/execution.json")
        require(sha(receipt_path)==receipts[(ident,seed)]["execution_sha256"],"Execution receipt binding differs")
        receipt=read(receipt_path)
        require(receipt["status"]==slot["execution_status"]==receipts[(ident,seed)]["status"],"Execution status differs")
        require(receipt["version_id"]==ident and receipt["seed"]==seed and receipt["stage"]=="evaluation","Wrong execution identity")
        recorded=entries(slot,case)
        outcome={"version_id":ident,"parent_id":version["parent_id"],"case_id":case,"seed":seed,"execution_status":slot["execution_status"],
                 "analysis_status":slot["analysis_status"],"generated_sha256":None,"recomputed":False}
        if receipt["status"]=="success":
            path=safe(f"executions/evaluation/{ident}/seed_{seed}/output/generated.csv")
            digest=sha(path);require(digest==receipt["generated_sha256"]==slot["generated_sha256"],"Generated hash differs")
            calc=arithmetic.compute_csv(path,case)
            require(sha(path)==digest,"Generated CSV changed during recomputation")
            results[(ident,seed)]=calc
            outcome.update(generated_sha256=digest,recomputed=True,component_violation_count=calc["quality"]["component_violation_count"])
            for category in ["analyses","diagnostics"]:
                for key,value in calc[category].items():
                    got=recorded[category][key]
                    expected_status="computed" if value is not None else "unavailable"
                    require(got["status"]==expected_status,"Endpoint availability differs")
                    compare(value,got["value"],f"{ident}/{seed}/{key}")
            for key,value in calc["quality"].items():compare(value,slot.get("quality",{}).get(key),f"{ident}/{seed}/quality/{key}")
        else:
            require(all(e["status"]=="unavailable" and e["value"] is None for cat in recorded.values() for e in cat.values()),"Failed slot supplies scientific values")
            results[(ident,seed)]={cat:{key:None for key,_ in arithmetic.PLANS[case][cat]} for cat in ["analyses","diagnostics"]}
        for category in ["analyses","diagnostics"]:
            for key,entry in recorded[category].items():
                ref=references[case][key]
                require(entry["reference"]==ref,"Reference aggregate differs from sealed snapshot")
                comparable=entry["status"]==ref["status"]=="computed"
                require(entry["comparison_status"]==("computed" if comparable else "unavailable"),"Comparison availability differs")
                delta=entry["value"]-ref["value"] if comparable else None
                compare(delta,entry["signed_difference"],f"{ident}/{seed}/{key}/signed_difference")
                compare(abs(delta) if delta is not None else None,entry["absolute_difference"],f"{ident}/{seed}/{key}/absolute_difference")
        verified.append(outcome)
    summary_expected={(ident,cat,key) for ident,v in versions.items() for cat in ["analyses","diagnostics"]
                      for key,_ in arithmetic.PLANS[v["case_id"]][cat]}
    summaries={(s["version_id"],s["category"],s["id"]):s for s in report["version_summaries"]}
    require(len(report["version_summaries"])==72 and set(summaries)==summary_expected,"Summary coverage differs")
    for (ident,category,key),summary in summaries.items():
        recorded=[next(e for e in slots[(ident,s)][category] if e["id"]==key) for s in SEEDS]
        available=[r for r in recorded if r["status"]=="computed"]
        comparable=[r for r in recorded if r["comparison_status"]=="computed"]
        require(summary["scheduled_seeds"]==3 and summary["available_seeds"]==len(available) and summary["comparable_seeds"]==len(comparable),"Summary availability denominator differs")
        values=[results[(ident,s)][category][key] for s in SEEDS if results[(ident,s)][category][key] is not None]
        compare(mean(values) if values else None,summary["seed_mean"],f"{ident}/{key}/seed_mean")
        for field,items in [("mean_signed_difference",[r["signed_difference"] for r in comparable]),
                            ("mean_absolute_difference",[r["absolute_difference"] for r in comparable])]:
            compare(mean(items) if items else None,summary[field],f"{ident}/{key}/{field}")
        if values:
            compare(min(values),summary["seed_range"][0],f"{ident}/{key}/seed_range_min")
            compare(max(values),summary["seed_range"][1],f"{ident}/{key}/seed_range_max")
        else:require(summary["seed_range"] is None,"Missing value range differs")
    pair_expected={(p["parent_id"],seed,cat,key) for p in parents.values() if p["role"]=="paired_parent"
                   for seed in SEEDS for cat in ["analyses","diagnostics"] for key,_ in arithmetic.PLANS[p["case_id"]][cat]}
    pairs={(p["parent_id"],p["seed"],p["category"],p["id"]):p for p in report["paired_seed_contrasts"]}
    require(len(report["paired_seed_contrasts"])==36 and set(pairs)==pair_expected,"Paired contrast coverage differs")
    paired_checks=[]
    for (parent,seed,category,key),pair in pairs.items():
        arms={b["arm"]:b["branch_id"] for b in branches.values() if b["parent_id"]==parent}
        require(set(arms)=={"feedback","second_look"},"Paired arm allocation differs")
        actual={"initial":results[(parent,seed)][category][key],
                **{arm:results[(ident,seed)][category][key] for arm,ident in arms.items()}}
        for label,value in actual.items():compare(value,pair["values"][label],f"pair/{parent}/{seed}/{key}/{label}")
        for field,a,b in [("feedback_minus_initial","feedback","initial"),("second_look_minus_initial","second_look","initial"),
                          ("feedback_minus_second_look","feedback","second_look")]:
            delta=actual[a]-actual[b] if actual[a] is not None and actual[b] is not None else None
            compare(delta,pair[field],f"pair/{parent}/{seed}/{key}/{field}")
        paired_checks.append({"parent_id":parent,"seed":seed,"category":category,"id":key,"values":actual,
                              "all_three_available":all(v is not None for v in actual.values())})
    diversity=[]
    for ident in versions:
        values=[v["generated_sha256"] for v in verified if v["version_id"]==ident and v["recomputed"]]
        diversity.append({"version_id":ident,"successful_seed_tables":len(values),"distinct_seed_table_hashes":len(set(values)),
                          "interpretation":"Byte diversity only; not independent constructions or a scientific acceptance criterion"})
    groups=[]
    for field in ["case_id","model_config","version_kind","arm"]:
        for value in sorted({str(v.get(field)) for v in versions.values()}):
            chosen={ident for ident,v in versions.items() if str(v.get(field))==value}
            selected=[s for (ident,_),s in slots.items() if ident in chosen]
            require(len(selected)==3*len(chosen),"Grouped denominator differs")
            groups.append({"group_by":field,"group":value,"scheduled_versions":len(chosen),"scheduled_seed_slots":len(selected),
                           "execution_status_counts":dict(Counter(s["execution_status"] for s in selected)),
                           "analysis_status_counts":dict(Counter(s["analysis_status"] for s in selected))})
    successes=sum(s["execution_status"]=="success" for s in slots.values());complete=sum(s["analysis_status"]=="complete" for s in slots.values())
    require(report["successful_evaluation_tables"]==successes and report["complete_evaluation_tables"]==complete,"Headline denominator differs")
    for name,digest in hashes.items():require(sha(safe(name))==digest,"Audit input changed during recomputation")
    return {"kind":"economy_independent_recomputation_v1","created_utc":datetime.now(timezone.utc).isoformat(),
            "status":"pass" if not discrepancies else "fail","scheduled_evaluation_slots":36,"recomputed_tables":successes,
            "complete_endpoint_slots":complete,"checked_version_summaries":72,"checked_paired_endpoint_seed_contrasts":36,
            "maximum_absolute_numeric_difference":max_difference,"discrepancies":discrepancies,"all_slots":verified,
            "paired_checks":paired_checks,"groups":groups,"seed_hash_diversity":diversity,
            "source_hashes":hashes,"audit_script_sha256":sha(__file__),"independent_calculation_source_sha256":sha(INDEPENDENT_SOURCE),
            "tolerances":{"absolute":ATOL,"relative":RTOL,"scope":"Arithmetic agreement only, not scientific acceptance"},
            "production_analyzer_reused":False,"generator_read_or_executed":False,"api_or_credentials_accessed":False,
            "patient_rows_read":False,"new_reference_fits":False,
            "method":"Independent direct numpy.linalg.lstsq, centered residual Pearson correlation, explicit ddof SD, physical-component fractions/counts, sealed slot summaries and same-parent contrasts"}


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--evaluation-complete-confirmed-by-root",action="store_true")
    args=parser.parse_args();require(args.evaluation_complete_confirmed_by_root,"Wait for root's explicit final-evaluation completion notification")
    output=HERE/"INDEPENDENT_RECOMPUTATION.json";require(not output.exists(),"Audit output is create-only")
    result=audit()
    with output.open("x",encoding="utf-8",newline="\n") as stream:json.dump(result,stream,indent=2,allow_nan=False);stream.write("\n")
    print(json.dumps({k:result[k] for k in ["status","scheduled_evaluation_slots","recomputed_tables","maximum_absolute_numeric_difference"]},indent=2))
    return 0 if result["status"]=="pass" else 1


if __name__=="__main__":raise SystemExit(main())
