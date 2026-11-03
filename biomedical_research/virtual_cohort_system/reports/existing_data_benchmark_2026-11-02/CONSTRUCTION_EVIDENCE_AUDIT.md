# Static construction and evidence-use audit

2 November 2026. **The added relationships were used mostly as qualitative guidance: 19 of 20 E1 author-by-relationship cells. Only E1_A01 numerically uses an added estimate, and that use does not enforce the reported source functional. None of the five E1 generators numerically constrains either Jansen conditional coefficient.** This is an audit of what the submitted programs implement, not a comparison of their performance.

This is a postconstruction static audit after the final submissions were closed. All ten final model specifications, generators, decision records and fixed evidence files were read. No execution directory, generated table, historical reference, target result or comparative statistic was opened; no generator was imported or run. The root reported final submission/freeze completion, but freeze/execution records are outside this audit's read set. The companion [JSON](CONSTRUCTION_EVIDENCE_AUDIT.json) records all 40 inspected file hashes and the classification basis. The auditor prepared the evidence/compiler earlier but authored none of these ten scientific models; this is not a separate independent audit of that packet work.

## What the added evidence actually does

**Q** means an explicitly stated qualitative rationale, without numerical use of the reported magnitude. **N*** means a numerical/algebraic use mediated by declared assumptions, not an enforced source statistic. A provenance citation alone was insufficient: the specification and executable parameter path were also inspected.

| E1 constructor | Jansen BMI 0.13 | Jansen FPG 2.29 | Bao Pearson 0.619 | MIND Spearman 0.529 |
|---|---|---|---|---|
| A01 | Q | Q | Q | N* |
| A02 | Q | Q | Q | Q |
| A03 | Q | Q | Q | Q |
| A04 | Q | Q | Q | Q |
| A05 | Q | Q | Q | Q |

Every E1 author cites all four records somewhere in its provenance/rationale; none is wholly unused at that qualitative level. No incorrect assertion of exact source matching was found. The 20 cells are record-use classifications, not independent studies or validations.

[E1_A01](scientific_submissions/E1_A01/generator.py) reads `source_rank_anchor=0.529` and computes `rho=0.85*2*sin(pi*0.529/6)` for conditional standardized log residuals. Its [specification](scientific_submissions/E1_A01/model_spec.json) correctly labels the Gaussian-copula interpretation, the 0.85 attenuation, and relocation from a marginal source rank association to a conditional residual association as assumptions. Shared mixture membership and covariates further alter the output association. This is real numerical uptake, but neither an exact Spearman match nor a numerical constraint on the reported MIND marginal functional.

E1_A02-A05 instead choose conditional log-residual correlations or variance fractions such as 0.42, 0.40/0.50, 0.45/0.55 and 0.45 as explicit assumptions. Their code contains no transformation or fitting step from the four reported relationships. Numeric source values appearing in prose/provenance do not become executable constraints.

All five explicitly decline to install or combine the two Jansen slopes. Their HbA1c equations operate directly in percent and use assumed log-scale covariate effects. No native-IFCC coefficient conversion, analytical solution for the two separate age/gender-adjusted OLS projections, or source-context projection-matching procedure appears. Consequently, **zero Jansen conditional functionals are numerically enforced**. This does not prove the finite outputs disagree with them; no such calculation was made. It means equality or discrepancy would be an outcome of the assumed law, not an implemented constraint.

## Structure diversity is real but concentrated

All ten follow the same broad hierarchy: bounded integer age, age-dependent female membership, age/sex-dependent lognormal BMI, a covariate-dependent latent glycemic state, and positively coupled glucose/HbA1c. All have assumed concave age terms in log BMI and independent primitive innovations conditional on the declared hierarchy. None identifies its latent state as an observed diagnosis. E0 already implements positive glycemic dependence without the four relationship records.

