"""Materialize the selected initial specification and its audit records."""
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
DEST = ROOT / 'initial'

def artifact(digest, ext='txt'):
    return {'path':f'literature/approved/{digest}.{ext}', 'sha256':digest}

tw = artifact('47555a144a38e836dab7da8c676a10f51089bc8f6f7776df74dbf31c464261ac')
uk = artifact('ef8b2d42b5285e1da10139a60ac85e536dc53805f89f8c90d949fb28fbc2c37a')
us = artifact('cbee30acd93184c1569619c148e57a323867657d842b3ff649e1e345a93d075c')
query_shape = artifact('222562948a768aecb2835e1f2d0d5146e36e5d2e28ea6590b2495b223b4c68e5', 'json')
counts = {'1':[75,2192,2308,1609], '2':[333,4766,1963,1291]}
ses = {'1':[1.52,.25,.21,.21], '2':[.79,.19,.27,.30]}
means = {'1':[61.83,51.92,46.75,43.25], '2':[66.55,60.72,54.66,51.06]}
sds = {k:(np.asarray(ses[k])*np.sqrt(counts[k])).tolist() for k in counts}
age_n = [4112,4087,4141,2197]
age_effect = [0,.75841,1.18484,.87361]
age_center = float(np.average(age_effect, weights=age_n))

sources = [
 {'id':'S_TW','identifier':'PMC6627528; doi:10.3390/genes10060440',
  'population':'Taiwan Biobank 2012-2016 participants aged 30-70; 6184 men, 8353 women; genotype-selected analytic sample.',
  'measurement':'HDL-C in mg/dL; BMI from biobank physical examination. Specific HDL assay and fasting protocol not stated in this article.',
  'cohort_overlap':'No known overlap with the target. All evidence items from this paper share one cohort and are not independent confirmations.',
  'approved_artifacts':[tw,artifact('23728f05bcc689d1e4d9549f25d163243c4dd6b3a174225f34a7758c1514eaa8','xml')]},
 {'id':'S_UK_MW','identifier':'PMC7364601; doi:10.1186/s12916-020-01648-0',
  'population':'Urban Malawi MEIRU and UK ALSPAC adolescents and parents; adult analytic samples 2277 and 6323, respectively; adults mainly middle-aged.',
  'measurement':'Fasting serum enzymatic lipids in Malawi (Beckman AU480); fasting plasma enzymatic lipids in UK (Technicon RA500); BMI measured.',
  'cohort_overlap':'No known target overlap. The two countries are distinct cohorts. ALSPAC parent/child records can be related; not counted as independent replications.',
  'approved_artifacts':[uk,artifact('4a057ec880a83b63313481262caf810bbf820486609fbff354ee2006dd7c4c70','xml')]},
 {'id':'S_DALLAS','identifier':'PMC4669058; doi:10.1016/j.amjcard.2015.01.015',
  'population':'Dallas Heart Study probability sample, baseline 2000-2002; 1977 adults, 51% women, 46% Black; selected to exclude lipid therapy, hormone therapy, malignancy, connective tissue disease, HIV; survival at least one year.',
  'measurement':'Fasting EDTA plasma; HDL-C reported in mg/dL separately from NMR HDL particles; specific cholesterol assay not fully stated.',
  'cohort_overlap':'No known overlap with target, Taiwan Biobank or ALSPAC/MEIRU.',
  'approved_artifacts':[us,artifact('73b5a9e3b9cb6b5677b965894f2cef6416421a771bc3a294606c5cc80d2b8c47','xml')]}
]

