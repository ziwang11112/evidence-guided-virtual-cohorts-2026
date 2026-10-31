"""Fixed M15-B1 estimands; no generation, calibration, or individual prediction.

Pure functions accept in-memory data and never open data files. The CLI is
disabled without --execute and a controller-authored release manifest; it
verifies both candidate freezes before opening the private reference. This is
a procedural gate, not an access-control sandbox or proof of reviewer identity.
See README.md for the release schema and estimand/status definitions.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


BASE_COLUMNS = ("sample_id", "race", "sex", "age", "bmi", "urate")
DESIGN_COLUMNS = ("SDMVSTRA", "SDMVPSU")
OPTIONAL_REFERENCE_COLUMNS = ("SEQN", "WTPH2YR")
GROUPS = (("White", "male"), ("White", "female"), ("Black", "male"), ("Black", "female"))
GLOBAL_IDS = ("global_bmi", "global_age", "global_curvature", "global_interaction")
GLOBAL_SPECS = (
    ("global_bmi", "urate ~ 1+b+a+m+r", "b", "mg/dL per 5 kg/m^2", "base", 1),
    ("global_age", "urate ~ 1+b+a+m+r", "a", "mg/dL per 10 years", "base", 2),
    ("global_curvature", "urate ~ 1+b+a+m+r+b*b", "b*b", "mg/dL per b^2", "curvature", 5),
    ("global_interaction", "urate ~ 1+b+a+m+r+b*m", "b*m",
     "mg/dL per 5 kg/m^2: male minus female slope", "interaction", 5),
)
LIMITATIONS = (
    "Unweighted descriptions of the identical 200-person equal-stratum quota cohort; "
    "not national estimates or survey inference. WTPH2YR is ignored in analysis. "
    "Leave-one-joint-PSU-out ranges are descriptive sensitivity ranges, not confidence "
    "intervals or sampling distributions. They do not account for literature, generator, "
    "transport, or finite-row authoring uncertainty. Same sign alone does not establish "
    "analytical usability; synthetic sample size does not increase real evidence."
)


class EvaluationError(ValueError):
    """Invalid structural contract or release gate; no silent row dropping."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise EvaluationError(message)


def validate_table(frame: pd.DataFrame, *, reference: bool = False) -> pd.DataFrame:
    """Validate structure and identities without dropping nonfinite numeric cells.

    Missing/nonfinite numeric data become explicit estimand failures, while
    duplicate IDs, bad categories, and unexpected columns reject the table.
    Optional private identifiers/weights are not used by any estimator.
    """
    _require(isinstance(frame, pd.DataFrame), "Expected a pandas DataFrame")
    _require(frame.columns.is_unique, "Duplicate table column names")
    required = set(BASE_COLUMNS) | (set(DESIGN_COLUMNS) if reference else set())
    allowed = required | (set(OPTIONAL_REFERENCE_COLUMNS) if reference else set())
    _require(required <= set(frame.columns), "Required analysis columns are missing")
    _require(set(frame.columns) <= allowed, "Unexpected analysis columns")
    result = frame.copy(deep=True)
    ids = result["sample_id"]
    _require(ids.map(lambda value: isinstance(value, str) and bool(value.strip())).all(),
             "sample_id must contain nonempty strings")
    _require(not ids.duplicated().any(), "Duplicate sample_id")
    _require(result["race"].isin(["White", "Black"]).all(), "race must be White or Black")
    _require(result["sex"].isin(["male", "female"]).all(), "sex must be male or female")
    for name in ("age", "bmi", "urate"):
        result[name] = pd.to_numeric(result[name], errors="coerce").astype(float)
    if reference:
        for name in DESIGN_COLUMNS:
            _require(result[name].notna().all(), "Reference design cells must not be missing")
            _require(result[name].map(lambda value: bool(str(value).strip())).all(),
                     "Reference design cells must not be empty")
            # Neither numeric infinities nor string spellings of them identify a PSU.
            _require(not result[name].astype(str).str.casefold().isin(
                ["nan", "inf", "+inf", "-inf", "infinity", "+infinity", "-infinity"]).any(),
                "Reference design cells must be finite")
    return result


def _canonical(frame: pd.DataFrame) -> pd.DataFrame:
    """Fixed ID order keeps floating-point reductions invariant to input ordering."""
    return frame.sort_values("sample_id", kind="stable").reset_index(drop=True)


