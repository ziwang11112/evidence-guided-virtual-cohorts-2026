"""Read-only numerical verification for this source-conditioned experiment.

Run only on controller authorization. No generator, harness estimator, reference
data, prior target results, or external evidence is imported or executed. The
source path enumerator is limited to the frozen schedule in this bundle. Target
paths must be supplied explicitly after AUTHOR_SEALED. Reports are exclusive
new files: failed/unavailable results are retained, never overwritten.

Examples (controller authorization is additionally required):
  python independent_verify.py source --candidates initial --out initial_audit.json
  python independent_verify.py target --manifest target_audit_inputs.json --out target_audit.json

Target manifest: {"runs":[{"candidate":"initial","seed":9701,
"output":"<current-bundle CSV>","analysis":"<current-bundle analysis JSON>",
"metric_pointers":{"K02-HDL-BMI":"/path/to/number",
"K02-TC-BMI":"/path/to/number","K02-LIPID-RESIDUAL":"/path/to/number"}}]}.
Paths outside this bundle and unit are rejected. JSON pointers follow RFC6901.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


UNIT = Path(__file__).resolve().parent
BUNDLE = Path("D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcSrcR01").resolve()
ATOL = 1e-10
RTOL = 1e-9
READS: dict[str, str] = {}


def require(ok, message):
    if not bool(ok):
        raise ValueError(message)


def allowed(path):
    path = Path(path).resolve()
    require(path.is_relative_to(BUNDLE) or path.is_relative_to(UNIT),
            f"Outside this experiment's read boundary: {path}")
    return path


def content(path):
    path = allowed(path)
    raw = path.read_bytes()
    READS[str(path)] = hashlib.sha256(raw).hexdigest()
    return raw


def read_json(path):
    return json.loads(content(path).decode("utf-8-sig"))


def frame(path, columns):
    import io
    # Preserve string-valued categories such as parity "0" and identifiers.
    types = {c["name"]: str for c in columns if c["kind"] in {"string", "category"}}
    return pd.read_csv(io.BytesIO(content(path)), dtype=types)


def finite(values, label):
    values = np.asarray(values, dtype=float)
    require(np.isfinite(values).all(), f"Nonfinite {label}; no row deletion performed")
    return values


def compare(actual, expected):
    if expected is None:
        return {"status": "unavailable", "reason": "Pipeline numeric value absent"}
    expected = float(expected)
    require(math.isfinite(expected), "Pipeline value is nonfinite")
    difference = float(actual - expected)
    return {"status": "match" if math.isclose(actual, expected, rel_tol=RTOL, abs_tol=ATOL)
            else "mismatch", "pipeline_value": expected, "difference": difference,
            "atol": ATOL, "rtol": RTOL,
            "interpretation": "Numerical equality tolerance only, not scientific fit"}


def design_info(design):
    singular = np.linalg.svd(design, compute_uv=False)
    tolerance = float(singular[0] * max(design.shape) * np.finfo(float).eps)
    rank = int(np.count_nonzero(singular > tolerance))
    return {"n": len(design), "columns": design.shape[1], "rank": rank,
            "full_rank": rank == design.shape[1], "rank_tolerance": tolerance,
            "singular_min": float(singular[-1]),
            "condition_number": float(singular[0] / singular[-1]) if singular[-1] else None}


def fit_qr_and_fwl(design, outcome, term_index):
    """Two independent algebraic routes, never np.linalg.lstsq/harness code."""
    design = finite(design, "design")
    outcome = finite(outcome, "outcome")
    info = design_info(design)
    require(info["full_rank"] and len(design) > design.shape[1],
            f"Full design rank/df failure: {info}")
    q, r = np.linalg.qr(design, mode="reduced")
    beta = np.linalg.solve(r, q.T @ outcome)
    residual = outcome - q @ (q.T @ outcome)
    nuisance = np.delete(design, term_index, axis=1)
    nuisance_info = design_info(nuisance)
    require(nuisance_info["full_rank"], f"Nuisance rank failure: {nuisance_info}")
    qn, _ = np.linalg.qr(nuisance, mode="reduced")
    x = design[:, term_index]
    xr = x - qn @ (qn.T @ x)
    yr = outcome - qn @ (qn.T @ outcome)
    denominator = float(xr @ xr)
    require(denominator > 0 and math.isfinite(denominator), "Exposure residual variance undefined")
    fwl = float((xr @ yr) / denominator)
    value = float(beta[term_index])
    agreement = compare(value, fwl)
    require(agreement["status"] == "match", "Independent full-design QR and FWL disagree")
    rss = float(residual @ residual)
    return {"value": value, "fwl_value": fwl, "qr_minus_fwl": value - fwl,
            "design": info, "nuisance_design": nuisance_info,
            "residual_sum_squares": rss,
            "residual_df": len(design) - design.shape[1],
            "residualized_exposure_sum_squares": denominator,
            "conventional_ols_se_generated_only": math.sqrt(rss / (len(design) - design.shape[1]) / denominator)}, residual


def table_quality(data, task):
    failures = []
    expected_columns = [c["name"] for c in task["columns"]]
    if list(data.columns) != expected_columns:
        failures.append("Column names/order differ from declared task")
    if len(data) != task["n_rows"]:
        failures.append("Row count differs from declared task")
    summaries = {}
    for column in task["columns"]:
        name = column["name"]
        if name not in data:
            failures.append(f"Missing column: {name}")
            continue
        values = data[name]
        if values.isna().any():
            failures.append(f"Missing values: {name}")
        if column["kind"] in {"number", "integer"}:
            a = values.to_numpy(dtype=float)
            if not np.isfinite(a).all():
                failures.append(f"Nonfinite values: {name}")
                continue
            if column["kind"] == "integer" and not np.equal(a, np.floor(a)).all():
                failures.append(f"Noninteger values: {name}")
            if "minimum" in column and np.any(a < column["minimum"]):
                failures.append(f"Below declared support: {name}")
            if "maximum" in column and np.any(a > column["maximum"]):
                failures.append(f"Above declared support: {name}")
            summaries[name] = {"unit": column["unit"], "mean": float(np.mean(a)),
                               "sample_sd": float(np.std(a, ddof=1)), "min": float(np.min(a)),
                               "max": float(np.max(a)),
                               "q01_q25_q50_q75_q99": np.quantile(a, [.01, .25, .5, .75, .99]).tolist()}
        elif column["kind"] == "category":
            if not values.isin([str(v) for v in column["categories"]]).all():
                failures.append(f"Unknown categories: {name}")
    identifier = data[task["row_id"]]
    if identifier.isna().any() or not identifier.is_unique:
        failures.append("Identifiers are missing or duplicated")
    tc = finite(data["total_cholesterol"], "TC")
    hdl = finite(data["hdl_cholesterol"], "HDL")
    incoherent = int(np.count_nonzero((tc <= 0) | (hdl <= 0) | (tc < hdl)))
    if incoherent:
        failures.append("Positive lipid concentration / TC>=HDL coherence violation")
    return {"status": "pass" if not failures else "failed", "failures": failures,
            "rows": len(data), "unique_ids": int(identifier.nunique()),
            "duplicate_rows_excluding_id": int(data.drop(columns=[task["row_id"]]).duplicated().sum()),
            "incoherent_lipid_rows": incoherent, "minimum_nonhdl": float(np.min(tc - hdl)),
            "summaries": summaries,
            "scope": "Declared support and numerical coherence, not clinical validation"}


def source_design(data, context, spec, operator):
    require(operator["kind"] == "ols_coefficient" and operator["include_intercept"],
            "Prepared verifier supports the declared OLS with intercept")
    require(operator["selection"] == [] and operator["missing_policy"] == "error",
            "Unexpected source selection/missing policy; unavailable rather than substitution")
    units = {c["name"]: c["unit"] for c in context["columns"]}
    require(units[operator["outcome"]] == "mmol/L" and units[operator["term"]] == "1"
            and operator["unit"] == "mmol/L", "Source analysis units differ from prepared mmol/L-per-zBMI audit")
    replacements = {}
    identities = []
    for declaration in context["predictor_checks"]:
        require(declaration["kind"] == "zscore" and declaration["selection"] == []
                and declaration["reference"] == {"mode": "sample", "selection": [], "ddof": 1},
                "Unexpected predictor convention; unavailable rather than substitution")
        raw = finite(data[declaration["raw_column"]], "raw BMI")
        # math.fsum provides an independently accumulated mean and variance.
        mean = math.fsum(map(float, raw)) / len(raw)
        sd = math.sqrt(math.fsum((float(v) - mean) ** 2 for v in raw) / (len(raw) - 1))
        require(sd > 0 and math.isfinite(sd), "Undefined sample zscore reference")
        rebuilt = (raw - mean) / sd
        stored = finite(data[declaration["column"]], "stored standardized BMI")
        max_error = float(np.max(np.abs(rebuilt - stored)))
        require(np.allclose(rebuilt, stored, rtol=1e-9, atol=1e-9), "Stored zscore identity fails")
        replacements[declaration["column"]] = rebuilt
        identities.append({"column": declaration["column"], "raw_column": declaration["raw_column"],
                           "n": len(raw), "reference_mean": mean, "reference_sample_sd": sd,
                           "maximum_absolute_error": max_error, "status": "identity_verified",
                           "original_source_convention": "unresolved; identity is only the declared generated convention"})
    dummy_identity = []
    for name, definition in spec["parameters"]["nuisance_definitions"].items():
        if name not in data:
            continue
        labels = data[name].astype(str)
        categories = list(map(str, definition["categories"]))
        require(labels.isin(categories).all(), f"Unknown nuisance category: {name}")
        counts = {label: int((labels == label).sum()) for label in categories}
        for k, label in enumerate(categories[1:], 1):
            dummy = f"{name}_{k}"
            if dummy not in data:
                continue
            rebuilt = (labels == label).to_numpy(dtype=float)
            require(np.array_equal(rebuilt, finite(data[dummy], dummy)), f"Dummy identity fails: {dummy}")
            replacements[dummy] = rebuilt
        dummy_identity.append({"category": name, "counts": counts, "status": "identity_verified"})
    names = ["intercept", *operator["predictors"]]
    design = np.column_stack([np.ones(len(data)), *[
        replacements[name] if name in replacements else finite(data[name], name)
        for name in operator["predictors"]]])
    require(operator["term"] in replacements, "Exposure lacks independent predictor identity")
    return design, names.index(operator["term"]), identities, dummy_identity


def source_audit(candidates):
    records = []
    for candidate in candidates:
        directory = BUNDLE / "candidates" / candidate
        plan = read_json(directory / "whole_cohort_source_replay_v1.json")
        contexts = {c["id"]: c for c in plan["contexts"]}
        spec = read_json(directory / "model_spec.json")
        evidence = {e["id"]: e for e in read_json(directory / "evidence.json")["items"]}
        for scheduled in plan["schedule"]:
            if scheduled["candidate"] != f"candidates/{candidate}":
                continue
            result = {**scheduled, "scope": "assumption_dependent_source_consistency_only", "checks": []}
            records.append(result)
            destination = BUNDLE / "whole_cohort_source_replays_v1" / scheduled["replay_id"]
            try:
                pipeline = read_json(destination / "replay.json")
                result["pipeline_status"] = pipeline["status"]
                result["pipeline_error"] = pipeline["context"]["error"]
                if pipeline["status"] != "success":
                    result.update(status="unavailable", reason="Pipeline source replay failed; retained without rerun")
                    continue
                context = contexts[scheduled["context_id"]]
                task = read_json(destination / "bundle/task.json")
                require(task["columns"] == context["columns"] and task["n_rows"] == scheduled["n_rows"],
                        "Source task/schema mismatch")
                data = frame(destination / "bundle/executions/replay/output/generated.csv", context["columns"])
                result["quality"] = table_quality(data, task)
                recipe = read_json(directory / context["recipe"]["path"])
                assumed = {r["check_id"]: r for r in pipeline["context"]["assumed_diagnostics"]}
                strict_rows = {r["id"]: r for r in (pipeline["context"].get("strict_feedback") or {}).get("checks", [])}
                for check in recipe["checks"]:
                    item = {"check_id": check["id"], "evidence_id": check["evidence_id"]}
                    result["checks"].append(item)
                    try:
                        operator = check["operator"]
                        design, index, zchecks, dummies = source_design(data, context, spec, operator)
                        numerical, _ = fit_qr_and_fwl(design, data[operator["outcome"]], index)
                        published = evidence[check["evidence_id"]]
                        pipe = assumed.get(check["id"], {})
                        pipe_value = (pipe.get("calculation") or {}).get("value")
                        equality = compare(numerical["value"], pipe_value)
                        item.update(status="computed", numerical=numerical, pipeline_comparison=equality,
                                    zscore_checks=zchecks, category_dummy_checks=dummies,
                                    operator=operator, reported_value=published["estimate"],
                                    reported_uncertainty=published["uncertainty"],
                                    difference_from_reported=numerical["value"] - published["estimate"],
                                    source_unit="mmol/L per generated within-context sample SD of BMI",
                                    raw_bmi_slope_mmol_L_per_kg_m2=numerical["value"] / zchecks[0]["reference_sample_sd"],
                                    outcome_conversion_factor=1.0,
                                    pipeline_strict_semantic_status=pipe.get("strict_semantic_status"),
                                    pipeline_strict_unavailable_reason=pipe.get("strict_unavailable_reason"),
                                    strict_record=strict_rows.get(check["id"]),
                                    interpretation="Reported comparison is assumption-dependent; no clinical-fit threshold or source interval acceptance rule")
                    except Exception as error:
                        item.update(status="unavailable", error_type=type(error).__name__, reason=str(error))
                all_equal = all(c.get("pipeline_comparison", {}).get("status") == "match" for c in result["checks"])
                result["status"] = "verified" if all_equal and result["quality"]["status"] == "pass" else "failed_or_unavailable"
            except Exception as error:
                result.update(status="unavailable", error_type=type(error).__name__, reason=str(error))
    return records


def pointer(document, path):
    require(isinstance(path, str) and path.startswith("/"), "Explicit JSON pointer required")
    value = document
    for part in path[1:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def target_audit(manifest, seal):
    require(allowed(seal).is_file(), "AUTHOR_SEALED is required before any target-output read")
    content(seal)
    task = read_json(BUNDLE / "task.json")
    units = {c["name"]: c["unit"] for c in task["columns"]}
    require(units["bmi"] == "kg/m^2" and units["total_cholesterol"] == "mmol/L"
            and units["hdl_cholesterol"] == "mmol/L", "Unexpected target units")
    runs = read_json(manifest)["runs"]
    protocol = read_json(UNIT / "PROTOCOL.json")
    require(len(runs) <= protocol["target_table_cap_all_alternatives"], "Target audit exceeds protocol table cap")
    records = []
    seen = set()
    for run in runs:
        key = (run["candidate"], run["seed"])
        require(key not in seen and run["candidate"] in protocol["candidate_names"]
                and run["seed"] in protocol["target_seeds"], "Unexpected or duplicate target run")
        seen.add(key)
        result = {"candidate": run["candidate"], "seed": run["seed"],
                  "scope": "generated_only_description_no_reference", "output": str(allowed(run["output"]))}
        records.append(result)
        try:
            data = frame(run["output"], task["columns"])
            result["quality"] = table_quality(data, task)
            require(result["quality"]["status"] == "pass", "Table quality failure; no row repair or exclusion")
            age = finite(data["age"], "age")
            bmi = finite(data["bmi"], "BMI")
            sex = data["sex"].astype(str)
            require(np.all(age >= 18) and sex.isin(["F", "M"]).all(), "Target eligibility failure; no exclusion")
            design = np.column_stack([np.ones(len(data)), age, (sex == "M").to_numpy(dtype=float), bmi])
            outcomes = {"K02-HDL-BMI": "hdl_cholesterol", "K02-TC-BMI": "total_cholesterol"}
            values, fits, residuals = {}, {}, {}
            for analysis_id, column in outcomes.items():
                mmol = finite(data[column], column)
                fitted, residual = fit_qr_and_fwl(design, mmol * 38.67, 3)
                raw_fitted, _ = fit_qr_and_fwl(design, mmol, 3)
                values[analysis_id] = fitted["value"] * 5.0
                fits[analysis_id] = {**fitted, "value_per_5_kg_m2": values[analysis_id],
                                     "unit": "mg/dL per 5 kg/m^2", "outcome_mmol_L_to_mg_dL": 38.67,
                                     "bmi_contrast_kg_m2": 5.0,
                                     "unit_conversion_check": compare(values[analysis_id], raw_fitted["value"] * 38.67 * 5)}
                residuals[column] = residual - np.mean(residual)
            tc_r, hdl_r = residuals["total_cholesterol"], residuals["hdl_cholesterol"]
            denominator = math.sqrt(float(tc_r @ tc_r) * float(hdl_r @ hdl_r))
            require(denominator > 0 and math.isfinite(denominator), "Residual correlation undefined")
            correlation = float((tc_r @ hdl_r) / denominator)
            require(-1 - ATOL <= correlation <= 1 + ATOL, "Residual correlation outside support")
            values["K02-LIPID-RESIDUAL"] = correlation
            pipeline = read_json(run["analysis"])
            comparisons = {}
            for analysis_id, value in values.items():
                try:
                    comparisons[analysis_id] = compare(value, pointer(pipeline, run["metric_pointers"][analysis_id]))
                except Exception as error:
                    comparisons[analysis_id] = {"status": "unavailable", "reason": str(error)}
            result.update(status="verified" if all(x["status"] == "match" for x in comparisons.values()) else "failed_or_unavailable",
                          values=values, fits=fits, pipeline_comparisons=comparisons,
                          residual_correlation={"value": correlation, "unit": "1", "paired_n": len(data),
                          "adjustment": ["intercept", "age", "sex_M", "bmi"],
                          "residual_sd_tc_mg_dL": float(np.std(tc_r, ddof=1)),
                          "residual_sd_hdl_mg_dL": float(np.std(hdl_r, ddof=1))})
        except Exception as error:
            result.update(status="unavailable", error_type=type(error).__name__, reason=str(error))
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["source", "target"])
    parser.add_argument("--candidates", nargs="+", choices=["initial", "revised"], default=["initial", "revised"])
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--author-seal", type=Path, default=UNIT / "AUTHOR_SEALED")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    output = allowed(args.out if args.out.is_absolute() else UNIT / args.out)
    require(output.is_relative_to(UNIT), "Verifier reports belong only in this unit")
    require(not output.exists(), "Report exists; use a new filename to preserve all failures")
    report = {"schema_version": 1, "mode": args.mode,
              "created_utc": datetime.now(timezone.utc).isoformat(),
              "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "independence": "No generator execution; no pipeline estimator imports; full-design QR and FWL; regenerated indicators and zBMI",
              "limitations": ["Source law, measurement, source standardization, weighting and transport assumptions are not validated",
                              "Repeated rows/seeds are numerical evaluations, not new clinical evidence",
                              "No reference data or original/old target outputs read",
                              "Numerical agreement is not patient validation or an overall quality-gain claim"]}
    try:
        if args.mode == "source":
            report["records"] = source_audit(args.candidates)
        else:
            require(args.manifest is not None, "Target mode needs an explicit current-experiment manifest")
            report["records"] = target_audit(args.manifest, args.author_seal)
        records = report["records"]
        report["status"] = "verified" if records and all(r["status"] == "verified" for r in records) else "failed_or_unavailable"
        report["summary"] = {"records": len(records), "verified": sum(r["status"] == "verified" for r in records),
                             "failed_or_unavailable": sum(r["status"] != "verified" for r in records),
                             "source_slope_comparisons": sum(len(r.get("checks", [])) for r in records)}
    except Exception as error:
        report.update(status="unavailable", error_type=type(error).__name__, reason=str(error))
    report["read_artifact_sha256"] = READS
    with output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2, allow_nan=False)
        handle.write("\n")
    print(json.dumps({"report": str(output), "status": report["status"], "summary": report.get("summary")}, indent=2))
    return 0 if report["status"] == "verified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
