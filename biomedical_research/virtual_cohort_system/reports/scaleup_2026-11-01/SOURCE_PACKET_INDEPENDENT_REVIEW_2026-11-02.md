# Independent Greiner source-packet review

Prepared 2 November 2026. Advisory review of extraction and declared semantics; this does not freeze a case, admit a target or activate feedback.

Reviewed JSON: `evidence/SOURCE_CANDIDATE_GREINER.json`, SHA256 `76609b9c923d7b0b1ea2bbeeded49aa72c7998e5951a48c61bee0babf2c06a02`.

The review used the existing `GREINER_SOURCE_OPERATOR_REVIEW.md`, the candidate companion Markdown, and an independent reading of the publisher's expanded [Tables 1 and 2 and Methods](https://gh.bmj.com/content/6/5/e005222) through wang Chrome. The 12 contextual regression records were compared with the existing DC2 audit; this review did not independently reopen that supplement. No target participant data, target effects, generator or calibration output was accessed. No original study or download quota was added; browser traffic was not metered.

## Decision

**The numerical extraction passes.** The 24 geometric means, six prevalence estimates, their 60 CI endpoints, 18 age summaries, sex/site labels and 12 table-specific subgroup counts agree with the primary tables. No numerical correction is indicated. This candidate is sufficiently faithful to advance to a declared source-informed construction protocol after the minor status fixes below. Full joint identification is not a prerequisite for a prospective feasibility experiment.

This is not approval to call a target-table calculation exact source replay. Source-context construction or an explicit transfer scenario, operator implementation and case-use protocol still need their own versioned approval. Unknown dependence, selection and assay transfer can remain declared assumptions; unresolved regression units must not silently become verified numerical constraints.

## What was verified

| Component | Independent result |
|---|---|
| Six source strata | Malawi rural/urban and Uganda, separately for reported Men/Women. No UK column accidentally included. `male`/`female` are normalized labels for these reported strata, not a claim about a separately verified measurement procedure. |
| BMI | Six geometric means and 12 CI limits match Table 1; unit kg/m². They are not arithmetic means. |
| TC, HDL, non-HDL | Eighteen geometric means and 36 CI limits match Table 2; source unit mmol/L. |
| Low HDL | Six percentages and 12 CI limits match Table 2. Strict `<1.03 mmol/L` for men and `<1.29 mmol/L` for women; multiplier 100 and percent units are consistent. |
| Age | All six medians and 12 quartiles match Table 1. Age is in years. Q1/Q3 describe the distribution, not confidence limits for the median. |
| Counts | Table 1: 4534, 3988, 2177, 5894, 7192, 2424. Table 2: 4534, 3988, 2179, 5893, 7190, 2429, in the packet's context order. Differences are preserved. No row-specific denominator is falsely supplied. |
| Eligibility | Adult inclusion, exclusions for reported pregnancy/HIV/diabetes, sex availability and complete lipid data agree with Methods. The unresolved diabetes definition is stated. |
| Measurement | Malawi fasting exceptions, laboratory devices and unresolved specimen/adherence details agree with the inspected Methods; unit conversion is not treated as an assay bridge. |
| Regression context | The 12 estimates, intervals, adjustment sets and analysis counts agree with the prior DC2 review. They are not converted into raw-unit coefficients, correlations or executable calibration operators. |
| Activation | Empty active-check list and absent loss/tolerances are consistent with a candidate packet. No builder release is claimed. |

The printed Malawi urban women's HDL interval remains 1.15–1.26 around a geometric mean of 1.15. The packet correctly preserves and quarantines it. This review does not infer the intended endpoint. Rounded equal CI endpoints also remain printed observations, not evidence of zero dispersion.

## Exact edits recommended before release

1. **Companion Markdown, last paragraph:** replace “already admitted original study” with “already reviewed original study.” The previous review admitted specified uses of evidence, while this packet and the eventual case protocol are still pending. The current sentence conflates those scopes.
2. **Every `constraint_candidates[*].admission.reported_value`:** replace the ambiguous `admitted` with `verified_reported_extraction` (or an equally explicit extraction-only status). There are 48 such records. Retain the separate activation/context-only statuses. This clarifies that verified transcription does not activate an operator or certify transfer.
3. **Row-level issue linkage, recommended before a machine consumes the candidate:** attach existing issue `rounded_or_collapsed_ci` to the uncertainty issue list for the five records below. The global warning and `use_for_precision_weighting:false` already protect the reviewed document; row linkage prevents a later row-only consumer from losing the warning. Do not change the printed numbers or fabricate CI widths.

| Affected geometric-mean record | Printed CI |
|---|---|
| `malawi_rural_men__non_hdl_cholesterol__geometric_mean` | 2.5–2.5 |
| `malawi_urban_men__non_hdl_cholesterol__geometric_mean` | 2.6–2.6 |
| `malawi_rural_women__total_cholesterol__geometric_mean` | 3.9–3.9 |
| `malawi_urban_women__non_hdl_cholesterol__geometric_mean` | 2.6–2.6 |
| `uganda_women__total_cholesterol__geometric_mean` | 3.7–3.7 |

None of these edits requires another source search or target inspection. No packet changes were made by this reviewer.

## Scientific interpretation that must survive implementation

- **Non-HDL:** compute TC minus HDL for each row before summarizing. Its geometric mean is not the difference between two geometric means. It is a derived, jointly informative quantity, not a third independent assay. Positive-domain failures must remain visible rather than be silently clipped.
- **Uncertainty:** source CIs concern estimated summaries. They do not supply person-level SD, conditional residual noise, a clinical reference range, or a permissible source-to-target error band. Repeated source strata and adjusted regressions also are not independent replication studies.
- **Age:** retaining median/IQR as contextual evidence is coherent. An Agent may choose an age distribution compatible with them as a declared assumption. Lack of a finite-sample quantile convention need not bar a whole-cohort experiment; it only prevents claiming an exact verified quantile replay under the current packet.
- **Lognormal option:** the stated inversion is algebraically correct when the assumed family, units, fraction-scale probability, finite inverse-normal quantile and positive sigma conditions hold. It remains a family-dependent marginal construction, not source-reported residual variance. Rounded summaries may be weak or incompatible constraints.
- **Sex-specific percentages:** the thresholds define a historical reporting statistic. Comparing their prevalence across sexes does not identify an equal-threshold contrast or a sex effect independent of the unequal cutoffs. The source itself cautions against reading low HDL alone as cardiovascular risk.
- **Joint evidence:** source regression context may guide an Agent's explicit assumptions and sensitivity scenarios. It must not be inserted as verified partial coefficients of a single equation. No exact age–BMI–TC–HDL joint law follows from the marginal summaries.
- **Source versus target:** a source-stratum simulation is a declared reconstruction, not actual source IPD. A target-transfer scenario should say which summaries are imposed, which are merely contextual and which analyses depend on unverified transport. No claim of universally applicable African lipid relationships follows from these two source countries.

## Bounded next step

Make the status/issue-link edits, retain candidate provenance, and construct a small approved feedback bundle with explicit source-context or transfer-scenario labels. Test the missing geometric-mean and percentage/derived-variable utilities separately, then freeze the prospective scientific-use protocol. Partial identification belongs in the assumption ledger and interpretation of results; it is not a reason to keep expanding this extraction audit indefinitely. This review neither selects generator parameters nor supplies expected target signs, means or slopes.
