# Independent scientific provenance audit: request-only repeatability

**Status: complete bounded review of 12 frozen authors and 36 requested-analysis mappings.** This is a source/code audit, not an evaluation of clinical reference agreement.

## Inspection boundary

Read only frozen candidates/specs/notes, final-selection narrative and captured original sources. Final-selection narratives include author-reported generated-only diagnostics; these were not used as truth. No EVALUATION, clinical reference, old target or patient/generated-row file was opened. No generator execution/new API/new paper. Prior historical result exposure is not a claim of personal blindness.

Bounded key-parameter maps for three requested analyses per author, not exhaustive parameter truth or extraction-accuracy certification. No target-usefulness verdict. Do not modify frozen methods from this audit.

No frozen candidate was edited, no generator was executed, and no target result or patient/generated-row file was opened. Static numerical calculations below check finite-dimensional covariance matrices and extrema of declared formulas; they do not sample data or estimate clinical effects.

The reviewer has prior historical project exposure. The accurate description is “current-run source/code-only audit,” not personal blinding. Source text, statistical definitions and code are the basis of these findings.

## Findings that change interpretation

1. All 12 authors submitted and selected v001 only. Existing execution and generated-only self-checking do not demonstrate scientific feedback revision.
2. All 12 maps contain joint-model or transfer assumptions. A correct unit conversion or Schur derivation does not certify transport or equality to the requested pooled analysis.
3. PNS_BASE_R3 alone draws shared cohort-level slope and residual-correlation parameters per seed; its seed spread mixes scenario and participant variability.
4. LIPID_BASE_R2 has an infinite ideal-law raw TC mean because a positive exponential nests an unbounded lognormal BMI. Finite successful tables do not refute this mathematical result.
5. LIPID_BASE_R1 has finite actual capped outputs. Its analogous uncapped law is a counterfactual with divergent TC mean; the two findings must not be conflated.
6. Both R3 lipid authors independently use positive component identities that guarantee TC>HDL, with different assumed residual structures. Earlier four lipid laws do not enforce that identity. No target or violation-count claim is made.
7. The three workflow lipid authors use different missing-scale/dependence strategies: IQR-derived source scale plus longitudinal variance decomposition; assumed BMI SD and raw conditional error correlation; transported standardized coefficient plus conditional component independence. This is a concrete modeling difference, not evidence that one is clinically superior.

The component and dependence choices show that both policies can make substantive scientific modeling decisions. These observations do not establish a policy winner. A matching source parameter, an executable generator and a useful analysis in a new population are separate claims.

## Uniform mathematical-tail audit

Every frozen law was checked for covariate support, output transformation, residual distribution, parameter mixing, truncation/caps and dependence on successful rejection. The table concerns positive moments of the modeled outputs; finite moments do not establish plausible tails or transport.

| Author | Frozen-law finding | Code lines |
|---|---|---|
| LIPID_BASE_R1 | FINITE_ONLY_WITH_IMPLEMENTED_CAPS — log(BMI) and log(lipid) caps [-30, 30] bound all outputs. Removing caps gives positive exponential of unbounded lognormal BMI and divergent TC mean. No inference about cap-hit frequency is made. | 25, 29, 34, 50 |
| LIPID_WORKFLOW_R1 | FINITE_MOMENTS_BOUNDED_MEAN_LOGNORMAL_NOISE — Age and BMI are bounded. Static endpoint checks of four affine TC/HDL means gave minimum TC 2.7476310287 and HDL 0.6197841244 mmol/L, so means stay positive and bounded. Fixed Gaussian lognoise has finite exponential moments of every fixed order. | 22, 59, 62, 71 |
| PNS_BASE_R1 | FINITE_RETURNED_BOUNDED — Covariates and accepted outputs bounded; pre-guard gamma/normal innovations also have finite moments. | 11, 28, 36, 78 |
| PNS_WORKFLOW_R1 | FINITE_MOMENTS_AT_FROZEN_SPEC — Bounded age/sex; lognormal BMI with bounded positive conditional means and fixed CV; affine BP mean in BMI plus Gaussian error. Static residual-covariance eigenvalues 27.2649309763 and 292.9425153206 are positive. For large BMI both DBP mean and pulse-pressure mean grow positively, so admissibility probability tends to 1; on remaining compact covariates it has a positive minimum. Accepted-moment integrability follows from Gaussian/lognormal moments and this bound. | 13, 48, 50, 85 |
| LIPID_BASE_R2 | IDEAL_TC_MEAN_DIVERGES_NO_CAP — See conditional proof. Only age is truncated. The actual specified ideal law, not merely a removed-cap counterfactual, nests positive exponential around unbounded lognormal BMI. | 18, 25, 31, 45, 46, 53 |
| LIPID_WORKFLOW_R2 | FINITE_MOMENTS_BOUNDED_MEAN_LOGNORMAL_NOISE — Bounded covariates and affine conditional means. Across setting/sex/support endpoints minimum TC 3.081 and HDL 0.727125 mmol/L. Fixed lognormal multipliers have finite moments of every fixed positive order. | 15, 27, 29, 51 |
| PNS_BASE_R2 | FINITE_RETURNED_BOUNDED — Accepted outputs bounded. Pre-rejection t7 has finite variance and moments of order < 7; do not claim all pre-guard moments exist. Final bounds make successful returned moments finite. | 14, 31, 44, 78 |
| PNS_WORKFLOW_R2 | FINITE_RETURNED_BOUNDED — Bounded covariates and accepted BP. Positive nondegenerate Gaussian probability of the acceptance region gives almost-sure ideal rejection termination; no fixed wall-time guarantee. | 34, 59, 82, 114 |
| LIPID_BASE_R3 | FINITE_MOMENTS_BOUNDED_MEAN_COMPONENT_LOGNORMAL — Endpoint minima for HDL/LDL/remnant conditional means are 0.63525/1.4425/0.222 mmol/L; log-error correlation eigenvalues 0.665479/1.134521/1.2 are positive. Age/BMI are bounded and all fixed lognormal moments exist. | 16, 27, 29, 49 |
| LIPID_WORKFLOW_R3 | FINITE_MOMENTS_BOUNDED_PARAMETERS_COMPONENT_GAMMA — For women, minimum HDL/non-HDL means 0.979875/1.79325, variances 0.08911575/0.628688; for men minima 0.8669/2.18035, variances 0.10150575/1.024938. Means are affine on bounded covariates; positive minima bound gamma scale and shape. CDF probabilities are clipped to [1e-12,1-1e-12], which imposes additional numerical support, not empirical validation. | 25, 26, 28, 83 |
| PNS_BASE_R3 | FINITE_RETURNED_BOUNDED — Age 20–79, BMI accepted in 15–55, and final SBP 60–270/DBP 30–160 with pulse pressure >10 are bounded. Gaussian cohort-level slopes are unbounded, but returned outputs remain bounded conditional on successful completion. This is not a guarantee of success for every possible global draw. | 35, 57, 98, 122 |
| PNS_WORKFLOW_R3 | FINITE_RETURNED_BOUNDED — Bounded age 20–79/BMI 14–60; accepted SBP 70–260/DBP 40–150 with pulse pressure >=15. Sex-specific source-derived residual matrices are positive definite (Schur eigenvalues M 0.33138,1.52413; F 0.23531,1.47678). | 9, 25, 41, 79 |

