"""Independent post-closure numerical audit; no model/provider/reference calls.

audit() first calls the frozen closure_gate, then verifies evaluation_v2's
completion marker and output hashes before opening final results or row tables.
The preserved v1 scalar-interface failure remains in the provenance record.
No real-data/reference file is opened. Embedded reference fields in completed
evaluation JSON/CSV are ignored. This additive script is not a frozen control.

Numerical tolerance fixed before output inspection: atol=1e-10, rtol=1e-9.
ENSANUT inverse-CDF quantiles must match exactly (the same observed value).
These are rounding tolerances, not biomedical accuracy/equivalence criteria.
"""
from __future__ import annotations
import bisect
import csv
import hashlib
import itertools
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import scipy
from scipy import linalg, stats
import runner

ROOT = Path(__file__).resolve().parent
FIELDS = ("age", "female", "bmi", "glucose", "hba1c")
ATOL, RTOL = 1e-10, 1e-9
CORRECTION_SHA = "4965fbe9bc15c4f18122f5ac393a1d52cb3f892448adb66f5466fa0ef2b24f9d"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    with Path(path).open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")


def unavailable(contract, reason):
    return {row["id"]: {"status": "unavailable", "value": None, "reason": reason}
            for category in ("analyses", "diagnostics") for row in contract[category]}


def computed(value):
    value = float(value)
    require(math.isfinite(value), "Nonfinite independent endpoint")
    return {"status": "computed", "value": value, "reason": None}


class RankUnavailable(ValueError):
    pass


def qr_fit(columns, outcome):
    """Independent pivoted QR solution with the declared SVD rank threshold.

    ENSANUT has exactly 375 rows in each of eight cells, so all weights are
    1/3000. Common positive weight scaling leaves coefficients/rank/RMS
    unchanged; ordinary QR is therefore the same specified WLS estimand.
    """
    x = np.column_stack((np.ones(len(outcome)), *columns))
    singular = linalg.svdvals(x)
    cutoff = max(x.shape) * np.finfo(float).eps * singular[0]
    rank = int(np.count_nonzero(singular > cutoff))
    if len(outcome) <= x.shape[1] or rank != x.shape[1]:
        raise RankUnavailable("rank_or_residual_df_failure")
    q, r, permutation = linalg.qr(x, mode="economic", pivoting=True)
    beta = np.empty(x.shape[1])
    beta[permutation] = linalg.solve_triangular(r, q.T @ outcome)
    require(np.isfinite(beta).all(), "Nonfinite independent QR solution")
    residual = outcome - x @ beta
    rms = math.sqrt(math.fsum(float(v) ** 2 for v in residual) / len(outcome))
    return beta, rms


def linear_quantile(ordered, probability):
    position = (len(ordered) - 1) * probability
    low = math.floor(position)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (position - low) * (ordered[high] - ordered[low])


def equal_mass_quantile_indices(n):
    """Inverse CDF on original row masses, no interpolation/tie aggregation.

    math.fsum independently supplies correctly rounded equal-mass prefixes,
    rather than importing the engine's Neumaier implementation. The final
    cumulative total normalizes q; no epsilon or ceil(q*n) shortcut is used.
    """
    mass = 1.0 / n
    cumulative = [math.fsum(itertools.repeat(mass, k)) for k in range(1, n + 1)]
    return [min(bisect.bisect_left(cumulative, q * cumulative[-1]), n - 1)
            for q in (0.1, 0.5, 0.9)]


