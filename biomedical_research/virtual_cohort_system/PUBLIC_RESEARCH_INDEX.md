# Research index for the KDD working manuscript

**Which Scientific Analyses Can Agent-Generated Biomedical Cohorts Support?** KDD Research working manuscript v0.38, 19 November 2026.

[Paper and supplement (PDF)](manuscript/kdd_draft_v38_2026-11-19/paper.pdf) · [Manuscript text](manuscript/kdd_draft_v38_2026-11-19/main.tex) · [Overleaf project](manuscript/kdd_draft_v38_2026-11-19/overleaf_v38.zip) · [Numerical and build checks](manuscript/kdd_draft_v38_2026-11-19/BUILD_CHECK.json)

Figure 1 compares the scientific analyses across cohorts. Table 2 on page 6 examines the original evidence, a statistical comparator and the six original-evidence agent laws. Figure 3 and Appendix Table 3 show the paired revisions given one extra statistic. [Figure source](reproducibility/plot_v37.py) · [Numerical verification](reproducibility/check_v38.py)

## What the A tables and within-band pairing each contribute

A statistical model reproducing the CHNS A summaries gave a pooled Hb–ferritin rank correlation of 0.237, compared with 0.317 in the B communities. The six original-evidence agents gave 0.293–0.320. Re-pairing each agent's records within Hb band gave expected correlations of 0.244–0.249 and preserved every threshold count. The study used one conventional law and three new 12,000-row draws after B had been disclosed. [All estimates and checks](work/chns_statistical_comparator_2026-11-19/RESULTS.md) · [Fixed comparator specification](work/chns_statistical_comparator_2026-11-19/PROTOCOL.md)

The [v0.36 contribution review](work/kdd_v36_contribution_review_2026-11-19/REVIEW.md) places blood pressure and iron status side by side. A reproducible rearrangement of the frozen iron comparator shows how much rank correlation can change while all 16 reported source checks stay fixed.

## Conditional evidence in held-out CHNS communities

Six initial authors and their matched revisions generated iron-status cohorts for two scientific analyses. Among 1,082 women in the sealed communities the Hb–ferritin rank correlation was 0.317. Adding a within-band statistic yielded 0.297–0.304 across six revised laws. All six met both planning tolerances. Neither arm met the prespecified threshold for incremental improvement. Only one of six revisions moved closer on the prespecified whole-cohort rank analysis. In the post hoc decomposition all six improved the middle band's contribution. [Study and figure](work/chns_iron_conditional_holdout_2026-11-19/RESULTS.md) · [Frozen design](work/chns_iron_conditional_holdout_2026-11-19/PROTOCOL.md) · [Independent verification](work/chns_iron_conditional_holdout_2026-11-19/VERIFICATION.json)

## Prospective iron-status test from an original article

Seven agent laws passed the 16 prespecified source checks after the recorded parameter-binding correction. The source threshold odds ratio stayed near 6.65 while continuous rank correlations ranged from −0.272 to +0.446. The external survey had 44 complete cases and no measured low-ferritin participant. Appendix Figure 6, Table 5 and the study report give all completed and incomplete arms. [Experimental report](work/original_paper_iron_sensitivity_2026-11-19/RESULTS.md) · [Model programs](work/original_paper_iron_sensitivity_2026-11-19/laws) · [Independent numerical review](work/original_paper_iron_sensitivity_2026-11-19/SCIENTIFIC_VERIFICATION.json)

## Prospective validation in v0.35

A new screening cohort from Freetown was held until the Agent's two laws and the statistical comparator were public. The two Agent laws matched the same source moments and implied different screening workloads. The released target shows zero discordant threshold pairs across 1,244 eligible people. [Results and two-panel figure](work/prospective_bp_freetown_2026-11-18/RESULTS.md) · [Reference field audit](work/prospective_bp_freetown_2026-11-18/REFERENCE_AUDIT.json)

## Experiments behind the paper

| Study | What to inspect |
| --- | --- |
| [Original papers to virtual cohorts](work/original_paper_capability_2026-11-17/RESULTS.md) | Six Agent constructions from original blood-pressure and iron studies. Inspect extracted evidence, model choices and the reference estimates. |
| [Real and virtual samples of matched size](work/matched_size_utility_2026-11-17/RESULTS.md) | Nine lifestyle contrasts under the same sample-size and analysis rules. The real-to-real comparison provides a sampling benchmark. |
| [Joint evidence for blood pressure](work/pns_evidence_content_control_2026-11-16/RESULTS.md) | Adding a reported joint statistic improved residual dependence. The report also gives both BMI slopes. |
| [Joint evidence for iron status](work/iron_evidence_content_control_2026-11-16/RESULTS.md) | A published threshold table improved the odds-ratio analysis. Rank association and joint prevalence are evaluated separately. |
| [Search for joint lipid evidence](work/lipid_joint_evidence_2026-11-16/RESULTS.md) | Evidence admission ended before cohort generation. The report records the reason. |
| [Request-only Agent and workflow](work/request_only_repeatability_2026-11-11/RESULTS.md) | Both arms start with a study request. The report tracks final analyses and costs across independent sessions. |
| [Checks and revision](work/scientific_check_revision_2026-11-11/RESULTS.md) | Mathematical, physiological and joint-structure checks, including unchanged programs and results. |
| [Controlled evidence composition](work/evidence_composition_pilot_2026-11-16/RESULTS.md) | An artificial-population experiment with known moments, reported separately from biomedical comparisons. |

