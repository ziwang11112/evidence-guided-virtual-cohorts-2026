# What the A tables and the agent's within-band pairing each contribute

On the archived CHNS split, an A-only conventional statistical law met both original target-comparison margins. Its pooled Spearman correlation was **0.2370** against **0.3168** in B. Six original-evidence agents gave **0.2927–0.3201**. Removing within-band pairing from each agent's records increased absolute rank error in all six comparisons, by a median of **0.0612**. The crude threshold odds ratio is already available from the A counts.

This analysis was designed after the earlier CHNS B results were known. The new statistical law, source hierarchy, seeds and scoring were frozen before any of its scientific outputs were compared with B. The measured reference comes from 1,082 women in 107 communities. The evidence tables describe 1,123 other women in 110 communities of the same survey. Both groups contain women aged 18–49 from the 2009 wave. [Protocol](PROTOCOL.md) · [Original A tables](../chns_iron_conditional_holdout_2026-11-19/A_TABLES.json) · [Original prospective study](../chns_iron_conditional_holdout_2026-11-19/RESULTS.md)

| Construction | Pooled or expected Spearman | Absolute rank difference from B | Crude OR | Absolute log OR difference from B |
|---|---:|---:|---:|---:|
| Direct arithmetic on the A counts | — | — | 5.083 | 0.187 |
| Statistical law with independence within Hb bands | 0.2370 | 0.0798 | 5.023 | 0.175 |
| Six agent laws, expected after within-band re-pairing | 0.2444–0.2489 | 0.0679–0.0724 | 4.998–5.175 | 0.170–0.205 |
| Six agent laws, original pairing | 0.2927–0.3201 | 0.0008–0.0241 | 4.998–5.175 | 0.170–0.205 |

Measured B rank was 0.3168 (95% community-bootstrap interval 0.2594–0.3732). Its crude OR was 4.218 (2.979–6.042). A-table arithmetic identifies a threshold association and leaves continuous ordering open. Positive dependence between the three Hb bands accounts for much of the whole-cohort rank even in the law with conditional independence. All six original models were closer on rank than the conventional law, with both sides already inside the 0.10 planning margin. The factor-of-1.50 OR margin was also met by all. Table ranges cover the six constructions. The target intervals describe variability across sampled communities.

## Within-construction comparison

| Original-evidence parent | Authored rank | Expected re-paired rank | Authored rank error | Error of expected re-paired rank | Paired reduction | Unchanged OR |
|---|---:|---:|---:|---:|---:|---:|
| Ordinary 1 | 0.3003 | 0.2444 | 0.0165 | 0.0724 | 0.0559 | 5.102 |
| Ordinary 2 | 0.3078 | 0.2464 | 0.0090 | 0.0704 | 0.0614 | 4.998 |
| Ordinary 3 | 0.3176 | 0.2447 | 0.0008 | 0.0721 | 0.0713 | 5.108 |
| Guided 1 | 0.2927 | 0.2473 | 0.0241 | 0.0695 | 0.0454 | 5.119 |
| Guided 2 | 0.3075 | 0.2465 | 0.0093 | 0.0703 | 0.0610 | 5.120 |
| Guided 3 | 0.3201 | 0.2489 | 0.0033 | 0.0679 | 0.0647 | 5.175 |

Re-pairing permutes ferritin among records in each of the three Hb bands. It fixes each law's own band-specific empirical marginals and all four threshold counts exactly. Conditional on those records, the expected within-band covariance of the two global midranks is zero. The between-band covariance therefore gives the expected Spearman correlation without Monte Carlo permutations. The comparison uses the error of the expected correlation. Summing the saved between- and within-band components recovers each original rank to numerical precision. A positive paired reduction means the authored pairing brought the correlation closer to the observed B value. [Original decomposition](../chns_iron_conditional_holdout_2026-11-19/RANK_COMPONENTS.json)

An independent implementation also read the 18 archived control draws, checked every file hash, recomputed the six original ranks and their exact re-pairing expectations, and verified the four threshold cells under a within-band reversal. A small enumeration with tied ranks verified the expectation against every allowed permutation. [Verification receipt](PAIRING_VERIFICATION.json) · [Verification code](verify_pairing.py)

## Statistical construction and checks

For the lower and middle Hb bands we fit scaled beta distributions to the supplied means and SDs. For the upper band we fit a shifted gamma. In each band we fit the maximum-entropy law on log ferritin subject to its mean, variance and depletion probability. This is a normal density reweighted across the log threshold. Conditional independence supplies the single missing dependence assumption in this construction. All fitted band masses, conditional means, SDs, geometric means, geometric SDs and depletion probabilities matched the rounded A inputs to numerical precision. The fitted law's population Spearman correlation was 0.2414 and its population OR was 5.083. The latter equals the direct A arithmetic. [Source model](source_model.py) · [Source-only results and draw hashes](SOURCE_RESULTS.json)

| Prespecified draw | Records | Spearman | OR |
|---|---:|---:|---:|
| 191901 | 12,000 | 0.2456 | 5.213 |
| 191903 | 12,000 | 0.2451 | 5.095 |
| 191909 | 12,000 | 0.2198 | 4.767 |

The comparison pools all three draws to match the published agent analysis. Each estimate passed an independent average-rank correlation and four-cell odds calculation. A replay regenerated all three submitted byte hashes on the recorded installation. One conventional law, 36,000 new virtual rows, zero new participant records and zero model calls. All generated rows remain local. [Freeze receipt](FREEZE.json) · [Aggregate comparison](RESULTS.json) · [Replay command and code](run.py)

## Interpretation for the manuscript

This split gives a specific example of added analysis utility. Relative to independence within the supplied Hb bands, the agents' choice of pairing made continuous rank estimates closer to the measured B estimate. The within-law comparison fixes each agent's marginals, whereas comparison with the independently specified law also changes their shapes. The improvement concerns the archived point estimate on one survey split and one model configuration. Errors in different bands can cancel. The result alone cannot establish that an agent recovered the biological dependence, that an agent is necessary, or that it will be more accurate in another population. The earlier incremental test of the added A contrast still improved the prespecified whole-cohort rank for one of six authors. That paired intervention has a different scientific question and denominator.
