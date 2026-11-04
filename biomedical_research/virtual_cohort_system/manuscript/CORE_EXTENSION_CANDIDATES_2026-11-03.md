# A focused extension from the completed experiments

3 November 2026. **Status: proposed research direction, not an implementation or released experiment.** This review uses existing authored reports and aggregate scientific records. No patient/generated table, new target effect, download, new original paper, generator or fitter was accessed or run. The v0.8 manuscript and frozen studies are unchanged.

**Recommendation: investigate one capability — choosing which missing joint evidence to obtain for a requested analysis, then generating the complete cohort from the augmented evidence.** Do not add another generic revision selector. The contribution would have to be demonstrated through the analyses of the generated data, not evidence-map completeness or how many papers the Agent selects.

This is a candidate for strengthening the research. It does not establish new active-design theory, field priority, biomedical validity or a top-venue result. The companion [neighbor audit](TOP_VENUE_NEIGHBOR_AUDIT_2026-11-03.md) must govern predecessor claims.

## What the existing experiments actually suggest

| Retained observation | Implication for a new experiment |
|---|---|
| [Main-study A01 trace](SUPPLEMENT_SOURCE_AND_ASSUMPTIONS_v05.md): two source HbA1c projections were converted into a joint response law through an assumed residual correlation of 0.25. The constrained projections were reproduced, while target BMI, glucose and age agreement differed. | Reported relationships can genuinely enter a model, but the unreported joint component still controls downstream analyses. A useful next operation concerns the missing information, not simply a larger generated sample. |
| [C3](../docs/C3_SOURCE_CONSTRAINED_GENERATION_RESULTS_2026-10-31.md): the alternative structure's fitted aggregate discrepancy decreased on the fitting seed but increased on both unused seeds, introducing age-slope failures. | Lowering a scalar source score does not establish improved analytical use. Another optimizer/weight sweep would repeat an already observed trade-off. |
| [C4](../docs/C4_REVISION_ACCEPTANCE_RESULTS_2026-10-31.md): every proposal was a truthful retention; all three selectors chose identical models. Two compatible invented worlds still implied opposite adjusted effects. | The experiment demonstrated an information limitation, not selector benefit. A new selector with no genuinely different information or candidates is uninformative. |
| [M7](../MILESTONE_7_RESULTS.md): six queries found relevant joint sources, but missing supplement/scaling/adjustment information prevented a quantitative update. The analysis map was prepared after retrieval. | This was a gap-directed search, not a controlled demonstration that an executable pre-search acquisition policy improved data quality. Semantic compatibility matters as much as topical relevance. |
| [M8](../MILESTONE_8_RESULTS.md): recovering the original 28 joint ratios enabled a reviewed interaction construction. Age magnitude improved on average, while BMI magnitude and some subgroups worsened; the baseline already retained the priority directions. | Obtaining a joint table can change the generator, but this does not isolate why that item was worth obtaining or show that any added joint evidence helps the requested analysis. |
| [Adaptive CHNS pilot](../reports/adaptive_reference_pilot_2026-11-03/RESULTS.md): a dependence repair brought Spearman agreement closer but slightly worsened all three regression discrepancies. | Once information is present, representation or update geometry can still cause trade-offs. Evidence acquisition is not automatically the explanation for every remaining error. |
| [CHNS supplied-summary study](../reports/information_revision_ablation_2026-11-03/RESULTS.md) and HRS public model: useful reconstruction became possible with richer quantitative information. | The system can make sufficiently informative evidence computationally useful. A new experiment should ask which additional information produces that benefit under a bounded acquisition budget. |

These observations are developmental and already exposed. They motivate a prospectively designed mechanism test; they are not its test results.

## Preferred capability: analysis-directed acquisition of joint evidence

Consider a researcher requesting a complete virtual cohort for an age/sex-adjusted association or interaction. Existing papers provide several margins and separate projections. Two or more complete joint models fit those reports but produce different answers to the requested analysis.

The new operation is to use that disagreement to decide which additional *reported scientific statistic* is worth retrieving. The first controlled pilot uses simulated source reports; a later literature application would require actual observed estimates from the admitted papers. The Agent should ask, for example, whether a joint covariate correlation, an appropriately adjusted coefficient or a subgroup contrast would distinguish the competing completions. It must preserve the candidate study's population, measurement, transformation and adjustment set. A statistic with the right variable names but the wrong statistical meaning may provide little usable information.

