"""Prepare evidence and covariate-only inputs. NEVER import or run generator.py.

Run from any directory with Python, numpy, pandas, scipy. This script reads only
the supplied build02 scientific inputs and writes inside its own candidate.
"""
from pathlib import Path
import copy
import hashlib
import json
import numpy as np
import pandas as pd
from scipy.stats import beta

C = Path(__file__).resolve().parent
B = C.parent.parent
def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))
def write(name, value):
    (C/name).write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

task = read(B/'task.json')
control = read(B/'allowed_inputs/controller_contract.json')
registry = read(B/'registry.json')
thai = read(B/'sources/thai2005.json')
gallagher = read(B/'sources/gallagher2000.json')
items = []
def evidence(eid, sid, locator, variables, kind, value, unit, selection,
             adjustment=None, applicability='', reported=None, statistic_name=None,
             uncertainty=None):
    note = applicability
    if reported is not None:
        note += ' Original printed value: '+str(reported)+'.'
    # Participant counts refer to identifier cardinality, not an empty variable set.
    if kind == 'reported_other' and not variables:
        variables = ['id']
    entry = dict(id=eid, source_id=sid, locator=locator, variables=variables,
                 kind=kind, estimate=value, unit=unit,
                 uncertainty=uncertainty or {'kind':'not_reported'},
                 adjustment=adjustment or [], selection=selection,
                 applicability=note or 'Source-only evidence; no target validation.')
    if kind == 'reported_other':
        entry['statistic_name'] = statistic_name
    items.append(entry)
    return eid

source_entries=[]
for sid, raw in [('thai2005',thai),('gallagher2000',gallagher)]:
    reg=next(x for x in registry['artifacts'] if x['source_id']==sid)
    assert sha(B/reg['path'])==reg['sha256']
    source_entries.append(dict(id=sid,identifier=raw['citation']+' DOI '+raw['doi'],
        population=json.dumps(raw['population'],ensure_ascii=False),
        measurement=json.dumps(raw['measurement'],ensure_ascii=False),
        cohort_ids=['Pongchaiyakul2005_rural_Thai'] if sid=='thai2005' else ['Gallagher2000_US_UK_Japan'],
        artifacts=[{'path':reg['path'],'sha256':reg['sha256']}]))

# All reported age/BMI/outcome moments remain distinct from coefficient evidence.
for group in thai['summary_moments']:
    label=group['context'].replace(' ','_')
    for variable in ['age','bmi','bodyfat']:
        for stat in ['mean','sd']:
            v=group[variable][stat]
            evidence('T_'+label+'_'+variable+'_'+stat,'thai2005',thai['summary_locator'],
                [variable],stat,v['value'],{'age':'years','bmi':'kg/m2','bodyfat':'%'}[variable],
                group['context']+'; n='+str(group['n']),
                applicability=('Development margin; used for covariate reconstruction or required replay. '
                 if label.startswith('development') else 'Visible validation evidence; contextual only, not a fitting constraint. ')
                 +'SD describes individuals, not uncertainty of the mean or conditional residuals.',reported=v['reported'])
    evidence('T_'+label+'_n','thai2005',thai['summary_locator'],[], 'reported_other',group['n'],
        'persons',group['context'],statistic_name='sample size',applicability='Composition; no independent replication.')
for r in thai['correlations']:
    sex='men' if 'men'==r['context'].split()[-1] else 'women'
    evidence('T_'+sex+'_bmi_r','thai2005',r['locator'],['bmi','bodyfat'],'correlation',r['value']['value'],'1',
        r['context']+'; n='+str(r['n']),applicability='Unadjusted Pearson product-moment correlation. P<0.001; no SE/CI reported.',reported=r['value']['reported'])
thai_terms=['bmi','age','male']
gallagher_terms=['inv_bmi','male','age','asian_inv_bmi','asian_age','male_inv_bmi','male_age']
units={'intercept':'%','bmi':'%/(kg/m2)','age':'%/years','male':'%/code',
       'inv_bmi':'%/(m2/kg)','asian_inv_bmi':'%/(m2/kg)','male_inv_bmi':'%/(m2/kg)',
       'asian_age':'%/years','male_age':'%/years'}
