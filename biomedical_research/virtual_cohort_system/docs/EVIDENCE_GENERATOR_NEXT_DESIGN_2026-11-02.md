# Evidence grounded biomedical generation and revision design

Status: design proposal for the next additive implementation. No new construction, calibration or target evaluation has run under this design. Existing frozen protocols and results remain unchanged. The execution budgets below become operative only in a separately reviewed release.

The product is reusable virtual biomedical data: a whole cohort when no participant observations exist, additional unmeasured variables when covariates exist, or completion of missing cells. A scientific Agent translates published evidence into a stochastic generation process. Statistical tools execute that process and calculate its consequences. Scientific utility is assessed through analyses of the resulting data, including analyses not supplied as fitting feedback.

The next implementation should establish that numerical evidence enters the generator through the correct source statistic, that the generator is mathematically suitable for the intended analyses, and that source improvements can support useful target analyses. More virtual rows alone do not establish any of these properties.

## Basis for the change

The completed [CHNS experiment](../reports/existing_data_benchmark_2026-11-02/RESULTS.md) included ten Agent-authored generators and thirty 3,000-row tables. Additional relationship evidence reduced the glucose-analysis discrepancy by 74.3%, while the BMI and age discrepancies increased. The fixed overall improvement condition failed. The [static audit](../reports/existing_data_benchmark_2026-11-02/CONSTRUCTION_EVIDENCE_AUDIT.md) found nineteen of twenty added-relationship uses qualitative only, and seven intended continuous laws with divergent biomarker moments.

That protocol permitted autonomous scientific choices but prohibited numerical source execution and scientific revision during construction. It tested one-shot use of additional information. Qualitative uptake did not violate its instructions. These observations identify design gaps; they do not prove that the restrictions caused every defect or target discrepancy.

## Division of responsibility

| Responsibility | Scientific Agent | Statistical tools and controller |
|---|---|---|
| Research task | Interpret intended population, variables and analyses; flag missing evidence | Validate the declared input regime and information boundary |
| Evidence | Select applicable evidence; explain conflicts and omissions | Check provenance bindings, units and declared statistic semantics |
| Model | Choose dependencies, transformations, distributions, parameters and transport assumptions | Execute the submitted law and enforce technical isolation |
| Scientific validity | Explain why the chosen composition supports the requested analyses | Apply supported mathematical checks and obtain independent review |
| Revision | Diagnose source discrepancies and revise, retain or stop | Return authenticated source results and enforce a fixed attempt budget |
| Evaluation | Receive source feedback only before target release | Freeze artifacts; evaluate all target analyses; preserve failures |

Use one scientific Agent by default. Independent review is a checking role, not a requirement for a multi-Agent generation architecture. The coordinator must not supply desired target slopes, signs, means or residual scales. Agent-authored code is a substantive generation method when its scientific decisions are traceable and consequential; writing code is not itself evidence of innovation.

## Main route and direct data route

The main route is an Agent-authored sampling program. The Agent writes the scientific specification and executable generator; a seeded runtime produces rows. This route supports repeatable sampling, inspectable equations and efficient large cohorts. Its scientific validity is not guaranteed by valid Python or finite output.

Direct table generation remains a supported alternative. The Agent may emit the numerical rows itself and revise them after allowed feedback. A finite table has finite empirical moments, but does not thereby define a valid population law, independent observations or a reliable regeneration procedure. Independent LLM-generated tables are needed to assess repeat-generation variation; applying several seed labels to one table does not create independent generations.

First complete the program route. A later small direct-table comparison should use a feasible common row budget, the same evidence and intended analyses, and report actual resource use. It should not expand the first pilot into a large route-by-model factorial. Historical direct-table experiments remain historical results, not new tests of this implementation.

## Evidence must have an executable role

Require an evidence-use record for every admitted item, extending the existing [analysis-evidence declaration](ANALYSIS_EVIDENCE.md). Each record includes the source population and selection, variable definitions and measurement, units and transformations, statistic and adjustment set, reported value and uncertainty information, cohort overlap, intended use, operator binding, affected parameters and unresolved assumptions.

Use four roles:

