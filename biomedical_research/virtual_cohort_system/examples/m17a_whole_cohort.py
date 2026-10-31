"""Prepare an aggregate-only artificial whole-cohort interface fixture.

No generation or execution occurs here. The supplied program is trusted test
code, not an Agent scientific proposal or a biomedical model.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


PROGRAM = '''import numpy as np
import pandas as pd

def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("Whole-cohort fixture cannot use observed rows")
    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    n = p["n_rows"]
    x = rng.normal(p["x_mean"], p["x_sd"], n)
    group = rng.binomial(1, p["group_probability"], n)
    y = p["offset"] + p["slope"] * x + p["group_shift"] * group + rng.normal(0, p["noise_sd"], n)
    return pd.DataFrame({"sample_id": [f"fictional_{i}" for i in range(n)], "x": x, "group": group, "y": y})
'''


def write(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def prepare(destination, n_rows=128):
    if type(n_rows) is not int or n_rows < 8:
        raise ValueError("Use an integer n_rows >= 8")
    root = Path(destination).resolve()
    if root.exists():
        raise ValueError("Fixture destination must not exist")
    root.mkdir(parents=True)
    candidate = root / "candidates/initial"
    candidate.mkdir(parents=True)
    (root / "sources").mkdir()
    population = "Artificial independent x/group population for interface testing only; no patients."
    task = {"schema_version": 1, "task_id": "m17a-artificial-whole-cohort", "mode": "whole_cohort",
            "population": population, "row_id": "sample_id", "n_rows": n_rows,
            "columns": [
                {"name": "sample_id", "kind": "string", "unit": "identifier", "role": "identifier", "nullable": False},
                {"name": "x", "kind": "number", "unit": "x_unit", "role": "generated", "nullable": False},
                {"name": "group", "kind": "category", "categories": [0, 1], "unit": "1", "role": "generated", "nullable": False},
                {"name": "y", "kind": "number", "unit": "y_unit", "role": "generated", "nullable": False}],
            "information_policy": {"mode": "published_evidence", "excluded_cohorts": [], "allowed_tools": ["local_fixture_only"]},
            "budget": {"source_queries": 0, "source_downloads": 0, "revisions": 1}}
    write(root / "task.json", task)
    source = root / "sources/artificial_aggregate_brief.txt"
    source.write_text("ARTIFICIAL AGGREGATE FIXTURE, NOT A PUBLICATION OR PATIENT DATA.\n"
                      "Population expectations: mean(x)=0; SD(x)=1; P(group=1)=0.5; mean(y)=1.3.\n"
                      "Adjusted OLS y~1+x+group: coefficient(x)=0.75; coefficient(group)=0.6.\n"
                      "The group-zero mean is 1.0. Residual SD 0.8 and distribution families are test-design assumptions.\n",
                      encoding="utf-8")
    artifact = {"path": "sources/artificial_aggregate_brief.txt", "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}
    write(root / "registry.json", {"artifacts": [{"source_id": "S_fixture", **artifact, "origin": "fixture", "screening": "approved"}]})
    base = {"source_id": "S_fixture", "locator": "artificial_aggregate_brief.txt lines 2-4",
            "uncertainty": {"kind": "not_reported"}, "selection": "Artificial population expectation",
            "applicability": "Mechanical test only; finite synthetic draws fluctuate around these expectations."}
    items = [
        {"id": "E_x_mean", **base, "variables": ["x"], "adjustment": [], "kind": "mean", "estimate": 0.0, "unit": "x_unit"},
        {"id": "E_x_sd", **base, "variables": ["x"], "adjustment": [], "kind": "sd", "estimate": 1.0, "unit": "x_unit"},
        {"id": "E_group", **base, "variables": ["group"], "adjustment": [], "kind": "proportion", "estimate": 0.5, "unit": "1"},
        {"id": "E_y_mean", **base, "variables": ["y"], "adjustment": [], "kind": "mean", "estimate": 1.3, "unit": "y_unit"},
        {"id": "E_slope", **base, "variables": ["x", "y"], "adjustment": ["group"], "kind": "ols_coefficient", "estimate": 0.75, "unit": "y_unit/x_unit"},
        {"id": "E_group_shift", **base, "variables": ["group", "y"], "adjustment": ["x"], "kind": "ols_coefficient", "estimate": 0.6, "unit": "y_unit"},
        {"id": "E_offset", **base, "variables": ["y"], "adjustment": [], "selection": "group=0", "kind": "mean", "estimate": 1.0, "unit": "y_unit"}]
    write(candidate / "evidence.json", {"schema_version": 1,
          "sources": [{"id": "S_fixture", "identifier": "fixture:m17a-aggregate-brief", "population": population,
                       "measurement": "Artificial unit labels", "cohort_ids": ["invented-m17a"], "artifacts": [artifact]}], "items": items})
    params = {"n_rows": n_rows, "x_mean": 0.0, "x_sd": 1.0, "group_probability": 0.5,
              "offset": 1.0, "slope": 0.75, "group_shift": 0.6, "noise_sd": 0.8}
    refs = {"x_mean": "E_x_mean", "x_sd": "E_x_sd", "group_probability": "E_group", "offset": "E_offset",
            "slope": "E_slope", "group_shift": "E_group_shift"}
    write(candidate / "model_spec.json", {"parameters": params,
          "assumptions": [{"id": "A_fixture", "description": "Trusted invented linear-Gaussian test with independent x/group; no biomedical claim. Finite draws are approximate source checks."}],
          "parameter_provenance": {key: {"evidence_ids": [refs[key]] if key in refs else [],
              "assumption_ids": ["A_fixture"], "derivation": "Explicit artificial test-design value; not a fitted patient parameter."} for key in params}})
    def op(kind, unit, **kwargs):
        return {"kind": kind, "unit": unit, "selection": [], "missing_policy": "error", **kwargs}
    definitions = [
        ("x_mean", "E_x_mean", op("mean", "x_unit", column="x")),
        ("x_sd", "E_x_sd", op("sd", "x_unit", column="x")),
        ("group_proportion", "E_group", op("proportion", "1", event={"column": "group", "op": "eq", "value": 1})),
        ("y_mean", "E_y_mean", op("mean", "y_unit", column="y")),
        ("adjusted_slope", "E_slope", op("ols_coefficient", "y_unit/x_unit", outcome="y", predictors=["x", "group"], term="x", include_intercept=True))]
    write(candidate / "whole_cohort_feedback.json", {"schema_version": 1, "population": population,
          "measurement": {"mode": "identity", "description": "Same artificial variable names and units."},
          "assumption_ids": ["A_fixture"], "checks": [{"id": key, "evidence_id": evidence_id, "status": "approximate",
            "operator": operator, "assumption_ids": [], "reason": "Compare the verified artificial output with the supplied population expectation."}
            for key, evidence_id, operator in definitions]})
    (candidate / "generator.py").write_text(PROGRAM, encoding="utf-8")
    (candidate / "decision.md").write_text("Trusted preparation-only interface fixture. No Agent scientific proposal, patient rows or hidden target. No generation has been run by preparation.\n", encoding="utf-8")
    write(candidate / "checks.json", {"scope": "fixture_only", "records": [{"name": "generator_execution",
          "status": "not_computable", "detail": "Preparation wrote task/evidence/program metadata; generator execution has not been attempted."}], "artifacts": []})
    return root


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--n-rows", type=int, default=128)
    args = parser.parse_args()
    print(prepare(args.destination, args.n_rows))
