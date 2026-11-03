# Independent implementation review — adaptive CHNS reference pilot

Reviewed 3 November 2026 by the independent implementation reviewer. This is a scoped implementation and aggregate-arithmetic review, not a scientific-validity certificate. The stable controller below had no remaining identified blocker for session initialization and the first isolated trial. Final delivery, actual author response to delivery feedback, and paired final results were still pending at this report's first issuance.

## Scope and reviewed bytes

`P = D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/virtual_cohort_system`.

`U = P/work/adaptive_reference_pilot_2026-11-03`.

`B = D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcAR/b`.

The session root is `D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcAR`; its bundle is `b`. Read scope comprised the author task, profile, preparation/attachment helpers, new controller/evaluator, authoritative harness interfaces and source code, supplied B aggregate/evidence inputs, the completed new `ar01_trial` submission, and that submission's successful synthetic output. No raw participant file, old scientific generator, old generated table, or old test suite was read/executed. The reviewer authored no scientific generator or parameter changes. The only executed reviewer numerical work was supplied-aggregate algebra and recomputation of an already generated synthetic CSV.

| Artifact | SHA256 reviewed |
|---|---|
| `U/implementation/adaptive_session.py` | `2ed217ccb33771e6560ae6cd6c45ae127a9d9788fb4fe7a0d5557f74a49c320c` |
| `U/implementation/reference_evaluation.py` | `ea77c8851f759dc6070bb70207dbd2a769e14c40d48799f0517951a686dfe65a` |
| `U/prepare_inputs.py` | `47d133cf306f271e180eddb4027e3b29383e6f9a5d992144bd92c5157ffb1479` |
| `U/attach_feedback.py` | `ea22f556ff1884f8f214931a67eeb9fd49080f5997816faa4aaa05e17e318f57` |
| `U/profile.json` | `a411ac75922512f7314079beab0f58c4bdfb8c5e85c1f125e27fe0c4ae22e54b` |
| `B/input/compiled_evidence.json` | `32890777ee5b5792c723a17b1fc717e88f7c4db9ebf4fe4a8bdbbf786d16d159` |
| `B/input/whole_cohort_feedback_template.json` | `138a3fa340f167069fb3df6ebd0a57b402a49d4be068aa4acba805ca749f191f` |
| `B/input/semantic_bindings_template.json` | `afb14bceb6a491846e7312363a954122e8289db80bd87902116822fa8c8f0aa3` |

Review findings were sent while implementation was still changing. The following fixes were independently reread before initialization; they are not unresolved findings against the final hash.

## Findings corrected before execution

| Severity | Concrete finding | Observed correction |
|---|---|---|
| P1 | The controller initially allowed 5,000-row trial tasks despite the 3,000-row author/profile contract. | Trial cap changed to 3,000, and initialization compares profile budget fields with the session/task budget. |
| P1 | E1 and E2 parenthesized slope units were rejected by semantic v1's literal per-unit rule; `attach_feedback` could not preflight the fixed recipes. | Feedback evidence and both recipe/semantic operators now use `%/kg/m^2` and `%/mmol/L`. Original readable `%/(kg/m^2)` and `%/(mmol/L)` remain in the reference/analysis definitions. Values and adjustment sets did not change. All 30 template operators passed the actual semantic measurement, evidence-role, uncertainty and task-type functions in a non-generating reviewer check. |
| P1 | A failed delivery stopped the seed loop; a resumed call started at an already attempted seed, while feedback demanded all three successful runs. One failure stranded the entire revision flow. | Delivery skips all previously reserved seeds and attempts only remaining fixed seeds. Failed and unresolved attempts retain their charged slots and yield all 30 named unavailable diagnostics. Stage feedback can then be handed back honestly without retrying a failed seed. |
| P2 | Any nonempty author/recipient ID could be recorded while the contract claimed one author. | Dispatch and handback now require exact equality with the sole declared author ID. Actual delivery remains a coordinator action, not a messaging action performed by this module. |

The engineer reported ten passing controller fixture tests, including mid-seed failure continuation. The reviewer did not rerun these tests or any legacy suite. This review's direct evidence is the stable code inspection, aggregate input checks, and independent actual-output recomputation below.

## Input coverage and scientific semantics

A reviewer JSON/algebra audit confirmed 67 evidence items across six source entries, with exactly 27 diagnostic IDs and three analysis IDs. The 30 checks and 30 semantic bindings cover those IDs once each. Every reference check is attached to `CHNS_DEV_REF`; estimates exactly match the admitted reference summary. All registry artifact hashes matched, and the reference input and its admitted source copy are byte-identical. Reference sample n is 6,631; generated task n is 3,000. The supplied female mean and SD satisfy the Bernoulli sample-SD identity exactly at n=6,631.

