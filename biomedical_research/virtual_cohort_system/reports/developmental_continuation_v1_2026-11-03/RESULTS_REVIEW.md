# Final results interpretation and public-boundary review

Status: **final review complete; no remaining substantive correction or public-content blocker identified in the inspected outputs**. The separately frozen independent target report and completion both record matched status with zero disagreements. Final RESULTS.md, README.md, PUBLIC_COMPLETION_BOUNDARY.md and COMPLETE_AGGREGATE_SUMMARY.json were checked against the primary and independent aggregate reports. This review did not access a row table, run a generator or experiment, rerun an evaluator/test suite, modify a frozen report/script, or operate Git.

The primary evaluation supports a specific, limited glucose-analysis result for A02 while showing failures to recover other requested properties. A02's age/female-adjusted glucose slopes are 0.40923762887134846, 0.4003427318765268 and 0.4234032994239159 %/(mmol/L), compared with the existing reference estimate 0.4020933879135471. This is a useful developmental signal for that projection. It is not evidence of globally high-quality virtual data, clinical utility, equivalence, calibrated inference, or a successful population transfer.

Both constructions give positive BMI and glucose slopes on every seed, but their BMI slope magnitudes are substantially below the reference: A01 0.008833529575779304–0.017409268324776964 and A02 0.020384061293250176–0.02355226134725612, versus 0.05494608227224506 %/(kg/m^2). A01's glucose slopes, 0.21410462305955405–0.22570228865894773, are also materially lower than the reference estimate. The adjusted age slope is not recovered: A01 varies around zero (-0.00042121765600892713 to 0.0009519078143716878), while all A02 values are negative (-0.0003241757603776977 to -0.00011278448971292243), versus the positive reference 0.008107035072072662 %/year. Assumed age/sex independence remains an unsupported modeling choice; these failures do not identify a replacement law.

A02's comparatively close glucose coefficient coexists with glucose SDs of 0.5969020288133411–0.6032337077366374 mmol/L versus 1.544545998346385, and HbA1c SDs of 0.4486961734634304–0.4625346817498349 percentage points versus 0.9535714185781632. Its Pearson correlations (0.533003096755972–0.5523900701500702) are below the reference 0.6609682868544315, while Spearman correlations (0.5151763999084888–0.5318719670968851) exceed the reference 0.36145731918117036. A01's Pearson is much lower (0.3055903183292546–0.32058938348503335), although its Spearman (0.3135983063998118–0.3237500488611165) is closer. Neither recovers both joint diagnostics. A01 additionally shifts BMI and HbA1c locations upward; all five marginal summaries per variable are retained below.

An adjusted regression slope is a ratio of residualized covariance to residualized predictor variance. Different joint distributions can yield a similar ratio. Consequently, agreement of one coefficient can coexist with incorrect variability, dependence, other coefficients and distributional shape. A02 illustrates why a projection-specific usefulness signal must remain separate from a broad data-quality claim. There is no prespecified overall success rule or equivalence margin; reference-interval membership is descriptive only.

## Coverage, paired repeats and uncertainty

All 18 target allocations succeeded, with 3,000 rows per allocation and no failed/unrun target slots. There are six distinct output hashes: one per constructor/seed. For each constructor/seed, initial, self_review and source_feedback have identical output hashes, complete analyses and generated-only diagnostics. The six profiles below therefore report all 18 allocations without treating repeated retained versions as independent constructions. All four actual branch decisions were retain. Every reported self-review-minus-initial, feedback-minus-initial and feedback-minus-self-review mean-absolute-discrepancy change is exactly 0.0 for all three endpoints and both constructors. The identical per-seed outputs also imply zero paired coefficient and diagnostic changes. This is no observed revision gain under this bounded protocol, not evidence that feedback never helps or that the methods are generally equivalent.

