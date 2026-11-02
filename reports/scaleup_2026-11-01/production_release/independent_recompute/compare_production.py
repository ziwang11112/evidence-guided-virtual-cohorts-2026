"""Compare committed independent aggregates with production JSON, never project math.

This performs no fitting and does not read cohort tables. The complete numerical
comparison is reproducible from two pinned report files. Boolean/integer/identity
checks are exact; floating point checks allow at most 1e-12 absolute plus relative
roundoff. Threshold decisions themselves must match exactly.
"""
import hashlib
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parent.parent.parents[3]
INDEPENDENT = HERE / "INDEPENDENT_WAVE_A_RESULTS.json"
PRODUCTION = WORKSPACE / "evcA/evaluation_results/FULL_EVALUATION.json"
EXPECTED_INDEPENDENT = "2070ea209071d39c74749cbab064a83038cec21baaaf5ea7e50ba523def2f4a7"
EXPECTED_PRODUCTION = "4bcebaffbf0600b0c0e613d8274107c4d952d688e363760ec613ee27870d970d"
ATOL = RTOL = 1e-12
checks = []


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def equal(category, location, independent, production):
    checks.append({"category": category, "location": location, "independent": independent,
                   "production": production, "pass": independent == production, "absolute_difference": None})


def number(category, location, independent, production):
    if independent is None or production is None:
        equal(category, location, independent, production)
        return
    finite = math.isfinite(independent) and math.isfinite(production)
    difference = abs(independent - production) if finite else None
    checks.append({"category": category, "location": location, "independent": independent,
                   "production": production, "pass": finite and math.isclose(independent, production, rel_tol=RTOL, abs_tol=ATOL),
                   "absolute_difference": difference})


def compare_analysis(label, ours, theirs, reference):
    n = ours["eligibility"]["eligible_n"]
    for own_key, production_key in (("input_n", "input_rows"), ("eligible_n", "eligible_rows"), ("excluded_n", "excluded_rows")):
        equal("eligibility_counts", label + "/" + own_key, ours["eligibility"][own_key], theirs["selection"][production_key])
    # Compare equivalent reason categories. Per-variable nonfinite counts in the
    # independent report intentionally have finer granularity than production's
    # union missing_numeric/infinite_numeric fields; no false summation of overlaps.
    own_reasons = ours["eligibility"]["overlapping_exclusion_counts"]
    production_reasons = theirs["selection"]["reason_counts_overlap"]
    reason_map = {"sex_missing": "missing_sex", "age_below_minimum": "age_below_40" if label.startswith("K01") else "age_below_18"}
    reason_map.update({key: key for key in own_reasons if key.startswith("nonpositive_")})
    for own_key, production_key in reason_map.items():
        equal("comparable_exclusion_reasons", label + "/" + own_key, own_reasons[own_key], production_reasons[production_key])
    own_design = ours["design"]
    production_design = theirs.get("designs", {"base": theirs.get("design")})
    equal("designs", label + "/design_inventory", sorted(own_design), sorted(production_design))
    for key, design in own_design.items():
        other = production_design[key]
        for field in ("rank", "columns"):
            equal("designs", label + "/" + key + "/" + field, design[field], other[field])
        equal("designs", label + "/" + key + "/n", n, other["n"])
        number("designs", label + "/" + key + "/rank_tolerance", design["rank_tolerance"], other["rank_tolerance"])
    equal("endpoint_inventory", label, sorted(ours["endpoints"]), sorted(theirs["estimands"]))
    for endpoint, own in ours["endpoints"].items():
        other = theirs["estimands"][endpoint]
        where = label + "/" + endpoint
        equal("endpoint_availability", where, own["available"], other["status"] == "computed")
        number("reference_points" if reference else "generated_points", where, own["value"], other["estimate"])
        equal("endpoint_sample_sizes", where, n, other["n"])
        interval = other["interval"]
        own_interval = own["hc3_interval"]
        equal("interval_availability", where, own_interval is not None, interval["status"] == "available")
        number("hc3_standard_errors", where, own["hc3_se"], interval["standard_error"])
        number("hc3_bounds", where + "/lower", None if own_interval is None else own_interval[0], interval["lower"])
        number("hc3_bounds", where + "/upper", None if own_interval is None else own_interval[1], interval["upper"])
        if own_interval is not None:
            number("hc3_multiplier", where, 1.959963984540054, interval["normal_multiplier"])
    if reference:
        equal("reference_sd_inventory", label, sorted(ours["reference_sample_sd"]), sorted(theirs["metric_denominators"]))
        for outcome, sd in ours["reference_sample_sd"].items():
            other = theirs["metric_denominators"][outcome]
            number("reference_sample_sd", label + "/" + outcome, sd, other["sample_sd"])
            equal("reference_sd_ddof", label + "/" + outcome, 1, other["ddof"])
            equal("reference_sd_sample_sizes", label + "/" + outcome, n, other["n"])
    else:
        equal("no_generated_sd", label, {}, theirs["metric_denominators"])


