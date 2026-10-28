# Direct Agent records and an Agent-designed generator

Development pilot, 27 October 2026. All candidates were frozen before relationship evaluation.

**Direct record generation is operationally feasible and should remain a candidate route. In this one attempt, correcting marginal distributions substantially improved source reconstruction but worsened the overall error on unprovided relationships. The independently designed program matched the supplied margins almost exactly, without achieving lower overall relationship error.** These results do not establish a generally superior method or validate synthetic patients as substitutes for empirical data.

## What was actually executed

Two fresh-context Agents received the same permitted evidence: five-visit means, sample SDs and observation counts for five variables, measurement definitions, and one external PFS–DD100 correlation with its population and uncertainty. Neither builder received real patient rows, previous generator code, previous performance, target relationship values, or the evaluation query definitions. Neither performed web retrieval. This run used local session subagents, not a comparison of three external model providers.

The task was 75 people at months 0, 3, 6, 9 and 12, with weight, Power of Food Scale (PFS), No-Go commission errors (GNG), and delay-discounting AUC for $100 and $1000. The target is the existing Ross obesity intervention development cohort. The target-derived marginal packet is not a paper-only or zero-target-data input condition.

| Route | Agent-controlled generation | Numerical processing | Revision |
|---|---|---|---|
| Direct records | Explicitly authored all 1,875 value/null slots, including individual trajectories and missingness | Flatten literal arrays into visit rows; divide an explicit PFS sum by 15; validate only | One revision changed 288 explicit values using permitted marginal feedback; masks unchanged |
| Population program | Selected and implemented nonlinear hierarchical trajectories, response heterogeneity, cross-variable coupling and missingness | Seeded simulation, nonlinear transforms, finite-cohort moment/lattice calibration | No model change; final generator is byte-identical to initial; documentation qualification added |

The program route was not supplied the prior copula model or a fixed stable-only update. Its parameters still include substantial assumptions. “Agent-designed” describes who proposed the executable model; it does not make its assumptions learned, identified, or biologically verified. The direct route's literal records are a different operational generation path, not a claim to inspect the language model's internal computation.

Both routes received one source-only feedback opportunity. The main program seed was fixed at 273001. A second seed was used only to test RNG behavior, never to select a cohort. The final proposals were retained regardless of scores; there was no return to a better-scoring initial version.

## Frozen results

The evaluator reused all 10 variable pairs at month 12 and all 10 pairs of individual month-12 minus month-3 changes. Each family has equal weight. Error is the absolute difference between synthetic and real sample Pearson correlations, averaged across queries; lower is better. These are development diagnostics on an already-used cohort, not a new untouched test or a complete replay of every analysis in the original paper.

| Frozen cohort | Mean error / source SD, averaged over 25 margins | Mean relative SD error | Month-12 rMAE | Change rMAE | Overall rMAE |
|---|---:|---:|---:|---:|---:|
| Direct initial | 0.045630 | 9.8376% | 0.150607 | 0.157673 | 0.154140 |
| Direct final | 0.004943 | 0.5269% | 0.140993 | 0.208881 | 0.174937 |
| Program initial | 6.557e-8 | 0.00001135% | 0.200375 | 0.181954 | 0.191165 |
| Program final, unchanged | 6.557e-8 | 0.00001135% | 0.200375 | 0.181954 | 0.191165 |

All four cohorts passed schema checks and all 20 queries were evaluable. The fixed primary comparison, program final minus direct final, is **+0.016228 rMAE**, numerically favoring direct final in this run. There is one proposal lineage per route and one retained program draw; no method-performance confidence interval or significance claim is justified. Program initial/final are the same cohort, not two independent replications.

![Source reconstruction and unprovided relationship errors](report/route_comparison.png)

Full numerical results: [all 80 query rows](evaluation/results/all_query_replays.csv), [metrics](evaluation/results/metrics.json), [combined source and relationship scores](report/source_and_relationship_scores.csv).

## What this exposes

The direct revision improved its mean and SD fit, while overall relationship error increased by 0.020797. Endpoint rMAE decreased by 0.009614; change rMAE increased by 0.051208. Thus marginal improvement and preservation of longitudinal joint behavior separated in this particular revision.

