"""One reviewed revision: exact numerical retention with expanded evidence/checks."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parent
FINAL=ROOT/'final'
FINAL.mkdir(exist_ok=True)
for filename in ['generator.py','model_spec.json','run_artificial_checks.py']:
    shutil.copyfile(ROOT/'initial'/filename,FINAL/filename)

def art(h,ext='txt'):
    return {'path':f'literature/approved/{h}.{ext}','sha256':h}

tw=art('47555a144a38e836dab7da8c676a10f51089bc8f6f7776df74dbf31c464261ac')
mex=art('cd509ac9ca5d45fc4aca2fd8a3f609656001de196a829fd5a7a56097278d7452')
tur=art('5363b935e158f87ad1e5716eaad40e7b289e8d945e60a1c1fd16ceba919c4aa6')
q7=art('cbdda90a0da6ca2c14fb232a533609872dc47e59db8f6728462026a1f6ac762d','json')
q8=art('4bf49f105aaec4ef85c4a06c1b258def5634fb7708bc6cbdea928448f08d58ef','json')
ev=json.loads((ROOT/'initial'/'evidence.json').read_text(encoding='utf-8'))
ev['sources'] += [
 {'id':'S_MEX','identifier':'PMC6755842; doi:10.1161/JAHA.119.012401',
 'population':'Initial cross-sectional sample of 1065 Mexican mestizo adults ages 20-65, recruited in Mexico City, 2013-2018; excludes chronic disease, glucose >=6.93 mmol/L, smoking, alcohol, medications and several other conditions. Intervention samples are distinct subsets and are not used numerically.',
 'measurement':'Overnight 12-hour fasting serum HDL measured on COBAS c111; BMI measured. This is not the target national sampling or assay protocol.',
 'cohort_overlap':'No known target or other included-cohort overlap; cross-sectional and intervention parts of this paper are overlapping rather than independent evidence.',
 'approved_artifacts':[mex,art('95b04f8fe4279eff567474d2c6ac4cd10bba1bd5787b1912fbdcbb99293117e2','xml')]},
 {'id':'S_TUR','identifier':'PMC6458951; doi:10.1155/2019/2521096',
 'population':'116 selected Turkish volunteers recruited with an endocrinology clinic; 10 obesity I, 13 obesity II, 22 obesity III. Extensive exclusions include chronic illness, diabetes/family history, hypertension, smoking, alcohol and regular extensive exercise. No sex mix by BMI group supplied.',
 'measurement':'Overnight fasting blood collection; HDL-C reported in mg/dL; specific HDL assay is not supplied. Table 1 reports mean plus/minus SD.',
 'cohort_overlap':'No known overlap with target or other included cohorts. Table 1 and Table 2 are one sample.',
 'approved_artifacts':[tur,art('765766b336a0dee9b8ed92251cc725b827fe94184396f59032703d216a5f1c38','xml')]}
]
ev['evidence'] += [
 {'id':'E_TW_AGE_BY_BMI','source_id':'S_TW','locator':'Table 5 Age rows, compared with Table 3; Table 2 Age rows supply stratum counts.',
 'estimand':'Adjusted within-BMI-category HDL mean differences by age category versus age 30-40.',
 'variables':['hdl','age_category','bmi_category'],
 'adjustment':'Separate regression by BMI category, including exercise, WHR, body fat, sex, smoking, drinking, coffee and vegetarian diet. Thus not merely BMI/age/sex conditioning.',
 'reported':{'bmi_categories':['underweight','normal','overweight','obese'],
  'age_categories':['30-40','40-50 (article label)','51-60','61-70'],
  'contrasts_mg_dl_by_bmi':[[0,4.01615,4.58714,4.24658],[0,1.37246,1.63715,1.03037],[0,-.10543,.60932,.65788],[0,.32885,.90307,1.17587]],
  'p_values_by_bmi':[[None,.0298,.0229,.1094],[None,.0004,'<0.0001',.0436],[None,.8231,.2041,.2371],[None,.4854,.0615,.0531]],
  'n_age_by_bmi':[[183,99,81,45],[2156,1966,1846,990],[941,1209,1355,766],[832,813,859,396]],
  'n_bmi':[408,6958,4271,2900]},
 'uncertainty':'No formal age-by-BMI interaction test, coefficient covariance or SEs. Largest point differences occur in underweight stratum with n=408, including n=45 at age 61-70. Separate p-values do not establish interaction.',
 'applicability':'Same source as main anchors, but residual adjustment and source cell mixing still differ from available target predictors. Does not supply age-by-sex estimates.',
 'model_use':'Added direct age-modification sensitivity. Retained pooled Table 3 age curve in selected generator; no numerical model change.',
 'bridge_assumptions':['Age knots and category means are distinct from individual conditional effects.','The finite common-versus-stratified contrast comparison is a sensitivity diagnostic, not a probability interval or a formal interaction estimate.']},
 {'id':'E_MEX_OBESITY_LEAD','source_id':'S_MEX','locator':'Participants, Biochemical Parameters, Results cross-sectional section, Figure 1 caption, and supporting-information description of Table S1.',
 'estimand':'Sex-specific HDL comparison across normal/overweight/obesity I-II-III categories in selected Mexican adults.',
 'variables':['hdl','bmi_category','sex'],'adjustment':'Descriptive comparisons; one-/two-way ANOVA mentioned; extensive participant selection. Not target-compatible fully adjusted conditional model.',
 'reported':{'n_total':1065,'description':'Obese participants had lower HDL in both sexes than normal-weight participants; the named Table S1 contains sex-by-obesity-class anthropometric/biochemical summaries.',
  'availability':'Table S1 is within JAH3-8-e012401-s001.pdf; gateway lists unsupported_supplement_format; contents not accessed.'},
 'uncertainty':'Exact sex/class means and uncertainty unavailable through supported route; do not digitize unrequested figure pixels or infer missing numbers.',
 'applicability':'Broad obesity categories and a COBAS serum measure are relevant leads; selected, largely overweight/obese Mexican sample has different exclusions and population.',
 'model_use':'Context and documented failed quantitative lead; no numerical calibration.',
 'bridge_assumptions':[]},
 {'id':'E_TUR_OBESITY_CLASSES','source_id':'S_TUR','locator':'Methods group definitions and n; Table 1, obese class I, II, III rows and table footnote.',
 'estimand':'Unadjusted HDL-C mean and SD in three obesity classes; corresponding BMI and age means.',
 'variables':['hdl','bmi_category','bmi','age'], 'adjustment':'None. Groups not matched, sex mix per category unavailable.',
 'reported':{'classes':['I:30-34.9','II:35-39.9','III:>=40'],'n':[10,13,22],
  'mean_bmi':[32.80,36.92,45.77],'sd_bmi':[1.55,1.75,4.35],
  'mean_age':[35.80,38.38,37.05],'sd_age':[5.66,4.74,4.35],
  'mean_hdl_mg_dl':[43.60,42.62,38.36],'sd_hdl_mg_dl':[5.62,7.04,7.51]},
 'uncertainty':'Small selected groups, no sex stratification or within-group predictor/outcome covariance. Published p-values compare each group to normal-weight, not within-obesity contrasts; no inferential weight assigned. Other discussion/reference-derived numerical claims are not used.',
 'applicability':'Primary within-obesity means provide a concrete declining-shape example through mean BMI 45.77. They do not establish target conditional sex-specific decline or behavior up to BMI 77.5.',
 'model_use':'Source-scale contrast of class III minus I (-5.24 mg/dL) computed and compared descriptively with the selected and flat-tail alternatives at reported BMI means; tail parameters retained.',
 'bridge_assumptions':['Plug-in predictions at group mean BMI/age are not integrated source predictions because of nonlinearity and missing sex/joint distributions.','Source contrast does not identify the selected asymptotes or decay parameter; it only keeps continuing decline plausible.']}
]
ev['access_limitations']=[
 {'pmcid':'PMC7596579','operation':'maintext fetch','status':'rejected','reason':'excluded_study_alias','content_used':False},
 {'pmcid':'PMC7202729','operation':'maintext fetch','status':'rejected','reason':'excluded_study_alias','content_used':False},
 {'pmcid':'PMC6755842','operation':'list-supplements','status':'unsupported','reason':'PDF unsupported; no supplement download or bypass','supplement_id':'bf2797542ed785bbb4d2afce'},
 {'pmcid':'PMC7364601','operation':'list-supplements (initial)','status':'unsupported','reason':'PDF unsupported; no supplement download or bypass','supplement_id':'7fc52ffdd90395cf7dbaf22e'}
]
(FINAL/'evidence.json').write_text(json.dumps(ev,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

gaps=json.loads((ROOT/'initial'/'gaps.json').read_text(encoding='utf-8'))
resolutions={
 'G_LOCATION':('unresolved','Correct reported cell means retained. Actual within-cell continuous BMI/age and omitted-covariate distributions remain unavailable; selected pointwise interpolation is still an assumption-dependent bridge.'),
 'G_SHAPE':('unresolved','Retrieved selected Turkish obesity-class means showing a 5.24 mg/dL class-III versus class-I decline. This keeps continuing decline plausible but does not identify target sex-specific decay/asymptotes; selected parameters and the flat-tail sensitivity are retained. Mexican exact sex/class table is unsupported PDF; pooled U.S. lead rejected. No bypass.'),
 'G_AGE':('unresolved','Re-extracted all Taiwan Table 5 age contrasts, p-values and Table 2 age-by-BMI counts. Quantified the difference from pooled contrasts, largest in small underweight stratum. Retained pooled age curve because richer adjustment, unknown covariance/formal interaction and missing sex-specific patterns do not identify a uniquely superior target curve. Additional age fulltext lead rejected; no standardized-to-raw conversion.'),
 'G_VARIANCE':('unresolved','Cell SD differs from conditional residual SD; adding the age curve also adds between-age variance when marginalizing. Explicit source-midpoint variance accounting performed as a diagnostic, with no invented covariance subtraction. No compatible residual variance/conditional quantile source obtained.'),
 'G_TAILS':('unresolved','Conditional lognormal family retained as a scenario; added studies supply cell means/SDs or inaccessible tables, not conditional tail evidence. Threshold probabilities remain family- and transport-sensitive.'),
 'G_TRANSPORT':('unresolved','New Mexican and Turkish sources have substantial exclusions and different population/measurement conditions. No numerical transport or assay correction is identified. Source heterogeneity remains separate from individual residual variation.'),
 'G_CAUSAL':('not_applicable','No causal or longitudinal claims added; all retained relationships describe a cross-sectional virtual-column scenario.')
}
for g in gaps:
    g['status'],g['resolution']=resolutions[g['id']]
    g['next_action']='Stop this one-review pilot with explicit limitation; future work requires compatible aggregate evidence under documented sampling/measurement/adjustment, not target outcome access.' if g['status']=='unresolved' else 'No causal operator is part of this task.'
(FINAL/'gaps.json').write_text(json.dumps(gaps,indent=2)+'\n',encoding='utf-8')

actions=json.loads((ROOT/'initial'/'actions.json').read_text(encoding='utf-8'))
for action in actions: action['phase']='initial'
new_actions=[
 {'gap_id':'G_AGE','action':'reextract','evidence_artifacts':[tw],'model_change':'Evidence extraction and qualification only; exact generator/spec retained.','reason':'F1: ledger now records all Table 5 age contrasts, p-values and Table 2 age/BMI cell counts; differences between individual estimates are not formal interaction tests.'},
 {'gap_id':'G_AGE','action':'sensitivity','evidence_artifacts':[tw],'model_change':'No selected coefficient change; added focused pooled-versus-BMI-stratified age-contrast comparison.','reason':'F1: shows the possible effect on age contrasts while keeping the source adjustment set and small underweight stratum visible.'},
 {'gap_id':'G_AGE','action':'stop','evidence_artifacts':[q8],'model_change':'No numerical change.','reason':'Compatible age/sex/BMI search found a potentially useful article, but its maintext was rejected for excluded_study_alias. Do not use its rejected content; retain the simpler pooled-age scenario rather than assert a new raw slope.'},
 {'gap_id':'G_LOCATION','action':'retain','evidence_artifacts':[tw],'model_change':'Mean interpolation retained.','reason':'F2: no joint within-cell predictor distributions obtained; source means cannot be reverse-engineered into a unique conditional model.'},
 {'gap_id':'G_VARIANCE','action':'source_check','evidence_artifacts':[tw],'model_change':'Clarified operator and variance accounting; no unsupported residual-variance deduction.','reason':'F2: calculate variance from the explicit source-midpoint age mixture separately from within-cell SD, and label it as an assumed diagnostic rather than source replication.'},
 {'gap_id':'G_SHAPE','action':'retrieve','evidence_artifacts':[q7,mex,tur],'model_change':'Added within-obesity evidence and measurement/selection qualifications; numerical model unchanged.','reason':'F3: followed concrete class-I/II/III leads; read Turkish Table 1 primary means/SDs; Mexican sex/class table is inaccessible PDF. The separate U.S. lead was rejected and supplied no maintext.'},
 {'gap_id':'G_SHAPE','action':'source_check','evidence_artifacts':[tur],'model_change':'Added source-scale descriptive contrast; retained tail parameters.','reason':'F3: class III minus I HDL mean is -5.24 mg/dL. Selected-sex plug-in contrasts are directionally compatible, but missing sex/joint distributions prevent an exact source model operator or numeric fit.'},
 {'gap_id':'G_SHAPE','action':'retain','evidence_artifacts':[tur,tw],'model_change':'Same assumed tail asymptotes and decay retained; original flat alternative remains explicit.','reason':'Continued decline remains plausible; small selected source does not justify re-estimating the target tail. This is a justified numerical no-op, not evidence of target accuracy.'},
 {'gap_id':'G_TAILS','action':'retain','evidence_artifacts':[tw,tur],'model_change':'Lognormal family retained.','reason':'Reported mean/SD information cannot discriminate conditional tail families; no threshold calibration performed.'},
 {'gap_id':'G_TRANSPORT','action':'source_check','evidence_artifacts':[mex,tur],'model_change':'Population/assay qualification strengthened; no change to person-level random noise.','reason':'Additional sources have substantial selection and measurement differences; neither identifies a U.S. transport offset.'},
 {'gap_id':'G_CAUSAL','action':'retain','evidence_artifacts':[tw],'model_change':'No causal model added.','reason':'Cross-sectional primary evidence does not identify intervention or aging responses.'},
 {'gap_id':'G_SHAPE','action':'stop','evidence_artifacts':[q7,q8,mex,tur],'model_change':'Final numerical candidate frozen without parameter changes.','reason':'Two focused review searches and four download attempts yielded two usable contextual sources and two rejections. Relevant available leads are assessed; no exhaustive saturation claimed. Total use 8 queries/7 downloads, below the cap.'}
]
for action in new_actions: action['phase']='revision'
actions.extend(new_actions)
(FINAL/'actions.json').write_text(json.dumps(actions,indent=2)+'\n',encoding='utf-8')

commitments={}
for filename,expected in [('generator.py','9ceb0ed108284457864602a58b6a753f2b1ffce191b04bd1d69229913ab166ba'),('model_spec.json','153db948978adb85f7c46944df62e7c7de2b6803df61814c8424a2019fbffa07')]:
    a=hashlib.sha256((ROOT/'initial'/filename).read_bytes()).hexdigest()
    b=hashlib.sha256((FINAL/filename).read_bytes()).hexdigest()
    assert a==expected and a==b
    commitments[filename]={'initial_sha256':a,'final_sha256':b,'exact_match':True}
revision={'generator_or_spec_changed':False,
 'reason':'Exact numerical no-op after re-extracting source age-by-BMI evidence, focused age sensitivity, two new primary sources and source-operator checks. No obtained evidence uniquely identifies a better target conditional structure or parameters under compatible sampling/measurement/adjustment. Retain the declared scenario rather than fit unsupported within-cell distributions.',
 'findings_addressed':[
  {'id':'F1','action':'Re-extracted Table 5 age rows with stratum counts and p-values; quantified age contrasts; retained pooled age curve with explicit unresolved heterogeneity.'},
  {'id':'F2','action':'Separated published cell SD from conditional residual proxy and added assumed-age-mixture variance accounting; no unsupported covariance or residual deduction.'},
  {'id':'F3','action':'Retrieved within-obesity primary means in Turkey and a Mexican table lead; assessed source contrast, selection, missing operators and access blocks; retained high-BMI scenario and flat-tail sensitivity.'}],
 'remaining_limitations':[v[1] for k,v in resolutions.items() if v[0]=='unresolved'],
 'numerical_file_hashes':commitments,
 'retrieval_budget':{'queries_used_total':8,'downloads_used_total':7,'queries_unused':4,'downloads_unused':5},
 'no_target_validation':True}
(FINAL/'revision.json').write_text(json.dumps(revision,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'numerical_retention':commitments,'evidence_count':len(ev['evidence']),'sources':len(ev['sources']),'final_directory':str(FINAL)},indent=2))
