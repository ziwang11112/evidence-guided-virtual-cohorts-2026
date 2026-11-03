"""Developmental paired-branch evaluation; no study reads at import.

Only evaluate() opens frozen reference aggregates, after the controller verifies
scientific closure and all output bindings. Never decodes reference patient data.
"""
from __future__ import annotations

import hashlib
import importlib.util
import io
import itertools
import json
from pathlib import Path
import platform
import sys

import numpy as np
import pandas as pd
import scipy


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
F2 = PROJECT / "work/chns_admission_2026-11-01/f2"
VARIABLES = ("age", "female", "bmi", "glucose", "hba1c")
CONSTRUCTORS = ("A01", "A02")
VERSIONS = ("initial", "self_review", "source_feedback")
ENDPOINTS = ("E1", "E2", "E3")
ANALYSIS_IDS = {"E1": "A_BMI", "E2": "A_GLUCOSE", "E3": "A_AGE"}
POLICY = {
    "schema_version": 1,
    "kind": "developmental_pilot_evaluation_v1",
    "constructors": list(CONSTRUCTORS),
    "versions": list(VERSIONS),
    "target_slots": 18,
    "rows_each": 3000,
    "primary_endpoints": list(ENDPOINTS),
    "primary_analysis": "unchanged_F2_unweighted_intercept_OLS_common_complete_case_contract",
    "reference": "frozen_F2_aggregate_and_independent_aggregate_no_patient_redecoding",
    "summary": "mean_absolute_discrepancy_over_all_three_seeds_only_when_complete",
    "contrasts": ["self_review_minus_initial", "source_feedback_minus_initial", "source_feedback_minus_self_review"],
    "reference_comparable_diagnostics": "five_variables_mean_sample_sd_q10_median_q90_and_glucose_hba1c_Pearson_Spearman",
    "generated_only_diagnostics": "BMI_glucose_HbA1c_linear_q01_q99_all_ten_Pearson_pairs_exact_duplicate_rows_finite_domain_counts_fit_rank",
    "duplicate_definition": "number_of_repeated_numeric_five_variable_rows_after_first_excluding_row_id_NaNs_equal",
    "invalid_values": "report_counts_including_fractional_age_withhold_statistics_no_row_deletion",
    "scientific_annotations": "all_six_versions_hash_bound_analysis_support_and_complete_authenticated_source_feedback",
    "analysis_environment": "live_host_Python_numpy_pandas_scipy_versions_equal_frozen_binding_before_reference_access",
    "reference_for_added_diagnostics": "unavailable_no_reference_supplement",
    "inference": "developmental_descriptive_two_constructors_seed_spread_is_conditional_simulation_variation",
    "equivalence_margin": None,
    "overall_success_rule": None,
}


class IntegrityError(ValueError):
    """Identity failures are fatal; they never become ordinary missing analyses."""


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
        valid = (sha(folder / "output/generated.csv") == slot["output_sha256"] and
                 sha(folder / "execution.json") == slot["execution_sha256"])
    except OSError as error:
        raise IntegrityError("target_artifact_unavailable_after_closure") from error
    if not valid:
        raise IntegrityError("target_artifact_identity_changed_after_closure")


def read_target_bytes(slot):
    verify_target_identity(slot)
    path = Path(slot["bundle"]) / "executions" / slot["run_id"] / "output/generated.csv"
    try:
        data = path.read_bytes()
    except OSError as error:
        raise IntegrityError("target_output_unavailable_during_read") from error
    if hashlib.sha256(data).hexdigest() != slot["output_sha256"]:
        raise IntegrityError("target_output_changed_during_read")
    return data


def parse_generated_bytes(data):
    try:
        frame = pd.read_csv(io.BytesIO(data), dtype={"row_id": "string", **{k: float for k in VARIABLES}}, float_precision="round_trip")
    except (ValueError, pd.errors.ParserError, UnicodeError) as error:
        raise OutputValidationError("generated_csv_parse_failed") from error
    if list(frame) != ["row_id", *VARIABLES] or len(frame) != 3000:
        raise OutputValidationError("generated_csv_layout_invalid")
    if not (frame["row_id"].notna().all() and frame["row_id"].str.len().gt(0).all() and frame["row_id"].is_unique):
        raise OutputValidationError("generated_row_identifiers_invalid")
    return frame


