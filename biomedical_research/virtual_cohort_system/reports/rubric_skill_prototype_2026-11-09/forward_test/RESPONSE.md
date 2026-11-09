# Bounded planning response

Fictional population planning only. No participant records are requested or produced. Each information condition is assessed using only its named sources. F1, F2 and F3 are the supplied fictional tables, not empirical samples; their stated quantities are exact population constraints.

## Prospective rubric

The following criteria and comparisons were fixed before running the calculations. There is no pooled score, significance target or invented clinical tolerance.

| ID; analysis | Basis and reference role | Check and comparison |
|---|---|---|
| R1; U1, U2 | Request and F1, Fictional summary table 1; task invariants and source reconstruction | Represent standardized A, B, C with zero means and unit variances; retain both requested Pearson estimands. Compare declared moments exactly. |
| R2; U1 | F1; source reconstruction | Compute population Pearson correlation A,B; require the exact stated value 0.3. |
| R3; U2 | Linear residualization with intercepts; algebraic consequence and task invariant | Verify a valid covariance matrix and strictly positive residual variances; compute correlation of the two residuals. Mathematical validity alone does not establish source reconstruction. |
| R4; U2 | Available joint evidence; source reconstruction when identified, otherwise no numerical reference | Determine whether the sources identify correlations A,C and B,C, or otherwise identify the residual correlation. If identified, compare exactly; if absent, report unresolved identification and descriptive scenario differences, with no pass threshold. |
| R5; U1, U2 use claims | F2 when available; source reconstruction of marginal shapes. Otherwise explicit assumptions, with no numerical reference | Separate evidence for marginal normality, joint Gaussianity and independence. Permit only claims supported by the condition's evidence and the executed law-level checks. |

These are population-law checks. Finite-table estimator performance, sampling uncertainty and source-population replay are outside this planning request.

## Executed implications

Write x = Corr(A,C), y = Corr(B,C). With F1's standardization, the population linear residuals with intercepts are A - xC and B - yC. Consequently,

    Var(A - xC) = 1 - x²
    Var(B - yC) = 1 - y²
    Cov(A - xC, B - yC) = 0.3 - xy
    U2 = (0.3 - xy) / sqrt((1 - x²)(1 - y²))

This is the requested residual Pearson correlation; it requires finite second moments and nonzero residual variances, not joint Gaussianity. It is not a regression coefficient or, without further assumptions, a statement about all conditional distributions.

For each declared law use mean zero and covariance `[[1,0.3,x],[0.3,1,y],[x,y,1]]`. Exact arithmetic in `calculate.py` produced `calculations.json`:

| Declared Gaussian law | x, y | Leading principal minors | Residual variances A, B | Residual covariance | U1 | U2 |
|---|---|---|---|---|---|---|
| Original candidate | 0, 0 | 1; 0.91; 0.91 | 1, 1 | 0.3 | 0.3 | 0.3 |
| Illustrative alternative for P1/P2 | 0.7, 0.7 | 1; 0.91; 0.224 | 0.51, 0.51 | -0.19 | 0.3 | -19/51 ≈ -0.372549 |
| Source-constrained P3 revision | 0.6, 0.6 | 1; 0.91; 0.406 | 0.64, 0.64 | -0.06 | 0.3 | -3/32 = -0.09375 |

All three symmetric matrices are positive definite by their positive leading principal minors. Their residual variances are positive. The 0.7 scenario is a mathematical counterexample selected to expose nonidentification, not additional evidence, a preferred value, a probability-weighted alternative or a bound. It uses no P3 information. Both P1/P2 scenarios have standard normal univariate margins by their declared Gaussian laws, yet their U2 values have opposite signs.

## Condition-specific findings and construction decisions

| Criterion | P1: F1 only | P2: F1 and F2 | P3: F1 and F3 |
|---|---|---|---|
| R1: variables, scaling, means and variances | Demonstrated for the declared candidate law; both estimands retained. | Same. | Demonstrated for original and revised laws. |
| R2: U1 reconstruction | Demonstrated: 0.3. | Demonstrated: 0.3. | Demonstrated before and after revision: 0.3. |
| R3: computable U2 | Demonstrated for candidate and illustrative alternative; positive definite matrices and nonzero residual scales. | Same. | Demonstrated for original and revised laws; valid computation alone does not save the original's source mismatch. |
| R4: U2 source reconstruction | Unresolved: x and y absent; candidate U2 = 0.3 is an assumption-dependent scenario. | Unresolved: normal marginal laws do not identify x and y or U2. | Original contradicted: F3 gives x = y = 0.6, so U2 = -0.09375. Revised law demonstrates exact reconstruction of that functional. |
| R5: permissible claims | Candidate's claim for both source relationships is unsupported; normal marginal shape, joint Gaussianity and independence of C are assumptions. | F2 supports the standard normal margins; joint Gaussianity and independence remain assumptions. The draft U2 claim is still unsupported. | Independence is contradicted by F3. Marginal normality and joint Gaussianity remain assumptions because F2 is not available here. Both revised Pearson functionals are source-supported. |

**P1 decision — retain only with a restricted use claim and explicit sensitivity.** The candidate is a valid construction matching F1 and reconstructs U1. Preserve U2 as a requested but unresolved source use; report its candidate-law value alongside the admissible alternative above. The source's missing joint information explains the gap, not a missing tool or a population-transfer issue. A check using same-population x and y (or direct evidence of this exact residual correlation) could resolve it. Retrieval is disallowed, so no source-reconstructed U2 conclusion is available now. If that conclusion is required, stop that use pending evidence; additional rows or noise cannot supply it.

**P2 decision — retain the same restricted construction and sensitivity.** F2, Fictional supplement table 2, adds exact univariate normality, which the candidate satisfies. The alternative also satisfies F1 and F2, so this addition cannot select U2's sign or value. Retain U1 as demonstrated and U2 as unresolved for source reconstruction. The resolving check remains joint evidence involving C; collecting more univariate marginal information would not address this finding. There is no reason to revise the moments solely because F2 arrived.

**P3 decision — revise the covariance to the third row's law.** F3, Fictional supplement table 3, directly supplies the missing x and y in the correct population and measurement. Replace both zero covariances with 0.6. The original U2 overstates the source-derived value by 63/160 = 0.39375 and has the opposite sign; this discrepancy is explained exactly by its incorrect independence assumption. It is not sampling variation. Recomputed means, unit variances, U1, covariance admissibility and residual variances remain supported after the correction. The resolving check is executed: the revised law gives U2 = -3/32. Retain the original candidate and its negative finding in the calculation artifact. Use the revised Gaussian law as one convenient construction supporting both population Pearson associations; do not claim that the entire source joint distribution has been recovered.

## Check record and use limits

Executed: read the specified skill, its two linked references and the source packet; derived the matching population residual estimator; ran one Python calculation using exact rational arithmetic; checked positive leading principal minors, positive residual variances and correlation bounds for all three declared laws; compared their moments with the condition-specific supplied constraints. Python exited successfully. The marginal-normality statement is a mathematical property of each declared Gaussian law, not a simulated goodness-of-fit test.

No participant table, finite-sample estimator run, source-population replay, literature retrieval, external data, outcome files or other project results were used. No confidence intervals or numerical tolerances are needed for the supplied exact fictional moments. Nothing here establishes finite-sample inferential calibration, real-person recovery, causality or the source's full joint distribution.
