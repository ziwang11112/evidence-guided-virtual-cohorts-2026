"""Independent M11 postrelease arithmetic audit; never changes sealed inputs.

Does not import the campaign or evaluator. Outputs only aggregate audit results.
"""
from pathlib import Path
import datetime
import hashlib
import json
import math

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "postrun_arithmetic_audit.json"
TOL = 1e-10


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def read_csv(path):
    return pd.read_csv(path, dtype={"row_id": str}, float_precision="round_trip")


def mean(values, weights):
    # Independent raw-weight arithmetic with compensated Python summation.
    return math.fsum(float(a) * float(b) for a, b in zip(values, weights)) / math.fsum(map(float, weights))


def quantile(values, weights, probability):
    # Binary-search the original-array CDF at candidate values. No binning,
    # normalized weights, cumulative-weight array, or evaluator function is used.
    support = sorted(set(map(float, values)))
    total = math.fsum(map(float, weights))
    target = probability * total
    lo, hi = 0, len(support) - 1
    while lo < hi:
        middle = (lo + hi) // 2
        mass = math.fsum(float(w) for y, w in zip(values, weights) if y <= support[middle])
        if mass >= target:
            hi = middle
        else:
            lo = middle + 1
    return support[lo]


def estimates(observed, values, weights):
    age = observed.age_years.to_numpy(dtype=float)
    bmi = observed.bmi_kg_m2.to_numpy(dtype=float)
    female = observed.sex.eq("female").to_numpy(dtype=float)
    result = {}
    for sex in ["male", "female"]:
        take = observed.sex.eq(sex).to_numpy()
        result["median_" + sex] = quantile(values[take], weights[take], .5) if take.any() else None
        for lo, hi in [(20, 39), (40, 59), (60, 79)]:
            take_cell = take & (age >= lo) & (age <= hi)
            key = f"mean_{sex}_{lo}_{hi}"
            result[key] = mean(values[take_cell], weights[take_cell]) if take_cell.any() else None
            result[key + "_n"] = int(take_cell.sum())
    result["q90_all"] = quantile(values, weights, .9)
    result["mean_all"] = mean(values, weights)
    # Independent centered/scaled normal equations, using compensated raw-weight
    # sums. The evaluator instead uses square-root-weighted np.linalg.lstsq.
    features = np.column_stack([age / 10, bmi / 5, female])
    center = np.array([mean(features[:, j], weights) for j in range(3)])
    scale = np.array([math.sqrt(mean((features[:, j] - center[j]) ** 2, weights)) for j in range(3)])
    z = np.column_stack([np.ones(len(values)), (features - center) / scale])
    gram = np.array([[mean(z[:, j] * z[:, k], weights) for k in range(4)] for j in range(4)])
    rhs = np.array([mean(z[:, j] * values, weights) for j in range(4)])
    if np.linalg.matrix_rank(gram) == 4:
        transformed = np.linalg.solve(gram, rhs)
        slopes = transformed[1:] / scale
        beta = np.r_[transformed[0] - np.dot(slopes, center), slopes]
        for key, value in zip(["intercept", "age_per_10y", "bmi_per_5", "female_offset"], beta):
            result[key] = float(value)
    else:
        result.update({key: None for key in ["intercept", "age_per_10y", "bmi_per_5", "female_offset"]})
    return result


def discrepancy(reference, generated):
    def absolute(key):
        return None if reference[key] is None or generated[key] is None else abs(reference[key] - generated[key])
    primary = [absolute("median_" + s) for s in ["male", "female"]]
    cells = [absolute(f"mean_{s}_{lo}_{hi}") for s in ["male", "female"] for lo, hi in [(20, 39), (40, 59), (60, 79)]]
    return {
        "sex_median_mae": None if None in primary else math.fsum(primary) / 2,
        "age_sex_cell_mean_mae": None if None in cells else math.fsum(cells) / 6,
        "q90_absolute_error": absolute("q90_all"),
        "age_slope_absolute_error": absolute("age_per_10y"),
        "bmi_slope_absolute_error": absolute("bmi_per_5"),
    }


