# Static scientific attribution of the review branches

Date: 2026-11-10. This document extends, without changing, `SCIENTIFIC_ATTRIBUTION_REVIEW_INITIAL.md` and `CROSS_MODEL_INITIAL_ATTRIBUTION.md`.

## Boundary and result

This audit reads the four review artifacts and their exact two initial parents, including model explanations and program/specification differences. It does not execute author code or read diagnostic files, generated tables, target-reference summaries, or final evaluation results. The feedback agents' own decision records describe their received diagnostic observations; those descriptions were read as part of the attribution review, not independently verified here. No new source was obtained and no author received this audit.

**Three review branches retain their parent's scientific specification and code exactly. The only data-law revision changes the lipid parent's age distribution. It leaves its generated BMI, sex, TC, and HDL values unchanged when evaluated with the same seed.** This is an actual structural change with appropriately revised mathematical explanation, but it cannot improve the prespecified lipid component-inversion endpoint. Its effect on adjusted scientific analyses is a separate empirical question.

## Artifact identities

| Review artifact | SHA-256 |
| --- | --- |
| PNS_SOL_A_SECOND_LOOK | `2d8830bc9063af6f3178de9d8f762642c2cf449dd0fd5e9dd22b3609004e2de3` |
| PNS_SOL_A_FEEDBACK | `bdfd2e577a32e751835b88261bd8e951b5776b8b75b03cdfe7acaab40e1ede3d` |
| LIPID_SOL_A_SECOND_LOOK | `695fc05d5c84ed1535ed8170d03fba5c47d5b0db9947d06b4c6a8256a55cb935` |
| LIPID_SOL_A_FEEDBACK | `f5554714919588a0515d667919ad9c12dc42a4727116bf2765369d8be9930eea` |

## Paired branch classification

| Parent and branch | Scientific specification equal to parent? | Generator string equal to parent? | Actual change | Meaning |
| --- | --- | --- | --- | --- |
| PNS, ordinary second look | Yes | Yes | Adds review rationale and analytic support explanation | Reporting only; all three population-estimand declarations unchanged |
| PNS, generated-diagnostic feedback | Yes | Yes | Clarifies supplied observations versus author-performed checks, and population versus sample claims | Reporting only; scalar claims remain 3.877, 2.9835, and 0.6. Their explanatory text changes, not their law |
| Lipids, ordinary second look | Yes | Yes | Adds review rationale and explicitly notes possible HDL > TC | Reporting only; all three scalar estimands remain null |
| Lipids, generated-diagnostic feedback | No | No | Replaces shifted-lognormal age with shifted/scaled beta age on [18,100]; updates age provenance and raw-moment recipe | A real support/family revision. BMI/lipid margins, copula, latent age loading, sex mixture, and uncertainty policy stay fixed. All three requested scalar estimands remain null |

Dictionary equality and generator-string equality were checked by reading/parsing the JSON artifacts. No candidate program was executed to make this classification.

## PNS: retention is scientifically coherent

Both review branches correctly identify that the original completed law already has full-rank regressors, a conditional mean in the requested design space, centered covariate-independent residuals, and analytic positive BP/pulse-pressure support. The ordinary branch independently gives the same pulse-pressure bound established in the initial static review. It was not sent that review.

The feedback branch describes the supplied diagnostics as insufficient to justify changing a population parameter to match an individual draw. That is an appropriate interpretation. No branch obtains additional evidence for target residual dependence or scales. Neither branch silently changes source coefficients, hides a support transformation, or converts a sample statistic into an exact population claim.

The retained program must produce identical same-seed tables across both branches and the parent, subject to the same execution environment. Any reported difference in same-seed data would require an execution/packaging investigation, not a scientific attribution to review quality.

## Lipids: a genuine age-law revision, not a relationship-evidence update

### What motivated and justified the change

The feedback author reports that its supplied generated observations exposed extreme age-tail realizations. It selects 100 years as a finite upper support endpoint, explicitly labeling it assumed and not derived from a publication, target distribution, or diagnostic maximum. Its original lower endpoint 18 remains task-specified.

This is a defensible disclosed scenario choice, not a newly identified population fact. The target contract has no upper age eligibility limit. Changing the model's support does not discard rows, but it does assign zero generated mass to eligible ages above the chosen limit. That limitation remains in the response.

