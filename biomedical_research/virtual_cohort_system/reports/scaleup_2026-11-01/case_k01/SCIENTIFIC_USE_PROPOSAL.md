# Provisional K01 scientific uses: adiposity and protocol-relative glucose

2 November 2026. **Proposal only: HAALSI is not admitted, these choices are not frozen, and no construction or target-effect evaluation is authorized.** This document follows design v1, the campaign budget and the K02 prospective exposure amendment. It uses the reviewed HAALSI definitions and schema findings; it does not use target measurement values, moments, effects or availability counts to choose an analysis. The bounded two-study source review is available, but its candidate evidence is not approved or activated.

## Recommended target and three uses

Recommend whole-cohort generation of age, sex, BMI and cleaned point-of-care glucose in **mmol/L**, representing the pooled HAALSI baseline measurement protocol. Do not call this universally fasting glucose, venous-plasma glucose or HbA1c. Source evidence may constrain a different assay or fasting context; transport to this protocol is a named scientific assumption, not a unit conversion.

The empirical reference is the exact acquired HAALSI baseline release and a prospectively defined complete cleaned subset. The point estimands are **unweighted finite-sample least-squares projections of the released cleaned numbers in that subset**, not latent biological-glucose, national population, future-patient or causal parameters. Census age, sex coding and measurement definitions identify the target; a specified coefficient or contrast identifies the scientific estimand. Sharing variables or a cohort name does not make two differently selected or adjusted estimands identical.

Let `G` denote cleaned glucose in mmol/L, `A` census age in years, `B` cleaned BMI in kg/m², and `S=1` for the verified Female code and `S=0` for Male. The conventional BMI unit interpretation is based on the cleaned height/weight definition, not an explicit unit string in the actual `BMI` label. Include an intercept in both models. No desired coefficient, direction or mean is supplied.

| Primary use | Provisional estimator and reported contrast | Scientific purpose |
|---|---|---|
| 1. Adiposity–glucose relationship | Fit `G ~ A + S + B`; report `5 × beta_B`, in mmol/L per 5 kg/m² BMI. | Quantify the age/sex-adjusted difference in measured glycemia associated with a fixed adiposity contrast. Matching only the glucose mean or an association's sign cannot recover its magnitude. |
| 2. Age–glucose relationship | From the same projection, report `10 × beta_A`, in mmol/L per 10 years of census age. | Quantify an age gradient after accounting for measured adiposity and sex. This is a separate substantive question using the same release, although the two estimates are statistically dependent and not independent replications. |
| 3. Conditional reuse across sex | Fit `G ~ A + S + B + S:B`; report `5 × beta_(S:B)`, the Female-minus-Male difference in the BMI contrast under a common age adjustment. | Ask whether the same joint table supports sex-specific adiposity–glycemia relationships beyond marginal summaries. Neither the difference's sign nor an interaction p-value alone demonstrates usefulness. |

Use 3 is the reuse item **within** the three primaries, not a fourth endpoint. It is not algebraically implied by the two pooled coefficients alone. A common age term is a defined projection choice, not a claim that every underlying age relation is linear or identical across sex. Do not replace the interaction with a more favorable subgroup, reverse regression or data-selected nonlinear form after target disclosure. Singular models, missing sex support or other estimator failures remain failures/unavailable endpoints under the eventual frozen rule.

## Outcome-blind selection and measurement choices

The proposed primary subset uses the released cleaned variables `rage`, `rsex`, `c_bs_bmi` and `c_bs_glucose`, with native/tagged missing treated as missing; no imputation of measured reference cells. Require finite numerical age/BMI/glucose, recognized sex coding, and positive BMI/glucose. Propose age at least 40 using `rage` as an investigator-defined restriction guided by official baseline metadata, with no invented upper age cutoff. Because `rage` refers to 31 July 2014 at sample selection, do not silently substitute interview age or assert that this restriction exactly reconstructs the original recruitment rule. Freeze the precise restriction after the remaining metadata review.

The canonical column names, kinds and units are shared; **population eligibility is context-specific**. The proposed target age minimum must be enforced for the target without rejecting legitimate younger source-context draws or silently relaxing target validation. Each admitted source context needs its own reviewed age bounds and selection contract, bound to the common scientific model. No global `age >= 40` source/target rule or undeclared source-age truncation is proposed. This is a later task/bridge packaging requirement, not a request for new code here.

