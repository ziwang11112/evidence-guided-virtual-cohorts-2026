"""M11 source-only artifacts. Does not import or execute biomedical generators."""
from __future__ import annotations
import argparse, copy, hashlib, json, math, shutil, statistics, sys
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PLAN = json.loads((HERE/'source_plan.json').read_text(encoding='utf-8'))
INHERITED = {'ha':ROOT/'work/m10/ha/candidates/f', 'hb':ROOT/'work/m10/hb/bundle/candidates/final'}

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    Path(p).write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
def normq(u):
    nd=statistics.NormalDist()
    return np.fromiter((nd.inv_cdf(float(v)) for v in u),dtype=float,count=len(u))

def make_contexts():
    out={s['id']:[] for s in PLAN['scenarios']}
    for j,sex in enumerate(PLAN['sex_order']):
        age=np.concatenate([np.repeat(np.arange(lo,lo+10),count) for lo,count in zip(PLAN['age_bin_lower'],PLAN['baseline_counts'][sex])])
        n=len(age); u=(np.arange(n)+0.5)/n; za=normq(u)
        noise=np.random.default_rng(PLAN['source_covariate_seed']+j).standard_normal(n)
        for scenario in PLAN['scenarios']:
            rho=scenario['latent_correlation']; latent=rho*za+math.sqrt(1-rho*rho)*noise
            rank=np.argsort(np.argsort(latent,kind='stable'),kind='stable')
            zb=normq((rank+0.5)/n); q25,med,q75=PLAN['bmi_quartiles']; z75=statistics.NormalDist().inv_cdf(.75)
            if scenario['bmi_quantile_family']=='asymmetric_normal':
                scale=np.where(zb<0,(med-q25)/z75,(q75-med)/z75)
                bmi=med+scale*zb
            else:
                scale=np.where(zb<0,math.log(med/q25)/z75,math.log(q75/med)/z75)
                bmi=med*np.exp(scale*zb)
            bmi=np.clip(bmi,*PLAN['bmi_bounds_assumed'])
            out[scenario['id']].append(pd.DataFrame({'row_id':[f'source_{sex}_{i:05d}' for i in range(n)],'age_years':age,'sex':sex,'bmi_kg_m2':bmi}))
    return {k:pd.concat(v,ignore_index=True) for k,v in out.items()}

def item(eid,sid,loc,var,kind,estimate,unit,selection,**extras):
    d={'id':eid,'source_id':sid,'locator':loc,'variables':[var],'kind':kind,'estimate':estimate,'unit':unit,'uncertainty':{'kind':'not_reported'},'adjustment':[],'selection':selection,'applicability':'Overlapping SHIP-Trend baseline evidence; source approximation and exact subset mismatch remain declared.'}
    d.update(extras)
    if kind in {'median','quantile'}: d['method']='not_reported'
    return d

