"""C4's staged, source-only controller. Never imports or evaluates Agent code."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np

from cohort_harness import contracts, execution, lifecycle
from cohort_harness.contracts import ContractError, require, validate_output
from cohort_harness.lifecycle import _bundle, _path, read_json, read_table, sha256, verify_candidate

SEEDS = {"feedback": [24101, 24103, 24107], "election": [24203, 24209, 24223],
         "test": [24301, 24307, 24317]}


def _write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    require(len(str(path.absolute())) <= 250, "Windows path exceeds 250 characters")
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                    allow_nan=False).encode()).hexdigest()


def _name(value):
    require(isinstance(value, str) and value.isascii() and value.isidentifier()
            and len(value) <= 12, "Use an ASCII identifier of at most 12 characters")
    return value


def _engine():
    files = [Path(__file__), Path(contracts.__file__), Path(lifecycle.__file__),
             Path(execution.__file__), Path(execution.__file__).with_name("_worker.py")]
    return {p.name: sha256(p) for p in files}


def validate_source(source):
    require(source["schema_version"] == "c4-source-contract-v1", "Wrong source schema")
    require(source["mode"] == "whole_cohort" and source["n_rows"] == 4000
            and source["row_id"] == "row_id", "Wrong whole-cohort shape")
    require([c["name"] for c in source["columns"]] == ["row_id", "x", "y", "z"],
            "Wrong source columns")
    require(source["estimators"] == {"mean": "arithmetic", "sd_ddof": 1,
                                      "correlation": "Pearson"}, "Wrong estimators")
    require(source["tolerances"] == {"mean_absolute": .10, "sd_absolute": .10,
                                      "correlation_absolute": .05}, "Wrong engineering bands")
    checks = source["source_checks"]
    require(isinstance(checks, list) and len(checks) in {8, 9}, "Expected 8 or 9 fixed checks")
    require([c["id"] for c in checks] == source["source_check_order"], "Check ordering mismatch")
    require(len({c["id"] for c in checks}) == len(checks), "Duplicate check ID")
    expected = {}
    for name in ("x", "y", "z"):
        for kind in ("mean", "sd"):
            value = source["moments"][name][kind]
            require(type(value) in {int, float} and math.isfinite(value), "Nonfinite source moment")
            require(kind != "sd" or value > 0, "SD must be positive")
            expected[f"{kind}:{name}"] = (kind, [name], value, .10)
    for pair, value in source["correlations"].items():
        require(pair in {"x,y", "y,z", "x,z"} and type(value) in {int, float}
                and math.isfinite(value) and -1 <= value <= 1, "Invalid correlation")
        expected["correlation:" + pair] = ("correlation", pair.split(","), value, .05)
    require(set(expected) == {c["id"] for c in checks}, "Fixed check set mismatch")
    for check in checks:
        require(set(check) == {"id", "kind", "columns", "target", "tolerance"}, "Wrong check fields")
        require(type(check["target"]) in {int, float} and math.isfinite(check["target"]), "Nonfinite check target")
        require((check["kind"], check["columns"], check["target"], check["tolerance"])
                == expected[check["id"]], "Check disagrees with source or fixed band")
    protected = [c["check_id"] for c in source["protected_uses"]]
    require(len(protected) == len(set(protected)) and set(protected)
            == {c["id"] for c in checks if c["kind"] == "correlation"},
            "Every admitted correlation, and only those, must be protected")
    return source


def setup_bundle(root, case):
    """Create source/task/registry scaffolding, without authoring a candidate."""
    root, case = _bundle(root), _name(case)
    source_path = _path(root, f"visible/{case}/source_contract.json")
    source = validate_source(read_json(source_path))
    require(source.get("case_id", case) == case, "Source case provenance mismatch")
    bundle = _path(root, f"b/{case}", file=False)
    require(not bundle.exists(), "Bundle already exists")
    bundle.mkdir(parents=True)
    task = {k: source[k] for k in ("task_id", "mode", "population", "n_rows", "row_id", "columns")}
    task.update(schema_version=1, information_policy={"mode": "published_evidence",
                "excluded_cohorts": [], "allowed_tools": ["visible_source_contract"]},
                budget={"source_queries": 0, "source_downloads": 0, "revisions": 3})
    contracts.validate_task(task)
    _write(bundle / "task.json", task)
    (bundle / "sources").mkdir()
    (bundle / "sources/source_contract.json").write_bytes(source_path.read_bytes())
    _write(bundle / "registry.json", {"artifacts": [{"source_id": source["task_id"],
           "path": "sources/source_contract.json", "sha256": sha256(source_path),
           "origin": "fixture", "screening": "approved"}]})
    (bundle / "candidates").mkdir()
    return bundle


def _candidate_binding(root, case, name):
    bundle = _path(root, f"b/{_name(case)}", file=False)
    relative = "candidates/" + _name(name)
    frozen = verify_candidate(bundle, relative)
    require(frozen["route"] == "generator.py", "C4 requires isolated generator execution")
    return {"name": name, "freeze_sha256": sha256(bundle / relative / "freeze.json"),
            "generator_sha256": sha256(bundle / relative / "generator.py"),
            "spec_sha256": sha256(bundle / relative / "model_spec.json")}


def freeze_plan(root, initials, seeds=None):
    """Root freezes the two initial labels and source-only rules before feedback."""
    root = _bundle(root)
    require(isinstance(initials, dict) and len(initials) == 2, "Exactly two cases required")
    require((SEEDS if seeds is None else seeds) == SEEDS, "Seeds differ from preregistered C4 seeds")
    cases = {}
    for case, name in sorted(initials.items()):
        source_path = _path(root, f"visible/{_name(case)}/source_contract.json")
        source = validate_source(read_json(source_path))
        bundle = _path(root, f"b/{case}", file=False)
        require(sha256(bundle / "sources/source_contract.json") == sha256(source_path),
                "Bundle source differs from visible contract")
        require(read_json(bundle / "task.json")["task_id"] == source["task_id"], "Wrong case provenance")
        cases[case] = {"task_id": source["task_id"], "source_sha256": sha256(source_path),
                       "task_sha256": sha256(bundle / "task.json"),
                       "initial": _candidate_binding(root, case, name)}
    require(len({v["task_id"] for v in cases.values()}) == 2, "Case task identifiers must be distinct")
    plan = {"schema_version": 1, "cases": cases, "seeds": SEEDS, "engine": _engine(),
            "scientific_run_budget": 54, "deduplicate": False,
            "loss": "mean_squared_error_normalized_by_fixed_engineering_tolerance",
            "gate": "all_provided_correlations_all_election_seeds_and_strict_loss_improvement",
            "tie": "lowest_candidate_index", "uncertainty_interpretation": "none"}
    _write(root / "method/plan.json", plan)
    return plan


def _plan(root):
    plan = read_json(_path(root, "method/plan.json"))
    require(plan["engine"] == _engine() and plan["seeds"] == SEEDS, "Frozen method/seed changed")
    for case, item in plan["cases"].items():
        source_path = _path(root, f"visible/{case}/source_contract.json")
        require(sha256(source_path) == item["source_sha256"], "Source contract changed")
        require(sha256(_path(root, f"b/{case}/task.json")) == item["task_sha256"], "Task changed")
        require(_candidate_binding(root, case, item["initial"]["name"]) == item["initial"],
                "Initial candidate changed")
    return plan


def _pool(root, plan):
    pool = read_json(_path(root, "method/pool.json"))
    require(pool["plan_sha256"] == sha256(root / "method/plan.json"), "Pool plan mismatch")
    require(set(pool["cases"]) == set(plan["cases"]), "Pool case mismatch")
    for case, entries in pool["cases"].items():
        require(len(entries) == 4 and entries[0] == plan["cases"][case]["initial"], "Wrong pool baseline/count")
        require(len({e["name"] for e in entries}) == 4, "Pool labels must remain distinct")
        require(entries == [_candidate_binding(root, case, e["name"]) for e in entries], "Pool candidate changed")
    return pool


def diagnostics(frame, source):
    """Trusted finite statistics; tolerances are engineering bands, never SEs."""
    validate_source(source)
    values = frame[["x", "y", "z"]].to_numpy(dtype=float)
    require(np.isfinite(values).all(), "Nonfinite generated values")
    items = []
    for check in source["source_checks"]:
        cols = check["columns"]
        a = frame[cols[0]].to_numpy(dtype=float)
        if check["kind"] == "mean":
            estimate = float(np.mean(a))
        elif check["kind"] == "sd":
            estimate = float(np.std(a, ddof=1))
        else:
            b = frame[cols[1]].to_numpy(dtype=float)
            require(np.std(a, ddof=1) > 0 and np.std(b, ddof=1) > 0, "Undefined correlation")
            estimate = float(np.corrcoef(a, b)[0, 1])
        require(math.isfinite(estimate), "Nonfinite statistic")
        error = (estimate - check["target"]) / check["tolerance"]
        require(math.isfinite(error * error), "Nonfinite normalized error")
        items.append({"id": check["id"], "estimate": estimate, "normalized_error": error,
                      "squared_error": error * error,
                      "within_band": abs(estimate - check["target"]) <= check["tolerance"]})
    return {"status": "success", "checks": items, "full_source_error": float(np.mean([x["squared_error"] for x in items])),
            "protected_pass": all(x["within_band"] for x in items if x["id"].startswith("correlation:")),
            "numeric_pass": all(x["within_band"] for x in items),
            "fixed_denominator": len(items)}


def _entries(root, plan, phase):
    require(phase in SEEDS, "Unknown phase")
    return ({c: [v["initial"]] for c, v in plan["cases"].items()} if phase == "feedback"
            else _pool(root, plan)["cases"])


def _slot(phase, case, index, seed):
    return f"{phase[0]}_{case}_{index}_{seed}"


def _stat(root, plan, phase, case, index, seed, entry):
    require(phase in SEEDS and seed in SEEDS[phase], "Wrong phase or seed")
    bundle, run_id = root / "b" / case, _slot(phase, case, index, seed)
    receipt = execution.verify_execution(bundle, run_id)
    require(receipt["candidate"] == "candidates/" + entry["name"]
            and receipt["candidate_freeze_sha256"] == entry["freeze_sha256"]
            and receipt["limits"]["seed"] == seed, "Execution candidate/seed binding mismatch")
    table = bundle / "executions" / run_id / "output/generated.csv"
    source = read_json(root / "visible" / case / "source_contract.json")
    task = read_json(bundle / "task.json")
    require(task["task_id"] == source["task_id"] == plan["cases"][case]["task_id"], "Case provenance mismatch")
    result = {"status": "failed", "checks": [], "full_source_error": None, "protected_pass": False,
              "numeric_pass": False, "fixed_denominator": len(source["source_checks"]),
              "failure": receipt.get("error"), "infinite_loss": True}
    if receipt["status"] == "success":
        frame = read_table(table, task, output=True)
        validate_output(None, frame, task)
        try:
            result = diagnostics(frame, source)
        except (ContractError, FloatingPointError) as error:
            result["failure"] = {"type": type(error).__name__, "message": str(error)}
    return {"schema_version": 1, "phase": phase, "case": case, "candidate_index": index,
            "seed": seed, "candidate": entry, "plan_sha256": sha256(root / "method/plan.json"),
            "source_sha256": plan["cases"][case]["source_sha256"],
            "table_sha256": sha256(table) if table.is_file() else None,
            "execution_sha256": sha256(table.parent.parent / "execution.json"),
            "run_id": run_id, **result}


def read_phase(root, phase):
    root, rows = _bundle(root), []
    plan = _plan(root)
    for case, entries in _entries(root, plan, phase).items():
        for index, entry in enumerate(entries):
            for seed in SEEDS[phase]:
                path = _path(root, "stats/" + _slot(phase, case, index, seed) + ".json")
                row = _stat(root, plan, phase, case, index, seed, entry)
                require(read_json(path) == row, "Diagnostic binding/tamper mismatch")
                rows.append(row)
    return rows


def freeze_pool(root, labels):
    root = _bundle(root)
    plan = _plan(root)
    feedback = read_phase(root, "feedback")
    require(set(labels) == set(plan["cases"]), "Pool case mismatch")
    cases = {}
    for case, names in labels.items():
        require(len(names) == len(set(names)) == 4 and names[0] == plan["cases"][case]["initial"]["name"],
                "Four distinct labels with initial first are required")
        cases[case] = [_candidate_binding(root, case, n) for n in names]
        for name in names[1:]:
            frozen = verify_candidate(root / "b" / case, "candidates/" + name)
            while frozen["parent"] is not None:
                frozen = verify_candidate(root / "b" / case, frozen["parent"]["candidate"])
            require(frozen["candidate"] == "candidates/" + names[0], "Revision lacks initial provenance")
    pool = {"plan_sha256": sha256(root / "method/plan.json"), "cases": cases,
            "feedback_sha256": _digest(feedback), "labeled_candidates": 8,
            "distinct_generator_spec_pairs": len({(e["generator_sha256"], e["spec_sha256"])
                                                    for es in cases.values() for e in es})}
    _write(root / "method/pool.json", pool)
    return pool


def choose(rows):
    """All selectors use one complete election matrix and fixed source diagnostics."""
    require(len(rows) == 12 and all(r["phase"] == "election" for r in rows), "Incomplete/wrong election phase")
    require(len({r["case"] for r in rows}) == 1, "Mixed case provenance")
    require({(r["candidate_index"], r["seed"]) for r in rows}
            == {(i, s) for i in range(4) for s in SEEDS["election"]}, "Wrong election seeds/slots")
    require(all(type(r["protected_pass"]) is bool and type(r["numeric_pass"]) is bool
                and r["status"] in {"success", "failed"} for r in rows), "Malformed election diagnostics")
    def valid(r):
        value = r["full_source_error"]
        return r["status"] == "success" and type(value) in {int, float} and math.isfinite(value) and value >= 0
    groups = [[r for r in rows if r["candidate_index"] == i] for i in range(4)]
    complete = [all(valid(r) for r in group) for group in groups]
    losses = [float(np.mean([r["full_source_error"] for r in group])) if ok else math.inf
              for group, ok in zip(groups, complete)]
    complete = [ok and math.isfinite(loss) for ok, loss in zip(complete, losses)]
    losses = [loss if ok else math.inf for ok, loss in zip(complete, losses)]
    eligible = [ok and all(r["protected_pass"] for r in group) for ok, group in zip(complete, groups)]
    numeric = [ok and all(r["numeric_pass"] for r in group) for ok, group in zip(complete, groups)]
    minimum = min(range(4), key=lambda i: (losses[i], i))
    improving = [i for i in range(1, 4) if eligible[i] and losses[i] < losses[0]]
    gated = min(improving, key=lambda i: (losses[i], i)) if improving else 0
    return {"retain_initial": 0, "minloss": minimum, "protected_gate": gated,
            "protected_gate_qualified": eligible[gated], "mean_losses": [x if math.isfinite(x) else None for x in losses],
            "protected_eligible": eligible, "numeric_eligible": numeric, "candidate_complete": complete,
            "failed_draws": [{"candidate_index": r["candidate_index"], "seed": r["seed"]} for r in rows if not valid(r)],
            "all_invalid": not any(complete), "null_loss_means": "positive_infinity",
            "strict_improvement_required": True}


def _selection(root):
    rows = read_phase(root, "election")
    plan = _plan(root)
    return {"plan_sha256": sha256(root / "method/plan.json"), "pool_sha256": sha256(root / "method/pool.json"),
            "election_sha256": _digest(rows), "cases": {c: choose([r for r in rows if r["case"] == c])
                                                         for c in plan["cases"]}}


def seal_selections(root):
    root = _bundle(root)
    require(not any((root / "stats").glob("t_*.json")), "Test results already exist")
    require(not any((root / "b").glob("*/executions/t_*")), "Test execution already attempted")
    result = _selection(root)
    _write(root / "method/selection.json", result)
    return result


def _release(root, phase, path):
    plan = _plan(root)
    expected = {"approved_by": "root", "decision": "authorized", "phase": phase,
                "plan_sha256": sha256(root / "method/plan.json")}
    _entries(root, plan, phase)
    if phase != "feedback":
        require(_pool(root, plan)["feedback_sha256"] == _digest(read_phase(root, "feedback")),
                "Pool feedback commitment changed")
        expected["pool_sha256"] = sha256(root / "method/pool.json")
    if phase == "test":
        require(read_json(_path(root, "method/selection.json")) == _selection(root), "Sealed selection mismatch")
        expected["selection_sha256"] = sha256(root / "method/selection.json")
    require(read_json(path) == expected, "Root release absent, wrong phase, or stale bindings")
    return plan


def run_phase(root, phase, release_path):
    """Explicit root release required. No retries, deduplication, or host fallback."""
    root = _bundle(root)
    plan = _release(root, phase, release_path)
    entries = _entries(root, plan, phase)
    bindings = {Path(release_path): sha256(release_path), root / "method/plan.json": sha256(root / "method/plan.json")}
    for name in (["pool"] if phase == "election" else ["pool", "selection"] if phase == "test" else []):
        path = root / "method" / (name + ".json")
        bindings[path] = sha256(path)
    slots = [(c, i, s, e) for c, es in entries.items() for i, e in enumerate(es) for s in SEEDS[phase]]
    for case, index, seed, entry in slots:
        run_id = _slot(phase, case, index, seed)
        require(not (root / "b" / case / "executions" / run_id).exists()
                and not (root / "stats" / (run_id + ".json")).exists(), "Existing run ID; automatic retry forbidden")
    for case, index, seed, entry in slots:
        require(all(sha256(p) == digest for p, digest in bindings.items()) and plan["engine"] == _engine(),
                "Root release or sealed inputs changed during phase")
        run_id = _slot(phase, case, index, seed)
        execution.run_candidate(root / "b" / case, "candidates/" + entry["name"], run_id, seed)
        _write(root / "stats" / (run_id + ".json"), _stat(root, plan, phase, case, index, seed, entry))
    return read_phase(root, phase)
