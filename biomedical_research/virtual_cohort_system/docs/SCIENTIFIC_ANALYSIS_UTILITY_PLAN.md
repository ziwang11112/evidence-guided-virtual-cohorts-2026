# Evidence guided virtual data for downstream scientific analysis

Research and experiment plan, 29 October 2026. This is a proposed next-stage design, not a preregistration or a report of new experiments. No additional target outcomes were inspected to prepare it.

Scope clarified by the user on 29 October 2026 (local time): **the primary objective is feasibility and analytical utility of the evidence-guided data-generation method. A capable ordinary Agent is a valid implementation of this method. Superiority of a special Agent framework is not a prerequisite or the main paper claim.** The earlier three-arm, 30-table schedule is retained in the M9 historical preparation snapshot but is superseded for the next run by the feasibility-first protocol.

Execution update, 30 October UTC: the 12-table Stage B screen is complete; see [M10 results](../MILESTONE_10_RESULTS.md). It showed partial analytical reuse and clear relation-specific failures. The remaining stages below are prospective. The two released targets are now development observations and cannot serve as fresh confirmation of changes inspired by their results.

Post-M10 review update, 29 October local time: see the [PRO review verification and adoption record](PRO_REVIEW_ADOPTION_2026-10-29.md). The immediate decision is to make one study-statistic conversion concrete before expanding cases. Distinguish benefits from additional evidence, from its method of interpretation, and from reuse of a frozen generator. A same-evidence statistical reference is claim-specific; superiority of a special Agent remains outside the primary requirement. This update does not amend frozen historical protocols or announce a new run.

M11 execution update: the proposed source-location conversion has now been tested on a fresh HbA1c endpoint in NHANES 2021–2023; see [M11 results](../MILESTONE_11_RESULTS.md). Source calibration worsened target location and subgroup discrepancies in all paired outputs, while age/BMI slopes were preserved by the additive structure. Stop that scalar-calibration branch. The next proposal must address evidence for source-to-target transport, rather than improve source fit alone; no new confirmation target or successful extension is claimed yet.

## The paper we want to test

**Can an Agent convert heterogeneous external study evidence into reusable virtual data that support scientific analyses in a target population, including analyses whose answers were not provided to the Agent?**

A possible working title is **From Study Level Evidence to Virtual Cohorts for Scientific Analysis**. The broad system continues to support whole-cohort synthesis, entirely unmeasured-variable enrichment, and missing-cell completion. The first experimental track should emphasize enrichment: retain measured target covariates, hide an entire biomarker, generate that biomarker using external evidence, and apply the same analysis code to generated and reserved real data. Separate experiments are needed before claiming the other two settings work equally well.

The intended product is a generated table, a reusable generation program or documented direct-generation procedure, and a record of supporting evidence and assumptions. It lets an analyst run regression, subgroup comparisons, nonlinear analyses and conditional study-design scenarios without access to the source studies' participant records. A generated value represents a possible value under a specification, not a recovered measurement for that person.

The useful claim is analysis-specific. Agreement on an age association does not certify every interaction, tail probability, individual prediction or causal effect. Synthetic results can inform exploratory analysis and study planning; they are not independent biological observations establishing the hypotheses used to generate them.

## What the existing result contributes

The [M8 report](../MILESTONE_8_RESULTS.md) contains a completed feasibility experiment on 1,575 reserved NHANES 2009–2010 participants. Both inherited and revised generators preserved the positive adjusted age association and negative BMI curvature in all three residual draws. The revised mean age estimate was closer to the real-data estimate; curvature changed little, BMI effect strength remained excessive, and subgroup discrepancies improved or worsened depending on subgroup.

This gives us an executable example, a documented scientific review correction and selected successful unprovided analyses. It does **not** establish incremental directional benefit: the inherited generator already reproduced every global and ordered-contrast point direction. The six tables are not six independent cohort replications. Existing exposed periods and results are development evidence for subsequent method changes.

Negative curvature on log TG can also arise from a positive additive arithmetic mean. Therefore a curvature sign alone cannot establish that the full biological response shape was learned from joint evidence. Retain direction agreement as a central scientific outcome, but add magnitude, shape, subgroup and assumption-sensitivity checks to distinguish useful agreement from an easy consequence of the chosen formula.

## Candidate contributions and the experiments that would earn them