After the additional item is acquired, the system incorporates it through a bounded, common update procedure and generates the full dataset. The researcher still receives analyzable virtual data. The acquisition decision is an internal step toward improving that data product.

### Changed operation

1. Receive the intended analysis definition, full allowed base evidence and candidate-source metadata. The research question is visible; the reference answer is not.
2. Construct a small set of scientifically distinct, base-evidence-compatible joint completions. Record exactly which unreported quantities differ. Do not treat different random seeds or renamed copies as different models.
3. Compute each candidate model's requested analysis and its predicted candidate-source statistics under the source conditions.
4. Choose one additional admissible evidence item based on how it can discriminate the completions that matter to the requested analysis. Candidate numeric results remain inaccessible until this selection.
5. Retrieve the actual reported item from the fixed evidence pool, integrate it using its actual operator/context, then deliver a complete virtual cohort through the same execution path.
6. Evaluate the resulting data using the prespecified analysis and the already supplied constraints. Retention and unresolved ambiguity are legitimate outcomes.

The Agent still authors scientific structure and parameters. A numerical tool can compute model implications and an acquisition score. This does not require multiple permanent Agents, a trained foundation model or a new loss.

The exact acquisition criterion is a design choice to freeze after the prior-art review. Candidate-model disagreement is not automatically a calibrated posterior. Equal model weights, interval widths or worst-case reductions must be labelled as explicit design conventions unless separately justified.

### Rival explanations to distinguish

| Possible reason for present errors | What the new evidence could change | Observation that would argue against this extension |
|---|---|---|
| Missing joint information | A useful acquired operator reduces ambiguity about the requested analysis. | Additional information does not distinguish the candidate predictions or improve generated-data analysis. |
| Misinterpreted operator, adjustment or measurement | Context-aware interpretation admits or transforms the right quantity. | The method still treats contextually different statistics as interchangeable. |
| Wrong family/completion assumptions | New evidence reveals that the candidate set lacks a useful model. | Even a diagnostic full-information construction cannot represent the required relation; evidence selection is not the principal bottleneck. |
| Population-transfer mismatch | Acquisition from an applicable source may help if a defensible transfer is available. | Correct source interpretation still fails in the new population. The mechanism pilot cannot settle this clinical issue. |
| Numerical sampling or update trade-offs | More careful common updating may preserve previously supplied relations. | The selected evidence is useful, but the resulting update damages existing analyses, reproducing the C3/adaptive problem. |

## One bounded first experiment

This is a **triage proposal**, not an executable frozen protocol. The root task must set the final inputs, budgets, criterion and stop rule before implementation.

### Data and tasks

Use two new, independently committed, low-dimensional known-law configurations represented as short study-like text and metadata. They are invented mechanism fixtures, not patient data or new biological evidence.

- **Joint-completion task:** margins and separate relationships leave a requested adjusted analysis ambiguous. Candidate evidence includes a useful cross-variable statistic and plausible but largely redundant information.
- **Source-context task:** apparently similar candidate relationships differ in population, measurement or adjustment conditions. A correctly interpreted item can constrain the requested analysis; variable-name matching alone is insufficient.

No selectable item should directly print the exact requested target coefficient. Otherwise this acquisition test collapses to copying a supplied answer. This restriction belongs to the mechanism test, not to the overall method: legitimately accessible target summaries remain valid construction inputs, as in the existing CHNS R study. Include plausible context twins, and fix the scenarios before testing either method. Do not design or replace them after seeing a favorable result.

The candidate corpus has explicit metadata and a finite number of accessible items. The full numerical contents of unselected items remain hidden from all acquisition policies. No internet search or new patient access is necessary for this initial test. Restricting acquisition to a fixed corpus is a limitation of this mechanism test, not a claim of free-form literature-search competence.

### Finite comparisons and budget

An illustrative ceiling is **24 final tables**:

> 2 task configurations × 3 acquisition policies × 2 independently authored initial model pools × 2 final sampling seeds.