def load_table(path, task, case):
    """Read one successful generated CSV; never filter, impute or deduplicate."""
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        header, rows = next(reader), list(reader)
    expected = [item["name"] for item in task["columns"]]
    require(len(header) == len(set(header)) and set(header) == set(expected), "Wrong CSV columns")
    require(len(rows) == task["n_rows"] == 3000, "Wrong row count")
    require(all(len(row) == len(header) for row in rows), "Ragged CSV")
    positions = {name: header.index(name) for name in header}
    identifiers = [row[positions[task["row_id"]]] for row in rows]
    require(all(s.strip() for s in identifiers), "Missing row identity")
    require(len(set(identifiers)) == len(rows), "Duplicate row identity")
    values = np.asarray([[float(row[positions[name]]) for name in FIELDS] for row in rows])
    require(np.isfinite(values).all(), "Nonfinite/missing scientific value")
    definitions = {item["name"]: item for item in task["columns"]}
    for i, name in enumerate(FIELDS):
        entry, column = definitions[name], values[:, i]
        if entry["kind"] == "integer":
            require((column == np.floor(column)).all(), "Noninteger " + name)
        if "minimum" in entry:
            require((column >= entry["minimum"]).all(), "Below task minimum: " + name)
        if "maximum" in entry:
            require((column <= entry["maximum"]).all(), "Above task maximum: " + name)
    require(np.isin(values[:, 1], (0, 1)).all(), "Invalid sex category")
    validation = {"n": len(rows), "unique_row_ids": len(set(identifiers)),
                  "finite_all_fields": True, "task_valid": True,
                  "duplicate_measurement_rows": len(rows) - len(set(map(tuple, values)))}
    if case == "ENSANUT2018":
        counts = [int(np.count_nonzero((values[:, 0] >= low) & (values[:, 0] < high) &
                                      (values[:, 1] == sex)))
                  for low, high in ((25, 40), (40, 55), (55, 70), (70, 80)) for sex in (0, 1)]
        require(counts == [375] * 8, "Wrong ENSANUT cell allocation")
        require((values[:, 2:] > 0).all() and (values[:, 3] < 126).all(), "Invalid ENSANUT bounds")
        validation["demographic_cell_counts"] = counts
    return values, validation


def calculate(values, case, contract):
    result = unavailable(contract, "not_computed")
    age, female, bmi, glucose, hba1c = values.T
    if case == "CHNS2009":
        if (glucose <= 0).any() or (hba1c <= 0).any():
            return unavailable(contract, "nonpositive_glycemia_interpretation_required")
        # Prospective formula order differs from the provider's internal order.
        for identifier, columns in (("E1", (bmi, age, female)), ("E2", (glucose, age, female)),
                                    ("E3", (age, female, bmi, glucose))):
            try:
                beta, _ = qr_fit(columns, hba1c)
                result[identifier] = computed(beta[1])
            except RankUnavailable as exc:
                result[identifier]["reason"] = str(exc)
    else:
        age10, bmi5, glucose10 = (age - 50) / 10, (bmi - 25) / 5, (glucose - 100) / 10
        try:
            full, rms = qr_fit((age10, female, bmi5, glucose10), hba1c)
            reduced, _ = qr_fit((age10, female, bmi5), hba1c)
            secondary, _ = qr_fit((age10, female, glucose10), hba1c)
        except RankUnavailable as exc:
            # ENSANUT withholds the whole payload if any mandatory model fails.
            return unavailable(contract, "singular_design: " + str(exc))
        for identifier, value in (("Q1_age10", full[1]), ("Q2_bmi5", reduced[3]),
                                  ("Q3_bmi5", full[3]), ("Q2_minus_Q3_bmi5", reduced[3] - full[3]),
                                  ("glucose10_age_sex", secondary[3]), ("q1_residual_rms", rms)):
            result[identifier] = computed(value)
    quantile_indices = equal_mass_quantile_indices(len(values)) if case == "ENSANUT2018" else None
    for i, name in enumerate(FIELDS):
        column = values[:, i]
        center = math.fsum(map(float, column)) / len(column)
        divisor = len(column) - 1 if case == "CHNS2009" else len(column)
        sd = math.sqrt(math.fsum((float(v) - center) ** 2 for v in column) / divisor)
        ordered = sorted(map(float, column))
        if case == "CHNS2009":
            entries = {"mean": center, "sd": sd, **dict(zip(("q10", "median", "q90"),
                       (linear_quantile(ordered, q) for q in (0.1, 0.5, 0.9))))}
            separator = "_"
        else:
            entries = {"mean": center, "sd_population": sd, **dict(zip(("q10", "q50", "q90"),
                       (ordered[k] for k in quantile_indices)))}
            separator = "."
        for statistic, value in entries.items():
            result[name + separator + statistic] = computed(value)
    if case == "CHNS2009":
        if (glucose == glucose[0]).all() or (hba1c == hba1c[0]).all():
            for kind in ("pearson", "spearman"):
                result["glucose_hba1c_" + kind]["reason"] = "constant_pair"
        else:
            result["glucose_hba1c_pearson"] = computed(stats.pearsonr(glucose, hba1c).statistic)
            result["glucose_hba1c_spearman"] = computed(stats.spearmanr(glucose, hba1c).statistic)
    return result


