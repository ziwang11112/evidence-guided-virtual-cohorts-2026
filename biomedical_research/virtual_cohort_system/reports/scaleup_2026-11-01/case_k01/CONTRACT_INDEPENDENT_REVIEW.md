# Independent K01 scientific contract review

2 November 2026. Reviewer: `context_bridge_review`.

**APPROVED as a fixed K01 scientific design commitment. Production execution is not ready or authorized.** The reviewed source roles, target eligibility, statistical reference, three estimands, uncertainty/failure rules and finite budgets are sufficiently specified for scientific case admission. Remaining uncertainty about joint structure and transport is explicit scientific content for the constructors, not a reason to keep reopening admission. The remaining implementation work is the bounded authentication, collection and controller wiring described below; this review does not issue a global freeze, approve an actual clinical candidate or permit reference disclosure.

This is a new review file. The earlier `INDEPENDENT_DESIGN_REVIEW.md`, including its MIND follow-up, remains byte-identical at SHA-256 `5120b704034509686ea7a111d5cb1a953373fcb549703a4d74f4f3fda521abfb`. Its original-source access limitations still apply. No raw participant file, target effect, new original study or browser was accessed in this contract unit. No actual source parameter fit or clinical cohort was produced.

## Fixed target and scientific analyses

The ordered generated columns are `id, age, sex, bmi, glucose`, in units `1, year, 1, kg/m^2, mmol/L`. IDs are unique nonempty strings; `F` means Female and `M` Male. The retained HAALSI schema audit verifies raw sex codes 1=Male and 2=Female. Age is the census age at 31 July 2014; glucose is the released cleaned pooled capillary POC measurement, not universally fasting or laboratory serum glucose. BMI's conventional unit follows the cleaned height/weight definition.

The measured-reference subset is fixed: native/tagged missing excluded before numerical use; finite age/BMI/glucose; age at least 40 with no upper cutoff; recognized sex; strictly positive BMI/glucose. There is no imputation, fasting or treatment restriction, range-flag exclusion, clipping or tail trimming. Unknown nonmissing canonical sex tokens and malformed numeric schema fail the input rather than silently coercing. The retained codebook/actual variable metadata identifies no named finite numeric nonmeasurement sentinel for these fields; explicit empty sentinel lists mean **none documented**, not proof none exists. Flag thresholds are not sentinel definitions. Retained positive finite cleaned boundary values keep a recorded-value interpretation, not exact latent biological accuracy. No reference sample size or distribution is given to constructors.

All three analyses use the same eligible reference frame and the entire valid generated target frame, unweighted OLS with an intercept:

| Endpoint | Fixed contrast |
|---|---|
| `K01-GLUCOSE-BMI` | 5 times the BMI coefficient in glucose on age, Female and BMI |
| `K01-GLUCOSE-AGE` | 10 times the age coefficient in that same base model |
| `K01-SEX-BMI` | 5 times the Female-by-BMI coefficient in the model adding that interaction; Female-minus-Male BMI contrast |

The two base-model outputs are different scientific questions, not independent replications. The third is the reuse item within the three primaries. All three remain joint-assumption dependent under the fixed evidence. No desired target sign or effect is prescribed. Coordinates `(age-50)/10`, `(BMI-25)/5`, Female and Female times scaled BMI implement these contrasts exactly; their centers are numerical coordinates, not source or target parameters.

Require n>5, both sexes and full base/interaction ranks 4/5 under the specified SVD tolerance. Failure of either rank, sex support, row count, constant glucose or nonfinite OLS arithmetic makes all three unavailable. Finite identifiable point estimates can remain when HC3 is unavailable. Reference-only HC3 with the fixed normal multiplier is a working descriptive sensitivity, not cluster/survey coverage or source/transport uncertainty. Generated tables supply no inferential intervals.

For every effect, report the raw discrepancy and `abs(generated-reference)/reference_glucose_SD`, with the reference SD calculated on that common eligible frame using ddof=1 and withheld from construction. A nonpositive/nonfinite denominator cannot pass. The fixed working boundary is <=0.10, with the complete 0.05/0.10/0.20/0.30 grid reported. These are exploratory resolutions, not clinical equivalence or percentage-error guarantees.

