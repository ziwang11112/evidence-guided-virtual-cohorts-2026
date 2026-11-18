# Main-study parameter provenance audit

10 November 2026. Retrospective audit of the 20 CHNS/ENSANUT Agent constructions; no new experiment or manuscript revision.

## Finding

The existing records support a useful **evidence-to-parameter-to-analysis explanation**, but not the claim that five improved endpoints changed from ASSUMED to REPORTED, or that provenance categories already predict target error. CHNS's conditional-age endpoint improves at arm level without a supplied age relationship. ENSANUT's glucose-adjusted BMI endpoint remains a model-derived quantity depending on assumed residual covariance. The CHNS BMI deterioration cannot be attributed exclusively to population transport by this design.

The defensible storyline is: added relationship evidence constrained particular source functionals; authors chose different ways of completing and transferring those constraints; the resulting target analyses show both improvements and unresolved discrepancies. Provenance makes those choices inspectable. It does not itself identify the cause of an error or calibrate reliability before target disclosure.

## Scope and retained evidence

This audit reads the original `model_spec.json`, `generator.py`, `numerical_uptake.json`, candidate freezes, selected existing analytic documentation and aggregate study summaries for all 20 Agent constructors. The companion JSON retains native grouped provenance, assumption descriptions, operation-use mappings, source paths/hashes and all 60 existing constructor-endpoint summaries. Generator source was read as text/AST; no generator or analytic author script was imported or executed. No real or generated row table was read, no evaluator was rerun, and no download, clinical fit, sampling, paid model call or historical-file modification occurred. Only this new audit directory is written.

Canonical study records: [completed study](../main_study_freeze_2026-11-03/RESULTS.md), [complete interpretation and constructor ledger](../main_study_freeze_2026-11-03/publication/RESULT_INTERPRETATION.md), [native uptake inventory](../main_study_freeze_2026-11-03/publication/UPTAKE_INVENTORY.json), [pre-evaluation decision closure](../main_study_freeze_2026-11-03/ALL_AUTHOR_DECISIONS_SUBMITTED.json), and [evaluation completion](../main_study_freeze_2026-11-03/final_evaluation/EVALUATION_COMPLETED.json). Original candidate files reside under `D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcMS/<constructor>/bundle/candidates/initial/`; exact paths and hashes are in the JSON.

E0/E1 are information conditions, not before/after versions of the same author. A01 in E0 is not paired with A01 in E1. Both references were already exposed to the research team; fresh author contexts and common closure do not restore project-level blindness. All selected laws were initial laws; there were no feedback-driven scientific revisions.

## Why the proposed explanation is too strong

| Claim to assess | Existing evidence | Conclusion |
|---|---|---|
| Five of six improve because ASSUMED becomes REPORTED | CHNS E3 conditional age has no reported age constraint in E1. Its mean absolute discrepancy nevertheless falls from 0.007281 to 0.004854 pp/year. A03 explicitly assumes demographic independence and zero population age slope; the other authors supply age effects or age correlations. | Improvement does not require this label transition. New evidence can affect a joint projection indirectly, and different authors choose different assumptions. |
| ENSANUT conditional BMI becomes a reported relationship | Jansen reports two separate age/sex-adjusted projections, not the coefficient additionally adjusted for glucose. Every ENSANUT E1 author solves for a joint coefficient using an assumed BMI-glucose covariance. | This endpoint is DERIVED with ASSUMED parents and a transport assumption. It is not directly REPORTED. |
| E0 is assumption-only while E1 is evidence-based | All E0 authors use reported source marginal moments. E0 also contains unit/moment derivations and source-to-target assumptions. Some E0 authors impose independence; others add shared factors or demographic effects. | Label the specific quantity and dependency, not the whole arm. |
| Reported/derived inputs rank target accuracy above assumed inputs | ENSANUT E0 A05, whose dependencies are explicitly assumed, has BMI discrepancy 0.007955 pp/5 BMI, below every E1 Agent's 0.021128–0.027184. CHNS E0 A02/A04 BMI discrepancies 0.006273/0.007723 are also below every E1 Agent's BMI discrepancy (minimum 0.009190). | These are selected descriptive counterexamples to a deterministic ranking, not proof that assumptions are generally better. All authors/endpoints remain in the JSON. |
| Directly reported coefficients ensure close target agreement | All ENSANUT E1 authors transport Pani's 0.01 pp/year age projection. Their generated age means cluster at 0.097769–0.102452 pp/decade, above reference 0.075132. | Source provenance does not establish target applicability. |
| CHNS BMI worsens purely because of transport | A01/A02/A04 constrain both Jansen projections; A03 instead constrains MIND rank and uses Jansen only as a check; A05 constrains Jansen BMI through an assumed uniform-source/rank bridge and changes target margins/age dependence. They do not share one transported law. | Transport is a plausible component, but exclusive causal attribution is unidentified. Structural completion, source choice/use, adjustment, target dispersion and sampling also differ. |

