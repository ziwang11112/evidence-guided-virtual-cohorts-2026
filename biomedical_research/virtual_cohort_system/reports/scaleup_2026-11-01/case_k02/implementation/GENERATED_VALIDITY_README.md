# K02 generated-release validity prerequisite

`generated_validity.validate_generated_release(frame, task)` accepts a supplied
pandas DataFrame and canonical K02 whole-cohort task. It returns an auditable
validity report or raises `cohort_harness.contracts.ContractError`. It never
reads a file, launches a generator, filters rows, repairs values or writes data.
The original frame and task remain unchanged on success or failure.

The guard reuses the existing task/output validators and requires exactly the
canonical ordered columns `id, age, sex, bmi, total_cholesterol,
hdl_cholesterol`, with source-native mmol/L lipids. It rejects a wrong row
count, extra/reordered columns, missing/nonfinite/non-numeric data, duplicate or
blank identifiers, an age below 18, any sex code except literal F/M, and **any
zero or negative BMI, TC or HDL value**. It imposes no arbitrary positive floor,
maximum, expected mean, relationship or TC-versus-HDL inequality. Literal F/M
validation does not establish their biological-label legend.

The required row count is `task.n_rows`. The production caller must first
verify the frozen execution and bind the actual approved **5,000-row** task.
The guard itself cannot authenticate the supplied task, a source CSV or its
execution. A caller must not replace the approved task with a smaller row
count after filtering. Small invented unit tests use explicitly smaller tasks;
they are not clinical releases.

Required future integration order:

1. Verify the generator execution and its exact frozen task/output bindings.
2. Read that verified canonical output through the declared lifecycle reader.
3. Call this guard against the bound 5,000-row task; a failure rejects the whole
   generated release. Do not silently drop invalid rows or substitute a seed.
4. Only after validity succeeds, apply the separately reviewed target-analysis
   unit map and the fixed analysis adapter. Confirm all required rows are still
   present; the analysis adapter's reference eligibility filtering must not
   reduce an invalid generated cohort into an apparently valid result.

The result includes canonical task and ordered content hashes, required and
validated counts, and explicit no-filter/no-repair/provenance limitations. These
are logical-content commitments, not CSV byte hashes, signatures, execution
authentication, clinical plausibility assessment or case/global release.
The DataFrame index is not part of the content digest; column/row order and the
identifier values are included.

This is a prerequisite component only. It is **not connected to a global
runner**, and adding it does not activate K02 construction, source feedback or
target evaluation. The reviewed request packet is unchanged. Tests use only
small invented arrays and inspect no clinical data or source articles.

Builder verification: only `test_generated_validity.py` ran; **38 passed in
0.57 seconds**. The checks cover whole-release rejection, immutability, numeric
types, row/schema/identifier defects, strict positivity, age/category rules,
content commitments and trapped file/process/network operations.
Independent static review found no blocking implementation issue, and its
separate run of the same new suite passed **38 tests in 0.55 seconds**. That
review preserves the exact approved-task and execution-binding prerequisite.
