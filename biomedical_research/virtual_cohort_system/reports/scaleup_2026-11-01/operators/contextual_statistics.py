"""Small in-memory diagnostics; no file access, generator or collector integration.

Geometric mean uses original positive values. Threshold prevalence delegates to
the existing frozen arithmetic. Source-check eligibility is a reviewed declared
context commitment, never a statistical pass or proof of population validity.
"""
from __future__ import annotations

import hashlib
import json
import math
from numbers import Integral, Real

import numpy as np
import pandas as pd

from cohort_harness.source_checks import NotComputable, apply_operator, condition


def require(ok, message):
    if not ok:
        raise ValueError(message)


def exact(value, keys):
    require(isinstance(value, dict) and set(value) == set(keys), "Unexpected/missing declaration fields")


def text(value):
    require(isinstance(value, str) and bool(value.strip()), "Nonempty declaration required")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def finite(value):
    return isinstance(value, Real) and not isinstance(value, (bool, np.bool_)) and math.isfinite(float(value))


def predicate(value):
    exact(value, {"column", "op", "value"})
    text(value["column"])
    require(value["op"] in {"eq", "ne", "lt", "le", "gt", "ge", "in"}, "Unsupported predicate")
    values = value["value"] if value["op"] == "in" else [value["value"]]
    require(isinstance(values, list) and bool(values), "Predicate values required")
    require(all(type(v) is str or finite(v) for v in values), "Predicate needs explicit string/finite numeric values")


def validate_operator(operator):
    require(isinstance(operator, dict), "Operator object required")
    kind = operator.get("kind")
    require(kind in {"geometric_mean", "proportion"}, "Only geometric mean and threshold proportion are supported")
    exact(operator, {"kind", "unit", "selection", "selection_missing_policy", "missing_policy"} |
          ({"column"} if kind == "geometric_mean" else {"event"}))
    text(operator["unit"])
    require(operator["missing_policy"] in {"error", "complete_cases"}, "Explicit operand missing policy required")
    require(operator["selection_missing_policy"] in {"error", "exclude"}, "Explicit selection missing policy required")
    require(isinstance(operator["selection"], list), "Explicit selection conjunction required")
    for selection in operator["selection"]:
        predicate(selection)
    names = {p["column"] for p in operator["selection"]}
    if kind == "geometric_mean":
        text(operator["column"])
        operand = operator["column"]
    else:
        predicate(operator["event"])
        require(operator["event"]["op"] in {"gt", "ge", "lt", "le"} and finite(operator["event"]["value"]),
                "Prevalence needs a finite numeric threshold with explicit boundary inclusion")
        require(operator["unit"] in {"1", "%"}, "Proportion unit must be 1 or %")
        operand = operator["event"]["column"]
    return names | {operand}, operand


def descriptor(value, names, *, source):
    common = {"context_id", "population", "measurement", "variable_units", "variable_scales"}
    exact(value, common | ({"source_id", "locator", "operator", "weights", "definition_status", "uncertainty_role"}
                           if source else {"kind"}))
    for key in ("context_id", "population", "measurement"):
        text(value[key])
    for key in ("variable_units", "variable_scales"):
        require(isinstance(value[key], dict) and set(value[key]) == names, "Declare units/scales for every operand and selection variable")
        for item in value[key].values():
            text(item)
    require(set(value["variable_scales"].values()) <= {"original", "categorical", "natural_log", "log10", "not_reported"},
            "Unknown variable scale")
    if source:
        for key in ("source_id", "locator"):
            text(value[key])
        require(value["weights"] in {"none", "weighted", "not_reported"}, "Unknown source weighting declaration")
        require(value["definition_status"] in {"specified", "not_reported", "unsupported"}, "Unknown source definition")
        require(value["uncertainty_role"] in {"estimator_confidence_interval", "estimator_standard_error",
                                             "between_person_dispersion", "not_reported", "unresolved"}, "Unknown uncertainty role")
        if value["definition_status"] == "specified":
            source_names, _ = validate_operator(value["operator"])
            require(source_names == names, "Source operator variable set differs")
        else:
            require(value["operator"] is None, "Unresolved source definition must have null operator")
    else:
        require(value["kind"] in {"source_context_simulation", "target_context_generated", "analytic_fixture"}, "Unknown table context kind")


