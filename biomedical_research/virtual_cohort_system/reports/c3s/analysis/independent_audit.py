"""Independent aggregate-only C3 audit; no production imports or simulation."""
from __future__ import annotations
import argparse, copy, hashlib, json, math, platform, re, sys, time
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[1]
STRUCTURES = ("linear", "alternative")
SEEDS = (19101, 19111, 19123)
CONTEXTS = ("lifelines", "pani")
COVARIATES = ["row_id", "age", "female", "bmi", "glucose"]
INPUTS, QA = {}, []
RTOL, ATOL = 1e-10, 1e-12

def sha(path):
    path = Path(path).resolve(strict=True)
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""): h.update(block)
    value = h.hexdigest()
    INPUTS[str(path)] = {"sha256": value, "bytes": path.stat().st_size}
    return value

def read(path):
    sha(path)
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()

def write(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n", encoding="utf-8")

def check(name, passed, detail="", fatal=False):
    QA.append({"check": name, "passed": bool(passed), "detail": str(detail)})
    if fatal and not passed: raise ValueError(name + ": " + str(detail))
    return bool(passed)

def near(a, b):
    return a is not None and b is not None and math.isfinite(float(a)) and math.isfinite(float(b)) and math.isclose(
        float(a), float(b), rel_tol=RTOL, abs_tol=ATOL)

def hashes(base, inventory, label, exact=False, exclude=()):
    base = Path(base).resolve()
    if exact:
        actual = {p.relative_to(base).as_posix() for p in base.rglob("*") if p.is_file()}
        check(label + ":inventory", actual - set(exclude) == set(inventory), fatal=True)
    for relative, expected in inventory.items():
        path = (base / relative).resolve()
        check(label + ":path", path.is_relative_to(base), fatal=True)
        check(label + ":" + relative, sha(path) == expected, fatal=True)

def freeze(bundle, name):
    obj = read(bundle / name / "freeze.json")
    check(str(bundle) + ":freeze_kind", obj["kind"] == "candidate_freeze", fatal=True)
    hashes(bundle, obj["commitments"], str(bundle) + ":commitments")
    return obj

def thresholds(criteria):
    req = criteria["scientific_requirements"]
    source = next(x for x in req if x.startswith("Source compatibility:"))
    slopes = next(x for x in req if x.startswith("Projected associations:"))
    marginals = next(x for x in req if x.startswith("Unrelated marginal no-harm:"))
    def values(pattern, text):
        match = re.search(pattern, text)
        if not match: raise ValueError("Unrecognized frozen criterion: " + pattern)
        return tuple(float(v) for v in match.groups())
    result = {
        "J_T1_hba1c_mean_pct": ("difference", *values(r"mean discrepancy<=([0-9.]+)", source)),
        "J_T1_hba1c_sd_pct": ("difference", *values(r"SD discrepancy<=([0-9.]+)", source)),
        "pani_means": ("difference", *values(r"age-stratum mean discrepancy<=([0-9.]+)", source)),
        "P_NHANES_age_slope": ("value", *values(r"Pani age OLS coefficient in\[([0-9.]+),([0-9.]+)\]", slopes)),
        "J_T2_bmi_slope_task_derived": ("value", *values(r"BMI projection in\[([0-9.]+),([0-9.]+)\]", slopes)),
        "J_T2_glucose_slope_task_derived": ("value", *values(r"glucose projection in\[([0-9.]+),([0-9.]+)\]", slopes)),
        "J_T1_female_proportion_derived": ("difference", *values(r"female fraction>([0-9.]+)", marginals)),
    }
    for part, pattern in [("age", r"age mean/SD discrepancies>([0-9.]+)year"),
                          ("bmi", r"BMI mean/SD>([0-9.]+)kg"),
                          ("glucose", r"glucose mean/SD>([0-9.]+)mg")]:
        limit, = values(pattern, marginals)
        for kind in ("mean", "sd"):
            suffix = "mg_dL_derived" if part == "glucose" else "task"
            result[f"J_T1_{part}_{kind}_{suffix}"] = ("difference", limit)
    return result

def select(frame, rules):
    mask = np.ones(len(frame), dtype=bool)
    for rule in rules:
        v, bound, op = frame[rule["column"]].to_numpy(), rule["value"], rule["op"]
        if pd.isna(v).any(): raise ValueError("Missing selection values under error policy")
        if op == "eq": keep = v == bound
        elif op == "ne": keep = v != bound
        elif op == "lt": keep = v < bound
        elif op == "le": keep = v <= bound
        elif op == "gt": keep = v > bound
        elif op == "ge": keep = v >= bound
        else: raise ValueError("Unknown selection operator")
        mask &= keep
    return frame.loc[mask]

def statistic(frame, op):
    """Independent raw-unit formulas, exact selection, strict missing policy."""
    if op["missing_policy"] != "error": raise ValueError("Unexpected missing policy")
    df = select(frame, op["selection"])
    n, kind = len(df), op["kind"]
    if not n: raise ValueError("Empty source selection")
    if kind in ("mean", "sd"):
        v = df[op["column"]].to_numpy(dtype=float)
        if not np.isfinite(v).all(): raise ValueError("Nonfinite summary")
        if kind == "sd" and n < 2: raise ValueError("SD needs two rows")
        value = np.mean(v) if kind == "mean" else np.std(v, ddof=1)
    elif kind == "proportion":
        v = df[op["event"]["column"]].to_numpy(dtype=float)
        if not np.isfinite(v).all(): raise ValueError("Nonfinite event")
        value = len(select(df, [op["event"]])) / n
    elif kind == "ols_coefficient":
        names = list(op["predictors"])
        x, y = df[names].to_numpy(dtype=float), df[op["outcome"]].to_numpy(dtype=float)
        if op["include_intercept"]:
            x = np.column_stack((np.ones(n), x))
            names = ["intercept"] + names
        if not np.isfinite(x).all() or not np.isfinite(y).all(): raise ValueError("Nonfinite OLS")
        if n <= x.shape[1] or np.linalg.matrix_rank(x) < x.shape[1]: raise ValueError("Rank deficient OLS")
        value = np.linalg.lstsq(x, y, rcond=None)[0][names.index(op["term"])]
    else: raise ValueError("Unknown statistic")
    if not math.isfinite(float(value)): raise ValueError("Nonfinite value")
    return float(value), n

def envelope(path):
    obj = read(path)
    check(str(path) + ":envelope", digest(obj["payload"]) == obj["sha256"], fatal=True)
    return obj["payload"], obj["sha256"]

def budget(bundle, result, intent):
    base = bundle / "calibration_budget"
    config, h = envelope(base / "config.json")
    head, _ = envelope(base / "head.json")
    paths = sorted((base / "events").glob("*.json"))
    check(str(base) + ":events", len(paths) == head["event_count"] == 2, fatal=True)
    original, reservation = h, None
    for i, path in enumerate(paths, 1):
        event, current = envelope(path)
        check(str(path) + ":chain", event["previous_sha256"] == h and event["config_sha256"] == original
              and event["sequence"] == i and event["session_id"] == "s", fatal=True)
        if i == 1:
            reservation = current
            check(str(path) + ":reserve", event["kind"] == "reserve" and event["binding"] == result["binding"]
                  and event["reservation"] == intent["reservation"], fatal=True)
        else:
            check(str(path) + ":completed", event["kind"] == "finish" and event["status"] == "completed"
                  and event["reservation_sha256"] == reservation and event["usage"] == result["usage"], fatal=True)
        h = current
    check(str(base) + ":head", head["config_sha256"] == original and head["last_event_sha256"] == h, fatal=True)
    check(str(base) + ":limits", config["limits"] == intent["reservation"] and config["refunds"] is False, fatal=True)
    return config["limits"]

def aggregate_loss(score, plan, criteria, label):
    scales = {(x["context_id"], x["check_id"]): x["scale"] for x in plan["constraints"]}
    weights = {(x["context_id"], x["check_id"]): x["weight"] for x in criteria["check_weights"]}
    rows, total, terms = score["constraints"], math.fsum(weights.values()), []
    keys = [(x["context_id"], x["check_id"]) for x in rows]
    check(label + ":all20", len(keys) == len(set(keys)) == 20 and set(keys) == set(scales), fatal=True)
    for x in rows:
        k = x["context_id"], x["check_id"]
        check(label + ":constants:" + k[1], x["scale"] == scales[k] and x["weight"] == weights[k])
        if x["status"] != "computed" or x["value"] is None: continue
        err = (x["value"] - x["reported_value"]) / scales[k]
        term = weights[k] * err * err / total
        check(label + ":arithmetic:" + k[1], near(err, x["scaled_error"]) and near(term, x["weighted_square"]))
        if math.isfinite(term): terms.append(term)
    loss = math.fsum(terms) if len(terms) == 20 else None
    check(label + ":loss", score["feasible"] == (loss is not None) and
          ((loss is None and score["loss"] is None) or near(loss, score["loss"])))
    return loss

def contract(df, context):
    result = {"rows6000": len(df) == 6000, "columns": df.columns.tolist() == [x["name"] for x in context["columns"]],
              "unique_ids": df.row_id.is_unique, "no_missing": not df.isna().any().any()}
    for col in context["columns"]:
        if col["name"] == "row_id": continue
        v = df[col["name"]].to_numpy(dtype=float)
        valid = np.isfinite(v).all()
        if col["kind"] == "integer": valid = valid and np.equal(v, np.floor(v)).all()
        if "minimum" in col: valid = valid and (v >= col["minimum"]).all()
        if "maximum" in col: valid = valid and (v <= col["maximum"]).all()
        result[col["name"]] = bool(valid)
    return result

def session_audit(s, releases):
    b, session = ROOT / s, ROOT / s / "source_calibration/s"
    check(s + ":no_failure", not (session / "failure.json").exists(), fatal=True)
    result = read(session / "result.json")
    check(s + ":complete", result["status"] in {"fit_complete_requires_scientific_review", "no_feasible_trial"}, fatal=True)
    intent, plan, criteria, release = [read(session / (n + ".json")) for n in ("intent", "plan", "criteria", "release")]
    initial = b / "candidates/initial"
    parent, panel, evidence = read(initial / "model_spec.json"), read(b / "SOURCE_PANEL_SPEC.json"), read(initial / "evidence.json")
    frozen = freeze(b, "candidates/initial")
    check(s + ":frozen_plan_criteria", plan == read(initial / "calibration_plan.json")
          and criteria == read(initial / "scientific_criteria.json"), fatal=True)
    check(s + ":root_release", release == read(ROOT / releases["structures"][s]["release"])
          and release["decision"] == "release" and release["session_id"] == "s", fatal=True)
    binding = release["binding"]
    check(s + ":session_binding", result["binding"] == intent["binding"] == {**binding, "release_sha256": digest(release)}, fatal=True)
    check(s + ":input_binding", binding["parent_freeze_sha256"] == sha(initial / "freeze.json")
          and binding["task_sha256"] == sha(b / "task.json") and binding["plan_sha256"] == digest(plan)
          and binding["criteria_sha256"] == digest(criteria), fatal=True)
    check(s + ":engine_runtime_binding", digest(intent["engines"]) == binding["engines_sha256"]
          and digest(intent["runtime"]) == binding["runtime_sha256"] and intent["engines"] == result["engines"], fatal=True)
    paths = {"adapter": ROOT / "method/run_source_calibration.py", "calibration": PROJECT / "cohort_harness/calibration.py",
             "calibration_budget": PROJECT / "cohort_harness/calibration_budget.py",
             "run_source_contexts.py": PROJECT / "work/autonomous_research_cycle2_2026-10-31/method/run_source_contexts.py"}
    for name, h in intent["engines"].items():
        check(s + ":engine:" + name, sha(paths.get(name, PROJECT / "cohort_harness" / name)) == h, fatal=True)
    hashes(session, result["files"], s + ":session", exact=True, exclude=("result.json",))
    limits = budget(b, result, intent)
    rules = thresholds(criteria)
    checks = {(c["id"], x["id"]): x for c in panel["contexts"] for x in c["checks"]}
    scales = {(x["context_id"], x["check_id"]): x["scale"] for x in plan["constraints"]}
    weights = {(x["context_id"], x["check_id"]): x["weight"] for x in criteria["check_weights"]}
    check(s + ":all20", len(checks) == len(scales) == len(weights) == 20 and set(checks) == set(scales) == set(weights), fatal=True)
    total = math.fsum(weights.values())
    data = {k: [] for k in ("checks", "losses", "trajectory", "parameters", "executions", "failures", "identities", "contracts")}
    frames, best, best_loss = {}, None, None
    for i, trial in enumerate(result["trials"]):
        folder = session / f"t{i:04d}"
        check(s + f":trial{i}:record", trial["index"] == i and trial == read(folder / "trial.json"), fatal=True)
        check(s + f":trial{i}:report", sha(folder / "fit/report.json") == trial["fit_report_sha256"], fatal=True)
        child, name = folder / "bundle", "candidates/t"
        trial_freeze = freeze(child, name)
        spec = read(child / name / "model_spec.json")
        expected = copy.deepcopy(parent)
        for parameter in plan["parameters"]:
            key, value = parameter["name"], trial["parameters"][parameter["name"]]
            expected["parameters"][key] = value
            before, after = parent["parameter_provenance"][key], spec["parameter_provenance"][key]
            changed = digest(value) != digest(parent["parameters"][key])
            derivation = (f"Calibrated numerical trial {i} under locked plan {binding['plan_sha256']}. Original derivation: "
                          + before["derivation"]) if changed else before["derivation"]
            expected["parameter_provenance"][key] = {**before, "derivation": derivation}
            check(s + f":trial{i}:provenance:" + key, after == expected["parameter_provenance"][key])
            check(s + f":trial{i}:bounds:" + key, parameter["lower"] <= value <= parameter["upper"], fatal=True)
            data["parameters"].append({"structure": s, "trial": i, "parameter": key, "value": value, "lower": parameter["lower"],
                                       "upper": parameter["upper"], "at_lower": value == parameter["lower"], "at_upper": value == parameter["upper"]})
        check(s + f":trial{i}:fixed_science", spec == expected, fatal=True)
        note = read(child / name / "calibration_trial.json")
        check(s + f":trial{i}:lineage", note == {"schema_version": 1, "kind": "numerical_parameter_trial",
            "trial_index": i, "parent_binding": result["binding"], "parameter_values": trial["parameters"],
            "value_origin": "unchanged_baseline" if i == 0 else "calibrated_trial",
            "scope": "source_only_not_target_validated"}, fatal=True)
        for filename in frozen["candidate_files"]:
            relative = filename.removeprefix("candidates/initial/")
            if relative != "model_spec.json":
                check(s + f":trial{i}:fixed:" + relative, sha(child / name / relative) == frozen["commitments"][filename], fatal=True)
        loss = aggregate_loss(trial["fit"], plan, criteria, s + f":trial{i}")
        if loss is not None and (best_loss is None or loss < best_loss): best, best_loss = i, loss
        data["trajectory"].append({"structure": s, "trial": i, "loss": loss, "best_so_far": best_loss,
                                   "feasible": loss is not None, "selected": i == result["selected_trial"]})
        for x in trial["fit"]["constraints"]:
            if x["status"] != "computed": data["failures"].append({"structure": s, "trial": i, **x})
    check(s + ":earliest_strict_minimum", best == result["selected_trial"], fatal=True)
    seal = read(session / "selection.json")
    check(s + ":selection_seal", seal["selected_trial"] == best and seal["fit_record_hashes"] ==
          [sha(session / f"t{i:04d}/trial.json") for i in range(len(result["trials"]))] and
          seal["selected_freeze_sha256"] == (sha(session / f"t{best:04d}/bundle/candidates/t/freeze.json") if best is not None else None)
          and seal["replay_seeds"] == [19111, 19123], fatal=True)
    replay_set = {"0"} | ({str(best)} if best is not None else set())
    count = 2 * len(result["trials"]) + 4 * len(replay_set)
    expected_usage = {"sessions": 1, "trials": len(result["trials"]), "executions": count, "reserved_seconds": count * 30}
    check(s + ":usage", result["usage"] == expected_usage and all(result["usage"][k] <= limits[k] for k in limits)
          and set(result["replay"]) == replay_set, fatal=True)
    for filename in result["files"]:
        if not filename.endswith("/executions/source/execution.json"): continue
        path = session / filename
        receipt = read(path)
        parts = filename.split("/")
        attempt, context = parts[1], parts[3]
        seed = 19101 if attempt == "fit" else int(attempt[1:])
        check(s + ":execution_context:" + filename, context in CONTEXTS, fatal=True)
        check(s + ":execution_limits:" + filename, receipt["limits"] == {**plan["execution"], "seed": seed}, fatal=True)
        output = path.parent / "output/generated.csv"
        logs = [(path.parent / k).stat().st_size for k in receipt["files"] if k.endswith(("stdout.log", "stderr.log"))]
        data["executions"].append({"structure": s, "trial": int(parts[0][1:]), "attempt": attempt, "context": context, "seed": seed,
            "status": receipt["status"], "error": json.dumps(receipt["error"]), "elapsed_seconds": receipt["elapsed_seconds"],
            "output_bytes": output.stat().st_size if output.exists() else 0, "max_log_bytes": max(logs, default=0),
            "timeout_cap_seconds": 30, "memory_cap_mb": 1024, "output_cap_bytes": 20000000, "log_cap_bytes": 100000})
    check(s + ":execution_count", len(data["executions"]) == count, fatal=True)
    for state, index in (("baseline", 0), ("selected", best)):
        if index is None: continue
        for seed in SEEDS:
            attempt = "fit" if seed == 19101 else f"v{seed}"
            folder = session / f"t{index:04d}" / attempt
            report = read(folder / "report.json")
            score = result["trials"][index]["fit"] if seed == 19101 else next(x["score"] for x in result["replay"][str(index)] if x["seed"] == seed)
            aggregate_loss(score, plan, criteria, f"{s}:{state}:{seed}")
            recorded = {(x["context_id"], x["check_id"]): x for x in score["constraints"]}
            feedback = {(c["id"], x["id"]): x for c in report["contexts"] if c["feedback"] is not None for x in c["feedback"]["checks"]}
            run_rows = []
            for context in CONTEXTS:
                path = folder / f"contexts/{context}/bundle/executions/source/output/generated.csv"
                rc = next(c for c in report["contexts"] if c["id"] == context)
                frame = None
                if rc["status"] == "success":
                    sha(path)
                    frame = pd.read_csv(path, dtype={"row_id": str})
                    frames[state, seed, context] = frame
                    valid = contract(frame, parent["parameters"]["contexts"][context])
                    for key, ok in valid.items(): check(f"{s}:{state}:{seed}:{context}:contract:{key}", ok)
                    data["contracts"].append({"structure": s, "state": state, "seed": seed, "context": context, **valid})
                for key, item in checks.items():
                    if key[0] != context: continue
                    value, n, error = None, 0, None
                    try:
                        if frame is None: raise ValueError("Failed source execution")
                        value, n = statistic(frame, item["operator"])
                    except Exception as exc: error = type(exc).__name__ + ": " + str(exc)
                    source = item["evidence_metadata"]["estimate"]
                    diff = None if value is None else value - source
                    scaled = None if diff is None else diff / scales[key]
                    contribution = None if scaled is None else weights[key] * scaled * scaled / total
                    rule = rules["pani_means" if key[1].startswith("P_NHANES_hba1c_age_") else key[1]]
                    lo, hi = (-rule[1], rule[1]) if rule[0] == "difference" else (rule[1], rule[2])
                    tested = diff if rule[0] == "difference" else value
                    passes = tested is not None and lo <= tested <= hi
                    calc = feedback.get(key, {}).get("calculation", {})
                    same = near(value, recorded[key]["value"]) and near(value, calc.get("value"))
                    check(f"{s}:{state}:{seed}:{key[1]}:independent_value", same, f"{value} vs {recorded[key]['value']}")
                    check(f"{s}:{state}:{seed}:{key[1]}:source_target", source == recorded[key]["reported_value"])
                    run_rows.append({"structure": s, "state": state, "trial": index, "seed": seed, "context": context,
                        "check_id": key[1], "kind": item["operator"]["kind"], "unit": item["operator"]["unit"], "n_selected": n,
                        "value": value, "source_value": source, "raw_difference": diff,
                        "absolute_difference": None if diff is None else abs(diff), "scale": scales[key], "weight": weights[key],
                        "scaled_difference": scaled, "loss_contribution": contribution, "recorded_value": recorded[key]["value"],
                        "independent_minus_recorded": None if value is None else value - recorded[key]["value"],
                        "calculation_reproduced": same, "criterion_type": rule[0], "criterion_lower": lo, "criterion_upper": hi,
                        "criterion_tested_value": tested, "criterion_pass": passes, "criterion_applies": seed != 19101, "error": error})
            loss = math.fsum(x["loss_contribution"] for x in run_rows) if len(run_rows) == 20 and all(x["loss_contribution"] is not None for x in run_rows) else None
            check(f"{s}:{state}:{seed}:independent_loss", near(loss, score["loss"]), f"{loss} vs {score['loss']}")
            worst = max((x["absolute_difference"] for x in run_rows if x["check_id"].startswith("P_NHANES_hba1c_age_") and x["absolute_difference"] is not None), default=None)
            data["losses"].append({"structure": s, "state": state, "seed": seed, "trial": index, "loss": loss,
                "recorded_loss": score["loss"], "all20_pass": all(x["criterion_pass"] for x in run_rows),
                "failed_criteria": sum(not x["criterion_pass"] for x in run_rows), "worst_pani_age_error": worst})
            data["checks"].extend(run_rows)
    if best is not None:
        for seed in SEEDS:
            for context in CONTEXTS:
                a, c = frames.get(("baseline", seed, context)), frames.get(("selected", seed, context))
                for col in COVARIATES:
                    same = a is not None and c is not None and np.array_equal(a[col].to_numpy(), c[col].to_numpy())
                    check(f"{s}:{seed}:{context}:exact_unchanged:{col}", same)
                    data["identities"].append({"structure": s, "seed": seed, "context": context, "column": col, "exactly_identical": same})
    data["summary"] = {"structure": s, "selected_trial": best, "stop_reason": result["stop_reason"], "usage": result["usage"],
        "reservation": intent["reservation"], "session_elapsed_seconds": result["elapsed_seconds"],
        "sum_execution_elapsed_seconds": math.fsum(x["elapsed_seconds"] for x in data["executions"]),
        "trial_cap_hit": len(result["trials"]) == 40, "failed_trials": sum(not x["feasible"] for x in data["trajectory"]),
        "failed_executions": sum(x["status"] != "success" for x in data["executions"]),
        "peak_memory_measured": False, "monetary_cost_measured": False, "scientific_requirements": criteria["scientific_requirements"]}
    data.update(frames=frames, parent=parent, plan=plan, criteria=criteria, panel=panel, evidence=evidence)
    return data

def figures(out, checks, losses, trajectory):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
                         "axes.spines.right": False, "pdf.fonttype": 42})
    colors = {"linear": "#225ea8", "alternative": "#a63603"}
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4), layout="constrained")
    for s in STRUCTURES:
        t = trajectory[trajectory.structure == s]
        axes[0].plot(t.trial, t.loss, color=colors[s], alpha=.3, lw=.8)
        axes[0].plot(t.trial, t.best_so_far, color=colors[s], lw=2, label=s.capitalize())
        for state, line, marker in (("baseline", "--", "o"), ("selected", "-", "s")):
            x = losses[(losses.structure == s) & (losses.state == state)].sort_values("seed")
            axes[1].plot(range(len(x)), x.loss, ls=line, marker=marker, color=colors[s], label=s.capitalize()+" "+state)
    axes[0].set(xlabel="Objective evaluation (0 = baseline)", ylabel="Declared weighted squared loss",
                title="Fit seed 19101: trials and best so far")
    axes[1].set(xticks=[0,1,2], xticklabels=["19101\nFitting", "19111\nUnused", "19123\nUnused"],
                ylabel="Declared weighted squared loss", title="Frozen baseline and selected parameters")
    for ax in axes: ax.grid(alpha=.2); ax.legend(fontsize=8)
    fig.suptitle("C3 source-only numerical development; loss is not clinical equivalence", fontsize=12)
    for ext in ("png","pdf"): fig.savefig(out / ("loss_and_trajectory."+ext), dpi=180)
    plt.close(fig)
    order = checks[checks.structure == "linear"].check_id.drop_duplicates().tolist()
    labels = [x.replace("J_T1_", "J ").replace("J_T2_", "J ").replace("P_NHANES_hba1c_age_", "P age ")
        .replace("P_NHANES_", "P ").replace("_task_derived", "").replace("_mg_dL_derived", " (mg/dL)")
        .replace("_derived", "").replace("_task", "").replace("_pct", " (%)").replace("_", " ") for x in order]
    columns, vals, failures = [], [], []
    for s in STRUCTURES:
        for state in ("baseline", "selected"):
            for seed in SEEDS:
                x = checks[(checks.structure == s) & (checks.state == state) & (checks.seed == seed)].set_index("check_id").reindex(order)
                columns.append(f"{s[:3]} {state[:3]}\n{seed}")
                vals.append(x.scaled_difference.to_numpy())
                failures.append((~x.criterion_pass.fillna(False)).to_numpy())
    matrix, fail = np.array(vals, dtype=float).T, np.array(failures, dtype=bool).T
    vmax = max(2, float(np.nanmax(abs(matrix))))
    fig, ax = plt.subplots(figsize=(12.6, 9.3), layout="constrained")
    im = ax.imshow(matrix, aspect="auto", cmap="RdBu_r", vmin=-vmax, vmax=vmax)
    for y in range(len(order)):
        for x in range(len(columns)):
            if fail[y,x]: ax.text(x,y,"x",ha="center",va="center",color="black",weight="bold",fontsize=12)
    ax.set(yticks=range(len(order)),yticklabels=labels,xticks=range(len(columns)),xticklabels=columns,
           title="Every source check retained: signed discrepancy / frozen loss scale")
    ax.tick_params(labelsize=8)
    ax.axvline(5.5,color="black",lw=1.2)
    fig.colorbar(im,ax=ax,label="(Generated statistic - published statistic) / scale",shrink=.7)
    fig.supxlabel("x = literal engineering criterion failure; fitting-seed marks are descriptive. Pani mean limit = 0.10; loss scale = 0.05.",fontsize=9)
    for ext in ("png","pdf"): fig.savefig(out / ("all_twenty_checks."+ext),dpi=180)
    plt.close(fig)

