# Which scientific analyses can the current virtual data support?

8 November 2026. Retrospective diagnosis of existing cases; no new clinical validation.

The method's purpose is to turn published evidence, a population description and optional observations into virtual biomedical data that researchers can analyze. The relevant unit of utility is a specified analysis under a specified information condition. A dataset can support one analysis and fail another. We therefore retain the complete results and separate demonstrated reconstruction, partial external-reference agreement and currently unsupported uses.

## Current scientific-use map

| Case and information condition | What the existing records support | What is not yet supported | Leading diagnosis and implication |
|---|---|---|---|
| CHNS summary-assisted generation; 30 target summaries legitimately supplied | Reconstruction of the supplied adjusted regressions and Pearson/Spearman relationships. Three Agent laws and the statistical comparator produce analyzable records with close values for the highlighted source constraints. | Transfer to a new population, reconstruction of every unprovided feature, or superiority over statistical calibration. | Information-rich reconstruction works. This is a positive capability example, not an independent target prediction. |
| HRS published-model reconstruction; coefficients and method code supplied | A full longitudinal table with conditional variables, four visits, subject effects and the requested mixed-model analysis. The lower-branch age–HbA1c interaction is negative in all three Agent draws. | Exact significance preservation, a stable upper-branch point sign across implementations (Agent 3/3 positive, corrected published-law reconstruction 0/3), or recovery of the original high-HbA1c subgroup distribution. | The valid programs encode the correct interaction sign. Deterministic source-law integration explains much of the distribution mismatch; finite-draw uncertainty remains relevant for the weak upper interaction. |
| External-evidence glycemia, especially Q5 | All three Q5 laws reproduce the requested effect directions. Constructor-mean age coefficients are 0.0995–0.1009 versus 0.0751 per decade; BMI coefficients before glucose adjustment are 0.0489–0.0603 versus 0.0836 per 5 kg/m². After glucose adjustment they are 0.0194–0.0510 versus 0.0566; H03 is closest on that endpoint. Outcomes are HbA1c percentage points. | Treating the closest coefficient as evidence that the entire table supports quantitative inference, dispersion-sensitive analyses or power calculations. H03 SD is 0.3523 versus 0.5274; residual RMS is 0.3006 versus 0.4885. | H03's narrow distribution is implied by its declared source/shape/transport choices, rather than an established coding mistake. More seeds will not change its population law. |
| External-evidence iron status; threshold counts and band summaries supplied | Positive threshold association for both laws. A has joint-low prevalence near the survey-weighted sample reference; B has continuous rank correlation near that reference. These are different model-specific successes. | A universal winning model, accurate target threshold OR, or independently established transport of the Chinese source law to US women. | Both source replays reproduce OR about 6.65, while the survey-weighted target OR is 17.79. A's transfer assumptions further weaken the association. Source fit and target applicability are separate. |
| External-evidence Turkana lipids, including Q5 | Negative adjusted HDL–BMI direction across the retained Q5 laws, with explicit finite-moment joint generators. Raw tables support the requested regression computations. | Reliable residual TC–HDL dependence: constructor-mean generated correlations 0.108–0.141 versus reference 0.512. Positive TC points are not a securely established population direction because its reference sensitivity interval crosses zero. | Pooled source Spearman correlations are transferred through a copula and within-sex assumptions; they are not direct evidence for the requested adjusted Pearson dependence. Current records do not uniquely separate evidence transport from joint-law misspecification. |
| Earlier prospective HAALSI | Both main-effect point directions agree across 15 Agent draws; the experiment provides a genuinely prospective, explicitly scoped check of the earlier method. | Claiming the full wave succeeded: only 3/5 constructions met the primary rule, versus the required 4/5; only 8/15 draws matched the interaction sign, and zero effects also satisfied the coarse primary margin. | Preserve the original stop. Main effects and interaction have different evidence requirements; a post-hoc relabeling of “pass” would not improve the method. |

“Near” above describes the displayed values; no new equivalence margin, clinical acceptance threshold or calibrated reliability label was introduced. Reference point estimates are finite-sample estimates, with the uncertainty and selection qualifications retained in their original reports. No model is selected retrospectively as a universal best method.

## What is implementation, and what is evidence?

There are verified historical implementation/model defects. The initial HRS comparator extraction overwrote seven coefficient/SE pairs across text sections; its corrected recovery and original failed tables remain documented. Iron A initially had an upper tail with divergent variance; its source-only revision repaired the mathematical tail while preserving threshold/rank analyses. These are real fixes, not proof that final scientific scores improved.

The current prominent discrepancies are different. A source-supported regression slope does not determine target residual variation. A banded cross-tabulation does not determine all continuous within-band ranks. Pooled rank correlation does not become an adjusted raw-unit Pearson correlation without additional assumptions. A small or weak reference coefficient may change point sign between legitimate finite samples. Each requires its own evidence and analysis; the available records do not justify calling all discrepancies bugs or all of them sampling noise.

We therefore improve the method's use of evidence in three concrete ways before proposing another generator change:

