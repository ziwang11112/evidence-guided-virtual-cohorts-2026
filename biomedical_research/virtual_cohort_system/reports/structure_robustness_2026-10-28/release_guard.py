"""Target-blind, experiment-specific release gate; no generator execution.

The custodian must authenticate this file before importing it. Hashes and UTC
timestamps support a procedural record, not host-enforced blinding or signatures.
The guard verifies generated artifacts through the supplied harness. It never
opens the custodian's hidden outcome table or performs a target analysis.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
from pathlib import Path
import re

from cohort_harness.lifecycle import read_json, verify_candidate
from cohort_harness.execution import verify_execution
from cohort_harness.source_replay import verify_source_replay


class ReleaseError(ValueError):
    """The committed experiment is not ready for target release."""


def _need(condition, message):
    if not condition:
        raise ReleaseError(message)


def _digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _sha(value):
    _need(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value), "Invalid SHA-256")
    return value


def _time(value):
    _need(isinstance(value, str), "Missing UTC timestamp")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    _need(result.tzinfo is not None and result.utcoffset().total_seconds() == 0,
          "Timestamp must have a UTC offset")
    return result


def _name(value):
    _need(isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", value),
          "Unsafe artifact name")
    return value


def _path(value, base):
    _need(isinstance(value, str) and value, "Path must be a nonempty string")
    raw = Path(value)
    _need(".." not in raw.parts, "Path traversal is prohibited")
    result = raw if raw.is_absolute() else base / raw
    for part in [result, *result.parents]:
        _need(not part.is_symlink() and not getattr(part, "is_junction", lambda: False)(),
              "Links and junctions are prohibited")
    return result.resolve(strict=True)


def _reference(entry, expected, base):
    _need(isinstance(entry, dict), "Artifact reference must be an object")
    path = _path(entry["path"], base)
    _need(path == expected.resolve(strict=True), "Artifact path differs from the expected experiment path")
    _need(path.is_file() and _digest(path) == _sha(entry["sha256"]), "Artifact hash mismatch")
    return path


def _schedule(values, name, count):
    _need(isinstance(values, list) and len(values) == count, f"Wrong {name} schedule length")
    _need(all(type(x) is int and 0 <= x < 2**32 for x in values), f"Invalid {name} seed")
    _need(len(set(values)) == len(values), f"Duplicate {name} seed")
    return values


def _rows(value, required, label):
    _need(isinstance(value, list), f"{label} must be a list")
    for row in value:
        _need(isinstance(row, dict) and required <= row.keys(), f"Invalid {label} record")
    return value


def _source_assumptions(directory, recipe):
    spec = read_json(directory / "model_spec.json")
    definitions = {item["id"]: item["description"] for item in spec["assumptions"]}
    used = set()
    for context in recipe["contexts"]:
        used.update(context["assumption_ids"])
        for check in context["checks"]:
            used.update(check["assumption_ids"])
    _need(used <= definitions.keys(), "Missing source assumption definition")
    return {key: definitions[key] for key in sorted(used)}


def verify_release(commitment_path: Path) -> dict:
    """Verify the complete frozen experiment before custodian target loading.

    Paths in the release manifest are relative to that manifest's directory,
    or absolute paths resolving to exactly the same expected artifacts. The
    experiment root is this file's directory, never a fixed machine path.
    """
    here = Path(__file__).resolve().parent
    self_path = here / "release_guard.py"
    commitment_path = Path(commitment_path).resolve(strict=True)
    base = commitment_path.parent
    manifest = read_json(commitment_path)
    _need(isinstance(manifest, dict), "Release manifest must be an object")
    _need(manifest.get("authorize_target_evaluation") is True and
          manifest.get("all_structures_and_seeds_committed") is True, "Target release is not authorized")
    _sha(manifest["custodian_lock_sha256"])

    # This separate record is not supplied or redefined by the release manifest.
    protocol_commitment_path = here / "protocol_commitment.json"
    anchor = read_json(protocol_commitment_path)
    _need(anchor.get("schema_version") == 1 and
          anchor.get("kind") == "structure_robustness_protocol_commitment", "Invalid protocol commitment")
    anchor_time = _time(anchor["created_utc"])
    files = anchor["files"]
    _need(isinstance(files, dict) and {"protocol.json", "release_guard.py"} <= files.keys(),
          "Protocol commitment must bind protocol and guard code")
    for name, expected in files.items():
        artifact = _path(name, here)
        _need(artifact.is_relative_to(here) and artifact.is_file(), "Protocol artifact escapes experiment")
        _need(_digest(artifact) == _sha(expected), "Protocol-anchored artifact hash mismatch")
    _reference(manifest["experiment_protocol"], here / "protocol.json", base)
    _reference(manifest["controller_guard"], self_path, base)
    _need(manifest["controller_guard"].get("function") == "verify_release", "Wrong guard entry point")
    protocol = read_json(here / "protocol.json")
    structures = protocol["structures"]
    _need(structures == ["s1", "s2", "s3"], "Wrong committed structure identifiers")
    source_seeds = _schedule(protocol["source_seeds"], "source", 3)
    target_seeds = _schedule(protocol["target_seeds"], "target", 5)
    _need(not set(source_seeds) & set(target_seeds), "Source and target seed schedules overlap")
    _need(protocol["source_feedback_round_max"] == 1 and
          type(protocol["source_feedback_round_max"]) is int, "Expected one source-feedback round")
    _need(manifest["structures"] == structures and manifest["seeds"] == target_seeds,
          "Manifest schedule differs from independently committed protocol")
    bundle = _path(manifest["bundle_path"], base)
    _need(bundle == (here / "agent_bundle").resolve(strict=True) and bundle.is_dir(), "Mixed or wrong bundle")
    observed_path = _reference(manifest["builder_observed"], bundle / "observed.csv", base)
    observed_hash = _digest(observed_path)
    task = read_json(bundle / "task.json")
    _need(task["budget"]["revisions"] == 1, "Task revision budget differs from protocol")

    expected_candidates = {(s, stage) for s in structures for stage in ("initial", "final")}
    candidates = _rows(manifest["candidate_commitments"],
                       {"structure", "stage", "candidate_name", "path", "sha256"}, "candidate commitments")
    candidate_keys = [(c["structure"], c["stage"]) for c in candidates]
    _need(len(candidate_keys) == len(set(candidate_keys)) and set(candidate_keys) == expected_candidates,
          "Candidate grid is incomplete or duplicated")
    frozen = {}
    shared = None
    for entry in candidates:
        key = (entry["structure"], entry["stage"])
        name = f"{key[0]}_{key[1]}"
        _need(entry["candidate_name"] == name, "Candidate label does not match fixed naming")
        directory = bundle / "candidates" / name
        _reference(entry, directory / "freeze.json", base)
        receipt = verify_candidate(bundle, "candidates/" + name)
        _need(receipt["candidate"] == "candidates/" + name and receipt["route"] == "generator.py",
              "Wrong candidate identity or submission route")
        _need(receipt["commitments"].get("observed.csv") == observed_hash,
              "Candidate does not bind the builder observed input")
        _time(receipt["created_utc"])
        recipe = read_json(directory / "source_replay.json")
        signature = (_digest(directory / "evidence.json"), _digest(directory / "source_replay.json"),
                     _source_assumptions(directory, recipe))
        if shared is None:
            shared = signature
        _need(signature == shared, "Evidence, source recipe, or source assumptions differ across candidates")
        frozen[key] = (receipt, entry["sha256"])
    for structure in structures:
        first, first_hash = frozen[(structure, "initial")]
        last, _ = frozen[(structure, "final")]
        _need(first["parent"] is None and first["revision_index"] == 0, "Initial candidate has a parent")
        expected_parent = {"candidate": f"candidates/{structure}_initial",
                           "receipt_path": f"candidates/{structure}_initial/freeze.json", "sha256": first_hash}
        _need(last["parent"] == expected_parent and last["revision_index"] == 1,
              "Final candidate has the wrong initial parent or revision index")
        _need(_time(first["created_utc"]) <= _time(last["created_utc"]), "Candidate chronology is reversed")

    source_rows = _rows(manifest["source_replays"], {"structure", "stage", "replay_id", "seed"}, "source replays")
    source_keys = [(r["structure"], r["stage"], r["seed"]) for r in source_rows]
    expected_source = {(s, st, seed) for s, st in expected_candidates for seed in source_seeds}
    _need(len(source_keys) == len(set(source_keys)) and set(source_keys) == expected_source,
          "Source replay grid is incomplete or duplicated")
    replay_ids = [_name(row["replay_id"]) for row in source_rows]
    _need(len(set(replay_ids)) == len(replay_ids), "Duplicate source replay artifact")
    source_hashes = []
    final_source_times = []
    stage_freeze_times = {
        stage: max(_time(frozen[(s, stage)][0]["created_utc"]) for s in structures)
        for stage in ("initial", "final")}
    earliest_final_freeze = min(_time(frozen[(s, "final")][0]["created_utc"]) for s in structures)
    for entry in source_rows:
        structure, stage, seed = entry["structure"], entry["stage"], entry["seed"]
        _need(type(seed) is int, "Source seed must be an integer")
        name = f"candidates/{structure}_{stage}"
        report = verify_source_replay(bundle, entry["replay_id"], candidate=name)
        receipt, freeze_hash = frozen[(structure, stage)]
        _need(report["status"] == "success" and report["limits"]["seed"] == seed,
              "Source replay failed or uses the wrong seed")
        _need(report["parent"]["candidate"] == name and report["parent"]["freeze.json_sha256"] == freeze_hash,
              "Source replay is bound to the wrong candidate")
        source_time = _time(report["created_utc"])
        _need(_time(receipt["created_utc"]) <= source_time, "Source replay predates its candidate")
        if stage == "initial":
            _need(source_time <= earliest_final_freeze,
                  "Initial source feedback was not complete before final freeze")
        else:
            final_source_times.append(source_time)
        _need(report["contexts"] and all(c["generation_link_verified"] for c in report["contexts"]),
              "Source replay lacks generation linkage")
        for context in report["contexts"]:
            child = _path(context["child_bundle"], bundle / "source_replays" / entry["replay_id"])
            expected_child = bundle / "source_replays" / entry["replay_id"] / "contexts" / _name(context["id"]) / "bundle"
            _need(child == expected_child.resolve(strict=True), "Wrong source child bundle")
            execution = read_json(child / "executions/replay/execution.json")
            execution_time = _time(execution["created_utc"])
            _need(max(anchor_time, stage_freeze_times[stage]) <= execution_time <= source_time,
                  "Source execution predates protocol commitment/freeze or follows report")
        source_hashes.append(_digest(bundle / "source_replays" / entry["replay_id"] / "replay.json"))

    outputs = _rows(manifest["outputs"], {"structure", "seed", "path", "sha256", "run_id", "candidate_name"}, "outputs")
    output_keys = [(o["structure"], o["seed"]) for o in outputs]
    _need(len(output_keys) == len(set(output_keys)) and
          set(output_keys) == {(s, seed) for s in structures for seed in target_seeds},
          "Target output grid is incomplete or duplicated")
    run_ids = [_name(o["run_id"]) for o in outputs]
    _need(len(set(run_ids)) == len(run_ids), "Duplicate target execution artifact")
    release_ready = max([anchor_time, *final_source_times,
                         *[_time(frozen[(s, "final")][0]["created_utc"]) for s in structures]])
    output_paths = set()
    for entry in outputs:
        _need(type(entry["seed"]) is int, "Target seed must be an integer")
        name = entry["structure"] + "_final"
        _need(entry["candidate_name"] == name, "Target output is not a final candidate")
        run = bundle / "executions" / entry["run_id"]
        output = _reference(entry, run / "output/generated.csv", base)
        _need(output not in output_paths, "Duplicate generated output file")
        output_paths.add(output)
        execution = verify_execution(bundle, entry["run_id"])
        _need(execution["status"] == "success" and execution["route"] == "generator.py" and
              execution["generator_executed"] is True, "Target execution is not a successful program run")
        _need(execution["candidate"] == "candidates/" + name and
              execution["candidate_freeze_sha256"] == frozen[(entry["structure"], "final")][1],
              "Target execution has the wrong candidate binding")
        _need(execution["limits"]["seed"] == entry["seed"], "Target execution uses the wrong seed")
        _need(execution["files"].get("output/generated.csv") == entry["sha256"],
              "Target output does not match execution receipt")
        _need(_time(execution["created_utc"]) >= release_ready,
              "Target generation began before all final freezes/source diagnostics")

    return {"status": "passed", "scope": "target_blind_artifact_and_schedule_release_guard",
            "structures": structures, "candidates_verified": len(candidates),
            "source_replays_verified": len(source_rows), "target_outputs_verified": len(outputs),
            "protocol_commitment_sha256": _digest(protocol_commitment_path),
            "protocol_sha256": _digest(here / "protocol.json"), "guard_sha256": _digest(self_path),
            "release_manifest_sha256": _digest(commitment_path), "source_replay_sha256": source_hashes,
            "target_outcomes_analyzed": False, "blinding": "procedural_not_OS_enforced",
            "chronology": "checked_recorded_UTC_timestamps_not_external_authentication"}
