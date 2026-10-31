"""Case-local mechanical source-context bridge; never execute Agent code on host."""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from cohort_harness import execution, lifecycle, source_replay_v2, whole_cohort_feedback as feedback
from cohort_harness.contracts import exact_keys, require, string_list, text, validate_task
from cohort_harness.lifecycle import _bundle, _candidate, _path, read_json, sha256

PLAN = "source_context_plan.json"
KIND = "whole_cohort_source_context_bridge"
RUN = "source"
FEEDBACK = "source"


def _canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def _digest(value):
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _engines():
    return {**feedback._engine(), Path(__file__).name: sha256(__file__),
            "source_replay_v2.py": sha256(source_replay_v2.__file__),
            "_worker.py": sha256(Path(execution.__file__).with_name("_worker.py"))}


def _candidate_path(root, candidate):
    value = str(candidate)
    if not Path(value).is_absolute() and "/" not in value and "\\" not in value:
        value = "candidates/" + execution._name(value)
    return _candidate(root, value)


def _common_spec(spec):
    result = copy.deepcopy(spec)
    del result["parameters"]["active_context"]
    return result


def _inventory(folder):
    result = {}
    for path in sorted(folder.rglob("*")):
        relative = path.relative_to(folder).as_posix()
        _path(folder, relative, file=False)
        require(path.is_dir() or path.is_file(), "Nonregular bridge artifact")
        if path.is_file():
            result[relative] = sha256(path)
    return result


def _immutable_inventory(folder):
    result = {}
    for name, digest in _inventory(folder).items():
        if name in {"preparation.json", "report.json"}:
            continue
        parts = name.split("/")
        if len(parts) >= 5 and parts[0] == "contexts" and parts[2] == "bundle" and parts[3] in {
                "executions", "whole_cohort_feedback"}:
            continue
        result[name] = digest
    return result


def _supports(columns, parent_columns, domain_columns):
    require([c["name"] for c in columns] == [c["name"] for c in parent_columns],
            "Context column names/order changed")
    for column, parent, domain in zip(columns, parent_columns, domain_columns):
        immutable = lambda c: {k: v for k, v in c.items() if k not in {"minimum", "maximum"}}
        require(_canonical(immutable(column)) == _canonical(immutable(parent)),
                "Context column identity/categories changed")
        require(_canonical(immutable(domain)) == _canonical(immutable(parent)),
                "Domain column identity/categories changed")
        for bound in ("minimum", "maximum"):
            if bound in domain:
                require(bound in column, "Context needs a declared bound for the model domain")
                require(column[bound] >= domain[bound] if bound == "minimum" else column[bound] <= domain[bound],
                        "Context support outside model domain")


def _task_for(parent, descriptor):
    task = copy.deepcopy(parent)
    task.update({key: copy.deepcopy(descriptor[key]) for key in ("population", "n_rows", "columns")})
    validate_task(task)
    return task


