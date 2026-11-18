# Adaptive evidence acquisition and analysis-oriented validation

9 November 2026. Decision memo responding to the user's questions about unrestricted paper counts, official medical knowledge, and applying the same analysis to real and virtual data. This is a read-only reassessment of the completed adaptive pilot plus targeted primary-source research. It is not a new experimental result or a modification of a frozen candidate.

## Decision

Continue with the scientific purpose already agreed: an Agent constructs virtual biomedical data that support the user's requested analyses. Expand useful evidence access and make feedback informative; evaluate the resulting data through those analyses. Neither a fixed number of papers nor a perfectly reproduced sample distribution defines success. Revision improvement is an optional mechanism claim, not a prerequisite for demonstrating that the final data have a useful application.

The previous explanation that the 34 unavailable checks chiefly require more conditional evidence was incomplete. There are both interface limitations and scientific information gaps. More searching is potentially useful for the latter; it cannot repair a missing statistical operator by itself.

## 1. What the completed pilot actually establishes

The independent [local audit](LOCAL_CHECK_AUDIT.md) inspected frozen evidence, recipes, semantic sidecars, statistical operators, gateway usage and the final decision. It found:

| Disjoint claim group | Count | Immediate interpretation |
|---|---:|---|
| Geometric means | 6 | Missing operator plus unreported source conventions; a descriptive geometric mean is calculable on positive values. |
| Age medians/quantiles | 6 | Conventional quantiles are calculable; exact source interpolation/weighting is unresolved. |
| Arithmetic means and individual SDs | 10 | Existing operators can calculate them; some source conventions are unknown. |
| Spearman correlations | 6 | A named rank/tie/missingness convention is calculable; it is not an adjusted Pearson relation. |
| Adjusted category effects | 6 | Exact source design and necessary adjustment variables are unavailable; a simpler model estimates a different quantity. |

Thus 28 claim records have ordinary descriptive analogues. They are not 28 newly passed source checks. All 34 frozen recipes declared `not_computable` and null operators, so these were not 34 numerical estimation crashes. Their reasons overlap, and repeated subgroup statistics are not independent evidence.

The author used 3/6 query-budget units and 2/3 downloads, then chose to retain its initial model. The cap was not reached. We cannot infer that removing the cap alone would have yielded better data, or that a further search necessarily would have found suitable conditional evidence.

The implementation currently exposes Europe PMC search and PMC article/supplement acquisition. Reading an arbitrary hospital page, government codebook or publisher PDF is not an already available capability of that experiment's gateway. This should be extended explicitly rather than merely promised in a prompt.

## 2. Give the Agent broader, purposeful access

### Search for an information gap, not a paper quota

The Agent should decide which sources to search and how many are useful. A task-level time/cost/network allowance remains appropriate; a fixed paper count should not be presented as scientific sufficiency. Retrieval cost should be logged, including failed and duplicate requests.

For each proposed search, the Agent should identify the missing fact, the analysis it affects, and what a useful finding could change. Examples include an adjustment set in a supplement, a residual dispersion estimate, a conditional correlation, an assay conversion, a source population's selection criteria, or an official measurement definition. This is a short decision record, not a requirement to expose private reasoning.

The next action can be reading a supplement, following a cited primary study, checking a laboratory manual, calculating under an explicit conventional assumption, comparing plausible structures, revising the model, or stopping. Do not force a new paper or a model change on every round. Stop when the consequential gap is resolved, remaining uncertainty does not change the intended analysis materially, plausible retrieval paths are exhausted, or the task resource limit is reached. Retain unresolved findings when stopping.

### Admit different source types for different purposes

| Material | Appropriate contribution | Interpretation needed |
|---|---|---|
| Original study and supplement | Numeric distributions, adjusted associations, joint statistics, analysis definitions | Population, measurement, adjustment, uncertainty and overlap |
| Government survey/codebook/laboratory manual | Units, assay, eligibility, weights, derived-variable rules, official aggregates | Exact wave/version and measured population |
| Hospital laboratory documentation or clinical guideline | Measurement conventions, diagnostic definitions, validated score bounds, clinical context | A healthy reference interval is not the entire patient distribution |
| Hospital cohort report | Observed clinical distributions and relationships | Referral/selection and treatment can differ from community populations |
| Clinical educational material | Qualitative plausibility and useful search leads | It does not supply an unreported numerical conditional effect |

