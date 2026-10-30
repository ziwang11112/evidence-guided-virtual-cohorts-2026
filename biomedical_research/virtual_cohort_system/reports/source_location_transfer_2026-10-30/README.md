# M11 curated source-location transfer record

See [the full result report](../../MILESTONE_11_RESULTS.md). Source-median calibration improved fitted SHIP statistics but worsened the new NHANES HbA1c target's level/subgroup discrepancies. All versions are retained.

This is a review/reproduction record, not a standalone portable package. It contains code, protocol, frozen scientific candidate files, constructed source covariates, source/target execution receipts, aggregate results and independent audit code. Participant-level observed/reference/generated target tables, weights/ID mappings, raw XPTs and downloaded paper full texts are deliberately excluded. The CSVs under candidate `source_contexts/` are artificial source-population inputs generated from published summaries, not participants. Result CSVs contain aggregate estimates only.

Original receipts bind private local inputs and paths. Hashes can be inspected here, but full original receipt verification requires those exact local files. Do not claim successful portable reproduction from this export alone. Source URLs, source-artifact hashes and extraction locations are retained in `source_audit/source_evidence_packet.json`; fresh web downloads may differ in bytes. Original participant inputs remain in the workspace.

For an original-workspace reproduction, preserve `work/m11` and its layout, use `custodian` preparation scripts only under the documented data boundary, restore admitted source bytes, run source construction scripts through the documented harness, and use `controller/campaign.py` stages freeze/execute/seal/evaluate after assigning new output locations. Existing frozen artifacts are not overwrite targets. The campaign depends on the sibling `cohort_harness` and approved WSL runtime; exact environment and limits are in execution receipts. Source scientific choices are documented in `source_plan.json` and each candidate specification.

Checks: 18 invented-data tests; 12 independently recomputed source corrections; 36 successful isolated source executions; 24 successful target executions; independent arithmetic verification of all 24 target tables. Custodian/code review is not a fully outcome-blind external reproduction. Default Windows pytest-temp permission errors and a pre-parse custody self-test repair are retained in audit/preparation records.

`file_manifest.json` binds every exported file except itself. No model-performance superiority, clinical equivalence or calibrated uncertainty claim follows from this pilot.
