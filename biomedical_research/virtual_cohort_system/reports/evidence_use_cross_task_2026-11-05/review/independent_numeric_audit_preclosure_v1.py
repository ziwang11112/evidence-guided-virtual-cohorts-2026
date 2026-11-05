"""Independent postclosure audit; no provider, generator, evaluator, or patient imports.

Prepared before reference/result access. An explicit --postclosure-authorized flag
is required. Only final generated tables, immutable session commitments, already
exposed aggregate references, and evaluation outputs are read when executed.
Every invocation writes a new directory and retains all failures.
"""
from __future__ import annotations

import argparse
import bisect
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import traceback

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ATOL = 1e-9
RTOL = 1e-10
CATEGORIES = ("analyses", "diagnostics")
EPS = np.finfo(float).eps
H_COLUMNS = ("age", "female", "bmi", "glucose", "hba1c")
L_COLUMNS = ("age", "bmi", "total_cholesterol", "hdl_cholesterol")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, obj):
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(obj, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def close(left, right):
    return finite(left) and finite(right) and abs(left-right) <= ATOL + RTOL*abs(right)


def sign(value):
    return None if not finite(value) else ("positive" if value > 0 else "negative" if value < 0 else "zero")


def arithmetic_mean(values):
    return math.fsum(float(x) for x in values) / len(values)


def rms(values):
    return math.sqrt(arithmetic_mean([float(x)*float(x) for x in values]))


def std(values, ddof):
    mean = arithmetic_mean(values)
    return math.sqrt(math.fsum((float(x)-mean)**2 for x in values)/(len(values)-ddof))


def qr_fit(x, y):
    """Householder QR solution, independent of production SVD/pseudoinverse/lstsq."""
    singular = np.linalg.svd(x, compute_uv=False)
    rank = int(np.count_nonzero(singular > max(x.shape)*EPS*singular[0]))
    if rank != x.shape[1]:
        raise ValueError("rank_deficient_design")
    q, r = np.linalg.qr(x, mode="reduced")
    beta = np.linalg.solve(r, q.T @ y)
    residual = y-x @ beta
    require(np.isfinite(beta).all() and np.isfinite(residual).all(), "nonfinite_QR_arithmetic")
    return beta, residual, rank


def h_inverse_cdf(values, probability):
    """Equal-stratum 375-per-cell inverse CDF, retaining binary mass boundaries.

    All weights are exactly the same binary64 number, 1/(8*375). At each
    cumulative boundary math.fsum computes the accurately summed mass, replacing
    the production Neumaier loop. In particular this is not ceil(n*q)-1:
    a mathematically exact decile may fall just below its binary64 threshold.
    """
    ordered = sorted(float(x) for x in values)
    weight = 1.0/(8.0*375)
    total = math.fsum([weight]*len(ordered))
    threshold = probability*total
    low, high = 1, len(ordered)
    while low < high:
        middle = (low+high)//2
        if math.fsum([weight]*middle) >= threshold:
            high = middle
        else:
            low = middle+1
    return ordered[low-1]


def linear_quantile(values, probability):
    ordered = sorted(float(x) for x in values)
    index = (len(ordered)-1)*probability
    low = math.floor(index)
    high = math.ceil(index)
    return ordered[low] + (index-low)*(ordered[high]-ordered[low])


def load_generated(path, case):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        names = reader.fieldnames
        require(names is not None and len(names) == len(set(names)), "Duplicate/missing CSV header")
        expected = {"id", *H_COLUMNS} if case == "ENSANUT2018" else {"id", "sex", *L_COLUMNS}
        require(set(names) == expected, "Wrong generated CSV schema")
        rows = list(reader)
    require(len(rows) == 3000, "Wrong generated row count")
    require(all(row["id"] for row in rows) and len({row["id"] for row in rows}) == 3000,
            "Missing or duplicate generated identifier")
    columns = H_COLUMNS if case == "ENSANUT2018" else L_COLUMNS
    values = {name: np.asarray([float(row[name]) for row in rows], dtype=float) for name in columns}
    require(all(np.isfinite(value).all() for value in values.values()), "Nonfinite generated value")
    if case == "Turkana":
        values["sex"] = [row["sex"] for row in rows]
    return values


def reconstruct_h(data):
    age, female, bmi, glucose, hba1c = (data[key] for key in H_COLUMNS)
    require(np.all((age >= 25) & (age < 80) & (age == np.floor(age))), "Invalid H age")
    require(np.isin(female, [0, 1]).all(), "Invalid H sex")
    require(np.all(bmi > 0) and np.all(glucose > 0) and np.all(glucose < 126)
            and np.all(hba1c > 0), "Invalid H scientific value")
    groups = np.asarray([bisect.bisect_right([25, 40, 55, 70, 80], value)-1 for value in age])
    cell = 2*groups+female.astype(int)
    counts = [int(np.count_nonzero(cell == index)) for index in range(8)]
    require(counts == [375]*8, "H allocation differs from exact eight-by-375")
    # Fixed allocation makes the original WLS weights equal; QR OLS has the
    # same coefficients and RMS, without reproducing its sqrt-weight solver.
    x = np.column_stack((np.ones(len(age)), (age-50)/10, female, (bmi-25)/5, (glucose-100)/10))
    beta, residual, _ = qr_fit(x, hba1c)
    reduced, _, _ = qr_fit(x[:, :4], hba1c)
    glucose_beta, _, _ = qr_fit(x[:, [0, 1, 2, 4]], hba1c)
    output = {
        "Q1_age10": float(beta[1]), "Q2_bmi5": float(reduced[3]), "Q3_bmi5": float(beta[3]),
        "Q2_minus_Q3_bmi5": float(reduced[3]-beta[3]),
        "glucose10_age_sex": float(glucose_beta[3]), "q1_residual_rms": rms(residual),
    }
    for name in H_COLUMNS:
        output[name+".mean"] = arithmetic_mean(data[name])
        output[name+".sd_population"] = std(data[name], 0)
        for probability in (0.1, 0.5, 0.9):
            output[name+".q"+str(round(probability*100))] = h_inverse_cdf(data[name], probability)
    return output, {"demographic_cell_counts": counts, "full_design_rank": 5}


def reconstruct_l(data):
    age, bmi = data["age"], data["bmi"]
    require(np.all(age >= 18) and np.all(bmi > 0), "Lipid eligibility failed")
    require(set(data["sex"]) <= {"F", "M"}, "Invalid lipid sex")
    require(np.all(data["total_cholesterol"] > 0) and np.all(data["hdl_cholesterol"] > 0),
            "Nonpositive lipid")
    female = np.asarray([float(value == "F") for value in data["sex"]])
    converted = {key: data[key] * (38.67 if "cholesterol" in key else 1.0) for key in L_COLUMNS}
    x = np.column_stack((np.ones(len(age)), (age-50)/10, female, (bmi-25)/5))
    output = {}
    residuals = {}
    rank = int(np.linalg.matrix_rank(x))
    for name, key in (("total_cholesterol", "K02-TC-BMI"), ("hdl_cholesterol", "K02-HDL-BMI")):
        output[key] = None
        output[name+".conditional_rms"] = None
        if rank == 4:
            beta, residual, _ = qr_fit(x, converted[name])
            output[name+".conditional_rms"] = rms(residual)
            if float(np.max(converted[name])-np.min(converted[name])) != 0:
                output[key] = float(beta[3])
                norm = math.sqrt(math.fsum(float(value)**2 for value in residual))
                y_norm = math.sqrt(math.fsum(float(value)**2 for value in converted[name]))
                resolution = 16*EPS*max(x.shape)*max(y_norm, np.finfo(float).tiny)
                if math.isfinite(norm) and norm > resolution:
                    residuals[name] = residual
    output["K02-LIPID-RESIDUAL"] = None
    if len(residuals) == 2:
        left = residuals["total_cholesterol"]
        right = residuals["hdl_cholesterol"]
        left = left-arithmetic_mean(left)
        right = right-arithmetic_mean(right)
        numerator = math.fsum(float(a)*float(b) for a, b in zip(left, right))
        denominator = math.sqrt(math.fsum(float(a)**2 for a in left)*math.fsum(float(b)**2 for b in right))
        correlation = numerator/denominator
        if finite(correlation) and abs(correlation) <= 1+256*EPS:
            output["K02-LIPID-RESIDUAL"] = min(1.0, max(-1.0, correlation))
    for name in L_COLUMNS:
        output[name+".mean"] = arithmetic_mean(converted[name])
        output[name+".sd_sample"] = std(converted[name], 1)
        for probability in (0.1, 0.5, 0.9):
            output[name+".q"+str(round(probability*100))] = linear_quantile(converted[name], probability)
    output["sex.F_fraction"] = arithmetic_mean(female)
    return output, {"full_design_rank": rank}


def verify_closure(protocol):
    """Hash-and-ledger gate before any reference, results, or generated table read."""
    closure = read_json(ROOT/"BATCH_CLOSURE.json")
    require(closure["protocol_sha256"] == sha(ROOT/"PROTOCOL.json"), "Closure protocol hash mismatch")
    require(closure["control_sha256"] == sha(ROOT/"CONTROL.json"), "Closure control hash mismatch")
    require(set(closure["authors"]) == set(protocol["authors"]), "Closure author coverage mismatch")
    ledgers = {}
    total = 0
    for author, setting in protocol["authors"].items():
        folder = ROOT/"sessions"/author
        require(not (folder/"operation.lock").exists(), "Author session remains locked: "+author)
        actual = {f.relative_to(folder).as_posix(): sha(f) for f in sorted(folder.rglob("*")) if f.is_file()}
        require(actual == closure["authors"][author]["files"], "Closed session files changed: "+author)
        previous = sha(folder/"contract.json")
        events = []
        for index, path in enumerate(sorted((folder/"events").glob("*.json")), 1):
            event = read_json(path)
            require(path.name == f"{index:04d}.json" and event["index"] == index
                    and event["previous_sha256"] == previous, "Session hash chain broken: "+author)
            events.append(event)
            previous = sha(path)
        require(events and events[-1]["kind"] == "closed"
                and sum(event["kind"] == "closed" for event in events) == 1, "Session not terminally closed: "+author)
        attempts = [event for event in events if event["kind"] == "attempt"]
        require(len(attempts) <= 5 and len({event["run_id"] for event in attempts}) == len(attempts),
                "Attempt inventory invalid: "+author)
        total += len(attempts)
        bundle = Path(setting["bundle"])
        for event in events:
            if event["kind"] == "freeze":
                require(sha(bundle/event["candidate"]/"freeze.json") == event["freeze_sha256"],
                        "Candidate freeze receipt changed: "+author)
            for key in ("receipt", "table", "feedback", "decision", "review", "unverified_receipt"):
                if isinstance(event.get(key), dict) and "path" in event[key] and "sha256" in event[key]:
                    require(sha(event[key]["path"]) == event[key]["sha256"], "Bound "+key+" changed: "+author)
        ledgers[author] = events
    require(total == closure["physical_attempts"] and total <= protocol["max_physical_executions"],
            "Physical attempt total/budget mismatch")
    require(closure["scheduled_final_slots"] == 18 and closure["reference_read"] is False,
            "Unexpected closure schedule/reference state")
    return closure, ledgers


def reference_maps(protocol, contract):
    """Read only the two already-exposed cached aggregates after the closure gate."""
    output = {}
    for case, binding in protocol["references"].items():
        require(sha(binding["path"]) == binding["sha256"], "Cached aggregate reference hash changed")
        source = read_json(binding["path"])
        for key in binding["selector"]:
            source = source[key]
        if case == "ENSANUT2018":
            output[case] = source
            continue
        mapped = {}
        for endpoint in contract[case]["analyses"]:
            original = source["estimands"][endpoint["id"]]
            require(original["unit"] == endpoint["unit"], "Lipid reference analysis unit mismatch")
            mapped[endpoint["id"]] = {
                "unit": original["unit"], "value": original["estimate"], "status": original["status"],
                "interval": original["interval"], "scope": "Existing exposed selected sample; identical K02 estimator",
            }
        for endpoint in contract[case]["diagnostics"]:
            value = None
            if endpoint["id"] in {"total_cholesterol.sd_sample", "hdl_cholesterol.sd_sample"}:
                name = endpoint["id"].split(".")[0]
                value = source["metric_denominators"][name]["sample_sd"]
            mapped[endpoint["id"]] = {
                "unit": endpoint["unit"], "value": value, "status": "computed" if finite(value) else "unavailable",
                "scope": "Existing sample ddof=1 SD" if finite(value)
                else "Not present in pinned aggregate; generated diagnostic only",
            }
        output[case] = mapped
    return output


def run_audit(destination):
    protocol = read_json(ROOT/"PROTOCOL.json")
    contract = read_json(ROOT/"ENDPOINT_CONTRACT.json")["cases"]
    closure, ledgers = verify_closure(protocol)
    # No generated table, evaluated result, or reference aggregate is opened above.
    evaluation = ROOT/"evaluation"
    completed = read_json(evaluation/"EVALUATION_COMPLETED.json")
    for name, digest in completed["outputs"].items():
        require(sha(evaluation/name) == digest, "Completed evaluation output hash mismatch: "+name)
    report = read_json(evaluation/"RESULTS.json")
    references = reference_maps(protocol, contract)
    problems = []
    checks = []

    def check(condition, code, **context):
        if not condition:
            problems.append({"code": code, **context})
        return bool(condition)

    def equal_numeric(actual, expected, code, **context):
        ok = actual is None if expected is None else close(actual, expected)
        return check(ok, code, actual=actual, expected=expected, **context)

    check(report["protocol_sha256"] == sha(ROOT/"PROTOCOL.json"), "report_protocol_binding")
    check(report["batch_closure_sha256"] == sha(ROOT/"BATCH_CLOSURE.json"), "report_closure_binding")
    check(report["reference_sha256"] == {case: spec["sha256"] for case, spec in protocol["references"].items()},
          "report_reference_binding")
    for key, expected in (("scheduled_authors", 6), ("reference_families", 2),
                          ("scheduled_final_slots", 18), ("physical_attempts", closure["physical_attempts"]),
                          ("new_clinical_reads_or_fits", False), ("exposed_development", True)):
        check(report.get(key) == expected, "report_"+key, actual=report.get(key), expected=expected)
    slots = report["all_final_slots"]
    expected_slot_keys = {(author, seed) for author in protocol["authors"] for seed in protocol["final_seeds"]}
    actual_slot_keys = [(slot["author_id"], slot["seed"]) for slot in slots]
    check(len(actual_slot_keys) == 18 and set(actual_slot_keys) == expected_slot_keys,
          "all_18_slots_retained", actual=actual_slot_keys)
    by_slot = {(slot["author_id"], slot["seed"]): slot for slot in slots}
    independent = {}
    table_bindings = []
    computed = 0
    available_reference = 0
    for author, setting in protocol["authors"].items():
        case = setting["case_id"]
        events = ledgers[author]
        attempts = [event for event in events if event["kind"] == "attempt"]
        outcomes = [event for event in events if event["kind"] == "result"]
        for seed in protocol["final_seeds"]:
            context = {"author_id": author, "seed": seed, "case_id": case}
            slot = by_slot.get((author, seed))
            if slot is None:
                slot = {"analyses": [], "diagnostics": []}
            selected = [attempt for attempt in attempts if attempt["purpose"] == "final" and attempt["seed"] == seed]
            require(len(selected) <= 1, "Repeated scheduled final attempt")
            values = {endpoint["id"]: None for category in CATEGORIES for endpoint in contract[case][category]}
            expected_status = "not_attempted"
            expected_run = expected_candidate = expected_route = expected_seed_role = table_hash = None
            table_problem = None
            if selected:
                attempt = selected[0]
                matches = [result for result in outcomes if result["attempt_index"] == attempt["index"]]
                require(len(matches) == 1, "Unresolved final attempt")
                outcome = matches[0]
                expected_status = outcome["status"]
                expected_run, expected_candidate = attempt["run_id"], attempt["candidate"]
                expected_route, expected_seed_role = outcome.get("output_route"), outcome.get("seed_role")
                if expected_status == "success":
                    require(outcome.get("table") is not None, "Successful result lacks table binding")
                    table = outcome["table"]
                    table_hash = sha(table["path"])
                    require(table_hash == table["sha256"], "Generated table hash mismatch before reconstruction")
                    expected_path = Path(setting["bundle"])/"executions"/expected_run/"output/generated.csv"
                    require(Path(table["path"]).resolve() == expected_path.resolve(), "Unexpected final generated table path")
                    table_bindings.append(table)
                    try:
                        data = load_generated(table["path"], case)
                        values, quality = reconstruct_h(data) if case == "ENSANUT2018" else reconstruct_l(data)
                        check(slot.get("n") == 3000, "reported_generated_n", **context)
                        if case == "ENSANUT2018":
                            actual_counts = list(slot.get("quality", {}).get("demographic_cell_counts", {}).values())
                            check(actual_counts == quality["demographic_cell_counts"], "reported_H_cell_counts", **context)
                        else:
                            check(slot.get("quality", {}).get("full_design_rank") == quality["full_design_rank"],
                                  "reported_lipid_design_rank", **context)
                    except Exception as error:
                        table_problem = {"type": type(error).__name__, "message": str(error)}
                        check(False, "independent_reconstruction_failed", error=table_problem, **context)
            for field, expected in (("execution_status", expected_status), ("run_id", expected_run),
                                    ("candidate", expected_candidate), ("case_id", case), ("scheduled", True),
                                    ("output_route", expected_route), ("seed_role", expected_seed_role),
                                    ("table_sha256", table_hash)):
                check(slot.get(field) == expected, "slot_"+field, actual=slot.get(field), expected=expected, **context)
            independent[(author, seed)] = {"values": values, "table_sha256": table_hash,
                                          "output_route": expected_route, "execution_status": expected_status}
            for category in CATEGORIES:
                evaluated = slot.get(category, [])
                ids = [record["id"] for record in evaluated]
                specs = contract[case][category]
                check(len(ids) == len(specs) and set(ids) == {spec["id"] for spec in specs},
                      "endpoint_coverage", category=category, **context)
                index = {record["id"]: record for record in evaluated}
                for spec in specs:
                    endpoint = spec["id"]
                    row = index.get(endpoint, {})
                    expected = values.get(endpoint)
                    computed += int(expected is not None)
                    reference = references[case][endpoint]
                    available_reference += int(finite(reference["value"]))
                    detail = {**context, "category": category, "endpoint": endpoint}
                    check(row.get("unit") == spec["unit"], "endpoint_unit", **detail)
                    expected_row_status = "computed" if expected is not None else "unavailable"
                    check(row.get("status") == expected_row_status, "endpoint_status", **detail)
                    numeric_ok = equal_numeric(row.get("value"), expected, "generated_value", **detail)
                    check(row.get("reference") == reference, "reference_copy_or_mapping", **detail)
                    check(reference["unit"] == spec["unit"], "reference_unit", **detail)
                    comparison = expected is not None and finite(reference["value"])
                    signed = expected-reference["value"] if comparison else None
                    absolute = abs(signed) if signed is not None else None
                    equal_numeric(row.get("signed_difference"), signed, "signed_difference", **detail)
                    equal_numeric(row.get("absolute_difference"), absolute, "absolute_difference", **detail)
                    check(row.get("comparison_status") == ("computed" if comparison else "unavailable"),
                          "comparison_status", **detail)
                    check(row.get("generated_direction") == sign(expected), "generated_direction", **detail)
                    check(row.get("reference_direction") == sign(reference["value"]), "reference_direction", **detail)
                    checks.append({**detail, "unit": spec["unit"], "independent_value": expected,
                                   "evaluated_value": row.get("value"), "reference_value": reference["value"],
                                   "absolute_reconstruction_difference": abs(expected-row["value"])
                                   if finite(expected) and finite(row.get("value")) else None,
                                   "numeric_match": numeric_ok, "expected_status": expected_row_status,
                                   "signed_difference": signed, "absolute_difference": absolute})
    check(len(checks) == 513, "all_513_predeclared_outputs_retained", actual=len(checks))
    check(report["successful_final_executions"] == sum(slot["execution_status"] == "success" for slot in independent.values()),
          "successful_execution_count")
    check(report["unique_final_table_hashes"] == len({slot["table_sha256"] for slot in independent.values()
                                                      if slot["table_sha256"]}), "unique_table_count")

    summaries = report["all_author_endpoint_summaries"]
    summary_keys = [(record["author_id"], record["endpoint"]) for record in summaries]
    check(len(summary_keys) == 18 and len(set(summary_keys)) == 18, "all_author_summary_coverage")
    summary_index = {(record["author_id"], record["endpoint"]): record for record in summaries}
    for author, setting in protocol["authors"].items():
        case = setting["case_id"]
        for spec in contract[case]["analyses"]:
            endpoint = spec["id"]
            detail = {"author_id": author, "endpoint": endpoint}
            record = summary_index.get((author, endpoint), {})
            reference = references[case][endpoint]
            good = [independent[(author, seed)]["values"][endpoint] for seed in protocol["final_seeds"]
                    if finite(independent[(author, seed)]["values"][endpoint]) and finite(reference["value"])]
            check(record.get("reference") == reference, "summary_reference_copy", **detail)
            check(record.get("case_id") == case and record.get("unit") == spec["unit"], "summary_identity", **detail)
            check(record.get("available_slots") == len(good) and record.get("scheduled_slots") == 3,
                  "summary_slot_counts", **detail)
            equal_numeric(record.get("slot_mean"), arithmetic_mean(good) if good else None, "summary_mean", **detail)
            expected_range = [min(good), max(good)] if good else None
            if expected_range is None:
                check(record.get("slot_range") is None, "summary_range", **detail)
            else:
                value = record.get("slot_range")
                check(isinstance(value, list) and len(value) == 2 and all(close(a, b) for a, b in zip(value, expected_range)),
                      "summary_range", actual=value, expected=expected_range, **detail)
            absolute = [abs(value-reference["value"]) for value in good]
            equal_numeric(record.get("mean_absolute_reference_difference"), arithmetic_mean(absolute) if absolute else None,
                          "summary_absolute_difference", **detail)
            check(record.get("same_direction_slot_count") == sum(sign(value) == sign(reference["value"]) for value in good),
                  "summary_direction_count", **detail)
            independent_slots = [independent[(author, seed)] for seed in protocol["final_seeds"]]
            check(record.get("output_routes") == sorted({slot["output_route"] for slot in independent_slots if slot["output_route"]}),
                  "summary_output_routes", **detail)
            check(record.get("unique_validated_table_hashes") == len({slot["table_sha256"] for slot in independent_slots
                                                                     if slot["table_sha256"]}), "summary_unique_tables", **detail)

    with (evaluation/"ALL_ENDPOINTS.csv").open(encoding="utf-8-sig", newline="") as stream:
        csv_rows = list(csv.DictReader(stream))
    csv_keys = [(row["author_id"], int(row["seed"]), row["category"], row["endpoint"]) for row in csv_rows]
    expected_keys = {(row["author_id"], row["seed"], row["category"], row["endpoint"]) for row in checks}
    check(len(csv_keys) == 513 and len(set(csv_keys)) == 513 and set(csv_keys) == expected_keys, "CSV_all_endpoint_coverage")
    csv_index = dict(zip(csv_keys, csv_rows))
    for row in checks:
        key = (row["author_id"], row["seed"], row["category"], row["endpoint"])
        stored = csv_index.get(key, {})
        detail = {name: row[name] for name in ("author_id", "seed", "category", "endpoint")}
        for field, expected in (("generated_value", row["independent_value"]), ("reference_value", row["reference_value"]),
                                ("signed_difference", row["signed_difference"]), ("absolute_difference", row["absolute_difference"])):
            value = stored.get(field)
            actual = None if value in (None, "") else float(value)
            equal_numeric(actual, expected, "CSV_"+field, **detail)
        check(stored.get("case_id") == row["case_id"] and stored.get("unit") == row["unit"], "CSV_identity", **detail)

    # Detect any mutation while the audit was running.
    verify_closure(protocol)
    for binding in table_bindings + list(protocol["references"].values()):
        require(sha(binding["path"]) == binding["sha256"], "Bound input changed during audit")
    for name, digest in completed["outputs"].items():
        require(sha(evaluation/name) == digest, "Evaluation changed during audit")
    write_json(destination/"ALL_RECONSTRUCTED_ENDPOINTS.json", checks)
    with (destination/"ALL_RECONSTRUCTED_ENDPOINTS.csv").open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(checks[0]))
        writer.writeheader()
        writer.writerows(checks)
    result = {
        "schema_version": "independent_cross_task_numerical_audit_v1",
        "status": "passed" if not problems else "failed",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "script_sha256": sha(__file__), "plan_sha256": sha(ROOT/"review/NUMERICAL_AUDIT_PREDECLARATION.json"),
        "evaluation_sha256": sha(evaluation/"RESULTS.json"), "closure_sha256": sha(ROOT/"BATCH_CLOSURE.json"),
        "tolerance": {"absolute": ATOL, "relative": RTOL, "rule": "abs(actual-expected) <= absolute + relative*abs(expected)"},
        "scheduled_slots_checked": 18, "predeclared_outputs_checked": len(checks),
        "independently_computed_outputs": computed, "missing_outputs_retained": len(checks)-computed,
        "outputs_with_available_reference": available_reference,
        "author_endpoint_summaries_checked": 18,
        "largest_absolute_reconstruction_difference": max((row["absolute_reconstruction_difference"] or 0) for row in checks),
        "problem_count": len(problems), "problems": problems,
        "independence": {
            "numeric_solver": "Householder QR plus triangular solve; no production solver call",
            "table_parser": "stdlib csv.DictReader and float, independent of pandas read_csv",
            "H_weighting": "Exact 8x375 implies equal weights; inverse CDF uses accurate binary mass boundaries",
            "lipid_units_and_moments": "TC/HDL times 38.67; sample SD ddof=1; manual linear quantiles",
            "providers_generators_or_evaluator_imported": False, "generated_tables_regenerated": False,
            "participant_reference_records_read_or_refit": False, "cached_reference_aggregates_only": True,
        },
        "limitations": "Independent arithmetic verifies declared operators and serialization, not scientific validity, source transport, or target generalization.",
    }
    write_json(destination/"AUDIT_RESULT.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--postclosure-authorized", action="store_true")
    parser.add_argument("--output", type=Path, required=True, help="New audit directory under this pilot review directory")
    args = parser.parse_args()
    require(args.postclosure_authorized, "Explicit root postclosure release is required before execution")
    review = (ROOT/"review").resolve()
    destination = args.output.resolve()
    require(destination.is_relative_to(review) and destination != review, "Audit output must be a fresh child of review")
    destination.mkdir(parents=False, exist_ok=False)
    write_json(destination/"AUDIT_STARTED.json", {
        "created_utc": datetime.now(timezone.utc).isoformat(), "script_sha256": sha(__file__),
        "postclosure_authorized": True, "absolute_tolerance": ATOL, "relative_tolerance": RTOL,
    })
    try:
        result = run_audit(destination)
    except Exception as error:
        write_json(destination/"AUDIT_FAILURE.json", {
            "type": type(error).__name__, "message": str(error), "traceback": traceback.format_exc(),
            "no_silent_retry": True,
        })
        raise
    print(json.dumps({key: result[key] for key in ("status", "predeclared_outputs_checked",
          "independently_computed_outputs", "problem_count", "largest_absolute_reconstruction_difference")}, indent=2))
    raise SystemExit(0 if result["status"] == "passed" else 1)


if __name__ == "__main__":
    main()

