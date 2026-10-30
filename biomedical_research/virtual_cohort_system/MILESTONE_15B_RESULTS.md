# M15-B1: literature-enabled direct Agent enrichment

30 October 2026. **Partial analytical feasibility, with a clear age-association failure and systematic distribution mismatch.** One scientific Agent directly authored a fictional urate column for 200 fixed real covariate records. It used full external originals, performed literature searches, inspected an additional original and a supplement after documented controller-assisted access, and reviewed actual source-statistic feedback. No sampling program produced the urate values.

After feedback the Agent retained its initial table and specification unchanged. The final freeze preceded the single measured-reference evaluation. All 24 scheduled estimands were reported. Independent recomputation agrees to floating-point precision. This is one authored table, not two independent initial/final constructions, and it does not demonstrate a benefit from revision or superiority over another method.

## Main analytical results

Both measured and fictional urate were analyzed on the same 200 participants. The global models adjust for age, BMI, recorded sex and race. Define `b=(BMI−28)/5`, `a=(age−40)/10`, `m=1` for male and `r=1` for Black. Curvature and interaction are fitted in separate models.

| Scheduled analysis | Measured urate | Agent urate | Generated minus measured | Interpretation in this finite benchmark |
|---|---:|---:|---:|---|
| Adjusted BMI coefficient, mg/dL per 5 kg/m² | 0.335316 | 0.345446 | 0.010129 | Positive relationship and point magnitude are close |
| Adjusted age coefficient, mg/dL per 10 years | −0.155459 | 0.069343 | 0.224802 | Direction is wrong |
| BMI curvature coefficient, mg/dL per `b²` | −0.031676 | −0.039252 | −0.007576 | Same negative curvature; magnitude differs |
| Male-minus-female BMI slope, mg/dL per 5 kg/m² | 0.049716 | 0.069171 | 0.019455 | Same positive point direction; not a test of equivalence |

The curvature model is `urate ~ 1+b+a+m+r+b²`; the interaction model is `urate ~ 1+b+a+m+r+b*m`. A common linear adjustment model supplies the BMI and age rows. These are descriptive regression coefficients, not causal effects or national survey estimates.

All 29 leave-one-joint-PSU-out reference fits succeeded for each of the four global coefficients. Their respective ranges were BMI `[0.316328,0.358387]`, age `[−0.179630,−0.118876]`, curvature `[−0.036090,−0.025591]`, and interaction `[0.010227,0.143223]`. Reference signs remained unchanged under these deletions. In particular, the age mismatch is not removed by this sensitivity check. **These ranges are descriptive sensitivity ranges, not confidence intervals, significance tests or calibrated uncertainty.** They do not cover literature, transport or authoring uncertainty.

The BMI relationship was supported by source evidence. A concave high-BMI hinge was explicitly imposed as an extrapolation assumption before generation; agreement in the quadratic coefficient's direction therefore provides target-transfer evidence for that shape assumption, not discovery of an unprompted mechanism. Age coefficients and a common working BMI slope by sex were also model assumptions. The builder was told the intended analysis families, including age, curvature and sex interaction. Measured target coefficients, their directions and other target-analysis answers were not supplied to the builder; the controller evaluated them only after final freeze.

## Group distributions and reverse regressions

Every group contains 50 people. Pairs below are **measured / generated**, all in mg/dL. SD uses `ddof=1`; Q90 uses linear interpolation.

| Group | Mean | SD | Median | Q90 |
|---|---|---|---|---|
| White male | 5.822 / 6.130 | 1.158 / 1.270 | 5.450 / 6.150 | 7.220 / 7.820 |
| White female | 4.378 / 4.670 | 0.936 / 1.203 | 4.300 / 4.600 | 5.720 / 6.120 |
| Black male | 5.766 / 6.374 | 1.103 / 1.522 | 5.650 / 6.250 | 7.200 / 8.610 |
| Black female | 4.588 / 4.930 | 1.355 / 1.567 | 4.450 / 4.750 | 6.550 / 7.110 |

All four means, SDs, medians and Q90 values are higher in the authored table. Mean shifts range from 0.292 to 0.608 mg/dL; Q90 shifts range from 0.400 to 1.410 mg/dL. Close source moments did not establish correct target levels or dispersion.

