"""Independent CSV/QR recomputation; imports neither primary scientific helper.

Shares only the controller's authenticated closure gate and frozen metadata.
Never decodes patients, runs generators, or rewrites the primary report.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import itertools
import json
import math
from pathlib import Path
import platform
import sys

import numpy as np
import pandas as pd
import scipy
from scipy import stats


HERE = Path(__file__).resolve().parent
VARIABLES = ("age", "female", "bmi", "glucose", "hba1c")
CONSTRUCTORS = ("A01", "A02")
VERSIONS = ("initial", "self_review", "source_feedback")
MODELS = {"E1": (("age", "female", "bmi"), "bmi", "%/(kg/m^2)"),
          "E2": (("age", "female", "glucose"), "glucose", "%/(mmol/L)"),
          "E3": (("female", "bmi", "glucose", "age"), "age", "%/year")}
RTOL, ATOL = 1e-8, 1e-10  # Arithmetic agreement only, never a utility tolerance.
ANALYSIS_IDS = {"E1": "A_BMI", "E2": "A_GLUCOSE", "E3": "A_AGE"}


class IntegrityError(ValueError):
    pass


class OutputValidationError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def analysis_environment():
    return {"schema_version": 1, "kind": "developmental_pilot_analysis_environment_v1",
            "python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__, "scipy": scipy.__version__}


def verify_target_identity(slot):
    if slot["status"] != "success":
        return
    folder = Path(slot["bundle"]) / "executions" / slot["run_id"]
    try:
        matches = (sha(folder / "output/generated.csv") == slot["output_sha256"] and
                   sha(folder / "execution.json") == slot["execution_sha256"])
    except OSError as error:
        raise IntegrityError("target_artifact_unavailable_after_closure") from error
    if not matches:
        raise IntegrityError("target_artifact_identity_changed_after_closure")


def read_target_bytes(slot):
    verify_target_identity(slot)
    try:
        contents = (Path(slot["bundle"]) / "executions" / slot["run_id"] / "output/generated.csv").read_bytes()
    except OSError as error:
        raise IntegrityError("target_output_unavailable_during_read") from error
    if hashlib.sha256(contents).hexdigest() != slot["output_sha256"]:
        raise IntegrityError("target_output_changed_during_read")
    return contents


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_release_sha256(release):
    """Recompute the controller's canonical full-release identity independently."""
    return hashlib.sha256(json.dumps(release, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def bound(item):
    require(set(item) == {"path", "sha256"}, "Bad binding")
    path = Path(item["path"])
    require(path.is_absolute() and path.is_file() and sha(path) == item["sha256"], "Bound file changed")
    return path.resolve()


def write_new(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def controller_gate(ledger, evaluator_sha256):
    spec = importlib.util.spec_from_file_location("developmental_pilot_independent_controller", HERE / "pilot_controller_v1.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.PilotController.open(ledger).verify_evaluation(evaluator_sha256)


def scientific_annotations(raw):
    require(isinstance(raw, dict) and set(raw) == {f"{c}/{v}" for c in CONSTRUCTORS for v in VERSIONS},
            "All six scientific versions required")
    result = {}
    for key, item in raw.items():
        require(set(item) == {"candidate_binding", "analysis_evidence", "support_assessment", "source_feedback",
                              "source_feedback_format", "unavailable_reason"}, "Invalid scientific annotation record")
        require(item["source_feedback_format"] == "pilot_source_closure_event_v1" and isinstance(item["source_feedback"], list),
                "Invalid source report declaration")
        labels = {}
        assessment = None
        if item["candidate_binding"] is None:
            require(item["analysis_evidence"] is None and item["support_assessment"] is None and
                    isinstance(item["unavailable_reason"], str) and item["unavailable_reason"].strip(), "Unavailable version lacks reason")
            for endpoint, analysis_id in ANALYSIS_IDS.items():
                labels[endpoint] = {"analysis_id": analysis_id, "status": "unavailable", "assessment": None,
                    "rationale": None, "assumption_ids": [], "gaps": [], "reason": item["unavailable_reason"]}
        else:
            declarations = read(bound(item["analysis_evidence"]))["analyses"]
            assessment = read(bound(item["support_assessment"]))
            by_id = {row["id"]: row for row in declarations}
            require(len(by_id) == len(declarations) and set(ANALYSIS_IDS.values()) <= set(by_id), "Missing focal scientific-use declaration")
            for endpoint, analysis_id in ANALYSIS_IDS.items():
                declaration = by_id[analysis_id]
                require(declaration["assessment"] in {"directly_reported", "transported", "partial", "unassessed"}
                        and isinstance(declaration["rationale"], str) and declaration["rationale"].strip()
                        and isinstance(declaration["assumption_ids"], list) and isinstance(declaration["gaps"], list),
                        "Incomplete analysis support declaration")
                labels[endpoint] = {"analysis_id": analysis_id, "status": "declared", **declaration}
        reports = []
        for item_binding in item["source_feedback"]:
            event = read(bound(item_binding))
            require(event.get("kind") == "sources_closed" and event["payload"].get("key") == key
                    and isinstance(event["payload"].get("feedback"), dict), "Source report identity mismatch")
            reports.append({"binding": item_binding, "report": event["payload"]})
        require(reports or (isinstance(item["unavailable_reason"], str) and item["unavailable_reason"].strip()),
                "Source report absence lacks reason")
        result[key] = {**item, "analysis_support": labels, "support_assessment_record": assessment, "source_discrepancy_reports": reports}
    return result


def parse_csv(contents):
    try:
        reader = csv.DictReader(io.StringIO(contents.decode("utf-8"), newline=""))
        if reader.fieldnames != ["row_id", *VARIABLES]:
            raise OutputValidationError("generated_csv_layout_invalid")
        rows = list(reader)
        if len(rows) != 3000:
            raise OutputValidationError("generated_csv_layout_invalid")
        if not (all(row["row_id"] for row in rows) and len({row["row_id"] for row in rows}) == len(rows)):
            raise OutputValidationError("generated_row_identifiers_invalid")
        missing = {"", "na", "n/a", "nan", "null", "none"}
        data = {name: np.array([np.nan if row[name].strip().lower() in missing else float(row[name]) for row in rows])
                for name in VARIABLES}
    except OutputValidationError:
        raise
    except (ValueError, UnicodeError, csv.Error, AttributeError) as error:
        raise OutputValidationError("generated_csv_parse_failed") from error
    return data


def quantile(values, probability):
    ordered = sorted(float(x) for x in values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    return ordered[lower] + (position - lower) * (ordered[upper] - ordered[lower])


def finite_correlation(left, right, *, ranked=False):
    if len(left) < 2 or max(left) == min(left) or max(right) == min(right):
        return None
    value = float(stats.spearmanr(left, right).statistic if ranked else stats.pearsonr(left, right).statistic)
    return value if math.isfinite(value) else None


def violations(data):
    nonfinite = {k: int(sum(not math.isfinite(float(x)) for x in v)) for k, v in data.items()}
    masks = {}
    for key, values in data.items():
        test = (lambda x: x < 35 or x > 74 or x != math.floor(x)) if key == "age" else (lambda x: x not in (0, 1)) if key == "female" else (lambda x: x <= 0)
        masks[key] = [math.isfinite(float(x)) and test(float(x)) for x in values]
    invalid = sum(any(not math.isfinite(float(data[k][i])) or masks[k][i] for k in VARIABLES) for i in range(len(data["age"])))
    return nonfinite, {k: sum(v) for k, v in masks.items()}, invalid


def added_diagnostics(data):
    nonfinite, domains, invalid = violations(data)
    tails = {k: {"q01": None, "q99": None} for k in ("bmi", "glucose", "hba1c")}
    pairs = {f"{a}__{b}": None for a, b in itertools.combinations(VARIABLES, 2)}
    if not invalid:
        tails = {k: {"q01": quantile(data[k], .01), "q99": quantile(data[k], .99)} for k in tails}
        pairs = {f"{a}__{b}": finite_correlation(data[a], data[b]) for a, b in itertools.combinations(VARIABLES, 2)}
    numeric_rows = [tuple("nan" if math.isnan(float(data[k][i])) else float(data[k][i]) for k in VARIABLES)
                    for i in range(len(data["age"]))]
    return {"status": "computed" if not invalid else "withheld_invalid_values", "scope": "generated_only",
            "reference_status": "unavailable_no_reference_supplement", "tail_quantiles": tails, "pearson_pairs": pairs,
            "duplicate_rows_after_first": len(numeric_rows) - len(set(numeric_rows)), "nonfinite_by_variable": nonfinite,
            "domain_violations_by_variable": domains,
            "fractional_age_rows": int(sum(math.isfinite(float(x)) and x != math.floor(x) for x in data["age"])),
            "invalid_rows": invalid, "n_rows": len(numeric_rows)}


def interval(reason):
    return {"status": "unavailable", "lower": None, "upper": None, "standard_error": None,
            "groups": None, "degrees_of_freedom": None, "reason": reason, "method": "CR1_t"}


def analyze(data):
    nonfinite, domains, invalid = violations(data)
    nonpositive = {k: domains[k] for k in ("glucose", "hba1c")}
    fractional = any(math.isfinite(float(x)) and x != math.floor(x) for x in data["age"])
    reason = "nonintegral_age_task_violation" if fractional else "nonpositive_glycemia_interpretation_required" if sum(nonpositive.values()) else \
             "invalid_analysis_values_no_row_deletion" if invalid else None
    n = len(data["age"])
    result = {"status": "withheld" if reason else "complete", "mode": "generated", "n": n,
              "quality": {"nonpositive_glycemia": nonpositive}, "gate_reason": reason,
              "estimands": {}, "diagnostics": None, "national_representativeness": False}
    for key, (predictors, focal, unit) in MODELS.items():
        record = {"status": "unavailable", "coefficient": None, "unit": unit, "n": n,
                  "rank": None, "condition_number": None}
        if reason:
            record.update(reason=reason, interval=interval(reason))
        else:
            design = np.column_stack([np.ones(n)] + [data[name] for name in predictors])
            rank = int(np.linalg.matrix_rank(design)) if n else 0
            condition = float(np.linalg.cond(design)) if n else np.inf
            record.update(rank=rank, condition_number=condition if math.isfinite(condition) else None,
                          interval=interval("primary_estimate_unavailable"))
            if n < 100 or rank != design.shape[1] or n <= design.shape[1]:
                record["reason"] = "insufficient_n" if n < 100 else "rank_or_residual_df_failure"
            else:
                q, r = np.linalg.qr(design, mode="reduced")
                beta = np.linalg.solve(r, q.T @ data["hba1c"])
                value = float(beta[1 + predictors.index(focal)])
                require(math.isfinite(value), "Nonfinite independent OLS")
                record.update(status="computed", coefficient=value, interval=interval("generated_no_inference"))
        result["estimands"][key] = record
    if not reason:
        marginal = {}
        for key, values in data.items():
            mean = math.fsum(float(x) for x in values) / n
            sd = math.sqrt(math.fsum((float(x) - mean) ** 2 for x in values) / (n - 1))
            marginal[key] = {"mean": mean, "sd": sd, "q10": quantile(values, .1),
                             "median": quantile(values, .5), "q90": quantile(values, .9)}
        result["diagnostics"] = {"marginal": marginal,
            "joint": {"pearson": finite_correlation(data["glucose"], data["hba1c"]),
                      "spearman": finite_correlation(data["glucose"], data["hba1c"], ranked=True)}}
    return result


def compare(reference, generated):
    result = {}
    for endpoint in MODELS:
        ref = reference["estimands"][endpoint]
        gen = generated["estimands"][endpoint]
        ci = ref["interval"]
        direction = "inconclusive"
        if ci["status"] == "available":
            direction = "positive" if ci["lower"] > 0 else "negative" if ci["upper"] < 0 else direction
        valid = ref["status"] == gen["status"] == "computed"
        value, base = gen["coefficient"], ref["coefficient"]
        result[endpoint] = {"status": "computed" if valid else "unavailable", "reference": base, "generated": value,
            "difference": value - base if valid else None, "reference_direction": direction,
            "generated_sign": None if value is None else "positive" if value > 0 else "negative" if value < 0 else "zero",
            "ratio": value / base if valid and direction != "inconclusive" and base != 0 else None,
            "interval_membership": bool(ci["lower"] <= value <= ci["upper"]) if valid and ci["status"] == "available" else None}
    return result


def summarize(reference, slots):
    endpoints = {}
    for endpoint in MODELS:
        ref = reference["estimands"][endpoint]
        constructors = {}
        for constructor in CONSTRUCTORS:
            versions = {}
            for version in VERSIONS:
                subset = sorted((s for s in slots if (s["constructor"], s["version"]) == (constructor, version)), key=lambda s: s["seed"])
                estimates = [{"seed": s["seed"], "coefficient": s["analysis"]["estimands"][endpoint]["coefficient"]
                              if s["analysis"] and s["analysis"]["estimands"][endpoint]["status"] == "computed" else None} for s in subset]
                values = [s["coefficient"] for s in estimates if s["coefficient"] is not None]
                complete = len(values) == 3 and all(s["status"] == "success" for s in subset) and ref["status"] == "computed"
                versions[version] = {"complete": complete, "valid_seed_count": len(values), "seed_estimates": estimates,
                    "analysis_support": subset[0]["analysis_support"][endpoint],
                    "mean_absolute_discrepancy": math.fsum(abs(v - ref["coefficient"]) for v in values) / 3 if complete else None,
                    "mean_signed_discrepancy": math.fsum(v - ref["coefficient"] for v in values) / 3 if complete else None,
                    "seed_range": [min(values), max(values)] if values else None,
                    "direction_status": "incomplete" if len(values) < 3 else "stable_positive" if all(v > 0 for v in values) else
                                        "stable_negative" if all(v < 0 for v in values) else "unresolved"}
            changes = {}
            for newer, older in (("self_review", "initial"), ("source_feedback", "initial"), ("source_feedback", "self_review")):
                complete = versions[newer]["complete"] and versions[older]["complete"]
                changes[f"{newer}_minus_{older}"] = {"complete": complete, "mean_absolute_discrepancy_change":
                    versions[newer]["mean_absolute_discrepancy"] - versions[older]["mean_absolute_discrepancy"] if complete else None}
            constructors[constructor] = {"versions": versions, "changes": changes}
        endpoints[endpoint] = {"unit": ref["unit"], "reference": ref, "constructors": constructors}
    return {"endpoints": endpoints, "reserved_target_slots": 18, "successful_execution_slots": sum(s["status"] == "success" for s in slots),
            "failed_or_unrun_slots": sum(s["status"] != "success" for s in slots), "independent_constructions": 2,
            "overall_success_rule": None, "equivalence_margin": None,
            "scope": "developmental_descriptive_paired_branches_two_constructors_not_72_independent_replications"}


def differences(expected, actual, path=""):
    errors = []
    if isinstance(expected, dict) and isinstance(actual, dict):
        if set(expected) != set(actual):
            errors.append({"path": path, "reason": "different_keys"})
        for key in sorted(expected.keys() & actual.keys()):
            errors += differences(expected[key], actual[key], path + "/" + key)
    elif isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            errors.append({"path": path, "reason": "different_lengths"})
        for index, (left, right) in enumerate(zip(expected, actual)):
            errors += differences(left, right, path + "/" + str(index))
    elif type(expected) in (int, float) and type(actual) in (int, float):
        if not math.isfinite(expected) or not math.isfinite(actual) or not math.isclose(expected, actual, rel_tol=RTOL, abs_tol=ATOL):
            errors.append({"path": path, "reason": "numeric_disagreement"})
    elif expected != actual:
        errors.append({"path": path, "reason": "semantic_disagreement"})
    return errors


def recompute(ledger_directory, *, verified_controller_gate=None):
    ledger = Path(ledger_directory).resolve()
    release = read(ledger / "release.json")
    metadata = release["evaluation"]
    require(bound(metadata["independent_recompute"]) == Path(__file__).resolve(), "Independent code changed")
    bound(release["evaluator"])  # Hash only; never imports primary evaluation.
    inventory = (verified_controller_gate or controller_gate)(ledger, release["evaluator"]["sha256"])
    require(inventory.get("kind") == "developmental_pilot_closed_inventory" and inventory.get("status") == "closed"
            and inventory.get("scientific_closed") is True and inventory.get("authorization") is not None,
            "Authorized scientific closure required")
    require(inventory["release_sha256"] == canonical_release_sha256(release), "Release mismatch")
    bound(metadata["analysis_module"])
    bound(metadata["analysis_plan"])
    bound(metadata["policy"])
    require(read(bound(metadata["analysis_environment"])) == analysis_environment(), "Live host analysis environment differs")
    annotations = scientific_annotations(inventory.get("scientific_annotations"))
    seeds = release["target_seeds"]
    require(len(seeds) == len(set(seeds)) == 3 and release["n_rows"] == 3000, "Wrong seed/size contract")
    slots = sorted([s for s in inventory["slots"] if s["role"] == "target"], key=lambda s: (s["constructor"], s["version"], s["seed"]))
    require(len(slots) == 18 and {(s["constructor"], s["version"], s["seed"]) for s in slots}
            == set(itertools.product(CONSTRUCTORS, VERSIONS, seeds)), "Incomplete target inventory")
    for slot in slots:
        require(slot["n_rows"] == 3000 and slot["context_id"] == release["target_context"], "Wrong target context/size")
        if slot["status"] == "success":
            folder = Path(slot["bundle"]) / "executions" / slot["run_id"]
            require(folder.resolve().is_relative_to(Path(slot["bundle"]).resolve()), "Bad output path")
            verify_target_identity(slot)
    completion = read(ledger / "evaluation/COMPLETION.json")
    report_path = bound(completion["report"])
    require(report_path == (ledger / "evaluation/REPORT.json").resolve() and not (ledger / "evaluation/FAILURE.json").exists(),
            "Successful bound primary report required")
    out = ledger / "independent_evaluation"
    out.mkdir()  # Exclusive; no retries or overwrite.
    write_new(out / "INTENT.json", {"release_sha256": inventory["release_sha256"], "inventory_sha256": inventory["inventory_sha256"],
                                   "primary_report_sha256": sha(report_path), "independent_code_sha256": sha(__file__),
                                   "analysis_environment": analysis_environment()})
    try:
        reference = read(bound(metadata["reference_report"]))["reference"]
        bound(metadata["independent_reference_report"])
        primary = read(report_path)
        errors = differences(reference, primary["reference"], "/reference")
        errors += differences(annotations, primary["scientific_annotations"], "/scientific_annotations")
        errors += differences(analysis_environment(), primary["analysis_environment"], "/analysis_environment")
        for field in ("release_sha256", "scientific_freeze_sha256", "inventory_sha256"):
            errors += differences(inventory[field], primary[field], "/" + field)
        recomputed = []
        for slot in slots:
            row = {**slot, "analysis_support": annotations[f'{slot["constructor"]}/{slot["version"]}']["analysis_support"],
                   "analysis": None, "comparison": None, "generated_only_diagnostics": None, "analysis_error": None}
            if slot["status"] == "success":
                contents = read_target_bytes(slot)
                try:
                    data = parse_csv(contents)
                    row["generated_only_diagnostics"] = added_diagnostics(data)
                    analysis = analyze(data)
                    comparison = compare(reference, analysis)
                    json.dumps({"analysis": analysis, "comparison": comparison}, allow_nan=False)
                    row.update(analysis=analysis, comparison=comparison)
                except IntegrityError:
                    raise
                except Exception as error:
                    row["analysis_error"] = {"code": error.code if isinstance(error, OutputValidationError) else "analysis_computation_failed",
                                             "exception": type(error).__name__}
                verify_target_identity(slot)
            recomputed.append(row)
        errors += differences(recomputed, primary["slots"], "/slots")
        summary = summarize(reference, recomputed)
        errors += differences(summary, {key: primary[key] for key in summary}, "/summary")
        result = {"schema_version": 1, "status": "matched" if not errors else "disagreement", "disagreements": errors,
                  "primary_report_sha256": sha(report_path), "independent_code_sha256": sha(__file__),
                  "numerical_tolerance": {"rtol": RTOL, "atol": ATOL, "scope": "arithmetic_not_scientific_utility"},
                  "patient_rows_read": 0, "generator_executions": 0, "recomputed_slots": recomputed, "summary": summary,
                  "scientific_annotations": annotations, "analysis_environment": analysis_environment(),
                  "method": "csv.DictReader; independent QR solve; manual linear quantiles and moments; scipy correlations; independent paired arithmetic",
                  "reference_uncertainty": "reused_frozen_aggregate_not_reestimated"}
        for slot in slots:
            verify_target_identity(slot)
        require(scientific_annotations(inventory["scientific_annotations"]) == annotations, "Scientific annotation identities changed")
        write_new(out / "REPORT.json", result)
        write_new(out / "COMPLETION.json", {"report_sha256": sha(out / "REPORT.json"), "status": result["status"]})
        return {"report": str(out / "REPORT.json"), "status": result["status"], "disagreement_count": len(errors)}
    except Exception as error:
        write_new(out / "FAILURE.json", {"error_type": type(error).__name__, "no_automatic_retry": True})
        raise


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger")
    args = parser.parse_args()
    print(json.dumps(recompute(args.ledger)))
