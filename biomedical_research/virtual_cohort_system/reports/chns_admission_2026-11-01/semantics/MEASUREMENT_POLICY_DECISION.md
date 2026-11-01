# Bounded CHNS measurement-policy decision

1 November 2026. This prospectively selected policy resolves the current dictionary gate for a **conditional analysis of the released data**, subject to independent F2 review. It does not certify the release, recover every undocumented missing code, select target-fitted thresholds or admit a generator. It supersedes the earlier draft's requirement for an exhaustive field-specific sentinel catalogue before any progress.

## Newly recovered definitions

Using the existing official paired examination codebook, the coordinator isolated page-specific code/category columns on pp. 1–2 and visually checked the resulting crops. A second reviewer independently checked those crops. [CODEBOOK_CODE_MAP.json](CODEBOOK_CODE_MAP.json) records the supported subset. In particular:

- Height and weight flag 9 means the value was designated implausible and set missing.
- Height flag 11 means average-height replacement; weight flag 4 means extrapolation.
- Weight flag 2 records an apparent-Jin interpretation and a conversion to kg already made by the release. It does not prove the original units were Jin. Do not divide the released weight again.
- Several other positive flags identify corrections or accepted extreme BMI. Discarding all positive flags would remove values the release retained as acceptable.
- `**OTHER**` is a format fallback category, not a numeric code and not a certificate for missing/unlisted flags.

The native age-missing definition and gender 1/2 categories were rechecked in isolated definition cells. Height/weight continuous rows did not reveal a field-specific numeric sentinel list. No current biomarker numeric-missing map was established by the older incompatible biomarker dictionary.

The [bounded official lookup](OFFICIAL_FORMAT_LOOKUP.md) examined three official documentation/release pages, including the complete lists of 54 individual-level files and the single biomarker file. No separate format catalogue/program or additional field-level sentinel rules were listed. No extra file or original study was downloaded/read. This ends broad dictionary searching for this unit; it does not prove no definition exists anywhere.

## Chosen reference policy

The eventual reference is an **age/wave/linkage/availability-selected sample from the public CHNS release**. It is not an unqualified all-comers, untreated, nondiabetic, nonpregnant or national-population reference. Age boundaries, common-versus-analysis-specific complete cases and final measurement selection still belong in F2, before clinical values are evaluated. No treatment or pregnancy exclusions are added merely because they appear in some source studies.

| Required component | Prospective handling | Evidence/assumption status |
|---|---|---|
| Native missingness | Preserve reader-recognized native missing; keep exposed missing-reason metadata when available. Do not fill target values. | Standard file decoding plus documented age `.` definition. No claim that all missing reasons survive decoding. |
| `GENDER` | Retain only documented categories 1/2 for projections requiring this variable; other/missing codes make that projection unavailable for the row. | Documented categories. No interpretation of every non-1 value as female. |
| `age` | Use the released age in years. Do not reconstruct age from birth year or pretend the rounding/reference date is known. | Documented released measure; timing/rounding limitation retained. |
| `HEIGHT`, `WEIGHT` | Preserve released cm/kg values and cleaning flags. If the corresponding flag is exactly 9, make the measurement unavailable. Do not repeat correction/conversion. Retain released average-height/extrapolated/corrected values, labelled as such in reference provenance. | Documented code subset plus an explicit released-data policy; not proof of original raw measurements. |
| Derived BMI | Compute kg/(cm/100)^2 only for finite, strictly positive height and weight; reject a nonfinite result. These are physical measurement-domain checks with a defined BMI denominator, not empirical percentile filters. | Algebraic definition. No target-fitted plausible-range cutoffs or winsorization. |
| `GLUCOSE`, `HbA1c` | Use finite released values of current non-field glucose in mmol/L and HbA1c in %. Preserve their serum/whole-blood measurement identities. Do not substitute field glucose or legacy names. Nonpositive values trigger the prespecified interpretation check below, not automatic missing-value recoding. | Current labels and assay metadata. OLS does not require positivity, and zero/below-detection semantics are not established by these metadata. |
| Undocumented numerical sentinels | Do not impose a universal 88/99/888 mask. Other finite values remain released measurements under a stated residual release-quality assumption. | Explicit assumption, not documented absence of positive sentinel codes. |
| Unknown cleaning flags | Preserve them and disclose them; do not certify them as clean or reinterpret OTHER as a numeric map. | Residual release-quality limitation. Any essential contradictory coding discovered at evaluation triggers the failure rule below. |

Under this policy, unknown individual fasting adherence, incomplete instrument comparability, different blood/examination timing and unrepresented source exclusions remain applicability/measurement assumptions. They are not silently resolved, but they need not block an explicitly conditional released-data analysis. Unknown actual units, field identity or a required category meaning would still block the affected quantity.

The constructor receives intended population/measurement definitions and admitted external evidence only. It receives no reference rows, clinical moments, coded-value counts, availability counts or completed reference analysis. The released-data policy is not a licence to choose parameters from CHNS summaries.

## Single-stage quality failure rule

After the protocol and candidates freeze, the custodian may apply the frozen decoding and report missingness/flag/eligibility diagnostics alongside the planned analyses. A nonpositive glycemic value triggers a measurement-interpretation check **before affected effect calculations**: do not presume that zero is a missing code, a detection-limit value or a valid physiological concentration. If interpretation cannot be supported by approved measurement documentation, withhold the affected analysis or stop the case rather than try convenient recodings. The same rule applies to other essential newly encountered coding contradictions. Do not try alternative recodings to improve source agreement, change the target population after seeing effects, or call a repaired post-reveal result fresh confirmation. Retained corrected/imputed measurements and uncertain sampling interpretation must remain in the result limitations.

This decision permits a test under declared assumptions; it does not guarantee interpretable data or a positive result. An exhaustive missing-code catalogue and a fully identified joint distribution are not required, whereas truthful measurement definitions, fixed handling and honest failure reporting are.

## Information exposure and costs

One initial layout probe repeated an already exposed identifier-column summary on examination p. 1. A fixed-width attempt on p. 2 also displayed leading fragments of cleaning-flag summaries because that page's column grid differs from p. 1. No values are repeated or used here. The final extraction uses each page's exact header-grid boundaries and code/category-only crops; no clinical value, clinical moment, joint relationship or participant row was accessed. These metadata-document exposures do not reset prior exposure. Full codebooks and crop images stay local.

New file-transfer bytes: 0. New original-study reads: 0. Previous source quota remains 2/6. No old frozen module or receipt changed, and no biomedical table was generated.