Statements concern the ideal stochastic law represented by formulas or bounded returned support. Finite-resolution PRNG/IEEE arithmetic may overflow, round or impose implicit numerical limits; ordinary successful finite tables do not prove population moments.

### Exact distinction between the two BASE lipid laws

**LIPID_BASE_R2: actual ideal stochastic law.** Fix bounded age, sex and setting. Its BMI is B = 12 + exp(Z), with Z Gaussian and positive conditional variance (generator line 25). TC can be written A exp(cB) U, where A > 0, c = 0.055/3.8 > 0, and U is an independent positive mean-one lognormal multiplier (lines 31–44). There is no subsequent TC or BMI cap (return at lines 46–53). The integral of exp[c exp(z) − (z−mu)^2/(2 sigma^2)] diverges because its positive exponential term dominates the negative quadratic. Nonnegativity and independence therefore give E(TC | age, sex, setting) = infinity. The finite-mean population interpretation of raw TC and its usual Pearson/OLS moments is unavailable under this ideal law. Arithmetic OLS and correlations computed on a finite table remain computable; successful finite draws do not settle integrability.

**LIPID_BASE_R1: actual capped law and a counterfactual.** The shipped code clips log(BMI) and log(lipid) to [-30, 30] (BMI line 29; lipids lines 49–50). Its actual output support is bounded and moments finite. Removing these caps would produce a positive exponential of unbounded lognormal BMI and a divergent TC mean, but that is a different law. The warranted concern is dependence of tail properties on numerical caps, not a claim that this shipped candidate has an infinite mean. No cap-hit rate or performance impact was measured.

These are mathematical claims about the specified continuous laws. Finite-resolution PRNG and floating-point arithmetic are not literal Gaussian probability spaces; overflow, finite machine support and observed finite cohorts must be reported separately. Neither finding permits altering or dropping this frozen batch after inspection.

## Seed interpretation and sampling unit

All 12 candidate programs were inspected for cohort-global random draws. Only PNS_BASE_R3 draws a shared BMI-slope pair and a shared person-residual correlation before drawing rows (lines 35–43). Its slope center and widths are agent assumptions informed by different sources, not a calibrated posterior; person rho is Uniform(0.50, 0.75). Conditional on these shared parameters its rows are independently drawn, but integrating over them induces dependence between rows. Its three-seed range includes global scenario variability as well as participant variability.

The other 11 frozen laws use fixed scientific parameters and participant-level random draws. Deterministic marginal-moment solvers in LIPID_WORKFLOW_R3 are not cohort-global random draws. For all 12, seeds remain nested within one author; they do not create extra independent authors or a calibrated transfer confidence interval.

## Per-author source-to-code maps

All line locators below refer to that author’s `candidates/v001/generator.py`. Hashes for source captures, generator, specification, notes, manifest and selection are in the companion JSON. A source hash binds the captured artifact, not an assertion that every section of every retrieved paper was exhaustively audited.

### LIPID_BASE_R1

Captured Kenya Table 1 and Ghana methods/Tables4–5 directly checked; log base unspecified in retrieved Ghana text.

