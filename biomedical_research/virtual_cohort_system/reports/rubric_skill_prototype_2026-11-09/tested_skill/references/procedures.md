# Procedures to load when a finding requires action

Use the procedures that address the current request. Do not run the whole menu by default. Keep models and parameters under the scientific author's control; use only tools actually supplied by the task.

## Source definition and replay

Compare the requested statistic with the original source's population, variable roles, units, transformations, selection, adjustment, weighting and uncertainty type. Re-read the needed table/method or supplement when the definition is ambiguous. A transformation must be recorded as a derivation, not silently substituted into the original report.

If all necessary source-context inputs are present, call the matching supported estimator on an appropriate replay. If only the operator is missing, propose its implementation and independent check. If source covariates, weights or definitions are missing, implementing a weighted or adjusted estimator alone cannot make replay valid. Return that precise missing input, and retrieve it or retain the qualification. Own-law moments are useful but are not source-population replay.

## Conditional variation

Use this procedure when the analysis depends on residual scale, heterogeneous spread, tails or sample-size planning. Determine whether each reported scale is individual SD, estimator SE, an interval, a quantile or a residual scale. Transform an SE to an individual SD only when the stated sampling/estimator assumptions justify the conversion; clustered, weighted or adjusted estimates require their own design information.

Separate variation explained by covariates from remaining within-person/group variation. Check the law of total variance or an appropriate numerical decomposition rather than using a marginal SD as an unexplained residual SD. A mean plus one quantile does not identify variance without a shape assumption. If using a shape assumption, show which requested analyses depend on it.

Use residual or subgroup distributional evidence when available. When absent, seek compatible evidence or offer justified sensitivity scenarios. Do not enlarge noise solely because a known target is more dispersed, and do not interpret more synthetic rows as more information about the evidence.

## Joint and conditional relationships

Use this procedure for adjusted associations, joint thresholds, interactions and multivariable uses. Keep marginal versus conditional, rank versus Pearson correlation, standardized versus raw coefficients, and binary versus continuous outcomes distinct. A regression coefficient cannot generally be substituted for a correlation or vice versa without the required moments and design.

Check whether the proposed joint law simultaneously preserves the adopted constraints. For covariance-based models check admissibility; for other families use the relevant dependence and support checks. Recompute the requested adjusted analysis and any constraints likely to change with the revision. An unreported relationship is not automatically zero. If marginal evidence leaves dependence unidentified, choose an explicit scenario or compare a small justified set, rather than asserting that the joint relationship was reconstructed.

## Repeated measurements

Use this procedure when the task involves trajectories, paired changes or longitudinal analyses. Represent subject identity, visit/time definition, selection and the intended repeated-measure estimator. Separate between-subject heterogeneity from within-subject residual variation. Marginal means at several visits do not identify paired-change variation or temporal dependence. If a published mixed model is supplied, check all specified components and the intended estimator; finite-draw interaction signs or p-values are not forced to match a point estimate.

## Hypothesis-dependent generation

When admitted evidence permits several substantively different joint constructions, keep the missing quantity explicit and choose alternatives justified by the scientific question. Their between-model variation is sensitivity to assumptions unless a probability model for weighting them is supported. Do not average incompatible datasets and call the mixture validated. If the user's requested analysis changes, adapt the rubric and construction prospectively and retain the old version.

## Output-level checks and revision

Execute the user's analysis on generated data through the approved route and compare it under the criterion's stated reference role. Examine relevant effect magnitude, direction, distribution and subgroup behavior, not only significance or a single similarity statistic. Sample uncertainty and generator Monte Carlo variation can explain some disagreement, but neither should be presumed to explain every mismatch.

Revisions should follow a specific diagnosed issue. A corrected unit, valid new constraint or changed assumption must be visible in the new artifact. Recheck affected strengths. If no permitted action would resolve an important gap, keep the generated data as explicitly exploratory or report the restricted use; further debate is optional, not a required step.
