# Assumption-labelled descriptive source feedback v1

This additive collector computes useful named descriptive statistics when the
source leaves weighting or software conventions unreported. It retains three
separate judgments: **calculation**, **source-definition match**, and
**applicability**. It does not change `semantic_feedback_v1`, its strict results,
the old controller, or any frozen candidate. A controller selecting this interface
must retain its strict source feedback separately; a descriptive result never
upgrades an unavailable strict result.

Only a successful, verified execution's `output/generated.csv` supplies numerical
data. The collector verifies the frozen candidate and execution receipt, binds
the output and metadata hashes, and recomputes every diagnostic during receipt
verification. It does not execute a generator, read patient inputs or target
references, choose clinical parameters, or reconstruct a source population.

## Plan authored before freezing

Place `descriptive_feedback_v1.json` in a **new** candidate before its normal
lifecycle freeze. Existing lifecycle hashing automatically includes the file.
Never retrofit an old frozen candidate. Its top-level fields are:

```json
{
  "schema_version": 1,
  "evidence_sha256": "SHA256 of the exact evidence.json bytes",
  "checks": []
}
```

`checks` is nonempty. Each check contains exactly these required fields:

| Field | Meaning |
|---|---|
| `id`, `evidence_id`, `source_locator` | A unique safe check ID, existing evidence ID, and exact evidence locator. The evidence hash binds estimates and source records. |
| `operator` | A supported declarative operator, or null to retain an unavailable diagnostic. |
| `conventions` | Explicit calculation conventions described below. |
| `source_definition` | Independently authored source interpretation described below. |
| `assumption_ids` | A nonempty list of IDs from `model_spec.json` assumptions. Describe the actual convention and transfer assumptions there. |
| `applicability` | `{ "status": "explicit_transfer_assumption" or "unsupported_target_claim", "reason": "substantive explanation" }`. This interface does not certify a matched source context. |
| `reason` | Why this diagnostic is informative, including relevant limitations. |

The operator uses the existing declarative fields `kind`, `unit`, `selection`
(a conjunction of typed predicates), and `missing_policy` (`error` or
`complete_cases`). Numeric operands must exist in the task; filter-only columns
may be categorical. Boolean values cannot substitute for numeric categories.
Statistic units must match the declared task units. No unit conversion occurs.

| Kind | Additional fields | Calculation |
|---|---|---|
| `mean` | `column` | Equal-weight arithmetic mean. |
| `sd` | `column` | Sample SD, denominator n−1, at least two complete rows. |
| `geometric_mean` | `column` | `exp(mean(log(x)))`, returned in the original unit; every used value must be strictly positive. Zero or negative values are never shifted or silently dropped. |
| `median` | `column`, `method: "linear"` | Quantile probability 0.5 with NumPy linear interpolation. |
| `quantile` | `column`, `q`, `method: "linear"` | Explicit probability in [0,1], with linear interpolation. |
| `correlation` | `x`, `y`, `unit: "1"` | Pearson correlation of complete selected pairs. |
| `spearman_correlation` | `x`, `y`, `unit: "1"` | Average ranks calculated within complete selected pairs, then Pearson correlation of those ranks. |

OLS, categorical contrasts, proportions and derived columns are outside this
version. They can be retained with a null calculation operator. Neither a
continuous slope nor a marginal correlation substitutes for an adjusted category
contrast. Geometric means are recognized only when the existing evidence schema
declares `kind: "reported_other"` and `statistic_name: "geometric_mean"` exactly;
the implementation does not reinterpret arbitrary narrative names.

`conventions` has these four keys. Use the shown value for the relevant operator
and null for each inapplicable key:

```json
{
  "weighting": "equal",
  "sd_ddof": null,
  "quantile_method": null,
  "spearman_ties": null
}
```

Set `sd_ddof` to integer `1` for SD, `quantile_method` to `"linear"` for median or
quantile, and `spearman_ties` to `"average"` for Spearman. A null operator uses
the all-null defaults above. Missingness and selection remain explicit in the
operator. Row accounting reports input, selected and used rows and missing
operand rows dropped after selection. It does not purport to reproduce source
nonresponse or unobserved selection variables.

`source_definition` requires:

```json
{
  "definition_status": "not_reported",
  "source_operator": null,
  "weights": "not_reported",
  "transform": "identity",
  "source_variable_units": {},
  "reason": "The central statistic is known, but source operational conventions are not fully reported."
}
```

`definition_status` is `specified`, `not_reported`, or `unsupported`. A specified
definition requires a complete independently authored `source_operator` and
source units for every operand, including selection variables. Other statuses
require a null source operator and empty units. `weights` is `none`, `weighted`,
or `not_reported`; `transform` is `identity`, `nonidentity`, or `not_reported`.
An optional source `conventions` object with the same four keys can explicitly
bind source SD degrees of freedom and rank-tie handling. Without it, SD and
Spearman retain an assumed-convention judgment even if their source operators
are specified.

Source interpretations must be authored from the source, with limitations
retained. Copying a calculation operator into the source definition establishes
only self-consistency. The logarithm inside a geometric-mean calculation is not
by itself a measurement-unit conversion; author the measurement declaration
accordingly, without editing the old strict sidecar.

## Independent outcomes

`calculation_status` is `ready` or `not_requested` at preflight, and `computed`
or `cannot_compute` in a retained report. Empty selections, insufficient sample
sizes, constant correlation operands, disallowed missingness, and nonpositive
geometric-mean inputs receive a reason and null calculation.

`source_definition_match.status` is:

| Status | Meaning |
|---|---|
| `matched_declared` | Supported declared source and calculation definitions agree, including all conventions required here. This does **not** certify source extraction or applicability. |
| `assumed_convention` | The known quantitative evidence definition is compatible, but weighting, measurement mapping, source operational definition, interpolation, SD degrees of freedom or ties remain assumptions. |
| `known_mismatch` | A known statistic kind, variables/adjustment, probability, unit, selection, missingness, weighting, measurement transformation or convention differs. The declared diagnostic may calculate, but its source difference is null. |
| `unsupported` | No calculation operator was requested and no additional known mismatch was identified. |

Thus arithmetic/geometric means and Pearson/Spearman correlations are never
silently interchanged. Evidence metadata is checked even if the source operator
is null, and copying an incompatible calculation into the declared source
operator cannot hide the mismatch. Malformed calculation declarations, unbound
assumptions, wrong evidence hashes/locators and unsupported operators fail
preflight before any arithmetic.

A raw `difference = calculation − reported estimate` is present only for a
computed `matched_declared` or `assumed_convention` check. It is a descriptive
comparison, not source replication, a fit criterion, a clinical tolerance or a
target validation. No discrepancy is standardized by a source CI or SD. Source
SE/CI stay in estimator uncertainty; an SD annotation stays in unresolved source
dispersion; Monte Carlo uncertainty is not estimated. Generated row counts never
become source sample size. Overlapping evidence items remain dependent checks.

`applicability` is retained independently of these outcomes. A sex or age filter
on generated task rows does not replay residence, disease selection, fasting,
assay or sampling design. A numerically matching statistic cannot promote
`unsupported_target_claim` to a supported target inference.

## API and CLI

```python
from cohort_harness import descriptive_feedback_v1 as feedback

feedback.preflight(bundle, candidate)  # declarations only; before freezing
feedback.collect(bundle, candidate, run_id, feedback_id)
feedback.verify(bundle, feedback_id, candidate=candidate, run_id=run_id)
```

`collect_feedback` and `verify_feedback` are aliases with the same signatures.
Reports are written exclusively to
`BUNDLE/descriptive_feedback_v1/FEEDBACK/feedback.json`. Existing IDs cannot be
overwritten. Verification checks both output provenance and exact recomputation,
including source judgments, conventions, assumptions, runtime and code hashes.
These are integrity commitments, not host-security signatures.

```text
python -m cohort_harness.descriptive_feedback_v1 preflight --bundle BUNDLE --candidate candidates/initial
python -m cohort_harness.descriptive_feedback_v1 collect --bundle BUNDLE --candidate candidates/initial --run-id RUN --feedback-id FEEDBACK
python -m cohort_harness.descriptive_feedback_v1 verify --bundle BUNDLE --feedback-id FEEDBACK
```

## Minimal one-check artificial example

Run this Python snippet from the project root with a **new** destination. It uses
the existing aggregate-only artificial fixture, authors one mean diagnostic and
retains unknown source conventions. No patient table or biomedical model is
used. The example demonstrates this collector directly; an adaptive controller
must also retain its separate strict result.

```python
from pathlib import Path
import json
import pandas as pd
from examples.m17a_whole_cohort import prepare
from cohort_harness import descriptive_feedback_v1 as feedback
from cohort_harness.execution import run_candidate
from cohort_harness.lifecycle import freeze_candidate, read_json, sha256

root = prepare(Path("work/new_descriptive_example"), n_rows=8)
candidate = root / "candidates/initial"
(candidate / "generator.py").unlink()  # This new example uses invented direct rows.
pd.DataFrame({"sample_id": [f"example_{i}" for i in range(8)],
              "x": list(range(8)), "group": [0, 1] * 4,
              "y": list(range(8))}).to_csv(candidate / "generated.csv", index=False)
item = read_json(candidate / "evidence.json")["items"][0]
plan = {"schema_version": 1, "evidence_sha256": sha256(candidate / "evidence.json"),
        "checks": [{
            "id": "descriptive_x_mean", "evidence_id": item["id"],
            "source_locator": item["locator"],
            "operator": {"kind": "mean", "column": "x", "unit": "x_unit",
                         "selection": [], "missing_policy": "error"},
            "conventions": {"weighting": "equal", "sd_ddof": None,
                            "quantile_method": None, "spearman_ties": None},
            "source_definition": {
                "definition_status": "not_reported", "source_operator": None,
                "weights": "not_reported", "transform": "identity",
                "source_variable_units": {},
                "reason": "The invented aggregate brief gives a mean but no weighting or missingness convention."},
            "assumption_ids": ["A_fixture"],
            "applicability": {"status": "explicit_transfer_assumption",
                              "reason": "Invented direct rows illustrate the diagnostic, not population reproduction."},
            "reason": "Calculate the equal-weight arithmetic mean of the eight selected rows."}]}
(candidate / feedback.FILE).write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
feedback.preflight(root, candidate)
freeze_candidate(root, candidate)
run_candidate(root, candidate, "run01", 17001)
report = feedback.collect(root, candidate, "run01", "feedback01")
assert report["checks"][0]["calculation"]["value"] == 3.5
assert report["checks"][0]["source_definition_match"]["status"] == "assumed_convention"
assert feedback.verify(root, "feedback01") == report
```

Focused tests use invented direct rows and cover formulas, ties, units, positive
domain, empty/selected rows, assumption labels, semantic mismatch, strict-result
retention and output/metadata/report tampering. Passing these tests supports the
software boundary, not the scientific utility of a generated biomedical cohort.
