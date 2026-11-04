"""Serialize the initial candidate and calculate deterministic law moments only.

This script never imports the generator, draws rows, or accesses target data.
"""
from pathlib import Path
import json
import math
import hashlib
from statistics import NormalDist
import numpy as np

B = Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcBuild01')
C = B / 'candidates/initial'
N = NormalDist()

def dump(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False)+'\n', encoding='utf-8')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

task = json.loads((B/'task.json').read_text(encoding='utf-8-sig'))
ledger = json.loads((B/'reviewed_evidence/EVIDENCE_CANDIDATES.json').read_text(encoding='utf-8-sig'))
registry = json.loads((B/'registry.json').read_text(encoding='utf-8-sig'))
ids = ['PMC7960723','PMC5330780','PMC2551641','Jansen2013','PMC7272077']
cohorts = [['Hainan Li cohort; reused in Li 2020'],['Japan Diabetes Prevention Program'],['Framingham Offspring Study','NHANES 2001-2004'],['LifeLines'],['Hoorn 1989-1992','Hoorn 2006-2007']]
sources = []
for sid, src, cohort in zip(ids, ledger['sources'], cohorts):
    artifact = next(a for a in registry['artifacts'] if a['source_id']==sid and a['path'].endswith('.txt'))
    sources.append(dict(id=sid,identifier=src['doi'],population=json.dumps(src['population'],ensure_ascii=False),measurement=json.dumps(src['measurements'],ensure_ascii=False),cohort_ids=cohort,artifacts=[{k:artifact[k] for k in ('path','sha256')}]))

items=[]
def item(eid,sid,locator,variables,kind,estimate,unit,selection,applicability,adjustment=None,uncertainty=None,**extra):
    items.append(dict(id=eid,source_id=sid,locator=locator,variables=variables,kind=kind,estimate=estimate,unit=unit,uncertainty=uncertainty or {'kind':'not_reported'},adjustment=adjustment or [],selection=selection,applicability=applicability,**extra))

hainan={
    'male': {'n':567,'female':0,'age':[49.16,13.03],'glucose':[5.56,1.70],'hba1c':[5.78,1.03],'rho':0.44},
    'female': {'n':1012,'female':1,'age':[47.43,13.50],'glucose':[5.43,1.28],'hba1c':[5.66,0.92],'rho':0.50}}
unit={'age':'years','bmi':'kg/m^2','glucose':'mmol/L','hba1c':'percent','female':'indicator'}
for sex,d in hainan.items():
    selection=f'Hainan volunteer sample, {sex} stratum; no diabetes or medication exclusion; source age limits and recruitment dates not reported.'
    for variable in ('age','glucose','hba1c'):
        m,s=d[variable]
        loc=f'Results > HbA1c predicts T2D better in females than in males; {sex} {variable} mean and SD (saved text lines 187-190).'
        applicability='Source arithmetic mean/individual SD; not precision. Transport to age35-74 Chinese analytical sample assumes unchanged glycaemic marginals despite redefined age mix. Age mean/SD parameterize a normal distribution subsequently restricted and rounded; they are not asserted as resulting age moments. Fasting plasma-to-serum equivalence is an explicit scenario.'
        item(f'Hainan_{sex}_{variable}_mean','PMC7960723',loc,[variable],'mean',m,unit[variable],selection,applicability,uncertainty={'kind':'sd','value':s})
        item(f'Hainan_{sex}_{variable}_sd','PMC7960723',loc,[variable],'sd',s,unit[variable],selection,applicability+' Source SD denominator convention is not stated; numerical SD replay is withheld.')
    item(f'Hainan_{sex}_HG_spearman','PMC7960723',f'Results same subsection, Fig1A prose; {sex} Spearman rho; Methods > Data analysis.', ['hba1c','glucose'],'spearman_correlation',d['rho'],'1',selection,'Unadjusted within-sex Spearman, not Pearson. Converted to latent Gaussian correlation only under the declared continuous Gaussian copula. Source sampling CI/SE not given.')
item('Hainan_female_fraction','PMC7960723','Results first paragraph, 1012 women among1579 participants.', ['female'],'proportion',1012/1579,'1','Whole Hainan sample.','Derived 1012/1579 from reported counts; selected sample composition, not national prevalence.')

