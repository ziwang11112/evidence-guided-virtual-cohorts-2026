# v0.10: question-led scientific draft revision

2026-11-04. This revision uses the `arise-evidence-to-manuscript` consistency workflow and the primary-paper reading notes for G-Sim, LLMSynthor and SPADA. It changes the scientific narrative and display organization. It does not change a frozen experiment, generate records, read patient rows or rerun an analysis.

## Result and organization

New draft: [DRAFT_v0_10.md](../../manuscript/DRAFT_v0_10.md).

Working title: **From Published Evidence to Analyzable Biomedical Data with a Scientific Agent**.

The main text currently contains approximately 4,923 whitespace-delimited words including captions and tables, with a 191-word abstract. The total including supporting-material navigation and references is approximately 5,636 words. These counts describe an English reading draft, not compliance with a selected venue's official page limit.

The story is application need → statistical construction difficulty → Agent scientific responsibilities → four empirical questions → information-dependent uses and limits. It follows the organizational lessons of the related conference papers without copying their artwork, claiming their performance results, or inventing corresponding ablations.

| Section | Scientific purpose | Revision from v0.9 |
|---|---|---|
| Abstract / Introduction | Explain the required data product, why available studies do not specify a joint law, and the demonstrated contribution | Use one coherent problem and three contributions; remove the sequence of operational checkpoints |
| Problem | Make inputs, output and scientific utility explicit | Request, qualified evidence, optional observations, Agent-authored generator and downstream analyses; complete-cohort generation remains primary |
| Method | Explain the actual scientific choices | Evidence qualification, numerical modeling, execution and review; retain the separate-projection equations and their concrete numerical example |
| Q1 | Test added relational information for requested analyses | Keep all six outcomes, all constructors and fixed statistical references; retain CHNS BMI deterioration and conditional-age mismatch |
| Q2 | Demonstrate summary-assisted joint-data reconstruction | Keep all five displayed relations, the available reference information and separate statistical supplement |
| Q3 | Demonstrate a materially different data/analysis structure | Retain the two longitudinal interactions, source-model identity, high-HbA1c mismatch and our comparator-parser incident |
| Q4 | Connect actual evidence acquisition to data and analysis-sensitive assumptions | Retain the complete seven-term figure, mixed utility, two analytical sensitivity points and all real-real metrics through supporting material |
| Discussion | Explain usefulness and remaining information/implementation limits | Consolidate repeated qualifications; keep exposed references, no demonstrated revision gain, missing uncertainty and limited standalone deployment |

## Source-reading lessons actually used

- [G-Sim note](GSIM_STORY_AND_FIGURES.md): align method choices with the application need; put complete principal results before an enabled-use example; keep an actual numerical modeling example.
- [LLMSynthor note](LLMSYNTHOR_STORY_AND_FIGURES.md): organize evaluation by questions, separate information conditions and data structures, and keep numeric execution distinct from LLM scientific decisions.
- SPADA official PDF, cached at `source_cache/spada_emnlp2025.pdf`: the parent inspected the method/experiment pages and figures. The draft author additionally read the cached original's front matter and Sections 3.1/3.3 to verify its observed-table input and conditional KDE use. The new citation explains this input distinction and does not label the prior work non-agentic or hard-coded.

Primary originals: [G-Sim](https://proceedings.mlr.press/v267/holt25b.html), [LLMSynthor v4](https://arxiv.org/html/2505.14752v4), [SPADA official record](https://aclanthology.org/2025.emnlp-main.525/).

## Numeric and result preservation

The complete [v0.9 draft](../../manuscript/DRAFT_v0_9.md) is retained unchanged as the extended methods/results companion. The historical supplement and exact experiment reports remain linked. Main-text condensation does not turn unlike protocols into one common benchmark.

| Original display | v0.10 treatment | Numerical check |
|---|---|---|
| v0.9 Table 1: three information settings | Condensed and extended into new Table 1, adding the separately identified open-search construction | Original counts and interpretations retained; no pooled denominator |
| v0.9 Table 2: six estimands and reference intervals | Full table remains in the extended companion; adjustments and units appear in new Table 2 and Figure 2 | No altered reference values |
| v0.9 Table 3: six information contrasts | New Table 2 | All **18 displayed discrepancy/contrast values** programmatically match exactly |
| v0.9 Table 4: five L/R analyses | New Table 3 | All **25 displayed reference/range values** programmatically match exactly |
| v0.9 Table 5: latest seven coefficients | Complete new Figure 5; full table retained in extended companion | No term or fixed seed excluded by draft selection |
| v0.9 Table 6: nine real-real quantities | Main-text examples plus linked full 36-metric table and seven-term supplementary figure | Definition unchanged; no acceptance line or new significance test |

The methods retain the main construction/seed hierarchy, exposed-reference status and different uncertainty meanings. Q2 retains 42 actual executions, 24 unique tables overall and 18 unique delivery tables; physical duplicates are not confused with final aliases in the later workflow. Q3 retains nine physical generations, three invalid initial comparator tables and six valid comparison tables. Q4 remains one construction plus one trial, not a multi-cohort autonomous benchmark.

Reference entries 1–14 are byte-for-byte text matches to v0.9. Reference 15 adds the verified SPADA official author/title/proceedings/page/DOI record. The source literature is used for precise task positioning; the manuscript does not claim that Agent involvement or numerical sampling is exclusive to this system.

## Figure and production status

The five main figure calls target `manuscript/conference_figures_v10_2026-11-04/`, using the filenames supplied by the coordinating author. The five main SVG files have been produced independently and all draft image paths resolve. Caption semantics distinguish generated seed ranges, model-conditional intervals and sample-reference uncertainty. The old figure packages remain unchanged.

The final local check found all 18 local references present, including all five new main figures. The author viewed new Figures 2–5. Figure 2/3 captions now describe their actual seed-dot, constructor-diamond and range-segment grammar; Figure 4 correctly says that dashed lines show source coefficients, without claiming that unplotted source intervals are displayed. Figure 5 maps panels (a–g) to every regression term and (h) to the two analytical scenarios. No missing original result/source record was found.

The v0.9 SHA-256 remains `0de628da4d71bc8ef1fa28c8ec703bccf991bcc27839b37af66aca5a6b00a05e`. The current v0.10 SHA-256 after caption/path checks is `d51907968c9b42c0c4eda4ba04c076e4cbb486c8803c41814a95f5a7e498ce6d`.

The independent reading refinement changes “isolate an information contrast” to “evaluate an information contrast”, avoiding a causal interpretation of independent constructor comparisons. Final captions explicitly distinguish the main no-individual-input setting from permitted target summaries and published model inputs, describe the review loop without claiming revision gain, and identify both HRS panels as spline branches of one full model. The separate [Figure 1 review](FIG1_REVIEW.md) confirms eleven nodes, ten scientifically appropriate arrows and a supplied PNG without clipping; the reviewer did not edit the diagram.

Final author declarations, conference selection, official template and actual-size typeset inspection remain separate submission work. This draft does not predict acceptance at a particular venue.
