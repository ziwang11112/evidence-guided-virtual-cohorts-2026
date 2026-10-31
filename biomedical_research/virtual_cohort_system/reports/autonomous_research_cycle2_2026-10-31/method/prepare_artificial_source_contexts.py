"""Write metadata and inert artificial program text; generate no individual table."""
from __future__ import annotations

import argparse
import copy
from pathlib import Path

from cohort_harness import execution
from cohort_harness.lifecycle import freeze_candidate, sha256

PROGRAM = '''import numpy as np
import pandas as pd

def generate(observed, specification, seed):
    if observed is not None:
        raise ValueError("Artificial whole-cohort test rejects observed records")
    parameters = specification["parameters"]
    context = parameters["contexts"][parameters["active_context"]]
    n = context["n_rows"]
    x = context["inputs"]["start"] + parameters["step"] * np.arange(n)
    return pd.DataFrame({"sample_id": [f"artificial_{i}" for i in range(n)], "x": x})
'''


def prepare(destination, *, freeze=True):
    root = Path(destination).absolute()
    if root.exists():
        raise ValueError("Artificial fixture destination already exists")
    candidate = root / "candidates/initial"
    candidate.mkdir(parents=True)
    (root / "sources").mkdir()
    columns = [{"name": "sample_id", "kind": "string", "unit": "identifier", "role": "identifier", "nullable": False},
               {"name": "x", "kind": "number", "unit": "fictional_units", "role": "generated", "nullable": False,
                "minimum": 0, "maximum": 2}]
    contexts = {}
    for identifier, n, start in (("target_design", 3, 0), ("source_a", 4, 10), ("source_b", 6, 20)):
        support = copy.deepcopy(columns)
        support[1].update(minimum=start, maximum=start + n - 1)
        contexts[identifier] = {"population": f"Invented {identifier} arithmetic sequence; no persons or biomedical claim.",
                                "n_rows": n, "columns": support, "inputs": {"start": start}}
    task = {"schema_version": 1, "task_id": "artificial-source-context-bridge", "mode": "whole_cohort",
            "population": contexts["target_design"]["population"], "row_id": "sample_id", "n_rows": 3,
            "columns": columns, "information_policy": {"mode": "published_evidence", "excluded_cohorts": ["reserved_fixture"],
                                                       "allowed_tools": ["artificial_fixture_only"]},
            "budget": {"source_queries": 0, "source_downloads": 0, "revisions": 1}}
    execution._write(root / "task.json", task)
    source = root / "sources/artificial_aggregates.txt"
    source.write_text("Invented aggregate engineering expectations only: source_a mean 11.5; source_b mean 22.5.\n", encoding="utf-8")
    artifact = {"path": "sources/artificial_aggregates.txt", "sha256": sha256(source)}
    execution._write(root / "registry.json", {"artifacts": [{"source_id": "S_artificial", **artifact,
                                                            "origin": "fixture", "screening": "approved"}]})
    items = [{"id": "E_" + identifier, "source_id": "S_artificial", "locator": "artificial_aggregates.txt line 1",
              "variables": ["x"], "kind": "mean", "estimate": estimate, "unit": "fictional_units",
              "uncertainty": {"kind": "not_reported"}, "adjustment": [], "selection": "Full invented sequence",
              "applicability": "Artificial interface test only"}
             for identifier, estimate in (("source_a", 11.5), ("source_b", 22.5))]
    execution._write(candidate / "evidence.json", {"schema_version": 1,
        "sources": [{"id": "S_artificial", "identifier": "fixture:source-context-bridge", "population": "Invented sequences",
                     "measurement": "Fictional units", "cohort_ids": ["invented_bridge"], "artifacts": [artifact]}], "items": items})
    parameters = {"active_context": "target_design", "contexts": contexts, "step": 1}
    execution._write(candidate / "model_spec.json", {"parameters": parameters,
        "assumptions": [{"id": "A_artificial", "description": "Invented deterministic engineering sequence, not a scientific model."}],
        "parameter_provenance": {key: {"evidence_ids": [], "assumption_ids": ["A_artificial"],
                                        "derivation": "Explicit artificial test design."} for key in parameters}})
    (candidate / "generator.py").write_text(PROGRAM, encoding="utf-8")
    (candidate / "decision.md").write_text("Trusted artificial interface fixture. No Agent scientific result or patient data.\n", encoding="utf-8")
    execution._write(candidate / "checks.json", {"scope": "fixture_only", "records": [
        {"name": "preparation", "status": "not_computable", "detail": "No generator has been executed by fixture preparation."}], "artifacts": []})
    entries = []
    for identifier in ("source_a", "source_b"):
        folder = candidate / "source_contexts" / identifier
        folder.mkdir(parents=True)
        child_task = copy.deepcopy(task)
        child_task.update({key: contexts[identifier][key] for key in ("population", "n_rows", "columns")})
        execution._write(folder / "task.json", child_task)
        recipe = {"schema_version": 1, "population": child_task["population"],
                  "measurement": {"mode": "identity", "description": "Same fictional variable/units"},
                  "assumption_ids": ["A_artificial"], "checks": [{"id": "mean_x", "evidence_id": "E_" + identifier,
                    "status": "approximate", "operator": {"kind": "mean", "unit": "fictional_units", "selection": [],
                    "missing_policy": "error", "column": "x"}, "assumption_ids": [], "reason": "Artificial arithmetic wiring check."}]}
        execution._write(folder / "whole_cohort_feedback.json", recipe)
        entries.append({"id": identifier, "task_path": f"source_contexts/{identifier}/task.json",
                        "feedback_path": f"source_contexts/{identifier}/whole_cohort_feedback.json"})
    domain = copy.deepcopy(columns)
    domain[1].update(minimum=0, maximum=30)
    execution._write(candidate / "source_context_plan.json", {"schema_version": 1,
        "model_domain": {"columns": domain, "assumption_ids": ["A_artificial"], "description": "Invented x domain 0 through 30"},
        "contexts": entries})
    if freeze:
        freeze_candidate(root, candidate)
    return root


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", required=True)
    print(prepare(parser.parse_args().destination))
