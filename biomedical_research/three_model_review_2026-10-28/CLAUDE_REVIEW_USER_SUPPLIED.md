I'll check whether the private repository is reachable, verify the prior-work and venue leads against primary sources, then write the full review here in the chat.

**Scope and access.** I could not access the private repository. Adding it to this session was refused for lack of access, and no repository under that owner or name is visible here. I tried no other route, so this is not a code audit.

I read both attachments in full: REVIEW_BRIEF.txt and all 13 files in IMPLEMENTATION_APPENDIX.txt.
- `protocol.json`, `BUILDER_GUIDE.md`, `policies/ordinary.md`, `policies/gap_policy.md`, `loop_control.py`, `custodian/evaluate.py`
- Ordinary1 final: `generator.py`, `model_spec.json`, `decision.md`
- Gap2 final: `generator.py`, `model_spec.json`, `gaps.json`, `actions.json`

No participant data were supplied, so I executed no project code. My only computation was arithmetic on the brief's HDL table and the supplied specs. I know Ordinary2 and Gap1 only from the brief. The brief asks for Chinese; I followed your chat instruction and wrote in English.

## 1. Bottom line

The broad idea supports a publishable methods-and-evaluation paper. It does not yet support a superiority claim, and it cannot rest on the two exposed NHANES cases.

Focus the first paper on use case B (adding a never-measured variable), with the ordinary Agent as the method. The paper would contribute three things:
- a precise task definition;
- a simple Agent whose output carries evidence-propagated uncertainty;
- a prospective multi-population evaluation of which analytical conclusions survive translation from literature to generator, and whether the Agent can tell in advance.

Two gaps block that paper today:
- **No isolating comparison.** Nothing separates what the Agent extracted from retrieved evidence from what the model already knew, or from what a statistician would build from the same sources.
- **Fixed parameters.** Every generator is one fixed parameterization. The five seeds therefore measure Monte Carlo noise, while the dominant structural and transport errors never appear in the outputs.

Drop the gap policy as a contribution. Its one useful product, an accurate list of unresolved components, should become the specification of an uncertainty ensemble.

## 2. Positioning

**Central question.** A target cohort observes X but never measured Y. Can an Agent turn heterogeneous published evidence into a generator p(Y | X, target) whose reserved analyses meet three tests?
- They are closer to the truth than the same model without retrieval, and closer than simple statistical source transfer.
- They come with calibrated uncertainty and support labels.
- They are worth a quantifiable number of real measurements of Y.

**Paper type.** Write a methods-and-evaluation paper. A benchmark is a by-product, released as scripts and task definitions because registered-access licences restrict redistribution. A discovery paper is not defensible: generators built from literature cannot reveal biology the literature lacks.

**Titles.**
1. *Which conclusions survive? A blinded multi-cohort evaluation of agent-built evidence generators for never-measured variables.* Recommended, because it stays honest if results are mixed.
2. *From published evidence to analysable variables: language-model agents for enriching cohorts with unmeasured biomarkers.*
3. *How many measurements is the literature worth? Evidence-built generators as priors for unmeasured biomarkers.* Use this only if experiment 2a in Section 6 shows a large effective sample size.

**The ordinary Agent as the method.** Yes, it can be the method. As tested, though, it is a coding assistant with a literature tool and a provenance template, which is not yet a contribution. It must demonstrably do three things a general assistant does not:
- translate estimands (marginal versus conditional, adjustment sets, scales, ecological-to-individual bridges) with typed records;
- emit evidence-propagated uncertainty rather than one parameterization;
- label which analyses its output supports, with measured calibration.

Provenance and freezing are necessary for credibility, but they are engineering.

## 3. What the record establishes

**Verified from the supplied record**
- **Auditable pipeline.** This is a genuine strength:
  - `freeze_candidate()` hash-binds candidates and checks `revision.json` claims and gateway registration.
  - `execute()` checks that observed cells are preserved, that inputs and the global random state are unchanged, and that the same seed reproduces its output.
  - `evaluate.py` opens `locked/reference.csv` only after all 40 output slots validate.
  - Its Taylor variance correctly gives zero scores to out-of-domain PSUs.