The two constructions remain the scientific units. Repeated seeds describe conditional generator variation, not additional clinical samples or independent model inventions. The 54 successful source allocations and 72 independently checked qualified source comparisons establish source-statistic implementation agreement (maximum absolute arithmetic discrepancy 3.3306690738754696e-16), not adequate source fit. Original strict source replay remains unavailable.

The existing CHNS reference is researcher-exposed developmental evidence, not an untouched confirmation cohort or a nationally representative population truth. Its common complete-case analytical sample has n=6,631 and 218 communities. Reference clustered intervals describe reference-sample uncertainty; generated analyses have point estimates and explicitly unavailable inference intervals. No patient reference decoding occurred in this unit. Source uncertainty, seed variation, reference uncertainty and transport assumptions must remain distinct.

## All endpoint estimates

E1: HbA1c on age/female/BMI, focal BMI, %/(kg/m^2). E2: HbA1c on age/female/glucose, focal glucose, %/(mmol/L). E3: HbA1c on female/BMI/glucose/age, focal age, %/year. All include an intercept. Values below retain the numeric precision serialized in the primary report.

| Constructor | Seed | Versions sharing this exact profile | E1 BMI | E2 glucose | E3 age |
|---|---:|---|---:|---:|---:|
| A01 | 41911 | initial; self_review; source_feedback | 0.011374143109382217 | 0.22570228865894773 | -0.00042121765600892713 |
| A01 | 41912 | initial; self_review; source_feedback | 0.008833529575779304 | 0.21410462305955405 | 0.0009519078143716878 |
| A01 | 41913 | initial; self_review; source_feedback | 0.017409268324776964 | 0.22393799467564288 | 0.0002478210307739126 |
| A02 | 41911 | initial; self_review; source_feedback | 0.02355226134725612 | 0.40923762887134846 | -0.00011278448971292243 |
| A02 | 41912 | initial; self_review; source_feedback | 0.020384061293250176 | 0.4003427318765268 | -0.00011717915797132016 |
| A02 | 41913 | initial; self_review; source_feedback | 0.022047201094015086 | 0.4234032994239159 | -0.0003241757603776977 |

| Reference endpoint | Point estimate | Clustered interval lower | Clustered interval upper |
|---|---:|---:|---:|
| E1 | 0.05494608227224506 | 0.04572624759489867 | 0.06416591694959145 |
| E2 | 0.4020933879135471 | 0.37128635859620074 | 0.43290041723089345 |
| E3 | 0.008107035072072662 | 0.006387035326816245 | 0.00982703481732908 |

All generated E1/E2 designs have rank 4 and E3 rank 5. All generated intervals remain unavailable with reason `generated_no_inference`. An interval containing a generated point does not constitute equivalence or account for generated-data inference.

## All 27 reference-comparable diagnostics

Each constructor table contains all 25 marginal diagnostics (mean, SD, q10, median, q90 for age, female, BMI, glucose and HbA1c) plus the glucose–HbA1c Pearson and Spearman correlations, at every seed. Each seed column applies identically to all three retained versions. Female mean is a fraction; other marginal units follow the variable's native analysis scale. These are descriptive profiles, not 27 independent validation tests.

### A01

