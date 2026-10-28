# Gemini review: adoption decisions and provisional two-review synthesis

Date: 28 October 2026. Status: review and proposed design only. No new experiment was run, no frozen experiment was edited, and no proposed performance threshold is an achieved result. This record combines the complete user-supplied Gemini response with the retained ChatGPT review; Claude's response has not yet been retrieved. Agreement between reviewers is not independent empirical validation.

## Material and inspection boundary

- Complete Gemini response: `GEMINI_REVIEW_USER_SUPPLIED.md`, copied byte-for-byte from the user's attachment; SHA256 `6633bf9e444e77813bf8c934ccc076c9df767e6c563ec786d203186f9debddfb`.
- Detailed independent check: `GEMINI_COMPLETE_CLAIM_CHECKS.md`.
- ChatGPT response: `CHATGPT_REVIEW.md`; earlier checks: `REVIEW_CLAIM_CHECKS.md` and `PRIMARY_SOURCE_CHECKS.md`.
- Experiment snapshot reviewed: private repository commit `51d19b6a8fab07f774d0bd6032a2bb9a379595d8` at https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026.

Gemini reviewed the brief and 13 reproduced source files, not the complete executable repository. Its statement that the private repository is inaccessible outside the local environment overgeneralizes its own access limitation. The complete response supplied by the user supersedes the partial response for content assessment; the partial record remains preserved as a separate retrieval artifact.

## What the first paper would ask

Can an Agent turn heterogeneous published evidence into a target-cohort data generator that supports useful analyses beyond the specific summaries supplied to it, while exposing which conclusions depend on unverified assumptions?

The broad project retains whole-cohort synthesis, entirely unmeasured variable enrichment, and missing-cell completion. Entire-column enrichment is a practical first-paper focus, not a permanent restriction or proof that ordinary statistical approaches cannot apply. Target-only fitted imputers lack observations of that column; evidence-informed statistical generators remain meaningful competitors.

Working title: **Evidence-Guided Virtual Cohort Enrichment: Generating Unmeasured Variables for Biomedical Analysis**. This is a provisional description, not a novelty or publication claim.

## Findings that survive both reviews

1. A capable ordinary Agent already performs consequential work: finding sources, choosing usable evidence, making explicit modeling assumptions and writing a stochastic generator. Fixed constants in the compiled program do not imply the coordinator hand-coded the biological relationships.
2. The extra gap policy has no demonstrated advantage in the completed pilot. Two constructions per arm cannot establish equivalence or universal uselessness. It can be deprioritized while retaining evidence review and revision capabilities.
3. The generated insulin and HDL data preserved broad associations, but more specific age, curvature and interaction behavior was not reliably recovered. Directional agreement on supplied relationships is feasibility evidence, not evidence that arbitrary new analyses are valid.
4. Source statistics need to retain their context. A BMI-bin mean is an average over the people in a bin, not a conditional mean at an assumed midpoint. An adjusted coefficient from one adjustment set is not automatically the coefficient for another population and adjustment set.
5. Repeating residual draws with fixed scientific parameters does not propagate source sampling, model or transport uncertainty. The existing intervals are conditional on the chosen generator; expanding the number of generated rows does not create new empirical evidence.

## Adopt, modify, defer

| Suggestion | Decision | Reason and required evidence |
|---|---|---|
| Reapply source analyses to source-context simulations | Adopt as the next mechanism to test | It directly tests whether the generator actually respects the evidence it claims to encode. If covariate distributions or adjustment variables are unavailable, label approximations and assumptions instead of claiming exact reproduction. |
| Separate shared uncertainty from individual variation | Adopt the architecture; defer inferential claims | Draw a shared model/evidence scenario before individual residuals. Distinguish justified probability distributions from sensitivity ranges. Test any interval rule in a specified repeated-sampling setting. |
| Attach evidence and assumption support to downstream analyses | Adopt descriptive labels | Use source-supported, assumption-dependent and unassessed. A matching predictor list alone does not establish identification in a new population. |
| Add threshold, tail and joint-function analyses | Adopt prospectively | The current HDL primary endpoints mainly probe conditional means. New analyses can test whether the distributional representation is useful. Their eligibility and scoring must be fixed before target results are exposed. |
| Improve access to PDF tables and supplements | Develop if needed by the case | Preserve source screening, provenance, units and footnotes; test extraction accuracy. Installation alone is not a validated capability. |
| Rubin pooling plus an arbitrary effective-sample-size correction | Reject as a universal solution | Different synthesis and imputation regimes require different inferential derivations. A scalar correction cannot fix structural or transport bias. |
| Zero-centered priors automatically prevent unsupported claims | Reject | Prior choices can suppress real relationships as well as unsupported ones. Report sensitivity; do not treat an interval spanning zero as proof of validity. |
| Reuse exposed HDL thresholds as success criteria | Development only | Age and curvature targets chosen after seeing HDL cannot provide fresh confirmation. |
| Treat no-retrieval performance as a contamination test | Modify | This tests incremental retrieval utility in that configuration. A tie or win does not establish memorization. |
| Prospective assays and recruitment savings | Defer | Potentially valuable future validation, but costs, power and savings require an actual design and experiment. |

