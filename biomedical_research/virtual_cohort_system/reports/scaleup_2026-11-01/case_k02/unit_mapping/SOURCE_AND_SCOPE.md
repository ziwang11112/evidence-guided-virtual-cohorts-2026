# K02: explicit cholesterol unit representation

2 November 2026. This mapping is a pre-outcome representation decision, not an assay calibration or clinical release.

The official NCBI Bookshelf page for **Appendix A: Lipid Conversion Factors**, in the AHRQ report *Screening and Treatment of Subclinical Hypothyroidism or Hyperthyroidism*, explicitly specifies multiplication by **38.67** when converting total, HDL and LDL cholesterol from mmol/L to mg/dL. Root inspected that appendix in a new **wang Chrome extension** tab. The independent reviewer separately opened and verified the same appendix in their own wang Chrome tab. [Official appendix](https://www.ncbi.nlm.nih.gov/books/NBK83505/).

Only total and HDL cholesterol are used here. Source and target generator contexts retain mmol/L; the target analysis receives a separate numeric view in mg/dL. No rounding is applied. IDs, age, sex and BMI remain unchanged. This published, rounded conversion convention is fixed for the campaign's K02 representation; it is not estimated from target records. The reverse conversion is unnecessary for this workflow.

`INPUT_CONTRACT.json` and `OUTPUT_CONTRACT.json` declare the full ordered schema. `PROPOSAL.json` deliberately contains no approval. An independent reviewer must bind the proposal digest, both contracts and the actual task template before creating a separately named approved manifest. Any change of columns, units, analyte, factor or numeric types requires renewed binding. No candidate, generated table or target effect has been inspected or converted in preparing these files.

The caller must verify actual generator execution and task correspondence before invoking the existing pure conversion adapter. The manifest alone does not convert values or establish execution linkage. The source-feedback path uses the original mmol/L data, including any row-wise non-HDL derivation. The frozen target analysis specification already expects mg/dL and performs its own prespecified eligibility accounting.

This conversion does **not** correct CardioChek versus central laboratory measurements, EDTA versus another specimen, fasting differences, selection differences, or source-to-target transfer. Those differences remain scientific assumptions or limitations in the model record. No participant-level residual variance, regression parameter or target relationship is introduced by the conversion.

This was a unit-reference check, not a new original empirical study or target-family admission. No external file was saved; browser traffic was unmetered. The cumulative saved-download ledger is unchanged.
