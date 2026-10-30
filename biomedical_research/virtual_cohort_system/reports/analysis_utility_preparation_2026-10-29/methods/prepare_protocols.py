"""Write preparation-stage protocols and equal-information Agent instructions.

Reads no target rows. Final release and executable candidate commitments are
separate gates. Re-running overwrites only these explicitly unexecuted protocols.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    common = {
        "schema_version": "m9-analysis-preparation-1",
        "status": "specified_before_target_analysis_not_a_release_authorization",
        "primary_estimands": [
            {"id": "adjusted_age_per10", "model": "adjusted", "coefficient": "A", "multiplier": 1},
            {"id": "adjusted_bmi_per5", "model": "adjusted", "coefficient": "B", "multiplier": 1},
            {"id": "bmi_curvature_second_difference", "model": "bmi_curve", "coefficient": "B_squared", "multiplier": 2,
             "meaning": "Quadratic projection contrast at BMI35 minus twice BMI30 plus BMI25, conditional on other covariates; not proof of a full biological curve"},
            {"id": "female_minus_male_bmi_slope_per5", "model": "sex_bmi", "coefficient": "female_times_B", "multiplier": 1}
        ],
        "expected_directions": None,
        "transforms": {"A": "(age-50)/10", "B": "(bmi-25)/5", "F": "1 if sex=2 else 0"},
        "secondary_estimands": ["adjusted_female_minus_male", "18 age-sex-BMI cell arithmetic means"],
        "cells": {"age": [[20,40],[40,60],[60,80]], "age_upper_exclusive": True,
                  "sex": [1,2], "bmi": ["0<bmi<25", "25<=bmi<30", "bmi>=30"],
                  "empty": "retain as nonestimable", "sparse": "flag n<30 without merging or dropping"},
        "weighted_fit": "Positive provided design weights normalized by their mean; WLS via weighted least squares; same point estimator for real and generated values",
        "point_script": "methods/analytical_points.py",
        "missingness": "Eligibility fixed by preparation; no endpoint-specific outcome imputation, winsorization or favorable-case removal",
        "reporting": {
            "direction": "Point-direction agreement for estimable primary contrasts, reported with magnitudes; do not count positive means as sign success",
            "magnitude": "Difference in the endpoint's scientific units; no universal mixed-unit score or posthoc tolerance",
            "conclusion": "No supported/absent-effect or equivalence category without an appropriate reference inference procedure and prespecified substantive criterion",
            "synthetic_uncertainty": "No ordinary synthetic-data standard error interpreted as evidence uncertainty; residual ranges labelled Monte Carlo only",
            "nonestimable": "Retain every planned endpoint and construction failure",
            "multiplicity": "Descriptive screen, no confirmatory binary superiority claim; primary family fixed before generation"
        },
        "source_overlap_classification": "Must be independently assigned per endpoint after packet admission and before generation: supplied / algebraic consequence / unprovided target analysis / assumption-dependent",
        "release_gates": ["source packet independently admitted and hashed", "visible task/observations validated and hashed",
                          "endpoint/source-overlap map frozen", "all arms and construction/draw schedule fixed",
                          "initial and final candidates frozen", "isolated generation receipts pass",
                          "evaluation code and inference scope fixed", "custodian reference hashes unchanged"],
        "boundaries": "Evaluation-only; builder receives scientific use brief, not this exact endpoint list or hidden answers. Procedural Agent separation, generator sandbox only. No guarantee against pretraining knowledge."
    }
    insulin = common | {
        "case_id": "nhanes_insulin", "outcome": "fasting_insulin_uU_ml", "outcome_transform": "natural_log",
        "covariate_adapter": {"age_years":"age", "bmi_kg_m2":"bmi", "fasting_glucose_mg_dl":"glucose_mg_dl", "sex":"sex", "row_id":"record_id_index"},
        "sex_value_adapter": {"male": 1, "female": 2},
        "additional_transform": "G=natural_log(glucose_mg_dl/100)",
        "models": {"adjusted": "log(insulin)=intercept+A+B+F+G", "bmi_curve": "log(insulin)=intercept+A+B+F+G+B_squared", "sex_bmi": "log(insulin)=intercept+A+B+F+G+F_times_B"},
        "reference_inference": "NHANES full-design domain Taylor inference planned using positive fasting weights, strata andPSU; adapter must be reviewed and frozen before any reference outcome analysis. Current point module alone does not implement this.",
        "derived_use": {"name": "HOMA1_IR", "formula": "insulin_uU_ml * glucose_mg_dl / 405", "estimand": "weighted arithmetic mean", "status": "derived use demonstration, not additional independent truth",
                        "algebraic_caveat": "Under log-linear analyses adjusting log glucose, several HOMA1 associations are algebraic re-expressions of insulin associations; do not count twice",
                        "reference": "https://pubmed.ncbi.nlm.nih.gov/3899825/", "universal_threshold": None}
    }
    pns = common | {
        "case_id": "pns_hba1c", "outcome": "hba1c_pct", "outcome_transform": "identity",
        "covariate_adapter": {"age_years":"age", "bmi_kg_m2":"bmi", "sex":"sex", "row_id":"record_id_index"},
        "sex_value_adapter": {"male": 1, "female": 2},
        "outcome_domain": "Analyze every finite HbA1c value without target-magnitude exclusions; separately review physiological invalidity of generated values rather than silently dropping rows",
        "models": {"adjusted": "HbA1c_percent=intercept+A+B+F", "bmi_curve": "HbA1c_percent=intercept+A+B+F+B_squared", "sex_bmi": "HbA1c_percent=intercept+A+B+F+F_times_B"},
        "reference_inference": "Point estimates under supplied peso_lab and unweighted sensitivity; no design-based CI because released laboratory workbook lacks PSU/strata. Do not manufacture independent-row survey CIs.",
        "target_interpretation": "Eligible complete laboratory participants under the supplied weights; national-population inference and peso_lab calibration remain unresolved",
        "unweighted_sensitivity": "Run same complete endpoint family with every weight=1, labelled sensitivity and never select preferred analysis after outcomes",
        "measurement": "C008 baseline IBGE age, baseline anthropometry versus later 2014-15 HbA1c collection; not necessarily same-visit contemporaneous association",
        "forbidden_predictors": ["Z034", "Z035", "HbA1c-derived diagnosis", "other HbA1c-derived fields"]
    }
    write_json(ROOT / "protocols/nhanes_insulin.json", insulin)
    write_json(ROOT / "protocols/pns_hba1c.json", pns)
    campaign = {
        "schema_version": "m9-comparison-preparation-1", "status": "task_preparation_no_constructions_or_target_evaluations_run",
        "cases": ["nhanes_insulin", "pns_hba1c"],
        "arms": {"structured": {"independent_constructions":2}, "ordinary": {"independent_constructions":2}, "statistical": {"independent_constructions":1, "deterministic_fit":True}},
        "route": "executable program for first comparison; direct-row generation remains separate extension",
        "residual_seeds": [92101,92102,92103], "source_replay_seeds": [91101,91102,91103],
        "scheduled_final_tables":30,
        "same_information": ["identical observed rows", "identical admitted source artifact and numeric extraction bytes", "same broad scientific use", "same source-check and execution interfaces"],
        "construction_limits": {"candidate_versions":3, "revisions":2, "literature_queries":0, "literature_downloads":0,
                                "source_replays_per_version":3, "source_contexts_per_replay_maximum":3},
        "model_budget": {"require_same_base_model_and_settings":True, "record_exact_model_identifier_before_launch":True,
                         "token_and_wall_time_metering":"not provided by current harness; record caller metadata if available, otherwise mark unavailable",
                         "strict_token_budget_equivalence_established":False,
                         "interpretation":"Matching evidence/steps is not proof of matching token cost. No cost-adjusted or strict compute-matched superiority claim without actual accounting."},
        "selection":"Prespecify source-only candidate selection; evaluate every independent final construction, not best-of-two. Initial and final remain available for later revision attribution.",
        "statistical_arm":"Choose transparent parametric/copula family based only on admitted evidence and accessible source contexts; numerical calibration only, no targetY or hand-fixed desired relationships. Exact family and underidentification rule must be frozen before launch.",
        "prepared_inputs":["both visible task datasets", "curated numeric evidence with item restrictions", "endpoint/source-overlap map", "common point estimator with invented tests"],
        "readiness_not_yet_claimed":["conventional family specification", "execution runtime bindings", "model identity/budget records", "NHANES variance adapter"],
        "retrieval_track":"Separate later experiment, because curated shared packets isolate evidence use rather than autonomous search",
        "future_ablation":"Review-disabled additional12tables only if useful; selection after screen is exploratory and confirmation needs fresh tasks",
        "prohibited":["hidden target feedback to construction", "tuning on released targets", "discarding failed or unfavorable constructions", "treating residual seeds or correlated endpoints as independent tasks"]
    }
    write_json(ROOT / "protocols/campaign.json", campaign)
    prompts = ROOT / "prompts"
    prompts.mkdir(exist_ok=True)
    common_brief = """# Common task brief

