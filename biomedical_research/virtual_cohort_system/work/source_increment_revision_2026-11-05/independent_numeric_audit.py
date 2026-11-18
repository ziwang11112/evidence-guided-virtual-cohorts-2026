"""Independent new-table audit; never imports the provider or its engine.

Run only after new-unit closure and completed evaluation. No generator or
separate reference file is opened. Embedded reference fields in RESULTS.json
are ignored. New tables are read only after freeze/execution/hash verification.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import math
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
BUNDLE = PROJECT.parent.parent / "evcIncE01"
CANDIDATE = "candidates/source_increment"
SEEDS = (5301, 5302, 5303)
COLUMNS = ("age", "female", "bmi", "glucose", "hba1c")
UNITS = dict(zip(COLUMNS, ("year", "1", "kg/m^2", "mg/dL", "%")))
PRIMARY = {"Q1_age10": "%/10years", "Q2_bmi5": "%/5kg/m^2", "Q3_bmi5": "%/5kg/m^2"}
DIAGNOSTICS = {"Q2_minus_Q3_bmi5": "%/5kg/m^2", "glucose10_age_sex": "%/10mg/dL", "q1_residual_rms": "%"}
DIAGNOSTICS.update({f"{field}.{stat}": unit for field, unit in UNITS.items()
                    for stat in ("mean", "sd_population", "q10", "q50", "q90")})
ENDPOINTS = {**PRIMARY, **DIAGNOSTICS}
ABS_TOL = 1e-10
REL_TOL = 1e-10


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def inside(base, relative):
    require(isinstance(relative, str) and "\\" not in relative, "Noncanonical relative path")
    relative_path = Path(relative)
    require(not relative_path.is_absolute() and ".." not in relative_path.parts, "Unsafe relative path")
    path = base / relative_path
    require(path.resolve().is_relative_to(base.resolve()), "Path escapes binding root")
    require(not any(part.is_symlink() or getattr(part, "is_junction", lambda: False)()
                    for part in (path, *path.parents)), "Linked binding path")
    return path


def gate():
    """Metadata/hash verification only; no table is parsed here."""
    closure = read(ROOT / "CLOSURE.json")
    commit_path = ROOT / "FREEZE_COMMITMENT.json"
    commit = read(commit_path)
    require(closure["scientific_authoring_closed"] is True, "Authoring is not closed")
    require(closure["candidate"] == commit["candidate"] == CANDIDATE, "Candidate identity changed")
    require(closure["freeze_commitment_sha256"] == sha(commit_path), "Freeze commitment changed")
    require(commit["seeds"] == list(SEEDS), "Committed schedule changed")
    require([x["seed"] for x in closure["slots"]] == list(SEEDS), "Closed schedule changed")
    require(all(type(x["seed"]) is int for x in closure["slots"]), "Invalid seed type")
    require(closure["physical_attempts"] == 3, "Unsupported attempt extension; audit needs review")
    require(len(list((ROOT / "attempts").glob("*.reserved.json"))) == 3, "Attempt inventory changed")
    for key, path in (("controller_sha256", ROOT / "run_unit.py"),
                      ("candidate_review_sha256", ROOT / "CANDIDATE_REVIEW_GATE.json"),
                      ("protocol_sha256", ROOT / "PROTOCOL.md"),
                      ("clarification_sha256", ROOT / "PROTOCOL_CLARIFICATION_01.md")):
        require(commit[key] == sha(path), "Committed artifact changed: " + key)
    freeze_path = BUNDLE / CANDIDATE / "freeze.json"
    require(sha(freeze_path) == commit["freeze_sha256"], "Frozen candidate changed")
    frozen = read(freeze_path)
    require(frozen["candidate"] == CANDIDATE and frozen["route"] == "generator.py", "Wrong frozen candidate/route")
    for relative, digest in frozen["commitments"].items():
        require(sha(inside(BUNDLE, relative)) == digest, "Frozen artifact changed: " + relative)
    result_path = ROOT / "evaluation" / "RESULTS.json"
    require(read(ROOT / "evaluation" / "COMPLETED.json")["results_sha256"] == sha(result_path), "Evaluation changed")
    result = read(result_path)
    require(result["closure_sha256"] == sha(ROOT / "CLOSURE.json"), "Evaluation closure mismatch")
    require(result["scheduled_slots"] == 3 and len(result["slots"]) == 3, "Evaluation slot coverage mismatch")
    require([x["seed"] for x in result["slots"]] == list(SEEDS), "Evaluation schedule mismatch")
    task = read(BUNDLE / "task.json")
    require(task["mode"] == "whole_cohort" and task["n_rows"] == 3000, "Unexpected task")
    for slot, evaluated in zip(closure["slots"], result["slots"]):
        seed, run_id = slot["seed"], f"increment_{slot['seed']}_a1"
        require(slot["run_id"] == evaluated["run_id"] == run_id, "Run identity mismatch")
        require(slot["status"] == evaluated["status"], "Evaluation execution status mismatch")
        reservation_path = ROOT / "attempts" / f"{run_id}.reserved.json"
        outcome_path = ROOT / "attempts" / f"{run_id}.result.json"
        require(sha(reservation_path) == slot["reservation_sha256"], "Reservation changed")
        require(sha(outcome_path) == slot["result_sha256"], "Execution result changed")
        reservation, outcome = read(reservation_path), read(outcome_path)
        require(reservation["run_id"] == outcome["run_id"] == run_id, "Attempt run mismatch")
        require(reservation["seed"] == outcome["seed"] == seed, "Attempt seed mismatch")
        require(reservation["candidate"] == CANDIDATE and outcome["status"] == slot["status"], "Attempt candidate/status mismatch")
        if slot["status"] != "controller_exception":
            run_root = BUNDLE / "executions" / run_id
            receipt_path = run_root / "execution.json"
            require(sha(receipt_path) == outcome["receipt_sha256"], "Execution receipt changed")
            receipt = read(receipt_path)
            require(receipt["run_id"] == run_id and receipt["candidate"] == CANDIDATE, "Receipt identity mismatch")
            require(receipt["candidate_freeze_sha256"] == commit["freeze_sha256"], "Receipt freeze mismatch")
            require(type(receipt["limits"]["seed"]) is int and receipt["limits"]["seed"] == seed, "Receipt seed mismatch")
            require(receipt["status"] == slot["status"] and receipt["route"] == "generator.py", "Receipt status/route mismatch")
            for relative, digest in receipt["files"].items():
                require(sha(inside(run_root, relative)) == digest, "Execution artifact changed: " + relative)
            if slot["status"] == "success":
                require(receipt["generator_executed"] is True, "Missing generator execution identity")
                require(receipt["runtime"]["backend"] == "wsl_bubblewrap", "Wrong execution backend")
                require(sha(run_root / "output/generated.csv") == slot["table_sha256"] == outcome["table_sha256"] == evaluated["table_sha256"], "Closed table mismatch")
    return closure, result


def quantiles(values, weights):
    """Specified inverse empirical CDF with compensated, ungrouped row mass."""
    ordered = sorted(zip(map(float, values), map(float, weights)), key=lambda pair: pair[0])
    cumulative, running, correction = [], 0.0, 0.0
    for _, weight in ordered:
        combined = running + weight
        larger, smaller = (running, weight) if abs(running) >= abs(weight) else (weight, running)
        correction += (larger - combined) + smaller
        running = combined
        cumulative.append(running + correction)
    answer = {}
    for probability, name in ((0.1, "q10"), (0.5, "q50"), (0.9, "q90")):
        threshold = probability * cumulative[-1]
        index = next((i for i, mass in enumerate(cumulative) if mass >= threshold), len(ordered) - 1)
        answer[name] = ordered[index][0]
    return answer


def weighted_fit(matrix, outcome, weights):
    """QR fit independent of the provider's np.linalg.lstsq coefficient path."""
    root_weights = np.sqrt(weights)
    design = matrix * root_weights[:, None]
    response = outcome * root_weights
    singular = np.linalg.svd(design, compute_uv=False)
    cutoff = float(max(matrix.shape) * np.finfo(np.float64).eps * singular[0])
    rank = int(np.count_nonzero(singular > cutoff))
    detail = {"rank": rank, "columns": int(matrix.shape[1]), "rank_tolerance": cutoff,
              "singular_values": singular.tolist(),
              "condition_number": float(singular[0] / singular[-1]) if singular[-1] > 0 else None}
    require(rank == matrix.shape[1], "Independent design is rank deficient: " + json.dumps(detail))
    orthogonal, triangular = np.linalg.qr(design, mode="reduced")
    beta = np.linalg.solve(triangular, orthogonal.T @ response)
    require(np.isfinite(beta).all(), "Independent coefficient is nonfinite")
    residual = outcome - matrix @ beta
    detail["residual_rms"] = math.sqrt(math.fsum(float(w * r * r) for w, r in zip(weights, residual)) / math.fsum(weights))
    return beta, detail