| Constructor and code | Age law | BMI and downstream coordinate | Glycemic law and residual dependence |
|---|---|---|---|
| [E0_A01](scientific_submissions/E0_A01/generator.py) | normal-CDF bin probabilities, conditioned to integer 35-74 | lognormal; Bao quartile-ratio dispersion; raw standardized BMI downstream | two state-specific lognormal components; shared-normal loadings 0.8 and 0.8 |
| [E0_A02](scientific_submissions/E0_A02/generator.py) | discrete Gaussian kernel on 35-74 | lognormal; assumed dispersion; tanh-saturated BMI downstream | two state-specific lognormal components; shared-normal loadings 0.75 and 0.8 |
| [E0_A03](scientific_submissions/E0_A03/generator.py) | discrete Gaussian kernel on 35-74 | lognormal; Bao quartile-ratio dispersion; raw standardized BMI downstream | two state-specific lognormal components; assumed class-specific log-residual correlations 0.60 and 0.75 |
| [E0_A04](scientific_submissions/E0_A04/generator.py) | scaled Beta(2.4,2.6), floored to integer 35-74 | lognormal; assumed dispersion; raw standardized BMI downstream | two lognormal components via state shifts and state-specific dispersion; shared-normal loadings (0.65,0.70) or (0.85,0.80) |
| [E0_A05](scientific_submissions/E0_A05/generator.py) | discrete Gaussian kernel on 35-74 | lognormal; Bao quartile-ratio dispersion; log-relative BMI downstream | lognormal cores plus shared additive gamma-severity tail on measurement scale; core shared-normal loadings 0.60 and 0.65 |
| [E1_A01](scientific_submissions/E1_A01/generator.py) | discrete Gaussian kernel on 35-74 | lognormal; assumed dispersion; raw standardized BMI downstream | two state-specific lognormal components; 0.85 * 2 * sin(pi * 0.529 / 6), used for conditional log residuals |
| [E1_A02](scientific_submissions/E1_A02/generator.py) | four ten-year strata, probabilities 0.27/0.31/0.25/0.17, discrete uniform within strata | lognormal; assumed dispersion; raw standardized BMI downstream | lognormal core with state-gated shared gamma severity added on log scale; assumed central conditional log-residual correlation 0.42 |
| [E1_A03](scientific_submissions/E1_A03/generator.py) | discrete Gaussian kernel on 35-74 | lognormal; Bao quartile-ratio dispersion times 1.03; raw centered BMI downstream | two state-specific lognormal components; assumed class-specific log-residual correlations 0.40 and 0.50 |
| [E1_A04](scientific_submissions/E1_A04/generator.py) | discrete Gaussian kernel on 35-74 | lognormal; assumed dispersion; raw standardized BMI downstream | two lognormal components via state multipliers and state-specific dispersion; assumed class-specific log-residual correlations 0.45 and 0.55 |
| [E1_A05](scientific_submissions/E1_A05/generator.py) | discrete Gaussian kernel on 35-74 | lognormal; assumed dispersion; log-relative BMI downstream | lognormal cores plus state-gated shared additive lognormal severity with outcome-specific lognormal noise; assumed core conditional log-residual correlation 0.45 |

Thus seven programs use two lognormal state components; one adds gamma severity on log scales, one adds gamma severity on measurement scales, and one adds lognormal severity on measurement scales. These differences affect tails and conditional relationships. They are not ten distinct broad model families. A state representation and a shared-factor representation are also not automatically separate biological mechanisms.

There is observable numerical use of common marginal evidence: E0_A01, E0_A03, E0_A05 and E1_A03 derive a lognormal BMI spread from Bao quartiles, with explicit conditional/transport qualifications. This common marginal uptake should not be confused with numerical uptake of the four added relationships.

## A mathematical tail limitation visible without generated rows

Seven models—E0_A01/A03/A04 and E1_A01/A02/A03/A04—use a positive linear function of unbounded lognormal BMI in **both** log-glucose and log-HbA1c equations. Under these exact population laws, a positive constant times `exp(c*BMI)` lower-bounds the conditional mean for `c>0`. A nondegenerate lognormal variable has no finite positive moment-generating function; the resulting raw biomarker means and second moments therefore diverge. Bounded age/sex and the positive state-specific scale factors do not remove this property.

This is a static mathematical consequence, **not an observed overflow, failed run or measured performance result**. The fixed finite samples may return finite values and calculable sample statistics. Those facts would not establish finite population moments or well-defined population OLS/correlation functionals for the underlying law. E0_A02's saturated BMI predictor and E0_A05/E1_A05's log-BMI predictors avoid this particular exponential-of-lognormal problem; this statement does not certify their overall realism or utility. No scientific correction was sent to authors and no submission was changed. The finding excludes no construction or seed, changes no fixed reporting denominator and authorizes no replacement.

## Assumptions, injection and interpretation

The code accepts `observed=None`, consumes specification/seed and contains no target-file, external-data or prior-result access. The specifications identify the demographic effects, latent-state probabilities, most scales, tail shapes and dependence parameters as assumptions. The audit found **no submitted evidence of target-row or target-effect injection**. It cannot establish how a model's unrecorded internal priors arose, prove pretraining non-exposure, or audit information absent from these artifacts. Task support and output row count are design inputs, not injected empirical target summaries.

Any eventual E0/E1 difference concerns availability and uptake of added evidence by these authors, with their model choices allowed to vary. It is not a controlled test of imposing four numerical constraints on one common generator. Shared prompts, source metadata/margins and general biological priors already support similar E0 structures; the narrow family spread further limits claims about broad methodological robustness. A weak contrast would not show that the unused numerical constraints lack value, and a favorable contrast would not establish that they were faithfully reproduced. The reused, already exposed CHNS benchmark supports explicitly labeled development analysis, not restored fresh confirmation or a clean causal attribution to a particular source operator.

This report intentionally makes no statement about the thirty generated tables, target agreement, arm superiority or comparative significance.
