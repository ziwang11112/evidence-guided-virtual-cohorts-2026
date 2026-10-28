# Evidence-guided virtual cohorts

Start with [Stage 1 results](stage1/RESULTS.md) for the completed new construction experiment, [RESULTS.md](RESULTS.md) for the earlier completion replay, or [METHODS_AND_EXPERIMENT_PLAN.md](METHODS_AND_EXPERIMENT_PLAN.md) for the method-paper design.

The intended use is biomedical research rehearsal: preparing analyses, exploring evidence-compatible scenarios and evaluating study-design choices. Whole-cohort synthesis and partial-record completion are separate tracks. Exact numerical replication is not required; analytical interpretation, magnitude, uncertainty and practical usefulness remain visible.

## Delivered

- A primary-literature-grounded paper and experiment plan.
- [Paired Agent strategy specification](AGENT_STRATEGIES.md), implemented and executed in the frozen [Stage 1 controller](stage1/README.md).
- Three-case Stage 1: nine fresh initial constructions, eighteen paired revision branches, 360 Agent cohorts plus 60 statistical cohorts; all 420 generated and all 7,700 prespecified analysis records retained.
- [Stage 1 decision](stage1/DECISION.md): retain the audited software and analytical benchmark; do not scale the unconstrained scenario policy as an accuracy improvement.
- [Manuscript scaffold](MANUSCRIPT_SKELETON.md), with prospective results deliberately unfilled.
- [Successful retrospective analysis batch](development_batch/attempt_02/README.md): 144 existing tables, 35 outputs each, 5,040 records, no analysis or pooling failures.
- The first failed wrapper attempt, preserved with its parser explanation in [development_batch/STATUS.md](development_batch/STATUS.md).
- [Independent final review](independent_review/VERIFICATION.md): 44 checks passed, including all 36 pooled calculations and retained-output accounting.

The successful run is **attempt_02**. Do not use the first wrapper as the current entry point and do not overwrite existing freezes or result directories. The batch does not execute generators, call models or export participant records. Verification from the successful directory is `python -B run_batch.py verify`; a new execution needs a separate versioned experiment.

Stage 1 has run, with the protocol frozen before fresh construction and reserved evaluation. Its three cases remain historically exposed development studies. Independent-case confirmation, joint-evidence acquisition, and research-design utility experiments have not run. They are conditional expansion stages, not missing outputs silently counted as completed. The current multiple-scenario policy did not show a consistent analytical advantage, so the proposed 1,100-cohort expansion is not launched.

Private code/aggregate-results repository: https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026. The separate sanitized export excludes participant-level reference, masked, completed and synthetic cohort tables. Public source data must be obtained separately for full replay. See the versioned delivery manifests; the original `delivery_manifest.json` describes the earlier delivery, while `delivery_stage1.json` records the new one.
