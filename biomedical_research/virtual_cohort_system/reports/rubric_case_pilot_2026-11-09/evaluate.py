"""Postclosure aggregate evaluation of eighteen developmental pilot slots.

Imports do not load clinical references or private tables. The first operation
of evaluation is the all-slot closure gate. Only approved aggregate references
and sealed generated outputs are read; authored programs are never imported.
"""
from __future__ import annotations

import importlib.util
import json
import math
from numbers import Real
from pathlib import Path
from statistics import mean
import sys

sys.dont_write_bytecode = True
import runner

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
CASES = {"H": "ENSANUT2018", "L": "Turkana"}
PROVIDERS = {
    "ENSANUT2018": PROJECT / "work/main_study_freeze_2026-11-03/cases/ENSANUT2018/generated_feedback.py",
    "Turkana": PROJECT / "work/evidence_use_cross_task_2026-11-05/lipid_provider.py",
}
REFERENCE_LOCATIONS = {
    "ENSANUT2018": (PROJECT / "work/main_study_freeze_2026-11-03/final_evaluation/RESULTS.json", ["references", "ENSANUT2018"]),
    "Turkana": (PROJECT / "work/scaleup_2026-11-01/production_release/evaluation/PUBLISHABLE_AGGREGATES.json", ["references", "K02"]),
}
CATEGORIES = ("analyses", "diagnostics")
LIMITATIONS = [
    "Developmental construction-stage comparison using previously exposed clinical aggregate references; no fresh clinical confirmation.",
    "One fresh author per arm and case: arm differences are confounded with author/model variation.",
    "Three seeded tables are draws from one fixed authored law, not three independent author constructions.",
    "Continuous deviations and directions describe selected estimands and diagnostics; they do not establish recovery of individual rows or a unique joint distribution.",
    "No numerical superiority threshold, hypothesis test, efficacy pass/fail gate, or p-value is introduced.",
    "No source feedback or output-informed revision was supplied in this construction-stage pilot.",
    "Actual token use was not instrumented or enforced; this is not an exact compute-matched superiority test.",
    "Clinical references are reused aggregates. Missing reference diagnostics remain unavailable; no clinical rows or new clinical reference fits are used.",
]


def finite(value):
    return isinstance(value, Real) and not isinstance(value, bool) and math.isfinite(value)


def direction(value):
    return "positive" if value > 0 else "negative" if value < 0 else "zero"


def _sealed_local(name, lock):
    path = runner.safe_file(name)
    runner.require(lock["records"].get(name) == runner.sha(path), "Evaluation input is not sealed: " + name)
    return path


def endpoint_contract(lock):
    raw = runner.read(_sealed_local("ENDPOINT_CONTRACT.json", lock))
    schema = raw["cases"]
    runner.require(set(schema) == set(CASES.values()), "Wrong endpoint cases")
    for case, contract in schema.items():
        runner.require(set(contract) == set(CATEGORIES), "Unexpected endpoint categories: " + case)
        identifiers = []
        for category in CATEGORIES:
            runner.require(isinstance(contract[category], list) and bool(contract[category]), "Empty endpoint contract")
            for item in contract[category]:
                runner.require(set(item) == {"id", "unit"} and all(isinstance(item[key], str) for key in item),
                               "Invalid endpoint contract row")
                identifiers.append(item["id"])
        runner.require(len(set(identifiers)) == len(identifiers), "Duplicate planned endpoint")
        runner.require(len(contract["analyses"]) == 3, "Expected three requested analyses")
    return schema


def reference_bindings(lock):
    """Metadata reader; caller must have passed the closure gate first."""
    bindings = runner.read(_sealed_local("REFERENCE_BINDINGS.json", lock))
    runner.require(set(bindings) == set(CASES.values()), "Wrong clinical reference families")
    for case, record in bindings.items():
        expected_path, expected_selector = REFERENCE_LOCATIONS[case]
        path = Path(record["path"])
        runner.require(path.resolve() == expected_path.resolve() and record["selector"] == expected_selector,
                       "Reference is outside the approved aggregate allowlist")
        runner.require(not any(runner.lifecycle._link(p) for p in [path, *path.parents]), "Linked reference rejected")
        runner.require(path.is_file() and runner.sha(path) == record["sha256"], "Pinned aggregate reference changed")
    return bindings


