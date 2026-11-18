"""Deterministic postclosure generated-table analysis against reused aggregates.

Only fixed trusted estimator code is imported. No patient source, custodian
loader, generator, provider client, or credential is accessed by this module.
"""
from __future__ import annotations
import argparse
import importlib.util
import math
from numbers import Real
from pathlib import Path
from statistics import mean
import sys
import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
import execute_pilot as host

ROOT, PROJECT = host.ROOT, host.PROJECT
PNS_ESTIMATOR = PROJECT / "work/next_case_validation_2026-11-09/runtime/analysis_tools.py"
LIPID_ESTIMATOR = PROJECT / "work/scaleup_2026-11-01/analysis/k02_analysis.py"
REFERENCES = {
    "PNS": (PROJECT / "work/next_case_validation_2026-11-09/RESULTS.json", "reference_weighted"),
    "lipids": (PROJECT / "work/scaleup_2026-11-01/production_release/evaluation/PUBLISHABLE_AGGREGATES.json", "references.K02"),
}
ENDPOINTS = {
    "PNS": {"analyses": [("bmi_sbp", "mmHg per 5 kg/m^2"), ("bmi_dbp", "mmHg per 5 kg/m^2"),
                          ("residual_correlation", "1")],
            "diagnostics": [("sbp.sd_population", "mmHg"), ("dbp.sd_population", "mmHg"),
                            ("sbp_below_dbp_fraction", "1")]},
    "lipids": {"analyses": [("K02-HDL-BMI", "mg/dL per 5 kg/m^2"), ("K02-TC-BMI", "mg/dL per 5 kg/m^2"),
                             ("K02-LIPID-RESIDUAL", "1")],
               "diagnostics": [("total_cholesterol.sd_sample", "mg/dL"), ("hdl_cholesterol.sd_sample", "mg/dL"),
                               ("hdl_above_total_fraction", "1")]},
}
LIMITATIONS = [
    "Developmental comparison using previously exposed clinical aggregate references; no new clinical confirmation.",
    "One construction per case/model configuration/context; repeated seeds are draws from one authored law, not independent constructions or clinical studies.",
    "No source or target quality feedback was supplied during construction; at most one static mechanical repair preceded the construction seal.",
    "The three adjusted estimands are association projections, not causal intervention effects or proof of individual-row recovery.",
    "No new numerical acceptance cutoff, pooled cross-unit score, significance test, superiority gate, or equivalence claim is introduced.",
    "PNS weights describe the declared finite analytical distribution; supplied row-resampling intervals are not design-based national-population confidence intervals.",
    "Lipid reference slopes use the existing selected complete-case sample and HC3 conditional sensitivity intervals; assay and population equivalence are not established by unit conversion.",
    "Missing reference diagnostics remain unavailable; no patient rows, new clinical fits, or reference recalibration are used.",
    "Host-side hashes audit bytes relative to commitments, not cryptographic signatures against a host rewriting artifacts and receipts together.",
]


def finite(value): return isinstance(value, Real) and not isinstance(value, bool) and math.isfinite(value)


def endpoint(identifier, unit, value=None, reason=None, uncertainty=None):
    ok = finite(value)
    return {"id": identifier, "unit": unit, "value": float(value) if ok else None,
            "status": "computed" if ok else "unavailable", "reason": None if ok else (reason or "not_available"),
            "uncertainty": uncertainty or {"status": "unavailable", "reason": "No inferential interval computed for this generated table"}}


def missing(case, reason):
    return {category: [endpoint(key, unit, reason=reason) for key, unit in plan]
            for category, plan in ENDPOINTS[case].items()}