| Requested analysis | Original statistic and source | Adopted implementation | Remaining assumptions and transfer conditions | Code lines |
|---|---|---|---|---|
| BMI–TC adjusted association | PMC6261546 Tables5/methods; PMC6435188 Table 1 — Sex-stratified log-lipid regressions: univariate TC BMI0.013eachsex; multivariable0.010men/−0.009women with other adiposity adjustment | Assumed/attenuated natural-log TC slope0.012perBMI; Kenyan means treated as conditional anchors | Univariate/multivariable coefficients differ from requested raw age/sex-adjusted OLS; Natural-log convention not confirmed by retrieved text; Nonlinear response plus scenario covariate mixture affects raw projection | 25, 29, 34, 50 |
| BMI–HDL adjusted association | PMC6261546 Table 4/methods — Male log-HDL BMI univariate−0.007 and multivariable0.001, uncertain; female coefficient not furnished in adopted row | Assumed pooled natural-log slope−0.005 | Not a demonstrated female inverse association; Conditional-to-pooled raw-scale projection and cross-population transfer | 34, 50 |
| TC–HDL residual dependence | No adopted direct residual correlation source; Kenya marginal SD rationale — Marginal HDL/TC spread does not identify raw conditional covariance | Assumed joint log-error rho0.35; sex-specific logSD TC0.22/0.25 andHDL0.24/0.28 | A heuristic shared-HDL rationale does not make0.35 an extracted estimate; Two separate lognormal outputs do not enforceTC>=HDL; Raw pooled OLS correlation differs from latent log-error rho | 42, 50 |

**Tail/support:** Actual code clips log(BMI) and log(lipid)s to[-30,30] at lines29,49–50, so shipped values are bounded and have finite moments. Counterfactual unclipped law has lognormalBMI entering positive0.012 TC logmean; E[exp(0.012BMI)] diverges. Finite-moment behavior therefore depends on numerical caps, and exact arithmetic-mean correction is broken where clipping binds. This is structural cap dependence, not measured poor target agreement. Do not label shipped candidate infinite-mean.

**Revision:** One candidate v001 retained; no post-execution scientific tuning. Reported rough source slopes and covariance remain declared assumptions.

### LIPID_WORKFLOW_R1

Captured Malawi Tables1–3, overlapping Malawi BMI IQR Table 1 and JHS model/Table 2 checked directly.

| Requested analysis | Original statistic and source | Adopted implementation | Remaining assumptions and transfer conditions | Code lines |
|---|---|---|---|---|
| BMI–TC adjusted association | PMC6747887 Table 3; PMC6005143 Table 1 — Malawi sex/area TC effects0.23/0.20/0.13/0.15 mmol/L per1SD BMI, fully adjusted; related survey BMI IQRs | Derived SD=age-adjustedBMImean*sqrt(exp((log(Q3/Q1)/(2Phi^-1(.75)))^2)−1); divide source effect byderivedSD | Approximate lognormalshape; IQR and age-adjustedmean from overlapping nonidentical subsets; Full source adjustment not requested age/sex projection; latent residence omitted; Centering age-standardized marginal means at pooled age approximates source operator | 30, 58 |
| BMI–HDL adjusted association | PMC6747887 Table 3; PMC6005143 Table 1 — Effects−0.03/−0.03/−0.05/−0.04 mmol/L per1SD BMI with broad adjustment | Same derivedSD denominator; raw conditional arithmetic mean slope | Same IQR/mean/subset/adjustment/mixture bridges; not exact physical-unit source recovery | 30, 58 |
| TC–HDL residual dependence | PMC7713018 model/Table 2 — JHS longitudinal log-lipid random-intercept SD TC0.1598/HDL0.2153, errorSD 0.1206/0.1200, random-interceptrho0.2235; multi-adjustment joint survival model | Random-effect covariance0.2235*0.1598*0.2153, totalvariances REvar+errorvar; independent cross-lipid errors; mean-one multipliers | Cross-population/longitudinal-to-single-measurement transport; Random-interceptrho not raw Pearson; rawconditional multipliercorr~0.153not requested pooled residualcorr; Separatepositive lipids do not enforceTC>=HDL; unmodeledstratum/heteroskedasticmeans affect pooled correlation | 62, 71 |

**Tail/support:** Bounded age/BMI domain; bounded positive affine lipid means times fixed-variance lognormal multipliers. All raw moments finite at fixed specification. No exp(positive unboundedlognormalBMI) nesting. Independent-error/lognormal model may generate HDL>TC despite positivity; no row count inferred.

**Revision:** One candidate v001 retained after execution. Source operators/derivedcovariance were chosen before finalization; no empirical demonstration of feedback-driven scientific revision.

### PNS_BASE_R1

Pivotal source methods/results and Table 1 checked directly in captured PMC5344187 and PMC7726937 XML.

| Requested analysis | Original statistic and source | Adopted implementation | Remaining assumptions and transfer conditions | Code lines |
|---|---|---|---|---|
| BMI–SBP adjusted association | PMC5344187 abstract/results/discussion; PMC7726937 Table 1 context — Approximately 3 mmHg per 4.5 kg/m2 BMI in adults35–89 without known chronic disease/antihypertensives; age/sex and district/education/smoking/activity/alcohol adjustment | 3/4.5*5 =3.333333 mmHg per 5 BMI in conditional mean | Approximate prose effect, not exact figure extraction; Restricted Mexican sample transported to unrestricted Brazilian analytical population; Chosen age/sex curves; reference contextual BP moments not conditional coefficients; Linear-age OLS omits nonlinear age/sex effects and guard selection | 30, 35 |
| BMI–DBP adjusted association | PMC5344187 abstract/discussion — Approximately 2 mmHg per 4.5 kg/m2 with same restrictions and broader adjustment | 2/4.5*5 =2.222222 mmHg per 5 BMI in conditional mean | Same transfer and approximate-prose limitations; Unrestricted target treatment mixture is not identified | 30, 35 |
| SBP–DBP residual dependence | No directly applicable residual-covariance source; PMC7726937 marginal scales and measurement protocol only — Local source BP summary averages all three measurements; no adopted adjusted joint covariance | Shared standardized gamma and independent normal innovations with rho 0.65; read-error rho 0.50; SD 5/3.5; default mean last two | Age-varying residual SD, gamma shape 3, reading offsets and aggregation are assumptions; Reading-average covariance differs from latent correlation; nonlinear mean misspecification and joint guards can change OLS residual dependence | 36, 78 |

