# Fixed author-packet assembly

10 November 2026. **Staged for independent leakage/contract audit; not frozen or dispatched.** This file and `packets/ASSEMBLY_MANIFEST.json` are controller records and must never be appended to an author prompt.

The two source-only payloads support the authorized 20-construction design: two cases × five configurations × two fresh contexts. Every construction of a case must receive the same `packets/<case>/prompt.txt` bytes. Provider configuration, budgets, slot order, seeds, execution protocol, results and references are outside the author payload. The author-visible analyses remain scientific analyses, not a schema-only request. No target outcome, expected effect, old generator, common scientific parameter or exemplar joint law was added.

## Files and interface

- `prepare_packets.py` deterministically reads only eight explicitly listed admitted anchors and verifies each original SHA256 before constructing any payload. A changed anchor aborts assembly. It neither invokes an API nor executes model-generated code, and it reads no credentials or `.env` file.
- `packets/common_prompt.txt` supplies the identical scientific and response instructions used for both cases.
- `packets/PNS/` and `packets/LIPID/` each contain `task.json`, `requested_analyses.json`, `evidence.json` and the complete `prompt.txt`. Only `prompt.txt` is the author message; its other three files are reviewable component artifacts, not extra messages.
- `packets/ASSEMBLY_MANIFEST.json` retains exact original anchor paths/hashes, assembled artifact hashes/sizes and the assembly-script hash. Source provenance inside the payload uses artifact names/hashes without local filesystem paths. These are hashes of supplied source extractions, not claims that original articles were authenticated again.

The response is one JSON object with exactly `model_spec` (object), `generator_py` (string) and `decision_record` (object). The agreed execution ABI is `generate(None, {"task": task_json, "model": model_spec}, seed) -> pandas.DataFrame`. The generator reads its scientific settings from `spec["model"]`, and row count/schema from `spec["task"]`. The internal scientific specification remains the author’s choice. The complete object returned as `model_spec` is the value of `spec["model"]`; no extra wrapper or harness-specific scientific specification is implied.

`task.json` uses the existing strict harness task schema. Both tasks have 3,000 rows, no observed individual inputs, no retrieval actions and zero scientific revisions. This does not define the controller’s separately logged mechanical repair allowance. Lipid strict positivity is retained in `requested_analyses.json` eligibility and population metadata; the existing harness schema can express only the inclusive minimum zero. The executor must additionally reject nonpositive BMI/TC/HDL, without silently discarding rows.

## Admitted scientific content

PNS uses the existing author-safe evidence packet and reported-moment algebra. All three source entries remain: INTERSALT and Beijing supply quantitative anchors; INTERMAP supplies methods-only context with its absence of admitted numerical BMI/BP evidence stated. All published values, adjustments, source populations, measurements, source uncertainty and source-moment derivations are retained. The existing study configuration is a staging input only: the assembly selects task population/schema, purpose and three analysis identifiers, replaces historical tool/budget settings, and excludes all remaining configuration fields. The purpose’s obsolete request for unspecified diagnostics is removed; the three scientific analyses are supplied explicitly.

The PNS output is ordered `row_id, age, female, bmi, sbp, dbp`, with integer unique identifiers, ages 20–79 and `female` coded 0/1. The two equal-weight OLS models use `[1, (age−50)/10, female, (bmi−25)/5]`, yielding SBP/DBP BMI slopes in mmHg per 5 kg/m². The third analysis is Pearson correlation of paired centered residuals after the same full design.

Lipids uses all three existing curator extractions: Agongo 2018, Greiner 2021 and Obirikorang 2015, plus only admitted population/methods metadata and the existing analysis request. All 48 Greiner reported-statistic records and all 12 regression records are retained. Homogeneous record lists are encoded losslessly as column names plus row values; heterogeneous lists retain their original record structure. The exact original artifact hash is recorded before any transformation. Reported values, source locators, selection, measurements, adjustment sets, uncertainties, ambiguous regression scales, overlapping-cohort limitations and the anomalous printed HDL interval remain visible.

The lipid output is ordered `id, age, sex, bmi, total_cholesterol, hdl_cholesterol`, with unique nonmissing string IDs, age ≥18, literal F/M sex and positive BMI/TC/HDL. Delivered lipid units are mmol/L. The two OLS slopes use the equivalent full design `[1, (age−50)/10, I(sex=='F'), (bmi−25)/5]`, converting lipids by 38.67 to report mg/dL per 5 kg/m². The third analysis is residual Pearson correlation after the same full design and rows. No unrequested target exclusions are inferred.

## Explicit content transformations

No new numerical scientific values were calculated. Existing PNS source-moment arithmetic is carried through with its rounded-SD envelope explicitly distinguished from sampling uncertainty.

Unavailable local-source paths and the historical derivation-script path are omitted from PNS source entries; citations and evidence remain. From Greiner, the assembly omits historical reused-harness IDs, the local origin path and implementation-specific source-check directions. It retains the upstream extraction hash and its original-source-reading limitation. The historical `numerical_calibration_allowed` flag is removed from regression rows; response/predictor-scale ambiguity is still stated in each row. Two historical policy-worded issue resolutions are restated as factual scale/quantile uncertainty requiring explicit assumptions. This avoids imposing an earlier implementation’s scientific veto while preserving the unresolved source issue. No scientific model, parameter, recommended direction or distribution is substituted. The other source-extraction cautions and uncertainty descriptions remain.

The lipid metadata uses an explicit whitelist: context, country, named population, geographic metadata, eligibility, measurement, unknown composition, inference scope and unit mapping. Historical draft status, controller provenance directions, reference-boundary text and prospective row-count placeholders are omitted. The old request’s diagnostics and execution directions are not forwarded. Its three requested analyses and units remain.

## Checks actually performed

- All eight original admitted anchor hashes matched before assembly.
- Both assembled task objects passed the existing `cohort_harness.contracts.validate_task` validator.
- Greiner compact table construction reconstructs its input records exactly by assertion; retained counts are 48 descriptive/statistic rows and 12 regression rows.
- A payload string scan found none of the protocol filenames, model/provider labels, USD/cost-ceiling text, old schema-only wording, controller execution seed or absolute local paths tested.
- No API call, model-generated code execution, source replay, target-reference lookup or clinical comparison was performed by the assembler.

These are assembly checks, not an independent leakage audit, clinical validation or source reauthentication. Root review must inspect the actual payloads and approve their hashes before freeze. Assembly refuses to overwrite a packet directory containing `packets/FREEZE.json`; later scientific or prompt changes require a separately versioned assembly.
