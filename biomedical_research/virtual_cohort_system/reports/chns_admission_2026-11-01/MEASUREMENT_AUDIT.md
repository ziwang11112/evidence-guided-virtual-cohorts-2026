# CHNS measurement metadata audit — 1 November 2026

**Decision: measurement identity is better specified, but the case is not admitted.** Central/non-field glucose, field glucose and HbA1c must remain separate. Actual release schema, fasting eligibility, assay provenance and compatible covariate files still require confirmation before F2.

This audit read official methods/protocol metadata, not participant data, numerical participant distributions, codebook frequency tables or target-effect papers. It performed no data analysis or generator execution. These are metadata documents, **zero newly deeply audited original studies**; the six-study quota is unchanged. The historical exposure log and three-family ceiling remain applicable.

## Sources and release scope

The official [Biomarker Data page](https://chns.cpc.unc.edu/data/datasets/biomarker-data/) describes the 2009 release as 26 fasting blood measures for people aged seven and older. This is a release description, not an adult eligible or complete-case sample count. Its linked results paper was not opened. The [documentation index](https://chns.cpc.unc.edu/data/documentation/) separately identifies ID, analysis-unit, missing-value and data-cleaning documentation; the index does not establish a valid join or measurement mapping.

The two-page [Biomarker Methods table](https://chns.cpc.unc.edu/wp-content/uploads/Biomarker_Methods.pdf) was read and both pages visually inspected. The July 2009 [Specimen Collection and Processing Manual](https://chns.cpc.unc.edu/wp-content/uploads/Blood-Collection-Protocol_English.pdf) has 63 physical PDF pages; relevant text and ambiguous schedule/storage pages were inspected. References below distinguish physical PDF page from printed page.

## Released-field candidates: retain exact distinctions

| Field | Methods-table metadata | Unit and unresolved boundary |
|---|---|---|
| `GLUCOSE` | Serum; GOD-PAP; Randox, UK; Hitachi 7600. | **mmol/L**; p. 2 lists factor ×18 alongside mg/dL reference units. No conversion was performed. |
| `Y48_1` | Explicitly field-measured glucose; serum; same listed method, reagent producer and instrument. | The p. 2 unit table has no separate `Y48_1` row. Do not silently assert its released-file unit from the central/non-field row alone. |
| `Y50` | Fresh whole blood; method notation HLC/HLC/HPLC; Tosoh HLC-723 G7, Bio-Rad D10 and Primus PDQ A1c; Bio-Rad calibration stated. | **Percent**, p. 2. Exact instrument-to-record mapping and certification/traceability are not established here. |

Source: [methods p. 1](https://chns.cpc.unc.edu/wp-content/uploads/Biomarker_Methods.pdf#page=1) and [p. 2](https://chns.cpc.unc.edu/wp-content/uploads/Biomarker_Methods.pdf#page=2). `GLUCOSE` is the central/non-field candidate in the existing checkpoint; the table itself labels it simply glucose. Preserve that distinction, but verify the released dictionary's laboratory provenance rather than infer it solely from the unprefixed name. Neither glucose field should be relabelled plasma.

## Protocol checks and ambiguities

- Eligibility: age **≥7** (PDF 10/printed 8; 28/26).
- Fasting: **8–12 hours** in preparation instructions (30/28), versus **8–16 hours** in specimen sections (52/50; 58/56). Uniform 12-hour compliance is unsupported.
- The schedule includes afternoon venipuncture (13/11), not universal morning collection.
- Serum stands before centrifugation, completed within three hours (17/15; 41/39; 48/46). Actual delays are unknown.
- Glucose appears in on-site and Beijing-central testing (51/49; 55/53). HbA1c is assigned to one provincial central laboratory per province, using EDTA whole blood (53/51; 54/52).
- Whole-blood storage: 2–8°C (44/42), versus HbA1c's seven days in “freezing condition” (54/52); test promptly within seven days (38/36). This ambiguity does not establish mishandling.
- The on-site glucose row prints **mol/L** (53/51), whereas the methods/central tables use **mmol/L**. This discrepancy is not authority to rescale released values.
- Questionnaire verification is required (37/35); fasting-compliance fields/completeness remain unverified.

All references in this subsection point to the [official collection manual](https://chns.cpc.unc.edu/wp-content/uploads/Blood-Collection-Protocol_English.pdf). They describe intended procedures, not observed compliance or released-record quality.

## Consequences for source compatibility and admission

These are review requirements, not new clinical findings:

1. **Choose and freeze one glucose measurement definition.** A source reporting fasting plasma glucose does not automatically bind to either serum field. A field/central substitution, averaging rule or fallback would need a justified, prospectively specified mapping; do not select among them after viewing target relationships.
2. **Treat units and scaling explicitly.** A per-mg/dL, per-mmol/L or per-ten-unit source effect needs the corresponding declared scale. The S1 identity gate does not implement these conversions. HbA1c percent must not be silently relabelled mmol/mol, nor does the listed calibrator alone prove cross-study assay equivalence.
3. **Separate collection intent from analysis eligibility.** Adult age bounds, observed fasting requirements, medication/diagnosis exclusions and missingness rules remain unfrozen. Neither the release title nor a reference-range table supplies these decisions or a sample-size estimate.
4. **Resolve schema without target-effect exposure.** Confirm exact SAS names/types/units, missing-value codes, assay/laboratory indicators, collection/fasting fields, and IDs against the versioned release and appropriate official metadata. Then identify compatible age/sex/anthropometry files. No such join or eligibility calculation was done here.
5. **Require independent applicability review.** Similar assay labels are insufficient to certify common population, specimen handling, estimand, weighting or uncertainty. No study-effect evidence was newly admitted; no source-to-target identity or calibrated transport uncertainty is claimed.

Clinical reference intervals and instrument linearity bounds visible in the methods table were not treated as participant distributions, outcome targets or automatic analysis exclusions. The protocol's translation/formatting inconsistencies should remain explicit until a source-authoritative resolution is available.

## Local acquisition and provenance

`rg --files` searches found no matching existing methods/protocol PDF under the project before acquisition. Only the two allowlisted official URLs above were downloaded, each below the 5 MiB document cap:

| Local metadata file | Actual downloaded/stored bytes | SHA-256 |
|---|---:|---|
| `measurement_sources/Biomarker_Methods.pdf` | 464,994 | `86d698ec005ea7ed35147c66dfa8e31c3dd7dd3ff43d4c2869be42d30ad924c7` |
| `measurement_sources/Blood-Collection-Protocol_English.pdf` | 1,362,462 | `b6528bbb67dc1bc6e4a9a17e9f34b2f1e5a3c7cc4497c45bee44cdb930e164b7` |

**Total metered payload: 1,827,456 bytes**, to debit against the continuation's 500 MiB cap. Both returned HTTP 200/application/pdf with matching Content-Length; final URLs were unchanged. Web-tool traffic and HTTP header/TLS overhead were not metered. The exact transfer record is `measurement_sources/DOWNLOAD_LEDGER.json`. PDF originals and local page renders remain local; they are not authorized public-repository payloads. Participant-file downloads and target-effect calculations in this subtask: **zero**.
