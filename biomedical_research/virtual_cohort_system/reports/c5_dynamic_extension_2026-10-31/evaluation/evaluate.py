"""C5 outcome-only evaluation. Run only after final-output commitment and reveal.

This file neither imports nor executes a candidate generator. The fixture is
artificial and fully identified by the public final Gaussian moment packet.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import NormalDist


FIXTURE = "c5_artificial_dynamic_extension"
EXPECTED = {
    "parent_r1": ("parent", 1, 25101, None),
    "parent_r2": ("parent", 2, 25103, None),
    "parent_r3": ("parent", 3, 25107, None),
    "joint_r1": ("joint", 1, 25201, None),
    "joint_r2": ("joint", 2, 25203, None),
    "joint_r3": ("joint", 3, 25207, None),
    "extended_r1": ("extended", 1, 25301, "parent_r1"),
    "extended_r2": ("extended", 2, 25303, "parent_r2"),
    "extended_r3": ("extended", 3, 25307, "parent_r3"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def resolve(root: Path, name: str) -> Path:
    path = Path(name)
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def verify_release_gate(root: Path):
    """Validate controller's final manifest before opening answers or tables."""
    manifest_path = root / "final_output_manifest.json"
    reveal_path = root / "reveal_authorization.json"
    require(manifest_path.is_file(), "Final-output manifest required before reveal")
    require(reveal_path.is_file(), "Explicit reveal authorization required")
    manifest, reveal = read_json(manifest_path), read_json(reveal_path)
    for obj, name in ((manifest, "manifest"), (reveal, "reveal")):
        require(obj.get("schema_version") == 1, f"Invalid {name} schema")
        require(obj.get("fixture_id") == FIXTURE, f"Wrong {name} fixture")
        require(obj.get("all_final_outputs_committed") is True,
                f"{name} does not attest all final outputs committed")
    require(bool(manifest.get("committed_utc")), "Manifest commitment time required")
    require(bool(reveal.get("authorized_utc")), "Reveal time required")
    require(reveal.get("authorized_by") == "root_controller", "Wrong reveal authorizer")
    require(reveal.get("final_output_manifest_sha256") == sha256(manifest_path),
            "Reveal must bind exact final manifest bytes")
    entries = manifest.get("outputs")
    require(isinstance(entries, list) and len(entries) == 9,
            "Manifest must commit exactly nine scheduled outputs")
    require({e.get("run_id") for e in entries} == set(EXPECTED),
            "Manifest missing/duplicating scheduled run IDs")
    paths = {}
    for entry in entries:
        rid = entry["run_id"]
        expected = EXPECTED[rid]
        actual = tuple(entry.get(k) for k in ("arm", "replicate", "seed", "parent_run_id"))
        require(actual == expected, f"Schedule metadata mismatch: {rid}")
        require(entry.get("n_rows") == 2000, f"Wrong declared sample size: {rid}")
        require(isinstance(entry.get("path"), str), f"Missing output path: {rid}")
        path = resolve(root, entry["path"])
        require(path.is_file(), f"Committed output absent: {rid}")
        require(sha256(path) == entry.get("sha256"), f"Committed output changed: {rid}")
        paths[rid] = path
    require(len(set(paths.values())) == 9, "Nine distinct output paths required")
    commitment = read_json(root / "source_commitment.json")
    require(commitment.get("fixture_id") == FIXTURE, "Wrong source commitment fixture")
    for item in commitment["committed_files"]:
        path = resolve(root, item["path"])
        require(path.is_file() and sha256(path) == item["sha256"],
                f"Changed committed fixture artifact: {item['path']}")
    return manifest, reveal, paths


def record_estimate(estimate, reference):
    delta = float(estimate) - float(reference)
    return {"estimate": float(estimate), "analytical_reference": float(reference),
            "signed_deviation": delta, "absolute_deviation": abs(delta)}


