"""Integration boundaries only; invented model values, no generator execution."""
import copy
import json
import sys
from pathlib import Path

import pandas as pd
import pytest

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
sys.path.insert(0, str(PROJECT))
sys.path.insert(0, str(HERE))
import bundle_assembly as assembly
import case_execution as runner
from cohort_harness.contracts import ContractError


def fixture_spec(package):
    contexts = {c["id"]: {"population": c["recipe"]["population"], "measurement": c["recipe"]["measurement"]["description"],
                           "n_rows": 5000, "inputs": {}} for c in package["templates"]}
    contexts[package["target_id"]] = {**package["target_descriptor"], "inputs": {}}
    params = {"active_context": package["target_id"], "contexts": contexts, "invented_constant": 1}
    spec = {"parameters": params, "assumptions": [{"id": "invented", "description": "Metadata test only, no scientific model"}],
            "parameter_provenance": {k: {"evidence_ids": [], "assumption_ids": ["invented"], "derivation": "Invented software fixture"} for k in params}}
    authoring = {"context_assumption_ids": {k: ["invented"] for k in contexts}, "context_varying_parameters": [], "descriptive_proxies": {}}
    return spec, authoring


@pytest.mark.parametrize("case", ["K01", "K02"])
def test_actual_packet_materialization_detects_tampering_without_model(tmp_path, case):
    package = assembly.load_package(case)
    folder = tmp_path / case
    review = {"curator_id": "invented-test-curator", "reviewed_utc": "invented-test-time",
              "reason": "Software fixture only, not scientific approval", "package_sha256": assembly.package_digest(package)}
    receipt = assembly.prepare_bundle(case, "A01", folder, review)
    assert not receipt["clinical_construction_released"]
    assert not (folder / "candidates").exists()
    assert assembly.verify_bundle_inputs(folder)["package_sha256"] == assembly.package_digest(package)
    altered = copy.deepcopy(receipt)
    del altered["files"]["task.json"]
    (folder / "INPUT_ASSEMBLY.json").write_bytes(assembly.encoded(altered))
    with pytest.raises(ContractError, match="exact permitted packet"):
        assembly.verify_bundle_inputs(folder)
    (folder / "INPUT_ASSEMBLY.json").write_bytes(assembly.encoded(receipt))
    (folder / "task.json").write_text('{}', encoding="utf-8")
    with pytest.raises(ContractError, match="Builder input changed"):
        assembly.verify_bundle_inputs(folder)


@pytest.mark.parametrize("case,nsources", [("K01", 2), ("K02", 6)])
def test_plans_preserve_science_and_force_no_target_feedback(case, nsources):
    package = assembly.load_package(case)
    spec, authoring = fixture_spec(package)
    before = copy.deepcopy(spec)
    plan = assembly.build_bridge_plan(package, "A01", "initial", spec, authoring)
    assert spec == before
    assert len(plan["trials"]) == nsources + 3
    target = [c for c in plan["contexts"] if c["role"] == "target"]
    assert len(target) == 1 and target[0]["feedback_policy"] == "none"
    assert [t["seed"] for t in plan["trials"][-3:]] == [2101, 2102, 2103]
    spec["parameters"]["contexts"][package["templates"][0]["id"]]["n_rows"] = 4999
    with pytest.raises(ContractError, match="Source descriptor differs"):
        assembly.build_bridge_plan(package, "A01", "initial", spec, authoring)


def test_mixed_sex_source_is_rejected_instead_of_filtered():
    package = assembly.load_package("K02")
    task = copy.deepcopy(package["task"])
    task["n_rows"] = 3  # Pure guard fixture; production authenticates 5,000 rows separately.
    frame = pd.DataFrame({"id": ["a", "b", "c"], "age": [40., 45., 50.], "sex": ["M", "F", "M"],
                          "bmi": [20., 22., 24.], "total_cholesterol": [3., 4., 5.], "hdl_cholesterol": [1., 1.2, 1.5]})
    before = frame.copy(deep=True)
    with pytest.raises(ContractError, match="wrong-sex"):
        runner._guard(frame, task, package, "malawi_rural_men")
    pd.testing.assert_frame_equal(frame, before)
    assert runner._guard(frame, task, package, package["target_id"])["pure_guard"]["validated_rows"] == 3


def test_proxy_cannot_reference_another_context_or_unknown_assumption():
    package = assembly.load_package("K02")
    spec, authoring = fixture_spec(package)
    authoring["descriptive_proxies"] = {"malawi_rural_men": {"assumption_ids": ["unknown"], "reason": "Fixture"}}
    with pytest.raises(ContractError, match="Unknown/missing proxy"):
        assembly.build_bridge_plan(package, "A01", "initial", spec, authoring)
