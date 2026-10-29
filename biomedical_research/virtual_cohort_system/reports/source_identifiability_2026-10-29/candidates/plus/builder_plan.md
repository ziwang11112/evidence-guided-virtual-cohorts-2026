# Source-only conditional-identifiability pilot: builder plan

Status: construction authorized, 2026-10-29. The original design was completed without generator calls or candidate construction. The supplied synthetic-probe task now authorizes building, static validation and freezing of zero/minus/plus; generator execution remains controller-only after independent review. The controller schedules and audits; the builder owns the scientific construction and parameters.

Binding implementation amendment: task `tg-source-identifiability-synthetic-probe-2026-10-29` has zero source queries/downloads and **zero revisions**. Therefore the optional implementation-repair round mentioned in the original design below is not available after freeze. Source seeds are 78101, 78102, 78103; synthetic-probe seeds are 78201, 78202, 78203. Materiality is the **maximum** absolute analytical plus-minus conditional mean difference over the four fixed male cells age {40,60} by BMI {23,27}, with threshold 5 mg/dL; it is not a requirement that all four exceed 5. The numerical tolerances below were design suggestions, superseded by the controller's separately committed descriptive gate (under review: 3 times the historical source-seed SD per check). No scientific parameter will change in response to that gate or execution output. The candidate includes exact semantic metric definitions for both arithmetic and geometric Table 2 interpretations. This amendment and the complete plan are copied into all three freezes.

## Recommended smallest experiment

Use one source-conditioned anchor and three prespecified labels: **zero, minus, plus**. They share the same positive conditional TG law except for a bounded age-by-BMI interaction in the male conditional density. The perturbation preserves, in the declared product source population, the entire age–TG and BMI–TG bivariate distributions. This is stronger than merely fitting a finite list of marginal summaries, and avoids a distribution-family-label comparison.

The practical question is whether these deliberately different conditional laws remain indistinguishable by the admitted source summaries and their approximated replay contexts. It is not whether the anchor is established as correct, nor whether a target association changes in a desired direction. There are no new real outcomes in this pilot.

Use the existing `s1_final` construction as a transparent anchor, not as a validated winner. Its code, specification, evidence and source feedback are within the allowed source-only boundary. The anchor has visible source misfits, detailed below. A successful pilot can establish numerical non-distinguishability relative to that anchor under declared assumptions; it cannot confer calibrated source admissibility or target validity.

## Admitted evidence and what it constrains

- Oh2019, Healthy Twin Study, Korea: 2,672 people, 1,029 men and 1,643 women; medication exclusions and family/twin structure. At least 12-hour fasting EDTA plasma; Cobas 6000; glycerol blanking is unreported. Table 1 arithmetic TG means/individual SDs are 141.6/107.7 mg/dL for men and 97.2/61.0 for women. Category counts below 150, 150–199, 200–499 and above 500 are 704/130/185/10 and 1401/131/110/1. These are source distribution constraints, not coefficient uncertainties.
- Oh Table 3 gives the age/sex-adjusted raw TG–BMI coefficient 6.813 mg/dL per kg/m², CI [5.853, 7.774]. This is the one replayed item with a reported sampling CI. It is not a log coefficient, sex-specific coefficient, fully adjusted coefficient, or causal effect. Family and exact analysis details remain approximated by replay OLS.
- Oh Table 2 contains real additional evidence even though the current replay does not numerically interpret it. Male age-stratum TG values for ≤29, 30–39, 40–49, 50–59 and ≥60 are 143, 147.5, 140.6, 143.5 and 128.1. Female values are 78.1, 80.7, 89.4, 127.8 and 135.3. BMI strata <20, 20–23, 23–25, 25–30 and >30 have male values 91.8, 109.4, 141.4, 165.3 and 220.5 and female values 73.8, 86.5, 100.9, 126.7 and 127.3. Their arithmetic/geometric interpretation is unresolved: methods mention geometric averages, while count-weighted strata closely reconstruct the arithmetic Table 1 TG means. Both interpretations must remain visible.
- Oh Tables 4–6 have different adjustment/design estimands (including missing metabolic variables, mixed/family structure and co-twin contrasts). They cannot be silently converted to the available age/sex/BMI model. They remain evidence with unassessed compatibility.
- Bansal2007, initially healthy US women aged ≥45, fasting subset n=20,118, fasting ≥8 hours; EDTA plasma and glycerol-corrected assay. Fasting median/IQR are 115 [81,169] mg/dL; TG–age and TG–BMI **Spearman** correlations are 0.18 and 0.33. Tertile/quintile counts and reverse-conditional age/BMI mean/SD provide additional constraints. No sampling intervals for these replayed summaries are supplied. Every female generated value remains paired and identical across the proposed labels.

