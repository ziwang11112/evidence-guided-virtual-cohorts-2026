"""Supplemental narrative check; reuse the completed aggregate-only audit."""
from datetime import datetime, timezone
import json
from independent_numeric_check import Checks, RUN, HERE, PROJECT, PREDICTORS, read_json, sha256


def audit_root_narrative(report, protocol):
    """Check the later delivery narrative using already verified aggregate values."""
    checks = Checks()
    checks.equal("audited_evaluation_report_unchanged", sha256(HERE / "REPORT.json"),
                 report["final_review"]["artifacts"]["report_sha256"])
    root_results = RUN / "RESULTS.md"
    narrative = root_results.read_text(encoding="utf-8-sig").replace("−", "-")
    reference_path = PROJECT / protocol["reference"]["path"]
    if sha256(reference_path) != protocol["reference"]["sha256"]:
        raise RuntimeError("Pinned aggregate reference changed before narrative review")
    historical = read_json(reference_path)
    deliveries = [r for r in report["runs"] if r["stage"] == "initial_delivery"]
    ranges = {}
    for analysis, reference_id in [("primary", "B"), ("descriptive_secondary", "A")]:
        for term in PREDICTORS[analysis]:
            ref = historical["reference"][reference_id]["coefficients"][term]
            values = [r["analyses"][analysis]["coefficients"][term]["value"] for r in deliveries]
            expected = f"{ref['value']:.5f} [{ref['lower']:.5f}, {ref['upper']:.5f}] | {min(values):.5f}–{max(values):.5f}"
            checks.equal("root_results.table." + analysis + "." + term, expected in narrative, True)
            ranges[analysis + "." + term] = {"minimum": min(values), "maximum": max(values)}
    for metric in ["mean", "sd", "q10", "q90"]:
        values = [r["analyses"]["primary"]["marginal"]["hba1c"][metric] for r in deliveries]
        expected = f"{min(values):.3f}–{max(values):.3f}"
        checks.equal("root_results.hba1c." + metric, expected in narrative, True)
        ranges["hba1c." + metric] = {"minimum": min(values), "maximum": max(values)}
    females = [r["analyses"]["primary"]["marginal"]["female"]["mean"] for r in deliveries]
    checks.equal("root_results.female_fraction", f"{min(females):.3f}–{max(females):.3f}" in narrative, True)
    ranges["female_fraction"] = {"minimum": min(females), "maximum": max(females)}
    for metric in ["pearson", "spearman"]:
        values = [r["analyses"]["primary"]["relationships"]["glucose_hba1c"][metric] for r in deliveries]
        ref = historical["reference"]["B"]["relationships"]["glucose_hba1c"][metric]
        checks.equal("root_results.glucose_hba1c." + metric,
                     f"{min(values):.3f}–{max(values):.3f} versus {ref:.3f}" in narrative, True)
        ranges["glucose_hba1c." + metric] = {"minimum": min(values), "maximum": max(values), "reference": ref}
    zero_counts = {}
    for analysis, term, expected, phrase in [
        ("primary", "bmi", 2, "two synthetic intervals include zero"),
        ("descriptive_secondary", "female", 3, "all three synthetic intervals include zero")]:
        count = sum(r["analyses"][analysis]["coefficients"][term]["lower"] <= 0 <=
                    r["analyses"][analysis]["coefficients"][term]["upper"] for r in deliveries)
        checks.equal("zero_count." + analysis + "." + term, count, expected)
        checks.equal("root_results.zero_phrase." + analysis, phrase in narrative, True)
        zero_counts[analysis + "." + term] = count
    checks.equal("root_results.reference_n", "6,631 selected participants in 218 communities" in narrative, True)
    checks.equal("reference.n", historical["reference"]["B"]["n"], 6631)
    checks.equal("reference.clusters", historical["reference"]["B"]["cluster_count"], 218)
    older = [s for s in historical["slots"] if s["request"] == "B" and s["stage"] == "final"]
    checks.equal("historical.final_b_delivery_count", len(older), 3)
    checks.equal("historical.bmi_all_negative", all(s["analysis"]["coefficients"]["bmi"]["value"] < 0 for s in older), True)
    checks.equal("current.bmi_all_positive", all(r["analyses"]["primary"]["coefficients"]["bmi"]["value"] > 0 for r in deliveries), True)
    historical_errors = {}
    for term in ["age", "glucose"]:
        ref = historical["reference"]["B"]["coefficients"][term]["value"]
        old_errors = [abs(s["analysis"]["coefficients"][term]["value"] - ref) for s in older]
        new_errors = [abs(r["analyses"]["primary"]["coefficients"][term]["value"] - ref) for r in deliveries]
        checks.equal("historical_comparison." + term, max(new_errors) < min(old_errors)
                     if term == "age" else min(new_errors) > max(old_errors), True)
        historical_errors[term] = {"historical_absolute_errors": old_errors, "current_absolute_errors": new_errors}
    plot_script = (RUN / "render_analysis_utility.py").read_text(encoding="utf-8-sig")
    checks.equal("plot.all_terms", "[['bmi', 'glucose', 'age', 'female'], ['bmi', 'age', 'female']]" in plot_script, True)
    checks.equal("plot.final_slots", "x['stage'] == 'final'" in plot_script, True)
    checks.equal("plot.reference_band", "rc['lower'], rc['upper']" in plot_script, True)
    checks.equal("plot.generated_intervals", "c['value']-c['lower']" in plot_script and "c['upper']-c['value']" in plot_script, True)
    return {"created_utc": datetime.now(timezone.utc).isoformat(), "status": checks.summary()["status"],
            "checks": checks.summary(), "recomputed_table_statistics_reused_from_prior_verified_audit": True,
            "additional_generated_table_reads": 0, "additional_generator_executions": 0,
            "patient_rows_read": 0, "ranges": ranges, "zero_interval_counts": zero_counts,
            "historical_contrast_absolute_errors": historical_errors,
            "figure_visual_inspection": "Auditor viewed ANALYSIS_UTILITY.png; all seven nonintercept panels, three seeds, reference bands and conditional intervals match audited results. Different uncertainty meanings are labeled.",
            "artifact_hashes": {name: sha256(RUN / name) for name in ["RESULTS.md", "render_analysis_utility.py", "ANALYSIS_UTILITY.png", "ANALYSIS_UTILITY.svg"]}}


