# PNS parameter provenance across both completed API pilots

This is a retrospective static map, not a new experiment or original-paper verification. It covers **14 initial attempts: 10 complete artifacts, 9 generators delivering data, 4 incomplete responses, and 1 complete artifact with execution failure**. Two unchanged review branches are separate lineage rows, not additional independent authors. No API or author code was run. Source packets are byte-identical across rounds.

The table reports **population functionals of the specified laws**, not synthetic sample estimates or clinical reference values. Root-owned synthesis joins the immutable evaluation summaries separately. Slopes use mmHg per 5 kg/m2. SDs below concern residuals of the requested age/sex/BMI linear projections.

| Round / initial or branch | Availability | Model-law BMI slopes: SBP / DBP | Model-law residual rho | Residual SD: SBP / DBP | Evidence route |
| --- | --- | --- | --- | --- | --- |
| R1 PNS_OA_ASTRA_C1 | success_existing_frozen_evaluation | 3.877 / 2.9835 | 0.6 | 15 / 9 | Source BMI anchor + assumed residual law |
| R1 PNS_DS_PRO_C1 | success_existing_frozen_evaluation | 3.877 / 2.9835 | 0.491514 | 17.9863 / 10.3489 | Source BMI anchor + marginal-source covariance/assumed decomposition |
| R1 PNS_CL_FABLE_C1 | incomplete response | — | — | — | No complete artifact; no parameter inferred |
| R1 PNS_GE_CARBON_C1 | incomplete response | — | — | — | No complete artifact; no parameter inferred |
| R1 PNS_OA_SOL_C1 | success_existing_frozen_evaluation | 3.877 / 2.9835 | 0.55 | 16 / 10 | Source BMI anchor + assumed residual law |
| R1 PNS_OA_ASTRA_C2 | success_existing_frozen_evaluation | 3.877 / 2.9835 | 0.568543 | 20.0794 / 10.7766 | Source BMI anchor + marginal-source covariance/assumed decomposition |
| R1 PNS_DS_PRO_C2 | success_existing_frozen_evaluation | 3.877 / 2.9835 | 0.5 | 13 / 8.5 | Source BMI anchor + assumed residual law |
| R1 PNS_CL_FABLE_C2 | incomplete response | — | — | — | No complete artifact; no parameter inferred |
| R1 PNS_GE_CARBON_C2 | incomplete response | — | — | — | No complete artifact; no parameter inferred |
| R1 PNS_OA_SOL_C2 | success_existing_frozen_evaluation | 3.877 / 2.9835 | 0.48 | 15 / 10 | Source BMI anchor + assumed residual law |
| R2 PNS_SOL_A | success_existing_frozen_evaluation | 3.877 / 2.9835 | 0.6 | 14 / 9 | Source BMI anchor + assumed residual law |
| R2 PNS_DS | failed_all_planned_seeds | 3.877 / 2.9835 | 0.5 | 15 / 9 | Source BMI anchor + assumed residual law |
| R2 PNS_SOL_B | success_existing_frozen_evaluation | 3.877 / 2.9835 | 0.47572 | 17.6313 / 10.2716 | Source BMI anchor + marginal-source covariance/assumed decomposition |
| R2 PNS_ASTRA | success_existing_frozen_evaluation | 4.677 / 3.5835 | 0.384615 | 11.7757 / 8.83176 | Source BMI anchor + assumed omitted-adjustment score and factors |
| R2 PNS_SOL_A_SECOND_LOOK | success_existing_frozen_evaluation | 3.877 / 2.9835 | 0.6 | 14 / 9 | Same PNS_SOL_A law; no independent author |
| R2 PNS_SOL_A_FEEDBACK | success_existing_frozen_evaluation | 3.877 / 2.9835 | 0.6 | 14 / 9 | Same PNS_SOL_A law; no independent author |

## Main distinctions

- All ten complete initial artifacts use the same INTERSALT numerical anchors. Nine specify requested BMI slopes 3.877/2.9835. R2 PNS_ASTRA adds an explicitly assumed omitted-adjustment contribution and instead implies 4.677/3.5835. Source copying, scale conversion, and target applicability are three separate steps.
- **No source reports the requested target residual correlation.** Some authors assume it or factor loadings. Others transport Beijing marginal moments and subtract covariance explained by assumed covariates/effects. The latter is reported + derived + assumed, not source-identified conditional evidence.
- R1 PNS_OA_ASTRA_C2 has innovation rho 0.578048 but requested linear-regression residual rho 0.568543 because an age hinge remains after the requested adjustment. Its author left the scalar null; the validated scalar comes from prior reviewer algebra. Do not plot the innovation rho as its requested endpoint.
- R1 PNS_DS_PRO_C1 uses literal residual rho 0.49151387 and literal SDs in execution. Its derived_marginal_moments block is explanatory metadata. The author-declared rho 0.4915139 is rounded; neither is an empirically measured result.
- R1 PNS_DS_PRO_C2 truncates age/BMI proposals, so their proposal means/SDs are not final covariate moments. Its additive BP law is evaluated on the final covariates; this does not invalidate the stated BP slopes or residual rho.
- R2 PNS_SOL_B correctly supplies a source-marginal-minus-explained covariance formula. This map evaluates that fixed analytic expression with scalar arithmetic only; it does not generate data.
- R2 PNS_DS has coherent abstract law claims but its output interface fails in all three existing evaluation slots. Treat it as **no delivered dataset**, not an inaccurate dataset. Frozen code is untouched.
- Both PNS review branches are exact code/specification no-ops. Additional explanatory detail is not additional scientific evidence or an independent construction.

## Traceability and use

`PNS_PARAMETER_MAP.json` contains every attempt, exact version IDs, source IDs and original locators, reported versus implemented quantities, operator/adjustment bridges, code lines, specification/decision pointers, artifact hashes, and endpoint claims. `provenance_components` deliberately permits multiple labels: deriving a number from a publication does not eliminate transport or model assumptions. Missing responses retain empty parameter lists and unavailable endpoints.

The main source is INTERSALT, Table II p322, with additionally adjusted inverse-variance-pooled within-centre coefficients. Beijing Table 1 contributes unadjusted marginal SDs only, when actually used. Study-specific means, age composition, device/measurement protocols, and selection remain different from the requested analytical population. The supplied standard errors quantify source coefficient estimation, not individual variation or uncertainty in transfer.

Numerical agreement of an output with this map can establish implementation fidelity to a chosen law. Only the separate scientific evaluation addresses agreement with the study reference. Repeated use of one anchor is not repeated independent external evidence.

Residual covariance contributes to the `sbp.sd_population` and `dbp.sd_population` diagnostics, but does not identify either marginal SD by itself. Marginal BP variation also includes variation in modeled conditional means over the covariate distribution. This core parameter map does not exhaustively audit every covariate choice or marginal diagnostic; unmatched diagnostics remain unassessed.