def _cell(value):
    # Typed commitment to supplied relevant values, including missing/nonfinite
    # values. Never emit rows. Float hex avoids decimal rounding in the binding.
    if value is None or value is pd.NA or bool(pd.isna(value)):
        return ["missing"]
    if isinstance(value, (bool, np.bool_)):
        return ["bool", bool(value)]
    if isinstance(value, Integral):
        return ["integer", str(int(value))]
    if isinstance(value, Real):
        return ["float", float(value).hex()]
    require(isinstance(value, str), "Only scalar numeric/categorical values are supported")
    return ["string", value]


def context_contract(frame, operator, table_context, source):
    """Material for independent review; this function never creates approval."""
    names, _ = validate_operator(operator)
    require(isinstance(frame, pd.DataFrame) and frame.columns.is_unique and names <= set(frame.columns), "Missing/duplicate table variables")
    descriptor(table_context, names, source=False)
    descriptor(source, names, source=True)
    columns = sorted(names)
    content = {"columns": columns, "rows": [[_cell(v) for v in row] for row in frame[columns].itertuples(index=False, name=None)]}
    return {"schema_version": 1, "relevant_table_sha256": hashlib.sha256(canonical(content).encode()).hexdigest(),
            "operator": json.loads(canonical(operator)), "table_context": json.loads(canonical(table_context)),
            "source": json.loads(canonical(source))}


def _compute(frame, operator, operand, scales):
    selections = operator["selection"]
    columns = sorted({s["column"] for s in selections})
    missing_selection = frame[columns].isna().any(axis=1) if columns else pd.Series(False, index=frame.index)
    if missing_selection.any() and operator["selection_missing_policy"] == "error":
        raise NotComputable("Missing selection values; eligibility cannot be determined")
    selected = frame
    for selection in selections:
        values = selection["value"] if selection["op"] == "in" else [selection["value"]]
        series = frame[selection["column"]]
        numeric = pd.api.types.is_numeric_dtype(series)
        scale = scales[selection["column"]]
        if scale not in {"original", "categorical"}:
            raise NotComputable("Unknown/log selection scales are unsupported; no implicit conversion")
        if selection["op"] in {"lt", "le", "gt", "ge"} and (
                scale != "original" or not numeric or isinstance(series.dtype, pd.CategoricalDtype)):
            raise NotComputable("Ordered selection requires an original-scale numeric variable; categorical/string order is unsupported")
        available = series.dropna()
        if pd.api.types.is_bool_dtype(series) or (numeric and not np.isfinite(available.to_numpy(dtype=float)).all()):
            raise NotComputable("Boolean/nonfinite selection values are unsupported")
        if not numeric and not all(isinstance(v, str) for v in available):
            raise NotComputable("Selection values require consistent numeric or string types")
        if any((not finite(v)) if numeric else not isinstance(v, str) for v in values):
            raise NotComputable("Selection value/type mismatch; no implicit encoding")
        selected = selected.loc[condition(selected, selection)]
    missing = selected[operand].isna()
    if missing.any() and operator["missing_policy"] == "error":
        raise NotComputable("Missing operand values; no implicit complete-case deletion")
    values = selected.loc[~missing, operand]
    if values.empty:
        raise NotComputable("No complete selected values")
    if not pd.api.types.is_numeric_dtype(values) or pd.api.types.is_bool_dtype(values):
        raise NotComputable("Numeric operand required; no implicit conversion")
    numbers = values.to_numpy(dtype=float)
    if not np.isfinite(numbers).all():
        raise NotComputable("Nonfinite operand values")
    if operator["kind"] == "geometric_mean":
        if (numbers <= 0).any():
            raise NotComputable("Geometric mean undefined for selected nonpositive values; no dropping or offset")
        try:
            value = math.exp(math.fsum(math.log(float(x)) for x in numbers) / len(numbers))
        except OverflowError as error:
            raise NotComputable("Geometric mean cannot be represented finitely") from error
        require(math.isfinite(value) and value > 0, "Geometric mean was not finite positive")
        result = {"value": value, "unit": operator["unit"], "n_input": len(frame), "n_selected": len(selected),
                  "n_used": len(values), "n_missing_dropped": int(missing.sum())}
    else:
        # Existing implementation, unchanged. Its denominator is all complete
        # selected event values, not only threshold-positive observations.
        existing = {k: v for k, v in operator.items() if k != "selection_missing_policy"}
        result = apply_operator(frame, existing)
    return {**result, "n_missing_selection_excluded": int(missing_selection.sum())}


