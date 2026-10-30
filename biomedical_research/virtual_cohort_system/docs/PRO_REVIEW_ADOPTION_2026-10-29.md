# PRO review: verification, adoption and next decision

Prepared 29 October 2026, local workspace time, after the user supplied a review of M10. This document evaluates advice; it does not report a new experiment or alter frozen results.

## Decision

Adopt the review's main focus: **translate study-specific published evidence into reusable generators for entirely unmeasured target biomarkers, and validate the scientific analyses supported by the generated data**. Keep an ordinary capable Agent as a valid implementation. Keep evidence and assumption dependence as a supporting contribution, not a separate quality-classification project.

The review strengthens the argument for a focused next experiment. It does not establish novelty. Source-statistic replay, aggregate-data synthesis and target-population transport have substantial predecessors. We still need to identify what our implementation adds and measure it.

Working title: **Evidence-Guided Enrichment of Unmeasured Biomarkers for Reusable Biomedical Analysis**.

## Review provenance and our inspection boundary

The supplied text is preserved byte-for-byte at [the review transcript](reviews/pro_response_after_m10_2026-10-29.txt), SHA-256 `055c7073518501332ccfe46dcebc4217b680ca9f675e344f9703c60686bfac3f`.

The reviewer reports reading the private repository at commit `d33d0cbad4c199fe5b450688fe8050d72afd9861`, including four constructions and targeted evaluation code, without rerunning participant data. That is the reviewer's access statement; this turn does not independently authenticate its remote browsing history.

We independently checked the material implementation claims against local frozen specifications and generator code. A separate read-only Agent audited the four constructions. No participant/reference tables were read for this review, no generators were run, and no new target outcomes were inspected. Published sources below were checked selectively, with access limits stated.

## 1. Findings that survive the code audit

### HbA1c: evidence and assumptions must receive separate credit

The SHIP-Trend sex-specific age coefficients enter both models as 0.0153 and 0.0191 percentage points per year. The successful target age association therefore gives a useful, limited transfer example.

The BMI effects have different provenance:

- Construction A uses `0.18 * tanh((BMI - 27) / 7.5)`.
- Construction B uses `0.02 * (BMI - 27)`.
- Both specifications identify these BMI effects as assumptions rather than quantities determined by admitted evidence.

See [A specification](../reports/analysis_utility_feasibility_2026-10-30/constructions/ha/selected/model_spec.json) and [B specification](../reports/analysis_utility_feasibility_2026-10-30/constructions/hb/selected/model_spec.json).

Consequently, positive generated BMI associations do not establish that the Agent extracted this relationship from the source papers. They support the usefulness of these evidence-plus-assumption constructions in the tested target. Future results should distinguish directly reported evidence, numerical consequences of evidence under assumptions, and additional assumed relationships. The last two categories must not become retrospectively evidence-derived after target evaluation.

### Insulin: a structural explanation is supported, but not a complete causal attribution

Both generators use a common BMI response across sexes on the modeled log-insulin scale. A's sex offset is zero; B uses an assumed female log offset of 0.08. Neither directly expresses a sex-dependent BMI function on that scale. See [A generator](../reports/analysis_utility_feasibility_2026-10-30/constructions/ia/selected/generator.py) and [B generator](../reports/analysis_utility_feasibility_2026-10-30/constructions/ib/selected/generator.py).

This helps explain the strongly attenuated target sex-by-BMI estimate. It does not prove the full cause: a common nonlinear function, different covariate distributions and projection onto an analysis model can produce a nonzero interaction estimate. B's log offset also produces multiplicative raw-scale differences. The modeled scale and evaluation scale matter.

Do not fix the new model by copying the revealed M10 interaction coefficient. M10 is now development evidence.

### Marginal summaries are not automatically conditional parameters

Both HbA1c constructions place source sex-specific marginal medians at assumed reference covariates age 49.5 and BMI 27. This conversion is explicitly declared. A uses approximate independent source covariates; B uses a balanced independent age–BMI lattice.

The review correctly says that marginal medians need not equal the conditional locations at those reference values. It has not demonstrated that every such anchor is wrong or that correcting it will improve the target. This is a scientific approximation to test, not a confirmed implementation bug.

Source checks currently test compatibility with these reconstructed source distributions. They do not establish compatibility with the unavailable original joint covariate distribution.

## 2. Literature checks that affect the contribution

