"""Fixed F2 scientific evaluation; pure frame helpers and a separate release gate.

No participant file is read at import. Only evaluate_released may decode source
files, after independent final-inventory approval and an exclusive reservation.
"""
from __future__ import annotations

import importlib.util
import importlib.metadata
from pathlib import Path
import platform

import numpy as np
import pandas as pd
from scipy.stats import t
import scipy

from cohort_harness import contracts, execution, lifecycle
from cohort_harness.contracts import require, exact_keys, text
from cohort_harness.lifecycle import _bundle, _path, read_json, sha256


VARIABLES = ("age", "female", "bmi", "glucose", "hba1c")
SEEDS = (1701, 1702, 1703)
CONSTRUCTIONS, STAGES = ("C1", "C2"), ("initial", "revised")
_INPUTS = {
    "biomarker_09.sas7bdat": ("IDind", "wave", ["GLUCOSE", "HbA1c"]),
    "pexam_00.sas7bdat": ("IDind", "WAVE", ["HEIGHT", "WEIGHT", "CLN_HT", "CLN_WT"]),
    "mast_pub_12.sas7bdat": ("Idind", None, ["GENDER"]),
    "surveys_pub_12.sas7bdat": ("Idind", "wave", ["age", "commid"]),
}
_MODELS = (("E1", ["age", "female", "bmi"], "bmi", "%/(kg/m^2)"),
           ("E2", ["age", "female", "glucose"], "glucose", "%/(mmol/L)"),
           ("E3", ["female", "bmi", "glucose", "age"], "age", "%/year"))


def _same(left, right):
    import json
    return json.dumps(left, sort_keys=True, allow_nan=False) == json.dumps(right, sort_keys=True, allow_nan=False)


def validate_plan(plan):
    require(type(plan["schema_version"]) is int and plan["schema_version"] == 1, "Invalid analysis plan")
    age = plan["target_age_interval"]
    require(plan["target_wave"] == 2009 and age["lower"] == 35 and age["upper"] == 74 and age["inclusive"] is True,
            "Unsupported wave/age policy")
    inputs = {item["file"]: item for item in plan["input_files"]}
    require(len(inputs) == 4 and set(inputs) == set(_INPUTS), "Exactly the four approved source files are required")
    for name, (key, wave, columns) in _INPUTS.items():
        require((inputs[name]["key"], inputs[name]["wave"], inputs[name]["columns"]) == (key, wave, columns),
                "Source field/key definition differs from fixed metadata")
        contracts._hash(inputs[name]["sha256"])
    require(plan["denominator"]["kind"] == "common_complete_case" and
            plan["denominator"]["required"] == list(VARIABLES) and plan["denominator"]["min_n_for_effects"] == 100,
            "Unsupported analysis denominator")
    require(len(plan["estimands"]) == 3, "Exactly three estimands are required")
    for item, (identifier, predictors, term, unit) in zip(plan["estimands"], _MODELS):
        require(item["id"] == identifier and item["operator"] == "ols_coefficient" and item["outcome"] == "hba1c" and
                item["predictors"] == predictors and item["term"] == term and item["unit"] == unit and
                item["intercept"] is True and item["weights"] == "none" and item["feedback"] is False,
                "Unsupported scientific estimand")
    interval = plan["reference_interval"]
    require(interval["method"] == "community_cluster_sandwich_CR1_t" and interval["level"] == 0.95 and
            interval["group"] == "survey_commid" and interval["min_groups"] == 20 and
            interval["correction"] == "G/(G-1)*(n-1)/(n-k)", "Unsupported reference interval")
    return plan


def _numeric(series, name):
    require(pd.api.types.is_numeric_dtype(series.dtype) and not pd.api.types.is_bool_dtype(series.dtype),
            "Numeric values required without coercion: " + name)
    return series.to_numpy(dtype=float, na_value=np.nan)