def common_evidence(bundle):
    # Union the two permitted inherited packets, retaining existing provenance IDs.
    ev=copy.deepcopy(read(INHERITED['ha']/'evidence.json'))
    known={x['id'] for x in ev['items']}
    for x in read(INHERITED['hb']/'evidence.json')['items']:
        if x['id'] not in known: ev['items'].append(x);known.add(x['id'])
    reg=read(bundle/'registry.json')['artifacts']
    byid={x['source_id']:x for x in reg}
    for sid,doi,pop in [('volzke2015','10.3238/arztebl.2015.0185','Whole SHIP-Trend baseline n4420; n2145 men/n2275 women; not exactly Masuch n4402.'),('grossmann2024_context_only','10.3390/ijms25031485','Whole SHIP-Trend baseline n4420 column; not selected n203 study subset. Context-only overlapping-cohort cross-check.')]:
        r=byid[sid]
        ev['sources'].append({'id':sid,'identifier':'https://doi.org/'+doi,'population':pop,'measurement':'Published baseline age in years and measured BMI in kg/m^2; shares cohort with ship2019; not independent evidence.','cohort_ids':['SHIP_Trend'],'artifacts':[{'path':r['path'],'sha256':r['sha256']}]})
    for var,unit,vals in [('age_years','year',[40,53,64]),('bmi_kg_m2','kg/m^2',[24.5,27.5,31.0])]:
        for q,v in zip([.25,.5,.75],vals):
            kind='median' if q==.5 else 'quantile'; extras={} if q==.5 else {'q':q}
            ev['items'].append(item(f'm11_ship_{var}_{int(q*100)}','ship2019','Table1, unweighted pooled SHIP-Trend column',var,kind,v,unit,'Masuch analyzed whole SHIP-Trend n4402; pregnancy/missingHbA1c excluded.',**extras))
    ev['items'].append(item('m11_ship_male_fraction','ship2019','Table1, men (%) row','sex','proportion',48.6,'%','Masuch whole SHIP-Trend n4402.'))
    for sex,counts in PLAN['baseline_counts'].items():
        for idx,(lo,count) in enumerate(zip(PLAN['age_bin_lower'],counts)):
            ev['items'].append(item(f'm11_agebin_{sex}_{lo}','volzke2015',f'Table1, SHIP-Trend {sex}, age bin {PLAN["age_bins_published"][idx]}, count {count}/{sum(counts)}','age_years','proportion',count/sum(counts),'1',f'Raw whole baseline {sex}; final >=70 bin open ended; n4420 cohort differs from HbA1c n4402.'))
    for var,unit,mean,sd,missing in [('age_years','year',51.96,15.46,0),('bmi_kg_m2','kg/m^2',28.12,5.23,7)]:
        for kind,v in [('mean',mean),('sd',sd)]:
            ev['items'].append(item(f'm11_grossmann_{var}_{kind}','grossmann2024_context_only','Table1, whole SHIP-TREND n4420 column',var,kind,v,unit,f'Whole baseline, pooled sexes; missing {missing}; context-only diagnostic, no fitting.'))
    return ev

def source_summary(contexts):
    result={}
    for key,d in contexts.items():
        result[key]={'n':len(d),'source_only':True,'covariates':{},'within_sex':{}}
        for v in ['age_years','bmi_kg_m2']:
            result[key]['covariates'][v]={'mean':float(d[v].mean()),'sd':float(d[v].std()),'quantiles':{str(q):float(d[v].quantile(q)) for q in [.25,.5,.75]},'min':float(d[v].min()),'max':float(d[v].max())}
        for sex,g in d.groupby('sex',sort=False):
            result[key]['within_sex'][sex]={'n':len(g),'age_bin_counts':{str(lo):int(((g.age_years>=lo)&(g.age_years<lo+10)).sum()) for lo in PLAN['age_bin_lower']},'pearson_age_bmi':float(g.age_years.corr(g.bmi_kg_m2)),'spearman_age_bmi':float(g.age_years.rank().corr(g.bmi_kg_m2.rank()))}
    return result

def check_context_invariants(contexts):
    for key,d in contexts.items():
        assert list(d.columns)==['row_id','age_years','sex','bmi_kg_m2']
        assert len(d)==PLAN['source_n'] and d.row_id.is_unique
        assert d.age_years.between(20,79).all() and d.bmi_kg_m2.between(15,50).all()
        for sex,counts in PLAN['baseline_counts'].items():
            g=d.loc[d.sex.eq(sex)]
            for lo,count in zip(PLAN['age_bin_lower'],counts):
                assert int(g.age_years.between(lo,lo+9).sum())==10*count
                for age in range(lo,lo+10):assert int(g.age_years.eq(age).sum())==count
    for key in contexts:
        pd.testing.assert_frame_equal(contexts[key][['row_id','age_years','sex']],contexts['primary'][['row_id','age_years','sex']])
    for sex in PLAN['sex_order']:
        a=contexts['primary'].loc[contexts['primary'].sex.eq(sex),'bmi_kg_m2'].to_numpy()
        b=contexts['alt1'].loc[contexts['alt1'].sex.eq(sex),'bmi_kg_m2'].to_numpy()
        assert np.array_equal(np.sort(a),np.sort(b))
        z=contexts['alt2'].loc[contexts['alt2'].sex.eq(sex),'bmi_kg_m2'].to_numpy()
        # Bounds may tie extreme BMI values; monotonic rank association cannot reverse.
        assert np.all(np.diff(z[np.lexsort((z,b))])>=0)

