"""Post-freeze evaluator. Import is inert; never run before all outputs are frozen.

Usage: python custodian/evaluate.py --freeze execution_freeze.json --out results
The unchanged analysis module is imported only after every frozen file verifies.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from validate_completion import validate_completion

ROOT = Path(__file__).resolve().parents[1]
METHODS = ("agent", "statistical_reference")
CASES = ("mcar_a", "mcar_b", "baseline_dependent")
OUTCOMES = ("primary_standardized_weight_pfs", "secondary_pfs_month3_minus0")
KEYS = ["person_id", "month"]


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _local(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if Path(relative).is_absolute() or not path.is_relative_to(root.resolve()):
        raise ValueError("Frozen project path must stay inside the project")
    return path


def verify_freeze(freeze: dict, root: Path = ROOT) -> dict:
    """Hash all artifacts before any data/module loads; fail closed on mismatch."""
    if freeze.get("m") != 20 or set(freeze.get("cases", {})) != set(CASES):
        raise ValueError("Freeze must contain m=20 and the three prespecified cases")
    files = freeze.get("files", {})
    if not isinstance(files, dict) or not files:
        raise ValueError("Freeze lacks artifact hashes")
    own_relative = str(Path(__file__).resolve().relative_to(root.resolve())).replace("\\", "/")
    validator_relative = "custodian/validate_completion.py"
    for required in (own_relative, validator_relative, "PROTOCOL.md", "allowed/evidence.json", "custodian/case_manifest.json"):
        if required not in files:
            raise ValueError(f"Mandatory frozen file absent: {required}")
    verified = {}
    for relative, expected in files.items():
        path = _local(root, relative)
        actual = sha256(path)
        if actual != expected:
            raise ValueError(f"Frozen hash mismatch: {relative}")
        verified[relative] = actual
    for label in ("reference", "analysis_module"):
        record = freeze[label]
        path = Path(record["path"])
        if not path.is_absolute() or sha256(path) != record["sha256"]:
            raise ValueError(f"Pinned {label} hash mismatch")
    seen_outputs = set()
    for case in CASES:
        entry = freeze["cases"][case]
        if set(entry["outputs"]) != set(METHODS):
            raise ValueError("Every case must include both prespecified methods")
        paths = [entry["masked"], entry["targets"]]
        for method in METHODS:
            outputs = entry["outputs"][method]
            if len(outputs) != freeze["m"] or len(set(outputs)) != freeze["m"]:
                raise ValueError("Every arm requires exactly 20 distinct completion files")
            for output in outputs:
                if output in seen_outputs:
                    raise ValueError("Completion file reused across arms")
                seen_outputs.add(output)
            paths.extend(outputs)
        for relative in paths:
            if relative not in files:
                raise ValueError(f"Unfrozen data path: {relative}")
    case_manifest = json.loads((root / "custodian/case_manifest.json").read_text(encoding="utf-8"))
    if case_manifest["reference"] != freeze["reference"]:
        raise ValueError("Reference does not match custodian case manifest")
    for case in CASES:
        for field in ("masked", "targets"):
            if case_manifest["cases"][case][field] != freeze["cases"][case][field]:
                raise ValueError("Case path differs from custodian case manifest")
    if case_manifest["shared_evidence_sha256"] != files[case_manifest["shared_evidence"]]:
        raise ValueError("Shared evidence hash differs from case manifest")
    return {"status": "verified", "n_artifacts": len(verified), "n_completions": len(seen_outputs),
            "files": verified, "reference_sha256": freeze["reference"]["sha256"],
            "analysis_module_sha256": freeze["analysis_module"]["sha256"]}


def pool_rubin(estimates, standard_errors) -> dict:
    q = np.asarray(estimates, dtype=float)
    se = np.asarray(standard_errors, dtype=float)
    if q.ndim != 1 or se.shape != q.shape or len(q) < 2:
        raise ValueError("Pooling needs aligned one-dimensional estimates/SEs, m>=2")
    if not np.isfinite(q).all() or not np.isfinite(se).all() or (se <= 0).any():
        raise ValueError("Cannot pool failed or nonfinite estimates/SEs")
    m = len(q)
    qbar = float(q.mean())
    ubar = float(np.mean(se**2))
    between = 0.0 if np.all(q == q[0]) else float(np.var(q, ddof=1))
    inflation = (1 + 1 / m) * between
    total = ubar + inflation
    pooled_se = math.sqrt(total)
    if between == 0:
        df = math.inf
        critical = float(stats.norm.ppf(0.975))
        pvalue = float(2 * stats.norm.sf(abs(qbar / pooled_se)))
    else:
        df = (m - 1) * (1 + ubar / inflation)**2
        critical = float(stats.t.ppf(0.975, df))
        pvalue = float(2 * stats.t.sf(abs(qbar / pooled_se), df))
    return {"status": "ok", "m": m, "estimate": qbar, "se": pooled_se,
            "Qbar": qbar, "Ubar": ubar, "B": between, "T": total,
            "df": None if math.isinf(df) else float(df), "df_infinite": math.isinf(df),
            "ci_low": qbar - critical * pooled_se, "ci_high": qbar + critical * pooled_se,
            "p": pvalue, "ci_method": "Rubin large-complete-sample t approximation; normal limit when B=0"}


def assert_mask_contract(reference: pd.DataFrame, masked: pd.DataFrame, targets: pd.DataFrame) -> None:
    if list(reference.columns) != list(masked.columns) or len(reference) != len(masked):
        raise ValueError("Masked case shape changed")
    if list(targets.columns) != KEYS or targets.duplicated(KEYS).any():
        raise ValueError("Invalid target-key table")
    if not reference[KEYS].equals(masked[KEYS]) or reference.duplicated(KEYS).any():
        raise ValueError("Case identifiers/order differ from unmasked reference")
    target_set = set(map(tuple, targets[KEYS].to_numpy()))
    reference_set = set(map(tuple, reference[KEYS].to_numpy()))
    if not target_set <= reference_set:
        raise ValueError("Target absent from reference")
    for position, row_key in enumerate(map(tuple, reference[KEYS].to_numpy())):
        for column in reference.columns:
            original = reference.iloc[position][column]
            current = masked.iloc[position][column]
            if column == "pfs" and row_key in target_set:
                if pd.isna(original) or not pd.isna(current) or int(row_key[1]) == 0:
                    raise ValueError("Mask is not originally observed follow-up PFS")
            elif not ((pd.isna(original) and pd.isna(current)) or original == current):
                raise ValueError("Mask modified a non-target cell")


def target_values(frame: pd.DataFrame, targets: pd.DataFrame) -> np.ndarray:
    """Key-based alignment supports independently permuted target-key files."""
    if frame.duplicated(KEYS).any() or targets.duplicated(KEYS).any():
        raise ValueError("Duplicate keys cannot be scored")
    index = pd.MultiIndex.from_frame(targets[KEYS])
    series = frame.set_index(KEYS)["pfs"]
    if not index.isin(series.index).all():
        raise ValueError("Missing target key during scoring")
    values = series.reindex(index).to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("Nonfinite target score input")
    return values


def cell_metrics(truth_values, completion_values) -> tuple[dict, list[dict]]:
    truth = np.asarray(truth_values, dtype=float)
    draws = np.asarray(completion_values, dtype=float)
    if draws.ndim != 2 or draws.shape[1:] != truth.shape or not np.isfinite(draws).all() or not np.isfinite(truth).all():
        raise ValueError("Invalid aligned arrays for target scoring")
    errors = draws - truth[None, :]
    draw_mae = np.mean(np.abs(errors), axis=1)
    draw_rmse = np.sqrt(np.mean(errors**2, axis=1))
    mean_error = draws.mean(axis=0) - truth
    aggregate = {"status": "ok", "n_targets": len(truth), "m": len(draws),
                 "mae_mean_completion": float(np.mean(np.abs(mean_error))),
                 "rmse_mean_completion": float(np.sqrt(np.mean(mean_error**2))),
                 "mean_draw_mae": float(draw_mae.mean()), "mean_draw_rmse": float(draw_rmse.mean()),
                 "score_scope": "Artificial masked PFS cells only; native missing cells unscored"}
    individual = [{"completion": i + 1, "mae": float(a), "rmse": float(b)}
                  for i, (a, b) in enumerate(zip(draw_mae, draw_rmse))]
    return aggregate, individual


def _valid_analysis(record: dict) -> bool:
    return record.get("status") == "ok" and all(record.get(k) is not None and math.isfinite(record[k])
                                                for k in ("estimate", "se", "ci_low", "ci_high")) and record["se"] > 0


def analyze_two(module, frame: pd.DataFrame) -> dict:
    """Use precisely the unchanged module functions specified in PROTOCOL.md."""
    selected = {}
    for outcome, function, selection in (
        (OUTCOMES[0], lambda: module.pooled_associations(frame), lambda r: r["term"] == "pfs"),
        (OUTCOMES[1], lambda: module.time_trajectory(frame, "pfs"), lambda r: r["term"] == "month_3_minus_0"),
    ):
        try:
            rows = [r for r in function() if selection(r)]
            if len(rows) != 1:
                raise ValueError("Analysis selector did not identify exactly one prespecified result")
            record = rows[0]
            if not _valid_analysis(record):
                record = dict(record, status=f"invalid_analysis:{record.get('status', 'absent')}")
            selected[outcome] = record
        except Exception as error:
            selected[outcome] = {"status": f"analysis_exception:{type(error).__name__}:{error}",
                                 "estimate": None, "se": None, "ci_low": None, "ci_high": None}
    return selected


def comparison(record: dict, reference: dict, missing: dict) -> dict:
    if not all(_valid_analysis(r) for r in (record, reference, missing)):
        return {"comparison_status": "unavailable_failed_analysis"}
    error = abs(record["estimate"] - reference["estimate"])
    missing_error = abs(missing["estimate"] - reference["estimate"])
    return {"comparison_status": "ok", "unmasked_estimate": reference["estimate"],
            "unmasked_se": reference["se"], "absolute_coefficient_error": error,
            "signed_coefficient_error": record["estimate"] - reference["estimate"],
            "se_ratio_to_unmasked": record["se"] / reference["se"],
            "missing_only_absolute_error": missing_error,
            "absolute_error_improvement_over_missing_only": missing_error - error,
            "improvement_interpretation": "Positive means smaller absolute error than missing-only; negative means deterioration"}


def evaluate(freeze_path: Path, output: Path, root: Path = ROOT) -> dict:
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    verification = verify_freeze(freeze, root)
    if output.exists() and any(output.iterdir()):
        raise ValueError("Results directory is not empty; refusing to overwrite a prior evaluation")
    if output.resolve() != (root / "results").resolve():
        raise ValueError("Evaluation output is restricted to this project's NEW results directory")
    # Import only after hash verification. No imputation modules are imported here.
    spec = importlib.util.spec_from_file_location("frozen_paper_analysis", freeze["analysis_module"]["path"])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    reference_frame = pd.read_csv(freeze["reference"]["path"], float_precision="round_trip")
    reference = analyze_two(module, reference_frame)
    failures = []
    if not all(_valid_analysis(r) for r in reference.values()):
        failures.append({"case": "unmasked", "method": "reference", "reason": "Unmasked reference analysis failed"})
    analysis_rows = [{"case": "unmasked", "method": "reference", "completion": None,
                      "outcome": outcome, **record} for outcome, record in reference.items()]
    pooled_rows, cell_rows, cell_draw_rows, arm_checks = [], [], [], []
    for case in CASES:
        entry = freeze["cases"][case]
        masked_path, targets_path = root / entry["masked"], root / entry["targets"]
        masked = pd.read_csv(masked_path, float_precision="round_trip")
        targets = pd.read_csv(targets_path)
        assert_mask_contract(reference_frame, masked, targets)
        missing = analyze_two(module, masked)
        truth_values = target_values(reference_frame, targets)
        for outcome, record in missing.items():
            analysis_rows.append({"case": case, "method": "missing_only", "completion": None,
                                  "outcome": outcome, **record})
            pooled_rows.append({"case": case, "method": "missing_only", "outcome": outcome,
                                **record, **comparison(record, reference[outcome], record)})
            if not _valid_analysis(record):
                failures.append({"case": case, "method": "missing_only", "outcome": outcome,
                                 "reason": record["status"]})
        for method in METHODS:
            all_analyses = {outcome: [] for outcome in OUTCOMES}
            predicted_values = []
            contract_failures = []
            for number, relative in enumerate(entry["outputs"][method], start=1):
                completion_path = root / relative
                try:
                    validated = validate_completion(masked_path, targets_path, completion_path)
                    completed = pd.read_csv(completion_path, float_precision="round_trip")
                    predicted_values.append(target_values(completed, targets))
                    estimates = analyze_two(module, completed)
                    contract_status = validated["status"]
                except Exception as error:
                    contract_status = f"failed:{type(error).__name__}:{error}"
                    contract_failures.append({"completion": number, "file": relative, "reason": contract_status})
                    estimates = {outcome: {"status": "completion_contract_failed", "estimate": None, "se": None,
                                           "ci_low": None, "ci_high": None} for outcome in OUTCOMES}
                for outcome, record in estimates.items():
                    all_analyses[outcome].append(record)
                    analysis_rows.append({"case": case, "method": method, "completion": number,
                                          "file": relative, "contract_status": contract_status,
                                          "outcome": outcome, **record,
                                          **comparison(record, reference[outcome], missing[outcome])})
            arm_checks.append({"case": case, "method": method, "n_expected": freeze["m"],
                               "n_contract_passed": freeze["m"] - len(contract_failures),
                               "contract_failures": contract_failures})
            for outcome, records in all_analyses.items():
                invalid = [i + 1 for i, r in enumerate(records) if not _valid_analysis(r)]
                if invalid or contract_failures or len(records) != freeze["m"]:
                    pooled = {"status": "incomplete_arm", "m_expected": freeze["m"],
                              "m_valid": sum(_valid_analysis(r) for r in records),
                              "invalid_completions": invalid,
                              "reason": "No failed completion or analysis is dropped or pooled around"}
                    failures.append({"case": case, "method": method, "outcome": outcome,
                                     "reason": "incomplete_arm", "invalid_completions": invalid})
                else:
                    pooled = pool_rubin([r["estimate"] for r in records], [r["se"] for r in records])
                pooled_rows.append({"case": case, "method": method, "outcome": outcome, **pooled,
                                    **comparison(pooled, reference[outcome], missing[outcome])})
            if contract_failures or len(predicted_values) != freeze["m"]:
                cell_rows.append({"case": case, "method": method, "status": "incomplete_arm",
                                  "n_expected": freeze["m"], "n_valid": len(predicted_values),
                                  "reason": "No scoring of a selected valid subset"})
            else:
                aggregate, per_draw = cell_metrics(truth_values, predicted_values)
                cell_rows.append({"case": case, "method": method, **aggregate})
                cell_draw_rows.extend({"case": case, "method": method, **r} for r in per_draw)
            print(f"Evaluated {case}/{method}: {freeze['m']} retained completion slots", flush=True)
    expected_completion_metrics = len(CASES) * len(METHODS) * freeze["m"] * len(OUTCOMES)
    actual_completion_metrics = sum(r["method"] in METHODS for r in analysis_rows)
    if actual_completion_metrics != expected_completion_metrics:
        raise AssertionError("Completion metric inventory is incomplete")
    report = {
        "status": "complete" if not failures else "incomplete",
        "freeze_sha256": sha256(freeze_path), "verification": verification,
        "n_completion_files": len(CASES) * len(METHODS) * freeze["m"],
        "expected_completion_metric_rows": expected_completion_metrics,
        "actual_completion_metric_rows": actual_completion_metrics,
        "n_reference_metric_rows": 2 + len(CASES) * 2,
        "reference": reference, "arm_checks": arm_checks, "failures": failures,
        "pooled": pooled_rows, "cell_metrics": cell_rows,
        "interpretation_limits": [
            "Native missing cells are not scored and remain unchanged.",
            "The unmasked reference is the source's observed-data analysis, with native missingness and sampling uncertainty.",
            "Three overlapping masks of one cohort do not estimate population coverage or a real-null false-positive rate.",
            "Rubin intervals use a large-complete-sample approximation and do not certify proper MI for arbitrary completion draws.",
            "Coefficient-error improvements and deteriorations are retained; p-value agreement is not the quality endpoint.",
        ],
    }
    # Recheck freeze immediately before persisting to detect concurrent changes.
    verify_freeze(freeze, root)
    output.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(freeze_path, output / "execution_freeze.json")
    (output / "evaluation.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    pd.DataFrame(analysis_rows).to_csv(output / "all_analysis_results.csv", index=False)
    pd.DataFrame(pooled_rows).to_csv(output / "pooled_results.csv", index=False)
    pd.DataFrame(cell_rows).to_csv(output / "cell_metrics.csv", index=False)
    pd.DataFrame(cell_draw_rows).to_csv(output / "cell_metrics_by_completion.csv", index=False)
    artifact_hashes = {p.name: sha256(p) for p in output.iterdir() if p.is_file()}
    (output / "artifact_hashes.json").write_text(json.dumps(artifact_hashes, indent=2) + "\n", encoding="utf-8")
    return {"status": report["status"], "n_completion_files": report["n_completion_files"],
            "n_completion_metric_rows": actual_completion_metrics, "n_failed_records": len(failures)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=ROOT / "results")
    parser.add_argument("--check-freeze", action="store_true")
    args = parser.parse_args()
    if args.check_freeze:
        freeze = json.loads(args.freeze.read_text(encoding="utf-8"))
        report = verify_freeze(freeze)
        print(json.dumps({k: v for k, v in report.items() if k != "files"}, indent=2))
    else:
        print(json.dumps(evaluate(args.freeze.resolve(), args.out.resolve()), indent=2))


if __name__ == "__main__":
    main()
