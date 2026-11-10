# Historical strengths audit

Audit date: 9 November 2026. This file reviews existing historical reports; it creates no new scientific result. Paths below are relative to the virtual_cohort_system project root, with `../` indicating a sibling directory. The companion HISTORY_AUDIT.json contains the full per-family ledger and a detailed temporal-prediction audit.

## What the historical evidence positively supports

The strongest defensible conclusion is that evidence-conditioned virtual data already support **selected subsequent analyses**, in several distinct input regimes. The record is not limited to making supplied means look right. It includes temporal real-sample prediction, entirely unmeasured biomarker enrichment, whole-cohort generation without participant inputs, literal row authorship and a genuine local repair. None establishes unrestricted replacement of measured data, stable superiority over competent ordinary methods, or avoided collection cost.

**Entirely unmeasured-variable enrichment has the broadest historical support.** The first insulin pilot added an absent insulin column to 1,700 real age/sex/BMI records using external papers. All20 draws retained positive adjusted and within-sex BMI associations, although the adjusted ratio was1.230 versus measured1.346 and shape/interaction failed. Later M10 used richer observed covariates including glucose: two builds in1,961 participants retained positive BMI and negative quadratic curvature across6 draws. Its independent-country PNS case (7,979 participants; two builds) retained positive age and BMI associations, with age estimates0.1589/0.1563 versus0.1470. These units demonstrate analysis-enabling virtual columns, not recovery of individuals' laboratory values.

**M5 and M17-B show benefits beyond a single linear relation.** M5's three proposed structures all preserve positive age and negative raw/log global BMI curvature in a new2,660-person NHANES period, over15 retained outputs; BMI magnitude remains too strong in every table. M17-B supplies no individual source or target records at all: two Agents generate age, sex, BMI and urate from three external papers plus prospective quotas. All6 draws preserve adjusted BMI, age and sex directions against one320-person quota reference; age magnitudes are also close. Complete-cohort utility is therefore demonstrated in a small case, though all generated BMI means are below the sample reference, forward/reverse effects trade off, and shape/interaction remain unresolved. M17-B uses programs, not literal row emission.

**A bounded true train-synthetic/test-real example is present.** H05 uses two literally authored128-row cohorts to train frozen models tested in1,811 later-cycle real NHANES participants. Logistic AUCs0.712130/0.726871 and Briers0.216229/0.213445 beat a prevalence-only reference (0.5/0.248578), while remaining below real128-row training (AUC0.734936, Brier0.210303). The ordinary100-draw median is0.717394/0.215560, so there is no stable direct-author advantage. This is a stronger analytical-use example than reconstructing a supplied statistic, but it requires rich outcome-conditioned summaries computed from128 measured people.

**Literal authorship is more than an unexecuted interface.** Early paired studies used directly written records; H16 literally authored all1,875 value/null slots for75 five-visit trajectories; M15-B and M16 literally authored entire urate columns. M15-B's BMI coefficient is0.345446 versus measured0.335316, though age has the wrong sign and all group distribution summaries are high. M16's three fresh authors all retain positive BMI and negative quadratic terms. One author changed exactly12 outcome values after source/own-guide feedback: BMI discrepancy improves0.048314→0.018438 and all four target group SDs improve. Age, curvature and interaction discrepancies worsen. This is evidence of a real, auditable local repair with specific utility, not universal repair improvement.

**Completion and within-study reconstruction remain useful, narrower strengths.** In H17, the Agent imputer beats the particular MICE–PMM reference on hidden-cell MAE and primary-coefficient discrepancy in all3 masks; it preserves every original observation and all31 native missing cells. Expanded replay preserves all18 affected evidence states, matching missing-only and exceeding MICE's17. But missing-only is closer on the main coefficient in all3 masks, and29/35 unchanged analyses are preservation controls. Early Travers reconstruction reproduces all four change directions/classifications, with one literal cohort closely recovering leptin change SD1.541 versus1.534; the provided means/SDs were computed from the source workbook. Supplying paired correlations later brings generated change-SD ratios near1 by design. These are transparent reconstruction capabilities, not independent validation.

## Temporal prediction: leakage and comparator check

The endpoint is **current laboratory HbA1c≥5.7% among adults with BMI≥30**, using age, sex, BMI, waist and systolic BP. It is not obesity classification, so BMI does not define the outcome; it is also not future diabetes prediction. HbA1c and labels are excluded from all model predictors. The source packet was freshly computed from a fixed seeded128-person training sample, not extracted from papers. Four outcome-by-sex strata supplied counts, moments, seven quantiles and regularized rank correlations. This is legitimate supervised summary-conditioned synthesis, and cannot support “no real data required.”

Both authors' unchanged round0 outputs were used. The historical audits report no scientific row repair or performance feedback. Pre-lock root changes repaired a `rows` schema mismatch, provenance binding and schedule validation. Each logistic scaler fits only its own training cohort. Two model families, the0.5 decision threshold and their settings were fixed; no test-guided preprocessing, feature/hyperparameter selection, recalibration or favorable ordinary-seed selection was used.

Recorded model lock is16:14:21.403UTC, before test acquisition at16:14:27.087UTC; IDs do not overlap. The independent historical audit checked207 prediction vectors,206 model schemas and323 bound artifacts, with metrics agreeing within1.33e-15. Current review read those aggregate audit reports and did not touch patient tables or rerun evaluation. Ancillary test assay/specimen documentation was exposed before lock, but outcome/predictor distributions were not reported as exposed. Procedural records cannot prove absence of unlogged or pretraining exposure.

The ordinary AUC2.5th–97.5th percentile range is0.651048–0.743380 and Brier range0.205302–0.234218. Both authors lie inside it; they exceed38 and67 of100 ordinary AUCs. These are generator variability ranges, not sampling confidence intervals. No inferiority/superiority/equivalence test was performed. The fixed boosting model and weighted sensitivities are retained in JSON; they do not reverse the primary mixed comparison. The sample is a selected complete-case survey domain, not a validated national clinical prediction service.

## How evidence is graded and counted

A = strongest available support for a bounded analytical use with a reserved measured reference; B = specific positive but mixed/development finding; C = supplied-constraint reconstruction or source-only illustration; E = engineering/constructed fixture; R = review/preparation without new empirical generation validation. Grades are qualitative review judgments, not statistical scores.

The36 entries below group canonical families or stages. They are not36 independent experiments. The55 reviewed report/audit paths include all22 top-level milestone reports, with M9 preparation, the A/B/C variants, and relevant25–28October sibling families plus nested follow-ups. Reused Ross/Travers/He references, repeated NHANES endpoints, retained lifecycle versions and residual seeds are explicitly dependent. Engineering execution counts and tests are never counted as clinical successes.

