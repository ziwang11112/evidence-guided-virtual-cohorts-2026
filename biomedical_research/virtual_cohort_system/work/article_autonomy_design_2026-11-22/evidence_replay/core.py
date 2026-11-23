"""Replay an immutable, author-selected evidence inventory on saved virtual rows."""
from collections import Counter
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import re

import pandas as pd

from .ops import ReplayError, compute, result_unit


def digest(obj):
    data = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(data.encode("utf8")).hexdigest()


def text_field(value):
    return isinstance(value, str) and bool(value.strip())


def inventory(evidence):
    items = evidence["evidence_checks"]
    if not isinstance(items, list) or (not items and not text_field(evidence.get("no_evidence_reason"))):
        raise ValueError("Declare evidence items or give a reason for an empty evidence inventory")
    seen = set()
    for item in items:
        key = item.get("id") if isinstance(item, dict) else None
        if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,79}", key) or key in seen:
            raise ValueError("Each evidence item requires a unique stable identifier")
        seen.add(key)
        if not all(text_field(item.get(k)) for k in ("claim","source","population")):
            raise ValueError(f"{key}: describe the claim, source location and population")
        if item.get("provenance") not in ("reported","derived","assumed"):
            raise ValueError(f"{key}: unknown provenance")
        if item.get("applicability") not in ("same_population","transport_assumption","unknown"):
            raise ValueError(f"{key}: unknown applicability")
        if ("operator" in item) == ("unresolved" in item):
            raise ValueError(f"{key}: choose an operator or explain why unresolved")
        if "unresolved" in item and not text_field(item["unresolved"]):
            raise ValueError(f"{key}: an unresolved item needs a reason")
        if "adjustment" in item and (not isinstance(item["adjustment"], list)
                                     or not all(text_field(k) for k in item["adjustment"])):
            raise ValueError(f"{key}: adjustment must name its covariates")
        ref = item.get("reference")
        if ref is None and "unresolved" in item:
            continue
        if not isinstance(ref, dict) or set(ref) != {"value","unit","decimals"}:
            raise ValueError(f"{key}: reference needs value, unit and decimals")
        value, digits = ref["value"], ref["decimals"]
        if type(value) not in (float,int) or not math.isfinite(value) or not text_field(ref["unit"]):
            raise ValueError(f"{key}: invalid reference value or unit")
        if digits is not None:
            if type(digits) is not int or not 0 <= digits <= 12:
                raise ValueError(f"{key}: invalid printed decimal precision")
            center = Decimal(str(value)).scaleb(digits)
            if center != center.to_integral_value():
                raise ValueError(f"{key}: value has more digits than its stated precision")
    return items


def check(item, frame, schema):
    row = {"id":item["id"]}
    if item["provenance"] == "assumed" or item["applicability"] != "same_population":
        return dict(row,status="not_source_comparable",reason=item.get("unresolved") or item["applicability"] + "/" + item["provenance"])
    if "unresolved" in item:
        return dict(row,status="unresolved",reason=item["unresolved"])
    if item.get("adjustment"):
        return dict(row,status="not_computable",reason="The replay operators do not implement covariate-adjusted estimands")
    ref,op = item["reference"],item["operator"]
    if isinstance(op, dict) and op.get("kind") == "count" and item.get("source_n") != len(frame):
        return dict(row,status="not_source_comparable",reason="Source sample size must be declared and match for comparing raw counts")
    try:
        value,n = compute(frame, schema, op)
        if result_unit(op) != ref["unit"]:
            raise ReplayError("Source value unit differs from operator result unit")
    except ReplayError as exc:
        return dict(row,status="not_computable",reason=str(exc)[:280])
    difference = value - ref["value"]
    row.update(value=value,n=n,difference=difference)
    if ref["decimals"] is None:
        return dict(row,status="descriptive_only")
    half = 0.5 * 10.0 ** -ref["decimals"]
    dist = abs(difference)
    if math.isclose(dist,half,rel_tol=1e-12,abs_tol=0):
        return dict(row,status="rounding_boundary")
    return dict(row,status="within_precision" if dist < half else "outside_precision")


def replay(root, mode, evidence, candidate, manifest):
    """Return only aggregate feedback derived from the bound model and its own rows."""
    if mode not in ("trial","final") or digest(candidate) != manifest["candidate_sha256"]:
        raise ValueError("Stage or frozen candidate binding mismatch")
    items = inventory(evidence)
    schema = {col["name"]:col["unit"] for col in candidate["model_spec"]["columns"]}
    if "row_id" in schema or any(k.startswith("diagnostic_") for k in schema):
        raise ValueError("Only measurements from the model's declared schema can be replayed")
    root = Path(root).resolve()
    result = {"inventory_sha256":digest(evidence), "candidate_sha256":digest(candidate),
              "stage":mode, "execution_status":manifest["status"], "declared_count":len(items),
              "evidence_index":items, "runs":[]}
    if not items:
        result["no_evidence_reason"] = evidence["no_evidence_reason"]
    for run in manifest["runs"]:
        summary = {k:run[k] for k in ("scenario","seed","status")}
        if run["status"] == "success":
            path = Path(run["table"]).resolve()
            if not path.is_relative_to(root / ("execution_" + mode)) or path.name != "generated.csv":
                raise ValueError("Table falls outside the bound execution stage")
            if hashlib.sha256(path.read_bytes()).hexdigest() != run["sha256"]:
                raise ValueError("Virtual table hash mismatch")
            frame = pd.read_csv(path, usecols=list(schema), float_precision="round_trip")
            if len(frame) != run["n"]:
                raise ValueError("Bound table row count mismatch")
            summary["table_sha256"] = run["sha256"]
            checks = [check(item,frame,schema) for item in items]
        else:
            checks = [{"id":item["id"],"status":"no_table"} for item in items]
        summary.update(checks=checks, counts=dict(Counter(c["status"] for c in checks)))
        result["runs"].append(summary)
    return result


def review_feedback(report):
    # The author already has its own design. Omit file paths, hashes of CSVs and row values.
    index = [{k:item.get(k) for k in ("id","source","reference")} for item in report["evidence_index"]]
    return {"inventory_sha256":report["inventory_sha256"],"evidence_index":index,
            "declared_count":report["declared_count"],"execution_status":report["execution_status"],
            "no_evidence_reason":report.get("no_evidence_reason"),
            "runs":[{k:v for k,v in run.items() if k in ("scenario","seed","status","checks","counts")}
                    for run in report["runs"]]}


def needs_disposition(report):
    if not report["runs"]:
        return {item["id"] for item in report["evidence_index"]}
    return {c["id"] for run in report["runs"] for c in run["checks"] if c["status"] != "within_precision"}
