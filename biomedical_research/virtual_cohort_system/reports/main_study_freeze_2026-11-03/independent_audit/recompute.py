"""Independent arithmetic for main-study generated tables, after global closure.

Does not import either case provider, the original clinical analysis engines or
the main evaluator. Original clinical-reference arithmetic has earlier audits;
here its frozen aggregate mapping is separately checked, not new patient data.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import numpy as np
import pandas as pd

UNIT = Path(__file__).resolve().parents[1]
PROJECT = UNIT.parents[1]
sys.path.insert(0, str(UNIT / "implementation"))
import main_session_v1 as control

VARIABLES = ["age", "female", "bmi", "glucose", "hba1c"]


def qr_fit(x, y, weights):
    sw = np.sqrt(weights)
    design = x * sw[:, None]
    if np.linalg.matrix_rank(design) != design.shape[1]:
        return None, None
    q, r = np.linalg.qr(design, mode="reduced")
    beta = np.linalg.solve(r, q.T @ (y * sw))
    residual = y - x @ beta
    return beta, float(np.sqrt(np.sum(weights * residual**2) / np.sum(weights)))


def inverse_weighted_quantile(values, weights, probability):
    order = np.argsort(values, kind="stable")
    index = np.searchsorted(np.cumsum(weights[order]) / weights.sum(), probability, side="left")
    return float(values[order[min(int(index), len(order)-1)]])


def calculate(frame, case, *, enforce_task=True):
    data = frame[VARIABLES].to_numpy(dtype=float)
    if not np.isfinite(data).all() or (enforce_task and len(data) != 3000):
        return None
    a, f, b, g, h = data.T
    if np.any((f != 0) & (f != 1)) or np.any(np.floor(a) != a) or np.any(data[:, 2:] <= 0):
        return None
    values = {}
    if case == "CHNS2009":
        if np.any(a < 35) or np.any(a > 74):
            return None
        designs = [("E1", [a, f, b], 3), ("E2", [a, f, g], 3), ("E3", [f, b, g, a], 4)]
        for ident, predictors, index in designs:
            beta, _ = qr_fit(np.column_stack([np.ones(len(a)), *predictors]), h, np.ones(len(a)))
            values[ident] = None if beta is None else float(beta[index])
        for name, column in zip(VARIABLES, data.T):
            for stat, value in {"mean": np.mean(column), "sd": np.std(column, ddof=1),
                                "q10": np.quantile(column, .1, method="linear"),
                                "median": np.quantile(column, .5, method="linear"),
                                "q90": np.quantile(column, .9, method="linear")}.items():
                values[name + "_" + stat] = float(value)
        for name, left, right in [("pearson", g, h), ("spearman", pd.Series(g).rank(method="average").to_numpy(), pd.Series(h).rank(method="average").to_numpy())]:
            left, right = left-left.mean(), right-right.mean()
            denominator = np.linalg.norm(left) * np.linalg.norm(right)
            values["glucose_hba1c_" + name] = float(left @ right / denominator) if denominator > 0 else None
    elif case == "ENSANUT2018":
        if np.any(a < 25) or np.any(a > 79) or np.any(g >= 126):
            return None
        bands = np.searchsorted([40, 55, 70], a, side="right")
        cell = 2 * bands + f.astype(int)
        counts = np.bincount(cell, minlength=8)
        if np.any(counts == 0) or (enforce_task and np.any(counts != 375)):
            return None
        weights = 1.0 / (8 * counts[cell])
        design = np.column_stack([np.ones(len(a)), (a-50)/10, f, (b-25)/5, (g-100)/10])
        full, rms = qr_fit(design, h, weights)
        reduced, _ = qr_fit(design[:, :4], h, weights)
        glucose, _ = qr_fit(design[:, [0, 1, 2, 4]], h, weights)
        if any(x is None for x in (full, reduced, glucose)):
            return None
        values.update(Q1_age10=float(full[1]), Q2_bmi5=float(reduced[3]), Q3_bmi5=float(full[3]),
                      Q2_minus_Q3_bmi5=float(reduced[3]-full[3]), glucose10_age_sex=float(glucose[3]), q1_residual_rms=rms)
        for name, column in zip(VARIABLES, data.T):
            avg = float(np.sum(weights*column) / weights.sum())
            values[name+".mean"] = avg
            values[name+".sd_population"] = float(np.sqrt(np.sum(weights*(column-avg)**2) / weights.sum()))
            for label, probability in (("q10", .1), ("q50", .5), ("q90", .9)):
                values[name+"."+label] = inverse_weighted_quantile(column, weights, probability)
    else:
        raise ValueError("Unknown case")
    return values


def close(a, b):
    if a is None or b is None:
        return a is None and b is None
    return bool(np.isclose(a, b, rtol=1e-9, atol=1e-9))


def lookup(document, keys):
    for key in keys:
        if not isinstance(document, dict) or key not in document:
            return None
        document = document[key]
    return document


def audit(release_path, result_path, output_path):
    release = control.READ(release_path)
    control.require_campaign_closed(release)  # Before result/reference/table access.
    manifest = control.READ(Path(__file__).with_name("CODE_COMMIT.json"))
    assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest() == manifest["recompute_sha256"]
    report = control.READ(result_path)
    assert report["release_sha256"] == control.SHA(release_path)
    binding_path = UNIT / "implementation/reference_bindings.json"
    assert control.SHA(binding_path) == report["reference_binding_sha256"]
    binding = control.READ(binding_path)
    errors, checks, numeric, max_difference = [], 0, 0, 0.0
    references = {}
    for case, spec in binding["cases"].items():
        path = PROJECT / spec["artifact"]["path"]
        assert control.SHA(path) == spec["artifact"]["sha256"]
        original = control.READ(path)
        references[case] = {}
        for category in ("analyses", "diagnostics"):
            for definition in spec[category]:
                ident = definition["id"]
                reference = lookup(original, definition["value_path"])
                references[case][ident] = reference
                checks += 1
                if not close(reference, report["references"][case][ident]["value"]):
                    errors.append({"case": case, "id": ident, "kind": "reference_mapping"})
    sessions = {x["id"]: control.Session(x["session_root"]) for x in release["constructions"]}
    slots = report["all_scheduled_slots"]
    assert len(slots) == 72 and len({(x["constructor_id"], x["seed"]) for x in slots}) == 72
    for slot in slots:
        actual = None
        if slot["execution_status"] == "success":
            path = sessions[slot["constructor_id"]].bundle / "executions" / slot["run_id"] / "output/generated.csv"
            assert control.SHA(path) == slot["output_sha256"]
            actual = calculate(pd.read_csv(path), slot["case_id"])
        for category in ("analyses", "diagnostics"):
            assert len(slot[category]) == len(binding["cases"][slot["case_id"]][category])
            for row in slot[category]:
                value = actual.get(row["id"]) if actual is not None else None
                expected_status = "computed" if value is not None else "unavailable"
                checks += 1
                if row["status"] != expected_status or not close(value, row["value"]):
                    errors.append({"constructor_id": slot["constructor_id"], "seed": slot["seed"], "id": row["id"], "kind": "generated_statistic", "independent": value, "primary": row["value"]})
                if value is not None and row["value"] is not None:
                    numeric += 1
                    max_difference = max(max_difference, abs(value-row["value"]))
                reference = references[slot["case_id"]][row["id"]]
                difference = value-reference if value is not None and reference is not None else None
                checks += 2
                if not close(difference, row["signed_discrepancy"]) or not close(abs(difference) if difference is not None else None, row["absolute_discrepancy"]):
                    errors.append({"constructor_id": slot["constructor_id"], "seed": slot["seed"], "id": row["id"], "kind": "discrepancy"})
    # Independent loop over the individual, already rechecked values; no main summarize import.
    for contrast in report["agent_information_contrasts"]:
        means, complete = {}, True
        for arm in ("E0", "E1"):
            members = [x for x in release["constructions"] if sessions[x["id"]].contract["case_id"] == contrast["case_id"] and sessions[x["id"]].contract["information_condition"] == arm and sessions[x["id"]].contract["constructor_kind"] == "agent"]
            constructor_means = []
            for member in members:
                rows = [next(e for e in x["analyses"] if e["id"] == contrast["endpoint"]) for x in slots if x["constructor_id"] == member["id"]]
                vals = [x["absolute_discrepancy"] for x in rows if x["absolute_discrepancy"] is not None]
                complete = complete and len(vals) == 3
                if len(vals) == 3:
                    constructor_means.append(sum(vals)/3)
            means[arm] = sum(constructor_means)/5 if len(constructor_means) == 5 else None
        expected = means["E1"]-means["E0"] if complete else None
        checks += 1
        if not close(expected, contrast["E1_minus_E0_mean_absolute_discrepancy"]) or contrast["complete_arm_comparison_available"] != complete:
            errors.append({"kind": "constructor_first_contrast", "case": contrast["case_id"], "id": contrast["endpoint"]})
    result = {"status": "matched" if not errors else "mismatch", "checks": checks,
              "numeric_statistics_compared": numeric, "maximum_numeric_difference": max_difference,
              "errors": errors, "generated_rows_regenerated": 0, "reference_raw_data_recomputed": False,
              "scope": "Independent QR/weighted arithmetic on retained generated outputs and independently mapped frozen reference aggregates; previous clinical reference audits remain separate.",
              "result_sha256": control.SHA(result_path), "audit_code_sha256": manifest["recompute_sha256"]}
    control.WRITE(Path(output_path), result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", required=True)
    parser.add_argument("--results", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    print(json.dumps(audit(args.release, args.results, args.output)))
