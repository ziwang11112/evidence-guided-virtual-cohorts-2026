"""Independent M17-B audit. No reference access occurs on import or self-check.

Fits use statsmodels formula OLS and HC3. All effects are prediction contrasts
constructed by patsy, independently of the custodian's array evaluator.
Only an explicitly released manifest permits real-table reads.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
from pathlib import Path

import numpy as np
import pandas as pd
import patsy
import statsmodels
import statsmodels.formula.api as smf

AUTHORIZATION = "root_releases_all_frozen_outputs_for_one_target_evaluation"
ENDPOINTS = ["adjusted_bmi", "adjusted_age", "adjusted_sex", "bmi_curvature",
             "bmi_sex_interaction", "male_bmi", "female_bmi", "reverse_urate"]
SEEDS = {17111, 17112, 17113}
Z95 = 1.959963984540054
FORMULAS = {
    "linear": "urate ~ x + a + female",
    "curved": "urate ~ x + I(x ** 2) + a + female",
    "interaction": "urate ~ x * female + a",
    "reverse": "bmi ~ urate + a + female",
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def binding(path):
    path = Path(path).resolve()
    return {"path": str(path), "sha256": digest(path)}


def snapshot(output, directories, files):
    """Only run on explicitly permitted, finished artifacts before release."""
    if Path(output).exists():
        raise ValueError("Refusing to replace a prior artifact snapshot")
    trees, bindings = [], []
    for directory in directories:
        root = Path(directory).resolve()
        if not root.is_dir():
            raise ValueError(f"Not a directory: {root}")
        paths = sorted(p for p in root.rglob("*") if p.is_file())
        trees.append({"path": str(root), "relative_files": [p.relative_to(root).as_posix() for p in paths]})
        bindings.extend(binding(p) for p in paths)
    bindings.extend(binding(p) for p in files)
    result = {"purpose": "pre-release artifact integrity only; no real outcome reads",
              "directories": trees, "artifacts": bindings}
    write_json(output, result)
    return {"files": len(bindings), "directories": len(trees), "snapshot_sha256": digest(output)}


def check_bindings(bindings):
    checked = {}
    for entry in bindings:
        path = str(Path(entry["path"]).resolve())
        expected = entry["sha256"].lower()
        if path in checked and checked[path] != expected:
            raise ValueError(f"Conflicting hash commitments: {path}")
        actual = digest(path)
        if actual != expected:
            raise ValueError(f"SHA-256 mismatch: {path}")
        checked[path] = actual
    return checked


def check_snapshot(value):
    hashes = check_bindings(value["artifacts"])
    for tree in value.get("directories", []):
        root = Path(tree["path"])
        actual = sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())
        if actual != sorted(tree["relative_files"]):
            raise ValueError(f"Artifact directory membership changed: {root}")
    return hashes


def validate_frame(frame):
    columns = ["sample_id", "age", "female", "bmi", "urate"]
    if list(frame.columns) != columns:
        raise ValueError("Expected exactly sample_id, age, female, bmi, urate, in that order")
    if len(frame) != 320 or frame.sample_id.isna().any() or frame.sample_id.duplicated().any():
        raise ValueError("Expected 320 unique nonmissing identifiers")
    if frame.sample_id.astype(str).str.strip().eq("").any():
        raise ValueError("Empty identifier")
    values = frame[columns[1:]].to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("Missing or nonfinite value; no silent complete-case deletion")
    if not ((frame.age >= 20) & (frame.age <= 79) & (frame.age == np.floor(frame.age))).all():
        raise ValueError("Task requires integer age 20 through 79")
    if not frame.female.isin([0, 1]).all() or not frame.bmi.gt(0).all() or not frame.urate.ge(0).all():
        raise ValueError("Invalid female, BMI, or urate domain")
    cells = [{"female": sex, "age_lo": lo, "age_hi_exclusive": lo + 15,
              "n": int(((frame.female == sex) & (frame.age >= lo) & (frame.age < lo + 15)).sum())}
             for sex in (0, 1) for lo in (20, 35, 50, 65)]
    if any(c["n"] != 40 for c in cells):
        raise ValueError(f"Quota mismatch: {cells}")
    return cells


def point(x=0.0, a=0.0, female=0.0, urate=5.0):
    return {"x": x, "a": a, "female": female, "urate": urate}


def prediction_contrast(fit, points, weights):
    # Rebuild this numeric-only RHS with patsy instead of relying on the
    # statsmodels version's internal formula metadata representation.
    matrix = patsy.dmatrix(fit.model.formula.split("~", 1)[1], pd.DataFrame(points), return_type="dataframe")
    matrix = matrix.loc[:, fit.params.index]
    contrast = np.asarray(weights, dtype=float) @ np.asarray(matrix)
    test = fit.t_test(contrast, use_t=False)
    estimate, se = float(np.asarray(test.effect).item()), float(np.asarray(test.sd).item())
    if not np.isfinite([estimate, se]).all():
        raise ValueError("Nonfinite HC3 contrast")
    return {"estimate": estimate, "se_hc3": se,
            "ci95_lo": estimate - Z95 * se, "ci95_hi": estimate + Z95 * se}


def endpoints(frame):
    data = frame.assign(x=(frame.bmi - 27.5) / 5, a=(frame.age - 50) / 10)
    fitted, failures = {}, {}
    for key, formula in FORMULAS.items():
        try:
            model = smf.ols(formula, data=data, missing="raise")
            if np.linalg.matrix_rank(model.exog) != model.exog.shape[1]:
                raise ValueError("Rank-deficient model")
            fit = model.fit(cov_type="HC3", use_t=False)
            if np.max(fit.get_influence().hat_matrix_diag) >= 1 - 1e-10:
                raise ValueError("HC3 leverage too close to one")
            fitted[key] = fit
        except Exception as exc:
            failures[key] = {"error_type": type(exc).__name__, "message": str(exc)}
    recipes = {
        "adjusted_bmi": ("linear", [point(x=1), point()], [1, -1]),
        "adjusted_age": ("linear", [point(a=1), point()], [1, -1]),
        "adjusted_sex": ("linear", [point(female=1), point()], [1, -1]),
        "bmi_curvature": ("curved", [point(x=1.5), point(x=.5), point(x=-.5)], [1, -2, 1]),
        "bmi_sex_interaction": ("interaction", [point(x=1, female=1), point(female=1),
                                                 point(x=1), point()], [1, -1, -1, 1]),
        "male_bmi": ("interaction", [point(x=1), point()], [1, -1]),
        "female_bmi": ("interaction", [point(x=1, female=1), point(female=1)], [1, -1]),
        "reverse_urate": ("reverse", [point(urate=6), point(urate=5)], [1, -1]),
    }
    results = {}
    for name, (model, points, weights) in recipes.items():
        try:
            if model not in fitted:
                raise ValueError(f"Model failed: {failures[model]}")
            results[name] = prediction_contrast(fitted[model], points, weights)
        except Exception as exc:
            results[name] = {"status": "failed", "error_type": type(exc).__name__, "message": str(exc)}
    return results, failures


def diagnostics(frame):
    summaries = []
    for label, subset in (("overall", frame), ("male", frame.loc[frame.female == 0]),
                          ("female", frame.loc[frame.female == 1])):
        for variable in ("bmi", "urate"):
            values = subset[variable]
            q = values.quantile([.1, .5, .9], interpolation="linear")
            summaries.append({"group": label, "variable": variable, "n": int(values.size),
                              "mean": float(values.mean()), "sd": float(values.std(ddof=1)),
                              "p10": float(q.loc[.1]), "p50": float(q.loc[.5]), "p90": float(q.loc[.9])})
    pearson = {}
    for left, right in (("age", "bmi"), ("bmi", "urate")):
        value = frame[left].corr(frame[right], method="pearson")
        pearson[f"{left}__{right}"] = float(value) if np.isfinite(value) else None
    return {"summaries": summaries, "pearson": pearson}


def analyze(path):
    frame = pd.read_csv(path, dtype={"sample_id": str})
    cells = validate_frame(frame)
    effects, failures = endpoints(frame)
    return {"path": str(Path(path).resolve()), "sha256": digest(path), "n": len(frame),
            "cells": cells, "endpoints": effects, "diagnostics": diagnostics(frame), "failed_models": failures}


def numerical_comparison(actual, reported, label, records):
    """Compare every requested field; absence is a discrepancy, never dropped."""
    if isinstance(actual, dict):
        if not isinstance(reported, dict):
            records.append({"field": label, "status": "missing_or_wrong_type"}); return
        for key, value in actual.items():
            numerical_comparison(value, reported.get(key), f"{label}.{key}", records)
    elif isinstance(actual, list):
        if not isinstance(reported, list) or len(actual) != len(reported):
            records.append({"field": label, "status": "list_length_mismatch"}); return
        for i, (left, right) in enumerate(zip(actual, reported)):
            numerical_comparison(left, right, f"{label}[{i}]", records)
    elif isinstance(actual, (int, float)) and not isinstance(actual, bool):
        good = isinstance(reported, (int, float)) and math.isclose(actual, reported, rel_tol=1e-8, abs_tol=1e-10)
        records.append({"field": label, "status": "match" if good else "mismatch",
                        "independent": actual, "reported": reported,
                        "absolute_difference": abs(actual - reported) if isinstance(reported, (int, float)) else None})
    else:
        records.append({"field": label, "status": "match" if actual == reported else "mismatch",
                        "independent": actual, "reported": reported})


def identity(item):
    return (item["builder"], item["stage"], item["seed"], item["route"])


def audit(release_path, reported_path, snapshot_path, output):
    release_path, reported_path, snapshot_path, output = map(Path, (release_path, reported_path, snapshot_path, output))
    # Before this gate, only the named root release manifest is read.
    release = load_json(release_path)
    if release.get("authorization") != AUTHORIZATION:
        raise ValueError("Root has not explicitly released frozen outputs for target evaluation")
    if not release.get("endpoint_exposure_classification_sha256"):
        raise ValueError("Missing prospective endpoint exposure commitment")
    if release["endpoint_exposure_classification"]["sha256"] != release["endpoint_exposure_classification_sha256"]:
        raise ValueError("Conflicting endpoint exposure commitments")
    if output.exists():
        raise ValueError("Refusing to overwrite an audit result")
    bindings = [release[k] for k in ("protocol", "evaluator", "reference", "endpoint_exposure_classification")]
    bindings += release["generated_tables"] + release.get("frozen_artifacts", [])
    bindings += [binding(release_path), binding(reported_path), binding(snapshot_path), binding(__file__)]
    before = check_bindings(bindings)
    artifact_snapshot = load_json(snapshot_path)
    snapshot_before = check_snapshot(artifact_snapshot)
    reported = load_json(reported_path)
    items = release["generated_tables"]
    keys = [identity(item) for item in items]
    if len(keys) != len(set(keys)):
        raise ValueError("Repeated builder/stage/seed/route identity")
    schedule_issues = []
    for builder in sorted({i["builder"] for i in items}):
        for stage in ("initial", "final"):
            group = [i for i in items if i["builder"] == builder and i["stage"] == stage]
            if not group:
                schedule_issues.append(f"Missing {builder}/{stage}"); continue
            routes = {i["route"] for i in group}
            if len(routes) != 1:
                schedule_issues.append(f"Mixed routes for {builder}/{stage}")
            elif routes == {"program"} and {i["seed"] for i in group} != SEEDS:
                schedule_issues.append(f"Wrong analytical seed set for {builder}/{stage}")
            elif routes != {"program"} and len(group) != 1:
                schedule_issues.append(f"Direct table counted as repeated realizations for {builder}/{stage}")
    reference = analyze(release["reference"]["path"])
    generated, failed, cache = [], [], {}
    for item in items:
        meta = {key: item[key] for key in ("builder", "stage", "seed", "route")}
        path = str(Path(item["path"]).resolve())
        try:
            if path not in cache:
                cache[path] = analyze(path)
            generated.append({**cache[path], **meta})
        except Exception as exc:
            failed.append({**meta, "path": path, "error_type": type(exc).__name__, "message": str(exc)})
    comparisons = []
    for generated_item in generated:
        meta = {k: generated_item[k] for k in ("builder", "stage", "seed", "route")}
        for endpoint in ENDPOINTS:
            real, gen = reference["endpoints"][endpoint], generated_item["endpoints"][endpoint]
            if "estimate" not in real or "estimate" not in gen:
                failed.append({**meta, "endpoint": endpoint, "error_type": "endpoint_failed"}); continue
            comparisons.append({**meta, "endpoint": endpoint, "generated_estimate": gen["estimate"],
                "reference_estimate": real["estimate"], "reference_se_hc3": real["se_hc3"],
                "reference_ci95_lo": real["ci95_lo"], "reference_ci95_hi": real["ci95_hi"],
                "generated_minus_reference": gen["estimate"] - real["estimate"],
                "reference_interval_spans_zero": real["ci95_lo"] <= 0 <= real["ci95_hi"],
                "point_sign_agreement": bool(np.sign(gen["estimate"]) == np.sign(real["estimate"]))})
    comparison = pd.DataFrame(comparisons)
    paired = []
    for initial in generated:
        if initial["stage"] != "initial":
            continue
        finals = [g for g in generated if g["builder"] == initial["builder"] and g["stage"] == "final"
                  and g["seed"] == initial["seed"]]
        if len(finals) != 1:
            schedule_issues.append(f"Missing unique final pair: {identity(initial)}"); continue
        final = finals[0]
        for endpoint in ENDPOINTS:
            left, right = initial["endpoints"][endpoint], final["endpoints"][endpoint]
            if "estimate" in left and "estimate" in right:
                target = reference["endpoints"][endpoint].get("estimate")
                paired.append({"builder": initial["builder"], "seed": initial["seed"], "endpoint": endpoint,
                    "initial_estimate": left["estimate"], "final_estimate": right["estimate"],
                    "final_minus_initial": right["estimate"] - left["estimate"],
                    "change_in_absolute_target_difference": (abs(right["estimate"] - target) - abs(left["estimate"] - target)) if target is not None else None,
                    "same_path": initial["path"] == final["path"], "same_bytes": initial["sha256"] == final["sha256"]})
    checks = []
    for field in ("endpoints", "diagnostics", "cells"):
        numerical_comparison(reference[field], reported.get("reference", {}).get(field), f"reference.{field}", checks)
    reported_generated = {identity(g): g for g in reported.get("generated", [])}
    if len(reported_generated) != len(reported.get("generated", [])):
        schedule_issues.append("Duplicate identities in reported evaluation")
    if set(reported_generated) != {identity(g) for g in generated}:
        schedule_issues.append("Generated identities differ between independent and reported evaluation")
    for item in generated:
        matched = reported_generated.get(identity(item), {})
        for field in ("endpoints", "diagnostics", "cells"):
            numerical_comparison(item[field], matched.get(field), f"{identity(item)}.{field}", checks)
    if reported.get("failed_analyses", []) or failed:
        schedule_issues.append("One or more analyses failed; preserved for review")
    after = check_bindings(bindings)
    snapshot_after = check_snapshot(artifact_snapshot)
    if before != after or snapshot_before != snapshot_after:
        raise ValueError("Input artifacts changed during independent recomputation")
    accounting = {"scheduled_stage_tables": len(items), "analyzed_stage_tables": len(generated),
                  "distinct_generated_paths": len({str(Path(i['path']).resolve()) for i in items}),
                  "distinct_generated_sha256": len({i['sha256'] for i in items}),
                  "scheduled_builder_seed_pairs": len({(i['builder'], i['seed']) for i in items}),
                  "note": "Stage reuse is not a new execution. Content hashes are not independent evidence samples."}
    mismatches = [r for r in checks if r["status"] != "match"]
    report = {"status": "passed" if not mismatches and not schedule_issues and not failed else "review_required",
              "release_sha256": digest(release_path), "reported_results_sha256": digest(reported_path),
              "independent_script_sha256": digest(__file__), "artifact_snapshot_sha256": digest(snapshot_path),
              "method": {"formulas": FORMULAS, "effects": "patsy prediction contrasts", "covariance": "statsmodels HC3",
                         "ci": "95% normal", "tolerance": {"relative": 1e-8, "absolute": 1e-10}},
              "environment": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__,
                              "patsy": patsy.__version__, "statsmodels": statsmodels.__version__},
              "accounting": accounting, "schedule_issues": schedule_issues, "numeric_checks": len(checks),
              "discrepancies": mismatches, "reference": reference, "generated": generated,
              "failed_analyses": failed, "reported_failed_analyses": reported.get("failed_analyses", []),
              "integrity": {"unchanged_before_after": True, "release_bound_paths": before,
                            "pre_release_artifacts": snapshot_before},
              "interpretation": "Unweighted quota sample; model-conditional HC3. Sign/interval agreement is descriptive; no equivalence or composite success criterion."}
    output.mkdir(parents=True)
    comparison.to_csv(output / "comparisons.csv", index=False)
    pd.DataFrame(paired).to_csv(output / "paired_initial_final.csv", index=False)
    if not comparison.empty:
        ranges = comparison.groupby(["builder", "stage", "endpoint"], dropna=False).agg(
            realizations=("generated_estimate", "size"), min_estimate=("generated_estimate", "min"),
            max_estimate=("generated_estimate", "max"), mean_estimate=("generated_estimate", "mean"),
            min_signed_difference=("generated_minus_reference", "min"),
            max_signed_difference=("generated_minus_reference", "max")).reset_index()
        ranges.to_csv(output / "realization_ranges.csv", index=False)
    write_json(output / "numeric_comparison.json", checks)
    write_json(output / "independent_audit.json", report)
    return {"status": report["status"], **accounting, "discrepancies": len(mismatches), "schedule_issues": schedule_issues}


def self_check():
    """Invented arithmetic fixture only; never executes a candidate program."""
    rng = np.random.default_rng(417)
    age = np.concatenate([np.tile(np.arange(lo, lo + 15), 3)[:40] for _ in (0, 1) for lo in (20, 35, 50, 65)])
    female = np.repeat([0, 1], 160)
    bmi = rng.uniform(18, 38, 320)
    x, a = (bmi - 27.5) / 5, (age - 50) / 10
    frame = pd.DataFrame({"sample_id": [f"arithmetic_{i}" for i in range(320)], "age": age,
                          "female": female, "bmi": bmi, "urate": 7 + .63*x - .18*a + .47*female})
    validate_frame(frame)
    results, failures = endpoints(frame)
    assert not failures
    for endpoint, expected in {"adjusted_bmi": .63, "adjusted_age": -.18, "adjusted_sex": .47,
                               "bmi_curvature": 0, "bmi_sex_interaction": 0, "male_bmi": .63,
                               "female_bmi": .63, "reverse_urate": 5/.63}.items():
        np.testing.assert_allclose(results[endpoint]["estimate"], expected, atol=1e-10, rtol=1e-10)
    frame["urate"] = 7 + .63*x - .18*a + .47*female + .31*x*x
    assert abs(endpoints(frame)[0]["bmi_curvature"]["estimate"] - .62) < 1e-10
    frame["urate"] = 7 + .63*x - .18*a + .47*female + .29*x*female
    effects = endpoints(frame)[0]
    assert abs(effects["female_bmi"]["estimate"] - .92) < 1e-10
    assert abs(effects["bmi_sex_interaction"]["estimate"] - .29) < 1e-10
    assert len(diagnostics(frame)["summaries"]) == 6
    return {"status": "passed", "invented_arithmetic_only": True, "candidate_generator_executed": False,
            "checked": "eight known linear effects, quadratic finite difference, sex interaction contrasts, quota and diagnostic shape"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("self-check")
    snap = subs.add_parser("snapshot")
    snap.add_argument("--output", required=True)
    snap.add_argument("--directory", action="append", default=[])
    snap.add_argument("--file", action="append", default=[])
    run = subs.add_parser("audit")
    for option in ("release", "reported-results", "artifact-snapshot", "output-dir"):
        run.add_argument("--" + option, required=True)
    args = parser.parse_args()
    if args.command == "self-check":
        result = self_check()
    elif args.command == "snapshot":
        result = snapshot(args.output, args.directory, args.file)
    else:
        result = audit(args.release, args.reported_results, args.artifact_snapshot, args.output_dir)
    print(json.dumps(result, allow_nan=False))
