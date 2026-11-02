"""Independent, fixed-plan recomputation. Import and --self-check read no study data.

The primary evaluator is reused ONLY for its final metadata/read-permission gate.
Decoding, preparation, estimates, CR1/t inference and comparisons are independent.
An explicit hash-bound recomputation authorization and completed primary report
are required before any reference or generated table is read. No generator runs.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm


PLAN_SHA = "a2c5f43969c700474a9466416be8503dc0c92b1c78b12a07a6edc6bc88f247b7"
EVALUATOR_SHA = "e40f403b13125f5b41f620126a807122bb99796558adda576518fcf50796365a"
VARIABLES = ["age", "female", "bmi", "glucose", "hba1c"]
RTOL, ATOL = 1e-8, 1e-10  # Numerical recomputation agreement, NOT scientific utility.


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def local(root, name):
    relative = Path(name)
    require(not relative.is_absolute() and ".." not in relative.parts, "Path must remain in its approved bundle")
    result = (root / relative).resolve()
    require(result.is_relative_to(root.resolve()), "Escaped bundle path")
    return result


def read_json(path):
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_new(path, value):
    with Path(path).open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")


def versions():
    return {"python": platform.python_version(), **{name: importlib.metadata.version(name)
            for name in ("numpy", "pandas", "scipy", "statsmodels", "pyreadstat")}}


def numeric(series):
    require(pd.api.types.is_numeric_dtype(series.dtype) and not pd.api.types.is_bool_dtype(series.dtype),
            "Unexpected nonnumeric field; no coercion")
    return series.to_numpy(dtype=float, na_value=np.nan)


def flags(frame):
    return {name: {"missing" if pd.isna(code) else str(float(code)): int(count)
                   for code, count in frame[name].value_counts(dropna=False).items()}
            for name in ("CLN_HT", "CLN_WT")}


def prepare(frames, plan):
    """Independent indexed intersections; no primary preparation helper imported."""
    indexed, missing, row_counts = {}, {}, {}
    for definition in plan["input_files"]:
        name, key, wave = definition["file"], definition["key"], definition["wave"]
        columns = [key] + ([wave] if wave else []) + definition["columns"]
        raw = frames[name]
        require(raw.columns.is_unique and set(columns) <= set(raw), "Missing/duplicate source columns")
        frame = raw[columns].copy()
        for column in columns:
            values = numeric(frame[column])
            if column == key or column == wave:
                require(np.isfinite(values).all() and (np.abs(values) < 2**53).all()
                        and (values == np.trunc(values)).all(), "Invalid linkage key")
        keys = [key] + ([wave] if wave else [])
        require(not frame.duplicated(keys).any(), "Duplicate linkage key in release; do not deduplicate")
        row_counts[name] = len(frame)
        missing[name] = {column: int(frame[column].isna().sum()) for column in definition["columns"]}
        if wave:
            frame = frame.loc[frame[wave].eq(plan["target_wave"])]
        frame = frame.set_index(keys)
        frame.index.names = ["person", "wave"] if wave else ["person"]
        indexed[name] = frame
    bio = indexed["biomarker_09.sas7bdat"]
    exam = indexed["pexam_00.sas7bdat"]
    survey = indexed["surveys_pub_12.sas7bdat"]
    master = indexed["mast_pub_12.sas7bdat"]
    ids = bio.index
    flow = {"biomarker_wave": len(ids)}
    ids = ids.intersection(exam.index, sort=False)
    flow["after_examination"] = len(ids)
    ids = ids.intersection(survey.index, sort=False)
    flow["after_surveys"] = len(ids)
    ids = ids[ids.get_level_values("person").isin(master.index)]
    flow["after_master"] = len(ids)
    linked = pd.concat([bio.loc[ids], exam.loc[ids], survey.loc[ids]], axis=1).reset_index(drop=True)
    linked["GENDER"] = master.reindex(ids.get_level_values("person"))["GENDER"].to_numpy()
    ht = numeric(linked["HEIGHT"]).copy()
    wt = numeric(linked["WEIGHT"]).copy()
    ht[linked["CLN_HT"].eq(9).to_numpy()] = np.nan
    wt[linked["CLN_WT"].eq(9).to_numpy()] = np.nan
    finite = np.isfinite(ht) & np.isfinite(wt)
    positive = finite & (ht > 0) & (wt > 0)
    bmi = np.full(len(linked), np.nan)
    with np.errstate(all="ignore"):
        bmi[positive] = wt[positive] * 10000 / np.square(ht[positive])
    derived_invalid = positive & (~np.isfinite(bmi) | (bmi <= 0))
    bmi[derived_invalid] = np.nan
    values = pd.DataFrame({"age": linked["age"], "female": linked["GENDER"].map({1: 0, 2: 1}),
                           "bmi": bmi, "glucose": linked["GLUCOSE"], "hba1c": linked["HbA1c"],
                           "survey_commid": linked["commid"]})
    age = plan["target_age_interval"]
    eligible = values["age"].ge(age["lower"]) & values["age"].le(age["upper"]) & values["female"].notna()
    finite_glycemia = np.isfinite(values[["glucose", "hba1c"]].to_numpy()).all(axis=1)
    complete = eligible & values[VARIABLES].notna().all(axis=1) & finite_glycemia
    quality = {"input_rows": row_counts, "linkage_rows": flow, "age_gender_eligible": int(eligible.sum()),
               "common_complete_case": int(complete.sum()), "native_missing": missing,
               "nonfinite_glycemia": {"scope": "linked_2009_before_age_gender_eligibility",
                   **{name: int(np.isinf(numeric(values[name])).sum()) for name in ("glucose", "hba1c")}},
               "flag9_masked": {"height": int(linked["CLN_HT"].eq(9).sum()), "weight": int(linked["CLN_WT"].eq(9).sum())},
               "invalid_anthropometry": int(((finite & ~positive) | derived_invalid).sum()),
               "cleaning_flag_counts": {"linked": flags(linked), "analysis": flags(linked.loc[complete])}}
    return values.loc[complete].reset_index(drop=True), quality


def unavailable_interval(reason, groups=None):
    return {"status": "unavailable", "lower": None, "upper": None, "standard_error": None,
            "groups": groups, "degrees_of_freedom": None, "reason": reason, "method": "CR1_t"}


def estimate(frame, item, reference):
    design = sm.add_constant(frame[item["predictors"]].astype(float), prepend=True, has_constant="add")
    n, k = design.shape
    rank = int(np.linalg.matrix_rank(design)) if n else 0
    condition = float(np.linalg.cond(design)) if n else float("inf")
    result = {"status": "unavailable", "coefficient": None, "unit": item["unit"], "n": n, "rank": rank,
              "condition_number": condition if np.isfinite(condition) else None,
              "interval": unavailable_interval("primary_estimate_unavailable")}
    if n < 100 or rank != k or n <= k:
        result["reason"] = "insufficient_n" if n < 100 else "rank_or_residual_df_failure"
        return result
    fitted = sm.OLS(frame["hba1c"].astype(float), design, missing="raise").fit()
    coefficient = float(fitted.params[item["term"]])
    require(np.isfinite(coefficient), "Nonfinite independent estimate")
    result.update(status="computed", coefficient=coefficient)
    if not reference:
        result["interval"] = unavailable_interval("generated_no_inference")
        return result
    if "survey_commid" not in frame:
        result["interval"] = unavailable_interval("missing_community_field")
        return result
    try:
        grouping = numeric(frame["survey_commid"])
    except ValueError:
        grouping = np.full(n, np.nan)
    if not (np.isfinite(grouping).all() and (grouping > 0).all() and (grouping == np.trunc(grouping)).all()):
        result["interval"] = unavailable_interval("invalid_community_ids")
        return result
    g = len(np.unique(grouping))
    if g < 20:
        result["interval"] = unavailable_interval("insufficient_communities", g)
        return result
    robust = fitted.get_robustcov_results(cov_type="cluster", groups=grouping,
                                        use_correction=True, df_correction=True, use_t=True)
    position = list(design).index(item["term"])
    variance = float(robust.cov_params()[position, position])
    if not np.isfinite(variance) or variance < 0:
        result["interval"] = unavailable_interval("invalid_cluster_variance", g)
        return result
    low, high = robust.conf_int(alpha=0.05)[position]
    result["interval"] = {"status": "available", "lower": float(low), "upper": float(high),
                          "standard_error": float(robust.bse[position]), "groups": g,
                          "degrees_of_freedom": g - 1, "reason": None, "method": "CR1_t"}
    return result


def diagnostics(frame):
    marginals = {}
    for name in VARIABLES:
        series = frame[name]
        qs = series.quantile([0.1, 0.5, 0.9], interpolation="linear") if len(series) else [None] * 3
        marginals[name] = {"mean": float(series.mean()) if len(series) else None,
                           "sd": float(series.std(ddof=1)) if len(series) > 1 else None,
                           **dict(zip(["q10", "median", "q90"], list(qs)))}
    x, y = frame["glucose"], frame["hba1c"]
    available = len(frame) > 1 and x.nunique() > 1 and y.nunique() > 1
    return {"marginal": marginals,
            "joint": {"pearson": float(stats.pearsonr(x, y).statistic) if available else None,
                      "spearman": float(stats.spearmanr(x, y).statistic) if available else None}}


def analyze(frame, plan, reference=False, quality=None):
    arrays = {name: numeric(frame[name]) for name in VARIABLES}
    nonpositive = {name: int(np.count_nonzero(np.isfinite(arrays[name]) & (arrays[name] <= 0)))
                   for name in ("glucose", "hba1c")}
    reason = "nonpositive_glycemia_interpretation_required" if sum(nonpositive.values()) else None
    if reason is None:
        valid = (all(np.isfinite(values).all() for values in arrays.values())
                 and frame["age"].between(35, 74, inclusive="both").all()
                 and frame["female"].isin([0, 1]).all() and frame["bmi"].gt(0).all())
        reason = None if valid else "invalid_analysis_values_no_row_deletion"
    result = {"status": "withheld" if reason else "complete", "mode": "reference" if reference else "generated",
              "n": len(frame), "quality": {**(quality or {}), "nonpositive_glycemia": nonpositive},
              "gate_reason": reason, "estimands": {}, "diagnostics": None, "national_representativeness": False}
    for item in plan["estimands"]:
        result["estimands"][item["id"]] = ({"status": "unavailable", "coefficient": None, "unit": item["unit"],
            "n": len(frame), "rank": None, "condition_number": None, "reason": reason,
            "interval": unavailable_interval(reason)} if reason else estimate(frame, item, reference))
    if reason is None:
        result["diagnostics"] = diagnostics(frame)
    return result


def comparisons(reference, generated):
    result = {}
    for name, ref in reference["estimands"].items():
        other = generated["estimands"][name]
        interval = ref["interval"]
        direction = "inconclusive"
        if interval["status"] == "available":
            direction = "positive" if interval["lower"] > 0 else "negative" if interval["upper"] < 0 else direction
        valid = ref["status"] == other["status"] == "computed"
        value, base = other["coefficient"], ref["coefficient"]
        result[name] = {"status": "computed" if valid else "unavailable", "reference": base, "generated": value,
                       "difference": value - base if valid else None, "reference_direction": direction,
                       "generated_sign": None if value is None else "positive" if value > 0 else "negative" if value < 0 else "zero",
                       "ratio": value / base if valid and direction != "inconclusive" and base != 0 else None,
                       "interval_membership": bool(interval["lower"] <= value <= interval["upper"])
                           if valid and interval["status"] == "available" else None}
    return result


def stage_summaries(rows):
    result = {}
    for construction in ("C1", "C2"):
        for stage in ("initial", "revised"):
            selected = [r for r in rows if r["construction"] == construction and r["stage"] == stage]
            result[f"{construction}_{stage}"] = {}
            for name in ("E1", "E2", "E3"):
                values = [r["analysis"]["estimands"][name]["coefficient"] for r in selected
                          if r["analysis"] and r["analysis"]["estimands"][name]["status"] == "computed"]
                mc = len(values) == 3 and all(r["route"] == "generator.py" for r in selected)
                direction = "incomplete" if len(values) < 3 else "not_assessed_direct_reuse" if not mc else \
                            "stable_positive" if all(v > 0 for v in values) else \
                            "stable_negative" if all(v < 0 for v in values) else "unresolved"
                result[f"{construction}_{stage}"][name] = {"valid_seed_count": len(values), "direction_status": direction,
                    "range": [min(values), max(values)] if values else None, "monte_carlo_credit": mc}
    return result


def differences(expected, actual, path="", errors=None):
    """Compare all reported semantic fields and numbers; no best-result selection."""
    errors = [] if errors is None else errors
    if isinstance(expected, dict) and isinstance(actual, dict):
        if set(expected) != set(actual):
            errors.append({"path": path, "reason": "different_keys", "expected": sorted(expected), "actual": sorted(actual)})
        for key in expected.keys() & actual.keys():
            differences(expected[key], actual[key], path + "/" + key, errors)
    elif isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            errors.append({"path": path, "reason": "different_lengths"})
        for index, (left, right) in enumerate(zip(expected, actual)):
            differences(left, right, path + "/" + str(index), errors)
    elif isinstance(expected, (float, int)) and not isinstance(expected, bool) and isinstance(actual, (float, int)) and not isinstance(actual, bool):
        if not np.isfinite(expected) or not np.isfinite(actual) or not np.isclose(expected, actual, rtol=RTOL, atol=ATOL):
            errors.append({"path": path, "reason": "numeric_disagreement", "independent": expected, "primary": actual})
    elif expected != actual:
        errors.append({"path": path, "reason": "semantic_disagreement", "independent": expected, "primary": actual})
    return errors


def gate(bundle, authorization):
    """Only the primary permission gate is reused; never its scientific helpers."""
    root = Path(bundle).resolve()
    auth_path = local(root, authorization)
    auth = read_json(auth_path)
    required = {"schema_version", "status", "reason", "script_sha256", "evaluation_release_sha256",
                "primary_report_sha256", "runtime_versions"}
    require(set(auth) == required and auth["schema_version"] == 1 and auth["status"] == "authorized", "Missing recomputation authorization")
    require(isinstance(auth["reason"], str) and auth["reason"].strip(), "Authorization requires a reason")
    require(auth["script_sha256"] == digest(__file__) and auth["runtime_versions"] == versions(), "Recompute script/runtime changed")
    require(digest(local(root, "analysis_plan.json")) == PLAN_SHA, "Independent fixed plan changed")
    evaluator_path = local(root, "evaluation/chns_f2_evaluation.py")
    require(digest(evaluator_path) == EVALUATOR_SHA, "Reviewed evaluator changed")
    release_path = local(root, "EVALUATION_RELEASE.json")
    require(digest(release_path) == auth["evaluation_release_sha256"], "Evaluation release changed")
    report_path = local(root, "evaluation_results/REPORT.json")
    require(digest(report_path) == auth["primary_report_sha256"], "Completed primary report changed")
    spec = importlib.util.spec_from_file_location("f2_primary_permission_gate_only", evaluator_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    checked_root, plan, slots, release_sha = module._evaluation_gate(root, "EVALUATION_RELEASE.json")
    require(checked_root == root and release_sha == auth["evaluation_release_sha256"], "Read permission mismatch")
    primary = read_json(report_path)
    require(primary["evaluation_release_sha256"] == release_sha, "Primary report belongs to another release")
    require(not local(root, "evaluation_results/FAILURE.json").exists(), "Primary evaluation has a failure record")
    return root, plan, slots, primary, auth, digest(auth_path)


def run(bundle, reference_dir, authorization):
    root, plan, slots, primary, auth, auth_hash = gate(bundle, authorization)
    destination = local(root, "independent_results")
    destination.mkdir(exist_ok=False)  # Exclusive reservation; failures are not auto-retried.
    write_new(destination / "REQUEST.json", {"authorization_sha256": auth_hash, "script_sha256": digest(__file__), "runtime_versions": versions()})
    try:
        reference_root = Path(reference_dir).resolve()
        files = {item["file"]: local(reference_root, item["file"]) for item in plan["input_files"]}
        for item in plan["input_files"]:
            require(digest(files[item["file"]]) == item["sha256"], "Reference SAS release changed")
        import pyreadstat  # Reused decoder dependency; preparation/estimation remain independent.
        frames = {}
        for item in plan["input_files"]:
            columns = [item["key"]] + ([item["wave"]] if item["wave"] else []) + item["columns"]
            frames[item["file"]], _ = pyreadstat.read_sas7bdat(str(files[item["file"]]), usecols=columns, user_missing=False)
        reference_frame, quality = prepare(frames, plan)
        reference = analyze(reference_frame, plan, reference=True, quality=quality)
        recomputed = []
        for slot in slots:
            analytical = None
            if slot["status"] == "success":
                run_id = f'{slot["construction"]}_{slot["stage"]}_s{slot["seed"]}'
                path = local(root, f"executions/{run_id}/output/generated.csv")
                require(digest(path) == slot["generated_sha256"], "Generated file changed")
                frame = pd.read_csv(path, dtype={"row_id": "string"})
                require(list(frame) == ["row_id"] + VARIABLES and len(frame) == 3000 and
                        frame["row_id"].notna().all() and frame["row_id"].is_unique, "Generated layout changed")
                analytical = analyze(frame, plan)
            recomputed.append({**{name: slot[name] for name in ("construction", "stage", "seed", "status", "route", "reason")},
                               "analysis": analytical, "comparison": comparisons(reference, analytical) if analytical else None})
        key = lambda row: (row["construction"], row["stage"], row["seed"])
        independent = {"reference": reference, "slots": sorted(recomputed, key=key), "stages": stage_summaries(recomputed), "global_score": None}
        recorded = {"reference": primary["reference"], "slots": sorted(primary["slots"], key=key), "stages": primary["stages"], "global_score": primary["global_score"]}
        disagreement = differences(independent, recorded)
        report = {"schema_version": 1, "status": "matched" if not disagreement else "disagreement",
                  "authorization_sha256": auth_hash, "primary_report_sha256": auth["primary_report_sha256"],
                  "script_sha256": digest(__file__), "runtime_versions": versions(), "numerical_tolerance": {"rtol": RTOL, "atol": ATOL},
                  "disagreements": disagreement, **independent,
                  "scope": "Independent indexed preparation and statsmodels OLS/cluster-CR1-t; all planned slots and diagnostics.",
                  "shared_dependencies": ["pyreadstat SAS decoder", "fixed analysis plan", "primary metadata permission gate only"],
                  "limitations": ["Numerical agreement is not biological validation or target-population truth.",
                                  "No new analyses, data generation, calibration or target-informed repair."]}
        write_new(destination / "REPORT.json", report)
        return {"status": report["status"], "disagreement_count": len(disagreement), "report": str(destination / "REPORT.json")}
    except Exception as error:
        write_new(destination / "FAILURE.json", {"type": type(error).__name__, "message": str(error), "authorization_sha256": auth_hash})
        raise


def self_check():
    """One fabricated in-memory case; no study paths, metadata or rows are read."""
    rng = np.random.default_rng(161803)
    n = 120
    frame = pd.DataFrame({"age": rng.integers(35, 75, n), "female": rng.integers(0, 2, n),
                          "bmi": rng.uniform(18, 35, n), "glucose": rng.uniform(4, 8, n),
                          "survey_commid": 5001 + np.arange(n) % 24})
    frame["hba1c"] = 3 + 0.02 * frame["age"] + 0.3 * frame["glucose"] + rng.normal(0, .2, n)
    specifications = [("E1", ["age", "female", "bmi"], "bmi", "%/(kg/m^2)"),
                      ("E2", ["age", "female", "glucose"], "glucose", "%/(mmol/L)"),
                      ("E3", ["female", "bmi", "glucose", "age"], "age", "%/year")]
    items = [{"id": key, "predictors": predictors, "term": term, "unit": unit} for key, predictors, term, unit in specifications]
    definitions = [("biomarker_09.sas7bdat", "IDind", "wave", ["GLUCOSE", "HbA1c"]),
                   ("pexam_00.sas7bdat", "IDind", "WAVE", ["HEIGHT", "WEIGHT", "CLN_HT", "CLN_WT"]),
                   ("mast_pub_12.sas7bdat", "Idind", None, ["GENDER"]),
                   ("surveys_pub_12.sas7bdat", "Idind", "wave", ["age", "commid"])]
    plan = {"target_wave": 2009, "target_age_interval": {"lower": 35, "upper": 74}, "estimands": items,
            "input_files": [{"file": name, "key": key, "wave": wave, "columns": cols} for name, key, wave, cols in definitions]}
    ids = np.arange(990001, 990001 + n)
    frames = {"biomarker_09.sas7bdat": pd.DataFrame({"IDind": ids, "wave": 2009, "GLUCOSE": frame.glucose, "HbA1c": frame.hba1c}),
              "pexam_00.sas7bdat": pd.DataFrame({"IDind": ids, "WAVE": 2009, "HEIGHT": 170., "WEIGHT": frame.bmi * 1.7**2, "CLN_HT": 0, "CLN_WT": 0}),
              "mast_pub_12.sas7bdat": pd.DataFrame({"Idind": ids, "GENDER": frame.female + 1}),
              "surveys_pub_12.sas7bdat": pd.DataFrame({"Idind": ids, "wave": 2009, "age": frame.age, "commid": frame.survey_commid})}
    frames["pexam_00.sas7bdat"].loc[0, "CLN_HT"] = 9
    frames["biomarker_09.sas7bdat"].loc[1, "GLUCOSE"] = np.inf
    frames["biomarker_09.sas7bdat"].loc[2, "HbA1c"] = np.nan
    frames = {name: table.iloc[::-1].copy() if "biomarker" not in name else table for name, table in frames.items()}
    prepared, quality = prepare(frames, plan)
    require(len(prepared) == 117 and quality["nonfinite_glycemia"]["glucose"] == 1 and quality["flag9_masked"]["height"] == 1,
            "Invented selection failed")
    np.testing.assert_allclose(prepared[VARIABLES], frame.loc[3:, VARIABLES], rtol=RTOL, atol=ATOL)
    result = analyze(prepared, plan, reference=True, quality=quality)
    for item in items:
        x = np.column_stack([np.ones(len(prepared)), prepared[item["predictors"]]])
        y = prepared.hba1c.to_numpy()
        beta = np.linalg.solve(x.T @ x, x.T @ y)
        group = prepared.survey_commid.to_numpy()
        unique = np.unique(group)
        scores = np.array([x[group == g].T @ (y - x @ beta)[group == g] for g in unique])
        bread = np.linalg.inv(x.T @ x)
        covariance = len(unique)/(len(unique)-1) * (len(y)-1)/(len(y)-x.shape[1]) * bread @ scores.T @ scores @ bread
        pos = 1 + item["predictors"].index(item["term"])
        actual = result["estimands"][item["id"]]
        np.testing.assert_allclose(actual["coefficient"], beta[pos], rtol=RTOL, atol=ATOL)
        np.testing.assert_allclose(actual["interval"]["standard_error"], np.sqrt(covariance[pos, pos]), rtol=RTOL, atol=ATOL)
        np.testing.assert_allclose(actual["interval"]["upper"], beta[pos] + stats.t.ppf(.975, len(unique)-1)*np.sqrt(covariance[pos,pos]), rtol=RTOL, atol=ATOL)
    altered = prepared.copy()
    altered.loc[0, "glucose"] = 0
    withheld = analyze(altered, plan)
    require(withheld["status"] == "withheld" and withheld["n"] == len(altered), "Invented nonpositive gate failed")
    require(not differences(result, result), "Comparison self identity failed")
    return {"status": "passed", "fixture": "one invented in-memory case, 120 rows; no patient/generated files or study metadata read",
            "checks": "indexed linkage, finite availability/flag/native missing, 3 OLS and CR1/t closed-form checks, withholding"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--bundle")
    parser.add_argument("--reference-dir")
    parser.add_argument("--authorization", default="INDEPENDENT_RECOMPUTATION_RELEASE.json")
    args = parser.parse_args()
    if args.self_check:
        require(args.bundle is None and args.reference_dir is None, "Self-check accepts no data paths")
        print(json.dumps(self_check()))
    else:
        require(args.bundle and args.reference_dir, "Explicit bundle and reference directory required")
        print(json.dumps(run(args.bundle, args.reference_dir, args.authorization)))
