"""Focused preregistration checks for new adapter and analysis meanings."""
import json
import numpy as np
import pandas as pd
from pilot import ROOT,PREP,SEEDS,LIMITS,task,isolated,read,write,sha,prompt,validate_artifact,client,CONFIG
from analyzer import evaluate,source_checks,identified,label_checks,ESTIMANDS
from verify_analysis import recompute

def exact_frame(cov,names):
    # Trusted deterministic matrix fixture with precisely the requested sample covariance.
    rng=np.random.default_rng(811); a=rng.normal(size=(40,len(names)));a-=a.mean(0)
    q=np.linalg.qr(a)[0];v=q@np.linalg.cholesky(cov).T*np.sqrt(len(a)-1)
    return pd.DataFrame({'person_id':np.arange(len(a)),**dict(zip(names,v.T))})

def main():
    checks=[]
    def check(name,ok):
        checks.append({'name':name,'passed':bool(ok)})
        if not ok: raise AssertionError(name)
    s=np.array([[1,.5,.6],[.5,1,.6],[.6,.6,1]])
    a=exact_frame(s,['X','Y','Z']);r=evaluate(a,'adjusted')
    check('partial_OLS_removes_covariate',abs(r['analyses']['partial_xy_given_z']-.21875)<1e-12)
    check('secondary_slope_not_standardized_beta_substitution',abs(r['analyses']['slope_x_on_z']-.6)<1e-12)
    check('adjusted_source_checks_exact_fixture',all(x['within_tolerance'] for x in source_checks(r,'adjusted','combined')))
    b=np.array([[4,3.2],[3.2,4]]);e=np.array([[1,-.6],[-.6,1]])
    c=np.block([[b+e,b],[b,b+e]])
    f=exact_frame(c,['X_visit1','Y_visit1','X_visit2','Y_visit2']);r2=evaluate(f,'longitudinal')
    check('change_corr_differs_from_same_visit',abs(r2['analyses']['change_correlation']+.6)<1e-12 and abs(r2['analyses']['same_visit_correlation']-.52)<1e-12)
    check('cross_visit_equals_stable_component_contribution',abs(r2['analyses']['cross_visit_correlation']-.64)<1e-12)
    check('within_variance_half_change_variance',np.allclose(r2['within_variances'],[1,1]))
    check('between_variance_is_cross_visit_covariance',np.allclose(r2['between_variances'],[4,4]))
    check('longitudinal_source_checks_exact_fixture',all(x['within_tolerance'] for x in source_checks(r2,'longitudinal','combined')))
    for family,frame,result in [('adjusted',a,r),('longitudinal',f,r2)]:
        other=recompute(frame,family)
        check('independent_formula_'+family,all(abs(other[k]-v)<1e-12 for k,v in result['analyses'].items()))
        for condition in ['none','anchor_only','bridge_only','combined']:
            check('primary_identification_'+family+'_'+condition,identified(family,condition,ESTIMANDS[family][0])==(condition=='combined'))
    broken=a.copy();broken['Z']=0
    try:evaluate(broken,'adjusted');ok=False
    except ValueError:ok=True
    check('degenerate_covariate_fails',ok)
    missing=a.copy();missing.loc[1,'Y']=np.nan
    try:evaluate(missing,'adjusted');ok=False
    except ValueError:ok=True
    check('nan_fails',ok)
    slot=read(PREP/'PLAN.json')['slots'][0];p=prompt(read(PREP/slot['payload']),slot['family'])
    check('payload_preserved',read(ROOT/'inputs'/slot['payload'])==read(PREP/slot['payload']))
    check('no_host_oracle_in_prompt','HOST_ONLY' not in p and 'REFERENCE' not in p and 'reference_value' not in p)
    req=client.make_request(CONFIG,p)[1]
    check('fresh_standalone_request',not any(k in req for k in ('previous_response_id','conversation','tools')) and req['store'] is False)
    check('bounded_output',req['max_output_tokens']==16384)
    # An actually launched namespace fixture; not an experimental author/table.
    qa=ROOT/'qa';qa.mkdir(exist_ok=False);cand=qa/'candidate';cand.mkdir()
    t=task('adjusted');t['n_rows']=12
    code='''import numpy as np\nimport pandas as pd\nimport os\nfrom pathlib import Path\ndef generate(observed,spec,seed):\n    assert not Path('/mnt').exists() and not Path('/home').exists()\n    assert 'OPENAI_API_KEY' not in os.environ\n    n=spec['task']['n_rows']\n    a=np.random.default_rng(seed).normal(size=(n,3))\n    return pd.DataFrame({'person_id':np.arange(n),'X':a[:,0],'Y':a[:,1],'Z':a[:,2]})\n'''
    (cand/'generator.py').write_text(code,encoding='utf-8');write(cand/'model_spec.json',{'task':t,'model':{}})
    r=isolated(cand,t,qa/'sandbox_run',881)
    check('actual_bubblewrap_execution',r['status']=='success' and r['generator_executed'] is True)
    write(ROOT/'PREFLIGHT.json',{'all_passed':all(c['passed'] for c in checks),'checks':checks,'count':len(checks),
            'experimental_calls':0,'qa_tables':1,'qa_table_not_an_experimental_result':True})
    print(json.dumps({'all_passed':True,'checks':len(checks),'actual_sandbox_execution':True}))

if __name__=='__main__':main()
