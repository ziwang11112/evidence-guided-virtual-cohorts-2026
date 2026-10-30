"""Prepare invented study summaries for an actual, separately launched LLM.

This prepares no generator, model parameters or preferred scientific structure.
There are no patient rows or hidden target outcomes. Summaries are engineering
fixtures, not published biomedical findings.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import pandas as pd

from cohort_harness.lifecycle import sha256


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def prepare(destination):
    root = Path(destination).resolve()
    if root.exists():
        raise ValueError("Use a new destination; prior artifacts are preserved")
    root.mkdir(parents=True)
    for folder in ("sources", "allowed_inputs", "candidates", "agent_exchange"):
        (root / folder).mkdir()
    columns = [
        {"name": "id", "kind": "string", "unit": "id", "role": "identifier", "nullable": False},
        {"name": "x", "kind": "number", "unit": "x_unit", "role": "observed", "nullable": False,
         "minimum": -0.5, "maximum": 0.5},
        {"name": "z", "kind": "category", "unit": "code", "role": "observed", "nullable": False,
         "categories": [0, 1]},
        {"name": "y", "kind": "number", "unit": "y_unit", "role": "generated", "nullable": False,
         "minimum": -100, "maximum": 100}]
    task = {"schema_version": 1, "task_id": "m12c-invented-study-composition", "mode": "enrichment",
        "population": "Eight invented target covariate rows; y has never been supplied or evaluated",
        "row_id": "id", "n_rows": 8, "columns": columns,
        "information_policy": {"mode": "published_evidence", "excluded_cohorts": [],
            "allowed_tools": ["local_fixture_only"]},
        "budget": {"source_queries": 0, "source_downloads": 0, "revisions": 3}}
    write(root / "task.json", task)
    pd.DataFrame({"id": ["target_%d" % i for i in range(8)], "x": [-.5, .5, -.25, .25]*2,
                  "z": [0]*4+[1]*4}).to_csv(root / "observed.csv", index=False)
    records, evidence_sources, items = [], [], []
    for name, n_zero, mean in (("A", 80, 11/3), ("B", 40, 13/3)):
        source_id = "S" + name
        source = root / "sources" / (name + ".txt")
        source.write_text(
            "INVENTED STUDY SUMMARY. NOT A REAL PAPER OR PATIENT DATA.\n"
            f"Study {name}: 120 observations; z=0: {n_zero}, z=1: {120-n_zero}.\n"
            "x takes -1 and +1 equally often within each z category. Both variables are measured without error in this fixture.\n"
            f"Mean(y) = {mean:.16g}; sample SD(y), denominator n-1, = {math.sqrt(2120/357):.16g}.\n"
            "Ordinary least squares y ~ intercept + x + z: adjusted coefficient of x = 2 y_unit/x_unit.\n"
            "No coefficient of z, conditional mean function, residual distribution or individual y records is supplied.\n"
            "Both studies use identical units and measurement definitions. Different participants, no overlap.\n"
            "These exact summaries are computational constraints. Sampling standard errors are not supplied.\n",
            encoding="utf-8")
        artifact = {"path": "sources/" + name + ".txt", "sha256": sha256(source)}
        records.append({"source_id": source_id, **artifact, "origin": "fixture", "screening": "approved"})
        evidence_sources.append({"id": source_id, "identifier": "fixture:study-"+name,
            "population": f"Invented study {name}, n=120, z=0:{n_zero}, z=1:{120-n_zero}",
            "measurement": "Identical invented x_unit, y_unit and numeric category z in both studies",
            "cohort_ids": ["invented-study-"+name], "artifacts": [artifact]})
        common = {"source_id": source_id, "locator": name+".txt lines 2-4", "uncertainty": {"kind": "not_reported"},
            "adjustment": [], "selection": "All 120 study rows", "applicability": "Invented source fitting only; no target validity"}
        items += [
            {"id": name+"_mean", **common, "kind": "mean", "variables": ["y"], "estimate": mean, "unit": "y_unit"},
            {"id": name+"_sd", **common, "kind": "sd", "variables": ["y"], "estimate": math.sqrt(2120/357), "unit": "y_unit"},
            {"id": name+"_beta", **common, "locator": name+".txt line 5", "kind": "ols_coefficient",
             "variables": ["x", "y"], "adjustment": ["z"], "estimate": 2, "unit": "y_unit/x_unit"}]
        frame = pd.DataFrame({"id": [f"{name}_{i}" for i in range(120)],
                              "x": [-1, 1]*60, "z": [0]*n_zero+[1]*(120-n_zero)})
        frame.to_csv(root / "allowed_inputs" / (name+"_covariates.csv"), index=False)
    write(root / "registry.json", {"artifacts": records})
    write(root / "allowed_inputs/evidence.json", {"schema_version": 1, "sources": evidence_sources, "items": items})
    controls = {"scope": "invented_source_only_agent_integration", "fit_seeds": [1301, 1302],
        "replay_seeds": [2301, 2302], "max_trials_per_session": 9, "max_sessions": 2,
        "max_contexts": 2, "loss_scales": {"mean": 1, "sd": 1, "ols_coefficient": 1},
        "target_loss": 0.04, "target_loss_role": "Predetermined engineering tolerance, not clinical equivalence",
        "execution": {"timeout_seconds": 30, "memory_mb": 1024, "output_bytes": 100000, "log_bytes": 10000},
        "scientific_loop": {"max_actions": 3, "max_promotions": 1},
        "allowed_candidate_name": "initial", "source_task_x_bounds": [-1, 1], "model_x_bounds": [-2, 2]}
    write(root / "allowed_inputs/controller_contract.json", controls)
    manifest = {p.relative_to(root).as_posix(): sha256(p) for p in sorted(root.rglob("*")) if p.is_file()}
    write(root / "agent_exchange/initial_input_manifest.json", {"files": manifest})
    return root


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", required=True)
    print(prepare(parser.parse_args().destination))
