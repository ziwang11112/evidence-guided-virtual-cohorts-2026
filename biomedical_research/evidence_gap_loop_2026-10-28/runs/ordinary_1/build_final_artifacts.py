"""Single reviewed revision; never overwrites the initial candidate."""
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent
INITIAL=RUN/'initial'
FINAL=RUN/'final'
FINAL.mkdir(exist_ok=True)
spec=json.loads((INITIAL/'model_spec.json').read_text(encoding='utf-8'))
ledger=json.loads((INITIAL/'evidence.json').read_text(encoding='utf-8'))

generator=(INITIAL/'generator.py').read_text(encoding='utf-8')
generator=generator.replace('# A separately declared longitudinal-to-cross-sectional tail bridge.', '# Cross-sectional obesity slope supplies the local additive tail derivative.')
generator=generator.replace('mean[selected] *= np.exp(p["tail_log_slopes"][label] * excess)', 'mean[selected] *= np.exp(\n            p["tail_additive_slope"] * excess / mean[selected]\n        )')
assert generator != (INITIAL/'generator.py').read_text(encoding='utf-8')
(FINAL/'generator.py').write_text(generator,encoding='utf-8')

spec['model_id']='ordinary_1_final_cross_sectional_tail_lognormal'
del spec['parameters']['tail_log_slopes']
spec['parameters']['tail_additive_slope']=-0.33
del spec['parameter_provenance']['tail_log_slopes']
spec['parameter_provenance']['tail_additive_slope']={
    'evidence_ids':['L02'], 'assumption_ids':['A01','A07'],
    'derivation':'Exact coefficient -0.33 mg/dL per kg/m^2, from the age- and sex-adjusted BMI>30 model in Table rev2 of the published author response embedded in the accepted PMC7644056 JATS. It is a pooled-sex additive cross-sectional slope. Use as the local mean derivative at the final BMI knot via m=m0*exp(beta*excess/m0), rather than asserting this positive curved continuation is the source linear model.'
}
for assumption in spec['assumptions']:
    if assumption['id']=='A01':
        assumption['description']='Transport Taiwan Biobank mean/variability patterns and an Italian clinic cross-sectional obesity slope to the target without target-outcome calibration. Geography, ancestry, selection, medication/disease exclusions, fasting and plasma/serum assay differences remain unresolved. Transportability is an assumption, not validation.'
    elif assumption['id']=='A07':
        assumption['description']='For BMI above 30.5, let m0 be the sex- and age-specific mean at the last anchor and use m=m0*exp(beta*(BMI-30.5)/m0), with beta=-0.33 mg/dL per BMI unit. The right derivative at the anchor equals beta for every age/sex. The source reports a common-sex linear association among BMI>30 clinic patients, not this exponential curvature or target-tail behavior. Exponential continuation maintains a positive mean; it is an assumption especially above the source upper BMI of about 64.6. No sex interaction in the additive tail slope is asserted.'
spec['equations'][2]='m=m0*exp(tail_additive_slope*max(b-30.5,0)/m0). For b>30.5, m0 holds BMI fixed at the final anchor; the right derivative there is tail_additive_slope.'
spec['alternatives_considered'] += [
    'Initial longitudinal percentage tail: replaced because newly retrieved age- and sex-adjusted cross-sectional BMI>30 evidence aligns more closely with the needed estimand; retained as a numerical sensitivity only.',
    'Source linear additive tail: its local slope is used, but a globally linear decline can become nonpositive; the exponential continuation is explicitly an assumed curvature, not claimed as a fitted source relationship.',
    'Representative BMI knots and source-age centering retained: no source supplements supply within-bin or joint sex-age-BMI distributions; alternative knot positions and zero age effects are checked without choosing based on outcomes.',
    'Residual spread and family retained: no retrieved conditional residual SD or quantile evidence justifies a numerical change. SD scaling and a matched-moment gamma distribution are checked as unvalidated alternatives.'
]
spec['revision_scope']='Single post-review revision responding to F1-F3. Source-compatible implementation checks only; no target outcome access or accuracy selection.'

def artifact(stem,ext):
    return {'path':f'literature/approved/{stem}.{ext}','sha256':stem}

