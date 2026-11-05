# Independent numerical review

**Passed after one audit parser correction.** All 18 scheduled final slots were retained and all **513 declared outputs** were independently reconstructed: 279 HbA1c outputs and 234 lipid outputs. No generated outputs were missing. The closed batch contains 24 physical attempts and 18 distinct successful final tables.

The corrected audit found **zero arithmetic, closure/table-hash, reference-binding, mapping, direction, summary, or CSV discrepancies**. The largest absolute reconstruction difference was **5.3290705182007514e-14**, within the predeclared rule `abs(actual - expected) <= 1e-9 + 1e-10 * abs(expected)`.

All 324 available aggregate-reference comparisons matched. The remaining 189 lipid diagnostic references were correctly unavailable because the pinned aggregate does not contain matching estimators. All 18 author primary-endpoint summaries and all 513 rows of `ALL_ENDPOINTS.csv` were checked.

Reconstruction used a separate standard-library CSV parser and Householder QR regression. HbA1c used the exact eight-by-375 allocation, population SD, and the declared inverse-CDF quantile convention with accurately summed binary mass boundaries. Lipids used the 38.67 mmol/L-to-mg/dL factor, sample SD with `ddof=1`, manual linear quantiles, and independently residualized correlation. The audit imported no provider, generator, or evaluator, and read no reference participant records.

The first run is preserved in `numerical_audit_attempt_01`. Its audit parser incorrectly expected the HbA1c identifier `id`; the frozen task uses `row_id`. That rejected nine HbA1c tables before numeric reconstruction and produced 2,565 cascading problem entries. All 234 lipid outputs matched in that run. Only the HbA1c identifier/header/uniqueness check was corrected; formulas and tolerances did not change. The original preclosure script and `NUMERICAL_AUDIT_CORRECTION_01.json` preserve the change. `numerical_audit_attempt_02` contains the passing full reconstruction.

No frozen candidate, controller, or evaluation file was changed. This review verifies declared arithmetic and artifact bindings; it does not establish scientific validity, source transport, generalization, or fresh clinical validation.

Artifacts: `INDEPENDENT_NUMERICAL_REVIEW.json`, `NUMERICAL_AUDIT_PREDECLARATION.json`, and `numerical_audit_attempt_02/AUDIT_RESULT.json`; all reconstructed values are retained in the attempt-02 JSON and CSV endpoint files.
