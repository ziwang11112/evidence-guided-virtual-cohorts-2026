# Declared-law validity v1

`scientific_validity_v1.assess_law(manifest)` accepts a plain JSON-compatible Python
dictionary and returns a JSON-compatible report. It uses only the standard library.
It never executes the AST, submitted Python, `eval`, numerical sampling, network
requests, or patient data. This is an analytical checker for this grammar, not a
proof checker for arbitrary stochastic programs.

## Manifest

```json
{
  "schema_version": "scientific_validity_v1",
  "variables": {
    "x": {"op": "normal", "mean": 0, "sd": 1},
    "z": {"op": "gamma", "shape": 2, "scale": 0.4},
    "y": {"op": "exp", "input": {"op": "ref", "name": "z"}}
  },
  "independence": [["x", "z"]],
  "analyses": [
    {"id": "projection", "kind": "ols", "outcome": "y", "predictors": ["x"]},
    {"id": "correlation", "kind": "pearson", "variables": ["x", "y"]}
  ]
}
```

All four top-level fields are required. Variables and analyses must be nonempty.
IDs must be unique. Names and IDs are nonempty strings of at most 200 characters.
An OLS analysis has at least one predictor and refers to the usual finite-second-
moment population projection; inclusion of an intercept and actual design rank
are independent-review questions. A Pearson analysis has exactly two variables.
Cross moments exist when both second moments are finite by Cauchy–Schwarz.
No uncertainty procedure is certified by these checks.

## Expression grammar

Each supported node has exactly the keys shown. `E` denotes an expression. Numeric
parameters must be finite `int` or `float`, excluding bool; strings, NaN and
infinity are rejected. Parameter comparisons use exact rational arithmetic on
Python's shortest decimal representation (`Fraction(str(value))`). This convention
defines the declared decimal parameters, including gamma boundary comparisons;
an independent code review must account for any floating-point implementation
differences. Huge numeric values beyond finite float range are rejected.

| Node | Definition and restrictions |
|---|---|
| `{"op":"constant","value":v}` | Constant real value. |
| `{"op":"normal","mean":m,"sd":s}` | Normal law, `s >= 0`; zero denotes a point mass. |
| `{"op":"lognormal","log_mean":m,"log_sd":s}` | `exp(N(m,s²))`, `s >= 0`. These parameters are on the natural-log scale. |
| `{"op":"gamma","shape":k,"scale":theta}` | Shape/scale gamma, both strictly positive; scale is not rate. |
| `{"op":"uniform","lower":a,"upper":b}` | Uniform on the finite interval, `a <= b`; equality is a point mass. |
| `{"op":"bernoulli","p":p}` | Exactly 0 or 1 with `P(X=1)=p`, `0 <= p <= 1`. Endpoints are point masses. |
| `{"op":"discrete_uniform","lower":a,"upper":b}` | Equal probability on every integer from `a` through `b`, inclusive; finite integer-valued bounds and `a <= b`. This is not a rounded continuous uniform. |
| `{"op":"ref","name":"x"}` | The same random variable `x` every time; never a fresh independent draw. No cycles. |
| `{"op":"affine","input":E,"scale":a,"shift":b}` | `a*E+b`. |
| `{"op":"sum","terms":[E,...]}` | Sum of 1–64 expressions. |
| `{"op":"product","factors":[E,...]}` | Product of 1–64 expressions. Repeated factors can express integer powers. |
| `{"op":"exp","input":E}` | Natural exponential. Mathematical real-law operation, not a machine-overflow check. |
| `{"op":"clip","input":E,"lower":a,"upper":b}` | `min(max(E,a),b)`, `a <= b`. Clipping is not conditional truncation. Its scientific justification requires review. |
| `{"op":"mixture","components":[{"weight":w,"law":E},...]}` | 1–64 branches with nonnegative finite weights; at least one positive. Selection probabilities are exactly `w/sum(weights)`. All branch laws are unconditional and must contain no refs. |

Each named definition without refs is a **source block**. Any stochastic primitive
occurrences inside it have the stated marginals, with no assumed internal
independence. Distinct named source blocks are likewise not automatically
independent. A group in `independence` asserts mutual independence of the entire
random source blocks named in that group. Definitions containing refs cannot be
listed in a group. Transformations inherit their source dependencies. Groups
are not combined transitively; pairwise independence does not establish mutual
independence. Treating an aliased/ref-derived variable as an independent source is
invalid. The generator must agree with these declarations under independent review.