Generate the entirely unmeasured biomarker for the provided observed rows using only the task's admitted external research evidence. Preserve observed values and record order. Produce an executable generator and the existing harness-required evidence, specification, parameter provenance, assumptions and check records. No scientific effect direction is required.

The output is intended for several downstream association, nonlinear and subgroup analyses. Hidden target outcomes, exact reserved analysis specifications and their answers are unavailable. Identifiers and row order/count are not biological predictors. Do not link records to public microdata or consult prior runs, other constructions, custodian files or excluded target-cohort papers. The scientific relationship and its strength are your choices, supported by evidence or explicit assumptions.

You receive the same source packet and tools as the other methods. At most three candidate versions, two revisions and three prespecified source-replay seeds per version are allowed. Freeze before execution. Select a final version using source evidence and permitted diagnostics only; document the rule before examining diagnostics. A justified no-op or unsupported relation is acceptable. Do not infer statistical certainty from three draws or enlarge the table to manufacture evidence. Never run generator code on the host if the supplied isolated runtime fails.

This task is not yet dispatched. Exact model/runtime/budget bindings and source admission must be completed first.
"""
    (prompts / "common.md").write_text(common_brief, encoding="utf-8")
    (prompts / "ordinary.md").write_text("""# Ordinary capable Agent construction