For the original-paper experiment, open the [per-construction results](work/original_paper_capability_2026-11-17/analysis/author_results.csv), [source and model audit](work/original_paper_capability_2026-11-17/SOURCE_MODEL_AUDIT.md) and [tool and cost summary](work/original_paper_capability_2026-11-17/audit/TRACE_SUMMARY.json). Each seed measures sampling variation within a construction.

## Files for numerical review

The [verification code](work/manuscript_integration_v34_2026-11-18/verify.py) checks manuscript values and plotted coordinates against released aggregate files. The [figure script](work/manuscript_integration_v34_2026-11-18/plot_analyses.py) draws the two primary result figures. The Overleaf archive contains the TeX source and five figure PDFs.

Reading or checking the reported estimates uses the public summaries. Regenerating measured reference estimates requires access to the original cohorts under their respective terms. Generating new virtual cohorts requires the appropriate public task inputs and, for new Agent sessions, model access. The public snapshot includes model programs, analysis code, methodological decisions, failures, reviewed aggregate outputs and per-construction costs where recorded. Participant-level measured and generated records, full API transcripts, private review correspondence, credentials and third-party full texts stay outside this release.

## Directory index

The following 36 dated work directories cover experimental runs, evidence audits, manuscript integration and scientific-use review from 10 to 18 November. A directory can contain several runs or only editorial work. Older curated reports are in [the historical report directory](reports/).

- [biomedical_review_v31_2026-11-11](work/biomedical_review_v31_2026-11-11/RESULTS.md)
- [cross_model_api_pilot_2026-11-10](work/cross_model_api_pilot_2026-11-10/RESULTS_SUMMARY.md)
- [economy_feedback_pilot_2026-11-10](work/economy_feedback_pilot_2026-11-10/RESULTS_SUMMARY.md)
- [evidence_composition_pilot_2026-11-16](work/evidence_composition_pilot_2026-11-16/RESULTS.md)
- [evidence_indirectness_review_2026-11-11](work/evidence_indirectness_review_2026-11-11/DESIGN_CRITIQUE.md)
- [html_report_refresh_2026-11-11](work/html_report_refresh_2026-11-11/RESULTS.md)
- [iron_evidence_content_control_2026-11-16](work/iron_evidence_content_control_2026-11-16/RESULTS.md)
- [kdd_first_paper_plan_2026-11-17](work/kdd_first_paper_plan_2026-11-17/PLAN_VERIFICATION.json)
- [lifestyle_application_2026-11-11](work/lifestyle_application_2026-11-11/RESULTS.md)
- [lipid_joint_evidence_2026-11-16](work/lipid_joint_evidence_2026-11-16/RESULTS.md)
- [llmsynthor_comparator_audit_2026-11-17](work/llmsynthor_comparator_audit_2026-11-17/FEASIBILITY.md)
- [manuscript_integration_v30_2026-11-11](work/manuscript_integration_v30_2026-11-11/RESULTS.md)
- [manuscript_integration_v31_2026-11-11](work/manuscript_integration_v31_2026-11-11/RESULTS.md)
- [manuscript_integration_v32_2026-11-16](work/manuscript_integration_v32_2026-11-16/RESULTS.md)
- [manuscript_integration_v33_2026-11-17](work/manuscript_integration_v33_2026-11-17/RESULTS.md)
- [manuscript_integration_v34_2026-11-18](work/manuscript_integration_v34_2026-11-18/QA.json)
- [manuscript_revision_v28_2026-11-10](work/manuscript_revision_v28_2026-11-10/RESULTS.md)
- [manuscript_revision_v29_2026-11-11](work/manuscript_revision_v29_2026-11-11/RESULTS.md)
- [matched_size_utility_2026-11-17](work/matched_size_utility_2026-11-17/RESULTS.md)
- [original_paper_capability_2026-11-17](work/original_paper_capability_2026-11-17/RESULTS.md)
- [parameter_attribution_2026-11-10](work/parameter_attribution_2026-11-10/ATTRIBUTION_MASTER.md)
- [pns_evidence_content_control_2026-11-16](work/pns_evidence_content_control_2026-11-16/RESULTS.md)
- [pns_joint_evidence_2026-11-16](work/pns_joint_evidence_2026-11-16/RESULTS.md)
- [provenance_audit_materials_2026-11-11](work/provenance_audit_materials_2026-11-11/README.md)
- [published_analysis_replay_2026-11-11](work/published_analysis_replay_2026-11-11/RESULTS.md)
- [request_only_agent_capacity_2026-11-10](work/request_only_agent_capacity_2026-11-10/RESULTS.md)
- [request_only_agent_pilot_2026-11-10](work/request_only_agent_pilot_2026-11-10/RESULTS.md)
- [request_only_agent_repair_2026-11-10](work/request_only_agent_repair_2026-11-10/RESULTS.md)
- [request_only_repeatability_2026-11-11](work/request_only_repeatability_2026-11-11/RESULTS.md)
- [review_claim_audit_2026-11-15](work/review_claim_audit_2026-11-15/ASSESSMENT.md)
- [scientific_check_revision_2026-11-11](work/scientific_check_revision_2026-11-11/RESULTS.md)
- [scientific_use_acceptance_2026-11-16](work/scientific_use_acceptance_2026-11-16/RESULTS.md)
- [scientific_use_review_v30_2026-11-11](work/scientific_use_review_v30_2026-11-11/RESULTS.md)
- [source_role_audit_2026-11-15](work/source_role_audit_2026-11-15/RESULTS.md)
- [two_round_synthesis_2026-11-10](work/two_round_synthesis_2026-11-10/RESULTS_SUMMARY.md)
- [v33_core_review_2026-11-17](work/v33_core_review_2026-11-17/REVIEW.md)