ledger['sources'].append({
    'id':'L2020','identifier':'PMC7644056; DOI:10.1371/journal.pone.0241841',
    'population':'1,214 consecutive overweight/obesity clinic patients in Bari/Apulia, Italy, 2018-2019, all described as Caucasian. No medications (including oral contraceptives); excluded diabetes, endocrine disease, chronic inflammatory disease, stable hypertension, clinical cardiovascular disease, malignancy, renal/liver failure and inherited thrombocytopenia. Table 1 age 39.50 +/-12.61, range14-74; BMI33.89 +/-6.08, range25-64.60. Text reports slightly different age/BMI ranges and sex counts; these discrepancies are retained, not reconciled. BMI>30 subgroup n not given in the embedded response table.',
    'measurement':'Overnight-fasting blood, plasma lipids including HDL-C by automated colorimetric method (Hitachi; Boehringer Mannheim). This is not an established calibration to the target direct-serum Roche assay.',
    'cohort_overlap':'Independent Italian clinical cohort; no identified overlap with Taiwan Biobank, GRAPHIC or target. No participant records accessed.',
    'approved_artifacts':[artifact('b2ee68e3163d9d8ad18df363ac332724afec410a690bdd9d7d386b5856e5bfd2','txt'),artifact('d4171b258e7d1d5e65496e1b0f20e80dc8f19265abed96730afa705ad6728299','xml')],
})
ledger['evidence'] += [
    dict(id='L01',source_id='L2020',locator='Main article Table 2, HDL row, BMI column; table footnote and Statistics',
         estimand='Linear cross-sectional additive HDL-C slope per kg/m^2 BMI among participants with BMI>=25',variables=['hdl','bmi','age','sex'],
         adjustment='Age and sex. Each anthropometric parameter modeled separately; no simultaneous WHR/TG adjustment for this HDL regression.',
         reported={'slope_mg_dl_per_bmi':-0.42,'confidence_interval_95':[-0.53,-0.32],'p_value':'<0.001','full_cohort_n':1214},
         uncertainty='A common-sex linear coefficient over BMI25-64.6, not a spline or exact tail curve. Age/sex coefficients and conditional residual SD unavailable. Selected clinical population; some adolescents included.',
         applicability='Outcome and cross-sectional regression estimand align better than a within-person change coefficient; the clinical exclusions, geography, age range and assay still limit transport.',
         model_use='Cross-sectional contextual comparison; BMI>30 subgroup estimate L02 is selected for the continuation, so this coefficient is not pooled or counted as independent evidence.',bridge_assumptions=['A01','A07']),
    dict(id='L02',source_id='L2020',locator='Published Author response to Decision Letter 0, 30 Aug 2020, response to Reviewer 2 minor point2; Table rev2, HDL row, BMI column; embedded directly in approved JATS/text (DOI:10.1371/journal.pone.0241841.r002)',
         estimand='Linear cross-sectional additive HDL-C slope per kg/m^2 BMI restricted to BMI>30',variables=['hdl','bmi','age','sex'],
         adjustment='Table rev2 footnote: adjusted for age and gender; anthropometric predictors analyzed separately.',
         reported={'slope_mg_dl_per_bmi':-0.33,'confidence_interval_95':[-0.47,-0.20],'p_value':'<0.001','subgroup_n':None},
         uncertainty='This subgroup result appears in the published response table rather than the main final article table. Subgroup n, sex-specific slopes, residual SD, age coefficients and nonlinear shape are unavailable. Same cohort as L01, not independent replication. CI is source sampling uncertainty, not target transport uncertainty.',
         applicability='Directly addresses between-person obesity slope with adjustment for the available predictors; still a drug-naive, disease-excluded Italian clinic sample including adolescents. No direct information beyond source BMI maximum about64.6.',
         model_use='Replace longitudinal tail with common additive slope -0.33 at final anchor; use a positivity-preserving exponential continuation and check flat/source-CI/linear/initial alternatives.',bridge_assumptions=['A01','A07']),
    dict(id='L03',source_id='L2020',locator='Main Table 1 HDL row and Clinical, anthropometric and biochemical parameters assessment',
         estimand='Overall unadjusted HDL-C mean/SD/range and measurement method in a selected mixed-sex obesity cohort',variables=['hdl'],adjustment='None.',
         reported={'mean_mg_dl':48.35,'sd_mg_dl':12.47,'range_mg_dl':[19,116],'assay':'automated colorimetric plasma lipid assay, Hitachi/Boehringer Mannheim','fasting':'overnight'},
         uncertainty='Overall SD mixes sex, BMI, age and unmeasured factors; it is not a conditional residual scale. Table/prose disagree slightly on other cohort summaries, though this HDL row is unambiguous.',
         applicability='Provides assay context and a dispersion comparison but no assay-equivalence factor, no exact-predictor residual variance and no target-matched distribution.',
         model_use='Context only; do not replace source-cell SD with overall mixed-sex SD or treat source minimum/maximum as truncation limits.',bridge_assumptions=[]),
]
for item in ledger['evidence']:
    if item['id']=='D01':
        item['model_use']='Retained for provenance of the initial version and its sensitivity comparator only. No final numerical parameter uses this longitudinal slope.'
        item['bridge_assumptions']=[]