| Diagnostic | CHNS reference | Seed 41911 | Seed 41912 | Seed 41913 |
|---|---:|---:|---:|---:|
| marginal.age.mean | 52.742572764288944 | 54.731 | 54.75833333333333 | 54.343333333333334 |
| marginal.age.sd | 10.4317907463803 | 11.364903255578973 | 11.607361493286671 | 11.539779506526196 |
| marginal.age.q10 | 39.0 | 39.0 | 39.0 | 38.0 |
| marginal.age.median | 53.0 | 55.0 | 55.0 | 55.0 |
| marginal.age.q90 | 68.0 | 70.0 | 71.0 | 70.0 |
| marginal.female.mean | 0.5368722666264515 | 0.5003333333333333 | 0.49766666666666665 | 0.509 |
| marginal.female.sd | 0.49867618579798456 | 0.5000832430428087 | 0.5000779087907293 | 0.5000023341059224 |
| marginal.female.q10 | 0.0 | 0.0 | 0.0 | 0.0 |
| marginal.female.median | 1.0 | 1.0 | 0.0 | 1.0 |
| marginal.female.q90 | 1.0 | 1.0 | 1.0 | 1.0 |
| marginal.bmi.mean | 23.69988843402959 | 25.029715124500168 | 25.01096269405513 | 25.014960352130373 |
| marginal.bmi.sd | 3.40632238200595 | 3.595695658749072 | 3.5811584459385544 | 3.678751211606073 |
| marginal.bmi.q10 | 19.531249999999996 | 21.048991675756536 | 20.978052273734644 | 20.983762531536218 |
| marginal.bmi.median | 23.423986359981807 | 24.468667660735896 | 24.462098935323077 | 24.366883182314986 |
| marginal.bmi.q90 | 28.100957027584915 | 29.698945543131344 | 29.80075842903753 | 30.060786200249108 |
| marginal.glucose.mean | 5.487767606695823 | 5.214858523728644 | 5.184001231985193 | 5.241824628992843 |
| marginal.glucose.sd | 1.544545998346385 | 1.401839755006524 | 1.4095407876984334 | 1.420734684461714 |
| marginal.glucose.q10 | 4.4190000000000005 | 3.5601990795631355 | 3.582945265987012 | 3.637242151864951 |
| marginal.glucose.median | 5.17 | 5.037446725778057 | 4.967868358008601 | 5.032082354671134 |
| marginal.glucose.q90 | 6.579 | 7.151876223822763 | 7.082516649290045 | 7.1008352547178335 |
| marginal.hba1c.mean | 5.675312924144171 | 6.101395404161233 | 6.07464358212622 | 6.0738455004917995 |
| marginal.hba1c.sd | 0.9535714185781632 | 1.010235421051454 | 0.9889403529921763 | 0.9926738523293497 |
| marginal.hba1c.q10 | 5.0 | 4.941579679278788 | 4.947000414637622 | 4.939676540837001 |
| marginal.hba1c.median | 5.5 | 5.978767341326268 | 5.9326632869618665 | 5.945332499395612 |
| marginal.hba1c.q90 | 6.3 | 7.420402497346467 | 7.388601973488154 | 7.356918978374974 |
| joint.pearson | 0.6609682868544315 | 0.3131602582393366 | 0.3055903183292546 | 0.32058938348503335 |
| joint.spearman | 0.36145731918117036 | 0.3237500488611165 | 0.3135983063998118 | 0.3197406168600685 |

### A02

