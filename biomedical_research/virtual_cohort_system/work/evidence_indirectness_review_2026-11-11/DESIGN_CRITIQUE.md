# Evidence indirectness: independent design critique

11 November 2026. Design assessment only. No model calls, new datasets, new generators or clinical evaluations were initiated. This document does not authorize the proposed 384-constructor experiment or a gate implementation.

## Judgment

This is a useful hypothesis to investigate within the existing paper: **when a scientific Agent turns published statistics into a joint data-generating model, does it preserve what each statistic actually identifies?** A cited number can be accurately extracted yet assigned to a different population, measurement, conditioning set, scale or stochastic component. That question is more specific, actionable and testable than a generic warning about poor source applicability.

Do not yet replace the paper's central contribution with a universal failure claim. The existing records establish candidate mechanisms and several inspectable examples, not a prevalence estimate or a causal explanation for every clinical discrepancy. Preserve the application contribution: request-driven construction of analyzable virtual biomedical data with inspectable evidence and assumptions. Add numerical evidence-use semantics as a focused experimental question if the pilot supports it.

The root's new primary-paper reading reports that MisleadQA (arXiv:2610.24851v1) and TruthTrap (EACL Findings 2026) already cover true but misleading/out-of-scope evidence; MisleadQA also separates recognition from answering and reports recognition without resistance. Those papers were not independently reread for this design memo. Their reported overlap rules out claiming the first true-but-inapplicable evidence benchmark or the first recognition-action gap. The defensible narrower setting is **a scientific statistic becoming a numerical commitment in a stochastic joint model, whose generated data are reused across multiple analyses**. Merely moving a known failure to biomedical examples would not establish a new method contribution.

## What the current record actually supports

The completed [request-only repeatability study](../request_only_repeatability_2026-11-11/RESULTS.md) and [preclinical code/source audit](../scientific_check_revision_2026-11-11/review/CODE_SOURCE_CHANGE_AUDIT.md) contain relevant, different kinds of examples:

| Existing example | Supported concern | What is not established |
|---|---|---|
| R08 uses a longitudinal log random-intercept relationship while the requested analysis is cross-sectional OLS residual dependence | A stochastic-component and analysis-operator bridge is needed | That every use of the number is erroneous, or that this choice alone caused the target discrepancy |
| R07 uses SBP, DBP and pulse-pressure variances to derive covariance and subtract a modeled covariate budget | A correct identity can be followed by assumption-dependent conditioning and transport | That the covariance identity itself is wrong, or that a mismatch ban would improve data |
| R09/R11 use external correlation matrices and partial-correlation algebra | Algebraic validity and population/measurement applicability are separate | That a source partial correlation is universally nontransferable |
| Standardized lipid coefficients are converted using inferred or synthetic BMI SD | A scale bridge may depend on unidentified source moments | That an assumed scale is unacceptable if it is disclosed and analyzed as a scenario |
| Scientific-check review repaired R04's divergent tail and R07's rounding acceptance | Implementation defects exist independently of evidence indirectness | That all remaining error can be attributed to missing evidence |

The [complete revision result](../scientific_check_revision_2026-11-11/RESULTS.md) found no new identified residual-dependence constraint. Most outputs were unchanged, and the numerical changes were mixed. This supports separating mathematical validity, evidence identification and analytical transfer. It does not identify the effect of an applicability gate that has never been evaluated.

The retrospective audit must include all eligible source-to-parameter links in the frozen roster, not only discrepant endpoints or memorable quotations. Its denominator should distinguish source records, numerical commitments, constructors and requested analyses. Several commitments in one model are dependent observations. Target error must not determine whether a source is classified as indirect.

## Definitions needed before a new experiment

Treat applicability as a relation among **source statistic, declared use, target estimand and bridge assumptions**, not a single permanent label attached to a paper.

1. **Directly matched:** population and measurement scope are acceptable for the stated claim, and the reported estimand is the requested quantity.
2. **Exactly transformable:** units or statistical quantities can be converted using available information and a valid identity. Preserve propagated uncertainty and any required positive-definiteness constraints.
3. **Indirect but borrowable:** the quantity informs a prior, hyperparameter or explicit scenario under an identified exchangeability/transport assumption. This is not directly observed target evidence.
4. **Unidentified bridge:** the desired quantity requires unreported covariance, variance, measurement-error or effect-modification information. Several joint models remain compatible with the supplied evidence.
5. **Irrelevant or contradictory for the proposed direct use:** the number cannot play its claimed role. A new model or a different scientific claim may still make it useful.

