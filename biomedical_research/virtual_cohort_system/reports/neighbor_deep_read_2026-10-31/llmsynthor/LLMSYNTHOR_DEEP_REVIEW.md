# LLMSynthor: paper, implementation, data, and evaluation audit

> Export note: this is an original reading/audit note. Downloaded papers and third-party implementation snapshots remain in the local research archive. Later scope decisions, including evidence-only full-cohort generation as a core intended capability, are recorded in the current paper-direction document.

Audit date: 2026-10-31. Scope: the 12-page arXiv v3, its appendices and figures, the linked official repository and project page, and public dataset-provider documentation. No experiments, generation, training, paid model calls, or target-outcome inspection were performed. Source PDFs and repository snapshots are retained locally only.

This is an original technical reading of Yihong Tang, Menglin Kong, Junlin He, Tong Nie, Wei Ma, and Lijun Sun, *LLMSynthor: Macro-Aligned Micro-Records Synthesis with Large Language Models*, arXiv:2505.14752v3, 31 May 2026, KDD 2026, DOI 10.1145/3770855.3818965. The PDF identifies a Creative Commons Attribution 4.0 license on page 1. Paper descriptions below are attributed to that work; proposed extensions are explicitly our analysis.

## 1. Decision-relevant findings

LLMSynthor is a substantial near neighbor. It already addresses generation from aggregate information, combines multiple sources in its mobility example, selects dependency groups using an LLM, and uses statistical feedback to guide further generation. Neither “an Agent reads statistics and generates data,” “multiple sources,” nor “generate/check/revise” alone is a sufficiently specific distinction.

The actual generation mechanism is also informative for our design: the LLM usually emits **proposals containing category assignments, numerical ranges, and record counts**. A sampler executes these proposals; the growing dataset supplies the next discrepancy report. This is materially different from asking an LLM to print every final measurement. Program execution does not make the LLM incidental: its choices define where probability mass is placed.

The paper does **not** establish that a missing biomedical target distribution can be recovered from heterogeneous external studies. Its experiments can obtain macro-statistics from reference micro-records, including joint tables and adaptive histogram refinements. An entire unmeasured column in a new target cohort has a different information boundary.

The public repository does **not currently provide an implementation to audit or run**. At the pinned commit below it contains a README, two image files, and two macOS metadata files. The paper-to-code gap must be reported as an availability limitation, not treated as evidence that the published experiments did not happen.

## 2. Version and release audit

