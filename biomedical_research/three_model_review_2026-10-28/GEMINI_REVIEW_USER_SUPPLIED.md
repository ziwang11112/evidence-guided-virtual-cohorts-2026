**Scope and Inspection Boundary Statement:** The private GitHub repository (`[https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026)` and commit `51d19b6a8fab07f774d0bd6032a2bb9a379595d8`) is inaccessible outside your local environment. Consequently, this independent review is grounded exclusively in the two supplied documents—`REVIEW_BRIEF.txt` and the 13 sanitized source files reproduced in `IMPLEMENTATION_APPENDIX.txt` (`protocol.json`, `BUILDER_GUIDE.md`, `policies/ordinary.md`, `policies/gap_policy.md`, `loop_control.py`, `runs/ordinary_1/final/{generator.py, model_spec.json, decision.md}`, `runs/gap_2/final/{generator.py, model_spec.json, gaps.json, actions.json}`, and `custodian/evaluate.py`)—supplemented by live web verification of external literature as of October 28, 2026. Omitted repository files, raw participant tables, and unattached audit scripts were not inspected, and this review does not constitute an end-to-end executable code audit.

---

## 1. Central Research Question, Paper Type, and Positioning (Briefing §A)

### Verified Facts vs. Strategic Positioning

* **Verified Fact:** Your project evaluates whether an LLM Agent can retrieve heterogeneous published aggregate evidence and compile auditable, executable Python data generators for target populations across three regimes: (A) whole-cohort synthesis, (B) never-measured variable enrichment, and (C) missing-cell completion.


* **Verified Fact:** Across Stage 1 (scenario enumeration) and the October 28, 2026 NHANES HDL pilot, adding complex procedural machinery (`gap_policy.md` requiring `gaps.json` and `actions.json`, or mandatory multi-scenario branches in Stage 1) did not yield superior analytical recovery over the baseline `ordinary.md` workflow. In the HDL pilot, `Gap1` and `Gap2` produced zero numerical parameter revisions between `initial/` and `final/`, whereas `Ordinary1` autonomously retrieved a cross-sectional obesity-tail regression slope from an author-response table (`PMC7644056`) and updated its generator.


* **Interpretation:** Trying to publish a paper claiming that a "Consequential Evidence-Gap Loop" or "Multi-Scenario Agent" beats an ordinary Agent is empirically indefensible on your own record. Conversely, the **"ordinary capable Agent" operating under `BUILDER_GUIDE.md` and `loop_control.py` is already a distinct, structured methodology**: it compiles unstructured scientific prose and tables into SHA256-locked, provenance-typed parametric simulation programs (`model_spec.json` + `generator.py`) without access to target outcome microdata.



### Recommended Paper Type and Scope Restriction

This should be positioned strictly as a **Biomedical Research Methodology Paper** (specifically, *Automated Evidence Synthesis & Generative Cohort Enrichment*), not a biomedical discovery paper (no new clinical biology is discovered by recombining literature) and not a static benchmark/resource paper (since participant-level NHANES and clinical trial artifacts are restricted or already public).

Furthermore, **a defensible first paper must narrow its primary scope to Use Case B (Variable Enrichment: synthesizing an entirely unmeasured variable conditional on observed covariates $X$)**, while treating Use Case A (Whole-Cohort Synthesis) as a special case ($X = \emptyset$ or marginal demographic grid) and relegating Use Case C (Missing-Cell Completion) to supplementary discussion or dropping it entirely. In Use Case C, when a variable is partially observed in the target cohort, standard statistical imputation (`MICE–PMM`, random forest imputation) already has direct access to the target conditional distribution $p(Y \mid X_{\text{obs}})$ and performed competitively (17/18 vs. 18/18 in your retrospective replay). Use Case B is where target-trained statistical imputers and tabular generative models (`CTGAN`, `TabDDPM`, `MICE`) completely fail—because the target column has 100% missingness—giving an evidence-guided Agent its cleanest methodological raison d'être.

### Most Defensible Central Research Question

> *"To what extent can an autonomous, provenance-constrained LLM agent synthesize heterogeneous published aggregate statistics into executable conditional data generators to enrich unmeasured variables in target biomedical cohorts, and which classes of downstream multivariable analyses can—and cannot—be validly supported without target outcome calibration?"*

### What the Ordinary Agent Must Contribute Beyond a General Coding Assistant

A general coding assistant prompted with *"Write Python code to simulate HDL from BMI, age, and sex"* will hallucinate plausible-looking linear coefficients from pretraining memory without citing sources, conflate standard errors with standard deviations, ignore covariate centering, and emit uncalibrated noise. To be a publishable method, your "Ordinary Agent" is defined not by extra gap-ledger JSON files, but by the **Compiler & Verification Contract** enforced in `BUILDER_GUIDE.md` and `loop_control.py`:

1. **Screened Primary-Literature Grounding:** Every numerical parameter in `model_spec.json` must resolve via `validate_spec()` to a cryptographic hash in `literature/audit.jsonl` or an explicit typed bridge assumption (`A01`–`A08`).


2. **Explicit Estimand Translation:** Separating marginal category means, adjusted regression slopes, and standard errors (`SEM * sqrt(n)`) rather than pasting raw numbers into linear formulas.


3. **Distribution-Preserving Stochastic Synthesis:** Preserving observed covariate spines (`output_check()` in `loop_control.py`) while generating conditional draws for downstream statistical pipelines.



### Candidate Titles

1. **Recommended Title:** *Compiling Published Aggregate Evidence into Auditable Virtual Cohorts for Unmeasured Variable Enrichment*
2. **Alternative Title 2 (Explicitly Cautious/Methodological):** *Evidence-Guided Virtual Cohort Enrichment: Capabilities and Identifiability Limits of Agent-Authored Conditional Data Generators*
3. **Alternative Title 3 (Task-Focused):** *Synthesizing Unmeasured Biomedical Variables from Heterogeneous Literature via Provenance-Constrained Language Model Agents*

---

## 2. Critical Audit of Completed Results, Code Artifacts, and Reviewer Objections (Briefing §A, §C)

### What Completed Results Genuinely Establish (Verified Facts)

1. **End-to-End Cryptographic and Procedural Integrity:** Inspection of `loop_control.py` and `custodian/evaluate.py` confirms an exceptionally well-engineered blinding and provenance architecture. `validate_ledger()` and `validate_spec()` enforce complete bipartite linking between parameters and gateway-approved literature hashes (`gateway_registry()`) or declared assumptions. `source_check()` uses Python AST parsing to block file I/O, network calls, and global RNG mutation inside `generator.py`. `custodian/evaluate.py` (`validate_release()` and `taylor_fit()`) ensures that reference NHANES data and survey design spines (15 strata, 30 PSUs) are touched only after all 40 scheduled outputs are hash-committed.


2. **Directional and Primary-Effect Feasibility in Unmeasured-Column Enrichment:** Across both NHANES 2017–2018 fasting insulin ($N=1,700$) and NHANES 2013–2014 HDL ($N=4,885$), clean Agents deprived of target outcomes retrieved non-NHANES literature and authored conditional lognormal generators that recovered the primary adjusted exposure-outcome direction and approximate magnitude (Insulin adjusted GMR per 5 BMI units: generated median $1.230$ vs. reference $1.346$ $[1.304, 1.390]$; HDL adjusted BMI slope per $5\text{ kg/m}^2$: `Ordinary1` $-2.935$, `Ordinary2` $-3.008$, `Gap2` $-3.224$ vs. reference $-3.916$ $[-4.369, -3.464]$).


3. **Null Value of Mandatory Gap/Action Bookkeeping (`gap_policy.md`):** Requiring the Agent to populate `gaps.json` and `actions.json` produced thoughtful prose diagnostics (e.g., `Gap2` noting in `G_VARIANCE` that cell $\text{SE} \times \sqrt{n}$ overestimates conditional residual variance by retaining within-cell predictor variation), but resulted in **zero parameter updates** in both `Gap1` and `Gap2` (`generator_or_spec_changed: false`) and worse primary endpoint accuracy in `Gap1` ($-5.380$ vs. reference $-3.916$).



