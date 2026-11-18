# Scientific uses, observed discrepancies, and acceptable differences

16 November 2026. This is a focused interpretation of closed experiments, not a new generation or patient-data validation. The current manuscript remains v0.32. The numerical ledger contains 222 saved estimate slots in 32 analysis-by-condition profiles; these are not 222 independent experiments. All constructors and all three saved draws are retained within each selected case. HRS reconstruction and artificial composition are considered separately because their references have different meanings.

## 1. Keep the scientific contribution concrete

The contribution is a way for an Agent to turn a biomedical research request, published evidence and optional observed covariates into virtual records that can be analyzed with ordinary scientific methods. The Agent chooses the joint law and numerical assumptions. Deterministic tools execute and check that choice. Whole-cohort generation remains part of the task; the method is not restricted to completing one missing column.

The relevant outcome is **which specified analyses the delivered data support**. Current evidence supports several association patterns and a targeted improvement in paired blood-pressure dependence. It does not establish uniform numerical adequacy across the entire dataset. Better tracing of assumptions helps explain and inspect a result; tracing alone does not certify it.

The same analysis must define the population, eligibility, transformation, adjustment set, weighting, contrast and unit on both sides. This is specific statistical utility, distinct from general resemblance of two tables [1]. Here, analyses were reimplemented from the source Methods where original scripts were unavailable. “Only replace the data” describes the shared implementation, not possession of the authors' original code.

## 2. What the existing data support

Ranges below include every saved draw of the specified constructors. A real-data estimate is a sample reference with uncertainty, not a known population parameter. These are observed discrepancies, **not retrospectively selected acceptance margins**.

| Requested scientific analysis | Existing evidence | Current defensible use | Important boundary |
|---|---|---|---|
| Age/sex-adjusted lifestyle contrasts in BMI | Urban minus pastoralist: real 1.882 kg/m²; virtual 1.700–2.251. Both urban BMI contrasts are positive in all 6 tables from 2 authors. Largest absolute point difference for urban minus pastoralist: 0.369 kg/m². | A concrete demonstration of reconstructing the requested observational group pattern and approximate effect scale. | Source-rich reconstruction: original paper findings were allowed. This is not new-population confirmation, a causal urbanization effect, or a formal equivalence result. |
| Paired SBP/DBP dependence after covariate adjustment | PNS residual correlation: real 0.7172; augmented-evidence virtual 0.6865–0.7182 across 3 authors and 9 tables. Mean absolute reference difference is 0.01277, versus 0.17962 with the original packet. | The strongest current example that complementary joint evidence improves a specified joint-analysis output. | Existing exposed reference; external sources remain partly mismatched and target residual dependence is assumed, not identified. This does not validate joint tail risks or every BP analysis. |
| Adjusted BMI–blood-pressure regressions | Augmented virtual SBP slope 3.666–4.193 versus real 3.524; DBP slope 2.829–3.195 versus real 2.260, all in mmHg per 5 kg/m². | Positive association scenarios; a complete scientific-use profile accompanying the dependence result. | Quantitative slope adequacy is unresolved. SBP slope and spread are less close after evidence augmentation; joint-correlation improvement is not overall dominance. |
| BMI–HbA1c association before and after glucose adjustment | Reduced-model BMI coefficient remains larger than the glucose-adjusted coefficient, and both remain positive in all 6 ENSANUT tables from 2 authors. Attenuation is 0.01394–0.02621 versus real 0.02701 HbA1c percentage points per 5 kg/m². | Reproduction of this specified conditioning pattern with one delivered table supporting both models. | Association attenuation is not evidence of causal mediation. HbA1c/residual variation is too narrow to infer that power, prediction intervals or individual risk will be adequate. |
| Lipid contrasts across lifestyle groups | TC rural minus pastoralist: real 9.493 mg/dL; virtual −0.695–1.943. HDL rural minus pastoralist: real 4.446; virtual −1.833–0.015. | Pipeline development and explicit sensitivity scenarios; urban TC direction is reproduced, but it cannot certify all lipid contrasts. | Current evidence does not support precise rural lipid magnitudes. Weak HDL reference effects have intervals including zero, so point-sign disagreement is not established biological reversal. |
| Joint iron-status analysis | Threshold OR: real 17.79; virtual 4.84–6.56. Both laws give positive co-occurrence. Rank and burden results differ by law and are retained in the ledger. | Co-occurrence scenario generation, with the assumed strength visible. | Positive direction alone does not establish usable OR magnitude. Do not select the better law after reveal and label the method validated. |
| Repeated-visit mixed-model analysis | The HRS source-model exercise generates balanced visits and fits the specified age-by-HbA1c interaction. The lower-segment interaction is negative in all 6 final tables from one Agent and one native comparator. | Testing a longitudinal analysis pipeline and reconstructing an explicitly supplied published model. | This is model reconstruction, not independently measured longitudinal validation. Weak upper-segment effects and uncertainty are not robustly recovered. |
| Joint inference from complementary compatible statistics | The artificial composition pilot: 24 constructions, 72 tables; all 90 identified estimates meet the predeclared numerical tolerance. Partial evidence is correctly treated as incomplete. | Controlled evidence that Agents can compose statistics into the requested mathematical joint relation. | Artificial known parameters and numerical tolerances do not supply biomedical validity or clinical equivalence margins. |