def summarize(out, data):
    names = ("checks","losses","trajectory","parameters","executions","failures","identities","contracts")
    tables = {name: pd.DataFrame([x for s in STRUCTURES for x in data[s][name]]) for name in names}
    checks, losses = tables["checks"], tables["losses"]
    comparisons, changes, summaries = [], [], []
    for s in STRUCTURES:
        for seed in SEEDS:
            group = losses[(losses.structure == s) & (losses.seed == seed)].set_index("state")
            base = group.loc["baseline","loss"]
            selected = group.loc["selected","loss"] if "selected" in group.index else np.nan
            comparisons.append({"structure":s,"seed":seed,"baseline_loss":base,"selected_loss":selected,
                "selected_minus_baseline":selected-base,"strictly_decreased":bool(np.isfinite(selected) and selected < base)})
            b = checks[(checks.structure==s)&(checks.state=="baseline")&(checks.seed==seed)].set_index("check_id")
            t = checks[(checks.structure==s)&(checks.state=="selected")&(checks.seed==seed)].set_index("check_id")
            for key in b.index:
                if key not in t.index: continue
                changes.append({"structure":s,"seed":seed,"context":b.loc[key,"context"],"check_id":key,"unit":b.loc[key,"unit"],
                    "baseline_difference":b.loc[key,"raw_difference"],"selected_difference":t.loc[key,"raw_difference"],
                    "raw_change":t.loc[key,"raw_difference"]-b.loc[key,"raw_difference"],
                    "absolute_error_change":t.loc[key,"absolute_difference"]-b.loc[key,"absolute_difference"],
                    "baseline_criterion_pass":bool(b.loc[key,"criterion_pass"]),"selected_criterion_pass":bool(t.loc[key,"criterion_pass"])})
        robust = all(x["strictly_decreased"] for x in comparisons if x["structure"]==s)
        unused = losses[(losses.structure==s)&(losses.state=="selected")&(losses.seed!=19101)]
        compatible = len(unused)==2 and bool(unused.all20_pass.all())
        identity = len(data[s]["identities"])==30 and all(x["exactly_identical"] for x in data[s]["identities"])
        category = "improvement with jointly acceptable declared source requirements" if robust and compatible and identity else (
            "tradeoff/incomplete compatibility" if robust else "no robust numerical improvement")
        summaries.append({**data[s]["summary"],"robust_improvement":robust,"selected_compatible":compatible,
                          "covariates_identical":identity,"category":category})
    cross = []
    for seed in (19111,19123):
        g = losses[(losses.state=="selected")&(losses.seed==seed)].set_index("structure")
        if set(g.index)!=set(STRUCTURES): continue
        failures = {}
        for s in STRUCTURES:
            failures[s]=set(checks[(checks.structure==s)&(checks.state=="selected")&(checks.seed==seed)&(~checks.criterion_pass)].check_id)
        cross.append({"seed":seed,"linear_loss":g.loc["linear","loss"],"alternative_loss":g.loc["alternative","loss"],
            "alternative_lower":bool(g.loc["alternative","loss"]<g.loc["linear","loss"]),
            "linear_worst_pani_error":g.loc["linear","worst_pani_age_error"],"alternative_worst_pani_error":g.loc["alternative","worst_pani_age_error"],
            "alternative_age_error_not_larger":bool(g.loc["alternative","worst_pani_age_error"]<=g.loc["linear","worst_pani_age_error"]),
            "alternative_new_failures":";".join(sorted(failures["alternative"]-failures["linear"])),
            "alternative_no_new_failure":not(failures["alternative"]-failures["linear"])})
    preferable = len(cross)==2 and all(x["alternative_lower"] and x["alternative_age_error_not_larger"] and x["alternative_no_new_failure"] for x in cross)
    cross_ids = []
    for state in ("baseline","selected"):
        for seed in SEEDS:
            for context in CONTEXTS:
                a,b=[data[s]["frames"].get((state,seed,context)) for s in STRUCTURES]
                equal=a is not None and b is not None and a[COVARIATES].equals(b[COVARIATES])
                check(f"cross_structure:{state}:{seed}:{context}:covariates",equal)
                cross_ids.append({"state":state,"seed":seed,"context":context,"exact_covariates_and_ids":equal})
    contexts=[copy.deepcopy(data[s]["parent"]["parameters"]["contexts"]) for s in STRUCTURES]
    for obj in contexts:
        for c in CONTEXTS: obj[c]["inputs"].pop("age_feature_reference")
    check("cross_structure:fixed_populations_except_declared_analytic_centering",contexts[0]==contexts[1])
    check("cross_structure:identical_evidence",data["linear"]["evidence"]==data["alternative"]["evidence"])
    check("cross_structure:identical_plan_criteria_panels",all(data["linear"][k]==data["alternative"][k] for k in ("plan","criteria","panel")))
    tables.update(loss_comparison=pd.DataFrame(comparisons),raw_changes=pd.DataFrame(changes),
                  structural_comparison=pd.DataFrame(cross),cross_structure_covariates=pd.DataFrame(cross_ids))
    filenames={"checks":"all20_checks","losses":"baseline_selected_loss","trajectory":"all_trials_trajectory",
        "parameters":"all_trials_parameters","executions":"execution_usage","failures":"all_trial_check_failures",
        "identities":"covariate_identity","contracts":"output_contracts"}
    for name,table in tables.items():
        table.to_csv(out/(filenames.get(name,name)+".csv"),index=False,float_format="%.17g")
    failed=checks[checks.criterion_applies&(~checks.criterion_pass)]
    failed.to_csv(out/"all_numeric_criterion_failures.csv",index=False,float_format="%.17g")
    figures(out,checks,losses,tables["trajectory"])
    decision={"scope":"source_only_no_target_evaluation","structures":summaries,"both_structures_retained":True,
        "alternative_meets_descriptive_preference":preferable,"structural_comparison":cross,
        "structure_selected_or_dropped":False,"clinical_equivalence_established":False,"target_access_authorized":False}
    write(out/"decision.json",decision)
    lines=["# Independent C3 source-only audit","",
        "Both frozen structures and all 20 source checks are retained. Each source table contains 6,000 fictional rows. No target evaluation, refit, new draw, source search or post-replay selection was performed.",""]
    for summary in summaries:
        s=summary["structure"]
        lines += [f"## {s.capitalize()}","",
            f"Result: **{summary['category']}**. Trial {summary['selected_trial']} was selected using seed 19101 only. Strict loss improvement at the fitting seed and both unused seeds: {summary['robust_improvement']}. All selected unused-seed numeric criteria pass: {summary['selected_compatible']}.","",
            "| Seed | Baseline loss | Selected loss | Selected minus baseline |","|---|---:|---:|---:|"]
        for x in comparisons:
            if x["structure"]==s: lines += [f"| {x['seed']} | {x['baseline_loss']:.10g} | {x['selected_loss']:.10g} | {x['selected_minus_baseline']:.10g} |"]
        sf=failed[(failed.structure==s)&(failed.state=="selected")]
        lines += ["",f"Selected numeric failures on unused seeds: {len(sf)}. Exact paired IDs and covariates preserved: {summary['covariates_identical']}. Full raw source discrepancies and changes are retained in the CSV files.",""]
        if len(sf):
            lines += ["| Seed | Failed check | Value | Signed source difference | Required interval |","|---|---|---:|---:|---|"]
            for _,x in sf.iterrows():
                lines += [f"| {x.seed} | {x.check_id} | {x.value:.9g} | {x.raw_difference:.9g} | {x.criterion_type}: [{x.criterion_lower:.9g}, {x.criterion_upper:.9g}] |"]
            lines += [""]
        params=tables["parameters"][(tables["parameters"].structure==s)&(tables["parameters"].trial==summary["selected_trial"])]
        hits=params[params.at_lower|params.at_upper]
        lines += [f"Execution: {summary['usage']['trials']}/40 trials, {summary['usage']['executions']}/88 reserved context executions, {summary['failed_trials']} infeasible trials and {summary['failed_executions']} failed executions. Stop reason: {summary['stop_reason']}. Trial cap hit: {summary['trial_cap_hit']}. Selected parameter-bound hits: {', '.join(hits.parameter) if len(hits) else 'none'}.",
            f"Recorded session elapsed: {summary['session_elapsed_seconds']:.6f} s; sum of execution elapsed times: {summary['sum_execution_elapsed_seconds']:.6f} s. The {summary['usage']['reserved_seconds']} s usage counter is timeout-cap accounting, not measured CPU consumption.",""]
    lines += ["## Descriptive structural comparison","",
        f"The alternative {'meets' if preferable else 'does not meet'} the complete authored preference rule: lower loss on both unused seeds, no larger worst Pani age-profile error, and no newly failed numeric compatibility requirement. Both structures remain reported; neither is selected or advanced to a target.","",
        "The fixed-denominator objective is a weighted mean of squared scaled discrepancies. Literal source criteria use absolute HbA1c mean error 0.05, SD error 0.03, and Pani age-mean error 0.10 percentage points, the stated projection intervals, and all declared marginal limits. The Pani mean objective scale is 0.05, distinct from its 0.10 compatibility limit. Equality is not numerical improvement.","",
        "Resource caps were 30 s, 1,024 MiB, 20,000,000 output bytes and 100,000 log bytes per execution. Execution receipts and retained output/log sizes are reported in execution_usage.csv. Peak memory, CPU time and monetary cost were not measured. A search cap, if reached, would not establish impossibility.","",
        "## Interpretation and next step","",
        "A robust reduction of aggregate source loss does not erase individual source failures. Source-side success could justify designing a separate fresh-target study; this unit authorizes no target access. These engineering limits cannot establish clinical equivalence, target utility, causal or individual validity, conditional biological curvature, or broad method validation.","",
        "The independence/covariance assumptions, finite age supports, residual law, Pani unweighted survey proxy, assay comparability and cross-source transport remain unverified. Lifelines' overall mean and Pani's 55–59 mean are distinct fixed source anchors; a future target location remains unidentified. Pani/Liu overlap is not independent replication, Pani SEs are not individual SDs, and Jansen interval confidence levels remain unknown.","",
        "## Independent QA and provenance","",
        f"No production generator, calibration or source-check module is imported. NumPy/pandas independently recompute mean, sample SD (ddof=1), event proportion and raw-unit OLS under exact declared selections. The comparison tolerance for reproducing floating arithmetic is rtol={RTOL:g}, atol={ATOL:g}; numeric source criteria and improvement use literal inequalities without tolerance. All-trial trajectories use aggregate records; only baseline/selected tables at the three fixed seeds are parsed.","",
        "The input manifest binds complete result files, release/authorization gates, candidate freezes, source inputs, budgets, execution artifacts and this analysis code. Hashes are retained-artifact commitments, not signatures against replacement of every record. All exported tables contain aggregate results only. Visual figure QA is recorded separately.",""]
    (out/"REPORT.md").write_text("\n".join(lines),encoding="utf-8")
    return decision

