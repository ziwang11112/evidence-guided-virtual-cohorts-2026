# Independent audit of the complete Claude review

28 October 2026. This audit checks the complete user-supplied Claude review against the frozen briefing, sanitized source and aggregate reports. The review offers useful design choices, but its arithmetic, mechanism explanations and proposed statistical procedures have different evidential status. Correct descriptive calculations do not establish a calibrated uncertainty method or an identified cause of failure.

Input: `CLAUDE_REVIEW_USER_SUPPLIED.md`, read in full, lines 1–378. SHA256: `8da64cb08b397f5a8332245ca9c60f70a0ceba793998285dc3634e5d3a68f20f`.

This review used local source inspection and arithmetic on already saved aggregate results. It ran no generators, new experiments, reference fits or participant-level analyses, and changed no frozen artifact. Primary literature, access conditions and venue assertions are being assessed separately; they are not independently certified by this document. Claude explicitly disclosed that it could not access the private repository, inspected the two supplied attachments and performed only arithmetic. Its response should not be described as an executed repository audit.

## Overall assessment

Retain the distinction between broad analytical feasibility and a demonstrated method advantage. Retain the suggestions to test source transfer, represent uncertainty beyond residual draws, and assess whether a generator can state what its output supports. The proposed source operators, ensembles, support labels and measurement-equivalence experiment are candidate methods, not already validated contributions.

The strongest corrections are:

- The HDL table arithmetic is correct, but point estimates falling inside a reference interval and an ensemble range containing a reference are descriptive diagnostics, not calibration or equivalence tests.
- The code has documented procedural isolation and real static-check gaps. The review found no evidence of actual target access or misuse by the inspected generators.
- Source adjustment mismatch and restricted age shape plausibly explain attenuated age effects. Their separate contributions have not been identified experimentally.
- Gaussian source weighting, parameter draws, variance-based support labels and empirical interval coverage need additional statistical specification. They cannot be adopted as an automatic calibration recipe.
- No-retrieval superiority, measurement savings, an uncertainty method and absent-column enrichment are possible paper claims or scope choices, not four compulsory requirements for the entire research idea.

## HDL arithmetic verified against saved aggregate results

Source files: `evidence_gap_loop_2026-10-28/custodian/results/endpoint_summary.csv`, `all_endpoint_draws.csv` and `RESULTS.md` in the sanitized repository. The calculations below use final medians over five residual draws per construction. They are not fresh model results.

| Endpoint | Final construction medians inside the reference 95% interval | Four-construction min–max contains reference estimate | Min–max width divided by reference interval width |
|---|---|---|---:|
| Crude BMI per 5 | None | Yes | 2.773 |
| Adjusted BMI per 5 | None | Yes | 2.701 |
| Adjusted age per 10 | Ordinary2 | No | 1.188 |
| Female minus male | None | Yes | 3.069 |
| BMI slope at 35 minus 25 | None | No | 1.527 |
| Female minus male BMI slope | All four | Yes | 0.517 |
| Male BMI slope | Ordinary1, Ordinary2, Gap2 | Yes | 1.309 |
| Female BMI slope | None | Yes | 2.443 |

Therefore Claude's **4/28**, **6/8**, and approximately **1.2–3.1** width ratio for the seven resolved endpoints are correct. The four hits are Ordinary2 age and the male BMI slopes from Ordinary1, Ordinary2 and Gap2. All four interaction medians fall within the unresolved reference interaction interval. The primary-effect ratios approximately 0.75, 0.77, 1.37 and 0.82, curvature ratios approximately 0.10–0.60, and near-flat age ratios approximately 0.06–0.13 for three builds also agree with the saved table.

These quantities need four qualifications:

1. The 28 pairs reuse seven overlapping analyses of one cohort and four constructions. They are not 28 independent validation studies.
2. A generated point estimate outside a real-data 95% interval is neither a two-sample significance test nor failure of a prespecified scientific equivalence margin. The reference has sampling uncertainty, and its interval is not a universal tolerance for synthetic utility.
3. A four-build min–max is not a 75% or any other nominal confidence/credible interval. It has no stated sampling or probability interpretation, and shared source choices can leave all builds wrong together.
4. Seven endpoint signs matching in four constructs establishes this pilot's sign agreement. It does not establish general reliability across biomarkers or populations. The claims remain stronger for broad supported directions than for curvature or modifiers.

