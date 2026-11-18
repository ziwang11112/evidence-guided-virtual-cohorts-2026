# Two-case scientific-use brief: content and assembly outline

11 November 2026. Prepared for a new, short external biomedical interpretation brief. No reviewer has been contacted; completed responses remain zero. This task did not open participant/generated rows, run models, recompute analyses or modify the older reviewer packages.

## Purpose and reading order

The missing decision is which **specific exploratory analyses** a biomedical reader would use, restrict or reject, given the complete results and modeling assumptions. We are not asking for another paper-venue review, an AI superiority judgment, a provenance scoring experiment or a general endorsement of synthetic patients.

Suggested compact package: a short introduction, one page per case, and the blank [review questions](REVIEWER_QUESTIONS.md). If a case page cannot legibly contain all authors, use an extra page rather than omit a weak author. Provide source/implementation links as optional detail. The first-pass material should not require reading the full manuscript or Python code. Aggregate results suffice for this review; no individual records are needed.

Selection is role-based and explicit: Case A tests a useful adjustment pattern with reduced dispersion; Case B tests joint-biomarker analysis with an unresolved dependence limitation. These are two illustrative completed cases, not a representative clinical sample, independent new validation or a blinded case-selection experiment. All authors and intended analyses within each chosen case remain visible.

## Case A: Q4 ENSANUT glycemia, E01 and E02

**Research use.** Explore how age and BMI associate with HbA1c, and how adding glucose changes the BMI coefficient. The target reference is the selected ENSANUT 2018 adult sample: ages 25-79, no reported previous diabetes diagnosis, recorded fasting duration 8-12 hours and serum glucose below 126 mg/dL, with equal mass in eight sex-by-age cells. It is not a nationally weighted regression for all Mexican adults or a diagnostic population. Source definitions and exact eligibility should accompany the brief, not be inferred from the cohort name.

**What the Agent received and produced.** Population/measurement definitions and intended analyses, without target records/results or bibliographic seeds. E01 and E02 independently selected external evidence and authored complete five-variable laws: age, recorded sex, BMI, glucose and HbA1c. Each selected law supplied three final 3,000-row tables, six tables for this selected case. These are two constructions, not six clinical studies. Both retained their initial model. The historical authoring setup differs from the later captured API launcher.

**Main display: all three requested analyses.** Values below are already reported means and seed ranges, not newly fitted results. HbA1c coefficients are percentage points (pp), not relative percent change.

| Analysis | E01 mean [seed range] | E02 mean [seed range] | Existing sample estimate |
|---|---:|---:|---:|
| Age, adjusted for sex/BMI/glucose; pp per decade | 0.10308 [0.10155, 0.10431] | 0.09772 [0.09495, 0.09913] | 0.07513 |
| BMI, adjusted for age/sex; pp per 5 kg/m² | 0.09165 [0.08994, 0.09441] | 0.07140 [0.07123, 0.07156] | 0.08364 |
| BMI, additionally adjusted for glucose; pp per 5 kg/m² | 0.07509 [0.07201, 0.07666] | 0.04733 [0.04502, 0.04859] | 0.05664 |

Include all individual seed estimates or their existing figure when available; ranges are sampling under a law, not confidence in its transfer. If plotting the reference uncertainty, use the saved ENSANUT empirical cluster-resampling stability bands. Do not replace them with acceptance zones or invented confidence intervals.

**Necessary diagnostics.** Both laws show BMI-coefficient attenuation after glucose adjustment, while both age effects are stronger than the sample estimate. Report HbA1c SD approximately 0.362/0.406 pp versus 0.527 and full-model residual RMS approximately 0.295/0.324 versus 0.488. These are E01/E02 values from the frozen diagnostic report. The positive pattern does not imply correct individual heterogeneity, causal mediation, uncertainty coverage or valid power calculations.

**Modeling assumptions to summarize.** E01 uses bounded beta BMI/glucose with conditional gamma HbA1c; E02 uses lognormal BMI, conditionally truncated-normal glucose and positive conditional-mean lognormal HbA1c. Conditional dependence, residual allocation and transport are modeling assumptions, not recovered participant physiology. All four Q4 laws passed their stated finite-moment review; that does not certify target tails. Ask the expert which measurement/selection or biological issue changes the permitted exploratory use, rather than asking them to re-prove implementation mathematics.

**Source of every displayed number:** [Q4 RESULTS](../core_workflow_replication_2026-11-04/RESULTS.md), [primary summary](../core_workflow_replication_2026-11-04/display/PRIMARY_SUMMARY.csv), [complete diagnostics](../core_workflow_replication_2026-11-04/display/ALL_DIAGNOSTICS.md). Optional source audit: [E01](../core_workflow_replication_2026-11-04/SOURCE_PROPOSAL_REVIEW_E01.md), [E02](../core_workflow_replication_2026-11-04/SOURCE_PROPOSAL_REVIEW_E02.md), [E02 transcription addendum](../core_workflow_replication_2026-11-04/SOURCE_PROPOSAL_REVIEW_E02_ADDENDUM.md). The package builder should bind exact aggregate versions/hashes and check numbers against its independent audit before export.

## Case B: request-only lipid construction, all six authors

**Research use.** Explore age/sex-adjusted BMI associations with TC and HDL and their residual relationship after age, sex and BMI adjustment. The intended context is adult Turkana-context lipid biology as specified in the frozen request and selected reference; it is not an arbitrary pan-African population. Include exact reference eligibility, measurement and source-population distinctions from the independent biological audit. Do not invent treatment/fasting eligibility absent from the supplied record.