for prefix,sid,eq,terms in [('T','thai2005',thai['equations'][0],thai_terms),
                           ('G','gallagher2000',gallagher['equations'][0],gallagher_terms)]:
    for term,value in eq['coefficients'].items():
        evidence(prefix+'_coef_'+term,sid,eq['locator'],['bodyfat']+([] if term=='intercept' else [term]),
            'ols_coefficient',value['value'],units[term],eq['context']+'; n='+str(eq['n']),
            adjustment=[t for t in terms if t!=term],
            applicability='Original adjusted regression coefficient. No coefficient SE/covariance reported. '
                +'Predictor order: '+', '.join(terms)+'. No standalone Asian intercept in Gallagher design. '
                +'Percent outcome; coefficient differences are percentage points per predictor unit.',reported=value['reported'])
evidence('T_r_squared','thai2005',thai['equations'][0]['locator'],['bodyfat'],'reported_other',.83,'1','pooled development; n=223',
         statistic_name='multiple regression R squared',applicability='Context only; same development cohort as all Thai replay diagnostics.',reported='0.83')
evidence('G_SEE','gallagher2000',gallagher['equations'][0]['locator'],['bodyfat'],'reported_other',4.31,'%',
         'pooled full DXA Equation 1 sample; n=1626',statistic_name='standard error of estimate',
         applicability='Reported residual prediction error in percentage points. Not coefficient SE. Supports initial scale, but sex homogeneity, distribution and transfer are assumptions.',reported='4.31')
evidence('G_multiple_R','gallagher2000',gallagher['equations'][0]['locator'],['bodyfat'],'reported_other',.90,'1',
         'pooled full DXA Equation 1 sample; n=1626',statistic_name='multiple correlation R',applicability='Context only; not additional independent evidence.',reported='0.90')
for i,group in enumerate(gallagher['group_counts_and_moments']):
    selection=group['source_ethnicity']+', '+('men' if group['male'] else 'women')+'; n='+str(group['n'])
    for variable in ['age','bmi']:
        for stat in ['mean','sd']:
            v=group[variable][stat]
            evidence(f'G_group{i}_{variable}_{stat}','gallagher2000',group['locator'],[variable],stat,v['value'],
                {'age':'years','bmi':'kg/m2'}[variable],selection,applicability='Source covariate margin. BMI/age joint distribution is unreported; no bodyfat moments are invented.',reported=v['reported'])
    evidence(f'G_group{i}_n','gallagher2000',group['locator'],[],'reported_other',group['n'],'persons',selection,
        statistic_name='sample size',applicability='Sex/ethnicity composition; US/UK white sites combined because site is not an allowed covariate.')
    for site,n in group['site_counts'].items():
        evidence(f'G_group{i}_site_'+site.replace(' ','_'),'gallagher2000',group['locator'],[],'reported_other',n,'persons',selection+'; '+site,
            statistic_name='site sample size',applicability='Contextual composition only; no site variable or device correction added.')

# Preserve additional printed numerical endpoints as explicitly unreplayed evidence.
v=thai['validation']; loc=v['locator']
evidence('T_validation_predicted_measured_r','thai2005',loc,['bodyfat'],'reported_other',v['predicted_measured_pearson_r']['value'],'1',
         'validation n=213',statistic_name='Pearson predicted-measured correlation',applicability='Visible validation, not a blind holdout or fitting constraint.',reported='0.93')
for side,item in zip(['lower','upper'],v['limits_of_agreement_pp']):
    evidence('T_validation_LOA_'+side,'thai2005',loc,['bodyfat'],'reported_other',item['value'],'%',
        'validation n=213',statistic_name='Bland-Altman limit of agreement '+side,
        applicability='Measured minus predicted; mean plus/minus TWO SD per Figure 5, not CI. Not fitted.',reported=item['reported'])
conf=v['reported_bias_conflict']
for label in ['body_text_mean_pp','table4_mean_pp']:
    val=conf[label]
    evidence('T_validation_bias_'+label,'thai2005',loc,['bodyfat'],'reported_other',val['value'],'%',
        'validation n=213',statistic_name='reported signed bias ('+label+')',applicability=conf['status'],reported=val['reported'])