def _sign(value: float | None) -> str | None:
    if value is None:
        return None
    return "positive" if value > 0 else "negative" if value < 0 else "zero"


def _ols(x: np.ndarray, y: np.ndarray, index: int) -> dict[str, Any]:
    n, p = x.shape
    complete = np.isfinite(y) & np.isfinite(x).all(axis=1)
    result: dict[str, Any] = {
        "n": int(n), "n_complete": int(complete.sum()), "rank": None,
        "n_parameters": int(p), "value": None, "status": "ok",
        "rank_definition": "OLS design matrix", "reason": "",
    }
    # Rank is still informative when only y is nonfinite; no rows are deleted.
    if np.isfinite(x).all():
        try:
            result["rank"] = int(np.linalg.matrix_rank(x)) if n else 0
        except np.linalg.LinAlgError:
            result.update(status="numerical_failure", reason="Matrix rank computation failed")
            return result
    if not complete.all():
        result.update(status="nonfinite", reason="Nonfinite response or predictor; no rows dropped")
        return result
    if n < p:
        result.update(status="insufficient_n", reason="Fewer rows than model parameters")
        return result
    if result["rank"] != p:
        result.update(status="rank_deficient", reason="Model design is not full column rank")
        return result
    try:
        beta, _, rank, _ = np.linalg.lstsq(x, y, rcond=None)
    except np.linalg.LinAlgError:
        result.update(status="numerical_failure", reason="Least squares computation failed")
        return result
    result["rank"] = int(rank)
    if rank != p:
        result.update(status="rank_deficient", reason="Least squares design is not full column rank")
    elif not np.isfinite(beta).all():
        result.update(status="numerical_failure", reason="Least squares returned nonfinite coefficients")
    else:
        result["value"] = float(beta[index])
    return result


def _global_estimates(frame: pd.DataFrame) -> list[dict[str, Any]]:
    with np.errstate(over="ignore", invalid="ignore"):
        b = (frame["bmi"].to_numpy(dtype=float) - 28.0) / 5.0
        a = (frame["age"].to_numpy(dtype=float) - 40.0) / 10.0
        m = (frame["sex"].to_numpy() == "male").astype(float)
        r = (frame["race"].to_numpy() == "Black").astype(float)
        base = np.column_stack((np.ones(len(frame)), b, a, m, r))
        designs = {"base": base, "curvature": np.column_stack((base, b*b)),
                   "interaction": np.column_stack((base, b*m))}
    y = frame["urate"].to_numpy(dtype=float)
    output = []
    for key, formula, coefficient, units, design, index in GLOBAL_SPECS:
        estimate = _ols(designs[design], y, index)
        output.append({"estimand": key, "family": "global_coefficient", "race": "all", "sex": "all",
                       "model": formula, "coefficient": coefficient, "units": units,
                       **estimate, "sign": _sign(estimate["value"])})
    return output


def _summary(values: np.ndarray, statistic: str) -> dict[str, Any]:
    n = len(values)
    result: dict[str, Any] = {
        "n": int(n), "n_complete": int(np.isfinite(values).sum()), "rank": 1 if n else 0,
        "n_parameters": 1, "rank_definition": "intercept-only group design; no regression fitted",
        "value": None, "status": "ok", "reason": "",
    }
    if not np.isfinite(values).all():
        result.update(status="nonfinite", reason="Nonfinite group outcome; no rows dropped")
    elif n < (2 if statistic == "sd" else 1):
        result.update(status="insufficient_n", reason="Too few group rows for this statistic")
    else:
        with np.errstate(over="ignore", invalid="ignore"):
            if statistic == "mean":
                value = np.mean(values)
            elif statistic == "sd":
                value = np.std(values, ddof=1)
            elif statistic == "median":
                value = np.quantile(values, 0.5, method="linear")
            else:
                value = np.quantile(values, 0.9, method="linear")
        if np.isfinite(value):
            result["value"] = float(value)
        else:
            result.update(status="numerical_failure", reason="Summary computation returned nonfinite value")
    return result