def _keys(frame, names):
    for name in names:
        values = _numeric(frame[name], name)
        require(np.isfinite(values).all() and (np.abs(values) < 2 ** 53).all() and (values == np.floor(values)).all(),
                "Missing, nonintegral or inexact linkage key")
    require(not frame.duplicated(names).any(), "Duplicate linkage key; no silent deduplication")


def _flag_counts(frame):
    return {name: {"missing" if pd.isna(key) else str(float(key)): int(count)
                   for key, count in frame[name].value_counts(dropna=False).items()}
            for name in ("CLN_HT", "CLN_WT")}


def prepare_reference_frames(frames, plan):
    """Apply only the fixed release policy to caller-supplied frames; return no IDs."""
    validate_plan(plan)
    require(set(frames) == set(_INPUTS), "Exactly four source frames are required")
    normalized, missing, counts = {}, {}, {}
    for name, (key, wave, columns) in _INPUTS.items():
        original = frames[name]
        require(isinstance(original, pd.DataFrame) and original.columns.is_unique, "Invalid source frame")
        selected = [key] + ([wave] if wave else []) + columns
        require(set(selected) <= set(original.columns), "Required source fields are missing")
        data = original[selected].copy()
        for column in selected:
            _numeric(data[column], column)
        _keys(data, [key] + ([wave] if wave else []))  # Check all waves before selection.
        missing[name] = {column: int(data[column].isna().sum()) for column in columns}
        counts[name] = len(data)
        data = data.rename(columns={key: "_id", **({wave: "_wave"} if wave else {})})
        normalized[name] = data.loc[data["_wave"] == 2009].copy() if wave else data
    joined = normalized["biomarker_09.sas7bdat"]
    flow = {"biomarker_wave": len(joined)}
    for name, label in (("pexam_00.sas7bdat", "after_examination"), ("surveys_pub_12.sas7bdat", "after_surveys")):
        joined = joined.merge(normalized[name], on=["_id", "_wave"], how="inner", validate="one_to_one", sort=False)
        flow[label] = len(joined)
    joined = joined.merge(normalized["mast_pub_12.sas7bdat"], on="_id", how="inner", validate="many_to_one", sort=False)
    flow["after_master"] = len(joined)
    linked_flags = _flag_counts(joined)
    height = joined["HEIGHT"].mask(joined["CLN_HT"] == 9).to_numpy(dtype=float)
    weight = joined["WEIGHT"].mask(joined["CLN_WT"] == 9).to_numpy(dtype=float)
    finite_pair = np.isfinite(height) & np.isfinite(weight)
    valid_pair = finite_pair & (height > 0) & (weight > 0)
    bmi = np.full(len(joined), np.nan)
    with np.errstate(over="ignore", divide="ignore", invalid="ignore", under="ignore"):
        bmi[valid_pair] = weight[valid_pair] / (height[valid_pair] / 100) ** 2
    invalid_derived = valid_pair & (~np.isfinite(bmi) | (bmi <= 0))
    bmi[invalid_derived] = np.nan
    derived = pd.DataFrame({"age": joined["age"], "female": joined["GENDER"].map({1: 0, 2: 1}),
                            "bmi": bmi, "glucose": joined["GLUCOSE"], "hba1c": joined["HbA1c"],
                            "survey_commid": joined["commid"]}, index=joined.index)
    eligible = derived["age"].between(35, 74, inclusive="both") & derived["female"].notna()
    finite_glycemia = {name: np.isfinite(_numeric(derived[name], name)) for name in ("glucose", "hba1c")}
    complete = (eligible & derived[list(VARIABLES)].notna().all(axis=1) &
                finite_glycemia["glucose"] & finite_glycemia["hba1c"])
    # Reference availability requires finite glycemia; finite zero/negative values
    # remain for the interpretation gate. Generated frames never use this filter.
    result = derived.loc[complete].reset_index(drop=True)
    quality = {"input_rows": counts, "linkage_rows": flow, "age_gender_eligible": int(eligible.sum()),
               "common_complete_case": int(complete.sum()), "native_missing": missing,
               "nonfinite_glycemia": {"scope": "linked_2009_before_age_gender_eligibility",
                   **{name: int((derived[name].notna() & ~finite_glycemia[name]).sum())
                      for name in finite_glycemia}},
               "flag9_masked": {"height": int((joined["CLN_HT"] == 9).sum()), "weight": int((joined["CLN_WT"] == 9).sum())},
               "invalid_anthropometry": int((finite_pair & ~valid_pair | invalid_derived).sum()),
               "cleaning_flag_counts": {"linked": linked_flags, "analysis": _flag_counts(joined.loc[complete])}}
    return result, quality


