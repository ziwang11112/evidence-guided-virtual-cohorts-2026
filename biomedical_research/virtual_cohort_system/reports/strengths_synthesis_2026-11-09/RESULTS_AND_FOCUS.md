# Empirical strengths and a focused paper question

9 November 2026 · Retrospective synthesis of the virtual-biomedical-data research record

## Decision

The strongest supported center is **constructing analyzable biomedical data from incomplete study evidence, without requiring target individual-level training records or a user-written joint generator**. A scientific Agent contributes the missing modeling work: interpreting study conditions, choosing a stochastic structure, assigning numerical evidence and assumptions to it, and delivering data for the requested analyses.

The proposed paper question is:

> Can a scientific Agent turn incomplete published biomedical evidence and a research request into virtual individual-level data that preserve the information needed for that analysis?

Complete-cohort generation remains central. Adding an entirely unmeasured indicator and completing missing observations remain valid input modes. The focus is a particular information-to-data problem, rather than a single biomarker or a requirement that every workflow use multiple Agents. The practical endpoint is usable data. Source checks and revisions explain how the data are obtained; they are not the primary scientific product.

This is an evidence-based positioning recommendation, not a new novelty search, a claim of priority, or a finding that all proposed analyses are reliable. Favorable historical results inform the question; they do not retroactively become prespecified confirmatory evidence.

## What was reviewed

Three read-only audits inspected the historical, primary and recent branches. The [all-unit index](ALL_UNIT_INDEX.csv) contains **78 audit records: 36 historical groups, 19 primary units and 23 recent units**. These include setup, engineering, diagnosis and overlapping milestone summaries; 78 is not a count of independent experiments or clinical replications. All 22 top-level milestone reports were covered. Unrelated earlier skin/omics and LLM-memory projects, GitHub mirrors and manuscript-render copies are outside this inventory.

The detailed records are [historical](HISTORY_AUDIT.md), [primary](PRIMARY_AUDIT.md) and [recent](RECENT_AUDIT.md). Each favorable finding carries its input regime, actual scale, comparator, counterresults and inference scope. Multiple random seeds are draws from a law, not independently learned mechanisms. Source strata, repeated evaluations and initial/final aliases are not new clinical populations.

The root recomputed the principal contrasts from frozen aggregate outputs, without accessing patient rows or rerunning generators. An independent review verified 160 arithmetic/count comparisons, maximum difference 3.16e-16, with no unresolved discrepancy: [derivation review](DERIVATION_REVIEW.md), [complete numeric contrasts](MAIN_COMPARISONS.csv), [aggregate derivation](derive_highlights.py). No new clinical analysis, literature search or outcome-guided tuning was performed.

## Ranked strengths

### 1. Relationship evidence can improve the scientific information carried by the final data

The [main frozen study](../main_study_freeze_2026-11-03/RESULTS.md) is the strongest current quantitative comparison. It has two biomedical cases, 20 fresh Agent constructions, four fixed statistical constructions and 72 final 3,000-row tables. Each Agent arm has five constructions, each evaluated over three seeds. References are selected CHNS2009 participants (n=6,631) and ENSANUT2018 participants (n=6,931); these are exposed developmental references, with target outcomes withheld from the constructors.

Compared with the basic/marginal-evidence arm E0, the relationship-evidence arm E1 has lower mean absolute sample-reference discrepancy for five of the six planned regression coefficients. These are differences in downstream analyses of the generated data, not just a better match to means and SDs.

| Analysis of HbA1c | E0 Agent mean absolute discrepancy | E1 Agent mean absolute discrepancy | Relative discrepancy reduction |
|---|---:|---:|---:|
| CHNS BMI coefficient | 0.020380 | 0.031557 | **−54.8%: worse** |
| CHNS glucose coefficient | 0.134019 | 0.024079 | 82.0% |
| CHNS conditional age coefficient | 0.007281 | 0.004854 | 33.3% |
| ENSANUT age coefficient | 0.063944 | 0.024670 | 61.4% |
| ENSANUT BMI coefficient | 0.056883 | 0.023732 | 58.3% |
| ENSANUT glucose-adjusted BMI coefficient | 0.048797 | 0.025649 | 47.4% |

Units differ across rows: CHNS predictors use kg/m², mmol/L and years; ENSANUT age uses ten years and BMI uses five kg/m². Do not pool these numbers into one unweighted error score. The arm differences are descriptive, not a paired causal estimate: different authors constructed E0 and E1 laws. A percentage reduction is not accuracy, an equivalence result, or a biomedical importance threshold.