japan={'male':{'n':121,'female':0,'median':24.7,'q25':23.2,'q75':26.6,'r':0.29,'beta':0.27},'female':{'n':124,'female':1,'median':23.2,'q25':21.9,'q75':26.0,'r':0.08,'beta':0.22}}
for sex,d in japan.items():
    sel=f'JDPP {sex} adults aged30-60, WHO IGT, health-check recruitment1999-2002; prior diabetes and listed illnesses excluded; missing cases omitted per analysis.'
    for kind,key,q in [('median','median',None),('quantile','q25',.25),('quantile','q75',.75)]:
        extra={'method':'not_reported'}
        if q is not None: extra['q']=q
        item(f'JDPP_{sex}_bmi_{key}','PMC5330780',f'Table1 (T1), BMI row, {sex} median (25th-75th percentiles).',['bmi'],kind,d[key],'kg/m^2',sel,'BMI margins transferred from selected Japanese IGT sample without data-supported correction. Quantile interpolation not reported. Lognormal median and quartile ratio are fitted; both individual quartile endpoints cannot also be exactly preserved.',**extra)
    item(f'JDPP_{sex}_BH_pearson','PMC5330780',f'Table2 (T2), BMI-HbA1c Pearson r, {sex}; Statistical analysis.', ['bmi','hba1c'],'correlation',d['r'],'1',sel,'Unadjusted Pearson, not the Table3 Beta. Direct transport of this correlation into broader Chinese mixed-disease population is a major assumption; it is converted algebraically for selected lognormal margins.')
    adj=['glucose','postload_glucose','white_rice'] if sex=='male' else ['glucose','homa_beta','bread']
    item(f'JDPP_{sex}_bmi_Beta_unresolved','PMC5330780',f'Table3 (T3), {sex} BMI Beta.', ['hba1c','bmi'],'reported_other',d['beta'],'unresolved Beta scale',sel,'Scale is not explicitly standardized or unstandardized; no CI/SE. Age absent; cannot identify target adjusted slope. Retained but not numerically calibrated.',adjustment=adj,statistic_name='Stepwise BMI Beta with unresolved scale')

for cohort,value in [('NHANES',.010),('FOS',.012)]:
    adj=['female','bmi','glucose']+(['postload_glucose'] if cohort=='FOS' else [])
    item(f'Pani_{cohort}_age','PMC2551641',f'RESULTS paragraph beginning There was no difference in BMI; adjusted {cohort} age association.', ['hba1c','age'],'ols_coefficient',value,'percent/years',f'{cohort} nondiabetic source adults aged>=25; operational diabetes exclusions differ from target.','NHANES is survey weighted, uses plasma glucose mg/dL and source diabetes exclusion; FOS additionally adjusts2h glucose. NHANES magnitude is an explicit transported age association assumption, not certified target estimate. Source SE/CI absent.',adjustment=adj)

lladj=['age','gender_unresolved','glucose','mch_z','mchc_z','smoking','alcohol']
for key,variable,value,lo,hi in [('bmi','bmi',.05,.02,.08),('glucose','glucose',2.13,1.91,2.36),('age','age',.07,.06,.09)]:
    allpredictors=['age','gender_unresolved','bmi','glucose','mch_z','mchc_z','smoking','alcohol']
    item(f'LifeLines_{key}_ModelIII','Jansen2013',f'Table3 ModelIII {key} row; saved publisher L345-L353.', ['hba1c',variable],'ols_coefficient',value,'mmol/mol/'+unit[variable],'Western-European unrelated LifeLines adults; diabetes/anemia exclusions; final model n not explicitly stated.','Reported CI endpoints '+str([lo,hi])+' have unverified confidence level; retained here, uncertainty=not_reported because schema requires a known CI level. HbA1c native mmol/mol; divide slope and endpoints by10.93 only for algebraic conversion. Extra covariates/coding absent, so not transported as target coefficient.',adjustment=[x for x in allpredictors if x!=variable])
item('LifeLines_bmi_age_gender','Jansen2013','Table2 BMI row L304; footnote L331.', ['hba1c','bmi'],'ols_coefficient',.13,'mmol/mol/kg/m^2','Same LifeLines cohort.','CI endpoints0.10-0.16; confidence level unverified. Adjusted only age and gender; same people as ModelIII, not independent evidence.',adjustment=['age','gender_unresolved'])
item('LifeLines_slope_scale_factor','Jansen2013','Methods > Selected SNPs, publisher L261.', ['hba1c'],'reported_other',10.93,'mmol/mol per percent','Unit conversion stated in source.','Slope factor only, not intercept conversion or target estimate.',statistic_name='HbA1c percentage-point to mmol/mol slope factor')
for wave,value,ci in [(1,-.135,[-.228,-.043]),(2,-.022,[-.044,.001])]:
    adj=['glucose','postload_glucose','age','female','waist','hip_quartiles','smoking','alcohol','carbohydrate','vitamin_c_quartiles']+(['creatinine_quartiles','fiber'] if wave==1 else [])
    item(f'Hoorn_wave{wave}_bmi_Q4_Q1','PMC7272077',f'Table2 (pone.0233769.t002), wave{wave} BMI Q4 versus Q1.',['hba1c','bmi_quartiles'],'reported_other',value,'percent',f'Hoorn wave{wave}; known diabetes/glucose-lowering treatment excluded; screen-detected diabetes retained; five imputed datasets.','BMI quartile contrast, not per-unit slope. Simultaneous waist, hip and2hPG conditioning changes estimand; nonmonotone wave1 and weak wave2 pattern retained. Author response warns instability of related predictors. Not pooled with LifeLines; not converted using assumed quartile distance.',adjustment=adj,uncertainty={'kind':'ci','low':ci[0],'high':ci[1],'level':.95},statistic_name='Adjusted BMI Q4-versus-Q1 categorical contrast')

