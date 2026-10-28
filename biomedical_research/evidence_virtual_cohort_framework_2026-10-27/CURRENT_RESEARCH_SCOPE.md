# Current scope: evidence-guided virtual cohort generation and enrichment

27 October 2026. Design amendment following the user's clarification. This is a prospective scope correction, not a new experimental result or a retrospective change to any evaluation. It takes precedence over the task hierarchy, mandatory scenario mechanism, and expansion rules in the earlier method plan and strategy specification. Frozen Stage 1 artifacts and their reported results remain unchanged.

## 1. What the system is for

**Research question:** Can an Agent combine available observations with applicable published evidence to generate richer virtual datasets that support useful biomedical analyses, including analyses whose results were not supplied during construction?

The output may contain variables that the original dataset never measured. It need not duplicate a complete real table, and there may be no complete real table to compare against. The principal evaluation concerns scientific conclusions and relationships obtained by analysing the generated data. Cell-wise reconstruction error and exact matching of means, standard deviations, coefficients, or p-values are not universal success requirements.

Keep three intended use cases distinct, without reducing the project to any one of them:

| Use case | Available input | Output |
|---|---|---|
| Whole virtual cohort | Target definition and study evidence; participant data optional | New virtual participants with the requested variables |
| Variable enrichment | Observed records with a limited variable set plus external evidence | Preserve observed cells and add synthetic variables that were never measured in this cohort |
| Missing-cell completion | Partially measured variables and applicable evidence | Preserve observed cells and fill designated missing cells with synthetic values |

**Running example:** a cohort contains BMI, and perhaps age and sex if actually measured. The Agent obtains applicable evidence about insulin and its relationships with available variables, then generates virtual insulin values conditional on the available observations and documented population assumptions. If age or sex is absent, it must not silently treat invented values as observed. Multiple possible insulin values for the same observed BMI express conditional variation; one person's true insulin is not recovered by definition.

An enriched cohort is a reusable object for analysis. Its additional columns make more questions computationally accessible; that does not automatically make every resulting relationship empirically established.

## 2. What the Agent must actually do

1. Inspect the observed schema, target population, requested added variables, and intended analysis classes. Record which columns/cells are observed, derived, or to be generated.
2. Identify information needed for conditional generation: joint relationships, variation, population modifiers, measurement definitions, and unresolved conflicts. A list of marginal means is not a complete conditional model.
3. Retrieve and assess additional studies when needed. Keep source locations, populations, adjustment sets, units, measurement conditions, and cohort overlap. Source access is permitted; protected final evaluation material is excluded.
4. Choose and implement how to generate the added variables or whole cohort. Both direct record generation and Agent-authored executable generators remain eligible routes. Numerical sampling is an implementation tool, not a substitute for evidence-linked Agent decisions.
5. Review schema, observed-cell preservation, source applicability, conditional variability, and consequences of assumptions. Revise using allowed evidence and development diagnostics. Retain the initial and revised artifacts and the reason for each substantive change.
6. Freeze the candidate and outputs before the independent evaluator accesses the reserved reference. Report all scheduled outputs and failures, rather than selecting a generation after seeing its final scientific conclusion.

The fixed controller should implement interfaces, provenance, preservation checks, access boundaries, and reproducible analysis. It should not silently prescribe the scientific dependence structure or hand-adjust case-specific correlations to match an inspected result. Agent outputs must make the consequential modeling decisions auditable. Single-agent and multi-agent implementations are engineering choices; multiple scenarios are optional sensitivity analyses, not the required core contribution.

## 3. Evaluation follows the intended analysis

Use the same declared scientific question and compatible analysis definitions when a reference is available. Compare interpretation, relation structure, and practical implications. Distribution checks remain useful diagnostics but are not the headline claim.

| Evaluation setting | What can be assessed | What the result means |
|---|---|---|
| Relationship explicitly supplied in the input evidence | Whether analysis of the generated data reproduces that relationship in its applicable context | Evidence consistency and successful translation into analysable records |
| Relevant published result withheld from construction | Whether a compatible generated-data analysis agrees with the reserved result | Held-out analytical agreement, with population and source-overlap limitations disclosed |
| New locked cohort containing the relevant variables | Whether reserved analyses on the generated data support conclusions compatible with independent observations | Empirical validation for those analyses and that target population |
| Added variable with no joint target reference | External evidence compatibility, stability, and analyses enabled by enrichment | A usable evidence-conditioned research scenario; target relationships remain unvalidated |
| Rich cohort with an entire measured column hidden from the Agent | Whether enrichment restores useful reserved analyses when the column is revealed only to the evaluator | A method benchmark for variable enrichment; not a requirement that every deployment have complete truth |

A relationship can be reserved from the Agent while supported by external sources. Conversely, an analysis whose result is already determined by the supplied evidence is not an independent validation merely because a different script computes it. Analyses using only unchanged observed columns are preservation controls, not evidence of successful generation.

Source independence is recorded separately from prompt withholding. Different papers can reuse the same participants. Published results withheld from the prompt can also exist in a pretrained model's knowledge; procedural isolation does not prove absence of prior exposure. Newly locked participant data provide a stronger check where available, but they are not required for every additional variable in every intended use.

