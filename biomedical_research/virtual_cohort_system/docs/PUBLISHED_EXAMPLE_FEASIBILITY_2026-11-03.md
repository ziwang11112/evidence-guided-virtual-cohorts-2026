# Public predecessor example: feasibility and next protocol

Verified 3 November 2026. **Select Filshtein et al.'s HRS recipient-side synthesis and cohort-specific, pre-imputation analysis.** This is a manageable native published component using publicly exported aggregate parameters. It does not require source participant records or a new statistical family. The full script is not turnkey: a small parameter adapter and a mixed-model evaluation runtime are still needed. This note proposes preparation; it releases no generation or fitting run.

The review read the existing Filshtein, SynthIPD and neighbor-method notes, then checked current primary papers and official GitHub artifacts. GitHub reads used the connected GitHub tool. No participant data, saved model objects, or third-party repository were downloaded; no generator, model fit, dependency installation or account creation occurred. A parallel reviewer independently checked the completeness of Filshtein's exported rules. No fallback method was pursued because this native component is feasible.

## Selected example and available artifacts

The [published paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC8338788/) is Filshtein et al., *Epidemiology* 2021, DOI 10.1097/EDE.0000000000001373. Its official [repository](https://github.com/powerepilab/Sim_for_data_pooling) remains public, default branch `master`, at commit **6708e43d5e342fa76d57b31d5a6d0bfcc2979539**, dated 16 September 2020. The current inventory contains ten files. It includes source-fitting scripts and aggregate outputs, but no source datasets or saved `.RDA` objects.

All following URLs were accessible. Hashes are **Git blob SHA-1 identifiers**, not SHA-256 file digests. Only this manifest is retained here; third-party files are not republished.

| Artifact | Role | Git blob SHA |
|---|---|---|
| [HRSmodels_20200902_fullDemoTable.txt](https://github.com/powerepilab/Sim_for_data_pooling/blob/6708e43d5e342fa76d57b31d5a6d0bfcc2979539/HRSmodels_20200902_fullDemoTable.txt) | Complete demographic cells and numerical generating rules; 4,938 bytes | `2943aab557016db49da1791398c510bae18c74bb` |
| [HRS source-fitting script](https://github.com/powerepilab/Sim_for_data_pooling/blob/6708e43d5e342fa76d57b31d5a6d0bfcc2979539/HRS_sim_data_code_postGitHub_20200728.R) | Confirms formulas, factor coding and exported model components; inspect only, do not run its source-IPD loading stage | `40bd9c505a2f1d3226c4ffc51572ba8124ec1593` |
| [RCTSim1](https://github.com/powerepilab/Sim_for_data_pooling/blob/6708e43d5e342fa76d57b31d5a6d0bfcc2979539/RCTSim1_postGitHub_20200728.R) | Parameter-list schema, random-effect covariance construction and visit schedule | `55dfe0ad34896f173bee5a140ff034a3b2d82ccb` |
| [RCTSim2](https://github.com/powerepilab/Sim_for_data_pooling/blob/6708e43d5e342fa76d57b31d5a6d0bfcc2979539/RCTSim2_postGitHub_20200728.R) | `dataGen`, HRS mixed-model formula and distribution diagnostics | `2ab7a9788c628c7f7fdf92f2d83272fb1d608d89` |
| [README](https://github.com/powerepilab/Sim_for_data_pooling/blob/6708e43d5e342fa76d57b31d5a6d0bfcc2979539/README.md) | Author's software environment and file roles | `8ec150ff743f21e5e4a69685c762e91c41f787c0` |

**Access and license:** these are publicly readable artifacts with no account or data-access application required. The repository has no LICENSE file, and GitHub reports `license: null`; an explicit code redistribution license was not found. This audit establishes access, not a blanket permission to relicense or republish the authors' files. Keep source links and attribution separate from our original adapter/documentation.

## Native task and completeness

The exported HRS text contains all 28 age-category/sex/race cell counts, CSES regression coefficients and residual SD, education multinomial coefficients, HbA1c Gamma-log coefficients and dispersion, and memory fixed effects plus random-intercept/random-slope SDs, correlation and residual SD. Static cross-checks against the source-fitting and sampling scripts found no missing numerical generating parameter for this HRS component. Source-fitting IPD is unnecessary at the recipient stage.

The native sampler requests **11,509 synthetic subjects at 0, 2, 4 and 6 years: 46,036 visit rows per release**. Baseline age is uniform within the published age categories, including the final 80–100 category. Female, White and College are reference categories. `base.age60=(baseline age−60)/10`; `age60=(baseline age+time−60)/10`. HbA1c is in percentage points, with `U65=min(HbA1c−6.5,0)` and `O65=max(HbA1c−6.5,0)`. Memory is on the published cohort-standardized scale; no original standardization records are needed to synthesize that scale.

The native HRS analysis is:

```text
mem.s ~ age60 * (U65 + O65 + race + educ + sex + cses)
        + (1 + age60 | ID)
```

The two age-by-HbA1c interactions are the focal scientific quantities; retain all 16 fixed effects and the original HRS distribution checks, not just favorable coefficients. [Paper Tables 2–3](https://pmc.ncbi.nlm.nih.gov/articles/PMC8338788/) provide original and synthetic summary references. The original HRS interaction estimates are reported as −0.047 and 0.013; the exported generating coefficients are −0.046837 and 0.012867. Original-source coefficients/intervals are **author-reported aggregates**, not results we independently recomputed. The source fit used 43,500 observed visits, whereas the published simulation schedule creates 46,036 balanced visits; preserve that distinction when interpreting precision. The paper's synthetic summaries average 5,000 repetitions, which this small comparison will not reproduce.

## Mechanical work and concrete prerequisites

1. Parse the single full-demographic HRS text into a reviewed parameter configuration. Replace unavailable `predict.multinom` and Gamma `predict.glm` object methods with their explicit softmax and `exp(Xβ)` formulas. Preserve factor contrasts, Gamma shape/scale convention and the original random-effect SD/correlation construction. Printed rounding is an input limitation, not an invitation to tune coefficients.
2. Isolate the published `dataGen` law and HRS analysis from the full two-cohort pooling/MICE routine and automatic `B=5000` footer. A faithful NumPy sampler adapter can use our existing Python generator worker; it must preserve the published law rather than introduce a new family. This is **reconstruction from rounded published parameters of a native method component**, not a bitwise author-code rerun or reproduction of the complete pooling method.
3. Prepare the longitudinal evaluator. The author README records R 4.0.1, lme4 1.1-23 and mvtnorm 1.1-1, with tidyverse/nnet/mice dependencies for the full scripts. Read-only local checks found WSL R 4.3.3 at `/usr/bin/Rscript`, but none of lme4, mvtnorm, dplyr, tidyr, tibble, nnet, mice, purrr or ggplot2 installed. No Windows Rscript was on PATH. A Python sampler avoids the R generation dependencies; the original primary mixed-model analysis still needs an available R/lme4 runtime, version recorded and checked before clinical execution. No runtime compatibility or execution speed has yet been demonstrated.

This is three bounded implementation tasks—parameter adapter, longitudinal task contract, and native mixed-model evaluation—not acquisition of new source IPD or construction of a survival/digitization subsystem. If it instead requires unreported parameters, extensive model redesign, or an impractical runtime build, record that blocker and stop this example rather than expand methods or datasets automatically.

## Minimal proposed comparison

- One HRS task, one Agent-authored construction, and one fixed reconstruction of the published recipient law. Give both the same complete aggregate packet, factor/measurement definitions, longitudinal request and analysis definitions. Do not supply source participant records. The Agent may use statistical software and may choose the same legitimate model family.
- Three fixed final seeds per construction: **six final generation attempts**, each with 11,509 subjects and 46,036 visit rows; at most 276,216 generated visit rows in total. This is a proposed new allocation, not an extension of the closed CHNS unit. Fix seed values, runtime limits and failure handling in its own short protocol before execution. Use invented inputs for implementation checks; no exploratory HRS tables, outcome-guided refit, best-seed selection or automatic replacement.
- Apply the native HRS mixed-model analysis and complete relevant Table 2 diagnostics to every final release. Report all fixed effects/SEs, the two focal interactions, convergence/singularity, invalid outputs and discrepancies at the precision justified by published references. Preserve individual-seed results and separate average absolute discrepancy from discrepancy of the seed mean. Both routes are executed anew; paper-reported results remain a separate column.
- Deliver the input/transform manifest, parameter-completeness record, two construction descriptions, six attempt records, aggregate native analyses and a concise scope statement. Keep generated rows local.
- **Stop after the declared attempts and independent aggregate verification regardless of ordering.** Matching supplied coefficients is legitimate analysis-preservation/calibration evidence. This task can demonstrate evidence-guided generation in a longitudinal setting; it does not establish unseen-relation prediction, the full cross-cohort pooling/imputation benefit, or superiority over all statistical generators. No human-cost contest is required.

## Why SynthIPD is not the first executable example

The [current SynthIPD record](https://arxiv.org/abs/2509.16466) remains v2, 24 July 2026, with a CC BY 4.0 paper. [N9741 and Table 10](https://arxiv.org/html/2509.16466v2) were rechecked: N9741 offers public graphical/subgroup information, but Table 10 gives no SynthIPD code source. The paper links, first-author research page and bounded GitHub search did not locate a study implementation or runnable input package. This is a scoped access finding, not proof that no code exists elsewhere.

The public [author website repository](https://github.com/ananke1999/zixuan_site/tree/b989ca9e54522f3ea64cf03f883d703b98b4e1f2) is currently at `b989ca9e54522f3ea64cf03f883d703b98b4e1f2`; it has no declared license. Its [illustrative JavaScript demo](https://github.com/ananke1999/zixuan_site/blob/aa933c5c486a09ad687e60a0323e7e54491544eb/js/viz-synthipd.js), blob `8df0df33549bd044f355f652b0b87332a1787b02`, explicitly describes simulated trials, Guyot-style reconstruction and baseline-table matching. It is not the paper's full DIGITIZE plus subgroup-loss Cov-Generation implementation. Reimplementing that method and graphics extraction would be substantially more work than the HRS adapter. No execution of the demo is proposed as a SynthIPD reproduction, and no fallback search was needed.