| Role | Interpretation |
|---|---|
| Numerical source constraint | An executable comparison with adequately specified source conditions and operator |
| Qualified numerical comparison | Executable only under declared missing-context, distributional or mapping assumptions |
| Qualitative context | Supports a modelling choice, but is not numerically fitted or validated |
| Unused or incompatible | Excluded with a reason; retained in the evidence ledger |

An algebraic derivation records its inputs and assumptions within either numerical role. A citation attached to a parameter is not sufficient to establish numerical uptake. An Agent may reject an inappropriate constraint rather than fit every published point. The omission must be visible.

The four current E1 relationships can support at most qualified numerical comparisons under the available packet. Source joint covariate distributions and parts of their analysis conditions remain unknown. If a required operator detail remains unknown, return unavailable instead of silently choosing it. Missing standard errors do not prevent a transparent point comparison; they prevent invented precision weights or confidence-based acceptance criteria. Published individual SDs are not standard errors, and intervals of unknown level must not be relabelled 95% intervals.

Examples of required distinctions:

- Jansen's BMI and fasting-glucose coefficients come from separate age/sex-adjusted projections. Compute two separate regressions in the source IFCC scale. Do not insert both estimates into a single joint structural equation.
- Bao Pearson and MIND Spearman are different functionals and have different source contexts. Neither is automatically a conditional residual correlation.
- A unit conversion may transform a level, SD or slope differently; an offset applies to levels but not slopes. Unit conversion does not establish assay equivalence.

## One model with explicit population contexts

Reuse the existing [whole-cohort context bridge](../reports/scaleup_2026-11-01/bridge/README.md). A common generator and specification expose a shared scientific core, source-population contexts, the target-population context and measurement mappings. Only the selected active context changes for execution.

The Agent declares which mechanisms and parameters are shared and which vary by population. Changes to source-fitting parameters must have a documented dependency path into the target generator if transport is claimed. Merely using the same code file is insufficient: independently adjustable source and target submodels can fit sources without informing the target at all. For this pilot, inspect the equations and executable code paths, including an analytical substitution of a declared shared parameter, without prescribing a target-effect sign. This is a static dependency check, not an additional simulation experiment or proof of useful transfer. Runtime perturbation experiments are outside the pilot budget.

Unknown source joint distributions remain explicit assumptions or bounded sensitivity scenarios. These scenarios do not constitute recovered patient data. Discrepancies calculated in an assumed source context must be labelled accordingly; target-context statistics must never masquerade as source reproduction.

Evidence from different populations need not agree exactly. Keep source-specific discrepancies and unresolved conflicts visible. The current evidence packet does not authorize treating heterogeneous reports as independent observations of one common effect or automatically pooling them into a precision-weighted loss.

## Scientific validity before numerical fitting

Add a law-and-analysis declaration to the candidate. It describes the distributional composition, variable dependencies, parameter restrictions and mathematical conditions needed by each intended analysis. Review the declaration against executable code.

For ordinary population OLS, a sufficient starting check includes finite relevant second moments and a nonsingular predictor moment matrix. Pearson additionally needs positive finite variances. Any uncertainty procedure requiring stronger conditions must be checked separately. The gate should report pass, fail or unresolved for a specified analysis, rather than issue an unrestricted quality certificate.

Catch the observed composition in which unbounded lognormal BMI enters a positive exponential link: finite simulated rows do not establish finite population moments. Audit the complete composition, including exponentiated gamma variables and mixtures. Log transformations, saturating responses or justified bounded support are options for the Agent, not mandatory manually selected biomedical relationships. Truncation requires a disclosed rationale before evaluation; it must not be silently fitted to known CHNS ranges.

Start with analytical checks for supported distribution/transform compositions plus independent review. Do not claim a universal proof checker for arbitrary Python. An unresolved required moment argument cannot obtain a pass. Stress sampling, tail summaries and duplicate checks supplement mathematical review; they do not replace it.

## Source feedback and revision loop

