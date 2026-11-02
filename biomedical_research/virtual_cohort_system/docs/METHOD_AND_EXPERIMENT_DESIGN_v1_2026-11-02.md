# Method and experiment design v1: evidence-guided virtual biomedical data

2 November 2026. Design consolidation requested by the user. This document defines the intended first-paper method and experimental hierarchy using the existing implementation and results. It is a prospective design reference, not a claim that the larger campaign has run or that all case contracts are executable. It does not change historical frozen experiments, their evidence, or their outcomes.

The [larger campaign](SCALED_EXPERIMENT_CAMPAIGN_2026-11-01.md) still governs scope, budgets and global release. This document resolves one prospective ambiguity: **the final frozen stage is the primary delivered-data evaluation; initial stages are evaluated secondarily for paired revision/retention analysis.** No target outcome was inspected to make this choice. Case-level scientific thresholds remain subject to the recorded pre-outcome release process.

## 1. The problem, product and paper

**Research question:** Can an Agent turn heterogeneous published biomedical evidence, a target-population description and optional observed measurements into joint virtual data that support several specified scientific analyses?

Published studies expose only parts of a joint distribution: marginal summaries, subgroup results, adjusted coefficients, correlations or prevalence. Their populations, measurements and analysis specifications can differ. Researchers may have no individual measurements at all, or may lack a variable or some measurements in an existing cohort. The method constructs a usable joint-data representation from this incomplete information and evaluates what that representation supports.

Working title: **From Published Evidence to Virtual Cohorts for Scientific Analysis**.

For the primary program-route campaign, the delivered object is a virtual dataset together with its executable generation recipe, source evidence and assumptions. The wider direct-table route records the construction and decisions without requiring a generator program. A generated person's value is a possible model-based value, not a recovered clinical measurement. More generated rows increase simulation resolution; they do not increase the number of measured participants or independently supported facts.

### Scope of the first paper

| Information regime | Available individual data | Output | Role in this paper |
|---|---|---|---|
| Complete-cohort generation | None | All requested variables generated jointly | Primary prospective experiment |
| Unmeasured-variable enrichment | Some observed columns | Preserve observed values; add virtual columns | Existing supporting experiments, reported separately |
| Missing-cell completion | Partially observed table | Preserve measured cells; complete specified cells | Overall method capability; report only actually validated uses |

The primary use is **exploratory descriptive scientific analysis**, including adjusted associations and joint relationships. Current evidence does not establish clinical substitution, individual diagnosis, causal intervention effects, confirmatory inference or actual reductions in recruitment cost. Those stronger claims are not necessary to state the data-generation problem clearly.

## 2. Contributions and research questions

| Contribution being developed | Required evidence | Current standing |
|---|---|---|
| A biomedical evidence-to-data method for unavailable joint measurements | A substantive Agent construction, actual generated data, and traceable evidence/assumptions | Demonstrated in bounded historical cases; not a claim of first aggregate-only generation |
| Study-conditioned interpretation when constructing a joint generator | Show how population, measurement, statistical definition and uncertainty affect construction and feedback | Several supporting operations implemented; general whole-cohort source/target linkage remains pending |
| Reusable scientific analyses from the same virtual release | Apply several fixed analyses to the same data and compare against a separately reserved measured reference | Selected directional feasibility demonstrated; quantitative usefulness remains the main prospective question |

**RQ1, primary:** At the final stage, do the generated data support the three prespecified scientific analyses at the declared resolution in each admitted measured setting?

**RQ2, primary reuse question:** Does the same release support the reuse item within the three primary analyses: a joint or conditional use beyond the statistics directly fitted, without generating a different dataset for each endpoint? This is not a fourth primary endpoint. Classify whether each use is directly reported in sources, algebraically implied, or dependent on unverified assumptions. Target holdout is a separate property.

