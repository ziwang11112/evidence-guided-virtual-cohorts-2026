"""Independent postclosure saved-CSV audit; aggregate output only, no generation."""
from pathlib import Path
import csv
import hashlib
import json
import math

HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def table(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    require(all(set(row) == {"id", "age", "sex", "bmi", "total_cholesterol", "hdl_cholesterol"} for row in rows), "Unexpected table schema")
    require(len({row["id"] for row in rows}) == len(rows), "Duplicate IDs")
    return rows


def coherence(rows):
    missing = nonfinite = violating = equal = nonpositive = 0
    excesses = []
    for row in rows:
        raw = (row["total_cholesterol"], row["hdl_cholesterol"])
        if any(value.strip() == "" for value in raw):
            missing += 1
            continue
        total, hdl = map(float, raw)
        if not (math.isfinite(total) and math.isfinite(hdl)):
            nonfinite += 1
            continue
        nonpositive += int(total <= 0 or hdl <= 0)
        equal += int(total == hdl)
        violating += int(hdl > total)
        excesses.append(max(hdl - total, 0.0))
    evaluated = len(excesses)
    return {
        "n_total": len(rows), "n_evaluated": evaluated,
        "n_missing": missing, "n_nonfinite": nonfinite,
        "n_unknown": missing + nonfinite, "n_nonpositive_pairs": nonpositive,
        "n_violating": violating, "n_satisfying": evaluated - violating,
        "violation_fraction_evaluated": violating / evaluated if evaluated else None,
        "max_violation": max(excesses) if evaluated else None,
        "n_equal_TC_HDL": equal,
    }


def pair_audit(before, after, seed):
    before_by_id = {row["id"]: row for row in before}
    after_by_id = {row["id"]: row for row in after}
    require(before_by_id.keys() == after_by_id.keys(), "Baseline/revision ID sets differ")
    nonlipid_changes = {key: 0 for key in ["age", "sex", "bmi"]}
    changed_pairs = changed_total = changed_hdl = changed_nonviolations = 0
    baseline_violations = changed_violations = midpoint_exact_mismatches = 0
    max_midpoint_error = max_pair_sum_error = 0.0
    boundary = baseline_boundary = new_boundary = 0
    for identifier, row in before_by_id.items():
        revised = after_by_id[identifier]
        for key in nonlipid_changes:
            nonlipid_changes[key] += int(row[key] != revised[key])
        total, hdl = float(row["total_cholesterol"]), float(row["hdl_cholesterol"])
        new_total, new_hdl = float(revised["total_cholesterol"]), float(revised["hdl_cholesterol"])
        require(all(math.isfinite(x) and x > 0 for x in (total, hdl, new_total, new_hdl)), "Nonpositive/nonfinite lipid value")
        changed = total != new_total or hdl != new_hdl
        changed_pairs += int(changed)
        changed_total += int(total != new_total)
        changed_hdl += int(hdl != new_hdl)
        violates = hdl > total
        baseline_violations += int(violates)
        changed_violations += int(violates and changed)
        changed_nonviolations += int(not violates and changed)
        baseline_boundary += int(total == hdl)
        boundary += int(new_total == new_hdl)
        new_boundary += int(total != hdl and new_total == new_hdl)
        if violates:
            midpoint = (total + hdl) / 2.0
            max_midpoint_error = max(max_midpoint_error, abs(new_total - midpoint), abs(new_hdl - midpoint))
            midpoint_exact_mismatches += int(new_total != midpoint or new_hdl != midpoint)
        max_pair_sum_error = max(max_pair_sum_error, abs((total + hdl) - (new_total + new_hdl)))
    require(not any(nonlipid_changes.values()), "A nonlipid field changed")
    require(changed_nonviolations == 0 and changed_violations == baseline_violations == changed_pairs, "Changed-pair support differs from original violations")
    require(midpoint_exact_mismatches == 0, "Saved projected values differ from the declared midpoint algorithm")
    require(boundary == baseline_boundary + baseline_violations, "Unexpected equality-boundary count")
    return {
        "seed": seed, "n_matched_ids": len(before), "id_sets_identical": True,
        "id_order_identical": [r["id"] for r in before] == [r["id"] for r in after],
        "unchanged_nonlipid_fields_checked_as_saved_text": list(nonlipid_changes),
        "nonlipid_changed_rows_by_field": nonlipid_changes,
        "n_changed_lipid_pairs": changed_pairs, "n_changed_TC": changed_total,
        "n_changed_HDL": changed_hdl, "n_original_violations": baseline_violations,
        "n_original_violations_changed": changed_violations,
        "n_original_nonviolations_changed": changed_nonviolations,
        "n_midpoint_exact_mismatches": midpoint_exact_mismatches,
        "max_midpoint_absolute_error_mmol_L": max_midpoint_error,
        "max_pair_sum_absolute_error_mmol_L": max_pair_sum_error,
        "baseline_equality_count": baseline_boundary,
        "revision_equality_count": boundary,
        "new_equality_count": new_boundary,
    }


def main():
    closed = read(HERE / "AUTHOR_CLOSED.json")
    require(closed["status"] == "author_finished_no_further_revision", "Author closure required")
    bundle = Path(closed["bundle"])
    actual_files = {str(p.relative_to(bundle)).replace("\\", "/") for p in bundle.rglob("*") if p.is_file()}
    require(actual_files == set(closed["files"]), "Closed file inventory changed")
    require(all(sha(bundle / name) == digest for name, digest in closed["files"].items()), "A closed bundle file changed")
    evaluation = read(HERE / "EVALUATION.json")
    require(evaluation["closure_sha256"] == sha(HERE / "AUTHOR_CLOSED.json"), "Evaluation closure binding changed")
    require(evaluation["protocol_sha256"] == sha(HERE / "PROTOCOL.json"), "Evaluation protocol binding changed")
    require(evaluation["reference_read"] is False, "Unexpected reference comparison")
    require(closed["final_candidate"] == "candidates/coherent_projection", "Unexpected final selection")
    expected = {(candidate, seed) for candidate in ("candidates/baseline", "candidates/coherent_projection") for seed in (9601, 9602, 9603)}
    require({(r["candidate"], r["seed"]) for r in evaluation["runs"]} == expected and len(evaluation["runs"]) == 6, "Run coverage mismatch")
    runs = []
    tables = {}
    for record in evaluation["runs"]:
        run_id = record["run_id"]
        folder = bundle / "executions" / run_id
        receipt = read(folder / "execution.json")
        output = folder / "output/generated.csv"
        require(receipt["status"] == record["status"] == "success", "Unsuccessful run")
        require(receipt["candidate"] == record["candidate"] and receipt["limits"]["seed"] == record["seed"], "Receipt stage/seed mismatch")
        require(sha(output) == record["output_sha256"] == receipt["files"]["output/generated.csv"], "Output binding mismatch")
        rows = table(output)
        require(len(rows) == 3000, "Unexpected row count")
        calculated = coherence(rows)
        reported = record["coherence"][0]
        for key in ["n_total", "n_evaluated", "n_missing", "n_nonfinite", "n_unknown", "n_violating", "n_satisfying"]:
            require(calculated[key] == reported[key], "Coherence count mismatch: " + key)
        require(math.isclose(calculated["max_violation"], reported["max_violation"], rel_tol=0, abs_tol=1e-12), "Coherence excess mismatch")
        require(calculated["violation_fraction_evaluated"] == reported["violation_fraction_evaluated"], "Coherence fraction mismatch")
        require(calculated["n_unknown"] == calculated["n_nonpositive_pairs"] == 0, "Ineligible lipid pairs")
        tables[(record["candidate"], record["seed"])] = rows
        runs.append({"run_id": run_id, "candidate": record["candidate"], "seed": record["seed"], "output_sha256": sha(output), "execution_receipt_sha256": sha(folder / "execution.json"), **calculated, "matches_evaluation_counts": True, "max_excess_absolute_difference_from_evaluation": abs(calculated["max_violation"] - reported["max_violation"])})
    pairs = [pair_audit(tables[("candidates/baseline", seed)], tables[("candidates/coherent_projection", seed)], seed) for seed in (9601, 9602, 9603)]
    totals = []
    for candidate in ("candidates/baseline", "candidates/coherent_projection"):
        subset = [r for r in runs if r["candidate"] == candidate]
        evaluated = sum(r["n_evaluated"] for r in subset)
        violating = sum(r["n_violating"] for r in subset)
        totals.append({"candidate": candidate, "runs": len(subset), "n_evaluated": evaluated, "n_violating": violating, "violation_fraction_evaluated": violating / evaluated, "max_violation_mmol_L": max(r["max_violation"] for r in subset), "n_equal_TC_HDL": sum(r["n_equal_TC_HDL"] for r in subset)})
    result = {
        "schema": "independent_coherence_recomputation_v1", "status": "passed",
        "scope": "Postclosure saved-CSV audit. No generator calls, new draws, target reads or individual values in this artifact.",
        "method": "Python csv reader and float arithmetic, independent of the analysis adapter; pair comparison by artificial ID within each preset seed.",
        "binding": {"bundle": str(bundle), "closure_sha256": sha(HERE / "AUTHOR_CLOSED.json"), "evaluation_sha256": sha(HERE / "EVALUATION.json"), "protocol_sha256": sha(HERE / "PROTOCOL.json"), "script_sha256": sha(Path(__file__)), "closed_files_verified": len(closed["files"]), "closed_inventory_unchanged": True, "final_candidate": closed["final_candidate"]},
        "rule": {"left": "hdl_cholesterol", "right": "total_cholesterol", "unit": "mmol/L", "tolerance": 0.0, "interpretation": "Underlying same-specimen concentrations; no separate assay-error model."},
        "recomputation_agreement_tolerance": {"max_excess_absolute_mmol_L": 1e-12, "meaning": "Floating-point audit agreement only; does not change the zero-tolerance component rule."},
        "runs": runs, "stage_totals": totals, "paired_seed_checks": pairs,
        "support_vs_observation": {"observed": "All six saved outputs and all three paired comparisons audited; counts describe these finite synthetic outputs only.", "construction": "For finite positive proposals, unchanged H<=T pairs satisfy the rule; assigning the same finite midpoint to both components when H>T enforces equality. This code-level support argument is separate from the finite counts and does not guarantee every other validity property or successful finite arithmetic for arbitrary inputs."},
        "limitations": ["Projection creates an artificial zero-nonHDL atom; its probability and biological plausibility are not source-validated.", "Equal-weight Euclidean metric is an author assumption, not assay precision.", "Lipid distributions and requested associations can change; constraint satisfaction does not show collateral preservation or overall improvement.", "No clinical validity, target accuracy, population recovery or general efficacy claim follows."]
    }
    (HERE / "COHERENCE_RECOMPUTATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "stage_totals": totals, "pair_checks": pairs}, indent=2))


if __name__ == "__main__":
    main()
