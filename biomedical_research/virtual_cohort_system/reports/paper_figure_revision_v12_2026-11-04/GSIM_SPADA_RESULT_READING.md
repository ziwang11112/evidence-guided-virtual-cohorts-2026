# Result-figure reading for v12

Read on 4 November 2026. This pass reopened the original cached PDFs, extracted the specified result pages and visually inspected the complete rendered pages. It did not rely only on abstracts, previous summaries or secondary descriptions. Official publication pages were also reopened.

## Primary-paper observations

**G-Sim, ICML 2025.** PDF p.7, Table 2 compares test Wasserstein distance across three simulated environments, including calibration variants and ablations. PDF p.8, Figure 2 compares generated and ground-truth trajectories under lockdown interventions. Figure 3 aligns two cost surfaces over the same capacity/lead-time coordinates; Table 3 compares optimized policies and cost. These displays separate overall fidelity from a simulator's use for intervention and decision analysis. The benchmark references are hand-designed simulators, not patient cohorts. [Official paper](https://proceedings.mlr.press/v267/holt25b.html), [primary PDF](https://raw.githubusercontent.com/mlresearch/v267/main/assets/holt25b/holt25b.pdf).

**SPADA, EMNLP 2025.** PDF p.6 (printed p.10342), Table 1 measures downstream prediction after synthetic-data training; Table 2 reports constraint-violation rates. PDF p.7, Figure 3 shows DCR distributions for six methods, and Table 3 separates training and sampling costs. PDF p.8, Figure 4 uses matched longitude/latitude joint plots with marginal histograms and the California boundary. The plotted geometry exposes a concrete data-validity problem that aggregate prediction scores cannot show. DCR is a diagnostic, not a formal privacy guarantee. [Official paper](https://aclanthology.org/2025.emnlp-main.525/), [primary PDF](https://aclanthology.org/2025.emnlp-main.525.pdf).

## Design decisions for our existing results

The useful lesson is to match a display directly to a scientific claim. We can emulate matched axes, a fixed visual encoding and task-specific comparisons. We cannot reproduce the appearance of a patient scatterplot, trajectory or joint-density estimate from aggregate coefficients that do not contain those records.

- Figure 2 will show the six actual regression coefficients in their native units. Every construction and seed remains visible against its appropriate sample reference. The numerical E0/E1 contrast belongs in the existing table and caption rather than an oversized second dashboard.
- Figure 3 will use five native-unit comparisons for the three regression summaries and two correlations. It will show which generated analyses approach the supplied summaries, with separate L/R authors and all seeds. A six-decimal colored card grid does not improve this scientific comparison.
- The visual grammar is white background, compact panel titles, numeric axes, restrained reference bands and one common legend. Color identifies conditions; it is not evidence of statistical significance or a winner badge.
- Reference uncertainty, seed variability and differences among authored models must remain distinct. Their visual proximity is not an equivalence test.

The papers' framework illustrations and empirical results serve different purposes. A detailed diagram can explain the Agent procedure, while a result figure should expose the measurements supporting the claim. This revision changes presentation only; it does not create new empirical relationships or a new benchmark.

## Inspection provenance

| Item | Local original | SHA256 | Visually inspected result pages |
|---|---|---|---|
| G-Sim | `work/neighbor_deep_read_2026-10-31/gsim/holt25b.pdf` | `77a62c51eff5fbfaf3f64cc16aa0de1b520dc038c834fa0df074baab623f770f` | PDF 7–8 |
| SPADA | `work/conference_draft_v10_2026-11-04/source_cache/spada_emnlp2025.pdf` | `632acac4046471f709b270fcafe0790de4335377b586c7545d6912ebde6927f5` | PDF 6–8 |

Page previews were rendered at 100 dpi into a local temporary directory for inspection. Third-party PDF/page images are not part of the public figure package. The source summaries above contain no extended quotations.