The original six endpoint contrasts remain descriptive: CHNS BMI worsens; CHNS glucose/age and all three ENSANUT endpoints improve at arm level. These are six related analysis definitions in two reference families, not six independent clinical studies. No author-level pairing, randomized mechanism intervention, probability of improvement, significance test or provenance prediction model is introduced here.

Exact counterexample pointers: CHNS E1 A03 [specification](../../../../evcMS/CHNS2009_E1_A03/bundle/candidates/initial/model_spec.json), assumption `A_DEMOGRAPHY`, explicitly states the zero population age coefficient; its [generator](../../../../evcMS/CHNS2009_E1_A03/bundle/candidates/initial/generator.py) draws independent demographics at lines 13–14 and biomarker innovations at lines 15–27. ENSANUT E0 A05 [specification](../../../../evcMS/ENSANUT2018_E0_A05/bundle/candidates/initial/model_spec.json), `/parameter_provenance/hba1c_loadings`, explicitly labels all dependence as assumption-dependent; its [generator](../../../../evcMS/ENSANUT2018_E0_A05/bundle/candidates/initial/generator.py) implements the chosen factors at lines 30–38. Their retained outcome records are `endpoint_rows` entries `CHNS2009_E1_A03/E3` and `ENSANUT2018_E0_A05/Q2_bmi5` in the companion JSON, copied from the original constructor summary rather than recomputed from rows.

## Endpoint-level evidence coverage

| Target analysis | What the added packet can supply | What the final target quantity still needs |
|---|---|---|
| CHNS BMI, adjusted age/sex | Jansen's separate source BMI slope, or indirect constraints from an adopted source joint/rank model | Choice of source operation to constrain; covariance/family completion; source/target measurement and selection bridge; target joint law. A03 never constrains this Jansen slope. |
| CHNS glucose, adjusted age/sex | Jansen's separate source glucose slope, Bao Pearson or MIND Spearman with different meanings | Raw-scale projection under adopted margins/dependence; rank-to-family mapping where used; target excess-glycemia assumptions; transport. An available operation need not be a fitted constraint. |
| CHNS age, adjusted sex/BMI/glucose | No directly supplied age coefficient | Assumed age effects/age dependence and the rest of the joint model determine the projection. |
| ENSANUT age, adjusted sex/BMI/glucose | Pani's adjusted source age point 0.01 pp/year | Applying that coefficient to a different selection, measurement and analytical weighting context remains assumed. |
| ENSANUT BMI, adjusted age/sex | Jansen's source projection, converted to task units | The selected additive law preserves that projection under stated covariance/composition assumptions; source-to-target equality is not observed. |
| ENSANUT BMI, additionally adjusted glucose | Not directly supplied | Joint coefficient derived from separate projections, residual SDs and assumed residual covariance, then transferred to target. |

The packet also contains Pani age-band means. A01/A04 keep these as context; A02/A03/A05 calculate checks without fitting them. Counting all eleven ENSANUT E1 operations as eleven constraints would be incorrect. Likewise, repeated statistics from a source family and converted units are not independent evidence.

## All 20 authors: concise construction mapping

R = reported source quantity; D = deterministic or model-conditional derivation; A = explicit scientific assumption. These are overlapping dependency labels, not exclusive quality grades. Every row also has task/design choices and source-to-target assumptions. The JSON provides individual native IDs and paths rather than assigning a single label to an entire constructor.

