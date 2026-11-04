"""Independent conditional-GLS arithmetic check for the native HRS lme4 fit.

This does not fit variance components, regenerate data, or call R.  Its only
scientific input is the same final CSV plus the native evaluator's fitted
variance components and fixed-effect estimates.  --self-test uses invented
arrays only and creates no data file.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


TERMS = [
    "(Intercept)", "age60", "hba1c_U65", "hba1c_O65", "raceBlack",
    "educHS", "educLessThanHS", "sexMale", "cses",
    "age60:hba1c_U65", "age60:hba1c_O65", "age60:raceBlack",
    "age60:educHS", "age60:educLessThanHS", "age60:sexMale", "age60:cses",
]
REQUIRED = [
    "id", "subject_id", "visit_time", "baseline_age", "age", "age60",
    "sex", "race", "educ", "cses", "hba1c", "mem_s",
]
NUMERIC = ["visit_time", "baseline_age", "age", "age60", "cses", "hba1c", "mem_s"]
TIMES = (0.0, 2.0, 4.0, 6.0)
ATOL = 2e-8
RTOL = 2e-7


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict]:
    """Read, validate, and return a generated table; never print records."""
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        names = reader.fieldnames or []
        if len(names) != len(set(names)):
            raise ValueError("Duplicate CSV column names")
        if not set(REQUIRED).issubset(names):
            raise ValueError("Missing required CSV columns")
        rows = []
        for row in reader:
            if None in row:
                raise ValueError("Malformed CSV row")
            item = {key: row[key] for key in REQUIRED}
            for key in NUMERIC:
                try:
                    value = float(item[key])
                except (TypeError, ValueError):
                    raise ValueError(f"Non-numeric value in {key}") from None
                if not math.isfinite(value):
                    raise ValueError(f"Non-finite value in {key}")
                item[key] = value
            rows.append(item)
    validate_rows(rows)
    return rows


def validate_rows(rows: list[dict]) -> None:
    if not rows:
        raise ValueError("Empty input")
    ids = [r["id"] for r in rows]
    if any(not isinstance(v, str) or not v.strip() for v in ids):
        raise ValueError("Empty visit identifier")
    if len(set(ids)) != len(ids):
        raise ValueError("Visit identifiers are not unique")
    groups = defaultdict(list)
    for row in rows:
        if not isinstance(row["subject_id"], str) or not row["subject_id"].strip():
            raise ValueError("Empty subject identifier")
        if any(not math.isfinite(float(row[k])) for k in NUMERIC):
            raise ValueError("Non-finite numeric input")
        if row["sex"] not in ("female", "male"):
            raise ValueError("Sex must use female/male canonical values")
        if row["race"] not in ("white", "black"):
            raise ValueError("Race must use white/black canonical values")
        if row["educ"] not in ("College", "HS", "LessThanHS"):
            raise ValueError("Unexpected education category")
        if row["hba1c"] <= 0:
            raise ValueError("HbA1c must be positive")
        if not math.isclose(row["age"], row["baseline_age"] + row["visit_time"], rel_tol=0, abs_tol=1e-8):
            raise ValueError("Age does not equal baseline age plus visit time")
        if not math.isclose(row["age60"], (row["age"] - 60.0) / 10.0, rel_tol=0, abs_tol=1e-8):
            raise ValueError("age60 does not equal (age - 60)/10")
        groups[row["subject_id"]].append(row)
    for group in groups.values():
        if len(group) != 4 or tuple(sorted(r["visit_time"] for r in group)) != TIMES:
            raise ValueError("Each subject must have visits at 0, 2, 4, 6 years")
        first = group[0]
        for row in group[1:]:
            if any(row[k] != first[k] for k in ("sex", "race", "educ")):
                raise ValueError("Subject categorical covariate varies between visits")
            if any(not math.isclose(row[k], first[k], rel_tol=0, abs_tol=1e-10)
                   for k in ("baseline_age", "cses", "hba1c")):
                raise ValueError("Subject baseline covariate varies between visits")


def design(rows: list[dict]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Construct treatment-coded design without using the native R matrix."""
    age = np.asarray([r["age60"] for r in rows], dtype=float)
    hba = np.asarray([r["hba1c"] for r in rows], dtype=float) - 6.5
    base = np.column_stack([
        np.minimum(hba, 0), np.maximum(hba, 0),
        [r["race"] == "black" for r in rows],
        [r["educ"] == "HS" for r in rows],
        [r["educ"] == "LessThanHS" for r in rows],
        [r["sex"] == "male" for r in rows],
        [r["cses"] for r in rows],
    ])
    x = np.column_stack([np.ones(len(rows)), age, base, age[:, None] * base])
    z = np.column_stack([np.ones(len(rows)), age])
    y = np.asarray([r["mem_s"] for r in rows], dtype=float)
    subjects = np.asarray([r["subject_id"] for r in rows])
    return x, z, y, subjects