For a mixture, the law is the specified finite mixture of unconditional branch
laws. Branches do not reference external variables because conditioning and
selection dependence would require a richer declaration. Zero-weight branches
are structurally validated but have no effect on moments. Unknown operations in
active expressions are opaque and unresolved, including when enclosed in a
bounded transform; the checker does not assume an unknown operation is real
valued. Unknown operations in unused variables do not invalidate otherwise
supported analyses. Additional keys on supported nodes are malformed.

The JSON tree is limited to depth 64 and 12,000 items; each expanded expression
also has a maximum node depth of 64. An unsupported operation or analysis kind
is unresolved. A malformed declaration, invalid parameter domain, missing ref,
or cycle makes the entire manifest unresolved. A bool anywhere in a manifest is
rejected; this version has no boolean fields.

## Analytical rules and limits

- Normal, lognormal, gamma and bounded variables have finite positive integer
  absolute polynomial moments. Finite sums preserve this property. Hölder's
  inequality can prove product or exponential-sum integrability without
  independence by requiring stronger marginal moments.
- `exp(a*X+b)` with nondegenerate lognormal `X` has an infinite second moment
  for every `a > 0`. Nonpositive `a`, a degenerate lognormal, and explicitly
  bounded alternatives are handled separately. `exp(exp(normal))` is also caught.
- For gamma `X` with scale `theta`, the order-`p` moment of `exp(a*X+b)` is
  finite exactly when `p*a*theta < 1`; equality diverges. For OLS/Pearson `p=2`.
  Shape must be positive but does not alter this threshold.
- A finite mixture has the required finite moment exactly when every
  positive-weight component does; one proved divergent component proves failure.
- Explicit independent source blocks permit expectation factorization. Without
  it, divergent terms are not assumed to survive arbitrary cancellation or
  dependence. Same-sign sums, bounded-direction exponent terms, and one
  non-Lp term plus only Lp terms have supported noncancellation rules.
- Unknown compositions, such as general products inside an exponential, remain
  unresolved. There is no algebraic normalizer: even an identity such as `X-X`
  can remain unresolved when separate divergent terms appear. This is deliberate
  conservatism, not a claim that the identity has divergent moments.

Finite simulated output is never used as proof. Machine overflow, empirical
duplicates, population appropriateness, transport, evidence uptake, variances,
design rank and arbitrary Python correspondence are outside this module.

## Report and controller integration

The return object contains:

```json
{
  "schema_version": "scientific_validity_report_v1",
  "scope": "declared_law_only",
  "manifest_valid": true,
  "status": "unresolved",
  "errors": [],
  "analyses": [{
    "id": "correlation",
    "kind": "pearson",
    "status": "unresolved",
    "second_moment_status": "pass",
    "required_moments": [{
      "variable": "x",
      "order": 2,
      "status": "pass",
      "reason": "A supported mathematical argument."
    }],
    "independent_review_required": [
      "code_correspondence",
      "positive_variances",
      "uncertainty_procedure_conditions_if_used"
    ]
  }]
}
```

`second_moment_status` is `pass` only when every required moment is proved finite,
`fail` when at least one is proved infinite, otherwise `unresolved`. A `fail`
means failure of this declared finite-second-moment gate; it is not a theorem
that every conceivable regression functional is undefined. Each required variable
is reported once. OLS lists `nonsingular_predictor_moment_matrix` instead of
`positive_variances` among its independent-review requirements. Unsupported
analysis kinds also include a `reason` and have no checked moments.

Full per-analysis `status` and top-level `status` are `fail` when a required
moment fails, and otherwise `unresolved`. This standalone module **never issues
a full scientific pass**. A controller may accept the moment result only together
with independent, artifact-bound reviews of code/law correspondence and the
remaining analysis conditions. Author assertions do not satisfy these reviews.
No reviewer receipt is interpreted by this module, and a reviewer cannot
silently override an unresolved moment argument through this API.

Malformed declarations return `manifest_valid: false`, diagnostics in `errors`,
and unresolved analysis stubs wherever well-formed IDs/kinds can be recovered.
For valid declarations, `manifest_valid: true` denotes syntax/domain validity,
not scientific suitability. Reports contain no NaN or infinity.

Run only the new fixture suite with Python 3.12:

```powershell
& 'C:\Users\ziwan\AppData\Local\Programs\Python\Python312\python.exe' -m pytest -q test_scientific_validity_v1.py
```
