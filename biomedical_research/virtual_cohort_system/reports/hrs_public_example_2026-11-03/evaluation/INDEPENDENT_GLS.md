# Independent conditional-GLS check for the HRS example

3 November 2026. This implementation independently checks the native mixed-model fixed-effect arithmetic. It does not fit a generator, draw participants, optimize variance components, or validate biological assumptions.

## Input and output contract

The CLI accepts one final generated CSV and the corresponding native evaluator JSON. It creates only an aggregate JSON review and refuses to overwrite either input or an existing review.

```text
python independent_gls.py --input-csv final.csv --native-json native.json --output-json independent.json
```

CSV columns required:

```text
id, subject_id, visit_time, baseline_age, age, age60,
sex, race, educ, cses, hba1c, mem_s
```

The input uses `female/male`, `white/black`, and `College/HS/LessThanHS`. Each subject has exactly four visits at years 0, 2, 4 and 6. Visit identifiers must be unique. Baseline age, sex, race, education, CSES and HbA1c must be constant within subject. Age must equal baseline age plus visit time, and `age60=(age-60)/10`. These are native-example coding and longitudinal-layout checks, not plausibility tests against unpublished patient values.

The native fit JSON supplies:

```json
{
  "input_sha256": "hash of the same final CSV",
  "fixed_effects": [{"term": "(Intercept)", "estimate": 0.0, "se": 0.1}],
  "random_effect_covariance": [[0.4, -0.025], [-0.025, 0.06]],
  "random_effect_covariance_terms": ["(Intercept)", "age60"],
  "residual_variance": 0.12
}
```

The displayed numbers are invented schema examples, not study parameters. The actual `fixed_effects` list must contain all 16 uniquely named terms. Native factor labels are `Female/Male`, `White/Black`, and `College/HS/LessThanHS`, with Female, White and College as references. The optional covariance-order key, when supplied, must have the order shown.

The CLI requires the native JSON's `input_sha256` to match the supplied CSV. The review records source CSV, native fit JSON and its own code SHA256 hashes; runtime versions; all 16 coefficient and SE comparisons; the information-matrix condition number; sample and subject counts; and explicit pass, mismatch or unavailable status. No individual rows or predictions are written to its output.

## Independent calculation

The design matrix is constructed directly from the canonical CSV. It does not use `model.matrix`, an exported native design, R or lme4. The two HbA1c terms are `min(hba1c-6.5,0)` and `max(hba1c-6.5,0)`. Main effects are followed by seven interactions with age60, giving these terms:

```text
(Intercept), age60, hba1c_U65, hba1c_O65, raceBlack,
educHS, educLessThanHS, sexMale, cses,
age60:hba1c_U65, age60:hba1c_O65, age60:raceBlack,
age60:educHS, age60:educLessThanHS, age60:sexMale, age60:cses
```

For each subject, `Z_i` has columns 1 and age60, and the marginal covariance is `V_i = Z_i G Z_i' + residual_variance * I_4`. Cholesky whitening accumulates `A = sum(X_i' V_i^-1 X_i)` and `b = sum(X_i' V_i^-1 y_i)`. The checker solves `A beta = b`; standard errors are the square roots of the diagonal of `A^-1`. This is the conditional GLS identity for the fitted linear mixed model.

The native covariance must be finite, symmetric and positive semidefinite; a singular random-effect covariance is allowed, provided the positive residual variance makes the four-visit marginal blocks positive definite. A rank-deficient fixed-effect design cannot pass by dropping coefficients. Default comparison tolerances are absolute `2e-8` and relative `2e-7`; both coefficient and SE comparisons are required for every term.

## Meaning and limits of a pass

A pass checks treatment coding, HbA1c knot placement, decade scaling, interactions, subject grouping and fixed-effect/SE algebra against the independently built design, **conditional on the variance components reported by lme4**. It can detect mismatched coding and a changed coefficient even if the native model converges.

It does not independently establish that the native variance optimizer found the REML optimum, validate variance-component or log-likelihood calculations, establish convergence or absence of singularity, verify a source-paper extraction, or validate clinical truth. Native convergence and singularity diagnostics remain separate reported outcomes. Generated tables are not additional real participants.

## Invented-data check completed

`python independent_gls.py --self-test` ran once with 48 invented subjects and 192 in-memory observations. It created no file and read no clinical or generated-study table. Five checks passed:

1. All 16 coefficients and SEs agree with a separately assembled dense covariance GLS calculation. Maximum absolute coefficient difference was `1.6375789613221059e-15`; maximum SE difference was `2.1094237467877974e-15`.
2. Adding 0.01 to one native interaction estimate yields mismatch.
3. Inconsistent age60 scaling is rejected.
4. An indefinite random-effect covariance is rejected.
5. Female/White/College, age 60, HbA1c 6.5 and CSES 0 produce the expected intercept-only design row.

Runtime for this check: Python 3.12, NumPy 2.4.5. Only these invented checks have been performed by this implementation unit; no formal HRS table has been fitted or evaluated here.