A final constructor passes only if all three effects pass on all three seeds. At least four of all five Agent constructors must pass; failed/missing attempts remain in the denominator. S01 has the same individual bundle rule and is reported separately. Final is primary; retention aliases initial outputs, and a failed changed final cannot fall back to initial. If all three zero-effect anchors are already within the working margin, the case is insufficiently discriminating for the positive continuation gate. Independently admitted K01 must pass and be discriminating; K02 cannot unlock Wave B alone. Unavailable reference endpoints prevent a case pass without replacing questions.

## Source packet and the 18 descriptive scenarios

The final eight-file constructor allowlist is bound by `request/packet_manifest.json`. I verified every file hash and length, all 34 copied original records against their retained JSON pointers/canonical hashes, and the exact 18 marginal-role bindings. The packet contains seven MIND selected items, eleven Ayele covariate margins, six contextual composite-DM ORs and ten contextual Bahendeka abstract records. It mounts neither original audit directories/private captures nor old target results. HbA1c, FPG, correlations and quarantined MIND agreement bundles are excluded from numerical construction inputs.

Exactly **four means, four individual SDs and ten count-derived proportions** are fixed for the two source contexts. All comparison values, source/context IDs, units, count operands and derivations match the retained evidence. Ayele printed percentages remain separate original records; comparisons use the specified count/872 ratios, not silently substituted rounded percentages. MIND Female is the preserved count ratio. SDs remain participant dispersion, not SEs, confidence intervals or residual noise.

These are reviewed descriptive scenarios: equal generated-row weights; SD ddof=1 while the source divisor remains unknown; an assumed complete post-analysis distribution rather than replay of original missingness/imputation. Ayele age bins explicitly interpret the printed completed-year labels as `[25,35)`, `[35,45)`, `[45,55)`, `[55,65)` for continuous generated ages. The source Methods support remains 25–64 inclusive and the caption discrepancy remains documented. The BMI middle event is the literal closed `[18.5,24.9]`, preserving its gap before 25. All proportions use all validated source rows as denominator. Conjunctions are one derived event; applying a lower bound as row selection would change the estimand and is forbidden.

The thin helper uses the existing `apply_operator` for means, sample SDs and proportions, materializing fixed Boolean conjunctions over the whole frame. Its 7+11 IDs, predicates and units match the plan. It does not compare source evidence values, invoke strict semantic feedback, create approvals or authenticate execution. Unknown source weights keep strict `semantic_feedback_v1` replay unavailable; the approved descriptive interpretation does not promote it to exact source reproduction or transport validation. An eventual collector must bind the strict result first and retain the descriptive result separately.

Source contexts have shared canonical column units but different eligibility: MIND 61–80, Ayele 25–64 by its Methods interpretation, target >=40 without an upper limit. Bahendeka is contextual and unscheduled. Shared mmol/L does not equate fasting serum, repeated capillary averages and pooled cleaned POC measurements. The Agent owns unreported dependencies and context transport; no source demographic margin becomes a prescribed target margin.

## Statistical reference and finite budget

The S01 specification is an acceptable transparent completion baseline, not an optimized competitor or evidence for independence. Its formulas are correct: bounded-beta age moment inversion under each declared source support; lognormal arithmetic mean/SD inversion for MIND BMI/glucose; and Ayele BMI lognormal inversion from the exact outer count ratios and fixed thresholds. Count operands and printed percentages stay distinct. Invalid domains stop without clipping, parameter replacement or family switching. Source SDs enter as an explicit population-moment approximation, not precision weights.

S01 assumes independent marginals within source/donor context. It copies the MIND glucose law to Ayele and target as unsupported measurement/population transport. The target selects each donor with probability one half, then conditions that donor's age law on >=40 through the specified inverse CDF. This differs from filtering a pooled mixture and changing donor weights. Its upper age support of 80 is a model limitation, not an upper target eligibility cutoff. The identical independent glucose law gives zero population contrasts by comparator assumption, without forcing a finite sample to zero or imposing that law on Agents.

The same admitted information goes to all five Agents and S01. The metadata normalizer preserves all 18 normalized records, locators, count operands and original-record hashes; its one explicit `≥25` to `>=25` spelling change is bound. I checked the actual view against the packet without calling fit/sample on it. All source/input/code hashes and normalized-content digest match. Its `_validate_inputs` call checks shape/count consistency only; it creates no fitted parameters. Expected-manifest matching is integrity, not an author signature or execution approval.