The current paper can lead with the first two rows, use ENSANUT as an additional reuse pattern, and retain the full lipid/BP profiles alongside them. This keeps final-data utility central without turning the work into a different failure-detection benchmark.

## 3. What difference can be accepted?

There is no justified single percentage for every variable and scientific use. An acceptable difference is the largest discrepancy that would **not change the intended interpretation or decision**. It must be stated in that analysis's units and justified independently of the result it will judge. The existing experiments did not predeclare such biomedical margins; this audit does not manufacture them afterward.

| Intended use | Appropriate criterion | What is insufficient |
|---|---|---|
| Demonstrate an association pattern | Report the named contrast/order/attenuation and all observed departures. For uncertain near-zero reference effects, preserve uncertainty instead of demanding a point-sign match. | A universal “all p-values agree” or “all directions match” score. |
| Approximate an effect for a substantive analysis | Define a use-specific margin Δ in original units before a subsequent evaluation. Report signed and absolute differences plus reference, construction and sampling uncertainty. | Choosing Δ just larger than the observed maximum discrepancy, or borrowing another endpoint's margin. |
| Evaluate a weak or null relation | Define a practically negligible region around the null and assess whether uncertainty supports it. | Treating p > .05 as evidence of no effect. |
| Use joint or threshold events | Check the requested conditional dependence or joint event itself, including the relevant tail/cell uncertainty. | Agreement of marginal means and SDs alone. |
| Plan power, sample size or individual prediction | Establish adequacy of the needed variance, dependence, prevalence and uncertainty components for that task. | More virtual rows, narrower synthetic-only intervals, or preserved signs. |

For the present task set, BMI contrasts use kg/m²; BP slopes use mmHg per 5 kg/m²; HbA1c slopes use percentage points per specified covariate increment. The HbA1c concentration mean itself remains expressed as NGSP %. Correlation differences are dimensionless; inference may use a justified transform. Odds ratios have null 1 and should also be examined on the log scale. Relative error is unsuitable for near-zero effects.

**The 0.369 kg/m² BMI difference and 0.03066 maximum residual-correlation difference describe current performance. They are not declarations that these discrepancies are acceptable for every biomedical application.** A domain collaborator can specify what a difference of that size would change in the proposed use. The useful question is about that use, not whether a plot looks close.

Formal equivalence requires bounds and an appropriate analysis of the *difference*; nonsignificance and overlapping separate confidence intervals do not establish it [2]. An ordinary synthetic regression interval is conditional on the selected law and generated row count. It usually omits uncertainty in literature extraction, source estimation, joint-model assumptions and transport. We therefore do not apply a formal equivalence label using these intervals alone.

Two uncertainty questions must stay separate:

- **Sampling context:** could discrepancies of this size arise when the same analysis is repeated on finite samples from the available empirical reference?
- **Scientific tolerance:** would discrepancies of this size change the intended scientific interpretation or decision?