Follow common.md and the task contract. Use your own analysis and coding approach, including checking and revision, to construct the best justified reusable generator within the common budget. You may question source applicability, compare structures and retain a prior version. All source and numerical tools available to the structured workflow are also available to you. No imposed evidence-map or separate reviewer format is required. Report actual work and unresolved assumptions.
""", encoding="utf-8")
    (prompts / "structured.md").write_text("""# Structured evidence and review construction

Follow common.md and the task contract. Before choosing a generator, map each used statistic to its population, measurement, selection, adjustment and scale; distinguish individual residual variation from study heterogeneity. Record consequential gaps and scientifically different compatible structures. Choose structures yourself rather than copying a case-specific harness formula.

Check statistics under their source conditions where executable; preserve unsupported operators as noncomputable. A reviewer examines extraction, transformations, dependencies, source-to-target assumptions and whether supplied source facts genuinely constrain the intended uses. Give the reviewer only admitted evidence, the candidate and source diagnostics. Revise, retain or stop based on these findings. Use the same total construction limits as the ordinary Agent; a review role is not permission for extra unlimited generation. Preserve initial and final programs and the actual feedback.
""", encoding="utf-8")
    (prompts / "review.md").write_text("""# Source-only review rubric

Check against admitted full-text locators: arithmetic versus geometric quantities; SE versus SD; standardized versus raw coefficients; conditional versus marginal estimates; mean versus median; paired-study heterogeneity versus individual variation; shared-cohort evidence; assay and population transfer. Check coding units, transformations, positivity, preserved observed fields, and scientific assumptions behind interpolation and dependence. A missing relation is not a zero coefficient.

Name a concrete error with an evidence or code locator and its scientific consequence, or state that no supported correction is available. Do not demand a desired age/BMI sign. Do not use hidden target statistics, prior target results, other arm candidates or external searches outside the packet. Review recommendations are not proof of improved scientific utility.
""", encoding="utf-8")
    print(json.dumps({"status":"protocols_and_prompts_written", "target_rows_read":False, "scientific_generation_run":False}))


if __name__ == "__main__":
    main()
