# M13 body-fat target protocol: independent review

2026-10-30. Reviewer: `/root/m13_protocol_review`. Status: proposed executable statistical specification, not an approved freeze or an evaluation result.

**Current M13-A scope is source-only:** two builders operate on a clearly invented qualification grid, with no real target download. The target rules below are recommendations for a later separately frozen evaluation. No executable target evaluator is required in M13-A.

No target participant rows, raw DXA outcomes, target results or target association summaries were acquired, read or evaluated for this review. Reads were restricted to the three requested local admission/exposure/evidence notes, source-operator documentation and prior evaluator **code**. Two official codebook requests extracted only category codes/descriptions for `DXAEXSTS` and `RIDRETH3`, suppressing frequencies; survey-method documentation was also consulted. No target sample size was computed or inferred. This is a new-outcome transport proposal in a previously used survey cycle, not a fresh-cohort claim.

## Recommendation and boundaries

Proceed with a small assumption-dependent transport pilot after a source packet and the following rules are frozen. Its operational endpoint is NHANES 2017–2018 `DXX_J.DXDTOPF`, in percentage points. Direct application of source models is the declared zero-additional-measurement-bias assumption. It does not assert scanner/software equivalence. Do not add five percentage points, apply a universal Lunar correction, or estimate a measurement adjustment using target outcomes. The source-to-target measurement and population changes remain inseparable possible causes of disagreement.

Use one common, source-mappable race domain for the main Agent/reference comparison: non-Hispanic White and non-Hispanic Black participants. This narrows the scientific claim but avoids pretending that Gallagher's Japanese indicator can be recovered from a broad Asian category. If an all-race Thai-only target is preferred, that is a different admissible protocol, with a separately restricted Gallagher reference; it must replace this choice before outcome acquisition, not become a post-result sensitivity.

## Target domain, covariates and missingness

Build the survey-design frame from **all** DEMO_J records with finite positive `WTMEC2YR` and nonmissing `SDMVSTRA`/`SDMVPSU`. Keep this frame intact for variance estimation, including children, adults outside the requested range and PSUs with no domain members. Join components by `SEQN` only inside custody. Nested `(SDMVSTRA, SDMVPSU)` identifies a PSU.

Define the common eligible domain `D` by all of:

- `20 <= RIDAGEYR <= 59`;
- `RIAGENDR` is 1 or 2; `BMXBMI` is finite;
- `RIDRETH3` is 3 or 4;
- `DXAEXSTS == 1` and `DXDTOPF` is nonmissing and finite;
- complete allowed covariates and valid positive examination weight/design fields as above.

`DXAEXSTS=1` means whole-body scan completed; code 2 means completed but invalid and is excluded. Requiring the published endpoint to be present handles invalid/missing total-body measurements even when a scan exists. Eligibility is frozen from metadata; the custodian applies it without reporting target values. Do not add outcome outlier trimming, regional-validity rules, diabetes/medication exclusions, fasting restrictions or inferred health exclusions absent from this contract. An impossible endpoint outside `[0,100]` is a custody/data-integrity failure to investigate, not a discretionary row deletion. [Official DXX_J documentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DXX_J.htm).

Define `D_primary = D & (18.5 <= BMI < 30)`. If Gallagher is admitted before freeze, also define `D_extension = D & (30 <= BMI <= 35)`. These disjoint domains are reported separately; never pool them to rescue a primary result. Thai evidence alone does not support the extension. Do not include BMI below 18.5 or above 35. The extension is a transfer test under Gallagher's upper BMI limit, not proof of general obesity coverage. Source replay retains the sources' own age/BMI support; the target's age cap must not become a universal schema constraint that truncates the Thai source ages.

Missing permitted covariates or missing endpoint/valid scan exclude a record from the corresponding domain, with no imputation or new nonresponse weighting. Custody later reports a deterministic exclusion flow and weighted/unweighted completeness within the age/race/BMI sampling frame. The estimand is the examination-weighted complete-covariate, valid-scan domain. MEC weights do not by themselves repair DXA nonresponse or identify the distribution among all eligible adults. This restriction must appear in result titles, not only limitations.

Future real-target builder whitelist: `record_id` (opaque, arbitrary key), `age` (years), `male` (`RIAGENDR=1` maps to 1; `RIAGENDR=2` to 0), `bmi` (kg/m²), and, if used by the declared model, `race_group` (`non_hispanic_white` or `non_hispanic_black`). The evaluator uses this race coding for adjustment even if a generator ignores it. Both builders receive the same permitted columns. No builder receives `SEQN`, survey weights, design variables, scan flags, validity/missingness reasons, DXA masses, regional or subtotal values, DXA percentages, BMC, DXA-derived anthropometry, or a residual calculated from any of them. Exclude the entire DXA measurement family by an explicit whitelist rather than deleting only `DXDTOPF`. These variables remain evaluator-only; no additional evaluator-only clinical endpoint is needed for this pilot.

