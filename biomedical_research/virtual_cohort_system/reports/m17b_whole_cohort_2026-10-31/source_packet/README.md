# Aggregate source packet for M17b

This packet contains three original non-NHANES publications and 51 reported aggregate evidence items. It is a curator proposal for root admission, not an approval record or a generator specification. There are no individual participant records. No target moments are included. The exact reported values are retained, including source relationships; no target analysis endpoint or desired result was used to choose values.

| Source ID | Original publication | Relevant original locators |
|---|---|---|
| S1_BOGALUSA_2014 | [Sun et al., Bogalusa Heart Study](https://pmc.ncbi.nlm.nih.gov/articles/PMC4208749/) | Table 1 adult panel: sex/race n, age, BMI and urate means/SDs. Table 2 adult BMI row: age-adjusted BMI-on-urate coefficients. Methods s2b–s2e. |
| S2_KAHP_2015 | [Lee et al., Korean health examinations](https://pmc.ncbi.nlm.nih.gov/articles/PMC4750804/) | Table 1: pooled-sex summaries in <40, 40–59 and ≥60 groups; Methods Sec3–Sec5. |
| S3_CHS_2009 | [Ekundayo et al., Cardiovascular Health Study](https://pmc.ncbi.nlm.nih.gov/articles/PMC2906633/) | Table 1 BEFORE MATCHING columns; Section 3.1 second sentence for pre-match urate means/SDs; Sections 2.1–2.2 for selection and assay. |

`SOURCE_MANIFEST.json` lists ready-to-register fulltext and per-source extraction paths and SHA-256 hashes. Each file in `extractions/` carries its source context, reported statistics and exact original-cell locators. `reported_statistics.json` and `verified_table_cells.json` are combined convenience copies. Source JSON entries label values as reported; no derived coefficients or pooled moments are supplied. `unknowns_and_transport.json` records missing information and the quota design supplied by root. `CURATOR_CHECKS.json` records checks actually performed.

The source set supports inspection of published marginal summaries and a limited adjusted relationship. It does not identify the full requested joint distribution. In particular, no selected paper gives all eight age-by-sex quota cells. Race-specific Bogalusa evidence cannot be silently transported into a race-free cohort. Its reported regression has BMI as the outcome; its reciprocal is not an urate-on-BMI effect and its standardized coefficient is not a Pearson correlation. CHS groups are defined by sex-specific urate thresholds and include participants over 79. Korean age groups are open-ended and have different selection and population context.

All patient-level source data and target data remain outside this packet. Source sample sizes, means and SDs are original publication evidence and must not be read as the requested target cell counts or target moments. The two fresh builders should read the same admitted packet and choose their constructions independently.
