"""Finite source/target dispatch with retained-byte linkage, not transport proof.

Only execution.run_candidate can launch submitted code. Preparation and sealing
never import it. All scientific values come from a frozen parent candidate.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

from cohort_harness import contracts, execution, lifecycle, semantic_feedback_v1 as semantic
from cohort_harness.lifecycle import _bundle, _candidate, _path, read_json, sha256

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "operators"))
import execution_feedback as supplement

PLAN = "context_bridge_v1.json"
FOLDER = "context_bridge_v1"
CHILD = "candidates/context"
RECIPE = "whole_cohort_feedback.json"
FEEDBACK = "declared"
require = contracts.require


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def _bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def _hash_bytes(value):
    return hashlib.sha256(value).hexdigest()


def _same(left, right, message):
    require(canonical(left) == canonical(right), message)


def _exact(value, fields, where):
    contracts.exact_keys(value, set(fields.split()), where=where)


def _resolve(bundle, candidate):
    root = _bundle(bundle)
    value = str(candidate)
    if "/" not in value and "\\" not in value:
        value = "candidates/" + execution._name(value)
    directory, relative = _candidate(root, value)
    return root, directory, relative


def _destination(root, relative):
    return _path(root, FOLDER + "/" + relative.split("/")[1], file=False)


def _common(spec):
    common = copy.deepcopy(spec)
    del common["parameters"]["active_context"]
    return common


def _engines():
    modules = [contracts, execution, lifecycle, semantic, supplement, supplement.statistics]
    return {**semantic.legacy._engine(), **{Path(m.__file__).name: sha256(m.__file__) for m in modules},
            "context_bridge.py": sha256(__file__), "_worker.py": sha256(Path(execution.__file__).with_name("_worker.py"))}


def _inventory(folder):
    result = {}
    for path in sorted(folder.rglob("*")):
        name = path.relative_to(folder).as_posix()
        _path(folder, name, file=False)
        require(path.is_dir() or path.is_file(), "Nonregular bridge artifact")
        if path.is_file():
            result[name] = sha256(path)
    return result


def _context_task(task, descriptor):
    derived = copy.deepcopy(task)
    derived.update(population=descriptor["population"], n_rows=descriptor["n_rows"])
    contracts.validate_task(derived)
    return derived


def _known_ids(values, known, where, *, nonempty=False):
    contracts.string_list(values, where, nonempty=nonempty)
    require(set(values) <= known, "Unknown " + where)


def preflight(bundle, candidate):
    """Read only the frozen declarative inputs; no output or approval is made."""
    root, directory, relative = _resolve(bundle, candidate)
    frozen = lifecycle.verify_candidate(root, directory)
    require(frozen["route"] == "generator.py", "Bridge requires generator.py")
    task, spec = read_json(root / "task.json"), read_json(directory / "model_spec.json")
    require(task["mode"] == "whole_cohort", "Whole-cohort only")
    require(not (root / "observed.csv").exists(), "Observed rows forbidden")
    names = lifecycle._files(directory)
    require(not any(Path(name).suffix.casefold() == ".csv" for name in names), "Candidate tables forbidden")
    require(not ({RECIPE, semantic.FILE, supplement.FILE, "source_check_report.json"} & set(names)),
            "Parent feedback must be inline in the bridge plan; legacy reports forbidden")
    plan = read_json(_path(directory, PLAN))
    _exact(plan, "schema_version shared_parameters context_varying_parameters contexts trials execution_limits budget", "bridge plan")
    require(type(plan["schema_version"]) is int and plan["schema_version"] == 1, "Invalid bridge schema")
    parameters = spec["parameters"]
    require({"active_context", "contexts"} <= set(parameters), "Missing active_context/contexts")
    active = execution._name(parameters["active_context"])
    descriptors = parameters["contexts"]
    require(isinstance(descriptors, dict) and 2 <= len(descriptors) <= 16, "Declare 2 to 16 contexts")
    require(len({execution._name(x).casefold() for x in descriptors}) == len(descriptors), "Context name collision")
    contracts.string_list(plan["shared_parameters"], "shared parameters")
    require(set(plan["shared_parameters"]) == set(parameters) - {"active_context", "contexts"},
            "Shared parameters must exhaust non-context parameters")
    evidence = read_json(directory / "evidence.json")
    evidence_ids = {x["id"] for x in evidence["items"]}
    item_sources = {x["id"]: x["source_id"] for x in evidence["items"]}
    source_ids = {x["id"] for x in evidence["sources"]}
    assumption_ids = {x["id"] for x in spec["assumptions"]}
    varying = plan["context_varying_parameters"]
    require(isinstance(varying, list), "Context-varying parameters must be a list")
    varying_names = []
    for entry in varying:
        _exact(entry, "name reason evidence_ids assumption_ids", "context-varying permission")
        contracts.text(entry["name"], "varying parameter name")
        contracts.text(entry["reason"], "varying reason")
        _known_ids(entry["evidence_ids"], evidence_ids, "varying evidence")
        _known_ids(entry["assumption_ids"], assumption_ids, "varying assumptions")
        require(entry["evidence_ids"] or entry["assumption_ids"], "Varying parameter requires provenance")
        varying_names.append(entry["name"])
    require(len(set(varying_names)) == len(varying_names), "Duplicate varying parameter")
    for descriptor in descriptors.values():
        _exact(descriptor, "population n_rows measurement inputs", "scientific context")
        contracts.text(descriptor["population"], "context population")
        contracts.text(descriptor["measurement"], "context measurement")
        require(type(descriptor["n_rows"]) is int and 1 <= descriptor["n_rows"] <= 1_000_000, "Invalid context row count")
        require(isinstance(descriptor["inputs"], dict) and set(descriptor["inputs"]) == set(varying_names),
                "Context inputs must exactly match declared varying parameters")
        _context_task(task, descriptor)
    require(active in descriptors, "Unknown active context")
    _same(_context_task(task, descriptors[active]), task, "Parent task must match active target context")
    contexts = plan["contexts"]
    require(isinstance(contexts, list) and len(contexts) == len(descriptors), "Context coverage mismatch")
    seen, targets = set(), []
    for context in contexts:
        _exact(context, "id role source_ids assumption_ids feedback_policy recipe semantics supplement", "context declaration")
        name = execution._name(context["id"])
        require(name in descriptors and name not in seen, "Unknown/duplicate context")
        seen.add(name)
        require(context["role"] in {"source", "target"}, "Unknown context role")
        _known_ids(context["source_ids"], source_ids, "context source IDs", nonempty=context["role"] == "source")
        _known_ids(context["assumption_ids"], assumption_ids, "context assumptions", nonempty=True)
        policy = context["feedback_policy"]
        require(policy in {"none", "semantic_v1", "semantic_v1_plus_supplement"}, "Unknown feedback policy")
        if context["role"] == "source":
            require(policy != "none", "Source contexts require explicit semantic_feedback_v1")
        else:
            targets.append(name)
            require(not context["source_ids"], "Target cannot be relabelled as an evidence source")
        if policy == "none":
            require(all(context[x] is None for x in ("recipe", "semantics", "supplement")), "No-feedback context has recipes")
        else:
            recipe = context["recipe"]
            require(isinstance(recipe, dict), "Feedback recipe required")
            require(recipe.get("population") == descriptors[name]["population"], "Recipe population mismatch")
            if context["role"] == "source":
                require({item_sources.get(check.get("evidence_id")) for check in recipe.get("checks", [])} == set(context["source_ids"]),
                        "Source recipe must cover exactly the declared source IDs")
            require(set(context["assumption_ids"]) <= set(recipe.get("assumption_ids", [])), "Recipe omits context assumptions")
            _same(recipe.get("measurement"), {"mode": "identity", "description": descriptors[name]["measurement"]},
                  "Recipe measurement mismatch")
            require(isinstance(context["semantics"], dict), "Semantic recipe required")
            for key in ("evidence_sha256", "recipe_sha256"):
                require(context["semantics"].get(key) == "", "Semantic binding placeholders must be empty")
            require((context["supplement"] is not None) == (policy == "semantic_v1_plus_supplement"), "Supplement policy mismatch")
            if context["supplement"] is not None:
                declaration = context["supplement"]
                for key in ("task_sha256", "evidence_sha256", "model_spec_sha256", "semantics_sha256"):
                    require(declaration.get(key) == "", "Supplement binding placeholders must be empty")
                require(declaration.get("context_review") is None, "Bridge cannot reuse a pre-derivation approval")
                table_context = declaration["table_context"]
                require(table_context["kind"] == {"source": "source_context_simulation", "target": "target_context_generated"}[context["role"]]
                        and table_context["context_id"] == name, "Supplement context role/identity mismatch")
                for check in declaration["checks"]:
                    if context["role"] == "source":
                        require(item_sources.get(check.get("evidence_id")) in context["source_ids"], "Supplement evidence belongs to an undeclared source")
                    require(check["proxy"] is None or check["proxy"].get("review") is None, "Proxy approval must follow derivation")
    require(targets == [active], "Exactly one declared target must be the parent active context")
    limits = plan["execution_limits"]
    _exact(limits, "timeout_seconds memory_mb output_bytes log_bytes", "execution limits")
    execution._limits(**limits, seed=0)
    trials = plan["trials"]
    require(isinstance(trials, list) and 2 <= len(trials) <= 256, "Declare 2 to 256 finite trial slots")
    trial_ids, covered = set(), set()
    counts = {"source_attempts": 0, "source_rows": 0, "target_attempts": 0, "target_rows": 0}
    roles = {c["id"]: c["role"] for c in contexts}
    for trial in trials:
        _exact(trial, "id context_id seed n_rows", "trial")
        name = execution._name(trial["id"])
        require(name.casefold() not in trial_ids, "Trial ID collision")
        trial_ids.add(name.casefold())
        identifier = trial["context_id"]
        require(identifier in descriptors, "Unknown trial context")
        covered.add(identifier)
        require(type(trial["n_rows"]) is int and trial["n_rows"] == descriptors[identifier]["n_rows"], "Trial rows differ from frozen context")
        execution._limits(**limits, seed=trial["seed"])
        counts[roles[identifier] + "_attempts"] += 1
        counts[roles[identifier] + "_rows"] += trial["n_rows"]
    require(covered == set(descriptors), "Every declared context requires a trial")
    _same(plan["budget"], counts, "Budget must exactly cover all slots, including failed attempts")
    return {"root": root, "directory": directory, "relative": relative, "frozen": frozen,
            "task": task, "spec": spec, "plan": plan}


def _payloads(state, context):
    """Only active_context and mechanical feedback-binding hashes are derived."""
    task = _context_task(state["task"], state["spec"]["parameters"]["contexts"][context["id"]])
    spec = copy.deepcopy(state["spec"])
    spec["parameters"]["active_context"] = context["id"]
    payloads = {"task.json": _bytes(task), "model_spec.json": _bytes(spec)}
    if context["feedback_policy"] != "none":
        payloads[RECIPE] = _bytes(context["recipe"])
        semantics = copy.deepcopy(context["semantics"])
        semantics.update(evidence_sha256=sha256(state["directory"] / "evidence.json"), recipe_sha256=_hash_bytes(payloads[RECIPE]))
        payloads[semantic.FILE] = _bytes(semantics)
        if context["supplement"] is not None:
            declaration = copy.deepcopy(context["supplement"])
            declaration.update(task_sha256=_hash_bytes(payloads["task.json"]), evidence_sha256=semantics["evidence_sha256"],
                               model_spec_sha256=_hash_bytes(payloads["model_spec.json"]), semantics_sha256=_hash_bytes(payloads[semantic.FILE]))
            payloads[supplement.FILE] = _bytes(declaration)
    return payloads


def _child_root(destination, identifier):
    return _path(destination, f"contexts/{identifier}/bundle", file=False)


def _parent_binding(state):
    root, directory = state["root"], state["directory"]
    return {"candidate": state["relative"], "freeze_sha256": sha256(directory / "freeze.json"),
            "task_sha256": sha256(root / "task.json"), "plan_sha256": sha256(directory / PLAN),
            "generator_sha256": sha256(directory / "generator.py"), "model_spec_sha256": sha256(directory / "model_spec.json"),
            "common_spec_sha256": digest(_common(state["spec"])), "evidence_sha256": sha256(directory / "evidence.json")}


def _binding_request(state, context):
    payloads = _payloads(state, context)
    binding = {"parent": _parent_binding(state), "context_id": context["id"], "role": context["role"],
               "feedback_policy": context["feedback_policy"], "derived": {k: _hash_bytes(v) for k, v in payloads.items()},
               "trials": [t for t in state["plan"]["trials"] if t["context_id"] == context["id"]]}
    declaration = json.loads(payloads[supplement.FILE]) if supplement.FILE in payloads else None
    return {"binding": binding, "binding_sha256": digest(binding),
            "supplement_sha256": None if declaration is None else supplement.declaration_digest(declaration),
            "proxy_sha256": {} if declaration is None else {check["id"]: supplement.proxy_digest(declaration, check["id"])
                for check in declaration["checks"] if check["proxy"] is not None}}


def _draft_files(state):
    """Expected immutable files, with no approval and no child freeze yet."""
    files = {}
    prefix = state["relative"] + "/"
    parent_files = {name.removeprefix(prefix): value for name, value in state["frozen"]["commitments"].items() if name.startswith(prefix)}
    registry = {"artifacts": read_json(state["root"] / "registry.json")["artifacts"][:state["frozen"]["registry_snapshot"]["artifact_count"]]}
    for context in state["plan"]["contexts"]:
        base = f"contexts/{context['id']}/bundle/"
        files[base + "registry.json"] = _hash_bytes(_bytes(registry))
        for name, value in state["frozen"]["commitments"].items():
            if name.startswith("sources/"):
                files[base + name] = value
        for name, value in parent_files.items():
            if name != "model_spec.json":
                files[base + CHILD + "/" + name] = value
        for name, value in _payloads(state, context).items():
            files[base + ("" if name == "task.json" else CHILD + "/") + name] = _hash_bytes(value)
    return files


def prepare(bundle, candidate, *, runtime=None):
    """Reserve the sole bridge location for this parent; produce unsigned drafts."""
    state = preflight(bundle, candidate)
    destination = _destination(state["root"], state["relative"])
    require(not destination.exists(), "Bridge already reserved for this candidate; no budget reset")
    runtime = execution._runtime(runtime)
    destination.parent.mkdir(exist_ok=True)
    destination.mkdir()
    intent = {"schema_version": 1, "kind": "bounded_context_bridge_v1", "parent": _parent_binding(state),
              "runtime": runtime, "engines": _engines(), "budget": state["plan"]["budget"]}
    execution._write(destination / "intent.json", intent)
    registry = {"artifacts": read_json(state["root"] / "registry.json")["artifacts"][:state["frozen"]["registry_snapshot"]["artifact_count"]]}
    prefix = state["relative"] + "/"
    for context in state["plan"]["contexts"]:
        child_root = _child_root(destination, context["id"])
        child = child_root / CHILD
        child.mkdir(parents=True)
        execution._write(child_root / "registry.json", registry)
        for name in state["frozen"]["commitments"]:
            if name.startswith("sources/"):
                out = child_root / name
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(_path(state["root"], name).read_bytes())
            elif name.startswith(prefix) and name != prefix + "model_spec.json":
                out = child / name.removeprefix(prefix)
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(_path(state["root"], name).read_bytes())
        for name, value in _payloads(state, context).items():
            (child_root / name if name == "task.json" else child / name).write_bytes(value)
        if context["feedback_policy"] != "none":
            semantic.preflight(child_root, CHILD)
    preparation = {"intent_sha256": sha256(destination / "intent.json"), "files": _draft_files(state),
                   "requests": {c["id"]: _binding_request(state, c) for c in state["plan"]["contexts"]}}
    execution._write(destination / "preparation.json", preparation)
    _verify_prepared(state, destination)
    return preparation


def _verify_prepared(state, destination):
    intent = read_json(_path(destination, "intent.json"))
    expected = {"schema_version": 1, "kind": "bounded_context_bridge_v1", "parent": _parent_binding(state),
                "runtime": execution._runtime(intent["runtime"]), "engines": _engines(), "budget": state["plan"]["budget"]}
    _same(intent, expected, "Bridge intent changed")
    preparation = read_json(_path(destination, "preparation.json"))
    expected = {"intent_sha256": sha256(destination / "intent.json"), "files": _draft_files(state),
                "requests": {c["id"]: _binding_request(state, c) for c in state["plan"]["contexts"]}}
    _same(preparation, expected, "Preparation or binding request changed")
    return preparation


def binding_requests(bundle, candidate):
    state = preflight(bundle, candidate)
    destination = _destination(state["root"], state["relative"])
    preparation = _verify_prepared(state, destination)
    require(not (destination / "seal.json").exists(), "Already sealed")
    expected = {**preparation["files"], "intent.json": sha256(destination / "intent.json"),
                "preparation.json": sha256(destination / "preparation.json")}
    _same(_inventory(destination), expected, "Prepared artifacts changed or unexpected files exist")
    return preparation["requests"]


def seal(bundle, candidate, reviews):
    """Add only externally supplied review records, then freeze each child."""
    requests = binding_requests(bundle, candidate)
    state = preflight(bundle, candidate)
    destination = _destination(state["root"], state["relative"])
    require(isinstance(reviews, dict) and set(reviews) == set(requests), "Reviews must cover exactly all contexts")
    # Validate every supplied review before the first write. No approval helper exists.
    for context in state["plan"]["contexts"]:
        identifier = context["id"]
        review, request = reviews[identifier], requests[identifier]
        _exact(review, "binding_review supplement_review proxy_reviews", "binding review packet")
        supplement._review(review["binding_review"], request["binding_sha256"])
        if request["supplement_sha256"] is None:
            require(review["supplement_review"] is None, "Undeclared supplement review")
        else:
            supplement._review(review["supplement_review"], request["supplement_sha256"])
        require(isinstance(review["proxy_reviews"], dict) and set(review["proxy_reviews"]) == set(request["proxy_sha256"]), "Proxy review set mismatch")
        for check_id, expected in request["proxy_sha256"].items():
            supplement._review(review["proxy_reviews"][check_id], expected)
    execution._write(destination / "reviews.json", reviews)
    for context in state["plan"]["contexts"]:
        child_root = _child_root(destination, context["id"])
        child = child_root / CHILD
        if context["supplement"] is not None:
            declaration = read_json(child / supplement.FILE)
            declaration["context_review"] = reviews[context["id"]]["supplement_review"]
            for check in declaration["checks"]:
                if check["proxy"] is not None:
                    check["proxy"]["review"] = reviews[context["id"]]["proxy_reviews"][check["id"]]
            # This replaces only explicitly unsigned review slots in an unfrozen draft.
            (child / supplement.FILE).write_bytes(_bytes(declaration))
        frozen = lifecycle.freeze_candidate(child_root, child)
        if context["feedback_policy"] != "none":
            semantic_plan = semantic.preflight(child_root, CHILD)
            if context["supplement"] is not None:
                supplement._declaration(child_root, child, frozen, CHILD, read_json(child_root / "task.json"), semantic_plan)
    execution._write(destination / "seal.json", {"status": "sealed", "files": _inventory(destination)})
    return verify(bundle, candidate)


def _verify_seal(state, destination):
    preparation = _verify_prepared(state, destination)
    seal_record = read_json(_path(destination, "seal.json"))
    _exact(seal_record, "status files", "seal")
    require(seal_record["status"] == "sealed", "Not sealed")
    reviews = read_json(_path(destination, "reviews.json"))
    require(set(reviews) == set(preparation["requests"]), "Review context set changed")
    expected_files = dict(preparation["files"])
    for context in state["plan"]["contexts"]:
        identifier = context["id"]
        child_root = _child_root(destination, identifier)
        child = child_root / CHILD
        base = f"contexts/{identifier}/bundle/{CHILD}/"
        request, review = preparation["requests"][identifier], reviews[identifier]
        _exact(review, "binding_review supplement_review proxy_reviews", "binding review packet")
        supplement._review(review["binding_review"], request["binding_sha256"])
        if context["supplement"] is not None:
            declaration = json.loads(_payloads(state, context)[supplement.FILE])
            supplement._review(review["supplement_review"], request["supplement_sha256"])
            require(set(review["proxy_reviews"]) == set(request["proxy_sha256"]), "Proxy reviews changed")
            declaration["context_review"] = review["supplement_review"]
            for check in declaration["checks"]:
                if check["proxy"] is not None:
                    supplement._review(review["proxy_reviews"][check["id"]], request["proxy_sha256"][check["id"]])
                    check["proxy"]["review"] = review["proxy_reviews"][check["id"]]
            expected_files[base + supplement.FILE] = _hash_bytes(_bytes(declaration))
        else:
            require(review["supplement_review"] is None and review["proxy_reviews"] == {}, "Undeclared review")
        frozen = lifecycle.verify_candidate(child_root, child)
        expected_files[base + "freeze.json"] = sha256(child / "freeze.json")
        require(sha256(child / "generator.py") == sha256(state["directory"] / "generator.py"), "Generator bytes differ")
        _same(_common(read_json(child / "model_spec.json")), _common(state["spec"]), "Scientific specification differs beyond active_context")
        if context["feedback_policy"] != "none":
            semantic_plan = semantic.preflight(child_root, CHILD)
            if context["supplement"] is not None:
                supplement._declaration(child_root, child, frozen, CHILD, read_json(child_root / "task.json"), semantic_plan)
    for name in ("intent.json", "preparation.json", "reviews.json"):
        expected_files[name] = sha256(_path(destination, name))
    _same(seal_record["files"], expected_files, "Sealed file set or bindings changed")
    for name, expected in expected_files.items():
        require(sha256(_path(destination, name)) == expected, "Sealed artifact changed: " + name)
    return seal_record


def _verify_semantic(child_root, run_id):
    report = semantic.verify_feedback(child_root, run_id, candidate=CHILD, run_id=run_id)
    expected = semantic._compute(child_root, child_root / CHILD, CHILD, run_id, run_id)
    expected["created_utc"] = report["created_utc"]
    _same(report, expected, "Typed semantic receipt changed")
    return report


def _attempt_binding(state, trial):
    return {"trial": trial, "parent": _parent_binding(state),
            "limits": execution._limits(**state["plan"]["execution_limits"], seed=trial["seed"])}


def _trial_artifacts(child_root, trial_id):
    files = {}
    for folder in ("executions", semantic.FOLDER, supplement.FOLDER):
        relative = folder + "/" + trial_id
        path = _path(child_root, relative, file=False)
        if path.exists():
            files.update({relative + "/" + name: value for name, value in _inventory(path).items()})
    return files


def _trial_record(state, destination, trial, *, require_outcome=True):
    attempt = _path(destination, f"attempts/{trial['id']}", file=False)
    binding = read_json(_path(attempt, "intent.json"))
    _same(binding, _attempt_binding(state, trial), "Attempt binding changed")
    outcome_path = _path(attempt, "outcome.json", file=False)
    if not outcome_path.exists():
        require(not require_outcome, "Attempt interrupted; slot consumed and cannot be retried")
        return {"trial_id": trial["id"], "context_id": trial["context_id"], "status": "interrupted", "attempt_consumed": True,
                "generation_link_verified": False}
    outcome = read_json(outcome_path)
    _exact(outcome, "status error execution_verified execution_sha256 generated_table_sha256 semantic_sha256 supplement_sha256 artifacts", "attempt outcome")
    context = next(c for c in state["plan"]["contexts"] if c["id"] == trial["context_id"])
    child_root = _child_root(destination, trial["context_id"])
    run = _path(child_root, "executions/" + trial["id"], file=False)
    execution_path = _path(run, "execution.json", file=False)
    linked = False
    require(outcome["status"] in {"success", "failed", "timeout", "error"}, "Invalid attempt status")
    require(type(outcome["execution_verified"]) is bool, "Invalid execution verification flag")
    _same(_trial_artifacts(child_root, trial["id"]), outcome["artifacts"], "Attempt artifacts changed")
    for field, name in {"execution_sha256": f"executions/{trial['id']}/execution.json",
                        "generated_table_sha256": f"executions/{trial['id']}/output/generated.csv",
                        "semantic_sha256": f"{semantic.FOLDER}/{trial['id']}/feedback.json",
                        "supplement_sha256": f"{supplement.FOLDER}/{trial['id']}/feedback.json"}.items():
        require(outcome[field] == outcome["artifacts"].get(name), "Attempt artifact binding changed: " + field)
    if execution_path.exists():
        require(outcome["execution_sha256"] == sha256(execution_path), "Execution hash changed")
        try:
            receipt = execution.verify_execution(child_root, trial["id"])
        except (OSError, ValueError, TypeError, KeyError, RuntimeError):
            require(outcome["status"] == "error" and outcome["execution_verified"] is False,
                    "Previously verified execution is no longer valid")
            receipt = None
        if receipt is not None:
            require(outcome["execution_verified"] is True, "Execution verification state changed")
            require(receipt["candidate"] == CHILD and receipt["route"] == "generator.py", "Wrong execution candidate/route")
            _same(receipt["limits"], binding["limits"], "Execution limits or seed changed")
            require(receipt["candidate_freeze_sha256"] == sha256(child_root / CHILD / "freeze.json"), "Execution freeze differs")
            if outcome["status"] != "error":
                require(outcome["status"] == receipt["status"], "Attempt/execution status mismatch")
            linked = receipt["status"] == "success" and receipt["generator_executed"] is True
        if outcome["status"] == "success":
            require(linked, "Successful generator required")
    else:
        require(outcome["status"] == "error" and outcome["execution_verified"] is False, "Missing recorded execution")
    if outcome["status"] == "success" and context["feedback_policy"] != "none":
        _verify_semantic(child_root, trial["id"])
        require(outcome["semantic_sha256"] == sha256(child_root / semantic.FOLDER / trial["id"] / "feedback.json"), "Semantic receipt hash changed")
        if context["supplement"] is not None:
            supplement.verify_feedback(child_root, trial["id"], candidate=CHILD, run_id=trial["id"])
            require(outcome["supplement_sha256"] == sha256(child_root / supplement.FOLDER / trial["id"] / "feedback.json"), "Supplement hash changed")
    if context["feedback_policy"] == "none":
        require(outcome["semantic_sha256"] is None and outcome["supplement_sha256"] is None, "Undeclared target feedback")
    if context["supplement"] is None:
        require(outcome["supplement_sha256"] is None, "Undeclared supplemental feedback")
    return {"trial_id": trial["id"], "context_id": trial["context_id"], "role": context["role"], "status": outcome["status"],
            "attempt_consumed": True, "generation_link_verified": linked,
            "execution_sha256": outcome["execution_sha256"], "generated_table_sha256": outcome["generated_table_sha256"]}


def verify(bundle, candidate):
    """Verify linkage and every retained file; never rerun submitted code."""
    state = preflight(bundle, candidate)
    destination = _destination(state["root"], state["relative"])
    seal_record = _verify_seal(state, destination)
    allowed = set(seal_record["files"]) | {"seal.json"}
    completion_path = _path(destination, "completion.json", file=False)
    completion_committed = completion_path.exists()
    if completion_committed:
        allowed.add("completion.json")
    records = []
    for trial in state["plan"]["trials"]:
        attempt = _path(destination, "attempts/" + trial["id"], file=False)
        if attempt.exists():
            records.append(_trial_record(state, destination, trial, require_outcome=False))
            allowed.add(f"attempts/{trial['id']}/intent.json")
            if (attempt / "outcome.json").exists():
                allowed.add(f"attempts/{trial['id']}/outcome.json")
            child = _child_root(destination, trial["context_id"])
            run = _path(child, "executions/" + trial["id"], file=False)
            if run.exists():
                allowed.update(f"contexts/{trial['context_id']}/bundle/executions/{trial['id']}/" + name for name in _inventory(run))
            context = next(c for c in state["plan"]["contexts"] if c["id"] == trial["context_id"])
            if context["feedback_policy"] != "none":
                allowed.add(f"contexts/{trial['context_id']}/bundle/{semantic.FOLDER}/{trial['id']}/feedback.json")
            if context["supplement"] is not None:
                allowed.add(f"contexts/{trial['context_id']}/bundle/{supplement.FOLDER}/{trial['id']}/feedback.json")
    actual = _inventory(destination)
    require(set(actual) <= allowed, "Unexpected bridge run, feedback or artifact")
    if completion_committed:
        completion = read_json(completion_path)
        _exact(completion, "schema_version files", "completion")
        require(type(completion["schema_version"]) is int and completion["schema_version"] == 1, "Invalid completion schema")
        _same({name: value for name, value in actual.items() if name != "completion.json"}, completion["files"],
              "Completed ledger or retained artifacts changed")
    allowed_directories = set()
    for name in allowed:
        allowed_directories.update(parent.as_posix() for parent in Path(name).parents if parent.as_posix() != ".")
    for trial in state["plan"]["trials"]:
        if (destination / "attempts" / trial["id"]).exists():
            run = f"contexts/{trial['context_id']}/bundle/executions/{trial['id']}"
            allowed_directories.update({run, run + "/input", run + "/output"})
            allowed_directories.update(parent.as_posix() for parent in Path(run).parents if parent.as_posix() != ".")
    require(all(p.relative_to(destination).as_posix() in allowed_directories for p in destination.rglob("*") if p.is_dir()),
            "Unexpected bridge directory")
    successful_roles = {r["role"] for r in records if r["generation_link_verified"]}
    all_links = len(records) == len(state["plan"]["trials"]) and all(r["generation_link_verified"] for r in records)
    all_successful = len(records) == len(state["plan"]["trials"]) and all(r["status"] == "success" for r in records)
    status = "sealed" if not records else "incomplete"
    if completion_committed:
        require(len(records) == len(state["plan"]["trials"]) and all(r["status"] != "interrupted" for r in records),
                "Completion cannot omit or interrupt a planned trial")
        status = "complete" if all(r["status"] == "success" for r in records) else "finished_with_failures"
    return {"status": status,
            "trials": records, "attempts_consumed": len(records), "budget": state["plan"]["budget"],
            "completion_committed": completion_committed,
            "source_target_generation_link_verified": all_links,
            "all_planned_generation_links_verified": all_links, "all_planned_trials_successful": all_successful,
            "any_verified_source_target_pair": successful_roles == {"source", "target"},
            "linkage_scope": "same_generator_bytes_and_complete_specification_except_active_context",
            "scientific_contract_compliance": "not_verified", "transport_validity": "not_assessed",
            "agent_authorship_verified": False, "case_release_authorized": False,
            "generator_isolation": "existing_execution_adapter_only", "agent_isolation": "not_provided",
            "budget_scope": "one_exclusive_bridge_per_retained_parent_candidate_not_host_enforced_global_budget"}


def execute(bundle, candidate):
    """Dispatch each declared slot once. Every exception still consumes its slot."""
    initial = verify(bundle, candidate)
    require(initial["attempts_consumed"] == 0, "Bridge already attempted; no retry/resume or budget reset")
    state = preflight(bundle, candidate)
    destination = _destination(state["root"], state["relative"])
    runtime = read_json(destination / "intent.json")["runtime"]
    (destination / "attempts").mkdir()
    for trial in state["plan"]["trials"]:
        # Exclusive intent is the budget debit, written before runner dispatch.
        attempt = destination / "attempts" / trial["id"]
        attempt.mkdir()
        execution._write(attempt / "intent.json", _attempt_binding(state, trial))
        child = _child_root(destination, trial["context_id"])
        context = next(c for c in state["plan"]["contexts"] if c["id"] == trial["context_id"])
        outcome = {"status": "error", "error": None, "execution_verified": False, "execution_sha256": None, "generated_table_sha256": None,
                   "semantic_sha256": None, "supplement_sha256": None, "artifacts": {}}
        try:
            receipt = execution.run_candidate(child, CHILD, trial["id"], trial["seed"], runtime=runtime,
                                              **state["plan"]["execution_limits"])
            outcome["status"] = receipt["status"]
            execution.verify_execution(child, trial["id"])
            outcome["execution_verified"] = True
            if receipt["status"] == "success" and context["feedback_policy"] != "none":
                semantic.collect_feedback(child, CHILD, trial["id"], trial["id"])
                _verify_semantic(child, trial["id"])
                if context["supplement"] is not None:
                    supplement.collect_feedback(child, CHILD, trial["id"], trial["id"], semantic_feedback_id=trial["id"])
        except (OSError, ValueError, TypeError, KeyError, RuntimeError) as error:
            outcome["status"] = "error"
            outcome["error"] = {"type": type(error).__name__, "message": str(error)[:2000]}
        for field, relative in {"execution_sha256": f"executions/{trial['id']}/execution.json",
                                "generated_table_sha256": f"executions/{trial['id']}/output/generated.csv",
                                "semantic_sha256": f"{semantic.FOLDER}/{trial['id']}/feedback.json",
                                "supplement_sha256": f"{supplement.FOLDER}/{trial['id']}/feedback.json"}.items():
            path = _path(child, relative, file=False)
            if path.is_file():
                outcome[field] = sha256(path)
        outcome["artifacts"] = _trial_artifacts(child, trial["id"])
        execution._write(attempt / "outcome.json", outcome)
    verify(bundle, candidate)
    execution._write(destination / "completion.json", {"schema_version": 1, "files": _inventory(destination)})
    return verify(bundle, candidate)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("preflight", "prepare", "requests", "seal", "execute", "verify"))
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--reviews")
    args = parser.parse_args(argv)
    if args.action == "preflight":
        result = preflight(args.bundle, args.candidate)
        result = {"status": "preflight_passed", "contexts": len(result["plan"]["contexts"])}
    elif args.action == "seal":
        require(args.reviews is not None, "seal requires independent --reviews JSON")
        result = seal(args.bundle, args.candidate, read_json(args.reviews))
    else:
        function = binding_requests if args.action == "requests" else globals()[args.action]
        result = function(args.bundle, args.candidate)
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