evidence={'schema_version':1,'sources':sources,'items':items}
dump(C/'evidence.json',evidence)

assumptions=[
('task_scope','Generate exactly3000 independent synthetic persons with six required columns and no observed rows. Complete-case selected analytical population; no national survey weights.'),
('hainan_transport','Transport Hainan sex proportions, HbA1c/glucose means/SDs and within-sex HbA1c-glucose rank correlations to the target despite unknown source dates/age limits, geography and clinical selection. Preserve glycaemic margins while changing age distribution; this is not literal source age restriction.'),
('jdpp_transport','Transport JDPP sex-specific BMI medians/quartile spread and unadjusted BMI-HbA1c Pearson correlations from Japanese IGT ages30-60 to Chinese ages35-74 with diabetes/treatment included. Source population mixing is scientifically uncertain, not identified by evidence. No numeric correction for selection is invented.'),
('copula_family','Within sex use a four-dimensional Gaussian copula. This is one positive-definite joint completion of incomplete evidence, not an estimated joint law. All sources are observational; arrows in computational generation carry no causal meaning.'),
('marginal_family','BMI is lognormal; HbA1c is3.5 plus a lognormal; glucose is2.0 plus a lognormal. Floors are regularization assumptions to prevent implausible low-tail values, not hard biological limits. The lognormal upper tails and full aggregate diabetes/treatment mixture are unvalidated. No explicit latent treatment status or diabetes prevalence is inferred.'),
('age_distribution','Age is discrete35,...,74. Probability of integer a is normal(mu,sigma) mass on[a-0.5,a+0.5] divided by mass on[34.5,74.5], using Hainan sex-specific mean/SD as untruncated normal parameters. This lowers SD and shifts mean. Normality and integer rounding convention are assumptions.'),
('missing_dependencies','Latent Gaussian correlations age-BMI=0.10, age-glucose=0.20 and BMI-glucose=0.25 in both sexes. No admitted source estimates these three quantities. They are moderate-dependence scenario choices, not zero-by-absence assumptions, and influence adjusted BMI strongly.'),
('age_association_transport','Use the NHANES adjusted cross-sectional age magnitude0.010 percent/year as a within-sex unweighted population OLS calibration under the constructed BMI/glucose margins. A source survey-weighted pooled US nondiabetic slope does not establish this common within-sex target law; this is an explicit transport/homogeneity assumption. FOS0.012 with extra2hPG is not averaged with it.'),
('measurement_identity','Use source fasting plasma glucose numerical values as a baseline scenario for target central serum glucose in mmol/L and assume no extra fasting-adherence contamination or assay offset. Such contamination is unmeasured, not known absent. HbA1c assay equivalence also unverified; no conversion other than declared native units is performed.'),
('source_operator_scope','Feedback computes only target-output summaries with matching declared numerical operators. It does not reconstruct any source population. Raw differences can reflect transport, age remapping, selected-population mixing and finite sampling; they are not significance tests or an optimization objective.'),
('uncertainty_scope','Within-row residual randomness models individual variation only. Reported source SD is not SE. No source CI level, posterior probability or precision weight is invented. Structural and transport uncertainty is documented but not calibrated by repeated rows.'),
('source_missingness','Hainan descriptions concern the stated sex strata; use all available complete synthetic rows for raw mean/rank comparisons. Hainan does not detail variable-specific missingness; source n metadata denotes reported stratum size, not verified complete-pair count. JDPP correlations used pairwise-complete source data with analysis-specific n not supplied.'),
('incompatible_models','Do not impose LifeLines rich adjusted BMI slopes or Hoorn body-composition-adjusted quartile contrasts on the target four-predictor regression. Their omitted covariate joint laws are unavailable. Quarantined Hainan regression orientation/scale and JDPP Beta scale remain unresolved.')]

def age_law(mu,sd):
    ages=np.arange(35,75,dtype=float)
    raw=np.array([N.cdf((a+.5-mu)/sd)-N.cdf((a-.5-mu)/sd) for a in ages])
    probs=raw/raw.sum()
    cum=np.cumsum(probs)
    # Thresholds on standard normal age score, with exact infinite endpoints.
    th=np.array([-np.inf]+[N.inv_cdf(float(x)) for x in cum[:-1]]+[np.inf])
    return ages,probs,th

def pos_law(mean,sd,floor):
    residual=mean-floor
    s=math.sqrt(math.log1p((sd/residual)**2))
    return {'floor':floor,'log_mu':math.log(residual)-s*s/2,'log_sd':s,'mean':mean,'sd':sd}