The effect on model construction is real: all ten E1 authors numerically used relationship evidence. This supports a contribution centered on **turning evidence into an executable joint model**, rather than treating papers only as verbal guidance. All retained/finalized laws and the worsening CHNS BMI endpoint remain in the comparison. The study has zero scientific feedback revisions; the improvement is not evidence for a feedback component.

### 2. There is a specific comparative advantage under incomplete joint specification

The main study contains a favorable comparison that should be presented, with its actual design visible. Agent arm-average discrepancies are lower than those of the delivered fixed statistical specification in all six E0 analyses and four of six E1 analyses.

| E1 analysis | Agent discrepancy | Fixed statistical discrepancy | Closer arm mean |
|---|---:|---:|---|
| CHNS BMI | 0.031557 | 0.052555 | Agent |
| CHNS glucose | 0.024079 | 0.012021 | Fixed statistical |
| CHNS conditional age | 0.004854 | 0.007878 | Agent |
| ENSANUT age | 0.024670 | 0.076680 | Agent |
| ENSANUT BMI | 0.023732 | 0.026202 | Agent |
| ENSANUT glucose-adjusted BMI | 0.025649 | 0.007940 | Fixed statistical |

The useful interpretation is **flexible completion of an incomplete model specification**. The E0 statistical baseline maximizes entropy under admitted constraints, yielding independence within source components; CHNS source mixing can still induce dependence. Agents can instead choose and disclose dependent structures using their modeling assumptions and prior knowledge. In ENSANUT E1, all five Agents also use the Pani age relationship numerically, whereas the fixed specification leaves that relationship and age bands contextual because source dispersion, age law and weighting are unbound.

That distinction is relevant to our application: a researcher may possess evidence without a fully specified simulator. However, it does not isolate the causal benefit of an LLM prior, a probability family or additional human effort. There are five Agent laws against one fixed statistical law per condition, and the fixed method does not perform comparable alternate-model search. Every E1 Agent loses to the fixed method on CHNS glucose and ENSANUT conditional BMI. The legitimate claim is the result against this stated completion rule, not superiority over all statistical generation.

**Paper role:** a concrete comparative panel and a motivated hypothesis about reducing required model specification. It should not become an exaggerated headline that Agent wins every analysis or needs no statistical assumptions.

### 3. Some generated data preserve useful joint analytical behavior, beyond marginal resemblance

The [core replication](../core_workflow_replication_2026-11-04/RESULTS.md) contains four fresh constructions for two requests and 12 final tables. All 36 primary seed estimates have the reference point direction across six analysis definitions. In CHNS, the age/sex-adjusted BMI coefficients are 0.03992 and 0.05338 versus 0.05495; glucose coefficients are 0.37754 and 0.49241 versus 0.40209. These magnitudes are more informative than direction counts alone.

In ENSANUT, the two complete author profiles give BMI coefficients of **0.09165 → 0.07509** and **0.07140 → 0.04733** after adding glucose adjustment; the reference is **0.08364 → 0.05664**. Every draw preserves attenuation. This is a useful multivariable relationship in the same generated dataset, not a causal mediation finding. It is also not a claim that this behavior is wholly independent of supplied relationship evidence.

The [real-real context analysis](../real_real_calibration_2026-11-04/RESULTS.md) adds a useful scale of comparison for a separate construction: its three virtual tables come from the single `evcBuild01` law in [evidence-to-generation](../evidence_to_generation_2026-11-04/RESULTS.md), seeds 7401–7403, not from the four core-replication authors above. Across 100 fixed community-disjoint resplits of the selected CHNS reference, the median absolute reduced-model BMI difference is 0.007239; the three frozen virtual-table symmetric discrepancies have medians 0.004383–0.012727. Age is 0.001705 versus 0.001055–0.002387. Several generated analyses therefore differ on a numerical scale also seen between real subsamples. This does not define an equivalence margin or create 100 independent cohorts. Full-model glucose remains appreciably worse: 0.079642–0.109154 versus real-real 0.023839.

Other input modes supply supporting evidence. M10 insulin augmentation has two constructions and six draws preserving positive BMI association and negative BMI curvature. M17-B generates every substantive variable without individual inputs and retains selected BMI, age and sex directions across six tables. These are earlier method versions; they show application breadth, not additional replications of the current frozen workflow.

Counterresults remain consequential: age magnitudes are biased in the core cases; ENSANUT residual spread is too narrow. In cross-task lipids, residual correlations are 0.108–0.141 versus 0.512. In the iron case, one author's rank correlations 0.391–0.430 are close to 0.398, but both authors' threshold ORs 4.835–6.565 are well below 17.79. Show complete author profiles, rather than combining one author's good prevalence with another author's good correlation.

