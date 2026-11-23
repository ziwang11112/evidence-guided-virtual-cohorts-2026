# Did the generated pairs respect the study's published joint counts?

The five delivered generators each explicitly acknowledged in their final decision record that their construction did not reproduce the BMI-category cross-tabulation. Review of each selected program confirmed that none calibrated its paired distribution to the 16 published category counts. All five retained their initial scientific model at review. The sixth assigned author exhausted the provider's output-token limit in its design call and delivered no candidate. [Author records and checks](AUTHOR_AUDIT.json)

## One common source check on the frozen primary tables

A separate reviewer extracted the all-participant count matrix from Table 3 of the exact article projection. Rows identify the self-reported category and columns the measured category. The diagonal of the verified matrix sums to 2,462 of 2,781, or 88.53%. The reviewer applied the same category definitions to the two raw BMI columns in each of the 15 virtual primary tables, verifying each table's original hash. The real workbook played no part in this diagnostic. [Original article](https://doi.org/10.1371/journal.pone.0280483) · [All 16 cells, all seeds](CATEGORY_AUDIT.json)

| Author | Pairing assumption in its selected program | Same-category proportion across the three primary seeds |
|---|---|---:|
| a01 | Working Pearson correlation 0.93; alternatives 0.90 and 0.95 | 72.22–72.65% |
| a02 | Design call truncated before a valid program was produced | No table |
| a03 | Working Pearson correlation 0.93; alternatives 0.90 and 0.97 | 72.22–72.62% |
| a04 | Paired difference SD of 2 kg/m²; alternatives 1 and 3 | 73.14–73.69% |
| a05 | Working Pearson correlation 0.95; alternatives 0.90 and 0.98 | 76.27–76.51% |
| a06 | Interpreted ICC of 0.9289 through an assumed concordance formula to set covariance; one model | 72.29–72.61% |

Every primary table understated category agreement by 12.02–16.31 percentage points. For all 15 tables the largest individual cell error occurred among pairs classed as normal on both measures. The study reported 28.16% in this cell; the generated proportions were 14.45–16.06%. Marginal category frequencies also differed. Measured normal BMI accounted for 31.57% of participants in the study and 22.72–23.76% in the virtual tables. For reported normal BMI these percentages were 31.25% and 22.40–23.36%, respectively. Both distribution shape and pairing matter for reproducing these categories.

The primary classification uses continuous BMI with cutoffs of 18.5, 23 and 27.5 kg/m², with equality entering the higher group. Table 3 includes one obesity heading with a strict greater-than sign, although its row label and the study methods indicate inclusion at 27.5. No primary virtual BMI exactly equaled an unrounded cutoff. Rounding each virtual BMI to one decimal before classifying produced agreement ranging from 72.10% to 76.52%. This diagnostic was added after construction, with the real workbook withheld from the reviewer. It supplies evidence about adherence to available published constraints. The observed deficit cannot establish how much of a discrepancy on the individual two-unit endpoint a different construction would eliminate.
