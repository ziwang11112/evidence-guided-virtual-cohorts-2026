# Independent checks of the complete Gemini review

28 October 2026. This is a critical assessment of the user-supplied complete review, not another experiment or a revision of existing results.

**Input:** `GEMINI_REVIEW_USER_SUPPLIED.md`, 61,826 bytes, SHA256 `6633bf9e444e77813bf8c934ccc076c9df767e6c563ec786d203186f9debddfb`.

The full document was read, including sections omitted by the first terminal output. Checks use the retained reports, exact committed source at `51d19b6a8fab07f774d0bd6032a2bb9a379595d8`, the previously reviewed source ledgers and the earlier partial-review assessment. No participant data were opened, no models were fit, and no experiment or frozen artifact was changed.

## Overall assessment

The review provides useful strategic direction: retain a capable simple Agent, evaluate the evidence-to-data method rather than require extra policy machinery, improve translation of study statistics into conditional models, and distinguish shared model uncertainty from individual variability. Its experimental prescriptions and mathematical guarantees should **not** be copied wholesale. Several central claims are overstated or incorrect, and some proposed success criteria are tailored to already observed HDL answers.

The strongest actionable ideas are source-context checks, evidence-matched comparators, distribution-sensitive downstream tasks, transparent support labels and a future measurement-efficiency experiment. These are candidate improvements with tests still needed. The automatic `OpCheck + Rubin + N_eff` package is not a validated solution.

## Source-level findings and corrections

| Topic | What is supported | What needs correction |
|---|---|---|
| Ordinary Agent as main method | Its workflow genuinely searches, selects evidence, writes a generator and undergoes source/code review. Added gap-policy benefit was not demonstrated. | Calling the gap machinery's value universally null is too strong. Two builds per arm in one cohort do not prove equivalence or general ineffectiveness. It can be deprioritized without a universal claim. |
| Agent decisions versus hard coding | Both representative programs contain fixed parameters and explicit interpolation choices. | These are Agent-selected source-derived or assumed parameters, not coordinator-written biological relationships. A compiled generator necessarily contains numerical constants. The issue is adequacy of evidence and uncertainty, not the mere existence of constants. “Hand-interpolated” risks misrepresenting who made the choices. |
| Cryptographic/static controls | Hashes, provenance references and release checks are real implementation assets. | They are not proof of secure blinding or scientific correctness. `source_check()` explicitly says it is a conservative AST check, not a sandbox or proof of no side effects. It blocks selected names/imports/attributes; it does not by itself establish universal file/network/global-RNG exclusion. |
| Parameter provenance | The controller requires matching provenance keys and resolvable evidence/assumption references. | `validate_spec()` does not execute derivation strings or prove a parameter's arithmetic. Gateway binding and semantic source review are distinct checks. Declared assumptions remain assumptions. |
| BMI-bin means as anchors | The programs interpolate reported category means at assumed BMI points. This is a real ecological-to-conditional bridge. | The review's precise attribution of target attenuation and curvature failure to that bridge is not demonstrated by an ablation. Its assertion that the source obese group is primarily BMI 27–32 is not established by the supplied category table. |
| Age clamping | Both supplied generators use a small age pattern and constant extrapolation outside the endpoint anchors. | This is a plausible cause of weak target age effects, not a quantified causal explanation. The review incorrectly adds triglycerides to Taiwan Table 3's adjustment set. Both retained ledgers list exercise, WHR, BMI, body fat, sex, smoking, drinking/alcohol, coffee and vegetarian diet, with no triglycerides. Log triglycerides appear in a separate Dallas source model. |
| Adjustment and mediation | Source age contrasts condition on more variables than the target model, so direct reuse requires a bridge. | Saying WHR/TG adjustment “blocks the mediating pathway” asserts causal structure not established by these cross-sectional summaries. Omitted-variable differences can change coefficients without proving a specific mediator mechanism. |
| Group SD as conditional SD | Source `SE*sqrt(n)` supplies group spread under the stated assumptions; conditional spread is not automatically identified. | Gap2 interpolates raw group SD; Ordinary1 interpolates source-derived log variance/CV and applies it to adjusted means. They are not literally identical SD equations. These are valid stochastic models with potentially incompatible source moments, not violations of the law of total variance. |
| Fixed draws | Parameters are fixed across the five residual draws. Source/model/transport uncertainty is not propagated. | The existing report explicitly labels synthetic intervals as conditional, so this is a limitation rather than an undisclosed numerical error. Whether interval widths are too small, too large or biased for a specified population target needs a defined repeated-sampling experiment. |
| Primary endpoint family | All eight HDL endpoints are weighted-linear-regression coefficient contrasts on raw HDL. | They mainly assess conditional means. Quantile/threshold/joint-function tasks are sensible additions. They must be prospectively added to a new protocol, not substituted after seeing the existing eight outcomes. |

