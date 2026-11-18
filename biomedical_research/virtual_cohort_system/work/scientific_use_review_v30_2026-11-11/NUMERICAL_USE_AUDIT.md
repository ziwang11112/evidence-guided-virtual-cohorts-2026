# Numerical audit of scientific use in two existing case studies

**Judgment for the review brief:** the ENSANUT case demonstrates preservation of a specified multivariable association pattern, beyond mere computability, while current lipid outputs demonstrate operational delivery but materially uneven support for the requested relationships. Neither case establishes calibrated patient/population inference. This is retrospective interpretation of completed results, not a new experiment, quality score, acceptance threshold or manuscript version.

## Scope and counting

The deliberately complementary cases are Q4 ENSANUT E01/E02 and all six initial current-runtime lipid authors. Every assigned constructor and all three requested analyses are retained. That is **8 initial laws, 24 saved tables and 72 primary seed estimates**: 2 × 3 × 3 =18 for ENSANUT and 6 × 3 × 3 =54 for lipids. These are not 72 independent scientific replications. This note additionally includes both already-completed R04 review branches of LIPID_BASE_R2: six dependent tables and eighteen primary seed estimates, separately labelled. They are not two new independent authors. No row-level table was read.

The comparison is to previously exposed sample estimates with their original estimands and uncertainty; it does not identify known population truth. Seed ranges describe those three runs, not source/transfer confidence. All native values and selected essential diagnostic seed records are included in the JSON companion. Other Q4 diagnostics remain available in the original complete table; selecting diagnostic *roles* here does not filter authors or primary outcomes.

## Four meanings that must not be conflated

| Statement | What is established here | What does not follow |
|---|---|---|
| The analysis runs | Required fields, estimators and finite sample outputs are available in all24 main tables. | The numerical result is scientifically accurate or the generating population estimand exists. |
| A relation pattern is recovered | A prespecified direction or conditioning contrast also appears in the sampled data, with its stability shown below. | A causal mechanism, independent discovery or quantitative fidelity. |
| Magnitudes agree | Report signed native-unit differences and descriptive ratios to this sample; judge each analysis separately. | CI overlap as a pass, a post-hoc tolerance, or a universally usable cohort. |
| Data support inference | Requires appropriate uncertainty, transport/selection/measurement assumptions and fit-for-purpose adequacy. | More synthetic rows create additional patient evidence, calibrated standard errors, prevalence or clinical decisions. |

## 1. Q4 ENSANUT: a preserved conditioning pattern with remaining scale mismatch

The target analytical standard is equal mass in eight recorded-sex-by-age cells among 6,931 selected adults aged25–79, without reported prior diabetes/high-blood-sugar diagnosis, with a recorded8–12h fast and serum glucose below126mg/dL. There was no verified medication or anemia exclusion. It is not a nationally weighted regression. Age effects adjust for recorded sex, BMI and glucose; BMI effects adjust for age/sex before and after adding glucose. All slopes below are HbA1c percentage points per stated increment.

| Primary analysis | Sample reference | E01 mean [seed min,max] | E02 mean [seed min,max] |
|---|---:|---:|---:|
| Age per10years, fully adjusted | 0.07513 | 0.10308 [0.10155, 0.10431] | 0.09772 [0.09495, 0.09913] |
| BMI per5kg/m², age/sex adjusted | 0.08364 | 0.09165 [0.08994, 0.09441] | 0.07140 [0.07123, 0.07156] |
| BMI per5kg/m², additionally glucose adjusted | 0.05664 | 0.07509 [0.07201, 0.07666] | 0.04733 [0.04502, 0.04859] |

Every one of the18 primary seed estimates is positive. Every one of the six tables has a lower BMI coefficient after glucose adjustment. This second statement is a tested relationship between analyses on the same generated records, not merely a statement that regressions completed. It supports exploratory reproduction of this specified association pattern. It is not evidence of glucose causing or mediating the BMI–HbA1c relation.