for side,val in zip(['lower','upper'],conf['body_text_95pct_ci_pp']):
    evidence('T_validation_bias_CI_'+side,'thai2005',loc,['bodyfat'],'reported_other',val['value'],'%',
        'validation n=213',statistic_name='printed signed-bias 95% CI endpoint '+side,applicability=conf['status'],reported=val['reported'])
for row in thai['diagnostic_results']['rows']:
    for metric in ['observed_prevalence_percent','sensitivity','specificity','positive_predictive_value','negative_predictive_value']:
        val=row[metric]
        evidence('T_validation_'+str(row['male'])+'_'+metric,'thai2005',thai['diagnostic_results']['locator'],['bodyfat'],'reported_other',
            val['value'],'%' if metric=='observed_prevalence_percent' else '1','validation; male='+str(row['male'])+'; n='+str(row['n']),
            statistic_name=metric,applicability='Context only; endpoint DXA >25% men or >35% women. '+thai['diagnostic_results']['calibration_status'],reported=val['reported'])
    evidence('T_validation_'+str(row['male'])+'_events','thai2005',thai['diagnostic_results']['locator'],['bodyfat'],'reported_other',
        row['observed_obese_n'],'persons','validation; male='+str(row['male']),statistic_name='observed obesity event count',applicability='Visible descriptive endpoint, not a fitting constraint.')
for sex in ['male','female']:
    val=thai['contextual_full_cohort_outcome_prevalence'][sex+'_percent']
    evidence('T_full_'+sex+'_bodyfat_prevalence','thai2005',thai['contextual_full_cohort_outcome_prevalence']['locator'],['bodyfat'],
        'reported_other',val['value'],'%','full cohort '+sex,statistic_name='DXA obesity prevalence',
        applicability=thai['contextual_full_cohort_outcome_prevalence']['definition']+'; '+thai['contextual_full_cohort_outcome_prevalence']['caveat']+' Context only.',reported=val['reported'])
for cutoff in [25,30]:
    val=thai['population'][f'reported_bmi_ge{cutoff}_prevalence_percent']
    evidence('T_full_bmi_ge'+str(cutoff),'thai2005',thai['population']['bmi_prevalence_locator'],['bmi'],'proportion',val['value'],'%',
        'full cohort n=436',applicability='Full-cohort descriptive prevalence; not an exact development margin. Zero BMI>=30 informs reconstruction support.',reported=val['reported'])
for i,row in enumerate(thai['within_validation_comparisons']['rows']):
    for field in ['r','mean_difference_pp']:
        val=row[field]
        evidence(f'T_comparison{i}_'+field,'thai2005',thai['within_validation_comparisons']['locator'],['bodyfat'],'reported_other',val['value'],
            '1' if field=='r' else '%','same validation participants; '+row['paper_label'],statistic_name=field,
            applicability=thai['within_validation_comparisons']['use'],reported=val['reported'])
    for side,val in zip(['lower','upper'],row['loa_pp']):
        evidence(f'T_comparison{i}_LOA_'+side,'thai2005','Table 4',['bodyfat'],'reported_other',val['value'],'%',
            'same validation participants; '+row['paper_label'],statistic_name='limit of agreement '+side,applicability=thai['within_validation_comparisons']['use'],reported=val['reported'])

for sid,raw,parts in [('thai2005',thai,['split','measurement','reporting_notes','exclusions']),
                      ('gallagher2000',gallagher,['overlap','measurement','additional_DXA_relationships','reporting_notes','exclusions'])]:
    for part in parts:
        evidence(sid+'_context_'+part,sid,
            'Methods; Tables 1-5; Figure 5; exact sublocators retained below' if sid=='thai2005' else 'pp695-699; exact sublocators retained below',
            [],'contextual',None,'','Admitted source context; unreplayed',applicability=json.dumps(raw[part],ensure_ascii=False))
write('evidence.json',{'schema_version':1,'sources':source_entries,'items':items})

