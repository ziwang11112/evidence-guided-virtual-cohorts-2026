"""Invented packet bytes only; normalization never fits any source records."""
import hashlib
import json

import pytest

import prepare_reference_inputs as prep
import statistical_reference as ref
from test_statistical_reference import invented_records


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def invented_packet():
    selected = {"schema": "k01_sanitized_selected_source_packet_v1", "records": []}
    plan = {"schema": "k01_prospective_descriptive_diagnostic_plan_v1", "diagnostic_count": 18, "items": []}
    for row in invented_records():
        item, context = row["evidence_id"], row["context_id"]
        is_mind = context == ref.MIND_CONTEXT
        source = "WANG2024_MIND" if is_mind else "ayele_2020_dire_dawa"
        original = dict(id=item, source_id=source, variable=row["variable"],
                        statistic=row["statistic"], unit=row["unit"])
        if is_mind and row["variable"] == "glucose": original["variable"] = "serum_glucose_fsg"
        original["source_locator" if is_mind else "locator"] = row["locator"]
        diagnostic = dict(id="descriptive__"+item, evidence_id=item, source_id=source,
                          context_id=context, operator=prep._operator(item),
                          comparison_unit=row["unit"], selection=[], generated_row_weights="equal")
        if "value" in row:
            original["estimate" if is_mind else "value"] = row["value"]
            diagnostic["comparison_value"] = row["value"]
        else:
            diagnostic["comparison_derivation"] = dict(numerator=row["numerator"], denominator=row["denominator"],
                                                        not_printed_percentage_division=True)
            if is_mind:
                original.update(statistic="sample_proportion", event="female", derivation={
                    "exact_numerator": row["numerator"], "exact_denominator": row["denominator"]})
            else:
                group = "≥25" if row["group"] == ">=25" else row["group"]
                original.update(statistic="printed_percentage", unit="%", group=group,
                    source_count=row["numerator"], source_denominator=row["denominator"], value=row["reported_percentage"])
                if row["variable"] == "bmi": original["category_unit"] = "kg/m^2"
                diagnostic.update(original_printed_percentage=row["reported_percentage"], original_printed_group=group)
        digest = hashlib.sha256(encoded(original)).hexdigest()
        diagnostic["original_record_canonical_sha256"] = digest
        selected["records"].append(dict(id=item, source_id=source, context_id=context,
            canonical_variable=row["variable"], record_class="potential_source_marginal",
            original_selected_record=original, provenance={"original_record_canonical_sha256": digest}))
        plan["items"].append(diagnostic)
    return selected, plan


def bundle(selected, plan):
    source_bytes, plan_bytes = encoded(selected), encoded(plan)
    manifest = {"schema": "k01_request_packet_manifest_v1", "files": {}}
    for name, data in (("selected_source_evidence.json", source_bytes), ("descriptive_diagnostic_plan.json", plan_bytes)):
        manifest["files"][name] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    manifest_bytes = encoded(manifest)
    return dict(selected_evidence_bytes=source_bytes, diagnostic_plan_bytes=plan_bytes,
                packet_manifest_bytes=manifest_bytes, expected_manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest())


def test_metadata_mapping_preserves_exact_counts_without_fitting(monkeypatch):
    def forbidden(*args, **kwargs): raise AssertionError("No fit or sample permitted")
    monkeypatch.setattr(ref, "fit_reference", forbidden)
    monkeypatch.setattr(ref, "sample", forbidden)
    view = prep.prepare_reference_inputs(**bundle(*invented_packet()))
    observed = {r["evidence_id"]: r for r in view["normalized_source_constraints"]}
    assert observed == {r["evidence_id"]: r for r in invented_records()}
    assert view["count_divisions_performed_by_normalizer"] == view["fit_calls"] == view["sample_calls"] == 0
    assert view["parameters_produced"] is False
    canonical = json.dumps(view["normalized_source_constraints"], sort_keys=True, separators=(",", ":"), allow_nan=False)
    assert view["normalized_constraints_sha256"] == hashlib.sha256(canonical.encode()).hexdigest()
    mapping = next(m for m in view["record_mappings"] if m["evidence_id"] == "ayele_bmi_overweight")
    assert "≥25 to ASCII>=25" in mapping["normalization"]


@pytest.mark.parametrize("defect", ["manifest_hash", "source_byte_hash", "source_identity", "context",
    "original_digest", "count_mapping", "middle_boundary", "moment_unit", "missing_id", "duplicate_diagnostic"])
def test_metadata_and_semantic_binding_rejects_tampering(defect):
    selected, plan = invented_packet()
    by_id = {r["id"]: r for r in selected["records"]}
    diag = {r["evidence_id"]: r for r in plan["items"]}
    if defect == "source_identity": by_id["MIND_K01_age_mean"]["source_id"] = "other_study"
    elif defect == "context": by_id["MIND_K01_age_mean"]["context_id"] = ref.AYELE_CONTEXT
    elif defect == "original_digest": by_id["MIND_K01_age_mean"]["original_selected_record"]["estimate"] = 71
    elif defect == "count_mapping": diag["ayele_bmi_underweight"]["comparison_derivation"]["numerator"] = 4
    elif defect == "middle_boundary": diag["ayele_bmi_normal"]["operator"]["boolean_event"]["all"][1] = {"column":"bmi","op":"lt","value":25}
    elif defect == "moment_unit": diag["MIND_K01_serum_glucose_fsg_mean"]["comparison_unit"] = "mg/dL"
    elif defect == "missing_id": selected["records"].pop()
    elif defect == "duplicate_diagnostic": plan["items"][-1] = plan["items"][0]
    inputs = bundle(selected, plan)
    if defect == "manifest_hash": inputs["expected_manifest_sha256"] = "0"*64
    elif defect == "source_byte_hash": inputs["selected_evidence_bytes"] += b" "
    with pytest.raises(ValueError): prep.prepare_reference_inputs(**inputs)
