"""Independent aggregate-only audit; never execute a generator or load patients.

Initial mode admits the four fixed initial executions only. Final comparison is
added only after an explicit author-closure instruction to the independent auditor.
No comparison_core or generated_diagnostics implementation is imported or reused.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
from scipy import stats
import statsmodels
import statsmodels.api as sm

HERE = Path(__file__).resolve().parent
RUN = HERE.parent
PROJECT = RUN.parent.parent
BUNDLE = PROJECT.parent.parent / "evcBuild01"
sys.path.insert(0, str(PROJECT))
from cohort_harness.execution import verify_execution  # verifier only, no execution

NUMERIC_COLUMNS = ["age", "female", "bmi", "hba1c", "glucose"]
PREDICTORS = {"primary": ["bmi", "glucose", "age", "female"],
              "descriptive_secondary": ["bmi", "age", "female"]}
RUNS = [("b_initial_trial_7400", 7400, "initial_trial"),
        ("b_initial_delivery_7401", 7401, "initial_delivery"),
        ("b_initial_delivery_7402", 7402, "initial_delivery"),
        ("b_initial_delivery_7403", 7403, "initial_delivery")]
UNITS = {"const": "%", "age": "year", "female": "1", "bmi": "kg/m^2",
         "hba1c": "%", "glucose": "mmol/L"}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Checks:
    def __init__(self):
        self.count = 0
        self.numeric_count = 0
        self.max_absolute_difference = 0.0
        self.failures = []

    def equal(self, label, actual, expected):
        self.count += 1
        if actual != expected:
            self.failures.append({"check": label, "actual": actual, "expected": expected})

    def close(self, label, actual, expected, atol=1e-9, rtol=1e-10):
        self.count += 1
        self.numeric_count += 1
        if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
            error = abs(float(actual) - float(expected))
            if math.isfinite(error):
                self.max_absolute_difference = max(self.max_absolute_difference, error)
            if math.isfinite(actual) and math.isfinite(expected) and math.isclose(
                    actual, expected, abs_tol=atol, rel_tol=rtol):
                return
        self.failures.append({"check": label, "actual": actual, "expected": expected})

    def compare(self, label, actual, expected):
        """Compare every expected key, allowing explicitly additional output fields."""
        if isinstance(expected, dict):
            if not isinstance(actual, dict):
                self.equal(label, type(actual).__name__, "dict")
                return
            for key, value in expected.items():
                if key not in actual:
                    self.equal(label + "." + key + ".present", False, True)
                else:
                    self.compare(label + "." + key, actual[key], value)
        elif isinstance(expected, float):
            self.close(label, actual, expected)
        else:
            self.equal(label, actual, expected)

    def summary(self):
        return {"status": "pass" if not self.failures else "fail", "checks": self.count,
                "numeric_checks": self.numeric_count,
                "maximum_absolute_numeric_difference": self.max_absolute_difference,
                "numeric_tolerance": {"absolute": 1e-9, "relative": 1e-10},
                "failures": self.failures}


def quality(frame, columns):
    values = {name: frame[name].to_numpy(dtype=float) for name in columns}
    return {
        "nonfinite": {name: int(np.count_nonzero(~np.isfinite(value)))
                      for name, value in values.items()},
        "out_of_age_scope": int(np.count_nonzero((values["age"] < 35) | (values["age"] > 74))),
        "invalid_female": int(np.count_nonzero(~np.isin(values["female"], [0, 1]))),
        "nonpositive_bmi": int(np.count_nonzero(values["bmi"] <= 0)),
        "nonpositive_glycemia": {name: int(np.count_nonzero(values[name] <= 0))
                                for name in ("hba1c", "glucose") if name in values},
    }


def marginal_summary(frame, columns):
    summaries = {}
    for name in columns:
        values = frame[name].to_numpy(dtype=float)
        q10, median, q90 = np.quantile(values, [0.1, 0.5, 0.9], method="linear")
        summaries[name] = {"mean": float(np.mean(values)),
                           "sd": float(np.std(values, ddof=1)),
                           "q10": float(q10), "median": float(median),
                           "q90": float(q90), "unit": UNITS[name]}
    return summaries


def relationship(left, right):
    return {"pearson": float(stats.pearsonr(left, right).statistic),
            "spearman": float(stats.spearmanr(left, right).statistic)}


def independent_regression(frame, predictors, numerical_checks, label):
    """Solve with QR; calculate HC3 using Q and R, without normal equations."""
    y = frame["hba1c"].to_numpy(dtype=float)
    design = np.column_stack([np.ones(len(frame)), frame[predictors].to_numpy(dtype=float)])
    q, r = np.linalg.qr(design, mode="reduced")
    beta = np.linalg.solve(r, q.T @ y)
    residual = y - design @ beta
    leverage = np.sum(q * q, axis=1)
    # Each column is a case's linear coefficient influence scaled for HC3.
    influence = np.linalg.solve(r, q.T * (residual / (1.0 - leverage)))
    covariance = influence @ influence.T
    standard_errors = np.sqrt(np.diag(covariance))
    degrees_freedom = len(frame) - design.shape[1]
    critical_t = float(stats.t.ppf(0.975, degrees_freedom))
    intervals = np.column_stack((beta - critical_t * standard_errors,
                                 beta + critical_t * standard_errors))

    external = sm.OLS(y, design).fit(cov_type="HC3", use_t=True)
    terms = ["const"] + predictors
    coefficients = {}
    for i, term in enumerate(terms):
        numerical_checks.close(label + ".statsmodels." + term + ".beta", float(beta[i]),
                               float(external.params[i]))
        numerical_checks.close(label + ".statsmodels." + term + ".se", float(standard_errors[i]),
                               float(external.bse[i]))
        for j, limit in enumerate(["lower", "upper"]):
            numerical_checks.close(label + ".statsmodels." + term + "." + limit,
                                   float(intervals[i, j]), float(external.conf_int()[i, j]))
        low, high = map(float, intervals[i])
        coefficients[term] = {
            "value": float(beta[i]), "standard_error": float(standard_errors[i]),
            "lower": low, "upper": high, "interval_status": "available",
            "unit": "%" if term == "const" else "%/" + UNITS[term],
            "role": "intercept" if term == "const" else ("primary" if term == "bmi" else "secondary"),
            "sign": "positive" if beta[i] > 0 else ("negative" if beta[i] < 0 else "zero"),
            "interval_direction": "positive" if low > 0 else ("negative" if high < 0 else "inconclusive"),
        }
    columns = [name for name in NUMERIC_COLUMNS if name in predictors or name == "hba1c"]
    relationships = {"bmi_hba1c": relationship(frame["bmi"], frame["hba1c"])}
    if "glucose" in predictors:
        relationships["glucose_hba1c"] = relationship(frame["glucose"], frame["hba1c"])
    result = {
        "n": len(frame), "quality": quality(frame, columns), "status": "complete",
        "coefficients": coefficients, "marginal": marginal_summary(frame, columns),
        "relationships": relationships, "reference_read": False,
        "design": {"predictors": predictors, "intercept": True,
                   "rank": int(np.linalg.matrix_rank(design)), "columns": design.shape[1],
                   "condition_number": float(np.linalg.cond(design))},
        "formula": "hba1c ~ 1 + " + " + ".join(predictors),
    }
    extras = {"estimator": "QR OLS with QR-based HC3 sandwich covariance",
              "degrees_freedom": degrees_freedom, "critical_t_0.975": critical_t,
              "leverage_min": float(np.min(leverage)), "leverage_max": float(np.max(leverage)),
              "residual_mean": float(np.mean(residual)),
              "covariance": {term: {other: float(covariance[i, j])
                                    for j, other in enumerate(terms)}
                             for i, term in enumerate(terms)}}
    return result, extras


def audit_run(run_id, seed, stage):
    directory = BUNDLE / "executions" / run_id
    execution_checks, diagnostics_checks, numeric_checks = Checks(), Checks(), Checks()
    receipt = read_json(directory / "execution.json")
    execution_checks.equal("receipt.run_id", receipt["run_id"], run_id)
    execution_checks.equal("receipt.seed", receipt["limits"]["seed"], seed)
    execution_checks.equal("receipt.status", receipt["status"], "success")
    execution_checks.equal("receipt.generator_executed", receipt["generator_executed"], True)
    execution_checks.equal("receipt.route", receipt["route"], "generator.py")
    execution_checks.equal("receipt.candidate", receipt["candidate"], "candidates/initial")
    file_hashes = {name: sha256(directory / name) for name in receipt["files"]}
    for name, recorded in receipt["files"].items():
        execution_checks.equal("execution.file." + name, file_hashes[name], recorded)
    actual_files = sorted(str(p.relative_to(directory)).replace("\\", "/")
                          for p in directory.rglob("*") if p.is_file() and p.name != "execution.json")
    execution_checks.equal("execution.file_set", actual_files, sorted(receipt["files"]))
    candidate = BUNDLE / receipt["candidate"]
    execution_checks.equal("candidate.freeze", sha256(candidate / "freeze.json"),
                           receipt["candidate_freeze_sha256"])
    bindings = read_json(directory / "input_bindings.json")
    execution_checks.equal("bindings.freeze", bindings["candidate_freeze_sha256"],
                           receipt["candidate_freeze_sha256"])
    for name, recorded in bindings["files"].items():
        source = BUNDLE / name if name == "task.json" else candidate / name
        execution_checks.equal("bindings.staged." + name, sha256(directory / "input" / name), recorded)
        execution_checks.equal("bindings.source." + name, sha256(source), recorded)
    request = read_json(directory / "input/request.json")
    for name, value in receipt["limits"].items():
        execution_checks.equal("request." + name, request[name], value)
    try:
        verified = verify_execution(BUNDLE, run_id)
        execution_checks.equal("harness.verify_execution.status", verified["status"], "success")
        verification = {"status": "pass", "execution_status": verified["status"], "generator_invoked_by_audit": False}
    except Exception as exc:
        verification = {"status": "fail", "error": type(exc).__name__ + ": " + str(exc)}
        execution_checks.equal("harness.verify_execution", verification["error"], "success")

    session_result_path = RUN / "sessions/B" / (run_id + "_result.json")
    session_result = read_json(session_result_path)
    execution_checks.compare("session", session_result, {"run_id": run_id, "seed": seed,
        "stage": stage, "candidate": "candidates/initial", "reference_read": False,
        "status": "success", "execution_status": "success", "execution_verified": True,
        "generator_executed": True, "table_sha256": file_hashes["output/generated.csv"],
        "diagnostics_status": "complete", "source_feedback_status": "complete"})
    diagnostics_path = BUNDLE / "author_feedback" / (run_id + "_diagnostics.json")
    execution_checks.equal("session.diagnostics.path", Path(session_result["diagnostics"]), diagnostics_path)
    execution_checks.equal("session.diagnostics.sha256", sha256(diagnostics_path), session_result["diagnostics_sha256"])
    source_feedback_path = Path(session_result["source_feedback"])
    expected_feedback = BUNDLE / "semantic_feedback_v1" / (run_id + "_source") / "feedback.json"
    execution_checks.equal("session.source_feedback.path", str(source_feedback_path), str(expected_feedback))
    execution_checks.equal("session.source_feedback.sha256", sha256(expected_feedback), session_result["source_feedback_sha256"])
    family = read_json(RUN / "sessions/B" / "initial_family.json")
    stage_binding = read_json(RUN / "sessions/B" / (stage + "_binding.json"))
    for label, binding in [("initial_family", family), (stage, stage_binding)]:
        execution_checks.compare(label, binding, {"candidate": "candidates/initial",
            "freeze_sha256": receipt["candidate_freeze_sha256"]})

    frame = pd.read_csv(directory / "output/generated.csv", dtype={"person_id": str})
    task = read_json(BUNDLE / "task.json")
    execution_checks.equal("table.row_count", len(frame), task["n_rows"])
    execution_checks.equal("table.column_order", list(frame.columns), [c["name"] for c in task["columns"]])
    table_quality = {"missing_cells": int(frame.isna().sum().sum()),
                     "duplicate_identifiers": int(frame["person_id"].duplicated().sum()),
                     "empty_identifiers": int(frame["person_id"].fillna("").str.strip().eq("").sum()),
                     "noninteger_age": int(np.count_nonzero(frame["age"] % 1)),
                     "noninteger_female": int(np.count_nonzero(frame["female"] % 1)),
                     **quality(frame, NUMERIC_COLUMNS)}
    for key in ["missing_cells", "duplicate_identifiers", "empty_identifiers", "noninteger_age", "noninteger_female"]:
        execution_checks.equal("table.quality." + key, table_quality[key], 0)
    execution_checks.compare("table.quality", table_quality, {
        "nonfinite": {name: 0 for name in NUMERIC_COLUMNS}, "out_of_age_scope": 0,
        "invalid_female": 0, "nonpositive_bmi": 0,
        "nonpositive_glycemia": {"hba1c": 0, "glucose": 0}})
    diagnostics = read_json(diagnostics_path)
    analyses, extras = {}, {}
    for name, predictors in PREDICTORS.items():
        recomputed, detail = independent_regression(frame, predictors, numeric_checks, name)
        reported = diagnostics if name == "primary" else diagnostics["descriptive_secondary"]
        diagnostics_checks.compare(name, reported, recomputed)
        analyses[name], extras[name] = recomputed, detail
    all_relationships = {left + "__" + right: relationship(frame[left], frame[right])
                         for left, right in itertools.combinations(NUMERIC_COLUMNS, 2)}
    return {"run_id": run_id, "stage": stage, "seed": seed,
            "artifacts": {"execution_receipt_sha256": sha256(directory / "execution.json"),
                          "table_sha256": file_hashes["output/generated.csv"],
                          "diagnostics_sha256": sha256(diagnostics_path),
                          "session_result_sha256": sha256(session_result_path),
                          "candidate_freeze_sha256": receipt["candidate_freeze_sha256"],
                          "execution_file_count": len(file_hashes)},
            "execution_verification": verification, "artifact_checks": execution_checks.summary(),
            "diagnostics_comparison": diagnostics_checks.summary(),
            "statsmodels_crosscheck": numeric_checks.summary(), "table_quality": table_quality,
            "analyses": analyses, "regression_details": extras, "all_pairwise_relationships": all_relationships}


def make_markdown(report):
    lines = ["# Independent numerical review", "", "Status: **" + report["status"] + "**.", "",
        "Scope: four prespecified initial generated tables (trial 7400; deliveries 7401–7403), "
        "3,000 rows each. No generator was executed, and no patient file or historical target reference was opened. "
        "Final author closure and reference comparison remain pending.", "",
        "Regression coefficients and HC3 covariance were independently recomputed using QR decomposition. "
        "95% intervals use the Student-t critical value with n − p residual degrees of freedom. "
        "An additional statsmodels OLS/HC3 check was performed. Marginal SD uses n − 1; quantiles use "
        "linear interpolation; Pearson and tie-aware Spearman correlations were recomputed with SciPy.", "",
        "| Seed | Stage | Artifact checks | Diagnostic checks | Statsmodels checks | Largest diagnostic absolute difference |",
        "|---:|---|---|---|---|---:|"]
    for run in report["runs"]:
        summary = run["diagnostics_comparison"]
        lines.append(f"| {run['seed']} | {run['stage']} | {run['artifact_checks']['status']} | "
                     f"{summary['status']} ({summary['numeric_checks']} numeric) | "
                     f"{run['statsmodels_crosscheck']['status']} | {summary['maximum_absolute_numeric_difference']:.3g} |")
    lines += ["", "All declared output quality flags were recomputed. Checks additionally cover identifier "
              "uniqueness, missing cells, integer age/sex values, column order and row count. Every recorded "
              "execution-file hash, candidate/input binding, prescribed seed, session result, feedback hash "
              "and diagnostic hash was verified. The harness verifier was invoked only in verification mode.", "",
              "| Seed | Analysis | BMI slope | HC3 95% interval |", "|---:|---|---:|---|"]
    for run in report["runs"]:
        for name, result in run["analyses"].items():
            bmi = result["coefficients"]["bmi"]
            lines.append(f"| {run['seed']} | {name} | {bmi['value']:.9f} | [{bmi['lower']:.9f}, {bmi['upper']:.9f}] |")
    lines += ["", "The JSON companion retains every coefficient, standard error, interval, covariance element, "
              "marginal summary, all ten pairwise Pearson/Spearman relationships, quality flag and check outcome. "
              "These are conditional summaries of the synthetic draws, not evidence of target validity or "
              "uncertainty about sources, model structure, transport or patients.", ""]
    failures = [(r["run_id"], block, r[block]["failures"]) for r in report["runs"]
                for block in ["artifact_checks", "diagnostics_comparison", "statsmodels_crosscheck"] if r[block]["failures"]]
    if failures:
        lines += ["## Failures", "", "```json", json.dumps(failures, indent=2), "```", ""]
    return "\n".join(lines)


def main():
    protocol = read_json(RUN / "PROTOCOL.json")
    if protocol["stages"]["initial_trial"] != [7400] or protocol["stages"]["initial_delivery"] != [7401, 7402, 7403]:
        raise RuntimeError("Prespecified initial schedule changed")
    results = [audit_run(*run) for run in RUNS]
    report = {"kind": "independent_aggregate_numerical_review", "created_utc": datetime.now(timezone.utc).isoformat(),
              "status": "pass_initial_pending_final_closure" if all(
                  r[block]["status"] == "pass" for r in results for block in
                  ["artifact_checks", "diagnostics_comparison", "statsmodels_crosscheck"]) else "fail",
              "script_sha256": sha256(__file__), "protocol_sha256": sha256(RUN / "PROTOCOL.json"),
              "scope": {"generated_tables_read": 4, "patient_files_read": 0, "historical_reference_read": False,
                        "generators_executed": 0, "new_tables_generated": 0, "aggregate_only_report": True,
                        "comparison_core_read_or_imported": False,
                        "final_author_closure_received": False},
              "methods": {"regression": "independent NumPy QR OLS and QR-based HC3 sandwich",
                          "intervals": "95% Student-t, df=n-p", "secondary_check": "statsmodels OLS HC3 use_t=True",
                          "sd": "sample ddof=1", "quantiles": "NumPy linear, probabilities .1/.5/.9",
                          "correlations": "SciPy Pearson and average-rank tie-aware Spearman"},
              "runtime": {"python": platform.python_version(), "numpy": np.__version__,
                          "pandas": pd.__version__, "scipy": scipy.__version__, "statsmodels": statsmodels.__version__},
              "runs": results}
    out = HERE / "INDEPENDENT_NUMERICAL_REVIEW.json"
    out.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    out.with_suffix(".md").write_text(make_markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "runs": len(results), "report": str(out),
                      "failures": sum(len(r[block]["failures"]) for r in results for block in
                      ["artifact_checks", "diagnostics_comparison", "statsmodels_crosscheck"])}))


if __name__ == "__main__":
    main()
