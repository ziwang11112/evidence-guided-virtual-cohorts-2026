# Task-bound literature adapter

Implemented 28 October 2026 as an M2 component. It reuses the earlier HDL gateway without changing that experiment. It does not itself launch an Agent, execute a generator, or provide an OS sandbox.

## Public entry points

```python
from cohort_harness.literature import run_literature

result = run_literature(bundle, "init")
result = run_literature(bundle, "search", query="your research query", limit=10, cursor="*")
result = run_literature(bundle, "fetch", pmcid="PMC123", version=None)
result = run_literature(bundle, "list-supplements", pmcid="PMC123")
result = run_literature(bundle, "fetch-supplement", pmcid="PMC123", supplement_id="returned-id")
```

`PMC123` and `returned-id` above are placeholders, not evidence recommendations. Returns a typed dictionary, including categorized errors. It does not print a traceback or rejected source content. Multiple source versions return `selection_required`, which is not an approved article and does not register source bytes.

Equivalent CLI from the system project directory:

```text
python -m cohort_harness.literature --bundle PATH init
python -m cohort_harness.literature --bundle PATH search --query "your research query" --limit 10
python -m cohort_harness.literature --bundle PATH fetch --pmcid PMC123
python -m cohort_harness.literature --bundle PATH list-supplements --pmcid PMC123
python -m cohort_harness.literature --bundle PATH fetch-supplement --pmcid PMC123 --supplement-id returned-id
```

## Task requirements and fixed session

The bundle must already have a valid `task.json` and `registry.json`. The registry may be empty. The adapter never resets or replaces a malformed registry to hide earlier sources.

- Information mode must be `published_evidence`. `prior_only` forbids initialization and retrieval.
- `allowed_tools` must contain the exact invoked tool name: `literature.search`, `literature.fetch`, `literature.list-supplements`, or `literature.fetch-supplement`.
- A permitted fetch can internally perform its required screened metadata lookup, charged to the query budget. It is not a free query or a silent retry.
- Query and download caps are exactly `task.budget.source_queries` and `source_downloads`. Auxiliary requests have a separate finite cap of `8 × (queries + downloads)` for version/manifest discovery. HTTP attempts and elapsed times are also returned.
- The task's `excluded_cohorts` strings are used as normalized text aliases. No task-specific population aliases or regular expressions are silently added. Curators should supply all known aliases before binding the task. An empty list means no cohort exclusions.
- One bundle uses one fixed `gateway/session` across initial construction and revision. The task bytes and absolute bundle location are bound on initialization. Changing the task, moving the bundle, or altering the generated configuration is rejected; such a change requires a separately declared new task rather than silently resetting a budget.

```text
bundle/
  task.json
  registry.json
  gateway/
    binding.json
    config.json
    session/
      state.json
      audit.jsonl
      approved/
  sources/gateway/<content-hash>.<extension>
```

Limits currently fixed by the adapter: 16 MiB response bytes, 30 seconds per HTTP request, search pages up to 10 records and 1,000,000 parsed table cells. The reused gateway supports its existing JATS/XML, text, strict HTML, CSV/TSV and XLSX paths; it is not a general PDF/document reader.

## Registration and provenance

Only artifacts returned by actual gateway actions are eligible for registration. A file placed under `approved/` does not become evidence. The adapter verifies the content-derived path, bytes, SHA-256 and an `artifact_approved` event with this configuration. Article and supplement registration additionally checks the parent state, XML/manifest relationship and source-linked supplement identity.

Article XML, extracted text and manifest are copied under `sources/gateway/` with `source_id` equal to the PMCID. Supplement bytes use the same PMCID. Search outputs use a separate `search-<hash>` source ID and remain metadata, not a claim that the full paper was read. Returned `registered_artifacts` contain the exact IDs, paths and hashes to use when preparing an evidence object. The adapter does not invent population descriptions, measurement mappings, numerical statistics or applicability judgments for the Agent.

Registration appends to the existing registry without changing previous entries. Repeated cached fetches do not duplicate entries or consume another download. Old frozen candidates remain valid because their receipts bind the earlier registry prefix. Cached artifacts are rechecked; corrupted bytes or missing approval events stop the return of source content.

Failed or rejected HTTP attempts count against their budget. There are no hidden retries. Rejected text is not returned or saved; logs retain categories and opaque hashes. The complete result and session state expose actual usage, including successful requests, attempts and elapsed time. The adapter records its invocation in the session audit.

## Limits and verification

These checks establish consistent procedural provenance, not authenticity against a malicious local writer. The task, session state, approval log, registry and adapter deployment are trusted inputs. An external caller with filesystem access can bypass a procedural tool or tamper with all records; real isolation requires a separate execution/tool boundary. Exclusion aliases are conservative and incomplete and may also reject independent articles that mention an excluded cohort in references.

The adapter does not claim scientific source applicability, absence of all target-derived information, calibrated uncertainty, or improved generated data. Independent source-context generation and scientific evaluation are separate components.

`tests/test_literature_adapter.py` uses intercepted HTTP and invented records only. It checks task/tool permissions, budget exhaustion and failed-request accounting, opaque exclusions, configuration/task tampering, cached-artifact and approval tampering, supplement linkage, registration idempotence, and continued validity of an older frozen candidate after source additions. No patient-level data or real publication retrieval is needed for these tests.
