# Independent v30 integration review: preliminary boundary and build risks

This review prepares manuscript integration, not a new experiment. The reviewer read the v29 build/compile/verification scripts, the v29 build manifest, and the actual PLAN, FINAL_TABLES and EVALUATION aggregates for the four-law capacity, twelve-law repeatability and twenty-four-session scientific-review units. No generator, model API, patient analysis or broad test suite was run. Only this review directory is editable by this reviewer.

## Facts that the draft must keep separate

| Stage | Author/review unit | Final tables | Recorded tariff estimate | Interpretation |
|---|---:|---:|---:|---|
| Earlier capacity round | 4 initial construction sessions | 12 | USD1.2760368 | Earlier successful stage, retained with its earlier failures/interface context |
| New request-only repeatability | 12 initial construction sessions | 36 | USD3.9851613 | Two requests × two policies × three fresh constructors |
| Scientific-check revision | 24 dependent review sessions of those12 laws | 72 | USD4.8731316 | Two fresh review policies per existing law; not24 new independent constructors |

Each final table has3,000 fictional rows and each law/branch has three seeds. Neither rows nor seeds are new clinical evidence. Twenty review episodes retained the imported v000; four selected changed v001 programs. Sixty retained-law outputs and all six R07 revised-code outputs match initial hashes, giving66/72 unchanged tables. Only R04 changes realized analyses. These review counts must not be added to initial constructors as independent replications.

The actual repeatability aggregates include the unfavorable workflow HDL–BMI coefficient−0.011599 and BP residual correlation0.783441. Keep the near-zero association and the counterexample to universal dependence attenuation. All six lipid laws remain below the lipid residual-correlation and HDL-dispersion references. There is no overall policy superiority conclusion.

The manuscript's earlier PNS DBP SD reference10.757 is a transcription error. The pinned value is11.09413727799307, displayed as11.094. Correct the new draft, preserve v29 and its old receipts. Capacity results such as BP residual correlations0.696/0.727 remain valid earlier-stage results, not the new repeated-study summaries.

## Build recipe and migration risks

The existing build is a custom Markdown-to-LaTeX pipeline, not Pandoc:

1. `build_review_copy.py` converts versioned Markdown, copies each cited PDF figure, writes `paper.tex`, hashes inputs, and packages the Overleaf ZIP.
2. `compile_review.py` runs LuaLaTeX twice. A separate `--standalone` invocation extracts the ZIP and independently compiles it twice. Rendering is a separate option.
3. `verify_review_copy.py` verifies copied/source figure hashes, ZIP members, identical extracted PDF text/external links, caption numbering and LaTeX errors. Final visual review remains necessary.

For v30, copy rather than mutate v29 scripts/assets. Change the hardcoded Markdown name, ZIP name in all three scripts, and the verification facts path; freeze hashes of v29 Markdown/PDF/ZIP and relevant older figures. Do not retain a verification pointer to v29's preservation receipt while claiming it protects the new version.

The builder discovers figure ordering and table counts from Markdown but requires consecutive `Figure N` / `Table N` captions and a single `## Supplementary results` split. Every image must have the corresponding PDF beside it. Basenames are flattened into `figures/`; distinct source folders with the same filename can overwrite each other. Confirm unique output basenames before building. New supplement page-break hints may need updating, but page count is not a target.

Markdown code blocks are intentionally rejected. Display mathematics is accepted only in the supplement. Raw pipe characters inside a Markdown table cell would break the simple table parser. Internal artifact links are rendered as labels; external references remain clickable. Review TeX blocks local workspace identifiers. Keep these design constraints visible when editing the prose and tables.

The script adds fixed author/affiliation placeholders. Do not invent authors, ethics approval or clinical validation while refreshing the edition. Standalone build agreement establishes package reproducibility, not scientific correctness or venue-format compliance.

## Final review criteria

- The main story remains Agent-selected evidence and modeling producing analyzable virtual cohorts with inspectable assumptions. No unvalidated indirectness-score experiment or changed contribution is silently added.
- Twelve fresh constructors,36 tables and two contexts are correctly foregrounded; the earlier four-law stage remains explicitly historical.
- Twenty-four review sessions and72 tables are dependent follow-up artifacts; no36-constructor claim arises from adding12+24.
- All prespecified analysis profiles, adverse estimates, retentions and unavailable historical outcomes are retained, with three-seed means/ranges distinguished from confidence intervals.
- R04 repairs divergent positive measurement moments; R07 repairs a possible post-rounding delivery error. Neither repair is promoted into four observed quality gains;66/72 unchanged outputs is explicit.
- Structured review has no established general advantage. Both policies had the same inspection capabilities, so the policy/gate comparison does not identify the causal effect of checker access.
- TC component ordering is tied to an ideal concentration model, not a universal rule for noisy paired assays. The unchanged R08 HDL>TC diagnostic remains visible.
- Reference estimates remain developmental, previously exposed and uncertain: PNS conditional row-resampling stability, lipid HC3 coefficient sensitivity, no invented residual-correlation interval or equivalence threshold.
- DBP SD is11.094; source means, coefficients, model-law estimands and generated-sample values are not conflated.
- Source traceability supports auditability, not verified transport, calibrated confidence or demonstrated human-review efficiency. No human study is implied by the prepared dossiers.
- New table cells and figure aggregates reconcile to frozen evaluation values; case/policy/stage mappings, units, legends and uncertainty meanings agree across prose and graphics.
- Counts of model calls, successful inspection receipts, failed tool attempts, admitted searches and generated tables have explicit denominators; cost is a tariff estimate, not an invoice.
- Old draft/build history and frozen scientific inputs remain unchanged. Row-level data, raw API captures, captured full papers and credentials are absent from the manuscript/Overleaf export.

Status: preliminary review ready; awaiting the final v30 Markdown and figure/aggregate paths for independent content reconciliation. Root owns build and export.