**RQ3, secondary:** How do results vary across independent scientific constructions, simulation seeds and biomedical settings? Does one source-feedback opportunity improve, leave unchanged or worsen the held-out analyses?

The generic Agent generate/check/revise loop, a new interface, more Agent roles and larger virtual row counts are not separate novelty claims. A new loss, model training or superiority to a direct-analysis Agent is not required. A claim that a particular translation mechanism improves validity would require an additional information-matched component comparison; the present campaign does not automatically prove that claim. The [completed positioning analysis](../manuscript/POSITIONING_GSIM_LLMSYNTHOR_2026-11-01.md) documents substantial overlap with prior methods.

## 3. Method: what the Agent actually does

The default scientific implementation uses **one Agent per independent construction, deterministic statistical tools and a controller**. Independent reviewers check evidence and implementation; their existence is not a multi-Agent performance claim.

| Step | Inputs and action | Deliverable / decision |
|---|---|---|
| 1. Specify the request | Population, eligibility, requested variables, measurement definitions, units, allowed observations, broad intended analyses and output size | A versioned task contract; no hidden target estimates |
| 2. Assemble evidence | Retrieve and inspect applicable original studies; preserve source context, conflicts, uncertainty and overlapping cohorts | A versioned evidence packet with original locators and applicability notes |
| 3. Construct the scientific model | Agent selects joint structure, distributions, conditional relationships, residual dependence, parameter values and transport assumptions | Model specification, parameter provenance and a short decision record |
| 4. Freeze and generate | Freeze the actual candidate before executing its program with prespecified seeds | Generated joint tables, execution records and validity diagnostics |
| 5. Diagnose using sources | Compute only supported statistical checks in explicitly declared contexts; keep unavailable and approximation-based diagnostics distinct | A source-feedback report bound to the actual output |
| 6. Make one feedback decision | Agent revises, retains or stops based on permitted source information | An immutable revised candidate or explicit retention record |
| 7. Release and evaluate | Close the scientific constructions before revealing measured target outcomes; apply the fixed analysis functions to every scheduled output | Analysis-specific results, discrepancies, uncertainty limits and a complete failure ledger |

### Evidence representation

Each numerical claim is documented jointly across the evidence record, source-semantic recipe and model specification: study/cohort identity and overlap; source population and selection; variable and measurement definition; units and transformations; statistic/operator; adjustment variables; value; uncertainty type and bounds where reported; table/page locator; applicability; and unresolved assumptions. These fields are not all stored inside one evidence item in the existing implementation. Unavailable definitions and uncertainty remain explicitly unknown.

The model distinguishes **reported**, **derived**, and **assumed** quantities. An adjusted regression coefficient is not automatically a structural parameter. A confidence interval is not participant-level SD. A missing relationship is not automatically zero or conditional independence. Incomplete evidence is expected; the Agent may fill gaps with named assumptions instead of requiring every joint relationship to have been published.

### Scientific decisions versus computation

The Agent owns the model's scientific content: which relationships to use, how to reconcile compatible findings, how to represent disagreement, which remaining dependencies to assume, and which changes a diagnostic justifies. It must make these decisions explicitly rather than merely narrating a coordinator-written generator.

The statistical runtime draws samples from that Agent-authored model and computes declared statistics. The controller checks contracts, freezes versions, controls execution and separates allowed inputs from reserved evaluation. It does not prescribe the desired target sign, mean, slope or variance. A program sampling the rows is therefore an Agent-authored data-generation route, not evidence that the Agent had no scientific role.

Direct Agent-authored tables remain a valid route in the wider method and have historical pilot evidence. The new primary campaign uses the program route for reproducible sampling and source-context evaluation. It does not add a second full direct-table factorial or claim the program route is superior without a comparison.

## 4. Sources and target are different contexts

Let E be the admitted study evidence, C* the target-population request, and O the optional observations. An Agent constructs a model G_theta conditional on context C and any allowed observations. A target release is D* = G_theta(C*, O; seed).

