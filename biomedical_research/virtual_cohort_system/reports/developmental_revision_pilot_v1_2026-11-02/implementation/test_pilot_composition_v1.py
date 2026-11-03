"""One invented full-inventory composition; only the process boundary is mocked.

One admitted version executes nine source and three target receipt slots. The
other five versions are explicitly aborted. No patient files or old reports are
read, and the submitted generator is never imported or executed.
"""
from __future__ import annotations

import copy
import itertools
from pathlib import Path
from types import SimpleNamespace

import pytest

import pilot_controller_v1 as pilot
import pilot_evaluation_v1 as primary
import independent_pilot_recompute as independent
import test_pilot_controller_v1 as fixture
import test_pilot_evaluation_v1 as analysis_fixture


def bound(path):
    return {"path": str(path.resolve()), "sha256": pilot.sha256(path)}


def prepare_invented_candidate(tmp_path, monkeypatch, release):
    old = fixture.old_fixture_module()
    with monkeypatch.context() as temporary:
        temporary.setattr(pilot.lifecycle, "freeze_candidate", lambda *a, **k: None)
        root = old.bundle.__wrapped__(tmp_path, monkeypatch, SimpleNamespace(param="qualified"))
    candidate = root / "candidates/invented"
    task = pilot.read_json(root / "task.json")
    task.update(row_id="row_id", n_rows=3000)
    task["budget"]["revisions"] = 2
    units = {"age": "year", "female": "1", "bmi": "kg/m^2", "glucose": "mmol/L", "hba1c": "%"}
    task["columns"] = [{"name": "row_id", "kind": "string", "unit": "1", "role": "identifier", "nullable": False}] + [
        {"name": name, "kind": "number", "unit": units[name], "role": "generated", "nullable": False}
        for name in primary.VARIABLES]
    fixture.write(root / "task.json", task)
    spec = pilot.read_json(candidate / "model_spec.json")
    descriptor = copy.deepcopy(spec["parameters"]["contexts"]["source"])
    spec["parameters"]["contexts"] = {c: {**copy.deepcopy(descriptor), "n_rows": 3000}
                                       for c in release["source_contexts"]}
    spec["parameters"]["contexts"]["target"] = {**copy.deepcopy(descriptor), "population": task["population"], "n_rows": 3000}
    fixture.write(candidate / "model_spec.json", spec)
    candidate.joinpath("generator.py").write_text('''import numpy as np
import pandas as pd
def generate(observed, specification, seed):
    n = specification["parameters"]["contexts"][specification["parameters"]["active_context"]]["n_rows"]
    rng = np.random.default_rng(seed)
    return pd.DataFrame({"row_id": ["invented-" + str(i) for i in range(n)],
        "age": rng.integers(35, 75, n), "female": rng.binomial(1, .5, n),
        "bmi": rng.uniform(19, 35, n), "glucose": rng.uniform(4, 7, n),
        "hba1c": rng.uniform(3, 9, n)})
''', encoding="utf-8")

    original_evidence = pilot.read_json(candidate / "evidence.json")
    original_plan = pilot.read_json(candidate / pilot.bridge.PLAN)
    original_qualified = pilot.read_json(candidate / "qualified_plan_v1.json")["contexts"]["source"]
    original_ledger = pilot.read_json(candidate / "evidence_use_v1.json")
    evidence = {"schema_version": 1, "sources": [], "items": []}
    registry, contexts, qualified_contexts, uptake = [], [], {}, []
    source_artifact = original_evidence["sources"][0]["artifacts"][0]
    for index, context in enumerate(release["source_contexts"]):
        source_record = copy.deepcopy(original_evidence["sources"][0])
        source_record.update(id=f"invented-source-{index}", identifier=f"invented:source-{index}", cohort_ids=[f"invented-source-{index}"])
        evidence["sources"].append(source_record)
        registry.append({"source_id": source_record["id"], **source_artifact, "origin": "fixture", "screening": "approved"})
        context_record = copy.deepcopy(original_plan["contexts"][0])
        context_record.update(id=context, source_ids=[source_record["id"]], feedback_policy="semantic_v1", supplement=None)
        context_record["recipe"]["checks"] = []
        context_record["semantics"]["bindings"] = []
        qualified = copy.deepcopy(original_qualified)
        qualified.update(context_id=context, source_ids=[source_record["id"]], checks=[])
        for required in [q for q in release["required_qualified_checks"] if q["context_id"] == context]:
            check_id = required["check_id"]
            evidence_id, semantic_id = "e-" + check_id, "strict-" + check_id
            item = copy.deepcopy(original_evidence["items"][0])
            item.update(id=evidence_id, source_id=source_record["id"], variables=["bmi", "hba1c"])
            evidence["items"].append(item)
            strict = copy.deepcopy(original_plan["contexts"][0]["recipe"]["checks"][0])
            strict.update(id=semantic_id, evidence_id=evidence_id)
            context_record["recipe"]["checks"].append(strict)
            semantic = copy.deepcopy(original_plan["contexts"][0]["semantics"]["bindings"][0])
            semantic.update(check_id=semantic_id, evidence_id=evidence_id)
            context_record["semantics"]["bindings"].append(semantic)
            comparison = copy.deepcopy(original_qualified["checks"][0])
            comparison.update(id=check_id, evidence_id=evidence_id, semantic_check_id=semantic_id)
            comparison["operator"].update(x="bmi", y="hba1c")
            qualified["checks"].append(comparison)
            use = copy.deepcopy(original_ledger["items"][0])
            use.update(evidence_id=evidence_id, context_id=context, check_ids=[semantic_id], source_reference={
                "source_id": source_record["id"], "source_sha256": pilot.digest(source_record), "item_sha256": pilot.digest(item)})
            uptake.append(use)
        contexts.append(context_record)
        qualified_contexts[context] = qualified
    fixture.write(root / "registry.json", {"artifacts": registry})
    fixture.write(candidate / "evidence.json", evidence)
    fixture.write(candidate / "evidence_use_v1.json", {"schema_version": 1, "evidence_sha256": pilot.digest(evidence), "items": uptake})
    fixture.write(candidate / "qualified_plan_v1.json", {"schema_version": 1, "contexts": qualified_contexts})
    original_plan["contexts"] = contexts + [original_plan["contexts"][1]]
    original_plan["trials"] = [{"id": s["run_id"], "context_id": s["context_id"], "seed": s["seed"], "n_rows": s["n_rows"]}
                              for s in pilot.planned_slots(release) if s["constructor"] == "A01" and s["version"] == "initial"]
    original_plan["budget"] = {"source_attempts": 9, "source_rows": 27000, "target_attempts": 3, "target_rows": 9000}
    fixture.write(candidate / pilot.bridge.PLAN, original_plan)

    prototype = pilot.read_json(candidate / "analysis_evidence.json")["analyses"][0]
    analyses, law_analyses = [], []
    for identifier, exposure, adjustment in (("A_BMI", "bmi", ["age", "female"]),
                                            ("A_GLUCOSE", "glucose", ["age", "female"]),
                                            ("A_AGE", "age", ["female", "bmi", "glucose"])):
        analysis = copy.deepcopy(prototype)
        analysis["id"] = identifier
        analysis["estimand"].update(outcome="hba1c", exposures=[exposure], adjustment=adjustment)
        analyses.append(analysis)
        law_analyses.append({"id": identifier, "kind": "ols", "outcome": "hba1c", "predictors": [exposure, *adjustment]})
    fixture.write(candidate / "analysis_evidence.json", {"schema_version": 1, "analyses": analyses})
    variables = {"age": {"op": "discrete_uniform", "lower": 35, "upper": 74}, "female": {"op": "bernoulli", "p": .5},
                 "bmi": {"op": "uniform", "lower": 19, "upper": 35}, "glucose": {"op": "uniform", "lower": 4, "upper": 7},
                 "hba1c": {"op": "uniform", "lower": 3, "upper": 9}}
    law = {"schema_version": "scientific_validity_v1", "variables": variables,
           "independence": [list(pair) for pair in itertools.combinations(variables, 2)], "analyses": law_analyses}
    fixture.write(candidate / "scientific_validity_v1.json", {"schema_version": 1, "context_laws": {
        c: copy.deepcopy(law) for c in [*release["source_contexts"], "target"]}})
    provenance = [{"kind": "assumption", "id": "fixture"}]
    support = {"schema_version": "support_selection_v1", "contexts": {c: {
        "final_supports": {v: {"domain": fixture.domain(closed=v == "female"), "provenance": provenance} for v in variables},
        "native_views": {}, "selection": {"route": "direct_eligible_joint", "exclusion_implementation": "not_claimed",
            "conditioning_event": None, "description": "Invented fixture joint law", "provenance": provenance},
        "transformations": [], "derivations": []} for c in [*release["source_contexts"], "target"]}}
    fixture.write(candidate / "support_selection_v1.json", support)
    pilot.lifecycle.freeze_candidate(root, candidate)
    old.ready(root)
    return root, "candidates/invented"