def _interval(reason, *, groups=None):
    return {"status": "unavailable", "lower": None, "upper": None, "standard_error": None,
            "groups": groups, "degrees_of_freedom": None, "reason": reason, "method": "CR1_t"}


def _fit(frame, item, plan, reference):
    n = len(frame)
    x = np.column_stack([np.ones(n), frame[item["predictors"]].to_numpy(dtype=float)])
    k = x.shape[1]
    rank = int(np.linalg.matrix_rank(x)) if n else 0
    condition = float(np.linalg.cond(x)) if n else np.inf
    record = {"status": "unavailable", "coefficient": None, "unit": item["unit"], "n": n, "rank": rank,
              "condition_number": condition if np.isfinite(condition) else None,
              "interval": _interval("primary_estimate_unavailable")}
    if n < 100 or rank != k or n <= k:
        record["reason"] = "insufficient_n" if n < 100 else "rank_or_residual_df_failure"
        return record
    y = frame["hba1c"].to_numpy(dtype=float)
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    position = item["predictors"].index(item["term"]) + 1
    coefficient = float(beta[position])
    require(np.isfinite(coefficient), "Nonfinite OLS result")
    record.update(status="computed", coefficient=coefficient)
    if not reference:
        record["interval"] = _interval("generated_no_inference")
        return record
    if "survey_commid" not in frame:
        record["interval"] = _interval("missing_community_field")
        return record
    groups = frame["survey_commid"]
    if not pd.api.types.is_numeric_dtype(groups.dtype) or pd.api.types.is_bool_dtype(groups.dtype):
        record["interval"] = _interval("invalid_community_ids")
        return record
    codes = groups.to_numpy(dtype=float, na_value=np.nan)
    if not (np.isfinite(codes).all() and (codes > 0).all() and (codes == np.floor(codes)).all()):
        record["interval"] = _interval("invalid_community_ids")
        return record
    unique, inverse = np.unique(codes, return_inverse=True)
    g = len(unique)
    if g < 20:
        record["interval"] = _interval("insufficient_communities", groups=g)
        return record
    residual = y - x @ beta
    scores = np.zeros((g, k))
    np.add.at(scores, inverse, x * residual[:, None])
    pinv = np.linalg.pinv(x)
    bread = pinv @ pinv.T
    covariance = (g / (g - 1) * (n - 1) / (n - k)) * bread @ (scores.T @ scores) @ bread
    variance = float(covariance[position, position])
    if not np.isfinite(variance) or variance < 0:
        record["interval"] = _interval("invalid_cluster_variance", groups=g)
        return record
    se = float(np.sqrt(variance))
    half = float(t.ppf(0.975, g - 1) * se)
    record["interval"] = {"status": "available", "lower": coefficient - half, "upper": coefficient + half,
                          "standard_error": se, "groups": g, "degrees_of_freedom": g - 1,
                          "reason": None, "method": "CR1_t"}
    return record


