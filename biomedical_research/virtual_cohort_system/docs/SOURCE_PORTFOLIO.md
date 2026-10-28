# Source diagnostics across fixed generator seeds

The analytical goal is reusable generated data that support defensible scientific analyses. Agreement with source means is one diagnostic; it does not establish preservation of unprovided target conclusions.

`cohort_harness.source_portfolio` adds a source-only review layer. It verifies execution-backed replays for every seed in an explicit ordered schedule, retains every diagnostic, and describes variation across generator seed draws. It does not choose biological coefficients, an objective function, a winner, or a scientific acceptance threshold.

```python
from cohort_harness.source_portfolio import summarize_source_portfolio, compare_source_portfolios

# Declare and retain these schedules before executing them. Each named replay
# must have completed through source_replay with its corresponding seed.
summary = summarize_source_portfolio(
    bundle, "candidates/initial", ["initial_101", "initial_102", "initial_103"], [101, 102, 103]
)
comparison = compare_source_portfolios(
    bundle, "candidates/initial", "candidates/final",
    ["initial_101", "initial_102", "initial_103"],
    ["final_101", "final_102", "final_103"], [101, 102, 103]
)
```

The comparison requires identical evidence bytes, source recipe bytes, and the descriptions of every source-context/check assumption. A study that changes evidence or source-population assumptions needs a separately declared comparison; it cannot silently label those differences generator improvements. Candidate models may differ. All paired changes remain visible in the original statistic's units; there is no summed score across correlations, means, proportions and slopes.

## What the numbers mean

- The range and sample SD describe **generator seed variation** with fixed source covariates and program/specification. Whether a seed varies residuals alone or also parameters depends on the generator and requires review. In the TG development pilot, the seed varies residuals only. They are not confidence intervals or uncertainty about the source study, model structure, population transfer or unmeasured variables.
- A discrepancy on the same side across three draws is a descriptive signal to investigate. Three draws do not establish statistical significance or exclude Monte Carlo noise.
- A failed scheduled execution stops summary generation. A numerically undefined statistic remains listed and receives no aggregate; it is not dropped to improve a score.
- Seeds can be paired across candidates to reduce simulation noise in a descriptive comparison. Shared seeds and shared source participants make diagnostics dependent, not independent confirmations.
- This API has no target outcome or target-evaluator argument. Verification still runs on a trusted host, and does not isolate the outer Agent's filesystem tools.

## Agent review protocol

1. Inspect all source diagnostics, including those that already fit adequately under the stated assumptions.
2. Separate extraction/estimator mismatch, residual simulation variation, approximate source covariates, and generator structure. In particular, a marginal rank correlation depends on the joint covariate distribution; it is not a conditional regression coefficient to copy into a generator.
3. Propose a retain/revise decision with the source evidence, intended changes and possible trade-offs. A change in dispersion can change a log-scale association even when arithmetic means stay fixed.
4. Freeze the next candidate with the actual feedback artifact and decision. Run the complete fixed schedule once; keep all changes and failures.
5. Evaluate target conclusions only through a separately frozen, unprovided analysis protocol. Better source fit alone does not promote the model to validated target use.

The API checks the supplied seed schedule against receipts. The timing of that declaration remains procedural; the controller should separately retain a protocol commitment before execution.