def test_real_closed_controller_inventory_composes_both_evaluators(tmp_path, monkeypatch):
    release = fixture.release.__wrapped__(tmp_path, monkeypatch)
    contract = pilot.read_json(release["support_contract"]["path"])
    for checks in contract["required_checks"].values():
        checks[0]["variable"] = "bmi"
    release["support_contract"] = fixture.write(Path(release["support_contract"]["path"]), contract)
    root, candidate = prepare_invented_candidate(tmp_path / "data", monkeypatch, release)
    packet_bindings = {"task": bound(root / "task.json"), "evidence": bound(root / candidate / "evidence.json"),
                       "registry": bound(root / "registry.json")}
    release["initial_packet"] = fixture.write(Path(release["initial_packet"]["path"]), {
        "schema_version": 1, "kind": "pilot_initial_author_packet", **packet_bindings,
        "files": [*packet_bindings.values(), release["protocol"], release["support_contract"], bound(root / "sources/invented.txt")]})
    (tmp_path / "evaluation_inputs").mkdir()
    evaluation_case = analysis_fixture.case.__wrapped__(tmp_path / "evaluation_inputs", primary)
    release.update(evaluator=evaluation_case["release"]["evaluator"], evaluation=evaluation_case["release"]["evaluation"])
    release["review"] = fixture.review(pilot.release_digest(release))
    controller = fixture.make_controller(release)
    fixture.register(controller, root, candidate, tmp_path)
    frame = analysis_fixture.invented_frame()
    launched = []
    monkeypatch.setattr(pilot.execution, "_runtime_manifest", lambda runtime: {"fixture": "mocked"})
    def capture(command, cwd, timeout, limit, stdout_path, stderr_path):
        launched.append(cwd.name)
        frame.to_csv(cwd / "output/generated.csv", index=False)
        fixture.write(cwd / "output/worker_report.json", {"status": "completed", "generator_started": True})
        stdout_path.write_text("Invented mocked process boundary", encoding="utf-8")
        stderr_path.write_text("", encoding="utf-8")
        return {"returncode": 0, "host_timeout": False, "logs": {}}
    monkeypatch.setattr(pilot.execution, "_capture", capture)
    forbidden = {p.resolve() for p in evaluation_case["reference_paths"]}
    original_open = Path.open
    opened, permitted = [], {"value": False}
    def guarded_open(path, *args, **kwargs):
        if path.resolve() in forbidden:
            assert permitted["value"], "Reference bytes opened before actual controller gate"
            opened.append(str(path.resolve()))
        return original_open(path, *args, **kwargs)
    monkeypatch.setattr(Path, "open", guarded_open)
    with pytest.raises(ValueError):
        primary.evaluate(controller.directory)
    assert not opened
    source_result = controller.dispatch_sources("A01", "initial")["payload"]
    assert source_result["eligibility"]["target_eligible"]
    assert len(source_result["eligibility"]["qualified_coverage"]) == 12
    assert all(c["available"] for c in source_result["eligibility"]["qualified_coverage"])
    assert len(source_result["eligibility"]["support_checks"]) == 9
    fixture.close_other_versions(controller)
    controller.freeze_scientific_inventory()
    controller.dispatch_targets("A01", "initial")
    closed = controller.close_targets()
    assert len(closed["slots"]) == 72
    assert sum(s["role"] == "target" for s in closed["slots"]) == 18
    assert sum(s["status"] == "success" for s in closed["slots"]) == 12
    assert not opened and len(launched) == 12
    controller.authorize_evaluation(release["evaluator"]["sha256"])
    inventory = closed
    assert inventory["scientific_annotations"]["A01/initial"]["source_feedback"]
    for key, annotation in inventory["scientific_annotations"].items():
        if key != "A01/initial":
            assert annotation["unavailable_reason"]
    # Default wrapper gates must call the actual controller, not an invented inventory.
    permitted["value"] = True
    result = primary.evaluate(controller.directory)
    report = primary.read(result["report"])
    assert len(report["slots"]) == report["reserved_target_slots"] == 18
    assert report["failed_or_unrun_slots"] == 15
    assert report["scientific_annotations"]["A01/initial"]["source_discrepancy_reports"][0]["report"]["feedback"] == source_result["feedback"]
    successful = [s for s in report["slots"] if s["status"] == "success"]
    assert len(successful) == 3 and all(s["analysis_error"] is None for s in successful)
    assert all(s["analysis_support"]["E3"]["assessment"] == "unassessed" for s in successful)
    check = independent.recompute(controller.directory)
    assert check["status"] == "matched", independent.read(check["report"])["disagreements"][:10]
    assert len(independent.read(check["report"])["recomputed_slots"]) == 18
    assert opened and len(launched) == 12
    fixture.write(tmp_path / "COMPOSITION_RECEIPT.json", {"status": "passed", "scope": "invented_only_process_boundary_mocked",
        "controller_sha256": pilot.sha256(pilot.__file__), "primary_sha256": primary.sha(primary.__file__),
        "independent_sha256": independent.sha(independent.__file__), "inventory_sha256": inventory["inventory_sha256"],
        "planned_slots": 72, "target_slots": 18, "mocked_source_executions": 9, "mocked_target_executions": 3,
        "actual_generator_processes": 0, "patient_rows_read": 0, "independent_status": check["status"],
        "primary_report": result["report"], "independent_report": check["report"]})