def _read_plan(root, directory):
    frozen = lifecycle.verify_candidate(root, directory)
    require(frozen["route"] == "generator.py", "Bridge requires a frozen program candidate")
    task = read_json(root / "task.json")
    require(task["mode"] == "whole_cohort", "Bridge requires whole_cohort mode")
    for name in lifecycle._files(directory):
        require(Path(name).suffix.casefold() != ".csv", "Candidate individual-table artifacts are forbidden")
        require(Path(name).name.casefold() != "observed.csv", "Observed input is forbidden")
    require(not (directory / "source_check_report.json").exists(),
            "Legacy source-check report auto-recomputation is unsupported by this bridge")
    spec = read_json(directory / "model_spec.json")
    parameters = spec["parameters"]
    require("active_context" in parameters and "contexts" in parameters, "Missing context selector/definitions")
    active = execution._name(parameters["active_context"])
    descriptors = parameters["contexts"]
    require(isinstance(descriptors, dict) and bool(descriptors), "Context definitions must be a nonempty object")
    require(active in descriptors, "Unknown parent active_context")
    identifiers = set()
    for identifier in descriptors:
        execution._name(identifier)
        require(identifier.casefold() not in identifiers, "Duplicate case-insensitive context definition")
        identifiers.add(identifier.casefold())
    plan = read_json(_path(directory, PLAN))
    exact_keys(plan, {"schema_version", "model_domain", "contexts"}, where="source context plan")
    require(type(plan["schema_version"]) is int and plan["schema_version"] == 1, "Invalid bridge plan schema")
    domain = plan["model_domain"]
    exact_keys(domain, {"columns", "assumption_ids", "description"}, where="common model domain")
    text(domain["description"], "Model domain description")
    known = {a["id"] for a in spec["assumptions"]}
    string_list(domain["assumption_ids"], "Model domain assumptions")
    require(set(domain["assumption_ids"]) <= known, "Unknown model domain assumption")
    domain_task = copy.deepcopy(task)
    domain_task["columns"] = domain["columns"]
    validate_task(domain_task)
    require(len(domain["columns"]) == len(task["columns"]), "Domain column count changed")
    for identifier, descriptor in descriptors.items():
        exact_keys(descriptor, {"population", "n_rows", "columns", "inputs"}, where="context descriptor")
        require(isinstance(descriptor["inputs"], dict), "Context aggregate inputs must be an object")
        require(type(descriptor["n_rows"]) is int and 1 <= descriptor["n_rows"] <= 1_000_000,
                "Context row count outside permitted range")
        context_task = _task_for(task, descriptor)
        _supports(context_task["columns"], task["columns"], domain["columns"])
    require(_canonical(_task_for(task, descriptors[active])) == _canonical(task),
            "Parent active_context does not match parent task")
    require(isinstance(plan["contexts"], list) and 1 <= len(plan["contexts"]) <= 16,
            "Bridge requires 1 to 16 source contexts")
    ids, paths, contexts = set(), set(), []
    evidence = {i["id"]: i for i in read_json(directory / "evidence.json")["items"]}
    for context in plan["contexts"]:
        exact_keys(context, {"id", "task_path", "feedback_path"}, where="source context entry")
        identifier = execution._name(context["id"])
        require(identifier in descriptors and identifier != active, "Source selector must name a declared nonparent context")
        require(identifier.casefold() not in ids, "Duplicate source context ID")
        ids.add(identifier.casefold())
        for key in ("task_path", "feedback_path"):
            path = _path(directory, context[key])
            require(path.suffix.casefold() == ".json" and context[key].startswith("source_contexts/"),
                    "Context artifact must be a source_contexts JSON file")
            require(context[key].casefold() not in paths, "Repeated context artifact path")
            paths.add(context[key].casefold())
        child_task = read_json(_path(directory, context["task_path"]))
        require(_canonical(child_task) == _canonical(_task_for(task, descriptors[identifier])),
                "Source task differs from its frozen context descriptor or parent invariants")
        recipe = read_json(_path(directory, context["feedback_path"]))
        # Existing reader expects its conventional filename. Validate the same schema
        # here without creating a transient candidate or importing submitted code.
        exact_keys(recipe, {"schema_version", "population", "measurement", "assumption_ids", "checks"}, where="feedback recipe")
        require(type(recipe["schema_version"]) is int and recipe["schema_version"] == 1, "Invalid feedback schema")
        require(recipe["population"] == child_task["population"], "Feedback population mismatch")
        exact_keys(recipe["measurement"], {"mode", "description"}, where="feedback measurement")
        require(recipe["measurement"]["mode"] == "identity", "Identity measurement only")
        text(recipe["measurement"]["description"], "Feedback measurement description")
        string_list(recipe["assumption_ids"], "Feedback assumptions")
        require(set(recipe["assumption_ids"]) <= known, "Unknown feedback assumption")
        require(set(domain["assumption_ids"]) <= set(recipe["assumption_ids"]), "Feedback omits model domain assumptions")
        require(isinstance(recipe["checks"], list) and bool(recipe["checks"]), "Feedback checks required")
        check_ids = set()
        for check in recipe["checks"]:
            exact_keys(check, {"id", "evidence_id", "status", "operator", "assumption_ids", "reason"}, where="source check")
            key = execution._name(check["id"]).casefold()
            require(key not in check_ids, "Duplicate feedback check ID")
            check_ids.add(key)
            require(check["evidence_id"] in evidence, "Unknown feedback evidence")
            string_list(check["assumption_ids"], "Check assumptions")
            require(set(check["assumption_ids"]) <= known, "Unknown check assumption")
            text(check["reason"], "Check reason")
            if check["status"] == "not_computable":
                require(check["operator"] is None, "Not-computable operator must be null")
            else:
                feedback.source_replay._check_metadata(check, evidence, known, recipe["assumption_ids"])
                # Validate operator syntax/types even when the first generated group
                # will be empty; no numerical table is made by this preflight.
                source_replay_v2._operator_preflight(check["operator"], child_task)
        contexts.append((context, child_task, recipe))
    return frozen, spec, contexts