For **M13-A source qualification only**, base inputs `age`, `bmi`, `male`, `asian` and deterministic original-Gallagher design columns are compatible with this boundary. Validate reciprocal BMI and interaction columns as exact functions of those permitted base inputs. The source `asian` flag denotes the source's Japanese indicator, not an inferred NHANES Asian mapping. A later restricted real target can set the Gallagher indicator to zero and recompute the same deterministic columns. Never derive them from measured fat or use invented qualification rows as a reconstruction of actual source participants.

## Ethnicity and published-equation mapping

| NHANES `RIDRETH3` | Protocol use | Gallagher equation-1 indicator |
|---|---|---|
| 3, non-Hispanic White | Included in common domain | `A=0` |
| 4, non-Hispanic Black | Included in common domain | `A=0` |
| 6, non-Hispanic Asian | Excluded from common domain | Unresolved: not a Japanese identifier |
| 1/2, Mexican American/other Hispanic; 7, other including multiracial | Excluded from common domain | Unsupported mapping |

The source includes white participants at US/UK sites and African Americans at the US site; all source Asian participants were Japanese examined in Japan. Mapping source race/ethnicity terms to the two NHANES categories is still a transport assumption, not genetic ancestry equivalence. No evidence licenses a fitted race-specific residual, a race correction, or use of `A=1` for every non-Hispanic Asian participant. The rural Thai source transfers across population and measurement context even in this restricted US domain. Label that explicitly. Metadata labels were confirmed against [DEMO_J](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DEMO_J.htm); source context comes from the screened Gallagher evidence and original pp. 695–696.

## Fixed weighted estimands

Let `w_i=WTMEC2YR_i`, `Y_i=DXDTOPF_i`, `M_i` indicate male, and `R_i` indicate non-Hispanic Black within the common domain. Every generated table replaces only `Y_i`; weights, covariates, row alignment, domain membership and estimators are identical. No observed/generated percentile trimming or analysis-specific regeneration is allowed. Use percentage points throughout, without log/exponential transforms.

**Mean and adjusted associations.** For each sex separately in the primary domain, report the weighted mean `mu = sum(w*D_s*Y)/sum(w*D_s)` and the weighted least-squares projection:

`beta = argmin_b sum_i w_i D_si [Y_i - x_i' b]^2`,

where `x_i = [1, B_i, A_i, R_i]`, `B_i=(BMI_i-24)/5`, and `A_i=(age_i-40)/10`.

The prespecified association estimands are `beta_B` (percentage points per 5 kg/m², age/race adjusted) and `beta_A` (percentage points per 10 years, BMI/race adjusted). They are descriptive weighted projection coefficients; the model is not assumed to equal the true conditional expectation and the age coefficient is not longitudinal aging or a causal effect. The race term controls compositional differences; its coefficient is not a scheduled biological claim. A missing race category or otherwise rank-deficient design makes this model not computable rather than triggering a revised formula.

**One response-shape check.** Fit the same sex-specific projection with `B^2` added. Report the fixed second difference at BMI 20, 24 and 28, at common age and race:

`C_BMI = m(28) - 2*m(24) + m(20) = 1.28 * beta_B2`.

Age and race terms cancel. This is a projection-shape summary, not an individual prediction or a source calibration target. Positive/negative denotes convex/concave fitted shape over the fixed four-unit steps; do not call it a clinically meaningful effect merely because its sign matches. Avoid a data-selected spline, breakpoint or grid. If the extension is active, report its sex-specific means and the same linear age/BMI projections, but do not attempt this wide-span curvature contrast wholly outside its support.

**Unfitted conditional distribution panel.** In the primary domain use exactly eight cells: sex (male/female) × age (20–39, 40–59) × BMI (`[18.5,25)`, `[25,30)`). For every estimable cell `c`, define:

`F_c(y) = sum_i w_i D_ci 1(Y_i <= y) / sum_i w_i D_ci`,

`Q_c(p) = inf{y: F_c(y) >= p}`, for `p=0.25,0.50,0.75`,

`IQR_c = Q_c(0.75)-Q_c(0.25)`.

Sort values ascending, aggregate ties, and return the first observed value whose cumulative normalized weight reaches `p`; no interpolation or random jitter. This differs deliberately from the source engine's unweighted type-7 quantile and must be named in output. If the extension is active, add exactly four sex × age cells with BMI `[30,35]`. Race is pooled within each cell, with the same target composition in generated and measured calculations. These are coarse-bin conditional distributions: IQR includes remaining age/BMI/race variation within a cell and must not be labelled a pure residual SD. The panel tests reused distributions that were not direct source-fitting targets; it does not show that all conditional quantiles are identified.

