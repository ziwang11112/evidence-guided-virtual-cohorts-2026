# Independent postrun audit

Status: **passed for the audited implementation, release chronology, aggregate arithmetic and report consistency; no blocking issue identified.** The source-stage section was drafted before the reviewer received target aggregate results and was completed with the released aggregate results afterward. No participant-row table, hidden outcome table, or generated-row CSV was read by this audit. No generator was executed, no target fit was rerun, and no frozen candidate, guard, controller, or method was changed. This is an audit of the retained record and reported results, not a certification of general scientific validity.

The two primary directions agree across all 15 frozen target outputs. That agreement coexists with source-fit discrepancies, systematically excessive adjusted BMI effects, substantially understated raw curvature in S1, and an unresolved BMI-by-sex interaction. These limitations are retained below rather than hidden by a winner selection.

## Source fit and revision trade-offs

The source feedback does not establish an across-the-board improvement or a source-compatible winner. S1's revision substantially reduced excessive BMI dependence in the Bansal context while worsening TG location and category-fraction agreement. S2 retains unresolved BMI-dependence discrepancies. S3 remains an explicitly source-challenged mixture parameterization; good agreement with some Oh moments does not repair its central-distribution mismatch in Bansal.

All six initial/final candidates completed the fixed three-seed source schedule: **18 replay reports and 36 source-context executions**. Every candidate has the same 46 diagnostics: **12 fixed-input age/BMI checks and 34 TG-dependent checks**. The input checks confirm the declared covariate reconstruction, not TG generation. The 23 unsupported/ambiguous statistics remain retained rather than silently substituted; two further evidence entries describe assay context. Repeated statistics, publications, and seeds are not independent clinical confirmations.

The table reports means across the three scheduled generator seeds. Units remain those of each statistic; no mixed-unit score or ranking is calculated. Full seed ranges for every check are preserved in [the complete diagnostic table](review/COMPLETE_SOURCE_DIAGNOSTICS.md) and [machine-readable audit](review/source_diagnostic_review.json).

| Source diagnostic | Reported | S1 final | S2 retained | S3 retained |
|---|---:|---:|---:|---:|
| Oh TG mean, men / women (mg/dL) | 141.6 / 97.2 | 141.253 / 97.193 | 140.171 / 95.734 | 142.026 / 97.098 |
| Oh TG SD, men / women (mg/dL) | 107.7 / 61.0 | 107.467 / 61.151 | 104.483 / 58.908 | 107.920 / 61.726 |
| Oh BMI OLS slope (mg/dL per kg/m²) | 6.813 | 6.840 | 6.274 | 5.764 |
| Bansal Q25 / median / Q75 (mg/dL) | 81 / 115 / 169 | 76.685 / 111.585 / 162.296 | 77.527 / 113.948 / 167.480 | 70.021 / 99.931 / 182.092 |
| Bansal BMI–TG Spearman correlation | 0.33 | 0.3464 | 0.4684 | 0.4607 |
| Bansal age–TG Spearman correlation | 0.18 | 0.1440 | 0.1815 | 0.1418 |
| Bansal BMI mean in TG tertiles 1 / 2 / 3 (kg/m²) | 24.2 / 25.9 / 27.6 | 24.029 / 25.977 / 27.965 | 23.384 / 25.921 / 28.529 | 23.605 / 25.882 / 28.895 |
| Bansal age SD in TG tertiles 1 / 2 / 3 (years) | 6.9 / 7.3 / 7.2 | 6.275 / 7.112 / 8.030 | 6.498 / 7.072 / 7.753 | 6.241 / 7.186 / 8.074 |
| Bansal fraction below first tertile boundary | 0.32757 | 0.35293 | 0.34294 | 0.43836 |

### S1: a targeted change with adverse trade-offs

The BMI Spearman mean moved from 0.43949 to 0.34640 toward 0.33, with final values 0.34570–0.34736. The first/third TG-tertile BMI means moved from 23.4466/28.3857 to 24.0289/27.9647, toward 24.2/27.6. These absolute discrepancies decreased in every paired seed, although the final dependence remains stronger than the reported source relationship.

The adverse location trade-off anticipated in the revision decision occurred. Q25/median/Q75 moved from 79.039/115.560/168.450 to 76.685/111.585/162.296, against 81/115/169. **Each of the three quantiles worsened in every paired seed.** Both cumulative tertile fractions and all four cumulative quintile fractions also worsened in every paired seed. The lower female BMI response therefore improved an association diagnostic without preserving all marginal-distribution diagnostics.

