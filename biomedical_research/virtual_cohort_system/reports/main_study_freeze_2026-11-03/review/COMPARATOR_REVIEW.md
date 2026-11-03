# Independent comparator implementation review

3 November 2026. **Ready for binding into the common pre-execution release.**
The originally blocking model-provenance interface defect was repaired. No
remaining blocking implementation or source-semantic mismatch was found in the
reviewed comparator. This is approval of this fixed implementation and its
declared scope, not a campaign release or a claim that an actual source fit,
clinical generator execution or target comparison has succeeded.

The reviewer `/root/existing_case_readiness` did not author the comparator;
its author is `/root/freeze_readiness_audit`. The reviewer authored the CHNS
case binding, so this report is not an independent admission review of that
case. Exact reviewed-file hashes are in `COMPARATOR_REVIEW.json`.

## Resolved blocking finding

The initial `build_spec` result used audit fields as `parameter_provenance`,
which could not satisfy the unchanged harness's per-parameter provenance ABI.
The author added `build_harness_spec(case_id, arm, packet_bytes, task_bytes,
compiled_evidence_bytes)`. It now returns a valid `model_spec`, a separate
`construction_trace` and its canonical hash, and invokes the actual harness
`validate_spec`. Every parameter has exactly the required evidence IDs,
assumption IDs and derivation fields. The model's components provenance binds
the trace hash. CHNS grouped-source IDs map to the existing compiled suffix
IDs; ENSANUT item IDs remain unchanged. The controller must retain and bind
both returned artifacts. The lower-level `build_spec` result is explicitly
documented as a recipe/diagnostic object and must not be submitted directly.

## Mathematical and information checks

- Separate Jansen BMI and glucose projections use their own covariance designs
  with age/sex adjustment and an intercept represented by centering. They are
  not inserted as two coefficients of one joint regression. IFCC-to-percent
  slope conversion uses only the multiplier; the shifted-lognormal response
  preserves the positive native IFCC scale. Glucose units and the corresponding
  7 mmol/L versus 126 mg/dL upper support agree with each case's source inputs.
- Lognormal/shifted-lognormal margins have finite first and second moments;
  declared age and glucose supports are bounded where required. Gaussian-copula
  dependence and finite donor mixtures preserve finite raw moments. Positive
  definiteness, fit residuals and quadrature agreement are checked. Source
  fitting is deterministic and bounded, with no alternate start or hidden
  fallback. A failed fit is a reported failed construction.
- The source covariance arithmetic and sampler transformations agree under
  the declared laws. Independent toy density integration verified truncated
  moments and truncated-normal covariance; fixed toy transform nodes matched
  the sampler transform and strict support. The documented inverse-CDF endpoint
  safeguard applies only to quadrature. The sampler fails on endpoints or
  invalid values instead of clipping, filtering or redrawing.
- CHNS applies the declared equal three-donor mixture, donor-specific sex
  fractions and target integer-age transformation. ENSANUT's eight loops each
  allocate 375 rows, preserve requested age/sex cells and use a conditional
  Gaussian law with target age-CDF positions. Target quotas never replace
  source demographics during source fitting. These are explicit transport
  assumptions; copied source laws do not establish target biological validity.
- E0 receives only its admitted marginal packet. Its within-component
  independence is the fixed unconstrained entropy choice, not an empirical
  assertion. E1 uses source relational records numerically in their separate
  source contexts. CHNS MIND rank use is the continuous Gaussian-copula identity,
  explicitly qualified for smoothing rather than reproduction of original
  imputation/ties. ENSANUT Pani records remain available but contextual/unfitted;
  no missing source SD, survey weight or target outcome is invented.
- No target data or target-effect input is accepted by the mathematical
  constructor. The sampler has no fitting, filesystem or retrieval calls.
  Exact approved packet/task/compiled-evidence identity and full raw-to-compiled
  correspondence remain controller/release responsibilities. The packaging
  wrapper's ID membership check alone does not certify evidence content.

## Verification and retained limits

The reviewer independently ran the final 13-test invented analytic suite: all
passed. Its complete-constructor fixture exercises the actual `validate_spec`
and sampler-parameter validation while random generation is patched to fail.
Four additional independent deterministic toy checks passed; their script and
result are retained as `check_comparator_arithmetic.py` and
`COMPARATOR_ARITHMETIC_CHECK.json`. No actual case fit, `generator.generate`
invocation, clinical table, raw record or target report was used in this review.

The local entropy optimization is not certified globally optimal. Source
selection is represented only to the explicitly declared extent, and source
weighting, assay transfer and unidentified dependence remain assumptions.
Pani numerical uptake is partial; source, structural and transport uncertainty
are not calibrated. One fixed statistical specification versus five Agent
constructions is an asymmetric descriptive comparison. These stated limits do
not block this finite benchmark and must remain beside its results.

The common campaign still must bind the reviewed modules, exact case inputs,
model/trace artifacts after construction, runtime, all attempt limits and the
common evaluation barrier. This review does not enable execution, resume old
budgets, or certify a favorable scientific outcome.
