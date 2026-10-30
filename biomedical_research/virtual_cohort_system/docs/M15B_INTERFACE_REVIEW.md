# M15-B interface review: retrieval-enabled virtual data

30 October 2026. Code/document inspection only. No literature request, generation, target access, test execution or change to frozen artifacts occurred in this review.

**Conclusion: the existing harness already supports a literature-enabled Agent that submits a directly authored table. M15-A's retrieval ban was a task restriction, not a missing core capability. A new task configuration and builder prompt are sufficient to remove that restriction. Scientific exposure accounting and validation admission still need explicit experiment-level decisions.**

## Minimal existing configuration

Start a new bundle in its final absolute location. It needs a valid `task.json` and `registry.json`; an empty starting registry is exactly `{"artifacts": []}`. Do not alter or reuse the bound M15-A task/session.

`task.json` requires exactly `schema_version`, `task_id`, `mode`, `population`, `row_id`, `n_rows`, `columns`, `information_policy`, and `budget`. There is no task-level `route` field. Each column declares name, kind, unit, role, nullability and optional numeric bounds or category values. At least one generated column and one unique identifier are required.

The policy fragment below enables the existing retrieval actions. Empty exclusions are schema-valid and disable the adapter's cohort-alias screening. They do not by themselves establish target independence; a target-specific admission/exposure policy must be decided before initializing a validation task.

```json
{
  "information_policy": {
    "mode": "published_evidence",
    "excluded_cohorts": [],
    "allowed_tools": [
      "literature.search",
      "literature.fetch",
      "literature.list-supplements",
      "literature.fetch-supplement"
    ]
  },
  "budget": {
    "source_queries": 12,
    "source_downloads": 6,
    "revisions": 2
  }
}
```

This is an illustrative fragment, not an initialized task or approved scientific budget. Query/download counts include failed requests; fetching a new paper can require a metadata query. Supplements consume resources too, so six downloads do not necessarily mean six fully read studies. The controller should choose the budget before binding and preserve actual usage.

From the project root, with `PATH`, `QUERY`, `PMCID`, `VERSION`, and `SUPPLEMENT_ID` replaced by actual admitted task values:

```text
python -m cohort_harness.literature --bundle PATH init
python -m cohort_harness.literature --bundle PATH search --query QUERY --limit 10
python -m cohort_harness.literature --bundle PATH fetch --pmcid PMCID --version VERSION
python -m cohort_harness.literature --bundle PATH list-supplements --pmcid PMCID
python -m cohort_harness.literature --bundle PATH fetch-supplement --pmcid PMCID --supplement-id SUPPLEMENT_ID
```

Initialization binds task bytes and the absolute bundle path to one `gateway/session`. A changed task, moved bundle or altered configuration is rejected. Initial construction and later revisions share this session; do not create another session to replenish resources.

The Agent reads actual returned articles and constructs `evidence.json`, `model_spec.json`, `decision.md`, `checks.json`, plus exactly one `generated.csv` or `generator.py`. A direct CSV selects the direct-row route automatically. Existing validate/freeze/verify commands support it; execution copies and validates its bytes with `generator_executed: false`, rather than manufacturing values.

## What retrieval and registration actually provide

Search uses Europe PMC core metadata. Full-text fetch uses PMCID/version-linked PMC Open Access cloud XML and manifests. Actual accepted search, article and supplement artifacts are copied to `sources/gateway/` and appended to the registry with returned source IDs, paths and SHA-256 values. Article IDs are PMCIDs; search-only artifacts have separate metadata IDs. The Agent should use these exact references, not invent approval entries or treat an abstract search result as a full-paper review.

The gateway returns full accepted article text, not a per-statistic screened excerpt. Once read, previously hidden same-paper SDs or relationships are potential inputs. The new task should allow their use and classify resulting agreement as source consistency. It should not retain M15-A's same-paper SDs as unseen validation answers.

