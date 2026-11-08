"""Evaluate all twelve sealed controlled tables; the only truth-reading entrypoint.

No p-value, CI overlap or pass/fail efficacy gate. Numerical error is descriptive;
this artificial same-population diagnostic is not evidence of clinical utility.
"""
from __future__ import annotations

import csv
import itertools
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import numpy as np
import pandas as pd

import runner
from cohort_harness import execution, source_checks
from cohort_harness.contracts import require

ROOT = Path(__file__).resolve().parent
MODELS = {"source_Z_X1": ["Z", "X1"], "source_Z_X2": ["Z", "X2"],
          "heldout_joint": ["Z", "X1", "X2"]}


def fit(frame, predictors):
    x = np.column_stack([np.ones(len(frame)), frame[predictors].to_numpy(dtype=float)])
    y = frame["Y"].to_numpy(dtype=float)
    rank = int(np.linalg.matrix_rank(x))
    require(rank == x.shape[1] and len(frame) > rank, "Regression has deficient rank/degrees of freedom")
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    residual = y - x @ beta
    residual_sd = float(np.sqrt(residual @ residual / (len(frame) - rank)))
    require(np.isfinite(beta).all() and np.isfinite(residual_sd), "Nonfinite regression diagnostic")
    return {"coefficients": dict(zip(["intercept", *predictors], map(float, beta))),
            "residual_sd": residual_sd, "residual_denominator": len(frame) - rank,
            "rank": rank, "n": len(frame)}


def truth_summary(truth):
    require(truth.get("columns") == runner.COLUMNS, "Truth column order differs")
    mean = np.asarray(truth["mean"], dtype=float)
    covariance = np.asarray(truth["covariance"], dtype=float)
    require(mean.shape == (4,) and covariance.shape == (4, 4) and
            np.isfinite(mean).all() and np.isfinite(covariance).all(), "Invalid finite truth moments")
    require(np.allclose(covariance, covariance.T, rtol=0, atol=1e-12), "Asymmetric truth covariance")
    eigen = np.linalg.eigvalsh(covariance)
    require(np.min(eigen) > 0, "Truth covariance must be positive definite")
    sd = np.sqrt(np.diag(covariance))
    models = {}
    for name, predictors in MODELS.items():
        indices = [runner.COLUMNS.index(x) for x in predictors]
        block = covariance[np.ix_(indices, indices)]
        cross = covariance[indices, 3]
        coefficients = np.linalg.solve(block, cross)
        residual_variance = float(covariance[3, 3] - cross @ coefficients)
        require(residual_variance > 0, "Truth residual variance not positive")
        models[name] = {"coefficients": {"intercept": float(mean[3] - mean[indices] @ coefficients),
                                       **dict(zip(predictors, map(float, coefficients)))},
                        "residual_sd": float(np.sqrt(residual_variance))}
    correlation = covariance / np.outer(sd, sd)
    return {"means": dict(zip(runner.COLUMNS, map(float, mean))),
            "sds": dict(zip(runner.COLUMNS, map(float, sd))),
            "covariance_eigenvalues": eigen.tolist(), "models": models,
            "predictor_correlations": {a + "__" + b: float(correlation[runner.COLUMNS.index(a), runner.COLUMNS.index(b)])
                                       for a, b in itertools.combinations(runner.COLUMNS[:3], 2)}}


