"""Independent CHNS R30 evaluator; no generation, calibration, or patient reads.

Import, --help and --self-test do not open experiment data. A run reads up to
three explicit final synthetic CSVs and two immutable aggregate JSON artifacts.
Seed names identify declared slots, not proof of the generator's RNG execution.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
import statistics
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import linalg, stats

SEEDS = (4101, 4102, 4103)
VARIABLES = ("age", "female", "bmi", "glucose", "hba1c")
MARGINALS = ("mean", "sd", "q10", "median", "q90")
ANALYSES = {
    "E1": (("age", "female", "bmi"), "bmi", "%/(kg/m^2)"),
    "E2": (("age", "female", "glucose"), "glucose", "%/(mmol/L)"),
    "E3": (("female", "bmi", "glucose", "age"), "age", "%/year"),
}
METRICS = tuple(ANALYSES) + tuple(v + "_" + s for v in VARIABLES for s in MARGINALS) + (
    "glucose_hba1c_pearson", "glucose_hba1c_spearman")
REFERENCE_SHA256 = "7cda7cb9a3a1b337b92bc6f6664366fede1cd50dd1da9d255d20c346d5d25b02"
HISTORICAL_SHA256 = "d64b7cd5bd1097a4ea51b84b00a3721d54c092cc87db85da9418bdd24bd187a0"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def close(a, b):
    return finite(a) and finite(b) and math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-10)


def bound_json(path, expected):
    payload = Path(path).read_bytes()
    require(digest(payload) == expected, "Aggregate artifact hash mismatch: " + str(path))
    return json.loads(payload.decode("utf-8-sig"))


def linear_quantile(values, probability):
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    fraction = position - lower
    return ordered[lower] + fraction * (ordered[min(lower + 1, len(ordered) - 1)] - ordered[lower])


def centered_qr(x, y):
    """Pivoted QR solves centered slopes; intercept is implicit and unpenalized."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    slopes, _, rank, _ = linalg.lstsq(x - x.mean(axis=0), y - y.mean(), lapack_driver="gelsy")
    return slopes, int(rank) + 1


def parse_csv(payload, expected_rows=3000):
    reader = csv.DictReader(io.StringIO(payload.decode("utf-8-sig"), newline=""))
    headers = reader.fieldnames or []
    require(len(headers) == len(set(headers)), "Duplicate CSV headers")
    require(set(VARIABLES).issubset(headers), "Missing required measured column")
    require(set(headers).issubset(set(VARIABLES) | {"row_id"}), "Unexpected CSV column")
    raw = list(reader)
    require(len(raw) == expected_rows, f"Expected {expected_rows} rows, received {len(raw)}")
    require(all(None not in row and all(row[v] is not None for v in VARIABLES) for row in raw),
            "Ragged CSV row")
    columns = {v: [float(row[v]) for row in raw] for v in VARIABLES}
    require(all(math.isfinite(x) for xs in columns.values() for x in xs), "Nonfinite measurement")
    violations = {
        "age_outside_35_74_or_noninteger": sum(x < 35 or x > 74 or x != int(x) for x in columns["age"]),
        "nonbinary_female": sum(x not in (0, 1) for x in columns["female"]),
        **{"nonpositive_" + v: sum(x <= 0 for x in columns[v]) for v in ("bmi", "glucose", "hba1c")},
    }
    if "row_id" in headers:
        ids = [row["row_id"] for row in raw]
        violations["invalid_or_duplicate_row_id"] = sum(x is None or x.strip() == "" for x in ids) + len(ids) - len(set(ids))
    quality = {"n": len(raw), "support_violations": violations,
               "duplicate_measurement_rows": len(raw) - len(set(zip(*(columns[v] for v in VARIABLES))))}
    return columns, quality


