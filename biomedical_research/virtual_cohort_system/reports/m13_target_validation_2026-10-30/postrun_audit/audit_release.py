"""Independent post-run arithmetic and provenance audit; aggregate output only."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

import numpy as np
import pandas as pd
from scipy.stats import t

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
PROJECT=ROOT.parents[1]
sys.path.insert(0,str(PROJECT))
from cohort_harness.execution import verify_execution

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csv(p):return pd.read_csv(p,dtype={'id':str},float_precision='round_trip')
spec=importlib.util.spec_from_file_location('independent_preaccess_kernel',ROOT/'audits/independent_fixture_checks.py')
reference=importlib.util.module_from_spec(spec);spec.loader.exec_module(reference)
independent_fit=reference.independent_fit

def quantiles(y,w):
    # Independently sort row values; ties return the same value at any crossing.
    order=np.argsort(y,kind='stable')
    cum=np.cumsum(w[order]);total=sum(w)
    return [float(y[order][np.flatnonzero(cum>=p*total)[0]]) for p in [.25,.5,.75]]

def schedule(full):
    y=full.DXDTOPF.to_numpy();bmi=full.BMXBMI.to_numpy();age=full.RIDAGEYR.to_numpy()
    eligible=(np.isfinite(y)&full.DXAEXSTS.eq(1).to_numpy()&full.RIDAGEYR.between(20,59).to_numpy()&full.RIDRETH3.isin([3,4]).to_numpy()&full.RIAGENDR.isin([1,2]).to_numpy()&full.BMXBMI.between(18.5,35).to_numpy())
    B=(bmi-24)/5;A=(age-40)/10;R=full.RIDRETH3.eq(4).to_numpy(float)
    linear=np.column_stack([np.ones(len(full)),B,A,R]);quad=np.column_stack([linear,B*B]);mean=np.ones((len(full),1))
    result=[]
    for domain in ['primary','extension']:
        base=eligible&(bmi<30 if domain=='primary' else bmi>=30)
        for sex,code in [('male',1),('female',2)]:
            d=base&full.RIAGENDR.eq(code).to_numpy()
            for stat,X,c in [('mean',mean,[1]),('bmi_per5',linear,[0,1,0,0]),('age_per10',linear,[0,0,1,0])]:
                result.append(dict(endpoint=f'{domain}.{sex}.{stat}',kind='linear',mask=d,X=X,c=np.array(c)))
            if domain=='primary':result.append(dict(endpoint=f'{domain}.{sex}.bmi_curvature_second_difference',kind='linear',mask=d,X=quad,c=np.array([0,0,0,0,1.28])))
            for ag,lo,hi in [('20_39',20,39),('40_59',40,59)]:
                ad=d&(age>=lo)&(age<=hi)
                bins=[('18_5_lt25',18.5,25),('25_lt30',25,30)] if domain=='primary' else [('30_35',30,35)]
                for label,lo,hi in bins:
                    bd=ad&(bmi>=lo)&((bmi<hi) if domain=='primary' else (bmi<=hi))
                    for stat in ['q25','q50','q75','iqr']:
                        result.append(dict(endpoint=f'{domain}.{sex}.age{ag}.bmi{label}.{stat}',kind='distribution',mask=bd,stat=stat))
    return eligible,result

def main():
    checked=[];comparisons=[];numerical=[];receipt_checks=[]
    def check(name,condition):
        assert bool(condition),name
        checked.append(name)
    def compare(label,a,b):
        difference=abs(float(a)-float(b))
        numerical.append(difference)
        assert np.isclose(a,b,rtol=1e-9,atol=1e-8),(label,a,b,difference)
    frozen=read(ROOT/'preaccess_freeze.json');protocol=read(ROOT/'protocol.json');manifest=read(ROOT/'generated_manifest.json');aggregate=read(ROOT/'results/aggregate.json')
    check('19 frozen files unchanged',len(frozen['files'])==19 and all(sha(ROOT/p)==h for p,h in frozen['files'].items()))
    check('manifest exact roster',[{k:x[k] for k in ['table_id','kind','builder','candidate','seed']} for x in manifest['tables']]==protocol['tables'])
    check('16 complete tables and full schedule',len(manifest['tables'])==16 and aggregate['table_count']==16 and aggregate['panel_count']==62 and all(x['status']=='complete' and len(x['panel'])==62 for x in aggregate['tables']))
    check('manifest preaccess binding',manifest['preaccess_sha256']==sha(ROOT/'preaccess_freeze.json'))
    fullpath=ROOT/'custodian/acquisition_corrected/private/full_frame.csv'
    check('aggregate input hashes',aggregate['input_sha256']==dict(full_frame=sha(fullpath),observed=sha(manifest['observed_path']),manifest=sha(ROOT/'generated_manifest.json'),preaccess=sha(ROOT/'preaccess_freeze.json')))
    full=csv(fullpath);obs=csv(manifest['observed_path']);allowed=protocol['observed_columns']
    weights=full.WTMEC2YR.to_numpy();strata=full.SDMVSTRA.to_numpy();psu=full.SDMVPSU.to_numpy();real_y=full.DXDTOPF.to_numpy()
    eligible,plan=schedule(full)
    check('independent 62 endpoint schedule',len(plan)==62 and [x['endpoint'] for x in plan]==[x['endpoint'] for x in aggregate['measured']])
    check('exact observed eligible order',full.loc[eligible,'id'].tolist()==obs.id.tolist())
    check('real outcome physical support',np.all((real_y[np.isfinite(real_y)]>=0)&(real_y[np.isfinite(real_y)]<=100)))
    deployments=read(ROOT/'deployment_manifest.json')
    for entry in deployments['deployments']:
        model=next(x for x in protocol['models'] if x['builder']==entry['builder'] and x['candidate']==entry['candidate'])
        candidate=Path(entry['bundle'])/'candidates'/entry['candidate']
        source=Path(model['source_bundle'])/'candidates'/entry['candidate']
        check('science '+entry['builder']+' '+entry['candidate'],sha(candidate/'generator.py')==model['generator_sha256']==sha(source/'generator.py') and sha(candidate/'model_spec.json')==model['spec_sha256']==sha(source/'model_spec.json') and sha(source/'freeze.json')==model['source_freeze_sha256'] and sha(candidate/'freeze.json')==entry['deployment_freeze_sha256'])
    vectors={'measured':real_y};stored={'measured':aggregate['measured']}
    for tab,release in zip(manifest['tables'],aggregate['tables']):
        name=tab['table_id'];path=Path(tab['path']);table=csv(path)
        check(name+' file hash',sha(path)==tab['sha256']==release['sha256'])
        check(name+' row/covariate preservation',list(table.columns)==allowed+['bodyfat'] and table.id.is_unique and set(table.id)==set(obs.id))
        table=table.set_index('id').loc[obs.id].reset_index()
        check(name+' allowed observations unchanged',np.allclose(table[allowed[1:]],obs[allowed[1:]],rtol=1e-12,atol=1e-12))
        yy=table.bodyfat.to_numpy();check(name+' physical generated support',np.isfinite(yy).all() and np.all((yy>=0)&(yy<=100)))
        if tab['kind']=='agent':
            bundle=ROOT/'deployment'/tab['builder'];run_id=f"{tab['candidate']}_{tab['seed']}"
            rec=verify_execution(bundle,run_id)
            check(name+' isolated receipt verified',rec['status']=='success' and rec['generator_executed'] and rec['isolation_scope']=='generator_process_only' and rec['limits']['seed']==tab['seed'])
            receipt_checks.append(dict(table_id=name,status=rec['status'],runtime=rec['runtime'],seed=rec['limits']['seed']))
        else:
            rec=read(tab['reference_receipt_path'])
            check(name+' reference receipt',rec['output_sha256']==sha(path) and rec['observed_sha256']==sha(manifest['observed_path']) and rec['controller_sha256']==sha(ROOT/'controller.py') and rec['seed']==tab['seed'] and rec['table_id']==name)
            mean=76+.053*obs.age.to_numpy()-20.6*obs.male.to_numpy()+(154*obs.male.to_numpy()-1097.8)/obs.bmi.to_numpy()+.034*obs.male.to_numpy()*obs.age.to_numpy()
            expected=mean.copy();redraws=0
            if tab['seed'] is not None:
                rng=np.random.default_rng(tab['seed']);expected+=rng.normal(0,4.31,len(mean))
                while np.any((expected<0)|(expected>100)):
                    bad=(expected<0)|(expected>100);redraws+=int(bad.sum());expected[bad]=mean[bad]+rng.normal(0,4.31,int(bad.sum()))
            check(name+' independent formula and rejection stream',np.allclose(expected,yy,rtol=0,atol=4e-14) and rec['redrawn_values']==redraws)
        yfull=np.full(len(full),np.nan);yfull[eligible]=yy;vectors[name]=yfull;stored[name]=release['panel']
    for table_id,values in vectors.items():
        for item,reported in zip(plan,stored[table_id]):
            d=item['mask'];w=weights[d];n=int(d.sum());npsu=len(set(zip(strata[d],psu[d])));nstrata=len(set(strata[d]));df=npsu-nstrata;kish=sum(w)**2/sum(w*w)
            estimable=n>=30 and kish>=20 and npsu>=8 and df>=4
            if item['kind']=='linear':estimable=estimable and np.linalg.matrix_rank(item['X'][d])==item['X'].shape[1] and n>item['X'].shape[1]
            check(table_id+' '+item['endpoint']+' gate',(reported['status']=='estimable')==estimable and reported['gate']['n']==n and reported['gate']['domain_psus']==npsu and reported['gate']['domain_strata']==nstrata and reported['df']==df)
            compare('Kish',kish,reported['gate']['kish_n'])
            if not estimable:continue
            row=dict(table_id=table_id,endpoint=item['endpoint'],kind=item['kind'],n=n,kish_n=kish,domain_psus=npsu,domain_strata=nstrata,df=df)
            if item['kind']=='linear':
                b,v,fitdf=independent_fit(item['X'],values,weights,strata,psu,d);c=item['c'];estimate=float(c@b);se=float(np.sqrt(c@v@c));hw=float(t.ppf(.975,df)*se)
                computed=dict(estimate=estimate,se=se,ci_low=estimate-hw,ci_high=estimate+hw)
                for key,val in computed.items():compare(table_id+' '+item['endpoint']+' '+key,val,reported[key])
                row.update(computed)
                if table_id!='measured':
                    b,v,_=independent_fit(item['X'],values-real_y,weights,strata,psu,d);pe=float(c@b);pse=float(np.sqrt(c@v@c));phw=float(t.ppf(.975,df)*pse)
                    paired=dict(estimate=pe,se=pse,ci_low=pe-phw,ci_high=pe+phw)
                    for key,val in paired.items():compare(table_id+' paired '+item['endpoint']+' '+key,val,reported['paired_difference'][key])
                    row.update({'paired_'+k:v for k,v in paired.items()})
            else:
                q=quantiles(values[d],w);estimate={'q25':q[0],'q50':q[1],'q75':q[2],'iqr':q[2]-q[0]}[item['stat']]
                compare(table_id+' '+item['endpoint'],estimate,reported['estimate']);row['estimate']=estimate
                check(table_id+' '+item['endpoint']+' no quantile intervals',reported['interval_available'] is False and reported['se'] is None and reported['ci_low'] is None and reported['ci_high'] is None)
            if table_id!='measured':
                real_report=next(x for x in aggregate['measured'] if x['endpoint']==item['endpoint'])
                error=estimate-real_report['estimate'];compare('signed error',error,reported['signed_error']);compare('absolute error',abs(error),reported['absolute_error']);row.update(signed_error=error,absolute_error=abs(error))
            comparisons.append(row)
    # Check all seed summaries, including both absolute error conventions.
    for summary in aggregate['seed_summaries']:
        group=[x for x in aggregate['tables'] if all(x[k]==summary[k] for k in ['kind','builder','candidate'])]
        check('seed group '+summary['candidate'],len(group)==3 and sorted(x['seed'] for x in group)==protocol['seeds'])
        for i,row in enumerate(summary['panel']):
            check('seed completeness',row['available_draws']==row['required_draws']==3 and row['status']=='complete')
            for field in ['estimate','signed_error','absolute_error']:
                vals=[tab['panel'][i][field] for tab in group]
                for key,val in [('mean',np.mean(vals)),('min',min(vals)),('max',max(vals))]:compare('seed '+field+' '+key,val,row['summaries'][field][key])
    dfout=pd.DataFrame(comparisons);dfout.to_csv(HERE/'independent_aggregate_recomputation.csv',index=False)
    summary=dict(status='pass',aggregate_sha256=sha(ROOT/'results/aggregate.json'),checks=len(checked),numeric_comparisons=len(numerical),maximum_absolute_numeric_discrepancy=max(numerical),
        measured_panels=1,generated_panels=16,endpoints_per_panel=62,aggregate_estimand_rows=len(comparisons),linear_estimand_rows=int((dfout.kind=='linear').sum()),distribution_estimand_rows=int((dfout.kind=='distribution').sum()),paired_linear_intervals=int(dfout.paired_estimate.notna().sum()),isolated_receipts_verified=receipt_checks,reference_formulas_verified=4,
        scope='Actual frozen release independently recomputed with SVD/row-influence survey kernel and inverse ECDF; aggregate output only. No scientific or frozen file changes.')
    (HERE/'audit_results.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='isolated_receipts_verified'},indent=2))

if __name__=='__main__':main()
