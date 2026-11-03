# Support and selection declaration v1

This additive module checks metadata, exact affine interval arithmetic, and retained-frame counts. It does not import a generator, sample rows, fit published points, or establish the actual support of arbitrary code. The controller must bind independent scientific/code review separately. The same declaration and checks apply to initial, self-review and numerical-feedback versions.

## APIs

```python
assess_support_selection(
    declaration,
    *,
    required_contexts,       # release-owned list of context IDs
    required_checks,         # release-owned {context_id: [check, ...]}
    known_provenance,        # release-owned evidence/assumption/definition ID lists
    context_sets=None,       # optional task/spec/evidence/bridge context ID lists
) -> dict

check_retained_frame(
    frame,                  # retained pandas DataFrame or mapping of column sequences
    *, context_id, declaration, required_checks,
) -> dict
```

Both APIs are available by importing the sibling `support_selection_v1` module. There are no nonstandard dependencies. `assess_support_selection` returns `status: declaration_checks_pass` or `declaration_checks_fail`, `issues`, and per-check interval results. It **always** returns `law_support_verified: false`, `actual_code_law_support: independent_review_required`, and `source_point_fit_required: false`. A declaration pass alone cannot admit a candidate. The controller owns the independent-review hash and must bind that review to the actual candidate bytes, declaration, release checks and this implementation; the module does not accept a self-declared review hash as proof.

The release supplies all context IDs, required scientific/eligibility domains and native views; the module contains no clinical constants, distribution-family requirement, desired association or target tolerance. If `context_sets` is supplied, it must contain exactly `task`, `spec`, `evidence`, and `bridge`; each list must equal `required_contexts` as a set. Candidate contexts and required-check contexts must also equal that set exactly. Each context needs at least one required check. Required-check IDs must be unique within their context.

## Exact numbers, domains and provenance

An interval has exactly four fields:

```json
{"lower": "0", "upper": null, "lower_closed": false, "upper_closed": false}
```

Bounds are integers or exact decimal/rational strings, including scientific notation; binary floats are rejected. `null` is the unbounded endpoint, which must be open. Empty/reversed intervals are rejected; a closed singleton is allowed. All arithmetic uses `Fraction`, including negative affine scales and endpoint reversal. A finite endpoint may be open or closed. There is no clinical epsilon or invented finite upper bound. Numeric strings are limited to 256 characters and exponents to magnitude 10000 for metadata resource safety.

Every support, map, selection, transformation and derivation has a nonempty `provenance` array:

```json
[{"kind": "assumption", "id": "A_LAW"}]
```

`known_provenance` has exactly `evidence`, `assumption`, and `definition` arrays. The release/controller supplies admitted evidence IDs, candidate-model assumption IDs, and reviewed definition IDs. Unknown kinds/IDs and duplicate references fail. Membership authenticates a reference name, not the truth or adequacy of its content. An author's assumption is not promoted to published evidence.

## Candidate structure

The top level has exactly `schema_version: "support_selection_v1"` and `contexts`. Each context has exactly these five objects/arrays:

```json
{
  "final_supports": {
    "x": {
      "domain": {"lower": "0", "upper": null, "lower_closed": false, "upper_closed": false},
      "provenance": [{"kind": "assumption", "id": "A_LAW"}]
    }
  },
  "native_views": {},
  "selection": {
    "route": "direct_eligible_joint",
    "exclusion_implementation": "not_claimed",
    "conditioning_event": null,
    "description": "The final joint law is specified directly for eligible persons; its unknown dependence is assumed.",
    "provenance": [{"kind": "assumption", "id": "A_LAW"}]
  },
  "transformations": [],
  "derivations": []
}
```

`final_supports` describes final output quantities after the complete declared composition. A support interval is the author's claimed range, with endpoint attainability reflected by closure. If a conservative enclosure reaches outside a required domain, the declaration fails this sufficient check; it may be refined within the protocol's existing correction allowance. The arithmetic does not prove that the implemented law attains the whole interval or obeys it. Required mathematical moments, measurement meaning, category/integer constraints and predictor rank remain other gates.

A native view has exactly:

```json
{"kind": "affine", "variable": "x", "scale": "1/2", "shift": "-5",
 "provenance": [{"kind": "definition", "id": "D_SCALE"}]}
```

Only affine maps from declared final variables are supported; map chains and unknown/nonlinear mappings are not silently approximated. Each release-owned check has exactly `id`, `variable`, `domain`, and optionally the paired fields `native_view` and `native_mapping`. If either native field is present, both are required. `native_mapping` has exactly `kind: "affine"`, `variable`, `scale`, and `shift`; its provenance belongs to the release contract, while the authored view retains its separate provenance references. Both base-variable names must equal the check variable. The authored scale and shift must equal the release-owned values exactly as `Fraction` numbers before mapping support or accessing retained rows. Rational-equivalent spellings are accepted; a substituted constant map, wrong sign, scale or offset fails even if its output falls inside the required domain.

