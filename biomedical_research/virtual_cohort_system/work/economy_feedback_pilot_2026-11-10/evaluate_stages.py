"""Generated-only diagnostic release, then post-review aggregate evaluation.

Reference access exists only behind the complete evaluation-stage closure gate.
The diagnostic report carries no targets, reference values, desired signs,
recommended parameters, or other authors' outputs.
"""
from __future__ import annotations
import argparse
from functools import lru_cache
import importlib.util
import json
from pathlib import Path
from statistics import mean
import sys
import numpy as np
import pandas as pd
import execute_stages as host

ROOT=host.ROOT
PRIMARY_COMPONENT={"PNS":"sbp_below_dbp_fraction","lipids":"hdl_above_total_fraction"}


@lru_cache(maxsize=1)
def trusted():
    """Load fixed generated-statistic functions; no reference/evaluate call."""
    previous=host.PREVIOUS
    sys.path.insert(0,str(previous))
    try:
        spec=importlib.util.spec_from_file_location("economy_trusted_previous_statistics",previous/"analyze_pilot.py")
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    finally:sys.path.remove(str(previous))
    return module


def frame_for(stage,row,seed):
    receipt=host.verify_execution(stage,row["version_id"],seed)
    if receipt["status"]!="success":return None,receipt
    path=host.runs(stage)[(row["version_id"],seed)]/"output/generated.csv"
    task=host.task_for(row)
    host.execution._csv_guard(path,task,host.LIMITS["output_bytes"])
    frame=host.lifecycle.read_table(path,task,output=True)
    host.validate_output(frame,task,row["case_id"])
    return frame,receipt


def extras(frame,case,task):
    """Descriptive generated-only margins and residual RMS in declared units."""
    units={c["name"]:c["unit"] for c in task["columns"]}
    identifier=task["row_id"]
    margins={}
    for name in frame.columns:
        if name==identifier:continue
        if name=="sex":
            margins[name]={"unit":units[name],"counts":{k:int(frame[name].eq(k).sum()) for k in ["F","M"]},
                           "fractions":{k:float(frame[name].eq(k).mean()) for k in ["F","M"]}}
        else:
            y=frame[name].to_numpy(dtype=float)
            margins[name]={"unit":units[name],"mean":float(y.mean()),"sd_population_ddof0":float(y.std(ddof=0)),
                           "sd_sample_ddof1":float(y.std(ddof=1)),"minimum":float(y.min()),"maximum":float(y.max()),
                           "quantiles":{str(q):float(np.quantile(y,q,method="linear")) for q in [.01,.05,.5,.95,.99]}}
    female=frame.female.to_numpy(dtype=float) if case=="PNS" else frame.sex.eq("F").to_numpy(dtype=float)
    x=np.column_stack([np.ones(len(frame)),(frame.age.to_numpy()-50)/10,female,(frame.bmi.to_numpy()-25)/5])
    rank=int(np.linalg.matrix_rank(x));outcomes=["sbp","dbp"] if case=="PNS" else ["total_cholesterol","hdl_cholesterol"]
    y=frame[outcomes].to_numpy(dtype=float)*(1 if case=="PNS" else 38.67)
    residual_rms={name:None for name in outcomes}
    if rank==4:
        residual=y-x@np.linalg.lstsq(x,y,rcond=None)[0]
        residual_rms={name:float(np.sqrt(np.mean(residual[:,i]**2))) for i,name in enumerate(outcomes)}
    gap=y[:,0]-y[:,1]
    return {"schema_and_finite":"passed","margins_in_delivered_units":margins,"full_design_rank":rank,
            "residual_rms":{"definition":"sqrt(mean(residual^2)); no degrees-of-freedom correction",
                "unit":"mmHg" if case=="PNS" else "mg/dL","design":["1","(age-50)/10","female","(bmi-25)/5"],
                "values":residual_rms},
            "component_gap":{"definition":"SBP minus DBP" if case=="PNS" else "total cholesterol minus HDL",
                "unit":"mmHg" if case=="PNS" else "mg/dL","minimum":float(gap.min()),
                "q01":float(np.quantile(gap,.01)),"median":float(np.median(gap)),"negative_count":int((gap<0).sum())},
            "source_or_declared_statistic_comparison":{"status":"not_comparable","reason":"No matched declarative source-statistic operator supplied; no automatic discrepancy or correction inferred"}}


