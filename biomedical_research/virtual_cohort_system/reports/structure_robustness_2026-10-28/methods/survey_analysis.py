"""Prespecified survey analyses. Importing reads no target data."""
from __future__ import annotations
import numpy as np
from scipy.stats import t

def fit_domain(X,y,weights,strata,psu,domain):
    X=np.asarray(X,dtype=float); y=np.asarray(y,dtype=float)
    weights=np.asarray(weights,dtype=float); domain=np.asarray(domain,dtype=bool)
    strata=np.asarray(strata); psu=np.asarray(psu)
    assert domain.any() and len(X)==len(y)==len(weights)==len(domain)
    assert np.isfinite(weights).all() and (weights>0).all()
    assert np.isfinite(X[domain]).all() and np.isfinite(y[domain]).all()
    w=weights/weights[domain].mean(); xd=X[domain]; yd=y[domain]; wd=w[domain]
    if np.linalg.matrix_rank(xd)!=xd.shape[1]: raise ValueError('Rank-deficient domain design')
    bread=np.linalg.inv(xd.T@(wd[:,None]*xd)); beta=bread@(xd.T@(wd*yd))
    score=np.zeros_like(X); score[domain]=xd*(wd*(yd-xd@beta))[:,None]
    meat=np.zeros((X.shape[1],X.shape[1])); full_psus=0
    for h in np.unique(strata):
        jvals=np.unique(psu[strata==h]); m=len(jvals); full_psus+=m
        if m<2: raise ValueError('Singleton full-design stratum')
        totals=np.array([score[(strata==h)&(psu==j)].sum(axis=0) for j in jvals])
        centered=totals-totals.mean(axis=0); meat+=(m/(m-1))*(centered.T@centered)
    covariance=bread@meat@bread; covariance=(covariance+covariance.T)/2
    domain_pairs=set(zip(strata[domain].tolist(),psu[domain].tolist()))
    domain_strata=len(set(strata[domain].tolist())); df=len(domain_pairs)-domain_strata
    if df<=0: raise ValueError('No occupied-domain design degrees of freedom')
    return {'beta':beta,'covariance':covariance,'df':df,'n':int(domain.sum()),'full_design_PSUs':full_psus,'full_design_strata':len(np.unique(strata)),'domain_PSUs':len(domain_pairs),'domain_strata':domain_strata}

def point_sign(x): return 'positive' if x>0 else 'negative' if x<0 else 'exactly_zero'

def interval(fit,contrast,scale):
    c=np.asarray(contrast,dtype=float); estimate=float(c@fit['beta'])
    variance=float(c@fit['covariance']@c)
    if variance < -1e-10: raise ValueError('Negative contrast variance')
    se=float(np.sqrt(max(variance,0))); delta=float(t.ppf(.975,fit['df'])*se)
    lo=estimate-delta; hi=estimate+delta
    out={'estimate':estimate,'se':se,'ci_low':lo,'ci_high':hi,'scale':scale,'point_direction':point_sign(estimate),'ci_direction':'positive' if lo>0 else 'negative' if hi<0 else 'interval_includes_zero','df':fit['df'],'n':fit['n']}
    if scale=='log_mg_dl': out.update(exp_estimate=float(np.exp(estimate)),exp_ci_low=float(np.exp(lo)),exp_ci_high=float(np.exp(hi)))
    return out