For source study j, an intended check compares its reported statistic s_j with T_j applied to a simulated source-context table after the declared measurement/selection mapping M_j:

`source diagnostic j = T_j(M_j(G_theta(C_j; seed))) compared with s_j`.

This expression defines the comparison being attempted. It is not a new estimator, a new loss function or a guarantee that C_j can be reconstructed. Evidence may constrain the model directly even when the source check cannot be computed.

The source/target contract must state:

1. Which scientific structure and parameters are shared across contexts.
2. Which population composition or measurement parameters may change, why, and how they are supported.
3. The actual transformation when units differ; relabelling a column is insufficient.
4. The source population approximation and any unavailable sampling weights, selection variables or assays.
5. How the source and target execution records bind to that common model.

Fitting unrelated per-study models and calling the files one generator does not demonstrate transferable construction. Conversely, shared structure does not require identical marginal distributions or identical regression projections in every population.

Feedback has three clearly separate states:

| Feedback state | Meaning |
|---|---|
| Supported declared statistical calculation | The available execution and operator permit the stated calculation; still does not by itself authenticate extraction or transport |
| Assumption-defined comparison | A declared approximation, such as an equal-weight scenario when source weights are unknown; useful for reasoning, not exact source reproduction |
| Unavailable | Insufficient context or unsupported semantics; no invented numerical discrepancy |

The existing `semantic_feedback_v1` checks declared meaning and supported arithmetic. It does not reconstruct every source population. The K02 supplemental collector binds additional diagnostics to verified outputs, but its cross-context scientific linkage is explicitly not supplied or verified. Completing this narrow linkage and unit path is remaining method work, not an already demonstrated capability.

## 5. Evidence retrieval and information boundary

Literature retrieval is allowed and scientifically useful. Relevant published relationships are valid inputs; the experiment need not hide every paper mentioning the same variables. However, a target-derived paper cannot simultaneously serve as independent external evidence and hidden validation for that target. Retrieval remains subject to the supplied task tools and remaining intake/query/download budgets; identifying a gap does not itself expand those permissions or budgets.

For the primary campaign, the shared source packet is established before scientific construction and supplied identically to all five Agent constructors and the statistical reference. An Agent can identify an evidence gap, but any scientific packet addition must go through the common pre-outcome version process. It cannot privately acquire extra evidence and then be credited with an information-matched advantage. A changed packet invalidates the assumption that prior constructions used the same input; do not silently add extra attempts to repair this.

Builders receive the population request, permitted evidence, interface and declared use classes. They do not receive private target tables, clinical target moments, target effect estimates, expected answer signs, results from other candidates, or result-bearing project summaries. Broad analysis questions may be known; the target estimates and specified numerical held-out checks are not feedback. The coordinator chooses scientific uses without inspecting their target effects.

Fresh contexts and restricted task packets are procedural separation, not a claim of an Agent-wide filesystem sandbox or absence of pretraining exposure. Disclose incidental study knowledge and distinguish cohort overlap, result exposure and ordinary background knowledge.

## 6. Experimental hierarchy and data roles

| Experiment block | Purpose | Data and scope | What it cannot establish |
|---|---|---|---|
| A. Existing whole-cohort results | Show actual evidence-to-data construction and analytical reuse, including failures | NHANES M17-B, ENSANUT and CHNS; 6 constructions, 18 unique target tables, 31,920 virtual rows, 90 existing estimates across 15 case-specific quantities | These different historical implementations are not three prospective validations of one unchanged new procedure |
| B. New primary campaign | Assess quantitative analytical usefulness under one declared procedure across admitted settings | Up to 4 target cohorts; actual cases selected on access, measurements and evidence before target effects | Planned slots are not acquired cases, completed experiments or guaranteed independent confirmations |
| C. Existing supporting cases | Show optional conditioning, direct-table generation, evidence translation and known failure modes | Enrichment, direct-row, transfer and artificial-mechanism studies already completed | These are separate information regimes; artificial results are not patient validation |
| D. Supporting diagnostics | Explain usefulness/failure and the effect of feedback | Source fits, relevant distributions, initial/final comparisons, construction/seed variation, actual costs | Diagnostics alone do not validate scientific use or demonstrate component superiority |

