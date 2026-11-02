# Designated Wave A evaluator

`evaluate_campaign.py` implements the fixed K01 and K02 analyses after both cases' construction inventories close. Importing the module, preparing its manifest, or asking for CLI help never opens participant records. The actual evaluator has not been invoked during implementation. `EVALUATION_MANIFEST.json` was prepared from existing schema-audit and reviewed code/specification metadata only; it copies the already recorded target paths, byte counts and hashes without reopening either target file.

## Fixed input and release bindings

The manifest fixes local output directory `D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcA/evaluation_results`. Preparing the manifest does not create that directory. The eventual global release must designate this exact evaluator Python path/hash and include the manifest and every entry in its `dependencies` list among the release artifacts. Raw target files are identified inside the reviewed manifest; they are not release artifacts for the controller to read during construction.

The two recorded reference identities are:

| Case | Local release file | SHA256 |
|---|---|---|
| K01 | `admission_next/private_data/HAALSI_baseline_dataverse_14Apr2017.dta` | `27c968d5c9e53948bc8ee21e0a5bdc2262ed3c17f1dbafb5bb303050b6715b9f` |
| K02 | `private_data/22Jul20_for_Dryad_noIDs.txt` | `7508097bd6578307a55aef793c15b4c26d2346e2d8e60e55ba8bf9d5254037f9` |

The evaluator uses the original, unchanged `case_k01/analysis/k01_analysis.py` and `analysis/k02_analysis.py`. Their historical `prospective_not_released` and `file_access_performed:false` fields remain unchanged: those pure functions perform no file access. The actual release/reveal and file-loader provenance are recorded by the outer evaluation intent, not by rewriting the frozen pure analyses.

## API and order of operations

```python
manifest = prepare_evaluation_manifest(output_directory)  # metadata only
completion = evaluate_revealed_campaign(
    ledger_path, manifest_path, reveal_receipt_sha256
)
```

The executable command is:

```text
python evaluate_campaign.py evaluate <released-ledger-directory> <pinned-evaluation-manifest> <single-reveal-event-SHA256>
```

The coordinator must first obtain the controller's designated-evaluator authorization after all twelve constructors across K01/K02 have closed. This function does not authorize construction or reveal for itself. It requires:

1. The release-bound ledger and current released artifact bytes, the exact designated evaluator path/hash, and this exact evaluation manifest/dependency inventory.
2. One matching target-reveal event, the same release hash and both-case closed inventory hash, and all twelve closed constructors.
3. Re-verification of every bound initial/final candidate's frozen parent/plan. Every usable output must still match the saved actual bridge and case-guard report and the same ledger stage authorization. Retained final inventory must equal the controller's exact alias reconstruction.
4. An exclusively created result directory and retained `EVALUATION_INTENT.json` before any measured-reference byte read.

Only then are reference bytes read, checked against their exact pinned size/hash, parsed, and passed to the fixed analyses. Generated target artifacts are independently verified, read under the actual target task, checked by the whole-frame case guard, and analyzed. They are never constructor feedback. Existing result directories refuse another invocation before another reference read. A failure after the intent produces a generic `EVALUATION_FAILURE.json` with no raw values and no automatic retry. Metadata or closed-artifact integrity failure stops before reference loading.

This is a trusted-coordinator procedural gate, not a hostile-host sandbox or an authentication signature. The evaluator does not import or rerun submitted generator programs. It invokes the existing readonly execution/guard verifiers. Run it in a fresh trusted Python process using the reviewed dependencies.

## Exact preparation rules

K01 reads only `prim_key`, `rage`, `rsex`, `c_bs_bmi`, and `c_bs_glucose` from the hash-verified Stata bytes. It verifies the reviewed variable labels, sex value-label definition, file dimensions, and ID integrity. Native and tagged Stata missing become canonical missing, with separate missing-kind counts retained. Sex code 1 maps to M and 2 to F. Numeric strings, booleans or unknown nonmissing codes fail preparation. The frozen finite numerical sentinel list is empty; numbers such as 88 or 99 are not automatically reclassified. There is no fasting, treatment, flag, range or outlier filter. The original analysis alone applies its fixed age≥40/positive cleaned-value/common-row rule and descriptive HC3 sensitivity.

K02 reads the hash-verified UTF-8-sig tab-delimited file with the exact reviewed header, retaining only ID, Age, Sex, BMI, Total cholesterol and HDL cholesterol for analysis. Only stripped empty strings and uppercase `NA` are missing. Nonmissing sex tokens are stripped F/M as in the admitted audit; no biological meaning for the F/M legend is newly asserted. Other missing-like tokens, malformed numbers, duplicate/missing IDs or nonfinite parsed numeric tokens fail whole preparation. There is no generic sentinel recoding, lifestyle/fasting filter, TC≥HDL rule or inferred outlier policy. The frozen analysis applies its age≥18/common-positive-finite-row eligibility.

