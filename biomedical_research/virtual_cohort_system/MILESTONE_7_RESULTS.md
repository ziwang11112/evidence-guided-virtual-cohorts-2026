# M7 — Analysis-specific evidence mapping and a justified retention decision

29 October 2026. This milestone implements and exercises evidence declarations and review. It does **not** report improved virtual-data accuracy: no new study generator, source replay or target evaluation was run. Invented software test fixtures are separate from this scientific execution count.

## Outcome

The source-only Agent found relevant joint evidence for age, BMI, sex and triglycerides (TG). It also identified reasons why the retrieved numbers cannot directly calibrate the current generator. Its recommendation was to retain the scientific generator unchanged. The controller accepted that recommendation and kept a newly prepared real-data evaluation locked.

The implemented outcome is a traceable decision: **additional evidence changes what we know about the model's limitations without automatically changing its coefficients.** This is useful framework behavior, not proof that our method outperforms ordinary Agents or other generators.

## What changed in the system

An optional `analysis_evidence.json` now records each requested analytical use, its estimand, linked source evidence, assumptions, differences and unresolved gaps. The manifest distinguishes outcome, exposure, conditioning variables, adjustment, scale, units, population, measurement and selection. It records planned or unavailable retrieval actions without claiming those actions ran.

The checks are integrated into both command-line validation and lifecycle freezing/verification. This prevents a caller from bypassing the new checks by invoking freeze directly. The map is immutable after freeze and cannot serve as the auxiliary result artifact for a claimed computed check. Existing candidates without the optional map remain supported.

The validator rejects unknown evidence/assumption references, incompatible declared statistic matches, omitted explanations for declared differences, and unsupported confidence fields. It does not infer scientific validity from matching variable names or successful code execution. Labels such as `partial` and `transported` remain Agent declarations, subject to substantive review. It cannot prove that every intended analysis or model dependency was listed.

See [schema and complete example](docs/ANALYSIS_EVIDENCE.md) and [implementation](cohort_harness/analysis_evidence.py).

## What the evidence search actually found

The researcher used six search queries and inspected primary sources. It had no new target outcomes or previous target results. The search was directed toward a specified analytical gap; the machine-readable maps were prepared after retrieval. This is **not** evidence that a preregistered map autonomously selected a successful search, nor a standalone model/API launcher.

| Source | Useful evidence | Why it did not justify an immediate coefficient update |
|---|---|---|
| Mikkelsen et al., 2023, Tromsø7 | Sex-specific models using 15 joint age–BMI categories; interaction tests reported in the main text | The 28 nonreference ratios and their intervals are in a supplement that the bounded retrieval did not obtain. Samples were nonfasting; estimates are adjusted, back-transformed log effects. They are not unadjusted arithmetic cell means. |
| Zhang et al., 2026, China-PAR | Six exact BMI–TG coefficients and CIs: overall and before/after the age-54 crossing, separately by sex | These are longitudinal mixed-model effects per **one SD of BMI**. The exact standardization denominator is unresolved, and the adjustment set includes variables unavailable in the current generator. Direct conversion to a cross-sectional slope per kg/m² is unjustified. |

For China-PAR, the before/after estimates are 29.98/17.53 mg/dL per SD in men and 17.96/13.63 in women. They support investigating age-dependent BMI associations. Using their ratios as target slope multipliers would additionally assume comparable standardization, adjustment, study design and population transport. That would be a hypothesis-transfer sensitivity, not source-calibrated improvement. We did not run it merely to create a second numerical result.

For Tromsø, P<0.001 in women supplies no interaction magnitude, while P=0.32 in men does not establish zero interaction. Conflicting male model counts in text and a figure caption are retained as unresolved. Failed supplement downloads are logged and are not registered as scientific evidence. The bounded search does not establish that suitable joint evidence is absent.