def _diagnostics(frame):
    marginal = {}
    for name in VARIABLES:
        values = frame[name].to_numpy(dtype=float)
        quantiles = np.quantile(values, [0.1, 0.5, 0.9], method="linear") if len(values) else [None] * 3
        marginal[name] = {"mean": float(values.mean()) if len(values) else None,
                          "sd": float(values.std(ddof=1)) if len(values) > 1 else None,
                          "q10": quantiles[0], "median": quantiles[1], "q90": quantiles[2]}
    pair = frame[["glucose", "hba1c"]]
    valid = len(pair) > 1 and all(pair[name].nunique() > 1 for name in pair)
    joint = {"pearson": float(np.corrcoef(pair.to_numpy(dtype=float), rowvar=False)[0, 1]) if valid else None,
             "spearman": float(np.corrcoef(pair.rank(method="average").to_numpy(dtype=float), rowvar=False)[0, 1]) if valid else None}
    return {"marginal": marginal, "joint": joint}


def analyze(frame, plan, *, reference=False, quality=None):
    validate_plan(plan)
    require(isinstance(frame, pd.DataFrame) and frame.columns.is_unique and set(VARIABLES) <= set(frame), "Invalid analysis frame")
    values = {name: _numeric(frame[name], name) for name in VARIABLES}
    nonpositive = {name: int((np.isfinite(values[name]) & (values[name] <= 0)).sum()) for name in ("glucose", "hba1c")}
    reason = "nonpositive_glycemia_interpretation_required" if any(nonpositive.values()) else None
    if reason is None and (not all(np.isfinite(value).all() for value in values.values()) or
                           not ((values["age"] >= 35) & (values["age"] <= 74)).all() or
                           not np.isin(values["female"], [0, 1]).all() or not (values["bmi"] > 0).all()):
        reason = "invalid_analysis_values_no_row_deletion"
    report = {"status": "withheld" if reason else "complete", "mode": "reference" if reference else "generated",
              "n": len(frame), "quality": {**(quality or {}), "nonpositive_glycemia": nonpositive}, "gate_reason": reason,
              "estimands": {}, "diagnostics": None, "national_representativeness": False}
    for item in plan["estimands"]:
        report["estimands"][item["id"]] = ({"status": "unavailable", "coefficient": None, "unit": item["unit"], "n": len(frame),
                                            "rank": None, "condition_number": None, "reason": reason,
                                            "interval": _interval(reason)} if reason else _fit(frame, item, plan, reference))
    if reason is None:
        report["diagnostics"] = _diagnostics(frame)
    return report


def compare_estimates(reference, generated):
    result = {}
    for identifier, _, _, _ in _MODELS:
        ref, gen = reference["estimands"][identifier], generated["estimands"][identifier]
        interval = ref["interval"]
        available = ref["status"] == gen["status"] == "computed"
        direction = ("positive" if interval["lower"] > 0 else "negative" if interval["upper"] < 0 else "inconclusive") \
            if interval["status"] == "available" else "inconclusive"
        result[identifier] = {"status": "computed" if available else "unavailable", "reference": ref["coefficient"],
                              "generated": gen["coefficient"], "difference": gen["coefficient"] - ref["coefficient"] if available else None,
                              "reference_direction": direction, "generated_sign": None if gen["coefficient"] is None else
                              ("positive" if gen["coefficient"] > 0 else "negative" if gen["coefficient"] < 0 else "zero"),
                              "ratio": gen["coefficient"] / ref["coefficient"] if available and direction != "inconclusive" and ref["coefficient"] != 0 else None,
                              "interval_membership": bool(interval["lower"] <= gen["coefficient"] <= interval["upper"])
                              if available and interval["status"] == "available" else None}
    return result


