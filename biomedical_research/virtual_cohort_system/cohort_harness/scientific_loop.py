"""Recorded external-Agent review and calibrated scientific-candidate promotion.

This adapter does not launch an LLM or isolate its tools. Requests, externally
supplied decisions, and actual calibration outputs are bound to immutable events.
Only generator execution is sandboxed by the existing adapters. Promotions are
development candidates, not approved target releases or biomedical validation.
"""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import json

from . import calibration as cal, calibration_budget as budget, lifecycle
from .contracts import _hash, exact_keys, require, string_list, text, validate_task
from .lifecycle import _bundle, _candidate, _files, _path, read_json, sha256, verify_candidate

DIRECTORY = "scientific_loop"
CHOICES = {"retain_structure", "revise_structure", "stop", "request_evidence"}


def _engines():
    return {"scientific_loop": sha256(__file__), **cal._engines()}


def _config(value):
    exact_keys(value, {"max_actions", "max_promotions"}, where="scientific loop config")
    for name, number in value.items():
        require(type(number) is int and 1 <= number <= 100, "Invalid " + name)
    require(value["max_promotions"] <= value["max_actions"], "Promotions cannot exceed actions")


def _name(value):
    return cal.execution._name(value)


def _write(path, value):
    cal.execution._write(path, value)


def _payload_size(value):
    require(len(budget._canonical(value)) <= budget._MAX_FILE_BYTES - 2048,
            "Scientific loop payload exceeds event byte limit")


def _source_state(root, candidate, session_id):
    candidate, relative = _candidate(root, candidate)
    frozen = verify_candidate(root, candidate)
    result = cal.verify_calibration(root, session_id)
    require(result["binding"]["candidate"] == relative, "Review calibration belongs to another candidate")
    session = _path(root, "cal/" + _name(session_id), file=False)
    binding = {"candidate": relative, "freeze_sha256": sha256(candidate / "freeze.json"),
        "calibration_session_id": session_id,
        "calibration_result_sha256": sha256(session / "result.json"),
        "calibration_plan_sha256": sha256(session / "plan.json"),
        "calibration_selection_sha256": sha256(session / "selection.json")}
    # A fixed registered prefix permits legitimate later append-only admissions.
    manifest = {"committed_files": copy.deepcopy(frozen["commitments"]),
        "registry_prefix": copy.deepcopy(frozen["registry_snapshot"]),
        "scope": "permitted_source_candidate_and_covariates_only",
        "agent_access_isolation": "procedural_not_os_enforced"}
    return candidate, frozen, result, binding, manifest


def _decision(value, candidate, plan):
    exact_keys(value, {"choice", "rationale", "evidence_ids", "addressed_constraints", "remaining_limits"},
               where="scientific decision")
    require(value["choice"] in CHOICES, "Unsupported scientific decision")
    text(value["rationale"], "decision rationale")
    require(len(value["rationale"]) <= 50_000, "Decision rationale exceeds limit")
    for field in ("evidence_ids", "addressed_constraints", "remaining_limits"):
        string_list(value[field], field)
        require(len(value[field]) <= 1000, "Decision list exceeds limit")
    evidence = {item["id"] for item in read_json(candidate / "evidence.json")["items"]}
    constraints = {c["context_id"] + "/" + c["check_id"] for c in plan["constraints"]}
    require(set(value["evidence_ids"]) <= evidence, "Decision cites an unknown evidence ID")
    require(set(value["addressed_constraints"]) <= constraints, "Decision cites an unknown source constraint")
    _payload_size(value)


def _location(bundle):
    root = _bundle(bundle)
    directory = _path(root, DIRECTORY, file=False)
    require(directory.is_dir(), "Create the fixed scientific loop first")
    return root, directory


