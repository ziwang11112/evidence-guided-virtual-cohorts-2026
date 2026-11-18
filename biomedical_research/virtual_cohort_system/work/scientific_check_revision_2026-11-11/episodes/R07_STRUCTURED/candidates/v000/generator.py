import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.special import expit

def generate(observed, spec, seed):
    """Generate fictional equal-weight adult records; no target records are used."""
    if observed is not None:
        raise ValueError('This generator is whole-cohort only.')
    rng = np.random.default_rng(seed)
    n = int(spec['n'])
    r = spec['reference']
    counts = np.asarray(r['group_n'], dtype=float)
    weights = counts / counts.sum()
    def pool(mean, sd):
        mean = np.asarray(mean, dtype=float)
        sd = np.asarray(sd, dtype=float)
        mu = weights @ mean
        # Population mixture of the reported group moments; ignores negligible n/(n-1) corrections.
        var = weights @ (sd**2 + (mean-mu)**2)
        return float(mu), float(var)
    age0, va = pool(r['age_mean'], r['age_sd'])
    bmi0, vb = pool(r['bmi_mean'], r['bmi_sd'])
    sbp0, vs = pool(r['sbp_mean'], r['sbp_sd'])
    dbp0, vd = pool(r['dbp_mean'], r['dbp_sd'])
    ss = np.asarray(r['sbp_sd']); ds = np.asarray(r['dbp_sd']); ps = np.asarray(r['pp_sd'])
    sm = np.asarray(r['sbp_mean']); dm = np.asarray(r['dbp_mean'])
    cov_sd = float(weights @ ((ss**2+ds**2-ps**2)/2 + (sm-sbp0)*(dm-dbp0)))
    female0 = float(weights @ np.asarray(r['female_fraction']))
    vf = female0*(1-female0)
    c = spec['conditional']
    ba = float(c['bmi_age']); bf = float(c['bmi_female'])
    vmean_bmi = ba*ba*va + bf*bf*vf
    # Under reference normal age independent of recorded sex, solve the lognormal CV from total BMI variance.
    cv2 = (vb-vmean_bmi)/(bmi0*bmi0+vmean_bmi)
    if cv2 <= 0:
        raise ValueError('Invalid BMI reference decomposition')
    C = np.array([[va, 0, ba*va], [0, vf, bf*vf], [ba*va, bf*vf, vb]])
    B = np.asarray([[c['sbp_age'], c['sbp_female'], c['sbp_bmi']],
                    [c['dbp_age'], c['dbp_female'], c['dbp_bmi']]], dtype=float)
    explained = B @ C @ B.T
    # Centered age-squared term orthogonal to linear reference predictors under the stated normal-age assumption.
    explained[1,1] += 2*va**2*c['dbp_age_quadratic']**2
    residual_cov = np.array([[vs, cov_sd], [cov_sd, vd]]) - explained
    if np.min(np.linalg.eigvalsh(residual_cov)) <= 0:
        raise ValueError('Residual covariance must be positive definite')
    residual_cov += np.asarray(spec['measurement_extra_cov'], dtype=float)
    L = np.linalg.cholesky(residual_cov)

    ages = np.arange(20,80, dtype=float)
    def probs(rate):
        z = -rate*(ages-20)
        p = np.exp(z-z.max())
        return p/p.sum()
    rate = brentq(lambda t: probs(t) @ ages-spec['demography']['mean_age'], -0.3, 0.3)
    ap = probs(rate)
    age = rng.choice(ages, size=n, p=ap)
    d = spec['demography']
    sex_gradient = float(d['female_log_odds_age'])
    intercept = brentq(lambda k: ap @ expit(k+sex_gradient*(ages-d['mean_age']))-d['female_fraction'], -10, 10)
    female = rng.binomial(1, expit(intercept+sex_gradient*(age-d['mean_age'])), size=n)
    a = age-age0
    f = female-female0
    bmi_mean = bmi0+ba*a+bf*f
    sigma2 = np.log1p(cv2)
    bmi = np.exp(np.log(bmi_mean)-sigma2/2 + np.sqrt(sigma2)*rng.standard_normal(n))
    X = np.column_stack([a, f, bmi-bmi0])
    mu = np.array([sbp0, dbp0]) + X @ B.T
    mu[:,1] += c['dbp_age_quadratic']*(a*a-va)
    bp = mu + rng.standard_normal((n,2)) @ L.T
    # Pairwise redraw, never sorting SBP/DBP or clipping values. Normally no or very few redraws.
    bad = (bp[:,1] <= 0) | (bp[:,0] <= bp[:,1])
    for _ in range(100):
        if not np.any(bad):
            break
        bp[bad] = mu[bad] + rng.standard_normal((int(bad.sum()),2)) @ L.T
        bad = (bp[:,1] <= 0) | (bp[:,0] <= bp[:,1])
    if np.any(bad):
        raise RuntimeError('BP rejection failed')
    # Half-mmHg resolution is an explicit last-two-integer-readings aggregation proxy.
    bp = np.round(2*bp)/2
    bad = (bp[:,1] <= 0) | (bp[:,0] <= bp[:,1])
    if np.any(bad):
        # Probability is negligible; maintain strict ordering after rounding without a silent correction.
        raise RuntimeError('Rounding produced invalid pressure ordering')
    return pd.DataFrame({'row_id': np.arange(1,n+1, dtype=np.int64),
                         'age': age, 'female': female.astype(np.int64),
                         'bmi': bmi, 'sbp': bp[:,0], 'dbp': bp[:,1]},
                         columns=['row_id','age','female','bmi','sbp','dbp'])