evidence = [
 {'id':'E_TW_CELLS','source_id':'S_TW','locator':'Methods 2.2 and 2.4; Table 2, Sex rows; BMI columns underweight/normal/overweight/obese',
  'estimand':'Unadjusted arithmetic mean and standard error of HDL within sex by BMI category.',
  'variables':['hdl','bmi_category','sex'],'adjustment':'None; each mean marginalizes the source age and unmeasured factors within its sex/BMI cell.',
  'reported':{'unit':'mg/dL','bmi_intervals':['<18.5','18.5 to <24','24 to <27','>=27'],'n_by_sex':counts,'mean_by_sex':means,'standard_error_by_sex':ses},
  'uncertainty':'SEs explicitly identified in Methods and table, rounded to two decimals. Approximate individual cell SD = SE * sqrt(n); this is not regression residual SD.',
  'applicability':'Directly relevant predictor/outcome combination, but Taiwanese ethnicity, selection, ages 30-70 and unspecified assay limit U.S. transport.',
  'model_use':'Anchor sex-specific conditional location and scale curves using reported cell means and converted cell SDs.',
  'bridge_assumptions':['Place cell means at assumed BMI representatives rather than treating those representatives as observed means.','Use within-cell SD as a conditional SD proxy without fitting unavailable within-cell age/BMI distributions.','Transport the level/scale without an empirically estimated U.S. shift.']},
 {'id':'E_TW_AGE','source_id':'S_TW','locator':'Table 3, Age rows; Table 2, age stratum counts summed across BMI columns',
  'estimand':'Adjusted HDL arithmetic mean contrasts for age strata versus age 30-40.',
  'variables':['hdl','age_category'],'adjustment':'Multivariable model includes exercise, WHR, BMI category, body fat category, sex, smoking, drinking, coffee and vegetarian diet.',
  'reported':{'age_categories':['30-40','40-50 (article label)','51-60','61-70'],'contrasts_mg_dl':age_effect,'p_values':[None,.003,'<0.0001',.0068],'n_age':age_n},
  'uncertainty':'No confidence intervals or coefficient SEs in Table 3. The overlapping 40 label is a source labeling ambiguity; no participant recoding inferred.',
  'applicability':'Supplies modest cross-sectional age variation under a richer adjustment set, not a longitudinal aging effect or a sex-specific age slope.',
  'model_use':'Common piecewise linear age pattern, centered on source age-stratum weighted contrast.',
  'bridge_assumptions':['Treat category effects as point effects at approximate midpoints.','Use the same age pattern in both sexes and BMI groups; this is a parsimonious assumption, not evidence of no interaction.','Clamp outside source representative ages.']},
 {'id':'E_TW_ADJUSTED','source_id':'S_TW','locator':'Tables 3 and 5',
  'estimand':'Covariate-adjusted sex and BMI contrasts, including sex contrasts within BMI categories.',
  'variables':['hdl','bmi_category','sex'],'adjustment':'Exercise, WHR, body fat, age, smoking, drinking, coffee, vegetarian diet; Table 5 stratified by BMI.',
  'reported':{'male_vs_female_overall_mg_dl':-9.87778,'bmi_vs_normal_mg_dl':{'underweight':5.64809,'overweight':-4.31095,'obese':-6.4423},'male_vs_female_by_bmi_mg_dl':[-6.10877,-10.93384,-9.12807,-7.89031]},
  'uncertainty':'Table 5 p-values do not test a formal sex-by-BMI interaction; no coefficient covariance or CIs supplied.',
  'applicability':'Supports preserving sex differences and considering possible modification; adjusted BMI effects cannot replace marginal cell contrasts for the available predictor set.',
  'model_use':'Context for sex-specific curves; no second independent numerical weight or additional sex offset.',
  'bridge_assumptions':['Table 2 cell contrasts are used instead of stacking Table 3 adjusted effects onto them.']},
 {'id':'E_UK_SHAPE','source_id':'S_UK_MW','locator':'Statistical analysis; Results paragraphs beginning The majority of the associations and Inverse associations; supplementary listing',
  'estimand':'Shape and population differences of age- and confounder-adjusted BMI-HDL associations.',
  'variables':['hdl','bmi','sex','population'],'adjustment':'Initially age, then socioeconomic, behavioral, ethnicity and medication factors; HIV/physical activity in Malawi only.',
  'reported':{'qualitative':'Most associations linear; BMI-HDL inverse in each sex/age/country group; inverse BMI-HDL association stronger in UK; UK adult women stronger than men.', 'numerical_supplement':'Named supplement is PDF and gateway reports unsupported_supplement_format.'},
  'uncertainty':'Exact HDL slopes and quintile locations unavailable through supported supplement route. Results also contain an apparent HDL/LDL labeling inconsistency in one positive adult-male example; that numeric example is not used.',
  'applicability':'Independent population comparison demonstrates imperfect transport and supplies no evidence for an exact high-BMI plateau.',
  'model_use':'Motivates declining rather than automatically flat extrapolation; qualitative support only.',
  'bridge_assumptions':['Neither qualitative linearity nor the unavailable supplement determines the high-BMI decay constant.']},
 {'id':'E_DALLAS_AGE','source_id':'S_DALLAS','locator':'Table 2, HDL-C Age rows; Methods standardized coefficient definition',
  'estimand':'Sex-specific standardized adjusted age coefficient in HDL-C regression.',
  'variables':['hdl','age','sex'],'adjustment':'Sex-stratified model of age, ethnicity, hypertension, diabetes, smoking, insulin resistance, exercise, alcohol, log triglycerides, family history, CRP; menopause for women.',
  'reported':{'male_standardized_beta':-.0038,'male_p':.91,'female_standardized_beta':.25,'female_p':'<0.00010','model_R2_male':.29,'model_R2_female':.21},
  'uncertainty':'SD(age) and SD(HDL) needed for an unstandardized conversion are not supplied for these regression samples; R2 includes many unavailable predictors.',
  'applicability':'U.S. population, but selection and adjustment differ substantially. Counters universal common-age assumptions.',
  'model_use':'Age-by-sex remains an important gap; do not use beta as mg/dL/year or treat non-significant male beta as known zero.',
  'bridge_assumptions':[]},
 {'id':'E_DALLAS_DISTRIBUTION','source_id':'S_DALLAS','locator':'Table 1, HDL-C columns; table footnote',
  'estimand':'Sex/ethnicity-specific marginal median and interquartile range of HDL-C.',
  'variables':['hdl','sex','ethnicity'],'adjustment':'None.',
  'reported':{'men':{'Black':[48,40,57],'White':[41,35,48],'Hispanic':[41,36,49]},'women':{'Black':[52,45,62],'White':[53,44,63],'Hispanic':[48,40,55]},'format':'[median,Q1,Q3] mg/dL'},
  'uncertainty':'Quantiles, not means or standard deviations; sampling uncertainty not stated.',
  'applicability':'Marginal variability broadly contextualizes the model but joint BMI and age distributions are unavailable.',
  'model_use':'Transport and scale context; no pooled target calibration.',
  'bridge_assumptions':['Cannot match source marginals without corresponding source predictor/ethnicity distributions.']}
]

