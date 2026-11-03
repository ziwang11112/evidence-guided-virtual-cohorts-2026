# Supplement: a source-to-generator trace and systematic evidence-use inventory

This supplement documents the completed main study using retained evidence, specifications, analytic artifacts and endpoint aggregates. CHNS2009 E1 A01 is selected by its first ordinal identifier, **not by performance**. It illustrates one scientific construction rather than a typical or preferred model. No participant or generated rows were accessed, and no generator, evaluator or fitting procedure was executed for this account.

## Admitted source operators

The worked trace starts with the two separately adjusted associations in Jansen et al., Table 2, from Lifelines. The source population comprised unrelated adults of western-European ancestry selected for genetic analysis, with older family members preferred. Exclusions included self-reported diabetes or fasting plasma glucose at least 7.0 mmol/L, anemia under the reported sex-specific definitions, and missing required HbA1c, erythrocyte or glucose measurements. The reported marginal sample contained 2,921 participants; the regression-row count remains unconfirmed. Fasting glucose used fresh plasma and a hexokinase/G6PD method; HbA1c used an IFCC-standardized immunoassay. [Primary source](https://doi.org/10.1111/joim.12010); [admitted population and operator definitions](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/26ccdfb5a77c665ddce1d1c0c73ce991b7107fb3/biomedical_research/virtual_cohort_system/reports/main_study_freeze_2026-11-03/cases/CHNS2009/source_operations.json).

| Admitted operator | Adjustment and response | Reported coefficient | Retained uncertainty |
|---|---|---:|---|
| `R_JANSEN_BMI` | HbA1c, mmol/mol, regressed on age, sex and BMI | 0.13 mmol/mol per kg/m² | Printed interval 0.10–0.16; confidence level unconfirmed; coefficient SE unavailable |
| `R_JANSEN_FPG` | HbA1c, mmol/mol, regressed separately on age, sex and fasting plasma glucose | 2.29 mmol/mol per mmol/L | Printed interval 2.07–2.51; confidence level unconfirmed; coefficient SE unavailable |

These are separate projections, not the BMI and glucose coefficients of one jointly adjusted equation. The admitted numerical interpretation uses equal-weight, intercept-including population least squares without interactions. Those conventions define a qualified source-context calculation; original weights, exact row processing and intercept convention were not recovered. Printed intervals were neither labelled 95% nor converted into individual dispersion, precision weights or acceptance bounds. Exact records are `relationship_records[0:2]` in the [E1 packet](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/26ccdfb5a77c665ddce1d1c0c73ce991b7107fb3/biomedical_research/virtual_cohort_system/reports/main_study_freeze_2026-11-03/cases/CHNS2009/E1_sources/evidence_packet.json).

## From separate projections to a joint law

A01 assumed independent centered age and sex variables and bounded independent standardized uniform factors. Let \(b\) and \(g\) denote BMI and glucose residuals after removing the stipulated age/sex contributions. Their standard deviations are \(s_B\) and \(s_G\), with an assumed residual correlation \(r=0.25\). Concretely, \(b=s_BU_B\) and \(g=s_G[rU_B+\sqrt{1-r^2}U_G]\), where the independent factors are uniform on \([-\sqrt{3},\sqrt{3}]\). The source response includes \(\theta_B b+\theta_G g\), plus separately specified age, sex and independent residual contributions. The two published projections therefore imply

\[
c_B=\theta_B+\theta_G r s_G/s_B,\qquad
c_G=\theta_G+\theta_B r s_B/s_G.
\]

The reported marginal BMI and glucose SDs, 4.1 kg/m² and 0.5 mmol/L, were reduced by the variance assigned to the assumed age/sex terms. Source age SD was 9.9 years; female probability was \(1-1176/2921\). A01 assigned age/female contributions of 0.04/0.4 to BMI and 0.005/−0.05 to glucose. Independence yields \(s_B=4.0761135686\) and \(s_G=0.4969390969\). These nuisance contributions and the residual correlation are completion assumptions, not reported associations.

Solving the two identities gives

\[
\theta_B=\frac{c_B-r(s_G/s_B)c_G}{1-r^2}=0.0642172833,
\qquad
\theta_G=\frac{c_G-r(s_B/s_G)c_B}{1-r^2}=2.1583153824.
\]

Thus the Agent did not copy 0.13 and 2.29 into one joint equation. The derived coefficients depend on the additional covariance assumption. The remaining positive response residual variance was chosen to reproduce the source HbA1c SD of 3 mmol/mol within this assumed law. Source age followed a continuous uniform distribution with mean 55.5 and SD 9.9; source support was not restricted to the CHNS target ages. [Frozen specification, `parameters.jansen_selected` and assumptions `A_J_*`](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/26ccdfb5a77c665ddce1d1c0c73ce991b7107fb3/biomedical_research/virtual_cohort_system/reports/main_study_freeze_2026-11-03/constructions/CHNS2009_E1_A01/selected/model_spec.json); [retained mathematical derivation](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/26ccdfb5a77c665ddce1d1c0c73ce991b7107fb3/biomedical_research/virtual_cohort_system/reports/main_study_freeze_2026-11-03/constructions/CHNS2009_E1_A01/selected/analytic/law_derivation.md).

The analytic source artifact returns 0.13000000000000003 and 2.29 for the two constrained projections. This equality is imposed by construction, not independent validation. Its moment calculation follows the model's loading matrix and independent-factor variances. [Retained source comparisons](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/26ccdfb5a77c665ddce1d1c0c73ce991b7107fb3/biomedical_research/virtual_cohort_system/reports/main_study_freeze_2026-11-03/constructions/CHNS2009_E1_A01/selected/analytic/source_comparisons.json), `comparisons[0:2]` and `constraint_derivation`.

## Target completion and transport

A01 multiplied the two derived residual-response coefficients by 0.09148, giving 0.0058745971 and 0.1974426912 in HbA1c percentage-point units. The [NGSP scale relation](https://ngsp.org/ifccngsp.asp) has an additional 2.152 intercept for levels; it does not change regression slopes. Target baseline levels were chosen separately rather than obtained by transporting the source intercept. This unit transformation supplies no new empirical evidence and does not establish equivalence between source plasma and target serum measurements.

The shared structural family was as follows; the target uses the converted response slopes:

\[
B=m_B+a_Ba+f_Bf+b,\quad
G=m_G+a_Ga+f_Gf+g+Q,
\]
\[
H=m_H+a_Ha+f_Hf+\theta_Bb+\theta_Gg+kQ+s_HU_H.
\]

Here \(a\) and \(f\) are centered age and female membership, and \(U_H\) is an independent standardized uniform residual. For the target, age was discrete uniform over 35–74, female probability was 0.58, and baseline BMI/glucose/HbA1c values were 24/5.15/5.65 in their respective native units. Baselines are not necessarily full-law means. Residual scales, age/sex contributions and covariance remained chosen assumptions. An independent Bernoulli component with probability 0.08 multiplied a lognormal glucose excess with mean 2.5 mmol/L and log SD 0.55; its response contribution used \(k=0.55\). This was an assumed heterogeneity component, not an estimated diabetes prevalence.

The Jansen scenario has no excess component (\(Q=0\)). Only the two baseline response slopes were transported from the qualified Jansen construction. Applying them across ancestry, selection, fasting, assay and plasma/serum differences remained unvalidated. The target's mixture and covariate structure can change its separate projections. Its fully adjusted age coefficient follows algebraically from the completed law; the CHNS packet supplied no corresponding conditional-age constraint. [Specification, `parameters.target`, `A_TARGET_*`, `A_MEASUREMENT_TRANSPORT` and `A_TAIL`](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/26ccdfb5a77c665ddce1d1c0c73ce991b7107fb3/biomedical_research/virtual_cohort_system/reports/main_study_freeze_2026-11-03/constructions/CHNS2009_E1_A01/selected/model_spec.json).

## Checks, nonuses and retained outcomes

Numerical use did not entail universal source agreement. For a separately assumed Bao source context, A01 calculated Pearson correlation 0.7354295110 against the admitted 0.619, a raw difference of +0.1164295110. This was an analytic check, not a fitted constraint. The contextual MIND-China Spearman correlation, 0.529, remained uncomputed because ordinary moments did not determine ranks and the source imputation/tie mechanism was unresolved. Pearson was not substituted for Spearman. [Bao primary source](https://doi.org/10.1136/bmj.c2249); [MIND primary source](https://doi.org/10.1371/journal.pone.0296694); [comparison and unavailability records](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/26ccdfb5a77c665ddce1d1c0c73ce991b7107fb3/biomedical_research/virtual_cohort_system/reports/main_study_freeze_2026-11-03/constructions/CHNS2009_E1_A01/selected/analytic/source_comparisons.json).

Retained independent review checked correspondence between the stated law and its analytic calculations, required finite moments, positive support, source projection arithmetic and the scale transformation. It retained the Bao discrepancy and unidentified target features. No source-population tables were produced; analytic comparisons under assumed contexts did not constitute replay of the original studies. Target-table feedback could not substitute for source replay. Source-estimation, structural and transport uncertainty were not propagated by the three sampling seeds. [Review findings in the complete uptake inventory](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/26ccdfb5a77c665ddce1d1c0c73ce991b7107fb3/biomedical_research/virtual_cohort_system/reports/main_study_freeze_2026-11-03/publication/UPTAKE_INVENTORY.json), entry `CHNS2009_E1_A01`.

The author retained the initial model after exploratory feedback. Its final target estimates were:

| Focal coefficient and adjustment | Seed 5101 | Seed 5102 | Seed 5103 | Three-seed mean | Sample reference |
|---|---:|---:|---:|---:|---:|
| BMI, adjusted for age/sex; per kg/m² | 0.015192 | 0.012107 | 0.009901 | 0.012400 | 0.054946 |
| Glucose, adjusted for age/sex; per mmol/L | 0.426437 | 0.413929 | 0.402203 | 0.414189 | 0.402093 |
| Age, adjusted for sex/BMI/glucose; per year | 0.003339 | 0.003230 | 0.003810 | 0.003459 | 0.008107 |

All response effects are HbA1c percentage-point changes. These values show differing analytical agreement within one delivered construction. They are not fitted source statistics or evidence of clinical equivalence. References are uncertain estimates from the previously exposed selected CHNS sample. Values are copied from the [frozen endpoint aggregates](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/26ccdfb5a77c665ddce1d1c0c73ce991b7107fb3/biomedical_research/virtual_cohort_system/reports/main_study_freeze_2026-11-03/final_evaluation/RESULTS.json), `all_scheduled_slots` for A01, and its `construction_summaries` entry; no target-reference values were supplied to this constructor.

## Systematic roles across all E1 Agents

The matrix covers every E1 scientific author. **C** = numerical model constraint; **A** = analytic check; **T** = context only; **—** = not an admitted relational operation for that case. A check need not agree. The Pani means column represents all eight admitted age-band means, each with the displayed role. [Complete operation-level records](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/26ccdfb5a77c665ddce1d1c0c73ce991b7107fb3/biomedical_research/virtual_cohort_system/reports/main_study_freeze_2026-11-03/publication/UPTAKE_INVENTORY.json).

| Case / author | Jansen BMI | Jansen glucose | Bao Pearson | MIND Spearman | Pani age slope | Pani means ×8 |
|---|---|---|---|---|---|---|
| CHNS A01 | C | C | A | T | — | — |
| CHNS A02 | C | C | A | T | — | — |
| CHNS A03 | A | A | A | C | — | — |
| CHNS A04 | C | C | A | T | — | — |
| CHNS A05 | C | A | A | C | — | — |
| ENSANUT A01 | C | C | — | — | C | T |
| ENSANUT A02 | C | C | — | — | C | A |
| ENSANUT A03 | C | C | — | — | C | A |
| ENSANUT A04 | C | C | — | — | C | T |
| ENSANUT A05 | C | C | — | — | C | A |

ENSANUT uses the admitted task-unit representations of the Jansen projections and the NHANES component of [Pani et al.](https://doi.org/10.2337/dc08-0577); these are not additional independent versions of the same evidence. [ENSANUT operation definitions](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/26ccdfb5a77c665ddce1d1c0c73ce991b7107fb3/biomedical_research/virtual_cohort_system/reports/main_study_freeze_2026-11-03/cases/ENSANUT2018/E1_source_operations.json). Across the CHNS Agents, the matrix contains nine constraints, eight checks and three contextual uses; ENSANUT contains fifteen, twenty-four and sixteen, respectively. Every E1 Agent used a numerical constraint, but the records establish neither simultaneous source fit nor transport. No record used the explicit declined label; contextual explanations could nevertheless decline numerical integration.

For completeness, the prescribed CHNS E1 statistical construction constrained all four relations. The ENSANUT E1 statistical construction constrained both Jansen projections and retained the Pani slope and eight means as context. Equal information availability therefore did not imply identical numerical-use decisions. These role differences document implementation choices; they do not identify the cause of the observed performance ordering.
