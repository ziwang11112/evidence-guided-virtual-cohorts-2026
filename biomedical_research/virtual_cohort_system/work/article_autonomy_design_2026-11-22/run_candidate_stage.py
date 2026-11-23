"""Run the author's generator and estimator together, with no case-specific operators."""
import argparse
import ast
import hashlib
import json
import math
from pathlib import Path
import re

import numpy as np
import pandas as pd
from filelock import FileLock

from author_stage import DIAGNOSTIC_SEED, HERE, N, SEEDS
from runtime_stage import WORKER, execute, lifecycle


WRAPPER = """
def generate(observed, spec, seed):
    import numbers
    import numpy as np
    import pandas as pd
    scientific = dict(spec['candidate_spec'], n=spec['n'], scenario=spec['scenario'])
    frame = _cohort_original_generate(observed, scientific, seed)
    names = ['row_id'] + [column['name'] for column in scientific['columns']]
    if not isinstance(frame, pd.DataFrame) or list(frame.columns) != names:
        raise ValueError('generator did not return declared measurement columns in order')
    estimates = analyze(frame.copy(deep=True), scientific)
    if not isinstance(estimates, dict) or set(estimates) != {item['name'] for item in scientific['outputs']}:
        raise ValueError('analyze did not return the declared output keys')
    for item in scientific['outputs']:
        name = item['name']
        value = estimates[name]
        if isinstance(value, (bool, np.bool_)) or not isinstance(value, numbers.Real) or not np.isfinite(value):
            raise ValueError('analyze returned a nonfinite or nonnumeric scalar')
        frame['diagnostic_' + name] = float(value)
    return frame
"""


def digest(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True, allow_nan=False,
                                     separators=(",", ":")).encode("utf8")).hexdigest()


def record(path, obj):
    if path.exists():
        if lifecycle.read_json(path) != obj:
            raise RuntimeError("Existing stage binding or result differs")
        return
    temp = path.with_suffix(".json.tmp")
    temp.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf8")
    temp.replace(path)


def valid_name(value):
    return isinstance(value, str) and value.isidentifier() and not value.startswith("diagnostic_")


