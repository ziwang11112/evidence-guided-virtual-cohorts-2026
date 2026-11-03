# Qualified relationship feedback v1

`qualified_relationships_v1.py` is an additive read-only collector. It calls the
real candidate, execution and `semantic_feedback_v1` verifiers and returns a
report; it never executes a generator, reads a supplied comparison table,
writes a receipt, makes an approval, or alters an old module. The phase
controller must retain the returned report outside the old bridge inventory
and bind it in its own immutable receipt.

```python
declaration_digest(declaration)
compute_qualified_feedback(child_bundle, child_candidate, run_id,
                           semantic_feedback_id, declaration, review)
```

The declaration contains exactly:

```text
schema_version: 1
bindings:
  task_sha256, candidate_freeze_sha256, evidence_sha256,
  model_spec_sha256, semantics_sha256, bridge_plan_sha256
context_role: source
context_id: <the model specification's active_context>
population: <exact actual child task population>
measurement: <exact child recipe and model-context measurement description>
source_ids: [<exact source IDs of that frozen bridge context>]
assumption_ids: [<nonempty frozen model assumption IDs>]
column_aliases:
  - source_name: <new native evidence name>
    generated_name: <original numeric generated task column>
    assumption_ids: [<nonempty frozen model measurement assumption IDs>]
checks:
  - id, evidence_id, semantic_check_id
    operator: <existing source_checks operator, or null>
    source_relation: <object below, or null>
    measurement_mapping: <object below>
```

The `context_bridge_v1.json` copied into the frozen child must identify its
active context as a source with the same source IDs. A target cannot become a
source by supplying a different declaration label. Each evidence item must
belong to that source scope and its linked v1 check. Checks cover exactly the
declared source IDs; repeated check/evidence IDs are rejected. Population and
measurement are context assumptions bound by the independent review, not
certified reconstruction of original participants.

The independent review is the existing commitment form:

```text
decision: approved
independent: true
reviewer_id, producer_id, reviewed_utc, reason: <nonempty strings>
approved_sha256: declaration_digest(declaration)
```

Reviewer and producer must differ after trimming and case normalization. No
identity authentication or cryptographic signature is implied. The review
must inspect the source relationship, all unresolved details, task variable
meaning, binary category membership, measurement map and mathematical model.

The explicit source relation contains exactly:

```text
kind: same_reported_functional_under_declared_assumptions
assumed_weights: equal
assumption_ids: [<nonempty frozen model assumption IDs>]
unresolved_original_details: [<nonempty statements>]
reason: <why this qualified functional is interpretable>
```

The original v1 binding must retain `weights: not_reported` and unavailable
status; its output must retain null calculation and discrepancy. A missing
proxy operator or explicit source relation produces an unavailable qualified
result. Known original operators must match the qualified operator. A null
original operator is permitted only for a separately explicit, reviewed source
relation; the original unresolved record is copied into the returned result.

Supported operators are `ols_coefficient`, `correlation` (Pearson) and
`spearman_correlation`. They use the existing `source_checks.apply_operator`
arithmetic, whole predeclared analysis tables (`selection: []`) and
`missing_policy: error`. No row deletion, imputation, weighting or optimization
is implemented. Pearson and Spearman require at least three pairs and
nonconstant columns; Spearman uses average ranks for ties. OLS requires an
intercept, the exact evidence adjustment set, one numeric nuisance and one
explicit binary nuisance: either numeric categories `[0, 1]`, or an integer
column with declared `minimum: 0` and `maximum: 1`. Both categories must be
observed, with positive residual degrees of freedom and full rank. Other
integer columns are never guessed to be binary.
Only the focal coefficient is compared. These restrictions support the two
separate Jansen projections; adding the other focal predictor changes the
adjustment set and fails. The category mapping must be declared in the
scientific context and independently reviewed; its historical numeric coding
is not inferred.

`column_aliases` is a required list, empty when no aliases are needed. It defines
one-step read-only views of existing generated columns, with every kind, unit,
bound, category and other column contract copied unchanged. No original column
may be overwritten; source names must be unique, and aliases cannot refer to
other aliases. At most 32 aliases are allowed. Numeric generated columns
include number/integer columns and explicitly numeric categories, not the row
identifier. Distinct operands in any single operator must trace to distinct
generated columns, including through the HbA1c map. Thus `FPG` and `FSG` may
both name `glucose` for separately reviewed source-context comparisons, but
cannot be used as two distinct measurements in one correlation or regression.

For the existing canonical task, reviewed aliases can bind `gender_binary` to
`female`, `BMI` to `bmi`, context-specific `FPG` or `FSG` to `glucose`, and
`HbA1c_percent` to `hba1c`; `age` already has its native name. These names do not
establish specimen, fasting, assay or population equivalence. The independent
review must explicitly assess those measurement assumptions. Bounds are also
unchanged: aliases cannot broaden an age range or reconstruct source support.

An identity mapping is exactly `{"kind":"identity"}`. Alternatively the only
implemented measurement map is:

```text
kind: hba1c_ngsp_to_ifcc
input_column: <existing numeric % task column or one-step alias>
output_column: <new native IFCC response column>
ngsp_percent_per_ifcc: <finite positive reviewed scale factor>
ngsp_percent_intercept: <finite reviewed intercept>
unit_evidence_id: <frozen contextual evidence item naming both representations>
assumption_ids: [<nonempty frozen model assumption IDs>]
```

It applies `IFCC = (NGSP_percent - intercept) / scale_factor` to a temporary
analysis view. No arbitrary affine map, predictor conversion, existing-column
overwrite or assay equivalence is accepted. The unit evidence and review must
establish that these are the HbA1c representations and correct documented
constants; the collector cannot verify a prose source or infer a clinical
conversion. It does not hardwire a clinical coefficient. The bridge's older
unit utility is multiplication-only and target-analysis scoped, so it cannot
perform this affine native-response map. Identity-native outputs are preferred
when already supplied. Both parenthesized and unparenthesized per-unit OLS
strings are supported without changing evidence bytes.

Each result is `kind: qualified_assumption_comparison` and retains the original
source weights, reported evidence, strict result, chosen operator, assumptions,
measurement map, calculated point and raw difference. Exact-source eligibility
is always false, strict difference is null, uncertainty conversion is none,
and pooled loss is null. Numerical failures remain unavailable, with no repair.
The report binds the actual execution output, execution/strict receipts,
candidate freeze, task, evidence, model, bridge plan, declaration, review and
calculator code. It does not establish law validity, original-source
reconstruction, transport, or independent evidence from simulated rows.

The receipt tests use invented arrays, source metadata and review records.
They mock the process/runtime boundary while exercising the real freeze,
execution receipt and v1 verification code. A separate compatibility test
reads the existing E1 evidence definitions and canonical task schema, then
checks their operators on eight explicitly artificial rows. It reads no
participant data and executes no clinical generator. These are not scientific
approvals, source reconstructions or evidence of sandbox operation.
