"""Pure analysis functions; no participant files are opened on import.

The frozen point estimator is loaded unchanged. Only reference data receive
survey inference. Generated data use identical point analyses, never ordinary
synthetic-row SEs as clinical evidence. See INFERENCE.md for the fixed rules.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import t

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
PREPARATION = PROJECT / "work/analysis-utility-preparation-2026-10-29"
POINT_PATH = PREPARATION / "methods/analytical_points.py"
_spec = importlib.util.spec_from_file_location("m10_frozen_points", POINT_PATH)
points = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(points)

PRIMARY = ("adjusted_age_per10", "adjusted_bmi_per5",
           "bmi_curvature_second_difference", "female_minus_male_bmi_slope_per5")
CONTRASTS = {PRIMARY[0]: ("adjusted", 1, 1.), PRIMARY[1]: ("adjusted", 2, 1.),
             PRIMARY[2]: ("bmi_curve", -1, 2.), PRIMARY[3]: ("sex_bmi", -1, 1.),
             "adjusted_female_minus_male": ("adjusted", 3, 1.)}


class DesignError(ValueError):
    """Invalid design fails closed rather than invoking singleton adjustments."""


def _unique(index, what):
    if not index.is_unique or index.hasnans:
        raise DesignError(f"{what} index must be unique and nonmissing")


def validate_design(design):
    """Full *positive-fasting-weight* design, never the eligible-only design."""
    if list(design.columns) != ["stratum", "psu", "weight"] or design.empty:
        raise DesignError("Expected full-design columns stratum, psu, weight")
    _unique(design.index, "Full design")
    if design.isna().any().any():
        raise DesignError("Missing full-design fields")
    w = design.weight.to_numpy(dtype=float)
    if not np.isfinite(w).all() or (w <= 0).any():
        raise DesignError("Full-design weights must be finite and positive")
    counts = design[["stratum", "psu"]].drop_duplicates().groupby("stratum").size()
    if (counts < 2).any():
        raise DesignError("Singleton PSU stratum in full design; no automatic adjustment")
    return {"full_design_rows": len(design), "full_design_strata": len(counts),
            "full_design_psus": int(counts.sum()), "full_design_df": int((counts-1).sum())}


def total_covariance(influence: pd.DataFrame, design: pd.DataFrame):
    """WR first-stage Taylor covariance, keeping zero-influence out-of-domain PSUs.

    For stratum h with m_h sampled PSUs and PSU influence totals U_hj:
      V = sum_h m_h/(m_h-1) sum_j (U_hj-mean_h)(U_hj-mean_h)'.
    Influence rows contain the weights already. IDs, not positions, join them.
    """
    validate_design(design)
    _unique(influence.index, "Influence")
    if not influence.index.isin(design.index).all():
        raise DesignError("Influence index contains records outside full design")
    if influence.shape[1] == 0 or not np.isfinite(influence.to_numpy(dtype=float)).all():
        raise DesignError("Empty or nonfinite influence matrix")
    full = influence.reindex(design.index, fill_value=0.)
    # Grouping by both keys nests repeated PSU codes within strata.
    totals = full.groupby([design.stratum, design.psu], sort=False).sum()
    covariance = np.zeros((influence.shape[1], influence.shape[1]))
    for _, block in totals.groupby(level=0, sort=False):
        values = block.to_numpy(dtype=float)
        m = len(values)
        centered = values-values.mean(axis=0)
        covariance += (m/(m-1)) * centered.T @ centered
    return (covariance+covariance.T)/2


def domain_df(design, ids):
    _unique(ids, "Domain")
    if len(ids) == 0 or not ids.isin(design.index).all():
        raise DesignError("Domain index absent from full design")
    d = design.loc[ids, ["stratum", "psu"]].drop_duplicates()
    return len(d)-d.stratum.nunique()


def domain_counts(design, ids):
    d = design.loc[ids, ["stratum", "psu"]].drop_duplicates()
    return {"domain_rows": len(ids), "domain_psus": len(d), "domain_strata": int(d.stratum.nunique()),
            "domain_df": int(len(d)-d.stratum.nunique())}


def _aligned(X, y, w, design):
    _unique(X.index, "Analysis")
    if not X.index.equals(y.index) or not X.index.equals(w.index):
        raise DesignError("Analysis/outcome/weight index must match exactly in order")
    validate_design(design)
    if not X.index.isin(design.index).all():
        raise DesignError("Analysis IDs absent from full design")
    if not np.array_equal(w.to_numpy(float), design.loc[X.index, "weight"].to_numpy(float)):
        raise DesignError("Analysis weights differ from full-design weights")


def wls_taylor(X: pd.DataFrame, y: pd.Series, w: pd.Series, design: pd.DataFrame):
    """Frozen WLS points plus sandwich Taylor variance of its estimating equation."""
    _aligned(X, y, w, design)
    beta = points.wls_point(X, y, w)
    x, values = X.to_numpy(float), y.to_numpy(float)
    weights = w.to_numpy(float)/w.mean()
    bread = x.T @ (weights[:, None]*x)
    score = x*(weights*(values-x@beta))[:, None]
    # No n/(n-p) row correction: first-stage PSU correction is in total_covariance.
    try:
        influence = np.linalg.solve(bread, score.T).T
    except np.linalg.LinAlgError as error:
        raise points.Nonestimable("Singular WLS information matrix") from error
    covariance = total_covariance(pd.DataFrame(influence, index=X.index), design)
    return {"beta": beta, "covariance": covariance, "rank": X.shape[1],
            "domain_df": domain_df(design, X.index),
            "ci_df": domain_df(design, X.index)-(X.shape[1]-1)}


def mean_taylor(y: pd.Series, w: pd.Series, design: pd.DataFrame):
    x = pd.DataFrame({"intercept": np.ones(len(y))}, index=y.index)
    _aligned(x, y, w, design)
    values, weights = y.to_numpy(float), w.to_numpy(float)
    if not len(values) or not np.isfinite(values).all():
        raise DesignError("Empty or nonfinite mean values")
    estimate = np.average(values, weights=weights)
    influence = weights*(values-estimate)/weights.sum()
    covariance = total_covariance(pd.DataFrame({"mean": influence}, index=y.index), design)
    return {"estimate": float(estimate), "variance": float(covariance[0, 0]),
            "domain_df": domain_df(design, y.index), "ci_df": domain_df(design, y.index)}


def _interval(estimate, variance, df, *, sign_screen=False):
    if not np.isfinite(variance) or variance < -1e-12:
        raise DesignError("Invalid Taylor variance")
    se = float(np.sqrt(max(0., variance)))
    result = {"uncertainty": "reference_full_design_domain_Taylor_WR", "standard_error": se,
              "ci_level": .95, "ci_df": int(df), "clinical_conclusion": "not_assessed_no_substantive_margin",
              "multiplicity": "unadjusted_descriptive_only"}
    if df <= 0:
        result.update(ci_status="not_estimable_insufficient_design_df", ci_lower=None, ci_upper=None,
                      zero_null_screen="unavailable")
    elif se == 0:
        # Do not turn exactly degenerate invented/model-perfect data into evidence.
        result.update(ci_status="degenerate_zero_variance", ci_lower=float(estimate), ci_upper=float(estimate),
                      zero_null_screen="unavailable_degenerate_variance")
    else:
        delta = float(t.ppf(.975, df)*se)
        lo, hi = float(estimate-delta), float(estimate+delta)
        screen = "not_applicable_positive_mean"
        if sign_screen:
            screen = "positive_excludes_zero" if lo > 0 else "negative_excludes_zero" if hi < 0 else "includes_zero_inconclusive"
        result.update(ci_status="estimated", ci_lower=lo, ci_upper=hi, zero_null_screen=screen)
    return result


def _models(observed, outcome, case):
    A, B = (observed.age-50)/10, (observed.bmi-25)/5
    F = (observed.sex == 2).astype(float)
    base = pd.DataFrame({"intercept": 1., "A": A, "B": B, "F": F}, index=observed.index)
    y = outcome.copy()
    if case == "nhanes_insulin":
        base["G"] = np.log(observed.glucose_mg_dl/100)
        y = np.log(y)
    return {"adjusted": base, "bmi_curve": base.assign(B_squared=B*B),
            "sex_bmi": base.assign(female_times_B=F*B)}, y


def evaluate_reference(observed, outcome, weights, case, full_design=None, design_ids=None):
    """Reserved reference only. Call after the campaign freeze; no I/O here.

    design_ids is a Series indexed by the opaque analysis ID, whose values name
    each record in the complete positive-weight design. It must match in order.
    """
    result = points.evaluate_points(observed, outcome, weights, case)
    if case == "pns_hba1c":
        sensitivity = points.evaluate_points(observed, outcome, pd.Series(1., index=observed.index), case)
        for record in result.values():
            record["uncertainty"] = "not_available_PNS_design_missing"
            record["clinical_conclusion"] = "not_assessed_no_design_inference_or_substantive_margin"
        return {"weighted": result, "unweighted_sensitivity": sensitivity,
                "inference_scope": "Provided-weight lab-complete participant points only; national calibration unresolved"}
    if full_design is None or design_ids is None or not observed.index.equals(design_ids.index):
        raise DesignError("NHANES requires full design and exactly aligned design-ID mapping")
    ids = pd.Index(design_ids.to_numpy(), name="design_id")
    _unique(ids, "Design mapping")
    metadata = validate_design(full_design)
    metadata.update(domain_counts(full_design, ids))
    x, y, w = observed.copy(), outcome.copy(), weights.copy()
    x.index = y.index = w.index = ids
    models, transformed = _models(x, y, case)
    fits = {}
    for name, X in models.items():
        try:
            fits[name] = wls_taylor(X, transformed, w, full_design)
        except points.Nonestimable:
            # Original frozen point records retain every planned nonestimable endpoint.
            continue
    for name, (model, term, multiplier) in CONTRASTS.items():
        if result[name]["status"] != "estimated":
            continue
        if model not in fits:
            result[name].update(uncertainty="not_estimable_information_matrix")
            continue
        fit = fits[model]
        variance = multiplier**2*fit["covariance"][term, term]
        if not np.isclose(result[name]["estimate"], multiplier*fit["beta"][term], rtol=1e-11, atol=1e-12):
            raise AssertionError("Frozen point and inference point diverged")
        result[name].update(_interval(result[name]["estimate"], variance, fit["ci_df"], sign_screen=True),
                            domain_df=int(fit["domain_df"]), model_rank=int(fit["rank"]))
    means = {"weighted_arithmetic_mean": (y, w),
             "derived_homa1_ir_mean": (y*x.glucose_mg_dl/405., w)}
    for low, high in [(20, 40), (40, 60), (60, 80)]:
        for sex in (1, 2):
            for group, lower, upper in [("lt25", 0., 25.), ("25lt30", 25., 30.), ("ge30", 30., np.inf)]:
                mask = (x.age >= low)&(x.age < high)&(x.sex == sex)&(x.bmi >= lower)&(x.bmi < upper)
                means[f"cell_age{low}_{high-1}_sex{sex}_bmi{group}_mean"] = (y[mask], w[mask])
    for name, (cell_y, cell_w) in means.items():
        if result[name]["status"] == "estimated":
            fit = mean_taylor(cell_y, cell_w, full_design)
            if not np.isclose(result[name]["estimate"], fit["estimate"], rtol=1e-11, atol=1e-12):
                raise AssertionError("Frozen mean and inference mean diverged")
            result[name].update(_interval(fit["estimate"], fit["variance"], fit["ci_df"]),
                                domain_df=int(fit["domain_df"]))
    return {"weighted": result, "design": metadata,
            "model_covariances": {k: v["covariance"].tolist() for k, v in fits.items()},
            "inference_scope": "Full positive-fasting-weight design domain inference; descriptive association only"}


def evaluate_generated(observed, outcome, weights, case):
    result = {"weighted": points.evaluate_points(observed, outcome, weights, case),
              "uncertainty_scope": "No clinical evidence uncertainty estimated from generated rows"}
    if case == "pns_hba1c":
        result["unweighted_sensitivity"] = points.evaluate_points(observed, outcome, pd.Series(1., index=observed.index), case)
    return result


def compare_points(reference, generated):
    """All endpoint magnitude errors; sign agreement only for fixed primary family."""
    if set(reference) != set(generated):
        raise ValueError("Endpoint sets differ; no dropping unfavorable/nonestimable endpoints")
    result = {}
    for name, real in reference.items():
        fake = generated[name]
        entry = {"reference_status": real["status"], "generated_status": fake["status"],
                 "tier": real["tier"], "clinical_conclusion_agreement": "not_assessed"}
        if real["status"] == fake["status"] == "estimated":
            if real["unit"] != fake["unit"]:
                raise ValueError("Endpoint scientific units differ")
            error = fake["estimate"]-real["estimate"]
            entry.update(reference_estimate=real["estimate"], generated_estimate=fake["estimate"],
                         signed_error=error, absolute_error=abs(error), unit=real["unit"])
            if name in PRIMARY:
                entry.update(point_direction_agreement=real["point_direction"] == fake["point_direction"],
                             reference_zero_null_screen=real.get("zero_null_screen", "unavailable"))
        result[name] = entry
    return result


def summarize_residual_draws(draws):
    """Three prespecified outputs are correlated Monte Carlo draws, not tasks."""
    if len(draws) != 3 or any(set(d) != set(draws[0]) for d in draws):
        raise ValueError("Expected three complete endpoint families")
    result = {}
    for name in draws[0]:
        records = [d[name] for d in draws]
        values = [r["estimate"] for r in records if r["status"] == "estimated"]
        entry = {"scheduled_draws": 3, "estimated_draws": len(values),
                 "uncertainty": "residual_Monte_Carlo_range_only_not_clinical_or_source_uncertainty"}
        if values:
            entry.update(median=float(np.median(values)), minimum=float(min(values)), maximum=float(max(values)))
        result[name] = entry
    return result
