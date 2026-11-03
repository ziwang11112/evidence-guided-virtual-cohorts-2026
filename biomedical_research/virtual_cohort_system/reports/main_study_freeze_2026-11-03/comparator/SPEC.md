# Same-information statistical reference: fixed source-moment construction

3 November 2026. Status: implementation and invented analytic checks complete; independent review and campaign release still required. No clinical source fit, target candidate or row table has been produced in this preparation unit.

## Constructor and runtime interface

After the external campaign release, call `build_spec.build_harness_spec(case_id, arm, packet_bytes, task_bytes, compiled_evidence_bytes)` once for each of `CHNS2009/E0`, `CHNS2009/E1`, `ENSANUT2018/E0` and `ENSANUT2018/E1`. It takes exact admitted external packet/task/compiled-evidence bytes, retains their SHA-256 hashes, normalizes source records, performs the fixed deterministic source fitting, and returns `model_spec`, `construction_trace` and the canonical trace SHA-256. The controller retains and binds both artifacts; only `model_spec` enters the harness. Its provenance keys exactly match its parameter keys and every provenance entry has the existing three-field ABI. The wrapper invokes the actual `cohort_harness.contracts.validate_spec`. It has no file discovery, reference-data argument, network access or random draws. Source fitting is construction work and has deliberately not been called on the actual case packets during preparation. The lower-level `build_spec` returns a recipe/diagnostic object and must not be used directly as a harness specification.

CHNS raw grouped records map to the established compiled item IDs with `_MEAN`/`_SD`, `_MEDIAN`/`_Q1`/`_Q3`, or `_FRACTION` suffixes; relational IDs remain unchanged and the unit-guidance ID is `U_NGSP_SCALE`. ENSANUT uses its admitted item IDs unchanged and `NGSP_UNIT_GUIDANCE`. Missing or duplicated compiled IDs fail before fitting. The controller must independently validate the complete compiled evidence and its raw-record correspondence; the wrapper's membership/ABI check is not a new source-extraction audit.

The unchanged standalone `generator.py` provides `generate(observed, spec, seed)` for the existing isolated harness. It requires `observed=None`, the bound 3,000-row case specification and a controller-supplied seed. It uses only NumPy, pandas and the Python standard library. It performs no fitting, retrieval, reads, writes, trial search, filtering or redraw. This sampler has been statically inspected and its parameter validator exercised; it has not been invoked to create rows here.

Every source fit has one fixed all-zero dependence starting point, a 300-iteration cap and no alternate-start/family search. All source contexts are fitted separately, never pooled in a cross-study objective. Analytic fitting creates no synthetic participant table. No exploratory row attempt is required by this reference; the two allowed slots remain unused unless a separately recorded eligible execution is scheduled. The three final draws are the only planned row production. A fitting or sampling failure stays in the construction/attempt denominator; no successful replacement is selected afterward.

## Statistical family and source projections

The family is a positive Gaussian copula with fixed source marginal models. With latent correlation matrix R, lognormal margins have `Cov(X,Y) = E[X] E[Y] (exp(sigma_X sigma_Y R_XY)-1)`. Additive offsets do not change covariance; the implementation subtracts the offset when applying this formula. Normal/lognormal mixed pairs have their analytic covariance. Other admitted pairs use deterministic Gauss-Hermite quadrature and a separate integration-order agreement check, not sampled rows.

Each adjusted-coefficient record is evaluated separately as the relevant element of `Sigma_XX^-1 Sigma_XY`, with its own stated regressor set and intercept represented by centering. Two separately age/sex-adjusted coefficients do not become structural coefficients in a joint BMI-plus-glucose equation. Pearson uses raw covariance; continuous-margin Spearman uses the Gaussian-copula identity `6/pi * asin(R/2)`. The rank identity is unavailable for tied/discrete operands, and no covariance-only claim identifies rank association. CHNS MIND use is therefore a law-specific derivation, not a call claiming the generic source-moment helper can recover Spearman. MIND mean-filling and original rank ties are not reproduced: its continuous, smoothed rank interpretation is an explicit approximation, not strict original-study replay.

At extreme deterministic quadrature nodes, inverse-CDF probabilities use a floating-point endpoint safeguard to avoid infinite numerical integration values; order 64 is checked against order 128. This numerical integration approximation is recorded separately from generation. The sampler never clips probabilities or generated measurements: an endpoint, overflow or support violation fails the physical attempt without repair or redraw.

The numerical objective minimizes `-log(det(R))` subject to the individually declared source point constraints and positive definiteness. This is a conventional entropy-completion criterion, not a new inference method. The constrained numerical solve is local: source-constraint satisfaction and numerical checks are verified, but a global optimum is not certified. Incompatible constraints fail explicitly, with residuals; they do not acquire hidden tolerances or become apparently exact fits. Numerical scaling is not precision weighting. No SE, sampling variance or calibrated uncertainty distribution is manufactured.

With E0 and no supplied relational constraints, this criterion yields independence within each source component. E1 genuinely uses the admitted supported relationships below. Missing associations and independent binary sex remain named model assumptions. The reference may consequently fail an intended analysis; that outcome is retained.

## Fixed source normalization

