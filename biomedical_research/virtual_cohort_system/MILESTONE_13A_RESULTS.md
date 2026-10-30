# M13-A: real-source Agent generation and feedback

30 October 2026. **Two actual Agent constructions and the real-source numerical feedback runs are complete. This is source-only development, not a real-target validation result.** Target body-fat measurements and patient-level target inputs were not acquired or used. The supplied qualification grid and all source-context covariates are simulated and explicitly labelled.

## What was implemented and run

Two fresh builder contexts received the same screened Pongchaiyakul 2005 and Gallagher 2000 extracts, permitted covariates and computational budget. Each Agent chose its conditional generator, individual variation, source covariate reconstruction, numerical parameters and calibration ranges. The controller provided the published-statistic checks and deterministic execution tools; it did not provide a ready-made generator or use target answers to tune one.

Both constructions used a bounded beta conditional family and published mean equations, with different partial-population-transfer and dispersion assumptions. This similarity is a result of two independently instantiated builds, not evidence that the builders are independent biological replicates. The use of a familiar conditional family or published coefficients is not claimed as a new statistical method.

Each initial candidate underwent an independent static/scientific review, an immutable freeze, nine bounded numerical trials, and replay on two separately scheduled random seeds. Generated Python ran through the existing WSL/bubblewrap adapter. An actual builder subsequently reviewed the full feedback. General Agent tool access remained procedurally restricted, not OS-isolated. Literature was screened upstream; this experiment did not demonstrate autonomous literature discovery.

Completed numerical work: **2 sessions, 18 trials, 80 generator executions and 720 retained source diagnostic records**. There were 18 constraints per source replay: ten Thai development statistics and eight Gallagher equation coefficients. Those counts are computational work, not numbers of clinical studies or target replications. Source support and deterministic design columns were checked without importing generated code on the host. No historical harness engine was changed.

## Source results

The loss is a mean squared discrepancy under fixed engineering unit scales. It is neither a likelihood nor a clinical accuracy measure. The separate replay uses the same reconstructed source contexts with new random seeds, not a new cohort or unseen scientific endpoint.

| Construction | Initial fitting loss | Selected fitting loss | Selected replay loss | Selected trial |
|---|---:|---:|---:|---:|
| build01 | 1.070225 | 0.668102 | 0.793914 | 6 |
| build02 | 0.695051 | 0.623795 | 0.706431 | 8 |

Both sessions reached the nine-trial limit. The declared exact-zero stopping value was not reached; `fit_threshold_not_met` is retained. It does not establish clinical failure or optimizer convergence. Source covariate assumptions differ between constructions, so their loss levels are not a controlled ranking of builder quality.

The aggregate improvement hides opposing source changes:

| Construction / source | Initial mean squared scaled discrepancy | Selected fitting discrepancy |
|---|---:|---:|
| build01 / Thai | 1.648631 | 0.755636 |
| build01 / Gallagher | 0.347217 | 0.558685 |
| build02 / Thai | 0.621390 | 0.702771 |
| build02 / Gallagher | 0.787127 | 0.525076 |

Using the **mean of absolute per-seed errors** for each constraint, build01 improved 10 and worsened 8; build02 improved 9 and worsened 9. The builder01 narrative used the absolute error of the seed mean, giving 11/7. Both calculations are retained and reconciled by the independent audit: Gallagher's Asian-age coefficient crosses the reference across seeds, so averaging before taking an absolute value cancels error. The canonical aggregate CSV uses per-seed absolute errors. No frozen review record was rewritten to hide the distinction.

Persistent mismatches include build01 Thai female SD around 9.78–9.84 percentage points versus the reported 8.4, and its Gallagher male/inverse-BMI coefficient around 41.7–74.8 versus 154 on the replay seeds. These are observed simulation ranges, not confidence intervals for either paper. All constraints and trade-offs remain in the report.

## A real problem found and corrected before execution

Builder02 initially reconstructed Thai BMI with bounded beta margins that closely matched sex-specific means/SDs and kept BMI below 30. But its development subset implied about 72.15 overweight participants, already more than the approximately 65 in the entire reported cohort. Matching moments and broad bounds had missed a joint consistency requirement across the reported summaries and study split.