| Source | What was checked | Consequence |
|---|---|---|
| [Jones et al., PLOS ONE 2026](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0341704) | Primary full-text sections describe sample-free LLM population synthesis from aggregates and evaluation of unconstrained joint tabulations, including section 5.3. | Neither aggregate-to-rows generation nor checking unprovided joint relationships is sufficient as a firstness claim. Its household/demographic task differs from biomarker enrichment, which is a possible scope distinction rather than proof of novelty. |
| [Jones correction, August 2026](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0356492) | Figure 10 was corrected: a preliminary experiment figure had appeared instead of the intended 20-run figure. | Use the corrected repeat-run figure if discussing that evidence; the correction does not erase the methodological overlap. |
| [ML-NMR, 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7362893/) | Individual models are integrated over source covariates to form aggregate likelihoods; the paper handles target populations and missing source correlations under explicit assumptions. | Population-specific statistical operators have clear statistical ancestry. Our formula or replay loop alone is not a new statistical principle. |
| [Statistical matching using fractional imputation, section 2](https://www150.statcan.gc.ca/n1/pub/12-001-x/2016001/article/14539/02-eng.htm) | The primary article shows how conditional-independence imputation constrains unobserved cross-variable relationships, including an adjusted coefficient estimated as zero under its setup. | Generating a new variable from X alone does not justify arbitrary later analyses involving another variable whose residual relationship was not modeled. |
| [SASC, Patterns 2022](https://pubmed.ncbi.nlm.nih.gov/35156066/) | Publication and summary-based cohort generation confirmed through indexed primary-paper records. PMC full text returned a browser challenge and the publisher page returned 403 in this turn. | Keep it as a close predecessor; do not claim its complete correlation-calibration procedure was re-audited in this turn. |

G-Sim, SynthCraft and STEAM remain relevant from the preceding [contribution brief](CONTRIBUTION_FOCUS_AND_PRO_REVIEW_2026-10-29.md). AMSIPD and SynDI were not newly rechecked here. No exhaustive novelty conclusion is claimed.

## 3. Adoption decisions

| Review recommendation | Decision | Qualification |
|---|---|---|
| Center the paper on study-conditioned evidence entering a target generator | Adopt | Specify a concrete operation and test it; listing metadata is insufficient |
| Separate evidence-derived success from assumed success | Adopt immediately | Change interpretation and prospective records, not historical data or frozen specifications |
| Use A/B evidence addition and same-evidence C | Adopt as a staged design | A/B tests information use; C tests a particular method claim only after C and B are concretely defined |
| Use one primary analysis, one reuse analysis and one preservation check | Adopt | Same frozen generator and declared analysis families; exact target answers remain hidden |
| Preserve assumption dependence | Adopt | Vary consequential source-X and structural alternatives, not just residual seeds |
| Postpone more agents, interfaces and scale | Adopt | The present bottleneck is a scientific conversion, not compute capacity |
| Similar performance to C implies only an application/software paper | Qualify | Comparable quality with measured reductions in expert intervention, fewer translation errors or wider evidence support can support a computational methods contribution; none of those benefits has yet been measured |
| B beating C proves study-context handling is responsible | Qualify | Model family, source reconstruction, search budget and parameter fitting may also differ. Attribution needs matched diagnostic checks |

An ordinary Agent can implement B. C should receive the same admissible evidence, units, transformations, adjustment information and source-reconstruction information. It must be an appropriate statistical alternative, not an intentionally context-blind straw man. Conversely, giving C extra true source/target outcomes would test a different information setting.

## 4. The first implementation question to resolve

Choose one scientific conversion with a clear correctness condition: **translate source marginal location statistics into conditional generator locations under explicit source-population assumptions**.

A simple illustrative mean model explains the issue. If `E[Y | X] = alpha + beta * X`, then a source mean satisfies `mean_source(Y) = alpha + beta * mean_source(X)`. A source population mean cannot simply be inserted as `alpha`. Medians with skewed residuals or nonlinear responses generally require evaluating the mixture distribution rather than applying that mean identity. This example is explanatory algebra, not a new algorithm or experiment result.

The reusable operation should be:

1. Read a published statistic together with its subgroup, scale, adjustment and measurement definition.
2. Build the corresponding executable analysis operation on generator outputs.
3. Represent source covariates from reported information. Where the joint distribution is unavailable, declare and vary plausible alternatives instead of pretending one reconstruction is known.
4. Numerically calibrate candidate parameters to the source statistics under each declared source scenario. Preserve unresolved/incompatible statistics and avoid arbitrary success tolerances.
5. Keep individual residual variation separate from uncertainty about source reconstruction, model structure and transport.
6. Freeze the generator and evaluate it on target covariates; use the same output for all declared analyses.

The Agent's useful role is interpreting the statistics, selecting justified candidate structures and identifying missing assumptions. Deterministic numerical code should implement and check the chosen operations. This division is compatible with an ordinary Agent; merely adding it does not establish novelty.

Calibration to guessed source X can fit an invented population very well and still transport badly. Correct implementation of an operator is therefore necessary but insufficient. Multiple published summaries can also be correlated or share participants; a fit objective must not silently treat all of them as independent likelihood evidence. Incomplete evidence may leave several distinct generators compatible with the same summaries.

Before evaluating biological targets, validate any new operator against invented known-distribution examples as software correctness checks. These checks establish that the conversion is implemented correctly, not biomedical utility or novelty. No such new checks or implementation were run in this review turn.

## 5. A bounded next experiment

### First gate: usable evidence and a fresh task

Find a genuine external joint statistic that can constrain the chosen relation and enough source-population information to make the operator meaningful. Audit study overlap and past project exposure before reserving a target. If the evidence cannot identify the intended parameter, preserve alternatives or choose another task; do not obtain the answer from the target.

The marginal-location conversion can be tested using location/distribution and subgroup analyses. If the intended primary outcome is a slope or interaction, evidence must constrain that relation. An intercept-only correction cannot be expected to repair a missing sex-dependent slope. Do not conflate these separate mechanisms in the pilot.

### Experimental conditions

| Condition | Evidence | Method | Main contrast |
|---|---|---|---|
| A | Basic packet E0 | Candidate method | Starting point |
| B | E0 plus eligible joint evidence | Same candidate method | B–A: use of added information |
| C | Same as B | Appropriate conventional calibration, with compatible context handling | B–C: chosen method or automation contribution |

C is a planned reference rather than a fixed named algorithm at this stage. If B and C implement the same numerical operation and model class, similar output is expected; the question then concerns translation reliability or effort, not a nonexistent numerical advantage. If different model classes are used, do not attribute a performance difference solely to evidence semantics.

Two independent constructions per Agent condition, each with three residual seeds, remain a small feasibility budget. Repeated draws for a deterministic statistical construction do not create independent method-design replications. No across-task superiority claim can rest on this pilot.

### Three outcomes, one freeze

1. Primary: the target relation or quantity constrained by the newly added source evidence.
2. Reuse: a scientifically meaningful analysis not directly used for calibration.
3. Preservation: a basic relationship that should not materially deteriorate.

Define each estimator, scale, reference uncertainty treatment and useful tolerance before target release. Direction remains central when it is the scientific question; effect scale and shape prevent a tiny or grossly distorted effect from counting as equivalent. A weak real reference permits an inconclusive result. Do not invent a universal percentage tolerance or force every endpoint into a sign score.

Evaluate all retained constructions, source scenarios and prespecified analyses. A new condition prompted by a revealed target belongs to development and needs new confirmation.

### Interpretation and stopping

- B improves over A with a traceable scientific change: useful evidence addition. Confirm independently before broad claims.
- B and C are comparable: no new statistical accuracy advantage demonstrated. Measure a specific automation benefit if that is the proposed contribution; otherwise use an application/workflow framing.
- B improves over C: check modeling and compute differences, then confirm independently; a single win does not establish the reason.
- Source fit improves but target analyses do not: inspect source reconstruction, transport and identifiability. Do not fix the target answer by hand.
- A corrected intercept improves location but not a missing interaction: this is consistent with the limited mechanism, not necessarily an implementation failure.
- No credible useful improvement across well-specified independent tasks: stop the method-advantage claim rather than multiplying cosmetic variants.

## 6. Scope after this review

Keep the data-generation direction and the user emphasis on downstream scientific conclusions. Do not make special-Agent superiority a prerequisite. Do not claim causal discovery, individual laboratory recovery or replacement of patient measurement.

The next authorized proposal should specify the exact conversion, admissible evidence, fresh data, three analysis questions and comparison conditions. This turn completes the review and decision record; it does not launch a larger campaign, modify the frozen generators, or claim that the planned mechanism already works.
