# NAGALA metadata-only schema review

Date: 2026-10-31. **No schema admission is possible from this pass.** Both authorized workbook download attempts failed. No workbook was saved or opened, so original headers, actual row/column counts, units, codes, and person-level structure remain unverified. The age/sex/BMI/fasting-plasma-glucose set is not semantically ready, and an exact clinical target is not definable from the admitted material.

## Contract and file identity

The pre-acquisition contract was verified against SHA-256 `ac44b2f2485dfa8ce162f11d1557134ea7c9689f8660c026e7c067a6d808829d`. It was not changed.

- Dataset DOI: [10.5061/dryad.8q0p192](https://doi.org/10.5061/dryad.8q0p192); version 22266; file 76808.
- Official filename: `Data set Int J Obesity.xlsx`.
- [Official version file-list API](https://datadryad.org/api/v2/versions/22266/files) reconfirmed the expected size **3,255,571 bytes** and MD5 **`47edfb147078657a0eecfff7f9364532`**. These describe the remote file; they are not hashes or measurements of an acquired copy.
- CC0-1.0 was documented in the existing official-API admission review.
- Actual workbook bytes and actual MD5/SHA-256: **unavailable**. Workbook bytes saved: **0**.

| Attempt | Official route | Result |
|---|---|---|
| 1 | `https://datadryad.org/api/v2/files/76808/download` | HTTP 401 Unauthorized |
| 2 | `https://datadryad.org/downloads/file_stream/76808` | HTTP 403 Forbidden |

The second URL was discovered by extracting only download hyperlinks from the [official dataset landing page](https://datadryad.org/dataset/doi:10.5061/dryad.8q0p192), and identifies the same file ID. No mirror or different data version was substituted. The two-attempt allowance is exhausted. The 10 MiB limit was enforced in the script, but no workbook body was received.

## Schema and clinical semantics

| Item | Admitted finding |
|---|---|
| Sheet names, original headers, row/column counts | Not available: workbook delivery failed. Metadata sample sizes were not substituted for workbook row counts. |
| Age | Column presence/name and unit unverified. |
| Sex | Column presence/name and category codes unverified. No code inferred. |
| BMI | The prior admission review records kg/m² from the original abstract. The released column, unit annotation, and coding remain unverified. |
| Fasting plasma glucose | Column presence/name, unit, fasting protocol, assay, and baseline-selection threshold unverified. |
| HbA1c | Column presence/name, unit scale, and assay unverified. |
| Person/longitudinal structure | One row per person and availability of baseline versus serial measures unverified. |
| Recruitment and selection | Exact primary-method dates, eligibility, diabetes definition, glucose threshold, and other exclusions unverified. Secondary snippets were not promoted to primary-method evidence. |
| Clinical target | Not fully definable: a conceptual baseline screening-cohort question does not establish a fixed population, operational endpoint, or harmonizable field definitions. |

## Original-paper methods access

Only the already-counted original [Okamura DOI 10.1038/s41366-018-0076-3](https://doi.org/10.1038/s41366-018-0076-3) was targeted. Direct publisher retrieval returned a `Client Challenge` document with no Methods section. An exact-DOI PMC identifier-conversion request reported that the identifier was not found in PMC. A browser-tool `find` for Methods on the exact publisher URL failed at an identity-provider redirect. Thus no primary-method text was available, and no additional primary paper was opened.

## Execution and exposure audit

`inspect_nagala_schema.py` enforces the contract hash, file-size cap, two-attempt cap, expected bytes/MD5, and metadata-only output. Python 3.12 and existing openpyxl 3.1.5 were available; nothing was installed. The workbook-inspection portion did not execute because acquisition failed. `finalize_schema_review.py` produces `SCHEMA_METADATA.json` from the verified contract and failed-attempt ledger without network access. The private ledger is `custodian/private/download_attempts.json`; no raw workbook exists.

The existing admission report contained original-abstract cohort/sex counts and proposed estimands. Those counts are not reproduced, used for construction, or substituted for schema observations here. The landing-page retrieval emitted download links only. No participant rows or examples, target-result tables, numerical effects, distributions, category frequencies, coefficients, analyses, generation runs, or uncertainty calculations were produced. No `STATE.json` mutation occurred. Finite cohort statistics have not been treated as population truth.