assumptions = [
 {'id':'A_TRANSPORT','description':'Conditional HDL location and individual variability from Taiwan are provisionally transported without a U.S. offset; population differences are model uncertainty and not extra per-person random noise.'},
 {'id':'A_BMI_POINTS','description':'BMI category representative locations are assumed as 17.5, 21.25, 25.5 and 30 kg/m2. The two closed intervals use their midpoints; open-bin representatives are assumptions. Linearly interpolate mean and SD between representatives; hold below 17.5.'},
 {'id':'A_SCALE','description':'SE*sqrt(n) is the approximate within-sex/BMI-cell SD. Use it as conditional SD, retaining omitted-factor heterogeneity; no claimed residual-variance decomposition. Endpoint SD is retained above BMI 30.'},
 {'id':'A_AGE','description':'Use the adjusted age contrasts as a common additive pattern at ages 35,45,55.5,65.5, with constant endpoint extrapolation. Assume every sex/BMI cell has the overall source age mixing weights when centering. This does not establish age-sex or age-BMI independence in the target.'},
 {'id':'A_TAIL','description':'Above BMI 30, continue the mean downward exponentially toward 30 mg/dL in men and 38 mg/dL in women, at decay 0.04 per BMI unit. These are explicitly assumed extrapolation values, not measured biological asymptotes. Alternative flat continuation is tested.'},
 {'id':'A_FAMILY','description':'Conditional HDL is lognormal matched to specified arithmetic mean and SD, chosen for positivity and right skew. Tail form and latent-factor mixtures are not identified by mean/SE evidence; independent local RNG draws represent residual individual variability only.'},
 {'id':'A_MEASUREMENT','description':'Treat reported HDL-C mg/dL as comparable to direct serum HDL with no estimated assay or fasting shift; this is a measurement bridge because assays/fasting differ or are incompletely reported. Continuous unrounded values are generated.'}
]

