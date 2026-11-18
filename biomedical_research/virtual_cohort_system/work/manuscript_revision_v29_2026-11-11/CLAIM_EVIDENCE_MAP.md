# Core story and evidence map for manuscript v0.29

Independent editorial audit, 11 November 2026. This document reads completed reports, captured attempt ledgers and static source/code audits. It runs no Agent, generator, patient analysis or new literature search. It supports the new manuscript rather than changing frozen experiments.

## The paper's central question

**Can a scientific Agent turn a biomedical research request and incomplete published evidence into a joint data-generating model whose virtual records support specified analyses, while making the construction's evidential and assumed dependencies inspectable?**

The deliverable is data, an executable generator and the record needed to inspect how they were constructed. Whole-cohort generation without target individual inputs is the demonstrated main setting. Enrichment and missing-cell completion remain applications of the broader design, not extra settings established by these new experiments.

Keep the current title, *From Published Evidence to Analyzable Biomedical Cohorts with Scientific Agents*, unless a later venue-specific revision requires otherwise. A short subtitle or contribution phrase can emphasize **traceable construction for scientific analysis**. Avoid a new title claiming general clinical reliability, the first literature-to-data system, or universal failure of Agent dependence modeling.

## Three contributions, with explicit evidence boundaries

| Contribution | Actual implemented work | Evidence now available | Claim to avoid |
|---|---|---|---|
| Request-to-data scientific construction | Agent selects studies where allowed, interprets measurements/adjustment, chooses joint structure and numerical assumptions, writes a sampler, inspects generated-only checks and selects a version | Latest request-only comparison: four independently closed sessions, four selected v001 laws, twelve final tables; complete API/tool records and numerical audit | Autonomous clinical truth, a new simulator-calibration principle, or universal workflow superiority |
| Analysis-specific empirical utility | Apply the same prespecified regression/dependence analyses to generated records and compare against existing clinical sample estimates | Repeated CHNS/ENSANUT constructions; five of six favorable relationship-evidence contrasts; current BP residual dependence numerically close; all unfavorable magnitudes and prospective outcomes retained | Direction alone proves usable inference; extra synthetic rows are new clinical evidence; matching one analysis validates all uses |
| Auditable scientific provenance | Connect source statistic and operator to adopted value, derivation/assumption, executable implementation, generated analysis and reference comparison | Thirty-construction retrospective audit; twenty delivered fixed-packet API laws; static source audit of all four current request-only laws | Provenance categories are confidence scores, Agent rationale reveals internal reasoning, or an audit trail itself establishes correctness |

This is a task/system/evaluation contribution with a biomedical use, not a claim that every component is algorithmically new. The relation to neighboring methods should be stated by input requirements, Agent responsibilities, scientific estimands and the delivered evidence chain; the word "Agent" alone does not establish novelty. The manuscript's primary literature review remains responsible for bibliographic priority claims; this audit does not supply a new exhaustive prior-work search.

## What the Agent actually does

| Stage | Agent decision | Deterministic infrastructure / human role |
|---|---|---|
| Formulate the construction problem | Translate the requested variables and analyses into evidence needs; choose queries and papers | Researcher supplies population, schema, units, analyses and permitted information; gateway enforces common retrieval scope |
| Interpret evidence | Choose how a reported mean, slope, rank correlation or subgroup contrast can inform the model; state population/conditioning bridges | Audits check source text, units, versions, overlap and mathematical use; they do not fill desired target coefficients |
| Complete a joint law | Choose distributions, dependence, covariate composition, variance allocation and unreported relationships | No host-written biological sign or coefficient is inserted into these current author sessions |
| Produce data | Write the executable stochastic generator and its scientific specification | Isolated worker samples records under fixed seeds; the LLM does not directly emit every patient-like row in the current primary route |
| Inspect and choose | Ask for permitted generated-only checks; retrieve further evidence, revise, retain or stop | Controller records immutable versions, calls, cost and budgets; evaluators calculate all predeclared final analyses after closure |