The full text, not only extracted replay items, was reviewed. A source-table anomaly was also identified: Oh Table 2 FBS-stratum entries labeled TG reconstruct fasting-glucose means near 95.0/89.7 rather than TG means 141.6/97.2. Do not use these as resolved TG constraints without an approved correction. This issue does not license dropping the age/BMI evidence.

Source locators: `agent_bundle/sources/oh2019_fulltext_readable.txt`, Table 1 and lines 308–388/Table 2; `oh2019_tables_extracted.json`; `bansal2007_article_body_web.txt`, embedded L176–L201 and Tables 1–3. Keep existing admitted hashes and exact version selection; do not create new source approvals.

## Explicit construction

Let a=age, b=BMI, and y=legacy-proxy TG in mg/dL. Retain the anchor's mean m(a,b,s), mean-one lognormal residual and technical assay mapping. In particular, for males:

`linear_mean = 141.6 + 9.557309727577666*(b-24.4) - 0.2*(a-43.9)`

`m = 15 + 8*log(1 + exp((linear_mean-15)/8))`

`CV = 0.7153743796657551; sigma² = log(1 + CV²)`

Thus f0(y|a,b) is lognormal with log location `log(m)-sigma²/2` and log SD `sigma = 0.642864579657887`. All female settings stay exactly those of `s1_final`.

Define two compact, source-centered bases:

`hA(a) = (9103/18693)*I(35 <= a <= 44) - I(55 <= a <= 64)`

`hB(b) = (10388/14851)*I(22 <= b < 24) - I(26 <= b < 28)`

Both are zero outside these explicitly declared regions, and absolute values are at most one. The counts were read from the permitted frozen Oh covariates, among 61,740 male source rows: age regions 18,693 and 9,103; BMI regions 14,851 and 10,388. Therefore each base has exactly zero marginal average on that fixed source file. These are source context counts, not target observations or clinical evidence.

Define the signed TG density kernel:

`hT(y) = I(70 <= y <= 120)/50 - I(140 <= y <= 190)/50`

Endpoints have zero probability under the continuous model. Its integral is zero, and its first moment is 95−165 = −70 mg/dL. Let H be its integral: zero below 70, `(y−70)/50` on [70,120], one on [120,140], `(190−y)/50` on [140,190], and zero above 190.

For label t in {0,−1,+1}:

`f_t(y|a,b,male) = f0(y|a,b) + t*delta*hA(a)*hB(b)*hT(y)`

For women, use f0 exactly. There is no source/cohort/assay-label switch in the biological law, no use of identifiers, no row rearrangement, and no fitting to a target covariate distribution. The existing assay map, if required by the future task, is applied after this legacy-scale draw and has no role in selecting the interaction.

These are explicit sensitivity constructions. The papers do not estimate the interaction kernel, its amplitude or its probability. Piecewise density changes are a diagnostic model class, not a claimed mechanism or clinical latent group.

## Analytic normalization, positivity and separation certificate

Normalization holds for every individual covariate combination because the integral of hT is zero. The following bound also proves nonnegative densities; it is not a grid-search assertion.

Across the compact active covariate rectangles, a conservative enclosing rectangle is a in [35,64], b in [22,28]. The anchor softplus mean is monotone increasing in b and decreasing in a, so its range is enclosed by the opposite corners:

- `m_low = 114.64248782964219` mg/dL;
- `m_high = 177.78631503091927` mg/dL (b=28 is included only for a conservative bound).

For fixed sigma, log lognormal density is concave jointly in log(y) and log(m). Its minimum over each rectangle formed by these mean bounds and either TG band is attained at a vertex. Evaluating all mean endpoints and TG endpoints {70,120,140,190} yields:

`d_min = 0.0017692554532692901 (mg/dL)^−1`, at m_low and y=190.

Choose, before any generator execution:

`delta = 0.8 * 50 * d_min = 0.07077021813077161`.

Since |hA*hB|≤1 and |hT|≤1/50, the perturbation magnitude is at most 0.8*d_min on its support. Therefore both f_minus and f_plus are at least 0.2*f0 on that support and equal f0 elsewhere. Genuine continuous residual variation remains. Store this derivation and corner values in a frozen analytic certificate and recalculate the same formulas independently during implementation review; do not tune delta using generated output.

The conditional mean difference is exactly:

`E_plus(Y|a,b) − E_minus(Y|a,b) = −140*delta*hA(a)*hB(b)`.

Its maximum absolute value is **9.907830538308025 mg/dL**, attained within age 55–64 and BMI 26–28. This lies inside the reconstructed source support, not only outside an artificial source range. A predeclared analytic materiality criterion of at least **5 mg/dL** on a nonempty interior rectangle is met. This is a practical model-separation criterion, not a clinically validated threshold or confidence statement. The three labels do not request any sign of a later regression or scientific conclusion.

## What is preserved, and under which assumption

