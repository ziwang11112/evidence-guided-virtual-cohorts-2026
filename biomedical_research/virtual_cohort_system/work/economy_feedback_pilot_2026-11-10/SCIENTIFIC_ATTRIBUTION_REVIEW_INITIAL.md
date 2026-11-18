# Initial scientific attribution review

Date: 2026-11-10. Scope: the two predesignated Sol_A parents only. This document records the initial audit before review-branch outputs were inspected. It is a root-only research artifact and must not be supplied to construction or revision agents.

## Inspection boundary

Read: `calls/initial/PNS_SOL_A/artifact.json`, `calls/initial/LIPID_SOL_A/artifact.json`, the corresponding original evidence and requested-analysis packets, task contracts, and common review instructions. No author program was imported or executed. No generated table, generated diagnostic, target outcome, target-reference summary, other initial author, or revision output was inspected for this review. No API call or external literature search was made.

The conclusions below concern static code-to-model consistency and the provenance recorded in the admitted packet. They do not independently authenticate the original articles or establish applicability to the target. This reviewer has historical project context; the review should not be described as a wholly historically blinded assessment. No historical target value was used to select or recommend a parameter.

Artifact identities (SHA-256):

| Artifact | SHA-256 |
| --- | --- |
| PNS_SOL_A initial artifact | `1f01954a0cca48c320ed5c736c20cdfd4105dcc9b174591adb3ce02f17aa72be` |
| LIPID_SOL_A initial artifact | `3c418f99a7b187a8b0f204dbacfd00f9220ec002eb1c41d48ba6813109419013` |
| PNS evidence packet | `c6ccbfa4ace5e909c48a53114e59de47e42a12f22e38edc44ea80f45b84da81f` |
| LIPID evidence packet | `8f4686adea0ddd9e9d7f17e0c08c32ad5c7fff58f88874dd5bd85b341b4562ed` |

## Main assessment

Both parents make substantial scientific choices, rather than merely printing a host-prescribed coefficient table. Both distinguish individual variability from uncertainty about the model, and neither claims execution that did not occur. Their present limitations differ:

- **PNS:** the declared population slopes and residual correlation follow exactly from the implemented additive law. Only the BMI coefficients have numerical external anchors, and their use in the requested target projection is an explicit transport assumption. Residual scales, residual correlation, and most of the covariate distribution remain assumed.
- **LIPID:** the code consistently implements a hybrid lognormal/copula scenario. Source marginal moments and pooled unadjusted ranks are transferred across populations and conditioning sets. The agent correctly refrains from equating a rank/copula latent parameter with an adjusted raw-scale estimand. The three requested population scalars are not calculated in its response, but the supplied analytic moment/projection recipe is appropriate. The law allows HDL to exceed TC.

This initial audit does not establish that either dataset supports an empirical scientific conclusion in the target. It also does not establish that feedback is necessary: one parent already has analytic component ordering, and both already disclose the principal evidence gaps.

## PNS_SOL_A

### Actual construction

Age is uniform on [20,79]. Female probability varies linearly from 0.48 to 0.56 across that range. Conditional BMI is an affine beta variable on [15,50], with mean `27 + 0.6*(age-50)/10 + female` and concentration 12. BP conditional means are linear in exactly the requested intercept, centered/scaled age, sex, and centered/scaled BMI design.

For independent standardized uniform variables U and V, independent of covariates:

```text
SBP = 122 + 5*a - 3*f + 0.7754*(BMI-25) + 14*U
DBP =  78 + 1.2*a - 2*f + 0.5967*(BMI-25) + 9*(0.6*U + 0.8*V)
a = (age-50)/10; f = female
U,V in [-sqrt(3), sqrt(3)] with mean 0 and variance 1
```

These equations are a transcription of the author's frozen code and specification, not an alternative generator proposed by the reviewer.

### Attribution of the important quantities

| Quantity | Packet supplies | Author uses | Attribution and unresolved bridge |
| --- | --- | --- | --- |
| SBP/BMI coefficient | INTERSALT 0.7754 mmHg per kg/m2, SE 0.0359; additional urinary-electrolyte and alcohol adjustment; inverse-variance pooled within-centre associations | 0.7754 as an additive conditional coefficient; requested per-5 value 3.877 | Reported numerical anchor plus assumed removal of adjustment differences, population/measurement transport, and extension beyond source ages 20-59 |
| DBP/BMI coefficient | INTERSALT 0.5967, SE 0.0257, same context | 0.5967; requested per-5 value 2.9835 | Same mixed provenance; the multiplication by five is algebra, whereas target applicability is not |
| BP residual Pearson correlation | No age/sex/BMI-adjusted residual correlation | 0.6, through the residual mixing matrix | Assumed. Beijing raw-moment correlations are explicitly not relabeled as residual correlations |
| Conditional BP SDs | No target conditional SDs; INTERSALT average subgroup SDs and Beijing marginal SDs have different operators | 14 and 9 mmHg | Assumed, explicitly distinguished from coefficient SEs and from marginal/subgroup SDs |
| Covariate distribution | Eligibility support and sex coding; joint distribution unidentified | Uniform age, age-dependent sex mixture, bounded beta BMI | Mostly assumed; source eligibility/coding does not identify density, mixture, slopes, or concentration |
| BP age/sex/intercept coefficients | No admitted compatible conditional operators | SBP [122,5,-3], DBP [78,1.2,-2] | Assumed |
| Tails and selection | No identified conditional tail/selection law | Bounded residual factors; direct modeling of the selected weighted analytical distribution | Assumed; equal-weight output is interpreted as draws from that already-weighted distribution, not as reconstruction of survey sampling |