**What was generated.** Six fresh sessions, three ordinary and three workflow authors, started with the same request and GPT/tools without prepared papers or target estimates. Each produced three 3,000-row tables: eighteen tables and 54 primary seed estimates for this lipid subset. Every author selected its first submitted law. All six are shown below; the ordinary/workflow labels identify origin, not quality ranks.

| Constructor | BMI-TC slope | BMI-HDL slope | Residual TC-HDL correlation | TC SD | HDL SD |
|---|---:|---:|---:|---:|---:|
| LIPID_BASE_R1 | 8.8287 | -1.1546 | 0.3308 | 37.8013 | 11.9592 |
| LIPID_BASE_R2 | 14.6148 | -1.4896 | 0.3590 | 36.6868 | 13.1331 |
| LIPID_BASE_R3 | 12.3831 | -2.3124 | 0.4233 | 35.7716 | 11.9587 |
| LIPID_WORKFLOW_R1 | 9.9313 | -1.3482 | 0.1456 | 32.9360 | 11.3752 |
| LIPID_WORKFLOW_R2 | 13.3370 | -0.0116 | 0.3560 | 42.1900 | 13.1809 |
| LIPID_WORKFLOW_R3 | 8.8104 | -1.4142 | 0.3193 | 39.2089 | 12.2797 |
| Existing sample reference | 5.6831 | -4.6230 | 0.5121 | 42.8466 | 20.1756 |

These are three-seed means. BMI slopes are mg/dL per 5 kg/m²; SDs are sample SDs in mg/dL. The fixed evaluation uses the recorded 38.67 conversion from mmol/L. Preserve the complete seed profiles in the figure or appendix. Existing reference intervals for the slopes are HC3 normal-assumption conditional sensitivity intervals, not general population/transport confidence intervals; the TC interval includes zero. No reference interval is available for residual correlation.

**What must stay visible.** Residual dependence and HDL SD are weaker than the sample reference in all six laws. The nearly zero HDL coefficient remains. LIPID_WORKFLOW_R1 has one HDL-above-TC record among its 9,000 rows; no row was removed. Exact concentration components and independently measured assays are different interpretations, so the expert should say what ordering or measurement assumptions matter for the intended use.

**Stage and mathematical boundary.** This table is the original repeatability output, not a mixture of selectively repaired branches. LIPID_BASE_R2's ideal law was found to have divergent TC moments despite plausible finite outputs. In the separate paired quality-assurance study, both review policies repaired that defect; the modest numerical changes did not resolve the dependence limitation. Disclose that status succinctly and offer the already completed repair result as optional context. Do not ask the biomedical reviewer to treat the initial law as a valid population-moment model, or substitute only its favorable revised values into this six-author table.

**Modeling assumptions to summarize.** Sources provide marginal anchors, standardized/categorical BMI effects or selected dependence quantities. Authors choose scale conversions, conditional variances, error correlations or positive component models. Those choices do not automatically identify the requested joint residual association. This helps the reviewer name the one missing measurement/source condition that would change a scientific-use decision; it is not a new evidence-indirectness experiment.

**Bound aggregate sources:** [repeatability RESULTS](../request_only_repeatability_2026-11-11/RESULTS.md), [all means/diagnostics](../request_only_repeatability_2026-11-11/AGGREGATE_TABLES.md), [source/code audit](../request_only_repeatability_2026-11-11/review/SCIENTIFIC_PROVENANCE_AUDIT.md). Optional repair context: [paired review RESULTS](../scientific_check_revision_2026-11-11/RESULTS.md). Use the v0.30 Figure 5 lipid panels or complete original aggregate figure, without new fitted curves or selected-author highlighting.

## Older packet and permission boundaries

- `deliverables/Biomedical_Review_Pack_2026-11-06` is an **iron-status-only** collaborator packet, with six fully synthetic row tables, measured-reference aggregates, source links, optional original generator code and an old v0.24 manuscript. Its README explicitly excludes real participant records, full third-party papers, credentials and external model-review conversations. It is prepared for local collaborator review, not a public data release. It can inform the short reading order and plain response form; its iron findings and historical permission to include those synthetic files do not automatically carry over to this new packet. None of those row files was opened here.
- `work/provenance_audit_materials_2026-11-11` has twelve dossiers from four **earlier capacity-stage** laws, not the twelve repeatability laws. Each A/B package contains no participant or generated rows, clinical reference estimates, full papers or credentials. The navigation maps add curated postclosure interpretation; their existence is not evidence of measured human benefit.
- The provenance package's `_host_only` answer key, identity mapping and ambiguity/scoring materials must stay out of an external packet. The earlier design gives each reviewer only A or B; sending both would violate its intended comparative assignment. This new qualitative use review is a separate purpose and does not claim that earlier experiment occurred.
- Both older preparations have zero completed human responses. Their static/source checks do not imply completed visual/interactive QA; the older provenance HTML's browser review was explicitly unverified. A newly built HTML/PDF/ZIP requires its own inspection.
- For this new brief, share original summaries, permitted aggregate figures, source links and the blank questions. Keep patient/generated individual tables, full third-party source documents, credentials, raw model payloads and private answer keys out. No external message or file transfer is performed by preparing these materials. Any later individual-table request is a separate sharing decision, not necessary for this first qualitative review.

## What to do with feedback

Preserve the response text and requested restrictions, including inability to assess. The useful output is a short analysis-by-analysis permitted-use statement and the single next evidence item that would change it. Do not score the reviewer against a preferred positive verdict, convert comments into a clinical-validation rate, or claim improved review speed without a separate study. Domain judgments supplement the numerical and source/code audits; they do not replace those checks.