For example, a generic native-domain requirement is `{ "id": "native_positive", "variable": "x", "native_view": "native", "native_mapping": {"kind":"affine", "variable":"x", "scale":"1/2", "shift":"-5"}, "domain": {"lower":"0", "upper":null, "lower_closed":false, "upper_closed":false} }`. The release/controller must bind these mapping values to the map used by the scientific source/target operator; a view name alone is not semantic identity. The image of declared final support must be a subset of the required domain. Missing, unsupported or mismatched required maps fail.

## Selection and transformation semantics

`selection.route` is one of:

- `direct_eligible_joint`: a joint law is specified for the eligible population. `exclusion_implementation` is `not_claimed`; `conditioning_event` is null. This does not require a parent population, selection prevalence or reconstructed individuals.
- `conditional_joint`: an assumed parent joint law is conditioned on an event. `exclusion_implementation` is `joint_conditioning`; `conditioning_event` is `{ "description": "...", "stage": 0 }`. Independent review must establish positive event probability, correct joint conditioning, scale/stage semantics and a bounded execution policy. Literal rejection sampling is not required.
- `transformed_variable_model`: an observation/processing model is declared. `exclusion_implementation` is `not_claimed`, `conditioning_event` is null, and at least one transformation is required. Its suitability for a source population is independently reviewed.

No route can claim clipping as the implementation of exclusion. That prohibition concerns population semantics, not a function name: an explicitly assumed atom-containing eligible law can contain a clipping construction. It must disclose the atom and changed functional and must not claim to recover a parent population's selection process.

A transformation has exactly:

```json
{"id":"tr1", "kind":"clip", "variable":"x", "stage":1,
 "role":"law_construction", "atom_effect":"possible",
 "description":"Explicit distributional construction; not simulated exclusion.",
 "provenance":[{"kind":"assumption", "id":"A_LAW"}]}
```

IDs are unique, the variable names a final output support, and stages are nonnegative integers. `kind` is `clip`, `winsorize`, `round`, `censor`, `affine`, or `other`; `role` is `law_construction`, `measurement`, or `processing`; `atom_effect` is `none`, `possible`, `creates`, or `unknown`. Descriptions must identify actual affected variables, precursor meaning and consequences; independent review checks completeness and truth. An atom declaration is not proof of its size or presence. Setting a transform's role to eligibility exclusion is rejected.

## Derivation claims

A derivation has exactly:

```json
{"id":"d1", "claim":"approximation", "applicable_stage":0,
 "transform_effects":{"tr1":"invalidated"},
 "description":"The precursor identity supplies an approximate starting parameter.",
 "provenance":[{"kind":"assumption", "id":"A_LAW"}]}
```

`claim` is `exact_final_law`, `approximation`, or `initialization`. IDs are unique. `transform_effects` can reference only known transforms with stage strictly greater than `applicable_stage`; its values are `preserved`, `invalidated`, or `unresolved`. An exact-final-law claim must cover **every** subsequent transform and declare each preserved. Invalidated, unresolved or omitted effects fail that claim. Approximation/initialization may honestly disclose invalidation or uncertainty. Numerical agreement with published points is not an admission requirement, and a declared preserved identity still needs independent mathematical review.

## Runtime reporting and limits

Call `check_retained_frame` after successful declaration assessment and binding. It evaluates every declared final-output support and every release-owned domain check against retained values and the exact native map, reporting `total_rows`, `invalid_or_nonfinite`, `outside_required_domain`, and `within_required_domain`. Rows in `checks` have `check_role: declared_final_support` (IDs prefixed `declared_support:`) or `check_role: required_domain`. Missing columns, unequal column lengths, invalid values, empty inputs and domain violations cannot pass. Malformed required-check metadata raises `DeclarationError`; the controller must retain that failure, not skip the check. The function does not alter/filter the frame, return replacement rows, or regenerate a table. Floating values are evaluated through their stored decimal spelling; no claim is made about pre-rounding values.

These row counts complement analytical support review and cannot establish population support or recover unobserved exclusions. They must not be returned as numerical source-fit feedback to the no-feedback branch. Apply the frozen failure policy equally to all candidate versions. Source-point discrepancies are reported by the existing authenticated operators, separately from this admission gate.

## Bounded verification

From this directory run `python -m unittest test_support_selection_v1.py`. The tests use metadata and small artificial scalar arrays only: exact native-map failure and repair, counterfeit constant/sign/scale/offset rejection before retained-row access, rational-equivalent map identity, endpoint closure, negative scale, selection/clipping semantics, derivation claims, provenance/context omissions and nonmutating counts. They do not import candidate code, simulate a cohort, read patient/target artifacts, or run the existing broad test suite.
