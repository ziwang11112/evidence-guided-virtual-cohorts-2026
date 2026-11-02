# HAALSI baseline: definition-only schema audit

Date: 2026-11-02. Scope: the official codebook and survey/variable documentation, with empirical summary columns masked. This is an original metadata audit, not a reproduced codebook or an analysis of participant measurements.

The definitions support acquiring the main baseline phenotype file for a bounded schema, ID and missingness audit of age, sex, BMI and point-of-care glucose. They do not establish K01 admission, analysis eligibility, a fasting-only cohort, laboratory equivalence, or a usable HbA1c field. The parent subsequently acquired one main baseline file; that file was not opened for this document audit.

## Source identities and safe inspection

| Official document | Local bytes | MD5 | SHA-256 |
|---|---:|---|---|
| `private_documents/HAALSI Baseline Codebook.pdf` (2016 documentation) | 1,740,530 | `57893c50d15dd0653e38ee126acdfa57` | `49d79434d4836485f2e3291ff884535b42b356821a183985d20f6d7bcbfcaa07` |
| `private_documents/HAALSI Baseline Survey and Variables.docx` (14 April 2017 update) | 194,943 | `898d6239a9e6a01dbd1c9c45f9d628cc` | `451d7dad209bae21b324604c95696f60143f825acedd28b12360ddb3de416c67` |

The parent recorded official acquisition and matched original-file MD5 commitments in `HAALSI_ACCESS.json` and `ACQUISITION_LEDGER.json`. Local document hashes were checked during this audit. No network request, empirical paper, participant file, or new original study was used.

`haal_si_schema_only.py` verifies the PDF hash and the consistent header geometry on all 104 landscape pages. Only variable name, type, label and source/derivation columns are emitted. The Obs, Mean, Min and Max region is excluded. The private masked images for pages 87, 88, 90, 93, 94 and 95 retain only definition columns; forbidden-region word bounding boxes are blanked to prevent spillover. Masked pages 88, 90, 93 and 94 were visually checked by the author; the independent reviewer checked all six masked images. No numerical summary or frequency column was read into the audit.

DOCX inspection used selected OOXML table rows with run-color metadata preserved. The coordinator's official file-description record in `HAALSI_ACCESS.json` identifies orange fields as confidential, grey as unavailable during coding/cleaning, and green as having alternative variables; the DOCX preserves these colors. The independent reviewer verified the document colors, not the online legend during this no-network review. Table and row locators below are **zero-based across all DOCX tables**. The reviewer also checked style inheritance and the default Normal style: the core cleaned fields have no colored override. An uncolored documentation row is not proof that the field is present or populated in the actual release.

## Core candidate schema

| Field | Definition and unit | Definition locator | Status or limit |
|---|---|---|---|
| `prim_key` | Character primary key | PDF p. 1 | Token not located in DOCX; actual presence, type, uniqueness and missingness require the file audit. |
| `rage` | Respondent age on 31 July 2014 at sample selection, preloaded from census | PDF p. 13; DOCX table 42, row 18 | Uncolored. Not age calculated on the interview date. |
| `rsex` | Respondent sex, preloaded from census | PDF p. 95; DOCX table 42, row 20 | Uncolored. A numerical code-to-label legend was not supplied in the reviewed definition rows; do not infer one. |
| `c_bs_bmi` | BMI calculated from cleaned height and weight | PDF p. 89; DOCX table 41, row 32 | Uncolored. Derivation identifies the conventional height/weight construction; unit/labels should be verified against the actual file metadata. |
| `c_bs_height` | Cleaned height, cm, from original measurements, comments, lab and revisit data | PDF p. 87 | Raw height rows are green replacement rows in DOCX; prefer the documented cleaned variable. |
| `c_bs_weight` | Cleaned weight, kg, from original measurements, comments, lab and revisit data | PDF p. 87 | Raw weight rows are green replacement rows in DOCX; prefer the documented cleaned variable. |
| `c_bs_glucose` | Cleaned point-of-care glucose, mmol/L, from `bs028`, `bs028_check`, `bs029` and comments | PDF p. 88; DOCX table 41, row 40 | Uncolored. Original `BS028`, `BS028_check` and `BS029` rows are green (`00B050`) and direct use of the cleaned replacement. |
| `c_bs_hrslastate` | Hours since last ate at the start of dried-blood-spot collection; reported eating time is compared with collection timestamp, with a previous-day assumption when eating time appears later | PDF p. 93 | Derived timing measure, not a directly verified fasting protocol. |
| `c_bs_fasting8hr` | At least eight hours since eating at collection start | PDF p. 93 | Derived from `c_bs_hrslastate`; no blanket fasting claim is justified. |
| `village_anon` | Anonymized village identifier | PDF p. 102 | Does not by itself establish sampling stratum, PSU, or a survey weight. |

