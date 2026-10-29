# Declared analytical uses and evidence gaps

An optional `candidates/<name>/analysis_evidence.json` records the analytical uses a builder intends, their links to admitted evidence, declared context differences, assumptions, unresolved gaps, and proposed retrieval actions. This is a strict version-1 declaration contract. It performs no retrieval, generator execution, row analysis, scientific scoring, or target evaluation.

The sidecar is checked by both `python -m cohort_harness validate` and direct/CLI candidate freezing. Candidate freezing already commits every file, including this sidecar. Changing or removing it after freezing invalidates verification. It is a submission declaration and cannot substitute for an auxiliary check-result artifact in `checks.json`. Candidates without the sidecar retain their previous behavior. No existing task file needs to change.

## API

```python
from cohort_harness.analysis_evidence import (
    validate_analysis_evidence,
    summarize_analysis_evidence,
)

validate_analysis_evidence(manifest, task, evidence, model_spec)  # None or ContractError
report = summarize_analysis_evidence(manifest, task, evidence, model_spec)
```

Both APIs validate the existing evidence and model-specification contracts, including declared excluded cohorts. Evidence references must be real item IDs; source IDs and assumption IDs must resolve. The pure API has no registry or filesystem input and does not independently admit evidence. Existing candidate freezing continues to check registered source artifacts and their hashes. Load saved JSON with `cohort_harness.lifecycle.read_json` to reject duplicate keys and nonfinite JSON values.

The returned summary is deterministic and labelled `scope: "declarations_and_references_only"`, `contract: "structurally_valid"`, and `assessment_origin: "submitter_declaration"`. Scientific validity, joint-distribution identification, and uncertainty calibration remain `"not_assessed"`. The report lists unresolved gaps, referenced assumptions, action IDs, shared declared cohorts, and sources with unknown cohort IDs. It has no confidence score or count of independent confirmations. It is derived output, not an execution receipt or approval record.

## Schema

Every object rejects unknown keys. All IDs, descriptions and rationales are nonempty strings. IDs are unique within their containing list; every reference list is duplicate-free. `analyses` is nonempty. All listed fields are required except the statistic-specific estimand fields below.

| Object | Fields |
|---|---|
| Manifest | `schema_version: 1`, `analyses` |
| Analysis | `id`, `estimand`, `assessment`, `rationale`, `assumption_ids`, `evidence_links`, `gaps`, `actions` |
| Estimand | `description`, `kind`, `outcome`, `exposures`, `conditioning`, `adjustment`, `scale`, `unit`, `population`, `measurement`, `selection` |
| Evidence link | `evidence_id`, `relation`, `comparisons`, `assumption_ids`, `rationale` |
| Unresolved gap | `id`, `dimension`, `description`, `consequence`, `assumption_ids` |
| Retrieval action | `id`, `gap_ids`, `tool`, `request`, `status`, `reason` |

Outcome, exposures, conditioning and adjustment name non-identifier task columns. The latter three are lists. The outcome cannot be a predictor/conditioner, and focal exposures and adjustment covariates are distinct. Pearson/Spearman correlation and OLS-coefficient requests require one focal exposure; mean/SD/median/quantile/proportion requests have none. Conditioning declares variables on which the requested use depends; adjustment declares the analytic adjustment set. Explain selection and conditioning values in the description/selection strings; this contract does not implement a target estimator.

Supported `kind` values are `mean`, `sd`, `median`, `quantile`, `correlation` (Pearson), `spearman_correlation`, `ols_coefficient`, `proportion`, and `reported_other`. `reported_other` requires `statistic_name` and can describe an interaction, nonlinear effect, causal estimand, or joint-distribution functional without pretending an operator exists. Median/quantile requests require `method: "linear"` or `"not_reported"`; quantile also requires finite `q` in `[0, 1]`. Those fields are forbidden for unrelated kinds. Scale describes the intended scientific interpretation; `unit` is its declared unit label.

`relation` is `direct_estimand` or `component`. A direct-estimand link must reference the same statistic kind and explicit definition (`statistic_name`, `q`, `method`). A source mean's SD/SE uncertainty cannot serve as an SD evidence estimate; Pearson cannot be renamed Spearman; two different quantiles cannot be interchanged. Component links may describe partial information for another requested statistic.

`comparisons` has exactly seven keys: `estimand`, `population`, `measurement`, `selection`, `conditioning`, `adjustment`, and `scale`. Every value is `declared_match`, `declared_difference`, or `unknown`. These are author declarations. A declared estimand match additionally requires equal kind/definition and the same outcome-plus-exposure variable set; a declared adjustment match requires equal adjustment lists as sets; a declared scale match requires equal unit labels. Those checks do not establish semantic equivalence or directed outcome/exposure roles. If an adjustment set was not reported, use `unknown`; an empty adjustment list is not evidence that adjustment is known to be absent.