def _parent(root, directory, relative, frozen, spec):
    return {"bundle": str(root), "candidate": relative, "freeze_sha256": sha256(directory / "freeze.json"),
            "plan_sha256": sha256(directory / PLAN), "generator_sha256": sha256(directory / "generator.py"),
            "spec_sha256": sha256(directory / "model_spec.json"), "common_spec_sha256": _digest(_common_spec(spec)),
            "registry_snapshot": frozen["registry_snapshot"]}


def _child(root, directory, frozen, spec, context, task, destination):
    destination.mkdir(parents=True)
    execution._write(destination / "task.json", task)
    registry = read_json(root / "registry.json")["artifacts"][:frozen["registry_snapshot"]["artifact_count"]]
    execution._write(destination / "registry.json", {"artifacts": registry})
    for relative in frozen["commitments"]:
        if relative.startswith("sources/"):
            output = destination / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(_path(root, relative).read_bytes())
    child = destination / "candidates/source"
    child.mkdir(parents=True)
    prefix = frozen["candidate"] + "/"
    for name in frozen["candidate_files"]:
        relative = name.removeprefix(prefix)
        if relative in {"model_spec.json", feedback.PLAN}:
            continue
        output = child / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(_path(directory, relative).read_bytes())
    derived = copy.deepcopy(spec)
    derived["parameters"]["active_context"] = context["id"]
    execution._write(child / "model_spec.json", derived)
    (child / feedback.PLAN).write_bytes(_path(directory, context["feedback_path"]).read_bytes())
    lifecycle.freeze_candidate(destination, child)


def _child_bindings(root, directory, frozen, spec, contexts, destination):
    records = []
    context_folder = _path(destination, "contexts", file=False)
    require(context_folder.is_dir() and sorted(p.name for p in context_folder.iterdir()) == sorted(c[0]["id"] for c in contexts),
            "Unexpected bridge context directory set")
    prefix = frozen["candidate"] + "/"
    parent_files = {name.removeprefix(prefix): digest for name, digest in frozen["commitments"].items() if name.startswith(prefix)}
    registry = {"artifacts": read_json(root / "registry.json")["artifacts"][:frozen["registry_snapshot"]["artifact_count"]]}
    for context, task, _ in contexts:
        child_root = _bundle(_path(destination, f"contexts/{context['id']}/bundle", file=False))
        child = child_root / "candidates/source"
        child_freeze = lifecycle.verify_candidate(child_root, child)
        require(_canonical(read_json(child_root / "task.json")) == _canonical(task), "Child task changed")
        require(_canonical(read_json(child_root / "registry.json")) == _canonical(registry), "Child registry prefix changed")
        expected_spec = copy.deepcopy(spec)
        expected_spec["parameters"]["active_context"] = context["id"]
        require(_canonical(read_json(child / "model_spec.json")) == _canonical(expected_spec),
                "Child specification differs beyond active_context")
        expected_files = {**parent_files, "model_spec.json": sha256(child / "model_spec.json"),
                          feedback.PLAN: sha256(_path(directory, context["feedback_path"]))}
        actual = {name.removeprefix("candidates/source/"): child_freeze["commitments"][name]
                  for name in child_freeze["candidate_files"]}
        require(actual == expected_files, "Child candidate artifacts differ from frozen construction")
        for name, digest in frozen["commitments"].items():
            if name.startswith("sources/"):
                require(sha256(_path(child_root, name)) == digest, "Child source artifact changed")
        records.append({"id": context["id"], "bundle": f"contexts/{context['id']}/bundle",
                        "freeze_sha256": sha256(child / "freeze.json"), "task_sha256": sha256(child_root / "task.json"),
                        "spec_sha256": sha256(child / "model_spec.json"), "feedback_recipe_sha256": sha256(child / feedback.PLAN)})
    return records


