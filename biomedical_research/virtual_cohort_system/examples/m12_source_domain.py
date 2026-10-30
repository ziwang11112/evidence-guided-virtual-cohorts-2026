"""M12-A invented arithmetic fixture; no patients, new evidence or Agent quality claim."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import pandas as pd

from cohort_harness import source_replay, source_replay_v2
from cohort_harness.contracts import ContractError, validate_input
from cohort_harness.demo import make_demo
from cohort_harness.lifecycle import freeze_candidate, read_json, sha256, verify_candidate

PROGRAM = """def generate(observed, spec, seed):
    out = observed.copy()
    p = spec['parameters']
    out['y'] = p['intercept'] + p['slope'] * out['x']
    return out
"""


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def build_fixture(destination, *, edit=None):
    root = make_demo(destination)
    candidate = root / "candidates/initial"
    (candidate / "generated.csv").unlink()  # Known file in this newly created fixture only.
    (candidate / "generator.py").write_text(PROGRAM, encoding="utf-8")
    task = read_json(root / "task.json")
    task["columns"][1].update(minimum=0, maximum=6)
    task["columns"][2].update(minimum=0, maximum=13)
    write(root / "task.json", task)
    source_frame = pd.DataFrame({"sample_id": ["source_0", "source_1", "source_2", "source_3"],
                                 "x": [7, 8, 9, 10]})
    source = candidate / "source_covariates.csv"
    source_frame.to_csv(source, index=False)
    fixture_values = pd.DataFrame({"x": [7, 8, 9, 10], "y": [15, 17, 19, 21]})
    fixture_values.to_csv(candidate / "source_tables/invented.csv", index=False)
    paper = root / "sources/invented_summary.txt"
    paper.write_text("ARTIFICIAL FIXTURE, NOT A PAPER. Source x=7,8,9,10; y=1+2x. Mean(y)=18; OLS slope=2.\n",
                     encoding="utf-8")
    registry = read_json(root / "registry.json")
    registry["artifacts"][0]["sha256"] = sha256(paper)
    write(root / "registry.json", registry)
    evidence = read_json(candidate / "evidence.json")
    evidence["sources"][0]["population"] = "Four invented source rows x=7,8,9,10"
    evidence["sources"][0]["artifacts"][0]["sha256"] = sha256(paper)
    evidence["items"][0]["estimate"] = 18
    for item in evidence["items"]:
        item["selection"] = "Four invented source rows; not the seven-row target fixture"
    write(candidate / "evidence.json", evidence)
    spec = read_json(candidate / "model_spec.json")
    spec["parameter_provenance"]["intercept"]["derivation"] = "18 - 2*mean(7,8,9,10)=1; invented fixture"
    write(candidate / "model_spec.json", spec)
    checks = read_json(candidate / "source_checks.json")
    table_hash = sha256(candidate / "source_tables/invented.csv")
    for check in checks["checks"]:
        check["table"]["sha256"] = table_hash
    write(candidate / "source_checks.json", checks)
    record = read_json(candidate / "checks.json")
    record["artifacts"][0]["sha256"] = table_hash
    record["records"][0]["detail"] = "Four explicit source rows support arithmetic fixture checks only."
    write(candidate / "checks.json", record)
    source_columns = copy.deepcopy(task["columns"])
    source_columns[1].update(minimum=0, maximum=10)
    source_columns[2].update(minimum=0, maximum=30)
    domain = copy.deepcopy(task["columns"])
    domain[1].update(minimum=0, maximum=12)
    domain[2].update(minimum=0, maximum=40)
    context = {"id": "wider_source", "population": "Four invented source rows outside target eligibility",
        "reason": "Verify independent source support without changing target or generator",
        "assumption_ids": ["A1"],
        "measurement": {"mode": "identity", "description": "Identical invented variable units"},
        "input": {"path": source.name, "sha256": sha256(source), "origin": "declared_source_covariates"},
        "checks": [{**{k: v for k, v in c.items() if k != "table"}, "status": "approximate"}
                   for c in checks["checks"]], "columns": source_columns}
    plan = {"schema_version": 2, "model_domain": {"description": "Declared invented computational support",
        "columns": domain, "assumption_ids": ["A1"]}, "contexts": [context]}
    if edit:
        edit(plan, source, task)
    write(candidate / "source_replay_v2.json", plan)
    write(candidate / "source_replay.json", {"schema_version": 1,
        "contexts": [{k: v for k, v in context.items() if k != "columns"}]})
    freeze_candidate(root, candidate)
    return root, candidate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--runtime", required=True)
    args = parser.parse_args()
    root, candidate = build_fixture(args.destination)
    before = {str(p.relative_to(root)): sha256(p) for p in
              [root / "task.json", candidate / "freeze.json", candidate / "generator.py", candidate / "model_spec.json"]}
    try:
        source_replay.run_source_replay(root, candidate, "legacy_reject", 12001,
                                        runtime=read_json(args.runtime))
    except ContractError as error:
        legacy_result = str(error)
    else:
        raise AssertionError("Legacy replay unexpectedly accepted out-of-target source rows")
    report = source_replay_v2.run_source_replay(root, candidate, "independent_source", 12001,
                                               runtime=read_json(args.runtime))
    assert report["status"] == "success"
    checks = report["contexts"][0]["checks"]
    assert abs(checks[0]["value"] - 18) < 1e-12 and abs(checks[1]["value"] - 2) < 1e-12
    assert before == {name: sha256(root / name) for name in before}
    verify_candidate(root, candidate)
    target = read_json(root / "task.json")
    target["n_rows"] = 4  # Only a local row-count adjustment to test the same original eligibility.
    try:
        validate_input(pd.read_csv(candidate / "source_covariates.csv"), target)
    except ContractError as error:
        target_rejection = str(error)
    else:
        raise AssertionError("Target eligibility was incorrectly widened")
    summary = {"scope": "invented arithmetic and real isolated execution only", "status": "passed",
        "legacy_source_rejection": legacy_result, "target_rejection_preserved": target_rejection,
        "source_mean": checks[0]["value"], "source_slope": checks[1]["value"],
        "same_generator_and_spec": True, "parent_bytes_unchanged": True,
        "report": str(root / "source_replays_v2/independent_source/replay.json"),
        "biomedical_utility_tested": False}
    write(root / "m12_demo_result.json", summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
