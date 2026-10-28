"""Read-only independent result audit; run only after explicit evaluator-complete signal.

Keeps participant data local. Writes only aggregate checks and discrepancies.
Does not call runner.evaluate, import production analysis, or generate cohorts.
"""
from pathlib import Path
import argparse
import collections
import datetime as dt
import hashlib
import itertools
import json
import math
import warnings
import numpy as np
import pandas as pd
from scipy import optimize, stats
import statsmodels.api as sm

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]/'stage1'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def finite(x): return x is not None and math.isfinite(x)
def state(row):
    if row.get('status')!='ok' or not finite(row.get('ci_low')) or not finite(row.get('ci_high')): return 'unavailable'
    return 'positive' if row['ci_low']>0 else 'negative' if row['ci_high']<0 else 'overlaps_null'

def pearson(x,y):
    use=np.isfinite(x)&np.isfinite(y);x=x[use];y=y[use];n=len(x)
    dx=x-np.mean(x);dy=y-np.mean(y)
    r=float(dx@dy/np.sqrt((dx@dx)*(dy@dy)))
    z=np.arctanh(np.clip(r,-1+1e-14,1-1e-14));zse=1/np.sqrt(n-3)
    lo,hi=np.tanh(z+np.array([-1,1])*1.95996398454*zse)
    t=r*np.sqrt((n-2)/max(1-r*r,1e-300))
    return dict(estimate=r,se=(1-r*r)*zse,ci_low=lo,ci_high=hi,p=2*stats.t.sf(abs(t),n-2),n_persons=n,n_rows=n)

def simple_results(df,case):
    out={}
    if case=='case_a':
        base=df.loc[df.month==0]
        for x,y in itertools.combinations(['pfs','gng','dd100','dd1000'],2):
            out[('baseline_pearson',x+'__'+y)]=pearson(base[x].to_numpy(float),base[y].to_numpy(float))
    else:
        endpoints=['leptin' if case=='case_b' else 'leptin_log10','body_mass','glucose','triglycerides'];changes={}
        for e in endpoints:
            x=df[e+'_pre'].to_numpy(float);y=df[e+'_post'].to_numpy(float);ok=np.isfinite(x)&np.isfinite(y)
            changes[e]=y-x;delta=(y-x)[ok];n=len(delta);estimate=np.sum(delta)/n
            sd=np.sqrt(np.sum((delta-estimate)**2)/(n-1));se=sd/np.sqrt(n);width=stats.t.ppf(.975,n-1)*se
            out[('paired_change',e)]={'estimate':estimate,'se':se,'ci_low':estimate-width,'ci_high':estimate+width,
                'p':2*stats.t.sf(abs(estimate/se),n-1),'change_sd':sd,'paired_r':pearson(x,y)['estimate'],'n_persons':n,'n_rows':n}
        for x,y in itertools.combinations(endpoints,2): out[('change_pearson',x+'__'+y)]=pearson(changes[x],changes[y])
    return out

