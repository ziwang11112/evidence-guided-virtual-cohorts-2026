# Which Scientific Analyses Can Agent-Generated Biomedical Cohorts Support?

KDD Research working manuscript, v0.50, 22 November 2026. [Full paper](paper.pdf) · [Linked external review copy](external_review.pdf) · [Overleaf project](overleaf_v50.zip) · [Linked Overleaf project](overleaf_external_review_v50.zip) · [Contribution and reviewer questions](REVIEWER_QUESTIONS.md)

## The question

A biomedical study may report both cholesterol means and a mean ratio without reporting which individual's total and HDL values belong together. A researcher can recover mean non-HDL by subtraction. To estimate the proportion above a cutoff, the researcher needs a joint model. We ask whether an agent can construct a virtual cohort from an original study and exhibit another, equally compatible with the supplied checks, that gives a materially different answer for the intended analysis.

The full-authoring procedure gives the agent the task and article and allows it to choose the scientific law, parameters and executable sampler. The matched experiment fixes the single-variable grids and source checks to isolate how the agent assigns the two values to each person. Both follow-ups receive the same full article and initial submission. The ordinary follow-up asks for a second defensible model. The targeted version additionally seeks a consequential change in the specified analysis. An independent implementation checks the source quantities, programs' outputs and contrasts. Measured participants address a separate question about the accuracy of a chosen model in a particular population. [Original-paper model audit](../../work/original_paper_capability_2026-11-17/SOURCE_MODEL_AUDIT.md) · [Matched design and results](../../work/article_portfolio_2026-11-22/RESULTS.md)

| In the paper | What to look for |
|---|---|
| Figure 1 and Table 1 | What an agent selected in three full-model iron proposals, and what freedom the investigator allowed in controlled pairing |
| Figure 2 | Across three original articles, how often ordinary and targeted follow-ups achieved a material change. For iron, compare each program with the two attainable mathematical endpoints |
| Figure 3 | One adjusted lifestyle regression applied to generated and measured data. The BMI result transfers more closely than several cholesterol contrasts in the source population |
| Figure 4 | What changes when the same generated values are re-paired in the iron and lifestyle studies |
| Figure 5 | A prospective real-world test of within-person grip difference, including its dependence on endpoint and population |
| Appendix | Per-case protocol, classical numerical controls, measured-sample failures, and earlier prospective decisions |

The new matched comparison used 36 assigned blocks, 106 GPT calls and 315 scored tables across three source publications. The constituent results were 0/12 versus 11/12 for lipids, 6/12 versus 11/12 for lung function, and 12/12 versus 12/12 for iron status. This is an evaluation of the instruction's **ability to generate a counterexample**. External accuracy is evaluated by population and scientific use. The earlier prospective studies and the three matched experiments reuse publications and answer different questions. [All three articles and denominators](../../work/article_portfolio_2026-11-22/RESULTS.md) · [Grip transfer](../../work/bilateral_grip_transfer_2026-11-21/RESULTS.md) · [Prospective use rankings](../../work/prospective_lipid_use_2026-11-21/RESULTS.md)

The numerical controls distinguish the role of the agent in translating a paper and writing code from the attainable range after the constraints have been formalized. In the earlier lipid test, a conventional solver also found source-compatible screening fractions of 9.375% and 41.406%. In iron, the same four threshold counts and the frozen marginal grids permit both signs of continuous correlation. [Constructive lipid results](../../work/kdd_v40_pairing_review_2026-11-20/REVIEW.md) · [Finite-grid iron endpoints](../../work/article_portfolio_2026-11-22/iron/RANK_AUDIT.json) · [Manuscript build checks](BUILD_CHECK.json)

The new post-outcome lung control takes the extracted source constraints and exhibits 1.18% and 52.46% below 0.70 on the same grids. Both assignments preserve the original sex-specific regressions and physiology checks. This demonstrates that conventional numerical search also finds an alternative after evidence translation. [Numerical control and independent verification](../../work/lung_pairing_numerical_control_2026-11-22/RESULTS.md)