**Paper role:** lead with actual analysis outputs—effect estimates, adjustment patterns and their uncertainty/context—then show distributions as supporting diagnostics. The final data's usefulness is the center; successful script execution is not the success criterion.

### 4. A historical synthetic-training experiment demonstrates downstream usefulness on later real participants

The [October 25 temporal pilot](../../../obesity_temporal_prediction_2026-10-25/RESULTS.md) deserves preservation. Two Agents literally wrote 128-row synthetic training cohorts. Fixed classifiers trained on those rows were evaluated on 1,811 eligible NHANES2017–18 participants, after model artifacts had been locked before the test download. The task is current elevated HbA1c (≥5.7%) among obese adults, using age, sex, BMI, waist and systolic BP. It is not prediction of future diabetes.

| Logistic training source | Later-sample AUC | Brier score |
|---|---:|---:|
| 128 real training records | 0.734936 | 0.210303 |
| Agent literal cohort A1 | 0.712130 | 0.216229 |
| Agent literal cohort A2 | 0.726871 | 0.213445 |
| 100 ordinary synthetic cohorts, median | 0.717394 | 0.215560 |

This is actual train-on-synthetic/test-on-real utility. However, the input was rich outcome-by-sex-conditioned summaries calculated from the same 128 real training records: margins, quantiles and rank correlations. It was not a literature-only setting. Neither Agent exceeds the real-training AUC; one is below and one above the ordinary-generation median, both within its draw distribution. There are no inferential equivalence/noninferiority conclusions. The second fixed classifier and all ordinary runs remain reported.

**Paper role:** historical supporting evidence that generated rows can carry usable predictive information. Keep it separate from the current literature-driven method's main table. Bringing this task into a current-method claim would require a distinct frozen replay, labelled developmental if reusing the revealed test.

### 5. Flexible generation is implemented, including literal rows, complete cohorts and longitudinal data

The archive demonstrates more than one fixed formula. Scientific authors have chosen bounded conditional models, shifted-gamma innovations, moment-equation solutions, copula/lognormal constructions, longitudinal random-effects models and literal row values. In HRS reconstruction, a generated cohort contains 11,509 virtual subjects with four visits each and supports the source mixed-model analysis. That example supplies the generating coefficients; it shows expressiveness and reconstruction, not independent clinical discovery. The corrected published comparator and our initial parser failure must accompany it.

The [recent adaptive case](../adaptive_case_loop_2026-11-09/RESULTS.md) completed 28 dispatched actions, real retrieval, two model structures and six outputs. The author chose scientific content and retained the initial law after inspection. The [source-conditioned construction](../source_conditioned_replay_2026-11-09/RESULTS.md) links one shared law to four source contexts and a target scenario: 12 source tables, 24 assumption-labelled numerical relationship projections and three target tables with nine requested estimates. All eight source relationship directions match, but strict source checks remain unavailable because standardization/weighting is unresolved; no new clinical reference was evaluated.

This is evidence that an Agent actually makes modeling choices, rather than a root-written biomarker formula being relabelled as Agent generation. Execution, arithmetic and workflow control remain deterministic software. Some older runs used curated packets; the later actual-retrieval runs should not retroactively make all experiments fully autonomous. No study here measures end-to-end researcher-time savings or a reduction in patient recruitment costs.

**Paper role:** an implementation capability that makes the data-construction problem practical. Avoid making the count of Agents, the number of checks or the amount of generated data a scientific contribution by itself.

## What should not lead the paper

| Candidate headline | What the full record shows | Treatment |
|---|---|---|
| Feedback consistently improves generation | Many explicit retain/no-op decisions; local improvements trade off with other analyses | Explain available action, not a required benefit claim |
| Multi-Agent collaboration is necessary | Ordinary Agents often perform the same useful reasoning; added reviews/instructions have no consistent gain | Keep optional implementation |
| Better missing-cell accuracy means better scientific analysis | Agent beats that MICE run on cell MAE in all three masks, but the primary coefficient is farther from the complete reference than the missing-only analysis in all three | Secondary application with complete results |
| Summary reconstruction alone is an Agent advantage | Rich-summary arm improves 27/30 metrics and ties three; conventional calibration also reconstructs supplied summaries | Reconstruction control, not exclusive novelty |
| Broad transport is established | Earlier prospective HAALSI primary standard passes 3/5 constructions, below the frozen 4/5 requirement; Turkana passes 0/5 | Report failed prospective criteria and method version |
| More draws solve unsupported dependence | Clinical dispersion and residual relationships can remain wrong despite stable coefficients/source matching | More seeds do not replace evidence or new constructions |
| Generating 10,000 rows creates 10,000 observations' worth of evidence | Draws reflect a modeled distribution and its assumptions; source information has not increased accordingly | Explicitly separate simulation size from empirical information |

