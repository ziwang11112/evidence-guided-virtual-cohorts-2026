# Scientific construction: source-conditioned whole-cohort replay

Initial construction, 9 November 2026. No individual records, old candidates, old generated outputs, hidden reference data, or requested target-use results were read. The source-only task, admitted inventories, independent reviews, original Soares 2019/2020 XML, and the saved Soares 2019 supplement text were read. There were no retrieval requests and no generated rows. Declaration-only preflight, unexecuted code compilation and closed-form support/sensitivity checks are bound in checks.json.

## Intended product and interpretation

The product is 3,000 synthetic adult rows with identifier, age in years, sex F/M, raw BMI in kg/m2, and paired total and HDL cholesterol in mmol/L. It is an explicit scenario for the supplied Turkana adult context. Neither its demographic mixture nor its lipid distribution is identified for that target population by the permitted evidence. The target law below is a declared donor-based transport scenario, not an estimate of the actual Turkana sampling distribution.

The lipid variables are coherent assay-scale surrogates of fasting concentrations. They are not claimed to be error-free latent concentrations: the source effects were estimated from measured lipids. The construction represents positive HDL and positive non-HDL on the observed concentration scale and returns TC = HDL + non-HDL. It does not deconvolve source measurement error or add a second inferred assay-error variance. Identity of the source and target measurement scales, fasting state, and coherent partition is a transport assumption. Actual independently measured assays need not obey exact partition under all measurement errors. Consequently, the ordering diagnostic is applicable to this particular construction but cannot validate assays or target measurement equivalence.

## Source constraints and their role

The primary family is Soares et al. 2019, DOI 10.1136/bmjgh-2019-001542, original XML Table 3, BMI column. All eight entries are retained:

| Stratum | Published analysis n | TC coefficient [95% CI] | HDL coefficient [95% CI] |
|---|---:|---:|---:|
| Rural women | 4,971 | 0.23 [0.19, 0.26] | -0.03 [-0.04, -0.02] |
| Rural men | 3,548 | 0.20 [0.16, 0.23] | -0.03 [-0.04, -0.02] |
| Urban women | 7,455 | 0.13 [0.11, 0.15] | -0.05 [-0.05, -0.04] |
| Urban men | 3,705 | 0.15 [0.12, 0.18] | -0.04 [-0.05, -0.04] |

The unit is mmol/L per one source BMI SD. These are raw-outcome continuous linear projections, separately by sex and site, adjusted for age, ethnicity, education, household asset quintile, marital status, parity for women, lipid-lowering medication category, smoking, alcohol, physical activity, and HIV/ART. Robust household-cluster standard errors concern inference; the published intervals are retained rather than converted into individual residual variation. The regression weighting, exact BMI SD reference, precise age basis, original missingness procedure, and some coding conventions are unresolved.

Soares 2020, DOI 10.1186/s12916-020-01648-0, S7 is a related-source consistency/reporting check. Its female adult TC/HDL entries are 0.15/-0.05 and male adult entries 0.20/-0.05 per source BMI SD, with the original intervals retained in evidence. It overlaps the MEIRU source, restricts age/urban location, and uses multiple imputation. It will not add precision to 2019, be fit as an independent study, or receive a falsely exact replay. No age-interaction parameter will be selected to fit these overlapping estimates.

Liu 2023 is not needed to identify or fit the primary model and will remain a separately labelled, different-population contextual comparison. Its partial correlations cannot identify African residual covariance. In particular, its derived 0.1897 relation will not be inserted as a target correlation. The primary covariance sensitivity below is an assumption analysis, not a Liu-constrained empirical covariance matrix.

## Source sampling and standardization

Four source contexts represent assumed selected analysis laws: rural women, rural men, urban women, and urban men. Each context samples directly from its assumed law conditional on adult eligibility, fasting measurement, and retention for regression. There is no assertion that the original selection or missingness mechanism was recovered. Broader fasting-sample descriptive summaries are approximate anchors for that selected law. The unresolved four-record urban-men discrepancy is preserved.

Raw BMI uses a bounded beta law on [14, 55] kg/m2. Its beta shapes are obtained algebraically from an assigned mean and SD: with m = (mean - 14)/41 and v = (SD/41)^2, k = m(1-m)/v - 1, alpha = m*k, beta = (1-m)*k. Positive shapes and finite support are checked by inspection/contract implementation, not by optimizing to target answers.

| Stratum | BMI mean | BMI SD | Age mean | Age SD |
|---|---:|---:|---:|---:|
| Rural women | 23.5 | 4.3 | 37.6 | 15.6 |
| Rural men | 21.6 | 2.8 | 38.1 | 16.5 |
| Urban women | 25.6 | 5.4 | 32.4 | 12.4 |
| Urban men | 22.5 | 3.6 | 33.2 | 14.1 |

BMI anchors are the non-missing-lipid columns of Soares 2019 Supplementary Tables 1/2; their denominators differ from Table 3. Age anchors are original Table 1. The supplement prints 32.5 for urban women whereas Table 1 prints 32.4; the original main Table 1 is explicitly selected for age. Age uses a bounded beta on [18, 90] with the same algebraic moment parameterization. The finite age/BMI bounds and distributional form are assumptions, not source maxima, cutoffs, or recovered tails.