def main():
    release_path = HERE / "release.json"
    release = read_json(release_path)
    assert sha(release["launch"]["path"]) == release["launch"]["sha256"]
    launch = read_json(release["launch"]["path"])
    protocol = read_json(HERE / "protocol.json")
    expected = {(f, a, s) for f in protocol["families"] for a in protocol["arms"] for s in protocol["target_seeds"]}
    planned = {(e["family"], e["arm"], e["seed"]): e for e in launch["schedule"]}
    actual = [(e["family"], e["arm"], e["seed"]) for e in release["executions"]]
    assert set(planned) == set(actual) == expected and len(actual) == len(set(actual)) == 24
    for binding in launch["bindings"]:
        assert sha(binding["path"]) == binding["sha256"], "Launch binding changed"

    input_paths = {name: HERE / path for name, path in {
        "observed": "custodian/visible/observed.csv",
        "reference": "custodian/private/reference.csv",
        "design_weights": "custodian/private/design_weights.csv",
    }.items()}
    preparation = read_json(HERE / "custodian/preparation_receipt.json")
    for name, path in input_paths.items():
        assert sha(path) == preparation["artifacts"][name]["sha256"]
    observed = read_csv(input_paths["observed"])
    reference = read_csv(input_paths["reference"])
    design = read_csv(input_paths["design_weights"])
    assert list(observed.columns) == ["row_id", "age_years", "sex", "bmi_kg_m2"]
    assert list(reference.columns) == ["row_id", "hba1c_pct"]
    assert list(design.columns) == ["row_id", "weight", "stratum", "psu"]
    assert observed.row_id.is_unique and reference.row_id.equals(observed.row_id) and design.row_id.equals(observed.row_id)
    weights = design.weight.to_numpy(dtype=float)
    assert np.isfinite(weights).all() and (weights > 0).all()
    real = estimates(observed, reference.hba1c_pct.to_numpy(dtype=float), weights)

    saved = read_json(HERE / "results/analysis.json")
    assert saved["release_sha256"] == sha(release_path) and saved["n"] == len(observed)
    saved_points = {(e["family"], e["arm"], e["seed"]): e["points"] for e in saved["generated"]}
    saved_errors = read_csv(HERE / "results/errors.csv").set_index(["family", "arm", "seed"])
    saved_pairs = read_csv(HERE / "results/paired_changes.csv").set_index(["family", "arm", "seed"])
    assert set(saved_points) == set(saved_errors.index) == expected
    assert len(saved_errors) == 24
    assert set(saved_pairs.index) == {k for k in expected if k[1] != "initial"} and len(saved_pairs) == 18
    mismatches, maxima, comparisons = [], {}, {}

    def compare(category, label, computed, reported):
        missing_computed = computed is None or (isinstance(computed, float) and math.isnan(computed))
        missing_reported = reported is None or (isinstance(reported, float) and math.isnan(reported))
        comparisons[category] = comparisons.get(category, 0) + 1
        if missing_computed or missing_reported:
            if missing_computed != missing_reported:
                mismatches.append({"category": category, "label": label, "kind": "missingness_mismatch"})
            return
        difference = abs(float(computed) - float(reported))
        maxima[category] = max(maxima.get(category, 0.0), difference)
        if not math.isfinite(difference) or difference > TOL:
            mismatches.append({"category": category, "label": label, "kind": "numerical_mismatch", "absolute_difference": difference})

    assert set(real) == set(saved["reference"])
    for key in real:
        compare("reference_points", key, real[key], saved["reference"][key])
    computed_points, computed_errors = {}, {}
    verified_outputs = []
    for entry in release["executions"]:
        key = (entry["family"], entry["arm"], entry["seed"])
        plan = planned[key]
        assert entry["run_id"] == plan["run_id"]
        assert sha(entry["generated"]["path"]) == entry["generated"]["sha256"]
        assert sha(entry["receipt"]["path"]) == entry["receipt"]["sha256"]
        receipt = read_json(entry["receipt"]["path"])
        assert receipt["status"] == "success" and receipt["candidate"] == plan["candidate"]
        assert receipt["limits"]["seed"] == key[2] and receipt["candidate_freeze_sha256"] == plan["freeze_sha256"]
        table = read_csv(entry["generated"]["path"])
        assert list(table.columns) == list(observed.columns) + ["hba1c_pct"]
        assert table.row_id.is_unique and table[observed.columns].equals(observed)
        values = table.hba1c_pct.to_numpy(dtype=float)
        assert np.isfinite(values).all()
        p = estimates(observed, values, weights)
        e = discrepancy(real, p)
        computed_points[key], computed_errors[key] = p, e
        assert set(p) == set(saved_points[key])
        for metric in p:
            compare("generated_points", str(key) + ":" + metric, p[metric], saved_points[key][metric])
        for metric in e:
            compare("error_aggregates", str(key) + ":" + metric, e[metric], saved_errors.loc[key, metric])
        verified_outputs.append({"family": key[0], "arm": key[1], "seed": key[2], "generated_sha256": entry["generated"]["sha256"]})

    changes = {metric: [] for metric in ["sex_median_mae", "age_sex_cell_mean_mae", "q90_absolute_error"]}
    preservation_deltas = {metric: [] for metric in ["age_per_10y", "bmi_per_5"]}
    for key in sorted(expected):
        if key[1] == "initial":
            continue
        base = (key[0], "initial", key[2])
        for metric in changes:
            a, b = computed_errors[base][metric], computed_errors[key][metric]
            change = None if a is None or b is None else b - a
            changes[metric].append(change)
            compare("paired_error_changes", str(key) + ":" + metric, change, saved_pairs.loc[key, metric + "_change"])
        for metric in preservation_deltas:
            a, b = computed_points[base][metric], computed_points[key][metric]
            delta = None if a is None or b is None else b - a
            preservation_deltas[metric].append(delta)
            compare("paired_preservation_deltas", str(key) + ":" + metric, delta, saved_pairs.loc[key, metric + "_change"])
            independent_flag = None if delta is None else abs(delta) <= TOL
            reported_flag = saved_pairs.loc[key, metric + "_preserved"]
            if independent_flag is not None:
                assert isinstance(reported_flag, (bool, np.bool_)) and bool(reported_flag) == independent_flag
            else:
                assert pd.isna(reported_flag)

    def direction_counts(values):
        present = [v for v in values if v is not None]
        return {"increased_error": sum(v > 0 for v in present), "decreased_error": sum(v < 0 for v in present), "equal_error": sum(v == 0 for v in present), "unassessed": len(values) - len(present)}

    audit = {
        "schema_version": 1, "reviewed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "role": "Authorized target custodian and independent arithmetic/code reviewer; postrelease access to real outcomes, not outcome-blind review",
        "script_sha256": sha(Path(__file__)), "release_sha256": sha(release_path),
        "result_file_hashes": {name: sha(HERE / "results" / name) for name in ["analysis.json", "errors.csv", "paired_changes.csv"]},
        "input_hashes": {name: sha(path) for name, path in input_paths.items()},
        "observable_rows": len(observed), "released_tables": len(actual), "paired_comparisons": 18,
        "method": {"weighted_quantiles": "Binary search of the original-array weighted CDF using math.fsum of raw weights at each candidate support value; left inverse, no interpolation", "weighted_means": "math.fsum of raw weight-value products divided by math.fsum weights", "wls": "Weighted centered/scaled covariates, compensated normal-equation moments, np.linalg.solve, then transform coefficients back", "independence": "No campaign/evaluator code imported", "absolute_comparison_tolerance": TOL},
        "checks": {"all_launch_bindings_unchanged": True, "canonical_input_hashes_match_custody_receipt": True, "release_schedule_complete_unique": True, "all_output_and_receipt_hashes_match": True, "candidate_seed_freeze_associations_match": True, "all_ids_and_visible_covariates_preserved": True, "preservation_flags_match": True},
        "comparison_counts": comparisons, "maximum_absolute_discrepancy": maxima,
        "mismatches": mismatches, "passed": not mismatches,
        "paired_error_change_counts": {metric: direction_counts(v) for metric, v in changes.items()},
        "paired_preservation": {metric: {"assessed": sum(v is not None for v in values), "within_1e_10": sum(v is not None and abs(v) <= TOL for v in values), "maximum_absolute_delta": max(abs(v) for v in values if v is not None)} for metric, values in preservation_deltas.items()},
        "verified_output_hashes": verified_outputs,
        "interpretation_check": "Counts describe the paired scenario/seed comparisons; seeds and repeated rows are not independent replications. Preserved slopes are an additive-location implementation identity, not evidence of learned target relationships.",
        "boundary": "No inputs, candidates, evaluator code, source_audit files or launch bindings modified. No target data or audit findings sent to source scientist. No row-level outcomes are included in this report."
    }
    assert not OUT.exists(), "Preserve an existing audit rather than overwriting it"
    OUT.write_text(json.dumps(audit, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"audit_path": str(OUT), "passed": audit["passed"], "rows": len(observed), "tables": len(actual), "maximum_absolute_discrepancy": maxima, "paired_error_change_counts": audit["paired_error_change_counts"], "paired_preservation": audit["paired_preservation"], "mismatch_count": len(mismatches)}, allow_nan=False))


if __name__ == "__main__":
    main()
