"""Assemble retrospective attribution from reviewed aggregate artifacts only.

Does not import scientific generators, read row-level data or call a model.
"""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8-sig"))


def bound(name):
    p = ROOT / name
    return {"file": name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}


def implied(record):
    if "numeric_value" in record:
        return record["numeric_value"]
    if "value_mmol_L" in record:
        return record["value_mmol_L"] * 38.67
    return record.get("value")


main, pns, other = map(read, ["MAIN_STUDY_AUDIT.json", "PNS_AUDIT.json", "LIPID_IRON_AUDIT.json"])
constructors = {c["constructor_id"]: c for c in main["constructors"]}
rows = []
for i, r in enumerate(main["endpoint_rows"]):
    c = constructors[r["constructor_id"]]
    s = r["existing_outcome_summary"]
    rows.append({
        "id": "main/" + r["row_id"], "case": r["case_id"],
        "construction": r["constructor_id"], "analysis": r["endpoint_label"],
        "unit": r["unit"], "record_role": "main_analysis",
        "source_statistic_context": c["reported_and_derived_inputs_summary"],
        "source_coverage": r["source_coverage"],
        "adopted_model": c["law_summary"],
        "parameter_provenance": c["native_grouped_parameter_provenance"],
        "analysis_dependency_chain": r["dependency_chain"],
        "model_implied_requested_value": None,
        "model_implied_status": "Not numerically derived in this integrated audit; see the dependency chain. Never substitute an adopted parameter or generated estimate.",
        "generated_summary_kind": "mean", "generated_value": s["mean_effect"],
        "generated_range": s["seed_effect_range"], "n_seeds": s["available_values"],
        "reference_value": r["reference"]["value"], "reference": r["reference"],
        "detail_file": "MAIN_STUDY_AUDIT.json", "detail_pointer": f"/endpoint_rows/{i}",
        "predicted_error": None, "validated_reliability_class": None,
    })
for i, r in enumerate(pns["analysis_rows"]):
    s = r["generated_summary"]
    rows.append({
        "id": "pns/" + r["row_id"], "case": "PNS_BP",
        "construction": r["author_id"], "analysis": r["endpoint_id"],
        "unit": r["requested_unit"], "record_role": "main_analysis",
        "source_statistic_context": r["source_statistics"],
        "source_coverage": r["source_evidence_status"],
        "adopted_model": r["literal_declared_parameter"],
        "parameter_provenance": r["parameter_provenance"],
        "analysis_dependency_chain": r["relevant_assumptions"],
        "model_implied_requested_value": r["model_implied_requested_value"]["value"],
        "model_implied_status": r["model_implied_requested_value"]["reason"],
        "generated_summary_kind": "median", "generated_value": s["median"],
        "generated_range": [s["minimum"], s["maximum"]], "n_seeds": s["n_draws"],
        "reference_value": r["target_reference"]["point"], "reference": r["target_reference"],
        "detail_file": "PNS_AUDIT.json", "detail_pointer": f"/analysis_rows/{i}",
        "predicted_error": None, "validated_reliability_class": None,
    })
for i, r in enumerate(other["rows"]):
    s, ref, theory = r["generated_aggregate"], r["reference"], r["model_implied_analysis_estimand"]
    rows.append({
        "id": "lipid_iron/" + r["row_id"],
        "case": "Turkana_lipids" if r["author"].startswith("L") else "NHANES_iron",
        "construction": r["author"], "analysis": r["analysis"],
        "unit": s["unit"], "record_role": r["record_role"],
        "source_statistic_context": r["source_statistics"],
        "source_coverage": "See statistical operator and bridge; provenance is not an ordinal reliability score.",
        "adopted_model": r["declared_parameters"],
        "parameter_provenance": r["declared_parameters"],
        "analysis_dependency_chain": r["bridge_assumptions"],
        "model_implied_requested_value": implied(theory),
        "model_implied_status": theory,
        "generated_summary_kind": "mean", "generated_value": s["mean"],
        "generated_range": [min(s["seed_values"]), max(s["seed_values"])],
        "n_seeds": len(s["seed_values"]),
        "reference_value": ref.get("value", ref.get("estimate")), "reference": ref,
        "detail_file": "LIPID_IRON_AUDIT.json", "detail_pointer": f"/rows/{i}",
        "predicted_error": None, "validated_reliability_class": None,
    })