| Candidate contribution | Discriminating experiment | Supportable conclusion if successful |
|---|---|---|
| External evidence supports useful target analyses | Freeze generators before releasing target biomarkers; evaluate unprovided estimates across new tasks and populations | Evidence-conditioned virtual data preserve specified analyses under the tested information conditions |
| The output identifies assumptions that matter for use | Compare genuinely different, evidence-compatible structures and transport scenarios; test known-null and weak-effect worlds | The system can distinguish robust conclusions from assumption-dependent ones within evaluated settings |
| One generated artifact serves multiple downstream analyses | Freeze one recipe, then apply several analysis families without task-specific regeneration | The output is reusable across the evaluated analysis families |

A comparison of Agent workflows or a review-disabled ablation is optional. It becomes necessary only if we choose to claim that a particular workflow or component improves performance. An ordinary Agent successfully implementing the method counts as a successful implementation, not a failure of the research direction. A statistically calibrated uncertainty claim requires additional evidence; a provenance label, three random seeds or an LLM confidence score is not such evidence.

## Where the method could differ from existing work

The following primary works already cover important parts of the proposed idea. This is a focused positioning check, not an exhaustive novelty search.

| Work | Existing overlap | Implication for our claim |
|---|---|---|
| [G-Sim, ICML 2025](https://proceedings.mlr.press/v267/holt25b.html) | LLM simulator construction and revision with numerical calibration | Executable Agent generation and feedback iteration alone are not new |
| [SynthCraft, PLOS Digital Health 2026](https://journals.plos.org/digitalhealth/article?id=10.1371/journal.pdig.0001290) | Agent-driven biomedical synthesis, NHANES/TCGA examples, analytical and predictive utility | Neither biomedical application nor regression-result validation is sufficient differentiation |
| [SPADA, EMNLP 2025](https://aclanthology.org/2025.emnlp-main.525/) | LLM dependency structures coupled to fitted conditional generators | LLM-selected dependence followed by numerical generation is established |
| [AMSIPD, AJE 2025, online 2024](https://academic.oup.com/aje/article/194/7/2060/7762598) | Combines aggregate and individual data, generates aggregate-matched synthetic IPD and estimates target-population effects | Study summaries to synthetic individuals to scientific estimation also has statistical predecessors |
| [STEAM, NeurIPS 2025](https://proceedings.nips.cc/paper_files/paper/2025/hash/2ba023061bca4e2d3cbe9ceaeef37e43-Abstract-Conference.html) | Generation and evaluation oriented toward preservation of treatment effects | Scientific-estimand preservation itself is not a new evaluation principle |

The narrower candidate distinction is **interpretation of heterogeneous external evidence for a variable entirely unavailable in the target data, with traceable source-to-target assumptions and validation on unprovided scientific analyses**. The degree of automation must be reported as implemented. Framework superiority is a separate optional question. Do not claim a first method, a new statistical identification result, or a new biological mechanism from the present evidence.

General distribution fidelity and specific analytical utility have long been distinguished in synthetic-data evaluation; see [Snoke et al., 2018](https://academic.oup.com/jrsssa/article/181/3/663/7072005). Our information regime and evidence-processing mechanism must carry the contribution.

## Framework improvements to test

Use the existing Python harness and isolated generator execution. The research change is the scientific workflow, not a platform rewrite or a requirement for multiple permanent Agents.

1. **Define the use and information boundary.** Record the target population, observed variables, hidden variables, measurement context and broad intended analyses. The evaluation custodian separately freezes exact test analyses and their implementation. The builder must not see target answers, required effect directions or private reference summaries.
2. **Represent evidence in its original conditions.** Every numeric statement needs a source locator, population, measurement, transformation, adjustment set, estimand and uncertainty. Shared cohorts and repeated publications must remain linked. An adjusted log-scale ratio cannot silently become an arithmetic subgroup mean.
3. **Identify a consequential gap.** State which conditional relation, variability, interaction or measurement bridge is unsupported. Use the supplied literature tools when permitted. Record whether retrieval actually occurred or a curator supplied the evidence. A proposed search is not a completed search.
4. **Construct a small set of justified alternatives.** The Agent chooses structures and parameters from the admitted evidence and explicit assumptions. Alternatives must differ scientifically, not merely by random seed. No harness default should encode the desired BMI or age sign. The visible contract fixes the candidate and revision budget before construction.
5. **Check source statistics under their study conditions.** Replay the actual generator with a declared source-population approximation and the appropriate analysis operator where possible. Preserve noncomputable checks when covariates or operators are unavailable. In M8, the new adjusted joint ratios were not fully replayable; this remains a capability gap rather than a passed check.
6. **Review and revise using permitted information only.** Distinguish extraction, scale, individual variability, population transport, model structure and Monte Carlo discrepancies. Preserve initial candidates, failures and justified no-op decisions. Freeze a source-only selection rule; never select the best candidate or seed after target evaluation.
7. **Deliver reusable data and a use report.** The report links analysis families to supporting evidence, transfer assumptions and unresolved alternatives. These are declarations until empirical evaluation validates their usefulness. Release the exact generator, evidence hashes and revision record with the table where data terms permit.

Current components include evidence registration, freezing, isolated program execution, source replay and case-specific evaluation. A general analysis adapter, calibrated use labels, full uncertainty propagation and autonomous end-to-end evidence recovery are not established capabilities. The initial comparison can use a curated shared evidence packet; the retrieval experiment should be separate.

## Public-data cases

Data access was checked through official metadata and documentation; no new participant outcomes were downloaded or analyzed for this plan. A documented cycle is not automatically an unexposed cycle: audit prior project use before assigning a confirmation role.

| Case | Visible target data and hidden variable | Main scientific use | Role and access |
|---|---|---|---|
| TG | Age, sex, BMI; hide TG and its aliases | Adjusted association, BMI response shape, subgroup contrasts, tail behavior | Existing development anchor; [NHANES 2009–10](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2009/DataFiles/TRIGLY_F.htm) and [2021–23](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/TRIGLY_L.htm) have public files |
| Fasting insulin | Age, sex, BMI, measured fasting glucose; optional waist; hide insulin | Conditional insulin association and downstream HOMA-IR analysis | First proposed new task; [2017–18 insulin](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/INS_J.htm) and [glucose](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/GLU_J.htm) codebooks establish feasibility, not freshness |
| HbA1c | PNS age, sex, measured weight/height; optional prespecified history; hide HbA1c | Chronic glycemia associations and transport to a different national survey | First proposed independent-cohort task; [Fiocruz public PNS laboratory files](https://www.pns.icict.fiocruz.br/bases-de-dados/) and [dictionary](https://www.pns.icict.fiocruz.br/wp-content/uploads/2023/05/dicionario_de_variaveis_exames_pns_2013_05052023.xlsx) are available |

PNS provides a genuinely different survey. Its official laboratory ZIP responded successfully to a metadata-only request; the dictionary confirms HbA1c `Z034`, creatinine `Z025` and cholesterol measures. [Primary laboratory methods](https://doi.org/10.1590/1980-549720190004.supl.2) describe the laboratory collection and access. PNS interviews and laboratory collection occurred at different times; laboratory weights, selection and timing must enter the protocol. It is not a TG or fasting-insulin validation dataset.

Important case-specific checks before freezing:

- **TG:** exclude duplicate triglyceride fields and calculated LDL fields that, with total and HDL cholesterol, can reveal TG algebraically. CDC documents a 2021–23 assay/instrument change and bridging equations. Prespecify the measurement conversion and sensitivity rather than treating an assay difference as biological transport.
- **Insulin:** exclude unit duplicates and precomputed insulin-derived measures. Use fasting eligibility, the appropriate subsample weights and prespecified handling of treatment/exogenous insulin. HOMA-IR is a derived endpoint using glucose and insulin, not an additional independently measured validation. Its definition and units must follow the [original HOMA work](https://doi.org/10.1007/BF00280883); do not invent a universal cutoff.
- **HbA1c:** exclude PNS `Z035`, estimated average glucose, because it is derived from HbA1c. Treatment, anemia, hemoglobin-related measurement issues and interview-to-laboratory timing require explicit handling. Do not import hidden-biomarker diagnoses or other derived fields without a leakage review.
- **Source overlap:** exclude evidence calculated from the target survey in the strict external-evidence track. Record cohort overlap, source release dates and the limits of protection against model pretraining knowledge. Separate same-survey evidence settings if later studied.

PNS creatinine is a feasible reserve target if more biological diversity is useful, but requires a new evidence packet and a prespecified kidney-function definition. KNHANES is a reserve cohort pending verification of its current registration/download route; access is not yet established here. Existing TG plus two new tasks provides a feasibility series, not three independent confirmatory successes.

## Experiments in order

### Stage A Lock two task packages

For insulin and PNS HbA1c, first assemble source evidence without reading hidden target outcomes. A custodian records eligibility, units, aliases, design weights, available sample size and exclusions. Define a small set of priority scientific questions and reserve secondary analyses before generation. Record exact model formulas, contrasts, multiplicity treatment, nonestimability behavior and all amendments. Do not choose a new period solely because it produces a favorable result.

Classify every evaluation endpoint before unblinding:

| Endpoint class | What it demonstrates |
|---|---|
| A statistic explicitly supplied as evidence | Faithful implementation or calibration |
| A relation algebraically forced by supplied facts or the chosen model | A consequence of the specification |
| An unprovided target analysis requiring joint structure or population transport | The main analytical-utility test |
| A relation not identified by available evidence | Sensitivity to assumptions; robust support may be unavailable |

Audit the class assignment independently. A result does not become an independent discovery merely because the exact regression output was omitted from the prompt.

### Stage B Run the data method feasibility experiment

Use one capable Agent implementation to construct evidence-guided generators for both prepared tasks. It may use the existing checks and review tools. No separate ordinary-Agent competitor is required. The primary reference is the corresponding analysis on reserved real data, using the same analysis definitions.

Initial capacity template: **two tasks × two independent Agent constructions × three residual draws = 12 final target tables**. Each independent construction chooses its own justified structure using the permitted evidence. Changing only a residual seed is not a new construction. Select each final recipe using source-only information and report every construction, including failures. Counts exclude source-replay tables, intermediate versions and prespecified sensitivity scenarios.

Keep construction and revision limits fixed, record model settings and actual available cost information, and freeze before releasing target answers. Do not require a strict token-matched comparator to begin a feasibility experiment. A traditional evidence-constrained generator can later provide context or diagnose whether a particular evidence feature matters. Its absence does not block this first run; if added, choose its family before inspecting the relevant held-out outcomes.

Evidence-removal, review-disabled, direct-row versus program, and ordinary-versus-structured comparisons are optional mechanistic or implementation studies. They should answer a specific question that remains after feasibility results. A comparison introduced after screening is exploratory and needs fresh confirmation for a confirmatory superiority claim.

### Stage C Test reuse and failure boundaries

Use the same frozen generation recipe for several reserved analysis families: covariate-adjusted associations, nonlinear summaries, subgroup contrasts, and downstream derived indices where applicable. Avoid rebuilding a tailored generator for every endpoint.

Test a small set of evidence-compatible structures and transport scenarios. Freeze the structural alternatives, transport scenarios and their interpretation rules using permitted source information before inspecting any target results. Alternatives introduced after inspection are exploratory and require fresh confirmation. If alternatives fit the source evidence comparably but reverse a target conclusion, classify that conclusion as assumption-dependent. Additional random draws cannot remove this ambiguity. Conversely, stability across materially different plausible structures is stronger evidence than agreement across seeds of one formula.

Add a controlled study with realistic covariates but independently simulated source evidence and target outcomes. Include known nulls, weak effects, meaningful effects and source-to-target mismatch. This is where false-positive rates and interval coverage can be assessed against known truth. Repeat source and target sampling; residual-only replay measures a narrower conditional property. Keep simulated-world evidence distinct from biological findings.

An inexpensive synthetic-sample-size stress test should increase generated rows while holding source information fixed. Numerical variability may shrink; evidence uncertainty must not disappear. Do not report standard errors from arbitrary synthetic replication as additional clinical precision.

For estimands that can be calculated directly from the fitted evidence model, optionally compare numerical integration with table-based analysis. This diagnoses interoperability and Monte Carlo cost; it is not a prerequisite or a competition against a direct-analysis Agent. A table does not create information beyond its evidence and assumptions.

### Stage D Confirm only after a useful screen

Freeze the scientific workflow, selection rules, endpoints, substantive margins and permitted revisions before new confirmation tasks. A provisional feasibility-extension template is four to six new tasks, three independent constructions of the chosen method and three residual draws: **36–54 final tables**. Add comparator or component arms only for specific additional claims.

These numbers are workload estimates, not a power calculation. Determine the required tasks and constructions from pilot variation and the precision needed for the intended claim. Tasks sharing participants, source studies or a survey are clustered; four to six tasks still support only limited generalization. Screening targets cannot become fresh confirmation targets after they inform method changes.

## What to measure

Keep the main presentation in scientific units and conclusions rather than one mixed-unit leaderboard score.

1. **Scientific conclusion agreement:** positive, negative, substantively negligible or indeterminate, using prespecified effect margins where defensible. A confidence interval crossing zero does not by itself establish absence. A result is indeterminate unless it satisfies a prespecified criterion for substantive negligibility or another supported conclusion. Until generated uncertainty is justified, report point-direction agreement separately from evidence-supported conclusions.
2. **Scientific adequacy:** effect magnitude, selected curve contrasts, subgroup ordering and consequential disagreement. Exact numerical equality is unnecessary; a correct sign with twice the association strength can still mislead an analyst. If no defensible tolerance exists, report discrepancies without declaring equivalence.
3. **Reuse:** which unprovided analysis families remain supported by one frozen output, without new outcome feedback or task-specific regeneration.
4. **Robustness and error behavior:** model/transport sensitivity, reference-inconclusive claims, reference-contradicted claims, failed construction and nonestimable analyses. Reserve the term false positive for settings where the truth is known sufficiently well.
5. **Practical cost:** construction time, tools/tokens, source acquisition, human review, failure recovery and cost per usable task. A faster workflow with comparable utility may be a useful result.

Source-statistic residuals, distributions and implausible values remain diagnostic checks. They are not substitutes for downstream utility and should not disappear merely because the main endpoints are conclusions. Avoid rewarding perfect source fit when unprovided analyses deteriorate.

Analyze generated-versus-real analytical agreement and failure patterns at the task/cohort level, retaining endpoint-family detail. If methods are compared, report paired differences separately. The hierarchy is cohort/task, independent construction, evidence/model scenario, residual draw, and endpoint. Do not treat generated rows, correlated endpoints or seeds as independent scientific replications. Real-data estimates have sampling uncertainty; containment in their confidence intervals does not establish equivalence.

Keep residual randomness, source-estimate uncertainty, structural uncertainty, transport uncertainty and target sampling uncertainty separate. Unknown shared-reference covariance cannot be replaced automatically by independent draws. Scenario ranges are sensitivity results unless probabilities are justified. Multiple-imputation pooling rules require appropriate assumptions and compatibility; they are not automatically valid for Agent-filled entire columns. See [Xie and Meng, 2017](https://www3.stat.sinica.edu.tw/statistica/j27n4/J27N41/J27N41-10.html).

## Separate evidence retrieval from evidence use

The first run uses curated source packets to test evidence-to-data feasibility. A later retrieval experiment can assess recovery of relevant sources, extraction correctness and eventual analytical utility. Archive retrieved sources and adjudicate their eligibility without target answers. If workflows are later compared, equal information or an equal-search-budget design helps distinguish better acquisition from better reasoning. Do not attribute richer information to a superior generation mechanism.

The current M8 supplement recovery involved an external source-curation phase. The next paper must truthfully describe which steps were autonomous, tool-enforced, procedurally separated or manually curated. Private GitHub should contain code, protocols and permitted aggregate results; participant rows and restricted source artifacts remain outside exports.

## Paper figures and decision gates

| Figure | Scientific purpose |
|---|---|
| 1 | Define available evidence, unmeasured target variables, generation and locked analytical evaluation |
| 2 | Show a worked evidence-to-generator example, source differences and a consequential reviewed correction |
| 3 | Compare real and generated scientific estimates across tasks, with direction and magnitude visible |
| 4 | Demonstrate reuse for nonlinear and subgroup analyses; show unfavorable and indeterminate results |
| 5 | Show which conclusions survive changes in evidence coverage, generation structure and transport assumptions |
| 6 | Show uncertainty/error behavior, construction variability and practical cost |

Start Methods and the reproducibility package now; write a definitive Results narrative after the feasibility screen. A methodological submission needs a useful and differentiated research question, a carefully demonstrated capability and its limits, and validation beyond one convenient relationship. Agent use and many figures do not determine journal level. Feasibility alone is not an automatic novelty or publication guarantee, but beating an ordinary Agent is not required for this data-method claim.

Continuation rules:

- **Advance the data-method claim** if generated data support useful unprovided target analyses across the tested cases, remain adequate under credible alternatives, and have clearly characterized failures. Freeze the exact success rule before confirmation.
- **Accept a simple implementation** if an ordinary Agent achieves this. Describe the evidence-to-data method and its empirical utility without claiming a superior Agent architecture.
- **Restrict the use** if source-compatible alternatives disagree or synthetic certainty is unjustified: use scenario exploration and hypothesis prioritization while repairing the inferential component.
- **Stop or revise the scientific claim** if success consists only of supplied relations or built-in functional-form consequences, or unprovided analyses remain unreliable. A simpler implementation performing equally well is a reason to simplify, not by itself a failure of evidence-guided generation.

The two reviewed task packages and **12-table feasibility screen** are now complete. Next, freeze an evidence-coverage and analytical-applicability experiment using fresh confirmation data, preserving the M10 failures and all development changes. A conventional-generator specification and ordinary-Agent superiority comparison remain optional, claim-specific studies. This scale needs neither new foundation-model training nor HPC; larger uncertainty simulations can be parallelized later if they become the actual bottleneck.