def recipe(context_hashes):
    contexts=[]
    for sc in PLAN['scenarios']:
        checks=[]
        def add(eid,kind,unit,column=None,selection=None,**kw):
            op={'kind':kind,'unit':unit,'selection':selection or [],'missing_policy':'error',**kw}
            if column:op['column']=column
            if kind in {'median','quantile'}:op['method']='linear'
            checks.append({'id':eid.replace('.','_'),'evidence_id':eid,'status':'approximate','operator':op,'assumption_ids':['M11_measurement'],'reason':'Source-only consistency diagnostic under the fixed approximated source-X distribution; covariate checks describe the approximation, and fitted medians are not independent validation.'})
        for sex,label in [('male','men'),('female','women')]:
            sel=[{'column':'sex','op':'eq','value':sex}]
            for q in [.25,.5,.75]:
                kind='median' if q==.5 else 'quantile';eid=f'ship_SHIP_Trend_{label}_median_None' if q==.5 else f'ship_SHIP_Trend_{label}_quantile_{q}'
                add(eid,kind,'%','hba1c_pct',sel,**({} if q==.5 else {'q':q}))
            add(f'ship_SHIP_Trend_{label}_age_beta_per_year','ols_coefficient','HbA1c percentage points per year',selection=sel,outcome='hba1c_pct',predictors=['age_years','bmi_kg_m2'],term='age_years',include_intercept=True)
            for lo in PLAN['age_bin_lower']:
                event={'column':'age_years','op':'ge','value':lo} if lo==70 else {'column':'age_years','op':'in','value':list(range(lo,lo+10))}
                add(f'm11_agebin_{sex}_{lo}','proportion','1',selection=sel,event=event)
        for var,unit in [('age_years','year'),('bmi_kg_m2','kg/m^2')]:
            for q in [.25,.5,.75]:
                add(f'm11_ship_{var}_{int(q*100)}','median' if q==.5 else 'quantile',unit,var,**({} if q==.5 else {'q':q}))
            for kind in ['mean','sd']:add(f'm11_grossmann_{var}_{kind}',kind,unit,var)
        add('m11_ship_male_fraction','proportion','%',event={'column':'sex','op':'eq','value':'male'})
        contexts.append({'id':sc['id'],'population':'Published SHIP-Trend baseline approximation; '+sc['description']+'; open>=70 compressed to70-79; original n4420 differs from HbA1c n4402.','reason':'Fixed source-X sensitivity for marginal-to-conditional location calibration; no target data.','assumption_ids':['M11_source_X','M11_support','M11_BMI','M11_dependence','M11_overlap'],'measurement':{'mode':'identity','description':'HbA1c %, age integer years, BMI kg/m^2, sex labels; age slopes divided by10 with originals retained.'},'input':{'path':f'source_contexts/{sc["id"]}.csv','sha256':context_hashes[sc['id']],'origin':'declared_source_covariates'},'checks':checks})
    return {'schema_version':1,'contexts':contexts}