The statistical caution is consistent with Reiter and Raghunathan (2007), *The multiple adaptations of multiple imputation*: original combining rules do not automatically carry over to all adaptations. [Institutional abstract](https://scholars.duke.edu/publication/742204), [DOI](https://doi.org/10.1198/016214507000000932).

## Corrections that affect the plan

Gemini attributes the weak age effect partly to triglyceride adjustment in Taiwan Table 3. The retained ledgers do not include triglycerides in that adjustment set; triglycerides occur in a separate Dallas source model. Even with the correct covariates, an observational adjusted coefficient does not establish that a causal mediator was blocked. Age clamping and category interpolation are plausible contributors, but no ablation has isolated their contribution.

Its proposed 12/16 interval coverage is a 75% agreement count on correlated endpoints, not evidence of nominal 95% repeated-sampling coverage. Reference cohort estimates are themselves uncertain. Dataset-variable pairs sharing participants are not independent studies. National cohorts are not clean ancestry interventions. Suggested task counts, effect improvements, biological R-squared ceilings, costs and journal thresholds are proposals or unsupported assertions, not established requirements or results.

## Proposed next experiment, with components kept separable

**Development:** use exposed HDL and insulin material to implement and debug a source-statistic checking interface. For each source statistic, retain population restrictions, units, measurement mapping, adjustment set, uncertainty and the computation needed to reproduce it. Let the Agent revise its own generator from these source checks. Do not enter the known target age effect, slope or curvature as a fitting target.

**Mechanism test:** compare ordinary Agent generation with the same Agent plus source-statistic checks, under comparable evidence access and generation budgets. Include a competent statistical generator supplied with equivalent evidence. A separate controlled case with known generating truth can isolate category-mean versus point-mean translation without using a hidden real-cohort answer. Reproducing fitted source summaries is an implementation check, not the final scientific endpoint.

**Independent confirmation:** select and audit a fresh eligible public cohort-variable case before revealing the target column to the generator. Lock the analyses, protocol and stopping rules. Evaluate reserved biomedical analyses for direction, practically meaningful effect categories, nonlinear/subgroup behavior and distribution-sensitive quantities, with uncertainty reported. Numerical error remains a useful diagnostic, but exact equality or patient-level reconstruction is not the goal. Preserve failures and abstentions.

**Uncertainty test:** evaluate outer shared uncertainty separately, using known-truth repeated worlds or a justified resampling design. Compare coverage, width and interval scores for a defined estimand. Do not bundle an unvalidated pooling formula into the source-check experiment and then attribute the outcome to one component.

Independent Agent constructions, source selection and new study families provide stronger replication than more residual seeds. The number of cases and constructions will be fixed by feasibility and precision needs, not copied from a model's asserted publication threshold.

## Decision boundary

Continue if source-context checks improve reserved analytical utility or provide comparable utility with measured reductions in manual effort, without creating unsupported confidence. If improvement only affects summaries directly fitted, the evidence supports constraint reproduction but not broader analytical usefulness. If source operators cannot be constructed without strong unidentified assumptions, record that limitation and test sensitivity rather than silently fill in the missing joint distribution.

The next milestone is a discriminating pilot, not large-scale execution or a publication guarantee. Claude's review may add useful objections, but it will be assessed against code, statistical reasoning and new evidence in the same way.
