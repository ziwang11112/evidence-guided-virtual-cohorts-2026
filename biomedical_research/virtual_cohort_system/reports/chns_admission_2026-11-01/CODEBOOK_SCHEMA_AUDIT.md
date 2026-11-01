# CHNS companion codebook schema audit

1 November 2026. **Decision: the three companion data files are justified for a reference requiring contemporaneous age, gender and BMI/anthropometry.** `pexam_00` supplies height/weight, `mast_pub_12` supplies gender, and `surveys_pub_12` supplies age by wave. These are dictionary findings, not validation of the actual SAS files or of a completed join. The controller handles acquisition and independently audits the biomarker file. No data file was downloaded, decoded or joined by this subtask. No new original study was opened; F2 remains unfrozen and the three-family/six-original-study limits are unchanged.

All page references below are physical PDF pages, numbered from one. Source PDFs remain local. The PDF skill was used; schema crops from examination pp. 1, 3, 4, master p. 1 and surveys p. 1 were visually checked. A material extraction failure and its incidental aggregate exposure are recorded below.

## Files and wave coverage

| Local codebook | Verified document schema | Companion-file decision |
|---|---|---|
| [pexam_00.pdf](https://dataverse.unc.edu/file.xhtml?fileId=7504991&version=1.0), 33 pages | p. 1: Physical Examination **1989-2011**, created 27 February 2014; **206 variables**; one individual/year observation, identified as `IDIND/WAVE`. The `WAVE` category-label column on p. 1 explicitly lists **2009**, among 1989, 1991, 1993, 1997, 2000, 2004, 2006 and 2011. | Acquire `pexam_00.sas7bdat`, file **7504992**, subject to exact bytes and the 200 MiB cap. It is not a 2000-only file despite its suffix. Codebook support for 2009 is established; actual 2009 rows, per-field availability and eligible counts in the acquired release remain unverified. |
| [mast_pub_12.pdf](https://dataverse.unc.edu/file.xhtml?fileId=7504949&version=1.0), 3 pages | p. 1: Master Individual ID File through **2015**, created 1 May 2018; **9 variables**; one observation per respondent (`IDind`). No `WAVE` field in the schema. | Acquire `mast_pub_12.sas7bdat`, file **7504950**, to obtain `GENDER` linked by person ID. It is a later master release; dictionary wording does not establish whether gender/demographic corrections are contemporaneous with 2009. |
| [surveys_pub_12.pdf](https://dataverse.unc.edu/file.xhtml?fileId=7504999&version=1.0), 4 pages | pp. 1-3: **20 variables**, one respondent/year observation (`IDind/wave`), created 1 May 2018. The title says **1989-2015**, but the DATA SET label says **1989-2011** and p. 1's listed `WAVE` category labels end at 2011 and include **2009**. | Acquire `surveys_pub_12.sas7bdat`, file **7505000**, for wave-specific `AGE` and linkage/participation metadata. Preserve the title/label discrepancy; do not infer complete 2015 coverage or exact 2009 eligibility from it. |

All three are in Individual-Level Data DOI `10.15139/S3/9PQ5KV`, version 1.0, as recorded in [FILE_ACCESS_AUDIT.md](FILE_ACCESS_AUDIT.md). These are necessary companions for the stated age/gender/BMI field requirement, not an instruction to acquire every CHNS file. The separate biomarker release remains essential for its own measurement fields. No physical-activity or constructed-income file is justified by this schema finding.

## Relevant field map

`Num` below is the codebook's SAS numeric storage type; it does not by itself imply a continuous analysis variable. Listed relevant fields have length 8 except master `GENDER`, length 6. Format names are retained as identifiers; they are not automatic decoding rules.

| File / pages | Exact fields | Definition, units and interpretation |
|---|---|---|
| Examination p. 1 | `IDIND`, `HHID`, `LINE`, `COMMID`, `WAVE` | Individual, household, line and community identifiers; survey year. All Num; `WAVE` format `YR`. Declared person-wave key is `IDIND/WAVE`; neither uniqueness nor household continuity was tested. |
| Examination p. 3 | `HEIGHT`, `WEIGHT` | Num; **cm** and **kg**, respectively. Candidate BMI is `WEIGHT / (HEIGHT / 100)^2`, yielding kg/m², only after documented missing/cleaning rules and same-occasion validity. No BMI calculation was performed. |
| Examination p. 4 | `T7_PE`, `U9`, `U10` | `T7_PE`: physical-measurement date, labelled **YYYYMMDD**, Num. `U9`: hip circumference, cm; `U10`: waist circumference, cm. A same-wave match does not prove the same examination/blood-collection day. |
| Examination pp. 1-2 | `CLN_BP`, `CLN_HIPS`, `CLN_HT`, `CLN_WAIST`, `CLN_WT` | Num, format `CLN`; cleaning indicators. Height/weight labels say cleaned if greater than zero. Code-label text includes accepted values, earlier cleaning, peer review, unit/typographical correction and values set to missing. Numeric code mappings and a prospective handling rule remain unresolved. Do not reapply a correction merely because its flag exists. |
| Examination pp. 2-3 | `DIASTOL1`, `DIASTOL2`, `DIASTOL3`, `SYSTOL1`, `SYSTOL2`, `SYSTOL3` | Num; separately labelled repeated blood-pressure measurements. Units and a repeat-combination rule are not established by these labels alone. Availability is not selection of a blood-pressure endpoint. |
| Examination pp. 6-8 | `U22`, `U24`, `U24A`, `U24B`, `U24C`-`U24F` | Diagnosed high blood pressure; antihypertensive drugs; diabetes diagnosis; age at diabetes diagnosis; diet, weight-control, oral-medication and insulin treatment indicators. Most categorical fields use `YESNONO`; `U24B` is age at diagnosis in years, **not current age**. Their 2009 availability, codes and eligibility role need verification. |
| Examination pp. 18, 20 | `U56`, `U87` | Currently pregnant and currently breastfeeding; Num, format `YESNOUNK`. Candidate eligibility fields only, not automatically mandated exclusions. |
| Master p. 1 | `IDIND`, `GENDER` | Num person ID and Num gender, format `SEX`. The isolated code/category cells explicitly map **1 = Male, 2 = Female**. No additional sex/gender construct or longitudinal stability is implied. |
| Master p. 1 | `WEST_DOB_Y`, `MOON_DOB_Y`, `NATIONALITY` | Western and lunar birth **year**, and nationality; Num, nationality format `RACE`. Birth year alone cannot reproduce an exact age at examination. Do not replace the survey's documented age with `2009 - birth year` without a separately justified convention. |
| Surveys p. 1 | `IDIND`, `HHID`, `LINE`, `WAVE`, `AGE`, `AGE_DAYS` | Num; `WAVE` format `YR`; age fields format `AGE`. `AGE` label: **Calculated Age in Years to 0 Decimal Points**. The label does not state rounding algorithm or reference date. `AGE_DAYS` has no explanatory variable label in this codebook; its name suggests days, but exact semantics remain unconfirmed. |
| Surveys p. 1 | `BIOMAKER`, `PHYSICAL`, `INDIVIDUAL`, `DIET`, `TOENAIL` | Num survey-component flags. Preserve the exact spelling **BIOMAKER**. The labels do not establish a complete biomarker panel, fasting compliance or usable values; missing versus nonparticipation semantics need documentation. |
| Surveys pp. 2-3 | `COMMID`, `T1`-`T5`, `STRATUM`, `URBAN`, `T7` | Geography/administrative categories and household interview date. `T7`'s encoding is not stated in its label. These fields do not establish sampling weights or a national-representativeness claim. |

The complete examination schema's 206 variable names were enumerated from the leftmost column. It contains no direct `AGE`, `GENDER`/`SEX`, birth-date or BMI field. Other age-labelled questions refer to events or conditions, not general participant age. Examination alone is therefore insufficient for the requested demographic/anthropometric reference.

## Missing codes, linkage and remaining gates

The isolated surveys `AGE` category row prints **`.` = Missing**. `AGE_DAYS` has a Missing category but the corresponding code cell was blank in extraction; no numeric sentinel is inferred. Formats `AGE`, `YR`, `SEX`, `CLN`, `YESNONO` and `YESNOUNK` require their authoritative definitions or stored format metadata. This audit does not establish all missing/special codes for height, weight, dates, diagnoses or identifiers. Observed ranges were not used to invent missing-value rules or clinical cutoffs.

Prospective linkage specification: map the actual biomarker key names/types explicitly to `IDIND` plus `WAVE`; join examination and surveys at that person-wave level; join master by `IDIND`. Case-normalizing field **names** is distinct from altering identifier **values**. Preserve original identifiers and numeric precision. Require documented wave selection, key uniqueness, expected many-to-one master linkage, no row multiplication, and transparent unmatched-record handling before an analysis-ready reference is declared. Those are future custodian checks, not checks completed here.

Still unresolved: actual SAS/codebook version agreement; biomarker-to-examination timing; age reference/rounding; field-specific 2009 availability; cleaning/missing-code decoding; fasting/assay indicators; joins and eligibility. The controller reports the acquired biomarker header differs from its older codebook; this audit supplies no authority to rename or equate those biomarker fields. Do not use target distributions to resolve a label or unit ambiguity. No eligibility count, source effect, scientific estimand or expected sign is selected here.

## Incidental exposure and extraction correction

This was **not a perfectly outcome-blind document read**. The first bounded layout probe exposed file-level observation counts and first-row aggregate cells for examination `IDIND`, master `DOD_Y` and surveys `BIOMAKER`. A subsequent crop incorrectly used the **Mean header** position: right-aligned numeric cells extended left of that position. Leading fragments of pooled codebook means were therefore displayed on examination pp. **11-32**, covering cancer indicators, smoking/alcohol, pregnancy, health/function/cognition and diet questions. Some final-page “no occurrences” warning-category labels were also visible. Values are not reproduced here and were not used for endpoint selection or construction. No participant rows, anthropometric/glycemic aggregate values, wave-specific target effects or joint-relationship analyses were shown.

The corrected method uses deduplicated PDF characters and actual table grid boundaries, ending before the Length column for visual review, and excludes summary/frequency columns. Subsequent isolated categorical-label checks showed wave names, cleaning descriptions, gender code labels and age missing-code definitions, without counts or percentages. The root controller was notified of both exposure incidents. These fields' marginal-summary scope must remain in the exposure ledger; a new Agent cannot erase it. The fragments do not establish all CHNS relationships, and their incomplete nature does not justify calling them unexposed.

## Local file identity

| Codebook | Bytes | SHA-256 |
|---|---:|---|
| `pexam_00.pdf` | 227,566 | `de9baba260025a4c0bc7cd90d4cb6aeec2272c946327dd52517532c577ed0074` |
| `mast_pub_12.pdf` | 137,393 | `768f4477008e905bc75593f89024b1fd9d28d4d3ac77b3dc63bb60db05a49c00` |
| `surveys_pub_12.pdf` | 143,120 | `4fb1528245ef26cca7e9c28531083c7926ca58f230eb4238d6b9d47a77a28144` |

Only this audit and local cropped rendering intermediates were written. No state, protocol freeze, raw data, automation or Git operation was changed.
