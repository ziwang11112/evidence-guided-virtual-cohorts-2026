# G-Sim implementation audit for a KDD nearest-method comparison

Date: 2026-11-05. Status: design and static verification only. No experiment, new cohort, package installation, paid model call, repository clone, or full-source download was performed. The primary paper and code snapshots already held locally were inspected; the official paper landing page and current GitHub metadata were rechecked online.

## Recommendation

G-Sim is a close methodological predecessor and a serious comparator for **LLM-authored generative programs with numerical calibration and structural revision**. It is not merely a parameter optimizer, and excluding it as “not an Agent” or as intrinsically unable to use aggregates would be wrong.

For the current v0.15 paper, use **G-Sim–ES adapted to supplied summaries** as a secondary matched-information mechanistic comparison, with the existing CHNS Q2 request as the smallest clean starting point. It can generate every requested variable without receiving individual records. Label it an adaptation, not an official-code reproduction. Its purpose is to test program search/calibration given the same numerical evidence; successful summary reconstruction would not establish external-literature transfer.

An external-evidence G-Sim comparison is also possible, but is not ready merely by running the released repository. It requires a declared observation/summary adapter and decisions about source populations, measurement mappings, adjustment sets, nuisance distributions and unreported dependence. If those study-specific operators are supplied by our workflow, the honest label is **G-Sim–ES + shared study-qualified evidence operators**. This remains a G-Sim-based method at the generator-search layer, while no longer being an independent test of the upstream evidence qualification/translation contribution.

This is an implementation and estimand boundary, not a reason to avoid a strong baseline. If the final paper's main technical claim becomes the generator-search loop itself, adapted G-Sim should be a main comparator. If the main claim remains end-to-end construction from heterogeneous published biomedical findings, the native release is less direct than a literature/macro-to-record method; G-Sim should still be included in the closest-method discussion and a clearly scoped control.

## 1. Audited sources and version

