"""Closed-author development evaluation using pinned reference aggregates only.

No patient-data reader, raw-data path or reference refitting is provided here.
"""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import platform
import sys
import numpy as np
import pandas as pd
import scipy
from generated_diagnostics import analyze_generated
from comparison_core import comparison, independently_check

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
P = ROOT.parents[1]
sys.path.insert(0, str(P))
from cohort_harness import execution, lifecycle
spec = importlib.util.spec_from_file_location("evidence_build_controller", ROOT / "run_session.py")
controller = importlib.util.module_from_spec(spec)
spec.loader.exec_module(controller)
SEEDS = [7401, 7402, 7403]


def read(path):
    return lifecycle.read_json(path)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    execution._write(Path(path), value)


def require(value, message):
    if not value:
        raise ValueError(message)


def inspect_closed_delivery(initial, final):
    """Validate frozen artifacts and the full attempt ledger without a reference read."""
    bundle, session = controller.setup("B")
    require(not (session / "controller_operation.lock").exists(), "Controller operation remains open")
    initial_receipt = lifecycle.verify_candidate(bundle, initial)
    final_receipt = lifecycle.verify_candidate(bundle, final)
    require(initial_receipt["revision_index"] == 0 and initial_receipt["parent"] is None,
            "Initial candidate is not an original construction")
    require(read(session / "initial_family.json") == controller.family(initial, bundle), "Initial family mismatch")
    require(read(session / "final_family.json") == controller.family(final, bundle), "Final family mismatch")
    decision = read(bundle / "FINAL_DECISION.json")
    choice = decision["choice"]
    require(decision["candidate"] == final and choice in {"retain", "revise"}, "Final decision mismatch")
    if choice == "retain":
        require(final == initial, "Retention must reuse the initial candidate")
    else:
        require(final != initial and final_receipt["revision_index"] == 1, "Expected one revision")
        require(final_receipt["parent"] == {"candidate": initial, "receipt_path": initial + "/freeze.json",
                "sha256": sha(bundle / initial / "freeze.json")}, "Revision parent mismatch")
    events = controller.inventory(bundle, session)
    reserved = {event["run_id"]: event for event in events}
    expected_ids = {"b_" + stage + "_" + str(seed)
                    for stage, seeds in controller.STAGES.items() for seed in seeds}
    require(set(reserved) <= expected_ids, "Unexpected physical attempt")
    for run_id, event in reserved.items():
        require(event["charged"] is True, "Uncharged physical attempt")
        stage = event["stage"]
        require(event["seed"] in controller.STAGES[stage] and
                run_id == "b_" + stage + "_" + str(event["seed"]), "Attempt schedule mismatch")
        expected_candidate = initial if stage.startswith("initial_") else final
        require(event["candidate"] == expected_candidate, "Attempt candidate mismatch")
        result_path = session / (run_id + "_result.json")
        require(result_path.exists(), "Unresolved reserved attempt")
        result = read(result_path)
        require(all(result[key] == event[key] for key in ("run_id", "seed", "stage", "candidate")),
                "Attempt/result binding mismatch")
        execution_path = bundle / "executions" / run_id / "execution.json"
        if execution_path.exists():
            receipt = execution.verify_execution(bundle, run_id)
            require(receipt["candidate"] == expected_candidate and receipt["limits"]["seed"] == event["seed"],
                    "Execution receipt disagrees with reserved attempt")
    controller.completed_stage(session, "initial_trial")
    initial_records = controller.completed_stage(session, "initial_delivery")
    initial_ids = [row["run_id"] for row in initial_records]
    if choice == "retain":
        require(not any(not event["stage"].startswith("initial_") for event in events),
                "Retained model has extra physical attempts")
        aliases = read(session / "final_delivery_aliases.json")["aliases"]
        require(len(aliases) == 3, "Retention must alias three deliveries")
        for seed, row, original in zip(SEEDS, aliases, initial_records):
            require(row["seed"] == seed and row["candidate"] == initial and row["run_id"] == original["run_id"]
                    and row["physical_execution"] is False and row["aliased_initial"] is True
                    and row["status"] == original["status"]
                    and row["initial_result_sha256"] == sha(session / (row["run_id"] + "_result.json")),
                    "Retention alias mismatch")
        final_ids = initial_ids
    else:
        final_ids = [row["run_id"] for row in controller.completed_stage(session, "final_delivery")]
    slots = []
    for stage, ids in (("initial", initial_ids), ("final", final_ids)):
        for seed, run_id in zip(SEEDS, ids):
            record = read(session / (run_id + "_result.json"))
            candidate = initial if stage == "initial" else final
            require(record["candidate"] == candidate and record["seed"] == seed, "Delivery mismatch")
            slot = {"request": "B", "stage": stage, "seed": seed, "run_id": run_id,
                    "candidate": candidate, "status": record["status"], "error": record.get("error"),
                    "execution_status": record.get("execution_status"),
                    "aliased_initial": stage == "final" and choice == "retain",
                    "table": None, "table_sha256": None, "execution_receipt_sha256": None}
            if record.get("execution_status") == "success" and record.get("execution_verified") is True:
                receipt = execution.verify_execution(bundle, run_id)
                require(receipt["status"] == "success" and receipt["candidate"] == candidate
                        and receipt["limits"]["seed"] == seed, "Successful execution binding mismatch")
                table = bundle / "executions" / run_id / "output/generated.csv"
                require(sha(table) == record["table_sha256"], "Generated table changed")
                slot.update(table=str(table), table_sha256=sha(table),
                            execution_receipt_sha256=sha(bundle / "executions" / run_id / "execution.json"))
            slots.append(slot)
    root_bindings = {path.relative_to(ROOT).as_posix(): sha(path) for path in sorted(session.glob("*.json"))}
    root_bindings["evaluation/CONTROL_MANIFEST.json"] = sha(HERE / "CONTROL_MANIFEST.json")
    bundle_bindings = {relative: sha(bundle / relative) for relative in
                       {initial + "/freeze.json", final + "/freeze.json", "FINAL_DECISION.json"}}
    for run_id in reserved:
        execution_path = bundle / "executions" / run_id / "execution.json"
        if execution_path.exists():
            bundle_bindings[execution_path.relative_to(bundle).as_posix()] = sha(execution_path)
    for slot in slots:
        if slot["table"] is not None:
            table = Path(slot["table"])
            bundle_bindings[table.relative_to(bundle).as_posix()] = slot["table_sha256"]
    inventory = {"reserved_attempts": len(events), "physical_delivery_attempts": len(set(initial_ids + final_ids)),
                 "successful_delivery_tables": len({slot["run_id"] for slot in slots if slot["table"] is not None}),
                 "choice": choice, "initial_freeze_sha256": sha(bundle / initial / "freeze.json"),
                 "final_freeze_sha256": sha(bundle / final / "freeze.json"),
                 "decision_sha256": sha(bundle / "FINAL_DECISION.json"),
                 "all_attempts": [read(session / (run_id + "_result.json")) for run_id in sorted(reserved)],
                 "artifact_bindings": {"run_files": root_bindings, "bundle_files": bundle_bindings}}
    return slots, inventory, {"initial": initial_ids, "final": final_ids}


