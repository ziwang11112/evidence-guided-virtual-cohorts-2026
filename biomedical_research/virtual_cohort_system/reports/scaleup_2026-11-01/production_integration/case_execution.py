"""Case guards before feedback, using the unchanged isolated bridge executor.

This controller extension executes only a previously sealed, globally released
and durably reserved campaign stage. It does not import submitted generators.
"""
from __future__ import annotations

import sys
from pathlib import Path

import bundle_assembly as assembly
from cohort_harness import execution, lifecycle, semantic_feedback_v1 as semantic
from cohort_harness.contracts import require

SCALE = assembly.SCALE
for folder in (SCALE / "operators", SCALE / "bridge"):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))
import context_bridge as bridge
import execution_feedback as supplement


def _state(bundle, candidate, case_id, constructor, stage):
    package = assembly.load_package(case_id)
    input_receipt = assembly.verify_bundle_inputs(bundle)
    require(input_receipt["case_id"] == case_id and input_receipt["constructor"] == constructor,
            "Wrong case or constructor input bundle")
    state = bridge.preflight(bundle, candidate)
    require(bridge.canonical(state["task"]) == bridge.canonical(package["task"]), "Execution task differs from committed case")
    require(bridge.canonical(lifecycle.read_json(state["directory"] / "evidence.json")) ==
            bridge.canonical(package["evidence"]), "Candidate substituted source evidence")
    authoring = lifecycle.read_json(state["directory"] / "context_authoring.json")
    expected = assembly.build_bridge_plan(package, constructor, stage, state["spec"], authoring)
    require(bridge.canonical(state["plan"]) == bridge.canonical(expected), "Stage differs from fixed mechanical plan")
    return state, package


def _guard(frame, task, package, context_id):
    case_id = package["case_id"]
    case = assembly._case(case_id)
    path = case / "implementation/generated_validity.py"
    module = assembly._load("production_" + case_id + "_guard", path)
    if case_id == "K01":
        report = module.validate_generated_context(frame, task, context_id=context_id)
    else:
        report = module.validate_generated_release(frame, task)
        if context_id != package["target_id"]:
            expected = {"malawi_rural_men": "M", "malawi_urban_men": "M", "uganda_men": "M",
                        "malawi_rural_women": "F", "malawi_urban_women": "F", "uganda_women": "F"}
            require(context_id in expected, "Unknown K02 source stratum")
            require(bool(frame["sex"].eq(expected[context_id]).all()), "Source table contains wrong-sex rows; filtering forbidden")
            report = {**report, "source_sex_all_rows": expected[context_id]}
    return {"guard_code_sha256": lifecycle.sha256(path), "pure_guard": report}


def _guard_directory(root, relative):
    return root / "case_execution_v1" / Path(relative).name


def _guard_binding(state, trial, child, receipt):
    return {"parent": bridge._parent_binding(state), "trial": trial,
            "task_sha256": lifecycle.sha256(child / "task.json"),
            "execution_sha256": lifecycle.sha256(child / f"executions/{trial['id']}/execution.json"),
            "table_sha256": receipt["files"].get("output/generated.csv"),
            "runner_sha256": lifecycle.sha256(__file__)}