def calculate(columns):
    values, ranks, reasons = {}, {}, {}
    for variable, xs in columns.items():
        values.update({variable + "_mean": statistics.mean(xs), variable + "_sd": statistics.stdev(xs),
                       variable + "_q10": linear_quantile(xs, .1), variable + "_median": statistics.median(xs),
                       variable + "_q90": linear_quantile(xs, .9)})
    glucose, hba1c = columns["glucose"], columns["hba1c"]
    constant_joint = len(set(glucose)) < 2 or len(set(hba1c)) < 2
    for name, function in (("pearson", stats.pearsonr), ("spearman", stats.spearmanr)):
        key = "glucose_hba1c_" + name
        value = None if constant_joint else float(function(glucose, hba1c).statistic)
        values[key] = value if finite(value) else None
        if values[key] is None:
            reasons[key] = "Constant joint variable or unavailable correlation"
    for key, (predictors, focal, _) in ANALYSES.items():
        x = np.column_stack([columns[v] for v in predictors])
        slopes, rank = centered_qr(x, columns["hba1c"])
        ranks[key] = rank
        value = float(slopes[predictors.index(focal)])
        values[key] = value if rank == len(predictors) + 1 and finite(value) else None
        if values[key] is None:
            reasons[key] = "Rank-deficient design or nonfinite QR coefficient"
    require(set(values) == set(METRICS), "Internal metric coverage mismatch")
    return values, ranks, reasons


def reference_values(reference):
    require(reference.get("n") == 6631, "Unexpected CHNS reference population size")
    values = {key: reference["estimands"][key]["coefficient"] for key in ANALYSES}
    for variable in VARIABLES:
        for statistic in MARGINALS:
            values[variable + "_" + statistic] = reference["diagnostics"]["marginal"][variable][statistic]
    values.update({"glucose_hba1c_" + s: reference["diagnostics"]["joint"][s] for s in ("pearson", "spearman")})
    require(all(finite(v) for v in values.values()), "Unavailable reference metric")
    return values


def discover_csvs(directory):
    directory = Path(directory).resolve()
    require(directory.is_dir(), "Final CSV directory not found")
    files = sorted(p for p in directory.rglob("*") if p.is_file() and p.suffix.lower() == ".csv")
    require(len(files) == 3, "Input directory must contain exactly three CSV files")
    mapped = {}
    for path in files:
        matches = re.findall(r"(?<!\d)(4101|4102|4103)(?!\d)", path.name)
        require(len(matches) == 1, "CSV basename must contain exactly one final seed: " + path.name)
        seed = int(matches[0])
        require(seed not in mapped, "Duplicate final seed slot")
        mapped[seed] = path
    require(set(mapped) == set(SEEDS), "Unexpected final seed allocation")
    return mapped


def validate_draw_closure(document, csv_files):
    """Validate the three declared slots against actual CSV names, without rows."""
    require(isinstance(document, dict) and isinstance(document.get("results"), list),
            "Draw closure must contain a results list")
    rows = document["results"]
    require(len(rows) == 3, "Draw closure must have exactly three final slots")
    require(all(isinstance(row, dict) and type(row.get("seed")) is int for row in rows),
            "Invalid closure seed record")
    require({row["seed"] for row in rows} == set(SEEDS), "Duplicate or unexpected closure seed")
    mapped = {}
    expected_names = set()
    for row in rows:
        require({"seed", "run_id", "status", "error", "receipt_sha256", "elapsed_seconds"}.issubset(row),
                "Draw closure record lacks required execution metadata")
        status = row.get("status")
        require(isinstance(status, str) and bool(status.strip()), "Missing draw status")
        receipt = row.get("receipt_sha256")
        require(receipt is None or (isinstance(receipt, str) and re.fullmatch(r"[0-9a-fA-F]{64}", receipt)),
                "Invalid declared receipt hash")
        elapsed = row.get("elapsed_seconds")
        require(elapsed is None or (finite(elapsed) and elapsed >= 0), "Invalid draw elapsed time")
        require(row.get("run_id") is None or isinstance(row["run_id"], str), "Invalid run identifier")
        if status == "success":
            require(receipt is not None and bool(row.get("run_id")), "Successful draw must identify its receipt and run")
            expected_names.add(f"final_{row['seed']}.csv")
        mapped[row["seed"]] = dict(row)
    require(set(csv_files) == expected_names,
            "Closure CSV inventory differs: successful slots need final_<seed>.csv; failed slots must have no CSV")
    return mapped


