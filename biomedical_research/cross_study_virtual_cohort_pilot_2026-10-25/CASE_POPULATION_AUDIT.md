# Public population-cohort case audit

Date: 25 October 2026 (America/Chicago). Scope: candidate selection, actual public-file access, schema and nonmissing counts. No target means, correlations, regressions, effect estimates, model fitting or synthetic generation were computed. At the parent's follow-up request, the verified modest raw files were saved locally after the initial in-memory audit. Counts below are file/availability counts, not effect-analysis results.

Local paths (relative to this audit's directory; all saved bytes match the SHA256 values below):

- `data/source/rich_healthcare/RC_Health_Care_Data-20180820.xlsx`.
- `data/target_reserved/nagala/Data_set_Int_J_Obesity.xlsx`.
- `data/source/nhanes2011_2012/{DEMO_G,BMX_G,GLU_G,TRIGLY_G,HDL_G,BIOPRO_G,DIQ_G}.XPT`.

The target directory is an organizational boundary, not an enforced filesystem access control. Do not let candidate methods read it. Total distinct raw files are approximately 44 MB; no cohort relationships were computed.

## Recommended first case

**Two independent source studies (Rich Healthcare, China, and NHANES 2011–2012, USA) → held-out NAGALA baseline triglyceride relationships, Japan.**

All three have actual, anonymously downloadable participant files; access to the relevant files was verified, not merely inferred from a paper's data-availability statement. They are different recruitment systems and countries. No participant overlap is expected by design, although there is no cross-dataset person identifier with which to prove zero overlap. This is a genuine cross-study transfer case, unlike two NHANES cycles.

The benchmark question can be: given restricted evidence from the two source studies and permitted target-population covariate summaries, can a method predict the **age-, sex- and fasting-glucose-adjusted baseline BMI–log(triglyceride) association** in NAGALA? This is a method evaluation of a withheld association, not a claim that the BMI–lipid relationship itself is new. The target is concurrent and observational, not incident-diabetes risk or a causal BMI effect.

Use adults aged 20–75, available BMI, age, recorded sex, fasting plasma glucose and triglycerides; a common FPG <6.1 mmol/L restriction can reduce the most obvious eligibility mismatch. Freeze exact inclusion rules and the model formula before target outcome inspection. Do not call the entire sample an obesity cohort: many participants are lean. A later BMI ≥25 sensitivity would need a coverage check and should not become a selectively reported subgroup.

Important residual mismatch: NAGALA excluded participants taking medication and with substantial alcohol intake and other conditions; Rich lacks a medication variable in its released workbook. NHANES medication modules exist but were not audited here. Common age/FPG restrictions do not harmonize every eligibility difference. The model should report transport uncertainty; these datasets must not simply be pooled as exchangeable rows.

## 1. Rich Healthcare Chinese cohort: verified source

- Original paper: Chen et al., *Association of body mass index and age with incident diabetes in Chinese adults: a population-based cohort study*, BMJ Open 2018. [Paper](https://bmjopen.bmj.com/content/8/9/e021768); [PubMed](https://pubmed.ncbi.nlm.nih.gov/30269064/).
- [Original Dryad deposit](https://datadryad.org/dataset/doi:10.5061/dryad.ft8750v).
- [Zenodo deposit carrying the same original DOI and checksum](https://zenodo.org/records/4997196).
- Actual working file endpoint: <https://zenodo.org/api/records/4997196/files/RC%20Health%20Care%20Data-20180820.xlsx/content>.
- File: `RC Health Care Data-20180820.xlsx`, 28,340,131 bytes. HTTP 200, valid XLSX.
- MD5: `b468cc3704b11ba1bd21532451fe2856`, matching the original Dryad file metadata.
- SHA256: `ffd341a1a91ac65585b9fba70847a2681f5671a6035d9cfbf92e50795d74fbf6`.
- Workbook: sheet `RC`, 211,834 rows including header, 25 columns; **211,833 participant rows**. This agrees with the original paper's analytic cohort, not its larger initial recruitment pool.
- Recruitment: adult health-check attendees across 32 sites/11 Chinese cities, 2010–2016, without diabetes at baseline; retained participants had repeated health examinations. This is not a random sample of all Chinese adults.

Actual fields needed for the pilot:

| Workbook column | Units / coding | Nonmissing rows |
|---|---|---:|
| `Age (y)` | years | 211,833 |
| `Gender(1, male; 2, female)` | recorded sex | 211,833 |
| `BMI(kg/m2)` | kg/m² | 211,833 |
| `SBP(mmHg)` | mmHg | 211,810 |
| `DBP(mmHg)` | mmHg | 211,809 |
| `FPG (mmol/L)` | mmol/L, baseline | 211,833 |
| `Triglyceride(mmol/L)` | mmol/L | 206,946 |
| `Cholesterol(mmol/L)` | mmol/L | 206,979 |
| `HDL-c(mmol/L)` | mmol/L | 117,271 |
| `LDL(mmol/L)` | mmol/L | 118,412 |
| `ALT(U/L)` | U/L | 210,051 |
| `AST(U/L)` | U/L | 88,543 |

Other fields include site, height, weight, renal markers, final-visit FPG, incident-diabetes indicator, follow-up years, smoking, drinking and diabetes family history. Smoking and drinking have only 60,230 nonmissing rows each. **Prefer TG over an HDL-dependent primary endpoint:** using HDL would discard a large, potentially selected subset. Do not fill missing clinical values with Agent guesses and then treat them as observations.

Dryad public web download returned HTTP 403 in this environment; its API metadata worked, but its API download endpoint required authorization (401). This was resolved using the openly downloadable Zenodo deposit, which has the exact matching original file checksum. No credentials, applications or author contact were needed.

## 2. NAGALA Japanese cohort: verified held-out target

- Original paper: Okamura et al., *Ectopic fat obesity presents the greatest risk for incident type 2 diabetes: a population-based longitudinal study*, International Journal of Obesity. [Paper DOI](https://doi.org/10.1038/s41366-018-0076-3).
- [Original Dryad deposit](https://datadryad.org/dataset/doi:10.5061/dryad.8q0p192).
- [Zenodo deposit carrying the same DOI](https://zenodo.org/records/4996032); metadata license: CC0.
- Actual working file endpoint: <https://zenodo.org/api/records/4996032/files/Data%20set%20Int%20J%20Obesity.xlsx/content>.
- File: `Data set Int J Obesity.xlsx`, 3,255,571 bytes. HTTP 200, valid XLSX.
- MD5: `47edfb147078657a0eecfff7f9364532`, matching Dryad metadata.
- SHA256: `671359aea2019c848f969395f88e57f888eaba8463ea0351bcda8f1c947f5523`.
- Workbook: sheet `Sheet 1`, 15,465 rows including header, 31 columns; **15,464 participant rows**.
- Medical examination cohort at Murakami Memorial Hospital, Gifu, Japan, 2004–2015; historical cohort with at least two examinations. It is not nationally representative.
- Original eligibility excludes diabetes/IFG (FPG ≥6.1 mmol/L), baseline medication use, heavy drinking, viral hepatitis and relevant missing data. Exact implementation must be taken from the original Methods, not reconstructed from a secondary paper's paraphrase.

Verified common columns (all 15,464 nonmissing in their SI-unit versions):

`Sex, 1:Men, 2:Women`; `Baseline Age, yrs`; `Baseline BMI, kg/m2`; `Baseline Waist circumference(WC), cm`; `Baseline ALT, IU/L`; `Baseline AST, IU/L`; `Baseline Body Weight, kg`; `Baseline GGT, IU/L`; `Baseline HDL-cholesterol, mmol/L`; `Baseline Total Cholesterol, mmol/L`; `Baseline Triglycerides, mmol/L`; `Baseline Fasting plasma glucose, mmol/L`; `Baseline Systolic blood pressure, mmHg`; `Baseline Diastolic blood pressure, mmHg`.

Additional fields include alcohol, smoking, exercise, ultrasound fatty liver, HbA1c, follow-up days and incident diabetes. Paired mg/dL and SI columns exist for several analytes. The HDL mg/dL column has 15,453 observed values versus 15,464 for mmol/L: use the prespecified SI field, not a rowwise mixture selected after seeing results.

Neither raw participant values nor outcome summaries were printed. Header names, dimensions, file hashes and nonmissing counts were the only workbook outputs. Reading the dataset landing page necessarily exposed the published abstract's existing incident-diabetes result; the proposed withheld endpoint is a different baseline relationship. This does not eliminate potential LLM pretraining contamination: the dataset and many secondary analyses are public and old.

## 3. NHANES 2011–2012: verified second source

Source-only use is appropriate because previous workspace work has already used NHANES modules and older NHANES 2015–2018 pilot results have been inspected. **Do not relabel any of those prior development data as untouched validation.** Other NHANES years remain the same survey program, even if their participants differ.

All of the following actual XPT files returned HTTP 200 and parsed successfully in memory. Use this URL pattern:

`https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/{MODULE}.XPT`

| Module | File rows | Fields for this task |
|---|---:|---|
| DEMO_G | 9,756 | SEQN, RIDAGEYR, RIAGENDR, RIDRETH3, SDMVPSU, SDMVSTRA |
| BMX_G | 9,338 | SEQN, BMXBMI, BMXWT, BMXHT, BMXWAIST |
| GLU_G | 3,239 | SEQN, LBDGLUSI, WTSAF2YR, PHAFSTHR, PHAFSTMN |
| TRIGLY_G | 3,239 | SEQN, LBDTRSI, WTSAF2YR |
| HDL_G | 7,821 | SEQN, LBDHDDSI |
| BIOPRO_G | 6,549 | SEQN, LBXSATSI (ALT), LBXSASSI (AST) |
| DIQ_G | 9,364 | SEQN, DIQ010 and diabetes treatment questions |

A metadata-only coverage audit joined these files one-to-one on SEQN: 3,239 records; 1,608 with age 20–75, FPG <6.1 mmol/L, `DIQ010 == 2` (no reported diabetes), and not known pregnant; 1,536 additionally fasting at least 8.5 but less than 24 hours with positive fasting weight; **1,509 additionally had all primary BMI/age/sex/FPG/TG fields observed**. These are provisional eligibility counts, not a finalized protocol or an association analysis. The corresponding NAGALA age 20–75 coverage is **15,450**, all with primary fields observed. The Rich restricted-sample count has not been computed.

Retain the special fasting weights. Source summaries for a national estimand must use survey design, strata and PSU as appropriate, rather than treating these rows as an ordinary convenience sample. Alternatively, the pilot can explicitly target the selected observed source cohort descriptively and avoid any US-population claim; using no weights must then be stated consistently. There is no need to claim a US-national estimand for the Japanese target. Survey versus clinic recruitment remains a real transport difference under either choice.

Use measured plasma glucose in GLU_G, not the similarly named serum glucose in BIOPRO_G. Use the reference triglyceride measurement in TRIGLY_G, not LBXSTR in the biochemistry module. These distinctions are explicitly documented by CDC:

- [GLU_G official codebook](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/GLU_G.htm).
- [TRIGLY_G official codebook](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/TRIGLY_G.htm).
- [BPX_G official codebook](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/BPX_G.htm): repeated BP readings; the chosen aggregation must be fixed. The BPX raw file was not downloaded in this audit.

Verified SHA256 values:

| Module | SHA256 |
|---|---|
| DEMO_G | eaf0525d1952626885af3e935415a1f66ad62c18698080e7354789c125af252d |
| BMX_G | 4814bfc3047ed400b9d43d285f8c3ea7c940ac6489404a9b699579715d158ec3 |
| GLU_G | e9c3816dbdfc21cd53a23d63c3610d2550662ee41a21df0a5b72c4a16cd1a8fd |
| TRIGLY_G | 4b7f9c73f5169f8bb582823d00a8e488d6985ea9d8784f85ee63ff60179589a0 |
| HDL_G | ffc060d394cc487f3206462fdfc77648bdbdd6e279bfc5dd8e9cbba3ccdcac4f |
| BIOPRO_G | 8c3a0b1bea79ff79c5600ad6a76c4206a7d689479f94ae81da6360058eda5d05 |
| DIQ_G | a9d5475e0cd66d6a7bc30230345ed0172a9abcbc0a7a4145a35025c827a52a87 |

## Minimal experiment recommended to the parent

1. **Freeze one primary estimand:** the BMI coefficient per 5 kg/m² in the prespecified descriptive target regression `log(TG mmol/L) ~ BMI + age + recorded sex + FPG`, with a continuous, consistently coded sample. A standardized BMI contrast is an alternative, but choose only one primary definition before computing target outcomes. Any nonlinear or interaction analyses should be a short frozen secondary set, not a search for the favorable result.
2. **Create one common evidence packet** from both source studies. For the first reproducible test, supply source-publication metadata plus prespecified, machine-readable summary panels computed from source participant data; mark this as controlled aggregate evidence rather than claiming a literature-only system. Avoid giving every cross-moment needed to algebraically reconstruct the target answer. Source summaries may include BMI–lipid information from one study and glucose–lipid/age–sex composition from another. Specify the panels before looking at target TG.
3. **Allowed target information:** recruitment/measurement protocol, eligibility and a prespecified limited set of age/sex/BMI/FPG covariate summaries. Do not provide target TG mean, spread, prevalence, regression coefficient or TG-related covariance. All methods receive exactly the same packet. If target covariate summaries are used, call the test target-informed transport, not zero-shot transfer.
4. **Three requested comparators:** direct Agent estimating the frozen quantity and uncertainty without generating rows; the same Agent constructing a numerical cohort-generating model; a capable statistical constrained joint or copula synthesis model with uncertainty, fitted only to the same packet. For the conventional arm, use a sensible hierarchical/transport formulation rather than simple independent Gaussian sampling. If a fitted conventional joint model can integrate the quantity analytically, retaining that answer helps determine whether Monte Carlo generation adds anything.
5. **One clear diagnostic:** compare two-source versus each single-source input using the same endpoints. This tests whether the method actually uses the second study and whether incompatible evidence harms it. The smaller repeated-generator runs quantify computational variability, not independent biomedical validation.
6. **Only after predictions are frozen**, compute target estimates with participant bootstrap uncertainty and score prediction error and interval score. Generated-row count is not evidential sample size. Three target quantities or repeated random seeds cannot establish calibrated coverage on a broad task population.

The actual final numbers for the target and source evidence packet have not been calculated here. The task is feasible with standard CPU data processing; no training or HPC is needed.

## Second case or stress test using this resource family

A reciprocal fold could use **NHANES + NAGALA as sources → Rich as target**, predicting a baseline BMI–ALT or BMI–TG conditional association. ALT has 210,051 nonmissing Rich values, so it is more practical than HDL/AST. However, use all three cohorts in a **predeclared leave-one-study-out design** if choosing this route. Once Rich or NAGALA contributes outcomes to another fold, it is no longer an untouched dataset for an adaptive later hypothesis. Reusing these three studies provides multiple transfer tasks, not multiple fully independent benchmark families.

For the user's requested 2–3 diverse cases, pair this population-transport case with another genuinely distinct study family (e.g., two intervention trials with comparable measurements). Do not inflate the case count by calling TG, BP and ALT in the same cohort three independent studies.

## Options not classified as immediately ready

- **KNHANES:** official site is live and describes SAS/SPSS public microdata with terms/security pledges; the actual anonymous raw-file route was not verified. [Official portal](https://knhanes.kdca.go.kr/knhanes/eng/main.do). Do not label access impossible, but do not promise a ready download based only on secondary papers.
- **CHNS:** a historically free source, but the official download-registration route was inaccessible in this audit; no current raw file or schema verified. [Official download route](https://www.cpc.unc.edu/projects/china/data/datasets/data-downloads-registration). It remains conditional, not a blocker for the first case.
- **NHANES temporal transfer:** technically easy, but new cycle ≠ independent study. Appropriate later as an easier transport condition, explicitly labelled temporal within-program validation.
- **UK Biobank, Framingham and other request-based cohorts:** not needed for the minimal test. No access assumptions should be made.

## Decision

**Proceed with this three-study population case at protocol/evidence-packet stage.** Access and matching baseline fields are verified. The key scientific limitation is population selection/measurement heterogeneity, which is part of what the method must handle and report, not a reason to silently harmonize away real differences. There is no result yet demonstrating an Agent or virtual-cohort advantage.

## Post-freeze correction: NAGALA sex coding (25 October 2026 local)

The original audit reported the workbook's literal column name `Sex, 1:Men, 2:Women` but did not inspect its code frequencies. **That header is misleading: the actual deposited values are 1 and 0, not 1 and 2.** Following the first evaluator failure, an independent repair audit read this sex column only and confirmed 8,430 values of 1 and 7,034 values of 0. These match the primary deposit's reported 8,430 men and 7,034 women. Use **1 = men, 0 = women; female = (value == 0)**. The earlier header-based interpretation must not be used for filtering.

The original target loader accepted only 1/2 and encoded female as code 2, thereby retaining men only and creating a constant zero sex covariate. Its first partial-correlation calculation consequently encountered a singular control covariance. The correction restores both sexes in the already intended target population; it does not change the scientific estimand, covariance controls, generated forecasts, bootstrap or scoring. No target associations were inspected for this independent repair audit.

Audit checks passed: the preserved `evaluate_attempt1.py` matches both the original forecast-freeze evaluator hash and `EVALUATOR_REPAIR.json`; the repaired evaluator matches its recorded hash; the forecast index, every frozen Agent artifact and every forecast NPZ remain byte-identical to the initial freeze. The code difference is confined to sex-code validation/mapping, the guarded logged resume path and its status field. The original target-open marker and forecast freeze remain intact, and the new repair-start file uses exclusive creation. The repaired run must be described as a transparently repaired evaluation after target access, with forecasts fixed before that access; these targets are not untouched for future adaptive work.