assumptions = {
 'A_transport':'A single conditional mean is used for every row. For asian=0 use Gallagher DXA Equation 1. For asian=1 convexly interpolate that equation with Thai BMI-age-sex regression using sex-specific weights. This is partial transport of two disagreeing conditional source relationships, not an asserted universal ethnicity effect. Weights are scenario/fit coefficients, not probabilities or precision weights. Thai/Japanese identity cannot be inferred from IDs and is not modeled.',
 'A_asian':'Asian is the supplied contextual source indicator: Thai participants and Japanese participants are coded 1. Non-Asian combines original white and African American groups; their equality conditional on these covariates is an assumption supported only by the selected original equation. Ethnicity can proxy site, device, environment and selection; there is no biological racial-essentialist interpretation and no claim for other ethnic groups.',
 'A_measurement':'Identity transport of untransformed DXA percentage is assumed across Thai Lunar DPX-IQ, US Lunar DPX v3.6, UK Hologic QDR1000 enhanced software, and Japan Lunar DPX-L v1.3z. Device and population equivalence are unproven and may explain disagreement. No BCA or four-compartment correction is invented.',
 'A_residual':'Individual bodyfat is beta-distributed on 0-100 conditional on a bounded conditional mean. Its desired SD is sex-specific and initially 4.31 percentage points from pooled Gallagher SEE; assigning that value by sex and transporting it is an assumption. Variance is min(sd^2, 0.95*mean*(100-mean)). This ensures valid beta shape parameters, allowing boundary heteroskedasticity without an endpoint atom. Conditional tails, shape, residual-covariate independence of this family, and sex homogeneity of the initial scale are not identified by sources. Seeds vary individuals, not scientific parameters.',
 'A_mean_boundary':'Before beta parameterization the interpolated mean is bounded to [0.1,99.9] percent. This regularization is computational, not evidence. It can alter original OLS predictions at extreme low BMI; all reported source checks remain present to expose the effect.',
 'A_source_shape':'Age in both sources and Gallagher BMI use scaled beta marginal quantiles on stated supports, treating reported moments as population moments; finite-grid errors are recorded. Thai BMI uses an assumed threshold-stratified mixture with exactly 10/98 men and 23/125 women >=25: 33/223 development participants, compatible with an assumed 32/213 validation participants and 65/436=14.91%, rounding to the reported full-cohort 15%. These subgroup counts are NOT reported or inferred unique counts. In each Thai sex stratum the upper component has assumed mean28.8 and population variance0.5, and the lower component moments follow the mixture identities so the final development BMI mean and sample SD match the printed values. Scaled-beta quadrature components initially span [14.05,24.95] and [25.05,29.95]; finite-grid affine moment correction remains within [14,25) and [25,30). Shape, within-threshold gap, upper-component moments and subgroup allocation are fixed assumptions. The female moment/threshold combination entails a broad lower tail and substantial near-threshold density; no empirical histogram is claimed. Unknown BMI minimum is assumed14; Gallagher adult minimum age18 is assumed, maximum97 reported; Thai ages20-84 are reported and BMI upper29.999999 encodes no BMI>=30. Alternative feasible allocations/shapes are scientific sensitivities, not tunable optimizer variables.',
 'A_covariance':'No age-BMI joint distribution is reported. All source strata use one fixed Gaussian rank-copula scenario with latent correlation +0.15. Realized Pearson correlations are measured in reconstruction diagnostics. This moderate positive scenario is not established independence and is not tuned in numerical fitting; a change toward zero or negative association would be a separate scientific sensitivity with consequences for nonlinear marginal means and OLS projections.',
 'A_composition':'Thai development rows are 40 times each reported sex count (98 men,125 women; 8920 rows); Gallagher rows are 6 times all six reported group counts (9756 rows). These are numerical integration rows, not additional subjects. White/African American source strata retain their different age/BMI margins and exact group proportions even though they share asian=0. Group membership is retained only in reconstruction diagnostics and row ranges, not as an added input covariate.',
 'A_domain':'Computational base-covariate domain is age 18-97, BMI 14-35, male/asian in {0,1}, bodyfat 0-100. Source support is independent of unchanged target eligibility age20-59,BMI18.5-35,asian0. Derived observed columns remain formally unbounded as in task but are recomputed exactly from base covariates; generator recomputes equation terms from base inputs rather than relying on an arbitrary transformed input.',
 'A_calibration':'Only bridge_male, bridge_female, residual_sd_male, residual_sd_female may be numerically fitted. Bridge bounds [0,1], step0.25 express convex partial transport; residual SD bounds [2,7] percentage points, step0.5 are broad assumptions around Gallagher SEE4.31 and contextual subgroup SEE3.8-5.4, not confidence intervals. All 18 correlated diagnostics receive fixed controller engineering scales, not statistical precision or independent evidence weight.',
 'A_rounding':'Published means, SDs, correlations and regression coefficients are rounded and share cohorts. Exact mutual consistency is not expected. Unknown coefficient precision remains unknown; neither residual SD nor instrument CV supplies coefficient uncertainty.'
}
params={'bridge_male':.5,'bridge_female':.5,'residual_sd_male':4.31,'residual_sd_female':4.31,
        'gallagher_dxa_coefficients':{k:v['value'] for k,v in gallagher['equations'][0]['coefficients'].items()},
        'thai_coefficients':{k:v['value'] for k,v in thai['equations'][0]['coefficients'].items()},
        'mean_bounds_percent':[.1,99.9],'variance_feasibility_fraction':.95}
