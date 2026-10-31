# b2 revision1 independent review

**PASS for the scheduled pre-authoring commitment. No blocking inconsistency found.**

This is a pre-authoring science/plan review, not an assessment of target accuracy. Read only the named builder's proposed science files, its initial science/freeze metadata, actual initial source/self feedback, and existing observed-covariate aggregate notes. No private target outcomes, raw target files, actual generated CSV rows, or unapproved candidates were accessed. No candidate edits, parameter changes, outcome calculations from rows, or new row generation occurred.

## Preservation and feedback linkage

The proposed action is row_repair, with initial as parent. Evidence, model_spec and construction are byte-identical to initial. Embedded construction equals the standalone file, and all 23 planned source checks remain exactly unchanged: 16 approximate comparisons and seven not-computable entries. Their definitions, source mappings, operators, selection predicates, reasons and assumption IDs match the actual initial feedback. The initial feedback's self-report digest, freeze digest, generated-table binding and construction digest agree. At review completion revision1 contains only the four proposed science/plan files and no generated.csv.

## Numerical claims

The plan accurately quotes the four joint standardized deviation SDs (0.8874, 0.8558, 0.9010, 0.8864), overall SD (0.8766), range, and scale-unit exceedance counts (54, 0, 0). The group mean deviations, eight Yun source mean/SD discrepancies, four original-direction Sun coefficients, raw/standardized BMI and age correlations, rank, duplicate counts and outcome range agree with the initial reports at stated rounding. The four Lee values and band counts also agree. The cited band composition values match the existing observed-only aggregate note; no row-level covariate recomputation was performed in this review.

The decision distinguishes location changes induced by the assumed guide on fixed covariates from authored deviations; it does not treat source marginal means as target quotas. Reverse-regression differences remain in the original direction with age adjustment. Wider covariate variation is identified as a possible contributor, not an exhaustive explanation. The unchanged scale multiplier remains a disclosed heuristic, not an estimated conditional residual SD.

## Scientific interpretation and limits

The proposed limit of at most 12 literal changes is a prospective, bounded realization heuristic. The reviewer does not prescribe which rows, values, signs or coefficients to change. The plan explicitly allows poorer marginal source-SD agreement and does not promise improved target utility. Its use of working_guides, absence of a specified distribution family, and acknowledgment that greater tail coverage need not be biologically more realistic are appropriate.

SD below one means smaller finite deviations relative to the chosen guide scale; it is not a calibrated test of underdispersion. In particular, zero values beyond two guide-scale units cannot be called fewer than an expected Gaussian count, or proof of a missing normal tail, without a declared and justified distribution law. The current plan expressly avoids that inference. Keep this distinction in the later decision/report.

The subsequent frozen-table review must verify the actual changed-value count is at most 12, observed cells and order remain unchanged, all scientific bytes/source plans stay fixed, and actual parent source/self feedback is bound. Those future properties cannot yet be established because no replacement table exists. A changed self-check or source discrepancy alone will not establish a scientific improvement. Target release remains locked.

## Reviewed byte bindings

- evidence.json: `e309b9b9aaef0f9a47113da2727c85e3b9a00fccc80ad8be8a783657736d9998`
- model_spec.json: `a355315f8c83c98cd587c82d2847804820939e0298f0cc6bc6347a5fa3eb0323`
- audit/construction.json: `f62b54747f4e4d53eb5f8c0eecd12ac236fdf1e45a15732ca26ab7235ee885cb`
- audit/revision_plan.json: `84ed14985ab52d9fdbceae17489a3b58a938891a52098865f205fb4fe73bc025`
- feedback/initial.json: `c5cd79cf1e0a909e135dff9e160a1cf2020e8d574d8ab56f36e09e31e145c06c`
- feedback/initial_self_current.json: `ec555e5fe3564de195935762c98ab02916ff971cdd779cd942013d8ca5d42a5a`
