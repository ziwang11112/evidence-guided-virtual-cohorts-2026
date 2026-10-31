# M17-A: verified feedback for evidence-only whole-cohort generation

Date: 2026-10-31. Status at initiation: implementation and artificial-data validation authorized by the ongoing project continuation. No new biomedical target is selected or opened.

## Purpose and scope

The user's intended system includes complete virtual-cohort generation from published evidence and a population specification, with no individual records provided. Column augmentation and missing-cell completion remain useful alternatives when observations exist.

The [readiness review](M17A_WHOLE_COHORT_READINESS.md) found that the base harness already supports complete-cohort program and direct-table output. It forbids an observed input table in that mode. The missing connection is reliable post-execution source-statistic feedback: existing linked replay adapters only support enrichment.

M17-A connects the already implemented pieces. It is an engineering unit, not a claim that an Agent generated scientifically valid patients. The prior M15-A source-only direct whole-cohort pilot remains historical; this is not described as the first full-cohort generation in the project.

## Concrete example

Use an explicitly invented two-variable population with aggregate source statements, a small seeded generator and no observed records. The program generates both variables. After freezing and execution, calculate allowed source means, dispersion or regression statistics on the verified output. A later verification repeats the calculation and checks that the frozen recipe, candidate and execution still match.

The invented coefficients test numerical wiring. They are not biomedical relationships, a literature claim or evidence of an Agent's modeling ability. The reference for this engineering check is independent arithmetic, not a held-out patient cohort.

## Minimal adapter

- Read a frozen whole-cohort candidate and a successful verified execution belonging to that candidate.
- Read a predeclared source-feedback recipe bound by the candidate freeze. Validate evidence identifiers, statistic type, units, adjustment variables and declared assumptions using existing checks.
- Read only the generated table identified by that execution. Do not accept an arbitrary caller-supplied table as the generation output.
- Apply the existing deterministic statistical operators. Preserve undefined statistics and discrepancies rather than silently dropping them.
- Store feedback in a new external feedback directory. Do not insert generated rows or reports into an already frozen candidate.
- Bind the candidate, recipe, task, execution and output. The verifier recomputes diagnostics, not merely a stored success flag.
- Distinguish direct-table output from executed generator code. A verified output link does not certify the appropriateness of a source population or measurement mapping.

The first adapter checks the complete cohort that was actually generated. It does not yet construct separate study populations or provide automatic cross-study measurement conversion. Those capabilities require additional explicit design, rather than relabelling enrichment replay.

## Required checks

1. A whole-cohort task has no `observed.csv`; all analytical variables are generated.
2. A correct output yields independently reproducible statistics and unchanged frozen-candidate bytes.
3. A wrong candidate, failed execution or mismatched output is rejected.
4. Modified recipe, receipt or table invalidates verification.
5. Unsupported or undefined statistics retain an explicit status.
6. Code execution remains in the existing isolated runtime; failure does not fall back to importing a generated program on the host.

Use focused artificial-fixture tests and one small actual execution if the already configured runtime is available. No model API, new package installation, training, third-party research-code execution, target download or HPC job is required. If the runtime is unavailable, record the concrete failure and leave actual execution unproved.

## Deliverables

- A small whole-cohort feedback module with collect/verify commands and its interface document.
- Focused boundary tests and a reproducible artificial fixture preparation script.
- An actual engineering result record separating mocked tests, isolated execution and independent arithmetic.
- A private GitHub export of the source, documentation and aggregate results; existing patient and target-generated tables remain local. Complete research papers and downloaded predecessor code remain local as well.

## Subsequent scientific test

After this bridge works, prepare a separately documented controlled study in which an Agent receives only aggregate evidence and a target-population description. Compare compatible and heterogeneous source conditions, while withholding the target individual table. An optional observed-covariate arm measures the effect of additional information and is not pooled with the evidence-only arm.

Freeze generated candidates before assessing predefined scientific analyses, including at least one relation not directly used as feedback. The controls should isolate evidence handling and revision; they need not assume a particular Agent organization or require a new trained model. The controlled truth and any later new biomedical reference belong to a separate evaluation boundary.

Advancement requires an informative scientific result, including a documented limitation, rather than simply more passing engineering checks. M17-A establishes trustworthy feedback wiring only.