def selftest():
    common={"missing_policy":"error","selection":[]}
    df=pd.DataFrame({"age":[39,40,44,45],"hba1c":[1.,2.,4.,9.],"female":[0,1,1,0]})
    assert statistic(df,{**common,"kind":"mean","column":"hba1c"})==(4.,4)
    assert near(statistic(df,{**common,"kind":"sd","column":"hba1c"})[0],math.sqrt(38/3))
    assert statistic(df,{**common,"kind":"proportion","event":{"column":"female","op":"eq","value":1}})==(.5,4)
    assert statistic(df,{**common,"kind":"mean","column":"hba1c","selection":[{"column":"age","op":"ge","value":40},{"column":"age","op":"le","value":44}]})==(3.,2)
    x,f=np.arange(10,dtype=float),np.array([0,1]*5,dtype=float)
    reg=pd.DataFrame({"x":x,"f":f,"y":17+.35*x-.4*f})
    assert near(statistic(reg,{**common,"kind":"ols_coefficient","outcome":"y","predictors":["x","f"],"term":"x","include_intercept":True})[0],.35)
    bad=df.copy(); bad.loc[0,"hba1c"]=np.nan
    try: statistic(bad,{**common,"kind":"mean","column":"hba1c"})
    except ValueError: pass
    else: raise AssertionError("Nonfinite values accepted")
    for s in STRUCTURES:
        limits=thresholds(read(ROOT/s/"candidates/initial/scientific_criteria.json"))
        assert limits["pani_means"]==("difference",.10)
        assert limits["J_T1_hba1c_mean_pct"]==("difference",.05)
        assert limits["J_T1_hba1c_sd_pct"]==("difference",.03)
    print("PASS: artificial operator checks and frozen literal threshold parsing; no session result/table reads")

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest",action="store_true")
    parser.add_argument("--completed-authorized",action="store_true")
    parser.add_argument("--output",default="audit_v1")
    args=parser.parse_args()
    if args.selftest: selftest(); return
    if not args.completed_authorized: parser.error("Controller authorization required for completed-result reads")
    if not re.fullmatch(r"[A-Za-z0-9_-]+",args.output): parser.error("Use simple new output directory name")
    out=Path(__file__).parent/args.output
    out.mkdir(exist_ok=False)
    started=time.monotonic()
    try:
        sha(__file__)
        auth=read(ROOT/"POSTRUN_ANALYSIS_AUTHORIZATION.json")
        check("root_postrun_authorization",auth["decision"]=="authorize_postrun_analysis_only"
              and auth["generator_execution_allowed"] is False and auth["target_access_allowed"] is False,fatal=True)
        for s in STRUCTURES:
            entry=auth["complete_results"][s]
            check(s+":authorized_result",sha(ROOT/entry["path"])==entry["sha256"],fatal=True)
            check(s+":completed_receipt_hash",sha(ROOT/(s+"_COMPLETED.json"))==entry["receipt_sha256"],fatal=True)
            receipt=read(ROOT/(s+"_COMPLETED.json"))
            check(s+":completed_receipt_result",receipt["result_sha256"]==entry["sha256"],fatal=True)
        releases=read(ROOT/"ROOT_RELEASE_SET.json")
        check("root_release",releases["status"]=="approved" and releases["target_access_authorized"] is False
              and releases["post_replay_selection_authorized"] is False,fatal=True)
        hashes(ROOT,releases["bindings"],"release_bindings")
        review=read(ROOT/"review/PREEXECUTION_REVIEW_BINDINGS.json")
        check("preexecution_review",review["status"]=="PASS",fatal=True)
        hashes(ROOT,review["files"],"review_bindings")
        manifest=read(ROOT/"INPUT_MANIFEST.json")
        check("source_only_inputs",manifest["target_input_supplied"] is False,fatal=True)
        hashes(ROOT/"inputs",manifest["files"],"source_inputs")
        for s,entry in releases["structures"].items():
            for path,h in [(ROOT/entry["release"],entry["release_sha256"]),
                (ROOT/s/"candidates/initial/freeze.json",entry["initial_freeze_sha256"]),
                (ROOT/s/"candidates/initial/calibration_plan.json",entry["plan_sha256"]),
                (ROOT/s/"candidates/initial/scientific_criteria.json",entry["criteria_sha256"])]:
                check("release:"+str(path),sha(path)==h,fatal=True)
        data={s:session_audit(s,releases) for s in STRUCTURES}
        decision=summarize(out,data)
        status="PASS" if all(x["passed"] for x in QA) else "AUDIT_DISCREPANCIES_RETAINED"
        write(out/"QA.json",{"status":status,"check_count":len(QA),"failed_checks":[x for x in QA if not x["passed"]],
            "checks":QA,"audit_elapsed_seconds":time.monotonic()-started,"visual_review":"pending"})
        with (out/"REPORT.md").open("a",encoding="utf-8") as stream:
            stream.write(f"\nAudit mechanics: **{status}**, {len(QA)} checks. Numeric source-compatibility failures are separate from audit failures.\n")
    except Exception as exc:
        write(out/"AUDIT_ERROR.json",{"type":type(exc).__name__,"message":str(exc),"checks":QA,"action":"Error retained; no refit/rerun"})
        raise
    finally:
        write(out/"INPUT_HASH_MANIFEST.json",{"created_utc":datetime.now(timezone.utc).isoformat(),"script_sha256":sha(__file__),
            "runtime":{"python":sys.version,"platform":platform.platform(),"numpy":np.__version__,"pandas":pd.__version__},
            "input_count":len(INPUTS),"inputs":INPUTS,"patientlike_rows_exported":False})
        write(out/"OUTPUT_HASH_MANIFEST.json",{"files":{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(out.iterdir()) if p.is_file() and p.name!="OUTPUT_HASH_MANIFEST.json"}})
    print(json.dumps({"output":str(out),"qa":status,"categories":[x["category"] for x in decision["structures"]]}))

if __name__=="__main__": main()