params = {'bmi_anchor_kg_m2':[17.5,21.25,25.5,30.0], 'mean_hdl_by_sex':means,
          'sd_hdl_by_sex':sds, 'age_knots_years':[35,45,55.5,65.5],
          'age_effect_mg_dl':age_effect, 'age_center_mg_dl':age_center,
          'tail_asymptote_by_sex':{'1':30.0,'2':38.0}, 'tail_decay_per_bmi':.04}
prov = {
 'bmi_anchor_kg_m2':{'evidence_ids':['E_TW_CELLS'],'assumption_ids':['A_BMI_POINTS'],'derivation':'Closed BMI interval midpoints; assumed representatives for the two open categories. No source BMI means were reported.'},
 'mean_hdl_by_sex':{'evidence_ids':['E_TW_CELLS'],'assumption_ids':['A_BMI_POINTS','A_TRANSPORT','A_MEASUREMENT'],'derivation':'Exact Table 2 sex-row arithmetic means at assumed representative BMI points; no outcome fitting.'},
 'sd_hdl_by_sex':{'evidence_ids':['E_TW_CELLS'],'assumption_ids':['A_SCALE','A_TRANSPORT'],'derivation':'For each sex/BMI cell, reported SE multiplied by sqrt(reported n); preserve full computation precision. Rounded SE limits precision.'},
 'age_knots_years':{'evidence_ids':['E_TW_AGE'],'assumption_ids':['A_AGE'],'derivation':'Approximate age-category midpoints. Article age label 40-50 retained as an acknowledged ambiguity.'},
 'age_effect_mg_dl':{'evidence_ids':['E_TW_AGE'],'assumption_ids':['A_AGE','A_TRANSPORT'],'derivation':'Table 3 contrasts [0,0.75841,1.18484,0.87361] in mg/dL, not slopes per year.'},
 'age_center_mg_dl':{'evidence_ids':['E_TW_AGE'],'assumption_ids':['A_AGE'],'derivation':'sum(n_age * contrast)/sum(n_age), with n_age=[4112,4087,4141,2197]. This exact centering holds only under assumed source-category midpoint mixing.'},
 'tail_asymptote_by_sex':{'evidence_ids':[],'assumption_ids':['A_TAIL'],'derivation':'Assumed men 30 and women 38 mg/dL; not a fitted floor or individual HDL lower bound.'},
 'tail_decay_per_bmi':{'evidence_ids':['E_UK_SHAPE'],'assumption_ids':['A_TAIL'],'derivation':'0.04 is assumed, with e-fold distance 25 BMI units. Qualitative inverse/mostly linear source associations motivate allowing continued decline but do not estimate this value.'}
}
spec = {'model_name':'sex-specific interpolated HDL moments with modest age pattern and positive stochastic residuals',
 'version':'initial', 'family':'conditional lognormal', 'parameters':params, 'assumptions':assumptions, 'parameter_provenance':prov,
 'equations':['m0(b,sex) is linear interpolation of Table 2 means at assumed BMI anchors.',
 'For b>30: m0=L_sex+(M_sex,30-L_sex)*exp(-0.04*(b-30)).',
 'm=m0+interp(age;age_knots,contrasts)-weighted_source_age_contrast.',
 's=linear interpolation of SE*sqrt(n) at the BMI anchors, constant beyond endpoints.',
 'v=log(1+(s/m)^2); log(HDL) ~ Normal(log(m)-v/2,v).'],
 'interpretation':'Associational virtual data. Fixed selected parameters do not quantify epistemic uncertainty. Source population differences are not individual residual noise.',
 'unsupported_exact_operators':['Taiwan published cell means after integrating over actual within-cell BMI and age: unavailable joint distributions.', 'Dallas marginal quantiles: missing source BMI/age/ethnicity joint distribution.', 'UK/Malawi numerical slope: unsupported PDF supplement.']}

