# Controlled joint-moment diagnostic — completed 8 November 2026

**Decision: do not add the extra joint-consistency instruction as a claimed improvement on this evidence.** Ordinary construction and the additional instruction both recovered the same source-compatible Gaussian law. This is an artificial mechanism check, not a clinical validation or a test of retrieval/feedback revision.

## Question and information boundary

Can an ordinary scientific agent combine separately adjusted associations into a joint generator, or is an additional consistency instruction necessary? Both arms received the same 15 exact population summaries for four neutral variables: four means, four SDs, three predictor correlations and four coefficients from two separate regressions. The summaries determine the requested joint linear projection and residual variance; they do not uniquely determine the full distribution or its tails.

Two fresh construction contexts per arm received only their own request and source packet. O1/O2 received an ordinary evidence-based construction request. C1/C2 additionally had to reconcile the constraints jointly and account for explained versus residual variation. Neither arm received a solver, the target joint coefficients, the hidden covariance or desired signs. The root prepared the artificial fixture but did not write or tune the four authored programs. Author isolation was instruction-based; numerical execution used the existing offline worker.

The design and evaluation definitions were locked before sampling, and all four programs were sealed together before the batch. Each construction produced 10,000 rows for each of three fixed seeds (8101–8103). There were 12 planned attempts, 12 successful deliveries, no trials and no revision rounds. All 180 source-statistic calculations were available. No real participant data were used.

## Complete results

Coefficient entries are mean absolute standardized coefficient errors, averaged over the three seeds within a construction. The residual entry is the mean absolute log ratio of estimated to population residual SD, using sqrt(SSE / (n − design rank)). Arm means give the two constructors equal weight. Lower is closer to this artificial population. No clinical acceptance margin or significance test was selected.

| Constructor | Z coefficient error | X1 coefficient error | X2 coefficient error | Residual SD log error |
|---|---:|---:|---:|---:|
| O1 | 0.015541 | 0.008916 | 0.012062 | 0.004403 |
| O2 | 0.009337 | 0.011565 | 0.014677 | 0.007856 |
| C1 | 0.009337 | 0.011565 | 0.014677 | 0.007856 |
| C2 | 0.015541 | 0.008916 | 0.012062 | 0.004403 |
| O (equal-weight mean) | 0.012439 | 0.010241 | 0.013370 | 0.006129 |
| C (equal-weight mean) | 0.012439 | 0.010241 | 0.013370 | 0.006129 |

All four laws imply joint coefficients (Z, X1, X2) = (0.25, 0.65, −0.40) and residual variance 0.6775, up to numerical rounding. These quantities were not directly supplied to the authors but follow algebraically from the supplied summaries. Thus this is not recovery of an unconstrained relationship or discovery of a new biological fact. The remaining finite-table errors are compatible with sampling from those same laws; the diagnostic did not establish a clinical tolerance.

**Twelve deliveries are six distinct tables, four separately authored programs and one probability law.** O1 and C2 used the same normal-number layout, as did O2 and C1. Under each shared seed the corresponding pairs produced identical table hashes. Both arms therefore contain the same six numerical tables and have exactly equal arm summaries. This follows from the same law and RNG layout; it does not establish independent replication across six populations. The three seeds within each layout produce distinct tables.

## Checks, interpretation and cost

The [design review](DESIGN_REVIEW.json) checked that the source summaries imply the held-out linear estimands. The [implementation review](IMPLEMENTATION_REVIEW.json) checked operators, denominators, failure retention and aggregation using a separate deterministic algebra fixture before execution. The [numerical recomputation](INDEPENDENT_RESULTS_REVIEW.json) uses a different calculation; its author also implemented the primary runner/evaluator, so it is not a distinct-person audit. The [distinct-person results review](PERSONNEL_RESULTS_REVIEW.json) separately verifies the joint coefficients, residual SDs, hashes and arm equality from the existing rows. Neither results check regenerates data.

This task demonstrates that an ordinary agent can translate sufficiently informative, consistent aggregate associations into a generator that supports a joint analysis. It supplies no evidence that the additional instruction improves data quality. It does not test imperfect paper extraction, incompatible source populations, noisy estimates, nonnormal tails, retrieval gains, source-only revision or transport to a biomedical population. It therefore cannot explain all previous clinical mismatches as an evidence problem, nor certify every analysis of the generated records.

The existing-code audit also found numerical relationship use in all ten Q1/E1 constructors. We should not describe those authors as generally ignoring numeric evidence. Numerical use, simultaneous consistency of all adopted statistics and transport to a new population are different checks. Some Q5 constructions explicitly approximate a marginal association as a conditional effect; those are declared bridge assumptions rather than an established implementation bug.

Cost: four fresh constructor sessions, twelve bounded offline sampling executions and independent design/implementation/results checks; no new paid API, training or HPC. All sampling finished without retry. Exact backend model snapshot, token billing and human time savings were not metered. Generated row count is not a clinical sample-size gain.

The single-batch stopping rule is reached. No new case, constructor, seed or tuning is added to seek a positive component effect. Keep the simpler workflow. The remaining scientific priorities are accurate source definitions, justified population bridges and analysis-specific evidence—not a new loss, agent hierarchy or unverified correction layer.

## Reproducible record

[Protocol](PROTOCOL.json) · [Source packet](SOURCE.json) · [Evaluation definitions](EVALUATION_SPEC.json) · [Design lock](DESIGN_LOCK.json) · [Batch lock](BATCH_LOCK.json) · [Complete aggregate JSON](RESULTS.json) · [All per-run metrics](RESULTS.csv) · [Runner](runner.py) · [Evaluator](evaluate.py).

The artificial truth fixture is disclosed after completion for inspection. Authored programs/specifications are retained for O1, O2, C1 and C2. Patient-level data, private reviews and third-party documents are not part of this experiment. Per-row generated tables remain local in the public export; rerunning the archived protocol would be a reproduction rather than additional evidence for this batch.