def load_draw_closure(path, directory, expected_sha256=None):
    payload = Path(path).read_bytes()
    actual_hash = digest(payload)
    if expected_sha256 is not None:
        require(actual_hash == expected_sha256.lower(), "Draw closure SHA256 mismatch")
    directory = Path(directory).resolve()
    require(not directory.exists() or directory.is_dir(), "Final CSV path is not a directory")
    # An entirely failed campaign need not have created a final-output directory.
    # The inventory validation below still rejects any success without its file.
    files = [p for p in directory.rglob("*") if p.is_file() and p.suffix.lower() == ".csv"] if directory.exists() else []
    require(all(p.parent == directory for p in files), "Closure mode requires CSVs directly in input directory")
    inventory = {p.name: p for p in files}
    require(len(inventory) == len(files), "Duplicate CSV names")
    slots = validate_draw_closure(json.loads(payload.decode("utf-8-sig")), inventory)
    metadata = {"path": str(Path(path).resolve()), "sha256": actual_hash,
                "expected_sha256": expected_sha256.lower() if expected_sha256 else None,
                "receipt_hash_role": "Declared in closure; receipt contents are verified separately by the release controller"}
    return slots, inventory, metadata


def unavailable_draw_record(slot):
    return {"constructor": "STAT_R30", "seed": slot["seed"], "file": None,
            "sha256": None, "bytes": None, "status": "unavailable",
            "values": {key: None for key in METRICS}, "quality": None, "ranks": {}, "reasons": {},
            "error": "Final draw did not succeed: " + slot["status"], "draw_closure_record": slot}


def evaluate_file(path, seed):
    payload = Path(path).read_bytes()
    record = {"constructor": "STAT_R30", "seed": seed, "file": str(Path(path).resolve()),
              "sha256": digest(payload), "bytes": len(payload), "status": "unavailable",
              "values": {key: None for key in METRICS}, "quality": None, "ranks": {}, "reasons": {}}
    try:
        columns, quality = parse_csv(payload)
        record["quality"] = quality
        require(not any(quality["support_violations"].values()), "Declared support/identifier violation")
        values, ranks, reasons = calculate(columns)
        record.update(values=values, ranks=ranks, reasons=reasons,
                      status="complete" if all(finite(v) for v in values.values()) else "incomplete")
    except (ValueError, TypeError, KeyError, OverflowError, UnicodeError, csv.Error, linalg.LinAlgError) as error:
        record["error"] = type(error).__name__ + ": " + str(error)
    return record


def load_historical(report, refs):
    require(report["reference_sha256"] == REFERENCE_SHA256, "Historical reference binding differs")
    selected = [r for r in report["runs"] if r["constructor"] in ("R01", "R02", "R03")
                and r["stage"] == "final" and r["purpose"] == "delivery"]
    require(len(selected) == 9, "Expected nine historical R final delivery records")
    records = []
    for constructor in ("R01", "R02", "R03"):
        rows = [r for r in selected if r["constructor"] == constructor]
        require(len(rows) == 3 and {r["seed"] for r in rows} == set(SEEDS), "Historical seed coverage mismatch")
        for row in rows:
            require(row["status"] == "success" and row["condition"] == "R", "Historical run state mismatch")
            items = row["statistics"]["analyses"] + row["statistics"]["diagnostics"]
            require(len(items) == 30 and {r["id"] for r in items} == set(METRICS), "Historical metric coverage mismatch")
            values = {}
            for item in items:
                key = item["id"]
                require(item["status"] == "computed" and item["n"] == 3000 and finite(item["value"]),
                        "Unavailable historical endpoint")
                require(close(item["reference"], refs[key]), "Historical endpoint reference mismatch")
                require(close(item["difference"], item["value"] - refs[key]), "Historical discrepancy mismatch")
                values[key] = item["value"]
                summary = [s for s in report["constructor_stage_statistics"] if s["constructor"] == constructor
                           and s["stage"] == "final" and s["id"] == key]
                require(len(summary) == 1 and close(summary[0]["seed_values"][str(row["seed"])], values[key]),
                        "Historical run/summary disagreement")
            records.append({"constructor": constructor, "seed": row["seed"], "status": "complete",
                            "run_id": row["run_id"], "output_sha256": row["output_sha256"], "values": values,
                            "historical_rows_reopened": False})
    return records


