# Independent CHNS identifier and schema audit

1 November 2026. **PASS: all independently computed checks match the controller audit.**

ReadStat (`pyreadstat`) decoded only the explicitly requested ID/wave columns into returned frames. Python counters and set membership independently computed duplicates and linkage counts; the controller used pandas' SAS reader and dataframe duplicate/merge operations. The controller JSON was loaded only after all independent computations. This is a second decoder and counting implementation, not a rereading of reported counts.

No participant identifiers, clinical values, age/sex summaries, moments, associations or row excerpts were printed or saved. Per-wave counts are structural exposure and are not eligibility counts. No analytic cohort was formed. F2, state, generators and original-study quotas were not changed.

## Integrity and duplicate counts

| File | Header / decoded rows | Columns | Missing-key rows | Duplicate-key rows, all waves | Complete-key rows, 2009 | Duplicate-key rows, 2009 |
|---|---:|---:|---:|---:|---:|---:|
| `biomarker_09.sas7bdat` | 9549 / 9549 | 49 | 0 | 0 | 9549 | 0 |
| `pexam_00.sas7bdat` | 110449 / 110449 | 206 | 0 | 0 | 11929 | 0 |
| `mast_pub_12.sas7bdat` | 39674 / 39674 | 9 | 0 | 0 | Not wave-indexed | Not wave-indexed |
| `surveys_pub_12.sas7bdat` | 143564 / 143564 | 19 | 0 | 0 | 12178 | 0 |

Duplicate counts include every row in a repeated complete-key group, not just excess rows. Every observed key cell was separately checked for finite integral representation and magnitude below 2^53, including wave cells in rows with missing person IDs. Whole-file SHA-256 values also match the controller audit; no identifier was rounded or silently deduplicated.

## Wave counts and biomarker linkage

Wave counts include every nonmissing wave cell, even if the corresponding person key is missing; 2009 linkage counts use complete keys only.

- `biomarker_09.sas7bdat`: 2009: 9549.
- `pexam_00.sas7bdat`: 1989: 6927; 1991: 12942; 1993: 12015; 1997: 14323; 2000: 12752; 2004: 12180; 2006: 11742; 2009: 11929; 2011: 15639.
- `surveys_pub_12.sas7bdat`: 1989: 15907; 1991: 14797; 1993: 13895; 1997: 14441; 2000: 15831; 2004: 12308; 2006: 11860; 2009: 12178; 2011: 15725; 2015: 16622.

| Companion | Biomarker 2009 records | Matched | Unmatched | Cardinality |
|---|---:|---:|---:|---|
| `pexam_00.sas7bdat` | 9549 | 9516 | 33 | one_to_one |
| `mast_pub_12.sas7bdat` | 9549 | 9549 | 0 | many_to_one |
| `surveys_pub_12.sas7bdat` | 9549 | 9548 | 1 | one_to_one |

A matched identifier does not establish a nonmissing assay, anthropometry, age or gender value, same-day measurement, fasting compliance, biological eligibility or source applicability.

## Survey dictionary mismatch

The old `surveys_pub_12.pdf` lists 20 fields on pp. 1-3. Comparison with the actual SAS header, with field-name case normalized only, finds:

- Missing from the actual file: `AGE_DAYS`.
- Additional actual fields: none.

This is a documented release/dictionary difference, not an inferred rename. `AGE` remains a distinct field; its label's rounding/reference-date limitations from [CODEBOOK_SCHEMA_AUDIT.md](CODEBOOK_SCHEMA_AUDIT.md) still apply. No absent field was reconstructed or imputed.

## Comparison and reproducibility

Discrepancies: none.

Private checker: `independent_key_audit.py`; SHA-256 `8dac7d91d0db0ba4c79d5c433620c54486117f5563696d2cb746bae3c4a11a52`. Compared against `SCHEMA_AND_KEY_AUDIT.json`; SHA-256 `3cb8a6236d3c33f49b54b8b2279331228162ea76d6b96e45c6a079a21dd4d4b9`. The checker retains identifiers only in process memory and writes this aggregate Markdown report. No patient rows or additional dataset artifacts are saved.
