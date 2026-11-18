"""Pure shared lifestyle analysis. No files, target references, generator or API."""
import numpy as np
import pandas as pd
from scipy import stats

TRAITS = ['bmi','total_cholesterol','hdl_cholesterol']
GROUPS = ['pastoralist','rural_nonpastoralist','urban_nonpastoralist']
CONTRASTS = [('rural_minus_pastoralist',np.array([0.,1.,0.,0.,0.])),
             ('urban_minus_pastoralist',np.array([0.,0.,1.,0.,0.])),
             ('urban_minus_rural',np.array([0.,-1.,1.,0.,0.]))]
REQUIRED = ['id','age','sex','lifestyle']+TRAITS

def _fit(x,y):
    n,p=x.shape
    if n<=p or np.linalg.matrix_rank(x)!=p: raise ValueError('Insufficient rows or singular design')
    b=np.linalg.lstsq(x,y,rcond=None)[0]
    residual=y-x@b; rss=float(residual@residual)
    if not np.isfinite(rss) or rss<=1e-15: raise ValueError('Residual variance degenerate')
    covariance=(rss/(n-p))*np.linalg.inv(x.T@x)
    return dict(beta=b,covariance=covariance,rss=rss,n=n,p=p,df=n-p)

def _contrasts(fit,trait,stratum,selected):
    result=[]
    for label,c in CONTRASTS:
        c=c[:fit['p']] if fit else c
        rec=dict(trait=trait,stratum=stratum,contrast=label,selected_by_paper_rule=selected,
                 unit='within-dataset biomarker SD',status='unavailable')
        if fit:
            estimate=float(c@fit['beta']);variance=float(c@fit['covariance']@c)
            if not np.isfinite(variance) or variance<=0: raise ValueError('Contrast variance degenerate')
            se=float(np.sqrt(variance));t=estimate/se;critical=float(stats.t.ppf(.975,fit['df']))
            rec.update(status='computed',estimate=estimate,se=se,lower=estimate-critical*se,
                upper=estimate+critical*se,p_value=float(2*stats.t.sf(abs(t),fit['df'])),
                n=fit['n'],df=fit['df'])
        result.append(rec)
    return result

def _bh(p_values):
    p=np.asarray(p_values,float);order=np.argsort(p);n=len(p)
    ordered=np.minimum.accumulate((p[order]*n/np.arange(1,n+1))[::-1])[::-1]
    q=np.empty(n);q[order]=np.clip(ordered,0,1);return q

def analyze_frame(frame):
    if list(frame.columns)!=REQUIRED: raise ValueError('Exact canonical schema required')
    if frame['id'].isna().any() or frame['id'].astype(str).duplicated().any(): raise ValueError('Missing or duplicated IDs')
    if not frame['sex'].isin(['F','M']).all(): raise ValueError('Invalid sex category')
    if not frame['lifestyle'].isin(GROUPS).all(): raise ValueError('Invalid lifestyle category')
    d=frame.copy()
    for c in ['age']+TRAITS:
        d[c]=pd.to_numeric(d[c],errors='raise')
    eligible_age=np.isfinite(d.age)&(d.age>18)
    if not np.isfinite(d.age).all(): raise ValueError('Missing or nonfinite age')
    d=d.loc[eligible_age].copy()
    result=dict(target_reference_read=False,operator_version='lifestyle_main_three_traits_v1',
        input_rows=len(frame),eligible_age_rows=len(d),age_excluded=int((~eligible_age).sum()),
        selected_sample='age >18; complete positive finite outcome separately for each trait',
        scaling='mean and sample SD on trait-specific eligible rows; reused for sex-specific fits',
        contrasts=[],interactions=[],group_summaries=[],trait_status=[],
        interval_scope='Classical OLS t intervals conditional on these rows/model; not uncertainty of source evidence or virtual-population truth',
        multiplicity_scope='BH over exactly 9 additive contrasts of this dataset, only when all 9 are available; not the original 11-outcome family',
        hdl_above_tc_count=int(((d.hdl_cholesterol>d.total_cholesterol)&d.hdl_cholesterol.notna()&d.total_cholesterol.notna()).sum()))
    for trait in TRAITS:
        mask=d[trait].notna()&np.isfinite(d[trait])&(d[trait]>0)
        t=d.loc[mask].copy();y=t[trait].to_numpy(float)
        n=len(t);sd=float(np.std(y,ddof=1)) if n>1 else None
        status=dict(trait=trait,n=n,missing=int(d[trait].isna().sum()),
            nonfinite_nonmissing=int((d[trait].notna()&~np.isfinite(d[trait])).sum()),
            nonpositive=int((d[trait].notna()&np.isfinite(d[trait])&(d[trait]<=0)).sum()),
            mean=float(np.mean(y)) if n else None,sample_sd=sd)
        for g in GROUPS:
            v=t.loc[t.lifestyle==g,trait].to_numpy(float)
            result['group_summaries'].append(dict(trait=trait,lifestyle=g,n=len(v),
                mean=float(v.mean()) if len(v) else None,sd=float(v.std(ddof=1)) if len(v)>1 else None))
        if n<=7 or sd is None or not np.isfinite(sd) or sd<=1e-12:
            status.update(status='unavailable',reason='Insufficient or constant outcome')
            result['trait_status'].append(status)
            result['interactions'].append(dict(trait=trait,status='unavailable',reason=status['reason']))
            for stratum in ['pooled','F','M']: result['contrasts']+=_contrasts(None,trait,stratum,None)
            continue
        z=(y-y.mean())/sd
        rural=(t.lifestyle=='rural_nonpastoralist').to_numpy(float)
        urban=(t.lifestyle=='urban_nonpastoralist').to_numpy(float)
        sex=(t.sex=='F').to_numpy(float);age=t.age.to_numpy(float)
        # Column order makes all three predeclared contrasts identical across strata.
        x=np.column_stack([np.ones(n),rural,urban,age,sex])
        fit=None;interaction=None
        try:
            fit=_fit(x,z)
            full=_fit(np.column_stack([x,rural*sex,urban*sex]),z)
            lr=max(0.,float(n*np.log(fit['rss']/full['rss'])))
            p=float(stats.chi2.sf(lr,2));interaction=p<.05
            result['interactions'].append(dict(trait=trait,status='computed',lr=lr,df=2,p_value=p,
                selects_sex_specific=interaction,comparison='Gaussian ML likelihood ratio, same rows, 2 interaction terms'))
        except ValueError as exc:
            result['interactions'].append(dict(trait=trait,status='unavailable',reason=str(exc)))
        result['contrasts']+=_contrasts(fit,trait,'pooled',not interaction if interaction is not None else None)
        for s in ['F','M']:
            ix=(t.sex==s).to_numpy();sf=None
            try: sf=_fit(x[ix,:4],z[ix])
            except ValueError: pass
            result['contrasts']+=_contrasts(sf,trait,s,interaction)
        status.update(status='computed' if fit else 'unavailable',selected_branch=('sex_specific' if interaction else 'pooled') if interaction is not None else 'unresolved')
        result['trait_status'].append(status)
    additive=[c for c in result['contrasts'] if c['stratum']=='pooled']
    if len(additive)==9 and all(c['status']=='computed' for c in additive):
        for c,q in zip(additive,_bh([c['p_value'] for c in additive])):c['q_subset_bh9']=float(q)
    else:
        for c in additive:c['q_subset_bh9']=None
    return result

def generated_diagnostics(frame,task):
    if len(frame)!=task['n_rows']: raise ValueError('Unexpected generated row count')
    return analyze_frame(frame)