Important information boundaries are different across families: workbook-derived source summaries, published-paper aggregates, target baseline summaries, target development feedback, real observed covariates, and remaining observed cells. Early M12/M17-A fixtures contain deliberately specified known laws; their success does not show autonomous scientific inference. Source-supported signs and imposed hinges are transferred assumptions, not previously unknown mechanisms. HOMA-derived outcomes do not independently validate each component biomarker. Ordinary synthetic-table intervals omit much source, structural and transport uncertainty.

## Canonical historical family ledger

### H01_pediatric_summary_authorship — grade C

- **Classification/input:** same-study summary holdout. Clinical group summaries supplied; IL-6 and TNF-alpha group summaries withheld; known paper identifiable.
- **Actual scale:** One 27-person pediatric source; two fresh direct 27-row constructions.
- **Comparison:** Authored group moments versus published moments.
- **Strongest support:** Both literal cohorts preserved higher IL-6 and TNF-alpha in MUO than MHO.
- **Numbers:** Paper contrasts 1.10/1.10; A 0.75/0.56; B 0.54/0.54. Supplied clinical mean median errors 0.05/0.07 source SD.
- **Counterresults:** All withheld contrasts attenuated; generated clinical SDs as low as 0.26 of supplied SD.
- **Inference boundary:** Prompt withholding does not exclude pretraining exposure; published-summary consistency, not independent patient validation.
- **Paper role:** Early feasibility illustration; do not use as independent discovery.
- **Reviewed sources:** `../obesity_agent_generation_pilot_2026-10-25/RESULTS.md`

### H02_travers_paired_reconstruction — grade C

- **Classification/input:** same-study reconstruction. Study design, units, n=12 and pre/post means/sample SDs rounded to3 decimals, freshly computed from public workbook rather than all printed in article; no paired correlations/change SD/CI/p-values or patient rows.
- **Actual scale:** One 12-man, three-day intervention cohort; two direct 12-person paired cohorts; four endpoints.
- **Comparison:** Same original paired analyses on measured and generated tables.
- **Strongest support:** Both constructions retained all four change directions and unadjusted significance classifications; one closely reconstructed leptin change variability.
- **Numbers:** Leptin real change/SD -2.563/1.534; B -2.567/1.541; paired p 0.0001212 versus 0.0001244.
- **Counterresults:** A underestimates change dispersion materially; B underestimates three of four endpoint dispersions.
- **Inference boundary:** Within-study reconstruction with disclosed margins and very small male-only sample; p agreement partly input constrained.
- **Paper role:** Concrete true-direct-row precedent; supplementary reconstruction example.
- **Reviewed sources:** `../obesity_public_data_replication_2026-10-25/RESULTS.md`

### H03_he_paired_reconstruction — grade C

- **Classification/input:** same-study comparative reconstruction. Same disclosed pre/post marginal moments for direct authors and ordinary paired Gaussian-copula sampler.
- **Actual scale:** 44 pediatric completers; glucose/TG 43 pairs; two direct constructions; 3,000 ordinary draws across three rho settings.
- **Comparison:** Direct rows versus primary rho=0.5 sampler and sensitivity rho=0/0.9.
- **Strongest support:** Direct rows closely reconstructed margins and body-mass paired dispersion better than the primary fixed-rho comparator.
- **Numbers:** Body-mass SD(change)/real: A 0.823, B 0.705, ordinary median 6.277.
- **Counterresults:** Ordinary comparator closer for three other paired dispersions; both direct cohorts made TG significant when measured data were nonsignificant (p 0.4014 vs 0.04359/0.02300).
- **Inference boundary:** One modest source; unknown paired dependence dominates; no consistent direct-author advantage.
- **Paper role:** Counterweight to selected reconstruction successes.
- **Reviewed sources:** `../obesity_larger_replication_2026-10-25/RESULTS.md`

### H04_dependence_disclosure — grade C

- **Classification/input:** reused-data reconstruction and engineering. He source margins plus newly disclosed within-endpoint pre/post correlations; cross-endpoint relations withheld.
- **Actual scale:** Same 44/43-pair source; two fresh direct authors; one tool planner; 1,000 ordinary draws; unchanged retained direct tables.
- **Comparison:** Direct supplied-constraint reconstruction versus ordinary/tool sampling; post-hoc 18 cross-endpoint edges.
- **Strongest support:** Explicit dependence evidence enables literal rows to reconstruct paired variability very closely.
- **Numbers:** Direct change-SD/packet ratios: D1 0.9784–1.0036; D2 0.9857–1.0099. Tool planner outputs exactly equal ordinary same-seed rows.
- **Counterresults:** No numerical revision occurred. Cross-endpoint rMAE D1 0.4212, D2 0.3292 versus ordinary 0.1903/0.2236.
- **Inference boundary:** Supplied correlations mathematically determine paired dispersion; not hidden-outcome recovery or new clinical replication. Review demo reuses H03 data and creates no new Agent run.
- **Paper role:** Mechanistic illustration of what evidence buys; avoid treating p-value reconstruction as independent validation.
- **Reviewed sources:** `../obesity_agent_feedback_dev_2026-10-25/RESULTS.md`; `../obesity_agent_system_design_2026-10-25/REVIEW_DEMO.md`

### H05_temporal_prediction — grade A

