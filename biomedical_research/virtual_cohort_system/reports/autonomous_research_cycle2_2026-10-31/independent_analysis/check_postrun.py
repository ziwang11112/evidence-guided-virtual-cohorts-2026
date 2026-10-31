"""Independent, explicitly authorized postrun arithmetic audit; inert on import.

No production evaluator is imported, executed, or used for arithmetic. No network,
generation, repair, or retry is provided. --self-check uses small algebra only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import re
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

ROOT = Path("D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/virtual_cohort_system/work/autonomous_research_cycle2_2026-10-31")
SCRIPT = "independent_analysis/check_postrun.py"
AUTH = "independent_analysis/POSTRUN_AUTHORIZATION.json"
OUT = "independent_analysis/postrun_results"
REFERENCE = "custodian/private/reference_v2.csv"
FIXED = {
    "release": "EVALUATION_RELEASE.json",
    "completion": "analysis/results/EVALUATION_COMPLETED.json",
    "aggregate": "analysis/results/aggregate.json",
    "endpoints": "analysis/results/all_endpoints.csv",
    "checker": SCRIPT,
}
FIELDS = ("age", "female", "bmi", "glucose", "hba1c")
CLUSTERS = ("lab_est_dis", "lab_upm_dis")
CELLS = tuple(f"age_{lo}_{hi}_female_{sex}" for lo, hi in
              ((25, 39), (40, 54), (55, 69), (70, 79)) for sex in (0, 1))
ENDPOINTS = ("Q1_age10", "Q2_bmi5", "Q3_bmi5", "Q2_minus_Q3_bmi5",
             "glucose10_age_sex") + tuple(f"{field}.{stat}" for field in FIELDS
             for stat in ("mean", "sd_population", "q10", "q50", "q90")) + ("q1_residual_rms",)
SEEDS = (18203, 18211, 18223)
ATTEMPTS, RESAMPLING_SEED = 399, 18301
ATOL, RTOL = 1e-10, 1e-10  # Computational comparison only; not equivalence bounds.


class AuditError(ValueError):
    """Only fixed codes, never row values, are included in an error receipt."""


def need(ok, code):
    if not ok:
        raise AuditError(code)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def path(relative):
    need(isinstance(relative, str) and relative and not re.search(r'[\\:\x00<>"|?*]', relative), "unsafe_path")
    parts = relative.split("/")
    reserved = {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)), *(f"lpt{i}" for i in range(1, 10))}
    need(all(p not in ("", ".", "..") and not p.endswith((".", " ")) and
             p.split(".")[0].lower() not in reserved and all(ord(c) >= 32 for c in p)
             for p in parts), "unsafe_path_segment")
    candidate = ROOT
    for part in (None, *parts):
        if part is not None:
            candidate /= part
        need(not candidate.is_symlink() and not getattr(candidate, "is_junction", lambda: False)(), "linked_path")
    need(candidate.resolve().is_relative_to(ROOT.resolve()), "path_escape")
    return candidate


def bound(binding, ledger, expected=None):
    need(isinstance(binding, dict) and set(binding) == {"path", "sha256"}, "binding_shape")
    need(re.fullmatch(r"[0-9a-f]{64}", str(binding["sha256"])) is not None, "hash_shape")
    need(expected is None or binding["path"] == expected, "binding_path")
    body = path(binding["path"]).read_bytes()
    need(sha(body) == binding["sha256"], "bound_hash_changed")
    ledger[binding["path"]] = binding["sha256"]
    return body


def write_new(filename, obj):
    with filename.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(obj, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def table(body, *, reference=False):
    header = next(csv.reader(io.StringIO(body.decode("utf-8-sig"))))
    need(len(header) == len(set(header)), "invalid_input")
    if reference:
        need(set(header) == set(FIELDS + CLUSTERS), "reference_columns")
    frame = pd.read_csv(io.BytesIO(body), float_precision="round_trip", keep_default_na=False,
                        na_values=[""], dtype={c: "string" for c in CLUSTERS} if reference else None)
    need(all(c in frame for c in FIELDS) and len(frame) > 0, "invalid_input")
    try:
        values = frame[list(FIELDS)].to_numpy(dtype=float)
    except (TypeError, ValueError, OverflowError):
        raise AuditError("invalid_input") from None
    a, f = values[:, 0], values[:, 1]
    need(np.isfinite(values).all() and np.all((a >= 25) & (a <= 79) & (a == np.floor(a))) and
         np.all((f == 0) | (f == 1)) and np.all(values[:, 2:] > 0) and
         np.all(values[:, 3] < 126), "invalid_input")
    if reference:
        need(not frame[list(CLUSTERS)].isna().any().any(), "invalid_input")
    return frame, values


def groups(values):
    # Separate comparisons, not the production searchsorted/bin-count path.
    age_band = (values[:, 0] >= 40).astype(int) + (values[:, 0] >= 55) + (values[:, 0] >= 70)
    labels = 2 * age_band + values[:, 1].astype(int)
    members = [np.flatnonzero(labels == h) for h in range(8)]
    need(all(len(m) for m in members), "empty_demographic_cell")
    return members, labels


def balanced_mean(vector, members):
    return math.fsum(math.fsum(float(vector[i]) for i in member) / len(member)
                     for member in members) / 8


def exact_quantiles(vector, members, labels):
    """Inverse CDF using exact integer masses proportional to 1/n_h.

    Counts' LCM removes all binary summation ambiguity at 10/50/90% boundaries.
    This is independent of the engine's compensated floating summation.
    """
    common = math.lcm(*(len(member) for member in members))
    mass = [common // len(member) for member in members]
    total, cumulative, answer = 8 * common, 0, []
    pending = iter(((1, 10), (1, 2), (9, 10)))
    target = next(pending, None)
    for i in sorted(range(len(vector)), key=lambda j: vector[j]):
        cumulative += mass[int(labels[i])]
        while target is not None and cumulative * target[1] >= total * target[0]:
            answer.append(float(vector[i]))
            target = next(pending, None)
        if target is None:
            break
    return answer


def qr_fit(design, outcome, members):
    row_scale = np.empty(len(outcome), dtype=float)
    for member in members:
        row_scale[member] = math.sqrt(1 / (8 * len(member)))
    lhs, rhs = design * row_scale[:, None], outcome * row_scale
    singular = np.linalg.svd(lhs, compute_uv=False)  # Protocol's rank diagnostic only.
    cutoff = max(lhs.shape) * np.finfo(float).eps * singular[0]
    need(np.count_nonzero(singular > cutoff) == lhs.shape[1], "singular_design")
    q, r = np.linalg.qr(lhs, mode="reduced")
    try:
        beta = np.linalg.solve(r, q.T @ rhs)
    except np.linalg.LinAlgError:
        raise AuditError("singular_design") from None
    need(np.isfinite(beta).all(), "singular_design")
    return beta


def estimate(values, *, generated=False):
    members, labels = groups(values)
    if generated:
        need(len(values) == 2000 and all(len(m) == 250 for m in members), "generated_cell_quota")
    age, female, bmi, glucose, outcome = values.T
    design = np.array([np.ones(len(values)), (age - 50) / 10, female,
                       (bmi - 25) / 5, (glucose - 100) / 10]).T
    full = qr_fit(design, outcome, members)
    reduced = qr_fit(design[:, [0, 1, 2, 3]], outcome, members)
    secondary = qr_fit(design[:, [0, 1, 2, 4]], outcome, members)
    result = dict(zip(ENDPOINTS[:5], map(float, (full[1], reduced[3], full[3],
                                               reduced[3] - full[3], secondary[3]))))
    for j, field in enumerate(FIELDS):
        vector = values[:, j]
        mean = balanced_mean(vector, members)
        sd = math.sqrt(balanced_mean((vector - mean) ** 2, members))
        vals = [mean, sd, *exact_quantiles(vector, members, labels)]
        for stat, val in zip(("mean", "sd_population", "q10", "q50", "q90"), vals):
            result[f"{field}.{stat}"] = val
    result["q1_residual_rms"] = math.sqrt(balanced_mean((outcome - design @ full) ** 2, members))
    need(tuple(result) == ENDPOINTS and all(math.isfinite(x) for x in result.values()), "nonfinite_estimate")
    return result, {label: len(member) for label, member in zip(CELLS, members)}


def linear_percentile(matrix, probability):
    ordered = np.sort(matrix, axis=0)
    at = (len(ordered) - 1) * probability
    lo, hi = math.floor(at), math.ceil(at)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (at - lo)


def stability(frame, values):
    # First appearance of strata and PSUs is the public sampling contract.
    strata = {}
    for i, (stratum, psu) in enumerate(zip(frame[CLUSTERS[0]], frame[CLUSTERS[1]])):
        strata.setdefault(stratum, {}).setdefault(psu, []).append(i)
    clusters = [[np.array(rows, dtype=int) for rows in psus.values()] for psus in strata.values()]
    rng = np.random.default_rng(RESAMPLING_SEED)
    valid, failures, samples = [], [], []
    for attempt in range(1, ATTEMPTS + 1):
        selected = []
        for stratum in clusters:
            if len(stratum) == 1:
                selected.append(stratum[0])  # No RNG consumption for singleton strata.
            else:
                choices = rng.integers(0, len(stratum), size=len(stratum))
                selected.extend(stratum[int(index)] for index in choices)
        replicate = values[np.concatenate(selected)]
        try:
            estimates, _ = estimate(replicate)
        except AuditError as error:
            need(str(error) in {"empty_demographic_cell", "singular_design"}, "unexpected_replicate_failure")
            failures.append({"attempt": attempt, "type": str(error)})
        else:
            valid.append(attempt)
            samples.append([estimates[key] for key in ENDPOINTS])
    bands = dict.fromkeys(ENDPOINTS)
    if samples:
        matrix = np.asarray(samples)
        lower, upper = linear_percentile(matrix, .025), linear_percentile(matrix, .975)
        bands = {key: {"lower": float(lower[i]), "upper": float(upper[i])} for i, key in enumerate(ENDPOINTS)}
    return {
        "seed": RESAMPLING_SEED, "attempted": ATTEMPTS, "valid": len(valid), "failed": len(failures),
        "failure_counts": {code: sum(f["type"] == code for f in failures)
                           for code in ("empty_demographic_cell", "singular_design")},
        "failure_attempts": failures, "valid_attempts": valid, "bands": bands,
        "band_status": "available" if valid else "unavailable_no_valid_replicates",
        "percentiles": [2.5, 97.5], "percentile_method": "linear",
        "represented_lab_strata": len(clusters), "represented_lab_psus": sum(map(len, clusters)),
        "singleton_lab_strata": sum(len(s) == 1 for s in clusters),
    }


def flat(result):
    if result is None:
        return dict.fromkeys(ENDPOINTS)
    values = {**result["questions"], **result["secondary"],
              **{f"{field}.{stat}": value for field, stats in result["diagnostics"].items() for stat, value in stats.items()},
              "q1_residual_rms": result["q1_residual_rms"]}
    need(set(values) == set(ENDPOINTS), "reported_endpoint_set")
    return values


def gate():
    need(Path(__file__).resolve() == path(SCRIPT).resolve(), "checker_location")
    authorization_body = path(AUTH).read_bytes()  # First case file access is the fixed root authorization.
    authorization = json.loads(authorization_body)
    need(authorization.get("schema") == "ensanut_independent_postrun_authorization_v1" and
         authorization.get("issuer") == "root" and authorization.get("status") == "approved" and
         authorization.get("purpose") == "independent_fixed_postrun_audit" and
         authorization.get("reference_and_scheduled_output_access_authorized") is True, "audit_not_authorized")
    need(set(authorization.get("bindings", {})) == set(FIXED), "authorization_bindings")
    ledger = {AUTH: sha(authorization_body)}
    payload = {key: bound(authorization["bindings"][key], ledger, relative) for key, relative in FIXED.items()}
    release, completed, aggregate = (json.loads(payload[key]) for key in ("release", "completion", "aggregate"))
    need(release.get("schema") == "ensanut_evaluation_release_v1" and release.get("issuer") == "root" and
         release.get("status") == "approved" and release.get("effects_authorized") is True and
         release.get("purpose") == "fixed_target_evaluation_once", "evaluation_release_not_approved")
    need(completed.get("status") == "completed" and completed.get("release_sha256") == ledger[FIXED["release"]], "completion_release")
    need(completed.get("outputs") == {"aggregate.json": ledger[FIXED["aggregate"]],
                                     "all_endpoints.csv": ledger[FIXED["endpoints"]]}, "completion_outputs")
    need(aggregate.get("schema") == "ensanut_evaluation_aggregate_v1" and
         aggregate.get("release_id") == release.get("release_id") and
         aggregate.get("input_hashes", {}).get("case:EVALUATION_RELEASE.json") == ledger[FIXED["release"]], "aggregate_release")
    builders = release.get("builders", [])
    need(1 <= len(builders) <= 2 and len({b["id"] for b in builders}) == len(builders), "builder_set")
    by_builder = {b["id"]: b for b in builders}
    for b in builders:
        need(re.fullmatch(r"[A-Za-z0-9_-]+", b["id"]) is not None, "builder_id")
        path(b["bundle"])
        need("private" not in b["bundle"].split("/"), "private_bundle")
    need(len({str(path(b["bundle"]).resolve()).casefold() for b in builders}) == len(builders), "shared_bundle")
    schedule = release.get("schedule", [])
    keys = [(s["builder"], s["stage"], s["seed"]) for s in schedule]
    expected = {(b["id"], stage, seed) for b in builders for stage in ("initial", "final") for seed in SEEDS}
    need(len(keys) == len(expected) and set(keys) == expected, "scheduled_grid")
    indexed = dict(zip(keys, schedule))
    for s in schedule:
        need(type(s["seed"]) is int and s["status"] in {"success", "failed", "timeout"}, "scheduled_status_seed")
        need(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", s["run_id"]) is not None, "run_id")
        need((re.fullmatch(r"[0-9a-f]{64}", str(s.get("output_sha256"))) is not None)
             if s["status"] == "success" else s.get("output_sha256") is None, "scheduled_output_hash")
        need(s["stage_candidate"] == by_builder[s["builder"]][s["stage"] + "_candidate"], "stage_candidate")
        if s.get("retained_from") is not None:
            need(s["stage"] == "final" and s["retained_from"] == {"stage": "initial", "seed": s["seed"]}, "retention_link")
            previous = indexed[(s["builder"], "initial", s["seed"])]
            need(all(s.get(k) == previous.get(k) for k in ("execution_candidate", "run_id", "receipt_sha256", "output_sha256", "status")), "retention_identity")
        prefix = by_builder[s["builder"]]["bundle"] + "/executions/" + s["run_id"]
        receipt = json.loads(bound({"path": prefix + "/execution.json", "sha256": s["receipt_sha256"]}, ledger))
        need(all(receipt.get(k) == s[k] for k in ("run_id", "status")) and
             receipt.get("candidate") == s["execution_candidate"] and
             receipt.get("limits", {}).get("seed") == s["seed"], "receipt_identity")
        if s["status"] == "success":
            need(receipt.get("files", {}).get("output/generated.csv") == s["output_sha256"], "receipt_output")
    need(release.get("reference", {}).get("path") == REFERENCE, "reference_path")
    # Only these already-authorized documents are needed; no source reports or harness imports.
    for name, relative in (("protocol", "PROTOCOL_v2.md"), ("analysis_engine", "analysis/analytical_engine.py"),
                           ("evaluation_controller", "analysis/run_evaluation.py")):
        bound(release["bindings"][name], ledger, relative)
    endpoint_rows = list(csv.DictReader(io.StringIO(payload["endpoints"].decode("utf-8"))))
    return release, aggregate, endpoint_rows, ledger


def equal_number(a, b, *, exact=False):
    if a is None or b is None:
        return a is None and b is None
    try:
        return math.isfinite(float(a)) and math.isfinite(float(b)) and (
            float(a) == float(b) if exact else math.isclose(float(a), float(b), rel_tol=RTOL, abs_tol=ATOL))
    except (ValueError, TypeError, OverflowError):
        return False


def run_postrun():
    release, aggregate, csv_rows, ledger = gate()
    output = path(OUT)
    need(not output.exists(), "audit_results_exist_no_repeat")
    output.mkdir()
    write_new(output / "ATTEMPT.json", {"started_utc": datetime.now(timezone.utc).isoformat(), "input_hashes": dict(ledger)})
    try:
        reference_body = bound(release["reference"], ledger, REFERENCE)
        reference_frame, reference_values = table(reference_body, reference=True)
        reference_estimates, reference_counts = estimate(reference_values)
        need(len(reference_values) >= 400 and min(reference_counts.values()) >= 30, "reference_readiness_floor")
        reference_bands = stability(reference_frame, reference_values)
        cache, computed_slots = {}, []
        builders = {b["id"]: b for b in release["builders"]}
        for slot in release["schedule"]:
            record = {k: slot.get(k) for k in ("builder", "stage", "seed", "stage_candidate", "execution_candidate", "run_id", "retained_from", "receipt_sha256", "output_sha256")}
            if slot["status"] != "success":
                record.update(status=slot["status"], failure="execution_" + slot["status"], estimates=None)
            else:
                relative = builders[slot["builder"]]["bundle"] + "/executions/" + slot["run_id"] + "/output/generated.csv"
                body = bound({"path": relative, "sha256": slot["output_sha256"]}, ledger)
                if slot["output_sha256"] not in cache:
                    try:
                        _, values = table(body)
                        estimates, counts = estimate(values, generated=True)
                        item = {"status": "success", "estimates": estimates, "n": len(values), "demographic_cell_counts": counts}
                    except AuditError as error:
                        need(str(error) in {"invalid_input", "empty_demographic_cell", "singular_design", "generated_cell_quota"}, "unexpected_generated_failure")
                        item = {"status": "invalid_generated_table", "failure": str(error), "estimates": None}
                    cache[slot["output_sha256"]] = item
                record.update(cache[slot["output_sha256"]])
            computed_slots.append(record)
        mismatches, comparison = [], []

        def check(condition, location):
            if not condition:
                mismatches.append(location)

        reported_slots = {(s["builder"], s["stage"], s["seed"]): s for s in aggregate["scheduled_results"]}
        check(len(reported_slots) == len(aggregate["scheduled_results"]) == len(computed_slots), "scheduled_result_count")
        check(set(reported_slots) == {(s["builder"], s["stage"], s["seed"]) for s in computed_slots}, "scheduled_result_grid")
        csv_index = {(r["kind"], r["builder"], r["stage"], r["seed"], r["endpoint"]): r for r in csv_rows}
        check(len(csv_index) == len(csv_rows) == 31 * (1 + len(computed_slots)), "csv_row_count")

        def compare_result(kind, current, reported, builder="", stage="reference", seed="", status="success", output_hash=None):
            for endpoint in ENDPOINTS:
                label = f"{kind}/{builder}/{stage}/{seed}/{endpoint}"
                actual, saved = current.get(endpoint), reported.get(endpoint)
                exact = endpoint.endswith((".q10", ".q50", ".q90"))
                point_match = equal_number(actual, saved, exact=exact)
                check(point_match, label + "/aggregate_value")
                row = csv_index.get((kind, builder, stage, str(seed), endpoint), {})
                csv_val = None if row.get("value") in (None, "") else row["value"]
                csv_match = equal_number(actual, csv_val, exact=exact)
                check(csv_match and bool(row), label + "/csv_value")
                check(row.get("status") == status and row.get("output_sha256", "") == (output_hash or ""), label + "/csv_metadata")
                band = reference_bands["bands"][endpoint] if kind == "reference" else None
                for side in ("lower", "upper"):
                    csv_bound = None if row.get(side) in (None, "") else row[side]
                    check(equal_number(band[side] if band else None, csv_bound), label + "/csv_" + side)
                comparison.append({"kind": kind, "builder": builder, "stage": stage, "seed": seed,
                    "status": status, "endpoint": endpoint, "independent_value": actual, "reported_value": saved,
                    "absolute_difference": abs(actual - saved) if actual is not None and isinstance(saved, (int, float)) else None,
                    "exact_quantile_comparison": exact, "aggregate_match": point_match, "csv_match": csv_match,
                    "output_sha256": output_hash})

        compare_result("reference", reference_estimates, flat(aggregate["reference"]), output_hash=release["reference"]["sha256"])
        check(aggregate["reference"].get("n") == len(reference_values), "reference_n")
        check(aggregate["reference"].get("demographic_cell_counts") == reference_counts, "reference_cells")
        for key, value in reference_bands.items():
            if key != "bands":
                check(aggregate["reference_stability"].get(key) == value, "stability/" + key)
        check(set(aggregate["reference_stability"]["bands"]) == set(ENDPOINTS), "stability/endpoint_set")
        for endpoint, band in reference_bands["bands"].items():
            reported = aggregate["reference_stability"]["bands"].get(endpoint)
            check((band is None and reported is None) or (isinstance(band, dict) and isinstance(reported, dict) and
                  all(equal_number(band[side], reported.get(side)) for side in ("lower", "upper"))), "stability/" + endpoint)
        for current in computed_slots:
            key = current["builder"], current["stage"], current["seed"]
            reported = reported_slots.get(key, {})
            for name in ("builder", "stage", "seed", "stage_candidate", "execution_candidate", "run_id", "retained_from", "receipt_sha256", "output_sha256", "status", "failure"):
                check(current.get(name) == reported.get(name), "slot/" + "/".join(map(str, key)) + "/" + name)
            if current["estimates"] is not None:
                saved_analysis = reported.get("analysis") or {}
                check(saved_analysis.get("n") == current["n"], "slot/" + "/".join(map(str, key)) + "/n")
                check(saved_analysis.get("demographic_cell_counts") == current["demographic_cell_counts"], "slot/" + "/".join(map(str, key)) + "/cells")
            compare_result("generated", current["estimates"] or dict.fromkeys(ENDPOINTS), flat(reported.get("analysis")),
                           *key, current["status"], current["output_sha256"])
        summary_counts = {"scheduled_slots": len(computed_slots), "unique_output_contents": len(cache),
            "unique_successful_execution_runs": len({(s["builder"], s["run_id"]) for s in release["schedule"] if s["status"] == "success"}),
            "successful_analytical_slots": sum(s["status"] == "success" for s in computed_slots),
            "failed_slots": sum(s["status"] != "success" for s in computed_slots)}
        for key, value in summary_counts.items():
            check(aggregate.get(key) == value, "summary/" + key)
        for relative, digest in ledger.items():
            need(sha(path(relative).read_bytes()) == digest, "consumed_input_changed")
        report = {"schema": "ensanut_independent_aggregate_audit_v1", "release_id": release["release_id"],
            "status": "match" if not mismatches else "discrepancies", "input_hashes": ledger,
            "comparison_rule": {"absolute_tolerance": ATOL, "relative_tolerance": RTOL,
                "point_quantiles": "exact equality to rational balanced-mass inverse CDF",
                "interpretation": "Numerical verification only; no biological equivalence decision."},
            "software": {"python": sys.version, "numpy": np.__version__, "pandas": pd.__version__},
            **summary_counts, "endpoint_count": len(ENDPOINTS), "mismatch_count": len(mismatches), "mismatches": mismatches,
            "reference": {"n": len(reference_values), "demographic_cell_counts": reference_counts, "estimates": reference_estimates},
            "reference_stability": reference_bands, "scheduled_results": computed_slots,
            "limitations": ["Replicate estimates are recomputed internally but not exported or available in the production aggregate for pairwise comparison.",
                "Execution and preparation provenance remain the responsibility of the bound production release; no source data or logs are inspected."]}
        write_new(output / "comparison.json", report)
        with (output / "endpoint_comparison.csv").open("x", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(comparison[0]))
            writer.writeheader()
            writer.writerows(comparison)
        write_new(output / "COMPLETED.json", {"status": report["status"], "completed_utc": datetime.now(timezone.utc).isoformat(),
            "outputs": {name: sha((output / name).read_bytes()) for name in ("comparison.json", "endpoint_comparison.csv")}})
        return {"status": report["status"], "mismatch_count": len(mismatches), **summary_counts}
    except Exception as error:
        write_new(output / "FAILURE.json", {"status": "failed_attempt_no_retry", "type": type(error).__name__,
                  "reason": str(error) if isinstance(error, AuditError) else "unexpected_error_no_rows_exported"})
        raise


def self_check():
    # Abstract arithmetic vectors, not a biomedical cohort or generated model.
    members = [np.array([i]) for i in range(8)]
    labels = np.arange(8)
    vector = np.arange(8, dtype=float)
    assert balanced_mean(vector, members) == 3.5
    assert balanced_mean((vector - 3.5) ** 2, members) == 5.25
    assert exact_quantiles(vector, members, labels) == [0.0, 3.0, 7.0]
    # Exact 10% boundary: eight cells of five rows, each mass 1/40.
    equal_cells = [np.arange(i * 5, (i + 1) * 5) for i in range(8)]
    assert exact_quantiles(np.arange(40), equal_cells, np.repeat(np.arange(8), 5)) == [3.0, 19.0, 35.0]
    # Unequal cells: each cell has equal mass, though rows do not.
    unequal = [np.arange(i * (i + 1) // 2, (i + 1) * (i + 2) // 2) for i in range(8)]
    uneven_labels = np.concatenate([np.full(i + 1, i) for i in range(8)])
    assert exact_quantiles(uneven_labels, unequal, uneven_labels) == [0.0, 3.0, 7.0]
    design = np.column_stack([np.ones(8), vector, (vector % 2)])
    beta = qr_fit(design, 2 + 3 * vector - (vector % 2), members)
    assert np.allclose(beta, [2, 3, -1], atol=1e-12, rtol=0)
    try:
        qr_fit(np.column_stack([vector, vector]), vector, members)
    except AuditError as error:
        assert str(error) == "singular_design"
    else:
        raise AssertionError("rank check")
    assert linear_percentile(np.array([[0.], [10.], [20.]]), .025)[0] == .5
    assert linear_percentile(np.array([[0.], [10.], [20.]]), .975)[0] == 19.5
    assert len(ENDPOINTS) == 31
    return {"status": "algebra_checks_passed", "actual_data_access": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--self-check", action="store_true", help="Run hand-computable abstract algebra checks only.")
    mode.add_argument("--run-postrun", action="store_true", help="Require the separate fixed root authorization, then audit once.")
    args = parser.parse_args(argv)
    if not args.self_check and not args.run_postrun:
        parser.print_help()
        return 0
    try:
        result = self_check() if args.self_check else run_postrun()
        print(json.dumps(result))
        return int(result["status"] == "discrepancies")
    except Exception as error:
        print(json.dumps({"status": "rejected_or_failed", "type": type(error).__name__,
                          "reason": str(error) if isinstance(error, AuditError) else "no_rows_exported"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