The main reference SD is the assigned stratum population SD above, interpreted as an approximation to the selected analysis-law SD. It is not described as the paper's known conversion constant. A displayed source predictor zBMI will use the generated context's sample mean and sample SD with ddof=1. Thus a coefficient estimated against zBMI is expected near b_raw times that realized source SD; Monte Carlo variation in the reference scale remains visible. The program will not orthogonalize residuals against predictors or force the realized coefficient to equal the printed estimate.

A relevant alternative is an all-four-strata pooled BMI SD computed from the reported broader-source means, SDs, and group counts 7,096/5,000/8,563/4,284. Using this common SD instead of stratum SD changes each corresponding raw-BMI coefficient. This is an analytic standardization sensitivity, not a claim that the original paper pooled its scale or that those descriptive denominators are exact. Its formula and resulting coefficient ratios can be reported without generating another cohort. No target BMI SD enters either convention.

## Explicit nuisance model and full design

All source nuisance variables will be generated and included in the source table. The replay design has an intercept, continuous linear age, and saturated categorical indicators for every stated source covariate; parity enters only women. A combined HIV/ART variable has negative, positive untreated, and positive treated states. Household asset quintiles remain categorical, with an assumed equal baseline probability. Reference category choices leave the fitted column space unchanged. Constant/absent dummy columns are handled transparently rather than changing the scientific adjustment list.

Baseline categorical probabilities use Table 1 counts within each sex/site where reported. HIV-positive probability and ART treatment among HIV-positive persons use the published counts/proportions, with the unresolved denominator distinction labelled. All categorical probabilities are normalized from counts, avoiding rounded percentages summing above or below one. Table 1 rural-women physical activity uses counts (100,224,6772), not the inconsistent printed high percentage.

The joint law is not reported. The chosen model makes source age and BMI independent before nuisance generation, then assigns categorical nuisances using finite marginal quotas. Baseline source weights are normalized, multiplied by the group row count, and rounded; every positive category receives at least one slot. Rounding differences are allocated deterministically as specified in the generator. Nonreference categories are then assigned in the frozen category order by ranking independent Gumbel draws plus declared BMI and age tilts among the remaining rows. The reference category receives the remaining slots. This is weighted assignment without replacement under fixed quotas, not an iid multinomial or recovered source joint distribution.

The BMI ranking covariate is (BMI - source BMI mean)/source BMI SD. The age ranking covariate is (age - 35.2)/15, with the existing 15-year scale explicitly stored as conditional_means.nuisance_age_scale_years. It makes nuisance ranking tilts dimensionless; it does not change the lipid conditional-mean age slopes, which remain per year. Assets, education, physical activity, alcohol and smoking use frozen BMI-tilt vectors with maximal values 0.20, 0.10, -0.20, 0.10 and -0.10 respectively. Marital status and parity use the frozen age-tilt vectors. Ethnicity has zero tilts. All vectors, category order, quota rules and independence restrictions are assumptions, not recovered correlations or calibration variables.

Most source nuisance coefficients are unidentified. The model will include modest nonzero concentration shifts for medication, HIV/ART, activity, smoking and alcohol, with their numerical values explicitly listed as assumptions. Ethnicity, education, marital status and parity have zero direct lipid shifts conditional on modeled variables in the reference scenario. This is an explicit conditional-mean restriction; absence of published coefficients is not evidence of zero effects. Their categorical variables remain in the full regression. Nonzero nuisance dependence on BMI and nonzero lipid shifts make the target age/sex-only projection distinct from the published full adjustment.

## Shared conditional concentration law

Let g index sex and a donor-environment regime. Denote the printed source BMI coefficients by b_Tg and b_Hg and the chosen source reference SD by s_g. Define shared raw slopes:

    beta_Tg = b_Tg / s_g
    beta_Hg = b_Hg / s_g
    beta_Ng = beta_Tg - beta_Hg

These slopes are shared by source and target contexts. Their exact equality across populations is the primary transport assumption. The eight published constraints therefore affect the target through one common conditional law; source and target branches do not contain disconnected fitted lipid models.

At covariates B,A,C, use linear conditional means for TC and HDL:

    m_T = T0_g + beta_Tg*(B - BMImean_g) + a_T*(A - 35.2) + d_T(C)
    m_H = H0_g + beta_Hg*(B - BMImean_g) + a_H*(A - 35.2) + d_H(C)
    m_N = m_T - m_H

The source conditional intercept anchors T0/H0 are (4.00,1.15), (3.73,1.09), (4.11,1.20), (3.98,1.15) in the same group order. These are original Table 2 age-standardized descriptive means, used only as approximate levels at centered covariates; they are not mislabelled regression intercepts. Centering nuisance terms at their assumed source expectation and reference age is a declared mapping, not exact recovery of the published standardization.

