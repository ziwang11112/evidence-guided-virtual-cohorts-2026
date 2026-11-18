# Lipid parameter map across the two completed pilots

This map covers **16 records: 10 first-round initial attempts, four second-round initial attempts, and two review branches**. Thirteen delivered scientific artifacts are mapped; two Gemini attempts ended with incomplete responses, and the second-round DeepSeek lipid attempt had a transport failure. Missing artifacts have no inferred parameters. The JSON is the detailed source/operator map; immutable evaluation results are joined separately by the root synthesis.

## Source anchors and operator bridges

The captured curator packet reports Agongo pooled arithmetic TC mean/SD **3.23/0.92** and HDL **1.14/0.38 mmol/L**, sex-specific and pooled BMI moments, and sex-specific univariate **log-lipid** BMI coefficients (TC **0.013**, male HDL **−0.007**; log base unresolved). Multiplying a coefficient by a raw mean gives a local raw derivative only after assuming a natural-log/exponential-mean bridge. Extending that derivative into a common age/sex-adjusted linear slope is another assumption.

Obirikorang rural pooled-sex Spearman anchors are **BMI–TC 0.212, BMI–HDL −0.100, TC–HDL 0.106**. Gaussian-copula models use `r = 2 sin(pi*rhoS/6)`. This is valid latent-correlation algebra under that family; it does not make either input the requested adjusted raw slope or residual Pearson correlation. Applying these pooled-sex anchors within sex, as the Astra R1 and Sol_A R2 laws do, adds a conditioning bridge. Sol C2 and the second-round Sol_B/Astra laws instead use unconditional anchors.

Greiner Uganda geometric means and age quartiles inform Astra C1's marginal construction; Agongo arithmetic coefficients of variation supply its log-shapes. Thus the cited Ghana SDs are reference shapes, not the final Uganda-centered generated SDs. Greiner regression scales remain unresolved and cannot directly identify target partial slopes or residual correlations. **Locator correction:** the captured packet uses `reported_statistics.columns` plus `reported_statistics.rows`, not `records` as asserted by the prior audit. Native row IDs and actual row indexes are recorded in the new JSON. This is a correction to the synthesis only.

## Delivered-law claims

Slope values below are **mg/dL per 5 kg/m²**. Exact values describe a fixed model's population projections, not demonstrated target validity. Copula rows retain a projection recipe without fabricating a scalar from generated samples.

| Round | Exact version ID | Static endpoint interpretation |
|---|---|---|
| R1 | `LIPID_OA_ASTRA_C1` | Raw-moment projection recipe; numeric endpoints unavailable |
| R1 | `LIPID_DS_PRO_C1` | Exact under fixed law: HDL -0.96675, TC 7.734, residual r 0.14 |
| R1 | `LIPID_CL_FABLE_C1` | Exact under fixed law: HDL -1.1601, TC 9.6675, residual r 0.35 |
| R1 | `LIPID_GE_CARBON_C1` | incomplete_response; no scientific parameters inferred |
| R1 | `LIPID_OA_SOL_C1` | Exact under fixed law: HDL -1.542933, TC 8.1187665, residual r 0.15 |
| R1 | `LIPID_OA_ASTRA_C2` | Raw-moment projection recipe; numeric endpoints unavailable |
| R1 | `LIPID_DS_PRO_C2` | Proposal claims only; positivity selection invalidates exact output identities |
| R1 | `LIPID_CL_FABLE_C2` | Exact under fixed law: HDL -1.063425, TC 9.6675, residual r 0.381330923 |
| R1 | `LIPID_GE_CARBON_C2` | incomplete_response; no scientific parameters inferred |
| R1 | `LIPID_OA_SOL_C2` | Raw-moment projection recipe; numeric endpoints unavailable |
| R2 | `LIPID_SOL_A` | Raw-moment projection recipe; numeric endpoints unavailable |
| R2 | `LIPID_SOL_B` | Raw-moment projection recipe; numeric endpoints unavailable |
| R2 | `LIPID_ASTRA` | Raw-moment projection recipe; numeric endpoints unavailable |
| R2 | `LIPID_DS` | transport_failure; no scientific parameters inferred |
| R2 | `LIPID_SOL_A_FEEDBACK` | Raw-moment projection recipe; numeric endpoints unavailable |
| R2 | `LIPID_SOL_A_SECOND_LOOK` | Raw-moment projection recipe; numeric endpoints unavailable |

The four supported exact laws have linear conditional means in the requested design and independent centered errors. Their positive-output guards/floors are inactive for the fixed supports. DS C1 uses bounded Rademacher errors; Sol C1 uses bounded uniform common factors, with residual correlation `0.5*0.3=0.15`; Claude C1 solves the latent correlation for a chosen raw error correlation. These are internally coherent assumption-dependent laws, not source-derived adjusted regressions.

Claude C2 constructs **TC = HDL + non-HDL**. With component residual SDs 0.33 and 0.80 and zero HDL/non-HDL residual correlation, the requested TC/HDL correlation is `0.33/sqrt(0.33²+0.80²) = 0.381330923`, not zero. Its non-HDL SD includes an assumed explained-variance budget and subjective reduction, so it is not purely derived from reported marginal SD. Component floors are inactive and TC≥HDL is structural.

DS C2 repeatedly redraws bivariate-normal lipid proposals until both outcomes are positive, with a finite-attempt floor fallback. Acceptance depends on covariates. Its declared slopes and rho are therefore proposal parameters, not established exact output projections. The structural derivation issue exists even when its numerical effect in a generated sample is small.

## Paired second-round lineage

Both lipid branches descend from **LIPID_SOL_A**, with identical initial artifact and prompt. The ordinary `SECOND_LOOK` branch retains the same generator and model_spec, while its returned decision record clarifies the reporting. The `FEEDBACK` branch changes **only age**: an unbounded shifted lognormal becomes a shifted-scaled beta on **[18,100]**. The 100-year endpoint is an explicit new assumption, not a task exclusion, source estimate, or observed maximum. Beta shapes preserve the assumed sex-specific age means and SDs; the latent age–BMI loading remains 0.3.

The revised age transform consumes no extra random draws and leaves sex, BMI and both lipid columns unchanged for matched seeds. It can nevertheless change age-adjusted BMI projections and residual correlations through age covariance. The decision correctly replaces the all-lognormal age cross-moment formula with the beta-quantile integral. It cannot change the lipid component-inversion fraction when the lipid columns are unchanged. This is a comparison of paired review strategies, not two independent initial models.

## Interpretation limits

Marginal SD, innovation SD, final OLS residual SD and parameter uncertainty must remain distinct. None of the fixed-seed scenarios propagates source or transport uncertainty. Source populations, selection rules, assays, fasting protocols and recorded sex mapping are not validated merely by reusing their numbers. Positive noncomponent copula margins permit HDL>TC; that diagnostic concerns component coherence and is not a frozen schema exclusion. No new paper verification, clinical-source assertion, API call, generator run, target tuning or frozen-file edit was performed for this map.