def explicit_mixed(df,variable='weight_kg',proxy=False):
    if proxy:
        d=df[['person_id','weight_kg',variable]].dropna()
        y=(d.weight_kg.to_numpy()-d.weight_kg.mean())/d.weight_kg.std(ddof=1)
        pred=(d[variable].to_numpy()-d[variable].mean())/d[variable].std(ddof=1)
        X=np.column_stack([np.ones(len(d)),pred]);contrast=np.array([0.,1.]);key=('pooled_standardized_reml',variable);crit=1.96
    else:
        d=df[['person_id','month',variable]].dropna();y=d[variable].to_numpy()
        X=np.column_stack([np.ones(len(d))]+[(d.month==month).to_numpy(float) for month in [3,6,9,12]])
        contrast=np.array([0.,0.,0.,0.,1.]);key=('weight_time_reml' if variable=='weight_kg' else variable+'_time_reml','month_12_minus_0');crit=1.95996398454
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        fit=sm.MixedLM(y,X,groups=d.person_id.to_numpy()).fit(reml=True,method='powell',maxiter=600,disp=False)
    beta=np.asarray(fit.fe_params);cov=np.asarray(fit.cov_params())[:X.shape[1],:X.shape[1]]
    est=float(contrast@beta);se=float(np.sqrt(contrast@cov@contrast))
    results=dict(estimate=est,se=se,ci_low=est-crit*se,ci_high=est+crit*se,p=2*stats.norm.sf(abs(est/se)),n_rows=len(d),n_persons=d.person_id.nunique())
    # An independently optimized scalar REML objective checks the contrast
    # estimate without relying on the MixedLM optimizer or formula machinery.
    groups=[np.where(d.person_id.to_numpy()==pid)[0] for pid in d.person_id.unique()]
    p=X.shape[1];n=len(y)
    def gls(q,ret=False):
        xx=np.zeros((p,p));xy=np.zeros(p);yy=0.;logdet=0.
        for ix in groups:
            xx0=X[ix];yy0=y[ix];m=len(ix);a=q/(1+m*q)
            sx=xx0.sum(axis=0);sy=yy0.sum()
            xx+=xx0.T@xx0-a*np.outer(sx,sx);xy+=xx0.T@yy0-a*sx*sy
            yy+=yy0@yy0-a*sy*sy;logdet+=np.log1p(m*q)
        b=np.linalg.solve(xx,xy);rss=yy-xy@b
        objective=(n-p)*np.log(rss/(n-p))+logdet+np.linalg.slogdet(xx)[1]
        return (objective,b) if ret else objective
    opt=optimize.minimize_scalar(lambda logq:gls(np.exp(logq)),bounds=(-18,18),method='bounded',options={'xatol':1e-11})
    q=np.exp(opt.x)
    if gls(0)<gls(q):q=0.
    independent_est=float(contrast@gls(q,True)[1])
    return key,results,independent_est,bool(fit.converged)