Oh sex-specific means and SDs remained near their anchors, but the pooled OLS mean changed from 6.83398 to 6.84006 rather than becoming exactly 6.813. This is consistent with the documented approximate moment/slope algebra, soft mean regularization, and finite constructed covariates. Oh threshold discrepancies remain; the male fractions below 150 and 200 mg/dL worsened in each paired draw, while the female fraction below 150 improved. The female extreme-tail discrepancy worsened, but the corresponding published tail count is only one person and is not a precise calibration target.

Age Spearman moved modestly from 0.14033 to 0.14405 with unchanged age coefficients and remains below 0.18. Reverse-conditional age SDs remain too small in the lower TG tertile and too large in the upper tertile. These changes show how a BMI/noise revision can alter rank and reverse-conditional diagnostics without changing the age slope itself.

### S2 and S3: reproducible retention is not compatibility

S2's age rank and TG quantiles are comparatively close to their source values, but BMI Spearman remains 0.46836 rather than 0.33 and the extreme-tertile BMI means remain too separated. Oh moments and its OLS slope are low; category fractions and conditional age/BMI spreads also retain discrepancies. No numerical compatibility pass is warranted merely because the program was retained.

S3 reproduces Oh means and SDs reasonably at this descriptive scale but has a lower pooled BMI slope, differing category shapes, and a substantial Bansal distribution mismatch. Its first-tertile fraction is 0.43836 versus 0.32757; its median is about 99.93 versus 115, while Q75 is about 182.09 versus 169. Its BMI dependence is too strong, and its lower/upper-tertile age spreads disagree. These findings challenge this parameterization, not every possible latent mixture.

For s2 and s3, all **12 paired source-context generated-output hashes** match between initial and final stages: two structures × three seeds × two contexts. All **276 per-seed diagnostic records** also match exactly. This confirms deterministic replay under unchanged code/specification, covariates, and seeds. It does not constitute new independent validation evidence.

## Source commitment and chronology checks

The independently inspected `structure_plan_commitment.json` matches the current structure-plan hash, original three initial freeze hashes, and protocol hash. Its SHA-256 is `312af733500e3830fec76e59503ea57d37c9978eefde4223b339d2689ed1508e`. Recorded UTC ordering is consistent:

- Last initial freeze: 2026-10-29 00:51:02.293599.
- Structure-plan commitment: 00:51:34.573941.
- First initial source execution: 00:51:37.203741.
- Last initial source report: 00:54:46.995876.
- First/last final freezes: 01:07:40.903983 / 01:07:42.864067.
- First final source execution: 01:08:24.234516.
- Last final source report: 01:11:36.223629.

Thus all initial structures were frozen before initial replay, the plan commitment preceded those executions, all initial feedback preceded final freezes, and all final structures were frozen before final replay. Hashes and timestamps authenticate consistency of the retained procedural record, not an adversarial host or external timestamp authority.

This independent audit checked every portfolio's seed schedule, check count/classification, summary arithmetic, paired absolute-discrepancy arithmetic, report hashes, source-context execution-receipt hashes, status/seed/candidate bindings, and output-hash linkage recorded in those receipts. It did **not** recompute operators from row tables. The controller's harness verification supplies that row-level computation linkage; this audit remained aggregate-only. The reproducible metadata audit script is [audit_source_metadata.py](review/audit_source_metadata.py).

## Limits on source and structural interpretation

The 160,320-row Oh and 80,472-row Bansal source contexts are numerical integration/Monte Carlo constructions, not enlarged clinical cohorts. Their seed ranges exclude evidence uncertainty, unknown source joint covariates, model structure, assay transfer, and target transport. Small seed variation cannot establish that a source discrepancy is statistically significant relative to the original study. No numerical acceptance tolerance or calibrated source-compatibility test was prespecified.

The three alternatives share positive BMI effects, selected opposite sex-specific age trends, source-context independence assumptions, measurement transfer, and restricted functional geometries. Agreement in a target endpoint can support robustness within this set, not identification of a unique curve or agreement across every source-compatible law. S3's source challenge remains visible alongside its target results. Neither source fitting nor target agreement establishes causal or individual recovery claims.

