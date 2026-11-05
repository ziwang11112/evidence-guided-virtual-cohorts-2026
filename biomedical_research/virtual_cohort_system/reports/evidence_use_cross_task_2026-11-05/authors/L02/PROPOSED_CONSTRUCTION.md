# L02 proposed construction — source review stage

Status: proposal only, 2026-11-05. No candidate, generator, random rows, or execution has been created. The construction is an explicitly assumed adult scenario informed by external African population studies; it is not an estimated Turkana joint distribution.

## Complete probability law

For each of the requested 3,000 independent synthetic records:

1. Draw the recorded category S with P(S=F)=0.50 and P(S=M)=0.50. Balanced composition is an assumption, not a source or target proportion. Mapping source women/men summaries to F/M is also an assumption because the target metadata do not independently verify that code legend.
2. Independently of S, draw Z=(Z_age,Z_bmi,Z_tc,Z_hdl) from a zero-mean multivariate normal distribution with unit marginal variances and the correlation matrix below.
3. Let U=Phi(Z_age). Generate age by continuous linear interpolation of the following inverse-CDF knots. For M: probabilities (0,.25,.50,.75,1) map to ages (18,24,33,46,85). For F they map to (18,25,34,48,85). The internal knots borrow Greiner's Malawi rural reported age quartiles; continuous interpolation, endpoint 85, and use for this target are assumptions. Age 85 is a tail-model boundary, not a target eligibility exclusion. No rows are rejected.
4. Generate BMI=G_bmi(S)*exp(s_bmi(S)*Z_bmi), TC=G_tc(S)*exp(s_tc*Z_tc), and HDL=G_hdl(S)*exp(s_hdl*Z_hdl). TC and HDL are delivered in mmol/L; BMI in kg/m^2. The parameters are in the table below. The row identifier is a unique deterministic string.

| Parameter | M | F | Interpretation and basis |
|---|---:|---:|---|
| G_bmi | 21.5 | 23.2 | Assumed transported geometric mean; Greiner Table 1, Malawi rural |
| G_tc | 3.6 | 3.9 | Assumed transported geometric mean, mmol/L; Greiner Table 2, Malawi rural |
| G_hdl | 1.05 | 1.10 | Assumed transported geometric mean, mmol/L; Greiner Table 2, Malawi rural |
| s_bmi | 0.15008518742354868 | 0.17153121087276144 | Log-scale **marginal**, within-sex SD; derived below |
| s_tc | 0.27929359630610007 | same | Log-scale **marginal**, within-sex SD; derived below |
| s_hdl | 0.32459284597450133 | same | Log-scale **marginal**, within-sex SD; derived below |

The latent correlation matrix, ordered age, BMI, TC, HDL, is

```
[[1,     .12,                 .25,                .05],
 [.12,   1,                   .22155024842155735, -.10467191248588766],
 [.25,   .22155024842155735,   1,                   .11094596004995781],
 [.05,  -.10467191248588766,   .11094596004995781,  1]]
```

The age correlations (.12,.25,.05) are modest, explicitly assumed latent dependencies; the admitted evidence does not identify them. They are not interpreted as source age slopes. Sex has no additional effect on latent dependence; dependence is homogeneous across sex by assumption.

The other three entries use the Gaussian-copula identity r_latent=2*sin(pi*r_Spearman/6) on Obirikorang's **rural unadjusted pooled Spearman** values: BMI–TC .212, BMI–HDL -.100, and TC–HDL .106. The reported statistics remain Spearman, unadjusted, and pooled. This formula is valid for the proposed continuous Gaussian copula; it is not a distribution-free conversion to observed Pearson correlation. Applying these three values to a sex-conditional copula and combining them with an assumed age dependence is a substantive transport/conditioning assumption. In particular, neither the pooled generated rank correlations nor the requested adjusted raw-scale analyses are forced to equal them.

For the four log dispersions, use the lognormal moment identity s=sqrt(log(1+(SD/mean)^2)). The inputs are Agongo arithmetic mean and individual SD: BMI men 20.87/3.15, BMI women 22.28/3.85, pooled TC 3.23/.92, pooled HDL 1.14/.38. This transfers the **coefficient of variation**, not the arithmetic mean or conditional residual SD. Applying the pooled lipid CV to each sex and moving all CVs from ages 40–60 to the adult scenario are explicit assumptions. The means of the new margins are G*exp(s^2/2); the source arithmetic and geometric means are never equated. No confidence interval is used to infer individual dispersion.

