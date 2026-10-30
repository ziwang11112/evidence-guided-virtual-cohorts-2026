# M13-B: frozen body-fat enrichment transport pilot

30 October 2026. This protocol implements the M13-A follow-up. It is a new-endpoint test in a previously used NHANES cycle, not a globally fresh cohort. Read `../m13/protocol_review.md` for the estimand equations and scientific limitations; the explicit decisions below supersede its optional branches. No outcome-based model development is allowed in this phase.

## Scientific question

Can the two source-built stochastic generators enrich an independent public target's age/sex/BMI records with body-fat percentage such that the same generated table supports useful adjusted associations, response shape and conditional distributions? Does the source-only numerical revision improve or worsen those analyses? Ordinary published equations are a scientific reference, not an Agent leaderboard.

The already-frozen initial and source-reviewed generator/specification bytes are retained. On this target (`asian=0`), build01's revision changes male location by -1 percentage point; build02's revision changes sex-specific dispersion. Neither revision learns a new target age/BMI functional relationship. Those shapes are largely inherited from Gallagher Equation 1. Success on a direction is evidence of transport of that supplied structure, not independent discovery of the relationship.

## Fixed target and schedule

Use official NHANES 2017-2018 DEMO_J, BMX_J and DXX_J files. Endpoint: DXDTOPF, total DXA body-fat percentage. The primary domain is age20-59, non-Hispanic White/Black (RIDRETH3 3/4), sex1/2, BMI18.5-<30, completed scan DXAEXSTS=1 with finite outcome and covariates, positive MEC weight and valid design. The separate extension is BMI30-35 inclusive. Retain all positive-MEC-weight DEMO frame PSUs for domain variance. No additional health restrictions or trimming. Outcome outside0-100 is an integrity failure, not an exclusion option.

The estimand is the examination-weighted complete-covariate, valid-scan domain. MEC weights do not resolve DXA nonresponse. Source-to-target population and device/software changes remain uncalibrated. Direct application assumes zero additional measurement bias. The NHANES BCA adjustment is not five body-fat percentage points and supplies no universal source-scanner correction.

Twelve Agent tables: builds01/02 x {initial, source_reviewed} x residual seeds33101,33102,33103. This replaces the optional two-scenario roster in the proposal with an explicit initial/final comparison; there is one structural scenario per builder. Four additional reference tables: Gallagher Equation1 deterministic mean and the same mean with independent Gaussian residual SD4.31 percentage points, rejecting/redrawing values outside0-100, at the same three seed identities. Rejection changes the stochastic reference conditional mean near the bounds; it is not exactly the deterministic mean after truncation. SEE-based residual form is an assumption, not identified target variance. Same seeds across different generators do not represent paired latent physiology. Sixteen tables total, all retained.

Every frozen table supports the complete panel; no analysis-specific regeneration. Final candidates are the primary scientific outputs, initial candidates document effects of source revision. Between-builder differences also include source-context assumptions, so they are not a controlled estimate of the value of a particular Agent.

## Analysis and uncertainty

For each sex: primary mean; weighted projection on intercept, B=(BMI-24)/5, A=(age-40)/10 and Black indicator; report BMI and age coefficients. Also fit B² and report the fixed curvature contrast1.28*beta_B². Extension reports mean and linear coefficients only. These are descriptive projections, not causal effects.

Eight primary distribution cells: sex x age20-39/40-59 x BMI18.5-<25/25-<30. Four extension cells: sex x age20-39/40-59 x BMI30-35. For each report weighted inverse-ECDF Q25/Q50/Q75/IQR with no interpolation. This pilot deliberately omits custom Woodruff and IQR confidence intervals: reference quantile uncertainty is not claimed. Native-unit discrepancies and three-seed ranges remain descriptive. This overrides the proposed interval extension rather than presenting unverified interval code as validated.

Means/projections/curvature use the full-frame nested-PSU Taylor sandwich, including zero-domain PSUs, and t intervals using domain-represented PSUs minus strata degrees of freedom. Their generated-minus-real difference uses the same operator on paired row differences. No independent-variance addition. Fail on full-frame singleton strata. Gates: n>=30, Kish weight diagnostic>=20, contributingPSUs>=8, domainDF>=4; regressions require full rank. Failed cells remain visible, not merged. No omnibus score, equivalent-performance cutoff or favorable-result selection.

Each interval is pointwise and design-conditional, not simultaneous, causal, individual-level or source/transport uncertainty. Three residual seeds give Monte Carlo descriptions only, not calibrated confidence/MI intervals or new participants.

## Information and execution boundary

Generator input columns exactly: id, age, bmi, male, asian, inv_bmi, male_inv_bmi, asian_inv_bmi, male_age, asian_age. The five derived columns are exact deterministic functions; asian=0. Opaque IDs do not encode SEQN. Race, weights, design, scan flags, all DXA families and real outcome stay in custody. Generators append only bodyfat. Only the generated program process is OS isolated by the existing WSL/bubblewrap adapter; LLM tool access relies on the assigned procedural boundary.

The pre-access manifest hashes this protocol, roster, evaluator, custody/controller code, audit and the original source model identities before acquisition. New execution bundles bind the real observed covariates, preserving original generator and specification bytes exactly; their new freeze is a deployment binding, not a scientific revision. All16 outputs are bound and evaluated once together. Implementation failures can be corrected with their original artifacts retained, but scientific model changes require a new reserved task.

Only aggregate results, code, protocols, source evidence and failure records enter the existing private GitHub. Real participant inputs/outcomes and generated participant tables remain local. No individual-level measurement recovery, clinical substitution, proven collection-cost savings or publication-readiness claim follows from this pilot.