| Diagnostic | CHNS reference | Seed 41911 | Seed 41912 | Seed 41913 |
|---|---:|---:|---:|---:|
| marginal.age.mean | 52.742572764288944 | 54.922 | 54.595666666666666 | 54.512 |
| marginal.age.sd | 10.4317907463803 | 11.405581020980126 | 11.581661921035913 | 11.511531658314347 |
| marginal.age.q10 | 39.0 | 39.0 | 38.0 | 38.0 |
| marginal.age.median | 53.0 | 55.0 | 55.0 | 55.0 |
| marginal.age.q90 | 68.0 | 71.0 | 70.0 | 70.0 |
| marginal.female.mean | 0.5368722666264515 | 0.4876666666666667 | 0.498 | 0.5046666666666667 |
| marginal.female.sd | 0.49867618579798456 | 0.49993119455446244 | 0.5000793534896192 | 0.500061572289769 |
| marginal.female.q10 | 0.0 | 0.0 | 0.0 | 0.0 |
| marginal.female.median | 1.0 | 0.0 | 0.0 | 1.0 |
| marginal.female.q90 | 1.0 | 1.0 | 1.0 | 1.0 |
| marginal.bmi.mean | 23.69988843402959 | 23.715480749613043 | 23.74022637731325 | 23.841704162135546 |
| marginal.bmi.sd | 3.40632238200595 | 3.294177782309986 | 3.289199194276674 | 3.405097661829057 |
| marginal.bmi.q10 | 19.531249999999996 | 19.72404140104991 | 19.745335403186708 | 19.776881640246298 |
| marginal.bmi.median | 23.423986359981807 | 23.48505943847212 | 23.524516366853902 | 23.56724788136458 |
| marginal.bmi.q90 | 28.100957027584915 | 28.01959467573053 | 28.019134629457735 | 28.373726923944627 |
| marginal.glucose.mean | 5.487767606695823 | 5.238335845593296 | 5.228341790570987 | 5.249883529876637 |
| marginal.glucose.sd | 1.544545998346385 | 0.6022661956449308 | 0.5969020288133411 | 0.6032337077366374 |
| marginal.glucose.q10 | 4.4190000000000005 | 4.493273729603203 | 4.49341928224108 | 4.513348479839681 |
| marginal.glucose.median | 5.17 | 5.212294009846023 | 5.199565779827016 | 5.212293948984636 |
| marginal.glucose.q90 | 6.579 | 6.025920643098836 | 6.005697771074336 | 6.026609469789633 |
| marginal.hba1c.mean | 5.675312924144171 | 5.642161143465341 | 5.626230557102532 | 5.6321166042431505 |
| marginal.hba1c.sd | 0.9535714185781632 | 0.4540669906918887 | 0.4486961734634304 | 0.4625346817498349 |
| marginal.hba1c.q10 | 5.0 | 5.067622493402425 | 5.079247626126794 | 5.047084888355055 |
| marginal.hba1c.median | 5.5 | 5.615876373803718 | 5.590530696850511 | 5.600749801581841 |
| marginal.hba1c.q90 | 6.3 | 6.2582128020233485 | 6.216534699382113 | 6.239390828864402 |
| joint.pearson | 0.6609682868544315 | 0.5428021219261437 | 0.533003096755972 | 0.5523900701500702 |
| joint.spearman | 0.36145731918117036 | 0.5318719670968851 | 0.5151763999084888 | 0.5238907306545255 |

## Generated-only checks and publication boundary

All 18 allocations report zero duplicate rows after the first, nonfinite values, domain violations, fractional-age rows and invalid rows. Their tail quantiles, all pairwise Pearson correlations and design diagnostics remain available in the aggregate report. They have no added reference counterpart (`generated_only_reference_unavailable`); they must not be presented as demonstrated tail fidelity or validation of omitted joint relationships. Zero numerical/format violations establish admissibility of these tables, not biomedical validity.

The primary REPORT.json and COMPLETION.json were inspected as aggregate artifacts. REPORT.json's byte hash matches COMPLETION.json. Recursive inspection found no participant row identifiers, individual records, long individual-value arrays, credential keys with values, private-key blocks or recognized credential-token payloads. The 36 dictionaries resembling numeric clinical tuples are exclusively the 18 per-variable nonfinite-count dictionaries and 18 per-variable domain-violation-count dictionaries; all entries are aggregate zeros. Reference linkage/missingness/cleaning counts, marginal/joint summaries, coefficients and uncertainty estimates are aggregates. Local paths, source file basenames and hashes are provenance, not embedded file contents.

There is no row-content or credential blocker to a coordinator-selected aggregate export of these reports. This review does not authorize following local paths or copying their referents. Reference participant files, generated row tables, raw execution directories, live ledgers and credentials remain excluded. The pre-target whitelist stays unchanged; target aggregate reports and final review/result documents require explicit additions. The completed independent report and final RESULTS.md consistency checks now support the stated numerical-verification claim. They do not establish scientific adequacy, equivalence or transport validity.

## Binding scope and completed verification

