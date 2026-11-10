"""Independent PNS-BP estimator checks using invented fixtures only.

This module never locates or reads clinical reference data. Its oracle uses
weighted orthogonal projection / Frisch-Waugh-Lovell, independently of the
production adapter's least-squares implementation. Running this file performs
only the artificial self-check until an explicit adapter comparison is added.
"""

from __future__ import annotations

import json
import math
import argparse
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import sys
import types
from typing import Any


def _dot(a: list[float], b: list[float], weights: list[float]) -> float:
    return math.fsum(w * x * y for w, x, y in zip(weights, a, b))


def _basis(columns: list[list[float]], weights: list[float]) -> list[list[float]]:
    basis: list[list[float]] = []
    for column in columns:
        residual = list(column)
        # Reorthogonalization keeps this independent implementation stable.
        for _ in range(2):
            for vector in basis:
                coefficient = _dot(residual, vector, weights)
                residual = [r - coefficient * q for r, q in zip(residual, vector)]
        norm_squared = _dot(residual, residual, weights)
        original_norm = _dot(column, column, weights)
        if norm_squared <= 1e-24 * max(original_norm, 1.0):
            raise ValueError("rank_deficient")
        denominator = math.sqrt(norm_squared)
        basis.append([value / denominator for value in residual])
    return basis


def _residualize(values: list[float], basis: list[list[float]], weights: list[float]) -> list[float]:
    residual = list(values)
    for vector in basis:
        coefficient = _dot(values, vector, weights)
        residual = [r - coefficient * q for r, q in zip(residual, vector)]
    return residual


def _population_sd(values: list[float], weights: list[float]) -> float:
    total = math.fsum(weights)
    mean = math.fsum(w * x for w, x in zip(weights, values)) / total
    return math.sqrt(max(math.fsum(w * (x - mean) ** 2 for w, x in zip(weights, values)) / total, 0.0))