def evaluate_table(frame: pd.DataFrame, *, reference: bool = False) -> list[dict[str, Any]]:
    """Return all 24 fixed records, including failures; never infer weights or CIs."""
    clean = _canonical(validate_table(frame, reference=reference))
    output = _global_estimates(clean)
    for race, sex in GROUPS:
        group = clean.loc[(clean["race"] == race) & (clean["sex"] == sex)]
        x = np.column_stack((np.ones(len(group)), group["urate"], group["age"]))
        estimate = _ols(x, group["bmi"].to_numpy(dtype=float), 1)
        output.append({"estimand": f"reverse_{race}_{sex}", "family": "group_reverse_coefficient",
                       "race": race, "sex": sex, "model": "bmi ~ 1+urate+age", "coefficient": "urate",
                       "units": "(kg/m^2)/(mg/dL)", **estimate, "sign": _sign(estimate["value"])})
    for race, sex in GROUPS:
        group = clean.loc[(clean["race"] == race) & (clean["sex"] == sex)]
        for statistic in ("mean", "sd", "median", "q90"):
            estimate = _summary(group["urate"].to_numpy(dtype=float), statistic)
            output.append({"estimand": f"{statistic}_{race}_{sex}", "family": "group_summary",
                           "race": race, "sex": sex, "model": "descriptive group statistic",
                           "coefficient": statistic, "units": "mg/dL", **estimate, "sign": None})
    assert len(output) == 24
    return output


def validate_pair(reference: pd.DataFrame, candidate: pd.DataFrame, *, require_quota: bool = True) -> None:
    """Require the exact same ID order and observed covariate values in both tables."""
    ref = validate_table(reference, reference=True)
    gen = validate_table(candidate)
    _require(ref["sample_id"].tolist() == gen["sample_id"].tolist(),
             "Candidate must preserve the reference sample_id rows and order")
    for name in ("race", "sex", "age", "bmi"):
        _require(np.array_equal(ref[name].to_numpy(), gen[name].to_numpy()),
                 f"Candidate changed observed {name} values")
    _require(np.isfinite(ref[["age", "bmi"]].to_numpy()).all(), "Observed covariates must be finite")
    if require_quota:
        _require(len(ref) == 200, "Benchmark requires exactly 200 matched people")
        for race, sex in GROUPS:
            _require(int(((ref["race"] == race) & (ref["sex"] == sex)).sum()) == 50,
                     "Benchmark requires exactly 50 people in each race/sex group")


def compare_tables(reference: pd.DataFrame, candidate: pd.DataFrame, *, require_quota: bool = True
                   ) -> list[dict[str, Any]]:
    """Pair all fixed estimands, reporting generated-minus-measured differences."""
    validate_pair(reference, candidate, require_quota=require_quota)
    measured = evaluate_table(reference, reference=True)
    generated = evaluate_table(candidate)
    output = []
    for ref, gen in zip(measured, generated, strict=True):
        _require(ref["estimand"] == gen["estimand"], "Internal estimand order mismatch")
        valid = ref["status"] == gen["status"] == "ok"
        is_coefficient = ref["family"] != "group_summary"
        output.append({
            **{key: ref[key] for key in ("estimand", "family", "race", "sex", "model", "coefficient", "units")},
            "measured": ref, "generated": gen,
            "difference_generated_minus_measured": gen["value"] - ref["value"] if valid else None,
            "same_sign": ref["sign"] == gen["sign"] if valid and is_coefficient else None,
        })
    return output