def uncertainty_metadata(entry, *, missing_reason):
    """Retain supplied scalar CI/SE metadata; never derive one from the other."""
    raw = entry.get("interval")
    interval = {"status": "unavailable", "lower": None, "upper": None,
                "reason": missing_reason, "equivalence_margin": False}
    if isinstance(raw, dict):
        for key in ("direction", "meaning", "kind", "reason"):
            if key in raw:
                runner.require(raw[key] is None or isinstance(raw[key], str), "Invalid interval metadata")
                interval[key] = raw[key]
        for key in ("nominal_level", "normal_multiplier"):
            if key in raw:
                runner.require(raw[key] is None or finite(raw[key]), "Nonfinite interval metadata")
                interval[key] = float(raw[key]) if raw[key] is not None else None
        if "equivalence_margin" in raw:
            runner.require(raw["equivalence_margin"] is False, "Reference interval cannot become an equivalence margin")
        available = (finite(raw.get("lower")) and finite(raw.get("upper")) and
                     raw["lower"] <= raw["upper"] and raw.get("status", "available") in {"available", "computed"})
        if available:
            interval.update(status="available", lower=float(raw["lower"]), upper=float(raw["upper"]))
            if "reason" not in raw:
                interval["reason"] = None
    standard_error = {"status": "unavailable", "value": None, "reported_field": None,
                      "reason": missing_reason}
    candidates = [("standard_error", entry.get("standard_error")), ("se", entry.get("se"))]
    if isinstance(raw, dict):
        candidates.append(("interval.standard_error", raw.get("standard_error")))
    available_errors = [(field, value) for field, value in candidates if finite(value) and value >= 0]
    if available_errors:
        runner.require(all(value == available_errors[0][1] for _, value in available_errors), "Conflicting supplied standard errors")
        field, value = available_errors[0]
        standard_error.update(status="available", value=float(value), reported_field=field, reason=None)
    return {"interval": interval, "standard_error": standard_error,
            "interpretation": "Supplied estimator uncertainty only; no interval is inferred for another quantity"}


def _reference(unit, value, scope, entry=None):
    available = finite(value)
    return {"unit": unit, "value": float(value) if available else None,
            "status": "computed" if available else "unavailable", "scope": scope,
            "uncertainty": uncertainty_metadata(entry or {}, missing_reason="Not supplied for this endpoint in the pinned aggregate")}


def load_references(schema, lock):
    """Gate again so direct calls cannot read clinical payloads prematurely."""
    runner.closure_gate()
    bindings = reference_bindings(lock)
    references = {}
    for case, record in bindings.items():
        source = runner.read(Path(record["path"]))
        for key in record["selector"]:
            source = source[key]
        mapped = {}
        if case == "ENSANUT2018":
            for category in CATEGORIES:
                for item in schema[case][category]:
                    entry = source[item["id"]]
                    runner.require(entry["unit"] == item["unit"], "Glycemia reference unit mismatch")
                    mapped[item["id"]] = _reference(item["unit"], entry["value"],
                        "Previously exposed ENSANUT aggregate; identical published estimator definition", entry)
        else:
            for item in schema[case]["analyses"]:
                entry = source["estimands"][item["id"]]
                runner.require(entry["unit"] == item["unit"], "Lipid reference unit mismatch")
                mapped[item["id"]] = _reference(item["unit"], entry["estimate"],
                    "Previously exposed selected sample; identical K02 estimator", entry)
            for item in schema[case]["diagnostics"]:
                value = None
                for column in ("total_cholesterol", "hdl_cholesterol"):
                    if item["id"] == column + ".sd_sample":
                        value = source["metric_denominators"][column]["sample_sd"]
                mapped[item["id"]] = _reference(item["unit"], value,
                    "Existing sample ddof=1 SD" if finite(value) else
                    "Not present in pinned aggregate; generated diagnostic only")
        references[case] = mapped
    return references, bindings


