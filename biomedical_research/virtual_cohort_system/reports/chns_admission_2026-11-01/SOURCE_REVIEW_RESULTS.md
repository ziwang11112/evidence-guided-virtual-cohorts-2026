# CHNS continuation: external evidence and operator decision

1 November 2026. **Decision: continue bounded CHNS admission; do not freeze F2 or generate yet.** Two of six new original-study slots are consumed. This unit strengthens and corrects the evidence input; it is not a new biomedical validation or a demonstrated improvement in generated data.

## What changed

1. The current SAS metadata and official CHNS documentation now have a [measurement contract draft](semantics/MEASUREMENT_CONTRACT_DRAFT.md). Names and units are supported; field-specific missing codes and some response/cleaning maps remain unresolved. Blank stored SAS formats do not resolve them.
2. Existing Lifelines/NHANES evidence was reconstructed without reopening old targets. The [reuse gap map](evidence/REUSED_SOURCE_GAP_MAP.md) separates genuinely reported projections from quarantined coefficients, source overlap and transport assumptions.
3. Two new, distinct external source studies were audited: [Bao 2010 SHDS II](evidence/BAO_2010_SOURCE_AUDIT.md) and [Wang 2024 MIND-China](evidence/MIND_2024_SOURCE_AUDIT.md). Bao contributes an unadjusted plasma-glucose/HbA1c Pearson association. MIND-China contributes paired serum/plasma and HbA1c rank associations under specified measurement and selection conditions. Neither identifies the entire five-variable target joint distribution.
4. Independent original-table inspection and two arithmetic formulations confirmed a source inconsistency: MIND's HbA1c composite table implies Cohen kappa 0.797825 rather than the reported 0.812. The FSG comparison agrees after rounding. [Independent review](evidence/MIND_2024_INDEPENDENT_ARITHMETIC_REVIEW.md) preserves the conflicting reports and the conditional history-free derivation. The disagreement bundle is quarantined; no paper value is silently corrected.
5. A [code/operator review](evidence/OPERATOR_AND_ESTIMAND_REVIEW.md) confirms Pearson, average-tie Spearman and raw unweighted OLS already exist. No new statistical operator is needed merely to ask the three proposed association questions. Weighted source estimation, standardized coefficients and genuine joint cross-tabs are not silently substituted by supported operations.

## Scientific plan retained

Whole-cohort generation remains the principal regime: an Agent would generate age, documented gender, BMI, glucose and HbA1c using approved external evidence and an explicitly described target population, without receiving target participant rows or empirical target moments. Optional individual-variable enrichment remains a later information regime, not a replacement for the whole-cohort objective.

The provisional questions, chosen from external evidence rather than CHNS results, remain:

| Question | Exact target projection, subject to population/missingness freeze | Evidence boundary |
|---|---|---|
| Adiposity-associated glycation | BMI coefficient in HbA1c ~ age + gender + BMI | Jansen reports the analogous projection in a different selected population. Unit and population bridges still need admission. |
| Glycemia-associated glycation | Glucose coefficient in HbA1c ~ age + gender + glucose | Source plasma and CHNS serum are different measurements. MIND supplies paired evidence but no universal conversion. |
| Age association beyond adiposity/glycemia | Age coefficient in HbA1c ~ gender + BMI + glucose + age | A weighted Pani source projection is not faithful unweighted feedback. Target utility can be tested as a declared transport question; the source check must remain unavailable unless correctly supported. |

These are three analyses of one cohort, not three independent replications. No desired target sign, coefficient or success cutoff is installed. Marginal and unadjusted source checks may support construction but cannot certify the conditional questions. The new MIND/Bao evidence is still a candidate packet, not automatically admitted feedback.

## Concrete next gates, in order

**A. Required-field coding.** Use already acquired/current official documentation to resolve the validity and missingness policy for `age`, `GENDER`, `HEIGHT`, `WEIGHT`, `GLUCOSE` and `HbA1c`; retain cleaning flags and measurement timing. Request no new user consent for unchanged CHNS terms. Do not infer a universal 88/99 mask, count missing drug answers as untreated, or repeat a past unit correction. Optional medication/pregnancy exclusions are required only if selected population definitions need them. An all-comers target is possible, but must explicitly differ from source exclusions. If an authoritative field rule cannot be recovered through allowed paths, simplify an affected use transparently or document the exact obstacle; do not keep auditing indefinitely.

**B. Executable evidence admission.** For each proposed source constraint, bind the named statistic, units, selection, adjustment set, weighting status, uncertainty role and source population. Ordinary methods described in a paper and unreported implementation details must be distinguished; no `not_reported` weighting field may be silently relabelled `none`. Quarantine contradictory source quantities. Decide which source populations can actually be replayed by a generator, and which statements remain context/transport assumptions. Existing task-population feedback is not already a source-population replay system.

**C. Protocol freeze.** Define the target population, estimands, measurement bridge, reference missingness and uncertainty, information boundaries and complete reporting; obtain independent review before F2. Only then pass an approved packet to a new-context constructor. Maximum two constructions, initial plus at most one source-feedback revision, three seeds per stage, unchanged. The one-time reference evaluation remains unavailable until candidates freeze.

No further original-study read is currently justified just to accumulate more supporting numbers. Four slots remain for a named unresolved evidence question. No fourth target family, repeated target evaluation, fresh API, training or HPC is added.

## Verification and costs

- Root re-read Bao's original Methods and main results, confirming the named Pearson operator, population/diagnosis selection and plasma measurement. Its remaining table extraction has the primary auditor's detailed locators; do not claim every Bao table was independently recounted.
- Root's exact-rational source arithmetic and the independent review agree. These calculations read published aggregate cells only, not patient records. The generated output is an audit JSON, not a synthetic patient table or a clinical mechanism experiment.
- Existing passed S1 tests and key-only linkage audits were not rerun. No frozen module, generator or historical receipt changed.
- Target clinical effects calculated: **0**. New generated biomedical tables: **0**. F2: **unfrozen**. Scientific admission: **pending**.
- Two saved copies of the same Table 2 image total **205,578 bytes**, counted conservatively against the transfer allowance; one duplicate resulted from a browser binding failure. Saved-file budget total is **232,720,603 bytes**; remaining **291,567,397 bytes**. No additional participant file or full paper was downloaded. Browser page traffic remains unmetered.
- This was foreground work. Verified scheduled runs remain **1**; the existing `chns` continuation is active and no extra schedule was created.

The useful framework lesson is source-aware evidence admission: a generator should not be penalized for failing to satisfy mutually inconsistent published constraints, and a matched statistic should not be confused with a matched population or measurement. This is an implementation requirement supported by a real source example, not yet a claim of methodological novelty or superior scientific utility.