| Constructor | R and D used in the law | A that materially controls requested analyses |
|---|---|---|
| CHNS E0 A01 | MIND means/individual SDs; lognormal moment conversion | Independent product law; all three population slopes zero. |
| CHNS E0 A02 | Same MIND margins; lognormal moment conversion | Shared log-factor loadings 0.30/0.60/0.70; demographic independence makes age slope zero. |
| CHNS E0 A03 | Same MIND margins; Gamma residual parameters derived from moments | Shared Gamma shape 4 and variance fractions 0.10/0.65/0.65; demographic independence. |
| CHNS E0 A04 | Same MIND margins; lognormal moment conversion | Shared loadings 0.35/0.75/0.65, female probability 0.5 and demographic independence. |
| CHNS E0 A05 | Same MIND margins; normalization preserves total moments under its mixture | Log-age effects 0.01/0.02/0.015 per decade, sex effects, factor loadings 0.35/0.65/0.80. |
| CHNS E1 A01 | Constrains Jansen BMI and glucose; derives joint slopes with assumed residual correlation 0.25; checks Bao | Assumed source nuisance effects, target residual SDs, age/sex effects, and independent 8% lognormal glucose-excess component with HbA1c loading 0.55. |
| CHNS E1 A02 | Same two Jansen constraints; residual correlation 0.30 enters the joint-slope derivation; checks Bao | Assumed target covariate effects, Gamma BMI innovation, 10% Gamma excess and extra HbA1c loading 0.20. |
| CHNS E1 A03 | Constrains MIND Spearman 0.529 via Gaussian-copula identity; Jansen/Bao are checks; MIND margins | Assumed lognormal/Gaussian-copula family, latent BMI-glucose correlation 0.20, conditional latent independence, demographic independence. |
| CHNS E1 A04 | Constrains both Jansen projections using assumed correlation 0.25; checks Bao; MIND target moment anchors | Uniform factors, assumed age coefficient 0.005 pp/year, 10% class with glucose/HbA1c shifts 4/1.8 and derived within-class residual scales. |
| CHNS E1 A05 | Constrains Jansen BMI via uniform-source slope-to-correlation/rank derivation and MIND Spearman; checks Jansen glucose/Bao | Uniform source versus lognormal target margins; BMI-glucose rank 0.25; target latent age correlations 0.10/0.10/0.15; transferred copula. |
| ENSANUT E0 A01 | Jansen marginal moments; bounded-Beta BMI and residual SD derivations | Age/BMI/shared-factor effects are assumed, including HbA1c age loading 0.004 pp/year and BMI/shared-glucose loadings 0.04/0.14. |
| ENSANUT E0 A02 | Jansen margins; lognormal BMI/HbA1c and scaled-Beta glucose moment conversion | Independent product law; all focal population projections zero. |
| ENSANUT E0 A03 | Jansen margins; Gamma BMI and scaled-Beta glucose/HbA1c conversion | Independent biomarkers/demographics; all focal population projections zero. |
| ENSANUT E0 A04 | Jansen margins; Gamma BMI/HbA1c and scaled-Beta glucose conversion | Independent product law; all focal population projections zero. |
| ENSANUT E0 A05 | Jansen margins; standardization and residual loading derivations | Chosen age/sex/common-factor loadings, including HbA1c 0.22/-0.06/0.20/0.50; Beta shape 3. |
| ENSANUT E1 A01 | Constrains Jansen's two projections and Pani age; joint slopes/residual SD derived | BMI-glucose correlation 0.25, Beta shapes, source-context reconstruction and target transport; eight Pani bands contextual. |
| ENSANUT E1 A02 | Same three constraints and derivation | Correlation 0.25, symmetric Beta shape 4, zero added sex effect and context/transport assumptions; eight Pani bands checked. |
| ENSANUT E1 A03 | Same three constraints and derivation | Correlation 0.30, chosen Beta/uniform factors, zero sex effect and context/transport assumptions; eight Pani bands checked. |
| ENSANUT E1 A04 | Same three constraints; solves covariance normal equations and residual variance | Assumed factor loadings 1.5 and 3.0 give covariance 4.5, chosen supports and transport; eight Pani bands contextual. |
| ENSANUT E1 A05 | Same three constraints; joint slopes and residual SDs after source demographic variance subtraction | Residual correlation 0.30, age/sex covariate loadings, Beta shape 3 and transport; eight Pani bands checked. |

## Concrete parameter-to-analysis chains

**Jansen to CHNS A01 is not a directly reported joint coefficient.** Its [frozen derivation](../../../../evcMS/CHNS2009_E1_A01/bundle/candidates/initial/analytic/law_derivation.md) records separate slopes cB=0.13 and cG=2.29 in IFCC response units. Residual SDs depend on assumed source age/sex effects, and residual correlation r=0.25 is assumed. Solving `cB = thetaB + thetaG*r*sG/sB` and `cG = thetaG + thetaB*r*sB/sG` yields one possible joint response law. The target uses converted joint slopes, different residual SDs and an added excess component. Its BMI projection is `thetaB + thetaG*r*sG_target/sB_target`, not necessarily the printed source cB. The excess is independent of BMI in this law, so it must not be casually blamed for the BMI numerator; it does change glucose-related projections and fully adjusted regression behavior. Source population differences, chosen completion and target remodeling are connected but distinct questions.