def missing(contract, reason):
    return {category: [{**item, "status": "unavailable", "value": None, "reason": reason,
                       "generated_uncertainty": uncertainty_metadata({}, missing_reason="Generated endpoint unavailable")}
                      for item in contract[category]] for category in CATEGORIES}


def normalize_payload(payload, contract):
    """Whitelist only scalar endpoint summaries from the trusted providers."""
    runner.require(isinstance(payload, dict), "Provider payload must be an object")
    normalized = {}
    for category in CATEGORIES:
        expected = {item["id"]: item["unit"] for item in contract[category]}
        values = payload[category]
        runner.require(len(values) == len(expected) and {item["id"] for item in values} == set(expected),
                       "Endpoint coverage mismatch")
        lookup = {item["id"]: item for item in values}
        normalized[category] = []
        for planned in contract[category]:
            item = lookup[planned["id"]]
            runner.require(item["unit"] == planned["unit"], "Endpoint unit mismatch")
            computed = item["status"] == "computed" and finite(item["value"])
            unavailable = item["status"] == "unavailable" and item["value"] is None
            runner.require(computed or unavailable, "Invalid endpoint value/status")
            result = {**planned, "status": item["status"], "value": float(item["value"]) if computed else None,
                      "reason": None if computed else "Trusted provider could not compute this endpoint",
                      "generated_uncertainty": uncertainty_metadata(item,
                          missing_reason="Not supplied by the trusted generated-only provider")}
            for field in ("n", "rank"):
                if field in item:
                    runner.require(finite(item[field]) and float(item[field]).is_integer() and item[field] >= 0,
                                   "Invalid endpoint count/rank")
                    result[field] = int(item[field])
            normalized[category].append(result)
    return normalized


def aggregate_quality(payload):
    """Keep only bounded quality counts, never arbitrary provider contents."""
    quality = payload.get("quality", {})
    result = {}
    for key in ("duplicate_measurement_rows", "full_design_rank"):
        if key in quality:
            value = quality[key]
            runner.require(finite(value) and value >= 0 and float(value).is_integer(), "Invalid quality count")
            result[key] = int(value)
    if "status" in quality:
        runner.require(quality["status"] in {"passed", "failed"}, "Unexpected quality status")
        result["status"] = quality["status"]
    return result


def add_references(payload, references):
    result = {}
    for category in CATEGORIES:
        result[category] = []
        for item in payload[category]:
            reference = references[item["id"]]
            runner.require(item["unit"] == reference["unit"], "Comparison unit mismatch")
            comparable = item["status"] == "computed" and reference["status"] == "computed"
            difference = item["value"] - reference["value"] if comparable else None
            runner.require(difference is None or finite(difference), "Nonfinite comparison")
            result[category].append({**item, "reference": reference,
                "comparison_status": "computed" if comparable else "unavailable",
                "generated_direction": direction(item["value"]) if item["status"] == "computed" else None,
                "reference_direction": direction(reference["value"]) if reference["status"] == "computed" else None,
                "signed_difference": difference, "absolute_difference": abs(difference) if comparable else None})
    return result


def load_provider(case):
    # Fixed trusted module locations; no author-supplied import path is accepted.
    path = PROVIDERS[case]
    definition = importlib.util.spec_from_file_location("rubric_pilot_trusted_" + case, path)
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module