- **Classification/input:** locked temporal prediction. Outcome-by-sex-stratified counts, means, SDs, seven quantiles and regularized rank correlations from 128 real NHANES 2015–16 participants; no individual author inputs.
- **Actual scale:** 128 real training rows; two literal 128-row cohorts; 100 ordinary cohorts; 1,811 eligible NHANES 2017–18 test participants; two frozen classifiers.
- **Comparison:** Real-only training and information-matched ordinary generation, no favorable-seed selection.
- **Strongest support:** Aggregate-conditioned literal synthetic rows retained useful discrimination for current elevated HbA1c in a later survey cycle.
- **Numbers:** Logistic AUC: real 0.734936; A1 0.712130; A2 0.726871; ordinary median 0.717394. Brier: real 0.210303; A1 0.216229; A2 0.213445; ordinary 0.215560. Prevalence-only AUC0.5/Brier0.248578. Ordinary AUC generation quantiles0.651048–0.743380; A1/A2 exceed38/67 of100 draws. Weighted logistic AUC real0.742122/A1 0.722713/A2 0.734453/ordinary0.724310.
- **Counterresults:** Neither author surpassed real-only AUC/Brier; one author below and one above ordinary AUC median. Both inside ordinary generation interval; no sampling CIs or noninferiority testing; boosting AUC real0.660930/A1 0.634484/A2 0.646883/ordinary0.638858 and Brier0.240598/0.247879/0.242525/0.261487.
- **Inference boundary:** Cross-cycle within same survey, current measured threshold not future diabetes; summaries used measured outcome labels; one training draw and two authors; no feedback intervention. Raw HbA1c excluded from five predictors. Training-only StandardScaler; threshold0.5 and both classifier families fixed. Model lock16:14:21.403UTC precedes test download16:14:27.087. Original round0 direct outputs unchanged; only prelock schema/provenance fixes. No formal guarantee against unlogged/pretraining exposure.
- **Paper role:** Strong historical downstream-use example; explicitly summary-conditioned and non-superiority.
- **Reviewed sources:** `../obesity_temporal_prediction_2026-10-25/RESULTS.md`; `../obesity_temporal_prediction_2026-10-25/NUMERICAL_AUDIT.md`; `../obesity_temporal_prediction_2026-10-25/DATA_AUDIT.md`; `../obesity_temporal_prediction_2026-10-25/CODE_AUDIT.md`; `../obesity_temporal_prediction_2026-10-25/TEST_DATA_AUDIT.md`

### H06_cross_study_forecast_screen — grade B

- **Classification/input:** two-case cross-study feasibility. Source-summary packets computed from public individual data, not automatically extracted paper tables; no target outcome summaries; forecasts frozen.
- **Actual scale:** Population NAGALA n=15,450; intervention DIETFITS n=464; three Agent contexts per arm; three queries per case.
- **Comparison:** Direct Agent A versus cohort Agent B versus random-effects C; source-specific references.
- **Strongest support:** Both Agent arms improved primary association point loss over exchangeable pooling in both cases.
- **Numbers:** Equal-case primary squared error A 0.001137; B 0.001500; C 0.006246. Population target r 0.3469; B forecasts 0.3291–0.3373.
- **Counterresults:** B did not beat A; C better all-query equal-case error (0.004286 vs A 0.005205/B 0.005434); evaluator sex-code repair disclosed.
- **Inference boundary:** Only two cases; primary forecasts not necessarily reusable-row superiority; source relevance varies by query; targets now exposed.
- **Paper role:** Support for contextual evidence use, not necessity of a virtual cohort representation.
- **Reviewed sources:** `../cross_study_virtual_cohort_pilot_2026-10-25/RESULTS.md`

### H07_exploratory_feedback_and_uncertainty — grade B

- **Classification/input:** exposed-target development. WLM/STRRIDE-PD aggregates; target baseline sex/TG summaries; sequential DIETFITS development feedback.
- **Actual scale:** Previously exposed DIETFITS n=464 split 301 development/163 internal check; four versions, 10,000 simulated rows each.
- **Comparison:** Initial versus marginal, conditional-point and uncertainty-informed revisions.
- **Strongest support:** Agent-authored feedback revisions can improve specific internal-check distribution or event metrics.
- **Numbers:** Check quantile error 0.3344 initially to 0.1478 after marginal repair; correlation MAE 0.0932 to 0.0829 after point repair; joint-event error 1.62528 to 1.16194 pp for uncertainty revision.
- **Counterresults:** Weight–HOMA correlation error rises to 0.13180; round3/round2 intervals include zero for all four differences; versions trade off.
- **Inference boundary:** All target already exposed; feedback uses target outcomes; numerical integration rows not new subjects; no external superiority baseline.
- **Paper role:** Development lineage showing real revisions and multidimensional trade-offs.
- **Reviewed sources:** `../exploratory_evidence_generator_2026-10-26/RESULTS.md`; `../exploratory_evidence_generator_2026-10-26/RESULTS_UNCERTAINTY.md`

### H08_measurement_transfer — grade B

- **Classification/input:** cross-study partial-feedback transfer. DIETFITS/FIT-MI aggregate sources; FIReWoRk baselines and development weight outcomes only; waist outcomes withheld until lock.
- **Actual scale:** FIReWoRk 400 complete pairs split 260/140; two versions, 10,000 rows each.
- **Comparison:** Initial versus one weight-calibration revision.
- **Strongest support:** Weight-only feedback improved held-out weight distribution and some unprovided waist/event diagnostics.
- **Numbers:** Weight quantile error 0.35493→0.10547; waist 0.39592→0.35802; joint-event MAE 7.00→2.85 pp.
- **Counterresults:** Waist/event improvement intervals include zero; partial-correlation error worsened 0.26402→0.27015; source/target waist sites differ.
- **Inference boundary:** Selected complete clinic-pair population; true additional-variable transfer is mixed, with no anatomical conversion validation.
- **Paper role:** Secondary limited example of unprovided metric improvement; retain relationship failure.
- **Reviewed sources:** `../exploratory_measurement_transfer_2026-10-26/RESULTS.md`

### H09_hierarchical_structure_transfer — grade B

- **Classification/input:** new-study structural comparison. Source aggregate joint evidence; all target baselines and development weight-only feedback, no target waist feedback.
- **Actual scale:** Queen's trial 215 complete records, 107 development/108 check; two fixed constructions; generated weight margins matched exactly.
- **Comparison:** Person mixture versus common-population construction.
- **Strongest support:** Separating study-level construction improved held-out partial correlation while holding generated weight margins fixed.
- **Numbers:** Primary partial-correlation error 0.30897→0.23661 (23.4%); joint-event error 7.981→6.488 pp; real partial r 0.83526 versus 0.52629/0.59865.
- **Counterresults:** Waist quantile error 0.40796→0.42724; adjusted slope error 0.04224→0.14317.
- **Inference boundary:** One independent study relative to prior FIReWoRk; transductive target-baseline information; contrast changes multiple structural ingredients.
- **Paper role:** A real specific structural improvement; avoid claiming universal joint fidelity.
- **Reviewed sources:** `../exploratory_hierarchical_transfer_2026-10-26/RESULTS.md`

### H10_structure_scale_transfer — grade B

