# Source-specific association replay before another target comparison

Design decision, 9 November 2026. This specifies a bounded follow-on; it is not an executed experiment or a claim of improved generated data. The current evidence-audit unit ends after independent review and publication of its findings.

## Scientific question

Can the Agent turn verified continuous association evidence into a generator whose source-population projections match the meaning of the evidence, while honestly exposing uncertainty in the requested target-population analyses?

The product remains an analyzable virtual cohort, including full generation without individual input. The question is not whether a manually inserted coefficient can be reproduced, or whether feedback must improve every candidate. The Agent chooses the structural model, nuisance distribution, parameterization and whether a revision is warranted.

## Evidence selection, made without target results

Use Soares2019 Table3 as the primary association source family: its adult rural/urban and sex strata are broader than the selected middle-aged urban comparison in Soares2020. Keep all eight TC/HDL BMI coefficients and their printed CIs, not a favorable subset. Soares2020 S7 remains a related-source consistency and reporting check, not independent precision or replication. Preserve the unresolved BMI-standardization reference and differing analysis denominators.

Liu2023 FigureS1 supplies authentic joint partial correlations in a different adult population. It may inform a separately labelled structural sensitivity analysis. It is not an African covariance target. Keep its extra batch adjustment, common-row assumption, uncertain exact n and absent sampling CI. Do not merge its entries and the Malawi coefficients into one supposed empirical covariance matrix.

Agongo, Greiner, categorical associations and rank correlations remain available under their actual labels. No automatic raw/log, Spearman/Pearson, category/continuous, or extra-covariate/age-sex-only conversion is allowed. An Agent may propose a conversion with visible mathematical assumptions, which receives an assumption-dependent label.

## Minimal implementation change

The next unfrozen controller should give each evidence item three separate fields:

1. `reported_operator`: what the paper computed, with strata, units, transformations, covariates and uncertainty.
2. `replay_contract`: the declared source-law sampling, selection, standardization and estimation procedure. Each unreported convention is marked, not silently filled.
3. `target_use_mapping`: which requested analysis it can inform, with exact, derived, assumption-dependent or context-only status.

Retain semantic_feedback_v1 and the existing analysis-use checks. Do not alter old frozen bundles. A numeric result can be computed under declared assumptions without receiving an exact-source or clinically validated label. The Agent can decide that an operator is not replayable and explain why; unavailable is not zero error or a failed biological effect.

## Source replay contract

For the primary source, generate a separate source-law sample with the variables required by its published model. Apply its eligible adult and sex/site strata. Fit each lipid in mmol/L against standardized BMI and the stated source adjustment variables. The exact covariate list and coefficients come from association_inventory.json; they are not invented in the controller.

The source does not fully resolve the BMI SD reference population. The Agent must choose and declare a reference rule grounded in the available study structure, label any unpublished convention as an assumption, and expose at least one relevant alternative if it materially changes the comparison. The paper need not establish a uniquely correct unpublished implementation for an assumption-dependent replay to proceed. A source SD taken from a different descriptive denominator is approximate, not an exact conversion. No target BMI SD, target lipid SD or old target coefficient may fill this gap.

If source-only nuisance variables or their joint distribution lack evidence, the Agent may propose a stochastic nuisance model. Those variables are model assumptions, not recovered measurements. The requested target-output columns need not include every source nuisance variable. Omitting nuisance variables and relabelling an age/sex model as the full source regression is not acceptable. Source-like and target-like sampling must remain distinguishable in code and logs.

The published coefficient CIs describe estimation uncertainty; they do not provide person-level noise SDs or a joint multivariate likelihood. Compare point discrepancies and source intervals descriptively, retaining dependence and overlap. Do not manufacture an acceptance threshold or interpret CI overlap as equivalence. Residual covariance and dispersion remain modelled or sensitivity quantities unless additional compatible evidence establishes them.

Before execution, the Agent must declare how the source and target laws are linked: shared parameters, population-specific parameters, measurement mappings, and any distributional transport assumptions. Independent fitted source generators with no explicit link to the target generator do not establish evidence use in target generation. The link may be hierarchical, conditional, mechanistic or another valid construction; its unsupported parts remain assumptions rather than enforced equality between populations.

For Liu, replay the three reported pairwise residual correlations under one declared age/sex/batch design and common sample. The derived BMI-adjusted correlation is a redundant algebraic check, not a fourth independent datum. Rounding bounds are not sampling CIs. A model that does not represent the source batch process can only perform a labelled approximation, not an exact replay.

## Agent information and freedom

Use a fresh scientific construction context. Provide approved original sources/metadata, the desired analyses, evidence gaps and this contract. Do not provide old candidates, old target values, generated outcomes, or a desired coefficient/sign. The printed source numbers remain legitimate inputs. The Agent may select any valid generator family, use auxiliary variables, revise assumptions or decline an unsupported use. The host does not hand-fill a slope, intercept, SD or correlation.

Retrieval is allowed for a concrete missing source definition. Avoid another general literature sweep. At most five further definition-discovery requests are available within the parent 24-request envelope, counting the present 18 successful requests and one failed connector attempt. Saved original-source transport remains within the parent 100 MiB ceiling, including the present audit. Record metered HTTP response bodies separately from unmetered browsing. Stop earlier when retrieval resolves the missing item or complementary original-source follow-up supplies no new executable information. Official clinical material can clarify definitions and measurement, but reference ranges cannot identify a population covariance.

## Bounded execution proposal

- One independent scientific construction, initial plus at most one source-feedback revision. A no-change decision is a valid recorded outcome.
- Three predeclared seeds per stage; at most six final target-like tables, each at most 3,000 rows, across all parameter/nuisance/transport alternatives combined. Register seeds and source-replay sample sizes before first execution. Source-law sampling is capped at 24 evaluations of at most 10,000 rows each, including calibration, diagnostics, sensitivity and final replay across both stages. All calibration objective evaluations, analytic or simulated, have an additional total ceiling of 200 across both stages. Count discarded attempts and optimizer-internal calls. Log these counts separately; they are numerical evaluations, never independent clinical cohorts. No unlogged inner loops. Further sensitivity must be analytic or source-law-only within these same ceilings.
- Freeze the initial construction and mappings before initial execution. The single revision may see source diagnostics and structural/coherence checks, but no target-reference values or requested target-use analysis results. Freeze the revision (or no-change declaration) before releasing the requested-use results for either stage. Then run the same three existing requested analyses on every final table. Include all outputs and uncertainty/assumption labels.
- A post-freeze coding defect is recorded as a repair with the same predeclared protocol, never as an unlogged scientific revision. Clinical coefficients/signs are not repair criteria; failed/unavailable outputs and no-change decisions stay in the record.
- Compare initial/revised source consistency and requested-use sensitivity. Neither is a new clinical validation. No old target is reopened to tune or select a candidate.
- If no defensible source replay contract can be implemented, stop before table generation and report the unresolved items. Do not simplify the published model silently to obtain a numerical pass.
- A later new-reference test requires a separate, explicitly recorded unexposed reference protocol; it is not included here.

## What would change our judgment

Useful progress is a functioning, auditable source-law replay that genuinely uses the continuous evidence and produces analysable target-like data, with remaining transfer sensitivity quantified. Failure is useful if it locates an unreported scale, nuisance distribution or joint relation that prevents that use. Lower source discrepancy alone does not demonstrate better target data, and generating more rows does not reduce missing-evidence uncertainty.

This is a source-consistency exploration, not a mandatory additional multi-agent framework, a mechanism-superiority claim, or a replacement for the paper's scientific-utility evaluation.
