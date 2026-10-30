# M15-A post hoc numerical evidence-basis audit

## Scope

This is a read-only descriptive inspection of the one already frozen, fully fictional 128-row table. It is not a new generation attempt, validation benchmark, clinical analysis or addition to the prespecified efficacy endpoints. The audit did not run the generator or frozen scorer and did not inspect real target participant data. Only the new `numeric_audit.py`, `numeric_audit.json` and this report were written.

The initial and final tables both retain SHA-256 `3e95264632fc2e9fd4e022147724b028c06c105eea753bee30eff4e435c915fb`, checked before and after inspection. There are 128 distinct IDs and no duplicated joint rows after ignoring ID. Absence of duplicates does not establish scientific validity.

## Main finding

The table has clear published marginal guidance, but strong within-group dependencies and perfectly symmetric urate marginal distributions that are author-selected. Their presence must not be described as recovered relationships or source-supported individual observations.

| Published descriptive stratum | n | BMI–urate Pearson r | BMI–urate Spearman rho | Age–urate Pearson r | Age–urate Spearman rho | Urate SD, mg/dL | Urate range, mg/dL |
|---|---:|---:|---:|---:|---:|---:|---|
| White male | 38 | 0.8152 | 0.7620 | 0.4246 | 0.3828 | 0.8571 | 4.2–8.0 |
| White female | 46 | 0.8991 | 0.9007 | 0.1174 | 0.0982 | 0.9843 | 2.5–6.5 |
| Black male | 19 | 0.9013 | 0.9088 | −0.0838 | −0.0816 | 1.0536 | 4.3–8.1 |
| Black female | 25 | 0.9354 | 0.9231 | −0.0582 | 0.0085 | 1.0824 | 2.7–6.5 |

These correlations are properties of the constructed table. The admitted excerpt contains no joint-relation estimate, and the builder explicitly declared positive BMI–urate ordering as a discretionary choice. This audit does not determine whether any displayed correlation agrees with the original cohort or a new target.

The age pattern is heterogeneous despite the builder's description of manually mixed ages: White males have Pearson r = 0.4246, whereas two other strata have slightly negative values. Manually mixing ages does not enforce or establish independence. The specification correctly avoids claiming that it does.

## Exact symmetry, dispersion and precision

Every urate value in each group has a reflected counterpart with the same multiplicity around that group's supplied mean. This is 38/38, 46/46, 19/19 and 25/25 mirror-matched observations; the odd-sized groups each have one value exactly at the center. Decimal arithmetic was used for the symmetry check. Thus all four empirical urate distributions are exactly symmetric around the supplied means, consistent with the builder's declared manual center-pairing construction.

This explains why exact agreement of the four urate means is achievable without having established empirical tails, spread or joint dependence. Exact symmetry is not itself prohibited or evidence of wrongdoing; it is an explicit unsupported construction choice in this source-only pilot.

Actual urate extrema match the four declared construction ranges. These were not source-derived physiological bounds. The original study's allowed age range is respected: observed group age ranges are 20–56, 20–56, 20–55 and 20–56 years. BMI ranges are 18.9–38.3, 15.9–40.1, 17.7–38.7 and 18.9–43.9 kg/m². There is no admitted empirical range or tail-shape comparator for BMI or urate.

Urate has 26/34/19/25 distinct values in the four groups. Integer age and one-decimal BMI/urate are authoring conventions, not evidence of original assay precision. Counts, extrema, distinct counts and correlations are reported descriptively without clinical p-values or inferential confidence intervals.

## Independent check of the earlier exploratory OLS

OLS with intercept, age, BMI, male indicator and Black indicator gives raw BMI coefficient 0.12010319308492791 mg/dL per kg/m², age coefficient 0.008397246713862827 mg/dL per year, descriptive R² = 0.8738772142783046, RSS = 25.214309667999206 and full design rank 5. These independently reproduce the earlier displayed estimates.

R² measures fit within this constructed table; it is not prediction accuracy or independent clinical agreement. The raw BMI slope must not be compared as an error against a differently adjusted standardized coefficient in the original paper. The original paper's relationship estimates were not admitted to the builder and cannot retrospectively be represented as inputs.

## Reproduction and boundary

Run `numeric_audit.py` using the existing Python environment with NumPy in its original local work-directory layout; paths are resolved relative to the script. An archived copy is auditable source code and is not a self-contained reproduction bundle because generated rows are not exported. Inputs are the unchanged initial/final fictional CSVs. The output JSON contains aggregate summaries only, with no row arrays, IDs, or individual records. This audit supplies no new feedback to the builder and recommends no numerical repair of the frozen table.