The generated columns are age, female, BMI, glucose and HbA1c. Identifier is separate, all five substantive variables have generated roles, mode is `whole_cohort`, and there is no `observed.csv`. Units are year, 0/1, kg/m², mmol/L and HbA1c percent. The requested unweighted regressions retain their exact conditioning:

| ID | Coefficient | Other predictors | Intercept |
|---|---|---|---|
| E1 | BMI in HbA1c regression | age, female | Yes |
| E2 | glucose in HbA1c regression | age, female | Yes |
| E3 | age in HbA1c regression | female, BMI, glucose | Yes |

The three available reference confidence intervals, standard errors, 218 groups, 217 degrees of freedom and `CR1_t` method remain in `reference_summary.json` and the numerical evaluator's reports. The semantic evidence represents the intervals as estimator uncertainty. Other diagnostic estimator uncertainties remain `not_reported`; individual SD estimates are not converted into estimator SEs. Three synthetic seeds do not estimate reference sampling, structural, transport or evidence uncertainty. No combined scientific score or post-hoc equivalence threshold was added.

`task.information_policy.mode="published_evidence"` and candidate `checks.scope="source_only"` are legacy schema vocabulary. For this explicitly authorized task they mean all declared admitted inputs, including the internal exposed CHNS development reference. They do not mean an external-literature-only experiment. The explicit source ID, task narrative, profile, recipe measurement description, author decision and evaluator limitations carry the more precise meaning. Internal reference comparison is not source-population reconstruction or external-paper replay; the author honestly records that external replay was not performed.

The semantic sidecar and numerical recipe are prepared together. Equality alone would establish only self-consistency. This review additionally checked their actual IDs, estimates, operands, adjustment sets, sample size and uncertainty roles against the separately supplied aggregate summary and analysis definitions. That does not verify the historical raw-data extraction, which was outside scope.

## Estimators and execution/control boundary

The primary evaluator correctly uses sample SD (`ddof=1`), linear 0.1/0.5/0.9 quantiles, ordinary Pearson correlation, and Pearson correlation of average-tie ranks for Spearman. OLS uses an intercept and the declared predictor order; full-rank checks precede `numpy.linalg.lstsq`, with the term index adjusted for the intercept. The explicit nonpositive-glycemia quality gate can withhold regression results. Diagnostic/reference IDs are checked, and the session additionally rejects duplicated/missing result IDs. A numerical value is not promoted to a significance or equivalence claim.

Initialization snapshots/hash-binds the actual controller, evaluator, profile, reference and definition files, plus harness source modules and supplied dependencies. Every locked mutating operation verifies those bindings. Successful evaluation binds the attempt, candidate freeze, execution receipt, CSV, semantic feedback and reference feedback; later stage verification recomputes feedback. Freeze remains structural acceptance. The new session directly calls `semantic_feedback_v1`; no legacy fallback was identified.

Attempts are reserved before execution. The controller permits two trial slots in each author phase, three fixed delivery seeds 3101/3102/3103 per stage, one initial/final review cycle, and ten total table attempts. Failed/reserved slots remain charged. Trials must precede that phase's delivery. Revision dispatch requires real initial feedback and recorded handback; final freeze requires the author decision. The coordinator must still perform and retain the actual author interaction, including a truthful no-op decision where appropriate.

The existing execution adapter stages task/specification/generator only for whole-cohort runs and calls `generate(None, spec, seed)` inside the configured WSL/bubblewrap worker. It has no local-generator fallback. Runtime namespace/mount isolation concerns the generator process, not the author's broader tool access. Execution receipts bind bytes and do not authenticate against a hostile host. New output mutation is constrained to the new session root; preparation reads historical admitted aggregate artifacts and copies into B. This scoped inspection does not independently certify unchanged bytes throughout every historical directory.

## Internal sampling and first candidate

The harness enforces attempted table counts and emitted CSV rows. It does not instrument internal generator random draws or hidden calibration cohorts. Therefore a general claim that every internal simulation was bounded to 3,000 rows would exceed its scope. Source-context trials and failed execution attempts must remain part of the same table budget. Author tool activity also requires truthful external accounting.

