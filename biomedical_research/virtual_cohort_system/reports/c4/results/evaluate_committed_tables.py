"""Post-reveal adapter: verify commitments and call the unchanged custodian evaluator.

Reads only already-generated tables. Never imports or executes candidate programs.
Reports every scheduled slot, while keeping content duplication explicit.
"""
import csv
import hashlib
import importlib.util
import json
import math
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
R = Path(__file__).resolve().parents[1]
OUT = R / "results"
GATE_HASH = "bea5626274935be637964e38e4cd971152fe0c69df9e04e2f0df24fe5272e2f1"
POLICIES = ["retain_initial", "minloss", "protected_gate"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")


def write_csv(path, rows):
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def average(values):
    return math.fsum(values) / len(values)


def main():
    OUT.mkdir(exist_ok=True)
    gate = read(R / "REVEAL_GATE.json")
    assert sha(R / "REVEAL_GATE.json") == GATE_HASH
    assert gate["decision"] == "reveal_and_evaluate" and gate["all_test_outputs_committed"]
    assert not gate["author_may_receive_hidden_feedback"] and not gate["generation_or_revision_allowed"]
    bound = {
        "TASK_COMMITMENT.json": gate["task_commitment_sha256"],
        "TEST_OUTPUT_MANIFEST.json": gate["test_outputs_manifest_sha256"],
        "test_COMPLETED.json": gate["test_completed_receipt_sha256"],
        "method/selection.json": gate["selection_sha256"],
    }
    for path, expected in bound.items():
        assert sha(R / path) == expected, path
    commitment = read(R / "TASK_COMMITMENT.json")
    for path, expected in dict(commitment["hidden_artifacts"], **commitment["visible_artifacts"]).items():
        assert sha(R / path) == expected, path
    assert sha(R / "TASK_ADMISSION.md") == commitment["admission_document_sha256"]
    manifest = read(R / "TEST_OUTPUT_MANIFEST.json")
    seal = R / "method" / "selection.json"
    selection = read(seal)
    test_gate = read(R / "TEST_GATE.json")
    assert test_gate["selection_sha256"] == sha(seal)
    assert manifest["selection_sha256"] == sha(seal)
    assert len(manifest["entries"]) == 24
    assert len({entry["table_sha256"] for entry in manifest["entries"]}) == 6
    expected_slots = {(case, index, seed) for case in ("task_a", "task_b")
                      for index in range(4) for seed in commitment["seeds"]["untouched_test"]}
    assert {(v["case"], v["candidate_index"], v["seed"]) for v in manifest["entries"]} == expected_slots
    for entry in manifest["entries"]:
        for kind in ("table", "diagnostic"):
            assert sha(R / entry[f"{kind}_path"]) == entry[f"{kind}_sha256"], entry[f"{kind}_path"]
    module_spec = importlib.util.spec_from_file_location("c4_original_hidden_evaluator", R / "custody" / "evaluate.py")
    evaluator = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(evaluator)
    full_rows, policy_rows, raw_manifests = [], [], []
    for entry in manifest["entries"]:
        result = evaluator.evaluate(R / entry["table_path"], entry["case"], seal)
        assert result["status"] == "ok", entry["table_path"]
        assert result["table_sha256"] == entry["table_sha256"]
        assert result["evaluator_sha256"] == commitment["hidden_artifacts"]["custody/evaluate.py"]
        assert result["evaluation_contract_sha256"] == commitment["hidden_artifacts"]["custody/evaluate_contract.json"]
        result["slot"] = {k: entry[k] for k in ("case", "candidate", "candidate_index", "seed", "selected_by")}
        name = f"evaluation_{entry['case']}_{entry['candidate']}_{entry['seed']}.json"
        write_json(OUT / name, result)
        raw_manifests.append({"path": f"results/{name}", "sha256": sha(OUT / name), "table_sha256": entry["table_sha256"]})
        diagnostic = read(R / entry["diagnostic_path"])
        assert diagnostic["table_sha256"] == entry["table_sha256"]
        assert diagnostic["status"] == "success"
        for world, endpoints in result["worlds"].items():
            for endpoint, metrics in endpoints.items():
                row = {"case": entry["case"], "candidate": entry["candidate"],
                       "candidate_index": entry["candidate_index"], "seed": entry["seed"],
                       "world": world, "endpoint": endpoint,
                       "estimate": metrics["estimate"], "truth": metrics["truth"],
                       "signed_error": metrics["signed_error"], "absolute_error": metrics["absolute_error"],
                       "squared_error": metrics["squared_error"],
                       "estimated_direction": metrics["estimated_direction"], "truth_direction": metrics["truth_direction"],
                       "direction_matches": metrics["direction_matches"],
                       "engineering_fidelity_band": metrics.get("engineering_fidelity_band", "not_prespecified_for_secondary"),
                       "numerical_utility_score": metrics.get("numerical_utility_score", ""),
                       "test_source_numeric_pass": diagnostic["numeric_pass"],
                       "test_source_protected_pass": diagnostic["protected_pass"],
                       "test_source_loss": diagnostic["full_source_error"],
                       "selected_by": "|".join(entry["selected_by"]),
                       "table_sha256": entry["table_sha256"], "table_path": entry["table_path"]}
                full_rows.append(row)
                for policy in POLICIES:
                    if selection["cases"][entry["case"]][policy] == entry["candidate_index"]:
                        policy_rows.append({"policy": policy, **row})
    write_csv(OUT / "all_table_endpoints.csv", full_rows)
    write_csv(OUT / "selected_policy_endpoints.csv", policy_rows)
    aggregates = []
    grouped = defaultdict(list)
    for row in policy_rows:
        grouped[(row["case"], row["policy"], row["world"], row["endpoint"])].append(row)
    for key, rows in grouped.items():
        case, policy, world, endpoint = key
        assert len(rows) == 3 and len({r["table_sha256"] for r in rows}) == 3
        primary = endpoint == "adjusted_x_coefficient"
        aggregates.append({"case": case, "policy": policy, "selected_candidate": rows[0]["candidate"],
                           "world": world, "endpoint": endpoint, "distinct_seed_tables": 3,
                           "truth": rows[0]["truth"], "mean_estimate": average([r["estimate"] for r in rows]),
                           "minimum_estimate": min(r["estimate"] for r in rows),
                           "maximum_estimate": max(r["estimate"] for r in rows),
                           "mean_signed_error": average([r["signed_error"] for r in rows]),
                           "mean_absolute_error": average([r["absolute_error"] for r in rows]),
                           "mean_squared_error": average([r["squared_error"] for r in rows]),
                           "maximum_absolute_error": max(r["absolute_error"] for r in rows),
                           "direction_matches_count": sum(r["direction_matches"] for r in rows),
                           "mean_numerical_utility_score": average([r["numerical_utility_score"] for r in rows]) if primary else "",
                           "engineering_fidelity_bands": "|".join(r["engineering_fidelity_band"] for r in rows),
                           "source_numeric_all_test_seeds_pass": all(r["test_source_numeric_pass"] for r in rows),
                           "source_protected_all_test_seeds_pass": all(r["test_source_protected_pass"] for r in rows)})
    write_csv(OUT / "aggregate_results.csv", aggregates)
    audit = {"schema": "c4_postreveal_evaluation_receipt_v1", "completed_utc": datetime.now(timezone.utc).isoformat(),
             "reveal_gate_sha256": GATE_HASH, "verified_bindings": bound,
             "original_custody_hashes_verified_before_and_after": True,
             "evaluator_sha256": sha(R / "custody" / "evaluate.py"),
             "evaluation_contract_sha256": sha(R / "custody" / "evaluate_contract.json"),
             "adapter_sha256": sha(__file__), "scheduled_slots_evaluated": 24, "unique_table_contents": 6,
             "raw_endpoint_rows": len(full_rows), "selected_policy_endpoint_rows": len(policy_rows),
             "policy_aggregate_rows": len(aggregates), "additional_generation_runs": 0,
             "candidate_code_imports": 0, "per_table_evaluations": raw_manifests}
    for path, expected in commitment["hidden_artifacts"].items():
        assert sha(R / path) == expected
    for name in ("all_table_endpoints.csv", "selected_policy_endpoints.csv", "aggregate_results.csv"):
        audit.setdefault("aggregate_artifacts", {})[name] = sha(OUT / name)
    write_json(OUT / "EVALUATION_RECEIPT.json", audit)
    print(json.dumps({"status": "complete", "evaluated_slots": 24, "unique_contents": 6,
                      "primary_results_shared_by_all_policies": [v for v in aggregates if v["endpoint"] == "adjusted_x_coefficient" and v["policy"] == "retain_initial"]}, indent=2))


if __name__ == "__main__":
    main()
