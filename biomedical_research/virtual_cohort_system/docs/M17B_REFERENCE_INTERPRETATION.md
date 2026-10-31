# Interpreting a measured reference without treating it as population truth

31 October 2026. Clarification prompted by the user's observation that the measured sample mean need not equal the true population mean. This changes interpretation and future design; it does not change the completed M17-B analysis, data, generator, protocol, audited numerical records or figure.

## What 29.1824 represents

The measured BMI mean 29.1824 kg/m2 is the arithmetic mean of the 320 selected reference records. It is an observed sample statistic, not a known population parameter. The observed arithmetic is fixed once those records are selected; its relationship to a broader target remains uncertain.

M17-B selected 40 people in each of eight age/sex cells. Its equal-weight sample mean describes that quota composition. It is not the survey-weighted national US mean or the unstandardized mean of all eligible NHANES participants. Even if the intended target is an equal-age/sex standardized population, its unknown mean is not made known by observing one finite sample.

Generated means of 27.1370–27.7796 are lower than this measured reference-sample mean. That is an observed discrepancy. It does not, by itself, establish the amount or direction of bias relative to the unknown population mean. Conversely, uncertainty in the reference does not establish that the generated means are closer to that unknown mean.

## Sources of uncertainty must stay distinct

| Quantity or process | Relevant uncertainty or limitation |
|---|---|
| Measured reference statistic | Finite sampling, the source survey design, quota selection, complete-case eligibility, measurement protocol and measurement error |
| Published aggregate evidence | Study sampling uncertainty, rounded reports, different eligibility/measurements, publication selection and study overlap |
| Generated statistic | Finite simulated draw, assumed joint structure, parameter uncertainty and transport to the intended population |

Adding generated rows reduces Monte Carlo variation conditional on a fixed generator. It does not supply additional measured evidence or resolve uncertainty about its model and transport assumptions. The three M17-B draws only illustrate conditional realization variation.

The existing HC3 intervals belong to the specified regression effects in the selected sample. **They are not uncertainty intervals for the BMI mean**, complex-survey population intervals, or calibrated intervals for evidence/model/transport uncertainty. M17-B did not run a mean-uncertainty analysis or establish equivalence margins. Do not retroactively describe its mean discrepancy as a statistically established population bias, or dismiss it as sampling noise without analysis.

## How to evaluate scientific usefulness going forward

1. Define the population and estimand first: a particular measured finite cohort, a standardized population, a survey population, or a specified prospective study. A claim about one must not silently become a claim about another.
2. Use measured datasets as empirical anchors with stated uncertainty. For an appropriate future protocol, quantify reference uncertainty using the design actually being analyzed, rather than applying an automatic independent-row bootstrap to a complex survey and calling it population inference.
3. Compare prespecified scientific quantities: associations, conditional effects, response shapes, subgroup contrasts and relevant distributional features. Evaluate both magnitude and direction in context; exact agreement with one sample statistic is not the goal.
4. State a scientifically meaningful tolerance or decision criterion prospectively when claiming practical equivalence or usefulness. An overlapping interval, a large p-value, or a shared sign alone does not establish equivalence.
5. Use multiple independently admitted references and source-consistency/sensitivity checks where feasible. Replication and complementary evidence can distinguish a sample-specific discrepancy from a recurring transport problem. Cross-population differences remain part of that assessment.

These are future-design requirements, not additional analyses completed in M17-B. The revealed reference remains closed to generator tuning. Existing discrepancies and successful relationship transfers are retained. The precise conclusion is selected relationship agreement with this measured reference under the declared design, with broader population fidelity unresolved.

## Wording correction

Prefer **measured reference-sample mean**, **reference effect estimate**, and **generated-minus-reference discrepancy**. Use **population bias**, **ground truth**, **equivalence**, or **recovery of a true effect** only when the study design supports those stronger meanings.

Earlier frozen reports and the figure retain their original bytes and terminology. Read statements such as “understates BMI” in those historical summaries as lower than the specified measured reference, not as established underestimation of an unknown population mean. Mutable project overviews now make this distinction explicit.