## Finite moments and analysis meaning

Age is bounded [18,85], sex is bounded, and the other variables are exponentials of a finite multivariate Gaussian vector. All their positive polynomial moments, including every pairwise second and fourth moment needed for the requested OLS and residual Pearson summaries, are finite. For example, E[BMI^p TC^q HDL^r | S] equals the corresponding geometric-mean product times exp(one half of the finite quadratic form in the log scales and latent covariance). There is no exponentiation of a lognormal BMI inside another lipid model. Positive-definite latent covariance and positive BMI variation prevent population design singularity; nonzero lipid variation prevents an identically zero residual variance.

The proposed law has no post-draw clipping or rejection of BMI or lipids. The separate measured lipid margins do not impose TC>=HDL; the task specifies no such exclusion. This choice can admit rare assay-inconsistent pairs and is a visible limitation, not a claim about their target frequency. Any later structural change would require a new scientific decision rather than silent row repair.

The three requested analyses are properties of this law:

| Analysis | Evidence-use decision | What remains assumed |
|---|---|---|
| K02-HDL-BMI | Relationship: rural BMI–HDL rank relation informs latent association; dispersion/scale: external BMI and HDL margins inform raw-scale behavior | Gaussian copula; source-to-target and pooled-to-sex-conditional transfer; age dependencies; sex composition; mean/dispersion transfer |
| K02-TC-BMI | Relationship: rural BMI–TC rank relation informs latent association; dispersion/scale: external BMI and TC margins inform raw-scale behavior | Same structural and transport assumptions; a source rank coefficient is not an adjusted raw TC slope |
| K02-LIPID-RESIDUAL | Relationship: all three rural rank relations define the joint lipid/BMI latent block; nuisance age and sex assumptions determine the adjusted residual result | No admitted source directly identifies Pearson(TC residual, HDL residual) after age, sex, BMI; it remains model-dependent |

Requested OLS is unweighted with intercept, age, F indicator, and raw BMI. Reporting multiplies lipid coefficients by 38.67 and BMI coefficients by 5. Those units do not certify assay equivalence. Normal score coefficients or log-scale regressions will not be relabelled as these estimands. No favorable result or requested sign has been imposed.

## Evidence scope and reviewable checks

The selected geometric means and age quartiles come from Greiner's Malawi rural external strata. Those strata are not treated as target lifestyle categories or as known mixture weights. Agongo and Obirikorang are Ghanaian studies with different ages, selection, laboratory assays and fasting conditions. None establishes CardioChek Plus agreement or the unspecified target mixture. Within each study, multiple statistics are dependent summaries of the same cohort, not independent studies or independent evidence weights.

Source weighting remains **not reported** for all three packets. Source n is not used to derive an SE or a precision weight. Quantile interpolation and Spearman tie/missingness rules are also not verified. A mathematical operational assumption may justify this synthetic law but cannot turn those source definitions into verified equal-weight operators. Semantic source-feedback checks needing unknown weighting remain not_computable. Greiner geometric means and Agongo log regressions likewise remain unavailable to an unsupported source operator; they are never replaced by arithmetic means or raw slopes. Generated-only unweighted statistics may be inspected under their own names.

Deterministic algebra actually executed: computed the three copula entries and four log dispersions above; computed the symmetric matrix eigenvalues (0.6801296892468623, 0.8273456761383242, 1.0880177807818767, 1.4045068538329362). All are positive. This checks mathematical existence of the latent law only. It does not test generated rows, transport, target performance, or a generator implementation. No sampling has occurred.

After independent review and implementation release, planned checks are contract validation; exact specification use; positive-definite covariance; finite/positive required fields; generated-only distribution and requested-analysis summaries; and truthful not-computable source-semantic declarations where required. No new uncertainty calibration is claimed. Seed variation would reflect only simulated individuals, while the fixed assumptions about structure and transport remain unquantified.