def summarize_slots(reference, slots):
    expected = {(c, s, seed) for c in CONSTRUCTIONS for s in STAGES for seed in SEEDS}
    require(len(slots) == 12 and {(row["construction"], row["stage"], row["seed"]) for row in slots} == expected,
            "Final results must preserve all twelve planned slots")
    records = []
    for row in slots:
        require(row["status"] in {"success", "failed", "not_run"}, "Unknown slot status")
        require(row["status"] != "success" or row["analysis"] is not None, "Successful slot lacks its analysis")
        require(row["status"] == "success" or row["analysis"] is None, "Failed/absent slot must not supply estimates")
        records.append({**row, "comparison": compare_estimates(reference, row["analysis"]) if row["analysis"] else None})
    stages = {}
    for construction in CONSTRUCTIONS:
        for stage in STAGES:
            selected = [row for row in records if row["construction"] == construction and row["stage"] == stage]
            stages[f"{construction}_{stage}"] = {}
            for identifier, _, _, _ in _MODELS:
                values = [row["analysis"]["estimands"][identifier]["coefficient"] for row in selected
                          if row["analysis"] and row["analysis"]["estimands"][identifier]["status"] == "computed"]
                mc = len(values) == 3 and all(row["route"] == "generator.py" for row in selected)
                status = "incomplete" if len(values) < 3 else "not_assessed_direct_reuse" if not mc else \
                    "stable_positive" if min(values) > 0 else "stable_negative" if max(values) < 0 else "unresolved"
                stages[f"{construction}_{stage}"][identifier] = {"valid_seed_count": len(values), "direction_status": status,
                    "range": [min(values), max(values)] if values else None, "monte_carlo_credit": mc}
    return {"slots": records, "stages": stages, "global_score": None}


def runtime_versions():
    return {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__,
            "scipy": scipy.__version__, "pyreadstat": importlib.metadata.version("pyreadstat")}


