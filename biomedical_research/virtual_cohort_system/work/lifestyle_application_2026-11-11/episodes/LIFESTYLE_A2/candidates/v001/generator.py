import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    """Whole fictional cohort; no observed records or external resources used."""
    rng = np.random.default_rng(seed)
    n = int(spec['n'])
    # Published Table 1 order is age bin x (past M,F; rural M,F; urban M,F).
    printed = np.asarray(spec['printed_counts'], dtype=float)
    quotas = printed.ravel() * n / printed.sum()
    counts = np.floor(quotas).astype(int)
    remainder_order = np.argsort(-(quotas-counts), kind='stable')
    counts[remainder_order[:n-counts.sum()]] += 1
    counts = counts.reshape(printed.shape)
    bounds = np.asarray(spec['age_bounds'], dtype=float)
    g_all, f_all, a_all = [], [], []
    # Analytic covariate moments of the chosen stratified age/sex design.
    pg, ag, va, vf, caf = [], [], [], [], []
    for g in range(3):
        w = counts[:, 2*g:2*g+2].astype(float)
        w /= w.sum()
        mid = bounds.mean(axis=1)
        second = (bounds[:,0]**2 + bounds[:,0]*bounds[:,1] + bounds[:,1]**2)/3
        fem = np.array([0.0, 1.0])
        p = np.sum(w * fem[None,:])
        am = np.sum(w * mid[:,None])
        pg.append(p)
        ag.append(am)
        va.append(np.sum(w * second[:,None]) - am**2)
        vf.append(p*(1-p))
        caf.append(np.sum(w * mid[:,None] * fem[None,:])-am*p)
        for b in range(len(bounds)):
            for f in range(2):
                k = int(counts[b,2*g+f])
                g_all.extend([g]*k)
                f_all.extend([f]*k)
                # Low endpoint 18 is excluded even if the RNG returns zero.
                u = rng.uniform(np.finfo(float).eps, 1.0, size=k)
                a_all.extend(bounds[b,0] + (bounds[b,1]-bounds[b,0])*u)
    group = np.asarray(g_all, dtype=int)
    female = np.asarray(f_all, dtype=float)
    age = np.asarray(a_all, dtype=float)
    pg, ag = np.asarray(pg), np.asarray(ag)
    pgrow, agrow = pg[group], ag[group]

    # Exact conditional arithmetic means, with sex-by-lifestyle terms.
    means = {}
    for key in ['bmi', 'hdl', 'tc']:
        p = spec[key]
        means[key] = (np.asarray(p['group_means'])[group]
                      + p['age_slope']*(age-agrow)
                      + (p['female_effect'] + np.asarray(p['female_interaction'])[group])*(female-pgrow))

    # Source pastoralist marginal SDs -> residual SDs under our chosen age/sex law.
    def pastoral_residual_sd(p):
        a, f = p['age_slope'], p['female_effect'] + p['female_interaction'][0]
        covar_var = a*a*va[0] + f*f*vf[0] + 2*a*f*caf[0]
        return np.sqrt(p['pastoral_marginal_sd']**2-covar_var)
    bmi_sd = pastoral_residual_sd(spec['bmi']) * np.asarray(spec['bmi']['residual_sd_multipliers'])[group]
    hdl_sd = pastoral_residual_sd(spec['hdl']) * np.asarray(spec['hdl']['residual_sd_multipliers'])[group]
    nhdl_mean = means['tc']-means['hdl']
    nhdl_sd = np.asarray(spec['non_hdl_residual_sd'])[group]
    if np.min(nhdl_mean) <= 0:
        raise ValueError('The specified TC and HDL conditional means are incompatible')

    # Gaussian-copula innovations. Correlations refer to latent normal residuals,
    # not raw Pearson correlations or standardized regression coefficients.
    L = np.linalg.cholesky(np.asarray(spec['latent_correlation'], dtype=float))
    z = rng.standard_normal((n,3)) @ L.T
    def positive_draw(mean, sd, innovation):
        # Mean/SD-matched lognormal: all conditional moments are finite.
        v = np.log1p((sd/mean)**2)
        return mean*np.exp(np.sqrt(v)*innovation-0.5*v)
    bmi = positive_draw(means['bmi'], bmi_sd, z[:,0])
    hdl = positive_draw(means['hdl'], hdl_sd, z[:,1])
    non_hdl = positive_draw(nhdl_mean, nhdl_sd, z[:,2])
    tc = hdl+non_hdl
    perm = rng.permutation(n)
    return pd.DataFrame({
        'id': [f'VIRTUAL-{i+1:04d}' for i in range(n)],
        'age': age[perm],
        'sex': np.where(female[perm] == 1, 'F', 'M'),
        'lifestyle': np.asarray(spec['lifestyle_labels'])[group[perm]],
        'bmi': bmi[perm],
        'total_cholesterol': tc[perm],
        'hdl_cholesterol': hdl[perm]
    }, columns=['id','age','sex','lifestyle','bmi','total_cholesterol','hdl_cholesterol'])
