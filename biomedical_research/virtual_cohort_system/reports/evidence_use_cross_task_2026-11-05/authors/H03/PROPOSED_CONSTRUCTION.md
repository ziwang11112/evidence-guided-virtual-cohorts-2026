# H03 proposed construction

Proposal awaiting independent scientific review. This is a statistical joint law for the specified fictional analytical design, not a causal mediation model. All parameters remain conditional on the following source transports and assumptions. The source numbers and provenance are in `SOURCE_REVIEW_REQUEST.md`; deterministic algebra and feasibility checks are retained in `PROPOSAL_ALGEBRA.py/.json`.

## Law and parameters

Let A=integer age, F=female, B=BMI, G=fasting serum glucose in mg/dL, H=HbA1c in percent.

1. Exactly375 individuals in each F crossed with the four age bands. Within each band, A is discrete-uniform on its inclusive ages. Thus E(A)=53.875 and Var(A)=270.359375 in the equal-cell design. The fixed quotas implement the task; the within-band distribution is A_design.
2. B is independent of A,F with scaled-beta support(10,65) kg/m², mean28.01 and SD3.8. Beta shape parameters are14.7796722475447 and30.3553623784941. The mean uses E_b_mean, the **marginal** SD uses E_K_moments. Supports and independence are A_BMI, not reported target properties or eligibility criteria. Broad bounds avoid a normal law's negative BMI while retaining underweight and severe obesity; behavior outside them is unassessed.
3. `mG = 91.2 + 0.20*(A-53.875) + 0.432*(B-28.01) - 4.4496*(F-0.5)`.
   Given A,B,F, `G/126 ~ Beta(p*kG,(1-p)*kG)`, p=mG/126. The constant concentration kG=22.3205971912142 is derived so that marginal Var(G)=12.4² in this design, rather than incorrectly setting the conditional SD to12.4. This gives0<G<126 almost surely. All corner means lie75.41988–114.42948 mg/dL. In eventual floating-point implementation, endpoints will be guarded by the task's positive/sub126 representable bounds; no additional clinical truncation is introduced.
4. Set a=0.010 pp/year, b=0.0125 pp/(kg/m²), f=0.0230 pp/female. These are respectively E_age and E_b_h. Let c be the HbA1c coefficient per mg/dL. It is **derived**, not a recovered published adjusted coefficient.
   `mH = 5.40 + a*(A-52) + (b-c*0.432)*(B-28.01) + (f+c*4.4496)*(F-0.5) + c*(G-90.825)`.
   Here90.825=E(G|A=52) under step3. Consequently the mean at age52 with reference covariate means is5.40, the BMI coefficient after marginalizing G is b, and the coefficient conditional on G is b−c*0.432. The age coefficient conditional on G remains a. These are statistical identities, not causal direct/indirect effects.
5. In a reference context with ages50–54 discrete-uniform, F balanced, and B and G as above, approximate marginal SD(H) by `(6.0-5.40)/z(.975)=0.306128074155` pp using E_h_ref and A_dispersion. This uses a normal approximation for a reported marginal quantile and mean, not a conversion of SE to SD. Reference covariate distributions are unreported and assumed (A_reference).
6. Solve the simultaneous moment equations: reference Var(H)=0.306128074155²; equal-cell marginal Corr(G,H)=0.23 (E_K_r, A_corr); and constant conditional Var(H|A,B,F,G)=s². Algebra yields c=0.00280394504774486 pp/(mg/dL), s²=0.0900283840773925 pp², BMI conditional coefficient0.0112886957393742 pp/(kg/m²), female conditional coefficient0.0354764338844455 pp. The squared correlation equation has a second root−0.0105409822543747, which fails the **signed** r=+0.23 equation and is discarded for that reason, not to force a desired coefficient sign.
7. Given all predictors, `H/100 ~ Beta(q*kH,(1-q)*kH)`, q=mH/100, `kH=mH*(100-mH)/s² - 1`. This preserves conditional mean mH and variance s² exactly. It respects the physical percentage support0<H<100 and imposes no HbA1c6.5 exclusion. Conditional draws are independent across people, apart from fixed stratum quotas. The conditional beta shape is a model assumption, not a measured residual law.

All predictors and responses have bounded supports; every moment is finite. The retained deterministic calculation verifies mH corner range4.654284–6.203936%, positive beta concentrations and s², and valid glucose means. No individual table, random draws or generator implementation was used. The future generator must use these actual specification values/derivations; only the controller executes it after freeze.

## Analytical-use decisions