- **Classification/input:** new-study 2x2 transfer. Source aggregates and target baselines; weight-only versus added development waist mean/SD feedback.
- **Actual scale:** CHANGE318 complete participants split159development/159check from428 released; four retained10,000-row cells; no post-check revision.
- **Comparison:** Person mixture/common population × weight-only/waist-affine calibration.
- **Strongest support:** Distributional improvement and a transferred correlation advantage are separable.
- **Numbers:** Common-population waist quantile error 0.62798→0.25715 (59.1%); partial-correlation error common 0.18725 vs mixture 0.24836.
- **Counterresults:** Common adjusted-slope error 0.07996→0.15410; primary joint objective not achieved.
- **Inference boundary:** Waist calibration uses measured target development moments; affine correlation preservation is algebraic, not new learning. Psychiatric/medication context and12month target versus6month sources; no learned time mechanism.
- **Paper role:** Useful calibration-versus-relationship separation, not broad synthesis success.
- **Reviewed sources:** `../exploratory_structure_scale_transfer_2026-10-26/RESULTS.md`

### H11_joint_evidence_revision — grade B

- **Classification/input:** retrospective source-representation repair. Existing source joint summaries repaired; four external papers contextual only, no new fitted external coefficient.
- **Actual scale:** Three exposed target checks: FIReWoRk 140, Queen's 108, CHANGE 159; weight-only and weight+waist settings.
- **Comparison:** Old versus joint-block generator.
- **Strongest support:** Preserving already available source conditional covariance reduced adjusted-relationship errors across three retrospective targets.
- **Numbers:** DIETFITS source partial r: real 0.703738, old 0.604224, joint 0.702743. Target partial-r errors 0.1854→0.1019; 0.2305→0.1556; 0.1872→0.1096.
- **Counterresults:** Slope worsens in two weight-only cases; some quantile/event diagnostics worsen.
- **Inference boundary:** Not three new independent confirmations; source representation defect correction on already exposed cases; external equations not fitted.
- **Paper role:** Evidence translation/representation strength, clearly retrospective.
- **Reviewed sources:** `../exploratory_joint_evidence_2026-10-26/RESULTS.md`

### H12_actual_paper_addition — grade B

- **Classification/input:** retrospective paper-evidence addition. Actual partial FIT/MI paper evidence plus target baseline aggregates; Han relation added after initial freeze.
- **Actual scale:** Historical target subsets 211 development/107 check; one initial and one evidence-linked revision.
- **Comparison:** G0 versus G1 across fixed joint-response and regression endpoints.
- **Strongest support:** One paper addition can improve specific conditional means and regressions with traceable provenance.
- **Numbers:** Check waist responder error 1.5279→0.7098 cm; slope error 0.0166→0.0104; intercept error 1.9162→0.0598 cm.
- **Counterresults:** Primary four-cell TV error worsens 5.0608→11.6473 pp; change interval includes zero; no stable population-reuse improvement.
- **Inference boundary:** Previously exposed target, one addition; equation reconstruction not target validation.
- **Paper role:** Narrow positive illustration with primary negative prominently retained.
- **Reviewed sources:** `../exploratory_paper_evidence_update_2026-10-26/RESULTS.md`

### H13_constructed_agent_review — grade E

- **Classification/input:** engineering mechanism experiment. Eight authored evidence/model cases with disclosed constraints; identical critique for continued/fresh reviser.
- **Actual scale:** Three planned reviewer runs; one failed before artifact; two completed; five distinct contexts/seven executed language stages.
- **Comparison:** Same-context versus separate-context review/revision.
- **Strongest support:** Both completed workflows corrected six faulty models and retained two valid models.
- **Numbers:** 16/24 accepted planned case instances in each workflow; 16/16 conditional on delivered reviews.
- **Counterresults:** No added benefit from separate reviewer; 1/3 reviewer delivery failure retained.
- **Inference boundary:** Invented cases and known oracle, not clinical data generation evidence.
- **Paper role:** Engineering evidence for review/correction; no clinical count.
- **Reviewed sources:** `../agent_review_loop_2026-10-26/RESULTS.md`

### H14_real_paper_review — grade E

- **Classification/input:** real-document review experiment. Three authored simulator memos about one disputed Framingham trial and dependent publications.
- **Actual scale:** Three memos; ten criteria each; initial output cap failed, amended transport retained exact original answers.
- **Comparison:** First appraisal versus continued/fresh audits.
- **Strongest support:** First reviews corrected all seven authored errors while preserving five valid/qualified statements.
- **Numbers:** Three initial appraisals 10/10 frozen criteria; no added correction from final audits.
- **Counterresults:** Incomplete source reading disclosed; third fresh audit introduced minor extraction error; initial transport failed.
- **Inference boundary:** Tests evidence interpretation on supplied proposals, not spontaneous failure detection, collaboration advantage or synthetic-patient validity.
- **Paper role:** Source interpretation component only.
- **Reviewed sources:** `../agent_real_evidence_review_2026-10-26/RESULTS.md`

### H15_ross_paper_replay_and_acquisition — grade B

- **Classification/input:** same-study reconstruction and development retrieval. Ross five-visit marginal summaries; first Agent-written stochastic generator then targeted external evidence acquisition.
- **Actual scale:** 75 people at five visits; twenty retained seeds per version; related reuse of same reference.
- **Comparison:** Original paper-question replay and prior versus evidence-revised generator.
- **Strongest support:** Repeated data support some supplied time contrasts and an unsupplied related-measure correlation; acquisition directly improves one informed relation.
- **Numbers:** DD100–DD1000 real baseline r 0.644, synthetic median 0.628, MAE 0.078; overall reserved rMAE 0.165590→0.164323 (0.77%).
- **Counterresults:** PFS/DD100 MAE 0.271; individual-change score barely changes; overall improvement interval spans zero; weight anomaly affects source SE.
- **Inference boundary:** Means disclosed; one reused small cohort; acquisition ledger 10 records is not 10 studies; no all-paper conclusion recovery.
- **Paper role:** Within-study analytical reuse with explicit supplied-versus-reserved split.
- **Reviewed sources:** `../obesity_paper_replay_2026-10-27/RESULTS.md`; `../obesity_evidence_acquisition_2026-10-27/RESULTS.md`

### H16_ross_direct_vs_program — grade B

- **Classification/input:** direct/program development comparison with post-hoc utility replay. Same target-derived margins for two fresh authors; external PFS–DD100 relation; no patient rows or query answers.
- **Actual scale:** 75 trajectories, five visits, 1,875 slots; one literal author with 288-cell revision; one program; three unique cohorts despite four lifecycle labels.
- **Comparison:** Direct initial/final versus program; later same scientific analyses on unchanged tables.
- **Strongest support:** Literal full trajectories are operationally feasible; program and direct rows support different useful analyses.
- **Numbers:** Direct supplied SD error 9.8376%→0.5269%; overall correlation error direct final 0.174937 vs program 0.191165. Program PFS–weight beta 0.1431 vs real 0.1657; direct final 0.3784.
- **Counterresults:** Direct repair worsens overall rMAE 0.154140→0.174937; program gives better 3/4 pooled associations despite worse correlation score; both overstate DD associations and significance.
- **Inference boundary:** Target margins disclosed; existing cohort; downstream extension post hoc; one lineage per route; unchanged versions duplicates.
- **Paper role:** Strong proof of distinct true direct route; analysis-specific utility, no route winner.
- **Reviewed sources:** `../obesity_generation_routes_2026-10-27/RESULTS.md`; `../obesity_analysis_utility_2026-10-27/RESULTS.md`