Sources: [Tromsø primary paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC10308115/), [China-PAR primary paper](https://www.jacc.org/doi/10.1016/j.jacasi.2026.01.013). Exact retrieval URLs, locators, units, uncertainty and artifact hashes are in the curated research records.

## Retention is a scientific decision, not an execution failure

The inherited baseline uses only the original Oh/Bansal evidence. The evidence-augmented candidate adds the newly reviewed source records and their analysis-specific limitations. Its generator program and model specification remain byte-identical to the baseline; the revision is explicitly `retain`. This does not endorse the baseline's existing fit or transport assumptions.

Because the specification is deliberately preserved, its historical descriptions still mention ages 20–79, the former `LBXTLG` target and previous seed schedules. Those are inherited provenance, not current M7 task instructions. The new task uses ages 40–79 and the `LBXTR` reference, and authorizes no scientific execution in this milestone. These distinctions are stated in the retained candidate's decision record.

Both candidates receive structured maps for the requested age association, BMI curvature and joint subgroup means. The new publications provide partial evidence; they do not identify the full target joint distribution. No interaction coefficient, standardization denominator, source covariance or missing supplementary value was invented. The retention decision and actual research/check artifacts are preserved separately from scientific parameters.

No new source feedback, synthetic cohort, target coefficient, target direction or downstream success score was produced. The unchanged model was not run twice and presented as an improvement comparison.

## New real-data test remains reserved

A separate custodian prepared **1,575 NHANES 2009–2010 participants aged 40–79**. The builder input exposes only opaque identifiers, age, sex, BMI and a measurement-context token. Real TG values and survey design stay with the custodian. The age range was selected from source applicability before outcome analysis, not from a favorable target result.

Eligibility uses the morning examination, 8.5 to <24 hours fasting and positive fasting-subsample `WTSAF2YR`. The reference outcome is glycerol-blanked `LBXTR`, not the separate standard-biochemistry TG variable. The `legacy_proxy` token is a documented measurement approximation, not proof that all source assays are interchangeable. [CDC TG documentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2009/DataFiles/TRIGLY_F.htm).

Preparation QA caught an incorrect morning-session code in the first attempt, which selected zero eligible rows. The original attempt is retained. The code was corrected to `PHDSESN=0`, explicitly amended and frozen again before any target association or distribution was computed. The custodian necessarily parsed outcomes for availability/positivity and unit checks; “reserved” does not mean that no software ever read the TG column. It means no target analytical answers were released or used to design the generator. [CDC fasting-questionnaire codebook](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2009/DataFiles/FASTQX_F.htm).

The planned evaluator covers weighted associations/curvature, all joint subgroup summaries and ordered BMI contrasts. Reserved threshold analyses would be applied to both generated and real data after release; they are excluded from builder feedback. They have **not** been evaluated in M7. This is an unused period according to the recorded local audit, not a new independent study or protection from LLM pretraining.

## Validation and limits

The complete harness suite passed **302 tests**, with **one existing Windows symlink-permission skip**. This validates contracts and execution infrastructure using fixtures; it does not establish biological performance. The test receipt binds the tested source files. Independent custody review checked methods, preparation provenance and hash integrity without parsing participant rows.

That review identified work required before a future evaluation release: the global-model rank-failure path currently aborts rather than recording nonestimability, and the phrase “target-only” should be clarified to mean evaluation-only. Positive subgroup means/proportions must not be counted as evidence of directional fidelity. The frozen custody files are preserved; these issues do not create a target result or justify opening the holdout now.

Source retrieval and construction used procedural role separation. The outer Agents' general tools were not OS-isolated. There is no new demonstration of autonomous research superiority, calibrated source compatibility, clinical usefulness, individual measurement recovery or reduced patient-collection cost.

The inspection package excludes participant rows, source-context rows, full papers, runtime settings and caches. Original frozen files stay local. Path normalization in copies is recorded using original and copied hashes; the reduced package is not a one-command replay archive.

## Next discriminating experiment

Obtain an exact, interpretable joint-statistic table or a compatible conditional-effect model with the necessary scaling and adjustment information. Have the Agent explain how it constrains the requested target analyses and which assumptions remain. Only then freeze a justified generator revision and run the reserved real-data comparison. Retain every predeclared endpoint and seed, including worsened results; do not feed those target answers back into this candidate.

This stage establishes a more inspectable decision process. Whether it improves the unprovided scientific conclusions remains an open experimental question.

See [curated inspection package](reports/analysis_evidence_gap_2026-10-29/README.md) and [validation manifest](m7_validation.json).
