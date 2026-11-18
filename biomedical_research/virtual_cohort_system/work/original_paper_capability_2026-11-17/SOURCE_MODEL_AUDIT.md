# Original-paper to model: source and implementation audit

17 November 2026 (America/Chicago). Root performed this source/code review using original materials, delivered tool results and all six immutable programs. Numerical analysis was separately recomputed with an independent implementation. This is not an external clinical adjudication or a validated confidence score.

## What the Agent actually did

All six fresh sessions accessed the original paper, chose additional searches, authored an executable generator plus parameters and provenance, inspected one generated-only trial, and retained their first candidate. Three original-paper BP constructors reconstructed an age/BMI partial covariance from the original correlation matrix. All three iron constructors independently collapsed the original eight-category table to a two-by-two table and distinguished crude from adjusted odds. These source derivations were not supplied in the task or by a coordinator-written numerical packet.

The coordinator supplied a known original-paper entry point, target-population/schema definition, analysis definitions, general model requirements, tools and budget. This demonstrates paper interpretation/model authorship from that entry point. It is not unaided discovery of the anchor study. The final records are sampled by the program written by the Agent; there is no host-authored scientific parameter template. The Agent chooses the probability law and numeric assumptions, and deterministic isolated tools execute it.

| Session | Model calls | Literature queries | Download attempts charged | Candidates / trials | Estimated USD |
|---|---:|---:|---:|---:|---:|
| P1_IRON_A1 | 21 | 4 | 2 | 1 / 1 | 0.1973 |
| P1_IRON_A2 | 22 | 6 | 0 | 1 / 1 | 0.2134 |
| P1_IRON_A3 | 23 | 6 | 2 | 1 / 1 | 0.2480 |
| P1_PNS_A1 | 28 | 7 | 2 | 1 / 1 | 0.2903 |
| P1_PNS_A2 | 25 | 5 | 2 | 1 / 1 | 0.3127 |
| P1_PNS_A3 | 23 | 5 | 2 | 1 / 1 | 0.2497 |

Download counters are the adapter's charged attempts, including screened/failed full-text requests; they are not counts of distinct usable papers. Full tool paths, byte hashes and delivered source parts are in `audit/TRACE_SUMMARY.json`. Each candidate has one immutable version, one trial, and three subsequent final seeds. Therefore this experiment does not estimate a revision benefit.

## Source interpretation and composition

**Blood pressure.** The original [Burkina Faso study](https://doi.org/10.1136/bmjopen-2024-089374) supplies arithmetic SDs, a Pearson correlation matrix, and fully adjusted BMI coefficients. All three Agents correctly distinguish the raw SBP/DBP correlation from the age/BMI partial correlation they calculate. The latter is approximately0.788; source residual SDs are approximately17.6/10.8mmHg. It does not include sex adjustment. All authors explicitly mark transfer to a different age range, treatment-inclusive population, measurement protocol and smaller adjustment set as an assumption. Supplementary Mexican/Brazilian papers are actually retrieved, not merely named in the final notes. PNS_A1's gamma-regression overweight contrasts are context, not mislabelled as continuous BMI coefficients. PNS_A3 uses sex-specific ELSA marginal means as conditional anchors and discloses this approximation.

**Iron status.** The original [Zhu study](https://doi.org/10.1024/0300-9831/a000014) has eight rows split by folate/B12/ferritin status. Each author recovers173/85/331/1082, crude OR6.65314, and distinguishes TableV's adjusted OR6.448. Each also recognizes inconsistent ferritin unit labels and broad intervals around geometric means, and does not substitute folate/B12 correlation for Hb/ferritin. Supplemental Canadian summaries change the marginal ferritin assumptions rather than blindly carrying over the Chinese deficiency prevalence. Access to the Canadian source is abstract-level; its population and measurement applicability are not certified. A1 additionally uses New Zealand Hb data; A3 reads Dutch donor methods as qualitative mechanism context. Neither paper identifies the target joint law.

`audit/SOURCE_DERIVATION_RECHECK.json` records the independent arithmetic. These checks establish traceable extraction and algebra, not clinical portability or automatic source certification. The exact wording of confidence/interval labels remains the original source's ambiguity, not repaired evidence.

## Model choices and remaining assumptions

| Session | Actual model choice | Most consequential unresolved choice |
|---|---|---|
| PNS A1 | Gamma BMI; joint lognormal DBP and positive pulse pressure | Demographic law and covariance/fully adjusted slope transport |
| PNS A2 | Lognormal BMI; DBP shifted by30 plus positive pulse pressure | Marginal/conditional and selection transport; incidental preview |
| PNS A3 | Beta age; gamma BMI; ELSA pressure anchors; positive pulse pressure | Marginal source levels used as conditional intercepts |
| Iron A1 | Hb mixture, ferritin lognormal, Clayton copula solved from OR | Unmeasured Hb mixture and copula-dependent rank relationship |
| Iron A2 | Two store components, inflammation, Hb hinge response | Assumed5% background anemia; transferred crude OR |
| Iron A3 | Lognormal stores, inflammation/other anemia, saturating Hb response | Source stratum anemia risks transferred; assumed continuous law |

All selected programs match the declared major scientific structure and parameters on code inspection. The BP construction uses positive DBP and positive pulse pressure, so SBP>DBP structurally; all27000 final BP rows satisfy this. Bounded age and gamma/lognormal BMI have finite relevant moments; conditional pressure means are linear in BMI with bounded age terms and fixed finite conditional variances. Iron A1 has bounded Hb/lognormal ferritin; A2/A3 use finite lognormal mixtures and lower-truncated normal Hb. Inspection finds no version of the earlier infinite-mean construction here. This is mathematical inspection of the particular selected laws, not proof of biomedical realism for every tail.

No selected program reads target data or performs realized-sample moment forcing, seed selection or target-based correction. Algebraic root finding in the iron models calibrates a probability law to the chosen source constraints before sampling, which is legitimate source fitting. Some notes describe a numerical root as unique; a general uniqueness proof is not supplied and is not claimed in this report. Six distinct program hashes and18 distinct final table hashes are retained. No scientific code was edited after submission.

## Delivered-source exposure

The conservative screen was imperfect. PNS_A2 received an incomplete search preview for [DOI10.1111/jch.13292](https://doi.org/10.1111/jch.13292), identifying the2013 Brazilian survey, n59402,56%women, ages18–100, methods and the qualitative obesity/BP question. The author explicitly excluded it and did not open it. The delivered preview did not contain the evaluated BMI coefficients or residual correlation. There is no visible use as a parameter source, but absence of visible use does not prove no influence. Retain the author and flag; do not replace it. PNS_A1 also received an NHANES2011–2020 cardiovascular-model preview and a different Chilean survey preview, and PNS_A2 received a Mexican survey preview; none was opened or declared as an adopted source. Exact delivered-result hashes are retained.

The API authors never received the local target records, aggregate answer files or final target-comparison feedback. This narrower statement is supported. A claim of perfectly target-free literature exposure is not. Both target families were already exposed at project level in any event.

## Decision

The feasibility gap was real and is now addressed: these Agents read original tables, compose useful statistics, choose differing laws, write code and deliver analyzable cohorts without host-filled relationships. This does not make every generated relationship accurate. The blood-pressure slopes are promising in this closed batch; iron dependence and prevalence remain materially discrepant. Preserve both as the capability and its current boundary. No additional repair or construction is authorized by this completed protocol.