The artifact consistently uses `mixed` for imported BMI coefficients whose numerical source is reported but whose target interpretation needs a bridge. It does not mistake the two correlated coefficients from one study for two independent sources.

### Mathematical and code checks

1. **BMI beta parameters remain valid on the whole specified support.** The conditional mean lies between 25.2 and 29.74. Both are strictly inside [15,50], so the constructed beta shape parameters are positive. There is positive conditional BMI variance, avoiding deterministic collinearity with age and sex.
2. **Population BMI projection claims are valid under the completed law.** The conditional means lie in the requested design span, and the errors have conditional mean zero. Correlations among the generated covariates do not change the population partial BMI coefficients from 5 times their additive raw-BMI coefficients. Thus 3.877 and 2.9835 are valid final-law projection values, rather than only proposal parameters.
3. **The residual-correlation claim is valid under the completed law.** The residual mixing rows have unit squared length; their inner product is 0.6. Covariate adjustment removes the full conditional mean. The final-law residual SDs are 14 and 9, and residual Pearson correlation is exactly 0.6 in the ideal population. No clipping, rejection, or nonlinear outcome transformation follows this construction.
4. **Component ordering already holds analytically.** The conditional mean difference is `44 + 3.8*a - f + 0.1787*(BMI-25)`. Its lower bound on the specified support is 29.813 mmHg. The residual difference is `8.6*U - 7.2*V`, whose absolute value is at most `15.8*sqrt(3)`, approximately 27.37. Therefore SBP-DBP is bounded below by approximately 2.45 mmHg. This conclusion is about the frozen support; it does not establish physiologic realism or target agreement. Both individual BP values also remain positive on these supports.
5. **Finite mathematical moments exist.** All covariates and residuals are bounded. The present law has no infinite-moment tail defect. Boundedness may nonetheless truncate clinically meaningful variation, which is a scientific modeling limitation rather than a nonexistence-of-moments defect.
6. **Uncertainty is described honestly.** Seeds change patient draws, not source coefficients or transfer assumptions. Repeated synthetic samples therefore do not quantify epistemic uncertainty.

The initial model contains three explicit numerical population-estimand claims, all supported by its code and algebra. Empirical samples can deviate through sampling variation; exact finite-sample matching is neither implemented nor claimed.

### What a subsequent revision could mean

A textual clarification alone would change reporting. A modification of residual mixing, dispersion, covariate law, mean law, or support would change the data-generating distribution. A source-only diagnostic cannot identify the target's unknown residual correlation or scales. Changing those values requires an additional stated assumption unless new admissible evidence is actually provided; this pilot does not provide such evidence.

## LIPID_SOL_A

### Actual construction

Recorded sex is sampled with probabilities [0.5,0.5]. Conditional on sex, BMI, TC, and HDL are lognormal margins driven by a Gaussian copula. BMI arithmetic mean/SD pairs are [20.87,3.15] for M and [22.28,3.85] for F. TC uses mean/SD [3.23,0.92] in both sexes, and HDL uses [1.14,0.38] in both sexes, in mmol/L.

The within-sex copula is parameterized by Spearman values [0.212,-0.1,0.106] for BMI-TC, BMI-HDL, and TC-HDL. Each is converted to a latent normal correlation using `2*sin(pi*r/6)`. An additional age coordinate has latent loading 0.3 on the BMI coordinate and independent Gaussian innovation. A positive lognormal age gap is added to 18, with assumed sex-specific gap moments [24,16] and [26,17].

The program does not round, clip, reject, calibrate a draw, or reorder lipid pairs. The specification explicitly says `enforce_total_cholesterol_at_least_hdl: false`.

### Attribution of the important quantities

| Quantity | Packet supplies | Author uses | Attribution and unresolved bridge |
| --- | --- | --- | --- |
| Sex-specific BMI arithmetic means and SDs | Agongo Navrongo adults aged 40-60 | Same numerical pairs, in adult target sex-specific lognormal margins | Mixed: reported values plus age/geography/selection transfer and an assumed lognormal family |
| TC and HDL arithmetic means/SDs | Agongo pooled moments | Same moment pair in each target sex stratum | Mixed: source values plus the substantive restriction that both target sex strata share the pooled moments |
| Three rank correlations | Obirikorang rural-community unadjusted Spearman values | Same ranks separately within each sex's target copula | Mixed: source values plus cross-population and pooled-to-conditional transfer; no source sex adjustment is claimed |
| Latent normal correlations | Not reported | `2*sin(pi*r/6)` from adopted ranks | Algebraically derived under the chosen continuous Gaussian copula, not direct raw Pearson or residual Pearson evidence |
| Age distribution and latent age-BMI loading | Target composition unidentified | Gap moments, loading 0.3, and no additional age-lipid latent path | Assumed; this restriction affects the adjusted projections |
| Requested adjusted raw-scale slopes and residual correlation | Not identified by the selected source operators | Numerical values left null; a moment/projection formula is supplied | Derived functionals of the fully specified law, not numerically evaluated by the author; their relation to target outcomes remains unverified |
| Uncertainty and selection | No numeric transfer-uncertainty model | Fixed scenario; no parameter sampling, clustering, or assay-error layer | Assumed scope, disclosed |

