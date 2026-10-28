# Session literature gateway

`literature_gateway.py` is a case-independent publication gateway. It needs only a JSON exclusion/budget configuration and an initially empty session directory. It does not load target data, outcomes, generator parameters, or another builder's session. All CLI responses are one ASCII-safe typed JSON object. Rejected source content is never displayed or saved: only a categorical reason and opaque SHA-256 are retained.

Each construction must use **one fixed session across initial construction and revision**. Different builders use different session paths. The path and exact configuration SHA-256 are fixed on session creation. A session lock prevents overlapping invocations. This is procedural separation on a shared filesystem, **not OS-enforced blinding or a security sandbox**. Builders must not read other session directories, alter gateway state, or bypass the gateway.

## CLI

From the experiment directory, in PowerShell:

```powershell
$python = 'python'
$gateway = './tools/literature_gateway.py'
$configuration = './tools/gateway_config.json'
$session = './builders/example/gateway_session'

& $python $gateway --session $session --config $configuration search --query 'your literature query' --limit 10
& $python $gateway --session $session --config $configuration fetch --pmcid PMC123456
& $python $gateway --session $session --config $configuration list-supplements --pmcid PMC123456
& $python $gateway --session $session --config $configuration fetch-supplement --pmcid PMC123456 --supplement-id 'id returned by list-supplements'
```

The IDs above are placeholders, not evidence recommendations. Fetch requires a PMCID. A direct fetch performs a screened `PMCID:` metadata lookup if the article is not already approved in that session; that lookup uses one query. `--version N` is required if PMC reports multiple versions. A larger version number is not assumed preferable. The first accepted version is fixed in that session. A cached maintext fetch verifies artifact hashes and does not consume another download. Supplement fetching always retrieves and screens the complete selected object and consumes one download.

Search returns complete core metadata records for one requested page, the total hit count and `next_cursor`. An additional `search ... --cursor 'returned cursor'` is another query. More hits than the page size are explicitly reported; records and fulltext are never silently cut. The result text may be large: builders should read approved saved artifacts in full rather than rely on a terminal's truncated display.

## Configuration and budgets

The supplied `gateway_config.json` has this schema:

```json
{
  "schema_version": 1,
  "budgets": {"queries": 12, "downloads": 12, "auxiliary_requests": 80},
  "limits": {
    "response_bytes": 16777216,
    "timeout_seconds": 30,
    "search_page_size": 10,
    "table_cells": 1000000
  },
  "exclusions": {"compact_aliases": ["excluded study alias"], "regexes": []}
}
```

The actual supplied exclusions cover NHANES/HANES/HHANES, full historical and punctuation/Unicode spelling variants, and several generic survey design fields. They encode a study exclusion only, not biological relationships. Unicode normalization, HTML entity and tag handling, and URL decoding precede alias checks. This conservative alias filter can reject unrelated references and cannot prove that all target-derived information has been excluded.

`queries` counts attempted Europe PMC searches, including direct-fetch metadata lookups. `downloads` counts attempted maintext and supplement retrievals together. `auxiliary_requests` counts PMC version/manifest requests. Each attempt is reserved before HTTP starts; failed or rejected requests still count. There are no hidden retries. All usage persists between commands and across revisions. JSON responses and `state.json` include attempts, HTTP successes, HTTP elapsed seconds and cumulative command elapsed seconds. `audit.jsonl` records per-request timing, opaque URL/response hashes, screening outcomes, and accepted artifacts.

## Official retrieval and provenance