The ordinary Agent has the same model and underlying tools and can choose careful scientific practices. The workflow supplies generic organization, not a curated answer packet. Both are valid implementations. The latest pair cannot identify which component caused an observed difference because their retrieved evidence and resulting laws differ.

## Complete role of the major experiments

| Experiment | Denominator and result | Role in the story | Boundary |
|---|---|---|---|
| [Main evidence contrast](../main_study_freeze_2026-11-03/RESULTS.md) | Two requests; twenty Agent constructions and four fixed statistical constructions; seventy-two final tables. E1 had smaller mean absolute discrepancy than E0 on five of six prespecified coefficients; CHNS BMI worsened | Published relational information can materially affect scientific analyses | Information changes, not architecture alone. One statistical specification per condition is not a general statistical-method optimum |
| [Open-retrieval core replication](../core_workflow_replication_2026-11-04/RESULTS.md) | Four laws, twelve final tables. All six requested glycemia point directions retained; ENSANUT BMI effects attenuated after glucose adjustment in every draw. Magnitudes and dispersion remain mixed | Useful scientific relationships can emerge in independently authored complete cohorts | Existing references; attenuation is an association pattern, not causal mediation |
| [Retrospective attribution](../parameter_attribution_2026-11-10/ATTRIBUTION_MASTER.md) | Thirty constructions; ninety requested-analysis records and six dispersion records. Numerical full-law implications were available for only seven requested analyses and six diagnostics | Inspect source-to-law-to-analysis dependencies, including unavailable derivations | This includes older experiments already listed, not thirty additional clinical studies; missing implications remain missing |
| [Two fixed-packet API rounds](../two_round_synthesis_2026-11-10/RESULTS_SUMMARY.md) | Twenty-eight initial attempts, twenty delivered initial laws; four dependent reviews. Five model configurations attempted across the first round; later roster unbalanced | Models choose different completions of absent joint evidence; all twenty delivered initial dependence means were below the two reference values | No live search; failed outputs have no scientific score; not a provider leaderboard or universal shrinkage law |
| [Request-only API rounds](../request_only_agent_capacity_2026-11-10/RESULTS.md) | Twelve constructor attempts over three versioned rounds, eight selected laws, twenty-four delivered/thirty-six scheduled final tables. Final round: four laws and twelve tables | Actual retrieval-to-data operation and policy comparison under equal within-round capabilities | Engineering changes and fresh authors across rounds prevent a paired causal repair estimate; only one final constructor per case/policy |
| Earlier iron, HAALSI, Turkana and HRS studies | Retain their separate frozen reports, including failed criteria and source-model reconstruction | Different estimands and boundaries of generalization | Different runtime versions and information conditions cannot be pooled as replications of the current API workflow |

The fixed-packet rounds cost an estimated $14.14412666 with $0.21840852 reserved for unknown usage. The three request-only rounds cost an estimated $2.95305. These are different experiment groups; the latter is not the project's all-time cost. API tariffs are not billing invoices or total research labor.

## Traceability and explainability: the useful claim

The current evidence supports **construction-level explainability**: a reviewer can inspect why the released program contains a scientific relationship, what source statistic motivated it, what transformation was used and which additional assumption supplies the missing information. A concise decision record is not access to private internal reasoning.

Use a five-object chain:

1. **Reported source statistic**, including study population, measurement, units, selection and adjustment.
2. **Adopted parameter**, with source anchors plus any derivation and assumptions. These labels can overlap.
3. **Full-model analysis**, derived only where valid after all nonlinearities, selection and transformations.
4. **Generated-data estimate**, computed from the released records with an explicit estimator.
5. **Clinical sample reference**, with its uncertainty and role as supplied, developmental or prospective evidence.

A code coefficient is not automatically the target regression coefficient. A marginal correlation is not a residual correlation. An algebraic conversion may be correct while the cross-population or adjustment bridge is unverified. Missing theoretical implications should not be estimated backwards from the observed reference.

Three concrete examples make this contribution visible:

| Construction | Traceable choice | Scientific consequence / interpretive limit |
|---|---|---|
| Current PNS ordinary | Uganda residual correlation 0.7307 is explicitly reported; the source uses a different covariate set, categorical BMI and treatment exclusions | Generated requested residual correlation 0.696 versus the existing reference 0.717. This numerical agreement does not validate the operator transfer |
| Current PNS workflow | Reported longitudinal Kendall tau is transformed through a Gaussian-copula assumption and an additional variance allocation | Requested residual correlation 0.727. Both the dependence family and conditioning bridge are visible assumptions rather than newly observed target facts |
| Current lipid workflow | Malawian per-SD BMI coefficients are converted using an assumed transported BMI SD of 4.8; HDL/non-HDL conditional independence is added | TC slope 7.656 versus 5.683 and residual correlation 0.323 versus 0.512. Inspectability explains the construction without making it the most accurate policy |

All source details and final values come from the [current source audit](../request_only_agent_capacity_2026-11-10/review/SCIENTIFIC_PROVENANCE_AUDIT.md) and [final result report](../request_only_agent_capacity_2026-11-10/RESULTS.md). These cases do not causally isolate a particular assumption's contribution. A controlled alternative-law analysis would be needed for that stronger assertion.

## Story order and figure roles

1. **Need and task.** Published pieces are insufficient to directly run a joint analysis. Introduce the actual research request and data deliverable.
2. **Agent construction.** Show the decisions and tool calls that create the joint law. Explain the emitted data and traceability record together.
3. **Useful analyses.** Start results with the core glycemia profiles and adjustment pattern. Show effect magnitudes, not only signs.
4. **Value of evidence.** Show all six E0/E1 contrasts and the delivered statistical comparator. This is the cleanest existing evidence intervention.
5. **Autonomous operation.** Show the latest ordinary/workflow result profiles, with previous incomplete deliveries separated from scientific quality.
6. **Explain what was inherited and assumed.** Use a concrete source-to-code-to-analysis diagram alongside the cross-model fixed-packet audit. Distinguish evidence insufficiency, scientific transfer and implementation failures.
7. **Scope.** Retain earlier iron/prospective failures and reconstruction endpoints. State which applications remain untested.

The current request-only blood-pressure results require revising a tempting headline: residual dependence was below reference in all twenty delivered initial fixed-packet constructions, but the new PNS constructions yielded 0.696 and 0.727 against 0.717. **The pattern is conditional on tasks, evidence and construction, not an immutable Agent bias.** This makes the scientific point stronger: the model's evidential and assumed dependencies matter, while retrieval alone does not resolve every mismatch.

## What can be written now, and what still needs evidence

| Statement | Status |
|---|---|
| The implemented Agent can autonomously retrieve, author, run and select a whole-cohort generator from the request | Supported in the latest bounded two-case pilot |
| The resulting records preserve several requested association patterns and selected magnitudes | Supported, analysis-specific; complete adverse profiles remain visible |
| Scientific inputs and choices can be traced through recorded artifacts | Supported within the completed audit scope |
| Providing the traceability record helps biomedical reviewers find errors faster | Not tested; feasible low-cost audit experiment in the extension plan |
| The workflow reliably outperforms ordinary Agent | Not supported; current results are mixed and have one constructor per cell |
| The method is robust across model configurations in the live retrieval setting | Not yet established; existing multi-model evidence is fixed-packet and unbalanced |
| The current live API runtime supports glycemia as well as BP and lipid requests | Not yet established by that runtime; earlier glycemia studies use different versions. One existing-case extension is proposed, subject to schema/operator readiness |
| Provenance predicts error on unseen targets | Not tested; a distinct prospective prediction claim, not necessary for this paper |
| Virtual records replace actual individual measurements or save demonstrated patient-collection cost | Not established |

The immediate paper revision needs accurate integration and explicit method-version accounting, not another architecture layer. After repeating the current two-request procedure, one existing glycemia request may strengthen scientific-task breadth more than a second model; a second model instead tests configuration dependence. The extension plan treats them as ordered alternatives, not an automatic full grid. Additional experiments should strengthen a chosen claim rather than increase the number of figures or the number of synthetic rows.
