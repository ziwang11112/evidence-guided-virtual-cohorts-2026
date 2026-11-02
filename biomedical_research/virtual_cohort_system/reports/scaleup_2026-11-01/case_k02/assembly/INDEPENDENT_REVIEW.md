# Independent K02 source-compiler review

Reviewer: `/root/context_bridge_review`, 2026-11-02. Producer:
`/root/context_bridge_build`. Scope: `source_compiler.py`, the bounded metadata
entrypoint and verification script, their new tests, and the retained compiled
metadata. The immutable request, current campaign STATE and existing semantic
v1/supplement contracts supplied the review boundary.

**No blocking finding remains for this metadata-only assembly.** This accepts
the source-to-schema translation and its pending templates. It does not approve
candidate-local assumptions, equal-weight proxy comparisons, source population
reconstruction, a scientific construction, execution, case admission or global
release. No target file, clinical fit, sample, source-check computation or new
study was accessed or run during this review.

## Finding and repair

The first reviewed compiler checked the allowed record-ID set but did not
explicitly bind each GM/prevalence ID's analyte/statistic suffix to those fields.
An altered fixture could retain a BMI ID while relabelling its contents as HDL.
The actual fixed-byte source packet did not contain that error, and the bounded
entrypoint already pinned its bytes. The author added the narrow identity
cross-check and an adversarial test; the final code rejects that mismatch.
A regression DOI cross-check was also added. Report counts now derive from
actual dispositions and evidence/template lengths.

The original metadata compilation and its truthful original compiler hash were
preserved. `COMPILER_VERIFICATION.json` separately binds the repaired code and
reports that its in-memory metadata recompilation matches all eight original
outputs. It does not rewrite the earlier report as though the repaired code
had produced it initially. I independently verified the current-code,
verification-script, original-report and all eight retained-output hashes.

## Actual retained evidence audit

A read-only audit compared all 60 compiled evidence items and provenance
records against the approved original packet. IDs and coverage matched exactly.
Original values, units, locators, source relationships, uncertainty, issue IDs
and complete original records were retained. Provenance pointers resolve to
the matching source records; original-record and projected-item hashes match.
The full source issue list is unchanged.

The actual dispositions, independently counted rather than accepted from the
report's totals, are:

| Source quantities | Count | Compiled disposition |
|---|---:|---|
| BMI, TC and HDL geometric means across six contexts | 18 | Potential direct supplemental descriptive diagnostics |
| Strict-threshold low-HDL proportions | 6 | Potential direct supplemental descriptive diagnostics |
| Non-HDL geometric means | 6 | Retained evidence and reference inputs; diagnostic unavailable without a separately reviewed derivation path |
| Age quartiles/medians | 18 | Context only; quantile convention remains unresolved |
| Table 3 regression coefficients | 12 | Context only; transform/scale and unavailable adjustments remain unresolved |

Thus all **30 numerical candidates** have a disposition, as do the 30 contextual
records. All 60 are inactive. The six non-HDL items are not silently discarded,
converted into another mean, added as output columns or made executable.

Geometric means remain `reported_other` with
`statistic_name="geometric_mean"`; they are not arithmetic means. Their v1
operators remain null and unsupported. Table 3 coefficients similarly remain
`reported_other`, explicitly labelled unresolved regression scale, with
reported adjustment sets, intervals and full original records retained. They
are not encoded as verified raw-scale slopes, correlations or joint-model
coefficients. No desired clinical relationship or model parameter was authored
by this compiler.

CI lower/upper/level values are mapped to lifecycle CI fields without numerical
conversion. Their roles remain estimator uncertainty; no individual/residual
SD, fitting weight, acceptance interval or generated precision is inferred.
Printed anomalies and rounded/collapsed intervals survive the translation.
Table-specific group counts and denominator qualifications remain attached to
the original records and selection metadata. The direct semantic bindings use
`source_n: not_reported` because row-specific analysis N is unresolved; neither
the group count nor the proposed 5,000 generated rows substitutes for it.

## Percent normalization and reference interface

Lifecycle prevalence evidence and its CI bounds remain in the original `%`
unit. The corresponding supplemental and native source operators also return
`%`, with the original strict `<` threshold and eligible-subgroup denominator.
No threshold, lipid unit or confidence interval is silently rescaled.

Only the separate S01 input view divides each of six prevalence point values
by 100 and labels the result unit `1`. I checked each normalized record against
its original, including identity, locator, threshold and threshold unit. Each
normalization record retains the complete original percentage record and hash,
the normalized record and hash, and the explicit division with
`times_applied=1`. No CI/SD field enters the reference input view. The BMI, HDL
and non-HDL GM inputs retain the original point values and canonical units;
the compiler does not take their logarithms or derive parameters.

The six normalized contexts have exactly the fields and record identities
expected by the pure reference interface. The new test invokes only that
interface's input validator on changed/invented source values, with fit/sample
functions trapped. The author's retained metadata verification also validates
the actual normalized input schema without fitting. My actual-data audit
checked the schema projection and arithmetic directly; I did not call the
clinical fit or sampler.

