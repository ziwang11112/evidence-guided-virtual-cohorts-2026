# Stage 1 export boundary

The Stage 1 export preserves the three-case development protocol, code, artificial-fixture tests, supplied marginal summaries, source checks, independent source reviews and frozen candidate construction artifacts. The nine initial candidates, eighteen policy revisions and three fixed statistical candidates are represented by source-only bundles. All 30 candidate manifests were present and each included file matched its original candidate commitment before copying.

Only these exact candidate filenames are eligible: `generator.py`, `decision.json`, `decision_template.json`, `evidence.json`, `schema.json`, `task.json`, `source_checks.py`, `source_feedback.json`, `REQUEST.md`, `staging_lock.json`, `candidate_manifest.json`, and the three `parent/` code/decision/feedback snapshots where present. The source-only diagnostic records contain aggregate summaries, not individual generated or observed rows. The 21 final `manifest.json` files retain seeds, counts, relative filenames and original hashes as execution metadata. The actual final cohort CSV files and participant-level custodian references are excluded.

Prelaunch v1/v2 implementation snapshots and v2/v3 amendment records preserve the protocol changes, including equal calibration allowance, the final-inventory gate and the baseline-only enrollment bound. Construction notes retain model differences and limitations. Retired unexecuted staging directories are described by the amendment logs; they are not silently represented as completed candidates.

## Paths and commitments

The original `REQUEST.md` files contain a machine-local workspace prefix. That prefix is removed in the export, leaving the original run's repository-relative path. No evidence, policy instruction or numerical value is changed. `sync/EXPORT_MANIFEST.json` records the original and exported SHA-256 values and the path-only transformation. Candidate manifests and staging locks retain their original hashes, including the original request hash: they are historical commitments and therefore do not validate the transformed request bytes directly. Use the source/export mapping for this intentionally transformed field.

Every other Stage 1 source file is copied byte-for-byte. Exact reviewed source hashes and candidate-manifest membership are checked by `sync/sync_export.py`, which refuses a refresh after an unreviewed source change. The allowlist never expands automatically.

## Included aggregate evaluation

The completed evaluation contains 7,700 analysis records from 420 separately analyzed cohorts. `analysis_records.csv` and `analysis_records.json` are two representations of those same records, not additional analyses. The nine manifest-listed output files also retain 55 reference analysis summaries, 165 paired lineage comparisons, 385 scenario-sensitivity records, 825 scenario summaries and the dataset-failure list. These are estimates, intervals, diagnostics and comparisons, not participant-level observations. All nine original output hashes are checked by the export audit.

The reference-analysis JSON files are explicitly analytical summaries; they are distinct from the omitted `custodian/case_*_reference.csv` participant tables. Every scenario remains separately labelled. The final manifest's original cohort hashes provide provenance without publishing the cohorts.

The final presentation adds 17 aggregate CSV tables, six PNG plots and six corresponding vector-PDF plots, code, narrative reports and independent reviews. These PDFs are locally generated scientific figures, not downloaded papers. The export verifies all 35 reporting-manifest file hashes, the report's `RESULTS.md` hash and the 63 critical artifact hashes in `delivery_stage1.json`. Figure points represent per-cohort analysis estimates or uncertainty ratios, never participant measurements. All six PNGs were inspected during export review in addition to the author's recorded visual QA.

## Reproduction limits

From this repository root, these checks run without patient records:

```shell
python -B biomedical_research/evidence_virtual_cohort_framework_2026-10-27/stage1/test_stage1.py
python -B biomedical_research/evidence_virtual_cohort_framework_2026-10-27/stage1/test_reporting.py
```

These are ten contract tests plus one artificial reporting test. Their temporary synthetic fixtures are removed by the tests and are not part of the export. They do not open reserved clinical reference outcomes.

The original complete source audit and evaluator require separately obtained public study inputs, historical extraction scripts and local frozen reference tables. Stage 1 `protocol_freeze.json` includes hashes of those omitted local artifacts; this partial checkout cannot pass the original all-source verification or rerun its target evaluation without reconstructing that provenance. The preserved `custodian/paper_analysis.py` is analytical code only. No custodian reference CSV or original machine-path provenance inventory is included.

All three studies remain previously exposed development cases. Fresh construction contexts and committed outputs do not create independent confirmation. The permitted evidence consists of target-derived marginal summaries; matching them is reconstruction, and neither synthetic cohorts nor analysis rows increase the number of independent clinical studies.
