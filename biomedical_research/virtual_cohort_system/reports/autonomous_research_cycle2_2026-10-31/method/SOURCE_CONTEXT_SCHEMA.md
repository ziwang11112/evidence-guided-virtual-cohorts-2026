# Bounded source-context bridge, version 1

Decision: keep all existing harness modules unchanged. The bridge accepts frozen whole-cohort **program** candidates only. It never imports the submitted generator on the host and delegates execution to the existing inspected WSL/bubblewrap adapter. Scientific adequacy, authorship and Agent-wide isolation remain unverified.

The parent `model_spec.json` retains the existing schema. Its `parameters` must include `active_context` and `contexts`. Each entry in `contexts` has exactly `population`, `n_rows`, `columns`, and `inputs`; `inputs` is an object of Agent-declared aggregate descriptors. All context definitions, scientific parameters, provenance and assumptions remain identical in every child specification. The only permitted change is `parameters.active_context`. The selected descriptor supplies the child's population, row count and column supports. The parent selector must also match its own task descriptor. No global row-count rewrite is made.

Before parent freeze, add `source_context_plan.json`:

```json
{
  "schema_version": 1,
  "model_domain": {
    "columns": ["FULL EXISTING COLUMN SCHEMAS"],
    "assumption_ids": ["DECLARED ASSUMPTION ID"],
    "description": "Agent-declared common computational domain"
  },
  "contexts": [
    {
      "id": "source_a",
      "task_path": "source_contexts/source_a/task.json",
      "feedback_path": "source_contexts/source_a/whole_cohort_feedback.json"
    }
  ]
}
```

The paths identify exact predeclared auxiliary artifacts inside the frozen parent candidate. Source IDs must occur in `parameters.contexts`, be portable and case-insensitively unique, and differ from the parent selector. At most 16 source contexts and 1,000,000 rows per descriptor are admitted. The source task must equal the parent task except for population, row count and numeric column minimum/maximum. Column identity/order, categories, nullability, task ID, policy and budgets stay fixed. All descriptors and the parent must fit inside the common domain. Finite domain bounds require corresponding declared context bounds; absent domain bounds do not manufacture a finite domain.

Each feedback recipe is validated before preparation using the existing whole-cohort feedback metadata/operator validation. It must name the actual source population. Domain assumptions must be included in the recipe's population assumptions. Unsupported statistics use `not_computable`. No transformations, statistical fitting, or new scientific parameters are supplied by the bridge. Candidate CSV artifacts, observed inputs and the legacy auto-recomputed `source_check_report.json` are rejected; absence of patient records hidden in admitted evidence/specification still requires substantive review.

`prepare_source_contexts` writes a new destination, pre-execution intent, exact derived child bundles, and a preparation manifest. `verify_preparation` verifies parent freeze/plan, shared specification identity, source registry prefix, every copied candidate/source artifact, child task derivation and child freeze. `execute_source_contexts` runs each prepared child once under fixed seed/resource limits, then uses existing execution and whole-cohort feedback verification. `verify_source_contexts` recomputes the source feedback and outer report. Reports/IDs are append-only. Failures retain their artifacts; an invalid execution receipt can stop final report creation and never receives successful linkage.

All generated outputs live under the caller-selected new destination. For this implementation exercise that destination is under this `method` directory. CLI: `python run_source_contexts.py prepare|execute|verify --bundle PARENT --destination NEW_PATH [--candidate initial]`; prepare also accepts `--seed` and optional `--runtime` pointing to the existing trusted runtime JSON. The script must be run with the project available on Python's import path; it does not modify the Python environment or use a local execution fallback.
