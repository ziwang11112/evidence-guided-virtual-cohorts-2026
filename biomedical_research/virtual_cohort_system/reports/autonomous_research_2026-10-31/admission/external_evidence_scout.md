# Bounded external aggregate-evidence scout

Date: 2026-10-31. Purpose: source-only feasibility assessment for whole-cohort generation; no source or target individual participant data (IPD) were accessed. This is a scouting record, not source-registry admission, a generator submission, target validation, or a biological finding.

## Scope, count, and access record

Four intended original papers were selected and read at methods/table level. Eight broad search queries preceded the fixed set; search-result snippets contained additional unselected titles. No fifth paper was deliberately added, and no further primary-paper search followed selection of the fourth. Paper/cohort identities below are SOURCE identities only. Their absence from all historical registries was not independently audited; the controller reported no known Japanese-source overlap.

There was one navigation deviation: a Frontiers supplemental-link click reused a numbered link after the page's numbering changed and unexpectedly returned the title/header of PubMed 26294660, an excluded Framingham publication. No abstract, result, table, or coefficient from that page was inspected or extracted. It is not evidence here. Consequently, this record distinguishes four substantive paper reads from that additional accidental title-only page opening; it does not claim a perfect four-page access count. No NAGALA/Dryad target record, target analysis, or target IPD was opened. Comparator/reference mentions of prohibited cohorts in search output were not used.

PMC initially returned browser-check pages. Cached original PMC tables and publisher HTML/PDF text subsequently supplied the listed evidence. JPHC PDF screenshots timed out. Oya web screenshot calls supplied no inspectable image; subsequently its PDF was fetched and rendered wholly in memory with PyMuPDF, and pages 942–943 were visually inspected. The printed threshold, assay description, Table 1, Table 2, and footnotes were verified. A Frontiers supplement named `Table_1.docx` was located in the same article's Europe PMC XML, but not retrieved or extracted. No article or IPD file was saved. In-memory direct HTTP reads were capped at 10 MiB; no download over 10 MiB was requested. Only this report was written; no STATE file was read or changed.

## Fixed source set