**Tail/support:** Bounded age/BMI and accepted bounded BP; successful outputs have finite moments. Gamma/normal innovations have finite moments. Fixed rejection limits can fail but do not silently return a different accepted law.

**Revision:** One frozen candidate v001; selected unchanged after generated-only execution. No demonstrated scientific feedback revision.

### PNS_WORKFLOW_R1

Pivotal China-PEACE methods/results, ELSA dairy-group Table 2/methods, and POF demographic paragraph checked in captured XML.

| Requested analysis | Original statistic and source | Adopted implementation | Remaining assumptions and transfer conditions | Code lines |
|---|---|---|---|---|
| BMI–SBP adjusted association | PMC6324286 Results/Statistical Analysis — China-PEACE adjusted coefficient1.15mmHg/BMI; additional socioeconomic/geographic/treatment adjustment | Conditional slope1.15 perBMI =5.75per5 | Source conditional association not requested age/sex-only projection; ELSA marginal means/variances anchor a different selected sample; Chosen age/BMI/sex law and target demographic transport | 31, 41, 64, 70 |
| BMI–DBP adjusted association | PMC6324286 Results/Statistical Analysis — Adjusted coefficient0.75mmHg/BMI with same extra adjustment | Conditional slope0.75 perBMI =3.75per 5 plus chosen age quadratic−0.006 | Quadratic generating age term not included in primary linear-age regression; Transfer across adjustment/treatment/sample boundaries | 31, 44, 64, 70 |
| SBP–DBP residual dependence | PMC6024610 Table 2/methods; actual reference arrays — Dairy-stratum marginal SBP/DBP/pulse-pressure SDs; PP=SBP−DBP; last2of3 BP protocol | Cov(S,D)=(VarS+VarD−VarPP)/2 within group plus between-group covariance; subtract B Cov(X) B-transpose and chosen age-quadratic variance | Moment pooling ignores finite-n corrections/printed rounding; Reference normal age independentofsex, linear BMI mean and chosen effects; not empirically identified residual covariance; Target demographic/reference laws differ; Gaussian errors/rounding/redraw affect projections | 13, 48, 70, 85 |

**Tail/support:** Finite age support; fixed-CV BMI lognormal with bounded conditional means; BP affine in BMI plus bounded-age terms and Gaussian noise, then positive-order rejection. No positive exponential-of-unbounded-lognormal nesting. Finite raw moments at the frozen specification; unrealistic support/rare rejection failure remain separate questions.

**Revision:** One candidate v001; source algebra plus generated-only checking; no scientific revision. Root flags incidental excluded-family search exposure separately; numerical non-use is an author statement, not an audit guarantee.

### LIPID_BASE_R2

Captured Kenya v2 Table 1 and Tanzania/Uganda Tables2/4 reviewed directly; categorical LDL/HDL results and rural/urban marginals verified.

| Requested analysis | Original statistic and source | Adopted implementation | Remaining assumptions and transfer conditions | Code lines |
|---|---|---|---|---|
| BMI–TC adjusted association | PMC6897412 Tables2/4; PMC6435188 Table 1 — BMI-category LDL differences+0.23/+0.48; no retrieved continuous TC slope; external marginal TC anchors | Assumed local reference-scale TC derivative0.055 mmol/L perBMI implemented as exponential positive BMI term0.055/3.8 | LDL category evidence does not identify continuous TC regression; Population/adjustment/latentsetting transfer; Reference derivative not constant slope across covariate domain | 18, 36 |
| BMI–HDL adjusted association | PMC6897412 Table 4 — BMI-category HDL differences−0.06/−0.15 with broader adjustment | Assumed local HDL derivative−0.012 implemented as exponential term−0.012/1.15 | Categorical-to-continuous and cross-population bridge; Setting affects BMI/lipid means but omitted from requested OLS | 28, 36 |
| TC–HDL residual dependence | No adopted measured partial-correlation source — Source marginal SDs do not identify adjusted covariance | Assumed log-errorrho0.35 and CVtc0.22/HDL0.28 | TC containsHDL is qualitative rationale, not measured correlation; Separatepositive lipids allow HDL>TC; IdealTC infinite moment means requested population Pearson correlation is not defined; finite-table correlation still computable | 37, 53 |

**Tail/support:** IDEAL-LAW DIVERGENCE: conditional on bounded age/sex/setting, BMI=12+exp(Z), Var(Z)>0 (lines18–25); TC=A*exp(c*BMI)*U, c=0.055/3.8>0 (31–33), U independent mean-one lognormal (39–44). Eexp(c*expZ)=infinite; Tonelli implies E(TC)=infinite. No later cap/truncation/normalization (44–53). Finite floating-point/PRNG samples are not literal ideal Gaussian laws and may be finite or overflow; ordinary finite output is compatible with this finding. No target failure is inferred.