def validate_variances(g: np.ndarray, residual: float) -> None:
    if g.shape != (2, 2) or not np.isfinite(g).all():
        raise ValueError("Random-effect covariance must be finite 2 by 2")
    if not math.isfinite(residual) or residual <= 0:
        raise ValueError("Residual variance must be finite and positive")
    scale = max(1.0, float(np.abs(g).max()))
    if not np.allclose(g, g.T, rtol=0, atol=1e-10 * scale):
        raise ValueError("Random-effect covariance is not symmetric")
    if np.linalg.eigvalsh(g).min() < -1e-10 * scale:
        raise ValueError("Random-effect covariance is not positive semidefinite")


def block_gls(x: np.ndarray, z: np.ndarray, y: np.ndarray,
              subjects: np.ndarray, g: np.ndarray, residual: float) -> dict:
    """Accumulate X'V^-1X and X'V^-1y in four-visit subject blocks."""
    validate_variances(g, residual)
    if x.shape != (len(y), 16) or z.shape != (len(y), 2):
        raise ValueError("Unexpected design dimensions")
    if len(subjects) != len(y) or not all(np.isfinite(a).all() for a in (x, z, y)):
        raise ValueError("Invalid design or response")
    groups = defaultdict(list)
    for index, subject in enumerate(subjects):
        groups[str(subject)].append(index)
    information = np.zeros((16, 16), dtype=float)
    rhs = np.zeros(16, dtype=float)
    for indices in groups.values():
        if len(indices) != 4:
            raise ValueError("GLS cross-check requires four visits per subject")
        xi, zi, yi = x[indices], z[indices], y[indices]
        vi = zi @ g @ zi.T + residual * np.eye(4)
        chol = np.linalg.cholesky(vi)
        whitened_x = np.linalg.solve(chol, xi)
        whitened_y = np.linalg.solve(chol, yi)
        information += whitened_x.T @ whitened_x
        rhs += whitened_x.T @ whitened_y
    information = (information + information.T) / 2.0
    chol_info = np.linalg.cholesky(information)
    estimate = np.linalg.solve(chol_info.T, np.linalg.solve(chol_info, rhs))
    inverse_chol = np.linalg.solve(chol_info, np.eye(16))
    covariance = inverse_chol.T @ inverse_chol
    se = np.sqrt(np.diag(covariance))
    return {
        "estimate": estimate, "se": se, "covariance": covariance,
        "information_condition_number": float(np.linalg.cond(information)),
        "subjects": len(groups), "rows": len(y),
    }