Do not rerun revealed historical targets or tune to their known effects. All completed primary outcomes and material failures remain in the Results, not only the favorable relationships. The [existing evidence atlas](../reports/existing_evidence_atlas_2026-11-02/README.md) and [data-use matrix](../reports/existing_evidence_atlas_2026-11-02/DATA_USE_MATRIX.md) supply this material now.

### New case slots

| Slot | Scientific domain | Intended analytical uses | Current status |
|---|---|---|---|
| K01 | Adiposity and glycemia | Two quantitative conditional relationships plus one additional joint/conditional use | No released case |
| K02 | Measured lipids | Adjusted HDL-BMI, adjusted total-cholesterol-BMI, and residual lipid dependence | Turkana is a qualified candidate, not admitted or released |
| K03 | Directly measured renal biomarkers | Two conditional relationships plus reuse beyond a derived formula | No released case |
| K04 | Inflammatory or hematological indicators | Conditional relationships and a justified distribution-sensitive use | No released case |

The intended ceiling is four independently admitted cohorts from at least three study families. Eligibility depends on access and scientific suitability; there is no promise of four positive or even four admissible cases. Current screening has used 3 of 6 family slots and 3 of 12 original-study reviews; zero cases are released. Do not increase this intake to fill a favorable figure.

K02 has disclosed prior target-study context, including generic dependence knowledge. Its three exact quantitative projections are not recorded as seen, but it is not a globally unseen study. Its formal independent-validation count remains unresolved; qualification is not permission to count it automatically among four independent confirmations. The campaign's stricter counting rule controls the final report.

## 7. Arms, repetition and fixed budget

**Evidence-guided Agent:** five fresh scientific construction contexts per admitted case, receiving the same packet and task. Each may choose a different model or reasonably converge to a similar model. Do not force cosmetic structural differences or count five contexts as five model brands.

**Statistical reference:** one transparent conventional construction using the same evidence and population description. Choose its compatible distribution family, fitting rule and treatment of unreported dependencies before target disclosure. A transformed conditional model or copula is an option, not a mandatory model for incompatible data. Document constraints it cannot use. It receives the same source diagnostic information and one predeclared calibration/retention opportunity.

The scientific comparator is therefore another data-generation construction under the available information. A direct-analysis Agent is not a mandatory opponent. Target-row-trained generators cannot be passed off as same-information alternatives; they would be an explicitly different information regime, not part of this campaign by default.

| Quantity | Per admitted case | Four-case upper bound |
|---|---:|---:|
| Agent constructions | 5 | 20 |
| Statistical-reference constructions | 1 | 4 |
| Candidate stages | Initial and final after at most one feedback decision | Up to 48 stage records |
| Sampling seeds per stage | 3 | Simulation draws, not clinical replications |
| Target table slots | 6 x 2 x 3 = 36 | 144 |
| Rows per new table | 5,000 | Up to 720,000 virtual rows |
| Primary analyses per table | 3 | Up to 432 slot-level evaluations |

A retained final stage aliases the initial outputs; it does not produce three new samples. If all stages retain, at most 72 unique tables are sampled. Actual failures, duplicate files and unexecuted stages reduce output counts. Source-context trials are not hidden inside the 144 target slots: their finite contexts, row sizes, seeds and calibration runs must be separately frozen before execution. No unmetered optimizer search is implied.

The five-Agent/one-statistical-specification design tests construction variability and provides a practical reference. It is not equal-search-budget superiority testing. Report every constructor and the fixed comparator; never select the best Agent and call that a fair algorithmic win.

## 8. Primary evaluation: analyses first, diagnostics in support

