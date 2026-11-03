# External evidence coverage and application audit

3 November 2026. Prepared for the new reference-assisted, whole-cohort CHNS pilot. All five requested variables—age, sex, BMI, fasting glucose and HbA1c—are generated. The separately supplied full CHNS reference-summary set is an explicitly permitted developmental input. Agreement with that exposed reference is reference consistency, not independent target validation. This audit contains external aggregate evidence and methodological qualifications; it prescribes no generating law, coefficient, sign, distribution or scientific parameter.

This is an independent reconciliation of existing authored extractions and original-source audits, including the 3 November Jansen addendum. It is **not a new original-paper verification**. No full original article text was located in the selected source directories; the authored audits document their earlier primary-source reads. No new browsing, literature fetch, numerical trial, generation or patient-level read occurred. New original-study/retrieval quota consumption: **0**. No old generator or model specification was opened.

## Source identity and status

All project paths below resolve under the exact root:

`P = D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/virtual_cohort_system`.

| Existing source ID | Primary source and original locators | Current authored source artifact |
|---|---|---|
| `S_BAO_2010` | Bao et al., BMJ 2010;340:c2249; [doi:10.1136/bmj.c2249](https://www.bmj.com/content/340/bmj.c2249). Methods/Study design, Anthropometric and biochemical measurements, Statistical analysis; Table 1; Results immediately after Table 1. | `P/work/chns_admission_2026-11-01/f2/sources/BAO_2010.md` |
| `S_MIND_2024` | Wang et al., PLOS ONE 2024; [doi:10.1371/journal.pone.0296694](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0296694). Methods; Table 1 total column; Results correlations. | `P/work/chns_admission_2026-11-01/f2/sources/MIND_2024.md` |
| `S_JANSEN_2013` | Jansen et al., Lifelines; [doi:10.1111/joim.12010](https://onlinelibrary.wiley.com/doi/10.1111/joim.12010). Methods/participants, laboratory, statistics; Tables 1–3 and footnotes; Appendices A3–A4 for the historical sample-size audit. | `P/work/chns_admission_2026-11-01/f2/sources/JANSEN_2013.md` |
| `S_PANI_2008` | Pani et al.; [doi:10.2337/dc08-0577](https://pmc.ncbi.nlm.nih.gov/articles/PMC2551641/). Methods/Laboratory measurements, Statistical analysis/NHANES; Table 1; Results immediately before Table 2. | `P/work/chns_admission_2026-11-01/f2/sources/PANI_2008.md` |
| `S_NGSP_UNITS` | Official [NGSP IFCC guidance](https://ngsp.org/ifccngsp.asp), “The IFCC and NGSP”, Table 2. | `P/work/chns_admission_2026-11-01/f2/sources/NGSP_UNITS.md` |

The five artifacts have `screening: approved` in `P/work/chns_admission_2026-11-01/f2/registry.json`. Historical “review-ready” language remains inside frozen summaries. That registry approval concerns the old artifacts; it does not make every contextual statistic executable or approve transport automatically. This new audit expands readable context without rewriting the old registry or claiming a new executable-check admission.

Existing main item IDs are `E_BAO_PEARSON_GLUCOSE_HBA1C`, `E_MIND_SPEARMAN_SERUM_GLUCOSE_HBA1C`, `E_JANSEN_BMI_CONTEXT`, `E_JANSEN_GLUCOSE_CONTEXT`, `E_PANI_AGE_CONTEXT` and `E_NGSP_SCALE_CONTEXT`, in `P/work/chns_admission_2026-11-01/f2/evidence.json`. Additional restored numerical context below has no invented legacy item ID.

## Numerical evidence and its meaning

**Bao / SHDS II.** Six Shanghai communities, 2007–2008, multistage age-stratified design; analyzed n=4,886, comprising 1,828 men and 3,058 women. Previously diagnosed diabetes, missing questionnaires and ages below 20 were excluded; text saying “over 20” leaves the exact age-20 boundary unresolved. Cancer, severe psychiatric disturbance, chronic kidney disease, pregnancy and glucocorticoid treatment were listed exclusions. Screen-detected diabetes remained included. An observed upper survey age is not a support rule; no separate implemented anemia exclusion was established.

The named Pearson correlation is **r(HbA1c, fasting plasma glucose)=0.619**, P<0.001, unadjusted. Overall n is not a confirmed pair-specific n; no correlation SE/CI is supplied. Weighting and correlation missingness rules are unreported. Table 1 reports the following **median [Q1, Q3]**, except the explicitly labelled male BMI mean/SD:

| Variable | Overall | Men | Women | Unit |
|---|---|---|---|---|
| Age | 49.4 [37.9, 57.7] | 49.0 [37.4, 59.0] | 49.5 [38.2, 56.9] | years |
| BMI | 23.5 [21.4, 25.9] | Mean 24.1; individual SD 3.3 | 23.2 [21.2, 25.5] | kg/m² |
| Fasting plasma glucose | 5.2 [4.8, 5.6] | 5.2 [4.7, 5.6] | 5.2 [4.8, 5.6] | mmol/L |
| HbA1c | 5.6 [5.3, 5.9] | 5.6 [5.4, 5.9] | 5.6 [5.3, 5.8] | % |

Quartile endpoints are not SD, SE, range or confidence limits; quantile convention is unknown. The female fraction 3058/4886 is a **derived unweighted count ratio**, not a separately reported weighted population proportion. Measurements used a stated 10-hour overnight fast; plasma glucose by glucose oxidase; HbA1c by HPLC, printed instrument HLC-73G7, Tosoh; within-two-hour analysis. Quality-assessment participation does not establish NGSP/IFCC certification. The plasma specimen, source exclusions and Shanghai sampling differ from CHNS serum/all-diagnosis reference context. Neither r nor these margins supplies an adjusted slope, residual law, complete covariance or tail dependence.

**MIND-China.** Selected rural Yanlou, Shandong follow-up, n=3,547, ages 61–80, free of dementia and functional disability; known diabetes history included. Baseline demographics/BMI were obtained in 2018 and laboratory measures in April–May 2019. Missing laboratory/history records were excluded; mean/mode filling is reported without field-specific affected counts. Analytic weights and exact overnight-fasting duration are unreported.

Full-sample **Spearman rho(FSG, HbA1c)=0.529**, P<0.001, unadjusted. This is rank association, not Pearson correlation or an adjusted slope. Pair-specific n, SE/CI and tie convention are unreported. Table 1 total-column **mean / individual SD**: age **69.5 / 4.2 years**; BMI **25.0 / 3.6 kg/m²**; serum glucose FSG **5.2 / 1.4 mmol/L**; HbA1c **6.1 / 1.0%**. The 2049/3547 female count ratio is derived, not an independently weighted population proportion. SD divisor convention is unreported; individual SD is not estimator precision.

FSG uses a coagulant serum tube, glucose oxidase/CS-600B, local laboratory within two hours; HbA1c uses EDTA blood, HPLC/Huizhong MQ6000, an NGSP-certified KingMed laboratory within two days. Its separate FPG uses fluoride plasma/hexokinase elsewhere. The older selected rural population, processing and imputation differ from CHNS; shared specimen names do not establish measurement identity. The earlier audit also retains FPG–FSG and FPG–HbA1c rank associations, but these concern an additional plasma measurement outside this five-variable task and are not substitutes for the FSG statistic. Conflicting HbA1c composite-agreement numbers and dependent table-derived agreement quantities remain quarantined; they have not been reinstated here.

**Jansen / Lifelines.** Unrelated western-European adults with older family members preferred for GWAS, marginal cohort n=2,921. Exclusions: diabetes by self-report or FPG≥7.0 mmol/L, anemia thresholds (Hb<8.2 men/<7.0 women mmol/L), and missing HbA1c/erythrocytes/FPG. HbA1c is an IFCC-standardized immunoassay; fresh fasting plasma glucose uses hexokinase/G6PD. Exact age limits, fasting hours, analytic weighting and gender coefficient coding are unresolved.

Table 1 **mean / individual SD**: age **55.5 / 9.9 years**; BMI **26.5 / 4.1 kg/m²**; FPG **5.1 / 0.5 mmol/L**; HbA1c **5.6 / 0.3%**, separately printed as **38 / 3 mmol/mol**. These rounded reports should stay distinct. There are **1,176 males, 40.3%**; 1745/2921 females is derivable by subtraction only if the reported categories exhaust that cohort. Full-cohort margins are not established as the margins of every regression's complete-case sample.

All regression entries below are directly reported HbA1c coefficients in **mmol/mol per predictor unit**, preserved with their actual conditioning. Printed intervals are retained; their confidence level and model/row-specific n are not established. No SE or statistical weight is reconstructed.

| Original model / term | Coefficient | Printed interval | Other conditioning variables | Evidential role |
|---|---:|---|---|---|
| Table 2 baseline age | 0.11 per year | 0.10–0.12 | Gender | Restored relevant age evidence; baseline adjusted projection |
| Table 2 added BMI | 0.13 per kg/m² | 0.10–0.16 | Age, gender | Existing contextual item `E_JANSEN_BMI_CONTEXT` |
| Table 2 added FPG | 2.29 per mmol/L | 2.07–2.51 | Age, gender | Existing contextual item `E_JANSEN_GLUCOSE_CONTEXT` |
| Table 3 II age | 0.08 per year | 0.07–0.09 | Gender, FPG | Previously read, historically quarantined model; restored contextual visibility |
| Table 3 II FPG | 2.25 per mmol/L | 2.03–2.48 | Age, gender | Same Table 3 II model, not a second independent study |
| Table 3 III age | 0.07 per year | 0.06–0.09 | Gender, BMI, FPG, MCH, MCHC, smoking, alcohol | Broader conditioning than the task's age analysis |
| Table 3 III BMI | 0.05 per kg/m² | 0.02–0.08 | Age, gender, FPG, MCH, MCHC, smoking, alcohol | Broader conditioning than the task's BMI analysis |

Table 3 II also prints gender 0.35 (0.12–0.58), with unresolved coding, and R²=20.5%. These do not identify an oriented female effect or residual distribution. Alcohol has 89 missing; Table 2 alcohol n=2,832, with associated R²=9.6%; Table 3 I has the same R² and appendices total 2,832. Inferring n=2,832 for Table 3 I/II remains **an inference**, not a verified model count. The genotype call-rate threshold of 95% is unrelated to coefficient CI confidence level.

Table 2 BMI and FPG rows are separate added-predictor projections. They cannot be concatenated with the baseline age row into a recovered multivariable equation. Table 3 III cannot be reduced by deleting its additional adjustment variables. Missing intercept, coefficient covariance and residual law prevent recovery of a complete conditional data-generating mechanism; they do not erase the observed source associations. The age coefficients are neither the target age coefficient nor a mandatory target sign.

**Pani / NHANES.** NHANES 2001–2004, n=3,270, ages≥25, excluding self-reported diabetes and FPG≥126 mg/dL. Analyses account for the complex survey design and weights. HbA1c uses NGSP/DCCT-standardized HPLC and plasma glucose hexokinase; fasting hours are unspecified. Results immediately before Table 2 directly report **HbA1c age coefficient 0.010 percentage points/year**, adjusted for **sex, BMI and FPG**, P<0.001. Coefficient SE/CI and coefficient-specific complete-case n are unreported.

Table 1 restores useful **survey-estimated age-stratum means and mean SE**, without manufacturing individual dispersions:

| Age, years | n | HbA1c mean, % | Mean SE, percentage points |
|---|---:|---:|---:|
| <40 | 1037 | 5.20 | 0.01 |
| 40–44 | 330 | 5.28 | 0.02 |
| 45–49 | 322 | 5.37 | 0.02 |
| 50–54 | 261 | 5.40 | 0.02 |
| 55–59 | 198 | 5.44 | 0.02 |
| 60–64 | 283 | 5.46 | 0.03 |
| 65–69 | 198 | 5.50 | 0.03 |
| ≥70 | 641 | 5.51 | 0.02 |

These are unadjusted age-group means in the selected survey population; they are not the adjusted age slope or individual SDs. SE×sqrt(n) does not recover survey individual dispersion. The analysis has the same named adjustment variables as the task's age question, but survey weighting, restricted disease selection, plasma measurement and population differ. A generated equal-weight coefficient is not a faithful weighted source replay. The separate FOS coefficient additionally adjusts two-hour glucose; it remains outside the selected five-variable application. Demographic spread-label ambiguity and percentile discrepancies remain quarantined. Pani overlaps Liu's NHANES survey years; Liu is not imported or counted as independent replication here.

**NGSP representation relation.** Official relation: `HbA1c (%) = 0.09148 × HbA1c (mmol/mol) + 2.152`. This is deterministic unit context. Slopes, individual SDs, SEs and slope-interval endpoints multiply by 0.09148; levels/intercepts additionally use the offset; variances use the squared multiplier. All resulting values are **derived representations of the same evidence**, not new study estimates. Conversion does not establish assay comparability, population transfer, a fasting-glucose model or serum/plasma equivalence.

## Coverage, uncertainty and application

The historical age-evidence issue is **selective packet coverage and applicability**, not absence of published age evidence. The 31 October audit already records Jansen Table 3 II; its companion summary deliberately quarantined that model. The 1 November gap map retains the distinction. The 3 November original-source reread verifies Table 2 baseline age and Table 3 II/III age rows. The inspected history does not establish why Table 2 baseline age was omitted from F2. This audit restores visibility without retroactively changing the historical disposition.

| Task component | External evidence present | Remaining scientific choices / limitations |
|---|---|---|
| Age, sex and biomarker marginals | Bao quartiles/counts and sex-specific margins; MIND means/SDs/counts; Jansen means/SDs/counts; Pani age-specific HbA1c means/SEs | Different selections, age supports and observation periods. None independently supplies CHNS margins. Full supplied CHNS summaries may be used as declared developmental information. |
| HbA1c–glucose association | Bao unadjusted Pearson; MIND unadjusted Spearman; Jansen age/gender-adjusted projections | Different statistics, populations and serum/plasma measurements. No universal covariance or common conditional law is identified. |
| BMI association | Jansen Table 2 age/gender-adjusted BMI projection; Table 3 III broader model | Adding/removing glucose or other adjustment changes the estimand. No source-to-target coefficient equality is justified by this audit. |
| Age association | Jansen gender-adjusted, gender/FPG-adjusted and broader-adjusted age rows; Pani sex/BMI/FPG-adjusted survey slope and age-stratum means | Age evidence exists. Unweighted task coefficients and differently adjusted source coefficients remain distinct. No fixed sign rule is imposed. |
| Complete five-variable dependence | Partial margins and projections above; full CHNS reference summaries separately allowed | Nonlinearity, interactions, subgroup covariance, tails, residual heteroscedasticity and uncertainty in transport remain underidentified. Absence of a reported relation does not mean zero or independence. |

Reported precision, individual variation and model uncertainty have separate roles. P values do not recover coefficient SEs. Unknown CI levels, model n and coefficient covariances remain unknown. Multiple Jansen rows share a study; Pani strata and its age coefficient share respondents. Derived unit versions and count ratios add no independent evidence. Finite-draw variation or increasing generated n does not remove evidence, structural or transport uncertainty.

If numerical checks are chosen, their records should identify the original operator, conditioning, population/selection, units, weights and any approximation. A conventional equal-weight Pearson/Spearman calculation on generated rows, average-tie Spearman interpretation or unweighted OLS is a declared approximation when the original details are unknown or different. A supported computation does not by itself constitute source-population replay. The scientific author chooses whether and how to use these facts jointly, can report incompatibility, and can retain multiple plausible constructions within the task budget.

## Provenance and handoff

Additional local authored evidence read for this audit, with exact paths relative to P:

- `P/work/autonomous_research_cycle2_2026-10-31/evidence/INDEPENDENT_SOURCE_AUDIT.md`: primary-source reread, Tables 1–3, Pani operator, uncertainty and quarantine qualifications.
- `P/work/autonomous_research_cycle2_2026-10-31/evidence/packet/sources/JANSEN2013/source_summary.md`: Jansen margins and historical Table 3 quarantine.
- `P/work/autonomous_research_cycle2_2026-10-31/evidence/packet/sources/PANI2008/source_summary.md`: exact Pani Table 1 age-stratum values.
- `P/work/chns_admission_2026-11-01/evidence/BAO_2010_SOURCE_AUDIT.md`: Bao Table 1 subgroup summaries and measurement/selection definitions.
- `P/work/chns_admission_2026-11-01/evidence/MIND_2024_SOURCE_AUDIT.md`: MIND measurements, source timing and preserved conflict qualification.
- `P/work/chns_admission_2026-11-01/evidence/SOURCE_PACKAGE_REVIEW.md`: source-package review and status corrections; no renewed execution claim.
- `P/work/chns_admission_2026-11-01/evidence/REUSED_SOURCE_GAP_MAP.md`: historical conditional applicability and unresolved dependence.
- `P/docs/pro_evaluation_review_2026-11-03/INTERNAL_METHOD_AUDIT.md`, section “Source-coverage addendum — Jansen age evidence verified on 3 November 2026”: direct original-source verification of Table 2 age 0.11, Table 3 II age 0.08 and Table 3 III age 0.07; original model uncertainty retained.
- `P/docs/pro_evaluation_review_2026-11-03/REVIEW_SYNTHESIS.md` and `P/docs/NEXT_ACTIONS_AFTER_PRO_2026-11-03.md`: governing reference-assisted scope and distinction between contextual evidence and target law.

For the new scientific author, copy this audit and the five current f2 authored source summaries. The author needs their content, not historical generator/result directories or complete third-party papers. The new task contract supplies the separate CHNS aggregate input and permitted scientific work; the older literature-only prohibitions embedded in historical notes do not override the new explicit reference-assisted authorization. Keep source bodies/table images out of public export; this authored reconciliation and source locators suffice.

Access accounting: no raw participant data, original generator, old model specification or new target computation was accessed. The explicitly requested review documents contain historical method/result discussion. One recursive source-ID search also returned source-metadata snippets from old feedback JSON; no historical performance figures were incorporated into this audit. All scientific quantities above come from the named source summaries/audits. Existing closed budgets and records were not reset or edited. No AGENTS.md was found in the project/ancestors or work/docs during the scoped check.