The reference age shifts are a_T=0.005 and a_H=-0.0005 mmol/L per year. Reference nuisance shifts are small and bounded, for example a maximum TC reduction of 0.50 for lipid medication, untreated-HIV shift (-0.20,-0.08) for (TC,HDL), treated-HIV shift (0.10,0.02), current-smoking shift (0.05,-0.04), and highest-alcohol-frequency shift (0.05,0.06). These numbers are unsupported model assumptions, not estimated treatment effects. Their full vectors and centering constants must be frozen before execution. The parameterization must establish m_H>0 and m_N>0 throughout the declared support; violation is a defect, not repaired by clipping rows.

For individual variation, generate mean-zero unit-variance bounded errors U_H,U_N using independent uniforms and a common-factor loading that gives Corr(U_H,U_N)=q. Set:

    H = m_H * (1 + c_H*U_H)
    N = m_N * (1 + c_N*U_N)
    TC = H + N

The reference c_H=c_N=0.25 and q=0 are individual-dispersion/coupling assumptions. With the proposed common-factor construction, each error magnitude is at most sqrt(6), so factors are at least 1-0.25*sqrt(6)>0. Every moment is finite. Heteroscedastic individual variation is allowed because its conditional expectation is zero. Source OLS remains a check of the raw conditional-mean projection; it is not a fit to a log-scale model or a retransformation shortcut. No coefficient CI is used to set c_H, c_N or q.

## Target law and transport limits

The target reference scenario has P(F)=P(M)=0.5, age = 18 + 62*Beta(2,4), and an independent 0.5/0.5 donor-environment regime. These are neutral declared design choices because target mixture information is unavailable. Donor environment means which source conditional function and BMI/nuisance anchor is used; it does not assert that a Turkana person has a Malawian location or ethnicity. The model's internal nuisance variables are transported statistical background draws, not recovered target characteristics. They are absent from the final six-column task output, but their effects and omitted-variable consequences are part of the target law.

Within sex/regime, the reference target BMI law, conditional lipid functions, and nuisance mechanisms are copied from the declared source law; the target age and mixture laws differ. This wholesale donor-law transport is a strong assumption, made inspectable rather than given a clinical-validity label. It is appropriate for this bounded source-consistency experiment only. Unknown target selection, diet, activity, infection, ancestry and assay differences can change both slopes and residual covariance.

The requested unweighted age/sex-adjusted raw BMI slopes are model projections after mixing regimes and omitting generated nuisances. They are not inserted into the generator. The requested paired TC/HDL residual correlation after age/sex/BMI adjustment depends on mixture, nuisance effects, residual dispersions and coupling. None of the eight primary coefficients identifies that correlation.

## Analytic sensitivities and uncertainty labels

The planned analytic sensitivity varies q over [-0.75,0,0.75] and separately the source standardization rule. These are scenarios with no probability weights. At fixed covariates, with s_H=c_H*m_H and s_N=c_N*m_N, the model implies:

    Corr(TC,H | A,B,C,g)
      = (s_H + q*s_N) / sqrt(s_H^2 + s_N^2 + 2*q*s_H*s_N).

This is a conditional relation with more covariates than the requested target residual analysis; it must never be reported as the latter. Its purpose is to exhibit the free coupling and component identity, not to fill the missing target answer. Changes to target regime mixture, nuisance effects and mean transport also remain free. More seeds only reduce Monte Carlo error conditional on these choices.

Source confidence intervals remain descriptive evidence uncertainty. The initial construction uses the printed point estimates without asserting a joint likelihood, independent study precision, or a sampled posterior. The source intervals, source-law Monte Carlo variation, individual dispersion, scale ambiguity, and transport uncertainty are distinct.

## Execution and review commitments

The candidate will read only the staged /input/task.json to choose the declared population/context, output columns and row count, and will preserve one generator.py and one model_spec.json across all source and target executions. It will return only task-declared columns. Source-only raw covariates, standardized BMI and nuisance columns will not leak into the requested target schema.

Proposed source schedule: four contexts, 8,000 rows each, seeds 19701/19702/19703, giving 12 source evaluations per stage and 24 across initial plus at most one revision. Target schedule: 3,000 rows, seeds 9701/9702/9703, once per stage, at most six final target tables total. There is no numeric optimizer and no planned calibration-objective evaluation. Closed-form parameter conversions and descriptive sensitivity calculations are logged separately; they are not independent clinical evidence.

Source feedback may justify one scientific revision or a retained model. No target requested-use results will be viewed before the final freeze. A code repair is distinguished from a scientific revision. All eight primary coefficients and their discrepancies remain reported; no CI-overlap acceptance threshold, favorable seed selection, or omitted diagnostic is allowed.

The supplied whole-cohort source replay schema has been implemented. Declaration-only lifecycle/source-replay/semantic/descriptive/use preflights passed. Closed-form bounds establish positive conditional component means over the declared support, and analytic source-scale/coupling sensitivities are bound separately. Generator execution, row-based source statistics and target analyses have not been run. Execution remains a controller action after independent review and freeze.

