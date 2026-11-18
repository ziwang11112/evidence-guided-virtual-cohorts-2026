# Scientific-use decision: focus the paper and the next validation

Completed 16 November 2026. This unit answers the user's request to clarify supported analyses, acceptable differences and the most necessary validation. It uses closed aggregates; **no new patient analysis, resampling, generator run or paid model call was performed**.

## Decision

Keep the paper centered on Agent-generated virtual data for requested biomedical analyses. Lead with the demonstrated lifestyle BMI pattern and the PNS complementary-evidence gain in paired dependence. Use the ENSANUT conditioning pattern as additional reuse evidence. Retain the full profiles and describe quantitative lipid, BP-slope and dispersion limitations. Do not replace the mainline with a general Agent-reliability benchmark.

The [use-and-margin assessment](SCIENTIFIC_USE_AND_MARGINS.md) separates source-rich reconstruction, external developmental comparison and controlled mathematical tasks. It also distinguishes pattern support, numerical adequacy and inferential/clinical uses. Existing results do not supply a universal clinical acceptance margin. No equivalence test or new pass/fail score was added.

## Findings with practical meaning

| Specific use | Real sample reference | All selected virtual draws | What is supported now |
|---|---:|---:|---|
| Urban–pastoralist adjusted BMI contrast | 1.882 kg/m² | 1.700–2.251 | Source-rich association pattern and approximate effect scale; 2 constructors, 6 draws. |
| PNS adjusted paired-BP correlation, augmented evidence | 0.7172 | 0.6865–0.7182 | Targeted joint-analysis improvement in an exposed developmental case; 3 constructors, 9 draws. |
| ENSANUT attenuation of BMI coefficient after glucose adjustment | 0.02701 HbA1c percentage points/5 kg/m² | 0.01394–0.02621 | Positive attenuation with both coefficients positive in both constructors and all 6 draws; not causal mediation. |
| Rural–pastoralist adjusted TC contrast | 9.493 mg/dL | −0.695–1.943 | Precise group-effect recovery is not supported by current results. |
| PNS adjusted BMI–DBP slope, augmented evidence | 2.260 mmHg/5 kg/m² | 2.829–3.195 | Direction preserved; exact quantitative adequacy unresolved. |

Each reference is a sample estimate. Ranges show generation variability across the saved draws, not confidence bounds for the target population. The maximum observed BMI-contrast discrepancy, 0.369 kg/m², is not a retrospectively chosen acceptable margin. The same applies to the 0.03066 maximum PNS correlation discrepancy.

## One priority, not a larger experiment grid

The [minimal protocol](MINIMAL_VALIDATION_PROTOCOL.md) proposes one matched-size real–real versus virtual–real empirical sampling diagnostic in the existing lifestyle case. It holds both Agent laws, all six saved tables, the shared operator and nine pooled contrasts fixed. It uses no paid call, new source or new dataset. It is **not run** and must receive wrapper/implementation review and an input freeze before execution.

The real trait-specific counts are 1,189 for BMI, 400 for TC and 405 for HDL, versus 1,226 complete virtual rows. Conditioning on matched sample size and group/sex composition can clarify whether apparent differences reflect ordinary empirical sampling or persistent discrepancy. The diagnostic does not produce independent clinical cohorts, isolate sample size from composition effects, set scientific margins, or justify generator tuning.

If a quantitative-equivalence claim is later desired, collect use-specific margin rationale with the [domain review form](USE_REVIEW_FORM.md). No expert response has been received. A new unexposed cohort is deferred unless a stronger generalization claim becomes the explicit objective.

## Implementation and checks

- `analyze_use.py` extracts 222 existing estimate slots into 32 analysis-by-condition profiles: 54 lifestyle, 90 PNS, 60 ENSANUT and 18 iron values. This is a focused audit, not a census of every historical experiment.
- `verify_aggregates.py` directly checks every slot against the original aggregate files and independently recomputes 224 profile quantities using decimal arithmetic. Maximum decimal-versus-float discrepancy: 3.34e−15 after upward rounding. This second implementation is root-led, not a separate human/model review and not a rerun of the original patient analyses.
- Two six-table pattern checks retain every author and seed. Units distinguish HbA1c concentration (%) from changes in percentage points; the iron OR null is 1, not 0. Iron draw numbers are explicitly indices because the imported audit did not provide original seed IDs.
- All 11 bound prior inputs are byte-unchanged. The current manuscript v0.32, its PDF/ZIP and historical generators are not edited. A [manuscript insertion proposal](MANUSCRIPT_USE_INSERT.md) is provided for the next planned revision.
- Primary statistical-methodology sources were consulted for analysis-specific utility, equivalence interpretation and simulation design. Scite failed before returning results; web retrieval was used. No new clinical source entered a generation packet.
- No patient rows or credentials were read, and no dataset was downloaded; no new API cost, new automation or public synchronization occurred. Local project-directory Git status reported that it is not a Git checkout; no Git operation or upload was attempted after that read-only check.

## Deliverables

[Main assessment](SCIENTIFIC_USE_AND_MARGINS.md) · [all observed profiles](OBSERVED_PROFILES.md) · [machine-readable profiles](ANALYSIS_USE_PROFILE.csv) · [full estimate ledger](ESTIMATE_LEDGER.csv) · [minimal validation protocol](MINIMAL_VALIDATION_PROTOCOL.md) · [second arithmetic check](NUMERICAL_RECHECK.json).

This bounded assessment is complete. The next executable scientific unit is the one diagnostic above, not another broad search or generation batch.