| Additional analysis/necessary diagnostic | Sample reference | E01 mean [seed min,max] | E02 mean [seed min,max] |
|---|---:|---:|---:|
| BMI coefficient decrease after glucose adjustment, pp/5kg/m² | 0.02701 | 0.01656 [0.01394, 0.01794] | 0.02407 [0.02281, 0.02621] |
| Glucose coefficient adjusted age/sex, pp/10mg/dL | 0.11420 | 0.05500 [0.05108, 0.05937] | 0.13047 [0.12815, 0.13247] |
| Full-model residual HbA1c RMS, pp | 0.48848 | 0.29502 [0.29455, 0.29542] | 0.32380 [0.32218, 0.32701] |
| HbA1c population SD, pp | 0.52738 | 0.36249 [0.36125, 0.36491] | 0.40568 [0.40229, 0.40878] |
| BMI population SD, kg/m² | 5.52110 | 3.76862 [3.68465, 3.85325] | 4.97743 [4.89472, 5.10800] |
| Glucose population SD, mg/dL | 11.93680 | 13.00697 [12.88079, 13.08429] | 11.08817 [10.94752, 11.19718] |
| HbA1c mean, pp | 5.31414 | 5.42033 [5.41713, 5.42467] | 5.47241 [5.46925, 5.47443] |

The descriptive magnitude picture is mixed. Both age coefficients exceed the sample point: E01 by0.02795pp/decade (37.2%), E02 by0.02259 (30.1%). The reduced BMI coefficients differ by+0.00801 and−0.01224pp/5kg/m² (approximately+9.6% and−14.6%); the fully adjusted coefficients differ by+0.01845 and−0.00931 (approximately+32.6% and−16.4%). These percentages describe a reference comparison, not prespecified errors or clinical tolerances. The attenuation amount is0.01656/0.02407 versus0.02701pp/5kg/m²; E02 is closer on that contrast, while its age and dispersion mismatches remain. No author is selected as universally successful.

Both HbA1c SDs are lower than the sample point (ratios0.687/0.769), as are residual RMS values (ratios0.604/0.663). This matters to uses requiring conditional variability, precision, power or predictive uncertainty. It is not proof of how much any new study would be biased: covariate distributions, dependence and source/transport uncertainty also matter. Glucose SD is higher in E01 and lower in E02, so these two cases do not establish universal variance shrinkage.

The reference bands are empirical cluster-resampling stability bands from399 fixed attempts, not national population confidence or acceptance regions. The saved primary bounds are age[0.06712,0.08219], reduced BMI[0.07037,0.09521], and full BMI[0.04390,0.06801]. These bands contextualize the native differences; this audit does not classify authors by overlap. Both authors chose age effects near0.10pp/decade and share some external literature, so repeated direction is not independent-source corroboration.

**Allowable use claim:** the two generated cohorts reproduce positive associations and the observed BMI attenuation after glucose adjustment in this selected analytical design, with quantified, analysis-specific magnitude and dispersion differences. **Not demonstrated:** unbiased effect estimation in a new population, causal mediation, individual HbA1c recovery, nationally representative prevalence, calibrated significance tests/prediction intervals or reliable power calculations from synthetic rows alone.

## 2. Current lipids: all constructors retained, relation magnitudes and stability remain uneven

Each law generated18+ adults in a Turkana-oriented analytical context with age, recorded sex, BMI, TC and HDL. Both BMI slopes adjust for age/sex; residual Pearson correlation adjusts both outcomes for age/sex/BMI. BMI slope units are mg/dL per5kg/m², SDs are mg/dL. The pooled real sample uses its observed site/lifestyle composition, not a universal lipid population.

