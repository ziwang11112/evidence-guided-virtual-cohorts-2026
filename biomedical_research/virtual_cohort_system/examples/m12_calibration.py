"""Invented M12-B calibration fixture; no clinical or Agent performance claim.

Run from the project root with ``python -m examples.m12_calibration --destination
<new-directory> --runtime work/m2-runtime-config.json``. The CLI uses the existing
WSL/bubblewrap adapter. It never imports or runs the candidate on the host.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
from pathlib import Path

import pandas as pd

from cohort_harness import calibration, calibration_budget as budget
from cohort_harness.lifecycle import freeze_candidate, read_json, sha256, verify_candidate

# Literal invented arithmetic, independently specified before the generator.
# Columns x, z, y. This table is evidence, never a replay covariate input.
REFERENCE = [(-1, 0, 0), (-1, 0, 2), (1, 0, 4), (1, 0, 6),
             (-1, 0, 0), (-1, 0, 2), (1, 0, 4), (1, 0, 6),
             (-1, 1, 2), (-1, 1, 4), (1, 1, 6), (1, 1, 8)]
EXPECTED = {"intercept": 3.0, "slope": 2.0, "noise_scale": 1.0}
PROGRAM = """def generate(observed, spec, seed):
    import numpy as np
    out = observed.copy()
    p = spec['parameters']
    residual = np.asarray([-1 if i % 2 == 0 else 1 for i in range(len(out))])
    sign = 1 if seed % 2 else -1
    out['y'] = (p['intercept'] + p['slope'] * out['x'].astype(float)
                + p['z_effect'] * out['z'].astype(float)
                + p['noise_scale'] * sign * residual)
    return out
