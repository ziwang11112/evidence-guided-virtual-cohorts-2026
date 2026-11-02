# Pure S01 analytic reference implementation

This module implements the separately reviewed reference design in
`../STATISTICAL_REFERENCE_AND_BUDGET_PROPOSAL.md`. It has no file I/O, source
parser, executable CLI, generator launcher, lifecycle adapter or approval helper.
No actual Greiner parameters or clinical table are included. Tests use small
invented inputs only. Actual S01 construction/execution remains unstarted.

```python
model = fit_reference(six_normalized_source_constraints)
frame = sample(model["parameters"], context_id, n_rows, seed)
```

`fit_reference` returns `parameters`, `provenance` and `model_assumptions`. It
performs exactly 24 log evaluations and six standard-normal inverse CDF
evaluations, with no optimizer or sampling. It preserves normalized inputs,
evidence IDs, locators, formulas and canonical JSON input/parameter hashes.
These are caller-supplied provenance commitments, not authenticated sources or
approval to fit a real packet. The caller must retain original source values,
their normalization derivations, packet/code hashes and the calculation attempt
receipt under the reviewed finite job budget.

The input is a list with exactly the six approved source context IDs; order is
normalized to the documented donor order. Each context record has exactly:

```text
context_id
bmi_geometric_mean
hdl_geometric_mean
non_hdl_geometric_mean
low_hdl_proportion
```

Each GM record has `evidence_id`, `locator`, `variable`, `statistic`, `unit` and
`value`. Its statistic is `geometric_mean`; variables are respectively `bmi`,
`hdl_cholesterol`, `non_hdl_cholesterol`; units are `kg/m^2`, `mmol/L`, `mmol/L`.
The evidence ID must be `{context_id}__{variable}__geometric_mean` and locator
nonempty. This binds declared context/analyte identity, not extraction truth.

The low-HDL record has `evidence_id`, `locator`, `variable`, `statistic`, `unit`,
`value`, `comparison`, `threshold` and `threshold_unit`. It must use
`{context_id}__hdl_cholesterol__low_prevalence`, variable `hdl_cholesterol`,
statistic `proportion`, unit `1`, comparison `lt` and threshold unit `mmol/L`.
`value` is an **already normalized probability**, strictly between 0 and 1 and
unequal to 0.5. The caller must explicitly record any original percentage /100
derivation; the function does not silently reinterpret percentages. GMs and
thresholds must be positive finite numeric values, without booleans or string
coercion. A zero/negative/nonfinite implied sigma fails.

The fitted theoretical marginals follow the reviewed unweighted lognormal
scenario. BMI and internal non-HDL use the HDL-derived log dispersion as an
explicit arbitrary completion assumption. Sampling uses separate independent
normal coordinates for BMI, HDL and internal non-HDL, and defines TC as their
positive lipid sum. Age is independent Uniform(18,80); target donor component
selection is a uniform integer draw over the six source strata. Sex is encoded
men→M/women→F internally; this does not authenticate a target biological code
legend. Source TC GMs and all age quantiles/regression records remain unfitted.

`sample` accepts one named source context or the exact request context
`target_turkana_adults`, 1–5,000 rows and an
unsigned 32-bit integer seed. It uses a local NumPy generator, preserving global
RNG state, and returns exactly `id, age, sex, bmi, total_cholesterol,
hdl_cholesterol`; numeric outputs remain in canonical units. Same parameters,
context, count, seed and NumPy runtime give reproducible output. IDs are unique
within the frame. No internal component column is delivered. The sample's
source-stratum/component counts are draws, not forced exact mixture counts.

Nonfinite values, underflow to nonpositive values or loss of the positive
non-HDL component through float addition raise an error. There is no clipping,
repair, filtration, favorable-cohort selection, parameter adaptation or retry.
The sampler never checks source goodness of fit to choose a result. Its TC>HDL
support is a model restriction, never a target eligibility rule. Ordinary
implementation details of NumPy's RNG are not extra scientific fits.

Callers must verify the actual frozen task, parameters, code, context/seed and
attempt allowance before scientific execution. This pure function cannot debit
campaign budgets or prove that supplied coefficients arose from the declared
source fitting. The production task still requires exactly 5,000 rows; small
counts exist solely for explicit software fixtures. The sibling generated-
validity adapter separately checks released output against its task.

The focused tests check inversion on invented pairs, provenance, no mutation,
separate noise-coordinate structure, the equal-mixture selection mechanism,
small-frame support/reproducibility, invalid metadata/numbers and fail-without-
redraw behavior. They do not estimate population correlations from large trials,
fit actual evidence, run an isolated generator or validate scientific transport.

```text
python -m pytest work/scaleup_2026-11-01/case_k02/implementation/test_statistical_reference.py -q -p no:cacheprovider
```