Measured K02 lipids already use mg/dL and are never converted again. Generated K02 lipids use the reviewed same-analyte mmol/L-to-mg/dL adapter and approved manifest, multiplying TC and HDL by 38.67. ID, age, sex and BMI remain identical. The evaluator checks the adapter's ordered input column kinds/roles/units and row ID against the actual child target task; the receipt binds input/output frames, approved map, execution/output hashes, target task and analysis specification. Unit conversion does not establish specimen, assay, fasting or population equivalence. Generated rows are never filtered or repaired; an exclusion attempted by the legacy K02 pure analysis fails the generated invocation.

## Complete reporting and pre-reveal failure clarification

There are 72 fixed target report entries: two cases × six constructors × two stages × three seeds. Thirty-six are final entries; retained finals reuse exactly the initial analysis/output identity and receive zero paired change when defined. Failures, unrun outputs, unavailable estimands and undefined denominators remain visible. A changed final failure never falls back to initial. The evaluator reports every fixed entry; it selects no best model, seed, endpoint or resolution.

Before any target disclosure, the coordinator confirmed this failure-accounting clarification: **available target diagnostics are retained, but construction-pass credit requires the entire same stage to have verified success**. A source execution or source guard failure therefore prevents constructor-pass credit at every resolution even when its target projections can be computed. This is the same whole-stage integrity condition already required for retention. The output distinguishes numerical endpoint comparisons from stage eligibility for bundle credit.

K01 uses absolute generated-minus-reference effect discrepancy divided by the same eligible reference glucose sample SD (ddof=1). K02 normalizes each BMI contrast by its respective reference outcome sample SD; residual correlation uses absolute correlation discrepancy. All raw point discrepancies and directions remain available when points exist, even if normalization is unavailable. The working boundary is ≤0.10 with the complete fixed 0.05/0.10/0.20/0.30 grid. All three estimands on all three seeds and whole-stage success are required for constructor pass; at least four of all five Agent constructors are required for case reliability. S01 is reported separately under the same rule.

All three zero-association anchors are reported. K01 must both pass final reliability and be discriminating to satisfy the positive Wave A scientific gate. K02 alone cannot do so. An unavailable anchor cannot establish discrimination. This report does not automatically authorize Wave B execution. Synthetic rows and seeds are not independent cohorts, and the working resolution is not clinical equivalence or percentage error. Reference HC3 intervals are descriptive working sensitivities, not survey/cluster/causal/transport uncertainty coverage; generated tables receive no inferential intervals.

Successful execution writes:

- `EVALUATION_INTENT.json`: release, reveal, manifest, evaluator and inventory bindings.
- `FULL_EVALUATION.json`: local candidate/output verification identities, reference preparation provenance, both reference analyses, all 72 target analyses/comparisons, unit receipts, full grid, bundle accounting, zero anchors and paired initial/final changes.
- `PUBLISHABLE_AGGREGATES.json`: the same scientific summaries and complete slot/failure accounting, excluding private artifact paths, trial verification records and detailed unit receipts. It contains no participant IDs or row-level records; publication itself is a separate coordinator action.
- `EVALUATION_COMPLETION.json`: hashes of all completed result files.

No participant table, canonical reference table or additional generated table is written.

## Verification

`test_evaluate_campaign.py` uses invented arrays/files only and mocks the custody/runtime boundary explicitly. It tests metadata-only manifest preparation, rejection before loading, real Stata parsing on an invented 24-row file, tag/sentinel handling, stripped F/M and strict TSV missing tokens, unit/task binding, unchanged analysis composition against independent QR arithmetic, unavailable denominators, every fixed output slot, alias reuse, failure denominators, whole-stage construction credit, both-case gate and exclusive rerun refusal. The invented full evaluator fixture uses 24-row frames in place of the separately verified production loader; production requires exactly 5,000 generated rows.

Author runs on 2026-11-02: initial **26 passed in 0.71 seconds**; after the two reviewed policy/loader fixes and two new focused tests, **28 passed in 0.83 seconds**. No author test failed. This does not rerun any previously passed frozen suite. Metadata-only manifest preparation succeeded once. Actual target analysis, clinical generation, actual approval and global release were not performed by this implementation work.

```text
python -m pytest work/scaleup_2026-11-01/production_release/evaluation/test_evaluate_campaign.py --basetemp <fresh-short-temporary-directory> --tb=short -q
```
