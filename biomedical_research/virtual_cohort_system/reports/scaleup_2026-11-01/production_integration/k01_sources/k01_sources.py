"""K01 committed metadata compiler and source-only, bridge-bound collector."""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SCALE = HERE.parents[1]
PROJECT = SCALE.parents[1]
CASE = SCALE / "case_k01"
DESIGN_SHA256 = "2e0fa250052ef0a71042041e00851caa17869185a4eeaa04675423aa1d7427bc"
ARTIFACT = "sources/k01_selected_source_evidence.json"
DECLARATION = "k01_descriptive_declaration.json"
FOLDER = "k01_source_descriptives"
SOURCE_CONTEXTS = {"source_mind_china_2019": "WANG2024_MIND", "source_ayele_dire_dawa_2017": "ayele_2020_dire_dawa"}
TARGET = "target_haalsi_pooled_poc"
sys.path.insert(0, str(PROJECT))
from cohort_harness import contracts, execution, lifecycle, semantic_feedback_v1 as semantic


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def same(left, right, message):
    contracts.require(canonical(left) == canonical(right), message)


def _module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sys.path.insert(0, str(SCALE / "operators"))
bridge = _module("k01_source_bound_bridge", SCALE / "bridge/context_bridge.py")


def _committed():
    """Read hash-committed metadata/code only; no reference or patient table."""
    path = CASE / "REVIEWED_DESIGN_COMMITMENT.json"
    contracts.require(lifecycle.sha256(path) == DESIGN_SHA256, "K01 design commitment changed")
    commitment = lifecycle.read_json(path)
    contracts.require(commitment["case_scientifically_admitted"] is True, "K01 not scientifically admitted")
    for relative, expected in commitment["files"].items():
        contracts.require(lifecycle.sha256(lifecycle._path(CASE, relative)) == expected, "Committed K01 artifact changed: " + relative)
    for relative, expected in commitment["read_only_dependencies"].items():
        contracts.require(lifecycle.sha256(lifecycle._path(PROJECT, relative)) == expected, "Committed dependency changed: " + relative)
    guard = _module("k01_bound_generated_validity", CASE / "implementation/generated_validity.py")
    previous = sys.modules.get("generated_validity")
    sys.modules["generated_validity"] = guard
    try:
        descriptive = _module("k01_bound_source_descriptives", CASE / "implementation/source_descriptives.py")
    finally:
        if previous is None:
            del sys.modules["generated_validity"]
        else:
            sys.modules["generated_validity"] = previous
    files = [Path(__file__), Path(bridge.__file__), Path(execution.__file__), Path(lifecycle.__file__), Path(semantic.__file__),
             Path(contracts.__file__), CASE / "implementation/generated_validity.py", CASE / "implementation/source_descriptives.py",
             PROJECT / "cohort_harness/source_checks.py", PROJECT / "cohort_harness/whole_cohort_feedback.py"]
    engines = {str(p.relative_to(PROJECT)).replace("\\", "/"): lifecycle.sha256(p) for p in files}
    return {
        "design_sha256": DESIGN_SHA256,
        "packet_bytes": (CASE / "request/selected_source_evidence.json").read_bytes(),
        "plan": lifecycle.read_json(CASE / "request/descriptive_diagnostic_plan.json"),
        "eligibility": lifecycle.read_json(CASE / "request/context_eligibility.json"),
        "task": lifecycle.read_json(CASE / "request/task_template.json"),
        "engines": engines, "guard": guard, "descriptive": descriptive,
    }


