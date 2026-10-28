"""Predeclared source-only copula sensitivities; endpoints independent.
No target fitting. Source summaries determine margins, not dependence.
"""
import numpy as np
import pandas as pd
from scipy import stats

def marginal(z, mean, sd, kind):
    u=np.clip(stats.norm.cdf(z),1e-10,1-1e-10)
    if kind=='normal': return mean+sd*z
    if kind=='beta':
        concentration=max(mean*(1-mean)/sd**2-1,.1)
        return stats.beta.ppf(u,max(mean*concentration,.01),max((1-mean)*concentration,.01))
    if kind=='gamma': return stats.gamma.ppf(u,(mean/sd)**2,scale=sd**2/mean)
    sigma=np.sqrt(np.log1p((sd/mean)**2))
    return np.exp(np.log(mean)-sigma**2/2+sigma*z)

def generate(n,seed,evidence,context='target'):
    if context not in ['target','rho_0','rho_04','rho_08']: raise ValueError('Unknown fixed reference sensitivity')
    rng=np.random.default_rng(seed)
    rho={'target':.4,'rho_0':0.,'rho_04':.4,'rho_08':.8}[context]
    if 'moments' in evidence:
        d={'participant_id':[f'SYN_{i+1:02d}' for i in range(n)]}
        for e,m in evidence['moments'].items():
            common=rng.normal(size=n)
            for t in ['pre','post']:
                z=np.sqrt(rho)*common+np.sqrt(1-rho)*rng.normal(size=n)
                values=marginal(z,m[t+'_mean'],m[t+'_sd'],'normal' if e=='leptin_log10' else 'lognormal')
                count=int(round(m['n']*n/evidence['n_persons']))
                values[count:]=np.nan
                d[e+'_'+t]=values
        return pd.DataFrame(d)
    d={'person_id':np.repeat(np.arange(1,n+1),5),'month':np.tile([0,3,6,9,12],n)}
    for col in ['weight_kg','pfs','gng','dd100','dd1000']:
        common=rng.normal(size=n); values=np.zeros((n,5))
        for j,month in enumerate([0,3,6,9,12]):
            m=next(x for x in evidence['marginal_summaries'] if x['month']==month and x['variable']==col)
            z=np.sqrt(rho)*common+np.sqrt(1-rho)*rng.normal(size=n)
            if col=='pfs': v=1+4*marginal(z,(m['mean']-1)/4,m['sd']/4,'beta')
            elif col.startswith('dd'): v=marginal(z,m['mean'],m['sd'],'beta')
            elif col=='gng': v=np.clip(np.round(marginal(z,m['mean'],m['sd'],'gamma')),0,512)
            else: v=marginal(z,m['mean'],m['sd'],'lognormal')
            count=int(round(m['n_observed']*n/evidence['n_persons']))
            if count<n: v[rng.choice(n,n-count,replace=False)]=np.nan
            values[:,j]=v
        d[col]=values.ravel()
    return pd.DataFrame(d)
