# Independent development evaluator for the iron study

Evaluator access only. The inputs to the constructor exclude this directory and the older case-specific requests, loaders and scorers. This key was read directly from the original article text, with the existing source audit as a cross-check. It implements an independent calculation. The development case was already exposed to project investigators.

Zhu et al. studied 1,671 nonpregnant, nonlactating women in Xianghe, China. The clinical thresholds in this development task are Hb strictly below 120 g/L and plasma ferritin strictly below 15 µg/L. The abstract and the footnotes to Tables II, III, IV and V support these units. Table I's ferritin label and a methods line are inconsistent with these other passages. Record how the constructor resolved the discrepancy. [Original article](https://doi.org/10.1024/0300-9831/a000014)

| Anchor | What can be checked |
|---|---|
| Table I, p. 147 | Geometric means of Hb and plasma ferritin. The displayed interval gives no individual Hb–ferritin pairing. |
| Table III, p. 150 | Counts in three Hb bands, within-band ferritin geometric means and percentages depleted. These are additional constraints on the same two continuous variables. |
| Table IV, p. 150 | Collapse eight folate/B12/ferritin categories by ferritin depletion. Among anemic women the depleted/replete counts are 173/85. Among nonanemic women they are 331/1082. These determine the source-sample crude odds ratio. |
| Table V, p. 151 | The multivariable logistic coefficient for iron depletion gives an adjusted odds ratio of 6.448. The covariates shown are folate, vitamin B12, BMI, age and education. |
| Table II and Results | A Pearson correlation of 0.16 belongs to folate and vitamin B12. The article supplies no numerical individual-level continuous Hb–ferritin Spearman coefficient. |

The reference is a published sample. Different synthetic sample sizes are accommodated by comparing joint cell proportions, effects and within-band summaries. Signed differences use the printed geometric means and percentages. Those are rounded. Report numerical discrepancies descriptively with the generating design and seeds. There is no target numerical score for the virtual correlation. Two demonstrably admissible configurations can witness sensitivity without establishing sharp bounds or their likelihood in the original population.

Run `python iron.py canonical.csv --output aggregate.json`. The input must contain normalized columns `hb_g_l` and `ferritin_ug_l`. Confirm units and conversion against the author's deposited model before using this interface. A descriptive source claim can optionally be transcribed into the `--claims` input following `test_iron.py`. Supply only explicit claims made by the constructor and record the submission path and location of each transcription separately. Missing fields generate no claim score. The independent row audit runs even when the author did not explicitly state a source estimate.

Run `python -m unittest -v test_iron` in this directory to test the evaluation operator with a deterministic artificial fixture. A correct alternative derivation uses the odds of anemia within each depletion group. Mutations replace the crude estimate with the adjusted one or relabel a threshold without rescaling it. The fixture also checks boundary equality, ties, invalid rows, zero denominators and changes in generated sample size. Outputs contain summary metrics only.
