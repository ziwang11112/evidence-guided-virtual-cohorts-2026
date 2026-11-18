# Controller's independent visual and scientific review

This review used the admitted original-source supplement, its local LibreOffice conversion, all six Poppler-rendered pages, and the previously admitted parent article. It did not read target outcomes or participant/generated rows. It was performed in parallel with the source-only author's extraction.

## Direct checks

- Page 1, Table S1, General population, `Age + sex + BMI` block: intercept 4.2966; age 30–44 versus 45–64: −0.1985; men versus women: 0.2472; BMI: **0.0240**, p **<0.0001**.
- Page 2, Table S2, same population/block: intercept 5.1281; age 30–44 versus 45–64: **−0.1120**; men versus women: **−0.0230**, p 0.2884; BMI: **0.0125**, p **<0.0001**.
- The table columns are beta and p-value. There are no printed coefficient SEs or confidence intervals. A thresholded p-value is not an exact SE or a participant residual SD.
- The source tables contain separately fitted anthropometric blocks. S2 does not contain a glucose-adjusted BMI coefficient. All four tables (S1–S4) lack a residual HbA1c SD/covariance sufficient for that adjustment.
- Table S1's WHtR/WHR row labels conflict with their model-block labels. The same conflict is visible on the rendered page; it is not a text-extraction shift. It is outside the prespecified BMI extraction and must not be silently repaired or used to invalidate the unrelated BMI cells.
- Tables S3 and S4 flow onto pages 4 and 6. Page 5 wraps one unrelated coefficient (−0.02174) over two lines. Structured DOCX extraction preserves it as one cell. No main BMI cell is clipped. The DOCX table numbering is sequential but S1's caption occurs after the first table in extracted body order; page identity and the visible caption establish S1 association.

## Units and applicability

The main article defines BMI in kg/m² and fasting glucose in mmol/L. The main Table 1 reports HbA1c in **both mmol/mol and percent**. S2 itself does not state which HbA1c scale applies to its regression coefficients. Its approximately 5-valued intercepts strongly support a percent-scale interpretation but do not constitute an explicit printed unit label. Therefore:

- `0.0125 × 5 = 0.0625` is an exact predictor rescaling in S2's same outcome units for the same source model.
- Calling that 0.0625 **percentage points** requires the recorded percent-scale interpretation. It is not a fully verified unit conversion or a target population estimate.
- A future Agent may use that interpretation as an explicit working assumption, check consistency against the source's descriptive measurements, and expose sensitivity. It must not present an inferred unit as directly reported. This limited ambiguity is not a reason to discard all numerical evidence or stop the project.

Methods specify a 30–64-year-old, complete-case, diabetes-excluded sample, with fasting 4–17 hours. The Finnish reference subgroup has n=653 and is drawn from Health 2011 participants in the cities corresponding to Maamu, not the entire unfiltered national sample. Age is binary, whereas E01 uses continuous age; source survey weights and equal-cell target projection weights differ. Exclusions include HbA1c ≥6.5% as well as glucose ≥7 mmol/L and diagnosed/treated diabetes. That outcome-based selection must not be dropped during transport.

The article says fasting glucose analyses also adjust for fasting duration, but the S1 printed design block/rows show only age, sex and BMI. Record the stated fasting adjustment and the incomplete printed specification separately. Do not silently assert the coefficient belongs to a fully known three-predictor model. Serum glucose is used in the Finnish subgroup; migrant subgroups use a different sample matrix. Their estimates are not automatically interchangeable.

## Consequence

The action supplies a real signed BMI association with a numerical magnitude, which the old packet's R² alone did not supply. It partially improves the basis for the source analogue of Q2. It does not identify Q3 (additional glucose adjustment), conditional individual variation, continuous age response, source uncertainty, or transport to the target. No generated-data improvement has been measured. The appropriate continuation is a source-informed development construction with these assumptions visible, not forced matching to exposed target outcomes.

After the independent extraction, the root also read the frozen static E01 proposal/specification (no execution or row data). That proposal already assumed the positive roots giving rBH=0.2322960527 and rBG=0.2302719109. The supplement supports the formerly assumed signs; it does not change those existing numerical partial-correlation choices. The magnitude/scale information could motivate a different source mapping, but a scientific change is not automatic and must not be forced. This comparison does not reopen the old model.