For each frozen target table, apply the same prespecified estimators used on the measured reference. A scientific effect is compared as an effect, not only as a generated-variable mean or histogram.

| Level | Report | Interpretation |
|---|---|---|
| Primary scientific use | Effect direction, raw effect/contrast, difference from measured reference, analysis-appropriate normalized discrepancy, reference uncertainty where supported | Whether the declared scientific analysis is useful at the prespecified resolution |
| Joint reuse | A residual, conditional, subgroup or other prespecified use not directly fitted as that numerical statistic | Whether one joint table carries useful information beyond marginal/source matching |
| Necessary distribution diagnostics | Dispersion, relevant quantiles/tails, impossible values, missing/invalid rows and subgroup coverage | Explain compressed variation, unreliable effects or measurement defects; not a replacement main endpoint |
| Construction and sampling variation | All five construction results and all three seeds; initial and final shown separately | Stability conditional on the observed constructions and sampling design |
| Source diagnostics | Supported, approximate and unavailable checks separately | Whether the model respects inputs under the specified interpretation; not target validation |

No universal weighted quality score is required. A positive direction, significant p-value, overlapping confidence interval or small marginal mean error alone does not establish quantitative usefulness. Where no defensible tolerance exists, report discrepancies without claiming equivalence.

Real-reference estimates are sample estimates, not known population truth. Their uncertainty is distinct from source-estimate uncertainty, participant variability, model/transport uncertainty, Agent construction variation and Monte Carlo seed variation. The current method does not deliver calibrated uncertainty for all these components. Do not use tiny standard errors from large virtual tables as additional clinical evidence.

### Stage and failure rules clarified here

- **Primary stage: final frozen delivery.** A valid retained final candidate uses its initial artifact identities and has zero revision gain. A changed final candidate uses its own frozen outputs.
- Both stages are evaluated only after scientific construction closes. Initial/final differences are paired descriptive feedback results; disclose unchanged and degraded outcomes. Better source fit is not automatically better target use.
- An invalid changed final output is a failed final attempt. Do not substitute the better initial stage, choose another seed or drop it from the denominator. Retention must be declared before target disclosure.
- Computational failures, scientifically mismatched results and unavailable endpoints are distinct entries. Implementation repairs follow the frozen rule and cannot use newly revealed scientific answers.

## 9. K02: a concrete instance of the design

**Task:** generate age, categorical sex, BMI, measured total cholesterol and HDL jointly with no individual covariates from the target. Target lipid analysis uses mg/dL.

**Empirical reference definition:** the named released Turkana file; investigator-selected age at least 18; documented F/M coding and missingness; common finite complete subset for the five variables; positive BMI/TC/HDL. No outcome-driven trimming or additional inferred health exclusions. The previously reported 397 is nonmissing availability, not final eligible N.

| Primary analysis | Estimand | Why it is included |
|---|---|---|
| HDL ~ age + sex + BMI | HDL difference per 5 kg/m2 BMI | A quantitative adjusted association |
| TC ~ age + sex + BMI | TC difference per 5 kg/m2 BMI | A second outcome using the same generated population |
| Correlation of residuals from both models | Pearson residual correlation | Joint reuse beyond the two adjusted BMI contrasts |

No desired sign or target coefficient is supplied. These are descriptive associations, not causal estimates.

The existing [K02 proposal](../reports/scaleup_2026-11-01/K02_PROSPECTIVE_DECISIONS_2026-11-02.md) uses an author-chosen **0.10 working resolution**: absolute BMI-effect discrepancy divided by reference outcome SD, and absolute residual-correlation discrepancy. The complete fixed sensitivity grid is 0.05/0.10/0.20/0.30. Reference SD is evaluation-only, never a generator input.