def lexical_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def preflight_tables(paths, np, pd):
    """Read structure and preservation only, before opening analytical answers."""
    frames, checks = {}, {}
    for rid, (arm, _, _, _) in EXPECTED.items():
        try:
            frame = pd.read_csv(paths[rid], dtype={"subject_id": str}, float_precision="round_trip")
            columns = ["subject_id", "x1", "x2"] + ([] if arm == "parent" else ["x3"])
            require(list(frame.columns) == columns, "Wrong columns or column order")
            require(len(frame) == 2000, "Wrong row count")
            require(bool(frame["subject_id"].notna().all()) and bool(frame["subject_id"].is_unique)
                    and bool(frame["subject_id"].astype(str).str.len().gt(0).all()), "Invalid identifiers")
            require(bool(np.isfinite(frame[columns[1:]].to_numpy(dtype=float)).all()),
                    "Nonfinite or nonnumeric cells")
            frames[rid] = frame
            checks[rid] = {"valid": True}
        except Exception as error:
            checks[rid] = {"valid": False, "failure": f"{type(error).__name__}: {error}"}
    for replicate in (1, 2, 3):
        parent_id, extension_id = f"parent_r{replicate}", f"extended_r{replicate}"
        if parent_id not in frames or extension_id not in frames:
            continue
        parent, extension = frames[parent_id], frames[extension_id]
        exact = parent["subject_id"].tolist() == extension["subject_id"].tolist() and all(
            np.array_equal(parent[name].to_numpy(), extension[name].to_numpy()) for name in ("x1", "x2"))
        checks[extension_id]["preserved_parent_cells"] = bool(exact)
        if not exact:
            checks[extension_id]["valid"] = False
            checks[extension_id]["failure"] = "Original identifiers, order, or numeric cells changed"
    return all(check["valid"] for check in checks.values()), checks


def analyze_table(frame, truth, np):
    names = [name for name in ("x1", "x2", "x3") if name in frame]
    idx = [truth["variables"].index(name) for name in names]
    means = np.asarray(truth["means"], dtype=float)
    covariance = np.asarray(truth["covariance"], dtype=float)
    values = frame[names].to_numpy(dtype=float)
    n, p = values.shape
    cov = np.cov(values, rowvar=False, ddof=1)
    corr = np.corrcoef(values, rowvar=False)
    statistics = {"mean": {}, "sd": {}, "quantiles": {}, "covariance": {}, "correlation": {}}
    for local, (name, true_index) in enumerate(zip(names, idx)):
        true_mean = means[true_index]
        true_sd = float(np.sqrt(covariance[true_index, true_index]))
        statistics["mean"][name] = record_estimate(values[:, local].mean(), true_mean)
        statistics["sd"][name] = record_estimate(values[:, local].std(ddof=1), true_sd)
        statistics["quantiles"][name] = {}
        for q in (0.05, 0.50, 0.95):
            ref = true_mean + true_sd * NormalDist().inv_cdf(q)
            statistics["quantiles"][name][str(q)] = record_estimate(
                np.quantile(values[:, local], q, method="linear"), ref)
        for other_local in range(local, p):
            other_name, other_index = names[other_local], idx[other_local]
            key = f"{name},{other_name}"
            statistics["covariance"][key] = record_estimate(
                cov[local, other_local], covariance[true_index, other_index])
            if other_local != local:
                true_corr = covariance[true_index, other_index] / np.sqrt(
                    covariance[true_index, true_index] * covariance[other_index, other_index])
                statistics["correlation"][key] = record_estimate(corr[local, other_local], true_corr)
    old_design = np.column_stack((np.ones(n), values[:, 0]))
    old_coefficients, _, old_rank, _ = np.linalg.lstsq(old_design, values[:, 1], rcond=None)
    require(old_rank == 2, "A1 regression matrix rank deficient")
    endpoints = {
        "A1_slope_x1": record_estimate(old_coefficients[1], truth["analytical_answers"]["A1_slope_x1"]),
        "A1_intercept": record_estimate(old_coefficients[0], truth["analytical_answers"]["A1_intercept"]),
    }
    residual_checks = None
    if "x3" in names:
        design = np.column_stack((np.ones(n), values[:, :2]))
        coefficients, _, rank, _ = np.linalg.lstsq(design, values[:, 2], rcond=None)
        require(rank == 3, "A2 regression matrix rank deficient")
        residuals = values[:, 2] - design @ coefficients
        residual_variance = float(residuals @ residuals / (n - 3))
        for name, estimate in (("A2_intercept", coefficients[0]),
                               ("A2_slope_x1", coefficients[1]),
                               ("A2_slope_x2", coefficients[2]),
                               ("A3_residual_variance", residual_variance),
                               ("A3_residual_sd", np.sqrt(residual_variance))):
            endpoints[name] = record_estimate(estimate, truth["analytical_answers"][name])
        beta = np.asarray(truth["conditional"]["slopes"], dtype=float)
        true_conditional_mean = means[2] + (values[:, :2] - means[:2]) @ beta
        true_residuals = values[:, 2] - true_conditional_mean
        residual_checks = {
            "residual_definition": "x3 minus the analytical population conditional mean",
            "mean": record_estimate(true_residuals.mean(), 0.0),
            "sd": record_estimate(true_residuals.std(ddof=1), truth["analytical_answers"]["A3_residual_sd"]),
            "pearson_with_x1": record_estimate(np.corrcoef(true_residuals, values[:, 0])[0, 1], 0.0),
            "pearson_with_x2": record_estimate(np.corrcoef(true_residuals, values[:, 1])[0, 1], 0.0),
        }
    return {"endpoints": endpoints, "source_and_distribution_checks": statistics,
            "population_conditional_residual_checks": residual_checks}


