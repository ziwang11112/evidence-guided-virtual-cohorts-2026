# Branch decision and permissible source-based specification

This branch identifies a reproducible alternative conditional mean (Pasco2012 model3), but no completed transport-validated revision. It supports a frozen structural sensitivity or direct source-fidelity check. It does not support a claim that substituting this equation improves the exposed M13-B target. No candidates were generated, calibrated, ranked, or evaluated.

## Structural specification, if a later protocol admits it

Let B be BMI in kg/m2, A age in years, M=1 for men and0 for women, and c=B-26.37. Use the published rounded conditional mean without fitted offsets or slope multipliers:

`mu = 37.8 - 16.7*M + 1.62*c - 0.06*c*c + 0.02*A - 0.17*M*c + 0.03*M*c*c + 0.04*M*A`.

Model3 is the published adjustment set compatible with age, sex and BMI inputs. Models4-5 require measured lean mass/BMC and are inadmissible substitutions. The source reports pooled regression S4.07pp, but that does not identify a complete sampling law for residuals. This specification therefore defines a conditional-mean reference, not a complete virtual-data generator. A later sensitivity that uses a Gaussian or sex-specific error law must label it as an assumption and cannot attribute it to this source.

## Direct source-fidelity checks

- Verify centering26.37, M coding, all eight coefficients and their units against Table4 model3, using pasco_coefficients.csv.
- Algebraically verify female/male local BMI derivatives1.62-.12c and1.45-.06c; age increments0.2/0.6pp per decade; quadratic coefficients-.06/-.03. These calculations require no target records.
- Compare any source-reconstruction fit only with quantities from the same model. The text's BMI25/30 predicted means refer to the preceding gender-BMI analysis, not an explicitly fixed-age model3 prediction. Do not impose those numbers as extra age-adjusted calibration constraints.
- Do not use the lower errors of models4-5, marginal fat SD, or fitted-mean CIs as model3 individual residual scales.

## Uncertainty and transport remain separate

Published marginal coefficient CIs do not identify their covariance. Independent draws of these eight coefficients would invent a joint distribution. Combined male age/BMI/curvature contrasts do not inherit valid95% CIs by adding marginal endpoints. A set of deterministic structural scenarios can be reported without probability weights, but it is not a posterior or a population confidence set.

Lunar DPX-L/ProdigyPro software versions and within-study scanner bridge are unspecified here. The source is almost entirely White and is selected by valid scans, with broad age support extending to96. Those facts do not identify population/device transport to the authorized mixed White/Black Hologic domain. An independent measurement audit must resolve any proposed bridge. No device correction is supplied by this branch.

## Minimum separate test, not executed

Before any later confirmation, freeze the exact candidate, residual assumptions, measurement mapping, uncertainty treatment, estimands and pass/fail criteria. Reserve an entirely unexposed target cohort or survey cycle with measured total DXA BF%, age/sex/BMI, documented scanner/software, and the design/selection variables required by its estimator. It must support the prespecified age20-59 primary BMI18.5-<30 domain and any separately declared BMI30-35 extension, including sex-specific analyses. Do not inspect its outcomes to choose between these three source equations. The already exposed M13-B target cannot supply independent confirmation.

Branch recommendation: **no-go for a complete source-supported generator revision on the evidence recovered here; conditional go only for recording the exact Pasco mean as an unvalidated structural alternative.** The missing residual law, joint coefficient uncertainty and population/device mapping are retained as scientific gaps, not filled by target-derived tuning. Root combines this result with the measurement branch for the final bounded-audit decision.