For the actual frozen `ar01_trial` generator, static inspection found no oversampling, rejection loop, hidden fit loop or extra synthetic cohort. Six primitive random arrays each have length n=3,000: age, female, BMI, mixture membership and two normal innovations. These represent six draws at each of the same 3,000 person positions, not six independent cohorts. Remaining arrays transform those positions. `analytic_fit.py` uses 40 age support points and 24-point deterministic quadrature with optimization; these are deterministic integration calculations, not random individuals. No generator was locally run by this reviewer.

All emitted scientific variables are bounded or binary. Direct parameter algebra gives pre-rounding glucose support [2.2133316354, 25.3434581885] and HbA1c support [2.4881376894, 18.0302554800]; specified rounding preserves positivity. BMI is clipped to [10,55], age to its sampled 35–74 support, both latent correlations are within [-1,1], and age probabilities sum to one. The theoretical BMI clipping mass is about 2.51e-9. Finite output moments are supported by the construction; those particular bounds and latent mixture are assumptions, not empirically identified tails.

The author distinguishes fitted CHNS quantities, contextual external evidence, algebraic derivations and unidentified independence/sex effects. The three regression projections are approximate after numerical quadrature, imperfect marginal fitting, clipping and rounding, so the retained calculation is not a guarantee of actual finite-sample coefficients. The first trial is required to observe these effects.

One nonblocking provenance issue remains for a future unfrozen author submission: `analytic_fit.json` includes `copula_correlations` and `expected_baseline_covariance`, but the retained `analytic_fit.py` does not produce those fields. The author declares a separate 64-point deterministic covariance solution. Preserve that actual solver or a precise calculation record in the next candidate to make the entire claimed analytic artifact reproducible. Do not modify the frozen trial to repair this documentation gap.

## Independent actual-output recomputation

Reviewer code `U/implementation/independent_recompute.py` does not import a generator, the primary evaluator, or the cohort harness. It checks the session contract/event chain, actual successful execution identity and CSV hash, reads the synthetic CSV with the standard CSV reader, verifies schema/order/bounds/finite values/unique identifiers, and recomputes all 30 statistics. It uses `statistics.fmean/stdev`, explicit sorted linear interpolation, independently coded average ranks and centered correlations, and SciPy pivoted QR/triangular solve for OLS rather than NumPy least squares. The absolute/relative 1e-10 comparison tolerances are arithmetic implementation tolerances only.

For each existing successful attempt, the audit compares both feedback implementations and their reference differences, counts every trial/delivery/failed/pending slot, and tracks exact CSV duplicates and duplicate measurement multisets across seeds and stages. It produces no synthetic data and no scientific pass score. The source reference remains exposed information throughout this check.

The first completed real trial `a01_initial_6101` was independently recomputed from its 3,000-row output. All 30 statistics agreed with both recorded calculators within the arithmetic tolerance; zero discrepancies were found. There were 3,000 unique IDs, no duplicate complete measurement rows and no nonpositive glucose/HbA1c. This result is retained in `U/INDEPENDENT_RECOMPUTE_01.json`, SHA256 `8b18762d5e38f69ea22a5290558e435bd16104695baa9a5dac2cb2af57ccbd41`.

The recomputed first-trial coefficients were E1=0.05315530393, E2=0.42558805521 and E3=0.00836939960. Pearson was 0.64768467859 and Spearman 0.43259151624, versus exposed references 0.66096828685 and 0.36145731918. The Spearman discrepancy is retained as actual scientific feedback, not hidden by the software checks. These are single-trial results and are not final delivery conclusions.

The same auditor should run again after actual initial/final delivery and feedback exist, writing a new immutable report. Final reporting must include all attempted slots and all 30 per-run diagnostics, distinguish paired seed changes from new independent evidence, verify actual initial/final author handback, and preserve failed slots or no-op duplicates. Those later steps were not claimed complete at first issuance.

## Second-trial addendum

`INDEPENDENT_RECOMPUTE_02.json` covers the first two actual attempts, both successful initial-phase trials. All 60 run-statistic values match both retained feedback calculators within the numerical tolerance; no arithmetic discrepancy was found. The second trial uses seed 6102, so its Spearman value near 0.4629 versus the first trial's 0.4326 is not a paired-seed improvement comparison. Both discrepancies remain visible. The initial phase has used both authorized trial slots.

Static comparison showed identical generator bytes in `ar01_trial` and `ar02_trial`; the only scientific parameter change is copula correlations from [0.40, 0.5717497553] to [0.28, 0.5871524664]. Thus the same finite-support and internal-row accounting apply. The second candidate now retains/hash-binds `covariance_solver.py` and its calculation provenance, addressing the first-trial reproducibility gap without modifying that frozen trial. The decision describes an earlier failed deterministic root-bracketing calculation and subsequent numerical clipping correction; it does not represent those mathematical operations as cohort executions.