def age_cov(ages,probs,th,law,r):
    # Gaussian exponential tilting: E[A exp(s Zx)]/Eexp=sum a*P(tlo-rs<Z<thi-rs).
    tilted=sum(float(a)*(N.cdf(float(hi-r*law['log_sd']))-N.cdf(float(lo-r*law['log_sd']))) for a,lo,hi in zip(ages,th[:-1],th[1:]))
    return (law['mean']-law['floor'])*(tilted-float(ages@probs))

def continuous_cov(l1,l2,r):
    return (l1['mean']-l1['floor'])*(l2['mean']-l2['floor'])*math.expm1(r*l1['log_sd']*l2['log_sd'])

def group_law(sex,bg=.25,calibrate_age=True,fixed_ah=None):
    d=hainan[sex];j=japan[sex]
    ages,probs,th=age_law(*d['age'])
    sb=math.log(j['q75']/j['q25'])/(2*N.inv_cdf(.75))
    mb=j['median']*math.exp(sb*sb/2)
    b={'floor':0.,'log_mu':math.log(j['median']),'log_sd':sb,'mean':mb,'sd':mb*math.sqrt(math.expm1(sb*sb))}
    g=pos_law(*d['glucose'],2.)
    h=pos_law(*d['hba1c'],3.5)
    bh=math.log1p(j['r']*math.sqrt(math.expm1(sb*sb)*math.expm1(h['log_sd']**2)))/(sb*h['log_sd'])
    gh=2*math.sin(math.pi*d['rho']/6)
    means=np.array([float(ages@probs),mb,g['mean'],h['mean']])
    cov=np.zeros((4,4))
    cov[0,0]=float(((ages-means[0])**2)@probs)
    for idx,law in [(1,b),(2,g),(3,h)]: cov[idx,idx]=law['sd']**2
    for i,jj,val in [(0,1,age_cov(ages,probs,th,b,.10)),(0,2,age_cov(ages,probs,th,g,.20)),(1,2,continuous_cov(b,g,bg)),(1,3,continuous_cov(b,h,bh)),(2,3,continuous_cov(g,h,gh))]: cov[i,jj]=cov[jj,i]=val
    # Frisch-Waugh-Lovell: Cov(A,H)=beta_A Var(A residual B,G)+Cov(A,[B,G]) Var([B,G])^-1 Cov([B,G],H).
    q=cov[0,1:3]@np.linalg.inv(cov[1:3,1:3])
    required=.010*(cov[0,0]-q@cov[1:3,0])+q@cov[1:3,3]
    if calibrate_age:
        lo,hi=-.95,.95
        for _ in range(90):
            mid=(lo+hi)/2
            if age_cov(ages,probs,th,h,mid)<required: lo=mid
            else: hi=mid
        ah=(lo+hi)/2
    else: ah=fixed_ah
    cov[0,3]=cov[3,0]=age_cov(ages,probs,th,h,ah)
    R=np.array([[1,.1,.2,ah],[.1,1,bg,bh],[.2,bg,1,gh],[ah,bh,gh,1]])
    eig=np.linalg.eigvalsh(R)
    assert eig.min()>0
    return {'female':d['female'],'age':{'untruncated_mean':d['age'][0],'untruncated_sd':d['age'][1],'values':ages.astype(int).tolist(),'probabilities':probs.tolist(),'latent_thresholds_finite':th[1:-1].tolist()},'bmi':b,'glucose':g,'hba1c':h,'latent_correlation':R.tolist(),'age_hba1c_latent_calibration':{'target_assumed_ols_age':.010,'attained_ols_age':float(np.linalg.solve(cov[:3,:3],cov[:3,3])[0])}},means,cov,eig

models={};moments={};covs={};means={}
for sex in hainan:
    model,mean,cov,eig=group_law(sex)
    models[sex]=model;means[sex]=mean;covs[sex]=cov
    moments[sex]={'order':['age','bmi','glucose','hba1c'],'mean':mean.tolist(),'covariance':cov.tolist(),'latent_eigenvalues':eig.tolist(),'within_sex_primary_slopes_age_bmi_glucose':np.linalg.solve(cov[:3,:3],cov[:3,3]).tolist(),'bmi_implied_q25':math.exp(model['bmi']['log_mu']-N.inv_cdf(.25)*-model['bmi']['log_sd']),'bmi_implied_q75':math.exp(model['bmi']['log_mu']+N.inv_cdf(.75)*model['bmi']['log_sd'])}

