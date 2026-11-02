# Positioning against G-Sim and LLMSynthor

Prepared 1 November 2026, America/Chicago. This is a bounded comparison of two direct predecessors with our actual implementation and completed results. It adds no experiment and establishes no field-wide priority claim. The working manuscript and frozen scientific artifacts are unchanged.

## Decision

Our strongest direction remains **turning published biomedical evidence, a population request and optional observations into virtual data that support specified scientific analyses**. Whole-cohort generation without individual input is central; enrichment and missing-cell completion remain other information regimes.

The potential methodological contribution is **study-conditioned evidence translation into a joint generator**: preserving what each study actually estimated, deciding what can constrain generation, and making the assumptions needed to complete and transfer the joint distribution explicit. The current implementation provides parts of this procedure and limited analytical feasibility. It does not yet establish a new general synthesis algorithm, reliable repair, or superiority over G-Sim or LLMSynthor.

Neither predecessor blocks this research. Both provide useful generation mechanisms that could be extended to our setting. The distinction must concern an implemented scientific operation and its consequences, rather than an assertion that their general frameworks cannot express our task.

## 1. What each project is trying to solve

| Dimension | G-Sim | LLMSynthor | Our intended problem and current boundary |
|---|---|---|---|
| Practical bottleneck | Constructing stochastic system simulators requires substantial structural modelling and parameter calibration. | Individual records are unavailable or expensive; plausible LLM records may collectively miss observed macro-statistics. | Biomedical evidence is distributed across studies with different populations, measurements and analysis definitions; available observations may omit variables or may be entirely absent. |
| Immediate output | An executable stochastic simulator, including state transitions, parameters and random mechanisms. | A growing dataset of micro-records generated from LLM-planned local configurations. | A virtual dataset plus its construction record, evidence interpretation and assumptions, with an executable recipe where used, for subsequent scientific analysis. |
| Main alignment object | Observed system behaviour through simulation discrepancies; the framework admits diverse data and summaries. | Supplied target macro-statistics; the reported implementation uses marginal and joint frequency tables. | Different study-specific estimates and contextual evidence, followed by assessment in a separately reserved target population. Not every source item is a numerical calibration target. |
| Agent's substantive decision | Simulator structure and revisions; a separate optimizer or SBI procedure calibrates numerical parameters. | Relevant dependencies, local variable configurations/ranges and record counts to correct discrepancies. | Joint structure, parameters and transport assumptions. In CHNS the Agent authored Python models; many biomedical parameters were explicitly assumed rather than identified by sources. |
| Current strongest empirical evidence | Known-truth simulated dynamical environments and system-use evaluations. | Mixed-source mobility, controlled transactions, hierarchical ACS population synthesis and downstream utility. | Whole-cohort biomedical analytical feasibility on CHNS and an artificial conditional-evidence translation example, with important quantitative failures. |

Sources: G-Sim §§2.3, 3 and 5, Appendices B.2 and G.1; LLMSynthor §§3–4 and Appendix A; our [core method](../reports/core_v0_2026-10-31/CORE_METHOD_V0.md), [CHNS report](../reports/chns_admission_2026-11-01/f2/CASE_RESULTS.md) and [contribution map](CONTRIBUTION_EVIDENCE_MAP_2026-11-01.md).

### Corrections to overly narrow comparisons

**G-Sim is not restricted in principle to complete raw trajectories.** Section 2.3 explicitly permits multiple partially overlapping datasets, unpaired observations and contextual text. Appendix B.2 permits summary-based discrepancies and domain checks. Appendix G.1 discusses aggregate-level calibration. Its principal experiments use hand-designed simulator trajectories; that empirical setting must not be confused with the entire formal scope. The earlier local review's emphasis on aggregate data as a future direction should be read with this correction. Multi-source biomedical application is not established merely by broad expressivity, but neither is it excluded. [Published paper](https://proceedings.mlr.press/v267/holt25b.html)

