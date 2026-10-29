"""One-off independent aggregate/receipt audit; never read generated row tables."""
from pathlib import Path
from datetime import datetime
import csv
import hashlib
import json
import math
import statistics

E = Path(__file__).resolve().parent.parent
P = E.parents[1]
checks = {}
hash_count = 0


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check(name, value):
    checks[name] = bool(value)


def bound(path, expected):
    global hash_count
    hash_count += 1
    if sha(path) != expected:
        raise AssertionError(f"Hash mismatch: {path}")


def close(a, b):
    return math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12)


def stamp(value):
    return datetime.fromisoformat(value)


protocol = read(E / "protocol_commitment.json")
source_commit = read(E / "source_commitment.json")
complete_commit = read(E / "evaluation_commitment.json")
authorization = read(E / "probe_authorization.json")
source = read(E / "source_analysis/aggregate_report.json")
complete = read(E / "results/aggregate_report.json")
gate = read(E / "analysis/frozen_gate.json")

for relative, expected in protocol["files"].items():
    bound(E / relative, expected)
for relative, expected in protocol["core_files"].items():
    bound(P / relative, expected)
bound(P / "work/m2-runtime-config.json", protocol["runtime_config_sha256"])
for label, expected in protocol["candidate_freezes"].items():
    bound(E / f"agent_bundle/candidates/{label}/freeze.json", expected)
for manifest in (source_commit, complete_commit):
    bound(E / "protocol_commitment.json", manifest["protocol_commitment_sha256"])
    for record in manifest["candidates"]:
        directory = Path(record["path"])
        for filename, key in (("freeze.json", "freeze_sha256"), ("generator.py", "generator_sha256"),
                              ("model_spec.json", "model_spec_sha256"), ("analytic_certificate.json", "analytic_certificate_sha256")):
            bound(directory / filename, record[key])
for directory in (E / "source_analysis", E / "results"):
    for relative, expected in read(directory / "artifact_hashes.json").items():
        bound(directory / relative, expected)
bound(E / "source_commitment.json", source["manifest_sha256"])
bound(E / "evaluation_commitment.json", complete["manifest_sha256"])
bound(E / "source_commitment.json", authorization["source_commitment_sha256"])
bound(E / "source_analysis/gate_summary.json", authorization["source_gate_result_sha256"])

source_logs, probe_logs = [], []
source_receipts = []
for label in ("zero", "minus", "plus"):
    freeze = read(E / f"agent_bundle/candidates/{label}/freeze.json")
    check(f"{label}_freeze_precedes_protocol", stamp(freeze["created_utc"]) < stamp(protocol["created_utc"]))
    for seed in (78101, 78102, 78103):
        rid = f"{label}_{seed}"
        log = read(E / f"controller_logs/{rid}.json")
        source_logs.append(log)
        report_path = E / f"agent_bundle/source_replays/{rid}/replay.json"
        report = read(report_path)
        source_receipts.append(report)
        check(f"{rid}_receipt", report["status"] == "success" and report["limits"]["seed"] == seed
              and report["parent"]["candidate"] == f"candidates/{label}"
              and report["parent"]["freeze.json_sha256"] == protocol["candidate_freezes"][label])
        check(f"{rid}_contexts", len(report["contexts"]) == 2 and {c["id"] for c in report["contexts"]} == {"oh", "bansal"}
              and all(c["generation_link_verified"] and c["status"] == "success" for c in report["contexts"]))
        for context in report["contexts"]:
            matching = [r for r in source_commit["sources"] if r["label"] == label and r["seed"] == seed and r["context"] == context["id"]]
            check(f"{rid}_{context['id']}_binding", len(matching) == 1 and matching[0]["sha256"] == context["generated_sha256"])
            bound(report_path, matching[0]["replay_report_sha256"])
            child_receipt = E / f"agent_bundle/source_replays/{rid}/contexts/{context['id']}/bundle/executions/replay/execution.json"
            bound(child_receipt, context["execution_sha256"])
            child = read(child_receipt)
            check(f"{rid}_{context['id']}_execution", child["status"] == "success" and child["limits"]["seed"] == seed
                  and child["generator_executed"] is True)
    for seed in (78201, 78202, 78203):
        rid = f"{label}_{seed}"
        log = read(E / f"controller_logs/{rid}.json")
        probe_logs.append(log)
        receipt = read(E / f"agent_bundle/executions/{rid}/execution.json")
        check(f"{rid}_execution", receipt["status"] == "success" and receipt["limits"]["seed"] == seed
              and receipt["candidate"] == f"candidates/{label}" and receipt["generator_executed"] is True)
