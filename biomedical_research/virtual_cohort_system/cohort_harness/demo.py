"""Invented interface fixture. Contains no patients, literature or hidden answers."""
from pathlib import Path
import hashlib
import json

import pandas as pd


def write_json(path, value):
    with Path(path).open("x", encoding="utf-8") as out:
        json.dump(value, out, indent=2, allow_nan=False)
        out.write("\n")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def make_demo(destination):
    root = Path(destination).resolve()
    if root.exists():
        raise ValueError("Demo destination must not exist; previous artifacts are preserved")
    root.mkdir(parents=True)
    source_dir = root / "sources"
    source_dir.mkdir()
    candidate = root / "candidates" / "initial"
    (candidate / "source_tables").mkdir(parents=True)
    task = {
        "schema_version": 1, "task_id": "invented-interface-demo", "mode": "enrichment",
        "population": "Seven invented rows for interface testing only; not a biomedical cohort.",
        "row_id": "sample_id", "n_rows": 7,
        "columns": [
            {"name": "sample_id", "kind": "string", "unit": "identifier", "role": "identifier", "nullable": False},
            {"name": "x", "kind": "number", "unit": "x_unit", "role": "observed", "nullable": False},
            {"name": "y", "kind": "number", "unit": "y_unit", "role": "generated", "nullable": False}],
        "information_policy": {"mode": "published_evidence", "excluded_cohorts": [], "allowed_tools": ["local_fixture_only"]},
        "budget": {"source_queries": 0, "source_downloads": 0, "revisions": 1}}
    write_json(root / "task.json", task)
    observed = pd.DataFrame({"sample_id": [f"demo_{i}" for i in range(7)], "x": list(range(7))})
    observed.to_csv(root / "observed.csv", index=False)
    generated = observed.assign(y=1 + 2 * observed.x)
    generated.to_csv(candidate / "generated.csv", index=False)
    generated[["x", "y"]].to_csv(candidate / "source_tables" / "invented.csv", index=False)
    source_path = source_dir / "invented_summary.txt"
    source_path.write_text("ARTIFICIAL FIXTURE, NOT A PAPER. x=0,...,6; y=1+2x. Mean(y)=7. OLS y~1+x slope=2.\n", encoding="utf-8")
    artifact = {"path": "sources/invented_summary.txt", "sha256": digest(source_path)}
    write_json(root / "registry.json", {"artifacts": [{"source_id": "S1", **artifact, "origin": "fixture", "screening": "approved"}]})
    common = {"source_id": "S1", "locator": "invented_summary.txt line 1", "variables": ["x", "y"],
              "uncertainty": {"kind": "not_reported"}, "adjustment": [], "selection": "All seven invented rows",
              "applicability": "Interface fixture only; no transport or biomedical interpretation"}
    evidence = {"schema_version": 1,
                "sources": [{"id": "S1", "identifier": "fixture:invented-summary", "population": task["population"],
                             "measurement": "Exact invented numbers", "cohort_ids": ["invented-demo"], "artifacts": [artifact]}],
                "items": [{"id": "E1", **common, "variables": ["y"], "kind": "mean", "estimate": 7, "unit": "y_unit"},
                          {"id": "E2", **common, "kind": "ols_coefficient", "estimate": 2, "unit": "y_unit/x_unit"}]}
    write_json(candidate / "evidence.json", evidence)
    write_json(candidate / "model_spec.json", {
        "parameters": {"intercept": 1, "slope": 2},
        "assumptions": [{"id": "A1", "description": "Deterministic invented fixture, not a scientific stochastic generator."}],
        "parameter_provenance": {
            "intercept": {"evidence_ids": ["E1", "E2"], "assumption_ids": ["A1"], "derivation": "7 - 2*mean(0,...,6)=1"},
            "slope": {"evidence_ids": ["E2"], "assumption_ids": ["A1"], "derivation": "Illustrative source slope 2"}}})
    (candidate / "decision.md").write_text("This is a deterministic fixture for contract and operator tests. No Agent or biomedical quality claim.\n", encoding="utf-8")
    table = {"path": "source_tables/invented.csv", "sha256": digest(candidate / "source_tables/invented.csv"), "origin": "fixture"}
    common_check = {"status": "computed", "table": table, "assumption_ids": [], "reason": "Arithmetic on the exact invented table"}
    write_json(candidate / "source_checks.json", {"schema_version": 1, "checks": [
        {"id": "C1", "evidence_id": "E1", **common_check,
         "operator": {"kind": "mean", "unit": "y_unit", "selection": [], "missing_policy": "error", "column": "y"}},
        {"id": "C2", "evidence_id": "E2", **common_check,
         "operator": {"kind": "ols_coefficient", "unit": "y_unit/x_unit", "selection": [], "missing_policy": "error",
                      "outcome": "y", "predictors": ["x"], "term": "x", "include_intercept": True}}]})
    write_json(candidate / "checks.json", {
        "scope": "fixture_only", "records": [{"name": "fixture_table_created", "status": "pass",
        "detail": "Constructed the stated seven-row deterministic fixture; this is not generator or target validation."}],
        "artifacts": [{"path": table["path"], "sha256": table["sha256"]}]})
    return root