The source regression rows with unresolved log bases or scales are deliberately unused. The author does not turn geometric means or confidence intervals into arithmetic means or individual SDs. Omitting incompatible rows is not the same as establishing validity of the selected rows.

### Mathematical and code checks

1. **The marginal moment transformation is correct.** The code uses log variance `log(1+(sd/mean)^2)` and log location `log(mean)-log_variance/2`. With standard normal latent coordinates, these give the declared arithmetic conditional means and SDs. All these lognormal mathematical moments are finite; unbounded tails alone are not an infinite-moment defect.
2. **The copula parameter conversion is correct for the chosen family.** Increasing lognormal transforms preserve ranks within sex. The transformed correlation matrix is symmetric with unit diagonal and strictly diagonally dominant for these values, hence positive definite. The age-coordinate construction adds independent positive-variance noise and does not require an additional incompatible correlation matrix.
3. **A pooled source rank is not a target conditional rank by algebra.** The agent explicitly records that bridge as assumed. The internally valid rank-to-Gaussian conversion does not authenticate it. Because BMI margins differ across sex, the generated pooled BMI-lipid ranks need not equal their imposed within-sex ranks.
4. **The population projection recipe is valid.** For a pair of conditional lognormal variables, the raw covariance is the product of means times `expm1(sigma_i*sigma_j*latent_rho)`. Mixing conditional moments must include between-sex mean variation and the covariances with the sex indicator. The artifact explicitly calls for the mixture terms, then raw-scale covariance-matrix regression and its residual covariance. Centering/scaling age and BMI preserves the regression space, with the stated per-five and 38.67 outcome-unit factors. The supplied formula is not the mistaken substitution of a latent correlation for the requested residual correlation.
5. **The response does not actually provide numerical population-estimand scalars.** All three are null. That is an honest coverage limit, not a model nonidentifiability claim: once its assumptions and parameters are fixed, those population functionals are determined. Subsequent claim-coverage reporting should preserve the distinction between derivable, numerically declared, and numerically verified values.
6. **HDL greater than TC has positive probability under this law.** TC and HDL have nondegenerate jointly normal logarithms with nonunit correlation. Their log ratio therefore has nonzero variance and full real support. Consequently neither lipid is almost surely ordered below the other. This follows without sampling a cohort. The author discloses the absence of ordering.
7. **Ordering is a diagnostic here, not an eligibility failure.** The admitted packet explicitly says not to infer a `TC>=HDL` exclusion. Thus an inversion must not be silently dropped or called a contract-invalid row. Component coherence remains scientifically relevant, but identifying how often measured assays can invert the pair would require an actual measurement-error basis. This artifact models no such layer. Conversely, enforcing order would change the joint law and could change marginal moments, slopes, and residual correlation; zero inversions alone would not prove a better overall cohort.
8. **Age is unbounded above.** The task specifies no upper age boundary; the program respects its lower-bound contract. That does not establish that the assumed shifted-lognormal adult distribution is demographically credible. This distinction is a scope/realism issue, not a numerical failure inferred from a target.

### What a subsequent revision could mean

Changing only provenance wording or computing already-defined population projections improves documentation, not the generated distribution. Changing the distribution family, copula, latent age structure, or imposing lipid ordering changes the law. A nonlinear ordering/positivity operation requires reconsidering the final-law moments and requested projection claims; it cannot inherit the original copula's raw-moment claims automatically.

## Planned branch comparison, without new success criteria

The later audit will compare each feedback and ordinary-review branch with its exact shared parent. It will classify:

1. No scientific/code change.
2. Reporting-only or claim-coverage change.
3. Actual parameter change with unchanged family.
4. Structural or support/measurement transformation change.
5. Invalid or unreceived revision retained under the protocol.

For every actual change, record the cited evidence or assumption, the code path that implements it, whether the explanation describes the final law, and which requested analyses it can affect. Do not infer benefit from the mere presence of a revision. Engineering execution and fresh-seed evaluation are separate stages; target comparisons remain withheld from the revision agents.

The experiment can test whether providing an agent its own generated diagnostics changes its construction usefully under the fixed protocol. With only two paired parents, it cannot identify a universal cause of weak dependence, establish model rankings, or show that feedback supplies missing target information. The present audit adds no new task, data source, preferred coefficient, or author-facing repair recipe.
