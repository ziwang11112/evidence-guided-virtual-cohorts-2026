# Three-provider research review

28 October 2026. This package preserves external model advice and subsequent critical checks of the evidence-guided virtual cohort project. It adds no experiment, participant analysis or validated method improvement. Provider agreement is not independent empirical validation, and recommendations are proposals rather than achieved results.

Read the [three-review synthesis](CLAUDE_ADOPTION_AND_THREE_REVIEW_SYNTHESIS.md) for the current adoption decisions. The earlier [Gemini decisions](GEMINI_ADOPTION_DECISIONS.md) are a historical two-review snapshot. The synthesis keeps data generation as the objective, allows a capable ordinary Agent as the main method, and treats source-statistic checks and uncertainty methods as separate hypotheses to test.

## Inputs and provenance

The original frozen experiment/export snapshot is [commit 51d19b6a8fab07f774d0bd6032a2bb9a379595d8](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/commit/51d19b6a8fab07f774d0bd6032a2bb9a379595d8). Existing study files and historical receipts remain unchanged.

The identical [brief](REVIEW_BRIEF.txt), [implementation appendix](IMPLEMENTATION_APPENDIX.txt), and [review request](REVIEW_REQUEST.txt) form the retained input packet. The appendix reproduces 13 selected sanitized files from that snapshot; it is representative rather than the complete implementation. [Its manifest](appendix_manifest.json) binds those bytes. [The material audit](MATERIAL_AUDIT.txt) records the input review. No participant tables or downloaded literature fulltexts accompanied this package. The responses are in English; the original brief's Chinese-language request and the retained English review request remain as submitted artifacts.

| Response | Retained origin | Reported inspection and limits |
|---|---|---|
| [ChatGPT](CHATGPT_REVIEW.md) | Complete retained provider response | Reports reading both attachments and selected private-repository files. This is its access statement, not an independently reconstructed browsing history or complete executable audit. |
| [Gemini](GEMINI_REVIEW_USER_SUPPLIED.md) | Complete user-supplied response, preserved byte-for-byte | Reports reading the packet without repository access. Its broader statement that the private repository is inaccessible outside the local environment is qualified in the adoption/check records. |
| [Claude](CLAUDE_REVIEW_USER_SUPPLIED.md) | Complete user-supplied response, preserved byte-for-byte | Reports reading the packet, denied repository access, and arithmetic on supplied summaries. It did not execute the project. |

The input packet was shared across providers, but actual access and interaction histories differed. The preserved full Gemini and Claude responses were supplied by the user; they are not independently verified browser captures. No response constitutes an end-to-end reproduction of the experiments.

## Critical checks and chronology

- [Earlier claim checks](REVIEW_CLAIM_CHECKS.md) assess the retained ChatGPT response and the earlier partial Gemini retrieval. They remain historical; the raw partial retrieval is omitted.
- [Primary-source checks](PRIMARY_SOURCE_CHECKS.md) verify selected external claims from the ChatGPT review.
- [Complete Gemini checks](GEMINI_COMPLETE_CLAIM_CHECKS.md) and [adoption decisions](GEMINI_ADOPTION_DECISIONS.md) assess the complete user-supplied response and supersede the partial review for content assessment.
- [Complete Claude checks](CLAUDE_COMPLETE_CLAIM_CHECKS.md) and [Claude primary-source checks](CLAUDE_PRIMARY_SOURCE_CHECKS.md) distinguish descriptive arithmetic, implementation observations, proposals, and external evidence.
- [The final synthesis](CLAUDE_ADOPTION_AND_THREE_REVIEW_SYNTHESIS.md) records which suggestions to retain, modify or defer. It authorizes no new experiment by itself.

These checks are targeted, not exhaustive certification of every citation, dataset-access claim or venue recommendation. The source experimental findings, including negative results, are preserved.

## Export and replay limits

[The package manifest](REVIEW_PACKAGE_MANIFEST.json) records every included source/export hash, byte count and reference transformation. Export-only changes replace temporary attachment links or local attachment references with package filenames and remove `utm_source` tracking parameters. Other article query parameters are preserved. Response prose and scientific claims are unchanged. The original source bytes remain local; the complete Gemini and Claude response files require no transformation.

Browser screenshots, raw DOM/HTML/JSON, the original submission receipt, private UI/upload identifiers, participant tables and literature fulltexts are excluded. The complete receipt of the private browser interaction is therefore not independently reproducible from this export.

`build_review_appendix.py` is retained exactly as used. It assumes the original sibling workspace/repository layout; its exported location does not satisfy that assumption automatically. It reads the selected working-tree files rather than checking out the recorded commit. For reconstruction, supply the intended repository at the recorded snapshot and adapt the path in a separate working copy, then verify the appendix hashes. Do not overwrite this historical packet to regenerate it.

Full numerical replay of the underlying studies still requires separately obtained public inputs and the omitted local data/fulltext artifacts described in the repository's reproduction notes. The review export does not rerun or expand those studies.
