"""One-time custodian fixture authoring and analytical checks only. No row simulation.

Run before any C4 candidate exists. The original commitment is exclusive-created.
This file is hidden because it contains the precommitted law choices and operators.
"""
from __future__ import annotations

import ast
import hashlib
import json
import math
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SEEDS = {"initial_feedback": [24101, 24103, 24107],
         "election": [24203, 24209, 24223], "untouched_test": [24301, 24307, 24317]}
XY, YZ = F(3, 10), F(3, 5)
LAW_XZ = {"task_a": {"identified_world": F(1, 5)},
          "task_b": {"compatible_world_1": F(1, 10), "compatible_world_2": F(7, 10)}}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")


def gauss_jordan_solve(matrix, vector):
    """Independent exact rational solution, no random or numerical sampling."""
    rows = [list(row) + [v] for row, v in zip(matrix, vector)]
    for k in range(len(rows)):
        pivot = rows[k][k]
        assert pivot != 0
        rows[k] = [v / pivot for v in rows[k]]
        for i in range(len(rows)):
            if i != k:
                multiple = rows[i][k]
                rows[i] = [a - multiple * b for a, b in zip(rows[i], rows[k])]
    return [row[-1] for row in rows]


def analyze_law(xz):
    correlation = [[F(1), XY, xz], [XY, F(1), YZ], [xz, YZ, F(1)]]
    determinant = F(1) + 2 * XY * YZ * xz - XY ** 2 - YZ ** 2 - xz ** 2
    leading_minors = [F(1), 1 - XY ** 2, determinant]
    assert all(v > 0 for v in leading_minors)
    # Independent LDL^T factorization verifies positive definiteness.
    d1 = F(1)
    l21, l31 = XY, xz
    d2 = 1 - l21 * l21 * d1
    l32 = (YZ - l31 * l21 * d1) / d2
    d3 = 1 - l31 * l31 * d1 - l32 * l32 * d2
    assert min(d1, d2, d3) > 0
    assert d1 * d2 * d3 == determinant
    beta_x = (XY - xz * YZ) / (1 - xz ** 2)
    beta_z = (YZ - xz * XY) / (1 - xz ** 2)
    independent_solution = gauss_jordan_solve([[F(1), xz], [xz, F(1)]], [XY, YZ])
    assert independent_solution == [beta_x, beta_z]
    partial = float(XY - xz * YZ) / math.sqrt(float((1 - xz ** 2) * (1 - YZ ** 2)))
    residual_covariance = XY - xz * YZ
    residual_x_variance = 1 - xz ** 2
    residual_y_variance = 1 - YZ ** 2
    partial_residual = float(residual_covariance) / math.sqrt(float(residual_x_variance * residual_y_variance))
    assert math.isclose(partial, partial_residual, rel_tol=0, abs_tol=1e-15)
    assert abs(partial) < 1
    truth = {"adjusted_x_coefficient": float(beta_x), "adjusted_z_coefficient": float(beta_z),
             "partial_correlation_xy_given_z": partial}
    law = {"family": "multivariate_gaussian", "column_order": ["x", "y", "z"],
           "means": [0, 0, 0], "sds": [1, 1, 1],
           "covariance": [[float(v) for v in row] for row in correlation], "truth": truth}
    check = {"sylvester_leading_principal_minors_exact": [str(v) for v in leading_minors],
             "ldlt_diagonal_exact": [str(d1), str(d2), str(d3)],
             "positive_definite": True, "determinant_exact": str(determinant),
             "normal_equation_solution_exact": {"adjusted_x_coefficient": str(beta_x),
                                                 "adjusted_z_coefficient": str(beta_z)},
             "closed_form_matches_exact_gauss_jordan": True,
             "partial_correlation_matches_residual_covariance_formula": True,
             "no_rows_generated": True}
    return law, check