counts = Counter(r["record_role"] for r in rows)
assert counts == {"main_analysis": 90, "supplementary_dispersion": 6}, counts
assert len({r["id"] for r in rows}) == len(rows)
assert all(r["n_seeds"] == 3 for r in rows)
assert all(r["reference_value"] is not None for r in rows)
assert all(r["predicted_error"] is None and r["validated_reliability_class"] is None for r in rows)
construct_count = len({(r["case"], r["construction"]) for r in rows})
assert construct_count == 30, construct_count

result = {
    "schema_version": 1, "date": "2026-11-10",
    "status": "retrospective_attribution_not_prospective_reliability_validation",
    "scope": "Thirty Agent constructions: main CHNS/ENSANUT20, PNS5, Q5 lipids3, iron2. Historical controls, HRS, HAALSI and other later/earlier versions are outside this first integrated attribution table.",
    "counts": {"constructions": construct_count, **counts},
    "input_bindings": [bound(n) for n in ["MAIN_STUDY_AUDIT.json", "PNS_AUDIT.json", "LIPID_IRON_AUDIT.json"]],
    "limits": [
        "One analysis can depend on reported, derived and assumed parameters simultaneously.",
        "An adopted conditional parameter is not automatically the requested post-selection regression estimand.",
        "Unknown model-implied quantities remain null. Finite seeds are not substituted.",
        "Reference samples are not known population truths; uncertainty definitions stay in each record.",
        "Means and medians are explicitly distinguished; no pooled cross-metric accuracy score or causal attribution is calculated.",
        "This is an outcome-aware retrospective audit; no validated reliability classes or prospective error predictions exist.",
    ],
    "rows": rows,
}
(ROOT / "ATTRIBUTION_MASTER.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def num(x):
    return "not derived" if x is None else f"{x:.6g}"

lines = [
    "# Evidence, model commitments and scientific analyses: attribution master table",
    "",
    "Retrospective audit, 10 November 2026. **30 Agent constructions, 90 requested-analysis records and 6 supplementary dispersion records.** These counts describe audit coverage, not independent clinical confirmations. No new cohort was generated or fitted.",
    "",
    "This first table covers the twenty main CHNS/ENSANUT constructions, five PNS authors, three Q5 lipid authors and two iron authors. It does not claim to cover every historical project experiment. HRS, HAALSI, statistical controls and other workflow versions remain in their original reports.",
    "",
    "The linked JSON contains source statistics, adopted parameters/provenance, bridging assumptions, model-implied estimands, generated estimates and measured references separately. Each row points to its detailed audit record. **Reported / derived / assumed are origins, not accuracy grades.** All retrospective reliability predictions remain null.",
    "",
    "Read [the interpretation](INTERPRETATION_ZH.md), [main-study audit](MAIN_STUDY_AUDIT.md), [PNS audit](PNS_AUDIT.md), or [lipid/iron audit](LIPID_IRON_AUDIT.md). Full machine-readable table: [ATTRIBUTION_MASTER.json](ATTRIBUTION_MASTER.json).",
    "",
    "The compact tables below are an index to the five-stage attribution, not a replacement for the source/parameter records. They retain requested analyses in native units. Generated ranges cover three draws of one law, not confidence intervals; PNS uses medians, other cases means. Reference uncertainty remains in the detail records and original reports. Missing theoretical values were not backfilled from sampled estimates or source coefficients.",
]
for role in ["main_analysis", "supplementary_dispersion"]:
    for case in dict.fromkeys(r["case"] for r in rows if r["record_role"] == role):
        selected = [r for r in rows if r["case"] == case and r["record_role"] == role]
        lines += ["", f"## {case} — {role}", "",
                  "| Author | Requested analysis (unit) | Model-implied | Generated summary [seed range] | Sample reference | Detail row |",
                  "|---|---|---:|---|---:|---|"]
        for r in selected:
            lo, hi = r["generated_range"]
            lines.append(f"| {r['construction']} | {r['analysis']} ({r['unit']}) | {num(r['model_implied_requested_value'])} | {r['generated_summary_kind']} {num(r['generated_value'])} [{num(lo)}, {num(hi)}] | {num(r['reference_value'])} | {r['detail_file']} `{r['detail_pointer']}` |")
(ROOT / "ATTRIBUTION_MASTER.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(json.dumps({"rows": len(rows), "constructions": construct_count, "role_counts": counts, "new_cohorts": 0}))
