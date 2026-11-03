"""Pure source-moment arithmetic; no table reads, fitting or generation.

Input moments must describe the author's declared source-population law AFTER
its declared source selection, not the target law or an unselected parent law.
This module checks arithmetic inputs, not their biological or law provenance.
It contains no reported source point estimates and no target statistics.
"""
from __future__ import annotations

import numpy as np


def _validated(context):
    if context.get("role") != "declared_source_population_moments":
        raise ValueError("A separately declared source population is required")
    if not context.get("assumption_ids") or not context.get("moment_derivation"):
        raise ValueError("Explicit assumptions and law-to-moment derivation required")
    if context.get("selection_status") != "moments_after_declared_source_selection":
        raise ValueError("Parent or target moments cannot stand in for selected-source moments")
    if context.get("weights") != "equal_assumption":
        raise ValueError("Only explicitly qualified equal-weight scenarios are supported")
    names = context["variables"]
    if not names or len(names) != len(set(names)):
        raise ValueError("Distinct variable names required")
    means = np.asarray(context["means"], dtype=float)
    cov = np.asarray(context["covariance"], dtype=float)
    if means.shape != (len(names),) or cov.shape != (len(names), len(names)):
        raise ValueError("Moment dimensions do not match variables")
    if not np.isfinite(means).all() or not np.isfinite(cov).all():
        raise ValueError("Finite population first and second moments required")
    scale = max(1.0, float(np.max(np.abs(cov))))
    if not np.allclose(cov, cov.T, rtol=0, atol=1e-12 * scale):
        raise ValueError("Covariance must be symmetric")
    if np.linalg.eigvalsh(cov).min() < -1e-10 * scale:
        raise ValueError("Covariance is not positive semidefinite")
    if len(context.get("units", {})) < len(names) or any(n not in context["units"] for n in names):
        raise ValueError("Every variable requires an explicit unit")
    return names, means, cov


def evaluate(evidence_id, context):
    """Return one qualified population functional, never a strict replay score.

    Covariance projection coefficients include an intercept by centering. Their
    analytic definition is Sigma_XX^{-1} Sigma_XY. No source coefficient is
    installed in the law, and no fit-to-source optimization happens here.
    """
    names, means, cov = _validated(context)
    units = context["units"]
    if evidence_id in {"R_JANSEN_BMI", "R_JANSEN_FPG"}:
        if context.get("source_context_id") != "CTX_JANSEN_SELECTED":
            raise ValueError("Jansen operation requires its declared source context")
        term = "BMI" if evidence_id == "R_JANSEN_BMI" else "FPG"
        required_units = {"age": "year", "gender_binary": "1", "BMI": "kg/m^2", "FPG": "mmol/L"}
        predictors = ["age", "gender_binary", term]
        if any(units.get(n) != required_units[n] for n in predictors):
            raise ValueError("Predictor unit mismatch")
        if context.get("gender_mapping") not in {"female=1,male=0", "male=1,female=0"}:
            raise ValueError("Explicit binary source membership mapping required")
        ix = [names.index(n) for n in predictors]
        gender = names.index("gender_binary")
        p = means[gender]
        if not 0 < p < 1 or not np.isclose(cov[gender, gender], p * (1 - p), rtol=1e-8, atol=1e-12):
            raise ValueError("Declared binary mean/variance does not support both groups")
        if "HbA1c_IFCC" in names:
            y = names.index("HbA1c_IFCC")
            if units.get("HbA1c_IFCC") != "mmol/mol":
                raise ValueError("IFCC response unit mismatch")
            xy = cov[ix, y]
            response_map = "identity_native_IFCC"
        else:
            y = names.index("HbA1c_percent")
            if units.get("HbA1c_percent") != "%":
                raise ValueError("NGSP response unit mismatch")
            # NGSP = 0.09148 * IFCC + 2.152. The additive offset cancels
            # in covariance and an intercept-including projection slope.
            xy = cov[ix, y] / 0.09148
            response_map = "NGSP_to_IFCC_affine; covariance_divided_by_0.09148"
        xx = cov[np.ix_(ix, ix)]
        if np.linalg.matrix_rank(xx) != len(ix):
            raise ValueError("Predictor covariance must have full rank; no regularization fallback")
        value = float(np.linalg.solve(xx, xy)[-1])
        unit = "mmol/mol/(kg/m^2)" if term == "BMI" else "mmol/mol/(mmol/L)"
    elif evidence_id == "R_BAO_PEARSON":
        if context.get("source_context_id") != "CTX_BAO_ANALYZED":
            raise ValueError("Bao operation requires its declared source context")
        if units.get("FPG") != "mmol/L" or units.get("HbA1c_percent") != "%":
            raise ValueError("Bao source measurement units required")
        x, y = (names.index(n) for n in ("FPG", "HbA1c_percent"))
        if cov[x, x] <= 0 or cov[y, y] <= 0:
            raise ValueError("Pearson operands must both have positive variance")
        value = float(cov[x, y] / np.sqrt(cov[x, x] * cov[y, y]))
        unit, response_map = "1", "identity_native_measures"
    elif evidence_id == "R_MIND_SPEARMAN":
        raise ValueError("Ordinary moments do not identify Spearman; an independently reviewed law-specific derivation is required")
    else:
        raise ValueError("Unbound relationship operation")
    if not np.isfinite(value):
        raise ValueError("Nonfinite source functional")
    return {"evidence_id": evidence_id, "source_context_id": context["source_context_id"],
            "calculated_value": value, "unit": unit, "response_map": response_map,
            "classification": "qualified_analytic_source_population_functional",
            "strict_replay": "not_computable", "exact_source_reconstruction": False,
            "transport_validated": False, "assumption_ids": list(context["assumption_ids"]),
            "moment_derivation": context["moment_derivation"]}