def reference_sensitivity(reference: pd.DataFrame) -> dict[str, Any]:
    """Delete each observed joint (stratum, PSU) group; keep every fit and failure."""
    ref = _canonical(validate_table(reference, reference=True))
    full = {record["estimand"]: record for record in _global_estimates(ref)}
    groups = list(ref.groupby(list(DESIGN_COLUMNS), sort=False, dropna=False).indices.items())
    # Stable serialization/order does not turn same-number PSUs in different strata into one group.
    groups.sort(key=lambda item: (str(item[0][0]), str(item[0][1])))
    deletions: dict[str, list[dict[str, Any]]] = {key: [] for key in GLOBAL_IDS}
    for (stratum, psu), indices in groups:
        keep = np.ones(len(ref), dtype=bool)
        keep[np.asarray(indices, dtype=int)] = False
        for estimate in _global_estimates(ref.loc[keep]):
            deletions[estimate["estimand"]].append({
                "omitted_stratum": str(stratum), "omitted_psu": str(psu),
                "n_omitted": int((~keep).sum()), "n_retained": int(keep.sum()), **estimate,
            })
    summaries = []
    for key in GLOBAL_IDS:
        fits = deletions[key]
        finite = [fit for fit in fits if fit["status"] == "ok" and fit["value"] is not None]
        values = [fit["value"] for fit in finite]
        same_finite_sign = (all(fit["sign"] == full[key]["sign"] for fit in finite)
                            if finite and full[key]["status"] == "ok" else None)
        complete = bool(fits) and len(finite) == len(fits) and full[key]["status"] == "ok"
        summaries.append({
            "estimand": key, "units": full[key]["units"], "n_full": len(ref),
            "full_estimate": full[key], "omitted_psu_group_count": len(fits),
            "finite_deletion_count": len(finite), "failed_deletion_count": len(fits) - len(finite),
            "rank_failure_count": sum(fit["rank"] is not None and fit["rank"] < fit["n_parameters"]
                                      for fit in fits),
            "range_min": min(values) if values else None, "range_max": max(values) if values else None,
            "finite_deletion_sign_stable_with_full": same_finite_sign,
            "all_deletions_sign_stable_with_full": same_finite_sign if complete else None,
            "status": "complete" if complete else "incomplete",
            "deletions": fits,
        })
    return {"kind": "descriptive_leave_one_joint_psu_out", "limitations": LIMITATIONS,
            "sign_definition": "Strict floating-point sign relative to the full reference estimate; no tolerance",
            "sign_stability_failure_rule": "All-deletions stability is null if any fit fails; finite-only stability is separate",
            "summaries": summaries}


def _sha256(path: Path) -> str:
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256")
    return digest.hexdigest()


def _json(path: Path) -> dict[str, Any]:
    def no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result = {}
        for key, value in pairs:
            _require(key not in result, "Duplicate release JSON key")
            result[key] = value
        return result

    def invalid_constant(value: str) -> None:
        raise EvaluationError(f"Invalid JSON constant: {value}")

    result = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=no_duplicates,
                        parse_constant=invalid_constant)
    _require(isinstance(result, dict), "Release manifest must be a JSON object")
    return result


def _check_hash(path: Path, digest: Any, label: str) -> None:
    _require(isinstance(digest, str) and len(digest) == 64 and
             all(char in "0123456789abcdef" for char in digest), f"Invalid {label} SHA256")
    _require(path.is_file() and _sha256(path) == digest, f"{label} hash mismatch or missing file")


def verify_release(manifest_path: Path, reference_path: Path, initial_path: Path, final_path: Path
                   ) -> dict[str, Any]:
    """Verify the controller release and both lifecycle freezes before reference access.

    The manifest is a trusted controller assertion, not a signed capability.
    Lifecycle verification may open candidate tables, never the reference.
    """
    release = _json(manifest_path)
    _require(release.get("schema_version") == 1 and
             release.get("kind") == "m15b_target_evaluation_release", "Wrong evaluation release schema")
    _require(release.get("evaluation_authorized") is True, "Controller did not authorize evaluation")
    checks = release.get("controller_checks", {})
    for key in ("both_releases_verified", "source_feedback_binding_verified", "source_exposure_map_verified",
                "preservation_verified", "independent_code_review_complete"):
        _require(checks.get(key) is True, f"Required controller check missing: {key}")
    bundle = Path(release["bundle_path"]).resolve()
    _require(bundle.is_dir(), "Release bundle is missing")
    _check_hash(Path(__file__).resolve().parent.parent / "PROTOCOL.md", release["protocol_sha256"], "protocol")
    _check_hash(Path(__file__).resolve(), release["evaluator_sha256"], "evaluator")
    _check_hash(bundle / "task.json", release["task_sha256"], "task")
    _check_hash(bundle / "observed.csv", release["observed_sha256"], "observed")
    project = Path(__file__).resolve().parents[3]
    if str(project) not in sys.path:
        sys.path.insert(0, str(project))
    from cohort_harness.lifecycle import verify_candidate

    receipts = {}
    for label, supplied in (("initial", initial_path), ("final", final_path)):
        item = release[label]
        relative = item["candidate"]
        _require(isinstance(relative, str) and len(relative.split("/")) == 2 and
                 relative.split("/")[0] == "candidates" and relative.split("/")[1] not in ("", ".", ".."),
                 "Release candidate must be candidates/<name>")
        candidate_dir = bundle / relative
        _require(supplied.resolve() == (candidate_dir / "generated.csv").resolve(),
                 f"Explicit {label} path differs from release candidate")
        _check_hash(candidate_dir / "freeze.json", item["freeze_sha256"], f"{label} freeze")
        receipt = verify_candidate(bundle, relative)
        _require(receipt["route"] == "generated.csv", "Evaluation requires the direct-table route")
        _require(receipt["commitments"].get("task.json") == release["task_sha256"] and
                 receipt["commitments"].get("observed.csv") == release["observed_sha256"],
                 "Release task/observed commitments differ from freeze")
        _check_hash(supplied, item["table_sha256"], f"{label} table")
        _require(receipt["commitments"].get(relative + "/generated.csv") == item["table_sha256"],
                 "Release table commitment differs from freeze")
        receipts[label] = receipt
    _require(receipts["initial"]["revision_index"] == 0, "Initial candidate is not the initial freeze")
    # Trace final lineage from the verified receipts: initial must be its ancestor or itself.
    current = receipts["final"]
    while current["candidate"] != receipts["initial"]["candidate"] and current["parent"] is not None:
        current = _json(bundle / current["parent"]["receipt_path"])
    _require(current["candidate"] == receipts["initial"]["candidate"], "Final does not descend from initial")
    _require(reference_path.resolve() == Path(release["reference_path"]).resolve(),
             "Explicit reference path differs from controller release")
    # First reference-file access occurs only after every release check above succeeds.
    _check_hash(reference_path, release["reference_sha256"], "reference")
    return release


