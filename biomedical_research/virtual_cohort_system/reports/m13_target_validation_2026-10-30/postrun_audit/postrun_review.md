# M13-B independent post-run audit

30 October 2026. Reviewer: `/root/m13b_audit`. **Arithmetic and artifact audit passed. The target findings show substantial transport errors and mixed effects of source-only revision.** No frozen code, candidate, protocol, acquired input or generated output was edited.

This audit was explicitly authorized after the single complete evaluator release. It uses the corrected private full frame, permitted input, all 16 generated outputs, execution/reference receipts and the aggregate release. Only aggregate audit artifacts are written. The accepted aggregate JSON SHA256 is `3644039b16b3cc90cec5432a88b2e2c2177c943ee85e93fa822da62e419d38f4`.

## Arithmetic and provenance

`audit_release.py` independently reconstructed the domain masks, fixed 62-endpoint schedule, covariate gates, weighted projections and tied inverse-ECDF quantiles. It used the separately written pre-access SVD/row-influence covariance kernel, not the evaluator's fitting functions. It recomputed every measured/generated endpoint and all paired linear difference intervals. A sorted-row inverse ECDF independently checked all quartiles and IQRs.

| Verified item | Result |
|---|---:|
| Complete panels | 1 measured + 16 generated |
| Endpoints per panel | 62; all estimable |
| Recomputed aggregate estimands | 1,054 |
| Linear estimands, including intervals | 238 |
| Quartile/IQR point estimands | 816 |
| Paired linear difference intervals | 224 |
| Numeric comparisons, including gates/errors/seed summaries | 8,492 |
| Maximum absolute numeric discrepancy | `6.09e-13` |
| Structural, gate and integrity assertions | 2,281 passing |
| Isolated Agent execution receipts | 12 verified, all successful |
| Published references | 4 formula/seed/rejection-stream/hash checks passed |

All 19 pre-access file hashes remain intact. All four deployed scientific candidates match their original generator/specification hashes and deployment freezes. Original source freeze identities also agree. Every generated output preserves the exact allowed covariates and row-key set, has the declared hash and contains finite body-fat values within [0,100]. The exact 12-Agent-plus-four-reference schedule is present, and no table or endpoint was dropped. The reference checks independently expand the Gallagher formula and reproduce each Gaussian rejection stream, including redraw counts.

The harness receipt verification checks recorded execution inputs, seeds, output bytes, candidate bindings and the documented generator-process isolation scope. It does not establish OS isolation of the LLM's general tools or scientific validity. No new generation was performed during this audit.

Detailed aggregate recomputation is in `independent_aggregate_recomputation.csv`; the counts, receipt statuses and maximum discrepancy are in `audit_results.json`. The preceding parser correction remains a separately recorded technical amendment; it did not change the 842 eligible participants or their permitted covariates.

## Principal target findings

The following generated values are arithmetic means over the three prespecified seeds. They are Monte Carlo summaries, not pooled inference. BMI coefficients have units of body-fat percentage points per 5 kg/m².

| Primary-domain estimand | Measured | Build01 source-reviewed | Build02 source-reviewed | Gallagher deterministic |
|---|---:|---:|---:|---:|
| Male mean | 23.764 | 19.064 | 20.034 | 20.308 |
| Female mean | 34.879 | 32.250 | 32.197 | 31.977 |
| Male BMI coefficient | 4.275 | 7.894 | 7.870 | 8.070 |
| Female BMI coefficient | 6.589 | 9.520 | 9.546 | 9.681 |

Both final generators understate primary-domain means and overstate adjusted BMI slopes. For each final builder, sex and seed, the paired mean-error interval is wholly negative and the paired BMI-slope-error interval wholly positive. These are pointwise conditional design intervals; they are not simultaneous guarantees, equivalence tests or complete model/transport uncertainty. The ordinary deterministic reference also shows mean underestimation and BMI-slope inflation, so these shared failures cannot be described as evidence of independent Agent discovery.

Age effects require a distinction between sign and uncertainty. The measured primary male age coefficient is `0.486` per decade, with 95% interval `[-0.401, 1.372]`. Both final builders give positive age point estimates and intervals wholly above zero in every seed. Agreement of point-estimate signs therefore does not reproduce the measured uncertainty conclusion. The measured primary female coefficient is `0.966 [0.368, 1.564]`, while both final builders also produce positive intervals. This more concordant result still concerns a supplied source relationship and does not demonstrate a causal aging effect.

Measured primary curvature is `-0.987 [-3.724, 1.751]` in males and `-1.229 [-3.017, 0.558]` in females. Both measured intervals include zero. Generated negative curvature signs alone cannot validate a target concavity claim, and a seed with a generated curvature interval excluding zero must not replace the full three-seed record. Similarly, the extension male age estimate is `-0.166 [-1.273, 0.942]`; its negative point estimate is not evidence of an established opposite age relationship.

## Effects of source-only revision

Build01's intended non-Asian male location shift lowers the three-seed primary male mean from `20.066` to `19.064`, while the measured mean is `23.764`. Its mean absolute error consequently worsens from `3.698` to `4.700` percentage points. The primary male BMI coefficient remains much too steep. Female outputs are unchanged by this source revision on the target domain. This is a direct example of improved source fitting not establishing improved target analysis.

Build02's residual-scale revision barely changes the primary means or the inherited BMI slopes. Using the prespecified **mean of per-seed absolute IQR errors**, it improves all six female cells, but worsens five of six male cells. The exception is males aged 20–39 at BMI 25–<30, whose IQR error decreases from `1.426` to `0.937`. These are descriptive cellwise changes, not an omnibus score or a controlled comparison of Agent quality.

Within the primary domain, the older female BMI 25–<30 cell has measured IQR `4.10`; final build01 and build02 three-seed IQR means are `7.77` and `6.56`. In the separate older female BMI 30–35 extension, measured IQR is `4.20`, versus `8.61` and `7.04`. Build02's female dispersion revision reduces these discrepancies without eliminating them. The full 12-cell record is retained in the aggregate recomputation rather than using these examples to select a favorable model.

The stochastic Gallagher reference is another useful check on interpretation: primary male curvature has an error of the seed-mean estimate near `-0.015`, but the mean absolute per-seed error is about `0.723`. Cancellation across seeds must not be presented as uniformly accurate draws. The release's separate signed and absolute seed summaries are arithmetically correct.

## What the distribution reuse and intervals support

All eight primary and four extension distribution cells pass the prespecified gates, so no conditional quantile result was removed for sparsity. These quartiles/IQRs are unfitted target checks, but their coarse cells retain age/BMI/race heterogeneity. Their IQRs are not pure residual standard deviations. Quartile/IQR uncertainty was deliberately omitted; their discrepancies must not be called statistically significant, calibrated, equivalent or clinically acceptable. A three-seed range is not a confidence interval.

The observed transport errors, favorable cells and source-revision trade-offs are all part of the same result. There is no prespecified clinical utility tolerance or aggregate success criterion. The analysis supports inspection of these generators for these fixed descriptive reuses; it does not establish measurement recovery, clinical substitution, collection-cost savings, causal effects or publication readiness. Source coefficient uncertainty, source-covariate reconstruction, DXA nonresponse, and measurement/population transport remain unresolved. The target is a new endpoint in a previously used survey cycle, not an entirely fresh cohort.

No further target-informed tuning or candidate selection is warranted within this frozen pilot. A new scientific revision would require a new reserved task rather than reusing this outcome release as confirmation evidence.
