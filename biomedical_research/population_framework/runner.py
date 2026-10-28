"""Case-independent execution of Agent-authored population models.

The caller delivers requests to an Agent and returns its code and decision.
This module does not call a model API. Input staging and import checks support
review; they are not an adversarial security sandbox. No real target outcomes
are loaded by this runner.
"""
from __future__ import annotations

import argparse
import ast
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import traceback

import numpy as np
import pandas as pd

try:
    from .observers import validate_frame, derive, observe, compare_invariants
except ImportError:
    from observers import validate_frame, derive, observe, compare_invariants

HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, obj):
    path = Path(path)
    if path.exists():
        raise FileExistsError(f"Preserve existing artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def stage_enabled(obj, name):
    return name in obj.get("stages", [name])


def verify(run):
    lock = read(Path(run) / "manifest.json")
    for relative, expected in lock["files"].items():
        if sha(Path(run) / relative) != expected:
            raise ValueError(f"Committed run changed: {relative}")
    for relative, expected in lock["engine"].items():
        if sha(Path(run) / relative) != expected:
            raise ValueError(f"Committed engine snapshot changed: {relative}")
    return lock


def validate_case(case, stage_name):
    if case.get("schema_version") != 1 or stage_name not in case["stages"]:
        raise ValueError("Unsupported schema or unknown stage")
    evidence_ids = [item["id"] for item in case["stages"][stage_name]["evidence"]]
    if len(evidence_ids) != len(set(evidence_ids)):
        raise ValueError("Duplicate evidence IDs")
    for name, context in case["contexts"].items():
        if Path(name).name != name or not name.replace("_", "").isalnum():
            raise ValueError("Context names must be simple alphanumeric identifiers")
        if context["n"] < 3 or not context["seeds"] or len(set(context["seeds"])) != len(context["seeds"]):
            raise ValueError("Invalid context sampling budget")
    check_ids = []
    for check in case["checks"]:
        if not stage_enabled(check, stage_name):
            continue
        check_ids.append(check["id"])
        if check["context"] not in case["contexts"] or not stage_enabled(case["contexts"][check["context"]], stage_name):
            raise ValueError("Check refers to unavailable context")
        if check["role"] not in {"source_fidelity", "target_baseline"}:
            raise ValueError("Runner feedback supports supplied source/baseline quantities only")
        if not check["evidence_ids"] or not set(check["evidence_ids"]).issubset(evidence_ids):
            raise ValueError("Check evidence IDs are absent from delivered evidence")
        if not np.isfinite(check["expected"]) or not np.isfinite(check["tolerance_abs"]) or check["tolerance_abs"] < 0:
            raise ValueError("Nonfinite expected value or invalid numerical tolerance")
    if len(check_ids) != len(set(check_ids)):
        raise ValueError("Duplicate check IDs")


def changes(old, new, path=""):
    """Structural evidence diff; not a scientific interpretation of that diff."""
    if isinstance(old, dict) and isinstance(new, dict):
        out = []
        for key in sorted(set(old) | set(new)):
            pointer = path + "/" + str(key).replace("~", "~0").replace("/", "~1")
            if key not in old:
                out.append({"path": pointer, "kind": "added"})
            elif key not in new:
                out.append({"path": pointer, "kind": "removed"})
            else:
                out += changes(old[key], new[key], pointer)
        return out
    if old != new:
        return [{"path": path or "/", "kind": "changed"}]
    return []


def stage(case_path, stage_name, run, parent=None, request_template=None):
    case_path, run = Path(case_path).resolve(), Path(run).resolve()
    if run.exists():
        raise FileExistsError("Use a new run directory")
    case = read(case_path)
    validate_case(case, stage_name)
    packet = (case_path.parent / case["stages"][stage_name]["packet"]).resolve()
    evidence = read(packet)
    parent_info = None
    if parent is not None:
        parent = Path(parent).resolve()
        manifest = verify(parent)
        previous = read(parent / "case.json")
        if previous["case_id"] != case["case_id"]:
            raise ValueError("Parent must be from the same case")
        parent_info = {"path": str(parent), "manifest_sha256": sha(parent / "manifest.json"), "status": manifest["status"]}
    run.mkdir(parents=True)
    # Future evidence/check values must not leak through the full case manifest.
    # Use an allowlist, rather than copying free-form future annotations such
    # as unscoped descriptions/claim_limits that may contain later estimates.
    delivered_case = {
        "schema_version": case["schema_version"], "case_id": case["case_id"],
        "description": case["stages"][stage_name].get("description", "Active-stage evidence and execution contract"),
        "stages": {stage_name: case["stages"][stage_name]},
        "contexts": {k: v for k, v in case["contexts"].items() if stage_enabled(v, stage_name)},
        "checks": [v for v in case["checks"] if stage_enabled(v, stage_name)],
        "claim_limits": case["stages"][stage_name].get("claim_limits", []),
    }
    write(run / "case.json", delivered_case)
    write(run / "evidence.json", evidence)
    write(run / "task.json", {"stage": stage_name, "case_id": case["case_id"], "parent": parent_info,
          "case_origin": str(case_path), "case_origin_sha256": sha(case_path),
          "packet_origin": str(packet), "packet_origin_sha256": sha(packet),
          "created_utc": datetime.now(timezone.utc).isoformat(),
          "dispatch": "External Agent handoff; no model API called by runner"})
    if parent is not None:
        (run / "parent").mkdir()
        for name in ["generator.py", "decision.json", "feedback.json"]:
            shutil.copy2(parent / name, run / "parent" / name)
        write(run / "evidence_delta.json", {"changed_paths": changes(read(parent / "evidence.json"), evidence),
              "note": "Structural changes only; Agent must interpret population, operator and transport applicability."})
    template_path = Path(request_template).resolve() if request_template else HERE / "BUILDER_REQUEST.md"
    template = template_path.read_text(encoding="utf-8")
    (run / "request.md").write_text(template, encoding="utf-8")
    staged = [p for p in run.rglob("*") if p.is_file()]
    write(run / "staging_lock.json", {"files": {str(p.relative_to(run)): sha(p) for p in staged}})
    return {"status": "awaiting_agent_artifacts", "run": str(run), "shared_request_sha256": sha(run / "request.md")}


def load_generator(path):
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    allowed = {"numpy", "pandas", "scipy", "math", "json", "typing", "__future__", "copy", "dataclasses"}
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
        if isinstance(node, ast.Import):
            modules = [a.name.split(".")[0] for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            modules = [(node.module or "").split(".")[0]]
        else:
            continue
        if not set(modules).issubset(allowed):
            raise ValueError(f"Generator import requires review: {modules}")
    spec = importlib.util.spec_from_file_location("population_candidate_" + sha(path)[:12], path)
    module = importlib.util.module_from_spec(spec)
    # Import checks are a review aid, not proof of no I/O or malicious behavior.
    import sys
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if not callable(getattr(module, "generate", None)):
        raise ValueError("Missing generate(n, seed, evidence, context)")
    return module, names


def validate_decision(decision, case, task, names):
    allowed_actions = {"build", "revise", "no_op", "legacy_replay"}
    if decision.get("action") not in allowed_actions:
        raise ValueError("Unknown decision action")
    ids = {x["id"] for x in case["stages"][task["stage"]]["evidence"]}
    used = decision.get("evidence_use", [])
    if {x["id"] for x in used} != ids or len(used) != len(ids):
        raise ValueError("Decision must address every delivered evidence ID exactly once")
    for item in used:
        if item["action"] not in {"use", "qualify", "defer"} or not item.get("reason"):
            raise ValueError("Evidence action/reason missing")
    if not decision.get("model_family") or not isinstance(decision.get("assumptions"), list) or not decision.get("component_map"):
        raise ValueError("Model description, assumptions or component map missing")
    for component in decision["component_map"]:
        if not component.get("functions") or not set(component["functions"]).issubset(names):
            raise ValueError("Declared component function missing from submitted code")
        if not set(component.get("evidence_ids", [])).issubset(ids):
            raise ValueError("Component cites undelivered evidence")
    if task["parent"] and decision["action"] == "revise" and not decision.get("changes"):
        raise ValueError("Revision must identify changed components and reasons")
    for change in decision.get("changes", []):
        if not all(change.get(k) for k in ["component", "reason", "expected_effect"]):
            raise ValueError("Incomplete revision change record")
        if not set(change.get("evidence_ids", [])).issubset(ids):
            raise ValueError("Change cites undelivered evidence")


def set_numeric_delta(obj, pointer, delta):
    result = copy.deepcopy(obj)
    if not pointer.startswith("/"):
        raise ValueError("Evidence probe needs an RFC6901-style pointer")
    keys = [x.replace("~1", "/").replace("~0", "~") for x in pointer[1:].split("/")]
    cursor = result
    for key in keys[:-1]:
        cursor = cursor[int(key)] if isinstance(cursor, list) else cursor[key]
    key = int(keys[-1]) if isinstance(cursor, list) else keys[-1]
    value = cursor[key]
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not np.isfinite(delta):
        raise ValueError("Probe must alter one finite numerical evidence value")
    cursor[key] = value + delta
    if not np.isfinite(cursor[key]):
        raise ValueError("Probe produced nonfinite evidence")
    return result


def execute(run):
    run = Path(run).resolve()
    if (run / "manifest.json").exists() or (run / "report.json").exists():
        raise FileExistsError("Executed candidates are immutable; stage a new revision")
    for relative, expected in read(run / "staging_lock.json")["files"].items():
        if sha(run / relative) != expected:
            raise ValueError(f"Delivered inputs changed: {relative}")
    case, evidence, task = read(run / "case.json"), read(run / "evidence.json"), read(run / "task.json")
    parent = Path(task["parent"]["path"]) if task["parent"] else None
    if parent:
        verify(parent)
        if sha(parent / "manifest.json") != task["parent"]["manifest_sha256"]:
            raise ValueError("Parent commitment changed")
    report = {"case_id": case["case_id"], "stage": task["stage"], "status": "failed", "checks": [],
              "invariants": [], "influence_probes": [], "contexts": {}, "errors": [],
              "real_target_outcomes_read_by_runner": False,
              "interpretation": "Source/baseline reconstruction and software behavior, not target accuracy or clinical evidence"}
    frames = {}
    try:
        decision = read(run / "decision.json")
        module, names = load_generator(run / "generator.py")
        validate_decision(decision, case, task, names)
        for name, context in case["contexts"].items():
            if not stage_enabled(context, task["stage"]):
                continue
            n, seed = context["n"], context["seeds"][0]
            kwargs = dict(n=min(n, 251), seed=seed, evidence=copy.deepcopy(evidence), context=name)
            a = validate_frame(module.generate(**kwargs), kwargs["n"], context["schema"])
            kwargs["evidence"] = copy.deepcopy(evidence)
            b = validate_frame(module.generate(**kwargs), kwargs["n"], context["schema"])
            if not a.equals(b):
                raise ValueError(f"Seed is not reproducible for {name}")
            report["contexts"][name] = {"n_per_seed": n, "seeds": context["seeds"], "reproducible": True}
            for seed in context["seeds"]:
                frame = validate_frame(module.generate(n=n, seed=seed, evidence=copy.deepcopy(evidence), context=name), n, context["schema"])
                frame = derive(frame, context.get("derived", []))
                frames[(name, seed)] = frame
                folder = run / "samples"
                folder.mkdir(exist_ok=True)
                frame.to_csv(folder / f"{name}_{seed}.csv", index=False, float_format="%.17g")
                for check in case["checks"]:
                    if check["context"] != name or not stage_enabled(check, task["stage"]):
                        continue
                    observed = observe(frame, check["statistic"])
                    error = abs(observed - check["expected"])
                    report["checks"].append({**check, "seed": seed, "observed": observed,
                        "absolute_error": error, "passed": bool(error <= check["tolerance_abs"])})
        invariants = list(decision.get("invariants", []))
        if decision["action"] == "no_op":
            if parent is None:
                raise ValueError("A no-op must have a predecessor")
            previous_case = read(parent / "case.json")
            for name, context in case["contexts"].items():
                if name in previous_case["contexts"] and name in report["contexts"]:
                    previous_context = previous_case["contexts"][name]
                    if context["n"] != previous_context["n"] or context["seeds"] != previous_context["seeds"]:
                        raise ValueError("No-op verification requires matching predecessor sampling budgets")
                    old_sample = pd.read_csv(parent / "samples" / f"{name}_{context['seeds'][0]}.csv", nrows=0)
                    all_columns = sorted(set(old_sample.columns) | set(frames[(name, context["seeds"][0])].columns))
                    invariants.append({"context": name, "columns": all_columns,
                                       "origin": "automatic_all_shared_output_columns_for_no_op"})
        for item in invariants:
            if parent is None:
                raise ValueError("Invariant claim has no predecessor")
            name = item["context"]
            if name not in report["contexts"]:
                raise ValueError("Invariant refers to an unavailable context")
            for seed in case["contexts"][name]["seeds"]:
                path = parent / "samples" / f"{name}_{seed}.csv"
                current_path = run / "samples" / f"{name}_{seed}.csv"
                if not path.exists():
                    result = {"status": "not_testable", "reason": "No predecessor samples for this context/seed"}
                else:
                    # Compare equally round-tripped CSVs, not serialized vs in-memory floats.
                    result = compare_invariants(pd.read_csv(path, float_precision="round_trip"), pd.read_csv(current_path, float_precision="round_trip"), item["columns"])
                report["invariants"].append({**item, "seed": seed, **result})
        for probe in decision.get("influence_probes", []):
            name = probe["context"]
            context = case["contexts"][name]
            seed = context["seeds"][0]
            alternate = set_numeric_delta(evidence, probe["pointer"], probe["delta"])
            perturbed = validate_frame(module.generate(n=context["n"], seed=seed, evidence=alternate, context=name), context["n"], context["schema"])
            perturbed = derive(perturbed, context.get("derived", []))
            columns = probe["columns"]
            reference = frames[(name, seed)]
            equal = compare_invariants(reference, perturbed, columns)
            if equal["status"] == "not_testable":
                raise ValueError("Input-use probe outputs are not comparable")
            numeric_columns = [c for c in columns if pd.api.types.is_numeric_dtype(reference[c]) and pd.api.types.is_numeric_dtype(perturbed[c])]
            maximum = float(np.abs(perturbed[numeric_columns].to_numpy(float) - reference[numeric_columns].to_numpy(float)).max()) if numeric_columns else None
            expectation = probe.get("expect", "changes")
            if expectation not in {"changes", "unchanged"}:
                raise ValueError("Unknown influence expectation")
            changed = equal["status"] == "fail"
            passed = changed if expectation == "changes" else not changed
            report["influence_probes"].append({**probe, "max_abs_record_difference": maximum,
                "numeric_difference_scope": "Numeric columns only; categorical changes are checked by exact equality",
                "equal_rows": equal["equal_rows"], "passed": bool(passed),
                "interpretation": "Numerical input-use check only; not proof of correct transport or biological causality"})
        invariants_ok = all(x["status"] == "pass" for x in report["invariants"])
        checks_ok = all(x["passed"] for x in report["checks"])
        probes_ok = all(x["passed"] for x in report["influence_probes"])
        report["status"] = "checks_passed" if checks_ok and invariants_ok and probes_ok else "needs_revision"
        report["model_action"] = decision["action"]
        report["component_linkage"] = "Declared function names exist; numerical probes test only the supplied perturbations. Source reconstruction alone does not verify target linkage."
    except Exception as exc:
        report["errors"].append({"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()})
    write(run / "report.json", report)
    feedback = {"access_class": "source_and_permitted_baseline_only", "status": report["status"],
                "checks": report["checks"], "invariants": report["invariants"], "influence_probes": report["influence_probes"],
                "errors": report["errors"], "selection_rule": "No target accuracy score is available. All candidate versions are retained.",
                "next_actions": ["revise", "qualify evidence", "request missing information", "no_op", "stop"]}
    write(run / "feedback.json", feedback)
    engine_paths = []
    for name in ["runner.py", "observers.py", "BUILDER_REQUEST.md"]:
        saved = run / "engine" / name
        saved.parent.mkdir(exist_ok=True)
        shutil.copy2(HERE / name, saved)
        engine_paths.append(saved)
    paths = [p for p in run.rglob("*") if p.is_file() and p.suffix != ".pyc" and "__pycache__" not in p.parts]
    write(run / "manifest.json", {"status": report["status"], "files": {str(p.relative_to(run)): sha(p) for p in paths},
          "engine": {str(p.relative_to(run)): sha(p) for p in engine_paths},
          "backend": "External collaboration Agent, model/token metadata unavailable unless separately recorded",
          "standalone_llm_service": False, "created_utc": datetime.now(timezone.utc).isoformat()})
    return {"case_id": case["case_id"], "stage": task["stage"], "status": report["status"],
            "checks": len(report["checks"]), "failed_checks": [x["id"] for x in report["checks"] if not x["passed"]],
            "errors": [{"type": x["type"], "message": x["message"]} for x in report["errors"]]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    stage_parser = sub.add_parser("stage")
    stage_parser.add_argument("--case", required=True)
    stage_parser.add_argument("--stage", required=True)
    stage_parser.add_argument("--run", required=True)
    stage_parser.add_argument("--parent")
    stage_parser.add_argument("--request-template", help="Snapshot a versioned experimental policy instead of the default request")
    for command in ["execute", "verify"]:
        p = sub.add_parser(command)
        p.add_argument("--run", required=True)
    args = parser.parse_args()
    if args.command == "stage":
        result = stage(args.case, args.stage, args.run, args.parent, args.request_template)
    elif args.command == "execute":
        result = execute(args.run)
    else:
        result = {"status": "verified", "commitment": verify(Path(args.run))["status"]}
    print(json.dumps(result, ensure_ascii=False))
    if args.command == "execute" and result["status"] == "failed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
