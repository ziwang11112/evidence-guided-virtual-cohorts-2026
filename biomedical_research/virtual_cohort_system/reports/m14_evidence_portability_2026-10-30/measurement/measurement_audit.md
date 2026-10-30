# M14-A measurement and uncertainty evidence audit

30 October 2026. **No defensible, uncertainty-aware conversion from the admitted source measurements to Discovery A / Apex 4.0 / NHANES BCA was established by these three selected studies.** There are real quantitative instrument comparisons, but the missing links are material. No generator, target data, target analysis, calibration or framework code was changed.

The three primary studies were selected and sent to the coordinating agent before their full relevant methods/results/tables were read. Selection was fixed; no favorable substitutions were made. Official CDC documentation was consulted only for measurement definitions. The local source packet supplied the previously admitted instrument identities. Full relevant article text was available for all three through the routes recorded below; only Hull's original author-manuscript PDF was successfully cached. Failed HTML/XML responses are not full texts.

## Evidence-to-analysis decisions

| Proposed constraint | Audit outcome | Analyses it could affect if its instrument conditions were met | Why it cannot repair this case as a supported revision |
|---|---|---|---|
| Diessel in-vivo DPX-IQ to QDR-4500 percent-fat equation | Usable reported constraint, restricted to the compared systems/cohort | Location, proportional slopes, transformed spread | No measured QDR-4500 to target Discovery A/Apex 4/BCA step; DPX-IQ software/site equivalence unknown; no coefficient uncertainty or individual calibration error reported numerically |
| Hull DPXL/Prodigy to iDXA component equations | Usable reported constraint, restricted to the compared systems/cohort | Fat/lean/BMC harmonization, including sex-specific effects | Inputs are component masses in kg, not BMI or percent fat; current source equations supply neither individual lean nor bone mass. Versions differ from Gallagher. Prodigy Pro equivalence to the tested Prodigy is unestablished |
| Shepherd Prodigy/enCORE 14 to Hologic Discovery/Delphi Apex 3.0 PFAT | Usable reported constraint, restricted to the compared systems/cohort | Proportional location/slope/spread conversion; internal calibration prediction error | Does not measure old source instruments, target Apex 4/BCA, or source software upgrades. Adult sample is entirely Chinese; sparse ages 20-50. BCA status and component-denominator ambiguity unresolved |
| Treat NHANES BCA as +5 percentage points | Incompatible | Would shift means only, if imposed | CDC defines addition of 5% of lean mass to fat mass, not addition of 5 pp to percent fat |
| Under a mass-preserving lean-to-fat reallocation, derive delta percent fat =5L/T pp | Defensible derived constraint, conditional algebra only | Distinguishes mass conversion from a constant offset | Requires the correct pre-BCA Hologic lean and denominator; cannot map arbitrary Lunar predictions; does not supply missing calibration uncertainty |
| Use phantom SD, component SEE or calibration RMS-CV as sex/age/BMI biological residual SD | Incompatible | None as currently justified | These quantify different errors. No selected study supplies the needed conditional biological variance law |
| Compose the reported equations into one source-to-target bridge | Unresolved assumption / no-go | Could change all quantitative associations and intervals | Software, model, population, component and covariance links are missing; algebraic composition does not validate them |

## Exact reported comparisons

### Diessel et al. 2000