Metadata comes only from the [Europe PMC Articles REST API](https://dev.europepmc.org/RestfulWebService). Maintext and supplementary objects come from the documented [PMC Cloud Service](https://pmc.ncbi.nlm.nih.gov/tools/cloud/) and [AWS access route](https://pmc.ncbi.nlm.nih.gov/tools/pmcaws/). The [official bucket README](https://pmc-oa-opendata.s3.amazonaws.com/README.txt) documents version prefixes, JSON manifests, XML URLs, media URLs and MD5 parameters. Documentation was checked on 2026-10-28. The old PMC OA FTP/package service was retired in August 2026 and is not used.

The gateway lists versions under the exact PMCID prefix, screens the complete manifest, retrieves its XML object, checks the manifest MD5 and XML article identifier, and screens the full XML including attributes and references. Supplement IDs are derived from the parent version and object URL. A supplement is eligible only when its exact local filename occurs inside a JATS `supplementary-material` or `inline-supplementary-material` element **and** the same filename occurs in that parent's manifest. A canonical parent article URL, parent XML SHA-256, source href, source object URL, and artifact SHA-256 accompany an accepted supplement. Noncanonical/external links, missing manifest objects and unsupported types are explicit unsupported results. The gateway does not guess publisher links or scrape `/bin/` URLs.

Official manifest `s3://pmc-oa-opendata/...` URLs are mapped to the documented bucket HTTPS origin. HTTPS hosts and paths are allowlisted; credentials, arbitrary queries, path traversal and cross-resource redirects are rejected. The response must be HTTP 200, have an accepted media type and encoding, fit size limits, match Content-Length when present, and match the manifest MD5. The service sometimes uses `binary/octet-stream`; structural parsing remains mandatory. Files are saved under digest-derived names, never source filenames.

## Actual supported supplement formats

- UTF-8 XML/NXML: complete well-formed XML; no internal DTD subset or entity declarations. Nontext embedded payloads are unsupported.
- UTF-8 CSV/TSV: strict complete parsing; ragged rows, malformed quotes and cell-limit overflow are rejected.
- UTF-8 plain text: complete decoded text; binary/control content is rejected.
- HTML/XHTML: balanced complete HTML with an explicit closing HTML element. Embedded images, script, iframe, SVG, canvas and similar content are rejected. Common permissive browser HTML may therefore be unsupported.
- XLSX using installed `openpyxl`: each ZIP member name and XML/rels/VML body is screened **before** workbook parsing. Archives are read only in memory, never extracted. Traversal, duplicate entries, symlinks, encryption, external relationships, expansion limits, parser warnings, unsupported cell types and nontext members (including embedded images and macros) are rejected. All nonempty cells, hidden sheets/rows/columns and comments are emitted. Formula text and any existing cached value are retained, with `cached_value_missing` and `formula_evaluated: false`. No formulas or external links execute. Workbook metadata and chart XML are screened but charts are not rendered; the approved workbook remains available as an artifact.

PDF, DOC/DOCX, XLS/XLSM, arbitrary ZIP/TAR/GZ archives, images, audio and video are explicitly unsupported. PDF support is not enabled because complete text extraction cannot be assured here. Unsupported files are listed as such and are not downloaded. Oversized, malformed or partially parsed inputs fail closed; nothing is silently omitted to fit a limit. The full retrieved maintext may mention or link figures, but only retrieved XML text is screened, not unrequested image pixels.

## Evidence registration and verification

Every approved artifact has `{session_relative_path, sha256, bytes}`. Each write also appends this stable registry event to `audit.jsonl`:

```json
{
  "type": "artifact_approved",
  "status": "accepted",
  "artifact": {"session_relative_path": "approved/<sha256>.<extension>", "sha256": "<sha256>", "bytes": 123},
  "config_sha256": "<configuration hash>"
}
```

A downstream controller should require a matching acceptance event in the intended builder session and verify the current bytes, hash, size and configuration fingerprint. A path containing `approved` is insufficient. Approved metadata is not equivalent to approved fulltext; retrieval scopes are explicit in outputs. No local log prevents a malicious user from editing files: compliance with procedural scopes is still required.

## Verification

```powershell
& $python -m unittest -v test_literature_gateway.py
```

Run from this `tools` directory. Synthetic tests cover rejection opacity, cumulative budgets and failed attempts, session locking/separation, exact parent links and manifest integrity, redirects, malformed/partial parsers, hidden spreadsheet cells/formula caches, archive traversal, and explicit unsupported PDF handling. Tests use temporary folders in `tools` and delete them afterward.

`smoke_neutral/` contains development-only API checks on software-tool papers, outside all experiment builder sessions. It includes failed development attempts as well as successful requests. It must not be used as experiment evidence. Live checks verified Europe PMC metadata and PMC Cloud article retrieval, JATS/manifest supplement listing, and actual service MIME/URL conventions; synthetic fixtures verify the complete supported-format download/parser route. Only neutral software papers were used for these checks.
