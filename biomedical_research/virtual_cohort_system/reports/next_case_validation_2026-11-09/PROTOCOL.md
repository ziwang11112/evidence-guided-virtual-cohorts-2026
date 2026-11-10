# PNS blood-pressure joint generation: prospective task protocol

Version: 1, drafted 2026-11-09. Status: REVIEW PENDING; this document is not itself the freeze receipt.

## Scientific question and evidence role

Can an evidence-guided Agent, given a target description and original external published evidence but no target individual measurements, generate one joint cohort that supports two adjusted blood-pressure associations and their residual dependence? The primary contribution under test is usable virtual biomedical data, not feedback superiority, a required multi-Agent architecture, or recovery of each patient's true measurements.

This is a new prespecified blood-pressure task in the previously exposed PNS laboratory-substudy release. PNS HbA1c analyses and full column names were previously exposed. A metadata search incidentally exposed national age/sex BP-prevalence snippets to the host; these are not the target subset or the three estimands, and are excluded from author packets. The history audit found no prior numerical exposure of these three PNS BP analyses. This is not a wholly unseen cohort or a globally blind validation.

## Target and metadata

Use the existing official `PNS2013_Exames.zip`, SHA256 d31544efdad138f3292ab86c9606cd722bf091781cc86ef371354ba63c9994bb; member `EXAMES-PNS-2013-FINAL_05052023.xlsx`, SHA256 80222fa535524829d531504109ac4b49d44e4e6d0c04c3c281ff972bd332d1f7. Expected sheet `EXAMES-PNS-2013-FINAL_com-ponde`. Verify hashes before reading.

The analytical distribution is the `peso_lab`-weighted complete-case adult frame defined below. It is not asserted to equal Brazil's national population. The released workbook has no supported PSU/stratum identifiers. Primary estimates are finite weighted descriptive projections, not causal effects. An unweighted sensitivity panel is retained. Generated equal-weight rows represent the requested weighted distribution under the author's transport assumptions; no target weighted shares or moments are disclosed.

Required source columns: `C008` age at baseline; `Z001` sex (dictionary 1 male, 2 female); lowercase `z004` weight kg, `z005` height cm; `P005` pregnancy; `W00407` final SBP mmHg; `W00408` final DBP mmHg; `peso_lab`. Formula BMI=kg/(cm/100)^2. Include baseline age20–79, recorded sex1/2, weight30–200kg, height120–210cm, SBP60–290mmHg, DBP30–200mmHg, positive finite labweight; all seven non-pregnancy analysis/design fields must be finite and present. Exclude only reported pregnancy P005=1; missing/unknown/inapplicable pregnancy status is retained and counted. Dictionary error999 and nonnumeric missing symbols in the seven required fields are ineligible, never recoded to biological values. No HbA1c completeness requirement, BMI trimming, hypertension/treatment restriction, or SBP≥DBP selection is applied. All three analyses use identical rows.

BP belongs to the initial interview; laboratory collection later occurred in2014–15. Do not age participants forward or call these BP values laboratory-visit measurements. The official manual specifies G-TECH MA100, seated rest≥5min, 3measurements separated by2min, normally leftarm. The manual/dictionary inspected do not establish the final released aggregation algorithm. Use the published final fields without claiming a last-two mean; preserve that limitation. Measurement manual hash and download receipt are separate. Source studies' different devices/averaging/treatment selections require applicability assumptions, not silent pooling.

## Fixed analyses and diagnostics

The common design matrix is [1,(age−50)/10,female,(BMI−25)/5]. The three focal estimates are (1) BMI coefficient in SBP regression, mmHg/5kg/m²; (2) BMI coefficient in DBP regression, same units; (3) weighted Pearson correlation of the two regressions' centered residuals. Centering constants are coordinate choices, not scientific model parameters. Generated analysis uses equal weights; reference uses `peso_lab`, plus unweighted sensitivity. This is a fixed analysis query, not an instruction to the Agent about its answers.

Required diagnostics: mean/SD of age, female, BMI, SBP and DBP; marginal SBP–DBP correlation; SBP and DBP residual SD; fraction SBP<DBP; finite output, sample size, effective weight count and design rank. These are not alternative primary outcomes. Report singular or deterministic failures explicitly, never remove failed authors or choose a favorable seed. No unregistered omnibus quality score or arbitrary pass threshold.