def diagnostic(frame, operator, table_context, source, *, approval=None):
    """Return descriptive availability separately from declared source eligibility."""
    contract = context_contract(frame, operator, table_context, source)
    _, operand = validate_operator(operator)
    result = {"schema_version": 1, "diagnostic_available": False, "diagnostic": None,
              "diagnostic_weights": "none", "diagnostic_scope": table_context["kind"],
              "source_weights": source["weights"], "source_uncertainty_role": source["uncertainty_role"],
              "uncertainty_estimated": False, "uncertainty_conversion": "none",
              "exact_source_check_allowed": False, "eligibility_basis": "reviewed_declared_context_only",
              "eligibility_reasons": [], "contract_sha256": hashlib.sha256(canonical(contract).encode()).hexdigest(),
              "scientific_validity": "not_assessed", "collector_integrated": False}
    reasons = result["eligibility_reasons"]
    try:
        if table_context["variable_scales"][operand] != "original":
            raise NotComputable("Only original-scale operands are supported; no log-base guess or conversion")
        if operator["kind"] == "geometric_mean" and table_context["variable_units"][operand] != operator["unit"]:
            raise NotComputable("Geometric-mean result/input units differ; no unit conversion")
        result["diagnostic"] = _compute(frame, operator, operand, table_context["variable_scales"])
        result["diagnostic_available"] = True
    except (NotComputable, ValueError) as error:
        reasons.append("Diagnostic unavailable: " + str(error))
    if table_context["kind"] != "source_context_simulation":
        reasons.append("Target/fixture diagnostics do not reproduce a source population")
    for key in ("context_id", "population", "measurement", "variable_units", "variable_scales"):
        if table_context[key] != source[key]:
            reasons.append("Source/table declared context mismatch: " + key)
    if source["definition_status"] != "specified" or canonical(source["operator"]) != canonical(operator):
        reasons.append("Source estimator/selection/denominator definition not matched")
    if source["weights"] != "none":
        reasons.append("Weighted/unknown source estimator is not implemented; unweighted diagnostic is not a substitute")
    try:
        exact(approval, {"decision", "independent", "reviewer_id", "producer_id", "reviewed_utc", "reason", "approved_contract"})
        require(approval["decision"] == "approved" and approval["independent"] is True, "Context approval missing")
        for key in ("reviewer_id", "producer_id", "reviewed_utc", "reason"):
            text(approval[key])
        require(approval["reviewer_id"].strip().casefold() != approval["producer_id"].strip().casefold(), "Context reviewer is producer")
        require(canonical(approval["approved_contract"]) == canonical(contract), "Context approval does not bind these inputs")
    except (ValueError, KeyError, TypeError):
        reasons.append("Independent approved source-context contract absent or mismatched")
    result["exact_source_check_allowed"] = result["diagnostic_available"] and not reasons
    return result