The real interaction interval overlapping zero remains unresolved evidence. It is not a known zero effect. None of these diagnostics proves biological absence or population false-positive rates.

## Source and implementation claims

| Claude claim | Audit finding |
|---|---|
| Freeze checks bind candidates, revisions and gateway registration | Supported by `loop_control.py::freeze_candidate`, including hash checks and the accepted-artifact registry. This verifies structural provenance, not truth of each derivation. |
| Execute preserves observed cells, inputs and global RNG; same seed reproduces | Substantially supported. The controller checks copied frames and spec, NumPy legacy global RNG, output round trips and repeated execution of the first scheduled seed. It is not a universal check of all possible process state or every seed. |
| Reference is opened after all 40 outputs validate | Supported by evaluator order in `run()` and `validate_release()`. This is the evaluator's access order, not proof that no process could previously read the shared filesystem. |
| Full-spine Taylor scores are zero outside the analysis domain | Supported by reindexing PSU score totals to all spine strata/PSUs with `fill_value=0`. The real cohort has target members in every PSU; the empty-domain-PSU edge case was checked with artificial fixtures, not exercised by that real comparison. |
| Static checker omits `loadtxt`, `genfromtxt`, `read_fwf` | Supported by inspection of allowed imports and `blocked_attrs`. In-process `exec_module` also exists. These are credible isolation limitations; no exploit was executed and no misuse was found in the inspected generator source. |
| Ordinary1 and Gap2 use the same Taiwan age vector, held constant outside its knots | Supported. Both use `[0, .75841, 1.18484, .87361]` at ages `[35, 45, 55.5, 65.5]`; `np.interp` clamps outside the knot range. The maximum spread is 1.18484 mg/dL. Their centering and BMI continuation differ. |
| Age results therefore establish adjustment-set mismatch as the cause | Too strong. The source adjusts for more variables than the target BMI/age/sex analysis, and the limited/clamped age curve is a plausible contributor. Source population, selection, covariate distribution, projection of nonlinear BMI effects, centering and residual Monte Carlo variation also matter. No ablation isolates their contributions. |
| Gap2 has six unresolved gaps of seven | Correct: location, shape, age, variance, tails and transport are unresolved; causal/time-series structure is not applicable. This is an honest underidentification record, not proof that all six cause target error or that the labels have measured predictive value. |
| Gap2 asymptotes and decay are assumptions | Correct. Floors 30 and 38 mg/dL have no evidence IDs; decay .04 has qualitative source context but its numerical value is explicitly assumed. The tail derivative at BMI 30 is −.5300 for men and −.5224 for women, agreeing with Claude's approximately −.53. |
| Gap2 did better because its assumed tail was steeper | Plausible, not demonstrated. It also differs from Ordinary1 in the last BMI anchor, source-age centering and spread treatment. A full-cohort regression is a weighted projection over the entire observed predictor distribution, not its derivative at one anchor. |
| Ordinary1's extrapolated tail comes from the −.33 clinic-subgroup coefficient | Correct as a local derivative in the chosen exponential continuation. Its tail form and extrapolation remain assumptions. Its category means also undergo age-centering; a claim that the primary coefficient is determined by only two numerical inputs omits the rest of the predictor distribution and model. No sample fraction in the extrapolation region was established by this review. |
| Five seeds only change residual draws within each fixed build | Correct for this HDL pilot. Across builds, some structure/source variation is present, but there is no calibrated probability distribution over it. “Dominant” source/transport uncertainty has not been quantitatively decomposed. |
| No uncertainty is reported | Incorrect literally. Real survey intervals, conditional synthetic intervals and residual-draw ranges are reported and clearly qualified. The defensible criticism is missing comprehensive source, structure and transport uncertainty. |
| Gap policy could act only in prose | Incorrect as a statement about its capabilities or actions. It retrieved papers, re-extracted statistics, ran source checks and sensitivity diagnostics. Both gap builds made no numerical generator revision. These facts support no demonstrated revision benefit, not an inability to act beyond prose or a general refutation of the policy. |
| Insulin's no-interaction assumption produced a sex-slope difference of zero | Correct only as a structural tendency, not the observed estimate. The saved report gives median .006, range −.045 to .058, and one positive conditional interval; covariate/model projection and residual draws can produce nonzero coefficients. The reference difference is −.109. |
| Stage 1 generated confident relationships where the reference was unresolved | Supported, with the report's qualification: this is unsupported-evidence discrepancy, not an observed population false positive. |
| PDF extraction blocked at least two Gap2 leads | Supported as two documented format barriers: UK/Malawi numeric supplement and Mexican sex/BMI table. Other leads were excluded by study-alias screening, which a PDF reader would not solve. Format support does not guarantee usable conditional evidence. |

