"""Prespecified survey analyses. Importing reads no target data."""
from __future__ import annotations
import numpy as np
from scipy.stats import t

class NonestimableDomain(ValueError):
    """A prespecified analysis domain cannot support its declared model."""

def fit_domain(X,y,weights,strata,psu,domain):
    X=np.asarray(X,dtype=float); y=np.asarray(y,dtype=float)
    weights=np.asarray(weights,dtype=float); domain=np.asarray(domain,dtype=bool)
    strata=np.asarray(strata); psu=np.asarray(psu)
    assert len(X)==len(y)==len(weights)==len(domain)
    assert np.isfinite(weights).all() and (weights>0).all()
    if not domain.any(): raise NonestimableDomain('Empty analysis domain')
    assert np.isfinite(X[domain]).all() and np.isfinite(y[domain]).all()
    w=weights/weights[domain].mean(); xd=X[domain]; yd=y[domain]; wd=w[domain]
    if np.linalg.matrix_rank(xd)!=xd.shape[1]: raise NonestimableDomain('Rank-deficient domain design')
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
    if df<=0: raise NonestimableDomain('No occupied-domain design degrees of freedom')
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
    base=np.column_stack([np.ones(len(full)),A,B,F])
    ordered=full.loc[domain,'record_id'].map(values)
    if ordered.isna().any() or not np.isfinite(ordered).all() or not ordered.gt(0).all(): raise ValueError('Missing, nonfinite or nonpositive target')
    raw=np.full(len(full),np.nan); raw[domain]=ordered.to_numpy()
    log=np.full(len(full),np.nan); log[domain]=np.log(ordered.to_numpy())
    kwargs=dict(weights=full.WTSAF2YR,strata=full.SDMVSTRA,psu=full.SDMVPSU,domain=domain)
    # A model rank failure must not hide a full-design error.
    strata=np.asarray(kwargs['strata']); psu=np.asarray(kwargs['psu'])
    for h in np.unique(strata):
        if len(np.unique(psu[strata==h]))<2: raise ValueError('Singleton full-design stratum')
    age_curve=np.column_stack([base,A*A]); bmi_curve=np.column_stack([base,B*B])
    # A failed model retains its declared endpoints; unrelated models still run.
    # Invalid weights, nonfinite analysis inputs and invalid full designs remain errors.
    models={}; model_failures={}
    for model,(X,yy) in {'adjusted':(base,log),'age_curve':(age_curve,log),'bmi_curve':(bmi_curve,log),'raw_age_curve':(age_curve,raw),'raw_bmi_curve':(bmi_curve,raw)}.items():
        try: models[model]=fit_domain(X,yy,**kwargs)
        except NonestimableDomain as exc: model_failures[model]=str(exc)
    definitions={
      'adjusted_age_per10':('adjusted',[0,1,0,0],'log_mg_dl'),
      'adjusted_bmi_per5':('adjusted',[0,0,1,0],'log_mg_dl'),
      'age_curvature_second_difference':('age_curve',[0,0,0,0,2],'log_mg_dl'),
      'bmi_curvature_second_difference':('bmi_curve',[0,0,0,0,2],'log_mg_dl'),
      'raw_age_curvature_second_difference':('raw_age_curve',[0,0,0,0,2],'mg_dl'),
      'raw_bmi_curvature_second_difference':('raw_bmi_curve',[0,0,0,0,2],'mg_dl'),
      'adjusted_female_vs_male':('adjusted',[0,0,0,1],'log_mg_dl')}
    results={name:({'status':'nonestimable','reason':model_failures[model],'n':int(domain.sum()),'scale':scale}
                   if model in model_failures else interval(models[model],c,scale))
             for name,(model,c,scale) in definitions.items()}
    bmi=full.BMXBMI.to_numpy(); age=full.RIDAGEYR.to_numpy(); sex=full.RIAGENDR.to_numpy()
    bmi_masks=[bmi<25,(bmi>=25)&(bmi<30),bmi>=30]
    group_X=np.column_stack(bmi_masks).astype(float)
    for lo,hi in [(40,60),(60,80)]:
        for sx in [1,2]:
            age_sex=domain&(age>=lo)&(age<hi)&(sex==sx)
            prefix=f'age{lo}_{hi-1}_sex{sx}'
            for gi,mask in enumerate(bmi_masks):
                subdomain=age_sex&mask
                for label,yy,scale in [('arithmetic',raw,'mg_dl'),('geometric',log,'log_mg_dl'),('tg_ge150',np.where(domain,raw>=150,np.nan),'proportion')]:
                    key=f'cell_{prefix}_bmi{gi}_{label}'
                    try:
                        fit=fit_domain(np.ones((len(full),1)),yy,**(kwargs|{'domain':subdomain}))
                        stats=interval(fit,[1],scale)
                        stats.update(domain_PSUs=fit['domain_PSUs'],domain_strata=fit['domain_strata'],sparse_n_lt30=fit['n']<30,sparse_df_lt8=fit['df']<8)
                        if label=='geometric':
                            stats.update(mean_mg_dl=stats['exp_estimate'],mean_ci_low=stats['exp_ci_low'],mean_ci_high=stats['exp_ci_high'])
                        if label=='tg_ge150': stats.update(wald_outside_probability_bounds=stats['ci_low']<0 or stats['ci_high']>1,degenerate_standard_error=stats['se']==0)
                        results[key]=stats
                    except NonestimableDomain as exc: results[key]={'status':'nonestimable','reason':str(exc),'n':int(subdomain.sum()),'scale':scale}
            for label,yy,scale in [('arithmetic',raw,'mg_dl'),('geometric',log,'log_mg_dl')]:
                try:
                    fit=fit_domain(group_X,yy,**(kwargs|{'domain':age_sex}))
                    for name,c in [('middle_minus_low',[-1,1,0]),('high_minus_middle',[0,-1,1]),('high_minus_low',[-1,0,1])]:
                        results[f'ordered_{prefix}_{label}_{name}']=interval(fit,c,scale)
                except NonestimableDomain as exc:
                    for name in ['middle_minus_low','high_minus_middle','high_minus_low']: results[f'ordered_{prefix}_{label}_{name}']={'status':'nonestimable','reason':str(exc),'n':int(age_sex.sum()),'scale':scale}
    if not reference:
        # Simulation draws get point estimates only: their survey CI is not model uncertainty.
        results={name:{k:v for k,v in stats.items() if k in ['estimate','scale','point_direction','n','exp_estimate','mean_mg_dl','status','reason']} for name,stats in results.items()}
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
    # Paired group differences use joint covariance, validated against direct influence sums.
    group=np.array([0,1,0,1,0,1,0,1]); XX=np.column_stack([group==0,group==1]).astype(float)
    fit=fit_domain(XX,y,weights,strata,psu,np.ones(8,bool)); c=np.array([-1.,1.])
    group_means=np.array([np.average(y[group==g],weights=weights[group==g]) for g in [0,1]])
    influence=np.array([c[g]*weights[i]*(y[i]-group_means[g])/weights[group==g].sum() for i,g in enumerate(group)])
    totals=np.array([influence[:2].sum(),influence[2:4].sum(),influence[4:6].sum(),influence[6:].sum()])
    expected=(totals[0]-totals[1])**2+(totals[2]-totals[3])**2
    assert np.allclose(c@fit['beta'],group_means[1]-group_means[0]) and np.allclose(c@fit['covariance']@c,expected)
    return {'status':'passed','scope':'invented_fixtures_only','checks':['analytic variance with empty domain PSU','occupied-domain df','global weight scaling','statsmodels WLS point estimates','PSD covariance','row permutation','raw-scale interval has no exponentiation'],'target_outcomes_analyzed':False}

if __name__=='__main__':
    import json
    print(json.dumps(validate_invented()))
