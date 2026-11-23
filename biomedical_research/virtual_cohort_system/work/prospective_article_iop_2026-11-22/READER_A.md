# Original article evidence key, reader A

22 November 2026. I used David C. Pye's PLOS ONE article and publisher JATS tables. I did not open the participant workbook or figure pixels, digitize figures, estimate the measured threshold frequency or inspect constructor output. The text and table readings below precede the modeling run.

## Population and measurements

Healthy optometry school students and staff in Sydney, aged 17–30 years. Each observation in the published analysis is the left eye of one participant. The investigators averaged three readings per instrument, with Pascal readings of Q3 quality or higher. Both eyes were measured, and the paper analyzes just the left eye. Explicitly distinguish measured dynamic contour pressure (Pascal DCT or PDCT) and measured Goldmann applanation pressure (IOPG) from calculated IOPTcalc. Pressure units are mmHg. Methods excluded ocular/systemic disease and relevant eye conditions. These volunteers do not represent a glaucoma population. [Original study, methods and Tables 1–2](https://doi.org/10.1371/journal.pone.0224824)

## Direct source values that matter for the request

| Quantity | Reported source value | Location |
|---|---:|---|
| Participants | 100 | Table 1 |
| Pascal pressure, mean and SD | 16.89 and 2.49 mmHg | Table 1 and abstract |
| Goldmann pressure, mean and SD | 15.06 and 2.71 mmHg | Table 1 and abstract |
| Pearson correlation of the two measured pressures | 0.5969, also rendered 0.598 and 0.597 | Results, Intercorrelation of parameters, and Fig. 3A caption. Table 2 gives significance only. The printed values differ slightly. |
| Participants with pressure readings differing by at least 4 mmHg | 19 of 100 | Discussion, Goldmann vs Pascal DCT tonometry. The wording identifies an unsigned discrepancy. The direction is usually Pascal higher, with no exact directional split. |

Table 1 provides the contextual quantities 42 men and 58 women, age 21.07 (SD 2.94) years, central corneal curvature 7.75 (SD 0.26) mm and central corneal thickness 549.9 (SD 32.8) µm. These do not enter either requested unadjusted estimator.

## Estimands and review limits

1. Let D be measured Pascal minus measured Goldmann, one pair per left eye. The arithmetic mean D follows from the two Table 1 means, giving 1.83 mmHg at their printed centers. Absolute uncertainty from independent rounding of the two displayed means is at most 0.01 mmHg, before considering finite sampling. The Discussion gives the group difference as 1.8 mmHg. The nearby 1.99 mmHg concerns Pascal versus a calculated pressure and cannot substitute.
2. The same pairs determine the percentage for which D is strictly greater than 3 mmHg. Its value is not explicitly tabulated in the reviewed text or tables. A count for |D| ≥4 is informative about the tails but does not determine the requested one-sided count. Measurements exactly at 3 are excluded. The two SDs and measured Pearson correlation also constrain var(D) by the variance-of-a-difference identity. They do not identify the full distribution of D. A constructor may choose an additional model or present alternate compatible examples.
3. Figure 3A depicts paired Pascal and Goldmann measurements. The evaluation concerns the prespecified textual/tables/captions representation. A reader with access to scatterplot pixels can potentially obtain further information, subject to overlap and digitization error. Source compatibility in a scenario needs independent assessment of both marginals, measured correlation and the absolute-tail count. More permissive numerical tolerances or target utility criteria should be labeled as protocol choices.

The publisher lists S1 as individual bilateral data and marks the paper CC BY. The supplement supplies the withheld same-study reference. Within-study verification addresses utility for this sample, with no independent population transfer claim. Any discrepancy between printed and workbook summaries remains unknown at this stage. [Article and supporting information](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0224824) · [S1 dataset landing page](https://doi.org/10.1371/journal.pone.0224824.s001)
