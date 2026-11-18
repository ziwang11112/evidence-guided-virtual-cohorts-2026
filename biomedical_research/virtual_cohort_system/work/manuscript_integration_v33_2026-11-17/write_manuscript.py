"""Assemble v0.33 from original prose and closed, hash-bound aggregates."""
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parents[2]
M=P/'manuscript'
old=(M/'DRAFT_v0_32.md').read_text(encoding='utf-8')
F='paper_figures_v33_2026-11-17'
text=r'''# From Fragmented Evidence to Analyzable Biomedical Cohorts with Scientific Agents

Working manuscript v0.33 — 17 November 2026.
Analysis-driven generation; integrated blood-pressure and iron-status evidence-content experiments. No venue page limit is imposed on this scientific reading edition.

## Abstract

Published biomedical findings are available even when the individual measurements needed for a new analysis are not. We study how scientific Agents can turn a research request and fragmented evidence into virtual cohorts that existing analysis software can use. The Agent interprets study conditions, combines compatible statistics, chooses a joint probability model and authors an executable generator. Numerical tools sample the model, check its outputs and preserve a source-to-assumption record. We evaluate scientific use through the same analyses on virtual and measured records, rather than marginal similarity alone. A lifestyle application reproduces an adjusted urban–pastoralist BMI contrast of 1.700–2.251 kg/m² across six generated cohorts, compared with 1.882 in the measured sample. Two controlled tasks show composition of complementary evidence into adjusted and within-person relationships. Two biomedical three-condition experiments then separate the addition of marginal summaries from the addition of joint statistics. Relative to summaries alone, joint evidence reduces residual-correlation discrepancy by 78.6% in blood pressure and absolute log-odds-ratio discrepancy by 46.8% in iron status. The complete profiles also reveal unchanged or worsened slopes, prevalence and continuous dependence. The contribution is an analysis-driven, inspectable route from evidence to records, with concrete evidence that joint information can improve a requested scientific use. These developmental results delimit the supported analyses; they do not establish clinical equivalence or general transport to new populations.

## 1. Introduction

Biomedical researchers often know the measurements and analyses a study needs before they can obtain a complete dataset. A cohort may omit an expensive biomarker, individual records may be inaccessible, or the available knowledge may consist only of papers describing different parts of a joint relationship. Published means, adjusted coefficients and subgroup counts are valuable, but cannot simply be concatenated into patient records. The practical opportunity is to make that evidence usable through a virtual data product.

Consider two requests. One asks for paired blood-pressure measurements suitable for an age-, sex- and BMI-adjusted analysis. Another asks for hemoglobin and ferritin measurements suitable for both deficiency co-occurrence and continuous association analysis. A collection of marginal summaries is insufficient for either joint task. Even a published correlation may describe a different adjustment set. The generator must supply a coherent joint law, including explicit choices where evidence is missing.

We study scientific Agents as model authors in this setting. Given a population, measurements, intended analyses and permitted evidence, an Agent interprets the sources, selects or derives constraints, chooses the scientific structure and writes a sampler. The resulting records can be passed to ordinary regression, group-comparison and joint-association software. The method includes complete cohort generation with no target individual input. Extending unmeasured columns and completing partially missing records are related uses with different information boundaries; they require separate validation.

The central scientific question is not answered by a plausible table alone: **which analyses can the generated data support, and what changes when the evidence covers the joint relationship those analyses require?** Generating more rows reduces sampling noise under a chosen law. Supplying complementary relationship evidence can change that law. Our experiments distinguish these two operations and show both the useful consequences and their limits.

We make three contributions. **First, an executable task and workflow:** a scientific request is translated into a joint model, virtual records and a traceable evidence/assumption record, with Agent decisions separated from deterministic execution. **Second, evidence-composition experiments:** two controlled tasks test mathematical composition, followed by two biomedical content controls that isolate the addition of joint statistics beyond marginal summaries. **Third, analysis-level evaluation:** the same scientific estimators are applied to virtual and measured records, with complete endpoint profiles and worked model-choice traces. The strongest experimental finding is a specific improvement in two requested joint analyses, not a universal quality gain across every use of a table.

## 2. Related work and task position

LLM-based simulation and summary-driven synthesis already cover important parts of this space. G-Sim proposes simulator structure and calibrates it with gradient-free optimization or simulation-based inference [1]. LLMSynthor uses aggregate alignment, inferred dependencies and statistical differences to guide synthetic records [2]. Biomedical approaches include simulation from summary rules for data pooling [3], SynthIPD's reconstruction from published materials [4], KMGen's literature-informed patient generation [5] and SynthCraft's medical synthetic-data workflow [6]. Agent terminology, a sampling program or a feedback loop alone does not distinguish the present work.

Our emphasis is the scientific modeling task connecting a biomedical request to the joint relationships needed for its analysis. We make the adopted study conditions and unsupported completions inspectable, and test what an increment of joint evidence changes in the delivered data. The biomedical examples cover adjusted pressure dependence and threshold-versus-continuous biomarker association, alongside a lifestyle reconstruction. We do not establish quality superiority over the neighboring systems; matched tasks and comparable inputs would be needed for that claim.

Statistical integration is an essential foundation. Multilevel network meta-regression relates individual models to study-level evidence [7], and SynDI incorporates external models through synthetic data [8]. Covariance projection, copulas and summary matching are established statistical tools. The Agent contribution is to interpret the evidence and construct a suitable executable combination for a request. Whether that construction is useful in a target sample remains an empirical question, separate from correctly executing the statistical algebra.

## 3. Method: from a research request to an executable joint model

### 3.1. Define the requested data and analyses

A request specifies the target population, measurement definitions and units, desired record structure, planned analyses and available inputs. It may supply no individual measurements, permitted covariates, or partially observed records. The main experiments here generate complete fictional records without target individual inputs. The request may explicitly name an intended analysis; it need not hide the user's scientific question. Evaluation measurements and results are withheld from fresh constructor contexts.

The output is more than a CSV: it includes the Agent-authored program, a model specification, parameter origins and the generated records. A new user request may legitimately lead to a different model. Freezing a delivery fixes one evaluation boundary; it does not force all future requests to use one immutable generator.

![Scientific Agent workflow from a request through evidence interpretation and model authorship to analyzable data](FIGDIR/fig1-request-to-data.drawio.svg)

**Figure 1. The Agent authors the scientific model; tools produce and inspect its records.** The Agent reads study conditions, composes supported relationships, selects a joint law and writes the generator. Numerical tools execute that law in isolation. The delivered table is analyzed with the same estimator used for its measured-sample comparison. The origin record links adopted parameters to reported evidence, derivations and remaining assumptions. Search and diagnostic revision are available actions; the new content-control experiments use fixed evidence packets and one construction call to isolate information content. Their evidence admission includes coordinator review, not fully automated source certification. The small table and analysis marks are schematic, not experimental observations.

### 3.2. Interpret evidence under its study conditions

Each evidence item retains its original population, measurement, unit, transformation, statistic, adjustment set and available uncertainty. A marginal Pearson correlation, a Spearman correlation and an adjusted residual correlation are different constraints. Source summaries also require compatible observations: covariances cannot be reconstructed from variances measured in unrelated subsets without further assumptions.

When retrieval is allowed, the Agent can search for missing information and inspect original material. The completed blood-pressure search used Europe PMC queries and retrieved full texts. A coordinating research assistant then checked methods and tables and withheld an ambiguous candidate. In the content-control experiments, the coordinator instead supplied audited, masked source packets. This separates an actual retrieval episode from a controlled test of what information a constructor receives.

Each consequential model choice is marked as reported, derived or assumed. These are composable descriptions of origin, not ranked confidence levels. A source residual correlation can be derived correctly while its transfer to a new population remains assumed. We preserve five distinct quantities: the published statistic, the adopted parameter, the complete model's implied analysis, the estimate from sampled records and the measured-sample comparator. Their separation makes a modeling decision inspectable without treating a provenance label as an accuracy certificate.

### 3.3. Let the Agent construct the joint law

The Agent chooses distributions, dependence structure, numerical parameters and how to complete underidentified relationships. It then authors the executable sampler. The host supplies an interface and the permitted inputs, not the desired target slope, correlation, odds ratio or expected sign. The main implementation is therefore Agent-authored programmatic generation: numerical software samples the scientific law that the Agent wrote. It is not direct token-by-token generation of every patient row.

This freedom has observable consequences. In the pressure experiment, Agents derive residual covariance from a reported matrix and select an innovation law and transfer assumption. In the iron experiment, Agents choose a copula and solve for a latent dependence parameter from four published cells. In the repeated-measure task, they separate stable person components from visit deviations. These are case-specific constructions; neither a fixed copula nor a fixed regression is the overall method.

When the evidence does not identify the requested relationship, a scenario can still be delivered with its assumptions recorded. Several source-consistent laws may support different downstream analyses. Repeated seeds explore sampling under one law; they do not express uncertainty across those unreported scientific possibilities.

### 3.4. Execute, check and close the delivery

The submitted programs run through an isolated worker, using WSL/bubblewrap with a cleared environment, unshared network, read-only code/runtime inputs and bounded resources. Schema, row counts, finite outputs and hashes are checked outside the Agent. Mathematical review examines support and relevant moments; physiological review examines measurement-consistent restrictions; scientific checks compare estimable source relationships. A source check is unavailable when its statistical operator or population conditions cannot be reproduced. Unavailable checks are not counted as passes.

The broader workflow can return permitted diagnostics to the Agent for a keep-or-revise decision. The two new content controls deliberately use one call per construction, without retries, feedback or host scientific repairs. This design tests evidence content and the Agent's initial model construction, not revision benefit. Programs and specifications close before all final tables are analyzed. Every planned construction and draw is retained.

API records retain requested and returned model identifiers, prompts, outputs, tool interactions, usage and tariff-based cost estimates. Program replay and model-decision reproducibility are different: the same scientific program can be resampled, whereas a new stochastic API session may choose another law.

### 3.5. Measure usefulness through scientific analyses

We apply the same analysis implementation to virtual and reference records, with the weighting appropriate to each design. Outcomes include adjusted contrasts, BMI slopes, linear-residual correlation, deficiency odds ratios, joint prevalence and rank correlation. For each construction, estimates from its prespecified seeds are averaged; construction-level summaries then receive equal weight. Discrepancies are calculated at the draw level before this averaging. This prevents an average across opposing errors from masquerading as accurate generation.

Measured samples provide uncertain references, not known population truths. Reference confidence intervals describe their own sampling design and are not automatic acceptance margins. Likewise, virtual draw ranges are Monte Carlo variation, not clinical-effect intervals. Controlled mathematical tasks have prespecified numerical tolerances. Biomedical adequacy is reported in analysis units; no retrospective equivalence threshold or universal quality score is introduced.

## 4. Evaluation design

**Table 1. Four main study blocks test different parts of the evidence-to-data claim. Seeds are nested within constructions.**

| Study and scientific use | Information available to the Agent | Construction scale | Evaluation role |
|---|---|---|---|
| Lifestyle: adjusted group contrasts | Original paper, group findings and context; no target individual records | 2 constructions; 6 tables of 1,226 | Source-rich reconstruction of a real analysis |
| Controlled composition: adjusted and within-person association | Basic summaries, A, B, or A+B; stipulated artificial structure | 24 constructions; 72 tables of 3,000 | Algebraic composition and underidentification |
| Blood pressure: slopes and residual dependence | BASE, +SUMMARY, or +JOINT from one added paper | 9 constructions; 27 tables of 3,000 | Developmental evidence-content comparison |
| Iron status: threshold and continuous association | Study context, +SUMMARY, or +JOINT from one paper | 9 constructions; 27 tables of 5,000 | Second developmental content comparison |

### 4.1. A real analysis with the data replaced

Lea et al. studied cardiometabolic variation across pastoralist, rural and urban Turkana lifestyles [9]. Two fresh Agent authors generated age, sex, lifestyle, BMI, total cholesterol and HDL cholesterol. The measured analytical pool comprised 1,226 eligible adults, with BMI, total cholesterol and HDL available for 1,189, 400 and 405 participants, respectively. Each virtual table contained all measurements for 1,226 fictional individuals.

We reimplemented the analysis from the published Methods and applied the same implementation to both data types. Original author software was unavailable; this is not an unchanged run of their code or replication of every paper result. All nine pooled adjusted pairwise lifestyle contrasts are primary. Sex-specific contrasts, interaction tests and diagnostics remain available. Because the original published group findings were permitted inputs, this is reconstruction, not independent discovery.

### 4.2. Complementary evidence in two controlled tasks

The first artificial task requests the correlation of X and Y after separate linear adjustment for Z. Basic records give standardized marginal moments; A gives the X–Y correlation; B gives both correlations with Z. Together they identify a residual correlation of 0.21875. The second task requests the correlation of two biomarkers' within-person changes. Its stipulated structure separates stable person components from independent visit deviations. A gives between-person correlation and B same-visit correlation; together they identify change correlation −0.6. Supplement S2 states the exact assumptions and derivations.

Each task has four information conditions and three fresh constructions per cell. There are 24 first attempts and 72 draws, without retries or repair calls. The numerical tolerance for identified correlations and slopes is 0.08; separate source diagnostics use the frozen scale-specific rules. These are mathematical implementation tolerances, not clinical equivalence margins. In incomplete conditions the primary relationship is underidentified, so we show the selected scenarios without grading them against one hidden completion.

### 4.3. Two biomedical evidence-content controls

The blood-pressure experiment uses an existing PNS analysis for adults aged 20–79 [10]. Its three primary quantities are both BMI–pressure slopes and residual SBP–DBP Pearson correlation. The common design matrix contains intercept, age per decade centered at 50, female indicator and BMI per 5 kg/m² centered at 25. Both pressure SDs and physiological ordering are diagnostics. The existing weighted complete-case laboratory-substudy analysis is the comparator; generated rows are equally weighted draws of the proposed analytical population.

The iron experiment uses an existing NHANES August 2021–2023 reference for 979 nonpregnant women aged 20–44 with both measurements and positive phlebotomy weights, without a CRP restriction. Its primary analyses are crude association of low Hb and low ferritin, their joint prevalence and continuous Spearman correlation. Thresholds are strictly Hb <12 g/dL and ferritin <15 μg/L. Single-marker prevalences are diagnostics. Source evidence comes from Zhu et al.'s study of 1,671 selected rural Chinese women [13].

**Table 2. Within-case information masks. JOINT versus SUMMARY is the primary content comparison; BASE has a different meaning in the two cases.**

| Case | BASE | Added in SUMMARY | Added only in JOINT |
|---|---|---|---|
| Blood pressure | Existing packet, including INTERSALT coefficients and a raw-covariance source | Burkina Faso study context and univariate summaries [11] | Six same-sample pairwise correlations |
| Iron status | Zhu study identity, population and measurements, without selected outcome statistics | Low-marker counts and ferritin geometric mean | Four paired threshold cells from the same women |

Within each case all arms use the same request, model and construction interface. SUMMARY and JOINT contain the same marginal evidence; only JOINT receives the paired block. Packets contain the reported values, not a host-derived target dependence parameter. Iron BASE is not the earlier full iron packet, and PNS BASE already contains some relationship information. These are not interchangeable no-evidence controls.

Each experiment uses nine fresh `gpt-6.1-sol` constructions with high reasoning and default service, shuffled once before calls: three per arm, one call each, three fixed seeds per program. All 18 constructions and 54 final tables completed. Constructors did not see reference outcomes, old programs or prior results. Both references were already exposed to the project; PNS was selected following a favorable two-arm follow-up. These are frozen developmental comparisons, not two unseen-population validations. No patient refit or new data download was needed.

For PNS the primary contrast is absolute residual-correlation discrepancy. For iron it is absolute natural-log OR discrepancy. Both are averaged within constructions and then across constructions. All other prespecified endpoints are co-reported. No pooled cross-case score, significance claim or row-based effective sample size is used.

## 5. Results

### 5.1. Virtual records support a concrete lifestyle analysis

The generated cohorts reproduce a clear urban BMI contrast. Across six draws, urban-minus-pastoralist BMI is 1.700–2.251 kg/m², against 1.882 in the measured sample (95% model-based interval 1.368–2.397). The same table format supports all planned adjusted comparisons without a custom analyzer for each generator. Figure 2 shows the full nine-contrast profile.

Other findings are less well represented. Urban-minus-pastoralist total cholesterol is 13.732–18.907 mg/dL against 20.342, while rural lipid contrasts and HDL contrasts can differ in direction. Total-cholesterol SD is approximately 31.85–34.06 versus 42.81 mg/dL; HDL SD is approximately 14.4–15.1 versus 20.23. Standardization can obscure such scale differences, so the figure uses original units. Supplement S1 preserves complete estimates and auxiliary checks.

![All nine lifestyle contrasts in original scientific units](FIGDIR/fig2-scientific-use.svg)

**Figure 2. Replace the data, retain the analysis.** Dark squares and bars are measured-sample estimates and model-based 95% intervals. Colored diamonds are the means of three draws from each Agent construction; open circles and ranges are those draws. All nine pooled adjusted contrasts are shown in original units. The BMI contrasts are well represented in this reconstruction; lipid contrasts show remaining differences. Published findings were allowed inputs. Reference measurement availability differs by biomarker, whereas virtual records are complete.

### 5.2. Agents compose information into relationships that are not directly supplied

All six full-information constructors in the controlled tasks derive the requested relationship. Their mean residual correlations are 0.2211–0.2230 against the identified 0.21875; mean change correlations are −0.6013 to −0.5991 against −0.6. Across primary and secondary functionals, all 90 identified analysis estimates meet the frozen numerical tolerance. These nested estimates are not 90 independent tasks. A separate implementation reproduces all 216 analysis values to within 1.17 × 10⁻¹⁵.

The incomplete conditions produce different valid scenarios. Figure 3 deliberately displays a reference only where the supplied evidence identifies the primary functional. The capability demonstrated is composition under compatible assumptions, including recovery of a negative change association despite positive same-visit association. It does not establish clinical transport or a new covariance identity.

![Controlled evidence composition for adjusted and repeated-visit relationships](FIGDIR/fig3-evidence-composition.svg)

**Figure 3. Complementary summaries identify the requested analysis.** Diamonds are construction means and open circles/ranges are three draws per construction. Panels are artificial mathematical populations, not patient cohorts. The reference is shown only in A+B, where the primary relation is identified. The other cells admit multiple completions and are not ranked by distance from that line. Every one of the 24 constructions is included.

### 5.3. Joint pressure evidence improves residual dependence beyond extra summaries

Adding only source context and univariate summaries leaves PNS residual-correlation discrepancy nearly unchanged: BASE 0.16317 and SUMMARY 0.16328. Adding the six joint correlations reduces it to 0.03498, a **78.6%** descriptive reduction versus SUMMARY. Every joint-informed construction is closer on this primary endpoint than every summary-only construction in this run. Mean generated correlation changes from 0.5539 to 0.7251, against the existing reference 0.7172. The smaller difference between these last two means is not the MAE; averaging before taking absolute differences would hide construction-level variation.

The Agent records reveal substantive modeling work. All three JOINT constructors independently derive an approximately 0.788 source residual correlation after age/BMI projection. Two select a transported innovation correlation of 0.70; the third uses the source conditional covariance with a Student-t innovation construction and support handling. The source projection does not include sex adjustment. These are explicit Agent-selected models and transfer assumptions, not target parameters inserted by the host.

The resulting table is not uniformly closer on all analyses. BMI–SBP slope discrepancy increases from 0.3396 to 0.5091 mmHg per 5 kg/m², and BMI–DBP discrepancy from 0.7378 to 0.7550. All nine constructions retain the older INTERSALT slope anchors. Systolic-pressure SD discrepancy improves from 0.7448 to 0.2991 mmHg; diastolic SD changes little. Figure 4 preserves the complete profile.

![All primary blood-pressure analyses and scale diagnostics under the three evidence conditions](FIGDIR/fig4-pressure-content.svg)

**Figure 4. Joint information changes the paired-pressure analysis.** Panels a–c show all three primary analyses and d–e both dispersion diagnostics. Gray is BASE, copper adds summaries and purple additionally adds the joint block. Each diamond represents one of three constructions in its condition; small circles/ranges show its three draws. Dashed lines are exposed measured-sample point references, not equivalence bands. Panel f compares the primary absolute discrepancy after averaging within each construction. Joint evidence improves residual dependence and systolic dispersion, while both slope discrepancies worsen. The original search episode is reported separately in Figure S1.

### 5.4. Iron evidence strengthens threshold association but does not identify all continuous uses

Adding paired iron-status counts moves the generated mean low-marker OR from 3.0638 with marginal summaries to 6.9725. Absolute log-OR discrepancy decreases from 1.7620 to 0.9373, a **46.8%** reduction. Every JOINT construction is closer on this endpoint than every SUMMARY construction. Nevertheless, the generated OR remains below the reference 17.7898 (design-based 95% interval 9.2786–34.1083). Improvement is not recovery of that reference.

All three JOINT Agents independently choose a Gaussian copula and numerically solve its latent correlation from the supplied table. The four cells imply source OR 6.6531 and joint prevalence 10.3531%. Under the selected Gaussian family, a separate source-only calculation gives latent correlation 0.5842 and implied Spearman correlation 0.5661. The host supplied neither a copula nor those derived values. Generated results follow the chosen laws, while different authors select different positive or bounded marginal distributions.

The same evidence addition worsens other requested uses. Joint-prevalence discrepancy increases from 0.5187 to 2.5940 percentage points. Continuous Spearman discrepancy increases from 0.0447 to 0.1736, with generated correlation 0.5720 against 0.3984. The source table constrains binary co-occurrence; it does not identify a continuous copula. The extrapolation from threshold dependence to continuous dependence is an additional modeling assumption.

The provenance record also locates a distinct margin-transport problem. The source has low-ferritin prevalence 504/1671 = 30.16%, versus 12.15% in the reference sample. Both evidence-augmented arms carry that source margin into generation, producing about 30%. Low-Hb prevalence, in contrast, remains close to 15%. These source and target populations differ in selection, geography and measurement conditions; the analysis explains the model-level discrepancy, not the biological cause of the population difference.

![All iron-status analyses and marginal diagnostics under three evidence conditions](FIGDIR/fig5-iron-content.svg)

**Figure 5. A better threshold association need not imply a better continuous model.** Panels a–c show OR, joint prevalence and Spearman correlation; d–e show single-marker prevalences. Panel a uses a log axis. Shading in a–c shows existing design-based 95% reference intervals; no intervals are invented for d–e. Points and draw ranges use the same construction-level encoding as Figure 4. Panel f shows absolute log-OR discrepancy. JOINT improves this primary comparison, while joint prevalence and rank correlation become less close. Two SUMMARY constructors share the same primary profiles under common seeds; their overlapping results are retained as separate constructions, not counted as extra independent evidence.

### 5.5. Inspectable decisions connect the evidence to scientific use

**Table 3. What the Agent actually adds between a source and a data table. Derivation and transport remain separate decisions.**

| Case | Available evidence | Agent decision observed | Consequence and remaining assumption |
|---|---|---|---|
| Pressure | Six same-sample correlations, with study context | Projects out age/BMI; chooses innovation family and target dependence | Residual analysis improves; sex adjustment and population transfer remain assumed |
| Iron | Four joint-threshold cells plus source margins | Chooses Gaussian copula; solves latent dependence; chooses concentration laws | Threshold OR improves; continuous rank relation is a structural extrapolation |
| Repeated visits | Between-person and same-visit summaries under stipulated structure | Separates stable and visit components; derives change covariance | Negative change relation recovered in the controlled task |

Mathematical and numerical inspection support these findings. All nine pressure programs and nine iron programs have finite relevant moments under their inspected laws. Final tables show no observed pressure-ordering violations, nonpositive requested biomarker values or duplicate measurement rows under the respective checks. Separate implementations reproduce 162 pressure and 135 iron endpoint values to maximum differences of 8.62 × 10⁻¹⁴ and 8.88 × 10⁻¹⁶. These are computational checks, not independent clinical validations. No submitted scientific law was edited after its results became visible.

Earlier comparisons remain part of the record. A same-model, request-only study found the specialized workflow closer on two of six aggregated analyses and an ordinary Agent closer on four. Later reviews repaired specific mathematical defects, but 66 of 72 tables were unchanged. These findings motivate treating search, checks and revision as available actions rather than claiming that extra scaffolding necessarily improves data quality. Supplement S6 retains the comparison boundaries and unsuccessful source admission.

## 6. Discussion

The data product is feasible and its scientific use can be tested concretely. The lifestyle example demonstrates reusable records for a recognizable adjusted analysis. Controlled tasks demonstrate that an Agent can compose compatible summaries into a relationship that is not supplied directly. Two real-case content controls then show that relevant joint information improves a prespecified joint analysis beyond adding marginal summaries alone. These observations connect the Agent's scientific decisions to an actual data product and its analysis.

The results also clarify the level at which usefulness should be claimed. A virtual table can represent a BMI group contrast while missing a lipid contrast, or better represent a deficiency OR while worsening continuous association. These are different functions of the joint law. The method therefore supports explicit analysis-use statements accompanied by the source-to-model trace. Traceability helps inspect which assumption changed; it is not a calibrated predictor of accuracy or proof that the Agent's self-description is always correct.

Several limits bound the current evidence. The biomedical content controls have three constructions per condition, one current GPT configuration and previously exposed project references. They are fixed-packet tests, not an autonomous-search advantage or a comparison against a neighboring published method. Source admission included coordinator review. Artificial tasks provide exact summaries and stipulated structure, unlike uncertain heterogeneous publications. Recorded usage costs omit investigator effort. Shared seeds and similar model choices can produce closely related outputs across fresh calls.

Most importantly, neither summary consistency nor numerical execution establishes population transport. Sampling intervals around a measured reference do not resolve missing source-to-target assumptions, and repeated virtual samples do not increase the number of observed patients. The current evidence supports scientific-analysis prototyping and reconstruction in the evaluated settings. Claims about replacing clinical measurements, calibrated inferential uncertainty or out-of-population reliability require further validation.

The next experiments should extend a specific claim rather than add generic components. One useful extension is an independently defined biomedical use with an agreed scientific tolerance and an unused evaluation boundary. Another is replication of the same content controls with a second model family. A matched reproduction of a neighboring method can test comparative quality where the task and input regime align. The present results already identify the core method and the evidence-composition question; they do not require turning the paper into a general failure benchmark.

## 7. Reproducibility, costs and data-use scope

This edition integrates closed aggregate results. It runs no new Agent calls, generates no new cohorts and refits no patient data. Frozen protocols, packets, schedules, prompts, requested/returned model identifiers, programs and output hashes remain in their original units. All 18 new biomedical constructions and 54 tables are represented. The 216,000 rows in those two experiments are Monte Carlo records from 18 laws, not clinical sample size.

Recorded tariff estimates are USD0.3746075 for lifestyle generation, USD0.6540764 for controlled composition, USD0.9223776 for the pressure content control and USD0.6806303 for the iron content control. The earlier pressure search-plus-generation episode cost USD1.0560459, and the unsuccessful lipid admission cost USD0.7708042. These are stored usage estimates, not invoices or a general price per validated finding.

Patient-level real and virtual records, complete third-party papers and credentials remain local. Shareable materials comprise original code, permitted source metadata, protocols and aggregate results after disclosure review. Applicable dataset conditions govern access and redistribution. The editable manuscript package includes vector figures and LuaLaTeX sources. Author metadata, contribution statements, funding, conflicts, ethics and dataset-specific declarations require completion before submission.

## Supporting materials and reproducibility

The supplement retains all numerical profiles, exact controlled derivations, the earlier search episode and historical comparison boundaries. The unchanged expanded v0.31 remains the full developmental record; v0.32 is preserved as the previous focused edition. This integration supplies a protected-input manifest, plotted-value ledger, claim-to-evidence map and PDF/build audit.

'''
refs=old.split('## References\n\n')[1].split('## Supplementary results')[0].strip()
refs+='\n13. Zhu JH et al. Iron, Folate, and B12 Deficiencies and their Associations with Anemia among Women of Childbearing Age in a Rural Area in Northern China. *International Journal for Vitamin and Nutrition Research*. 2010;80(2):144–154. [DOI](https://doi.org/10.1024/0300-9831/a000014). Original Tables I and IV provide the admitted iron evidence.\n'
refs+='14. National Center for Health Statistics. NHANES August 2021–August 2023 laboratory documentation. [Ferritin, FERTIN_L](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/FERTIN_L.htm); [Complete blood count, CBC_L](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/CBC_L.htm). Published September 2024; documentation checked 17 November 2026.\n'
text=text.replace('The iron experiment uses an existing NHANES August 2021–2023 reference', 'The iron experiment uses an existing NHANES August 2021–2023 reference [14]')
text+='## References\n\n'+refs+'\n\n## Supplementary results\n\n'
text+=old.split('### S1.')[1].split('### S3.')[0].join(['### S1.',''])