def _load(root, directory):
    require({p.name for p in directory.iterdir()} == {"config.json", "head.json", "events", ".operation.lock"},
            "Loop inventory changed or initialization was interrupted")
    config, config_hash = budget._read_envelope(directory, "config.json")
    exact_keys(config, {"schema_version", "kind", "task_sha256", "limits", "engines"}, where="loop config")
    require(type(config["schema_version"]) is int and config["schema_version"] == 1 and
            config["kind"] == "recorded_scientific_loop", "Invalid scientific loop identity")
    require(config["task_sha256"] == sha256(_path(root, "task.json")), "Loop task changed")
    require(config["engines"] == _engines(), "Scientific loop engine changed")
    _config(config["limits"])
    head, _ = budget._read_envelope(directory, "head.json")
    exact_keys(head, {"config_sha256", "event_count", "last_event_sha256"}, where="loop head")
    require(head["config_sha256"] == config_hash, "Loop configuration binding changed")
    require(type(head["event_count"]) is int and 0 <= head["event_count"] <= 400, "Invalid event count")
    events = _path(directory, "events", file=False)
    files = sorted(events.iterdir())
    require(len(files) == head["event_count"], "Loop event inventory differs from head")
    actions, pending, stopped, promotions, previous = {}, None, False, 0, config_hash
    for index, path in enumerate(files, 1):
        require(path.name == f"{index:08d}.json", "Loop events must be contiguous")
        event, digest = budget._read_envelope(events, path.name)
        exact_keys(event, {"schema_version", "sequence", "previous_sha256", "config_sha256", "created_utc",
                           "kind", "action_id", "payload"}, where="loop event")
        require(type(event["schema_version"]) is int and event["schema_version"] == 1 and
                type(event["sequence"]) is int and event["sequence"] == index, "Invalid loop event sequence")
        require(event["previous_sha256"] == previous and event["config_sha256"] == config_hash,
                "Loop event chain changed")
        text(event["created_utc"], "event time")
        action_id, payload = _name(event["action_id"]), event["payload"]
        kind = event["kind"]
        if kind == "request":
            require(not stopped and pending is None, "Request occurs while loop unavailable")
            require(action_id.casefold() not in {x.casefold() for x in actions}, "Action ID reused")
            require(len(actions) < config["limits"]["max_actions"], "Global action limit exceeded")
            exact_keys(payload, {"prompt", "actor", "binding", "revealed_source_manifest"}, where="review request")
            for field in ("prompt", "actor"):
                text(payload[field], field)
            actions[action_id] = {"status": "awaiting_decision", "request": payload,
                                  "request_sha256": digest}
            pending = {"kind": "decision", "action_id": action_id}
        elif kind == "decision":
            require(pending == {"kind": "decision", "action_id": action_id}, "Decision lacks pending request")
            action = actions[action_id]
            exact_keys(payload, {"request_sha256", "decision"}, where="recorded decision")
            require(payload["request_sha256"] == action["request_sha256"], "Decision request changed")
            require(payload["decision"].get("choice") in CHOICES, "Invalid recorded choice")
            action.update(status="decided", decision=payload["decision"], decision_sha256=digest)
            pending = None
            stopped = payload["decision"]["choice"] == "stop"
        elif kind == "promotion_start":
            require(not stopped and pending is None and action_id == list(actions)[-1], "Promotion is out of order")
            action = actions[action_id]
            require(action["status"] == "decided" and action["decision"]["choice"] == "retain_structure",
                    "Promotion requires an unpromoted retain_structure decision")
            require(promotions < config["limits"]["max_promotions"], "Global promotion limit exceeded")
            exact_keys(payload, {"new_candidate", "decision_sha256", "owner"}, where="promotion reservation")
            require(payload["decision_sha256"] == action["decision_sha256"], "Promotion decision changed")
            budget._check_owner(payload["owner"])
            require(payload["new_candidate"].startswith("candidates/"), "Invalid promoted candidate path")
            _name(payload["new_candidate"].removeprefix("candidates/"))
            promotions += 1
            action.update(status="promotion_pending", promotion=payload, promotion_start_sha256=digest)
            pending = {"kind": "promotion", "action_id": action_id}
        elif kind == "promotion_finish":
            require(pending == {"kind": "promotion", "action_id": action_id}, "Promotion finish lacks reservation")
            action = actions[action_id]
            exact_keys(payload, {"promotion_start_sha256", "freeze_sha256"}, where="promotion finish")
            require(payload["promotion_start_sha256"] == action["promotion_start_sha256"], "Promotion reservation changed")
            _hash(payload["freeze_sha256"])
            action.update(status="promoted", promoted_freeze_sha256=payload["freeze_sha256"], promotion_finish_sha256=digest)
            pending = None
        else:
            raise ValueError("Unsupported scientific loop event")
        previous = digest
    require(head["last_event_sha256"] == previous, "Loop head changed")
    return {"config": config, "config_sha256": config_hash, "event_count": len(files),
            "last_event_sha256": previous, "actions": actions, "pending": pending, "stopped": stopped,
            "usage": {"actions": len(actions), "promotions": promotions}}