| Initial author | BMI–TC | BMI–HDL | Residual r | TC SD | HDL SD | HDL>TC fraction |
|---|---:|---:|---:|---:|---:|---:|
| LIPID_BASE_R1 | 8.82872 | -1.15458 | 0.33079 | 37.80128 | 11.95921 | 0.00000 |
| LIPID_BASE_R2 | 14.61480 | -1.48962 | 0.35900 | 36.68682 | 13.13311 | 0.00000 |
| LIPID_BASE_R3 | 12.38309 | -2.31238 | 0.42330 | 35.77156 | 11.95865 | 0.00000 |
| LIPID_WORKFLOW_R1 | 9.93132 | -1.34819 | 0.14563 | 32.93603 | 11.37517 | 0.00011 |
| LIPID_WORKFLOW_R2 | 13.33703 | -0.01160 | 0.35605 | 42.19000 | 13.18085 | 0.00000 |
| LIPID_WORKFLOW_R3 | 8.81036 | -1.41417 | 0.31929 | 39.20889 | 12.27970 | 0.00000 |
| Existing sample reference | 5.68311 | -4.62300 | 0.51207 | 42.84657 | 20.17555 | unavailable |

All18 TC slopes and all18 residual correlations are positive. All six *mean* HDL slopes are negative, but only16/18 seed HDL slopes are negative. LIPID_WORKFLOW_R2 gives+0.03121,−0.14890,+0.08289 and averages−0.01160; its sign is unstable and magnitude near zero. Do not describe this as robust recovery of the negative HDL relationship merely because the mean has the desired sign.

All six mean TC slopes are larger than the sample point (8.810–14.615 versus5.683), all mean HDL-slope magnitudes are smaller (0.012–2.312 versus4.623), and all18 seed residual correlations remain below0.51207. Residual-correlation means are0.14563–0.42330, and all18 HDL SD values are below20.17555. Those differences identify limits of the current *sample-comparison profile*, without establishing population error or the same failure mechanism in every model. A near-reference TC SD, such as WORKFLOW_R2, does not rescue its nearly absent HDL–BMI relation.

The sample TC coefficient has a broad HC3 conditional-sensitivity interval[−3.75350,15.11972], and the HDL coefficient has[−8.39195,−0.85405]. TC’s population direction is therefore not established by the reference point alone. There is no available residual-correlation interval, and no interval was added here. Shared inclusion in a wide band is not evidence of equivalence or adequate data quality. The observed one HDL>TC row belongs to WORKFLOW_R1 at seed54003 and remains retained; zero violations in other finite draws do not certify every mathematical or physiological property.

**Allowable use claim:** the method autonomously produces fully analyzable paired-lipid records and exposes how individual constructions realize requested relations. Positive TC association and residual dependence recur, but quantitative dependence, HDL dispersion and one law’s HDL relation are not adequately established as substitutes for the measured sample. **Not demonstrated:** faithful joint-risk/co-occurrence estimates, calibrated inference on the lipid relationships, equivalence to real records or general usefulness for untested biomedical endpoints. This is not a declaration that the data have no use; it restricts the demonstrated use to the analyses and limitations actually examined.

## 3. Completed mathematical repair of the affected lipid law

The initial BASE_R2 law has a positive exponential TC contribution applied to shifted-lognormal BMI, so its ideal continuous positive TC moments diverge. Finite table regressions are runnable, but their existence cannot certify a corresponding finite-moment population regression. The defect is not the current endpoint of the work: **both already-completed R04 review branches repair it**. Ordinary review uses a positive affine BMI contribution; structured review uses log-BMI with positive HDL/non-HDL components. The independent fixed-specification audit supports finite positive polynomial measurement moments for both. These six paired repair tables are dependent continuations, not additional independent constructors.