| Source ID | Original study and persistent identifier | Cohort aliases / overlap handling | Read depth |
|---|---|---|---|
| EXT_OYA2014 | Oya et al. *Effects of Age on Insulin Resistance and Secretion in Subjects without Diabetes*. Internal Medicine 53:941–947 (2014). [DOI 10.2169/internalmedicine.53.1580](https://doi.org/10.2169/internalmedicine.53.1580) | Saitama-ken Saiseikai Kurihashi / SSK / Kurihashi; Yamanouchi Hospital. Two source centers in ONE paper, not two independent replications. | Publisher PDF methods pp.942–943, Tables 1–2, including visual verification; later regression description inspected. |
| EXT_BABA2001 | Baba et al. *Anthropometric Measures, Blood Pressure and Major Laboratory Examination Results in the Health Check-up Examination among the JPHC Study Participants at Baseline Survey*. J Epidemiol 11 Suppl:S87–S93 (2001). [DOI 10.2188/jea.11.6sup_87](https://doi.org/10.2188/jea.11.6sup_87); PMID 11763144; PMCID PMC11858362 | JPHC / Japan Public Health Center-based Study, Cohorts I and II; includes Suita 1 and Suita 2. All tables share this source family. Original PDF issue year is 2001; PMC displays a later online date. | Methods, Table 1 attendance/coverage, Tables 4–5 BMI/SBP; other table headings screened. |
| EXT_IKEDA2008 | Ikeda et al. *Understanding the decline of mean systolic blood pressure in Japan: an analysis of pooled data from the National Nutrition Survey, 1986–2002*. Bull WHO 86:978–988. [DOI 10.2471/BLT.07.050195](https://doi.org/10.2471/BLT.07.050195); PMID 19142299; PMCID PMC2649578 | Japanese National Nutrition Survey / NNS 1986–2002. This is the Japanese survey, not US NHANES. Repeated annual samples are one pooled source analysis. | Original full-text methods, variable definitions, Tables 3–6, especially Table 5 model. |
| EXT_LI2018 | Li et al. *Association of Age-Related Trends in Blood Pressure and Body Composition Indices in Healthy Adults*. Front Physiol 9:1574. [DOI 10.3389/fphys.2018.01574](https://doi.org/10.3389/fphys.2018.01574); PMCID PMC6275465 | Chinese health/basic physiological-parameters survey; Xi'an, Hanzhong, Qishan, Hu County, June–July 2014. Publisher calls the province “Shanxi”; retain site names to avoid silently resolving that geographic spelling inconsistency. | Full publisher methods, Tables 1–2, Figure 2/3 captions; supplemental-table locator only. |

No documented participant overlap among these four source families was established. Independence is not proved merely by different titles. None shares the named target hospital in the source population descriptions inspected.

## Extracted constraints and their limits

### EXT_OYA2014: best glucose source in this bounded set

[Publisher PDF](https://www.jstage.jst.go.jp/article/internalmedicine/53/9/53_53.1580/_pdf), p.942 Methods and p.943 Table 1. Adults aged 30–79 without diabetes; exclusions include cancer, anemia, cardiovascular disease, and medication for hypertension/dyslipidemia. Kurihashi examinations: February 2006–January 2007; Yamanouchi: April 2009–March 2010. FPG measured after a 10-hour fast by hexokinase UV; diabetes definition includes FPG ≥126 mg/dL or known diabetes. Values below are reported mean ± individual SD, not SE.

| Sex / center | n | Age, years | BMI, kg/m² | FPG, mg/dL |
|---|---:|---:|---:|---:|
| Men / Kurihashi | 1,350 | 51 ± 9 | 23.8 ± 3.1 | 95 ± 12 |
| Men / Yamanouchi | 974 | 54 ± 10 | 23.3 ± 3.0 | 98 ± 12 |
| Women / Kurihashi | 697 | 51 ± 8 | 22.4 ± 3.1 | 90 ± 10 |
| Women / Yamanouchi | 775 | 54 ± 9 | 22.2 ± 3.4 | 94 ± 12 |

Table 2, p.943: male FPG versus age B=0.224, SE=0.026, standardized coefficient=0.175, adjusted for study center; no BMI adjustment. Female analyses split menopausal status. Residual SD/intercept and BMI–FPG covariance are not supplied. Table 2's printed male BMI row is B=−0.291, SE=0.007, standardized coefficient=−0.091; the scaling inconsistency is present in the original image, not an OCR error. Author clarification is needed before use. Female coefficients also require orientation/scaling clarification before executable use. Do not repair, invert, or pool coefficients silently.

Source-age interpretation audit (scout derivation, not a new reported fact): the male FPG forward-slope interpretation yields approximately 0.224×10/13=0.172, close to reported standardized 0.175. The male BMI row instead gives −0.291×10/3.1≈−0.939, far from −0.091. Exact equivalence is not expected after center adjustment, but this order-of-magnitude mismatch makes silent repair indefensible. Female FPG printed values are 0.103 (SE 0.026; standardized 0.173) before menopause and 0.095 (0.018; 0.198) after menopause. Subgroup moments are absent from Table 1, and the report does not resolve their orientation/scaling by taking reciprocals. The paper's heading/results describe an effect of age, but provide no fully explicit fitted equation.

### EXT_BABA2001: directly usable age–sex marginal constraints

[Original PMC text](https://pmc.ncbi.nlm.nih.gov/articles/PMC11858362/), Tables 4 and 5; [publisher PDF](https://www.jstage.jst.go.jp/article/jea1991/11/6sup/11_6sup_87/_pdf), pp.S89–S90. Municipal health-exam attendees, mostly examinations in 1990/1993; Suita 2 in 1993–1994. These are selected attendees, not a diabetes-free, untreated population. Overall collected sizes: 23,313 and 24,654 in Cohorts I/II. Example coherent subset, Suita 2:

| Sex / age stratum | BMI mean ± SD, kg/m² | SBP mean ± SD, mmHg |
|---|---:|---:|
| Men, 40–49 | 23.3 ± 2.76 | 119.1 ± 15.7 |
| Men, 50–59 | 23.5 ± 2.63 | 127.6 ± 20.9 |
| Women, 40–49 | 22.1 ± 2.81 | 117.2 ± 17.1 |
| Women, 50–59 | 22.4 ± 2.97 | 124.9 ± 19.7 |

These constrain each marginal conditional on sex and age bin; they do not supply BMI–SBP covariance, within-bin continuous-age dependence, or exact stratum weights. Suita 1 and Katsushika ages are only 40 or 50; do not interpret their apparent decade rows as full age bands. Table 1 indicates Suita 2 BMI-component/SBP measurement coverage of 100%, but not whole-cohort target comparability. Lipid-table presence alone supplies no glucose/HbA1c joint model.

### EXT_IKEDA2008: useful adjusted effects, unsuitable direct four-variable equation

[Original Table 5 and Methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC2649578/). Ages ≥20; 90,554 men and 101,903 women. First seated SBP reading after five minutes' rest; mercury instrument. Second-stage sex-specific linear model includes BMI, age categories, age×BMI, exercise, smoking, drinking, prefecture-level salt intake, predicted treatment probability from the first stage, and survey-year indicators.

Reported reference-age BMI coefficients: men 1.36 (SE 0.07), women 1.29 (SE 0.05) mmHg/(kg/m²), reference age 20–29. Age 40–44 interaction increments: −0.02 (0.13) and +0.33 (0.08), respectively. Thus 40–44 conditional slopes are *derived* 1.34 and 1.62; their SE cannot be obtained by adding SEs without coefficient covariance. Intercepts 86.08/83.29 belong to the complete model; adjusted R²=0.26/0.37. Residual SD is not reported. Table 3 age-standardized mean CIs are not individual SDs. Missing lifestyle/treatment/context distributions preclude applying this as E(SBP|age,sex,BMI). No such target equation is proposed.

### EXT_LI2018: partial correlation is not the required marginal correlation

[Original publisher Tables 1–2 and Methods](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2018.01574/full). Selected healthy adults aged 18–79; pre-existing hypertension/systemic disease and pregnancy exclusions. SBP averaged from three electronic measurements after ≥10 minutes' rest.

| Sex | n | Age mean ± SD, years | BMI mean ± SD, kg/m² | SBP mean ± SD, mmHg |
|---|---:|---:|---:|---:|
| Men | 1,669 | 44.07 ± 13.85 | 23.57 ± 3.36 | 120.72 ± 12.95 |
| Women | 2,419 | 42.66 ± 13.04 | 22.81 ± 3.40 | 112.79 ± 14.62 |

Table 2 calls its results partial Pearson correlations; BMI–SBP r=0.296 men, 0.237 women. Its note lists age, education, smoking, alcohol, and residential location (worded “P was adjusted”). These must not be relabeled unadjusted Pearson correlations or assumed to equal within-age-bin correlations. Figure 2 adjusted slopes also involve absent covariates; captions leave orientation less explicit than needed for a generator. Supplementary Table S1 is not extracted, so no age-bin numerical constraint is claimed from it. No residual SD or full covariance matrix was found in the inspected tables.

## Selection and transport boundary

EXT_OYA2014's glucose evidence is conditional on no known diabetes and measured FPG below 126 mg/dL, plus the additional health/medication exclusions. It cannot identify a diabetic tail, nor should its mean/SD be combined with an unrestricted normal FPG distribution and called the original source population. Tail handling and any moment-preserving truncated family remain assumptions. All source-replay comparisons must retain the selection. This selection can change age/BMI/FPG associations; transporting them to a differently selected health-exam cohort is an untested assumption.

EXT_BABA2001 and EXT_IKEDA2008 include broader attendee/community populations; the inspected methods do not impose the same non-diabetic/untreated selection. NNS explicitly includes treated people. EXT_LI2018 excludes pre-existing hypertension and systemic disease and defines hypertension at SBP≥140 or DBP≥90; the relationship between known-history exclusions and measured eligibility requires clarification before hard-truncating SBP at 140. Its selected healthy distribution is not interchangeable with the broader Japanese SBP sources. Device, rest time, first-reading versus three-reading average, period, and selection also differ. No equality of source and target eligibility or measurement was assumed or checked here.

## One concrete feasibility opinion

**Feasible only as a limited, assumption-indexed four-variable glucose pilot:** generate complete rows of age, sex, BMI, and FPG for a declared adult health-exam design, using EXT_OYA2014 sex×center summaries. Its center is an internal source-context variable, not an extra target measurement. A five-variable age/sex/BMI/FPG/HbA1c pilot is not supported by these four papers: no HbA1c constraint was identified.

For source reconstruction, the published counts determine sex/center mixing; means/SDs constrain the three continuous margins. The male FPG–age coefficient could constrain one age relationship with center retained in the source replay. Its ordinary units are consistent with the male marginal scales. Intercepts centered on each source-center mean, homoscedastic errors, continuous-age distribution/truncation, and the transfer of this age effect between centers would still be model assumptions. A finite-sample fitted coefficient should be checked under the original center adjustment. A residual variance computed as marginal variance minus explained age variance would be a model-dependent derivation, not a reported residual SD; truncation and rounding require numerical checking. Female age effects should remain unassessed until the coefficient ambiguity is resolved.

BMI–FPG residual dependence is unreported. A zero residual correlation and nonzero alternatives can reproduce the same admitted margins and male age coefficient. Therefore residual correlations, nonlinear tails, and sex-specific BMI associations must be labeled sensitivity assumptions. No reciprocal-regression conversion is permitted: B(Y|X) is not 1/B(X|Y). A partial correlation adjusted for absent Z is not corr(X,Y), and E(Y|X,Z) cannot be reduced to E(Y|X) by deleting Z terms without additional assumptions about Z|X.

This limitation does **not** make every analytical-utility experiment impossible. A custodian could predeclare hidden evaluation of sex-specific marginal moments, FPG–age association, and age-bin/sex mean contrasts, then compare an evidence-informed generator with a marginal-only baseline. Such testing must be performed without giving builders target IPD or target results. Target performance remains unknown here. Source table reproduction is only a construction check; it cannot validate transport to a Japanese target cohort.

The case does **not** currently support claims about BMI-adjusted FPG effects, HbA1c, diabetes risk prediction, incident disease, causal effects, or recovery of the full target joint distribution. If admission requires a source-supported BMI-conditional biomarker relationship across both sexes, this fixed four-paper set is insufficient. If admission permits an explicitly limited test of marginal and selected age-association utility, the four-variable glucose pilot is concrete enough to specify, while maintaining the unresolved dependence as an assumption rather than inventing evidence. EXT_BABA2001 supplies an alternative age/sex/BMI/SBP marginal design, but the other two SBP papers do not resolve its context-compatible BMI dependence.

No generator, simulated rows, source-replay results, or target-performance result was produced by this scout. Stopping reason: fixed four-paper budget reached; further paper expansion is intentionally deferred to the controller.

## Append-only resource-accounting correction

Added 2026-10-31 after the controller closed this bounded cycle as admission-only. No further research or network request was made for this correction. The earlier statement that no article file was saved describes filesystem persistence only; it does **not** imply zero download bytes.

Existing direct-HTTP call records establish four successful in-memory response-body reads:

| Read | Existing request | Body bytes retained in accounting records | Existing per-read application limit |
|---|---|---|---:|
| 1 | Europe PMC `PMC6275465/fullTextXML` | Unknown; XML body length and Content-Length were not printed or retained | 10,485,760 bytes |
| 2 | Frontiers DOI `10.3389/fphys.2018.01574`, full HTML | Unknown; HTML body length and Content-Length were not printed or retained | 10,485,760 bytes |
| 3 | J-STAGE Oya PDF, rendered page 943 | Unknown; PDF body length and Content-Length were not printed or retained | 10,485,760 bytes |
| 4 | Same J-STAGE Oya PDF fetched again, rendered page 942 | Unknown; this was a second transfer, not a cached reuse | 10,485,760 bytes |

Each script checked any reported Content-Length against 10 MiB and called `read(10485760)`. The actual header values and byte lengths were not exported from the short-lived Python processes. Their existing outputs contain selected text or a newly rendered PNG, neither of which determines the original response size. Thus the **exact direct-download total is unknown**, not zero. The sum of application-level bytes read was bounded above by 41,943,040 bytes (40 MiB); this is a conservative cap across four reads, not a measured total or a bound on HTTP/TLS overhead or redirect traffic.

The `web.run` searches, original-page opens, PDF parsing, and screenshot attempts also involved unmetered service-side retrievals. Their response/source byte sizes are unavailable in the returned records and are excluded from the direct-read cap; failed screenshot attempts cannot be assumed to transfer zero bytes. Repeated retrievals must not be collapsed into a single download for accounting. No total network-byte claim can be made from these records.

Known exact persistence count: **0 source article/XML/HTML/PDF/IPD files saved to disk** by this scout. This report is a generated local artifact, not a downloaded source file. No exact positive network-byte count was retained. No new requests were issued to reconstruct missing sizes, and STATE was not edited.
