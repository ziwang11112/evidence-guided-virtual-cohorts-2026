# From distribution fit to downstream analysis utility

27 October 2026. **The user's distinction changes the interpretation of the route screen.** Matching input means and SDs is a reconstruction check. Average correlation error compares real and synthetic joint statistics, but it is not sufficient evidence that the data support the intended paper analyses. The appropriate question is whether the same scientifically relevant analysis gives compatible effects and uncertainty on real and generated records.

This extension used unchanged, previously frozen cohorts. It ran the same existing analysis function on real data and all four initial/final synthetic cohorts: six baseline correlations, 25 time contrasts and four standardized pooled weight association models. All 140 synthetic analysis rows completed successfully. Program initial/final are identical, leaving three unique synthetic cohorts. The new analysis is explicitly post hoc on an already-used development cohort; no claim of a new independent test is made.

## Results tied to the paper's scientific questions

[Ross et al.](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0243530) studied food reward sensitivity, impulsivity and weight during and after an intervention. The categorical-time mixed model reproduces major published effect estimates and SEs closely. The article does not fully specify its association-model formula, scaling and inference, so the four models below are transparent analysis-utility tests, **not exact reproductions of the published association coefficients**.

Each association uses `z(weight) ~ z(predictor)` with participant random intercept, REML, and visitwise complete observations. There is no time or demographic adjustment. Coefficients combine between-person and within-person information; they are not causal effects, Pearson correlations, or pure within-person effects. Standardization is calculated separately within each fitted dataset.

| Analysis | Real-data estimate | Direct initial | Direct final | Program initial/final |
|---|---:|---:|---:|---:|
| Weight change, month 3 minus baseline, kg | -6.0160 | -5.4349 | -5.5062 | -5.6938 |
| Weight change, month 12 minus month 3, kg | +2.3913 | +3.0894 | +3.0878 | +2.6781 |
| Standardized PFS association with weight | +0.1657 | +0.3770 | +0.3784 | +0.1431 |
| Standardized No-Go association with weight | +0.0998 | +0.1779 | +0.1227 | +0.0721 |
| Standardized DD100 association with weight | -0.0183 | -0.2407 | -0.2719 | -0.1324 |
| Standardized DD1000 association with weight | -0.0038 | -0.1780 | -0.1483 | -0.0583 |

The program final coefficient is closer to the real estimate than direct final in three of four pooled association models: PFS, DD100 and DD1000. For GNG, direct final is slightly closer (absolute errors 0.022817 versus 0.027692). This differs from the earlier overall pairwise-correlation-error ordering. Neither is a general method ranking: each examines a different use, and only one Agent proposal lineage per route was evaluated. All six headline rows were chosen from the paper's questions before this new synthetic replay, and all 35 analyses per cohort remain available. Independent audit corrected an initial coordinator statement that the program was closer on all four associations; no numerical output or candidate changed.

The association results also expose material remaining failure. Real-data DD100 has beta -0.0183, SE 0.0487, whereas direct final has beta -0.2719, SE 0.0298 and program final has beta -0.1324, SE 0.0317. Synthetic records produce stronger negative association and smaller model SEs. Both synthetic routes give p<.05 for all four pooled associations, while the real-data version has p>.05 for GNG/DD100/DD1000. This is descriptive disagreement in three analyses, **not an estimated false-positive rate**, and a real-data nonsignificant result does not prove a zero population effect.

![Downstream association effects](results/downstream_associations.png)

Normal-Wald synthetic intervals are pipeline outputs, not validated intervals for real population effects. The generators condition on finite-cohort summaries and include arbitrary dependence assumptions. The main evaluation therefore presents coefficients, SEs and intervals together; p-value agreement alone is not a quality criterion. Increasing synthetic sample size cannot create new empirical information.

Time-effect agreement is partly constrained by supplied visit means. The previously identified, unverified month-9 source weight anomaly also strongly influences the real time-model SEs. Main data are unchanged. [weight_sensitivity.csv](results/weight_sensitivity.csv) separately repeats the already-defined one-observation influence analysis; it is not a corrected dataset or a route-selection criterion.

## Scope of what has and has not been checked

This adds direct downstream analysis to the earlier distribution and relationship diagnostics. It does not yet reproduce every central paper model: baseline predictors of later weight change, interactions, change–change predictor models, PFS subscales and all adjacent-visit contrasts remain outside this replay. We cannot claim preservation of the complete article's conclusions. Original SAS denominator-df inference is also not exactly reproduced.

The old analysis module, original data, and all four generated datasets retained their hashes. No generator was revised using these new outputs. The protocol and execution script were locked before this run; because earlier target results were already known, that is an execution integrity record rather than prospective preregistration. Implementation review also checked that repeated visits were grouped by person and contrast SEs included fixed-effect covariance. An independent result audit passed 1,523 checks and reproduced all 35 analyses for real data and all three unique synthetic datasets exactly. Fifteen DD1000 time-contrast rows retain boundary-of-parameter-space warnings, corresponding to two distinct fitted datasets; their fits converged with finite estimates, but the warnings remain visible. See [result audit](result_audit/AUDIT.md). The existing one-observation sensitivity checks weight time contrasts only, not robustness of the pooled associations.

Full artifacts: [paper-question rows with SEs, intervals and p-values](results/paper_question_comparison.csv), [all 140 comparisons](results/all_replays.csv), [execution summary](results/execution_summary.json), [protocol](PROTOCOL.md), [runner](replay.py).

## Direction for the next experiment

Retain complete population generation, but add evidence-guided completion as a separate use case. Existing real observations provide information that summary-only generation lacks. Agent contributions can be evidence retrieval/interpretation, matching population and measurement conditions, selecting a conditional model, representing unresolved assumptions, generating multiple completions, and auditing whether conclusions change. Merely forcing records to reproduce a supplied validation coefficient would be circular.

The next small experiment should mask originally observed values, give the Agent only remaining observations and permitted independent evidence, and compare the same downstream analysis before masking and after completion. The detailed [completion protocol](NEXT_IMPUTATION_PROTOCOL.md) keeps this distinct from inventing an unmeasured variable or filling an unreported paper statistic. No new imputation experiment has been run in this extension.