### H17_masked_completion_and_expanded_replay — grade B

- **Classification/input:** masked-cell development comparison and reuse. Visible observations condition both imputers; one external correlation explicitly not numerically used. Agent sees only first masked input before generic method freeze.
- **Actual scale:** 75-person five-visit cohort; three overlapping masks each hide 54/269 observed follow-up PFS cells; 20 imputations per method/mask; 31 native gaps preserved.
- **Comparison:** Agent joint longitudinal imputer versus MICE–PMM versus missing-only; expanded 35-analysis replay.
- **Strongest support:** Agent imputer improves hidden-cell accuracy and primary coefficient recovery relative to this MICE reference while preserving existing observations and all affected evidence states.
- **Numbers:** Cell MAE Agent 0.338457/0.327963/0.393704 vs MICE 0.362037/0.382223/0.471975. Primary coefficient mean error Agent 0.044560 vs MICE 0.087097. Affected evidence-state agreement Agent 18/18, MICE 17/18, missing-only 18/18.
- **Counterresults:** Missing-only primary error 0.010656, better in 3/3 masks. Agent improves effect discrepancy over missing-only 6/18. 29/35 unchanged outputs are preservation controls. Post-hoc weight influence check does not reverse main conclusion.
- **Inference boundary:** One cohort, one Agent model; unequal features/specifications prevent isolating LLM benefit; no demonstrated external-evidence gain or calibrated MI coverage.
- **Paper role:** Useful completion and exact preservation claim; primary utility negative versus no filling must accompany it.
- **Reviewed sources:** `../obesity_masked_completion_2026-10-27/RESULTS.md`; `../evidence_virtual_cohort_framework_2026-10-27/RESULTS.md`

### H18_stage1_scenario_policy — grade B

- **Classification/input:** three-case exposed-data scenario sensitivity. Supplied moments from Ross/Travers/He; matched ordinary versus expanded scenario revisions; fixed statistical references.
- **Actual scale:** Three previously exposed sources (75, 12, 44/43); nine initial lineages; 18 paired revisions; 420 cohort draws; 55 reference terms.
- **Comparison:** Ordinary revision versus each prespecified scenario, no best-scenario selection or pooling.
- **Strongest support:** Demonstrates auditable analysis sensitivity to plausible but unreported dependence assumptions.
- **Numbers:** He persistent/stable alternatives match six-correlation evidence states 41/42, 40/42, 41/42; alternative shared-response scenarios only 0/36, 0/36, 7/36.
- **Counterresults:** No recurring accuracy advantage; some scenarios add confident unsupported findings; Travers body-mass SE ratios up to 16.97; given means are reconstruction not validation.
- **Inference boundary:** Not 420 studies; 33 given mean terms versus 22 reserved relations; no calibrated inference or independent confirmation.
- **Paper role:** Sensitivity/failure-mode evidence, not headline accuracy.
- **Reviewed sources:** `../evidence_virtual_cohort_framework_2026-10-27/stage1/RESULTS.md`; `../evidence_virtual_cohort_framework_2026-10-27/stage1/DECISION.md`; `../evidence_virtual_cohort_framework_2026-10-27/stage1/reporting/STATISTICAL_REFERENCE_RESULTS.md`

### H19_initial_insulin_enrichment — grade A

- **Classification/input:** locked entirely unmeasured-variable enrichment. Only target age/sex/BMI rows; six non-NHANES papers searched by clean Agent; no glucose, HOMA, target insulin summaries or analysis answers.
- **Actual scale:** NHANES 2017–18 n=1,700 domain; one Agent lognormal construction; twenty residual draws.
- **Comparison:** Same reserved real-versus-generated survey-weighted analyses.
- **Strongest support:** External evidence can populate an entirely absent biomarker and preserve broad BMI associations, including both sexes.
- **Numbers:** Adjusted geometric-mean ratio per5 BMI real 1.346 [1.304,1.390], generated median 1.230; all 20 positive with intervals above null. Within-sex all20 positive; male/female medians 1.223/1.233.
- **Counterresults:** Curvature contrast real -0.123 vs median 0.003; sex interaction real -0.109 vs 0.006. Fixed common slope/no interaction assumptions explain failure.
- **Inference boundary:** One construction and one survey cycle; supported relation transfer not unknown biology; 34,000 virtual values not participants; retired contaminated search context disclosed.
- **Paper role:** Core historical enrichment support with structural limits.
- **Reviewed sources:** `../insulin_feature_enrichment_2026-10-27/RESULTS.md`

### H20_hdl_gap_policy — grade A

- **Classification/input:** locked comparative enrichment. Only age/sex/BMI, opaque IDs and metadata; equal literature tools/budgets to ordinary and explicit-gap builders.
- **Actual scale:** NHANES2013–14 4,885-person target; two independent builds per policy; five seeds/stage;40 files but25 unique tables.
- **Comparison:** Ordinary capable Agent versus explicit gap/action policy; initial/final.
- **Strongest support:** All four constructions preserve negative BMI/sex-specific BMI and higher female HDL; independent ordinary Agent retrieves/revises usefully.
- **Numbers:** Real adjusted BMI -3.916; final medians ordinary -2.935/-3.008, gap -5.380/-3.224. Ordinary1 -2.747→-2.935 after revision.
- **Counterresults:** Both gap builders retain identical numerical generators; ordinary1 improves five endpoints/worsens three; age near-flat for three builders; gap-policy superiority unsupported.
- **Inference boundary:** Four constructions one cohort; protocol engineering adds no verified quality advantage; preserved directions partly external-evidence constrained.
- **Paper role:** Broad enrichment robustness across builders, not policy superiority.
- **Reviewed sources:** `../evidence_gap_loop_2026-10-28/RESULTS.md`

### H21_review_and_design_only — grade R

