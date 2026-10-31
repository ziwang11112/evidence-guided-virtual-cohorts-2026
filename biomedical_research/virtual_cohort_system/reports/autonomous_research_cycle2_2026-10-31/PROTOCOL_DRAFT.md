# ENSANUT glycemia: prospective whole-cohort analytical-use pilot

31 October 2026. **Draft for independent review; not an experiment freeze or permission to inspect target effects.** The approved acquisition contract covers metadata only. This draft changes neither old experiments nor their reference status.

## Scientific purpose

Can a scientific Agent turn external published marginal and conditional evidence into one reusable five-variable virtual cohort, with no real individual rows supplied, and support prespecified analyses in a new study family? Source reproduction, cross-population transfer and a not-directly-calibrated conditional analysis are separate questions. The pilot does not test causal effects or require superiority over another Agent.

The five generated variables are age (years), female indicator (0 male, 1 female), BMI (kg/m2), fasting serum glucose (mg/dL), and HbA1c (percent). An identifier is synthetic bookkeeping. Every scientific variable is generated. The source papers use fasting plasma glucose; transfer to ENSANUT serum glucose is an explicit specimen/assay assumption, not an identity established by unit conversion.

External evidence is the audited Pani 2008, Jansen 2013 and Liu 2015 material. Primary source quantities keep their original population, selection, units, adjustment and uncertainty. Separate regressions must not be concatenated into a structural equation. Pani and Liu NHANES overlap; they are not independent clinical replications. The target ENSANUT family is excluded from scientific construction evidence. Newly found target results cannot silently become inputs.

The scientific Agent selects its own generator, dependencies, numerical parameters, residual variation and transfer assumptions. The controller supplies the public task, audited evidence and analysis protocol. It does not prescribe target slopes, desired signs or scientific parameter repairs.

## Target and reference estimand

The proposed target is an explicitly **age/sex-balanced analytical population** of adults aged 25–79 with no reported prior doctor diagnosis of diabetes/high blood sugar, a recorded 8–12-hour fast, and fasting glucose below 126 mg/dL. It is not the Mexican national population. Four age ranges (25–39, 40–54, 55–69, 70–79) cross two sexes; each of the eight strata has weight 1/8. Within-stratum joint distributions are the object to generate and validate, not provided target answers.

Each generated table has 2,000 fictional individuals, exactly 250 per design stratum. This row count reduces simulation noise; it creates no additional clinical information. Within-stratum age distributions and all biomarker relationships remain Agent-authored evidence/assumption choices. No target empirical age histogram, BMI or glycemia summary is given to the builder.

The measured reference is the complete, eligible linked subset of the pinned ENSANUT release. For reference analyses, each participant in stratum h receives weight 1/(8*n_h). All available eligible participants contribute; no favorable reference subsample is selected. The generated analyses use the same stratum-standardized estimator. This is a finite empirical analytical reference with a prespecified demographic standard, not an estimate of national prevalence or national means.

The public lab glucose expansion weight and both modules' survey fields remain preserved locally. Their suitability for the joint complete-case subset is unresolved. This pilot will not substitute either expansion weight or claim national design-based inference. Lab PSU/stratum fields are used only for a declared empirical stability resampling; the anthropometry strata are not overwritten.

## Measurement and eligibility proposal

All rules below must pass metadata/code review before being frozen. No eligible counts, values, effects or scientific summaries have yet been inspected.

1. Join pinned lab and anthropometry files one-to-one on the four validated string keys, retaining original columns and module suffixes. Require the recorded age/sex agreement already established in preflight.
2. Use reported age 25–79 and sex codes 1/2, mapped explicitly. Require lab P7==2 (no previous doctor diagnosis). Codes 1, 3 (pregnancy-related diagnosis), 9 and blank are excluded; this is deliberately a never-reported-diagnosis subset, not all people free of current clinical diabetes. No medication variable is available, and no claim of independently verified treatment exclusion is made.
3. Require 8<=P5_1<=12 recorded hours since food, finite glucose below 126 mg/dL and available HbA1c. The fasting range is a prospective analytical restriction; the papers' unreported fasting duration is not retrospectively filled with this value.
4. For women aged 25–49, require the anthropometry P6 response documenting neither current pregnancy nor breastfeeding. Other sexes/ages follow questionnaire routing and are not assigned invented negative answers. The label is 'no pregnancy/lactation documented under the questionnaire rules'; unasked status in older women remains a limitation.
5. Use the age-routed standing measurements: PESO1/TALLA4 under 60; PESO12/TALLA15 at 60+. Exclude explicit inability-to-stand/amputation routes where the official coding requires an alternative measurement. Use the first complete valid standing weight/height pair; if it is missing/nonmeasurement, use the second complete pair. Do not mix a first weight with second height, estimate stature from knee height/hemi-span, or retrospectively choose the reading nearest an expected BMI. Documented 222.222/222.2 nonmeasurement codes are excluded in both same-unit repeats as a conservative declared cleaning rule. Positive numeric readings are required.
6. Define BMI from that prespecified pair as kg/(cm/100)^2. This is an investigator-defined secondary-analysis measurement, not a claim to reproduce an unpublished final/third-reading ENSANUT BMI algorithm. Retain repeat availability and discrepancy diagnostics for preparation audit only, without selecting a more favorable analysis rule after evaluation.
7. No anemia exclusion is claimed: hemoglobin is not in the acquired two-table set. The Lifelines/Liu anemia-screened source populations therefore differ from the target; the Agent must declare that transfer assumption. HbA1c is not a substitute for hemoglobin. No additional patient archive is required solely to make all source populations appear identical.
8. Exclude missing required values according to explicit source codes; no target imputation, winsorization, distribution-based outlier removal or fitted recalibration. Physical nonpositive laboratory or anthropometry measurements are invalid. Any unexplained coding error stops preparation for adjudication before effects are calculated; it does not license silent truncation.