def pooled_projection(covs,means):
    p=1012/1579
    within=(1-p)*covs['male']+p*covs['female']
    b=np.linalg.solve(within[:3,:3],within[:3,3])
    inter=means['male'][3]-b@means['male'][:3]
    female=means['female'][3]-means['male'][3]-b@(means['female'][:3]-means['male'][:3])
    keep=[0,1]
    bs=np.linalg.solve(within[np.ix_(keep,keep)],within[keep,3])
    inters=means['male'][3]-bs@means['male'][keep]
    females=means['female'][3]-means['male'][3]-bs@(means['female'][keep]-means['male'][keep])
    return {'primary_order':['intercept','bmi','glucose','age','female'],'primary':[float(inter),float(b[1]),float(b[2]),float(b[0]),float(female)],'secondary_order':['intercept','bmi','age','female'],'secondary':[float(inters),float(bs[1]),float(bs[0]),float(females)]}

projection=pooled_projection(covs,means)
sensitivity=[]
for bg in [.10,.40]:
    altcov={};altmeans={}
    for sex in hainan:
        _,m,c,_=group_law(sex,bg=bg,calibrate_age=False,fixed_ah=models[sex]['latent_correlation'][0][3])
        altcov[sex]=c;altmeans[sex]=m
    sensitivity.append({'changed_only_latent_bmi_glucose':bg,**pooled_projection(altcov,altmeans)})

params={'n_rows':3000,'row_id_prefix':'EVCB01_','female_probability':1012/1579,'copula_order':['age','bmi','glucose','hba1c'],'sex_models':models,'rounding_digits':8}
prov={
'n_rows':{'evidence_ids':[],'assumption_ids':['task_scope'],'derivation':'Task required3000 rows.'},
'row_id_prefix':{'evidence_ids':[],'assumption_ids':['task_scope'],'derivation':'Unique serial identifier prefix; no source identity.'},
'female_probability':{'evidence_ids':['Hainan_female_fraction'],'assumption_ids':['hainan_transport'],'derivation':'1012/1579 from original sex counts; Bernoulli draw, no forced realized count.'},
'copula_order':{'evidence_ids':[],'assumption_ids':['copula_family'],'derivation':'Indices identify age normal score, BMI, glucose, HbA1c.'},
'sex_models':{'evidence_ids':[x['id'] for x in items if x['source_id'] in ('PMC7960723','PMC5330780') and 'unresolved' not in x['id']]+['Pani_NHANES_age'],'assumption_ids':['hainan_transport','jdpp_transport','copula_family','marginal_family','age_distribution','missing_dependencies','age_association_transport','measurement_identity'],'derivation':'Age PMF=normal cell masses conditional34.5<=age*<=74.5. BMI log_mu=log(reported median), log_sd=log(q75/q25)/(2*Phi^-1(.75)); this fits median+quartile ratio, not both asymmetric endpoints. Shifted positive law s^2=log(1+(sd/(mean-floor))^2), mu=log(mean-floor)-s^2/2. r_latent(H,G)=2*sin(pi*rho_S/6). r_latent(B,H)=log(1+r_P*sqrt(expm1(sB^2)*expm1(sH^2)))/(sB*sH). Age-BMI=.10,age-glucose=.20,BMI-glucose=.25 are assumptions. Age-H correlation solves exact discrete-age/shifted-lognormal covariance identity for within-sex OLS age=.010, with90 deterministic bisection steps; formula and precision in static_model_math.py/report. All other entries are numerical derivations of these choices, not extra source estimates.'},
'rounding_digits':{'evidence_ids':[],'assumption_ids':['task_scope'],'derivation':'Round continuous output to8 decimals for stable CSV; model moments describe unrounded law, perturbation at most5e-9 per continuous cell.'}}
spec={'parameters':params,'assumptions':[{'id':i,'description':d} for i,d in assumptions],'parameter_provenance':prov}
dump(C/'model_spec.json',spec)

report={'scope':'deterministic_specification_math_only','generator_executed':False,'random_draws':0,'target_data_read':False,'method':'Closed-form shifted-lognormal pair moments and exact finite-sum normal exponential tilting for integer age. Pooled OLS uses weighted within-sex covariance because intercept and female permit sex-specific intercepts. Ninety-step bisection for age latent correlation; double precision. Analytic law is unrounded;8-decimal output rounding error<=5e-9 per continuous value.','sex_moments':moments,'pooled_projection':projection,'assumption_sensitivity':sensitivity,'moment_existence':'Age is bounded and female Bernoulli. Each positive variable is shifted exp(mu+sZ), Z jointly Gaussian with positive-definite finite matrix. Every polynomial joint moment is finite by Gaussian MGF. Nondegenerate continuous conditional variation plus both sexes and multiple age categories gives positive-definite population predictor covariance. Thus both requested population linear projections exist uniquely.','interpretation':'Values are consequences of this assumed law, not results from generated rows, source validation or target fit. Primary BMI is determined by conditional covariance, not directly set. Varying only the unidentified BMI-glucose link changes it substantially. Scenario endpoints have no probability or confidence interpretation.'}
dump(C/'static_math_report.json',report)