### Additional earlier records included in this release

- [adaptive_reference_pilot_2026-11-03](work/adaptive_reference_pilot_2026-11-03/RESULTS.md)
- [agent_diagnosis_2026-11-04](work/agent_diagnosis_2026-11-04/EVIDENCE_GAPS.md)
- [agent_positioning_review_2026-11-05](work/agent_positioning_review_2026-11-05/DECISION_RESPONSE_ZH.md)
- [analysis_use_rubric_2026-11-09](work/analysis_use_rubric_2026-11-09/INTEGRATION_RECOMMENDATION.md)
- [chns_admission_2026-11-01](work/chns_admission_2026-11-01/ACQUISITION_AND_LINKAGE_RESULTS.md)
- [conditional_evidence_2026-11-09](work/conditional_evidence_2026-11-09/finalize_audit.py)
- [core_highlight_2026-11-02](work/core_highlight_2026-11-02/RESULTS.md)
- [evidence_gap_actions_2026-11-05](work/evidence_gap_actions_2026-11-05/RESULTS_ZH.md)
- [existing_data_benchmark_2026-11-02](work/existing_data_benchmark_2026-11-02/CONSTRUCTION_EVIDENCE_AUDIT.md)
- [independent_v26_review_2026-11-09](work/independent_v26_review_2026-11-09/METHOD_REVIEW.md)
- [m15a_direct_rows_2026-10-30](work/m15a_direct_rows_2026-10-30/CONTROLLER_RUNBOOK.md)
- [m2-controlled-agent](work/m2-controlled-agent/TASK_BRIEF.md)
- [manuscript_consolidation_2026-11-04](work/manuscript_consolidation_2026-11-04/METHOD_AND_RERUN_AUDIT.md)
- [manuscript_focus_v26_2026-11-09](work/manuscript_focus_v26_2026-11-09/METHOD_COVERAGE.md)
- [manuscript_revision_v27_2026-11-09](work/manuscript_revision_v27_2026-11-09/INDEPENDENT_REVIEW.md)
- [next_case_validation_2026-11-09](work/next_case_validation_2026-11-09/AUTHOR_TASK_TEMPLATE.md)
- [quality_attribution_2026-11-04](work/quality_attribution_2026-11-04/RESULTS_ZH.md)
- [retrieval_validation_analysis_2026-11-09](work/retrieval_validation_analysis_2026-11-09/LOCAL_CHECK_AUDIT.md)
- [rubric_case_pilot_2026-11-09](work/rubric_case_pilot_2026-11-09/PROCESS_REVIEW.md)
- [source_increment_revision_2026-11-05](work/source_increment_revision_2026-11-05/RESULTS_ZH.md)
- [strengths_synthesis_2026-11-09](work/strengths_synthesis_2026-11-09/RESULTS_AND_FOCUS.md)
- [supplement_probe_2026-11-05](work/supplement_probe_2026-11-05/RESULTS_ZH.md)

The [release manifest](PUBLIC_SYNC_v34_SHA256.tsv) lists the screened research files added or changed since the 9 November snapshot, with byte counts and SHA-256 digests. Generated navigation pages and the manifest itself are outside its scope.
