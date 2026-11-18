# Independent scientific review

Review date: 2026-11-09. Status: baseline code, host contract and corrected author sidecar drafts reviewed; freeze and optional revision pending. This is a declaration/code audit, not an outcome or clinical-validity assessment. No real-target results or generated rows have been read for this unit. No candidate, bundle input, engine or lock has been modified by this reviewer.

## Baseline and intended use

All nine copied scientific files match `input/baseline_commitments.json`. The baseline generator and model specification retain SHA256 `622cb18b6225832ae754812ae80477a5783958603da1e8e2470202a046a655ef` and `e469f7075314cce63ac9a3b1fb3d961c2770f96d9680e844bab43ad2abd36fa7`, respectively.

The new protocol explicitly governs underlying same-specimen lipid concentration scenarios with no separate assay-error model. Historical measured-assay metadata and baseline assumptions remain unchanged provenance; source measured moments to an underlying law remain a transfer assumption. This explicit change of use resolves the scope ambiguity raised during preparation review. It does not retrospectively classify every noisy measured-value violation as a biological impossibility.

The three host estimands preserve the requested two unweighted age/sex-adjusted BMI slopes, expressed as five times the BMI coefficient after lipid conversion by 38.67, and paired residual Pearson correlation adjusted for age, sex and BMI. The protocol retains all 23 diagnostics, three new fixed seeds, all stages and source feedback, with no real-target comparison and no prescribed repair algorithm or desired association.

The baseline uses positive lognormal BMI/lipid variables coupled by a nonsingular Gaussian copula. The implied log(HDL)-log(TC) variance is positive in both age strata (approximately 0.126841 and 0.098050). Thus its support permits HDL>TC; this is an analytic consequence of its model law rather than a finite-output finding. Marginal positivity does not imply a nonnegative non-HDL component. No output clipping or component-order restriction appears in the baseline generator.

## Review timeline

1. Baseline preparation reviewed; all nine hashes verified. New interpretation and scientific-analysis definitions are explicit.
2. Author notified reviewer that baseline sidecars are being drafted. A controller registry-approval issue was reported to the coordinator before author actions; no scientific conclusion follows from that infrastructure issue.
3. Baseline sidecar audit: all three requested estimands match exactly. All evidence links are selective component inputs, with partial coverage; no source rank correlation or category contrast is promoted to a requested adjusted estimand. Population, selection, measurement, functional-form and uncertainty gaps remain explicit. The author corrected a minor scale-gap wording error to distinguish lipid mmol/L from BMI kg/m^2 before freeze. The rule is declared applicable at unchanged zero tolerance, while acknowledging the baseline has no guarantee. Draft hashes are bound in the JSON record.
4. Optional revision audit: pending author decision. No revised candidate exists at this review checkpoint.

## Unresolved scientific questions

Source marginal arithmetic moments, community Spearman associations and category contrasts do not directly establish the requested adjusted continuous slopes or residual Pearson correlation. The reviewed sidecars retain these distinctions and the population, measurement and selection-transfer assumptions. Their selected links do not claim exhaustive generator dependency coverage. Model implications cannot be promoted to direct evidence merely by satisfying a component constraint. Quantitative source conformity and collateral analysis changes require the separately authorized postclosure review; they have not been assessed here.