(FINAL/'model_spec.json').write_text(json.dumps(spec,indent=2)+'\n',encoding='utf-8')
(FINAL/'evidence.json').write_text(json.dumps(ledger,indent=2)+'\n',encoding='utf-8')

decision='''# Final model decision: ordinary_1

The conditional lognormal generator retains the initial Taiwan Biobank sex-by-BMI mean anchors, age-centering construction and source-derived variability proxy. The numerical revision replaces its longitudinal percentage tail with a cross-sectional additive obesity slope. No target outcome or generated target cohort was inspected to select this change.

## Review F1: directly relevant cross-sectional tail evidence

Two additional gateway searches identified L2020 (PMC7644056), a study of 1,214 Italian overweight/obesity clinic patients. Its main Table 2 gives an HDL-on-BMI coefficient of -0.42 mg/dL per BMI unit (95% CI -0.53 to -0.32), adjusted for age and sex. More specifically, the published author response embedded in the approved JATS contains Table rev2 for patients with BMI>30: coefficient -0.33 (95% CI -0.47 to -0.20), with the same adjustment. This is a separate subgroup analysis in the publication correspondence, not a main-text coefficient, a downloaded DOCX table, or an independent second cohort. All numbers were read from the gateway-approved complete article text/XML; no external supplement or individual data was accessed.

The final model uses -0.33 as the right derivative of the conditional arithmetic HDL mean at BMI30.5, common to men and women. Let m0 be the sex- and age-specific mean at that anchor. Beyond it, m=m0*exp(-0.33*(BMI-30.5)/m0). This retains a positive mean and preserves the source slope locally. It does NOT reproduce a fitted source linear model across the entire range: exponential curvature is assumed. The initial sex-specific longitudinal percentage slopes remain only a comparator, not final parameters. This removes the change-from-within-person-to-between-person bridge while leaving transport and curve-shape bridges unresolved.

L2020 is selected and not target matched. It excludes medications, diabetes and several diseases, is from Italy, and includes ages as young as14. Table1 reports BMI25-64.60; target predictor support extends beyond that. Several Table1/prose age, sex-count and BMI-range entries differ slightly. No numerical correction is invented; no model parameter uses those discrepant summaries. The subgroup n is unavailable. Its slope confidence interval is sampling uncertainty within the source, not a bound on target transport. Flat-tail, original longitudinal-tail, source-CI slope and linear-tail alternatives are evaluated on invented inputs only.

## Review F2: retained anchor and age assumptions

The original G2019 (PMC6627528) Table2 sex-by-BMI means are category averages, not exact-BMI conditional means. Knots17,21.25,25.5,30.5 are assumed representatives; only the two closed-bin knots are midpoints of published boundaries. The source has no registered supplements (gateway list-supplements returned an empty list), and no retrieved evidence identifies within-bin BMI distributions or joint sex-by-age-by-BMI cells. Its Table3 age effects also adjust for lifestyle, WHR and body fat, unlike the generated model.

The current means and modest common age pattern are retained because no available replacement identifies the missing joint information more directly. Final checks vary representative BMI values and remove age effects; these reveal sensitivity, not identify a preferred alternative. The source-age centering identity is an algebraic identity at assumed representatives only. It does not demonstrate reproduction of actual source within-bin distributions. No conditional age/sex interaction is inferred from pooled margins, and a printed overlap in source age-bin boundaries remains disclosed.

## Review F3: variability and measurement

G2019 SEM*sqrt(n) correctly recovers approximate individual SD under the usual independent-mean formula. The resulting SD remains a broad-cell marginal SD, not a residual SD conditional on exact BMI, age and sex. The final model retains it as an explicit variability proxy; lognormal shape, source-derived CV with age and the extreme BMI tail, and independent participant residuals remain assumptions. Repeated random draws quantify Monte Carlo variation under the fixed scenario, not source or transport uncertainty.

L2020's overall HDL48.35+/-12.47 mg/dL is a mixed-sex, mixed-predictor mean and SD. It is not substituted for conditional spread. That study used overnight-fasting plasma lipids measured by automated colorimetry (Hitachi/Boehringer Mannheim); this does not establish calibration to the target direct-serum Roche method. G2019's exact HDL assay remains unspecified in its retrieved maintext. Final checks include SD multipliers0.75/1.25 and a matched-mean/matched-variance gamma alternative. These are deliberately illustrative model choices with no evidence-based uncertainty coverage.

## Preserved evidence cautions and scientific scope

H2019 (PMC6566419) overlaps G2019's parent cohort and contains inconsistent SEM and BMI count labels; it is qualitative context only. K2017 (PMC5627541) concerns HDL function as well as concentration; CEC coefficients, heritability and repeat correlations are not used as HDL residual variance. D2019 remains abstract-only longitudinal context. Neither the added Italian source nor the original sources establish US target calibration or individual HDL recovery.

The virtual column can support transparent scenario analyses conditional on BMI, age and sex. Relations not directly estimated by the evidence arise from chosen model structure. It cannot establish clinical risk, causal weight-change/aging effects, associations with unobserved covariates, or increased clinical information from larger synthetic sample size. Supported implementation claims and unresolved scientific gaps are distinct.

## Retrieval, tests and preservation

Revision used two queries and two download attempts: a potentially useful ARIC fulltext was rejected by the gateway and was not bypassed; L2020 was accepted. The G2019 supplement listing was empty. Total use is8/12 queries and7/12 downloads, leaving4 queries and5 downloads unused. Retrieval stops because the new source directly reduces F1's estimand gap, while no supplied joint summaries or residual measures warrant further numerical changes. No attempt was made to retrieve original/source individual datasets.

All initial files are preserved. final/artificial_checks.json records actual source-arithmetic, provenance, invented-input distribution, interface and sensitivity checks, reproducible with run_final_checks.py. These are implementation/source checks only. No target accuracy or improvement claim is made. final/revision.json records the substantive change and unresolved limitations.
'''
(FINAL/'decision.md').write_text(decision,encoding='utf-8')
revision={
    'generator_or_spec_changed':True,
    'reason':'Replaced longitudinal percent-change BMI-tail parameters with newly retrieved age/sex-adjusted cross-sectional BMI>30 slope -0.33 mg/dL per BMI unit; adjusted the positive continuation to preserve this additive derivative locally. Source mean/age/variance anchors otherwise retained.',
    'findings_addressed':[
        {'id':'F1','action':'Retrieved L2020 fulltext and embedded author-response subgroup table; selected cross-sectional BMI>30 coefficient, removed longitudinal coefficient from final parameters, documented selected cohort and exponential-tail assumptions; evaluated alternatives.'},
        {'id':'F2','action':'Checked G2019 supplement manifest (none). Retained unidentifiable representative/age bridges with explicit limitations and ran knot/age sensitivities without target selection.'},
        {'id':'F3','action':'Inspected new assay and marginal SD information but did not mislabel it as residual SD or assay equivalence. Retained variability proxy; ran SD scaling and gamma-family sensitivity; preserved separation of sampling, residual and transport uncertainty.'},
    ],
    'remaining_limitations':[
        'Clinical Italian and Taiwan volunteer cohorts are not target-matched; no target calibration or assay-equivalence factor.',
        'Cross-sectional pooled-sex linear subgroup coefficient does not identify exponential curvature, sex interaction or extreme BMI behavior beyond about64.6.',
        'Source within-bin BMI distributions and sex-by-age-by-BMI mixtures unavailable; knots and age marginalization remain assumed.',
        'Broad-cell SD is a residual proxy; conditional variance, lognormal family and tail shape unvalidated.',
        'Source coefficient CI and illustrative sensitivities do not quantify transport uncertainty; no target accuracy tests performed.',
    ],
    'budget_used':{'queries':8,'downloads':7},
}
(FINAL/'revision.json').write_text(json.dumps(revision,indent=2)+'\n',encoding='utf-8')
print('Wrote final generator, model spec, evidence, decision and revision record.')