**Revision:** One candidate v001; no scientific revision. Tail finding must not trigger mid-batch repair or exclusion.

### LIPID_WORKFLOW_R2

Captured Tanzania/Uganda Tables2/4 and Malawi Table 3 reviewed directly; source units, full adjustment and fasting/nonfasting differences verified.

| Requested analysis | Original statistic and source | Adopted implementation | Remaining assumptions and transfer conditions | Code lines |
|---|---|---|---|---|
| BMI–TC adjusted association | PMC6747887 Table 3; PMC6897412 Table 2 — Malawi sex/area effects0.23/0.20rural and0.13/0.15urban per1SD BMI; Tanzania weighted marginal TC3.85/4.42/4.72 | Source effect divided by ASSUMED4kg/m2; rural slopes0.0575F/0.05M, nonrural0.0325F/0.0375M | SourceSD missing, not recovered; Anchored marginal means become conditional means; Fasting source associations and nonfasting marginal anchors; latentsetting omitted byanalysis | 29, 39 |
| BMI–HDL adjusted association | PMC6747887 Table 3; PMC6897412 Tables2/4 — Malawi effects−0.03rural,−0.05F/−0.04Murban per1SD BMI; TanzaniaHDL1.01/1.22/1.39 | Divide byassumed4; female shift0.08; assumedage0.0015 | Broad source adjustment differs from requestedmodel; Female shift/contextmixture transferred; sourceconditionalandmarginaloperatorsnotidentical | 29, 39 |
| TC–HDL residual dependence | No source adjusted-correlation estimate — Conditional raw-errorrho andCVs are assumed | rho_raw0.30,CVtc0.24/CVhdl0.28; algebraically convert to lognormalrho=log(1+r*CVtc*CVhdl)/(sigma_tc*sigma_hdl) | Valid conversion conditional on jointlynormal logerrors, not empiricalidentification; Pooled residualcorr changes with omitted setting and conditionalmeans; Separatepositive outputs permitHDL>TC | 41, 51 |

**Tail/support:** FINITE MOMENTS: age/BMI bounded; affine lipid means bounded and checked positive; fixed-variance bivariate lognormal mean-one multipliers have all positive moments finite. No positive exponential of unbounded lognormalBMI. Positivity alone does not impose physiological TC>=HDL.

**Revision:** One candidate v001; final diagnostics not a scientific parameter revision.

### PNS_BASE_R2

Adler background citation of INTERSALT, captured primary INTERSALT abstract, POF Table 1 and ELSA Table 1/methods checked. Primary full-text INTERSALT coefficient table not available here; mark secondary reporting.

| Requested analysis | Original statistic and source | Adopted implementation | Remaining assumptions and transfer conditions | Code lines |
|---|---|---|---|---|
| BMI–SBP adjusted association | PMC4514940 Background citing INTERSALT; PMID2810326 capturedabstract — Secondary reported BMI slopes0.91men/0.72women mmHg/unit; originalabstract supports age20–59 multiadjusted association but not these exactsex coefficients | Sex-specific conditional slopes0.91/0.72 | Secondary citation reliance; extrapolationto79 anddifferentadjustment; Heterogeneous slopes commonOLS isprojection; ELSA marginalBPmeans treated as conditional referencevalues | 33, 43 |
| BMI–DBP adjusted association | PMID2810326 abstract plus adoptedSBPcoefficients — Abstract reports3.0SBP/2.2DBP per10kgweight, notsex-specificBMI DBPslopes | Multiply sex-specificSBP BMIcoefficients by2.2/3 | Effectratio frombodyweight comparison transferredtoBMI sex-specificslopes; explicitlyapproximate; Population/age/treatment andadjustmenttransfer | 34, 43 |
| SBP–DBP residual dependence | No directly applicable residualcorrelation source; ELSA marginalBPcontext — MarginalsourceSDs not conditionalvariance; no measuredrepeaterrorlaw | Latent standardized bivariate t7rho 0.65; readingerrorsrho0.5,SD5/4averaged2 | Tailfamily/SD/aggregation assumed; t7 hasfinitevariance butguardedoutput bounded; Nonlinearage,sex-specificslopes andjointrejectionalter pooled residualcorr | 44, 78 |

**Tail/support:** FINITE MOMENTS of successful outputs: age20–79 andBMI14–60; BPacceptance SBP65–260/DBP35–155/pulsepressure15–130. Pre-guard standardized t7 innovations have finite second moments (not all higher moments); after guards returned pressures are bounded. A finite rejection budget can raise an error, not establish a heavy-tail failure of returned values.

**Revision:** One candidatev001; generated-only primary/flexible-age diagnostics; no scientificrevision.

### PNS_WORKFLOW_R2

Helsinki original Table 2 ABOVE-diagonal Pearson matrix and measurement/medication selection checked; EpiFloripa Table 1, ELSA Table 1/protocol and China-PEACE coefficient/operator checked.

