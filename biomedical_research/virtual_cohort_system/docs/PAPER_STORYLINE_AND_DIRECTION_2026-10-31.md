# Paper storyline and research direction

Date: 2026-10-31. Design note following the [G-Sim / LLMSynthor deep review](GSIM_LLMSYNTHOR_DEEP_REVIEW_2026-10-31.md). This is a proposed manuscript argument, not a report of completed new experiments or established novelty.

## Recommended direction

**Turn published biomedical evidence into reusable virtual data for scientific analysis.**

Working title: **From Published Evidence to Virtual Cohorts for Scientific Analysis**.

Scope clarified by the user on 2026-10-31: **the method must include complete virtual-cohort generation when no individual-level data are available.** An existing cohort is optional. A target population can be specified by its eligibility, setting, variables and measurement definitions without a table of participants.

The paper studies evidence-driven generation under different amounts of available individual data. Evidence-only full-cohort generation is a core intended capability, not merely a future extension of missing-column imputation. Whole-column augmentation remains a valuable existing pilot and validation setting; partial-cell completion is another supported problem formulation. Which capabilities the final paper can claim will depend on completed experiments, but the research scope must not assume target covariates are always available.

| Information regime | Inputs permitted to the generator | Intended output | Appropriate reference comparison |
|---|---|---|---|
| Evidence-only full-cohort generation | Target-population description and external published aggregate evidence; no target or source individual records supplied | A complete virtual cohort, jointly generating the requested variables | Population distributions and scientific analyses on a reserved complete real dataset; no row-wise matching |
| Whole-column augmentation | External evidence plus observed target covariates; one or more variables entirely unmeasured | Virtual variables conditional on the observed participants, preserving observed cells | Identical analyses on augmented versus complete reserved data |
| Partial-cell completion | External evidence plus an incomplete individual table | Multiple plausible completions of missing cells, preserving observed cells | Analysis-level validity under explicitly defined missingness conditions |

These regimes share a method interface: **published evidence + population specification + optional observed data → executable joint/conditional generator → virtual datasets → scientific-use evaluation**. They should be reported separately because observing target covariates provides information unavailable to evidence-only generation. If any individual source records are supplied in an additional experiment, identify that as a separate information tier.

The technical focus currently worth testing is a generator that respects the population, measurement and analysis conditions attached to each published result. This is the method's potential technical contribution, while the scientific purpose is usable virtual data. Neither a large role diagram nor the number of Agents defines the research question.

## 1. What the two precedents do narratively

The following is our reconstruction of their published argument. It does not claim to know the authors' private discovery process or why reviewers accepted the papers.

| Argument stage | G-Sim | LLMSynthor | Transferable writing lesson |
|---|---|---|---|
| Practical need | Build simulators that support system-level experimentation | Obtain useful micro-records when aggregate information is available | Begin with the user's unavailable capability |
| Technical tension | Domain-plausible structures need empirical grounding and usable stochastic behavior | Plausible individual records need population-level statistical alignment and scalable generation | Identify one central tension rather than list unrelated deficiencies |
| Organizing idea | LLM structure search plus numerical calibration and refinement | Dependency-aware macro constraints plus compact sampling proposals and discrepancy feedback | Explain why the components belong together |
| Method organization | Requirements P0–P3 connect to structural, calibration and refinement roles | Dependency selection and iterative synthesis form two main methodological parts | Map requirements to operations the reader can inspect |
| Empirical support | Known simulator fidelity, ablations, interventions and policy-use demonstrations | Mobility RQ1, controlled e-commerce RQ2, variable-length ACS households RQ3 | Every experiment should answer a stated research question |
| Broader value | An executable simulator can be edited and used for decisions | Generated records can support downstream tasks and queries | Show what the output enables after generation |