def _compile(state):
    packet = json.loads(state["packet_bytes"])
    plans = {p["evidence_id"]: p for p in state["plan"]["items"]}
    contracts.require(len(plans) == 18 and len(packet["records"]) == 34, "K01 evidence coverage changed")
    evidence = {"schema_version": 1, "sources": [], "items": []}
    artifact_sha = hashlib.sha256(state["packet_bytes"]).hexdigest()
    for source in packet["source_objects"]:
        evidence["sources"].append({
            "id": source["source_id"], "identifier": source["doi"],
            "population": canonical(source["population"]), "measurement": canonical(source["measurement"]),
            "cohort_ids": {"WANG2024_MIND": ["MIND-China"], "ayele_2020_dire_dawa": ["Dire Dawa community 2017"], "bahendeka_2016_uganda": ["Uganda national survey 2014"]}[source["source_id"]],
            "artifacts": [{"path": ARTIFACT, "sha256": artifact_sha}],
        })
    provenance = {}
    for index, record in enumerate(packet["records"]):
        original = record["original_selected_record"]
        original_source = next(s for s in packet["source_objects"] if s["source_id"] == record["source_id"])
        contracts.require(digest(original) == record["provenance"]["original_record_canonical_sha256"], "Original record commitment changed")
        statistic = original["statistic"]
        kind = {"arithmetic_mean": "mean", "individual_standard_deviation": "sd", "sample_proportion": "proportion"}.get(statistic, "reported_other")
        uncertainty = original.get("uncertainty")
        uncertainty = ({"kind": "ci", "low": uncertainty["lower"], "high": uncertainty["upper"], "level": uncertainty["level"]}
                       if uncertainty is not None else {"kind": "not_reported"})
        item = {
            "id": record["id"], "source_id": record["source_id"],
            "locator": original.get("locator", original.get("source_locator")),
            "variables": [record["canonical_variable"] or original["variable"]],
            "kind": kind, "estimate": original.get("estimate", original.get("value")), "unit": original["unit"],
            "uncertainty": uncertainty, "adjustment": copy.deepcopy(original_source.get("analysis", {}).get("logistic_adjustment_variable_headings", []) if statistic == "adjusted_odds_ratio" else original.get("adjustment", [])),
            "selection": canonical({"source_context": record["context_id"], "original_group": original.get("group", original.get("population", original.get("event"))), "source_counts": {k: original[k] for k in ("source_count", "source_denominator", "source_analysis_n") if k in original}}),
            "applicability": canonical({"record_class": record["record_class"], "original_record_sha256": digest(original), "strict_source_replication": "unavailable", "uncertainty_role": "individual SD estimate is participant dispersion, never residual SD or estimator precision" if kind == "sd" else "original role retained", "original_record": original}),
        }
        if kind == "reported_other":
            item["statistic_name"] = statistic
        evidence["items"].append(item)
        provenance[item["id"]] = {"packet_pointer": f"/records/{index}", "original_record": copy.deepcopy(original), "original_record_sha256": digest(original), "disposition": record["record_class"], "original_source": copy.deepcopy(original_source)}
    contracts.validate_evidence(evidence, state["task"])
    templates = []
    for context_id, source_id in SOURCE_CONTEXTS.items():
        source = next(s for s in evidence["sources"] if s["id"] == source_id)
        recipe = {"schema_version": 1, "population": state["eligibility"]["contexts"][context_id]["population"],
                  "measurement": {"mode": "identity", "description": source["measurement"]}, "assumption_ids": [], "checks": []}
        semantics = {"schema_version": 1, "evidence_sha256": "", "recipe_sha256": "", "bindings": []}
        for item in evidence["items"]:
            if item["id"] not in plans or plans[item["id"]]["context_id"] != context_id:
                continue
            check_id = "k01_" + item["id"].lower()
            reason = "Strict source replay unavailable: original weights and exact conventions are not fully reported. The separately committed descriptive approximation is not the source estimator."
            recipe["checks"].append({"id": check_id, "evidence_id": item["id"], "status": "not_computable", "operator": None, "assumption_ids": [], "reason": reason})
            original = provenance[item["id"]]["original_record"]
            denominator = original.get("source_denominator")
            if "derivation" in original:
                denominator = original["derivation"].get("exact_denominator")
            source_n = {"status": "not_reported"} if denominator is None else {"status": "reported", "value": denominator, "scope": "Reported source category/count denominator; not generated n or field-specific complete-case n"}
            semantics["bindings"].append({"check_id": check_id, "evidence_id": item["id"], "source_locator": item["locator"], "definition_status": "not_reported", "source_operator": None, "weights": "not_reported", "transform": "identity", "source_variable_units": {}, "source_n": source_n, "uncertainty_role": "estimate" if item["uncertainty"]["kind"] == "ci" else "not_reported", "reason": reason})
        templates.append({"id": context_id, "role": "source", "source_ids": [source_id], "assumption_ids": [], "feedback_policy": "semantic_v1", "recipe": recipe, "semantics": semantics, "supplement": None})
    return {
        "schema": "k01_source_compilation_v1", "design_sha256": state["design_sha256"],
        "source_artifact_sha256": artifact_sha, "evidence": evidence, "record_provenance": provenance,
        "source_context_templates": templates, "descriptive_plan": copy.deepcopy(state["plan"]),
        "registration_requirements": [{"source_id": s["id"], "path": ARTIFACT, "sha256": artifact_sha} for s in evidence["sources"]],
        "engine_sha256": state["engines"], "strict_available": 0, "active_diagnostics": 0,
        "counts": {"evidence_records": 34, "descriptive_candidates": 18, "context_only": 16},
        "approval_created": False,
    }


