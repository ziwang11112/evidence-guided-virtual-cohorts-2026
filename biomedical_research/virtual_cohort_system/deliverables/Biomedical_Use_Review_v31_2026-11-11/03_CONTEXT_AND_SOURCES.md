# Context, methods and sources

This package accompanies manuscript v0.31. It adds the completed lifestyle case
to the earlier glycemia/lipid materials. It is a root-led summary of recorded
source/code audits and completed results, not a new independent source review.

## Source study and population

Lea et al. (2020), *Urbanization and market integration have strong, nonlinear
effects on cardiometabolic health in the Turkana*.
[Original article](https://pmc.ncbi.nlm.nih.gov/articles/PMC7577730/),
[DOI](https://doi.org/10.1126/sciadv.abb1430),
[supplementary methods](https://gurven.anth.ucsb.edu/sites/default/files/sitefiles/papers/lea%20et%20al.%202020%20supplement.pdf).

Locators: main Methods, Data filtering and processing; Testing for lifestyle
effects on measured biomarkers (models 1-2); Figure 2A; Tables 1-2; supplement
measurement and lifestyle definitions, pp. 3-8. Full articles are not bundled.
The recorded source audit could not recover the original S1/S2 spreadsheets or
author analysis script. No missing coefficients were inferred from their filenames.

Pastoralists combine Turkana-county location, pastoral subsistence and daily milk
consumption. Rural nonpastoralists are the remaining Turkana-county residents;
urban nonpastoralists are Laikipia-county residents. These are observational,
composite categories, not randomized interventions. BMI is kg/m2; TC/HDL are mg/dL
measured with venous EDTA blood and CardioChek Plus, not automatically fasting
central-laboratory values. The generation law is an ideal component model and
does not recover separate assay errors.

Published demographic cells total 1,360, while the reported sample is 1,226.
Both Agents rescaled the published cells under explicit assumptions. The source
Table 2 counts (BMI 1,198; TC and HDL 406 each) differ from this evaluation's
eligible available-case counts (1,189; 400; 405). The released file has 1,226 rows;
strict age >18 excludes nine. No fresh cohort was acquired for this evaluation.

## Inputs and scientific authorship

Each fresh GPT Agent received the research request, original-study evidence,
audited published aggregates, and access to search/read tools. Each searched
twice, read the original and an additional paper, authored a sampling program,
examined one generated-data trial, and retained the initial law. All three final
seeds per law were sampled after closure. No new real-reference coefficient or
old project generator was given to the author; the original published findings
were legal inputs. Source-rich reconstruction is therefore the interpretation.

A1's additional source: [PMC7347104](https://pmc.ncbi.nlm.nih.gov/articles/PMC7347104/).
The prior audit verified reported variability ratios as qualitative context,
not signed Turkana conditional coefficients. A2's additional source:
[Lee et al., rural Kenyan populations](https://pmc.ncbi.nlm.nih.gov/articles/PMC6435188/).
Its raw Maasai female/male HDL difference supplied a unit-converted numerical
anchor, but treating it as a conditional coefficient remains an assumption.

## Fixed analysis

Each trait uses age >18 and observed, finite, positive outcome values. The same
implementation is applied to the real reference and all six generated tables.
Outcome scaling uses that dataset's eligible pooled sample mean and sample SD.
One three-category OLS fit adjusts for age and sex; all three pairwise contrasts
use its full covariance. Raw units are retained alongside standardized effects.
A Gaussian ML LRT checks two added lifestyle-by-sex terms, at nominal p<0.05.
All nine additive and all eighteen sex-specific contrasts are retained per dataset.
Sex-specific fits use the same pooled scaling. Exploratory BH adjustment over
nine additive tests is not the original paper's eleven-outcome testing family.

These are explicit Methods-guided choices, not verified original-script details.
Conventional OLS intervals condition on the sample/model. Generated intervals do
not quantify source, structural or transport uncertainty. Three seeds per law
measure draw variation; two authors are not six independent clinical studies.

## Prior cases in optional/

The earlier brief contains the full selected ENSANUT pair and six lipid authors.
Its lipid residual correlation additionally adjusts for BMI and uses a different
case selection. The lifestyle task uses separate available-case outcomes. Do not
interchange their denominators or call the aggregate package a pooled validation.

## Verification record

The lifestyle experiment's prior independent recomputation checked 189 contrasts
and 21 LRTs (5,846 checks; 4,690 numerical comparisons; largest difference
8.52e-13). It checked arithmetic and artifact integrity, not clinical validity.
Both frozen laws have positive conditional means, finite first/second moments
and positive HDL/non-HDL construction under the declared support. These are
law-specific properties, not evidence that their joint distribution is correct.
This packet exports existing reviewed aggregates only. No human domain feedback
has yet been collected. Original frozen files and manuscript remain unchanged.
