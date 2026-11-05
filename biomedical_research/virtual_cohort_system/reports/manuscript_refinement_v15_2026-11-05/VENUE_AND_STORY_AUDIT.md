# Venue and story audit

**Audit/access date: 5 November 2026.** Read: `DRAFT_v0_14.md`, the current v14 gap checklist, original papers and official calls. This assesses fit and readiness, not acceptance probability. No experiments or manuscript changes were made.

## Recommendation

**中文摘要：** 主线应是“Agent 将带有人群、统计定义和适用边界的文献证据转成可执行联合生成模型”，而非“首次用 LLM 生成数据”或“反馈提高准确率”。会议优先看 MLHC Research；Agent 社群可考虑下一轮 AAMAS。PLOS Digital Health 是独立期刊路线。KDD Research/AI for Sciences 可以挑战，但应先讲清实际方法贡献及科学用途，不需要虚构训练创新、临床发现或全面优越性。

Three prioritized routes, respecting the conference preference:

1. **MLHC Research, next announced call:** strongest direct conference fit for biomedical synthetic-data methods and analysis-specific evaluation. State the generalizable insight: compatible published relationships do not uniquely determine all downstream analyses. Clarify the practical scenario use and exposed-reference boundary. MLHC is a specialist ML/health conference, not a universal top-tier CS conference.
2. **AAMAS Generative and Agentic AI, a future main cycle:** best Agent-community fit. Make the consequential scientific decisions visible and distinguish them from deterministic sampling. The ordinary 2027 deadline has passed. A measured reduction in researcher effort would strengthen an application-benefit claim but is not needed to describe the demonstrated workflow.
3. **PLOS Digital Health, Research Article:** best direct journal alternative, with a relevant SynthCraft precedent. Explain the advance over record-based generator orchestration and provide clear intended-use boundaries. Journal fit does not eliminate validation or author-review requirements.

If a broad flagship venue is essential, assess **KDD Research** and its new **AI for Sciences** track before defaulting to ICML/NeurIPS. Research suits the general evidence-to-law method; AI for Sciences suits a paper whose central contribution is advancing biomedical research practice. Neither requires a newly trained model or universal superiority. Neither is established as submission-ready by the current evidence.

## Official conference checks

Future rules are unknown unless explicitly published. Expired dates below are availability checks, not proposed deadlines. All links are official.

