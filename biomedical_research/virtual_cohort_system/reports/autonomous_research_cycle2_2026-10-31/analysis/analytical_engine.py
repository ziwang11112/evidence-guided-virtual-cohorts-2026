"""Fixed, pure analytical operators for the prospective glycemia pilot.

No file access, cohort selection, generation, survey expansion weights, p-values,
or target-specific fitting rules are implemented here. Input tables have already
passed their separately frozen preparation rules. The same estimator applies to
reference and generated tables. Cluster bands describe empirical stability and
have no confidence-coverage or national-population interpretation.
"""

from __future__ import annotations

from collections import Counter
from numbers import Integral

import numpy as np
import pandas as pd


SCIENTIFIC_COLUMNS = ("age", "female", "bmi", "glucose", "hba1c")
CLUSTER_COLUMNS = ("lab_est_dis", "lab_upm_dis")
AGE_EDGES = (25, 40, 55, 70, 80)
CELL_NAMES = tuple(
    f"age_{lower}_{upper - 1}_female_{female}"
    for lower, upper in zip(AGE_EDGES[:-1], AGE_EDGES[1:])
    for female in (0, 1)
)
DEFAULT_ATTEMPTS = 399
DEFAULT_RESAMPLING_SEED = 18301
FUTURE_GENERATOR_ANALYTICAL_SEEDS = (18203, 18211, 18223)
ESTIMAND_LABEL = "finite empirical age/sex-standardized analytical population"
STABILITY_LABEL = (
    "Empirical cluster-resampling stability bands conditional on the observed "
    "eligible reference; valid replicates only; no confidence-coverage or "
    "national design-based inference claim."
)


class AnalyticalError(ValueError):
    """A declared input or numerical failure with a machine-readable code."""

    code = "analytical_error"


class InputValidationError(AnalyticalError):
    code = "invalid_input"


class EmptyDemographicCellError(AnalyticalError):
    code = "empty_demographic_cell"


class SingularDesignError(AnalyticalError):
    code = "singular_design"


def validate_cohort(frame: pd.DataFrame, *, require_clusters: bool = False) -> np.ndarray:
    """Validate without altering the caller's frame; return the five numeric fields.

    Age must be an integer in 25..79 and female must be 0 or 1. All five
    fields must be finite; BMI/glucose/HbA1c must be strictly positive and
    glucose must be below 126 mg/dL. Any invalid row rejects the input table.
    Eligibility beyond these requirements belongs to the frozen preparation
    operator, not this analytical engine.
    """
    if not isinstance(frame, pd.DataFrame):
        raise InputValidationError("Input must be a pandas DataFrame.")
    if not frame.columns.is_unique:
        raise InputValidationError("Duplicate column names are not allowed.")
    needed = SCIENTIFIC_COLUMNS + (CLUSTER_COLUMNS if require_clusters else ())
    missing = [column for column in needed if column not in frame.columns]
    if missing:
        raise InputValidationError(f"Missing required columns: {missing}")
    if len(frame) == 0:
        raise InputValidationError("An empty cohort is not analyzable.")
    try:
        values = frame.loc[:, SCIENTIFIC_COLUMNS].to_numpy(dtype=np.float64)
    except (ValueError, TypeError, OverflowError) as exc:
        raise InputValidationError("All five scientific fields must be numeric.") from exc
    if not np.isfinite(values).all():
        raise InputValidationError("All five scientific fields must be finite.")
    age, female = values[:, 0], values[:, 1]
    if ((age < 25) | (age >= 80) | (age != np.floor(age))).any():
        raise InputValidationError("Age must be an integer in 25..79.")
    if not np.isin(female, (0, 1)).all():
        raise InputValidationError("Female must be coded 0 or 1.")
    if np.any(values[:, 2:] <= 0):
        raise InputValidationError("BMI, glucose, and HbA1c must be strictly positive.")
    if np.any(values[:, 3] >= 126):
        raise InputValidationError("Glucose must be below 126 mg/dL.")
    if require_clusters:
        for column in CLUSTER_COLUMNS:
            if frame[column].isna().any():
                raise InputValidationError(f"Missing cluster identifier in {column}.")
            for identifier in frame[column]:
                try:
                    hash(identifier)
                except TypeError as exc:
                    raise InputValidationError("Cluster identifiers must be hashable.") from exc
                if isinstance(identifier, (float, np.floating)) and not np.isfinite(identifier):
                    raise InputValidationError("Numeric cluster identifiers must be finite.")
    return values


