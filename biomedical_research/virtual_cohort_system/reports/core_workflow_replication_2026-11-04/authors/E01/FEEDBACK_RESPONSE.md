# E01 final choice: retain initial

I reviewed the actual combined feedback for e01_initial_8100 and verified its SHA-256 as `15aeab839b1e9a8419fdd7aa5f098ff8fb09a705a21f10c5b4f29cde1dbc62af`. The selected candidate is the unchanged frozen `candidates/initial`, freeze hash `de80010ffd3f678fec1b0facc98a7f00a7d2ca098adf53007be33923afd667a8`. No scientific revision is requested.

The feedback reports verified output linkage, 3,000 valid rows, exactly375 in each age/sex cell, no duplicate measurement rows and all requested analyses computable with ranks5/4/5. I reviewed all three analysis estimates, the Q2–Q3 difference, glucose association and residual-RMS diagnostics, all supplied marginal mean/SD/quantiles, the six available source comparisons and fourteen unavailable checks. Own-run coefficients are .09808082, .10462077 and .08748243 in their requested units. These are implementation outputs, not target estimates or evidence of empirical validity.

The six approximate Kerman comparisons use 2,682 generated observations aged at most75. They do not reconstruct the source's population. A constant-only calculation of the frozen law, enumerating distinct integer age support values rather than individuals, gives the following population moments under that same observable range:

| Quantity | Source report | Trial8100 | Frozen-law population moment |
|---|---:|---:|---:|
| Age mean,years |43.8|51.13311|51.25|
| Female proportion |.56381|.49478|.5|
| BMI SD,kg/m² |3.8|3.83556|3.8|
| Glucose mean,mg/dL |91.2|92.90588|93.03492|
| Glucose SD,mg/dL |12.4|13.33487|13.05063|
| Raw glucose–HbA1c Pearson r |.23|.32001|.33137|

The model moments are not expected finite-sample SD/correlation estimates. No calibrated Monte Carlo interval was computed. Remaining differences between a single trial and its model moments can include sampling variation; their precise attribution is unassessed and is not a reason to tune to this seed.

The age/sex mismatches are predominantly imposed by equal-cell design and the restricted age range, so matching the Kerman demographic distribution would violate the intended design. The glucose center and dispersion shifts follow the model's demographic effects and its assumption that12.4 is a residual scale, not a transported target marginal SD. Similarly, the proposal explicitly uses raw source Pearson.23 as an assumed age/sex-residual correlation. The same law therefore implies raw correlation.33137 after adding shared demographic variation. The trial's.32001 is not an implementation attempt to reproduce source raw.23. Changing the law just to erase this discrepancy would silently replace the predeclared conditioning choice. The feedback does expose how consequential that unsupported choice is; it does not identify which source-to-target conditional law is correct.

The fourteen unavailable checks remain unavailable: NHANES weighted quantities, Finnish weighted R-squared/predictive margins with binary-age and fasting-time adjustment, Taiwanese male-variable conversion, and unresolved Kerman printed slopes. None is relabeled as an available unweighted comparison. Their absence limits the model's empirical assessment.

All original limitations remain: no Mexico source, different diagnosis/fasting/HbA1c selections and assays, uncertain plasma/serum transport, residual scales/correlations combined across cohorts, assumed positive signs and binary-to-continuous-age transfer, and assumed tails/families/absence of interactions. Retaining this sensitivity construction does not establish causal effects, clinical suitability, person-level recovery or validity of unassessed analyses.

The controller reported a mechanical pre-freeze rename of the reserved Windows folder name `aux` to `review_artifacts`, with checks paths/record updated and scientific files unchanged. I did not modify the frozen candidate. An attempted read of the mechanical receipt at the bundle root failed because it was not at that path; no alternate experiment location was inspected. The source feedback hash and frozen specification hash were verified directly. Acquisition remains closed. No new source, target reference, other-author value, final-delivery row, random draw or local generator execution was used in this decision. FINAL_DECISION.json binds the actual feedback while preserving the initial candidate unchanged.