For the declared male source population, assume age and BMI are independent with the same frozen marginal laws used to center hA and hB. Integrating the density perturbation over BMI gives zero for every a and y; integrating over age gives zero for every b and y. Consequently the following **population** quantities are exactly shared by all labels:

- complete joint law of age and TG, and complete joint law of BMI and TG;
- TG marginal distribution, all its moments, thresholds, quantiles and tails;
- every age-only or BMI-only TG-stratum distribution, including arithmetic or geometric means and either quantile interpretation;
- covariances of TG with age and BMI and, because predictor laws are unchanged, the source OLS projection onto intercept/sex/age/BMI;
- all female laws, hence all Bansal diagnostics.

The three-way age–BMI–TG conditional law is different. Pairwise laws do not determine this three-way dependence. This is a concrete unidentified degree of freedom conditional on the specified covariate-population assumptions.

The existing Oh file was formed by independently permuting finite marginal samples; it is **not** an exact Cartesian-product population. Exact centering of each marginal does not imply exact empirical independence or exact cancellation within every finite age/BMI stratum. Replay must quantify these finite-context residuals. The analytical invariance is not a proof that the actual Korean cohort had independent age and BMI. Unknown source joint covariates, family links, omitted predictors and cross-cohort transport remain substantive limitations.

Preserving the anchor's source discrepancies does not cure them. Nor does preserving available age/BMI/TG pairwise laws establish compatibility with jointly adjusted or family-based estimates involving unavailable variables.

## Implementation route using the existing isolated adapter

Use the generator program route and existing `generate(observed, spec, seed)` contract. Put all scientific constants, compact basis bounds, density kernel, centering fractions, delta and label into the specification with evidence/assumption provenance. Do not modify historical candidates or harness core.

Prefer common-uniform inverse-CDF coupling, which reduces finite seed noise and gives exact paired invariants:

1. Draw the anchor's normals for all rows in the same order for every label; construct the same baseline TG values first. No extra random draws are required.
2. Return the baseline for label zero. For minus/plus, modify only active men whose baseline TG lies strictly inside [70,190]. All female rows, men outside the active age/BMI rectangles, and baseline TG outside that interval retain their exact original draw.
3. Set `u = Phi(z)` using the same normal draw. Solve `F0(y|a,b) + t*delta*hA*hB*H(y) = u` on [70,190] with 40 vectorized bisection iterations. Standard-library `math.erf` supplies Phi, with NumPy for arrays; no additional package is essential. Positivity proves the CDF is strictly increasing. The bracketing width gives at most 120/2^40 ≈ 1.1e−10 mg/dL numerical interval width, apart from ordinary floating-point evaluation.
4. Apply the common measurement equation only as the task requires, then preserve every observed cell and row order.

Oh <200 and <500 event indicators are then identical per paired row, because all changes remain inside [70,190]. Both labels still retain full individual residual variation. A rejection-sampling implementation with envelope 1.8 is mathematically available but is not preferred: it would add avoidable paired Monte Carlo noise and consume different random draws.

The generator runs only through the supplied WSL/bubblewrap adapter after freeze. An unavailable backend is a stop, never a local execution fallback.

## Bounded source-only schedule and gates

This design deliberately uses **zero numerical scientific fitting rounds**: the scientific amplitude is selected from a positivity bound and the interaction is centered with source covariates only. It is a matched-anchor experiment, not three independently tuned distributions. Do not disguise a fixed anchor as a newly fitted optimum.

Before build, the controller supplies the task/protocol, exact source replay seeds and approved budgets. Recommended schedule: three labels × three fixed paired source seeds × two existing contexts = 18 isolated source-context executions. The first seed can be an early failure check, but all three seeds belong to the frozen schedule and none may be replaced after inspection. Keep original evidence, source contexts, recipe and semantic assumptions identical across labels so the portfolio comparison is valid.

One implementation-repair round is permissible only if the future task authorizes it and an actual contract, numerical inversion or execution bug is found. Preserve failed candidates/receipts and bind feedback. Do not adjust the kernel, amplitude, source contexts, calibration weights or acceptance limits to rescue a failed scientific comparison. If science-level source drift fails the gate, stop and report it. A later redesign requires a new declared study, not silent retuning.

Gate components to freeze in the protocol:

1. Contract validity, verified execution success and source-output linkage for every scheduled run; input/row preservation; no undefined scheduled statistic silently removed.
2. Exact paired equality of female generated values and Bansal diagnostics; exact equality of Oh female values, <200/<500 indicators and all covariate-only inputs across labels. These are implementation invariants, not empirical biomedical tests.
3. Report all 46 existing source checks: 12 covariate-only construction checks and 34 TG-dependent diagnostics. Preserve absolute discrepancies against literature, paired differences against zero, every seed result and generator-seed spread.
4. Suggested **descriptive paired drift limits** for altered male summaries: absolute portfolio-mean difference versus zero ≤0.75 mg/dL for TG mean, ≤1.5 mg/dL for TG SD, ≤0.003 for TG<150 proportion, and ≤0.10 mg/dL per kg/m² for pooled BMI OLS. Require no seed to exceed twice its limit. All exact invariants above retain zero tolerance except stated floating-point representation. These are engineering comparison tolerances, not sampling confidence limits, inverse-variance weights, probabilities of correctness or equivalence-test margins. The design cannot claim statistical equivalence from three seeds.
5. Add a source-only semantic supplement for all 20 Oh age/BMI stratum TG entries, reporting the generated arithmetic **and** geometric means under explicitly alternative interpretations against the same printed values. Do not relabel the evidence as exact arithmetic/geometric. Under the product model both versions are invariant; on the finite context compare each perturbation with zero and retain discrepancies. Suggested paired drift limit: 1 mg/dL for each interpretation, with any exceedance investigated rather than omitted. The supplement can calculate statistics from verified replay output without modifying harness core and must bind output/candidate/report hashes. It cannot truthfully claim the current declarative operator verified a geometric mean.
6. Report the other three extracted unsupported Oh estimands and any further full-text constraints as unassessed, with the missing covariates/design explained. Neither lack of an operator nor ambiguity removes evidence from the scientific ledger.
7. The analytic 5 mg/dL conditional-separation criterion must remain met. The proposed covariate-only probe (ages 20–79, BMI 18–40, balanced sexes, ten replicates, all legacy_proxy) is only a structural illustration. Report the analytical law and simulated summaries separately: ten replicas per point are not precise estimates of each conditional expectation. Do not treat probe agreement as population validation or use it to choose amplitude/sign.

If the existing anchor is judged too discrepant for a substantive source-agreement claim, stop at a **diagnostic-coverage demonstration**. If the paired gate fails, report that this finite implementation/context did distinguish the alternatives. Either outcome is informative and permits stopping before any target outcome evaluation.

## Existing source-fit obstacles that must remain visible

The permitted `s1_final_portfolio.json` already shows, averaged over its three historical source seeds:

- male TG mean 141.25272 versus 141.6 and SD 107.46684 versus 107.7;
- male TG<150 proportion 0.66472 versus 0.684159, and TG<500 0.98664 versus 0.990282;
- pooled BMI OLS 6.84006 versus 6.813;
- Bansal quartiles/median 76.68495/111.58464/162.29614 versus 81/115/169;
- Bansal age/BMI Spearman 0.14405/0.34640 versus 0.18/0.33;
- Bansal top-tertile age SD 8.02981 versus 7.2, and top-tertile BMI mean 27.96470 versus 27.6.

The larger source contexts and seed repetitions reduce simulation noise; they do not increase the number of people studied or resolve these discrepancies. The proposed perturbations leave Bansal unchanged by design. All absolute discrepancies must be presented next to matched-anchor results. No confidence interval is manufactured from replay row counts or generator-seed ranges.

Calibration weights, if later needed in a different study, would be optimization choices. Here no aggregate mixed-unit score, no inverse-variance weighting and no inference of source-study precision is used. The only reported replayed sampling CI belongs to the Oh BMI coefficient; being inside it would not validate the rest of the joint distribution.

## Scope, estimates and stop point

Estimated implementation/audit effort after receipt of contract: 45–90 minutes for the three compact candidate bundles, proof/certificate, inverse-CDF static review and semantic supplement; approximately 10–25 minutes for the 18 source-context executions and verification/portfolio work, depending on adapter overhead. These are planning estimates, not benchmarked runtimes. The generator itself should plausibly fit a 60-second/1,024-MB limit per existing source context: roughly a few hundred thousand scalar erf evaluations plus array operations. A timeout is retained and investigated through the approved adapter only.

The minimum experiment is the three shared-anchor labels above, using existing evidence and contexts, one complete paired schedule and no scientific refitting. A two-label minus/plus comparison would save runs but loses a useful numerical zero control; keep zero for today's pilot. Do not expand to unrelated model families or new baselines before this bounded test is decided.

An initially considered age residual-copula rotation was **abandoned before construction**. Although it could preserve TG/BMI marginals under a product population, it could change the real Oh age-stratum evidence. Unsupported replay operators do not make that evidence disappear. The density-interaction construction was selected because it preserves both relevant bivariate laws in the same mathematical population.

Only approved source artifacts, source candidate code/spec/evidence/decision/recipe and source feedback, allowed covariate-only source files, and the harness/skill interfaces were read. No project README/milestone reports, target outcome data, target evaluations, custodian directories, other chats, web associations or historical generated target tables were read. The only calculations performed for this design were source-covariate counts and the explicit analytic lognormal positivity/separation bound. Await the task contract and approved protocol before candidate building or freezing.