Under that proposal, a final constructor passes only when all three analyses meet the working margin on all three prespecified seeds; an Agent case-level result requires at least four of all five constructors, including failed attempts in the denominator. The single fixed statistical reference uses the same three-analysis/three-seed constructor bundle; the four-of-five rule applies only to the Agent constructions. If every zero-association anchor already lies within the margin, the case is not sufficiently discriminating to independently advance the next wave. The primary-stage clarification above applies prospectively.

These are exploratory operational criteria, not clinical equivalence bounds, a 10% relative-error promise or a universal criterion for all cases. They remain pending final case release. Report all raw effects, discrepancies and grid results, without choosing a better threshold afterwards.

The K02 three-analysis arithmetic and supplemental collector have been implemented and independently checked within their documented test scope. Source/target linkage, mmol/L-to-mg/dL representation, statistical reference, real-reference preparation, diagnostic/evaluation wiring and final uncertainty/budget choices remain incomplete. HC3 regression intervals can be reference sensitivity summaries; residual-correlation population uncertainty remains unavailable. No target effect was fitted in the implementation checkpoint.

## 10. Execution order and stopping decisions

1. **Complete admissibility and method release.** Resolve actual cases and exposure classes, evidence/task packets, source/target model contract, unit transformations, per-case statistical reference, analysis rules and finite source budgets. Independently review the implemented path. Do not require complete joint identification; require assumptions to be explicit.
2. **Global pre-outcome freeze.** Freeze admitted case identities and all primary/secondary questions, the common procedure, interpretation criteria and resources before the first target result is revealed. Record screening shortfalls rather than silently changing case families or outcome slots.
3. **Wave A.** Construct the released K01/K02 cases under their contracts; close both cases' scientific outputs before either measured target is disclosed. If a slot is not admissible, preserve the shortfall and resolve its effect on the design prospectively; do not silently replace or renumber it after results.
4. **Evaluate once and independently recompute.** Evaluate every available planned output, including failures and retained candidates. The final stage drives the prospective gate; initial/final and comparator results are also reported.
5. **Continuation decision.** If neither Wave A case meets its frozen quantitative-use bundle, or a material implementation/information-boundary defect invalidates the comparison, pause for a method/claim decision. Do not use source fit, an attractive subgroup or a case that fails its prespecified discrimination rule to bypass the gate.
6. **Wave B if allowed.** Use the unchanged pre-admitted K03/K04 contracts and procedure. Builders do not receive earlier target results. A changed method requires a new version and cannot retroactively claim confirmation from exposed targets.
7. **Close and write.** Report every admitted case, all primary uses, evidence/assumption status, failures, costs and the justified scope. A null or negative result can close a work unit; further components are not added merely to obtain a positive conclusion.

No new execution, evidence intake, scheduling, training, HPC or paid API is started by this document. Existing download ceilings, public-access restrictions and the 14 November new-work cutoff remain in force. The existing CHNS schedule remains paused.

## 11. Manuscript structure and core freeze checklist

The paper's narrative is: **unavailable biomedical measurements and fragmented evidence -> explicit scientific construction -> a reusable joint virtual dataset -> measured-reference evidence about its analytical uses and limits**.

| Main display | Question answered | Material |
|---|---|---|
| Method figure and one worked evidence/model table | What does the Agent infer, and what is generated? | Input regimes; source conditions; shared/context-specific choices; one concrete trace |
| Main scientific-use figure | What analyses does the data support? | All prespecified effects and reference uncertainty, grouped by cohort and method version |
| Joint-use and diagnostic figure | Where do conclusions or variability fail? | Reuse endpoint plus relevant dispersion/tail diagnostics; no favorable-only endpoint selection |
| Stability/comparison figure | How repeatable is the construction, and what did feedback change? | All constructors, seeds, statistical reference and initial/final results; zero gains shown as zero |
| Supplement | Can the workflow and conclusions be inspected? | Existing optional-input cases, complete outcomes, exposure/overlap, assumptions and reproduction instructions |