The scientific schedule is fixed by the reviewed reference/budget JSON, including where request metadata still describes controller scheduling as pending:

| Allocation | Source | Target |
|---|---:|---:|
| Contexts/seeds per executed stage | MIND 3101, Ayele 3102; 5,000 rows each | Target 2101, 2102, 2103; 5,000 rows each |
| Initial+final reserved slots, six constructors | 24 / 120,000 scheduled rows | 36 / 180,000 scheduled rows |
| Maximum new attempts with all five Agents revising and S01 retaining | 22 / 110,000 scheduled rows | 33 / 165,000 scheduled rows |

S01 precommits retention if execution/contract integrity holds; its final reservations alias initial outputs and cannot be reassigned. Each constructor receives one initial packet containing both source reports, including unavailable/failing entries. A changed final is frozen before execution; final diagnostics cannot trigger another revision. Target summaries are never construction feedback. Failed prelaunch attempts, timeouts and interruptions consume their slot/full scheduled-row allocation; no replacement seed, retry, warm-up, hidden calibration or automatic partial resumption is allowed.

Scheduled executions retain the 60-second, 1,024-MiB, 2,000,000-output-byte and 10,000-log-byte caps. Analytic derivation permits one reviewed deterministic job per initial/changed-final construction, 120 seconds/1,024 MiB: 12 reserved, at most 11 new with S01 retention. No optimization/grid/quadrature/Monte Carlo fitting or cohort sampling is allowed inside that job. Standard CDF/inverse-CDF evaluations serve only the declared formulas/sampler. The existing 40-turn ceiling and zero extra simulation-calibration calls remain. Pending integration cannot be interpreted as discretion to change these scientific allocations.

## Component review and independent verification

I reviewed the new analysis, whole-frame context guard, descriptive helper, statistical reference and metadata normalizer. No substantive unresolved defect was found. Two packet alignment issues were fixed before the final commitment: visible endpoint IDs now equal the analysis IDs, and the source category prose explicitly distinguishes original age labels from the half-open diagnostic scenario. All three exact population strings/age bounds match the guard constants.

The guard checks exact task/population/context consistency, ordered columns, requested rows, IDs, finite values, sex, positive BMI/glucose and context age bounds. A target task cannot be passed with the Ayele context to bypass age>=40. Every generated row must pass; there is no filtering or repair. A caller could still supply an entirely different self-consistent tuple, so the returned hashes prove input consistency, not provenance. The production caller must obtain context/task identity from authenticated immutable execution, not select it after seeing rows. The code honestly marks authentication and release false.

Author verification is recorded separately from my work: root reported 18 new analysis/guard tests, initially 17 passing plus one test-oracle failure, corrected by a test-only metadata fix and an affected-test pass; three new descriptive tests passed. The reference author reported 54 invented-input tests passing on the first run and 11 new normalizer tests passing on the first run. I inspected the relevant tests/code and did not rerun these suites or any old suite.

I performed **one independent composed invented check**, first attempt successful: the author's explicitly invented 18-record fixture, one analytic fit, then one in-memory 24-row draw in each of the two source contexts and the target, each using fixed seed 20261102. Total: 72 invented rows, three sample calls. All guards passed. All 18 source outputs matched the frozen plan's IDs/units/predicates and full-row denominators; independent arithmetic maximum error was `2.220446049250313e-16`. The invented target contrasts were:

| Invented endpoint, not a clinical result | Value |
|---|---:|
| BMI contrast | -0.022429149132349113 |
| Age contrast | -0.003770013015672924 |
| Female-minus-Male BMI contrast | 0.5622390460947222 |

An independent raw-coordinate QR calculation agreed with the implemented point estimates within `1.801510329801914e-15`; an independently formed HC3 SE agreed within `8.881784197001252e-16`. The reference-role calculation here used the same **invented** frame solely as an arithmetic oracle. Generated-role output exposed no inferential interval or SD denominator. No CSV, candidate, isolated execution, actual-source fit, participant result or extra scientific study was created.