The four age-adjusted within-group models `BMI ~ 1+urate+age` also retain positive directions but underestimate the measured coefficient:

| Group | Measured | Generated | Units |
|---|---:|---:|---|
| White male | 3.580026 | 2.673546 | (kg/m²)/(mg/dL) |
| White female | 5.550369 | 4.525487 | (kg/m²)/(mg/dL) |
| Black male | 3.951960 | 2.484635 | (kg/m²)/(mg/dL) |
| Black female | 3.502524 | 2.288869 | (kg/m²)/(mg/dL) |

These 24 analyses comprise four global coefficients, four group reverse coefficients and 16 group summaries. None was dropped or selected after viewing results. Target reverse regressions use all 50 people per group, ages 20–56; the source-feedback Sun comparisons restrict ages 20–54. Those two sets of generated coefficients must not be conflated.

## What the Agent actually did

1. **Evidence research.** It read full Yun 2021 and Sun 2014 Bogalusa originals, including SDs and reported relationships; identified gaps in age, subgroup dependence, conditional variation and extrapolation; and completed five targeted gateway searches. The gateway charged six queries, including the metadata query associated with article acquisition. It attempted two full-text downloads: Ferrara was conservatively rejected because of an incidental NHANES citation, while a repeat Yun acquisition enabled supplement discovery.
2. **Source-access repair.** At the Agent's request, a separate controller review acquired the Ferrara original and the linked Yun DOCX supplement at their original URLs, exactly one attempt each. Original provenance, numerical tables and units were independently checked. The complete originals, structural text and embedded supplement figures were made available. This is curator-seeded, Agent-directed retrieval with controller assistance, not entirely autonomous discovery from scratch. Three unique originals represent two recruitment populations; the two Bogalusa papers and supplement are not independent cohorts.
3. **Model choice.** The Agent chose source-centered subgroup means, a roughly 0.07 mg/dL-per-BMI-unit working relationship, sex-specific weak age guides, attenuated high-BMI slope above 40 and explicit residual-scale guides. The BMI scale is an assumption-dependent conversion of standardized source effects, not a reported raw coefficient. Unavailable smoking/alcohol create an additional omitted-variable transport assumption. Marginal SDs were not equated with residual SDs.
4. **Evidence-informed assumption change.** Before authorship, the added Ferrara paper prompted the Agent to reduce its female age guide from 0.020 to 0.010 mg/dL/year. Ferrara supplies no adjusted urate-on-age coefficient; this remained a qualitative modeling choice, not a fitted evidence estimate. Its eventual wrong target direction shows why a documented rationale is insufficient evidence of accuracy.
5. **Direct authorship.** The Agent wrote all 200 urate values as literal CSV text. No generator script, sampler, solver, optimizer or rescaling program populated the outcome. Structural tools checked row count, all five original columns, row order, finite support, schemas and provenance. Deterministic tools subsequently calculated the declared statistics.
6. **Feedback and retention.** A frozen initial table produced 12 approximate numeric source diagnostics plus one explicitly noncomputable standardized-source comparison. Three native Sun slopes remained materially discrepant. The Agent documented the broader observed BMI distribution and unmatched source selection, declined to force equality, and retained the scientific files byte-for-byte. One feedback pass was used; no second pass or numeric repair occurred.
7. **Locked reference analysis.** After final freeze and independent release review, the controller opened the measured urate reference for the scheduled analyses. A second implementation then independently recomputed the results. No measured-reference feedback returned to the builder and no post-reference scientific revision occurred.

The source-check interface documentation lacked its full JSON recipe envelope, which caused a legitimate packaging pause. That documentation is now complete. No harness scientific behavior changed. Other operational observations are retained in [implementation notes](reports/m15b_literature_direct_2026-10-30/IMPLEMENTATION_NOTES.md).

## Data and validation boundary

NHANES August 2021–August 2023 supplied BIOPRO_L, DEMO_L, BMX_L and DIQ_L. Selection was fixed before acquisition: examined adults 20–56, the two specified non-Hispanic race groups and recorded sexes, no self-reported professional diabetes diagnosis, valid BMI/weight/design data and available urate. This is not a laboratory-defined diabetes exclusion, fasting restriction or treatment-free cohort. Fifty people in each race/sex group were selected by a deterministic salted hash of their original IDs, not by favorable urate values. The builder received only pseudonymous ID, race, sex, age and BMI.