def analyze(frame, source, truth):
    runner.validate_table(frame)
    covariance = np.cov(frame[runner.COLUMNS].to_numpy(dtype=float), rowvar=False, ddof=1)
    eigen = np.linalg.eigvalsh(covariance)
    failure = []
    if not np.isfinite(covariance).all() or not np.isfinite(eigen).all():
        failure.append("nonfinite_covariance")
    if np.min(eigen) <= 0:
        failure.append("nonpositive_sample_covariance_eigenvalue")
    means = {c: float(frame[c].mean()) for c in runner.COLUMNS}
    sds = {c: float(frame[c].std(ddof=1)) for c in runner.COLUMNS}
    source_report = runner.source_diagnostics(frame, source)
    models = {}
    for name, predictors in MODELS.items():
        try:
            fitted = fit(frame, predictors)
            true = truth["models"][name]
            signed = {term: float((fitted["coefficients"][term] - true["coefficients"][term]) *
                                 truth["sds"][term] / truth["sds"]["Y"]) for term in predictors}
            errors = {term: abs(value) for term, value in signed.items()}
            fitted["standardized_coefficient_signed_errors"] = signed
            fitted["standardized_coefficient_absolute_errors"] = errors
            fitted["mean_standardized_coefficient_absolute_error"] = float(np.mean(list(errors.values())))
            fitted["abs_log_residual_sd_ratio"] = (float(abs(np.log(fitted["residual_sd"] / true["residual_sd"])))
                                                  if fitted["residual_sd"] > 0 else None)
            fitted["log_residual_sd_ratio"] = (float(np.log(fitted["residual_sd"] / true["residual_sd"]))
                                              if fitted["residual_sd"] > 0 else None)
            if fitted["residual_sd"] <= 0:
                failure.append(name + ":zero_residual_sd")
            models[name] = {"status": "computed", **fitted}
        except (ValueError, np.linalg.LinAlgError) as error:
            models[name] = {"status": "not_computable", "reason": str(error)}
            failure.append(name + ":rank_or_finite_failure")
    corr = {}
    for a, b in itertools.combinations(runner.COLUMNS[:3], 2):
        operator = {"kind": "correlation", "x": a, "y": b, "unit": "1",
                    "selection": [], "missing_policy": "error"}
        runner.validate_operator(operator, source["units"])
        try:
            value = source_checks.apply_operator(frame, operator)["value"]
            corr[a + "__" + b] = {"value": value, "absolute_truth_error": abs(value - truth["predictor_correlations"][a + "__" + b])}
        except source_checks.NotComputable as error:
            corr[a + "__" + b] = {"value": None, "reason": str(error)}
            failure.append(a + "__" + b + ":correlation_not_computable")
    marginal = {}
    for column in runner.COLUMNS:
        marginal[column] = {"mean": means[column], "sd": sds[column], "variance": sds[column] ** 2,
                            "standardized_mean_absolute_error": abs(means[column] - truth["means"][column]) / truth["sds"][column],
                            "log_sd_ratio": float(np.log(sds[column] / truth["sds"][column])) if sds[column] > 0 else None,
                            "abs_log_sd_ratio": float(abs(np.log(sds[column] / truth["sds"][column]))) if sds[column] > 0 else None}
        if sds[column] <= 0:
            failure.append(column + ":zero_sd")
    return {"status": "evaluated", "rows": len(frame), "failure_flags": failure,
            "sample_covariance": covariance.tolist(), "sample_covariance_eigenvalues": eigen.tolist(),
            "marginals": marginal, "source_checks": source_report,
            "models": models, "predictor_correlations": corr}


def flatten(records):
    rows = []
    def emit(author, seed, section, metric, value=None, error=None, status="computed", signed_error=None):
        rows.append({"author": author, "seed": seed, "section": section, "metric": metric,
                     "value": value, "error": error, "signed_error": signed_error, "status": status})
    for record in records:
        author, seed = record["author"], record["seed"]
        emit(author, seed, "execution", "status", status=record["status"])
        if record["status"] != "evaluated":
            continue
        for name, item in record["marginals"].items():
            emit(author, seed, "marginal_mean", name, item["mean"], item["standardized_mean_absolute_error"])
            emit(author, seed, "marginal_sd", name, item["sd"], item["abs_log_sd_ratio"], signed_error=item["log_sd_ratio"])
            emit(author, seed, "marginal_variance", name, item["variance"])
        for check in record["source_checks"]["checks"]:
            emit(author, seed, "source_constraint", check["id"],
                 check["calculation"]["value"] if check["calculation"] else None,
                 check["difference"], check["status"])
        for name, model in record["models"].items():
            if model["status"] != "computed":
                emit(author, seed, name, "not_computable", status=model["status"])
                continue
            for term, value in model["coefficients"].items():
                emit(author, seed, name, "coefficient_" + term, value,
                     model["standardized_coefficient_absolute_errors"].get(term),
                     signed_error=model["standardized_coefficient_signed_errors"].get(term))
            emit(author, seed, name, "residual_sd", model["residual_sd"], model["abs_log_residual_sd_ratio"],
                 signed_error=model["log_residual_sd_ratio"])
        for key, item in record["predictor_correlations"].items():
            emit(author, seed, "predictor_correlation", key, item.get("value"), item.get("absolute_truth_error"),
                 "computed" if item.get("value") is not None else "not_computable")
        for flag in record["failure_flags"]:
            emit(author, seed, "failure_flag", flag, status="flagged")
    return rows


