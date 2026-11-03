"""Independent closed-form review: never import/execute a generator or sample rows.

Reads only the three assigned bundles, profiles, decisions and harness lifecycle.
All array calculations are finite-dimensional moment algebra, not synthetic data.
"""
import sys
sys.dont_write_bytecode = True
import ast
import hashlib
import json
import math
import re
from pathlib import Path
import numpy as np

W = Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16')
H = W / 'biomedical_research/virtual_cohort_system'
sys.path.insert(0, str(H))
from cohort_harness import lifecycle

OUT = Path(__file__).resolve().parent
NAMES = ['ENSANUT2018_E0_A04', 'ENSANUT2018_E1_A04', 'ENSANUT2018_E0_A05']
BANDS = [[25,39],[40,54],[55,69],[70,79]]

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def close(x, y):
    assert np.allclose(x, y, rtol=1e-11, atol=1e-12), (x,y)

def design(bands, sexes, rows):
    assert bands == BANDS and sexes == [0,1] and rows == 375
    mu = sum((lo+hi)/2 for lo,hi in bands)/4
    second = sum(((hi-lo+1)**2-1)/12+((lo+hi)/2)**2 for lo,hi in bands)/4
    return {'n_rows': 2*4*rows, 'rows_each_cell': rows, 'age_mean':mu,
            'age_second_moment':second, 'age_variance':second-mu**2,
            'female_mean':0.5, 'female_variance':0.25}

def affine_bounds(mean, coefficients, intervals):
    lo=hi=float(mean)
    for a,(l,u) in zip(coefficients,intervals):
        v=(a*l,a*u); lo+=min(v); hi+=max(v)
    return [lo,hi]

def projection(cov, indices):
    x=cov[np.ix_(indices,indices)]
    assert np.linalg.eigvalsh(x).min()>0
    return np.linalg.solve(x,cov[indices,4])

def unit_checks(items):
    v={x['id']:x['estimate'] for x in items}
    close(v['J_T1_glucose_mean_mg_dL_derived'],18*v['J_T1_glucose_mean_mmol_L'])
    close(v['J_T1_glucose_sd_mg_dL_derived'],18*v['J_T1_glucose_sd_mmol_L'])
    close(v['J_T1_hba1c_mean_pct_from_ifcc'],.09148*v['J_T1_hba1c_mean_ifcc']+2.152)
    close(v['J_T1_hba1c_sd_pct_from_ifcc'],.09148*v['J_T1_hba1c_sd_ifcc'])
    close(v['J_T1_female_proportion_derived'],1-v['J_T1_male_proportion_reported'])
    return v