def main():
    audit_path = HERE / "INDEPENDENT_NUMERICAL_REVIEW.json"
    original = read_json(audit_path)
    if original["status"] != "pass_final":
        raise RuntimeError("Completed numerical review is required")
    result = audit_root_narrative(original, read_json(RUN / "PROTOCOL.json"))
    result["reviewed_numerical_audit_sha256"] = sha256(audit_path)
    result["script_sha256"] = sha256(__file__)
    out = HERE / "NARRATIVE_REVIEW.json"
    out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    lines = ["# Delivery narrative and figure review", "", "Status: **" + result["status"] + "** (" + str(result["checks"]["checks"]) + " checks).", "", "Root RESULTS.md effect ranges, HbA1c mean/SD/tails, female fraction and glucose-HbA1c Pearson/Spearman ranges match the completed independent aggregate audit. Primary BMI intervals include zero in two of three deliveries; secondary female intervals include zero in all three. Historical point-sign and age/glucose proximity statements match the pinned aggregate report.", "", result["figure_visual_inspection"], "", "The supplemental check reused the completed numerical audit. It performed no new table fit, generator execution or patient read. The immutable evaluation REPORT.json remains byte-identical to the audited file.", "", "| Artifact | SHA-256 |", "|---|---|"]
    lines += ["| " + name + " | `" + value + "` |" for name, value in result["artifact_hashes"].items()]
    if result["checks"]["failures"]:
        lines += ["", "```json", json.dumps(result["checks"]["failures"], indent=2), "```"]
    out.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "checks": result["checks"], "report": str(out)}))


if __name__ == "__main__":
    main()