def analyze_generated(frame, module, plan):
    age = frame["age"].to_numpy(dtype=float)
    fractional = np.isfinite(age) & (age != np.floor(age))
    if not fractional.any():
        return module.analyze(frame, plan, reference=False)
    reason = "nonintegral_age_task_violation"
    nonpositive = {k: int((np.isfinite(frame[k]) & (frame[k] <= 0)).sum()) for k in ("glucose", "hba1c")}
    report = {"status": "withheld", "mode": "generated", "n": len(frame),
              "quality": {"nonpositive_glycemia": nonpositive}, "gate_reason": reason,
              "estimands": {}, "diagnostics": None, "national_representativeness": False}
    for item in plan["estimands"]:
        report["estimands"][item["id"]] = {"status": "unavailable", "coefficient": None, "unit": item["unit"], "n": len(frame),
            "rank": None, "condition_number": None, "reason": reason,
            "interval": {"status": "unavailable", "lower": None, "upper": None, "standard_error": None,
                         "groups": None, "degrees_of_freedom": None, "reason": reason, "method": "CR1_t"}}
    return report


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_release_sha256(release):
    """Full release identity used by the controller; independent of JSON layout."""
    return hashlib.sha256(json.dumps(release, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def binding(path):
    path = Path(path).resolve()
    return {"path": str(path), "sha256": sha(path)}


def checked_binding(item):
    require(isinstance(item, dict) and set(item) == {"path", "sha256"}, "Invalid file binding")
    path = Path(item["path"])
    require(path.is_absolute() and path.is_file() and sha(path) == item["sha256"], "Bound file changed: " + str(path))
    return path.resolve()


def write_new(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, "Cannot import bound module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _controller_gate(ledger, evaluator_sha256):
    controller = load_module(HERE / "pilot_controller_v1.py", "developmental_pilot_evaluation_controller")
    return controller.PilotController.open(ledger).verify_evaluation(evaluator_sha256)


def scientific_annotations(raw):
    expected = {f"{c}/{v}" for c in CONSTRUCTORS for v in VERSIONS}
    require(isinstance(raw, dict) and set(raw) == expected, "All six scientific annotation records required")
    resolved = {}
    for key, record in raw.items():
        require(set(record) == {"candidate_binding", "analysis_evidence", "support_assessment", "source_feedback",
                                "source_feedback_format", "unavailable_reason"}, "Invalid scientific annotation record")
        require(record["source_feedback_format"] == "pilot_source_closure_event_v1", "Unknown source feedback format")
        require(isinstance(record["source_feedback"], list), "Source feedback bindings required")
        support = {}
        assessment = None
        if record["candidate_binding"] is None:
            require(record["analysis_evidence"] is None and record["support_assessment"] is None and
                    isinstance(record["unavailable_reason"], str) and record["unavailable_reason"].strip(),
                    "Unavailable scientific version requires a reason")
            support = {e: {"analysis_id": a, "status": "unavailable", "assessment": None, "rationale": None,
                            "assumption_ids": [], "gaps": [], "reason": record["unavailable_reason"]}
                       for e, a in ANALYSIS_IDS.items()}
        else:
            declaration = read(checked_binding(record["analysis_evidence"]))
            assessment = read(checked_binding(record["support_assessment"]))
            analyses = declaration["analyses"]
            by_id = {a["id"]: a for a in analyses}
            require(len(by_id) == len(analyses) and set(ANALYSIS_IDS.values()) <= set(by_id), "Required scientific analyses missing")
            for endpoint, analysis_id in ANALYSIS_IDS.items():
                analysis = by_id[analysis_id]
                require(analysis["assessment"] in {"directly_reported", "transported", "partial", "unassessed"}
                        and isinstance(analysis["rationale"], str) and analysis["rationale"].strip()
                        and isinstance(analysis["assumption_ids"], list) and isinstance(analysis["gaps"], list),
                        "Incomplete scientific analysis-support declaration")
                support[endpoint] = {"analysis_id": analysis_id, "status": "declared", **analysis}
        feedback = []
        for item in record["source_feedback"]:
            event = read(checked_binding(item))
            require(event.get("kind") == "sources_closed" and event["payload"].get("key") == key
                    and isinstance(event["payload"].get("feedback"), dict), "Wrong authenticated source report")
            feedback.append({"binding": item, "report": event["payload"]})
        require(feedback or (isinstance(record["unavailable_reason"], str) and record["unavailable_reason"].strip()),
                "Missing source feedback requires its disposition reason")
        resolved[key] = {**record, "analysis_support": support, "support_assessment_record": assessment,
                         "source_discrepancy_reports": feedback}
    return resolved


def prepare_evaluation(ledger_directory, *, controller_gate=None):
    """Verify closure and output bytes before touching either reference binding.

    controller_gate is a trusted adapter seam for invented fixtures; normal calls
    use PilotController.verify_evaluation, never a caller-supplied inventory.
    """
    ledger = Path(ledger_directory).resolve()
    release_path = ledger / "release.json"
    release = read(release_path)
    own_hash = sha(__file__)
    require(checked_binding(release["evaluator"]) == Path(__file__).resolve(), "Wrong evaluator path")
    require(release["evaluator"]["sha256"] == own_hash, "Evaluator changed")
    inventory = (controller_gate or _controller_gate)(ledger, own_hash)
    require(inventory.get("kind") == "developmental_pilot_closed_inventory" and inventory.get("schema_version") == 1
            and inventory.get("status") == "closed" and inventory.get("scientific_closed") is True,
            "Scientifically closed inventory required")
    require(inventory.get("release_sha256") == canonical_release_sha256(release), "Closed inventory release mismatch")
    for name in ("scientific_freeze_sha256", "inventory_sha256"):
        require(isinstance(inventory.get(name), str) and len(inventory[name]) == 64, "Missing immutable closure binding")
    require(inventory.get("authorization") is not None, "Evaluation authorization required")
    metadata = release["evaluation"]
    require(set(metadata) == {"analysis_module", "analysis_plan", "reference_report", "independent_reference_report",
                              "independent_recompute", "policy", "analysis_environment"}, "Unexpected evaluation metadata")
    require(checked_binding(metadata["analysis_module"]) == (F2 / "evaluation/chns_f2_evaluation.py").resolve(),
            "Only unchanged F2 scientific analysis is supported")
    require(checked_binding(metadata["analysis_plan"]) == (F2 / "analysis_plan.json").resolve(), "Wrong F2 analysis plan")
    checked_binding(metadata["independent_recompute"])
    policy_path = checked_binding(metadata["policy"])
    require(read(policy_path) == POLICY, "Evaluation policy differs from frozen implementation")
    require(read(checked_binding(metadata["analysis_environment"])) == analysis_environment(), "Live host analysis environment differs")
    seeds = release["target_seeds"]
    require(len(seeds) == len(set(seeds)) == 3 and all(type(s) is int for s in seeds), "Three distinct target seeds required")
    require(release["n_rows"] == 3000, "Fixed 3000-row design required")
    targets = [s for s in inventory["slots"] if s["role"] == "target"]
    expected = set(itertools.product(CONSTRUCTORS, VERSIONS, seeds))
    require(len(targets) == 18 and {(s["constructor"], s["version"], s["seed"]) for s in targets} == expected,
            "All eighteen distinct target slots required")
    for slot in targets:
        require(slot["n_rows"] == 3000 and slot["context_id"] == release["target_context"], "Wrong target context or size")
        require(isinstance(slot["status"], str) and slot["status"], "Slot disposition required")
        if slot["status"] == "success":
            run = Path(slot["bundle"]) / "executions" / slot["run_id"]
            require(run.resolve().is_relative_to(Path(slot["bundle"]).resolve()), "Execution path escapes bundle")
            verify_target_identity(slot)
    annotations = scientific_annotations(inventory.get("scientific_annotations"))
    return ledger, release, inventory, sorted(targets, key=lambda s: (s["constructor"], s["version"], s["seed"])), annotations


def generated_diagnostics(frame):
    """Added diagnostics are generated-only; never silently omit bad rows."""
    arrays = {k: frame[k].to_numpy(dtype=float) for k in VARIABLES}
    finite = {k: np.isfinite(v) for k, v in arrays.items()}
    nonfinite = {k: int((~v).sum()) for k, v in finite.items()}
    outside = {
        "age": finite["age"] & ((arrays["age"] < 35) | (arrays["age"] > 74) | (arrays["age"] != np.floor(arrays["age"]))),
        "female": finite["female"] & ~np.isin(arrays["female"], [0, 1]),
        **{k: finite[k] & (arrays[k] <= 0) for k in ("bmi", "glucose", "hba1c")},
    }
    invalid = np.zeros(len(frame), dtype=bool)
    for key in VARIABLES:
        invalid |= ~finite[key] | outside[key]
    good = not invalid.any()
    tails = {k: {"q01": None, "q99": None} for k in ("bmi", "glucose", "hba1c")}
    pairs = {f"{a}__{b}": None for a, b in itertools.combinations(VARIABLES, 2)}
    if good:
        for key in tails:
            q = np.quantile(arrays[key], [.01, .99], method="linear")
            tails[key] = {"q01": float(q[0]), "q99": float(q[1])}
        for a, b in itertools.combinations(VARIABLES, 2):
            if len(frame) > 1 and np.ptp(arrays[a]) > 0 and np.ptp(arrays[b]) > 0:
                value = float(np.corrcoef(arrays[a], arrays[b])[0, 1])
                pairs[f"{a}__{b}"] = value if np.isfinite(value) else None
    return {"status": "computed" if good else "withheld_invalid_values", "scope": "generated_only",
            "reference_status": "unavailable_no_reference_supplement", "tail_quantiles": tails,
            "pearson_pairs": pairs, "duplicate_rows_after_first": int(frame.duplicated(list(VARIABLES)).sum()),
            "nonfinite_by_variable": nonfinite, "domain_violations_by_variable": {k: int(v.sum()) for k, v in outside.items()},
            "fractional_age_rows": int((finite["age"] & (arrays["age"] != np.floor(arrays["age"]))).sum()),
            "invalid_rows": int(invalid.sum()), "n_rows": len(frame)}


def summarize(reference, slots, seeds):
    require(len(slots) == 18 and {(s["constructor"], s["version"], s["seed"]) for s in slots}
            == set(itertools.product(CONSTRUCTORS, VERSIONS, seeds)), "Summary requires all eighteen slots")
    endpoints = {}
    for endpoint in ENDPOINTS:
        ref = reference["estimands"][endpoint]
        records = {}
        for constructor in CONSTRUCTORS:
            versions = {}
            for version in VERSIONS:
                selected = [s for s in slots if s["constructor"] == constructor and s["version"] == version]
                estimates = [{"seed": s["seed"], "coefficient": s["analysis"]["estimands"][endpoint]["coefficient"]
                              if s.get("analysis") and s["analysis"]["estimands"][endpoint]["status"] == "computed" else None}
                             for s in sorted(selected, key=lambda s: s["seed"])]
                values = [x["coefficient"] for x in estimates if x["coefficient"] is not None]
                complete = len(values) == 3 and all(s["status"] == "success" for s in selected) and ref["status"] == "computed"
                versions[version] = {"complete": complete, "valid_seed_count": len(values), "seed_estimates": estimates,
                    "analysis_support": selected[0]["analysis_support"][endpoint],
                    "mean_absolute_discrepancy": sum(abs(v - ref["coefficient"]) for v in values) / 3 if complete else None,
                    "mean_signed_discrepancy": sum(v - ref["coefficient"] for v in values) / 3 if complete else None,
                    "seed_range": [min(values), max(values)] if values else None,
                    "direction_status": "incomplete" if len(values) < 3 else "stable_positive" if min(values) > 0 else
                                        "stable_negative" if max(values) < 0 else "unresolved"}
            changes = {}
            for after, before in (("self_review", "initial"), ("source_feedback", "initial"), ("source_feedback", "self_review")):
                complete = versions[after]["complete"] and versions[before]["complete"]
                changes[f"{after}_minus_{before}"] = {"complete": complete, "mean_absolute_discrepancy_change":
                    versions[after]["mean_absolute_discrepancy"] - versions[before]["mean_absolute_discrepancy"] if complete else None}
            records[constructor] = {"versions": versions, "changes": changes}
        endpoints[endpoint] = {"unit": ref["unit"], "reference": ref, "constructors": records}
    return {"endpoints": endpoints, "reserved_target_slots": 18,
            "successful_execution_slots": sum(s["status"] == "success" for s in slots),
            "failed_or_unrun_slots": sum(s["status"] != "success" for s in slots),
            "independent_constructions": 2, "overall_success_rule": None, "equivalence_margin": None,
            "scope": "developmental_descriptive_paired_branches_two_constructors_not_72_independent_replications"}


def evaluate(ledger_directory, *, controller_gate=None):
    ledger, release, inventory, targets, annotations = prepare_evaluation(ledger_directory, controller_gate=controller_gate)
    out = ledger / "evaluation"
    out.mkdir()  # Exclusive reservation, before reference bytes; no overwrite/retry.
    write_new(out / "INTENT.json", {"release_sha256": inventory["release_sha256"],
              "inventory_sha256": inventory["inventory_sha256"], "evaluator_sha256": sha(__file__),
              "analysis_environment": analysis_environment()})
    try:
        meta = release["evaluation"]
        ref_path = checked_binding(meta["reference_report"])
        independent_path = checked_binding(meta["independent_reference_report"])
        reference = read(ref_path)["reference"]
        independent_reference = read(independent_path)["reference"]
        # Both aggregate hashes are frozen; their historic numerical agreement was
        # independently reviewed. Do not demand byte-identical independent floats.
        require(set(reference["estimands"]) == set(independent_reference["estimands"]) == set(ENDPOINTS),
                "Frozen reference endpoints are incomplete")
        module = load_module(checked_binding(meta["analysis_module"]), "developmental_pilot_f2_analysis")
        plan = read(checked_binding(meta["analysis_plan"]))
        module.validate_plan(plan)
        rows = []
        for slot in targets:
            record = {**slot, "analysis_support": annotations[f'{slot["constructor"]}/{slot["version"]}']["analysis_support"],
                      "analysis": None, "comparison": None, "generated_only_diagnostics": None, "analysis_error": None}
            if slot["status"] == "success":
                data = read_target_bytes(slot)  # Identity failures bypass recoverable analysis handling.
                try:
                    frame = parse_generated_bytes(data)
                    record["generated_only_diagnostics"] = generated_diagnostics(frame)
                    analysis = analyze_generated(frame, module, plan)
                    comparison = module.compare_estimates(reference, analysis)
                    json.dumps({"analysis": analysis, "comparison": comparison}, allow_nan=False)
                    record.update(analysis=analysis, comparison=comparison)
                except IntegrityError:
                    raise
                except Exception as error:
                    record["analysis_error"] = {"code": error.code if isinstance(error, OutputValidationError) else "analysis_computation_failed",
                                                "exception": type(error).__name__}
                verify_target_identity(slot)  # Also catches changes during parse/analysis.
            rows.append(record)
        report = {"schema_version": 1, "kind": "developmental_pilot_paired_branch_evaluation", "reference": reference,
                  "reference_bindings": {k: meta[k] for k in ("reference_report", "independent_reference_report")},
                  "release_sha256": inventory["release_sha256"], "scientific_freeze_sha256": inventory["scientific_freeze_sha256"],
                  "inventory_sha256": inventory["inventory_sha256"], "slots": rows, **summarize(reference, rows, release["target_seeds"]),
                  "analysis_environment": analysis_environment(),
                  "scientific_annotations": annotations,
                  "patient_reference_redecoded": False, "independent_recomputation": "pending",
                  "diagnostic_scope": {"existing_27": "reference_comparable", "added": "generated_only_reference_unavailable"},
                  "limitations": ["CHNS was researcher-exposed; this is developmental evidence.",
                                  "Reference clustered intervals, source uncertainty, conditional seed variation and transport assumptions remain distinct.",
                                  "Reference interval membership is descriptive, not equivalence.",
                                  "Finite sampled tails do not establish finite population moments."]}
        for slot in targets:
            verify_target_identity(slot)
        require(scientific_annotations(inventory["scientific_annotations"]) == annotations, "Scientific annotations changed during evaluation")
        write_new(out / "REPORT.json", report)
        write_new(out / "COMPLETION.json", {"report": binding(out / "REPORT.json"), "intent": binding(out / "INTENT.json")})
        return {"report": str(out / "REPORT.json"), "reserved_target_slots": 18, "independent_recomputation": "pending"}
    except Exception as error:
        write_new(out / "FAILURE.json", {"error_type": type(error).__name__, "no_automatic_retry": True})
        raise


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger")
    arguments = parser.parse_args()
    print(json.dumps(evaluate(arguments.ledger)))