These results need not dominate the introduction, but they remain accessible and bound the claims. Focusing on supported strengths means selecting coherent research questions, not removing unfavorable outcomes from their corresponding experiments.

## Contribution and story recommended now

1. **Application and task:** evidence-to-data construction for biomedical research when relevant individual measurements are inaccessible or absent. Input is the requested use, target description, available scientific evidence and optional real observations; output is virtual individual-level data plus a reproducible generator where applicable.
2. **Method:** a scientific Agent authors the joint model, chooses how numerical and conditional evidence apply, and can retrieve, inspect, retain or revise. Reusable skills perform statistical execution and semantic checks. Scientific assumptions remain attributable to the author; the host does not insert target slopes to obtain a desired result.
3. **Empirical finding:** resulting data support selected downstream analyses across construction modes; relationship evidence often materially improves those uses. Explicitly tested statistical comparisons reveal both favorable regions and losses. The diagnoses point to evidence adequacy and joint assumptions as leading explanations for remaining limits, rather than a blanket claim of numerical incompetence; they do not uniquely separate transfer failure from model misspecification.

The existing title *From Published Evidence to Analyzable Biomedical Cohorts with Scientific Agents* still fits. A new acronym, new loss or obligatory multi-Agent architecture is unnecessary to express these contributions. Their exact novelty relative to prior work must continue to use the existing verified comparison; this retrospective audit adds no priority claim.

### Proposed main figures

| Figure | Question | Content and display rule |
|---|---|---|
| 1: Evidence to analyzable data | What scientific work does the Agent perform? | One concrete request, evidence conditions, authored stochastic structure, resulting table and two analyses; distinguish Agent choices from statistical execution |
| 2: Scientific use | What can a user actually do with the data? | Complete CHNS/ENSANUT author profiles for adjusted effects and attenuation; reference intervals and generated variation; all planned endpoints |
| 3: Value of relationship information | Does evidence improve the data's analytical content? | Six E0/E1 contrasts and the fixed statistical reference; include the worsening BMI endpoint and the two comparator wins |
| 4: Input/method breadth | Does the capability extend beyond one fixed output? | Explicitly separate full-cohort, indicator-extension and longitudinal examples; label method versions and supplied vs withheld information |
| Supplement: downstream prediction and failures | Which historical results support practical utility and bound claims? | Full temporal classifier results; prospective failures; masks; dispersion and residual diagnostics; no pooled success rate |

A real-real context panel can accompany Figure 2, separately labelled as the earlier single evidence-to-generation construction rather than the core-replication authors. Predictive utility can move to the main paper only with sufficient room and an explicit distinction between rich training summaries and literature-only inputs. Source-replay checks support the method trace; they should not displace the main final-data results.

## Smallest next work, organized around the strengths

**First, integrate the evidence already obtained.** Create one claim-to-figure table using this synthesis, name the exact method version for each case, and retain complete endpoints and author profiles. The main information experiment and core replication can support drafting now. Historical positives add context, not more current-method trials.

**Second, resolve only the gap that changes the main claim.** If the intended claim is that one released workflow constructs useful data for several requests, select a small fixed set of existing cases by task/measurement coverage, specify the final workflow once, and check which records already use it. Only genuinely missing workflow coverage merits a replay. Reusing revealed references must be labelled developmental; it cannot repair the absence of a new transport confirmation. No new data acquisition is required for this inventory step.

**Third, pursue an additional mechanism comparison only if it explains the observed advantage.** The strongest candidate is whether the Agent can use incomplete conditional evidence to author a useful dependence structure, compared with a transparent fixed completion under the same information. Before execution, equalize admitted numerical evidence, budgets and analysis definitions. If the Agent prior is the only extra information, say so. This is a proposed explanatory test, not authorization to rerun or tune old outcomes.

Do not initiate further generic rubric/Agent layers, broad database acquisition, repeated source-only checking or endpoint-specific tuning just to strengthen the paper. An unsupported interaction can remain an explicitly unvalidated use. A claimed universal transport capability cannot be rescued by presenting only the successful endpoints.

## Safe stopping point

This synthesis is complete. The research focus is supported analysis-specific virtual-data construction, with evidence-to-model flexibility as the mechanism to explain. No additional model was generated or selected. The experimental record remains unchanged. The next substantive action is manuscript/figure integration and a method-version coverage inventory, rather than another open-ended generation round.