The first pilot should target statistical-type and stochastic-component mismatches where the required bridge can be specified mathematically. Population differences are softer: they do not themselves establish different effects. Keep population transport as a separate later stress test, rather than confounding it with conditioning, units and measurement changes in one task.

### Acknowledgment followed by use is not sufficient evidence of failure

A scientific Agent can correctly recognize population mismatch and still use the source as a weak prior. It can choose an assumption-dependent point scenario because the user requested simulated data. It can transform an unadjusted quantity if the necessary joint moments are available. None of those behaviors is automatically wrong.

The potentially testable failure is **unjustified promotion of indirect information to a directly identified target constraint**. It requires evidence about all of the following: what the source reports; what bridge is needed; what the Agent says the number means; how the executable law uses it; and what uncertainty or sensitivity reaches the downstream analysis. A disclaimer in notes does not repair a contradictory `reported` label in the executable model. Conversely, a numerical effect on the output does not make a properly disclosed borrowing operation a semantic error.

Use two separate judgments: (a) source-role/claim validity before target reveal; (b) analytical behavior under a hidden controlled law. A fortuitously close scalar estimate cannot validate an invalid source-role claim. A transparent assumption can be inaccurate in one hidden world without becoming a false extraction claim.

## Problems with the proposed large experiment

| Proposed feature | Main problem | Required correction |
|---|---|---|
| Six tasks x four conditions x eight replicates x two models | 384 authors do not resolve ambiguous labels; six task templates remain six task templates | Test label adjudication and manipulability first; expand only after the mechanism is discriminated |
| No/applicable/inapplicable/both evidence | The four conditions estimate information effects, not workflow superiority | Hold the Agent/prompt/tools fixed for this probe; add a same-information policy comparison separately |
| Call all acknowledged-but-used evidence failures | Conflates reasonable borrowing with unjustified direct substitution | Inspect the declared and implemented role, bridge assumptions and downstream uncertainty |
| Mix five mismatch dimensions in every task | A negative result cannot be attributed to any one mechanism | Begin with one operator distinction per task and matched populations/measurements |
| Prefer the condition with smallest reference error | Rewards coincidental closeness; may encourage outcome-based case selection | Define source-role labels before reveal; evaluate every predeclared analysis and hidden world |
| Weighted average of unlike coefficients | Coefficients with different adjustment sets or scales are not estimates of the same parameter | Convert to a common estimand only when identified; otherwise use an explicit model/scenario rather than arithmetic pooling |
| Give a wide interval or prior to every mismatch | A range is not calibrated uncertainty; a sufficiently broad range covers everything | Define its meaning; measure both coverage and informativeness only across enough held-out controlled worlds |
| Estimate about USD50 for 384 authors | Costs depend on context, tool calls, model settings and added review | Use actual ledger distributions and reservation ceilings; include all review calls and failures |

For orientation only, the completed request-only unit used USD3.9851613 for twelve constructors, while the review unit used USD4.8731316 for 24 review sessions. Simple arithmetic extrapolations give about USD127.53 per 384 construction sessions or USD77.97 per 384 review sessions at those observed averages, before any extra gate arm. These are not forecasts: the proposed compact controlled tasks could be cheaper and other models or prompts could be much more expensive. Neither USD50 nor the user's monthly credit is a defensible authorization or billing estimate.

## Smallest discriminating pilot

### First make the probe interpretable without new model spending

Freeze two controlled operator templates, source-record schemas, valid bridges and independent adjudication rules. Check that the different hidden laws really generate identical evidence where nonidentification is claimed. Make source-statistic replay and analytical identities unit-testable. Retrospectively code the existing complete roster without changing frozen models or treating exposed clinical targets as new confirmation.

The controlled evidence records should be explicitly described as artificial experimental records, not attributed to fabricated real papers. They can reproduce statistical patterns found in the real source audit. Freeze all record contents, orders, target laws and evaluation operators before any new construction. No searching for a new favorable patient cohort is needed for this mechanism test.

### Two operator families

**A. Marginal correlation versus covariate-adjusted residual correlation.** Request a joint generator for continuous X, Y and Z and the residual association of Y and Z after adjustment for X. The indirect record reports a marginal correlation of Y and Z. Under a linear model,

`Cov(Y,Z) = beta_Y * beta_Z * Var(X) + Cov(e_Y,e_Z)`.

