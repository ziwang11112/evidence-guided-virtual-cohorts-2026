# Turkana independent schema-only review

1 November 2026. **Pass for the requested file-identity, key and availability audit.** This is not case admission or scientific eligibility validation. No generator, experiment, existing test suite, outcome search or statistical model was run.

## Independent method and boundary

The reviewer read `turkana_schema_audit.py` and `TURKANA_SCHEMA_AUDIT.json`, then independently processed the explicitly named local deposit using PowerShell `Import-Csv` with a tab delimiter and UTF-8 decoding, an ordinal string-key dictionary, and per-field blank/`NA` checks. The root implementation uses Python `csv.reader` and `Counter`; it was not imported, called or reused for the recomputation. SHA-256 was independently obtained with `Get-FileHash`.

Only file bytes/hash, header, row count, unique/duplicate identifier counts, missingness and the permitted Age/Sex/BMI/Total cholesterol/HDL cholesterol nonmissing intersection were emitted. Field contents were treated as strings, without conversion of clinical values to numbers. No patient identifier, clinical value, range, mean, quantile, subgroup outcome, association or effect was emitted or calculated.

The root script respects its declared boundary: explicit path input; fixed expected hash and header; row-width validation without row-content errors; key/missingness counters; the declared availability intersection; no network, directory discovery, numeric clinical processing, endpoint fitting or reference-effect selection. Its output count is labelled availability rather than a frozen analysis population. Missingness here is strictly the specified trimmed blank or literal `NA` rule; this check does not independently validate all possible source processing or missing-value conventions.

## Identity, header and counts

Input: `D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/virtual_cohort_system/work/scaleup_2026-11-01/private_data/22Jul20_for_Dryad_noIDs.txt`.

| Item | Independent result | Comparison with root audit |
|---|---:|---|
| Bytes | 87,736 | Exact agreement |
| Rows in deposit | 1,226 | Exact agreement |
| Columns including identifier | 14 | Exact agreement |
| Distinct nonmissing IDs | 1,226 | Exact agreement |
| Duplicate nonmissing-ID groups | 0 | Exact agreement |
| Duplicate nonmissing-ID extra rows | 0 | Exact agreement |
| Nonmissing Age/Sex/BMI/Total cholesterol/HDL cholesterol intersection | 397 | Exact agreement |

SHA-256: `7508097bd6578307a55aef793c15b4c26d2346e2d8e60e55ba8bf9d5254037f9` — exact agreement.

Header, in order: `Individual ID`; `Waist circumference`; `Systolic BP`; `Diastolic BP`; `Blood glucose`; `Body fat`; `Total cholesterol`; `HDL cholesterol`; `Triglycerides`; `LDL cholesterol`; `Sex`; `Age`; `BMI`; `Lifestyle category`. Exact agreement with the root audit. There are **thirteen substantive fields**, not thirteen directly measured biomarkers.

| Field | Missing blank/NA count |
|---|---:|
| Individual ID | 0 |
| Waist circumference | 22 |
| Systolic BP | 30 |
| Diastolic BP | 82 |
| Blood glucose | 790 |
| Body fat | 391 |
| Total cholesterol | 825 |
| HDL cholesterol | 820 |
| Triglycerides | 821 |
| LDL cholesterol | 873 |
| Sex | 0 |
| Age | 0 |
| BMI | 28 |
| Lifestyle category | 0 |

Every missingness count agrees exactly with `TURKANA_SCHEMA_AUDIT.json`. No discrepancy was found in the requested outputs.

## Interpretation limit

The 1,226 deposit rows and 397 five-field-available rows are **not final analysis eligibility counts**. This review applies no age restriction, measurement-validity rule, medical selection, fasting criterion or target-specific exclusion. It does not establish representativeness, biological validity, statistical precision, independence from published target summaries, or adequate power for any proposed endpoint. The separately recorded public-paper exposure remains in force. No target scientific relationship was reconstructed by this audit.