1. Declare the research purpose, population, permitted inputs, planned analyses and information boundary.
2. Agent submits the evidence roles, shared/context-specific model, generator, parameter provenance and scientific-validity argument.
3. Review semantics, context linkage and validity. Record all defects and corrections before any study branch is formed.
4. Execute the reviewed source-context recipe through the bridge and `semantic_feedback_v1`. Bind feedback to the actual code, specification, context, output and operator.
5. Return source-specific reported points, generated statistics, Monte Carlo variation, discrepancies, operator failures and assumptions. Keep source uncertainty, simulation variation and transport uncertainty separate.
6. Agent diagnoses the discrepancy and chooses revise, retain or stop. It may change structure or parameters within the declared budget, explain the evidence affected, and retain an unresolved conflict. A revision need not be forced when evidence cannot justify it.
7. Recheck any changed scientific law and run the prespecified source checks. Preserve initial and revised artifacts and every attempted run.
8. Freeze the entire release before target evaluation. Run every declared target analysis and independently recompute the aggregate results.

Source feedback can distinguish an implementation or unit error, a mistaken statistical operator, an assumed source context, insufficient model flexibility, or incompatible/insufficient evidence. It cannot by itself determine which transfer assumption holds in the target population.

Permit evidence-gap retrieval at the framework level when authorized by the task and budget. For the first controlled pilot, keep the existing E1 packet fixed to isolate the feedback mechanism. This is a pilot information boundary, not a permanent prohibition on literature search.

## Numerical fitting is an optional tool

The first implementation should connect executable source feedback to Agent revision. Do not make a new optimizer a prerequisite. The Agent can revise a justified parameter or give a checked algebraic derivation.

If repeated manual numerical search by the Agent becomes the bottleneck, add a narrow whole-cohort calibration adapter. Reuse the bounded-search and immutable-trial concepts in [calibration.py](../cohort_harness/calibration.py), whose current execution path is enrichment-specific, and execute whole cohorts through the existing bridge. The Agent must declare tunable parameters, admissible ranges, source comparisons and discrepancy scales before fitting. Numerical optimization must not invent a scientific graph or access target outcomes. Unknown precision cannot be replaced by artificial inverse-variance weights.

Calibration will require a separate frozen budget and reviewed loss or multiobjective rule. It is not included in the first pilot below. Source fitting and target transport must remain separately reported even if calibration succeeds.

## Small developmental pilot before scale-up

Use existing CHNS and the already reviewed E1 evidence. CHNS has been exposed to the research team; it is a developmental benchmark, not a fresh independent confirmation. Authors receive only the permitted packet and task in new contexts. Context restrictions do not prove absence of pretrained knowledge or OS-level isolation of the authoring model.

First perform one source-only integration construction with no target-result access: at most three source-context tables of 1,000 rows, one per context, and no target tables. Verify the adapters, static dependency paths and scientific gates. This is an engineering feasibility check, excluded from comparative scientific results. Fix interface errors before the study release, rather than changing procedures after seeing target performance. A failed integration gate returns to design review; it does not silently expand this execution allowance.

Proposed study budget, subject to release review:

- Two fresh scientific constructions, with the same E1 input and validity requirements.
- Each submits one initial law and may receive at most one common pre-branch validity correction. Keep rejected submissions and their reasons in the denominator; do not silently replace a failed author.
- From each admissible initial law, create two independent revision contexts: one self-review without numerical source feedback, and one with the authenticated numerical source feedback. Each gets one revision opportunity with the same call/output allowance and common validity requirements. This is an internal mechanism check for the value of feedback, not a requirement to claim superiority over ordinary Agents.
- The initial law and both final branch versions each use three prespecified target seeds: at most eighteen target tables of 3,000 rows. Unchanged retained versions are paired repeats, not additional independent scientific constructions.
- Three source contexts, three diagnostic seeds per context, initial plus both final versions: at most fifty-four 3,000-row source tables. The no-feedback branch does not see its numerical source results before freezing. Record simulation variation descriptively; three draws do not establish a calibrated Monte Carlo confidence interval.
- No optimizer, extra evidence retrieval, target-guided repair, additional constructors or post-result extension. Validity failures and infeasible source recipes produce recorded failures rather than replacement runs. Any infrastructure retry policy must be frozen in the release.

