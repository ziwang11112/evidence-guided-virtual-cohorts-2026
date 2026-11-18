import numpy as np
import pandas as pd

def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('Whole-cohort generator requires observed=None')
    rng = np.random.default_rng(seed)
    m = spec['model']
    n = spec['task']['n_rows']
    # Published pooled Pearson correlations and sex contrasts reconstruct
    # an approximate covariance matrix, NOT individual source records.
    sd = np.asarray(m['ghana']['sd_age_bmi_tc_hdl'], dtype=float)
    R = np.asarray(m['ghana']['correlation_age_bmi_tc_hdl'], dtype=float)
    C = R * np.outer(sd, sd)
    p = m['ghana']['female_fraction']
    vs = p * (1.0-p) * 120.0/119.0
    delta = np.asarray(m['ghana']['female_minus_male_age_bmi_tc_hdl'])
    cov_s = delta * vs
    # Predictors ordered age, female indicator, BMI; outcomes TC and HDL.
    Sxx = np.array([[C[0,0], cov_s[0], C[0,1]],
                    [cov_s[0], vs, cov_s[1]],
                    [C[1,0], cov_s[1], C[1,1]]])
    Sxy = np.array([[C[0,2], C[0,3]],
                    [cov_s[2], cov_s[3]],
                    [C[1,2], C[1,3]]])
    B = np.linalg.solve(Sxx, Sxy)
    E = C[2:4,2:4] - Sxy.T @ B
    rho = E[0,1]/np.sqrt(E[0,0]*E[1,1])
    if np.min(np.linalg.eigvalsh(E)) <= 0:
        raise ValueError('Source-derived residual covariance not positive definite')
    female = rng.random(n) < m['female_probability']
    sex = np.where(female, 'F', 'M')
    probs = np.where(female[:,None], np.array(m['age_group_probabilities_F']),
                     np.array(m['age_group_probabilities_M']))
    u = rng.random(n)
    group = (u[:,None] > np.cumsum(probs,axis=1)).sum(axis=1)
    age = np.empty(n)
    for k, (left, mode, right) in enumerate(m['age_triangles']):
        z = group == k
        age[z] = rng.triangular(left,mode,right,size=int(z.sum()))
    # Exact expected sex-specific age, for centering only.
    age_means = np.mean(np.array(m['age_triangles']),axis=1)
    aF = np.dot(m['age_group_probabilities_F'],age_means)
    aM = np.dot(m['age_group_probabilities_M'],age_means)
    age_center = np.where(female,aF,aM)
    transition = rng.random(n) < m['transition_probability']
    base_bmi = np.where(female,25.5,21.8)
    bmi_sd = np.where(female,4.8,3.4)
    bmi_shift = np.where(female,1.0,0.9)
    # Modest positive age-BMI relation is assumed; not extrapolated from students.
    mean_bmi = base_bmi + m['bmi_age_slope']*(age-age_center) + transition*bmi_shift
    sigma_bmi = np.sqrt(np.log1p((bmi_sd/mean_bmi)**2))
    bmi = mean_bmi*np.exp(sigma_bmi*rng.standard_normal(n)-0.5*sigma_bmi**2)
    # Source-derived age/BMI slopes transported on the arithmetic lipid scale.
    # Baseline sex-specific means instead come from rural Tanzania.
    mu_tc = np.where(female,4.43,3.74) + B[0,0]*(age-age_center) + B[2,0]*(bmi-base_bmi) + transition*np.where(female,0.24,0.42)
    mu_hd = np.where(female,1.69,1.67) + B[0,1]*(age-age_center) + B[2,1]*(bmi-base_bmi) + transition*np.where(female,0.25,0.24)
    s_tc = np.where(female,1.30,1.00)
    s_hd = np.where(female,0.38,0.30)
    if np.any(mu_tc <= 0) or np.any(mu_hd <= 0):
        raise ValueError('Nonpositive conditional lipid mean')
    # Bivariate lognormal noise with arithmetic means mu and constant conditional
    # SDs; per-row latent rho makes conditional Pearson rho equal the derived rho.
    lt = np.sqrt(np.log1p((s_tc/mu_tc)**2))
    lh = np.sqrt(np.log1p((s_hd/mu_hd)**2))
    latent_rho = np.log1p(rho*s_tc*s_hd/(mu_tc*mu_hd))/(lt*lh)
    if np.any(np.abs(latent_rho) >= 1):
        raise ValueError('Infeasible lognormal covariance')
    zt = rng.standard_normal(n)
    zh = latent_rho*zt + np.sqrt(1-latent_rho**2)*rng.standard_normal(n)
    tc = mu_tc*np.exp(lt*zt-0.5*lt**2)
    hd = mu_hd*np.exp(lh*zh-0.5*lh**2)
    out = pd.DataFrame({'id':['SYN%05d' % (i+1) for i in range(n)],
        'age':age, 'sex':sex, 'bmi':bmi, 'total_cholesterol':tc,
        'hdl_cholesterol':hd})
    assert out.shape == (3000,6)
    assert np.isfinite(out[['age','bmi','total_cholesterol','hdl_cholesterol']].to_numpy()).all()
    assert (out[['bmi','total_cholesterol','hdl_cholesterol']].to_numpy()>0).all()
    return out
