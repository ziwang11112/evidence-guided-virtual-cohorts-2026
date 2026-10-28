# Fasting-insulin feature enrichment pilot

27 October 2026. New pilot under the [current research scope](../evidence_virtual_cohort_framework_2026-10-27/CURRENT_RESEARCH_SCOPE.md). Status: 20 generated enriched datasets, one frozen reserved evaluation and independent numerical audit completed. Start with [RESULTS.md](RESULTS.md). The main BMI association is retained; reserved shape and sex-slope differences are not recovered. All 84 fits and 168 endpoints were independently verified. No model is being tuned to these results.

Task: preserve observed BMI, age and sex, let a blinded Agent independently retrieve non-NHANES primary evidence and generate an entirely withheld fasting-insulin column, then evaluate reserved analyses on generated and real values. The target is the eligible NHANES 2017–2018 adult fasting subsample, with eligibility and units audited from official sources. This is a newly locked evaluation in this project, not a newly collected cohort or a guarantee that pretrained models never encountered NHANES publications.

Separation:

- `shared/`: visible covariates, target description, schema. No insulin, derived insulin quantities, target analysis results, or original participant IDs.
- `agent/`: exact construction request, independent evidence ledger, Agent-authored model and versioned decisions. Public literature access is permitted subject to source exclusion.
- `custodian/`: local public source downloads, private original-ID mapping, full fasting design spine, eligibility audit and locked real reference. Participant-level files are not included in GitHub exports.
- `review/`: analysis specification and implementation written without target results, source/code audit and artificial-fixture checks. These are not shown to the generation Agent except approved source/interface feedback.
- `runs/`: locally generated enriched tables and execution checks.
- `results/`: aggregate scientific comparison only after generation and evaluation inputs have been frozen.

The controller specifies an interface and integrity checks, not biological relations. A numerical sampler is permitted when authored by the Agent; its parameters and assumptions must be traceable. Twenty stochastic draws from one Agent-authored model do not establish between-Agent reliability. No original patient measurements are replaced in the source files. No inference of patient-specific true insulin is claimed.

This pilot assesses feasibility and analytical agreement. It does not yet compare a large model set, establish superiority, or prove reduced patient recruitment cost. Input-supported relationships and genuinely reserved target-specific analyses are distinguished. The complete-case eligibility domain limits population generalization.