def compare(rows: list[dict], native: dict, atol: float = ATOL, rtol: float = RTOL) -> dict:
    validate_rows(rows)
    if not math.isfinite(atol) or not math.isfinite(rtol) or atol < 0 or rtol < 0:
        raise ValueError("Invalid comparison tolerances")
    entries = native.get("fixed_effects", [])
    if len(entries) != 16 or {x.get("term") for x in entries} != set(TERMS):
        raise ValueError("Native fit must supply exactly the 16 expected fixed-effect terms")
    native_terms = {x["term"]: x for x in entries}
    for item in entries:
        if not all(math.isfinite(float(item[k])) for k in ("estimate", "se")) or float(item["se"]) < 0:
            raise ValueError("Invalid native fixed-effect estimate/SE")
    labels = native.get("random_effect_covariance_terms", ["(Intercept)", "age60"])
    if labels != ["(Intercept)", "age60"]:
        raise ValueError("Unexpected random-effect covariance order")
    g = np.asarray(native["random_effect_covariance"], dtype=float)
    residual = float(native["residual_variance"])
    x, z, y, subjects = design(rows)
    result = block_gls(x, z, y, subjects, g, residual)
    effects = []
    for index, term in enumerate(TERMS):
        expected = native_terms[term]
        estimate = float(result["estimate"][index])
        se = float(result["se"][index])
        estimate_difference = estimate - float(expected["estimate"])
        se_difference = se - float(expected["se"])
        effects.append({
            "term": term, "gls_estimate": estimate, "native_estimate": float(expected["estimate"]),
            "estimate_difference": estimate_difference, "gls_se": se,
            "native_se": float(expected["se"]), "se_difference": se_difference,
            "estimate_matches": math.isclose(estimate, float(expected["estimate"]), abs_tol=atol, rel_tol=rtol),
            "se_matches": math.isclose(se, float(expected["se"]), abs_tol=atol, rel_tol=rtol),
        })
    return {
        "schema_version": "hrs_conditional_gls_v1",
        "status": "pass" if all(v["estimate_matches"] and v["se_matches"] for v in effects) else "mismatch",
        "comparison_tolerances": {"absolute": atol, "relative": rtol},
        "n_rows": result["rows"], "n_subjects": result["subjects"],
        "fixed_effects": effects,
        "maximum_absolute_estimate_difference": max(abs(v["estimate_difference"]) for v in effects),
        "maximum_absolute_se_difference": max(abs(v["se_difference"]) for v in effects),
        "information_condition_number": result["information_condition_number"],
        "random_effect_covariance": g.tolist(),
        "random_effect_covariance_terms": ["(Intercept)", "age60"],
        "residual_variance": residual,
        "method": "Independent treatment-coded design; per-subject 4x4 covariance whitening; conditional GLS and inverse information SE.",
        "scope": "Conditional on the native fitted variance components; not an independent REML optimizer, variance-component validation, source reconstruction, or biological validation.",
        "new_generated_rows": 0,
    }


