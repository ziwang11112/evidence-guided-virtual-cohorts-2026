# Independent data and evaluation audit: G-Sim and LLMSynthor

> Export note: this is an original reading/audit note. Downloaded papers and third-party implementation snapshots remain in the local research archive. Later scope decisions, including evidence-only full-cohort generation as a core intended capability, are recorded in the current paper-direction document.

Audit date: 2026-10-31. Scope: primary papers, pinned public implementation snapshots, and official data-access metadata. No external implementation was run; no individual-level dataset was downloaded or inspected. This is a reproducibility and interpretation audit, not a reproduction of published results.

## 1. Main conclusions

Both papers are serious relevant precedents. G-Sim already separates LLM structure search from numerical calibration and uses validation feedback. LLMSynthor already turns macro-statistics into micro-records, combines source datasets, and measures downstream utility. Those components cannot be claimed as absent from prior work.

Their evaluation settings are nevertheless distinct from generating an entirely unmeasured biomedical column using heterogeneous external study results. G-Sim's main benchmark has a known simulator that can be queried for distributional comparison. LLMSynthor's experimental target macro-statistics are extracted from the ground-truth microdata (Appendix A). Neither fact invalidates the respective experiment; both must be made explicit before adapting the methods to our information setting.

The public releases have different readiness: G-Sim has inspectable source and simulators, with important execution/configuration caveats; LLMSynthor's linked repository currently lacks implementation files. Open underlying sources do not by themselves make the exact published processed datasets reproducible.

## 2. Claim and information matrix

| Setting | Actual reference data | Generator/selection can access | Evaluation shown | Unresolved boundary |
|---|---|---|---|---|
| G-Sim SIR, supply, hospital | Trajectories from hand-designed stochastic simulators, not observed hospital patients or epidemic records | Text description; training trajectories for parameter estimation; validation metrics for structural search. Released Wasserstein/MMD evaluator also queries the known ground-truth simulator | Distributional next-state error, trajectory MSE, five-seed intervals, ablations and stress tests | Separate finite-observation information from oracle simulator information when porting; release defaults differ from paper settings |
| LLMSynthor mobility | Open PFLOW reconstructed movements plus LLMob activity summaries | Guiding marginal/joint macro-statistics from different sources, semantic descriptions, iterative discrepancies | Maps, temporal distributions, mode-distance relationships, concert scenario demonstration | Which exact files/dates/filters and mappings were used? Demonstration does not establish a real concert causal effect |
| LLMSynthor e-commerce | 2,000 records sampled from a known six-variable Bayesian network | All marginal statistics plus joint tables over network-correlated groups | Marginal/joint metrics, classifier two-sample tests, rule-label downstream classifiers, semantic rejection | Documentation differs on baseline supervision; precise independent downstream split and constraints-to-tests overlap need released code |
| LLMSynthor ACS | Survey household/person microdata, South Carolina, approximately 15,000 households after preprocessing | Target macro-statistics derived from reference microdata under Appendix A; precise task-specific list not supplied | 16 policy queries in six categories and record/household consistency screens | Year/product, preprocessing, weights, exact macro/query overlap and evaluation partition not specified sufficiently for exact reproduction |
| Our proposed biomedical setting | Locked real target measurements used only by evaluator; external study evidence provided to agent | Observed target covariates plus source summaries, population/measurement/analysis definitions | Frozen generated data subjected to prespecified analyses beyond source-fitting diagnostics | Still needs evidence that useful results transfer; a different information setting alone is not a proven new method |

