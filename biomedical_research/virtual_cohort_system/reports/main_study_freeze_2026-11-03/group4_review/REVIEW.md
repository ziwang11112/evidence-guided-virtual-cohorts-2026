# Group 4 independent review

Reviewer: `/root/main_review_g3`. Both assigned frozen `candidates/initial` selections are **ready**, with no blocking findings. Both decisions are `initial_final`; no exploratory trial or feedback was required. Prior review reports were left unchanged.

| Candidate | Independent review result |
|---|---|
| CHNS2009_E0_A04 | The implemented one-factor multivariate lognormal law has finite mixed polynomial moments, positive support and nonsingular population projections. All 31 source marginals trace to registered evidence; E0 empty uptake is appropriate. All 31 target-table source comparisons remain unavailable. |
| ENSANUT2018_E1_A02 | The standardized-beta factor law preserves the exact 375-row demographic cells and task support. Independent covariance/projection algebra verifies the three declared source constraints. All 30 source evidence items and 11 uptake operations are accounted for. The target and Lifelines laws are bounded; the Pani shifted-Gamma age law and affine response have finite polynomial moments. All 29 target-table source comparisons remain unavailable. |

For ENSANUT2018_E1_A02, all eight Pani age-band conflicts were independently reproduced. Model means exceed reported means by **0.1500068464–0.3505737705 percentage points**. The candidate retains the failed compatibility check, keeps the source >=70 band unbounded, and treats reported SE as estimator uncertainty. These discrepancies argue against transferring the common level/age curve across both source populations; they are not hidden, tuned away or treated as a readiness blocker. Three constrained projections do not imply that all supplied evidence is reproduced.

Both `lifecycle.verify_candidate(bundle, 'candidates/initial')` calls and semantic preflights passed. Registered-source, frozen candidate, decision, analytic and semantic bindings were checked. Each root now contains `independent_review.json`, plus the independent non-sampling script and `deterministic_audit.json` under `independent_review_support/`. No generator or author calculation script was imported/executed; no rows, clinical target results, source replay, sampling or quadrature were used. Incidental caches, frozen files and decisions were left unchanged. No closure or final delivery occurred.

Readiness concerns implementation, finite probability laws, evidence accounting and integrity. Dependence, composition, selection, support restrictions, source law authenticity and transport remain scientifically unvalidated; unknown source-estimate, structural and transport uncertainty is not represented by seeded residual draws.

CHNS2009_E0_A04 bindings:

- Freeze: `930ac6e617e36153eef545169fac5bc8bf6e7a186774a0635ae196380806f844`.
- Decision: `a8de1af90f5966a03fc3034274f473517ba61a4297d5e65617d19de02ed22074`.
- Review: `53dca222d62f7b3d196930f565f878fcbddf40fd2bb5b132cbdf6d5a1023df46`.

ENSANUT2018_E1_A02 bindings:

- Freeze: `cb4a44510add464b4a629a977b855dad8c43e584965d4aacba940a0b2f0d09a1`.
- Decision: `3a7a462ebad9739f2b9294ee98a435f872a5018768bcd6ce07707f268229fd4c`.
- Review: `b506c1b11e357d92319baf1ac14a12fe31a694f5d8a4d6fdd665943ce5804298`.
