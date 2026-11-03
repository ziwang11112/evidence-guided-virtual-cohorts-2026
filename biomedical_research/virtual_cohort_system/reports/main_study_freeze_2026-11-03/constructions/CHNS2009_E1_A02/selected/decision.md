# Initial construction decision — CHNS2009_E1_A02

I chose an affine biomarker model with independent age/sex and explicit residual
dependence, a positive gamma BMI innovation, and an upper metabolic component.
The two Jansen coefficients constrain their own separate age/sex-adjusted source
projections. An assumed residual BMI/glucose correlation then selects joint
response coefficients; it is not inferred from those publications. The selected
source scenario has FPG below 7 without clipping target rows.

The target is broader than Jansen's selected western-European cohort. Bao
medians provide ordinary-component locations, and a MIND BMI dispersion informs
one explicit target scale assumption. Unknown target composition, serum/plasma
and assay transport, direct age/female loadings, residual variance and the
metabolic component remain assumptions. Source uncertainty is not used as
individual variation or precision weights. Neither disease prevalence nor
individual clinical measurements have been recovered.

Actual deterministic analytic checks reproduce the two constrained Jansen
source projections and evaluate Bao's Pearson functional in a distinct eligible
source scenario. The Bao raw difference is approximately -0.002142, with no
optimization or significance/pass interpretation. MIND Spearman remains
contextual because no source rank/imputation law is represented. These are
qualified source scenarios, not source replay. All target-table source
comparisons are marked unavailable.

The submitted law has positive support for BMI/glucose/HbA1c and finite first
and second moments, proved from its affine gamma/uniform structure. The target
OLS coefficients, including E3, are assumption-dependent consequences of that
law. Exact analytic calculations and static contract checks are retained; no
generator has been imported, executed or sampled locally.

This initial candidate is submitted unfrozen for controller review and one
optional exploratory execution at seed 5201. A final retain/revise decision will
follow any permitted feedback. No target observations, target outcomes, prior
constructors or sources outside the assigned packet were used.