The scientific relationships and numerical constants in these generators were chosen by the builder Agents and declared in their submitted code/specifications. Fixed code at execution time is not evidence that the coordinator hand-coded the intended relationships. The controller enforces contracts; it does not supply HDL coefficients.

## Proposed evidence weighting and parameter ensembles

The observation-operator idea is useful: define what each paper actually measured and analyzed before treating its statistic as a constraint. Several unresolved requirements remain.

**Compatible operators need missing source information.** Recreating an adjusted coefficient or group statistic may require source covariate distributions, correlations, selection, measurement mappings and adjustment covariates that the paper never reports. The operator must record which components are assumed. A replay on an invented midpoint population is an assumed diagnostic, not exact replication of the source. Source replay used for fitting is also not independent validation.

**The product of Gaussian terms is an approximation with assumptions.** Multiple estimates from one table, papers reusing the same cohort, or outcomes measured on overlapping people are dependent. Multiplying marginal likelihoods as independent double-counts evidence. A covariance-aware block likelihood or explicit dependence sensitivity is needed. If the intended weights are posterior/importance weights, the prior on structures/parameters and the sampling proposal must be specified; arbitrary particles cannot simply receive a likelihood product and automatically become a posterior. Simulation error in each operator also needs control or representation.

**A variance term cannot generally repair bias.** A source-tier or adjustment-mismatch category is not itself an empirical transport variance. Population and measurement mismatches can induce directional shifts, nonlinear distortions or nonexchangeability. Increasing a zero-centered Gaussian variance makes a model more tolerant but does not correct the estimand. A missing operator should not automatically become a direct parameter prior with a larger variance: a group mean, standardized association and conditional raw-scale slope can be different mathematical objects. Independent normal draws also need parameter constraints and covariance to preserve valid scales and coherent joint models.

**Shared outer uncertainty is a useful design, not a guarantee.** Drawing source/model/transport parameters once per generated cohort separates shared uncertainty from individual residual noise. Under a suitable parameter distribution, an estimand's between-draw variation can persist as numerical sample size increases. It need not persist for an estimand insensitive to those parameters, and variation does not guarantee honest coverage. Missing structural alternatives or biased source bridges can still yield a narrow, wrong ensemble. Preset alternative weights are sensitivity weights until their meaning and calibration are established.

Claude's M1 comparison is therefore worthwhile only after defining the inference target and probability model. Compare fixed-generator, parameter/structure ensemble and independent-builder ensemble with comparable actual budgets and adequate draws. K independent builds may cost more than parameter sampling; “the cheaper builder ensemble” is an unmeasured assumption. Shared sources and model priors also make builder disagreement an incomplete measure of uncertainty.

## What uncertainty and support would mean

The next protocol must choose among at least three targets: the unavailable values/statistic for this finite cohort, a descriptive parameter of the target population, and a future measured cohort's statistic. Their uncertainty differs. Across-draw variation conditional on observed X is not automatically survey sampling uncertainty for a population parameter. Evaluating intervals against one noisy real-data estimate is empirical agreement unless the task explicitly predicts that estimate; it is not known-truth frequentist coverage for the underlying parameter.

“Never report within-dataset SEs or p-values” is too broad. Conditional synthetic SEs can be valid diagnostics for the declared generator and may be components of an appropriately derived inferential procedure. They must not be presented as total uncertainty about an unobserved real population merely because many virtual rows were generated. Deleting them does not, by itself, make across-ensemble intervals valid. Similarly, the observed target sample size carries information about the X distribution, support and marginal functionals, although it supplies no direct measured Y information. Holding synthetic n equal to target n is a useful bookkeeping convention for enrichment, not a statistical calibration theorem.

M2's evidence-support proposal is worth investigating, with these corrections:

- A fixed but wrong assumption has zero ensemble variance. Variance share alone can therefore give it no warning despite large bias.
- Correlated parameters and interactions prevent unique additive attribution without an explicit convention. Reparameterization can change individual shares while leaving the generated distribution unchanged.
- Directly extracted coefficients can be poorly transportable; assumptions can be harmless for a particular endpoint. Provenance category is not an error probability.
- AUROC measures ranking/discrimination, not calibration. It needs a predeclared failure definition, a numeric score or ordering, held-out tasks and clustered uncertainty. If probabilities are claimed, reliability or proper probability scoring is additionally needed; precision–recall and risk–coverage curves may matter for rare failures and abstention.
- Gap2 already labeled nearly every applicable component unresolved. Saying a new scheme “would have flagged” known failures is a post hoc possibility; it does not establish incremental discrimination. The key test is whether it prospectively distinguishes usable from fragile analyses better than simpler support checks.
- Leave-one-source-out assessment must hold out source clusters when papers overlap and must refit/rebuild without the held-out evidence. It measures transfer among available source studies, not guaranteed transport to the target population.

Point generators still have uncertainty when supported by evidence. A useful interface could report an estimate with its support and separate uncertainty components, rather than reserve ranges exclusively for “unsupported” analyses.

## Identification and scope statements requiring qualification

The review correctly emphasizes that aggregate evidence usually does not identify individual conditional relationships. Its wording sometimes overextends that point.

**Individual agreement is not universally capped by an unspecified R².** Under squared loss, the conditional expectation is the optimal predictor and residual conditional variance gives an irreducible MSE. A squared-correlation ceiling requires a specific definition. Independently generated residuals do not recover a participant's unknown realization. These are precise limitations; they are not a single upper bound for every agreement metric.

**Unconditioned variables need a dependence model.** If generated Y is drawn independently of Z given X, the construction imposes a conditional-independence restriction. Marginal Y–Z associations can nevertheless arise through X, and a misspecified linear adjustment for X need not yield a zero coefficient for Z. More generally, extra joint evidence, latent structure or restrictions can narrow a statistical-matching identified set; it is not universally limited to only one named pair of bounds. Curvature, interactions and thresholds are often underidentified from coarse moments, rather than logically impossible when additional compatible constraints exist.

**Absent-column enrichment is a clean task definition, not clean identification.** Starting with use case B makes the information boundary easier to describe; it does not identify p(Y|X,target). A and C can remain part of the broad system, with separate protocols. A public-data benchmark can itself be a contribution; licensing does not force it to be a by-product.

**Literature-driven generators can propose previously unreported implications.** They cannot validate a novel biological mechanism by generating it. The absolute claim that they cannot reveal anything beyond the literature is too strong if it excludes hypothesis generation through evidence combination, followed by independent measurement or intervention. There is no current validated biological discovery in these pilots.

## Experiment design and decision thresholds

The information ladder is useful as an empirical comparison, but it does not causally separate translation from transport. Donors can differ in sample size, measurement, selection, year, available predictors and fitting method as well as population. If an external donor misses age and curvature, transport is a candidate explanation, not the uniquely identified cause. An informative decomposition would need nested controls holding other factors fixed, clear information tiers and overlap/selection diagnostics.

A no-retrieval arm tests incremental retrieval benefit in the chosen setup. A tie or loss does not prove pretraining contamination, nor does a win prove its absence. Restricted access and recent releases are risk controls, not categorical proof of no prior knowledge. Exact future assay values cannot be memorized beforehand, but related covariates, summaries and model priors can still be exposed.

No-retrieval superiority is necessary for a claim specifically about retrieval's improvement. It is not necessary for every paper about evidence-informed generation, analysis preservation or a useful benchmark. Similarly, a statistician baseline is highly informative but not a universal publication law. Direct row generation should be evaluated fairly rather than predeclared weak from unrelated studies. A direct-analysis Agent is an optional utility comparison; give it the same relevant information, numeric tools and target covariates. Allow it to answer new analyses when the generator is also queried. Reusability and coherence are empirical questions, not proof that rows are mathematically indispensable.

Claude labels the thresholds as proposals, which is appropriate. They still need redesign before preregistration:

- Nominal 80% intervals covering 60% can be a permissive exploratory gate; it is not calibrated 80% coverage. The 50%, 60%, 70–90%, 2× and 3× rules have no validation in the supplied record.
- Forty task–endpoint pairs are not forty independent replications when endpoints share participants, sources and model structure. Use the cohort/task hierarchy, clustered uncertainty and sensitivity by population/variable. Six tasks from two populations provide limited external replication.
- AUROC ≥ .7 and wins in 5/6 or 2/3 tasks are operational choices, not established standards. Uncertainty and effect size should accompany counts.
- Ratios to near-zero effects are unstable. Significance matching inherits reference power and threshold discontinuities. Define scientifically meaningful tolerances or decision losses before a fresh evaluation, with unresolved references kept separate.
- The proposed z denominator mixes reference SE and cross-population heterogeneity. It can be a descriptive scale if both have clearly defined roles, but it is not automatically a z score with a known null distribution. |z|≤1 does not necessarily mean “as close as a typical foreign cohort”: that requires an applicable, approximately centered heterogeneity distribution and estimation of its mean, measurement differences and uncertainty. Large heterogeneity can make the tolerance easy while the output remains practically unhelpful.
- WIS requires specified quantiles/interval levels and a defined predictive target. Scoring a real sample estimate versus a population parameter are different tasks. Normalization across endpoints and populations must be fixed before testing. Width plus coverage alone does not establish conditional calibration.
- The null generator needs an explicit information-consistent definition. A constant or independent-column null may help detect trivial performance, but it is not a substitute for a capable evidence-matched generator.
- Retrofitting M1 on HDL/insulin belongs in a new development version. Preserve frozen outputs, code and original interpretations. New tasks, not rerunning exposed endpoints, establish confirmation.

The proposed timings, staffing, dataset counts and venue thresholds are planning opinions. Access, compatible assays, usable covariates and whether task outcomes are already known must be checked before promising the timetable. An independent analyst choosing new analyses after method freeze is useful only with a documented protocol preventing outcome-dependent cherry-picking and separating exploratory from confirmatory analysis families.

## Measurement-equivalence and sample savings

The two-phase proposal is one of the more concrete utility ideas, but it changes the setting once real Y values are revealed. It tests a literature-informed prior or initializer updated by limited measurements, rather than pure zero-Y enrichment alone.

Define a performance level q using a prespecified task loss and an appropriate uncertainty criterion. For a fixed acquisition/update policy, a useful comparison is:

`Δk(q) = k_baseline(q) − k_literature(q)`.

If the generator with zero target outcomes matches a baseline at k observations, that k can be called a task-specific label-equivalent result, with uncertainty. It is not a universal effective sample size of the virtual cohort or a count of additional independent patients. Learning curves may cross, be nonmonotone or never attain q; negative savings, non-crossings and censoring at the maximum k must be reported.

Repeated subsample selection, a reserved evaluation set or explicit finite-cohort estimand, comparable predictors and model flexibility, source uncertainty, survey design/selection, and any active acquisition rule all need to be accounted for. Fitting and evaluating on the same revealed subjects would inflate utility. Under active selection, inclusion probabilities and positivity matter. Literature-guided updates can also harm performance under source mismatch.

Retrospective masking can estimate measurement efficiency in silico. A prospective assay study can test previously unexposed predictions. Neither automatically establishes actual laboratory cost savings or reduced patient recruitment. The suggested 100–300 specimens is not a power calculation. New HDL measurements are not intrinsically decorative; their value depends on the claim and genuinely new setting. A sparsely studied biomarker may offer a useful stress test but could also lack enough compatible source evidence to construct the method.

## Recommended adoption

**Keep now:** the audited pipeline, ordinary Agent as a viable method candidate, typed provenance, honest no-ops, analysis-level utility, separation of given and reserved relationships, and exposed-case labels.

**Design next:** a bounded evidence-matched comparison with a precise scientific/analytical user task; a versioned uncertainty prototype whose components and target are explicit; a small fresh task set with real source and population differences. The no-retrieval arm is useful to test retrieval's incremental contribution, without becoming the sole project-wide go/no-go condition.

**Test before claiming:** source-operator reliability, support-label discrimination and calibration, ensemble interval performance, and task-specific measurement-equivalence. Each can fail independently; no need to make all four compulsory features of the first implementation.

**Do not adopt literally:** automatic independent Gaussian weighting, arbitrary mismatch inflation, “no uncertainty was reported,” “policy could act only in prose,” a blanket ban on all conditional synthetic SEs, calibration from four-build ranges, or claims that information-ladder comparisons uniquely identify the failure cause.

The review is strongest as a careful reorientation toward tested analytical usefulness. It does not demonstrate the proposed fixes, guarantee publication, or justify rewriting the existing negative and mixed results.