## Context and feedback boundary

Each of six templates declares one corresponding source descriptor. Its four
recipe checks cover exactly that declared source ID, and each supplemental
check references the same ID, original locator, full population and measurement
descriptor. The seven lifecycle source descriptors (six strata plus pooled
regression evidence) describe one original paper and overlapping source
cohorts; they are not seven independent studies or confirmations.

The full original adult/health eligibility and assay/fasting descriptions are
metadata. The explicit available-column selections are only age at least 18
and the internal source sex code. The compiler does not reconstruct pregnancy,
HIV or diabetes status, declare the target free of those conditions, equate
source sites with target lifestyle categories, or establish assay/specimen/
fasting equivalence. F/M is an internal encoding convention, not proof of the
target biological-label legend. Future context review must inspect the
Agent's scientific population/composition assumptions and implementation;
matching strings or hashes alone cannot certify that reconstruction.

Every v1 recipe check is `not_computable`; all source weights remain
`not_reported`. The threshold definition can be specified while its exact
weighted-estimator comparison remains unavailable. All geometric v1 bindings
retain null operators. There is no legacy-feedback fallback or promotion to
valid source replay.

The actual templates have empty assumption lists, empty candidate-dependent
hashes, `context_review=null`, and `proxy=null` for all 24 potential supplemental
diagnostics. They therefore cannot pass the bridge/collector's required
candidate-local binding review as emitted. `bind_context_assumptions` only
copies externally supplied IDs; it writes no descriptions, model parameters or
approvals. Even after legitimate context review, `proxy=null` permits only
descriptive statistics, with no numeric source discrepancy. A later raw
unweighted difference requires a separate actual proxy review tied to declared
assumptions; it still cannot establish exact source-estimator agreement.

`registration_requirements.json` is a list of required artifact registrations,
not a fabricated screening or admission approval. The original source bytes
must still be registered and retained in any future lifecycle bundle.

## Verification and preservation

The author reports **18 new tests passed in 0.76 s** after repair. I independently
ran only `test_source_compiler.py`: **18 passed in 0.75 s**, using a fresh
temporary directory. These are separate executions of the same 18 tests, not
36 distinct tests. The suite uses modified/invented numerical records with
source metadata structure and real contract/semantic/declaration validators.
Its synthetic review records exist only inside temporary validator fixtures;
they are not approvals of the actual clinical templates. No fixture is frozen,
no row CSV is created, and execution/feedback/process/network calls are trapped.
No passed old suite was rerun.

Before and after this review, all **29** files listed in the protected reviewed
design snapshot matched their recorded hashes. The immutable request/source,
prior component code and reviews, unit approval, exposure amendment and earlier
snapshot were not edited. The sole reviewer-authored repository artifact in
this work unit is this document. No STATE, export, Git or older review file was
changed by this reviewer.

## Commitments

| Artifact | SHA256 |
|---|---|
| `source_compiler.py` | `e7d3835dc48bda1feb6de0b16b11efd8dd2c83decf3100674ee50965bed2f3cb` |
| `compile_metadata.py` | `e719133fa0501a0823d1ac598af338b55b417ae086bf81a3970b335a69ac3c12` |
| `verify_compilation.py` | `c38cce556757474189ee9f4ff23d1463a9bcd3a8197658fe0547e999a059aed6` |
| `test_source_compiler.py` | `e41a7d513ec87f2eda5037b65368b017c76329ebdeadf367441a3fa320ba31bd` |
| `COMPILER_VERIFICATION.json` | `bf8397fca94b4108bc029dd21fe3cd6c4125c9ddd43a9ffaade7fe67b380cb11` |
| `compiled/COMPILATION_REPORT.json` | `0cda12eaae358351c1c82d8c3f85cdd5d161cc036360f7aa86f43f9934662ccb` |
| `compiled/evidence.json` | `3730663b4ebd955be9c43a36cda287e296eed735e1ad7c931900f3583f016ba8` |
| `compiled/source_context_templates.json` | `a7e308c6cfee8670d5a78c724978bccdd63c317c070a3a138a453d8a443c9484` |
| `compiled/s01_normalized_constraints.json` (file bytes) | `027facfd13661720e5f152a8d0aa782893f7ab3098f92eb9fa1c29746b0172a7` |
| Normalized constraints (compiler canonical JSON) | `12540c73bf96f30aae44d31152c722e8f08d732d6e51c80830958e2723ac6a4e` |
| Original source packet | `34eeb0be18f7a9d015e9a7d2446beeb10beb134d389315c998a22199f7d7e753` |
| Protected `REVIEWED_DESIGN_SNAPSHOT.json` | `bb2d10a9237ed2733fccd02dd64789d95e487212f03890f2e9b35d0e18cf03ff` |

The preserved compilation report and current verification record bind the other
retained metadata files. This review supplies no clinical-release flag.