| Requested analysis | Original statistic and source | Adopted implementation | Remaining assumptions and transfer conditions | Code lines |
|---|---|---|---|---|
| BMI–SBP adjusted association | PMC6324286 Results/StatisticalAnalysis; PMC3545980demographic/BMI andPMC4338719BPanchors — China coefficient1.15perBMI broadadjustment; Brazilian anchors aredifferentselectedpopulations | Conditional1.15perBMI; assumedagehinge/square andfemale−8 | RequestedlinearageOLS differentfromfullconditionalmodel; Under60EpiFloripa demographics enlargedbyassumedolderfractions; ELSAselectedBPlevels notpooledwithdiscordantEpiFloripa | 61, 80 |
| BMI–DBP adjusted association | PMC6324286; ELSABPlevels — China adjusted0.75perBMI | Conditional0.75pluschosen age50square−0.012,female−4 | Additionaladjustmentandpopulationtransfer; Chosen nonlinearage affects primarylinearageprojection | 61, 80 |
| SBP–DBP residual dependence | PMC4768573 Table 2 above diagonal andmedicalvariables — UnadjustedpairwisePearson: ageBMI.01,ageSBP.15,ageDBP−.01,BMISBP.29,BMIDBP.34,SBPDBP.69; varyingn675–710; onlymen45–56,noBPmedication,singlemercuryreading | Schurcomplement controlsageBMI producesrho~.6673; GaussianerrorSD14.5/10assumed | Pairwiseroundedmatrix notonecomplete-case matrix; Sexconstantinsource; transferringtoallsexes20–79/treatment/averageddigitalendpoint unvalidated; Targetprojection/nonlinearage/rejectiondifferent | 82, 111 |

**Tail/support:** FINITE MOMENTS of returned outputs: boundedage20–79,BMI14–65,SBP70–280,DBP35–170. Constant-covariance Gaussianerrors,positive-widthrejectiondomain. Rejectionwhileloops have no hardcodediterationcap butacceptancepositive atfrozenboundedcovariates; almost-sureterminationisnotafinitewalltimeguarantee. No exponentialofunboundedlognormalnesting.

**Revision:** One candidatev001; generated-onlydiagnostics, no scientificrevision.

### LIPID_BASE_R3

Directly checked PMC6435188 Table 1 and measurement context, and PMC6897412 Table 4 categorical contrasts/nonfasting measurement. The qualitative age abstract is contextual and not the source of numerical age slopes.

| Requested analysis | Original statistic and source | Adopted implementation | Remaining assumptions and transfer conditions | Code lines |
|---|---|---|---|---|
| BMI–TC adjusted association | PMC6897412 Table 4; PMC6435188 Table 1 — Tanzania/Uganda LDL contrasts +0.23 overweight/+0.48 obese versus normal BMI; these are categorical, hierarchically adjusted LDL estimates, not continuous TC slopes. Kenyan lipid means/SDs are marginal, fasting summaries. | Conditional component BMI slopes HDL -0.012, LDL +0.050, remnant +0.012 mmol/L per BMI; TC=sum gives +0.050, or 9.6675 mg/dL per 5 BMI within latent stratum. | Category contrasts do not uniquely identify continuous slopes; chosen category separations and remnant slope are assumptions.; A three-stratum lifestyle mixture affects BMI and lipids, so age/sex-only OLS is not the within-stratum slope.; Fasting and nonfasting sources, different populations and adjustment sets are mixed. | 29, 49 |
| BMI–HDL adjusted association | PMC6897412 Table 4 — Overweight/obese contrasts -0.06/-0.15 mmol/L, with age/sex/stratum and hierarchical additional covariates. | Conditional HDL slope -0.012 mmol/L per BMI, or -2.3202 mg/dL per 5 BMI. | Explicit approximate continuous slope, not an exactly extracted coefficient.; Numerical age/sex/lifestyle effects and demographic mixture are assumptions. | 29, 47 |
| TC–HDL residual dependence | No numerical joint source; component identity and selected marginal scales only — Kenyan Table 1 supplies marginal TC/HDL/LDL scales; it does not supply adjusted covariance or a three-component residual model. | Three correlated mean-corrected lognormal components. Log-error correlations HDL–LDL 0.15, HDL–remnant -0.15, LDL–remnant 0.20. TC contains HDL, guaranteeing TC>HDL. | Component CVs and log-error correlations are assumed; positive part-whole covariance is structural, not empirical confirmation.; Latent lifestyle also contributes after requested age/sex/BMI residualization. | 14, 15, 44, 49 |

**Tail/support:** Bounded age/BMI and positive bounded affine component means, multiplied by fixed lognormal errors, yield finite positive moments of every fixed order. TC>HDL is enforced by the positive component identity, not row deletion.

**Revision:** Only v001 was submitted and selected. Generated-only checking did not result in a second scientific candidate; no demonstrated scientific feedback revision.

### LIPID_WORKFLOW_R3

Directly checked PMC6435188 eligibility, fasting assay, Table 1 Maasai columns, and PMC6747887 methods/Table 3 standardized associations, full adjustment and rural complete-case counts.

