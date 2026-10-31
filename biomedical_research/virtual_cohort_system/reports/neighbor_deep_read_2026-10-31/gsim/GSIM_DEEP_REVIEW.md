# G-Sim deep review: methods, data, implementation, evidence, and extension choices

> Export note: this is an original reading/audit note. Downloaded papers and third-party implementation snapshots remain in the local research archive. Later scope decisions, including evidence-only full-cohort generation as a core intended capability, are recorded in the current paper-direction document.

Date: 2026-10-31. Scope: primary paper and appendices plus static inspection of the official repository. No experiment, package installation, API invocation, or independent numerical reproduction was performed. Full source files stay in this local work directory. This review does not modify or reopen any virtual-cohort target.

## Executive judgment

G-Sim is a useful direct predecessor for the **program-generating branch** of our system. It gives the LLM responsibility for the simulator's functional form and stochastic mechanism, while a statistical engine fits numerical parameters. The LLM really changes the data-generating program; it is not merely narrating a hand-fixed model. This division of labor is worth adopting.

Its experiments establish a more restricted claim than “literature can generate reliable biomedical cohorts.” They use **three hand-written, known-truth simulation environments** and train on their trajectories. The released structure-selection feedback also samples from the known ground-truth transition simulator. Our problem has published summaries, differing study populations and measurements, and an unmeasured target variable. That is a materially different information regime, although G-Sim already discusses heterogeneous and aggregate data as future directions.

The proper response is to reuse and extend the mechanism, specify the unavailable information, and test scientific analyses on independent real data. “Agent proposes, checks, and revises” alone is not our new contribution; neither does overlap make the project unpublishable.

## 1. Sources and certainty levels

