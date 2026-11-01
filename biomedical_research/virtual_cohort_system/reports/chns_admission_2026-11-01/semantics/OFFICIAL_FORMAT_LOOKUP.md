# Bounded official CHNS format lookup

Date: 2026-11-01. Unit: field-coding metadata lookup following the `chns@2026-11-01T23:15:59.031Z` heartbeat. This is a documentation finding, not a clinical analysis or an admission approval.

## Result

No release-compatible SAS format catalog, format-definition program, or additional field-specific missing-code dictionary was found in the three official pages checked. This is a bounded negative finding about these routes, not proof that no such documentation exists elsewhere. The required numeric sentinel rules remain unresolved by this lookup. Do not apply a blanket 88/99, repeated-eight/repeated-nine, or negative-value mask.

The existing measurement draft and current STATE were read before browsing. Their local-header findings were used as prior evidence rather than independently repeated: the downloaded files expose no stored format mapping, value-label dictionary, user-missing definition, or missing-range metadata for the selected fields. No local codebook pages or SAS observations were opened in this unit; the separate schema inspection remains responsible for those findings.

## Exact official routes checked

All browsing used the authorized Chrome profile. Three distinct official pages were opened; the individual-level directory was viewed in two pagination windows within the same page. No search engine, new original study, extra questionnaire, or legacy login route was opened.

1. [CHNS documentation index](https://chns.cpc.unc.edu/data/documentation/). The visible index links cover identifiers, special LINE numbers, unit of analysis, variable names, missing values, dates, cleaning, notes, and SAS XPORT usage. No current release format-catalog or format-definition download was listed. The SAS XPORT link points to the legacy `www.cpc.unc.edu/projects/china/acl_users/credentials_cookie_auth/require_login` route, with the former `/projects/china/data/documentation/sasxpt` page as its destination. It was not followed; its contents and relevance remain unknown.
2. [Individual-Level Data, DOI 10.15139/S3/9PQ5KV](https://dataverse.unc.edu/dataset.xhtml?persistentId=doi:10.15139/S3/9PQ5KV), displayed Version 1.0. The file-type menu showed 27 Data and 27 Document entries. Viewing filenames 1–50 and 51–54 established that all 54 listed files are 27 PDF/SAS7BDAT pairs. These include `mast_pub_12.pdf`/`.sas7bdat`, `surveys_pub_12.pdf`/`.sas7bdat`, and `pexam_00.pdf`/`.sas7bdat`. No separately listed `.sas7bcat`, `.sas`, archive, or format dictionary appeared. Filenames and release metadata were inspected; none of the files was opened or downloaded. The existing PDF codebooks may contain definitions, but their applicability is a separate local schema check.
3. [Biomarker Data, DOI 10.15139/S3/GQ9GPP](https://dataverse.unc.edu/dataset.xhtml?persistentId=doi:10.15139/S3/GQ9GPP), displayed Version 1.0. Its complete Files list contained one file, `biomarker_09.sas7bdat`, file ID 7505013. No companion format catalog, codebook, or SAS program was listed. The file itself was not opened or downloaded.

Already-reviewed generic documentation at `/data/documentation/missing/`, `/cleaning/`, `/notes/`, `/idvar/`, and `/datevar/` was not reopened. Its general guidance does not establish a current per-variable sentinel map.

## Consequence for the measurement contract

| Required field | Existing supported metadata | What this lookup adds or leaves unresolved |
|---|---|---|
| `age` | Current survey field, years; historical codebook formatting has zero decimals. | No new definition of reference date, rounding, or field-specific numeric missing codes. |
| `GENDER` | Existing master codebook gives 1 = male and 2 = female. | No additional current release missing/other-code rule. Values outside the defined pair must not be silently recoded as female. |
| `HEIGHT`, `WEIGHT` | Existing definitions specify cm and kg. | No numeric sentinel dictionary found. Preserve the cleaning flags and the distinction between accepted corrections and missing measurements. |
| `CLN_HT`, `CLN_WT` | Parent separately reports recovering category-code labels from definition-only crops of the existing pexam codebook, including accepted corrections and a category for improbable values set missing. | This browser lookup neither repeats nor independently verifies those crops. Their recovery resolves a subset of flag labels, not all numeric measurement sentinels, current code frequencies, or automatic row-exclusion policy. In particular, a positive cleaning flag is not generically an invalidity flag. |
| `GLUCOSE` | Current header and methods support mmol/L; the documented central serum assay is distinct from field glucose. | No extra release-bound missing-code definition, per-person fasting assurance, or row-specific assay provenance was found. |
| `HbA1c` | Current field and methods support percent. | No additional missing-code map. The obsolete `Y50` dictionary mismatch cannot establish a current name/unit conversion or sentinel rule. |

Where an unresolved coding rule is necessary to define eligibility or an estimand, keep that rule explicitly unresolved before freezing the corresponding task. A scientifically justified, documented simplification can be reviewed separately; empirical frequencies or plausible ranges are not substitutes for metadata in this unit.

## Boundary and accounting

No files were downloaded or saved from the web: additional metered asset bytes = 0. Ordinary browser transport was not measured. Existing PDFs/SAS files were not downloaded again. No participant rows, clinical distributions, target effects, new primary papers, or questionnaire results were read. No masking, recoding, cohort selection, generator, or clinical analysis was run. STATE, the measurement draft, and the export checkout were unchanged. F2 remains unfrozen; this note supplies no biomedical-validation claim.