gaps = [
 {'id':'G_LOCATION','component':'conditional location/dependence','affected_analysis':'BMI-HDL association and sex contrasts','evidence_status':'Usable sex-by-BMI mean/SE constraints with assumption-dependent continuous interpolation.', 'consequence':'Category averages do not determine pointwise effects; transporting them can shift means and slopes.', 'next_action':'Source-check arithmetic summaries, avoid stacking adjusted BMI coefficients, review any source-calibration mismatch.', 'status':'acted','resolution':'Extracted exact sex-by-BMI means and SEs and selected interpolated mean/SD model; exact integrated source cell means remain unidentified.'},
 {'id':'G_SHAPE','component':'relationship shape and extreme BMI','affected_analysis':'Nonlinearity, severe-obesity contrasts and BMI tail analyses','evidence_status':'Only an open obesity category and qualitative cross-population monotonic/linear context; severe-BMI slope missing.', 'consequence':'Flat versus continuing decline above BMI 30 can materially alter interpretation at BMI 40-70.', 'next_action':'Compare the selected exponential decline with flat continuation on invented BMI inputs; seek source severe-BMI stratification if review identifies an attainable lead.', 'status':'acted','resolution':'Focused sensitivity executed; retained explicit declining extrapolation provisionally rather than infer a zero slope from a missing subdivision.'},
 {'id':'G_AGE','component':'relevant modifiers and age applicability','affected_analysis':'Age association, age-by-sex interaction and older-adult contrasts','evidence_status':'Small common adjusted Taiwan age contrasts; Dallas standardized age coefficient differs by sex; compatible raw slope not available.', 'consequence':'Common age effect may understate sex-specific patterns; 20-29 and 71-79 require extrapolation.', 'next_action':'Reserve retrieval budget for age-sex effects or source SDs under compatible adjustment following review.', 'status':'open','resolution':'Common modest age curve is provisional; no conversion of standardized beta to mg/dL/year.'},
 {'id':'G_VARIANCE','component':'conditional variability','affected_analysis':'Correlations, subgroup spread, low-HDL prevalence and confidence intervals','evidence_status':'Cell SE and n yield total cell SD, not exact residual SD conditional on continuous BMI and age.', 'consequence':'Conditional spread may be overestimated by retained within-cell predictor variance or underestimated by transport differences.', 'next_action':'Verify SE conversion; test model moments on invented repeated inputs; revisit if residual evidence obtained.', 'status':'acted','resolution':'Used source-cell SD proxy with no unwarranted residual deduction; source-specific marginal quantiles cannot calibrate conditional variance.'},
 {'id':'G_TAILS','component':'conditional HDL distribution tails','affected_analysis':'Threshold prevalence and extreme HDL quantiles','evidence_status':'Mean/SE and marginal U.S. IQR do not identify conditional distribution family.', 'consequence':'Lognormal family fixes skew and tail probabilities absent direct evidence.', 'next_action':'Retain positive lognormal as explicit assumption; do not interpret tail fit as validated.', 'status':'unresolved','resolution':'Positivity and stochasticity verified. Conditional tail probabilities remain assumption-sensitive.'},
 {'id':'G_TRANSPORT','component':'source selection, population and measurement','affected_analysis':'Every target association and absolute HDL level','evidence_status':'Non-U.S. primary anchor; U.S. contextual source excludes several conditions/therapies; source assays incomplete or different.', 'consequence':'Neither source can identify target conditional distribution without transport assumptions.', 'next_action':'Keep selection/assay bridges explicit and use independent U.S. context for review; no survey-wide target calibration.', 'status':'acted','resolution':'Added Dallas context and UK/Malawi transport evidence; no numerical offset inferred from unmatched marginal summaries.'},
 {'id':'G_CAUSAL','component':'causal/time-series structure','affected_analysis':'Intervention or longitudinal HDL response','evidence_status':'Not the intended cross-sectional virtual-column task.', 'consequence':'Cross-sectional associations cannot be interpreted as treatment or aging responses.', 'next_action':'Qualify uses.', 'status':'not_applicable','resolution':'No causal or time-series model is claimed.'}
]
actions = [
 {'gap_id':'G_LOCATION','action':'retrieve','evidence_artifacts':[tw],'model_change':'Parameter and structure: sex-specific BMI anchor means and approximate SDs selected.','reason':'Joint sex/BMI cells constrain the available predictor-outcome relationship directly.'},
 {'gap_id':'G_LOCATION','action':'reextract','evidence_artifacts':[tw],'model_change':'Interpretation: kept adjusted coefficients separate from unadjusted cell means.','reason':'Stacking Table 3 effects onto Table 2 means would double count associations and change the adjustment estimand.'},
 {'gap_id':'G_SHAPE','action':'retrieve','evidence_artifacts':[uk,query_shape],'model_change':'Analysis qualification and assumed declining extrapolation.','reason':'Shape search yielded an independent cross-country lead; its numerical supplement is unsupported PDF, so its content was not accessed.'},
 {'gap_id':'G_SHAPE','action':'sensitivity','evidence_artifacts':[tw,uk],'model_change':'No tuning to simulation draw; contrasted declining-tail and flat-tail conditional means.','reason':'Both can agree at central anchors while differing materially at severe BMI; finite sensitivity pair is not a calibrated uncertainty interval.'},
 {'gap_id':'G_AGE','action':'retrieve','evidence_artifacts':[us],'model_change':'Qualification: common age pattern provisional; no unsupported standardized-to-raw conversion.','reason':'Dallas female standardized age coefficient differs from male; source age/HDL SDs for those models are missing.'},
 {'gap_id':'G_VARIANCE','action':'source_check','evidence_artifacts':[tw],'model_change':'Scale parameter derived as SE*sqrt(n), rather than mistakenly using SE as individual noise.','reason':'Methods explicitly define reported plus/minus as SE. Numerical tests recover each assumed moment.'},
 {'gap_id':'G_TAILS','action':'retain','evidence_artifacts':[tw,us],'model_change':'Distribution assumption: positive lognormal retained.','reason':'No retrieved conditional quantiles identify a better tail family; marginal Dallas quantiles are not exact conditional checks.'},
 {'gap_id':'G_TRANSPORT','action':'source_check','evidence_artifacts':[tw,uk,us],'model_change':'Measurement/population qualifications; no target calibration.','reason':'Source predictor distributions and compatible sampling/measurement operators are unavailable.'},
 {'gap_id':'G_CAUSAL','action':'retain','evidence_artifacts':[tw],'model_change':'Use qualification only.','reason':'Cross-sectional construction does not estimate causal interventions.'},
 {'gap_id':'G_AGE','action':'stop','evidence_artifacts':[us],'model_change':'Initial model frozen pending independent review.','reason':'Six queries and three downloads used; six queries and nine downloads reserved for an attainable review-triggered correction. This is pragmatic stopping, not exhaustive search saturation.'}
]

for name,data in [('model_spec.json',spec),('evidence.json',{'sources':sources,'evidence':evidence}),('gaps.json',gaps),('actions.json',actions)]:
    (DEST/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'parameters':params,'sources':len(sources),'evidence_items':len(evidence),'initial_directory':str(DEST)},indent=2))
