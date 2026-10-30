"""Run a received Agent submission through existing source-only adapters."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

import numpy as np
import pandas as pd
from cohort_harness import calibration, calibration_budget, scientific_loop
from cohort_harness.lifecycle import read_json, sha256, freeze_candidate, verify_candidate

P = Path(__file__).resolve().parents[2]


def write_new(path, value):
    if path.exists():
        raise ValueError(f"Refuse overwrite: {path}")
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def derived_check(frame):
    expected = {"inv_bmi": 1/frame.bmi, "male_inv_bmi": frame.male/frame.bmi,
                "asian_inv_bmi": frame.asian/frame.bmi, "male_age": frame.male*frame.age,
                "asian_age": frame.asian*frame.age}
    for key, values in expected.items():
        if not np.allclose(frame[key], values, rtol=1e-12, atol=1e-12):
            raise ValueError(f"Incorrect deterministic source design column: {key}")


def run(name, candidate_name, session_id):
    root = P / "work/m13" / name
    candidate = root / "candidates" / candidate_name
    controls = read_json(root / "allowed_inputs/controller_contract.json")
    original_inputs = read_json(root / "agent_exchange/initial_input_manifest.json")["files"]
    assert all(sha256(root/rel) == digest for rel, digest in original_inputs.items())
    before = read_json(P / "work/m13/engine_hashes_before.json")
    assert all(sha256(P/"cohort_harness"/rel) == digest for rel, digest in before.items())
    plan = read_json(candidate / "proposed_calibration_plan.json")
    recipe = read_json(candidate / "source_replay_v2.json")
    assert len(recipe["contexts"]) == 2
    assert plan["fit_seeds"] == controls["fit_seeds"] and plan["replay_seeds"] == controls["replay_seeds"]
    assert plan["optimizer"] == {"method": "bounded_coordinate_search", "max_trials": 9,
                                 "shrink": .5, "min_step_fraction": .01, "target_loss": 0.}
    assert plan["execution"] == controls["execution"]
    scales = controls["loss_scales"]
    evidence = read_json(candidate / "evidence.json")
    evidence_by_id = {e["id"]: e for e in evidence["items"]}
    required_counts = {"thai2005": 10, "gallagher2000": 8}
    counts = {k: 0 for k in required_counts}
    check_map = {}
    context_diagnostics = []
    for context in recipe["contexts"]:
        frame = pd.read_csv(candidate/context["input"]["path"])
        assert len(frame) <= controls["max_rows_per_context"]
        derived_check(frame)
        source_ids = {evidence_by_id[c["evidence_id"]]["source_id"] for c in context["checks"]}
        assert len(source_ids) == 1, "Do not merge distinct source contexts"
        source_id = next(iter(source_ids))
        counts[source_id] += len(context["checks"])
        for check in context["checks"]:
            op = check["operator"]
            check_map[(context["id"], check["id"])] = op
        context_diagnostics.append({"id": context["id"], "source_id": source_id, "n_simulated": len(frame),
                                    "checks": len(context["checks"]), "derived_columns_verified": True,
                                    "input_sha256": sha256(candidate/context["input"]["path"])})
    assert counts == required_counts
    for con in plan["constraints"]:
        op = check_map[(con["context_id"], con["check_id"])]
        expected = scales["coefficient_by_term"][op["term"]] if op["kind"] == "ols_coefficient" else scales[op["kind"]]
        assert con["scale"] == expected
    derived_check(pd.read_csv(root/"observed.csv"))
    receipt = {"actor": "/root/m13_"+name, "received_utc": datetime.now(timezone.utc).isoformat(),
               "scope": "unexecuted real-source candidate; no target participants",
               "files": {p.relative_to(candidate).as_posix(): sha256(p) for p in sorted(candidate.rglob("*")) if p.is_file()},
               "context_diagnostics": context_diagnostics, "approved_inputs_unchanged": True,
               "controller_and_engine_bindings_verified": True}
    write_new(root/"agent_exchange"/(session_id+"_construction_receipt.json"), receipt)
    if not (candidate/"freeze.json").exists():
        if candidate_name == "initial":
            freeze_candidate(root, candidate)
        else:
            revision=read_json(root/"agent_exchange"/(candidate_name+"_revision.json"))
            freeze_candidate(root,candidate,parent_receipt=verify_candidate(root,"candidates/initial"),revision=revision)
    calibration._validate(root, candidate, plan)
    if not (root/"calibration_budget").exists():
        calibration_budget.create_budget(root, controls["budget_limits"])
    if not (root/"scientific_loop").exists():
        scientific_loop.create_loop(root, controls["scientific_loop"])
    result = calibration.run_calibration(root, candidate, session_id, plan,
                    runtime=read_json(P/"work/m2-runtime-config.json"))
    chosen=result["selected_trial"]
    summary={"status":result["status"],"session":session_id,"selected_trial":chosen,
             "initial_loss":result["trials"][0]["fit"]["loss"],
             "selected_loss":None if chosen is None else result["trials"][chosen]["fit"]["loss"],
             "replay_loss":None if result["replay"] is None else result["replay"]["loss"],
             "usage":result["usage"],"scope":"source only; no target evaluation"}
    write_new(root/"agent_exchange"/(session_id+"_fit_summary.json"), summary)
    print(json.dumps(summary,indent=2),flush=True)


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("name",choices=["build01","build02"])
    parser.add_argument("--candidate",default="initial")
    parser.add_argument("--session",default="initial_fit")
    args=parser.parse_args()
    run(args.name,args.candidate,args.session)
