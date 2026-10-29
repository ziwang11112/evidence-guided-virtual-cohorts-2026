# Committed controller and custodian methods review

Reviewed 2026-10-28 local date, after the experiment protocol commitment and before candidate execution. Inspected only current protocol, code, lock/manifest metadata, and task schema. No hidden participant table, raw data, generated target table, prior target-result contents, or fitted target result was inspected. Committed files were not modified.

## Assessment

The controller contains scheduling, verification, and artifact-handling logic, with no biological coefficients or model-form choices. It validates all candidate freezes before each stage, retains all scheduled source diagnostics, generates every final structure/seed output, and prepares the complete release manifest. The release guard additionally enforces the cross-structure chronological ordering and fixed experiment grid. The three mathematical constructions described by the builder are not selected or parameterized in controller code.

The custodian analysis implements the prespecified endpoints correctly:

- Adjusted age is the A coefficient from the **linear-BMI** log-TG model, with A=(age-50)/10 and sex adjustment.
- Primary curvature is 2 times the B-squared coefficient from the **full eligible-domain** log-TG model, with B=(BMI-25)/5 and age/sex adjustment. It equals the modeled contrast at BMI 25, 30, and 35; it is a quadratic projection, not a local spline conclusion.
- Secondary raw-TG curvature uses exactly the same domain and basis, stays in mg/dL, and is not exponentiated.
- Generated outputs are reported with point estimates only. Reference intervals use the explicitly documented occupied-domain PSU-minus-stratum t degrees of freedom and full positive-weight design covariance, including zero-score excluded-domain PSUs.
- The assay context is a typed task input. The controller does not apply assay calibration to generated rows. The evaluator verifies base covariate preservation and that the added target metadata is `unblanked_2021_2023`.

The custodian evaluator verifies custody anchors and the controller guard before parsing the hidden table, validates every generated table, and retains non-estimable auxiliary sensitivities. It uses the fixed native assay as primary. The backward calibration is auxiliary and applies the same fixed mapping to reference and generated outcomes without clipping or selective record removal.

No primary-endpoint mathematics or schedule inconsistency was found that requires changing the committed methods before execution.

## Important interpretation and audit limits

1. `structure_plan_commitment.json` is written before the initial source runs and its hash is included in the release manifest. The current guard does not inspect that optional manifest field or recheck the plan bytes against it. Preserve and independently audit this additional pre-execution commitment; the six candidate science artifacts remain fully bound by their freeze trees.
2. The custodian loads the guard path/hash supplied by the trusted root release manifest. Its digest check prevents a changed guard relative to that manifest; it is not independent authentication of an arbitrary replacement manifest plus guard. The real guard verifies its own code against the separately retained protocol commitment. The threat model remains trusted root/custodian with procedural Agent blindness, not an adversarial host.
3. Controller-created manifest paths are absolute. Guard and controller source code derive their roots dynamically, but moving the entire retained record requires path-aware replay or an explicit relocation mapping; do not claim that every exported absolute-path manifest is immediately relocatable unchanged.
4. Under the unchanged domain and intercept-containing basis, the backward affine mapping multiplies raw-TG curvature by 0.9785. That auxiliary raw result is algebraically linked to native raw curvature and is not an independent replication. Log-TG endpoints can change under the additive offset.
5. If the calibrated reference has a nonpositive value, the evaluator records reference sensitivity non-estimability and skips that scale's comparisons. Report this as an unavailable auxiliary comparison, not as a favorable structure omission. Native primary analyses are unaffected.
6. Generated point-direction agreement is descriptive. Exact zero is the frozen sign rule, so magnitudes must accompany signs, especially near zero. Neither agreement nor reference nonsignificance supplies equivalence, causal validity, or calibrated model uncertainty.
7. Nested Windows source-replay paths can exceed system path limits; the invented guard fixtures initially encountered this. Execution failures must remain visible and must not trigger local generator execution or selective schedule changes.

## Checks actually performed

Ran the new `survey_analysis.py` self-check using only its invented fixtures: passed analytic variance with an empty domain PSU, occupied-domain df assertion, global weight scaling, WLS coefficient agreement, covariance positive semidefiniteness, row permutation, and absence of raw-scale exponentiation.

Also imported that module and evaluated a fully invented balanced BMI-by-age-by-sex factorial design. Checks passed for recovery of a planted adjusted age effect and planted quadratic log-TG second difference; agreement of raw curvature with direct NumPy least squares; absence of generated SE/CI fields; and a deterministic linear log-TG example having zero log-scale curvature but positive raw-scale curvature. This tests the transformation diagnostic without using any biomedical participant data.

No R survey-package cross-validation, target fit, generator execution, or source-population assumption validation was performed by this review.
