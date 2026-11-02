"""Bounded K01 source-metadata normalization; never fit or sample actual evidence.

The bytes-in function is pure. The explicit CLI reads only the three named
request metadata files and writes one unactivated normalization view.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from statistical_reference import AYELE_CONTEXT, EVIDENCE_IDS, MIND_CONTEXT, _SPECS, _validate_inputs


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(value: Any, *, ensure_ascii: bool = False) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=ensure_ascii, allow_nan=False).encode("utf-8")


def _load(data: bytes) -> dict:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            _require(key not in result, "Duplicate JSON key")
            result[key] = value
        return result
    def invalid_constant(value):
        raise ValueError("Nonfinite JSON constant")
    value = json.loads(data.decode("utf-8-sig"), object_pairs_hook=unique, parse_constant=invalid_constant)
    _require(type(value) is dict, "JSON object required")
    return value


def _operator(item_id: str) -> dict:
    _, variable, statistic, _, group = _SPECS[item_id]
    if group is None:
        result = {"kind": "mean" if statistic == "arithmetic_mean" else "standard_deviation", "column": variable}
        if statistic == "individual_standard_deviation": result["ddof"] = 1
        return result
    if variable == "sex":
        conditions = [{"column": "sex", "op": "eq", "value": "F" if group == "Female" else "M"}]
    elif variable == "age":
        low = {"ayele_age_25_34": 25, "ayele_age_35_44": 35,
               "ayele_age_45_54": 45, "ayele_age_55_64": 55}[item_id]
        conditions = [{"column": "age", "op": "ge", "value": low},
                      {"column": "age", "op": "lt", "value": low+10}]
    elif item_id == "ayele_bmi_underweight":
        conditions = [{"column": "bmi", "op": "lt", "value": 18.5}]
    elif item_id == "ayele_bmi_normal":
        conditions = [{"column": "bmi", "op": "ge", "value": 18.5},
                      {"column": "bmi", "op": "le", "value": 24.9}]
    else:
        conditions = [{"column": "bmi", "op": "ge", "value": 25}]
    return {"kind": "proportion", "boolean_event": {"all": conditions}, "output_unit": "1"}


def prepare_reference_inputs(*, selected_evidence_bytes: bytes, diagnostic_plan_bytes: bytes,
                             packet_manifest_bytes: bytes, expected_manifest_sha256: str) -> dict[str, Any]:
    """Verify byte/content mappings and copy18 normalized input records, with no fit.

    The expected manifest hash is caller-pinned; matching it is an integrity check,
    not an author signature, evidence admission or verification of a clinical run.
    """
    _require(_sha(packet_manifest_bytes) == expected_manifest_sha256, "Packet manifest hash mismatch")
    manifest = _load(packet_manifest_bytes)
    _require(manifest.get("schema") == "k01_request_packet_manifest_v1", "Wrong manifest schema")
    sources = {"selected_source_evidence.json": selected_evidence_bytes,
               "descriptive_diagnostic_plan.json": diagnostic_plan_bytes}
    bindings = {}
    for name, data in sources.items():
        commitment = manifest["files"][name]
        _require(commitment["sha256"] == _sha(data) and commitment["bytes"] == len(data),
                 "Request file byte commitment differs: "+name)
        bindings[name] = {"sha256": _sha(data), "bytes": len(data)}
    selected, plan = _load(selected_evidence_bytes), _load(diagnostic_plan_bytes)
    _require(selected.get("schema") == "k01_sanitized_selected_source_packet_v1", "Wrong source packet schema")
    _require(plan.get("schema") == "k01_prospective_descriptive_diagnostic_plan_v1", "Wrong diagnostic plan schema")
    candidates = {}
    for index, record in enumerate(selected["records"]):
        if record["record_class"] == "potential_source_marginal":
            _require(record["id"] not in candidates, "Duplicate marginal ID")
            candidates[record["id"]] = (index, record)
    diagnostics = {record["evidence_id"]: record for record in plan["items"]}
    _require(set(candidates) == set(EVIDENCE_IDS) and set(diagnostics) == set(EVIDENCE_IDS)
             and len(plan["items"]) == len(EVIDENCE_IDS) == plan["diagnostic_count"],
             "Exact18 selected/diagnostic IDs required")
    normalized, mapping = [], []
    for item_id in EVIDENCE_IDS:
        index, wrapper = candidates[item_id]
        original, diagnostic = wrapper["original_selected_record"], diagnostics[item_id]
        context, variable, statistic, unit, group = _SPECS[item_id]
        source_id = "WANG2024_MIND" if context == MIND_CONTEXT else "ayele_2020_dire_dawa"
        _require(wrapper["source_id"] == original["source_id"] == diagnostic["source_id"] == source_id,
                 "Original/wrapper/diagnostic source identity differs")
        _require(wrapper["context_id"] == diagnostic["context_id"] == context and
                 wrapper["canonical_variable"] == variable and original["id"] == item_id,
                 "Context/variable/original ID mapping differs")
        original_variable = "serum_glucose_fsg" if context == MIND_CONTEXT and variable == "glucose" else variable
        _require(original["variable"] == original_variable, "Unexpected original analyte mapping")
        original_hash = _sha(_canonical(original))
        _require(wrapper["provenance"]["original_record_canonical_sha256"] == original_hash ==
                 diagnostic["original_record_canonical_sha256"], "Original record digest differs")
        _require(diagnostic["id"] == "descriptive__"+item_id and diagnostic["operator"] == _operator(item_id)
                 and diagnostic["comparison_unit"] == unit and diagnostic["selection"] == []
                 and diagnostic["generated_row_weights"] == "equal", "Diagnostic operator/scale differs")
        row = dict(evidence_id=item_id, context_id=context, variable=variable,
                   statistic=statistic, unit=unit,
                   locator=original["source_locator"] if context == MIND_CONTEXT else original["locator"])
        if group is None:
            _require(original["statistic"] == statistic and original["unit"] == unit,
                     "Original moment statistic/unit differs")
            row["value"] = original["estimate"] if context == MIND_CONTEXT else original["value"]
            _require(diagnostic["comparison_value"] == row["value"], "Diagnostic moment differs")
            operation = "Copy original moment, unit and locator; no numerical transformation"
        else:
            row["group"] = group
            if context == MIND_CONTEXT:
                _require(original["statistic"] == "sample_proportion" and original["unit"] == "1"
                         and original["event"] == "female", "MIND count-ratio meaning differs")
                row["numerator"] = original["derivation"]["exact_numerator"]
                row["denominator"] = original["derivation"]["exact_denominator"]
                operation = "Preserve exact integer count operands; female label to Female; no division"
            else:
                expected_group = "≥25" if item_id == "ayele_bmi_overweight" else group
                _require(original["statistic"] == "printed_percentage" and original["unit"] == "%"
                         and original["group"] == expected_group, "Ayele original proportion/group differs")
                if variable == "bmi":
                    _require(original["category_unit"] == "kg/m^2", "BMI category threshold unit differs")
                row.update(numerator=original["source_count"], denominator=original["source_denominator"],
                           reported_percentage=original["value"])
                _require(diagnostic["original_printed_percentage"] == original["value"]
                         and diagnostic["original_printed_group"] == expected_group,
                         "Printed source metadata differs")
                operation = "Preserve integer counts and printed percentage separately; no division"
                if expected_group == "≥25": operation += "; explicit ≥25 to ASCII>=25 spelling"
            derivation = diagnostic["comparison_derivation"]
            _require(derivation["numerator"] == row["numerator"] and derivation["denominator"] == row["denominator"]
                     and derivation["not_printed_percentage_division"] is True,
                     "Diagnostic integer-count derivation differs")
        normalized.append(row)
        mapping.append({"evidence_id": item_id, "source_id": source_id, "context_id": context,
                        "selected_record_pointer": f"/records/{index}", "original_record_sha256": original_hash,
                        "diagnostic_id": diagnostic["id"], "operator": diagnostic["operator"],
                        "normalization": operation})
    # Shape/count validation only: no beta/lognormal fitting, inverse CDF or sample.
    _validate_inputs(normalized)
    return {
        "schema": "k01_reference_input_view_v1", "status": "prepared_metadata_view_not_activated",
        "approved_for_builder": False, "clinical_execution_authorized": False,
        "packet_manifest_sha256": expected_manifest_sha256, "source_bindings": bindings,
        "selected_item_count": len(normalized), "normalized_source_constraints": normalized,
        "normalized_constraints_sha256": _sha(_canonical(normalized, ensure_ascii=True)),
        "normalized_digest_convention": "sorted compact JSON, ensure_ascii=True; same as pure fit provenance",
        "record_mappings": mapping, "count_divisions_performed_by_normalizer": 0,
        "fit_calls": 0, "sample_calls": 0, "parameters_produced": False,
        "authentication_scope": "Expected manifest and source bytes verified; no publisher authentication, approval signature or execution verification",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-view", action="store_true", required=True)
    parser.add_argument("--expected-manifest-sha256", required=True)
    args = parser.parse_args()
    case = Path(__file__).resolve().parent.parent
    request = case/"request"
    view = prepare_reference_inputs(
        selected_evidence_bytes=(request/"selected_source_evidence.json").read_bytes(),
        diagnostic_plan_bytes=(request/"descriptive_diagnostic_plan.json").read_bytes(),
        packet_manifest_bytes=(request/"packet_manifest.json").read_bytes(),
        expected_manifest_sha256=args.expected_manifest_sha256,
    )
    view["normalizer_code_sha256"] = _sha(Path(__file__).read_bytes())
    view["reference_code_sha256"] = _sha((case/"implementation"/"statistical_reference.py").read_bytes())
    with (case/"REFERENCE_INPUT_VIEW.json").open("x", encoding="utf-8", newline="\n") as output:
        json.dump(view, output, ensure_ascii=False, indent=2, allow_nan=False)
        output.write("\n")
    print("Prepared18-record metadata-only reference input view; no fit or sample.")


if __name__ == "__main__":
    main()
