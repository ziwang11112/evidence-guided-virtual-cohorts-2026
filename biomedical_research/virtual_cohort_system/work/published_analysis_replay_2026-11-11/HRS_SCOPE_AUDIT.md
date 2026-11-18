# HRS published-analysis scope audit

2026-11-11. Independent read-only review of local original R code, frozen evaluator and published aggregate-reference definitions. No individual data, model/API calls, fitting, sampling or old-file changes.

## Admission conclusion

HRS can supply a useful completed **published recipient-stage analysis preservation** report without rerunning generation. It cannot presently supply an unchanged full-paper pipeline with real and virtual IPD substituted as inputs. The existing complete output already covers all16 fixed effects and27 expanded baseline diagnostic fields; reporting only the two focal interactions would unnecessarily hide the full result.

## Direct code mapping

| Item | Original material | Frozen local implementation | Audit conclusion |
|---|---|---|---|
| Longitudinal analysis | `sources/original/RCTSim2_postGitHub_20200728.R:315–320` | `evaluation/native_evaluate.R:84–103` | Same fixed-effect expansion and correlated intercept/age-slope structure; ID and outcome names adapted. |
| Fixed formula | `mem.s ~ age60*(hba1c_U65+hba1c_O65+race+educ+sex+cses)+(1+age60|ID)` | Same formula with `mem_s` and `subject_id` |16 fixed coefficients, including all interactions, not just two focal terms. |
| Age and spline coding | RCTSim2:212–221 | native_evaluate.R:28,75–76,89–90 | Age centered60/divided10; HbA1c branches centered6.5; multiplication indicator and pmin/pmax are equivalent at/below/above knot. |
| Factor reference coding | Exported coefficient names / HRS_PUBLISHED_REFERENCES.json | native_evaluate.R:84–87 | Female,White,College reference levels explicitly fixed. Paper “Greater than HS” maps to code College; do not reinterpret as a new category. |
| Fit convention | RCTSim2:319–320, default REML | native_evaluate.R:92–94 |bobyqa,maxfun2e8,REML TRUE. The original source-IPD fit in HRS_sim_data_code_postGitHub_20200728.R:127–129 instead leaves optimizer at its historical default. |
| Missingness and schema | Original source fit accepts its historical input; default na.action | native_evaluate.R:17–37,93 |Complete-table validation and na.fail; balanced4 visits at0/2/4/6. Not a replay of original missing-visit patterns. |
| Baseline descriptions | RCTSim2:383–403; HRS source script:40–61 | native_evaluate.R:52–63 |Source20 native fields expanded into27 reported diagnostics, including categorical percentages. Sample SD denominator n−1. Baseline memory uses first assessment; no re-standardization of already standardized synthetic memory. |
| Runtime | EVALUATOR_MANIFEST records historicalR4.0.1/lme4 1.1-23 | R4.3.3/lme4 1.1-35.1 |Compatible implementation, not bitwise historical-runtime reproduction. |

## Executable scope and limits

The directly reusable scientific fragment is the HRS `lmer` block atRCTSim2:315–320, after documented column/factor adaptation, plus its baseline summary block383–403. The full script also generates ARIC, imputes/pools cohorts, fits additional diet/group models, and loops5000 times. Those stages are outside the completed local case; missing serialized models were replaced by explicit formulas in the published-law reconstruction.

SourceHRS comprises11509 people and43500 observed visits. Each local table contains11509 fictional subjects and46036 balanced visits. The retained comparison has3 Agent tables+3 corrected-law tables;9 physical generation attempts include3 invalid initial comparator deliveries caused by the local coefficient parser. All failures remain recorded. Six tables are not six clinical cohorts or six independent scientific constructions.

## What the references mean

`HRS_PUBLISHED_REFERENCES.json` transcribes rounded Original and Synthetic columns from publishedTables2/3. Original is an author-reported sample result, not a local real-IPD refit. Synthetic is the paper's5000-draw summary, not an independent clinical sample. The more precise exported model coefficients were supplied to both constructors. Thus analysis agreement is a legitimate reconstruction result, not recovery of relationships withheld from the Agent.

Retain separate columns for original published sample, original paper synthetic summary, high-precision generating coefficients, Agent3seed outputs and corrected-law3seed outputs. Preserve the weak upper-HbA1c interaction and original-versus-synthetic upper-HbA1c dispersion mismatch. Do not treat sign/p-value agreement, confidence-interval overlap or additional fictional rows as calibrated clinical evidence.

The existing six fits returned all16 terms with optimizer code0 and no warnings/singularity. Existing GLS verification is conditional on the fitted variance components; it does not independently verify the REML optimum. This audit did not rerun those checks.

## Minimal completion recommendation

Produce a code/estimand mapping and full analysis-preservation display from saved outputs, with the above boundaries. This is a useful documentation/interpretation completion unit, not a new experiment or untouched real-IPD validation. A separate true input-substitution study needs its own admitted original analysis specification/code and accessible real data; none is certified by this HRS audit.

All paths above are relative to `work/hrs_public_example_2026-11-03/`. Supporting records: `PROTOCOL.md`, `RESULTS.md`, `FINAL_RESULT_REVIEW.md`, `evaluation/EVALUATOR_MANIFEST.json`, `sources/HRS_STUDY_NOTES.md`, and `sources/HRS_PUBLISHED_REFERENCES.json`.
