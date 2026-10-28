# Postrun aggregate and provenance audit — 2026-10-28

No blocking reporting or consistency error found in the reviewed artifacts. This audit reads aggregate results, source diagnostics, code/specifications, and receipts only. No participant-level observed, generated, hidden-outcome, or raw tables were opened; no scientific models were refitted. Only this audit file was written.

All five frozen endpoints are present in the curated and original reports: adjusted BMI, adjusted age, adjusted female-versus-male contrast, BMI curvature, and BMI–sex interaction. The endpoint table contains all 50 endpoint-by-stage-by-seed rows, with 25 matched initial/final comparisons. Recalculation of medians, ranges, absolute errors, and direction counts from that aggregate table agrees with both reports. Original result/aggregate manifests and the curated file manifest match their retained files.

| Endpoint | Initial median absolute log error | Final median absolute log error |
|---|---:|---:|
| Adjusted BMI per 5 kg/m² | 0.085841 | 0.067545 |
| Adjusted age per 10 years | 0.011070 | 0.010205 |
| Adjusted female versus male | 0.044027 | 0.088497 |
| BMI curvature second difference | 0.006334 | 0.003350 |
| BMI–sex interaction | 0.051420 | 0.013529 |

Four of five endpoint median absolute errors decreased. This must not be restated as four median estimates moving closer, or as uniform improvement across draws. In particular, the age median estimate moved from 0.070196 to 0.073300 against reference 0.063095: farther away, despite its slightly lower median absolute error. Three of five paired age errors increased. BMI remains overstated: its final median estimate is 0.168709 versus reference 0.101164. The sex contrast worsened. The reference interaction interval includes zero (−0.069019 to 0.002249); its negative point estimate does not establish a negative population interaction.

The source comparison contains 29 checks: 21 involve generated TG, with 13 smaller and 8 larger absolute discrepancies; all 8 covariate-only checks are unchanged. Values agree with the retained replay reports. These correlated checks use mixed units and are not an aggregate scientific score or independent confirmations. Source-replay plans are byte-identical, retain the same source-context commitments and check definitions, and use identical limits/seed. The actual parameter changes are common arithmetic BMI slope 6.8 → male 8.0/female 5.0 mg/dL per kg/m², and female residual log SD 0.48 → 0.50. Other parameter groups are unchanged; the final generator uses those changes.

Recorded UTC chronology is consistent: initial freeze 18:41:16; initial source feedback 18:41:51; final freeze 18:48:43; final source feedback 18:49:19; all 10 successful execution receipts precede commitment at 18:50:21; evaluation release is 18:51:05 and completion 18:52:01. Current candidate-freeze hashes match the pre-evaluation commitment and release receipt. Current code/specification/evidence/recipe/decision bytes match their freezes; final has revision index 1 linked to initial. Execution receipts bind the committed output hashes and fixed seeds. Output bytes were not reopened in this audit. No post-evaluation change appears in this retained lineage; the completion receipt records one evaluation attempt. These are trusted-host receipts, not signatures or proof of the Agent's external access history.

This is one public-case Agent construction, one source-feedback revision, and five residual draws per stage (10 generated tables), followed by one held-out evaluation. Draws, rows, and endpoints are not independent scientific replications. The controlled invented fixture is an interface check, not another clinical validation. Generated intervals omit evidence/model/transport uncertainty; draw ranges are simulation sensitivity. There is no matched extra-compute/no-feedback control, calibrated equivalence claim, causal identification, clinical replacement claim, or evidence of general method superiority.

The curation code copies an explicit list of aggregate results, candidate text/code, and methods. The reviewed methods directory contains code, protocol, count-only reader amendment, and invented-fixture guard validation; no participant rows or raw data are embedded. These relocated methods are review snapshots, not a standalone executable data package. The earlier source audit correctly describes its pre-evaluation scope; this postrun audit is separate.

Reviewed SHA-256 hashes follow. `R` denotes `reports/source_feedback_2026-10-28/`; `E` denotes `work/source-feedback-2026-10-28/custodian/nhanes_tg_j_v2/evaluation/`; `W` denotes `work/source-feedback-2026-10-28/`.

| Artifact | SHA-256 |
|---|---|
| R/aggregate_results.json | `514e98f6fe363121c89117a7c27c7100ef4ce851389ec8522a0ef3010c2ed47e` |
| R/source_diagnostic_comparison.csv | `91674649313623fbf34e74c28f0ac03de4977793d535a09a6d4cf690e42de5c8` |
| R/endpoint_comparison.csv | `b1e30ee5e42b424fd06a450f1dc9cc7dc77e1e2e32be584e98a4ceb866b572c4` |
| R/initial_final_changes.csv | `e075d690cbc29097a82bc311a6e1cf608d5f2710ada2f211437869c53b13dc3b` |
| R/reference_analyses.json | `82bad198b750c5ea55f17b8f901bead8d58043fc1f85b9033865104565653fd0` |
| R/curated_file_hashes.json | `0f6ace131ccaa1c4dd15dc1985946bd2f7ee5bc4828af1020951911741c9ac9b` |
| E/aggregate_report.json | `9d29d2a0461fc3b418459a950c64e9ff3b6ebfad0aa6dd4d91642db229901d39` |
| E/aggregate_endpoint_summary.csv | `af695e214a613e1cd289e63c3e242f9d946559ad6600e903a9c2e286eaa96be2` |
| E/aggregate_hashes.json | `6de3a16a836f58e1fce44a09aa0b3fcbb5d56792e16f06b87a6875db7feb469b` |
| E/result_hashes.json | `6eea74fc43b10a4f3b72441b6388d9d8ea42c769b3a0442d59d6a97fec9a5369` |
| E/release_receipt.json | `74df4709bfb926e6f8ef61a0d09c19ce77045ab58fc797e25cec82552715c2af` |
| E/completion_receipt.json | `22ba39ce4a19a5d82253cdc4694cab3d29c379278b9bcd807ea81cc285b3f562` |
| W/evaluation_commitment.json | `2fdd5e7db3d97dd5d7864fb17347beb33fc72778a605df9f9dff2a81ddc5c4f9` |