- **Classification/input:** review and positioning, no new empirical unit. Prior results and briefs supplied to model reviewers.
- **Actual scale:** No new biomedical dataset, generation, or target analysis.
- **Comparison:** Research framing recommendations and factual corrections.
- **Strongest support:** Clarifies three input regimes and separates ordinary capable Agent feasibility from optional multi-Agent policy benefit.
- **Numbers:** No empirical numerical support counted.
- **Counterresults:** Review agreement is not independent experimental confirmation; some reviews lacked repository access.
- **Inference boundary:** Not part of scientific experiment denominator.
- **Paper role:** Historical context only.
- **Reviewed sources:** `../obesity_multimodel_review_2026-10-25/REVIEW_SYNTHESIS.md`; `../three_model_review_2026-10-28/CLAUDE_ADOPTION_AND_THREE_REVIEW_SYNTHESIS.md`

### M_engineering_fixtures — grade E

- **Classification/input:** engineering only. Invented data/evidence; M12-A/B and M17-A contain deliberately specified known generators; M2/M12-C include actual independent Agent construction.
- **Actual scale:** M1 seven-row arithmetic fixture; M2 128 rows/three executions; M12-B 12 source rows/26 trials/56 executions; M12-C one construction/eight executions; M17-A one 128-row complete-cohort fixture.
- **Comparison:** Contracts, source context, immutable calibration, retain/promotion and execution/linkage behavior.
- **Strongest support:** Three input modes and two output routes have executed and verified interfaces; valid failures and explicit retention retained.
- **Numbers:** M2 same-seed bytes identical/different seed changed outcome with observed inputs preserved; M12-B recovered intercept3/slope2/scale1 on compatible fixture and retained contradictory/infeasible cases; M17-A five independent stats agree ≤2.22e-16.
- **Counterresults:** No biomedical accuracy evidence, no Agent superiority; M1 program route only statically inspected; invented successful stopping criteria not clinical thresholds.
- **Inference boundary:** Do not pool software tests/executions with target studies. M2 real search is separate transport smoke; no fictional model scientific support from fetched paper.
- **Paper role:** Methods implementation evidence only, no clinical denominator.
- **Reviewed sources:** `MILESTONE_1_REPORT.md`; `MILESTONE_2_PROGRESS.md`; `MILESTONE_12A_RESULTS.md`; `MILESTONE_12B_RESULTS.md`; `MILESTONE_12C_RESULTS.md`; `MILESTONE_17A_RESULTS.md`

### M03_tg_source_feedback — grade A

- **Classification/input:** locked enrichment plus separate toy component. Real target age/sex/BMI; two curated external source papers; target TG and analysis answers withheld. Separate 128-row fictional retention trial.
- **Actual scale:** NHANES 2017–18 n=2,072; one initial construction/one source-driven revision; five paired residual seeds each.
- **Comparison:** Initial versus source-only revision on same withheld target.
- **Strongest support:** Source-only feedback can improve a selected unprovided effect without target tuning; BMI/age/curvature directions stable.
- **Numbers:** Primary absolute log-BMI error median 0.08584→0.06755 (21.3%), decreases all5 pairs; real logeffect0.1012 vs initial0.1870/final0.1687; curvature -0.0448 vs -0.0511/-0.0471.
- **Counterresults:** BMI still too strong; sex difference worsens -0.1630→-0.2593 vs -0.1708; interaction target CI spans zero.
- **Inference boundary:** One construction/case; curated evidence, no equal-budget ordinary self-review contrast; toy retention not clinical success.
- **Paper role:** Concrete positive source-feedback example with paired trade-off.
- **Reviewed sources:** `MILESTONE_3_RESULTS.md`

### M04_source_portfolio_retention — grade C

- **Classification/input:** source-only development; reused generator. Inherited M3 final model, same source recipes plus quantile/rank operators; no new target evaluation.
- **Actual scale:** One review; zero scientific parameter changes; six replays/twelve context executions/204 checks.
- **Comparison:** Richer source diagnostics and justified retention.
- **Strongest support:** Additional source checks can expose conflicts and justify no-op retention instead of arbitrary overfitting.
- **Numbers:** WHS TG median113.97 vs115; BMI Spearman0.3362 vs0.33; initial/final102 paired changes all0.
- **Counterresults:** Age Spearman0.2107 vs0.18; other source age-cell mean already low; qualitative historical target sentence incidentally exposed through README.
- **Inference boundary:** No new blinded target result; simulated source covariates; repeated checks not independent populations.
- **Paper role:** Responsible retention and source-trade-off case only.
- **Reviewed sources:** `MILESTONE_4_RESULTS.md`

### M05_tg_temporal_structures — grade A

- **Classification/input:** locked temporal enrichment with structural alternatives. Same two external papers, target age/sex/BMI, no target TG or previous target answers.
- **Actual scale:** NHANES2021–23 n=2,660; one Agent/three structures/five draws each;15 tables.
- **Comparison:** Additive, multiplicative and latent-mixture alternatives with source feedback; new temporal reference.
- **Strongest support:** All three substantially different submitted structures retain positive adjusted age and negative global BMI curvature on log and raw TG scales.
- **Numbers:** Age real0.05528; S1/S2/S3 means0.06208/0.06446/0.04541. Logcurvature real-0.05366; -0.03376/-0.04897/-0.03580. Both priority directions15/15.
- **Counterresults:** All15 BMI effects exceed real95% CI upper bound; interaction unstable; S3 source-challenged; shared structural assumptions remain.
- **Inference boundary:** One Agent alternatives, not three independent Agents; same survey temporal replication; global quadratic projection not local biological threshold; seed ranges not uncertainty CIs.
- **Paper role:** Strong reserved analysis-use evidence beyond input mean reconstruction.
- **Reviewed sources:** `MILESTONE_5_RESULTS.md`

### M06_constructive_identifiability — grade E

- **Classification/input:** synthetic constructive stress test. Inherited imperfect source-informed TG law; assumed product covariate distribution; prespecified synthetic probe.
- **Actual scale:** Three law labels/three seeds; no real target;276 alternative comparisons.
- **Comparison:** Zero/minus/plus bounded interaction perturbations preserving declared pairwise laws.
- **Strongest support:** Source-summary and global-projection stability can coexist with different subgroup expectations.
- **Numbers:** 276/276 descriptive screen passes;252 exactly unchanged; male55–64 BMI26–27 plus-minus8.94–10.92 mg/dL; designed analytical9.90783.
- **Counterresults:** No global age/curvature direction reversal; separation known by design; baseline fit not certified.
- **Inference boundary:** Mathematical implementation demonstration under product source assumption, not biomedical discovery or independent validation.
- **Paper role:** Explanation of analysis-specific support limits.
- **Reviewed sources:** `MILESTONE_6_RESULTS.md`