def source_contract(case):
    checks = []
    for kind, target, tolerance in (("mean", 0.0, 0.10), ("sd", 1.0, 0.10)):
        for variable in ("x", "y", "z"):
            checks.append({"id": f"{kind}:{variable}", "kind": kind, "columns": [variable],
                           "target": target, "tolerance": tolerance})
    correlations = {"x,y": 0.30, "y,z": 0.60}
    if case == "task_a":
        correlations["x,z"] = 0.20
    for pair, target in correlations.items():
        checks.append({"id": f"correlation:{pair}", "kind": "correlation",
                       "columns": pair.split(","), "target": target, "tolerance": 0.05})
    return {
        "schema_version": "c4-source-contract-v1", "task_id": f"c4_{case}", "case_id": case,
        "mode": "whole_cohort", "n_rows": 4000, "row_id": "row_id",
        "population": "Explicitly invented three-measurement synthetic biomedical-surrogate population; no real persons, disease, tissue, treatment, or clinical interpretation.",
        "columns": [{"name": "row_id", "kind": "string", "unit": "", "role": "identifier", "nullable": False}]
                   + [{"name": v, "kind": "number", "unit": "synthetic_standardized_unit", "role": "generated", "nullable": False} for v in ("x", "y", "z")],
        "column_meanings": {v: f"Invented neutral surrogate measurement {v.upper()}; no actual biomarker or clinical meaning." for v in ("x", "y", "z")},
        "moments": {v: {"mean": 0.0, "sd": 1.0} for v in ("x", "y", "z")},
        "correlations": correlations,
        "joint_family": "multivariate_gaussian",
        "distribution_assumption": "Joint multivariate Gaussian is an admitted artificial construction assumption; it is not inferred from literature or patient evidence.",
        "marginals": {"x,y": {"family": "bivariate_gaussian", "correlation_key": "x,y"},
                      "y,z": {"family": "bivariate_gaussian", "correlation_key": "y,z"}},
        "source_uncertainty": {"kind": "exact_constructed_population_moments",
                               "explanation": "These values are exact definitions of an artificial population. They are not noisy study estimates, source standard errors, confidence intervals, or claims about biomedical truth."},
        "tolerances": {"mean_absolute": 0.10, "sd_absolute": 0.10, "correlation_absolute": 0.05},
        "tolerance_interpretation": "Precommitted engineering tolerances for finite synthetic tables on the standardized scale; not medical acceptance limits or source uncertainty.",
        "estimators": {"mean": "arithmetic", "sd_ddof": 1, "correlation": "Pearson"},
        "source_checks": checks, "source_check_order": [c["id"] for c in checks],
        "n_source_checks_per_table": len(checks),
        "protected_uses": [{"check_id": c["id"], "kind": "pearson_correlation", "variables": c["columns"]}
                           for c in checks if c["kind"] == "correlation"],
        "source_aggregate_loss": {"formula": "mean_over_every_fixed_check_and_every_election_seed((estimate - target)^2 / tolerance^2)",
                                  "denominator_checks_per_seed": len(checks), "denominator_election_seeds": 3,
                                  "exclude_or_drop_failed_checks": False, "failed_check_policy": "infinite_loss_and_numeric_gate_failure",
                                  "same_formula_for_all_methods": True},
        "numeric_source_gate": {"scope": "every_fixed_source_check_on_every_election_seed", "criterion": "absolute_error <= tolerance for each individual check", "fixed_denominator": len(checks) * 3},
        "protected_use_gate": {"scope": "every_admitted_correlation_on_every_election_seed",
                               "criterion": "absolute_error <= tolerance for each individual protected check",
                               "must_not_average_away_failures": True,
                               "proposal_adoption": "strict aggregate loss improvement over the initial candidate and all protected checks pass every election seed",
                               "fallback": "retain initial candidate and report its protected-use qualification flag"},
        "information_boundary": {
            "admitted_inputs": ["This exact source_contract.json artifact after controller registry admission"],
            "unknowns": ([] if case == "task_a" else ["The X,Z correlation and Gaussian copula parameter are unidentified by the admitted X,Y and Y,Z marginals; no value, sign, or independence may be asserted as source evidence."]),
            "identification": "All Gaussian parameters are admitted, so the joint artificial law is identified." if case == "task_a" else "The visible packet defines a family of compatible Gaussian joint laws, not one identified joint law.",
            "unreported_relationship_policy": "An author may derive general relationships from admitted information. Any extra unidentified parameter choice must be labeled as an assumption; unknown does not mean zero or independent.",
            "forbidden_inputs": ["custody directory", "hidden laws or evaluation operators", "held-out outcomes", "prior benchmark result files", "other candidates", "real patient data", "external web or paid API", "training data"],
            "not_permitted_as_feedback": "No hidden operator, answer, error, direction, score, or world-specific result may enter candidate construction or method selection.",
            "source_provenance": "New artificial benchmark fixture authored before candidate construction; no literature-derived claim.",
            "clinical_interpretation": "None; rows and population are wholly fictional and kept local."
        }
    }


