# Literature gateway review

The gateway is ready for a fresh, procedurally blinded generator. It does not change any frozen data-packet artifact. The generator chooses its own literature queries; the gateway retrieves publication text from the Europe PMC REST API and applies a conservative contamination screen before exposing text.

Run from the experiment root using the existing Python installation:

```powershell
& 'python' -B literature_gateway.py search --query 'YOUR QUERY' --limit 10
& 'python' -B literature_gateway.py fetch --pmcid PMC1234567
& 'python' -B literature_gateway.py fetch --pmid 12345678
& 'python' -B literature_gateway.py fetch --url 'https://pmc.ncbi.nlm.nih.gov/articles/PMC1234567/'
```

Search uses `resultType=core`, requests title and abstract metadata, and permits limits from 1 through 20. Records without a title or abstract are rejected. Accepted results include source ID, PMID where applicable, PMCID, DOI, title, year, abstract, and the scope of screening. The raw response and rejected record contents are never saved. A search abstract that passes remains only an abstract-screened source; its full text must pass a separate fetch before the generator uses full-text claims.

Fetch accepts a PMCID or PMID. A PMID is resolved through the same screened core-metadata route and must have a retrievable open full text. The URL option accepts only canonical PMC/Europe PMC article URLs or a canonical PubMed ID URL. It extracts the publication identifier and retrieves Europe PMC article XML; it never directly downloads a caller-supplied URL. CDC URLs, arbitrary publishers/downloads, supplementary-file paths, query-bearing URLs, raw-data paths, user information, non-HTTPS schemes, and alternate-host redirects are blocked. The gateway has no patient-data download operation.

Screening is case insensitive and checks normalized text for NHANES, its expanded survey name, punctuation/spacing/markup/Unicode variants, and canonical target file/variable aliases. Complete retrieved article XML is screened, including reference text, captions and appendices. A hit anywhere rejects the entire item. XML processing errors, missing full text and unsafe redirects fail closed. HTTP response bodies, exception representations and rejected excerpts are never printed. Supplementary data are not fetched.

Approved content is stored under `literature/approved` using its SHA256 in the filename, with create-exclusive writes and hash verification on an existing content-addressed filename. `literature/audit.jsonl` is append-only and records queries, status, source IDs, categorical rejection reasons, screened counts and opaque content hashes/artifact integrity metadata. It contains no rejected snippets. The clean generator should use gateway output and approved files only, not audit source IDs to attempt alternate retrieval.

Network requests use the Python standard library, an exact Europe PMC API host/path boundary, a 20-second timeout per attempt, at most two attempts, one second between retries, and an 8 MiB response limit. A PMID fetch can make two sequential requests. No dependency was installed. CLI JSON uses ASCII escapes so legacy Windows console encodings do not corrupt output; approved files remain UTF-8.

Validation completed:

- Thirteen synthetic tests passed, covering aliases, absent-abstract rejection, rejection before display or saving, reference-only contamination, accepted articles, artifact hashes, URL blocking, audit appends, output encoding and search-limit enforcement.
- A neutral live search for protein-folding titles from 2020-2021 screened two abstracts and accepted both. Approved artifact SHA256: `8e6fb1a351a34a6182066c62471df7e2b1a9ea1419d747e0f8ba6bf8c377b24a`.
- A neutral full-text fetch for PMC8284583 passed complete-XML screening. Approved text SHA256: `b5670797ec7b0138230a9911278901d7da45ad41884c2d0272e21d9dc1d3a589`.
- An initial neutral CLI probe encountered a Windows console Unicode-print failure after successful screening. Output was changed to ASCII-safe JSON, a regression test was added, and the live CLI probe then succeeded. Audit records of the failed probe are retained.
- Every hash in the existing frozen packet manifest remained unchanged after implementation.

Implementation hashes at review completion:

| File | SHA256 |
|---|---|
| literature_gateway.py | 74640d1bdc96e57dcc5949e17663b22e04d83c4a70392f83f65f655647680508 |
| test_literature_gateway.py | ccdf3a993f887dc2db56604c5ffe121d770fe2121918c28103a5c6135d7317c7 |

This is scientific-blinding screening, not a guarantee of complete contamination detection. A paper may derive from the target population without naming it in retrieved text; false rejections can also occur. The shared filesystem and internet are not technically isolated by this script. Fresh-agent instructions must prohibit direct web searches, raw target retrieval, rejected-source recovery, and access to custodian/evaluator directories. The gateway does not choose a generation model or evaluate target outcomes.