### M07_M09_M14_preparation — grade R

- **Classification/input:** source audit/preparation only. M7 joint TG literature gap; M9 insulin/HbA1c eligibility/evidence packets; M14 body-fat measurement/transport sources.
- **Actual scale:** No new target efficacy result: M7 no new generator/replay/evaluation; M9 prepares1961/7979; M14 retains unexecuted source-mean substitution.
- **Comparison:** Source admissibility and applicability decisions.
- **Strongest support:** Evidence-aware workflow can refuse incompatible statistic conversion and keep unavailable/inapplicable evidence explicit.
- **Numbers:** M7 six searches, unresolved supplement/standardization; M9 18 conflicting SHIP items withheld; M14 six-study audit with one unexecuted sensitivity specification.
- **Counterresults:** No numerical-generation improvement or new target validity demonstrated; approved sources do not identify transport.
- **Inference boundary:** Prepared participants not extra empirical validations; M14 does not validate scanner conversion; no field invented to complete bridge.
- **Paper role:** Methods evidence governance; exclude from empirical denominator.
- **Reviewed sources:** `MILESTONE_7_RESULTS.md`; `MILESTONE_9_PREPARATION.md`; `MILESTONE_14A_RESULTS.md`

### M08_joint_tg_evidence — grade A

- **Classification/input:** locked temporal enrichment revision. Observed age/sex/BMI and external joint Tromso ratios; source-only construction; withheld fasting TG.
- **Actual scale:** NHANES2009–10 n=1,575; inherited baseline/revision × three draws;67 endpoints each.
- **Comparison:** Initial versus interaction-only joint-evidence revision.
- **Strongest support:** A substantive source-informed revision preserves both priority directions and improves age magnitude.
- **Numbers:** Age measured0.03873; baseline0.04965→revision0.04309; curvature measured-0.04033, -0.03101→-0.03134.
- **Counterresults:** Other analyses trade off; baseline already preserved directions; no overall-superiority claim.
- **Inference boundary:** Temporal holdout same survey; ratios are nonfasting adjusted log-effects not subgroup means;28 related contrasts not28 studies.
- **Paper role:** Second specific evidence-driven update with limited transfer gain.
- **Reviewed sources:** `MILESTONE_8_RESULTS.md`

### M10_insulin_enrichment — grade A

- **Classification/input:** locked unmeasured-variable enrichment. Age/sex/BMI/fasting glucose observed; external sources; insulin entirely withheld; no autonomous retrieval.
- **Actual scale:** NHANES2015–16 n=1,961; two fresh constructions×three draws.
- **Comparison:** Frozen retained generators versus measured reserved analyses.
- **Strongest support:** Both independent constructions preserve positive BMI association and negative BMI curvature across all6 draws.
- **Numbers:** BMI real0.2959, A0.2379/B0.2517; curvature real-0.0517,A-0.0206/B-0.0391.
- **Counterresults:** Age weak/unresolved; sex-slope difference real-0.1193 vs -0.0081/-0.0051 markedly attenuated.
- **Inference boundary:** Input glucose makes this richer than H19; three residual draws are not construction replications; no revision benefit, individual recovery or full fidelity.
- **Paper role:** Replicated selected enrichment utility, show richer covariate setting explicitly.
- **Reviewed sources:** `MILESTONE_10_RESULTS.md`

### M10_hba1c_enrichment — grade A

- **Classification/input:** locked external-country enrichment. PNS baseline age/sex/BMI observed; later HbA1c withheld; external non-PNS evidence.
- **Actual scale:** Brazil PNS n=7,979; two fresh constructions×three draws.
- **Comparison:** Retained evidence-built generators versus measured weighted analyses.
- **Strongest support:** Positive age and BMI relations transfer to a different survey/country case.
- **Numbers:** Age real0.1470, A0.1589/B0.1563; BMI real0.1610, A0.0906/B0.1043; both directions all6.
- **Counterresults:** Curvature real0.0409 vs -0.0060/+0.0116; slope magnitudes attenuated and interaction unstable.
- **Inference boundary:** PNS lab weights but no explicit PSU/stratum in workbook; no invented survey CIs; baseline/lab time gap; no revision advantage.
- **Paper role:** Breadth across biomarker/country within bounded enrichment claim.
- **Reviewed sources:** `MILESTONE_10_RESULTS.md`

### M11_hba1c_source_calibration — grade B

- **Classification/input:** new-endpoint locked negative-transfer mechanism. Inherited M10 families; source median shifts from SHIP scenarios; target age/sex/BMI only.
- **Actual scale:** NHANES2021–23 HbA1c n=5,378; two inherited families×four versions×three seeds=24 tables.
- **Comparison:** Initial versus exact source-median calibration plus two source-covariate sensitivities.
- **Strongest support:** Mechanism clearly separates source fit from target utility; broad associations remain executable/stable.
- **Numbers:** Sex-median MAE A0.1769→0.2525,B0.1417→0.2261; source medians fit numerically.
- **Counterresults:** All three headline level/subgroup discrepancies worsen; retained associations expected under additive shifts.
- **Inference boundary:** Negative transfer, not efficacy; new endpoint in reused survey cycle; no new Agent repetitions or whole-cohort validation.
- **Paper role:** Necessary limit to source-fit optimization claims.
- **Reviewed sources:** `MILESTONE_11_RESULTS.md`

### M13_bodyfat_source_to_target — grade B

- **Classification/input:** source development followed by locked endpoint test. Two screened papers; initial simulated qualification grid/source contexts; later target age/sex/BMI only, body fat withheld.
- **Actual scale:** Two Agent builds; source18trials/80executions; target primary612 and extension230;12 Agent tables plus4 published-equation references;62 endpoints.
- **Comparison:** Initial/reviewed Agent generators; deterministic/stochastic published equation reference.
- **Strongest support:** Some body-fat relationships, especially female age association, transfer despite overall level/effect mismatch.
- **Numbers:** Female age real0.966pp/decade, final0.881/0.816. All primary BMI associations positive. Source fitting losses1.070225→0.668102 and0.695051→0.623795.
- **Counterresults:** Male means real23.764 vs19.064/20.034; BMI effects male4.275 vs7.894/7.870; source revision often worsens target. Curvature real intervals include0.
- **Inference boundary:** M13A no real target; M13B new endpoint within already used cycle; source equations explicitly supply relationships; published reference must remain visible.
- **Paper role:** Limited transfer plus strong counterexample to source fit sufficiency.
- **Reviewed sources:** `MILESTONE_13A_RESULTS.md`; `MILESTONE_13B_RESULTS.md`

