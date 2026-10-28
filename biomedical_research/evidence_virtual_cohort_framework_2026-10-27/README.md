# Evidence-guided virtual cohorts

Start with [RESULTS.md](RESULTS.md) for completed development work, or [METHODS_AND_EXPERIMENT_PLAN.md](METHODS_AND_EXPERIMENT_PLAN.md) for the proposed method-paper design.

The intended use is biomedical research rehearsal: preparing analyses, exploring evidence-compatible scenarios and evaluating study-design choices. Whole-cohort synthesis and partial-record completion are separate tracks. Exact numerical replication is not required; analytical interpretation, magnitude, uncertainty and practical usefulness remain visible.

## Delivered

- A primary-literature-grounded paper and experiment plan.
- [Paired Agent strategy specification](AGENT_STRATEGIES.md), marked proposed rather than implemented.
- [Manuscript scaffold](MANUSCRIPT_SKELETON.md), with prospective results deliberately unfilled.
- [Successful retrospective analysis batch](development_batch/attempt_02/README.md): 144 existing tables, 35 outputs each, 5,040 records, no analysis or pooling failures.
- The first failed wrapper attempt, preserved with its parser explanation in [development_batch/STATUS.md](development_batch/STATUS.md).
- [Independent final review](independent_review/VERIFICATION.md): 44 checks passed, including all 36 pooled calculations and retained-output accounting.

The successful run is **attempt_02**. Do not use the first wrapper as the current entry point and do not overwrite existing freezes or result directories. The batch does not execute generators, call models or export participant records. Verification from the successful directory is `python -B run_batch.py verify`; a new execution needs a separate versioned experiment.

The next prospective experiment has not run. The current outputs involve one already examined clinical cohort, and most completion outputs are unchanged-data controls. See the plan for distinct study-level, builder-level and sampling-level counts.