| Requested analysis | Original statistic and source | Adopted implementation | Remaining assumptions and transfer conditions | Code lines |
|---|---|---|---|---|
| BMI–TC adjusted association | PMC6747887 Table 3; PMC6435188 Table 1 Maasai — Fasting rural Malawi: TC +0.23 women/+0.20 men mmol/L per source sex/area BMI SD; adjusted age, ethnicity, education/assets, marital status, parity, medication, smoking, alcohol, activity and HIV/ART. Kenyan Maasai BMI SD is 4.8, a different population. | Divide +0.23/+0.20 by synthetic/analogue SD 4.8; conditional raw slopes 0.0479167/0.0416667 mmol/L per BMI. | This deliberately transports standardized association magnitudes; it is not recovery of the Malawi raw-BMI coefficient.; Broader source adjustment is collapsed to an age/sex model by assumption.; Sex-specific slopes and generated BMI distribution determine the pooled OLS estimand. | 63, 70 |
| BMI–HDL adjusted association | PMC6747887 Table 3; PMC6435188 Table 1 — Rural Malawi HDL -0.03 mmol/L per source BMI SD in both sexes; Kenyan means/SDs are marginal fasting summaries. | -0.03/4.8=-0.00625 mmol/L per BMI, or -1.2084375 mg/dL per 5 BMI; chosen age slope +0.001. | Synthetic-SD standardized transfer, not source-SD unit conversion.; Age slope magnitude and Gaussian-copula age–BMI dependence 0.20 are assumed. | 63, 76 |
| TC–HDL residual dependence | No applicable empirical residual covariance; PMC6435188 marginal variances — Marginal TC/HDL SDs 0.9/0.3 women and 1.1/0.32 men. Predictor-explained variance subtraction approximates Pearson age–BMI correlation with latent copula correlation. | Independent conditional gamma HDL and non-HDL; TC=HDL+non-HDL. Cov(TC,HDL/X)=Var(HDL/X), so positive residual dependence is structural. | Conditional independence of HDL and non-HDL is unsupported, not equivalent to TC/HDL independence.; Variance subtraction is approximate; the latent-normal correlation need not equal raw age–BMI Pearson correlation.; Sex-specific means, scales and slopes affect pooled OLS residual dependence. | 71, 83 |

**Tail/support:** Bounded age/BMI; strictly positive bounded HDL/non-HDL means and fixed positive conditional variances. Gamma shapes/scales are bounded away from invalid values; all fixed positive moments exist. TC>HDL follows from component identity.

**Revision:** Only v001 was submitted and selected. Generated-only checking did not result in a second scientific candidate; no demonstrated scientific feedback revision.

### PNS_BASE_R3

Directly checked PMC6479514 sampling/protocol and marginal BMI, PMC5344187 methods/Table 1 and approximate association, and PMC4537884 methods/adjustment/6.7 and 3.6 effects. The larger Chinese cohort is overlapping contextual evidence, not an independent additional estimate.

| Requested analysis | Original statistic and source | Adopted implementation | Remaining assumptions and transfer conditions | Code lines |
|---|---|---|---|---|
| BMI–SBP adjusted association | PMC5344187; PMC4537884; PMC6479514 contextual scale — Mexico: approximately 3 mmHg per 4.5 BMI, untreated and chronic-disease-free, age/sex plus broader adjustment. Rural China: 6.7 mmHg per 5 BMI, excluding antihypertensive users, with age/education/income/smoking/alcohol/fruit/sedentary time/season adjustment. | Chosen central 4.7 mmHg per 5 BMI; one normal cohort-level draw with assumed SD 0.8; 15% attenuation above age 60. | 4.7 is an agent-selected compromise, not a pooled meta-analytic estimate.; Older-age attenuation is a modeling assumption; Chinese source actually reported a stronger SBP association at older ages.; Age/sex BP and BMI means are drawn from a restricted Mexican sample and re-used as conditional reference curves, including assumed values below age 35.; Requested pooled age/sex-only OLS differs from source adjustment and generated nonlinear/age-interacting mean. | 35, 43, 59, 70 |
| BMI–DBP adjusted association | PMC5344187; PMC4537884 — Mexico: approximately 2 mmHg per 4.5 BMI; rural China: 3.6 mmHg per 5 BMI with the restrictions/adjustment above. | Chosen central 2.6 per 5 BMI; shared normal draw with assumed SD 0.45 and correlation 0.6 with the SBP slope; same older-age attenuation. | Compromise and parameter-distribution width are assumed; no calibrated transport posterior.; Same source-population and adjustment mismatch; age curves, guards and reading averages alter requested OLS projection. | 35, 43, 59, 70 |
| SBP–DBP residual dependence | PMC6479514 supports mean of the last two of three readings; no applicable numerical residual-correlation source — Opportunistic Brazilian screening, mainly hospitals/clinics, three seated Omron readings; mean readings 2 and 3. | Per-seed person-level residual rho drawn uniformly from 0.50 to 0.75; added visit rho 0.75 and read-error rho 0.50, with assumed SDs, followed by mean-last-two aggregation. | No empirical source identifies any adopted correlation or hierarchical error split.; The shared parameter draw induces marginal dependence between synthetic rows; rows are independent only conditional on that draw.; Nonlinear age means, heterogeneous SDs and joint BP guards can change pooled OLS residual correlation. | 35, 43, 73, 110 |

**Tail/support:** Successful returned age, BMI and BP are bounded. Shared unbounded normal slope draws do not remove output bounds; exceptionally incompatible shared draws may exhaust the finite rejection budget. No observed failure rate was assessed.

**Revision:** Only v001 was submitted and selected. Generated-only checking did not result in a second scientific candidate; no demonstrated scientific feedback revision.

### PNS_WORKFLOW_R3

Directly checked PMC5344187 methods/Table 1, PMC4563590 parental-generation inclusion/methods and Table 2 orientation/values. ELSA PMC4338719 source identity and marginal anchors are the same source checked in the earlier audit; no new target results used.