def compare_discrepancy(label, own, other, anchor=False):
    fields = {"reference": "reference_estimate", "generated": "generated_estimate",
              "signed_difference": "signed_raw_discrepancy", "absolute_difference": "absolute_raw_discrepancy",
              "denominator": "reference_denominator", "scaled_discrepancy": "normalized_discrepancy"}
    for a, b in fields.items():
        number("zero_anchor_numbers" if anchor else "discrepancy_numbers", label + "/" + a, own[a], other[b])
    own_direction = None if own["reference_direction"] is None or own["generated_direction"] is None else own["reference_direction"] == own["generated_direction"]
    equal("directions", label, own_direction, other["direction_agrees"])
    for margin, passed in own["pass_grid"].items():
        equal("zero_anchor_grid" if anchor else "endpoint_grid", label + "/" + margin, passed, other["passes"][margin])


def main():
    if sha(INDEPENDENT) != EXPECTED_INDEPENDENT:
        raise ValueError("Independent report does not match its pre-production commitment")
    if sha(PRODUCTION) != EXPECTED_PRODUCTION:
        raise ValueError("Production file does not match the coordinator's completion hash")
    commitment = load(HERE / "INDEPENDENT_WAVE_A_RESULTS_COMMITMENT.json")
    if commitment["report_sha256"] != EXPECTED_INDEPENDENT or commitment["production_results_read"] is not False:
        raise ValueError("Independent committed-first receipt differs")
    independent, production = load(INDEPENDENT), load(PRODUCTION)
    equal("inventory", "reference_cases", sorted(independent["references"]), sorted(production["references"]))
    for case, ours in independent["references"].items():
        compare_analysis(case + "/reference", ours, production["references"][case], True)
    own_slots = {s["report_slot_id"]: s for s in independent["report_slots"]}
    production_slots = {s["report_id"]: s for s in production["target_slots"]}
    equal("inventory", "report_slot_ids", sorted(own_slots), sorted(production_slots))
    equal("inventory", "report_slot_count", independent["report_slot_count"], len(production["target_slots"]))
    equal("inventory", "alias_slot_count", independent["alias_slot_count"], sum(s["alias_of"] is not None for s in production_slots.values()))
    equal("inventory", "unique_target_outputs", independent["unique_target_output_count"], len({s["verified_trial"]["trial_id"] for s in production_slots.values()}))
    for report_id, ours in own_slots.items():
        other = production_slots[report_id]
        for field in ("case", "constructor", "stage", "seed", "alias_of"):
            equal("slot_identity", report_id + "/" + field, ours[field], other[field])
        equal("stage_accounting", report_id, ours["whole_stage_pass"], other["stage_verified_success"])
        for own_key, production_key in (("actual_trial_id", "trial_id"), ("table_sha256", "generated_table_sha256"),
                                         ("generation_link_verified", "generation_link_verified"), ("trial_status", "status")):
            equal("slot_provenance", report_id + "/" + own_key, ours[own_key], other["verified_trial"][production_key])
        analysis = independent["unique_target_analyses"][ours["analysis_key"]]["analysis"]
        compare_analysis(report_id, analysis, other["analysis"], False)
        for endpoint, comparison in ours["comparisons"].items():
            compare_discrepancy(report_id + "/" + endpoint, comparison, other["comparison"][endpoint])
        for margin, passed in ours["pass_grid"].items():
            production_pass = bool(other["stage_verified_success"] and other["verified_trial"]["status"] == "success"
                                   and all(c["passes"][margin] for c in other["comparison"].values()))
            equal("slot_grid", report_id + "/" + margin, passed, production_pass)
    aggregate = production["aggregate"]
    equal("inventory", "constructor_bundles", len(independent["constructor_bundles"]), len(aggregate["bundles"]))
    for ours in independent["constructor_bundles"]:
        key = f'{ours["case"]}:{ours["constructor"]}:{ours["stage"]}'
        other = aggregate["bundles"][key]
        for margin, passed in ours["pass_grid"].items():
            equal("constructor_grid", key + "/" + margin, passed, other["passes"][margin])
        group = [s for s in own_slots.values() if (s["case"], s["constructor"], s["stage"]) == (ours["case"], ours["constructor"], ours["stage"])]
        equal("constructor_stage_success", key, all(s["whole_stage_pass"] for s in group), other["whole_stage_verified_success"])
        failed = sum(not(s["whole_stage_pass"] and s["trial_status"] == "success" and all(c["scaled_discrepancy"] is not None for c in s["comparisons"].values())) for s in group)
        equal("constructor_failure_count", key, failed, other["failed_or_unavailable_seed_count"])
    for case, ours in independent["case_results"].items():
        for stage, margins in ours["reliability"].items():
            other = aggregate["cases"][case + ":" + stage]
            equal("case_denominator", case + ":" + stage, 5, other["agent_denominator"])
            s01 = next(b for b in independent["constructor_bundles"] if (b["case"], b["constructor"], b["stage"]) == (case, "S01", stage))
            for margin, values in margins.items():
                equal("case_counts", case + "/" + stage + "/" + margin, values["passing_agents"], other["agent_pass_counts"][margin])
                equal("case_grid", case + "/" + stage + "/" + margin, values["reliability_pass"], other["reliability_pass"][margin])
                equal("statistical_reference_grid", case + "/" + stage + "/" + margin, s01["pass_grid"][margin], other["statistical_reference_pass"][margin])
        anchor = aggregate["zero_anchors"][case]
        equal("zero_anchor_gates", case + "/discriminating", ours["discriminating"], anchor["discriminating"])
        equal("zero_anchor_gates", case + "/insufficient", ours["zero_all_within_working_resolution"], anchor["insufficient_discrimination"])
        equal("zero_anchor_gates", case + "/defined", all(e["scaled_discrepancy"] is not None for e in ours["zero_anchors"].values()), anchor["defined"])
        for endpoint, comparison in ours["zero_anchors"].items():
            compare_discrepancy(case + "/anchor/" + endpoint, comparison, anchor["endpoints"][endpoint], True)
    equal("paired_inventory", "paired_seed_count", 36, len(aggregate["initial_final_paired"]))
    for pair in aggregate["initial_final_paired"]:
        prefix = f'{pair["case"]}_{pair["constructor"]}'
        seed = pair["seed"]
        initial = own_slots[f"{prefix}_initial_target_{seed}"]
        final = own_slots[f"{prefix}_final_target_{seed}"]
        equal("paired_retention", prefix + "/" + str(seed), final["alias_of"] is not None, pair["retained_alias"])
        for endpoint, reported in pair["endpoints"].items():
            a, b = initial["comparisons"][endpoint], final["comparisons"][endpoint]
            number("paired_changes", prefix + "/" + str(seed) + "/" + endpoint + "/effect", b["generated"] - a["generated"], reported["effect_change"])
            number("paired_changes", prefix + "/" + str(seed) + "/" + endpoint + "/error_reduction", a["scaled_discrepancy"] - b["scaled_discrepancy"], reported["normalized_error_reduction"])
    equal("global_gate", "positive_wave_a", independent["positive_wave_a_gate"], aggregate["positive_wave_a_scientific_gate"])
    equal("global_gate", "wave_b_execution", independent["wave_b_automatic_execution"], aggregate["wave_b_execution_authorized"])
    equal("grid_contract", "working_resolution", independent["working_resolution"], aggregate["working_resolution"])
    equal("grid_contract", "full_grid", independent["sensitivity_grid"], aggregate["full_resolution_grid"])
    failures = [c for c in checks if not c["pass"]]
    maxima = {}
    for check in checks:
        if check["absolute_difference"] is not None:
            key = check["category"]
            maxima[key] = max(maxima.get(key, 0.0), check["absolute_difference"])
    report = {
        "kind": "committed_independent_vs_production_comparison",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "independent_report_path": str(INDEPENDENT), "independent_report_sha256": EXPECTED_INDEPENDENT,
        "independent_committed_utc": commitment["created_utc"],
        "production_report_path": str(PRODUCTION), "production_report_sha256": EXPECTED_PRODUCTION,
        "comparison_script_sha256": sha(__file__), "raw_tables_read_by_comparator": False,
        "production_mathematics_read_or_imported": False,
        "numerical_tolerance": {"absolute": ATOL, "relative": RTOL, "decisions": "exact"},
        "pass": not failures, "check_count": len(checks), "failure_count": len(failures),
        "checks_by_category": dict(sorted(Counter(c["category"] for c in checks).items())),
        "maximum_absolute_differences_by_category": maxima,
        "comparison_scope": {"references": 2, "reference_points": 6, "unique_generated_tables": 36,
                             "generated_report_slots": 72, "generated_endpoint_slots": 216,
                             "constructor_stage_bundles": 24, "sensitivity_margins": 4},
        "schema_note": "Independent nonfinite counts are per-variable; production reports a union missing_numeric and union infinite_numeric. Equivalent age/sex/nonpositive reasons and total input/eligible/excluded counts are compared exactly; per-variable counts are retained independently, not falsely summed across overlaps.",
        "failures": failures, "checks": checks}
    output = HERE / "INDEPENDENT_PRODUCTION_COMPARISON.json"
    with output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")
    receipt = {"path": str(output), "sha256": sha(output), "pass": not failures,
               "check_count": len(checks), "failure_count": len(failures),
               "maximum_absolute_differences_by_category": maxima}
    with (HERE / "COMPARISON_RECEIPT.json").open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(receipt, handle, indent=2)
        handle.write("\n")
    print(json.dumps(receipt))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
