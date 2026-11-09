# Public website and PDF evidence adapter v1

`cohort_harness/web_evidence_v1.py` adds one task-bound public HTTPS retrieval
operation. It does not run an Agent, invoke a model, execute a generator, infer
clinical relationships, or modify a frozen candidate. No publication list or
domain allowlist is built in: the caller can supply a public hospital, NIH, CDC,
publisher, or other primary-source URL. The caller remains responsible for source
selection and applicability. A declared source type does not authenticate its site.

## Public API

```python
from cohort_harness.web_evidence_v1 import init, fetch, verify, validate_config

configuration = validate_config({"http_requests": 12, "total_bytes": 16_777_216})
initialized = init(bundle, configuration)
result = fetch(bundle, url, source_id="source-definition",
               purpose="Inspect the published measurement definition",
               source_type="official_hospital_website")
current_state = verify(initialized["state"])
# verify(bundle) is equivalent when the caller does not have a binding descriptor.
```

The example deliberately leaves `url` to the caller. It is not a suggested paper
or an applicability assessment. `init` and `fetch` return typed dictionaries;
successful statuses are `ok` and `accepted`. Errors use `error` or `rejected`, an
opaque categorized `reason`, and sometimes a content hash. Rejected text and
tracebacks are not returned. `verify` raises `ContractError` or a categorized
gateway parsing/screening error on invalid state. `validate_config` has no file or
network side effects and rejects unknown fields, booleans, and invalid integers.

The stable `init(...)["state"]` descriptor contains exactly:

```json
{
  "schema_version": 1,
  "kind": "web_evidence_binding",
  "bundle": "<absolute bundle path>",
  "task_sha256": "<task byte hash>",
  "config_sha256": "<canonical config byte hash>",
  "state_path": "web_evidence_v1/state.json"
}
```

`verify` reads the current state rather than treating this descriptor as a stale
snapshot. It verifies task/config binding, usage bounds, cached artifact bytes and
hashes, approval events, manifest linkage, and registry membership. The full disk
state has `binding`, `created_utc`, `usage`, `retrievals`, and `registrations`.

## Permission and resource accounting

The existing task must validate and use `published_evidence`. Fetch additionally
requires the exact `web.fetch` permission in `information_policy.allowed_tools`.
The existing `registry.json` must validate before initialization or retrieval.

The adapter uses the existing literature gateway's fixed configuration, session,
exclusion screen, and lock. One previously uncached URL consumes one existing
`task.budget.source_downloads` allowance, including transport, parsing, and
screening failures. There is no new paper-count budget. The controller can set a
large download allowance while bounding operational cost with its own actions
and the explicit request/byte limits below. Cached successful URLs use no further
download or request allowance. Changing the caller's purpose or source ID creates
a new provenance manifest over the same verified cached retrieval.

| Config key | Default | Meaning |
|---|---:|---|
| `response_bytes` | 16,777,216 | Maximum bytes read from one HTTP response |
| `extracted_bytes` | 8,388,608 | Maximum UTF-8 text bytes accepted |
| `total_bytes` | 67,108,864 | Cumulative response bytes across this session |
| `http_requests` | 32 | Cumulative attempts, including redirect hops and failures |
| `timeout_seconds` | 30 | Deadline for one retrieval, across DNS, redirects, reading and parsing checks |
| `max_redirects` | 5 | Maximum redirects followed for one retrieval |
| `pdf_pages` | 300 | Maximum PDF pages submitted to text extraction |

Only `total_bytes`, `http_requests`, and `max_redirects` may be zero. `init` stores
the merged exact configuration. Reinitialization cannot reset usage or change
configuration. Task edits, a moved bundle, or changed configuration bytes fail
binding checks. Neither budget exhaustion nor a failed request triggers retries.

`usage` reports adapter `downloads`, `http_attempts`, `http_successes`,
`response_bytes`, and command `elapsed_seconds`; `shared_usage` reports the
existing gateway counters, including downloads from both adapters. Response
bytes include bytes read before a later rejection. Rejected content is not saved.
HTTP error and redirect bodies are not read. Declared oversized bodies are
rejected before reading. Without a Content-Length, a body reaching the exact byte
ceiling is conservatively rejected because checking EOF would exceed that ceiling.

## Transport and parsing boundary

Only HTTPS on port 443 is accepted. URL user information, local hostnames, private,
loopback, reserved, link-local and other non-global addresses are blocked. Every
redirect is checked independently. All DNS answers must be global. A validated
address is used directly for the socket connection; TLS still verifies the
original hostname. The transport does not resolve again during connection and
does not use environment proxies, authentication, cookies or automatic redirects.
A timed daemon resolver bounds how long the caller waits for DNS. No hidden
address fallback or network retry occurs.

