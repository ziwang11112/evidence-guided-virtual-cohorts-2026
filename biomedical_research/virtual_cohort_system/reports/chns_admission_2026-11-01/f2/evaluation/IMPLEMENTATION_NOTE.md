# Fixed F2 evaluator: implementation and future release gate

1 November 2026. Implemented [evaluator](chns_f2_evaluation.py), pending independent review before any reference access. **No evaluation release exists or was created. No participant file was opened, hashed, decoded or imported by this work. No biomedical generator or old test suite ran.** The four exact key/wave/field definitions and file hashes in the analysis plan were checked against the existing metadata-only `SCHEMA_AND_KEY_AUDIT.json`; all matched. No prior key-count audit was repeated.

## Scientific computation

`prepare_reference_frames(frames, plan)` takes four caller-supplied DataFrames keyed by the source filenames. It validates numeric, finite, integral linkage keys with magnitude below 2^53 and all-wave uniqueness before selecting 2009. Biomarker/examination/survey joins are one-to-one on ID/wave; master gender is many-to-one on ID. It returns the five analytical columns and `survey_commid`, **without participant IDs**, plus aggregate preparation counts.

The helper implements the fixed age 35–74 and gender 1/2 mapping, native missingness, exact flag-9 height/weight masking, released cm/kg BMI calculation with finite positive inputs/result, and the common complete-case denominator. Other cleaning flags and positive values are retained without empirical cutoffs, repeated unit corrections or invented sentinel masks. Community missingness is not part of the complete-case filter. Linkage/eligibility counts, original-column native missingness, exact flag-9 counts and linked/analysis flag distributions remain distinct. Reference glucose/HbA1c availability requires finite released values, as specified by the fixed plan. The separate `nonfinite_glycemia` counts report observed ±Inf values (excluding native missingness) in the linked 2009 frame before age/gender eligibility. Finite zero/negative glycemia remains in the analytical frame for the interpretation gate. Generated frames do not pass through this reference eligibility filter.

`analyze(frame, plan, reference=..., quality=...)` checks the analytical frame **before scientific computation**. Any finite nonpositive glucose/HbA1c value withholds all primary estimates and marginal/joint diagnostics for that table; no row is deleted. Other invalid/nonfinite analytical values likewise withhold rather than alter the denominator. This applies to reference and generated frames. Ordinary prespecified exclusions already applied during reference preparation are not changed.

The three fixed raw, unweighted, intercept-including OLS projections are E1 BMI in H~age+female+BMI; E2 glucose in H~age+female+glucose; E3 age in H~female+BMI+glucose+age. Each requires n≥100, full design rank and residual degrees of freedom. Rank and condition number accompany each estimate. Insufficient n/rank makes the affected primary estimate unavailable without changing the population.

Reference inference uses cluster score sums and CR1 covariance correction `G/(G−1) × (n−1)/(n−k)`, with k including the intercept and t critical value with G−1 degrees of freedom. Every community ID must be numeric, finite, positive and integral; G must be at least 20. Invalid groups disable only the interval: the unchanged full-sample OLS point remains, with no row deletion or IID fallback. Generated tables receive no confidence interval from their artificial row count. These are selected-sample, assumption-dependent intervals, not national survey-design inference.

Diagnostics use all five marginal means/sample SDs and linear q10/q50/q90, plus Pearson and average-tie Spearman glucose–HbA1c. `compare_estimates` always retains available signed point differences; ratios are available only when the reference interval excludes zero. Interval membership is descriptive. `summarize_slots` requires all twelve planned slots, including failed/not-run entries. All three valid program-seed coefficients are needed for a stable nonzero-sign classification; incomplete/mixed/zero cases are not successes. Repeated direct-row outputs explicitly receive no Monte Carlo credit. Seed ranges are conditional output descriptions, not calibrated evidence/transport uncertainty. No ranking or global score is computed.

## The only reference-file entrypoint

The pure frame helpers perform no file reads. The future `evaluate_released(bundle, reference_dir, release="EVALUATION_RELEASE.json")` orchestrator first verifies the study release, independently reviewed final inventory, all fixed hashes and runtime versions. It then reserves `evaluation_results/` exclusively **before** hashing or decoding any source file. No automatic second run or retry is allowed. Existing lifecycle/execution verification binds each accepted generated output; no generator is invoked.

