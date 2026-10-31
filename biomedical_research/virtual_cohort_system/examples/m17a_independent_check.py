"""Independent arithmetic for the M17-A artificial fixture, not patient validation.

Uses Python's standard library, not the harness statistical operators. The
adjusted x coefficient is computed from centered cross-products of x and group.
No code is generated, fitted for a biomedical use, or executed by this checker.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics


def inside(root, relative):
    path = (root / relative).resolve()
    path.relative_to(root)
    return path


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(bundle, feedback_id):
    root = Path(bundle).resolve()
    report_path = inside(root, f"whole_cohort_feedback/{feedback_id}/feedback.json")
    report = read(report_path)
    task = read(root / "task.json")
    if task["task_id"] != "m17a-artificial-whole-cohort" or task["mode"] != "whole_cohort":
        raise ValueError("This checker is specific to the invented M17-A fixture")
    if (root / "observed.csv").exists():
        raise ValueError("Unexpected observed individual input")
    candidate = inside(root, report["candidate"])
    execution = inside(root, f"executions/{report['run_id']}")
    if (execution / "input/observed.csv").exists():
        raise ValueError("Observed records were staged")
    receipt = read(execution / "execution.json")
    if receipt["status"] != "success" or receipt["candidate"] != report["candidate"]:
        raise ValueError("Execution is not successful or belongs to another candidate")
    if report["scientific_validity"] != "not_assessed" or report["source_context_validity"] != "not_certified":
        raise ValueError("Engineering report overstates scientific scope")
    table_path = execution / "output/generated.csv"
    bindings = {
        "task_sha256": root / "task.json",
        "candidate_freeze_sha256": candidate / "freeze.json",
        "recipe_sha256": candidate / "whole_cohort_feedback.json",
        "evidence_sha256": candidate / "evidence.json",
        "model_spec_sha256": candidate / "model_spec.json",
        "execution_receipt_sha256": execution / "execution.json",
        "generated_table_sha256": table_path,
    }
    if set(bindings) != set(report["bindings"]):
        raise ValueError("Unexpected binding set")
    for name, path in bindings.items():
        if digest(path) != report["bindings"][name]:
            raise ValueError(f"Independent hash mismatch: {name}")
    with table_path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["sample_id", "x", "group", "y"]:
            raise ValueError("Unexpected fixture columns")
        rows = list(reader)
    if len(rows) != task["n_rows"] or len({row["sample_id"] for row in rows}) != len(rows):
        raise ValueError("Row count or identifier uniqueness mismatch")
    x = [float(row["x"]) for row in rows]
    g = [float(row["group"]) for row in rows]
    y = [float(row["y"]) for row in rows]
    if not all(math.isfinite(v) for col in (x, g, y) for v in col) or not set(g) <= {0.0, 1.0}:
        raise ValueError("Invalid fixture values")
    mx, mg, my = map(statistics.mean, (x, g, y))
    dx, dg, dy = ([v - m for v in col] for col, m in ((x, mx), (g, mg), (y, my)))
    cross = lambda a, b: math.fsum(v * w for v, w in zip(a, b))
    sxx, sgg, sxg = cross(dx, dx), cross(dg, dg), cross(dx, dg)
    determinant = sxx * sgg - sxg * sxg
    if determinant <= 0:
        raise ValueError("Fixture adjusted regression is singular")
    slope = (cross(dx, dy) * sgg - cross(dg, dy) * sxg) / determinant
    values = {"x_mean": mx, "x_sd": statistics.stdev(x), "group_proportion": mg,
              "y_mean": my, "adjusted_slope": slope}
    source_values = {"x_mean": 0.0, "x_sd": 1.0, "group_proportion": 0.5,
                     "y_mean": 1.3, "adjusted_slope": 0.75}
    checks = {record["id"]: record for record in report["checks"]}
    if set(checks) != set(values) or len(report["checks"]) != len(values):
        raise ValueError("Unexpected or duplicated diagnostic set")
    discrepancies = {}
    max_stat, max_difference = 0.0, 0.0
    for key, value in values.items():
        record = checks[key]
        calculation = record["calculation"]
        if record["status"] != "approximate" or record["reported_value"] != source_values[key]:
            raise ValueError("Fixture diagnostic status or aggregate reference changed")
        counts = {k: calculation[k] for k in ("n_input", "n_selected", "n_used", "n_missing_dropped")}
        if counts != {"n_input": len(rows), "n_selected": len(rows), "n_used": len(rows), "n_missing_dropped": 0}:
            raise ValueError("Unexpected analysis row accounting")
        difference = value - source_values[key]
        if not math.isclose(value, calculation["value"], rel_tol=1e-12, abs_tol=1e-12):
            raise ValueError(f"Independent statistic differs: {key}")
        if not math.isclose(difference, record["difference"], rel_tol=1e-12, abs_tol=1e-12):
            raise ValueError(f"Independent discrepancy differs: {key}")
        max_stat = max(max_stat, abs(value - calculation["value"]))
        max_difference = max(max_difference, abs(difference - record["difference"]))
        discrepancies[key] = {"value": value, "source_expectation": source_values[key], "difference": difference}
    return {"status": "PASS", "scope": "Artificial-fixture arithmetic and declared bindings only; not biomedical accuracy or Agent quality.",
            "n_rows": len(rows), "n_statistics": len(values), "verified_binding_count": len(bindings),
            "no_observed_table": True, "no_staged_observed_table": True,
            "execution_route": receipt["route"], "generator_execution_recorded": receipt["generator_executed"],
            "max_absolute_statistic_difference": max_stat, "max_absolute_discrepancy_difference": max_difference,
            "feedback_sha256": digest(report_path), "checker_sha256": digest(Path(__file__)), "statistics": discrepancies}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--feedback-id", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = check(args.bundle, args.feedback_id)
    with Path(args.output).open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps(result, indent=2, allow_nan=False))