Sources: [G-Sim, Introduction, §2–3 and §5–6](https://proceedings.mlr.press/v267/holt25b.html); [LLMSynthor, Introduction, §3–4](https://arxiv.org/html/2505.14752v3).

G-Sim's title and introduction name the useful research object before detailing its implementation. Its explicit properties—system experimentation, plausible generalization, empirical alignment and faithful data forms—give the reader a way to judge the method. LLMSynthor's Figure 1 first visualizes the problem and proposed capability; Figure 2 then explains execution. Its experimental section explicitly maps three applications to three research questions.

We should reuse that alignment of problem, mechanism and evidence. We should not repeat unsupported introductory generalizations, such as implying every classical synthesis method requires individual records, or borrow their strongest empirical claims without the qualifications documented in our audit.

## 2. Our paper's central argument

### Opening example

A researcher wants to analyze an adult population using age, sex, BMI, glucose and insulin but has no participant table. Published studies supply partial distributions, associations and subgroup results, under differing population, measurement and adjustment conditions. The intended method constructs a joint generator and produces a complete virtual cohort from this evidence and a target-population specification.

The same method can use an existing cohort when one is available. For example, it can preserve observed age, sex, BMI and glucose while generating an unmeasured insulin column. This conditional case provides a useful validation path but does not define the entire project.

For evidence-only validation, the evaluator can hold a complete independent real dataset while the generator receives none of its participant rows. Any permitted target descriptions or aggregates must be declared; hidden target distributions cannot silently enter as sampling templates. Compare scientific analyses and population properties, rather than pairing generated individuals with real participants. Where no real reference exists, source compatibility and sensitivity can be assessed, but target fidelity remains unvalidated.

### Six-sentence story

1. Individual biomedical data can be entirely unavailable, costly, restricted or incomplete, limiting the analyses researchers can conduct.
2. Published research contains relevant evidence that remains difficult to reuse as individual-level analytical data.
3. That evidence constrains distributions only partially and under different study conditions; producing plausible rows or matching pooled summaries does not settle the target joint relationships.
4. We investigate an Agent-based method that converts those study-conditioned results into an executable generation process and checks its implications against permitted evidence.
5. The resulting frozen data are evaluated by the scientific analyses they support, including analyses that were not used to fit or revise the generator.
6. The study reports where useful relationships transfer, which methodological operations account for that behavior, and where evidence remains insufficient.

The broad conceptual framing is **data generation as a way to operationalize distributed scientific evidence**. This is a research framing, not a claim that evidence synthesis or aggregate-data generation is new.

## 3. Three contribution slots, each requiring evidence

| Proposed contribution | Concrete content | What would substantiate it | Current status |
|---|---|---|---|
| A well-defined generation problem | External study results and target-population specifications are available; individual records may be entirely absent or partially observed | Separate information contracts for full-cohort generation, column augmentation and cell completion; overlap audit and meaningful scientific use | Scope includes all three regimes; pilots so far do not establish evidence-only full-cohort performance |
| A reusable evidence-to-generator method | Agent interprets evidence and proposes structure; tools execute source-conditioned analyses and numerical calibration; source-only feedback supports revision | Correct extraction/operators and a mechanism comparison showing when these operations help | Candidate technical direction; not a proven novelty claim |
| Demonstrated analytical usefulness and limits | Frozen generated datasets support several prespecified target analyses and make uncertainty/unsupported relationships visible | Independent reference data, effects and functional forms, controlled truth, repeatability and failure cases | M16 provides selected feasibility and a repair trade-off, not broad superiority or publication readiness |

The contributions should be written around achieved results at submission time. If an ordinary Agent or simpler statistical implementation works equally well, use that finding to simplify the method and narrow the claim. A comparison with naive pooling alone cannot establish superiority over competent condition-aware statistical synthesis.

## 4. Experimental questions that build the argument

These are a proposed proof structure, not a frozen benchmark or a requirement to implement every extension immediately.

| Research question | Experiment | What it distinguishes |
|---|---|---|
| RQ1: Can evidence-generated data support useful scientific analysis? | Evaluate full-cohort generation with all individual records withheld, and separately evaluate column augmentation; run identical analyses on frozen virtual and reserved real data | Source-fitting success versus analytical usefulness under explicitly different information regimes |
| RQ2: Does respecting study conditions matter? | Controlled compatible versus heterogeneous source populations/measurements; compare ordinary and condition-aware handling with matched inputs | A concrete mechanism effect rather than a different LLM or extra information |
| RQ3: Does the same generator support more than its fitting objectives? | Freeze once; evaluate unprovided adjusted relations, nonlinear shapes and subgroup analyses across independent cases | Reusable data versus individually fitted answers |
| RQ4: How does usefulness change with evidence and cost? | Vary evidence completeness, access to observed covariates, source conflicts or revision budget in development settings; track fit, reserved use and actual resources | Information limitations, helpful revisions and diminishing returns |

A few well-chosen cases can answer different questions more convincingly than many nearly identical cohorts. Use multiple controlled mechanisms and genuinely distinct real cases when expanding. A different cycle of the same survey is useful evidence of temporal transfer, but should not be presented as an unrelated study family.

Biological fidelity includes association direction, meaningful effect magnitude, nonlinear shape and subgroup behavior. Distributional checks remain useful diagnostics. Neither a matching sign nor a low aggregate error alone establishes scientific equivalence. Statistical significance should not become the sole success label.

Evidence uncertainty and uncertainty about an unobserved relationship differ from random variation across generated rows. More generated records do not create more measured participants. Any claim about inference or study-design reliability needs uncertainty appropriate to that claim.

## 5. A possible figure and table sequence

This is a planning device; the final number of figures should follow the evidence and venue constraints.

| Display | Reader's question | Content |
|---|---|---|
| Figure 1: problem and new capability | What can a researcher do with this method? | Population specification + condition-labelled published evidence + optional observed data → complete virtual cohort or augmented dataset → several scientific analyses; visibly distinguish observed and virtual values |
| Figure 2: method | How is the capability produced? | Evidence interpretation, generative proposal, deterministic source checks, calibration/revision, freeze and separate reference evaluation |
| Main results table / Figure 3 | Does it work across cases and analyses? | Effects or curves with uncertainty where justified, direct constraints versus unprovided analyses, failures retained |
| Figure 4: mechanism | Why does the proposed evidence handling matter? | Compatible/heterogeneous sources; source-fit and reserved-analysis trajectories; targeted ablations |
| Figure 5 or application panel | What does useful generated data enable? | A coherent biomedical secondary-analysis example using the frozen output; distinguish reproduced, externally validated and exploratory findings |
| Supplement | Can someone verify and reproduce it? | Evidence objects, source-condition mappings, prompts, algorithms, information budgets, extraction audits, all endpoints and resource records |

Figure 1 should explain the scientific task. A dashboard of many Agent roles would not by itself communicate the contribution. Figure 4 should explain an observed result, rather than serve as a collection of unrelated ablations.

## 6. Introduction, abstract and Results writing

### Introduction in five moves

1. Give the unavailable-individual-data example, followed by the optional incomplete-cohort case, and explain the analyses these gaps prevent.
2. Explain why published statistical evidence is a reusable resource, with a precise boundary relative to raw-data-trained generators and existing macro-statistic synthesis.
3. State the central challenge: study-conditioned partial evidence does not directly identify the target joint distribution or guarantee useful downstream analysis.
4. Explain the proposed method's main operation and why Agent interpretation plus deterministic statistical execution is appropriate.
5. State only the contributions and empirical claims the completed study actually supports.

The technical machinery should answer the challenge already introduced. The introduction should not promise all biomarkers, all populations, individual truth recovery, clinical replacement, universally beneficial revision, or a new biological mechanism inferred solely from synthetic output.

### Abstract scaffold, with no invented result

> Biomedical individual-level data are often unavailable or incomplete, while relevant evidence is distributed across published studies. We study whether this evidence can support generation of virtual cohorts, with optional conditioning on existing measurements. [Method] represents source populations, measurement definitions and analysis conditions, and uses an Agent to construct a generator with statistically executable evidence checks. We evaluate [completed information regimes, tasks and cases] using reserved real measurements and analyses excluded from generation feedback. [Actual quantitative findings and a material limitation.] These results characterize [the demonstrated scope of scientific usefulness].

Fill the results only after evaluation. Do not write a positive result first and then select endpoints to match it.

### Results section logic

Organize around findings: analytical usefulness, transfer across study conditions, evidence for the mechanism, and limits. Implementation chronology belongs in a development log. When a mechanism fails, report it where it changes the interpretation of the main result.

Cost claims should use measured compute, token consumption and any measured human effort. This project has not established that generating rows eliminates the need to collect patient measurements. A supportable initial utility claim concerns enabling exploratory analyses and study-design work under explicit evidence assumptions.

## 7. Direction and next milestone

The primary route is an AI-for-science data-generation methods paper with substantive biomedical validation. This is a proposed genre and proof structure, not a prediction of acceptance by ICML, KDD or a journal. A biological-discovery paper would require a separate discovery-and-validation argument; adding synthetic rows alone would not supply it.

The next milestone should include an evidence-only full-cohort condition in the controlled test, alongside a separately labeled observed-covariate condition where useful. It should establish whether evidence handling changes analytical usefulness and what information each result depends on, then extend to fresh independent real cases if justified. These are proposed tests, not newly completed capabilities. The broad direction stays stable while the exact sampler, Agent organization and optimizer remain replaceable design choices.

We can draft the opening example, problem definition and Figure 1 specification now. A results-bearing manuscript should follow the first coherent mechanism test and independent cases. Previous pilot findings remain part of the record; they are not fresh validation targets.

No new experiments, target downloads, paid model calls, training or HPC jobs were launched for this narrative-design note.