def analyze_slot(author, seed, closed, schema, references, protocol, providers):
    """Read one verified generated table only after the complete closure gate."""
    case = CASES[author[0]]
    slot = {"author_id": author, "case_id": case, "arm": author[1],
            "arm_description": protocol["arms"][author[1]], "seed": seed,
            "scheduled": True, "execution_status": "unavailable", "analysis_status": "unavailable",
            "generated_sha256": None, "execution_receipt_sha256": None, "quality": {}, "error_type": None}
    payload = missing(schema[case], "Scheduled output unavailable")
    try:
        receipt = runner.verify_execution(author, seed)
        run = runner.inventory()[(author, seed)]
        digest = runner.sha(run / "execution.json")
        committed = [item for item in closed["records"] if (item["author"], item["seed"]) == (author, seed)]
        runner.require(len(committed) == 1 and digest == committed[0]["execution_sha256"], "Receipt differs from closure")
        slot.update(execution_status=receipt["status"], execution_receipt_sha256=digest)
        if receipt["status"] != "success":
            # A generator's exception string could contain rows. Do not publish it.
            slot["error_type"] = "execution_" + receipt["status"]
            payload = missing(schema[case], "Execution " + receipt["status"] + "; local receipt retained")
        else:
            task = runner.task_contract(author)
            path = run / "output/generated.csv"
            runner.execution._csv_guard(path, task, runner.LIMITS["output_bytes"])
            frame = runner.lifecycle.read_table(path, task, output=True)
            runner.contracts.validate_output(None, frame, task)
            raw = providers[case].generated_statistics(frame)
            payload = normalize_payload(raw, schema[case])
            slot["quality"] = aggregate_quality(raw)
            slot["analysis_status"] = "complete" if all(item["status"] == "computed"
                for category in CATEGORIES for item in payload[category]) else "incomplete"
            slot["generated_sha256"] = receipt["generated_sha256"]
            slot["n"] = len(frame)
    except Exception as error:
        slot["error_type"] = type(error).__name__
        slot["analysis_status"] = "integrity_or_evaluation_failure"
        payload = missing(schema[case], "Integrity or generated-table evaluation failure; no endpoint omitted")
    slot.update(add_references(payload, references[case]))
    return slot


def summarize(slots, schema):
    """Seeds are nested in one construction. No cross-unit or superiority score."""
    summaries = []
    for author in runner.AUTHORS:
        chosen = [slot for slot in slots if slot["author_id"] == author]
        case = CASES[author[0]]
        runner.require(len(chosen) == len(runner.SEEDS), "Wrong scheduled construction slots")
        for category in CATEGORIES:
            for planned in schema[case][category]:
                values = [next(item for item in slot[category] if item["id"] == planned["id"]) for slot in chosen]
                available = [item for item in values if item["status"] == "computed"]
                comparable = [item for item in values if item["comparison_status"] == "computed"]
                summaries.append({"author_id": author, "case_id": case, "arm": author[1], "category": category,
                    **planned, "scheduled_seeds": len(runner.SEEDS), "available_generated_seeds": len(available),
                    "comparable_reference_seeds": len(comparable), "all_three_generated_complete": len(available) == 3,
                    "available_seed_mean": mean(item["value"] for item in available) if available else None,
                    "available_seed_range": [min(item["value"] for item in available), max(item["value"] for item in available)] if available else None,
                    "reference": values[0]["reference"],
                    "generated_uncertainty_by_seed": [{"seed": slot["seed"], "uncertainty": item["generated_uncertainty"]}
                                                       for slot, item in zip(chosen, values)],
                    "mean_signed_difference": mean(item["signed_difference"] for item in comparable) if comparable else None,
                    "mean_absolute_difference": mean(item["absolute_difference"] for item in comparable) if comparable else None,
                    "direction_agreement_count": sum(item["generated_direction"] == item["reference_direction"] for item in comparable),
                    "interpretation": "Available-seed description of one authored law; failures and unavailable endpoints retained separately"})
    return summaries


def _cell(value):
    if value is None:
        return "unavailable"
    if finite(value):
        return format(value, ".6g")
    return str(value).replace("|", "\\|").replace("\n", " ")


def _uncertainty_cell(uncertainty):
    interval, standard_error = uncertainty["interval"], uncertainty["standard_error"]
    text = ("[" + _cell(interval["lower"]) + ", " + _cell(interval["upper"]) + "]"
            if interval["status"] == "available" else "interval unavailable")
    text += "; SE " + (_cell(standard_error["value"]) if standard_error["status"] == "available" else "unavailable")
    description = interval.get("kind") or interval.get("meaning")
    return text + ("; " + description if description else "")


