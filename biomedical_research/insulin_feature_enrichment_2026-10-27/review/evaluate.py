"""Freeze predictor-only analyses, then evaluate a locked manifest after release.

The evaluator deliberately has no built-in dataset paths, target coefficients, signs,
success thresholds, individual-value accuracy metric, or outcome-based model selection.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import t


HERE = Path(__file__).resolve().parent
MISSING = {"", "nan", "na", "null", "none"}
PREDICTORS = ("row_id", "bmi", "age", "sex")
WARNINGS = [
    "Associations are descriptive, not causal, and apply to the specified scored domain.",
    "Reserved target-specific recovery is not discovery independent of imported external evidence.",
    "Synthetic intervals condition on generated outcomes and survey design; they are not calibrated uncertainty about the wholly unobserved true outcome.",
    "Between-draw spread is descriptive; fixed-parameter residual draws omit source-estimation and transport uncertainty. No Rubin pooling is used.",
    "No effect-difference significance test, equivalence claim, or overall pass/fail is calculated.",
    "Residual degrees of freedom equal full-spine design degrees of freedom minus (model rank - 1); sparse domains can still have unstable variance estimates.",
]


class EvaluationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise EvaluationError(message)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def json_write(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def read_table(path, mapping=None):
    """Read exact decoded CSV cells; mapping is canonical-name -> CSV-name."""
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        header = next(csv.reader(handle), [])
    require(header and len(header) == len(set(header)), f"Missing/duplicate CSV header: {path}")
    raw = pd.read_csv(path, dtype=str, keep_default_na=False)
    require(not raw.columns.duplicated().any(), f"Duplicate columns: {path}")
    mapping = mapping or {}
    rename = {actual: canonical for canonical, actual in mapping.items()}
    frame = raw.rename(columns=rename)
    require(not frame.columns.duplicated().any(), f"Column mapping collision: {path}")
    require("row_id" in frame, f"Missing row_id: {path}")
    require(frame.row_id.ne("").all() and frame.row_id.is_unique, f"Empty/duplicate row_id: {path}")
    return frame


def numeric(frame, column):
    require(column in frame, f"Missing column: {column}")
    try:
        # Python's correctly rounded string-to-float conversion matches the
        # runner's round-trip contract; pandas.to_numeric may differ by one ULP.
        values = np.asarray([float(value) for value in frame[column]], dtype=float)
    except (ValueError, TypeError) as exc:
        raise EvaluationError(f"Column {column} must contain finite numbers") from exc
    require(np.isfinite(values).all(), f"Column {column} must contain finite numbers")
    return values


def fingerprint(frame):
    """Exact cell fingerprint independent of CSV row order and serialization."""
    records = frame.loc[:, PREDICTORS].sort_values("row_id").to_dict("records")
    return hashlib.sha256(json.dumps(records, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def observed_predictors(frame):
    for column in PREDICTORS:
        require(column in frame, f"Observed table missing {column}")
    bmi, age = numeric(frame, "bmi"), numeric(frame, "age")
    require((bmi > 0).all(), "BMI must be positive")
    require((age >= 20).all(), "This prespecified evaluator uses adults aged >=20")
    if "insulin" in frame:
        require(frame.insulin.str.lower().isin(MISSING).all(), "Observed insulin column is not wholly withheld")
    require(not frame.sex.str.lower().isin(MISSING).any(), "Observed sex is missing")
    return bmi, age


def freeze(observed, output, schema=None):
    mapping = (schema or {}).get("observed", {})
    frame = read_table(observed, mapping)
    bmi, age = observed_predictors(frame)
    levels = sorted(frame.sex.unique().tolist())
    require(len(levels) == 2, "Exactly two documented sex codes required for this pilot")
    knots = np.quantile(bmi, [0.10, 0.50, 0.90]).tolist()
    locations = np.quantile(bmi, [0.25, 0.50, 0.75]).tolist()
    require(np.all(np.diff(knots) > 0), "BMI spline knots are not distinct")
    require(np.all(np.diff(locations) > 0), "BMI contrast locations are not distinct")
    spec = {
        "analysis_version": "1.0", "base_spec_sha256": sha256(HERE / "analysis_spec.json"),
        "evaluator_sha256": sha256(__file__), "observed_sha256": sha256(observed),
        "predictor_fingerprint": fingerprint(frame), "row_count": len(frame),
        "observed_column_mapping": mapping, "bmi_knots": knots,
        "bmi_contrast_locations": locations, "bmi_center": float(np.median(bmi)),
        "age_center": float(np.mean(age)), "sex_reference": levels[0],
        "sex_comparison": levels[1], "sex_interpretation": f"code {levels[1]} versus code {levels[0]}; use metadata for labels",
        "quantile_method": "numpy linear interpolation; unweighted observed predictors only",
        "domain": "All observed rows; exact one-to-one reference matching required",
    }
    require(not Path(output).exists(), "Frozen specification already exists; choose a new revision path")
    json_write(output, spec)
    return spec


def spline_term(bmi, knots):
    """One restricted cubic nonlinear term for three knots, scaled by range squared."""
    x = np.asarray(bmi, dtype=float)
    k1, k2, k3 = np.asarray(knots, dtype=float)
    require(k1 < k2 < k3, "Invalid spline knots")
    return (np.maximum(x-k1, 0)**3 - (k3-k1)/(k3-k2)*np.maximum(x-k2, 0)**3
            + (k2-k1)/(k3-k2)*np.maximum(x-k3, 0)**3) / (k3-k1)**2


def model_matrices(frame, spec):
    bmi, age = numeric(frame, "bmi"), numeric(frame, "age")
    require(set(frame.sex) <= {spec["sex_reference"], spec["sex_comparison"]}, "Unfrozen sex code")
    b = (bmi-spec["bmi_center"])/5
    a = (age-spec["age_center"])/10
    s = (frame.sex.to_numpy() == spec["sex_comparison"]).astype(float)
    one = np.ones(len(frame))
    return {
        "A": (np.column_stack([one, b]), ["intercept", "bmi_per_5"]),
        "B": (np.column_stack([one, b, a, s]), ["intercept", "bmi_per_5", "age_per_10", "sex_comparison"]),
        "C": (np.column_stack([one, b, spline_term(bmi, spec["bmi_knots"]), a, s]),
              ["intercept", "bmi_linear_per_5", "bmi_nonlinear", "age_per_10", "sex_comparison"]),
        "D": (np.column_stack([one, b, a, s, b*s]),
              ["intercept", "bmi_reference_per_5", "age_per_10", "sex_at_center", "bmi_sex_interaction"]),
    }


def validate_spine(spine, domain):
    for column in ("weight", "stratum", "psu"):
        require(column in spine, f"Spine missing {column}")
    require((numeric(spine, "weight") > 0).all(), "Full spine must contain only positive fasting weights")
    require(not spine[["stratum", "psu"]].isin([""]).any().any(), "Missing design identifier")
    require(set(domain.row_id) <= set(spine.row_id), "Scored row absent from full design spine")
    pairs = spine[["stratum", "psu"]].drop_duplicates()
    counts = pairs.groupby("stratum", sort=False).size()
    require((counts >= 2).all(), "Singleton stratum in full spine: cannot use prespecified Taylor estimator")
    full = spine.set_index("row_id").loc[domain.row_id]
    for column in ("stratum", "psu"):
        require(np.array_equal(full[column].to_numpy(), domain[column].to_numpy()), f"Domain/spine {column} mismatch")
    require(np.array_equal(numeric(full, "weight"), numeric(domain, "weight")), "Domain/spine weight mismatch")
    return pairs


def taylor_fit(X, y, domain, spine):
    """WLS point estimates and stratified-PSU Taylor covariance for a domain.

    Outside-domain rows have zero estimating-equation scores. Their PSU/stratum
    membership is still retained in the full spine when centering PSU totals.
    """
    X, y = np.asarray(X, float), np.asarray(y, float)
    require(X.ndim == 2 and y.shape == (len(X),) and len(X) == len(domain), "Fit dimensions disagree")
    require(np.isfinite(X).all() and np.isfinite(y).all(), "Nonfinite model inputs")
    require(np.linalg.matrix_rank(X) == X.shape[1], "Rank-deficient prespecified model")
    pairs = validate_spine(spine, domain)
    # Common scaling cancels from sandwich and prevents huge survey totals.
    w = numeric(domain, "weight")
    w = w / w.mean()
    bread = X.T @ (w[:, None]*X)
    inv_bread = np.linalg.inv(bread)
    beta = np.linalg.solve(bread, X.T @ (w*y))
    scores = (w*(y-X@beta))[:, None]*X
    score_names = [f"score_{i}" for i in range(X.shape[1])]
    tagged = domain[["stratum", "psu"]].reset_index(drop=True).copy()
    tagged[score_names] = scores
    totals = tagged.groupby(["stratum", "psu"], sort=False)[score_names].sum()
    full_index = pd.MultiIndex.from_frame(pairs)
    totals = totals.reindex(full_index, fill_value=0)
    meat = np.zeros_like(bread)
    for _, group in totals.groupby(level="stratum", sort=False):
        values = group.to_numpy()
        centered = values-values.mean(axis=0)
        meat += len(values)/(len(values)-1) * centered.T @ centered
    covariance = inv_bread @ meat @ inv_bread
    covariance = (covariance+covariance.T)/2
    design_df = len(pairs)-pairs.stratum.nunique()
    residual_df = design_df-(X.shape[1]-1)
    domain_pairs = domain[["stratum", "psu"]].drop_duplicates()
    diagnostics = {
        "domain_n": len(domain), "full_spine_n": len(spine),
        "full_strata": int(pairs.stratum.nunique()), "full_psus": len(pairs),
        "domain_strata": int(domain_pairs.stratum.nunique()), "domain_psus": len(domain_pairs),
        "design_df": int(design_df), "residual_df": int(residual_df),
        "rank": X.shape[1], "weighted_domain_total": float(numeric(domain, "weight").sum()),
        "kish_weight_effective_n_descriptive": float(w.sum()**2/(w@w)),
        "interval_status": "available" if residual_df > 0 else "insufficient_design_degrees_of_freedom",
    }
    return beta, covariance, diagnostics


def linear_contrast(beta, covariance, contrast, df):
    c = np.asarray(contrast, dtype=float)
    estimate = float(c@beta)
    variance = float(c@covariance@c)
    require(variance >= -1e-10, "Negative contrast variance beyond numerical tolerance")
    se = float(np.sqrt(max(0, variance)))
    lower = upper = None
    if df > 0:
        margin = float(t.ppf(0.975, df))*se
        lower, upper = estimate-margin, estimate+margin
    def safe_exp(value):
        if value is None or value > np.log(np.finfo(float).max):
            return None
        return float(np.exp(value))
    return {"estimate_log_scale": estimate, "standard_error": se,
            "ci95_low_log_scale": lower, "ci95_high_log_scale": upper,
            "exp_estimate": safe_exp(estimate), "exp_ci95_low": safe_exp(lower),
            "exp_ci95_high": safe_exp(upper)}


def contrasts(spec):
    q1, q2, q3 = spec["bmi_contrast_locations"]
    r1, r2, r3 = spline_term([q1, q2, q3], spec["bmi_knots"])
    curvature = 5*((r3-r2)/(q3-q2)-(r2-r1)/(q2-q1))
    return {
        "A": [("overall_bmi_per_5", [0, 1], "input-consistency")],
        "B": [("adjusted_bmi_per_5", [0, 1, 0, 0], "reserved-primary"),
              ("adjusted_age_per_10", [0, 0, 1, 0], "reserved-secondary"),
              ("adjusted_sex_comparison", [0, 0, 0, 1], "reserved-secondary")],
        "C": [("upper_minus_lower_bmi_slope_per_5", [0, 0, curvature, 0, 0], "reserved-shape")],
        "D": [("sex_difference_bmi_slope_per_5", [0, 0, 0, 0, 1], "reserved-subgroup"),
              ("sex_reference_bmi_slope_per_5", [0, 1, 0, 0, 0], "reserved-subgroup-supporting"),
              ("sex_comparison_bmi_slope_per_5", [0, 1, 0, 0, 1], "reserved-subgroup-supporting")],
    }


def weighted_correlation(x, y, w):
    w = np.asarray(w, float)/np.sum(w)
    xc = np.asarray(x)-w@x
    yc = np.asarray(y)-w@y
    denom = float(np.sqrt((w@(xc*xc))*(w@(yc*yc))))
    return float((w@(xc*yc))/denom) if denom > 0 else None


def analyze(frame, insulin, domain, spine, spec):
    insulin = np.asarray(insulin, float)
    require(insulin.shape == (len(frame),), "Insulin row count mismatch")
    require(np.isfinite(insulin).all() and (insulin > 0).all(), "Insulin must be finite and positive")
    log_insulin = np.log(insulin)
    endpoints, fits = [], {}
    all_contrasts = contrasts(spec)
    for model, (X, names) in model_matrices(frame, spec).items():
        beta, covariance, diagnostics = taylor_fit(X, log_insulin, domain, spine)
        fits[model] = {"coefficient_names": names, "coefficients": beta.tolist(),
                       "covariance": covariance.tolist(), "diagnostics": diagnostics}
        for name, c, label in all_contrasts[model]:
            endpoints.append({"analysis": model, "endpoint": name, "label": label,
                              **linear_contrast(beta, covariance, c, diagnostics["residual_df"])})
    bmi, w = numeric(frame, "bmi"), numeric(domain, "weight")
    return {"endpoints": endpoints, "fits": fits, "descriptive_correlations": {
        "bmi_raw_insulin": weighted_correlation(bmi, insulin, w),
        "bmi_log_insulin": weighted_correlation(bmi, log_insulin, w)}}


def match_reference(observed, reference, spine):
    require(set(reference.row_id) == set(observed.row_id), "Reference and observed row ID sets differ")
    reference = reference.set_index("row_id").loc[observed.row_id].reset_index()
    # Optional reference predictors must agree; primary predictor source remains observed.
    for column in ("bmi", "age", "sex"):
        if column in reference:
            if column in ("bmi", "age"):
                require(np.array_equal(numeric(reference, column), numeric(observed, column)), f"Reference {column} mismatch")
            else:
                require(np.array_equal(reference[column], observed[column]), f"Reference {column} mismatch")
    validate_spine(spine, reference)
    return reference


def match_generated(observed, generated):
    require(set(generated.row_id) == set(observed.row_id), "Generated and observed row ID sets differ")
    row_order_preserved = generated.row_id.tolist() == observed.row_id.tolist()
    generated = generated.set_index("row_id").loc[observed.row_id].reset_index()
    for column in observed.columns:
        if column == "insulin":
            continue
        require(column in generated, f"Generated table lost observed column {column}")
        if column in ("bmi", "age"):
            unchanged = np.array_equal(numeric(observed, column), numeric(generated, column))
        elif column == "sex":
            try:
                # Numeric category codes can be serialized as 1 or 1.0.
                unchanged = np.array_equal(numeric(observed, column), numeric(generated, column))
            except EvaluationError:
                unchanged = np.array_equal(observed[column].to_numpy(), generated[column].to_numpy())
        else:
            unchanged = np.array_equal(observed[column].to_numpy(), generated[column].to_numpy())
        require(unchanged, f"Generated table changed observed cells in {column}")
    return numeric(generated, "insulin"), row_order_preserved


def manifest_path(base, path):
    p = Path(path)
    return p if p.is_absolute() else base/p


def evaluate(observed_path, reference_path, spine_path, manifest_path_arg, output):
    manifest_file = Path(manifest_path_arg).resolve()
    manifest = json.loads(manifest_file.read_text(encoding="utf-8-sig"))
    base = manifest_file.parent
    spec_record = manifest["analysis_spec"]
    spec_path = manifest_path(base, spec_record["path"])
    require(sha256(spec_path) == spec_record["sha256"], "Frozen analysis spec hash mismatch")
    spec = json.loads(spec_path.read_text(encoding="utf-8-sig"))
    require(spec["base_spec_sha256"] == sha256(HERE/"analysis_spec.json"), "Base analysis specification changed after freeze")
    require(spec["evaluator_sha256"] == sha256(__file__), "Evaluator code changed after freeze")
    require(sha256(observed_path) == spec["observed_sha256"] == manifest["observed_sha256"], "Observed input hash mismatch")
    observed = read_table(observed_path, spec["observed_column_mapping"])
    observed_predictors(observed)
    require(fingerprint(observed) == spec["predictor_fingerprint"], "Frozen predictor fingerprint mismatch")
    columns = manifest.get("columns", {})
    draws = manifest["draws"]
    require(isinstance(draws, list) and len(draws) > 0, "Manifest has no generated draws")
    counts = Counter(d["model"] for d in draws)
    require(max(counts.values()) <= 20, "More than 20 draws for a model revision")
    require(len({(d["model"], str(d["draw_id"])) for d in draws}) == len(draws), "Duplicate model/draw ID")
    # Validate every generated artifact before opening the hidden reference.
    validated_draws = []
    for draw in draws:
        path = manifest_path(base, draw["path"])
        require(sha256(path) == draw["sha256"], f"Generated file hash mismatch: {draw['model']}/{draw['draw_id']}")
        generated = read_table(path, draw.get("columns", columns.get("generated", {})))
        insulin, preserved = match_generated(observed, generated)
        require((insulin > 0).all(), "Nonpositive generated insulin")
        validated_draws.append((draw, insulin, preserved))
    # Read-only commitments bind the hidden files without tuning to their contents.
    require(sha256(reference_path) == manifest["reference_sha256"], "Reference commitment hash mismatch")
    require(sha256(spine_path) == manifest["spine_sha256"], "Spine commitment hash mismatch")
    if "outputs_freeze" in manifest:
        locked = manifest["outputs_freeze"]
        require(sha256(manifest_path(base, locked["path"])) == locked["sha256"], "Root output-freeze hash mismatch")
    spine = read_table(spine_path, columns.get("spine", {}))
    reference = read_table(reference_path, columns.get("reference", {}))
    reference = match_reference(observed, reference, spine)
    true = analyze(observed, numeric(reference, "insulin"), reference, spine, spec)
    true_lookup = {r["endpoint"]: r for r in true["endpoints"]}
    results, rows = [], []
    for row in true["endpoints"]:
        rows.append({"source": "reference", "model_revision": "reference", "draw_id": "reference", **row})
    for draw, insulin, preserved in validated_draws:
        result = analyze(observed, insulin, reference, spine, spec)
        for row in result["endpoints"]:
            difference = row["estimate_log_scale"]-true_lookup[row["endpoint"]]["estimate_log_scale"]
            row["signed_difference_from_reference"] = difference
            row["absolute_difference_from_reference"] = abs(difference)
            rows.append({"source": "generated", "model_revision": draw["model"], "draw_id": str(draw["draw_id"]), **row})
        results.append({"model_revision": draw["model"], "draw_id": str(draw["draw_id"]),
                        "observed_cells_preserved": True, "row_order_preserved": preserved, **result})
    table = pd.DataFrame(rows)
    summaries = []
    generated_rows = table[table.source == "generated"]
    for (revision, endpoint), group in generated_rows.groupby(["model_revision", "endpoint"], sort=False):
        values = group.estimate_log_scale.to_numpy()
        target = true_lookup[endpoint]["estimate_log_scale"]
        summaries.append({"model_revision": revision, "endpoint": endpoint, "draw_count": len(values),
                          "mean_estimate": float(values.mean()), "between_draw_sd": float(values.std(ddof=1)) if len(values)>1 else None,
                          "min_estimate": float(values.min()), "max_estimate": float(values.max()),
                          "signed_mean_difference": float(values.mean()-target),
                          "mean_absolute_difference": float(np.abs(values-target).mean())})
    destination = Path(output)
    require(not (destination/"evaluation.json").exists(), "Evaluation output already exists; use a new revision directory")
    destination.mkdir(parents=True, exist_ok=True)
    payload = {"warnings": WARNINGS, "frozen_analysis": spec, "manifest_sha256": sha256(manifest_file),
               "reference_sha256": sha256(reference_path), "spine_sha256": sha256(spine_path),
               "reference": true, "generated": results, "draw_summaries": summaries}
    json_write(destination/"evaluation.json", payload)
    table.to_csv(destination/"endpoints.csv", index=False)
    pd.DataFrame(summaries).to_csv(destination/"draw_summaries.csv", index=False)
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    f = sub.add_parser("freeze", help="Freeze specification using observed predictors only")
    f.add_argument("--observed", required=True)
    f.add_argument("--output", required=True)
    f.add_argument("--schema", help='Optional JSON {"observed": {"canonical_name": "csv_name"}}')
    e = sub.add_parser("evaluate", help="Run only after explicit release and artifact freeze")
    for name in ("observed", "reference", "spine", "run-manifest", "output"):
        e.add_argument("--"+name, required=True)
    args = parser.parse_args()
    if args.command == "freeze":
        schema = json.loads(Path(args.schema).read_text(encoding="utf-8-sig")) if args.schema else None
        spec = freeze(args.observed, args.output, schema)
        print(json.dumps({"frozen_analysis": str(Path(args.output).resolve()), "sha256": sha256(args.output),
                          "rows": spec["row_count"], "predictors_only": True}))
    else:
        payload = evaluate(args.observed, args.reference, args.spine, args.run_manifest, args.output)
        print(json.dumps({"output": str(Path(args.output).resolve()), "generated_draws": len(payload["generated"])}))


if __name__ == "__main__":
    main()