The two sampling draws probe Monte Carlo variation; they are not independent scientific tasks. Intermediate model evaluation and any trial execution must receive a separate explicit budget before release, rather than being hidden behind the final-table count.

All policies use the same committed initial model pools, full base evidence, allowed candidate metadata, source-context tools, one-item acquisition budget and downstream integration procedure:

1. **Capable ordinary Agent:** a normal request to obtain useful additional evidence and generate the requested data. It may reason about ambiguity and use the same numerical tools; it is not forced to ignore metadata or prevented from discovering the proposed strategy.
2. **Numerical active-evidence policy:** a fully specified finite rule operating on the same admissible operator predictions and model pool. It should retain source context and be chosen from the closest relevant goal-oriented design alternative in the prior-art check. A maximum raw-disagreement heuristic may be a diagnostic, but is not automatically a sufficient published-method comparator.
3. **Proposed analysis-directed Agent policy:** explicit comparison of joint completions and acquisition according to the requested analysis and source meaning.

The initial pools are paired across policies. The post-acquisition procedure is common, so additional model calls or unconstrained repair do not create an artificial policy advantage. Identical acquired evidence and identical resulting models must be counted as identical outputs where appropriate.

A full-information/known-law calculation can diagnose whether the task is solvable and whether the generator family can represent it. Such privileged information is an upper-bound diagnostic, not a competing method under the same information budget. If it requires additional generation, those tables must be separately authorized and counted; they are not silently added to the 24-table plan.

### Proposed total budget, not just final tables

The following ceilings make the illustrative 24-table design bounded. They are design proposals to review before release, not permission to start execution:

| Operation | Proposed maximum | Counting and restriction |
|---|---:|---|
| Independent initial pools | 4 | Two configurations by two scientific author contexts; each pool is shared across the three policies. |
| Initial authorship/diversity attempts | 8 model turns total | At most two turns per pool, yielding at most three frozen completions per pool (12 laws total). A duplicate or analytically indistinguishable pool stops before policy comparison; no manual diversity injection or replacement author. |
| Initial operator diagnostics | 288 operator calculations | At most 12 permitted operators per candidate, at most two passes, across at most 12 laws. This includes the requested model-implied analysis. Calculations use submitted model implications, not hidden reference answers. Repeated cached reads do not create new evidence. |
| Evidence-selection events | 12 | Three policies by four pools. At most eight model selection turns (ordinary/proposed policies) and four deterministic policy calls. No uncounted retry or additional source search. |
| Actual evidence acquisition | 12 one-item disclosures | One item per policy/pool, from the fixed corpus. Identical items are not twelve independent sources. Unselected numerical contents remain hidden. |
| Post-acquisition integration | 24 model turns total | At most two turns per policy/pool: initial integration and at most one common source-feedback correction, both before final freeze. Retention is allowed. All three policies receive the same update budget and scientific freedom. |
| Post-acquisition operator diagnostics | 288 operator calculations | At most 12 permitted operators for each of at most 24 proposed updated laws. No target answer or unselected source value enters these diagnostics. |
| Final cohort execution | 24 tables | One selected law per policy/pool, two fixed seeds, provisionally 5,000 rows each. Any failed slot remains failed; no replacement seed. |
| Other patient-like tables | 0 | This first mechanism test requires analytic operator evaluation for the admitted low-dimensional families. If a necessary operator instead needs source-table simulation, the plan must explicitly count that work before release; it cannot be silently added. |

Thus the illustrative ceiling is **40 model turns, 12 acquisition events, 576 operator calculations and 24 final tables**, with failure and retention consuming their scheduled opportunities. The eventual executable protocol must define the precise operator set and account for all attempts, wall-clock work and model/tool usage. Neither 24 tables nor 120,000 invented rows means that many independent validations.

**No-new-evidence assessment.** Each initial author nominates a preferred base-evidence law before any candidate item is revealed. Its requested analysis and existing constraints are assessed analytically as a shared pre-acquisition reference. This gives a no-acquisition comparison without eight extra generated baseline tables. Analytic baseline quantities and finite-sample generated estimates must retain their different precision meanings. If matching finite-table baselines becomes necessary, those additional outputs require an explicitly revised table budget; they are not part of the 24-table proposal.