### What Remains Unresolved & Specific Flaws Found in Supplied Code

1. **Systematic Attenuation of Continuous Slopes via Piecewise Bin Interpolation (`ordinary_1/final/generator.py` & `gap_2/final/generator.py`):**
In both `ordinary_1` and `gap_2`, the builders anchored their conditional mean function on Table 2 of a Taiwan Biobank study (`PMC6627528`), which reports marginal HDL means across four coarse BMI categories (`<18.5`, `18.5–24`, `24–27`, `>=27`). Both generators apply `np.interp(bmi, bmi_knots, centered_means)` across assumed knot midpoints (`[17.0, 21.25, 25.5, 30.5]` in `ordinary_1`; `[17.5, 21.25, 25.5, 30.0]` in `gap_2`).


* *Mathematical Critique:* In Taiwan Biobank, the top category (`BMI >= 27`) pools everyone above 27 (primarily BMI 27–32). When applied to a US NHANES cohort where a large fraction of adults have BMI between 30 and 45+, anchoring BMI 30.5 to the Taiwanese `>=27` mean ($43.25\text{ mg/dL}$ in men) and decaying slowly (`-0.33 mg/dL` per BMI unit in `ordinary_1` line 45, or exponential decay rate `0.04` toward asymptotes `30.0`/`38.0` in `gap_2` lines 25–27) severely flattens the slope across BMI 25–35. Furthermore, linear interpolation between category averages without deconvolving within-bin variance creates artificial kinks at the knots, explaining why the reserved curvature contrast (`BMI slope at 35 minus at 25`: reference $3.156\text{ mg/dL}$) was missed by a wide margin (`0.303` to `1.879`).




2. **Severe Underestimation of the Age Effect due to Estimand Confounding (`ordinary_1` & `gap_2` `model_spec.json`):**
Reference NHANES adjusted age slope is $+1.201\text{ mg/dL}$ per 10 years $[0.843, 1.558]$, whereas `Ordinary1`, `Gap1`, and `Gap2` generated nearly flat age slopes ($0.077$, $0.159$, $0.079$). Why? Inspection of `ordinary_1/final/model_spec.json` (`age_contrasts: [0.0, 0.75841, 1.18484, 0.87361]` at knots `[35, 45, 55.5, 65.5]`) and `decision.md` (Review F2) reveals that the Agent extracted age contrasts from Taiwan Biobank Table 3, which **simultaneously adjusted for waist-to-hip ratio (WHR), body fat percentage, triglycerides, and lifestyle factors**, and then clamped age flat below 35 and above 65.5 (`np.interp` default clamping behavior in `ordinary_1/final/generator.py` line 29)! Because NHANES covers ages 20–79 (so ages 20–35 and 65.5–79 have a literally zero derivative under `np.interp`) and because adjusting for triglycerides/WHR blocks the mediating pathway between age and HDL, the resulting generator hard-coded a near-zero age slope for a model conditioning only on `(BMI, age, sex)`.


3. **Conflation of Aleatoric Monte Carlo Noise with Epistemic Uncertainty:**
In `protocol.json`, each builder is evaluated across 5 seeds (`[281001..281005]`). Inside `ordinary_1/final/generator.py` (lines 52–57) and `gap_2/final/generator.py` (lines 45–47), `model_spec.json` parameters `p` are treated as fixed constants across all 5 seeds; only `rng.standard_normal(len(result))` changes. Thus, across draws, the variance of any regression estimate scales as $\mathcal{O}(1/N_{\text{target}})$ ($N=4,885$), yielding tight synthetic confidence intervals in `custodian/evaluate.py` (`contrast()`) that reflect zero uncertainty about source sampling error, knot locations, or Taiwan-to-US transport.



### The Strongest Reviewer Objections

* **Objection 1 ("Garbage-In, Algebraic-Out / Circularity"):** *"You fed the Agent literature reporting that BMI is negatively associated with HDL and women have higher HDL, and the Agent wrote a 50-line lognormal script encoding those two facts. Wherever the Agent lacked direct matched estimands (age slope conditioned only on BMI/sex, curvature, sex-by-BMI interaction), it failed or guessed. Why generate synthetic patient rows at all instead of reading the published meta-analytic summary?"*
* **Objection 2 ("Pretraining Memorization of NHANES"):** *"NHANES 2013–2014 and 2017–2018 are among the most heavily analyzed public datasets in history. Even though `literature_gateway.py` blocked NHANES papers during retrieval, the frontier LLM's pretrained weights already encode exact NHANES BMI–HDL and BMI–insulin distributions."*
* **Objection 3 ("No Statistical Baselines in the Flagship Experiments"):** "Neither the NHANES insulin benchmark nor the NHANES HDL benchmark includes a single non-LLM statistical comparator (e.g., parametric moment transport, Constrained Maximum Likelihood, or human-curated formula transfer). You only compared an Agent against another Agent."



---

## 3. Closest Methods and Statistical Precedents (Verified Web Research) (Briefing §B)

Independent web verification conducted on October 28, 2026 confirms the publication status and technical scope of your listed leads and identifies essential statistical precedents that reviewers will cite:

| Work & Verified Status | Core Mechanism | Overlap with Your Project | Substantive / Empirical / Engineering Gap |
| --- | --- | --- | --- |
| **G-Sim** (Holt, Luyten, Berthon, & van der Schaar, *ICML 2025*, PMLR v267; [Direct Link](https://proceedings.mlr.press/v267/holt25b.html), [Code](https://github.com/samholt/generative-simulations)) | Hybrid loop where an LLM proposes executable simulator code/causal structure and calibrates numerical parameters via Gradient-Free Optimization (EvoTorch) or Simulation-Based Inference (SBI) against observed trajectory data $D$. | Both use LLMs to author executable Python simulators rather than directly emitting tokens. | **Substantive:** G-Sim assumes access to empirical target trajectories $D$ to fit parameters $\omega^*$. Your Use Case B has **zero target outcome observations** ($Y_{\text{target}} = \emptyset$) and must calibrate against external published aggregate statistics.

 |
| **SPADA** (Yang, Zhang, Prenkaj, & Kasneci, *EMNLP 2025*, pp. 10337–10358; [Direct Link](https://aclanthology.org/2025.emnlp-main.525/)) | Uses an LLM to induce a sparse feature dependency DAG, then fits Gaussian KDE or conditional normalizing flows on an observed tabular dataset $T$ to sample synthetic rows $9,500\times$ faster than autoregressive LLMs. | Sparse conditional graph structure + fast non-LLM numerical sampling. | **Substantive:** SPADA requires a complete training table $T$ to fit its KDE/flows; it cannot synthesize a wholly unmeasured variable from external literature text/tables. |
| **DALL-M** (*Computers in Biology and Medicine*, May 2025, Vol. 190, 110022, PMID: 40174497; [Direct Link](https://doi.org/10.1016/j.compbiomed.2025.110022), [arXiv](https://arxiv.org/abs/2407.08227)) | Three-phase clinical tabular augmentation using RAG + expert queries to infer unrecorded clinical features (e.g., symptoms/smoking from chest X-ray reports and demographics) row-by-row via LLM prompting. | Directly targets **Variable Enrichment (Use Case B)**—adding unmeasured clinical features using RAG and domain context. | **Substantive & Methodological:** DALL-M performs row-by-row LLM inference evaluated only on downstream ML classification accuracy (F1/Recall) on $N=799$ cases, without explicit parametric equations, estimand deconvolution, or epidemiological regression validity checks. |
| **SynthCraft** (Callender, Boyd, Davis, Estevez, Lavista Ferres, & van der Schaar, *PLOS Digital Health*, March 9, 2026, 5(3):e0001290, PMCID: PMC12970901; [Direct Link](https://doi.org/10.1371/journal.pdig.0001290)) | Verified published primary paper! An interactive LLM agent wrapper around `SynthCity` and Python that guides clinicians through dataset characterization, generator selection, and privacy/fidelity evaluation. | Agentic orchestration, provenance logging, and natural-language-to-Python synthetic data workflow. | **Substantive:** SynthCraft orchestrates standard target-trained generators (`SynthCity` plugins on an existing dataset); it does not extract quantitative parameters from primary literature or synthesize unmeasured columns. |
| **ModelSMC** (Wahl, Schenk, Farnoud, Macke, & Gedon, *ICML 2026*, Poster 66508 / arXiv:2602.18266; [Direct Link](https://icml.cc/virtual/2026/poster/66508), [GitHub](https://github.com/mackelab/ModelSMC)) | Verified accepted at **ICML 2026**! Probabilistic LLM-based scientific model discovery using Sequential Monte Carlo (SMC) where candidate mechanistic models are particles weighted by SBI posterior predictive checks. | Explicitly maintains a **distribution over plausible candidate models** rather than committing to one point-estimate script. | **Substantive Opportunity:** ModelSMC calibrates against observed experimental data via SBI (`npe_pfn`), whereas your setting calibrates against heterogeneous published summary statistics. However, ModelSMC's particle-ensemble perspective directly exposes the weakness of your single-scenario generators. |
| **ML-NMR** (Phillippo et al., *JRSS Series A*, 2020, 183(3):1189–1210; [Direct Link](https://pmc.ncbi.nlm.nih.gov/articles/PMC7362893/)) & **CML / GIM / GENMETA** (Chatterjee et al., *JASA* 2016; Kundu et al., 2019; [PMC11728056](https://pmc.ncbi.nlm.nih.gov/articles/PMC11728056/), 2024) | Statistical frameworks integrating Individual Participant Data (IPD) with external Aggregate Data (AgD) by integrating individual-level regression models over the covariate distribution of aggregate studies or applying empirical-likelihood score constraints. | **Exact Mathematical Precedent:** Solving the ecological-to-individual bridge when combining IPD ($X$ observed) with external AgD (published moments/slopes of $Y \mid X$). | **Substantive:** ML-NMR and CML/GIM require a human statistician to manually curate compatible summary statistics and specify link functions. Your genuine novelty is **automating the messy front-end translation** (literature retrieval $\rightarrow$ estimand alignment $\rightarrow$ observation operator $\rightarrow$ conditional generator) across incompatible reporting formats. |
| **SASC** (D'Amico et al., *Patterns* 2022, 3:100453; [ResearchGate](https://www.google.com/search?q=https://www.researchgate.net/publication/355535395)) & **NCHS Synthetic Linked Data** (CDC, updated Oct 8, 2026; [CDC Link](https://www.cdc.gov/nchs/linked-data/synthetic/index.html)) | SASC generates virtual cohorts from clinical trial summary tables via constrained random draws. NCHS provides synthetic linked mortality/claims files with a formal verification server comparing synthetic vs. restricted regression estimates. | SASC shares the summary-table-to-virtual-cohort goal; NCHS establishes the gold-standard **analytical verification protocol** (comparing regression coefficients and SEs across real vs. synthetic linked variables). | **Empirical:** SASC relies on manual table input and simple marginal/grouped draws without covariate adjustment transport; NCHS uses restricted IPD to build synthetic links, whereas your Agent uses public literature. |

**Where Your True Novelty Lies:** Do not claim novelty for "LLM writes Python simulator code" (*G-Sim* owns that), "LLM augments clinical features" (*DALL-M* owns that), or "Agent manages synthetic data pipelines" (*SynthCraft* owns that). Your defensible gap is **Zero-Target-Data Cross-Study Variable Enrichment via Automated Estimand & Observation-Operator Translation**: bridging the statistical rigor of aggregate-to-individual data integration (*ML-NMR / CML*) with autonomous literature extraction when target outcomes are completely unmeasured.

---

## 4. Highest-Value Method Improvements: Observation Operators & Uncertainty Propagation (Briefing §B, §C)

Do **not** add multi-agent debate swarms, custom neural loss functions, or heavier `gaps.json` schemas. Keep the single "Ordinary Agent" workflow (`BUILDER_GUIDE.md` + `loop_control.py`), and implement **two high-value mathematical modifications** to how the Agent constructs and executes `model_spec.json` and `generator.py`.

### Improvement 1: Executable Forward Observation-Operator Alignment (Solving Estimand & Variance Conflation)

Right now, in `ordinary_1` and `gap_2`, the Agent reads published summary statistics and plugs them directly into target generation formulas via algebraic heuristics (e.g., setting conditional residual SD equal to marginal bin $\text{SE} \times \sqrt{n}$, or adding a multi-covariate-adjusted age contrast onto unadjusted BMI bin means).

* **Mechanism:** Upgrade `artificial_checks.json` into a mandatory **Forward Source-Simulation Check (`source_operator_check.py`)** inside the ordinary Agent's single build-and-revise loop. For each numerical source $s$ used in `evidence.json`:


1. The Agent generates a synthetic *source* covariate sample $\tilde{X}_s$ matching the source study's reported marginal demographics (e.g., Taiwan Biobank age/sex/BMI bin counts in `ordinary_1/final/model_spec.json`).


2. The Agent applies its candidate `generate(X_s, spec, seed)` to produce $\tilde{Y}_s$.
3. The Agent runs the **exact statistical analysis reported in source $s$** (e.g., computing marginal bin means/SDs, or fitting the source's age/sex-adjusted regression) on $(\tilde{X}_s, \tilde{Y}_s)$ and checks whether the simulated outputs match the published numbers in `evidence.json` within reported standard errors.
4. **Variance Deconvolution Correction:** By the Law of Total Variance, within any broad BMI bin $B_j$,

$$\text{Var}(Y \mid X \in B_j) = \mathbb{E}[\text{Var}(Y \mid \text{BMI}, \text{age}, \text{sex}) \mid X \in B_j] + \text{Var}(\mathbb{E}[Y \mid \text{BMI}, \text{age}, \text{sex}] \mid X \in B_j)$$



When the Agent runs the forward operator on $\tilde{X}_s$, it will immediately see that plugging $\sigma_{\text{cell}} = \text{SE} \times \sqrt{n}$ into the pointwise conditional generator inflates total cell variance by $\text{Var}(\mathbb{E}[Y \mid X] \mid X \in B_j)$, and that clamping `np.interp` at age knots `[35, 65.5]` distorts the linear age slope. The Agent can then solve for the deconvolved conditional parameters before freezing `final/generator.py`.




* **Discriminating Test:** Compare `Ordinary-Base` vs. `Ordinary+OperatorCheck` on source-moment recovery error and held-out continuous slope/variance accuracy across 5 enrichment tasks.

### Improvement 2: Two-Stage Parameter-Prior Sampling + Rubin's Rules with $N_{\text{eff}}$ Capping (Solving Uncertainty & Artificial Precision)

Currently, `generate(observed, evidence, seed)` uses `seed` only to draw person-level residual noise $Z_i \sim \mathcal{N}(0,1)$ under a fixed parameter vector $\theta$. Consequently, pooling or taking medians across 5 draws ignores all epistemic uncertainty, and generating $N=4,885$ (or $N=100,000$) rows produces arbitrarily small standard errors.

* **Mechanism:**
1. **Parameter Distribution in `model_spec.json`:** Require every parameter in `model_spec.json` to specify a **prior distribution** $\theta \sim p(\theta \mid \text{Evidence})$ rather than a scalar float:
* For source-estimated parameters, use the reported sampling distribution: e.g., in `ordinary_1`, `tail_additive_slope` is reported as $-0.33$ (95% CI $-0.47$ to $-0.20$), so $\beta_{\text{tail}} \sim \mathcal{N}(-0.33, 0.069^2)$.


* For open-ended bin knots (e.g., underweight BMI knot `17.0` and obese knot `30.5` in `ordinary_1`), specify a uniform or truncated normal bridge distribution (e.g., $\kappa_4 \sim \text{Uniform}(29.0, 33.5)$).


* For cross-population transport (Assumption `A01` in `ordinary_1` / `A_TRANSPORT` in `gap_2`), include an explicit zero-mean random transport shift $\delta_{\text{loc}} \sim \mathcal{N}(0, \tau_{\text{loc}}^2)$ and slope multiplier $\delta_{\text{slope}} \sim \mathcal{N}(1, \tau_{\text{slope}}^2)$ (e.g., $\tau_{\text{slope}} = 0.15$ to reflect typical 15% between-cohort epidemiological heterogeneity when no target calibration data exist).




2. **Hierarchical Draw Execution in `generator.py`:** For draw $m \in \{1, \dots, M\}$ (increase $M$ from 5 to $M=20$ or $50$—which takes $<1$ second in NumPy):


* First sample one parameter vector $\theta^{(m)} \sim p(\theta \mid \text{Evidence})$ using `rng = np.random.default_rng(seed)`.
* Then sample individual outcomes $Y_i^{(m)} \sim p(Y \mid X_i, \theta^{(m)})$.


3. **Combining Inferences via Rubin's Multiple Imputation Rules & $N_{\text{eff}}$ Cap (`custodian/evaluate.py`):**
Instead of reporting only the median across draws, compute the pooled point estimate $\bar{\hat{\beta}} = \frac{1}{M}\sum_{m=1}^M \hat{\beta}^{(m)}$ and Rubin's total variance:



$$V_{\text{total}} = \bar{W} + \left(1 + \frac{1}{M}\right) B, \quad \text{where } \bar{W} = \frac{1}{M}\sum_{m=1}^M \widehat{\text{Var}}(\hat{\beta}^{(m)}), \quad B = \frac{1}{M-1}\sum_{m=1}^M (\hat{\beta}^{(m)} - \bar{\hat{\beta}})^2$$



Critically, because $\theta^{(m)}$ varies across draws $m$, the between-draw variance $B$ **does not shrink to zero as synthetic sample size $N_{\text{syn}} \to \infty$**! Furthermore, scale the within-draw variance $\bar{W}$ by $\max\left(1, \frac{N_{\text{target}}}{\min(N_{\text{target}}, N_{\text{source\_eff}})}\right)$ so a user cannot create fake statistical significance by synthesizing 1,000,000 virtual rows from a 500-person source study.


4. **Handling Unsupported Relationships without Vague Refusals:** In `model_spec.json`, require the Agent to classify each pair of variables/interactions into one of three machine-readable tiers: `DIRECTLY_IDENTIFIED` (source conditions on the same covariates), `BRIDGE_IDENTIFIED` (identified via explicit deconvolution/additivity assumptions), or `UNIDENTIFIED_STRUCTURAL` (e.g., `sex * BMI` slope interaction when only marginal sex and marginal BMI slopes are available, or unmeasured confounders). For `UNIDENTIFIED_STRUCTURAL` terms, the prior $p(\theta_{\text{int}})$ is centered at $0$ with a plausible weakly informative scale $\tau_{\text{int}}$, ensuring that downstream regression automatically yields a wide confidence interval straddling zero (preventing false discovery) rather than a falsely narrow spike at $0.000$.





---

## 5. Prioritized Experiment Matrix & Appropriate Baselines (Briefing §D, §E)

### Why Your Current Baselines Are Insufficient

In the insulin and HDL benchmarks, you ran **zero statistical baselines**. A reviewer will immediately ask whether a 10-line deterministic formula or standard statistical moment-matching achieves the exact same result. Conversely, as you rightly noted, target-trained `CTGAN`, `TabDDPM`, or standard `MICE` cannot run when the target variable is 100% absent.

### Appropriate Comparators Across Information Regimes

1. **Regime B (100% Unmeasured Variable Enrichment — Primary Focus):**
* **Baseline 1: Parametric Summary-Moment Transport (`Stat-Moment-Bridge`):** A fixed, non-agent statistical baseline that takes the primary source table's category means/SDs (or overall published regression slope/intercept + residual SD) and applies standard linear/lognormal moment-matching without LLM structural synthesis or multi-paper triangulation.
* **Baseline 2: Constrained Maximum Likelihood / Simulated Method of Moments (`Stat-CML/SMM`):** Using the published aggregate constraints from the same retrieved source ledger (`evidence.json`), fit a maximum-entropy / empirical-likelihood conditional model via numerical optimization (the statistical benchmark following Chatterjee et al. 2016 / indirect inference). This isolates whether the LLM's code generation is better or worse than formal statistical optimization on the same extracted evidence.


* **Baseline 3: Zero-Retrieval Pretraining Agent (`Agent-NoRAG`):** The exact same Ordinary Agent and `BUILDER_GUIDE.md` contract, but with `literature_gateway.py` disabled—forcing the Agent to specify `model_spec.json` and `generator.py` purely from pretrained biomedical knowledge. **This is a crucial ablation:** if `Agent-NoRAG` performs as well as `Ordinary-Agent` on NHANES, your retrieval pipeline is not driving performance (or pretraining leakage is dominating)!
* **Baseline 4: Direct Token/Row LLM Generator (`LLM-Direct-Rows`):** Prompting the LLM with the retrieved evidence summary to directly output CSV rows (or batch sampling) to prove the necessity of the executable Python generator route (`SPADA`/`G-Sim` style contrast).


* **Ancillary Utility Comparator: Direct-Analysis Agent (`Agent-NoGen-Meta`):** Give the Agent the target covariate summary table ($\bar{X}, \text{Cov}(X)$) and the retrieved literature, and ask it to directly predict the 8 target regression endpoints and 95% CIs *without generating a virtual cohort*.


* *When this is relevant:* For simple bivariate slopes, `Agent-NoGen-Meta` should tie the generative Agent. The generative Agent's unique value over `Agent-NoGen-Meta` must be shown on **complex downstream tasks** where analytic formulas fail: e.g., non-linear survey-weighted quantile regressions, clinical risk-threshold classification ($\text{HDL} < 40\text{ mg/dL}$), multi-variable composite indices (e.g., Triglyceride-to-HDL ratio or HOMA-IR combining observed glucose with enriched insulin), or privacy-preserving drop-in code prototyping.




2. **Regime C (Partially Observed / Missing-Cell Completion — Secondary/Optional):**
* Compare `MICE–PMM` (target-only), `Amelia/MissForest` (target-only), and `Hybrid Bayesian Prior + MICE` (using the Agent's literature-derived conditional distribution as an informative prior when target observed sample size is tiny, e.g., $n_{\text{obs}} \in \{15, 30, 50\}$). Note: when $n_{\text{obs}} > 200$, target-only `MICE` will almost always beat external literature because it avoids transport bias.



### Staged Experiment Matrix

| Priority & Stage | Exact Task & Public Dataset (Verifiable Access) | Input Information to Methods | Comparators Included | Held-Out Target Evaluation | Unit of Replication & Repeats | Success / Failure Criteria (Operational Proposals) | Est. Effort |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Stage 0: Two-Week Mechanism Pilot** | **Unmeasured Variable Enrichment** on already-prepared NHANES 2013–2014 HDL ($N=4,885$) & 2017–2018 Insulin ($N=1,700$) (*labeled strictly as development validation, not held-out discovery*).

 | Observed `(BMI, age, sex)` + screened PMC gateway (`max 12 queries/downloads`).

 | 1. `Ordinary-Fixed` (current)<br>

<br>2. `Ordinary+OpCheck+Rubin` ($M=30$ parameter draws)<br>

<br>3. `Agent-NoRAG` (pretraining ablation)<br>

<br>4. `Stat-SMM` (fitted on extracted `evidence.json`). | All 8 locked survey-weighted endpoints in `custodian/evaluate.py` + 95% CI coverage.

 | **Unit:** 2 cases $\times$ 3 independent Agent builds per arm ($M=30$ parameter draws per build). | **Go:** `OpCheck` fixes the age-slope attenuation ($>0.6\text{ mg/dL/10y}$ vs. $0.08$) and Rubin's 95% CI covers $\ge 6/8$ true target parameters (vs. $\le 2/8$ under fixed-parameter draws). **No-Go:** If `Agent-NoRAG` matches or beats `Ordinary` with RAG, retrieval is decorative. | **2 Weeks** (1 FTE, local CPU) |
| **Stage 1: Multi-Cohort Cross-Population Enrichment Benchmark (Core Paper Package)** | **Single- & Dual-Column Enrichment** across **4 distinct public cohorts** $\times$ **3 target biomarkers** = **12 independent tasks**.<br>

<br>*Cohorts:*<br>

<br>1. **KNHANES** (Korea, public download)<br>

<br>2. **CHARLS** (China Health & Retirement Study, public)<br>

<br>3. **CHNS** (China Health & Nutrition Survey, public)<br>

<br>4. **NHANES 2021–2023** (post-pandemic US cycle).<br>

<br>*Targets:* `HDL`, `Fasting Insulin` (for HOMA-IR with observed Glucose), `HbA1c` or `hs-CRP`. | Observed predictors `(Age, Sex, BMI, Waist, BP, Fasting Glucose)` + screened PMC literature excluding the target survey family (e.g., exclude all KNHANES papers when enriching KNHANES). | 1. `Ordinary+OpCheck+Rubin` (Main Method)<br>

<br>2. `Agent-NoRAG`<br>

<br>3. `Stat-Moment-Bridge` (single best paper)<br>

<br>4. `Stat-CML/SMM` (multi-paper moment optimizer)<br>

<br>5. `Agent-NoGen-Meta` (direct coefficient prediction). | 1. Primary adjusted slopes<br>

<br>2. Nonlinear spline/quantile contrasts<br>

<br>3. **Composite clinical index accuracy** (e.g., HOMA-IR = $\text{Glucose} \times \text{Insulin}/405$ association with hypertension/BP, where Glucose & BP are observed in target!)<br>

<br>4. Interval calibration (ECE / 95% coverage). | **Unit:** **12 cohort-variable tasks** (true independent units). 3 independent Agent builds per task; $M=30$ parameter draws per build. | **Success:**<br>

<br>1. Beat `Agent-NoRAG` and `Stat-Moment-Bridge` on MAE of standardized regression coefficients by $\ge 20\%$ across the 12 tasks.<br>

<br>2. 95% Rubin intervals achieve $80\%\text{--}95\%$ empirical coverage across identified endpoints.<br>

<br>3. Recover composite cross-variable associations (e.g., HOMA-IR $\leftrightarrow$ SBP) that `Agent-NoGen-Meta` cannot compute without microdata. | **3–4 Weeks** (Local CPU; ~$150 API budget) |
| **Stage 2: Pretraining-Proof Temporal / Regional Holdout** | **Strict Post-Cutoff / Unindexed Cohort Test:** Use 2 regional cohorts whose microdata or summary distributions are sparse or post-date LLM pretraining cutoffs (e.g., **2024–2025 KNHANES release** or a restricted/newly released **PhysioNet / Dryad / Zenodo clinical cohort from 2025–2026** where specific lab panels are masked). | Observed baseline covariates + controlled injection of 3–5 specific source papers into a local offline repository. | 1. `Ordinary+OpCheck+Rubin`<br>

<br>2. `Agent-NoRAG` (strictly blinded to injected papers). | Recovery of conditional associations and shift between pre- vs. post-retrieval generators. | **Unit:** 4 cohort-biomarker tasks $\times$ 3 builds. | **Success:** Clear, statistically significant improvement from `Agent-NoRAG` to `Ordinary+OpCheck+Rubin`, proving genuine evidence integration rather than weight memorization. | **2 Weeks** |
| **Stage 3: Low-Sample Hybrid Completion (Optional Secondary Scope)** | **Small-Sample Partial Observation (Regime C):** Subsample target observed biomarker to $n_{\text{obs}} \in \{10, 25, 50, 100, 500\}$ out of $N=4,000$ across 4 cohorts from Stage 1. | Observed $X$ for all $N$, observed $Y$ for $n_{\text{obs}}$, plus external literature. | 1. `MICE–PMM` (target-only)<br>

<br>2. `TabPFN / MissForest` (target-only)<br>

<br>3. `Evidence-Prior + MICE` (Shrinkage combination of Agent prior and target $n_{\text{obs}}$). | Downstream regression MSE and CI width as a function of $n_{\text{obs}}$. | **Unit:** 4 tasks $\times$ 5 sample sizes $\times$ 20 random subsamples. | **Success:** Demonstrate the exact crossover sample size $n^*$ (typically $n_{\text{obs}} \approx 30\text{--}80$) below which external evidence shrinkage outperforms pure target `MICE–PMM`. | **1.5 Weeks** |

---

## 6. Justifying a Methods Paper Beyond Reproducing Fed-In Relationships (Briefing §C, §F)

A methods paper will be desk-rejected if its only empirical finding is: *"The Agent read from Paper A that $\beta_{Y\mid X_1} = -0.35$, put $-0.35$ into Python, and when we regressed synthetic $Y$ on $X_1$, we got $-0.35$."* To justify a methods paper without circularity, your evaluation must separate analytical endpoints into three distinct epistemic tiers:

### Tier 1: Direct Evidence Consistency (Sanity Diagnostic Only)

* **Definition:** Recovering a marginal mean, SD, or univariate slope that was explicitly reported in a retrieved source paper.
* **Role in Paper:** Necessary verification check (proving the code compiler works), never claimed as a scientific result.



### Tier 2: Multi-Source Triangulation & Conditional Covariate Transport (The Core Methodological Value)

How can a synthetic variable $Y$ support a useful analysis that was **not** simply fed in? By combining **target-observed joint covariate structure $p_{\text{target}}(X_1, X_2, X_3, Z)$** with **partial conditional constraints from multiple non-overlapping studies**:

* **Concrete Mechanism (Marginal-to-Joint Conditioning & Composite Biomarkers):** Suppose the target cohort measures `BMI` ($X_1$), `Age` ($X_2$), `Sex` ($X_3$), `Fasting Glucose` ($G$), and `Systolic Blood Pressure` ($Z$), but **lacks `Fasting Insulin` ($Y$)**.
* Literature Source 1 gives $p(Y \mid X_1, X_2, X_3)$.
* Literature Source 2 gives the conditional correlation between `Fasting Glucose` ($G$) and `Fasting Insulin` ($Y$) within BMI strata: $p(Y \mid G, X_1)$.
* **Neither source measured Blood Pressure ($Z$) or computed the relationship between HOMA-IR ($\frac{G \times Y}{405}$) and Blood Pressure ($Z$) adjusted for age and waist circumference!**
* However, because the target cohort *actually observed* the joint distribution $(X_1, X_2, X_3, G, Z)$ on the same real individuals, enriching $Y$ conditional on $(X_1, X_2, X_3, G)$ allows the researcher to estimate the downstream association between **HOMA-IR and Blood Pressure ($Z$)** (assuming conditional independence $Y \perp Z \mid X_1, X_2, X_3, G$, or bounding it via sensitivity parameter $\rho_{YZ\mid X,G} \in [-0.2, 0.2]$).


* **Why This Beats Circularity:** Neither source paper contained the HOMA-IR $\leftrightarrow$ Blood Pressure coefficient, and a non-generative meta-analysis (`Agent-NoGen-Meta`) cannot easily compute nonlinear composite thresholds (e.g., prevalence of metabolic syndrome or $\text{HOMA-IR} > 2.5$ across target survey strata) without integrating over the empirical joint distribution of the target individuals' observed covariates!

### Preventing Pretraining Leakage, Circular Validation, and Artificial Precision

1. **Strict Target-Family & Alias Blacklisting + `Agent-NoRAG` Control:** Keep your SHA256-audited `literature_gateway.py` exclusion filter, expand it to block secondary meta-analyses that pool the target cohort (e.g., NCD-RisC or Global Burden of Disease papers that include NHANES), and always report the paired `Agent-NoRAG` baseline so reviewers can see the exact delta attributable to retrieved literature.


2. **Pre-Registered Frozen Evaluation (`custodian/evaluate.py`):** Retain your strongest software asset—the cryptographic commit-and-release gate in `loop_control.py` and `custodian/evaluate.py`—and highlight it prominently in the Methods section as a safeguard against post-hoc prompt tuning.


3. **Eliminating Artificial Sample-Size Precision:** Enforce the Rubin's Rules + $N_{\text{eff}}$ variance floor described in Section 4. Explicitly show in a dedicated figure that as synthetic sample size increases from $N=1,000$ to $N=100,000$, naive single-parameter pooling causes false-positive significance rates to explode toward 100%, whereas your parameter-ensemble generator (`Ordinary+OpCheck+Rubin`) asymptotes to a non-zero epistemic uncertainty floor governed by between-draw variance $B$.

---

## 7. Demonstrating Enrichment, Cross-Study Transfer, and Unsupported-Analysis Prediction Safely (Briefing §C, §F)

### 1. New-Variable Enrichment (Use Case B)

Frame variable enrichment strictly as **Distributional Multiple Imputation from External Priors**, never as "predicting individual patients' unmeasured lab values".

* **Required Diagnostic Metric:** Alongside regression slope recovery, report **Prediction Interval Coverage** and **Energy Distance / Wasserstein-1 Distance** on conditional quantiles ($q_{0.10}, q_{0.50}, q_{0.90}$) across covariate strata (`custodian/evaluate.py` already computes weighted quantiles `[0.1, 0.5, 0.9]`, which is a great foundation).


* **Explicit Non-Recovery Proof:** Show that while individual-level $R^2$ against hidden true HDL is modest ($R^2 \approx 0.12\text{--}0.18$, which is the biological ceiling of predicting HDL from BMI, age, and sex alone!), **stochastic conditional sampling recovers population regression slopes and threshold prevalences**, whereas deterministic conditional mean prediction ($\hat{Y}_i = \mathbb{E}[Y \mid X_i]$, which `BUILDER_GUIDE.md` rightly forbids) severely underestimates tail prevalence ($\text{HDL} < 40\text{ mg/dL}$) and distorts nonlinear regressions.



### 2. Cross-Study Transport (e.g., East Asian Source $\rightarrow$ US or European Target)

In your HDL pilot, both `ordinary_1` and `gap_2` transported Taiwan Biobank (`PMC6627528`) conditional means to US NHANES.

* **Why Raw Transport Shifted Slopes:** East Asian populations develop metabolic dyslipidemia at lower BMI thresholds (hence Taiwan Biobank uses $\text{BMI} \ge 27\text{ kg/m}^2$ as the obesity cutoff, whereas US cohorts use $\text{BMI} \ge 30\text{ kg/m}^2$).


* **How to Demonstrate Cross-Study Transfer Rigorously:**
* Contrast **Naive Direct Transport** (plugging Taiwan BMI knots `[17, 21.25, 25.5, 30.5]` directly into US BMI) against **Covariate-Standardized / Quantile-Aligned Transport** (where the Agent maps ethnic-specific WHO/IDF BMI percentiles or waist-to-height equivalents when bridging East Asian and Western cohorts, or incorporates a transport uncertainty prior $\tau_{\text{transport}}$).
* Because our proposed Stage 1 matrix includes both East Asian cohorts (**KNHANES, CHARLS, CHNS**) and Western cohorts (**NHANES**), you can run a clean $2 \times 2$ **Matched-Ancestry vs. Cross-Ancestry Transport Experiment**:
1. Enrich KNHANES using East Asian literature vs. Western literature.
2. Enrich NHANES using Western literature vs. East Asian literature.
Quantifying this transport penalty—and showing that your parameter-uncertainty ensemble widens its 95% intervals appropriately under cross-ancestry transport—turns a weakness of your HDL pilot into a headline methodological finding!





### 3. Useful Prediction vs. Epistemic Abstention on Unsupported Analyses

When an analyst runs a downstream regression on an enriched dataset—for example, testing `HDL ~ BMI * Sex` (effect modification) or `HDL ~ Education + Smoking` (where `Education` and `Smoking` were observed in the target cohort, but **not** conditioned on in the HDL generator)—what happens?

* **Mathematical Law of Omitted Conditioning Variables:** If the generator samples $Y \sim p(Y \mid \text{BMI}, \text{Age}, \text{Sex})$, then by construction $Y \perp \text{Smoking} \mid (\text{BMI}, \text{Age}, \text{Sex})$. Regressing synthetic $Y$ on `Smoking` adjusting for `BMI, Age, Sex` will **always yield a true synthetic slope of zero**, regardless of true biology!
* **How Your Method Should Handle This:**
1. **Automated Design-Matrix Audit (`audit_analysis_support()`):** Add a lightweight function to your evaluation/user toolkit that inspects the user's downstream regression formula against `model_spec.json`.
2. If the downstream formula includes a target covariate $W$ (like `Smoking`) that is absent from `model_spec.json`'s conditioning set, the tool raises a hard **`UNCONDITIONED_COVARIATE_BIAS` flag** (attenuation toward conditional null).
3. If the downstream formula tests a higher-order interaction (`BMI * Sex` or `BMI^2`) that is marked `UNIDENTIFIED_STRUCTURAL` in `model_spec.json`, the parameter-ensemble generator draws the interaction coefficient from its zero-centered prior $\theta_{\text{int}}^{(m)} \sim \mathcal{N}(0, \tau_{\text{int}}^2)$. Instead of falsely reporting $\hat{\beta}_{\text{int}} = -0.044 \pm 0.05$ ("interaction ruled out!"), Rubin's pooled interval reports $\hat{\beta}_{\text{int}} = -0.04 \pm 1.15$ ("evidence insufficient to resolve interaction; consistent with reference $[-1.342, 0.586]$").





---

## 8. Public-Data-Only Route vs. Optional Wet-Lab / Prospective-Measurement Route (Briefing §D, §G)

**Clarification:** A computational methodology paper in biomedical informatics or biostatistics **does not require wet-lab experiments** to be publishable. However, separating what a purely public-data route establishes from what a small, targeted wet-lab/biobank measurement add-on would establish clarifies your strategic options.

### Route A: 100% Public-Data Route (Recommended Default — Zero Wet-Lab Dependency)

* **Data Sources:** NHANES (US, multiple cycles), KNHANES (Korea), CHARLS (China), CHNS (China), plus longitudinal clinical cohorts from PhysioNet/Dryad/NIDDK repository.
* **What It Validates:**
1. Accuracy of conditional slope, quantile, and composite-index recovery across 12+ cohort-variable pairs against gold-standard lab assays ($N=1,500\text{--}5,000$ per cohort).
2. Cross-ancestry vs. matched-ancestry transportability and uncertainty calibration.
3. Sample-size crossover curves in hybrid missing-data completion (Regime C).


* **Ceiling:** Sufficient for top field journals (*JAMIA*, *Journal of Biomedical Informatics*, *PLOS Digital Health*, *Statistics in Medicine*, *Briefings in Bioinformatics*) and potentially *NPJ Digital Medicine* or *Nature Computational Science* if the methodological theory and multi-cohort benchmark are exceptionally rigorous.

### Route B: Optional Targeted Biobank / Wet-Lab Add-On (Only If Local Collaboration Is Low-Friction)

Do **not** recruit a new clinical cohort from scratch. If a collaborator at your institution has an existing banked cohort (e.g., $N=150\text{--}250$ frozen serum/plasma samples from a metabolic, cardiovascular, or geriatric study where standard demographics, BMI, and routine lipids/glucose are already recorded in a database, but a secondary biomarker like **fasting insulin, adiponectin, ApoB, or hs-CRP** has not yet been assayed):

* **The Prospective "Virtual-Before-Assay" Protocol:**
1. **Step 1 (Pre-Assay Freeze):** Given only the cohort's observed baseline table ($N \approx 200$), run your Agent (`Ordinary+OpCheck+Rubin`) to synthesize the unmeasured biomarker, pre-registering the predicted conditional associations, power calculation for detecting a subgroup difference, and SHA256 freeze manifest.
2. **Step 2 (Targeted Wet-Lab ELISA / Clinical Chemistry Assay):** Run a standard commercial ELISA or clinical analyzer panel on the 150–250 banked aliquots (typical reagent cost: ~$1,500–$3,000 for 2–3 plates; 1 week of bench time).
3. **Step 3 (Prospective Unblinding & Two-Phase Design Validation):** Compare the pre-registered virtual cohort predictions against the newly measured wet-lab values, AND demonstrate **Two-Phase Stratified Assay Selection**: show that using the Agent's virtual cohort to select the most informative $n=50$ samples to assay (two-phase sampling design) achieves the same regression precision as randomly assaying $n=150$ samples!


* **What Route B Actually Validates That Public Data Cannot:**
1. **Absolute Proof Against Pretraining Leakage:** It is physically impossible for any LLM to have memorized measurements that were sitting unassayed in a $-80^\circ\text{C}$ freezer until November 2026.
2. **Tangible Cost/Sample-Efficiency Utility:** Showing that evidence-guided virtual enrichment guides two-phase wet-lab assay selection (reducing ELISA assay counts by 40%–60% for a target confidence interval width) provides a concrete, non-fabricated recruitment/measurement savings demonstration.





---

## 9. Realistic Venue Tiers, Publication Requirements, and Story Structure (Briefing §F, §G)

### Venue Tiers and Exact Conditions for Each

| Tier & Target Venues | Realistic Fit & Expectations | What Must Be True in Your Results to Justify Submission |
| --- | --- | --- |
| **Tier 1 (Ambitious Interdisciplinary / High-Impact Computational):**<br>

<br>*Nature Communications*, *Nature Computational Science*, *Science Advances*, *NPJ Digital Medicine* | High bar for both methodological generality and real-world biomedical utility. Reviewers will reject a paper that looks like "prompt engineering on 2 NHANES columns." | 1. **Scale:** $\ge 12\text{--}15$ diverse cohort-variable tasks across $\ge 4$ independent cohorts/populations.<br>

<br>2. **Methodological Depth:** Formalized Forward Observation-Operator Deconvolution + Rubin Parameter-Ensemble Uncertainty (`Ordinary+OpCheck+Rubin`) that provably beats `Agent-NoRAG`, `Stat-Moment-Bridge`, and `Stat-CML/SMM`.<br>

<br>3. **Killer Utility Demonstration:** Either the **Prospective Banked-Sample Two-Phase Assay Experiment** (Route B) OR a compelling **Two-Phase Subsampling / Clinical Trial Covariate Augmentation Study** on public multi-center trials showing tangible variance reduction or study-planning accuracy. |
| **Tier 2 (Premier Field Journals — Recommended Primary Target for Public-Data Route):**<br>

<br>*Journal of the American Medical Informatics Association (JAMIA)*, *Journal of Biomedical Informatics (JBI)*, *PLOS Digital Health*, *Briefings in Bioinformatics* | Ideal home for rigorous LLM-for-biomedicine methods, provenance architectures, and synthetic data validation (note: *PLOS Digital Health* just published *SynthCraft* in March 2026). | 1. **Scale:** 8–12 public-data tasks across 3–4 cohorts (Stage 1 + Stage 2 matrix).<br>

<br>2. **Rigorous Baselines:** Clear comparison against `Agent-NoRAG`, `Stat-Moment-Bridge`, `LLM-Direct-Rows`, and `MICE–PMM` (in partial-data regime).<br>

<br>3. **Honest Identifiability Boundaries:** Strong emphasis on your SHA256 audit architecture (`loop_control.py`), variance deconvolution, and preventing false discovery on unsupported interactions.

 |
| **Tier 3 (Specialized Statistical / Medical Computing Journals):**<br>

<br>*Computer Methods and Programs in Biomedicine (CMPB)*, *BMC Medical Research Methodology*, *Statistics in Medicine* | Focuses heavily on software reproducibility (`CMPB`) or formal statistical properties of aggregate-to-individual synthesis (`Stat Med`). | 1. Complete open-source release of the gateway, controller, and benchmark scripts.<br>

<br>2. Simulation study with known ground-truth data-generating mechanisms alongside 4–6 real NHANES/KNHANES empirical cases. |

### Logical Narrative Arc & Proposed Main Figures (6-Figure Blueprint)

* **Figure 1: Problem Formulation & Compiler Architecture.** Contrast traditional target-trained synthesis (`CTGAN`/`MICE`, which fail when target column $Y$ is 100% unmeasured) with **Evidence-Guided Virtual Cohort Enrichment**. Diagram the four locked stages: (1) Screened Literature Gateway (`audit.jsonl`), (2) Typed Evidence & Estimand Ledger (`evidence.json`), (3) Forward Observation-Operator Check & Parameter-Prior Specification (`model_spec.json`), and (4) Hierarchical Parameter-Ensemble Sampling (`generator.py` $\rightarrow$ Rubin's Rules evaluation).


* **Figure 2: Mechanism Validation — How Forward Observation Operators & Variance Deconvolution Fix Estimand Bias.** Use your HDL and Insulin development cases to show *why* naive literature plugging fails (attenuated age slopes from over-adjusted source tables; inflated conditional variance from $\text{SE} \times \sqrt{n}$; artificial kinks from coarse bin interpolation) and how the Forward Operator Check + Deconvolution quantitatively corrects them.


* **Figure 3: Multi-Cohort Variable Enrichment Benchmark (12 Tasks across 4 Populations).** Forest plots and standardized MAE comparisons across NHANES, KNHANES, CHARLS, and CHNS comparing `Ordinary+OpCheck+Rubin` against `Agent-NoRAG`, `Stat-Moment-Bridge`, `Stat-CML/SMM`, and `LLM-Direct-Rows`.
* **Figure 4: Downstream Analytical Utility Beyond Fed-In Relationships.** Show (A) recovery of nonlinear clinical threshold prevalences ($\text{HDL} < 40$, $\text{HOMA-IR} > 2.5$), (B) composite biomarker associations with third variables observed only in the target cohort (e.g., enriched HOMA-IR vs. observed blood pressure), and (C) the sample-size crossover curve ($n_{\text{obs}} = 0 \to 500$) where Evidence-Prior + MICE outperforms target-only `MICE–PMM`.
* **Figure 5: Uncertainty Calibration, Sample-Size Scaling, and Epistemic Abstention.** (A) Empirical coverage of 95% intervals (showing fixed-parameter draws fail at $<30\%$ coverage while parameter-ensemble Rubin draws achieve $\sim 85\%\text{--}90\%$). (B) False-positive rate vs. synthetic sample size $N_{\text{syn}} \in [10^3, 10^6]$ demonstrating the $N_{\text{eff}}$ variance floor. (C) Automated detection of `UNCONDITIONED_COVARIATE_BIAS` and `UNIDENTIFIED_STRUCTURAL` interactions.
* **Figure 6 (Conditional on Route A vs. Route B):** Either **Cross-Ancestry Transportability Matrix** (East Asian $\leftrightarrow$ US source-target swap quantifying transport shift and prior widening) OR **Prospective Two-Phase Biobank Assay Validation** (showing reagent/sample savings when using virtual cohorts to guide wet-lab subsampling).

---

## 10. Concrete Two-Week First Milestone, Go/No-Go Criteria, and Ranked Action Plan (Briefing §H)

### Ranked "Keep / Remove / Redesign / Test" Recommendations

#### 1. KEEP (High-Value Assets Already Working)

* **Keep the Cryptographic Controller & Blinded Evaluator (`loop_control.py` and `custodian/evaluate.py`):** Your AST static checker (`source_check()`), bipartite parameter-to-evidence validator (`validate_spec()`), gateway hash registry (`gateway_registry()`), and full-spine Taylor linearization evaluator (`taylor_fit()`) are publication-grade engineering.


* **Keep the Executable Python Generator Route (`ordinary.md`):** Having the Agent author inspectable, deterministic-seed NumPy/SciPy code parameterized by `model_spec.json` is vastly superior in transparency, speed, and auditability to row-by-row LLM token generation.


* **Keep Negative & No-Op Reporting:** Your commitment in `protocol.json` to retaining no-ops and negative results is scientifically admirable and will build strong reviewer trust.



#### 2. REMOVE (Stop Doing Immediately — Tradeoff: Saves Token Budget & Prevents Reviewer Distraction)

* **Stop Running `gap_policy.md` (`gaps.json` and `actions.json`) as a Competing Treatment Arm:** In `IMPLEMENTATION_APPENDIX.txt`, `gap_2/final/gaps.json` and `actions.json` consumed 22 action blocks and extensive token overhead only to freeze the exact same initial parameters (`generator_or_spec_changed: false`). Fold the single useful concept from `gap_policy.md`—tagging each parameter/analysis as `DIRECTLY_IDENTIFIED`, `BRIDGE_IDENTIFIED`, or `UNIDENTIFIED_STRUCTURAL`—directly into `model_spec.json` of the single Ordinary Agent workflow.


* **Stop Claiming or Testing Uncalibrated Multi-Scenario Enumeration (Stage 1 `stage1/RESULTS.md`):** Offering a user 3 uncalibrated scenarios without probability weights leaves the downstream analyst paralyzed and produced false positives in your Stage 1 pilot. Replace discrete scenario branches with a continuous parameter prior $p(\theta \mid \text{Evidence})$ sampled across $M=30$ draws.


* **Stop Treating `initial` vs. `final` Self-Revision as a Primary Research Question:** A two-turn build-and-check loop is good software hygiene, not a scientific thesis. Do not dedicate main-text tables to initial-vs-final diffs.


* **Stop Blocking PDF Supplements in `literature_gateway.py`:** Both `REVIEW_BRIEF.txt` and `gap_2/final/actions.json` (`G_SHAPE`: *"Mexican exact sex/class table is unsupported PDF"*; *"UK/Malawi numerical slope: unsupported PDF supplement"*) show that your builders repeatedly hit a wall because `literature_gateway.py` rejects PDF supplements. Adding `pypdf`/`pdfplumber` or `pymupdf` table extraction to `literature_gateway.py` is a 1-day engineering fix that removes an artificial handicap.



#### 3. REDESIGN (High-Leverage Method Upgrades)

* **Redesign `model_spec.json` and `generator.py` to Sample Parameter Priors $\theta^{(m)}$ Across Draws:** Stop holding `parameters` fixed across seeds. Sample $\theta^{(m)} \sim p(\theta \mid \text{Evidence}, \text{TransportPrior})$ once per seed $m \in \{1, \dots, 30\}$ before drawing individual residuals, and pool endpoint estimates in `custodian/evaluate.py` using Rubin's Multiple Imputation rules with an $N_{\text{eff}}$ cap.


* **Redesign `artificial_checks.json` into an Automated Forward Source-Operator Check:** Before freezing `generator.py`, require the Agent to simulate synthetic cohorts matching its cited source studies' marginal demographics, apply the source studies' exact statistical models/binnings, and verify that (a) conditional residual variance plus between-cell mean variance equals reported marginal cell variance, and (b) covariate adjustment matches the target conditioning set.



#### 4. TEST (The Single Highest-Information-Value Experiment Right Now)

The single highest-information-value experiment you can run in the next 14 days is **the 4-Arm Ablation on your existing NHANES HDL and Insulin cases (`Ordinary-Fixed` vs. `Ordinary+OpCheck+Rubin` vs. `Agent-NoRAG` vs. `Stat-SMM`)**.

* *Why this comes first:* Before spending 3–4 weeks curating 12 new tasks across KNHANES and CHARLS, you must know (1) whether `Ordinary-Agent` actually beats `Agent-NoRAG` (proving literature retrieval adds value over LLM weight memorization) and `Stat-SMM` (proving agentic synthesis adds value over basic moment matching), and (2) whether Forward Operator Deconvolution + Rubin Parameter Sampling fixes the age-slope attenuation ($0.077 \to \sim 1.0$) and 95% CI under-coverage observed in your October 28 pilot.



---

### Concrete Two-Week First Milestone & Go/No-Go Criteria (Oct 29 – Nov 11, 2026)

* **Days 1–3 (Engineering & Gateway Upgrade):**
1. Add PDF supplement table parsing (`pdfplumber` / `pymupdf`) to `tools/literature_gateway.py` (preserving the pre-display NHANES alias screen).


2. Update `custodian/evaluate.py` to compute **Rubin's Rules pooled point estimates, total variance $V_{\text{total}} = \bar{W}_{\text{capped}} + (1 + M^{-1})B$, and empirical 95% CI coverage** across $M=30$ draws.




* **Days 4–7 (Method Upgrade — Operator Check & Parameter Priors):**
1. Update `BUILDER_GUIDE.md` and `loop_control.py` (`validate_spec()`) so each parameter in `model_spec.json` specifies `{mean, sd/interval, distribution, identification_tier}` instead of a point constant, and `generator.py` samples $\theta^{(m)}$ once per seed $m$.


2. Require `run_source_operator_checks.py` during the build phase to verify variance deconvolution ($\sigma_{\text{residual}}^2 = \sigma_{\text{cell}}^2 - \sigma_{\text{between-predictor}}^2$) and continuous knot derivatives across the full target age/BMI range (`[20, 79]` years, `[15, 50]` BMI).




* **Days 8–12 (Execute the 4-Arm Discriminating Pilot):**
Run 3 independent builds ($M=30$ draws each) on NHANES 2013–2014 HDL and NHANES 2017–2018 Insulin across four arms:
1. `Agent-NoRAG` (Gateway disabled; pure pretraining prior).
2. `Stat-Moment-Bridge` (Standard parametric lognormal fit to the primary retrieved table without LLM adjustments).
3. `Ordinary-Fixed` (Your Oct 28 baseline).


4. `Ordinary+OpCheck+Rubin` (Upgraded single-agent method).


* **Days 13–14 (Go/No-Go Evaluation Gate):**
* **GO Criterion 1 (Retrieval Value):** `Ordinary+OpCheck+Rubin` achieves $\ge 25\%$ lower standardized MAE across the 8 locked endpoints than `Agent-NoRAG`. *(If `Agent-NoRAG` ties or beats RAG on NHANES, NHANES is contaminated by pretraining memorization and you must immediately pivot your benchmark to post-cutoff / non-US cohorts or perturbed synthetic ground-truth worlds).*
* **GO Criterion 2 (Operator Mechanism):** In HDL, `Ordinary+OpCheck+Rubin` recovers a positive adjusted age slope $\ge 0.65\text{ mg/dL/10y}$ (fixing the $0.077$ clamping/estimand bug) and improves curvature recovery (`BMI 35 vs 25` contrast $\ge 2.0\text{ mg/dL}$).


* **GO Criterion 3 (Uncertainty Calibration):** Across the 16 combined endpoints (8 HDL + 8 Insulin), Rubin's 95% intervals cover at least **12/16 (75%)** of the true NHANES reference parameters without spanning trivially useless widths (e.g., primary slope CI width $< 2.5\times$ the source standard error).



### Summary of Strongest Objection and What Would Change My Mind

My strongest objection to the project in its current October 28 state is that **sampling random normal residuals around a fixed, hand-interpolated literature lookup table creates an illusion of individual-level data without adding statistical information beyond the input summary table—and actively misleads downstream users when conditional variance, adjustment sets, and epistemic parameter uncertainty are conflated**.

**What would change my mind—and turn this into a strong, highly citable methods paper:** Demonstrating across $\ge 10$ multi-cohort enrichment tasks that (1) **Forward Observation-Operator Checks** enable an Agent to accurately deconvolve incompatible published summaries into a coherent conditional model $p(Y \mid X_1, X_2, X_3)$ that beats naive moment-matching, (2) combining that enriched variable with **other variables already observed in the target cohort** (such as computing HOMA-IR or adjusting for target comorbidities) recovers downstream multivariable relationships that cannot be read off any single published paper, and (3) **Parameter-Ensemble Sampling + Rubin's Rules** produces honest, well-calibrated uncertainty intervals that automatically widen when transport or structural identification is weak.