def _append(directory, state, kind, action_id, payload):
    index = state["event_count"] + 1
    event = budget._envelope({"schema_version": 1, "sequence": index,
        "previous_sha256": state["last_event_sha256"], "config_sha256": state["config_sha256"],
        "created_utc": datetime.now(timezone.utc).isoformat(), "kind": kind, "action_id": action_id, "payload": payload})
    budget._write_atomic(_path(directory, "events", file=False), f"{index:08d}.json", event)
    budget._write_atomic(directory, "head.json", budget._envelope({"config_sha256": state["config_sha256"],
        "event_count": index, "last_event_sha256": event["sha256"]}), replace=True)


def create_loop(bundle, config):
    """Create once. Replacing/resetting an existing loop is forbidden."""
    _config(config)
    root = _bundle(bundle)
    validate_task(read_json(_path(root, "task.json")))
    directory = _path(root, DIRECTORY, file=False)
    require(not directory.exists(), "Scientific loop already exists; reset is forbidden")
    directory.mkdir()
    with budget._operation(directory, "loop_create") as guard:
        guard["dirty"] = True
        directory.joinpath("events").mkdir()
        envelope = budget._envelope({"schema_version": 1, "kind": "recorded_scientific_loop",
            "task_sha256": sha256(_path(root, "task.json")), "limits": copy.deepcopy(config), "engines": _engines()})
        budget._write_atomic(directory, "config.json", envelope)
        budget._write_atomic(directory, "head.json", budget._envelope({"config_sha256": envelope["sha256"],
            "event_count": 0, "last_event_sha256": envelope["sha256"]}))
        return _load(root, directory)


def request_review(bundle, action_id, candidate, calibration_session_id, prompt, actor):
    """Record the exact request before the calling environment dispatches the LLM."""
    root, directory = _location(bundle)
    action_id = _name(action_id)
    for field, value, maximum in (("prompt", prompt, 60_000), ("actor", actor, 1000)):
        text(value, field)
        require(len(value) <= maximum, field + " exceeds limit")
    _, _, _, binding, manifest = _source_state(root, candidate, calibration_session_id)
    payload = {"prompt": prompt, "actor": actor, "binding": binding, "revealed_source_manifest": manifest}
    _payload_size(payload)
    with budget._operation(directory, "loop_request") as guard:
        state = _load(root, directory)
        require(not state["stopped"] and state["pending"] is None, "Loop is stopped or has a pending action")
        require(action_id.casefold() not in {x.casefold() for x in state["actions"]}, "Action ID already used")
        require(state["usage"]["actions"] < state["config"]["limits"]["max_actions"], "Global action budget exhausted")
        guard["dirty"] = True
        _append(directory, state, "request", action_id, payload)
        return _load(root, directory)["actions"][action_id]


def _check_action(root, action):
    request = action["request"]
    b = request["binding"]
    candidate, frozen, result, binding, manifest = _source_state(root, b["candidate"], b["calibration_session_id"])
    require(binding == b and manifest == request["revealed_source_manifest"], "Revealed review inputs changed")
    if "decision" in action:
        plan = read_json(root / "cal" / b["calibration_session_id"] / "plan.json")
        _decision(action["decision"], candidate, plan)
    return candidate, frozen, result


def record_decision(bundle, action_id, decision):
    """Ingest a real external response; this validates references, not its reasoning."""
    root, directory = _location(bundle)
    action_id = _name(action_id)
    with budget._operation(directory, "loop_decision") as guard:
        state = _load(root, directory)
        require(state["pending"] == {"kind": "decision", "action_id": action_id}, "No matching pending review")
        action = state["actions"][action_id]
        candidate, _, _ = _check_action(root, action)
        plan = read_json(root / "cal" / action["request"]["binding"]["calibration_session_id"] / "plan.json")
        _decision(decision, candidate, plan)
        guard["dirty"] = True
        _append(directory, state, "decision", action_id,
                {"request_sha256": action["request_sha256"], "decision": copy.deepcopy(decision)})
        return _load(root, directory)["actions"][action_id]