The conditional correlation additionally needs the two residual variances. Do not quietly supply enough additional source moments to identify all of these and then call the valid derivation an error. Include at least two hidden laws with different residual dependence but identical allowed marginal evidence. An applicable record directly reports the conditional quantity or supplies the complete valid covariance bridge. A raw-to-residual substitution without its missing terms is the numerical misuse of interest.

**B. Between-person correlation versus single-visit residual correlation.** Request repeated or single-visit joint measurements with a declared analysis. Use a Gaussian random-intercept setup initially so a log transformation does not add another mechanism:

`rho_visit = (Cov(b_Y,b_Z) + Cov(e_Y,e_Z)) / sqrt[(Var(b_Y)+Var(e_Y)) * (Var(b_Z)+Var(e_Z))]`.

An indirect record reports the random-intercept correlation only. It does not identify same-visit residual correlation when the within-person covariance or variance components are missing. Two hidden laws can share the reported between-person correlation and differ in within-visit dependence. An applicable record provides the requested quantity or the full variance-component bridge. A source may legitimately constrain the random intercept while leaving the other component as an explicit assumption.

Each family should include a harmless exact unit-conversion check so a policy that rejects everything does not appear competent. A simple algebraically compatible case is a positive control. A source's reported sampling uncertainty is retained separately from unspecified bridge uncertainty. If the task uses a fitted coefficient, record its adjustment set and link function explicitly; do not substitute a marginal/conditional correlation for a regression coefficient.

### Four information conditions

| Condition | Supplied relation evidence | Intended discrimination |
|---|---|---|
| None | Common population, variables and nuisance information; no identifying joint relation | What assumptions does the model make without evidence? |
| Applicable | Exactly matched or fully transformable identifying relation | Can the Agent use a legitimate constraint? |
| Indirect | Realistic statistic about a different operator, with its true definition visible | Does it retain the correct source role or silently promote it? |
| Both | Applicable and indirect records, with order counterbalanced | Does a tempting additional statistic displace or corrupt a valid constraint? |

All conditions get the same task, interface, model and allowed execution budget. Information differences are intentional; this is not an end-to-end workflow comparison. Source order and numerical presentation should be counterbalanced across fresh contexts, not chosen after results. Use the same hidden-law evaluation for all assigned conditions. Never provide hidden target measurements or downstream answers to the author or reviewer.

### Two defensible scales; choose one, not both automatically

**Recommended first step: 24 construction sessions.** Two operator families x four information conditions x three fresh constructor sessions x one existing economical GPT configuration. This is a descriptive mechanism pilot with very few task templates; it is not a powered cross-model benchmark. The primary endpoint is unjustified numerical promotion, with functional data-generation checks and hidden-law analysis profiles reported separately. No gate arm is needed until this establishes a reproducible action failure.

**If the immediate question must include a gate: 24 total sessions.** Use two constructors per family-condition (16 initial sessions). Take all four `both`-condition starting laws, without selecting by success or error, and give each to two new reviewers: ordinary review and semantic review, with identical evidence, tools and remaining budgets (eight review sessions). This isolates a small paired revision-policy contrast but has even less information for construction prevalence. It is preferable to adding only a semantic reviewer and attributing extra deliberation to the gate.

If the first design uses three authors, reviewing only four of its six `both` laws would require a predeclared, outcome-independent selection rule. A cleaner policy test reviews all six, giving twelve additional sessions and 36 total. A four-session gate add-on chosen after inspection is not a credible treatment comparison. Do not silently turn a 24-session pilot into that larger study.

Either design can use the selected law's analytical moments and a small fixed set of simulation seeds to check implementation. Synthetic rows and seeds are not extra constructors. An identifiable numerical-error benchmark and an unidentifiable-world pair serve different purposes: the latter tests whether the output honestly represents ambiguity, not whether it guesses the hidden law.

## What an applicability intervention should actually do

Do not start with a universal five-field rejection gate or mandatory weighted pooling. Provide a reusable operator contract and let the Agent choose a scientifically defensible action:

- Use directly, or make an exact transformation with its required inputs.
- Borrow under an explicit target/source model, distinguishing sampling variance from transport uncertainty.
- Construct several compatible scenarios or a generative mixture at the **law** level; disclose what its mixing weights mean.
- Seek missing conditional information if retrieval is part of a later end-to-end study.
- Decline a directly identified claim while still supplying assumption-labeled virtual data.

A mixture of models, an average of model parameters and a pooled dataset generally have different scientific properties. Mixing correlation matrices or coefficients can require additional constraints, and each final covariance matrix must remain positive semidefinite. Marginal means, separate adjusted slopes or separate regressions usually do not determine all cross-covariances. A weight cannot manufacture the missing information.

