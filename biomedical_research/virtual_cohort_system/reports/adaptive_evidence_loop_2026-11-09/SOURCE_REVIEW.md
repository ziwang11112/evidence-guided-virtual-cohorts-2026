# Independent source and candidate declaration review

Status: initial frozen candidate reviewed. Four issues identified in the draft were corrected or explicitly retained as unresolved source ambiguity before freeze. No remaining extraction or declaration error was identified in the reviewed files. This review reads approved registry-bound source artifacts and candidate declarations only. It does not read patient rows, generated rows, target references or generated-analysis results, and does not prescribe desired target relationships or parameters. `SOURCE_REVIEW.json` records exact source and declaration hashes.

## Verified source definitions

- **Zanzibar, PMC6615808:** Table 2 adult strata are 18–<45 (n=195) and 45+ (n=110). Sixteen arithmetic mean/individual-SD items and three adult age/sex count fractions in the draft match Tables 2–3. The full n=470 includes 165 children. The analysis sample comes from complete biomarker cases, reported fasting and removal of top 1% extreme cardiometabolic/obesity values; age filtering does not replay these restrictions. Weighting and SD divisor conventions are not fully specified. Its association models are mixed logistic odds ratios with household intercepts and additional adjustment, not continuous raw lipid slopes.
- **Tanzania/Uganda, PMC6897412:** The four rural lipid means and CIs and two categorical HDL coefficients are transcribed correctly. Table 2 means are survey-weighted; CIs describe estimator precision. The hierarchical regressions explicitly omit sampling weights and retain strata/age/sex plus source-model covariates. Nonfasting serum measured with Cobas Integra 400 Plus is not verified equivalent to the task assay.
- **Ashanti and Navrongo:** Candidate numbers agree with the admitted curator packets. Ashanti contains community-specific unadjusted Spearman correlations, not Pearson or conditional correlations; age eligibility is unresolved in the packet. Navrongo BMI means concern ages 40–60 and the derived sex contrast is marginal. These packets were not independently reauthenticated against newly retrieved primary full text in this review.
- **Greiner:** Reviewed admitted packet, unused in the initial candidate. Its reported geometric means and estimator CIs must not become arithmetic means/individual SDs; age quantile conventions, selected source populations and denominator disagreements remain explicit.
- **PTS manufacturer page:** Current strip-specific ranges differ for HDL: Lipid Panel uses 20–120 mg/dL, while CHOL+HDL variants use 15–100 mg/dL. These are device ranges, not biological bounds or source population SDs. The draft properly retains unknown historical strip/version/censoring and uses ranges only diagnostically.

## Findings sent before freeze

1. **SR1 — preserve contradictory source evidence.** PMC6897412 Table 4 prints female HDL +0.08 with 95% CI 0.05–0.11; the Results prose says female gender is associated with lower HDL. The draft adapts the table coefficient but omits this source contradiction. Retain both and state the disposition; this review prescribes neither a direction nor a parameter.
2. **SR2 — correct known weighting metadata.** Both adjusted category-contrast checks say `weights: not_reported`; methods explicitly state these regressions are unweighted. Correct the metadata while keeping the unsupported calculation status.
3. **SR3 — remove unsupported age eligibility.** The draft calls Ashanti participants adults although the admitted packet says the age range was not established. Remove that assertion or bind supporting primary evidence.
4. **SR4 — distinguish core from complete adjustment.** Age and stratum are known core adjustments for the female contrast; the exact complete final coefficient-specific adjustment is not explicit in Table 4. Preserve this uncertainty instead of certifying the short list as complete.

## Assumptions and scientific limits

The candidate clearly labels cross-population transfer, lognormal marginals, Gaussian-copula dependence, equal community influence, marginal-to-conditional transfer, sex-effect adaptation, within-stratum age independence and older-age support. These are model assumptions, not extraction mistakes. Source marginal moments and ranks do not uniquely identify the requested adjusted raw-scale BMI coefficients or residual TC–HDL correlation.

The separate strict route remains unavailable; the descriptive route names conventional calculations without promoting them to verified source reproduction. Four weighted source comparators remain known mismatches. Category contrasts stay unavailable. Source SDs and estimator CIs are not pooled or used as tolerances. Reusing the same generated correlation against two community coefficients supplies overlapping diagnostics, not independent validations.

No target-calibrated conclusion or biomedical usefulness claim follows from this declaration review.


## Initial frozen candidate: author dispositions and integrity

The draft finding timeline above is retained. In the frozen initial candidate, SR1 is disclosed explicitly in evidence applicability and `A_sex`: the table coefficient is chosen provisionally for the scenario while the contradictory prose remains unresolved. SR2 is corrected to `weights: none` for both contrasts in both feedback plans. SR3 removes the unsupported adult-age assertion for Ashanti. SR4 states that age/stratum are only known core adjustment and the complete coefficient-specific set remains unresolved. No numerical parameter was requested by this review.

The reviewed metadata, generator and deterministic-math file hashes match the initial freeze commitments. Freeze SHA-256: `910ac38a114a47e2798e27046e4888492c2da47962289541c778a11fc710e5d5`. The JSON records the separate draft and frozen snapshots, so this is not a retrospective claim that the original draft had no issues.

Declaration-only preflight confirms 29 strict unavailable checks. The descriptive plan has 26 ready calculations and three null operators: 22 assumed-convention definitions, four known weighting mismatches, and three unsupported definitions. These are plan statuses, not inspected numerical feedback results. Strict unavailable results are not upgraded.

## Static generator and independent model-law check

The frozen generator matches the declared two-stratum beta age model, age-stratum sex fractions, sex-specific lognormal marginals and common Gaussian copula. Independent algebra from the specification confirms positive beta shapes, the declared age means/variances, a positive-definite copula, positive sex-specific means and positive within-sex variation. All six marginal mean/variance identities agree with the retained deterministic calculation. No random draw or generator import was performed.

For stratum mean m, SD s, female fraction q and sex difference delta, between-sex variance is b=q(1−q)delta². The implemented log variance is log[(m²+s²)/(m²+b)]. Its within-sex mixture variance plus b equals s², so the sex contrast does not consume the source SD twice. All lognormal parameters are finite, giving finite model moments. This verifies the specified mathematical law, not a target population law.

Age supports match the feedback age filters in the continuous model; the old-age upper support is explicitly an assumption. Units stay in years, kg/m² and mmol/L. The generator has no extra disease/fasting/assay-range eligibility filter, deterministic tail clipping, row dropping or TC≥HDL enforcement. Consequently HDL>TC is possible under the declared separate lognormal variables and remains a scientific limitation/diagnostic, not a silently repaired value. The exact-age independence, copula transport, tail shape and source assay differences remain unverified assumptions regardless of numerical source fit.

Any later candidate revision must receive its own stage record in `SOURCE_REVIEW.json`; this review has read no generated or target results.
