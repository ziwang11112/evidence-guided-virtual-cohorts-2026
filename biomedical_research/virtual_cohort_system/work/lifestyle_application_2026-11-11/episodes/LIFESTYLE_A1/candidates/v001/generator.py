import numpy as np
import pandas as pd
from scipy.stats import chi2
import json


def analyze_generated(df):
    """Generated-only analyses; all standardized outcomes use one pooled sample SD."""
    n = len(df)
    r = (df['lifestyle'].to_numpy() == 'rural_nonpastoralist').astype(float)
    u = (df['lifestyle'].to_numpy() == 'urban_nonpastoralist').astype(float)
    f = (df['sex'].to_numpy() == 'F').astype(float)
    age = df['age'].to_numpy()
    xa = np.column_stack([np.ones(n), r, u, age, f])
    xi = np.column_stack([xa, r*f, u*f])
    def contrasts(b):
        return {'rural_minus_pastoralist': float(b[1]),
                'urban_minus_pastoralist': float(b[2]),
                'urban_minus_rural': float(b[2]-b[1])}
    ans = {'n': n, 'counts': df.groupby(['lifestyle','sex'], observed=True).size().to_dict(),
           'hdl_above_tc': int((df.hdl_cholesterol > df.total_cholesterol).sum()),
           'missing_cells': int(df.isna().sum().sum()), 'outcomes': {}}
    ans['counts'] = {str(k): int(v) for k,v in ans['counts'].items()}
    for name in ['bmi','total_cholesterol','hdl_cholesterol']:
        y = df[name].to_numpy()
        z = (y-y.mean())/y.std(ddof=1)
        ba = np.linalg.lstsq(xa,z,rcond=None)[0]
        bi = np.linalg.lstsq(xi,z,rcond=None)[0]
        ssa = np.sum((z-xa@ba)**2)
        ssi = np.sum((z-xi@bi)**2)
        lr = max(0.0, n*np.log(ssa/ssi))
        d = {'pooled_mean': float(y.mean()), 'pooled_sd_ddof1': float(y.std(ddof=1)),
             'additive': contrasts(ba), 'interaction_lrt_2df': float(lr),
             'interaction_p': float(chi2.sf(lr,2)), 'sex_specific': {},
             'group_mean_sd': {}}
        for label in ['F','M']:
            ix = df['sex'].to_numpy() == label
            xs = np.column_stack([np.ones(ix.sum()),r[ix],u[ix],age[ix]])
            bs = np.linalg.lstsq(xs,z[ix],rcond=None)[0]
            d['sex_specific'][label] = contrasts(bs)
        for label, sub in df.groupby('lifestyle', observed=True):
            d['group_mean_sd'][str(label)] = [float(sub[name].mean()),float(sub[name].std(ddof=1))]
        ans['outcomes'][name] = d
    return ans


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('Whole-cohort generator requires observed=None')
    rng = np.random.default_rng(seed)
    n = int(spec['n'])
    groups = spec['lifestyles']
    # Table 1 order within each age band: P-M, P-F, R-M, R-F, U-M, U-F.
    raw = np.asarray(spec['published_age_sex_counts'], dtype=float)
    expected = n*raw/raw.sum()
    allocated = np.floor(expected).astype(int)
    remainder = n-int(allocated.sum())
    priority = np.argsort(-(expected-allocated).ravel(), kind='stable')
    allocated.ravel()[priority[:remainder]] += 1
    bounds = np.asarray(spec['age_bounds'], dtype=float)
    bm = bounds.mean(axis=1)
    bv = ((bounds[:,1]-bounds[:,0])**2)/12.0
    a, mode, b = spec['oldest_triangular']
    bm[-1] = (a+mode+b)/3.0
    bv[-1] = (a*a+mode*mode+b*b-a*mode-a*b-mode*b)/18.0
    g_parts, f_parts, age_parts = [], [], []
    for k in range(raw.shape[0]):
        for j in range(raw.shape[1]):
            m = int(allocated[k,j])
            g_parts.append(np.full(m,j//2,dtype=int))
            f_parts.append(np.full(m,j%2,dtype=int))
            if k == raw.shape[0]-1:
                aa = rng.triangular(a,mode,b,m)
            else:
                lo = np.nextafter(bounds[k,0],np.inf) if k == 0 else bounds[k,0]
                aa = rng.uniform(lo,bounds[k,1],m)
            age_parts.append(aa)
    g = np.concatenate(g_parts)
    f = np.concatenate(f_parts)
    age = np.concatenate(age_parts)
    order = rng.permutation(n)
    g, f, age = g[order], f[order], age[order]
    # Population moments conditional on the fixed, rescaled demographic layout.
    weights, mean_age, female_prop = [], [], []
    for j in range(3):
        w = allocated[:,2*j:2*j+2].astype(float)
        w /= w.sum()
        weights.append(w)
        mean_age.append(np.sum(w*bm[:,None]))
        female_prop.append(w[:,1].sum())
    mean_age, female_prop = np.array(mean_age), np.array(female_prop)
    corr = np.asarray(spec['latent_gaussian_correlation'],dtype=float)
    z = rng.standard_normal((n,3)) @ np.linalg.cholesky(corr).T
    values = {}
    for q, name in enumerate(['bmi','hdl','nonhdl']):
        par = spec['traits'][name]
        means = np.asarray(par['group_marginal_means'],dtype=float)
        sds = np.asarray(par['group_marginal_sds'],dtype=float)
        ba = float(par['age_slope'])
        bf = float(par['female_main_effect']) + np.asarray(par['female_interaction'],dtype=float)
        sigma = np.zeros(3)
        for j in range(3):
            cell_mu = means[j] + ba*(bm[:,None]-mean_age[j]) + bf[j]*(np.array([0.,1.])[None,:]-female_prop[j])
            vmu = np.sum(weights[j]*((cell_mu-means[j])**2+ba*ba*bv[:,None]))
            cv2 = (sds[j]**2-vmu)/(means[j]**2+vmu)
            if cv2 <= 0:
                raise ValueError('Requested marginal variance is smaller than covariate variance')
            sigma[j] = np.sqrt(np.log1p(cv2))
        mu = means[g]+ba*(age-mean_age[g])+bf[g]*(f-female_prop[g])
        if np.any(mu <= 0):
            raise ValueError('Nonpositive conditional mean')
        # Exact conditional arithmetic mean mu; no empirical post-hoc rescaling.
        values[name] = mu*np.exp(sigma[g]*z[:,q]-0.5*sigma[g]**2)
    df = pd.DataFrame({
        'id': [f'VIRT_{j+1:04d}' for j in range(n)],
        'age': age,
        'sex': np.where(f==1,'F','M'),
        'lifestyle': np.asarray(groups,dtype=object)[g],
        'bmi': values['bmi'],
        'total_cholesterol': values['hdl']+values['nonhdl'],
        'hdl_cholesterol': values['hdl']
    }, columns=['id','age','sex','lifestyle','bmi','total_cholesterol','hdl_cholesterol'])
    assert len(df)==1226 and not df.isna().any().any()
    assert (df.age>18).all() and (df[['bmi','total_cholesterol','hdl_cholesterol']]>0).all().all()
    if spec.get('print_generated_diagnostics',False):
        print('GENERATED_ONLY_ANALYSIS '+json.dumps(analyze_generated(df),sort_keys=True))
    return df