**ENSANUT's conditional BMI coefficient makes the assumption dependence explicit.** A01/A02 use rho=0.25 and store joint BMI coefficient 0.00587257 pp per BMI; A03 uses rho=0.30 and stores 0.00464633; A05 uses rho=0.30 plus source age/sex residualization and stores 0.00472203. A04 instead specifies an assumed covariance of 4.5. All constrain the same two separate source projections. These different joint coefficients are legitimate consequences of different completions, not four differently reported source effects. This audit does not claim the cross-author differences isolate rho: families, covariate effects and finite-table behavior also differ.

**A source point can coexist with an assumed target null.** CHNS E1 A03 constrains reported glucose-HbA1c Spearman yet makes age independent of every biomarker. Its population adjusted age slope is therefore zero. The retained target mean is -0.000509, compared with reference +0.008107. A single provenance label attached to the whole model would conceal this unsupported analysis.

## A defensible attribution schema

Use one record per **scientific quantity/use**, linked into each requested estimand. Do not count every scalar or every JSON field as an independent evidence item. Task quotas, row IDs, RNG constants and algebraic standardization factors must not inflate a biological-assumption score.

1. `quantity_id`, value/unit, source population, selection, measurement, weighting, adjustment set and source locator. Record the original source statistic before conversion.
2. `origin`: REPORTED, ASSUMED, or TASK/DESIGN. `transformation`: direct, unit conversion, algebraic identity, or model-conditional derivation. DERIVED must retain its parent quantity and assumption IDs; it does not erase ASSUMED ancestry.
3. `use_role`: numerical constraint, analytic check, context-only, or declined. Preserve the native operation disposition; availability is not adoption, and adoption is not exact source replay.
4. `context_bridge`: source to constructed source scenario to target. Record population, measurement, selection, weighting and adjustment changes separately, including unknowns. A reported source coefficient used unchanged in target has REPORTED origin plus ASSUMED transport.
5. `implementation`: exact model-spec JSON pointer, generator/function/line, frozen file hash, and recorded analytical implication if one exists. Absence of a supported analytic implication is explicit; do not invent it.
6. `affected_estimands`: each requested endpoint with the dependency path, what the admitted evidence constrains, and which unresolved assumptions remain relevant. Include nuisance distributions and supports where the actual law makes the estimand depend on them.
7. `assessment_phase`: historical pre-evaluation artifact, retrospective coding, or later held-reference comparison. Append existing mean/range/discrepancy as outcomes, keeping them out of the provenance definition.

For the present audit, native grouped provenance is retained rather than automatically expanding a group-level evidence ID onto every descendant scalar. For example CHNS A01's `target` group contains both evidence-derived slopes and assumed target settings; ENSANUT A01's `coefficients` group combines reported age, derived BMI/glucose and derived residual SD. A single group label would be wrong. A targeted leaf-level chain is feasible for the focal relationships; an exhaustive independent recoding of every scalar was not performed here.

## What was knowable before reveal, and what remains retrospective

All 20 specifications already contain `parameter_provenance` and named assumptions. The audit checks original freeze commitments for each specification, generator, uptake and evidence file. Candidate freeze timestamps precede the recorded common decision closure at 2026-11-03 19:52:44 UTC, when `reference_evaluation_started` was false; the completed evaluation is recorded at 20:09:50 UTC. This establishes a retained pre-common-evaluation record, not proof of no prior project exposure. Byte checks establish identity, not scientific correctness.

Thus a future reviewer could code source origin, use role and explicit assumptions from these artifacts without needing target values. **This audit's category definitions, focal chains and example selection are retrospective and outcome-aware.** Neither the historical provenance nor a new outcome-masked rater makes this a prospectively validated predictor of error. The current constructors share sources, task definitions and service conditions; labels are strongly entangled with information arm and model family. Three seeds are draws within a law. Sixty constructor-endpoint records are not sixty independent scientific tasks.

No provenance-error regression, threshold, success-rate comparison or training/evaluation split is fitted here. At most the current evidence can motivate a prespecified prediction hypothesis. Testing such a hypothesis would require definitions and scoring fixed before new outcome access, preserved null/negative cases, and independent task/reference assessment. This audit does not authorize that new experiment.

## Fit with the current paper

The audit fits v0.27's stated contribution: Agent-authored joint biomarker construction from incomplete heterogeneous evidence, evaluated on specified scientific analyses. It can strengthen the source/assumption case analysis and explain why additional evidence constrains some uses without identifying every joint relationship. It does not justify changing the paper into a validated provenance-based error-prediction method, claiming that all five improvements are parameter upgrades to reported truth, or treating CHNS BMI as a pure transport ablation. No manuscript, figure, generator, outcome or historical decision was changed.

The practical next editorial decision is whether to include a compact endpoint dependency table and one worked chain, with the complete 20-author mapping retained as supporting material. That is a presentation option, not an automatic manuscript edit or a new experimental commitment.