def prepare(bundle,family):
    task=read(bundle/'task.json');assert task['mode']=='enrichment'
    cols=[c['name'] for c in task['columns'] if c['role']!='generated']
    assert cols==['row_id','age_years','sex','bmi_kg_m2']
    cand=bundle/'candidates/initial';cand.mkdir(parents=True,exist_ok=False)
    contexts=make_contexts();check_context_invariants(contexts)
    hashes={}
    for key,d in contexts.items():
        p=cand/f'source_contexts/{key}.csv';p.parent.mkdir(exist_ok=True)
        d.to_csv(p,index=False,float_format='%.17g',lineterminator='\n');hashes[key]=sha(p)
    src=INHERITED[family];shutil.copyfile(src/'generator.py',cand/'generator.py')
    spec=copy.deepcopy(read(src/'model_spec.json'))
    for a in spec['assumptions']:
        if a['id'] in {'A_source_context','Asource'}:a['description']='Superseded source-X scenario metadata for M11: see M11_source_X, M11_BMI, M11_dependence and source_plan.json. Original M10 artificial replay context is not used.'
        if a['id']=='Atransport':a['description']=a['description'].replace('supplied PNS participants','supplied target adults')
    extras={
      'M11_source_X':'Reported sex-age-bin counts from whole SHIP-Trend n4420, replicated10fold, uniform integer age within each bin; exact n4402 pregnancy/missingHbA1c exclusion covariates unknown. Frozen source covariates use no target rows.',
      'M11_support':'Open >=70 bin compressed to70-79 for inherited task support. Sampling age20-79 is not proof of source examination maximum. BMI clipped15-50 is numerical assumption, not published support.',
      'M11_BMI':'Both sexes share a pooledBMI marginal matching Masuch quartiles24.5,27.5,31.0. Primary/alt1 asymmetric-normal quantile tails and alt2 log-BMI tails are assumed; no raw sex-specificBMI law identified.',
      'M11_dependence':'Primary uses independence within sex; alt1/alt2 fixed Gaussian-copula latent rho+0.35, not a reported correlation. Actual source age-BMI dependence unknown.',
      'M11_measurement':'Identity source/task variables and units; published quantile method unknown, replay uses type7 linear interpolation. Mean regression slopes as median-location shifts require additive invariant residual law.',
      'M11_overlap':'Masuch2019,Volzke2015,Grossmann2024 share SHIP-Trend baseline participants. Grossmann pooled means/SD are context-only diagnostics; weighted VolzkeBMI is not fit. No independent replication.',
      'M11_calibration':'Prospectively fixed operation: sex location shift equals source published median minus pooled verified initial source outcome median over seeds94101/2/3, separately per frozen scenario. No other scientific parameter changes; all versions retained. Initial is the uncalibrated inherited comparator.'}
    spec['assumptions'].extend({'id':k,'description':v} for k,v in extras.items())
    write(cand/'model_spec.json',spec);write(cand/'evidence.json',common_evidence(bundle));write(cand/'source_replay.json',recipe(hashes))
    shutil.copyfile(HERE/'source_plan.json',cand/'source_plan.json')
    summary=source_summary(contexts)
    prep={'family':family,'generator_original_sha256':sha(src/'generator.py'),'generator_copied_sha256':sha(cand/'generator.py'),'same_generator_bytes':(src/'generator.py').read_bytes()==(cand/'generator.py').read_bytes(),'same_scientific_parameters':spec['parameters']==read(src/'model_spec.json')['parameters'],'plan_sha256':sha(HERE/'source_plan.json'),'source_context_hashes':hashes,'source_covariate_summary':summary,'biomedical_generator_imported_or_executed_locally':False,'target_observed_read_by_preparer':False}
    assert prep['same_generator_bytes'] and prep['same_scientific_parameters']
    write(cand/'preparation_check.json',prep)
    write(cand/'checks.json',{'scope':'source_only','records':[{'name':'artifact_and_source_X_preparation','status':'pass','detail':'Checked generator byte identity, unchanged initial scientific parameters, exact prescribed source-X row counts and age-bin counts; result bound in preparation_check.json. This is not biomedical generation.'},{'name':'biomedical_execution','status':'not_computable','detail':'Not executed when this candidate was prepared; actual harness replay feedback will remain outside this frozen candidate.'}],'artifacts':[{'path':'preparation_check.json','sha256':sha(cand/'preparation_check.json')}]})
    (cand/'decision.md').write_text(f'Inherited {family} scientific family, not a fresh independent construction. Initial scientific parameters and generator bytes are unchanged; source evidence/context metadata are expanded identically across families. The three fixed source-X scenarios and calibration rule are in source_plan.json. Only a later execution-backed source-median calibration may change sex locations. No target outcome/reference or result estimates were inspected. Source fitting is not target validity. All age/BMI/residual/transport limitations are retained. Prior-run check claims were not copied.\n',encoding='utf-8')
    print(json.dumps({'prepared':str(cand),'source_plan_sha256':prep['plan_sha256'],'source_n':PLAN['source_n'],'same_generator':True}),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--bundle',type=Path,required=True);ap.add_argument('--family',choices=['ha','hb'],required=True);args=ap.parse_args();prepare(args.bundle.resolve(),args.family)
