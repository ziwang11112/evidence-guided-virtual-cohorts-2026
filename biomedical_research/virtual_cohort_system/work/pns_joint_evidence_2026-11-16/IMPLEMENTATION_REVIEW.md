# Implementation review — completed PNS evidence increment

Root-led original-code and artifact inspection; independently coded numerical recomputation. No second blinded scientific reviewer or human domain review is claimed.

## Inputs and freeze

- Baseline packet remains byte-identical to the historical packet. Both payloads share the task and requested-analysis objects; only the additional-source object differs.
- Source Agent selected papers using no supplied target estimates. Source proposals were checked against archived original methods/tables. The Burkina Faso algebra was recomputed by Schur complement and independently by QR of a covariance fixture.
- Six fresh author calls received only the approved payload. Complete source-search and constructor records are retained. Source materials are inputs, not executable instructions.
- Generation freeze: `b297c1818c78c47bf081fdf9f246ff434a650a88476acf72cfca12a98e8eeaf5`.
- No root edits to generated scientific code/parameters. Program interfaces were parsed and statically validated, never imported on the host. Failures would retain their slots; none occurred.

## Runtime and estimator

The new orchestrator uses the existing provider client and source-tool runtime. Each program runs through the existing worker in WSL/bubblewrap, with a curated filesystem, no target/reference mounts and no network. Pre-import probes were checked for every successful execution. The staged scientific files are hash-bound and read-only. All constructors closed before draws; all draws closed before the old aggregate reference was parsed by the comparison routine.

The production estimator is the unchanged PNS regression adapter. Independent saved-row recomputation uses QR least squares and centered residual dot products, not the production weighted/SVD routine. It agrees on all 108 endpoint values to 5.23e-13. No real patient data or target refit occurred. All model and generated-table hashes are retained; zero scientific retries or repairs.

## All six laws inspected

| Constructor | Original selected law | Material relationship choice | Mathematical/semantic audit |
|---|---|---|---|
| ORIGINAL_1 | Shifted-lognormal BMI; conditionally truncated bivariate t, df7; age-60 hinge | Pre-support correlation 0.55, SDs17/10.5 | Bounded accepted support gives finite moments; hinge and rejection mean the requested residual is not exactly this parameter |
| ORIGINAL_2 | Truncated lognormal BMI; conditionally truncated bivariate t, df7; quadratic DBP age term | Pre-support correlation0.50, SDs16/10 | Shared chi-square multiplier has correct variance standardization; bounded output; source raw dependence is explicitly not a residual estimate |
| ORIGINAL_3 | Truncated lognormal BMI; heteroscedastic conditioned bivariate t, df7 | Pre-support correlation0.55; SBP SD increases with age | Finite bounded outputs; no treating heterogeneous conditional covariance as exact requested Pearson |
| AUGMENTED_1 | Beta covariates; bounded beta DBP error plus independent centered gamma SBP innovation | Model residual correlation0.70, SDs17/11 | All gamma moments finite; not compact SBP support. Analytic lower bounds prove DBP>45.03 and pulse pressure>11.74. Fixed model assumption, not target-identified correlation |
| AUGMENTED_2 | Beta covariates and independent bounded beta residual components | Model residual correlation0.72, SDs16/10 | Covariance algebra matches code. Analytic lower bounds prove SBP>56.43, DBP>43.94 and pulse pressure>12.49. No sample-wise moment forcing |
| AUGMENTED_3 | Truncated lognormal BMI; conditioned bivariate Gaussian; nonlinear age hinge | Innovation correlation0.70, SDs17/11 | Nonsingular covariance and nonempty acceptance region; all delivered variables bounded. Correct warning that requested projection differs from nominal parameters |

The two exact-residual constructions use the requested covariate design, independent mean-zero residual components and nondegenerate covariates. Their population projection identities follow algebraically; finite draws need not equal the parameters. The other four laws explicitly alter those identities through omitted nonlinear age terms, heteroscedasticity or conditional support restrictions.

Five laws bound accepted BP values. The remaining gamma law is unbounded above but has finite moments; do not describe all six as bounded. Fixed supports and gamma/t/beta shapes are Agent assumptions. Mathematical validity does not establish physiological tail realism.

All six use the converted INTERSALT BMI anchors3.877/2.9835 before any projection changes. Their persistence helps explain why extra joint evidence can improve paired dependence while leaving the DBP slope discrepancy. This explanation is a modeling inspection, not a separate intervention identifying the cause of every observed error.

The provenance records distinguish source raw correlations, source multilevel components and chosen target covariance. The two additional sources are used to motivate quantitative scenario choices, not as a validated pooled estimator. A source consistency check cannot be replaced by applying a different source operator to these target-population rows; no such passed replay is claimed.

## Audit artifacts

- `review/first_five_static_review.json`: recorded before target comparison; exact candidate hashes.
- `review/analytic_AUGMENTED_1.json`, `review/analytic_AUGMENTED_2.json`: support/covariance calculations, no generated or target inputs.
- `analysis/INDEPENDENT_RECOMPUTATION.json`: independent-estimator agreement.
- `analysis/details.json`: complete scale, range, duplicate, rank and component diagnostics.
- `analysis/COSTS.json`: all six returned model IDs, usage and combined search/construction cost.
- Figure rendered and visually inspected; all six constructors and three primary analyses are visible, with Monte Carlo ranges explicitly distinguished from confidence intervals.

No critical execution defect was found. Remaining scientific weaknesses are partial source applicability, assumed demographic/conditional laws, no source-specific generative replay, no propagated transport uncertainty, one historically exposed case and three constructions per evidence arm. These limits do not negate the observed joint-analysis improvement, but limit its generalization.