Independent review stopped this unexecuted candidate. The Agent archived its complete original bytes and reconstructed a different bounded marginal under an explicitly assumed allocation: 33 development and 32 validation participants above the BMI threshold, giving 65/436, which rounds to the published 15%. Development BMI moments were preserved. The conditional generator code was unchanged. This was a source-input correction, not an improvement established on patient outcomes.

The assumed allocation is not a recovered subgroup count. Builder01 chose a different feasible allocation, and its resulting female BMI marginal is strongly U-shaped. These are important remaining reconstruction uncertainties. The implementation can audit compatibility with reported constraints, but satisfying them does not identify a realistic full source distribution.

## Agent review and retained candidate

Builder01 chose `retain_structure`: its selected parameters changed the Asian blend from 0.35 to 0.50 and the shared male location shift from 0 to −1 percentage point. It explicitly retained the cross-source failures rather than adding unsupported terms. The controller promoted the exact selected code/specification into a frozen `source_reviewed` development candidate. The provenance revision is not a new structural model.

Builder02 also chose `retain_structure`. Its male/female Asian bridge weights changed from 0.50/0.50 to 0.75/0.25, and its male/female conditional SDs changed from 4.31/4.31 to 4.81/3.81 percentage points. It rejected an unsupported structural expansion and retained all adverse source trade-offs. Its exact selected code/specification was also promoted to `source_reviewed`; both loop completion records passed integrity verification. Neither builder used the optional second numerical session or performed a structural revision after outcome generation.

For the intended non-Asian target domain, the build01 selection only changes the male conditional location, subject to the declared bounds. Build02's Asian bridge weights do not change its non-Asian conditional mean; residual-scale changes affect individual variation. Age/BMI mean shapes are largely inherited from the published equation. Matching their directions later would be a transport check, not discovery of previously unknown relationships. Additional value must be assessed through the usefulness of the whole generated distribution and analyses not directly fitted.

## Verification and limits

An independent auditor recomputed **216 source statistics from 24 retained source-generated tables** across the two constructions, using ordinary numerical analysis rather than importing either generator. Maximum discrepancies from stored results were 1.11e-10 and 7.94e-11. Observed covariates were preserved exactly. The auditor checked all 80 receipt/output hash bindings, all 720 diagnostic records, selection arithmetic, original coefficient coding and the source-input repair. All 108 aggregate CSV rows and the two error-summary conventions were also checked.

These checks establish that the recorded source computations are internally consistent. They do not validate source covariate assumptions, scanner equivalence, individual measurement recovery, calibrated uncertainty, general biological realism or publication-level novelty. The source checks were approximate because the papers do not supply the complete joint covariate distributions. No full test-suite rerun was needed: the historical core was unchanged, and actual case-level arithmetic, contracts, execution receipts and artifacts were verified.

## Next step

Stop optimizing this source-only score. Finalize the already drafted real-target protocol and evaluator, then use the frozen scientific candidates to generate data for a quarantined public target. Primary scope is adults aged 20–59, non-Hispanic White/Black, valid DXA and BMI 18.5–<30; BMI 30–35 is a separate, prespecified transfer extension. The entire DXA measurement family stays outside builder input.

Use the same generated release for adjusted age/BMI relations, a fixed curvature contrast and unfitted age/sex/BMI-cell quartiles and IQR. Retain a published-equation reference. Fix the exact candidate/seed roster and estimator implementation before outcome access. Compare scientific conclusions, magnitudes and distributional reuse; do not select a candidate by its target score or silently tune away a failure. Current work requires no model training or HPC allocation.

Detailed source evidence, all aggregate results, candidate artifacts, failed preparation and audit records are curated under `reports/m13_source_loop_2026-10-30/`. The report there specifies export limits and reproduction inputs. Historical admission remains in [the admission review](docs/REAL_CASE_ADMISSION_2026-10-30.md); the proposed target estimators are retained with this milestone and remain unfrozen until their implementation is checked.
