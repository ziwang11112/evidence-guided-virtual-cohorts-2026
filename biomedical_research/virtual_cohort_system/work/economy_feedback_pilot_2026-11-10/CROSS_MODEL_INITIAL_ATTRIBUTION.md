# Cross-model initial scientific attribution

Date: 2026-11-10. Static review of all seven received initial artifacts. No generated diagnostics, synthetic/real rows, target-reference statistics, evaluation outcomes, or review responses were inspected. Author programs were read as text and were not executed. Original source articles were not freshly authenticated. The initial two-parent audit remains unchanged in `SCIENTIFIC_ATTRIBUTION_REVIEW_INITIAL.md`.

Seven received artifacts do not mean seven working generators. LIPID_DS had no artifact; its transport failure is reported by the root task and is not a scientific model result. PNS_DS has an apparent output-interface defect described below.

## PNS: the same source coefficients lead to distinct completion laws

All four artifacts import the INTERSALT BMI coefficients, 0.7754 and 0.5967 mmHg per kg/m2. Those sources have additional sodium/potassium/alcohol adjustment and within-centre pooling; the requested analyses do not. No artifact obtains a compatible target residual correlation from the packet.

| Initial artifact | Source-supported part and bridge | Conditional dispersion/dependence | Transformations and claimed population estimands | Static assessment |
| --- | --- | --- | --- | --- |
| PNS_SOL_A | Imports INTERSALT point slopes and assumes equality after changing adjustment/population/measurement | Assumed residual SDs 14/9 mmHg and Pearson rho 0.6, implemented by two standardized uniforms | Bounded covariates and additive BP; no clipping/rejection. Claimed per-5 slopes 3.877/2.9835 and residual rho 0.6 | All three final-law claims follow from the implemented conditional mean/covariance. The law guarantees SBP > DBP; assumptions remain unvalidated |
| PNS_SOL_B | Same slope bridge. Additionally transports Beijing overall marginal SBP/DBP/PP SDs 20.35/10.93/17.2 | Residual covariance is the transported marginal covariance minus covariance of the assumed conditional means; not a raw correlation mislabeled as residual correlation | Bounded beta BMI and a uniform disk mapped through residual Cholesky. Claims slopes 3.877/2.9835 and an exact expression for residual rho | Mean-covariance algebra and radius-2 disk covariance are correct. Residual scales/rho are mixed provenance: source marginal second moments plus assumptions about means, covariates, and transport. The numeric residual-rho scalar was not supplied |
| PNS_ASTRA | Imports source slopes as conditional-on-extra-adjustment anchors, then adds an assumed omitted-adjustment score associated with BMI | Assumed uniform-factor loadings give residual variances 416/3 and 78, covariance 40, hence rho 5/13 | Bounded additive law. Requested slopes 4.677/3.5835 include additional assumed contributions 0.8/0.6 per five BMI units | The different slopes are mathematically consistent, not a unit error: they arise from an explicit unverified adjustment bridge. Extra sophistication does not establish a more appropriate target relation |
| PNS_DS | Same direct source-to-requested slope bridge as Sol_A/Sol_B | Assumed bivariate-normal residual SDs 15/9, rho 0.5; independent age/sex/lognormal BMI roots | Declared additive law implies slopes 3.877/2.9835 and rho 0.5; Gaussian BP residuals permit negative/order-inverted values with positive probability | Scientific law claims are coherent. However, final `df[task['columns']]` indexes with descriptor dictionaries rather than names and is expected to fail. This is an implementation defect, not an evidence insufficiency result; execution outcome must be reported separately |

### Details that matter for interpretation

- **Sol_B derives conditional covariance instead of borrowing a raw correlation.** Its `K = Cov(E[BP|age,sex,BMI])` is computed from independent age, centered-sex, and beta roots. The displayed loadings and variances in its exact residual-rho expression match the program. The final covariance is `R = C_Beijing - K`. For the fixed settings, its diagonal residual variances are positive and the covariance matrix is positive definite. This construction honors the adopted marginal dispersion internally; it does not show that Beijing dispersion transports to the target.
- **Astra does not simply reproduce the source coefficients.** Its omitted score has conditional mean coefficient 0.2 on scaled BMI and outcome loadings 4/3. Marginalizing that score adds 0.8/0.6 to the requested slopes. The coefficient shift is explicitly assumed. Its exact residual correlation is `40 / sqrt((416/3)*78) = 5/13`.
- **The three bounded PNS constructions are not identical.** Sol_A uses independent uniform factors; Sol_B uses an elliptical uniform disk; Astra uses four uniform factors. All have finite moments and positive component ordering on their frozen supports. For example, Astra's minimum mean SBP-DBP is about 33.18 mmHg while its residual difference has maximum absolute value 32. For Sol_B, the corresponding minimum mean difference is about 33.51 and the residual difference is bounded by `2*sqrt(295.84 - Var(mean_SBP-mean_DBP))`, about 31.24. These are analytic support checks, not generated observations.
- **Independent covariates are not required for additive-model coefficient claims.** PNS_DS mentions independence as the reason its regression coefficients equal the conditional slopes. It is sufficient here, but the stronger useful property is a correct full linear conditional mean with mean-zero errors. The other PNS models retain correlated covariates without invalidating their projection derivations.
- **A valid mathematical law is not a delivered artifact.** Do not count PNS_DS's valid abstract law as successful data generation if its unchanged ABI fails. Do not repair the author output silently.

