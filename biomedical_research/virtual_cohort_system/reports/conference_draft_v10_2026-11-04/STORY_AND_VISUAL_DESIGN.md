# Conference-style story and visual design

4 November 2026. This writing unit reorganizes completed evidence; it adds no scientific experiment. The full preceding v0.9 and frozen artifacts remain unchanged. The result is a venue-neutral working draft, not a claim of acceptance or compliance with an official conference template.

## What was read

The [G-Sim reading note](GSIM_STORY_AND_FIGURES.md) and [LLMSynthor reading note](LLMSYNTHOR_STORY_AND_FIGURES.md) record primary methods/results reading and inspection of actual PDF pages. Their contribution to this unit is a question-led narrative and compact scientific displays, not borrowed performance claims.

We additionally read the official [SPADA paper](https://aclanthology.org/2025.emnlp-main.525/) in the EMNLP 2025 proceedings: Introduction, Method, experimental design and Results, with actual PDF pages 4 and 6 inspected for methods and comparison displays. Its Figure 1 positions the synthesis task; Figure 2 explains the dependency-graph and numerical generation mechanism. Tables separately address predictive utility, constraints and computational cost. The method fits its numerical components to an observed table. Our no-individual-input setting is different, while the separation of model decisions from sampling is shared. The lesson is to make each display answer a distinct question; we cannot import its efficiency or utility results. The official PDF was kept only in local reading cache (2,480,028 bytes; SHA-256 `632acac4046471f709b270fcafe0790de4335377b586c7545d6912ebde6927f5`).

## The manuscript's own argument

**Problem:** useful biomedical measurements or individual records are unavailable, while studies report partial distributions and relationships.

**Scientific difficulty:** these quantities describe different populations and statistical operators. They do not automatically determine one joint law suitable for a new analysis.

**Method:** an Agent qualifies evidence, chooses its numerical role, authors a joint model and declares missing-dependence assumptions. Numerical tools execute and inspect that model. The requested use can change the generator; the delivered data can then support ordinary scientific analysis.

**Contributions supported now:** an implemented scientific construction workflow; inspectable evidence-to-model transformations and sensitivity; evaluation of useful data products under several explicit information conditions. These are the three introduction claims. Universal quality, first-ever literature-to-data synthesis and systematic revision gains are not claimed.

| Empirical question | Existing evidence | Main display |
|---|---|---|
| Q1. Does relational evidence improve requested analyses? | CHNS/ENSANUT, all six prespecified endpoints; five improvements and one deterioration | Figure 2 and Table 2 |
| Q2. Can accessible summaries become useful joint data? | Separate CHNS L/R study, five focal summaries, all constructors | Figure 3 and Table 3 |
| Q3. Can generated records support longitudinal analysis? | HRS published-model reconstruction; both threshold interactions | Figure 4; complete 16-effect record remains supporting material |
| Q4. Can actual search reach scientific use, and what depends on missing evidence? | Open search, one constructor, seven coefficients, two pre-generation analytical scenarios | Figure 5; real-real variation remains a supplement |

Table 1 states each setting's inputs, construction unit and reference role once. Results are organized by these questions rather than the chronology of development. Main text is approximately 4,923 words; it contains five original figures, three tables and fifteen references. The earlier full draft preserves detailed tables and historical failures.

## Visual decisions

- Figure 1 is original editable draw.io artwork. It distinguishes Agent decisions, deterministic execution, optional inspection feedback and evaluation information. It includes the actual separately-adjusted-projection transformation, rather than implementation plumbing.
- Figures 2–5 use compact full-width layouts, native units, restrained role colors, small panel headings and captions outside the plot. No decorative result banners are needed.
- All prescribed panels and values remain. Seed ranges, seed confidence intervals and empirical reference intervals have distinct meanings in captions. HRS source coefficients are dashed lines without an invented uncertainty band.
- The last sensitivity panel contains exactly the two evaluated analytical scenarios. It is neither a fitted curve nor a patient-validation plot.
- Source SVG/PDF outputs are retained. PNGs are for inspection. The reading copy is ten pages in a generic two-column article layout; no particular conference page budget has been imposed.

The figures were redrawn from existing aggregate JSON, without opening patient tables or rerunning generators. Independent checks bind displayed results to their frozen inputs. Figure 1's cropped PDF corrects a page-size export issue without changing diagram content.

## Next scientific and writing decision

The existing evidence is sufficient for this concrete working draft. The strongest next editorial work is to sharpen the scientific model-author contribution against the cited neighbors and select a venue whose claims and scope fit the demonstrated settings. The current open-retrieval branch has one constructor; a broader claim for that exact branch would require a separately specified study, not relabeling earlier versions. No such new experiment is released by this writing unit.

Author details, declarations, software/data-release terms and official submission formatting remain to complete. The present package is ready for manuscript review, not submission.