The NIH/NLM [MedlinePlus explanation](https://medlineplus.gov/lab-tests/how-to-understand-your-lab-results/) explicitly describes population- and laboratory-dependent reference ranges. In our design, those ranges would be contextual knowledge, not automatic clipping limits or a substitute for an individual SD. Our inference: an authoritative institution makes a source worth considering but does not make every statistic applicable to a new target population.

A new web/PDF ingestion adapter should preserve origin, version/date, source location, the actual extracted statement, measurement/population context and its assigned role. Separate observed evidence, algebraic derivation and model assumption. An official-source label must not silently promote an assumption to a measured relationship.

The [official-knowledge review](OFFICIAL_KNOWLEDGE.md) documents Synthea's use of public medical knowledge and a directly relevant 2026 LLM-assisted extension. It is useful implementation precedent for our next design. Its distinction between satisfying model requirements and validating generated populations reinforces the need to test final-data analysis utility rather than rely on an Agent's rubric score alone.

## 3. Make checking more informative without changing historical results

Retain the old strict verdict. Add a separate diagnostic with three fields:

1. **Calculation:** was a specified statistic computed successfully, on which rows and with which convention?
2. **Definition match:** verified source definition, explicit conventional assumption, or known different estimand?
3. **Applicability:** source-context replay, target-data plausibility comparison, or a declared transport scenario?

The immediate useful addition is a geometric-mean operator, with positivity and unit handling verified. Existing mean, SD, quantile and Spearman operators should be available for assumption-labelled descriptive comparisons. Only add categorical-regression support for a fully specified requested contrast; do not call a continuous slope a category effect or fabricate absent source covariates.

Feedback should explain what can change: extraction, units, the calculation, population assumptions, model structure or stochastic variation. A source match is useful construction feedback. It is not automatically a target-validity certificate. A metadata uncertainty should not suppress every ordinary descriptive calculation.

## 4. Use scientific analysis utility as the main evaluation

The user's proposed comparison is appropriate: execute the same requested analysis on real and virtual data, then examine whether the results support similar scientific interpretation. It is established practice. The [primary-paper notes](PUBLISHED_VALIDATION_PATTERNS.md) cover SynthIPD, Filshtein, SynthCraft and an AML study, including their different input-access conditions. They are representative examples, not a systematic review.

Two additional primary examples directly support this evaluation choice:

- [Reiner Benaim et al., JMIR Medical Informatics, 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7059086/): five hospital studies repeated clinical analyses on original and synthetic records, comparing proportions, odds ratios, hazard ratios, survival curves and intervals. Five synthetic repetitions were used for the main comparison, and 1,000 repetitions for selected bias/stability analyses. This generator used original hospital data; it was not literature-only synthesis.
- [On the fidelity versus privacy and utility trade-off of synthetic patient data, 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12059695/): predictive models trained on synthetic records were tested on a held-out 20% of real records. Ten same-size synthesis repetitions assessed variability; classification used AUC and survival prediction used C-index. Utility differed across datasets, illustrating why marginal similarity alone is insufficient.

Our proposed evaluation should therefore have a small set of substantive primary analyses, supported by diagnostic plots. For current clinical/phenotype tables, these may be adjusted associations, nonlinear exposure-response curves and subgroup or joint relationships. Gene-expression differential analysis or pathway enrichment belongs to a genuine omics task with appropriate generated measurements; it should not be added decoratively to clinical tables.

### What to compare

| Intended use | Same analysis on both data sources | Main evidence of usefulness |
|---|---|---|
| Association estimation | Same formula, transformations and adjustment set | Direction, effect magnitude in scientific units, uncertainty and interpretive stability |
| Nonlinear or subgroup analysis | Same basis/contrasts, eligibility and adjustment | Curve shape over supported ranges; subgroup contrasts and their precision |
| Longitudinal/survival analysis, when suitable data exist | Same time origin, event/censoring or repeated-measure model | Time pattern, survival/RMST or interaction effects |
| Prediction, when it is a requested use | Synthetic-trained versus real-trained models on the same untouched real test set | Discrimination, calibration and relevant subgroup performance |

Do not require a source paper to report every future query. Conversely, do not accept one coincidentally matching coefficient as proof that the entire table is useful. Include analyses central to the user's purpose and enough related checks to detect an incorrect joint structure. Repeated draws assess whether a result is stable under that generator, not whether the biomedical model is true.

### Define closeness in the right context

The real sample is a reference estimate, not known population truth. Where raw reference data and sampling design are available, use size- and design-matched real-versus-real splits or appropriate resampling to display ordinary sample variability. The same effect estimates can then be shown for real-versus-virtual comparisons. This is context, not an automatic pass threshold, and within-cohort resampling does not establish cross-population transport.

Align eligibility, units, missingness, sample size and adjustment before interpreting a difference. A more heterogeneous or differently selected population may appropriately have a different result. Separate such population differences from a failure to generate the requested target population.

When a justified practical tolerance exists, define it before examining the comparison. Otherwise report agreement descriptively in meaningful units. Matching signs, overlapping intervals or a nonsignificant difference alone does not establish equivalence. Many more synthetic rows reduce Monte Carlo error; they do not add independent clinical observations or remove uncertainty in source estimates and model assumptions.

### Let the Agent know the research question

The research question, estimator and desired output schema may be fully visible. The Agent may dynamically tailor a generator to a different user request. When one dataset is advertised for several uses, evaluate that dataset on those uses; when a new task triggers a new generator, assess task-conditioned construction explicitly. Neither requires hiding the question itself.

Real-reference information can also be used, provided its role is recorded:

- A supplied distribution/effect or a disclosed evaluation result is calibration information; matching it establishes consistency with that information.
- A comparison never used in construction/selection tests additional analytical usefulness.
- An independent population tests transfer when the populations and analysis question are meaningfully related.

These are legitimate experimental conditions rather than a blanket prohibition on useful inputs. Keep their results separate. The already disclosed pilot remains development evidence; new independent-validation claims need a suitable untouched reference.

## 5. Focus the next implementation and experiment

1. Add assumption-labelled descriptive feedback and the geometric-mean calculation in a new version. Test actual mathematical/semantic behavior; retain old frozen receipts unchanged.
2. Add an evidence ingestion route for relevant official pages, primary publisher material and PDFs, with the same provenance and information-role recording. Replace paper-count-driven prompting with question-driven retrieval and a task resource budget.
3. Use an existing admitted clinical case for a development run with a small prespecified panel of meaningful analyses. Let the Agent select evidence, scientific structure, parameters and useful next actions. Do not prescribe the desired signs or coefficients.
4. Compare final-data analysis utility, source-supported diagnostics, unresolved assumptions and actual retrieval cost. Reuse a suitable existing frozen comparison when available; do not make broad superiority over every statistical generator a prerequisite for demonstrating an application.

This turn did not implement these changes, regenerate data, read new patient tables, tune to disclosed results, or update the public repository. The new artifacts are this memo and independent research/audit notes. Their purpose is to make the next improvement concrete and preserve the distinction between a proposal and demonstrated performance.
