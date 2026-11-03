"""Audit closed source allocations only, without harness or generator imports.

Run once after all six source-version dispositions have closed:
  python -B independent_source_audit.py --output SOURCE_AUDIT.json
Output names are confined to this script's directory and must be new.
Only generated J/B/M CSVs are opened. No target/reference file is accessed.
The numerical tolerance concerns implementation agreement, not scientific fit.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import platform
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
RELEASE = HERE.parent / "RELEASE.json"
VERSIONS = tuple(f"{a}/{v}" for a in ("A01", "A02")
                 for v in ("initial", "self_review", "source_feedback"))
REQUIRED = {"J": ("Q_J_bmi", "Q_J_fpg"), "B": ("Q_B_pearson",),
            "M": ("Q_M_spearman",)}
ATOL = RTOL = 1e-10


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def json_file(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def verified_bytes(path, expected):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), f"Missing regular file: {path}")
    payload = path.read_bytes()
    require(hashlib.sha256(payload).hexdigest() == expected, f"Hash mismatch: {path}")
    return payload


def child(root, relative):
    root = Path(root).resolve()
    path = (root / relative).resolve()
    require(path.is_relative_to(root) and path != root, "Path escapes bound source root")
    return path


def average_ranks(values):
    """Independent exact-equality, one-based average ranks."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = np.empty(len(values), dtype=float)
    left = 0
    while left < len(order):
        right = left + 1
        while right < len(order) and values[order[right]] == values[order[left]]:
            right += 1
        ranks[order[left:right]] = ((left + 1) + right) / 2.0
        left = right
    return ranks


def pearson(x, y):
    require(len(x) == len(y) and len(x) >= 3, "At least three complete pairs required")
    require(np.isfinite(x).all() and np.isfinite(y).all(), "Nonfinite correlation input")
    # math.fsum provides an independent centered dot-product implementation.
    x_mean, y_mean = math.fsum(map(float, x)) / len(x), math.fsum(map(float, y)) / len(y)
    xc = [float(v) - x_mean for v in x]
    yc = [float(v) - y_mean for v in y]
    xx, yy = math.fsum(v*v for v in xc), math.fsum(v*v for v in yc)
    require(xx > 0 and yy > 0, "Constant correlation input")
    return math.fsum(a*b for a, b in zip(xc, yc)) / math.sqrt(xx*yy)


def parse_table(payload, expected_n):
    reader = csv.DictReader(io.StringIO(payload.decode("utf-8-sig"), newline=""), strict=True)
    cols = ("age", "female", "bmi", "glucose", "hba1c")
    require(reader.fieldnames is not None and len(reader.fieldnames) == 6
            and set(reader.fieldnames) == {"row_id", *cols}, "Unexpected source CSV schema")
    rows = list(reader)
    require(len(rows) == expected_n, "Source row count differs from allocation")
    require(all(None not in r and all(v is not None for v in r.values()) for r in rows),
            "Malformed source CSV row; no rows may be removed")
    identifiers = [r["row_id"] for r in rows]
    require(all(v.strip() for v in identifiers) and len(set(identifiers)) == len(rows),
            "Empty or duplicate source identifiers")
    arrays = {c: np.asarray([float(r[c]) for r in rows]) for c in cols}
    require(all(np.isfinite(v).all() for v in arrays.values()), "Nonfinite source value")
    require(set(arrays["female"]) <= {0, 1}, "Invalid generated binary gender")
    require(np.all(arrays["age"] == np.floor(arrays["age"])), "Noninteger age")
    return arrays