def prepare_source_contexts(bundle, candidate, destination, seed, *, runtime=None,
                            timeout_seconds=30, memory_mb=1024, output_bytes=20_000_000, log_bytes=100_000):
    root = _bundle(bundle)
    directory, relative = _candidate_path(root, candidate)
    frozen, spec, contexts = _read_plan(root, directory)
    limits = execution._limits(timeout_seconds, memory_mb, output_bytes, log_bytes, seed)
    runtime = execution._runtime(runtime)
    requested = Path(destination).absolute()
    parent_folder = _bundle(requested.parent)
    destination = _path(parent_folder, requested.name, file=False)
    require(not destination.exists(), "Bridge destination already exists; preserve previous attempts")
    require(not destination.is_relative_to(directory), "Bridge output cannot be inside frozen parent candidate")
    intent = {"schema_version": 1, "kind": KIND, "parent": _parent(root, directory, relative, frozen, spec),
              "contexts": [c[0]["id"] for c in contexts], "limits": limits, "runtime": runtime,
              "run_id": RUN, "feedback_id": FEEDBACK, "engines": _engines()}
    destination.mkdir()
    execution._write(destination / "intent.json", intent)
    for context, task, _ in contexts:
        _child(root, directory, frozen, spec, context, task, destination / f"contexts/{context['id']}/bundle")
    bindings = _child_bindings(root, directory, frozen, spec, contexts, destination)
    preparation = {"schema_version": 1, "kind": KIND, "status": "prepared", "intent_sha256": sha256(destination / "intent.json"),
                   "contexts": bindings, "files": _immutable_inventory(destination)}
    execution._write(destination / "preparation.json", preparation)
    return verify_preparation(root, destination, candidate=relative)


def verify_preparation(bundle, destination, *, candidate=None):
    root, destination = _bundle(bundle), _bundle(destination)
    intent = read_json(_path(destination, "intent.json"))
    exact_keys(intent, {"schema_version", "kind", "parent", "contexts", "limits", "runtime", "run_id", "feedback_id", "engines"}, where="bridge intent")
    require(type(intent["schema_version"]) is int and intent["schema_version"] == 1 and intent["kind"] == KIND,
            "Invalid bridge intent")
    require(intent["engines"] == _engines(), "Bridge implementation changed; use recorded versions")
    require(intent["run_id"] == RUN and intent["feedback_id"] == FEEDBACK, "Bridge run/feedback IDs changed")
    execution._limits(**intent["limits"])
    execution._runtime(intent["runtime"])
    directory, relative = _candidate_path(root, intent["parent"]["candidate"])
    if candidate is not None:
        require(_candidate_path(root, candidate)[1] == relative, "Bridge belongs to a different candidate")
    frozen, spec, contexts = _read_plan(root, directory)
    require(intent["parent"] == _parent(root, directory, relative, frozen, spec), "Bridge parent binding changed")
    require(intent["contexts"] == [c[0]["id"] for c in contexts], "Bridge context selection/order changed")
    preparation = read_json(_path(destination, "preparation.json"))
    expected = {"schema_version": 1, "kind": KIND, "status": "prepared", "intent_sha256": sha256(destination / "intent.json"),
                "contexts": _child_bindings(root, directory, frozen, spec, contexts, destination),
                "files": _immutable_inventory(destination)}
    require(preparation == expected, "Bridge preparation or immutable artifacts changed")
    return preparation


