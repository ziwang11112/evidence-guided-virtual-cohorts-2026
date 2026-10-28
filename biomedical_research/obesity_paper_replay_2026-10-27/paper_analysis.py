"""Identical analysis of real and synthetic data; no generator imports allowed.

Primary held-out results are the six baseline Pearson correlations in Table 1.
Secondary reconstruction uses the published random-intercept, categorical-visit
REML weight model. Estimates/SEs are comparable; normal-Wald p/CI are not asserted
to reproduce SAS's unspecified denominator-df procedure exactly.
"""
from pathlib import Path
from itertools import combinations
import argparse
import json
import warnings
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

BASELINE_VARIABLES = ['pfs', 'gng', 'dd100', 'dd1000']
REQUIRED = ['person_id','month','weight_kg',*BASELINE_VARIABLES]

def result(analysis, term, estimate, se, lo, hi, p, d, status, role, **extra):
    def value(x):
        return float(x) if x is not None and np.isfinite(x) else None
    return {'analysis':analysis, 'term':term, 'estimate':value(estimate),
            'se':value(se), 'ci_low':value(lo), 'ci_high':value(hi), 'p':value(p),
            'n_persons':int(d.person_id.nunique()), 'n_rows':int(len(d)),
            'status':status, 'role':role, **extra}

def validate_input(df):
    absent=set(REQUIRED)-set(df)
    if absent:
        raise ValueError(f'Missing required columns: {absent}')
    if df.duplicated(['person_id','month']).any():
        raise ValueError('Repeated person_id/month key')
    if not set(df.month.dropna()).issubset({0,3,6,9,12}):
        raise ValueError('Unexpected visit')
    if df[['person_id','month']].isna().any().any():
        raise ValueError('Missing identifiers/visits')
    for c in REQUIRED:
        if not pd.api.types.is_numeric_dtype(df[c]):
            raise ValueError(f'Non-numeric canonical column {c}')
    out=df.copy()
    out['month']=out['month'].astype(int)
    return out

def baseline_correlations(df):
    out=[]
    base=df.loc[df.month.eq(0)]
    for x,y in combinations(BASELINE_VARIABLES,2):
        d=base[['person_id',x,y]].dropna()
        if len(d)<4 or d[x].nunique()<2 or d[y].nunique()<2:
            out.append(result('baseline_pearson',f'{x}__{y}',None,None,None,None,None,
                              d,'degenerate','heldout_primary'))
            continue
        r,p=stats.pearsonr(d[x],d[y])
        # Fisher-z interval on r; SE field is the delta-method SE on the r scale.
        z=np.arctanh(np.clip(r,-1+1e-14,1-1e-14)); zse=1/np.sqrt(len(d)-3)
        lo,hi=np.tanh([z-1.95996398454*zse,z+1.95996398454*zse])
        out.append(result('baseline_pearson',f'{x}__{y}',r,(1-r*r)*zse,lo,hi,p,d,
                          'ok','heldout_primary',ci_method='Fisher z',p_method='Pearson exact t under bivariate normal null'))
    return out

def fit_random_intercept(formula, d):
    with warnings.catch_warnings(record=True) as ww:
        warnings.simplefilter('always')
        fit=smf.mixedlm(formula,d,groups=d.person_id).fit(reml=True,method='powell',maxiter=600,disp=False)
    messages=sorted(set(str(w.message) for w in ww))
    return fit,messages

def time_trajectory(df, variable='weight_kg'):
    d=df.dropna(subset=[variable,'month','person_id']).copy()
    analysis='weight_time_reml' if variable=='weight_kg' else f'{variable}_time_reml'
    contrasts=[(3,0),(6,0),(9,0),(12,0),(12,3)]
    try:
        fit,messages=fit_random_intercept(f'{variable} ~ C(month)',d)
        names=list(fit.fe_params.index)
        beta=fit.fe_params.to_numpy()
        vcov=fit.cov_params().loc[names,names].to_numpy()
        out=[]
        for later,earlier in contrasts:
            v=np.zeros(len(names))
            for month,sign in [(later,1),(earlier,-1)]:
                if month:
                    v[names.index(f'C(month)[T.{month}]')]+=sign
            est=v@beta; se=np.sqrt(v@vcov@v)
            p=2*stats.norm.sf(abs(est/se))
            status='ok' if fit.converged and np.isfinite(se) else 'not_converged'
            out.append(result(analysis,f'month_{later}_minus_{earlier}',est,se,
                              est-1.95996398454*se,est+1.95996398454*se,p,d,status,
                              'reconstruction_secondary',ci_method='normal Wald',p_method='normal Wald; SAS finite-df method not specified',
                              fit_warnings=messages,variable=variable))
        return out
    except Exception as e:
        return [result(analysis,f'month_{a}_minus_{b}',None,None,None,None,None,
                       d,f'fit_failed:{type(e).__name__}:{e}','reconstruction_secondary') for a,b in contrasts]

def pooled_associations(df):
    """Optional method sensitivity, not an exact replay of published coefficients.

    The article does not specify enough details to reconcile its beta scaling and
    denominator degrees of freedom. This standardized implementation is labelled
    exploratory and cannot be used to claim exact published-model reproduction.
    """
    out=[]
    for x in BASELINE_VARIABLES:
        d=df[['person_id','weight_kg',x]].dropna().copy()
        try:
            d['z_weight']=(d.weight_kg-d.weight_kg.mean())/d.weight_kg.std(ddof=1)
            d['z_x']=(d[x]-d[x].mean())/d[x].std(ddof=1)
            fit,messages=fit_random_intercept('z_weight ~ z_x',d)
            est=fit.fe_params['z_x']; se=fit.bse_fe['z_x']
            out.append(result('pooled_standardized_reml',x,est,se,est-1.96*se,est+1.96*se,
                              2*stats.norm.sf(abs(est/se)),d,'ok' if fit.converged else 'not_converged',
                              'heldout_exploratory',fit_warnings=messages,
                              specification='Weight z score ~ predictor z score + participant random intercept; not asserted exact original model'))
        except Exception as e:
            out.append(result('pooled_standardized_reml',x,None,None,None,None,None,d,
                              f'fit_failed:{type(e).__name__}:{e}','heldout_exploratory'))
    return out

def analyze(df, include_exploratory=False):
    df=validate_input(df)
    results=baseline_correlations(df)
    for variable in ['weight_kg',*BASELINE_VARIABLES]:
        results+=time_trajectory(df,variable)
    if include_exploratory:
        results+=pooled_associations(df)
    return results

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('data',type=Path)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--include-exploratory',action='store_true')
    args=ap.parse_args()
    results=analyze(pd.read_csv(args.data),args.include_exploratory)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(results,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print(f'Saved {len(results)} analysis metrics to {args.out}')

if __name__=='__main__':
    main()
