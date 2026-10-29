# Successful source-only supplement recovery log

2026-10-29 UTC; task began about 22:01 and recovery/extraction completed about 22:07, within the requested 20-minute bound. No further literature search was needed after the requested supplement was recovered.

## Information boundary

Read the evidence-cohort-generation SKILL.md and harness-interface.md; read only the authorized previous research directory and external public primary-source material. Wrote only to this joint-evidence-pilot research directory. No custodian, target data, prior scientific result, inventory outside research, generator, or candidate file was accessed. No generator was executed. These artifacts are source extraction and provenance, not a self-issued harness admission record.

## Search queries issued (six)

1. `"1158383" "supplementary"`
2. `"Mikkelsen" "1158383" Tromsø munin`
3. `"1158383" site:munin.uit.no`
4. `"1158383" "Table_1"`
5. `PMC supplementary files open data S3 PMC10308115`
6. `"1158383" site:diva-portal.org`

The fifth query surfaced current official PMC AWS documentation. Its October 2026 page reports completion of the new distribution structure and removal of legacy FTP/cloud distribution files in August 2026. This is a documented public retrieval route, not a browser challenge bypass. The repository search also located a DiVA article PDF, but it was not needed or retrieved. No China-PAR or other fallback evidence was fetched or altered.

## Retrieval chain and selected version

- Official documentation opened: https://pmc.ncbi.nlm.nih.gov/tools/pmcaws/
- Public archive README opened and saved: https://pmc-oa-opendata.s3.amazonaws.com/README.txt
- Followed its documented ListObjectsV2 pattern: https://pmc-oa-opendata.s3.amazonaws.com/?list-type=2&prefix=PMC10308115.&delimiter=/
- Result: exactly one version prefix, `PMC10308115.1/`; listing preserved as `PMC10308115_versions.xml`.
- Metadata saved: https://pmc-oa-opendata.s3.amazonaws.com/PMC10308115.1/PMC10308115.1.json
- Metadata matches PMID 37396133 and DOI 10.3389/fnut.2023.1158383; is_manuscript=false, is_pmc_openaccess=true, is_retracted=false, license CC BY. This establishes why the sole listed version was selected.
- Supplement link present in metadata was retrieved: https://pmc-oa-opendata.s3.amazonaws.com/PMC10308115.1/Table_1.DOCX
- Article XML from the same version was retrieved: https://pmc-oa-opendata.s3.amazonaws.com/PMC10308115.1/PMC10308115.1.xml
- All five local source artifacts and their exact-byte hashes are in `source_artifact_manifest.json`. Supplement size is 686738 bytes. Its MD5 `fac328bf60febc38d736b0951fc4a7a1` exactly matches the official metadata; SHA256 `14b0f6ddecd322bab4ea51220599008156599e9587e9f6b001eadcbbb640536c`. Main XML MD5 `f736d5a9c365e1452c4b79c9ec395b31` also exactly matches metadata.

## Checks and extraction

- Parsed the DOCX ZIP package, preserving complete word/document.xml, complete table cells as JSON, and plain text.
- Extracted 30 joint age/BMI/sex rows including two reference rows, so 28 nonreference ratios and 95% CIs. Unique keys and confidence bounds were checked. Raw estimate/CI strings and 1-based DOCX table and row indices are retained in the tidy extraction.
- Inspected package relationships and all media entries. The sole image is attached to header2.xml and was visually inspected as the Frontiers logo. No numeric image, OCR or digitization was used.
- Read exact primary article Sections 2.2, 2.4, 2.5, 3.2.2, 3.2.3 and Figures 2/3 captions. Context excerpts retained.
- Preserved main-text versus supplement sample-size discrepancy (men 9341 vs 9583). Used the supplement's n for its own rows, with discrepancy explicit.
- Preserved adjustment ambiguity: general S1 footnote and Figure 3 caption list education/drugs for all; Figure 2 says women-only and only women have those coefficient rows in S1. Did not assert identical sex-specific covariate sets.
- Preserved women age40-49 BMI25-29.9 RD1.24 CI[1.23,1.28] exactly despite unusual interval asymmetry; no numerical correction or SE inference.
- Initial Python stdout printing failed because Windows cp1252 could not encode >=; the UTF-8 extracted files had already saved correctly. Later reads and scripts explicitly used UTF-8. One measurement-inspection shell attempt lacked its per-call output-directory variable and wrote nothing; corrected on the next call. Neither error changed source bytes or extracted values.

## Outcome

The requested exact supplement is available, with full provenance and known source inconsistencies. It provides quantitative within-sex joint age-category/BMI-category conditional TG ratios that can constrain a general source-derived conditional shape. It does not provide a baseline intercept, individual residual SD, between-sex baseline effect, coefficient covariance, or within-cell continuous slopes. Population/measurement/covariate transport remains assumption-dependent. No further search or invented missing coefficient was needed.