def analyze_generated(stage,row,seed):
    frame,receipt=frame_for(stage,row,seed)
    slot={"version_id":row["version_id"],"parent_id":row["parent_id"],"case_id":row["case_id"],"seed":seed,
          "model_config":row["model_config"],"role":row["role"],"version_kind":row["version_kind"],"arm":row.get("arm"),
          "disposition":row.get("disposition"),"execution_status":receipt["status"],"analysis_status":"unavailable",
          "failure_type":receipt["failure_class"],"generated_sha256":receipt["generated_sha256"]}
    payload=trusted().missing(row["case_id"],"Scheduled generated table unavailable: "+receipt["status"])
    if frame is not None:
        try:
            payload=trusted().analyze_frame(frame,row["case_id"])
            slot["analysis_status"]=payload.pop("status")
            payload["additional_generated_diagnostics"]=extras(frame,row["case_id"],host.task_for(row))
        except Exception as error:
            slot.update(analysis_status="failed",failure_type=type(error).__name__)
            payload=trusted().missing(row["case_id"],"Generated-only analysis failed; no silent filtering or repair")
    slot.update(payload);return slot


def prepare_diagnostics():
    """Both paired parents finish diagnostic draws before either feedback release."""
    host.verify_stage_closure("diagnostic")
    host.require(not host.safe("DIAGNOSTIC_REPORTS.json",file=False).exists(),"Diagnostic report generation is create-only")
    reports={}
    for row in host.versions("diagnostic"):
        slots=[analyze_generated("diagnostic",row,seed) for seed in host.SEEDS["diagnostic"]]
        # This whitelist projection carries only the recipient's own generated summaries.
        payload={"kind":"own_generated_diagnostic_feedback_v1","parent_id":row["parent_id"],"case_id":row["case_id"],
                 "scheduled_seeds":host.SEEDS["diagnostic"],"scheduled_rows_per_seed":3000,
                 "interpretation":"These three fixed-seed generated draws describe one authored law; they are not clinical evidence, confidence intervals, or scientific acceptance decisions.",
                 "diagnostics_by_seed":[{k:v for k,v in s.items() if k in {"seed","execution_status","analysis_status","failure_type",
                     "analyses","diagnostics","quality","additional_generated_diagnostics"}} for s in slots],
                 "revision_scope":"Use your own scientific judgment; no formula, sign, parameter, or correction is recommended by this diagnostic report."}
        path=f"_host_only/diagnostic_reports/{row['parent_id']}.json"
        host.write(host.safe(path,file=False),payload)
        reports[row["parent_id"]]={"path":path,"sha256":host.sha(host.safe(path))}
    host.verify_stage_closure("diagnostic")
    manifest={"kind":"economy_generated_only_diagnostic_reports_v1","created_utc":host.now(),
              "diagnostic_closure_sha256":host.sha(host.safe("DIAGNOSTIC_CLOSURE.json")),"reports":reports,
              "target_reference_read":False,"other_authors_in_feedback":False,"scientific_parameters_recommended":False}
    host.write(host.safe("DIAGNOSTIC_REPORTS.json",file=False),manifest)
    return manifest


def feedback_for(branch_id):
    """Only a preassigned feedback branch may request its own parent's report."""
    initial=host.verify_initial();manifest=host.verify_diagnostic_reports()
    branches=[b for b in initial["branches"] if b["branch_id"]==branch_id]
    host.require(len(branches)==1 and branches[0]["arm"]=="feedback","Ordinary second-look branch cannot receive generated diagnostic feedback")
    entry=manifest["reports"][branches[0]["parent_id"]]
    payload=host.read(host.safe(entry["path"]))
    host.require(payload["parent_id"]==branches[0]["parent_id"],"Feedback parent mismatch")
    return payload


def references_after_evaluation():
    host.verify_stage_closure("evaluation")
    initial=host.verify_initial();path=host.safe("_host_only/REFERENCE_SNAPSHOT.json")
    host.require(host.sha(path)==initial["reference_snapshot_sha256"],"Aggregate snapshot changed")
    value=host.read(path)
    host.require(value["author_visible"] is False and value["patient_rows_read"] is False and value["new_reference_fits"] is False,
                 "Unexpected reference scope")
    return value