def _promotion_material(root, action_id, action, candidate, result):
    session_id = action["request"]["binding"]["calibration_session_id"]
    selected = result["selected_trial"]
    require(selected is not None and result["trials"][selected]["fit"]["feasible"] and
            result["replay"] is not None and result["replay"]["feasible"],
            "Promotion requires feasible selected fit and independent-seed replay")
    selected_dir = root / "cal" / session_id / ("t%04d" % selected) / "candidates/t"
    source_result = root / "cal" / session_id / "result.json"
    provenance = {"schema_version": 1, "kind": "scientific_candidate_promotion", "action_id": action_id,
        "request_sha256": action["request_sha256"], "decision_sha256": action["decision_sha256"],
        "parent_binding": action["request"]["binding"], "selected_trial": selected,
        "selected_freeze_sha256": sha256(selected_dir / "freeze.json"),
        "generator_sha256": sha256(selected_dir / "generator.py"), "model_spec_sha256": sha256(selected_dir / "model_spec.json"),
        "calibration_status": result["status"], "fit_loss": result["trials"][selected]["fit"]["loss"],
        "replay_loss": result["replay"]["loss"], "scope": "source_checked_development_candidate_not_target_release"}
    prefix = "scientific_review/"
    require(not any(name == "calibration_provenance.json" or name.startswith(prefix) for name in _files(candidate)),
            "Reserved promotion artifacts already exist; prepare a fresh scientific submission")
    feedback = {"calibration_result.json": source_result.read_bytes(),
                "request.json": (json.dumps(action["request"], indent=2, allow_nan=False) + "\n").encode(),
                "decision.json": (json.dumps(action["decision"], indent=2, allow_nan=False) + "\n").encode(),
                "parent_checks.json": (candidate / "checks.json").read_bytes(),
                "parent_decision.md": (candidate / "decision.md").read_bytes()}
    artifacts = [{"path": prefix + name, "sha256": hashlib.sha256(data).hexdigest()} for name, data in feedback.items()]
    checks = {"scope": "source_only", "records": [
        {"name": "verified_calibration", "status": "pass", "detail": "Verified source-only calibration provenance and all retained trial outcomes; this is not target validation."},
        {"name": "source_fit_criterion", "status": "pass" if result["status"] == "fit_threshold_met" else "fail",
         "detail": "Recorded calibration fit status: " + result["status"]},
        {"name": "external_agent_review", "status": "pass", "detail": "Recorded referenced retain_structure decision; scientific correctness is not automatically certified."}],
        "artifacts": artifacts}
    decision_text = ("External scientific review: retain_structure\n\n" + action["decision"]["rationale"] +
        "\n\nSelected numerical trial promoted with exact program/specification bytes. This is a source-checked development candidate, not a target release.\n\nRemaining limitations:\n" +
        "\n".join("- " + s for s in action["decision"]["remaining_limits"]) + "\n")
    return selected_dir, provenance, feedback, checks, decision_text


def _promotion_revision(action, candidate, destination):
    changed = any(sha256(destination / n) != sha256(candidate / n) for n in ("generator.py", "model_spec.json"))
    return {"kind": "revise" if changed else "retain", "reason": action["decision"]["rationale"],
            "addressed_findings": action["decision"]["addressed_constraints"],
            "remaining_limitations": action["decision"]["remaining_limits"]}