def audit(evaluation):
    out=ROOT/'custodian'/evaluation
    if not (out/'evaluation_manifest.json').exists(): raise RuntimeError('No committed complete evaluation manifest')
    checks=[];discrepancies=[];numeric_counts=collections.Counter();largest=collections.defaultdict(float);mixed_samples=[]
    def check(name,ok,detail=None):
        checks.append({'check':name,'passed':bool(ok),'detail':detail})
        if not ok:discrepancies.append(checks[-1])
    def eq(name,a,b,atol=1e-9,rtol=1e-9):
        ok=(a is None and b is None) or (finite(a) and finite(b) and math.isclose(a,b,abs_tol=atol,rel_tol=rtol))
        check(name,ok, None if ok else {'committed':a,'recomputed':b})
    def compare(name,row,recomputed,family):
        for key,val in recomputed.items():
            eq(name+':'+key,row.get(key),float(val))
            if finite(row.get(key)) and finite(val): largest[family+':'+key]=max(largest[family+':'+key],abs(row[key]-float(val)))
        numeric_counts[family]+=1
    fm=read(out/'evaluation_manifest.json');freeze=read(ROOT/'protocol_freeze.json');inventory=read(ROOT/'final_inventory.json')
    for rel,digest in freeze['files'].items():check('freeze_hash:'+rel,sha(ROOT/rel)==digest)
    for rel,digest in fm['files'].items():check('evaluation_hash:'+rel,sha(out/rel)==digest)
    check('protocol_commitment',fm['protocol_sha256']==inventory['protocol_sha256']==sha(ROOT/'protocol_freeze.json'))
    expected_manifests={x['path'].replace('\\','/'):x['sha256'] for x in inventory['records']}
    actual_manifests={k.replace('\\','/'):v for k,v in fm['final_manifests'].items()}
    check('all_final_manifests',actual_manifests==expected_manifests and len(expected_manifests)==21)
    check('all_requested_cohorts',fm['requested_cohorts']==inventory['requested_cohorts']==420)
    registry=read(ROOT/'analysis_registry.json');reg={(x['case_id'],x['analysis'],x['term']):x for x in registry}
    records=read(out/'analysis_records.json');table=pd.DataFrame(records)
    by_draw=collections.defaultdict(list)
    for row in records:by_draw[(row['run_id'],row['draw'])].append(row)
    check('term_record_count',len(records)==fm['analysis_records']==7700)
    check('unique_term_keys',len({(r['run_id'],r['draw'],r['analysis'],r['term']) for r in records})==7700)
    check('case_record_counts',table.case_id.value_counts().to_dict()=={'case_a':4900,'case_b':1400,'case_c':1400})
    check('cohort_record_groups',len(by_draw)==420)
    ref={};references={}
    for case in ['case_a','case_b','case_c']:
        rrows=read(out/f'{case}_reference_analyses.json');references[case]=rrows
        check(case+':reference_inventory',{(r['analysis'],r['term']) for r in rrows}=={(a,t) for c,a,t in reg if c==case})
        for row in rrows:ref[(case,row['analysis'],row['term'])]=row
        df=pd.read_csv(ROOT/'custodian'/f'{case}_reference.csv')
        simple=simple_results(df,case)
        for row in rrows:
            key=(row['analysis'],row['term'])
            if key in simple:compare('reference:'+case+':'+':'.join(key),row,simple[key],'reference_simple')
        if case=='case_a':
            for variable,proxy in [('weight_kg',False),('pfs',True)]:
                key,computed,gls_est,converged=explicit_mixed(df,variable,proxy)
                row=ref[(case,*key)];compare('reference:'+':'.join(key),row,computed,'mixed_explicit_design')
                eq('reference:independent_gls:'+str(key),row['estimate'],gls_est,atol=2e-4,rtol=2e-4)
                mixed_samples.append({'dataset':'case_a reference','analysis':key[0],'term':key[1],'committed_estimate':row['estimate'],'independent_gls_estimate':gls_est,'explicit_design_converged':converged})
    check('reference_record_count',len(ref)==fm['reference_analysis_records']==55)
    expected_draws=set();failures=[]
    selected_mixed={('case_a_build_01_ordinary_v1',1),('case_a_build_02_proposed_v1',15),('case_a_build_00_statistical_v1',15)}
    for rel,digest in expected_manifests.items():
        mp=ROOT/rel;manifest=read(mp);task=manifest['task'];case=task['case_id'];rid=task['run_id']
        check(rid+':final_manifest_hash',sha(mp)==digest)
        check(rid+':final_before_evaluation',manifest['created_utc']<=fm['created_utc'])
        for rec in manifest['records']:
            key=(rid,rec['draw']);expected_draws.add(key);rows=by_draw[key]
            check(rid+f":draw{rec['draw']}:inventory",{(r['analysis'],r['term']) for r in rows}=={(a,t) for c,a,t in reg if c==case})
            check(rid+f":draw{rec['draw']}:identity",all(r['seed']==rec['seed'] and r['scenario']==rec['scenario'] and r['case_id']==case and r['branch']==task['branch'] and r['lineage_id']==task['lineage_id'] for r in rows))
            if rec['status']!='ok':failures.append(key);continue
            path=mp.parent/rec['path'];check(rid+f":draw{rec['draw']}:cohort_hash",sha(path)==rec['sha256'])
            df=pd.read_csv(path);simple=simple_results(df,case)
            for row in rows:
                termkey=(row['analysis'],row['term'])
                if termkey in simple:compare(rid+f":draw{rec['draw']}:"+':'.join(termkey),row,simple[termkey],'synthetic_simple')
            if key in selected_mixed:
                for variable,proxy in [('weight_kg',False),('pfs',True)]:
                    termkey,computed,gls_est,converged=explicit_mixed(df,variable,proxy)
                    row=next(r for r in rows if (r['analysis'],r['term'])==termkey)
                    compare(rid+f":draw{rec['draw']}:"+':'.join(termkey),row,computed,'mixed_explicit_design')
                    eq(rid+f":draw{rec['draw']}:independent_gls:"+str(termkey),row['estimate'],gls_est,atol=2e-4,rtol=2e-4)
                    mixed_samples.append({'dataset':rid+f":draw{rec['draw']}",'analysis':termkey[0],'term':termkey[1],'committed_estimate':row['estimate'],'independent_gls_estimate':gls_est,'explicit_design_converged':converged})
    check('exact_draw_identity',set(by_draw)==expected_draws)
    check('generation_failures',not failures,failures)
    for i,row in enumerate(records):
        key=(row['case_id'],row['analysis'],row['term']);rr=ref[key];policy=reg[key];label='record'+str(i)
        check(label+':registry',row['validation_role']==policy['validation_role'] and row['multiplicity_family']==policy['multiplicity_family'])
        s=state(row);rs=state(rr);valid=s!='unavailable' and rs!='unavailable'
        check(label+':state',s==row['evidence_state'] and rs==row['reference_evidence_state'] and valid==row['valid_comparison'])
        for k in ['estimate','se','ci_low','ci_high']:eq(label+':reference_'+k,row['reference_'+k],rr[k])
        if valid:
            check(label+':agreement',row['evidence_state_agreement']==(s==rs))
            check(label+':unsupported',row['unsupported_evidence_discrepancy']==(rs=='overlaps_null' and s in ['positive','negative']))
            direction=(np.sign(row['estimate'])==np.sign(rr['estimate'])) if rs in ['positive','negative'] else None
            check(label+':direction',row['direction_agreement']==direction and row['reference_direction_established']==(rs in ['positive','negative']))
            eq(label+':absolute_error',row['absolute_estimate_error'],abs(row['estimate']-rr['estimate']))
            eq(label+':se_ratio',row['se_ratio'],row['se']/rr['se'] if rr['se']>0 else None)
            if 'change_sd' in row:
                eq(label+':change_sd_ratio',row['change_sd_ratio'],row['change_sd']/rr['change_sd'])
                eq(label+':paired_r_error',row['paired_r_absolute_error'],abs(row['paired_r']-rr['paired_r']))
    grouping=['case_id','lineage_id','branch','scenario','validation_role','multiplicity_family','analysis','term']
    groups={tuple(row[k] for k in grouping):row for row in read(out/'scenario_summaries.json')}
    check('scenario_summary_count',len(groups)==sum(1 for _ in table.groupby(grouping)))
    for key,g in table.groupby(grouping):
        s=groups[key];v=g.loc[g.valid_comparison];label='summary:'+str(key)
        check(label+':denominator',s['analyses_total']==len(g) and s['analyses_usable']==len(v))
        eq(label+':usable_fraction',s['usable_fraction'],len(v)/len(g))
        eq(label+':agreement',s['evidence_state_agreement'],v.evidence_state_agreement.mean() if len(v) else None)
        eq(label+':unsupported_count',s['unsupported_evidence_discrepancies'],float(v.unsupported_evidence_discrepancy.sum()) if len(v) else 0)
        eq(label+':median_error',s['median_absolute_estimate_error'],v.absolute_estimate_error.median() if len(v) else None)
        eq(label+':median_se_ratio',s['median_se_ratio'],v.se_ratio.median() if len(v) else None)
    sensitivities=read(out/'scenario_sensitivity.json');skeys=['case_id','lineage_id','branch','analysis','term'];sgroups={key:g for key,g in table.groupby(skeys)}
    check('scenario_sensitivity_count',len(sensitivities)==len(sgroups))
    for row in sensitivities:
        key=tuple(row[k] for k in skeys);g=sgroups[key];modal=[]
        check('sensitivity:'+str(key)+':scenario_set',set(row['scenarios'])==set(g.scenario.unique()))
        for scenario,d in row['scenarios'].items():
            sub=g.loc[g.scenario==scenario];counts=dict(collections.Counter(sub.evidence_state));modes=sorted(k for k,v in counts.items() if v==max(counts.values()));modal.append(tuple(modes))
            check('sensitivity:'+str(key)+':'+scenario,d['n']==len(sub) and d['states']==counts and d['modal_states']==modes and d['rates']=={k:v/len(sub) for k,v in counts.items()})
            est=sub.loc[sub.status=='ok','estimate'].dropna()
            eq('sensitivity:'+str(key)+':'+scenario+':median',d['median_estimate'],est.median() if len(est) else None)
            if len(est):check('sensitivity:'+str(key)+':'+scenario+':range',np.allclose(d['estimate_range'],[est.min(),est.max()],atol=1e-9,rtol=1e-9))
        check('sensitivity:'+str(key)+':disagreement',row['between_scenario_modal_evidence_state_disagreement']==(len(set(modal))>1))
    paired=read(out/'paired_lineage_comparisons.json')
    check('paired_lineage_count',len(paired)==165)
    for row in paired:
        g=table.loc[(table.case_id==row['case_id'])&(table.lineage_id==row['lineage_id'])&(table.analysis==row['analysis'])&(table.term==row['term'])]
        check('paired:'+str(row['lineage_id'])+':arms',set(row['arms'])=={'ordinary','proposed'})
        for branch,scenarios in row['arms'].items():
            for s in scenarios:
                sub=g.loc[(g.branch==branch)&(g.scenario==s['scenario'])];v=sub.loc[sub.valid_comparison]
                check('paired:'+str(row['lineage_id'])+':denominator',s['draws']==len(sub) and s['usable']==len(v))
                eq('paired:agreement',s['evidence_state_agreement'],v.evidence_state_agreement.mean() if len(v) else None)
                eq('paired:unsupported_rate',s['unsupported_evidence_discrepancy_rate'],v.unsupported_evidence_discrepancy.mean() if len(v) else None)
                eq('paired:median_error',s['median_absolute_estimate_error'],v.absolute_estimate_error.median() if len(v) else None)
    fit_warnings=collections.defaultdict(set);warning_terms=collections.Counter()
    for row in records:
        for warning in row.get('fit_warnings',[]):
            fit_warnings[warning].add((row['run_id'],row['draw'],row['analysis'],row['term'] if row['analysis']=='pooled_standardized_reml' else 'trajectory'))
            warning_terms[warning]+=1
    warning_summary={w:{'term_records':warning_terms[w],'unique_fits':len(fits),'analyses':dict(collections.Counter(x[2] for x in fits)),
                        'specific_fits':sorted(fits) if 'Hessian' in w else None} for w,fits in fit_warnings.items()}
    result={'audit_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'evaluation':evaluation,'evaluation_manifest_sha256':sha(out/'evaluation_manifest.json'),
        'checks_total':len(checks),'checks_passed':sum(c['passed'] for c in checks),'discrepancies':discrepancies,'numeric_rows_recomputed':dict(numeric_counts),
        'largest_absolute_numeric_differences':dict(largest),'mixed_model_checks':mixed_samples,'term_records':len(records),
        'status_counts':table.status.value_counts().to_dict(),'dataset_failure_count':len(read(out/'dataset_failures.json')),'fit_warning_summary':warning_summary,
        'unusable_record_count':int((~table.valid_comparison).sum()),'scenario_summaries':len(groups),'scenario_sensitivity_rows':len(sensitivities),'paired_lineage_rows':len(paired),
        'audit_implementation_corrections':['The initial inventory comparison did not normalize Windows backslashes versus forward slashes. All 21 path/hash pairs agreed after separator normalization. This audit-only correction changes no production artifact or result.'],
        'interpretation':['Independent implementation recomputed all paired and baseline-correlation quantities from committed CSVs.',
            'Eight representative mixed-model terms use explicit design matrices, plus independently optimized scalar REML GLS checks on their estimates.',
            'Shared numerical libraries and fixed inferential assumptions remain; this is computational verification, not clinical or coverage validation.']}
    (HERE/'evaluation_audit.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,allow_nan=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--evaluation-authorized',action='store_true');p.add_argument('--evaluation',default='evaluation_v1');args=p.parse_args()
    if not args.evaluation_authorized:raise SystemExit('Explicit authorization flag required after complete evaluation signal')
    audit(args.evaluation)