def build_closure(initial, final, author_closed):
    require(author_closed is True, "Explicit author closure is required")
    _, inventory, deliveries = inspect_closed_delivery(initial, final)
    closure = {"kind": "closed_evidence_build_author", "created_utc": datetime.now(timezone.utc).isoformat(),
        "protocol_sha256": sha(ROOT / "PROTOCOL.json"), "requests": {"B": {
            "author_closed": True, "initial_candidate": initial, "final_candidate": final,
            "choice": inventory["choice"], "decision_file": "FINAL_DECISION.json",
            "decision_sha256": inventory["decision_sha256"], "delivery_runs": deliveries,
            "initial_freeze_sha256": inventory["initial_freeze_sha256"],
            "final_freeze_sha256": inventory["final_freeze_sha256"],
            "artifact_bindings": inventory["artifact_bindings"]}}}
    write(ROOT / "LIVE_CLOSURE.json", closure)
    return closure


def closure_gate(path):
    controller.verify_control_manifest()
    closure = read(path)
    require(closure["protocol_sha256"] == sha(ROOT / "PROTOCOL.json") and set(closure["requests"]) == {"B"},
            "Closure protocol/request mismatch")
    item = closure["requests"]["B"]
    require(item["author_closed"] is True and item["decision_file"] == "FINAL_DECISION.json", "Author not closed")
    slots, inventory, deliveries = inspect_closed_delivery(item["initial_candidate"], item["final_candidate"])
    require(item["delivery_runs"] == deliveries and item["decision_sha256"] == inventory["decision_sha256"]
            and item["choice"] == inventory["choice"], "Closure differs from final artifacts")
    require(item["initial_freeze_sha256"] == inventory["initial_freeze_sha256"]
            and item["final_freeze_sha256"] == inventory["final_freeze_sha256"]
            and item["artifact_bindings"] == inventory["artifact_bindings"],
            "Closed artifact digests changed")
    return slots, inventory


