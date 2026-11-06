# Source review for the iron pilot

Reviewed 2026-11-05 against the two original publications. The review accessed source articles only.

### Zhu et al., northern China

Xianghe, June 2004. Six townships identified 2,084 mothers in delivery logs, 1,702 participated and 1,671 met eligibility. Participants were parous, nonpregnant, nonlactating IUD users, 2–4 years postpartum. Eligibility excluded several chronic conditions and recent multivitamin use. The team measured fasting venous Hb in duplicate with HemoCue, and raw EDTA plasma ferritin by Randox immunoturbidimetry. These eligibility and assay differences matter for transfer. [Methods, pp. 145–146](https://storage.imrpress.com/imr/journal/IJVNR/article/501902/1752835456699.pdf#page=3)

Table I gives mean age 30.9 years (SD 4.2), mean BMI 23.9 kg/m² (SD 3.8), ferritin 17.4 and Hb 129.9 g/L. The latter two appear beneath the geometric-mean heading, while Table II and accompanying prose label Hb as a mean. I recommend recording Hb 129.9 as a descriptive location with statistic-type ambiguity. Interpret ferritin in µg/L based on Tables III–V and the Table I cutoff. The Table I concentration row and a methods cutoff unit disagree with those labels. [Tables I–II](https://storage.imrpress.com/imr/journal/IJVNR/article/501902/1752835456699.pdf#page=4)

| Source Hb band, g/L | n | Geometric mean plasma ferritin, µg/L | Raw ferritin <15 µg/L |
|---|---:|---:|---:|
| <100 | 53 | 1.3 | 94.3% |
| 100 to <120 | 205 | 5.9 | 60.0% |
| ≥120 | 1,413 | 22.3 | 23.4% |

The Table III ferritin statistic is exp(mean(log ferritin)) in each Hb band. Preserve its operator when replaying a generator. The paper labels its broad parenthetical intervals 95% CIs. Their construction is insufficiently specified to infer either individual-level spread or sampling SEs; admit the rounded point summaries. These three summaries and the binary counts describe overlapping women and therefore should not be weighted as independent observations. [Table III, p. 150](https://storage.imrpress.com/imr/journal/IJVNR/article/501902/1752835456699.pdf#page=7)

| Raw ferritin | Hb <120 g/L | Hb ≥120 g/L |
|---|---:|---:|
| <15 µg/L | 173 | 331 |
| ≥15 µg/L | 85 | 1,082 |

I summed Table IV across folate and B12 status. Column and row margins recover 258 low-Hb and 504 low-ferritin observations. The joint proportion is 173/1,671 = 10.35%. The cross-product OR is 6.6531. An ordinary independent-observation log-OR Wald interval gives 4.9916–8.8677 (derived). The published age/BMI/education-adjusted OR is 6.5 (4.9–8.7). Adding folate and B12 deficiency gives 6.448 (4.827–8.615). The latter two belong to their respective fitted analyses. These tables constrain binary dependence and ferritin by Hb band. They leave continuous within-band ordering and the exact Spearman coefficient undetermined. [Tables IV–V and adjusted analyses, pp. 148–151](https://storage.imrpress.com/imr/journal/IJVNR/article/501902/1752835456699.pdf#page=5)

### Pita-Rodríguez et al., Cuba

The 2016–2018 sample included 742 mothers aged 18–40 with a child aged 6–59 months, across selected Cuban regions. Pregnancy, recent delivery, specified acute or chronic diseases and hematological care were exclusion criteria. Hb was available for 729 women, ferritin and inflammatory measures for 711. Venous whole-blood Hb used a hematology analyzer; fasting serum ferritin, hsCRP and AGP used immunoturbidimetry. [Study methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC10049065/)

The reported association pairs Hb <120 g/L with serum ferritin <15 µg/L **after inflammation correction**. The authors used quantile regression and accounted for the sampling design in the binary association analysis. The OR is 3.023 (95% CI 1.816–5.033). Correcting ferritin for inflammation is conceptually distinct from multivariable adjustment of an odds ratio. A fitted correction formula sufficient for exact replay could not be recovered from the article's methods and tables. Use this estimate as contextual evidence about another source operator. Keep it separate from the raw ferritin four-cell estimate. [Sections 2.2–2.3 and 3.4, Table 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC10049065/)

The pilot may transport the raw binary association, absolute burden and continuous rank association as separate questions. Selection, specimen and assay differences remain part of generator uncertainty. An individual synthetic row carries no measured clinical value.
