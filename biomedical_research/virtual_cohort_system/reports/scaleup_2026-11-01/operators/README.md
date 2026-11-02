# Small context-aware statistics utility

2 November 2026. This directory adds a pure **in-memory** utility and analytic
tests. It does not modify frozen harness modules, receipts or candidate files.
It does not read tables, find participant files, execute a generator, call a
collector, or integrate a new operator into the released campaign pipeline.

## Existing capabilities and the narrow addition

`cohort_harness/source_checks.py` and `semantic_feedback_v1.py` already support
threshold prevalence as `proportion`, using a threshold `event`, conjunction
`selection` predicates, explicit `1`/`%` units and missingness policy. Sex/site
strata can be declared in the selection. Thresholds must retain the original
boundary convention: `>` and `>=` are different events.

Median and individual quantiles also exist, with an explicitly declared
`linear` interpolation convention. The strict collector leaves an unreported
source convention unavailable. There is no dedicated IQR operator. Quartiles
can be represented separately when their definitions are established; an
unknown convention or an IQR alone should not be silently converted into SD,
mean, precision weights or an exact source discrepancy.

Geometric mean is absent from the frozen evidence-kind schema, semantic gate
and arithmetic. `contextual_statistics.py` adds only its point calculation:

```text
exp(sum(log(x)) / n), for finite, strictly positive original-scale x
```

This calculation avoids multiplying observations. Zero/negative selected
values make the diagnostic unavailable; they are not dropped, offset or
clipped. Natural-log/log10/unknown input scales are declared but unsupported:
the utility does not guess a log base or silently back-transform inputs.

The utility also wraps threshold prevalence using the **existing**
`source_checks.apply_operator` arithmetic. It adds shared context checks and
explicit handling of missing selection variables; it does not implement a
second prevalence formula or a general statistics framework.

Geometric-mean source evidence must not be relabelled `mean` merely to pass
the old evidence validator. Until separately reviewed pipeline integration,
preserve its original reported kind in a separate declaration or the existing
`reported_other` representation, with its source meaning/locator intact. The
new utility is not a legacy-collector fallback and cannot produce a v1
feedback receipt for geometric mean.

## API and declarations

```python
contract = context_contract(frame, operator, table_context, source)
# Independent substantive review occurs separately; no approval is created here.
result = diagnostic(frame, operator, table_context, source,
                    approval=independently_reviewed_record)
```

`frame` is an already supplied pandas DataFrame. Only scalar numeric and
categorical variables are supported; there is no file-path argument.

`operator` has exactly:

```text
kind: geometric_mean | proportion
unit: <original measurement unit for geometric mean; 1 or % for proportion>
column: <geometric-mean operand, only for that kind>
event: {column, op: gt|ge|lt|le, value: <finite numeric threshold>}
       # only for proportion
selection: [{column, op: eq|ne|lt|le|gt|ge|in, value}, ...]
selection_missing_policy: error | exclude
missing_policy: error | complete_cases
```

For example, a female/site-A source stratum is represented by two predicates,
`sex == "F"` and `site == "A"`, with the category coding explicitly declared.
An empty selection explicitly means no additional row predicates; it does not
erase source eligibility restrictions from the population/context contract.
The missing-selection policy is separate because missing sex/site membership
cannot be assumed eligible. Missing numeric values are excluded only under
`complete_cases`. Nonfinite values, Boolean encodings and implicit numeric
conversion are rejected where the operand/selection requires a numeric value.
Categorical/string selection is limited to `eq`, `ne` and `in`; its ordering
is never inferred from string sorting or pandas category order. Ordered
predicates (`lt`, `le`, `gt`, `ge`) require both a numeric non-categorical
column and a declared `original` scale. Unknown, natural-log and log10
selection scales make the diagnostic unavailable, including equality tests;
there is no implicit scale interpretation or conversion. These restrictions
apply before both geometric-mean and delegated prevalence calculations.

`table_context` has exactly:

```text
kind: source_context_simulation | target_context_generated | analytic_fixture
context_id: <explicit identifier>
population: <eligibility, age/sex/site and other population definition>
measurement: <assay, specimen and measurement definition>
variable_units: {every operand/selection column: <unit>}
variable_scales: {every operand/selection column:
                 original|categorical|natural_log|log10|not_reported}
```

`source` has the same five context/measurement fields except `kind`, plus:

```text
source_id; locator: <nonempty source identity and precise source location>
operator: <the explicit reported operator, or null if unresolved>
definition_status: specified | not_reported | unsupported
weights: none | weighted | not_reported
uncertainty_role: estimator_confidence_interval | estimator_standard_error |
                  between_person_dispersion | not_reported | unresolved
```

Source operator and table operator must match exactly for source-check
eligibility, including threshold boundary, selection and denominator rules.
Units and scales cover selection columns as well as the statistic operand.
No unit, assay, population, adjustment or weighting conversion is implemented.

The approval record has exactly `decision:"approved"`, `independent:true`,
nonempty `reviewer_id`, `producer_id`, `reviewed_utc`, `reason`, and
`approved_contract`. Reviewer and producer identities must differ.
`approved_contract` must equal the full output of `context_contract` for these
inputs. That contract includes the operator, both descriptors and a SHA256
commitment to the relevant supplied columns and their row order. Numeric,
categorical and missing cells have explicit typed encoding; finite floats use
their hexadecimal representation. Index/unrelated columns are not committed;
different missing representations are normalized. This is not a CSV-byte hash
or an execution receipt. Category dtype/order is not committed: only supported
order-independent categorical predicates are allowed, so such ordering cannot
change an eligible result under the same scalar commitment. Approval is never
generated automatically.

## Descriptive diagnostics versus source checks

The result deliberately separates:

- `diagnostic_available`: whether the requested **unweighted** calculation is
  defined on the supplied table, with a value, unit and row accounting.
- `exact_source_check_allowed`: whether that diagnostic is eligible for an
  exact check **under the independently approved declared source contract**.

The second field requires a source-context simulation, matching population,
measurement, units/scales, operator, source weighting explicitly `none`, and
the matching independent approval. A target table remains a target-context
diagnostic even if someone approves its metadata. A source label without
approval is insufficient. Relabelling a previously approved target table or
changing relevant table values invalidates that approval.

Unknown or weighted source estimators remain ineligible. An unweighted table
diagnostic can still be displayed, but the result explicitly records
`diagnostic_weights:"none"` and the distinct `source_weights`; it is not an
equal-weight interpretation of the original estimator. No optional source
proxy or alternative weighting assumption is silently enabled.

No reported source estimate is compared here, and there is no agreement,
acceptance, loss, uncertainty or scientific-validity score. In particular,
geometric means/prevalences can be useful constraints without identifying the
joint distribution or every adjusted relationship. Source CIs/SEs remain
estimator uncertainty; this utility accepts only their declared role and
performs **no CI-to-SD conversion** or precision weighting. Generated row
counts are bookkeeping, not additional source participants or certainty.

The frozen whole-cohort collector evaluates the actual task population; it
explicitly implements no source-population reconstruction. Filtering a target
table to a source's sex/site labels does not solve selection, measurement or
transport differences. A real source-context construction and substantive
approval are still necessary before using the new eligibility flag in a
future reviewed adapter.

## Limits and verification

The context contract is a procedural commitment, not an authenticated
signature, proof of source extraction, generator provenance, true population
membership or absence of target-data contamination. A host user can coherently
rewrite data, declarations and approvals. The utility cannot establish that
scientific assumptions are justified; those remain review responsibilities.
It must not be described as an isolation layer or an implemented campaign
source-replay pipeline. `collector_integrated` is always false and
`scientific_validity` is always `not_assessed`.

Only the new `test_contextual_statistics.py` suite ran: **31 passed in 0.85
seconds**. Tests use small invented arrays with closed-form answers, explicit
sex/site strata and mocked approvals. They cover geometric versus arithmetic
mean, product-overflow avoidance, nonpositive/nonfinite/empty inputs, explicit
missing policies, strict/inclusive prevalence boundaries and denominator,
unknown weighting, target/source label changes, changed input commitments,
context/units/selection mismatches, unsupported scales and absence of data-read,
process or network calls. These are arithmetic and contract checks, not new
patient validation. No old passed suite was rerun.

Independent review then identified two selection-semantic gaps: a scalar
commitment did not bind category order, and an unknown selection scale could
remain eligible. The restrictions above address both. Only the new affected
tests ran after those fixes: `-k selection_review` gave **21 passed, 31
deselected in 0.62 seconds**. The regression cases exercise both statistic
paths, reproduce the unchanged scalar hash under reversed category order,
preserve equality/membership and original-scale numeric thresholds, and reject
unknown/log or ordinal-category selection thresholds. The expanded full suite
was not rerun.