def seed_variation(slots):
    """Descriptive variation across all available scheduled draws; never pooled with reference CI."""
    result = {}
    for stage in ("initial", "final"):
        selected = [row for row in slots if row["stage"] == stage]
        result[stage] = {"scheduled_seeds": SEEDS,
                        "failed_or_unavailable": [row["seed"] for row in selected if row["analysis"] is None],
                        "retained_aliases": all(row["aliased_initial"] for row in selected), "analyses": {}}
        for analysis_name in ("primary", "descriptive_secondary"):
            analyses = [(row["seed"], row["analysis"] if analysis_name == "primary"
                         else row["analysis"]["descriptive_secondary"])
                        for row in selected if row["analysis"] is not None]
            valid = [(seed, analysis) for seed, analysis in analyses if analysis["status"] == "complete"]
            terms = ["bmi", "glucose", "age", "female"] if analysis_name == "primary" else ["bmi", "age", "female"]
            summary = {"interval_meaning": "Synthetic-seed variation conditional on one fixed model; not a confidence interval.",
                       "n_complete": len(valid), "unavailable_seeds": [seed for seed, analysis in analyses if analysis["status"] != "complete"],
                       "coefficients": {}}
            for term in terms:
                values = [analysis["coefficients"][term]["value"] for _, analysis in valid]
                summary["coefficients"][term] = {"per_seed": [{"seed": seed, "value": analysis["coefficients"][term]["value"]}
                    for seed, analysis in valid], "minimum": min(values) if values else None,
                    "maximum": max(values) if values else None,
                    "mean": float(np.mean(values)) if values else None,
                    "sample_sd": float(np.std(values, ddof=1)) if len(values) > 1 else None}
            result[stage]["analyses"][analysis_name] = summary
    return result


def render_results(report):
    lines = ["# Evidence-to-generation development comparison", "",
             "All scheduled initial and final deliveries are retained below. Reference intervals are reused community-cluster CR1-t intervals for an already-exposed selected sample. Synthetic intervals condition on the submitted model and draw. Seed ranges are Monte Carlo variation, not reference uncertainty or independent clinical replication.", "",
             f"Physical attempts: {report['inventory']['reserved_attempts']}; final choice: {report['inventory']['choice']}.", ""]
    for name, refkey in (("primary", "B"), ("descriptive_secondary", "A")):
        lines.extend(["## " + name.replace("_", " "), "", "| Term | Reference estimate [95% CI] | Initial seed range | Final seed range |", "|---|---:|---:|---:|"])
        for term in report["seed_variation"]["initial"]["analyses"][name]["coefficients"]:
            ref = report["reference"][refkey]["coefficients"][term]
            ranges = []
            for stage in ("initial", "final"):
                row = report["seed_variation"][stage]["analyses"][name]["coefficients"][term]
                ranges.append("unavailable" if row["minimum"] is None else f"{row['minimum']:.6g} to {row['maximum']:.6g}")
            ci = "unavailable" if ref["lower"] is None else f"{ref['lower']:.6g}, {ref['upper']:.6g}"
            lines.append(f"| {term} | {ref['value']:.6g} [{ci}] | {ranges[0]} | {ranges[1]} |")
        lines.append("")
    lines.extend(["## Delivery inventory", "", "| Stage | Seed | Run | Status | Initial alias |", "|---|---:|---|---|---|"])
    for slot in report["slots"]:
        lines.append(f"| {slot['stage']} | {slot['seed']} | {slot['run_id']} | {slot['status']} | {slot['aliased_initial']} |")
    lines.extend(["", "REPORT.json contains every intercept and nonintercept coefficient, conditional synthetic interval, distribution summary, correlation and raw difference for every delivery slot, including failures. No favorable-result filter or equivalence threshold is applied.", "",
                  "This comparison cannot identify an effect of evidence search, model revision or author choice. Agreement does not establish clinical validity, causal effects, transportability, or publication readiness. Separate reviewer recomputation is required before final delivery.", ""])
    with (HERE / "RESULTS.md").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write("\n".join(lines))