For the controlled policy contrast, ordinary and semantic review must have the same source set, tool access and budget; otherwise the effect combines evidence retrieval, information and review policy. This deliberate same-information mechanistic test coexists with the paper's earlier request-only end-to-end studies. It does not require redefining their ordinary-Agent baseline as a curated-packet agent.

## Outcomes, units and falsifiers

Predeclare the source-role coding rubric and have an independent reviewer inspect the record plus code without hidden-law errors. Do not use an LLM judge alone to certify semantic correctness. Separate extraction, recognition, bridge specification, actual commitment and downstream claims. Recognition must be observed before final commitment in the **same session**, or clearly labeled as a separate ability probe; a separate model's classification is not proof the constructing Agent acknowledged the issue.

Report per family and condition:

1. Rate of unjustified direct-use commitments and their exact traceable code locations. Denominator: relevant numerical decisions, clustered within authors; also show author-level counts.
2. Correct use of applicable/transformable records, retention of useful constraints, executable delivery and explicit unsupported assumptions. A system that avoids errors by refusing every task must not win unqualified.
3. Each requested scientific estimand under the generated law, plus mean/dispersion/coherence checks. Use effect units and analytical targets where known. No cross-unit total error score.
4. Whether uncertainty/scenario statements actually propagate to the generated datasets and requested analyses. A decorative interval in notes is not propagation.
5. API/tool costs and failure/retention records, including unchanged revisions. A large self-reported confidence drop is not an established improvement.

Do not report significance from two templates or inflate n with 3,000 generated rows. The constructors are repeated responses from fixed model configurations, not independent clinical populations. Two model brands are fixed conditions, not a random sample of models. Generalization requires additional independent task families later, not just more seeds or eight authors per cell. If a large follow-up is warranted, use pilot effect variability and clustered simulation-based power calculations for the specified estimand; there is no justified universal minimum of eight authors.

The proposed mechanism is weakened or falsified if any of these occur:

- Most allegedly indirect uses have valid algebraic bridges or honest prior/scenario roles on blind audit.
- Replacing a source's statistical label while holding its numeric value fixed does not change unsupported adoption, suggesting another mechanism or ineffective manipulation.
- Incorrect role labels occur, but actual numerical construction does not use the disputed quantity.
- Applicable evidence does not improve identification or execution, so the probe mostly measures unrelated implementation failure.
- A semantic intervention improves prose/labels without changing unsupported commitments or meaningful uncertainty propagation.
- It reduces unsupported use by discarding identifying evidence, failing to deliver data, or generating vacuously broad scenarios.
- Ordinary review matches semantic review under the same evidence and budget.
- The pattern disappears across the second operator family or depends on one particular number, source order or task wording.

Numerical closeness in a single world is not a required falsifier of semantic misuse: incompatible evidence can be accidentally close. Conversely, larger error against one unidentifiable hidden world is not a sufficient falsifier of a correctly stated model ensemble. Keep those axes separate.

## Positive formulation and paper decision

A positive, testable contribution would be: **a scientific Agent converts partial published evidence into executable joint-model assumptions while preserving the distinction between identified quantities, valid transformations and transported or unidentified components; this distinction makes downstream virtual-data analyses inspectable and can prevent specific unsupported numerical commitments without eliminating useful generation.**

The minimal paper extension could contain an all-roster retrospective source-to-code map, the controlled operator pilot, and one worked end-to-end biomedical trace already present in the project. The pilot does not by itself demonstrate biomedical discovery, clinical transportability, calibrated risk labels or general superiority. The current source/code records support the map; the controlled contrast and any intervention benefit remain untested.

If the pilot shows no semantic intervention advantage, retain the operator benchmark and error anatomy only if the findings are robust and distinct from the known true-but-inapplicable evidence literature. If the basic failure is rare or the proposed labels are not reproducible, stop this branch and keep the quality-assurance result as a limitation. Do not replace the successful data-generation application with an unproven failure headline, or add multiple Agents, new retrieval components or a 384-author benchmark to rescue a weak initial effect.

Suggested provisional framing: **From Reported Statistics to Generative Commitments: Evidence Semantics in Scientific Agents**. This is a candidate framing, not a novelty or venue claim. Freeze the audit definitions and the minimal discriminating protocol before any paid follow-up; do not change the main manuscript thesis solely from selected historical discrepancies.