def prepare(candidate):
    spec = candidate["model_spec"]
    for key in ("columns", "outputs"):
        items = spec.get(key)
        if not isinstance(items, list) or not items:
            raise ValueError("Both columns and outputs require a nonempty declaration list")
        if any(not isinstance(item, dict) or not valid_name(item.get("name"))
               or not isinstance(item.get("unit"), str) for item in items):
            raise ValueError("Invalid measurement or output name or unit")
    names = [item["name"] for key in ("columns", "outputs") for item in spec[key]]
    if "row_id" in names or len(set(names)) != len(names):
        raise ValueError("Duplicate or reserved measurement or output name")
    alternatives = spec.get("alternatives")
    if not isinstance(alternatives, list) or len(alternatives) > 2 or any(
            not valid_name(v) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,63}", v)
            for v in alternatives):
        raise ValueError("Alternatives must be a list of up to two portable identifiers")
    scenarios = ["primary", *alternatives]
    if len(set(name.casefold() for name in scenarios)) != len(scenarios):
        raise ValueError("Duplicate scenario names")
    syntax = ast.parse(candidate["generator_py"])
    funcs = [node for node in syntax.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    for key in ("generate", "analyze"):
        if sum(node.name == key and isinstance(node, ast.FunctionDef) for node in funcs) != 1:
            raise ValueError("Both generate and analyze require one synchronous top-level function")
    if any(node.name == "_cohort_original_generate" for node in funcs):
        raise ValueError("Reserved worker function name")
    next(node for node in funcs if node.name == "generate").name = "_cohort_original_generate"
    code = ast.unparse(syntax) + "\n" + WRAPPER
    return spec, scenarios, code


def seed_run(path, run_spec, code, seed):
    path.mkdir(exist_ok=True)
    attempts = sorted(path.glob("attempt_*"))
    for attempt in attempts:
        result_path = attempt / "result.json"
        if result_path.is_file():
            result = lifecycle.read_json(result_path)
            completed = result["runs"][0] if result["runs"] else result
            if completed.get("table") and lifecycle.sha256(completed["table"]) != completed.get("sha256"):
                raise RuntimeError("Retained table hash differs")
            return completed
    return_result = execute(run_spec, code, path / f"attempt_{len(attempts) + 1:03}", (seed,), N)
    return return_result["runs"][0] if return_result["runs"] else return_result


def stage(root, mode):
    seeds = (DIAGNOSTIC_SEED,) if mode == "trial" else SEEDS
    candidate = lifecycle.read_json(root / "build.json")
    review = lifecycle.read_json(root / "review.json") if mode == "final" else {}
    action = review.get("action", "initial")
    if action == "revise":
        candidate = review["candidate"]
    stage_dir = root / ("execution_" + mode)
    stage_dir.mkdir(exist_ok=True)
    with FileLock(stage_dir / "stage.lock", timeout=15):
        binding = dict(candidate_sha256=digest(candidate), review_sha256=digest(review), n=N,
                       action=action, seeds=list(seeds), driver_sha256=lifecycle.sha256(__file__),
                       executor_sha256=lifecycle.sha256(HERE / "runtime_stage.py"),
                       worker_sha256=lifecycle.sha256(WORKER))
        record(stage_dir / "binding.json", binding)
        runs = []
        manifest = dict(**binding, status="abstained" if action == "abstain" else "success", runs=runs)
        if action != "abstain":
            try:
                spec, scenarios, code = prepare(candidate)
            except (ValueError, SyntaxError, KeyError, TypeError) as error:
                manifest.update(status="failed", public_error=(
                    str(error) if type(error) is ValueError else "Invalid submitted scientific interface"))
                scenarios = []
            for index, scenario in enumerate(scenarios):
                columns = list(spec["columns"]) + [dict(name="diagnostic_" + item["name"], unit=item["unit"])
                                                   for item in spec["outputs"]]
                run_spec = dict(candidate_spec=spec, columns=columns, scenario=scenario)
                if isinstance(spec.get("population"), str) and spec["population"].strip():
                    run_spec["population"] = spec["population"]
                for seed in seeds:
                    row = dict(scenario=scenario, seed=seed, status="failed")
                    receipt = seed_run(stage_dir / f"s{index}_{seed}", run_spec, code, seed)
                    if receipt["status"] == "success":
                        table = Path(receipt["table"])
                        frame = pd.read_csv(table, float_precision="round_trip")
                        outputs = {}
                        for item in spec["outputs"]:
                            name = item["name"]
                            values = frame["diagnostic_" + name]
                            if values.nunique(dropna=False) != 1 or not math.isfinite(float(values.iloc[0])):
                                raise RuntimeError("Invalid repeated diagnostic scalar")
                            outputs[name] = float(values.iloc[0])
                        measures = {}
                        for item in spec["columns"]:
                            values = frame[item["name"]].to_numpy()
                            measures[item["name"]] = dict(mean=float(np.mean(values)), sd=float(np.std(values)),
                                                          minimum=float(np.min(values)), maximum=float(np.max(values)))
                        row.update(status="success", table=str(table), sha256=receipt["sha256"],
                                   n=len(frame), outputs=outputs, measurements=measures)
                    else:
                        manifest["status"] = "failed"
                        row["public_error"] = "Candidate did not complete the isolated generation, analysis and output checks"
                        row["local_error"] = receipt.get("error")
                    runs.append(row)
        record(root / (mode + "_manifest.json"), manifest)
        if mode == "trial":
            public = {k: manifest[k] for k in ("status", "public_error") if k in manifest}
            public["runs"] = [{k: v for k, v in row.items() if k in
                              ("scenario", "seed", "status", "n", "outputs", "measurements", "public_error")}
                              for row in runs]
            record(root / "trial_public.json", public)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("trial", "final"))
    parser.add_argument("--run", required=True)
    args = parser.parse_args()
    if not args.run.isidentifier():
        raise ValueError("Use an opaque run identifier")
    answer = stage(HERE / "private" / args.run, args.stage)
    print(answer["status"], len(answer["runs"]), flush=True)
