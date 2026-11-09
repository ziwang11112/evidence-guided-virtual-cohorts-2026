# Rubric and skill prototype: completed behavioral check

9 November 2026. A project-local experimental skill was created and used by one fresh-context Agent on a fictional planning request. The Agent performed deterministic calculations and proposed source-consistent constructions. No participant data were generated, no clinical case was rerun and no current-versus-new workflow comparison was performed.

## What was built

The [design](../../docs/RUBRIC_SKILL_METHOD_DESIGN_2026-11-09.md) separates task-specific scientific criteria from reusable procedures. The [current skill](../../experimental_skills/analysis-guided-cohort/SKILL.md) points to a concise rubric reference and selectively used procedures for source replay, conditional variation, dependence and repeated measurements. It preserves whole-cohort, enrichment and completion modes and both program and direct-table routes.

This is not a newly installed global skill, a controller upgrade or a new agent hierarchy. Its proposed benefit is to make a concrete construction or retrieval decision depend on the requested analysis and actual evidence. It does not give arbitrary rubric scores the meaning of biomedical validity.

## Forward-test result

The [packet](fixture/SOURCE_PACKET.json) supplies hypothetical standardized variables A, B and C, their moments and a candidate Gaussian law. Both marginal A–B correlation and A–B correlation after residualizing on C are visible requests.

| Information condition | Actual Agent decision |
|---|---|
| Only A–B correlation is provided | Retain that marginal relationship; identify the adjusted relationship as dependent on the candidate's additional independence assumption. Show two admissible laws with different adjusted relationships. |
| Univariate normal marginal distributions are also provided | Correctly retain the same unresolved adjusted use: additional marginal shape information does not identify the missing joint dependence. |
| Matching correlations of A and B with C are provided | Revise the covariance structure. Preserve marginal correlation 0.3 while calculating the now-identified residual correlation as -0.09375. |

The Agent independently chose a 0.7-correlation sensitivity example for the first two conditions, without using the later 0.6 values as evidence for those conditions. It explicitly kept scenario choices separate from source-supported relationships and did not claim to recover the full joint population law. The [actual response](forward_test/RESPONSE.md), [executed calculation script](forward_test/calculate.py) and [calculation output](forward_test/calculations.json) are retained.

Root independently recomputed covariance Schur complements, determinants and eigenvalues rather than rerunning the author's Fraction calculations. Fifteen numerical comparisons agreed within 1.12e-16 and all three matrices were positive definite. The [adjudication](ADJUDICATION.json) records the six predeclared behavioral criteria and the limited assessment scope.

## What this does and does not establish

One Agent could use the skill to distinguish an identified analysis from an assumption-dependent one, avoid an unhelpful revision when evidence was irrelevant, and use informative joint evidence correctly. These behaviors are relevant to the real lipid diagnosis.

There is no baseline arm, no skill-effect estimate, no generated-table quality result and no biomedical validation. The example does not show that an ordinary Agent would fail. Dispersion and longitudinal procedures were not behaviorally tested. Fresh context and instructions did not create a technical filesystem sandbox.

## Independent review and narrow correction

Independent review found that the first procedure wording could prohibit legitimate calibration against a reference scale that the user explicitly supplied. The current wording now distinguishes authorized calibration from independent/evaluation-only references. This preserves the user's option to provide real statistics for construction.

The tested skill bytes were archived before that correction: [archive map](TESTED_VERSION_ARCHIVE.json) and [original design lock](DESIGN_LOCK.json). The dependence-only forward test used the archived version. The correction was reviewed and format-validated, but this same run is not relabeled as testing the changed bytes. The proposed three-condition comparison was also clarified to evaluate supplied-rubric guidance, not autonomous rubric induction.

## Decision

Retain the prototype for a bounded development comparison. Do not replace the frozen method or claim that quality improved. The next question is whether current workflow, rubric-only guidance and rubric plus procedures produce different final-data scientific results under the same evidence and budget. Use existing cases as development, retain all results, and simplify if the additional guidance adds no material value.