The official [PMLR entry](https://proceedings.mlr.press/v267/holt25b.html) identifies the ICML 2025 paper, PMLR 267:23513–23561, and links directly to the [author repository](https://github.com/samholt/generative-simulations). The 49-page published PDF and text were reused from `work/neighbor_deep_read_2026-10-31/gsim/`; the earlier manifest records PDF SHA256 `77a62c51eff5fbfaf3f64cc16aa0de1b520dc038c834fa0df074baab623f770f`.

Live metadata on 2026-11-05 confirms:

| Item | Observed state |
|---|---|
| Default inspected branch | `master` |
| Branch head | `72b5d51a7790b8b2ebc87973ee5e9d21aa818ece` |
| Commit message | `Initial Commit`; no parent commits in the returned record |
| Author timestamp | 2025-08-25T21:41:57Z |
| Committer timestamp | 2025-09-30T12:38:05Z; distinguish this from author date |
| Releases | Empty collection |
| Tag refs | Empty collection |
| License | MIT, copyright 2025 Samuel Holt |

Metadata sources: [branch head](https://api.github.com/repos/samholt/generative-simulations/branches/master), [releases](https://api.github.com/repos/samholt/generative-simulations/releases), [tag refs](https://api.github.com/repos/samholt/generative-simulations/git/matching-refs/tags/), [license at the audited commit](https://github.com/samholt/generative-simulations/blob/72b5d51a7790b8b2ebc87973ee5e9d21aa818ece/LICENSE). The ordinary tags endpoint was unsupported by the connector; the permitted Git tag-ref endpoint was queried successfully. The branch head is unchanged from the 2026-10-31 review, so the pinned local source snapshots remain relevant. This is a source release, not a versioned package or independently reproduced experiment archive.

Local context read: `manuscript/DRAFT_v0_15.md` §§2–4 and relevant Q2/Q5 supplementary descriptions; `docs/GSIM_LLMSYNTHOR_DEEP_REVIEW_2026-10-31.md`; `work/neighbor_deep_read_2026-10-31/gsim/GSIM_DEEP_REVIEW.md`; Q2 `PROTOCOL.md`; Q5 `PROTOCOL.json`; Q1 CHNS `AUTHOR_COMMON.md` and `source_operations.json`.

Throughout: **published** denotes an author-reported result; **release** denotes a static code observation; **design** denotes our proposed adaptation. No numerical claim below is independently reproduced.

## 2. Actual algorithm and responsibility split

The method separates a discrete/functional simulator structure from its numerical parameters. Domain knowledge and an environment specification guide the LLM's structural proposal. A numerical routine fits the exposed parameters for that fixed program. Diagnostics and candidate history then guide LLM reflection and a new program. Validation performance selects the retained candidate. Paper §§3.1–3.3 and Appendix E describe this outer loop; the released implementation makes it concrete:

| Stage | Released behavior | Pinned source |
|---|---|---|
| Proposal | LLM fills a `SimulatorStep` skeleton, including stochastic transition code and parameter/bound interfaces | [`agents.py:456–501`](https://github.com/samholt/generative-simulations/blob/72b5d51a7790b8b2ebc87973ee5e9d21aa818ece/agents.py#L456-L501); [`utils/gesim_prompts.py`](https://github.com/samholt/generative-simulations/blob/72b5d51a7790b8b2ebc87973ee5e9d21aa818ece/utils/gesim_prompts.py) |
| Execution | Generated Python is loaded and sent to the environment evaluator | [`utils/llm_tools.py:53–96`](https://github.com/samholt/generative-simulations/blob/72b5d51a7790b8b2ebc87973ee5e9d21aa818ece/utils/llm_tools.py#L53-L96) |
| Numerical fit | ES/GFO or neural SBI calibrates parameters within the proposed bounds | [`libs/SIR/env.py:148–258`](https://github.com/samholt/generative-simulations/blob/72b5d51a7790b8b2ebc87973ee5e9d21aa818ece/libs/SIR/env.py#L148-L258) |
| Reflection | Validation Wasserstein, per-dimension errors, fitted parameters and prior programs feed reflection | [`agents.py:342–438`](https://github.com/samholt/generative-simulations/blob/72b5d51a7790b8b2ebc87973ee5e9d21aa818ece/agents.py#L342-L438) |
| Structural revision | The model is expressly asked to regenerate code; the interface is fixed but its internal functional form can change | [`agents.py:575–624`](https://github.com/samholt/generative-simulations/blob/72b5d51a7790b8b2ebc87973ee5e9d21aa818ece/agents.py#L575-L624) |
| Retention | Candidate archive is ranked by validation Wasserstein; identical code may reuse stored results | [`agents.py:625–743`](https://github.com/samholt/generative-simulations/blob/72b5d51a7790b8b2ebc87973ee5e9d21aa818ece/agents.py#L625-L743) |

The LLM can change dependencies, nonlinear forms and stochastic mechanisms; the optimizer cannot invent a missing structural term unless a candidate program exposes it. Consequently a control that freezes G-Sim's structure to our chosen copula and permits only parameter fitting is **not** the full G-Sim comparator. It can be a separately labelled fixed-structure calibration ablation.

The inspected path uses one LLM for proposal/reflection plus tools, not a necessary multi-agent architecture. It does not fine-tune the LLM. SBI trains a separate neural posterior estimator. The released SIR initial prompt's trajectory-snippet field is empty: empirical information need not be inserted as raw records into the LLM prompt, although numerical fitting still receives observations.

## 3. What empirical information is required?

### Published framework versus released benchmark

Paper §2.3 already allows partially overlapping observations, asynchronous logging and missing variables, together with textual/symbolic knowledge. Appendix G.1 explicitly discusses heterogeneous sources and aggregate-level constraints. Therefore “G-Sim requires a complete joint individual table in principle” is too strong. Its calibration machinery can be defined against suitable summaries.

The implemented demonstrations are SIR, supply-chain and hospital-bed **hand-written simulation environments**, not individual biomedical cohorts reconstructed from independent publications. The ordinary main-table release loads 100 trajectories per train/validation/test split, each with 60 transitions. The GP baseline is overridden to 24 trajectories. See [`run.py:84–92,164–179`](https://github.com/samholt/generative-simulations/blob/72b5d51a7790b8b2ebc87973ee5e9d21aa818ece/run.py#L84-L92) and the environment loaders; the config's separate 10,000-trajectory sweep is not this default main-table count.

In SIR, ES minimizes rollout MSE against observed training trajectories, starting the candidate at each observed initial state. SBI conditions on the flattened **first training trajectory**, draws candidate trajectories from that initial condition, learns a parameter posterior, and returns the posterior mean. These are specific released choices, not requirements that every summary adaptation must preserve literally. [`SIR trajectory objective:87–98`](https://github.com/samholt/generative-simulations/blob/72b5d51a7790b8b2ebc87973ee5e9d21aa818ece/libs/SIR/env.py#L87-L98); [`SBI:181–258`](https://github.com/samholt/generative-simulations/blob/72b5d51a7790b8b2ebc87973ee5e9d21aa818ece/libs/SIR/env.py#L181-L258).

The strongest information difference is structural validation. At **each observed state**, SIR draws 200 next states from the proposed simulator and 200 from the known true simulator to calculate distributional discrepancies. Supply also uses 200; hospital uses 20. This oracle operates during validation and therefore drives structural revision, not merely a final external score. [`SIR:100–113`](https://github.com/samholt/generative-simulations/blob/72b5d51a7790b8b2ebc87973ee5e9d21aa818ece/libs/SIR/env.py#L100-L113); [`SUPPLY:133–146`](https://github.com/samholt/generative-simulations/blob/72b5d51a7790b8b2ebc87973ee5e9d21aa818ece/libs/SUPPLY/env.py#L133-L146); [`HOSP:161–173`](https://github.com/samholt/generative-simulations/blob/72b5d51a7790b8b2ebc87973ee5e9d21aa818ece/libs/HOSP/env.py#L161-L173).

The release computes test metrics for each candidate but the inspected prompts/ranking use validation scores. This is not evidence of test-answer leakage. A new comparison should nevertheless withhold the final target evaluator entirely until candidates close, rather than inherit this less isolated execution layout.

### Minimum inputs for a literature-only adaptation

GFO can fit a fixed structure if it receives (1) a permitted numerical summary vector, (2) a function that computes the same summaries on candidate-generated data, (3) fixed units/scales and discrepancy rules, and (4) parameter bounds and valid sampling. No target individual records are mathematically necessary. For literature from one harmonized population, this is a modest environment/observation adapter.

Cross-study evidence adds substantive requirements: source eligibility and population distributions, measurement transformations, estimator definition/adjustment set, and assumptions for unreported covariate joint distributions. Merely matching a source adjusted slope to a target marginal slope is not a valid adapter. Conversely, missing details do not automatically forbid all use: a declared equal-weight source scenario or analytic relationship may be defensible, with its assumptions and limits retained. Both methods must receive the same convention and evidence.

For SBI, replacing flattened trajectories by summaries additionally requires a generative observation model for those summaries: source sample sizes/designs, sampling uncertainty and dependence between reported statistics, or explicit approximations. An unweighted vector of heterogeneous point estimates does not by itself specify a calibrated posterior. ES is the cleaner first comparator when these observation-process details are absent. SBI posteriors condition on the proposed structure and do not automatically cover source bias, transport or missing biological relationships.

## 4. Calibration and implementation cost

“GP” should be disambiguated. In this repository it means **Genetic Programming**, a separate symbolic baseline. G-Sim's numerical fit is called GFO/ES and uses EvoTorch's `GeneticAlgorithm`; the audited implementation does not use a Gaussian-process calibrator.

| Component | Paper/release settings | Consequence for a fair budget |
|---|---|---|
| ES/GFO | Paper Appendix E.3: population 200, 10 generations; release: population 200, 20 generations | Thousands of parameter-objective evaluations per structural candidate; do not call these LLM proposals |
| Variation | Simulated binary crossover, tournament 4, eta 8; Gaussian mutation SD 0.03 | Optimizes bounded parameters; structure remains fixed during this inner loop |
| SBI | 1,000 simulations per candidate; release default 10,000 posterior samples and 60-second posterior-sampling timeout | Includes neural estimator fitting and posterior sampling; timeout is not an end-to-end runtime cap |
| Outer structure loop | Paper typically five refinement loops; release three total generations, one code proposal per generation | Ordinary success path: three code candidates and two reflection calls; retries can add calls |
| Default final evaluation | Train/validation/test distributional resampling per candidate | Significant extra simulator/oracle cost, separate from calibration |

Sources: paper Appendix E.3/E.5; [`config/config.yaml`](https://github.com/samholt/generative-simulations/blob/72b5d51a7790b8b2ebc87973ee5e9d21aa818ece/config/config.yaml); [`SIR ES/SBI`](https://github.com/samholt/generative-simulations/blob/72b5d51a7790b8b2ebc87973ee5e9d21aa818ece/libs/SIR/env.py#L148-L258); [`agents.py:466,564–624`](https://github.com/samholt/generative-simulations/blob/72b5d51a7790b8b2ebc87973ee5e9d21aa818ece/agents.py#L456-L624).

As an order-of-magnitude illustration, 200 × 20 parameter evaluations × 100 trajectories × 60 steps is about 24 million candidate transition calls per ES structural fit, before final diagnostics; actual optimizer reevaluation accounting can differ. The released SIR distributional diagnostics alone nominally request 3 splits × 100 trajectories × 61 states × 200 samples × 2 simulators = 7.32 million next-state calls per candidate. Neither number is a benchmark runtime estimate for our vectorized cohort laws.

Published Table 5 reports 55.7 ± 0.399 seconds for ES and 63.9 ± 2.49 for SBI on a **fixed SIR structure**. Table 6 separately reports 2,314 seconds for the full G-Sim–ES pipeline and 134 seconds for Genetic Programming. These cannot be combined as equivalent end-to-end budgets. Paper Appendix H reports an i9-12900K, 64 GB RAM and RTX3090 24 GB; this does not demonstrate that every small adaptation needs that GPU. No applicable current API-dollar total was verified, and current model prices were not queried because no run is proposed here.

## 5. Release/runtime readiness

The release is useful source code, but not a turnkey reproduction of the paper or a ready Windows package.

| Item | Static finding and action for a future adaptation |
|---|---|
| Python/runtime | [`setup/install.sh`](https://github.com/samholt/generative-simulations/blob/72b5d51a7790b8b2ebc87973ee5e9d21aa818ece/setup/install.sh) creates Python 3.10 Conda environment, installs PyTorch/Hydra and uses Linux `apt-get`; pin an isolated Linux/WSL environment if reused |
| Dependencies | [`requirements.txt`](https://github.com/samholt/generative-simulations/blob/72b5d51a7790b8b2ebc87973ee5e9d21aa818ece/requirements.txt) pins `openai==1.59.6`, `gym==0.23.1`; most packages including `sbi` are unpinned. SIR imports `evotorch` and `ray`, not explicitly installed by these lists; dependency resolution needs checking |
| LLM | Paper p.33 says O1; release selects `o3` and Azure API. [`llm_utils.py:16–30`](https://github.com/samholt/generative-simulations/blob/72b5d51a7790b8b2ebc87973ee5e9d21aa818ece/llm_utils.py#L16-L30) contains placeholder endpoint/key and deployment metadata, not proof of a working current model snapshot. Use the same observable backbone/service across compared methods, report the departure from published settings |
| API path | Main runner uses `llm_utils.py`; do not mistake standalone `llm_api.py`'s GPT-4o example for the main experiment model. The synchronous path calls `openai.chat.completions.create` at lines 319–364; no live credential/API test was done |
| SBI timeout | SIR uses `signal.SIGALRM` at lines 234–244, unsuitable as-is for native Windows; implement equivalent bounded execution or use Linux |
| No-calibration control | ZeroShot sets `optimize_params=False` at `agents.py:761`; SIR SBI branch does not check this flag. For a true uncalibrated control, select the ES branch or implement and verify a genuine no-fit route |
| RNG | Fresh unseeded `default_rng()` calls in SIR mean global seeding does not fully fix trajectories. Pass explicit RNGs/cache common observations; do not inherit unequal realized inputs |
| Execution | `utils/llm_tools.py` executes generated code in-process. Reuse our isolated generator executor, with no target/reference file access |

These are static integration requirements, not measured explanations for published performance. Baseline-state and distribution-evaluation concerns documented in the earlier deep review reinforce using one common evaluator; reproducing unrelated neural/GP baseline paths is unnecessary for the proposed G-Sim control.

## 6. When does an adaptation remain G-Sim?

| Change | Defensible description | What comparison it supports |
|---|---|---|
| Cohort sampling interface replaces SIR transition schema; LLM still proposes structure, optimizer fits parameters, reflection revises and archive selects | G-Sim cohort adaptation | Transfer of its program-search mechanism to complete scientific data |
| Replace trajectory loss/oracle by the same supplied target-summary discrepancy available to every method | G-Sim–ES, summary-adapted | Matched-summary reconstruction; no individual construction records |
| Give every method fixed reviewed source-population/measurement/analysis operators | G-Sim–ES + shared study-qualified operators | Downstream law construction/search conditional on an already qualified evidence interface |
| Ask G-Sim's LLM to interpret the same raw source packets and author its own operators, while preserving its original search/calibration loop | End-to-end G-Sim-based literature adaptation | Potentially fair overall workflow comparison, but a substantial new adapter/prompt contract that must be audited and reported |
| Add our evidence agent, source qualification, operator validator and transport/assumption policy only to G-Sim | Hybrid/ablation of our workflow with G-Sim search | Component replacement, not independent original G-Sim reproduction |
| Freeze our law and permit G-Sim only to fit its coefficients, or remove its refinement to meet two trial-table slots | Fixed-structure or one-shot ablation | Does not represent full G-Sim's structural contribution |

A statistic-specific discrepancy is natural to the broad G-Sim framework; the paper already anticipates aggregate calibration. The new scientific machinery lies in how heterogeneous findings are interpreted and made comparable. Calling every adapter an entirely new algorithm would overstate novelty; calling a full source-reconciliation system “unmodified G-Sim” would hide material work. Report inherited components, shared harness functions and new scientific decisions separately.

## 7. Smallest fair comparison using existing requests

This is a proposed **new unit**, not authorization to reopen closed budgets or run anything now.

1. **Start with Q2's CHNS summary condition.** Reuse the existing whole-cohort request, schema, population/measurement definitions, analysis definitions and 30 supplied developmental summaries (three adjusted coefficients plus 27 distribution/joint diagnostics). Supply exactly the same permitted evidence to G-Sim and the current workflow; no individual inputs, previous generators or hidden target values. Every requested variable must be sampled. The existing [Q2 protocol](../information_revision_ablation_2026-11-03/PROTOCOL.md) already distinguishes this from the literature-only condition.
2. **Make the observation adapter common and small.** A cohort generator exposes parameters/bounds and samples rows. The common evaluator computes the supplied summaries. Predeclare fit scales/weights using permitted information or fixed domain units; never use unfed target errors to tune them. Preserve native-unit scientific results rather than advertise one optimizer loss as overall scientific utility.
3. **Retain G-Sim's essential loop.** Permit its own program structure, numerical calibration, localized summary diagnostics, reflection and best-candidate retention. ES first avoids adding a poorly specified summary-likelihood/SBI claim. Pin either the paper ES budget or release ES budget and state which; a reduced budget is explicitly a reduced-budget adaptation.
4. **Budget the actual work.** The earlier two/four row-producing trial slots are incompatible with thousands of internal calibration simulations. Do not squeeze G-Sim into those slots and call it faithful. A new budget must count all parameter-objective calls, synthetic rows, candidate programs, LLM/reflection calls, retries, wall time and model cost. Match backbone and information; grant the same optimizer/execution cap to relevant controls, or report an explicit cost–quality comparison. Calibration-only calculations do not become free merely because a program performs them internally.
5. **Use replicated constructors and frozen outputs.** A minimum developmental comparison can mirror Q2's three independent constructor contexts per method, each delivering three fixed 3,000-row final samples. The constructor is the unit of replication; seeds/rows are not independent author replications. Show all constructors and failures. Separate initial/calibrated/revised versions where the budget allows, without selecting a winning author after seeing reference outcomes.
6. **Interpret fit and validation correctly.** If all 30 summaries are supplied, agreement on them measures reconstruction. Recomputing the same summaries on fresh simulated seeds evaluates Monte Carlo stability, not withheld empirical generalization. Use separate source/summary holdouts only when predefined and equally applied; do not retroactively relabel supplied statistics as independent utility endpoints. Existing references are exposed development references.

For an external-evidence extension, reuse Q1's CHNS/ENSANUT E0/E1 packets or Q5's glycemia/lipid requests. Provide the same full packets, qualification opportunity and declared assumptions to all methods. Keep a separate table of which numerical source constraints are computable, which are scenario-dependent, and which remain contextual. Target means/covariates/biomarkers must remain absent from construction.

This extension has a concrete readiness gate. Q1 CHNS `source_operations.json` currently says `execution_enabled: false` and distinguishes qualified equal-weight mathematical scenarios from certified original-study replay. Q5 reports all 132 source-check entries unavailable under its semantic rules. These facts do not mean no useful literature evidence exists; numerical derivations were used. They do mean those existing runs do **not** already provide an operational numeric calibration oracle for G-Sim. Resolve a common source operator/subset, or clearly design a new agent-authored operator interface, before claiming an external-evidence optimized G-Sim comparison. If no numeric source discrepancy is usable, report an uncalibrated program-generation control rather than silently call it calibrated G-Sim.

## 8. Claims to retain and avoid

Retain: G-Sim is a close agentic program-generation predecessor; structure and parameters are genuinely separate; its generic framework accommodates partial/aggregate observations; its released evidence is primarily known-simulator trajectory calibration; a no-individual-input cohort adaptation is feasible in principle and scientifically worthwhile.

Avoid: “G-Sim cannot use literature,” “it is not an Agent,” “it only tunes hand-fixed equations,” “SBI proves full uncertainty coverage,” “the public repository reproduces the paper out of the box,” or “our agent beats G-Sim” when the compared methods receive different information, calibration budgets or source-interpretation machinery.

The current evidence supports selecting and specifying this comparator, not predicting who will win. No new result has been generated in this audit.
