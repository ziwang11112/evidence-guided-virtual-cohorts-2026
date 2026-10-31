"""Prepare aggregate-evidence artifacts only. Never imports/runs generator.py."""
from pathlib import Path
import json
import math

B = Path(__file__).parent
C = B / 'candidates' / 'initial'
C.mkdir(parents=True, exist_ok=True)
def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))
def write(name, value):
    (C/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

task = read(B/'task.json')
registry = read(B/'registry.json')['artifacts']
packets = [read(B/'sources'/'extractions'/f'{s}.json') for s in
           ['S1_BOGALUSA_2014','S2_KAHP_2015','S3_CHS_2009']]
sources, items, raw = [], [], {}
for packet in packets:
    ctx = packet['source_context']; sid = packet['source_id']
    sources.append({
        'id':sid, 'identifier':ctx['citation']+' DOI '+ctx['identifiers']['doi'],
        'population':json.dumps(ctx['population'], ensure_ascii=False),
        'measurement':json.dumps(ctx['measurement'], ensure_ascii=False),
        'cohort_ids':ctx['cohort_ids'],
        'artifacts':[{'path':a['path'],'sha256':a['sha256']} for a in registry if a['source_id']==sid]})
    for x in packet['reported_statistics']:
        eid=x['evidence_id']; raw[eid]=x
        variable={'serum_urate':'urate','BMI':'bmi'}.get(x.get('variable'),x.get('variable','sample_size'))
        common={'id':eid,'source_id':sid,'locator':x['locator'],
                'variables':[variable],'unit':x.get('unit','1').replace('kg/m^2','kg/m2'),
                'uncertainty':{'kind':'not_reported'},'adjustment':[],
                'selection':x.get('source_context_id','all')+'; '+ctx['population']['selection'],
                'applicability':'Reported source statistic, not a target constraint. '+
                 ' '.join(ctx['limitations'])+' '+x.get('uncertainty','')}
        typ=x['statistic_type']
        if typ=='arithmetic_mean_and_standard_deviation':
            items.append(dict(common,id=eid+'_mean',kind='mean',estimate=x['mean']))
            items.append(dict(common,id=eid+'_sd',kind='sd',estimate=x['sd']))
        elif typ=='linear_regression_coefficient_pair':
            common.update(variables=['bmi','urate'],adjustment=['age'],unit='kg/m2 per mg/dL')
            items.append(dict(common,kind='ols_coefficient',estimate=x['unstandardized_coefficient']))
            items.append(dict(common,id=eid+'_standardized',kind='reported_other',
                              statistic_name='standardized age-adjusted BMI-on-urate coefficient',
                              unit='1',estimate=x['standardized_coefficient']))
        elif typ=='count':
            items.append(dict(common,kind='reported_other',statistic_name='source participant count',estimate=x['value']))
        elif typ=='count_and_percentage':
            items.append(dict(common,kind='proportion',unit='%',estimate=x['percentage']))
            items.append(dict(common,id=eid+'_count',kind='reported_other',unit='persons',
                              statistic_name='source category count',estimate=x['count']))

def pool(groups, variable):
    rows=[raw[g+'_'+variable] for g in groups]
    n=sum(x['sample_size'] for x in rows)
    mean=sum(x['sample_size']*x['mean'] for x in rows)/n
    variance=sum((x['sample_size']-1)*x['sd']**2+x['sample_size']*(x['mean']-mean)**2 for x in rows)/(n-1)
    return mean,math.sqrt(variance),n

young={}
for sex,label in [(0,'male'),(1,'female')]:
    groups=[f'S1_BOGALUSA_2014_{race}_{label}' for race in ['white','black']]
    young[sex]={v:pool(groups,v) for v in ['age','bmi','serum_urate']}
    n=young[sex]['bmi'][2]
    young[sex]['slope']=sum(raw[g+'_bmi_on_urate']['sample_size']*raw[g+'_bmi_on_urate']['unstandardized_coefficient'] for g in groups)/n
    for v in ['bmi','serum_urate']:
        m,s,_=young[sex][v]; variable='urate' if v=='serum_urate' else v
        for kind,value in [('mean',m),('sd',s)]:
            items.append({'id':f'D_S1_{label}_{variable}_{kind}','source_id':'S1_BOGALUSA_2014',
                          'locator':'DERIVED from Table 1 adult '+label+' white/black counts, means and SDs; means=sum(n*m)/N; sample variance=sum((n-1)*s^2+n*(m-pooled_mean)^2)/(N-1).',
                          'variables':[variable],'kind':kind,'estimate':value,
                          'unit':'mg/dL' if variable=='urate' else 'kg/m2',
                          'uncertainty':{'kind':'not_reported'},'adjustment':[],
                          'selection':f'Bogalusa {label} adults 19-54 pooled across two reported race strata with source counts.',
                          'applicability':'Derived aggregate reconstruction from rounded reported numbers, not an independently reported statistic. Source composition is adopted as an imperfect younger-adult reference, not inferred target racial composition. Source age distribution differs from quotas.'})

oldgroups=['S3_CHS_2009_normal_urate_before_matching','S3_CHS_2009_high_urate_before_matching']
old={v:pool(oldgroups,v) for v in ['age','bmi','serum_urate']}
for v in ['bmi','serum_urate']:
    m,s,_=old[v]; variable='urate' if v=='serum_urate' else v
    for kind,value in [('mean',m),('sd',s)]:
        items.append({'id':f'D_S3_all_{variable}_{kind}','source_id':'S3_CHS_2009',
                      'locator':'DERIVED from pre-match Table 1 group counts/BMI and Section 3.1 pre-match urate moments; means=sum(n*m)/N; sample variance=sum((n-1)*s^2+n*(m-pooled_mean)^2)/(N-1).',
                      'variables':[variable],'kind':kind,'estimate':value,
                      'unit':'mg/dL' if variable=='urate' else 'kg/m2',
                      'uncertainty':{'kind':'not_reported'},'adjustment':[],
                      'selection':'All 5461 CHS adults >=65 without baseline heart failure before matching; normal/high urate groups exhaust sample.',
                      'applicability':'Derived aggregate reconstruction, with whole-unit rounding for BMI. Target excludes ages>=80 and has 50% female; source is about57.5% female. Differences are expected and not tuning obligations.'})

pf=(raw[oldgroups[0]+'_female']['count']+raw[oldgroups[1]+'_female']['count'])/old['bmi'][2]
old_gap=1.0
old_urate_male=old['serum_urate'][0]+pf*old_gap
old_urate_sd=math.sqrt(old['serum_urate'][1]**2-pf*(1-pf)*old_gap**2)
knots=[32.0,49.0,73.0]
mid_offset=raw['S2_KAHP_2015_age40_59_bmi']['mean']-raw['S2_KAHP_2015_age_lt40_bmi']['mean']
moments={}
for sex in [0,1]:
    u0=young[sex]['serum_urate'][0]; u1=old_urate_male-sex*old_gap
    moments[str(sex)]={
        'bmi_mean':[young[sex]['bmi'][0],young[sex]['bmi'][0]+mid_offset,old['bmi'][0]],
        'bmi_sd':[young[sex]['bmi'][1],young[sex]['bmi'][1],old['bmi'][1]],
        'urate_mean':[u0,u0+(u1-u0)*(knots[1]-knots[0])/(knots[2]-knots[0]),u1],
        'urate_sd':[young[sex]['serum_urate'][1],young[sex]['serum_urate'][1]+(old_urate_sd-young[sex]['serum_urate'][1])*(knots[1]-knots[0])/(knots[2]-knots[0]),old_urate_sd],
        'bmi_on_urate':[young[sex]['slope'],young[sex]['slope']+(0.8-young[sex]['slope'])*(knots[1]-knots[0])/(knots[2]-knots[0]),0.8]}

assumptions=[
 {'id':'A_design','description':'Task design fixes 40 rows per sex x 15-year age bin. Sample integer ages uniformly within each bin, independently across rows; this within-bin age law is unreported. The male/female coding is transported from source labels and is not a biological or ascertainment validation.'},
 {'id':'A_transport','description':'These three geographically and temporally different selected sources are approximate descriptive anchors for fictional US community adults. Quotas do not recreate their selection, racial composition, clinical treatment or nationally representative distributions. No target records or target statistics were accessed.'},
 {'id':'A_young_pool','description':'Use source-count-pooled Bogalusa sex-specific moments as working younger-adult reference values. This marginalizes reported race strata only for construction; it does not assert target race proportions. Use them as age32 conditional moments although source moments span19-54; the omitted age decomposition is unknown.'},
 {'id':'A_age','description':'Use piecewise-linear age-dependent moments with knots32,49,73 and constant continuation outside. The+0.8kg/m2 middle-age BMI increment transfers the Korean 40-59 minus<40 marginal contrast additively to both US sex references. This is an assumption, not a within-person or continuous age coefficient; source selection and sex composition may explain it. Interpolation to CHS is not identified from the publications and the 55-64 bridge is unsupported.'},
 {'id':'A_old_sex','description':'CHS does not report sex-specific urate/BMI moments. Set old male-minus-female urate mean gap to1.0mg/dL as an explicit assumption, preserving the reconstructed pooled urate mean at the source female fraction3142/5461. Allocate remaining pooled urate variance equally within sex after removing this assumed between-sex component. Set old BMI mean and SD equal across sexes. These are unreported allocations, not evidence of sex equality or a measured age-by-sex interaction.'},
 {'id':'A_dependence','description':'Age-conditional young BMI-on-urate projection slopes are source-count-weighted averages of the two published race-specific, age-adjusted coefficients. They are not a recovered pooled adjusted coefficient. Set the older slope to0.8kg/m2 per mg/dL as a working extension of CHS high-versus-normal group mean BMI contrast2 divided by urate contrast2.5; that ecological ratio is NOT an identified individual or adjusted regression slope. Linearly interpolate these assumed projection slopes. No inversion of BMI-on-urate slopes and no standardized-beta-as-correlation substitution is performed.'},
 {'id':'A_distribution','description':'At fixed age and sex, use a bivariate lognormal law matching assigned arithmetic means, SDs and raw BMI-on-urate linear-projection slope. Source marginals do not identify this family, skew, tails, conditional response shape, residual variance or copula. Normal log-scale residuals are independent across rows; all unmeasured covariates are absorbed into the distribution without mechanistic or causal claims.'},
 {'id':'A_uncertainty','description':'Published SDs describe individual spread; no coefficient SEs or model-transport probabilities are supplied. Seeds vary individual draws only. Parameter, model-family and transport uncertainty are not represented probabilistically; this one declared construction requires sensitivity work before substantive use.'},
 {'id':'A_checks','description':'Feedback compares the generated quota sample to published or transparently pooled source statistics in overlapping age/sex selections. Means/SDs need not agree because population, age truncation, weighting, treatment and measurement protocols differ. Identity variable/unit mapping is assumed; it is not assay equivalence. Unsupported race and sex-threshold selections remain not_computable.'}
]
parameters={
 'design':{'age_bins':[[20,35],[35,50],[50,65],[65,80]],'sex_values':[0,1],'rows_per_cell':40,'age_law':'discrete_uniform','id_prefix':'B2-FICTIONAL-','columns':['sample_id','age','female','bmi','urate'],'shuffle_rows':True},
 'age_knots':knots,
 'moments_by_female':moments,
 'distribution':{'family':'bivariate_lognormal','dependence_target':'raw_bmi_on_urate_projection','outside_age_knots':'constant'},
 'anchor_derivation':{'young':{str(s):young[s] for s in young},'old_pooled':old,'old_source_female_fraction':pf,'old_assumed_urate_sex_gap':old_gap,'old_assumed_bmi_on_urate':0.8,'middle_age_bmi_increment':mid_offset}
}
provenance={
 'design':{'evidence_ids':[],'assumption_ids':['A_design'],'derivation':'Literal task quota; all within-cell ages fictional and stochastic.'},
 'age_knots':{'evidence_ids':['S2_KAHP_2015_age40_59_age_mean','S3_CHS_2009_normal_urate_before_matching_age_mean','S3_CHS_2009_high_urate_before_matching_age_mean'],'assumption_ids':['A_age','A_young_pool'],'derivation':'Rounded working ages32,49,73, not population-specific cell moments.'},
 'moments_by_female':{'evidence_ids':[i['id'] for i in items if i['id'].startswith('D_')]+['S1_BOGALUSA_2014_'+g+'_bmi_on_urate' for g in ['white_male','black_male','white_female','black_female']]+['S2_KAHP_2015_age40_59_bmi_mean','S2_KAHP_2015_age_lt40_bmi_mean','S3_CHS_2009_normal_urate_before_matching_female_count','S3_CHS_2009_high_urate_before_matching_female_count'],'assumption_ids':['A_transport','A_young_pool','A_age','A_old_sex','A_dependence','A_uncertainty'],'derivation':'Source pooled moments use sum(n*m)/N and sum((n-1)*sd^2+n*(m-M)^2)/(N-1). Young slopes are count-weighted, assumption-dependent averages. Old urate mean male=M+pf*gap, female=M-(1-pf)*gap; within-sex SD=sqrt(pooled_SD^2-pf*(1-pf)*gap^2). Old BMI moments are shared. Middle BMI=young BMI+0.8; middle urate,SD and dependence values are linear interpolations32to73. No values are fitted to generated data.'},
 'distribution':{'evidence_ids':[],'assumption_ids':['A_distribution','A_dependence'],'derivation':'For means mB,mU and SDs sB,sU, log SDs are sqrt(log(1+(s/m)^2)); log correlation=log(1+beta*sU^2/(mB*mU))/(logSD_B*logSD_U), matching the chosen raw BMI-on-urate projection slope. This is algebra within the assumed family, not inversion of a reported regression.'},
 'anchor_derivation':{'evidence_ids':[i['id'] for i in items if not i['id'].endswith('_standardized')],'assumption_ids':['A_young_pool','A_age','A_old_sex','A_dependence'],'derivation':'Audit values derived only from the admitted aggregates. Source cohort counts specify aggregation weights, not observed target records. Scientific choices are explicitly labeled in keys.'}
}
write('evidence.json',{'schema_version':1,'sources':sources,'items':items})
write('model_spec.json',{'parameters':parameters,'assumptions':assumptions,'parameter_provenance':provenance})

checks=[]
def add_check(eid,selection,reason):
    item=next(i for i in items if i['id']==eid)
    checks.append({'id':'check_'+eid,'evidence_id':eid,'status':'approximate',
                   'operator':{'kind':item['kind'],'unit':item['unit'],'selection':selection,'missing_policy':'error','column':item['variables'][0]},
                   'assumption_ids':['A_checks'],'reason':reason})
for sex,label in [(0,'male'),(1,'female')]:
    for variable in ['bmi','urate']:
        for kind in ['mean','sd']:
            add_check(f'D_S1_{label}_{variable}_{kind}',[{'column':'female','op':'eq','value':sex},{'column':'age','op':'le','value':54}],
                      'Approximate comparison with source-count-pooled Bogalusa sex-specific adult moment; generated ages20-54 have a different age distribution and no original medication/race selection.')
for variable in ['bmi','urate']:
    for kind in ['mean','sd']:
        add_check(f'D_S3_all_{variable}_{kind}',[{'column':'age','op':'ge','value':65}],
                  'Approximate comparison of generated65-79 with pre-match CHS>=65 pooled source moment. Sex proportions, upper age bound, health selection and BMI rounding differ.')
for group,filters in [('age_lt40',[{'column':'age','op':'lt','value':40}]),('age40_59',[{'column':'age','op':'ge','value':40},{'column':'age','op':'lt','value':60}]),('age_ge60',[{'column':'age','op':'ge','value':60}])]:
    for variable in ['bmi','serum_urate']:
        add_check(f'S2_KAHP_2015_{group}_{variable}_mean',filters,
                  'Context-only comparison with Korean medication-selected health-examination adults; no established quantitative US transport. This is not an optimization target.')
for item in items:
    if item['kind']=='ols_coefficient' or item['id'].endswith('_standardized'):
        checks.append({'id':'unsupported_'+item['id'],'evidence_id':item['id'],'status':'not_computable','operator':None,'assumption_ids':[],
                       'reason':'Race strata are not generated and pooled adjustment specification is incompletely reported; standardized coefficients are not correlations. A differently adjusted or marginal coefficient would not reproduce this source statistic.'})
for group in oldgroups:
    for variable in ['bmi','serum_urate']:
        eid=group+'_'+variable+'_mean'
        checks.append({'id':'unsupported_'+eid,'evidence_id':eid,'status':'not_computable','operator':None,'assumption_ids':[],
                       'reason':'Source group is a sex-specific urate threshold union. The supplied AND-only selection operator cannot express this union on the exact task columns. No pooled or sex-specific substitute is relabelled as the original group.'})
for index, check in enumerate(checks, 1):
    check['id'] = 'source_' + str(index).zfill(2)
write('whole_cohort_feedback.json',{'schema_version':1,'population':task['population'],
      'measurement':{'mode':'identity','description':'Age years, female0/1, BMI kg/m2 and serum urate mg/dL are mapped identically. Assay/fasting/anthropometry and source population equivalence are unverified; all cross-population checks approximate.'},
      'assumption_ids':['A_transport','A_checks'],'checks':checks})
write('checks.json',{'scope':'source_only','records':[
    {'name':'contract_validation','status':'not_computable','detail':'Not yet run; submission preparation only.'},
    {'name':'generator_execution','status':'not_computable','detail':'Builder did not execute or import generator; isolated controller execution required after freeze.'},
    {'name':'source_feedback','status':'not_computable','detail':'Recipe submitted; no simulated table exists and no source statistic was computed from generated rows.'}], 'artifacts':[]})
print(json.dumps({'candidate':str(C),'evidence_items':len(items),'feedback_checks':len(checks),'parameters':parameters},indent=2))
