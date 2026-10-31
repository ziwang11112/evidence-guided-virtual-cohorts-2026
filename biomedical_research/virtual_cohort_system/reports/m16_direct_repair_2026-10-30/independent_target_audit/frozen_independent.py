"""Independent M15-B numerical/dataflow audit. No work or row reads on import.

Implemented from PROTOCOL.md and the evaluator README, without consulting or
importing the evaluator implementation. All execution on actual rows requires
the controller's explicit post-freeze authorization and a verified manifest.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
import sys
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd
from scipy.linalg import svdvals
import statsmodels.formula.api as smf


CANDIDATE_COLUMNS = ["sample_id", "race", "sex", "age", "bmi", "urate"]
OBSERVED_COLUMNS = CANDIDATE_COLUMNS[:-1]
GROUPS = [(race, sex) for race in ("White", "Black") for sex in ("male", "female")]
GLOBAL_MODELS = [
    ("global.bmi", "urate ~ b + a + m + r", "b", "mg/dL per 5 kg/m^2 BMI"),
    ("global.age", "urate ~ b + a + m + r", "a", "mg/dL per 10 years"),
    ("global.curvature", "urate ~ b + a + m + r + I(b ** 2)", "I(b ** 2)", "mg/dL per squared scaled BMI"),
    ("global.interaction", "urate ~ b + a + m + r + b:m", "b:m", "mg/dL per 5 kg/m^2 BMI male interaction"),
]


def finite_number(value):
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) else None


def sign(value):
    return None if value is None else (1 if value > 0 else -1 if value < 0 else 0)


def linear_quantile(values, probability):
    """Linear interpolation at (n - 1) * probability, independently explicit."""
    if not values or not 0 <= probability <= 1:
        raise ValueError("Quantile needs observations and a probability in [0, 1].")
    ordered = sorted(values)
    index = (len(ordered) - 1) * probability
    left = math.floor(index)
    right = math.ceil(index)
    fraction = index - left
    return (1 - fraction) * ordered[left] + fraction * ordered[right]


def estimate_record(key, units, n, complete_n, rank, value=None, reason=None, rank_kind="OLS design"):
    if value is not None and not math.isfinite(float(value)):
        value, reason = None, "Nonfinite fitted estimate."
    return {"estimand": key, "value": None if value is None else float(value),
            "units": units, "n": n, "complete_n": complete_n,
            "matrix_rank": rank, "rank_kind": rank_kind,
            "status": "ok" if value is not None else "failure", "reason": reason}


def numeric_rank(matrix):
    singular = svdvals(matrix, check_finite=True)
    if len(singular) == 0 or singular[0] == 0:
        return 0
    tolerance = max(matrix.shape) * sys.float_info.epsilon * singular[0]
    return sum(bool(item > tolerance) for item in singular)


def model_estimate(rows, key, formula, term, units, reverse=False):
    prepared = []
    for row in rows:
        age, bmi, urate = (finite_number(row.get(column)) for column in ("age", "bmi", "urate"))
        if age is None or bmi is None or urate is None:
            continue
        if row.get("sex") not in ("male", "female") or row.get("race") not in ("White", "Black"):
            continue
        prepared.append({"age": age, "bmi": bmi, "urate": urate,
                         "b": (bmi - 28) / 5, "a": (age - 40) / 10,
                         "m": int(row["sex"] == "male"), "r": int(row["race"] == "Black")})
    n, complete_n = len(rows), len(prepared)
    if complete_n != n:
        return estimate_record(key, units, n, complete_n, None, reason="Missing, nonnumeric, nonfinite, or invalid model inputs; no rows dropped.")
    if n == 0:
        return estimate_record(key, units, n, complete_n, 0, reason="Empty model domain.")
    try:
        model = smf.ols(formula, data=pd.DataFrame(prepared), missing="raise")
        rank = numeric_rank(model.exog)
        if rank != model.exog.shape[1]:
            return estimate_record(key, units, n, complete_n, rank, reason="Rank-deficient design; no pseudoinverse estimate accepted.")
        result = model.fit(method="qr")
        return estimate_record(key, units, n, complete_n, rank, value=float(result.params[term]))
    except (ValueError, ArithmeticError) as error:
        return estimate_record(key, units, n, complete_n, None, reason=f"Model fit failed: {type(error).__name__}.")


def global_estimates(rows):
    stable_rows = sorted(rows, key=lambda row: str(row.get("sample_id", "")))
    return {key: model_estimate(stable_rows, key, formula, term, units)
            for key, formula, term, units in GLOBAL_MODELS}


def estimate_table(rows):
    """The fixed 24 estimands, with no inferred or omitted endpoints."""
    stable_rows = sorted(rows, key=lambda row: str(row.get("sample_id", "")))
    result = global_estimates(stable_rows)
    for race, sex in GROUPS:
        group = [row for row in stable_rows if row.get("race") == race and row.get("sex") == sex]
        prefix = f"group.{race}.{sex}"
        key = f"{prefix}.reverse"
        result[key] = model_estimate(group, key, "bmi ~ urate + age", "urate", "(kg/m^2)/(mg/dL)", reverse=True)
        numbers = [finite_number(row.get("urate")) for row in group]
        valid = [number for number in numbers if number is not None]
        n, complete_n = len(group), len(valid)
        for name in ("mean", "sd", "median", "q90"):
            key = f"{prefix}.{name}"
            reason, value = None, None
            if n == 0:
                reason = "Empty summary domain."
            elif complete_n != n:
                reason = "Missing, nonnumeric, or nonfinite urate; no rows dropped."
            elif name == "sd" and n < 2:
                reason = "Sample SD requires at least two observations."
            elif name == "mean":
                value = statistics.fmean(valid)
            elif name == "sd":
                value = statistics.stdev(valid)
            elif name == "median":
                value = statistics.median(valid)
            else:
                value = linear_quantile(valid, 0.9)
            result[key] = estimate_record(key, "mg/dL", n, complete_n, int(n > 0), value, reason,
                                          rank_kind="Intercept-only summary domain; no regression fitted")
    if len(result) != 24:
        raise AssertionError("Fixed endpoint count changed.")
    return result


def reference_psu_sensitivity(rows):
    """Delete each joint (stratum, PSU), retaining every success and failure."""
    groups = sorted({(str(row["SDMVSTRA"]), str(row["SDMVPSU"])) for row in rows})
    if any(not stratum or not psu for stratum, psu in groups):
        raise ValueError("Missing design group identifier.")
    full = global_estimates(rows)
    deletions = []
    for stratum, psu in groups:
        kept = [row for row in rows if (str(row["SDMVSTRA"]), str(row["SDMVPSU"])) != (stratum, psu)]
        deletions.append({"stratum": stratum, "psu": psu, "omitted_n": len(rows) - len(kept),
                          "remaining_n": len(kept), "estimates": global_estimates(kept)})
    ranges = {}
    for key, fit in full.items():
        successful = [record["estimates"][key]["value"] for record in deletions
                      if record["estimates"][key]["status"] == "ok"]
        failures = sum(record["estimates"][key]["status"] != "ok" for record in deletions)
        finite_stable = None if fit["value"] is None or not successful else all(sign(value) == sign(fit["value"]) for value in successful)
        ranges[key] = {"full": fit, "minimum": min(successful) if successful else None,
                       "maximum": max(successful) if successful else None,
                       "omitted_psu_groups": len(groups), "finite_deletions": len(successful),
                       "failed_deletions": failures,
                       "rank_failed_deletions": sum("Rank-deficient" in (record["estimates"][key]["reason"] or "") for record in deletions),
                       "finite_deletion_sign_stable_with_full": finite_stable,
                       "all_deletions_sign_stable_with_full": finite_stable if not failures else None}
    return {"interpretation": "Unweighted descriptive joint-PSU deletion sensitivity in a fixed quota cohort; not confidence intervals or population uncertainty.",
            "ranges": ranges, "deletions": deletions}


def decimal_value(value):
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("Invalid preservation number.") from None
    if not number.is_finite():
        raise ValueError("Nonfinite preservation number.")
    return number


def candidate_value_for_change_count(value):
    # Preserve invalid outcomes for the estimand failure records rather than
    # dropping them or preventing the fixed endpoint report from being made.
    try:
        return ("number", decimal_value(value))
    except ValueError:
        return ("invalid", str(value))


def validate_identity_and_covariates(observed, reference, initial, final, require_quota=True):
    expected_ids = [row.get("sample_id") for row in observed]
    if any(not isinstance(item, str) or not item for item in expected_ids) or len(set(expected_ids)) != len(expected_ids):
        raise ValueError("Observed IDs must be unique nonempty strings.")
    counts = Counter((row.get("race"), row.get("sex")) for row in observed)
    if set(counts) != set(GROUPS):
        raise ValueError("Observed race/sex domain differs from the four fixed groups.")
    if require_quota and (len(observed) != 200 or any(counts[group] != 50 for group in GROUPS)):
        raise ValueError("Benchmark requires 200 people and exactly 50 per race/sex group.")
    for label, rows in (("reference", reference), ("initial", initial), ("final", final)):
        if [row.get("sample_id") for row in rows] != expected_ids:
            raise ValueError(f"{label}: identity or row order differs from observed.")
        for original, candidate in zip(observed, rows):
            if any(candidate.get(column) != original.get(column) for column in ("race", "sex")):
                raise ValueError(f"{label}: categorical covariate changed.")
            if any(decimal_value(candidate.get(column)) != decimal_value(original.get(column)) for column in ("age", "bmi")):
                raise ValueError(f"{label}: numeric covariate changed.")
    changed_n = sum(candidate_value_for_change_count(first.get("urate")) != candidate_value_for_change_count(last.get("urate"))
                    for first, last in zip(initial, final))
    lexical_changed_n = sum(str(first.get("urate")) != str(last.get("urate")) for first, last in zip(initial, final))
    return {"identity_order_and_covariates_preserved": True, "n": len(observed),
            "group_counts": {f"{race}.{sex}": counts[(race, sex)] for race, sex in GROUPS},
            "changed_urate_rows": changed_n, "lexically_changed_urate_rows": lexical_changed_n,
            "numeric_preservation_convention": "Exact decimal values; formatting-only differences recorded separately."}


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv_rows(path, role):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        columns = reader.fieldnames
        expected = OBSERVED_COLUMNS if role == "observed" else CANDIDATE_COLUMNS
        if role == "reference":
            required = set(CANDIDATE_COLUMNS + ["SDMVSTRA", "SDMVPSU"])
            if columns is None or len(columns) != len(set(columns)) or not required.issubset(columns) or set(columns) - required - {"SEQN", "WTPH2YR"}:
                raise ValueError("Unexpected reference schema.")
        elif columns != expected:
            raise ValueError(f"Unexpected {role} schema.")
        rows = list(reader)
        if any(None in row or any(value is None for value in row.values()) for row in rows):
            raise ValueError(f"Malformed {role} CSV row.")
        return rows


def verify_commitment(path, commitment, label):
    if not isinstance(commitment, str) or len(commitment) != 64 or any(character not in "0123456789abcdef" for character in commitment):
        raise ValueError(f"Invalid {label} SHA256 commitment.")
    actual = sha256_file(path)
    if actual != commitment:
        raise ValueError(f"{label} SHA256 mismatch.")
    return {"label": label, "sha256": actual, "matched": True}


def release_gate(manifest_path):
    """Verify every manifest binding before parsing any cohort CSV.

    This independent gate does not import the evaluator or lifecycle verifier.
    The manifest's review/lifecycle assertions remain trusted controller claims.
    """
    manifest_path = Path(manifest_path).resolve(strict=True)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    if manifest.get("schema_version") != 1 or manifest.get("kind") != "m15b_target_evaluation_release" or manifest.get("evaluation_authorized") is not True:
        raise ValueError("Controller release is absent or unauthorized.")
    checks = ["both_releases_verified", "source_feedback_binding_verified", "source_exposure_map_verified",
              "preservation_verified", "independent_code_review_complete"]
    if any(manifest.get("controller_checks", {}).get(check) is not True for check in checks):
        raise ValueError("A required controller release assertion is absent.")
    bundle = Path(manifest["bundle_path"])
    reference = Path(manifest["reference_path"])
    if not bundle.is_absolute() or not reference.is_absolute():
        raise ValueError("Bundle and reference paths must be absolute.")
    bundle = bundle.resolve(strict=True)
    study = Path(__file__).resolve().parent.parent
    paths = {"observed": bundle / "observed.csv", "reference": reference.resolve(strict=True)}
    bindings = []
    commitments = [(study / "PROTOCOL.md", manifest.get("protocol_sha256"), "protocol"),
                   (study / "evaluation_code" / "evaluator.py", manifest.get("evaluator_sha256"), "released evaluator"),
                   (bundle / "task.json", manifest.get("task_sha256"), "task"),
                   (paths["observed"], manifest.get("observed_sha256"), "observed")]
    for label in ("initial", "final"):
        entry = manifest.get(label, {})
        relative = Path(entry.get("candidate", ""))
        if not entry.get("candidate") or relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"Invalid {label} candidate relative path.")
        candidate = (bundle / relative).resolve(strict=True)
        if not candidate.is_relative_to(bundle):
            raise ValueError(f"{label} candidate escaped bundle.")
        paths[label] = candidate / "generated.csv"
        commitments.extend([(candidate / "freeze.json", entry.get("freeze_sha256"), f"{label} freeze"),
                            (paths[label], entry.get("table_sha256"), f"{label} table")])
    for path, commitment, label in commitments:
        bindings.append(verify_commitment(path, commitment, label))
    # Reference bytes are first accessed only after all nonreference commitments.
    bindings.append(verify_commitment(paths["reference"], manifest.get("reference_sha256"), "reference"))
    return paths, {"release_manifest_sha256": sha256_file(manifest_path), "commitments": bindings,
                   "controller_assertions": manifest["controller_checks"],
                   "independent_audit_sha256": sha256_file(Path(__file__)),
                   "limitation": "Hash verification binds bytes; timing, reviewer identity, source review, and lifecycle validity remain controller assertions. No OS isolation is claimed."}


def audit_rows(observed, reference, initial, final, require_quota=True):
    preservation = validate_identity_and_covariates(observed, reference, initial, final, require_quota)
    estimates = {label: estimate_table(rows) for label, rows in (("reference", reference), ("initial", initial), ("final", final))}
    comparisons = []
    for key in estimates["reference"]:
        measured = estimates["reference"][key]
        entry = {"estimand": key, "units": measured["units"], "reference": measured}
        for label in ("initial", "final"):
            candidate = estimates[label][key]
            entry[label] = candidate
            entry[f"{label}_minus_reference"] = None if measured["value"] is None or candidate["value"] is None else candidate["value"] - measured["value"]
            if key.startswith("global.") or key.endswith(".reverse"):
                entry[f"{label}_direction"] = {"reference_sign": sign(measured["value"]), "candidate_sign": sign(candidate["value"])}
        comparisons.append(entry)
    return {"schema_version": 1, "kind": "m15b_independent_numerical_dataflow_audit",
            "interpretation": "Unweighted descriptions of the same selected 200-person equal-stratum quota cohort; no national inference or combined quality score.",
            "preservation": preservation, "unique_candidate_value_tables": 1 if preservation["changed_urate_rows"] == 0 else 2,
            "estimates": estimates, "comparisons": comparisons,
            "reference_psu_sensitivity": reference_psu_sensitivity(reference)}


def compare_canonical_released_output(independent, released):
    """Compare a transparently mapped released aggregate, never evaluator code.

    Expected canonical aggregate fields: estimates[label][key] with value/n/
    complete_n/matrix_rank/status; reference_psu_sensitivity matching this
    script's ranges/deletion schema; preservation.changed_urate_rows. A schema
    adapter, if needed, must be explicit and retain all 24 keys and deletions.
    Differences are reported numerically without a scientific pass threshold.
    """
    differences = []
    def walk(left, right, location):
        if isinstance(left, dict):
            for key, value in left.items():
                if key in ("units", "reason", "rank_kind", "interpretation", "numeric_preservation_convention", "lexically_changed_urate_rows"):
                    continue
                if key not in right:
                    differences.append({"field": f"{location}.{key}", "kind": "missing_released_field"})
                else:
                    walk(value, right[key], f"{location}.{key}")
        elif isinstance(left, list):
            if not isinstance(right, list) or len(left) != len(right):
                differences.append({"field": location, "kind": "list_length_mismatch"})
                return
            for index, (first, second) in enumerate(zip(left, right)):
                walk(first, second, f"{location}[{index}]")
        elif isinstance(left, (float, int)) and not isinstance(left, bool) and isinstance(right, (float, int)) and not isinstance(right, bool):
            if left != right:
                differences.append({"field": location, "kind": "numeric_difference", "independent": left, "released": right,
                                    "independent_minus_released": left - right, "absolute_difference": abs(left - right)})
        elif left != right:
            differences.append({"field": location, "kind": "categorical_or_null_mismatch", "independent": left, "released": right})
    for field in ("estimates", "reference_psu_sensitivity"):
        walk(independent[field], released.get(field, {}), field)
    walk(independent["preservation"]["changed_urate_rows"], released.get("preservation", {}).get("changed_urate_rows"), "preservation.changed_urate_rows")
    return {"differences": differences,
            "note": "Exact numeric differences include ordinary floating-point roundoff. No scientific threshold or quality pass/fail is applied."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute-after-controller-release", action="store_true")
    parser.add_argument("--release-manifest")
    parser.add_argument("--output-dir")
    parser.add_argument("--canonical-released-output", help="Optional explicit aggregate schema mapping of released evaluation output.")
    args = parser.parse_args(argv)
    if not args.execute_after_controller_release:
        parser.error("No input opened: explicit post-freeze controller authorization is required.")
    if not args.release_manifest or not args.output_dir:
        parser.error("A controller release manifest and a new private output directory are required.")
    output = Path(args.output_dir)
    if output.exists():
        raise ValueError("Output directory already exists; refusing overwrite.")
    paths, bindings = release_gate(args.release_manifest)
    rows = {role: read_csv_rows(path, role) for role, path in paths.items()}
    report = audit_rows(rows["observed"], rows["reference"], rows["initial"], rows["final"])
    report["bindings"] = bindings
    if args.canonical_released_output:
        mapped = Path(args.canonical_released_output)
        released = json.loads(mapped.read_text(encoding="utf-8-sig"))
        report["released_output_comparison"] = compare_canonical_released_output(report, released)
        report["bindings"]["canonical_released_output_sha256"] = sha256_file(mapped)
    output.mkdir(parents=True, exist_ok=False)
    (output / "independent_audit.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    with (output / "independent_estimands.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["estimand", "units", "reference", "initial", "final", "initial_minus_reference", "final_minus_reference"])
        writer.writeheader()
        for row in report["comparisons"]:
            writer.writerow({"estimand": row["estimand"], "units": row["units"],
                             **{label: row[label]["value"] for label in ("reference", "initial", "final")},
                             **{f"{label}_minus_reference": row[f"{label}_minus_reference"] for label in ("initial", "final")}})
    print(json.dumps({"aggregate_outputs_written": 2, "fixed_estimands": len(report["comparisons"]),
                      "changed_urate_rows": report["preservation"]["changed_urate_rows"]}))


if __name__ == "__main__":
    main()
