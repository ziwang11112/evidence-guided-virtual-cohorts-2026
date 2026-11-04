# Independent initial scientific and implementation review

Date: 2026-11-04. Candidate: evcBuild01/candidates/initial. Decision: no materially blocking source, mathematical, specification/code or feedback-labeling inconsistency found. The candidate is ready for the controller's freeze and scheduled isolated execution. This accepts a coherent assumption-dependent construction for testing; it does not establish target-population validity or numerical agreement of generated rows.

No candidate edit was requested by this review. The author reports the submitted draft preserved at drafts/submitted_initial_v1. This reviewer read the stable candidate, the admitted source packet and relevant original passages, and independently calculated deterministic specification moments. No generator was imported or executed, no random rows were drawn, no target/reference data were read, and no network requests were made.

## Source meanings and provenance

The five cited text artifacts use the exact registered IDs/paths/hashes. Packet hashes and curator admission were verified in PROTOCOL_REVIEW.md. The LifeLines source remains a partial publisher rendering admitted by the controller after independent review, not gateway-approved content.

The Hainan sex counts, age/glucose/HbA1c mean-SD pairs and within-sex Spearman correlations were checked against the saved Results and Methods. The methods distinguish Spearman analysis from log-transformed/outlier-trimmed visualization; the candidate does not adopt the ambiguous regression coefficients. JDPP BMI medians/quartiles, unadjusted BMI-HbA1c Pearson values and relevant-analysis missing-case omission agree with the saved Tables 1–2 and methods. Its Table 3 Beta scale remains unresolved and is not used as a numeric per-unit slope.

Pani's main text distinguishes the adjusted age magnitudes 0.012 in FOS and 0.010 in NHANES, and documents NHANES survey weighting. The candidate uses the latter magnitude only through an explicit transport and sex-homogeneity assumption, not as a verified target age effect. LifeLines Model III values and extra covariates agree with the saved table; reported CI endpoints remain in notes with no invented confidence level or SE. The source's 10.93 factor is a slope conversion only. Hoorn Q4-versus-Q1 contrasts and CIs agree with the saved table and remain categorical, richer-adjustment conflict evidence. The author response's instability caution is retained. None of these differing adjusted estimands is silently substituted for the requested BMI term or pooled by sign.

All five check-artifact hashes listed in checks.json match the actual files. The semantic sidecar's evidence and recipe hashes match. The actual contract/static-validation reports state the program contract passed without generator execution, and the preflight record does not claim numerical agreement.

## Mathematical and code agreement

The sampler generates the declared Bernoulli female indicator, then a four-dimensional normal vector within each sex using the submitted Cholesky matrix. Its age threshold mapping produces exactly the stated 35–74 integer support. The three positive variables use the submitted shifts and exponential laws. The returned column order, row count, unique serial IDs and eight-decimal output rounding match the task/specification. No source file, reference path, external I/O or alternate scientific parameter is used by generator.py.

The source Spearman-to-latent conversion `2 sin(pi rho/6)` is correct for the declared continuous Gaussian-copula pair. The Pearson-to-latent conversion is correct for the selected lognormal/shifted-lognormal margins; additive shifts do not change correlation. These are consequences of the assumed family, not distribution-free source conversions. The BMI median and quartile-ratio fit does not fit both asymmetric source quartiles; the candidate explicitly reports the resulting endpoints.

The integer-age covariance uses the normal exponential-tilting identity over the actual category thresholds. It does not approximate age as continuous. The within-sex age slope calibration applies Frisch–Waugh–Lovell to the exact covariance matrix. A common pooled age slope need not equal the two calibrated within-sex slopes when the remaining slopes differ, and the separately calculated pooled value is correctly retained.

An independent deterministic checker, review_candidate_math.py, read the specification only and used SciPy's normal CDF to verify the PMF/threshold correspondence, positive definiteness, continuous pair moments and exact discrete-age covariances. It then reconstructed the full mixture covariance including the female regressor and solved both population OLS projections, independently of the author's within-sex pooling implementation. CANDIDATE_MATH_REVIEW.json records PASS: maximum covariance discrepancy 1.48e-12 and maximum pooled-projection discrepancy 2.22e-15. The latent minimum eigenvalues are about 0.539 and 0.454. The recomputed correlations and within-sex age calibrations agree to floating-point precision.

Bounded age/sex and a positive-definite Gaussian vector transformed by finite shifted exponentials give finite polynomial joint moments of every order. Nondegenerate conditional variation yields unique population linear projections. The stated existence claim is sound. The static calculations refer to the unrounded law; table rounding is a separate tiny numerical perturbation. No assertion is made that unbounded lognormal upper tails are empirically appropriate.

## Feedback scope and unresolved scientific assumptions

There are 34 bindings: 11 declared numerical operators and 23 unavailable definitions/estimands. Every computable recipe is labeled `approximate`, with raw target-output/source-summary differences only. They cover six Hainan means, two Hainan Spearman correlations, its female fraction and two JDPP Pearson correlations. The plan names the actual target population and explicitly denies source-population reconstruction. SD denominator conventions, quantile conventions, weighted/missing-covariate regressions, native-unit incompatibilities and unresolved Beta scales remain unavailable. No separate source context or mandatory source replay is required by this review.

Hainan's source n metadata means reported stratum size, not a verified variable-specific complete-pair denominator; missingness is not fully described. The `error` missing-value rule operates on the task's complete synthetic table and must not later be described as independent verification of the source's missing-data procedure. JDPP complete-pair n is left unknown. The sidecar and assumption notes already state these limitations. “Matched declared” means preflight agreement of declarations, not actual source-statistic agreement or faithful source-population replay.

The major assumptions are visible and consequential: transferring glycaemic margins/ranks from Hainan; transferring BMI margins/correlation from selected Japanese IGT adults; assigning unreported age–BMI, age–glucose and BMI–glucose latent links; importing an age magnitude across survey selection/geography; choosing shifted lognormal tails; and treating source fasting plasma as a baseline for target serum with unmeasured fasting adherence. The static BMI–glucose-link sensitivity already shows that adjusted BMI can change materially under unsupported dependence choices. This is structural uncertainty, not extra source precision or a calibrated probability distribution. Source feedback can inspect these assumptions but cannot certify them.

## Reviewed commitments and next gate

- generator.py: `6915bfdbae9647d5200cdcf79c2378a5836d5fc5388bd7c2ee0d523bd20ddb40`
- model_spec.json: `dff9fdc9a79548772411a5cb24134c5ec839a564f4ed8020a0c278f4a0465e92`
- evidence.json: `898e38d0010ff3adcca762ed7cc595e9f8919cc7ec2ae0f4cc0efaa514afdb09`
- source_semantics_v1.json: `cf2f10e8858bd53719c69c6ff5914af22e41d662c7bc44ddb332c12af6f8e965`
- whole_cohort_feedback.json: `a9968ab0211aee7ea1fa337dfd761eb17c7342f67787e12713f11abffe78ee02`
- checks.json: `9c9ce2d7d0ca379e52dc79e3b64247541223d51da49abc4408bb6d8aff9c2f09`

The next gate is actual frozen isolated execution and honest source/generated-only feedback. Preserve all scheduled seeds and failures, then permit at most one feedback revision or explicit retain decision. Numerical agreement with constraints used to construct this law is fitted consistency, not independent target validation. Target evaluation remains closed until the author finishes.