This is at most seventy-two study tables and 216,000 simulated rows, not that many independent observations of method performance. Two constructors permit a feasibility decision, not a reliable general method ranking. Pilot seeds, package versions, exact artifact schema, source-comparability assumptions, gate rules and analysis code must be reviewed and frozen before author dispatch.

Evaluate in a fixed order:

1. **Scientific validity:** Does the submitted law meet the requirements of each intended analysis? Report every failure and correction.
2. **Evidence uptake:** Which numerical source statistics were actually executed? Which parameters or structures changed? Did declared dependency paths operate? Keep exact, qualified and unavailable comparisons distinct.
3. **Source behaviour:** Report the complete source discrepancy vector and trade-offs before and after revision. Improvement in an assumed source context is conditional on its assumptions.
4. **Target analysis usefulness:** Use the existing BMI, glucose and age analyses plus the prespecified dispersion, dependence and tail diagnostics. Report directions, effect estimates and discrepancies with reference uncertainty. Do not select only the improved endpoint or demand that all target coefficients improve as the sole mechanism criterion.
5. **Analyses beyond feedback:** Mark explicitly which target analyses were not numerical fitting objectives. Reuse one frozen output for all of them; do not regenerate separately for each question.

Before release, specify any substantive tolerance used to label an analysis useful; never invent it after observing outputs. In the absence of a defensible tolerance, report continuous comparisons and avoid binary equivalence or adequacy claims. A reference interval membership count alone is not an equivalence test.

Continue development if evidence uptake and validity demonstrably work and the complete target profile shows a defensible use case. If source fit improves but target utility does not, report a transport limitation and examine the declared assumptions without tuning to the revealed target. If the mechanism adds no useful change, simplify it. No outcome in this pilot automatically triggers new data acquisition or a larger run.

## Implementation sequence

| Step | Reuse | Add or change in a new version | Completion evidence |
|---|---|---|---|
| 1 | `analysis_evidence.py` and current candidate submission | Mandatory evidence-use and law-validity declarations | Real candidate records can distinguish numerical use from contextual citations |
| 2 | `semantic_feedback_v1.py` and context bridge | Explicit shared-parameter/dependency review; qualified-context feedback labels | Correct native source operators; no source/target substitution |
| 3 | Existing author/reviewer/retain-revise-stop flow | Wire the declarations, gates and source feedback into a new controller | Immutable before/after artifacts and truthful retain/stop decisions |
| 4 | Existing isolated execution and aggregation | Targeted regression fixtures for semantic mismatch, disconnected contexts and invalid tail composition | Artificial cases detect the identified defects; no patient-validity claim |
| 5 | Existing CHNS analysis and independent recomputation | Separately reviewed pilot release and paired branch report | Complete results and failures for every frozen slot |

Existing passing semantic tests need not be rerun wholesale unless affected dependencies change. Tests should target newly added logic. Do not modify old frozen modules or receipts to make the new run appear to have used the improved gates.

## User-facing output and paper claim

Deliver the virtual table, generation program when applicable, source evidence ledger, assumptions, version/seed provenance, and an analysis-use report. The report distinguishes source-constrained, assumption-sensitive, evaluated and unassessed analyses. These labels describe evidence and evaluation scope; they are not clinical certification.

Multiple admissible generators represent sensitivity to assumptions unless a separately justified uncertainty model exists. Several Agents or seeds are not automatically posterior draws. More generated rows reduce simulation noise but do not add independent biomedical evidence, recover a participant's unmeasured assay or replace clinical data collection.

The intended contribution remains a method for converting fragmented published evidence into virtual biomedical data that can support reusable scientific analyses, including when no individual input data exist. The proposed checks make this claim testable. A feedback loop, code generation, extra Agents or component combination alone does not establish novelty. The next pilot tests a mechanism; broader empirical support and comparison to relevant evidence-conditioned generation methods remain necessary before claiming general usefulness or freezing the paper's core method.

## Design review

An independent read-only design review found the study arithmetic coherent and accepted the qualified-source, developmental-target, Agent-choice and matched-revision boundaries. It identified one ambiguity: a proposed parameter-intervention check could add unbudgeted simulations. The design now limits that check to equations/code paths and explicitly bounds the separate integration construction. This review is of the proposed design, not of an implemented controller or a new experimental result.
