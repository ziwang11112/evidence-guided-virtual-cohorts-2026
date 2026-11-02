"""Designated Wave A evaluator. Reference bytes are read only after reveal gates.

No import, manifest preparation or CLI help loads participant records. Local
procedural commitments are not signatures or protection against a hostile host.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import importlib.util
import io
import json
import math
import numbers
from pathlib import Path
import re
import sys

import numpy as np
import pandas as pd
from pandas.io.stata import StataMissingValue, StataReader

HERE = Path(__file__).resolve().parent
SCALE = HERE.parent.parent
GRID = (0.05, 0.10, 0.20, 0.30)
CASES = ("K01", "K02")
CONSTRUCTORS = ("A01", "A02", "A03", "A04", "A05", "S01")
SEEDS = (2101, 2102, 2103)
IDS = {"K01": ("K01-GLUCOSE-BMI", "K01-GLUCOSE-AGE", "K01-SEX-BMI"),
       "K02": ("K02-HDL-BMI", "K02-TC-BMI", "K02-LIPID-RESIDUAL")}
MAPPINGS = {"K01": {"prim_key":"id", "rage":"age", "rsex":"sex", "c_bs_bmi":"bmi", "c_bs_glucose":"glucose"},
            "K02": {"Individual ID":"id", "Age":"age", "Sex":"sex", "BMI":"bmi",
                    "Total cholesterol":"total_cholesterol", "HDL cholesterol":"hdl_cholesterol"}}
DEPENDENCIES = (
    "case_k01/analysis/k01_analysis.py", "case_k01/analysis/K01_ANALYSIS_SPEC_v1.json",
    "analysis/k02_analysis.py", "analysis/K02_ANALYSIS_SPEC_v0.json",
    "case_k01/implementation/generated_validity.py", "case_k02/implementation/generated_validity.py",
    "bridge_units/unit_conversion.py", "case_k02/unit_mapping/APPROVED_MANIFEST.json",
    "case_k02/unit_mapping/INPUT_CONTRACT.json", "case_k02/unit_mapping/OUTPUT_CONTRACT.json",
    "admission_next/HAALSI_DATA_SCHEMA_AUDIT.json", "TURKANA_SCHEMA_AUDIT.json",
    "case_k01/CONTRACT_DECISION_2026-11-02.md", "K02_PROSPECTIVE_DECISIONS_2026-11-02.md",
    "K02_ADMISSION_REVIEW_2026-11-02.md",
)


class EvaluationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise EvaluationError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def same(left, right, message):
    require(canonical(left) == canonical(right), message)


def _module(name, relative):
    path = (SCALE/relative).resolve()
    name = "wave_a_evaluation_" + name
    if name in sys.modules:
        module = sys.modules[name]
        require(Path(module.__file__).resolve() == path, "Analysis module path changed")
        return module
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _controller():
    path = SCALE/"production_integration/campaign_control"
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
    import campaign_control
    require(Path(campaign_control.__file__).resolve() == path/"campaign_control.py", "Controller module path changed")
    return campaign_control


def prepare_evaluation_manifest(output_directory):
    """Metadata only: copy recorded target identities, never hash/read raw files."""
    output = Path(output_directory).resolve()
    haalsi = read_json(SCALE/"admission_next/HAALSI_DATA_SCHEMA_AUDIT.json")
    turkana = read_json(SCALE/"TURKANA_SCHEMA_AUDIT.json")
    targets = {
        "K01": {"path":str((SCALE/"admission_next/private_data"/haalsi["input"]["filename"]).resolve()),
                "sha256":haalsi["input"]["sha256"], "bytes":haalsi["input"]["bytes"],
                "format":"stata", "raw_mapping":MAPPINGS["K01"], "rows_in_schema_audit":haalsi["file_dimensions"]["rows"]},
        "K02": {"path":str((SCALE/"private_data/22Jul20_for_Dryad_noIDs.txt").resolve()),
                "sha256":turkana["sha256"], "bytes":turkana["bytes"], "format":"utf8_sig_tsv",
                "raw_mapping":MAPPINGS["K02"], "rows_in_schema_audit":turkana["rows_in_deposit"]},
    }
    return {"schema_version":1, "kind":"wave_a_fixed_evaluation_manifest", "output_directory":str(output),
        "target_files":targets,
        "dependencies":[{"path":str((SCALE/name).resolve()), "sha256":file_hash(SCALE/name)} for name in DEPENDENCIES],
        "policy":{"cases":list(CASES), "constructors":list(CONSTRUCTORS), "stages":["initial","final"],
            "target_seeds":list(SEEDS), "target_rows_per_generated_table":5000,
            "fixed_target_report_slots":72, "final_target_slots":36, "working_resolution":0.10,
            "complete_sensitivity_grid":list(GRID), "case_agent_pass_requirement":"at_least_4_of_all_5",
            "constructor_pass_requirement":"whole_stage_verified_success_and_all_3_estimands_on_all_3_seeds",
            "pre_reveal_failure_accounting":"Available target diagnostics retained; source execution or guard failure prevents construction pass at every margin",
            "zero_anchor":"all_three_within_0.10_means_insufficient_discrimination",
            "positive_wave_a":"K01_final_reliability_and_K01_discrimination_required;K02_alone_insufficient",
            "wave_b_automatic_execution":False, "weights":"none", "clinical_equivalence_claim":False,
            "k01_missing":"native_and_tagged_Stata_missing_only;finite_sentinel_list_empty",
            "k01_sex_mapping":{"1":"M","2":"F"}, "k01_fasting_or_flag_filter":False,
            "k02_missing_tokens_after_strip":["","NA"], "k02_sex":"stripped_literal_F_M_no_biological_legend_claim",
            "k02_reference_lipids":"already_mg/dL_no_conversion",
            "k02_generated_lipids":"approved_manifest_mmol/L_to_mg/dL"}}


def _gate(ledger_path, manifest_path, reveal_receipt_sha256):
    """Only metadata/code are read here. Generated data are verified next."""
    cc = _controller()
    ledger = cc.CampaignLedger.open(ledger_path)
    state, events = ledger._read()
    released = ledger.manifest
    evaluator = {"path":str(Path(__file__).resolve()), "sha256":file_hash(__file__)}
    same(released["designated_evaluator"], evaluator, "This is not the exact designated evaluator")
    path = Path(manifest_path).resolve()
    binding = {"path":str(path), "sha256":file_hash(path)}
    require(binding in released["artifacts"], "Evaluation manifest is not in the approved release")
    manifest = read_json(path)
    same(manifest, prepare_evaluation_manifest(manifest["output_directory"]), "Fixed evaluation manifest differs")
    require(all(dep in released["artifacts"] for dep in manifest["dependencies"]), "Evaluation dependency omitted from release")
    require(state["wave_closed"] is not None and state["reveal"] is not None, "Both-case closure and reveal required")
    reveals = [event for event in events if event["kind"] == "target_reveal"]
    require(len(reveals) == 1 and reveals[0]["event_sha256"] == reveal_receipt_sha256, "Exact single reveal receipt required")
    reveal = reveals[0]["payload"]
    require(reveal["release_sha256"] == ledger.release_sha256 and reveal["evaluator_code_sha256"] == evaluator["sha256"], "Reveal release/evaluator differs")
    same(reveal["cases"], list(CASES), "Reveal must cover both cases")
    same(reveal["closed_inventory_sha256"], state["wave_closed"]["closed_inventory_sha256"], "Reveal inventory differs")
    expected_keys = {f"{case}:{constructor}" for case in CASES for constructor in CONSTRUCTORS}
    require(set(state["constructors"]) == expected_keys and all(x["closed"] for x in state["constructors"].values()), "Incomplete constructor inventory")
    closed = {key:entry["closed"] for key,entry in state["constructors"].items()}
    same(closed, state["wave_closed"]["closed_inventory"], "Closed inventory changed")
    require(digest(closed) == reveal["closed_inventory_sha256"], "Closed inventory digest differs")
    return ledger, state, manifest, binding


def _verify_inventory(ledger, state):
    """Authenticate every usable initial/final output before measured target read."""
    cc = _controller()
    for key, record in state["constructors"].items():
        case, constructor = key.split(":")
        same(record["closed"]["final_inventory"], ledger._final_inventory(case,constructor,record), "Final aliases/inventory differ")
        for stage, entry in record["stages"].items():
            same(cc._inspect(entry["bundle"],entry["candidate"]),
                 {name:entry[name] for name in ("bundle","candidate","parent","plan")}, "Frozen candidate changed")
            cc._validate_plan(entry["plan"],case,constructor,stage)
            result = entry["result"]
            if result is not None and result["verified"] is not None:
                fresh = cc._verify_stage(entry["bundle"],entry["candidate"],case)
                same(fresh,result["verified"],"Execution/guard artifacts changed after closure")
                same(fresh["guards"]["authorization"],ledger._authorization(case,constructor,stage,entry), "Stage belongs to another authorization")
    return {key:{stage:{"parent":entry["parent"], "result_status":None if entry["result"] is None else entry["result"]["status"],
                       "verification_sha256":None if entry["result"] is None else entry["result"]["verification_sha256"]}
                 for stage,entry in record["stages"].items()} for key,record in state["constructors"].items()}


def _missing(value):
    return isinstance(value,StataMissingValue) or value is None or (isinstance(value,numbers.Real) and math.isnan(float(value)))


def _canonical_stata(raw, audit):
    require(list(raw.columns) == list(MAPPINGS["K01"]), "Stata selected columns differ")
    data = {}
    missing = {}
    for original, column in MAPPINGS["K01"].items():
        values, counts = [], {}
        for value in raw[original].tolist():
            if _missing(value):
                token = value.string if isinstance(value,StataMissingValue) else "native_NA"
                counts[token] = counts.get(token,0)+1
                values.append(np.nan if column != "sex" else None)
            elif column == "id":
                require(isinstance(value,str) and bool(value.strip()), "Invalid reference ID schema")
                values.append(value)
            elif column == "sex":
                require(isinstance(value,numbers.Real) and not isinstance(value,(bool,np.bool_)) and value in (1,2), "Unknown nonmissing Stata sex code")
                values.append("M" if value == 1 else "F")
            else:
                require(isinstance(value,numbers.Real) and not isinstance(value,(bool,np.bool_)), "Malformed Stata numerical schema")
                values.append(float(value))
        data[column] = values
        missing[column] = counts
    frame = pd.DataFrame(data)
    require(len(frame) == audit["file_dimensions"]["rows"], "Reference row count differs from schema identity")
    require(not frame["id"].isna().any() and frame["id"].is_unique, "Reference ID integrity differs")
    return frame, {"native_tagged_missing_counts":missing, "units":"glucose_mmol/L", "value_labels_used_as_measurements":False}


_NUMBER = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?\Z")


def _canonical_tsv(payload, audit):
    reader = csv.reader(io.StringIO(payload.decode("utf-8-sig")), delimiter="\t")
    header = next(reader,None)
    require(header == audit["columns"], "Reference TSV header differs")
    indexes = {key:header.index(key) for key in MAPPINGS["K02"]}
    data = {value:[] for value in MAPPINGS["K02"].values()}
    missing = {value:0 for value in data}
    for row in reader:
        require(len(row) == len(header), "Reference TSV row width differs")
        for original,column in MAPPINGS["K02"].items():
            value = row[indexes[original]]
            stripped = value.strip()
            if stripped in {"","NA"}:
                data[column].append(None if column in {"sex","id"} else np.nan)
                missing[column] += 1
            elif column == "id": data[column].append(value)
            elif column == "sex":
                require(stripped in {"F","M"}, "Unknown nonmissing TSV sex code")
                data[column].append(stripped)
            else:
                require(_NUMBER.fullmatch(stripped) is not None, "Malformed TSV numerical token")
                number = float(stripped)
                require(math.isfinite(number), "Nonfinite parsed TSV number")
                data[column].append(number)
    frame = pd.DataFrame(data)
    require(len(frame) == audit["rows_in_deposit"], "Reference row count differs from schema identity")
    require(not frame["id"].isna().any() and frame["id"].is_unique, "Reference ID integrity differs")
    return frame, {"recognized_missing_counts":missing, "units":"TC_HDL_already_mg/dL", "conversion_applied":False}


def _load_reference(case, binding):
    """Called only inside the gated, exclusively reserved evaluation invocation."""
    payload = Path(binding["path"]).read_bytes()
    require(len(payload) == binding["bytes"] and hashlib.sha256(payload).hexdigest() == binding["sha256"], "Reference bytes differ from pinned schema audit identity")
    if case == "K01":
        audit = read_json(SCALE/"admission_next/HAALSI_DATA_SCHEMA_AUDIT.json")
        with StataReader(io.BytesIO(payload),convert_categoricals=False,convert_missing=True) as reader:
            labels = reader.variable_labels()
            require(len(labels) == audit["file_dimensions"]["columns"], "Stata column count differs")
            for name in MAPPINGS[case]:
                require(labels.get(name) == audit["selected_field_metadata"][name]["variable_label"], "Stata variable metadata differs")
            require(reader.value_labels().get("SEX") == {1:"Male",2:"Female"}, "Stata sex legend differs")
            raw = reader.read(columns=list(MAPPINGS[case]))
        frame, preparation = _canonical_stata(raw,audit)
    else:
        audit = read_json(SCALE/"TURKANA_SCHEMA_AUDIT.json")
        frame, preparation = _canonical_tsv(payload,audit)
    return frame, {"input_sha256":binding["sha256"], "input_bytes":len(payload), "rows_loaded":len(frame),
                   "selected_raw_columns":list(MAPPINGS[case]), "preparation":preparation}


def _analyze(frame, case, role):
    relative = "case_k01/analysis/k01_analysis.py" if case == "K01" else "analysis/k02_analysis.py"
    return _module(case+"analysis",relative).analyze_frame(frame,role=role)


def _unavailable(case, reason):
    result = _analyze(pd.DataFrame(),case,"generated")
    result.update(status="unavailable",reason=reason)
    for endpoint in result["estimands"].values():
        endpoint.update(status="unavailable",estimate=None,reason=reason)
    return result


def _load_generated(case, entry, trial, verified_trial):
    cc = _controller()
    bridge, _, _ = cc._modules()
    state = bridge.preflight(entry["bundle"],entry["candidate"])
    destination = bridge._destination(state["root"],state["relative"])
    child = bridge._child_root(destination,trial["context_id"])
    task = bridge.read_json(child/"task.json")
    receipt = bridge.execution.verify_execution(child,trial["id"])
    path = child/f"executions/{trial['id']}/output/generated.csv"
    require(receipt["status"] == "success" and receipt["files"]["output/generated.csv"] == verified_trial["generated_table_sha256"], "Generated output identity differs")
    require(file_hash(child/f"executions/{trial['id']}/execution.json") == verified_trial["execution_sha256"], "Execution identity differs")
    frame = bridge.lifecycle.read_table(path,task,output=True)
    require(len(frame) == 5000, "Generated table must have all 5000 rows")
    guard = _module(case+"guard",f"case_{case.lower()}/implementation/generated_validity.py")
    if case == "K01": guard.validate_generated_context(frame,task,context_id=trial["context_id"])
    else: guard.validate_generated_release(frame,task)
    return _map_generated_units(frame,case,task,{
        "execution_receipt_sha256":verified_trial["execution_sha256"],
        "generated_csv_sha256":verified_trial["generated_table_sha256"],
        "target_task_sha256":file_hash(child/"task.json"),
        "analysis_spec_sha256":file_hash(SCALE/("analysis/K02_ANALYSIS_SPEC_v0.json" if case == "K02" else "case_k01/analysis/K01_ANALYSIS_SPEC_v1.json"))})


def _map_generated_units(frame,case,task,caller_binding):
    unit_receipt = None
    if case == "K02":
        units = _module("units","bridge_units/unit_conversion.py")
        before = read_json(SCALE/"case_k02/unit_mapping/INPUT_CONTRACT.json")
        after = read_json(SCALE/"case_k02/unit_mapping/OUTPUT_CONTRACT.json")
        manifest = read_json(SCALE/"case_k02/unit_mapping/APPROVED_MANIFEST.json")
        require(task["row_id"] == before["row_id"], "Unit row ID differs from target task")
        same([{k:c[k] for k in ("name","kind","role","unit")} for c in task["columns"]],
             [{k:c[k] for k in ("name","kind","role","unit")} for c in before["columns"]], "Unit input contract differs from actual target task")
        frame,unit_receipt = units.convert_frame(frame,manifest,input_contract=before,output_contract=after,
            expected_input_sha256=units.frame_digest(frame),caller_binding=caller_binding)
    return frame, unit_receipt


def _slot_plan(state):
    cc = _controller()
    result = []
    for case in CASES:
        for constructor in CONSTRUCTORS:
            record = state["constructors"][f"{case}:{constructor}"]
            for stage in ("initial","final"):
                alias = stage == "final" and record["decision"]["decision"] == "retain"
                origin = "initial" if alias else stage
                entry = record["stages"].get(origin)
                completion = None if entry is None else entry["result"]
                verified = None if completion is None else completion["verified"]
                trials = {} if verified is None else {x["trial_id"]:x for x in verified["bridge"]["trials"]}
                guards = {} if verified is None else {x["trial_id"]:x for x in verified["guards"]["trials"]}
                source_trials = {t["seed"]:t for t in cc.stage_trials(case,constructor,origin) if t["context_id"] == cc.TARGETS[case]}
                for seed in SEEDS:
                    trial = source_trials[seed]
                    actual,guard = trials.get(trial["id"]),guards.get(trial["id"])
                    usable = bool(actual and guard and actual["status"] == "success" and actual["generation_link_verified"] and guard["guard_status"] == "valid")
                    result.append({"case":case,"constructor":constructor,"stage":stage,"seed":seed,
                        "report_id":f"{case}_{constructor}_{stage}_target_{seed}", "alias_of":trial["id"] if alias else None,
                        "origin_trial":trial,"entry":entry,"verified_trial":actual,"usable":usable,
                        "stage_verified_success":bool(completion and completion["status"] == "success"),
                        "execution_disposition":"retained_alias" if alias else "verified_output" if usable else "failed_or_unrun"})
    require(len(result) == 72 and len({x["report_id"] for x in result}) == 72, "Fixed report inventory differs")
    return result


def compare(case, generated, reference):
    result = {}
    for key in IDS[case]:
        g,r = generated["estimands"][key],reference["estimands"][key]
        outcome = "glucose" if case == "K01" else "hdl_cholesterol" if key == IDS[case][0] else "total_cholesterol"
        denominator = 1.0 if key == "K02-LIPID-RESIDUAL" else reference["metric_denominators"].get(outcome,{}).get("sample_sd")
        point_valid = g["status"] == r["status"] == "computed"
        raw = float(g["estimate"]-r["estimate"]) if point_valid else None
        point_valid = bool(point_valid and math.isfinite(raw))
        valid = point_valid and isinstance(denominator,numbers.Real) and math.isfinite(denominator) and denominator > 0
        error = abs(raw)/denominator if valid else None
        valid = bool(valid and math.isfinite(error))
        result[key] = {"status":"computed" if valid else "unavailable", "generated_estimate":g["estimate"],
            "reference_estimate":r["estimate"], "unit":r["unit"], "signed_raw_discrepancy":raw if point_valid else None,
            "absolute_raw_discrepancy":abs(raw) if point_valid else None, "normalized_discrepancy":error if valid else None,
            "normalization":"absolute_correlation_difference" if key == "K02-LIPID-RESIDUAL" else "reference_outcome_sample_SD_ddof1",
            "reference_denominator":denominator, "direction_agrees":bool(np.sign(g["estimate"]) == np.sign(r["estimate"])) if point_valid else None,
            "passes":{str(margin):bool(valid and error <= margin) for margin in GRID}}
    return result


def summarize(slots, references):
    require(len(slots) == 72, "Cannot omit any initial/final slot")
    bundles, cases, anchors = {}, {}, {}
    for case in CASES:
        ref = references[case]
        zero = copy.deepcopy(ref)
        for endpoint in zero["estimands"].values():
            if endpoint["status"] == "computed": endpoint["estimate"] = 0.0
        anchor = compare(case,zero,ref)
        defined = all(x["status"] == "computed" for x in anchor.values())
        insufficient = defined and all(x["passes"]["0.1"] for x in anchor.values())
        anchors[case] = {"endpoints":anchor,"defined":defined,"insufficient_discrimination":insufficient,
                         "discriminating":defined and not insufficient}
        for stage in ("initial","final"):
            for constructor in CONSTRUCTORS:
                selected = [x for x in slots if (x["case"],x["stage"],x["constructor"]) == (case,stage,constructor)]
                require(len(selected) == 3 and {x["seed"] for x in selected} == set(SEEDS), "Bundle seed inventory differs")
                bundles[f"{case}:{constructor}:{stage}"] = {"case":case,"constructor":constructor,"stage":stage,
                    "passes":{str(m):all(row["stage_verified_success"] and all(row["comparison"][key]["passes"][str(m)] for key in IDS[case]) for row in selected) for m in GRID},
                    "whole_stage_verified_success":all(row["stage_verified_success"] for row in selected),
                    "failed_or_unavailable_seed_count":sum(any(row["comparison"][key]["status"] != "computed" for key in IDS[case]) for row in selected)}
            counts = {str(m):sum(bundles[f"{case}:{c}:{stage}"]["passes"][str(m)] for c in CONSTRUCTORS[:5]) for m in GRID}
            cases[f"{case}:{stage}"] = {"agent_denominator":5,"agent_pass_counts":counts,
                "reliability_pass":{str(m):counts[str(m)] >= 4 for m in GRID},
                "statistical_reference_pass":bundles[f"{case}:S01:{stage}"]["passes"]}
    paired = []
    lookup = {(x["case"],x["constructor"],x["stage"],x["seed"]):x for x in slots}
    for case in CASES:
        for constructor in CONSTRUCTORS:
            for seed in SEEDS:
                a,b = (lookup[(case,constructor,stage,seed)] for stage in ("initial","final"))
                endpoints = {}
                for key in IDS[case]:
                    left,right = a["comparison"][key],b["comparison"][key]
                    valid = left["status"] == right["status"] == "computed"
                    endpoints[key] = {"status":"computed" if valid else "unavailable",
                        "effect_change":right["generated_estimate"]-left["generated_estimate"] if valid else None,
                        "normalized_error_reduction":left["normalized_discrepancy"]-right["normalized_discrepancy"] if valid else None}
                paired.append({"case":case,"constructor":constructor,"seed":seed,"retained_alias":bool(b["alias_of"]),"endpoints":endpoints})
    positive = cases["K01:final"]["reliability_pass"]["0.1"] and anchors["K01"]["discriminating"]
    return {"bundles":bundles,"cases":cases,"zero_anchors":anchors,"initial_final_paired":paired,
        "working_resolution":0.1,"full_resolution_grid":list(GRID),
        "positive_wave_a_scientific_gate":positive,"k02_alone_cannot_enable_wave_b":True,"wave_b_execution_authorized":False,
        "inference_scope":"unweighted finite measured-sample comparisons; HC3 working sensitivity only; no survey, causal, transport or clinical-equivalence claim",
        "independent_units":"cases/studies and constructions, not synthetic rows or seeds"}


def _write(path, value):
    with Path(path).open("xb") as handle:
        handle.write(canonical(value)+b"\n")


def evaluate_revealed_campaign(ledger_path, manifest_path, reveal_receipt_sha256):
    """One fixed invocation; no construction, target feedback, selection or retry."""
    ledger,state,manifest,manifest_binding = _gate(ledger_path,manifest_path,reveal_receipt_sha256)
    verified_inventory = _verify_inventory(ledger,state)
    plans = _slot_plan(state)
    output = Path(manifest["output_directory"])
    output.mkdir(parents=True,exist_ok=False)
    intent = {"release_sha256":ledger.release_sha256,"reveal_receipt_sha256":reveal_receipt_sha256,
        "closed_inventory_sha256":state["wave_closed"]["closed_inventory_sha256"],"manifest":manifest_binding,
        "evaluator_sha256":file_hash(__file__),"fixed_target_report_slots":72}
    _write(output/"EVALUATION_INTENT.json",intent)
    try:
        references,provenance = {},{}
        for case in CASES:
            frame,provenance[case] = _load_reference(case,manifest["target_files"][case])
            references[case] = _analyze(frame,case,"reference")
        rows,cache = [],{}
        for plan in plans:
            case = plan["case"]
            identity = (case,plan["constructor"],plan["origin_trial"]["id"])
            unit_receipt,error_type = None,None
            if plan["usable"]:
                if identity not in cache:
                    try:
                        frame,unit_receipt = _load_generated(case,plan["entry"],plan["origin_trial"],plan["verified_trial"])
                        analysis = _analyze(frame,case,"generated")
                        # K02's old pure function filters reference-style rows; case guard
                        # precedes it, and this extra assertion prevents silent filtering.
                        require(analysis["selection"]["excluded_rows"] == 0,"Generated analysis attempted row exclusion")
                    except (OSError,ValueError,TypeError,KeyError,RuntimeError,OverflowError) as error:
                        error_type = type(error).__name__
                        analysis = _unavailable(case,"verified_output_analysis_failed")
                    cache[identity] = (analysis,unit_receipt,error_type)
                analysis,unit_receipt,error_type = copy.deepcopy(cache[identity])
            else:
                analysis = _unavailable(case,"execution_failed_or_unrun_no_fallback")
            row = {k:plan[k] for k in ("case","constructor","stage","seed","report_id","alias_of","execution_disposition","stage_verified_success")}
            row.update(analysis=analysis,comparison=compare(case,analysis,references[case]),unit_conversion_receipt=unit_receipt,
                       error_type=error_type,verified_trial=plan["verified_trial"])
            rows.append(row)
        aggregates = summarize(rows,references)
        report = {"schema_version":1,"kind":"wave_a_evaluation","intent":intent,
            "verified_candidate_inventory":verified_inventory,"reference_provenance":provenance,"references":references,
            "target_slots":rows,"aggregate":aggregates,"target_rows_or_ids_emitted":False,
            "pure_analysis_release_status_fields":"Historical labels retained unchanged; actual authorization is the evaluator intent/reveal binding"}
        public_rows = [{k:v for k,v in row.items() if k not in {"verified_trial","unit_conversion_receipt"}} for row in rows]
        public = {"schema_version":1,"kind":"wave_a_publishable_aggregates","references":references,
                  "target_slots":public_rows,"aggregate":aggregates,"target_rows_or_ids_emitted":False}
        _write(output/"FULL_EVALUATION.json",report)
        _write(output/"PUBLISHABLE_AGGREGATES.json",public)
        completion = {"status":"complete","intent_sha256":digest(intent),
            "files":{name:file_hash(output/name) for name in ("EVALUATION_INTENT.json","FULL_EVALUATION.json","PUBLISHABLE_AGGREGATES.json")}}
        _write(output/"EVALUATION_COMPLETION.json",completion)
        return completion
    except (OSError,ValueError,TypeError,KeyError,RuntimeError,OverflowError) as error:
        _write(output/"EVALUATION_FAILURE.json",{"status":"failed","error_type":type(error).__name__,
            "intent_sha256":digest(intent),"automatic_retry_allowed":False})
        raise EvaluationError("Evaluation failed; retained local failure receipt, no automatic retry") from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command",required=True)
    prepare = sub.add_parser("prepare-manifest",help="Metadata only; no reference read")
    prepare.add_argument("output_directory",type=Path)
    prepare.add_argument("manifest_path",type=Path)
    run = sub.add_parser("evaluate",help="Requires closed both-case campaign and exact reveal receipt")
    run.add_argument("ledger_path",type=Path)
    run.add_argument("manifest_path",type=Path)
    run.add_argument("reveal_receipt_sha256")
    args = parser.parse_args()
    if args.command == "prepare-manifest":
        _write(args.manifest_path,prepare_evaluation_manifest(args.output_directory))
    else:
        print(json.dumps(evaluate_revealed_campaign(args.ledger_path,args.manifest_path,args.reveal_receipt_sha256)))


if __name__ == "__main__":
    main()