## Target release and endpoint audit

The release commitment SHA-256 is `f41fd145f0b566d3332419b3f65e78d5e774bc44434c6dc313bd167846ff4f65`. The custodian receipt records a passed guard before the hidden table was parsed. The recorded grid comprises exactly **6 candidate versions, 18 source replays and 15 final target outputs**: three structures, each with an initial and final candidate, three source seeds per candidate, and five target seeds per final candidate. There is no initial-candidate target comparison.

The target part of the chronology follows the completed source stage:

| Event | Recorded UTC, 29 October 2026 |
|---|---|
| Last final source report | 01:11:36.223629 |
| First target execution | 01:19:11.023544 |
| Last target execution recorded end | 01:19:33.966312 |
| Complete output commitment | 01:21:14.478288 |
| Custodian release | 01:24:52.534861 |

Every target execution receipt has the expected successful program route, final candidate/freeze binding, seed and committed output digest; there are exactly 15 target execution directories. The complete source stage precedes all target generation, and all target generation precedes commitment and release. The six final/initial freezes remain unchanged. All **42 frozen scientific files** across the six candidates—program, specification, evidence, source recipes/check definitions and decision records—still match their committed hashes. Frozen custodian methods and analysis protocol also match their lock. There is no evidence in these files or receipts of post-target scientific tuning. Hash stability does not establish what an outer Agent knew or provide independent authentication of the host's clock.

The independently recomputed aggregate checks passed for **180 endpoint rows**, **36 structure summaries**, **12 global endpoint summaries** and **12 reference intervals**. The grids are six endpoints × two measurement scales × three structures × five draws, with five draws in every structure/endpoint/scale summary. All estimates, absolute/signed errors, sign agreements, medians, extrema and reported reference bounds reconcile. All released result-file hashes match their result manifest. There are zero recorded nonestimable sensitivities or omitted draws.

The reference intervals reproduce `estimate ± t(0.975, 15) × SE` from the reported design-based SEs. This verifies interval arithmetic, not the estimator against independent survey software. Earlier invented-fixture checks and frozen-method review address estimator behavior. The audit does not repeat row-level checks or independently refit the reference. Generated rows contain point estimates only, with no generated SE or CI represented in the aggregate endpoint table.

The reproducible [aggregate audit script](review/audit_target_aggregates.py) records the complete checks and all 36 summaries in [target_aggregate_audit.json](review/target_aggregate_audit.json). Its allowlist permits only the two released aggregate CSV filenames and metadata; no participant table is required.

### All native endpoint results

Generated entries below are the median and full min–max range over five fixed-seed draws. Reference brackets are 95% design-based confidence intervals; generated brackets are descriptive simulation ranges and are **not confidence intervals**.

| Endpoint | Reference [95% CI] | S1 median [range] | S2 median [range] | S3 median [range] |
|---|---:|---:|---:|---:|
| Adjusted age, log TG per 10 years | 0.05528 [0.03550, 0.07506] | 0.06208 [0.05420, 0.06588] | 0.06446 [0.05644, 0.06821] | 0.04541 [0.03166, 0.05103] |
| Full-domain BMI curvature, log TG | −0.05366 [−0.06437, −0.04294] | −0.03376 [−0.04377, −0.02497] | −0.04897 [−0.05889, −0.04049] | −0.03580 [−0.05495, −0.03070] |
| Full-domain BMI curvature, raw TG mg/dL | −7.471 [−9.238, −5.704] | −1.876 [−4.047, −1.099] | −6.912 [−8.872, −6.268] | −6.639 [−9.639, −4.906] |
| Adjusted BMI, log TG per 5 kg/m² | 0.08316 [0.06397, 0.10234] | 0.16958 [0.16852, 0.19301] | 0.11783 [0.11618, 0.14093] | 0.15210 [0.14783, 0.15353] |
| Adjusted female versus male, log TG | −0.10994 [−0.15803, −0.06185] | −0.22762 [−0.24923, −0.20088] | −0.09893 [−0.12092, −0.07242] | −0.16617 [−0.17895, −0.12579] |
| BMI×female interaction | −0.02456 [−0.07733, 0.02821] | −0.03179 [−0.07458, 0.00008] | 0.03229 [−0.00965, 0.06451] | −0.02222 [−0.04611, 0.00542] |