A broad sampling distribution does not make a scientifically consequential difference acceptable. A narrow one can make a practically negligible difference detectable. Both questions are informative, and neither requires exact row-by-row reconstruction.

## 4. The one most informative next validation

Prioritize a **matched-size real–real versus virtual–real sampling diagnostic within the already completed lifestyle case**. Keep its two Agent laws, six saved tables, three biomarkers and all nine pooled contrasts fixed. Use the same operator and exact trait-specific available-case sample counts. Report the three SD diagnostics alongside the contrasts. The complete plan is [MINIMAL_VALIDATION_PROTOCOL.md](MINIMAL_VALIDATION_PROTOCOL.md).

This case directly tests the user's proposed application: repeat the published-style analysis and replace the dataset. It also addresses an existing evaluation asymmetry: the real BMI, TC and HDL analyses used 1,189, 400 and 405 observations, whereas each complete virtual table has 1,226. Matching sample size and prespecified group/sex composition contextualizes precision without changing a generator or selecting a favorable analysis.

The diagnostic will show whether a discrepancy remains centered away from zero relative to ordinary empirical sampling variation. It will not convert resamples into independent cohorts, certify an equivalence margin, explain every model defect, or establish transport. This protocol is **drafted, not executed** in this unit. No new model call, source search or target dataset is needed.

If BMI patterns remain supported and lipid differences persist, write the paper around the demonstrated uses and state those limits. If an apparent discrepancy is largely a sample-size/precision effect, correct the evaluation interpretation. Neither outcome calls for tuning these exposed generators. A separately unexposed cohort becomes necessary only for a stronger new-population claim; it is not a prerequisite for finishing this focused empirical paper.

## 5. What to retain, defer, and ask a domain reviewer

- Retain the full source-to-data trace, scientific-use results and PNS complementary-evidence result. Keep every selected constructor, analysis, failure and unfavorable comparison.
- Defer larger model/provider grids, more data families, renewed lipid searches, another generic feedback component, and universal “quality” scores. None answers the immediate use question as directly.
- Ask the domain reviewer to name the intended use, raw-unit discrepancy that would change its interpretation, and essential extra diagnostics. Record their rationale and whether they saw current results; post-result judgments remain developmental.
- Add a concise scientific-use paragraph to the manuscript at its next planned revision, using [MANUSCRIPT_USE_INSERT.md](MANUSCRIPT_USE_INSERT.md). Do not revise v0.32 or its figures just to rename the same evidence.

## Sources and reading scope

[1] Snoke J, Raab GM, Nowok B, Dibben C, Slavkovic A. *General and specific utility measures for synthetic data*. JRSS A (2018). [Publisher DOI](https://doi.org/10.1111/rssa.12358); [author-institution copy read](https://www.pure.ed.ac.uk/ws/portalfiles/portal/57112054/Snoke_et_al_2018_Journal_of_the_Royal_Statistical_Society_3A_Series_A_28Statistics_in_Society_29.pdf). We use its distinction between general and analysis-specific utility. Its synthesis settings do not supply automatic inferential guarantees for literature-only generation.

[2] Lakens D. *Equivalence Tests: A Practical Primer for t Tests, Correlations, and Meta-Analyses*. Social Psychological and Personality Science (2017). [Primary article](https://journals.sagepub.com/doi/10.1177/1948550617697177). The methods discussion supports prespecified, justified equivalence bounds and the distinction between nonsignificance and equivalence. It supplies no BMI, lipid or blood-pressure tolerance for this project.

[3] Morris TP, White IR, Crowther MJ. *Using simulation studies to evaluate statistical methods*. Statistics in Medicine (2019). [Primary article](https://doi.org/10.1002/sim.8086). Used for explicit aims, data-generating mechanisms, estimands, methods, performance measures and Monte Carlo uncertainty in the diagnostic plan; it does not turn empirical reference resampling into known biomedical truth.

The Scite connector failed before returning results; the primary journal/institution sources above were checked with web retrieval. No new clinical evidence was admitted. No conclusion relies on the inaccessible full methods of a newer confidence-interval-coverage article found during search.
