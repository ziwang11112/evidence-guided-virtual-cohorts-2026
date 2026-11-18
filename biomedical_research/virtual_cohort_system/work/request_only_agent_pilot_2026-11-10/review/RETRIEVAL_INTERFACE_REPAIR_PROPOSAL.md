# Minimal mechanical repair for the request-only retrieval interface

This is a post-terminal engineering recommendation for the two completed PNS episodes. It does not change this round, scientific policy, evidence exclusions, cases, clinical references or generation requirements. Lipid episodes are still running when this note is prepared.

## Observed failure and attribution

Both PNS episodes terminated at the 250,000-byte request ceiling before submitting a candidate. Ordinary made 19 API calls and workflow made 20; their recorded tariff estimates were $0.1830744 and $0.1880455. This is an execution-interface failure, not an observed scientific failure of a generated cohort.

| Quantity | PNS ordinary | PNS workflow |
|---|---:|---:|
| Last successfully reserved request, bytes | 239,346 | 246,269 |
| Function-output items in that request, bytes | 207,690 (86.8%) | 204,050 (82.9%) |
| Opaque encrypted-content strings, bytes | 14,960 (6.3%) | 22,904 (9.3%) |
| Literature-search actions | 11 | 12 |
| Extra search-metadata read actions | 4 | 1 |
| Returned search-metadata characters, including overlap | 131,601 | 129,680 |
| Admitted metadata rows, including repeated hits | 37 | 34 |
| Unique admitted PMCIDs | 26 | 31 |
| Admitted PMCIDs literally exposed in metadata outputs | 8 | 10 |
| Unique admitted titles | 35 | 33 |
| Complete admitted title fields literally exposed | 10 | 5 |
| Distinct full-text articles fetched | 2 | 2 |

These byte counts are measured from serialized request-item structures; encrypted content was counted by length and was not decoded or summarized. The last sent request is reported, rather than inventing a size for the next request rejected before reservation. Literal title/PMCID counts are conservative: a field split across output boundaries is not counted as a complete exposed field. They measure presentation, not model comprehension.

The current interface serializes complete Europe PMC core records with indentation, then returns the first 10,000 characters. Long author and affiliation lists can precede useful identifying fields. Character pagination is explicit and therefore not silent truncation, but forces the model to spend calls locating titles and IDs inside metadata that is poorly suited to the task. The workflow model eventually used article section/table selectors; that capability did not resolve the search-result overhead.

## Smallest useful change

Keep the actual gateway search, full-record screening, source exclusions, query and download limits unchanged. Change only the default presentation of already approved search results:

1. Return normalized hit cards: stable local hit ID, exact title, year, PMCID/PMID/DOI when available, canonical article URL, and a bounded abstract preview.
2. Keep the complete original approved record in the existing local cache. Include its record hash and the cache artifact hash. Do not call the preview the complete abstract. Report `abstract_complete`, full character count and an explicit way to read the complete abstract or original record.
3. Paginate between complete hit cards rather than splitting a pretty-printed raw JSON object. Distinguish provider search cursor from local cached-hit cursor so local pagination never silently issues a new query.
4. Use an approximately 800-character abstract preview as a presentation limit, not a scientific filter. All approved hits remain retrievable; none are reranked using case outcomes. Fit as many complete cards as possible under the existing response allowance and give an explicit next cached-hit cursor for the remainder. If an unusually long title/identifier block itself exceeds the allowance, expose the hit ID and declared continuation instead of silently dropping the record.
5. Let the same `read_source` interface request one cached hit's complete abstract or original metadata, in addition to existing PMC section/table access. Do not require the model to rediscover which part of a large core JSON object contains its article.

For ordinary six-hit pages, identity fields plus six 800-character previews should usually fit comfortably below 10,000 characters. This is a design expectation to verify by replaying the actual approved records offline, not a universal size guarantee. Abstract wording remains source text; normalization must not introduce new coefficients, interpretation or evidence selections.

## Context and budget policy

Do not first increase the byte limit or discard encrypted reasoning. Function outputs account for roughly 83–87% of the last sent request sizes; encrypted strings account for about 6–9%. Compact search presentation addresses the measured dominant cause while keeping the same scientific opportunity and cost ceiling.

The transport-byte ceiling is not a model context-token limit. The loop currently reserves costs using serialized bytes plus 4,096 as a deliberately conservative token allowance; this includes escaped tool-output JSON and encrypted content. If compact presentation still fails in a later frozen run, separately measure visible tool/message bytes, opaque bytes, provider input tokens and conservative reservation amounts. Any revision of those ceilings should be explicit and shared by both arms. Do not silently remove prior evidence, tool calls or encrypted continuation items, or introduce a model-written history summary in this minimal repair.

## Validation before a separately versioned rerun

- Replay this round's approved search-cache records through the new formatter without HTTP or model calls.
- Verify that all original hit IDs and complete identity fields are recoverable; every preview is marked; full abstract/record retrieval is byte/hash linked; exclusions and accepted-hit order are unchanged.
- Check record-level pagination, no extra network query for cached pagination, and bounded output for very long abstracts/titles.
- Compare returned bytes and identity-field exposure on the same saved inputs. Do not interpret this engineering replay as evidence that the scientific method improves.
- Keep the current failures and costs. Any new live trial belongs to a new versioned unit, with the same cases, evidence access and scientific policies. The current cohort-generation results remain absent; they cannot be repaired retroactively.

This recommendation does not add agents, a rubric, extra clinical evidence or host-chosen numerical relationships. It makes existing search results usable within the already declared budget.