def _tree_digest(directory):
    import hashlib
    import json
    files = {}
    if directory.exists():
        for path in sorted(directory.rglob("*")):
            relative = path.relative_to(directory).as_posix()
            _path(directory, relative, file=False)
            require(path.is_file() or path.is_dir(), "Unexpected filesystem entry")
            if path.is_file():
                files[relative] = sha256(path)
    return hashlib.sha256(json.dumps(files, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _reference(root, reference):
    exact_keys(reference, {"path", "sha256"}, where="evaluation file reference")
    path = _path(root, reference["path"])
    require(sha256(path) == reference["sha256"], "Evaluation-bound metadata changed")
    return path


def _final_inventory(root, inventory, release):
    exact_keys(inventory, {"schema_version", "status", "f2_release_sha256", "final_decisions", "controller_state_sha256", "slots"},
               where="final candidate inventory")
    require(type(inventory["schema_version"]) is int and inventory["schema_version"] == 1 and inventory["status"] == "final",
            "Candidate inventory is not final")
    require(inventory["f2_release_sha256"] == release["f2_release_sha256"] and
            inventory["controller_state_sha256"] == _tree_digest(root / "f2_controller"), "Final campaign state changed")
    # The existing controller cannot rerun a reserved stage. Every stage must be
    # reserved before reference reveal; early-stop closure needs separate review.
    for construction in CONSTRUCTIONS:
        for stage in STAGES:
            slot = f"{construction}_{stage}"
            request = read_json(_path(root, f"f2_controller/{slot}/run_request.json"))
            require(request["slot"] == slot and type(request["reserved_target_table_slots"]) is int and
                    request["reserved_target_table_slots"] == 3 and _same(request["seeds"], list(SEEDS)) and
                    request["release_sha256"] == release["f2_release_sha256"] and
                    request["candidate_freeze_sha256"] == sha256(_path(root, f"candidates/{slot}/freeze.json")),
                    "A permitted stage remains runnable or has an incoherent reservation")
    require(set(inventory["final_decisions"]) == set(CONSTRUCTIONS), "Both construction decisions must be final")
    for decision in inventory["final_decisions"].values():
        exact_keys(decision, {"decision", "reason"}, where="final construction decision")
        require(decision["decision"] in {"retain_initial", "revised", "stopped"}, "Invalid final construction decision")
        text(decision["reason"], "final decision reason")
    expected = {(c, s, seed) for c in CONSTRUCTIONS for s in STAGES for seed in SEEDS}
    slots = inventory["slots"]
    require(isinstance(slots, list) and len(slots) == 12 and
            {(row["construction"], row["stage"], row["seed"]) for row in slots} == expected, "Final inventory must contain all twelve slots")
    run_ids = {f"{c}_{s}_s{seed}" for c, s, seed in expected}
    executions = _path(root, "executions", file=False)
    if executions.exists():
        require(all(path.is_dir() and path.name in run_ids for path in executions.iterdir()), "Unplanned execution in final bundle")
    for row in slots:
        exact_keys(row, {"construction", "stage", "seed", "status", "reason", "route", "candidate_freeze_sha256",
                         "execution_sha256", "generated_sha256", "run_artifacts_sha256"}, where="final slot")
        require(type(row["seed"]) is int and row["status"] in {"success", "failed", "not_run"}, "Invalid final slot")
        text(row["reason"], "slot reason")
        slot = f'{row["construction"]}_{row["stage"]}'
        run_id, candidate = f'{slot}_s{row["seed"]}', "candidates/" + slot
        run = _path(root, "executions/" + run_id, file=False)
        if row["status"] == "not_run":
            require(not run.exists() and all(row[key] is None for key in
                    ("route", "candidate_freeze_sha256", "execution_sha256", "generated_sha256", "run_artifacts_sha256")),
                    "An existing execution cannot be omitted as not-run")
            continue
        require(row["route"] in {"generator.py", "generated.csv"}, "Unknown final candidate route")
        frozen = lifecycle.verify_candidate(root, candidate)
        require(frozen["route"] == row["route"] and sha256(root / candidate / "freeze.json") == row["candidate_freeze_sha256"],
                "Final candidate freeze changed")
        require(row["run_artifacts_sha256"] == (_tree_digest(run) if run.exists() else None), "Final execution artifacts changed")
        receipt_path = _path(run, "execution.json", file=False)
        if receipt_path.exists():
            receipt = execution.verify_execution(root, run_id)
            require(sha256(receipt_path) == row["execution_sha256"] and receipt["candidate"] == candidate and
                    receipt["limits"]["seed"] == row["seed"], "Final execution binding changed")
            require((receipt["status"] == "success") == (row["status"] == "success"), "Successful output cannot be labelled failed")
        else:
            require(row["status"] == "failed" and row["execution_sha256"] is None and
                    (root / "f2_controller" / slot / f'seed_{row["seed"]}_attempt.json').is_file(),
                    "Missing execution must have a bound failed attempt")
        if row["status"] == "success":
            require(sha256(_path(run, "output/generated.csv")) == row["generated_sha256"], "Final generated output changed")
        else:
            require(row["generated_sha256"] is None, "Failed slot cannot nominate a scientific output")
    require(any(row["status"] == "success" for row in slots), "No successful candidate: reference reveal is unnecessary")
    return slots


def _evaluation_gate(bundle, release):
    root = _bundle(bundle)
    release_path = _path(root, release)  # Missing release fails before any file content read.
    approval = read_json(release_path)
    exact_keys(approval, {"schema_version", "status", "f2_release_sha256", "protocol_sha256", "analysis_plan_sha256",
                          "evaluator_sha256", "runtime_versions", "final_inventory", "independent_review"}, where="evaluation release")
    require(type(approval["schema_version"]) is int and approval["schema_version"] == 1 and approval["status"] == "released",
            "Evaluation has not been released")
    require(approval["evaluator_sha256"] == sha256(__file__) and _same(approval["runtime_versions"], runtime_versions()),
            "Evaluator/runtime differs from evaluation release")
    require(sha256(_path(root, "F2_RELEASE.json")) == approval["f2_release_sha256"] and
            sha256(_path(root, "PROTOCOL.md")) == approval["protocol_sha256"] and
            sha256(_path(root, "analysis_plan.json")) == approval["analysis_plan_sha256"], "Released study documents changed")
    f2 = read_json(root / "F2_RELEASE.json")
    controller_path = Path(__file__).resolve().parents[1] / "controller/chns_f2_controller.py"
    require(sha256(controller_path) == f2["controller_sha256"], "Study controller changed")
    spec = importlib.util.spec_from_file_location("chns_f2_released_controller", controller_path)
    controller = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(controller)
    controller._release(root)  # Existing study release and independent-review gates, no source data read.
    review = read_json(_reference(root, approval["independent_review"]))
    exact_keys(review, {"schema_version", "decision", "reviewer_id", "coordinator_id", "independent", "reviewed_utc", "reason",
                        "approved_release"}, where="evaluation independent review")
    require(type(review["schema_version"]) is int and review["schema_version"] == 1 and review["decision"] == "approved" and
            review["independent"] is True, "Evaluation review is not approved")
    for key in ("reviewer_id", "coordinator_id", "reviewed_utc", "reason"):
        text(review[key], "evaluation review " + key)
    require(review["reviewer_id"].strip().casefold() != review["coordinator_id"].strip().casefold() and
            _same(review["approved_release"], {k: v for k, v in approval.items() if k != "independent_review"}),
            "Independent review does not cover this evaluation release")
    plan = validate_plan(read_json(root / "analysis_plan.json"))
    slots = _final_inventory(root, read_json(_reference(root, approval["final_inventory"])), approval)
    return root, plan, slots, sha256(release_path)


def _read_reference_files(reference_dir, plan):
    """Private reader: called only after release validation and reservation."""
    directory = _bundle(reference_dir)
    paths = {}
    for item in plan["input_files"]:
        path = _path(directory, item["file"])
        require(sha256(path) == item["sha256"], "Reference release file hash changed")
        paths[item["file"]] = path
    import pyreadstat  # Deliberately imported only after the read gate and file hashes.
    frames = {}
    for item in plan["input_files"]:
        columns = [item["key"]] + ([item["wave"]] if item["wave"] else []) + item["columns"]
        frames[item["file"]], _ = pyreadstat.read_sas7bdat(str(paths[item["file"]]), usecols=columns, user_missing=False)
    return frames


def evaluate_released(bundle, reference_dir, *, release="EVALUATION_RELEASE.json"):
    root, plan, inventory, release_hash = _evaluation_gate(bundle, release)
    destination = _path(root, "evaluation_results", file=False)
    require(not destination.exists(), "One-time evaluation already reserved; no automatic retry")
    destination.mkdir()
    execution._write(destination / "REQUEST.json", {"evaluation_release_sha256": release_hash, "evaluator_sha256": sha256(__file__)})
    try:
        frames = _read_reference_files(reference_dir, plan)
        frame, quality = prepare_reference_frames(frames, plan)
        reference = analyze(frame, plan, reference=True, quality=quality)
        task = read_json(root / "task.json")
        slots = []
        for item in inventory:
            result = None
            if item["status"] == "success":
                run_id = f'{item["construction"]}_{item["stage"]}_s{item["seed"]}'
                generated = lifecycle.read_table(_path(root, f"executions/{run_id}/output/generated.csv"), task, output=True)
                result = analyze(generated, plan, reference=False)
            slots.append({key: item[key] for key in ("construction", "stage", "seed", "status", "route", "reason")} | {"analysis": result})
        report = {"schema_version": 1, "evaluation_release_sha256": release_hash, "runtime_versions": runtime_versions(),
                  "reference": reference, **summarize_slots(reference, slots), "independent_recomputation": "pending",
                  "limitations": ["Released selected sample, not national design-based inference.",
                                  "Native missing reasons may be collapsed by the reader; no positive sentinel masks are invented.",
                                  "Cluster inference, release quality and measurement transport remain assumptions.",
                                  "No post-reveal tuning or selective output/estimand reporting is authorized."]}
        execution._write(destination / "REPORT.json", report)
        return report
    except Exception as error:
        execution._write(destination / "FAILURE.json", {"type": type(error).__name__, "message": str(error),
                                                        "evaluation_release_sha256": release_hash})
        raise