def recompute(table):
    """Read only a verified new generated table and independently calculate."""
    frame = pd.read_csv(table, dtype={"row_id": "string"}, float_precision="round_trip",
                        keep_default_na=False, na_values=[""])
    require(list(frame.columns) == ["row_id", *COLUMNS] and len(frame) == 3000, "Invalid table shape")
    require(frame["row_id"].notna().all() and frame["row_id"].is_unique, "Invalid row identifiers")
    values = frame.loc[:, COLUMNS].to_numpy(dtype=np.float64)
    require(np.isfinite(values).all(), "Nonfinite scientific value")
    age, female, bmi, glucose, hba1c = values.T
    require(np.all((age >= 25) & (age < 80) & (age == np.floor(age))), "Invalid ages")
    require(np.isin(female, (0, 1)).all(), "Invalid sex coding")
    require((values[:, 2:] > 0).all() and (glucose < 126).all(), "Invalid measurement bounds")
    masks = [(age >= lower) & (age < upper) & (female == sex)
             for lower, upper in ((25, 40), (40, 55), (55, 70), (70, 80)) for sex in (0, 1)]
    counts = [int(mask.sum()) for mask in masks]
    require(counts == [375] * 8, "Wrong demographic allocation")
    weights = np.empty(len(frame), dtype=np.float64)
    for mask, count in zip(masks, counts):
        weights[mask] = 1.0 / (8 * count)
    design = np.column_stack((np.ones(len(frame)), (age - 50) / 10, female,
                              (bmi - 25) / 5, (glucose - 100) / 10))
    full, full_info = weighted_fit(design, hba1c, weights)
    reduced, reduced_info = weighted_fit(design[:, :4], hba1c, weights)
    glucose_fit, glucose_info = weighted_fit(design[:, [0, 1, 2, 4]], hba1c, weights)
    output = {"Q1_age10": float(full[1]), "Q2_bmi5": float(reduced[3]), "Q3_bmi5": float(full[3]),
              "Q2_minus_Q3_bmi5": float(reduced[3] - full[3]),
              "glucose10_age_sex": float(glucose_fit[3]), "q1_residual_rms": full_info["residual_rms"]}
    total = math.fsum(weights)
    for name, column in zip(COLUMNS, values.T):
        mean = math.fsum(float(w * x) for w, x in zip(weights, column)) / total
        variance = math.fsum(float(w * (x - mean) ** 2) for w, x in zip(weights, column)) / total
        stats = {"mean": mean, "sd_population": math.sqrt(variance), **quantiles(column, weights)}
        output.update({f"{name}.{stat}": value for stat, value in stats.items()})
    _, bmi_cond = weighted_fit(design[:, [0, 1, 2, 4]], bmi, weights)
    _, glucose_cond = weighted_fit(design[:, :4], glucose, weights)
    extra = {"n": len(frame), "cell_counts": counts,
             "duplicate_measurement_rows": int(frame.loc[:, COLUMNS].duplicated().sum()),
             "models": {"full": full_info, "reduced": reduced_info, "glucose_age_sex": glucose_info},
             "conditional_variability": {
                 "bmi_given_age_sex_glucose_rms": {"value": bmi_cond["residual_rms"], "unit": "kg/m^2"},
                 "glucose_given_age_sex_bmi_rms": {"value": glucose_cond["residual_rms"], "unit": "mg/dL"}},
             "interpretation": "Generated-only conditional variability and numerical rank; no new target endpoint."}
    require(set(output) == set(ENDPOINTS), "Independent endpoint implementation incomplete")
    return output, extra