| Input | Predeclared numerical use |
|---|---|
| Positive individual mean and SD | Lognormal moment fit; SD is never treated as an SE |
| Jansen native IFCC HbA1c mean and SD | Positive IFCC lognormal transformed by `percent = 0.09148 * IFCC + 2.152`, represented as a shifted lognormal; this preserves positive native IFCC support |
| Rounded Jansen percentage summaries | Alternative representation/diagnostic, not duplicate constraints in addition to the canonical native-IFCC information |
| Jansen glucose mean and SD | Upper-truncated positive lognormal, fitted to the source moments before dependence fitting; upper boundary is 7 mmol/L or the explicit 126 mg/dL conversion |
| Bao positive median/Q1/Q3 | Unweighted least squares on the three log quantiles; every residual is retained rather than asserting exact simultaneous agreement |
| Source age mean/SD | Uniform interval `mean +/- sqrt(3)*SD`; this is a bounded approximation, not a recovered empirical age law |
| Bao age quantiles | Unweighted three-quantile uniform fit with all residuals retained |
| Source sex counts/fractions | Explicit female Bernoulli fraction; named category and rounding convention follow the actual packet |

The age approximations must respect the declared source bounds checked in the recipe; no silent replacement follows a support failure. The source-law input moments describe a qualified selected-source scenario, not an unselected parent subsequently filtered to change its moments. Unknown selection variables, assay differences, source weights, anemia/diagnosis details and source sampling uncertainty remain limitations. These declarations do not assert strict reconstruction of any survey or original study estimator.

## Four construction bindings

| Cell | Numerical relational use | Target transport |
|---|---|---|
| CHNS E0 | No supplied relationship constraints; all three source margin components retained | Equal-probability Jansen/Bao/MIND donor mixture; age uniform over requested integers 35-74; donor-specific external female fraction |
| CHNS E1 | Separate Jansen BMI and FPG projections, Bao Pearson, MIND Spearman; each in its own source context | The identical donor/marginal transport rule as E0 |
| ENSANUT E0 | Jansen margins; no supplied relationship constraints | Jansen biomarker donor; exact requested eight age/sex cells, 375 rows each, age uniform over integers within each band |
| ENSANUT E1 | Separate Jansen BMI and glucose projections on the explicitly converted task measurement scale | The identical donor/marginal transport rule as E0 |

For CHNS, all Jansen/Bao/MIND source relationships enter their own fitting constraints; no pooled cross-source error criterion is used. An equal source mixture is an explicit target scenario, not an estimated CHNS mixture. The reference does not invent CHNS age/sex observations or add a disease-mixture parameter fitted to its exposed outcomes.

For ENSANUT, the source operator uses its source age law and source sex fraction. Target quotas are used only for target sampling. The sampler assigns the requested age/sex cells, positions each integer age within its target CDF mass and uses the conditional Gaussian copula for the continuous biomarkers. Jansen glucose support is already below 126 mg/dL; post-fit clipping and row deletion are prohibited. Fasting, diagnosis, pregnancy/lactation and measurement restrictions remain transport/applicability assumptions where they are not identified by the source law.

**ENSANUT Pani limitation:** all Pani age-coefficient and age-band-mean records remain available in the admitted packet and are explicitly logged as contextual/unfitted by this reference. The packet does not bind the individual HbA1c dispersion, exact source age law or original survey weighting needed for a source-law completion. Age-band SEs are not individual SDs; target quotas are not source quotas. No target SD or target coefficient is inserted to fill these gaps. This reference therefore does not claim full numerical Pani uptake. Its actual uptake is reported beside every Agent's uptake. Removing this qualification would require a newly reviewed pre-construction source-law assumption; no such additional fitting is included here.

The fixed five-Agent-versus-one-statistical-specification allocation is asymmetric. This reference permits a descriptive same-input comparison and interpretation of construction variability; it does not by itself establish general algorithmic superiority or an equal-search-budget contest.

## Verification and remaining release requirements

Thirteen invented analytic tests passed. They cover separate versus joint coefficients, the closed-form Gaussian entropy completion, unit rescaling, lognormal Pearson versus rank association, positive native-scale offsets, bounded source-moment fitting, inconsistent constraints, unavailable input rejection, quadrature against an analytic identity, and a complete invented source constructor through sampler-parameter validation with random generation patched to raise. A static sampler check confirms that its imports contain no filesystem/network or fitting module.

Earlier test failures were retained in the development history: integer-valued input variances initially created an integer covariance array and truncated fractional covariances; explicit floating-point construction fixed that implementation defect. A later shifted-moment test used exact floating equality; it was corrected to a numerical-tolerance assertion. Independent static review identified that the diagnostic constructor object was not the harness provenance ABI; the explicit packaging wrapper now separates the trace and validates the model specification against the existing validator. No clinical fit or generated table was affected because none had run.

Before execution, the independent reviewer and controller must bind these modules, the exact case packets/tasks, source operator qualifications, final seeds and failure accounting to the immutable campaign release. The clinical fitter and all samplers remain unexecuted in this unit. This specification neither enables the campaign nor enlarges the 120-attempt cap. No new data, sources, target effect access, API purchase, training or HPC is involved.