Keep the raw glucose scale. No automatic logs, winsorization, outcome-based trimming, diabetes-treatment exclusion or threshold-derived diabetes outcome is proposed. The legacy diabetes composites remain unused because their diagnosis/treatment cross-references and fasting boundary are unreconciled. No medication or village endpoint is added.

Propose retaining finite positive **released cleaned numbers**, with no range-flag exclusion, clipping or tail trimming. A plausibility flag is not proof that a cleaned value is invalid. Native/tagged missing is excluded; any officially documented numeric nonmeasurement sentinel must be listed and handled explicitly before freeze, never inferred from a value's extremeness. Instrument-limit or substituted boundary values, if retained as released numbers, do not become exact biological glucose measurements. The recorded-value estimand preserves that censoring/assay limitation; it does not require reconstructing latent true glucose. Freeze this rule before outcomes rather than later selecting a favorable flag policy.

| Protocol option | Interpretation and decision |
|---|---|
| Pooled protocol-relative glucose — **recommended primary** | Include eligible cleaned measurements irrespective of fasting status; do not require the fasting field or silently classify missing fasting as nonfasting. The estimand includes the cohort's measurement-protocol mixture. Unknown feeding composition and its dependence on age/sex/BMI remain transport assumptions for constructors, not supplied target proportions. |
| Fasting-only reference — alternative before freeze | Restrict using the reviewed fasting definition and explicit missing/timing policy. This changes the target subset and demands corresponding source applicability and generator-context assumptions. The derived eight-hour flag is not proof of verified fasting. Choose this only for a scientific measurement reason before outcomes, not because a subgroup yields better agreement. |

Do not add a fasting subgroup analysis to a four-column release that contains no fasting state. That would require a declared task/context change or an additional generated variable and consumes a prespecified secondary slot; it is not authorized here. The recommended primary choice needs no such expansion.

## Evidence status and remaining source decisions

Use a claim-level label separately from whether the target is held out:

- **Directly reported:** the source reports the same relation and operator with documented scale, adjustment, population and measurement context. A source result can be a valid input while still requiring transport to HAALSI; it is not thereby a target answer.
- **Algebraically implied:** the required statistic follows from reported quantities by a documented identity and its stated assumptions. For example, two comparable sex-specific BMI slopes can imply their difference. A unit change alone does not turn a fasting assay into pooled POC glucose or a confidence interval into participant dispersion.
- **Joint-assumption dependent:** the available claims do not identify the relation. The constructor supplies an explicit dependence, interaction, residual or context-transport assumption. Missing information is not evidence for a zero interaction, conditional independence or identical sex-specific slopes.

The local [bounded source review](evidence/SOURCE_REVIEW_2026-11-02.md) gives the following disposition. This drafting unit read that original review rather than opening new papers or browsing.

| Reviewed original | Usable information and applicability limit |
|---|---|
| Ayele 2020, DOI `10.1177/2050312120975235` | Direct age moments, sex composition and BMI-category margins; categorical composite-diabetes adjusted ORs are contextual. The latter do not identify continuous glucose slopes. Source glucose is a three-consecutive-day capillary average with an unresolved fasting/random mixture and medication contribution to diabetes classification; imputed covariates and selection also differ. Methods ages 25–64 conflict with table captions 25–65; do not silently repair the source boundary or import its exclusions into HAALSI. |
| Bahendeka 2016, DOI `10.1111/tmi.12663` | Abstract-only verification of sex-specific age moments and weighted IFG/diabetes prevalence in a national Ugandan fasting-capillary survey aged 18–69. Continuous glucose moments/slopes, device and detailed operator/weighting information are unavailable. These prevalences cannot become an exact equal-weight threshold check in the four-column request. Full-protocol/overlap assessment remains limited. |

**All three proposed continuous-glucose projections are joint-assumption dependent relative to these verified inputs; none is directly reported or algebraically implied.** The reviewed sources provide no continuous glucose scale/dispersion or matching adjusted slopes. This is a material limitation of the current evidence basis, not evidence that any slope or interaction is zero. The interaction is a candidate reuse beyond these inputs, not proof that the eventual model supports it well. If a shared, pre-outcome packet addition later reports matching sex-specific slopes or otherwise determines the contrast, update its direct/derived status. Do not conceal that status or change the endpoint after target revelation to preserve a stronger novelty claim. Target holdout and reuse beyond fitted information are different properties.