def aggregate(rows):
    """Seeds are nested within constructions; never count rows as replicates."""
    groups = {}
    for row in rows:
        if row["status"] not in {"computed", "evaluated"}:
            continue
        for field in ("value", "error", "signed_error"):
            value = row[field]
            if isinstance(value, (int, float)) and np.isfinite(value):
                key = (row["author"], row["section"], row["metric"], field)
                groups.setdefault(key, []).append(float(value))
    constructions = []
    arm_groups = {}
    for (author, section, metric, field), values in sorted(groups.items()):
        item = {"author": author, "section": section, "metric": metric, "field": field,
                "n_seeds_available": len(values), "n_seeds_planned": 3,
                "mean": float(np.mean(values)), "min": min(values), "max": max(values)}
        constructions.append(item)
        arm_groups.setdefault((author[0], section, metric, field), []).append(item)
    arms = []
    for (arm, section, metric, field), members in sorted(arm_groups.items()):
        complete = len(members) == 2 and all(m["n_seeds_available"] == 3 for m in members)
        arms.append({"arm": arm, "section": section, "metric": metric, "field": field,
                     "n_constructions_available": len(members), "n_constructions_planned": 2,
                     "status": "complete" if complete else "incomplete_no_arm_average",
                     "equal_weight_construction_mean": float(np.mean([m["mean"] for m in members])) if complete else None,
                     "construction_means": {m["author"]: m["mean"] for m in members}})
    return {"construction_summaries": constructions, "arm_summaries": arms,
            "failures": "All attempt and metric failures remain in per-slot records; incomplete arm metrics have no arm average."}


def main():
    protocol, lock, source = runner.verify_batch()
    expected_slots = {(a, s) for a in runner.AUTHORS for s in runner.SEEDS}
    attempts = runner.inventory()
    require(set(attempts) == expected_slots, "Evaluate only after all twelve slots have been attempted")
    require(not (ROOT / "RUNNING.lock").exists(), "Generation is still active or needs interruption audit")
    require(not (ROOT / "RESULTS.json").exists() and not (ROOT / "RESULTS.csv").exists(), "Results already exist; do not overwrite")
    truth_path = runner.safe_file("custodian/TRUTH.json")
    require(runner.sha(truth_path) == lock["truth_sha256"], "Truth differs from sealed commitment")
    truth_raw = runner.read(truth_path)
    truth = truth_summary(truth_raw)
    records = []
    for author in runner.AUTHORS:
        for seed in runner.SEEDS:
            run = attempts[(author, seed)]
            record = {"author": author, "seed": seed, "status": "failed", "execution_receipt_sha256": None}
            try:
                receipt = runner.verify_execution(author, seed)
                record["execution_receipt_sha256"] = runner.sha(run / "execution.json")
                record["execution_status"] = receipt["status"]
                if receipt["status"] != "success":
                    record["error"] = receipt.get("error", {"message": "Execution unsuccessful"})
                else:
                    execution._csv_guard(run / "output/generated.csv", runner.task_contract(), runner.LIMITS["output_bytes"])
                    frame = pd.read_csv(run / "output/generated.csv", float_precision="round_trip")
                    record.update(analyze(frame, source, truth))
                    record["generated_sha256"] = runner.sha(run / "output/generated.csv")
            except Exception as error:
                record.update(status="integrity_or_evaluation_failure", error={"type": type(error).__name__, "message": str(error)[:1500]})
            records.append(record)
    runner.verify_batch()
    report = {"schema_version": 1, "scope": "controlled_same_population_mechanism_diagnostic",
              "created_utc": runner.now(), "clinical_evidence": False,
              "source_feedback_returned_to_authors": False, "attempts": len(records),
              "evaluated_tables": sum(r["status"] == "evaluated" for r in records),
              "batch_lock_sha256": runner.sha(ROOT / "BATCH_LOCK.json"), "truth_sha256": runner.sha(truth_path),
              "evaluation_sha256": runner.sha(__file__), "truth_moment_reference": truth,
              "error_definitions": {"coefficient": "Signed (beta_hat-beta_truth)*sigma_X_truth/sigma_Y_truth and its absolute value",
                                    "sd": "Signed log(SD_hat/SD_truth) and its absolute value",
                                    "residual_sd": "sqrt(SSE/(n-rank(design)))",
                                    "source": "raw signed difference from supplied source estimate"},
              "records": records,
              "limitations": ["Four author constructions and three draws each do not estimate broad Agent superiority.",
                              "All source and target statistics belong to the same artificial population; no transport claim.",
                              "Source diagnostics are computed after final generation and are not a feedback treatment.",
                              "No p-value, confidence-interval overlap or efficacy pass/fail gate is applied."]}
    flattened = flatten(records)
    report["aggregation"] = aggregate(flattened)
    csv_path = ROOT / "RESULTS.csv"
    with csv_path.open("x", newline="", encoding="utf8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["author", "seed", "section", "metric", "value", "error", "signed_error", "status"])
        writer.writeheader(); writer.writerows(flattened)
    report["results_csv_sha256"] = runner.sha(csv_path)
    execution._write(ROOT / "RESULTS.json", report)
    print(json.dumps({k: report[k] for k in ("scope", "attempts", "evaluated_tables", "clinical_evidence")}, indent=2))


if __name__ == "__main__":
    main()
