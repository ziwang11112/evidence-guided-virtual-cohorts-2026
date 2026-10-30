"""Task-local M15-A scoring only. This file never creates or repairs data values."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent.parent
sys.path.insert(0, str(PROJECT))
from cohort_harness.__main__ import validate_bundle
from cohort_harness.contracts import validate_output
from cohort_harness.execution import run_candidate, verify_execution
from cohort_harness.lifecycle import read_json, read_table, verify_candidate

BUNDLE = ROOT / "visible" / "bundle"
GROUPS = [("White", "male", 38), ("White", "female", 46),
          ("Black", "male", 19), ("Black", "female", 25)]
MOMENTS = [("age", "mean"), ("age", "sd"), ("bmi", "mean"),
           ("bmi", "sd"), ("urate", "mean")]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_new(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(obj, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def audit(event, **fields):
    path = ROOT / "private" / "controller_events.jsonl"
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps({"utc": datetime.now(timezone.utc).isoformat(),
                                 "event": event, **fields}, allow_nan=False) + "\n")


def verify_precommit():
    receipt = read_json(ROOT / "private" / "precommit.json")
    for relative, expected in receipt["files"].items():
        if sha(ROOT / relative) != expected:
            raise ValueError("Precommitted file changed: " + relative)
    for relative, expected in receipt["harness_files"].items():
        if sha(PROJECT / relative) != expected:
            raise ValueError("Harness implementation changed: " + relative)
    return sha(ROOT / "private" / "precommit.json")


def candidate_path(name):
    if name not in {"initial", "final"}:
        raise ValueError("Only initial and final candidates are permitted")
    return BUNDLE / "candidates" / name


def structural(name, require_frozen=True):
    directory = candidate_path(name)
    errors, frame, frozen = [], None, None
    try:
        result = validate_bundle(BUNDLE, directory)
        if result["route"] != "direct_rows":
            raise ValueError("Only literal direct_rows are permitted")
        task = read_json(BUNDLE / "task.json")
        frame = read_table(directory / "generated.csv", task)
        validate_output(None, frame, task)
        if not bool((frame["bmi"] > 0).all()):
            errors.append("BMI must be strictly positive")
        for race, sex, expected in GROUPS:
            count = int(((frame["race"] == race) & (frame["sex"] == sex)).sum())
            if count != expected:
                errors.append(f"Group count {race}/{sex}: {count}; required {expected}")
        if require_frozen:
            frozen = verify_candidate(BUNDLE, directory)
            if frozen["route"] != "generated.csv":
                errors.append("Frozen candidate must use generated.csv")
    except Exception as error:
        errors.append(type(error).__name__ + ": " + str(error))
    return frame, errors, frozen


def moments(frame):
    evidence = read_json(ROOT / "visible" / "templates" / "evidence.json")
    reported = {item["id"]: item["estimate"] for item in evidence["items"]}
    rows = []
    for race, sex, _ in GROUPS:
        group = frame.loc[(frame["race"] == race) & (frame["sex"] == sex)]
        key = race.lower() + "_" + sex
        for variable, statistic in MOMENTS:
            values = group[variable].to_numpy(dtype=float)
            observed = float(np.mean(values) if statistic == "mean" else np.std(values, ddof=1))
            reference = float(reported[f"U1_{key}_{variable}_{statistic}"])
            rows.append({"group": key, "variable": variable, "statistic": statistic,
                         "reported": reference, "observed": observed,
                         "absolute_error": abs(observed - reference),
                         "absolute_relative_error": abs(observed - reference) / abs(reference)})
    return rows


def moment_summary(rows):
    # All units are retained in per-item errors; each variable is also summarized separately.
    return {variable: {"n_moments": len(part),
                       "mean_absolute_error_in_variable_units": float(np.mean([x["absolute_error"] for x in part])),
                       "mean_absolute_relative_error": float(np.mean([x["absolute_relative_error"] for x in part]))}
            for variable in ("age", "bmi", "urate")
            for part in [[x for x in rows if x["variable"] == variable]]}


def validate_direct_execution(name, run_id):
    receipt = run_candidate(BUNDLE, candidate_path(name), run_id, 0, runtime=None)
    if receipt["status"] != "success":
        raise ValueError("Direct-row validation receipt failed: " + str(receipt.get("error")))
    if receipt["generator_executed"] is not False or receipt["runtime"] != {"backend": "direct_rows_validation"}:
        raise ValueError("Unexpected execution route")
    verify_execution(BUNDLE, run_id)
    return {"run_id": run_id, "generator_executed": False, "backend": "direct_rows_validation"}


def feedback():
    commitment = verify_precommit()
    budget = ROOT / "private" / "feedback_budget_consumed.json"
    write_new(budget, {"pass": 1, "maximum": 1, "candidate": "initial", "precommit_sha256": commitment,
                       "utc": datetime.now(timezone.utc).isoformat()})
    # The exclusive budget marker precedes calculation; a failure never silently resets it.
    frame, errors, frozen = structural("initial")
    rows = moments(frame) if frame is not None and not errors else []
    result = {"scope": "source_only_visible_feedback", "feedback_pass": 1,
              "maximum_feedback_passes": 1, "structural_errors": errors,
              "visible_moment_errors": rows, "separate_variable_summaries": moment_summary(rows) if rows else {},
              "definition": "absolute_relative_error = abs(observed-reported)/abs(reported); SD uses n-1",
              "interpretation": "Descriptive engineering discrepancies for fictional rows; no clinical inference.",
              "input_sha256": sha(candidate_path("initial") / "generated.csv") if (candidate_path("initial") / "generated.csv").is_file() else None,
              "freeze_sha256": sha(candidate_path("initial") / "freeze.json") if frozen else None}
    if not errors:
        result["direct_rows_validation"] = validate_direct_execution("initial", "initial_direct_validation")
    destination = ROOT / "visible" / "feedback" / "initial_feedback.json"
    write_new(destination, result)
    audit("feedback_complete", structural_errors=errors, numerical_moment_count=len(rows), output_sha256=sha(destination))
    print(json.dumps({"feedback": str(destination), "structural_errors": errors, "numerical_moment_count": len(rows)}))
    return 0 if not errors else 2


def ols(y, columns, names):
    matrix = np.column_stack(columns).astype(float)
    coefficients, _, rank, singular = np.linalg.lstsq(matrix, y, rcond=None)
    residual = y - matrix @ coefficients
    total = float(np.sum((y - np.mean(y)) ** 2))
    if int(rank) < matrix.shape[1]:
        return {"status": "not_identifiable", "rank": int(rank), "n_columns": matrix.shape[1]}
    return {"status": "computed", "coefficients": dict(zip(names, map(float, coefficients))),
            "n_rows": int(len(y)), "rank": int(rank), "residual_sum_squares": float(residual @ residual),
            "r_squared_descriptive": 1.0 - float(residual @ residual) / total if total > 0 else None,
            "condition_number": float(singular[0] / singular[-1])}


def exploratory(frame):
    y = frame["urate"].to_numpy(float)
    age = frame["age"].to_numpy(float)
    bmi = frame["bmi"].to_numpy(float)
    male = (frame["sex"] == "male").to_numpy(float)
    black = (frame["race"] == "Black").to_numpy(float)
    one = np.ones(len(frame))
    z = (bmi - 28.0) / 5.0
    results = {
        "interpretation": "Same-table exploratory descriptions; no external truth, p-values, sign success, or clinical confidence intervals.",
        "ols_main": ols(y, [one, age, bmi, male, black], ["intercept", "age", "bmi", "male", "Black"]),
        "ols_curvature": ols(y, [one, age, z, male, black, z*z], ["intercept", "age", "bmi_center28_scale5", "male", "Black", "bmi_center28_scale5_squared"]),
        "ols_sex_by_bmi": ols(y, [one, age, z, male, black, male*z], ["intercept", "age", "bmi_center28_scale5", "male", "Black", "male_by_bmi_center28_scale5"]),
        "within_sex_urate_quartiles": []}
    for sex in ("male", "female"):
        group = frame.loc[frame["sex"] == sex].copy()
        boundaries = np.quantile(group["urate"].to_numpy(float), [0.25, 0.5, 0.75], method="linear")
        bins = np.searchsorted(boundaries, group["urate"].to_numpy(float), side="left") + 1
        for q in (1, 2, 3, 4):
            part = group.loc[bins == q]
            results["within_sex_urate_quartiles"].append({"sex": sex, "quartile": q, "n": len(part),
                "linear_quantile_boundaries": list(map(float, boundaries)),
                "boundary_rule": "Q1 <= q25; Q2 q25 < x <= q50; Q3 q50 < x <= q75; Q4 > q75; ties stay together",
                "means": {v: float(part[v].mean()) if len(part) else None for v in ("age", "bmi", "urate")},
                "Black_fraction": float((part["race"] == "Black").mean()) if len(part) else None})
    return results


def evaluate():
    commitment = verify_precommit()
    feedback_path = ROOT / "visible" / "feedback" / "initial_feedback.json"
    feedback_report = read_json(feedback_path)
    if feedback_report["structural_errors"] or len(feedback_report["visible_moment_errors"]) != 20:
        raise ValueError("Initial valid frozen submission and its single 20-moment feedback are required")
    if not (ROOT / "private" / "feedback_budget_consumed.json").is_file():
        raise ValueError("Feedback budget receipt missing")
    frames, receipts = {}, {}
    for name in ("initial", "final"):
        frame, errors, frozen = structural(name)
        if errors:
            raise ValueError(name + ": " + "; ".join(errors))
        frames[name], receipts[name] = frame, frozen
    if receipts["initial"]["parent"] is not None or receipts["initial"]["revision_index"] != 0:
        raise ValueError("Initial candidate is not initial")
    if receipts["final"]["parent"]["candidate"] != "candidates/initial" or receipts["final"]["revision_index"] != 1:
        raise ValueError("Final candidate must be the sole child of initial")
    if feedback_report["input_sha256"] != sha(candidate_path("initial") / "generated.csv") or feedback_report["freeze_sha256"] != sha(candidate_path("initial") / "freeze.json"):
        raise ValueError("Feedback does not bind the frozen initial candidate")
    checks = read_json(candidate_path("final") / "checks.json")
    if not any(item["sha256"] == sha(feedback_path) and sha(candidate_path("final") / item["path"]) == sha(feedback_path) for item in checks["artifacts"]):
        raise ValueError("Final checks must bind an exact copy of actual initial feedback")
    execution = validate_direct_execution("final", "final_direct_validation")
    # Only here, after BOTH freezes and their lineage verify, open held-out values.
    hidden = read_json(ROOT / "private" / "heldout_urate_sd.json")
    result = {"scope": "SOURCE-ONLY", "precommit_sha256": commitment,
              "heldout_type": "same-source held-out summaries; not independent validation",
              "blinding": "Procedural only; parents know heldouts; pretraining recall cannot be excluded.",
              "clinical_inference": "None: 128 directly authored rows are not iid participant evidence.",
              "direct_rows_validation_final": execution, "candidates": {}}
    for name in ("initial", "final"):
        frame = frames[name]
        visible_rows = moments(frame)
        holdout_rows = []
        for row in hidden["groups"]:
            part = frame.loc[(frame["race"] == row["race"]) & (frame["sex"] == row["sex"]), "urate"]
            observed = float(part.std(ddof=1))
            reference = row["reported_urate_sd"]
            holdout_rows.append({"race": row["race"], "sex": row["sex"], "reported": reference,
                "observed": observed, "absolute_error": abs(observed-reference),
                "absolute_relative_error": abs(observed-reference)/abs(reference)})
        result["candidates"][name] = {"generated_csv_sha256": sha(candidate_path(name) / "generated.csv"),
            "freeze_sha256": sha(candidate_path(name) / "freeze.json"),
            "visible_moment_errors": visible_rows, "visible_separate_variable_summaries": moment_summary(visible_rows),
            "visible_joint_mean_absolute_relative_error_descriptive_only": float(np.mean([x["absolute_relative_error"] for x in visible_rows])),
            "heldout_urate_sd_errors": holdout_rows,
            "heldout_urate_sd_mean_absolute_relative_error": float(np.mean([x["absolute_relative_error"] for x in holdout_rows])),
            "exploratory": exploratory(frame)}
    before, after = frames["initial"], frames["final"]
    if set(before["sample_id"]) == set(after["sample_id"]):
        before = before.set_index("sample_id").sort_index()
        after = after.set_index("sample_id").sort_index()
        result["literal_changes"] = {"changed_cells_by_column": {col: int((before[col] != after[col]).sum()) for col in before.columns},
                                     "changed_rows": int((before != after).any(axis=1).sum())}
    else:
        result["literal_changes"] = {"status": "identifiers_changed; exact aligned cell change count unavailable"}
    destination = ROOT / "private" / "evaluation" / "final_report.json"
    write_new(destination, result)
    audit("final_evaluation_complete", output_sha256=sha(destination))
    print(json.dumps({"evaluation": str(destination), "status": "complete", "scope": "SOURCE-ONLY"}))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["feedback", "evaluate", "verify-precommit"])
    args = parser.parse_args()
    try:
        if args.command == "verify-precommit":
            print(json.dumps({"precommit_sha256": verify_precommit(), "status": "intact"}))
            return 0
        return feedback() if args.command == "feedback" else evaluate()
    except Exception as error:
        audit("command_failed", command=args.command, error_type=type(error).__name__, message=str(error))
        print(json.dumps({"status": "failed", "type": type(error).__name__, "message": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