def _cell_ids(values: np.ndarray) -> np.ndarray:
    age_group = np.searchsorted(np.asarray(AGE_EDGES), values[:, 0], side="right") - 1
    return 2 * age_group + values[:, 1].astype(np.int64)


def _weights_and_counts(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    cell_ids = _cell_ids(values)
    counts = np.bincount(cell_ids, minlength=8)
    if np.any(counts == 0):
        missing = [CELL_NAMES[i] for i in np.flatnonzero(counts == 0)]
        raise EmptyDemographicCellError(f"Empty demographic cells: {missing}")
    return 1.0 / (8.0 * counts[cell_ids]), counts


def demographic_weights(frame: pd.DataFrame) -> np.ndarray:
    """Return row weights 1/(8*n_h), with every demographic cell required."""
    values = validate_cohort(frame)
    weights, _ = _weights_and_counts(values)
    return weights


def weighted_quantile(values, weights, q: float) -> float:
    """Inverse-CDF quantile: smallest observed x with cumulative mass >= q.

    Zero-mass entries are discarded. Original sorted row weights are accumulated
    with Neumaier compensation, without rounding tied-value masses separately.
    The final cumulative total supplies normalization. There is no interpolation,
    midpoint convention, or added floating-point tolerance.
    """
    values = np.asarray(values, dtype=np.float64)
    weights = np.asarray(weights, dtype=np.float64)
    if values.ndim != 1 or weights.shape != values.shape or not values.size:
        raise InputValidationError("Quantiles require equally sized nonempty vectors.")
    if not np.isfinite(values).all() or not np.isfinite(weights).all():
        raise InputValidationError("Quantile inputs must be finite.")
    if np.any(weights < 0) or not np.any(weights > 0):
        raise InputValidationError("Quantile weights must be nonnegative with positive total.")
    if not np.isfinite(q) or not 0 <= q <= 1:
        raise InputValidationError("Quantile probability must be in [0, 1].")
    positive = weights > 0
    values, weights = values[positive], weights[positive]
    order = np.argsort(values, kind="stable")
    ordered = values[order]
    ordered_weights = weights[order]
    cumulative = np.empty(len(ordered_weights), dtype=np.float64)
    total, correction = 0.0, 0.0
    for i, mass in enumerate(ordered_weights):
        new_total = total + mass
        correction += ((total - new_total) + mass if abs(total) >= abs(mass)
                       else (mass - new_total) + total)
        total = new_total
        cumulative[i] = total + correction
    if not np.isfinite(cumulative[-1]):
        raise InputValidationError("Quantile total weight must be finite.")
    threshold = q * cumulative[-1]
    index = np.searchsorted(cumulative, threshold, side="left")
    return float(ordered[min(int(index), len(ordered) - 1)])


def _fit_wls(x: np.ndarray, y: np.ndarray, weights: np.ndarray, names) -> dict:
    """Full-rank sqrt(weight) least squares, with an explicit SVD threshold."""
    sqrt_weights = np.sqrt(weights)
    weighted_x = x * sqrt_weights[:, None]
    weighted_y = y * sqrt_weights
    singular_values = np.linalg.svd(weighted_x, compute_uv=False)
    relative_tolerance = max(x.shape) * np.finfo(np.float64).eps
    tolerance = float(relative_tolerance * singular_values[0])
    rank = int(np.sum(singular_values > tolerance))
    if rank != x.shape[1]:
        raise SingularDesignError(
            f"Design {tuple(names)} has rank {rank}/{x.shape[1]} at tolerance {tolerance:.17g}."
        )
    coefficients, _, solver_rank, _ = np.linalg.lstsq(
        weighted_x, weighted_y, rcond=relative_tolerance
    )
    if int(solver_rank) != x.shape[1] or not np.isfinite(coefficients).all():
        raise SingularDesignError("Least-squares solution failed the fixed rank/finite check.")
    residual = y - x @ coefficients
    return {
        "coefficients": dict(zip(names, map(float, coefficients))),
        "rank": rank,
        "rank_tolerance": tolerance,
        "singular_values": list(map(float, singular_values)),
        "residual_rms": float(np.sqrt(np.dot(weights, residual * residual) / weights.sum())),
    }


def analyze_cohort(frame: pd.DataFrame) -> dict:
    """Calculate every frozen question and diagnostic on one complete table.

    Q2 minus Q3 is the descriptive BMI coefficient change after glucose
    adjustment; it is not causal mediation. No significance or equivalence
    decision is generated. Optional cluster columns are unused here.
    """
    values = validate_cohort(frame)
    weights, counts = _weights_and_counts(values)
    age, female, bmi, glucose, hba1c = values.T
    x = np.column_stack((np.ones(len(frame)), (age - 50) / 10, female,
                         (bmi - 25) / 5, (glucose - 100) / 10))
    names = ("intercept", "age10", "female", "bmi5", "glucose10")
    full = _fit_wls(x, hba1c, weights, names)
    reduced = _fit_wls(x[:, :4], hba1c, weights, names[:4])
    glucose_only = _fit_wls(x[:, (0, 1, 2, 4)], hba1c, weights,
                          ("intercept", "age10", "female", "glucose10"))
    q2, q3 = reduced["coefficients"]["bmi5"], full["coefficients"]["bmi5"]
    diagnostics = {}
    for column, field_values in zip(SCIENTIFIC_COLUMNS, values.T):
        mean = float(np.dot(weights, field_values) / weights.sum())
        diagnostics[column] = {
            "mean": mean,
            "sd_population": float(np.sqrt(np.dot(weights, (field_values - mean) ** 2)
                                           / weights.sum())),
            "q10": weighted_quantile(field_values, weights, 0.1),
            "q50": weighted_quantile(field_values, weights, 0.5),
            "q90": weighted_quantile(field_values, weights, 0.9),
        }
    return {
        "estimand": ESTIMAND_LABEL,
        "n": len(frame),
        "demographic_cell_counts": dict(zip(CELL_NAMES, map(int, counts))),
        "questions": {
            "Q1_age10": full["coefficients"]["age10"],
            "Q2_bmi5": q2,
            "Q3_bmi5": q3,
            "Q2_minus_Q3_bmi5": q2 - q3,
        },
        "secondary": {"glucose10_age_sex": glucose_only["coefficients"]["glucose10"]},
        "diagnostics": diagnostics,
        "q1_residual_rms": full["residual_rms"],
        "models": {"Q1_Q3_full": full, "Q2_without_glucose": reduced,
                   "secondary_glucose": glucose_only},
        "interpretation": "Associational projections; Q2 minus Q3 is descriptive and noncausal.",
    }


def _cluster_groups(frame: pd.DataFrame) -> list[list[np.ndarray]]:
    """Build represented strata and pair-defined PSUs in first-appearance order."""
    strata = {}
    for position, (stratum, psu) in enumerate(
        frame.loc[:, CLUSTER_COLUMNS].itertuples(index=False, name=None)
    ):
        strata.setdefault(stratum, {}).setdefault(psu, []).append(position)
    return [[np.asarray(positions, dtype=np.int64) for positions in psus.values()]
            for psus in strata.values()]


def _draw_indices(groups: list[list[np.ndarray]], rng) -> np.ndarray:
    selected = []
    for psus in groups:
        count = len(psus)
        # Singleton strata are carried exactly once and consume no random draw.
        draws = np.zeros(1, dtype=np.int64) if count == 1 else rng.integers(0, count, size=count)
        selected.extend(psus[int(draw)] for draw in draws)
    return np.concatenate(selected)


def draw_cluster_indices(frame: pd.DataFrame, rng: np.random.Generator) -> np.ndarray:
    """Draw c PSUs per represented lab stratum, retaining complete clusters/multiplicity.

    Indices are positional (not DataFrame index labels). The pair
    (lab_est_dis, lab_upm_dis) defines a cluster. Strata and PSUs are ordered by
    first occurrence in the supplied table, fixing random-stream assignment.
    """
    validate_cohort(frame, require_clusters=True)
    return _draw_indices(_cluster_groups(frame), rng)


def _reported_estimands(result: dict) -> dict[str, float]:
    estimates = {**result["questions"], **result["secondary"]}
    for field, summary in result["diagnostics"].items():
        estimates.update({f"{field}.{statistic}": value for statistic, value in summary.items()})
    estimates["q1_residual_rms"] = result["q1_residual_rms"]
    return estimates


def cluster_stability(
    frame: pd.DataFrame, *, attempts: int = DEFAULT_ATTEMPTS,
    seed: int = DEFAULT_RESAMPLING_SEED,
) -> dict:
    """Fixed-attempt empirical cluster resampling, with no replacement for failures.

    Expanded duplicate rows make each original person's combined contribution
    m_i/(8*sum(m_j in cell h)). The SVD row count is the expanded replicate's
    actual row count. All five fields' diagnostics are included in the bands.
    Endpoints are numpy's linear 2.5/97.5 percentiles of valid replicates only.
    An invalid original table raises; only expected empty-cell/rank failures
    of replicates are counted. Other errors propagate rather than being hidden.
    """
    if isinstance(attempts, (bool, np.bool_)) or not isinstance(attempts, Integral) or attempts < 1:
        raise InputValidationError("Attempts must be a positive integer.")
    if isinstance(seed, (bool, np.bool_)) or not isinstance(seed, Integral) or seed < 0:
        raise InputValidationError("Seed must be a nonnegative integer.")
    validate_cohort(frame, require_clusters=True)
    point = analyze_cohort(frame)
    groups = _cluster_groups(frame)
    rng = np.random.default_rng(int(seed))
    valid_estimates = []
    valid_attempts = []
    failure_counts = Counter({"empty_demographic_cell": 0, "singular_design": 0})
    failure_attempts = []
    for attempt in range(1, int(attempts) + 1):
        indices = _draw_indices(groups, rng)
        replicate = frame.iloc[indices]
        try:
            estimate = _reported_estimands(analyze_cohort(replicate))
        except (EmptyDemographicCellError, SingularDesignError) as exc:
            failure_counts[exc.code] += 1
            failure_attempts.append({"attempt": attempt, "type": exc.code})
        else:
            valid_attempts.append(attempt)
            valid_estimates.append(estimate)
    names = tuple(_reported_estimands(point))
    if valid_estimates:
        matrix = np.asarray([[estimate[name] for name in names] for estimate in valid_estimates])
        endpoints = np.percentile(matrix, (2.5, 97.5), axis=0, method="linear")
        bands = {name: {"lower": float(endpoints[0, i]), "upper": float(endpoints[1, i])}
                 for i, name in enumerate(names)}
    else:
        bands = {name: None for name in names}
    return {
        "label": STABILITY_LABEL,
        "point_estimate": point,
        "seed": int(seed),
        "attempted": int(attempts),
        "valid": len(valid_estimates),
        "failed": int(sum(failure_counts.values())),
        "failure_counts": dict(failure_counts),
        "failure_attempts": failure_attempts,
        "valid_attempts": valid_attempts,
        "bands": bands,
        "band_status": "available" if valid_estimates else "unavailable_no_valid_replicates",
        "percentiles": [2.5, 97.5],
        "percentile_method": "linear",
        "valid_replicate_estimates": valid_estimates,
        "sampling_frame": "represented eligible lab strata and pair-defined eligible PSUs",
        "stratum_order": "first appearance; PSU order also first appearance",
        "represented_lab_strata": len(groups),
        "represented_lab_psus": sum(map(len, groups)),
        "singleton_lab_strata": sum(len(psus) == 1 for psus in groups),
    }