- **HDL accuracy (my arithmetic).** I excluded the unresolved sex-by-BMI interaction, which all four builds fell inside.
  - On the 28 remaining builder–endpoint pairs, every sign matched, but only 4 point estimates fell inside the reference 95% interval.
  - None did on the primary endpoint, where the ratios to the reference were 0.75, 0.77, 1.37 and 0.82.
  - All four builds attenuated curvature (ratios 0.10–0.60).
  - Three builds were nearly flat on adjusted age (ratios 0.06–0.13).
- **Between-build spread.** On resolved endpoints, the spread across builds was 1.2–3.1 times the width of the reference interval. The four-build range contained the reference on 6 of 8 endpoints, missing age and curvature.
- **Shared sources.**
  - Both appendix builds anchor on the same Taiwan Biobank sex-by-BMI table and use the identical age vector `[0, 0.75841, 1.18484, 0.87361]`.
  - Ordinary1's `decision.md` notes that this vector comes from a model adjusted for lifestyle, WHR and body fat.
  - The vector spans only 1.2 mg/dL and is held constant outside roughly 35–65 years.
  - The near-flat target age slopes (0.077 and 0.079) are therefore a predictable adjustment-set mismatch, not two independent errors.
- **Gap2 assumptions.**
  - `tail_asymptote_by_sex` has `evidence_ids: []`, and `tail_decay_per_bmi` is declared as assumed.
  - Gap2's `gaps.json` marks 6 of 7 components unresolved, including the shape and age gaps where it later erred.
  - Its generator and spec were nonetheless exact no-ops.
- **Ordinary1 fixed parameters.**
  - Ordinary1's `model_spec.json` fixes all parameters; only the residual draws vary.
  - Above BMI 25.5, its slope comes from just two inputs: one Taiwanese category contrast (anchors at 25.5 and an assumed 30.5), and one Italian clinic-subgroup coefficient (−0.33 per unit, flattening further beyond 30.5).
  - The spec itself shows that the primary endpoint rests on extrapolation over much of the US BMI range.
- **Other completed work.**
  - Insulin had one build and no comparator. The main association survived, but curvature and the sex-slope difference did not; the latter was lost to an explicit no-interaction assumption.
  - Neither the retrospective completion replay nor Stage 1 isolates an Agent or policy advantage.

**Interpretation**
- **First-order directions.** These are reproduced reliably. On NHANES targets that is weak evidence, because the relationships are textbook and the model probably knew them before retrieval.
- **Second-order structure.** Translation fails on curvature, effect modification and age patterns. The failures are predictable from provenance: they sit where parameters are bridged across adjustment sets, extrapolated beyond the source's BMI support, or simply assumed.
- **Confident defaults.** Where structure is unsupported, the generator still gives a definite answer.
  - The insulin build's assumed common slope produced a sex difference of zero.
  - Stage 1's shared-response scenarios produced confident relationships where the reference was unresolved.
- **Right for the wrong reason.** Gap2's closer primary slope plausibly owes much to its steeper tail, about −0.53 per BMI unit at its last anchor, which rests on assumption only. Ordinary1's tail slope of −0.33 came instead from an Italian clinic subgroup in a published author-response table. Agreement on an endpoint does not validate the evidence pathway.
- **Gap policy.** It diagnosed the gaps correctly but could act on them only in prose. Labelling nearly everything unresolved gives a user no guidance.