HTML and plain text use the declared charset, or UTF-8 when absent. HTML is parsed
as inert text with the standard-library parser. Script/style/template/noscript
contents are omitted from extracted text, while the complete decoded HTML,
including attributes, hidden contents and reference sections, is alias-screened
before storage. No linked assets, scripts, frames or secondary URLs are loaded.
HTML parsing tolerates ordinary imperfect web markup; it is not a browser render
or a guarantee of a page's scientific completeness.

PDF uses optional locally installed `pypdf`, falling back explicitly to the
already-installed `PyPDF2` API. The chosen parser name and actual package version
are recorded. Parsing runs in a separate process with the remaining retrieval
deadline. It accepts text extraction only and performs no OCR. If both parsers
are unavailable, or a PDF is encrypted/invalid, exceeds a page or extraction limit,
has empty extracted text, or times out, an explicit failure category is returned. An
image-only page or figure is not represented as read evidence. PDF binary objects,
visual content and embedded files are not exhaustively screened or interpreted.
No PDF code is executed and no parser package is installed by this adapter.

The screen is the existing gateway's normalized `excluded_cohorts` alias screen;
no population-specific exclusions or clinical assumptions are added. URLs, caller
declarations, decoded HTML/plain text, raw PDF character sequences, PDF metadata,
and extracted PDF page text are screened. A
source mentioning an excluded cohort even in its references may be rejected.
Alias screening can miss target-derived evidence and cannot establish scientific
independence. Network and parser resource checks are procedural controls; parser
processes do not have a separate memory quota or OS sandbox.

## Provenance and immutable registration

```text
bundle/
  task.json
  registry.json
  gateway/                  # unchanged literature gateway contract
  web_evidence_v1/
    binding.json
    config.json
    state.json
    audit.jsonl
  sources/web_evidence_v1/
    <hash>.raw              # actual response bytes, never executed
    <hash>.txt              # extracted UTF-8 source text
    <hash>.json             # typed provenance manifest
```

Each accepted manifest records the requested and actual final URLs, redirect
chain, actual retrieval UTC time, media type, parsed form (`html_text`,
`plain_text`, or `pdf_text`), parser details, raw/extracted byte counts and hashes,
caller source ID, `author_stated_purpose`, and `author_stated_source_type`.
`applicability` is always `not_assessed`. All retrieved contents carry the
`untrusted_source_data` role and must never be interpreted as tool instructions.

Only parsed and screened artifacts are appended to the existing registry. Its
five-field schema remains unchanged: `source_id`, `path`, `sha256`, `origin`
(`gateway`), and `screening` (`approved`). The registered manifest carries the
additional typed provenance. An approval event must bind each cached retrieval
and registration; merely placing a file in the source directory grants no
approval. Repeated requests recheck hashes, sizes and approval linkage before
returning paths. Previous registry entries and frozen candidates are untouched.

Files and logs remain trusted local inputs, as in the literature adapter. A
malicious local writer who rewrites all trusted records can defeat procedural
provenance. An interrupted multi-file append may require explicit review;
initialization never silently removes records or repairs/reset budgets.

## Verification performed

`tests/test_web_evidence_v1.py` uses invented records and intercepted HTTP. It
covers permission binding, public-address checks, redirect charging and rejection,
TLS hostname with a pinned address, cumulative byte/request limits, failed calls,
shared download allowance, conservative exclusions, PDF-unavailable/no-OCR paths,
cache and approval tampering, source reuse with a new purpose, and continued
verification of a previous frozen receipt. In addition to explicitly substituted
parser fixtures, the tests generate a tiny invented PDF with the existing `fitz`
package and pass its actual bytes through the installed parser subprocess. A
second real-parser fixture tests an excluded alias in PDF metadata.

On 9 November 2026 the specified local Python had no `pypdf` installation, but its
existing `PyPDF2` fallback successfully extracted the invented PDF. No packages
were installed. The focused adapter plus existing literature suite passed 54
tests, with outputs under `work/adaptive_evidence_loop_2026-11-09/w5`.

A single live request to the NIH About page was also attempted. The server
returned HTTP 403; the adapter recorded one failed HTTP/download attempt, zero
body bytes and no new evidence. It did not retry or report successful retrieval.
The exact result is retained in
`work/adaptive_evidence_loop_2026-11-09/live/smoke_result.json`.