def read_analysis_table(path: Path, *, reference: bool) -> pd.DataFrame:
    """Read only when called explicitly; the CLI calls this after release verification."""
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream)
        header = next(reader, [])
    _require(len(header) == len(set(header)), "Duplicate CSV header")
    frame = pd.read_csv(path, dtype={"sample_id": str, "race": str, "sex": str,
                                    "SDMVSTRA": str, "SDMVPSU": str},
                        float_precision="round_trip", keep_default_na=False, na_values=[""])
    return validate_table(frame, reference=reference)


def _write_results(destination: Path, result: dict[str, Any]) -> None:
    _require(not destination.exists(), "Output directory already exists; results are never overwritten")
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "evaluation.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    flattened = []
    for candidate in result["candidate_comparisons"]:
        for record in candidate["estimands"]:
            row = {key: value for key, value in record.items() if key not in ("measured", "generated")}
            row["candidate_labels"] = ";".join(candidate["labels"])
            for source in ("measured", "generated"):
                for key in ("value", "n", "n_complete", "rank", "n_parameters", "status", "reason", "sign"):
                    row[f"{source}_{key}"] = record[source][key]
            flattened.append(row)
    with (destination / "estimands.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(flattened[0]))
        writer.writeheader()
        writer.writerows(flattened)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Explicitly authorize this gated invocation")
    parser.add_argument("--release-manifest", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--initial", type=Path, required=True)
    parser.add_argument("--final", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    if not args.execute:
        parser.error("Evaluation is disabled without --execute; no input files have been read")
    try:
        release = verify_release(args.release_manifest, args.reference, args.initial, args.final)
        reference = read_analysis_table(args.reference, reference=True)
        initial = read_analysis_table(args.initial, reference=False)
        final = read_analysis_table(args.final, reference=False)
        initial_result = compare_tables(reference, initial)
        final_result = compare_tables(reference, final)
        identical = initial.equals(final)
        changed = int((initial["urate"].to_numpy() != final["urate"].to_numpy()).sum())
        comparisons = [{"labels": ["initial", "final"] if identical else ["initial"],
                        "estimands": initial_result}]
        if not identical:
            comparisons.append({"labels": ["final"], "estimands": final_result})
        result = {"schema_version": 1, "protocol": "M15-B1", "limitations": LIMITATIONS,
                  "cohort_n": len(reference), "stratum_n": 50, "estimand_count": 24,
                  "quantile_convention": "linear: h=(n-1)*q, interpolate adjacent order statistics",
                  "sd_ddof": 1, "unique_candidate_tables": 1 if identical else 2,
                  "changed_urate_rows_initial_to_final": changed,
                  "release_manifest_sha256": _sha256(args.release_manifest),
                  "evaluator_sha256": release["evaluator_sha256"],
                  "candidate_comparisons": comparisons,
                  "reference_sensitivity": reference_sensitivity(reference)}
        _write_results(args.output_dir, result)
    except (EvaluationError, OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, f"Evaluation stopped: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