| Analysis | Initial BASE_R2 | R04 ordinary review | R04 structured review | Sample reference |
|---|---:|---:|---:|---:|
| K02-TC-BMI | 14.61480 | 14.10641 | 13.36362 | 5.68311 |
| K02-HDL-BMI | -1.48962 | -1.48962 | -1.51102 | -4.62300 |
| K02-LIPID-RESIDUAL | 0.35900 | 0.35938 | 0.35838 | 0.51207 |
| total_cholesterol.sd_sample | 36.68682 | 36.50331 | 36.41752 | 42.84657 |
| hdl_cholesterol.sd_sample | 13.13311 | 13.13311 | 13.12470 | 20.17555 |

Both repaired BMI–TC means move closer to the sample point, while TC SD moves slightly farther and residual dependence remains about0.359. The structured HDL slope changes slightly; ordinary leaves it unchanged. Finite moments are a legitimate mathematical-quality gain, but not proof that missing target relationships were recovered. The ideal concentration ordering in the structured law is not an observed violation-rate improvement here: initial BASE_R2 already had zero observed violations. Neither repair branch is chosen as a winner. Their source covariance remains assumption-dependent.

## 4. Wording and practical decision for the review brief

Prefer: “Generated ENSANUT cohorts retained positive conditional associations and the BMI attenuation after glucose adjustment across both constructions and all saved seeds; effect magnitudes and conditional dispersion remained imperfect. Autonomous lipid cohorts were executable, but their analysis-specific profiles exposed weaker residual dependence/HDL dispersion and one unstable HDL association. Subsequent checks repaired an ideal-law moment defect without broadly repairing the joint-analysis profile.”

Avoid collapsing these into “all analyses were supported” or “all directions reproduced.” Say exactly which pattern, author/seed scope and scientific use are demonstrated. The data are defensible for transparent scenario exploration and reproducing the named association patterns under stated assumptions; this is distinct from providing new clinical evidence. No new use threshold, pass rate, broad failure theory or causal attribution to evidence indirectness is justified by this bounded re-interpretation. A biomedical reviewer should assess the practical importance of each native-unit discrepancy and which intended use actually needs the missing dispersion/dependence; that judgment is not supplied by an arbitrary numerical cutoff.

## Appendix: every primary seed with essential dispersion

### Q4 ENSANUT, six tables

| Author | Seed | Age/10y | BMI/5 | BMI/5 +glucose | Attenuation | Residual RMS | HbA1c SD |
|---|---:|---:|---:|---:|---:|---:|---:|
| E01 | 8101 | 0.10339 | 0.09441 | 0.07660 | 0.01781 | 0.29542 | 0.36491 |
| E01 | 8102 | 0.10431 | 0.09060 | 0.07666 | 0.01394 | 0.29509 | 0.36129 |
| E01 | 8103 | 0.10155 | 0.08994 | 0.07201 | 0.01794 | 0.29455 | 0.36125 |
| E02 | 8101 | 0.09913 | 0.07156 | 0.04836 | 0.02320 | 0.32221 | 0.40878 |
| E02 | 8102 | 0.09909 | 0.07123 | 0.04502 | 0.02621 | 0.32218 | 0.40597 |
| E02 | 8103 | 0.09495 | 0.07140 | 0.04859 | 0.02281 | 0.32701 | 0.40229 |

### Current lipids, all eighteen initial tables

