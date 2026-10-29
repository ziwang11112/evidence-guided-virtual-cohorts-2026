# Review of the controller's proposed frozen gate

2026-10-29. This supersedes illustrative numerical gate examples in `DESIGN_REVIEW.md`; it does not certify candidate execution or source compatibility. The controller confirmed the rule below before new candidate execution.

The proposed gate is acceptable as a finite descriptive comparison. Use three candidates, zero/minus/plus. For every one of the 46 source checks, every scheduled source seed, and both perturbed candidates, require

`abs(T_alternative,seed - T_zero,seed) <= 3 * historical_s1_final_generator_seed_draw_sd`.

Freeze the complete numerical threshold table, its derivation, historical input hashes, check mapping, and code before the first new execution. A zero historical SD requires exact equality. No portfolio averaging, favorable seed selection, threshold enlargement, statistic dropping, or scientific retuning can rescue a failed check. Undefined required statistics and execution/integrity failures remain failures. The paired comparison uses all results from the fixed schedule.

Three times a sample SD from three historical generator draws is a descriptive scale, not a paired SE, clinical margin, confidence limit, or calibrated simultaneous acceptance region. Common random numbers may reduce paired simulation variation, but do not give this multiplier a coverage probability. Twelve covariate-only checks are implementation invariants and receive no biological-fit credit.

The zero candidate must retain the historical s1 scientific conditional law algebraically. Preserve every zero and alternative discrepancy from the published point summaries. Otherwise three similarly misspecified models could agree with each other without even retaining the stated anchor. Report the Oh adjusted BMI coefficient's location relative to its reported CI [5.853, 7.774] for every candidate/seed; label this interval-location diagnostic separately from the descriptive paired gate. Report all 40 Oh Table 2 arithmetic/geometric alternative interpretations and all unavailable adjusted/paired estimands without declaring source-wide compatibility.

The primary materiality rule is **the maximum absolute analytic plus-minus conditional-mean difference over the four fixed male cells (age,BMI)=(40,23),(40,27),(60,23),(60,27) is at least 5 mg/dL**. Report all four magnitudes and their individual >=5 indicators. The controller expressly chose MAX over the fixed set, not a requirement that every cell exceed 5. Already available design values, approximately 3.37, 4.82, 6.93, and 9.91 mg/dL, must be identified as pre-run algebraic expectations. They are not prospective empirical discoveries. Keep the amplitude and basis definitions fixed.

The safety factor 0.8 is algebraically valid if the code establishes `|hA*hB|<=1` and a certified reference-density lower bound m over every active covariate/TG rectangle. With 50 mg/dL bands, `delta=0.8*50*m` guarantees `0.2*f0 <= f_plus/minus <= 1.8*f0` on perturbation support, and equality to f0 outside it. A finite grid minimum alone is not a certificate. The constant-CV lognormal endpoint proof, including the softplus conditional-mean extrema, must match code and frozen parameters.

Primary invariance claims concern the declared product source population; the actual finite source table has approximately independent permutations. Quantify its departures and preserve all paired drift. Passing this gate means that this finite descriptive screen did not distinguish the pair. It does not mean the empirical clinical population has the assumed independence or that either law is statistically compatible with all source evidence.

No candidate was imported, generated, or executed during this gate review. Implementation review follows separately before controller execution.

Boundary disclosure added during continuation: a later general agent-readiness inventory automatically displayed unrelated historical target aggregate summaries. This gate review and the scalar design checks were completed before that exposure. No related files or patient rows were opened and no design choice was changed using those summaries. The controller was notified; later review is restricted to code and proof consistency.
