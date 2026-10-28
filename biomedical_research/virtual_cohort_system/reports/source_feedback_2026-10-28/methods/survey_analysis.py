"""Locked survey estimators; importing this module reads no target data."""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.stats import t

def fit_domain(X, y, weights, strata, psu, domain):
    X=np.asarray(X,dtype=float); y=np.asarray(y,dtype=float)
    weights=np.asarray(weights,dtype=float); domain=np.asarray(domain,dtype=bool)
    strata=np.asarray(strata); psu=np.asarray(psu)
    assert domain.any() and len(X)==len(y)==len(weights)==len(domain)
    assert np.isfinite(weights).all() and (weights>0).all()
    assert np.isfinite(X[domain]).all() and np.isfinite(y[domain]).all()
    w=weights/weights[domain].mean()
    xd=X[domain]; yd=y[domain]; wd=w[domain]
    if np.linalg.matrix_rank(xd)!=xd.shape[1]:
        raise ValueError("Rank-deficient domain design")
    bread=np.linalg.inv(xd.T@(wd[:,None]*xd))
    beta=bread@(xd.T@(wd*yd))
    score=np.zeros_like(X)
    score[domain]=xd*(wd*(yd-xd@beta))[:,None]
    meat=np.zeros((X.shape[1],X.shape[1]))
    full_psus=0
    for h in np.unique(strata):
        jvals=np.unique(psu[strata==h]); m=len(jvals); full_psus+=m
        if m<2:
            raise ValueError("Singleton full-design stratum")
        totals=np.array([score[(strata==h)&(psu==j)].sum(axis=0) for j in jvals])
        centered=totals-totals.mean(axis=0)
        meat+=(m/(m-1))*(centered.T@centered)
    covariance=bread@meat@bread
    covariance=(covariance+covariance.T)/2
    domain_pairs=set(zip(strata[domain].tolist(),psu[domain].tolist()))
    domain_strata=len(set(strata[domain].tolist()))
    df=len(domain_pairs)-domain_strata
    if df<=0:
        raise ValueError("No domain design degrees of freedom")
    return {"beta":beta,"covariance":covariance,"df":df,"n":int(domain.sum()),"full_design_PSUs":full_psus,"full_design_strata":len(np.unique(strata)),"domain_PSUs":len(domain_pairs),"domain_strata":domain_strata}

def interval(fit, contrast):
    c=np.asarray(contrast,dtype=float)
    estimate=float(c@fit["beta"])
    variance=float(c@fit["covariance"]@c)
    if variance < -1e-10:
        raise ValueError("Invalid negative contrast variance")
    se=float(np.sqrt(max(variance,0)))
    delta=float(t.ppf(.975,fit["df"])*se)
    lo=estimate-delta; hi=estimate+delta
    return {"log_estimate":estimate,"se":se,"log_ci_low":lo,"log_ci_high":hi,"ratio":float(np.exp(estimate)),"ratio_ci_low":float(np.exp(lo)),"ratio_ci_high":float(np.exp(hi)),"direction":"positive" if lo>0 else "negative" if hi<0 else "interval_includes_zero","df":fit["df"],"n":fit["n"]}

def evaluate(full, values):
    """values is one positive TG value per eligible record_id; never a fitting input."""
    domain=full.eligible.eq(1).to_numpy()
    B=(full.BMXBMI.to_numpy()-25)/5
    A=(full.RIDAGEYR.to_numpy()-50)/10
    F=full.RIAGENDR.eq(2).astype(float).to_numpy()
    base=np.column_stack([np.ones(len(full)),B,A,F])
    y=np.full(len(full),np.nan)
    ordered=full.loc[domain,"record_id"].map(values)
    if ordered.isna().any() or not np.isfinite(ordered).all() or not ordered.gt(0).all():
        raise ValueError("Missing, nonfinite or nonpositive target output")
    y[domain]=np.log(ordered.to_numpy())
    kwargs=dict(y=y,weights=full.WTSAF2YR,strata=full.SDMVSTRA,psu=full.SDMVPSU,domain=domain)
    adjusted=fit_domain(base,**kwargs)
    curve=fit_domain(np.column_stack([base,B*B]),**kwargs)
    interaction=fit_domain(np.column_stack([base,B*F]),**kwargs)
    return {
      "adjusted_bmi_per5":interval(adjusted,[0,1,0,0]),
      "adjusted_age_per10":interval(adjusted,[0,0,1,0]),
      "adjusted_female_vs_male":interval(adjusted,[0,0,0,1]),
      "bmi_curvature_second_difference":interval(curve,[0,0,0,0,2]),
      "bmi_sex_interaction":interval(interaction,[0,0,0,0,1])
    }

def validate_invented():
    """Analytic fixture includes a zero-contribution domain-excluded PSU."""
    strata=np.repeat([1,2],4); psu=np.tile([1,1,2,2],2)
    weights=np.array([1,2,3,4,2,3,1,2.],dtype=float)
    y=np.array([1,3,2,6,5,4,7,9.],dtype=float)
    X=np.ones((8,1)); domain=np.array([1,1,0,0,1,1,1,1],dtype=bool)
    result=fit_domain(X,y,weights,strata,psu,domain)
    mean=np.sum(weights[domain]*y[domain])/weights[domain].sum()
    z=np.where(domain,weights*(y-mean),0)
    totals=np.array([z[:2].sum(),z[2:4].sum(),z[4:6].sum(),z[6:].sum()])
    expected=((totals[0]-totals[1])**2+(totals[2]-totals[3])**2)/weights[domain].sum()**2
    assert np.allclose(result["beta"],[mean])
    assert np.allclose(result["covariance"],[[expected]])
    assert result["df"]==1 and result["full_design_PSUs"]==4
    scaled=fit_domain(X,y,weights*137,strata,psu,domain)
    assert np.allclose(result["beta"],scaled["beta"])
    assert np.allclose(result["covariance"],scaled["covariance"])
    import statsmodels.api as sm
    x=np.column_stack([np.ones(8),np.arange(8,dtype=float)])
    fit=fit_domain(x,y,weights,strata,psu,np.ones(8,dtype=bool))
    reference=sm.WLS(y,x,weights=weights).fit()
    assert np.allclose(fit["beta"],reference.params)
    assert np.linalg.eigvalsh(fit["covariance"]).min()>-1e-10
    # Permuting rows must preserve the full stratified cluster estimator.
    permutation=np.array([5,1,7,2,6,3,0,4])
    permuted=fit_domain(x[permutation],y[permutation],weights[permutation],strata[permutation],psu[permutation],np.ones(8,dtype=bool))
    assert np.allclose(fit["covariance"],permuted["covariance"])
    return {"status":"passed","scope":"invented_fixtures_only","checks":["analytic stratified ratio-mean variance with empty domain PSU","correct domain df","global weight scaling invariance","WLS coefficients agree with statsmodels","covariance positive semidefinite","row permutation invariance"],"R_survey_cross_validation":False,"target_outcomes_analyzed":False}

if __name__=="__main__":
    import json
    print(json.dumps(validate_invented()))