def main():
    assert not (ROOT / "TASK_COMMITMENT.json").exists(), "Commitment already exists; never overwrite a frozen task"
    for case in ("task_a", "task_b"):
        dump(ROOT / "visible" / case / "source_contract.json", source_contract(case))
    cases, checks = {}, {}
    for case, worlds in LAW_XZ.items():
        cases[case] = {"worlds": {}}
        checks[case] = {}
        for world_id, xz in worlds.items():
            law, check = analyze_law(xz)
            cases[case]["worlds"][world_id] = law
            checks[case][world_id] = check
    a, b = (cases["task_b"]["worlds"][world]["truth"]["adjusted_x_coefficient"]
            for world in ("compatible_world_1", "compatible_world_2"))
    assert a > 0 > b and abs(a - b) > 0.40
    # Every visible source population check is exactly shared by both B worlds.
    for world in cases["task_b"]["worlds"].values():
        assert world["means"] == [0, 0, 0] and world["sds"] == [1, 1, 1]
        assert world["covariance"][0][1] == 0.30 and world["covariance"][1][2] == 0.60
    contract = {
        "schema_version": "c4-hidden-evaluation-contract-v1", "n_rows": 4000,
        "fixed_before_generator_execution": True, "candidate_feedback_forbidden": True,
        "reveal_condition": "All selectors for both tasks have been sealed and all 24 untouched-test tables have been generated, verified, and committed; root then audits reveal.",
        "no_outcome_selection": "Evaluate each final Task B table under both worlds; never choose a preferred world based on estimates, method, sign, or fit.",
        "cases": cases,
        "primary_endpoint": "adjusted_x_coefficient",
        "secondary_endpoints": ["adjusted_z_coefficient", "partial_correlation_xy_given_z"],
        "operators": {
            "adjusted_x_coefficient": {"operator": "OLS with intercept, y regressed on x and z", "coefficient": "x",
                                       "formula": "(s_xy*s_zz-s_yz*s_xz)/(s_xx*s_zz-s_xz^2)",
                                       "scale": "fixed artificial population-standardized measurement units; do not restandardize by sample SD"},
            "adjusted_z_coefficient": {"operator": "OLS with intercept, y regressed on x and z", "coefficient": "z",
                                       "formula": "(s_yz*s_xx-s_xy*s_xz)/(s_xx*s_zz-s_xz^2)",
                                       "scale": "fixed artificial population-standardized measurement units; do not restandardize by sample SD"},
            "partial_correlation_xy_given_z": {"operator": "Pearson correlation between centered x and y residuals after separate OLS projections on z with intercept",
                                               "formula": "(s_xy-s_xz*s_yz/s_zz)/sqrt((s_xx-s_xz^2/s_zz)*(s_yy-s_yz^2/s_zz))"},
            "s_ab": "sample covariance centered at sample arithmetic means with n-1 denominator; ratios cancel denominator"
        },
        "primary_scoring": {
            "report": ["signed_error", "absolute_error", "squared_error", "numerical_utility_score", "engineering_fidelity_band"],
            "utility_formula": "1/(1+(absolute_error/utility_scale)^2)", "utility_scale": 0.10,
            "absolute_error_bands": [
                {"upper_inclusive": 0.05, "label": "within_0.05"},
                {"upper_inclusive": 0.10, "label": "above_0.05_through_0.10"},
                {"upper_inclusive": 0.20, "label": "above_0.10_through_0.20"}],
            "above_all_bands_label": "above_0.20", "invalid_table_utility": 0.0,
            "interpretation": "Predeclared descriptive engineering numerical-fidelity bands only; no arbitrary clinical threshold, biomedical usefulness assertion, or hypothesis-test claim.",
            "direction": "Report positive/negative/zero and exact sign agreement separately; never replace magnitude error with direction success."
        },
        "secondary_scoring": "Report signed, absolute, and squared errors and direction separately for both secondary endpoints, under every world.",
        "world_summary": "Report all per-world endpoints; additionally report primary worst-world absolute error and min/max world error; assign no probability weights to worlds.",
        "task_b_identification_separation": {"primary_truth_absolute_difference": abs(a - b),
                                             "any_single_estimate_minimum_possible_worst_world_absolute_error": abs(a - b) / 2},
        "schedule": {"seeds": SEEDS, "total_generation_runs": 54, "initial_feedback_runs": 6,
                     "election_runs": 24, "untouched_test_runs": 24, "pool_size_per_task": 4,
                     "methods": ["baseline_retain", "minimum_aggregate_source_error", "source_protected_use_gate"],
                     "shared_candidate_pool": True, "test_all_pool_members": True,
                     "same_visible_packet_for_both_b_worlds": True},
        "invalid_endpoint_policy": "Record invalid table, null numerical errors and zero numerical utility. Do not silently drop the table, seed, endpoint, or world."
    }
    dump(HERE / "evaluate_contract.json", contract)
    dump(HERE / "analytical_checks.json", {
        "schema_version": "c4-analytical-checks-v1", "law_checks": checks,
        "compatible_b_worlds_have_identical_admitted_moments": True,
        "b_primary_coefficients_have_opposite_sign": True,
        "b_primary_truth_difference_exceeds_0_40": True,
        "methods": ["exact rational Sylvester principal minors", "independent exact rational LDL factorization",
                    "closed-form regression algebra checked with independent exact Gauss-Jordan solver",
                    "partial correlation checked by residual-covariance algebra"],
        "simulated_or_patient_rows_generated": 0, "candidate_programs_imported": 0,
        "prior_result_or_candidate_files_read": 0})
    ast.parse((HERE / "evaluate.py").read_text(encoding="utf-8"))
    admission = """# C4 task admission and frozen information boundary

This is a new controlled artificial benchmark. It does not contain real patients,
literature evidence, a medical target, or a claim of new biomedical discovery.
All three generated columns are invented neutral standardized measurements.
Each table contains exactly 4,000 local fictional rows in row_id,x,y,z order.

## Visible artifacts proposed for controller admission

- visible/task_a/source_contract.json: all means 0, all population SDs 1; Pearson
  population correlations X,Y = 0.30, Y,Z = 0.60, X,Z = 0.20. The admitted Gaussian
  family and these parameters fully identify its artificial joint law.
- visible/task_b/source_contract.json: the same means, SDs, X,Y and Y,Z marginals.
  The Gaussian X,Z dependence is explicitly unknown and unidentified. No value or
  independence assumption is admitted. There is one byte-identical visible packet
  for every compatible hidden world; candidates do not receive a world assignment.

The fixture custodian proposes these artifacts; the root/controller must inspect
and register their exact hashes using the harness registry before the author starts.
This document is not a fabricated registry approval. The source contract is a
synthetic source fixture, even if a harness compatibility enum says published_evidence.

## Source criteria and comparison

All constructed moments are exact artificial population definitions, not source
standard errors or confidence intervals. The table estimators are arithmetic means,
sample SDs (ddof=1), and Pearson correlations. Absolute tolerances are 0.10 for means,
0.10 for SDs, and 0.05 for correlations. These are engineering tolerances on this
standardized synthetic scale, not clinical acceptance limits.

The fixed denominator is every source check: 9 per Task A table and 8 per Task B
table. Aggregate loss is the arithmetic mean of squared error/tolerance over all
fixed checks and all three election seeds, using precisely the same formula for
every method. Missing, invalid, or failed checks cannot shrink the denominator;
they produce infinite loss and a failed numeric gate.

Protected uses are exactly every admitted correlation: three in A and two in B.
The use gate requires each protected error to be within its own tolerance on every
one of the three election seeds. It must not average away a failed seed or introduce
any unreported relationship. The full numeric source gate separately requires every
fixed source check to pass on all three election seeds. The protected-use method
adopts a proposal only with strict aggregate-loss improvement over the initial and
all protected checks passing; otherwise retain the initial and report its protected-use
qualification flag. The method controller fixes remaining comparison/tie rules
before election outputs are inspected.

The methods are baseline retain, minimum aggregate source error, and a
source-protected-use gate. Every method receives the same initial candidate and
three proposal opportunities. Retention and duplicate/no-op proposals are allowed;
the protocol never requires an intentionally poor baseline or artificial diversity.

## Fixed execution schedule

- Initial feedback seeds: 24101, 24103, 24107; 2 tasks x 1 initial x 3 = 6 runs.
- Election seeds: 24203, 24209, 24223; 2 tasks x 4 pool members x 3 = 24 runs.
- Untouched test seeds: 24301, 24307, 24317; 2 tasks x 4 pool members x 3 = 24 runs.
- Total 54 generation runs, each n=4,000. All 24 untouched-test tables remain in
  the fixed report, even when selectors choose the same candidate.

No rerun, discarded seed, outcome-selected world, extra proposal, web access,
paid API, training, or real patient data is authorized by this task packet.

## Custody and release

Hidden laws, analytical answers, endpoint operators, numerical-fidelity bands, and
scoring rules are fixed inside custody before candidate construction. They must not
be read by the author, selectors, or feedback controller before both task selections
are sealed. Held-out operators, values, errors, signs, scores and world-specific
results are never candidate feedback. The root may inspect this admission document,
visible source contracts and hash-only commitment metadata without opening custody.

The custodian analytically verified positive definiteness and algebra without
generating rows or importing candidate code. TASK_COMMITMENT.json binds the visible
and hidden artifacts. Reveal and export of the hidden truth/evaluator are permitted
only after selector sealing, all untouched-test table commitments, and root audit.
All compatible hidden worlds are reported; no probability weights or preferred
world are inferred. Numeric fidelity and direction are reported separately and
neither establishes clinical usefulness, causality, or population transport.
"""
    (ROOT / "TASK_ADMISSION.md").write_text(admission, encoding="utf-8")
    visible = {str(p.relative_to(ROOT)).replace("\\", "/"): digest(p)
               for p in sorted((ROOT / "visible").rglob("*.json"))}
    hidden = {str(p.relative_to(ROOT)).replace("\\", "/"): digest(p)
              for p in sorted(HERE.iterdir()) if p.is_file()}
    commitment = {
        "schema_version": "c4-task-commitment-v1",
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "state": "frozen_before_author_start_and_any_generator_run",
        "source_origin": "new_explicitly_invented_artificial_fixture",
        "visible_artifacts": visible, "hidden_artifacts": hidden,
        "admission_document_sha256": digest(ROOT / "TASK_ADMISSION.md"),
        "n_rows": 4000, "case_ids": ["task_a", "task_b"],
        "seeds": SEEDS,
        "fixed_counts": {"initial_feedback": 6, "election": 24, "untouched_test": 24, "total": 54},
        "hidden_analysis_count": {"primary": 1, "secondary": 2},
        "source_checks_per_case": {"task_a": 9, "task_b": 8},
        "all_hidden_laws_positive_definite": True,
        "hidden_analytical_checks_passed": True,
        "fixture_authoring_generated_rows": 0,
        "registry_admission_status": "proposed_for_root_controller_review_and_registration",
        "mutation_policy": "Never overwrite this commitment or any bound file. Any correction requires explicit new version before author access, with previous commitment retained.",
        "reveal_policy": "After all selectors sealed, all 24 untouched-test outputs committed, and root audit; never supply hidden material as candidate feedback."
    }
    dump(ROOT / "TASK_COMMITMENT.json", commitment)
    print(json.dumps({"status": "frozen", "task_commitment_sha256": digest(ROOT / "TASK_COMMITMENT.json"),
                      "visible_artifacts": visible, "hidden_artifact_count": len(hidden),
                      "analytical_checks_passed": True, "generated_rows": 0}))


if __name__ == "__main__":
    main()