| Requested analysis | Original statistic and source | Adopted implementation | Remaining assumptions and transfer conditions | Code lines |
|---|---|---|---|---|
| BMI–SBP adjusted association | PMC5344187; PMC4338719 marginal anchors — Approximately 3 mmHg per 4.5 BMI in restricted Mexican adults with broader adjustment; ELSA BP means are marginal contextual summaries. | Conditional slope 3/4.5 mmHg per BMI, or 3.3333 per 5; Mexican age shapes re-centered at ELSA age 52 with assumed sex offset. | Transfer from untreated/chronic-disease-free source to the requested community context.; Turning marginal age/sex summaries into additive conditional mean curves needs a joint model.; Pooled OLS and guards need not recover the declared conditional coefficient exactly. | 27, 40 |
| BMI–DBP adjusted association | PMC5344187; PMC4338719 — Approximately 2 mmHg per 4.5 BMI; source restrictions/adjustment as above. | Conditional 2/4.5 mmHg per BMI, or 2.2222 per 5; nonlinear age curves and chosen conditional SD. | SD 10.4 is an approximate residual-scale choice, not a reported adjusted residual SD.; Male–female offset and transport are assumed; treatment mixture is not identified. | 27, 40, 54, 60 |
| SBP–DBP residual dependence | PMC4563590, Table 2 parental generation — Punjabi Ramdasia parental generation ages 30.5–60.7, n=954 (439 men/515 women), healthy/no medication in prior 2 weeks; two readings averaged. Upper triangle men, lower triangle women. Raw Pearson matrices include age, BMI, SBP and DBP. | Schur-complement partial correlation after linear age/BMI: men 0.6425320, women 0.7238647. Used as Gaussian conditional residual correlations with chosen scales. | Algebra is a derivation from source raw correlations, not a directly reported residual correlation.; Transport from selected Indian parental-generation participants is unverified.; Synthetic nonlinear age means, sex-specific scales and eligibility guards imply pooled residual correlation is not fixed to either source partial value. | 41, 79 |

**Tail/support:** Bounded age/BMI and accepted SBP/DBP give finite returned moments. Static Schur-complement eigenvalues are positive for both sexes. Rejection has a finite cap; this is separate from scientific transport.

**Revision:** Only v001 was submitted and selected. Generated-only checking did not result in a second scientific candidate; no demonstrated scientific feedback revision.

## Cross-study arithmetic is not automatically a common estimand

- Mexican BMI–BP prose gives approximate effects per 4.5 BMI. Converting units is valid arithmetic; replacing a restricted, more extensively adjusted source estimate with the target age/sex-only coefficient is a transport/modeling assumption.
- A raw SBP/DBP correlation is not an age/BMI-adjusted residual correlation. The workflow PNS authors instead derive covariance or partial correlations from different sources; the derived quantity still depends on the source matrix, adjustment, selection and its transfer. Source measurement averaging also affects the noise covariance.
- The Malawi lipid estimates are per source sex/area BMI SD. IQR-based approximation, an assumed SD, and explicitly transporting the standardized effect to a new SD are three different procedures. They must not all be described as an exact unit conversion.
- PNS_BASE_R2 adopts sex-specific INTERSALT coefficients through a secondary paper; the captured primary abstract supports a weight-based overall contrast, not the exact adopted sex-specific BMI coefficients. The DBP conversion also assumes the overall DBP/SBP ratio applies to those sex-specific coefficients.
- The Kenya subgroup lipid mean/SDs are marginal values. Using them as conditional anchors or subtracting modeled explained variance requires the chosen covariate and residual structure. A copula latent correlation is generally not the raw Pearson correlation.
- HDL/non-HDL independence gives positive TC/HDL dependence through the shared HDL component. It is not the same as assuming TC and HDL are independent, and the biochemical identity does not identify the size of the empirical residual association.

## What this audit supports

It supports a bounded, inspectable explanation of how each author connected retrieved evidence, transformations and explicit assumptions to three requested analyses. It identifies exact source definitions and several consequential derivations. This is a concrete provenance capability. It does not establish that the records were automatically complete, that confidence labels predict errors, that review is faster, that a workflow is clinically superior, or that any target population is recovered.

All authors retained their only submitted candidate. The batch tests final generated-data behavior under the frozen policies; it does not demonstrate improvement due to scientific revision. Rejection guards, component identities, covariance derivations and transport distributions are scientific choices inside those initial candidates.

## Exposure and limitations

- No target agreement, patient rows, generated rows, model execution, new paper retrieval or API calls were used in this audit.
- This reviewer has historical project exposure; this is a current-run source/code-only audit, not a claim of personal blinding.
- The operational reviewer owns excluded-family exposure and call-log completeness; author provenance declarations are not accepted as proof of no exposure.
- No calibrated confidence prediction, complete extraction accuracy, clinical trust or human-review benefit is established.
- Tail arguments apply to the frozen specification and ideal stochastic interpretation, with stated numerical/termination qualifications; they are not a verified runtime proof for every future spec.

The operational reviewer separately owns source-access and target-family exposure checks. In particular, the reported PNS_WORKFLOW_R1 incidental excluded-family search hit at call 0005 must remain visible in the operational account. Author statements that target results were unused are provenance declarations, not independent proof.

No candidate, protocol, source packet or target evaluation should be changed on the basis of this after-construction audit. Preserve all 12 authors and all predeclared outcomes. Future design changes, if justified after the full results, require a separate declared version.
