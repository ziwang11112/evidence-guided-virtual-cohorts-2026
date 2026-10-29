"""Invented release records; no participant data and no generator execution.

Harness verifiers are replaced with small record/hash verifiers to isolate the
new gate. The real harness's algorithm and isolation tests remain separate.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


SOURCE = Path(__file__).resolve().parents[1] / "release_guard.py"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def case(tmp_path_factory, monkeypatch):
    root = tmp_path_factory.mktemp("r")
    code = root / "release_guard.py"
    code.write_bytes(SOURCE.read_bytes())
    spec = importlib.util.spec_from_file_location("invented_release_guard", code)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    bundle = root / "agent_bundle"
    bundle.mkdir()
    (bundle / "observed.csv").write_text("invented covariate marker only\n", encoding="utf-8")
    write(bundle / "task.json", {"budget": {"revisions": 1}})
    protocol = {"structures": ["s1", "s2", "s3"], "source_seeds": [76101, 76102, 76103],
                "target_seeds": [76201, 76202, 76203, 76204, 76205], "source_feedback_round_max": 1}
    write(root / "protocol.json", protocol)
    write(root / "protocol_commitment.json", {
        "schema_version": 1, "kind": "structure_robustness_protocol_commitment",
        "created_utc": "2026-10-28T00:00:00+00:00",
        "files": {"protocol.json": digest(root / "protocol.json"), "release_guard.py": digest(code)}})
    manifest = {"authorize_target_evaluation": True, "all_structures_and_seeds_committed": True,
                "custodian_lock_sha256": "1" * 64, "structures": protocol["structures"],
                "seeds": protocol["target_seeds"], "bundle_path": "agent_bundle",
                "experiment_protocol": {"path": "protocol.json", "sha256": digest(root / "protocol.json")},
                "controller_guard": {"path": "release_guard.py", "sha256": digest(code), "function": "verify_release"},
                "builder_observed": {"path": "agent_bundle/observed.csv", "sha256": digest(bundle / "observed.csv")},
                "candidate_commitments": [], "source_replays": [], "outputs": []}
    recipe = {"contexts": [{"id": "x", "assumption_ids": ["A_source"],
                             "checks": [{"assumption_ids": []}]}]}
    for structure in protocol["structures"]:
        for stage in ["initial", "final"]:
            name = f"{structure}_{stage}"
            directory = bundle / "candidates" / name
            write(directory / "evidence.json", {"scope": "invented"})
            write(directory / "source_replay.json", recipe)
            write(directory / "model_spec.json", {"assumptions": [{"id": "A_source", "description": "invented source context"}]})
            (directory / "generator.py").write_text("# Invented marker, never executed\n", encoding="utf-8")
            commitments = {"observed.csv": digest(bundle / "observed.csv")}
            for filename in ["evidence.json", "source_replay.json", "model_spec.json", "generator.py"]:
                commitments[f"candidates/{name}/{filename}"] = digest(directory / filename)
            parent = None if stage == "initial" else {
                "candidate": f"candidates/{structure}_initial", "receipt_path": f"candidates/{structure}_initial/freeze.json",
                "sha256": digest(bundle / f"candidates/{structure}_initial/freeze.json")}
            receipt = {"candidate": f"candidates/{name}", "route": "generator.py", "commitments": commitments,
                       "parent": parent, "revision_index": int(stage == "final"),
                       "created_utc": f"2026-10-28T00:0{1 if stage == 'initial' else 4}:{'30' if structure == 's3' else '00'}+00:00"}
            write(directory / "freeze.json", receipt)
            freeze_hash = digest(directory / "freeze.json")
            manifest["candidate_commitments"].append({"structure": structure, "stage": stage, "candidate_name": name,
                "path": f"agent_bundle/candidates/{name}/freeze.json", "sha256": freeze_hash})
            for seed in protocol["source_seeds"]:
                replay_id = f"{name}_{seed}"
                replay_dir = bundle / "source_replays" / replay_id
                execution_time = "2026-10-28T00:02:00+00:00" if stage == "initial" else "2026-10-28T00:05:00+00:00"
                report_time = "2026-10-28T00:03:00+00:00" if stage == "initial" else "2026-10-28T00:06:00+00:00"
                write(replay_dir / "contexts/x/bundle/executions/replay/execution.json", {"created_utc": execution_time})
                report = {"status": "success", "limits": {"seed": seed}, "created_utc": report_time,
                          "parent": {"candidate": f"candidates/{name}", "freeze.json_sha256": freeze_hash},
                          "contexts": [{"id": "x", "generation_link_verified": True,
                                        "child_bundle": "contexts/x/bundle"}]}
                write(replay_dir / "replay.json", report)
                manifest["source_replays"].append({"structure": structure, "stage": stage, "seed": seed, "replay_id": replay_id})
        for seed in protocol["target_seeds"]:
            name = f"{structure}_final"
            run_id = f"{name}_{seed}"
            output = bundle / "executions" / run_id / "output/generated.csv"
            output.parent.mkdir(parents=True)
            output.write_text(f"invented output marker {structure} {seed}\n", encoding="utf-8")
            receipt = {"status": "success", "route": "generator.py", "generator_executed": True,
                       "candidate": f"candidates/{name}", "candidate_freeze_sha256": digest(bundle / f"candidates/{name}/freeze.json"),
                       "limits": {"seed": seed}, "files": {"output/generated.csv": digest(output)},
                       "created_utc": "2026-10-28T00:07:00+00:00"}
            write(output.parents[1] / "execution.json", receipt)
            manifest["outputs"].append({"structure": structure, "seed": seed, "candidate_name": name, "run_id": run_id,
                "path": output.relative_to(root).as_posix(), "sha256": digest(output)})
    calls = {"candidate": [], "source": [], "execution": []}

    def verify_candidate(actual_bundle, name):
        assert actual_bundle == bundle
        calls["candidate"].append(name)
        receipt = read(bundle / name / "freeze.json")
        for filename, expected in receipt["commitments"].items():
            if digest(bundle / filename) != expected:
                raise ValueError("Mock harness: frozen candidate tree changed")
        return receipt

    def verify_source(actual_bundle, replay_id, *, candidate):
        assert actual_bundle == bundle
        calls["source"].append((replay_id, candidate))
        report = read(bundle / "source_replays" / replay_id / "replay.json")
        assert candidate == report["parent"]["candidate"]
        return report

    def verify_execution(actual_bundle, run_id):
        assert actual_bundle == bundle
        calls["execution"].append(run_id)
        return read(bundle / "executions" / run_id / "execution.json")

    monkeypatch.setattr(module, "verify_candidate", verify_candidate)
    monkeypatch.setattr(module, "verify_source_replay", verify_source)
    monkeypatch.setattr(module, "verify_execution", verify_execution)
    path = root / "release.json"
    write(path, manifest)
    return {"root": root, "bundle": bundle, "module": module, "manifest": manifest, "path": path, "calls": calls}


def run(case):
    write(case["path"], case["manifest"])
    return case["module"].verify_release(case["path"])


def test_complete_portable_grid_passes_without_hidden_data(case):
    result = run(case)
    assert result["status"] == "passed" and result["target_outcomes_analyzed"] is False
    assert (result["candidates_verified"], result["source_replays_verified"], result["target_outputs_verified"]) == (6, 18, 15)
    assert [len(case["calls"][key]) for key in ["candidate", "source", "execution"]] == [6, 18, 15]
    assert not (case["root"] / "custodian").exists()


@pytest.mark.parametrize("field", ["candidate_commitments", "source_replays", "outputs"])
@pytest.mark.parametrize("mutation", ["omit", "duplicate"])
def test_incomplete_or_duplicate_grids_rejected(case, field, mutation):
    rows = case["manifest"][field]
    rows.pop() if mutation == "omit" else rows.append(copy.deepcopy(rows[0]))
    with pytest.raises(ValueError, match="grid"):
        run(case)


def test_manifest_cannot_shrink_its_own_seed_grid(case):
    case["manifest"]["seeds"].pop()
    case["manifest"]["outputs"] = [x for x in case["manifest"]["outputs"] if x["seed"] != 76205]
    with pytest.raises(ValueError, match="independently committed"):
        run(case)


@pytest.mark.parametrize("filename", ["protocol.json", "release_guard.py"])
def test_protocol_or_guard_tampering_rejected_even_if_release_manifest_rehashed(case, filename):
    path = case["root"] / filename
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    key = "experiment_protocol" if filename == "protocol.json" else "controller_guard"
    case["manifest"][key]["sha256"] = digest(path)
    with pytest.raises(ValueError, match="Protocol-anchored"):
        run(case)


def test_mixed_bundle_rejected(case):
    (case["root"] / "other_bundle").mkdir()
    case["manifest"]["bundle_path"] = "other_bundle"
    with pytest.raises(ValueError, match="Mixed or wrong bundle"):
        run(case)


def test_uncommitted_candidate_tree_edit_is_sent_to_harness_verifier(case):
    (case["bundle"] / "candidates/s1_initial/generator.py").write_text("changed", encoding="utf-8")
    with pytest.raises(ValueError, match="frozen candidate tree changed"):
        run(case)


def test_output_bytes_must_match_manifest(case):
    path = case["root"] / case["manifest"]["outputs"][0]["path"]
    path.write_text("altered output", encoding="utf-8")
    with pytest.raises(ValueError, match="Artifact hash mismatch"):
        run(case)


@pytest.mark.parametrize("field,value,message", [
    ("status", "failed", "successful program"), ("route", "generated.csv", "successful program"),
    ("generator_executed", False, "successful program"), ("candidate", "candidates/s2_final", "candidate binding"),
    ("candidate_freeze_sha256", "2" * 64, "candidate binding"),
    ("created_utc", "2026-10-28T00:05:00+00:00", "before all final")])
def test_execution_identity_status_and_chronology_rejected(case, field, value, message):
    row = case["manifest"]["outputs"][0]
    path = case["bundle"] / "executions" / row["run_id"] / "execution.json"
    receipt = read(path)
    receipt[field] = value
    write(path, receipt)
    with pytest.raises(ValueError, match=message):
        run(case)


def test_execution_seed_cannot_be_relabelled(case):
    row = case["manifest"]["outputs"][0]
    path = case["bundle"] / "executions" / row["run_id"] / "execution.json"
    receipt = read(path)
    receipt["limits"]["seed"] = 999
    write(path, receipt)
    with pytest.raises(ValueError, match="wrong seed"):
        run(case)


def test_output_hash_must_also_match_execution_receipt(case):
    row = case["manifest"]["outputs"][0]
    path = case["root"] / row["path"]
    path.write_text("substituted and manifest rehashed", encoding="utf-8")
    row["sha256"] = digest(path)
    with pytest.raises(ValueError, match="match execution receipt"):
        run(case)


def test_initial_feedback_cannot_follow_final_freeze(case):
    replay_id = case["manifest"]["source_replays"][0]["replay_id"]
    path = case["bundle"] / "source_replays" / replay_id / "replay.json"
    report = read(path)
    report["created_utc"] = "2026-10-28T00:05:00+00:00"
    write(path, report)
    with pytest.raises(ValueError, match="before final freeze"):
        run(case)


def test_protocol_commitment_cannot_follow_source_execution(case):
    path = case["root"] / "protocol_commitment.json"
    anchor = read(path)
    anchor["created_utc"] = "2026-10-28T00:02:30+00:00"
    write(path, anchor)
    with pytest.raises(ValueError, match="predates protocol"):
        run(case)


def test_failed_source_execution_is_not_ignored(case):
    replay_id = case["manifest"]["source_replays"][0]["replay_id"]
    path = case["bundle"] / "source_replays" / replay_id / "replay.json"
    report = read(path)
    report["status"] = "failed"
    write(path, report)
    with pytest.raises(ValueError, match="Source replay failed"):
        run(case)


def test_source_assumption_changes_cannot_hide_inside_new_frozen_candidate(case):
    directory = case["bundle"] / "candidates/s2_initial"
    spec = read(directory / "model_spec.json")
    spec["assumptions"][0]["description"] = "a different source-population assumption"
    write(directory / "model_spec.json", spec)
    receipt = read(directory / "freeze.json")
    receipt["commitments"]["candidates/s2_initial/model_spec.json"] = digest(directory / "model_spec.json")
    write(directory / "freeze.json", receipt)
    for entry in case["manifest"]["candidate_commitments"]:
        if entry["candidate_name"] == "s2_initial":
            entry["sha256"] = digest(directory / "freeze.json")
    with pytest.raises(ValueError, match="source assumptions differ"):
        run(case)


def test_wrong_final_parent_rejected_even_with_rehashed_candidate_manifest(case):
    directory = case["bundle"] / "candidates/s1_final"
    receipt = read(directory / "freeze.json")
    receipt["parent"]["candidate"] = "candidates/s2_initial"
    write(directory / "freeze.json", receipt)
    for entry in case["manifest"]["candidate_commitments"]:
        if entry["candidate_name"] == "s1_final":
            entry["sha256"] = digest(directory / "freeze.json")
    with pytest.raises(ValueError, match="wrong initial parent"):
        run(case)


def test_duplicate_execution_file_rejected(case):
    outputs = case["manifest"]["outputs"]
    outputs[1]["run_id"] = outputs[0]["run_id"]
    outputs[1]["path"] = outputs[0]["path"]
    outputs[1]["sha256"] = outputs[0]["sha256"]
    with pytest.raises(ValueError, match="Duplicate target execution"):
        run(case)


@pytest.mark.parametrize("stage,early_time", [
    ("initial", "2026-10-28T00:01:15+00:00"), ("final", "2026-10-28T00:04:15+00:00")])
def test_every_structure_must_freeze_before_any_stage_replay(case, stage, early_time):
    row = next(r for r in case["manifest"]["source_replays"] if r["structure"] == "s1" and r["stage"] == stage)
    path = case["bundle"] / "source_replays" / row["replay_id"] / "contexts/x/bundle/executions/replay/execution.json"
    write(path, {"created_utc": early_time})
    with pytest.raises(ValueError, match="predates protocol commitment/freeze"):
        run(case)


@pytest.mark.parametrize("filename", ["evidence.json", "source_replay.json"])
def test_changed_frozen_source_bytes_rejected_across_structures(case, filename):
    directory = case["bundle"] / "candidates/s2_initial"
    path = directory / filename
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    receipt = read(directory / "freeze.json")
    receipt["commitments"]["candidates/s2_initial/" + filename] = digest(path)
    write(directory / "freeze.json", receipt)
    for entry in case["manifest"]["candidate_commitments"]:
        if entry["candidate_name"] == "s2_initial":
            entry["sha256"] = digest(directory / "freeze.json")
    with pytest.raises(ValueError, match="Evidence, source recipe"):
        run(case)


def test_wrong_source_seed_rejected(case):
    row = case["manifest"]["source_replays"][0]
    path = case["bundle"] / "source_replays" / row["replay_id"] / "replay.json"
    report = read(path)
    report["limits"]["seed"] = 999
    write(path, report)
    with pytest.raises(ValueError, match="wrong seed"):
        run(case)