def version_summaries(slots,rows):
    summaries=[]
    for row in rows:
        chosen=[s for s in slots if s["version_id"]==row["version_id"]]
        host.require(len(chosen)==3,"Wrong version seed coverage")
        for category in ["analyses","diagnostics"]:
            for key,unit in trusted().ENDPOINTS[row["case_id"]][category]:
                entries=[next(e for e in s[category] if e["id"]==key) for s in chosen]
                available=[e for e in entries if e["status"]=="computed"]
                comparable=[e for e in entries if e["comparison_status"]=="computed"]
                values=[e["value"] for e in available]
                summaries.append({"version_id":row["version_id"],"parent_id":row["parent_id"],"case_id":row["case_id"],
                    "model_config":row["model_config"],"role":row["role"],"version_kind":row["version_kind"],"arm":row.get("arm"),
                    "category":category,"id":key,"unit":unit,"scheduled_seeds":3,"available_seeds":len(values),"comparable_seeds":len(comparable),
                    "seed_mean":mean(values) if values else None,"seed_range":[min(values),max(values)] if values else None,
                    "reference":entries[0]["reference"],"mean_signed_difference":mean(e["signed_difference"] for e in comparable) if comparable else None,
                    "mean_absolute_difference":mean(e["absolute_difference"] for e in comparable) if comparable else None})
    return summaries


def paired_contrasts(slots):
    initial=host.verify_initial();by_key={(s["version_id"],s["seed"]):s for s in slots};result=[]
    for parent in [r for r in initial["records"] if r["role"]=="paired_parent"]:
        branches={b["arm"]:b["branch_id"] for b in initial["branches"] if b["parent_id"]==parent["parent_id"]}
        for seed in host.SEEDS["evaluation"]:
            chosen={"initial":by_key[(parent["parent_id"],seed)],**{arm:by_key[(ident,seed)] for arm,ident in branches.items()}}
            for category in ["analyses","diagnostics"]:
                for key,unit in trusted().ENDPOINTS[parent["case_id"]][category]:
                    values={name:next(e for e in s[category] if e["id"]==key)["value"] for name,s in chosen.items()}
                    def difference(a,b):return values[a]-values[b] if values[a] is not None and values[b] is not None else None
                    result.append({"parent_id":parent["parent_id"],"case_id":parent["case_id"] ,"seed":seed,"category":category,"id":key,"unit":unit,
                        "values":values,"feedback_minus_initial":difference("feedback","initial"),"second_look_minus_initial":difference("second_look","initial"),
                        "feedback_minus_second_look":difference("feedback","second_look"),
                        "interpretation":"Shared-parent, same-label-seed descriptive contrast; different laws need not preserve common random-number coupling. No causal feedback-effect or acceptance inference."})
    return result


def review_reporting_provenance():
    rows=[]
    for record in host.verify_reviews()["records"]:
        name=f"calls/review/{record['branch_id']}/artifact.json"
        path=host.safe(name,file=False)
        rows.append({"branch_id":record["branch_id"],"disposition":record["disposition"],
                     "returned_artifact_path":name if path.exists() else None,
                     "returned_artifact_sha256":host.sha(path) if path.exists() else None,
                     "selected_data_law_candidate_path":record["candidate_path"],
                     "claim_coverage_and_correctness":"not_assessed_by_numerical_evaluator",
                     "interpretation":"Returned review decision remains in the captured artifact. Retaining an initial data law does not imply an unchanged explanation or reporting record."})
    return rows


def markdown(report):
    def fmt(v):return "unavailable" if v is None else f"{v:.6g}" if isinstance(v,float) else str(v).replace("|","\\|")
    lines=["# Economy paired-feedback pilot", "",f"Evaluation slots: {report['successful_evaluation_tables']}/36 executed successfully; "
           f"{report['complete_evaluation_tables']}/36 have complete endpoint sets. Diagnostic slots were separately fixed at 6.","",
           "Only two preassigned Sol initial laws received diagnostic sampling. Their feedback and ordinary second-look branches shared the exact initial artifact. "
           "All four final review dispositions were sealed before fresh evaluation seeds. Retained/no-op and review-failed branches remain separately identified.","",
           "Primary inspection concerns component consistency in generated data. Previously exposed aggregate reference comparisons describe the adjusted analyses and scales; "
           "they supply no construction feedback and do not establish fresh clinical confirmation.","",
           "| Version | Case | Kind | Arm | Seed | Execution | Analysis |", "|---|---|---|---|---:|---|---|"]
    for s in report["all_slots"]:lines.append("| "+" | ".join(fmt(s[k]) for k in ["version_id","case_id","version_kind","arm","seed","execution_status","analysis_status"])+" |")
    lines += ["","## Component consistency and adjusted analyses","", "| Version | Endpoint | Unit | Available/3 | Mean | Range | Reference | Mean absolute deviation |", "|---|---|---|---:|---:|---|---:|---:|"]
    for s in report["version_summaries"]:
        lines.append("| "+" | ".join(fmt(v) for v in [s["version_id"],s["id"],s["unit"],s["available_seeds"],s["seed_mean"],s["seed_range"],s["reference"]["value"],s["mean_absolute_difference"]])+" |")
    lines += ["","Each seed remains a draw from one law. Seed ranges are not confidence intervals; no numeric superiority, equivalence, pooled score, or new acceptance threshold is applied. "
              "Component violations are counted without altering delivered values. A feedback contrast uses one shared parent per case and cannot establish a general model-level or causal feedback effect.",""]
    return "\n".join(lines)