def promote(bundle, action_id, new_name):
    root, directory = _location(bundle)
    action_id, new_name = _name(action_id), _name(new_name)
    new_relative = "candidates/" + new_name
    destination = _path(root, new_relative, file=False)
    with budget._operation(directory, "loop_promote_reserve") as guard:
        state = _load(root, directory)
        require(not state["stopped"] and state["pending"] is None and bool(state["actions"]) and
                action_id == list(state["actions"])[-1], "Promotion must use the latest completed review")
        action = state["actions"][action_id]
        require(action["status"] == "decided" and action["decision"]["choice"] == "retain_structure",
                "Only retain_structure decisions can promote selected numeric trials")
        require(state["usage"]["promotions"] < state["config"]["limits"]["max_promotions"], "Global promotion budget exhausted")
        require(not destination.exists(), "Promoted candidate destination already exists")
        candidate, frozen, result = _check_action(root, action)
        require(frozen["revision_index"] < read_json(root / "task.json")["budget"]["revisions"], "Scientific revision budget exhausted")
        material = _promotion_material(root, action_id, action, candidate, result)
        guard["dirty"] = True
        _append(directory, state, "promotion_start", action_id, {"new_candidate": new_relative,
            "decision_sha256": action["decision_sha256"], "owner": budget._owner()})
        action = _load(root, directory)["actions"][action_id]
    # Reservation is durable before the first candidate file is created.
    selected_dir, provenance, feedback, checks, decision_text = material
    destination.mkdir()
    for name in cal.replay.legacy._candidate_bindings(frozen):
        if name in {"generator.py", "model_spec.json", "checks.json", "decision.md"}:
            continue
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(_path(candidate, name).read_bytes())
    for name in ("generator.py", "model_spec.json"):
        (destination / name).write_bytes((selected_dir / name).read_bytes())
    destination.joinpath("scientific_review").mkdir()
    for name, data in feedback.items():
        (destination / "scientific_review" / name).write_bytes(data)
    _write(destination / "calibration_provenance.json", provenance)
    _write(destination / "checks.json", checks)
    (destination / "decision.md").write_text(decision_text, encoding="utf-8", newline="\n")
    revision = _promotion_revision(action, candidate, destination)
    lifecycle.freeze_candidate(root, destination, parent_receipt=frozen, revision=revision)
    _check_action(root, action)
    _verify_promotion(root, action_id, action, candidate, frozen, result, require_finished=False)
    with budget._operation(directory, "loop_promote_finish") as guard:
        state = _load(root, directory)
        current = state["actions"][action_id]
        require(state["pending"] == {"kind": "promotion", "action_id": action_id} and
                current["promotion"]["owner"] == budget._owner(), "Interrupted promotion cannot resume")
        guard["dirty"] = True
        _append(directory, state, "promotion_finish", action_id, {"promotion_start_sha256": current["promotion_start_sha256"],
                                                                "freeze_sha256": sha256(destination / "freeze.json")})
    return verify_loop(root)["actions"][action_id]


def _verify_promotion(root, action_id, action, candidate, frozen, result, *, require_finished=True):
    directory, relative = _candidate(root, action["promotion"]["new_candidate"])
    actual = verify_candidate(root, directory)
    require(actual["parent"] == {"candidate": frozen["candidate"], "receipt_path": frozen["candidate"] + "/freeze.json",
                                 "sha256": sha256(candidate / "freeze.json")}, "Promoted lineage changed")
    require(actual["revision"] == _promotion_revision(action, candidate, directory),
            "Promoted revision annotations differ from the Agent decision")
    if require_finished:
        require(sha256(directory / "freeze.json") == action["promoted_freeze_sha256"], "Promoted freeze changed")
    selected, provenance, feedback, checks, decision_text = _promotion_material(root, action_id, action, candidate, result)
    for name in ("generator.py", "model_spec.json"):
        require((directory / name).read_bytes() == (selected / name).read_bytes(), "Promoted program/spec is not the selected trial")
    require(read_json(directory / "calibration_provenance.json") == provenance, "Promotion provenance changed")
    require(read_json(directory / "checks.json") == checks, "Promotion source checks changed")
    require((directory / "decision.md").read_text(encoding="utf-8") == decision_text, "Promotion decision text changed")
    expected = set(cal.replay.legacy._candidate_bindings(frozen)) | {"calibration_provenance.json"} | {
        "scientific_review/" + name for name in feedback}
    require(set(_files(directory)) == expected, "Promoted artifact inventory changed")
    for name, data in feedback.items():
        require((directory / "scientific_review" / name).read_bytes() == data, "Promotion feedback bytes changed")
    for name, digest in cal.replay.legacy._candidate_bindings(frozen).items():
        if name not in {"generator.py", "model_spec.json", "checks.json", "decision.md"}:
            require(sha256(directory / name) == digest, "Promotion changed scientific input bytes")


def verify_loop(bundle):
    root, directory = _location(bundle)
    with budget._operation(directory, "loop_verify"):
        state = _load(root, directory)
        for action_id, action in state["actions"].items():
            candidate, frozen, result = _check_action(root, action)
            if action["status"] == "promoted":
                _verify_promotion(root, action_id, action, candidate, frozen, result)
        return state
