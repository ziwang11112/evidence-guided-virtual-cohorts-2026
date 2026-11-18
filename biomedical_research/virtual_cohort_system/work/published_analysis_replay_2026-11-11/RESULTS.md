# Same analysis, different data: completed published-method reuse

11 November 2026. **Completed one fixed analysis on the existing real Turkana deposit and all selected existing virtual tables. No Agent API call or new data generation.** This gives a concrete scientific-use comparison rather than another marginal-distribution score.

## What was reused

Lea et al., *Science Advances* 2020, DOI [10.1126/sciadv.abb1430](https://pmc.ncbi.nlm.nih.gov/articles/PMC7577730/), Supplement PDF page 7, describes age/sex-adjusted biomarker correlations. We implemented that operator once and supplied either real or virtual data. All three pairs supported by the generated schema were retained: BMI–TC, BMI–HDL and TC–HDL. Variables were centered/scaled, separately regressed on intercept + age + sex, and their residuals compared by Pearson r. TC–HDL is **not additionally adjusted for BMI** here.

This is a three-variable Methods-guided partial reanalysis. Original analysis code was not located, and the original paper had ten biomarkers and lifestyle/mediation analyses. Current virtual outputs lack lifestyle; additional original fields are absent from the public patient release. The original complete/pairwise-case and extreme-outlier rules were not fully documented. Our common-case/positivity rules are explicit investigator choices, not an assertion of identical original analytic membership.

The [protocol](PROTOCOL.md), code, input identities and [independent preflight](PREFLIGHT_REVIEW.md) were [frozen](FREEZE.json) before this unit decoded rows. The population and some related statistics were already exposed in earlier development; these are not new independent confirmation data. Choice of the three pairs follows available columns, not favorable results.

## Complete accounting

- One existing real processed dataset: 1,226 input records; 829 incomplete on the five required fields and one participant aged exactly 18 excluded, leaving **396**. Strict age >18 follows the publication's recruitment wording; old project analyses used >=18 and had a different denominator.
- Six existing initial Agent constructions, three saved draws each: **18** tables. Ordinary construction 1 retained 2,972 / 2,969 / 2,961 of its original 3,000 rows under the same strict age rule; all other initial releases retained 3,000. No rows were regenerated or altered.
- Both already completed corrections of ordinary construction 2: **six dependent tables**, shown separately. They do not replace the original or constitute new independent constructors. Other unchanged reviews are duplicates, not additional inputs.
- **25 table analyses and 75 pair estimates**, each with signed r and r²; no failed or omitted table/pair. 54 estimates are initial virtual-table analyses, 18 are dependent correction analyses, three are real-reference estimates. They are not 75 experiments or clinical studies.
- The previously recorded HDL>TC row in workflow construction 1 is retained, not removed to improve agreement. The initial ordinary construction 2 has a previously identified theoretical tail defect; both completed finite-moment repairs are shown rather than hiding that history.

## Results

Each virtual value below is the mean over the three saved draws of that one construction. All individual draws, exact r² and row counts are in [PAIR_RESULTS.csv](PAIR_RESULTS.csv) and [ANALYSIS.json](ANALYSIS.json). Ranges in figures describe draw variation, not clinical confidence intervals.

| Input | BMI–TC r | BMI–HDL r | TC–HDL r |
|---|---:|---:|---:|
| Real processed sample, n=396 | 0.0701 | -0.1166 | 0.4983 |
| Ordinary 1 | 0.1849 | -0.0754 | 0.3112 |
| Ordinary 2, initial | 0.3139 | -0.0886 | 0.3118 |
| Ordinary 3 | 0.2707 | -0.1475 | 0.3633 |
| Workflow 1 | 0.2282 | -0.0883 | 0.1211 |
| Workflow 2 | 0.2368 | -0.0005 | 0.3458 |
| Workflow 3 | 0.2156 | -0.1089 | 0.2865 |
| Ordinary 2 → generic review, dependent | 0.3046 | -0.0886 | 0.3141 |
| Ordinary 2 → structured review, dependent | 0.2892 | -0.0899 | 0.3157 |

BMI–TC and TC–HDL have positive estimates throughout the initial saved draws, agreeing in direction with this real sample. Their magnitudes differ systematically in opposite directions: BMI–TC is stronger in the virtual releases and TC–HDL is weaker. BMI–HDL is negative in five constructions across their three draws, with several construction means near the real point estimate. Workflow 2 is near zero and changes sign (+0.00177, -0.00794, +0.00476); its slightly negative average is not stable negative-association preservation. The two tail repairs change these three analysis outputs only modestly and do not establish general improvement in analysis fidelity.

## What this supports

The same analysis function runs without case-specific numerical changes on real and Agent-generated data. Existing virtual releases retain some association directions and approximate some selected associations. They do not preserve the whole three-pair quantitative profile uniformly. This supports **analysis-specific reuse with an explicit complete result profile**, not automatic substitution for all conclusions of the original study. We do not infer causality, population truth, statistical equivalence, clinical accuracy or policy superiority from this descriptive comparison.

No clinical threshold or success score was invented after viewing these estimates. The selected real sample is uncertain, and unprovided lifestyle composition or evidence-transfer assumptions may affect the comparison. This unit does not identify the cause of the discrepancies. Correlation alone also does not certify marginal distributions, prediction or power calculations.

## Verification

The preflight repaired two implementation-reporting issues before release: retain row counts if a later fit is unavailable, and reject malformed nonmissing tokens even when another field in the same row is missing. Seven initial invented-data tests and three affected revision test executions passed (overlapping test cases are not ten independent checks of scientific quality).

An independent implementation used a centered covariance Schur complement, rather than importing the main least-squares function, and independently parsed/selected all inputs. [Independent recomputation](INDEPENDENT_RECOMPUTATION.md) passed **649 checks**, including all 150 numerical r/r² outputs; maximum absolute discrepancy was **1.33e-15**. Input hashes before and after remained unchanged. Patient and generated individual rows were not exported.

## Decision and next action

Use this completed result as a small, concrete **same-analysis / different-data** example in the paper and report, alongside the stronger longitudinal HRS analysis-preservation example and the glycemia adjustment-pattern example. The HRS source-model case is separately scoped in [HRS_SCOPE_AUDIT.md](HRS_SCOPE_AUDIT.md); do not equate it with a true raw-HRS reanalysis.

Do not retune the six frozen laws against these newly shown correlations. Do not expand the benchmark simply to obtain more favorable pairs. If a later experiment is intended to reproduce the Turkana paper's main lifestyle application, its required output schema must include the original lifestyle grouping and its original analysis must be specified first. That would be a new task, not a cosmetic relabelling of latent mixture components or another analysis of the present tables. It is not automatically launched by this unit.

[Standalone visual comparison](index.html). The manuscript v0.30, previous scientific results and their frozen files remain unchanged. No new generation, paid API call, dataset download, training, HPC job, browser workaround or public synchronization occurred.