### M15A_literal_complete_rows — grade C

- **Classification/input:** source-summary direct-row illustration. Twenty supplied moments from one Bogalusa paper; four urate SDs withheld; all age/BMI/urate/race/sex fictional.
- **Actual scale:** One fresh direct author,128 rows, four proportional groups; one unique table, initial/final retained duplicate.
- **Comparison:** Supplied moment reconstruction and same-source withheld SD check.
- **Strongest support:** Literal all-variable cohort authoring achieves close marginal reconstruction without a sampling program.
- **Numbers:** All20 supplied moment mean relative error1.10%; urate group means essentially exact.
- **Counterresults:** All withheld urate SDs too narrow:17.97–36.33% relative errors; no independent reference for joint analyses.
- **Inference boundary:** One small source-shaped table; actual independent authorship route but no repair, clinical inference or target validation.
- **Paper role:** Unambiguous true-direct whole-cohort route; reconstruction-only.
- **Reviewed sources:** `MILESTONE_15A_RESULTS.md`

### M15B_literal_enrichment — grade A

- **Classification/input:** locked direct-row enrichment. Real fixed age/sex/race/BMI rows; three originals/two recruitment populations plus supplements and assisted retrieval; urate wholly withheld.
- **Actual scale:** One literal200-cell author;50/group;24 endpoints; one unique table with retained initial/final labels.
- **Comparison:** Measured versus literal urate under same unweighted analysis.
- **Strongest support:** Literal evidence-informed values support a close adjusted BMI effect and negative curvature in one reserved finite sample.
- **Numbers:** BMI real0.335316 versus0.345446; quadratic real-0.031676 versus-0.039252; interaction0.049716 versus0.069171.
- **Counterresults:** Age direction wrong:-0.155459 versus+0.069343; all16 group distribution summaries high; reverse slopes attenuated.
- **Inference boundary:** Shape hinge was imposed as assumption, not discovered; intended analysis families disclosed; no repair benefit or national inference; possible cross-task participant overlap.
- **Paper role:** Selected literal-data analytical feasibility with clear failure boundary.
- **Reviewed sources:** `MILESTONE_15B_RESULTS.md`

### M16_literal_repair — grade A

- **Classification/input:** locked direct-row repeatability and repair. Same200 target covariate records and external originals; declared working guide frozen before literal outcomes; no urate answers.
- **Actual scale:** NHANES2017–18 finite200-person equal-quota sample;three fresh builders;four unique table versions;one12-cell repair.
- **Comparison:** Three literal constructions; source/own-guide feedback; B2 initial/final measured-reference utility.
- **Strongest support:** All three literal tables retain positive BMI/negative quadratic direction; one auditable direct repair improves BMI magnitude, all four group SDs, three reverse slopes.
- **Numbers:** B2 BMI discrepancy0.048314→0.018438; standardized-guide deviation SD0.87658→0.99298; beyond2 scales0→10;12/24 errors improve,9 worsen,3 unchanged.
- **Counterresults:** Age direction only2/3; B2 age/curvature/interaction discrepancies worsen; Black-female reverse slope3.545406→2.840129 vs real3.845699; all4 Yun source-SD errors worsen.
- **Inference boundary:** Three contexts one model setup and one cohort; imposed high-BMI attenuation; guide fidelity not biological validity; no universal repair benefit.
- **Paper role:** Strongest true-direct repair demonstration; specific benefit, complete trade-off.
- **Reviewed sources:** `MILESTONE_16_RESULTS.md`

### M17B_evidence_only_complete_cohort — grade A

- **Classification/input:** locked evidence-only full-cohort feasibility. Three external publication populations plus prospective age×sex quota; no individual source or target rows and no target means/coefficients.
- **Actual scale:** Two fresh program authors;three320-row draws each;one newly admitted NHANES2007–08 quota reference n=320;retention duplicates not new outputs.
- **Comparison:** Six unique synthetic cohorts versus measured same-quota reference;eight endpoints.
- **Strongest support:** Selected adjusted BMI, age and sex directions transfer even when every substantive variable is generated.
- **Numbers:** All6 positive BMI/age and negative female; real age0.1485 [0.0694,0.2275], B1 0.1430–0.2098/B2 0.1613–0.1799; real BMI0.2722,B2 0.2561–0.3266.
- **Counterresults:** All6 BMI means below reference; B1 BMI effect0.3083–0.4684; forward/reverse trade-offs; curvature/interaction unresolved; both retain, zero repair gain.
- **Inference boundary:** Two similar bivariate-lognormal families; literature/assumption relationship transfer not discovery; finite standardized sample not national truth; program route, not literal rows.
- **Paper role:** Most direct historical evidence-only scientific-use support, with no superiority or general equivalence.
- **Reviewed sources:** `MILESTONE_17B_RESULTS.md`

## Duplicate, engineering and review exclusions

M1/M2/M12-A/B/C/M17-A are engineering evidence. M3's fictional component is separate from its realTG experiment. M4 is source-only reuse with no new target run. M6 is a deliberately constructed sensitivity proof. M7/M9/M14-A provide evidence audit/preparation, not new target results. M13-A is source-only and M13-B supplies the later measured endpoint. M15-A has one unique table despite two freezes; M15-B is one table; M16 has four unique versions, not six independent stage records; M17-B has six unique analytical tables despite twelve initial/final entries.

The Ross route analysis-utility replay and expanded completion replay reuse frozen existing cohorts; their extra analyses do not create new people or constructions. The exploratory uncertainty follow-up and joint-evidence/actual-paper revisions are exposed-target development. External model-review directories contain research opinions, not independent clinical confirmations. GitHub export/mirror and review-preparation copies were excluded. Unrelated skin, omics and exercise-mechanism projects were excluded; the Queen's exercise cohort remains included because it is explicitly a virtual-data transfer experiment.

## Recommended positive framing

“Across historical feasibility experiments, evidence-conditioned virtual data preserved selected analytical relationships, supported a later-cycle prediction task, and provided executable complete-cohort, enrichment and missing-cell routes. Directly authored rows and source-guided local repair were both demonstrated. The useful scope depended on the information supplied and the analysis: reconstruction, individual-cell accuracy, source fit and downstream inference did not consistently improve together.”

Do not convert that into “better than real data,” “all experiments succeeded,” “no measured data needed,” “patient-level recovery,” “calibrated scientific equivalence,” “autonomous end-to-end literature discovery in every experiment,” or “measured recruitment savings.”