No HbA1c or glycated-hemoglobin field was located in the reviewed PDF definition columns or DOCX token search. `c_bs_hemoglobin` is point-of-care hemoglobin in g/dL and must not be substituted for HbA1c. Absence of a token in these documents does not prove that no such assay exists in another release.

## Measurement and missingness limits

The collection definitions include blood-specimen fields for Hemocue, CareSens and CardioCheck (PDF p. 85), dried-blood-spot consent, and a fingerstick insufficient-blood reason (p. 86). These establish point-of-care/fingerstick collection context. They do not establish exact device model, plasma equivalence, or interchangeability with a venous laboratory assay. `bs023` is a CareSens blood-specimen field; it is not sufficient alone to identify every analytical detail of `c_bs_glucose`.

The following numbers are **documented flag definitions, not observed minima, maxima, frequencies or eligibility criteria**:

- `fl_c_bs_glucose`: cleaned glucose outside the test range, below 1.1 or above 33.3 mmol/L (PDF p. 90).
- `fl_c_bs_height`: cleaned height outside 125–220 cm; `fl_c_bs_weight`: cleaned weight outside 30–160 kg (p. 89).
- `fl_c_bs_bmi`: either height/weight flagged, or BMI below 11 or above 60 (p. 90).

The documents inspected do not settle how below/above-range glucose is stored, whether its number is a boundary value or a special code, or which Stata tagged missing codes occur. Do not infer these from hidden summary columns, clip or repair measurements, or turn range flags into automatic exclusion rules. A file audit may inspect code labels, permitted flag tokens and missingness without exposing continuous measurements.

## Diabetes and design fields: unresolved definitions

Raw treatment definitions include `cm009` (ever received treatment), `cm010` (currently receiving treatment), and `cm011` treatment choices including diet, weight loss, medication and insulin (PDF pp. 63–64). The raw `cm007` sex-specific questions ask about prior diagnosis. These are reported diagnosis/treatment constructs rather than an independent glycemic assay.

The legacy cleaned diabetes definitions on PDF p. 94 contain conflicting cross-references: the narrow current-treatment definition `c_cm_diabetes_srtrt` cites the `cm007` sex-specific fields, while the broad diagnosis definition `c_cm_diabetes_srdiag` cites `cm010`. The DOCX question wording confirms that those references do not match the stated constructs. Also, the fasting field says “at least 8 hours,” whereas the legacy composite wording says greater than eight hours and treats missing fasting as nonfasting. Preserve these as unresolved; do not silently swap fields, choose a boundary, or use either composite as an approved outcome/eligibility definition. These ambiguities do not prevent checking continuous glucose schema availability.

No survey-weight, stratum or PSU field was positively identified during this bounded definition review. No claim of unweighted representativeness or independent sampling follows. Sample selection, design weights, exact assay comparability, categorical coding and missing/censoring conventions remain open metadata questions.

## Bounded next step and disposition

The authorized next step is one audit of the acquired main baseline file: selected variable names and labels/value-label coding; row/column counts; ID missing/unique/duplicate counts; selected-variable missing counts (tagged missing separately if available); joint age/sex/BMI/glucose availability; and unique sex/fasting/test-range flag tokens without frequencies. No continuous value, mean, extrema, dispersion, association, clinical filtering, or final analysis sample size is authorized by this schema checkpoint. Inspecting the variable dictionary does not admit the case or select an estimand.

This document unit adds no study slot, patient analysis, generation or source fitting. Current campaign accounting is maintained by the parent; at this checkpoint it reports four screened families and three original studies. No STATE or exported artifact was edited. Original private metadata files and masked intermediates remain under `private_documents`.
