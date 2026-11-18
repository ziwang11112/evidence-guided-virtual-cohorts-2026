# Focused primary-source audit: evidence applicability and virtual cohorts

Date: 2026-11-11. Scope: literature only; no model calls, experiments, patient data or changes to frozen results. This is a targeted overlap check, not an exhaustive novelty search.

## 1. KMGen: substantial verified overlap

Official venue: **MLHC 2026, PMLR 340:755–814**, verified independently of the arXiv header. [Official proceedings](https://proceedings.mlr.press/v340/jiang26a.html)

Its agents extract supplied trial materials into typed configurations; a mechanistic sampler produces demographics, survival and adverse events. Source priority is registry → reconstructed survival → publication/appendix → SAP/protocol. Missing fields use declared defaults. External risk multipliers include approximations, not exclusively reported coefficients. Demographics use archetypes and specified distributions; survival uses bootstrap/rank coupling. Joint-event dependence remains incompletely identified. [Methods 2.2; Appendices B/I](https://arxiv.org/html/2608.22618)

Evaluation separates extraction and generation, uses three oncology trials with withheld IPD and 30 regenerations, and acknowledges demographic support/taxonomy errors, underestimated event burden, absent configuration range checks and unvalidated non-oncology generalization. [Results 3.3–3.4; Discussion; Appendix J](https://arxiv.org/html/2608.22618)

**Implication:** agent extraction, explicit priors, provenance, synthetic IPD and real-data comparison are already covered. A distinction worth testing is request-specific model construction and applicability decisions for new target analyses; superiority remains unproved.

Access: main HTML, methods, evaluation and appendices inspected. Repository code was not independently executed or audited here.

## 2. Correction: the supplied JMIR link is not an LLM-GRADE experiment

DOI **10.2196/87804** resolves to *Concerns of Using Large Language Models in Health Care Research and Practice: Umbrella Review*. It applies human-reviewer AMSTAR-2/GRADE appraisal to reviews of LLM concerns. It does not experimentally evaluate an LLM performing indirectness assessment. [Published article](https://www.jmir.org/2026/1/e87804/)

Access: publisher HTML inspected. Do not cite this article as direct experimental evidence of automated GRADE scoring.

## 3. Quicker: a closer published evidence-appraisal system

*Streamlining evidence based clinical recommendations with large language models*, **npj Digital Medicine 8, 793 (2025)**, implements question decomposition, search, selection, evidence assessment and recommendation formulation. Its selection experiment explicitly analyzes indirect evidence and the sensitivity/precision consequences of relaxed PICO matching. GRADE-related evaluation particularly tests risk-of-bias judgments and extraction; this should not be overstated as comprehensive validation of every indirectness judgment. System-level outputs are recommendations, not joint synthetic cohorts. [Primary article](https://www.nature.com/articles/s41746-025-02273-y); [PubMed record](https://pubmed.ncbi.nlm.nih.gov/41423701/)

**Implication:** LLM applicability assessment and evidence workflows have precedents. Indirect evidence is not automatically useless: rejecting every imperfect population match can discard legitimately informative evidence.

Access: substantial publisher/PMC primary full-text sections retrieved through search indexing; direct Nature HTML/PDF redirected to an inaccessible authorization page, PMC direct HTML returned a browser check, and the Europe PMC mirror did not load. Supplementary material and implementation were not inspected.

## 4. NUMBERS: direct overlap with the proposed failure phenomenon

*Language models reflect clinical evidence but fail to adapt it to patients* is a **September 2026 medRxiv preprint**. It tests 16 configurations on 1,300 evidence-linked questions, then population/patient updating and actions. Methods specify no retrieval, browsing or calculation tools. Evidence-consistent answers can miss context-specific quantities; supplied inputs/calculation instructions improve updating, and complete rules improve actions. Patient targets are subgroup prevalences, not individual measurements. [Primary preprint](https://www.medrxiv.org/content/10.64898/2026.09.14.26363047v1.full)

**Implication:** “correct/general evidence, wrong application” is already an explicit studied phenomenon. A narrower unresolved question is how applicability mistakes enter executable joint generators and alter downstream analyses. This is a proposed distinction, not demonstrated novelty.

Access: live abstract/full HTML/PDF requests returned 403; indexed primary abstract, Methods and Results were inspected. Supplementary protocols/code and peer-reviewed publication status were not verified. Do not describe this as a fully reproduced study.

## 5. Decision for this project

Retain the biomedical generation objective. Avoid making either “Agent + literature → synthetic patients” or “real evidence may be inapplicable” the sole novelty claim. A focused next design could test the following chain:

**Source conditions → applicability decision → parameter/structure choice → generated joint law → requested scientific analysis.**

A discriminating test needs independently judged source–task pairs: applicable evidence, legitimate indirect evidence requiring stated assumptions, and genuinely incompatible evidence. Separate population, measurement, adjustment/estimand and timing mismatches. Hold numerical content constant where useful so the test concerns applicability rather than factual fabrication. Record accept/adapt/reject/unknown decisions and their downstream consequences; do not reward indiscriminate rejection or equate a citation with valid transport.

This is our design inference from the audit, not a claim that no prior work has attempted it. The root audit of other robustness benchmarks is complementary. No new experiment is authorized by this note.
