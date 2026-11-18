# Biological interpretation of two existing virtual-cohort cases

11 November 2026. **These cases support exploratory, analysis-specific virtual data: Q4 demonstrates a useful change-of-adjustment pattern; the current lipid case demonstrates substantive construction alongside unresolved joint-distribution limitations. Neither establishes a replacement for measured participants.**

This aggregate-only review read v0.30 Sections 5.1/5.3/5.11 and S3/S16/S22/S23, Q4 source/proposal reviews, the repeatability results and source/code audit. Three targeted published studies/methods papers were checked online. No participant records, generation, refitting, model API or new dataset acquisition was used. This is a methodological interpretation, not a clinician's completed review.

## 1. Q4 ENSANUT: what the retained pattern means

The same virtual records support two BMI-HbA1c regressions: adjustment for age/sex, then additional glucose adjustment. E01 changes from **0.09165 to 0.07509**, E02 from **0.07140 to 0.04733**, versus **0.08364 to 0.05664** in the selected sample reference. Units are HbA1c percentage points per 5 kg/m² BMI. Each of the six generated tables retained attenuation.

This is useful evidence that the constructed joint distribution supports a scientific question involving different conditioning sets. It does **not** show that glucose mediates an obesity effect, that the smaller coefficient is the true direct effect, or that the removed fraction has a biological causal interpretation. Changing adjustment changes the estimand; causal interpretations require an appropriate causal structure and identification assumptions. This distinction follows the methodological treatment of intermediates and adjustment in [Schisterman, Cole and Platt (2009)](https://pmc.ncbi.nlm.nih.gov/articles/PMC2744485/). Here, the observed contrast is an associational model comparison.

The target is unusually specific: 6,931 selected adults aged 25-79, no reported prior diabetes diagnosis, recorded 8-12-hour fast, serum glucose below 126 mg/dL, and equal mass across eight sex/age cells. It is **not** the national ENSANUT population; medication and anemia exclusions were not verified. These facts come from the existing project eligibility/method record, not a new source audit.

Source transfer remains substantive. Both authors used Huang et al.: Taiwanese participants aged 30-70 without prior diabetes diagnosis, with nonuniversal fasting; its cited regression adjusts for age and sex, not BMI and glucose. Thus its sex coefficient cannot become a fully adjusted Mexican coefficient merely by citation. This was directly verified in [Huang et al., Methods and Table 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC8038122/). E01 additionally converts marginal evidence into residual quantities; E02 uses an ecological HGI-derived guide. The existing independent source reviews correctly label these as assumptions/derivations.

**Use supported:** exploring the specified adjustment pattern and inspecting how evidence-based modeling choices affect it. **Use not established:** causal mediation, individual HbA1c recovery, diagnostic classification or calibrated intervention analysis.

## 2. Dispersion is part of the intended use

Q4 ENSANUT residual RMS is **0.295/0.324 versus 0.488** percentage points; total HbA1c SD is **0.362/0.406 versus 0.527**. These are individual/residual variation, not uncertainty in a coefficient. They qualify the usefulness of the otherwise retained pattern.

For a regression demonstration, a useful coefficient pattern can coexist with imperfect spread. For power calculations, prediction intervals, subgroup extremes or prevalence estimation, that same mismatch is directly relevant. Under a fixed-design linear model, coefficient variance depends on residual variance and predictor geometry; generating more rows can make the simulated estimate more precise without improving either the evidence or its transfer. Hence any design exercise must be described as conditional on the chosen law, not calibrated to real recruitment. Effect magnitudes should remain in native units, alongside spread, without converting interval overlap into an equivalence verdict.

## 3. Lipids: measured quantities versus an ideal component model

The original Turkana study sampled adults across pastoralist, rural nonpastoralist and urban settings. Its supplement confirms EDTA venous blood and immediate CardioChek Plus measurement of **TC, HDL and triglycerides**; LDL was calculated. Nonfasting participants were retained, with fasting status recorded. See [Lea et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC7577730/) and [supplement, biomarker methods pp. 5-6](https://gurven.anth.ucsb.edu/sites/default/files/sitefiles/papers/lea%20et%20al.%202020%20supplement.pdf). Our 397-person complete-case reference and age/sex/BMI-adjusted residual correlation are project-defined analyses, not a reproduction of the paper's lifestyle estimand.

Current constructors give residual TC-HDL correlation **0.146-0.423 versus 0.512**, and HDL SD **11.38-13.18 versus 20.18 mg/dL**. They can illustrate alternative lipid-association scenarios, but joint-tail analyses, co-occurrence and individualized risk uses are not established by these results. The broad TC-slope reference interval includes zero; its positive point estimate is not a confirmed population direction.

Constructing `TC = HDL + non-HDL`, with positive components, guarantees ordering **within an ideal concentration model**. It does not establish the covariance of separate measured outputs or an assay-error model. The measured protocol alone does not certify exact observed ordering; the review did not estimate its assay error or explain an individual ordering violation. Conversely, a shared component does not identify residual correlation: component covariance, covariate composition and measurement errors remain relevant. Neither component positivity nor finite moments proves adequate scientific analysis. The observed lipid mismatch should remain visible even when mathematical repair succeeds.

## 4. Questions for the biomedical reader

For **each** requested analysis, ask the same short questions and retain unfavorable answers:

1. What precise exploratory question could these virtual records inform, and what would be an overclaim?
2. Do the population, fasting, specimen, assay and adjustment definitions fit that use? Which bridge is least defensible?
3. Do the effect magnitude and residual/spread discrepancies materially change that use? Explain in native units, without retrospectively choosing a pass threshold.
4. For glycemia, is the noncausal adjustment interpretation clear? For lipids, is an ideal component model an acceptable approximation to the intended measured endpoint?
5. What missing evidence would change the judgment, rather than simply increase the synthetic sample size?

Provide the complete two-case profiles, source/assumption summaries and these questions; do not provide only favorable panels. A friend's response is qualitative domain interpretation, not clinical validation, a powered user study or measured efficiency improvement.

**Access scope:** Huang full HTML Methods/Table 1 were available. Lea main text and the author-hosted original supplement were available; publisher DOI access returned 403. Schisterman's abstract and indexed full-text methodological sections were accessible, while a direct PMC request intermittently returned a challenge page. Other cited construction-source details were checked against existing audited local notes, not newly reread originals. Source links, local hashes and these limits are retained in `SOURCE_LEDGER.json`.