def summarize(results, np):
    arm_summary = {}
    for arm in ("parent", "joint", "extended"):
        selected = [result for result in results.values()
                    if result["arm"] == arm and result.get("analysis") is not None]
        arm_summary[arm] = {}
        if not selected:
            continue
        for endpoint in selected[0]["analysis"]["endpoints"]:
            values = np.array([r["analysis"]["endpoints"][endpoint]["estimate"] for r in selected])
            ref = selected[0]["analysis"]["endpoints"][endpoint]["analytical_reference"]
            arm_summary[arm][endpoint] = {
                "n_available_scheduled_draws": len(values),
                "mean": float(values.mean()),
                "between_seed_sample_sd": float(values.std(ddof=1)) if len(values) > 1 else None,
                "minimum": float(values.min()), "maximum": float(values.max()),
                "analytical_reference": ref,
                "mean_signed_deviation": float((values - ref).mean()),
                "mean_absolute_deviation": float(np.abs(values - ref).mean()),
                "maximum_absolute_deviation": float(np.abs(values - ref).max()),
            }
    differences = []
    for replicate in (1, 2, 3):
        joint, extended = results[f"joint_r{replicate}"], results[f"extended_r{replicate}"]
        if joint.get("analysis") is None or extended.get("analysis") is None:
            differences.append({"replicate": replicate, "status": "not_computable_due_to_recorded_structure_or_analysis_failure"})
            continue
        delta = {key: joint["analysis"]["endpoints"][key]["estimate"] -
                      extended["analysis"]["endpoints"][key]["estimate"]
                 for key in joint["analysis"]["endpoints"]}
        differences.append({"replicate": replicate, "joint_minus_extended": delta,
                            "interpretation": "descriptive bookkeeping comparison, not paired samples or an algorithm-effect estimate"})
    return arm_summary, differences


