# Reproduction and local data

This is a code-and-aggregate-results export, not a turnkey clinical-data reproduction package. Source code and batch outputs are retained byte-for-byte unless the export manifest records a transformation. Frozen original files are never repaired or rewritten by this export.

## What works without patient records

The generic runner and observer tests exercise artificial fixtures, including stage isolation, immutable run artifacts, numerical diagnostics and preservation claims. The seven retrospective batch tests also use artificial fixtures. `sync/audit_export.py` verifies exported hashes, aggregate table structure, blocked file types, secret patterns and local-path exposure.

The original batch output manifest can be checked against the five included aggregate execution/output files. It references an omitted original pre-execution freeze by hash. That hash is provenance, not a claim that the omitted artifact is available in this checkout.

## What is deliberately unavailable

The 75-person, five-visit reference table, three masked tables, 120 completion tables, individual mask keys, original source-file freezes, execution case packets and full synthetic cohort files are excluded. Masked and completed tables retain observed patient cells and must be treated as participant-level material. Earlier result reports that quoted individual source observations were omitted rather than copied verbatim.

The archived `run_batch.py` and `audit_attempt_02.py` need that omitted material to verify source hashes and recompute clinical models. Their original relative tree is preserved, but they cannot complete a full run from this checkout alone. The existing freezes may contain machine-local absolute paths; relocating an original research archive therefore needs a separate, explicitly versioned provenance-aware adaptation, not silent path replacement inside frozen records.

## Public source and local layout

The earlier study replay used the article [PLOS ONE 10.1371/journal.pone.0243530](https://doi.org/10.1371/journal.pone.0243530) and its [public S1 supplementary workbook](https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0243530.s001&type=supplementary). Consult source terms and metadata before obtaining it. No supplement is bundled here and the export scripts never download data.

The original local archive expected sibling folders beneath `biomedical_research/`:

```text
obesity_paper_replay_2026-10-27/
  paper_analysis.py                 included code
  evaluation/real.csv              omitted participant-level reference
  evaluation_freeze.json           omitted original source commitment
  runs/...                         omitted prior generation archive
obesity_masked_completion_2026-10-27/
  custodian/evaluate.py            included code
  custodian/validate_completion.py included code
  freeze.json                     omitted source/input commitment
  ...                             omitted masked/completed inputs and case packets
evidence_virtual_cohort_framework_2026-10-27/
  development_batch/attempt_02/
    run_batch.py                   included unchanged code
    freeze.json                    omitted original registry/source commitment
    results/                       included aggregate analysis outputs
```

Obtaining the public workbook alone does not reconstruct all historical Agent outputs, case masks and frozen execution context. A fresh reproduction must separately define and freeze its data transformation, masking, generators, model versions, seeds and analysis environment. It must use a new experiment directory and report any differences from the archived run.

## Export transformations

The independent review's `verification.json` contains original machine-absolute filenames as hash-map keys. Only these workspace path strings are normalized to repository-relative paths in the exported copy; numerical findings and artifact hash values are preserved. `sync/EXPORT_MANIFEST.json` records both source and export SHA-256 values and names the transformation. The original local review remains unchanged.

Local sync and audit paths are portable. Some archived Markdown links refer to intentionally omitted source artifacts; absence is part of the export boundary, not evidence that a result was regenerated in GitHub.