Methods and the historical Results can be drafted now. Freezing the prospective core method requires the following concrete completion items; a publication venue is not determined by checking boxes or by the number of virtual rows.

- [ ] Exact executable method version, one declared output route for the primary campaign and an actual end-to-end checked path.
- [ ] Shared source/target model contract, explicit unit transformations, supported/approximate/unavailable check behavior and source-run cap.
- [ ] Final target identities and independence/exposure labels; no promise based only on planned slots.
- [ ] Common evidence packet, substantive Agent responsibilities and a same-information statistical construction for each case.
- [ ] Primary final-stage estimands, eligibility, reference-uncertainty scope, discrepancy scales, interpretation rules and failure handling.
- [ ] Frozen counts, seeds, rows, stages, feedback access and target-release sequence; no best-stage or best-constructor selection.
- [ ] Independent review of the case-specific implementation before real target analysis.

Final claims about the new campaign's quantitative usefulness require complete planned target evaluation, independent recomputation, all primary outcomes and an honest interpretation. A bounded methods-and-feasibility paper can still be completed from the existing historical evidence if prospective admission or execution cannot be completed; its scope must be explicit. Selected directions with large magnitude failures support a narrower feasibility claim. A main quantitative failure belongs in Results and changes the claim; an optional unvalidated mode can remain a limitation.

## 12. Current status and next bounded work

**Settled here:** central problem and data product; primary no-individual-input regime; Agent/program division; study-conditioned construction and assumption handling; primary versus supporting experiments; planned arms/scale; scientific-analysis-first evaluation; final-stage primary interpretation; publication claim boundaries.

**Already available:** historical real-case results; evidence/model contracts and candidate freezing/execution; supported semantic diagnostics; K02 in-memory analyses and supplemental feedback component; independent component reviews.

**Not yet complete:** campaign case release; general source/target binding and unit path; K02 statistical reference and raw/evaluation adapters; remaining case-specific evidence and quantitative-use rules; live common-procedure campaign. Current new-phase counts remain zero admitted cases, zero constructions and zero generated tables.

The next implementation unit should therefore connect the existing generator lifecycle to one declared source/target context contract, with explicit unit handling and a finite source-run budget, and verify that path on invented fixtures. Then finish the already authorized case admission/global freeze. This serves the central data-generation experiment; it is not a mandate to build a broader Agent platform.

## Local evidence used to consolidate this design

- [Current focus and claim boundaries](CURRENT_RESEARCH_FOCUS.md)
- [Larger campaign and immutable historical budget](SCALED_EXPERIMENT_CAMPAIGN_2026-11-01.md)
- [Experimental sufficiency assessment](EXPERIMENT_SUFFICIENCY_2026-11-01.md), with its earlier single-case recommendation superseded by the larger campaign
- [Existing evidence atlas](../reports/existing_evidence_atlas_2026-11-02/README.md) and [data-use matrix](../reports/existing_evidence_atlas_2026-11-02/DATA_USE_MATRIX.md)
- [K02 prospective criteria](../reports/scaleup_2026-11-01/K02_PROSPECTIVE_DECISIONS_2026-11-02.md), [coordinator definition](../reports/scaleup_2026-11-01/K02_COORDINATOR_DECISION_2026-11-02.md), and [implementation checkpoint](../reports/scaleup_2026-11-01/K02_IMPLEMENTATION_CHECKPOINT_2026-11-02.md)
- [Agent loop](SCIENTIFIC_AGENT_LOOP.md), [statistical semantics](SEMANTIC_FEEDBACK_V1.md), and [analysis-evidence declarations](ANALYSIS_EVIDENCE.md)
- [Prior-work positioning and its primary-paper locators](../manuscript/POSITIONING_GSIM_LLMSYNTHOR_2026-11-01.md)

This consolidation inspected original project documentation, reviewed component boundaries and existing aggregate records only. It did not open patient tables, compute target effects, run scientific generators, download evidence or consume new original-study/family slots.