The source audit's `release_sha256` is a raw byte hash of its RELEASE.json input; the controller report's same-named field identifies canonical full-release JSON. The approved review-excluding release digest has a third defined scope. Their different values are encoding/scope differences, not evidence of different scientific releases. Preserve these historical fields unchanged and label their scopes when presenting them.

- Primary REPORT.json raw SHA-256: `ba6cab2cefd4e63c8320dc23d60ad09d5c9e8c57da82d041ff837366639bf903`.
- Controller canonical full-release SHA-256: `5f590c178fb8f9ca015e9d8b7f997ca452c41e2a4ec2c85f8eb93847708a3f02`.
- Source-audit raw RELEASE.json byte SHA-256: `8656ff97b42def9f78a3a6155cff58e2b5e17597a06666e1f7e081905e727b2a`.
- Approved review-excluding release digest: `3d3d8f25f2558d0cdb64ff6e5466c64fc98030f9706f3d6a9ad4c16cb51cc343`.
- Scientific freeze: `9d59d7b4eb852c8599de24632d5438dd79d5f596e8edd25eaf67635f255ee1c5`.
- Closed inventory: `b9cd799467f2a4810562de4514b7c4307ef78c6c1b5db6431263d807a03a437c`; matches CLOSED_INVENTORY.json metadata.


## Final report, rendering and cost checks

The actual independent COMPLETION.json binds the independent REPORT.json, which binds the same primary report inspected above. Status is `matched`, disagreements are empty, and 18 target profiles were recomputed by the frozen independent entry point. Its recorded method is independent CSV parsing, QR regression, manual moments/linear quantiles, SciPy correlations and independent paired arithmetic; its tolerances are relative 1e-8 and absolute 1e-10 for arithmetic agreement only. Reference uncertainty was reused from the frozen aggregate, not reestimated. This reviewer verified the completed aggregate artifacts and their links; it did not rerun that entry point or read its input rows. The primary report's historical `pending` field remains unchanged and is superseded for current verification status by the bound independent completion/report.

The complete rendered summary preserves all 18 primary target-slot records, all endpoint summaries and changes, the reference aggregate, scientific annotations and all 72 closed allocation dispositions exactly. All 54 endpoint estimate/comparison/support records, all 486 reference-comparable diagnostic seed values with their ranges, and all 18 generated-only/design diagnostic profiles were checked against the primary report. All 27 displayed diagnostic rows, all four source-statistic rows and all three endpoint rows in RESULTS.md match the underlying aggregates at the displayed precision. The reference interval widths agree with the reported clustered standard errors and 217-degree-of-freedom two-sided 95% t convention; no uncertainty was reestimated.

Count claims are consistent: 54 source and 18 target allocations, 18 source and six target distinct output hashes, 24 distinct hashes overall, and 3,000 rows per allocation. The 162,000 source and 54,000 target virtual row-slots are accounting totals, not independent clinical observations. All four branch decisions were retention; the 18 reported branch/endpoint discrepancy-change summaries are zero and there is no revision gain. Positive directions, low BMI magnitudes, unrecovered age associations, the A02 glucose-projection agreement and marginal/joint failures are all represented. RESULTS.md and README.md do not claim source-to-target equivalence, global data recovery, general method superiority, a matched old-versus-new advantage or an independent confirmatory CHNS result.

The six measured target-dispatch wall times sum to 4459.530000000028 seconds (reported as 4459.530 seconds or 74.33 minutes); the 18 adapter elapsed times sum to 15.687 seconds. Every cost receipt hash matches the corresponding primary target-slot receipt hash. These checks use the measured cost summary and report metadata, not reopened execution receipts or row tables. The stated exclusions of source work, global closure, evaluation, author/reviewer time and unavailable model tokens are retained. The two are different scopes; their gap is not an instrumented CPU profile or proof of achieved savings. The earlier unsupported adjective 'avoidable' was removed; the final report says potential reductions were not measured.

