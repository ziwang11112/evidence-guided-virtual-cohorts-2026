# Evidence-guided virtual cohorts

Private research development repository. This is an explicitly allowlisted export of method documents, reusable code, artificial-fixture tests and aggregate analytical results. It is not a complete copy of the research workspace.

Start with [the current results](biomedical_research/evidence_virtual_cohort_framework_2026-10-27/RESULTS.md), [method and experiment plan](biomedical_research/evidence_virtual_cohort_framework_2026-10-27/METHODS_AND_EXPERIMENT_PLAN.md), [paired Agent strategies](biomedical_research/evidence_virtual_cohort_framework_2026-10-27/AGENT_STRATEGIES.md), and [manuscript scaffold](biomedical_research/evidence_virtual_cohort_framework_2026-10-27/MANUSCRIPT_SKELETON.md).

The completed retrospective batch has 144 input tables and 5,040 analysis records, with 36 pooled completion outputs and no analysis/pooling failures. Those inputs are one already examined clinical cohort, masks/completions of it, and draws from one existing generator. They are not 144 independent studies. Most completion outputs are unchanged-data preservation controls. Current results do not establish an Agent advantage, clinical validity, population coverage or recruitment savings.

The subsequent frozen Stage 1 construction experiment includes nine initial lineages across three previously exposed development cases, eighteen paired Agent revision arms and three fixed statistical arms. Its 420 final cohorts yield 7,700 analysis records. Cohorts and scenarios are analyzed separately; CSV and JSON versions of the analysis table contain the same records. The export includes the construction code, decisions, source-only diagnostics and aggregate evaluation, with participant-level and generated cohort tables omitted.

Read [the completed Stage 1 report](biomedical_research/evidence_virtual_cohort_framework_2026-10-27/stage1/RESULTS.md), [all-term comparisons and figures](biomedical_research/evidence_virtual_cohort_framework_2026-10-27/stage1/reporting/README.md), [independent post-run review](biomedical_research/evidence_virtual_cohort_framework_2026-10-27/stage1_review/postrun/POSTRUN_REVIEW.md), and [the advance/stop decision](biomedical_research/evidence_virtual_cohort_framework_2026-10-27/stage1/DECISION.md). The unchanged scenario policy did not show consistent analytical improvement and is not being advanced to the planned broad expansion. The complete outputs, uncertainty discrepancies and fit warnings remain available.

## Contents

- `biomedical_research/evidence_virtual_cohort_framework_2026-10-27/`: plan, strategy contract, manuscript skeleton, expanded retrospective batch, aggregate outputs and independent review.
- `biomedical_research/population_framework/`: generic runner, observers, common builder request and artificial-fixture tests; selected prior policy-comparison summaries preserve negative results.
- The method project's `stage1/` and `stage1_review/` contain the frozen three-case protocol, candidate construction bundles and source audits. See [the Stage 1 export boundary](docs/STAGE1_EXPORT.md) for path transformations and reproduction limits.
- `biomedical_research/obesity_paper_replay_2026-10-27/paper_analysis.py` and `biomedical_research/obesity_masked_completion_2026-10-27/custodian/`: unchanged analytical and validation modules used by the archived batch.
- `docs/`: export/data policy, local reproduction limits and earlier limitations.
- `sync/`: exact source allowlist, content hashes, refresh/audit scripts and file inventory.

No participant-level reference, masked or completed tables are included. Full synthetic cohort tables are also omitted in this initial export. No paper PDFs/HTML, downloaded supplements, environments, credentials or patient-bearing prompts are included. The CSV files here are analysis-level summaries.

## Run the independent checks

The export preserves the `biomedical_research/` package tree. Use Python 3.12 and a compatible installation of numpy, pandas, scipy and statsmodels. Exact versions used by the original batch are recorded in its `results/summary.json`; this export does not vendor an environment.

From the repository root:

```shell
python -B -m unittest discover -s biomedical_research/population_framework/tests -v
python -B -m unittest discover -s biomedical_research/evidence_virtual_cohort_framework_2026-10-27/development_batch/attempt_02 -p test_batch.py -v
python -B biomedical_research/evidence_virtual_cohort_framework_2026-10-27/stage1/test_stage1.py
python -B biomedical_research/evidence_virtual_cohort_framework_2026-10-27/stage1/test_reporting.py
python -B sync/audit_export.py
```

The fixture tests require no study data. The full batch and original independent audit require omitted local artifacts. Do not interpret archived original `run_batch.py verify` instructions as a claim that this public-data-free checkout can replay the clinical study. See [reproduction and local data](docs/REPRODUCTION.md).

## Synchronization

`sync/sync_export.py` copies only exact entries in `sync/source_allowlist.json`. It never discovers new research files, uploads files or pushes Git. Changes to the allowlist require content review. A local refresh is:

```shell
python -B sync/sync_export.py --workspace PATH_TO_LOCAL_RESEARCH_WORKSPACE
python -B sync/audit_export.py
```

Review `sync/EXPORT_AUDIT.json` and the complete `sync/FILE_INVENTORY.tsv` before an explicit Git commit/push. This repository should remain private. The repository's remote access control must be checked separately; the scripts do not change GitHub visibility.