def markdown(report):
    lines = ["# Developmental rubric case pilot: aggregate evaluation", "",
             "All six authored programs were sealed before the eighteen scheduled draws. Each construction contributes three seeds. "
             "The reference aggregates were read only after the all-slot closure gate. No private rows are included.", "",
             f"Execution successes: {report['successful_executions']}/18. Complete endpoint sets: {report['complete_endpoint_slots']}/18.", "",
             "## Interpretation", ""]
    lines.extend("- " + item for item in report["limitations"])
    lines += ["", "Direction agreement is a descriptive sign count, not a success criterion. Deviations retain the endpoint's units. "
              "A mean uses available seeds and displays its denominator; an unavailable reference is never replaced by a new fit. "
              "Seed ranges are not confidence intervals. Supplied reference intervals retain their original meaning; unavailable CI/SE fields are explicit.", "",
              "## All scheduled slots", "",
              "| Author | Arm | Case | Seed | Execution | Endpoints | Error type |",
              "|---|---|---|---:|---|---|---|"]
    for slot in report["all_slots"]:
        lines.append("| " + " | ".join(_cell(slot[key]) for key in
            ("author_id", "arm", "case_id", "seed", "execution_status", "analysis_status", "error_type")) + " |")
    for category, title in (("analyses", "Requested analysis summaries"), ("diagnostics", "Prespecified diagnostic summaries")):
        lines += ["", "## " + title, "",
                  "| Author | Endpoint | Unit | Available/3 | Comparable/3 | Seed mean | Seed range | Reference | Mean signed deviation | Mean absolute deviation | Sign agreement |",
                  "|---|---|---|---:|---:|---:|---|---:|---:|---:|---|"]
        for item in report["construction_summaries"]:
            if item["category"] != category:
                continue
            span = item["available_seed_range"]
            cells = [item["author_id"], item["id"], item["unit"], item["available_generated_seeds"],
                     item["comparable_reference_seeds"], item["available_seed_mean"],
                     " to ".join(_cell(v) for v in span) if span else None, item["reference"]["value"],
                     item["mean_signed_difference"], item["mean_absolute_difference"],
                     str(item["direction_agreement_count"]) + "/" + str(item["comparable_reference_seeds"])]
            lines.append("| " + " | ".join(_cell(value) for value in cells) + " |")
    lines += ["", "## Supplied uncertainty for every endpoint", "",
              "Reference intervals below belong only to their named estimands. No mean, scale, correlation or coefficient interval is borrowed from another endpoint. "
              "Generated uncertainty is retained separately for each seed when the trusted provider supplies it.", "",
              "| Author | Category | Endpoint | Unit | Supplied reference uncertainty | Generated uncertainty by seed |",
              "|---|---|---|---|---|---|"]
    for item in report["construction_summaries"]:
        generated = "; ".join(str(row["seed"]) + ": " + _uncertainty_cell(row["uncertainty"])
                              for row in item["generated_uncertainty_by_seed"])
        cells = [item["author_id"], item["category"], item["id"], item["unit"],
                 _uncertainty_cell(item["reference"]["uncertainty"]), generated]
        lines.append("| " + " | ".join(_cell(value) for value in cells) + " |")
    lines += ["", "## Every scheduled endpoint by seed", "",
              "| Author | Seed | Category | Endpoint | Unit | Generated | Reference | Signed deviation | Absolute deviation | Direction | Status |",
              "|---|---:|---|---|---|---:|---:|---:|---:|---|---|"]
    for slot in report["all_slots"]:
        for category in CATEGORIES:
            for item in slot[category]:
                cells = [slot["author_id"], slot["seed"], category, item["id"], item["unit"], item["value"],
                         item["reference"]["value"], item["signed_difference"], item["absolute_difference"],
                         item["generated_direction"], item["status"] + "; reference comparison " + item["comparison_status"]]
                lines.append("| " + " | ".join(_cell(value) for value in cells) + " |")
    lines += ["", "Only aggregate outputs and provenance hashes are published. Execution receipts and generated rows remain local.", ""]
    return "\n".join(lines)