prov={}
for key in params:
    if key.startswith('bridge_'):
        prov[key]={'evidence_ids':['G_coef_'+t for t in ['intercept']+gallagher_terms]+['T_coef_'+t for t in ['intercept']+thai_terms],
            'assumption_ids':['A_transport','A_asian','A_measurement','A_calibration'],
            'derivation':'Initial 0.5 is an equal convex compromise between conditional functions; it is not a claim of equal evidence precision. Numerical interval/step are declared in A_calibration.'}
    elif key.startswith('residual_sd_'):
        prov[key]={'evidence_ids':['G_SEE'],'assumption_ids':['A_residual','A_calibration'],
            'derivation':'Initial desired conditional SD 4.31 pp is borrowed from pooled residual SEE, not a marginal outcome SD. Per-sex assignment and bounds are assumptions.'}
    elif key=='gallagher_dxa_coefficients':
        prov[key]={'evidence_ids':['G_coef_'+t for t in ['intercept']+gallagher_terms],'assumption_ids':['A_transport','A_measurement','A_rounding'],
            'derivation':'Exact printed DXA Equation 1 coefficients; all seven predictors retained, no standalone Asian intercept. Coefficients are fixed during numerical fitting.'}
    elif key=='thai_coefficients':
        prov[key]={'evidence_ids':['T_coef_'+t for t in ['intercept']+thai_terms],'assumption_ids':['A_transport','A_measurement','A_rounding'],
            'derivation':'Exact body-text/Table4 linear coefficients; conditional intercept is -10.672, not a marginal bodyfat mean. Fixed during fitting.'}
    else:
        prov[key]={'evidence_ids':[],'assumption_ids':['A_mean_boundary','A_residual'],
            'derivation':'Computational bounded-distribution regularization, fixed rather than optimized.'}
write('model_spec.json',{'parameters':params,'assumptions':[{'id':k,'description':v} for k,v in assumptions.items()],
                         'parameter_provenance':prov})

# Only covariates are simulated below. No outcome equation is evaluated here.
seed=40702
rng=np.random.default_rng(seed)
diagnostics={'scope':'covariates only; no generator import or execution','seed':seed,'latent_copula_correlation':.15,
             'software':{'numpy':np.__version__,'pandas':pd.__version__},'contexts':{}}
(C/'source_contexts').mkdir(exist_ok=True)
def margin(n,mean,sd,lo,hi):
    m=(mean-lo)/(hi-lo); vv=sd**2/(hi-lo)**2
    concentration=m*(1-m)/vv-1
    assert concentration>0
    aa=m*concentration; bb=(1-m)*concentration
    values=lo+(hi-lo)*beta.ppf((np.arange(n)+.5)/n,aa,bb)
    return values,{'distribution':'bounded beta stratified quantiles','alpha':aa,'beta':bb,'support':[lo,hi],
                   'reported_mean':mean,'reported_sd':sd}