def evaluate(full,values,reference=True):
    domain=full.eligible.eq(1).to_numpy()
    B=(full.BMXBMI.to_numpy()-25)/5; A=(full.RIDAGEYR.to_numpy()-50)/10
    F=full.RIAGENDR.eq(2).astype(float).to_numpy()
    base=np.column_stack([np.ones(len(full)),B,A,F]); curve=np.column_stack([base,B*B])
    ordered=full.loc[domain,'record_id'].map(values)
    if ordered.isna().any() or not np.isfinite(ordered).all() or not ordered.gt(0).all(): raise ValueError('Missing, nonfinite or nonpositive target')
    raw=np.full(len(full),np.nan); raw[domain]=ordered.to_numpy()
    log=np.full(len(full),np.nan); log[domain]=np.log(ordered.to_numpy())
    kwargs=dict(weights=full.WTSAF2YR,strata=full.SDMVSTRA,psu=full.SDMVPSU,domain=domain)
    models={'adjusted':fit_domain(base,log,**kwargs),'curve':fit_domain(curve,log,**kwargs),'raw_curve':fit_domain(curve,raw,**kwargs),'interaction':fit_domain(np.column_stack([base,B*F]),log,**kwargs)}
    definitions={
      'adjusted_age_per10':('adjusted',[0,0,1,0],'log_mg_dl'),
      'bmi_curvature_second_difference':('curve',[0,0,0,0,2],'log_mg_dl'),
      'raw_bmi_curvature_second_difference':('raw_curve',[0,0,0,0,2],'mg_dl'),
      'adjusted_bmi_per5':('adjusted',[0,1,0,0],'log_mg_dl'),
      'adjusted_female_vs_male':('adjusted',[0,0,0,1],'log_mg_dl'),
      'bmi_sex_interaction':('interaction',[0,0,0,0,1],'log_mg_dl')}
    results={name:interval(models[model],c,scale) for name,(model,c,scale) in definitions.items()}
    if not reference:
        # Simulation draws get point estimates only: their survey CI is not model uncertainty.
        results={name:{k:v for k,v in stats.items() if k in ['estimate','scale','point_direction','n','exp_estimate']} for name,stats in results.items()}
    return results

def validate_invented():
    strata=np.repeat([1,2],4); psu=np.tile([1,1,2,2],2)
    weights=np.array([1,2,3,4,2,3,1,2.]); y=np.array([1,3,2,6,5,4,7,9.])
    X=np.ones((8,1)); domain=np.array([1,1,0,0,1,1,1,1],bool)
    r=fit_domain(X,y,weights,strata,psu,domain)
    mean=np.sum(weights[domain]*y[domain])/weights[domain].sum()
    z=np.where(domain,weights*(y-mean),0); totals=np.array([z[:2].sum(),z[2:4].sum(),z[4:6].sum(),z[6:].sum()])
    expected=((totals[0]-totals[1])**2+(totals[2]-totals[3])**2)/weights[domain].sum()**2
    assert np.allclose(r['beta'],[mean]) and np.allclose(r['covariance'],[[expected]])
    assert r['df']==1 and r['full_design_PSUs']==4
    scaled=fit_domain(X,y,weights*137,strata,psu,domain)
    assert np.allclose(r['beta'],scaled['beta']) and np.allclose(r['covariance'],scaled['covariance'])
    import statsmodels.api as sm
    x=np.column_stack([np.ones(8),np.arange(8,dtype=float)])
    fit=fit_domain(x,y,weights,strata,psu,np.ones(8,bool))
    assert np.allclose(fit['beta'],sm.WLS(y,x,weights=weights).fit().params)
    assert np.linalg.eigvalsh(fit['covariance']).min()>-1e-10
    perm=np.array([5,1,7,2,6,3,0,4]); permuted=fit_domain(x[perm],y[perm],weights[perm],strata[perm],psu[perm],np.ones(8,bool))
    assert np.allclose(fit['covariance'],permuted['covariance'])
    raw=interval(fit,[0,1],'mg_dl'); log=interval(fit,[0,1],'log_mg_dl')
    assert 'exp_estimate' not in raw and 'exp_estimate' in log
    return {'status':'passed','scope':'invented_fixtures_only','checks':['analytic variance with empty domain PSU','occupied-domain df','global weight scaling','statsmodels WLS point estimates','PSD covariance','row permutation','raw-scale interval has no exponentiation'],'target_outcomes_analyzed':False}

if __name__=='__main__':
    import json
    print(json.dumps(validate_invented()))