# Only declared source statistics that can be meaningfully calculated are given operators.
checks=[];bindings=[]
items_by_id={x['id']:x for x in items}
def check(eid,operator=None,reason='',definition='specified',weights='none',transform='identity',n=None,assume=None):
    it=items_by_id[eid];cid='check_'+eid
    checks.append({'id':cid,'evidence_id':eid,'status':'approximate' if operator else 'not_computable','operator':operator,'assumption_ids':assume or ['source_operator_scope'],'reason':reason})
    vars=set()
    if operator:
        vars.update(s['column'] for s in operator['selection'])
        if operator['kind'] in ('mean','sd','median','quantile'):vars.add(operator['column'])
        elif operator['kind'] in ('correlation','spearman_correlation'):vars.update([operator['x'],operator['y']])
        elif operator['kind']=='proportion':vars.add(operator['event']['column'])
    bindings.append({'check_id':cid,'evidence_id':eid,'source_locator':it['locator'],'definition_status':definition if operator else ('unsupported' if definition=='specified' else definition),'source_operator':operator,'source_variable_units':{v:unit[v] for v in sorted(vars)},'weights':weights,'transform':transform,'source_n':{'status':'reported','value':n,'scope':'Reported source sex-stratum cohort size; not verified variable-specific complete-pair/model denominator.'} if n else {'status':'not_reported'},'uncertainty_role':'individual_dispersion' if it['uncertainty']['kind']=='sd' else ('estimate' if it['uncertainty']['kind'] in ('se','ci') else 'not_reported'),'reason':reason})

for sex,d in hainan.items():
    sel=[{'column':'female','op':'eq','value':d['female']}]
    for variable in ('age','glucose','hba1c'):
        eid=f'Hainan_{sex}_{variable}_mean'
        op={'kind':'mean','unit':unit[variable],'selection':sel,'missing_policy':'error','column':variable}
        check(eid,op,'Arithmetic mean of stated sex stratum. Target age restriction/remapping, all-adult glycaemic-margin transport and serum/plasma identity assumptions remain; raw discrepancy is not source-population replay.',n=d['n'],assume=['hainan_transport','age_distribution','measurement_identity','source_operator_scope','source_missingness'])
        check(f'Hainan_{sex}_{variable}_sd',reason='Source reports individual SD but does not state denominator convention. Retained as dispersion evidence; no exact sample-SD definition is invented.',definition='not_reported',n=d['n'])
    op={'kind':'spearman_correlation','unit':'1','selection':sel,'missing_policy':'error','x':'hba1c','y':'glucose'}
    check(f'Hainan_{sex}_HG_spearman',op,'Unadjusted within-sex Spearman correlation explicitly specified by source. Complete synthetic rows, identity measurement and target transport are approximate; reported source cohort n is not proven pairwise n.',n=d['n'],assume=['hainan_transport','measurement_identity','source_operator_scope','source_missingness'])
check('Hainan_female_fraction',{'kind':'proportion','unit':'1','selection':[],'missing_policy':'error','event':{'column':'female','op':'eq','value':1}},'Derived source fraction from original counts; generated selected sample composition compared under explicit transport.',n=1579,assume=['hainan_transport','source_operator_scope'])
for sex,d in japan.items():
    for key in ('median','q25','q75'):
        check(f'JDPP_{sex}_bmi_{key}',reason='Source quantile interpolation convention not stated; numerical quantile feedback withheld. Family construction uses reported population-style locations as an approximation.',definition='not_reported',n=d['n'],assume=['jdpp_transport','marginal_family'])
    op={'kind':'correlation','unit':'1','selection':[{'column':'female','op':'eq','value':d['female']}],'missing_policy':'complete_cases','x':'bmi','y':'hba1c'}
    check(f'JDPP_{sex}_BH_pearson',op,'Source explicitly uses Pearson and omits missing cases per analysis. Numerical target comparison retains the substantial IGT-to-unrestricted-population transport assumption; source complete-pair n unknown.',assume=['jdpp_transport','source_operator_scope','source_missingness'])
    check(f'JDPP_{sex}_bmi_Beta_unresolved',reason='Beta scale unresolved; sex-specific models additionally use unavailable covariates and omit age. No per-unit target coefficient substitute.',definition='not_reported')
for eid in ['Pani_NHANES_age','Pani_FOS_age']:
    check(eid,reason='Source weighting/selection and glucose mg/dL differ; FOS also requires unavailable2h glucose. Numerical magnitude may guide an explicit model assumption, but v1 cannot reproduce source estimator with this output.',weights='weighted' if 'NHANES' in eid else 'none',transform='nonidentity')
for eid in [x['id'] for x in items if x['source_id']=='Jansen2013']:
    check(eid,reason='Native HbA1c mmol/mol or slope conversion factor; rich adjustment/coding unavailable and CI level unresolved. No automatic unit conversion or omission of covariates in v1.')