**Strongest reviewer objections**
1. No comparator isolates the Agent's value. There is no no-retrieval arm, no statistician working from the same sources, and no simple source transfer.
2. Pretraining exposure is unmeasured: the gateway excludes NHANES papers but not the model's memory.
   - LLMs memorise popular tabular datasets ([Bordt et al.](https://arxiv.org/abs/2404.06209v3)).
   - LLM imputers beat MICE on public datasets but not on synthetic ones, which the authors attribute to pretraining exposure ([Mangussi et al.](https://arxiv.org/html/2603.22332v1)).
3. Replication is thin: two enrichment cases, one population and three predictors. The builds share sources, and the seeds are Monte Carlo replicates.
4. No build fell inside the reference interval on the primary endpoint, and no uncertainty is reported.
5. Isolation is procedural.
   - `source_check()` blocks `read_csv`, `load` and `fromfile`, but not `numpy.loadtxt`, `numpy.genfromtxt` or `pandas.read_fwf`.
   - Generators run in-process via `exec_module`, beside the reference on a shared filesystem.
   - I saw no misuse in the two supplied generators, but reviewers will expect OS-level isolation.
6. "Useful" is undefined: there is no user task, no decision endpoint, and no estimate of measurement savings.

## 4. Closest work and novelty

I checked each status below against primary pages in this session unless it is marked otherwise.

| Work | Verified status | Overlap | Remaining difference |
|---|---|---|---|
| [G-Sim](https://proceedings.mlr.press/v267/holt25b.html) | ICML 2025 | The LLM proposes a simulator's structure, which is calibrated gradient-free or by simulation-based inference | G-Sim calibrates to data from the simulated system, but here Y has no target data. The difference is substantive only if aggregate calibration is built |
| [ModelSMC](https://arxiv.org/html/2602.18266v1) | arXiv v1, Feb 2026; no venue stated | LLM-written models treated as weighted SMC particles | Weights use the likelihood of observed data. Ensembling is not novel; aggregate-evidence weighting would be |
| [Li, Fox & Goodman](https://arxiv.org/html/2402.17879v2) | ICML 2024 | The LM writes and critiques probabilistic programs | Fits to available data |
| [SPADA](https://aclanthology.org/2025.emnlp-main.525/) | EMNLP 2025 main; published title begins "Doubling Your Data in Minutes" | LLM-induced dependency graph | Conditionals are fitted on real rows (a regime difference) |
| [DALL-M](https://arxiv.org/html/2407.08227v3) | Comput Biol Med 190:110022, 2025 ([record](https://opus.lib.uts.edu.au/rest/bitstreams/dc1ab5d3-0320-46e6-af6c-8ed1408bf429/retrieve)) | LLM plus retrieval adds patient-level features (MIMIC-IV) | Judged by prediction and MSE, where a supervised model beat the LLM values; no estimands or uncertainty |
| [ProCI](https://web3.arxiv.org/pdf/2507.02928) | arXiv 2025; venue unverified | The LLM proposes and fills unmeasured confounders | Uses pretrained knowledge only |
| [SynthCraft](https://ideas.repec.org/a/plo/pdig00/0001290.html) | PLOS Digit Health 5(3), 2026 | Agent-run synthetic-data workflow with regression checks | Trained on real NHANES and TCGA data; one GAN inverted a sex association |
| [Text-to-tabular](https://arxiv.org/html/2412.05153v2); [LLM lung-cancer cohorts](https://www.elsevier.es/en-revista-open-respiratory-archives-11-articulo-synthetic-lung-cancer-cohorts-generated-by-S2659663625001572) | IEEE ICHI 2025 (per arXiv); Open Respir Arch 2026 | Whole cohorts generated without data | Large distortions (EGFR positivity tripled), so direct row generation is a weak baseline |
| [Fasseeh et al.](https://www.mdpi.com/1999-4893/18/8/475) | Algorithms 2025 | Cohorts built from summary statistics and correlation inputs | Non-agentic; a comparator for A |
| [Gu, Taylor & Mukherjee](https://arxiv.org/abs/2106.06835v2) | Biometrics 79(4), 2023 | Synthetic outcomes from external reduced models, stacked with internal covariates | Internal Y exists. This is B's statistical core and a required baseline |
| [ML-NMR](https://econpapers.repec.org/RePEc:bla:jorssa:v:183:y:2020:i:3:p:1189-1210); [hierarchical related regression](https://econpapers.repec.org/RePEc:bla:jorssa:v:171:y:2008:i:1:p:159-178) | JRSS A 2020; JRSS A 2008 | An individual-level model integrated over aggregate studies' covariates, which is your "observation operator" | Hand-built; automating it is engineering-plus |
| [AutoElicit](https://proceedings.mlr.press/v267/capstick25a.html) | ICML 2025 | LLM-elicited priors, valued as labelling effort saved | Prediction priors drawn from model knowledge; a precedent for "worth n measurements" |

**Statistical precedents to reuse**
- **Plasmode simulation** ([Franklin et al.](https://econpapers.repec.org/RePEc:eee:csdana:v:72:y:2014:i:c:p:219-226)): real covariates with simulated outcomes, which is B's data structure.
- **Statistical matching** ([Conti, Marella & Scanu](https://www.scb.se/contentassets/ca21efb41fee47d293bbee5bf7be7fb3/uncertainty-analysis-in-statistical-matching.pdf)): the conditional-independence default and its identification bounds.
- **Mass imputation** ([Kim & Rao](https://econpapers.repec.org/RePEc:oup:biomet:v:99:y:2012:i:1:p:85-100)): the donor baseline.
- **Record-level probabilistic bias analysis** ([Fox, Lash & Greenland](https://scilit.net/publications/678dc81fac6060021bf5f021fb5d6924)): the uncertainty template.
- **Synthetic-data inference and utility:** combining rules ([Raghunathan, Reiter & Rubin](https://scholars.duke.edu/publication/689859)) and interval-overlap utility ([Karr et al.](https://econpapers.repec.org/RePEc:bes:amstat:v:60:y:2006:m:august:p:224-232)).
- **Pseudo-IPD** ([Papadimitropoulou et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC6767371)).
- **Use case A:** [Synthea](https://academic.oup.com/jamia/article/25/3/230/4098271) and QSP virtual populations ([Allen et al.](https://www.biorxiv.org/content/10.1101/028548v1)).
- **Indirect inference:** Gourieroux et al. 1993, a standard reference I did not re-verify.
- **NCHS public-use synthetic linked files** ([page](https://www.cdc.gov/nchs/linked-data/synthetic/)): users can request verification metrics against the original files, a precedent for analysis-level checks. The page does not describe the synthesis method.

**Novelty**
- **Substantive, if delivered:**
  - the regime itself: no target Y, heterogeneous aggregate evidence, inferential targets;
  - calibrated support labels;
  - a quantified information value of the literature.
- **Empirical:** performance against the baselines, and the size of the transport limits.
- **Engineering:** retrieval, provenance, freezing, gap records, multi-agent review and generator code.

## 5. Method improvements (proposals), identifiability and uncertainty

**How evidence should change a generator.** Treat the parameters θ and a small set of structures s as uncertain.
- For each evidence item e that reports a statistic s_e with standard error SE_e, the Agent writes an operator g_e(θ, s).
- The operator simulates under e's covariate distribution, measurement and analysis, and returns the statistic e would have reported.
- Draws are then weighted by

  w(θ, s) ∝ ∏_e N(s_e; g_e(θ, s), SE_e² + τ_e²).

The bridge variance τ_e comes from a pre-registered rule over typed mismatch categories, never from LLM confidence.
- **Categories:**
  - population distance;
  - adjustment mismatch;
  - assay or fasting differences;
  - ecological bridges;
  - source tier: main text, supplement, author-response correspondence, or abstract only.
- **Calibration:** ideally from cross-cohort heterogeneity in public data.
- **Fallback:** where g_e cannot be computed, the item becomes a direct prior on the parameter, with a larger τ_e.

This is ML-NMR or indirect inference with an LLM front end, and should be presented as such. A simple version can be built in days:
- draw each parameter from N(estimate, SE² + τ²);
- give each declared structural alternative a preset weight;
- skip replay weighting.

**M1: evidence-propagated ensembles**
- **Change:** replace the fixed `parameters` dictionary with `sample_parameters(evidence, rng)`. Add one declared structural alternative per consequential unresolved gap, such as a flat versus a declining tail. The controller then emits M datasets at the target n, each from a different draw.
- **Mechanism:** the gap map becomes variability in the data, so uncertainty no longer shrinks as the synthetic n grows.
- **Test:** on fresh tasks, compare coverage and weighted interval score (WIS) across three arms:
  - (a) the fixed generator with naive synthetic intervals;
  - (b) M1;
  - (c) K independent builds without parameter draws.

  If (c) matches (b), the cheaper builder ensemble suffices.

**M2: provenance-derived support labels**
- **Change:** for each analysis, decompose the endpoint's variance across the ensemble. Attribute it to parameters that are direct, bridged, assumed, or set by a conditional-independence default, and label the analysis accordingly.
- **Deployment check:** add a target-free check that also works in real use. Hold out each source that has a computable operator, and score how well the remaining evidence predicts it.
- **Test:** measure the AUROC of the labels, and of the replay error, for predicting target failure across tasks and endpoints. Compare against the Agent's current free-text support statements. Applied post hoc, these labels would have flagged Gap2's curvature and both builds' age effects.

**Impossible without added assumptions**
- **Individual values:** agreement is capped by R²(Y|X).
- **Associations between generated Y and anything not conditioned on,** including a second generated variable: these rest on conditional independence, and the identified set is only the Fréchet or positive-definiteness bounds.
- Curvature or interactions inferred from category means.
- Transported levels and slopes.
- Threshold prevalences derived from means and SDs.
- Causal effects.
- For case A, joint structure beyond the reported correlations.

**Still useful**
- direction and approximate magnitude where a compatible estimand exists;
- the range of conclusions compatible with the evidence;
- planning quantities;
- priors for two-phase designs;
- prototyping.

**Avoiding vagueness and false precision**
- Give point generators where an analysis is supported, and ranges only where it is not. WIS penalises both width and misses.
- Never report within-dataset standard errors or p-values from synthetic data.
- Keep the synthetic n equal to the target n, and report the across-draw distribution of each estimate. The target's n carries no information about Y | X.

## 6. Experiment matrix (proposals)

| Stage | Task and inputs | Methods | Unit | Primary outcome | Go/stop (proposed) | Effort |
|---|---|---|---|---|---|---|
| 0. Diagnostics | HDL and insulin, existing X and locked endpoints (development only) | Frozen builds; no-retrieval Agent (2 builds per case); null generator; same-population donor (another NHANES cycle); external donor (KNHANES or CHARLS); fixed moment-matching on the Agent's extracted evidence; M1 retrofit | Case (2) | Normalised error and its decomposition | If no-retrieval ≈ Agent, retrieval adds nothing here. If the external donor also misses age and curvature, the problem is transport | 1–2 weeks |
| 1. Pilot | 6 fresh tasks (3 variables × 2 populations); 5–8 predictors; pre-registered endpoint families | Agent + M1 (2 builds); Agent fixed; no-retrieval (2 builds); time-capped statistician using the same gateway; published-equation transfer; donors; null | Task (6) | Normalised WIS; 80% coverage; agreement on interpretation | Go if the Agent beats no-retrieval in ≥5 of 6 tasks and coverage is ≥60% at ≤2× the heterogeneity width | 4–6 weeks |
| 2. Main | 16–24 tasks; ≥4 populations; ≥8 variables; 3 vs about 10 predictors; post-freeze analyses chosen by an independent analyst | As Stage 1 | Task (hierarchical model) | As Stage 1, plus label AUROC | Drop any claim that misses its pre-registered criterion | 3–5 months, 1–2 FTE |
| 2a. Two-phase | Reveal k ∈ {0, 25, 50, 100, 200, 400} measured Y values | Literature generator updated with k observations vs imputation from the subsample alone | Task × k | Effective sample size: the k at which the subsample alone matches the generator | Report regardless | +2 weeks |
| 2b. Unsupported analyses | Two never-measured variables | With and without joint evidence; independence default; bounds | Task pair | Bound coverage; label accuracy | — | +2 weeks |
| 3. Unexposed | A data release or new assay after the freeze | Best Stage 2 configuration | Release | As above | — | Depends on access |

**Comparators by regime**
- **B (absent column):** the arms above.
  - The statistician is the expert baseline.
  - The external donor is a reference with richer information, not a fair competitor.
  - Target-trained CTGAN, TabDDPM and MICE cannot exist when Y was never measured.
- **C (missing cells):** MICE/PMM on the observed cells, Bayesian imputation with literature priors, and the Agent (via Stage 2a).
- **A (whole cohort):** a summary-statistics copula generator, direct LLM row generation as a weak baseline, and the Agent. Target-trained generators appear only as clearly labelled information oracles.
- **Direct-analysis Agent:** ancillary. It answers a single planned estimate, such as an effect size for study planning.
  - Give it the analysis list and the same budget, and give the generator no list.
  - The generator's claim must then rest on unplanned analyses and on coherence across analyses.

**Datasets (verified this session)**
- **NHANES:** public. The 2021–2023 HDL file was first published in September 2024 ([HDL_L](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/HDL_L.htm)), so it probably falls within recent pretraining.
- **KNHANES:** microdata available from the survey website ([profile](https://stacks.cdc.gov/view/cdc/27858)).
- **CHARLS:** 2015 blood data downloadable after sign-up since 2019 ([notice](https://charls.pku.edu.cn/en/info/1104/1274.htm)).
- **HSE:** licensed through the UK Data Service.
- **Unverified leads:** ELSA, MHAS, IFLS and LASI.

"Public to the world" is not the same as "unexposed to construction":
- **Can be enforced:** tool and file isolation, and the choice of reserved analyses unlikely to have been published.
- **Can only be measured:** pretraining exposure, via the no-retrieval arm and memorisation probes.
- **Can only be avoided** through releases after the training cutoff, restricted data, or new measurement.

## 7. Results that would justify claims

**Ladder of evidence**
1. Source replay is only a sanity check.
2. Leave-one-source-out prediction shows that translation generalises.
3. Reserved analyses, stratified by support class, are the main result.
4. Coverage and WIS show calibration.
5. Label AUROC shows label value.
6. Effective sample size and planning accuracy show user value.
7. Between-build SD relative to interval width shows reproducibility.

**Proposed tolerances (not standards)**
- **Normalised error.** Define z = (θ_gen − θ_ref)/√(SE_ref² + τ²), where τ is the between-population SD of the same estimand across independent public cohorts other than the target.
  - |z| ≤ 1 means the estimate is as close as a real foreign cohort typically is.
  - The criterion does not tighten merely because the reference is large.
- **Main effects.** The sign must match, and the ratio to the reference must fall in [0.67, 1.5].
- **Curvature or effect modification.** The generated estimate must agree on whether the reference interval excludes zero. If it does, the ratio must fall in [0.5, 2].
- **Calibration.** Nominal 80% intervals should cover 70–90% of at least 40 task–endpoint pairs.
- **Labels.** AUROC ≥ 0.7.

Change direction if any of these holds:
- the Agent does not beat no-retrieval on most tasks;
- M1 coverage stays below 50%;
- the labels perform near chance.

**Controls against leakage, circularity and false precision**
- **Leakage:**
  - run builders in containers where the custodian files do not exist;
  - keep the reference encrypted until release;
  - pre-register endpoints, tolerances and stop rules;
  - use an independent custodian;
  - never use exposed cases as confirmation.
- **Circularity:** before evaluation, classify every endpoint as directly evidenced, bridged or unsupported, and report each class separately. Reproducing a relationship that was fed in counts only as consistency.
- **False precision:** follow the rules in Section 5.

**Demonstrations without overclaiming**
- **Enrichment:** tasks with richer X, which is where identifiability starts to bind.
- **Cross-study transfer:** the information ladder (literature Agent, external donor, same-population donor) separates translation error from transport error.
- **Unsupported analyses:** use Stage 2b, plus analyses of Y against covariates that the evidence does not cover.
  - Success means the labels flag these analyses and the bounds cover the truth, not a point hit.
  - Report individual-level agreement only to show its R² ceiling.

## 8. Public-data and wet-lab routes

**Public data only.** Four components:
- the information ladder;
- the multi-population benchmark;
- two-phase simulation on real data, which estimates measurement savings in silico;
- pre-registration against announced data releases (check the release calendars).

Together they validate fidelity, calibration, the information value of literature and transport limits, all under measured contamination.

**Optional prospective or wet-lab route.** After freezing a generator, assay a sparsely studied biomarker in 100–300 stored samples from an existing cohort.
- This validates genuinely unexposed prediction and real two-phase savings.
- Re-measuring HDL would be decorative.
- No mechanistic experiment is needed, because the claims concern evidence transfer, not biology.

## 9. Venues

**Ambitious.** Nature Communications is plausible only with all of the following, and nothing guarantees acceptance:
- 15–20 or more prospective tasks across at least 3–4 populations;
- clear wins over the no-retrieval and statistician baselines, or a striking effective-sample-size result;
- calibrated intervals;
- at least one genuinely unexposed confirmation;
- open code.

npj Digital Medicine and Patterns are high-visibility alternatives with an informatics framing.

**Attainable.**
- Statistics in Medicine
- American Journal of Epidemiology
- Epidemiology
- Research Synthesis Methods
- JAMIA or JBI
- BMC Medical Research Methodology

**ML venues.** NeurIPS renamed its datasets track [Evaluations & Datasets](https://neurips.cc/Conferences/2026/CallForEvaluationsDatasets) in 2026.
- It welcomes negative results.
- Its hosting and access requirements suit an NHANES-only release better than registered-access data.
- I have not verified the 2027 call, ML4H or CHIL.

**Main figures**
1. Regimes and pipeline.
2. Information-ladder error decomposition.
3. Accuracy by support class.
4. Coverage against width, fixed versus ensemble.
5. Label ROC, and replay error versus target error.
6. Two-phase WIS against k.
7. A failure gallery: curvature, effect modification and the independence default.

## 10. Two-week milestone and ranked plan

**Schedule**
- **Days 1–2:** pre-register Stage 0, isolate the reference, and apply for KNHANES and CHARLS access.
- **Days 2–6:** run the no-retrieval Agent (2 builds per case), the null generator and the same-population donors. Add the external donor when access arrives; NHANES III is the fallback.
- **Days 5–8:** retrofit M1 onto the frozen Ordinary1 and Gap2 specs, as a development check only.
- **Days 8–14:** pre-register and run 2–3 fresh Stage 1 tasks.

**Decision rule**
- **Go** if both hold:
  - the retrieval Agent beats no-retrieval on most endpoints in at least 2 of 3 fresh tasks;
  - M1's 80% intervals cover at least 60% of resolved endpoints within 3× the heterogeneity width. This is looser than Stage 1 because only 2–3 tasks exist.
- **Otherwise redirect:** choose targets the model is less likely to know, or reframe the work as an evaluation-of-limits paper.

**Stop**
- two-build policy comparisons;
- mandatory gap and action files;
- scenario enumeration as a stand-in for uncertainty;
- confidence intervals computed on synthetic data;
- extra agents;
- using HDL or insulin as confirmation.

**Keep**
- typed provenance;
- gateway exclusions;
- freezing;
- the independent evaluator;
- honest no-ops.

**Build:** PDF supplement extraction, which blocked at least two of Gap2's leads.

**Ranked plan**
1. Run the information ladder with a no-retrieval arm. This is the highest-value experiment: it shows whether retrieval adds anything, and whether error comes from translation or transport.
2. Adopt M1, normalised-error and WIS evaluation, and OS-level isolation.
3. Run the Stage 1 pilot.
4. Test M2 labels and the two-phase effective sample size.
5. Scale up, with A and C as secondary.

**Tradeoffs**
- Starting with B narrows the story but gives clean identification.
- Ensembles widen the outputs, and WIS keeps that width accountable.
- Statistician baselines cost hours, but reviewers will demand them.

**Strongest objection.** I cannot yet separate what the Agent learned from retrieval from what the model already knew. Its errors also look dominated by structural and transport assumptions that fixed generators hide.

**What would change my mind.** Across at least 10 fresh tasks:
- the retrieval Agent clearly beats no-retrieval;
- ensemble intervals cover near nominal at a useful width;
- the labels discriminate;
- the literature proves worth a non-trivial effective sample size.

## Sources

- **Prior work:** [G-Sim (PMLR)](https://proceedings.mlr.press/v267/holt25b.html) · [ModelSMC (arXiv)](https://arxiv.org/html/2602.18266v1) · [Li, Fox & Goodman (arXiv)](https://arxiv.org/html/2402.17879v2) · [SPADA (ACL Anthology)](https://aclanthology.org/2025.emnlp-main.525/) · [DALL-M (arXiv)](https://arxiv.org/html/2407.08227v3) and [publication record](https://opus.lib.uts.edu.au/rest/bitstreams/dc1ab5d3-0320-46e6-af6c-8ed1408bf429/retrieve) · [ProCI (arXiv)](https://web3.arxiv.org/pdf/2507.02928) · [SynthCraft (PLOS record)](https://ideas.repec.org/a/plo/pdig00/0001290.html) and [preprint](https://www.medrxiv.org/content/10.1101/2025.08.17.25333866.full.pdf) · [Text-to-tabular (arXiv)](https://arxiv.org/html/2412.05153v2) · [LLM lung-cancer cohorts](https://www.elsevier.es/en-revista-open-respiratory-archives-11-articulo-synthetic-lung-cancer-cohorts-generated-by-S2659663625001572) · [Fasseeh et al.](https://www.mdpi.com/1999-4893/18/8/475) · [AutoElicit (PMLR)](https://proceedings.mlr.press/v267/capstick25a.html) · [Bordt et al.](https://arxiv.org/abs/2404.06209v3) · [Mangussi et al.](https://arxiv.org/html/2603.22332v1)
- **Statistical precedents:** [Gu, Taylor & Mukherjee](https://arxiv.org/abs/2106.06835v2) · [ML-NMR](https://econpapers.repec.org/RePEc:bla:jorssa:v:183:y:2020:i:3:p:1189-1210) · [Hierarchical related regression](https://econpapers.repec.org/RePEc:bla:jorssa:v:171:y:2008:i:1:p:159-178) · [Plasmode simulation](https://econpapers.repec.org/RePEc:eee:csdana:v:72:y:2014:i:c:p:219-226) · [Uncertainty in statistical matching](https://www.scb.se/contentassets/ca21efb41fee47d293bbee5bf7be7fb3/uncertainty-analysis-in-statistical-matching.pdf) · [Kim & Rao](https://econpapers.repec.org/RePEc:oup:biomet:v:99:y:2012:i:1:p:85-100) · [Fox, Lash & Greenland](https://scilit.net/publications/678dc81fac6060021bf5f021fb5d6924) · [Raghunathan, Reiter & Rubin](https://scholars.duke.edu/publication/689859) · [Karr et al.](https://econpapers.repec.org/RePEc:bes:amstat:v:60:y:2006:m:august:p:224-232) · [Papadimitropoulou et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC6767371) · [Synthea](https://academic.oup.com/jamia/article/25/3/230/4098271) · [Allen et al.](https://www.biorxiv.org/content/10.1101/028548v1) · [NCHS synthetic linked data](https://www.cdc.gov/nchs/linked-data/synthetic/)
- **Data and venues:** [NHANES HDL_L](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/HDL_L.htm) · [KNHANES profile](https://stacks.cdc.gov/view/cdc/27858) · [CHARLS blood-data notice](https://charls.pku.edu.cn/en/info/1104/1274.htm) · [NeurIPS 2026 Evaluations & Datasets call](https://neurips.cc/Conferences/2026/CallForEvaluationsDatasets)