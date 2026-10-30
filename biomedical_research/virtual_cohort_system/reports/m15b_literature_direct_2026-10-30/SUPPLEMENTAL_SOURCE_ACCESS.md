# Supplemental source access and provenance review

Completed 2026-10-30. This controller review used exactly two permitted acquisition attempts, both successful. No additional query, retry, redirect, alternate source, upload or registration action occurred. No target/reference/generated rows or other experiment outputs were accessed. The root controller retains the admission decision and separate budget charge.

## Acquisition record

| Slot | Source and exact endpoint | UTC interval | HTTP | Bytes | SHA-256 |
|---|---|---|---|---:|---|
| 1 | [PMC6941025 full original XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6941025/fullTextXML) | 2026-10-30T17:34:39.255047+00:00 to 2026-10-30T17:34:40.736709+00:00 | 200 | 110248 | `e3a9523f20628c54800933f1dec18239c8793703fc10a2e48e6ed7e8f2b0b679` |
| 2 | [Yun2021 full supplemental DOCX](https://pmc-oa-opendata.s3.amazonaws.com/PMC8236402.1/41366_2021_810_MOESM1_ESM.docx?md5=802708ea0f6eb323d8b0dcbe5e44e780) | 2026-10-30T17:34:40.736709+00:00 to 2026-10-30T17:34:41.166636+00:00 | 200 | 316127 | `417a28f721b2f07f78a5beb2680bdc7c0cf765aebcf207871de52af99cd9c790` |

The DOCX URL came solely from `visible/bundle/gateway/session/state.json`, parent `PMC8236402`, its sole supplement. Original bytes and unredacted extractions are retained in `private/source_access/`. The XML article identifier matches PMC6941025; both hashes were rechecked; DOCX ZIP CRC validation passed. Gateway-state hash was unchanged at the check. This helper modified no gateway, registry or configuration artifact.

## Ferrara original: actual cohort and relevant evidence

Bonaccorsi et al. (2019), DOI `10.3390/ijms20246321`, analyzes two University of Ferrara research studies. Section 4.1 identifies women undergoing densitometry at the university's Centre of Menopause and Osteoporosis plus female university employees in Ferrara, Italy. This is an original **non-NHANES cohort**. The sample contains 358 apparently healthy Caucasian women aged 25–65: 124 premenopausal and 234 postmenopausal. Recruitment was reported as random within this restricted clinic/employment frame. Premenopause meant regular cycles; postmenopause meant amenorrhea longer than 12 months. Exclusions included pregnancy/breastfeeding, excess alcohol, major chronic disease, medications affecting urate, premenopausal osteoporosis and diabetes. It is not a representative general adult cohort.

Serum urate was measured after fasting using an enzymatic uricase/peroxidase assay; intra-/inter-assay CVs were 2.5%/5.3% (Section 4.4). Urate units are µmol/L; BMI units are kg/m²; age is in years.

| Original locator | Premenopausal | Postmenopausal | Interpretation |
|---|---:|---:|---|
| Table 1, age mean ± SD | 35 ± 10 | 55 ± 4 | Unadjusted descriptive summaries |
| Table 1, BMI mean ± SD | 23 ± 4 | 25 ± 3 | Unadjusted descriptive summaries |
| Table 1, urate mean ± SD (µmol/L) | 225 ± 76 | 239 ± 76 | No significant group difference stated in Section 2.1; exact p and CI absent |
| Table 2, BMI–urate Pearson r | −0.013 | 0.345, p < 0.001 | Unadjusted within-menopause correlations; no CI/SE |

No adjusted urate-on-age slope, age trend or menopause effect adjusted for age/BMI is reported in the acquired article. The descriptive age separation cannot identify an age effect. SDs describe person-to-person variation and are not SEs. The Pearson coefficients are neither adjusted slopes nor causal effects.

Table 3 and Section 2.3 report **total-hip BMD as the outcome**, with SUA as predictor. Its base standardized coefficient is 0.220 (narrative p = 0.001), adjusted for age, smoking, hormonal treatment and years since menopause. Adding BMI reduces that SUA coefficient to 0.119, no longer significant. These are not urate-on-BMI or urate-on-age coefficients. No corresponding covariate coefficients or CIs/SEs are supplied. The table's final-column heading describes the reverse variance direction, but its explicit footnote specifies BMD as the outcome; this source inconsistency is retained. The table footnote also mentions more models than the six displayed in the XML.

NHANES appears incidentally in **Discussion, `sec3-ijms-20-06321`, paragraph 3**, which cites references `B16`, `B25` and `B27` (full IDs in the JSON). Mention detection retained that paragraph only in private raw/unredacted extraction; its findings and target numbers are absent from this report. Admission of the full original will expose this discussion and must record that scoped exposure. No Bonaccorsi supplementary URL was fetched.

## Yun2021 supplement: cohort dependence and relevant evidence

The exact DOCX is the supplement to DOI `10.1038/s41366-021-00810-9`. The existing admitted parent XML (Sec3–Sec5) supplies its provenance and adjustment context. The **Bogalusa Heart Study** recruited nondiabetic Black and White participants in Bogalusa, Louisiana. Its cross-sectional samples contain 3,102 children aged 5–19 and 3,402 adults aged 20–56; linked longitudinal samples contain 564 child-to-adult participants and 911 adults. These are not NHANES data. The supplement and parent share a cohort and must not be counted as independent evidence; their longitudinal and cross-sectional subsets also overlap in their sampling source. Ferrara and Bogalusa have distinct stated recruitment frames.

DOCX ZIP/XML extraction recovered three complete tables and retained three embedded figures. S1 and S2 give standardized cross-lagged UA↔BMI paths; S3 gives subgroup mediation regression coefficients. Embedded figures are retained in the DOCX and as private PNGs; XML text extraction does not OCR their labels. The parent identifies Figure S1 as the cohort flow and Figures S2/S3 as DBP/hypertension mediation analyses.

| Supplement Table S3, adult group | n | Adjusted standardized BMI→UA β1 |
|---|---:|---:|
| White | 2,221 | 0.337 |
| Black | 1,181 | 0.302 |
| Male | 1,521 | 0.332 |
| Female | 1,881 | 0.407 |

All four coefficients carry S3's p < 0.05 marker. Race- and sex-difference p values are 0.204 and 0.675, respectively; no coefficient CI/SE is reported. Parent Sec5 specifies age/race/sex adjustment, plus smoking and alcohol for adults. A subgroup fixes its stratifying characteristic; the exact subgroup design matrix is not shown. Original measurement units are mg/dL for urate and kg/m² for BMI, but these coefficients are **dimensionless standardized effects**, not raw-unit slopes.

S2's adult baseline-BMI→follow-up-UA paths are 0.064 for men (n = 365) and 0.069 for women (n = 546), neither marked significant; between-sex p = 0.941. Parent Sec5 describes residual adjustment for age, smoking and alcohol followed by standardization within race-sex groups, then a joint cross-lagged model additionally adjusted for follow-up duration. These paths are not contemporaneous BMI coefficients. The three supplemental tables provide no adjusted urate-on-age coefficient or menopause result.

Two source inconsistencies remain visible: some S1 significance markers/subgroup p values differ from the parent Results summary, and the parent statistical-method prose appears to reverse the fit-index threshold labels. Neither was silently corrected or used to set a generation parameter.

## Implication and retained files

The sources resolve cohort provenance and expand context for BMI/urate and menopausal strata. They **do not close the adjusted age-slope gap**. This report supplies extraction and limitations only; it selects no generation parameter and establishes neither target transportability nor independent validation.

Machine-readable attempts, hashes, source locators, statistics, exposure and checks are in `private/source_access/access_report.json`. Full originals are `PMC6941025.fullTextXML.xml` and `41366_2021_810_MOESM1_ESM.docx`; unredacted text/structured extractions, the DOCX document XML and embedded PNGs sit beside them. No artifact has been uploaded or admitted by this helper.
