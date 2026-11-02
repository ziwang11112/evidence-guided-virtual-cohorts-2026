"""Two real isolated executions of an invented fixture, never a clinical case.

prepare writes unsigned requests; a separate reviewer supplies context_reviews.json
and unit_mapping_approved.json. run cannot manufacture either approval. One source
and one target slot are fixed by the frozen fixture. No automatic retry exists.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

PROJECT = Path(__file__).resolve().parents[3]
SCALE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
sys.path.insert(0, str(SCALE / "bridge"))
sys.path.insert(0, str(SCALE / "bridge_units"))

import context_bridge as bridge
from invented_fixture import build_parent
import unit_conversion as units
from cohort_harness import execution, lifecycle


def write(path, value):
    execution._write(Path(path), value)


def prepare(root):
    root = Path(root).absolute()
    root.mkdir(parents=True, exist_ok=False)
    bundle = build_parent(root / "bundle")
    plan = lifecycle.read_json(bundle / "candidates/invented" / bridge.PLAN)
    assert plan["budget"] == {"source_attempts": 1, "source_rows": 3,
                              "target_attempts": 1, "target_rows": 6}
    bridge.prepare(bundle, "invented")
    write(root / "binding_requests.json", bridge.binding_requests(bundle, "invented"))
    inputs = {"row_id": "id", "columns": [
        {"name": "id", "kind": "string", "role": "identifier", "analyte_id": "row_id",
         "unit": "1", "scale": "categorical"},
        {"name": "x", "kind": "number", "role": "generated", "analyte_id": "invented_quantity",
         "unit": "example_unit", "scale": "original"},
    ]}
    outputs = copy.deepcopy(inputs)
    outputs["columns"][1]["unit"] = "example_unit_scaled"
    mapping = {"schema_version": 1, "purpose": "analytic_fixture",
               "input_contract_sha256": units.contract_digest(inputs),
               "output_contract_sha256": units.contract_digest(outputs),
               "columns": [
                   {"column": "id", "operation": "identity", "factor": 1.0, "source": None},
                   {"column": "x", "operation": "multiply", "factor": 2.0,
                    "source": {"kind": "invented_fixture", "reference": "Invented definition: scaled = 2 * original",
                               "locator": "run_invented_pair.prepare", "analyte_id": "invented_quantity",
                               "input_unit": "example_unit", "output_unit": "example_unit_scaled"}},
               ], "review": None}
    write(root / "unit_input_contract.json", inputs)
    write(root / "unit_output_contract.json", outputs)
    write(root / "unit_mapping_proposal.json", mapping)
    write(root / "SMOKE_PLAN.json", {
        "kind": "invented_software_integration_not_biomedical_experiment",
        "prepared_utc": datetime.now(timezone.utc).isoformat(),
        "source_rows": 3, "target_rows": 6, "max_source_attempts": 1, "max_target_attempts": 1,
        "seeds": {"source-one": 101, "target-one": 103},
        "generator_sha256": lifecycle.sha256(bundle / "candidates/invented/generator.py"),
        "parent_freeze_sha256": lifecycle.sha256(bundle / "candidates/invented/freeze.json"),
        "unit_mapping_proposal_digest": units.manifest_digest(mapping),
        "unit_adapter_sha256": lifecycle.sha256(units.__file__),
        "smoke_driver_sha256": lifecycle.sha256(__file__),
        "expected_source_geometric_mean": 2.0,
        "expected_original_pattern": [1.0, 2.0, 4.0],
        "expected_scaled_pattern": [2.0, 4.0, 8.0],
        "production_unit_factors": False,
        "review_state": "pending_actual_independent_review",
        "clinical_case_release": False,
    })
    return {"prepared": True, "review_required": True, "generator_runs": 0,
            "unit_mapping_proposal_digest": units.manifest_digest(mapping)}


def run(root):
    root = Path(root).absolute()
    bundle = root / "bundle"
    plan = lifecycle.read_json(root / "SMOKE_PLAN.json")
    assert plan["kind"] == "invented_software_integration_not_biomedical_experiment"
    assert plan["generator_sha256"] == lifecycle.sha256(bundle / "candidates/invented/generator.py")
    assert plan["parent_freeze_sha256"] == lifecycle.sha256(bundle / "candidates/invented/freeze.json")
    assert plan["unit_adapter_sha256"] == lifecycle.sha256(units.__file__)
    assert plan["smoke_driver_sha256"] == lifecycle.sha256(__file__)
    assert lifecycle.read_json(bundle / "task.json")["task_id"] == "invented-bridge"
    reviews = lifecycle.read_json(root / "context_reviews.json")
    mapping = lifecycle.read_json(root / "unit_mapping_approved.json")
    inputs = lifecycle.read_json(root / "unit_input_contract.json")
    outputs = lifecycle.read_json(root / "unit_output_contract.json")
    assert units.manifest_digest(mapping) == plan["unit_mapping_proposal_digest"]
    units.validate_manifest(mapping, inputs, outputs)
    target_task_path = bundle / bridge.FOLDER / "invented/contexts/target/bundle/task.json"
    target_task = lifecycle.read_json(target_task_path)
    assert inputs["row_id"] == target_task["row_id"]
    column_fields = ("name", "kind", "role", "unit")
    assert [{key: c[key] for key in column_fields} for c in inputs["columns"]] == [
        {key: c[key] for key in column_fields} for c in target_task["columns"]]
    # All reviews must exist and match before any generator dispatch.
    bridge.seal(bundle, "invented", reviews)
    report = bridge.execute(bundle, "invented")
    write(root / "BRIDGE_REPORT.json", report)
    assert len(report["trials"]) == 2 and all(x["status"] == "success" for x in report["trials"])
    assert report["source_target_generation_link_verified"] is True
    bridge.verify(bundle, "invented")
    base = bundle / bridge.FOLDER / "invented" / "contexts"
    receipts, frames = {}, {}
    for context, run_id, expected_rows in [("source", "source-one", 3), ("target", "target-one", 6)]:
        child = base / context / "bundle"
        receipt = execution.verify_execution(child, run_id)
        assert receipt["status"] == "success" and receipt["generator_executed"] is True
        task = lifecycle.read_json(child / "task.json")
        frame = lifecycle.read_table(child / "executions" / run_id / "output/generated.csv", task, output=True)
        assert len(frame) == expected_rows
        assert frame["x"].tolist() == plan["expected_original_pattern"] * (expected_rows // 3)
        receipts[context], frames[context] = receipt, frame
    source = base / "source" / "bundle"
    native = lifecycle.read_json(source / bridge.semantic.FOLDER / "source-one/feedback.json")
    supplemental = lifecycle.read_json(source / bridge.supplement.FOLDER / "source-one/feedback.json")
    assert native["checks"][0]["status"] == "not_computable"
    assert native["checks"][0]["difference"] is None
    check = supplemental["checks"][0]
    assert abs(check["diagnostic"]["diagnostic"]["value"] - plan["expected_source_geometric_mean"]) < 1e-12
    assert check["strict_source_difference"] is None and check["proxy"] is None
    target = base / "target" / "bundle"
    target_run = target / "executions/target-one"
    converted, conversion = units.convert_frame(
        frames["target"], mapping, input_contract=inputs, output_contract=outputs,
        expected_input_sha256=units.frame_digest(frames["target"]),
        caller_binding={"kind": "root_verified_invented_bridge_execution",
                        "execution_sha256": lifecycle.sha256(target_run / "execution.json"),
                        "generated_csv_sha256": lifecycle.sha256(target_run / "output/generated.csv"),
                        "target_task_sha256": lifecycle.sha256(target_task_path),
                        "unit_adapter_sha256": lifecycle.sha256(units.__file__),
                        "bridge_report_sha256": lifecycle.sha256(root / "BRIDGE_REPORT.json")})
    assert converted["x"].tolist() == plan["expected_scaled_pattern"] * 2
    assert converted["id"].equals(frames["target"]["id"])
    write(root / "UNIT_CONVERSION_RECEIPT.json", conversion)
    result = {"kind": "invented_live_isolated_integration_result", "status": "passed",
              "source_rows": 3, "target_rows": 6, "source_attempts": 1, "target_attempts": 1,
              "isolated_generator_runs": 2, "real_lifecycle_verification": True,
              "source_target_generation_link_verified": True,
              "source_semantic_v1_status": "not_computable_original_geometric_mean_preserved",
              "supplemental_geometric_mean": check["diagnostic"]["diagnostic"]["value"],
              "supplemental_strict_difference": None,
              "target_feedback_policy": "none", "unit_view_verified": True,
              "new_biomedical_generations": 0, "patient_data_accessed": False,
              "clinical_unit_conversion_activated": False,
              "elapsed_execution_seconds": {k: v["elapsed_seconds"] for k, v in receipts.items()},
              "bridge_report_sha256": lifecycle.sha256(root / "BRIDGE_REPORT.json"),
              "unit_conversion_receipt_sha256": lifecycle.sha256(root / "UNIT_CONVERSION_RECEIPT.json")}
    write(root / "LIVE_RESULT.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "run"])
    parser.add_argument("root", help="New local software-fixture directory, never a clinical bundle")
    args = parser.parse_args()
    print(json.dumps(prepare(args.root) if args.action == "prepare" else run(args.root), indent=2))
