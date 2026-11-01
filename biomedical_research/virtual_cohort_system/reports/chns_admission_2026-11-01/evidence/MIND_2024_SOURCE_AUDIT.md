# MIND-China 2024: source evidence and measurement audit

1 November 2026. Pending independent admission; not an approved construction packet. This is the second newly audited original in this bounded continuation, alongside Bao 2010. MIND-China is an external evidence source, not a fourth candidate target family. No source individual data were requested, and no CHNS clinical values or effects were accessed.

## Primary source and inspection

Wang et al., *Comparing glycemic traits in defining diabetes among rural Chinese older adults*, PLOS ONE, 2024, DOI [10.1371/journal.pone.0296694](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0296694). The main methods/results and original Tables 1–3 were read through the requested Chrome extension. Table 2 was inspected as the publisher's table image after a browser screenshot failed. Full papers/table images remain local. The source figures and cited original studies were not opened as additional reads.

## Population and measurement operators

The 2018 MIND-China baseline included 5,765 people aged at least 60 in 52 villages in Yanlou, Shandong. The 2019 follow-up invited a selected group excluding those aged at least 80 at baseline and people unable to complete follow-up. Of 3,817 completing follow-up, 242 missing laboratory measures and 28 missing diabetes-history information were excluded. The reported analysis comprises **3,547 people aged 61–80, free of dementia and functional disability**, including **425 with known diabetes history** and **3,122 without previous diagnosis**. This selection is not a representative national adult population. CHNS and MIND-China are distinct named sampling studies; participant-level non-overlap has not been established.

Demographics, lifestyle and BMI were collected in 2018, whereas blood testing occurred in April–May 2019. A cross-sectional equation with contemporaneous age/BMI is therefore not automatically the published observation operator. Overnight fasting is stated without an exact duration in the inspected paragraph. The methods say missing continuous variables were mean-filled and categorical variables mode-filled; numbers imputed by field are not supplied.

| Variable | Specimen, assay and timing | Permitted interpretation |
|---|---|---|
| FSG | Coagulant serum tube; centrifuged at 3,000 rpm for 10 minutes; glucose oxidase, CS-600B, local town laboratory, within two hours | Serum glucose in mmol/L under this specific handling protocol |
| FPG | Fluoride plasma tube; transported at 4°C to KingMed, Jinan; hexokinase, Beckman AU5821, same day | Plasma glucose in mmol/L; not an interchangeable name for FSG |
| HbA1c | EDTA whole blood; HPLC, Huizhong MQ6000; KingMed NGSP-certified laboratory; within two days | HbA1c percent. IFCC presentation is a scale conversion, not additional empirical evidence |

The paper provides paired serum/plasma evidence, but specimen, assay, site and handling all differ. Their combined effect cannot identify a universal serum-to-plasma correction, nor a CHNS-specific correction. The observed difference of source means must not be installed as an individual conversion constant.

## Usable candidates and limits

**Marginal summaries:** Table 1 explicitly labels mean and individual SD. In the full analysis sample, age is 69.5 (4.2) years, BMI 25.0 (3.6) kg/m², FPG 5.4 (1.4) mmol/L, FSG 5.2 (1.4) mmol/L and HbA1c 6.1 (1.0)%; 2,049/3,547 participants are female. These are source sample summaries, not target-population moments. Its diabetes/no-diabetes columns have n=506/3,041 according to the composite FPG diagnosis, which differs from the 425/3,122 previous-history split. No individual SD is a coefficient SE or a mean SE. Rounding, imputation and source sampling limit the precision available for replay.

**Joint evidence:** the Methods explicitly specify **Spearman** correlations. Full-sample coefficients are FPG–FSG 0.845, FPG–HbA1c 0.574 and FSG–HbA1c 0.529; the corresponding known-history-subgroup coefficients are 0.972, 0.763 and 0.743. The reported P values are below 0.001; correlation SEs/CIs and pair-specific sample counts are not supplied. These are unadjusted rank associations, not Pearson covariances, conditional slopes or a residual distribution. They cannot identify age/BMI interactions, nonlinear conditional response or a complete joint law.

**Threshold analysis:** Table 2 and the Results assign ROC/threshold results to the 3,122 people without previous diagnosis. At HbA1c 6.5%, sensitivity=88.9%, specificity=93.7%, PPV=27.2%, NPV=99.7%, Youden=0.825, positive likelihood ratio=14.0 and negative likelihood ratio=0.12 against FPG 7.0 mmol/L. The AUC is 0.952 (95% CI 0.917–0.986). An isolated Methods sentence describes subsequent accuracy calculations in the total sample; retain this inconsistency rather than silently resolving it. Most text uses >=7.0, while a table footnote uses >7.0 for FSG. Equality handling is not fully certified. These are historical source analysis definitions, not clinical recommendations or CHNS decision thresholds.

**Composite agreement:** Table 3 combines medical/self-reported diabetes history, current glucose-lowering treatment and the respective laboratory threshold in all 3,547 people. Rows are FPG-composite negative/positive. Columns are the other composite negative/positive. The printed cells are:

- FSG composite: [[3029, 12], [21, 485]].
- HbA1c composite: [[2848, 193], [9, 497]].

The paper reports kappas 0.962 and 0.812 respectively. Applying its stated ordinary Cohen formula to the printed cells gives **0.961681382 and 0.797825128**, respectively. Thus the HbA1c printed kappa is not reproduced by the displayed contingency table. [Independent original-table inspection and arithmetic](MIND_2024_INDEPENDENT_ARITHMETIC_REVIEW.md) confirmed this discrepancy under the documented formula; it does not establish which source component is erroneous. **Quarantine the conflicting HbA1c kappa and table-derived agreement bundle from calibration until resolved.** Do not force a generator to satisfy both or quietly replace the printed coefficient. The FSG kappa reproduces after rounding, but other admission conditions still apply.

If, and only if, the same 425 known-history participants are positive under each composite, the tables use the same analytic sample without differential exclusion, and the common history/treatment set corresponds exactly to those 425, removing them from the common-positive cells implies history-free tables of [[3029,12],[21,60]] and [[2848,193],[9,72]]. The second yields sensitivity 72/81 and specificity 2848/3041, matching the rounded Table 2 values. This is an algebraic, assumption-qualified consistency check, not independent data. It does not identify the FSG–HbA1c cross-tab or erase the source inconsistency. Do not count cells, derived ratios and kappa as independent constraints.

## Consequence for our framework

This source supplies precisely the type of evidence that a generic statistic-name matcher can mishandle: serum versus plasma, Pearson versus rank association, old-history versus measured-positive groups, and incompatible summary arithmetic. A construction Agent may use admitted source facts and explicit transport assumptions; it must not receive a false requirement to match every reported number.

For this case, source extraction, internal arithmetic consistency, source-population execution and target applicability are separate gates. Passing semantic-feedback-v1 alone proves none of the other three. The source's age/BMI conditional effects remain unreported. The new evidence can support measurement sensitivity and unadjusted joint constraints once admitted; it cannot close the missing five-variable conditional model or justify promising all scientific relationships.

Next: source-item admission with quarantine status and explicit source-population applicability. The code review confirms rank correlation already exists; composite-event functionality is unnecessary unless a corresponding endpoint is selected. No target coefficients, generated table, revised generator or F2 freeze is produced here.
