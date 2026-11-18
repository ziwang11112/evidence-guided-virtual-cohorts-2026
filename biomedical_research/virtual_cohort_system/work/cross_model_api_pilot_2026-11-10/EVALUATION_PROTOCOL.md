# Cross-model API construction pilot: frozen evaluation protocol

This developmental pilot schedules twenty independent API constructions: two cases (PNS blood pressure and lipids), five model configurations, and two fresh context replicates using the same case prompt. The same returned law supplies three equal-weight tables of 3,000 rows using seeds 31001, 31003, and 31007. These sixty scheduled slots are the maximum; there are no replacement seeds or runtime repairs. At most one mechanical API repair is permitted before construction closure, using syntax/schema findings only. Scientific source checks and target-quality feedback are not provided during construction.

All initial and final API artifacts are sealed before any scientific generator execution. The root reviewer records freeze approval against the full construction seal and implementation hashes. Generator execution reuses the unchanged `cohort_harness.execution` WSL/bubblewrap command and unchanged `_worker.py`, with the approved Ubuntu-24.04 runtime. Only task, model wrapper, generator, request, and worker are staged. The model wrapper is exactly `{"task": task_json, "model": returned_model_spec}`; `generate(observed, spec, seed)` receives `observed=None`. No source/reference artifacts, credentials, home directory, host drive, or network are exposed to the generator. Backend failure stops execution; no unrestricted fallback exists.

All sixty scheduled slots receive accounting, including three unavailable slots for a construction that could not be sealed. Generator/runtime/output failures are retained. A failure never resets the seed or table budget. Aggregate evaluation begins only after all construction artifacts and all execution outcomes are sealed. Construction and execution integrity failures halt the batch for audit.

## Primary estimands

PNS uses the existing generated-only blood-pressure estimator, with equal-weight generated rows representing the declared `peso_lab`-weighted finite complete-case analytical distribution. Both regressions have design `[1,(age-50)/10,female,(bmi-25)/5]`. The three primary estimands are the SBP BMI coefficient, DBP BMI coefficient (both mmHg per 5 kg/m²), and Pearson correlation of centered paired regression residuals.

Lipids uses the unchanged existing K02 / lipid Q5 estimator. Delivered TC and HDL values are in mmol/L and are multiplied by 38.67 for mg/dL analysis; this is numerical unit conversion only. The design is `[1,(age-50)/10,I(sex=='F'),(bmi-25)/5]`. The three primary estimands are the adjusted HDL and TC BMI coefficients (mg/dL per 5 kg/m²) and residual Pearson correlation. Every delivered row must satisfy the supplied fixed complete-row eligibility: age at least 18, sex exactly F or M, and strictly positive BMI, TC and HDL. Invalid rows make analysis unavailable; they are never silently removed.

## Secondary diagnostics and comparison

The outcome marginal SDs retain their existing conventions: PNS uses population variance under normalized weights (generated equal weights, ddof=0); lipids uses sample SD (ddof=1). Component violations are SBP below DBP and HDL above total cholesterol, reported as fractions and counts. Violations remain in the data and are not silently repaired, clipped, swapped, filtered, or imputed. The fixed lipid eligibility does not exclude HDL above TC. Mixed numeric/text, nonfinite values, missing values, unexpected categories, incorrect counts, and duplicate identifiers are not coerced into acceptable observations.

Each primary/secondary endpoint retains its original units. Report generated values by seed, reference value where available, generated-minus-reference signed difference, absolute difference, and within-construction available-seed mean/range and availability denominator. Descriptive sign agreement is not a pass criterion. No pooled cross-unit score, new acceptance cutoff, hypothesis test, superiority/equivalence decision, or confidence interval from the three seeds is introduced. Singular designs and degenerate residual correlations remain explicitly unavailable.

## Reused reference boundary

The host-only aggregate snapshot is prepared from exactly two already released aggregate files: `work/next_case_validation_2026-11-09/RESULTS.json` selecting `reference_weighted` plus its supplied row-resampling stability metadata, and `work/scaleup_2026-11-01/production_release/evaluation/PUBLISHABLE_AGGREGATES.json` selecting `references.K02`. It is hash-bound before execution, never included in author packets, and never mounted into the generator. No custodian loader or patient source is called; no reference fit or recalibration is performed.

PNS supplied intervals describe conditional IID row-resampling stability, not survey-design or national-population confidence. Existing lipid HC3 slope sensitivity intervals retain their original interpretation. The lipid component-violation reference is unavailable in the existing aggregate and remains unavailable. No interval is invented, borrowed from another endpoint, or treated as an equivalence margin.

## Interpretation and verification

Previously exposed reference families make this a developmental construction comparison, not a fresh clinical confirmation. One construction per case/configuration/context does not isolate model quality from construction variation. Three seeds are draws from one law, not independent constructions or clinical studies. Agreement on selected estimands does not establish causal validity, individual-row recovery, unique joint-distribution recovery, population transport, or assay equivalence.

Before root freeze approval, new adapters are checked with synthetic factorial fixtures with known adjusted slopes/residual correlation; rank deficiency, strict numeric typing, nonfinite data, component preservation, unit conversion, closure mutation, and preapproval refusal are checked. Runtime availability is inspected with trusted Python only. No scientific generator execution is permitted during preparation.
