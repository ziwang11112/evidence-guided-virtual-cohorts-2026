# MIND-China 2024: independent aggregate-arithmetic review

1 November 2026. **Confirmed inconsistency: ordinary Cohen kappa calculated from the published FPG–HbA1c Table 3 cells is 0.797825128, which does not round to the paper's 0.812.** FPG–FSG kappa does reproduce the reported 0.962 after rounding. The original cells, published statistics and independent derivations must remain separate; this audit cannot determine which original quantity is erroneous without further authoritative information.

Source: Wang et al., *Comparing glycemic traits in defining diabetes among rural Chinese older adults*, PLOS ONE 2024;19:e0296694, [original article](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0296694). Methods 2.2–2.3 and Results 3.2–3.4 were read directly. The [original Table 3](https://journals.plos.org/plosone/article/figure?id=10.1371/journal.pone.0296694.t003) and [Table 2](https://journals.plos.org/plosone/article/figure?id=10.1371/journal.pone.0296694.t002) were independently inspected visually in the requested Chrome extension. The numbers below were not accepted solely from the coordinator's transcription.

## Printed cells and ordinary kappa

Rows are FPG-defined **composite** diabetes status (No/Yes); columns are the other composite definition (No/Yes). Each definition includes common diagnosed-history/drug-treatment status OR its glycemic threshold. These are not threshold-only biomarker labels.

| Comparison | No/No | No/Yes | Yes/No | Yes/Yes | Row totals | Column totals |
|---|---:|---:|---:|---:|---|---|
| FPG versus FSG | 3,029 | 12 | 21 | 485 | 3,041; 506 | 3,050; 497 |
| FPG versus HbA1c | 2,848 | 193 | 9 | 497 | 3,041; 506 | 2,857; 690 |

Both sum to n=3,547. Table 3 prints kappas 0.962 and 0.812, respectively. Methods 2.3 explicitly gives `(P0-Pe)/(1-Pe)`. For ordinary Cohen kappa, `P0=(a+d)/n` and `Pe=[(a+b)(a+c)+(c+d)(b+d)]/n²`.

| Quantity | FPG–FSG | FPG–HbA1c |
|---|---:|---:|
| Observed agreement P0 | 0.990696363124 | 0.943050465182 |
| Marginal expected agreement Pe | 0.757203222679 | 0.718315465549 |
| Exact count-form kappa fraction | 2,937,626 / 3,054,677 | 2,827,438 / 3,543,932 |
| Recomputed kappa | 0.961681382352 | 0.797825127570 |
| Rounded to three decimals | **0.962** | **0.798** |

Independent arithmetic used the displayed integer counts, with a second algebraic form, `2(ad-bc)/[(a+b)(b+d)+(a+c)(c+d)]`, providing the same values. These small integer products are exactly represented by the calculation. The HbA1c difference from 0.812 is about −0.014174872; ordinary rounding cannot explain it. Simultaneously transposing the table or exchanging class labels does not remedy an ordinary-kappa discrepancy. No alternative weighting, excluded subset or modified cells was invented to make the published coefficient fit.

## Conditional reconstruction of the history-free table

Results 3.4 reports **425 participants with known diabetes history**; Results 3.2/Table 2 identifies **3,122 without previous diagnosis**. Methods and Table 3 describe a shared history/treatment component in all three composite definitions. **If these are exactly the same 425 people**, all must lie in the Yes/Yes cell of either composite cross-tabulation. Removing them only from the HbA1c table's lower-right cell gives:

`[[2848, 193], [9, 497 − 425]] = [[2848, 193], [9, 72]]`, n=3,122.

This is a conditional algebraic consequence of the published definitions, not a participant-level reconstruction or proof that the original implementation applied those definitions consistently. The article uses self-reported, recorded and treated history descriptions in different passages; their set equivalence is an explicit condition, not an independently checked fact.

Using FPG as reference, TN=2,848, FP=193, FN=9 and TP=72:

| Statistic | Derived from counts | Published Table 2, HbA1c 6.5% |
|---|---:|---:|
| Sensitivity = 72/81 | 88.8889% | 88.9% |
| Specificity = 2848/3041 | 93.6534% | 93.7% |
| PPV = 72/265 | 27.1698% | 27.2% |
| NPV = 2848/2857 | 99.6850% | 99.7% |
| Youden index | 0.825422924 | 0.825 |
| Positive likelihood ratio | 14.005757052 | 14.0 |
| Negative likelihood ratio | 0.118640762 | 0.12 |

Every listed value agrees at the published precision. This strengthens the coherence of the displayed counts with Table 2; it does not establish which Table 3 quantity should be corrected. The conditionally reconstructed history-free kappa is approximately 0.392023. It is a derived contextual statistic, not a published source claim or a replacement for total-sample composite kappa. Inclusion of a common positive-history set changes prevalence and agreement; composite-label agreement must not be advertised as independent assay agreement.

## Disposition and limits

Retain the Table 3 HbA1c kappa as **published but internally unreconciled** and quarantine it from numeric calibration. Preserve the reported cells as source aggregates, the stated formula, the derived value and this discrepancy together. They could support a small evidence-consistency fixture: correctly implementing the named operator should flag disagreement with the published claim. Such a fixture tests extraction/arithmetic reasoning, not clinical efficacy, biological synthesis quality or a CHNS target result. It must not silently rewrite the source or present the derived value as a verified original-data correction.

Table 2 sensitivity/specificity use a history-free denominator and FPG reference. They cannot be substituted for Table 3's total-sample agreement. Likewise, the paper's Spearman correlations are separate operators and were not recomputed from these categorical counts. No confidence interval or sampling uncertainty was manufactured for kappa. No population transport, assay interchangeability or clinical threshold recommendation is established by this check.

Machine-readable arithmetic and scope are in [MIND_2024_INDEPENDENT_ARITHMETIC_REVIEW.json](MIND_2024_INDEPENDENT_ARITHMETIC_REVIEW.json). One **already allocated** original was independently reread, adding no new original-study quota. No other original/reference, participant file, CHNS effect or generator was opened/run. No article/PDF was downloaded or saved; browser page/image traffic was unmetered. Only this note and its JSON were written; STATE, source packets and frozen artifacts were not changed.