Gap `dimension` is one of those seven comparison dimensions, `joint_distribution`, `interaction`, `uncertainty`, or `other`. Each declared difference/unknown needs a corresponding gap. An estimand difference can instead be represented by a joint-distribution or interaction gap. Every gap remains unresolved even when the builder names an assumption allowing a model to proceed. Each gap must be addressed by at least one planned or unavailable action. Gap and link assumption IDs must also appear in the containing analysis's `assumption_ids`, which must exist in `model_spec.json`.

| Declared assessment | Structural requirements |
|---|---|
| `directly_reported` | At least one direct-estimand link; all links are direct; all comparisons declared matches; no declared gaps or assumptions. This describes the source evidence declaration, not the generator's validity. |
| `transported` | At least one direct-estimand link; at least one difference/unknown on those links; explicit analysis assumptions and bridge assumptions on every direct link; unresolved gaps/actions retained. |
| `partial` | At least one evidence link and at least one unresolved gap with an action. |
| `unassessed` | No claimed evidence links; at least one explicit unresolved gap with an action. Useful for unsupported or prior-only uses. |

Actions are plans only. `status` is `planned` or `unavailable`; `completed` and other claims of execution are rejected. `tool` is `literature.search`, `literature.fetch`, `literature.list-supplements`, `literature.fetch-supplement`, or `none`. A planned action requires the literal task permission, published-evidence mode and a nonzero corresponding task budget. `none` requires unavailable status. `request` states the concrete query or identifier and needed information; `reason` explains why it could resolve the linked gaps or why it is unavailable. These strings are never executed as code or commands.

The manifest does not know remaining adapter usage or reserve budget. A planned action must later use the existing task-bound literature session, actual remaining budgets and approval registry; it must not reset a session or alter the task. A fetch may also consume query budget. An unavailable action can name a currently forbidden tool to explain the missing capability, without granting permission to invoke it.

## Example: declared transport with an unresolved population gap

This is a schema illustration. `E1`, `A1`, and column `y` must exist in the actual candidate contracts; the strings below do not constitute evidence or source approval.

```json
{
  "schema_version": 1,
  "analyses": [{
    "id": "mean_y",
    "estimand": {
      "description": "Arithmetic mean of y in the intended target population",
      "kind": "mean",
      "outcome": "y",
      "exposures": [],
      "conditioning": [],
      "adjustment": [],
      "scale": "Arithmetic mean on the original measurement scale",
      "unit": "y_unit",
      "population": "Explicit description of the intended target population",
      "measurement": "Explicit description of how y is measured",
      "selection": "All members satisfying the stated target eligibility"
    },
    "assessment": "transported",
    "rationale": "The source reports the mean, but population transfer remains an assumption.",
    "assumption_ids": ["A1"],
    "evidence_links": [{
      "evidence_id": "E1",
      "relation": "direct_estimand",
      "comparisons": {
        "estimand": "declared_match",
        "population": "declared_difference",
        "measurement": "declared_match",
        "selection": "declared_match",
        "conditioning": "declared_match",
        "adjustment": "declared_match",
        "scale": "declared_match"
      },
      "assumption_ids": ["A1"],
      "rationale": "The builder declares measurement and analytic correspondence; A1 describes population transfer."
    }],
    "gaps": [{
      "id": "G_population",
      "dimension": "population",
      "description": "No mean from the intended population is available.",
      "consequence": "The target mean depends on the unverified transfer assumption.",
      "assumption_ids": ["A1"]
    }],
    "actions": [{
      "id": "R_population",
      "gap_ids": ["G_population"],
      "tool": "none",
      "request": "Seek a source reporting the mean of y in the intended population with the stated measurement.",
      "status": "unavailable",
      "reason": "No retrieval action is currently permitted in this illustrative task."
    }]
  }]
}
```

## Scope and source replay

The requested-use list lives in this optional candidate sidecar. The harness cannot detect an intended user analysis omitted from that list, infer all generator dependencies, or prove that declared comparisons and assumptions are exhaustive or true. Existing evidence records do not encode directed OLS variable roles or a complete conditional/joint law. Review those meanings against approved source artifacts; do not infer them from matching variable sets or strings.

Source replay copies all frozen candidate artifacts unchanged and changes the derived task's population and row count. The sidecar continues to describe the original intended analytical uses. It is not rebound to the source context, and it contains no full task hash or requirement that its population string equal the current execution task's population. The existing freeze/replay commitments protect its bytes. A successful source replay, a zero source-statistic discrepancy, and repeated generator seeds do not remove any declared gap or upgrade an assessment.

In particular, marginal summaries and pairwise correlations do not by themselves identify the joint distribution, interactions, nonlinear functionals, conditional effects or transport assumptions required by another use. More rows, papers from the same cohort, or seeds do not create independent clinical evidence. The summary reports known overlapping cohort IDs and unknown cohort identities without turning them into precision or confidence.

The tests use invented declarations and mocked replay execution. They check reference and role/set constraints, rejected statistic/uncertainty substitutions, contradictory coverage, strict JSON, registry enforcement during freeze, freeze immutability, action permissions, absence compatibility and unchanged replay copying. They do not validate biomedical conclusions or establish isolation.