def thai_bmi_margin(n,grp):
    # A finite-integration covariate construction, not an outcome calculation.
    mean=grp['bmi']['mean']['value']; sd=grp['bmi']['sd']['value']
    high_n=n*grp['assumed_bmi_ge25_n']//grp['n']; low_n=n-high_n; proportion=high_n/n
    high_mean=28.8; high_variance=.5
    low_mean=(mean-proportion*high_mean)/(1-proportion)
    pooled_population_variance=sd**2*(n-1)/n
    low_variance=(pooled_population_variance-proportion*high_variance
        -proportion*(1-proportion)*(high_mean-low_mean)**2)/(1-proportion)
    components=[]; component_info=[]
    for label,count,mu,var,lo,hi in [('below25',low_n,low_mean,low_variance,14.05,24.95),
                                    ('ge25',high_n,high_mean,high_variance,25.05,29.95)]:
        vals,meta=margin(count,mu,np.sqrt(var),lo,hi)
        vals=mu+(vals-vals.mean())*np.sqrt(var/vals.var(ddof=0))
        components.append(vals)
        component_info.append({'label':label,'rows':count,'initial_quadrature':meta,
            'target_population_variance':var,'actual_mean':float(vals.mean()),
            'actual_population_variance':float(vals.var(ddof=0)),
            'actual_min':float(vals.min()),'actual_max':float(vals.max())})
    values=np.sort(np.concatenate(components))
    assert values.min()>=14 and values.max()<30
    assert int((values>=25).sum())==high_n
    assert abs(values.mean()-mean)<1e-10 and abs(values.std(ddof=1)-sd)<1e-10
    return values,{'distribution':'two threshold-stratified scaled-beta quadratures with exact finite moment correction',
        'support':[14,29.999999],'reported_mean':mean,'reported_sd':sd,
        'assumed_reported_scale_ge25_count':grp['assumed_bmi_ge25_n'],
        'assumed_ge25_fraction':proportion,'components':component_info}

def context_table(name,groups,multiplier,age_limits,bmi_limits):
    frames=[]; records=[]; cursor=0
    for index,grp in enumerate(groups):
        n=grp['n']*multiplier
        a,ad=margin(n,grp['age']['mean']['value'],grp['age']['sd']['value'],*age_limits)
        if 'assumed_bmi_ge25_n' in grp:
            b,bd=thai_bmi_margin(n,grp)
        else:
            b,bd=margin(n,grp['bmi']['mean']['value'],grp['bmi']['sd']['value'],*bmi_limits)
        z=rng.normal(size=(n,2)); score=.15*z[:,0]+np.sqrt(1-.15**2)*z[:,1]
        aa=np.empty(n); bb=np.empty(n)
        aa[np.argsort(z[:,0])]=a; bb[np.argsort(score)]=b
        frame=pd.DataFrame({'id':[f'{name}_{cursor+j:05d}' for j in range(n)],'age':aa,'bmi':bb,
                            'male':grp['male'],'asian':grp['asian']})
        frame['inv_bmi']=1/frame.bmi; frame['male_inv_bmi']=frame.male/frame.bmi
        frame['asian_inv_bmi']=frame.asian/frame.bmi; frame['male_age']=frame.male*frame.age
        frame['asian_age']=frame.asian*frame.age
        for var,desc in [('age',ad),('bmi',bd)]:
            s=frame[var]
            desc.update(actual_mean=float(s.mean()),actual_sample_sd=float(s.std(ddof=1)),
                        actual_min=float(s.min()),actual_max=float(s.max()),
                        mean_error=float(s.mean()-desc['reported_mean']),sd_error=float(s.std(ddof=1)-desc['reported_sd']))
        records.append({'stratum_index':index,'source_label':grp['label'],'reported_n':grp['n'],'simulation_n':n,
                        'first_row_zero_based':cursor,'last_row_zero_based':cursor+n-1,'male':grp['male'],'asian':grp['asian'],
                        'age':ad,'bmi':bd,'actual_pearson_age_bmi':float(np.corrcoef(aa,bb)[0,1]),
                        'bmi_ge30_count':int((bb>=30).sum()),'bmi_ge25_count':int((bb>=25).sum()),
                        'bmi_ge25_fraction':float((bb>=25).mean())})
        cursor+=n; frames.append(frame)
    result=pd.concat(frames,ignore_index=True)
    assert len(result)<=12000
    result.to_csv(C/f'source_contexts/{name}.csv',index=False,float_format='%.17g')
    diagnostics['contexts'][name]={'rows':len(result),'replication_factor':multiplier,'strata':records,
        'covariate_columns':list(result.columns),'contains_bodyfat':False,
        'bmi_ge30_count':int((result.bmi>=30).sum()),'bmi_ge25_count':int((result.bmi>=25).sum()),
        'bmi_ge25_fraction':float((result.bmi>=25).mean()),'age_min':float(result.age.min()),'age_max':float(result.age.max()),
        'bmi_min':float(result.bmi.min()),'bmi_max':float(result.bmi.max())}
    return result