The ordinary branch instead retains the original unbounded age law and makes no new scientific claim. The contrast shows that generated diagnostics prompted one different modeling decision. It does not show that the new assumption is more transferable or that the resulting adjusted associations are more accurate.

### Exact change and mathematical consistency

The revision retains the assumed conditional age means of 42/44 years and SDs of 16/17 years. It replaces the positive lognormal age gap by an affine beta gap of span 82:

```text
d = upper - lower = 82
q = gap_mean / d
c = gap_mean*(d-gap_mean)/gap_SD^2 - 1
alpha = q*c
beta = (1-q)*c
age = lower + d*BetaQuantile(Phi(Z_age), alpha, beta)
```

These are the correct beta moment-matching formulas. Both fixed sex-specific shape pairs are positive: each desired gap variance is less than `gap_mean*(82-gap_mean)`. As a mathematical distribution, this gives the specified mean/variance and no endpoint atoms. Finite-precision endpoint behavior is an execution consideration, not tested in this static review.

The age transformation is monotone within each sex, so it preserves the specified conditional copula/rank relationships while changing raw covariances and higher moments. It does not guarantee that pooled age ranks or adjusted raw-scale regressions stay unchanged.

The author correctly replaces the former all-lognormal covariance recipe. With `f_s(z)` denoting the new age quantile transformation, latent age–lipid correlation `r`, and log-lipid SD `sigma`, it states:

```text
t = sigma*r
E[age*lipid | sex=s]
  = mean_lipid * integral f_s(z)*exp(t*z-t^2/2)*phi(z) dz
```

This follows from the conditional normal exponential moment and is appropriate for the final beta-age/lognormal law. The response then uses the mixed raw moments for the requested linear projections. It does not carry forward a lognormal age covariance formula after changing age, and does not reuse parent sample estimates as revised population values.

### What remains exactly invariant in a matched-seed execution

The code change adds deterministic CDF/quantile transformations after generating the same sex draws, three-dimensional lipid/BMI Gaussian block, and age innovation. It adds no RNG calls. Hence the parent and revised branch use the same arrays for:

- Participant identifiers and recorded sex.
- BMI, TC, and HDL values, including all their unadjusted marginal statistics and pairwise functions.
- Each row's indicator of HDL > TC.

Only age values change. The preserved latent age loading is still an assumption. The three requested analyses adjust for age, so their coefficients/residual correlation can change despite identical BMI and lipid observations. Such changes are not themselves improvements: the frozen evaluation must determine their direction and relevance.

### Component ordering remains unresolved by design

The revised program, like the ordinary review, leaves measured lipids unordered. It explicitly distinguishes absence of a task `TC>=HDL` exclusion from an error-free biochemical component law. No validated measurement-error mechanism for inversions is added. The law therefore retains its positive inversion probability and, with paired seeds, the exact same inversion counts as its parent.

## Consequences for the frozen experiment

1. **The primary coherence endpoint cannot improve in these particular branches under the static trace.** PNS branches are code/specification no-ops; lipid feedback changes only age. Report this even if secondary age-tail diagnostics look better. Do not replace the prespecified endpoint after seeing this revision.
2. **Feedback triggered one disclosed support revision.** This is a mechanism observation about these two parents, not evidence that feedback generally improves scientific usefulness.
3. **No new relation evidence was supplied.** Source-supported, derived, and assumed dependencies remain distinguishable. The change cannot resolve source-to-target transfer by itself.
4. **Numerical claim coverage did not increase.** PNS keeps its three supported scalar claims. Lipids keeps all three scalar values null and revises the analytic recipe appropriately. Honest nulls avoid false precision but are not new data-quality evidence.
5. **Data delivery remains a separate axis.** The PNS_DS initial output-interface defect identified in the cross-model audit must remain unmodified; its abstract law should not count as delivered data if execution fails. It is unrelated to the paired Sol review comparison.
6. **Proceed with the fixed evaluation rather than another repair round.** The static audit found no mathematical inconsistency requiring a root-authored change to the lipid revision. The planned fresh-seed evaluation should retain no-ops, failures, and all requested analyses. This audit authorizes no extra call, new case, search, or parameter adjustment.

No claim about target performance or overall quality improvement is made in this static review.