def _records(destination, preparation, limits):
    records = []
    for context in preparation["contexts"]:
        child = _bundle(_path(destination, context["bundle"], file=False))
        executions = child / "executions"
        require(executions.is_dir() and sorted(p.name for p in executions.iterdir()) == [RUN], "Unexpected child execution set")
        receipt = execution.verify_execution(child, RUN)
        require(receipt["candidate"] == "candidates/source" and receipt["route"] == "generator.py", "Wrong child execution")
        require(receipt["limits"] == limits, "Child execution limits/seed changed")
        record = {"id": context["id"], "status": receipt["status"], "generation_link_verified": False,
                  "execution_sha256": sha256(child / f"executions/{RUN}/execution.json"), "feedback": None}
        feedback_folder = child / feedback.FOLDER
        if receipt["status"] == "success":
            require(receipt["generator_executed"] is True, "Missing successful generator execution")
            require(feedback_folder.is_dir() and sorted(p.name for p in feedback_folder.iterdir()) == [FEEDBACK], "Unexpected child feedback set")
            result = feedback.verify_feedback(child, FEEDBACK, candidate="candidates/source", run_id=RUN)
            record.update(generation_link_verified=True, feedback=result,
                          feedback_sha256=sha256(feedback_folder / FEEDBACK / "feedback.json"))
        else:
            require(not feedback_folder.exists(), "Failed execution cannot have accepted feedback")
            record["error"] = receipt["error"]
        records.append(record)
    return records


def execute_source_contexts(bundle, destination, *, candidate=None):
    root, destination = _bundle(bundle), _bundle(destination)
    preparation = verify_preparation(root, destination, candidate=candidate)
    require(not (destination / "report.json").exists(), "Bridge report already exists")
    intent = read_json(destination / "intent.json")
    for context in preparation["contexts"]:
        child = _bundle(_path(destination, context["bundle"], file=False))
        require(not (child / "executions").exists() and not (child / feedback.FOLDER).exists(),
                "Attempt already started; retain it and use a new destination")
    for context in preparation["contexts"]:
        verify_preparation(root, destination, candidate=candidate)
        child = _bundle(_path(destination, context["bundle"], file=False))
        receipt = execution.run_candidate(child, "candidates/source", RUN, runtime=intent["runtime"], **intent["limits"])
        if receipt["status"] == "success":
            feedback.collect_feedback(child, "candidates/source", RUN, FEEDBACK)
    records = _records(destination, preparation, intent["limits"])
    report = {"schema_version": 1, "kind": KIND, "created_utc": datetime.now(timezone.utc).isoformat(),
              "status": "success" if all(r["generation_link_verified"] for r in records) else "failed",
              "scope": "mechanical_same_construction_source_diagnostics", "agent_authorship_verified": False,
              "source_context_adequacy": "requires_separate_substantive_review", "agent_isolation": "not_provided",
              "preparation_sha256": sha256(destination / "preparation.json"), "contexts": records,
              "files": _inventory(destination)}
    execution._write(destination / "report.json", report)
    return verify_source_contexts(root, destination, candidate=candidate)


def verify_source_contexts(bundle, destination, *, candidate=None):
    destination = _bundle(destination)
    preparation = verify_preparation(bundle, destination, candidate=candidate)
    report = read_json(_path(destination, "report.json"))
    text(report.get("created_utc"), "Bridge report timestamp")
    records = _records(destination, preparation, read_json(destination / "intent.json")["limits"])
    files = _inventory(destination)
    del files["report.json"]
    expected = {"schema_version": 1, "kind": KIND, "created_utc": report["created_utc"],
                "status": "success" if all(r["generation_link_verified"] for r in records) else "failed",
                "scope": "mechanical_same_construction_source_diagnostics", "agent_authorship_verified": False,
                "source_context_adequacy": "requires_separate_substantive_review", "agent_isolation": "not_provided",
                "preparation_sha256": sha256(destination / "preparation.json"), "contexts": records, "files": files}
    require(report == expected, "Bridge report or execution/feedback artifacts changed")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "execute", "verify"))
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--candidate", default="initial")
    parser.add_argument("--seed", type=int, default=17401)
    parser.add_argument("--runtime")
    args = parser.parse_args(argv)
    if args.action == "prepare":
        result = prepare_source_contexts(args.bundle, args.candidate, args.destination, args.seed,
                                        runtime=read_json(args.runtime) if args.runtime else None)
    elif args.action == "execute":
        result = execute_source_contexts(args.bundle, args.destination, candidate=args.candidate)
    else:
        result = verify_source_contexts(args.bundle, args.destination, candidate=args.candidate)
    print(json.dumps({"status": result["status"], "contexts": len(result["contexts"])}, indent=2))


if __name__ == "__main__":
    main()
