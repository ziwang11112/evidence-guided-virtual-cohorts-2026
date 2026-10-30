"""Prepare real-source, source-only Agent tasks; no target patient data or generator."""
from pathlib import Path
import itertools
import json
import shutil

import pandas as pd
from cohort_harness.contracts import validate_input
from cohort_harness.lifecycle import sha256

P = Path(__file__).resolve().parents[2]


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def prepare(name):
    root = P / "work/m13" / name
    if root.exists():
        raise ValueError("Preserve previous bundle; destination must be new")
    for folder in ("sources", "allowed_inputs", "candidates", "agent_exchange"):
        (root / folder).mkdir(parents=True, exist_ok=True)
    columns = [{"name": "id", "kind": "string", "unit": "id", "role": "identifier", "nullable": False}]
    for label, unit, bounds in [
        ("age", "years", [20, 59]), ("bmi", "kg/m2", [18.5, 35]),
    ]:
        columns.append({"name": label, "kind": "number", "unit": unit, "role": "observed", "nullable": False,
                        "minimum": bounds[0], "maximum": bounds[1]})
    for label, categories in [("male", [0, 1]), ("asian", [0])]:
        columns.append({"name": label, "kind": "category", "unit": "code", "role": "observed", "nullable": False,
                        "categories": categories})
    for label, unit in [("inv_bmi", "m2/kg"), ("male_inv_bmi", "m2/kg"), ("asian_inv_bmi", "m2/kg"),
                        ("male_age", "years"), ("asian_age", "years")]:
        columns.append({"name": label, "kind": "number", "unit": unit, "role": "observed", "nullable": False})
    columns.append({"name": "bodyfat", "kind": "number", "unit": "%", "role": "generated", "nullable": False,
                    "minimum": 0, "maximum": 100})
    rows = []
    for i, (age, bmi, male) in enumerate(itertools.product([25., 40., 58.], [20., 25., 29., 33.], [0, 1])):
        rows.append([f"invented_grid_{i}", age, bmi, male, 0, 1/bmi, male/bmi, 0., male*age, 0.])
    frame = pd.DataFrame(rows, columns=[c["name"] for c in columns[:-1]])
    task = {"schema_version": 1, "task_id": f"m13a-real-source-bodyfat-{name}", "mode": "enrichment",
            "population": "INVENTED qualification grid, not patients: planned adult non-Asian transport support; no target outcomes present",
            "row_id": "id", "n_rows": len(frame), "columns": columns,
            "information_policy": {"mode": "published_evidence", "excluded_cohorts": ["NHANES"],
                                   "allowed_tools": ["screened_local_sources_only"]},
            "budget": {"source_queries": 0, "source_downloads": 0, "revisions": 3}}
    validate_input(frame, task)
    write(root / "task.json", task)
    frame.to_csv(root / "observed.csv", index=False)
    records = []
    for source_id in ("thai2005", "gallagher2000"):
        dest = root / "sources" / (source_id + ".json")
        shutil.copy2(P / "work/m13/packet/screened_sources" / (source_id + ".json"), dest)
        records.append({"source_id": source_id, "path": dest.relative_to(root).as_posix(),
                        "sha256": sha256(dest), "origin": "curator", "screening": "approved"})
    write(root / "registry.json", {"artifacts": records})
    controls = {
        "scope": "M13-A real published source replay only; invented qualification grid; not target validation",
        "base_covariates": ["age", "bmi", "male", "asian"],
        "derived_columns": {"inv_bmi": "1/bmi", "male_inv_bmi": "male/bmi", "asian_inv_bmi": "asian/bmi",
                            "male_age": "male*age", "asian_age": "asian*age"},
        "derived_column_role": "Deterministic design columns to match a published source estimator; not assigned biomedical effects",
        "population_coding": "male=1; source Asian indicator follows original study (Thai/Japanese transport is an assumption); target qualification grid asian=0. Later real primary domain non-Hispanic White/Black only.",
        "source_contexts": ["Thai development sample only", "Gallagher six sex-by-ethnicity groups"],
        "max_contexts": 2, "max_rows_per_context": 12000,
        "required_checks": {"thai2005": ["male and female bodyfat means", "male and female bodyfat SDs",
                                          "male and female Pearson BMI-bodyfat correlations", "adjusted BMI, age, male coefficients and intercept"],
                            "gallagher2000": ["all eight terms of reported DXA Equation 1 using original design matrix"]},
        "not_fitting_targets": ["Thai validation sample", "unreported subgroup quantiles", "unreported source covariance", "any target outcome"],
        "fit_seeds": [13101, 13102], "replay_seeds": [23101, 23102],
        "max_trials_per_session": 9, "max_sessions": 2, "max_scientific_revisions": 1,
        "loss_scales": {"mean": 2., "sd": 1., "correlation": .1,
                        "coefficient_by_term": {"intercept": 10., "bmi": .25, "age": .05, "male": 2.,
                                                "inv_bmi": 100., "male_inv_bmi": 50., "asian_inv_bmi": 50.,
                                                "male_age": .05, "asian_age": .05}},
        "loss_scale_role": "Fixed engineering unit scales, not source precision, likelihood or clinical equivalence; preserve per-constraint errors",
        "target_loss": 0., "target_loss_role": "Zero stops only at exact source agreement; nonzero loss is retained, not a clinical failure threshold",
        "execution": {"timeout_seconds": 30, "memory_mb": 1024, "output_bytes": 5000000, "log_bytes": 20000},
        "budget_limits": {"sessions": 2, "trials": 18, "executions": 80, "reserved_seconds": 2400},
        "scientific_loop": {"max_actions": 2, "max_promotions": 1},
        "global_campaign": "Exactly two separately instantiated builders; same information and numerical allowance, no ranking from target outcomes",
        "measurement_rule": "Untransformed DXA scale is an explicit cross-study transport assumption, not proven device equivalence. No invented BCA correction.",
    }
    write(root / "allowed_inputs/controller_contract.json", controls)
    write(root / "agent_exchange/initial_input_manifest.json", {
        "scope": controls["scope"], "files": {p.relative_to(root).as_posix(): sha256(p) for p in sorted(root.rglob("*")) if p.is_file()}})
    return root


if __name__ == "__main__":
    for name in ("build01", "build02"):
        print(prepare(name))
