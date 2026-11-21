# Which Scientific Analyses Can Agent-Generated Biomedical Cohorts Support?

KDD Research working manuscript v0.42, 21 November 2026. An agent can generate different virtual cohorts that satisfy the same published evidence. This release tests whether knowing how much the results change across those cohorts helps a researcher choose an analysis before seeing a new study's measurements. [External review PDF](external_review.pdf) · [Anonymous PDF](paper.pdf) · [Anonymous Overleaf source](overleaf_v42.zip) · [External review Overleaf source](overleaf_external_review_v42.zip)

## Read the main figures

| Figure | Question | What the experiment shows |
|---|---|---|
| 1, p. 2 | What does an agent actually decide? | Four published iron-status counts determine the threshold odds. Several assignments of continuous values to the same individuals preserve those counts and change the rank correlation. |
| 2, p. 3 | Can virtual records support a published regression? | The adjusted urban–pastoralist BMI contrast is close on the scale of two real resamples. The rural cholesterol contrast is understated. |
| 3, p. 6 | Does the agent's choice of pairing improve a measured relationship? | For all six CHNS laws, the agent's iron pairing brought the continuous correlation closer to the community holdout. Reassigning ages had little effect on the Kenyan lifestyle BMI contrast. |
| 4, p. 7 | Does agreement with a statistical generator establish that the screening fraction is determined? | The two initial predictions were 25.53% and 25.52%. Each of four agents later implemented two alternatives under the same evidence, producing differences of 16.37–29.35 percentage points. |
| 5, p. 7 | Did anyone identify the most fragile use before seeing the Virginia sample? | All four advisers with the scenario ranges put the eventual largest error last. All four seeing the base packet placed it fifth. The statistical rule matched the full arm. At the primary choice of two uses, all rankings agreed and neither use was confirmed within its tolerance. |
| 14, p. 19 | Could reassigning the same HDL values across individuals reach the Virginia result? | The measured screening fraction exceeded even the unrestricted pairing bound. Its sampling interval overlapped the bound. Higher total cholesterol accounted for most of the shift in mean non-HDL. |

The Virginia results use one external study with 400 eligible adults and eight pre-disclosure decisions by one model. The screening comparison at coverage five is a secondary result chosen for discussion after examining the registered coverage curve. The two Ethiopian recruitment frames were available during advising. The subsequent diagnostic on all three samples used no new target for validation. [Complete decision study](../../work/prospective_lipid_use_2026-11-21/RESULTS.md) · [Time-stamped advisor outputs](../../work/prospective_lipid_use_2026-11-21/DECISION_CLOSURE.json) · [All analyses and decision coverages](../../work/prospective_lipid_use_2026-11-21/RESULTS.json) · [Exposure registry](../../docs/DATASET_EXPOSURE_REGISTRY.md)

## Reproduce and inspect

The build contains 14 figures and seven tables. References begin on page eight, followed by the appendix on page nine. The two Overleaf packages compile with `main.tex` as the root. Both were built from a fresh extraction, all cross-references resolved and the scientific body rendered identically in the anonymous and linked editions. [Anonymous build receipt](BUILD_CHECK.json) · [External edition receipt](EXTERNAL_REVIEW_CHECK.json)

From the project root, run `python -B work/prospective_lipid_use_2026-11-21/verify.py --public-only` for all rankings, six estimates' decision scores, coverage and costs. Run `python -B work/prospective_lipid_use_2026-11-21/check_pairing_public.py` for the cross-study bound comparison. The original study hosts its public data. The full reference checker uses the native S serialization and a separate bootstrap implementation. [Human study archive](https://hbiostat.org/data/repo/diabetes) · [Verification receipt](../../work/prospective_lipid_use_2026-11-21/VERIFICATION.json) · [Previous manuscript and checks](../kdd_draft_v41_2026-11-20/README.md)
