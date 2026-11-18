"""Append a separately evidenced correction; never alter historical reviews or source packets."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re

U = Path(__file__).resolve().parent
OLD = U.parent/"cross_model_api_pilot_2026-11-10"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text(encoding="utf-8"))


def main():
    evidence_path = OLD/"packets/LIPID/evidence.json"
    artifact_path = OLD/"calls/LIPID_OA_ASTRA_C1_initial/artifact.json"
    evidence, artifact = read(evidence_path), read(artifact_path)
    table = evidence["sources"][1]["reported_statistics"]
    assert set(table) == {"format", "columns", "rows"} and len(table["rows"]) == 48
    assert sha(evidence_path) == "8f4686adea0ddd9e9d7f17e0c08c32ad5c7fff58f88874dd5bd85b341b4562ed"
    resolved = []
    for index, entry in enumerate(artifact["decision_record"]["parameter_provenance"]):
        for pindex, pointer in enumerate(entry.get("source_pointers", [])):
            if not isinstance(pointer, dict): continue
            path = pointer.get("evidence_path", "")
            match = re.fullmatch(r"\$\.sources\[1\]\.reported_statistics\.rows\[(\d+)\]", path)
            if not match: continue
            row_index = int(match.group(1)); row = dict(zip(table["columns"], table["rows"][row_index]))
            if "statistic_id" in pointer: assert pointer["statistic_id"] == row["id"]
            resolved.append({"author_field": f"decision_record.parameter_provenance[{index}].source_pointers[{pindex}]",
                "declared_pointer": pointer, "resolved_row_index": row_index, "resolved_statistic_id": row["id"],
                "resolved_estimate": row["estimate"], "resolved_unit": row["unit"], "path_resolves": True,
                "declared_statistic_id_matches": pointer.get("statistic_id") == row["id"] if "statistic_id" in pointer else None})
    assert len(resolved) == 16 and len({r["resolved_row_index"] for r in resolved}) == 12
    paths = [OLD/"provenance_review/CORE_PROVENANCE_REVIEW.md", OLD/"provenance_review/LIPID_CORE_REVIEW.md", OLD/"provenance_review/LIPID_CORE_REVIEW.json"]
    correction = {"id": "round1_greiner_astra_c1_rows_locator_erratum", "status": "confirmed_retraction_of_prior_reviewer_criticism",
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "incorrect_prior_claim": "Astra C1 .rows pointers fail because the supplied Greiner table uses .records.",
        "correction": "The actual frozen author packet uses reported_statistics={format,columns,rows}; there is no records field. All 16 declared .rows[i] occurrences resolve to 12 unique rows. All 12 occurrences carrying a statistic_id match it exactly; the other four locators identify the corresponding Uganda age median/Q3 rows. The earlier literal-path-error criticism is withdrawn.",
        "actual_reported_statistics_keys": list(table), "table_rows": 48, "table_column_count": len(table["columns"]),
        "path_occurrences_checked": 16, "unique_row_indices": 12, "named_statistic_id_matches": 12,
        "original_evidence_sha256": sha(evidence_path), "original_author_artifact_sha256": sha(artifact_path),
        "original_evidence_path": str(evidence_path), "original_author_artifact_path": str(artifact_path),
        "historical_reports_preserved": {str(p): sha(p) for p in paths}, "resolved_author_pointers": resolved,
        "effect": "Corrects an error in the prior reviewer report, not the author's source pointers. No source values, source packet, generator, statistical output, or other operator/transport conclusions are changed.",
        "scope": "Independent examination of the original admitted packet and captured author artifact, not a new article retrieval or article-level evidence audit."}
    target = U/"ROUND_ALIGNMENT_AUDIT.json"
    report = read(target)
    assert not report.get("historical_audit_errata"), "Correction already recorded"
    report["historical_audit_errata"] = [correction]
    report["supplemental_erratum_script_sha256"] = sha(Path(__file__))
    report["updated_utc"] = datetime.now(timezone.utc).isoformat()
    for path in paths + [evidence_path, artifact_path]: report["source_hashes"][str(path)] = sha(path)
    target.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8", newline="\n")
    with (U/"ROUND_ALIGNMENT_AUDIT.md").open("a", encoding="utf-8", newline="\n") as stream:
        stream.write("""
## Correction to the first-round provenance review

The earlier `CORE_PROVENANCE_REVIEW.md` (line 19), `LIPID_CORE_REVIEW.md` (line 37) and associated `LIPID_CORE_REVIEW.json` wrongly said that Astra C1's Greiner `.rows` evidence pointers should have used `.records`. **That criticism is retracted.** The actual frozen author packet encodes `reported_statistics` using exactly `format`, `columns`, and `rows`; no `records` field exists. All 16 declared `.rows[i]` pointer occurrences resolve to 12 unique rows. All 12 occurrences with a declared statistic ID match the resolved ID exactly; the other four correctly identify the Uganda age median/Q3 rows.

This is an error in the previous reviewer report, not a source-pointer failure by the author. The original packet SHA-256 is `8f4686adea0ddd9e9d7f17e0c08c32ad5c7fff58f88874dd5bd85b341b4562ed`; the captured Astra C1 artifact SHA-256 is `ece8aedcbb32106f24c9e0f833443f0cb40a52637de1c4e533ab6e6c027c935f`. The JSON audit stores each pointer, its resolved row and the exact historical-report hashes. Historical audits remain unchanged for traceability. No source values, programs, numerical results or separate statistical-operator/transport conclusions are altered. This check used the admitted frozen packet and captured artifact; it was not a new original-article audit.
""")
    print(json.dumps({"status": "pass", "erratum": correction["id"], "pointer_occurrences": len(resolved), "updated_report_sha256": sha(target)}, indent=2))


if __name__ == "__main__": main()