## Recommendations that are useful after narrowing

**Source-statistic operators:** Ask the Agent to represent selection, measurement, covariate distributions, adjustment and the actual reported statistic. Fit or check a model through that operator, instead of treating a category mean as a pointwise conditional mean. However, matching source marginal demographics does not identify the source joint distribution. It may not permit the “exact statistical analysis” if adjustment variables or covariances are absent. Report an approximate operator or sensitivity model when needed. Reproducing fitted constraints is not independent validation; withhold compatible source summaries and target analyses where possible.

**Shared uncertainty:** One outer draw for evidence/model/transport choices, followed by individual residual draws, prevents a study-level shift from being mistakenly treated as independent person-level noise. This is conceptually useful. Parameter distributions must be justified or labeled sensitivity assumptions. Not every parameter needs randomization: known definitions may remain fixed. Related source coefficients, means and variances require compatible joint distributions; independent Normal perturbations can violate constraints. A reported confidence interval can motivate an approximate sampling model, but it is not automatically a transport posterior.

**Analysis-support audit:** Compare a downstream analysis with the model's conditioning variables, measurement mapping and assumed structure. Flag unsupported residual dependencies and extrapolation. Use descriptive labels such as `source_supported`, `assumption_dependent` and `unassessed`; a matching covariate list alone does not prove `DIRECTLY_IDENTIFIED` for a new population.

**Evidence-matched statistical comparator:** A competent parametric or summary-constrained generator using the same evidence is valuable. A single-paper shortcut is useful as a cheap baseline but cannot be the only strong statistical opponent of a multi-paper Agent. A direct-analysis Agent should receive equivalent observed information and access to numerical computation. Restricting it to means/covariances while the generator sees all real predictor rows would confound the comparison.

**PDF support:** The recorded unsupported supplement is a concrete capability gap. Add parsers with source-parent binding, quarantine and screening before display, extraction checks and explicit failure handling. A parser being installed does not establish reliable table extraction or preserve units/footnotes automatically. “One day” is an unverified effort estimate.

**Measurement utility:** A future preregistered virtual-before-assay study can provide useful prospective validation. An actual same-budget selection comparison can test measurement efficiency. Neither improvement, cost nor sample savings should be assumed before execution.

## Statistical proposals that must not be adopted as guarantees

### 1. Rubin pooling plus an effective-sample-size cap is not a general derivation

The review proposes `T = W_bar + (1 + 1/M) B` and multiplies `W_bar` by a ratio involving target and source effective sample sizes. This may be an exploratory heuristic, but it does not establish calibrated inference for evidence-only enrichment, whole synthesis and missing-cell completion simultaneously.

Appropriate combining rules depend on what is observed, what is synthesized, which uncertainty sources are already in each component, and the inferential target. Arbitrarily sampled parameter priors do not automatically yield proper multiple imputations. Source overlap, survey design, differing estimands and fitted constraints also prevent a universal scalar `N_source_eff`. Adding both parameter variation and a source-size inflation can double-count some uncertainty while missing other uncertainty.

As written, the cap uses `N_target`, not necessarily the increased number of synthetic rows; it therefore does not even specify a consistent rule for the proposed million-row experiment. More generally, a scalar variance floor cannot repair structural bias or missing transport assumptions.