[Publisher](https://journals.physiology.org/doi/full/10.1152/jappl.2000.89.2.599), DOI 10.1152/jappl.2000.89.2.599; relevant pages 600-603, Table 1 and Figures 1-4. Author-uploaded original article was readable as [full-text transcription](https://www.researchgate.net/publication/12393120_Evaluation_of_a_new_body_composition_phantom_for_quality_control_and_cross-calibration_of_DXA_devices).

Healthy men/women, three US sites; 45 San Francisco participants had paired DPX-IQ/QDR-4500 scans. Age/BMI ranges and sex counts are absent. DPX-IQ/QDR-4500 software versions and paired scan interval are unreported. Linear regression used scanner percent fat without covariates. The text reports 130 volunteers, whereas Table 1 lists 45/75/75/10 comparison counts; do not add these into a unique sample. Participant overlap with prior source cohorts is unverified.

| Orientation | Equation; x and y in percentage points | Location |
|---|---|---|
| DPX-IQ to QDR-4500, human paired data, n=45 | y=3.68+0.807x | Figure 4 |
| DPX-IQ to QDR-4500, phantom | y=-2.35+0.966x | Figure 4; deliberately not a biological constraint |
| QDR-1500 to QDR-4500, Memphis, n=75 | y=1.30+0.832x | Figure 1 |
| QDR-1500 to QDR-4500, Pittsburgh, n=75 | y=2.67+0.791x | Figure 2 |
| QDR-4500 Memphis to Pittsburgh, n=10 | y=-0.66+1.019x | Figure 3 |

DPX-IQ human/phantom slopes and intercepts differed (p<0.05). No coefficient SE/covariance, numerical regression SEE or individual limits are supplied. Phantom repeated-scan SDs are 0.6 pp (QDR-4500) and 0.8 pp (DPX-IQ), not human residual SDs. This comparison does not establish QDR-1000/enhanced-software equivalence, nor the QDR-4500 subtype's equivalence to the later target. The bridge's direction is preserved, including its tendency toward lower QDR-4500 values at higher fatness.

### Hull et al. 2009

[Primary article record](https://pmc.ncbi.nlm.nih.gov/articles/PMC2661815/), DOI 10.1016/j.jocd.2008.09.004. Local `local_sources/hull2009.pdf` is the NIH author manuscript, 15 pages; methods pp 2-3, results pp 4-7, Table 1 p 9, Table 4 p 15. Table 4 was visually checked after rendering. The primary BioC fulltext independently returned valid XML; the ordinary PMC HTML requests returned challenge pages.

Community volunteers at St Luke's-Roosevelt, New York: 47 men / 52 women; three scans within 3 hours. Men age 19-76, BMI 19.2-35.0; women age 18-81, BMI 18.1-46.4. Maximum admission weight 300 lb. Equipment: DPXL 4.7e, Prodigy 8.80, iDXA 10.40. Sex entered regression; no age/BMI conditional biological model. The same 99 people supply all equations, without an independent validation sample. Shared institution/authors with Gallagher 2000 do not prove either overlap or independence; participant linkage unavailable.

All Table 4 equations below predict **iDXA mass in kg**, y=a+b*x. SEE is pooled model prediction residual error in kg; it is not a coefficient SE or a percent-fat SD.

| Input component/system | Women a,b | Men a,b | SEE, kg | R² |
|---|---:|---:|---:|---:|
| Fat, DPXL |2.032,1.003|5.073,0.925|1.090|0.99|
| Fat, Prodigy |1.171,0.944|1.829,0.944|0.968|0.99|
| Lean, DPXL |-3.486,1.052|-3.486,1.005|1.181|0.99|
| Lean, Prodigy |0.405,1.005|0.405,0.978|1.290|0.99|
| Bone, DPXL |0.072,0.956|0.072,0.956|0.092|0.97|
| Bone, Prodigy |0.219,0.883|0.219,0.912|0.113|0.96|

Coefficient SE/covariance and residual covariance across fat/lean/bone are unreported. Algebraically inverting a regression would not establish a reverse conditional prediction. The paper supplies no DPXL 1.3z to 4.7e, DPX 3.6 to DPXL, Prodigy Pro to Prodigy 8.80, or Prodigy 8.80 to enCORE 14 comparison. Its kg equations cannot be applied directly to Pasco's percent-fat regression or Gallagher's percent-fat predictions.

### Shepherd et al. 2012

[Publisher](https://onlinelibrary.wiley.com/doi/full/10.1002/jbmr.1654), DOI 10.1002/jbmr.1654; pp 2209-2215, Tables 1-4. Relevant full article text read in the [author-uploaded transcription](https://www.researchgate.net/publication/225059064_A_multinational_study_to_develop_universal_standardization_of_whole-body_bone_density_and_composition_using_GE_Healthcare_Lunar_and_Hologic_DXA_systems); publisher-indexed Table 3 independently confirms the PFAT equation. Original PDF retrieval failed; numerical values were text-checked, not visually verified from a PDF.

199 usable paired participants: 40 US children and 159 China participants, including all 108 adults. 91 were below 20, 97 above 50, and 11 between 20 and 50. 121 scans were lost to corrupted files. Prodigy/enCORE 14.0 versus Discovery (US) or Delphi (China)/Apex 3.0; the Discovery subtype and BCA option are not stated. Abstract gives same-day US/within 1 week China, whereas methods says same-day; retain conflict. No external validation; internal resubstitution and .632+bootstrap. Tested demographic covariates were not retained for soft tissue; that is not proof of transport invariance. Cohort was recruited separately from NHANES. NHANES population CV comparators in Table 4 are excluded as generator evidence.

| PFAT orientation; percent units | Published equation | R² | .632+bootstrap RMS-CV |
|---|---|---:|---:|
| Hologic Apex 3 to Prodigy/enCORE 14 |GE=-2.173+1.119H|0.97|0.0478|
| Prodigy/enCORE 14 to Hologic Apex 3 |H=1.943+0.894GE|0.97|0.0359|

These are reversible Deming relations (rounded publication coefficients), not age/BMI regression slopes. No coefficient covariance, calibration-error distribution, sex/age/BMI error law or cross-site covariance is available. RMS-CV is internal calibration prediction error, not a posterior distribution for the bridge.

**Component-convention inconsistency:** methods defines TM=LSTM+BMC+FM; Table 2 adult Hologic TM 58538.3 g instead equals 38973.4 g LSTM + 19564.9 g FM, without separately adding listed BMC 1763.2 g. The two pediatric Hologic groups show the same identity. In contrast, adult GE TM 58715.1 g equals 35984.5 g LSTM + 20794.5 g FM + 1936.1 g BMC; its pediatric groups also include BMC separately. Thus the Hologic quantity labeled LSTM may already include bone. The derivation LSTM=(1-PFAT)*TM also omits bone. This establishes a reporting/convention ambiguity, not a demonstrated PFAT denominator mismatch; do not silently choose an interpretation. Abstract mean age 44.2 also differs from Table 1 pooled 36.8. Neither inconsistency was used to select an estimate. All Chinese adults limit direct inference for US adult White/Black populations, and there was no inter-site phantom cross-calibration.

## Target definition and uncertainty boundary

The official [CDC DXX_J documentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DXX_J.htm), Protocol and Procedure, Scan Analysis, and Data Processing/Editing, specifies Discovery model A acquisition using Apex 3.2, analysis using Apex 4.0, and NHANES BCA enabled. Its first protocol paragraph calls the file DXX_I, but the later Scan Analysis paragraph explicitly identifies 2017-18 and confirms Apex 4.0. Retain that copy-label inconsistency. The [2018 procedures manual](https://wwwn.cdc.gov/nchs/data/nhanes/public/2017/manuals/Body_Composition_Procedures_Manual_2018.pdf), section 2.1.1, identifies Discovery A fan-beam hardware. These are technical definitions, not new biological cohorts.

CDC describes BCA as adding 5% of lean mass to fat mass. For fixed total denominator T and eligible pre-adjustment lean L, algebra gives deltaPFAT=5L/T percentage points. Only if L=T-F does this simplify to PFAT'=5+0.95PFAT. If bone is outside L, a bone-fraction term remains. This is conditional algebra, not a verified exact implementation formula and not a Lunar-to-Hologic calibration. Do not apply BCA again to already adjusted target values.

Measurement-error spread, biological variation conditional on covariates, estimated bridge uncertainty and structural transport uncertainty are distinct. Hull's kg SEE cannot determine a percentage variance without components and their residual covariance. Shepherd's RMS-CV does not identify a Gaussian homoscedastic error or sex/age/BMI heteroscedasticity. Diessel's phantom SD does not identify biological variance. None provides uncertainty weights for choosing between structural alternatives.

For any genuinely valid linear bridge y=a+b*x, known a and b would give conditional mean a+b*E[x|covariates], multiply slopes by b and residual SDs by abs(b), while an uncertain shared a/b would also induce correlated uncertainty across generated participants. More independent residual draws cannot represent that shared uncertainty. Here those required coefficient covariances and applicability checks are unavailable, so no uncertainty distribution is invented.

## Measurement go/no-go

**No-go for a source-supported exact target measurement correction in this bounded unit.** The three papers justify rejecting generic offsets and unsupported software equivalence. They do not justify a numerical repair of the exposed target's means, BMI effects or male-age inference.

Pasco's DPX-L/Prodigy Pro instrument families partly overlap Hull/Shepherd, but the tested models/versions and output components are not the same established configuration. A valid future bridge would need matched same-person measurement across the specific source software(s) and Discovery A/Apex 4/BCA, documented endpoint denominators, relevant adult BMI/sex support, coefficients and covariance, individual calibration errors, and validation on independent people. For a multi-step bridge, every link and shared-error covariance needs support; labels such as Lunar or Hologic are insufficient. A separate reserved evaluation target would still be required after any candidate/protocol freeze. No new target or study is acquired by this recommendation; the audit stops here.

`search_retrieval_ledger.json` records actual queries, selection/exclusion and retrieval limits. `source_extractions.json` preserves numerical facts and explicit null uncertainty. `local_file_manifest.json` hashes local retrieval bytes, including failed responses; only identified successful sources are scientific evidence. Original PDFs and fulltext caches stay local and must not be added to the distributed evidence packet.