for eid in ['Hoorn_wave1_bmi_Q4_Q1','Hoorn_wave2_bmi_Q4_Q1']:
    check(eid,reason='BMI categorical contrast with unavailable waist/hip,2h glucose and diet covariates and multiple imputation. A continuous target BMI coefficient is a different estimand; retained conflicting evidence cannot be numerically substituted.')
plan={'schema_version':1,'population':task['population'],'measurement':{'mode':'identity','description':'Target output is compared as generated, in stated units; no source reconstruction or conversion. Fasting plasma-to-target serum equality is an explicit baseline scenario, not an established measurement fact.'},'assumption_ids':['source_operator_scope','measurement_identity'],'checks':checks}
dump(C/'whole_cohort_feedback.json',plan)
dump(C/'source_semantics_v1.json',{'schema_version':1,'evidence_sha256':sha(C/'evidence.json'),'recipe_sha256':sha(C/'whole_cohort_feedback.json'),'bindings':bindings})

generator='''"""Whole-cohort sampler. All scientific settings are in model_spec.json."""
import numpy as np
import pandas as pd

def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("whole-cohort input must be None")
    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    n = int(p["n_rows"])
    female = rng.binomial(1, p["female_probability"], size=n)
    age = np.empty(n, dtype=np.int64)
    bmi = np.empty(n, dtype=float)
    glucose = np.empty(n, dtype=float)
    hba1c = np.empty(n, dtype=float)
    for sex in ("male", "female"):
        model = p["sex_models"][sex]
        indices = np.flatnonzero(female == model["female"])
        R = np.asarray(model["latent_correlation"], dtype=float)
        # A Cholesky failure is an error, never repaired by changing the model.
        z = rng.standard_normal((len(indices), 4)) @ np.linalg.cholesky(R).T
        bins = np.asarray(model["age"]["latent_thresholds_finite"], dtype=float)
        values = np.asarray(model["age"]["values"], dtype=np.int64)
        age[indices] = values[np.searchsorted(bins, z[:, 0], side="right")]
        for k, out, column in ((1, bmi, "bmi"), (2, glucose, "glucose"), (3, hba1c, "hba1c")):
            law = model[column]
            out[indices] = law["floor"] + np.exp(law["log_mu"] + law["log_sd"] * z[:, k])
    digits = int(p["rounding_digits"])
    return pd.DataFrame({
        "person_id": [p["row_id_prefix"] + str(i + 1).zfill(6) for i in range(n)],
        "age": age,
        "female": female,
        "bmi": np.round(bmi, digits),
        "hba1c": np.round(hba1c, digits),
        "glucose": np.round(glucose, digits),
    })
'''
(C/'generator.py').write_text(generator,encoding='utf-8')
# Preserve derivation code in the candidate as a static review artifact. It has no random draws.
(C/'static_model_math.py').write_text(Path(__file__).read_text(encoding='utf-8'),encoding='utf-8')
dump(C/'checks.json',{'scope':'source_only','records':[{'name':'deterministic_law_moments','status':'pass','detail':'Executed assemble_initial.py for deterministic parameter derivation, positive-definiteness and exact finite-sum covariance/OLS calculations only. No generator import, random draws, generated table or target access.'},{'name':'generator_execution','status':'not_computable','detail':'Intentionally not executed by constructor. Controller must freeze and use supplied isolated execution adapter.'},{'name':'source_output_feedback','status':'not_computable','detail':'Sidecars submitted; no source statistic has yet been calculated on generated output. Exact source populations unavailable.'}],'artifacts':[{'path':'static_math_report.json','sha256':sha(C/'static_math_report.json')},{'path':'static_model_math.py','sha256':sha(C/'static_model_math.py')}]})

