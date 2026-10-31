"""ENSANUT preparation v2 only; a separate reviewed second attempt, never a v1 repair.

No effects, distributions, fitting, source feedback, or generator execution occur here.
The CLI has no alternate-input path, override, or ungated mode.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
import csv
import datetime as dt
import hashlib
import io
import json
import math
import re
import sys

import numpy as np

RUN_DIR = Path(__file__).resolve().parent.parent
KEY_WIDTHS = {"UPM": 5, "VIV_SEL": 2, "HOGAR": 1, "NUMREN": 2}
LAB_REQUIRED = set(KEY_WIDTHS) | {
    "EDAD", "SEXO", "P7", "P5_1", "VALOR_GLU_SUERO", "VALOR_HB1AC",
    "UPM_DIS", "EST_DIS",
}
ANTH_REQUIRED = set(KEY_WIDTHS) | {
    "EDAD", "SEXO", "PESO1_1", "PESO1_2", "TALLA4_1", "TALLA4_2",
    "PESO12_1", "PESO12_2", "TALLA15_1", "TALLA15_2",
    "P2", "P3", "P5", "P6", "P11", "P13", "P14", "P16",
}
REFERENCE_COLUMNS = ["age", "female", "bmi", "glucose", "hba1c", "lab_upm_dis", "lab_est_dis"]
FLOW_STAGES = ["linked", "age_sex", "no_prior_diagnosis", "fasting_8_to_12",
               "positive_labs_glucose_below_126", "pregnancy_lactation_rule",
               "standing_pair_and_quality", "reference"]
AGE_BANDS = ((25, 39), (40, 54), (55, 69), (70, 79))
INPUTS = {
    "laboratory": {"path": "custodian/private/DetBioCronicosAdultos.csv",
                   "sha256": "d32341b00b7e01ac22d3552f5e07094cd1e7ef05da2421200794b14a0d3d86e3",
                   "archive_id": "lab_csv"},
    "anthropometry": {"path": "custodian/private/CN_ANTROPOMETRIA.csv",
                      "sha256": "a2e0d4d0a5eb93d62049d09ebc5880868be7f9143c6d9e0cb26d06d6099b37b1",
                      "archive_id": "anthropometry_csv"},
}
FIXED_BINDINGS = {
    "protocol": "PROTOCOL_v2.md",
    "amendment": "PREPARATION_AMENDMENT_01.md",
    "adjudication": "custodian/MEASUREMENT_RULE_ADJUDICATION.md",
    "preparation_script": "custodian/prepare_reference_v2.py",
    "preparation_tests": "custodian/test_prepare_reference_v2.py",
    "download_ledger": "custodian/DOWNLOAD_LEDGER.json",
    "prior_release": "PREPARATION_RELEASE.json",
    "prior_attempt": "custodian/PREPARATION_ATTEMPT.json",
    "prior_hold": "custodian/PREPARATION_HOLD.json",
}


class PreparationHold(Exception):
    """Only field/reason/count can leave a failed preparation; never raw exceptions."""
    def __init__(self, field=None, reason=None, *, issues=None):
        self.issues = issues if issues is not None else [{"field": field, "reason": reason, "count": 1}]
        super().__init__("preparation held; see aggregate field/reason counts")


def _combine_issues(counter, error):
    for item in error.issues:
        counter[(item["field"], item["reason"])] += item["count"]


def _raise_issues(counter):
    if counter:
        raise PreparationHold(issues=[{"field": f, "reason": r, "count": n}
                                      for (f, r), n in sorted(counter.items())])


def _text(value):
    return "" if value is None else str(value).strip()


def _number(value, field):
    raw = _text(value)
    if not raw:
        return None
    try:
        number = Decimal(raw)
    except InvalidOperation:
        raise PreparationHold(field, "malformed_numeric") from None
    return number if number.is_finite() else None


def _integer(value, field):
    number = _number(value, field)
    if number is None:
        return None
    if number != number.to_integral_value():
        raise PreparationHold(field, "nonintegral_integer_field")
    return int(number)


def _code(value, field, allowed):
    if not _text(value):
        return None
    number = _integer(value, field)
    if number is None or number not in allowed:
        raise PreparationHold(field, "undocumented_code")
    return number


def normalize_key(row, module):
    """Keep source keys untouched; create strict text-only zero-padded working keys."""
    result = []
    for field, width in KEY_WIDTHS.items():
        value = row.get(field)
        if not isinstance(value, str):
            raise PreparationHold(module + "." + field, "key_must_be_original_string")
        value = value.strip()
        if not re.fullmatch(r"[0-9]{1," + str(width) + r"}", value):
            raise PreparationHold(module + "." + field, "missing_or_malformed_key")
        result.append(value.zfill(width))
    return tuple(result)


def _index_rows(rows, module, required):
    index, issues = {}, Counter()
    for row in rows:
        try:
            if not required.issubset(row):
                raise PreparationHold(module + ".schema", "required_column_missing")
            key = normalize_key(row, module)
            if key in index:
                raise PreparationHold(module + ".key", "duplicate_person_key")
            index[key] = row
        except PreparationHold as error:
            _combine_issues(issues, error)
    _raise_issues(issues)
    return index


def join_tables(lab_rows, anth_rows):
    """One-to-one inner join; all original fields, including keys, retain suffixes."""
    lab = _index_rows(lab_rows, "laboratory", LAB_REQUIRED)
    anth = _index_rows(anth_rows, "anthropometry", ANTH_REQUIRED)
    merged, issues = [], Counter()
    for key, lrow in lab.items():
        if key not in anth:
            continue
        arow = anth[key]
        try:
            for field in ("EDAD", "SEXO"):
                lv = _integer(lrow[field], "laboratory." + field)
                av = _integer(arow[field], "anthropometry." + field)
                if lv != av:
                    raise PreparationHold("join." + field, "module_disagreement")
            row = dict(zip(KEY_WIDTHS, key))
            row.update({name + "_lab": value for name, value in lrow.items()})
            row.update({name + "_anth": value for name, value in arow.items()})
            merged.append(row)
        except PreparationHold as error:
            _combine_issues(issues, error)
    _raise_issues(issues)
    return merged, {"laboratory_rows": len(lab), "anthropometry_rows": len(anth),
                    "linked_rows": len(merged), "laboratory_unmatched": len(lab) - len(merged),
                    "anthropometry_unmatched": len(anth) - len(merged)}


def _reading(a, field, sentinel):
    value = _number(a[field], "anthropometry." + field)
    return None if value is None or value <= 0 or value == sentinel else value


def select_standing_pair(a, age):
    """Selected investigator quality rule; no averaging or cross-ordinal mixing."""
    if not isinstance(age, int) or not 25 <= age <= 79:
        raise PreparationHold("measurement.age", "outside_function_contract")
    older = age >= 60
    wf = ("PESO12_1", "PESO12_2") if older else ("PESO1_1", "PESO1_2")
    hf = ("TALLA15_1", "TALLA15_2") if older else ("TALLA4_1", "TALLA4_2")
    ws, hs, cf = ("P14", "P16", "P13") if older else ("P3", "P5", "P2")
    required = set(wf + hf) | {ws, hs, cf} | ({"P11"} if older else set())
    if not required.issubset(a):
        raise PreparationHold("anthropometry.schema", "required_column_missing")
    wstatus = _code(a[ws], "anthropometry." + ws, {1, 2, 3, 9})
    hstatus = _code(a[hs], "anthropometry." + hs, {1, 2, 3, 9})
    clothing = _code(a[cf], "anthropometry." + cf, {1, 2, 3, 4} if older else {1, 2, 3, 4, 9})
    route = _code(a["P11"], "anthropometry.P11", {1, 2, 3, 4, 5, 6}) if older else None
    weights = [_reading(a, f, Decimal("222.222")) for f in wf]
    heights = [_reading(a, f, Decimal("222.2")) for f in hf]
    complete = [i for i in (0, 1) if weights[i] is not None and heights[i] is not None]
    diagnostics = {"complete_pair1": 0 in complete, "complete_pair2": 1 in complete,
                   "weight_third_trigger": None, "height_third_trigger": None,
                   "clothing_unknown": clothing in (None, 9), "clothing_heavy": clothing == 2,
                   "upper_limb_amputation_standing_route": older and route == 1}
    if all(v is not None for v in weights):
        diagnostics["weight_third_trigger"] = abs(weights[0] - weights[1]) >= Decimal("0.4")
    if all(v is not None for v in heights):
        delta = abs(heights[0] - heights[1])
        diagnostics["height_third_trigger"] = delta >= 1 if older else delta > 1

    def exclude(decision, reason):
        return {"decision": decision, "reason": reason, "diagnostics": diagnostics}

    if older and route in {2, 3, 5, 6}:
        if any(v is not None for v in weights + heights):
            return exclude("EXCLUDE_DOCUMENTATION_CONSISTENCY", "alternative_route_with_standing_values")
        return exclude("EXCLUDE_EXPLICIT_OR_MISSING", "alternative_route")
    if clothing == 4:
        if any(v is not None for v in weights):
            return exclude("EXCLUDE_DOCUMENTATION_CONSISTENCY", "not_weighed_with_numeric_weight")
        return exclude("EXCLUDE_EXPLICIT_OR_MISSING", "not_weighed")
    if not complete:
        return exclude("EXCLUDE_EXPLICIT_OR_MISSING", "no_complete_ordinal_pair")
    if older and route not in {1, 4}:
        return exclude("EXCLUDE_QUALITY_RESTRICTION", "standing_route_not_documented")
    if wstatus != 1 or hstatus != 1:
        return exclude("EXCLUDE_QUALITY_RESTRICTION", "both_block_results_not_code1")
    i = complete[0]
    return {"decision": "ADMIT_PAIR", "reason": "first_available_complete_pair", "repeat": i + 1,
            "weight_kg": weights[i], "height_cm": heights[i], "diagnostics": diagnostics}


def demographic_cell(age, female):
    for low, high in AGE_BANDS:
        if low <= age <= high:
            return f"{low}-{high}_female{female}"
    raise PreparationHold("readiness.age", "outside_age_bands")


def readiness_counts(reference_rows):
    """Counts and boolean rank checks only: no coefficients, moments, or singular values returned."""
    cells = {f"{lo}-{hi}_female{sex}": 0 for lo, hi in AGE_BANDS for sex in (0, 1)}
    for row in reference_rows:
        cells[demographic_cell(row["age"], row["female"])] += 1
    n = len(reference_rows)
    ranks = {"Q1_Q3": False, "Q2": False, "secondary_glucose": False}
    nonconstant = False
    if n:
        matrix = np.array([[r[k] for k in REFERENCE_COLUMNS[:5]] for r in reference_rows], dtype=float)
        nonconstant = bool(np.all(np.any(matrix != matrix[0], axis=0)))
        age, female, bmi, glucose = matrix[:, 0], matrix[:, 1], matrix[:, 2], matrix[:, 3]
        x = np.column_stack((np.ones(n), (age - 50) / 10, female, (bmi - 25) / 5, (glucose - 100) / 10))
        weights = np.array([1 / (8 * cells[demographic_cell(r["age"], r["female"])]) for r in reference_rows])
        for name, columns in {"Q1_Q3": [0, 1, 2, 3, 4], "Q2": [0, 1, 2, 3], "secondary_glucose": [0, 1, 2, 4]}.items():
            design = x[:, columns] * np.sqrt(weights[:, None])
            singular = np.linalg.svd(design, compute_uv=False)
            tolerance = max(design.shape) * np.finfo(float).eps * singular[0]
            ranks[name] = bool(np.count_nonzero(singular > tolerance) == len(columns))
    ready = n >= 400 and min(cells.values()) >= 30 and nonconstant and all(ranks.values())
    return {"ready": bool(ready), "total_rows": n, "cell_counts": cells,
            "minimum_total": 400, "minimum_per_cell": 30,
            "all_five_nonconstant": nonconstant, "full_rank_designs": ranks}


def prepare_records(lab_rows, anth_rows):
    """Pure in-memory preparation, used by artificial tests; no filesystem access."""
    joined, linkage = join_tables(lab_rows, anth_rows)
    flow = {name: 0 for name in FLOW_STAGES}
    flow["linked"] = len(joined)
    refs, audit, issues, exclusions = [], [], Counter(), Counter()
    consistency = Counter({"alternative_route_with_standing_values": 0, "not_weighed_with_numeric_weight": 0})
    for ordinal, row in enumerate(joined):
        try:
            age = _integer(row["EDAD_lab"], "laboratory.EDAD")
            sex = _code(row["SEXO_lab"], "laboratory.SEXO", {1, 2})
            if age is None or not 25 <= age <= 79 or sex is None:
                continue
            flow["age_sex"] += 1
            if _code(row["P7_lab"], "laboratory.P7", {1, 2, 3, 9}) != 2:
                continue
            flow["no_prior_diagnosis"] += 1
            fast = _integer(row["P5_1_lab"], "laboratory.P5_1")
            if fast is None or not 8 <= fast <= 12:
                continue
            flow["fasting_8_to_12"] += 1
            glucose = _number(row["VALOR_GLU_SUERO_lab"], "laboratory.VALOR_GLU_SUERO")
            hba1c = _number(row["VALOR_HB1AC_lab"], "laboratory.VALOR_HB1AC")
            if glucose is None or hba1c is None or not 0 < glucose < 126 or hba1c <= 0:
                continue
            flow["positive_labs_glucose_below_126"] += 1
            if sex == 2 and 25 <= age <= 49:
                if _code(row["P6_anth"], "anthropometry.P6", {1, 2, 3, 4, 9}) != 4:
                    continue
            flow["pregnancy_lactation_rule"] += 1
            a = {key[:-5]: val for key, val in row.items() if key.endswith("_anth")}
            selected = select_standing_pair(a, age)
            audit.append({"joined_ordinal": ordinal, "decision": selected["decision"],
                          "reason": selected["reason"], "repeat": selected.get("repeat"),
                          "diagnostics": selected["diagnostics"]})
            if selected["decision"] != "ADMIT_PAIR":
                exclusions[selected["reason"]] += 1
                if selected["decision"] == "EXCLUDE_DOCUMENTATION_CONSISTENCY":
                    consistency[selected["reason"]] += 1
                continue
            flow["standing_pair_and_quality"] += 1
            design = {}
            for original, output, width in (("UPM_DIS", "lab_upm_dis", 5), ("EST_DIS", "lab_est_dis", 3)):
                raw = row[original + "_lab"]
                if not isinstance(raw, str) or not re.fullmatch(r"[0-9]{1," + str(width) + r"}", raw.strip()):
                    raise PreparationHold("laboratory." + original, "missing_or_malformed_design_identifier")
                design[output] = raw.strip().zfill(width)
            bmi = selected["weight_kg"] / (selected["height_cm"] / 100) ** 2
            numeric = {"bmi": float(bmi), "glucose": float(glucose), "hba1c": float(hba1c)}
            if not all(math.isfinite(value) and value > 0 for value in numeric.values()):
                raise PreparationHold("conversion", "nonfinite_or_nonpositive_output")
            if numeric["glucose"] >= 126:
                raise PreparationHold("conversion.glucose", "strict_boundary_crossed_by_float_conversion")
            refs.append({"age": age, "female": sex - 1, **numeric, **design})
            flow["reference"] += 1
        except PreparationHold as error:
            _combine_issues(issues, error)
    _raise_issues(issues)
    return {"reference_rows": refs, "joined_rows": joined, "private_diagnostics": audit,
            "flow": {"linkage": linkage, "remaining_after_stage": flow,
                     "measurement_exclusion_reasons": dict(sorted(exclusions.items())),
                     "consistency_exclusion_reasons": dict(sorted(consistency.items()))},
            "readiness": readiness_counts(refs)}


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _safe_nonprivate_path(root, relative):
    if not isinstance(relative, str) or "\\" in relative:
        raise PreparationHold("release.binding_path", "invalid_relative_path")
    rel = Path(relative)
    if rel.is_absolute() or ":" in relative or ".." in rel.parts or any(p.casefold() == "private" for p in rel.parts):
        raise PreparationHold("release.binding_path", "unsafe_or_private_path")
    target = (root / rel).resolve()
    if not target.is_relative_to(root.resolve()):
        raise PreparationHold("release.binding_path", "path_outside_run")
    if any(p.casefold() == "private" for p in target.relative_to(root.resolve()).parts):
        raise PreparationHold("release.binding_path", "binding_resolves_to_private")
    return target


@dataclass(frozen=True)
class VerifiedRelease:
    root: Path
    release_sha256: str
    release_id: str
    bindings: dict


def verify_release(root):
    """Validate only release/nonprivate metadata first. Does not open private inputs."""
    root = Path(root).resolve()
    release_path = root / "PREPARATION_RELEASE_v2.json"
    if not release_path.is_file():
        raise PreparationHold("release", "missing_root_preparation_release")
    try:
        body = release_path.read_bytes()
        release = json.loads(body)
    except (OSError, ValueError):
        raise PreparationHold("release", "unreadable_or_invalid_json") from None
    required = {"schema": "ensanut_preparation_release_v2", "issuer": "root", "status": "approved",
                "purpose": "prepare_reference_only", "effects_authorized": False,
                "attempt_number": 2, "attempt_budget": 1}
    if any(release.get(k) != v for k, v in required.items()) or release.get("effects_authorized") is not False or not release.get("release_id"):
        raise PreparationHold("release", "required_authorization_fields_mismatch")
    bindings = release.get("bindings", {})
    names = set(FIXED_BINDINGS) | {"analysis_engine", "independent_review"}
    if set(bindings) != names:
        raise PreparationHold("release.bindings", "required_binding_set_mismatch")
    for name in sorted(names):
        record = bindings[name]
        if not isinstance(record, dict) or set(record) != {"path", "sha256"}:
            raise PreparationHold("release." + name, "invalid_binding_record")
        if name in FIXED_BINDINGS and record["path"] != FIXED_BINDINGS[name]:
            raise PreparationHold("release." + name, "fixed_path_mismatch")
        path = _safe_nonprivate_path(root, record["path"])
        if not re.fullmatch(r"[0-9a-f]{64}", str(record["sha256"])):
            raise PreparationHold("release." + name, "invalid_sha256")
        if not path.is_file() or _sha(path.read_bytes()) != record["sha256"]:
            raise PreparationHold("release." + name, "file_hash_mismatch")
    prior_attempt = json.loads((root / FIXED_BINDINGS["prior_attempt"]).read_text(encoding="utf-8"))
    prior_hold = json.loads((root / FIXED_BINDINGS["prior_hold"]).read_text(encoding="utf-8"))
    if prior_attempt.get("release_sha256") != bindings["prior_release"]["sha256"] or prior_hold.get("status") != "HOLD":
        raise PreparationHold("release.prior_history", "failed_first_attempt_history_mismatch")
    if release.get("inputs") != {name: {k: spec[k] for k in ("path", "sha256")} for name, spec in INPUTS.items()}:
        raise PreparationHold("release.inputs", "pinned_inputs_mismatch")
    ledger = json.loads((root / FIXED_BINDINGS["download_ledger"]).read_text(encoding="utf-8"))
    for name, spec in INPUTS.items():
        archives = [a for a in ledger.get("artifacts", []) if a.get("id") == spec["archive_id"] and a.get("status") == "complete"]
        members = [m for a in archives for m in a.get("zip_members", [])
                   if "custodian/" + m.get("local_relative_path", "") == spec["path"]]
        if len(members) != 1 or members[0].get("sha256") != spec["sha256"]:
            raise PreparationHold("release." + name, "input_not_bound_to_download_ledger")
    return VerifiedRelease(root, _sha(body), str(release["release_id"]), bindings)


def _load_private_inputs(gate):
    """Called only after verified release and exclusive attempt receipt. Parse hash-verified bytes."""
    if not isinstance(gate, VerifiedRelease):
        raise PreparationHold("release", "verified_release_required")
    fresh_gate = verify_release(gate.root)
    if fresh_gate.release_sha256 != gate.release_sha256 or fresh_gate.bindings != gate.bindings:
        raise PreparationHold("release", "release_changed_before_input_read")
    bodies = {}
    for name, spec in INPUTS.items():
        path = gate.root / spec["path"]
        if not path.resolve().is_relative_to(gate.root / "custodian" / "private"):
            raise PreparationHold("input." + name, "input_resolves_outside_private_directory")
        body = path.read_bytes()
        if _sha(body) != spec["sha256"]:
            raise PreparationHold("input." + name, "actual_file_hash_mismatch")
        bodies[name] = body
    result = {}
    for name, body in bodies.items():
        try:
            reader = csv.DictReader(io.StringIO(body.decode("utf-8-sig"), newline=""))
            required = LAB_REQUIRED if name == "laboratory" else ANTH_REQUIRED
            if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames) or not required.issubset(reader.fieldnames):
                raise PreparationHold("input." + name, "invalid_csv_schema")
            rows = list(reader)
            if any(None in row or any(value is None for value in row.values()) for row in rows):
                raise PreparationHold("input." + name, "ragged_csv")
            result[name] = rows
        except (UnicodeError, csv.Error):
            raise PreparationHold("input." + name, "invalid_csv_encoding_or_syntax") from None
    return result


def _json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def _csv_bytes(rows, columns):
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode("utf-8")


def run_authorized(root=RUN_DIR):
    """One guarded attempt; never called by tests with real input access."""
    gate = verify_release(root)  # No private existence checks or hashes precede this.
    custodian = gate.root / "custodian"
    attempt = custodian / "PREPARATION_ATTEMPT_v2.json"
    targets = [custodian / "private" / n for n in (
        "reference.csv", "linked_source.csv", "measurement_audit.json",
        "reference_v2.csv", "linked_source_v2.csv", "measurement_audit_v2.json")]
    targets += [custodian / n for n in ("PREPARATION_RECEIPT.json", "PREPARATION_RECEIPT_v2.json", "PREPARATION_HOLD_v2.json")]
    if attempt.exists() or any(path.exists() for path in targets):
        raise PreparationHold("execution", "prior_attempt_or_output_exists")
    with attempt.open("xb") as handle:
        handle.write(_json_bytes({"release_id": gate.release_id, "release_sha256": gate.release_sha256,
                                  "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                                  "scope": "one reviewed second preparation attempt; no target effects"}))
    try:
        data = _load_private_inputs(gate)
        prepared = prepare_records(data["laboratory"], data["anthropometry"])
        if verify_release(gate.root).release_sha256 != gate.release_sha256:
            raise PreparationHold("release", "release_changed_before_output_write")
        joined_columns = list(prepared["joined_rows"][0]) if prepared["joined_rows"] else list(KEY_WIDTHS)
        bodies = {
            "private/reference_v2.csv": _csv_bytes(prepared["reference_rows"], REFERENCE_COLUMNS),
            "private/linked_source_v2.csv": _csv_bytes(prepared["joined_rows"], joined_columns),
            "private/measurement_audit_v2.json": _json_bytes(prepared["private_diagnostics"]),
        }
        output_manifest = {}
        for relative, body in bodies.items():
            with (custodian / relative).open("xb") as handle:
                handle.write(body)
            output_manifest[relative] = {"sha256": _sha(body), "bytes": len(body)}
        receipt = {"schema": "ensanut_preparation_receipt_v2", "release_id": gate.release_id,
                   "release_sha256": gate.release_sha256, "bindings": gate.bindings,
                   "flow": prepared["flow"], "readiness": prepared["readiness"], "outputs": output_manifest,
                   "scope": "eligibility flow, readiness counts/booleans, hashes only; no effects",
                   "completed_utc": dt.datetime.now(dt.timezone.utc).isoformat()}
        with (custodian / "PREPARATION_RECEIPT_v2.json").open("xb") as handle:
            handle.write(_json_bytes(receipt))
        return receipt
    except PreparationHold as error:
        with (custodian / "PREPARATION_HOLD_v2.json").open("xb") as handle:
            handle.write(_json_bytes({"status": "HOLD", "issues": error.issues}))
        raise


def main():
    if len(sys.argv) != 1:
        print(json.dumps({"status": "HOLD", "issues": [{"field": "CLI", "reason": "no_override_arguments_supported", "count": 1}]}))
        return 2
    try:
        receipt = run_authorized()
        print(json.dumps({"status": "PREPARED", "ready": receipt["readiness"]["ready"],
                          "receipt": "custodian/PREPARATION_RECEIPT_v2.json"}))
        return 0
    except PreparationHold as error:
        print(json.dumps({"status": "HOLD", "issues": error.issues}))
        return 2
    except Exception as error:
        # Never expose exception text, rows, identifiers, values, or a traceback.
        print(json.dumps({"status": "HOLD", "issues": [{"field": "runtime", "reason": type(error).__name__, "count": 1}]}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
