# External evidence packet: adult systolic and diastolic blood pressure

Status: source audit complete, 2026-11-09. This packet contains external reported facts and clearly labelled algebra, not a fitted model, parameter prescription, target-data summary, or validation threshold. All PNS/National Health Survey target-outcome studies are excluded. The requested task covers ages 20–79 and whole synthetic rows of age, female, BMI (kg/m²), SBP and DBP (mmHg). Three planned analyses concern age/sex-adjusted BMI slopes for SBP and DBP, and correlation of the paired residuals. The frozen task protocol governs exact computation.

## S1. INTERSALT: original cross-sectional report

Intersalt Cooperative Research Group. BMJ 1988;297:319–328. [Original report](https://pmc.ncbi.nlm.nih.gov/articles/PMC1834069/); DOI 10.1136/bmj.297.6644.319. Local original: `_local_only/sources/INTERSALT_BMJ1988_p319.png` through `p328.png` (all ten pages).

Population: 10,079 men and women, ages 20–59, 52 centres/32 countries; diverse community and workforce sampling. The report retains people receiving antihypertensives. Seated BP was measured twice with a Hawksley random-zero instrument after five minutes’ rest; the participant average was analysed. Height and weight were measured twice; BMI is kg/m². See pp319–320.

**Table II, p322: reported within-centre BMI coefficients, pooled by inverse variance.** Adjustments: age, sex, urinary sodium and potassium, and two alcohol-intake indicators. These observational coefficients have more adjustment than the task regression.

| Outcome | Reported coefficient, mmHg per kg/m² BMI | Reported SE | Algebraic rescaling to +5 kg/m²: coefficient (SE) |
|---|---:|---:|---:|
| SBP | 0.7754 | 0.0359 | 3.8770 (0.1795) |
| DBP | 0.5967 | 0.0257 | 2.9835 (0.1285) |

The reported SE concerns the pooled source estimate; it does not quantify transfer uncertainty to another population. Table II does not supply a residual correlation or residual SD.

**Appendix II, p327: illustrative source context, all centres retained in the original page.** The following three rows were transcribed for legibility and geographic context, not similarity to any unseen target. They are not selected validation references or a proposed mixture.

| Centre | N | SBP mean (SD), mmHg | DBP mean (SD), mmHg | BMI mean (SD), kg/m² |
|---|---:|---:|---:|---:|
| Argentina | 200 | 116.1 (14.3) | 72.8 (12.6) | 25.0 (3.8) |
| Japan, Osaka | 197 | 116.5 (14.7) | 68.6 (11.5) | 21.6 (2.4) |
| United Kingdom, Belfast | 200 | 120.3 (13.7) | 73.8 (10.7) | 24.8 (4.0) |

**Definition matters:** the table averages means and SDs calculated separately for men 20–39, men 40–59, women 20–39 and women 40–59. These displayed SDs are averages of subgroup SDs, not unconditional pooled SDs. Neither pooled variance nor an age/sex covariance matrix can be recovered from these entries alone. The complete table includes all centres, including geographically isolated populations; none was discarded because of its numerical result.

## S2. Beijing Longitudinal Study of Aging

Zhang et al. J Clin Hypertens 2022; DOI 10.1111/jch.14529. [Original report](https://pmc.ncbi.nlm.nih.gov/articles/PMC9278591/). Local full text: `_local_only/sources/PMC9278591.xml` (readable extraction `.txt`).

Methods §§2–2.2, Table 1: 2009 Beijing community baseline, selected middle-aged/older participants. Prior myocardial infarction, stroke or severe heart failure and substantial blood-sample refusal/missingness reduced inclusion to 1,257. Antihypertensive use was retained. Omron HEM-4021, seated non-dominant arm after five minutes’ rest; average of two measurements within two minutes. Exact minimum/maximum age is not established by this extraction. Table entries below are unadjusted means and individual SDs, not SEs; no sampling CIs are supplied for these moments.

| Group | N | Age mean (SD), years | Male, n (%) | SBP mean (SD) | DBP mean (SD) | PP mean (SD) |
|---|---:|---:|---:|---:|---:|---:|
| All | 1257 | 69.16 (8.10) | 550 (43.76) | 138.93 (20.35) | 76.68 (10.93) | 62.25 (17.20) |
| <65 years | 466 | 60.51 (2.95) | 194 (41.63) | 134.98 (18.61) | 78.45 (10.21) | 56.53 (14.88) |
| ≥65 years | 791 | 74.26 (5.37) | 356 (45.01) | 141.29 (20.98) | 75.63 (11.22) | 65.66 (17.59) |

BP/PP units: mmHg. PP=SBP−DBP. The age-group contrasts are descriptive, not adjusted age effects. No BMI or BMI–BP coefficient is supplied here.

**Derived, not reported:** on the same complete paired observations, Cov(SBP,DBP)=(SD_SBP²+SD_DBP²−SD_PP²)/2. The rounded table yields raw correlations 0.534443 overall, 0.603032 below65, and 0.545126 at65+. These are not correlations after adjustment for age, sex or BMI. No sampling CI is identified. `_local_only/sources/derive_reported_moments.py` reproduces the algebra.

## S3. INTERMAP: methods and demographics only

Stamler et al. J Hum Hypertens 2003;17:591–608; DOI 10.1038/sj.jhh.1001603. [Original report](https://pmc.ncbi.nlm.nih.gov/articles/PMC6660162/). Retained reading receipt: `_local_only/sources/INTERMAP_WEB_METHODS_RECEIPT.txt`; a standalone full-text download was not obtained.

Methods and Table5: 4,680 participants aged40–59 from17 general-population/workforce samples in China, Japan, UK and USA, approximately balanced across four age/sex groups. Average age49.2 (SD5.5), women2321/4680. Each person’s BP averaged eight seated random-zero readings over four visits, after ≥5-minute rest; height/weight were measured at visits1 and3. Thus its measurement averaging differs from a single-visit BP release. Incomplete visits/diet/urine/protocol data were excluded and replacements recruited. The report does not provide original INTERMAP BP/BMI moments or BMI slopes; its INTERSALT summary tables are not independent replication. The separately published Appendix Tables were not acquired, so no statistics were copied from their snippets.

## Quantities that remain unidentified

- The target population’s age/sex/BMI distribution and their dependence; treatment/selection effects and transfer across countries, eras and age ranges.
- A complete age20–79 conditional BP surface, including adjusted sex contrasts, nonlinear age patterns and age-by-BMI interactions. Between-group means do not identify these coefficients.
- The task’s age/sex-only, weighted BMI coefficients. Richer-adjustment source coefficients cannot be equated to them without an assumption about omitted covariates and weighting.
- Residual SBP–DBP dependence and conditional residual scales. Raw covariance is reduced by the covariance explained by the chosen design matrix; that component is not supplied. It is invalid simply to relabel the Beijing raw correlation as a residual correlation.
- Full unconditional variances from INTERSALT’s averaged subgroup SDs; individual-level distributional shapes, tails and missingness mechanisms; uncertainty of cross-population transfer.

These gaps require declared construction assumptions, not invented literature estimates. Different defensible choices remain possible. This packet neither selects an author’s model nor supplies evidence of successful validation.