def execute_case_stage(bundle, candidate, ledger_path, case_id, constructor, stage):
    """Once only. Guard failure consumes the slot and emits no numerical feedback."""
    sys.path.insert(0, str(assembly.HERE / "campaign_control"))
    from campaign_control import verify_dispatch
    authorization = verify_dispatch(ledger_path, case_id, constructor, stage, bundle, candidate)
    state, package = _state(bundle, candidate, case_id, constructor, stage)
    initial = bridge.verify(bundle, candidate)
    require(initial["attempts_consumed"] == 0, "Stage already attempted; no retry or resume")
    destination = bridge._destination(state["root"], state["relative"])
    runtime = lifecycle.read_json(destination / "intent.json")["runtime"]
    guards = _guard_directory(state["root"], state["relative"])
    guards.mkdir(parents=True, exist_ok=False)
    execution._write(guards / "intent.json", {"case_id": case_id, "constructor": constructor,
                      "stage": stage, "authorization": authorization, "parent": bridge._parent_binding(state),
                      "runner_sha256": lifecycle.sha256(__file__)})
    (destination / "attempts").mkdir()
    for trial in state["plan"]["trials"]:
        attempt = destination / "attempts" / trial["id"]
        attempt.mkdir()
        execution._write(attempt / "intent.json", bridge._attempt_binding(state, trial))
        child = bridge._child_root(destination, trial["context_id"])
        context = next(c for c in state["plan"]["contexts"] if c["id"] == trial["context_id"])
        outcome = {"status": "error", "error": None, "execution_verified": False, "execution_sha256": None,
                   "generated_table_sha256": None, "semantic_sha256": None, "supplement_sha256": None, "artifacts": {}}
        guard_report = {"status": "not_run", "binding": None, "guard": None, "error": None}
        try:
            receipt = execution.run_candidate(child, bridge.CHILD, trial["id"], trial["seed"], runtime=runtime,
                                              **state["plan"]["execution_limits"])
            outcome["status"] = receipt["status"]
            execution.verify_execution(child, trial["id"])
            outcome["execution_verified"] = True
            if receipt["status"] == "success":
                guard_report["binding"] = _guard_binding(state, trial, child, receipt)
                task = lifecycle.read_json(child / "task.json")
                frame = lifecycle.read_table(child / f"executions/{trial['id']}/output/generated.csv", task, output=True)
                guard_report["guard"] = _guard(frame, task, package, trial["context_id"])
                guard_report["status"] = "valid"
                if context["feedback_policy"] != "none":
                    semantic.collect_feedback(child, bridge.CHILD, trial["id"], trial["id"])
                    bridge._verify_semantic(child, trial["id"])
                    if context["supplement"] is not None:
                        supplement.collect_feedback(child, bridge.CHILD, trial["id"], trial["id"], semantic_feedback_id=trial["id"])
        except (OSError, ValueError, TypeError, KeyError, RuntimeError) as error:
            outcome["status"] = "error"
            outcome["error"] = {"type": type(error).__name__, "message": str(error)[:2000]}
            if guard_report["status"] != "valid":
                guard_report["status"], guard_report["error"] = "unavailable_or_failed", outcome["error"]
        execution._write(guards / (trial["id"] + ".json"), guard_report)
        for field, relative in {"execution_sha256": f"executions/{trial['id']}/execution.json",
                                "generated_table_sha256": f"executions/{trial['id']}/output/generated.csv",
                                "semantic_sha256": f"{semantic.FOLDER}/{trial['id']}/feedback.json",
                                "supplement_sha256": f"{supplement.FOLDER}/{trial['id']}/feedback.json"}.items():
            path = lifecycle._path(child, relative, file=False)
            if path.is_file():
                outcome[field] = lifecycle.sha256(path)
        outcome["artifacts"] = bridge._trial_artifacts(child, trial["id"])
        execution._write(attempt / "outcome.json", outcome)
    bridge.verify(bundle, candidate)
    execution._write(destination / "completion.json", {"schema_version": 1, "files": bridge._inventory(destination)})
    execution._write(guards / "completion.json", {"files": bridge._inventory(guards)})
    return verify_case_stage(bundle, candidate, case_id)


def verify_case_stage(bundle, candidate, case_id):
    """Recompute successful guards against committed outputs; never execute code."""
    root, _, relative = bridge._resolve(bundle, candidate)
    guards = _guard_directory(root, relative)
    intent = lifecycle.read_json(guards / "intent.json")
    require(intent["case_id"] == case_id, "Wrong case guard receipt")
    state, package = _state(bundle, candidate, case_id, intent["constructor"], intent["stage"])
    require(bridge.canonical(intent["parent"]) == bridge.canonical(bridge._parent_binding(state)), "Guard parent changed")
    require(intent["runner_sha256"] == lifecycle.sha256(__file__), "Runner changed after execution")
    completion = lifecycle.read_json(guards / "completion.json")
    require(completion["files"] == {k: v for k, v in bridge._inventory(guards).items() if k != "completion.json"},
            "Guard inventory changed")
    result = bridge.verify(bundle, candidate)
    destination = bridge._destination(root, relative)
    rows = []
    for trial in state["plan"]["trials"]:
        report_path = guards / (trial["id"] + ".json")
        record = lifecycle.read_json(report_path)
        child = bridge._child_root(destination, trial["context_id"])
        if record["status"] == "valid":
            receipt = execution.verify_execution(child, trial["id"])
            require(receipt["status"] == "success", "Guard claims success for failed execution")
            require(bridge.canonical(record["binding"]) == bridge.canonical(_guard_binding(state, trial, child, receipt)),
                    "Guard binding differs")
            task = lifecycle.read_json(child / "task.json")
            frame = lifecycle.read_table(child / f"executions/{trial['id']}/output/generated.csv", task, output=True)
            require(bridge.canonical(record["guard"]) == bridge.canonical(_guard(frame, task, package, trial["context_id"])),
                    "Guard result differs")
        outcome = lifecycle.read_json(destination / f"attempts/{trial['id']}/outcome.json")
        require(outcome["status"] != "success" or record["status"] == "valid", "Successful stage slot lacks valid guard")
        rows.append({"trial_id": trial["id"], "context_id": trial["context_id"],
                     "role": "target" if trial["context_id"] == package["target_id"] else "source",
                     "guard_status": record["status"], "trial_status": outcome["status"],
                     "receipt_path": str(report_path), "receipt_sha256": lifecycle.sha256(report_path)})
    return {"schema_version": 1, "kind": "verified_case_stage_guards", "case_id": case_id,
            "constructor": intent["constructor"], "stage": intent["stage"], "authorization": intent["authorization"],
            "bridge_status": result["status"], "parent": bridge._parent_binding(state), "trials": rows,
            "all_guards_valid": all(x["guard_status"] == "valid" for x in rows),
            "all_slots_successful": all(x["trial_status"] == "success" for x in rows),
            "target_effects_computed": False}