- [Official ICML 2025 / PMLR entry](https://proceedings.mlr.press/v267/holt25b.html).
- [Published PDF, 49 pages](https://raw.githubusercontent.com/mlresearch/v267/main/assets/holt25b/holt25b.pdf). Page numbers below are PDF page numbers, matching printed page numbers.
- [Official repository, fixed commit](https://github.com/samholt/generative-simulations/tree/72b5d51a7790b8b2ebc87973ee5e9d21aa818ece).
- Commit: `72b5d51a7790b8b2ebc87973ee5e9d21aa818ece`, dated 2025-08-25, message “Initial Commit.” The retrieved tree has code and demonstration scripts, but no bundled run logs or numerical-result archive.
- Downloaded PDF SHA256: `77a62c51eff5fbfaf3f64cc16aa0de1b520dc038c834fa0df074baab623f770f`.
- `SOURCE_MANIFEST.json` records retrieved source hashes and snapshot scope.

Labels used here:
**P** = paper authors report; **C** = static observation of this released commit; **I** = our interpretation or proposed extension. C is not evidence that the same version produced the paper's tables. P is not independently reproduced.

## 2. What is actually generated and who decides it?

| Stage | Actual role | Locator and status |
|---|---|---|
| Environment specification | Human supplies task/state schema, contextual knowledge and a code skeleton | Paper §3.1, pp5–6; `utils/gesim_prompts.py:14–95,192–298` [P,C] |
| Structural proposal | LLM fills a NumPy `SimulatorStep` class: step logic, parameter definitions, bounds, state changes and sampling distributions | `agents.py:456–501`; `utils/llm_tools.py:53–96` [C] |
| Parameter calibration | Evolutionary optimizer or neural posterior inference fits parameters for a fixed proposed structure | Paper §3.2,p5; AppE.3,p32; `libs/SIR/env.py:148–258` [P,C] |
| Diagnostics | Validation Wasserstein plus state-dimension MSE and optimized parameters are prepared for the LLM | `agents.py:342–438` [C] |
| Reflection | Same LLM explains actionable structural changes; subsequent call emits revised code | `agents.py:575–624` [C] |
| Retention | Archive candidates, rank by validation Wasserstein, retain best; duplicate code can reuse cached evaluation | `agents.py:625–704` [C] |
| Final return | Return the test metrics stored for the validation-best candidate | `agents.py:736–743` [C] |

This is a single model performing proposal and reflection with deterministic tools. The inspected path does not contain a literature-search agent, study-extraction agent, external evidence ledger, or a multi-agent debate. No LLM fine-tuning is required. The default SBI route **does train a separate neural posterior estimator**; “no LLM training” does not mean no statistical/neural fitting anywhere.

The initial SIR prompt contains the domain label, state keys, time horizon, objective and skeleton. Its “Trajectory Snippet” field is empty in the released prompt (`utils/gesim_prompts.py:78–80`). Therefore “the LLM reads the raw training table” is not an accurate description of this path. Numerical data reach the optimizer; the LLM receives their diagnostic consequences. Feedback includes past code and parameter values, enabling structural changes such as different stochastic laws or nonlinear transition forms.

The code is loaded through Python `exec` in the host process (`utils/llm_tools.py:64–66`). A new implementation should preserve the flexible proposal interface while using an isolated execution boundary. This inspection did not execute that path.

## 3. Data: three simulated tasks, not clinical cohorts

| Task | State / dynamics | Released generation and split | Important qualification |
|---|---|---|---|
| COVID-labelled SIR | Susceptible, infected, recovered; binomial infection and recovery | `libs/SIR/env.py:62–85,275–303`: each split independently simulated; 60 transitions, 61 stored states per trajectory; default 100 trajectories each | A small synthetic epidemic model, not a COVID patient dataset |
| Supply chain | Inventory, backlog, time, shipment pipeline; stochastic demand and delivery delay | `libs/SUPPLY/env.py:315–341`: constant order action 4, initial inventory 15–50, 60 transitions; default 100 per split | Actual implemented example is single-stage, despite broader multistage beer-game motivation |
| Hospital beds | Day, ICU/ward occupancy and a list of patients with disease, bed, remaining stay, survival fields | `libs/HOSP/env.py:350–373`: 60 transitions, default 100 per split; numeric representation has seven aggregate fields (`326–348`) | Patient dictionaries are simulated internal state, not a public clinical cohort |

Paper evidence: §5,p7 and AppC,pp22–28 explicitly describe hand-designed simulators.

**Count trap:** `config/config.yaml` contains a trajectory sweep of 10,000, but the default MAIN_TABLE branch passes `run.samples=100` (`run.py:84–92`). That 10,000 setting is not the main-table sample count. Genetic Programming is overridden to **24 trajectories** (`run.py:164–174`). The methods therefore do not all use the same number of trajectories in the released main-run path.

**Seed trap:** the runner calls global seeding before each method, but simulation repeatedly constructs `np.random.default_rng()` without a seed. Global `np.random.seed` does not seed those new generators. The datasets are regenerated separately by each method, so identical dataset realizations are not guaranteed by the released code. Sources: `run.py:164–179`, `utils/exp_utils.py:9–22`, `libs/SIR/env.py:75,94,108–109`, `libs/HOSP/env.py:353`. This is a static reproducibility concern, not a numerical estimate of its impact.

Paper AppC SIR initialization offers S roughly 900–1000 and I roughly 1–20 as examples (p23); the released implementation uses S=50–100 and I=1–5. Report the exact configuration used in any reproduction rather than treating illustrative appendix values as immutable benchmark definitions.

## 4. Calibration, search budget, and uncertainty

### Evolutionary calibration

The fixed simulator's parameter vector is normalized to [-1,1] and mapped back through LLM-defined bounds. GeneticAlgorithm uses population 200, simulated binary crossover, tournament size 4, eta 8, and Gaussian mutation SD .03. The objective in the inspected SIR code is **full-trajectory MSE**, not conditional Wasserstein (`libs/SIR/env.py:87–98,148–168`). Validation Wasserstein subsequently selects among structures.

The appendix specifies 10 evolutionary generations and typically five refinement loops/patience three (pp32,35); the released config specifies 20 evolutionary generations, three total generations, patience 20. The actual code samples **one** proposed program per generation, even though configuration keys suggest larger groups (`agents.py:466,564–572`). In the ordinary success path that means one initial code call and two calls per revision: three code candidates plus two reflections at the released default. API retries can add calls.

Do not conflate the optimizer's 200 parameter candidates with 200 LLM-generated structures.

### SBI

Paper p32 describes 1,000 simulator draws for Neural Posterior Estimation, an LLM-defined box prior, flattened trajectories, and posterior-mean parameters for final evaluation. The released SIR code uses `train_states[0]` as the observation and also initializes synthetic SBI trajectories from that first training trajectory (`libs/SIR/env.py:192–206`); the other training trajectories do not enter that particular posterior observation. Defaults are 1,000 simulator draws and 10,000 posterior samples, with a timeout (`181–185`).

The learned posterior estimates parameter uncertainty **conditional on the proposed structure**. It does not automatically represent uncertainty over missing biological mechanisms, literature bias, cross-study transport, measurement mapping or competing structures. The authors themselves emphasize this limitation in §3.2.1,p5 and AppB.4,p21. They already propose model averaging and active disagreement-based queries as future directions; those phrases alone cannot establish our novelty.

The final evaluation uses a posterior mean rather than integrating many posterior draws into downstream scientific analyses (`libs/SIR/env.py:250–258`). This is an actionable distinction for virtual-cohort inference.

## 5. Exactly what the validation oracle knows

The released SIR diagnostic loops over each state in each split. For every state, it draws 200 next states from the candidate and **200 fresh next states from the hand-written true simulator**, then measures their distributions (`libs/SIR/env.py:100–113`). Supply uses 200; hospital uses 20 (`libs/SUPPLY/env.py:133–146`; `libs/HOSP/env.py:161–173`).

This is stronger information than one realized transition, and far stronger than a reported mean or regression coefficient from a publication. It applies to the validation score fed to the LLM as well as test scoring. A known-simulator oracle is useful for measuring controlled fidelity; it is unavailable in a real cohort where the missing biomarker and generating process are unknown.

Important distinctions:

- Training records calibrate parameters.
- Validation score selects and revises the simulator structure.
- Test states and true-simulator calls are evaluated **for each candidate**, and their scores are stored.
- The inspected LLM prompt and ranking code use validation diagnostics; I did **not** find test metrics inserted into the reflection prompt or used for ranking. Repeated test computation is a weaker isolation design, but is not by itself proof of answer leakage.
- Model code is executed in-process without a restrictive sandbox, so implementation isolation is weaker than statistical prompt isolation.
- No retrieved demonstration shows the same feedback mechanism operating purely from published aggregate evidence without the simulator oracle.

For our use case, replace the oracle with **source-study analysis operators and their reported uncertainty**, freeze candidates based on those allowed sources, and reveal independent target analyses only afterward. This is an extension proposal, not a demonstrated result.

## 6. Evaluation and published numbers

All numbers below are **author-reported**, visually checked against PDF tables, not reproduced. Main Table2,p7 reports mean and 95% CI across five seeds.

| Method | SIR Wasserstein | Supply Wasserstein | Hospital Wasserstein |
|---|---:|---:|---:|
| DyNODE | 65.1 ± 2.21 | 38.3 ± .40 | 231 ± .14 |
| SINDy | 23.9 ± .40 | 18.2 ± .24 | 199 ± .04 |
| RNN | 16.7 ± 1.61 | 9.71 ± 2.21 | 199 ± 2.49 |
| Transformer | 3.30 ± .15 | 2.29 ± .06 | 199 ± .25 |
| Genetic Program | 63.6 ± 7.64 | 30.7 ± 1.41 | 231 ± .04 |
| One-shot code, no calibration | 1.17 ± .71 | 2.63 ± 2.79 | 102 ± 1.01 |
| One-shot code, ES calibration | .469 ± .107 | 9.89 ± 15.3 | 103 ± 2.06 |
| G-Sim–SBI | .351 ± .094 | 1.22 ± 1.68 | 5.24 ± 2.70 |
| G-Sim–ES | .405 ± .060 | 1.55 ± 1.39 | 101 ± 17.4 |

What these numbers support: structural proposals plus feedback can work well on their controlled simulation tasks. What they do not establish: calibration always helps, every extra revision helps, all biomedical variables can be synthesized, or an arbitrary direct-generating agent cannot match the method.

The supply one-shot calibrated mean is worse than the uncalibrated mean and has a broad CI. Hospital gains are dominated by the SBI variant; the ES variant is close to the one-shot numbers. AppI.3 Table5,p47 holds the proposed SIR structure fixed and instead finds ES better than SBI:

| Fixed-structure comparison | ES | SBI |
|---|---:|---:|
| Time, seconds | 55.7 ± .399 | 63.9 ± 2.49 |
| Test MSE | 3.11 ± .0558 | 1.11e3 ± 491 |
| MMD | .0583 ± .0197 | .07 ± .0245 |
| Wasserstein | .814 ± .0346 | 1.29 ± .101 |

These are different experiments, so they are not a contradiction. They do rule out treating SBI as uniformly superior.

Other author-reported evidence:

- Structural graph scores, Table4,p47: SIR F1 95.5±4.09%, SHD1.5±1.35; supply F1 93.3±6%, SHD.333±.3; hospital F1 100%, SHD0. They concern known synthetic graphs, not causal identification from real observational cohort data.
- Intervention plots, pp8,46: lockdown changes and longer supply lead times. AppC.4,p28 states that corresponding code parameters are manually located and modified in both true and generated simulators. This tests meaningful editability under an assumed intervention mapping; it is not autonomous causal discovery of the intervention effect.
- Table3,p8: best-policy cost 29,274 in the true environment versus 32,703 in the generated environment; lockdown starts 10 vs15, extra beds2500 both. Published wording calls the task hospital bed scheduling, while released `insight_experiments/sir_insight.py:477–525` implements a bed-overflow cost on a SIR simulation. Reconcile the exact experiment before reproducing that table.
- Table6,p48: G-Sim–ES 2,314s and16 fitted simulator parameters, compared with Transformer95s/2,560,353 parameters. The small parameter count excludes the pretrained LLM and is not evidence of lower total compute. Calibration-only Table5 times and whole-pipeline Table6 times must not be mixed.
- Hardware, AppH,p45: i9-12900K,64GB RAM,RTX3090 24GB. No need to assume a cluster is necessary for a small mechanism reproduction.

No published analysis in this paper evaluates adjusted BMI/age associations, subgroup conclusions, nonlinear biomarker relationships or scientific inference from a completed real cohort.

## 7. Implementation audit: what to repair before borrowing the repository

These are release-level observations, not allegations about unseen experimental code.

| Issue | Exact source | Consequence / handling |
|---|---|---|
| Model/config version mismatch | Paperp33 O1; `config/config.yaml:6` o3 | Reproduction must state model snapshot and which settings recreate each table |
| Counts differ across methods | `run.py:84–92,169–170` | Cache one dataset per seed and enforce equal allowed records |
| New RNGs bypass global seed | SIRenv75,94,108–109; HOSPenv353 | Pass explicit generator/seed through all simulations |
| Default SBI calibrates even ZeroShot flag | `agents.py:761` sets optimize_params; SIRenv127–133 routes SBI; SBI181–258 never checks flag | Do not label default-SBI ZeroShot “uncalibrated”; select ES explicitly or implement real no-fit branch |
| Full target score computed inside every proposal | SIRenv174–179,253–258; `utils/llm_tools.py:91` | Separate frozen final evaluator; do not expose target files to proposal execution |
| Baseline state mismatch | `agents.py:1355–1378` combines numeric state with a random pipeline/patient list | Creates hybrid states not necessarily corresponding to any real trajectory; unify state representation |
| Distribution-evaluation mismatch | RNN `agents.py:1343–1345` first5% windows;1385–1403 repeats point prediction; G-Simenv100–113 samples full stochastic transition | Not a clean universal comparison between conditional generators; compare matched inputs and probabilistic outputs |
| Potential mutable-reference contamination | RNN `agents.py:1399–1403` calls true hospital step without deepcopy; G-SimHOSP171–172 uses deepcopy | Hospital step mutates state. Independently test evaluator state invariance before trusting its metric |
| “Shared one-step loss” is not literal in release | Paperp30; SIRenv87–98,115–117 rollout MSE; SBI192–206 first trajectory | Describe loss and information per branch, not a generic shared objective |
| Dependency/runtime gaps | `requirements.txt`, `setup/install.sh`; env imports evotorch/ray; SIRenv234–244 uses SIGALRM | Scripts do not form a pinned turnkey Windows reproduction; use explicit isolated environment if reproducing |
| Aggregation/log inconsistencies | `utils/results_utils.py:104–110` marker checked differs marker split; default `process_result_file.py:21` points to absent results file | Do not promise “run once reproduces published table”; choose correct parser and archive raw records |

The baseline fairness concerns are particularly important for interpreting very large hospital differences. They motivate a cleaner evaluation, not a claim that G-Sim's idea is invalid.

Aggregation that can be verified: `utils/results_utils.py:63–69` computes a Student-t CI half-width; `186–193` groups by environment and method. The main table writer in `run.py:158` uses another helper, `generate_main_results_table`; do not mistake the older MSE-only writer for the final Wasserstein table. Without the original logs, exact reported aggregates remain unverified.

## 8. What is worth borrowing

1. **Make the LLM choose functional structure.** Record the proposed variables, conditional factors, distribution family, nonlinear terms, measurement mappings and rationale. Let numerical tools calibrate only exposed parameters. This gives a clear, inspectable Agent contribution.
2. **Distinguish parameter failure from structure failure.** First test whether any parameters fit the current allowed evidence; ask for a structural revision when they cannot. Avoid repeatedly asking for “more realistic” rows without a diagnostic.
3. **Give localized diagnostics.** A global loss is insufficient; show which allowed source statistics conflict, with units, sample conditions and sampling uncertainty.
4. **Keep candidate history and select explicitly.** Revision is optional; retaining a good earlier candidate is valid. Report how often revision actually improves independent analyses.
5. **Demonstrate downstream use.** G-Sim's policy-editing experiments are important because they show what the simulator enables. Our parallel should be scientific analyses of the generated table, not only similarity scores.

## 9. Concrete extensions for our project, without claiming novelty yet

### A. Study-conditioned evidence calibration — first priority

**Question:** Can an Agent turn heterogeneous published summaries into a target-compatible generator without access to the target biomarker?

**Modification:** replace a universal discrepancy against observed trajectories with a per-study operator:
population eligibility → measurement/unit transform → original adjustment model → reported statistic.
The same generator is evaluated under each source study's conditions. Numerical calibration and Agent structural revision receive these source-only diagnostics.

**Needed evidence:** extraction/operator correctness; consistency with source statistics; independent target coefficient directions and useful effect ranges; held-out nonlinear/subgroup analyses; sensitivity to source removal and contradictory evidence. Include an unsophisticated pooled-summary treatment to test whether handling conditions actually matters.

**Why this is more than relabelling:** it changes what information is observable and how mismatches are interpreted. However G-Sim's AppG.1 already envisages fragmented/aggregate data. Novelty needs the concrete representation, reliable implementation and demonstrated scientific utility.

### B. Analysis-supported generation under incomplete identification — second priority

**Question:** When multiple generators fit the same evidence, which scientific conclusions are stable?

**Modification:** retain several source-compatible structures; propagate parameter, residual and structural uncertainty into multiple virtual datasets; report support per analysis rather than certify the entire table as true.

**Needed evidence:** known-ground-truth controlled tasks to test interval calibration, independent real-data analyses, unsupported-interaction negative controls, and whether more synthetic rows shrink only Monte Carlo error rather than erase evidence uncertainty.

**Near-neighbor boundary:** SBI parameter posteriors already exist here; model averaging is already proposed as future work. Our proposed gain is an operational bridge to downstream biomedical analyses under cross-study and identification uncertainty, requiring a broader literature check.

### C. Evidence acquisition driven by disagreement — conditional priority

**Question:** Can a limited new literature query resolve disagreement among plausible generators and improve unfed analyses?

**Modification:** frozen candidates nominate a missing conditional relation; retrieve external source evidence; re-run the same evidence operators; revise or retain candidates before target evaluation.

**Needed evidence:** fixed retrieval budget, provenance, same-query controls, independent target analyses, and no source/target overlap. A query that merely retrieves the benchmark answer cannot establish generalization.

**Boundary:** G-Sim already mentions active learning and query-by-disagreement (pp21,42). The executable source-query and transport protocol, and demonstrable utility, would have to carry any contribution.

These are choices, not a mandate to implement all three. A plus scientific-use evaluation is the most direct continuation of our stated problem; B may make negative/ambiguous findings scientifically useful; C should follow only when source discovery is genuinely the bottleneck.

## 10. Smallest useful next step after the joint prior-work review

Do not begin a large rerun simply because the paper has attractive plots. Freeze the current evidence and targets. Design one controlled evidence-only benchmark with heterogeneous study summaries and no simulator-oracle feedback. Reuse the proposal–calibration–revision decomposition, retain a direct-row-generation branch if it remains of interest, and assess the same unfed scientific analyses.

The first gate is not “beat G-Sim's synthetic Table2.” It is: **can the allowed evidence constrain useful downstream analyses, and does the proposed evidence handling preserve them when naive pooling does not?** Exact controls can be finalized after the LLMSynthor review; they should isolate the changed mechanism rather than predetermine a winner.

## 11. Compact claim ledger

| ID | Claim | Evidence | Confidence / limit |
|---|---|---|---|
| G01 | G-Sim generates program structure, not patient rows directly | PaperFig1/§3; agents456–624 | High, P+C |
| G02 | Main benchmarks are hand-designed simulations | Paperp7,AppC22–28; three env loaders | High, P+C |
| G03 | Released MAIN_TABLE uses100 trajectories/split exceptGP24 | config;run84–92,169–174;envloaders | High,C; not assumed exact published configuration |
| G04 | LLM receives valWasserstein and per-dimensionMSE | agents342–438 | High,C |
| G05 | ValWasserstein uses a ground-truth resampling oracle | SIRenv100–113 and174–176 | High,C; key information boundary |
| G06 | Test computed per candidate but not found in ranking/feedback | SIRenv174–179;agents379,457,681,738 | High for inspected path; no claim of full sandbox isolation |
| G07 | SBI conditions on first training trajectory and uses posterior mean | SIRenv192–206,250–258 | High,C |
| G08 | Structural uncertainty is not covered by conditional SBI posterior | Paperp5/AppB.4p21 | High,P; authors acknowledge |
| G09 | Large reported gains coexist with important baseline-evaluation concerns | Table2p7;agents1343–1408 | Numbers P; concerns C; causal effect of issues not measured |
| G10 | Program editability enables intervention demos, with manual mapping | PaperAppC.4p28;insightscripts | High,P+C; not clinical causal validation |
| G11 | Multi-source, aggregate, active queries and ensembles are already discussed | Paperpp21,42–43 | High,P; must not claim these concepts alone as new |
| G12 | A source-conditioned virtual-cohort extension remains testable | Derived from our problem and above boundaries | I; requires its own empirical proof and broader novelty check |

