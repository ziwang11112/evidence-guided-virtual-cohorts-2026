# Explicit units between generator output and target analysis

2 November 2026. This additive, pure in-memory adapter supports one reviewed
multiplicative unit conversion per same-named numeric column. Generator tasks
can retain identical canonical units in every source and target context. A
separate analysis copy can then use the units required by its target-analysis
contract. This adapter does not launch a generator, write a scientific table,
read files, fit a relationship, or modify any frozen harness component.

`output = input * factor` is the only nonidentity operation. Factors must be
finite and positive. Identity is explicit for every other column. Offsets,
logs, standardization, imputation, derived columns, row selection, renaming,
ordering changes and assay correction are unsupported. Original numeric
scales and categorical/string identity are the only supported scales.

## API

```python
mapped, receipt = convert_frame(
    frame, manifest,
    input_contract=input_contract,
    output_contract=output_contract,
    expected_input_sha256=expected_frame_digest,
    caller_binding={
        "execution_receipt_sha256": verified_execution_receipt_hash,
        "generated_csv_sha256": verified_output_byte_hash,
        "analysis_task_sha256": fixed_analysis_task_hash,
    },
)
```

The caller must first verify the actual execution, its output and all expected
task/candidate bindings through the supplied lifecycle. It then computes
`frame_digest(frame)` on the verified, parsed frame and passes that commitment
as `expected_input_sha256`. A stale or different frame fails. The caller also
checks that the declared input and output contracts really correspond to its
task and fixed analysis schema. The adapter validates the declared contracts;
it does not discover their relationship to external files.

`caller_binding` is a required, nonempty finite JSON object. It is copied and
hashed in the receipt, with
`execution_binding_status: caller_asserted_not_verified_by_unit_adapter`.
Supplying hashes here does **not** mean the adapter authenticated a run.

`frame_digest` binds every value, ordered column, pandas dtype name, row order,
index value and index name, using typed cells and exact hexadecimal float
representations. This digest is not a CSV byte hash. Frame attributes and
unobserved categorical levels are outside it. The returned receipt binds the
input and output frame hashes, both contracts, full manifest, reviewed proposal
and caller binding. The original frame is not mutated. Numeric multiplication
uses float arithmetic and rejects nonfinite results, underflow to zero, and
integer inputs/factors that would lose precision in conversion to float.

## Contracts and review

Each input/output contract has exactly:

```text
row_id: name of the identifier column
columns: ordered list of {
  name, kind, role, analyte_id, unit, scale
}
```

Kinds are `number`, `integer`, `string`, or `category`. Numeric scales must be
`original`; strings/categories use `categorical`. Exactly the declared row ID
has role `identifier`; other role names are explicit nonempty strings. All
columns, kinds, roles, analyte identities and scales must match between input
and output; only units may differ. Multiplication is limited to nonidentifier
`number` columns. Strings/categories require string values; all numeric values
must already be finite numeric data, without boolean values or string coercion.
Missing values, duplicate row IDs, unmapped columns and column-order mismatches
fail before a result is returned. Index and identifiers remain unchanged.

The manifest has exactly:

```text
schema_version: 1
purpose: target_analysis_unit_conversion | analytic_fixture
input_contract_sha256: contract_digest(input_contract)
output_contract_sha256: contract_digest(output_contract)
columns: ordered list of {
  column,
  operation: identity | multiply,
  factor,
  source: null | {
    kind: official_unit_documentation | invented_fixture,
    reference, locator, analyte_id, input_unit, output_unit
  }
}
review: {
  decision: approved,
  independent: true,
  reviewer_id, producer_id, reviewed_utc, reason,
  approved_sha256: manifest_digest(manifest)
}
```

Identity requires unchanged units, factor 1 and null source. Multiplication
requires differing units, a nonunit factor and provenance naming the exact
same analyte and unit direction as the contracts. Invented provenance can be
used only with purpose `analytic_fixture`. A cholesterol conversion cannot be
assigned to a different analyte under an unchanged source declaration.

`manifest_digest` excludes only the `review` field. `contract_digest`,
`manifest_digest` and `validate_manifest` are available to callers. No function
creates an approval. Reviewer/producer identifiers must differ after trimming
outer whitespace and case-folding, and the review
must bind the exact typed JSON proposal. Thus changing `2.0` to `2` also requires
review again. Review hashes are procedural commitments, not signatures or
proof that a cited factor is correct. Independent scientific review must check
the original official source, analyte, direction, exact factor, intended use
and both external task schemas. Coherent relabelling of a false source by the
caller cannot be detected by a pure unit adapter.

Analysis thresholds and selections must already be declared in the resulting
output units. This adapter does not transform thresholds or existing evidence,
or reinterpret a source statistic. The source-feedback path should continue to
use its canonical source-unit frame. Hashing a conversion manifest alone does
not apply it; the numeric `convert_frame` call is required before target
analysis consumes the mapped frame.

## Current scientific activation and verification

The admitted Greiner review and source metadata identify source mmol/L and
target mg/dL but contain no authoritative conversion factor. **No real lipid
factor, production manifest, scientific review approval or target table is
included or activated.** The existing review also records assay/specimen and
fasting differences; a unit conversion cannot establish assay or population
equivalence or resolve the source regression's raw/log ambiguity. No new
original-study review, target-data access or biomedical source retrieval was
performed for this adapter.

`test_unit_conversion.py` uses only invented three-row arrays and the explicit
toy definition `toy_B = 2 * toy_A`. Test reviews are clearly synthetic. They
exercise numerical conversion, identity preservation, exact content bindings,
stale reviews, wrong analytes/directions, nonfinite and missing values,
unsupported transforms, unmapped columns and arithmetic limits. These are
adapter tests, not evidence of a clinical conversion or a verified full
generator execution.

Run from the project root:

```text
python -m pytest work/scaleup_2026-11-01/bridge_units/test_unit_conversion.py -q -p no:cacheprovider
```