| Author | Seed | BMI–TC | BMI–HDL | Residual r | TC SD | HDL SD | HDL>TC fraction |
|---|---:|---:|---:|---:|---:|---:|---:|
| LIPID_BASE_R1 | 54001 | 7.75488 | -1.53047 | 0.32533 | 37.94155 | 12.08468 | 0.00000 |
| LIPID_BASE_R1 | 54003 | 10.40563 | -0.74699 | 0.34924 | 37.59234 | 12.09551 | 0.00000 |
| LIPID_BASE_R1 | 54007 | 8.32564 | -1.18628 | 0.31780 | 37.86996 | 11.69745 | 0.00000 |
| LIPID_BASE_R2 | 54001 | 13.98958 | -1.78680 | 0.34416 | 36.44741 | 13.19978 | 0.00000 |
| LIPID_BASE_R2 | 54003 | 16.06049 | -1.01226 | 0.39204 | 37.18836 | 13.27305 | 0.00000 |
| LIPID_BASE_R2 | 54007 | 13.79434 | -1.66980 | 0.34079 | 36.42470 | 12.92651 | 0.00000 |
| LIPID_BASE_R3 | 54001 | 11.80572 | -2.85388 | 0.42017 | 37.10258 | 11.98142 | 0.00000 |
| LIPID_BASE_R3 | 54003 | 12.88851 | -1.93618 | 0.42951 | 35.56371 | 11.85355 | 0.00000 |
| LIPID_BASE_R3 | 54007 | 12.45505 | -2.14707 | 0.42023 | 34.64839 | 12.04099 | 0.00000 |
| LIPID_WORKFLOW_R1 | 54001 | 8.66918 | -1.76570 | 0.14919 | 33.37339 | 11.49045 | 0.00000 |
| LIPID_WORKFLOW_R1 | 54003 | 9.70368 | -0.86665 | 0.13321 | 32.08903 | 11.22680 | 0.00033 |
| LIPID_WORKFLOW_R1 | 54007 | 11.42109 | -1.41222 | 0.15449 | 33.34568 | 11.40827 | 0.00000 |
| LIPID_WORKFLOW_R2 | 54001 | 13.06936 | 0.03121 | 0.34319 | 42.45813 | 13.12020 | 0.00000 |
| LIPID_WORKFLOW_R2 | 54003 | 12.98261 | -0.14890 | 0.37211 | 41.32468 | 13.37541 | 0.00000 |
| LIPID_WORKFLOW_R2 | 54007 | 13.95914 | 0.08289 | 0.35284 | 42.78720 | 13.04695 | 0.00000 |
| LIPID_WORKFLOW_R3 | 54001 | 8.67269 | -1.43557 | 0.33592 | 39.52274 | 12.30380 | 0.00000 |
| LIPID_WORKFLOW_R3 | 54003 | 7.51240 | -1.52372 | 0.30253 | 38.62179 | 12.26427 | 0.00000 |
| LIPID_WORKFLOW_R3 | 54007 | 10.24598 | -1.28323 | 0.31941 | 39.48214 | 12.27104 | 0.00000 |

### Dependent R04 repairs, all six tables

| Review branch | Seed | BMI–TC | BMI–HDL | Residual r | TC SD | HDL SD | HDL>TC fraction |
|---|---:|---:|---:|---:|---:|---:|---:|
| R04_GENERIC | 54001 | 13.52214 | -1.78680 | 0.34473 | 36.27105 | 13.19978 | 0.00000 |
| R04_GENERIC | 54003 | 15.49945 | -1.01226 | 0.39218 | 36.97773 | 13.27305 | 0.00000 |
| R04_GENERIC | 54007 | 13.29763 | -1.66980 | 0.34123 | 36.26116 | 12.92651 | 0.00000 |
| R04_STRUCTURED | 54001 | 12.62988 | -1.73640 | 0.35455 | 36.21686 | 13.30221 | 0.00000 |
| R04_STRUCTURED | 54003 | 15.01116 | -1.19723 | 0.38589 | 37.24988 | 13.04518 | 0.00000 |
| R04_STRUCTURED | 54007 | 12.44983 | -1.59945 | 0.33470 | 35.78583 | 13.02671 | 0.00000 |

## Audit boundary and provenance

This audit reconciles saved endpoint CSV/JSON records, recomputes summaries and the algebraic attenuation contrast, and reuses previously completed numerical/source-code audits. It does not call the generation models, inspect patient records, regenerate rows, refit clinical models or modify frozen artifacts. A passed reconciliation means the brief numbers are bound to the existing records, not that a virtual cohort has passed a medical-quality criterion. The JSON companion retains input hashes, exact numeric records, reference conventions, all selected seed values and checks.