Positive adjusted age and negative log curvature occur in all 15 outputs, matching the reference directions. Raw curvature is also negative in all 15. Thus the observed reference's global quadratic contrast is not solely created by logging TG. This does not prove local or universal biological concavity. The endpoint is the full-domain fitted contrast `2 × coefficient(B²)` for `B=(BMI−25)/5`, not a local derivative estimate or an identified complete dose-response curve. On the log scale, its exponential is a ratio of ratios. Within-sex affine raw means can still yield a nonzero global quadratic projection when a common-coefficient fitted basis omits sex-specific BMI/age relationships and reflects the target covariate distribution; S1 also uses positive-mean regularization.

Direction agreement is materially weaker evidence than magnitude agreement. All 15 adjusted BMI estimates exceed the native reference CI upper bound of 0.10234. That is a descriptive discrepancy, not a calibrated two-estimator test. S1's raw-curvature median is −1.876 versus −7.471 and its female contrast is much more negative than the reference. S2's comparatively close target estimates coexist with an excessive source BMI rank relationship. S3's target sign agreement does not repair its source distribution challenge. None of these observations defines an automatic or post-hoc winner.

The interaction is unresolved: nine generated estimates are negative and six positive; negative counts are 4/5 for S1, 1/5 for S2 and 4/5 for S3. Every structure's five-draw range crosses zero, and the reference CI also crosses zero. The result is neither an established null nor a validated interaction sign. This secondary uncertainty remains visible beside the favorable primary directions.

### Assay sensitivity and uncertainty semantics

All 15 outputs and the reference remain estimable under the prespecified CDC backward assay equation. The backward-reference age estimate is 0.06642 [0.04333, 0.08951]; log curvature is −0.06155 [−0.07418, −0.04893]; raw curvature is −7.311 [−9.040, −5.582]. Both primary signs and the raw-curvature sign remain unchanged. The interaction remains nine negative/six positive generated estimates with a reference CI crossing zero.

For an affine outcome transformation with an intercept in the fitted design, the raw-curvature estimate, SE and CI bounds scale by the positive slope. Every raw auxiliary estimate and the reference SE/CI equal **0.9785 × native**, to maximum absolute roundoff `4.64 × 10⁻¹³`. This is mechanical sensitivity to an assay scale, not an independent validation. The additive assay offset affects log analyses, and the two published rounded forward/backward regression equations are not exact inverses. Assay-transfer and bridge-coefficient uncertainty remain unpropagated.

The five target seeds measure residual/state simulation sensitivity for fixed structures and parameters on fixed observed covariates. They are not five independent Agent builds, clinical samples, imputation analyses or calibrated draws over model/evidence/transport uncertainty. The primary result supports temporal directional robustness within these three proposed structures in NHANES 2021–2023, not an independent external-cohort replication or equivalence of real and synthetic data.

Only final structures were evaluated on this target. Source-diagnostic improvement therefore cannot be translated into a claim that S1's revision improved target performance. The released target is now development knowledge; future tuning followed by evaluation on this same target would not be a fresh validation.

## Final report consistency review

The full `MILESTONE_5_RESULTS.md` and the current M5 summary in README v0.5 are consistent with the audited aggregates and source records. All **72 printed numbers** in the native endpoint table independently match their aggregates at the displayed precision. The report correctly retains source trade-offs, S3's source challenge, the global-projection interpretation, all 180 rows/36 summaries, the unresolved interaction, the absence of an initial-target comparison, and the descriptive meaning of the adjusted-BMI/CI discrepancy. No unsupported scientific conclusion or blocking inconsistency was identified in those reviewed versions.

The new-check receipts support 32 invented-record release-guard checks plus 11 custodian gate/estimator checks, or **43 checks**. The 32 gate checks mock core harness verifiers and do not revalidate isolation. The prior 258-passed/1-skipped core-suite result is correctly described as historical and not rerun; this audit did not reopen earlier result reports. The custom survey estimator has not been independently matched to an R survey-package implementation.

The inspected figure has three native panels, shows five generated dots per family, and clearly separates the reference CI from descriptive generated ranges. The full endpoint table retains secondary outcomes omitted from the figure. The [report consistency record](review/report_consistency_review.json) binds these judgments to exact report hashes and is also embedded in the aggregate audit. Export-package completeness and portability are separate controller checks.