The analysis ledger records three separate fields: information supplied to construction, independence of the evaluation evidence, and applicability of the evaluation population. Agreement in an external population is not automatically validation in the intended target population.

## 4. What counts as a similar scientific conclusion

For each question, define the interpretation before inspecting final generated results. Report:

- Whether a direction or qualitative pattern is retained, reversed, unresolved, or not independently assessable.
- Where relevant, whether the relationship is monotonic, nonlinear, subgroup-dependent, or changed by the same adjustment set. Do not substitute a crude association for an adjusted result.
- Whether the implied magnitude changes the scientific interpretation. Exact coefficient matching is unnecessary. Use a practical category only when it has an independent substantive justification; otherwise show the estimate and uncertainty without inventing a pass threshold.
- Whether the conclusion is stable across scheduled Agent constructions and repeated generations, including disagreements and failures.
- Whether uncertainty or unsupported assumptions materially change the interpretation. Matching statistical significance is not the definition of success, and a wide reference interval is not evidence of no relationship.
- What new analysis becomes possible after enrichment and whether its interpretation has independent support or remains conditional on the generating assumptions.

An association built directly into the generator can be a useful input-consistency result, but it cannot alone establish that the method predicts unseen relationships. Generation should preserve realistic conditional variability rather than force every record to obey a deterministic positive or negative relationship.

Generated sample size is an output choice, not new empirical information. A small p-value obtained by generating more rows is not additional evidence. Keep within-generator sampling variation, uncertainty about model/evidence choices, and uncertainty from real measurements distinct. A synthetic-only regression confidence interval does not automatically include all three.

## 5. A bounded next experiment, without redefining the whole project

Start with one variable-enrichment case, while keeping whole-cohort synthesis and missing-cell completion in the paper's scope:

1. Audit a public obesity/metabolic dataset and its primary study before selecting it. It must measure BMI and an eligible additional variable, such as insulin, with adequate population, unit, measurement, and analysis metadata. No new eligible dataset has been established by this amendment.
2. Create an Agent-facing view with the entire added variable removed, including derived columns that would reveal it. The evaluator retains the complete reference separately. Exposed historical studies remain development cases; independent confirmation requires newly locked material.
3. Permit external evidence retrieval and Agent choice of generation route. Record source reuse and any target-derived summaries. Define the allowed literature and development feedback before the final test.
4. Have the Agent generate the enriched virtual datasets and produce executable analyses. Freeze outputs before opening the reserved results.
5. Run the same reserved analysis specifications on enriched and complete reference data. Make conclusion/relationship agreement the main report, with distribution and numerical discrepancies as explanatory diagnostics when relevant.
6. Retain an initial-to-revised comparison to inspect whether the workflow changed anything useful. Select a small appropriate comparator after the available information is audited; do not preselect an arbitrary model family, or claim superiority from an uncontrolled demonstration.
7. Separately demonstrate a deployment where the added column truly was never observed. Report analyses enabled, applicable evidence, and unresolved questions. Do not transfer the benchmark's validation to every unmeasured relationship in that deployment.

For variable enrichment, an eventual comparator must also have access to the relevant external information. A conditional statistical generator or donor model can be appropriate when its necessary evidence exists. Ordinary target-only imputation cannot learn an insulin model from a target table in which insulin was never measured; using that as the sole opponent would misrepresent the task.

The decision to expand should depend on whether the system generates usable richer data, preserves supported conclusions, and shows useful agreement on genuinely reserved analyses across repeated constructions. If only supplied relationships succeed, record that narrower utility and investigate the evidence or model limitation. Do not call it either universal success or failure of the complete idea.

## 6. How this changes the interpretation of completed work

- The earlier completion pilot preserved two selected conclusions. This is relevant feasibility evidence, but neither unique benefit nor broad transport validity has been established.
- Frozen Stage 1 restricted builders to marginal summary packets and tested a specific dependence-scenario policy. It did not implement the full autonomous evidence-acquisition and never-measured-variable enrichment task.
- Its negative or mixed comparison remains valid for that tested policy. It does not show that enrichment, direct generation, or evidence acquisition cannot work.
- Keep the audited analysis functions, source checks, output interfaces, and failure records. Do not reuse the old scenario requirement as the definition of the new method.
- No additional experiments have run as part of this scope amendment. No accuracy, discovery, recruitment-saving, or publication claim follows from updating the plan.

## 7. Relevant precedents and contribution boundary

[DALL-M](https://doi.org/10.1016/j.compbiomed.2025.110022) explicitly studies contextual clinical feature augmentation with LLMs. Therefore, adding synthetic features to existing clinical records is an established research idea, not a sufficient novelty claim by itself. Our prospective question concerns how cross-study evidence and revision support useful reserved biomedical analyses under documented population and measurement differences.

The [NCHS synthetic linked-data programme](https://www.cdc.gov/nchs/linked-data/synthetic/index.html) illustrates synthetic data used for association analyses with subsequent verification against original data. That precedent supports the practical analysis-and-verification use case; it does not establish the validity of our system when no joint target reference exists.

These references contextualize the design and were checked on 27 October 2026. They are not a systematic novelty review. A method-paper claim requires demonstrated performance of the implemented process, beyond naming the broader use case.
