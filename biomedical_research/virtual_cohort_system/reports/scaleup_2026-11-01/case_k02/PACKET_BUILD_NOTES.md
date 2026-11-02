# K02 request packet build notes — coordinator only

2 November 2026. The draft in `request/` is an Agent-visible clinical request
and context/evidence packet. It is not a model, generator, executable bridge
plan, case admission or global release. No source check is activated.

The target task is whole-cohort generation of 5,000 rows with ordered columns
`id, age, sex, bmi, total_cholesterol, hdl_cholesterol`. `id` is a string
identifier; age, BMI and both lipids are numeric; sex is categorical F/M. All
values are required. The target age lower boundary is 18, selected prospectively
by the investigator. BMI/TC/HDL must be strictly positive without an invented
numerical floor. The existing basic task contract cannot encode an exclusive
lower bound, so the clinical request records that case-validation requirement.
All 5,000 required generated rows must meet it. The analysis adapter's reference
eligibility filtering must not silently turn invalid generated values into a
smaller delivered cohort; a separate generated-output gate is required.

Every generation context uses age in years, BMI in kg/m², and TC/HDL in mmol/L.
The separate root-owned unit mapping will produce the mg/dL target analysis
view after its review. No clinical conversion factor is selected or activated
by this packet builder. Unit conversion is not assay/fasting harmonization.

The source packet was copied byte-for-byte. Its original SHA256 remains:

`34eeb0be18f7a9d015e9a7d2446beeb10beb134d389315c998a22199f7d7e753`

Each of the six source contexts retains its original context record, actual
cohort/country/site/sex metadata, source eligibility, measurement method,
fasting qualification, table-specific counts and eight original record
references. The resulting 48 references include 24 geometric means, six
threshold proportions and 18 age quantiles. Twelve pooled source regression
records remain in the immutable source packet and are linked as contextual
evidence, not numerical target or subgroup equations.

The potential direct descriptive path covers 18 BMI/TC/HDL geometric means
and six HDL proportions. Six non-HDL geometric means remain evidence only
because the frozen output lacks a non-HDL column and no derived diagnostic
view is supplied. Unknown source weights prevent strict source-estimator
checks. Geometric means also stay unavailable in frozen semantic v1.
Unweighted proxies would require separately reviewed assumptions; none is
approved or activated here.

## Input and information-boundary audit

Permitted coordinator inputs inspected were the current `STATE.json`,
`METHOD_AND_EXPERIMENT_DESIGN_v1_2026-11-02.md`, the K02 coordinator decision,
the methods-only Turkana review, the Greiner candidate packet and existing
source/operator reviews, and the existing prospective analysis specification.
The evidence-cohort skill and harness interface supplied contract guidance.
These coordinator documents are not themselves constructor inputs: some
contain evaluation or exposure context. Only sanitized population,
eligibility, measurement and formula metadata were transferred to the packet.

No target participant file, target fitted estimate, new study or search,
external download, scientific candidate, submitted generator or execution was
accessed or produced. Target availability counts, demographic frequencies,
clinical moments, expected effects, evaluation margins, target-study outcome
narratives, historical target results and other constructions were excluded.
The original source evidence was neither edited nor numerically reinterpreted.
No complete third-party paper is copied into the packet.

The target demographic/BMI/lifestyle/joint distributions remain explicitly
unspecified. Shared structure, model families, numerical parameters and
context-varying settings remain future Agent choices with provenance and
assumptions. Missing joint relations, weights or assay bridges are described
with their consequences; they are not each promoted to an independent release
blocker. The remaining operational requirements are finite source/target
schedules, the reviewed unit map, actual scientific construction declarations,
case/global release and the downstream verification path.

## Checks and review

The harness `validate_task` check passed. A focused packet integrity audit
verified all draft manifest hashes, unchanged source bytes, all six original
source contexts and 48 linked records, exact measurement references, source
constraint disposition, the 5,000-row/age/F-M/unit contract, zero activated
checks, and absence of CSV/model-spec/generator artifacts. No old test suite
or real data execution ran.

The independent reviewer identified an overstatement of the target F/M
biological-label legend. The packet and build script were corrected: only
literal F/M categories are verified, with the biological legend explicitly
unverified. Source male-to-M/female-to-F encoding is an internal convention,
not confirmation of the target legend. The selected BMI and residual-correlation
estimands do not require a biological interpretation of the label orientation.
No new metadata search was needed.

The task-template SHA256 after that correction is unchanged:

`ca7f255c428aba919f01368e338046ad17a1cf129dd2ca0decf0173d1893debf`

The independent reviewer rechecked the repaired metadata, all current manifest
bytes, six source encodings and task/unit-contract alignment, and reported no
further blocking packet-content finding. The strict-positive generated-output
gate above remains an operational prerequisite, not a demand to supply clinical
model values. The corrected packet's manifest SHA256 is:

`5c85e316672f970e94337b8a22fe6b4da9de4d731d7f5234c3c4c9f87187d93f`

Nothing in this note changes `STATE.json`, existing frozen artifacts, exports
or the campaign's release state.