reports={}
for name in NAMES:
    root=W/'evcMS'/name; b=root/'bundle'; c=b/'candidates/initial'
    receipt=lifecycle.verify_candidate(b,'candidates/initial')
    assert receipt['route']=='generator.py' and receipt['parent'] is None
    choice=read(root/'decision.json')
    assert choice['author_id']==name and choice['candidate']=='candidates/initial'
    assert choice['action']=='initial_final' and choice['reason']
    profile=read(root/'profile.json'); task=read(b/'task.json')
    assert task['n_rows']==3000 and task['mode']=='whole_cohort'
    assert profile['source_numeric_mode']=='reviewed_analytic_only'
    spec=read(c/'model_spec.json'); p=spec['parameters']
    evidence=read(c/'evidence.json'); admitted={}
    for entry in read(b/'registry.json')['artifacts']:
        source=b/entry['path']
        assert sha(source)==entry['sha256']
        for block in re.findall(r'```json\s*(.*?)```',source.read_text(encoding='utf-8'),re.S):
            obj=json.loads(block)
            if 'evidence' in obj: admitted[obj['evidence']['id']]=obj['evidence']
    assert all(admitted[item['id']]==item for item in evidence['items'])
    assert len(admitted)==len(evidence['items'])
    assert read(b/'input/evidence.json')==evidence
    v=unit_checks(evidence['items'])
    feedback=read(c/'whole_cohort_feedback.json')
    assert all(x['status']=='not_computable' and x['operator'] is None for x in feedback['checks'])
    assert {x['evidence_id'] for x in feedback['checks']}==set(admitted)
    semantics=read(c/'source_semantics_v1.json')
    assert {x['evidence_id'] for x in semantics['bindings']}==set(admitted)
    operations=read(b/'input/source_operations.json')['non_marginal_operations']
    uptake=read(c/'numerical_uptake.json')['records']
    assert {x['operation_id'] for x in operations}=={x['operation_id'] for x in uptake}
    assert len(operations)==len(uptake)
    tree=ast.parse((c/'generator.py').read_text(encoding='utf-8-sig'))
    functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='generate']
    assert len(functions)==1 and len(functions[0].args.args)==3
    report={'candidate_freeze_sha256':sha(c/'freeze.json'),
            'decision_sha256':sha(root/'decision.json'),
            'lifecycle_verify_candidate':'passed',
            'candidate_bindings':{f:sha(c/f) for f in ['generator.py','model_spec.json','evidence.json','mathematical_properties.md','numerical_uptake.json','analytic_calculation.py','analytic_results.json']},
            'admitted_evidence_items_exact':len(admitted),
            'all_target_as_source_checks_unavailable':True,
            'non_marginal_operation_count':len(operations),
            'uptake_use_counts':{s:sum(x['use']==s for x in uptake) for s in ['model_constraint','analytic_check','context_only','declined']}}
    if name.endswith('E0_A04'):
        d=p['design']; des=design(d['age_bands'],d['female_values'],d['rows_per_cell'])
        assert d['n_rows']==des['n_rows']
        laws={}; moments={}
        for variable in ['bmi','hba1c']:
            m,s=p[variable]['mean'],p[variable]['sd']
            k=(m/s)**2; theta=s*s/m
            assert k>0 and theta>0
            laws[variable]={'shape':k,'scale':theta,'support':'(0,infinity)'}
            moments[variable]={'mean':k*theta,'second':theta**2*k*(k+1),'variance':s*s}
            close(moments[variable]['mean'],m)
            close(moments[variable]['second'],m*m+s*s)
        g=p['glucose']; lo,hi=g['lower'],g['upper']; w=hi-lo
        q=(g['mean']-lo)/w; conc=q*(1-q)/(g['sd']/w)**2-1
        a,bb=q*conc,(1-q)*conc
        assert (lo,hi)==(0,126) and a>0 and bb>0
        gm=lo+w*a/(a+bb); gv=w*w*a*bb/((a+bb)**2*(a+bb+1))
        close(gm,g['mean']); close(gv,g['sd']**2)
        laws['glucose']={'alpha':a,'beta':bb,'support':'(0,126)'}
        moments['glucose']={'mean':gm,'variance':gv,'second':gm*gm+gv}
        assert uptake==[]
        report.update(design=des,law_parameters=laws,biomarker_moments=moments,
                      finite_moment_proof='Gamma positive shape/scale gives finite moments theta^r Gamma(k+r)/Gamma(k); glucose and demographics bounded. Product independence gives finite cross moments.',
                      projection_values={'Q1_age10':0.0,'Q2_bmi5':0.0,'Q3_bmi5':0.0},
                      qualification='Zero slopes follow from explicit independence; no dependence evidence or target validation.')
        author=read(c/'analytic_results.json')
        close([author['random_design_row_moments'][k]['mean'] for k in moments],[moments[k]['mean'] for k in moments])
        close([author['random_design_row_moments'][k]['second_raw_moment'] for k in moments],[moments[k]['second'] for k in moments])
    elif name.endswith('E1_A04'):
        d=p['design']; des=design(d['age_bands'],d['female_values'],d['rows_per_cell'])
        assert d['n_rows']==des['n_rows']
        m,f,sl=p['marginals'],p['factor'],p['source_projections']
        assert f['positive_probability']==.5
        vb,vg=m['bmi_sd']**2,m['glucose_sd']**2
        cross=f['bmi_loading']*f['glucose_loading']
        S=np.array([[vb,cross],[cross,vg]])
        assert np.linalg.eigvalsh(S).min()>0
        beta=np.linalg.solve(S,[vb*sl['bmi_age_sex'],vg*sl['glucose_age_sex']])
        j=p['source_contexts']['lifelines']; pp=p['source_contexts']['pani']
        error=m['hba1c_sd']**2-sl['age_full']**2*j['age_sd']**2-float(beta@S@beta)
        assert error>0
        shapes={}; supports={}
        for var,total in [('bmi',vb),('glucose',vg)]:
            low,high=p['residual_support'][var]; rv=total-f[var+'_loading']**2
            assert low<0<high and 0<rv<-low*high
            conc=-low*high/rv-1; a=-low*conc/(high-low); bb=high*conc/(high-low)
            close(low+(high-low)*a/(a+bb),0)
            close((high-low)**2*a*bb/((a+bb)**2*(a+bb+1)),rv)
            shapes[var]={'alpha':a,'beta':bb,'residual_variance':rv}
            supports[var]=[m[var+'_mean']-abs(f[var+'_loading'])+low,m[var+'_mean']+abs(f[var+'_loading'])+high]
        supports['hba1c_target']=affine_bounds(m['hba1c_mean'],[sl['age_full'],*beta,1],
            [[25-j['age_mean'],79-j['age_mean']],
             [x-m['bmi_mean'] for x in supports['bmi']],
             [x-m['glucose_mean'] for x in supports['glucose']],[-math.sqrt(3*error),math.sqrt(3*error)]])
        assert supports['bmi'][0]>0 and 0<supports['glucose'][0]<supports['glucose'][1]<126 and supports['hba1c_target'][0]>0
        close(sl['bmi_age_sex'],.09148*v['J_T2_bmi_slope_original'])
        close(sl['glucose_age_sex'],.09148*v['J_T2_glucose_slope_original']/18)
        close(sl['age_full'],v['P_NHANES_age_slope'])
        contexts={}
        prob=pp['age_geometric_probability']; assert 0<prob<1
        for ctx,am,av,fp in [('lifelines',j['age_mean'],j['age_sd']**2,j['female_probability']),('pani',pp['age_minimum']+(1-prob)/prob,(1-prob)/prob**2,pp['female_probability'])]:
            primitive=np.diag([av,fp*(1-fp),1.0,shapes['bmi']['residual_variance'],shapes['glucose']['residual_variance'],error])
            L=np.array([[1,0,0,0,0,0],[0,1,0,0,0,0],[0,0,f['bmi_loading'],1,0,0],[0,0,f['glucose_loading'],0,1,0],[sl['age_full'],0,beta[0]*f['bmi_loading']+beta[1]*f['glucose_loading'],beta[0],beta[1],1]])
            cov=L@primitive@L.T
            mean=[am,fp,m['bmi_mean'],m['glucose_mean'],m['hba1c_mean']+sl['age_full']*(am-j['age_mean'])]
            assert np.linalg.eigvalsh(cov).min()>0
            contexts[ctx]={'mean':mean,'covariance':cov.tolist(),'second_moments':(cov+np.outer(mean,mean)).tolist()}
        cj=np.array(contexts['lifelines']['covariance']); cp=np.array(contexts['pani']['covariance'])
        slopes=[projection(cj,[2,0,1])[0],projection(cj,[3,0,1])[0],projection(cp,[0,1,2,3])[0]]
        close(slopes,[sl['bmi_age_sex'],sl['glucose_age_sex'],sl['age_full']])
        assert sum(x['use']=='model_constraint' for x in uptake)==3 and sum(x['use']=='context_only' for x in uptake)==8
        report.update(design=des,beta_residual_shapes=shapes,supports=supports,joint_coefficients=beta.tolist(),
                      covariance_bmi_glucose=cross,hba1c_residual_variance=error,source_contexts=contexts,
                      qualified_source_slopes=dict(zip(['J_T2_bmi_slope_task_derived','J_T2_glucose_slope_task_derived','P_NHANES_age_slope'],slopes)),
                      finite_moment_proof='Target and Lifelines variables bounded; Pani reference age geometric with finite mean/variance and outcome affine in age plus bounded variables.',
                      qualification='Reference source laws follow the same conditional equations with explicitly substituted age/sex distributions. Survey weights, same Table2 population, and all transport remain assumed; eight age-band means are contextual.')
        author=read(c/'analytic_results.json')
        close(error,author['hba1c_residual_variance'])
        for ctx in contexts:
            close(contexts[ctx]['mean'],author['source_context_moments'][ctx]['mean'])
            close(contexts[ctx]['covariance'],author['source_context_moments'][ctx]['covariance'])
        close(slopes,[x['value'] for x in author['qualified_source_projections']])
    else:
        des=design(p['age_bands'],p['female_values'],p['rows_per_cell'])
        am,av=des['age_mean'],des['age_variance']; astd=math.sqrt(av)
        b,g,h=p['bmi_loadings'],p['glucose_loadings'],p['hba1c_loadings']
        rad=[1-sum(x*x for x in d.values()) for d in [b,g,h]]
        assert min(rad)>0
        rb,rg,rh=map(math.sqrt,rad)
        k=p['residual_beta_shape']; assert k>0
        L=np.array([[astd,0,0,0,0],[0,.5,0,0,0],
          [p['bmi_sd']*x for x in [b['age'],b['female'],rb,0,0]],
          [p['glucose_sd']*x for x in [g['age'],g['female'],g['bmi_factor'],rg,0]],
          [p['hba1c_sd']*x for x in [h['age'],h['female'],h['bmi_factor'],h['glucose_factor'],rh]]])
        cov=L@L.T; assert np.linalg.eigvalsh(cov).min()>0
        means=[am,.5,p['bmi_mean'],p['glucose_mean'],p['hba1c_mean']]
        intervals=[[(25-am)/astd,(79-am)/astd],[-1,1]]+[[-math.sqrt(2*k+1),math.sqrt(2*k+1)]]*3
        names=['age','female','bmi','glucose','hba1c']
        supports={n:affine_bounds(mu,row,intervals) for n,mu,row in zip(names,means,L)}
        assert supports['bmi'][0]>0 and supports['hba1c'][0]>0 and 0<supports['glucose'][0]<supports['glucose'][1]<126
        close(np.diag(cov)[2:],[p['bmi_sd']**2,p['glucose_sd']**2,p['hba1c_sd']**2])
        full=projection(cov,[0,1,2,3]); reduced=projection(cov,[0,1,2])
        q={'Q1_age10':10*full[0],'Q2_bmi5':5*reduced[2],'Q3_bmi5':5*full[2]}
        q['Q2_minus_Q3_bmi5']=q['Q2_bmi5']-q['Q3_bmi5']
        report.update(design=des,residual_variances=rad,loading_matrix=L.tolist(),means=means,
                      covariance=cov.tolist(),second_moments=(cov+np.outer(means,means)).tolist(),supports=supports,
                      projection_values=q,finite_moment_proof='Independent bounded standardized Beta factors and bounded demographic variables; affine map makes all moments finite.',
                      qualification='All dependence loadings and technical support limits explicitly assumed. E0 empty uptake is correct; algebra is target-law mathematics, not clinical target results.')
        author=read(c/'analytic_results.json')
        close(cov,author['raw_covariance_matrix'])
        for n in supports: close(supports[n],author['closed_support_bounds'][n])
        for key in q: close(q[key],author['substitution_formula_values'][key])
    # Reverify after every read/calculation, binding the unchanged frozen bytes.
    lifecycle.verify_candidate(root/'bundle','candidates/initial')
    assert report['candidate_freeze_sha256']==sha(c/'freeze.json')
    assert report['decision_sha256']==sha(root/'decision.json')
    report['independent_calculation_passed']=True
    report['target_results_used']=False
    reports[name]=report

result={'reviewer_id':'/root/main_review_g7','method':'Deterministic algebra; no sampling, quadrature, generator execution/import, or target reference access.',
        'script_sha256':sha(Path(__file__)), 'cases':reports}
with (OUT/'independent_algebra_results.json').open('x',encoding='utf-8') as stream:
    json.dump(result,stream,indent=2,allow_nan=False); stream.write('\n')
print(json.dumps({n:{'verified':r['lifecycle_verify_candidate'],'calculation_passed':r['independent_calculation_passed'],'freeze':r['candidate_freeze_sha256'],'decision':r['decision_sha256']} for n,r in reports.items()},indent=2))