def evaluate():
    closed = runner.closure_gate()  # Must precede reference or evaluator table reads.
    protocol, lock = runner.verify_batch()
    runner.require(protocol["cases"] == CASES, "Unexpected case mapping")
    runner.require(set(protocol["arms"]) == {"A", "B", "C"}, "Unexpected arm mapping")
    schema = endpoint_contract(lock)
    outputs = [ROOT / name for name in ("EVALUATION.json", "EVALUATION.md", "EVALUATION_STARTED.json",
                                        "EVALUATION_COMPLETED.json", "EVALUATION_FAILURE.json")]
    runner.require(not any(path.exists() for path in outputs), "Evaluation already reserved; no silent rerun")
    runner.execution._write(ROOT / "EVALUATION_STARTED.json", {
        "created_utc": runner.now(), "batch_closure_sha256": runner.sha(ROOT / "BATCH_CLOSURE.json"),
        "evaluation_sha256": runner.sha(__file__), "scope": "postclosure aggregate-only evaluation"})
    try:
        references, bindings = load_references(schema, lock)
        providers = {case: load_provider(case) for case in CASES.values()}
        slots = [analyze_slot(author, seed, closed, schema, references, protocol, providers)
                 for author in runner.AUTHORS for seed in runner.SEEDS]
        runner.require(len(slots) == runner.MAX_TABLES, "Scheduled slot coverage differs")
        runner.closure_gate()
        reference_bindings(lock)  # Recheck reference hashes before publishing.
        report = {"schema_version": 1, "kind": "rubric_case_pilot_aggregate_evaluation_v1", "created_utc": runner.now(),
            "developmental": True, "previously_exposed_references": True,
            "new_patient_reads_or_clinical_reference_fits": False, "source_feedback_returned": False,
            "private_rows_published": False, "scheduled_authors": len(runner.AUTHORS),
            "authors_per_arm_per_case": 1, "seeds_per_authored_model": len(runner.SEEDS),
            "scheduled_slots": runner.MAX_TABLES, "physical_attempts": closed["physical_attempts"],
            "successful_executions": sum(slot["execution_status"] == "success" for slot in slots),
            "complete_endpoint_slots": sum(slot["analysis_status"] == "complete" for slot in slots),
            "protocol_sha256": runner.sha(ROOT / "PROTOCOL.json"), "batch_lock_sha256": runner.sha(ROOT / "BATCH_LOCK.json"),
            "batch_closure_sha256": runner.sha(ROOT / "BATCH_CLOSURE.json"), "evaluation_sha256": runner.sha(__file__),
            "endpoint_contract_sha256": runner.sha(ROOT / "ENDPOINT_CONTRACT.json"),
            "reference_sha256": {case: record["sha256"] for case, record in bindings.items()},
            "arms": protocol["arms"], "all_slots": slots, "construction_summaries": summarize(slots, schema),
            "comparison_definitions": {"signed_difference": "generated minus reference in the declared endpoint unit",
                "absolute_difference": "absolute generated-minus-reference deviation in the declared endpoint unit",
                "direction_agreement": "same sign among comparable seeds; descriptive, not a threshold or success rate",
                "aggregation": "Means/ranges within each authored model; availability denominators retained; no pooled score across units or cases"},
            "limitations": LIMITATIONS}
        text = markdown(report)
        runner.execution._write(ROOT / "EVALUATION.json", report)
        with (ROOT / "EVALUATION.md").open("x", encoding="utf8", newline="\n") as stream:
            stream.write(text)
        runner.execution._write(ROOT / "EVALUATION_COMPLETED.json", {
            "created_utc": runner.now(), "outputs": {name: runner.sha(ROOT / name) for name in ("EVALUATION.json", "EVALUATION.md")}})
        return {key: report[key] for key in ("scheduled_slots", "successful_executions", "complete_endpoint_slots", "private_rows_published")}
    except Exception as error:
        runner.execution._write(ROOT / "EVALUATION_FAILURE.json", {"created_utc": runner.now(),
            "error_type": type(error).__name__, "reason": "Evaluation stopped; no silent rerun. Inspect local state.",
            "private_rows_published": False})
        raise


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2, allow_nan=False))