The 200-person equal-quota benchmark is not a national probability sample. Analyses are unweighted descriptions on identical records; blood-analysis weights are preserved privately but are not used to claim national inference. Source and target differ in period, geography, covariate distributions, selection and assay platform. Some participants may overlap the project's earlier HbA1c work in the same NHANES cycle; this is a new urate-outcome task, not a claim of entirely unseen participants or freedom from model-training knowledge.

Full-source exposure was recorded, including incidental older NHANES discussion in independent originals; those cited findings were not adopted as generation constraints. Separation is procedural, not an OS sandbox. Eligibility was committed before downloading; the consolidated analysis protocol was completed during acquisition but before generation or target analysis. No external preregistration is claimed.

The broader project retains whole-cohort generation, unmeasured-variable enrichment and missing-cell completion. **This experiment tests only the enrichment case.** Two hundred virtual measurements do not recover 200 individuals' true laboratory values or create 200 new empirical observations.

## Verification and retained artifacts

- 24 evaluator tests passed on invented data. An independent exact-rational/analytic check verified 72 invented numerical comparisons, maximum difference 3.87×10⁻¹⁴.
- Source extraction, all 13 source-check definitions, provenance, preservation, feedback binding and final release were independently reviewed before reference analysis.
- The actual-data independent audit verifies all 24 reference/initial/final estimates, all 29×4 reference deletion fits and summaries, IDs/order/covariates, and zero changed outcome rows. The maximum discrepancy among estimates and PSU results is 4.44×10⁻¹⁵; the maximum discrepancy among the 48 derived generated-minus-reference differences is 7.11×10⁻¹⁵. No categorical/count/rank/sign-stability mismatch was found. JSON and CSV agree on all 24 records.
- Initial table SHA-256: `69b01e7ec84cef431da50d394040edfe661413c5541130b8960490c541607b42`; final table is identical.
- Initial freeze: `558effb25a1ede3ef7b514a5e0c028b4185881a80466451c4dd0a441a5499a1b`; final freeze: `1cd0da713677689509cbdcd8bc8c44bf12bb69a2eaf3c081c66f9cf1f7e24a4e`.

Local records: [protocol](reports/m15b_literature_direct_2026-10-30/PROTOCOL.md), [complete aggregate results](reports/m15b_literature_direct_2026-10-30/results/evaluation.json), [all 24 estimates](reports/m15b_literature_direct_2026-10-30/results/estimands.csv), [source review](reports/m15b_literature_direct_2026-10-30/SOURCE_EXTRACTION_REVIEW.md), [release review](reports/m15b_literature_direct_2026-10-30/FINAL_RELEASE_REVIEW.md), and [independent audit](reports/m15b_literature_direct_2026-10-30/independent_target_audit/). Real/generated row tables and full article/supplement content remain local. Only reviewed code, documents and aggregate records are eligible for the existing private GitHub repository. Earlier frozen experiments remain unchanged.

## Decision and next discriminating step

This run supports the feasibility of directly authored, literature-informed data for **selected** downstream associations in one small benchmark. It does not support general data replacement, valid age analysis, calibrated tails, reliable individual reconstruction, or the claim that source feedback improved the table. One favorable BMI estimate cannot establish repeatability or novelty.

Close this measured target to further tuning or fresh-confirmation claims. Before scaling, the next useful bounded experiment is repeatability and uncertainty: freeze a small set of independent Agent constructions under the same literature-access protocol, then evaluate all of them on a separately admitted outcome/cycle or cohort, preserving complete failures and each construction's assumptions. An explicitly source-supported alternative for unidentified age/dispersion may be examined as a new specification, but the revealed age answer here must not become its hidden calibration target. No such next cohort, training job, HPC job or paid API run was started by this milestone.

Primary sources: [Yun et al. 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC8236402/), [Sun et al. 2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC4208749/), and [Bonaccorsi et al. 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6941025/). Extraction and transfer assumptions are documented separately from their reported findings.