def run(closure_path):
    slots, inventory = closure_gate(closure_path)
    protocol = read(ROOT / "PROTOCOL.json")
    reference_path = P.joinpath(*lifecycle.safe_relative(protocol["reference"]["path"]))
    require(sha(reference_path) == protocol["reference"]["sha256"], "Pinned aggregate reference changed")
    receipt = {"kind": "postclosure_aggregate_reference_read", "created_utc": datetime.now(timezone.utc).isoformat(),
               "closure_sha256": sha(closure_path), "protocol_sha256": sha(ROOT / "PROTOCOL.json"),
               "reference_path": str(reference_path), "reference_sha256": sha(reference_path),
               "patient_rows_read": 0, "patient_data_decoded": False, "reference_refitted": False,
               "author_closed": True, "control_manifest_sha256": sha(HERE / "CONTROL_MANIFEST.json")}
    write(HERE / "REFERENCE_READ_RECEIPT.json", receipt)
    previous = read(reference_path)
    refs = {key: previous["reference"][key] for key in ("A", "B")}
    checks = []
    for slot in slots:
        table = slot.pop("table")
        slot.update(analysis=None, comparison=None)
        if table is not None:
            frame = pd.read_csv(table, dtype={"person_id": "string"}, float_precision="round_trip")
            require(len(frame) == protocol["n_rows"], "Generated row count mismatch")
            analysis = analyze_generated(frame, "B")
            checks.append({"run_id": slot["run_id"], "stage": slot["stage"],
                           "primary": independently_check(frame, analysis, "B"),
                           "descriptive_secondary": independently_check(frame, analysis["descriptive_secondary"], "A")})
            slot.update(analysis=analysis, comparison={"primary": comparison(refs["B"], analysis),
                "descriptive_secondary": comparison(refs["A"], analysis["descriptive_secondary"])})
    report = {"schema_version": 1, "kind": "closed_evidence_build_development_comparison",
        "protocol_sha256": sha(ROOT / "PROTOCOL.json"), "closure_sha256": sha(closure_path),
        "reference_provenance": receipt, "reference": refs, "inventory": inventory,
        "slots": slots, "seed_variation": seed_variation(slots), "internal_recomputation_checks": checks,
        "independent_reviewer_status": "pending_separate_review", "patient_rows_read": 0,
        "versions": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__, "scipy": scipy.__version__},
        "limitations": ["Previously exposed development reference; not fresh independent confirmation.",
            "Reference aggregate intervals are reused unchanged; no new patient decoding or refitting.",
            "Three synthetic draws measure conditional seed variation, not three clinical cohorts.",
            "Synthetic HC3-t intervals exclude source, structure and transport uncertainty.",
            "No equivalence claim, causal claim, favorable filtering or pooled success score.",
            "One author/model/evidence bundle cannot isolate the effect of evidence search or revision."]}
    write(HERE / "REPORT.json", report)
    render_results(report)
    return {"status": "complete", "slots": len(slots), "reserved_attempts": inventory["reserved_attempts"],
            "reference_rows_decoded": 0, "review": "pending_separate_review"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["close", "evaluate"])
    parser.add_argument("--initial")
    parser.add_argument("--final")
    parser.add_argument("--author-closed", action="store_true")
    parser.add_argument("--closure", type=Path, default=ROOT / "LIVE_CLOSURE.json")
    args = parser.parse_args()
    if args.action == "close":
        if not args.initial or not args.final:
            parser.error("close requires --initial and --final as candidates/NAME")
        result = build_closure(args.initial, args.final, args.author_closed)
    else:
        result = run(args.closure)
    print(json.dumps(result, indent=2, allow_nan=False))