def independent_estimate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Return an independent complete-case estimate from caller-supplied rows.

    Required columns are age, female (0/1), bmi, sbp and dbp; weight defaults
    to one. This is a numerical oracle, not a clinical eligibility definition.
    No row-count or magnitude restrictions are silently added.
    """
    fields = ("age", "female", "bmi", "sbp", "dbp", "weight")
    valid: list[list[float]] = []
    for row in rows:
        try:
            values = [float(row.get(field, 1.0) if field == "weight" else row[field]) for field in fields]
        except (KeyError, TypeError, ValueError):
            continue
        if all(math.isfinite(value) for value in values) and values[-1] > 0:
            valid.append(values)
    result: dict[str, Any] = {"n": len(valid), "sbp_bmi_per1": None, "dbp_bmi_per1": None,
                              "sbp_bmi_per5": None, "dbp_bmi_per5": None,
                              "residual_correlation": None, "status": "nonestimable"}
    if not valid:
        return result
    age, female, bmi, sbp, dbp, weights = [list(column) for column in zip(*valid)]
    # Scaling weights and centering age/BMI do not change the requested fits.
    mean_weight = math.fsum(weights) / len(weights)
    weights = [weight / mean_weight for weight in weights]
    age = [(value - 50.0) / 10.0 for value in age]
    bmi = [value - 25.0 for value in bmi]
    try:
        nuisance = _basis([[1.0] * len(valid), age, female], weights)
        _basis([[1.0] * len(valid), age, female, bmi], weights)
    except ValueError:
        return result
    bmi_residual = _residualize(bmi, nuisance, weights)
    denominator = _dot(bmi_residual, bmi_residual, weights)
    outcome_residuals: list[list[float]] = []
    for label, outcome in (("sbp", sbp), ("dbp", dbp)):
        partial = _residualize(outcome, nuisance, weights)
        coefficient = _dot(bmi_residual, partial, weights) / denominator
        residual = [y - coefficient * x for y, x in zip(partial, bmi_residual)]
        outcome_residuals.append(residual)
        result[label + "_bmi_per1"] = coefficient
        result[label + "_bmi_per5"] = 5.0 * coefficient
        result[label + "_sd"] = _population_sd(outcome, weights)
        result[label + "_residual_sd"] = _population_sd(residual, weights)
    left, right = outcome_residuals
    left_norm = _dot(left, left, weights)
    right_norm = _dot(right, right, weights)
    result["status"] = "partly_estimable"
    if left_norm > 1e-20 and right_norm > 1e-20:
        result["residual_correlation"] = max(-1.0, min(1.0, _dot(left, right, weights) / math.sqrt(left_norm * right_norm)))
        result["status"] = "estimable"
    return result


def invented_fixture(weighted: bool = True) -> list[dict[str, float]]:
    """Create 48 artificial records with known adjusted BMI slopes."""
    rows = [{"age": float(22 + (i * 7) % 56), "female": float(i % 2),
             "bmi": 20.0 + ((i * 11) % 17) / 2.0,
             "weight": float((1, 2, 5, 3)[i % 4]) if weighted else 1.0}
            for i in range(48)]
    weights = [row["weight"] for row in rows]
    columns = [[1.0] * len(rows)] + [[row[key] for row in rows] for key in ("age", "female", "bmi")]
    full_basis = _basis(columns, weights)
    first = _residualize([math.sin(i * 0.73) for i in range(len(rows))], full_basis, weights)
    other = _residualize([math.cos(i * 1.13) for i in range(len(rows))], full_basis, weights)
    for i, row in enumerate(rows):
        row["sbp"] = 80.0 + 0.35 * row["age"] + 2.0 * row["female"] + 1.75 * row["bmi"] + 7.0 * first[i]
        row["dbp"] = 45.0 - 0.05 * row["age"] - 1.0 * row["female"] + 0.80 * row["bmi"] + 3.0 * first[i] + 5.0 * other[i]
    return rows


def self_check() -> dict[str, Any]:
    checks: list[str] = []
    for weighted in (False, True):
        rows = invented_fixture(weighted)
        estimate = independent_estimate(rows)
        assert estimate["status"] == "estimable"
        assert math.isclose(estimate["sbp_bmi_per1"], 1.75, abs_tol=1e-11)
        assert math.isclose(estimate["dbp_bmi_per1"], 0.80, abs_tol=1e-11)
        checks.append("known_slopes_" + ("weighted" if weighted else "unweighted"))
        for name, changed in (("row_permutation", list(reversed(rows))),
                              ("weight_scaling", [dict(row, weight=row["weight"] * 71.0) for row in rows])):
            comparison = independent_estimate(changed)
            for key in ("sbp_bmi_per1", "dbp_bmi_per1", "residual_correlation", "sbp_residual_sd", "dbp_sd"):
                assert math.isclose(comparison[key], estimate[key], abs_tol=1e-10)
            checks.append(name + ("_weighted" if weighted else "_unweighted"))
    rows = invented_fixture()
    invalid = [dict(rows[0], sbp=float("nan")), dict(rows[0], dbp=float("inf")),
               dict(rows[0], weight=0), dict(rows[0], weight=-1), dict(rows[0], weight=None)]
    assert independent_estimate(rows + invalid) == independent_estimate(rows)
    checks.append("common_complete_case_positive_finite_weight_mask")
    singular = [dict(row, bmi=25.0) for row in rows]
    assert independent_estimate(singular)["status"] == "nonestimable"
    checks.append("rank_deficient_preserved_as_nonestimable")
    exact = [dict(row, sbp=80.0 + 0.35 * row["age"] + 2.0 * row["female"] + 1.75 * row["bmi"]) for row in rows]
    result = independent_estimate(exact)
    assert result["status"] == "partly_estimable" and result["residual_correlation"] is None
    assert math.isclose(result["sbp_bmi_per1"], 1.75, abs_tol=1e-11)
    checks.append("zero_residual_variance_retains_slopes")
    assert independent_estimate([])["status"] == "nonestimable"
    checks.append("empty_case_nonestimable")
    return {"status": "PASS", "fixture_only": True, "clinical_data_reads": 0,
            "method": "weighted orthogonal projection / Frisch-Waugh-Lovell",
            "checks": checks, "checks_passed": len(checks)}


def compare_adapter(adapter_path: Path) -> dict[str, Any]:
    """Load only an explicitly named adapter; exercise invented data only."""
    import numpy as np
    import pandas as pd

    spec = importlib.util.spec_from_file_location("reviewed_bp_adapter", adapter_path)
    if spec is None or spec.loader is None:
        raise ValueError("Cannot load the named adapter")
    adapter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adapter)
    checks: list[str] = []

    def compare(rows: list[dict[str, float]], name: str) -> None:
        expected = independent_estimate(rows)
        obtained = adapter.summarize(pd.DataFrame(rows), [row["weight"] for row in rows])
        assert obtained["n"] == expected["n"]
        for production_key, oracle_key in (("bmi_sbp", "sbp_bmi_per5"),
                                           ("bmi_dbp", "dbp_bmi_per5"),
                                           ("residual_correlation", "residual_correlation")):
            actual, target = obtained["estimates"][production_key], expected[oracle_key]
            assert (actual is None) == (target is None), (name, production_key, actual, target)
            if actual is not None:
                assert math.isclose(actual, target, abs_tol=1e-10, rel_tol=1e-10), (name, production_key, actual, target)
        if expected["status"] != "nonestimable":
            for outcome in ("sbp", "dbp"):
                for actual, target in ((obtained["diagnostics"]["margins"][outcome]["sd"], expected[outcome + "_sd"]),
                                       (obtained["diagnostics"]["residual_sd"][outcome], expected[outcome + "_residual_sd"])):
                    assert math.isclose(actual, target, abs_tol=1e-10, rel_tol=1e-10)
        json.dumps(obtained, allow_nan=False)
        checks.append(name)

    for weighted in (False, True):
        rows = invented_fixture(weighted)
        label = "weighted" if weighted else "unit_weighted"
        compare(rows, label + "_independent_estimates_and_sd")
        compare(list(reversed(rows)), label + "_permuted")
        compare([dict(row, weight=row["weight"] * 71.0) for row in rows], label + "_rescaled_weights")
    rows = invented_fixture()
    compare([dict(row, bmi=25.0) for row in rows], "singular_design_all_estimands_retained_as_null")
    compare([dict(row, sbp=80.0 + .35*row["age"] + 2*row["female"] + 1.75*row["bmi"]) for row in rows],
            "deterministic_sbp_keeps_slopes_nulls_correlation")
    for field, value in (("sbp", float("nan")), ("dbp", float("inf")), ("weight", 0.0),
                         ("weight", -1.0), ("female", 2.0)):
        changed = [dict(row) for row in rows]
        changed[0][field] = value
        try:
            adapter.summarize(pd.DataFrame(changed), [row["weight"] for row in changed])
        except ValueError:
            pass
        else:
            raise AssertionError(("invalid_input_not_rejected", field, value))
    checks.append("generated_estimator_rejects_invalid_values_instead_of_filtering")

    with tempfile.TemporaryDirectory(prefix="invented_bp_review_") as temporary:
        folder = Path(temporary)
        generated = pd.DataFrame(invented_fixture(False)).drop(columns="weight")
        generated.to_csv(folder / "invented.csv", index=False)
        task = {"mode": "whole_cohort", "n_rows": len(generated)}
        request = {"schema_version": 1, "task": task, "purpose": "invented fixture only", "analyses": adapter.ANALYSES}
        (folder / "task.json").write_text(json.dumps(task), encoding="utf-8")
        (folder / "request.json").write_text(json.dumps(request), encoding="utf-8")
        result = adapter.analyze(folder / "invented.csv", folder / "task.json", folder / "request.json")
        assert math.isclose(result["estimates"]["bmi_sbp"], 8.75, abs_tol=1e-10)
        assert math.isclose(result["estimates"]["bmi_dbp"], 4.0, abs_tol=1e-10)
        json.dumps(result, allow_nan=False)
        checks.append("generated_adapter_exact_envelope_and_per5_units")
        request["extra"] = True
        (folder / "request.json").write_text(json.dumps(request), encoding="utf-8")
        try:
            adapter.analyze(folder / "invented.csv", folder / "task.json", folder / "request.json")
        except ValueError:
            pass
        else:
            raise AssertionError("unexpected request field accepted")
        checks.append("generated_adapter_rejects_extra_request_fields")

    expected_draws = {key: [] for key in adapter.ANALYSES}
    rng = np.random.default_rng(73991)
    for _ in range(500):
        indices = rng.integers(0, len(rows), size=len(rows))
        estimate = independent_estimate([rows[int(index)] for index in indices])
        for key, oracle_key in (("bmi_sbp", "sbp_bmi_per5"), ("bmi_dbp", "dbp_bmi_per5"),
                                ("residual_correlation", "residual_correlation")):
            if estimate[oracle_key] is not None:
                expected_draws[key].append(estimate[oracle_key])
    stability = adapter.row_resampling_stability(pd.DataFrame(rows), [row["weight"] for row in rows])
    assert stability["seed"] == 73991 and stability["repeats"] == 500
    assert "not design-based" in stability["interpretation"]
    for key, values in expected_draws.items():
        ordered = sorted(values)
        for bound, probability in (("low", .025), ("high", .975)):
            position = (len(ordered) - 1) * probability
            lo, hi = math.floor(position), math.ceil(position)
            quantile = ordered[lo] + (position - lo) * (ordered[hi] - ordered[lo])
            assert math.isclose(stability["intervals"][key][bound], quantile, abs_tol=1e-10, rel_tol=1e-10)
        assert stability["intervals"][key]["estimable_replicates"] == len(values)
    json.dumps(stability, allow_nan=False)
    checks.append("500_fixed_seed_row_resamples_independent_oracle_and_quantiles")
    return {"status": "PASS", "fixture_only": True, "clinical_data_reads": 0,
            "adapter_path": str(adapter_path.resolve()),
            "adapter_sha256": hashlib.sha256(adapter_path.read_bytes()).hexdigest(),
            "checks": checks, "checks_passed": len(checks),
            "numpy_version": np.__version__, "pandas_version": pd.__version__}


def compare_selection(evaluator_path: Path) -> dict[str, Any]:
    """Call select_rows only; never call load_reference/readiness/evaluate."""
    import pandas as pd

    spec = importlib.util.spec_from_file_location("reviewed_bp_evaluator", evaluator_path)
    if spec is None or spec.loader is None:
        raise ValueError("Cannot load the named evaluator")
    evaluator = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(evaluator_path.resolve().parent))
    try:
        spec.loader.exec_module(evaluator)
    finally:
        sys.path.pop(0)
    base = [{"C008": row["age"], "Z001": row["female"] + 1,
             "z004": row["bmi"] * (1.70 ** 2), "z005": 170.0,
             "P005": 2, "W00407": row["sbp"], "W00408": row["dbp"],
             "peso_lab": row["weight"], "Z034": None} for row in invented_fixture()]
    template = base[0]
    valid_additions = [
        dict(template, C008=20, z004=30, z005=120, W00407=60, W00408=30),
        dict(template, C008=79, z004=200, z005=210, W00407=290, W00408=200),
        dict(template, W00407=60, W00408=200),
        dict(template, P005="."), dict(template, P005=None), dict(template, P005=9),
        dict(template, z004=200, z005=120), dict(template),
    ]
    invalid_changes = [("C008", 19), ("C008", 80), ("C008", "."), ("Z001", 3),
                       ("z004", 999), ("z005", 999), ("P005", 1), ("W00407", 999),
                       ("W00408", 999), ("W00407", float("inf")), ("W00408", "."),
                       ("peso_lab", 0), ("peso_lab", -1), ("peso_lab", float("inf"))]
    invalid = [dict(template, **{field: value}) for field, value in invalid_changes]
    supplied = pd.DataFrame(base + valid_additions + invalid)
    selected, weights, audit = evaluator.select_rows(supplied)
    assert len(selected) == len(base) + len(valid_additions) == 56
    assert len(weights) == len(selected)
    assert audit["raw_rows"] == 70
    assert audit["common_eligible_rows"] == 56
    assert audit["design_rank"] == 4 and audit["both_sexes_present"]
    assert audit["unknown_or_inapplicable_pregnancy_retained"] == 3
    # The two unknown pregnancy spellings both coerce to missing, creating
    # a second required-field match; neither such match is removed.
    assert audit["duplicate_required_field_rows"] == 2
    assert audit["no_effects_means_or_correlations_disclosed"] is True
    assert selected.iloc[48]["age"] == 20 and selected.iloc[49]["age"] == 79
    assert selected.iloc[50]["sbp"] < selected.iloc[50]["dbp"]
    assert math.isclose(selected.iloc[54]["bmi"], 200 / 1.2**2)
    assert selected.iloc[0]["female"] == 0 and selected.iloc[1]["female"] == 1
    assert math.isclose(selected.iloc[0]["bmi"], invented_fixture()[0]["bmi"])
    assert weights[0] == invented_fixture()[0]["weight"]
    assert sum(stage["excluded_at_step"] for stage in audit["sequential_exclusions"]) == 14
    assert audit["sequential_exclusions"][-1]["remaining"] == 56
    json.dumps(audit, allow_nan=False)
    # HbA1c values and availability are completely outside the selected fields.
    changed = supplied.copy()
    changed["Z034"] = 12345.0
    altered, altered_weights, _ = evaluator.select_rows(changed)
    assert selected.equals(altered) and all(weights == altered_weights)
    empty, empty_weights, empty_audit = evaluator.select_rows(pd.DataFrame(invalid))
    assert len(empty) == len(empty_weights) == 0 and empty_audit["design_rank"] == 0
    try:
        evaluator.select_rows(supplied.drop(columns="W00408"))
    except ValueError:
        pass
    else:
        raise AssertionError("Missing source column accepted")
    checks = ["inclusive_dictionary_bounds_and_sex_mapping", "common_eight_field_selection",
              "seven_analysis_fields_required_but_unknown_pregnancy_retained",
              "sentinels_nonnumeric_nonfinite_and_nonpositive_weights_rejected",
              "bmi_units_and_no_undeclared_bmi_or_pressure_order_trimming",
              "exact_required_field_duplicates_retained",
              "sequential_exclusion_accounting_and_rank",
              "hba1c_values_and_availability_ignored", "empty_selection_and_missing_column_handling"]
    return {"status": "PASS", "fixture_only": True, "clinical_data_reads": 0,
            "functions_called": ["select_rows"], "functions_not_called": ["load_reference", "readiness", "evaluate"],
            "evaluator_path": str(evaluator_path.resolve()),
            "evaluator_sha256": hashlib.sha256(evaluator_path.read_bytes()).hexdigest(),
            "checks": checks, "checks_passed": len(checks)}


def check_evaluation_guards(evaluator_path: Path) -> dict[str, Any]:
    """Fault-test evaluator plumbing with a fake controller and fake reference.

    This checks evaluator ordering only, not the actual controller's verifier.
    All source/archive loading is replaced in memory by invented fixtures.
    """
    import contextlib
    import io
    import pandas as pd

    spec = importlib.util.spec_from_file_location("reviewed_bp_evaluator_guards", evaluator_path)
    if spec is None or spec.loader is None:
        raise ValueError("Cannot load the named evaluator")
    evaluator = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(evaluator_path.resolve().parent))
    try:
        spec.loader.exec_module(evaluator)
    finally:
        sys.path.pop(0)
    checks: list[str] = []
    previous_controller = sys.modules.get("controller")
    fake_controller = types.ModuleType("controller")
    sys.modules["controller"] = fake_controller
    try:
        with tempfile.TemporaryDirectory(prefix="invented_evaluator_guard_") as temporary:
            folder = Path(temporary)
            evaluator.PROJECT = folder
            (folder / "fixed.txt").write_text("invented immutable metadata", encoding="utf-8")
            metadata_hash = hashlib.sha256((folder / "fixed.txt").read_bytes()).hexdigest()
            for label, key in (("relative", "fixed.txt"), ("absolute", str(folder / "fixed.txt"))):
                (folder / "lock.json").write_text(json.dumps({"files": {key: metadata_hash}}), encoding="utf-8")
                evaluator.check_lock(folder / "lock.json")
                checks.append("freeze_" + label + "_path_resolution")
            (folder / "fixed.txt").write_text("changed invented metadata", encoding="utf-8")
            try:
                evaluator.check_lock(folder / "lock.json")
            except ValueError:
                pass
            else:
                raise AssertionError("Changed freeze binding accepted")
            checks.append("changed_freeze_binding_rejected")

            invented = invented_fixture()
            reference_frame = pd.DataFrame(invented).drop(columns="weight")
            weights = [row["weight"] for row in invented]
            reference_calls: list[str] = []
            events: list[str] = []
            genuine_summarize = evaluator.summarize

            def fake_reference():
                reference_calls.append("invented_only")
                events.append("reference_load")
                return reference_frame, weights, {"fixture_only": True, "common_eligible_rows": len(invented)}

            def traced_summarize(frame, weights=None):
                events.append("reference_summary" if frame is reference_frame else "generated_summary")
                return genuine_summarize(frame, weights)

            def fake_stability(frame, supplied_weights, repeats=500, seed=73991):
                assert frame is reference_frame and list(supplied_weights) == weights
                assert repeats == 500 and seed == 73991
                return {"interpretation": "invented stub: numerical resampling independently checked elsewhere",
                        "repeats": repeats, "seed": seed}

            evaluator.load_reference = fake_reference
            evaluator.summarize = traced_summarize
            evaluator.row_resampling_stability = fake_stability

            def setup(name: str, readiness: str = "ready", corrupt_hash: bool = False,
                      invalid_output: bool = False, add_singular: bool = False) -> dict[str, Any]:
                case = folder / name
                case.mkdir()
                evaluator.U = case
                (case / "READINESS.json").write_text(json.dumps({"status": readiness}), encoding="utf-8")
                generated = reference_frame.copy()
                if invalid_output:
                    generated.loc[0, "sbp"] = float("nan")
                generated.to_csv(case / "invented_generated.csv", index=False)
                output = {"author_id": "A01", "candidate": "candidates/initial", "run_id": "seed271",
                          "seed": 271, "status": "success", "path": str(case / "invented_generated.csv"),
                          "sha256": "0"*64 if corrupt_hash else hashlib.sha256((case / "invented_generated.csv").read_bytes()).hexdigest()}
                outputs = [output]
                if add_singular:
                    singular = reference_frame.copy()
                    singular["bmi"] = 25.0
                    singular.to_csv(case / "invented_singular.csv", index=False)
                    outputs.append({**output, "author_id": "A02", "path": str(case / "invented_singular.csv"),
                                    "sha256": hashlib.sha256((case / "invented_singular.csv").read_bytes()).hexdigest()})
                verified = {"selected_outputs": outputs, "batch_seal_sha256": "invented_seal_only",
                            "author_outcomes": [{"author_id": f"A{i:02}", "status": "completed" if i <= len(outputs) else "abandoned",
                                                 "selected_output_count": 1 if i <= len(outputs) else 0} for i in range(1, 6)],
                            "all_attempted_output_count": 5}
                fake_controller.verify_batch_seal = lambda: verified
                return verified

            def expect_pre_reference_failure(label: str) -> None:
                before = len(reference_calls)
                try:
                    evaluator.evaluate()
                except ValueError:
                    pass
                else:
                    raise AssertionError("Expected pre-reference rejection: " + label)
                assert len(reference_calls) == before, label
                checks.append(label)

            setup("seal_rejected")
            def reject_seal():
                raise ValueError("invented failed batch seal")
            fake_controller.verify_batch_seal = reject_seal
            expect_pre_reference_failure("batch_verifier_failure_precedes_reference_load")
            setup("readiness_failed", readiness="not_ready")
            expect_pre_reference_failure("failed_readiness_precedes_reference_load")
            setup("changed_output", corrupt_hash=True)
            expect_pre_reference_failure("changed_generated_hash_precedes_reference_load")
            setup("invalid_output", invalid_output=True)
            expect_pre_reference_failure("invalid_generated_values_precede_reference_load")
            verified = setup("successful_invented_evaluation", add_singular=True)
            events.clear()
            with contextlib.redirect_stdout(io.StringIO()):
                evaluator.evaluate()
            assert events.index("generated_summary") < events.index("reference_load")
            result = json.loads((evaluator.U / "RESULTS.json").read_text(encoding="utf-8"))
            assert len(result["author_outcomes"]) == 5 and len(result["generated"]) == 2
            assert result["all_attempted_output_count"] == 5 and result["selected_output_count"] == 2
            assert set(result["comparisons"][0]["estimates"]) == {"bmi_sbp", "bmi_dbp", "residual_correlation"}
            expected_reference = independent_estimate(invented)
            expected_generated = independent_estimate([dict(row, weight=1.0) for row in invented])
            for production_key, oracle_key in (("bmi_sbp", "sbp_bmi_per5"), ("bmi_dbp", "dbp_bmi_per5"),
                                               ("residual_correlation", "residual_correlation")):
                comparison = result["comparisons"][0]["estimates"][production_key]
                assert math.isclose(comparison["reference"], expected_reference[oracle_key], abs_tol=1e-10)
                assert math.isclose(comparison["generated"], expected_generated[oracle_key], abs_tol=1e-10)
                assert math.isclose(comparison["signed_difference"], expected_generated[oracle_key] - expected_reference[oracle_key], abs_tol=1e-10)
                assert math.isclose(result["reference_unweighted_sensitivity"]["estimates"][production_key], expected_generated[oracle_key], abs_tol=1e-10)
            assert result["comparisons"][1]["status"] == "rank_deficient"
            assert all(entry["generated"] is None for entry in result["comparisons"][1]["estimates"].values())
            assert all(result["comparisons"][1]["dispersion_ratios"]["residual_" + key] is None for key in ("sbp", "dbp"))
            assert result["reference_row_resampling_stability"]["repeats"] == 500
            json.dumps(result, allow_nan=False)
            checks.append("generated_analysis_precedes_fake_reference_load")
            checks.append("all_focal_estimates_weighted_reference_unweighted_sensitivity_and_differences")
            checks.append("singular_selected_output_retained_without_substitution")
            checks.append("fixed_stability_arguments_and_finite_aggregate_json")
            expect_pre_reference_failure("existing_results_prevent_second_reference_reveal")
    finally:
        if previous_controller is None:
            sys.modules.pop("controller", None)
        else:
            sys.modules["controller"] = previous_controller
    return {"status": "PASS", "clinical_data_reads": 0, "invented_reference_only": True,
            "real_batch_verifier_executed": False,
            "evaluator_sha256": hashlib.sha256(evaluator_path.read_bytes()).hexdigest(),
            "checks": checks, "checks_passed": len(checks)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adapter", type=Path, help="Explicit production adapter to check with invented records only")
    parser.add_argument("--evaluator", type=Path, help="Explicit evaluator whose select_rows receives invented records only")
    parser.add_argument("--evaluation-guards", type=Path, help="Evaluator to fault-test with a fake controller and invented reference only")
    args = parser.parse_args()
    result = {"oracle_self_check": self_check()}
    if args.adapter:
        result["adapter_comparison"] = compare_adapter(args.adapter)
    if args.evaluator:
        result["selection_comparison"] = compare_selection(args.evaluator)
    if args.evaluation_guards:
        result["evaluation_guards"] = check_evaluation_guards(args.evaluation_guards)
    print(json.dumps(result, indent=2, allow_nan=False))
