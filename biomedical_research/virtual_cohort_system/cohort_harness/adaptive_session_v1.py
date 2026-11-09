"""Host-dispatched adaptive author session; no model client or Agent-wide sandbox.

The author chooses actions. This controller executes the supplied adapters,
reserves allowances before dispatch, and preserves versions and failures.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import types

from . import calibration_budget as ledger
from . import execution, lifecycle as lc, literature, semantic_feedback_v1 as semantic
from .contracts import ContractError, _hash, exact_keys, require, text, validate_task

DIRECTORY = "adaptive_session_v1"
COUNTERS = {"actions", "candidates", "executions", "feedbacks", "analyses"}
CHARGES = {"submit": "candidates", "execute": "executions", "feedback": "feedbacks", "analysis": "analyses"}
MAX_RESULT_BYTES = 24 * 1024 * 1024
SCOPE = "Declared-source diagnostic contrast on task output; no source-population reconstruction or target validation."


def _name(value):
    execution._name(value)
    lc.safe_relative(value)
    return value


def _candidate(value):
    text(value, "candidate")
    if "/" not in value:
        value = "candidates/" + value
    parts = lc.safe_relative(value)
    require(len(parts) == 2 and parts[0] == "candidates", "Use candidates/NAME")
    _name(parts[1])
    return value


def _host_file(value):
    path = Path(value)
    require(path.is_absolute() and ".." not in path.parts, "Host adapter paths must be absolute")
    require(path.is_file(), "Host adapter file is missing")
    require(not any(lc._link(p) for p in (path, *path.parents)), "Host adapter links are not accepted")
    return path


def _config(value):
    exact_keys(value, {"schema_version", "limits", "allowed_seeds", "runtime", "execution_limits",
                       "analysis_adapters"}, where="adaptive config")
    require(type(value["schema_version"]) is int and value["schema_version"] == 1, "Config version must be 1")
    exact_keys(value["limits"], COUNTERS, where="limits")
    for key, count in value["limits"].items():
        require(type(count) is int and 0 <= count <= 1000, "Invalid allowance: " + key)
    require(value["limits"]["actions"] > 0, "A positive action allowance is required")
    seeds = value["allowed_seeds"]
    require(isinstance(seeds, list) and bool(seeds), "Declare scheduled seeds")
    require(all(type(s) is int and 0 <= s < 2**32 for s in seeds) and len(seeds) == len(set(seeds)),
            "Seeds must be unique uint32 integers")
    exact_keys(value["execution_limits"], {"timeout_seconds", "memory_mb", "output_bytes", "log_bytes"},
               where="execution limits")
    execution._limits(**value["execution_limits"], seed=seeds[0])
    if value["runtime"] is not None:
        execution._runtime(value["runtime"])
    require(isinstance(value["analysis_adapters"], dict), "analysis_adapters must be a mapping")
    for name, adapter in value["analysis_adapters"].items():
        _name(name)
        exact_keys(adapter, {"path", "function", "sha256"}, {"dependencies"}, where="host analysis adapter")
        require(isinstance(adapter["function"], str) and adapter["function"].isidentifier(), "Invalid function")
        require(Path(adapter["path"]).suffix == ".py", "Analysis adapter must be Python source")
        dependencies = adapter.get("dependencies", {})
        require(isinstance(dependencies, dict), "Adapter dependencies must map paths to hashes")
        for path, expected in {**dependencies, adapter["path"]: adapter["sha256"]}.items():
            _hash(expected)
            require(lc.sha256(_host_file(path)) == expected, "Host analysis adapter/dependency changed")
    return value


def _engines():
    names = ["adaptive_session_v1.py", "calibration_budget.py", "contracts.py", "lifecycle.py", "execution.py",
             "_worker.py", "literature.py", "_vendor/literature_gateway.py", "semantic_feedback_v1.py",
             "whole_cohort_feedback.py", "source_checks.py", "source_replay.py"]
    return {name: lc.sha256(Path(__file__).parent / name) for name in names}


def _gateway(root):
    folder = lc._path(root, "gateway", file=False)
    if not folder.exists():
        return {}
    return {"gateway/" + name: lc.sha256(lc._path(folder, name)) for name in lc._files(folder)}


def _inputs(root):
    names = ["task.json", "request.json"]
    for name in ("observed.csv", "AUTHOR_TASK.md", "SETUP_NOTES.md", "adapters.json"):
        if lc._path(root, name, file=False).exists():
            names.append(name)
    for namespace in ("input", "skills"):
        folder = lc._path(root, namespace, file=False)
        if folder.exists():
            require(folder.is_dir(), "Static context namespace must be a directory")
            names.extend(namespace + "/" + name for name in lc._files(folder))
    return {name: lc.sha256(lc._path(root, name)) for name in sorted(names)}


def _action(value):
    require(isinstance(value, dict), "Action must be an object")
    kind = value.get("kind")
    fields = {
        "literature": ({"action"}, {"query", "limit", "cursor", "pmcid", "version", "supplement_id"}),
        "preflight": ({"candidate"}, set()),
        "submit": ({"candidate"}, {"parent", "revision"}),
        "execute": ({"candidate", "run_id", "seed"}, set()),
        "feedback": ({"candidate", "run_id", "feedback_id"}, set()),
        "analysis": ({"candidate", "run_id", "adapter", "analysis_id"}, set()),
        "finish": ({"final_candidate", "reason"}, set()),
    }
    require(isinstance(kind, str) and kind in fields, "Unknown adaptive action")
    required, optional = fields[kind]
    exact_keys(value, {"kind"} | required, optional, where="action")
    value = json.loads(ledger._canonical(value))
    for key in ("candidate", "parent", "final_candidate"):
        if key in value and value[key] is not None:
            value[key] = _candidate(value[key])
    for key in ("run_id", "feedback_id", "adapter", "analysis_id"):
        if key in value:
            _name(value[key])
    if kind == "literature":
        require(value["action"] in literature.ACTIONS, "Unknown literature action")
    if kind == "finish":
        text(value["reason"], "finish reason")
    return value


def _append(directory, state, kind, action_id, payload):
    index = state["event_count"] + 1
    event = ledger._envelope({"sequence": index, "previous_sha256": state["last_event_sha256"],
        "config_sha256": state["config_sha256"], "created_utc": datetime.now(timezone.utc).isoformat(),
        "kind": kind, "action_id": action_id, "payload": payload})
    ledger._write_atomic(directory / "events", f"{index:08d}.json", event)
    ledger._write_atomic(directory, "head.json", ledger._envelope({"config_sha256": state["config_sha256"],
        "event_count": index, "last_event_sha256": event["sha256"]}), replace=True)
    state.update(event_count=index, last_event_sha256=event["sha256"])


def _load(root, directory):
    require({p.name for p in directory.iterdir()} == {"config.json", "head.json", "events", "results",
                                                      ".operation.lock"}, "Session inventory changed")
    config, config_hash = ledger._read_envelope(directory, "config.json")
    require(config["bundle"] == str(root), "Session bundle moved")
    require(config["engines"] == _engines(), "Session engine changed")
    _config(config["settings"])
    for name, expected in config["inputs"].items():
        require(lc.sha256(lc._path(root, name)) == expected, "Session input changed: " + name)
    require(_inputs(root) == config["inputs"], "Static scientific context inventory changed")
    head, _ = ledger._read_envelope(directory, "head.json")
    require(head["config_sha256"] == config_hash, "Session configuration changed")
    state = {"config": config, "config_sha256": config_hash, "event_count": 0,
             "last_event_sha256": config_hash, "usage": {key: 0 for key in COUNTERS},
             "status": "active", "pending": None, "actions": {}, "candidates": [], "seed_slots": []}
    files = sorted((directory / "events").iterdir())
    require(len(files) == head["event_count"], "Session event inventory differs from head")
    registry = config["registry"]
    gateway = config["gateway"]
    expected_results = set()
    for index, path in enumerate(files, 1):
        require(path.name == f"{index:08d}.json", "Session events are not contiguous")
        event, digest = ledger._read_envelope(directory / "events", path.name)
        require(event["sequence"] == index and event["previous_sha256"] == state["last_event_sha256"]
                and event["config_sha256"] == config_hash, "Session event chain changed")
        action_id, payload = _name(event["action_id"]), event["payload"]
        if event["kind"] == "reserve":
            require(state["pending"] is None and state["status"] == "active", "Action follows unavailable session")
            require(action_id.casefold() not in {x.casefold() for x in state["actions"]}, "Action ID reused")
            action = _action(payload)
            _reserve_checks(state, action)
            state["usage"]["actions"] += 1
            if action["kind"] in CHARGES:
                state["usage"][CHARGES[action["kind"]]] += 1
            if action["kind"] == "execute":
                state["seed_slots"].append([action["candidate"], action["seed"]])
            state["actions"][action_id] = {"action": action}
            state["pending"] = action_id
        elif event["kind"] == "result":
            require(state["pending"] == action_id, "Result lacks matching reservation")
            entry = state["actions"][action_id]
            result_name = action_id + ".json"
            expected_results.add(result_name)
            result_path = lc._path(directory / "results", result_name)
            require(lc.sha256(result_path) == payload["result_sha256"], "Action result changed")
            result = lc.read_json(result_path)
            require(result["action_id"] == action_id and result["status"] == payload["status"]
                    and result["session_status"] == payload["session_status"], "Action result identity changed")
            for name, expected in payload["artifacts"].items():
                require(lc.sha256(lc._path(root, name)) == expected, "Action artifact changed: " + name)
            require(lc._registry(root, registry["artifact_count"])[0] == registry, "Registry prefix changed")
            new_registry = payload["registry"]
            if entry["action"]["kind"] != "literature":
                require(new_registry == registry, "Only literature actions may append evidence")
                require(payload["gateway"] == gateway, "Gateway changed outside literature action")
            require(new_registry["artifact_count"] >= registry["artifact_count"], "Registry shrank")
            registry = new_registry
            gateway = payload["gateway"]
            entry.update(result=result, receipt=payload)
            if entry["action"]["kind"] == "submit" and result["status"] == "success":
                state["candidates"].append(entry["action"]["candidate"])
            state.update(pending=None, status=result["session_status"])
        else:
            raise ContractError("Unknown session event")
        state.update(event_count=index, last_event_sha256=digest)
    require(head["last_event_sha256"] == state["last_event_sha256"], "Session head changed")
    require({p.name for p in (directory / "results").iterdir()} == expected_results, "Result inventory changed")
    require(lc._registry(root)[0] == registry, "Evidence changed outside a recorded literature action")
    require(_gateway(root) == gateway, "Gateway bytes changed outside a recorded action")
    for candidate in state["candidates"]:
        lc.verify_candidate(root, candidate)
    state["registry"] = registry
    state["gateway"] = gateway
    return state


def _reserve_checks(state, action):
    settings, usage = state["config"]["settings"], state["usage"]
    require(usage["actions"] < settings["limits"]["actions"], "Action allowance exhausted")
    kind = action["kind"]
    if kind in CHARGES:
        counter = CHARGES[kind]
        require(usage[counter] < settings["limits"][counter], counter + " allowance exhausted")
    if kind in {"execute", "feedback", "analysis"}:
        require(action["candidate"] in state["candidates"], "Candidate was not submitted through this session")
    if kind == "submit":
        require(action["candidate"] not in state["candidates"], "Candidate already submitted")
        parent = state["candidates"][-1] if state["candidates"] else None
        require(action.get("parent") == parent, "Submit must extend the latest accepted candidate")
        require((parent is not None) == (action.get("revision") is not None), "Revision record must match lineage")
    if kind == "execute":
        require(type(action["seed"]) is int and action["seed"] in settings["allowed_seeds"], "Seed is not scheduled")
        require([action["candidate"], action["seed"]] not in state["seed_slots"], "Candidate/seed already attempted")
        require(not any(e["action"].get("run_id") == action["run_id"] and e["action"]["kind"] == "execute"
                        for e in state["actions"].values()), "Execution ID already attempted")
    if kind in {"feedback", "analysis"}:
        runs = [e for e in state["actions"].values() if e["action"]["kind"] == "execute"
                and e["action"]["run_id"] == action["run_id"] and e["action"]["candidate"] == action["candidate"]]
        require(len(runs) == 1 and runs[0].get("result", {}).get("status") == "success", "Requires session-successful execution")
    if kind == "analysis":
        require(action["adapter"] in settings["analysis_adapters"], "Analysis adapter is not host-allowlisted")
    for unique_field in ("feedback_id", "analysis_id"):
        if unique_field in action:
            require(not any(e["action"].get(unique_field, "").casefold() == action[unique_field].casefold()
                            for e in state["actions"].values()), unique_field + " already attempted")
    if kind == "finish" and action["final_candidate"] is not None:
        require(action["final_candidate"] in state["candidates"], "Final candidate was not submitted")
        for candidate, seed in ((c, s) for c in state["candidates"] for s in settings["allowed_seeds"]):
            runs = [e for e in state["actions"].values() if e["action"]["kind"] == "execute"
                    and e["action"]["candidate"] == candidate and e["action"]["seed"] == seed]
            require(len(runs) == 1, "Submitted candidate is missing a scheduled seed attempt: " + candidate)
            if runs[0].get("result", {}).get("status") != "success":
                continue
            run_id = runs[0]["action"]["run_id"]
            completed = [e["action"] for e in state["actions"].values() if e.get("result", {}).get("status") == "success"
                         and e["action"].get("run_id") == run_id and e["action"].get("candidate") == candidate]
            if state["config"]["mode"] == "whole_cohort":
                require(any(a["kind"] == "feedback" for a in completed), "Final run is missing semantic feedback")
            for adapter in settings["analysis_adapters"]:
                require(any(a["kind"] == "analysis" and a["adapter"] == adapter for a in completed),
                        "Final run is missing its host-approved analysis")
        require(any(e["action"]["kind"] == "execute" and e["action"]["candidate"] == action["final_candidate"]
                    and e.get("result", {}).get("status") == "success" for e in state["actions"].values()),
                "No successful final output; finish with final_candidate null to abandon")


def create_session(bundle, config):
    """Host-only setup. Existing sessions and historical run outputs cannot be adopted."""
    root = lc._bundle(bundle)
    settings = json.loads(ledger._canonical(_config(config)))
    task = lc.read_json(lc._path(root, "task.json"))
    validate_task(task)
    request = lc.read_json(lc._path(root, "request.json"))
    require(request.get("task") == task and bool(request.get("analyses")) and bool(request.get("purpose")),
            "A matching research request with visible analyses is required")
    for name in ("executions", "semantic_feedback_v1", DIRECTORY):
        require(not lc._path(root, name, file=False).exists(), "Use a fresh session bundle: " + name)
    candidates = lc._path(root, "candidates", file=False)
    require(not candidates.exists() or not list(candidates.glob("*/freeze.json")), "Cannot adopt old frozen candidates")
    if task["mode"] != "whole_cohort":
        lc._path(root, "observed.csv")
    else:
        require(not lc._path(root, "observed.csv", file=False).exists(), "Whole-cohort session forbids observed.csv")
    manifest = {"schema_version": 1, "kind": "host_dispatched_adaptive_session_v1", "bundle": str(root),
                "mode": task["mode"], "inputs": _inputs(root), "registry": lc._registry(root)[0], "gateway": _gateway(root), "settings": settings,
                "engines": _engines(), "source_feedback_scope": SCOPE, "agent_isolation": "not_provided",
                "model_dispatch": "external_host", "analysis_adapter_trust": "host-reviewed code; not sandboxed"}
    directory = root / DIRECTORY
    directory.mkdir()
    with ledger._operation(directory, "create") as guard:
        guard["dirty"] = True
        (directory / "events").mkdir()
        (directory / "results").mkdir()
        envelope = ledger._envelope(manifest)
        ledger._write_atomic(directory, "config.json", envelope)
        ledger._write_atomic(directory, "head.json", ledger._envelope({"config_sha256": envelope["sha256"],
            "event_count": 0, "last_event_sha256": envelope["sha256"]}))
        return _summary(_load(root, directory))


def _analysis(root, state, action):
    settings = state["config"]["settings"]
    adapter = settings["analysis_adapters"][action["adapter"]]
    _config(settings)
    receipt = execution.verify_execution(root, action["run_id"])
    require(receipt["candidate"] == action["candidate"] and receipt["status"] == "success", "Wrong analysis execution")
    raw = _host_file(adapter["path"]).read_bytes()
    module = types.ModuleType("adaptive_host_" + action["adapter"])
    module.__file__ = adapter["path"]
    exec(compile(raw, adapter["path"], "exec"), module.__dict__)
    function = getattr(module, adapter["function"])
    require(callable(function), "Host adapter entrypoint is not callable")
    result = function(root / f"executions/{action['run_id']}/output/generated.csv", root / "task.json", root / "request.json")
    require(isinstance(result, dict), "Analysis adapter must return a JSON object")
    require(len(ledger._canonical(result)) <= 2 * 1024 * 1024, "Analysis result exceeds 2 MiB")
    _config(settings)
    execution.verify_execution(root, action["run_id"])
    return {"kind": "generated_output_analysis", "analysis_id": action["analysis_id"], "adapter": action["adapter"],
            "candidate": action["candidate"], "run_id": action["run_id"], "reference_role": "none",
            "source_population_replay": False, "result": result}


def _verify_execution(root, state, action):
    """Check trusted staging for failed receipts too, without changing the old verifier."""
    receipt = execution.verify_execution(root, action["run_id"])
    settings = state["config"]["settings"]
    run = root / "executions" / action["run_id"]
    require(receipt["candidate"] == action["candidate"], "Execution candidate identity changed")
    submission = next(e for e in state["actions"].values() if e["action"]["kind"] == "submit"
                      and e["action"]["candidate"] == action["candidate"] and e.get("result", {}).get("status") == "success")
    expected_freeze = submission["receipt"]["artifacts"][action["candidate"] + "/freeze.json"]
    require(receipt["candidate_freeze_sha256"] == expected_freeze, "Execution differs from submitted freeze")
    require(receipt["limits"] == {**settings["execution_limits"], "seed": action["seed"]}, "Execution allowance changed")
    task = lc.read_json(root / "task.json")
    request = lc.read_json(lc._path(run, "input/request.json"))
    require(request == {"schema_version": 1, **receipt["limits"], "task_id": task["task_id"]}, "Staged request identity changed")
    expected_inputs = {"task.json", "model_spec.json", receipt["route"]}
    if task["mode"] != "whole_cohort":
        expected_inputs.add("observed.csv")
    require(set(lc.read_json(run / "input_bindings.json")["files"]) == expected_inputs, "Staged input inventory changed")
    actual_inputs = set(lc._files(run / "input"))
    require(expected_inputs | {"request.json"} <= actual_inputs <= expected_inputs | {"request.json", "worker.py"},
            "Unexpected staged input artifact")
    require(set(lc._files(run / "output")) <= {"generated.csv", "worker_report.json"}, "Unexpected execution output")
    if receipt["route"] == "generator.py":
        require(receipt["runtime"] == settings["runtime"], "Program runtime identity changed")
        worker = run / "input/worker.py"
        if worker.exists():
            require(lc.sha256(worker) == state["config"]["engines"]["_worker.py"], "Staged trusted worker changed")
        launch_path = run / "launch.json"
        if launch_path.exists():
            launch = lc.read_json(launch_path)
            require(launch == {"argv": execution._command(settings["runtime"], run, receipt["limits"]["timeout_seconds"]),
                               "runtime": settings["runtime"], "worker_sha256": state["config"]["engines"]["_worker.py"],
                               "isolation": "curated_bubblewrap_mounts_no_network", "authentication": "not_a_signature"},
                    "Execution launch identity changed")
        if receipt.get("process") is not None:
            require(worker.is_file() and launch_path.is_file(), "Launched program lacks trusted staging")
    return receipt


def _disposition(state):
    """Keep skipped schedules explicit even for a deliberate abandonment."""
    stages = []
    for candidate in state["candidates"]:
        runs = []
        for seed in state["config"]["settings"]["allowed_seeds"]:
            match = next((e for e in state["actions"].values() if e["action"]["kind"] == "execute"
                          and e["action"]["candidate"] == candidate and e["action"]["seed"] == seed), None)
            run_id = match["action"]["run_id"] if match else None
            diagnostics = [{"kind": e["action"]["kind"], "status": e.get("result", {}).get("status", "pending"),
                            "adapter": e["action"].get("adapter")} for e in state["actions"].values()
                           if run_id is not None and e["action"].get("run_id") == run_id
                           and e["action"]["kind"] in {"feedback", "analysis"}]
            runs.append({"seed": seed, "run_id": run_id,
                         "status": match.get("result", {}).get("status", "pending") if match else "not_attempted",
                         "diagnostics": diagnostics})
        stages.append({"candidate": candidate, "runs": runs})
    return stages


def _invoke(root, state, action):
    kind, settings = action["kind"], state["config"]["settings"]
    if kind == "literature":
        return literature.run_literature(root, **{k: v for k, v in action.items() if k != "kind"})
    if kind in {"preflight", "submit"}:
        require(state["config"]["mode"] == "whole_cohort" or kind == "submit", "Semantic preflight supports whole-cohort only")
        if state["config"]["mode"] == "whole_cohort":
            preflight = semantic.preflight(root, action["candidate"])
        else:
            preflight = {"status": "not_available", "reason": "No source-feedback adapter selected for this mode"}
        if kind == "preflight":
            return preflight
        frozen = lc.freeze_candidate(root, action["candidate"], parent_receipt=(
            root / action["parent"] / "freeze.json") if action.get("parent") else None, revision=action.get("revision"))
        return {"preflight": preflight, "freeze": lc.verify_candidate(root, action["candidate"]), "route": frozen["route"]}
    if kind == "execute":
        frozen = lc.verify_candidate(root, action["candidate"])
        require(frozen["route"] != "generator.py" or settings["runtime"] is not None, "Program runtime was not supplied by host")
        result = execution.run_candidate(root, action["candidate"], action["run_id"], action["seed"],
                                         runtime=settings["runtime"], **settings["execution_limits"])
        require(result == _verify_execution(root, state, action), "Returned receipt differs from recorded execution")
        return result
    if kind == "feedback":
        require(state["config"]["mode"] == "whole_cohort", "No semantic source-feedback adapter for this mode")
        semantic.preflight(root, action["candidate"])
        return semantic.collect_feedback(root, action["candidate"], action["run_id"], action["feedback_id"])
    if kind == "analysis":
        return _analysis(root, state, action)
    return {"final_candidate": action["final_candidate"], "reason": action["reason"],
            "scientific_validity": "not_certified", "source_feedback_scope": SCOPE, "stage_disposition": _disposition(state)}


def _outcome(action, result):
    if action["kind"] == "literature" and result.get("status") in {"error", "rejected"}:
        reason = result.get("reason", "")
        safe = (reason.startswith(("excluded_", "budget_exhausted_", "unsupported_", "http_status_", "invalid_", "partial_"))
                or reason in {"cloud_fulltext_unavailable", "requested_version_unavailable", "fetch_and_approve_parent_first",
                              "unknown_source_linked_supplement", "invalid_pmcid", "invalid_search_arguments",
                              "session_parent_version_already_fixed", "network_or_timeout_failure", "empty_http_response",
                              "unexpected_http_status", "unexpected_http_content_type", "response_size_limit",
                              "response_size_limit_or_invalid_length", "empty_text", "binary_or_control_characters"})
        if reason in {"invalid_configuration", "invalid_artifact_path"}:
            safe = False
        return result["status"], "active" if safe else "halted"
    if action["kind"] == "execute" and result.get("status") != "success":
        # No worker entry or an infrastructure exception is not a scientific revision signal.
        active = result.get("generator_executed") is True and result.get("process") is not None
        return result["status"], "active" if active else "halted"
    if action["kind"] == "finish":
        return "success", "completed" if action["final_candidate"] else "abandoned"
    return "success", "active"


def _artifacts(root, action):
    names = []
    if action["kind"] == "submit":
        names = [action["candidate"] + "/freeze.json"]
    elif action["kind"] == "execute":
        path = root / f"executions/{action['run_id']}/execution.json"
        if path.is_file():
            receipt = lc.read_json(path)
            names = [path.relative_to(root).as_posix()] + [f"executions/{action['run_id']}/{n}" for n in receipt["files"]]
    elif action["kind"] == "feedback":
        names = [f"semantic_feedback_v1/{action['feedback_id']}/feedback.json"]
    return {name: lc.sha256(lc._path(root, name)) for name in names if (root / name).is_file()}


def dispatch(bundle, action_id, action):
    """Reserve, really dispatch, record, then return one author-selected action."""
    root = lc._bundle(bundle)
    directory = lc._path(root, DIRECTORY, file=False)
    action_id, action = _name(action_id), _action(action)
    with ledger._operation(directory, "dispatch") as guard:
        state = _load(root, directory)
        require(state["status"] == "active" and state["pending"] is None, "Session is terminal or interrupted")
        require(action_id.casefold() not in {x.casefold() for x in state["actions"]}, "Action ID already used")
        _reserve_checks(state, action)
        guard["dirty"] = True
        _append(directory, state, "reserve", action_id, action)
        result, error = None, None
        try:
            result = _invoke(root, state, action)
            status, session_status = _outcome(action, result)
        except Exception as exc:
            error = {"type": type(exc).__name__, "message": str(exc)[:2000]}
            recoverable = isinstance(exc, ContractError) and action["kind"] in {"preflight", "submit"}
            if action["kind"] == "submit" and (root / action["candidate"] / "freeze.json").exists():
                recoverable = False
            status, session_status = "error", "active" if recoverable else "halted"
        # Catch mutation by trusted adapters or concurrent writers; never resume after it.
        try:
            for name, expected in state["config"]["inputs"].items():
                require(lc.sha256(lc._path(root, name)) == expected, "Session input changed during action")
            require(_inputs(root) == state["config"]["inputs"], "Static scientific context changed during action")
            _config(state["config"]["settings"])
            require(state["config"]["engines"] == _engines(), "Session engine changed during action")
            for candidate in state["candidates"]:
                lc.verify_candidate(root, candidate)
            registry = lc._registry(root)[0]
            old = state["registry"]
            require(lc._registry(root, old["artifact_count"])[0] == old, "Registry prefix changed during action")
            if action["kind"] != "literature":
                require(registry == old, "Evidence changed outside literature action")
            else:
                added = lc.read_json(root / "registry.json")["artifacts"][old["artifact_count"]:]
                require(all(a["origin"] == "gateway" for a in added), "New evidence did not come from gateway")
            artifacts = _artifacts(root, action)
            gateway = _gateway(root)
            if action["kind"] != "literature":
                require(gateway == state["gateway"], "Gateway changed outside literature action")
        except Exception as exc:
            # Preserve both the adapter response and explicit infrastructure/integrity error.
            status, session_status = "error", "halted"
            error = {"type": type(exc).__name__, "message": str(exc)[:2000]}
            registry, artifacts, gateway = state["registry"], {}, state["gateway"]
        response = {"schema_version": 1, "action_id": action_id, "status": status, "session_status": session_status,
                    "result": result, "error": error}
        raw = ledger._canonical(response) + b"\n"
        require(len(raw) <= MAX_RESULT_BYTES, "Action result exceeds storage bound; session remains interrupted")
        result_path = directory / "results" / (action_id + ".json")
        with result_path.open("xb") as out:
            out.write(raw)
            out.flush()
            os.fsync(out.fileno())
        _append(directory, state, "result", action_id, {"result_sha256": lc.sha256(result_path), "status": status,
            "session_status": session_status, "registry": registry, "gateway": gateway, "artifacts": artifacts})
        # Persisted integrity failures remain stopped even when detailed verification now fails.
        return response


def _summary(state):
    return {"schema_version": 1, "status": state["status"], "pending": state["pending"],
            "usage": state["usage"], "limits": state["config"]["settings"]["limits"],
            "allowed_seeds": state["config"]["settings"]["allowed_seeds"], "candidates": state["candidates"],
            "seed_slots": state["seed_slots"], "actions": {k: {"kind": v["action"]["kind"],
                "status": v.get("result", {}).get("status", "pending")} for k, v in state["actions"].items()},
            "source_feedback_scope": SCOPE, "agent_isolation": "not_provided"}


def verify_session(bundle):
    """Verify ledger, all committed bytes, frozen candidates, and execution/feedback receipts."""
    root = lc._bundle(bundle)
    directory = lc._path(root, DIRECTORY, file=False)
    with ledger._operation(directory, "verify"):
        state = _load(root, directory)
        require(state["pending"] is None, "Interrupted action; automatic recovery is unsupported")
        for entry in state["actions"].values():
            action = entry["action"]
            if action["kind"] == "execute" and entry["receipt"]["artifacts"]:
                _verify_execution(root, state, action)
            if action["kind"] == "feedback" and entry["result"]["status"] == "success":
                semantic.verify_feedback(root, action["feedback_id"], candidate=action["candidate"], run_id=action["run_id"])
        return _summary(state)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    for name in ("create", "act", "status", "verify"):
        sub = subs.add_parser(name)
        sub.add_argument("--bundle", required=True)
        if name == "create":
            sub.add_argument("--config", required=True)
        if name == "act":
            sub.add_argument("--action-id", required=True)
            sub.add_argument("--action", required=True, help="Path to JSON action")
    args = parser.parse_args(argv)
    try:
        if args.command == "create":
            result = create_session(args.bundle, lc.read_json(args.config))
        elif args.command == "act":
            result = dispatch(args.bundle, args.action_id, lc.read_json(args.action))
        else:
            result = verify_session(args.bundle)
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
        return 2 if result.get("status") in {"error", "failed", "timeout", "rejected", "halted"} else 0
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(json.dumps({"status": "error", "type": type(error).__name__, "message": str(error)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