decision=f'''# Initial scientific decision

This is one fully specified, assumption-dependent virtual cohort for the requested primary and secondary linear projections. It is not an estimate of a uniquely identified Chinese population law.

## Construction and evidence choices

Generate3000 independent people, with Hainan's selected-sample female fraction. Within sex, use a Gaussian copula for age, BMI, glucose and HbA1c. Age is a rounded normal restricted to35-74, with Hainan's mean/SD as pre-restriction parameters. BMI is lognormal with the JDPP median and log-quartile spread. HbA1c and glucose are shifted lognormal with Hainan means/SDs; the assumed lower locations3.5percent and2mmol/L regularize low tails without truncating high observations. Single skewed marginals stand in for the aggregate disease/treatment mixture: no identifiable diabetes prevalence, treatment status or mechanism is claimed.

Hainan is geographically relevant and retains diabetes/treatment, making its descriptive glycaemic margins preferable here to nondiabetic European margins. Its frame/date/age uncertainties remain. JDPP provides explicit BMI margins and BMI-HbA1c Pearson correlations but is Japanese IGT-selected; transferring them unchanged is a substantial, visible modeling choice. The two correlations remain sex-specific0.29/0.08. They are converted using the chosen lognormal margins. Hainan's Spearman0.44/0.50 is converted via2*sin(pi*rho/6), never equated with Pearson or latent correlation. The BMI median and log-quartile ratio fit cannot preserve both asymmetric source quartile endpoints, and this is recorded in the static report.

The missing age-BMI, age-glucose and BMI-glucose latent correlations are assumed0.10,0.20 and0.25. They are not estimates from the packet. A normal exponential-tilting identity calculates the exact covariance of bounded integer age with each shifted lognormal. The age-HbA1c latent correlation is solved so the within-sex population OLS age term equals0.010percent/year, borrowing the magnitude from Pani NHANES under an explicit source-to-target and sex-homogeneity assumption. Weighted US nondiabetic evidence does not validate that target law. Neither additional source precision nor confidence weights are invented.

LifeLines ModelIII has a continuous BMI term0.05mmol/mol perkg/m^2 (algebraically0.0045746percent perkg/m^2), while its age/gender-only term is0.13mmol/mol perkg/m^2. These are different adjustments in the same cohort. Its CI levels and gender coding are unresolved. Hoorn Q4-versus-Q1 effects-0.135 and-0.022percent condition on waist, hip,2h glucose and other variables; they are not linear slopes. These conflicting conditional findings remain in evidence and unavailable feedback entries. No sign averaging or substitution is performed, and omitted-covariate independence is not assumed. JDPP's unresolved Beta and Hainan's ambiguous regression scale/orientation are withheld.

## What the joint model implies

For centered X=(age,BMI,glucose), the primary within-sex coefficient is Var(X)^-1 Cov(X,HbA1c). With an intercept and female indicator but no sex interactions, the requested pooled slope uses the sex-probability-weighted within-sex covariance matrices. The female coefficient is the difference of sex means after applying those common slopes. Thus the BMI coefficient emerges from the full covariance law; it is not set to any source adjusted coefficient. The secondary projection removes glucose from that matrix rather than reusing the primary BMI term.

Deterministic unrounded-law primary coefficients in order intercept,BMI,glucose,age,female are {projection['primary']}. Secondary coefficients in order intercept,BMI,age,female are {projection['secondary']}. These are algebraic consequences before sampling, not generated-data or target results. The static report also changes only the unreported BMI-glucose latent correlation to0.10 and0.40: this demonstrates structural sensitivity without selecting a favorable realization or assigning scenario probabilities.

Age and sex are bounded; all other variables are shifted exponentials of a positive-definite Gaussian vector. Gaussian moment generating functions give finite polynomial joint moments of every order. Nondegenerate predictor variation gives unique population linear projections. Integer-age covariances are evaluated by finite sums, not a continuous-age approximation. Double precision and deterministic bisection are the numerical approximations; final8-decimal table rounding is at most5e-9 per cell. Lognormal tails are assumptions and need empirical scrutiny.

## Applicability and checks

The construction supports inspecting distributions, Pearson/Spearman associations and the two declared regressions under its law. These uses remain assumption-dependent, especially glucose-adjusted BMI. It cannot establish causal BMI effects, individual recovery, clinical decision validity, national representation, treatment response or calibrated target uncertainty. Target fasting adherence and serum/plasma equivalence are unverified; the baseline assumes no extra contamination, without claiming none exists.

Source feedback compares only the actual generated target table, not a relabeled source sample. Hainan means, sex fraction and Spearman plus JDPP Pearson are approximate raw comparisons. Unknown SD denominator/quantile convention and incompatible conditional estimands remain unavailable. Source SD denotes individual dispersion. Exact source replay is not attempted because unreported joint populations and omitted variables would require further unsupported detail.

The construction used the five admitted originals and reviewed packet only, with zero new searches/downloads and no generator execution. Analytical/static calculations are preserved. Contract validation and semantic preflight are the remaining authorized constructor checks. Initial acquisition is closed; at most one controller feedback revision/retain decision remains. No seed is chosen here.
'''
(C/'decision.md').write_text(decision,encoding='utf-8')
dump(B/'drafts/construction_record.json',{'stage':'initial_written_static_math_complete','allowed_inputs_read':['CONSTRUCTION_ASSIGNMENT.md','task.json','request.json','SOURCE_ADMISSION.json','registry.json','reviewed_evidence/EVIDENCE_CANDIDATES.json','reviewed_evidence/EVIDENCE_REPORT.md','reviewed_evidence/INDEPENDENT_REVIEW.md','sources originals','evidence-cohort-generation skill and harness-interface','allowed cohort_harness interface code and docs'],'new_searches':0,'new_downloads':0,'generator_executions':0,'random_draws':0,'target_data_or_old_results_read':False,'sidecar_names':['whole_cohort_feedback.json','source_semantics_v1.json'],'scientific_check':report['method']})
print(json.dumps({'written':str(C),'evidence_items':len(items),'feedback_checks':len(checks),'implied_ols':projection,'minimum_eigenvalues':{s:min(moments[s]['latent_eigenvalues']) for s in moments}},indent=2))