Exclusion aliases are normalized text screening supplied by the task. The implementation adds no special NHANES aliases by itself. Screening includes references and can reject an otherwise independent paper for merely mentioning an excluded cohort. It also cannot guarantee that every target-derived source is detected. This is a known admission limitation, not a reason to ban all literature. Review rejected-access cases at the controller level and record any new admission policy before a new task; do not silently bypass the fixed session.

Limits: 16 MiB per response, 30 seconds per HTTP request, search pages up to 10 records, 1,000,000 parsed table cells; supported supplement paths include text/HTML/CSV/TSV/XLSX. This is not a general PDF reader or arbitrary publisher browser. A paper can be publicly readable elsewhere yet unavailable through this adapter. Such access failure must not be reported as absence of scientific evidence.

## More rows and more variables under the current contracts

| Intended expansion | Supported mode and constraint |
|---|---|
| Generate 100 fictional people from reported summaries | `whole_cohort`, `n_rows: 100`; all scientific columns generated; no `observed.csv`. The number of source participants is not tied to output count. |
| Add one or several unmeasured indicators to existing people | `enrichment`; declare each new indicator as a generated column. Input contains only identifier/observed columns. Existing values, row order and row count must remain unchanged. |
| Fill missing measurements while retaining observed values | `completion`; generated columns may contain missing input cells; observed cells in those columns must remain exactly unchanged. |
| Turn 10 existing people into 100 rows while preserving the original 10 | Not supported by silently changing an enrichment output. Use separately specified whole-cohort generation for the additional fictional population, or design an explicit new mixed-origin contract later. |
| Add an indicator discovered after task initialization | Cannot mutate the task's bound column list in place. Propose a follow-on task, retaining evidence/session history and controller-level total usage; do not reset the scientific budget silently. |

Thus a small pilot should agree on a useful initial output schema before binding, while allowing the Agent to discover the necessary evidence and propose later variable extensions. The code does not require all variables to appear in a single source paper.

## Existing useful components and remaining work

- `analysis_evidence.json` already supports declared analytical uses, source links, context differences, assumptions, unresolved gaps and proposed retrieval actions. These are declarations; the adapter must actually execute the requested actions. The sidecar does not audit source correctness automatically.
- `source-checks` already computes declared statistics from bound submitted tables. For direct-row work, bind the actual submitted table used by each check and retain the source population/analysis definition. A syntactically valid operator does not certify scientific comparability or that a separate table shares the intended construction.
- Execution-backed source replay currently supports enrichment **programs**, not direct tables or arbitrary whole-cohort replay. Do not label a direct-table check as an execution-backed replay. A multi-source direct-table task may require separate source-context tables with explicit provenance; this is experiment work, not evidence that those populations are already reconstructed.
- Candidate freezes include evidence and specification files, and revisions preserve ancestors. The lifecycle enforces the revision-depth budget and allows a truthful retain decision. It does not itself schedule a complete scientific Agent or classify real-target exposure.
- The adapter logs accessed artifacts, but there is no automatic semantic inventory of every fact seen, no comprehensive cohort-overlap detector and no generic target-analysis evaluator. A task-level exposure ledger and scientific source review must distinguish source inputs, development references, locked target analyses and genuinely unused tests.
- Procedural file/tool rules are not a security sandbox for the builder. Generator-process isolation does not isolate the Agent's general tools. Use a fresh builder with a deliberately limited packet and tool contract, and describe the boundary honestly.

## Recommended smallest adjustment

Reuse the existing literature adapter, direct-row submission, evidence/specification contracts and freeze lifecycle. Replace the M15-A prompt with a new task that expressly permits gap-driven retrieval and using all relevant accepted source statistics. Define output variables and intended analyses before binding; record unresolved joint structure as assumptions. Freeze after retrieval/construction, then assess the fixed output under a separately admitted empirical validation protocol. No core framework rewrite is needed just to grant retrieval, and no further data generation is performed by this review.

Inspected implementation: `cohort_harness/contracts.py`, `literature.py`, `_vendor/literature_gateway.py`, `lifecycle.py`, `execution.py`, `__main__.py`, `analysis_evidence.py`, `source_checks.py`, source-replay mode checks, and the corresponding interface documents/tests.