check("all_controller_returncodes_zero", all(log["returncode"] == 0 for log in source_logs + probe_logs))
check("protocol_precedes_all_source_runs", stamp(protocol["created_utc"]) < min(stamp(l["started_utc"]) for l in source_logs))
check("all_source_runs_precede_source_commitment", max(stamp(l["ended_utc"]) for l in source_logs) < stamp(source_commit["created_utc"]))
check("source_commitment_precedes_probe_authorization", stamp(source_commit["created_utc"]) < stamp(authorization["created_utc"]))
check("authorization_precedes_all_probe_runs", stamp(authorization["created_utc"]) < min(stamp(l["started_utc"]) for l in probe_logs))
check("all_probe_runs_precede_complete_commitment", max(stamp(l["ended_utc"]) for l in probe_logs) < stamp(complete_commit["created_utc"]))
check("source_commitment_no_probe_outputs", source_commit["probes"] == [] and source_commit["authorize_probe_analysis"] is False)
check("complete_commitment_nine_probe_outputs", len(complete_commit["probes"]) == 9 and complete_commit["authorize_probe_analysis"] is True)

for key in ("source_checks", "source_check_summary", "source_input_preservation", "source_paired_invariants",
            "fixed_source_context_departure", "fixed_source_context_region_departure", "fixed_source_context_conditional_departure",
            "oh_table2_both_interpretations", "oh_table2_summary", "independent_analytic_certificate", "gate"):
    check(f"source_phase_unchanged_{key}", source[key] == complete[key])

thresholds = {c["check_id"]: c for c in gate["checks"]}
portfolio_values = {}
for record in source_commit["portfolios"]:
    bound(record["path"], record["sha256"])
    portfolio = read(record["path"])
    for item in portfolio["checks"]:
        for run in item["runs"]:
            portfolio_values[(record["label"], run["seed"], item["definition"]["check_id"])] = run["value"]
rows = source["source_checks"]
unique = {(r["label"], r["seed"], r["check_id"]) for r in rows}
check("source_414_unique_records", len(rows) == len(unique) == 414)
numeric_ok = True
for row in rows:
    value = portfolio_values[(row["label"], row["seed"], row["check_id"])]
    zero = portfolio_values[("zero", row["seed"], row["check_id"])]
    threshold = thresholds[row["check_id"]]
    change = value - zero
    numeric_ok &= row["value"] == value and row["paired_change_vs_zero"] == change
    numeric_ok &= row["paired_absolute_limit"] == threshold["paired_absolute_limit"] == 3 * threshold["historical_generator_seed_draw_sd"]
    numeric_ok &= row["gate_pass"] == (abs(change) <= threshold["paired_absolute_limit"])
    numeric_ok &= close(row["signed_discrepancy"], value - threshold["reported_value"])
check("source_values_pairs_limits_pass_flags_recomputed", numeric_ok)
alternatives = [r for r in rows if r["label"] != "zero"]
exact = [r for r in alternatives if r["exact_invariant_pass"] is not None]
check("all_276_alternative_comparisons_pass", len(alternatives) == 276 and all(r["gate_pass"] for r in alternatives))
check("252_exact_invariant_comparisons", len(exact) == 252 and all(r["exact_invariant_pass"] and r["paired_change_vs_zero"] == 0 for r in exact))
check("18_source_input_and12_paired_sets_pass", len(source["source_input_preservation"]) == 18 and len(source["source_paired_invariants"]) == 12
      and all(r["passed"] for r in source["source_input_preservation"] + source["source_paired_invariants"]))
ratios = [{"label": r["label"], "seed": r["seed"], "check_id": r["check_id"],
           "ratio": abs(r["paired_change_vs_zero"]) / r["paired_absolute_limit"]}
          for r in alternatives if r["paired_absolute_limit"] > 0]
semantic = source["oh_table2_both_interpretations"]
skeys = lambda r: (r["seed"], r["variable"], r["sex"], r["reported_stratum"], r["interpretation"])
sref = {skeys(r): r["value"] for r in semantic if r["label"] == "zero"}
check("360_semantic_records_and_pairs", len(semantic) == 360 and len({(r["label"], *skeys(r)) for r in semantic}) == 360
      and all(math.isfinite(r["value"]) and r["n"] > 0 and close(r["paired_change_vs_zero"], r["value"] - sref[skeys(r)]) for r in semantic))

probe = complete["probe"]
check("9_probe_preservation_and6_paired_sets_pass", len(probe["preservation"]) == 9 and len(probe["paired_invariants"]) == 6
      and all(r["passed"] for r in probe["preservation"] + probe["paired_invariants"]))
