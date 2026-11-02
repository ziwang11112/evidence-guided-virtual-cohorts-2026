# Pure K01 statistical reference component

`statistical_reference.py` implements the reviewed S01 formulas in
`../STATISTICAL_REFERENCE_AND_BUDGET_PROPOSAL.md`. It performs no file access,
evidence admission, clinical release, target lookup, execution dispatch or
budget-ledger mutation. No actual source values have been fitted in this unit.

## API and normalized inputs

`fit_reference(normalized_source_constraints)` accepts exactly 18 records and
returns `parameters`, `provenance` and `model_assumptions`. The IDs are the seven
selected MIND and eleven selected Ayele IDs listed in the proposal JSON. Input
order is irrelevant. Wrong/duplicate IDs, contexts, analytes, units, statistics,
groups, extra fields and invalid numerical domains fail. Inputs are not mutated.

Every record contains `evidence_id`, `context_id`, `variable`, `statistic`, `unit`
and a nonempty `locator`. Moment records add `value`; their statistic is
`arithmetic_mean` or `individual_standard_deviation`. Count records use statistic
`count_ratio`, unit `1`, and add `group`, integer `numerator` and `denominator`.
Ayele count records also retain `reported_percentage` as unfitted metadata.
The three Ayele category sets must exhaust the same declared denominator.

Normalization is an explicit, bound preparation step. It must retain the original
record, locator and source hash; map source FSG to canonical `glucose` without
discarding its serum/fasting context; and document the original `≥25` to normalized
ASCII `>=25` group spelling. The component does not infer or authenticate that
mapping. It uses the provided integer count divisions, not rounded percentages.
Retained printed percentages are not independently authenticated or reconciled
with counts. Age printed labels retain en dashes; the separate diagnostic
interpretation uses the reviewed completed-year half-open scenario. The BMI
middle diagnostic remains closed at24.9, not silently extended to25.

`prepare_reference_inputs.py` now supplies that bounded preparation. Its pure
bytes-in function checks the caller-pinned request-manifest hash, exact selected
evidence/diagnostic file bytes, each original-record hash, source/context/analyte
identity, units and the fixed diagnostic operators. It copies the 18 records,
preserving integer count operands without division; it calls only the input
shape/count validator, never `fit_reference` or `sample`. The explicit CLI reads
only the three named request metadata files and exclusively creates the view.
The other manifest files remain subject to the separately reviewed full packet.

The actual metadata-only preparation succeeded once and created
`../REFERENCE_INPUT_VIEW.json`, SHA256
`16f54e233035739144b7ca2f53718a9ab86ea857cfe8e5b992d95f929a5d839a`.
It binds manifest
`3b45d796ebcbff18f1a67abdbffdd441eb583a17e3ac5d94e0458fe8a3a6087b`
and the actual source/diagnostic bytes. This unactivated view contains source
inputs, not fitted parameters or generated rows. It has not been passed to the
fit or draw function. Hash verification is not an approval signature.

The fit result preserves canonicalized input records, their digest, a parameter
digest, formulas and unfitted-item IDs. Those hashes bind caller-supplied content;
they are not proof of source authenticity or an executed run. The caller still
must bind the reviewed source bytes, normalization, task, scientific candidate
and actual execution. All source SDs remain population-moment approximations
with unknown original divisor/weights.

`sample(parameters, context_id, n_rows, seed)` returns exactly the ordered columns
`id, age, sex, bmi, glucose`. Context IDs are:

- `source_mind_china_2019`: source age support61–80.
- `source_ayele_dire_dawa_2017`: methods support25–64; caption discrepancy remains.
- `target_haalsi_pooled_poc`: equal donor mixture with age>=40 conditioning within
  each selected donor, before retaining donor weights1/2.

The canonical units are year, kg/m² and mmol/L, with `F`/`M` for Female/Male. The
reference's age support ends at80, but the target eligibility contract has no
upper age cutoff. Context eligibility is not placed into shared column bounds.
The root-owned `validate_generated_context` must validate the full frame against
the authenticated context/task; it neither filters nor repairs rows.

The pure function accepts1–5000 rows so invented tests can be small. A production
caller must bind the actual approved5000-row task, scheduled seed and finite
attempt ledger. This function accepting a context name is not authorization to
run it. NumPy/SciPy/pandas supply standard draws, inverse beta CDF and DataFrame
construction. The sampler has no optimizer, fitting loop, cohort retry,
diagnostic-based selection, clipping or parameter adaptation. Invalid/nonfinite
results fail; the caller must not silently resample them.

Glucose uses one independent MIND-derived marginal in every context. Its copied
law is an unsupported measurement/population transport assumption. Population
null contrasts follow from S01 independence; no finite table is orthogonalized
to force them, and Agents receive no such coefficient requirement. The intended
source-feedback action is precommitted retention, implemented by the controller,
not by this pure module.

## Invented verification

From the project root:

```text
python -m pytest work/scaleup_2026-11-01/case_k01/implementation/test_statistical_reference.py -q
```

The author run passed **54 tests in0.67s**, first attempt. All source moments and
counts in `invented_records()` are invented, despite using the required schema
slot IDs. No evidence file, participant file, clinical table or generated CSV is
read or written. Draw fixtures contain at most24 rows.

Checks reconstruct the implied beta and lognormal moments and outer-bin
probabilities analytically; verify that printed rounding/unfitted age counts do
not alter fitted parameters; preserve the24.9 gap; test exact fixed-noise sampling
structure and conditional-CDF arithmetic without a large Monte Carlo test; and
check deterministic seeds, distinct draws, input immutability, invalid domains,
context/metadata mismatches and failure without redraw. No old guard or analysis
suite was rerun by this author unit.

The independent reviewer subsequently completed that one invented composed check:
24 rows in each of the two source contexts and target, seed20261102, with all
guards passing. Eighteen source diagnostics matched independent arithmetic
within2.23e-16; target OLS/HC3 matched a raw-coordinate QR calculation within
1.81e-15. No rows or clinical candidate were retained.

The added `test_prepare_reference_inputs.py` passed **11 tests in0.62s**, first
attempt, on invented packet bytes. It verifies integer/glyph normalization,
absence of fitting/sampling calls, source-byte/original-record integrity, exact
source/context identity, moments/units, count mapping and the literal BMI
boundary. The earlier 54-test component suite was not rerun. No failed test or
actual-source fitting attempt occurred in this unit.