An interface incident is preserved in `U/AR02_ENCODING_REPAIR.json`: the first ar02 freeze rejected a CP1252 decision file before execution; the coordinator re-encoded it to UTF-8 before freezing. The repair expanded line endings, a normalization assertion failed, and the original before-hash was not saved. Therefore byte-preserving equivalence was not independently established and is not claimed. The subsequent freeze/execution succeeded, and the frozen file was not repaired again. The reviewer additionally observed mojibake in the copied first-trial prose (`â€”`, `35â€“74`, and related dashes), beyond the line-ending issue. Scientific numbers remained readable. The minimal remedy is author cleanup in a new unfrozen candidate, preserving ar02's historical bytes. This was a pre-execution interface failure, not an uncharged failed generator attempt.

## Initial delivery and actual revision dispatch addendum

`INDEPENDENT_RECOMPUTE_05.json` audits all five then-completed attempts: two trials and the initial deliveries at fixed seeds 3101, 3102 and 3103. All five succeeded; all 150 run-statistic values match both retained calculators within the arithmetic tolerance. No duplicate table hashes or measurement multisets occur across these five runs. Each delivery contains 3,000 unique IDs, no complete duplicate measurement rows, and no nonpositive glucose/HbA1c.

| Initial seed | E1 | E2 | E3 | Pearson | Spearman |
|---|---:|---:|---:|---:|---:|
| 3101 | 0.06324772 | 0.43928095 | 0.00888698 | 0.70519121 | 0.41604442 |
| 3102 | 0.05144013 | 0.37361490 | 0.00810780 | 0.62110695 | 0.41284221 |
| 3103 | 0.05863093 | 0.40560989 | 0.00795681 | 0.68531827 | 0.43812381 |

The initial delivery Spearman association is consistently above the exposed reference 0.36145732. This repeated discrepancy is scientific feedback for the author; software agreement is not scientific equivalence. The variation of the other coefficients across seeds remains visible without selecting a favorable draw or reporting a composite fit score.

The coordinator confirmed sending the full initial feedback to the same scientific author via actual follow-up before recording handback and revision dispatch. The reviewer checked the matching ordered ledger: event 0018 records `session/feedback/initial.json` with SHA256 `c98f183d8173b6f7360442086fc23f2a642901d42225f3af1f3085e154e808bc`; event 0019 hands that identical hash to `/root/adaptive_scientific_author`; event 0020 dispatches the revision phase to that same author. This is an actual initiated author revision flow, not merely a static feedback file. Final author decision and final outputs remain pending at this addendum.

## Revision-trial addendum

`INDEPENDENT_RECOMPUTE_06.json` covers all six completed successful outputs: two initial trials, three initial deliveries and one revision trial. All 180 run-statistic values match both calculators without arithmetic discrepancies. The actual revision trial's Spearman is approximately 0.368165 versus reference 0.361457; E1, E2 and E3 are approximately 0.065437, 0.435049 and 0.008790. This single new seed is not a paired comparison with initial delivery and does not establish final performance.

The `ar03_trial` generator has exactly the same bytes as the earlier generator. Core/broad copula correlations change to [0.12, 0.6076353386]; all margins, supports and regression shifts remain unchanged. The static finite-support and six length-3,000 random-array findings continue to apply. No hidden random integration or extra cohort was found.

The newly retained `rank_integral.py` calculates joint moments of marginal mid-distribution ranks under the declared distribution. It correctly conditions both markers on the same mixture membership and age, integrates BMI independently with its declared clipping, uses marker rounding before rank lookup, and applies the discrete-rank variance identity `(1-sum(p_i^3))/12`. The glucose/HbA1c support grids cover the mathematically bounded outputs. Its 48/64 normal-node calculations predict the old core setting near 0.4263/0.4262 and the proposed core 0.12 near 0.3613. This is a deterministic calculation, not a synthetic trial table, and was not imported or executed by the independent output auditor.

The rank calculation remains an approximation: BMI and the joint expectation use quadrature, and rounding makes the integrand nonsmooth. Agreement at two node counts is useful numerical evidence, not a certified error bound. The script's wording “exact marginal rank variances” means the exact variance identity applied to quadrature-approximated marginal masses; it does not make the entire population integral exact. The author appropriately describes the retained result as approximate and keeps the actual isolated trial distinct. Final paired delivery remains pending.