| Venue / track | Verified scope, length and timing | Fit and minimal claim-directed gap |
|---|---|---|
| **MLHC Research** | Archival PMLR; generalizable methods/analytical insights. **2026 precedent: 10–15 content pages**, excluding references/appendix; explicit generalizable-insights section. **2027 meeting: 11–13 August, ETH Zurich; CFP/deadline/page rule not yet located.** [2026 CFP](https://mlhc.org/archive-2026-call-for-papers), [2027 homepage](https://mlhc.org/) | Strong fit. Make the health-research use and generalizable finding explicit. Previously exposed references support development, not independent clinical confirmation. Clinical Abstracts is non-archival and not an equivalent full-paper route. |
| **AAMAS GAAI / IASI** | GAAI includes workflows and hybrid classical/generative agents. IASI includes emerging applications/prototypes and evidence of benefit. **8 pages + references**, double blind. **2027 paper deadline: 8 October 2026, closed.** [CFP](https://warwick.ac.uk/fac/sci/dcs/aamas2027/calls/call-for-main-track/), [format](https://warwick.ac.uk/fac/sci/dcs/aamas2027/guidelines-and-policies/instructions/) | GAAI fits the present workflow; IASI fits an application-centered account. Show what the Agent decides and how its choices affect analyses. No need to relabel the system as multi-agent or claim a component advantage. |
| **KDD Research** | Innovative data-science/AI methods, including application-oriented technical work. **8 content pages**, references/appendix additional. **2027 cycle 1: 26 July 2026, closed.** CFP mentions February 2027 but provides no exact next deadline. [CFP](https://kdd2027.kdd.org/research-track-call-for-papers/) | Plausible, ambitious. Sharpen the substantive difference from LLMSynthor/G-Sim. A matched information-condition comparison would strengthen a comparative mechanism claim; the current paper need not make that claim. |
| **KDD Applied Data Science** | Deployed applications ordinarily require **quantified post-launch performance**; limited exceptions are described. **8 content pages**, single blind. Same closed cycle-1 deadline; exact next deadline unverified. [CFP](https://kdd2027.kdd.org/applied-data-science-ads-track-call-for-papers/) | Poor present fit: offline studies/public code do not establish deployed benefit. Do not choose ADS merely because the problem is applied or the statistics are established. |
| **KDD AI for Sciences** | Explicitly includes epidemiology/health; prioritizes domain advancement, rigorous analysis and interdisciplinary expertise. **8-page original full papers**, single blind; references/appendix additional. **26 July 2026 cycle-1 deadline closed; next exact deadline unverified.** [CFP](https://kdd2027.kdd.org/ai4sciences-track-call-for-papers/) | Relevant conditional option. Explain the actual biomedical research benefit and domain-expert involvement. A novel clinical discovery is not mandatory; do not imply one. Methods-centered work is directed to Research. Required limitations/ethics and generative-AI-use sections count within the main paper. |
| **AAAI Main / AISI** | Broad AI includes empirical/integrative contributions; AISI emphasizes socially important problems and evaluation. **7 content pages, 9 total**, remaining pages references. **AAAI-27 paper: 28 July 2026, closed.** [CFP](https://aaai.org/conference/aaai/aaai-27/main-technical-track-call/) | Ambitious. Need a concise AI contribution beyond applying an Agent in medicine. Social benefit is motivation here, not a measured outcome. No subsequent-cycle dates assumed. |
| **ICML Main** | Original rigorous research of broad ML interest; evaluation and probabilistic methods included. **2026 precedent: 8 content pages**, references/impact/appendices additional. **2027 CFP/deadline/page rule forthcoming.** [2026 CFP](https://icml.cc/Conferences/2026/CallForPapers), [current homepage](https://icml.cc/) | Ambitious, not excluded by training-free design. Clarify which general methodological or empirical insight goes beyond G-Sim; additional evidence depends on that chosen claim. |
| **NeurIPS Main** | Health/biotechnology and analyses of limitations included. **2026 precedent: 9 content pages**; references/appendices/checklist additional. No official 2027 CFP/deadline located. [CFP](https://neurips.cc/Conferences/2026/CallForPapers), [handbook](https://neurips.cc/Conferences/2026/MainTrackHandbook) | Ambitious. Use-Inspired or Concept & Feasibility contribution types exist, with high standards. One sensitivity is not a broad negative-results study. Need a substantial generalizable finding, not necessarily new training. |

## Journal alternatives, separately

| Journal | Official fit / format | Main preparation need |
|---|---|---|
| **PLOS Digital Health** | Database Creation and Curation explicitly includes synthetic generation/validation; methods/tools must establish advance, utility and availability. **No fixed word/figure/supporting-information limit**; concision requested. No annual conference deadline. [Scope](https://journals.plos.org/digitalhealth/s/journal-information), [guidance](https://journals.plos.org/digitalhealth/s/submission-guidelines) | Differentiate the evidence-to-law contribution from SynthCraft. Demonstrate useful scenario analyses without claiming measured-cohort replacement. |
| **Journal of Biomedical Informatics** | Explicitly welcomes generalizable biomedical methodology and a “method of methods” selecting established techniques for a class of problems; expects domain knowledge, comparison and healthcare-professional involvement. [Publisher scope](https://shop.elsevier.com/journals/journal-of-biomedical-informatics/1532-0464) | Good conceptual fit if evidence interpretation is specified operationally. The [author guide](https://www.sciencedirect.com/journal/journal-of-biomedical-informatics/publish/guide-for-authors) returned HTTP 403; current length rules were not verified. |

These are alternative publication paths, not concurrent submissions. Author/affiliation, access/ethics, funding/conflicts, AI assistance and licensing details remain incomplete.

## Full-paper storytelling lessons

The following observations come from methods/results, not abstracts alone.

| Published paper | Reading and lesson | Transfer to our manuscript |
|---|---|---|
| **G-Sim, ICML 2025** | Main pp. 1–9 re-read from the existing official PDF; result page 8 visually inspected. It connects desired simulator capabilities to design choices, separates fidelity/ablations (Table 2) from intervention/optimization use (Figs. 2–3). Evaluation uses hand-designed simulators. [Official paper](https://proceedings.mlr.press/v267/holt25b.html) | Define the capability, show the modeling choice, then analyze its consequence. Use our assumption sensitivity for insight; do not inherit intervention or feedback-improvement claims. |
| **SPADA, EMNLP 2025** | Official methods/results read; page 8 visually inspected. Conceptual contrast and operational diagram are separate. Matched geographic plots expose boundary violations that prediction scores miss. Its sampler uses an observed table. [Official paper/PDF](https://aclanthology.org/2025.emnlp-main.525/) | Separate evidence interpretation from sampling. Make residual-dependence failure visible. Do not invent patient scatterplots from aggregate results or inherit speed/privacy claims. |
| **SynthCraft, PLOS Digital Health 2026** | Full main article read. Separates workflow/system comparison, statistical fidelity and downstream use; Fig. 2 retains subgroup results and unsuccessful augmentation. [Published full text](https://journals.plos.org/digitalhealth/article?id=10.1371/journal.pdig.0001290) | Start with the researcher's usable output; keep failures in the main story. Our information contrast is not a controlled Agent-component ablation. |

LLMSynthor's [KDD publication](https://doi.org/10.1145/3770855.3818965) and [author full text v4](https://arxiv.org/html/2505.14752v4) were also checked through methods/results. Its input-supervision labels are useful presentation practice. Aggregate-only construction, LLM dependency modeling and discrepancy feedback are not independently new claims for our paper. Its convergence story cannot describe six retained initial laws.

## Core story and display plan

**Question:** Can an Agent turn heterogeneous published biomedical evidence into an explicit joint law supporting a specified analysis, while exposing conclusions that remain assumption-dependent?

Build the narrative around three results:

- **Evidence becomes an executable model:** qualify population, measurement, operator and adjustment; derive compatible constraints; declare missing dependence. The adjusted-projection example demonstrates scientific modeling, rather than number extraction.
- **The workflow produces complete cohorts across information conditions:** preserve the distinction between external evidence, supplied summaries, longitudinal models and open retrieval. Six laws/18 tables show repeated execution across glycemia/lipids, not independent clinical replication.
- **Usefulness is analysis-specific:** relational evidence improved five of six mean discrepancies; CHNS BMI worsened. All 54 cross-task point estimates matched cached reference signs, but magnitudes, residual dependence and spread remained mixed; the TC reference interval crosses zero. The sensitivity explains why matched relationships cannot guarantee other analyses.

| Display | Scientific role |
|---|---|
| Worked mechanism | One qualified source finding → numerical derivation → chosen law/explicit assumption → generated table → requested analysis. Make the Agent's decision visible. |
| Evidence contrast | All six Q1 coefficients, constructions and seeds, native units and appropriate references; retain CHNS BMI deterioration. |
| Cross-request usefulness | Effects alongside lipid residual dependence and dispersion; preserve every law and reference uncertainty. Avoid a misleading “54/54 success” badge. |
| Assumption sensitivity | Fixed reported relationships, changed missing dependence, reversed conditional coefficient. Label analytical scenarios, not new empirical validation or causal intervention. |

Keep summary-assisted and longitudinal cases compact or supplementary as length requires, without losing their information boundaries. In the abstract, replace chronological batch inventory with one capability result and one analytical boundary.

**Writing can proceed now.** Stronger quantitative transport claims need an unexposed reference; component/feedback improvement needs a controlled comparison; calibrated uncertainty needs source/structural/transport uncertainty; efficiency claims need full preparation/review costs. These are claim-specific options, not a mandatory new benchmark, and none was launched.

## Provenance

G-Sim local official copy: `work/neighbor_deep_read_2026-10-31/gsim/holt25b.pdf`; official record reverified online. Existing rendered `tmp/pdfs/v12_reference_reading/gsim_p8.png` and `spada_p8.png` were inspected. SPADA official ACL PDF and SynthCraft official PLOS HTML supplied the other main-paper readings. LLMSynthor v4 was read as author full text, without claiming pixel-level figure inspection. Venue facts were checked against official sources on the audit date; no projected deadlines or acceptance probabilities were used.