"""


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def budget_limits(plan):
    """One context and one session; reserve the full schedule, including initial."""
    trials = plan["optimizer"]["max_trials"]
    executions = trials * len(plan["fit_seeds"]) + len(plan["replay_seeds"])
    return {"sessions": 1, "trials": trials, "executions": executions,
            "reserved_seconds": executions * plan["execution"]["timeout_seconds"]}


def build_fixture(destination, incompatible=False, noncomputable=False):
    """Return (bundle, frozen_candidate, plan); caller creates the fixed budget.

    incompatible adds a second, deliberately conflicting mean constraint.
    noncomputable restricts the adjusted regression to z=0, making its design
    rank deficient. Neither variant silently drops the problematic constraint.
    """
    root = Path(destination).resolve()
    if root.exists():
        raise ValueError("Fixture destination must be new; existing artifacts are preserved")
    candidate = root / "candidates/p"
    candidate.mkdir(parents=True)
    (root / "sources").mkdir()
    columns = [
        {"name": "id", "kind": "string", "unit": "id", "role": "identifier", "nullable": False},
        {"name": "x", "kind": "number", "unit": "x_unit", "role": "observed", "nullable": False,
         "minimum": -0.5, "maximum": 0.5},
        {"name": "z", "kind": "category", "unit": "code", "role": "observed", "nullable": False,
         "categories": [0, 1]},
        {"name": "y", "kind": "number", "unit": "y_unit", "role": "generated", "nullable": False,
         "minimum": -20, "maximum": 20}]
    task = {"schema_version": 1, "task_id": "m12-invented-calibration", "mode": "enrichment",
        "population": "Four invented covariate rows; no target reference exists", "row_id": "id", "n_rows": 4,
        "columns": columns, "information_policy": {"mode": "published_evidence", "excluded_cohorts": [],
        "allowed_tools": ["local_fixture_only"]}, "budget": {"source_queries": 0, "source_downloads": 0, "revisions": 0}}
    write(root / "task.json", task)
    pd.DataFrame({"id": ["t0", "t1", "t2", "t3"], "x": [-0.5, 0.5, -0.5, 0.5],
                  "z": [0, 0, 1, 1]}).to_csv(root / "observed.csv", index=False)
    reference = pd.DataFrame(REFERENCE, columns=["x", "z", "y"])
    reference.to_csv(root / "sources/reference.csv", index=False)
    artifacts = [{"path": "sources/reference.csv", "sha256": sha256(root / "sources/reference.csv")}]
    if incompatible:
        # A second literal table with the same covariates and a different mean.
        conflicting = [2, 4, 6, 8, 2, 4, 6, 8, 4, 6, 8, 10]
        reference.assign(y=conflicting).to_csv(root / "sources/conflict.csv", index=False)
        artifacts.append({"path": "sources/conflict.csv", "sha256": sha256(root / "sources/conflict.csv")})
    write(root / "registry.json", {"artifacts": [{"source_id": "S1", **a, "origin": "fixture",
                                                   "screening": "approved"} for a in artifacts]})
    covariates = reference[["x", "z"]].copy()
    covariates.insert(0, "id", ["s%d" % i for i in range(len(reference))])
    covariates.to_csv(candidate / "cov.csv", index=False)
    common = {"source_id": "S1", "locator": "reference.csv, all 12 literal invented rows",
        "uncertainty": {"kind": "not_reported"}, "adjustment": [], "selection": "All 12 invented rows",
        "applicability": "Arithmetic software fixture only; no biomedical or target validity"}
    items = [
        {"id": "M", **common, "variables": ["y"], "kind": "mean", "estimate": 11 / 3, "unit": "y_unit"},
        {"id": "B", **common, "variables": ["x", "y"], "adjustment": ["z"], "kind": "ols_coefficient",
         "estimate": 2, "unit": "y_unit/x_unit"},
        {"id": "D", **common, "variables": ["y"], "kind": "sd", "estimate": math.sqrt(212 / 33), "unit": "y_unit"}]
    if incompatible:
        items.append({"id": "I", **common, "locator": "conflict.csv, all 12 literal invented rows",
            "variables": ["y"], "kind": "mean", "estimate": 17 / 3, "unit": "y_unit"})
    write(candidate / "evidence.json", {"schema_version": 1, "sources": [{"id": "S1",
        "identifier": "fixture:literal-arithmetic-m12b", "population": "Invented 8:4 mixture of z=0 and z=1",
        "measurement": "Literal unitless-in-substance arithmetic values; not measurements",
        "cohort_ids": ["invented-m12b"], "artifacts": artifacts}], "items": items})
    parameters = {"intercept": 1, "slope": 1, "noise_scale": 0.5, "z_effect": 2}
    write(candidate / "model_spec.json", {"parameters": parameters,
        "assumptions": [{"id": "A", "description": "Invented additive structure and fixed orthogonal residual pattern; no clinical interpretation"}],
        "parameter_provenance": {name: {"evidence_ids": [], "assumption_ids": ["A"],
            "derivation": "Predeclared invented starting value; z_effect is fixed and excluded from calibration"}
                                 for name in parameters}})
    (candidate / "generator.py").write_text(PROGRAM, encoding="utf-8")
    (candidate / "decision.md").write_text(
        "Numerical calibration fixture only. All scientific structure and the z effect are fixed.\n"
        "The twelve source rows have x centered within z; the alternating residual is orthogonal to 1, x, z.\n"
        "No target outcome exists. Incompatible references or rank deficiency are deliberate negative controls.\n",
        encoding="utf-8")
    write(candidate / "checks.json", {"scope": "fixture_only", "records": [{"name": "execution_pending",
        "status": "not_computable", "detail": "The frozen generator has not been executed; literal evidence is not generator validation"}],
        "artifacts": []})
    base = {"unit": "y_unit", "selection": [], "missing_policy": "error"}
    operators = [
        ("mean", "M", {**base, "kind": "mean", "column": "y"}),
        ("beta", "B", {**base, "kind": "ols_coefficient", "unit": "y_unit/x_unit", "outcome": "y",
                         "predictors": ["x", "z"], "term": "x", "include_intercept": True}),
        ("sd", "D", {**base, "kind": "sd", "column": "y"})]
    if noncomputable:
        operators[1][2]["selection"] = [{"column": "z", "op": "eq", "value": 0}]
    if incompatible:
        operators.append(("conflict", "I", {**base, "kind": "mean", "column": "y"}))
    checks = [{"id": name, "evidence_id": evidence_id, "status": "approximate", "operator": operator,
        "assumption_ids": ["A"], "reason": "Declared invented arithmetic context; negative controls are intentional"}
        for name, evidence_id, operator in operators]
    source_columns = copy.deepcopy(columns)
    source_columns[1].update(minimum=-1, maximum=1)
    domain = copy.deepcopy(source_columns)
    domain[1].update(minimum=-2, maximum=2)
    context = {"id": "s", "population": "Twelve invented rows with unbalanced z mixture",
        "reason": "Fixed source population for numerical fixture only", "assumption_ids": ["A"],
        "measurement": {"mode": "identity", "description": "Identical invented units"},
        "input": {"path": "cov.csv", "sha256": sha256(candidate / "cov.csv"), "origin": "declared_source_covariates"},
        "columns": source_columns, "checks": checks}
    write(candidate / "source_replay_v2.json", {"schema_version": 2, "model_domain": {"columns": domain,
        "assumption_ids": ["A"], "description": "Fixed computational support for every trial"}, "contexts": [context]})
    plan = {"schema_version": 1, "parameters": [
        {"name": "intercept", "lower": 0, "upper": 5, "step": 0.5},
        {"name": "slope", "lower": 0, "upper": 3, "step": 0.5},
        {"name": "noise_scale", "lower": 0, "upper": 2, "step": 0.5}],
        "constraints": [{"context_id": "s", "check_id": c["id"], "scale": 1,
                         "scale_reason": "Predeclared one numerical unit in this invented statistic's units"} for c in checks],
        "fit_seeds": [101, 102], "replay_seeds": [201, 202], "noncomputable": "infeasible",
        "optimizer": {"method": "bounded_coordinate_search", "max_trials": 3 if incompatible or noncomputable else 25, "shrink": 0.5,
                      "min_step_fraction": 0.01, "target_loss": 1e-20},
        "execution": {"timeout_seconds": 30, "memory_mb": 1024, "output_bytes": 100000, "log_bytes": 10000}}
    write(root / "calibration_plan.json", plan)
    (root / "README.md").write_text(
        "# Invented M12-B calibration fixture\n\n"
        "No patients, target outcomes or clinical interpretation. Covariates are id,x,z; y is generated.\n"
        "Source z counts are 8 and 4. Within each z, x is centered. Residual (-1,1,-1,1) repeats three times.\n"
        "Literal reference y=(0,2,4,6,0,2,4,6,2,4,6,8). Mean=11/3; adjusted x coefficient=2; sample SD=sqrt(212/33).\n"
        "Sum(x^2)=12, sum((z-1/3)^2)=8/3, sum(residual^2)=12; cross products vanish.\n"
        "Fixed model y=a+b*x+2*z+c*residual uses a seed-dependent residual sign. This preserves all three checks.\n"
        "Initial (a,b,c)=(1,1,0.5); reference (3,2,1); steps all 0.5; maximum 25 trials includes the initial trial.\n"
        "Fit seeds 101,102; independent replay seeds 201,202. All source checks enter the fixed scaled objective.\n"
        "Negative controls use only three trials. The incompatible variant adds mean 17/3; its objective is bounded below by 0.5 analytically.\n"
        "The noncomputable variant makes adjusted OLS rank deficient.\n"
        "Tests use a labeled mock backend. The CLI requires a real runtime configuration and routes through WSL/bubblewrap.\n",
        encoding="utf-8")
    freeze_candidate(root, candidate)
    return root, candidate, plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--runtime", required=True)
    parser.add_argument("--incompatible", action="store_true")
    parser.add_argument("--noncomputable", action="store_true")
    args = parser.parse_args()
    root, candidate, plan = build_fixture(args.destination, args.incompatible, args.noncomputable)
    before = {str(p.relative_to(root)): sha256(p) for p in
              [root / "task.json", candidate / "freeze.json", candidate / "model_spec.json", candidate / "generator.py"]}
    budget.create_budget(root, budget_limits(plan))
    result = calibration.run_calibration(root, candidate, "s", plan, runtime=read_json(args.runtime))
    assert result == calibration.verify_calibration(root, "s")
    assert before == {name: sha256(root / name) for name in before}
    verify_candidate(root, candidate)
    chosen = result["selected_trial"]
    if args.noncomputable:
        assert result["status"] == "no_feasible_trial" and chosen is None
    elif args.incompatible:
        assert result["status"] == "fit_threshold_not_met"
    else:
        assert result["status"] == "fit_threshold_met"
        assert result["trials"][chosen]["parameters"] == EXPECTED and result["replay"]["feasible"]
    summary = {"scope": "invented arithmetic and real isolated execution only", "status": result["status"],
        "trials": len(result["trials"]), "selected_parameters": None if chosen is None else result["trials"][chosen]["parameters"],
        "replay_feasible": None if result["replay"] is None else result["replay"]["feasible"],
        "parent_bytes_unchanged": True, "biomedical_utility_tested": False,
        "result_path": str(root / "cal/s/result.json")}
    write(root / "m12_calibration_result.json", summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
