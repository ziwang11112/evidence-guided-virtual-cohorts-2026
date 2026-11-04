"""Aggregate comparison and generated-only recomputation; no patient-data adapter."""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy import stats
from generated_diagnostics import REQUESTS


def qr_recompute(frame,request):
    """Independent QR score formulation, separate from the production pseudoinverse path."""
    predictors=REQUESTS[request]['predictors']
    x=np.column_stack([np.ones(len(frame)),frame[predictors].to_numpy(float)])
    y=frame.hba1c.to_numpy(float)
    q,r=np.linalg.qr(x,mode='reduced');ri=np.linalg.inv(r)
    beta=np.linalg.solve(r,q.T@y);resid=y-x@beta
    n,k=x.shape
    leverage=(q*q).sum(axis=1)
    valid=bool(np.all(1-leverage > np.finfo(float).eps))
    if valid:
        cov=ri@(q.T@((resid/(1-leverage))[:,None]**2*q))@ri.T
        variance=np.diag(cov)
        valid=bool(np.isfinite(variance).all() and (variance>=0).all())
    if valid:
        se=np.sqrt(variance);half=stats.t.ppf(.975,n-k)*se
    return {term:{'value':float(beta[i]),'standard_error':float(se[i]),
                  'lower':float(beta[i]-half[i]),'upper':float(beta[i]+half[i])}
            if valid else {'value':float(beta[i]),'standard_error':None,'lower':None,'upper':None}
            for i,term in enumerate(['const']+predictors)}


def independently_check(frame,analysis,request):
    if analysis['status']!='complete':
        return {'status':'not_computed','reason':analysis['status']}
    qr=qr_recompute(frame,request)
    differences=[]
    unavailable=[]
    for term,values in qr.items():
        for key,value in values.items():
            observed=analysis['coefficients'][term][key]
            if observed is None or value is None:
                if key == 'value':
                    raise AssertionError('Unavailable coefficient value in complete analysis')
                unavailable.append({'term':term,'quantity':key,
                    'production_available':observed is not None,'qr_available':value is not None})
                continue
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
            'unavailable_interval_checks':unavailable,
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
                         'generated':generated['relationships'][rel][stat],
                         'difference':(generated['relationships'][rel][stat]-reference['relationships'][rel][stat])
                            if generated['relationships'][rel][stat] is not None and reference['relationships'][rel][stat] is not None else None}
                    for stat in ('pearson','spearman')}
               for rel in generated['relationships']}
    return {'status':'complete','coefficients':terms,'marginals':marginal,'relationships':relations,
            'global_score':None,'new_confirmation':False}
