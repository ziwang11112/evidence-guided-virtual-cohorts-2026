# External original-evidence audit

Completed 2026-11-09 for the admitted PNS BP task; source-only. No target rows, means, correlations, slopes, unused outcomes, generated candidates or evaluation results were accessed. The public numerical data in this audit concern external source populations only.

## Decision

**Minimal packet adequate for evidence-informed construction with explicit nonidentification; inadequate to identify the target joint distribution or guarantee the three validation endpoints.** Two original families supply numeric anchors: INTERSALT supplies a BMI association and body/BP scales; Beijing supplies same-sample SBP/DBP/PP moments. INTERMAP adds a clearly documented, different measurement context. Stop at these three families; no fourth study or broader search is needed merely to manufacture a reported residual correlation.

The deliverable for construction is `AUTHOR_SAFE_EVIDENCE_PACKET.md`, with machine-readable facts in `AUTHOR_SAFE_EVIDENCE_PACKET.json`. It prescribes no model parameters, scoring cutoffs or tuning rule. Original files remain under `_local_only/sources`; `SOURCE_ARTIFACT_REGISTRY.json` records bytes, SHA256, origin and content status, including unsuccessful downloads. A CAPTCHA/error payload is not labelled full text.

## Verification and admissibility

| Source/family | What was actually read | Admitted use | Important limit |
|---|---|---|---|
| INTERSALT, original BMJ1988, DOI10.1136/bmj.297.6644.319 | All10 original page scans, pp319–328; methods319–321; TableII322; AppendixII327 and its footnote | Reported BMI coefficients/SEs; labelled age/sex-group-averaged descriptive scales | Adjusted within-centre observational coefficients; not the target weighted age/sex-only estimand. Averaged SDs are not pooled SDs. |
| Zhang2022, Beijing, DOI10.1111/jch.14529 / PMC9278591 | Full XML acquired; study selection, BP measurement, PP definition, statistical methods, Table1 and first results section checked | Marginal means/SDs and age-group context; algebraic raw covariance/correlation | Older, selected Chinese sample; no BMI term; no adjusted covariance; no exact source age range inferred. |
| Stamler2003, INTERMAP, DOI10.1038/sj.jhh.1001603 / PMC6660162 | Original web methods, design, descriptive tables and their definitions | Measurement/recruitment context and Table5 age/sex description | Original BP/BMI descriptive appendix not obtained. The main paper’s INTERSALT review tables are not a separate original dataset. |

Root independently checked INTERSALT TableII coefficient, SE and footnote against p322 and Beijing Table1 typed values. Three AppendixII examples were transcribed for readable context, not closeness to the unseen target; the complete page retains every centre. Do not treat those examples as a pooled source population.

## Access paths and rejected shortcuts

- Started with the three requested families. Dyer/Elliott1989 PMID2810326 was obtained as metadata/abstract only; its per10kg body-weight contrast is not substituted for a perBMI coefficient. No unverified table or CI from that paper is admitted.
- Hypertension1989 DOI10.1161/01.HYP.14.5.570 full text was inaccessible. The accessible original BMJ1988 report supplies TableII instead. These reports all concern INTERSALT and count as one family, not independent studies.
- INTERMAP publisher AppendixTables DOI10.1038/sj.jhh.1001634 showed subscription-only content; search snippets were not extracted as quantitative evidence. Its main-paper full web reading is documented, but a failed XML request, CAPTCHA HTML, BioC error and metadata-only efetch do not count as local full text.
- Beijing was downloaded through EuropePMC fullTextXML; INTERSALT scans through linked NCBI CDN page URLs. The original ten-page scan is the full-text copy, not just a table screenshot. Source receipts contain the obtained URLs and content hashes.
- No PNS or Brazilian National Health Survey outcome publication was queried or incorporated. Existing task measurement metadata is separate from this external generation-evidence packet.

## Estimand and uncertainty audit

INTERSALT TableII reports inverse-variance pooled within-centre coefficients with age, sex, urinary sodium/potassium and two alcohol indicators adjusted. Its SE quantifies uncertainty of that pooled source coefficient. Rescaling coefficient and SE by5 is transparent unit algebra, not refitting. Sampling uncertainty within that study does not cover different ages, countries, treatment patterns, outcome measurement or survey weighting.

Beijing Table1 reports SD rather than SE. The covariance identity uses three SDs calculated on a common group with PP defined as SBP−DBP. We verified common group Ns and this definition. Rounding the printed SDs prevents exact recovery; a ±0.005 SD rounding calculation is stored only as a numerical rounding envelope, explicitly not a sampling confidence interval. The derived covariance is raw. Residual covariance would also require the covariance of both outcomes with the same covariate vector and its covariance matrix, absent here. An age-stratum correlation still adjusts for neither continuous age nor sex/BMI.

INTERSALT AppendixII first computes each of four age/sex-group means and SDs and then averages them. Recovering an unconditional variance requires group weights, group means and group variances; an average SD is insufficient. No pooled covariance, normal distribution or homoscedastic residual has been inferred from the table.

## Remaining construction assumptions

The target age/sex/BMI distribution, BMI dependence with age/sex, conditional sex and age effects over20–79, age nonlinearities, treatment mix, residual scales, residual correlation, tails, and transport uncertainty remain incompletely or entirely unidentified. The original source facts can constrain plausible construction choices but do not uniquely determine them. The author must state choices and their evidence/assumption status before evaluation. The audit has not selected these choices.

Use the accompanying packet’s per-source contexts. Do not combine an older Beijing mean, a younger INTERSALT slope and an INTERMAP demographic balance as if jointly observed in one population. Successful validation remains an empirical question under the frozen protocol.