tg=[dict(g,asian=1,label=g['context'],assumed_bmi_ge25_n=10 if g['male'] else 23)
    for g in thai['summary_moments'] if g['context'].startswith('development')]
gg=[dict(g,label=g['source_ethnicity']+' '+('men' if g['male'] else 'women')) for g in gallagher['group_counts_and_moments']]
tf=context_table('thai_development',tg,40,(20,84),(14,29.999999))
gf=context_table('gallagher_full',gg,6,(18,97),(14,35))
diagnostics['contexts']['thai_development']['full_cohort_threshold_compatibility']={
    'reported_full_cohort_bmi_ge25_percent':15,'reported_full_cohort_n':436,
    'assumed_development_ge25_count':33,'assumed_validation_ge25_count':32,
    'assumed_full_cohort_ge25_count':65,'implied_full_cohort_percent':100*65/436,
    'reported_percent_rounding_assumption':'nearest whole percent; compatible total count range64..67',
    'actual_development_ge25_count_on_source_scale':int((tf.bmi>=25).sum())/40,
    'status':'compatible assumed partition; no validation covariates or outcomes reconstructed'}
validation_certificates=[]
for group in thai['summary_moments']:
    if not group['context'].startswith('validation'): continue
    n=group['n']; count=9 if group['male'] else 23; probability=count/n
    total_mean=group['bmi']['mean']['value']; total_variance=group['bmi']['sd']['value']**2*(n-1)/n
    upper_mean=29.0; upper_variance=.5
    lower_mean=(total_mean-probability*upper_mean)/(1-probability)
    lower_variance=(total_variance-probability*upper_variance
        -probability*(1-probability)*(upper_mean-lower_mean)**2)/(1-probability)
    lower_bound=(lower_mean-14)*(25-lower_mean)
    assert 14<lower_mean<25 and 0<lower_variance<lower_bound
    assert 0<upper_variance<(upper_mean-25)*(30-upper_mean)
    validation_certificates.append({'context':group['context'],'reported_n':n,
        'assumed_bmi_ge25_count':count,'upper_component_assumed_mean':upper_mean,
        'upper_component_assumed_population_variance':upper_variance,
        'lower_component_derived_mean':lower_mean,'lower_component_derived_population_variance':lower_variance,
        'lower_component_maximum_variance_on_14_to_25':lower_bound,
        'status':'strictly within bounded moment feasibility; no validation rows generated'})
diagnostics['contexts']['thai_development']['validation_count_feasibility_arithmetic']=validation_certificates
for name,frame,terms in [('thai_development',tf,thai_terms),('gallagher_full',gf,gallagher_terms)]:
    x=np.column_stack([np.ones(len(frame)),frame[terms].to_numpy()])
    diagnostics['contexts'][name]['regression_design']={'predictors':terms,'rank':int(np.linalg.matrix_rank(x)),
            'columns_including_intercept':x.shape[1],'condition_number_unscaled':float(np.linalg.cond(x))}
write('reconstruction_diagnostics.json',diagnostics)

def columns(age,bmi,asian):
    result=copy.deepcopy(task['columns'])
    for col in result:
        if col['name']=='age': col.update(minimum=age[0],maximum=age[1])
        elif col['name']=='bmi': col.update(minimum=bmi[0],maximum=bmi[1])
        elif col['name']=='asian': col['categories']=asian
    return result
def check(cid,eid,kind,unit,selection=None,**fields):
    return {'id':cid,'evidence_id':eid,'status':'approximate',
            'operator':dict(kind=kind,unit=unit,selection=selection or [],missing_policy='error',**fields),
            'assumption_ids':['A_measurement','A_source_shape','A_covariance','A_transport'],
            'reason':'Source consistency under declared approximate source covariates and measurement transport; no target validation.'}