**All-eligible-information feasibility check.** The independent custodian examines whether the complete allowed operator set, with the actual source contexts, is compatible with the committed generating world and can constrain the requested analysis within the declared task assumptions. This is an analytic design diagnostic, not a perfectly informed Agent and not proof that the author-selected family can represent the truth. If all eligible information still leaves the analysis ambiguous, retain that limitation rather than calling the check an oracle. Any later full-information Agent generation would be an additional, separately counted condition.

### Data-use outcome and falsifiers

**Primary outcome:** absolute discrepancy of the prespecified scientific analysis applied to the final generated cohort against the known-law quantity, reported in the analysis's fixed natural units. Do not normalize by a near-zero true effect or choose a tolerance after observing results.

Also retain:

- the existing source-operator discrepancies, to expose damage to already supported relationships;
- model-pool disagreement before and after the actual acquired item;
- every selected item, its actual population/measurement/adjustment meaning, and whether the information genuinely entered the final law;
- all invalid, unchanged and failed constructions;
- actual scientific model authors, model calls, acquisition items and numerical work.

Evidence selection accuracy alone is insufficient: the selected information must produce data whose requested analysis is better supported. Conversely, a smaller uncertainty proxy with an unchanged or worse generated-data analysis is not success.

Stop or simplify if:

- the initial pool contains no genuinely distinct compatible completions;
- no eligible item can change the requested analysis under those completions;
- the ordinary Agent already selects and integrates the same information with equivalent quality;
- the numerical active-design rule matches the proposed policy, leaving no distinct policy contribution;
- new information improves one score but breaks required scientific relationships;
- the apparent gain disappears when information and computation budgets are matched.

With only two controlled tasks, even favorable results justify a broader feasibility evaluation, not a paper-level claim of general performance or clinical utility. A null result should end this proposed selection component without another selector, task replacement or budget expansion.

## Why this is not another run of C3, C4 or M8

C3 fitted parameters against a fixed evidence set. C4 selected among unchanged proposals without obtaining new information. M8 added one externally recovered joint table and assessed its consequences, without a controlled choice among evidence items. The proposed manipulation is **which source-qualified observation becomes available before final cohort construction**, with all downstream policies and budgets held fixed.

This difference is worth testing, but it does not establish novelty by itself. The neighbor audit already identifies close operations in LLMSynthor's missing-joint/statistic expansion and G-Sim's refined diagnostics. Active experimental design is a direct conceptual predecessor. The paper would need to show a repeatable evidence-to-data capability across difficult operator/context conditions, not just that more informative input helps.

## Alternative considered but not recommended as the next headline

**Constraint-preserving generator revision** could try to add a rank/dependence or subgroup property while preserving already supported regressions and margins. The adaptive CHNS result makes this useful in principle. However, C3 already explored calibration trade-offs, C4 already tested a protected-use selection rule, and M8 already used a carefully designed interaction construction preserving reference-line curves. Generic constrained optimization or a new acceptance wrapper would therefore be a weak new headline without a substantially different and broadly useful operation.

Retain this as a possible implementation requirement inside the common update stage, not a second research campaign. It must not hide the lack of new information or force an arbitrary generator to satisfy incompatible evidence.

## Available resources and later evidence

Existing source-context execution, declarative operators, analysis maps, evidence manifests and isolated sampling provide reusable infrastructure. Their existence does not mean the proposed acquisition policy or discriminating model pool is already implemented. The initial controlled test needs no new biomedical cohort.

For a subsequent real-evidence capability test, the already retained Jansen/Pani/Bao/MIND or Tromso material can support a fixed-corpus demonstration, with its historical exposure and measurement limitations stated. The clinical reference outcomes are already known and cannot be labelled new confirmation. The [three-candidate feasibility audit](EXISTING_REFERENCE_FEASIBILITY_v07_2026-11-03.md) admits no fresh independent target; HAALSI lipids remains only a qualified metadata lead.

A stronger empirical paper would later need repeated task families and, for a transport claim, a separately admitted prospective target use. Neither requirements nor specific sample counts should be invented from a venue label. The immediate decision is narrower: does the proposed evidence-acquisition operation actually make generated data more useful than competent alternatives under the same information budget?