def report_markdown(report):
    lines = ["# C5 artificial dynamic-variable-extension evaluation", "",
             "This evaluates one invented, fully specified Gaussian example. It is an implementation and mechanism sanity check, not biomedical validation, a new conditional-probability theory, or method superiority.", "",
             "All nine scheduled outputs were committed and their hashes verified before analytical answers and tables were read. All declared endpoints are retained. Monte Carlo discrepancies are descriptive; no clinical or numerical closeness threshold was invented.", "",
             f"Structural checks passed for all tables: **{report['all_structural_checks_pass']}**.",
             f"Exact parsed original-cell preservation for all extensions: **{report['all_extensions_preserve_old_cells']}**.", "",
             "## Analytical references", "", "| Endpoint | Population answer |", "|---|---:|"]
    for name, value in report["analytical_reference"]["analytical_answers"].items():
        lines.append(f"| {name} | {value:.10g} |")
    lines.extend(["", "## Prespecified per-run endpoint estimates", "",
                  "| Run | Endpoint | Estimate | Reference | Signed deviation |", "|---|---|---:|---:|---:|"])
    for rid, result in report["runs"].items():
        if result.get("analysis") is None:
            lines.append(f"| {rid} | RECORDED FAILURE | — | — | — |")
            continue
        for endpoint, stat in result["analysis"]["endpoints"].items():
            lines.append(f"| {rid} | {endpoint} | {stat['estimate']:.8g} | {stat['analytical_reference']:.8g} | {stat['signed_deviation']:.6g} |")
    lines.extend(["", "## Old-cell preservation", "",
                  "| Extension | Parent | Parsed cells exact | Printed tokens exact | Maximum absolute x1/x2 difference |",
                  "|---|---|---|---|---:|"])
    for item in report["preservation"]:
        lines.append(f"| {item['extended_run_id']} | {item['parent_run_id']} | {item['all_old_cells_exact']} | {item.get('lexical_old_cells_exact')} | {item.get('maximum_absolute_numeric_difference')} |")
    lines.extend(["", "## Interpretation and complete diagnostics", "",
                  "Each extension shares every old variable and row with its parent. Joint draws are separate draws; matching replicate numbers are only bookkeeping. The three seeds per arm are Monte Carlo draws from one specified model and source construction, not independent scientific evidence. A single fresh author supplies the three programs, so differences cannot establish an author or algorithm effect.", "",
                  "The accompanying evaluation.json records all source moments, correlations, quantiles, conditional residual checks, per-arm means, between-seed sample SDs, ranges, deviations, and every prespecified joint-minus-extension endpoint difference. Failed structure or analysis is retained explicitly. No output is rejected for a numerical result and no source or generator is revised from these results.", "",
                  "A successful result supports reuse and compatible variable extension for this artificial fixture only. It does not establish transport to real populations, real unmeasured-variable recovery, calibration under uncertain evidence, causal validity, or a general advantage over one-shot generation.", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    manifest, reveal, paths = verify_release_gate(root)
    # Deliberately imported/read only after final-output commitment and reveal gate.
    import numpy as np
    import pandas as pd
    preflight_ok, preflight = preflight_tables(paths, np, pd)
    if not preflight_ok:
        outcome_free_failure = {"fixture_id": FIXTURE, "analytical_truth_read": False,
            "status": "stopped_fewer_than_nine_valid_scheduled_tables", "preflight": preflight,
            "interpretation": "Retain every run and failure. Do not regenerate or reveal analytical truth to force a comparison."}
        destination = root / "evaluation" / "preflight_failure.json"
        destination.write_text(json.dumps(outcome_free_failure, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": outcome_free_failure["status"], "analytical_truth_read": False,
                          "failure_record": str(destination)}))
        return
    truth = read_json(root / "custody" / "analytic_truth.json")
    require(truth["fixture_id"] == FIXTURE, "Wrong analytic truth fixture")
    frames, results = {}, {}
    for rid, (arm, replicate, seed, parent_id) in EXPECTED.items():
        entry = {"arm": arm, "replicate": replicate, "seed": seed, "parent_run_id": parent_id,
                 "path": str(paths[rid]), "sha256": sha256(paths[rid]), "analysis": None}
        try:
            frame = pd.read_csv(paths[rid], dtype={"subject_id": str}, float_precision="round_trip")
            columns = ["subject_id", "x1", "x2"] + ([] if arm == "parent" else ["x3"])
            checks = {"column_order": list(frame.columns) == columns,
                      "row_count": len(frame) == 2000,
                      "identifiers": "subject_id" in frame and bool(frame["subject_id"].notna().all())
                          and bool(frame["subject_id"].is_unique)
                          and bool(frame["subject_id"].astype(str).str.len().gt(0).all())}
            numeric_columns = [name for name in columns if name != "subject_id"]
            checks["finite_numeric_values"] = all(name in frame for name in numeric_columns) and bool(
                np.isfinite(frame[numeric_columns].to_numpy(dtype=float)).all())
            entry["structural_checks"] = checks
            entry["structure_pass"] = all(checks.values())
            frames[rid] = frame
            if entry["structure_pass"]:
                entry["analysis"] = analyze_table(frame, truth, np)
            else:
                entry["analysis_status"] = "not_computable_due_to_recorded_structure_failure"
        except Exception as error:
            entry["structure_pass"] = entry.get("structure_pass", False)
            entry["analysis_status"] = "recorded_failure"
            entry["failure"] = f"{type(error).__name__}: {error}"
        results[rid] = entry
    preservation = []
    for replicate in (1, 2, 3):
        parent_id, extension_id = f"parent_r{replicate}", f"extended_r{replicate}"
        item = {"parent_run_id": parent_id, "extended_run_id": extension_id, "all_old_cells_exact": False}
        try:
            parent, extended = frames[parent_id], frames[extension_id]
            ids_match = parent["subject_id"].tolist() == extended["subject_id"].tolist()
            numeric_equal = {name: bool(np.array_equal(parent[name].to_numpy(), extended[name].to_numpy()))
                             for name in ("x1", "x2")}
            differences = {name: float(np.max(np.abs(parent[name].to_numpy(dtype=float) -
                                                     extended[name].to_numpy(dtype=float))))
                           for name in ("x1", "x2")}
            lexical_parent, lexical_extension = lexical_rows(paths[parent_id]), lexical_rows(paths[extension_id])
            lexical_equal = len(lexical_parent) == len(lexical_extension) and all(
                all(a.get(name) == b.get(name) for name in ("subject_id", "x1", "x2"))
                for a, b in zip(lexical_parent, lexical_extension))
            item.update({"identifier_and_order_exact": ids_match, "numeric_columns_exact": numeric_equal,
                         "maximum_absolute_difference_by_column": differences,
                         "maximum_absolute_numeric_difference": max(differences.values()),
                         "lexical_old_cells_exact": lexical_equal,
                         "all_old_cells_exact": ids_match and all(numeric_equal.values())})
            old_parent = results[parent_id].get("analysis")
            old_extended = results[extension_id].get("analysis")
            if old_parent and old_extended:
                item["A1_estimates_exact"] = all(old_parent["endpoints"][key]["estimate"] ==
                    old_extended["endpoints"][key]["estimate"] for key in ("A1_intercept", "A1_slope_x1"))
        except Exception as error:
            item["failure"] = f"{type(error).__name__}: {error}"
        preservation.append(item)
    summary, differences = summarize(results, np)
    report = {
        "schema_version": 1, "fixture_id": FIXTURE,
        "evaluated_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Explicitly artificial fully identified Gaussian implementation/mechanism sanity check",
        "final_output_manifest_sha256": sha256(root / "final_output_manifest.json"),
        "source_commitment_sha256": sha256(root / "source_commitment.json"),
        "reveal_authorization": reveal, "all_output_hashes_verified_before_truth_read": True,
        "n_scheduled_outputs": 9, "n_scheduled_outputs_retained": len(results),
        "all_structural_checks_pass": all(r.get("structure_pass", False) for r in results.values()),
        "all_analyses_computed": all(r.get("analysis") is not None for r in results.values()),
        "all_extensions_preserve_old_cells": all(r["all_old_cells_exact"] for r in preservation),
        "analytical_reference": truth, "runs": results, "preservation": preservation,
        "per_arm_descriptive_summary": summary, "joint_minus_extended_by_replicate": differences,
        "interpretation_constraints": [
            "All three primary analysis definitions, both partial slopes, and all scheduled runs retained.",
            "Finite-sample differences are descriptive Monte Carlo variation, without a clinical tolerance or closeness pass threshold.",
            "Extensions share parent cells; matching joint replicate numbers do not create paired independent evidence.",
            "Repeated seeds and duplicated source summaries are not independent scientific evidence.",
            "One author across arms does not identify algorithm superiority or an authorship effect.",
            "Exact Gaussian moment evidence identifies the population answers; this is not unidentifiable discovery.",
            "No biomedical, causal, transportability, or real-evidence uncertainty validation is claimed.",
        ],
    }
    destination = root / "evaluation"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "evaluation.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (destination / "report.md").write_text(report_markdown(report), encoding="utf-8")
    print(json.dumps({"evaluation_json": str(destination / "evaluation.json"),
                      "report_md": str(destination / "report.md"),
                      "all_structural_checks_pass": report["all_structural_checks_pass"],
                      "all_analyses_computed": report["all_analyses_computed"],
                      "all_extensions_preserve_old_cells": report["all_extensions_preserve_old_cells"]}))


if __name__ == "__main__":
    main()