def compile_committed():
    """Compile actual fixed metadata; no patient table or numerical operator."""
    return _compile(_committed())


def stage_sources(destination):
    """Exclusive metadata staging; registration screening is a caller decision."""
    state = _committed()
    compiled = _compile(state)
    path = Path(destination)
    contracts.require(not path.exists(), "Staging destination exists")
    path.mkdir(parents=True)
    (path / ARTIFACT).parent.mkdir()
    (path / ARTIFACT).write_bytes(state["packet_bytes"])
    for name, value in {"compilation.json": compiled, "evidence.json": compiled["evidence"], "source_context_templates.json": compiled["source_context_templates"], "registration_requirements.json": compiled["registration_requirements"]}.items():
        (path / name).write_bytes(encoded(value))
    return {"destination": str(path), "compilation_sha256": lifecycle.sha256(path / "compilation.json"), "registration_approved": False}


def bind_context_assumptions(compiled, assumption_ids_by_context):
    contracts.require(set(assumption_ids_by_context) == set(SOURCE_CONTEXTS), "Assumptions must cover both source contexts")
    templates = copy.deepcopy(compiled["source_context_templates"])
    for template in templates:
        values = assumption_ids_by_context[template["id"]]
        contracts.string_list(values, "Agent-authored assumption IDs", nonempty=True)
        template["assumption_ids"] = list(values)
        template["recipe"]["assumption_ids"] = list(values)
    return templates


def declaration_digest(declaration):
    value = copy.deepcopy(declaration)
    value.pop("review", None)
    return digest(value)


def build_declaration(compiled, assumption_ids_by_context, *, model_spec):
    bind_context_assumptions(compiled, assumption_ids_by_context)
    contracts.validate_spec(model_spec, {i["id"] for i in compiled["evidence"]["items"]})
    return {"schema_version": 1, "design_sha256": compiled["design_sha256"], "compilation_sha256": digest(compiled),
            "evidence_sha256": hashlib.sha256(encoded(compiled["evidence"])).hexdigest(),
            "model_spec_sha256": hashlib.sha256(encoded(model_spec)).hexdigest(),
            "descriptive_plan_sha256": digest(compiled["descriptive_plan"]), "engine_sha256": compiled["engine_sha256"],
            "assumption_ids_by_context": copy.deepcopy(assumption_ids_by_context), "review": None}