def recompute(arrays, declaration, check):
    mapped = dict(arrays)
    for alias in declaration["column_aliases"]:
        source, generated = alias["source_name"], alias["generated_name"]
        require(source not in mapped and generated in arrays, "Invalid declared native alias")
        mapped[source] = arrays[generated]
    operator, mapping = check["operator"], check["measurement_mapping"]
    require(operator is not None and check["source_relation"] is not None,
            "Qualified operator or source relation is unavailable")
    require(operator["missing_policy"] == "error" and operator["selection"] == [],
            "Audit requires the declared complete, unfiltered source table")
    require(check["source_relation"]["assumed_weights"] == "equal", "Non-equal weights")
    if mapping["kind"] == "hba1c_ngsp_to_ifcc":
        require(mapping["output_column"] not in mapped, "Mapping overwrites a column")
        require(mapping["ngsp_percent_per_ifcc"] != 0, "Zero conversion slope")
        mapped[mapping["output_column"]] = (
            mapped[mapping["input_column"]] - mapping["ngsp_percent_intercept"]
        ) / mapping["ngsp_percent_per_ifcc"]
    else:
        require(mapping == {"kind": "identity"}, "Unsupported measurement mapping")
    info = {"n_input": len(arrays["age"]), "n_used": len(arrays["age"]),
            "n_selected": len(arrays["age"]), "n_missing_dropped": 0,
            "unit": operator["unit"]}
    if operator["kind"] == "ols_coefficient":
        require(operator["include_intercept"] is True, "OLS intercept omitted")
        predictors = operator["predictors"]
        term = operator["term"]
        require(predictors == ["age", "gender_binary", term]
                and term in {"BMI", "FPG"}, "J must use separate age/gender-adjusted projections")
        require(operator["outcome"] == "HbA1c_IFCC"
                and mapping["kind"] == "hba1c_ngsp_to_ifcc", "J response is not mapped native IFCC")
        require(set(mapped["gender_binary"]) == {0, 1}, "Both binary gender categories required")
        response = mapped[operator["outcome"]]
        design = np.column_stack([np.ones(len(response)), *[mapped[p] for p in predictors]])
        require(len(response) >= 5 and np.isfinite(design).all()
                and np.isfinite(response).all(), "Invalid complete OLS design")
        coefficients, _, rank, _ = np.linalg.lstsq(design, response, rcond=None)
        require(rank == design.shape[1] and len(response) > rank, "Non-full-rank OLS design")
        value = float(coefficients[1 + predictors.index(term)])
        info.update(design_rank=int(rank), residual_degrees_of_freedom=int(len(response)-rank),
                    method="numpy.linalg.lstsq_with_intercept")
    else:
        x, y = mapped[operator["x"]], mapped[operator["y"]]
        if operator["kind"] == "spearman_correlation":
            require(np.isfinite(x).all() and np.isfinite(y).all(), "Nonfinite rank input")
            x, y = average_ranks(x), average_ranks(y)
            info["tie_method"] = "exact_numeric_equality_one_based_average_ranks"
        else:
            require(operator["kind"] == "correlation", "Unsupported correlation operator")
        value = pearson(x, y)
        info["method"] = "manual_centered_dot_product_with_math_fsum"
    require(math.isfinite(value), "Nonfinite independently calculated statistic")
    return {**info, "value": value}


