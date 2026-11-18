# Independent review of provenance-audit materials

**Decision: pass for prepared factual review materials, with the limits below. No blocking correction found.** The two ZIPs can be offered as clearly labeled inspection aids; this is not evidence of an audit-time benefit, reliable human scoring, autonomous explanation quality, or clinical trust.

I checked the actual frozen generator code, model specifications, original author notes and locally captured source XML. I did not score a model by its agreement with a target cohort. I have prior exposure to this project’s results and therefore do not claim to be an outcome-blind reviewer. No new target-result or patient/generated-row files were opened in this audit.

## What was checked

- All 12 dossiers, representing three requested analyses of each of four frozen laws, in two clinical contexts.
- The original research requests, exact contracts, source/version manifests, four complete generators, four specifications and four author-note records.
- Every map/answer-key entry against actual code locations and pivotal source statistics, units, populations, measurements and adjustment sets.
- Both reviewer ZIPs, complementary assignment, file contents, original-artifact parity, relative links, HTML IDs, empty response forms and JavaScript syntax.
- Postclosure map attribution, unresolved source interpretations and the absence of claimed human results.

**Independent mechanical checks:** 60 original-artifact parity comparisons; 12 recorded generator/spec/note hash bindings; 55 receipt hash bindings and 55 XML hash/byte bindings; 24 HTML pages with unique IDs; 298 working local links; 24 blank five-question forms; 24 JavaScript syntax checks; 170 ZIP members checked. No failure was found. These are implementation checks, not 170 independent scientific validations.

## Scientific adjudication

| Dossiers | Directly checked basis | Decision and boundary |
|---|---|---|
| D01–02, D04–05 | China-PEACE PMC6324286: statistical methods and BMI–BP results | 1.15/0.75 mmHg per BMI unit and 5.75/3.75 per five units are correct. Additional source adjustment includes treatment and social/geographic factors. Code mean coefficients do not equal every requested linear-age OLS projection. |
| D03 | Uganda PMC11392332: methods, Table 2 and accompanying text | Table 2/abstract call 0.7307 a residual correlation; code uses innovation rho0.73. Categorical BMI, screened covariates and medication exclusion differ. Preserve the contradictory introductory correlation wording rather than score “raw only” as truth. |
| D01–03 | ELSA-Brasil PMC7433850: methods and Table 1 | Sex-specific source moments are marginal anchors. Chosen innovation SD14.8/9.9 is not a directly reported conditional SD. |
| D06 | PMC4143670 phenotype methods/Table3, PMC4338719 sample/Table1, actual lawB | Tau0.578 concerns treatment-corrected age/sex/smoking-adjusted mean residuals over up to three exams. It is not baseline Pearson correlation. Independent formula calculation confirms proxy0.78822561199044 and innovation rho0.763162705682261. Gaussian conversion and independent variance budgeting remain assumptions. |
| D07–08 | Tanzania/Uganda PMC6897412: methods and Table4 | Categorical LDL+0.23/+0.48 and HDL−0.06/−0.15 mmol/L are correct. They do not identify continuous TC/HDL slopes. Actual assumed HDL−0.012 plus nonHDL+0.065 implies conditional TC+0.053 before pooled analysis. |
| D09 | Original notes, specification and lognormal-component code | Rho0.08 is the assumed latent log-error correlation of HDL/nonHDL, not observed TC–HDL residual Pearson correlation. Shared HDL, multiplicative noise and latent context jointly matter. |
| D10–11 | Malawi PMC6747887: methods and Tables2–3; Kenya PMC6435188 v2 Table1 | Reported TC/HDL effects are per ONE SD BMI. Divisor4.8 is Kenyan/model SD, not a retrieved Malawian SD. Full source adjustment, fasting protocol and context differences are correctly distinguished from the requested projection. |
| D12 | Kenya PMC6435188 v2 Table1; lawD mean-variance and gamma code | Female TC/HDL SD0.9/0.30 and male1.1/0.32 mmol/L are correct marginal quantities. Conditional independence of gamma HDL/nonHDL is assumed; TC shares HDL. Neither marginal SDs nor within-context covariance directly identifies pooled OLS residual dependence. |