def _prepare(bundle, candidate, trial_id):
    committed = _committed()
    compiled = _compile(committed)
    trial_id = execution._name(trial_id)
    verified = bridge.verify(bundle, candidate)
    contracts.require(verified["completion_committed"] is True, "Completed bridge required")
    state = bridge.preflight(bundle, candidate)
    same(state["task"], committed["task"], "Parent task differs from approved K01 task")
    context_map = {c["id"]: c for c in state["plan"]["contexts"]}
    contracts.require(set(context_map) == {TARGET, *SOURCE_CONTEXTS}, "K01 context coverage mismatch")
    contracts.require(context_map[TARGET]["feedback_policy"] == "none", "Target feedback forbidden")
    trial = next((t for t in state["plan"]["trials"] if t["id"] == trial_id), None)
    contracts.require(trial is not None and trial["context_id"] in SOURCE_CONTEXTS, "Only a scheduled K01 source trial may be collected")
    record = next((r for r in verified["trials"] if r["trial_id"] == trial_id), None)
    contracts.require(record and record["status"] == "success" and record["generation_link_verified"] is True, "Successful verified source slot required")
    for context_id, descriptor in state["spec"]["parameters"]["contexts"].items():
        contracts.require(descriptor["n_rows"] == 5000, "Committed K01 rows must be5000 in every context")
        contracts.require(descriptor["population"] == committed["eligibility"]["contexts"][context_id]["population"], "Context population mismatch")
    schedule = sorted((t["context_id"], t["seed"], t["n_rows"]) for t in state["plan"]["trials"])
    same(schedule, sorted([(TARGET, s, 5000) for s in (2101, 2102, 2103)] + [(c, s, 5000) for c, s in zip(SOURCE_CONTEXTS, (3101, 3102))]), "K01 fixed stage schedule differs")
    directory = state["directory"]
    declaration = lifecycle.read_json(lifecycle._path(directory, DECLARATION))
    expected = build_declaration(compiled, declaration["assumption_ids_by_context"], model_spec=state["spec"])
    expected["review"] = declaration["review"]
    same(declaration, expected, "Frozen K01 descriptive declaration changed")
    contracts.require(lifecycle.sha256(directory / "model_spec.json") == declaration["model_spec_sha256"], "Parent model bytes differ from bound encoding")
    bridge.supplement._review(declaration["review"], declaration_digest(declaration))
    known = {a["id"] for a in state["spec"]["assumptions"]}
    contracts.require(all(set(v) <= known for v in declaration["assumption_ids_by_context"].values()), "Unknown candidate context assumptions")
    for template in bind_context_assumptions(compiled, declaration["assumption_ids_by_context"]):
        same(context_map[template["id"]], template, "Source recipe differs from committed compilation")
    same(lifecycle.read_json(directory / "evidence.json"), compiled["evidence"], "Candidate evidence differs from admitted compilation")
    contracts.require(lifecycle.sha256(directory / "evidence.json") == declaration["evidence_sha256"], "Evidence bytes differ from bound encoding")
    destination = bridge._destination(state["root"], state["relative"])
    child_root = bridge._child_root(destination, trial["context_id"])
    child = child_root / bridge.CHILD
    same(lifecycle.read_json(child / DECLARATION), declaration, "Child descriptive declaration differs")
    task = lifecycle.read_json(child_root / "task.json")
    spec = lifecycle.read_json(child / "model_spec.json")
    contracts.require(spec["parameters"]["active_context"] == trial["context_id"], "Actual active context mismatch")
    receipt = execution.verify_execution(child_root, trial_id)
    contracts.require(receipt["candidate"] == bridge.CHILD and receipt["candidate_freeze_sha256"] == lifecycle.sha256(child / "freeze.json"), "Child execution linkage mismatch")
    v1 = bridge._verify_semantic(child_root, trial_id)
    contracts.require(all(c["semantic_status"] == "unavailable" and c["difference"] is None for c in v1["checks"]), "Strict-v1 unavailable gate changed")
    output = lifecycle._path(child_root, f"executions/{trial_id}/output/generated.csv")
    bindings = {"design_sha256": committed["design_sha256"], "compilation_sha256": digest(compiled), "parent": bridge._parent_binding(state),
                "bridge_completion_sha256": lifecycle.sha256(destination / "completion.json"), "context_id": trial["context_id"], "trial": trial,
                "task_sha256": lifecycle.sha256(child_root / "task.json"), "child_freeze_sha256": lifecycle.sha256(child / "freeze.json"),
                "model_spec_sha256": lifecycle.sha256(child / "model_spec.json"), "generator_sha256": lifecycle.sha256(child / "generator.py"),
                "declaration_sha256": lifecycle.sha256(child / DECLARATION), "evidence_sha256": lifecycle.sha256(child / "evidence.json"),
                "execution_sha256": lifecycle.sha256(child_root / f"executions/{trial_id}/execution.json"), "generated_table_sha256": lifecycle.sha256(output),
                "semantic_feedback_sha256": lifecycle.sha256(child_root / semantic.FOLDER / trial_id / "feedback.json"),
                "descriptive_plan_sha256": digest(compiled["descriptive_plan"]), "engine_sha256": committed["engines"]}
    contracts.require(bindings["generated_table_sha256"] == record["generated_table_sha256"], "Bridge/output hash mismatch")
    return committed, compiled, state, declaration, child_root, task, output, bindings


