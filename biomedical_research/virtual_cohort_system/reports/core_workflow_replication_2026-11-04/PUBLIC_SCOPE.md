# Public release boundary

This is a reviewed research export of the completed four-author open-evidence workflow replication. It includes original method/implementation code, contracts and commitments, original source/implementation/numerical reviews, aggregate results, all planned endpoint summaries, figures and an aggregate-only figure builder. The original evaluator failure and its additive correction remain visible. This batch is developmental and uses already exposed sample references.

Selected scientific-author artifacts are copied into `authors/C01`, `authors/C02`, `authors/E01` and `authors/E02`: executable generator, model specification, extracted evidence facts and locators, source semantics, feedback recipe, checks, decision and freeze commitment. Their original bytes are preserved. These are research artifacts; local execution paths and hashes describe the original run, not a turnkey portable clinical rerun. Unexported local freeze dependencies and the retained full originals are required for a complete execution audit. Agent conversation contexts and raw acquisition responses are not published.

No participant-level real or generated table, source article/XML/PDF, codebook, credential or raw model context is included. The only CSVs are endpoint-level or author/diagnostic-level aggregates. The only PNG/PDF is our own six-panel statistical result figure. Source facts, numerical summaries, citations and original reviewer prose are included; full third-party works stay local. No prior frozen experiment is replaced.

The public aggregate display can be regenerated from this directory:

```powershell
python build_result_display.py
```

It requires Python and Matplotlib and verifies the two completion-bound aggregate inputs. It creates the figures and summary displays without reading any participant-like records, invoking an Agent, generating a cohort or refitting a real sample. That convenience does not make source acquisition and clinical evaluation available without their separate dependencies/access rights.

Local `work/` links in navigation are changed to public `reports/` links. Otherwise selected code, aggregate JSON/CSV, commitments and figures are copied unchanged. Markdown link rewriting is tracked in the public manifest. The latest paper remains v0.12; this new completed experiment awaits a separately versioned manuscript integration.