for key, expected_count, dimension in (("endpoints", 63, "endpoint"), ("blocks", 36, "block")):
    items = probe[key]
    ref = {(r["seed"], r[dimension]): r["value"] for r in items if r["label"] == "zero"}
    check(f"probe_{key}_counts_unique_pairs", len(items) == expected_count
          and len({(r["label"], r["seed"], r[dimension]) for r in items}) == expected_count
          and all(close(r["paired_change_vs_zero"], r["value"] - ref[(r["seed"], r[dimension])]) for r in items))
    summaries = probe["endpoint_summary" if key == "endpoints" else "block_summary"]
    check(f"probe_{key}_summary_means", all(close(r["mean"], statistics.mean(i["value"] for i in items if i["label"] == r["label"] and i[dimension] == r[dimension])) for r in summaries))
check("all_block_sizes200", all(r["n"] == 200 for r in probe["blocks"]))
check("12_block_plus_minus_differences", len(probe["block_plus_minus_gaps"]) == 12
      and all(close(r["paired_plus_minus_gap"], r["value_plus"] - r["value_minus"]) for r in probe["block_plus_minus_gaps"]))
with (E / "results/probe_grid.csv").open(newline="", encoding="utf-8") as stream:
    grid = list(csv.DictReader(stream))
check("24840_aggregate_grid_cells", len(grid) == 24840 and len({(r["label"], r["seed"], r["sex"], r["age"], r["bmi"]) for r in grid}) == 24840
      and all(int(r["n"]) == 10 for r in grid))

newzero_ratios = [{"check_id": r["check_id"], "new_zero_sd": r["generator_seed_draw_sd"],
                   "historical_sd": thresholds[r["check_id"]]["historical_generator_seed_draw_sd"],
                   "new_to_historical_ratio": r["generator_seed_draw_sd"] / thresholds[r["check_id"]]["historical_generator_seed_draw_sd"]}
                  for r in source["source_check_summary"] if r["label"] == "zero" and thresholds[r["check_id"]]["historical_generator_seed_draw_sd"] > 0]
worst_semantic = {kind: max((r for r in semantic if r["label"] == "zero" and r["interpretation"] == kind), key=lambda r: r["absolute_discrepancy"])
                  for kind in ("arithmetic", "geometric")}
result = {"status": "passed" if all(checks.values()) else "blocked", "checks": checks, "hash_comparisons": hash_count,
          "scope": "Independent aggregate arithmetic, receipt metadata and hashes; no generated participant/source/probe row table opened and no generator execution",
          "script_sha256": sha(__file__), "protocol_commitment_sha256": sha(E / "protocol_commitment.json"),
          "source_commitment_sha256": sha(E / "source_commitment.json"), "evaluation_commitment_sha256": sha(E / "evaluation_commitment.json"),
          "source_aggregate_sha256": sha(E / "source_analysis/aggregate_report.json"), "complete_aggregate_sha256": sha(E / "results/aggregate_report.json"),
          "max_paired_gate_ratio": max(ratios, key=lambda r: r["ratio"]),
          "nonzero_source_changes": sum(r["paired_change_vs_zero"] != 0 for r in alternatives),
          "maximum_table2_paired_drift_mg_dl": max(abs(r["paired_change_vs_zero"]) for r in semantic),
          "worst_zero_table2_discrepancy_by_interpretation": worst_semantic,
          "largest_new_zero_to_historical_seed_sd_ratios": sorted(newzero_ratios, key=lambda r: r["new_to_historical_ratio"], reverse=True)[:5],
          "summary_arithmetic_tolerance": "1e-12 relative/absolute only for independent elementary summary recomputation; scientific gate comparisons retain their exact frozen thresholds",
          "chronology": {"protocol_utc": protocol["created_utc"], "first_source_start_utc": min(l["started_utc"] for l in source_logs),
                         "source_commitment_utc": source_commit["created_utc"], "probe_authorization_utc": authorization["created_utc"],
                         "first_probe_start_utc": min(l["started_utc"] for l in probe_logs), "evaluation_commitment_utc": complete_commit["created_utc"]}}
out = E / "review/POSTRUN_CHECKS.json"
with out.open("x", encoding="utf-8") as stream:
    json.dump(result, stream, indent=2, allow_nan=False)
    stream.write("\n")
print(json.dumps({"status": result["status"], "checks": len(checks), "failures": [k for k,v in checks.items() if not v],
                  "hash_comparisons": hash_count, "report_sha256": sha(out)}))