After freezing preparation, a custodian may release only the eligibility flow and readiness boolean: at least 30 reference participants in every design stratum, at least 400 total, and sufficient nonconstant values/full rank for the fixed analyses. These are minimum execution-readiness floors, not a promise of power. Failure is reported; no endpoint-driven cohort modification is allowed.

## Prespecified analytical questions

Fit HbA1c in percentage points as outcome using weighted least squares and the exact demographic standard above. Use age10=(age-50)/10, BMI5=(BMI-25)/5 and glucose10=(glucose-100)/10 for conditioning and readable units; centering changes no linear slope.

| ID | Question and exact analysis | Relationship to supplied evidence |
|---|---|---|
| Q1 | Age10 coefficient in HbA1c ~ 1 + age10 + female + BMI5 + glucose10 | Pani supplies a corresponding adjusted age projection in a different population. This is a transfer check, not an unseen relation. |
| Q2 | BMI5 coefficient in HbA1c ~ 1 + age10 + female + BMI5 | Lifelines supplies the age/sex-adjusted BMI projection. Selection, ancestry and measurement transfer remain assumptions. |
| Q3 | BMI5 coefficient in the Q1 model; additionally report Q2 minus Q3 | The exact five-variable BMI projection is not a supplied calibration target. Lifelines Model III conditions on additional erythrocyte/lifestyle variables and cannot substitute for it. This checks one useful analysis of the unreported joint structure. The difference is descriptive attenuation, not causal mediation. |

Secondary fixed diagnostics: glucose10 coefficient in HbA1c ~ 1 + age10 + female + glucose10 (source-indexed transfer); age/sex/BMI/glucose/HbA1c means, SDs and 10/50/90 percentiles under the standard; and residual descriptive spread for the Q1 model. All are reported; diagnostics do not become feedback. No data-dependent subgroup search or polynomial choice is added.

For the real-reference uncertainty display, resample lab PSUs within lab strata with replacement, carrying complete clusters and recomputing the demographic standard (399 replicates, fixed seed to be specified in the freeze). Preserve singleton strata, count failed/empty-stratum/singular replicates and report them. These percentile ranges are **empirical cluster-resampling stability bands**, conditional on this observed/selected reference. They are not national design-based confidence intervals or proof that a sample estimate equals population truth. Validate this implementation independently. Generated-seed variation is displayed separately and is not biological sampling uncertainty.

Compare direction, units, magnitude, assumption sensitivity and reference stability, not individual generated-to-real matching. There is no invented equivalence tolerance or 'CI overlaps therefore equivalent' rule. Synthetic p-values do not establish biological significance. Report each construction and seed, including opposite or unresolved directions. An exposed reference is permanently closed to further tuning and new-confirmation claims.

## Construction, source feedback and budget

At most two fresh-context scientific constructions, each with initial and one source-feedback revision/retention opportunity. Three final analytical seeds per stage (to be fixed before execution). Repeated retained stages share outputs and do not double the evidence.

Use the existing isolated program executor. A case-local mechanical source-context bridge is being tested: one byte-identical Agent-authored generator; all model-specification fields identical except a frozen active_context selector; every source context definition is declared before feedback. Context definitions may supply source-specific population distributions and selection assumptions, but no controller-supplied biomedical repairs. The bridge verifies frozen cross-context identity; it cannot certify scientific adequacy.

Preferred source checks are in separate Lifelines and Pani/NHANES contexts, if the Agent can defend the reconstruction from admitted aggregates. No source IPD is supplied. Reconstructed source populations are normally approximate, especially Pani's survey target and unreported covariances. Unsupported checks remain not computable. Liu is contextual/unadjusted evidence, not a mandatory third simulation context. Source rows/seed and exact operators must be fixed in the task and bridge plan before the feedback run. No adaptive extra draws to obtain a better feedback score.

Review may support revise, retain, or stop. All actual feedback and decisions are bound. No target diagnostics are released to a builder. All target analyses wait until every final candidate is frozen. If the bridge cannot be verified, no host fallback or false source-context claim is allowed; the ordinary Agent construction can still be evaluated under a clearly revised and independently reviewed pre-execution protocol.

## Release gate and decisions

Required before clinical generation: source-audit admission; measurement/eligibility/design review; fixed source feedback definitions and all budgets/seeds; working isolation and bridge verification; evaluator unit/independent arithmetic checks using artificial data only; and a hash-bound protocol/task/evidence/evaluator release. The custodian keeps participant data private. Builders see only their allowed package and approved originals, not this target-preparation workspace or other constructions.

After all frozen outputs, evaluate once and independently recompute the fixed reference and generated analyses. Determine which source-supported transfers and which extra conditional analysis the data support; retain failures. The outcome can support analytical feasibility, expose sensitivity to unreported joint assumptions, or justify simplifying/stopping. It does not establish method superiority, calibrated model uncertainty, replacement of clinical measurements, or publication readiness by itself.