def summarize(records, refs):
    summaries = []
    for constructor in ("STAT_R30", "R01", "R02", "R03"):
        rows = [r for r in records if r["constructor"] == constructor]
        require(len(rows) == 3 and {r["seed"] for r in rows} == set(SEEDS), "Summary seed coverage mismatch")
        for key in METRICS:
            seed_values = {str(r["seed"]): r["values"][key] for r in sorted(rows, key=lambda r: r["seed"])}
            available = [v for v in seed_values.values() if finite(v)]
            complete = len(available) == 3
            effect = statistics.mean(available) if complete else None
            summaries.append({"constructor": constructor, "id": key, "reference": refs[key],
                              "seed_values": seed_values, "available_seeds": len(available),
                              "status": "complete" if complete else "incomplete",
                              "mean": effect, "seed_range": [min(available), max(available)] if complete else None,
                              "mean_signed_difference": effect - refs[key] if complete else None,
                              "absolute_difference_of_mean": abs(effect - refs[key]) if complete else None,
                              "mean_absolute_difference": statistics.mean(abs(v - refs[key]) for v in available) if complete else None})
    return summaries


def markdown(report):
    fmt = lambda x: "unavailable" if x is None else f"{x:.9g}"
    lines = ["# CHNS R30: independent descriptive calibration comparison", "",
             "This is a new statistical adaptation compared with retained historical Agent aggregates. Target summaries were supplied. It is not independent clinical validation or a matched-budget superiority experiment.", "",
             "All 30 metrics and all scheduled seeds are shown. No cross-metric score, winner, p-value, or equivalence conclusion is computed. Seed ranges measure sampling variation conditional on each law, not total inferential uncertainty.", "",
             "## Inputs and checks", "", f"Overall evaluation status: **{report['status']}**.", "",
             f"Reference SHA256: `{REFERENCE_SHA256}`.", f"Historical report SHA256: `{HISTORICAL_SHA256}`.", "",
             "| Final seed | Status | Rows | Support violations |", "|---|---|---:|---|"]
    for row in report["new_final_records"]:
        quality = row["quality"] or {}
        lines.append(f"| {row['seed']} | {row['status']} | {quality.get('n', 'unavailable')} | {quality.get('support_violations', row.get('error', 'unavailable'))} |")
    if report.get("draw_closure"):
        lines += ["", "Draw closure SHA256: `" + report["draw_closure"]["sha256"] + "`.",
                  "Failed closure slots have no fabricated CSV and remain unavailable; declared receipt hashes require separate controller verification."]
    lines += ["", "## Analysis definitions and reference intervals", "",
              "E1: HbA1c ~ age + female + BMI; BMI coefficient. E2: HbA1c ~ age + female + glucose; glucose coefficient. E3: HbA1c ~ female + BMI + glucose + age; age coefficient. All include an intercept and use unweighted OLS.", "",
              "Reference intervals are community-cluster CR1-t intervals for the previously exposed selected CHNS sample, not equivalence margins.", ""]
    for key, record in report["reference_intervals"].items():
        lines.append(f"- {key}: {fmt(record['lower'])} to {fmt(record['upper'])}; {ANALYSES[key][2]}.")
    lines += ["", "## Every metric and final seed", "",
              "Mean absolute difference is the mean of three seed-wise absolute differences, distinct from the absolute difference of the three-seed mean.", "",
              "| Metric | Constructor | Reference | Seed 4101 | Seed 4102 | Seed 4103 | Mean | Mean signed difference | Mean absolute difference | Absolute difference of mean |",
              "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for key in METRICS:
        for row in [s for s in report["constructor_metric_summaries"] if s["id"] == key]:
            values = [row["reference"]] + [row["seed_values"][str(s)] for s in SEEDS] + [row["mean"], row["mean_signed_difference"], row["mean_absolute_difference"], row["absolute_difference_of_mean"]]
            lines.append("| " + key + " | " + row["constructor"] + " | " + " | ".join(fmt(v) for v in values) + " |")
    lines += ["", "## Limits", ""] + ["- " + item for item in report["limits"]]
    return "\n".join(lines) + "\n"


def self_test():
    import unittest

    class ArithmeticTests(unittest.TestCase):
        def test_qr(self):
            x = np.array([[1, 1], [1, -1], [-1, 1], [-1, -1]], dtype=float)
            slopes, rank = centered_qr(x, 7 + x @ np.array([2., -3.]))
            np.testing.assert_allclose(slopes, [2., -3.], rtol=0, atol=1e-12)
            self.assertEqual(rank, 3)

        def test_rank_failure(self):
            _, rank = centered_qr(np.array([[1, 2], [2, 4], [3, 6.]]), np.array([1, 3, 2.]))
            self.assertEqual(rank, 2)

        def test_quantile_and_tied_ranks(self):
            self.assertAlmostEqual(linear_quantile([0., 10., 20., 30.], .1), 3.)
            self.assertAlmostEqual(statistics.stdev([1., 2., 3.]), 1.)
            self.assertAlmostEqual(float(stats.spearmanr([1, 1, 2, 3], [4, 4, 3, 1]).statistic), -1.)

        def test_support_and_nan(self):
            header = "age,female,bmi,glucose,hba1c\n"
            _, q = parse_csv((header + "35,0,20,5,6\n74,1,21,6,7\n").encode(), 2)
            self.assertFalse(any(q["support_violations"].values()))
            _, q = parse_csv((header + "34,2,0,5,6\n74,1,21,6,7\n").encode(), 2)
            self.assertEqual(sum(q["support_violations"].values()), 3)
            with self.assertRaises(ValueError):
                parse_csv((header + "35,0,20,nan,6\n74,1,21,6,7\n").encode(), 2)
            with self.assertRaises(ValueError):
                parse_csv((header + "35,0,20,5,6\n").encode(), 2)

        def test_no_survivor_mean(self):
            refs = {key: 1. for key in METRICS}
            records = [{"constructor": c, "seed": s, "values": dict(refs)}
                       for c in ("STAT_R30", "R01", "R02", "R03") for s in SEEDS]
            records[0]["values"]["E1"] = None
            result = summarize(records, refs)[0]
            self.assertEqual(result["available_seeds"], 2)
            self.assertIsNone(result["mean_absolute_difference"])

        def test_complete_metric_bundle(self):
            columns = {"age": [35., 40., 45., 50., 55., 60., 65., 70.],
                       "female": [0., 1., 1., 0., 0., 1., 0., 1.],
                       "bmi": [20., 22., 21., 27., 25., 24., 29., 26.],
                       "glucose": [4., 7., 5., 6., 4.5, 8., 6.5, 5.5]}
            columns["hba1c"] = [2 + .01*a + .2*f + .03*b + .4*g
                                 for a, f, b, g in zip(*(columns[v] for v in VARIABLES[:-1]))]
            values, ranks, reasons = calculate(columns)
            self.assertEqual(set(values), set(METRICS))
            self.assertTrue(all(finite(v) for v in values.values()))
            self.assertAlmostEqual(values["E3"], .01, places=11)
            self.assertEqual(ranks, {"E1": 4, "E2": 4, "E3": 5})
            self.assertFalse(reasons)

        def test_failed_draw_closure(self):
            slots = [{"seed": seed, "run_id": "run_" + str(seed),
                      "status": "success" if seed != 4102 else "failed",
                      "error": None if seed != 4102 else "invented failure",
                      "receipt_sha256": "a" * 64, "elapsed_seconds": .01} for seed in SEEDS]
            inventory = {"final_4101.csv": Path("final_4101.csv"),
                         "final_4103.csv": Path("final_4103.csv")}
            accepted = validate_draw_closure({"results": slots}, inventory)
            failed = unavailable_draw_record(accepted[4102])
            self.assertIsNone(failed["file"])
            self.assertTrue(all(value is None for value in failed["values"].values()))
            refs = {key: 1. for key in METRICS}
            records = [{"constructor": c, "seed": seed, "values": dict(refs)}
                       for c in ("STAT_R30", "R01", "R02", "R03") for seed in SEEDS]
            records[1] = failed
            summary = summarize(records, refs)[0]
            self.assertEqual(summary["available_seeds"], 2)
            self.assertIsNone(summary["mean"])
            self.assertIsNone(summary["mean_absolute_difference"])
            with self.assertRaises(ValueError):
                validate_draw_closure({"results": slots}, {**inventory, "final_4102.csv": Path("final_4102.csv")})
            with self.assertRaises(ValueError):
                validate_draw_closure({"results": slots}, {"final_4101.csv": Path("final_4101.csv")})

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ArithmeticTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return result.wasSuccessful()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path)
    parser.add_argument("--reference-summary", type=Path)
    parser.add_argument("--historical-results", type=Path)
    parser.add_argument("--output-prefix", type=Path)
    parser.add_argument("--draw-closure", type=Path, help="Three-slot closure manifest; retain failures without fabricated CSVs")
    parser.add_argument("--draw-closure-sha256", help="Optional expected hash of the exact draw-closure bytes")
    parser.add_argument("--fit-artifact", type=Path, help="Optional metadata file hash only; no fit parameters used in evaluation")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        raise SystemExit(0 if self_test() else 1)
    require(all((args.input_dir, args.reference_summary, args.historical_results, args.output_prefix)),
            "Evaluation requires --input-dir, --reference-summary, --historical-results and --output-prefix")
    output_json, output_md = args.output_prefix.with_suffix(".json"), args.output_prefix.with_suffix(".md")
    require(not output_json.exists() and not output_md.exists(), "Refusing to overwrite an evaluation")
    require(args.draw_closure is not None or args.draw_closure_sha256 is None,
            "--draw-closure-sha256 requires --draw-closure")
    closure_slots, closure_metadata = None, None
    if args.draw_closure:
        closure_slots, inventory, closure_metadata = load_draw_closure(
            args.draw_closure, args.input_dir, args.draw_closure_sha256)
        files = {seed: inventory[f"final_{seed}.csv"] for seed, row in closure_slots.items() if row["status"] == "success"}
    else:
        files = discover_csvs(args.input_dir)
    reference = bound_json(args.reference_summary, REFERENCE_SHA256)
    refs = reference_values(reference)
    history = bound_json(args.historical_results, HISTORICAL_SHA256)
    historical = load_historical(history, refs)
    final_records = []
    for seed in SEEDS:
        slot = closure_slots[seed] if closure_slots else None
        if slot is not None and slot["status"] != "success":
            record = unavailable_draw_record(slot)
        else:
            record = evaluate_file(files[seed], seed)
            if slot is not None:
                record["draw_closure_record"] = slot
        final_records.append(record)
    report = {
        "schema_version": "chns_r30_independent_evaluation_v1", "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "complete" if all(r["status"] == "complete" for r in final_records) else "incomplete",
        "script_sha256": digest(Path(__file__).read_bytes()), "reference_sha256": REFERENCE_SHA256,
        "historical_results_sha256": HISTORICAL_SHA256,
        "draw_closure": closure_metadata,
        "fit_artifact_sha256": digest(args.fit_artifact.read_bytes()) if args.fit_artifact else None,
        "fit_artifact_role": "Optional provenance binding only; no parameter fitted, imported, or used in statistical calculations",
        "method": "stdlib CSV, mean, sample SD (ddof=1), linear quantiles; SciPy Pearson/Spearman average ties; centered pivoted-QR OLS",
        "new_final_records": final_records, "historical_final_records": historical,
        "reference_values": refs,
        "reference_intervals": {key: reference["estimands"][key]["interval"] for key in ANALYSES},
        "constructor_metric_summaries": summarize(final_records + historical, refs),
        "original_patient_reads": 0, "historical_generated_row_reads": 0, "new_generation_or_fitting": 0,
        "limits": [
            "R30 target summaries were supplied for calibration; this is not a new independent clinical validation.",
            "One new fixed statistical construction versus three retained historical Agent constructions is descriptive, with unmatched historical search, feedback and effort budgets.",
            "The reference is an exposed selected CHNS sample, not known population truth; its intervals are not equivalence margins.",
            "Seed variation is conditional Monte Carlo variation, not source, completion, structural or transport uncertainty.",
            "CSV basenames declare seed slots. Execution receipts and the release manifest must separately bind RNG seeds, generator/specification and immutable output hashes.",
            "Historical rows were not reopened; historical aggregate values were hash-bound and cross-checked against their retained constructor summaries, not independently recalculated here.",
            "Finite rows and support checks do not certify finite theoretical moments of a generating law; mathematical model review remains separate.",
            "No global accuracy score, ranking, p-value, equivalence verdict, matched-cost claim or real-versus-real resampling is produced.",
        ],
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with output_json.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")
    with output_md.open("x", encoding="utf-8") as stream:
        stream.write(markdown(report))
    print(json.dumps({"status": report["status"], "scheduled_final_slots": len(final_records),
                      "final_csvs_read": sum(r["file"] is not None for r in final_records), "metrics_per_table": 30,
                      "historical_final_tables": len(historical), "json": str(output_json), "markdown": str(output_md)}))
    raise SystemExit(0 if report["status"] == "complete" else 2)


if __name__ == "__main__":
    main()