The pivotal Kenya rows were also checked in captured v1, used by lawC, and agree with v2. The supplementary Maasai context anchor in PMC7263614 Table2 (BMI21.9 SD3.9; TC177.7 SD38.9 mg/dL) matches the original notes. I did not attempt a new full systematic review of all sources the constructors ever retrieved.

All line references were read against the byte-identical generators. Source/reference scales, assumed conditional quantities, derived transformations and final requested projections remain distinct in the key. The original source documents contain neither the generated pooled coefficients nor proof that any transfer assumption is correct.

## ZIP eligibility, neutrality and redistribution boundary

Each ZIP contains **85 files**: 13 HTML, 48 JSON, 12 Python and 12 request-text files. Reviewer A has six mapped and six standard dossiers; B has the complementary format for each dossier and reverse order. Each has three mapped and three standard dossiers per clinical context.

The copied generator, specification, notes, request and task files match the frozen originals. Source manifests match between presentations. ZIP members also match their assigned master copies. The only content difference relevant to the intervention is the extra curated interpretation/navigation and associated presentation metadata; source/code access remains available in both formats.

No patient rows, generated individual tables, target/reference numerical results, host scoring key, full third-party paper, explicit policy/provider identities, absolute local paths or credential patterns were found. The term “outcome” appears in analysis definitions and is not a result leak. File type allowlisting, content inspection and exact-original parity support this conclusion; pattern matching alone was not treated as proof.

Neutral law letters and dossier IDs remove explicit arm/provider labels, but cannot guarantee reviewers will not infer construction style from code or prose. Format itself is visible. Source identities are intentionally visible because auditing them is the task.

## Limits to retain when using these materials

1. **This is a curated audit aid.** The map explicitly says it was assembled after construction from Agent records plus source/code review, adds interpretation/derivations, and has unmeasured preparation effort. A later comparison tests this aid over already informative original notes; it does not isolate autonomous Agent tracing or a layout-only intervention.
2. **The answer key is a factual draft with independent source/code checking.** This review does not empirically validate the 0/1/2 rubric or show inter-rater reliability. Accept equivalent valid source/code locations, distinguish assumptions from errors, and exclude unresolved interpretations with explicit scored denominators.
3. **There are no human observations.** Response count remains zero. A single friend’s comments are qualitative feedback. Two reviewers and 12 nested dossiers would still be a small descriptive pilot. Repeated exposure to the same four laws produces learning that reverse order cannot eliminate.
4. **Source ambiguity is genuine.** Preserve the Uganda correlation-label/reading-aggregation issues; the copula’s repeated corrected phenotypes and Gaussian bridge; categorical-to-continuous lipid assumptions; missing Malawian physical-unit SD; and conditional versus pooled dependence distinctions. A disagreement here must not be labeled an implementation error solely because a target estimate differs.
5. **No visual or interactive QA was completed.** Chrome local-file preview was denied by security policy, and no workaround was attempted. Static HTML/link inspection and JavaScript syntax checks passed. Timer activation, saving downloads, browser rendering, navigation comfort and interruption handling remain unverified in a real reviewer session. No background network or code-execution call is present in the page scripts.
6. **Current public pages may differ from captured versions.** The package correctly warns about this. XML hashes and bytes were locally checked, but future source URL accessibility was not tested. Retain inaccessible-source reports; do not score absence of access as scientific error.
7. **Do not turn provenance into a quality certificate.** Source faithfulness and transparent assumptions aid inspection; they do not establish target transport, model calibration or clinical utility.

No new web retrieval, model/API call, data acquisition, generator execution, human contact or frozen-law edit was performed. The inspection did not require changing any materials. The companion JSON records exact file hashes and source XML bindings for this reviewed release.