| Analysis | Proposed use | Law-implied population coefficient, not observed target result | Critical limits |
|---|---|---|---|
| Q1_age10 | `relationship`: E_age → a |0.100 pp/10 years | Source adjustment matches variables but serum/plasma, country, sampling, selection and constant-age-slope transport remain assumptions. |
| Q2_bmi5 | `relationship`: E_b_h → b; G and H parameters enforce marginalization identity |0.0625 pp/5 kg/m² | Finnish age is binary and target age continuous; Finnish HbA1c/medication/fasting exclusions are stronger. No causal interpretation. |
| Q3_bmi5 | `relationship`/explicit assumption: E_b_h and E_b_g plus E_K_r and moment constraints → b−c*0.432 |0.0564434786968711 pp/5 kg/m² | No source directly reports this usable coefficient. It is an assumption-dependent joint-law consequence, especially A_corr and A_joint, not an independently supported source estimate. |

Model-use decisions will bind actual parameter paths, evidence IDs, assumption IDs, and retained deterministic checks for each requested analysis. Q3 will be marked partial, not directly reported. Q1/Q2 may be marked transported with direct-estimand links only where valid unit/adjustment definitions permit; all other links are components. No desired sign or hidden estimate was supplied or used.

## Named assumptions and uncertainty

- **A_population:** US NHANES, Finnish urban general population and Iranian Kerman associations/moments can be combined for this Mexico analytical design. Country/ethnic/laboratory/calendar differences remain unresolved.
- **A_selection:** Prior-diagnosis, fasting-duration, medication and HbA1c-selection differences do not alter the transferred components beyond this model. In particular, Finland excludes H>=6.5 and medications; Kerman includes known diabetes below the glucose cutoff. Target medication/anemia exclusions are not invented.
- **A_measurement:** Original HbA1c percentages are treated as commensurable; plasma-versus-serum and assay differences remain unresolved. Finnish serum glucose offers the closer compartment for its slopes.18.0 mg/dL per mmol/L is a recorded rounded unit conversion, not a biological calibration.
- **A_design:** Uniform integer ages within each mandated sex-age cell and fixed quotas; no national representativeness.
- **A_BMI:** BMI mean28.01 and SD3.8 can be combined, beta support10–65 is adequate, and BMI is independent of age and sex. Unreported age/sex/BMI associations are not asserted to be scientifically zero.
- **A_age_coding:** Finnish binary-age-adjusted BMI/sex slopes transfer to continuous-age adjustment; main effects are constant across25–79 with no age/sex interactions. Taiwan and Finnish subgroup findings qualify this choice.
- **A_g_age:** Approximately8 mg/dL source age contrast motivates0.20 mg/dL/year through an assumed40-year span; the denominator and linear extrapolation are assumptions.
- **A_fasting_adjustment:** S1 glucose slope is transported despite the displayed-block versus Methods ambiguity about fasting adjustment; no fasting variable is generated.
- **A_corr:** Kerman's *marginal Pearson* r0.23 transfers to the full equal-cell analytical distribution. It is never relabelled as a partial r. This strong design-sensitive constraint is central to Q3 and remains unverified.
- **A_dispersion:** NHANES age50–54 mean and upper quantile can define a normal-approximation marginal SD; subtracting proposed predictor variance leaves a constant conditional variance. Beta conditional shapes are working distributions. Reported SEs/p-values are not precision weights or residual variances.
- **A_reference:** Reference-age-band predictor distribution follows the assumed target BMI/sex/glucose law; original joint covariates are unavailable.
- **A_joint:** Selected components from different cohorts are simultaneously compatible in one linear-mean joint law. The algebra verifies mathematical compatibility only, not scientific transport. No causal pathway is inferred from regression decomposition.

Residual individual variation is distinct from uncertainty about all of these choices. No source precision has been fabricated, no posterior over transports is claimed, and multiple seeds would only measure Monte Carlo variation under this one model.

## Proposed review/check plan and stopping

Retained check so far: deterministic formula/moment/positive-support feasibility calculation, pass on the stated inputs. Neither harness validation nor source-feedback execution has yet occurred. Subsequent source/generated-only feedback should retain all available source comparisons and context mismatches: age-adjusted coefficient, mean/quantile by source age bands, BMI mean, glucose mean/SD, Pearson r, and any representable BMI slopes. The Finnish binary-age adjustment and ungenerated fasting covariate must not silently be replaced by continuous age; mark exact unavailable operators as not computable. Source means/quantiles that conflict with the chosen constraints remain visible, rather than being removed.

Matching a fitted source constraint is not independent validation. Q3 has no direct check against a source conditional coefficient. Do not use the inconsistent Kerman Table2 slopes as feedback targets. Full uncertainty, tails outside assumed BMI support, age/sex interactions and target validity remain unassessed. Three searches yielded no new usable conditional source; one query credit and two download slots remain before freeze, but no further search is currently justified by a promising admitted record. Submit this proposal for independent review before implementation.
