import numpy as np
import pandas as pd
from scipy.special import ndtr
from scipy.stats import truncnorm
from scipy.optimize import least_squares


def generate(observed, spec, seed):
    """Generate a fictional rural-active adult analogue, never real participants."""
    if observed is not None:
        raise ValueError('This generator is whole-cohort only.')
    rng = np.random.default_rng(seed)
    n = int(spec['n_rows'])
    female = rng.random(n) < spec['female_probability']
    sex = np.where(female, 'F', 'M')
    z_age = rng.standard_normal(n)
    r = spec['age_bmi_latent_correlation']
    z_bmi = r*z_age + np.sqrt(1-r*r)*rng.standard_normal(n)
    age = np.empty(n)
    bmi = np.empty(n)
    mh = np.empty(n)
    mn = np.empty(n)
    vh = np.empty(n)
    vn = np.empty(n)
    u_age = np.clip(ndtr(z_age), 1e-12, 1-1e-12)
    u_bmi = np.clip(ndtr(z_bmi), 1e-12, 1-1e-12)

    for s in ['F', 'M']:
        ix = sex == s
        p = spec['sex_parameters'][s]
        am, ast = p['age_mean'], p['age_sd']
        bm, bst = p['bmi_mean'], p['bmi_sd']
        al, ah = spec['age_bounds']
        bl, bh = spec['bmi_bounds']
        # Fit pre-truncation parameters to specified post-truncation moments.
        def age_err(par):
            loc, scale = par[0], np.exp(par[1])
            a, b = (al-loc)/scale, (ah-loc)/scale
            m, v = truncnorm.stats(a, b, loc=loc, scale=scale, moments='mv')
            return [(float(m)-am)/ast, (np.sqrt(float(v))-ast)/ast]
        fit_a = least_squares(age_err, [am, np.log(ast)], max_nfev=200)
        loc, scale = fit_a.x[0], np.exp(fit_a.x[1])
        if np.linalg.norm(fit_a.fun) > 1e-6:
            raise ValueError('Age marginal fitting did not converge')
        age[ix] = truncnorm.ppf(u_age[ix], (al-loc)/scale, (ah-loc)/scale, loc=loc, scale=scale)

        def bmi_err(par):
            mu, sig = par[0], np.exp(par[1])
            a, b = (np.log(bl)-mu)/sig, (np.log(bh)-mu)/sig
            den = ndtr(b)-ndtr(a)
            m = np.exp(mu+0.5*sig*sig)*(ndtr(b-sig)-ndtr(a-sig))/den
            m2 = np.exp(2*mu+2*sig*sig)*(ndtr(b-2*sig)-ndtr(a-2*sig))/den
            return [(m-bm)/bst, (np.sqrt(max(m2-m*m, 1e-15))-bst)/bst]
        sig0 = np.sqrt(np.log1p((bst/bm)**2))
        mu0 = np.log(bm)-0.5*sig0*sig0
        fit_b = least_squares(bmi_err, [mu0, np.log(sig0)], max_nfev=200)
        mu, sig = fit_b.x[0], np.exp(fit_b.x[1])
        if np.linalg.norm(fit_b.fun) > 1e-6:
            raise ValueError('BMI marginal fitting did not converge')
        lb, ub = (np.log(bl)-mu)/sig, (np.log(bh)-mu)/sig
        bmi[ix] = np.exp(truncnorm.ppf(u_bmi[ix], lb, ub, loc=mu, scale=sig))

        # Malawi standardized associations are transported per SD of synthetic BMI.
        bt = p['tc_difference_per_bmi_sd']/bst
        bhdl = p['hdl_difference_per_bmi_sd']/bst
        at = spec['tc_age_slope']
        a_h = spec['hdl_age_slope']
        mt = p['tc_mean'] + bt*(bmi[ix]-bm) + at*(age[ix]-am)
        mh[ix] = p['hdl_mean'] + bhdl*(bmi[ix]-bm) + a_h*(age[ix]-am)
        mn[ix] = mt-mh[ix]
        # Approximate Pearson age-BMI correlation by its latent copula value.
        cov_ab = r*ast*bst
        var_mt = bt*bt*bst*bst + at*at*ast*ast + 2*bt*at*cov_ab
        var_mh = bhdl*bhdl*bst*bst + a_h*a_h*ast*ast + 2*bhdl*a_h*cov_ab
        vt = p['tc_sd']**2-var_mt
        vh[ix] = p['hdl_sd']**2-var_mh
        vn[ix] = vt-vh[ix]
    if not (np.all(mh > 0) and np.all(mn > 0) and np.all(vh > 0) and np.all(vn > 0)):
        raise ValueError('Incompatible mean/variance specification')
    # Independent positive HDL and non-HDL components conditional on covariates.
    hdl = rng.gamma(shape=mh*mh/vh, scale=vh/mh)
    non_hdl = rng.gamma(shape=mn*mn/vn, scale=vn/mn)
    total = hdl+non_hdl
    out = pd.DataFrame({'id': [f'fictional_{i+1:04d}' for i in range(n)],
                        'age': age, 'sex': sex, 'bmi': bmi,
                        'total_cholesterol': total, 'hdl_cholesterol': hdl})
    vals = out[['age','bmi','total_cholesterol','hdl_cholesterol']].to_numpy()
    if not np.isfinite(vals).all() or not (vals[:,1:] > 0).all():
        raise ValueError('Nonfinite or nonpositive generated value')
    return out[['id','age','sex','bmi','total_cholesterol','hdl_cholesterol']]