def _load_fixed(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _numeric(frame, columns):
    for name in columns:
        dtype = frame[name].dtype
        if (not pd.api.types.is_numeric_dtype(dtype) or pd.api.types.is_bool_dtype(dtype)
                or pd.api.types.is_complex_dtype(dtype)):
            raise ValueError("Canonical real numeric column required: " + name)
    array = frame[columns].to_numpy(dtype=float, na_value=np.nan)
    if not np.isfinite(array).all(): raise ValueError("Complete finite numerical rows required; no filtering or imputation")
    return array


def analyze_frame(frame, case, expected_rows=3000):
    """Analyze supplied generated rows unchanged apart from declared lipid units."""
    if case not in ENDPOINTS or not isinstance(frame, pd.DataFrame): raise ValueError("Unknown case or frame")
    if list(frame.columns) != host.CASES[case] or not frame.columns.is_unique: raise ValueError("Wrong columns/order")
    if len(frame) < 5 or (expected_rows is not None and len(frame) != expected_rows): raise ValueError("Wrong row count")
    identifier = host.CASES[case][0]
    if frame[identifier].isna().any() or frame[identifier].duplicated().any(): raise ValueError("Missing or duplicate identifiers")
    result = missing(case, "not_estimable")
    if case == "PNS":
        z = _numeric(frame, ["age", "female", "bmi", "sbp", "dbp"])
        if not np.isin(z[:,1], [0, 1]).all(): raise ValueError("female must be numeric 0 or 1")
        if not ((z[:,0] >= 20) & (z[:,0] <= 79)).all(): raise ValueError("PNS age outside declared eligibility")
        raw = _load_fixed(PNS_ESTIMATOR, "api_pilot_trusted_pns").summarize(frame)
        result["analyses"] = [endpoint(key, unit, raw["estimates"][key], reason=raw["status"])
                              for key, unit in ENDPOINTS[case]["analyses"]]
        d = raw["diagnostics"]
        values = [d["margins"]["sbp"]["sd"], d["margins"]["dbp"]["sd"], d["sbp_below_dbp_fraction"]]
        result["diagnostics"] = [endpoint(key, unit, value) for (key,unit), value in zip(ENDPOINTS[case]["diagnostics"], values)]
        result["quality"] = {"design_rank": raw["rank"], "n": len(frame), "row_filtering": False,
                             "component_violation_count": int((z[:,3] < z[:,4]).sum()),
                             "duplicate_measurement_rows": int(frame.drop(columns=[identifier]).duplicated().sum()),
                             "sd_convention": "sqrt(mean((x-mean(x))^2)); equal weights; population ddof=0"}
    else:
        z = _numeric(frame, ["age", "bmi", "total_cholesterol", "hdl_cholesterol"])
        if not frame.sex.isin(["F", "M"]).all(): raise ValueError("sex must be exactly F or M")
        if not (z[:,0] >= 18).all() or not (z[:,1:] > 0).all():
            raise ValueError("Fixed lipid eligibility failed; no rows silently removed")
        converted = frame.copy(deep=True)
        for key in ("total_cholesterol", "hdl_cholesterol"): converted[key] = converted[key] * 38.67
        raw = _load_fixed(LIPID_ESTIMATOR, "api_pilot_trusted_lipid").analyze_frame(converted, role="generated")
        if raw["selection"]["eligible_rows"] != len(frame): raise ValueError("Trusted estimator excluded rows")
        result["analyses"] = [endpoint(key, unit, raw["estimands"][key]["estimate"],
            reason=raw["estimands"][key]["reason"], uncertainty=raw["estimands"][key]["interval"])
            for key,unit in ENDPOINTS[case]["analyses"]]
        values = [float(converted.total_cholesterol.std(ddof=1)), float(converted.hdl_cholesterol.std(ddof=1)),
                  float((z[:,3] > z[:,2]).mean())]
        result["diagnostics"] = [endpoint(key, unit, value) for (key,unit), value in zip(ENDPOINTS[case]["diagnostics"], values)]
        result["quality"] = {"design_rank": raw["design"]["rank"] if raw["design"] else None, "n": len(frame),
            "row_filtering": False, "component_violation_count": int((z[:,3] > z[:,2]).sum()),
            "duplicate_measurement_rows": int(frame.drop(columns=[identifier]).duplicated().sum()),
            "sd_convention": "sample SD ddof=1", "unit_conversion": "mmol/L times 38.67 to mg/dL; not assay harmonization"}
    result["status"] = "complete" if all(e["status"] == "computed" for k in ENDPOINTS[case] for e in result[k]) else "incomplete"
    return result


def stage_reference_snapshot():
    """Host-only preparation from two explicit existing aggregate allowlist files.

    Called before freeze by the evaluation custodian, never by source authors.
    The snapshot is not an author input and contains no clinical rows.
    """
    host.require(not host.safe("CONSTRUCTION_CLOSURE.json", file=False).exists(), "Reference preparation already frozen")
    pns_path, _ = REFERENCES["PNS"]
    lipid_path, _ = REFERENCES["lipids"]
    for path in [pns_path, lipid_path]:
        host.require(not any(host.lifecycle._link(p) for p in [path, *path.parents]), "Linked aggregate input rejected")
    pns_source, lipid_source = host.read(pns_path), host.read(lipid_path)
    pns, lipid = pns_source["reference_weighted"], lipid_source["references"]["K02"]
    refs = {"PNS": {}, "lipids": {}}
    for key,unit in ENDPOINTS["PNS"]["analyses"]:
        supplied = pns_source["reference_row_resampling_stability"]
        uncertainty = {"status": "available", "kind": supplied["interpretation"],
                       "lower": supplied["intervals"][key]["low"], "upper": supplied["intervals"][key]["high"],
                       "seed": supplied["seed"], "repeats": supplied["repeats"], "equivalence_margin": False}
        refs["PNS"][key] = endpoint(key,unit,pns["estimates"][key], uncertainty=uncertainty)
    for key,unit in ENDPOINTS["PNS"]["diagnostics"]:
        value = pns["diagnostics"]["sbp_below_dbp_fraction"] if key == "sbp_below_dbp_fraction" else pns["diagnostics"]["margins"][key.split(".")[0]]["sd"]
        refs["PNS"][key] = endpoint(key,unit,value, uncertainty={"status":"unavailable","reason":"Not supplied in existing aggregate"})
    for key,unit in ENDPOINTS["lipids"]["analyses"]:
        entry = lipid["estimands"][key]
        host.require(entry["unit"] == unit, "Lipid reference unit mismatch")
        refs["lipids"][key] = endpoint(key,unit,entry["estimate"], uncertainty=entry["interval"])
    for key,unit in ENDPOINTS["lipids"]["diagnostics"]:
        value = lipid["metric_denominators"][key.split(".")[0]]["sample_sd"] if key.endswith(".sd_sample") else None
        refs["lipids"][key] = endpoint(key,unit,value, reason="Not present in existing aggregate; no new reference fit",
            uncertainty={"status":"unavailable","reason":"Not supplied in existing aggregate"})
    value = {"kind": "developmental_exposed_aggregate_snapshot_v1", "created_utc": host.now(),
             "author_visible": False, "previously_exposed_references": True, "patient_rows_read": False,
             "new_reference_fits": False, "sources": {case: {"path": str(path), "sha256": host.sha(path), "selector": selector}
             for case,(path,selector) in REFERENCES.items()}, "references": refs,
             "reference_scope": {"PNS": "peso_lab-weighted complete-case finite analytical distribution; n=8352",
                                 "lipids": "Existing K02 / lipid Q5 selected empirical complete-case sample; n=397"}}
    host.write(host.safe("_host_only/REFERENCE_SNAPSHOT.json", file=False), value)
    return {"snapshot_sha256": host.sha(host.safe("_host_only/REFERENCE_SNAPSHOT.json")), "sources": value["sources"]}


def load_references():
    host.evaluation_gate()
    value = host.read(host.safe("_host_only/REFERENCE_SNAPSHOT.json"))
    host.require(value["patient_rows_read"] is False and value["new_reference_fits"] is False and value["author_visible"] is False,
                 "Wrong reference scope")
    for case,(path,selector) in REFERENCES.items():
        bound = value["sources"][case]
        host.require(Path(bound["path"]).resolve() == path.resolve() and bound["selector"] == selector and host.sha(path) == bound["sha256"],
                     "Allowlisted source aggregate changed")
    return value


def compare(payload, case, references):
    for category in ENDPOINTS[case]:
        for entry in payload[category]:
            ref = references[case][entry["id"]]
            host.require(entry["unit"] == ref["unit"], "Endpoint units differ")
            comparable = entry["status"] == ref["status"] == "computed"
            diff = entry["value"] - ref["value"] if comparable else None
            entry.update(reference=ref, comparison_status="computed" if comparable else "unavailable",
                         signed_difference=diff, absolute_difference=abs(diff) if comparable else None,
                         same_sign=(np.sign(entry["value"]) == np.sign(ref["value"])).item() if comparable else None)
    return payload


def summarize(slots, constructions):
    rows = []
    for construction in constructions:
        chosen = [r for r in slots if r["construction_id"] == construction["construction_id"]]
        host.require(len(chosen) == 3, "Wrong seed coverage")
        case = construction["case_id"]
        for category, plan in ENDPOINTS[case].items():
            for key,unit in plan:
                entries = [next(e for e in s[category] if e["id"] == key) for s in chosen]
                available = [e for e in entries if e["status"] == "computed"]
                comparable = [e for e in entries if e["comparison_status"] == "computed"]
                values = [e["value"] for e in available]
                rows.append({"construction_id": construction["construction_id"], "case_id": case,
                             "model_config": construction.get("model_config"), "context": construction.get("context"),
                             "category": category, "id": key, "unit": unit, "scheduled_seeds": 3,
                             "available_seeds": len(values), "comparable_seeds": len(comparable),
                             "seed_mean": mean(values) if values else None,
                             "seed_range": [min(values), max(values)] if values else None,
                             "reference": entries[0]["reference"],
                             "mean_signed_difference": mean(e["signed_difference"] for e in comparable) if comparable else None,
                             "mean_absolute_difference": mean(e["absolute_difference"] for e in comparable) if comparable else None,
                             "same_sign_count": sum(e["same_sign"] for e in comparable)})
    return rows


def markdown(report):
    def fmt(x):
        if x is None: return "unavailable"
        if isinstance(x, float): return f"{x:.6g}"
        return str(x).replace("|", "\\|").replace("\n", " ")
    lines = ["# Cross-model API construction pilot: scientific analysis", "",
             f"Scheduled constructions: 20. Scheduled seed slots: 60. Successful executions: {report['successful_executions']}/60. "
             f"Complete endpoint sets: {report['complete_endpoint_slots']}/60.", "",
             "All initial and final constructions were sealed before execution. Only existing aggregate references were reused. "
             "These are developmental results; no patient rows were read and no reference model was refit.", ""]
    lines.extend("- " + line for line in LIMITATIONS)
    for category,title in [("analyses", "Primary adjusted estimands"), ("diagnostics", "Secondary SD and component diagnostics")]:
        lines += ["", "## " + title, "", "| Construction | Endpoint | Unit | Available/3 | Seed mean | Seed range | Reference | Mean signed difference | Mean absolute difference |",
                  "|---|---|---|---:|---:|---|---:|---:|---:|"]
        for row in report["construction_summaries"]:
            if row["category"] != category: continue
            vals = [row[k] for k in ["construction_id","id","unit","available_seeds","seed_mean","seed_range"]]
            vals += [row["reference"]["value"],row["mean_signed_difference"],row["mean_absolute_difference"]]
            lines.append("| " + " | ".join(map(fmt,vals)) + " |")
    lines += ["", "## Every scheduled slot", "", "| Construction | Seed | Execution | Analysis | Failure |", "|---|---:|---|---|---|"]
    for row in report["all_slots"]:
        lines.append("| " + " | ".join(fmt(row[k]) for k in ["construction_id","seed","execution_status","analysis_status","failure_type"]) + " |")
    lines += ["", "Endpoint-level seed values, supplied reference uncertainty, provenance hashes, and unavailable entries are retained in EVALUATION.json. "
              "Seed ranges are descriptive ranges, not confidence intervals. Component violations are counted in the delivered rows without silently repairing them.", ""]
    return "\n".join(lines)


def evaluate():
    constructions, closed = host.evaluation_gate()  # Before references or generated-table reads.
    outputs = ["EVALUATION_STARTED.json", "EVALUATION.json", "EVALUATION.md", "EVALUATION_COMPLETED.json", "EVALUATION_FAILURE.json"]
    host.require(not any(host.safe(p,file=False).exists() for p in outputs), "Evaluation create-only; no silent rerun")
    host.write(host.safe("EVALUATION_STARTED.json",file=False), {"created_utc":host.now(),
        "construction_closure_sha256":host.sha(host.safe("CONSTRUCTION_CLOSURE.json")),
        "execution_closure_sha256":host.sha(host.safe("EXECUTION_CLOSURE.json"))})
    try:
        references = load_references()
        slots = []
        for construction in constructions["records"]:
            case, ident = construction["case_id"], construction["construction_id"]
            for seed in host.SEEDS:
                receipt = host.verify_execution(ident,seed)
                slot = {"construction_id":ident,"case_id":case,"seed":seed,
                        "model_config":construction.get("model_config"),"context":construction.get("context"),
                        "execution_status":receipt["status"],"analysis_status":"unavailable",
                        "failure_type":receipt["failure_class"],"generated_sha256":receipt["generated_sha256"]}
                payload = missing(case, "Scheduled generated table unavailable: " + receipt["status"])
                if receipt["status"] == "success":
                    try:
                        task = host.task_for(construction)
                        path = host.run_inventory()[(ident,seed)] / "output/generated.csv"
                        host.execution._csv_guard(path,task,host.LIMITS["output_bytes"])
                        frame = host.lifecycle.read_table(path,task,output=True)
                        host.validate_generated_output(frame,task,case)
                        payload = analyze_frame(frame,case)
                        slot["analysis_status"] = payload.pop("status")
                    except Exception as error:
                        slot.update(analysis_status="failed",failure_type=type(error).__name__)
                        payload = missing(case,"Generated table analysis failed; local error type retained")
                slot.update(compare(payload,case,references["references"]))
                slots.append(slot)
        host.evaluation_gate()
        load_references()
        report = {"kind":"cross_model_api_pilot_scientific_evaluation_v1","created_utc":host.now(),
                  "developmental":True,"previously_exposed_references":True,"patient_rows_read":False,"new_reference_fits":False,
                  "no_acceptance_cutoff":True,"scheduled_constructions":20,"scheduled_slots":60,
                  "successful_executions":sum(s["execution_status"]=="success" for s in slots),
                  "complete_endpoint_slots":sum(s["analysis_status"]=="complete" for s in slots),
                  "reference_snapshot_sha256":host.sha(host.safe("_host_only/REFERENCE_SNAPSHOT.json")),
                  "construction_closure_sha256":host.sha(host.safe("CONSTRUCTION_CLOSURE.json")),
                  "execution_closure_sha256":host.sha(host.safe("EXECUTION_CLOSURE.json")),
                  "reference_sources":references["sources"],"all_slots":slots,
                  "construction_summaries":summarize(slots,constructions["records"]),"limitations":LIMITATIONS}
        host.write(host.safe("EVALUATION.json",file=False),report)
        with host.safe("EVALUATION.md",file=False).open("x",encoding="utf-8",newline="\n") as stream: stream.write(markdown(report))
        host.write(host.safe("EVALUATION_COMPLETED.json",file=False),{"created_utc":host.now(),"files":{
            name:host.sha(host.safe(name)) for name in ["EVALUATION.json","EVALUATION.md"]}})
        return {key:report[key] for key in ["scheduled_constructions","scheduled_slots","successful_executions","complete_endpoint_slots"]}
    except Exception as error:
        host.write(host.safe("EVALUATION_FAILURE.json",file=False),{"created_utc":host.now(),"error_type":type(error).__name__,
                   "message":"Stopped without silent rerun; inspect local state"})
        raise


if __name__ == "__main__":
    import json
    parser=argparse.ArgumentParser();parser.add_argument("command",choices=["stage-references","evaluate"])
    args=parser.parse_args()
    print(json.dumps(stage_reference_snapshot() if args.command=="stage-references" else evaluate(),indent=2,allow_nan=False))
