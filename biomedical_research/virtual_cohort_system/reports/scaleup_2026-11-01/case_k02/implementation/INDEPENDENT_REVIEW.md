# Independent review of the two pure K02 components

Reviewer: `/root/context_bridge_review`, 2026-11-02. Authors:
`/root/context_bridge_build` (generated validity) and
`/root/context_unit_contract` (statistical reference).

**No blocking implementation finding within the authorized pure-component
scope.** The components implement the separately reviewed design and passed
their new invented-input suites. One additional small composed check passed.
This checkpoint does not construct S01 from actual evidence, admit or release
K02, authorize scientific executions, or release the campaign/global freeze.

## Generated validity

The guard validates the entire supplied frame against the supplied canonical
task before any analysis eligibility filtering. Existing task/output contracts
check shape, ordered columns, numeric finiteness/type, nonmissing fields and
unique identifiers. The added requirements correctly enforce nonblank IDs,
age at least 18, literal F/M, and strictly positive BMI/TC/HDL for every row.
No filter, repair, clipping, arbitrary positive floor, maximum, or TC/HDL
inequality was introduced. The literal sex codes do not establish their
biological legend.

Its report binds the supplied task and ordered values, reports the full count,
and explicitly denies task/execution authentication and scientific release.
The content hash intentionally excludes the DataFrame index and CSV encoding.
The caller must authenticate the approved production task with 5,000 rows:
this helper accepts smaller explicitly invented tasks and cannot independently
detect a caller who substituted a smaller task after filtering. This is a
documented integration responsibility, not an asserted completed safeguard.

## Analytic reference

The fit computes log-GM locations and
`sigma = (log(threshold) - log(HDL_GM)) / Phi_inverse(p)` from six explicitly
normalized source contexts. The inversion is correct for the declared
continuous unweighted lognormal completion scenario. It rejects invalid
identities, analytes, units, probabilities, zero/negative sigma and nonfinite
values. Percentages are not silently interpreted as proportions. Normalization
and authentic source commitments remain the caller's separate responsibility.

The function performs no sampling or optimizer work. It returns preserved
normalized constraints, locators, evidence IDs, derivations, parameter/input
hashes and explicit assumptions. The source-only input does not take target
relationships, target moments, fitted TC means or source regressions as
coefficients. Unidentified joint structure is completed by the stated
assumptions, rather than presented as observed biology.

Sampling uses distinct normal coordinates for BMI, HDL and internal non-HDL,
common HDL-derived log dispersion within each source stratum, independent
Uniform(18,80) age and TC=HDL+positive internal non-HDL. A source context fixes
its stratum; the target selects each of six ordered donor strata with equal
probability. The code implements random mixture counts, not forced balance.
Source male/female-to-M/F encoding remains an internal convention. The age
upper support and TC>HDL model restriction must never become measured-target
exclusions.

The sampler uses a local seeded RNG and returns the exact six canonical
columns in mmol/L. It fails on overflow, underflow to zero or floating-point
loss of positive non-HDL, without clipping, redraw or adaptation. Context,
row-count and seed validation is explicit; no source parser, file access,
clinical launcher or campaign ledger exists in this pure module. Provenance
hashes do not prove source authenticity or that caller-supplied parameters
were produced by the approved finite analytic job.

## Verification performed

Only the two new focused suites ran independently; no passed legacy suite was
repeated. Author and reviewer executions below are separate runs of the same
tests, not extra unique tests.

| Suite | Author result | Independent result |
|---|---|---|
| `test_generated_validity.py` | 38 passed, 0.57 s | 38 passed, 0.55 s |
| `test_statistical_reference.py` | 56 passed, 0.51 s | 56 passed, 0.50 s |

These are 94 distinct new tests. The checks include semantics/inversion,
provenance, immutability, controlled independent-coordinate and mixture
mechanisms, bounded small samples, invalid inputs, whole-release rejection
and no repair/redraw. They do not establish clinical fidelity, transport,
unidentified relationships or population precision.

The parent additionally authorized exactly one small composed interface check.
`INDEPENDENT_COMPOSED_CHECK.py` used only the reference test's invented
constraints and the validity test's artificial task, changed explicitly to
24 rows. It made one sample call with seed **20261102**, context
`target_turkana_adults`, then called the guard, the approved TC/HDL unit map,
and existing analysis with `role="generated"`. It read no actual Greiner
numbers or measured target table, wrote no CSV/row data, and created no frozen
candidate or isolated generator execution.

All 24 rows were valid and eligible; zero were filtered. ID, age, sex and BMI
were unchanged; both lipid conversions agreed exactly with independently
written scalar multiplication by 38.67. The analysis design had rank 4 and
all three estimands computed. QR/triangular-solve OLS and independently written
residual-correlation arithmetic differed from the analysis by:

| Quantity | Absolute discrepancy |
|---|---:|
| HDL-on-BMI coefficient | 3.68594044175552e-14 |
| TC-on-BMI coefficient | 9.414691248821327e-14 |
| Lipid residual correlation | 1.6653345369377348e-16 |

All were below the prewritten 1e-10 tolerance. No generated standard errors or
reference SD denominators were emitted. The report retains only commitments,
counts, discrepancies and scope statements; no individual values or clinical
performance claims. This check was not the earlier real isolated bridge smoke
and must not be counted as a clinical trial or a new isolated execution.

## Remaining integration boundary

Before clinical use, separately authenticate normalized evidence and its
percentage conversion, freeze the common source/target spec and generator,
review context/operator bindings, enforce the reserved source/target and
analytic-job ledgers across candidate versions, verify exact runtime/output
bindings, invoke the guard against the approved 5,000-row task, and preserve
all rows through conversion/analysis. Source feedback and target custody
remain separated. The prospective exposure amendment and independent K01
Wave-A gate remain effective; this review does not alter them.

No actual source fitting, clinical table, target read, new literature source,
STATE/export edit or global release was performed by this review. Existing
semantic v1 and old modules were not edited.

## Reviewed SHA256 commitments

| Artifact | SHA256 |
|---|---|
| `generated_validity.py` | `5548ed6be15383fa7d0c6af60f46519d815ebc5b2a5921adbb7ed21660378516` |
| `test_generated_validity.py` | `9289f06570efd8f0303f144f41703b7a37a211a3efa290220fca33dd6f199980` |
| `GENERATED_VALIDITY_README.md` | `55cbe1260f66a606975201411c37155719382568ef2c81fef16e648c2b77d284` |
| `statistical_reference.py` | `aea6a8953e3a7118123ea8bc39db3d16a0497945304efc259471c600de5dd78f` |
| `test_statistical_reference.py` | `2c01740a983c101a4140fdd51227a2997706caef61a7d8a6239e5da1b033fb32` |
| `STATISTICAL_REFERENCE_README.md` | `5151023e17b6dc0baec42a5bd2f4eb2278e39029d8c9720d750e295fab8a5ebc` |
| `INDEPENDENT_COMPOSED_CHECK.py` | `5315469a69c246feca7e0d6bd7ceddd0de036c91678329eea3cb0618ac865be4` |
| `INDEPENDENT_COMPOSED_RESULT.json` | `a804abcac4f09bfd46bab3e844b7e6b5c75b1eb8b4461e8f8dc0dc7128f65bc9` |

The composed result also binds the existing analysis, conversion adapter,
approved unit manifest and both unit contracts by file hashes. The independent
approval remains restricted to numerical unit representation.
