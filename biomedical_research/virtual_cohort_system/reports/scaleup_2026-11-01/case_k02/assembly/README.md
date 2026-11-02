# K02 source evidence and recipe compiler

This additive component compiles the fixed reviewed Greiner packet into
lifecycle-compatible evidence, provenance, six source-context recipe templates
and the normalized input shape required by S01. It performs metadata translation
only: no candidate is frozen, source statistic evaluated, source parameter
fitted, row sampled, target table read or scientific run authorized.

`compile_source_packet(packet_bytes, task, expected_packet_sha256=...)` is the
pure compiler. It requires exact source bytes and their externally expected
hash, validates supported source meanings and returns new objects. Its hash
check is a retained-byte commitment, not source authentication. The actual
entrypoint `compile_metadata.py` reads only the fixed request/source paths,
checks all 29 files in `REVIEWED_DESIGN_SNAPSHOT.json`, and exclusively writes
`compiled/`. It accepts no substitute source, table or runtime path.

The initial metadata compilation is preserved with its original code hash in
`compiled/COMPILATION_REPORT.json`. Independent review found a narrow validation
gap for deliberately changed fixtures: an evidence ID could disagree with its
analyte field. That identity check and contextual-regression DOI binding were
tightened. `verify_compilation.py` then recompiled the actual metadata in memory,
verified that every existing compiled artifact was identical, checked S01's
input schema without fitting, and wrote `COMPILER_VERIFICATION.json` binding
the current code and the preserved original report. Old run metadata was not
relabelled as a new compiler run.

## Compiled artifacts and meaning

- `evidence.json`: 60 original records in the existing lifecycle schema: 30
  numerical source candidates, 18 contextual age quantiles and 12 contextual
  regression coefficients. There are seven source-descriptor records for six
  strata and the pooled regression context, all from the same original paper;
  they are not seven independent studies. Shared cohort IDs and the same source
  packet hash retain that overlap.
- `record_provenance.json`: every complete original record, its JSON pointer,
  canonical record hash, full-packet byte hash and compiled item hash. Original
  CIs, table-specific counts, row-N uncertainty, applicability and issue flags
  remain available even where the narrow lifecycle schema cannot express them.
- `source_context_templates.json`: six bridge-compatible source entry shapes,
  each with four declared supplemental operators, explicit semantic-v1 gates,
  and empty assumption/review slots. These are **templates**, not executable
  bridge plans or an activation of checks.
- `dispositions.json` and `source_issues.json`: every record's disposition and
  original unresolved issues. Actual disposition counts are recomputed from
  the records, rather than treating every source quantity as operational.
- `s01_normalized_constraints.json` and `s01_normalization_records.json`: the
  exact six-context S01 input shape plus documented percentage normalization.
- `registration_requirements.json`: source IDs, required artifact path and byte
  hash. It contains no fabricated curator screening or registry approval.

The 30 numerical candidates have these dispositions:

| Source quantity | Count | Compiled disposition |
|---|---:|---|
| BMI, TC and HDL geometric means | 18 | Potential descriptive supplemental operators |
| Strict-threshold low-HDL percentages | 6 | Potential descriptive supplemental operators |
| Non-HDL geometric means | 6 | Retained evidence; no executable derived diagnostic |

Non-HDL is absent from the task columns. The compiler neither adds it to the
release nor inserts a derived-variable engine. S01's explicitly prescribed
input interface may retain these reported values for its later analytic fit;
that does not make their source diagnostic executable. Age quantiles remain
contextual with interpolation `not_reported`; regression coefficients remain
`reported_other` with `regression_coefficient_unresolved_scale`, their original
adjustment sets, and no executable OLS operator.

## Units, uncertainty and checks

Lifecycle evidence and feedback keep prevalence point estimates and CI bounds
on their original **percentage** scale. The threshold operator outputs `%` and
retains the original strict `lt` boundary in mmol/L. Only the separate S01 input
view divides the percentage point estimate by 100 and labels the result `1`.
Each of these six conversions retains the full original record, original and
normalized hashes, locator, units and literal one-time division derivation.
No percentage division occurs inside S01 and no CI/SD is supplied to its
normalized input. Other S01 geometric-mean inputs preserve their values/units.

Geometric means stay `reported_other/statistic_name=geometric_mean`; semantic
v1 receives no unsupported geometric-mean operator. Every source weight stays
`not_reported`, and every direct semantic gate remains unavailable. Native
proportion semantics retain the exact threshold but do not override that
weighting limitation. Unknown row-specific N stays `source_n:not_reported`;
reported table-group N remains attached to the original record, never replaced
by a generated row count. CIs stay estimator uncertainty, not residual or
participant SD, precision weights or acceptance bands. Anomalous and rounded
intervals are preserved without guessed repairs.

All supplemental `proxy` values are null. Later descriptive values may be
computed only after actual candidate/context binding and review. A raw
unweighted difference requires a separately declared and independently
approved equal-weight scenario under the existing supplemental collector.
Neither an empty assumption list nor this compiler's success supplies that
approval. The compiler never calls any collector and cannot fall back to the
legacy collector.

## Scientific and lifecycle integration still required

The source metadata specify adult/sex strata and their reported health
selection, assay and fasting conditions. Age/sex predicates retain the source
definition; site stays a context description, not an invented output column.
The male-to-M/female-to-F source encoding is an internal convention, not a
verified biological legend for target F/M. Unavailable disease/pregnancy/HIV
flags are not reconstructed, and these source exclusions do not become target
filters. Units alone do not establish assay, fasting or population equivalence.

The future Agent must author scientific structure, distributions, numerical
parameters and explicit context/transport assumptions. The compiler writes no
model specification or clinical generator. Its `bind_context_assumptions`
helper copies only caller-authored nonempty assumption IDs into the six
templates; the actual model specification and bridge must later verify those
IDs and their meaning. No descriptions or approvals are generated by the helper.

Before execution, the controller must supply the curated registry/source
artifact, the Agent's model/specification, all shared/context-varying settings,
finite source/target row and seed schedules, the target context, and the full
bridge plan. Population and measurement descriptions in model contexts must
match the frozen recipe declarations. Bridge preparation fills the hash slots;
independent reviewers then supply context/binding and any separate proxy
approvals before sealing. There is no approved source-context reconstruction,
strict source fit, model compliance or transport claim in these compiled files.

S01 input-schema compatibility was checked without calling `fit_reference` or
`sample`. That is not a source fit or a claim that the chosen reference model
matches all retained evidence. The full-table validity guard, reviewed target
unit map, authenticated execution and reserved evaluator still need their
actual production integration and global release.

## Verification

Only the new `test_source_compiler.py` suite ran: 18 tests passed in 0.76 s
after the review repair. Its explicitly changed invented packet tests cover
percentage/CI provenance, all-record retention, hash/identity/DOI/denominator/
weight/threshold failures, contextual-only meanings and exact S01 input shape.
Actual semantic-v1 and supplemental declaration validators run on temporary
invented metadata with test-only assumption/review scaffolding; no collector,
generator, freeze, CSV, source fit or sampling runs. The actual metadata compile
and revalidation verified all 29 protected reviewed artifacts unchanged.
The independent review in `INDEPENDENT_REVIEW.md` repeated the new suite:
18 passed in 0.75 s, and audited all actual record projections, normalization,
dispositions and protected hashes with no blocking metadata-scope finding.