def evaluate():
    host.verify_stage_closure("evaluation")
    names=["EVALUATION_STARTED.json","EVALUATION.json","EVALUATION.md","EVALUATION_COMPLETED.json","EVALUATION_FAILURE.json"]
    host.require(not any(host.safe(n,file=False).exists() for n in names),"Evaluation is create-only")
    host.write(host.safe(names[0],file=False),{"created_utc":host.now(),"evaluation_closure_sha256":host.sha(host.safe("EVALUATION_CLOSURE.json"))})
    try:
        references=references_after_evaluation();rows=host.versions("evaluation");slots=[]
        for row in rows:
            for seed in host.SEEDS["evaluation"]:
                slot=analyze_generated("evaluation",row,seed)
                trusted().compare(slot,row["case_id"],references["references"]);slots.append(slot)
        host.verify_stage_closure("evaluation")
        report={"kind":"economy_paired_feedback_evaluation_v1","created_utc":host.now(),"developmental":True,
                "previously_exposed_references":True,"patient_rows_read":False,"new_reference_fits":False,"target_feedback":False,
                "scheduled_initial_laws":8,"scheduled_review_branches":4,"diagnostic_slots":6,"evaluation_slots":36,"max_tables":42,
                "primary_inspection":"component consistency; no required direction or numeric acceptance threshold",
                "successful_evaluation_tables":sum(s["execution_status"]=="success" for s in slots),
                "complete_evaluation_tables":sum(s["analysis_status"]=="complete" for s in slots),
                "initial_seal_sha256":host.sha(host.safe("INITIAL_SEAL.json")),"review_seal_sha256":host.sha(host.safe("REVIEW_SEAL.json")),
                "evaluation_closure_sha256":host.sha(host.safe("EVALUATION_CLOSURE.json")),"reference_snapshot_sha256":host.sha(host.safe("_host_only/REFERENCE_SNAPSHOT.json")),
                "reference_sources":references["sources"],"all_slots":slots,"version_summaries":version_summaries(slots,rows),
                "paired_seed_contrasts":paired_contrasts(slots),"review_dispositions":host.verify_reviews()["records"],
                "review_reporting_provenance":review_reporting_provenance(),
                "limitations":["One shared parent per case; review branches are dependent, not independent constructions.",
                    "Both ordinary second-look and diagnostic feedback receive a second API opportunity; no rescue of failed parents or post-output parent selection.",
                    "Fresh evaluation seeds differ from diagnostic seeds; matching seed labels need not induce common random numbers across different laws.",
                    "Previously exposed clinical aggregates and unbalanced model allocation make this developmental rather than confirmatory or a model ranking.",
                    "No clinical rows, new clinical reference fits, automatic scientific host edits, or output-informed replacement draws."]}
        host.write(host.safe("EVALUATION.json",file=False),report)
        with host.safe("EVALUATION.md",file=False).open("x",encoding="utf-8",newline="\n") as stream:stream.write(markdown(report))
        host.write(host.safe("EVALUATION_COMPLETED.json",file=False),{"created_utc":host.now(),"files":{n:host.sha(host.safe(n)) for n in ["EVALUATION.json","EVALUATION.md"]}})
        return {k:report[k] for k in ["evaluation_slots","successful_evaluation_tables","complete_evaluation_tables"]}
    except Exception as error:
        host.write(host.safe("EVALUATION_FAILURE.json",file=False),{"created_utc":host.now(),"error_type":type(error).__name__,"message":"Stopped without silent rerun"})
        raise


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("command",choices=["prepare-diagnostics","evaluate"]);a=p.parse_args()
    print(json.dumps(prepare_diagnostics() if a.command=="prepare-diagnostics" else evaluate(),indent=2,allow_nan=False))