def profile(case,title,num,defs):
 path=P/'work'/f'{case}_evidence_content_control_2026-11-16/analysis'
 ar=pd.read_csv(path/'arm_results.csv');dr=pd.read_csv(path/'seed_results.csv')
 out=f'### S{num}. {title}\n\n**Table S{num}. Complete {case} profile. Entries are mean estimate / mean absolute discrepancy. Absolute differences are computed before construction and arm averaging.**\n\n'
 out+='| Analysis | Sample reference | BASE | SUMMARY | JOINT |\n|---|---|---|---|---|\n'
 for ep,label,factor in defs:
  ref=dr.loc[dr.estimand==ep,'reference'].unique();assert len(ref)==1
  vals=[]
  for arm in ['BASE','SUMMARY','JOINT']:
   z=ar[(ar.arm==arm)&(ar.estimand==ep)].iloc[0]
   vals.append(f'{z.author_mean*factor:.4f} / {z.author_mean_absolute_reference_difference*factor:.4f}')
  out+='| '+label+' | '+f'{ref[0]*factor:.4f}'+' | '+' | '.join(vals)+' |\n'
 return out+'\n'

text+=profile('pns','Pressure content control',3,[('residual_correlation','Residual Pearson r',1),('bmi_sbp','BMI–SBP (mmHg/5 kg/m²)',1),('bmi_dbp','BMI–DBP (mmHg/5 kg/m²)',1),('sbp.sd_population','SBP SD (mmHg)',1),('dbp.sd_population','DBP SD (mmHg)',1)])
text+='''The two augmented arms share the Burkina Faso population description and univariate summaries. Its admitted matrix describes 2,114 complete-case partnered adults aged at least 40, excluding recent antihypertensive use and pregnancy, with pressure averaged from the last two of three seated measurements. Source age/BMI projection does not identify sex-adjusted target dependence. The original BASE packet retains its historical extraction status; this unit did not reauthenticate every old source. Source uncertainty, rounding and transport are not converted into fabricated target intervals.

All nine models are sampled at seeds 16211, 16213 and 16217. The programs are sealed before 27 final outputs and aggregate comparison. Every table has a unique hash. The pressure-ordering violation fraction is zero for every draw, the sixth endpoint in the independent 162-value calculation. Case-specific source audit, model decisions, receipts and full outputs remain in `work/pns_evidence_content_control_2026-11-16`. Figure 4 plots all five scientific metrics rather than only the primary gain.

'''
text+=profile('iron','Iron content control',4,[('odds_ratio','Crude OR / absolute log-OR difference',1),('joint_prevalence','Both low (%) / pp difference',100),('spearman','Continuous Spearman r',1),('low_hb_fraction','Low Hb (%) / pp difference',100),('low_ferritin_fraction','Low ferritin (%) / pp difference',100)])
text+='''The source four-cell table is both low 173, Hb-only 85, ferritin-only 331 and neither low 1,082, after collapsing the folate/B12 categories. The source crude OR is 6.6531. It must not be confused with the paper's separately adjusted OR of 6.4. Agents saw the source cells and definitions, not these derived ORs or a prescribed copula. The source population includes selected parous rural Chinese women, 2–4 years postpartum and using IUD contraception; it is not a representative US target sample.

The existing NHANES reference uses a stratified delete-one-PSU JKn calculation, with 15 strata, 30 PSUs and 15 degrees of freedom. Its 95% intervals are OR 9.2786–34.1083, joint prevalence 6.0681–9.5541% and Spearman 0.3183–0.4729. No intervals were calculated for the two displayed marginal fractions in this unit. The stored weighted reference is parsed after the new construction and generation outputs close. The project had already seen it historically; delayed parsing does not make it a new holdout.

All nine laws have finite relevant moments. Five bound both concentrations; one has ideal half-normal log tails with finite positive polynomial moments and an additional numerical probability guard; three have bounded Hb and positive lognormal-type ferritin tails. No post-submission scientific edits are made. One provenance classification remains incorrect: BASE_2 labels its source-suitability assessment REPORTED although it is an Agent assessment. Origin records therefore remain inspectable evidence, not infallible truth labels.

All 27 tables have distinct hashes. SUMMARY_1 and SUMMARY_2 nevertheless have identical three-seed primary profiles because their threshold probabilities, latent dependence and common seeds coincide; there are 24 unique primary draw triplets. No construction is removed or counted as an independent scientific replication merely because its rows differ. Seeds are 16311, 16313 and 16317. All 135 scientific endpoints independently agree to 8.88 × 10⁻¹⁶. Full records remain in `work/iron_evidence_content_control_2026-11-16`.

### S5. Earlier search-to-generation pressure episode

Before the three-condition control, an API-connected search Agent made 14 queries and retrieved six full texts. Coordinator original-source review admitted Burkina Faso and Ghana records [11,12]. Six fresh constructors received original or augmented packets, producing 18 tables. The mean residual correlation moved from 0.5376 to 0.7046; MAE fell from 0.17962 to 0.01277 (92.89%). This favorable exploratory result motivated the content-control experiment; it is not the latter's effect estimate. The new 78.6% result uses different fresh constructions and a more specific SUMMARY comparison.

![Earlier two-arm pressure search episode retained separately](FIGDIR/figS1-search-followup.svg)

**Figure S1. Earlier search follow-up, kept distinct from the new content control.** All three primary analyses and two scale diagnostics are shown for three constructions per arm, each sampled three times. Points, draw ranges and reference lines have the same interpretation as Figure 4. Added evidence improves residual dependence and diastolic outcomes while worsening systolic slope and spread agreement. This episode changes the entire source packet and does not isolate the effect of its joint statistics.

'''
prior=old.split('**Table S3.')[1].split('### S4.')[0]
prior='**Table S5.'+prior
text+=prior+'\n### S6. Historical checks, unsuccessful admission and replay boundaries\n\n'
hist=old.split('**Table 3.')[1].split('## 6.')[0]
hist='**Table S6.'+hist
start=hist.index('| Evidence block |')
end=hist.index('The lipid follow-up')
hist=hist[:start]+'''| Evidence block | Retained finding | Interpretation |
|---|---|---|
| Glycemia | Conditional BMI and residual spread do not uniformly improve | Different historical packets and exposed references |
| Earlier iron study | Threshold summaries are representable; transfer differs | Two constructions; separate from the new content control |
| Repeated follow-up | Rich model exports support requested analyses | Information-rich reconstruction |
| Ordinary Agent versus workflow | Workflow closer on 2/6 aggregate analyses | 12 constructions; no consistent superiority |
| Paired review | Tail and rounding repairs; 66/72 tables unchanged | 24 dependent review sessions |
| New lipid search | No complete admissible increment packet | No new construction or table |

'''+hist[end:]
text+=hist
text+='''The paired scientific-review programs repaired a divergent tail and a possible threshold-rounding failure, while 66/72 final tables remained byte-identical. Finite observed values do not prove a finite population mean; mathematical review and scientific accuracy are distinct. These older repairs are documented in the unchanged expanded manuscript and `work/scientific_check_revision_2026-11-11/RESULTS.md`. They are not credited as gains from the one-call content controls.

Reproduction has three levels: plotting released aggregates; resampling a frozen law under its recorded environment and access conditions; and initiating a new API construction using recorded prompts and tools. The last is stochastic and model availability can change. Earlier host-mediated episodes with incomplete backend identifiers are not described as fully recorded API runs. The controlled and content-control units retain explicit requested/returned IDs and usage. Independent numerical recomputation here means a separate implementation within the same research process, not an external investigator's adjudication.

'''
text=text.replace('Panel f compares the primary absolute discrepancy after averaging within each construction.', 'Panel f compares the primary absolute discrepancy after averaging within each construction; its horizontal bars are arm means.')
text=text.replace('Panel f shows absolute log-OR discrepancy.', 'Panel f shows construction-level absolute log-OR discrepancies and horizontal arm means.')
(M/'DRAFT_v0_33.md').write_text(text.replace('FIGDIR',F),encoding='utf-8')
print({'words':len(text.split()),'figures':text.count('!['),'output':'DRAFT_v0_33.md'})