One descriptive, post-evaluation localization illustrates the failure. For changes in PFS and DD1000, real sample r was -0.189439, direct initial r was -0.187725, and direct final r was +0.098190. That pair's error grew from 0.001714 to 0.287629. This example was inspected after evaluation, is not a new primary endpoint, and does not prove that the initially close value was more than accidental. Every other pair remains in the full table.

There is a structural reason this is possible. Even matching each visit's means and SDs does not constrain the cross-time covariance terms:

`Cov(X12-X3, Y12-Y3) = Cov(X12,Y12) + Cov(X3,Y3) - Cov(X12,Y3) - Cov(X3,Y12)`.

The supplied summaries do not identify these four terms. Altering selected values to fix per-visit spreads can alter trajectories and their coupling. Preserving old synthetic correlations would not by itself solve the problem: they can also be wrong. This pilot identifies a failure mode worth testing, not an established new scientific phenomenon or a validated remedy.

The program's almost exact marginal fit is expected from its calibration step. Its lower change error than direct final, but higher endpoint and overall error, gives no basis for choosing it solely because it is more elaborate or has better-looking marginal statistics. More model freedom did not demonstrate an overall advantage here.

## Implementation audit

An independent source-only reviewer reconstructed the direct CSVs and reran the program. All four outputs had 75 unique trajectories, 375 visit rows, 1,681 observed values and 194 missing slots. All 25 observation counts and checked supports/lattices matched. The direct change ledger matched exactly 288 altered slots, with zero mask changes. Initial artifacts retained their hashes.

The program passed same-seed reproducibility, different-seed responsiveness, unchanged global RNG and input-evidence checks. Perturbing permitted evidence changed its output. Interface probes at n=1, 2, 31 and 76 passed the tested schema constraints. Those probes were not alternative evaluated candidates. The audit found no unresolved concrete defect within its scope. Existing converter/evaluator tests covered 4 and 17 cases respectively, including full evaluator CLI fixtures.

The reviewer corrected one reporting overstatement: observation ranks are independent of pre-calibration latent outcomes, but the final finite-cohort calibration depends on the realized observed mask. Neither final-value MCAR nor iid records follows. Conventional synthetic-row standard errors are not demonstrated to represent real population uncertainty.

The audit and its artifact hashes were included in [IMPLEMENTATION_AUDIT.md](IMPLEMENTATION_AUDIT.md) before [freeze.json](freeze.json) was written. The evaluator verified frozen input hashes and the real-reference hash before reading the data. A separate post-run reviewer then passed 154 hash checks and 2,105 arithmetic/structure checks, independently recomputing all 100 real/synthetic Pearson estimates and all 80 errors with person-ID merges and scipy.stats.pearsonr. The maximum correlation discrepancy was 4.44e-16; no discrepancy exceeded 1e-12. Source summary arithmetic also agreed. See [independent verification](postrun_review/VERIFICATION.md). No frozen candidate changed.

## Limits and next discriminating experiment

- The real reference has 75 people, and its correlations are sample estimates with uncertainty. Matching them is not proof of population truth.
- These target marginals and diagnostic families have been used before. The coordinator knew previous results. Fresh builder contexts reduce direct leakage, but are a procedural separation, not a security sandbox or proof of absence of pretrained knowledge.
- The one external relationship does not identify longitudinal mechanisms, cross-lag coupling, response subgroups or missingness. Agent choices about those quantities remain assumptions.
- One attempt per route and unmeasured provider-level token/compute budgets cannot establish a fair efficiency ranking, stable method ranking or model-provider comparison.
- The exact No-Go opportunity count remains unverified; 512 is a conservative schema bound. No generated count exceeded 103 in this pilot, which does not resolve the source-definition question.
- Neither privacy, causal effects, patient replacement, complete original-paper conclusion recovery nor cross-study superiority was tested.

Stop this run without repairing its relationship errors. Keep both routes. The next useful experiment is a prospective repetition across fresh Agent attempts and an independent public cohort, with a fixed evidence packet and analysis plan. Separate variability between Agent proposals from variability between samples of one program. Retain every initial/final proposal and measure whether source-only revision repeatedly improves or damages unprovided longitudinal analyses.

Only if that pattern repeats should we test a framework modification: require a revision proposal to identify which joint and cross-time relationships it can change, distinguish evidence-supported corrections from unconstrained changes, and produce multiple plausible completions where evidence is absent. Compare that policy with ordinary revision under the same information and feedback budget. Its benefit must be tested; simply penalizing change in an initially wrong synthetic relationship would not establish validity.