Before admission, resolve the source review's use dispositions and retain its documented limits on original-study identity/overlap, age/selection, assay/feeding/medication, units/transforms, operators/adjustment and uncertainty. Ethiopian and Ugandan recruitment supports geographical separation from HAALSI Agincourt; it is not a participant-linkage proof, and Bahendeka's abstract-only overlap assessment is incomplete. Binary diabetes or HbA1c findings cannot be relabelled as continuous POC-glucose slopes. Unknown weights, selection, dependence and target composition remain explicit. Incomplete joint identification alone does not forbid an assumption-labelled construction, but it limits what success or failure can be attributed to the sources.

All five Agent constructions and the statistical reference receive the same admitted source packet and population/measurement description. The Agent owns unreported joint structure and measurement transport; the coordinator does not supply a desired target relation. A transparent same-information reference and finite source-context budget remain to be specified before release, with no hidden source calibration or target-derived parameters.

## Quantitative interpretation and campaign boundary

Recommend the existing convention: report each raw contrast, its difference from the measured reference, and absolute discrepancy divided by the **reference glucose SD**. That SD is evaluation-only and never a generator input. If it is zero/undefined, the normalized endpoint is unavailable under a fixed rule. As a provisional research resolution, retain the K02-style 0.10 working margin and complete 0.05/0.10/0.20/0.30 sensitivity grid, pending pre-outcome review. These are operational resolutions, not clinical equivalence bounds or percentage errors. No new metric or composite score is proposed.

Apply the same frozen estimator to every scheduled output. A possible carried-forward bundle rule is all three uses within the working margin on all three seeds, and at least four of all five Agent constructors; the single reference uses its own three-use/three-seed bundle. Preserve the zero-association discrimination check before granting a continuation claim. Freeze the exact rule before evaluation rather than selecting a margin that makes this case pass. HC3 intervals may be reported as working descriptive sensitivity summaries; they are not proof of population-calibrated uncertainty or robustness to clustering. Virtual-table precision does not add measured evidence.

The final frozen stage is primary; initial/final comparisons are paired secondary feedback analyses. Retained finals alias initial artifacts, while a failed revised final cannot be replaced by a more favorable initial stage or seed. Preserve five Agents plus one statistical reference, one source-feedback opportunity, seeds 2101–2103, 5,000 rows per new table, and at most 36 target slots for this case. Source executions need their own finite reviewed cap. This document adds no runs, study intake or secondary endpoints.

Under `case_k02/PROSPECTIVE_EXPOSURE_AMENDMENT.md`, K01 must be independently admitted as an unexposed quantitative reference, and only its eventual fixed-bundle pass can satisfy the positive Wave B continuation condition. K02 success alone cannot. HAALSI access and schema sufficiency do not establish source independence, case admission, a global freeze or scientific success. The next decision is the bounded source-applicability review and confirmation of the recorded-value eligibility rule, followed by independent review of the complete case contract.

## Local basis

- `docs/METHOD_AND_EXPERIMENT_DESIGN_v1_2026-11-02.md`, especially sections 4–8 and 10.
- `work/scaleup_2026-11-01/campaign_plan.json`, budget and retention rules; its older Wave A gate is superseded by the exposure amendment.
- `work/scaleup_2026-11-01/case_k02/PROSPECTIVE_EXPOSURE_AMENDMENT.md`.
- `work/scaleup_2026-11-01/admission_next/HAALSI_CODEBOOK_SCHEMA.md`, `HAALSI_INDEPENDENT_SCHEMA_REVIEW.md`, and official landing metadata recorded in `HAALSI_ACCESS.json`.
- `work/scaleup_2026-11-01/case_k01/evidence/SOURCE_REVIEW_2026-11-02.md` (Ayele full original reviewed by the source agent; Bahendeka abstract-only verification).

This drafting unit opened no patient file, read no target clinical measurements/effects, searched no network, wrote no generator or new code, and ran no tests. Previously authorized schema/availability findings remain metadata, not calibration inputs or an analysis-selection criterion.
