"""Fail-closed campaign gate. Reference CSVs are hashed, not parsed here."""
from __future__ import annotations
import hashlib
import json
from datetime import datetime
from pathlib import Path
import re
import sys

from analysis import HERE, PROJECT, PREPARATION, POINT_PATH

SEEDS = [92101, 92102, 92103]
IDS = {"ia": "nhanes_insulin", "ib": "nhanes_insulin", "ha": "pns_hba1c", "hb": "pns_hba1c"}


class GateError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise GateError(message)


def absolute(value):
    p = Path(value)
    require(p.is_absolute(), "Manifest paths must be absolute")
    return p.resolve()


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _digest(value):
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None,
            "Invalid SHA-256 binding")
    return value


def validate_schedule(manifest):
    """Shape/schedule checks use no files; easily tested on invented manifests."""
    require(manifest.get("schema_version") == "m10-campaign-freeze-1", "Wrong freeze schema")
    require(manifest.get("status") == "frozen_before_target_analysis", "Manifest is not frozen")
    require(manifest.get("target_outcomes_inspected") is False, "Blindness declaration absent")
    stamp = datetime.fromisoformat(manifest["frozen_utc"].replace("Z", "+00:00"))
    require(stamp.tzinfo is not None, "Freeze timestamp needs timezone")
    require(manifest.get("residual_seeds") == SEEDS, "Residual schedule changed")
    items = manifest.get("constructions", [])
    require(len(items) == 4 and {c["construction_id"] for c in items} == set(IDS),
            "All four independent constructions are required")
    output_paths, runs, bundles = set(), set(), set()
    for construction in items:
        require(IDS[construction["construction_id"]] == construction["case_id"], "Construction case mismatch")
        bundle = absolute(construction["bundle_path"])
        require(bundle not in bundles, "Independent constructions require distinct bundle paths")
        bundles.add(bundle)
        for field in ["initial_candidate", "selected_candidate", "final_selection_path"]:
            absolute(construction[field])
        outputs = construction["outputs"]
        require(len(outputs) == 3 and sorted(o["seed"] for o in outputs) == SEEDS,
                "Every construction requires all three residual seeds")
        for output in outputs:
            path, receipt = absolute(output["path"]), absolute(output["receipt_path"])
            run_id = output["run_id"]
            require(isinstance(run_id, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", run_id), "Unsafe run ID")
            require(path == bundle / "executions" / run_id / "output/generated.csv", "Output path not canonical for bundle/run")
            require(receipt == bundle / "executions" / run_id / "execution.json", "Receipt path not canonical for bundle/run")
            require(path not in output_paths and (bundle, run_id) not in runs, "Duplicate output path or scoped run ID")
            output_paths.add(path)
            runs.add((bundle, run_id))
            _digest(output["sha256"])
            _digest(output["receipt_sha256"])
    require(len(output_paths) == 12, "Twelve final output slots are required")
    require(set(manifest.get("cases", {})) == {"nhanes_insulin", "pns_hba1c"}, "Both case input specifications required")
    return items


def verify_manifest(path, *, candidate_verifier=None, execution_verifier=None):
    """Verify all campaign bytes/receipts *before* any reserved outcome parsing.

    Injected verifiers exist only for invented unit tests. Production always uses
    the unchanged harness's recursive candidate and execution verification.
    """
    manifest_path = absolute(path)
    manifest_digest = sha256(manifest_path)
    manifest = read_json(manifest_path)
    constructions = validate_schedule(manifest)
    bindings = {}
    for item in manifest.get("bindings", []):
        p, digest = absolute(item["path"]), _digest(item["sha256"])
        require(p not in bindings, "Duplicate binding path")
        bindings[p] = digest
    required = {POINT_PATH.resolve(), (HERE/"FREEZE_INTERFACE.md").resolve(), (HERE/"INFERENCE.md").resolve()}
    required.update(p.resolve() for p in HERE.glob("*.py"))
    required.update((PREPARATION/"protocols"/name).resolve() for name in
                    ["nhanes_insulin.json", "pns_hba1c.json", "endpoint_evidence_map.json", "campaign_feasibility_v2.json"])
    controller_paths = manifest.get("controller_binding_paths")
    require(isinstance(controller_paths, list) and bool(controller_paths), "Controller protocol/campaign/input manifests must be bound")
    required.update(absolute(p) for p in controller_paths)
    expected_case_keys = {
        "nhanes_insulin": {"observed_path", "reference_path", "prepare_reader_path", "demo_path", "fasting_design_path"},
        "pns_hba1c": {"observed_path", "reference_path", "weights_path", "id_mapping_path"}}
    for case, config in manifest["cases"].items():
        require(set(config) == expected_case_keys[case], "Unexpected or missing case input path fields")
        required.update(absolute(p) for p in config.values())
    for c in constructions:
        bundle = absolute(c["bundle_path"])
        required.update([bundle/"observed.csv", bundle/"task.json", absolute(c["initial_candidate"])/"freeze.json",
                         absolute(c["selected_candidate"])/"freeze.json", absolute(c["final_selection_path"])])
    require(required.issubset(bindings), "Missing required code/protocol/candidate/input/custody binding")
    # Full case paths must be the original prepared case, not substituted reference data.
    for case, config in manifest["cases"].items():
        require(absolute(config["reference_path"]) == (PREPARATION/case/"custodian/reference.csv").resolve(), "Unexpected reserved reference path")
        require(absolute(config["observed_path"]) == (PREPARATION/case/"visible/observed.csv").resolve(), "Unexpected visible input path")
    for p, expected in bindings.items():
        require(sha256(p) == expected, f"Frozen bytes changed: {p}")
    if candidate_verifier is None or execution_verifier is None:
        sys.path.insert(0, str(PROJECT))
        from cohort_harness.lifecycle import verify_candidate
        from cohort_harness.execution import verify_execution
        candidate_verifier = candidate_verifier or verify_candidate
        execution_verifier = execution_verifier or verify_execution
    for c in constructions:
        bundle, candidate = absolute(c["bundle_path"]), absolute(c["selected_candidate"])
        candidate_verifier(bundle, absolute(c["initial_candidate"]))
        frozen = candidate_verifier(bundle, candidate)
        require(frozen["route"] == "generator.py", "This feasibility freeze requires executable generators")
        selected = read_json(c["final_selection_path"])
        require(selected.get("target_outcomes_read") is False, "Builder selection lacks blindness declaration")
        require(selected.get("target_feedback_used", False) is False, "Target feedback used in selection")
        name = Path(selected["selected_candidate"])
        selected_path = name if name.is_absolute() else bundle/name if len(name.parts) > 1 else bundle/"candidates"/name
        require(selected_path.resolve() == candidate, "Final selection differs from frozen selected candidate")
        observed = absolute(manifest["cases"][c["case_id"]]["observed_path"])
        require(sha256(bundle/"observed.csv") == bindings[observed], "Construction did not use shared observed input")
        for output in c["outputs"]:
            require(sha256(output["path"]) == output["sha256"], "Frozen output changed")
            require(sha256(output["receipt_path"]) == output["receipt_sha256"], "Frozen execution receipt changed")
            receipt = execution_verifier(bundle, output["run_id"])
            require(receipt["status"] == "success" and receipt["generator_executed"] is True, "Final generation did not succeed")
            require(receipt["limits"]["seed"] == output["seed"], "Residual seed/receipt mismatch")
            require((bundle/receipt["candidate"]).resolve() == candidate, "Execution used a different selected candidate")
            require(receipt["files"].get("output/generated.csv") == output["sha256"], "Output hash not bound in verified receipt")
    require(sha256(manifest_path) == manifest_digest, "Campaign manifest changed while being verified")
    return manifest, {"status": "passed", "manifest_sha256": manifest_digest,
                      "construction_count": 4, "scheduled_outputs": 12,
                      "reference_outcomes_parsed_during_gate": False,
                      "isolation": "procedural_agent_separation_not_OS_or_cryptographic_isolation"}
