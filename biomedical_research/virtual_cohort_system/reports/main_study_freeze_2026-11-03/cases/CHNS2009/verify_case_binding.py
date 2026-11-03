"""Focused hand-checkable invented arithmetic; no biomedical sampling or files."""
from __future__ import annotations
import copy
import itertools
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import generated_provider
import source_operations
from cohort_harness.contracts import validate_task


def run():
    checks = []
    def check(name, predicate):
        if not predicate:
            raise AssertionError(name)
        checks.append(name)
    # Balanced deterministic factorial fixture makes all nuisance predictors
    # orthogonal. Its known response coefficients are engineering constants.
    data = list(itertools.product((40., 60.), (0., 1.), (20., 30.), (4., 6.))) * 8
    frame = pd.DataFrame(data, columns=["age", "female", "bmi", "glucose"])
    frame["hba1c"] = 2 + .01 * frame.age + .3 * frame.female + .02 * frame.bmi + .4 * frame.glucose
    frame["row_id"] = [f"invented_{i}" for i in range(len(frame))]
    output = generated_provider.generated_statistics(frame)
    check("F2_three_exact_hand_coefficients", np.allclose([x["value"] for x in output["analyses"]], [.02, .4, .01], atol=1e-12, rtol=0))
    check("F2_complete_27_diagnostics_and_generated_only_shape", len(output["diagnostics"]) == 27 and set(output) == {"analyses", "diagnostics", "quality", "n"})
    check("no_reference_fields", all(set(row) <= {"id", "value", "unit", "status", "n", "rank", "reason"} for key in ("analyses", "diagnostics") for row in output[key]))
    invalid = frame.copy(); invalid.loc[0, "glucose"] = 0
    withheld = generated_provider.generated_statistics(invalid)
    check("nonpositive_withholds_without_row_deletion", withheld["n"] == len(frame) and all(x["value"] is None for x in withheld["analyses"] + withheld["diagnostics"]))
    rank_bad = frame.copy(); rank_bad["female"] = 0
    check("rank_failure_not_regularized", all(x["value"] is None for x in generated_provider.generated_statistics(rank_bad)["analyses"]))
    check("F2_existing_minimum_n_retained", all(x["value"] is None for x in generated_provider.generated_statistics(frame.iloc[:16])["analyses"]))
    renamed = frame.rename(columns={"female": "gender_binary", "bmi": "BMI", "glucose": "FPG", "hba1c": "HbA1c_percent"})
    names = ["age", "gender_binary", "BMI", "FPG", "HbA1c_percent"]
    values = renamed[names].to_numpy(float)
    ctx = {"role": "declared_source_population_moments", "source_context_id": "CTX_JANSEN_SELECTED", "assumption_ids": ["invented_fixture"], "moment_derivation": "Exact balanced finite support fixture; population covariance ddof0", "selection_status": "moments_after_declared_source_selection", "weights": "equal_assumption", "variables": names, "means": values.mean(axis=0).tolist(), "covariance": np.cov(values, rowvar=False, ddof=0).tolist(), "units": {"age": "year", "gender_binary": "1", "BMI": "kg/m^2", "FPG": "mmol/L", "HbA1c_percent": "%"}, "gender_mapping": "female=1,male=0"}
    for evidence, golden in (("R_JANSEN_BMI", .02 / .09148), ("R_JANSEN_FPG", .4 / .09148)):
        got = source_operations.evaluate(evidence, ctx)
        check(evidence + "_native_IFCC_covariance_projection", abs(got["calculated_value"] - golden) < 1e-12)
        check(evidence + "_qualified_not_strict", got["strict_replay"] == "not_computable" and not got["exact_source_reconstruction"])
    native = copy.deepcopy(ctx)
    native["variables"][-1] = "HbA1c_IFCC"
    native["units"].pop("HbA1c_percent")
    native["units"]["HbA1c_IFCC"] = "mmol/mol"
    native["means"][-1] = (native["means"][-1] - 2.152) / .09148
    transform = np.eye(5); transform[-1, -1] = 1 / .09148
    native["covariance"] = (transform @ np.asarray(ctx["covariance"]) @ transform).tolist()
    check("native_IFCC_and_affine_response_paths_agree", abs(source_operations.evaluate("R_JANSEN_BMI", native)["calculated_value"] - .02 / .09148) < 1e-12)
    bao = copy.deepcopy(ctx); bao["source_context_id"] = "CTX_BAO_ANALYZED"
    check("Bao_Pearson_matches_independent_centered_formula", abs(source_operations.evaluate("R_BAO_PEARSON", bao)["calculated_value"] - .4 / np.sqrt(.01**2*100 + .3**2*.25 + .02**2*25 + .4**2)) < 1e-12)
    def singular_covariance(context):
        context["covariance"][0] = [0.] * 5
        for row in context["covariance"]:
            row[0] = 0.
    for name, mutate, evidence in [("target_context_rejected", lambda x: x.update(role="target_moments"), "R_JANSEN_BMI"), ("preselection_moments_rejected", lambda x: x.update(selection_status="parent_law"), "R_JANSEN_BMI"), ("ordinary_moments_do_not_identify_rank_correlation", lambda x: None, "R_MIND_SPEARMAN"), ("singular_projection_rejected", singular_covariance, "R_JANSEN_BMI")]:
        bad = copy.deepcopy(ctx); mutate(bad)
        try:
            source_operations.evaluate(evidence, bad)
        except (ValueError, np.linalg.LinAlgError):
            check(name, True)
        else:
            check(name, False)
    task = json.loads((HERE / "task.json").read_text())
    validate_task(task)
    check("actual_harness_task_schema", True)
    report = {"status": "passed", "checks": checks, "check_count": len(checks), "fixtures": "invented_deterministic_arrays_only", "patient_or_generated_clinical_rows_read": False, "clinical_generators_executed": False, "source_estimates_or_target_effects_used_in_tests": False, "independent_review": "pending"}
    (HERE / "arithmetic_verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))

if __name__ == "__main__":
    run()