No tail thresholds, AUCs, extra correlation panels, race-stratified subgroup searches, individual prediction scores or post hoc clinical cut points are necessary for the minimal experiment. An individual predictive draw is not a point estimate of a person's true fat percentage.

## Survey uncertainty and sparse cells

The prior `work/source-feedback-2026-10-28/custodian/nhanes_tg_j_v2/survey_analysis.py` already implements a reusable weighted projection with full-frame, zero-contribution domain scores. Reuse its mathematical kernel; do **not** copy its fasting weight, log outcome, exponential/ratio reporting or TG endpoints.

For a projection, set `A = sum(w*D*x*x')`, `U_hj = sum_{i in PSU(h,j)} w_i D_i x_i (Y_i-x_i'beta)`, and:

`V(beta) = A^-1 [sum_h m_h/(m_h-1) sum_j (U_hj-Ubar_h)(U_hj-Ubar_h)'] A^-1`.

All full-frame PSUs contribute, including zero-score PSUs. Global rescaling of weights changes neither point estimates nor this variance. For a contrast `c`, use `SE=sqrt(c'V c)` and `estimate +/- t_(df,0.975)*SE`, with `df = number of domain-represented PSUs - number of domain-represented strata`. Use an intercept-only version for means. Fail on a full-design singleton stratum; do not silently apply an undocumented lonely-PSU correction. The proposed domain treatment and reduced subgroup degrees of freedom follow [NCHS variance guidance](https://wwwn.cdc.gov/nchs/nhanes/tutorials/varianceestimation.aspx). No finite-population correction is introduced.

For quartiles use a small Woodruff implementation, reusing the same intercept-only survey kernel. At `qhat=Q_c(p)`, fit the weighted mean of `Z_i=1(Y_i<=qhat)` in cell `c`; call the estimate `fhat` and standard error `s_f`. Invert the probability-scale interval `[fhat-t*s_f, fhat+t*s_f]` through the same weighted inverse ECDF. Use cell domain degrees of freedom and `t=t_(df,1-alpha/2)`. If either probability bound is outside `[0,1]`, or a nondegenerate probability variance cannot be estimated, retain the point estimate but mark the interval unavailable; do not clamp the interval to manufacture precision. The point quartile rule, probability convention, handling of ties and this boundary rule must be tested and frozen. This is an approximate survey interval, consistent with the probability-scale approach documented for [`survey::svyquantile`](https://search.r-project.org/CRAN/refmans/survey/html/svyquantile.html), not a claim of exact finite-sample coverage.

Report pointwise 95% intervals for quartiles. For a conservative nominal 95% IQR interval, first obtain **97.5%** intervals `[L25,U25]` and `[L75,U75]` for the two quartiles, then report `[max(0,L75-U25), U75-L25]`. This Bonferroni construction avoids treating the quartiles as independent and avoids introducing a density estimator or a bootstrap framework. If either component interval is unavailable, mark the IQR interval unavailable. Do not calculate a standard error for IQR by summing marginal quartile variances. These approximate intervals are not simultaneous coverage across the entire panel.

Freeze the following pragmatic reporting safeguards, explicitly as protocol choices rather than universal NCHS thresholds. For any sex/domain projection or distribution cell require unweighted `n>=30`, Kish weight-dispersion diagnostic `n_K=(sum w)^2/sum(w^2)>=20`, at least eight contributing PSUs and domain `df>=4`. Projections additionally require full rank and positive residual degrees of freedom. The Kish number ignores clustering; it is a warning screen, not the inferential sample size. A failed cell is retained in the output schedule as `not_estimable` with the failed criterion and counts, without merging cells, changing bins, relaxing the criterion or choosing a different sex/race domain. The same covariate/design gate applies to every generated table and the reference. Point-estimate availability and interval availability remain separate flags when the Woodruff step itself fails.

**Generated–measured differences.** Report signed and absolute errors in the native units for every estimand. For means, linear coefficients and quadratic contrast, exploit the common rows and common linear operator: run that operator on `Y_generated - Y_measured` to obtain the paired survey difference and its conditional design interval. Do not add independent measured/generated variances. For quartile and IQR errors, report the point discrepancy, the measured reference interval and simulation variation separately; omit a formal discrepancy interval in this minimal implementation. Reference-interval inclusion is descriptive and is not a hypothesis test of Agent equivalence. No aggregate success score or effect-size tolerance is implied; any such tolerance would need scientific justification and freeze before access.

Measured-reference intervals describe design sampling uncertainty within the declared valid-scan domain. A generated table's optional design interval conditions on that frozen model and realized draw; it excludes source coefficient uncertainty, omitted source dependence, model construction variation and measurement/population transport uncertainty. None is an individual prediction interval. The existing evaluator should not be presented as fully survey-validated merely because it imports successfully: its code records invented-fixture checks but no R survey cross-validation.

## Builders, source loop, references and one release

Use two independently instantiated builder contexts with the same screened source packet. They must not see one another's outputs, target outcomes, evaluator results or prior unscreened target-paper snippets. Source evidence and source-only feedback may be used under a fixed revision budget. Each builder retains one primary scenario and at most one additional scientifically motivated scenario. Freeze each scenario's complete model, source dependence, individual residual law, support handling and measurement assumptions before any target evaluation. Scenarios are alternatives, not probability-weighted posterior draws; do not force a second scenario when evidence supplies no meaningful alternative.

Use three prespecified residual seeds per retained scenario, for at most `2 builders x 2 scenarios x 3 seeds = 12` final **Agent** tables. Reuse each table for the whole analysis panel. Seeds must not change the source calibration, conditional mean specification, eligibility or target covariate rows. Never concatenate draws or builders into a larger sample. For each endpoint show all three draws and their arithmetic mean and min/max by builder/scenario; these summaries describe conditional Monte Carlo variation. Keep scenario and builder comparisons separate, with no pooled confidence interval and no Rubin multiple-imputation combination. Three seeds do not supply a calibrated simulation interval, and twelve tables do not create twelve clinical datasets.

At minimum include the locked Gallagher equation-1 mean reference on the common domain, with `A=0` and `M=male`:

`m_G = 76.0 - 1097.8/BMI - 20.6*M + 0.053*age + 154*M/BMI + 0.034*M*age`.

The full source equation retains its Japanese terms in source documentation; omitting them here follows the restricted domain. If Gallagher is not admitted, there is no BMI 30–35 extension and the deterministic reference is the Thai development equation:

`m_T = -10.672 + 1.648*BMI + 0.065*age - 15.3*male`.

Do not mix or average the two equations into an allegedly validated population model. The deterministic reference may show nonzero within-cell IQR because covariates vary inside bins; it still has no individual residual distribution. If feasible before freeze, add the Gallagher mean plus independent Gaussian error with source SEE 4.31 percentage points as a labelled homoscedastic stochastic reference. Reject and redraw values outside `[0,100]` under a frozen truncated-normal rule; state that this changes the mean near boundaries and that SEE is not coefficient or transport uncertainty. Use the same three declared seed identities and row order, without implying that different generators' random numbers represent the same latent physiology. This is a reference assumption, not evidence that target residuals are normal or homoscedastic.

Specify the comparator budget explicitly: twelve is the maximum number of Agent tables; one deterministic reference and, if admitted, three stochastic reference realizations are additional scheduled comparisons. They may be evaluated without retaining participant-level exports, but must not disappear from the experiment count. If a total-table cap of twelve is intended instead, reduce the Agent scenario budget at freeze rather than quietly exceeding it. Preserve the primary reference choice and every comparison regardless of which performs best.

A later target phase requires generator, evidence, source feedback, scenario/seed roster, domain, evaluator and output schema hashes plus a technical audit before custody acquires/quarantines DXA outcomes and evaluates. M13-A does not authorize that phase. Return the whole scheduled aggregate release together once. Failed cells, failed scenarios and technical failures remain in the release. Outcome-informed regeneration, new residual tuning, new race maps and selective scenario retention require a new reserved task; this target cannot continue as the development set for its own confirmation claim.

## Minimal implementation work and pre-access checks

No change to the general source-statistic engine is required. Keep its unweighted source-context estimands distinct from this target evaluator. A small custodian script can adapt the prior survey kernel, add a weighted inverse ECDF/Woodruff helper, define the fixed domains/design matrices, and write one structured aggregate report. Keep preparation, generator execution and target evaluation separate through the existing contract/receipt pattern. No new generic survey framework, omnibus ranking metric, spline search, latent ethnicity model or scanner-calibration adapter is required for this pilot.

Before target access, use invented fixtures to verify: percentage-point outputs without old TG transforms; full-frame domain variance with an empty-domain PSU; weight-rescaling and row-permutation invariance; nested PSU handling; paired-difference identity for linear contrasts; the `1.28` curvature multiplier; weighted inverse-ECDF ties/boundaries; sparse-cell flags; and the conservative IQR bound calculation. Cross-check the WLS mean/variance and Woodruff quantile conventions against one established survey implementation using invented fixtures if available. If cross-validation is unavailable, record that limitation and require independent formula/code review before running this custom extension; do not substitute target-data debugging. Also verify whitelist rejection of extra DXA-family columns and exact row-key agreement for every generated realization.

This note specifies the minimum scientific analysis. It neither freezes the execution budget nor authorizes data acquisition by itself. The controller must resolve and record the common race-domain choice, comparator cap, retained source package and concrete seed list in the machine-readable contract before the one target release.
