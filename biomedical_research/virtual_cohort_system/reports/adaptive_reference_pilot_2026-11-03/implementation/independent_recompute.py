"""Reviewer-only aggregate audit of this session's existing synthetic CSVs.

Never imports a candidate, the primary evaluator, or the cohort harness. Never
samples rows. Reads only the declared session, its aggregate definitions, and
its successful recorded synthetic output. A numeric agreement tolerance is a
software arithmetic check, not a scientific acceptance/equivalence margin.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import statistics

import numpy as np
import scipy
from scipy import linalg

REVIEW_ROOT = Path(__file__).resolve().parent.parent
ABS_TOL = 1e-10
REL_TOL = 1e-10


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    def pairs(values):
        out = {}
        for key, value in values:
            require(key not in out, "Duplicate JSON key: " + key)
            out[key] = value
        return out
    def nonfinite(value):
        raise ValueError("Nonfinite JSON constant: " + value)
    return json.loads(Path(path).read_text(encoding="utf-8-sig"),
                      object_pairs_hook=pairs, parse_constant=nonfinite)


def inside(root, relative):
    path = (root / relative).resolve()
    require(path.is_relative_to(root), "Path outside declared session: " + str(path))
    return path


def quantile(values, probability):
    values = sorted(values)
    position = (len(values) - 1) * probability
    left = math.floor(position)
    right = math.ceil(position)
    return values[left] + (position - left) * (values[right] - values[left])


def correlation(x, y):
    mx, my = statistics.fmean(x), statistics.fmean(y)
    xx, yy = [v - mx for v in x], [v - my for v in y]
    sxx = math.fsum(v * v for v in xx)
    syy = math.fsum(v * v for v in yy)
    if not sxx or not syy:
        return None
    return math.fsum(a * b for a, b in zip(xx, yy)) / math.sqrt(sxx * syy)


def average_ranks(values):
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and values[order[end]] == values[order[start]]:
            end += 1
        rank = (start + 1 + end) / 2
        for index in order[start:end]:
            ranks[index] = rank
        start = end
    return ranks


def qr_coefficient(columns, definition):
    require(definition["operator"] == "ols_coefficient" and definition["intercept"] is True
            and definition["weights"] == "none", "Unexpected declared regression")
    predictors = definition["predictors"]
    y = np.array(columns[definition["outcome"]], dtype=float)
    x = np.array([[1.0, *row] for row in zip(*(columns[k] for k in predictors))], dtype=float)
    q, r, pivot = linalg.qr(x, mode="economic", pivoting=True, check_finite=True)
    diagonal = np.abs(np.diag(r))
    tolerance = np.finfo(float).eps * max(x.shape) * diagonal.max()
    rank = int((diagonal > tolerance).sum())
    singular = linalg.svdvals(x)
    condition = float(singular[0] / singular[-1]) if singular[-1] else None
    value = None
    # Preserve the primary evaluator's explicitly declared glycemia quality gate.
    if rank == x.shape[1] and len(y) > rank and all(v > 0 for k in ("glucose", "hba1c") for v in columns[k]):
        coefficients = np.empty(x.shape[1])
        coefficients[pivot] = linalg.solve_triangular(r, q.T @ y, check_finite=True)
        value = float(coefficients[predictors.index(definition["term"]) + 1])
    return value, {"rank": rank, "n": len(y), "condition_number": condition,
                   "unit": definition["unit"], "outcome": definition["outcome"],
                   "term": definition["term"], "predictors": predictors}


def table(path, task):
    names = [c["name"] for c in task["columns"]]
    numeric = [c for c in task["columns"] if c["role"] == "generated"]
    values = {c["name"]: [] for c in numeric}
    row_ids = []
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = csv.DictReader(stream)
        require(rows.fieldnames == names, "CSV columns/order mismatch")
        for row in rows:
            require(None not in row and all(v is not None and v != "" for v in row.values()), "Malformed/missing CSV field")
            row_ids.append(row[task["row_id"]])
            for column in numeric:
                name = column["name"]
                value = float(row[name])
                require(math.isfinite(value), "Nonfinite output: " + name)
                if column["kind"] == "integer":
                    require(value.is_integer(), "Noninteger output: " + name)
                for key, valid in (("minimum", lambda bound: value >= bound), ("maximum", lambda bound: value <= bound)):
                    require(key not in column or valid(column[key]), "Output bound mismatch: " + name)
                values[name].append(value)
    require(len(row_ids) == task["n_rows"] == 3000, "Output row count differs from 3000")
    require(len(set(row_ids)) == len(row_ids), "Duplicate row identifiers")
    measurement_rows = list(zip(*(values[c["name"]] for c in numeric)))
    canonical = json.dumps(sorted(measurement_rows), separators=(",", ":"), allow_nan=False)
    return values, {"n": len(row_ids), "unique_ids": len(set(row_ids)),
                    "duplicate_measurement_rows": len(measurement_rows) - len(set(measurement_rows)),
                    "nonpositive_glycemia": {k: sum(v <= 0 for v in values[k]) for k in ("glucose", "hba1c")},
                    "measurement_multiset_sha256": hashlib.sha256(canonical.encode()).hexdigest()}


def calculate(values, definitions):
    result, fits = {}, {}
    for name, data in values.items():
        result.update({name + "_mean": statistics.fmean(data), name + "_sd": statistics.stdev(data),
                       name + "_q10": quantile(data, .1), name + "_median": quantile(data, .5),
                       name + "_q90": quantile(data, .9)})
    result["glucose_hba1c_pearson"] = correlation(values["glucose"], values["hba1c"])
    result["glucose_hba1c_spearman"] = correlation(average_ranks(values["glucose"]), average_ranks(values["hba1c"]))
    for definition in definitions["analyses"]:
        result[definition["id"]], fits[definition["id"]] = qr_coefficient(values, definition)
    return result, fits


def references(summary):
    out = {name + "_" + key: value for name, vals in summary["diagnostics"]["marginal"].items() for key, value in vals.items()}
    out.update({"glucose_hba1c_" + key: value for key, value in summary["diagnostics"]["joint"].items()})
    out.update({key: value["coefficient"] for key, value in summary["estimands"].items()})
    return out


def same_number(actual, expected):
    return actual is expected if actual is None or expected is None else math.isclose(actual, expected, rel_tol=REL_TOL, abs_tol=ABS_TOL)


def compare_feedback(independent, reference, primary, location):
    findings = []
    def check(label, actual, expected):
        if not same_number(actual, expected):
            findings.append({"location": location, "field": label, "recorded": actual, "recomputed": expected})
    evaluation = primary["reference_evaluation"]
    records = evaluation["diagnostics"] + evaluation["analyses"]
    require(len(records) == 30 and {r["id"] for r in records} == set(independent), "Primary feedback has incomplete/duplicate statistic IDs")
    for row in records:
        key = row["id"]
        check(key + ".value", row["value"], independent[key])
        check(key + ".reference", row["reference"], reference[key])
        check(key + ".difference", row["difference"], None if independent[key] is None else independent[key] - reference[key])
    strict = primary["semantic_feedback_v1"]
    require(strict is not None and len(strict["checks"]) == 30 and {r["id"] for r in strict["checks"]} == set(independent), "Missing v1 semantic feedback")
    for row in strict["checks"]:
        key = row["id"]
        check(key + ".semantic_reference", row["reported_value"], reference[key])
        # Semantics computes valid unweighted OLS even if a zero-glycemia quality
        # gate makes the separate reference evaluator withhold its coefficient.
        # Flag that scope difference explicitly rather than changing its value.
        value = row["calculation"]["value"] if row["calculation"] else None
        check(key + ".semantic_value", value, independent[key])
        check(key + ".semantic_difference", row["difference"], None if independent[key] is None else independent[key] - reference[key])
    return findings


def audit(root):
    root = Path(root).resolve()
    contract_path = root / "session/contract.json"
    contract = read(contract_path)
    require(Path(contract["root"]).resolve() == root, "Wrong session root")
    bundle = inside(root, contract["bundle"])
    task = read(bundle / "task.json")
    require(task["mode"] == "whole_cohort" and not (bundle / "observed.csv").exists(), "Unexpected participant input")
    require(sha(bundle / "task.json") == contract["task_sha256"], "Task hash changed")
    for source, binding in contract["bindings"].items():
        require(sha(source) == binding["sha256"] == sha(inside(root, binding["snapshot"])), "Frozen session binding changed: " + source)
    profile = read(contract["profile"])
    definitions, reference_summary = read(profile["analysis_definitions"]), read(profile["reference_summary"])
    reference = references(reference_summary)
    require(len(reference) == 30 and set(reference) == set(contract["diagnostic_ids"] + contract["analysis_ids"]), "Unexpected 30-statistic coverage")
    events, previous = [], sha(contract_path)
    for index, path in enumerate(sorted((root / "session/events").glob("*.json")), 1):
        event = read(path)
        require(path.name == f"{index:04d}.json" and event["index"] == index and event["previous_sha256"] == previous, "Broken event chain")
        events.append(event)
        previous = sha(path)
    attempts = [e for e in events if e["kind"] == "attempt"]
    require(len(attempts) <= 10, "More than ten table attempts")
    for phase in ("initial", "revision"):
        require(sum(e["phase"] == phase and e["purpose"] == "trial" for e in attempts) <= 2, "Phase trial budget exceeded")
    for stage in ("initial", "final"):
        seeds = [e["seed"] for e in attempts if e["purpose"] == "delivery" and e["stage"] == stage]
        require(len(seeds) == len(set(seeds)) and set(seeds) <= {3101, 3102, 3103}, "Duplicated/unapproved delivery slot")
    feedback = defaultdict(list)
    for event in events:
        if event["kind"] in ("feedback", "trial_feedback"):
            path = inside(root, event["feedback_path"])
            require(sha(path) == event["feedback_sha256"], "Feedback hash changed")
            report = read(path)
            for run in report["runs"] if event["kind"] == "feedback" else [report]:
                feedback[run["run_id"]].append((str(path), run))
    runs, findings = [], []
    for attempt in attempts:
        recorded = [e for e in events if e["kind"] == "result" and e["attempt_index"] == attempt["index"]]
        require(len(recorded) <= 1, "Multiple completion events for a reserved attempt")
        result = recorded[0] if recorded else {"status": "interrupted_or_pending", "execution_sha256": None}
        base = {key: attempt.get(key) for key in ("run_id", "seed", "candidate", "bundle", "purpose", "phase", "stage", "rows")}
        base["status"] = result["status"]
        require(attempt["rows"] <= 3000, "Oversized attempted output")
        if result["status"] != "success":
            if result["execution_sha256"] is not None:
                failed_receipt = inside(root, attempt["bundle"]) / "executions" / attempt["run_id"] / "execution.json"
                require(sha(failed_receipt) == result["execution_sha256"], "Failed receipt hash changed")
            base.update(error=result.get("error"), recomputation="unavailable_no_successful_table",
                        unavailable_statistics=sorted(reference), feedback_reports=[p for p, _ in feedback[attempt["run_id"]]])
            runs.append(base)
            continue
        run_bundle = inside(root, attempt["bundle"])
        run_dir = run_bundle / "executions" / attempt["run_id"]
        receipt_path = run_dir / "execution.json"
        require(sha(receipt_path) == result["execution_sha256"], "Execution receipt hash changed")
        receipt = read(receipt_path)
        require(receipt["status"] == "success" and receipt["generator_executed"] is True and receipt["isolation_scope"] == "generator_process_only", "Incorrect successful execution scope")
        require(receipt["candidate"] == attempt["candidate"] and receipt["limits"]["seed"] == attempt["seed"], "Attempt identity mismatch")
        require(receipt["candidate_freeze_sha256"] == attempt["freeze_sha256"] == sha(run_bundle / attempt["candidate"] / "freeze.json"), "Candidate freeze hash changed")
        output = run_dir / "output/generated.csv"
        require(sha(output) == receipt["files"]["output/generated.csv"], "Generated output hash changed")
        values, quality = table(output, read(run_bundle / "task.json"))
        numbers, fits = calculate(values, definitions)
        require(set(numbers) == set(reference), "Independent statistic coverage mismatch")
        comparisons = []
        for location, primary in feedback[attempt["run_id"]]:
            require(primary["generated_table_sha256"] == sha(output), "Feedback/output binding mismatch")
            strict_path = run_bundle / "semantic_feedback_v1" / ("session_" + attempt["run_id"]) / "feedback.json"
            require(sha(strict_path) == primary["semantic_feedback_sha256"] and read(strict_path) == primary["semantic_feedback_v1"], "Semantic feedback binding mismatch")
            discrepancies = compare_feedback(numbers, reference, primary, location)
            findings.extend(discrepancies)
            comparisons.append({"path": location, "n_compared": 30, "arithmetic_mismatches": discrepancies})
        base.update(output_sha256=sha(output), quality=quality, regression_fits=fits,
                    statistics=[{"id": key, "value": value, "reference": reference[key],
                                 "difference": None if value is None else value-reference[key]} for key, value in numbers.items()],
                    comparisons=comparisons, feedback_comparison_status="checked" if comparisons else "pending_primary_feedback")
        runs.append(base)
    repeated = {}
    for field in ("output_sha256", "measurement_multiset_sha256"):
        groups = defaultdict(list)
        for run in runs:
            value = run.get("output_sha256") if field == "output_sha256" else run.get("quality", {}).get(field)
            if value:
                groups[value].append(run["run_id"])
        repeated[field] = [{"sha256": digest, "run_ids": ids} for digest, ids in groups.items() if len(ids) > 1]
    paired = []
    initial = {r["seed"]: r for r in runs if r["stage"] == "initial" and r["status"] == "success"}
    final = {r["seed"]: r for r in runs if r["stage"] == "final" and r["status"] == "success"}
    for seed in sorted(set(initial) & set(final)):
        before, after = initial[seed], final[seed]
        old = {row["id"]: row["value"] for row in before["statistics"]}
        new = {row["id"]: row["value"] for row in after["statistics"]}
        paired.append({"seed": seed, "initial_run_id": before["run_id"], "final_run_id": after["run_id"],
                       "identical_output_bytes": before["output_sha256"] == after["output_sha256"],
                       "identical_measurement_multiset": before["quality"]["measurement_multiset_sha256"] == after["quality"]["measurement_multiset_sha256"],
                       "statistics": [{"id": key, "initial": old[key], "final": new[key], "reference": reference[key],
                                       "change": None if old[key] is None or new[key] is None else new[key]-old[key],
                                       "initial_absolute_discrepancy": None if old[key] is None else abs(old[key]-reference[key]),
                                       "final_absolute_discrepancy": None if new[key] is None else abs(new[key]-reference[key])}
                                      for key in sorted(reference)],
                       "interpretation": "Same prescribed seed; parameter/code changes may alter random-number use. Per-statistic discrepancies are not a scientific pass score."})
    status = "arithmetic_mismatch" if findings else ("pending_outputs_or_feedback" if not runs or any(not feedback[r["run_id"]] or r["status"] == "interrupted_or_pending" for r in runs) else "available_feedback_numerically_recomputed")
    return {"schema_version": 1, "kind": "independent_synthetic_aggregate_recomputation", "status": status,
            "created_utc": datetime.now(timezone.utc).isoformat(), "auditor_sha256": sha(__file__),
            "session_contract_sha256": sha(contract_path), "event_chain_tip_sha256": previous,
            "reference_sha256": sha(profile["reference_summary"]), "definitions_sha256": sha(profile["analysis_definitions"]),
            "runtime": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
            "software_comparison_tolerance": {"absolute": ABS_TOL, "relative": REL_TOL,
                "scope": "Arithmetic implementation agreement only; no scientific acceptance margin"},
            "attempt_counts": {"total": len(attempts), "trials": sum(e["purpose"] == "trial" for e in attempts),
                "delivery": sum(e["purpose"] == "delivery" for e in attempts), "statuses": dict(Counter(r["status"] for r in runs))},
            "runs": runs, "repeated_tables": repeated, "paired_delivery_comparisons": paired, "arithmetic_mismatches": findings,
            "limitations": ["All reference quantities were exposed construction inputs; discrepancies are not independent validation.",
                "This audit reads existing synthetic rows; it does not run or import a generator or inspect raw participant data.",
                "Attempt and output counts do not count internal generator random draws/calibration simulations.",
                "Repeated seeds or identical tables add no independent biomedical evidence.",
                "Known reference regression intervals are CR1_t over 218 groups; no source uncertainty is estimated from synthetic rows.",
                "No overall scientific score, post-hoc success margin, or target-population validity certificate is produced."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--output", help="New reviewer JSON file under the pilot review directory")
    args = parser.parse_args()
    result = audit(args.root)
    if args.output:
        path = Path(args.output).resolve()
        require(path.is_relative_to(REVIEW_ROOT), "Reviewer output must stay in pilot review directory")
        with path.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, indent=2, allow_nan=False)
            stream.write("\n")
        print(json.dumps({"status": result["status"], "path": str(path), "attempt_counts": result["attempt_counts"],
                          "arithmetic_mismatch_count": len(result["arithmetic_mismatches"])}))
    else:
        print(json.dumps(result, indent=2, allow_nan=False))
    return 1 if result["arithmetic_mismatches"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
