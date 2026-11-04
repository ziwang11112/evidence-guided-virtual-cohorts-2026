"""Independent aggregate-only audit; never execute a generator or load patients.

Initial mode admits the four fixed initial executions only. The explicit
--final-author-closed flag admits the pinned aggregate reference after closure.
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
        elif isinstance(expected, list):
            if not isinstance(actual, list):
                self.equal(label + ".type", type(actual).__name__, "list")
                return
            self.equal(label + ".length", len(actual), len(expected))
            for i, (a, e) in enumerate(zip(actual, expected)):
                self.compare(label + f"[{i}]", a, e)
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


def comparison_expected(generated, reference):
    coefficients, marginals, relations = {}, {}, {}
    for term, value in generated["coefficients"].items():
        old = reference["coefficients"][term]
        coefficients[term] = {
            "reference": old["value"], "generated": value["value"],
            "difference": value["value"] - old["value"],
            "same_point_sign": (value["value"] > 0) - (value["value"] < 0) ==
                               (old["value"] > 0) - (old["value"] < 0),
            "reference_interval_direction": old["interval_direction"],
            "generated_conditional_interval_direction": value["interval_direction"],
            "reference_ci": [old["lower"], old["upper"]],
            "generated_conditional_ci": [value["lower"], value["upper"]],
        }
    for name, values in generated["marginal"].items():
        marginals[name] = {}
        for metric in ["mean", "sd", "q10", "median", "q90"]:
            old, new = reference["marginal"][name][metric], values[metric]
            marginals[name][metric] = {"reference": old, "generated": new, "difference": new - old}
    for name, values in generated["relationships"].items():
        relations[name] = {}
        for metric, new in values.items():
            old = reference["relationships"][name][metric]
            relations[name][metric] = {"reference": old, "generated": new, "difference": new - old}
    return {"status": "complete", "coefficients": coefficients, "marginals": marginals,
            "relationships": relations, "global_score": None, "new_confirmation": False}


def audit_final(results, protocol):
    """Only admitted aggregate reference is opened; no patient path is accessed."""
    closure_checks, report_checks, binding_checks, variation_checks, markdown_checks = [Checks() for _ in range(5)]
    closure_path = RUN / "LIVE_CLOSURE.json"
    closure = read_json(closure_path)
    declared = closure["requests"]["B"]
    if declared.get("author_closed") is not True or declared.get("choice") != "retain":
        raise RuntimeError("This audit requires an explicit closed retain decision")
    closure_checks.equal("closure.protocol", closure["protocol_sha256"], sha256(RUN / "PROTOCOL.json"))
    deliveries = [r for r in results if r["stage"] == "initial_delivery"]
    expected_ids = [r["run_id"] for r in deliveries]
    expected_all = [r["run_id"] for r in results]
    freeze_hash = sha256(BUNDLE / "candidates/initial/freeze.json")
    closure_checks.compare("closure.request", declared, {
        "author_closed": True, "initial_candidate": "candidates/initial", "final_candidate": "candidates/initial",
        "choice": "retain", "decision_file": "FINAL_DECISION.json",
        "decision_sha256": sha256(BUNDLE / "FINAL_DECISION.json"),
        "initial_freeze_sha256": freeze_hash, "final_freeze_sha256": freeze_hash,
        "delivery_runs": {"initial": expected_ids, "final": expected_ids}})
    for group, base in [("run_files", RUN), ("bundle_files", BUNDLE)]:
        for relative, recorded in declared["artifact_bindings"][group].items():
            binding_checks.equal("closure." + group + "." + relative, sha256(base / relative), recorded)
    controller = read_json(HERE / "CONTROL_MANIFEST.json")
    binding_checks.equal("controller.protocol", controller["protocol_sha256"], sha256(RUN / "PROTOCOL.json"))
    # Hash controller bytes without reading/reusing any analysis implementation.
    for group, base in [("controller_files", RUN), ("mechanics_files", PROJECT)]:
        for relative, recorded in controller[group].items():
            binding_checks.equal("controller." + relative, sha256(base / relative), recorded)
    for name, artifact in controller["checks"].items():
        binding_checks.equal("controller.check." + name, sha256(RUN / artifact["path"]), artifact["sha256"])
    decision = read_json(BUNDLE / "FINAL_DECISION.json")
    closure_checks.compare("decision", decision, {"choice": "retain", "candidate": "candidates/initial",
        "initial_freeze_sha256": freeze_hash, "scheduled_runs_reviewed": expected_all,
        "feedback_decision_round": 1, "revisions_used": 0, "feedback_decisions_used": 1,
        "candidate_unchanged": True, "new_candidate_created": False, "new_table_created": False,
        "target_reference_read": False, "seed_selection": False,
        "findings": {"quality_failures": 0, "primary_bmi_values": {
            r["run_id"]: r["analyses"]["primary"]["coefficients"]["bmi"]["value"] for r in results},
            "secondary_bmi_values": {r["run_id"]: r["analyses"]["descriptive_secondary"]["coefficients"]["bmi"]["value"]
                                     for r in results}}})
    for artifact in decision["artifacts"]:
        binding_checks.equal("decision.artifact." + artifact["path"], sha256(BUNDLE / artifact["path"]), artifact["sha256"])
    manifest = read_json(BUNDLE / "FEEDBACK_READ_MANIFEST.json")
    closure_checks.compare("feedback_manifest", manifest, {"candidate": "candidates/initial",
        "scheduled_runs": expected_all, "initial_freeze": {"path": "candidates/initial/freeze.json", "sha256": freeze_hash}})
    binding_checks.equal("feedback_manifest.audit", sha256(BUNDLE / manifest["audit"]["path"]), manifest["audit"]["sha256"])
    binding_checks.equal("feedback_manifest.file_count", len(manifest["files"]), 8)
    actual_feedback_members = []
    source_record_count = 0
    coefficient_record_count = 0
    for artifact in manifest["files"]:
        path = BUNDLE / artifact["path"]
        binding_checks.equal("feedback_manifest.hash." + artifact["path"], sha256(path), artifact["sha256"])
        binding_checks.equal("feedback_manifest.size." + artifact["path"], path.stat().st_size, artifact["bytes"])
        actual_feedback_members.append((artifact["run_id"], artifact["role"]))
        data = read_json(path)
        if artifact["role"] == "source_semantics_feedback":
            source_record_count += len(data["checks"])
            binding_checks.compare("feedback.link." + artifact["run_id"], data, {
                "run_id": artifact["run_id"], "candidate": "candidates/initial", "status": "complete",
                "output_link_verified": True, "generator_execution_recorded": True,
                "n_computable": 11, "n_not_computable": 23})
            audited_run = next(r for r in results if r["run_id"] == artifact["run_id"])
            binding_checks.compare("feedback.binding." + artifact["run_id"], data["bindings"], {
                "candidate_freeze_sha256": freeze_hash,
                "execution_receipt_sha256": audited_run["artifacts"]["execution_receipt_sha256"],
                "generated_table_sha256": audited_run["artifacts"]["table_sha256"],
                "task_sha256": sha256(BUNDLE / "task.json"),
                "model_spec_sha256": sha256(BUNDLE / "candidates/initial/model_spec.json"),
                "evidence_sha256": sha256(BUNDLE / "candidates/initial/evidence.json"),
                "recipe_sha256": sha256(BUNDLE / "candidates/initial/whole_cohort_feedback.json"),
                "semantics_sha256": sha256(BUNDLE / "candidates/initial/source_semantics_v1.json")})
        else:
            coefficient_record_count += len(data["coefficients"]) + len(data["descriptive_secondary"]["coefficients"])
    expected_feedback_members = [(run_id, role) for run_id in expected_all
                                 for role in ["source_semantics_feedback", "generated_only_diagnostics"]]
    binding_checks.equal("feedback_manifest.members", sorted(actual_feedback_members), sorted(expected_feedback_members))
    closure_checks.compare("feedback_manifest.counts", manifest["review_counts"], {
        "feedback_files": 4, "diagnostic_files": 4, "source_check_records": source_record_count,
        "coefficient_records": coefficient_record_count})
    closure_checks.compare("decision.counts", decision["findings"], {
        "source_checks_reviewed": source_record_count, "coefficient_intervals_reviewed": coefficient_record_count})
    aliases = read_json(RUN / "sessions/B/final_delivery_aliases.json")
    expected_aliases = [{"stage": "final_delivery", "seed": r["seed"], "candidate": "candidates/initial",
        "run_id": r["run_id"], "aliased_initial": True, "physical_execution": False, "status": "success",
        "initial_result_sha256": r["artifacts"]["session_result_sha256"]} for r in deliveries]
    closure_checks.compare("aliases", aliases, {"kind": "retained_delivery_aliases", "aliases": expected_aliases})
    closure_checks.compare("final_family", read_json(RUN / "sessions/B/final_family.json"), {
        "candidate": "candidates/initial", "freeze_sha256": freeze_hash})
    closure_checks.equal("physical_execution_directory_ids", sorted(p.name for p in (BUNDLE / "executions").iterdir() if p.is_dir()), sorted(expected_all))
    closure_checks.equal("physical_reserved_ids", sorted(p.stem.removesuffix("_reserved")
        for p in (RUN / "sessions/B").glob("*_reserved.json")), sorted(expected_all))
    closure_checks.equal("unique_delivery_table_hashes", len({r["artifacts"]["table_sha256"] for r in deliveries}), 3)

    reference_path = PROJECT / protocol["reference"]["path"]
    reference_hash = sha256(reference_path)
    if reference_hash != protocol["reference"]["sha256"]:
        raise RuntimeError("Pinned aggregate reference SHA mismatch; reference not parsed")
    old_reference = read_json(reference_path)["reference"]
    supplied_report_path = HERE / "REPORT.json"
    supplied = read_json(supplied_report_path)
    read_receipt = read_json(HERE / "REFERENCE_READ_RECEIPT.json")
    report_checks.compare("report.reference", supplied["reference"], old_reference)
    report_checks.equal("report.reference.keys", sorted(supplied["reference"]), sorted(old_reference))
    report_checks.compare("report", supplied, {"protocol_sha256": sha256(RUN / "PROTOCOL.json"),
        "closure_sha256": sha256(closure_path), "patient_rows_read": 0})
    report_checks.equal("report.reference_provenance", supplied["reference_provenance"], read_receipt)
    closure_checks.compare("reference_read_receipt", read_receipt, {
        "closure_sha256": sha256(closure_path), "protocol_sha256": sha256(RUN / "PROTOCOL.json"),
        "reference_sha256": reference_hash, "patient_rows_read": 0, "patient_data_decoded": False,
        "reference_refitted": False, "author_closed": True,
        "control_manifest_sha256": sha256(HERE / "CONTROL_MANIFEST.json")})
    closure_checks.equal("reference_read_receipt.path", str(Path(read_receipt["reference_path"])), str(reference_path))
    closure_checks.equal("reference_read_after_closure", datetime.fromisoformat(read_receipt["created_utc"]) >=
                         datetime.fromisoformat(closure["created_utc"]), True)
    closure_checks.equal("feedback_review_before_closure", datetime.fromisoformat(manifest["reviewed_at_utc"]) <=
                         datetime.fromisoformat(closure["created_utc"]), True)
    report_checks.compare("inventory", supplied["inventory"], {"reserved_attempts": 4,
        "physical_delivery_attempts": 3, "successful_delivery_tables": 3, "choice": "retain",
        "initial_freeze_sha256": freeze_hash, "final_freeze_sha256": freeze_hash,
        "decision_sha256": sha256(BUNDLE / "FINAL_DECISION.json"), "artifact_bindings": declared["artifact_bindings"]})
    report_checks.equal("inventory.attempt_ids", sorted(a["run_id"] for a in supplied["inventory"]["all_attempts"]), sorted(expected_all))
    for attempt in supplied["inventory"]["all_attempts"]:
        report_checks.equal("inventory.attempt." + attempt["run_id"], attempt,
            read_json(RUN / "sessions/B" / (attempt["run_id"] + "_result.json")))

    report_checks.equal("slots.count", len(supplied["slots"]), 6)
    report_checks.equal("slots.schedule", [(s["stage"], s["seed"]) for s in supplied["slots"]],
                        [(stage, seed) for stage in ["initial", "final"] for seed in [7401, 7402, 7403]])
    comparisons = []
    for slot in supplied["slots"]:
        run = next(r for r in deliveries if r["seed"] == slot["seed"])
        label = f"slots.{slot['stage']}.{slot['seed']}"
        report_checks.compare(label, slot, {"request": "B", "stage": slot["stage"], "seed": run["seed"],
            "run_id": run["run_id"], "candidate": "candidates/initial", "status": "success", "error": None,
            "execution_status": "success", "aliased_initial": slot["stage"] == "final",
            "table_sha256": run["artifacts"]["table_sha256"],
            "execution_receipt_sha256": run["artifacts"]["execution_receipt_sha256"]})
        entry = {"stage": slot["stage"], "seed": slot["seed"], "run_id": run["run_id"], "comparison": {}}
        for analysis, reference_id in [("primary", "B"), ("descriptive_secondary", "A")]:
            generated = run["analyses"][analysis]
            reported_analysis = slot["analysis"] if analysis == "primary" else slot["analysis"][analysis]
            report_checks.compare(label + "." + analysis, reported_analysis, generated)
            report_checks.equal(label + "." + analysis + ".coefficient_terms", sorted(reported_analysis["coefficients"]), sorted(generated["coefficients"]))
            expected_comparison = comparison_expected(generated, old_reference[reference_id])
            report_checks.compare(label + ".comparison." + analysis, slot["comparison"][analysis], expected_comparison)
            entry["comparison"][analysis] = expected_comparison
        comparisons.append(entry)
    for stage in ["initial", "final"]:
        variance = supplied["seed_variation"][stage]
        variation_checks.compare(stage, variance, {"scheduled_seeds": [7401, 7402, 7403],
            "failed_or_unavailable": [], "retained_aliases": stage == "final"})
        for analysis, predictors in PREDICTORS.items():
            output = variance["analyses"][analysis]
            variation_checks.compare(stage + "." + analysis, output, {"n_complete": 3, "unavailable_seeds": []})
            variation_checks.equal(stage + "." + analysis + ".terms", sorted(output["coefficients"]), sorted(predictors))
            for term in predictors:
                values = [r["analyses"][analysis]["coefficients"][term]["value"] for r in deliveries]
                variation_checks.compare(stage + "." + analysis + "." + term, output["coefficients"][term], {
                    "per_seed": [{"seed": r["seed"], "value": value} for r, value in zip(deliveries, values)],
                    "minimum": min(values), "maximum": max(values), "mean": float(np.mean(values)),
                    "sample_sd": float(np.std(values, ddof=1))})
    report_checks.equal("internal_recomputation_slots", [(r["stage"], r["run_id"]) for r in supplied["internal_recomputation_checks"]],
                        [(s["stage"], s["run_id"]) for s in supplied["slots"]])
    for check in supplied["internal_recomputation_checks"]:
        for analysis, predictors in PREDICTORS.items():
            report_checks.compare("internal." + check["stage"] + "." + check["run_id"] + "." + analysis,
                check[analysis], {"status": "PASS", "unavailable_interval_checks": [],
                    "coefficient_terms": len(predictors) + 1, "marginals": len(predictors) + 1,
                    "relationship_pairs": 2 if analysis == "primary" else 1})
            report_checks.equal("internal.maximum_tolerance", check[analysis]["maximum_coefficient_interval_absolute_difference"] < 1e-9, True)
    markdown = (HERE / "RESULTS.md").read_text(encoding="utf-8-sig")
    markdown_checks.equal("markdown.inventory", "Physical attempts: 4; final choice: retain." in markdown, True)
    for analysis, reference_id in [("primary", "B"), ("descriptive_secondary", "A")]:
        for term in PREDICTORS[analysis]:
            old = old_reference[reference_id]["coefficients"][term]
            values = [r["analyses"][analysis]["coefficients"][term]["value"] for r in deliveries]
            row = f"| {term} | {old['value']:.6g} [{old['lower']:.6g}, {old['upper']:.6g}] | {min(values):.6g} to {max(values):.6g} | {min(values):.6g} to {max(values):.6g} |"
            markdown_checks.equal("markdown." + analysis + "." + term, row in markdown, True)
    for slot in supplied["slots"]:
        row = f"| {slot['stage']} | {slot['seed']} | {slot['run_id']} | success | {slot['stage'] == 'final'} |"
        markdown_checks.equal("markdown.slot." + slot["stage"] + "." + str(slot["seed"]), row in markdown, True)
    blocks = {"closure_checks": closure_checks.summary(), "binding_checks": binding_checks.summary(),
              "report_checks": report_checks.summary(), "seed_variation_checks": variation_checks.summary(),
              "markdown_checks": markdown_checks.summary()}
    return {"status": "pass" if all(b["status"] == "pass" for b in blocks.values()) else "fail",
            "authorization": "Explicit root instruction after author closure, received 2026-11-04",
            "artifacts": {"report_sha256": sha256(supplied_report_path), "results_markdown_sha256": sha256(HERE / "RESULTS.md"),
                          "closure_sha256": sha256(closure_path), "reference_read_receipt_sha256": sha256(HERE / "REFERENCE_READ_RECEIPT.json"),
                          "reference_sha256": reference_hash, "reference_path": str(reference_path)},
            "inventory": {"physical_executions_including_trial": 4, "unique_delivery_tables": 3,
                          "initial_delivery_slots": 3, "final_delivery_slots": 3, "final_aliases": 3,
                          "new_final_tables": 0, "model_revisions": 0},
            **blocks, "independent_reference_comparisons": comparisons,
            "limitations": ["Historical reference aggregates were reused without new patient reads or refits.",
                            "A file hash and numerical agreement do not establish scientific validity.",
                            "Reference CR1-t intervals and synthetic HC3-t intervals have different uncertainty meanings.",
                            "Six delivery slots represent only three unique delivery tables; retain has no new-model gain."]}


def make_markdown(report):
    lines = ["# Independent numerical review", "", "Status: **" + report["status"] + "**.", "",
        "Scope: four prespecified initial generated tables (trial 7400; deliveries 7401–7403), "
        "3,000 rows each. No generator was executed and no patient file was opened. " +
        ("Author closure, six delivery slots and the pinned historical aggregate reference comparison are verified."
         if "final_review" in report else "The historical target reference was not opened; final closure comparison remains pending."), "",
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
    if "final_review" in report:
        final = report["final_review"]
        lines += ["## Postclosure verification", "", f"Final status: **{final['status']}**. "
                  "The author retained the unchanged initial candidate. Six delivery slots contain three unique "
                  "delivery tables, with all three final slots explicitly aliasing their initial runs. Four physical "
                  "executions exist including the trial; no revision or final generation occurred.", "",
                  "| Check block | Outcome | Checks | Maximum numeric difference |",
                  "|---|---|---:|---:|"]
        for key in ["closure_checks", "binding_checks", "report_checks", "seed_variation_checks", "markdown_checks"]:
            block = final[key]
            lines.append(f"| {key} | {block['status']} | {block['checks']} | {block['maximum_absolute_numeric_difference']:.3g} |")
            if block["failures"]:
                lines += ["", "```json", json.dumps(block["failures"], indent=2), "```", ""]
        lines += ["", "Verified the closure and final-decision hash chains, all feedback-manifest hashes/sizes, "
                  "136 source-check records and 36 coefficient records, final aliases, control-manifest file hashes, "
                  "reference read-after-closure receipt, all coefficients including intercepts, every marginal and "
                  "relationship comparison, seed summaries, and displayed RESULTS.md rows.", "",
                  "The reused aggregate reference is byte-identical to the protocol pin. No reference patient data "
                  "were decoded or refitted. Historical reference uncertainty is community-cluster CR1-t; generated "
                  "intervals are conditional HC3-t intervals. Numerical correctness does not establish target validity.", "",
                  "Audited REPORT.json SHA-256: `" + final["artifacts"]["report_sha256"] + "`.", ""]
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
                        "comparison_core_implementation_inspected_or_imported": False,
                        "final_author_closure_received": False},
              "methods": {"regression": "independent NumPy QR OLS and QR-based HC3 sandwich",
                          "intervals": "95% Student-t, df=n-p", "secondary_check": "statsmodels OLS HC3 use_t=True",
                          "sd": "sample ddof=1", "quantiles": "NumPy linear, probabilities .1/.5/.9",
                          "correlations": "SciPy Pearson and average-rank tie-aware Spearman"},
              "runtime": {"python": platform.python_version(), "numpy": np.__version__,
                          "pandas": pd.__version__, "scipy": scipy.__version__, "statsmodels": statsmodels.__version__},
              "runs": results}
    if "--final-author-closed" in sys.argv[1:]:
        report["final_review"] = audit_final(results, protocol)
        report["status"] = "pass_final" if report["status"] != "fail" and report["final_review"]["status"] == "pass" else "fail"
        report["scope"]["final_author_closure_received"] = True
        report["scope"]["historical_reference_read"] = True
        report["scope"]["reference_patient_rows_read"] = 0
        report["scope"]["reference_refitted"] = False
        report["scope"]["controller_bytes_hashed_without_implementation_inspection"] = True
    out = HERE / "INDEPENDENT_NUMERICAL_REVIEW.json"
    out.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    out.with_suffix(".md").write_text(make_markdown(report), encoding="utf-8")
    failures = sum(len(r[block]["failures"]) for r in results for block in
                   ["artifact_checks", "diagnostics_comparison", "statsmodels_crosscheck"])
    if "final_review" in report:
        failures += sum(len(report["final_review"][block]["failures"]) for block in
                        ["closure_checks", "binding_checks", "report_checks", "seed_variation_checks", "markdown_checks"])
    print(json.dumps({"status": report["status"], "runs": len(results), "report": str(out), "failures": failures}))


if __name__ == "__main__":
    main()