tc=[]
for sex,male in [('men',1),('women',0)]:
    selection=[{'column':'male','op':'eq','value':male}]
    for kind in ['mean','sd']:
        tc.append(check(sex+'_'+kind,'T_development_'+sex+'_bodyfat_'+kind,kind,'%',selection,column='bodyfat'))
    tc.append(check(sex+'_bmi_r','T_'+sex+'_bmi_r','correlation','1',selection,x='bmi',y='bodyfat'))
for term in ['intercept']+thai_terms:
    tc.append(check('coef_'+term,'T_coef_'+term,'ols_coefficient',units[term],outcome='bodyfat',
                    predictors=thai_terms,term=term,include_intercept=True))
gc=[]
for term in ['intercept']+gallagher_terms:
    gc.append(check('coef_'+term,'G_coef_'+term,'ols_coefficient',units[term],outcome='bodyfat',
                    predictors=gallagher_terms,term=term,include_intercept=True))
contexts=[]
for name,pop,cols,cs in [('thai_development','Approximate rural Thai DEVELOPMENT cohort, n223 source participants, 8920 integration rows; asian=1',columns((20,84),(14,29.999999),[1]),tc),
                       ('gallagher_full','Approximate complete Gallagher DXA cohort, n1626 source participants, 9756 integration rows, all six sex/ethnicity groups',columns((18,97),(14,35),[0,1]),gc)]:
    rel=f'source_contexts/{name}.csv'
    contexts.append({'id':name,'population':pop,'reason':'Reported marginal moments and exact relative group counts; independent support and fixed unreported copula scenario. All reconstruction errors recorded.',
        'columns':cols,'assumption_ids':['A_domain','A_asian','A_measurement','A_source_shape','A_covariance','A_composition','A_transport','A_rounding'],
        'measurement':{'mode':'identity','description':assumptions['A_measurement']},
        'input':{'path':rel,'sha256':sha(C/rel),'origin':'declared_source_covariates'},'checks':cs})
replay={'schema_version':2,'model_domain':{'description':assumptions['A_domain'],'columns':columns((18,97),(14,35),[0,1]),
        'assumption_ids':['A_domain']},'contexts':contexts}
write('source_replay_v2.json',replay)
constraints=[]
for ctx in contexts:
    for ch in ctx['checks']:
        op=ch['operator']; kind=op['kind']
        scale=control['loss_scales']['coefficient_by_term'][op['term']] if kind=='ols_coefficient' else control['loss_scales'][kind]
        constraints.append({'context_id':ctx['id'],'check_id':ch['id'],'scale':scale,
            'scale_reason':'Fixed controller term/statistic engineering scale; not sampling precision, likelihood, independence weight, or clinical equivalence.'})
plan={'schema_version':1,'parameters':[
    {'name':'bridge_male','lower':0,'upper':1,'step':.25},
    {'name':'bridge_female','lower':0,'upper':1,'step':.25},
    {'name':'residual_sd_male','lower':2,'upper':7,'step':.5},
    {'name':'residual_sd_female','lower':2,'upper':7,'step':.5}],
    'constraints':constraints,'fit_seeds':control['fit_seeds'],'replay_seeds':control['replay_seeds'],
    'optimizer':{'method':'bounded_coordinate_search','max_trials':9,'shrink':.5,'min_step_fraction':.01,'target_loss':0},
    'execution':control['execution'],'noncomputable':'infeasible'}
write('proposed_calibration_plan.json',plan)
checks={'scope':'source_only','records':[
    {'name':'source_covariate_reconstruction','status':'pass','detail':'Actually generated covariates only, recomputed sample moments, support, age-BMI Pearson and regression design ranks; diagnostics bound below.'},
    {'name':'generator_execution','status':'not_computable','detail':'Not imported or executed by builder. Controller must freeze and execute through isolated adapter.'},
    {'name':'source_outcome_replay','status':'not_computable','detail':'All 18 source outcome checks declared; no outcome statistics computed here.'}],
    'artifacts':[{'path':'reconstruction_diagnostics.json','sha256':sha(C/'reconstruction_diagnostics.json')}]}
write('checks.json',checks)
print(json.dumps({'status':'prepared','candidate':str(C),'evidence_items':len(items),'contexts':{n:d['rows'] for n,d in diagnostics['contexts'].items()},
                  'replay_checks':len(constraints),'generator_executed':False},indent=2))
