# HRS published-example comparison

3 November 2026. User-authorized continuation after manuscript v0.6. This is a new bounded public-example experiment, not a reopening of CHNS/ENSANUT. Its scientific question is whether the evidence-guided Agent can turn the public HRS generating information into longitudinal data supporting the original HbA1c–memory analysis.

## Task and information

Use the HRS recipient-stage component of Filshtein et al. (Epidemiology, 2021) and the public source repository at commit `6708e43d5e342fa76d57b31d5a6d0bfcc2979539`. The admitted material includes printed generating coefficients, demographic counts, conditional-dispersion and random-effect parameters, original definitions/formulas and author-reported aggregate references. No source participant records, unpublished fitted objects or project-generated answers are available to either construction.

The source packet is intentionally rich. All reported numerical relationships may be used, including the scientific analyses subsequently evaluated. This is reconstruction and analysis-preservation on a native published example; there is no hidden-relationship or independent-patient-validation claim. The whole-cohort data product and its longitudinal analyses remain the purpose.

## Two constructions

1. **Published-law reconstruction:** an original mechanical implementation of the published HRS recipient law from its rounded exported parameters. Missing serialized R model objects are replaced by their explicit prediction formulas. It is not a bitwise rerun or the full two-cohort pooling/MICE pipeline.
2. **Scientific Agent:** one fresh author context receives the common source packet, task, analysis definitions and harness interface. It chooses its scientific law and parameters from that information and records assumptions. The Agent may choose the published family. It does not see the other candidate, private review outputs, new generated tables or new evaluation results before freeze.

The coordinator fixes schema, task, evaluation and budgets, not the Agent's relationship signs, coefficients or family. Native-model coefficients in the common source material are allowed reported evidence, not manually chosen target answers. Evidence preprocessing and study selection remain researcher assisted. Agent general-tool access is procedurally scoped; only generator execution is technically isolated.

## Fixed output and allocation

- 11,509 synthetic subjects per release, four visits at 0, 2, 4 and 6 years: 46,036 rows.
- Exact columns: `id`, `subject_id`, `visit_time`, `baseline_age`, `age`, `age60`, `sex`, `race`, `educ`, `cses`, `hba1c`, `mem_s`. Unique visit `id`; stable repeated `subject_id`. Evaluator derives spline terms.
- Canonical factors: sex `female/male`, race `white/black`, education `College/HS/LessThanHS`; references female/white/College.
- Seeds **6101, 6102, 6103** for each construction: **six final physical generation attempts**. Matching seed labels do not imply matched random numbers across different code.
- No clinical exploration draws, outcome-guided scientific revisions, refits, alternate laws or best-seed selection. Mechanical errors can be fixed before release using invented inputs; actual final-run failures remain spent attempts.
- Both candidates, their source bindings, the native evaluator and runtime definitions must be fixed before any final generation. Then generate all releases and evaluate all available outputs together.
- Per generator attempt: isolated existing WSL/bubblewrap backend, 120 seconds, 1,024 MiB memory, 30,000,000 output bytes, 100,000 log bytes. No fallback local execution.
- Per longitudinal model fit: one native lme4 fit, 300 seconds, no automatic optimizer retry. Record model warnings, convergence, singularity and numerical output. Numerical independent GLS checks may use the fitted variance components; they do not constitute a second scientific fit or independently validate the optimum.

Invented input tests do not count as HRS tables, but their data and purpose must be identified. No new source IPD, account, paid API, model training or HPC is needed. Necessary runtime dependencies are installed only in a project/user library; setup traffic and downloaded artifact bytes are recorded separately from biomedical data. Existing download restrictions remain in force; a large runtime build is a reason to stop this example rather than expand indefinitely.

## Scientific evaluation

Use the original HRS longitudinal specification:

`mem_s ~ age60 * (U65 + O65 + race + educ + sex + cses) + (1 + age60 | subject_id)`

where `age60=(baseline_age+visit_time-60)/10`, `U65=min(hba1c-6.5,0)`, and `O65=max(hba1c-6.5,0)`. Use native factor contrasts and source-specified fitting convention, to be verified in the evaluator specification before release.

Report all 16 fixed effects and standard errors, including both focal age-by-HbA1c interactions, covariance/dispersion estimates, warnings and fit status. Apply all relevant native HRS distribution checks with their actual subject/visit denominator. The final analysis manifest must enumerate them before release. Compare with published aggregate references at their reported precision and with supplied generating coefficients separately. Source estimates from 43,500 observed visits and synthetic balanced schedules of 46,036 visits have different observation patterns; do not claim equal precision or an exact reproduction of 5,000 published simulation repetitions.

Show every final seed. For each estimand, report the mean of estimates, seed range, signed discrepancy of that mean and mean absolute discrepancy; do not confuse these summaries. There is no overall winner requirement, pooled heterogeneous accuracy score, post-hoc clinical equivalence threshold or invented independent truth. Complete results determine which original scientific relationships the delivered tables retain.

## Closure

Stop after the six fixed attempt slots and complete aggregate verification, regardless of method ordering. Preserve incomplete slots and numerical failures; no silent regeneration. If the public parameter adapter or native mixed-model runtime cannot be established without unreported parameters or substantial model redesign, close with that specific blocker and the completed preparation. Publish original code, manifests and aggregate findings only; third-party source files and generated individual tables remain local.

This protocol fixes the scientific allocation. The subsequent release record binds final source, candidate and evaluator bytes after the implementation checks; it does not change these limits.