The retained aggregate record is `implementation/INDEPENDENT_COMPOSED_RESULT.json`; it records the executed inline check, fixture/code commitments and results without storing rows or rerunning the check. `implementation/INDEPENDENT_COMPOSED_CHECK.py` preserves the exact executed Python body, saved after that run and not rerun as a file; its project-root working directory is recorded in the JSON, with no timing claim. The coordinator's `CONTRACT_DECISION_2026-11-02.md` and `K01_CONTRACT_CHECKPOINT_2026-11-02.md` were also read: their distinction between fixed scientific design and blocked production execution is consistent with this review.

## Remaining production gate

Scientific case design is approved at these bytes. Before any clinical run or reference disclosure, the existing controller still must bind the approved allowlist, actual constructor model/assumptions/shared-versus-varying parameters, immutable common generator/spec and exact child contexts; reserve the finite attempts/retention aliases; authenticate outputs before the context guard; and bind strict semantic feedback plus separately reviewed descriptive comparisons. The reference preparation must preserve native/tagged missing semantics and the verified raw sex mapping before the fixed analyzer. The evaluation/bundle code must enforce the fixed rules on every planned output after construction closes. Global campaign freeze and custody remain separate gates.

These are specific production bindings, not a request for more source studies, new endpoints, a general framework or complete biological identification. No scientific success, calibrated transport uncertainty, accurate individual reconstruction, assay equivalence or clinical substitution follows from the component checks.

## Final byte commitments

Paths are relative to `case_k01/`. The packet manifest commits all eight constructor files. This review does not rewrite their historical proposal/activation flags or earlier checkpoint hashes.

| Artifact | SHA-256 |
|---|---|
| `request/packet_manifest.json` | `3b45d796ebcbff18f1a67abdbffdd441eb583a17e3ac5d94e0458fe8a3a6087b` |
| `request/context_eligibility.json` | `22665dcd83e6f5e9b17b073d0bfb33e055a823311f2e57e6b9214f5296b6da94` |
| `request/descriptive_diagnostic_plan.json` | `efcf3377056f1940692034a85767398816b092e4aab3c7ba912ca79ce111d570` |
| `analysis/K01_ANALYSIS_SPEC_v1.json` | `a5b1e945360083fd24b30087e25d4f822306eb6ef2931736c6f49463c8045872` |
| `analysis/k01_analysis.py` | `e334919da8e785382544d647b3e6a849c00c2b034af043bbbd8ac3f9b5ef071a` |
| `implementation/generated_validity.py` | `da8286654b1330f9c86611027058ba1f38cdda944ac48fcfb7ea3a65f4b25ec8` |
| `implementation/source_descriptives.py` | `00c7e0f55ad5fa4104648a1c89bce3dc4d2a373b7cae3e46d6ad99ae6f69b609` |
| `implementation/statistical_reference.py` | `c9c903b6a12b2c669eb25f7c2e3f69318368a17e64b415569e91d4636c80b9f7` |
| `implementation/prepare_reference_inputs.py` | `40808d5c59abf48080744b9ca1363a34bd31187f322169e0b8c33bd1e72720a6` |
| `REFERENCE_INPUT_VIEW.json` | `16f54e233035739144b7ca2f53718a9ab86ea857cfe8e5b992d95f929a5d839a` |
| `implementation/INDEPENDENT_COMPOSED_CHECK.py` | `f28c26d1c0f5ddb3c24fedf1a9299c598927581f7d6167a28ea8b2744dd94225` |
| `implementation/INDEPENDENT_COMPOSED_RESULT.json` | `0271d9605555287698721893e827c00e981e21de18c5aa691c53e2d82e2b06f4` |
| `STATISTICAL_REFERENCE_AND_BUDGET_PROPOSAL.md` | `db8cf45fb676c6f5e0229c30371cb8b33014631320e69cdf044f578fcde23fc3` |
| `statistical_reference_and_budget_proposal.json` | `60b90a876dafaa5861202d56754b4d9a41859e2343c6ecc776b737b8a5c5269d` |

The metadata view's normalized-constraint digest is `ac120ce1da570887bbeb2d43d999b4e8e82019e54ade161c94741a18b755da26` under its declared compact sorted `ensure_ascii=True` convention. It binds source inputs, not fitted parameters or an execution. This review changes no STATE, export, old review, frozen K02 module or campaign inventory.
