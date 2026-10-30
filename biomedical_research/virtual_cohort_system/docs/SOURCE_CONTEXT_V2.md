# Independent source contexts (M12-A)

Implemented scope: enrichment generators, identical ordered variable identities and units, identity measurement mapping. This extends source-task support without changing any historical harness module.

`cohort_harness.source_context.compile_source_task(target_task, context, model_domain, source_frame, assumption_ids=...)` compiles a validated v1 execution task. Only population, row count and column support definitions change. Source and target declared supports must both fit the model's declared computational domain. A finite domain requires explicit finite input support on that side; known rows inside a range cannot justify an undeclared unbounded support.

The domain is declared and traceable to assumptions, not learned or empirically certified. Source rows are neither clipped nor filtered to make them pass. Generated-output ranges are source-specific and also constrained by the model domain.

## Plan

Place `source_replay_v2.json` inside the candidate before its ordinary freeze:

```json
{
  "schema_version": 2,
  "model_domain": {
    "description": "Declared computational support",
    "columns": ["full v1 column-schema objects, including generated columns"],
    "assumption_ids": ["A1"]
  },
  "contexts": [
    {
      "id": "source_one",
      "population": "Source eligibility description",
      "reason": "Reason for this source approximation",
      "columns": ["independent full v1 source column-schema objects"],
      "assumption_ids": ["A1"],
      "measurement": {"mode": "identity", "description": "Explicit same-scale assumption"},
      "input": {"path": "source_covariates.csv", "sha256": "actual SHA256", "origin": "declared_source_covariates"},
      "checks": ["existing source replay check objects"]
    }
  ]
}
```

This schematic contains placeholders; see `examples/m12_source_domain.py` for a runnable invented fixture. Every model-domain assumption is also listed in each context so its approximate-check status propagates to the output. Context IDs must be unique ignoring case. CSV parsing uses source category types, not target category types.

Source input contains exactly identifier and observed columns in task order; no generated outcomes or extra covariates. Source and model schemas preserve names, types, roles, units and nullability. Numerical support and category sets can differ. Additional adjustment variables, unit conversions, assay bridges, arbitrary source selection programs and other generation modes are not implemented by this version.

## Execute and verify

From the project root, after preparing and freezing a normal bundle:

```powershell
python -m cohort_harness.source_replay_v2 run --bundle PATH --candidate candidates/initial --replay-id NEW_ID --seed 12001 --runtime work/m2-runtime-config.json
python -m cohort_harness.source_replay_v2 verify --bundle PATH --candidate candidates/initial --replay-id NEW_ID
```

Source replay runs under `source_replays_v2/NEW_ID/`; existing `source_replays/` and all original module files remain unchanged. Each child is a complete frozen bundle using the same candidate bytes, source covariate bytes and approved source registry snapshot. The existing isolated execution adapter enforces source input/output contracts. There is no direct host execution fallback.

The verifier binds parent, source task, child candidate, execution outputs, intent and engine versions, and recomputes statistics. It does not certify source-population reconstruction or measurement compatibility. A constant correlation or rank-deficient regression may be recorded as not computable even if the generator executed successfully. Failed executions have no verified source statistics.

Operator structure is checked on empty typed data before any execution; those checks calculate no scientific result. Runtime exceptions and partial artifacts remain visible. This is not yet a resumable campaign controller or a globally budgeted calibration session.

## Reproduce the engineering example

```powershell
python -m examples.m12_source_domain --destination work/NEW_INVENTED_DEMO --runtime work/m2-runtime-config.json
```

The destination must not exist. The example has target x in 0–6, source x in 7–10, and a declared model domain covering both. The invented generator is y = 1 + 2x. It tests source mean 18 and slope 2, old-path rejection, new isolated execution and unchanged target eligibility. This example has no patient data and cannot demonstrate biomedical utility.

For Windows pytest runs, use a fresh short workspace `--basetemp`; long nested replay paths can exceed Windows path limits. Create its parent first, and never use a directory containing existing data as pytest-managed scratch.