Publication-content inspection covered primary and independent aggregate reports/completions, the complete aggregate summary, RESULTS.md, TARGET_EXECUTION_COST.json, README.md, PUBLIC_COMPLETION_BOUNDARY.md, both SVGs and both captions. No individual rows, long individual-value arrays, credential-value payloads or embedded CSV/binary-data attachments were identified. Numeric clinical-key dictionaries are per-variable aggregate quality counts. SVGs contain no scripts, foreign objects or embedded images. PNG metadata contains only software, DPI and short aggregate-figure descriptions (including one input hash). The target PNG/SVG/caption hashes match the rendered summary. Visual clarity was checked separately by the coordinator; this reviewer checked aggregate content and metadata. Paths/hashes remain provenance, not authorization to export their referents.

Two wording corrections were requested and applied to the final prose: source diagnostics are described as qualified equal-weight source-context point comparisons, and potential orchestration savings are not presented as measured. No remaining substantive correction was identified. No new draw, reanalysis, method experiment or test-suite execution was needed.

### Exact final input bindings

- Primary report: `ba6cab2cefd4e63c8320dc23d60ad09d5c9e8c57da82d041ff837366639bf903` (`D:\AIR-014_ECRC_Paper_Clean_2026-08-16\evcDC\ledger\evaluation\REPORT.json`).
- Primary completion: `baa469dd53a7da3e0c19b9d896ca4608a24625699354ee5515424af256fd74ce` (`D:\AIR-014_ECRC_Paper_Clean_2026-08-16\evcDC\ledger\evaluation\COMPLETION.json`).
- Independent report: `ac93f42b75253c5facdd8b9325fb92fb1f7863e7c7e15ecb90eb3887b803e79b` (`D:\AIR-014_ECRC_Paper_Clean_2026-08-16\evcDC\ledger\independent_evaluation\REPORT.json`).
- Independent completion: `7710d71632f05df7c21016127105ad3d326c9dfe0bdbdbc079dadab854ae6e8f` (`D:\AIR-014_ECRC_Paper_Clean_2026-08-16\evcDC\ledger\independent_evaluation\COMPLETION.json`).
- Complete aggregate summary: `a986c16e9633e2e6f9ff4d164774ba656621f395d0653bed2340a04efaeff6a1` (`D:\AIR-014_ECRC_Paper_Clean_2026-08-16\biomedical_research\virtual_cohort_system\work\developmental_continuation_v1_2026-11-03\COMPLETE_AGGREGATE_SUMMARY.json`).
- Final results prose: `a4bd616424d3fc54dcb9c194138021bfcb1c3375648037f10e756a398edb294b` (`D:\AIR-014_ECRC_Paper_Clean_2026-08-16\biomedical_research\virtual_cohort_system\work\developmental_continuation_v1_2026-11-03\RESULTS.md`).
- Target cost summary: `851d71e8476adb87524cbd7235a0fd4548919f504df2b1cd0f4a759a26a8a01c` (`D:\AIR-014_ECRC_Paper_Clean_2026-08-16\biomedical_research\virtual_cohort_system\work\developmental_continuation_v1_2026-11-03\TARGET_EXECUTION_COST.json`).
- README: `d64d28435475b8f7d8395dd895488dff07b99d46097beac4c24c7ab78549efa5` (`D:\AIR-014_ECRC_Paper_Clean_2026-08-16\biomedical_research\virtual_cohort_system\work\developmental_continuation_v1_2026-11-03\README.md`).
- Completed-result publication boundary: `fa6047a94dc3e59b0713080fb4e407107c8d7d41601b64acee9e3bae44fa3249` (`D:\AIR-014_ECRC_Paper_Clean_2026-08-16\biomedical_research\virtual_cohort_system\work\developmental_continuation_v1_2026-11-03\PUBLIC_COMPLETION_BOUNDARY.md`).

Finalized 2026-11-03T08:53:49.410105+00:00. These conclusions bind the inspected file hashes; later substantive edits require renewed review.