## Lipids: common rank anchors, different unreported demographic dependencies

All three received lipid artifacts use the same rural Obirikorang Spearman triple (BMI-TC 0.212, BMI-HDL -0.1, TC-HDL 0.106) and Agongo arithmetic lipid moments (TC mean/SD 3.23/0.92, HDL 1.14/0.38 mmol/L). They choose positive lognormal margins and a Gaussian copula. These are shared source and family choices, not three independent confirmations of those relationships in the target.

| Initial artifact | Marginal and rank provenance | Additional assumed dependencies | Population claims / support |
| --- | --- | --- | --- |
| LIPID_SOL_A | Sex-specific Agongo BMI moments; pooled lipid moments duplicated within sex; pooled rural ranks imposed separately within sex | Equal sex mixture; sex-specific shifted-lognormal ages; latent age-BMI loading 0.3, all remaining age-lipid latent association mediated through BMI | Three numerical estimands null; supplies valid conditional-lognormal mixture covariance and projection recipe. Raw requested residual correlation is not set to 0.106. HDL > TC has positive law probability |
| LIPID_SOL_B | Pooled Agongo BMI/lipid moments; rural ranks imposed on the unconditional continuous copula block | Thresholded-normal sex; seven assumed latent correlations for age/sex with the other variables | Three numerical estimands null; supplies raw lognormal moments, threshold-normal sex covariances, and correct Schur-complement projections. No ordering/selection transform |
| LIPID_ASTRA | Same pooled marginal and rank strategy as Sol_B | Thresholded-normal sex; seven assumed correlations with several different values from Sol_B | Three numerical estimands null; correctly defines the population regression/residual operators but does not supply an evaluated scalar. No ordering/selection transform |

The assumed latent Pearson parameters expose the relevant difference between Sol_B and Astra:

| Pair | Sol_B | Astra |
| --- | ---: | ---: |
| age-sex score | 0.10 | 0.10 |
| age-BMI | 0.20 | 0.15 |
| age-TC | 0.15 | 0.25 |
| age-HDL | 0.05 | 0.05 |
| sex score-BMI | 0.15 | 0.20 |
| sex score-TC | 0.10 | 0.08 |
| sex score-HDL | 0.05 | 0.06 |

These are author-chosen **latent** relationships, not reported raw correlations. They affect the requested age/sex-adjusted scientific analyses even when the three reported marginal rank anchors and lipid moments are unchanged.

The relevant mathematics is internally coherent: the positive-moment lognormal transformation and continuous Gaussian-copula rank bridge are correct; the full supplied correlation matrices are strictly diagonally dominant and positive definite. Sol_B's covariance formula with a thresholded sex field, `m_j*(Phi(r_j,sex*sigma_j - q)-p)`, is appropriate. Both covariance-based projection formulas and Astra's full normal-equation formula use the requested regression space and unit conversion correctly.

All three models have finite mathematical moments and unbounded positive tails. None claims that 0.106 is its adjusted raw residual correlation. All allow HDL > TC and adult ages with no finite upper endpoint. The original packet explicitly forbids silently adding a `TC>=HDL` eligibility exclusion; inversion counts are a component-coherence diagnostic, not automatically invalid rows. No assay-error mechanism justifying the inversion rate is specified by these artifacts.

## What these artifacts support before outcome evaluation

1. **The agent's consequential role is identifiable.** The source packet does not prescribe independent uniform factors, a marginal-minus-explained covariance bridge, a latent omitted score, within-sex versus pooled copulas, or seven demographic latent correlations. Authors select these parts of the joint law. Their provenance should remain visible at the analysis level.
2. **A universal “all agents copy the same parameter” claim is too strong.** PNS_Astra changes the requested slopes through a stated assumed bridge; Sol_B derives residual covariance using source marginal moments. Lipid families/anchors converge but their conditioning and assumed adjustment relationships differ. Three lipid artifacts and four PNS artifacts are too few to establish a general cross-model prior-convergence phenomenon.
3. **A universal “dependence errors are coding errors” claim is also unsupported.** Most inspected formulas correctly realize their stated scientific assumptions. PNS_DS is a separable output-interface failure. The distinction among law consistency, implementation delivery, and source-to-target applicability is essential.
4. **Numerical population-claim coverage differs by case.** PNS has explicit scalars or an exact analytic expression. All three lipid authors leave the three scalars null while correctly saying the completed law determines them. More verbose prose should not be counted as more identified evidence or successful numerical verification.
5. **Economy choice remains a workflow decision.** The two Sol draws per case already produce materially different valid scientific constructions, while the more expensive Astra adds an explicit bridge in PNS and a related copula in lipids. That does not establish Astra's added assumptions are more accurate. DeepSeek's one missing response and one apparent ABI failure are relevant delivery observations in this tiny run, not a model-wide ranking. Scientific performance and cost must be read from the separate sealed evaluation and ledger, which this review has not inspected.

This document does not recommend a replacement parameter, extra experiment, source search, or model repair. The four frozen review branches and planned evaluations should proceed without injecting this root-only review into their inputs.
