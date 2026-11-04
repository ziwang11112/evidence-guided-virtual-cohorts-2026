"""Metadata-only completion after the documented scope-scanner false positive.

No SAS/CSV decoder, pandas, NumPy, fitting, sampling or study-data imports.
Raw input files are opened only as binary streams to verify their pinned hashes.
The original independent program, receipt and production report stay unchanged.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ORIGINAL_CODE_SHA = "98439a57a3c6db963ae0f56a2f467da5beef533df881ab0c685f2206de07ab18"
REPORT_SHA = "bc836fd61973ca7ece74855b87c0064d3b07ecb37228316318099239460ca95f"


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def write(name, value):
    content = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    with (HERE / name).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(content)


def scan_aggregates(value, path="report"):
    forbidden = {"person_id", "IDind", "Idind", "survey_commid", "commid", "r1_positions", "r2_positions",
                 "selected_row_positions", "assigned_community_positions", "membership", "members", "rows"}
    if isinstance(value, dict):
        for key, entry in value.items():
            entry_path = f"{path}.{key}"
            if entry_path == "report.design.selection_hash_domains.rows":
                need(entry == "real_real:rows:v1", "Unexpected row-hash domain label")
            elif entry_path == "report.provenance.reference_quality.native_missing.surveys_pub_12.sas7bdat.commid":
                need(type(entry) is int and entry >= 0, "Unexpected community-field missing count")
            else:
                need(key not in forbidden, f"Unexpected participant-level field: {entry_path}")
            scan_aggregates(entry, entry_path)
    elif isinstance(value, list):
        need(len(value) < 3000, f"Unexpected row-length array: {path}")
        for i, entry in enumerate(value):
            scan_aggregates(entry, f"{path}[{i}]")


def main():
    need(not (HERE / "INDEPENDENT_REVIEW.json").exists(), "Final independent report already exists")
    need(sha(HERE / "independent_review.py") == ORIGINAL_CODE_SHA, "Original audit code changed")
    need(sha(HERE / "REPORT.json") == REPORT_SHA, "Production report changed")
    original_receipt = read("INDEPENDENT_READ_RECEIPT.json")
    failure = read("INDEPENDENT_REVIEW_FAILURE.json")
    need(original_receipt["independent_code_sha256"] == ORIGINAL_CODE_SHA
         and original_receipt["production_report_sha256"] == REPORT_SHA, "Original receipt differs")
    need(failure["original_code_sha256"] == ORIGINAL_CODE_SHA and failure["exit_code"] == 1
         and failure["failure_message"] == "Participant-level field in report: report.design.selection_hash_domains.rows",
         "Unexpected original failure")
    # Bind the exact source checkpoint and the earlier completed assertions.
    source = (HERE / "independent_review.py").read_text(encoding="utf-8").splitlines()
    need(source[457].strip() == "scope = aggregate_scope(report)", "Traceback/source checkpoint mismatch")
    need(source[455].strip() == "historical = historical_check(protocol, reference, generated, historical_comparator)",
         "Historical comparison checkpoint changed")
    need("compare.check(report[name], expected, name)" in "\n".join(source[418:431]), "Numeric loop checkpoint changed")
    report = read("REPORT.json")
    scan_aggregates(report)
    need(set(report) == {"schema_version", "kind", "design", "generated", "splits", "summary", "limitations", "provenance"},
         "Unexpected production section")
    need(report["design"]["seeds"] == list(range(8400, 8500)) and len(report["splits"]) == 100
         and report["design"]["metric_n"] == 36, "Aggregate schedule differs")
    files = sorted(p for p in HERE.rglob("*") if p.is_file())
    figures = {"REAL_REAL_CONTEXT.png", "REAL_REAL_CONTEXT.svg"}
    for path in files:
        need(path.parent == HERE, "Unexpected nested output")
        need(path.suffix in {".json", ".md", ".py"} or path.name in figures, "Unexpected output artifact")
    renderer = (HERE / "render_results.py").read_text(encoding="utf-8")
    need("report = json.loads((HERE/'REPORT.json').read_text(encoding='utf-8'))" in renderer,
         "Renderer does not use the known aggregate report")
    need(all(token not in renderer for token in ("read_csv", "read_sas", "private_data", "generated.csv")),
         "Renderer has a data-decoding path")
    # Check the entire displayed 36-row table against the aggregate report.
    table = (HERE / "COMPLETE_METRIC_TABLE.md").read_text(encoding="utf-8")
    labels = list(report["generated"])
    def formatted(q):
        return "Unavailable" if q["median"] is None else f"{q['median']:.5g} [{q['q10']:.5g}, {q['q90']:.5g}]"
    expected_lines = []
    for name in report["design"]["metric_names"]:
        item = report["summary"][name]
        expected_lines.append("| " + name + " | " + formatted(item["real_real"]["absolute"]) + " | "
            + " | ".join(formatted(item["generated"][label]["sym_abs"]) for label in labels) + " |")
    actual_lines = [line for line in table.splitlines() if any(line.startswith("| " + name + " |")
                    for name in report["design"]["metric_names"])]
    need(actual_lines == expected_lines and len(actual_lines) == 36, "Complete metric table differs from REPORT")
    posthashes = {}
    for label, item in original_receipt["frozen_inputs_before_decode"].items():
        actual = sha(item["path"])
        need(actual == item["sha256"], f"Input changed after independent numerical audit: {label}")
        posthashes[label] = {"sha256": actual, "unchanged": True}
    result = {
        "schema_version": 1, "status": "PASS", "execution_status": "completed_in_two_stages_with_documented_reviewer_scanner_repair",
        "created_utc": datetime.now(timezone.utc).isoformat(), "production_report_sha256": REPORT_SHA,
        "original_independent_code_sha256": ORIGINAL_CODE_SHA,
        "independent_read_receipt_sha256": sha(HERE / "INDEPENDENT_READ_RECEIPT.json"),
        "original_failure_record_sha256": sha(HERE / "INDEPENDENT_REVIEW_FAILURE.json"),
        "metadata_scanner_failure_record_sha256": sha(HERE / "INDEPENDENT_REVIEW_CONTINUATION_FAILURE.json"),
        "metadata_only_continuation_code_sha256": sha(__file__),
        "numeric_stage": {
            "status": "all_scheduled_numerical_assertions_completed_without_failure",
            "evidence": {"source_file": "independent_review.py", "traceback_line": 458,
                "statement": "scope = aggregate_scope(report)", "historical_check_line": 456,
                "traceback_record": "INDEPENDENT_REVIEW_FAILURE.json",
                "basis": "The retained actual traceback occurs only after all numeric and historical comparison calls return; it is bound to the unchanged original code and report hashes."},
            "scope": "Every production numeric field; all 100 seeds and selection hashes/attempts; 36 point metrics; all RR signed/absolute, G-R2 signed/absolute, symmetric absolute and summary values; historical shared point-statistic anchors.",
            "method": "Separate PCG64 pool enumeration/hash encoding; SciPy Householder QR; math.fsum means/sample SD; explicit linear quantile interpolation; SciPy Pearson/Spearman.",
            "production_statistical_functions_imported_or_called": False,
            "tolerance": {"relative": 1e-9, "absolute": 2e-11},
            "numeric_leaf_comparison_count": None, "maximum_absolute_difference": None,
            "unpersisted_diagnostics_reason": "Original process exited at the later false-positive scope scanner before these in-memory diagnostics were written. No counter or maximum is inferred or reconstructed.",
        },
        "actual_execution_cost": {"full_independent_numerical_runs": 1,
            "summarized_frames": {"total": 204, "sampled_real_halves": 200, "fixed_generated_tables": 3,
                                  "old_full_reference_for_historical_anchor": 1},
            "repeated_frame_recalculations_after_failure": 0, "new_generator_executions": 0,
            "metadata_continuation_attempts": 2,
            "original_run_observed_wall_seconds": failure["observed_wall_time_seconds"],
            "continuation_row_decodes": 0, "continuation_regression_fits": 0,
            "continuation_input_access": "JSON/code/Markdown aggregate reads and binary hashing of frozen input bytes only."},
        "selection": {"reference_n": 6631, "reference_community_n": 218, "split_n": 100,
            "seeds": list(range(8400, 8500)), "sample_n_per_side": 3000, "assigned_communities_per_side": 109,
            "person_and_community_disjointness": "All scheduled assertions passed in original numerical stage.",
            "alternate_linkage": "Separate survey-master-exam merge order plus BMI/eligibility derivation; ordered selected-frame equality passed."},
        "historical_consistency": {"status": "all_shared_coefficient_marginal_and_relationship_assertions_passed",
            "new_diagnostics": "BMI-glucose Pearson/Spearman were prespecified for this developmental unit, not historical holdout outcomes.",
            "historical_intervals": "Unchanged; no historical campaign or interval fit rerun."},
        "resolved_scanner_issue": {"path": "report.design.selection_hash_domains.rows", "value": "real_real:rows:v1",
            "resolution": "Narrow path-and-value exception for this fixed domain-label string, plus the exact native_missing survey commid path when a nonnegative integer count; all other row/identifier/membership fields remain prohibited.",
            "metadata_followup_false_positive": "First metadata scan also rejected the aggregate commid missing count by field name. Its separate failure record is retained. Only aggregate scanning was repeated; no numerical or row computation was repeated.",
            "aggregate_figures": "Explicit allowance for the known PNG/SVG figures produced solely from REPORT.json; no data-decoding path in renderer."},
        "aggregate_output_scope": {"status": "PASS", "participant_or_generated_rows_exported": 0,
            "complete_36_metric_table_matches_report": True, "files_scanned": [p.name for p in files],
            "renderer_sha256": sha(HERE / "render_results.py"),
            "figure_hashes": {name: sha(HERE / name) for name in sorted(figures)}},
        "input_hashes_unchanged_after_review": True, "postreview_hashes": posthashes,
        "production_and_original_audit_files_modified": False,
        "scientific_interpretation": "Arithmetic/accounting audit only. All 100 splits are same-cohort developmental analyses; no independent cohort, biological-utility revalidation, equivalence threshold or clinical certification."
    }
    write("INDEPENDENT_REVIEW.json", result)
    text = "\n".join([
        "# Independent numerical review", "",
        "**PASS — numerical assertions completed; a later reviewer scope-scanner false positive was resolved in a metadata-only continuation.**", "",
        "The one full independent run rebuilt all 100 seeds (8400–8499), selection hashes and attempt logs, all 36 point metrics, every signed/absolute/symmetric discrepancy and all summary quantiles. It also checked the shared historical coefficient, marginal and relationship anchors. The completed 204 frames were 200 real halves, three fixed generated tables and one old full-reference anchor; there was no new generation or repeated frame calculation.", "",
        "The original program then exited at line 458 when its scope scanner incorrectly treated the fixed `report.design.selection_hash_domains.rows` string (`real_real:rows:v1`) as patient rows. The actual traceback is retained in [INDEPENDENT_REVIEW_FAILURE.json](INDEPENDENT_REVIEW_FAILURE.json). The unchanged original code shows that all numerical and historical comparison calls precede this checkpoint. A numerical assertion failure would have exited earlier.", "",
        "The follow-up [independent_review_continue.py](independent_review_continue.py) reads metadata, the aggregate REPORT and rendered table, and hashes frozen input bytes. It performs no row decoding, fitting or sampling. Its first scope pass also flagged the integer missing-value count named `commid`; that second field-name false positive is retained in [INDEPENDENT_REVIEW_CONTINUATION_FAILURE.json](INDEPENDENT_REVIEW_CONTINUATION_FAILURE.json). The final scanner permits only the exact hash-domain string and the exact nonnegative missing-count path, retains other identifier/membership prohibitions, and admits the known aggregate PNG/SVG figures produced solely from REPORT.json. There was one full numerical run and two metadata-only continuation attempts.", "",
        "Every bound input hash remains unchanged after the audit, and the complete 36-metric displayed table matches REPORT.json. Output contains only original code, controls, aggregate statistics, counts, hashes and aggregate figures. The production report, original audit program and original read receipt remain untouched.", "",
        "Numerical comparison tolerances were rtol=1e-9 and atol=2e-11. The exact comparison counter and maximum absolute difference were still in memory when the later scanner error ended the process; both are therefore null in the review record. They were not reconstructed or invented, and the clinical data were not reprocessed to recover them.", "",
        "The calculations used independent pool enumeration and hash construction, SciPy QR regression, math.fsum means/sample SD, explicit linear quantile interpolation and SciPy correlations. A different linkage order and independent measurement/eligibility derivation reproduced the entire ordered selected frame. Production statistical functions were not imported or called.", "",
        "BMI–glucose Pearson/Spearman are newly prespecified developmental diagnostics, not earlier holdout outcomes. Historical intervals remain unchanged. All 100 splits remain same-cohort development analyses; this audit does not revalidate biological utility or establish clinical validity, external transportability, equivalence, a scientific pass threshold or independent-cohort calibration.", ""
    ])
    with (HERE / "INDEPENDENT_REVIEW.md").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
    print(json.dumps({"status": "PASS", "stages": 2, "full_numerical_runs": 1,
        "frames": 204, "continuation_row_decodes": 0, "posthash_count": len(posthashes),
        "maximum_absolute_difference": None, "numeric_comparison_count": None}, indent=2))


if __name__ == "__main__":
    main()
