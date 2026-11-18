# v0.28 integration and bounded next experiment

Completed locally on 10 November 2026. This is an editorial/attribution integration, not a new clinical experiment.

## Delivered

- [Manuscript v0.28](../../manuscript/DRAFT_v0_28.md), [48-page reading PDF](../../manuscript/methods_draft_v28_2026-11-10/paper.pdf), and [independently compiled Overleaf ZIP](../../manuscript/methods_draft_v28_2026-11-10/overleaf_v28.zip).
- Completed PNS validation integrated in main results and S18, with all five authors, fifteen draws, reference uncertainty and exposure limits.
- Thirty-construction attribution integrated in Methods, Results and S19; 90 requested-analysis entries plus six dispersion entries are audit records, not 96 independent experiments.
- Two new vector figures: model implications versus sampled analyses; complete blood-pressure comparisons. All eleven older figure assets remain unchanged.
- [Twelve-slot cross-provider protocol](CROSS_MODEL_PILOT.md), not launched. It does not presume that fresh host contexts are different model families.

## What the integration supports

The Agent can author an executable joint model from incomplete published evidence and make the completion assumptions inspectable. Particular model operations can explain particular scientific results: the iron independent-redraw step changes the model odds ratio, and lipid L03's weak residual dependence is already implied by its joint law. Target agreement remains analysis-specific. The PNS task adds whole-cohort evidence and a clear coexistence of closer SBP slopes, higher DBP slopes and lower residual dependence.

The audit does not show that all errors are transport errors, all variances contract, or provenance categories predict accuracy. The Q2 ENSANUT counterexample concerns the age/sex-adjusted BMI coefficient before additional glucose adjustment. Unknown exact historical model identities remain unknown; same-host author consistency is not cross-provider confirmation. Source checks that could not execute are not counted as successful checks.

## Verification and corrections

[Independent content review](INDEPENDENT_REVIEW.md) checks aggregate values, estimands, original source records and preservation. All 38 existing references and eleven figures remain; thirteen old table blocks are byte-equivalent, while Tables 4 and 5 only receive PNS rows. One new table provides all PNS author medians. Three clarifications from review were applied and rechecked against the final source hash. Review independence is limited by the reviewer having contributed to the prior PNS attribution audit; this is not independent patient-level validation.

[Build QA](../../manuscript/methods_draft_v28_2026-11-10/BUILD_QA.json) verifies 13 figures, 16 tables, unchanged v0.27, matching standalone ZIP text/links, and no overfull or missing-character errors. Final visual checks covered all contact sheets and the new results pages. A one-line near-empty page was fixed by removing a forced supplement break. Final length is 20 main pages and 48 total. This is a reading edition; author/declaration details and target-venue formatting remain pending.

## Cost and next decision

No new patient-level or generated rows were read, no scientific generator executed, no target analysis refitted, no new data downloaded, and no paid API or model-provider session launched. Work consisted of existing-aggregate plotting, document integration, compilation and review.

The next bounded unit is to stage two identical fixed case payloads and verify actual provider/model identities and transcript capture, then run 12 fresh constructions under the protocol. These are historical exposed cases used for developmental comparison, not new independent clinical validation. No new agent architecture or large-scale campaign is justified by this manuscript revision alone. Public GitHub synchronization has not occurred in this unit.