def ledger_sources(release):
    ledger = Path(release["ledger_directory"])
    require(json_file(ledger / "release.json") == release, "Ledger release differs")
    require(release["review"]["approved_sha256"] == digest({k:v for k,v in release.items()
                                                           if k != "review"}), "Release approval mismatch")
    previous, states, bindings = digest(release), {k: {} for k in VERSIONS}, []
    for index, path in enumerate(sorted((ledger / "events").glob("*.json"))):
        event = json_file(path)
        require(path.name == f"{index:06d}.json" and event["sequence"] == index
                and event["previous_sha256"] == previous, "Broken ledger chain")
        require(event["event_sha256"] == digest({k:v for k,v in event.items()
                                                 if k != "event_sha256"}), "Changed ledger event")
        previous = event["event_sha256"]
        bindings.append({"path": str(path), "event_sha256": previous,
                         "file_sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        kind, payload = event["kind"], event["payload"]
        # Stop at the first scientific freeze: later target events are unnecessary.
        if kind == "scientific_freeze":
            break
        require(not kind.startswith("target") and kind not in {"authorization", "closed"},
                "Target phase appeared without a preceding scientific freeze")
        if kind in {"registered", "sources_intent", "sources_closed", "aborted", "decision"}:
            require(payload["key"] in states, "Unexpected version")
            require(kind not in states[payload["key"]], "Duplicate source-version disposition")
            states[payload["key"]][kind] = payload
    for key, state in states.items():
        require("sources_closed" in state or "aborted" in state
                or state.get("decision", {}).get("decision", {}).get("action") == "stop",
                f"Source version remains open: {key}; do not audit incomplete outputs")
    return states, bindings


def audit_slot(slot, report, release):
    require(slot["role"] == "source" and slot["context_id"] in REQUIRED, "Non-source slot refused")
    bundle = Path(slot["bundle"]).resolve()
    candidate = child(bundle, slot["candidate"])
    execution_dir = child(bundle, f"executions/{slot['run_id']}")
    receipt = json.loads(verified_bytes(execution_dir / "execution.json", slot["execution_sha256"]))
    require(receipt["run_id"] == slot["run_id"] and receipt["candidate"] == slot["candidate"]
            and receipt["status"] == "success" and receipt["generator_executed"] is True
            and receipt["route"] == "generator.py", "Receipt execution identity/status mismatch")
    require(receipt["limits"] == {**release["execution_limits"], "seed": slot["seed"]},
            "Receipt seed or limits mismatch")
    # Verify the complete source receipt inventory, without executing imported code.
    for name, expected in receipt["files"].items():
        if name != "output/generated.csv":
            verified_bytes(child(execution_dir, name), expected)
    require(receipt["files"]["output/generated.csv"] == slot["output_sha256"], "Receipt table mismatch")
    frozen = json.loads(verified_bytes(candidate / "freeze.json", receipt["candidate_freeze_sha256"]))
    for name, expected in frozen["commitments"].items():
        verified_bytes(child(bundle, name), expected)
    q = report["qualified_feedback"]
    if q is None:
        verified_bytes(execution_dir / "output/generated.csv", slot["output_sha256"])
        return [{"run_id": slot["run_id"], "check_id": check_id,
                 "independent_status": "unavailable_no_qualified_definition",
                 "collector_qualified_status": report.get("qualified_status"),
                 "collector_error": report.get("error"), "agrees": None}
                for check_id in REQUIRED[slot["context_id"]]]
    require(q["context_role"] == "source" and q["context_id"] == slot["context_id"]
            and q["run_id"] == slot["run_id"] and q["candidate"] == slot["candidate"]
            and q["output_link_verified"] is True, "Qualified report identity/link mismatch")
    bindings, declaration = q["bindings"], q["declaration"]
    require(declaration["context_role"] == "source" and declaration["context_id"] == slot["context_id"],
            "Declaration is not this source context")
    require(bindings["declaration_sha256"] == digest(declaration)
            and bindings["review_sha256"] == digest(q["review"])
            and q["review"]["approved_sha256"] == digest(declaration)
            and q["review"]["decision"] == "approved" and q["review"]["independent"] is True,
            "Qualified declaration/review commitment mismatch")
    paths = {"candidate_freeze_sha256": candidate / "freeze.json",
             "bridge_plan_sha256": candidate / "context_bridge_v1.json",
             "evidence_sha256": candidate / "evidence.json",
             "model_spec_sha256": candidate / "model_spec.json",
             "recipe_sha256": candidate / "whole_cohort_feedback.json",
             "semantics_sha256": candidate / "source_semantics_v1.json", "task_sha256": bundle / "task.json",
             "execution_receipt_sha256": execution_dir / "execution.json",
             "semantic_feedback_sha256": child(bundle, f"semantic_feedback_v1/{q['semantic_feedback_id']}/feedback.json")}
    for name, path in paths.items():
        verified_bytes(path, bindings[name])
    require(all(bindings[k] == v for k,v in declaration["bindings"].items()), "Declaration binding changed")
    require(bindings["generated_table_sha256"] == slot["output_sha256"], "Qualified table linkage mismatch")
    require(q["engine_sha256"]["qualified_relationships_v1.py"] == release["engine_sha256"]["revision/qualified_relationships_v1.py"]
            and q["engine_sha256"]["source_checks.py"] == release["engine_sha256"]["bridge/source_checks.py"],
            "Qualified collector engine commitment changed")
    payload = verified_bytes(execution_dir / "output/generated.csv", slot["output_sha256"])
    arrays = parse_table(payload, slot["n_rows"])
    evidence = {item["id"]: item for item in json_file(candidate / "evidence.json")["items"]}
    checks = {c["id"]: c for c in q["checks"]}
    declared = {c["id"]: c for c in declaration["checks"]}
    require(set(checks) == set(declared) == set(REQUIRED[slot["context_id"]]), "Qualified check coverage differs")
    results = []
    for check_id in REQUIRED[slot["context_id"]]:
        original, definition = checks[check_id], declared[check_id]
        require(all(original[k] == definition[k] for k in ("id", "evidence_id", "operator",
                "semantic_check_id", "source_relation", "measurement_mapping")), "Qualified definition changed")
        item = evidence[definition["evidence_id"]]
        require(item == original["reported_evidence"], "Qualified source evidence changed")
        strict = original["strict_result"]
        require(strict["status"] == "not_computable" and strict["calculation"] is None
                and strict["difference"] is None and original["exact_source_check_allowed"] is False,
                "Strict replay incorrectly promoted")
        result = {"run_id": slot["run_id"], "check_id": check_id,
                  "evidence_id": item["id"], "unit": item["unit"],
                  "operator": definition["operator"], "measurement_mapping": definition["measurement_mapping"],
                  "reported_source_point": item["estimate"], "collector_status": original["status"],
                  "collector_calculation": original["calculation"], "collector_raw_difference": original["raw_difference"],
                  "collector_unavailable_reason": original["unavailable_reason"]}
        try:
            independent = recompute(arrays, declaration, definition)
        except (ValueError, KeyError, np.linalg.LinAlgError) as error:
            result.update(independent_status="unavailable", independent_reason=str(error),
                          agrees=original["status"] == "unavailable" and original["calculation"] is None)
        else:
            difference = independent["value"] - item["estimate"]
            collector = original["calculation"]
            value_error = None if collector is None else independent["value"] - collector["value"]
            raw_error = None if original["raw_difference"] is None else difference - original["raw_difference"]
            agrees = (original["status"] == "available" and collector is not None
                      and all(independent[k] == collector[k] for k in ("n_input", "n_selected", "n_used", "n_missing_dropped", "unit"))
                      and math.isclose(independent["value"], collector["value"], abs_tol=ATOL, rel_tol=RTOL)
                      and math.isclose(difference, original["raw_difference"], abs_tol=ATOL, rel_tol=RTOL))
            result.update(independent_status="available", independent_calculation=independent,
                          independent_raw_difference=difference, value_error=value_error,
                          raw_difference_error=raw_error, agrees=agrees)
        results.append(result)
    # Verify immutable table bytes again after the arithmetic.
    verified_bytes(execution_dir / "output/generated.csv", slot["output_sha256"])
    return results


def run():
    release = json_file(RELEASE)
    states, events = ledger_sources(release)
    rows, comparisons, versions, errors = [], [], [], []
    for key in VERSIONS:
        state = states[key]
        if "sources_closed" not in state:
            disposition = state.get("aborted") or state["decision"]
            versions.append({"key": key, "status": "closed_without_source_execution", "disposition": disposition})
            a, v = key.split("/")
            for context, check_ids in REQUIRED.items():
                for seed in release["source_seeds"]:
                    run_id = f"{a}_{v}_{context}_{seed}"
                    rows.append({"run_id": run_id, "status": "not_run", "disposition": disposition})
                    comparisons.extend({"run_id": run_id, "check_id": check_id, "independent_status": "not_run",
                                        "agrees": None, "disposition": disposition} for check_id in check_ids)
            continue
        closed = state["sources_closed"]
        packet = closed["feedback"]
        require(digest(packet["packet"]) == packet["packet_sha256"] == closed["feedback_sha256"],
                f"Source feedback packet commitment mismatch: {key}")
        slots = closed["slots"]
        reports = {r["trial_id"]:r for r in packet["packet"]["reports"]}
        trials = {t["trial_id"]:t for t in closed["phase"]["trials"]}
        a, v = key.split("/")
        expected = {f"{a}_{v}_{c}_{s}" for c in REQUIRED for s in release["source_seeds"]}
        require(len(slots) == 9 and {s["run_id"] for s in slots} == expected, f"Source slot inventory changed: {key}")
        versions.append({"key": key, "status": closed["phase"]["status"],
                         "controller_eligibility": closed["eligibility"],
                         "feedback_sha256": closed["feedback_sha256"]})
        for slot in slots:
            require(slot["role"] == "source" and slot["context_id"] in REQUIRED
                    and slot["constructor"] == a and slot["version"] == v
                    and slot["seed"] in release["source_seeds"] and slot["n_rows"] == release["n_rows"],
                    "Source allocation metadata changed")
            row = dict(slot)
            if slot["status"] != "success":
                row["audit_status"] = "failed_or_unrun_disposition_preserved"
                comparisons.extend({"run_id":slot["run_id"], "check_id":check_id,
                                    "independent_status":"not_run", "agrees":None,
                                    "slot_status":slot["status"], "error":slot["error"]}
                                   for check_id in REQUIRED[slot["context_id"]])
            else:
                try:
                    trial = trials[slot["run_id"]]
                    require(trial["status"] == "success" and trial["generation_link_verified"] is True
                            and trial["execution_sha256"] == slot["execution_sha256"]
                            and trial["generated_table_sha256"] == slot["output_sha256"], "Phase trial linkage mismatch")
                    result = audit_slot(slot, reports[slot["run_id"]], release)
                    comparisons.extend(result)
                    row["audit_status"] = ("mismatch" if any(r["agrees"] is False for r in result)
                                           else "pass" if all(r["agrees"] is True for r in result)
                                           else "unavailable_disposition_preserved")
                except (ValueError, KeyError, OSError, TypeError) as error:
                    message = f"{slot['run_id']}: {type(error).__name__}: {error}"
                    errors.append(message)
                    row.update(audit_status="error", audit_error=message)
                    comparisons.extend({"run_id":slot["run_id"], "check_id":check_id,
                                        "independent_status":"audit_error", "agrees":False, "audit_error":message}
                                       for check_id in REQUIRED[slot["context_id"]])
            rows.append(row)
    require(len(rows) == 54 and len(comparisons) == 72, "Incomplete source comparison accounting")
    discrepancies = [abs(c["value_error"]) for c in comparisons if c.get("value_error") is not None]
    return {"schema_version":1, "kind":"independent_source_only_numerical_audit",
            "created_utc":datetime.now(timezone.utc).isoformat(),
            "status":"pass" if not errors and all(c["agrees"] is not False for c in comparisons) else "fail",
            "scope":"All closed J/B/M source allocations; no target/reference files, no generator execution",
            "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "release_sha256":hashlib.sha256(RELEASE.read_bytes()).hexdigest(),
            "runtime":{"python":platform.python_version(), "numpy":np.__version__},
            "arithmetic_tolerance":{"absolute":ATOL,"relative":RTOL,"meaning":"Implementation agreement only; no scientific fit threshold"},
            "source_slot_count":len(rows), "source_slot_status_counts":dict(Counter(r["status"] for r in rows)),
            "comparison_opportunities":len(comparisons),
            "independent_status_counts":dict(Counter(c["independent_status"] for c in comparisons)),
            "compared_available_count":len(discrepancies),
            "maximum_absolute_statistic_error":max(discrepancies, default=None),
            "hash_checked_event_prefix":events,"versions":versions,"source_slots":rows,
            "comparisons":comparisons,"errors":errors,
            "limitations":["Hashes are procedural commitments, not verified signatures.",
                           "Source point agreement does not establish target validity or reconstruct source participants.",
                           "Controller support eligibility is retained as metadata, not independently reestimated by this numerical audit."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="SOURCE_AUDIT.json")
    args = parser.parse_args()
    path = HERE / args.output
    require(Path(args.output).name == args.output and path.suffix == ".json", "Use a simple local JSON filename")
    require(not path.exists(), "Audit output already exists; it will not be overwritten")
    report = run()
    with path.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")
    print(json.dumps({k:report[k] for k in ("status", "source_slot_count", "comparison_opportunities",
                      "compared_available_count", "maximum_absolute_statistic_error", "errors")}))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
