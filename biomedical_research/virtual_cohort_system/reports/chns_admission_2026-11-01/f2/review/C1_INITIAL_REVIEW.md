# Independent C1 initial candidate review

1 November 2026. **Scientific/static review PASS for the proposed fixed scenario; final candidate-file approval is pending one author-owned wording clarification.** No generator or scientific table was executed or inspected. This review does not assess agreement with the hidden reference, identify a true joint model, or prescribe desired target parameters.

Reviewed scientific bytes:

- `generator.py`: `edcfd145960d4106589aa5deea4c374b78edd393c884c149d2ef928927ec45e3`.
- `model_spec.json`: `155210429431be8107a7b0e22f9bd82185df5270d7bde34e975bea4f34a523b3`.
- Active F2 release: `730a1cbab4e3dddaa33f3fa24d43ba1bc260ed57de8a8beb48075a37df02d8a9`.

## Scientific interpretation and implementation

The code implements the stated observational conditional-lognormal scenario: discrete-uniform age, independent Bernoulli female category and lognormal BMI, conditional lognormal glucose, then conditional lognormal HbA1c with explicit age/BMI/glucose terms and independent errors. The reference centering, draw order, exact row count/columns, units, RNG and zero sex-shift assumptions agree with the specification. The generator accepts `observed=None`, reads scientific settings from its supplied spec, uses the supplied seed, returns a DataFrame and has no file, network or target-data access code. It rejects nonfinite/nonpositive continuous output rather than clipping or silently changing the model.

Every scientific setting has provenance pointing to a source context, explicit assumption or task layout. The numerical age/BMI effects, dependence structure, distributions, residual scales, age/sex composition and no-mixture simplification are expressly assumed. Source medians and means are not claimed to be equivalent estimators; source correlations are not relabelled elasticities; Jansen's separate regressions are not concatenated as one fitted conditional equation; Pani's weighted coefficient is not installed as a matching unweighted target effect. The stated local derivatives of the model's log relation are algebraic explanations of its assumed parameters, not new source evidence.

This remains a strongly assumption-dependent scenario. Uniform target age, independent baseline predictors, zero sex effects, fixed lognormal tails and omission of treatment/disease mixtures may fail for important analyses. Fixed residual randomness represents row variation, not evidence/model/transport uncertainty. The candidate documents these limitations and does not claim a correct target distribution or source fit. Their presence is not an implementation error or reason to demand full joint-law identification before the authorized pilot.

The builder's metadata records report static contract validation, syntax/provenance checks and no biomedical execution. Those records and code were inspected; the reviewer did not rerun the builder's checks or any passed test suite. Actual generated output remains unvalidated until the controller uses the scheduled slots.

## Candidate-specific interpretation approval

The candidate requests both exact optional policy interpretations and declines neither. Its six required policy assumptions are preserved. The reviewer created model-bound `interpretation_approval.json`, dispositioning all 16 evidence items: the two named correlation items approved solely for the conditional target-proxy calculations, and the remaining 14 not approved for numerical feedback while retaining their admitted modelling-context role. No source weights, missingness or transport facts were upgraded.

The resulting `conditional_interpretations_v1.json` binds task, evidence, recipe, semantic sidecar, exact model and independent approval. Actual metadata-only preflight was performed for this new candidate:

- Strict v1: both checks `unavailable`, retaining unknown original weighting.
- Conditional v1: `approved_declarations` for both optional interpretations, with source reproduction explicitly not established.
- Approval SHA-256: `fb5ca2ff768677b472e6e71a8b1c8855e3c7f0ab053008b30ff21c35c99fd644`.
- Conditional-plan SHA-256: `69af12f7e1adb02d326d1ed1e73c81848e6151a18c691850ef9bf95f164fca4c`.

These checks read declarations only, without generating/reading rows, source-statistic arithmetic, target access, freezing or execution. They are not a repeat of a passed software suite and not evidence of scientific accuracy.

## Pending wording and final binding

The initial decision prose says that Pani overlaps with "excluded NHANES material." The intended meaning is omitted **Liu source material**, not a new global NHANES exclusion or a CHNS target overlap. The requested author-only clarification is: Pani shares NHANES survey years with Liu material omitted from this packet, which supplies no additional independent replication. No generator, model, parameter, source fact or test needs changing for this prose repair.

After the author makes that clarification, the reviewer must check the actual final decision bytes and issue `candidate_review.json` binding all final candidate files except that review and the future controller binding. Until then this note and the conditional approval do not substitute for the controller's required final candidate review or authorize execution. No frozen file or old receipt has been edited.

## Final resolution and candidate approval

The author has clarified that the omitted material is Liu's NHANES source material. Final `decision.md` SHA-256 is `f95399f103a1e015cc8c8de67cb490847705cd7eae0221691521e5dd8be1fcde`. The generator, model specification and conditional approval/plan hashes above are unchanged. This is a nonscientific prose amendment; the builder's historical metadata-check records retain their earlier decision-file hash and are not presented as a new check of these final prose bytes.

The reviewer checked the final clarification and issued `candidate_review.json`, binding the complete current candidate-file set and active F2 release. **Final candidate disposition: approved for the scheduled initial execution.** This is separate from scientific output validity, which remains unassessed. No preflight, passed test or generator was repeated for the wording change. The controller must still validate the complete approval and freeze the candidate before executing its allocated slots.
