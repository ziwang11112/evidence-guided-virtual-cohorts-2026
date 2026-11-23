"""Bind operator units to the author's pre-sampling, case-neutral column declarations."""
from collections import defaultdict
from copy import deepcopy

from .ops import FIELDS


def _references(operator):
    if not isinstance(operator, dict) or not isinstance(operator.get("kind"), str):
        raise ValueError("Missing or invalid operator kind")
    fields = FIELDS.get(operator["kind"])
    if fields is None or not fields <= operator.keys() <= fields | {"kind", "units", "where"}:
        raise ValueError("Unknown operator or fields outside its supported signature")
    names = [operator[key] for key in ("x", "y") if key in fields]
    predicates = operator.get("where", [])
    if not isinstance(predicates, list):
        raise ValueError("where must be a list of predicates")
    predicates = predicates + [operator[k] for k in ("event", "exposure", "outcome") if k in fields]
    for p in predicates:
        if not isinstance(p, dict) or "column" not in p:
            raise ValueError("Predicate does not name a column")
        names.append(p["column"])
    if any(not isinstance(name, str) or not name.strip() for name in names):
        raise ValueError("Operator contains an unnamed column")
    return sorted(set(names))


def bind_design(design):
    """Return an independent working copy and one provenance record per evidence item.

    Only a completely absent units map is filled in. Explicit contradictions are
    retained in the audit record and marked unresolved in the executable copy.
    The original design and scientific column definitions remain unchanged.
    """
    normalized = deepcopy(design)
    by_name = defaultdict(list)
    columns = design.get("columns")
    if isinstance(columns, list):
        for index, column in enumerate(columns):
            if isinstance(column, dict) and isinstance(column.get("name"), str):
                by_name[column["name"]].append((index, column))

    audit = []
    for item in normalized["evidence"]["evidence_checks"]:
        entry = {"id": item["id"]}
        audit.append(entry)
        if "operator" not in item:
            entry["status"] = "no_operator"
            continue
        if "unresolved" in item:
            raise ValueError("Evidence cannot declare both an operator and an unresolved reason")
        op = item["operator"]
        entry["submitted_operator"] = deepcopy(op)
        try:
            names = _references(op)
            units = {}
            sources = {}
            for name in names:
                if name.casefold() in {"id", "row_id"} or name.casefold().startswith("diagnostic_"):
                    raise ValueError(f"Identifier or diagnostic column cannot supply a measurement: {name}")
                if len(by_name[name]) != 1:
                    raise ValueError(f"Design must declare exactly one column named {name}")
                index, col = by_name[name][0]
                if col.get("role") in ("id", "identifier", "row_id", "diagnostic"):
                    raise ValueError(f"Design marks {name} as an identifier or diagnostic")
                unit = col.get("unit")
                if not isinstance(unit, str) or not unit.strip():
                    raise ValueError(f"Design omits the unit of {name}")
                units[name] = unit
                sources[name] = f"columns[{index}].unit"
            if "units" in op:
                if op["units"] != units:
                    raise ValueError("Supplied units map conflicts with the exact declared columns or units")
                entry["status"] = "explicit_verified"
            else:
                op["units"] = units
                entry["status"] = "bound_from_design"
            entry.update(units=deepcopy(units), unit_sources=sources)
        except ValueError as error:
            reason = str(error)
            del item["operator"]
            item["unresolved"] = "Unit binding unresolved: " + reason
            entry.update(status="unresolved", reason=reason)
    return normalized, audit
