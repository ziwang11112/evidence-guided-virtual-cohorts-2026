# Official knowledge and synthetic-cohort validation

Checked 2026-11-09. This is a source audit and proposed validation policy, not an experiment. No participant-level data were downloaded.

## Answer to the research question

Yes: an evidence-guided agent can retrieve public hospital laboratory documentation, government documentation and statistics, and professional clinical guidelines in addition to research papers. Eligibility should depend on the precise claim being supported, its provenance, and its applicability. An official domain is not a substitute for validation of the generated cohort. A paper hosted by NIH/PMC is also not automatically an NIH-authored recommendation.

The useful separation is between (a) definitions and measurement rules, (b) normative clinical workflows, (c) population summaries, and (d) conditional clinical relationships. These are distinct evidence objects; the generator should not silently promote one into another.

## Direct precedents and their limits

**Original Synthea paper.** Walonoski et al. was published online 30 August 2017 and appeared in the March 2018 JAMIA issue (25:230–238; DOI 10.1093/jamia/ocx079). It explicitly combines public aggregate health statistics, clinical practice guidelines, clinician input, and coding dictionaries in state-transition models. Its initial validation emphasized type 2 diabetes: age at diagnosis, disease/complication prevalence, and treatment properties were compared with public statistics. Initial output contained substantial errors; transition probabilities were revised, then several simulations were compared. Remaining discrepancies included underestimated complications and overestimated medication use, with perfect prescribing/adherence identified as a likely explanation. Some progression probabilities were estimates because suitable statistics were unavailable. This is a precedent for transparent, iterative calibration, not proof that all modules or joint distributions were validated. The paper positioned its data for nonclinical secondary uses and explicitly limited claims about clinical discovery. These statements describe the reported historical version, not every current Synthea release. [Primary paper, especially “Validation of Synthea,” Table 2, and Table 3](https://pmc.ncbi.nlm.nih.gov/articles/PMC7651916/)

**A directly relevant LLM precedent already exists.** Kramer et al., JAMIA Open 2026;9(1):ooaf123, used supplied authoritative medical sources to construct functional requirements, generate a Synthea model, assess syntax and requirement implementation, and iteratively refine it. The authors did not rely only on internal LLM knowledge. Hyperthyroidism was the example. Level 1 checked model structure; Level 2 used an LLM judge. Scores reaching 100% meant the judge considered requirements met, not that implementation or clinical validity was established. Expert inspection found models runnable but not production-ready. Population validation was not attempted because model shortcomings remained; clinical expertise and systematic expert review were still needed. This supports retrieval-assisted model construction while sharply limiting claims based on self-evaluation. [Primary paper](https://academic.oup.com/jamiaopen/article/9/1/ooaf123/8415656) · [Verified PubMed record](https://pubmed.ncbi.nlm.nih.gov/41502536/) · [PMC full-text record](https://pmc.ncbi.nlm.nih.gov/articles/PMC12772637/)

The official project also maintains a repository of output-visualization/validation notebooks. Its existence is evidence of an explicit evaluation workflow, not a certification of every generated dataset. [Synthea module-validation repository](https://github.com/synthetichealth/module-validation)

## Concrete CDC example: hs-CRP

The NHANES 2017–2018 hs-CRP codebook identifies the unit (mg/L), eligible ages (1+), measurement method, lower detection limit (0.15 mg/L), below-detection flag, and LLOD/√2 fill convention. QA included staff assessments, blind split samples, repeat testing of 2% of specimens, Westgard rules, quarterly QC review, and laboratory confirmation of improbable results. An instrument-bridging study found mean results 19.6% lower on the newer instrument despite correlation r=0.997; specified regression adjustments have restricted concentration ranges. Thus very high correlation did not establish measurement equivalence. The codebook also requires survey-design variables and attention to missingness. These support correct measurement semantics, censoring, harmonization, and interpretation of population summaries. They do not supply a colorectal-cancer-specific conditional biomarker model. [CDC HSCRP_J documentation](https://wwwn.cdc.gov/nchs/data/nhanes/public/2017/datafiles/HSCRP_J.htm)

The corresponding method manual distinguishes an adult serum reference range (<5 mg/L), analytical measurement range (0.15–20 mg/L), and reportable range with dilution (0.15–300 mg/L). These are different concepts. [CDC laboratory method manual, section 9](https://wwwn.cdc.gov/nchs/data/nhanes/public/2017/labmethods/HSCRP-J-MET-508.pdf)

## Proposed operating policy — methodological inference, not a published result

| Retrieved evidence | Appropriate use | What it cannot establish on its own |
|---|---|---|
| Hospital/official assay documentation | Units, specimen, method, detection/censoring rules, applicable reference intervals | Disease-cohort means, tails, correlations, or outcome relationships |
| Clinical guideline | Definitions, decision thresholds, contraindications, recommended care sequences | Actual adherence, utilization, treatment assignment probability, or causal treatment effect |
| Official aggregate statistics | Target population, prevalence, demographic margins, explicitly reported strata | Unreported joint distributions or transportability to a hospital-selected cohort |
| Clinical study with conditional estimates | A particular association/transition given its population, adjustment set, endpoint, and timing | General validity outside those conditions or automatic causal interpretation |

For each extracted claim, retain publisher, exact URL, title, issue/version date, source passage/table location, population, setting, specimen/method, units, denominator, conditioning variables, uncertainty, and intended generator use. Mark whether it is directly reported, transformed, inferred, or assumed. Trace a retrieved summary back to its primary evidence where the proposed use requires numerical estimation.

Validate in separate layers:

1. **Extraction:** check numbers, units, reference population, time window, and transformations against the source; adjudicate conflicts instead of averaging incompatible values.
2. **Implementation:** run schema/unit/probability tests, formula checks, temporal checks, and requirement-to-code traceability. A clinically unusual value should not be rejected merely because it lies outside a healthy reference interval.
3. **Clinical plausibility:** review patient trajectories and combinations against explicit rules, with domain expertise. Label unmeasured dependencies and assumed transition probabilities.
4. **Statistical fidelity:** predefine relevant margins, subgroups, correlations, conditional distributions, missingness, and temporal/outcome relationships. Compare with suitable evidence reserved from calibration where possible, quantify uncertainty, and inspect variation across seeds. Reproducing the same statistics used to fit a generator is calibration evidence.
5. **Intended-use validity:** evaluate the downstream analysis or prediction task against independent evidence appropriate to that claim. Agreement with references and aggregate tables alone supports evidence consistency; it does not demonstrate performance in real patients.

When only aggregate evidence is available, report partial validation and sensitivity to alternative plausible dependency structures. Different patient-level joint distributions can reproduce identical margins. Neither a reputable website nor an LLM judge resolves that identification problem.
