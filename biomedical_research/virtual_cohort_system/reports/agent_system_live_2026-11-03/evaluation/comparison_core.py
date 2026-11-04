"""Analysis only. Callers enforce closure and frozen artifact gates before loading data."""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy import stats
from generated_diagnostics import analyze_generated, REQUESTS


def analyze_reference(frame, request):
    result=analyze_generated(frame,request)
    result.update(reference_read=True,mode='exposed_development_reference',
        interval_meaning='Community-cluster CR1-t 95% selected-sample uncertainty; not known population truth; no survey weights.')
    if result['status']!='complete':return result
    predictors=REQUESTS[request]['predictors']
    x=np.column_stack([np.ones(len(frame)),frame[predictors].to_numpy(float)])
    y=frame.hba1c.to_numpy(float)
    beta=np.linalg.lstsq(x,y,rcond=None)[0]
    codes=frame.survey_commid.to_numpy(float)
    valid=bool(np.isfinite(codes).all() and (codes>0).all() and (codes==np.floor(codes)).all())
    groups=np.unique(codes) if valid else np.array([])
    g=len(groups);n,k=x.shape
    if valid and g>=20:
        resid=y-x@beta
        scores=np.vstack([(x[codes==c]*resid[codes==c,None]).sum(axis=0) for c in groups])
        pinv=np.linalg.pinv(x);bread=pinv@pinv.T
        cov=g/(g-1)*(n-1)/(n-k)*bread@(scores.T@scores)@bread
        variance=np.diag(cov)
        valid=bool(np.isfinite(variance).all() and (variance>=0).all())
    else:valid=False
    result['cluster_count']=g
    for i,term in enumerate(['const']+predictors):
        row=result['coefficients'][term]
        se=float(np.sqrt(variance[i])) if valid else None
        half=float(stats.t.ppf(.975,g-1)*se) if valid else None
        lo=float(beta[i]-half) if valid else None
        hi=float(beta[i]+half) if valid else None
        row.update(standard_error=se,lower=lo,upper=hi,interval_status='available' if valid else 'unavailable',
                   interval_direction=('positive' if lo>0 else 'negative' if hi<0 else 'inconclusive') if valid else 'unavailable',
                   degrees_of_freedom=g-1 if valid else None,method='CR1_t')
    return result


def qr_recompute(frame,request,*,reference=False):
    """Independent QR score formulation, separate from the production pseudoinverse path."""
    predictors=REQUESTS[request]['predictors']
    x=np.column_stack([np.ones(len(frame)),frame[predictors].to_numpy(float)])
    y=frame.hba1c.to_numpy(float)
    q,r=np.linalg.qr(x,mode='reduced');ri=np.linalg.inv(r)
    beta=np.linalg.solve(r,q.T@y);resid=y-x@beta
    n,k=x.shape
    if reference:
        ids=frame.survey_commid.to_numpy()
        codes,inv=np.unique(ids,return_inverse=True);g=len(codes)
        score=np.zeros((g,k));np.add.at(score,inv,q*resid[:,None])
        cov=g/(g-1)*(n-1)/(n-k)*ri@(score.T@score)@ri.T
        df=g-1
    else:
        leverage=(q*q).sum(axis=1)
        cov=ri@(q.T@((resid/(1-leverage))[:,None]**2*q))@ri.T
        df=n-k
    se=np.sqrt(np.diag(cov));half=stats.t.ppf(.975,df)*se
    return {term:{'value':float(beta[i]),'standard_error':float(se[i]),
                  'lower':float(beta[i]-half[i]),'upper':float(beta[i]+half[i])}
            for i,term in enumerate(['const']+predictors)}


def independently_check(frame,analysis,request,*,reference=False):
    if analysis['status']!='complete':
        return {'status':'not_computed','reason':analysis['status']}
    qr=qr_recompute(frame,request,reference=reference)
    differences=[]
    for term,values in qr.items():
        for key,value in values.items():
            observed=analysis['coefficients'][term][key]
            np.testing.assert_allclose(observed,value,rtol=1e-8,atol=1e-10)
            differences.append(abs(observed-value))
    for variable,row in analysis['marginal'].items():
        x=frame[variable].to_numpy(float)
        expected={'mean':float(np.mean(x)),'sd':float(np.std(x,ddof=1)),
                  **dict(zip(['q10','median','q90'],np.quantile(x,[.1,.5,.9],method='linear')))}
        for key,value in expected.items():np.testing.assert_allclose(row[key],value,rtol=1e-12,atol=1e-12)
    for relation,row in analysis['relationships'].items():
        variable=relation.removesuffix('_hba1c')
        array=frame[[variable,'hba1c']].to_numpy(float)
        if row['pearson'] is None:continue
        pearson=np.corrcoef(array,rowvar=False)[0,1]
        ranked=np.column_stack([stats.rankdata(array[:,i]) for i in range(2)])
        spearman=np.corrcoef(ranked,rowvar=False)[0,1]
        np.testing.assert_allclose([row['pearson'],row['spearman']],[pearson,spearman],rtol=1e-12,atol=1e-12)
    return {'status':'PASS','method':'independent QR coefficients/covariance and NumPy marginal/rank checks',
            'maximum_coefficient_interval_absolute_difference':max(differences),
            'coefficient_terms':len(qr),'marginals':len(analysis['marginal']),
            'relationship_pairs':len(analysis['relationships'])}


def comparison(reference,generated):
    """Transparent descriptive comparison; no invented equivalence or success score."""
    if reference['status']!='complete' or generated['status']!='complete':
        return {'status':'unavailable','reference_status':reference['status'],'generated_status':generated['status']}
    terms={}
    for term,gen in generated['coefficients'].items():
        ref=reference['coefficients'][term]
        terms[term]={'reference':ref['value'],'generated':gen['value'],
                     'difference':gen['value']-ref['value'],'same_point_sign':gen['sign']==ref['sign'],
                     'reference_interval_direction':ref['interval_direction'],
                     'generated_conditional_interval_direction':gen['interval_direction'],
                     'reference_ci':[ref['lower'],ref['upper']],
                     'generated_conditional_ci':[gen['lower'],gen['upper']],
                     'interpretation':'Descriptive scale/direction comparison; neither overlap nor membership establishes equivalence.'}
    marginal={v:{stat:{'reference':reference['marginal'][v][stat],
                       'generated':generated['marginal'][v][stat],
                       'difference':generated['marginal'][v][stat]-reference['marginal'][v][stat]}
                 for stat in ('mean','sd','q10','median','q90')}
              for v in generated['marginal']}
    relations={rel:{stat:{'reference':reference['relationships'][rel][stat],
                         'generated':generated['relationships'][rel][stat]}
                    for stat in ('pearson','spearman')}
               for rel in generated['relationships']}
    return {'status':'complete','coefficients':terms,'marginals':marginal,'relationships':relations,
            'global_score':None,'new_confirmation':False}
