"""Reusable, deliberately invented bridge fixture. No approvals or runs created.

build_parent(path) exclusively writes and freezes a source/target parent. Its
small deterministic generator is source code only until the isolated adapter
is explicitly called. All x values, units, populations and evidence are invented.
"""
from pathlib import Path
import copy

from cohort_harness import execution, lifecycle
import context_bridge as bridge


GENERATOR = '''"""Invented arithmetic fixture, no biomedical parameters."""
import pandas as pd

def generate(observed, specification, seed):
    context = specification["parameters"]["contexts"][specification["parameters"]["active_context"]]
    n = context["n_rows"]
    return pd.DataFrame({"id": ["fixture-" + str(i) for i in range(n)],
                         "x": [specification["parameters"]["scale"] * float(2 ** (i % 3)) for i in range(n)]})
'''


def build_parent(path):
    """Return a new frozen invented bundle path; never launch generator/reviewer."""
    root = Path(path).absolute()
    root.mkdir(parents=True, exist_ok=False)
    directory = root / "candidates/invented"
    directory.mkdir(parents=True)
    source_path = root / "sources/invented.txt"
    source_path.parent.mkdir()
    source_path.write_text("Invented fixture only. Geometric mean 2 example_unit. No actual source study.\n", encoding="utf-8")
    source_hash = lifecycle.sha256(source_path)
    task = {"schema_version": 1, "task_id": "invented-bridge", "mode": "whole_cohort", "population": "Invented target context",
            "row_id": "id", "n_rows": 6,
            "columns": [{"name": "id", "kind": "string", "unit": "1", "role": "identifier", "nullable": False},
                        {"name": "x", "kind": "number", "unit": "example_unit", "role": "generated", "nullable": False}],
            "information_policy": {"mode": "published_evidence", "excluded_cohorts": ["forbidden-target"], "allowed_tools": []},
            "budget": {"source_queries": 0, "source_downloads": 0, "revisions": 0}}
    evidence = {"schema_version": 1, "sources": [
        {"id": "invented-source", "identifier": "invented:fixture", "population": "Invented source context", "measurement": "Invented measurement",
         "cohort_ids": ["invented-source"], "artifacts": [{"path": "sources/invented.txt", "sha256": source_hash}]}],
        "items": [{"id": "invented-geo", "source_id": "invented-source", "locator": "Invented text line 1", "variables": ["x"],
                   "kind": "reported_other", "statistic_name": "geometric_mean", "estimate": 2.0, "unit": "example_unit",
                   "uncertainty": {"kind": "not_reported"}, "adjustment": [], "selection": "All invented rows",
                   "applicability": "Invented arithmetic fixture; no real scientific evidence"}]}
    spec = {"parameters": {"active_context": "target", "scale": 1.0, "contexts": {
                "source": {"population": "Invented source context", "n_rows": 3, "measurement": "Invented measurement", "inputs": {}},
                "target": {"population": task["population"], "n_rows": 6, "measurement": "Invented measurement", "inputs": {}}}},
            "assumptions": [{"id": "fixture", "description": "Invented source and target arithmetic contexts; no transport claim"}],
            "parameter_provenance": {key: {"evidence_ids": [], "assumption_ids": ["fixture"], "derivation": "Invented mechanical fixture"}
                                     for key in ("active_context", "contexts", "scale")}}
    recipe = {"schema_version": 1, "population": "Invented source context", "measurement": {"mode": "identity", "description": "Invented measurement"},
              "assumption_ids": ["fixture"], "checks": [{"id": "native-geo", "evidence_id": "invented-geo", "status": "not_computable",
              "operator": None, "assumption_ids": [], "reason": "Frozen semantic v1 does not implement geometric mean"}]}
    semantics = {"schema_version": 1, "evidence_sha256": "", "recipe_sha256": "", "bindings": [{
        "check_id": "native-geo", "evidence_id": "invented-geo", "source_locator": "Invented text line 1",
        "definition_status": "unsupported", "source_operator": None, "weights": "not_reported", "transform": "identity",
        "source_variable_units": {}, "source_n": {"status": "not_reported"}, "uncertainty_role": "not_reported",
        "reason": "Invented original statistic retained without unsupported v1 arithmetic"}]}
    operator = {"kind": "geometric_mean", "column": "x", "unit": "example_unit", "selection": [],
                "selection_missing_policy": "error", "missing_policy": "error"}
    table_context = {"kind": "source_context_simulation", "context_id": "source", "population": "Invented source context",
                     "measurement": "Invented measurement", "variable_units": {"x": "example_unit"}, "variable_scales": {"x": "original"}}
    source_context = {key: copy.deepcopy(value) for key, value in table_context.items() if key != "kind"}
    source_context.update(source_id="invented-source", locator="Invented text line 1", operator=copy.deepcopy(operator),
                          weights="not_reported", definition_status="specified", uncertainty_role="not_reported")
    declaration = {"schema_version": 1, "task_sha256": "", "evidence_sha256": "", "model_spec_sha256": "", "semantics_sha256": "",
                   "table_context": table_context, "assumption_ids": ["fixture"], "context_review": None,
                   "checks": [{"id": "supp-geo", "evidence_id": "invented-geo", "semantic_check_id": "native-geo",
                               "operator": operator, "source": source_context, "proxy": None}]}
    plan = {"schema_version": 1, "shared_parameters": ["scale"], "context_varying_parameters": [], "contexts": [
        {"id": "source", "role": "source", "source_ids": ["invented-source"], "assumption_ids": ["fixture"],
         "feedback_policy": "semantic_v1_plus_supplement", "recipe": recipe, "semantics": semantics, "supplement": declaration},
        {"id": "target", "role": "target", "source_ids": [], "assumption_ids": ["fixture"],
         "feedback_policy": "none", "recipe": None, "semantics": None, "supplement": None}],
        "trials": [{"id": "source-one", "context_id": "source", "seed": 101, "n_rows": 3},
                   {"id": "target-one", "context_id": "target", "seed": 103, "n_rows": 6}],
        "execution_limits": {"timeout_seconds": 30, "memory_mb": 1024, "output_bytes": 2000000, "log_bytes": 10000},
        "budget": {"source_attempts": 1, "source_rows": 3, "target_attempts": 1, "target_rows": 6}}
    for path, value in [(root / "task.json", task), (root / "registry.json", {"artifacts": [{"source_id": "invented-source", "path": "sources/invented.txt",
        "sha256": source_hash, "origin": "fixture", "screening": "approved"}]}), (directory / "evidence.json", evidence),
        (directory / "model_spec.json", spec), (directory / bridge.PLAN, plan), (directory / "checks.json", {
            "scope": "fixture_only", "records": [{"name": "no-prior-execution", "status": "not_computable", "detail": "Source code fixture has not run"}], "artifacts": []})]:
        execution._write(path, value)
    (directory / "generator.py").write_text(GENERATOR, encoding="utf-8")
    (directory / "decision.md").write_text("Invented arithmetic fixture for mechanical bridge verification only.\n", encoding="utf-8")
    lifecycle.freeze_candidate(root, directory)
    return root