def self_test() -> dict:
    """A deterministic invented design, compared with a separate dense solve."""
    rng = np.random.default_rng(20261103)
    rows = []
    for i in range(48):
        baseline = 51 + (i * 7) % 39 + rng.uniform(-0.2, 0.2)
        cses = rng.normal(0, 0.7)
        hba = 5.2 + (i % 8) * 0.4 + rng.uniform(-0.08, 0.08)
        for j, time in enumerate(TIMES):
            rows.append({
                "id": f"toy_{i}_{j}", "subject_id": f"toy_{i}", "visit_time": time,
                "baseline_age": baseline, "age": baseline + time,
                "age60": (baseline + time - 60) / 10,
                "sex": "male" if i % 5 in (0, 2) else "female",
                "race": "black" if i % 7 in (0, 3, 5) else "white",
                "educ": ("College", "HS", "LessThanHS")[(i // 2) % 3],
                "cses": cses, "hba1c": hba, "mem_s": 0.0,
            })
    validate_rows(rows)
    x, z, _, subjects = design(rows)
    known_beta = np.linspace(-0.15, 0.27, 16)
    y = x @ known_beta + rng.normal(0, 0.3, len(rows))
    for row, value in zip(rows, y):
        row["mem_s"] = float(value)
    g = np.array([[0.4, -0.025], [-0.025, 0.06]])
    residual = 0.12
    # Dense construction does not call the block accumulator.
    same_subject = subjects[:, None] == subjects[None, :]
    dense_v = (z @ g @ z.T) * same_subject + residual * np.eye(len(y))
    inv_v_x = np.linalg.solve(dense_v, x)
    dense_information = x.T @ inv_v_x
    dense_cov = np.linalg.inv(dense_information)
    dense_beta = np.linalg.solve(dense_information, x.T @ np.linalg.solve(dense_v, y))
    native = {
        "fixed_effects": [{"term": term, "estimate": float(dense_beta[k]), "se": float(np.sqrt(dense_cov[k, k]))} for k, term in enumerate(TERMS)],
        "random_effect_covariance": g.tolist(), "residual_variance": residual,
    }
    checked = compare(rows, native, atol=1e-10, rtol=1e-10)
    if checked["status"] != "pass":
        raise AssertionError("Block and dense GLS arithmetic disagree")
    # A coding/term perturbation must not silently pass the comparison.
    changed = json.loads(json.dumps(native))
    changed["fixed_effects"][9]["estimate"] += 0.01
    if compare(rows, changed)["status"] != "mismatch":
        raise AssertionError("Known fixed-effect perturbation was not detected")
    bad_rows = [dict(r) for r in rows]
    bad_rows[0]["age60"] += 0.1
    try:
        validate_rows(bad_rows)
    except ValueError:
        pass
    else:
        raise AssertionError("Age-scale inconsistency was not rejected")
    bad_native = dict(native, random_effect_covariance=[[0.1, 0.8], [0.8, 0.1]])
    try:
        compare(rows, bad_native)
    except ValueError:
        pass
    else:
        raise AssertionError("Indefinite random-effect covariance was not rejected")
    reference_rows = [dict(rows[0], id=f"reference_{i}", subject_id="reference", visit_time=t,
                           age=60+t, baseline_age=60, age60=t/10,
                           sex="female", race="white", educ="College", cses=0, hba1c=6.5)
                      for i, t in enumerate(TIMES)]
    rx, _, _, _ = design(reference_rows)
    if not np.array_equal(rx[0], np.array([1.0] + [0.0] * 15)):
        raise AssertionError("Reference coding or hinge origin is wrong")
    return {"status": "pass", "invented_subjects": 48, "invented_rows": 192,
            "checks": ["block_vs_dense_all_16_coefficients_and_SEs", "known_coefficient_mismatch",
                       "age_scale_rejection", "indefinite_covariance_rejection", "reference_factor_and_hinge_origin"],
            "maximum_absolute_estimate_difference": checked["maximum_absolute_estimate_difference"],
            "maximum_absolute_se_difference": checked["maximum_absolute_se_difference"],
            "clinical_inputs_read": 0, "files_created": 0}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-csv", type=Path)
    parser.add_argument("--native-json", type=Path)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        if any(v is not None for v in (args.input_csv, args.native_json, args.output_json)):
            parser.error("--self-test does not accept file arguments")
        print(json.dumps(self_test(), indent=2))
        return 0
    if any(v is None for v in (args.input_csv, args.native_json, args.output_json)):
        parser.error("Specify --input-csv, --native-json and --output-json")
    if args.output_json.resolve() in (args.input_csv.resolve(), args.native_json.resolve()):
        parser.error("Output must not overwrite an input")
    if args.output_json.exists():
        parser.error("Output already exists; preserve prior review artifact")
    try:
        rows = read_csv(args.input_csv)
        native = json.loads(args.native_json.read_text(encoding="utf-8-sig"))
        if native.get("input_sha256") != sha256(args.input_csv):
            raise ValueError("Native input_sha256 does not bind the same CSV")
        result = compare(rows, native)
    except (ValueError, KeyError, TypeError, np.linalg.LinAlgError) as exc:
        result = {"schema_version": "hrs_conditional_gls_v1", "status": "unavailable",
                  "error_type": type(exc).__name__, "error": str(exc),
                  "new_generated_rows": 0}
    result["created_utc"] = datetime.now(timezone.utc).isoformat()
    result["inputs"] = {
        "generated_csv_sha256": sha256(args.input_csv),
        "native_fit_json_sha256": sha256(args.native_json),
        "crosscheck_code_sha256": sha256(Path(__file__)),
    }
    result["runtime"] = {"python": sys.version.split()[0], "numpy": np.__version__}
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "output": str(args.output_json)}))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
