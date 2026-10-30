# M9/M10 export boundary and audit status

30 October 2026. The local M9/M10 export is copied and its full historical audit passes with zero findings. It contains 1,639 source records and 1,691 audited files, including 801 project source files. Commit and push remain pending controller steps. The scientific work does not depend on this archival step. The repository remains an inspection archive; omitted participant inputs and dependencies prevent a claim of self-contained clinical reproduction.

The exact reviewed delta contains 165 source files: the 37-file historical M9 preparation package, the 124-file M10 feasibility package, and four approved project documents. It adds 164 files and revises only the project README among historical source records. The four documents are `MILESTONE_9_PREPARATION.md`, `MILESTONE_10_RESULTS.md`, `README.md` and `docs/SCIENTIFIC_ANALYSIS_UTILITY_PLAN.md`. The separately edited repository overview is preserved with its own previous/current hash binding. All 838 nonproject source records and 656 unchanged historical project/local artifacts remain verified.

Both curated file manifests and 34 M9/120 M10 provenance pairs were checked. The four CSVs contain 16 source-screen metadata rows and 48, 16 and 6 aggregate result rows. Four plot files contain two PNG and two SVG aggregate charts. JSON structures were inspected for embedded participant records; identifier-like keys were schema declarations or adapters, and the insulin reference means were published aggregates. No raw work directory, participant/reference table, individual generated table, full text, runtime or credential is exported. The retained 124-check postrun review is an aggregate reviewer/implementer check, not an independent code audit. This archive does not turn the two-case feasibility study into a full four-method comparison or a superiority claim.

The initial pre-copy scan retained one remaining machine-path literal in the curated curation helper. The controller repaired it and refreshed provenance, the repair record and file manifest before copy. The first dry run then encountered three unchanged M7 paths longer than the Windows ordinary path limit. Extended-path reads verified their original hashes; a narrow root-path I/O correction allowed the existing checks to run without changing historical bytes. These attempts and repairs are recorded in `sync/M10_PRECOPY_REVIEW.json` and `sync/M10_FINALIZATION_LOG.json`. Source copies are byte-preserving, including the project README's CRLF endings. Six invented export-guard tests passed; no clinical test, generator or target analysis was rerun during export.

The M10 successor is pinned to M8 commit `72daa75a5c212ca511c0df5d72c5770685aa597e`. It records explicit historical/current hashes for the project README and hashes for every addition. Unchanged records and historical milestone receipts remain bound. The complete M8 audit runs on that Git snapshot through a byte-reader adapter; M8's rules and its M7-to-M3 historical chain are retained. The export therefore requires those Git objects, not merely a shallow checkout of the latest files.

## Before finalization

The controller first finishes and reviews its curated M9 preparation package, `reports/analysis_utility_feasibility_2026-10-30/`, the M10 report, scientific plan and project README in the source workspace. The exact M9 package name and document names are supplied by that review. Nothing under a raw work directory is discovered or copied by these tools.

Create `sync/M10_EXPORT_PLAN.json` only after that review. It must contain:

- `schema_version: 1`, `milestone: "M10"`, and the exact pinned `base_commit` above.
- `content_review_complete: true`, `participant_or_generated_output_rows_exported: false`, and `experiments_or_tests_rerun: false`.
- `curated_roots`: the exact repository-relative M9 and M10 report-package directories, each ending with `/`. The M10 directory is `biomedical_research/virtual_cohort_system/reports/analysis_utility_feasibility_2026-10-30/`.
- `project_documents`: exact repository-relative top-level project Markdown/JSON files plus the explicitly approved `docs/SCIENTIFIC_ANALYSIS_UTILITY_PLAN.md`. Only the existing project README may revise an M8 source record; other historical source bytes must remain unchanged.
- `files`: one entry for every selected file, with matching repository-relative `source` and `destination`, `transform: "none"`, a meaningful `classification`, and its exact lowercase `reviewed_sha256`. CSV/TSV entries also require `aggregate_table: {"rows": N, "required_keys": [...]}`. Binary plots require `classification: "aggregate_plot"`.

The plan is an exact addition/revision list, not a replacement for the historical allowlist. Paths cannot contain wildcards, traversal, raw/work/cache/runtime folders, or participant/generated-table filenames. Machine-specific path normalization must already be completed and disclosed in the curated source package; the export makes no further transformations. Human review is necessary: regular-expression scans and file names cannot establish privacy. Do not include full texts, credentials, participant records, hidden target tables or individual generated rows. Inspect aggregate JSON for embedded row-level arrays too.

## Finalization commands

Run from the export repository, using a local Python environment with the existing audit dependencies. `SOURCE_WORKSPACE` below is the local parent of `biomedical_research`; do not put its absolute path into an exported document or receipt.

```text
python -B -m unittest discover -s sync -p test_m10_export.py
python -B sync/finalize_m10_export.py --workspace SOURCE_WORKSPACE
python -B sync/finalize_m10_export.py --workspace SOURCE_WORKSPACE --apply
python -B sync/audit_export.py
git -c core.whitespace=trailing-space,space-before-tab,cr-at-eol diff --check
git status --short
```

The first finalizer call is a dry run. It checks reviewed hashes, existing export integrity, paths, credential patterns and aggregate table schemas. `--apply` repeats the checks, copies only approved bytes, and writes the additive allowlist, export manifest and `sync/M10_EXPORT_RECEIPT.json`. It never calls a generator, evaluates a target, starts a scientific test, commits, pushes or reads unallowlisted source files. Its invented export-guard tests are separate from scientific experiments. These commands describe the completed local procedure; the finalizer now refuses a second apply because its receipt exists.

Do not run the broad historical source refresher for this update: it could reread changed originals outside the approved M10 delta. Do not manually replace old milestone receipts or relax their historical checks. If the pinned base has advanced, a source hash changes, or a requested existing revision is broader than README, stop and review the new explicit successor scope.

The apply phase is not a multi-file transaction. If a filesystem failure interrupts writing, do not commit or push. Inspect the partial changes against the fixed M8 snapshot and the approved plan before restoring the affected export files or completing the reviewed copy. The finalizer refuses to overwrite an existing M10 receipt. A completed export must pass the full audit, including the historical snapshot chain; a failed audit is not bypassed.

After the full audit passes, review the diff, receipt, inventory and excluded-data boundary. Update this document with actual counts and status only then. Commit and push remain separate controller steps under the existing user authorization. Verify branch/remote identity, remote privacy and final working-tree state before claiming the archive is synchronized.