Display reference weighted point estimates with 500 IID row-resampling stability replicates (seed73991), retaining each sampled row's original weight. The 2.5%–97.5% intervals describe conditional row-resampling stability, **not survey-design confidence intervals or known population truth**. Each generator's three draws show Monte Carlo variation; five fresh constructions show author variability, not five independent clinical studies. Compare signed/absolute estimate differences and dispersion ratios descriptively. A same-sign result alone is not sufficient, and exact equality is not required. No formal superiority or equivalence test is planned.

## Agent method and information boundary

Reuse frozen additive adaptive_session_v2, semantic_feedback_v1, descriptive_feedback_v1, and isolated WSL/bubblewrap execution. Optional whole_cohort_source_replay_v1 is available when a defensible source population and operator can be declared; source-context output cannot be replaced by target-context statistics and relabelled exact replay.

Five independent fresh-context authors A01–A05 receive the same task/schema, authoring skill, vetted external-source packet and interface documentation. Actual host dispatch IDs, inherited model identity and unavailable model/token metadata are recorded honestly. No paid model API is introduced. The host does not write the scientific generator, desired coefficients, signs, covariance, or target-informed parameters. Authors may use their priors as explicitly marked assumptions and retrieve further public non-PNS evidence under the fixed budget. The source packet and discovery log distinguish original reports, algebraic implications and assumptions. Correlations conditioned on different covariates are not silently equated.

Authors can choose program or direct-table route supported by the task contract; no requirement for a particular model family. Program route uses `generate(observed,spec,seed)`, observed=None. Output:3000virtual rows with identifier, age, female, BMI, SBP, DBP. The three research queries are visible. Clinical reference records, target means, slopes, dependence and comparison results are unavailable until all authors close.

Per author: at most12source queries,10new source downloads,50MiBnew source bytes, 2submitted candidates (initial+at most1source-driven revision);3seeds271,409,557 for every submitted stage. At most6target-like generator executions,6strict+descriptive feedback pairs,6generated-analysis calls. Any optional source replay has separately recorded max6executions, not counted as clinical validation. All failed attempts consume the applicable budget. Web-discovery queries, if used outside the controller, count against the same12query budget and are logged; snippets are leads, not quantitative evidence. No resets or replacement authors to compensate for failure.

Before submit, independent implementation review checks no reference access, declared parameter provenance, bounded mathematical behavior, schema and feedback operator semantics without imposing wanted scientific relations. Authors see their own generated diagnostics and permitted source feedback. They choose revise/retain/stop; all decisions are valid outcomes. A selected law's three outputs are final (max15final tables); all stages remain preserved (max30target-like tables), and source-replay tables have their own accounting.

## Freeze, reveal and stopping

First freeze admission/selection before custodial schema/readiness counts; no target means or associations are emitted. Then bind protocol, source packet, skill, new adapter/wrapper/evaluator and core engine hashes after independent artificial-fixture checks. Launch no author until this second freeze. Do not modify frozen inputs or engines; any necessary software failure repair requires a versioned receipt before reference reveal and a truthful account of which outputs were affected.

After the selection lock, one custodian-only readiness read may produce only the frozen counts/rank checks; it must not produce outcome means, associations or comparisons. Seal each author's selected or failed outcome, all candidates and attempted seeds, outputs, feedback, analysis and reviews. The batch seal requires all5fixed slots. Only after that batch seal may the reference analyses or comparison results be computed or revealed. Independent recomputation follows. Do not regenerate or adjust a generator after target results are revealed. If source admission is inadequate, schema/readiness fails, or the permitted runtime is unavailable, preserve the concrete failure and stop; do not launch a substitute case automatically.

## Reporting and limits

Report every prespecified outcome, stage and author. Explain direct source constraints vs missing joint/transport assumptions. No claim of recovered personal values, avoided measurements in clinical care, national prevalence, new biology, calibrated uncertainty, novelty from number of Agents, or universal superiority. Clinical and generated row-level tables and full third-party documents stay local; public synchronization may include reviewed original code, protocol, provenance metadata and aggregate results only.