| Item | Verified finding | Locator |
|---|---|---|
| Paper reviewed | arXiv v3, 31 May 2026, 12 pages, six authors; KDD 2026 DOI printed | [Paper PDF](https://arxiv.org/pdf/2505.14752v3), p. 1 |
| Original title retained by repository | *Large Language Models for Data Synthesis*, three-author citation | [Pinned README](https://github.com/YihongT/LLMSynthor/blob/92e443f93c6edecc0fa9ca3045d4204da7d42aa5/README.md#L37-L41) |
| Repository HEAD | 92e443f93c6edecc0fa9ca3045d4204da7d42aa5; commit date 2025-07-03 | [Commit](https://github.com/YihongT/LLMSynthor/commit/92e443f93c6edecc0fa9ca3045d4204da7d42aa5) |
| Tree completeness | Recursive tree API reports truncated=false; only five files | Local repository_tree.json |
| Branches/tags/releases | Main only; no tags; no releases | Local branches.json, tags.json, releases.json |
| Code availability notice | README promises release following acceptance | [README lines 18–20](https://github.com/YihongT/LLMSynthor/blob/92e443f93c6edecc0fa9ca3045d4204da7d42aa5/README.md#L18-L20) |
| License for code | No license file; README says an open-source license will accompany publication | [README lines 26–28](https://github.com/YihongT/LLMSynthor/blob/92e443f93c6edecc0fa9ca3045d4204da7d42aa5/README.md#L26-L28) |
| Alternate official route | Project page retains old title and points to the same GitHub repository | [Project page](https://yihongt.github.io/llmsynthor_web/) |
| Community requests | Two open issues about release; both show zero comments when checked | [Issue 1](https://github.com/YihongT/LLMSynthor/issues/1), [Issue 2](https://github.com/YihongT/LLMSynthor/issues/2) |

The paper’s abstract says source code is available. The linked repository does not substantiate that at this audit. We can reconstruct a **paper-based implementation**, but cannot call it reproduction of their released code or attest to execution details not specified in the paper.

## 3. What the method actually computes

### 3.1 Information contract

A micro-record consists of named variables and values; record length may vary, allowing household structures. The input is a collection of aggregate statistics plus variable descriptions. An aggregation operator maps a candidate dataset to the same statistics. The objective is to reduce discrepancies between candidate summaries and target summaries. In practice the summaries are marginal histograms and joint contingency tables. [Paper §3, pp. 3–5](https://arxiv.org/html/2505.14752v3#S3)

The LLM identifies groups of related variables. The paper then retains marginals and selects or refines the joint statistics used for guidance. It explicitly distinguishes:

- joint statistics actually available;
- numerical constraints reliably supplied by practitioners;
- unsupported relationships that can be excluded;
- optional approximate joint statistics suggested by the LLM when approximate control is acceptable.

Therefore, “LLM dependency inference” does not mean all numerical joint relationships were discovered from names without reference data. Selection of variable groups, acquisition of their numerical target tables, and sampling from them are separate steps. [§3.2, p. 3](https://arxiv.org/html/2505.14752v3#S3.SS2)

The copula terminology is an interpretation motivating separation of marginals and dependence. The supplied method infers variable subsets and uses them for statistical alignment. The paper does not provide a normalized copula density estimator, a general identifiability result, or calibrated posterior uncertainty for unobserved relationships.

### 3.2 Execution trace

| Stage | LLM or program? | Actual representation/action | Source |
|---|---|---|---|
| Define schema | Provided descriptions | Valid categories, numerical types/ranges, domain names | §3 and App. C |
| Select related variables | LLM | JSON groups of two or more variable names | App. C.2, p. 12 |
| Obtain guidance | Target-statistic source + aggregation logic | Compatible marginal and selected joint frequency tables | §3.2; App. A |
| Diagnose cumulative dataset | Program | Target frequency minus synthetic frequency for named bins/cells | §3.3; App. A |
| Plan correction | LLM | A small collection of proposals, each with a rationale, variable configuration, and count | §3.3; App. C.1 |
| Produce records | Sampler | Categories fixed by proposal; continuous values sampled in proposed intervals | §3.3, p. 5 |
| Update | Program | Append batch to cumulative dataset | Algorithm 1 |
| Final output | Program | Final cumulative dataset after the loop | Algorithm 1 |

The example on page 5 asks for 50 trips with fixed origin, destination, transport mode and activity, and a time interval. It does not ask the model to separately choose 50 exact timestamps.

For numerical variables, the main method states uniform sampling inside intervals; Appendix C allows uniform sampling or another simple scheme. A mixture of such local proposals can express nontrivial dependencies across the entire population. **Conditional independence between numerical variables within each proposal is not specified clearly enough to verify without code.** If implemented as independent uniform draws within each box, the fine-scale within-box dependence is an implementation assumption, while cross-box dependence comes from the mixture. This distinction matters when evaluating continuous slopes and curvature.

The proposal prompt requests a pure JSON object, uses a “proposal” string in the displayed schema, and discusses category/min/max rules. It is not a complete executable schema specification. Parsing, schema repair, integer rounding, duplicate handling, retry limits, and exact row-budget enforcement cannot be audited from released code.

### 3.3 What “revision” means here

The described algorithm adds new records. Appendix A explicitly focuses on positive discrepancies because it cannot remove records. Overrepresented regions can only be diluted by adding other records. There is no demonstrated best-candidate selector, acceptance/rejection gate for objective improvement, or rollback rule in Algorithm 1. Record validity checks appear in evaluation but should not be silently conflated with proposal-selection logic.

This is well matched to constructing an initially empty cohort. For our fixed participants with observed covariates, freely appending participants would change the problem. An adaptation needs to preserve participant IDs and observed cells while revising only allowed generated values. That is a concrete engineering difference; whether it becomes a methodological contribution depends on generalization and evidence.

The text sometimes describes iterating until sufficient alignment, while the algorithm takes a fixed iteration count. Appendix A gives 100 iterations. The paper does not expose a fully specified data-dependent stopping policy.

### 3.4 Defaults and resource use

| Detail | Reported setting / unresolved point |
|---|---|
| Proposal count | 5 per iteration |
| Iterations | 100 |
| Dependency groups | 3; Appendix A says inferred each iteration, while Algorithm 1 places inference before the loop |
| Main backbone | GPT-4.1-nano Chat Completion; temperature 0.8 |
| Open-model comparisons | Qwen2.5-7B-Instruct and Qwen2.5-3B-Instruct in Table 3 |
| Local inference settings | vLLM; 2048 max new tokens; temperature 0.7; top_k 20; top_p 0.98 |
| Continuous bins | 6 quantile main bins; 8 uniform subdivisions in the most underrepresented main bin when micro-records are available |
| Repeats | At least 3; e-commerce rejection table explicitly uses 5 |
| Hardware | Xeon E5-2698 v4, 40 threads, 252 GB RAM, four 32 GB Tesla V100 GPUs |
| Learning | No task-specific model fine-tuning described for LLMSynthor |
| Cost reporting | Figure 7 shows time/iteration trade-offs; complete API token/call costs, retries and per-task usage are not provided |
| Runtime reproducibility | Exact environment, generator code, task configs and seeds are unavailable in the inspected official repository |

The procedure is inference-time planning, sampling and feedback. It is not training a new foundation model.

## 4. Data and evaluation, case by case

### 4.1 Mobility: mixing sources and creating a scenario

**Inputs:** Open PFLOW trip information (origin, destination and timestamp), with transport modes assigned by the authors; time–activity patterns from LLMob supply activity information absent from that source. **Output:** 30,000 trips in Tokyo over one day. [§4.1, pp. 5–6](https://arxiv.org/html/2505.14752v3#S4.SS1)

**Evaluation:** time–activity heatmaps, origin–destination heatmaps, spatial/time maps, mode/distance comparisons. The paper explicitly chooses a qualitative assessment for this mixed-source case instead of an adapted quantitative comparator.

**Extra scenario:** a concert at Tokyo Dome from 20:00 to 24:00 is inserted as a prompt, and the generation shows additional trips to the venue. This demonstrates contextual controllability. It is not validation against measured event attendance or a causal forecast benchmark.

**Access:** the original [Open PFLOW repository](https://github.com/sekilab/OpenPFLOW) lists nine Tokyo ZIP files and a trajectory schema including ID, time, longitude, latitude and transport mode. File links were identified, not downloaded. The LLMSynthor paper nevertheless says it assigns transport modes; the exact selection or assignment procedure remains unspecified. LLMob’s README describes trajectory folders and Foursquare-derived mappings. LLMSynthor does not release its specific macro tables, extraction scripts, transport-mode assignment rule, or precise source-version manifest. Consequently, upstream public availability is not enough for exact recreation of this benchmark.

Open PFLOW should also not be casually described as a fully measured GPS cohort: the original source describes constructing movement data from public statistics. The related current Pseudo PFLOW service likewise distinguishes synthetic movement from actual individual tracking. These sources are related but version-distinct; we did not infer which current release the LLMSynthor authors used. [Original lab description](https://sekilab.iis.u-tokyo.ac.jp/wp-content/uploads/2018kashiyama_openpflow.pdf), [current provider description](https://pflow.csis.u-tokyo.ac.jp/data-provision-service/about-pseudo-people-flow-data/)

**What it establishes:** compatible aggregates from different sources can guide a useful joint synthetic representation.

**What it leaves open:** numerical recovery of an unobserved cross-source relationship; transport under population and measurement differences; empirical correctness of newly prompted scenarios.

### 4.2 E-commerce: a controlled generative experiment

**Data:** 2,000 simulated reference transactions, six variables: age, gender, location tier, category, price, payment method. The known factorization is:

`p(age) p(gender) p(location) p(category | age, gender) p(price | category) p(payment | location)`.

The input contains every marginal and joint tables over groups defined by that generating network. This is a legitimate controlled problem, but it supplies the correct dependence groups and their numerical empirical targets. It is not evidence that the LLM identifies a hidden medical joint distribution from sparse unrelated articles. [§4.2, pp. 6–8](https://arxiv.org/html/2505.14752v3#S4.SS2)

**Baselines:** TVAE, CTGAN, CopulaGAN, GReaT, TabSyn, SPADA, IPF, and LLM-ICL. Table 1’s caption distinguishes supervision: IPF/LLM-ICL/LLMSynthor macro-only; SPADA macro+micro; other methods micro-trained. The surrounding text’s blanket statement that all baselines train on micro-records is inconsistent with that caption. For our comparisons, use the explicit information table, not the blanket prose.

**Metrics:**

- Marginals: Wasserstein distance for continuous variables, total variation for categorical variables, classifier two-sample test gap.
- Joint groups: Jensen–Shannon divergence and two-sample classification gap.
- Validity: three semantic plausibility rules; rejection rates.
- Utility: classifiers trained on synthetic data and evaluated on reference data for two derived labels.
- Dynamics: diversity, macro bias, conditional bias and runtime as generation grows.

The two utility labels, discount propensity and lifetime-value band, are computed from fixed hand-designed rules involving the transaction variables. The paper names logistic regression, decision trees and random forests. It does not give complete label equations, hyperparameters, or an auditable independent test-split protocol. It supports practical predictive utility in this synthetic task, not biomedical effect recovery or externally measured outcomes.

**Selected numerical results, as printed:**

| Quantity | LLMSynthor | Comparator | Locator |
|---|---:|---:|---|
| Age Wasserstein | 1.130 | TabSyn 1.196; IPF 5.270 | Table 1 |
| Price Wasserstein | 12.762 | TabSyn 114.120; SPADA 54.603 | Table 1 |
| Joint age/gender/category JSD | 0.071 | TabSyn 0.083 | Table 2 |
| Joint category/price JSD | 0.134 | TabSyn 0.237 | Table 2 |
| Joint location/payment JSD | 0.007 | TabSyn 0.027 | Table 2 |
| Semantic rejection | 0.5% | Reference 0.6%; LLM-ICL 0.0% | Table 4 |

These are published results, not independently reproduced measurements. The strong results on joint tables partly concern quantities that also guide generation. This is fit to observed information; it should not be labeled fully held-out relationship discovery.

### 4.3 ACS: real household structure and policy queries

**Data:** approximately 15,000 South Carolina ACS households after preprocessing. Variable-length household/person records make this more than a flat-table task. The source data family is public through Census PUMS, but the paper does not identify an exact ACS year, 1-year/5-year product, complete inclusion rules, source filenames, survey-weight treatment, or complete query definitions. [§4.3, pp. 8–9](https://arxiv.org/html/2505.14752v3#S4.SS3); [Census PUMS](https://www.census.gov/programs-surveys/acs/microdata.html)

**Comparison:** CP tensor factorization, hierarchical mixture model HMM, and neural variational inference NVI. Six thematic categories summarize 16 policy queries. It is not documented which query combinations were excluded from generation guidance. Therefore, these are useful downstream query evaluations, but cannot all be classified as independently withheld analyses.

| Measure | LLMSynthor | CP | HMM | NVI |
|---|---:|---:|---:|---:|
| Household rejection % | 13.3 | 73.9 | 57.8 | 96.8 |
| Demographic MRE | 0.21 | 0.54 | 0.56 | 0.53 |
| Employment MRE | 0.20 | 1.02 | 0.32 | 0.27 |
| Equity MRE | 0.25 | 5.79 | 4.23 | 5.49 |
| Household MRE | 0.13 | 2.34 | 2.01 | 2.06 |
| Mobility MRE | 0.35 | 1.47 | 0.48 | 0.24 |
| Vulnerability MRE | 0.37 | 0.86 | 0.91 | 1.06 |

Values are Table 5; Table 6 gives rule-specific rejection details. LLMSynthor is best in **five of six** category averages, not all six: NVI is better for mobility. The household-validity gain is substantial as reported, while a 13.3% household rejection rate still leaves meaningful error.

## 5. Reporting and reproducibility issues to preserve in our notes

These are bounded observations from the inspected materials, not an allegation about the authors’ work:

1. **Code release gap:** paper says available; public linked repository has no implementation.
2. **Baseline information contradiction:** general prose says every baseline uses microdata; Table 1 explicitly specifies macro-only comparators.
3. **Overbroad superiority language:** Table 5 mobility favors NVI. Table 1 also has classifier-gap columns where LLMSynthor is not the smallest, so “all metrics” is too strong.
4. **Repeated table numbers differ:** GPT-4.1-nano category TVD is 0.010 in Table 1 and 0.022 in Table 3. Rejection values for some methods also differ between Tables 1 and 4; distinct rule sets or runs could explain this, but the inspected description does not resolve it.
5. **Dependency-inference schedule:** Algorithm 1 infers groups before the loop; Appendix A describes three groups per iteration. Exact implementation cannot be resolved.
6. **Unknown target-statistic budget:** the adaptive sub-bin process can query additional reference frequencies. A fixed external-paper packet cannot supply arbitrary refinements. Counting only LLM tokens would miss this information resource.
7. **Incomplete independent-test specification:** e-commerce label/test definitions and ACS query-to-input overlap are insufficiently documented for our stronger holdout claim.
8. **Uncertainty:** reported run variability is primarily LLM stochasticity. It is not uncertainty from finite source-study samples, incompatible evidence, unidentified relationships or transport assumptions.
9. **Privacy:** aggregate-only operation is a useful privacy design choice, not an established differential privacy guarantee.

We should learn from the mechanism and the successful demonstrations while improving these specifications in our own work.

## 6. What transfers to our virtual-cohort problem

| Mechanism worth borrowing | Why it is useful | Required adaptation |
|---|---|---|
| Compact proposals rather than literal full tables | Scales generation while leaving substantive distribution choices to the Agent | Preserve observed target covariates; explicitly parameterize only missing measurements |
| Named, attributable statistical feedback | Tells the Agent what relation is mismatched and where | Compute each statistic under its original study’s population, units and adjustment set |
| Dependence-group selection | Helps focus limited context and evidence acquisition | Distinguish “plausible dependency” from “measured numerical constraint” |
| Separate semantic and statistical checks | Plausible individuals and valid population relationships are different goals | Include biomedical consistency without pretending this verifies unknown associations |
| Several task formats under one harness | Demonstrates breadth beyond one tuned association | Freeze common generation/revision logic across independent enrichment cases |
| Output-level scientific utility | Evaluates what synthetic data can support | Prespecify regression, interaction and nonlinear analyses excluded from feedback |

A useful ablation is not only “ordinary Agent vs many Agents.” It is whether the **same evidence and resource budget**, passed through these specific representations and feedback rules, yields more reliable downstream analyses.

## 7. Constructive next questions; not established novelty claims

### A. Can study-conditioned constraints outperform naive pooled targets?

Different papers estimate different quantities: an unadjusted correlation, an adjusted regression coefficient, a subgroup mean, or a biomarker after a measurement transformation. They should not be pooled as if they describe one common target histogram.

A concrete adaptation would retain a study-specific observation operator for each reported statistic. The Agent proposes a common conditional generator plus explicit population/measurement mappings. A deterministic executor evaluates each source constraint under its own settings and attributes conflicts back to those settings. This extends the type of evidence handled, rather than merely adding an Agent role. Similar statistical traditions exist; novelty must be checked against indirect inference, data fusion and transportability work.

A decisive test would compare identical source evidence under naive aggregate matching and study-conditioned matching, then evaluate a genuinely independent target with its biomarker hidden.

### B. Does generation remain useful when the strongest target statistics are unavailable?

Use a controlled information ladder:

1. All target marginals and relevant joint tables available.
2. Coarse aggregates only.
3. External compatible studies only.
4. External studies with population or measurement shift.
5. Target covariates visible, entire biomarker column absent.

This isolates whether a method’s advantage comes from an effective controller or access to nearly complete target information. LLMSynthor is a useful starting comparator for the upper-information levels; the lower levels need explicitly labeled adaptations. The purpose is explanation, not weakening a baseline to win.

### C. Can a frozen generator support multiple unprovided scientific analyses with honest uncertainty?

Several generators can satisfy the same source summaries yet disagree on age slopes, nonlinear BMI response or interaction. More synthetic rows reduce Monte Carlo noise but do not resolve that ambiguity.

An extension could retain several source-compatible candidate structures, report analyses that are stable across them, and label unsupported analyses instead of presenting one guessed answer as certain. Evaluating empirical coverage and the usefulness of that qualification is a scientific contribution candidate. Merely producing several random seeds is not an uncertainty method.

### D. Can revision preserve fixed observed participants?

For entire-column augmentation, corrections must operate on missing values while keeping observed covariates and IDs fixed. A proposal can describe a conditional missing-variable distribution or a group of allowed cell changes. Compare this to unrestricted append-only synthesis under exactly the same evidence. This makes the operation match the application, but must be demonstrated across cases before claiming a general algorithmic advance.

## 8. Bounded readiness assessment

**Ready now:** understand and implement a clearly labeled LLMSynthor-inspired proposal controller from the paper; prepare evidence schemas and an explicit information-budget protocol; reproduce simple toy aggregate-alignment behavior without claiming reproduction of published results.

**Not ready now:** claim source-code reproduction, reproduce the exact ACS/e-commerce tables, attribute all published gains to withheld relationship recovery, or run a fair same-information comparison without reconstructing and documenting the missing task details.

**Suggested next step after the combined near-neighbor review:** agree on one narrow first implementation—fixed-participant biomarker enrichment with explicit source-conditioned operators—and one controlled information-ladder test. Keep the existing closed biomedical targets closed. No new target download or generation is initiated by this note.

## Primary-source links

- [LLMSynthor arXiv v3 HTML](https://arxiv.org/html/2505.14752v3); [12-page PDF](https://arxiv.org/pdf/2505.14752v3); [DOI](https://doi.org/10.1145/3770855.3818965).
- [Official repository at the inspected commit](https://github.com/YihongT/LLMSynthor/tree/92e443f93c6edecc0fa9ca3045d4204da7d42aa5).
- [Official project page](https://yihongt.github.io/llmsynthor_web/).
- [LLMob official repository](https://github.com/Wangjw6/LLMob); [NeurIPS 2024 source paper](https://proceedings.neurips.cc/paper_files/paper/2024/file/e142fd2b70f10db2543c64bca1417de8-Paper-Conference.pdf).
- [US Census ACS PUMS](https://www.census.gov/programs-surveys/acs/microdata.html).
- [Original Open PFLOW repository](https://github.com/sekilab/OpenPFLOW); [original lab material](https://sekilab.iis.u-tokyo.ac.jp/wp-content/uploads/2018kashiyama_openpflow.pdf); [current Pseudo PFLOW provider page](https://pflow.csis.u-tokyo.ac.jp/data-provision-service/about-pseudo-people-flow-data/).

All comparisons to our project in Sections 6–8 are analytical proposals. They are not new empirical results, priority claims, or promises of publication.