Outer parameter uncertainty can remain when inner Monte Carlo size grows, **if the estimand is sensitive to the uncertain parameters**. It is not guaranteed for every estimand: under a delta approximation the contribution is `J Sigma J'`, which can be zero in directions to which the estimand is insensitive. Neither a positive parameter variance nor the proposed cap proves that false confidence is impossible.

The prior checked statistical reference, Reiter and Raghunathan (2007), explicitly discusses different combining rules for different adaptations of multiple imputation. See [the institutional abstract](https://scholars.duke.edu/publication/742204). This supports deriving or choosing an appropriate rule, not automatic rejection or automatic use of Rubin pooling.

### 2. A zero-centered interaction prior is not automatic abstention or false-positive protection

The selected scale and center are informative modeling choices. Such a prior does not ensure every pooled interval spans zero, nor does a zero-spanning interval prove a scientifically safe result. It can conceal a real interaction or create unsupported alternatives. Label the resulting inference as prior-sensitive and assess robustness/calibration in defined truth scenarios. Do not present the review's illustrative `−0.04 ± 1.15` interval as a calculated result.

### 3. Conditional independence does not force a coefficient to zero in every adjusted regression

If a generator samples `Y` using only `X` with independent residual randomness, it imposes `Y independent of W given X` in its probability model. That is a sound warning about unmodeled residual dependence. But the review's claim that a regression “adjusting for X” **always** gives zero W slope is false when the analysis models X inadequately.

An analytic counterexample requires no experiment: let X be centered Normal and let `Y = X^2 + epsilon` and `W = X^2 + eta`, with independent mean-zero noises. Y and W are conditionally independent given X. Regressing Y on an intercept, **linear X**, and W nevertheless gives W a positive population coefficient `Var(X^2)/(Var(X^2)+Var(eta))`, because W proxies the omitted nonlinear X effect. Correct conditional adjustment, finite-sample variation, weighting and model specification must be considered.

The proposed audit should warn “residual dependence with W was not modeled; inspect functional-form compatibility,” not promise an exactly zero coefficient or diagnose a known biological bias solely from a missing name in the conditioning list.

## Experimental criteria requiring redesign

1. **Twelve of sixteen is not calibrated nominal 95% coverage.** The sixteen HDL/insulin endpoints are correlated estimands from two cohorts, and real reference estimates are uncertain, not known population parameters. Counting intervals that include reference point estimates measures a finite agreement diagnostic. It does not establish repeated-sampling 95% coverage. Even as an operational screen, 75% is substantial nominal undercoverage rather than a defensible calibration target. Use known-truth repeated worlds or a justified resampling design and report uncertainty in coverage, widths and interval scores.
2. **Age ≥0.65 and curvature ≥2 are post-result targets.** These thresholds were selected after seeing true HDL results. They can be labeled engineering-development targets, but cannot serve as new independent evidence that the method works. The current locked analyses remain historical; they are no longer unexposed targets for further method selection.
3. **A NoRAG tie/win does not diagnose pretraining contamination.** It could reflect useful general knowledge, poor retrieval, irrelevant source estimates, transport failure, stochastic builder choices, or inadequate budget. It demonstrates no observed incremental benefit from that retrieval setup. It does not prove memorization of this dataset. Likewise, a RAG win does not prove absence of pretraining contamination.
4. **The NoRAG contract needs a truthful separate specification.** The existing controller requires nonempty source/evidence ledgers. Disabling the gateway while keeping the exact contract is not directly executable without an explicit revised ablation interface. Never fill fake source references to pass validation. Both arms should retain comparable generation freedom, review and observable budgets while exposing their distinct information regimes.
5. **Twelve cohort-variable tasks are not twelve independent study samples.** Several biomarkers from the same participants share covariates, physiology and source literature. Builds are nested within tasks; seeds are nested within builds. Separate study families are the stronger replication level, and claims should reflect dependencies.
6. **The four-arm proposal bundles causes.** Adding source operators and uncertainty simultaneously prevents attribution of benefit. A staged implementation check or modest factorial comparison is needed if the paper claims which component works. A useful end-to-end package can be tested first, but it should not claim isolated mechanism evidence from the bundled comparison.
7. **Country labels are not ancestry interventions.** NHANES is heterogeneous; KNHANES, CHARLS and CHNS differ in age, selection, geography, assay, medication, period and socioeconomic context. Their comparison can test cross-study/population transport. Calling it a clean matched-versus-cross-ancestry experiment confounds many factors. Quantile-aligning BMI can change the meaning of the exposure and needs an independently justified bridge.
8. **Numerical promises are hypothetical.** No 20–25% accuracy gain, source-to-target 15% heterogeneity constant, 30–80 observation crossover, 200-observation MICE dominance, $150 API bill, one-second runtime, or 50-versus-150 assay equivalence has been established here. The tasks may reveal different patterns; all must be labeled proposals or omitted.
9. **Synthetic rows do not necessarily add information, but may add usable representation.** A deterministic mean omits conditional variability, yet it does not always underestimate a particular threshold prevalence; the direction depends on where means fall relative to the threshold. The claimed HDL biological R-squared ceiling 0.12–0.18 is not established by the supplied materials. Measure selected task utility rather than assert a universal biological ceiling or necessity of rows.
10. **Actual no-reference deployment needs bounded claims.** Composite analyses such as HOMA-IR versus blood pressure can be useful tasks, but combining partial conditionals does not identify their full joint law. The review does acknowledge a conditional-independence bridge; its illustrative residual-correlation range `[−0.2,0.2]` is another assumption, not a verified bound.

## Publication, data and wet-lab recommendations

Focusing the first paper on absent-column enrichment is a reasonable strategic suggestion, not a requirement proved by the evidence. Whole-cohort generation and partial completion may remain broader scope or secondary demonstrations. A benchmark/resource contribution is not ruled out merely because the underlying data are public or restricted: access, task curation and reproducible evaluation are separate questions.

The journal tiers, task counts and “must beat” requirements are Gemini's opinions, not editorial rules. They do not establish novelty or acceptance prospects. The complete answer includes several direct primary links, but this task did not independently reverify every paper title, method scope or current venue status. The SASC row links a Google search wrapping a ResearchGate URL rather than a primary paper; groupings such as CML/GIM/GENMETA need precise individual citations. The stated method differences and claimed first-of-kind gap remain literature-review hypotheses.

Public-data routes are candidates, not verified ready-to-run cases. The availability of a named cohort does not establish unrestricted access, biomarker availability in the requested wave, sample size, compatible assay, joint glucose/insulin measurements, or an unexposed target. “Post-cutoff” requires an actual model version/cutoff and release/exposure audit; a recent calendar year alone is not proof.

A genuinely newly assayed specimen cannot have its future exact assay readout memorized beforehand, but that narrow fact is not “absolute proof against pretraining leakage” for all associated covariates, related assays, published summaries or study characteristics. Prospective measurement strengthens evaluation when the complete freeze and access process are maintained. Reagent cost, assay choice, sample adequacy and savings require collaborator and laboratory confirmation. Simulation does not substitute for patient measurements or establish recruitment savings.

## Recommended use of this review

- **Keep:** simple capable Agent as a candidate main method; source-statistic alignment; separation of shared uncertainty and residual noise; independent analysis tests; fair statistical baselines; explicit source/assumption support.
- **Develop cautiously:** PDF extraction, distribution-dependent endpoints, joint-variable tasks and future measurement selection. Each needs a concrete information regime and verification.
- **Reject as stated:** universal Rubin-plus-N_eff guarantee; automatic zero-centered-prior abstention; 12/16 coverage as nominal calibration; post-seen HDL thresholds as confirmation; NoRAG victory as proof of contamination; country-as-ancestry attribution; unsupported numerical cost/performance/biology promises.
- **Do not change frozen studies:** implement any accepted ideas in a new versioned development branch and assess the final chosen method on genuinely reserved material. Existing HDL/insulin outputs remain honest development evidence.

The review is useful as a set of testable suggestions. It is not a validated experimental plan, a proof of the proposed statistical correction, or permission to reclassify exposed results as confirmation.