Only after that gate does `_read_reference_files` verify all four approved SAS hashes, import the reader and decode the specifically requested columns. Reader-recognized missing values remain NaN (`user_missing=False`); distinctions among tagged native missing reasons may be collapsed and are not claimed recovered. No source or analytical rows are written. `REPORT.json` contains aggregates, all twelve slot outcomes and interpretation limitations; errors retain a `FAILURE.json` under the consumed reservation. Independent numerical recomputation remains explicitly pending.

The evaluation release has exactly:

```text
schema_version: 1; status: "released"
f2_release_sha256; protocol_sha256; analysis_plan_sha256
evaluator_sha256
runtime_versions: {python, numpy, pandas, scipy, pyreadstat}
final_inventory: {path, sha256}
independent_review: {path, sha256}
```

Paths are bundle-relative. The independent review has `schema_version:1`, `decision:"approved"`, distinct `reviewer_id`/`coordinator_id`, `independent:true`, `reviewed_utc`, `reason`, and `approved_release` equal to the release payload excluding its review reference. Approval is procedural; hashes do not authenticate identities or protect against coherent host rewriting.

The SAS decoder version is obtained through `importlib.metadata.version("pyreadstat")` without importing the decoder or accessing participant files. Installed package metadata reports 1.3.7. The future release must bind this value along with the other runtime versions.

The final inventory has `schema_version:1`, `status:"final"`, the F2-release hash, `controller_state_sha256` (the evaluator's canonical file-tree digest), both constructions' final decisions (`retain_initial`, `revised` or `stopped`, each with a reason), and **all twelve** unique construction/stage/seed slots. Each slot includes status (`success`, `failed`, `not_run`), reason, route, candidate-freeze hash, execution-receipt hash, generated-output hash and execution-tree digest. Not-run entries require an absent execution and null route/hashes; failed entries cannot nominate a scientific table. Existing successful outputs cannot be hidden as failed/not-run. At least one successful output is required before revealing the reference.

**Unused-budget closure is mandatory:** all four canonical stages must already have coherent `run_request.json` reservations for their three fixed seeds and matching F2/candidate-freeze hashes. An unreserved/early-stopped stage blocks reference access even if the inventory calls it not-run. The existing frozen controller is unchanged; this gate relies on its refusal to rerun a reserved stage. A case with an unused runnable stage needs a separately reviewed closure decision/implementation before clinical access. This evaluator never writes fake reservations or receipts.

## Verification and stable hashes

Only the new `tests/test_chns_f2_evaluation.py` suite ran. **77 cases passed in 2.12 seconds**, using fabricated in-memory rows and temporary invented metadata. Independent centered/closed-form calculations and installed statsmodels 0.15.0 agreed with OLS and CR1/t results. Tests cover actual column/key spelling, linkage and measurement policies, pre-statistics withholding, inference failure without row deletion, n/rank thresholds, diagnostics, comparisons, twelve-slot preservation, missing-release rejection before file-content access and rejection when any stage remains unreserved. An initial fixture-setup path error was corrected to use a fresh workspace-owned temporary base; it was not a scientific failure.

Independent pre-evaluation review then identified two corrections: reference ±Inf eligibility did not match the fixed finite-value plan, and decoder version was absent from runtime binding. Both are corrected above without changing the frozen protocol or controller. Only the affected tests ran after these edits: `-k "reference_preparation or invalid_analysis_values or runtime_versions"` yielded **17 passed, 70 deselected in 1.80 seconds**. These checks cover ±Inf in each reference glycemia field, separate native-missing/nonfinite counts, retained finite zero/negative interpretation gates, unchanged generated-value withholding without row deletion, and decoder metadata binding. The complete expanded 87-case suite was not rerun; the earlier 77-pass result is historical evidence for the previous implementation, not a claim that all current cases ran. No actual source file or generator was accessed.

| Artifact | SHA256 |
|---|---|
| Evaluator | `e40f403b13125f5b41f620126a807122bb99796558adda576518fcf50796365a` |
| New tests | `e6d779a6ab5a997caa17f329181f42b563a46c7d4f694e596e4775af3150872d` |
| Analysis-plan input | `a2c5f43969c700474a9466416be8503dc0c92b1c78b12a07a6edc6bc88f247b7` |
| Existing schema/key metadata | `3cb8a6236d3c33f49b54b8b2279331228162ea76d6b96e45c6a079a21dd4d4b9` |

These checks establish only the tested implementation behavior. They do not establish clinical release quality, cluster exchangeability, measurement equivalence, target utility or an executed real-data analysis. The final evaluation release, real candidate inventory and independent recomputation remain future gates.