def _compute(prepared, trial_id):
    committed, compiled, state, declaration, child_root, task, output, bindings = prepared
    context_id = bindings["context_id"]
    frame = lifecycle.read_table(output, task, output=True)
    guard = committed["guard"].validate_generated_context(frame, task, context_id=context_id)
    raw = committed["descriptive"].compute_source_descriptives(frame, task, context_id=context_id)
    plans = {p["evidence_id"]: p for p in compiled["descriptive_plan"]["items"] if p["context_id"] == context_id}
    contracts.require({r["id"] for r in raw["checks"]} == set(plans), "Helper check coverage differs from committed plan")
    checks = []
    for result in raw["checks"]:
        plan = plans[result["id"]]
        contracts.require(result["diagnostic"]["n_used"] == task["n_rows"], "Descriptive denominator changed")
        value = result["diagnostic"]["value"]
        difference = value - plan["comparison_value"]
        contracts.number(difference, "descriptive raw difference")
        checks.append({"evidence_id": result["id"], "semantic_check_id": "k01_" + result["id"].lower(), "source_id": SOURCE_CONTEXTS[context_id],
                       "definition": plan, "original_record": compiled["record_provenance"][result["id"]]["original_record"],
                       "computed": result, "source_comparison_value": plan["comparison_value"], "unit": plan["comparison_unit"],
                       "descriptive_raw_difference": difference, "strict_source_difference": None, "normalized_score": None,
                       "interpretation": "approved_assumption_defined_descriptive_raw_difference_not_strict_source_replay"})
    contracts.require(lifecycle.sha256(output) == bindings["generated_table_sha256"], "Output changed during collection")
    bridge.verify(state["root"], state["relative"])
    return {"schema_version": 1, "kind": "k01_execution_bound_source_descriptives_v1", "scope": "source_feedback_only", "status": "complete",
            "candidate": state["relative"], "trial_id": trial_id, "context_id": context_id, "bindings": bindings,
            "guard": guard, "checks": checks, "review": declaration["review"], "assumption_ids": declaration["assumption_ids_by_context"][context_id],
            "source_context_metadata": next(v["original_source"] for v in compiled["record_provenance"].values() if v["original_source"]["source_id"] == SOURCE_CONTEXTS[context_id]),
            "scenario_assumptions": compiled["descriptive_plan"]["global_assumptions"],
            "execution_link_verified": True, "semantic_feedback_v1_verified_first": True, "strict_source_replay": "unavailable",
            "rows_filtered": 0, "uncertainty_conversion": "none", "case_release_authorized": False,
            "limitations": ["Hash commitments attest retained bytes, not hostile-host authenticity.", "Approximate source descriptions do not certify scientific transport or Agent authorship.", "Cross-stage campaign budget and delivery authorization are separate controller responsibilities."]}


def _report_path(state, trial_id):
    return lifecycle._path(state["root"], f"{FOLDER}/{Path(state['relative']).name}/{trial_id}", file=False)


def collect_descriptives(parent_bundle, parent_candidate, trial_id):
    """No caller table/context: derive both from the verified scheduled child."""
    prepared = _prepare(parent_bundle, parent_candidate, trial_id)
    folder = _report_path(prepared[2], trial_id)
    contracts.require(not folder.exists(), "K01 source feedback already exists")
    report = _compute(prepared, trial_id)
    report["created_utc"] = datetime.now(timezone.utc).isoformat()
    folder.parent.mkdir(parents=True, exist_ok=True)
    folder.mkdir()
    (folder / "feedback.json").write_bytes(encoded(report))
    return verify_descriptives(parent_bundle, parent_candidate, trial_id)


def verify_descriptives(parent_bundle, parent_candidate, trial_id):
    prepared = _prepare(parent_bundle, parent_candidate, trial_id)
    folder = _report_path(prepared[2], trial_id)
    contracts.require(sorted(p.name for p in folder.iterdir()) == ["feedback.json"], "Unexpected descriptive report artifact")
    report = lifecycle.read_json(lifecycle._path(folder, "feedback.json"))
    contracts.text(report.get("created_utc"), "creation time")
    expected = _compute(prepared, trial_id)
    expected["created_utc"] = report["created_utc"]
    same(report, expected, "Descriptive report changed")
    return report