Primary paper locators: [G-Sim](https://proceedings.mlr.press/v267/holt25b.html), §3.2–3.3, §5, Appendices C/E/H; [LLMSynthor v3](https://arxiv.org/html/2505.14752v3), §3, §4.1–4.3, Tables 1–6, Appendix A.

## 3. G-Sim: independently checked code boundaries

Pinned release: [samholt/generative-simulations, 72b5d51](https://github.com/samholt/generative-simulations/tree/72b5d51a7790b8b2ebc87973ee5e9d21aa818ece).

- **Default main-table sample count is 100 per split, not 10,000.** config/config.yaml sets run.samples=100; run.py:84–92 passes that value in MAIN_TABLE. run.py:164–176 sets run.trajectories from it. The 10,000 trajectories_sweep setting belongs to the other sweep branch. Each load_data calls simulate(n) independently for train, validation and test. With T=60, each trajectory contains the initial state plus 60 steps. Sources: libs/SIR/env.py:275–303; libs/SUPPLY/env.py:315–341; libs/HOSP/env.py:350–373. The GP branch overrides n to 24 (run.py:169–170); do not describe every default method as using an identical number of trajectories.
- **Seed labels do not guarantee byte-identical reference data.** run.py:166 calls seed_all(seed), and the configuration selects seeds 10–14. But HOSP constructs np.random.default_rng() without a supplied seed (env.py:353), and SIR prediction/reference sampling creates fresh unseeded generators (env.py:94,109–110). Distinct methods regenerate data. This is a static reproducibility concern; it does not establish the size or direction of any published result change.
- **Validation distributional fitness has oracle access.** SIR env.py:100–114 constructs SimulatorStep(), then draws 200 next-state samples from both it and the candidate for every reference state. SUPPLY uses the same 200-sample structure; HOSP uses 20. Finite held-out trajectories supply conditioning states, while an executable ground-truth simulator supplies reference transition draws. This cannot be directly reproduced with only a biomedical paper reporting means and regression coefficients.
- **Validation, not test loss, enters the inspected feedback.** agents.py:361–386 serializes validation Wasserstein loss and per-dimension validation MSE; agents.py:457 selects Wasserstein fitness and :681–691 sorts/culls candidates. The environment computes test losses for each evaluated candidate, but the inspected reflection does not include them. Computation of test metrics is not by itself evidence of test-driven selection.
- **The released SBI path uses a particularly specific observation.** SIR env.py:192–206 flattens train_states[0] as the observed trajectory for NPE. After fitting, :247–257 uses the posterior mean for train/validation/test metrics. It is incorrect to assume this code pools all 100 training trajectories in its SBI observation.
- **Uncertainty exists, but has a scope.** The paper explicitly discusses parameter posterior uncertainty conditional on a candidate structure and explicitly states that it does not capture uncertainty of structural search (§3.2.1; §6). Five-run confidence intervals on benchmark scores are also different from calibrated intervals on a new scientific analysis. We should not claim G-Sim lacks uncertainty, nor assume its reported intervals establish calibration for our target inference problem.

Code paths above are relative to the pinned repository. A fuller baseline-state and implementation audit is in the sibling G-Sim review; this note independently checked the counts, observation, oracle metric, and feedback separation.

## 4. LLMSynthor: what evaluation does and does not establish

**The data generation is hybrid.** The LLM proposes configurations/ranges and numbers of records; continuous values are uniformly sampled within ranges. The cumulative dataset is corrected by adding batches in underrepresented bins. Appendix A explicitly says the process can add records but cannot remove them. This is materially more specific than an unrestricted agent rewriting every cell.

**The experimental feedback is informative target information.** Appendix A says target macros are derived from ground-truth datasets. Continuous variables use six quantile-based main bins and eight sub-bins for local refinement; joint contingency tables are computed for selected groups. Default settings are five proposals per iteration, 100 iterations, three joint combinations per iteration, and at least three repeats. Consequently, matching these bins is a meaningful constraint-fitting result but not independent validation of an unprovided relationship. Exact input/evaluation overlap needs a machine-readable manifest.

**E-commerce is a controlled simulator benchmark.** §4.2 specifies the factorization p(A)p(G)p(L)p(C|A,G)p(X|C)p(M|L). Its target joint groups and reported joint metrics substantially overlap. The two downstream labels, discount_propensity and lifetime_value_band, are deterministic rules over the original fields and are applied to both generated and reference data. The paper trains logistic regression, decision tree and random forest classifiers on synthetic data and evaluates on the reference. This is genuine task-utility evaluation in a known artificial system; it is not prediction of independently measured customer outcomes. Exact disjoint split handling needs clarification before reproduction.

**Baseline descriptions need reconciliation.** §4.2 says all comparison methods use full micro-records. Table 1 instead explicitly marks IPF, LLM-ICL and LLMSynthor as macro-only, SPADA as macro+micro, and the other baselines as micro-supervised. Preserve these distinctions rather than repeating the prose universally. Differing supervision is not intrinsically unfair, but must be reported and interpreted as an information-budget comparison.

**ACS already tests downstream queries.** Sixteen queries across six categories are explicitly defined as practical utility (§4.3). It would be wrong to claim prior work only measures univariate fit or never analyzes generated data. The paper does not provide enough task-specific information to verify that those queries were all excluded from input summaries. Table 5 is also more nuanced than the prose: LLMSynthor has mobility-category MRE 0.35, whereas NVI has 0.24. It wins the other five reported categories. Do not claim lowest MRE in all six.

**Rejection is part of the reported pipeline.** ACS household rejection 13.3% and person rejection 6.3% for LLMSynthor (Table 6) show remaining errors, not perfect logical fidelity. Household failure can be amplified by any failing member. To reproduce comparisons, obtain rules, denominators, rejection order, and whether utility is measured before/after screening. We cannot infer a baseline bug from rejection percentages alone.

**Release status.** The linked [LLMSynthor repository](https://github.com/YihongT/LLMSynthor/tree/92e443f93c6edecc0fa9ca3045d4204da7d42aa5) contains README/images/system files, without the implementation, preprocessing, configs or experiment outputs at the pinned commit. The inspected README still describes the older preprint. A paper-based implementation is possible but must be labeled an independent reconstruction, not an official-code reproduction.

## 5. Underlying data access: verified metadata versus exact reproduction

| Source | Verified access evidence | Important remaining limitation |
|---|---|---|
| Open PFLOW | [Official repository README](https://github.com/sekilab/OpenPFLOW) lists nine Tokyo trajectory ZIP links and fields: ID, timestamp, coordinates, transport. No ZIP was fetched. | The [original 2017 paper](https://doi.org/10.1016/j.trc.2017.09.016) describes constructed movements from open information; records do not correspond to actual movement of identifiable real people. LLMSynthor's exact subset/day/transformations not established. README license text refers to images; do not silently extrapolate it to all data. |
| LLMob | [Official README](https://github.com/Wangjw6/LLMob) describes processed 2019, 2021 and combined directories, from Foursquare records; metadata listing confirms multiple .pkl files in data/2019 and mapping files. No pickle was downloaded or opened. | Availability of processed LLMob files does not identify which subset/activity mapping LLMSynthor used. Complete original Foursquare collection, present API access and reuse conditions are separate issues. |
| ACS/PUMS | [US Census access page](https://www.census.gov/programs-surveys/acs/microdata/access.html) provides CSV/SAS housing and person files, 1-year and 5-year products, API and data.census.gov access. No microdata downloaded. | LLMSynthor states South Carolina and approximately 15,000 households but not enough detail to select the exact year/product, variable recoding/filtering and survey-weight treatment. A new public ACS test is feasible; exact paper dataset recovery is not yet established. |
| G-Sim benchmarks | Released simulator source permits inspection of the data-generating process without restricted observational data. | Known simulator provenance does not remove seed/config/metric differences. No benchmark was executed here. |
| LLMSynthor e-commerce | Paper provides known Bayesian-network structure and examples. | Complete probabilities, reference seed, processed records, prompts and baseline configurations need the missing release or an explicit independent design. |

## 6. Practical recommendation for the next authorized unit

First construct a small, explicit **information contract**, not a large new biomedical experiment:

1. Freeze a known toy joint distribution and separate allowed source summaries from locked analysis queries.
2. Implement an independent LLMSynthor-style append-only proposal/count sampler and a G-Sim-style program/calibration interface using the same allowed inputs; clearly label any reconstruction.
3. Use deterministic stub proposals to test batching, bin comparisons, hard constraints, evidence provenance, and no-answer-access before connecting an LLM.
4. Evaluate source fit separately from unprovided query utility. Add a heterogeneous-source variant only after the single-source mechanics pass.
5. Preserve positive and negative results. Match information and budget where relevant; do not demand that existing papers' original experiments prove our different problem.

Without a paid API or executing third-party code, we can finish contracts, inspect algorithms, build our own small deterministic tests, and design the evaluator. We cannot claim to reproduce their LLM quality numbers. Local open-weight models could support a later experiment, but model acquisition/execution was not undertaken in this audit.

The useful extension question is specific: can the method construct usable target-population data when externally published statistics were computed under different population, measurement and adjustment conditions, and can its frozen data support analyses that were not part of fitting? The audited precedents motivate this question; they neither establish its answer nor rule it out.

