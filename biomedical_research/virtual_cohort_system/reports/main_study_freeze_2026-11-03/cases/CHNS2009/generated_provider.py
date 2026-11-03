"""Generated-only provider using the unchanged F2 numerical implementation.

No reference report/participant decoder or information-revision R evaluator is
called. The fixed analysis plan is metadata; its old execution schedule is inert.
"""
from __future__ import annotations
import importlib.util
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[3]
sys.path.insert(0, str(PROJECT))
from cohort_harness import execution, lifecycle
from cohort_harness.contracts import require

PLAN = PROJECT / "work/chns_admission_2026-11-01/f2/analysis_plan.json"
ENGINE = PROJECT / "work/chns_admission_2026-11-01/f2/evaluation/chns_f2_evaluation.py"


def generated_statistics(frame):
    spec = importlib.util.spec_from_file_location("main_chns_f2_pure", ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    plan = lifecycle.read_json(PLAN)
    report = module.analyze(frame, plan, reference=False)
    analyses = []
    for item in plan["estimands"]:
        row = report["estimands"][item["id"]]
        analyses.append({"id": item["id"], "value": row["coefficient"], "unit": row["unit"],
                         "status": row["status"], "n": row["n"], "rank": row["rank"], "reason": row.get("reason")})
    diagnostics = []
    units = {"age": "year", "female": "1", "bmi": "kg/m^2", "glucose": "mmol/L", "hba1c": "%"}
    available = report["diagnostics"] is not None
    for variable in plan["diagnostics"]["marginal_variables"]:
        for statistic in ("mean", "sd", "q10", "median", "q90"):
            value = report["diagnostics"]["marginal"][variable][statistic] if available else None
            diagnostics.append({"id": f"{variable}_{statistic}", "value": value, "unit": units[variable],
                                "status": "computed" if value is not None else "unavailable", "n": len(frame),
                                "reason": report["gate_reason"]})
    for kind in ("pearson", "spearman"):
        value = report["diagnostics"]["joint"][kind] if available else None
        diagnostics.append({"id": f"glucose_hba1c_{kind}", "value": value, "unit": "1",
                            "status": "computed" if value is not None else "unavailable", "n": len(frame),
                            "reason": report["gate_reason"] if not available else (None if value is not None else "constant_pair")})
    return {"analyses": analyses, "diagnostics": diagnostics, "quality": report["quality"], "n": report["n"]}


def evaluate_generated(bundle, candidate, run_id, profile):
    config = lifecycle.read_json(profile)
    require(config.get("case_id") == "CHNS2009" and config.get("information_condition") in {"E0", "E1"}, "Wrong case or information condition")
    require(config.get("source_numeric_mode") == "reviewed_analytic_only", "Unsupported source mode")
    require(not any(k in config for k in ("reference", "reference_summary", "target_results")), "Reference forbidden")
    require(config.get("analysis_ids") == ["E1", "E2", "E3"], "Fixed analysis coverage required")
    root = lifecycle._bundle(bundle)
    _, relative = lifecycle._candidate(root, candidate)
    task = lifecycle.read_json(root / "task.json")
    require(task["mode"] == "whole_cohort" and task["n_rows"] == 3000, "Wrong task mode/size")
    receipt = execution.verify_execution(root, run_id)
    require(receipt["status"] == "success" and receipt["candidate"] == relative, "Wrong successful frozen execution")
    output = lifecycle._path(root, "executions/" + run_id + "/output/generated.csv")
    frame = lifecycle.read_table(output, task, output=True)
    return generated_statistics(frame)