def compare(evaluated, independent, extra):
    rows = [*evaluated["analyses"], *evaluated["diagnostics"]]
    require(len(evaluated["analyses"]) == 3 and len(evaluated["diagnostics"]) == 28, "Reported endpoint category count changed")
    require(len(rows) == 31 and {row["id"] for row in rows} == set(ENDPOINTS), "Reported endpoint coverage changed")
    comparisons = []
    for row in rows:
        name = row["id"]
        require(row["unit"] == ENDPOINTS[name], "Reported unit changed: " + name)
        computed = independent is not None and row["status"] == "computed" and isinstance(row["value"], (int, float)) and not isinstance(row["value"], bool) and math.isfinite(row["value"])
        difference = float(independent[name] - row["value"]) if computed else None
        quantile = name.rsplit(".", 1)[-1] in {"q10", "q50", "q90"}
        agrees = computed and (difference == 0 if quantile else math.isclose(independent[name], row["value"], rel_tol=REL_TOL, abs_tol=ABS_TOL))
        record = {"id": name, "unit": ENDPOINTS[name], "reported_status": row["status"],
                  "reported_generated_value": row["value"],
                  "independent_value": independent[name] if independent is not None else None,
                  "signed_numeric_difference": difference,
                  "audit_status": "matched" if agrees else "mismatch" if independent is not None else "not_recomputed"}
        if name in PRIMARY and independent is not None:
            expected_rank = extra["models"]["reduced" if name == "Q2_bmi5" else "full"]["rank"]
            record.update(reported_rank=row.get("rank"), independent_rank=expected_rank)
            if row.get("rank") != expected_rank:
                record["audit_status"] = "mismatch"
        comparisons.append(record)
    return comparisons


