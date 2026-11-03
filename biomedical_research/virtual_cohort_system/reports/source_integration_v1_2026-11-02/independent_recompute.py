"""Independent, aggregate-only recomputation for the fixed source integration.

No harness, qualified-comparison, candidate, or generator code is imported.
The only data inputs are three explicit, locally retained generated-source CSVs
and the author's context_eligibility.json. No target input is accepted.

Usage (after the authorized source executions):
    python independent_recompute.py --j J.csv --b B.csv --m M.csv \
        --eligibility context_eligibility.json --output independent.json
Arithmetic-only verification (no files read or generated):
    python independent_recompute.py --self-test

Exit codes: 0 = complete and source eligibility/schema checks pass;
1 = report written with an unavailable operation or failed check;
2 = invalid invocation/declaration or output cannot be written.
The output must not already exist. No rows, individual values, fitted values,
or residuals are emitted. No input is modified and no rows are filtered.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import operator
from pathlib import Path
import sys

import numpy as np


COLUMNS = ("age", "female", "bmi", "glucose", "hba1c")
OUTPUT_COLUMNS = ("row_id",) + COLUMNS
SOURCE_IDS = ("J", "B", "M")
EXPECTED_ROWS = 1000
OPS = {"ge": operator.ge, "gt": operator.gt, "le": operator.le,
       "lt": operator.lt, "eq": operator.eq}
NGSP_SLOPE = 0.09148
NGSP_OFFSET = 2.152


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def ifcc_from_ngsp(values: np.ndarray) -> np.ndarray:
    return (values - NGSP_OFFSET) / NGSP_SLOPE


def average_ranks(values: np.ndarray) -> np.ndarray:
    """One-based average ranks; exact numeric equality defines a tie."""
    if not np.isfinite(values).all():
        raise ValueError("nonfinite_rank_input")
    ordered = sorted(range(len(values)), key=lambda index: values[index])
    ranks = np.empty(len(values), dtype=float)
    left = 0
    while left < len(ordered):
        right = left + 1
        while right < len(ordered) and values[ordered[right]] == values[ordered[left]]:
            right += 1
        mean_rank = ((left + 1) + right) / 2.0
        for position in range(left, right):
            ranks[ordered[position]] = mean_rank
        left = right
    return ranks


def pearson(x: np.ndarray, y: np.ndarray) -> float:
    """Centered normalized dot product, independent of correlation libraries."""
    if len(x) != len(y) or len(x) < 3:
        raise ValueError("fewer_than_three_pairs_or_unequal_lengths")
    if not (np.isfinite(x).all() and np.isfinite(y).all()):
        raise ValueError("nonfinite_required_columns")
    # Pre-scaling avoids unnecessary overflow; centering remains unweighted.
    x_scale = max(abs(float(value)) for value in x)
    y_scale = max(abs(float(value)) for value in y)
    if x_scale == 0.0 or y_scale == 0.0:
        raise ValueError("constant_required_column")
    xs = [float(value) / x_scale for value in x]
    ys = [float(value) / y_scale for value in y]
    x_mean = math.fsum(xs) / len(xs)
    y_mean = math.fsum(ys) / len(ys)
    xc = [value - x_mean for value in xs]
    yc = [value - y_mean for value in ys]
    xx = math.fsum(value * value for value in xc)
    yy = math.fsum(value * value for value in yc)
    if xx == 0.0 or yy == 0.0:
        raise ValueError("constant_required_column")
    result = math.fsum(a * b for a, b in zip(xc, yc)) / math.sqrt(xx * yy)
    if not math.isfinite(result):
        raise ValueError("nonfinite_correlation")
    return result


def solve_ols(predictors: np.ndarray, response: np.ndarray) -> tuple[np.ndarray, int]:
    """Separate equal-weight intercept-including projection via lstsq."""
    design = np.column_stack((np.ones(len(response)), predictors))
    if not (np.isfinite(design).all() and np.isfinite(response).all()):
        raise ValueError("nonfinite_required_columns")
    coefficients, _, rank, _ = np.linalg.lstsq(design, response, rcond=None)
    return coefficients, int(rank)


def predicate_counts(values: np.ndarray, op: str, value: float) -> dict:
    finite = np.isfinite(values)
    passed = finite & OPS[op](values, value)
    n = len(values)
    evaluated = int(finite.sum())
    n_passed = int(passed.sum())
    return {"n": n, "evaluated": evaluated, "passed": n_passed,
            "failed": evaluated - n_passed, "unevaluable": n - evaluated}


def load_eligibility(path: Path) -> tuple[dict, str]:
    payload = path.read_bytes()
    declaration = json.loads(payload.decode("utf-8-sig"))
    if not isinstance(declaration, dict) or declaration.get("schema_version") != 1:
        raise ValueError("eligibility_schema_version_must_be_1")
    contexts = declaration.get("contexts")
    if not isinstance(contexts, dict):
        raise ValueError("eligibility_contexts_must_be_an_object")
    for context_id in SOURCE_IDS:
        entry = contexts.get(context_id)
        if not isinstance(entry, dict):
            raise ValueError(f"missing_eligibility_context_{context_id}")
        conditions = entry.get("output_conditions")
        if not isinstance(conditions, list) or not conditions:
            raise ValueError(f"missing_output_conditions_{context_id}")
        for condition in conditions:
            if not isinstance(condition, dict) or set(condition) != {"column", "op", "value"}:
                raise ValueError(f"malformed_output_condition_{context_id}")
            if condition["column"] not in COLUMNS or condition["op"] not in OPS:
                raise ValueError(f"unsupported_output_condition_{context_id}")
            threshold = condition["value"]
            if (isinstance(threshold, bool) or not isinstance(threshold, (int, float))
                    or not math.isfinite(threshold)):
                raise ValueError(f"condition_threshold_must_be_finite_numeric_{context_id}")
        for key in ("unobserved_selection_assumptions", "notes"):
            if not isinstance(entry.get(key), list) or not all(
                    isinstance(item, str) for item in entry[key]):
                raise ValueError(f"invalid_{key}_{context_id}")
    return contexts, digest(payload)


def parse_source_csv(payload: bytes) -> tuple[dict[str, np.ndarray], dict]:
    """Parse the six-column task schema; identifiers never leave this function."""
    info = {}
    reader = csv.reader(io.StringIO(payload.decode("utf-8-sig"), newline=""), strict=True)
    header = next(reader, None)
    if (header is None or len(header) != len(OUTPUT_COLUMNS)
            or len(set(header)) != len(header) or set(header) != set(OUTPUT_COLUMNS)):
        raise ValueError("CSV_requires_exactly_row_id_age_female_bmi_glucose_hba1c_columns")
    positions = {column: header.index(column) for column in COLUMNS}
    row_id_position = header.index("row_id")
    values = {column: [] for column in COLUMNS}
    invalid_numeric = {column: 0 for column in COLUMNS}
    malformed_records = 0
    empty_row_ids = 0
    row_id_counts = {}
    for record in reader:
        # Keep one array position per CSV record, including malformed/blank rows.
        if len(record) != len(header):
            malformed_records += 1
        row_id = record[row_id_position] if row_id_position < len(record) else ""
        if not row_id.strip():
            empty_row_ids += 1
        else:
            # Preserve the exact identifier; do not trim, repair, or emit it.
            row_id_counts[row_id] = row_id_counts.get(row_id, 0) + 1
        for column in COLUMNS:
            index = positions[column]
            try:
                value = float(record[index]) if index < len(record) else float("nan")
            except (ValueError, OverflowError):
                value = float("nan")
            if not math.isfinite(value):
                invalid_numeric[column] += 1
            values[column].append(value)
    arrays = {column: np.asarray(value, dtype=float) for column, value in values.items()}
    n = len(arrays["age"])
    age = arrays["age"]
    female = arrays["female"]
    age_violations = int((~np.isfinite(age) | (age < 0) | (age != np.floor(age))).sum())
    female_violations = int((~np.isfinite(female) | ~np.isin(female, (0.0, 1.0))).sum())
    minimum_violations = {
        "bmi": int((np.isfinite(arrays["bmi"]) & (arrays["bmi"] < 5e-324)).sum()),
        "glucose": int((np.isfinite(arrays["glucose"]) & (arrays["glucose"] < 0)).sum()),
        "hba1c": int((np.isfinite(arrays["hba1c"]) & (arrays["hba1c"] < 0)).sum())}
    duplicate_records = sum(count for count in row_id_counts.values() if count > 1)
    duplicate_excess = sum(count - 1 for count in row_id_counts.values() if count > 1)
    info.update({"n_records": n, "expected_n": EXPECTED_ROWS,
                 "n_matches_schedule": n == EXPECTED_ROWS,
                 "malformed_record_count": malformed_records,
                 "empty_or_whitespace_row_id_count": empty_row_ids,
                 "distinct_nonempty_row_id_count": len(row_id_counts),
                 "duplicate_row_id_record_count": duplicate_records,
                 "duplicate_row_id_occurrences_after_first": duplicate_excess,
                 "invalid_or_nonfinite_count_by_column": invalid_numeric,
                 "age_nonnegative_integer_violation_count": age_violations,
                 "female_binary_violation_count": female_violations,
                 "finite_numeric_minimum_violation_count_by_column": minimum_violations,
                 "female_category_counts": {"0": int((female == 0).sum()),
                                            "1": int((female == 1).sum())},
                 "schema_pass": not (malformed_records or any(invalid_numeric.values())
                                      or age_violations or female_violations
                                      or any(minimum_violations.values())
                                      or empty_row_ids or duplicate_records)})
    return arrays, info


def read_source(path: Path) -> tuple[dict[str, np.ndarray], dict]:
    payload = path.read_bytes()
    arrays, info = parse_source_csv(payload)
    info.update({"path": str(path.resolve()), "sha256": digest(payload)})
    return arrays, info


def eligibility_report(arrays: dict, declaration: dict) -> dict:
    n = len(arrays["age"])
    all_pass = np.ones(n, dtype=bool)
    any_fail = np.zeros(n, dtype=bool)
    any_unknown = np.zeros(n, dtype=bool)
    reports = []
    for index, condition in enumerate(declaration["output_conditions"]):
        values = arrays[condition["column"]]
        finite = np.isfinite(values)
        passed = finite & OPS[condition["op"]](values, condition["value"])
        all_pass &= passed
        any_fail |= finite & ~passed
        any_unknown |= ~finite
        reports.append({"predicate_index": index, **condition,
                        **predicate_counts(values, condition["op"], condition["value"])})
    return {"status": "pass" if n > 0 and bool(all_pass.all()) else "fail",
            "n": n, "predicates": reports,
            "all_predicates_pass_count": int(all_pass.sum()),
            "any_predicate_failed_count": int(any_fail.sum()),
            "any_predicate_unevaluable_count": int(any_unknown.sum()),
            "not_all_predicates_pass_count": int((~all_pass).sum()),
            "counts_note": "Any-failed and any-unevaluable counts can overlap; no rows removed.",
            "unobserved_selection_assumptions_verified": False,
            "unobserved_selection_assumptions": declaration["unobserved_selection_assumptions"],
            "author_notes": declaration["notes"]}


def j_projection(arrays: dict, focal: str) -> dict:
    n = len(arrays["age"])
    native = "BMI" if focal == "bmi" else "FPG"
    result = {"statistic": "ols_coefficient", "n": n, "design_rank": None,
              "design_columns": ["intercept", "age", "gender_binary", native],
              "intercept": True, "focal_term": native, "coefficient": None,
              "unit": "mmol/mol/(kg/m^2)" if focal == "bmi" else "mmol/mol/(mmol/L)",
              "evidence_id": "R_JANSEN_BMI" if focal == "bmi" else "R_JANSEN_FPG",
              "status": "not_computable", "reasons": []}
    predictors = np.column_stack((arrays["age"], arrays["female"], arrays[focal]))
    response = ifcc_from_ngsp(arrays["hba1c"])
    if not np.isfinite(predictors).all():
        result["reasons"].append("nonfinite_required_predictors")
        return result
    # Compute rank even if the response is invalid; never select finite rows.
    design = np.column_stack((np.ones(n), predictors))
    try:
        _, _, rank, _ = np.linalg.lstsq(design, np.zeros(n), rcond=None)
        result["design_rank"] = int(rank)
    except np.linalg.LinAlgError:
        result["reasons"].append("design_rank_computation_failed")
        return result
    if n < 5:
        result["reasons"].append("fewer_than_five_rows")
    if result["design_rank"] != 4:
        result["reasons"].append("design_not_full_column_rank")
    if n - result["design_rank"] <= 0:
        result["reasons"].append("nonpositive_residual_degrees_of_freedom")
    female = arrays["female"]
    if not np.isin(female, (0.0, 1.0)).all() or set(female.tolist()) != {0.0, 1.0}:
        result["reasons"].append("binary_gender_contract_requires_both_categories")
    if not np.isfinite(response).all():
        result["reasons"].append("nonfinite_HbA1c_IFCC_response")
    if result["reasons"]:
        return result
    try:
        coefficients, rank = solve_ols(predictors, response)
    except (ValueError, np.linalg.LinAlgError):
        result["reasons"].append("least_squares_computation_failed")
        return result
    if not np.isfinite(coefficients).all():
        result["reasons"].append("nonfinite_least_squares_result")
        return result
    result.update({"status": "computed", "coefficient": float(coefficients[-1]),
                   "design_rank": rank, "residual_degrees_of_freedom": n - rank})
    return result


def correlation_report(arrays: dict, use_ranks: bool) -> dict:
    n = len(arrays["glucose"])
    x, y = arrays["glucose"], arrays["hba1c"]
    result = {"statistic": "spearman_correlation" if use_ranks else "pearson_correlation",
              "n": n, "design_rank": None, "design_rank_note": "not_applicable_to_correlation",
              "columns": ["FSG" if use_ranks else "FPG", "HbA1c_percent"],
              "unit": "1", "correlation": None, "status": "not_computable", "reasons": [],
              "evidence_id": "R_MIND_SPEARMAN" if use_ranks else "R_BAO_PEARSON"}
    if use_ranks:
        result["tie_method"] = "exact_equality_average_one_based_ranks"
    try:
        if use_ranks:
            x, y = average_ranks(x), average_ranks(y)
        result["correlation"] = pearson(x, y)
        result["status"] = "computed"
    except ValueError as error:
        result["reasons"].append(str(error))
    return result


def arithmetic_self_test() -> dict:
    """Fixed abstract arrays/CSV bytes only: no clinical generation or file I/O."""
    np.testing.assert_allclose(ifcc_from_ngsp(np.array([2.152, 5.62824])), [0.0, 38.0])
    np.testing.assert_equal(average_ranks(np.array([4, 1, 4, 2, 2])), [4.5, 1, 4.5, 2.5, 2.5])
    assert math.isclose(pearson(np.array([1, 2, 3]), np.array([3, 2, 1])), -1.0)
    assert math.isclose(pearson(np.array([1, 2, 3]), np.array([1, 3, 2])), 0.5)
    assert math.isclose(pearson(average_ranks(np.array([1, 1, 2, 3])),
                                average_ranks(np.array([1, 2, 2, 4]))), 5.0 / 6.0)
    predictors = np.array([[a, b, c] for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)])
    response = 2 + predictors @ np.array([3, -4, 5])
    coefficients, rank = solve_ols(predictors, response)
    np.testing.assert_allclose(coefficients, [2, 3, -4, 5], atol=1e-12)
    assert rank == 4
    _, deficient_rank = solve_ols(predictors[:, [0, 0, 2]], response)
    assert deficient_rank == 3
    values = np.array([0.0, 1.0, 2.0, float("nan")])
    expected_pass = {"ge": 2, "gt": 1, "le": 2, "lt": 1, "eq": 1}
    for op, count in expected_pass.items():
        assert predicate_counts(values, op, 1.0) == {
            "n": 4, "evaluated": 3, "passed": count, "failed": 3 - count, "unevaluable": 1}
    for x, y in ((np.array([1, 1, 1]), np.array([1, 2, 3])),
                 (np.array([1, np.nan, 3]), np.array([1, 2, 3]))):
        try:
            pearson(x, y)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid correlation input was accepted")
    csv_bytes = (b"row_id,age,female,bmi,glucose,hba1c\n"
                 b"abstract_a,0,0,1,0,0\nabstract_b,1,1,2,1,1\n")
    parsed, parsed_info = parse_source_csv(csv_bytes)
    assert parsed_info["schema_pass"] and parsed_info["n_records"] == 2
    assert parsed_info["distinct_nonempty_row_id_count"] == 2
    np.testing.assert_equal(parsed["bmi"], [1.0, 2.0])
    assert set(parsed) == set(COLUMNS) and "abstract_a" not in json.dumps(parsed_info)
    duplicate_parsed, duplicate_info = parse_source_csv(csv_bytes.replace(b"abstract_b", b"abstract_a"))
    assert not duplicate_info["schema_pass"]
    assert duplicate_info["duplicate_row_id_record_count"] == 2
    assert duplicate_info["duplicate_row_id_occurrences_after_first"] == 1
    assert duplicate_info["n_records"] == 2  # Neither duplicate row was removed.
    np.testing.assert_equal(duplicate_parsed["bmi"], [1.0, 2.0])
    _, empty_id_info = parse_source_csv(csv_bytes.replace(b"abstract_b", b" "))
    assert not empty_id_info["schema_pass"]
    assert empty_id_info["empty_or_whitespace_row_id_count"] == 1
    return {"status": "pass", "scope": "fixed_nonclinical_arithmetic_arrays_and_in_memory_CSV_only",
            "checks": ["NGSP_inverse", "average_tied_ranks", "negative_Pearson",
                       "nonperfect_Pearson", "tied_Spearman", "OLS_known_coefficients",
                       "OLS_rank_deficiency", "all_five_predicate_operators",
                       "constant_and_nonfinite_correlation_rejection",
                       "six_column_task_CSV_parsing", "duplicate_row_id_schema_rejection_without_filtering",
                       "empty_row_id_schema_rejection"],
            "source_tables_read": 0, "generator_executions": 0, "files_written": 0}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for context in SOURCE_IDS:
        parser.add_argument("--" + context.lower(), type=Path, help=f"retained generated-source {context} CSV")
    parser.add_argument("--eligibility", type=Path, help="author's context_eligibility.json")
    parser.add_argument("--output", type=Path, help="new aggregate JSON path; existing files are not overwritten")
    parser.add_argument("--self-test", action="store_true", help="only run fixed abstract arithmetic checks")
    args = parser.parse_args(argv)
    if args.self_test:
        if any(getattr(args, name) is not None for name in ("j", "b", "m", "eligibility", "output")):
            parser.error("--self-test cannot be combined with file arguments")
        print(json.dumps(arithmetic_self_test(), indent=2, allow_nan=False))
        return 0
    if any(getattr(args, name) is None for name in ("j", "b", "m", "eligibility", "output")):
        parser.error("--j, --b, --m, --eligibility and --output are all required")
    inputs = [args.j.resolve(), args.b.resolve(), args.m.resolve(), args.eligibility.resolve()]
    if len(set(inputs)) != 4 or args.output.resolve() in inputs:
        parser.error("all input paths must be distinct; output must differ from every input")
    if args.output.exists():
        parser.error("output already exists; provide a new report path")
    try:
        declarations, eligibility_hash = load_eligibility(args.eligibility)
    except (OSError, UnicodeError, ValueError, TypeError, OverflowError):
        parser.error("eligibility declaration unavailable or invalid; no source CSV read")
    report = {"schema_version": 1, "scope": "independent_source_only_aggregate_recomputation",
              "implementation_sha256": digest(Path(__file__).read_bytes()),
              "numpy_version": np.__version__,
              "eligibility_path": str(args.eligibility.resolve()),
              "eligibility_sha256": eligibility_hash,
              "unit_mapping": {"equation": "NGSP_percent = 0.09148 * IFCC_mmol_per_mol + 2.152",
                               "applied_to_J_response": "IFCC = (hba1c - 2.152) / 0.09148",
                               "assay_equivalence_certified": False},
              "analysis_conventions": {"weights": "equal", "selection": [], "missing_policy": "error",
                                       "gender_binary_alias": "female (0/1)", "J_intercept": True,
                                       "J_projections": "separate age/female/BMI and age/female/FPG",
                                       "M_ties": "average", "rows_filtered_or_repaired": 0},
              "limitations": ["Qualified scenario only; original weights and estimator processing remain unknown.",
                              "Unobserved exclusions cannot be verified from generated columns.",
                              "Source eligibility failures invalidate matched-source interpretation.",
                              "No source fit, transport, target validity, or improvement conclusion is made."],
              "target_inputs_read": 0, "contexts": {}}
    all_pass = True
    for context_id in SOURCE_IDS:
        source_path = getattr(args, context_id.lower())
        entry = {"path": str(source_path.resolve())}
        report["contexts"][context_id] = entry
        try:
            arrays, info = read_source(source_path)
        except (OSError, UnicodeError, ValueError, csv.Error):
            entry.update({"status": "not_computable", "reason": "source_CSV_unavailable_or_invalid",
                          "eligibility": {"status": "not_computable"}, "statistics": {}})
            all_pass = False
            continue
        eligible = eligibility_report(arrays, declarations[context_id])
        source_valid = info["schema_pass"] and info["n_matches_schedule"] and eligible["status"] == "pass"
        if context_id == "J":
            statistics = {"Q_J_bmi": j_projection(arrays, "bmi"),
                          "Q_J_fpg": j_projection(arrays, "glucose")}
        elif context_id == "B":
            statistics = {"Q_B_pearson": correlation_report(arrays, False)}
        else:
            statistics = {"Q_M_spearman": correlation_report(arrays, True)}
        for statistic in statistics.values():
            statistic["source_eligibility_and_schema_pass"] = source_valid
            statistic["interpretation"] = (
                "qualified_source_scenario_point_only" if source_valid and statistic["status"] == "computed"
                else "diagnostic_only_not_accepted_as_matched_source_evidence")
        entry.update({"input": info, "eligibility": eligible, "statistics": statistics})
        context_pass = source_valid and all(s["status"] == "computed" for s in statistics.values())
        entry["status"] = "complete" if context_pass else "failed_or_unavailable"
        all_pass &= context_pass
    report["status"] = "complete" if all_pass else "failed_or_unavailable"
    try:
        # Exclusive creation preserves earlier audit reports and every input.
        with args.output.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(report, stream, indent=2, allow_nan=False)
            stream.write("\n")
    except (OSError, ValueError):
        print("Aggregate report could not be written; no inputs were changed.", file=sys.stderr)
        return 2
    print(json.dumps({"status": report["status"], "aggregate_report": str(args.output.resolve())}))
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