**LLMSynthor already addresses macro-to-micro generation without individual inputs.** Its operator can represent arbitrary statistics in principle, and §3.2 permits optional approximation of missing joint statistics. Its mobility experiment combines complementary sources; its ACS case evaluates 16 policy queries. Appendix A distinguishes aggregate-only use from benchmarks where available microdata supply target summaries. We cannot say it requires patient records, cannot combine sources, or only produces distributions without useful analyses. [Latest checked full text, v4](https://arxiv.org/html/2505.14752v4)

## 2. The substantive difference: the same variable names need not imply the same constraint

Consider an illustrative biomedical request: generate age, sex, BMI, glucose and HbA1c for a specified adult population, with no individual input. Available articles might report:

- an unadjusted glucose–HbA1c correlation in one selected population;
- a BMI–HbA1c coefficient adjusted for age and sex in another;
- age-stratified summaries from an older population with a different assay;
- a standard deviation describing individual variability, rather than uncertainty in an estimated effect.

These are not interchangeable numbers describing one target joint distribution. A reported adjusted coefficient is a projection under its own adjustment set and population. It is not automatically a structural coefficient to insert into a joint generator. A correlation can change under altered case mix without any change in a conditional relationship. Matching a source's statistic on the target table can therefore be the wrong objective.

The desired operation is to retain a source record of the form:

`study → population/selection → measurement and units → estimator and adjustment → value and uncertainty → permitted use`

An ideal source check is `T_j(G evaluated under source context C_j) ≈ reported s_j`; generation for the user uses a separately specified target context. If the source context cannot be reconstructed, the method must state the approximation, use the result only as context, or leave the check unavailable. Completing an unidentified relationship still requires an assumption or additional evidence.

**This equation is explanatory, not a new statistical estimator.** G-Sim's general discrepancy formulation could accommodate it; LLMSynthor could be extended with suitable aggregation operators. Indirect inference, simulated-moment methods, statistical matching and evidence synthesis also precede this work. The potential contribution lies in a concrete biomedical translation procedure and demonstrated analytical usefulness under these information conditions. A comparison with these two papers alone does not complete the statistical-prior-work review.

The completed CHNS implementation generates **no source-context tables**. It preserves source conditions and implements restricted mathematical checks; its numerical correlation feedback evaluates assumption-defined proxies on the generated target table. This gap cannot be hidden by calling the implementation a general evidence compiler.

## 3. Capability comparison without claiming overall superiority

| Capability | G-Sim | LLMSynthor | Our supported status |
|---|---|---|---|
| LLM makes substantive generation decisions | Yes: executable simulator structure. | Yes: dependence groups and sampling proposals. | Yes: Agent-authored models; not merely a narrative around root-written scientific coefficients. This is shared, not novel. |
| Generation without individual input | Aggregate calibration is within its stated scope; main benchmarks use trajectories. | Explicit central setting. | Demonstrated whole-cohort execution with external evidence in CHNS. This capability alone is not unique. |
| Multiple sources or partial variable coverage | Explicit formal support. | Demonstrated mixed-source mobility and optional missing-joint approximation. | Source records retain heterogeneous biomedical conditions; comprehensive source reconstruction remains absent. |
| Statistical feedback and revision | Structural refinement plus numerical calibration. | Discrepancy-guided addition of record batches. | Strict and conditional feedback paths execute; both CHNS Agents retained their models. No demonstrated repair gain. |
| Dynamical interventions and system policies | Central intended use and evaluated in simulated environments. | Context-controlled scenarios, including an event example. | No validated causal, intervention or longitudinal capability in the present core case. |
| Hierarchical or variable-length records | Structured system state can include patient-level entities. | Demonstrated household/person records and mobility records. | Current central evidence concerns five-variable biomedical tables. No superior breadth claim. |
| Downstream use of generated data | System-level applications, beyond matching a histogram. | Prediction and population queries. | Three prespecified biomedical regressions on each frozen CHNS table, with directional success and effect-scale failures. Downstream use itself is not new. |
| Study-specific statistical meaning | Flexible checks/context can express it; the paper does not establish our biomedical extraction-to-transfer workflow. | Generic aggregation can express more than histograms; the reported correction mechanism uses discretized frequencies. | Supported checks enforce declared estimator/role/adjustment/unit consistency; source extraction and transport are not certified. This is a concrete implemented operation, not yet a proven advantage. |
| Uncertainty | SBI parameter uncertainty conditional on a chosen structure; structural limitations acknowledged. | Run variation mainly reflects stochastic generation; no universal uncertainty guarantee. | Assumptions and uncertainty types recorded; no calibrated source, structural or transport uncertainty. Seed variation is not a replacement. |

The correct conclusion is complementarity and a distinct applied inference problem, not that our prototype is more capable overall. G-Sim supplies a strong program-construction precedent; LLMSynthor supplies a strong proposal-generation precedent. Either could become a backend for a study-aware evidence interface. That is a design option, not an integration already implemented or a new experiment authorized here.

## 4. The concrete operations we can point to in our code

| Operation | Implementation locator | What it does and does not establish |
|---|---|---|
| Bind a statistic to its declared meaning | [semantic_feedback_v1.py](../cohort_harness/semantic_feedback_v1.py), `_signature` line 53, `_measurement` line 109, `_bind_evidence` line 155, `_preflight` line 199 | Checks estimator, roles, predictors/adjustment, coefficient term, selection, units and associated declarations before arithmetic. It does not independently authenticate the article extraction. |
| Preserve unsupported checks | Same module, lines 252–259 and 291–297 | Unsupported weighting or unknown transformations can leave a check unavailable with a null discrepancy. Absence of a numerical score is not successful fit. |
| Separate a conditional interpretation from source reproduction | [conditional_feedback_v1.py](../cohort_harness/conditional_feedback_v1.py), lines 117–132 and 167–208 | Restricted, separately approved equal-weight Pearson/Spearman interpretations with unreported original weights are reported as target proxies. This exception does not cover known weighted estimators. Original strict results remain unavailable. Population and specimen differences do not disappear. |
| Trace model assumptions | [contracts.py](../cohort_harness/contracts.py), `validate_spec` line 318; [C1 specification](../reports/chns_admission_2026-11-01/f2/candidates/C1_initial/model_spec.json); [C2 specification](../reports/chns_admission_2026-11-01/f2/candidates/C2_initial/model_spec.json) | Every parameter has provenance references and derivation text. Validation checks completeness and references, not the scientific truth of a derivation or automatic identification of a parameter. |
| Generate joint records under real Agent choices | C1/C2 specifications and the [case implementation account](../reports/chns_admission_2026-11-01/f2/CASE_RESULTS.md) | C1 uses sequential conditional lognormal models; C2 uses a covariate-dependent mixture with correlated glycemic residuals. Their choice is substantive, but these model families are not new. |
| Apply the feedback boundary before target evaluation | [CHNS controller](../reports/chns_admission_2026-11-01/f2/controller/chns_f2_controller.py), `freeze_stage` line 171 and `run_stage` line 231 | Exact frozen evidence/feedback binding and strict-before-conditional execution. This makes the experiment inspectable; it is not an automatic improvement policy or an Agent-wide filesystem sandbox. |

The old [whole-cohort adapter](../cohort_harness/whole_cohort_feedback.py) evaluates an already generated task table under identity measurement. The earlier enrichment replay uses supplied covariate-only source contexts. Neither implements arbitrary study sampling, source missingness, assay conversion or whole-cohort population reconstruction. See the [explicit CHNS interpretation boundary](../reports/chns_admission_2026-11-01/f2/evidence/SOURCE_INTERPRETATIONS.md).

These checks matter because they can prevent an attractive but invalid feedback objective. Nevertheless, checking metadata alone would be a weak central methods contribution. The paper's output must remain useful virtual data, and any claim that these operations improve those data needs corresponding evidence.

## 5. Contribution claims at three levels

| Level | Claim we can make | Present evidence / remaining requirement |
|---|---|---|
| **Implemented research capability** | An Agent can construct a complete biomedical joint generator from admitted external evidence and a target description without target individual records or target numerical feedback. | CHNS whole-cohort case. This is an implemented application and information regime, not first aggregate-only synthesis. |
| **Implemented method with preliminary scientific evidence** | Evidence use retains study-specific statistical declarations and named assumptions; generated data can be reused for selected prespecified analyses. | Semantic/proxy code plus CHNS results and the bounded conditional-evidence illustration. Current source-context handling is restricted and partly curated. |
| **Potential stronger innovation, not established** | A study-conditioned translation mechanism improves transferable scientific analyses compared with a capable generator given the same evidence. | Not settled by current results. A new label, an extra Agent, more seeds, or a different evidence packet does not establish this claim. No new comparison is launched by this document. |

The primary innovation candidate can be stated as **making heterogeneous published study estimates operational for target-population joint-data generation**. Its value would be more than copying source numbers: it would preserve relevant conditional structure through population and analysis changes, while making unsupported completion visible. The present project has concrete building blocks, but not a fully demonstrated general solution.

### What our results currently say

- **Real case:** two constructors generated six unique 3,000-row CHNS-directed tables. Twelve execution slots include identical retained copies. All eighteen primary coefficients have the measured reference's positive directions. BMI effect magnitudes are only approximately 30–39% of the reference estimate; HbA1c/glucose variation is too low. The reference comprises 6,631 selected complete cases, not known population truth. Both constructors retained their original models, so there is no revision gain. The regression outputs were held out from numerical feedback; related associations were present in source evidence. [Complete results](../reports/chns_admission_2026-11-01/f2/CASE_RESULTS.md)
- **Mechanism illustration:** artificial group-conditional evidence translated to target-composition slopes near the stipulated 0.50 and −0.20, whereas a marginal/pairwise construction stayed near 0.13–0.15. This illustrates an evidence-to-joint-data operation; the target projections are algebraically implied, and one constructor per evidence packet confounds evidence with author variation. A marginal-evidence construction was worse than description-only generation in one world. Compatible residual laws still imply different tails. [Complete pilot](../reports/evidence_value_2026-11-01/RESULTS.md)

These support selected analytical feasibility and a bounded translation example. They do not prove quantitative interchangeability, recovery of unmeasured individual values, general algorithmic superiority, new biological discovery, recruitment savings, or calibrated inference. Primary failures belong in Results. Optional unvalidated capabilities can remain limitations.

## 6. What the paper should learn from their stories

| Paper | Narrative logic | Lesson for our manuscript |
|---|---|---|
| G-Sim | Expert-intensive simulator construction → LLM structure proposals plus numerical calibration → faithful and useful system simulation. | Explain the division of scientific decisions and deterministic computation. Make the generated object and its intended use concrete. |
| LLMSynthor | Missing microdata and macro mismatch → dependency inference plus proposal sampling → fidelity, realism and utility across record formats. | Demonstrate the value of the generated dataset, not just that an Agent ran. Make the information available to each method explicit. |
| Ours | Missing measurements and fragmented study estimates → explicit evidence interpretation and joint completion → reuse for specified scientific analyses in a reserved population, with quantitative limits. | Keep evidence-to-data generation central. Organize results by what the frozen data support; do not replace the paper with an audit framework or conceal main failures in limitations. |

Recommended working title remains **From Published Evidence to Virtual Cohorts for Scientific Analysis**. A more technical subtitle or positioning phrase is **Study-conditioned evidence translation for biomedical data generation**. Avoid an unconditional “analysis-ready,” “clinically equivalent,” “autonomous discovery,” or “universal” claim.

### Manuscript-ready positioning paragraph

> G-Sim couples language-model construction of stochastic simulators with numerical calibration and diagnostic refinement, while LLMSynthor converts aggregate constraints into micro-records through dependency inference and discrepancy-guided proposals. These approaches establish that LLMs can participate substantively in calibrated generation, including aggregate-only and multi-source settings. We investigate a related biomedical problem: constructing joint virtual data from published results whose populations, measurements and estimands need not coincide with those of the intended user. Our procedure retains declared statistical semantics and generation assumptions, separates supported source checks from assumption-defined target diagnostics, and evaluates several prespecified analyses on the same frozen virtual release against separately reserved measurements. The current results establish selected analytical feasibility and expose effect-scale, variability and transport limitations; they do not establish general superiority over existing synthesis methods.

In the CHNS instantiation, both strict correlation checks remained unavailable because original weighting was unreported; the numerical diagnostics were separately approved equal-weight target proxies. This qualification belongs in the Methods alongside the general positioning paragraph.

### Contribution statements supported by the present record

1. We specify and implement an evidence-to-cohort workflow supporting complete-cohort generation without individual inputs, with optional observation regimes retained in the system design.
2. We bind supported statistical feedback to declared study estimands and explicitly separate unavailable checks from approved assumption-defined target proxies, while recording the evidence and assumptions behind joint generation.
3. We evaluate analytical reuse on a reserved real cohort and provide a bounded artificial illustration of conditional-evidence translation, reporting both successful directions and consequential quantitative failures.

These are contribution statements, not three independent algorithmic novelty claims. The strongest methods claim remains conditional on showing that the specific translation operation adds value; feasibility alone supports a narrower paper. No particular venue follows automatically from this comparison.

## 7. Evidence boundary and next writing action

The comparison used the cached published G-Sim paper and pinned implementation, the cached LLMSynthor v3 paper, and a fresh browser reading of LLMSynthor **v4, 8 June 2026**: §§3–4, §6 and Appendix A. The relevant capability conclusions remain supported by v4. No claim is made that the entire v3/v4 documents are byte-identical. G-Sim's publication page was also checked in Chrome.

- [G-Sim, ICML 2025](https://proceedings.mlr.press/v267/holt25b.html); primary locators: §2.3 pp.3–4; §3 pp.5–6; §5 p.7; Appendix B.2 pp.18–20; Appendix G.1 pp.42–43.
- [G-Sim pinned implementation](https://github.com/samholt/generative-simulations/tree/72b5d51a7790b8b2ebc87973ee5e9d21aa818ece); relevant paths: `agents.py`, `utils/gesim_prompts.py`, `utils/llm_tools.py`, `libs/SIR/env.py`. This is a static inspection, not an independent reproduction.
- [LLMSynthor v4](https://arxiv.org/html/2505.14752v4); primary locators: §§3.1–3.3; §§4.1–4.3; §6; Appendix A. [KDD DOI](https://doi.org/10.1145/3770855.3818965).
- [LLMSynthor repository snapshot inspected previously](https://github.com/YihongT/LLMSynthor/tree/92e443f93c6edecc0fa9ca3045d4204da7d42aa5). That snapshot has project material rather than executable algorithm code. This is not a claim about the repository's current release status; method descriptions here are paper-derived.

The immediate action is to use this positioning in the manuscript, keep prior overlapping capabilities acknowledged, and tie each claimed operation to the actual implementation and result. If a stronger algorithmic improvement is retained as essential, identify its single missing evidentiary requirement before considering further work. This document does not reopen revealed targets, add cases, start a baseline suite, or resume the paused automation. General replay, broad uncertainty calibration and arbitrary variable requests remain outside present demonstrated capability.