def audit():
    require((ROOT / "CLOSURE.json").is_file() and (ROOT / "evaluation/RESULTS.json").is_file(), "Closure and evaluation required before audit")
    dest = ROOT / "independent_audit"
    dest.mkdir(exist_ok=False)
    write(dest / "STARTED.json", {"created_utc": datetime.now(timezone.utc).isoformat(), "script_sha256": sha(__file__),
                                  "absolute_tolerance": ABS_TOL, "relative_tolerance": REL_TOL, "quantiles_require_exact_match": True})
    try:
        closure, result = gate()
        slots = []
        for slot, evaluated in zip(closure["slots"], result["slots"]):
            item = {"seed": slot["seed"], "run_id": slot["run_id"], "execution_status": slot["status"], "table_sha256": slot.get("table_sha256")}
            independent = extra = None
            try:
                if slot["status"] == "success":
                    independent, extra = recompute(BUNDLE / "executions" / slot["run_id"] / "output/generated.csv")
                    item["independent_diagnostics"] = extra
                else:
                    item["failure"] = "Execution did not succeed; no table parsed"
                item["endpoint_comparisons"] = compare(evaluated, independent, extra)
                item["status"] = ("matched" if independent is not None and all(row["audit_status"] == "matched" for row in item["endpoint_comparisons"])
                                  else "mismatch" if independent is not None else "unavailable")
            except Exception as error:
                item.update(status="audit_failure", error={"type": type(error).__name__, "message": str(error)})
                item["endpoint_comparisons"] = [{"id": name, "unit": unit, "audit_status": "not_recomputed"} for name, unit in ENDPOINTS.items()]
            slots.append(item)
        # Recheck all closed commitments after numerical work; still no reference read.
        gate()
        status = "passed" if all(slot["status"] == "matched" for slot in slots) else "mismatch_or_unavailable"
        report = {"status": status, "created_utc": datetime.now(timezone.utc).isoformat(),
                  "closure_sha256": sha(ROOT / "CLOSURE.json"), "evaluation_sha256": sha(ROOT / "evaluation/RESULTS.json"),
                  "script_sha256": sha(__file__), "scheduled_slots": 3, "scheduled_endpoints_per_slot": 31,
                  "reference_fields_used": False, "provider_or_engine_imported": False, "generator_executed": False,
                  "method": "Independent QR WLS, compensated inverse-CDF quantiles, fsum moments; generated-only audit",
                  "tolerances": {"absolute": ABS_TOL, "relative": REL_TOL, "quantiles_exact": True}, "slots": slots}
        write(dest / "RESULTS.json", report)
        write(dest / "COMPLETED.json", {"status": status, "results_sha256": sha(dest / "RESULTS.json")})
        return {"status": status, "scheduled_slots": 3, "matched_slots": sum(slot["status"] == "matched" for slot in slots)}
    except Exception as error:
        write(dest / "FAILED.json", {"type": type(error).__name__, "message": str(error)})
        raise


if __name__ == "__main__":
    summary = audit()
    print(json.dumps(summary))
    sys.exit(0 if summary["status"] == "passed" else 2)