1. For each intended analysis, state which exact source quantity constrains it, including adjustment, population and measurement. Mark a bridge or shape assumption explicitly when the needed quantity is absent.
2. Check the mathematical implications of the chosen law for both associations and variation. If an observed output follows the declared law but differs from the clinical reference, changing the sampler is not a demonstrated repair.
3. Keep source reconstruction and external-reference analysis side by side. Report when one succeeds and the other does not, so a user can choose a supported analytical use without assuming the whole table has passed a universal quality test.

These are refinements to scientific construction and reporting, not a new agent hierarchy, an additional training objective or a proven performance-improvement component.

## Targeted checks completed in this unit

The case audits and deterministic checks examine the frozen programs and existing aggregate results. No authored generator is imported or executed, no participant rows are read and no new clinical effects are fitted. See the linked records below for actual checks, numerical results and qualifications. All earlier frozen laws and data remain unchanged.

- [Glycemia audit](GLYCEMIA_AUDIT.json): source-to-coefficient use and H03 variance decomposition.
- [Iron and lipid audit](IRON_LIPID_AUDIT.json): source counts, target transport and adjusted joint dependence.
- [Reconstruction and prospective audit](RECONSTRUCTION_PROSPECTIVE_AUDIT.json): summary-assisted generation, HRS and HAALSI.
- [HRS source-law mathematical check](HRS_DETERMINISTIC_AUDIT.json): deterministic integration of the existing recursive law; no sampled table.
- [Age-profile sensitivity](AGE_PROFILE_SENSITIVITY.json): all eight already-admitted Pani age-specific means and upper quantiles, checked against the original table.
- [Independent algebraic checks](INDEPENDENT_CHECK.json): separate root calculations of H03, iron transformations, L03 projections and the HRS truncated-Gamma identity.

The new age-profile calculation is an important negative design result. Under a normal-within-age approximation and the requested equal-band/uniform-year age weights, all eight source mean/97.5th-percentile pairs imply mean 5.38167 and SD 0.32904. The unchanged H03 law implies mean 5.41980 and SD 0.35162. The complete profile therefore does not raise H03's overall spread in this calculation. It can inform age-specific location/tail modeling, but it is not a demonstrated remedy for narrow target dispersion. The source's >=70 category includes older people than the task's 70–79 band; source survey weighting, eligibility and the normal-shape bridge remain assumptions. Mean plus one quantile does not identify variance. This calculation generated no records and did not fit a target value.

## Next experimental decisions

**First priority: conditional variability under the intended eligibility and age design.** The existing packet does contain age-specific means and upper quantiles, but the completed sensitivity does not support using them as a simple variance repair. Before a new candidate, resolve the intended selection and assay context and seek an actually reported individual or residual scale, or richer distributional evidence. A source-profile candidate can be justified for an age-specific analysis request; it must also reconcile the separately reported adjusted effects and distinguish marginal age spread from residual heteroscedasticity. The known target SD is not a parameter to copy. If evidence is insufficient, retain dispersion-dependent uses as unvalidated rather than force a match.

**Second priority: adjusted joint dependence.** The lipid need is an age/sex/BMI-conditioned relationship or sufficiently detailed joint evidence, not another marginal mean or another unadjusted rank coefficient. A future evidence update should test that specific gap while preserving already supported margins and associations. The current residual target value must not be supplied as an external source constraint.

**Do not repeat the completed extra-instruction trial or add random seeds as a substitute for this evidence.** The ordinary Agent already solved the earlier exact-moment fixture. Existing HRS/iron defects have documented recoveries. No present finding warrants another architecture layer or target-informed parameter correction.

This unit ends with the analysis-specific diagnosis and reviewed mathematical checks. Any subsequent source-supported candidate must have a separate frozen construction protocol. Evaluation on these already revealed cases can only be developmental; a claim of new-population reliability requires a genuinely independent reference.

## Minimal next experiment specification

No blanket method rewrite is justified by this audit. The next new construction should address one of two explicit inputs, chosen by evidence availability rather than target fit:

| Candidate question | Evidence required before construction | Agent freedom and fixed checks | What a successful result would establish |
|---|---|---|---|
| Can an age-aware cohort preserve both the published conditional associations and age-specific variability? | Compatible age-stratified location/tail summaries plus a defensible dispersion or shape specification, with explicit selection and weighting. The eight available Pani pairs alone do not prove residual heteroscedasticity. | Agent chooses structure and may retain an earlier family or report incompatible constraints. Check all adopted source projections, nonnegative variance components, all age groups and final analysis effects; do not optimize against a revealed target SD. | Better source-profile coverage under stated assumptions. Quantitative target utility would remain a separate question. |
| Can a virtual lipid cohort preserve the requested adjusted joint relationship? | A matching adjusted covariance/correlation or enough joint information to derive it, with population/measurement transfer recorded. Existing pooled rank correlations are insufficient by themselves. | Agent chooses a dependence structure; retain mean/SD and regression checks alongside the residual-correlation check. Do not insert the known target residual correlation. | A stronger evidence-to-joint-analysis construction; improvement in a new population requires independent evaluation. |

If neither evidence requirement is met, retain the current capability paper with its demonstrated uses and limitations. Additional synthetic rows or decorative components would not answer the identified questions.