def compare(expected, observed, exact):
    if observed.get("status") not in ("computed", "unavailable"):
        return False, None, None, "invalid_evaluation_status"
    if expected["status"] != observed["status"]:
        return False, None, None, "availability_mismatch"
    if expected["status"] == "unavailable":
        return observed.get("value") is None, None, None, "both_unavailable"
    value = observed.get("value")
    if type(value) not in (int, float) or not math.isfinite(value):
        return False, None, None, "invalid_evaluation_value"
    difference = expected["value"] - value
    tolerance = 0.0 if exact else ATOL + RTOL * max(abs(expected["value"]), abs(value))
    return abs(difference) <= tolerance, difference, tolerance, "numeric_comparison"


def audit():
    closed = runner.closure_gate()  # FIRST operation; no row/result read above.
    evaluation = ROOT / "evaluation_v2"
    marker_path = evaluation / "EVALUATION_COMPLETED.json"
    require(marker_path.is_file(), "Corrected main evaluation must complete first")
    marker_hash, marker = sha(marker_path), read_json(marker_path)
    require(set(marker["outputs"]) == {"RESULTS.json", "ALL_ENDPOINTS.csv"}, "Unexpected completed outputs")
    for name, digest in marker["outputs"].items():
        require(sha(evaluation / name) == digest, "Completed output changed: " + name)
    require(sha(ROOT / "EVALUATOR_V2_CORRECTION.json") == CORRECTION_SHA, "Correction identity changed")
    correction = read_json(ROOT / "EVALUATOR_V2_CORRECTION.json")
    for artifact in correction["bindings"]:
        require(sha(artifact["path"]) == artifact["sha256"], "Correction binding changed")
    report = read_json(evaluation / "RESULTS.json")
    require(report.get("correction_manifest_sha256") == CORRECTION_SHA, "Not the reviewed corrected evaluation")
    protocol = read_json(ROOT / "PROTOCOL.json")
    contracts = read_json(ROOT / "ENDPOINT_CONTRACT.json")["cases"]
    destination = evaluation / "independent_numerical_audit"
    require(not destination.exists(), "Audit already reserved; no silent replacement")
    destination.mkdir()
    issues, inventory, slots, endpoints = [], [], [], []

    def check(condition, message):
        if not condition:
            issues.append(message)

    try:
        check(report["batch_closure_sha256"] == sha(ROOT / "BATCH_CLOSURE.json"), "Closure identity mismatch")
        check(report["protocol_sha256"] == sha(ROOT / "PROTOCOL.json"), "Protocol identity mismatch")
        planned = {(aid, seed) for aid in protocol["authors"] for seed in protocol["final_seeds"]}
        keys = [(s["author_id"], s["seed"]) for s in report["all_final_slots"]]
        check(len(planned) == len(keys) == 12 and set(keys) == planned, "Twelve unique planned slots required")
        main_slots = {(s["author_id"], s["seed"]): s for s in report["all_final_slots"]}
        main_authors = {a["author_id"]: a for a in report["authors"]}
        check(len(report["authors"]) == 4 and set(main_authors) == set(protocol["authors"]), "Author inventory mismatch")
        with (evaluation / "ALL_ENDPOINTS.csv").open(encoding="utf-8-sig", newline="") as handle:
            csv_rows = list(csv.DictReader(handle))
        csv_keys = [(r["author_id"], int(r["seed"]), r["category"], r["endpoint"]) for r in csv_rows]
        csv_lookup = dict(zip(csv_keys, csv_rows))
        check(len(csv_keys) == len(set(csv_keys)), "Duplicate CSV endpoint")
        endpoint_keys, table_hashes, attempt_keys = set(), set(), set()
        attempt_details = {}
        total_attempts = 0
        for aid, setting in protocol["authors"].items():
            bundle, session = Path(setting["bundle"]), ROOT / "sessions" / aid
            events = [read_json(p) for p in sorted((session / "events").glob("*.json"))]
            bykind = lambda kind: [e for e in events if e["kind"] == kind]
            attempts, results, freezes, decisions, terminal = (bykind(k) for k in ("attempt", "result", "freeze", "decision", "closed"))
            trials = [a for a in attempts if a["purpose"] == "trial"]
            finals = [a for a in attempts if a["purpose"] == "final"]
            total_attempts += len(attempts)
            attempt_keys.update((aid, a["run_id"]) for a in attempts)
            for attempt in attempts:
                result = next((r for r in results if r["attempt_index"] == attempt["index"]), {})
                attempt_details[(aid, attempt["run_id"])] = {
                    **{k: attempt[k] for k in ("purpose", "stage", "seed")},
                    **{k: result.get(k) for k in ("status", "output_route", "seed_role")}}
            check(len(terminal) == 1 and events[-1]["kind"] == "closed", aid + ": not terminal")
            check(len(attempts) <= 5 and len(trials) <= 2 and len(freezes) <= 2 and len(decisions) <= 1, aid + ": budget exceeded")
            check(len({(a["purpose"], a["seed"]) for a in attempts}) == len(attempts), aid + ": repeated slot")
            check(len(results) == len(attempts) and {r["attempt_index"] for r in results} == {a["index"] for a in attempts},
                  aid + ": unresolved/duplicate result")
            for trial in trials:
                check(trial["seed"] == protocol["trial_seeds"].get(trial["stage"]), aid + ": unscheduled trial")
            if decisions:
                decision = decisions[0]
                for stage in ("initial", "revision"):
                    if stage == "initial" or any(f["stage"] == stage for f in freezes):
                        matching = [t for t in trials if t["stage"] == stage]
                        check(len(matching) == 1, aid + ": missing " + stage + " trial")
                        for t in matching:
                            result = [r for r in results if r["attempt_index"] == t["index"]]
                            check(len(result) == 1 and result[0]["index"] < decision["index"], aid + ": decision before trial resolution")
                selected = [f for f in freezes if f["candidate"] == decision["candidate"]]
                check(len(selected) == 1, aid + ": decision candidate not frozen")
                if selected:
                    check(decision["action"] == ("revise" if selected[0]["stage"] == "revision" else "retain"), aid + ": wrong decision action")
                decision_doc = read_json(decision["decision"]["path"])
                feedback = {f["run_id"]: f["feedback"]["sha256"] for f in bykind("feedback")}
                check(decision_doc["feedback_hashes"] == feedback, aid + ": decision feedback binding mismatch")
            else:
                check(not finals and terminal[0]["status"] == "construction_failed", aid + ": workflow without decision")
            for final in finals:
                check(final["seed"] in protocol["final_seeds"], aid + ": unscheduled final")
                check(bool(decisions) and final["index"] > decisions[0]["index"] and final["candidate"] == decisions[0]["candidate"],
                      aid + ": final before decision/from wrong candidate")
            registry = read_json(bundle / "registry.json")["artifacts"]
            originals = sorted({r["source_id"] for r in registry if not r["source_id"].startswith("search-")})
            usage = read_json(bundle / "gateway/session/state.json")["usage"]
            inputs, main_author = read_json(session / "inputs.json"), main_authors.get(aid, {})
            check(len(originals) <= 4 and usage["queries"] <= 8 and usage["downloads"] <= 4, aid + ": source budget exceeded")
            check(originals == inputs["original_source_ids"] == sorted(main_author.get("source_ids", [])), aid + ": source inventory mismatch")
            check(usage == main_author.get("gateway_usage"), aid + ": acquisition accounting mismatch")
            check(main_author.get("decision") == (decisions[0]["action"] if decisions else None), aid + ": reported decision mismatch")
            check(main_author.get("terminal_status") == terminal[0]["status"], aid + ": reported closure mismatch")
            expected_freezes = [{k: f[k] for k in ("candidate", "stage", "freeze_sha256")} for f in freezes]
            check(main_author.get("initial_and_revision_freezes") == expected_freezes, aid + ": reported freezes mismatch")
            inventory.append({"author_id": aid, "case_id": setting["case_id"], "source_ids": originals,
                "original_source_count": len(originals), "registered_artifacts": len(registry),
                "query_credits": usage["queries"], "downloads": usage["downloads"],
                "acquisition_manifest_sha256": sha(session / "inputs.json"), "search_ledger_sha256": sha(bundle / "SEARCH_LEDGER.json"),
                "physical_attempts": len(attempts), "trials": len(trials), "finals": len(finals), "freezes": len(freezes),
                "decision": decisions[0]["action"] if decisions else None, "terminal_status": terminal[0]["status"]})
            task, case = read_json(bundle / "task.json"), setting["case_id"]
            check(sha(bundle / "task.json") == setting["task_sha256"], aid + ": task identity changed")
            contract = contracts[case]
            check(len(contract["analyses"]) == 3 and len(contract["diagnostics"]) == (27 if case == "CHNS2009" else 28), aid + ": endpoint count")
            for seed in protocol["final_seeds"]:
                label, main = aid + "/" + str(seed), main_slots.get((aid, seed), {})
                attempted = [a for a in finals if a["seed"] == seed]
                check(len(attempted) <= 1, label + ": duplicate final")
                outcome = next((r for r in results if attempted and r["attempt_index"] == attempted[0]["index"]), None)
                status = outcome["status"] if outcome else "not_attempted"
                check(main.get("case_id") == case and main.get("scheduled") is True, label + ": slot metadata")
                check(main.get("execution_status") == status, label + ": execution status")
                check(main.get("run_id") == (attempted[0]["run_id"] if attempted else None), label + ": run identity")
                check(main.get("candidate") == (attempted[0]["candidate"] if attempted else None), label + ": candidate")
                independent, validation, digest = unavailable(contract, "Execution " + status), None, None
                if outcome:
                    for key in ("output_route", "seed_role"):
                        check(main.get(key) == outcome.get(key), label + ": " + key)
                    if status != "success":
                        check(main.get("error") == outcome.get("error"), label + ": failure detail not retained")
                if status == "success":
                    try:
                        require(outcome.get("table") is not None, "Successful execution lacks verified table")
                        path = bundle / "executions" / attempted[0]["run_id"] / "output/generated.csv"
                        require(Path(outcome["table"]["path"]).resolve() == path.resolve(), "Wrong table path")
                        digest = sha(path)
                        require(digest == outcome["table"]["sha256"], "Changed table")
                        check(main.get("table_sha256") == digest, label + ": evaluation table identity")
                        values, validation = load_table(path, task, case)
                        independent = calculate(values, case, contract)
                        table_hashes.add(digest)
                    except Exception as exc:
                        issues.append(label + ": independent calculation failure: " + type(exc).__name__ + ": " + str(exc))
                        independent = unavailable(contract, "Independent audit failure: " + type(exc).__name__ + ": " + str(exc))
                else:
                    check(main.get("table_sha256") is None, label + ": failed/unattempted table claimed valid")
                expected_analysis_status = ("unavailable" if status != "success" or main.get("error")
                    else "complete" if all(r["status"] == "computed" for r in independent.values()) else "incomplete")
                check(main.get("analysis_status") == expected_analysis_status, label + ": analysis status inconsistent with payload")
                slot_rows = []
                for category in ("analyses", "diagnostics"):
                    expected, observed = contract[category], main.get(category, [])
                    check(len(observed) == len(expected) and {r["id"] for r in observed} == {r["id"] for r in expected},
                          label + ": incomplete/duplicate " + category)
                    lookup = {r["id"]: r for r in observed}
                    for spec in expected:
                        key = (aid, seed, category, spec["id"])
                        endpoint_keys.add(key)
                        observed_row = lookup.get(spec["id"], {})
                        check(observed_row.get("unit") == spec["unit"], label + "/" + spec["id"] + ": unit mismatch")
                        exact = case == "ENSANUT2018" and spec["id"].endswith((".q10", ".q50", ".q90"))
                        matched, difference, tolerance, kind = compare(independent[spec["id"]], observed_row, exact)
                        check(matched, label + "/" + spec["id"] + ": " + kind)
                        csv_row = csv_lookup.get(key, {})
                        check(csv_row.get("case_id") == case and csv_row.get("unit") == spec["unit"] and csv_row.get("execution_status") == status,
                              label + "/" + spec["id"] + ": CSV metadata mismatch")
                        literal = csv_row.get("generated_value", "")
                        csv_value = float(literal) if literal else None
                        check(csv_value == observed_row.get("value"), label + "/" + spec["id"] + ": CSV/JSON generated value mismatch")
                        item = {"author_id": aid, "case_id": case, "seed": seed, "category": category, "endpoint": spec["id"],
                            "unit": spec["unit"], "execution_status": status, "evaluation_status": observed_row.get("status"),
                            "evaluation_generated_value": observed_row.get("value"), "independent_status": independent[spec["id"]]["status"],
                            "independent_value": independent[spec["id"]]["value"], "independent_reason": independent[spec["id"]]["reason"],
                            "evaluation_reason": observed_row.get("reason"), "difference": difference, "tolerance": tolerance,
                            "comparison": kind, "matches": matched,
                            "evaluation_comparison_status": observed_row.get("comparison_status")}
                        endpoints.append(item)
                        slot_rows.append(item)
                slots.append({"author_id": aid, "case_id": case, "seed": seed, "run_id": main.get("run_id"),
                    "execution_status": status, "execution_error": outcome.get("error") if outcome else None,
                    "evaluation_analysis_status": main.get("analysis_status"), "evaluation_error": main.get("error"),
                    "output_route": main.get("output_route"), "seed_role": main.get("seed_role"), "table_sha256": digest,
                    "row_validation": validation, "computed_endpoints": sum(r["independent_status"] == "computed" for r in slot_rows),
                    "unavailable_endpoints": sum(r["independent_status"] == "unavailable" for r in slot_rows),
                    "endpoint_mismatches": sum(not r["matches"] for r in slot_rows)})
        check(len(endpoint_keys) == len(endpoints) == 366, "Expected 366 endpoints")
        check(set(csv_keys) == endpoint_keys and len(csv_keys) == 366, "CSV endpoint inventory mismatch")
        check(total_attempts == closed["physical_attempts"] == report["physical_attempts"] and total_attempts <= 20,
              "Charged execution count mismatch")
        cost_keys = [(r["author_id"], r["run_id"]) for r in report["all_attempt_cost_records"]]
        check(len(cost_keys) == len(attempt_keys) and set(cost_keys) == attempt_keys, "Attempt cost inventory mismatch")
        for cost in report["all_attempt_cost_records"]:
            expected = attempt_details.get((cost["author_id"], cost["run_id"]), {})
            check(all(cost.get(k) == v for k, v in expected.items()),
                  cost["author_id"] + "/" + cost["run_id"] + ": cost metadata mismatch")
        summaries = report["all_author_endpoint_summaries"]
        summary_keys = [(s["author_id"], s["endpoint"]) for s in summaries]
        expected_summaries = {(aid, spec["id"]) for aid, setting in protocol["authors"].items()
                              for spec in contracts[setting["case_id"]]["analyses"]}
        check(len(summary_keys) == 12 and set(summary_keys) == expected_summaries, "Generated summary inventory mismatch")
        for summary in summaries:
            aid, identifier = summary["author_id"], summary["endpoint"]
            rows = [r for r in endpoints if r["author_id"] == aid and r["category"] == "analyses" and r["endpoint"] == identifier]
            # The summary's inclusion convention is comparison availability,
            # which can differ from generated availability if a reference is
            # unavailable. Inspect that status only, never reference values.
            good = [r["independent_value"] for r in rows if r["evaluation_comparison_status"] == "computed"
                    and r["independent_status"] == "computed"]
            expected_mean = math.fsum(good) / len(good) if good else None
            expected_range = [min(good), max(good)] if good else None
            same_number = lambda x, y: x is None and y is None or (
                type(x) in (int, float) and type(y) in (int, float) and
                math.isclose(x, y, abs_tol=ATOL, rel_tol=RTOL))
            check(summary["available_slots"] == len(good) and summary["scheduled_slots"] == 3,
                  aid + "/" + identifier + ": summary counts")
            check(same_number(summary["slot_mean"], expected_mean), aid + "/" + identifier + ": generated summary mean")
            observed_range = summary["slot_range"]
            check((observed_range is None and expected_range is None) or
                  (isinstance(observed_range, list) and len(observed_range) == 2 and expected_range is not None and
                   all(same_number(x, y) for x, y in zip(observed_range, expected_range))),
                  aid + "/" + identifier + ": generated summary range")
            author_slots = [s for s in slots if s["author_id"] == aid]
            check(summary["output_routes"] == sorted({s["output_route"] for s in author_slots if s["output_route"]}),
                  aid + "/" + identifier + ": summary routes")
            check(summary["unique_validated_table_hashes"] == len({s["table_sha256"] for s in author_slots if s["table_sha256"]}),
                  aid + "/" + identifier + ": summary unique tables")
        check(report["successful_final_executions"] == sum(s["execution_status"] == "success" for s in slots), "Successful slot count")
        check(report["unique_final_table_hashes"] == len(table_hashes), "Unique table count")
        check(report["scheduled_final_slots"] == 12 and report["scheduled_authors"] == 4, "Schedule totals")
        runner.closure_gate()
        require(sha(marker_path) == marker_hash, "Completion marker changed during audit")
        for name, digest in marker["outputs"].items():
            require(sha(evaluation / name) == digest, "Evaluation changed during audit")
        output = {"schema_version": "core_workflow_independent_numerical_audit_v1", "status": "PASS" if not issues else "FAIL",
            "created_utc": datetime.now(timezone.utc).isoformat(), "audit_script_sha256": sha(__file__),
            "control_sha256": sha(ROOT / "CONTROL.json"), "batch_closure_sha256": sha(ROOT / "BATCH_CLOSURE.json"),
            "evaluation_directory": "evaluation_v2", "evaluation_completion_sha256": marker_hash, "evaluation_outputs": marker["outputs"],
            "correction_manifest_sha256": CORRECTION_SHA,
            "preserved_v1_failure": {"diagnosis_sha256": sha(ROOT / "EVALUATOR_V1_BUG_DIAGNOSIS.json"),
                "description": "Finite NumPy scalar quantiles rejected by v1 exact Python type guard; CHNS payloads unavailable. No regeneration."},
            "runtime": {"numpy": np.__version__, "scipy": scipy.__version__}, "absolute_tolerance": ATOL, "relative_tolerance": RTOL,
            "ensanut_inverse_cdf_quantiles": "exact observed-value equality", "reference_files_opened": False,
            "new_generations_or_real_data_fits": False, "provider_or_engine_functions_called": False, "author_inventory": inventory,
            "planned_final_slots": len(planned), "physical_attempts": total_attempts, "unique_validated_table_hashes": len(table_hashes),
            "scheduled_endpoints": len(endpoints), "computed_endpoint_comparisons": sum(r["comparison"] == "numeric_comparison" for r in endpoints),
            "both_unavailable_endpoint_comparisons": sum(r["comparison"] == "both_unavailable" for r in endpoints),
            "endpoint_mismatches": sum(not r["matches"] for r in endpoints), "issues": issues,
            "all_final_slots": slots, "all_endpoint_comparisons": endpoints,
            "interpretation": "Numerical/accounting agreement only; not clinical validity, source-transport validation, seed-independence certification or reference accuracy."}
        write_json(destination / "RESULTS.json", output)
        write_json(destination / "AUDIT_COMPLETED.json", {"status": output["status"], "outputs": {"RESULTS.json": sha(destination / "RESULTS.json")}})
        return {key: output[key] for key in ("status", "planned_final_slots", "physical_attempts", "scheduled_endpoints",
                "computed_endpoint_comparisons", "both_unavailable_endpoint_comparisons", "endpoint_mismatches", "issues")}
    except Exception as exc:
        write_json(destination / "AUDIT_FAILURE.json", {"type": type(exc).__name__, "message": str(exc), "no_silent_retry": True})
        raise


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, allow_nan=False))
